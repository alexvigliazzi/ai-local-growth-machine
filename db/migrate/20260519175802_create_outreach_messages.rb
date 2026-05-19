class CreateOutreachMessages < ActiveRecord::Migration[8.1]
  def change
    create_table :outreach_messages, id: :uuid do |t|
      t.references :lead, null: false, foreign_key: true, type: :uuid
      t.string :channel
      t.string :message_type
      t.text :message
      t.string :status, default: "pending"

      t.timestamps
    end
  end
end
