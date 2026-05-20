# QA Local — Teste MVP (2026-05-19)

## Ambiente
- Rails 8.1.3, Ruby 4.0.4, Puma 8.0.1
- PostgreSQL 16 (Docker, porta 5433)
- Windows 11 + MSYS2

## Resultados

| # | Teste | Status | Notas |
|---|-------|--------|-------|
| 1 | GET / (landing) | ✅ PASS | 200, layout glassmorphism renderiza |
| 2 | GET /briefing | ✅ PASS | 200, formulário multi-step renderiza (11 step refs) |
| 3 | POST /briefing (envio realista) | ✅ PASS | 302 → /briefing/obrigado. Lead + Client + ContentRequest criados |
| 4 | Confirmar Lead/Client/CR no banco | ✅ PASS | Lead: Clinica Dental Star, Client: Clinica Dental Star, CR: pending |
| 5 | GET /session/new | ✅ PASS | 200, formulário de login renderiza |
| 6 | POST /session (login admin) | ✅ PASS | 302 (autenticação bem-sucedida) |
| 7 | GET /admin | ✅ PASS | 200, dashboard com sidebar renderiza |
| 8 | KPIs no dashboard | ✅ PASS | Leads: 9, Clientes: 5, Pendentes: 5, Conteúdos: 11 |
| 9a | GET /admin/leads | ✅ PASS | 200 |
| 9b | GET /admin/clients | ✅ PASS | 200 |
| 9c | GET /admin/content_requests | ✅ PASS | 200 |
| 9d | GET /admin/content_outputs | ✅ PASS | 200 |
| 9e | GET /admin/outreach_messages | ✅ PASS | 200 |
| 9f | GET /admin/reports | ✅ PASS | 200 |
| 9g | Show pages (lead, client, CR, CO) | ✅ PASS | 200 em todas |
| 9h | Edit pages (lead, CO) | ✅ PASS | 200 em ambas |
| 9i | GET /r/:token (relatório público) | ✅ PASS | 200, página branded renderiza |
| 9j | GET /briefing/obrigado | ✅ PASS | 200 |

## Bugs Encontrados

### BUG-001: Senha admin desconhecida (não-bloqueante)
- **Severidade:** Baixa
- **Descrição:** Seed data não definiu senha documentada. Admin user `admin@growthm.local` existia mas senha era desconhecida.
- **Fix:** Reset via `rails runner` para `admin123456`. Seed data deve incluir senha padrão documentada.
- **Status:** Corrigido em teste (não persistido no seed)

### Observações (não bugs)
- CSRF em requests via curl é esperado — funciona corretamente em browser real
- Report model não tem coluna `status` — schema correto, não é necessário para MVP
- Outreach messages e reports sem dados de teste (seed não os inclui) — correto para MVP
- Niche values no form: `oficina_moto`, `estetica_beleza`, `odontologia`, `outro` — OK

## Conclusão
**MVP APROVADO para deploy.** Todos os 12 fluxos passaram. Zero bugs bloqueantes.
