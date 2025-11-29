"""
Modelos de dados para grades horárias.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class GradeSemestre:
    """Representa a grade de um semestre específico."""
    semestre: int
    disciplinas: List[Dict]  # Lista de disciplinas com turma e horários
    creditos_total: int
    
    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "semestre": self.semestre,
            "disciplinas": self.disciplinas,
            "creditos_total": self.creditos_total
        }


@dataclass
class GradeResultado:
    """Resultado da otimização da grade."""
    grade: Dict[int, List[Dict]]  # semestre -> lista de disciplinas
    creditos_por_semestre: Dict[int, int]
    status: int  # Status do solver
    objetivo_value: Optional[float] = None
    tempo_execucao: Optional[float] = None
    
    @property
    def sucesso(self) -> bool:
        """Verifica se a otimização foi bem-sucedida."""
        from ortools.linear_solver import pywraplp
        return self.status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE)
    
    @property
    def infactivel(self) -> bool:
        """Verifica se o modelo é infactível."""
        from ortools.linear_solver import pywraplp
        return self.status == pywraplp.Solver.INFEASIBLE


@dataclass
class DadosDisciplinas:
    """Estrutura de dados carregada e processada."""
    disciplinas: Dict[str, dict]
    turmas_por_disciplina: Dict[str, List[str]]
    horarios_por_turma: Dict[str, List[str]]
    periodos_validos_por_disciplina: Dict[str, set]
    obrigatorias_ids: List[str]
    restritas_ids: List[str]
    condicionadas_ids: List[str]
    livres_ids: List[str]
    
    @property
    def optativas_ids(self) -> List[str]:
        """Retorna todas as IDs de optativas."""
        return self.restritas_ids + self.condicionadas_ids + self.livres_ids
    
    @property
    def todas_disciplinas_ids(self) -> List[str]:
        """Retorna todas as IDs de disciplinas."""
        return (
            self.obrigatorias_ids +
            self.restritas_ids +
            self.condicionadas_ids +
            self.livres_ids
        )

