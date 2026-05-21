module Api
  class ContentOutputsController < BaseController
    def create
      output = ContentOutput.new(output_params)
      if output.save
        render json: { id: output.id, status: output.status }, status: :created
      else
        render json: { errors: output.errors.full_messages }, status: :unprocessable_entity
      end
    end

    private

    def output_params
      params.require(:content_output).permit(:content_request_id, :title, :content, :output_type, :status)
    end
  end
end
