# Seed 10 demo content outputs for sales validation
# Uses existing clients and content requests

# --- Moto Wind (Pedro Silva - Botucatu) ---
mw_client = Client.find_by!(business_name: "Moto Wind")
mw_cr = ContentRequest.find_by!(client: mw_client)

# 1. Content Plan
ContentOutput.find_or_create_by!(content_request: mw_cr, title: "Plano de Conteudo 7 Dias - Moto Wind") do |o|
  o.output_type = "content_plan"
  o.status = "approved"
  o.content = <<~CONTENT
    CALENDARIO EDITORIAL — MOTO WIND (7 DIAS)

    Dia 1 (Segunda) — REELS
    Tema: "3 barulhos que sua moto faz quando precisa de revisao"
    Formato: Video 35s, dono falando na oficina
    Objetivo: Educar + gerar identificacao

    Dia 2 (Terca) — CARROSSEL
    Tema: "Antes e depois: restauracao de tanque"
    Formato: 5 fotos do processo
    Objetivo: Mostrar qualidade do trabalho

    Dia 3 (Quarta) — REELS
    Tema: "Um dia na Moto Wind" (bastidores)
    Formato: Video 30s, rotina da oficina
    Objetivo: Humanizar a marca

    Dia 4 (Quinta) — POST IMAGEM
    Tema: Depoimento de cliente satisfeito
    Formato: Foto do cliente + moto + texto
    Objetivo: Prova social

    Dia 5 (Sexta) — REELS
    Tema: "Troca de oleo em 5 minutos — como fazemos"
    Formato: Video acelerado 25s
    Objetivo: Demonstrar agilidade

    Dia 6 (Sabado) — STORIES
    Tema: Promocao de final de semana
    Formato: 3 stories com CTA
    Objetivo: Conversao direta

    Dia 7 (Domingo) — POST IMAGEM
    Tema: Dica rapida de manutencao para o motociclista
    Formato: Imagem com texto sobreposto
    Objetivo: Valor + alcance organico
  CONTENT
end
puts "1/10 - Plano de conteudo Moto Wind"

# 2. Video Script - Moto Wind
ContentOutput.find_or_create_by!(content_request: mw_cr, title: "Roteiro: 3 Barulhos que Sua Moto Faz") do |o|
  o.output_type = "video_script"
  o.status = "approved"
  o.content = <<~CONTENT
    GANCHO (3s):
    Sua moto ta fazendo um barulho diferente? Para e escuta.

    CONTEXTO (7s):
    Tem 3 barulhos que todo motociclista ignora — e que podem custar caro depois.

    DEMONSTRACAO (15s):
    Barulho 1: estalo na corrente — pode ser folga ou desgaste.
    Barulho 2: chiado no freio — pastilha no limite.
    Barulho 3: batida no motor — pode ser biela. Esse e urgente.

    PROVA (5s):
    Aqui na Moto Wind a gente diagnostica de graca. Sem surpresa.

    CTA (5s):
    Manda audio do barulho no nosso WhatsApp. A gente te fala o que e. Link na bio.
  CONTENT
end
puts "2/10 - Roteiro barulhos Moto Wind"

# 3. Video Script - Moto Wind
ContentOutput.find_or_create_by!(content_request: mw_cr, title: "Roteiro: Troca de Oleo em 5 Minutos") do |o|
  o.output_type = "video_script"
  o.status = "approved"
  o.content = <<~CONTENT
    GANCHO (3s):
    Troca de oleo em 5 minutos. Bora ver?

    CONTEXTO (7s):
    Muita gente adia a troca de oleo. Mas demora menos do que voce imagina.

    DEMONSTRACAO (15s):
    [Video acelerado mostrando o processo]
    Passo 1: drenar o oleo velho.
    Passo 2: trocar o filtro.
    Passo 3: colocar oleo novo.
    Pronto. Motor protegido por mais 3.000 km.

    PROVA (5s):
    Fizemos 12 trocas so hoje. Sua moto pode ser a proxima.

    CTA (5s):
    Agenda pelo WhatsApp. Sem fila, sem espera. Link na bio.
  CONTENT
end
puts "3/10 - Roteiro oleo Moto Wind"

# 4. Social Post - Moto Wind
ContentOutput.find_or_create_by!(content_request: mw_cr, title: "Post: Depoimento Cliente Moto Wind") do |o|
  o.output_type = "social_post"
  o.status = "approved"
  o.content = <<~CONTENT
    Quando o cliente sai sorrindo, a gente sabe que fez certo.

    O Marcos trouxe a CG dele com problema na partida.
    Diagnostico: vela e bobina precisando trocar.
    Resolvido no mesmo dia.

    "Achei que ia gastar uma fortuna, mas foi rapido e justo."
    — Marcos, cliente Moto Wind

    Se sua moto ta com problema, manda mensagem.
    A gente resolve sem enrolacao.

    #motocenterwind #oficinademoto #botucatu #mecanicademoto
    #manutencaomotos #motociclismo #revisaomoto
  CONTENT
end
puts "4/10 - Post depoimento Moto Wind"

# 5. Social Post - Moto Wind
ContentOutput.find_or_create_by!(content_request: mw_cr, title: "Post: Dica de Manutencao Preventiva") do |o|
  o.output_type = "social_post"
  o.status = "approved"
  o.content = <<~CONTENT
    3 coisas que voce pode checar na sua moto agora mesmo:

    1. Pressao dos pneus — pneu murcho gasta mais e freia pior
    2. Nivel do oleo — puxa a vareta e veja se ta entre as marcas
    3. Luzes — pisca, farol, lanterna. Demora 10 segundos

    Se alguma coisa tiver estranha, traz pra gente dar uma olhada.
    Diagnostico e sempre gratis aqui na Moto Wind.

    Salva esse post pra lembrar no fim de semana.

    #dicademoto #manutencaopreventiva #motocenterwind #botucatu
    #oficinademoto #motociclista #segurancaemduasrodas
  CONTENT
end
puts "5/10 - Post dica manutencao Moto Wind"

# --- Moto Center Silva (Carlos - Campinas) ---
mcs_client = Client.find_by!(business_name: "Moto Center Silva")
mcs_cr = ContentRequest.find_by!(client: mcs_client)

# 6. Content Plan
ContentOutput.find_or_create_by!(content_request: mcs_cr, title: "Plano de Conteudo 7 Dias - Moto Center Silva") do |o|
  o.output_type = "content_plan"
  o.status = "approved"
  o.content = <<~CONTENT
    CALENDARIO EDITORIAL — MOTO CENTER SILVA (7 DIAS)

    Dia 1 (Segunda) — REELS
    Tema: "5 sinais que sua moto precisa de revisao"
    Formato: Video 35s com mecanico explicando
    Objetivo: Educar e atrair

    Dia 2 (Terca) — POST IMAGEM
    Tema: Antes e depois de customizacao
    Formato: Foto comparativa
    Objetivo: Mostrar trabalho

    Dia 3 (Quarta) — REELS
    Tema: "Bastidores da oficina"
    Formato: Video 30s do dia a dia
    Objetivo: Conexao

    Dia 4 (Quinta) — CARROSSEL
    Tema: "4 erros que encurtam a vida da sua moto"
    Formato: 5 slides educativos
    Objetivo: Autoridade

    Dia 5 (Sexta) — REELS
    Tema: "Customizacao completa em 60 segundos"
    Formato: Timelapse
    Objetivo: Impacto visual

    Dia 6 (Sabado) — STORIES
    Tema: Horario especial de sabado
    Formato: 3 stories com link
    Objetivo: Conversao

    Dia 7 (Domingo) — POST IMAGEM
    Tema: Frase motivacional de motociclista
    Formato: Imagem com frase
    Objetivo: Engajamento
  CONTENT
end
puts "6/10 - Plano de conteudo Moto Center Silva"

# 7. Video Script - Moto Center Silva
ContentOutput.find_or_create_by!(content_request: mcs_cr, title: "Roteiro: Customizacao Completa em 60 Segundos") do |o|
  o.output_type = "video_script"
  o.status = "approved"
  o.content = <<~CONTENT
    GANCHO (3s):
    De moto cansada pra moto dos sonhos em 60 segundos.

    CONTEXTO (7s):
    O dono dessa Titan queria algo unico. Trouxe pra gente e olha o resultado.

    DEMONSTRACAO (15s):
    [Timelapse acelerado da customizacao]
    Pintura nova. Banco revestido. Guidao esportivo.
    Escapamento cromado. Retrovisores novos.
    Cada detalhe pensado com o cliente.

    PROVA (5s):
    Ja fizemos mais de 200 customizacoes aqui no Moto Center Silva.

    CTA (5s):
    Quer transformar a sua? Manda foto da moto no WhatsApp. Link na bio.
  CONTENT
end
puts "7/10 - Roteiro customizacao Moto Center Silva"

# 8. Video Script - Moto Center Silva
ContentOutput.find_or_create_by!(content_request: mcs_cr, title: "Roteiro: 4 Erros que Encurtam a Vida da Moto") do |o|
  o.output_type = "video_script"
  o.status = "approved"
  o.content = <<~CONTENT
    GANCHO (3s):
    Voce ta fazendo isso com sua moto? Para agora.

    CONTEXTO (7s):
    4 erros que a maioria dos motociclistas comete sem saber.

    DEMONSTRACAO (15s):
    Erro 1: acelerar com motor frio. Da 30 segundos pro oleo circular.
    Erro 2: ignorar a corrente. Lubrifica a cada 500 km.
    Erro 3: freio so na roda de tras. Use os dois, sempre.
    Erro 4: pular a revisao. Seu bolso agradece depois.

    PROVA (5s):
    90% dos problemas graves que a gente ve aqui comecaram com esses erros.

    CTA (5s):
    Salva esse video e manda pro amigo motociclista. Sua moto agradece.
  CONTENT
end
puts "8/10 - Roteiro erros Moto Center Silva"

# 9. Social Post - Moto Center Silva
ContentOutput.find_or_create_by!(content_request: mcs_cr, title: "Post: Bastidores da Oficina") do |o|
  o.output_type = "social_post"
  o.status = "approved"
  o.content = <<~CONTENT
    Segunda-feira, 7h da manha.
    Cafe feito. Ferramentas organizadas. Primeira moto do dia ja na rampa.

    Isso aqui nao e so uma oficina.
    E onde cada moto recebe atencao de verdade.

    Desde 2015 cuidando das motos de Campinas e regiao.
    Se voce ainda nao conhece, ta na hora.

    Passa aqui ou manda mensagem.
    A porta ta sempre aberta.

    #motocentersilva #oficinacampinas #mecanicademoto
    #bastidores #rotina #campinas #motociclismo
  CONTENT
end
puts "9/10 - Post bastidores Moto Center Silva"

# 10. Social Post - Moto Center Silva
ContentOutput.find_or_create_by!(content_request: mcs_cr, title: "Post: Promocao Revisao Completa") do |o|
  o.output_type = "social_post"
  o.status = "approved"
  o.content = <<~CONTENT
    Sua moto merece uma revisao antes do frio chegar.

    Neste mes, revisao completa com:
    - Troca de oleo
    - Verificacao de freios
    - Regulagem de corrente
    - Checagem eletrica

    Tudo isso com preco justo e sem surpresa.
    Orcamento na hora, sem compromisso.

    Manda um "REVISAO" no WhatsApp e agenda a sua.
    Link na bio.

    #revisaomoto #oficinacampinas #motocentersilva
    #manutencaomoto #promocao #campinassp
  CONTENT
end
puts "10/10 - Post promocao Moto Center Silva"

puts
puts "=== RESUMO ==="
puts "Total content outputs: #{ContentOutput.count}"
puts "  - video_script: #{ContentOutput.where(output_type: 'video_script').count}"
puts "  - social_post: #{ContentOutput.where(output_type: 'social_post').count}"
puts "  - content_plan: #{ContentOutput.where(output_type: 'content_plan').count}"
