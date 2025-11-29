"""
Aplicação Streamlit para otimização de grade horária.

Aplicação web interativa para gerar grades curriculares otimizadas usando MILP.
"""
import json
import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional

from config import config
from models.grade import DadosDisciplinas, GradeResultado
from services.data_loader import DataLoader
from ui.components import (
    renderizar_selecao_disciplinas,
    renderizar_resultados
)
from utils.logging_config import setup_logging, get_logger
from utils.validators import validate_semestre, validate_file_exists

# Configurar logging
logger = setup_logging()

# Importação lazy do optimizer para evitar erro se ortools não estiver instalado
# até que seja realmente necessário
def _get_optimizer_classes():
    """Importa classes do optimizer apenas quando necessário."""
    try:
        from services.optimizer import OptimizerService, OptimizerConfig
        return OptimizerService, OptimizerConfig
    except ImportError as e:
        logger.error(f"Erro ao importar otimizador: {e}")
        logger.error("Certifique-se de que ortools está instalado: pip install ortools")
        raise

# Configuração da página
st.set_page_config(
    page_title="Otimizador de Grade Horária",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def carregar_disciplinas_completas() -> Dict[str, dict]:
    """
    Carrega informações completas de todas as disciplinas.
    
    Returns:
        Dicionário com todas as disciplinas
    
    Raises:
        FileNotFoundError: Se arquivo não existir
        json.JSONDecodeError: Se JSON inválido
    """
    try:
        validate_file_exists(config.DISCIPLINAS_PATH)
        with open(config.DISCIPLINAS_PATH, 'r', encoding='utf-8') as f:
            disciplinas = json.load(f)
        
        todas_disciplinas_info = {d['id']: d for d in disciplinas}
        logger.info(f"Carregadas {len(todas_disciplinas_info)} disciplinas com sucesso")
        return todas_disciplinas_info
    
    except FileNotFoundError as e:
        logger.error(f"Arquivo de disciplinas não encontrado: {e}")
        st.error(f"❌ ERRO CRÍTICO: Não foi possível ler {config.DISCIPLINAS_PATH}")
        st.error(f"Verifique se o arquivo existe e tente novamente.")
        st.stop()
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        st.error(f"❌ ERRO: Arquivo JSON inválido: {config.DISCIPLINAS_PATH}")
        st.stop()
    except Exception as e:
        logger.exception(f"Erro inesperado ao carregar disciplinas: {e}")
        st.error(f"❌ ERRO INESPERADO: {e}")
        st.stop()


def validar_configuracao() -> tuple:
    """
    Valida configuração da aplicação.
    
    Returns:
        Tupla (sucesso, mensagem_erro)
    """
    sucesso, mensagem = config.validate_paths()
    if not sucesso:
        logger.error(f"Validação de configuração falhou: {mensagem}")
    return sucesso, mensagem


def processar_otimizacao(
    disciplinas_concluidas_ids: List[str],
    semestre_inicio: int,
    todas_disciplinas_info: Dict[str, dict]
) -> Optional[GradeResultado]:
    """
    Processa otimização da grade horária.
    
    Args:
        disciplinas_concluidas_ids: IDs de disciplinas concluídas
        semestre_inicio: Semestre de início
        todas_disciplinas_info: Informações completas de todas as disciplinas
    
    Returns:
        GradeResultado ou None em caso de erro
    """
    try:
        # Carregar dados
        logger.info("Carregando dados para otimização")
        loader = DataLoader()
        dados = loader.carregar_dados(disciplinas_concluidas_ids)
        
        if not dados or not dados.disciplinas:
            st.error("❌ Nenhuma disciplina disponível para otimização.")
            logger.warning("Nenhuma disciplina disponível após filtragem")
            return None
        
        # Importar classes do otimizador (lazy loading)
        OptimizerService, OptimizerConfig = _get_optimizer_classes()
        
        # Criar configuração do otimizador
        optimizer_config = OptimizerConfig(
            dados=dados,
            todas_disciplinas_info=todas_disciplinas_info,
            creditos_minimos=config.CREDITOS_MINIMOS_TOTAIS,
            creditos_maximos_por_semestre=config.CREDITOS_MAXIMOS_POR_SEMESTRE,
            disciplinas_concluidas_ids=disciplinas_concluidas_ids,
            semestre_inicio=semestre_inicio,
            total_creditos_curso=config.TOTAL_CREDITOS_CURSO
        )
        
        # Executar otimização
        optimizer_service = OptimizerService(optimizer_config)
        resultado = optimizer_service.resolver()
        
        return resultado
    
    except FileNotFoundError as e:
        logger.error(f"Arquivo não encontrado: {e}")
        st.error(f"❌ Erro ao carregar dados: {e}")
        return None
    except Exception as e:
        logger.exception(f"Erro durante otimização: {e}")
        st.error(f"❌ Erro durante otimização: {e}")
        st.info("Verifique os logs para mais detalhes.")
        return None


def main():
    """Função principal da aplicação."""
    # Título e descrição
    st.title("🎓 Otimizador de Grade Horária")
    st.write(
        "Selecione as disciplinas que você já concluiu e gere uma grade otimizada "
        "para minimizar o tempo de graduação."
    )
    
    # Validar configuração
    sucesso, mensagem_erro = validar_configuracao()
    if not sucesso:
        st.error(f"❌ {mensagem_erro}")
        st.info("Configure os caminhos dos arquivos em `config.py` ou via variáveis de ambiente.")
        st.stop()
    
    # Carregar disciplinas completas
    try:
        todas_disciplinas_info = carregar_disciplinas_completas()
    except Exception:
        st.stop()
    
    # Seção 1: Informações do usuário
    st.header("1. Suas Informações")
    
    # Seleção de disciplinas concluídas
    disciplinas_concluidas_ids = renderizar_selecao_disciplinas(
        todas_disciplinas_info
    )
    
    # Informação sobre seleção
    if disciplinas_concluidas_ids:
        st.info(f"✅ {len(disciplinas_concluidas_ids)} disciplina(s) selecionada(s) como concluídas.")
    else:
        st.info("ℹ️ Nenhuma disciplina selecionada. O otimizador considerará todas como pendentes.")
    
    # Seleção de semestre de início
    st.subheader("Próximo Semestre")
    semestre_inicio = st.number_input(
        "Qual o NÚMERO do seu próximo semestre?",
        min_value=1,
        max_value=config.NUM_SEMESTRES_TOTAL,
        value=1,
        help=f"Digite um número entre 1 e {config.NUM_SEMESTRES_TOTAL}"
    )
    
    # Validar semestre
    try:
        validate_semestre(semestre_inicio)
        st.warning(
            f"⚠️ Otimizador irá considerar que você está começando o "
            f"**{semestre_inicio}º semestre**."
        )
    except ValueError as e:
        st.error(f"❌ {e}")
        st.stop()
    
    # Seção 2: Gerar grade
    st.header("2. Gerar Grade")
    
    if st.button("🚀 Encontrar Grade Otimizada", type="primary", use_container_width=True):
        # Validar entrada
        if not disciplinas_concluidas_ids and semestre_inicio > 1:
            st.warning(
                "⚠️ Você selecionou um semestre avançado mas não marcou nenhuma disciplina "
                "como concluída. Isso pode resultar em uma solução infactível."
            )
        
        # Processar otimização
        with st.spinner("🔄 Calculando a melhor grade horária..."):
            resultado = processar_otimizacao(
                disciplinas_concluidas_ids,
                semestre_inicio,
                todas_disciplinas_info
            )
        
        # Armazenar resultado no session_state
        if resultado:
            st.session_state['ultimo_resultado'] = resultado
            st.session_state['semestre_inicio'] = semestre_inicio
    
    # Seção 3: Resultados
    if 'ultimo_resultado' in st.session_state:
        renderizar_resultados(
            st.session_state['ultimo_resultado'],
            st.session_state.get('semestre_inicio', semestre_inicio)
        )
    
    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Informações")
        st.markdown("### Configurações")
        st.text(f"Créditos máximos/semestre: {config.CREDITOS_MAXIMOS_POR_SEMESTRE}")
        st.text(f"Créditos mínimos restrita: {config.CREDITOS_MINIMOS_TOTAIS['restrita']}")
        st.text(f"Créditos mínimos condicionada: {config.CREDITOS_MINIMOS_TOTAIS['condicionada']}")
        st.text(f"Créditos mínimos livre: {config.CREDITOS_MINIMOS_TOTAIS['livre']}")
        
        st.markdown("### Sobre")
        st.markdown(
            "Esta aplicação utiliza otimização MILP (Mixed Integer Linear Programming) "
            "para encontrar a melhor distribuição de disciplinas ao longo dos semestres, "
            "respeitando pré-requisitos, conflitos de horário e limites de créditos."
        )


if __name__ == "__main__":
    main()
