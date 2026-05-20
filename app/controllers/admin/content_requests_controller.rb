module Admin
  class ContentRequestsController < BaseController
    def index
      @content_requests = ContentRequest.includes(:client).order(created_at: :desc)
      @pending_requests = ContentRequest.where(status: "pending").count
    end

    def show
      @content_request = ContentRequest.find(params[:id])
    end
  end
end
