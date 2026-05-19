# Agentes do Produto

Estes sao os agentes LLM usados pelo produto para atender clientes. Sao diferentes dos agentes do development-system (que orquestram o desenvolvimento).

## Arquitetura

Cada agente e implementado como um **node do LangGraph** em `automations/graphs/`. O LLM Router decide qual backend usar (Ollama, Claude, Gemini, Codex) baseado no profile da tarefa.

```
LangGraph Workflow
    |
    +-- agent_researcher (node)     → Gemini CLI (web-research)
    +-- agent_content_planner (node) → Ollama draft + Claude refine
    +-- agent_copywriter (node)      → Claude haiku (balanced)
    +-- agent_video_script (node)    → Claude sonnet (strong)
    +-- agent_reporter (node)        → Claude haiku (balanced)
```

## Agentes

### 1. agent_researcher

**Proposito:** Pesquisar nichos locais e identificar oportunidades de conteudo.

**Arquivo:** `automations/agents/agent_researcher.md`

**Input:** nicho, cidade, perfil do negocio
**Output:** dores, oportunidades, angulos de conteudo, concorrentes, posicionamento

**LLM Router Profile:** `web-research` → Gemini CLI (acesso a informacoes atuais)
**Fallback:** Claude sonnet via CLI

---

### 2. agent_copywriter

**Proposito:** Criar mensagens comerciais curtas e naturais.

**Arquivo:** `automations/agents/agent_copywriter.md`

**Input:** perfil do negocio, objetivo da mensagem, canal (WhatsApp/email/Instagram)
**Output:** mensagem pronta para envio

**LLM Router Profile:** `balanced` → Claude haiku via CLI
**Fallback:** Ollama llama3.1:8b

---

### 3. agent_content_planner

**Proposito:** Criar calendario editorial de 7 ou 14 dias.

**Arquivo:** `automations/agents/agent_content_planner.md`

**Input:** briefing completo (nicho, tom, servicos, publico, referencias)
**Output:** calendario com objetivo, formato, gancho, roteiro resumido e CTA por dia

**LLM Router Profile:** `fast` (draft) → Ollama llama3.1:8b, depois `strong` (refine) → Claude sonnet
**Fallback:** Claude haiku para ambos

---

### 4. agent_video_script

**Proposito:** Criar roteiros de video curto (ate 35 segundos).

**Arquivo:** `automations/agents/agent_video_script.md`

**Input:** tema, nicho, tom de voz, objetivo do video
**Output:** roteiro estruturado (gancho, contexto, demonstracao, prova, CTA)

**LLM Router Profile:** `strong` → Claude sonnet via CLI (criatividade + portugues natural)
**Fallback:** Ollama llama3.1:8b

---

### 5. agent_reporter

**Proposito:** Transformar entregas em relatorio executivo para o cliente.

**Arquivo:** `automations/agents/agent_reporter.md`

**Input:** lista de content_outputs do periodo, metricas
**Output:** relatorio formatado com: o que foi feito, por que, proximos passos, recomendacao

**LLM Router Profile:** `balanced` → Claude haiku via CLI
**Fallback:** Ollama llama3.1:8b

---

## Como os Agentes se Conectam

### No workflow content_generation.py:
1. `agent_researcher` pesquisa o nicho (se primeiro briefing)
2. `agent_content_planner` cria o calendario
3. `agent_video_script` cria os roteiros
4. `agent_reporter` compila o relatorio final

### No workflow lead_outreach.py:
1. `agent_researcher` avalia o perfil do lead
2. `agent_copywriter` gera a mensagem de abordagem

### No workflow weekly_report.py:
1. `agent_reporter` gera o relatorio semanal
