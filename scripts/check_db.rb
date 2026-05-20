puts "--- LEADS ---"
Lead.order(created_at: :desc).each do |l|
  puts "#{l.id[0..7]} | #{l.business_name} | #{l.niche} | #{l.city} | #{l.status} | #{l.source} | #{l.created_at}"
end

puts
puts "--- CLIENTS ---"
Client.order(created_at: :desc).each do |c|
  puts "#{c.id[0..7]} | #{c.business_name} | #{c.plan} | #{c.contact_name}"
end

puts
puts "--- CONTENT REQUESTS ---"
ContentRequest.order(created_at: :desc).each do |cr|
  obj = cr.objective.to_s.truncate(60)
  puts "#{cr.id[0..7]} | #{cr.client.business_name} | #{obj} | #{cr.tone} | #{cr.status}"
end

puts
puts "--- CONTENT OUTPUTS ---"
ContentOutput.all.each do |co|
  puts "#{co.id[0..7]} | #{co.title} | #{co.output_type} | #{co.status}"
end
