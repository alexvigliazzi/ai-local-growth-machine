module Admin
  class OutreachMessagesController < BaseController
    def index
      @outreach_messages = OutreachMessage.includes(:lead).order(created_at: :desc)
    end

    def show
      @outreach_message = OutreachMessage.find(params[:id])
    end
  end
end
