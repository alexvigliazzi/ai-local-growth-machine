# Pipeline de Vendas e Automacao

## Estagios do Pipeline

```
NEW → CONTACTED → QUALIFIED → PROPOSAL_SENT → CONVERTED | LOST
```

### 1. NEW (Lead Identificado)

**Como entra:**
- Scraping manual (Instagram, Google Maps)
- Indicacao
- Lead organico pelo formulario de briefing
- Import CSV em `data/leads/`

**Dados coletados:**
- business_name, niche, city, instagram_url, whatsapp, email

**Automacao:**
- LangGraph `lead_outreach.py` → Ollama classifica perfil (fast/free)
- Score automatico baseado em: presenca digital, tamanho, nicho

---

### 2. CONTACTED (Primeiro Contato Feito)

**Trigger:** Mensagem enviada via WhatsApp ou email

**Automacao:**
- LangGraph `lead_outreach.py` → Claude gera mensagem personalizada (balanced/haiku)
- Mensagem salva em `outreach_messages` com status "sent"
- Follow-up agendado em 3 dias se sem resposta

**Criterio para avancar:** Resposta positiva ou neutra do lead

---

### 3. QUALIFIED (Lead Qualificado)

**Trigger:** Lead respondeu e demonstrou interesse

**Criterios de qualificacao:**
- Tem orcamento (R$497+ nao e problema)
- Tem presenca em rede social (Instagram ativo)
- Precisa de conteudo (confirmado na conversa)
- Decisor acessivel (dono, nao funcionario)

**Automacao:**
- Atualizar status no Rails (admin dashboard)
- Preparar diagnostico rapido do perfil digital

**Criterio para avancar:** Lead pede proposta ou aceita ver exemplo

---

### 4. PROPOSAL_SENT (Proposta Enviada)

**Trigger:** Envio de proposta formal ou exemplo personalizado

**Automacao:**
- LangGraph `content_generation.py` → gera mini-exemplo de plano de conteudo
- Exemplo baseado no nicho e cidade do lead (Ollama draft → Claude refine)
- Proposta enviada como PDF/mensagem com preco e incluso

**Follow-up:**
- Dia 1: "Conseguiu ver?"
- Dia 3: "Alguma duvida?"
- Dia 7: Ultima tentativa ou arquivar

**Criterio para avancar:** Lead aceita e confirma pagamento

---

### 5. CONVERTED (Cliente)

**Trigger:** Pagamento confirmado (manual — sem integracao de pagamento no MVP)

**Automacao:**
- Criar registro em `clients` com plano (pilot/pro)
- Enviar link de briefing (`/briefing?client_id=...`)
- LangGraph `content_generation.py` inicia apos briefing preenchido

**Fluxo pos-conversao:**
1. Cliente preenche briefing
2. Solid Queue enfileira `LanggraphJob.perform_later("content_generation", params)`
3. LangGraph gera conteudo (Ollama draft → Claude final)
4. Resultados salvos via Rails API (`/api/content_outputs`)
5. Admin revisa e aprova
6. Relatorio gerado e enviado ao cliente

---

### 5b. LOST (Nao Converteu)

**Motivos registrados:**
- Sem orcamento
- Sem interesse
- Sem resposta (timeout 14 dias)
- Escolheu concorrente

**Automacao:** Nenhuma. Registro para analise futura.

---

## Mapeamento Pipeline → LangGraph Workflows

| Estagio | Workflow LangGraph | Trigger |
|---------|-------------------|---------|
| NEW | `lead_outreach.py` (classificacao) | Novo lead criado |
| CONTACTED | `lead_outreach.py` (mensagem) | Lead classificado como qualificavel |
| PROPOSAL_SENT | `content_generation.py` (mini-exemplo) | Lead pede exemplo |
| CONVERTED | `content_generation.py` (full) | Briefing preenchido |
| Recorrente | `weekly_report.py` | Cron semanal |

---

## Fluxos de Automacao Detalhados

### Fluxo 1: Entrada do Cliente (Post-Venda)

```
Cliente preenche /briefing
    |
    v
Rails cria Lead + Client + ContentRequest
    |
    v
Solid Queue enfileira LanggraphJob
    |
    v
LangGraph content_generation.py:
    1. Ollama classifica nicho e tom (fast/free)
    2. Ollama gera rascunho de plano (fast/free)
    3. Claude refina plano final (strong/sonnet)
    4. Claude gera roteiros de video (strong/sonnet)
    5. Claude gera legendas + hashtags (balanced/haiku)
    |
    v
LangGraph salva via POST /api/content_outputs
    |
    v
Admin recebe notificacao (email/dashboard)
    |
    v
Admin revisa → aprova → gera relatorio
    |
    v
Cliente recebe pacote via /r/:token ou WhatsApp
```

### Fluxo 2: Prospeccao (Pre-Venda)

```
Lista de 50 leads em data/leads/leads.csv
    |
    v
Import via Rails admin ou script
    |
    v
LangGraph lead_outreach.py:
    1. Ollama avalia cada perfil (fast/free)
    2. Score e classificacao automatica
    3. Claude gera mensagem personalizada (balanced/haiku)
    |
    v
Mensagens salvas em outreach_messages
    |
    v
Envio manual via WhatsApp (MVP)
    |
    v
Registrar status: sent → replied → qualified → proposal_sent
    |
    v
Follow-up automatico em 3 dias (LangGraph)
```

### Fluxo 3: Entrega Semanal (Recorrencia)

```
Cron semanal (ou manual via admin)
    |
    v
LangGraph weekly_report.py:
    1. Busca content_outputs do periodo via Rails API
    2. Claude gera resumo executivo (balanced/haiku)
    3. Compila metricas (conteudos gerados, aprovados, pendentes)
    |
    v
Salva report via POST /api/reports
    |
    v
Gera PDF via Prawn
    |
    v
Link publico /r/:token
    |
    v
Envio ao cliente via WhatsApp/email
```

---

## LLM Router por Estagio

| Estagio | Operacao | Backend | Custo Estimado |
|---------|----------|---------|---------------|
| NEW | Classificar lead | Ollama gemma3:4b | R$0 |
| CONTACTED | Gerar mensagem | Claude haiku via CLI | ~R$0.02/msg |
| PROPOSAL | Mini-exemplo | Ollama draft + Claude refine | ~R$0.15 |
| CONVERTED | Plano completo | Ollama draft + Claude final | ~R$0.50 |
| SEMANAL | Relatorio | Claude haiku via CLI | ~R$0.10 |
| **Total por lead convertido** | | | **~R$0.80** |

**Custo por piloto completo (7 dias):** ~R$2-5 em LLM (maioria no Ollama gratis)
**Margem bruta no Starter R$497:** ~99%

---

## Metricas de Acompanhamento

| Metrica | Meta Inicial | Onde Ver |
|---------|-------------|---------|
| Leads criados/semana | 50 | Admin dashboard |
| Taxa de resposta | > 10% | outreach_messages status |
| Qualificados/semana | 5 | Pipeline filter |
| Propostas enviadas | 3 | Pipeline filter |
| Conversao | 1/semana | clients count |
| Tempo medio de conversao | < 7 dias | created_at diff |
| NPS do piloto | > 8 | Feedback manual |
