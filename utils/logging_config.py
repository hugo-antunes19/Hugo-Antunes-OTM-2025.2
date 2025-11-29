"""
Configuração de logging da aplicação.

Fornece logging estruturado com diferentes níveis e handlers.
"""
import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from config import config
except ImportError:
    # Fallback para quando config não está disponível
    import logging as _logging
    config = type('Config', (), {
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'app.log'
    })()


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho do arquivo de log (opcional)
    
    Returns:
        Logger configurado
    """
    log_level = getattr(logging, (level or config.LOG_LEVEL).upper(), logging.INFO)
    log_file_path = log_file or config.LOG_FILE
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # Adicionar arquivo de log se especificado
    if log_file_path:
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding='utf-8'))
    
    # Configurar logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Sobrescrever configuração anterior se existir
    )
    
    # Configurar formatter em todos os handlers
    for handler in handlers:
        handler.setFormatter(formatter)
    
    logger = logging.getLogger(__name__)
    # Usar mensagem sem acentos para evitar problemas de encoding
    level_name = logging.getLevelName(log_level)
    logger.info(f"Logging configurado - Nivel: {level_name}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger com o nome especificado.
    
    Args:
        name: Nome do logger (geralmente __name__)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)

