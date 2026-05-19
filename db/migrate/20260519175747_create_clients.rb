class CreateClients < ActiveRecord::Migration[8.1]
  def change
    create_table :clients, id: :uuid do |t|
      t.string :business_name
      t.string :niche
      t.string :city
      t.string :contact_name
      t.string :whatsapp
      t.string :email
      t.string :plan
      t.string :status, default: "active"

      t.timestamps
    end
  end
end
