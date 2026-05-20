ENV["BUNDLE_GEMFILE"] ||= File.expand_path("../Gemfile", __dir__)

require "bundler/setup" # Set up gems listed in the Gemfile.
require "bootsnap/setup" # Speed up boot time by caching expensive operations.

# Encode special characters in the DATABASE_URL password BEFORE anything
# reads it. Rails parses DATABASE_URL during Rake task *definition* (databases.rake),
# which fires before config/environment.rb loads. Ruby's URI parser treats '?'
# as a query-string separator, breaking passwords like 'abc?XYZ'.
# config/boot.rb is the earliest file loaded by every Rails entry-point
# (Rake, Puma, rails server, etc.), so this is the only safe location.
if (db_url = ENV["DATABASE_URL"])
  ENV["DATABASE_URL"] = db_url.sub(%r{^((?:postgresql|postgres)://[^:@]+:)([^@]+)(@)}) do
    "#{$1}#{$2.gsub("?", "%3F").gsub("#", "%23").gsub("@", "%40")}#{$3}"
  end
end
