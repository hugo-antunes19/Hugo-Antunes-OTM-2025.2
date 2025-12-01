# optimizerSCIP.py

from ortools.linear_solver import pywraplp

def resolver_grade(dados, creditos_minimos, NUM_SEMESTRES, CREDITOS_MAXIMOS_POR_SEMESTRE, disciplinas_cursadas=None):
    """
    Cria e resolve o modelo de otimização da grade horária usando SCIP.
    """
    if disciplinas_cursadas is None:
        disciplinas_cursadas = []
    
    # Set de IDs cursados para busca rápida
    cursadas_set = set(disciplinas_cursadas)

    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print("Solver SCIP não encontrado.")
        return None, None, -1, None
        
    infinity = solver.infinity()

    # Extrai os dados
    disciplinas = dados["disciplinas"]
    turmas_por_disciplina = dados["turmas_por_disciplina"]
    horarios_por_turma = dados["horarios_por_turma"]
    periodos_validos_por_disciplina = dados["periodos_validos_por_disciplina"]
    obrigatorias_ids = dados["obrigatorias_ids"]
    restritas_ids = dados["restritas_ids"]
    condicionadas_ids = dados["condicionadas_ids"]
    livres_ids = dados["livres_ids"]
    ids_optativas = restritas_ids + condicionadas_ids + livres_ids

    # --- 3. Variáveis de Decisão ---
    alocacao = {}
    
    cursada_vars = {}
    semestre_da_disciplina = {}

    for d_id in disciplinas:
        if d_id in cursadas_set:
            cursada_vars[d_id] = 1
            semestre_da_disciplina[d_id] = 0
            continue

        # Se não cursou, cria variáveis de decisão
        periodos_validos = periodos_validos_por_disciplina.get(d_id, {1, 2})
        oferta_em_impar = 1 in periodos_validos
        oferta_em_par = 2 in periodos_validos

        for t_id in turmas_por_disciplina.get(d_id, []):
            for s in range(1, NUM_SEMESTRES + 1):
                is_semestre_impar = (s % 2 != 0)
                if (is_semestre_impar and oferta_em_impar) or (not is_semestre_impar and oferta_em_par):
                    alocacao[(d_id, s, t_id)] = solver.BoolVar(f'alocacao_{d_id}_s{s}_t{t_id}')
        
        semestre_da_disciplina[d_id] = solver.IntVar(1, NUM_SEMESTRES + 1, f'semestre_{d_id}')

    # --- 4. Restrições ---
    # R1: Cursar a disciplina apenas uma vez

    # R1.1: Obrigatórias (Exatamente uma vez)
    for d_id in obrigatorias_ids:
        if d_id in cursadas_set:
            continue
        vars_obrigatoria = [var for key, var in alocacao.items() if key[0] == d_id]
        solver.Add(solver.Sum(vars_obrigatoria) == 1)

    # R1.2: Optativas (No máximo uma vez)
    for d_id in ids_optativas:
        if d_id in cursadas_set:
            continue
        vars_optativa = [var for key, var in alocacao.items() if key[0] == d_id]
        solver.Add(solver.Sum(vars_optativa) <= 1)

    # R2: Ligação (Linearizada)
    for d_id in disciplinas:
        if d_id in cursadas_set:
            continue

        cursada_var = solver.Sum([var for key, var in alocacao.items() if key[0] == d_id])
        cursada_vars[d_id] = cursada_var 
        
        termos_semestre = []
        for (d, s, t), var in alocacao.items():
            if d == d_id:
                termos_semestre.append(s * var)
        
        solver.Add(semestre_da_disciplina[d_id] == solver.Sum(termos_semestre) + (1 - cursada_var) * (NUM_SEMESTRES + 1))

    # R3: Créditos Mínimos (Linear)
    if restritas_ids:
        solver.Add(solver.Sum(int(disciplinas[d_id]['creditos']) * cursada_vars[d_id] for d_id in restritas_ids) >= creditos_minimos['restrita'])
    if condicionadas_ids:
        solver.Add(solver.Sum(int(disciplinas[d_id]['creditos']) * cursada_vars[d_id] for d_id in condicionadas_ids) >= creditos_minimos['condicionada'])
    if livres_ids:
        solver.Add(solver.Sum(int(disciplinas[d_id]['creditos']) * cursada_vars[d_id] for d_id in livres_ids) >= creditos_minimos['livre'])

    # --- R4: Pré-requisitos ---
    M_prereq = NUM_SEMESTRES + 1 

    for d_id, disc_info in disciplinas.items():
        if d_id in cursadas_set:
            continue

        for prereq_id in disc_info.get('prerequisitos', []):
            if prereq_id not in disciplinas: 
                continue

            var_d = cursada_vars[d_id]
            var_pre = cursada_vars[prereq_id]
            
            sem_d = semestre_da_disciplina[d_id]
            sem_pre = semestre_da_disciplina[prereq_id]

            if isinstance(var_pre, int) and var_pre == 1:
                pass
            else:
                solver.Add(var_pre >= var_d)
            
            solver.Add(sem_d - sem_pre >= 1 - M_prereq * (1 - var_d))
            

    # R5: Conflitos de Horário (Linear)
    for s in range(1, NUM_SEMESTRES + 1):
        horarios_do_semestre = {}
        for (d, sem, t), var in alocacao.items():
            if sem == s:
                for h in horarios_por_turma.get(t, []):
                    if h not in horarios_do_semestre: horarios_do_semestre[h] = []
                    horarios_do_semestre[h].append(var)
        for h, turmas_conflitantes in horarios_do_semestre.items():
            solver.Add(solver.Sum(turmas_conflitantes) <= 1)

    # R6: Limite de Créditos por Semestre (Linear)
    for s in range(1, NUM_SEMESTRES + 1):
        termos_de_credito = []
        for d_id in disciplinas:
            if d_id in cursadas_set: continue
            
            creditos = int(disciplinas[d_id]['creditos'])
            cursada_neste_semestre_vars = [var for (d, sem, t), var in alocacao.items() if d == d_id and sem == s]
            if cursada_neste_semestre_vars: 
                termos_de_credito.append(creditos * solver.Sum(cursada_neste_semestre_vars))
        if termos_de_credito: 
            solver.Add(solver.Sum(termos_de_credito) <= CREDITOS_MAXIMOS_POR_SEMESTRE)

    # R7: Regras Específicas (Estágio) -> Estágio apenas após metade das disciplinas totais concluídas
    id_estagio = "EEWU00"
    if id_estagio in semestre_da_disciplina and id_estagio not in cursadas_set:
        total_disciplinas = len(disciplinas)
        metade_total = total_disciplinas / 2.0
        M_estagio = total_disciplinas + 1

        for s in range(1, NUM_SEMESTRES + 1):
            # Variáveis de alocação do estágio neste semestre
            vars_estagio_s = [var for (d, sem, t), var in alocacao.items() if d == id_estagio and sem == s]
  
            if not vars_estagio_s:
                continue

            is_estagio_in_s = solver.Sum(vars_estagio_s)

            # Contar disciplinas concluídas ANTES do semestre s
            # 1. Já cursadas
            count_cursadas_past = len(cursadas_set)
 
            # 2. Cursadas nos semestres anteriores (1 até s-1)
            vars_concluidas_antes_s = []
            for d_other in disciplinas:
                if d_other in cursadas_set: continue
                if d_other == id_estagio: continue

                # Soma alocações de d_other em semestres < s
                for sem_past in range(1, s):
                    for t_other in turmas_por_disciplina.get(d_other, []):
                        if (d_other, sem_past, t_other) in alocacao:
                            vars_concluidas_antes_s.append(alocacao[(d_other, sem_past, t_other)])
            
            total_concluidas_antes_s = count_cursadas_past + solver.Sum(vars_concluidas_antes_s)
            
            # Se estágio for em s, então total_concluidas >= metade
            solver.Add(total_concluidas_antes_s >= metade_total - M_estagio * (1 - is_estagio_in_s))

    # --- 5. Função Objetivo ---
    # Minimizar o semestre máximo de TODAS as disciplinas CURSADAS
    
    semestre_maximo = solver.IntVar(1, NUM_SEMESTRES, 'semestre_maximo')
    M_obj = NUM_SEMESTRES + 1 

    for d_id in disciplinas:
        if d_id in cursadas_set: continue

        solver.Add(semestre_maximo >= semestre_da_disciplina[d_id] - M_obj * (1 - cursada_vars[d_id]))

    solver.Minimize(semestre_maximo)

    # --- 6. Chamar o Solver ---
    print(f"Número de variáveis: {solver.NumVariables()}")
    print(f"Número de restrições: {solver.NumConstraints()}")
    solver.set_time_limit(300 * 1000) 
    status = solver.Solve()
    
    # --- 7. Processar e Retornar os Resultados ---
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        grade = {s: [] for s in range(1, NUM_SEMESTRES + 1)}
        creditos_por_semestre = {s: 0 for s in range(1, NUM_SEMESTRES + 1)}
        
        # Estrutura para relatório de créditos
        creditos_por_tipo = {
            "Obrigatória": 0,
            "Escolha Restrita": 0,
            "Escolha Condicionada": 0,
            "Livre Escolha": 0,
            "Outros": 0
        }

        # Adicionar créditos das disciplinas JÁ cursadas
        for d_id in cursadas_set:
            if d_id in disciplinas:
                tipo = disciplinas[d_id].get("tipo", "Outros")
                cred = int(disciplinas[d_id].get("creditos", 0))
                
                # Normalizar tipos
                if "Obrigatória" in tipo: key = "Obrigatória"
                elif "Restrita" in tipo: key = "Escolha Restrita"
                elif "Condicionada" in tipo: key = "Escolha Condicionada"
                elif "Livre" in tipo: key = "Livre Escolha"
                else: key = "Outros"
                
                creditos_por_tipo[key] += cred

        for (d_id, s, t_id), var in alocacao.items():
            if var.solution_value() > 0.5:
                # Obter dados completos da disciplina
                disc_data = disciplinas[d_id]
                horarios = horarios_por_turma.get(t_id, [])
                
                # Objeto estruturado
                disciplina_obj = {
                    "id": d_id,
                    "nome": disc_data["nome"],
                    "turma": t_id,
                    "horarios": horarios,
                    "creditos": disc_data["creditos"],
                    "tipo": disc_data.get("tipo", "Desconhecido")
                }
                
                grade[s].append(disciplina_obj)
                creditos_por_semestre[s] += disc_data['creditos']
                
                # Contabilizar créditos das disciplinas SUGERIDAS
                tipo = disc_data.get("tipo", "Outros")
                cred = int(disc_data.get("creditos", 0))
                
                if "Obrigatória" in tipo: key = "Obrigatória"
                elif "Restrita" in tipo: key = "Escolha Restrita"
                elif "Condicionada" in tipo: key = "Escolha Condicionada"
                elif "Livre" in tipo: key = "Livre Escolha"
                else: key = "Outros"
                
                creditos_por_tipo[key] += cred
        
        return grade, creditos_por_semestre, status, solver.Objective().Value(), creditos_por_tipo
    
    return None, None, status, None, None