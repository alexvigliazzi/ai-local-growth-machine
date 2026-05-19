# Admin user
admin = User.find_or_create_by!(email_address: "admin@growthm.local") do |u|
  u.password = "admin123"
  u.password_confirmation = "admin123"
end
puts "Admin: admin@growthm.local / admin123"

# Demo leads
[
  { business_name: "Moto Center Silva", niche: "oficina_moto", city: "Campinas - SP", whatsapp: "(19) 99999-1111", instagram_url: "@motocentersilva" },
  { business_name: "Studio Bella", niche: "estetica_beleza", city: "Campinas - SP", whatsapp: "(19) 99999-2222", instagram_url: "@studiobella" },
  { business_name: "Dr. Marcos Odonto", niche: "odontologia", city: "Valinhos - SP", whatsapp: "(19) 99999-3333", instagram_url: "@drmarcos.odonto" },
  { business_name: "Oficina do Beto", niche: "oficina_moto", city: "Sumare - SP", whatsapp: "(19) 99999-4444" },
  { business_name: "Estetica Renova", niche: "estetica_beleza", city: "Indaiatuba - SP", whatsapp: "(19) 99999-5555" },
].each do |attrs|
  Lead.find_or_create_by!(business_name: attrs[:business_name]) do |l|
    l.assign_attributes(attrs.merge(source: "seed"))
  end
end
puts "5 demo leads created"

# Demo client with content request
client = Client.find_or_create_by!(business_name: "Moto Center Silva") do |c|
  c.niche = "oficina_moto"
  c.city = "Campinas - SP"
  c.contact_name = "Carlos Silva"
  c.whatsapp = "(19) 99999-1111"
  c.email = "carlos@motocenter.com"
  c.plan = "starter"
end

cr = ContentRequest.find_or_create_by!(client: client) do |r|
  r.objective = "Atrair mais clientes para a oficina, mostrar os servicos de customizacao"
  r.tone = "descontraido"
  r.services = "Manutencao preventiva, customizacao, troca de oleo, funilaria"
end

ContentOutput.find_or_create_by!(content_request: cr, title: "Roteiro: 5 Sinais que sua Moto Precisa de Revisao") do |o|
  o.output_type = "video_script"
  o.content = <<~CONTENT
    GANCHO (3s): Sua moto ta fazendo um barulho estranho?

    CONTEXTO (7s): Muita gente ignora sinais simples que podem virar um problema caro.

    DEMONSTRACAO (15s): Aqui na Moto Center Silva a gente ve isso todo dia.
    Sinal 1: barulho no motor. Sinal 2: freio mole. Sinal 3: oleo escuro.
    Sinal 4: partida dificil. Sinal 5: consumo alto de combustivel.

    PROVA (5s): Semana passada um cliente trouxe a moto com 3 desses sinais.
    Resolvemos tudo em 2 horas.

    CTA (5s): Manda um oi no WhatsApp e agenda sua revisao. Link na bio.
  CONTENT
  o.status = "approved"
end

puts "Demo client + content created"
