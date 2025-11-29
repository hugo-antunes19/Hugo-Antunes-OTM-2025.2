"""
Configurações da aplicação.

Centraliza todas as constantes e configurações, permitindo override via variáveis de ambiente.
"""
from pathlib import Path
import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class AppConfig:
    """Configuração principal da aplicação."""
    
    # Diretórios base
    BASE_DIR: Path = Path(__file__).parent
    WEB_DIR: Path = Path(__file__).parent  # Mesmo que BASE_DIR agora
    
    # Caminhos dos arquivos de dados (podem ser sobrescritos via env vars)
    DISCIPLINAS_PATH: Path = BASE_DIR / "attempt1" / "disciplinas.json"
    OFERTAS_PATH: Path = BASE_DIR / "attempt1" / "ofertas.json"
    
    # Limites de créditos
    CREDITOS_MAXIMOS_POR_SEMESTRE: int = 32
    TOTAL_CREDITOS_CURSO: int = 240
    
    # Créditos mínimos por tipo de optativa
    CREDITOS_MINIMOS_TOTAIS: Dict[str, int] = None
    
    # Configurações do solver
    NUM_SEMESTRES_TOTAL: int = 14
    SOLVER_TIMEOUT_MS: int = 120_000  # 120 segundos
    
    # Nível de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    def __post_init__(self):
        """Inicializa valores padrão e permite override via env vars."""
        if self.CREDITOS_MINIMOS_TOTAIS is None:
            self.CREDITOS_MINIMOS_TOTAIS = {
                "restrita": 4,
                "condicionada": 40,
                "livre": 8
            }
        
        # Permitir override via variáveis de ambiente
        if os.getenv("DISCIPLINAS_PATH"):
            self.DISCIPLINAS_PATH = Path(os.getenv("DISCIPLINAS_PATH"))
        if os.getenv("OFERTAS_PATH"):
            self.OFERTAS_PATH = Path(os.getenv("OFERTAS_PATH"))
        if os.getenv("LOG_LEVEL"):
            self.LOG_LEVEL = os.getenv("LOG_LEVEL")
    
    def validate_paths(self) -> tuple:
        """
        Valida se os arquivos de configuração existem.
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem_erro)
        """
        if not self.DISCIPLINAS_PATH.exists():
            return False, f"Arquivo de disciplinas não encontrado: {self.DISCIPLINAS_PATH}"
        if not self.OFERTAS_PATH.exists():
            return False, f"Arquivo de ofertas não encontrado: {self.OFERTAS_PATH}"
        return True, ""


# Instância global de configuração
config = AppConfig()

