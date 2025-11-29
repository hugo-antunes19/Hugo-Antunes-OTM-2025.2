# 🎓 Hugo Antunes OTM 2025.2

Aplicação web interativa para otimização de grades curriculares usando Programação Linear Inteira Mista (MILP).

**Repositório:** Hugo Antunes OTM 2025.2

## 📋 Pré-requisitos

- **Python 3.8 ou superior**
- **pip** (geralmente incluído com Python)
- **Git** (opcional, para clonar o repositório)

## 🚀 Instalação Rápida

### Opção 1: Script Automatizado (Recomendado)

#### Windows (PowerShell)
```powershell
.\setup.ps1
```

#### Linux/macOS
```bash
chmod +x setup.sh
./setup.sh
```

### Opção 2: Instalação Manual

#### 1. Clone ou navegue até o diretório do projeto
```bash
git clone <url-do-repositorio>
cd "Hugo Antunes OTM 2025.2"
```

#### 2. Crie e ative um ambiente virtual

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 **Nota:** Se você receber um erro de política de execução no PowerShell (Windows), execute:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

#### 3. Atualize o pip (recomendado)
```bash
python -m pip install --upgrade pip
```

#### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

#### 5. Verifique a instalação
```bash
python test_imports.py
```

## ▶️ Execução

### Ativar o ambiente virtual (se ainda não estiver ativo)

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Executar a aplicação

```bash
streamlit run app.py
```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`.

### Desativar o ambiente virtual

Quando terminar de usar a aplicação:
```bash
deactivate
```

## 📁 Estrutura do Projeto

```
Hugo Antunes OTM 2025.2/
├── app.py                      # Entry point Streamlit
├── config.py                   # Configurações centralizadas
├── requirements.txt            # Dependências Python
├── setup.sh                    # Script de setup (Linux/macOS)
├── setup.ps1                   # Script de setup (Windows)
├── test_imports.py             # Script de teste de imports
├── Relatorio_Otimizador_Grade.ipynb  # Notebook de relatório e execução
├── attempt1/                   # Dados de disciplinas e ofertas
│   ├── disciplinas.json       # Arquivo JSON com disciplinas
│   └── ofertas.json           # Arquivo JSON com ofertas
├── attempt2/                   # Dados alternativos
│   └── disciplinas.json
├── baseModel/                  # Modelo base de dados
│   ├── disciplinas.json
│   └── ofertas.json
├── models/                     # Modelos de dados
│   ├── disciplina.py          # Modelo de disciplina
│   └── grade.py               # Modelos de grade horária
├── services/                   # Lógica de negócio
│   ├── data_loader.py         # Carregamento e processamento de dados
│   └── optimizer.py           # Serviço de otimização MILP
├── utils/                      # Utilitários
│   ├── logging_config.py      # Configuração de logging
│   └── validators.py          # Validações de entrada
└── ui/                         # Componentes de interface
    └── components.py          # Componentes Streamlit reutilizáveis
```

## ⚙️ Configuração

### Arquivos de Dados

Certifique-se de que os arquivos de dados existem:
- `attempt1/disciplinas.json`
- `attempt1/ofertas.json`

Os arquivos de dados estão no diretório raiz do projeto junto com o código.

Ou configure os caminhos via variáveis de ambiente (veja abaixo).

### Via Arquivo de Configuração

Edite `config.py` para alterar:
- Caminhos dos arquivos de dados
- Limites de créditos
- Configurações do solver
- Nível de logging

### Via Variáveis de Ambiente

**Windows (PowerShell):**
```powershell
$env:DISCIPLINAS_PATH="C:\caminho\para\disciplinas.json"
$env:OFERTAS_PATH="C:\caminho\para\ofertas.json"
$env:LOG_LEVEL="DEBUG"
```

**Linux/macOS:**
```bash
export DISCIPLINAS_PATH="/caminho/para/disciplinas.json"
export OFERTAS_PATH="/caminho/para/ofertas.json"
export LOG_LEVEL="DEBUG"
```

## 🎯 Funcionalidades

- ✅ Seleção interativa de disciplinas concluídas
- ✅ Otimização automática da grade horária
- ✅ Visualização de grade semanal
- ✅ Respeito a pré-requisitos
- ✅ Detecção de conflitos de horário
- ✅ Limites de créditos por semestre
- ✅ Minimização do tempo de graduação

## 🔧 Desenvolvimento

### Estrutura de Código

O projeto segue uma arquitetura modular:
- **models/**: Modelos de dados e estruturas
- **services/**: Lógica de negócio e processamento
- **utils/**: Utilitários e helpers
- **ui/**: Componentes de interface do usuário

### Logging

O sistema de logging está configurado em `utils/logging_config.py`. Logs são escritos em:
- Console (stdout)
- Arquivo `app.log` (se configurado)

### Validações

Validações de entrada estão em `utils/validators.py`:
- Validação de semestre
- Validação de arquivos
- Validação de IDs de disciplinas
- Validação de formato de horários

### Testes

Para adicionar testes, crie arquivos em `tests/` seguindo o padrão `test_*.py`.

Execute o script de teste de imports:
```bash
python test_imports.py
```

## 🐛 Troubleshooting

### Erro: "python: comando não encontrado"
**Solução:** Use `python3` em vez de `python` (Linux/macOS):
```bash
python3 -m venv venv
```

### Erro: "Solver SCIP não encontrado"
**Solução:** Certifique-se de que o ambiente virtual está ativo e instale o OR-Tools:
```bash
pip install ortools
```

### Erro: "Arquivo não encontrado"
**Solução:** 
1. Verifique os caminhos em `config.py`
2. Configure via variáveis de ambiente
3. Certifique-se de que os arquivos JSON existem

### Erro: "Modelo infactível"
**Solução:** Isso pode acontecer se:
- Há conflitos de horário insuperáveis
- Os créditos mínimos não podem ser alcançados
- Há pré-requisitos impossíveis de satisfazer

Tente ajustar as disciplinas concluídas ou os parâmetros de configuração.

### Erro de política de execução no PowerShell (Windows)
**Solução:** Execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problemas com ambiente virtual
**Solução:** 
1. Certifique-se de estar no diretório raiz do projeto
2. Delete o diretório `venv` e recrie:
   ```bash
   rm -rf venv  # Linux/macOS
   Remove-Item -Recurse -Force venv  # Windows PowerShell
   python -m venv venv
   ```

## 📚 Documentação Adicional

### Guias de Instalação
- [Guia Rápido](QUICKSTART.md) - Início rápido em 3 passos
- [Guia de Instalação Detalhado](INSTALACAO.md) - Instruções passo a passo completas

### Documentação Técnica
- [Análise e Melhorias](ANALISE_E_MELHORIAS.md) - Análise detalhada do código
- [Guia de Migração](MIGRACAO.md) - Guia de migração da versão anterior
- [Resumo da Refatoração](RESUMO_REFATORACAO.md) - Detalhes da refatoração completa
- [Correções Aplicadas](CORRECOES_APLICADAS.md) - Lista de correções realizadas

## 💡 Dicas

- **Sempre ative o ambiente virtual** antes de executar a aplicação
- **Mantenha o ambiente virtual atualizado** executando `pip install --upgrade -r requirements.txt` periodicamente
- **Use o script de teste** (`test_imports.py`) para verificar se tudo está funcionando
- **Consulte os logs** em `app.log` para debug de problemas

## 👤 Autor

**Hugo Antunes**

Desenvolvido como parte do projeto de Otimização - Engenharia de Computação (UFRJ) - 2025.2

## 📄 Licença

Este projeto está sob a licença MIT.
