module Admin
  class ContentRequestsController < BaseController
    def index
      @content_requests = ContentRequest.includes(:client).order(created_at: :desc)
      @pending_requests = ContentRequest.where(status: "pending").count
    end

    def show
      @content_request = ContentRequest.find(params[:id])
    end

    def queue_generation
      @content_request = ContentRequest.find(params[:id])
      @content_request.update!(status: "pending")
      redirect_to admin_content_request_path(@content_request),
        notice: "Enfileirado. Rode: python run.py content"
    end
  end
end
