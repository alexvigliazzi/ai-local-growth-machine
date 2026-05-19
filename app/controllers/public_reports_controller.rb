class PublicReportsController < ApplicationController
  allow_unauthenticated_access

  def show
    @report = Report.find_by!(token: params[:token])
  end
end
