# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_05_19_180236) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"
  enable_extension "pgcrypto"

  create_table "clients", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.string "business_name"
    t.string "city"
    t.string "contact_name"
    t.datetime "created_at", null: false
    t.string "email"
    t.string "niche"
    t.string "plan"
    t.string "status", default: "active"
    t.datetime "updated_at", null: false
    t.string "whatsapp"
  end

  create_table "content_outputs", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.text "content"
    t.uuid "content_request_id", null: false
    t.datetime "created_at", null: false
    t.string "output_type"
    t.string "status", default: "draft"
    t.string "title"
    t.datetime "updated_at", null: false
    t.index ["content_request_id"], name: "index_content_outputs_on_content_request_id"
  end

  create_table "content_requests", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.uuid "client_id", null: false
    t.datetime "created_at", null: false
    t.text "objective"
    t.text "references"
    t.text "services"
    t.string "status", default: "pending"
    t.string "tone"
    t.datetime "updated_at", null: false
    t.index ["client_id"], name: "index_content_requests_on_client_id"
  end

  create_table "leads", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.string "business_name"
    t.string "city"
    t.datetime "created_at", null: false
    t.string "email"
    t.string "instagram_url"
    t.string "niche"
    t.text "notes"
    t.string "source"
    t.string "status", default: "new"
    t.datetime "updated_at", null: false
    t.string "whatsapp"
  end

  create_table "outreach_messages", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.string "channel"
    t.datetime "created_at", null: false
    t.uuid "lead_id", null: false
    t.text "message"
    t.string "message_type"
    t.string "status", default: "pending"
    t.datetime "updated_at", null: false
    t.index ["lead_id"], name: "index_outreach_messages_on_lead_id"
  end

  create_table "reports", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.uuid "client_id", null: false
    t.text "content"
    t.datetime "created_at", null: false
    t.string "title"
    t.string "token", null: false
    t.datetime "updated_at", null: false
    t.index ["client_id"], name: "index_reports_on_client_id"
    t.index ["token"], name: "index_reports_on_token", unique: true
  end

  create_table "sessions", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "ip_address"
    t.datetime "updated_at", null: false
    t.string "user_agent"
    t.uuid "user_id", null: false
    t.index ["user_id"], name: "index_sessions_on_user_id"
  end

  create_table "users", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "email_address", null: false
    t.string "password_digest", null: false
    t.datetime "updated_at", null: false
    t.index ["email_address"], name: "index_users_on_email_address", unique: true
  end

  add_foreign_key "content_outputs", "content_requests"
  add_foreign_key "content_requests", "clients"
  add_foreign_key "outreach_messages", "leads"
  add_foreign_key "reports", "clients"
  add_foreign_key "sessions", "users"
end
