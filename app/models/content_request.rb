class ContentRequest < ApplicationRecord
  belongs_to :client
  has_many :content_outputs, dependent: :destroy

  validates :status, inclusion: { in: %w[pending in_progress completed] }

  scope :pending, -> { where(status: "pending") }
end
