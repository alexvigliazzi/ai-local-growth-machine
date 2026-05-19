# Runbook Operacional

## 1. Onboarding de Novo Cliente

### Pre-requisitos
- Pagamento confirmado (manual)
- Plano definido: Starter (R$497) ou Pro (R$997)

### Passos

1. **Criar cliente no sistema**
   - Admin dashboard → Clients → New
   - Preencher: business_name, niche, city, contact_name, whatsapp, email, plan

2. **Enviar link de briefing**
   ```
   https://[dominio]/briefing?client_id=[UUID]
   ```
   Ou compartilhar via WhatsApp: "Preenche esse formulario rapido que ja comeco a trabalhar no seu conteudo."

3. **Aguardar briefing preenchido**
   - Sistema cria ContentRequest automaticamente
   - Status: pending

4. **Disparar geracao de conteudo**
   - Automatico: Solid Queue enfileira LanggraphJob apos briefing
   - Manual (se necessario):
     ```powershell
     cd C:\Dev\apps\ai-local-growth-machine
     python automations/graphs/content_generation.py --request_id [UUID]
     ```

5. **Revisar conteudo gerado**
   - Admin dashboard → Content Outputs → filtrar por cliente
   - Verificar qualidade, tom de voz, adequacao ao nicho
   - Editar se necessario (inline edit via Turbo Frames)
   - Aprovar items prontos

6. **Gerar relatorio**
   - Admin dashboard → Reports → New → selecionar cliente e periodo
   - Ou via LangGraph:
     ```powershell
     python automations/graphs/weekly_report.py --client_id [UUID]
     ```

7. **Entregar ao cliente**
   - Link publico: `/r/[TOKEN]`
   - Ou exportar PDF e enviar via WhatsApp

---

## 2. Geracao de Conteudo

### Fluxo Normal (Automatico)

```
Briefing preenchido
    → Solid Queue dispara LanggraphJob
    → content_generation.py executa:
        1. Classificacao (Ollama, ~5s)
        2. Draft do plano (Ollama, ~30s)
        3. Refinamento (Claude CLI, ~60s)
        4. Roteiros de video (Claude CLI, ~90s)
        5. Legendas + hashtags (Claude CLI, ~30s)
    → Resultados salvos via Rails API
    → Notificacao no dashboard
```

**Tempo total estimado:** 3-5 minutos por briefing completo

### Fluxo Manual (Contingencia)

Se a automacao falhar:

1. Abrir terminal no diretorio do projeto
2. Executar workflow manualmente:
   ```powershell
   python automations/graphs/content_generation.py --request_id [UUID] --verbose
   ```
3. Se Claude CLI estiver com rate limit, usar flag de fallback:
   ```powershell
   python automations/graphs/content_generation.py --request_id [UUID] --force-ollama
   ```
4. Revisar output no dashboard e salvar manualmente se necessario

### Qualidade do Conteudo

**Checklist de revisao antes de entregar:**
- [ ] Tom de voz condiz com o briefing
- [ ] Conteudo e especifico para o negocio (nao generico)
- [ ] Roteiros tem no maximo 80 palavras (35s de fala)
- [ ] Hashtags incluem cidade e nicho
- [ ] CTA e claro e unico por conteudo
- [ ] Nenhum erro factual obvio
- [ ] Nenhuma promessa exagerada

---

## 3. Prospeccao (Outreach)

### Preparar Lista de Leads

1. **Scraping manual:**
   - Instagram: buscar por hashtag da cidade + nicho (ex: #oficinademotoscampinas)
   - Google Maps: buscar "[nicho] em [cidade]", anotar nome + Instagram
   - Salvar em `data/leads/leads_[nicho]_[cidade].csv`

2. **Formato do CSV:**
   ```csv
   business_name,niche,city,instagram_url,whatsapp,email
   Oficina do Ze,oficina_moto,Campinas,@oficinaze,19999999999,
   ```

3. **Importar no sistema:**
   - Admin dashboard → Leads → Import CSV
   - Ou via Rails console:
     ```ruby
     Lead.import_csv("data/leads/leads_oficina_campinas.csv")
     ```

### Gerar Mensagens

```powershell
python automations/graphs/lead_outreach.py --niche oficina_moto --city Campinas
```

Resultado: mensagens personalizadas salvas em `outreach_messages`

### Enviar (Manual no MVP)

1. Abrir Admin dashboard → Outreach Messages
2. Copiar mensagem do lead
3. Enviar via WhatsApp Web ou email
4. Marcar status: "sent"
5. Registrar resposta quando houver
6. Follow-up em 3 dias se sem resposta

### Meta Semanal
- 50 leads identificados
- 50 mensagens geradas
- 30-50 enviadas
- 5+ respostas
- 1+ qualificado
- 1 venda em 2 semanas

---

## 4. Entrega Semanal (Clientes Pro)

### Toda Segunda-Feira

1. Gerar relatorio da semana anterior:
   ```powershell
   python automations/graphs/weekly_report.py --all-active-clients
   ```

2. Revisar relatorios no dashboard

3. Enviar para cada cliente:
   - Link: `/r/[TOKEN]`
   - Ou PDF via WhatsApp com mensagem:
     ```
     Oi [NOME], segue o relatorio da semana passada.
     [LINK ou PDF]
     Qualquer duvida, me chama.
     ```

4. Registrar envio no sistema (status: "delivered")

---

## 5. Troubleshooting

### LangGraph nao executa
```powershell
# Verificar Python e dependencias
python --version
pip show langgraph langchain-core httpx

# Testar Ollama
curl http://localhost:11434/api/tags

# Testar Claude CLI
claude --version
claude -p "teste" --output-format json

# Testar Gemini CLI
gemini --version
```

### Ollama nao responde
```powershell
# Verificar container Docker
docker ps | Select-String ollama

# Reiniciar se necessario
docker restart context-ia-manager-ollama-1

# Testar
curl http://localhost:11434/api/tags
```

### Claude CLI rate-limited
- Usar `--force-ollama` nos workflows
- Ou aguardar reset do tier (geralmente 1 hora)
- Monitorar uso em: Settings do Claude Pro

### Rails nao inicia
```powershell
# Verificar Postgres
docker ps | Select-String growth_machine_pg

# Reiniciar se necessario
docker start growth_machine_pg

# Verificar conexao
rails db:migrate:status

# Iniciar
rails server
```

---

## 6. Criterios de Escala vs Kill

### Escalar o Nicho Se:
- Taxa de resposta > 10% (5+ respostas em 50 contatos)
- 1+ venda em 2 semanas
- Feedback positivo do cliente piloto
- Ciclo de venda < 7 dias
- Margem > 90% (custo LLM < R$50/mes)

**Proximos passos ao escalar:**
- Criar templates especificos para o nicho
- Automatizar mais etapas do outreach
- Considerar Piloto Pro como padrao
- Testar preco mais alto (R$1.497)

### Matar o Nicho Se:
- < 5% resposta em 100 contatos
- Zero vendas em 3 semanas
- Objecoes irresoluveis (ex: "nao uso redes" recorrente)
- Custo de aquisicao > 30% do ticket

**Ao matar:**
- Registrar aprendizados em `data/niches/[nicho]_postmortem.md`
- Pivotar para proximo nicho da lista (ver ICP.md)
- Nao gastar mais de 1 semana validando cada nicho

### Pivotar Se:
- Respostas positivas mas sem conversao → ajustar oferta/preco
- Conversao ok mas churn > 50% → problema de entrega
- Muito interesse mas ticket baixo → testar pacote mais caro ou add-ons

---

## 7. Stack de Comandos Rapidos

```powershell
# Iniciar tudo
docker start growth_machine_pg
rails server

# Gerar conteudo para um cliente
python automations/graphs/content_generation.py --request_id [UUID]

# Gerar outreach para um nicho
python automations/graphs/lead_outreach.py --niche [NICHO] --city [CIDADE]

# Gerar relatorio semanal
python automations/graphs/weekly_report.py --client_id [UUID]

# Gerar todos os relatorios
python automations/graphs/weekly_report.py --all-active-clients

# Verificar saude do sistema
docker ps
rails db:migrate:status
curl http://localhost:11434/api/tags
claude --version
```
