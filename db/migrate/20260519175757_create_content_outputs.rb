class CreateContentOutputs < ActiveRecord::Migration[8.1]
  def change
    create_table :content_outputs, id: :uuid do |t|
      t.references :content_request, null: false, foreign_key: true, type: :uuid
      t.string :output_type
      t.string :title
      t.text :content
      t.string :status, default: "draft"

      t.timestamps
    end
  end
end
