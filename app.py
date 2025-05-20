# Importa o módulo 'os' para interagir com o sistema operacional,
# como por exemplo, para acessar variáveis de ambiente.
import os

# Importa classes do Flask para criar a aplicação web, lidar com requisições e retornar respostas JSON.
from flask import Flask, request, jsonify

# Importa CORS para permitir requisições de diferentes origens (necessário para front-ends em domínios diferentes).
from flask_cors import CORS

# Importa a função para carregar variáveis de ambiente de um arquivo .env.
from dotenv import load_dotenv

# Importa o SDK do Google Generative AI.
import google.generativeai as genai

# Importa os tipos Enum para definir categorias de dano e limiares de bloqueio para as configurações de segurança.
# Isso torna o código mais legível e menos propenso a erros do que usar strings diretamente.
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Carrega as variáveis de ambiente definidas no arquivo .env para o ambiente de execução.
# Isso é útil para manter chaves de API e outras configurações sensíveis fora do código.
load_dotenv()

# Cria uma instância da aplicação Flask.
# __name__ é uma variável especial em Python que representa o nome do módulo atual.
app = Flask(__name__)

# Habilita o CORS (Cross-Origin Resource Sharing) para a aplicação Flask.
# Isso permite que a API seja acessada por aplicações web rodando em outros domínios/portas.
CORS(app)

# Bloco try-except para configurar a API do Google Generative AI de forma segura.
try:
    # Obtém a chave da API do Google a partir das variáveis de ambiente.
    api_key = os.getenv("GOOGLE_API_KEY")
    # Verifica se a chave da API foi realmente carregada.
    if not api_key:
        # Se a chave não for encontrada, lança um erro para alertar o desenvolvedor.
        raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")
    # Configura o SDK do Google Generative AI com a chave da API.
    genai.configure(api_key=api_key)
    print("Chave da API do Google configurada com sucesso.") # Mensagem de sucesso
except ValueError as e:
    # Captura o erro se a chave da API não estiver definida e imprime uma mensagem.
    print(f"Erro ao configurar a API do Google: {e}")
    # exit(1) # Descomente esta linha se quiser que a aplicação pare caso a chave não seja encontrada.
            # No ambiente de produção, pode ser melhor logar o erro e tentar continuar ou retornar um erro específico na API.

# Define as configurações de geração para o modelo de IA.
# Estas configurações influenciam como o modelo gera o texto.
generation_config = {
    "temperature": 0.8,       # Controla a aleatoriedade da saída. Valores mais altos (ex: 0.8) tornam a saída mais criativa e aleatória. Valores mais baixos (ex: 0.2) tornam-na mais determinística e focada.
    "top_p": 0.9,             # Amostragem por nucleus. Controla a diversidade. O modelo considera apenas os tokens com probabilidade acumulada até top_p.
    "top_k": 40,              # O modelo seleciona o próximo token entre os 'k' tokens mais prováveis.
    "max_output_tokens": 150, # Define o número máximo de tokens (palavras/subpalavras) que o modelo pode gerar na resposta.
}

# ----- INÍCIO DA DEFINIÇÃO DOS SAFETY SETTINGS -----
# Define as configurações de segurança para o modelo.
# Isso ajuda a filtrar conteúdo potencialmente prejudicial.
safety_settings = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT, # Categoria: Assédio
        "threshold": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE, # Limiar: Bloquear se a confiança de ser assédio for Baixa ou Superior. MAIS RESTRITIVO.
    },
    {
        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,  # Categoria: Discurso de Ódio
        "threshold": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE, # Limiar: Bloquear se a confiança de ser discurso de ódio for Baixa ou Superior. MAIS RESTRITIVO.
    },
    {
        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, # Categoria: Conteúdo Sexualmente Explícito
        "threshold": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,      # Limiar: Bloquear se a confiança de ser sexualmente explícito for Baixa ou Superior. MAIS RESTRITIVO.
    },
    {
        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, # Categoria: Conteúdo Perigoso
        "threshold": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,      # Limiar: Bloquear se a confiança de ser conteúdo perigoso for Baixa ou Superior. MAIS RESTRITIVO.
    },
]
# ----- FIM DA DEFINIÇÃO DOS SAFETY SETTINGS -----

# Inicializa a variável 'model' como None. Ela armazenará o modelo de IA carregado.
model = None
# Bloco try-except para inicializar o modelo generativo.
try:
    # Carrega o modelo generativo especificado (gemini-1.5-flash-latest).
    # Passa as configurações de geração e as configurações de segurança definidas anteriormente.
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest", # Nome do modelo a ser usado.
        generation_config=generation_config,  # Aplica as configurações de geração.
        safety_settings=safety_settings       # Aplica as configurações de segurança.
    )
    # Imprime uma mensagem indicando que o modelo foi inicializado com sucesso.
    print("Modelo GenerativeModel (gemini-1.5-flash-latest) inicializado com sucesso com safety settings atualizados.")
except Exception as e:
    # Captura e imprime qualquer erro que ocorra durante a inicialização do modelo.
    print(f"Erro ao inicializar o modelo GenerativeModel: {e}")
    # Em um app de produção, você pode querer logar este erro de forma mais robusta
    # e talvez impedir que o app inicie ou retorne um status de erro global.

# ... (o restante do seu código app.py permanece o mesmo) ...

# Define a rota '/gerar_legenda' que aceita requisições POST.
# Esta rota será usada para receber uma imagem e gerar uma legenda para ela.
@app.route('/gerar_legenda', methods=['POST'])
def gerar_legenda_route():
    # Verifica se o modelo de IA foi inicializado corretamente.
    if model is None:
        # Se o modelo não estiver carregado, retorna um erro 500 (Erro Interno do Servidor).
        return jsonify({"error": "O modelo de IA não foi inicializado corretamente. Verifique a configuração da API e os logs do servidor."}), 500

    # Verifica se um arquivo foi incluído na requisição ('file' é o nome esperado do campo do formulário).
    if 'file' not in request.files:
        # Se nenhum arquivo for encontrado, retorna um erro 400 (Requisição Inválida).
        return jsonify({"error": "Nenhum arquivo de imagem enviado"}), 400
    
    # Obtém o arquivo da requisição.
    file = request.files['file']
    # Obtém a lista de palavras-chave do formulário. 'getlist' é usado caso múltiplas palavras-chave sejam enviadas com o mesmo nome.
    keywords = request.form.getlist('keywords')

    # Verifica se o nome do arquivo está vazio (o que pode acontecer se o campo de arquivo for enviado sem um arquivo selecionado).
    if file.filename == '':
        # Se nenhum arquivo for selecionado, retorna um erro 400.
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    # Informa no console se nenhuma palavra-chave foi fornecida.
    if not keywords:
        print("Nenhuma palavra-chave fornecida, gerando legenda apenas com base na imagem.")

    # Bloco try-except para lidar com possíveis erros durante o processamento da imagem e a chamada da API.
    try:
        # Lê o conteúdo do arquivo de imagem em bytes.
        image_bytes = file.read()
        
        # Monta o prompt (instrução) para o modelo de IA.
        # Instrução base para a geração da legenda.
        prompt_text = "Crie uma legenda curta, criativa e única para esta imagem, com no máximo 3 frases.Não muito sensacionalista."
        # Se palavras-chave foram fornecidas, adiciona-as ao prompt.
        if keywords:
            prompt_text += f" Use as seguintes palavras-chave como inspiração principal: {', '.join(keywords)}."
        # Adiciona instruções específicas sobre o formato da resposta desejada, para evitar frases introdutórias ou formatação indesejada.
        # Esta é uma parte crucial da "engenharia de prompt" para obter o resultado esperado.
        prompt_text += " Forneça APENAS o texto da legenda final. NÃO inclua frases introdutórias como 'Claro, aqui está...', 'Aqui estão algumas opções:', ou 'Legenda gerada:'. NÃO numere ou rotule as legendas como 'Opção 1', 'Opção 2', etc. NÃO peça para escolher uma opção. NÃO use formatação Markdown como asteriscos para negrito ou outros símbolos de formatação. Apenas o texto puro da legenda."
        
        # Imprime o prompt final que será enviado à API (útil para debugging).
        print(f"Prompt enviado para a API: {prompt_text}")

        # Prepara o conteúdo a ser enviado para o modelo.
        # Consiste no prompt textual e nos dados da imagem com seu tipo MIME.
        contents = [
            prompt_text, # A instrução textual.
            {
                "mime_type": file.mimetype, # O tipo MIME do arquivo (ex: 'image/jpeg', 'image/png').
                "data": image_bytes         # Os bytes da imagem.
            }
        ]
        
        # Envia o conteúdo para o modelo de IA gerar a legenda.
        # O modelo já foi inicializado com as configurações de geração e segurança.
        response = model.generate_content(contents)

        # Define uma legenda padrão caso a geração falhe ou a resposta seja vazia.
        legenda = "Não foi possível gerar a legenda ou a resposta do modelo está vazia." 
        
        # Verifica se a API retornou uma resposta.
        if response:
            # Bloco try-except para tentar extrair a legenda da estrutura da resposta da API.
            # A estrutura da resposta pode variar um pouco ou ter erros.
            try:
                # Tenta acessar a legenda através da lista de 'candidates' na resposta.
                # Esta é a forma mais comum de obter o texto gerado.
                if response.candidates and \
                   response.candidates[0].content and \
                   response.candidates[0].content.parts:
                    
                    # Concatena todas as partes de texto encontradas no primeiro candidato.
                    legenda_gerada = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text')).strip()
                    # Se uma legenda foi efetivamente extraída e não está vazia.
                    if legenda_gerada:
                        legenda = legenda_gerada
                    else:
                        # Se 'parts' estava vazio mas 'response.text' existe (fallback).
                        if hasattr(response, 'text') and response.text and response.text.strip():
                            legenda = response.text.strip()
                        else: 
                            # VERIFICA SE A GERAÇÃO FOI BLOQUEADA PELAS CONFIGURAÇÕES DE SEGURANÇA.
                            # Acessa o motivo do término da geração do primeiro candidato.
                            finish_reason = response.candidates[0].finish_reason
                            if finish_reason == 'SAFETY': # Ou o enum correspondente: FinishReason.SAFETY
                                legenda = f"A legenda não pôde ser gerada devido às configurações de segurança. Conteúdo potencialmente inadequado detectado."
                                # Loga detalhes do bloqueio, se disponíveis.
                                print(f"Geração bloqueada por motivo de segurança. Detalhes (se disponíveis nos safety_ratings): {response.candidates[0].safety_ratings}")
                            # Verifica se o prompt foi bloqueado por outros motivos.
                            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                                legenda = f"Legenda bloqueada. Motivo: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                            else:
                                # Se não houve legenda gerada nem bloqueio claro, loga a resposta para investigação.
                                print(f"Resposta do modelo não continha texto extraível nas partes nem bloqueio: {response}")
                
                # Fallback: Se a estrutura 'candidates' não for como esperado, tenta acessar 'response.text' diretamente.
                # Algumas respostas mais simples ou de erro podem vir assim.
                elif hasattr(response, 'text') and response.text and response.text.strip():
                     legenda = response.text.strip()
                
                # VERIFICA SE A GERAÇÃO FOI BLOQUEADA PELAS CONFIGURAÇÕES DE SEGURANÇA (ao nível do prompt/imagem inicial).
                # Isso pode acontecer se o próprio prompt ou a imagem forem considerados inadequados.
                elif response.prompt_feedback and response.prompt_feedback.block_reason == 'SAFETY':
                    legenda = f"A legenda não pôde ser gerada devido às configurações de segurança. Conteúdo potencialmente inadequado detectado no prompt ou na imagem."
                    print(f"Geração bloqueada por motivo de segurança no prompt/imagem. Detalhes (se disponíveis nos safety_ratings): {response.prompt_feedback.safety_ratings}")
                # Verifica outros motivos de bloqueio no feedback do prompt.
                elif response.prompt_feedback and response.prompt_feedback.block_reason:
                     legenda = f"Legenda bloqueada. Motivo: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                else:
                    # Se a resposta não tem 'candidates' válidos, nem 'text', nem um bloqueio claro, loga a resposta.
                    print(f"Resposta inesperada do modelo (sem texto, candidates válidos ou bloqueio claro): {response}")

                # Bloco de "limpeza" da legenda: remove frases introdutórias ou finais indesejadas que o modelo possa ter gerado
                # mesmo com as instruções no prompt.
                # Só executa se a legenda não for uma mensagem de bloqueio.
                if not legenda.startswith("Legenda bloqueada") and not legenda.startswith("A legenda não pôde ser gerada devido às configurações de segurança"):
                    # Lista de frases comuns que o modelo pode adicionar no início.
                    frases_indesejadas_inicio = [
                        "claro, aqui está uma legenda:", "claro, aqui está:", "aqui está sua legenda:", "aqui está:",
                        "legenda:", "opção 1:", "opção 2:", "opção 3:"
                    ]
                    # Converte a legenda para minúsculas para comparação case-insensitive.
                    legenda_lower_test = legenda.lower()
                    for frase in frases_indesejadas_inicio:
                        if legenda_lower_test.startswith(frase):
                            # Remove a frase indesejada do início da legenda.
                            legenda = legenda[len(frase):].lstrip(": ").strip() 
                            legenda_lower_test = legenda.lower() # Atualiza para o próximo loop, se necessário
                    
                    # Lista de frases comuns que o modelo pode adicionar no final.
                    frase_final_indesejada = "escolha a opção que melhor se adapta ao seu estilo e à mensagem que você deseja transmitir."
                    if legenda.lower().endswith(frase_final_indesejada):
                        # Remove a frase indesejada do final da legenda.
                        legenda = legenda[:-(len(frase_final_indesejada))].strip()

            # Captura erros de atributo (ex: tentar acessar 'response.candidates' quando não existe).
            except AttributeError as e_attr:
                print(f"AttributeError ao processar resposta do modelo: {e_attr}. Resposta: {response}")
                # Tenta um fallback mais simples se possível, ou informa sobre o bloqueio.
                if hasattr(response, 'text') and response.text:
                     legenda = response.text.strip() 
                elif response.prompt_feedback and response.prompt_feedback.block_reason:
                    legenda = f"Legenda bloqueada. Motivo: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                else:
                    legenda = "Erro ao processar a resposta do modelo (AttributeError)."
            # Captura outros erros genéricos durante a extração da legenda.
            except Exception as e_parse:
                print(f"Erro genérico ao extrair legenda da resposta: {e_parse}. Resposta: {response}")
                # Informa sobre o bloqueio, se aplicável.
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    legenda = f"Legenda bloqueada. Motivo: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                else:
                    legenda = "Erro ao extrair a legenda da resposta do modelo."
        
        # Imprime a legenda final que será retornada (útil para debugging).
        print(f"Legenda gerada final: {legenda}")
        # Retorna a legenda gerada (ou mensagem de erro/bloqueio) como JSON.
        return jsonify({"legenda": legenda})

    # Captura exceções que podem ocorrer no bloco 'try' principal (ex: problemas de rede, erros da API).
    except Exception as e:
        # Imprime o erro no console do servidor.
        print(f"Erro durante a geração da legenda (nível superior): {e}")
        # Trata erros específicos da API para fornecer feedback mais útil ao cliente.
        if "API key not valid" in str(e) or "API_KEY_INVALID" in str(e):
             return jsonify({"error": "Chave de API inválida ou não configurada corretamente. Verifique suas credenciais e a configuração do servidor."}), 500
        if "DeadlineExceeded" in str(e): # Erro de timeout
            return jsonify({"error": "A solicitação à API demorou muito para responder (timeout)."}), 504 # Gateway Timeout
        if "404" in str(e) and ("model" in str(e).lower() or "deprecated" in str(e).lower()): # Modelo não encontrado ou descontinuado
            return jsonify({"error": f"O modelo de IA especificado não foi encontrado ou foi descontinuado. Verifique a configuração do servidor. Detalhe: {str(e)}"}), 500
        if "quota" in str(e).lower() or "ResourceExhausted" in str(e): # Cota da API excedida
            return jsonify({"error": "Cota da API excedida. Por favor, verifique seus limites de uso na plataforma do Google AI."}), 429 # Too Many Requests
        
        # Para outros erros não especificados, retorna um erro genérico 500.
        return jsonify({"error": f"Ocorreu um erro interno ao gerar a legenda. Tente novamente mais tarde."}), 500

# Este bloco é executado apenas quando o script é rodado diretamente (não quando importado como módulo).
if __name__ == '__main__':
    # Inicia o servidor de desenvolvimento Flask.
    # debug=True habilita o modo de depuração, que recarrega o servidor automaticamente após alterações no código e fornece mais informações de erro.
    # port=5000 define a porta em que o servidor irá escutar.
    app.run(debug=True, port=5000)