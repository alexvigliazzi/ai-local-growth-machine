module Admin
  class DashboardController < BaseController
    def index
      @leads_count = Lead.count
      @clients_count = Client.count
      @pending_requests = ContentRequest.pending.count
      @outputs_count = ContentOutput.count
      @recent_leads = Lead.recent.limit(5)
    end
  end
end
