# 🎓 Otimizador de Grade Horária

Este projeto é uma aplicação web que ajuda estudantes a otimizar sua grade horária, sugerindo um plano de estudos para os próximos semestres com base nas disciplinas já cursadas. Ele utiliza Programação Linear Inteira Mista (MILP) através da biblioteca OR-Tools do Google para encontrar a melhor combinação de disciplinas.

## 📂 Estrutura do Projeto

- **backend/**: Contém o código fonte do servidor e a lógica de otimização.
  - `main.py`: Arquivo principal da API (FastAPI).
  - `optimizerMILP.py`: Lógica do modelo matemático de otimização.
  - `data_loader.py`: Utilitários para carregar os dados das disciplinas.
  - `static/`: Arquivos frontend (HTML/CSS/JS).
- **attempt1/**: Contém os dados (JSON) das disciplinas e ofertas.
- **requirements.txt**: Lista de dependências do projeto.

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para configurar e executar o projeto em sua máquina.

### 1. Pré-requisitos

Certifique-se de ter o **Python 3.8+** instalado em seu sistema.

### 2. Configurar o Ambiente Virtual (venv)

É recomendável usar um ambiente virtual para isolar as dependências do projeto.

**No Windows:**
```powershell
# Abra o terminal na pasta do projeto
python -m venv .venv

# Ative o ambiente virtual
.\.venv\Scripts\activate
```

**No Linux/macOS:**
```bash
# Abra o terminal na pasta do projeto
python3 -m venv .venv

# Ative o ambiente virtual
source .venv/bin/activate
```

### 3. Instalar Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

Caso não tenha o arquivo `requirements.txt`, você pode instalar manualmente:
```bash
pip install fastapi uvicorn ortools pydantic
```

### 4. Executar a Aplicação

Para iniciar o servidor, execute o seguinte comando na raiz do projeto ou dentro da pasta `backend`:

```bash
# Se estiver na raiz do projeto (d:\Arquivos\Desktop\novo)
python backend/main.py
```
Ou usando o uvicorn diretamente (se estiver na pasta `backend`):
```bash
uvicorn main:app --reload
```

O servidor iniciará em `http://127.0.0.1:8000`.

### 5. Usar o Otimizador

1. Abra seu navegador e acesse [http://127.0.0.1:8000](http://127.0.0.1:8000).
2. Na interface, selecione as disciplinas que você **já cursou**.
3. Clique em "Gerar Grade Otimizada".
4. O sistema calculará e exibirá o plano sugerido para os próximos semestres.

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, FastAPI
- **Otimização**: Google OR-Tools (MILP)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 📝 Notas

- O arquivo `main.py` está configurado para rodar no host `127.0.0.1` para garantir compatibilidade no Windows.
- Certifique-se de que os arquivos de dados (`disciplinas.json` e `ofertas.json`) estejam na pasta `attempt1` conforme esperado pelo sistema.
