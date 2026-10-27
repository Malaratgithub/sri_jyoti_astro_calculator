"""Private localhost-only web app, no database or internet connection needed."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json
import sqlite3
import threading
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import Request, urlopen
from engine import calculate
from report_render import export
from marriage_report import export_marriage
ROOT = Path(__file__).parent
DB_PATH = ROOT / 'saved_birth_profiles.sqlite3'
DB_LOCK = threading.Lock()
FIELDS = ('name','date','time','place','latitude','longitude','timezone','ayanamsa','node')
def db_connect():
    conn=sqlite3.connect(DB_PATH,timeout=10)
    conn.execute('CREATE TABLE IF NOT EXISTS profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, details TEXT NOT NULL, updated_at TEXT NOT NULL)')
    return conn
def validate_profile(data):
    if not isinstance(data,dict):raise ValueError('Invalid profile')
    details={key:str(data.get(key,'')).strip() for key in FIELDS}
    if not details['name'] or len(details['name'])>120:raise ValueError('Enter a client name (up to 120 characters).')
    if any(len(details[x])>240 for x in FIELDS):raise ValueError('Field too long')
    for required in ('date','time','place','latitude','longitude','timezone'):
        if not details[required]:raise ValueError('Missing '+required)
    if not -90 <= float(details['latitude']) <= 90 or not -180 <= float(details['longitude']) <= 180:raise ValueError('Invalid coordinates')
    if details['ayanamsa'] not in ('lahiri','raman','krishnamurti') or details['node'] not in ('mean','true'):raise ValueError('Invalid calculation settings')
    return details

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/profiles':
            try:
                with DB_LOCK:
                    with db_connect() as db:
                        rows=db.execute('SELECT id, name, details, updated_at FROM profiles ORDER BY name COLLATE NOCASE, id').fetchall()
                self.json_response(200,{'ok':True,'profiles':[dict(id=r[0],name=r[1],details=json.loads(r[2]),updated_at=r[3]) for r in rows]})
            except Exception as exc:self.json_response(500,{'ok':False,'error':str(exc)})
            return
        if self.path.startswith('/api/places?'):
            try:
                q=parse_qs(urlparse(self.path).query).get('q',[''])[0].strip()
                if len(q)<3 or len(q)>120: raise ValueError('Type at least three letters for the birthplace.')
                uri='https://nominatim.openstreetmap.org/search?'+urlencode({'q':q,'format':'jsonv2','limit':8,'addressdetails':1})
                req=Request(uri,headers={'User-Agent':'SriJyotiAstroPrivateCalculator/1.6 (personal birth-location search)','Accept':'application/json'})
                with urlopen(req,timeout=12) as reply: places=json.load(reply)
                from timezonefinder import TimezoneFinder
                tf=TimezoneFinder(in_memory=True)
                result=[]
                for place in places:
                    lat=float(place['lat']);lon=float(place['lon'])
                    tz=tf.timezone_at(lat=lat,lng=lon)
                    if not tz:continue
                    result.append({'label':place['display_name'],'latitude':lat,'longitude':lon,'timezone':tz,'country':place.get('address',{}).get('country','')})
                self.json_response(200,{'ok':True,'places':result});return
            except Exception as exc:
                self.json_response(400,{'ok':False,'error':'Location lookup failed: '+str(exc)});return
        if self.path not in ('/','/index.html','/assets/master_header.png','/assets/master_footer.png','/porutham.html'):
            self.send_error(404); return
        data=(ROOT / ('index.html' if self.path in ('/','/index.html') else self.path.lstrip('/'))).read_bytes()
        mime='image/png' if self.path.endswith('.png') else 'text/html; charset=utf-8'
        self.send_response(200); self.send_header('Content-Type',mime); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(data))); self.end_headers();self.wfile.write(data)
    def json_response(self,status,data):
        blob=json.dumps(data).encode()
        self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(blob)));self.end_headers();self.wfile.write(blob)
    def do_POST(self):
        if self.path not in ('/api/calculate','/api/report','/api/marriage-report','/api/profiles/save','/api/profiles/delete'): self.send_error(404);return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0 < length < 200000: raise ValueError('Invalid input size')
            data=json.loads(self.rfile.read(length))
            if self.path == '/api/profiles/save':
                details=validate_profile(data.get('details'))
                profile_id=data.get('id')
                with DB_LOCK:
                    with db_connect() as db:
                        now=datetime.now(timezone.utc).isoformat()
                        if profile_id is not None:
                            cur=db.execute('UPDATE profiles SET name=?,details=?,updated_at=? WHERE id=?',(details['name'],json.dumps(details),now,int(profile_id)))
                            if cur.rowcount==0:raise ValueError('Saved profile was not found')
                            saved_id=int(profile_id)
                        else:
                            cur=db.execute('INSERT INTO profiles (name,details,updated_at) VALUES (?,?,?)',(details['name'],json.dumps(details),now))
                            saved_id=cur.lastrowid
                self.json_response(200,{'ok':True,'id':saved_id});return
            if self.path == '/api/profiles/delete':
                with DB_LOCK:
                    with db_connect() as db:
                        cur=db.execute('DELETE FROM profiles WHERE id=?',(int(data['id']),))
                        if cur.rowcount==0:raise ValueError('Saved profile not found')
                self.json_response(200,{'ok':True});return
            if self.path == '/api/marriage-report':
                fmt=data.get('format','pdf')
                if fmt not in ('pdf','png'):raise ValueError('Invalid report format')
                with DB_LOCK:
                    with db_connect() as db:
                        ids=[int(data.get('bride_id',0)),int(data.get('groom_id',0))]
                        if any(x<=0 for x in ids) or ids[0]==ids[1]:raise ValueError('Select two distinct saved birth profiles')
                        stored=[]
                        for pid in ids:
                            row=db.execute('SELECT name,details FROM profiles WHERE id=?',(pid,)).fetchone()
                            if row is None:raise ValueError('Saved birth profile not found')
                            stored.append({'name':row[0],'calculation':calculate(json.loads(row[1]))})
                checks=data.get('checks',[])
                if not isinstance(checks,list) or len(checks)!=10:raise ValueError('Calculate the ten Poruthams first')
                clean=[]
                for check in checks:
                    if check.get('status') not in ('Matches','Does not match','Review'):raise ValueError('Invalid Porutham status')
                    clean.append({k:str(check.get(k,''))[:350] for k in ('label','status','detail')})
                blob,mime,ext=export_marriage({'bride':stored[0],'groom':stored[1], 'checks':clean,'comments':data.get('comments',''),'asof':data.get('asof','')},fmt)
                self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Disposition',f'attachment; filename=Sri_Jyoti_Marriage_Matching.{ext}');self.send_header('Content-Length',str(len(blob)));self.end_headers();self.wfile.write(blob);return
            if self.path == '/api/report':
                fmt=data.get('format','png')
                if fmt not in ('png','pdf'):raise ValueError('Invalid report format')
                blob,mime,ext=export(data['calculation'],str(data.get('prediction',''))[:20000],fmt)
                self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Disposition',f'attachment; filename=Sri_Jyoti_Prediction_Report.{ext}');self.send_header('Content-Length',str(len(blob)));self.end_headers();self.wfile.write(blob);return
            result={'ok':True,'result':calculate(data)}
            status=200
        except Exception as exc:
            result={'ok':False,'error':str(exc)};status=400
        b=json.dumps(result).encode()
        self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
if __name__=='__main__':
    import webbrowser,threading
    url='http://127.0.0.1:8766'
    print('Sri Jyoti Astro Calculator: '+url+' (Ctrl+C to stop)',flush=True)
    threading.Timer(1,lambda:webbrowser.open(url)).start()
    ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
