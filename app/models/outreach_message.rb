class OutreachMessage < ApplicationRecord
  belongs_to :lead

  validates :channel, inclusion: { in: %w[whatsapp email instagram_dm] }
  validates :message, presence: true
  validates :status, inclusion: { in: %w[pending sent replied] }
end
