import csv
import os
import json
from datetime import datetime
from config import EXPORT_DIR
from database import get_all_points, get_all_stays
import xml.etree.ElementTree as ET

def ensure_export_dir():
    """Garante que o diretório de exports existe."""
    os.makedirs(EXPORT_DIR, exist_ok=True)

def export_csv():
    points = get_all_points()
    if not points:
        print("Nenhum dado para exportar.")
        return

    ensure_export_dir()
    filename = os.path.join(EXPORT_DIR, f"pontos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Latitude', 'Longitude', 'Altitude', 'Precisao', 'Velocidade', 'Direcao', 'Timestamp'])
            for p in points:
                writer.writerow([p['id'], p['latitude'], p['longitude'], p['altitude'], p['accuracy'], p['speed'], p['bearing'], p['timestamp']])
        print(f"CSV exportado com sucesso: {filename}")
        return filename
    except Exception as e:
        print(f"Erro ao exportar CSV: {e}")
        return None

def export_gpx():
    points = get_all_points()
    if not points:
        print("Nenhum dado para exportar.")
        return

    ensure_export_dir()
    filename = os.path.join(EXPORT_DIR, f"percurso_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gpx")
    
    try:
        # Cria a estrutura XML do GPX
        gpx = ET.Element('gpx', version="1.1", creator="TermuxTracker", xmlns="http://www.topografix.com/GPX/1/1")
        trk = ET.SubElement(gpx, 'trk')
        trkseg = ET.SubElement(trk, 'trkseg')
        
        for p in points:
            trkpt = ET.SubElement(trkseg, 'trkpt', lat=str(p['latitude']), lon=str(p['longitude']))
            if p['altitude'] is not None:
                ele = ET.SubElement(trkpt, 'ele')
                ele.text = str(p['altitude'])
            time = ET.SubElement(trkpt, 'time')
            # Formato ISO 8601 para GPX
            dt = datetime.strptime(p['timestamp'], '%Y-%m-%d %H:%M:%S')
            time.text = dt.isoformat() + 'Z'
            
        # Indenta o XML e salva
        ET.indent(gpx, space="  ", level=0)
        tree = ET.ElementTree(gpx)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        print(f"GPX exportado com sucesso: {filename}")
        return filename
    except Exception as e:
        print(f"Erro ao exportar GPX: {e}")
        return None

def save_stay_file(lat, lon, arrival_time, departure_time, duration_minutes, point_count, stay_id):
    """
    Salva um arquivo JSON individual para cada permanência detectada.
    Facilita o envio compartilhando apenas arquivos específicos.
    """
    ensure_export_dir()
    
    # Nome do arquivo com data/hora de chegada para fácil identificação
    arrival_dt = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')
    filename = os.path.join(EXPORT_DIR, f"permanencia_{arrival_dt.strftime('%Y%m%d_%H%M%S')}.json")
    
    stay_data = {
        "id": stay_id,
        "tipo": "permanencia",
        "localizacao": {
            "latitude": lat,
            "longitude": lon,
            "google_maps": f"https://www.google.com/maps?q={lat},{lon}",
            "waze": f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
        },
        "chegada": arrival_time,
        "saida": departure_time,
        "duracao_minutos": round(duration_minutes, 2),
        "pontos_registrados": point_count,
        "exportado_em": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stay_data, f, indent=2, ensure_ascii=False)
        print(f"Permanência salva em: {filename}")
        return filename
    except Exception as e:
        print(f"Erro ao salvar arquivo de permanência: {e}")
        return None

def list_export_files():
    """Lista todos os arquivos exportados disponíveis para envio."""
    if not os.path.exists(EXPORT_DIR):
        print("Nenhum arquivo exportado encontrado.")
        return []
    
    files = []
    for f in sorted(os.listdir(EXPORT_DIR)):
        if f.endswith(('.csv', '.gpx', '.json')):
            filepath = os.path.join(EXPORT_DIR, f)
            size = os.path.getsize(filepath)
            files.append({'name': f, 'path': filepath, 'size': size})
            if f.startswith('permanencia_'):
                print(f"📍 {f} ({size} bytes) - Permanência")
            elif f.endswith('.gpx'):
                print(f"🛣️  {f} ({size} bytes) - Percurso GPX")
            elif f.endswith('.csv'):
                print(f"📊 {f} ({size} bytes) - Pontos CSV")
            else:
                print(f"📄 {f} ({size} bytes)")
    
    if not files:
        print("Nenhum arquivo encontrado.")
    
    return files

def get_latest_stay_file():
    """Retorna o caminho do arquivo de permanência mais recente."""
    if not os.path.exists(EXPORT_DIR):
        return None
    
    stay_files = [f for f in os.listdir(EXPORT_DIR) if f.startswith('permanencia_') and f.endswith('.json')]
    if not stay_files:
        return None
    
    latest = sorted(stay_files)[-1]
    return os.path.join(EXPORT_DIR, latest)
