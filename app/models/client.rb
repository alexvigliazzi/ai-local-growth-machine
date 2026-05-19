class Client < ApplicationRecord
  has_many :content_requests, dependent: :destroy
  has_many :reports, dependent: :destroy

  validates :business_name, presence: true
  validates :niche, presence: true
  validates :city, presence: true
  validates :plan, inclusion: { in: %w[starter pro] }, allow_nil: true

  scope :active, -> { where(status: "active") }
  scope :recent, -> { order(created_at: :desc) }
end
