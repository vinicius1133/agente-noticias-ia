import os
import smtplib
import time
import urllib.request
import xml.etree.ElementTree as ET
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from google import genai

load_dotenv()

class AgenteNoticiasIA:
    def __init__(self):
        self.nome = "AI Trends Agent"
        self.rss_url = "https://news.google.com/rss/search?q=Artificial+Intelligence+LLM+models&hl=en-US&gl=US&ceid=US:en"
        self.client = genai.Client()

    def buscar_novidades(self):
        print(f"🤖 [{self.nome}]: Buscando as últimas novidades sobre IA...\n")
        try:
            req = urllib.request.Request(self.rss_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            noticias = root.findall('./channel/item')[:5]
            
            dados = []
            for idx, item in enumerate(noticias, 1):
                titulo = item.find('title').text
                link = item.find('link').text
                dados.append(f"{idx}. {titulo}\n   Link: {link}")
            
            return "\n".join(dados)
        except Exception as e:
            print(f"Erro ao buscar novidades: {e}")
            return ""

    def enviar_email(self, conteudo_markdown):
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        receiver = os.getenv("EMAIL_RECEIVER")

        if not all([sender, password, receiver]):
            print("⚠️ Variáveis de e-mail ausentes no .env. Envio cancelado.")
            return

        print(f"✉️ [{self.nome}]: Enviando e-mail para {receiver}...")

        msg = MIMEMultipart()
        msg['From'] = f"{self.nome} <{sender}>"
        msg['To'] = receiver
        msg['Subject'] = "🚨 Resumo Diário: Notícias & Modelos de IA"

        msg.attach(MIMEText(conteudo_markdown, 'plain', 'utf-8'))

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender, password)
                server.send_message(msg)
            print("✅ E-mail enviado com sucesso!\n")
        except Exception as e:
            print(f"❌ Erro ao enviar e-mail: {e}\n")

    def executar(self):
        noticias_brutas = self.buscar_novidades()
        if not noticias_brutas:
            print("Nenhuma notícia encontrada.")
            return

        prompt = f"""
        Você é um agente especialista em Inteligência Artificial.
        Analise o feed de notícias abaixo, traduza os pontos principais para o Português
        e gere um resumo executivo bem formatado em Markdown com os links originais:

        {noticias_brutas}
        """

        modelo = "gemini-3.8-flash"
        max_tentativas = 8  # Aumentamos para 8 tentativas
        tempo_espera = 15   # Inicia esperando 15 segundos

        print(f"🤖 [{self.nome}]: Gerando resumo executivo via Gemini ({modelo})...\n")

        for tentativa in range(1, max_tentativas + 1):
            try:
                chat = self.client.chats.create(model=modelo)
                response = chat.send_message(prompt)

                resumo = response.text
                print("=== RESUMO DAS NOTÍCIAS ===")
                print(resumo)
                print("===========================\n")

                self.enviar_email(resumo)
                return

            except Exception as e:
                erro_str = str(e)
                if "503" in erro_str or "UNAVAILABLE" in erro_str:
                    print(f"⚠️ Servidor sobrecarregado (503). Tentativa {tentativa}/{max_tentativas}. Aguardando {tempo_espera}s...")
                    time.sleep(tempo_espera)
                    # Limita a espera máxima por ciclo a 45s
                    tempo_espera = min(tempo_espera + 10, 45)
                else:
                    print(f"❌ Erro na chamada da API: {e}")
                    break

        print("\n❌ Não foi possível gerar e enviar o resumo no momento.")

if __name__ == "__main__":
    agente = AgenteNoticiasIA()
    agente.executar()