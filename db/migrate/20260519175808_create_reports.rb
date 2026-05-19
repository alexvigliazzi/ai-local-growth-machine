class CreateReports < ActiveRecord::Migration[8.1]
  def change
    create_table :reports, id: :uuid do |t|
      t.references :client, null: false, foreign_key: true, type: :uuid
      t.string :title
      t.text :content
      t.string :token, null: false

      t.timestamps
    end

    add_index :reports, :token, unique: true
  end
end
