ENV["BUNDLE_GEMFILE"] ||= File.expand_path("../Gemfile", __dir__)

require "bundler/setup" # Set up gems listed in the Gemfile.
require "bootsnap/setup" # Speed up boot time by caching expensive operations.

# Flush stdout immediately so Railway log collector sees output in real time.
# Without this, Ruby buffers stdout when not attached to a TTY (e.g. Docker).
$stdout.sync = true
$stderr.sync = true

# Encode special characters in the DATABASE_URL password BEFORE anything
# reads it. Rails parses DATABASE_URL during Rake task *definition* (databases.rake),
# which fires before config/environment.rb loads. Ruby's URI parser treats '?'
# as a query-string separator, breaking passwords like 'abc?XYZ'.
# config/boot.rb is the earliest file loaded by every Rails entry-point
# (Rake, Puma, rails server, etc.), so this is the only safe location.
if (db_url = ENV["DATABASE_URL"])
  # 1. Encode special characters in the password (?, #, @) so URI parsers
  #    don't misinterpret them as query-string or fragment separators.
  db_url = db_url.sub(%r{^((?:postgresql|postgres)://[^:@]+:)([^@]+)(@)}) do
    prefix   = $1
    password = $2
    at_sign  = $3
    "#{prefix}#{password.gsub("?", "%3F").gsub("#", "%23").gsub("@", "%40")}#{at_sign}"
  end

  # 2. Inject connect_timeout=10 so libpq fails fast instead of hanging
  #    indefinitely when Supabase free-tier DB is paused or unreachable.
  unless db_url.include?("connect_timeout")
    separator = db_url.include?("?") ? "&" : "?"
    db_url = "#{db_url}#{separator}connect_timeout=10"
  end

  ENV["DATABASE_URL"] = db_url
end
