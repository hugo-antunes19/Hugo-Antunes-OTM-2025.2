"""
Validações de entrada e dados.

Fornece funções de validação para garantir integridade dos dados.
"""
from typing import List, Set, Optional
from pathlib import Path
import re

try:
    from config import config
except ImportError:
    # Fallback para quando config não está disponível
    config = type('Config', (), {
        'NUM_SEMESTRES_TOTAL': 14
    })()


class ValidationError(Exception):
    """Exceção customizada para erros de validação."""
    pass


def validate_semestre(
    numero: int,
    min_val: int = 1,
    max_val: Optional[int] = None
) -> bool:
    """
    Valida número de semestre.
    
    Args:
        numero: Número do semestre a validar
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido (usa config.NUM_SEMESTRES_TOTAL se None)
    
    Returns:
        True se válido
    
    Raises:
        TypeError: Se não for inteiro
        ValueError: Se estiver fora do range
    """
    if not isinstance(numero, int):
        raise TypeError(f"Semestre deve ser inteiro, recebido {type(numero).__name__}")
    
    max_val = max_val or config.NUM_SEMESTRES_TOTAL
    if not (min_val <= numero <= max_val):
        raise ValueError(
            f"Semestre deve estar entre {min_val} e {max_val}, recebido {numero}"
        )
    return True


def validate_file_exists(path: Path) -> Path:
    """
    Valida existência de arquivo.
    
    Args:
        path: Caminho do arquivo a validar
    
    Returns:
        Path validado
    
    Raises:
        FileNotFoundError: Se arquivo não existir
        ValueError: Se não for um arquivo
    """
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    if not path.is_file():
        raise ValueError(f"Caminho não é um arquivo: {path}")
    return path


def validate_disciplina_ids(
    disciplina_ids: List[str],
    disciplinas_validas: Set[str],
    allow_empty: bool = True
) -> List[str]:
    """
    Valida lista de IDs de disciplinas.
    
    Args:
        disciplina_ids: Lista de IDs a validar
        disciplinas_validas: Set de IDs válidos
        allow_empty: Se permite lista vazia
    
    Returns:
        Lista de IDs válidos
    
    Raises:
        ValidationError: Se houver IDs inválidos
    """
    if not isinstance(disciplina_ids, list):
        raise TypeError(f"disciplina_ids deve ser lista, recebido {type(disciplina_ids).__name__}")
    
    if not disciplina_ids and not allow_empty:
        raise ValidationError("Lista de disciplinas não pode estar vazia")
    
    ids_invalidos = set(disciplina_ids) - disciplinas_validas
    if ids_invalidos:
        raise ValidationError(
            f"IDs de disciplinas inválidos encontrados: {', '.join(sorted(ids_invalidos))}"
        )
    
    return disciplina_ids


def validate_horario_format(horario_str: str) -> bool:
    """
    Valida formato de string de horário.
    
    Formato esperado: "DIA-HH-MM" (ex: "SEG-08-10", "TER-13-15")
    
    Args:
        horario_str: String de horário a validar
    
    Returns:
        True se formato válido
    
    Raises:
        ValueError: Se formato inválido
    """
    if not isinstance(horario_str, str):
        raise TypeError(f"horario_str deve ser string, recebido {type(horario_str).__name__}")
    
    # Padrão: DIA-HH-MM ou DIA-HH-MM-HH-MM (para horários compostos)
    pattern = r'^(SEG|TER|QUA|QUI|SEX|SAB|DOM)-(\d{2})-(\d{2})(?:-(\d{2})-(\d{2}))?$'
    
    if not re.match(pattern, horario_str):
        raise ValueError(
            f"Formato de horário inválido: '{horario_str}'. "
            f"Esperado: 'DIA-HH-MM' (ex: 'SEG-08-10')"
        )
    
    return True


def validate_creditos(creditos: int, min_val: int = 0, max_val: int = 100) -> bool:
    """
    Valida número de créditos.
    
    Args:
        creditos: Número de créditos
        min_val: Valor mínimo
        max_val: Valor máximo
    
    Returns:
        True se válido
    
    Raises:
        ValueError: Se fora do range
    """
    if not isinstance(creditos, int):
        raise TypeError(f"Créditos deve ser inteiro, recebido {type(creditos).__name__}")
    
    if not (min_val <= creditos <= max_val):
        raise ValueError(
            f"Créditos deve estar entre {min_val} e {max_val}, recebido {creditos}"
        )
    return True

