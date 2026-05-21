module Api
  class OutreachMessagesController < BaseController
    def index
      messages = OutreachMessage.includes(:lead)
      messages = messages.where(status: params[:status]) if params[:status].present?
      render json: messages.map { |m|
        { id: m.id, lead_id: m.lead_id, channel: m.channel,
          message_type: m.message_type, status: m.status }
      }
    end

    def create
      message = OutreachMessage.new(message_params)
      if message.save
        render json: { id: message.id, status: message.status }, status: :created
      else
        render json: { errors: message.errors.full_messages }, status: :unprocessable_entity
      end
    end

    def update
      message = OutreachMessage.find(params[:id])
      if message.update(message_params)
        render json: { id: message.id, status: message.status }
      else
        render json: { errors: message.errors.full_messages }, status: :unprocessable_entity
      end
    end

    private

    def message_params
      params.require(:outreach_message).permit(:lead_id, :channel, :message, :message_type, :status)
    end
  end
end
