# Prompt para Claude Design — Frontend da Growth Machine

Cole este prompt inteiro no Claude Design junto com o template selecionado.

---

## PROMPT INICIO

Preciso que voce redesenhe o frontend completo de um MVP chamado **Growth Machine** — uma agencia automatizada de conteudo local com IA para negocios brasileiros. Use o template que selecionei como base visual, adaptando-o para as paginas e fluxos descritos abaixo.

---

### 1. CONTEXTO DO NEGOCIO

**O que e:** SaaS/servico que vende pilotos de conteudo (R$497 starter / R$997 pro) para negocios locais brasileiros. O cliente preenche um briefing, recebe em 7 dias um pacote com roteiros de video, posts para Instagram e calendario editorial.

**Nichos-alvo:**
- Oficinas e lojas de moto (prioridade 1)
- Estetica e beleza
- Odontologia

**Publico:** Donos de negocios locais, 25-50 anos, pouco tempo, pouca habilidade digital. Precisam de praticidade. Tomam decisao rapida se a proposta for clara.

**Tom de voz:** Direto, amigavel, sem jargao de marketing. Fala como um amigo que entende do negocio deles.

**Idioma:** Todo o conteudo em portugues brasileiro (sem acentos nos textos por padrao do projeto, mas com linguagem natural).

---

### 2. STACK TECNICO (importante para compatibilidade)

- **Backend:** Rails 8.1 (Ruby) — as views usam `.html.erb` com tags ERB `<%= %>`
- **CSS:** Tailwind CSS (ja integrado via Rails)
- **JS:** Hotwire/Turbo (Rails 8 default) — sem React/Vue
- **Assets:** Propshaft (nao Sprockets)
- **Layout principal:** `app/views/layouts/application.html.erb`
- **Layout admin:** `app/views/layouts/admin.html.erb`
- **Fontes:** usar Google Fonts via CDN (Inter como primaria recomendada)

**Constraint:** O output deve ser HTML + Tailwind classes. Nao use CSS-in-JS, styled-components, ou frameworks JS de componentes. O codigo sera colado diretamente em arquivos `.html.erb`.

---

### 3. PAGINAS NECESSARIAS

#### 3.1 LANDING PAGE (rota: `/`)
**Objetivo:** Converter visitante em lead que preenche o briefing.

**Secoes obrigatorias (nesta ordem):**

1. **Hero** — Headline forte, subheadline, CTA primario ("Quero meu piloto" → `/briefing`), texto de seguranca ("7 dias. Sem compromisso.")
2. **Dor/Problema** — 3 cards: "Sem tempo para postar", "Nao sabe o que postar", "Agencia cara demais"
3. **Solucao/Entregaveis** — O que o piloto inclui: 5 roteiros de video, 3 legendas prontas, calendario de 7 dias, relatorio executivo
4. **Nichos** — 3 cards mostrando os nichos atendidos (Oficinas/Moto, Estetica, Odontologia) com icones
5. **Como funciona** — 3 passos: Preenche briefing (2 min) → Recebe conteudo (7 dias) → Grava e posta
6. **Prova social/Depoimento** — Espaco para 2-3 depoimentos (pode ser placeholder por enquanto)
7. **Precos** — Card Starter R$497 e card Pro R$997, com features listadas e CTA
8. **FAQ** — Accordion com 4-5 perguntas frequentes
9. **CTA Final** — Repetir o call-to-action principal
10. **Footer** — Links basicos, WhatsApp, Instagram

**Paleta de cores sugerida:**
- Primaria: azul escuro (confianca/profissionalismo)
- Accent: amarelo ou verde (urgencia/acao)
- Background: branco/cinza claro
- Texto: cinza escuro

#### 3.2 BRIEFING FORM (rota: `/briefing`)
**Objetivo:** Coletar dados do negocio para gerar o conteudo.

**Campos organizados em steps ou secoes:**

**Secao 1 — Seu negocio:**
- Nome do negocio (text, obrigatorio)
- Cidade (text, obrigatorio)
- Nicho (select: Oficina/Moto, Estetica/Beleza, Odontologia, Outro)

**Secao 2 — Contato:**
- Seu nome (text)
- WhatsApp (text, obrigatorio)
- Email (text)
- Instagram do negocio (text)

**Secao 3 — Sobre o conteudo:**
- Objetivo com conteudo (textarea)
- Principais servicos (textarea)
- Tom de voz (select: Profissional, Descontraido, Tecnico, Amigavel)
- Perfis que admira (textarea, opcional)

**UI:** Formulario limpo, amplo, com progresso visual. Botao "Enviar briefing" no final. Mensagem de seguranca embaixo.

**ERB necessario:**
```erb
<%= form_with url: briefing_path, method: :post do |f| %>
  <!-- campos -->
<% end %>
```

#### 3.3 THANK YOU PAGE (rota: `/briefing/obrigado`)
**Objetivo:** Confirmar recebimento, reforcar expectativa.

Pagina simples com icone de check, titulo "Briefing recebido!", texto "Vamos analisar seu negocio e preparar o conteudo. Voce recebera tudo por WhatsApp em ate 7 dias.", link para voltar ao inicio.

#### 3.4 RELATORIO PUBLICO (rota: `/r/:token`)
**Objetivo:** Cliente acessa o relatorio por link unico (sem login).

Pagina branded com:
- Logo/nome Growth Machine no topo
- Titulo do relatorio
- Nome do negocio + data
- Conteudo formatado (textos, listas)
- Botao de download (futuro)
- Footer com CTA para contratar plano Pro

**ERB necessario:**
```erb
<%= @report.title %>
<%= @report.client.business_name %>
<%= simple_format(@report.content) %>
```

#### 3.5 LOGIN ADMIN (rota: `/session/new`)
Pagina de login simples. Email + senha. Sem cadastro publico.

#### 3.6 ADMIN DASHBOARD (rota: `/admin`)
**Layout:** Sidebar esquerda (dark) com menu + area de conteudo a direita.

**Sidebar links:**
- Dashboard
- Leads
- Clientes
- Pedidos (content_requests)
- Conteudos (content_outputs)
- Outreach
- Relatorios
- Separador
- Site (link externo para `/`)
- Sair

**Dashboard:**
- 4 KPI cards no topo: Leads, Clientes, Pedidos Pendentes, Conteudos Gerados
- Tabela de leads recentes com colunas: Negocio, Nicho, Cidade, Status (badge colorido), Data
- Status badges: new=azul, contacted=amarelo, converted=verde, lost=vermelho

**ERB das variaveis:**
```erb
@leads_count, @clients_count, @pending_requests, @outputs_count, @recent_leads
```

#### 3.7 ADMIN — TABELAS CRUD
Cada recurso (leads, clients, content_requests, content_outputs, outreach_messages, reports) precisa de:
- **Index:** Tabela paginada com colunas relevantes, link para show
- **Show:** Detalhes do registro, dados relacionados
- **Edit** (onde aplicavel): Formulario de edicao

**Convencao de rotas ERB:**
```erb
admin_leads_path, admin_lead_path(lead)
admin_clients_path, admin_client_path(client)
admin_content_requests_path, admin_content_request_path(cr)
admin_content_outputs_path, admin_content_output_path(co)
admin_outreach_messages_path, admin_outreach_message_path(om)
admin_reports_path, admin_report_path(report)
```

---

### 4. DADOS DOS MODELOS (para referenciar nos templates)

**Lead:** business_name, niche, city, email, whatsapp, instagram_url, status, notes, source, created_at

**Client:** business_name, niche, city, contact_name, whatsapp, email, plan (starter/pro), status

**ContentRequest:** client (belongs_to), objective, tone, services, references, status (pending/in_progress/completed)

**ContentOutput:** content_request (belongs_to), output_type (video_script/social_post/content_plan), title, content, status (draft/review/approved)

**OutreachMessage:** lead (belongs_to), channel (whatsapp/email/instagram_dm), message_type, message, status (pending/sent/replied)

**Report:** client (belongs_to), title, content, token (public URL slug), created_at

---

### 5. REQUISITOS DE DESIGN

- **Mobile-first** — a landing e o briefing serao acessados primariamente por celular (WhatsApp → link)
- **Carregamento rapido** — sem JS pesado, sem imagens grandes, Tailwind puro
- **Acessibilidade basica** — contraste adequado, labels nos inputs, botoes com tamanho minimo de toque
- **Consistencia** — usar o mesmo sistema de cores, tipografia e espacamento em todas as paginas
- **Profissional mas acessivel** — nao parecer startup de tecnologia, parecer servico confiavel para dono de oficina
- **Sem emojis excessivos** — maximo 1 emoji por card/secao quando fizer sentido (icones SVG preferidos)
- **Responsivo** — desktop e mobile, sidebar admin colapsa em mobile

---

### 6. ENTREGAVEIS ESPERADOS

Para cada pagina, entregue o HTML completo com classes Tailwind, pronto para colar nos arquivos `.html.erb` do Rails. Indique claramente:

1. `app/views/layouts/application.html.erb` — layout publico
2. `app/views/layouts/admin.html.erb` — layout admin com sidebar
3. `app/views/pages/landing.html.erb` — landing page
4. `app/views/briefings/new.html.erb` — formulario de briefing
5. `app/views/briefings/thank_you.html.erb` — pagina de confirmacao
6. `app/views/public_reports/show.html.erb` — relatorio publico
7. `app/views/sessions/new.html.erb` — login admin
8. `app/views/admin/dashboard/index.html.erb` — dashboard
9. `app/views/admin/leads/index.html.erb` — lista de leads
10. `app/views/admin/leads/show.html.erb` — detalhe do lead
11. `app/views/admin/leads/edit.html.erb` — editar lead
12. `app/views/admin/clients/index.html.erb` — lista de clientes
13. `app/views/admin/clients/show.html.erb` — detalhe do cliente
14. `app/views/admin/content_requests/index.html.erb` — lista de pedidos
15. `app/views/admin/content_requests/show.html.erb` — detalhe do pedido
16. `app/views/admin/content_outputs/index.html.erb` — lista de conteudos
17. `app/views/admin/content_outputs/show.html.erb` — detalhe do conteudo
18. `app/views/admin/content_outputs/edit.html.erb` — editar conteudo
19. `app/views/admin/outreach_messages/index.html.erb` — lista de mensagens
20. `app/views/admin/outreach_messages/show.html.erb` — detalhe da mensagem
21. `app/views/admin/reports/index.html.erb` — lista de relatorios
22. `app/views/admin/reports/show.html.erb` — detalhe do relatorio

Mantenha as tags ERB (`<%= %>`) nos lugares certos — nao substitua por texto fixo.

---

### 7. EXEMPLO DE CONTEUDO REAL (para preencher os templates)

**Lead exemplo:** Moto Wind, oficina_moto, Botucatu - SP, Pedro Silva, (14) 99888-7766

**Cliente exemplo:** Moto Center Silva, oficina_moto, Campinas - SP, Carlos, plano starter

**Content Output exemplo:**
- Tipo: video_script
- Titulo: "Roteiro: 3 Barulhos que Sua Moto Faz"
- Status: approved

**Piloto Starter R$497 inclui:**
- 5 roteiros de video curto (ate 35s)
- 3 legendas prontas com hashtags
- Calendario editorial de 7 dias
- Relatorio executivo com diagnostico

**Piloto Pro R$997 inclui tudo do Starter +:**
- 10 roteiros de video
- 5 mensagens de prospeccao
- Calendario completo com horarios
- 2 relatorios semanais
- Sessao de 30 min para alinhamento

---

Adapte o template selecionado para este sistema. Priorize a landing page e o briefing (sao as paginas que o cliente ve). O admin pode ser mais funcional e menos estetico.

## PROMPT FIM
