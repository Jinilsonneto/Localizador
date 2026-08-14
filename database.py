import sqlite3
import os
from datetime import datetime
from config import DATA_DIR

DB_PATH = os.path.join(DATA_DIR, 'tracker.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Tabela de pontos GPS
    c.execute('''
        CREATE TABLE IF NOT EXISTS gps_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            accuracy REAL,
            speed REAL,
            bearing REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de permanências (stays)
    c.execute('''
        CREATE TABLE IF NOT EXISTS stays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            arrival_time DATETIME,
            departure_time DATETIME,
            duration_minutes REAL,
            point_count INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_point(lat, lon, alt, acc, speed, bearing):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO gps_points (latitude, longitude, altitude, accuracy, speed, bearing, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (lat, lon, alt, acc, speed, bearing, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro de banco de dados: {e}")

def insert_stay(lat, lon, arrival, departure, duration, count):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO stays (latitude, longitude, arrival_time, departure_time, duration_minutes, point_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (lat, lon, arrival, departure, duration, count))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao salvar permanência: {e}")

def get_last_point():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM gps_points ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    return row

def get_all_points():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM gps_points ORDER BY timestamp ASC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_stays():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM stays ORDER BY arrival_time ASC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_stats():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) as count FROM gps_points')
    total_points = c.fetchone()['count']
    
    c.execute('SELECT * FROM gps_points ORDER BY timestamp ASC LIMIT 1')
    first_point = c.fetchone()
    
    c.execute('SELECT * FROM gps_points ORDER BY timestamp DESC LIMIT 1')
    last_point = c.fetchone()
    
    c.execute('SELECT COUNT(*) as count, SUM(duration_minutes) as total_duration FROM stays')
    stay_data = c.fetchone()
    
    conn.close()
    return {
        'total_points': total_points,
        'first_point': first_point,
        'last_point': last_point,
        'total_stays': stay_data['count'],
        'total_stop_time': stay_data['total_duration'] if stay_data['total_duration'] else 0
    }
