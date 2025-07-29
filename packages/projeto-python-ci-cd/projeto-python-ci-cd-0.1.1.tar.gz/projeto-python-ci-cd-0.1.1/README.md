# 🐍 Projeto Python com CI/CD usando GitHub Actions

Este projeto é um exemplo simples e funcional de como configurar um pipeline de **Integração Contínua (CI)** com **GitHub Actions**, utilizando testes automatizados com `pytest` e verificação de qualidade de código com `flake8`.

Ele também está preparado para **Publicação no PyPI** via GitHub Actions (CD - Continuous Deployment) a partir de uma tag.

---

## 🎯 Objetivo

Demonstrar como configurar um fluxo de CI/CD para projetos Python, com:

- Execução de testes unitários automaticamente (`pytest`)
- Verificação de qualidade do código com `flake8`
- Publicação automática no PyPI quando uma nova tag for criada
- Versionamento com `bump2version`

---

## 📁 Estrutura do Projeto

projeto-python-ci-cd/
├── src/
│ └── calc.py # Função simples de exemplo
├── tests/
│ └── test_calc.py # Testes automatizados com pytest
├── .github/
│ └── workflows/
│ └── python-ci.yml # Arquivo de workflow CI/CD
├── requirements.txt # Dependências do projeto
├── setup.py # Configuração para empacotamento e publicação
├── LICENSE # Licença do projeto
├── .gitignore # Arquivos e pastas ignoradas pelo Git
└── README.md # Este arquivo

## ⚙️ Tecnologias Utilizadas

- Python 3.10+
- Git & GitHub
- GitHub Actions
- Pytest
- Flake8
- bump2version
- Twine
- setuptools / wheel

---

## 🚀 Como executar localmente

### 1. Clone o rep

git clone https://github.com/seu-usuario/projeto-python-ci-cd.git

### 2. Crie uma Venv para facilitar:

python -m venv venv
source venv/bin/activate  
venv\Scripts\activate     

### 3. Instale as dependências:

pip install -r requirements.txt


# 🧪 Pipeline CI/CD
Este projeto possui um pipeline automatizado que:

Valida a qualidade do código com flake8

Roda os testes com pytest

Cria pacotes .tar.gz e .whl para distribuição

Verifica o pacote com twine

Publica automaticamente no PyPI ao criar uma nova tag v* no GitHub

# 📦 Publicação PyPI
Você pode publicar uma nova versão com:

bump2version patch  # ou minor / major
git push --follow-tags

A tag acionará o GitHub Actions para gerar o pacote e enviá-lo ao PyPI.

# 📄 Licença
Este projeto está licenciado sob os termos da licença MIT. Veja o arquivo LICENSE para mais detalhes.