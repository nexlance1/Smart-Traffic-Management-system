
import json, sqlite3, os, cv2, io
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd

STATE_FILE = 'signal_state.json'
DB_FILE = 'traffic_stats.db'

def ensure_state():
    if not os.path.exists(STATE_FILE):
        state = {'N':'GREEN','E':'RED','S':'GREEN','W':'RED','switch_count':0,'last_switch':None,'forced':None}
        with open(STATE_FILE,'w') as f: json.dump(state,f)

def read_state():
    ensure_state()
    with open(STATE_FILE,'r') as f: return json.load(f)

def write_state(state):
    with open(STATE_FILE,'w') as f: json.dump(state,f)

def set_direction_green(dir_name, duration=30):
    s = read_state()
    opposites = {'N':'S','S':'N','E':'W','W':'E'}
    for d in ['N','E','S','W']:
        s[d] = 'GREEN' if (d==dir_name or d==opposites.get(dir_name)) else 'RED'
    s['switch_count'] = s.get('switch_count',0) + 1
    s['last_switch'] = datetime.utcnow().isoformat()
    s['forced'] = dir_name
    write_state(s)

def reset_auto():
    s = read_state()
    s.update({'N':'GREEN','S':'GREEN','E':'RED','W':'RED','forced':None})
    s['last_switch'] = datetime.utcnow().isoformat()
    write_state(s)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats
                 (id INTEGER PRIMARY KEY, camera TEXT, timestamp TEXT, total_vehicles INTEGER, accidents INTEGER, ambulances INTEGER)''')
    conn.commit(); conn.close()

def log_stats(camera, total, accidents, ambulances):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO stats (camera,timestamp,total_vehicles,accidents,ambulances) VALUES (?,?,?, ?, ?)',
              (camera, datetime.utcnow().isoformat(), total, accidents, ambulances))
    conn.commit(); conn.close()

def aggregate_stats():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT * FROM stats', conn, parse_dates=['timestamp'])
    conn.close()
    if df.empty:
        return None
    df['ts'] = pd.to_datetime(df['timestamp']).dt.floor('T')
    agg = df.groupby('ts')[['total_vehicles','accidents','ambulances']].sum()
    return agg

def compute_co2_savings(total_vehicles, per_vehicle_saved_seconds=20):
    saved_seconds = total_vehicles * per_vehicle_saved_seconds
    liters_saved = saved_seconds * 0.0004
    co2_saved = liters_saved * 2.31
    return round(co2_saved,3), round(liters_saved,3), saved_seconds

def plot_metrics_image():
    agg = aggregate_stats()
    if agg is None or agg.empty:
        return None
    fig, ax = plt.subplots(2,1, figsize=(6,4))
    agg['total_vehicles'].plot(ax=ax[0], title='Total vehicles (all cameras)')
    agg['accidents'].plot(ax=ax[1], title='Accidents (all cameras)')
    plt.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=100); buf.seek(0)
    return Image.open(buf)

def draw_boxes(frame, boxes, state=None):
    for (x,y,w,h) in boxes:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
    h,w = frame.shape[:2]
    base_x, base_y = 20,20
    size = 18
    if state is None:
        state = {'N':'GREEN','E':'RED','S':'GREEN','W':'RED'}
    colors = {'GREEN':(0,200,0),'RED':(0,0,200)}
    cv2.putText(frame, 'Signals:', (base_x, base_y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),1)
    pos = {'N':(base_x, base_y), 'E':(base_x+60, base_y), 'S':(base_x+120, base_y), 'W':(base_x+180, base_y)}
    for d,(px,py) in pos.items():
        color = colors.get(state.get(d,'RED'), (0,0,200))
        cv2.circle(frame, (px,py), size//2, color, -1)
        cv2.putText(frame, d, (px-6, py+20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255),1)
    cv2.putText(frame, 'Smart Traffic', (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    return frame
