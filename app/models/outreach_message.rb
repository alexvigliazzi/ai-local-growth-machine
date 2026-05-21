class OutreachMessage < ApplicationRecord
  belongs_to :lead

  validates :channel, inclusion: { in: %w[whatsapp email instagram_dm] }
  validates :message, presence: true, unless: :queued?
  validates :status, inclusion: { in: %w[queued pending sent replied] }

  def queued? = status == "queued"
end
