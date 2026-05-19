class BriefingsController < ApplicationController
  allow_unauthenticated_access

  def new
    @lead = Lead.new
  end

  def create
    @lead = Lead.new(lead_params)
    @lead.source = "briefing_form"

    if @lead.save
      # Create client and content request from the briefing
      client = Client.create!(
        business_name: @lead.business_name,
        niche: @lead.niche,
        city: @lead.city,
        contact_name: params[:contact_name],
        whatsapp: @lead.whatsapp,
        email: @lead.email,
        plan: "starter"
      )

      ContentRequest.create!(
        client: client,
        objective: params[:objective],
        tone: params[:tone] || "profissional",
        services: params[:services],
        references: params[:references]
      )

      redirect_to briefing_thank_you_path
    else
      render :new, status: :unprocessable_entity
    end
  end

  def thank_you
  end

  private

  def lead_params
    params.permit(:business_name, :niche, :city, :email, :whatsapp, :instagram_url, :notes)
  end
end
