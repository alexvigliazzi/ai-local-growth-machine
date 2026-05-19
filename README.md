# AI Local Growth Machine

MVP de agencia automatizada de conteudo e prospeccao local usando IA.

Vende pilotos de criacao de conteudo (R$497-R$997) para negocios locais — oficinas, estetica, odontologia.

## Arquitetura

```
Development-System (19 agentes) → orquestra o DESENVOLVIMENTO
    |
Rails 8 App → Landing, Briefing, Admin Dashboard, Reports
    |
LangGraph (Python) → Workflows de automacao (content, outreach, reports)
    |
LLM Router → Ollama (free) | Claude (OAuth) | Gemini (OAuth) | Codex (OAuth)
```

## Stack

- **Backend:** Ruby on Rails 8
- **Database:** PostgreSQL 16 (Docker)
- **Frontend:** Tailwind CSS + Hotwire/Turbo
- **Background Jobs:** Solid Queue (Rails 8 built-in, sem Redis)
- **Auth:** Rails 8 built-in authentication
- **Automacao:** LangGraph 1.2.0 (Python)
- **LLM Router:** Ollama local + Claude/Gemini/Codex via CLI OAuth
- **PDF:** Prawn
- **Orchestration:** Development-system framework

## Estrutura do Projeto

```
ai-local-growth-machine/
├── app/                          # Rails application
│   ├── controllers/
│   │   ├── admin/                # Dashboard e CRUD
│   │   ├── api/                  # Endpoints para LangGraph callback
│   │   ├── pages_controller.rb   # Landing page
│   │   ├── briefings_controller.rb
│   │   └── public_reports_controller.rb
│   ├── models/                   # Lead, Client, ContentRequest, etc.
│   ├── services/                 # Report generator, PDF, etc.
│   ├── jobs/                     # Solid Queue jobs (LangGraph bridge)
│   └── views/
├── automations/
│   ├── graphs/                   # LangGraph workflows (Python)
│   │   ├── llm_router.py
│   │   ├── content_generation.py
│   │   ├── lead_outreach.py
│   │   └── weekly_report.py
│   ├── prompts/                  # LLM prompt templates
│   │   ├── content_plan.md
│   │   ├── video_script.md
│   │   ├── social_post.md
│   │   ├── outreach_message.md
│   │   └── weekly_report.md
│   └── agents/                   # Agent role definitions
│       ├── agent_researcher.md
│       ├── agent_copywriter.md
│       ├── agent_content_planner.md
│       ├── agent_video_script.md
│       └── agent_reporter.md
├── data/
│   ├── leads/                    # CSV imports
│   ├── niches/                   # Niche research data
│   └── content-plans/            # Generated plan exports
├── docs/
│   ├── OFFER.md                  # Pricing e scripts de venda
│   ├── ICP.md                    # Ideal Customer Profile
│   ├── PIPELINE.md               # Pipeline de vendas e automacao
│   ├── AGENTS.md                 # Definicao dos agentes do produto
│   └── RUNBOOK.md                # Manual operacional
├── scripts/                      # Utility scripts (Ruby + Python)
├── config/
├── db/
└── README.md
```

## Setup

### Pre-requisitos

- Ruby 3.3+ (`scoop install ruby` ou `choco install ruby`)
- Docker (para PostgreSQL)
- Python 3.14 (ja instalado)
- Node.js (ja instalado)
- LangGraph (`pip install langgraph`)
- Ollama rodando em localhost:11434

### Instalacao

```powershell
# 1. PostgreSQL via Docker
docker run -d --name growth_machine_pg \
  -e POSTGRES_USER=growth_machine \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=growth_machine_development \
  -p 5433:5432 \
  postgres:16-alpine

# 2. Dependencias Ruby
bundle install

# 3. Database
rails db:create db:migrate db:seed

# 4. Iniciar
rails server
# Visitar http://localhost:3000
```

### Variavel de Ambiente

Criar `.env` baseado em `.env.example`:

```
DATABASE_URL=postgres://growth_machine:password@localhost:5433/growth_machine_development
OLLAMA_URL=http://localhost:11434
INTERNAL_API_TOKEN=seu_token_aqui
```

**Nota:** Claude, Gemini e Codex usam OAuth via CLI — nao precisam de API key.

## LLM Router

| Tarefa | Backend | Custo |
|--------|---------|-------|
| Classificar lead | Ollama gemma3:4b | Gratis |
| Rascunho de conteudo | Ollama llama3.1:8b | Gratis |
| Conteudo final | Claude sonnet via CLI | Tier Pro |
| Roteiro de video | Claude sonnet via CLI | Tier Pro |
| Pesquisa de nicho | Gemini via CLI | Tier Pro |
| Outreach message | Claude haiku via CLI | Tier Pro |
| Relatorio | Claude haiku via CLI | Tier Pro |

**Custo por piloto completo:** ~R$2-5 (maioria no Ollama gratis)

## Comandos Uteis

```powershell
# Gerar conteudo
python automations/graphs/content_generation.py --request_id [UUID]

# Gerar outreach
python automations/graphs/lead_outreach.py --niche oficina_moto --city Campinas

# Gerar relatorio
python automations/graphs/weekly_report.py --client_id [UUID]

# Rails console
rails console

# Rodar testes
rails test
```

## Documentacao

- [OFFER.md](docs/OFFER.md) — Pacotes, precos, scripts de venda
- [ICP.md](docs/ICP.md) — Perfil ideal por nicho
- [PIPELINE.md](docs/PIPELINE.md) — Pipeline de vendas e automacao
- [AGENTS.md](docs/AGENTS.md) — Agentes LLM do produto
- [RUNBOOK.md](docs/RUNBOOK.md) — Manual operacional
