# Instalar bibliotecas necessárias
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    import google.generativeai as genai
except ImportError:
    install("google-generativeai")

try:
    import pandas as pd
except ImportError:
    install("pandas")

try:
    from dotenv import load_dotenv
except ImportError:
    install("python-dotenv")

import os
import json

import os
import json
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


# Carregar as variáveis de ambiente do arquivo .env
load_dotenv("/content/drive/MyDrive/Alura_Postagem_Instagram_OpenAI/chave.env")

# Acessa a chave
api_key = os.getenv('GOOGLE_API_KEY')

# Configurar a chave da API manualmente
genai.configure(api_key=api_key)


generation_config = {
  "temperature": 0,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config
)

reviews = pd.read_csv('/content/drive/MyDrive/Alura_Boost_Transcricao_Imagem/reviews-entrega-MercadoAgil-imagens.csv')
for index, review in reviews.iterrows():
  reviewer_id = review['reviewer_id']
  reviewer_name = review['reviewer_name']  
  reviewer_email = review['reviewer_email']
  review_image = review['review_image']

  print(f'Processando imagem do review {reviewer_id} de {reviewer_email}...')
  arquivo_Imagem = genai.upload_file(path=f'/content/drive/MyDrive/Alura_Boost_Transcricao_Imagem/Imagem/{review_image}')
  prompt = 'Transcreva detalhadamente o arquivo de imagem em anexo.'
  response = model.generate_content([prompt, arquivo_Imagem])
  with open(f"/content/drive/MyDrive/Alura_Boost_Transcricao_Imagem/Imagem/{reviewer_id}.txt", "w", encoding="utf-8") as arquivo:
    print(f'Salvando transcrição de imagem do review {reviewer_id} de {reviewer_name}...')
    arquivo.write(response.text)
