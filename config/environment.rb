# Pre-process DATABASE_URL: encode special chars in the password component
# (e.g. '?', '#') before Ruby's URI parser reads it. Rails automatically
# picks up DATABASE_URL at initialization, and URI::parse chokes on '?'.
if (db_url = ENV["DATABASE_URL"])
  ENV["DATABASE_URL"] = db_url.sub(%r{^((?:postgresql|postgres)://[^:@]+:)([^@]+)(@)}) do
    "#{$1}#{$2.gsub("?", "%3F").gsub("#", "%23")}#{$3}"
  end
end

# Load the Rails application.
require_relative "application"

# Initialize the Rails application.
Rails.application.initialize!
