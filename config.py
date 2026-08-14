import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXPORT_DIR = os.path.join(BASE_DIR, 'exports')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

DEFAULT_CONFIG = {
    # ECONOMIA DE BATERIA: Altere estes valores para mudar o comportamento
    "interval_seconds": 60,      # Intervalo de coleta (60, 300, 600, etc.)
    "stay_radius_meters": 30,    # Raio para considerar "permanência"
    "stay_duration_minutes": 10, # Tempo mínimo parado para registrar permanência
    "jitter_radius_meters": 10   # Raio para ignorar oscilações normais do GPS
}

def ensure_dirs():
    for d in [DATA_DIR, EXPORT_DIR, LOG_DIR]:
        os.makedirs(d, exist_ok=True)

def load_config():
    ensure_dirs()
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, 'r') as f:
            cfg = json.load(f)
            # Merge with defaults to ensure new keys exist
            return {**DEFAULT_CONFIG, **cfg}
    except Exception:
        return DEFAULT_CONFIG

def save_config(cfg):
    ensure_dirs()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=4)
