#!/usr/bin/env python3
import os
import sys
import time
import signal
import math
from datetime import datetime, timedelta
from config import load_config, save_config, LOG_DIR
from database import init_db, insert_point, insert_stay, get_last_point, get_all_points, get_all_stays, get_stats
from gps import get_location, check_termux_api
from export import export_csv, export_gpx

PID_FILE = os.path.join(LOG_DIR, 'tracker.pid')

def haversine(lat1, lon1, lat2, lon2):
    """Calcula a distância em metros entre dois pontos GPS."""
    R = 6371000  # Raio da Terra em metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def is_running():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Verifica se o processo existe
            return True
        except (ProcessLookupError, ValueError, PermissionError):
            os.remove(PID_FILE)
    return False

def stop_tracker():
    if is_running():
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Rastreador (PID {pid}) interrompido com segurança.")
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
        except Exception as e:
            print(f"Erro ao parar: {e}")
    else:
        print("O rastreador não está rodando.")

def start_tracker():
    if is_running():
        print("O rastreador já está em execução.")
        return

    if not check_termux_api():
        print("Erro: Termux:API não está instalado.")
        return

    init_db()
    cfg = load_config()
    
    # Salva o PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    print(f"Iniciando rastreamento. Intervalo: {cfg['interval_seconds']}s. Pressione CTRL+C para parar.")
    
    # Variáveis de controle de permanência
    last_lat = None
    last_lon = None
    potential_stay_start = None
    stay_lat = None
    stay_lon = None
    stay_point_count = 0

    def safe_exit(signum=None, frame=None):
        print("\nEncerrando com segurança. Salvando dados...")
        if potential_stay_start and potential_stay_start < datetime.now() - timedelta(minutes=cfg['stay_duration_minutes']):
            insert_stay(stay_lat, stay_lon, potential_stay_start.strftime('%Y-%m-%d %H:%M:%S'), 
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                        (datetime.now() - potential_stay_start).total_seconds() / 60, stay_point_count)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        sys.exit(0)

    signal.signal(signal.SIGINT, safe_exit)
    signal.signal(signal.SIGTERM, safe_exit)

    while True:
        loc = get_location()
        
        if loc:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Local: {loc['latitude']:.5f}, {loc['longitude']:.5f} (Acc: {loc['accuracy']:.0f}m)")
            insert_point(loc['latitude'], loc['longitude'], loc['altitude'], loc['accuracy'], loc['speed'], loc['bearing'])
            
            # Lógica de Permanência (Stay Detection)
            if last_lat is not None:
                dist = haversine(last_lat, last_lon, loc['latitude'], loc['longitude'])
                
                if dist < cfg['jitter_radius_meters']:
                    # Está parado
                    if potential_stay_start is None:
                        potential_stay_start = datetime.now()
                        stay_lat = loc['latitude']
                        stay_lon = loc['longitude']
                        stay_point_count = 1
                    else:
                        stay_point_count += 1
                        
                    # Verifica se completou o tempo de permanência
                    if datetime.now() - potential_stay_start >= timedelta(minutes=cfg['stay_duration_minutes']):
                        # Ainda está parado, atualiza a saída mas não salva no BD ainda, 
                        # só salva quando sair do raio.
                        pass
                else:
                    # Movimentou-se
                    if potential_stay_start and (datetime.now() - potential_stay_start) >= timedelta(minutes=cfg['stay_duration_minutes']):
                        # Esteve parado o suficiente, salva a permanência
                        dep_time = datetime.now()
                        duration = (dep_time - potential_stay_start).total_seconds() / 60
                        insert_stay(stay_lat, stay_lon, potential_stay_start.strftime('%Y-%m-%d %H:%M:%S'),
                                    dep_time.strftime('%Y-%m-%d %H:%M:%S'), duration, stay_point_count)
                        print(f"Permanência registrada: {duration:.1f} min.")
                    
                    # Reseta a permanência
                    potential_stay_start = None
                    stay_point_count = 0

            last_lat = loc['latitude']
            last_lon = loc['longitude']
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Aguardando sinal GPS...")
        
        # ECONOMIA DE BATERIA: O sleep é respeitado rigorosamente
        time.sleep(cfg['interval_seconds'])

def show_status():
    last = get_last_point()
    if last:
        print(f"Último registro: {last['timestamp']}")
        print(f"Localização: {last['latitude']:.5f}, {last['longitude']:.5f}")
        print(f"Precisão: {last['accuracy']:.1f}m | Velocidade: {last['speed']:.1f}m/s")
    else:
        print("Nenhum registro encontrado.")

def show_history(limit=10):
    points = get_all_points()
    if not points:
        print("Sem histórico.")
        return
        
    print(f"\n--- Últimos {min(limit, len(points))} Registros ---")
    for p in points[-limit:]:
        print(f"{p['timestamp']} | Lat: {p['latitude']:.5f} | Lon: {p['longitude']:.5f} | Acc: {p['accuracy']:.0f}m")

def show_stats():
    stats = get_stats()
    print("\n=== ESTATÍSTICAS ===")
    print(f"Pontos registrados: {stats['total_points']}")
    print(f"Permanências detectadas: {stats['total_stays']}")
    print(f"Tempo total parado: {stats['total_stop_time']:.1f} minutos")
    
    if stats['total_points'] > 1:
        points = get_all_points()
        total_dist = 0
        for i in range(1, len(points)):
            d = haversine(points[i-1]['latitude'], points[i-1]['longitude'], points[i]['latitude'], points[i]['longitude'])
            # Ignora jitter para cálculo de distância total
            if d > 5: 
                total_dist += d
        
        first_dt = datetime.strptime(stats['first_point']['timestamp'], '%Y-%m-%d %H:%M:%S')
        last_dt = datetime.strptime(stats['last_point']['timestamp'], '%Y-%m-%d %H:%M:%S')
        total_time_min = (last_dt - first_dt).total_seconds() / 60
        moving_time = total_time_min - stats['total_stop_time']
        
        print(f"Distância total: {total_dist/1000:.2f} km")
        print(f"Tempo total em movimento: {moving_time:.1f} minutos")
        print(f"Primeira localização: {stats['first_point']['timestamp']}")
        print(f"Última localização: {stats['last_point']['timestamp']}")
    else:
        print("Dados insuficientes para calcular distância.")

def config_menu():
    cfg = load_config()
    print("\n--- CONFIGURAÇÕES ATUAIS ---")
    for k, v in cfg.items():
        print(f"{k}: {v}")
    
    print("\nDeseja alterar? (Deixe em branco para manter o atual)")
    
    try:
        interval = input(f"Intervalo de coleta (segundos) [{cfg['interval_seconds']}]: ")
        if interval: cfg['interval_seconds'] = int(interval)
        
        radius = input(f"Raio de permanência (metros) [{cfg['stay_radius_meters']}]: ")
        if radius: cfg['stay_radius_meters'] = int(radius)
        
        duration = input(f"Duração de permanência (minutos) [{cfg['stay_duration_minutes']}]: ")
        if duration: cfg['stay_duration_minutes'] = int(duration)
        
        jitter = input(f"Raio de oscilação (metros) [{cfg['jitter_radius_meters']}]: ")
        if jitter: cfg['jitter_radius_meters'] = int(jitter)
        
        save_config(cfg)
        print("Configurações salvas com sucesso!")
    except ValueError:
        print("Erro: Insira apenas números inteiros.")

def main():
    if len(sys.argv) < 2:
        print("Uso: python tracker.py [start|stop|status|history|stats|export|config]")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    
    if cmd == 'start':
        start_tracker()
    elif cmd == 'stop':
        stop_tracker()
    elif cmd == 'status':
        show_status()
    elif cmd == 'history':
        show_history()
    elif cmd == 'stats':
        show_stats()
    elif cmd == 'export':
        if len(sys.argv) > 2 and sys.argv[2] == 'gpx':
            export_gpx()
        elif len(sys.argv) > 2 and sys.argv[2] == 'csv':
            export_csv()
        else:
            print("Especifique o formato: python tracker.py export csv OU python tracker.py export gpx")
    elif cmd == 'config':
        config_menu()
    else:
        print("Comando não reconhecido.")

if __name__ == '__main__':
    main()
