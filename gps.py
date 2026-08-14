import subprocess
import json
import shutil
import logging

logging.basicConfig(
    filename='logs/tracker.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_termux_api():
    """Verifica se o comando termux-location está disponível."""
    return shutil.which("termux-location") is not None

def get_location():
    """
    Obtém a localização via Termux:API.
    Retorna um dicionário com os dados ou None em caso de erro.
    """
    if not check_termux_api():
        msg = "Termux:API não encontrado. Instale com 'pkg install termux-api'."
        print(msg)
        logging.error(msg)
        return None

    try:
        # Usa o provedor 'gps' para garantir funcionamento offline.
        # Timeout de 20 segundos para evitar travamentos se o GPS demorar.
        result = subprocess.run(
            ["termux-location", "-p", "gps"],
            capture_output=True, text=True, timeout=20
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            msg = "Permissão de localização negada ou GPS indisponível."
            print(msg)
            logging.error(f"Termux API error: {result.stderr}")
            return None
            
        data = json.loads(result.stdout)
        
        # Validação básica
        if 'latitude' not in data or 'longitude' not in data:
            msg = "Dados GPS inválidos recebidos."
            print(msg)
            logging.error(f"Invalid data: {data}")
            return None
            
        # Em alguns casos o Termux:API retorna 0.0 se não conseguir o fix.
        if data['latitude'] == 0.0 and data['longitude'] == 0.0:
            msg = "Sinal GPS perdido (lat/lon = 0)."
            print(msg)
            return None

        return {
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'altitude': data.get('altitude', 0.0),
            'accuracy': data.get('accuracy', 0.0),
            'speed': data.get('speed', 0.0),
            'bearing': data.get('bearing', 0.0)
        }
        
    except subprocess.TimeoutExpired:
        msg = "Tempo esgotado ao tentar obter o sinal GPS."
        print(msg)
        logging.error(msg)
        return None
    except json.JSONDecodeError:
        msg = "Erro ao ler a resposta do Termux:API."
        print(msg)
        logging.error(msg)
        return None
    except Exception as e:
        msg = f"Erro inesperado no GPS: {e}"
        print(msg)
        logging.error(msg)
        return None
