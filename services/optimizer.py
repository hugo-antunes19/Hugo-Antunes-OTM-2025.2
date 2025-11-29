"""
Serviço de otimização de grade horária usando MILP.

Implementa o modelo de otimização usando Google OR-Tools SCIP solver.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import time

from ortools.linear_solver import pywraplp

from models.grade import DadosDisciplinas, GradeResultado
from utils.logging_config import get_logger
from config import config

logger = get_logger(__name__)


@dataclass
class OptimizerConfig:
    """Configuração para o otimizador."""
    dados: DadosDisciplinas
    todas_disciplinas_info: Dict[str, dict]
    creditos_minimos: Dict[str, int]
    creditos_maximos_por_semestre: int
    disciplinas_concluidas_ids: List[str]
    semestre_inicio: int
    total_creditos_curso: int
    num_semestres_total: int = None
    solver_timeout_ms: int = None
    
    def __post_init__(self):
        """Inicializa valores padrão."""
        if self.num_semestres_total is None:
            self.num_semestres_total = config.NUM_SEMESTRES_TOTAL
        if self.solver_timeout_ms is None:
            self.solver_timeout_ms = config.SOLVER_TIMEOUT_MS


class OptimizerService:
    """Serviço de otimização de grade horária."""
    
    def __init__(self, optimizer_config: OptimizerConfig):
        """
        Inicializa o serviço de otimização.
        
        Args:
            optimizer_config: Configuração do otimizador
        """
        self.config = optimizer_config
        self.solver = None
        self._inicializar_solver()
    
    def _inicializar_solver(self):
        """Inicializa o solver SCIP."""
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.solver:
            logger.error("Solver SCIP não encontrado. Verifique instalação do OR-Tools.")
            raise RuntimeError("Solver SCIP não disponível")
        logger.info("Solver SCIP inicializado com sucesso")
    
    def resolver(self) -> GradeResultado:
        """
        Resolve o problema de otimização.
        
        Returns:
            GradeResultado com a solução encontrada
        
        Raises:
            RuntimeError: Se solver não estiver disponível
        """
        if not self.solver:
            raise RuntimeError("Solver não inicializado")
        
        start_time = time.time()
        logger.info("Iniciando otimização da grade horária")
        
        # Preparar dados
        disciplinas_a_cursar = self._preparar_disciplinas_a_cursar()
        creditos_minimos_restantes = self._calcular_creditos_minimos_restantes()
        
        # Criar variáveis de decisão
        alocacao, semestre_da_disciplina, cursada_vars = self._criar_variaveis_decisao(
            disciplinas_a_cursar
        )
        
        # Adicionar restrições
        self._adicionar_restricoes(
            disciplinas_a_cursar,
            alocacao,
            semestre_da_disciplina,
            cursada_vars,
            creditos_minimos_restantes
        )
        
        # Definir função objetivo
        self._definir_funcao_objetivo(semestre_da_disciplina, cursada_vars)
        
        # Resolver
        status = self._resolver()
        
        # Processar resultados
        resultado = self._processar_resultados(status, alocacao, start_time)
        
        logger.info(
            f"Otimização concluída - Status: {status}, "
            f"Tempo: {resultado.tempo_execucao:.2f}s"
        )
        
        return resultado
    
    def _preparar_disciplinas_a_cursar(self) -> Dict[str, List[str]]:
        """
        Prepara lista de disciplinas a cursar.
        
        Returns:
            Dicionário com obrigatórias e optativas a cursar
        """
        disciplinas_concluidas_set = set(self.config.disciplinas_concluidas_ids)
        
        obrigatorias_a_cursar = [
            d_id for d_id in self.config.dados.obrigatorias_ids
            if d_id not in disciplinas_concluidas_set
        ]
        
        optativas_a_cursar = [
            d_id for d_id in self.config.dados.optativas_ids
            if d_id not in disciplinas_concluidas_set
        ]
        
        logger.debug(
            f"Disciplinas a cursar - Obrigatórias: {len(obrigatorias_a_cursar)}, "
            f"Optativas: {len(optativas_a_cursar)}"
        )
        
        return {
            "obrigatorias": obrigatorias_a_cursar,
            "optativas": optativas_a_cursar,
            "todas": obrigatorias_a_cursar + optativas_a_cursar
        }
    
    def _calcular_creditos_minimos_restantes(self) -> Dict[str, int]:
        """
        Calcula créditos mínimos restantes por tipo de optativa.
        
        Returns:
            Dicionário com créditos mínimos restantes
        """
        creditos_feitos = {"restrita": 0, "condicionada": 0, "livre": 0}
        
        for d_id in self.config.disciplinas_concluidas_ids:
            if d_id in self.config.todas_disciplinas_info:
                disciplina = self.config.todas_disciplinas_info[d_id]
                credito_disciplina = int(disciplina.get('creditos', 0))
                tipo = disciplina.get("tipo", "").lower()
                
                if "restrita" in tipo:
                    creditos_feitos["restrita"] += credito_disciplina
                elif "condicionada" in tipo:
                    creditos_feitos["condicionada"] += credito_disciplina
                elif "livre" in tipo or d_id.startswith("ARTIFICIAL"):
                    creditos_feitos["livre"] += credito_disciplina
        
        creditos_minimos_restantes = {
            "restrita": max(0, self.config.creditos_minimos['restrita'] - creditos_feitos['restrita']),
            "condicionada": max(0, self.config.creditos_minimos['condicionada'] - creditos_feitos['condicionada']),
            "livre": max(0, self.config.creditos_minimos['livre'] - creditos_feitos['livre'])
        }
        
        logger.debug(f"Créditos mínimos restantes: {creditos_minimos_restantes}")
        
        return creditos_minimos_restantes
    
    def _criar_variaveis_decisao(
        self,
        disciplinas_a_cursar: Dict[str, List[str]]
    ) -> tuple:
        """
        Cria variáveis de decisão do modelo.
        
        Returns:
            Tupla (alocacao, semestre_da_disciplina, cursada_vars)
        """
        alocacao = {}
        disciplinas_todas = disciplinas_a_cursar["todas"]
        
        for d_id in disciplinas_todas:
            for t_id in self.config.dados.turmas_por_disciplina.get(d_id, []):
                for s in range(
                    self.config.semestre_inicio,
                    self.config.num_semestres_total + 1
                ):
                    alocacao[(d_id, s, t_id)] = self.solver.BoolVar(
                        f'alocacao_{d_id}_s{s}_t{t_id}'
                    )
        
        semestre_da_disciplina = {
            d_id: self.solver.IntVar(
                self.config.semestre_inicio,
                self.config.num_semestres_total + 1,
                f'semestre_{d_id}'
            )
            for d_id in disciplinas_todas
        }
        
        # Variáveis auxiliares para indicar se disciplina foi cursada
        cursada_vars = {}
        dummy_value = self.config.num_semestres_total + 2
        
        for d_id in disciplinas_todas:
            vars_disciplina = [
                var for key, var in alocacao.items() if key[0] == d_id
            ]
            
            if not vars_disciplina:
                cursada_vars[d_id] = self.solver.IntVar(0, 0, f'cursada_{d_id}')
                self.solver.Add(semestre_da_disciplina[d_id] == dummy_value)
                continue
            
            cursada_var = self.solver.Sum(vars_disciplina)
            cursada_vars[d_id] = cursada_var
            
            termos_semestre = [
                s * var for (d, s, t), var in alocacao.items() if d == d_id
            ]
            self.solver.Add(
                semestre_da_disciplina[d_id] ==
                self.solver.Sum(termos_semestre) +
                (1 - cursada_var) * dummy_value
            )
        
        logger.debug(
            f"Criadas {len(alocacao)} variáveis de alocação e "
            f"{len(semestre_da_disciplina)} variáveis de semestre"
        )
        
        return alocacao, semestre_da_disciplina, cursada_vars
    
    def _adicionar_restricoes(
        self,
        disciplinas_a_cursar: Dict[str, List[str]],
        alocacao: Dict,
        semestre_da_disciplina: Dict,
        cursada_vars: Dict,
        creditos_minimos_restantes: Dict[str, int]
    ):
        """Adiciona todas as restrições do modelo."""
        # R1: Obrigatórias devem ser cursadas exatamente uma vez
        self._adicionar_restricao_obrigatorias(
            disciplinas_a_cursar["obrigatorias"],
            alocacao
        )
        
        # R2: Optativas podem ser cursadas no máximo uma vez
        self._adicionar_restricao_optativas(
            disciplinas_a_cursar["optativas"],
            alocacao
        )
        
        # R3: Créditos mínimos por tipo de optativa
        self._adicionar_restricao_creditos_minimos(
            cursada_vars,
            creditos_minimos_restantes
        )
        
        # R4: Pré-requisitos
        self._adicionar_restricao_prerequisitos(
            disciplinas_a_cursar["todas"],
            cursada_vars,
            semestre_da_disciplina
        )
        
        # R5: Conflitos de horário
        self._adicionar_restricao_conflitos_horario(alocacao)
        
        # R6: Limite de créditos por semestre
        self._adicionar_restricao_limite_creditos(alocacao)
    
    def _adicionar_restricao_obrigatorias(
        self,
        obrigatorias: List[str],
        alocacao: Dict
    ):
        """R1: Obrigatórias devem ser cursadas exatamente uma vez."""
        for d_id in obrigatorias:
            vars_obrigatoria = [
                var for key, var in alocacao.items() if key[0] == d_id
            ]
            if not vars_obrigatoria:
                logger.warning(
                    f"Disciplina obrigatória {d_id} não tem oferta de turma"
                )
                continue
            self.solver.Add(self.solver.Sum(vars_obrigatoria) == 1)
    
    def _adicionar_restricao_optativas(
        self,
        optativas: List[str],
        alocacao: Dict
    ):
        """R2: Optativas podem ser cursadas no máximo uma vez."""
        for d_id in optativas:
            vars_optativa = [
                var for key, var in alocacao.items() if key[0] == d_id
            ]
            if vars_optativa:
                self.solver.Add(self.solver.Sum(vars_optativa) <= 1)
    
    def _adicionar_restricao_creditos_minimos(
        self,
        cursada_vars: Dict,
        creditos_minimos_restantes: Dict[str, int]
    ):
        """R3: Créditos mínimos por tipo de optativa."""
        dados = self.config.dados
        
        if dados.restritas_ids:
            termos_restritas = []
            for d_id in dados.restritas_ids:
                # Verificar se disciplina existe em disciplinas e em cursada_vars
                if d_id in dados.disciplinas and d_id in cursada_vars:
                    creditos = int(dados.disciplinas[d_id]['creditos'])
                    termos_restritas.append(creditos * cursada_vars[d_id])
            
            if termos_restritas:
                self.solver.Add(
                    self.solver.Sum(termos_restritas) >= creditos_minimos_restantes['restrita']
                )
        
        if dados.condicionadas_ids:
            termos_condicionadas = []
            for d_id in dados.condicionadas_ids:
                # Verificar se disciplina existe em disciplinas e em cursada_vars
                if d_id in dados.disciplinas and d_id in cursada_vars:
                    creditos = int(dados.disciplinas[d_id]['creditos'])
                    termos_condicionadas.append(creditos * cursada_vars[d_id])
            
            if termos_condicionadas:
                self.solver.Add(
                    self.solver.Sum(termos_condicionadas) >= creditos_minimos_restantes['condicionada']
                )
        
        if dados.livres_ids:
            termos_livres = []
            for d_id in dados.livres_ids:
                # Verificar se disciplina existe em disciplinas e em cursada_vars
                if d_id in dados.disciplinas and d_id in cursada_vars:
                    creditos = int(dados.disciplinas[d_id]['creditos'])
                    termos_livres.append(creditos * cursada_vars[d_id])
            
            if termos_livres:
                self.solver.Add(
                    self.solver.Sum(termos_livres) >= creditos_minimos_restantes['livre']
                )
    
    def _adicionar_restricao_prerequisitos(
        self,
        disciplinas_todas: List[str],
        cursada_vars: Dict,
        semestre_da_disciplina: Dict
    ):
        """R4: Pré-requisitos devem ser cursados antes."""
        disciplinas_concluidas_set = set(self.config.disciplinas_concluidas_ids)
        m_prereq = self.config.num_semestres_total + 2
        
        for d_id in disciplinas_todas:
            # Verificar se disciplina existe em dados.disciplinas antes de acessar
            if d_id not in self.config.dados.disciplinas:
                continue
            
            disc_info = self.config.dados.disciplinas[d_id]
            for prereq_id in disc_info.get('prerequisitos', []):
                if prereq_id in disciplinas_concluidas_set:
                    continue
                elif prereq_id in disciplinas_todas and prereq_id in cursada_vars and d_id in cursada_vars:
                    self.solver.Add(
                        cursada_vars[prereq_id] >= cursada_vars[d_id]
                    )
                    self.solver.Add(
                        semestre_da_disciplina[d_id] - semestre_da_disciplina[prereq_id] >=
                        1 - m_prereq * (1 - cursada_vars[d_id])
                    )
    
    def _adicionar_restricao_conflitos_horario(self, alocacao: Dict):
        """R5: Não pode haver conflitos de horário no mesmo semestre."""
        for s in range(
            self.config.semestre_inicio,
            self.config.num_semestres_total + 1
        ):
            horarios_do_semestre = {}
            for (d, sem, t), var in alocacao.items():
                if sem == s:
                    for h in self.config.dados.horarios_por_turma.get(t, []):
                        if h not in horarios_do_semestre:
                            horarios_do_semestre[h] = []
                        horarios_do_semestre[h].append(var)
            
            for h, turmas_conflitantes in horarios_do_semestre.items():
                if len(turmas_conflitantes) > 1:
                    self.solver.Add(
                        self.solver.Sum(turmas_conflitantes) <= 1
                    )
    
    def _adicionar_restricao_limite_creditos(self, alocacao: Dict):
        """R6: Limite de créditos por semestre."""
        creditos_cursados_no_semestre = {}
        
        for s in range(
            self.config.semestre_inicio,
            self.config.num_semestres_total + 1
        ):
            termos_de_credito_s = []
            for d_id in self.config.dados.disciplinas:
                creditos = int(self.config.dados.disciplinas[d_id]['creditos'])
                cursada_neste_semestre_vars = [
                    var for (d, sem, t), var in alocacao.items()
                    if d == d_id and sem == s
                ]
                if cursada_neste_semestre_vars:
                    termos_de_credito_s.append(
                        creditos * self.solver.Sum(cursada_neste_semestre_vars)
                    )
            
            if termos_de_credito_s:
                creditos_cursados_no_semestre[s] = self.solver.Sum(termos_de_credito_s)
            else:
                creditos_cursados_no_semestre[s] = self.solver.IntVar(
                    0, 0, f'creditos_s{s}'
                )
            
            self.solver.Add(
                creditos_cursados_no_semestre[s] <=
                self.config.creditos_maximos_por_semestre
            )
    
    def _definir_funcao_objetivo(
        self,
        semestre_da_disciplina: Dict,
        cursada_vars: Dict
    ):
        """Define a função objetivo: minimizar semestre máximo."""
        semestre_maximo = self.solver.IntVar(
            self.config.semestre_inicio,
            self.config.num_semestres_total,
            'semestre_maximo'
        )
        m_obj = self.config.num_semestres_total + 2
        
        for d_id in cursada_vars:
            self.solver.Add(
                semestre_maximo >=
                semestre_da_disciplina[d_id] -
                m_obj * (1 - cursada_vars[d_id])
            )
        
        self.solver.Minimize(semestre_maximo)
    
    def _resolver(self) -> int:
        """
        Executa o solver.
        
        Returns:
            Status do solver
        """
        self.solver.set_time_limit(self.config.solver_timeout_ms)
        status = self.solver.Solve()
        return status
    
    def _processar_resultados(
        self,
        status: int,
        alocacao: Dict,
        start_time: float
    ) -> GradeResultado:
        """
        Processa resultados do solver.
        
        Args:
            status: Status do solver
            alocacao: Variáveis de alocação
            start_time: Tempo de início
        
        Returns:
            GradeResultado processado
        """
        tempo_execucao = time.time() - start_time
        
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            grade = {
                s: [] for s in range(
                    self.config.semestre_inicio,
                    self.config.num_semestres_total + 1
                )
            }
            creditos_por_semestre = {
                s: 0 for s in range(
                    self.config.semestre_inicio,
                    self.config.num_semestres_total + 1
                )
            }
            
            for (d_id, s, t_id), var in alocacao.items():
                if var.solution_value() > 0.5:
                    # Verificar se disciplina existe antes de acessar
                    if d_id not in self.config.dados.disciplinas:
                        logger.warning(f"Disciplina {d_id} alocada mas não encontrada em dados.disciplinas")
                        continue
                    
                    disciplina_alocada = {
                        "nome": self.config.dados.disciplinas[d_id]["nome"],
                        "turma": t_id,
                        "horarios": self.config.dados.horarios_por_turma.get(t_id, []),
                        "creditos": self.config.dados.disciplinas[d_id]['creditos']
                    }
                    grade[s].append(disciplina_alocada)
                    creditos_por_semestre[s] += int(
                        self.config.dados.disciplinas[d_id]['creditos']
                    )
            
            # Filtrar semestres vazios
            grade_filtrada = {s: g for s, g in grade.items() if g}
            
            obj_val = self.solver.Objective().Value()
            
            return GradeResultado(
                grade=grade_filtrada,
                creditos_por_semestre=creditos_por_semestre,
                status=status,
                objetivo_value=obj_val,
                tempo_execucao=tempo_execucao
            )
        else:
            return GradeResultado(
                grade={},
                creditos_por_semestre={},
                status=status,
                objetivo_value=None,
                tempo_execucao=tempo_execucao
            )


# Função de conveniência para compatibilidade
def resolver_grade(
    dados: DadosDisciplinas,
    todas_disciplinas_info: Dict[str, dict],
    creditos_minimos: Dict[str, int],
    creditos_maximos_por_semestre: int,
    disciplinas_concluidas_ids: List[str],
    semestre_inicio: int,
    total_creditos_curso: int
) -> tuple:
    """
    Função de conveniência para resolver grade.
    
    Retorna tupla para compatibilidade com código antigo.
    """
    optimizer_config = OptimizerConfig(
        dados=dados,
        todas_disciplinas_info=todas_disciplinas_info,
        creditos_minimos=creditos_minimos,
        creditos_maximos_por_semestre=creditos_maximos_por_semestre,
        disciplinas_concluidas_ids=disciplinas_concluidas_ids,
        semestre_inicio=semestre_inicio,
        total_creditos_curso=total_creditos_curso
    )
    
    service = OptimizerService(optimizer_config)
    resultado = service.resolver()
    
    # Retornar no formato antigo para compatibilidade
    return (
        resultado.grade,
        resultado.creditos_por_semestre,
        resultado.status,
        resultado.objetivo_value
    )

