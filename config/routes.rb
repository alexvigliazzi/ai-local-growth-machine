Rails.application.routes.draw do
  resource :session
  resources :passwords, param: :token
  # Public
  root "pages#landing"
  get "briefing", to: "briefings#new"
  post "briefing", to: "briefings#create"
  get "briefing/obrigado", to: "briefings#thank_you", as: :briefing_thank_you
  get "r/:token", to: "public_reports#show", as: :public_report

  # Admin
  namespace :admin do
    root "dashboard#index"
    resources :leads
    resources :clients
    resources :content_requests
    resources :content_outputs
    resources :outreach_messages
    resources :reports
  end

  # API (LangGraph callback)
  namespace :api do
    post "content_outputs", to: "content_outputs#create"
    post "outreach_messages", to: "outreach_messages#create"
  end

  # Health
  get "up" => "rails/health#show", as: :rails_health_check
end
