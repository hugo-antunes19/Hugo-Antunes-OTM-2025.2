"""
Serviço de carregamento e processamento de dados.

Carrega dados de disciplinas e ofertas, realiza pré-processamento e filtragem.
"""
import json
from pathlib import Path
from typing import List, Dict, Set, Optional

from models.grade import DadosDisciplinas
from utils.logging_config import get_logger
from utils.validators import validate_file_exists
from config import config

logger = get_logger(__name__)


class DataLoader:
    """Classe para carregar e processar dados de disciplinas."""
    
    def __init__(
        self,
        disciplinas_path: Optional[Path] = None,
        ofertas_path: Optional[Path] = None
    ):
        """
        Inicializa o carregador de dados.
        
        Args:
            disciplinas_path: Caminho do arquivo de disciplinas
            ofertas_path: Caminho do arquivo de ofertas
        """
        self.disciplinas_path = disciplinas_path or config.DISCIPLINAS_PATH
        self.ofertas_path = ofertas_path or config.OFERTAS_PATH
        
        # Validar arquivos
        validate_file_exists(self.disciplinas_path)
        validate_file_exists(self.ofertas_path)
    
    def carregar_dados(
        self,
        disciplinas_concluidas: Optional[List[str]] = None
    ) -> DadosDisciplinas:
        """
        Carrega e processa dados das disciplinas.
        
        Args:
            disciplinas_concluidas: Lista de IDs de disciplinas já concluídas
        
        Returns:
            DadosDisciplinas processados
        
        Raises:
            FileNotFoundError: Se arquivos não existirem
            json.JSONDecodeError: Se JSON inválido
        """
        disciplinas_concluidas = disciplinas_concluidas or []
        logger.info(f"Carregando dados de {len(disciplinas_concluidas)} disciplinas concluídas")
        
        # Carregar JSONs
        disciplinas_data = self._carregar_json(self.disciplinas_path)
        ofertas_data = self._carregar_json(self.ofertas_path)
        
        logger.debug(f"Carregadas {len(disciplinas_data)} disciplinas e {len(ofertas_data)} ofertas")
        
        # Filtrar disciplinas concluídas
        disciplinas_filtradas = self._filtrar_disciplinas_concluidas(
            disciplinas_data,
            disciplinas_concluidas
        )
        
        # Categorizar disciplinas
        categorias = self._categorizar_disciplinas(disciplinas_filtradas)
        
        # Processar ofertas
        ofertas_processadas = self._processar_ofertas(
            ofertas_data,
            disciplinas_filtradas
        )
        
        # Filtrar listas de categorias para conter apenas disciplinas com ofertas
        disciplinas_com_oferta_set = set(ofertas_processadas["disciplinas"].keys())
        
        obrigatorias_filtradas = [
            d_id for d_id in categorias["obrigatorias"]
            if d_id in disciplinas_com_oferta_set
        ]
        restritas_filtradas = [
            d_id for d_id in categorias["restritas"]
            if d_id in disciplinas_com_oferta_set
        ]
        condicionadas_filtradas = [
            d_id for d_id in categorias["condicionadas"]
            if d_id in disciplinas_com_oferta_set
        ]
        livres_filtradas = [
            d_id for d_id in categorias["livres"]
            if d_id in disciplinas_com_oferta_set
        ]
        
        # Criar estrutura de dados
        dados = DadosDisciplinas(
            disciplinas=ofertas_processadas["disciplinas"],
            turmas_por_disciplina=ofertas_processadas["turmas_por_disciplina"],
            horarios_por_turma=ofertas_processadas["horarios_por_turma"],
            periodos_validos_por_disciplina=ofertas_processadas["periodos_validos"],
            obrigatorias_ids=obrigatorias_filtradas,
            restritas_ids=restritas_filtradas,
            condicionadas_ids=condicionadas_filtradas,
            livres_ids=livres_filtradas
        )
        
        logger.info(
            f"Processamento concluído: {len(dados.disciplinas)} disciplinas com ofertas "
            f"(Obrigatórias: {len(dados.obrigatorias_ids)}, "
            f"Restritas: {len(dados.restritas_ids)}, "
            f"Condicionadas: {len(dados.condicionadas_ids)}, "
            f"Livres: {len(dados.livres_ids)})"
        )
        
        return dados
    
    def _carregar_json(self, path: Path) -> List[Dict]:
        """
        Carrega arquivo JSON.
        
        Args:
            path: Caminho do arquivo
        
        Returns:
            Lista de dicionários do JSON
        
        Raises:
            FileNotFoundError: Se arquivo não existir
            json.JSONDecodeError: Se JSON inválido
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"JSON carregado: {path}")
            return data
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON {path}: {e}")
            raise
    
    def _filtrar_disciplinas_concluidas(
        self,
        disciplinas_data: List[Dict],
        disciplinas_concluidas: List[str]
    ) -> List[Dict]:
        """
        Remove disciplinas concluídas e ajusta pré-requisitos.
        
        Args:
            disciplinas_data: Lista de disciplinas
            disciplinas_concluidas: IDs de disciplinas concluídas
        
        Returns:
            Lista filtrada de disciplinas
        """
        disciplinas_concluidas_set = set(disciplinas_concluidas)
        disciplinas_filtradas = []
        
        for disciplina in disciplinas_data:
            if disciplina['id'] not in disciplinas_concluidas_set:
                # Criar cópia para não modificar original
                disciplina_filtrada = disciplina.copy()
                # Remover pré-requisitos já cumpridos
                disciplina_filtrada['prerequisitos'] = [
                    p for p in disciplina.get('prerequisitos', [])
                    if p not in disciplinas_concluidas_set
                ]
                disciplinas_filtradas.append(disciplina_filtrada)
        
        logger.debug(
            f"Filtradas {len(disciplinas_data) - len(disciplinas_filtradas)} "
            f"disciplinas concluídas"
        )
        
        return disciplinas_filtradas
    
    def _categorizar_disciplinas(self, disciplinas: List[Dict]) -> Dict[str, List[str]]:
        """
        Categoriza disciplinas por tipo.
        
        Args:
            disciplinas: Lista de disciplinas
        
        Returns:
            Dicionário com listas de IDs por categoria
        """
        categorias = {
            "obrigatorias": [],
            "restritas": [],
            "condicionadas": [],
            "livres": []
        }
        
        for disciplina in disciplinas:
            tipo = disciplina.get("tipo", "").lower()
            disciplina_id = disciplina["id"]
            
            if "período" in tipo or "periodo" in tipo:
                categorias["obrigatorias"].append(disciplina_id)
            elif "restrita" in tipo:
                categorias["restritas"].append(disciplina_id)
            elif "condicionada" in tipo:
                categorias["condicionadas"].append(disciplina_id)
            elif "livre" in tipo or disciplina_id.startswith("ARTIFICIAL"):
                categorias["livres"].append(disciplina_id)
        
        return categorias
    
    def _processar_ofertas(
        self,
        ofertas_data: List[Dict],
        disciplinas: List[Dict]
    ) -> Dict:
        """
        Processa ofertas e cria estruturas de dados.
        
        Args:
            ofertas_data: Lista de ofertas
            disciplinas: Lista de disciplinas
        
        Returns:
            Dicionário com estruturas processadas
        """
        # Criar dicionário de disciplinas por ID
        disciplinas_dict = {d['id']: d for d in disciplinas}
        
        # IDs de disciplinas com oferta
        disciplinas_ofertadas_ids = {o['disciplina_id'] for o in ofertas_data}
        
        # Filtrar apenas disciplinas com oferta
        disciplinas_com_oferta = {
            d_id: d for d_id, d in disciplinas_dict.items()
            if d_id in disciplinas_ofertadas_ids
        }
        
        # Estruturas de dados
        turmas_por_disciplina: Dict[str, List[str]] = {
            d_id: [] for d_id in disciplinas_com_oferta
        }
        horarios_por_turma: Dict[str, List[str]] = {}
        periodos_validos: Dict[str, Set[int]] = {}
        
        # Processar ofertas
        for oferta in ofertas_data:
            d_id = oferta['disciplina_id']
            t_id = oferta['turma_id']
            
            if d_id not in turmas_por_disciplina:
                continue
            
            turmas_por_disciplina[d_id].append(t_id)
            horarios_por_turma[t_id] = oferta.get('horario', [])
            
            # Processar períodos válidos
            if 'periodo' in oferta and oferta['periodo']:
                periodos = {
                    int(p.strip())
                    for p in oferta['periodo'].split(',')
                    if p.strip()
                }
                if d_id not in periodos_validos:
                    periodos_validos[d_id] = set()
                periodos_validos[d_id].update(periodos)
        
        return {
            "disciplinas": disciplinas_com_oferta,
            "turmas_por_disciplina": turmas_por_disciplina,
            "horarios_por_turma": horarios_por_turma,
            "periodos_validos": periodos_validos
        }


# Função de conveniência para compatibilidade
def carregar_dados(
    caminho_disciplinas: Path,
    caminho_ofertas: Path,
    disciplinas_concluidas: Optional[List[str]] = None
) -> DadosDisciplinas:
    """
    Função de conveniência para carregar dados.
    
    Args:
        caminho_disciplinas: Caminho do arquivo de disciplinas
        caminho_ofertas: Caminho do arquivo de ofertas
        disciplinas_concluidas: Lista de IDs de disciplinas concluídas
    
    Returns:
        DadosDisciplinas processados
    """
    loader = DataLoader(caminho_disciplinas, caminho_ofertas)
    return loader.carregar_dados(disciplinas_concluidas)

