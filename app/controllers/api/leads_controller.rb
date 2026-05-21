module Api
  class LeadsController < BaseController
    def index
      leads = Lead.all
      leads = leads.where(status: params[:status]) if params[:status].present?
      render json: leads.map { |l| serialize_lead(l) }
    end

    def show
      lead = Lead.find(params[:id])
      render json: serialize_lead(lead)
    end

    private

    def serialize_lead(l)
      {
        id: l.id,
        business_name: l.business_name,
        niche: l.niche,
        city: l.city,
        email: l.email,
        whatsapp: l.whatsapp,
        instagram_url: l.instagram_url,
        notes: l.notes,
        source: l.source,
        status: l.status,
        created_at: l.created_at
      }
    end
  end
end
