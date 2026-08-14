import csv
import os
from datetime import datetime
from config import EXPORT_DIR
from database import get_all_points, get_all_stays
import xml.etree.ElementTree as ET

def export_csv():
    points = get_all_points()
    if not points:
        print("Nenhum dado para exportar.")
        return

    filename = os.path.join(EXPORT_DIR, f"pontos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Latitude', 'Longitude', 'Altitude', 'Precisao', 'Velocidade', 'Direcao', 'Timestamp'])
            for p in points:
                writer.writerow([p['id'], p['latitude'], p['longitude'], p['altitude'], p['accuracy'], p['speed'], p['bearing'], p['timestamp']])
        print(f"CSV exportado com sucesso: {filename}")
    except Exception as e:
        print(f"Erro ao exportar CSV: {e}")

def export_gpx():
    points = get_all_points()
    if not points:
        print("Nenhum dado para exportar.")
        return

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
    except Exception as e:
        print(f"Erro ao exportar GPX: {e}")
