# 📁 Localização dos Arquivos JSON de Dados

## 📍 Onde Estão os Arquivos JSON

Os arquivos JSON com os dados das disciplinas estão localizados em:

```
otm/
├── attempt1/
│   ├── disciplinas.json    (28KB - 159 disciplinas)
│   └── ofertas.json        (16KB - ofertas de turmas)
├── app.py
├── config.py
└── ...
```

### Caminhos Configurados

**Configuração padrão em `config.py`:**
```python
DISCIPLINAS_PATH: Path = BASE_DIR / "attempt1" / "disciplinas.json"
OFERTAS_PATH: Path = BASE_DIR / "attempt1" / "ofertas.json"
```

Onde `BASE_DIR` é o diretório raiz do projeto, ou seja:
- **Windows:** `D:\Arquivos\Desktop\otm\attempt1\disciplinas.json`
- **WSL:** `/mnt/d/Arquivos/Desktop/otm/attempt1/disciplinas.json`

## 📊 Estrutura dos Arquivos JSON

### `disciplinas.json`
Contém informações completas de todas as disciplinas:
- ID da disciplina
- Nome
- Créditos
- Tipo (Obrigatória, Restrita, Condicionada, Livre)
- Pré-requisitos
- Período sugerido

**Total:** 159 disciplinas

### `ofertas.json`
Contém informações sobre as ofertas de turmas:
- ID da disciplina
- ID da turma
- Horários
- Períodos em que é ofertada

## 🔄 Como São Carregados

### 1. Carregamento Inicial (`app.py`)

```python
def carregar_disciplinas_completas():
    """Carrega TODAS as disciplinas do JSON para a interface."""
    with open(config.DISCIPLINAS_PATH, 'r', encoding='utf-8') as f:
        disciplinas = json.load(f)
    return {d['id']: d for d in disciplinas}
```

**Uso:** Para popular a interface de seleção de disciplinas concluídas.

### 2. Carregamento para Otimização (`services/data_loader.py`)

```python
class DataLoader:
    def carregar_dados(self, disciplinas_concluidas):
        # Carrega disciplinas.json e ofertas.json
        disciplinas_data = self._carregar_json(self.disciplinas_path)
        ofertas_data = self._carregar_json(self.ofertas_path)
        
        # Filtra disciplinas concluídas
        # Processa ofertas
        # Retorna apenas disciplinas COM ofertas disponíveis
```

**Uso:** Para a otimização, retorna apenas disciplinas que têm ofertas.

## 🔍 Diferença Importante

### `carregar_disciplinas_completas()` (app.py)
- **Carrega:** TODAS as 159 disciplinas do JSON
- **Uso:** Interface de seleção
- **Retorna:** Todas as disciplinas, mesmo sem ofertas

### `DataLoader.carregar_dados()` (services/data_loader.py)
- **Carrega:** Disciplinas + Ofertas
- **Filtra:** Apenas disciplinas COM ofertas disponíveis
- **Retorna:** ~60 disciplinas (as que podem ser alocadas)

## ⚙️ Configuração de Caminhos

### Via Arquivo de Configuração

Edite `config.py`:
```python
DISCIPLINAS_PATH: Path = BASE_DIR / "attempt1" / "disciplinas.json"
OFERTAS_PATH: Path = BASE_DIR / "attempt1" / "ofertas.json"
```

### Via Variáveis de Ambiente

**Windows (PowerShell):**
```powershell
$env:DISCIPLINAS_PATH="C:\caminho\completo\disciplinas.json"
$env:OFERTAS_PATH="C:\caminho\completo\ofertas.json"
```

**Linux/macOS/WSL:**
```bash
export DISCIPLINAS_PATH="/caminho/completo/disciplinas.json"
export OFERTAS_PATH="/caminho/completo/ofertas.json"
```

## 📝 Verificação

Para verificar se os arquivos estão sendo encontrados:

```python
from config import config
print("Disciplinas:", config.DISCIPLINAS_PATH)
print("Existe:", config.DISCIPLINAS_PATH.exists())
print("Ofertas:", config.OFERTAS_PATH)
print("Existe:", config.OFERTAS_PATH.exists())
```

## ✅ Status Atual

- ✅ Arquivos JSON existem em `attempt1/`
- ✅ Caminhos configurados corretamente
- ✅ Carregamento funcionando (159 disciplinas carregadas)
- ✅ Filtragem funcionando (60 disciplinas com ofertas)

## 📚 Resumo

**Localização dos dados:**
- `attempt1/disciplinas.json` - Todas as disciplinas (159)
- `attempt1/ofertas.json` - Ofertas de turmas

**Como são usados:**
1. Interface: Carrega TODAS as 159 disciplinas para seleção
2. Otimização: Usa apenas as ~60 disciplinas que têm ofertas

**Configuração:**
- Padrão: `config.py` aponta para `attempt1/` (mesmo diretório raiz)
- Customizável: Via variáveis de ambiente

