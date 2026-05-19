module Admin
  class ReportsController < BaseController
    def index
      @reports = Report.includes(:client).order(created_at: :desc)
    end

    def show
      @report = Report.find(params[:id])
    end
  end
end
