class ContentOutput < ApplicationRecord
  belongs_to :content_request

  validates :output_type, inclusion: { in: %w[video_script social_post content_plan] }
  validates :title, presence: true
  validates :status, inclusion: { in: %w[draft review approved] }
end
