class Lead < ApplicationRecord
  has_many :outreach_messages, dependent: :destroy

  validates :business_name, presence: true
  validates :niche, presence: true
  validates :city, presence: true
  validates :status, inclusion: { in: %w[new contacted qualified proposal_sent converted lost] }

  scope :by_status, ->(status) { where(status: status) }
  scope :recent, -> { order(created_at: :desc) }
end
