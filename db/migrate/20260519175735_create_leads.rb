class CreateLeads < ActiveRecord::Migration[8.1]
  def change
    create_table :leads, id: :uuid do |t|
      t.string :business_name
      t.string :niche
      t.string :city
      t.string :email
      t.string :whatsapp
      t.string :instagram_url
      t.string :status, default: "new"
      t.text :notes
      t.string :source

      t.timestamps
    end
  end
end
