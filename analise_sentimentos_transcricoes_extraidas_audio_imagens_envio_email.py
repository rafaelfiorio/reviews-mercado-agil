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
import smtplib
from email.mime.text import MIMEText

load_dotenv()


# Carregar as variáveis de ambiente do arquivo .env
load_dotenv("/content/drive/MyDrive/Alura_Postagem_Instagram_OpenAI/chave.env")

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
import smtplib
from email.mime.text import MIMEText
import time # import the time module

load_dotenv()


# Carregar as variáveis de ambiente do arquivo .env
load_dotenv("/content/drive/MyDrive/Alura_Postagem_Instagram_OpenAI/chave.env")

# Acessa a chave
api_key = os.getenv('GOOGLE_API_KEY')
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')

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

# Lista para armazenar as informações de cada transcrição
transcricoes = []

# transcrevendo as imagens
reviews = pd.read_csv('/content/drive/MyDrive/Alura_Boost_Transcricao_Imagem/reviews-entrega-MercadoAgil-imagens.csv')
for index, review in reviews.iterrows():
  reviewer_id = review['reviewer_id']
  reviewer_name = review['reviewer_name']  
  reviewer_email = review['reviewer_email']
  review_image = review['review_image']

  print(f'Processando imagem do review {reviewer_id} de {reviewer_email}...')
  arquivo_Imagem = genai.upload_file(path=f'/content/drive/MyDrive/Alura_Boost_Transcricao_Imagem/Imagem/{review_image}')
  prompt = 'Transcreva detalhadamente o arquivo de imagem em anexo.'
  
  # Implement retry logic with exponential backoff
  max_retries = 3
  retry_count = 0
  while retry_count < max_retries:
    try:
      response = model.generate_content([prompt, arquivo_Imagem])
      break  # Break the loop if successful
    except ConnectionError as e:
      print(f"Connection error processing image for review {reviewer_id}: {e}")
      retry_count += 1
      wait_time = 2 ** retry_count  # Exponential backoff
      print(f"Retrying in {wait_time} seconds...")
      time.sleep(wait_time)
    except Exception as e: # Catching a broader range of exceptions
      print(f"Error processing image for review {reviewer_id}: {e}")
      break # Break the loop if a different error occurs
  
  if retry_count == max_retries:
    print(f"Failed to process image for review {reviewer_id} after multiple retries.")
    continue # Skip to the next iteration if all retries fail

  # Adicionar as informações da transcrição à lista
  transcricoes.append({
        'reviewer_id': reviewer_id,
        'reviewer_name': reviewer_name,
        'reviewer_email': reviewer_email,
        'reviewer_transcricao': response.text
  })


# transcrevendo os audios
reviews = pd.read_csv('/content/drive/MyDrive/Alura_Boost_Transcricao_Audio/reviews-entrega-MercadoAgil-audio.csv')
for index, review in reviews.iterrows():
  reviewer_id = review['reviewer_id']
  reviewer_name = review['reviewer_name']
  reviewer_email = review['reviewer_email']
  review_audio = review['review_audio']

  print(f'Processando áudio do review {reviewer_id} de {reviewer_email}...')
  arquivo_audio = genai.upload_file(path=f'/content/drive/MyDrive/Alura_Boost_Transcricao_Audio/Audio/{review_audio}')
  prompt = 'Transcreva detalhadamente o arquivo de áudio em anexo.'
  # Added a try-except block to catch the ConnectionError and other potential errors
  try:
    response = model.generate_content([prompt, arquivo_audio])
  except (ConnectionError, Exception) as e: # Catching a broader range of exceptions
    print(f"Error processing audio for review {reviewer_id}: {e}")
    continue # Skip to the next
  # Adicionar as informações da transcrição à lista # This line was indented incorrectly, causing the data to not be appended if a ConnectionError occurred
  transcricoes.append({
        'reviewer_id': reviewer_id,
        'reviewer_name': reviewer_name,
        'reviewer_email': reviewer_email,
        'reviewer_transcricao': response.text
  })

# Criar um DataFrame a partir da lista de transcrições
df = pd.DataFrame(transcricoes)

# Salvar o DataFrame como um arquivo CSV
df.to_csv('/content/drive/MyDrive/Alura_Boost_email_automatico_insatisfeitos_audio_imagem/avaliacoes.csv', index=False)  



#Carregando as transcrições
reviews = pd.read_csv("/content/drive/MyDrive/Alura_Boost_email_automatico_insatisfeitos_audio_imagem/avaliacoes.csv")
reviews = reviews[["reviewer_id", "reviewer_name", "reviewer_email", "reviewer_transcricao"]]

#Início da Análise de Sentimento
modelo = "gemini-pro"


generation_config = {
  "temperature": 0,
  "response_mime_type": "application/json",
}

#Configura os parâmetros do objeto model passado para o gemini
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="""
Você é um analisador de sentimentos de uma empresa de entrega.
Você deve analisar o sentimento das avaliações de clientes apenas em relação à entrega e não à outros aspectos.
A sua análise deve responder para cada avaliação dos clientes:
  "negativo", "neutro" ou "positivo".
Dê uma nota para o sentimento de cada avaliação dos clientes, onde:
  -5 é totalmente negativo, 0 é neutro, para avaliações inconclusivas quanto à entrega, 5 é totalmente positivo.
Para as análise que resultaram valor "negativo" deve sugerir um texto de e-mail a ser enviado para o cliente.
O formato da resposta deve ser um JSON como a seguir:

```json
[
  {
  "reviewer_id": <id aqui>,
  "reviewer_name": <nome aqui>,
  "reviewer_email": <email aqui>
  "sentimento": "<sentimento aqui>"
  "nota": "<nota aqui>"
  "texto_email": "<texto email aqui>"
 }
]
```
"""
)

prompt_usuario = f"""
Analise o sentimento das avaliações do CSV a seguir:

```csv
{reviews.to_csv()}
```
"""

response = model.generate_content(prompt_usuario)
conteudo = response.text

# Converte o arquivo retornado para Json
json_resultado = json.loads(conteudo)


# Criar um DataFrame
resultados_df = pd.DataFrame(json_resultado)



#Disparando emails para avaliações negativas
# Configurações do SMTP do Mailtrap (substitua pelos seus dados)
smtp_server = "sandbox.smtp.mailtrap.io"
smtp_port = 2525


for index, row in resultados_df.iterrows():
  if row['sentimento'] == 'negativo':
    # Conteúdo do email
    sender_email = "meu_email@example.com"
    receiver_email = row['reviewer_email']  # Access email directly from row
    subject = "Email Hare Express"
    body = row['texto_email']  # Access email text directly from row

    # Criação do objeto mensagem
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Conexão com o servidor SMTP e envio do email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
      server.starttls()
      server.login(smtp_username, smtp_password)
      server.sendmail(sender_email, receiver_email, message.as_string())




