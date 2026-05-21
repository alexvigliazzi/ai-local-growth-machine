module Api
  class ReportsController < BaseController
    def create
      report = Report.new(report_params)
      if report.save
        render json: { id: report.id, token: report.token }, status: :created
      else
        render json: { errors: report.errors.full_messages }, status: :unprocessable_entity
      end
    end

    private

    def report_params
      params.require(:report).permit(:client_id, :title, :content)
    end
  end
end
