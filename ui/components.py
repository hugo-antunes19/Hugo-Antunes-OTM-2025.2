"""
Componentes reutilizáveis da interface Streamlit.
"""
import pandas as pd
import streamlit as st
from typing import Dict, List, Set

from models.grade import GradeResultado
from utils.logging_config import get_logger

logger = get_logger(__name__)


def criar_grade_semanal(disciplinas_do_semestre: List[Dict]) -> pd.DataFrame:
    """
    Cria DataFrame com grade horária semanal.
    
    Args:
        disciplinas_do_semestre: Lista de disciplinas com horários
    
    Returns:
        DataFrame com grade horária
    """
    dias_semana = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB"]
    slots_horas_padrao = [
        "08-10", "10-12", "13-15", "15-17",
        "17-19", "19-21", "21-23"
    ]
    
    # Coletar todos os slots presentes nas disciplinas
    slots_presentes = set(slots_horas_padrao)
    
    for disciplina in disciplinas_do_semestre:
        for horario_str in disciplina.get("horarios", []):
            try:
                partes = horario_str.split("-")
                if len(partes) >= 3:
                    # Formato: DIA-HH-MM ou DIA-HH-MM-HH-MM
                    slot = f"{partes[1]}-{partes[2]}"
                    slots_presentes.add(slot)
            except Exception as e:
                logger.warning(f"Erro ao processar horário '{horario_str}': {e}")
    
    slots_index = sorted(list(slots_presentes))
    if not slots_index:
        slots_index = slots_horas_padrao
    
    # Criar DataFrame vazio
    df = pd.DataFrame(index=slots_index, columns=dias_semana).fillna("")
    
    # Preencher grade
    for disciplina in disciplinas_do_semestre:
        nome_disciplina = disciplina.get("nome", "Desconhecida")
        turma = disciplina.get("turma", "")
        
        for horario_str in disciplina.get("horarios", []):
            try:
                partes = horario_str.split("-")
                if len(partes) >= 3:
                    dia = partes[0]
                    slot = f"{partes[1]}-{partes[2]}"
                    
                    if dia in df.columns and slot in df.index:
                        texto_disciplina = f"{nome_disciplina} (Turma: {turma})"
                        
                        if df.loc[slot, dia] == "":
                            df.loc[slot, dia] = texto_disciplina
                        else:
                            df.loc[slot, dia] += f" / {texto_disciplina}"
                    else:
                        logger.warning(
                            f"Horário '{horario_str}' fora da grade "
                            f"(dia: {dia}, slot: {slot})"
                        )
            except Exception as e:
                logger.warning(f"Não foi possível parsear horário: '{horario_str}'. {e}")
    
    return df


def renderizar_selecao_disciplinas(
    todas_disciplinas_info: Dict[str, dict],
    chave_prefixo: str = "select_"
) -> List[str]:
    """
    Renderiza interface de seleção de disciplinas concluídas.
    
    Args:
        todas_disciplinas_info: Dicionário com todas as disciplinas
        chave_prefixo: Prefixo para chaves do session_state
    
    Returns:
        Lista de IDs de disciplinas selecionadas
    """
    st.subheader("Disciplinas Concluídas")
    
    # Organizar disciplinas por categoria
    obrigatorias_por_periodo: Dict[str, List[tuple]] = {}
    opt_restritas: List[tuple] = []
    opt_condicionadas: List[tuple] = []
    opt_livres: List[tuple] = []
    outras: List[tuple] = []
    
    for d_id, d in todas_disciplinas_info.items():
        tipo = d.get("tipo", "")
        opcao = (f"{d['id']} - {d.get('nome', 'Nome Desconhecido')}", d['id'])
        
        if "Período" in tipo or "Periodo" in tipo:
            if tipo not in obrigatorias_por_periodo:
                obrigatorias_por_periodo[tipo] = []
            obrigatorias_por_periodo[tipo].append(opcao)
        elif "Escolha Restrita" in tipo:
            opt_restritas.append(opcao)
        elif "Escolha Condicionada" in tipo:
            opt_condicionadas.append(opcao)
        elif "Livre Escolha" in tipo or d["id"].startswith("ARTIFICIAL"):
            opt_livres.append(opcao)
        else:
            outras.append(opcao)
    
    # Criar grupos de seleção
    grupos_de_selecao: Dict[str, List[tuple]] = {}
    
    for periodo in sorted(obrigatorias_por_periodo.keys()):
        grupos_de_selecao[f"Obrigatórias - {periodo}"] = obrigatorias_por_periodo[periodo]
    
    grupos_de_selecao["Optativas - Escolha Restrita"] = opt_restritas
    grupos_de_selecao["Optativas - Escolha Condicionada"] = opt_condicionadas
    grupos_de_selecao["Optativas - Livre Escolha"] = opt_livres
    
    if outras:
        grupos_de_selecao["Outras (Estágio, TCC, etc.)"] = outras
    
    # Renderizar seletores
    all_selected_ids = set()
    
    for titulo_grupo, opcoes_grupo in grupos_de_selecao.items():
        if not opcoes_grupo:
            continue
        
        chave_estado = f"{chave_prefixo}{titulo_grupo}"
        
        if chave_estado not in st.session_state:
            st.session_state[chave_estado] = []
        
        with st.expander(titulo_grupo):
            col1, col2, _ = st.columns([1, 1, 3])
            
            # Botões para selecionar tudo ou limpar (modificam session_state ANTES do widget)
            if col1.button(f"Selecionar Tudo", key=f"btn_all_{chave_estado}"):
                # Armazenar lista completa de opções (tuplas) no formato esperado pelo multiselect
                st.session_state[chave_estado] = opcoes_grupo.copy()
                st.rerun()
            
            if col2.button(f"Limpar", key=f"btn_clear_{chave_estado}"):
                st.session_state[chave_estado] = []
                st.rerun()
            
            # Usar o valor do session_state como default (já está no formato de tuplas)
            default_selected = st.session_state[chave_estado]
            
            selected = st.multiselect(
                f"Selecione ({titulo_grupo}):",
                options=opcoes_grupo,
                format_func=lambda x: x[0],
                key=chave_estado,
                label_visibility="collapsed",
                default=default_selected
            )
            
            # Usar o valor retornado pelo multiselect diretamente
            # O Streamlit já atualiza o session_state automaticamente
            selected_ids = [item[1] for item in selected]
            all_selected_ids.update(selected_ids)
    
    return list(all_selected_ids)


def renderizar_resultados(
    resultado: GradeResultado,
    semestre_inicio: int
):
    """
    Renderiza resultados da otimização.
    
    Args:
        resultado: Resultado da otimização
        semestre_inicio: Semestre de início
    """
    st.header("3. Resultados")
    
    if resultado.sucesso:
        semestres_restantes = (
            int(resultado.objetivo_value) - semestre_inicio + 1
            if resultado.objetivo_value else 0
        )
        
        st.success("🎉 Solução encontrada!")
        
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Número Mínimo de Semestres Restantes",
            f"{semestres_restantes} Semestres"
        )
        col2.metric(
            "Semestre de Conclusão Previsto",
            f"{int(resultado.objetivo_value)}º Semestre"
            if resultado.objetivo_value else "N/A"
        )
        col3.metric(
            "Tempo de Execução",
            f"{resultado.tempo_execucao:.2f}s"
            if resultado.tempo_execucao else "N/A"
        )
        
        st.subheader("Grade Horária Sugerida:")
        
        for s in sorted(resultado.grade.keys()):
            st.markdown("---")
            st.markdown(
                f"#### Semestre {s} "
                f"(Total: {resultado.creditos_por_semestre.get(s, 0)} créditos)"
            )
            
            disciplinas_do_semestre = resultado.grade[s]
            
            if disciplinas_do_semestre:
                df_grade = criar_grade_semanal(disciplinas_do_semestre)
                st.dataframe(df_grade, use_container_width=True)
                
                with st.expander("Lista de disciplinas deste semestre"):
                    for d in disciplinas_do_semestre:
                        st.markdown(
                            f"- **{d['nome']}** "
                            f"(Turma: {d['turma']}, Créditos: {d['creditos']})"
                        )
            else:
                st.write("Nenhuma disciplina alocada neste semestre.")
    
    elif resultado.infactivel:
        st.error("❌ Nenhuma solução encontrada: O modelo é infactível.")
        st.info(
            "Isso pode acontecer se:\n"
            "- Há conflitos de horário insuperáveis\n"
            "- Os créditos mínimos não podem ser alcançados\n"
            "- Há pré-requisitos impossíveis de satisfazer"
        )
    else:
        st.error(f"❌ Nenhuma solução encontrada (status: {resultado.status}).")
        st.info("Tente ajustar os parâmetros ou verifique os logs para mais detalhes.")

