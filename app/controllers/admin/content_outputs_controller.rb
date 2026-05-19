module Admin
  class ContentOutputsController < BaseController
    def index
      @content_outputs = ContentOutput.includes(content_request: :client).order(created_at: :desc)
    end

    def show
      @content_output = ContentOutput.find(params[:id])
    end

    def edit
      @content_output = ContentOutput.find(params[:id])
    end

    def update
      @content_output = ContentOutput.find(params[:id])
      if @content_output.update(content_output_params)
        redirect_to admin_content_output_path(@content_output), notice: "Conteudo atualizado."
      else
        render :edit, status: :unprocessable_entity
      end
    end

    private

    def content_output_params
      params.require(:content_output).permit(:title, :content, :status, :output_type)
    end
  end
end
