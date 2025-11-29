#!/bin/bash

# Script de setup para Linux/macOS
# Cria ambiente virtual e instala dependências

set -e  # Parar em caso de erro

echo "🎓 Configurando Otimizador de Grade Horária..."
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual
if [ -d "venv" ]; then
    echo "⚠️  Ambiente virtual já existe. Removendo..."
    rm -rf venv
fi

echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip --quiet

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Verificar instalação
echo ""
echo "🧪 Verificando instalação..."
if python test_imports.py; then
    echo ""
    echo "✅ Instalação concluída com sucesso!"
    echo ""
    echo "Para executar a aplicação:"
    echo "  1. Ative o ambiente virtual: source venv/bin/activate"
    echo "  2. Execute: streamlit run app.py"
    echo ""
    echo "Para desativar o ambiente virtual: deactivate"
else
    echo ""
    echo "⚠️  Alguns testes falharam. Verifique as mensagens acima."
    exit 1
fi

