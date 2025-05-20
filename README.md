## 🖼️ Gerador de Legendas com IA
Este projeto é uma aplicação web que permite o envio de imagens com palavras-chave, gerando automaticamente uma legenda descritiva usando inteligência artificial.

## 🧠 Funcionalidade Principal
O usuário seleciona uma imagem do seu dispositivo.

Adiciona palavras-chave relacionadas à imagem.

O sistema envia esses dados para um servidor Python (Flask).

O backend processa a imagem com as palavras-chave e retorna uma legenda gerada automaticamente.

A legenda é exibida no histórico, podendo ser copiada ou excluída.

## 📂 Estrutura do Projeto
![image](https://github.com/user-attachments/assets/784228c5-461c-491f-b428-d83f031f690e)

## 🧩 Como Funciona Cada Parte
🔙 app.py (Backend com Flask)
Roda um servidor local em localhost:5000.

Recebe via POST a imagem e as palavras-chave no endpoint /gerar_legenda.

Usa a API do Gemini (ou outro modelo de IA) para gerar a legenda com base na imagem e nas palavras.

Retorna a legenda em formato JSON.

# 🌐 index.html (Frontend)
Estrutura a interface com Tailwind CSS.

Contém o formulário de upload da imagem e palavras-chave.

Exibe o histórico com as legendas geradas.

# 📜 script.js (Lógica JavaScript)
Captura eventos de envio do formulário.

Valida se a imagem e as palavras foram inseridas.

Faz a requisição fetch para o backend Flask.

Mostra mensagens de erro ou sucesso dinamicamente.

Exibe a imagem com a legenda gerada e opções de copiar ou excluir.

## 🚀 Como Executar Localmente
Clone o repositório:

bash
Copiar
Editar
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
Instale as dependências:

bash
Copiar
Editar
pip install flask flask-cors
Execute o backend:

bash
Copiar
Editar
python app.py
Abra o index.html em seu navegador (ou use um servidor local).

## 🌍 Projeto Publicado
Você pode testar o projeto online através do seguinte link:

👉 legendas-com-ia.vercel.app

# 📸 Exemplo de Uso
Escolha uma imagem.

Digite palavras-chave como “praia”, “verão”, “pôr do sol”.

Clique em Enviar.

A legenda aparecerá com opções para copiar ou excluir.

## 💬 Créditos
Projeto desenvolvido por Mariana Meirelles, aluna de Desenvolvimento de Sistemas.
