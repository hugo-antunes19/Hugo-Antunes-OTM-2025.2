"""
Modelos de dados para disciplinas.
"""
from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class TipoDisciplina(str, Enum):
    """Tipos de disciplina."""
    OBRIGATORIA = "obrigatoria"
    RESTRITA = "restrita"
    CONDICIONADA = "condicionada"
    LIVRE = "livre"
    OUTRA = "outra"


@dataclass
class Disciplina:
    """Representa uma disciplina do curso."""
    id: str
    nome: str
    creditos: int
    tipo: TipoDisciplina
    prerequisitos: List[str]
    periodo_sugerido: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Disciplina":
        """
        Cria instância de Disciplina a partir de dicionário.
        
        Args:
            data: Dicionário com dados da disciplina
        
        Returns:
            Instância de Disciplina
        """
        tipo_str = data.get("tipo", "")
        tipo = cls._parse_tipo(tipo_str)
        
        return cls(
            id=data["id"],
            nome=data.get("nome", ""),
            creditos=int(data.get("creditos", 0)),
            tipo=tipo,
            prerequisitos=data.get("prerequisitos", []),
            periodo_sugerido=data.get("periodo")
        )
    
    @staticmethod
    def _parse_tipo(tipo_str: str) -> TipoDisciplina:
        """
        Parse do tipo de disciplina a partir da string.
        
        Args:
            tipo_str: String com tipo da disciplina
        
        Returns:
            TipoDisciplina correspondente
        """
        tipo_str = tipo_str.lower()
        if "período" in tipo_str or "periodo" in tipo_str:
            return TipoDisciplina.OBRIGATORIA
        elif "restrita" in tipo_str:
            return TipoDisciplina.RESTRITA
        elif "condicionada" in tipo_str:
            return TipoDisciplina.CONDICIONADA
        elif "livre" in tipo_str or tipo_str.startswith("artificial"):
            return TipoDisciplina.LIVRE
        else:
            return TipoDisciplina.OUTRA
    
    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "creditos": self.creditos,
            "tipo": self.tipo.value,
            "prerequisitos": self.prerequisitos,
            "periodo_sugerido": self.periodo_sugerido
        }

