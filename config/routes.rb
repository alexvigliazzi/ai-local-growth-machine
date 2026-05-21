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
    resources :leads do
      member { post :queue_outreach }
    end
    resources :clients
    resources :content_requests do
      member { post :queue_generation }
    end
    resources :content_outputs
    resources :outreach_messages
    resources :reports
  end

  # API (orchestrator local)
  namespace :api do
    resources :clients, only: %i[index show]
    resources :leads, only: %i[index show]
    resources :content_requests, only: %i[index show update]
    resources :content_outputs, only: %i[create]
    resources :outreach_messages, only: %i[index create update]
    resources :reports, only: %i[create]
  end

  # Health
  get "up" => "rails/health#show", as: :rails_health_check
end
