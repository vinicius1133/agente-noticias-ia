import urllib.request
import xml.etree.ElementTree as ET

class AgenteNoticiasIA:
    def __init__(self):
        self.nome = "AI Trends Agent"
        # Feed RSS de notícias sobre Inteligência Artificial
        self.rss_url = "https://news.google.com/rss/search?q=Artificial+Intelligence+LLM+models&hl=en-US&gl=US&ceid=US:en"

    def buscar_novidades(self):
        print(f"🤖 [{self.nome}]: Buscando as últimas novidades sobre novos modelos de IA...\n")
        try:
            req = urllib.request.Request(self.rss_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            noticias = root.findall('./channel/item')[:5] # Pega os 5 primeiros resultados
            
            print("=== ÚLTIMAS ATUALIZAÇÕES SOBRE IA ===")
            for idx, item in enumerate(noticias, 1):
                titulo = item.find('title').text
                link = item.find('link').text
                print(f"\n{idx}. {titulo}")
                print(f"   🔗 Link: {link}")
                
        except Exception as e:
            print(f"Erro ao buscar novidades: {e}")

if __name__ == "__main__":
    agente = AgenteNoticiasIA()
    agente.buscar_novidades()