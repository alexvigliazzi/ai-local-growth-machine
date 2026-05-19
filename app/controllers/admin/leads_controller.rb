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

    private

    def lead_params
      params.require(:lead).permit(:business_name, :niche, :city, :email, :whatsapp, :instagram_url, :status, :notes, :source)
    end
  end
end
