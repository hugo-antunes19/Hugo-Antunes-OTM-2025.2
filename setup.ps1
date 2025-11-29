# Script de setup para Windows PowerShell
# Cria ambiente virtual e instala dependências

Write-Host "🎓 Configurando Otimizador de Grade Horária..." -ForegroundColor Cyan
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado. Por favor, instale Python 3.8 ou superior." -ForegroundColor Red
    exit 1
}

# Criar ambiente virtual
if (Test-Path "venv") {
    Write-Host "⚠️  Ambiente virtual já existe. Removendo..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

Write-Host "📦 Criando ambiente virtual..." -ForegroundColor Cyan
python -m venv venv

# Ativar ambiente virtual
Write-Host "🔌 Ativando ambiente virtual..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Verificar se a ativação funcionou
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Aviso: Ambiente virtual pode não estar ativo." -ForegroundColor Yellow
    Write-Host "   Se necessário, execute: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
}

# Atualizar pip
Write-Host "⬆️  Atualizando pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip --quiet

# Instalar dependências
Write-Host "📥 Instalando dependências..." -ForegroundColor Cyan
pip install -r requirements.txt

# Verificar instalação
Write-Host ""
Write-Host "🧪 Verificando instalação..." -ForegroundColor Cyan
if (python test_imports.py) {
    Write-Host ""
    Write-Host "✅ Instalação concluída com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para executar a aplicação:" -ForegroundColor Yellow
    Write-Host "  1. Ative o ambiente virtual: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  2. Execute: streamlit run app.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para desativar o ambiente virtual: deactivate" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "⚠️  Alguns testes falharam. Verifique as mensagens acima." -ForegroundColor Yellow
    exit 1
}

