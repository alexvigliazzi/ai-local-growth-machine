class EnableRlsForSupabasePublicTables < ActiveRecord::Migration[8.1]
  TABLES = %w[
    ar_internal_metadata
    clients
    content_outputs
    content_requests
    leads
    outreach_messages
    reports
    schema_migrations
    sessions
    users
  ].freeze

  def up
    TABLES.each do |table|
      execute %(ALTER TABLE public.#{table} ENABLE ROW LEVEL SECURITY)
    end
  end

  def down
    TABLES.reverse_each do |table|
      execute %(ALTER TABLE public.#{table} DISABLE ROW LEVEL SECURITY)
    end
  end
end
