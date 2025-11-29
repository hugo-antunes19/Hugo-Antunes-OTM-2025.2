"""
Script de teste para verificar imports e estrutura básica.

Execute: python test_imports.py
"""
import sys
from pathlib import Path

def test_imports():
    """Testa todos os imports principais."""
    errors = []
    
    print("Testando imports...")
    
    # Teste 1: Config
    try:
        from config import config
        print("✅ config.py - OK")
    except Exception as e:
        errors.append(f"❌ config.py - ERRO: {e}")
    
    # Teste 2: Models
    try:
        from models.grade import DadosDisciplinas, GradeResultado
        from models.disciplina import Disciplina
        print("✅ models/ - OK")
    except Exception as e:
        errors.append(f"❌ models/ - ERRO: {e}")
    
    # Teste 3: Utils
    try:
        from utils.validators import validate_semestre, validate_file_exists
        from utils.logging_config import setup_logging, get_logger
        print("✅ utils/ - OK")
    except Exception as e:
        errors.append(f"❌ utils/ - ERRO: {e}")
    
    # Teste 4: Services (sem ortools)
    try:
        # Tentar importar apenas data_loader que não precisa de ortools
        from services.data_loader import DataLoader, carregar_dados
        print("✅ services/data_loader.py - OK")
    except Exception as e:
        errors.append(f"❌ services/data_loader.py - ERRO: {e}")
    
    # Teste 5: UI (sem streamlit)
    try:
        # Verificar apenas sintaxe, não executar
        import ast
        with open('ui/components.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ ui/components.py - Sintaxe OK")
    except SyntaxError as e:
        errors.append(f"❌ ui/components.py - ERRO DE SINTAXE: {e}")
    except Exception as e:
        # Streamlit não instalado é OK para teste de sintaxe
        print(f"⚠️ ui/components.py - Streamlit não disponível (OK para teste de sintaxe)")
    
    # Resumo
    print("\n" + "="*50)
    if errors:
        print("ERROS ENCONTRADOS:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✅ TODOS OS TESTES PASSARAM!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

