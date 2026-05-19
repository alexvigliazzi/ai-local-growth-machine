module Admin
  class ClientsController < BaseController
    def index
      @clients = Client.recent.all
    end

    def show
      @client = Client.find(params[:id])
      @content_requests = @client.content_requests.includes(:content_outputs)
    end
  end
end
