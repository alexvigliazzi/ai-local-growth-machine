class CreateContentRequests < ActiveRecord::Migration[8.1]
  def change
    create_table :content_requests, id: :uuid do |t|
      t.references :client, null: false, foreign_key: true, type: :uuid
      t.text :objective
      t.string :tone
      t.text :services
      t.text :references
      t.string :status, default: "pending"

      t.timestamps
    end
  end
end
