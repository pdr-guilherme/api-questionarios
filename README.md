# Questionários

> API de um sistema de questionários, com funcionalidades de cadastro de usuários (adminstradores e respondentes), criação e edição de questionários e das perguntas que os compõem

[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Sumário

- [Sobre](#sobre)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como rodar](#como-rodar)
- [Testes](#testes)
- [Documentação da API](#documentação-da-api)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Licença](#licença)

---

## Sobre

API para um sistema de questionários, feito como avaliação da minha capacidade de modelagem, organização e tomada de decisão técnica com Django REST Framework.

### Funcionalidades do Projeto

- Cadastro e gerenciamento de usuários administradores;
- Cadastro e gerenciamento de usuários respondentes pelos adminstradores;
- Cadastro e edição de questionários;
- Cadastro e edição de perguntas a um questionário;
- Cadastro e edição de imagens em uma pergunta;
- Cadastro e edição de opções de resposta em uma pergunta;
- Controle de acesso a questionários;
- Acompanhamento de progresso das respostas;

---

## Requisitos

- Python 3.12+
- pip / virtualenv

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/pdr-guilherme/api-questionarios.git
cd api-questionarios/

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute as migrações
python manage.py migrate
```

---

## Como rodar

```bash
# Servidor de desenvolvimento
python manage.py runserver
```

---

## Testes

```bash
# Rodar todos os testes
pytest

# Rodar testes de um app específico
pytest apps/surveys/
```

---

## Documentação da API

Com o servidor rodando, acesse:

- **Swagger UI**: http://localhost:8000/api/schema/docs/
- **Redoc**: http://localhost:8000/api/schema/redoc/

---

## Estrutura do projeto

```
./
├── apps/
│   ├── answers    # Respostas dos usuários a questionários
│   ├── core       # Funcionalidades usadas por outros apps (paginação, permissões, etc.)
│   ├── surveys    # Questionários, perguntas, imagens das perguntas e opções
│   └── users      # Gerenciamento de usuários
├── config/        # Configurações do projeto Django
├── manage.py
├── pyproject.toml
└── requirements.txt
```

---

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.
