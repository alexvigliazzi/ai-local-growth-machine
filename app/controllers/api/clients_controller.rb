module Api
  class ClientsController < BaseController
    def index
      clients = Client.all
      clients = clients.where(status: params[:status]) if params[:status].present?
      render json: clients.map { |c| serialize_client(c) }
    end

    def show
      client = Client.find(params[:id])
      render json: serialize_client(client).merge(weekly_summary(client))
    end

    private

    def serialize_client(c)
      {
        id: c.id,
        business_name: c.business_name,
        niche: c.niche,
        city: c.city,
        contact_name: c.contact_name,
        email: c.email,
        whatsapp: c.whatsapp,
        plan: c.plan,
        status: c.status
      }
    end

    def weekly_summary(client)
      week_start = 1.week.ago.beginning_of_day
      outputs = ContentOutput.joins(:content_request)
                             .where(content_requests: { client_id: client.id })
                             .where("content_outputs.created_at >= ?", week_start)

      {
        weekly_outputs: outputs.map { |o|
          { id: o.id, title: o.title, output_type: o.output_type, status: o.status }
        },
        weekly_output_count: outputs.count
      }
    end
  end
end
