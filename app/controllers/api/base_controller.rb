module Api
  class BaseController < ActionController::API
    before_action :authenticate_token

    private

    def authenticate_token
      token = request.headers["Authorization"]&.remove("Bearer ")
      expected = Rails.application.credentials.dig(:api, :token) || ENV["API_TOKEN"]

      unless expected.present? && ActiveSupport::SecurityUtils.secure_compare(token.to_s, expected)
        render json: { error: "unauthorized" }, status: :unauthorized
      end
    end
  end
end
