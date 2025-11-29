"""Serviços da aplicação."""

from .data_loader import DataLoader, carregar_dados

# Importação lazy do optimizer para evitar erro se ortools não estiver instalado
def _lazy_import_optimizer():
    """Importa optimizer apenas quando necessário."""
    from .optimizer import OptimizerService, OptimizerConfig
    return OptimizerService, OptimizerConfig

# Tornar disponível via getattr para compatibilidade
__all__ = [
    "DataLoader",
    "carregar_dados",
    "OptimizerService",
    "OptimizerConfig",
]

# Exportar via __getattr__ para lazy loading
def __getattr__(name):
    if name in ("OptimizerService", "OptimizerConfig"):
        OptimizerService, OptimizerConfig = _lazy_import_optimizer()
        globals()[name] = OptimizerService if name == "OptimizerService" else OptimizerConfig
        return globals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

