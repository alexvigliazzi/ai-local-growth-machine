module Api
  class ContentRequestsController < BaseController
    def index
      requests = ContentRequest.includes(:client)
      requests = requests.where(status: params[:status]) if params[:status].present?
      render json: requests.map { |r| serialize_request(r) }
    end

    def show
      request = ContentRequest.includes(:client).find(params[:id])
      render json: serialize_request(request)
    end

    def update
      request = ContentRequest.find(params[:id])
      request.update!(status: params[:status])
      render json: serialize_request(request)
    end

    private

    def serialize_request(r)
      {
        id: r.id,
        status: r.status,
        objective: r.objective,
        services: r.services,
        tone: r.tone,
        references: r.references,
        created_at: r.created_at,
        client: {
          id: r.client.id,
          business_name: r.client.business_name,
          niche: r.client.niche,
          city: r.client.city,
          plan: r.client.plan
        }
      }
    end
  end
end
