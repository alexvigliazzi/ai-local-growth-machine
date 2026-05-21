module Admin
  class LeadsController < BaseController
    def index
      @leads = Lead.recent.all
    end

    def show
      @lead = Lead.find(params[:id])
    end

    def edit
      @lead = Lead.find(params[:id])
    end

    def update
      @lead = Lead.find(params[:id])
      if @lead.update(lead_params)
        redirect_to admin_lead_path(@lead), notice: "Lead atualizado."
      else
        render :edit, status: :unprocessable_entity
      end
    end

    def queue_outreach
      @lead = Lead.find(params[:id])
      channel = params[:channel].presence_in(%w[whatsapp email instagram_dm]) || "whatsapp"
      message_type = params[:message_type].presence_in(%w[primeiro_contato follow_up proposta pos_venda]) || "primeiro_contato"

      msg = @lead.outreach_messages.create!(
        channel: channel,
        message_type: message_type,
        status: "queued"
      )

      redirect_to admin_lead_path(@lead),
        notice: "Mensagem enfileirada (#{channel}). Rode: python run.py outreach"
    end

    private

    def lead_params
      params.require(:lead).permit(:business_name, :niche, :city, :email, :whatsapp, :instagram_url, :status, :notes, :source)
    end
  end
end
