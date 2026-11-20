#!/usr/bin/env python3
"""legoweb : application web locale (Python standard, aucune dépendance) autour de legokit.

Trois fonctions dans le navigateur :
  - Kit à imprimer : numéro de set -> plateaux 3MF/STL par couleur, aperçu 3D, liste de pièces avec photos, ZIP ;
  - Modèle avec les pièces du set : forme -> modèle LDraw + notice + kit, avec les seules pièces et couleurs du set ;
  - Notice de montage : set de l'OMR LDraw ou fichier .ldr/.mpd envoyé -> notice 3D étape par étape.
Usage : python3 legoweb.py            puis ouvrir http://127.0.0.1:8000
        python3 legoweb.py --port 9000 --ldraw complete.zip --cache ~/.cache/legokit
Le serveur n'écoute que sur cette machine par défaut (il télécharge et écrit des fichiers, pas d'authentification) :
ne l'exposez pas sur Internet tel quel.
"""
import argparse, json, os, re, shutil, sys, threading, time, traceback, uuid, zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse
import legoset as S, legoprint as P, legobuild as B, legonotice as N, legopreview as PV

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = dict(cache=None, workdir=None, ldraw=None)
JOBS, JOBS_LOCK, RUN_LOCK = {}, threading.Lock(), threading.Lock()
SET_RE = re.compile(r'^\d{1,8}(-\d{1,3})?$')
SHAPES = ('sphere', 'cone', 'cylinder', 'torus', 'pyramid')
MIME = {'.html': 'text/html; charset=utf-8', '.csv': 'text/csv; charset=utf-8', '.ldr': 'text/plain; charset=utf-8', '.png': 'image/png',
        '.pdf': 'application/pdf', '.zip': 'application/zip', '.stl': 'application/octet-stream', '.3mf': 'application/octet-stream'}
MAX_UPLOAD = 40 << 20
_LIB = {}

# ---------------------------------------------------------------- paramètres
def num(p, key, default, lo, hi, cast=float):
    try: v = cast(p.get(key, default))
    except (TypeError, ValueError): raise ValueError(f'{key} invalide')
    if not lo <= v <= hi: raise ValueError(f'{key} doit être entre {lo} et {hi}')
    return v

def clean(p):
    s = str(p.get('set', '')).strip()
    if not SET_RE.match(s): raise ValueError('numéro de set invalide (ex. 40468 ou 10698-1)')
    bx, by = (p.get('bed') or [256, 256])[:2]
    return dict(set=s, bed=(num({'b': bx}, 'b', 256, 100, 600), num({'b': by}, 'b', 256, 100, 600)), tol=num(p, 'tol', 0.1, 0, 0.5))

def library(job):
    path = CFG['ldraw'] or os.path.join(S.cache_dir(CFG['cache']), 'ldraw_complete.zip')
    if path not in _LIB:
        if not os.path.exists(path): job['log'].append('téléchargement de la bibliothèque LDraw (~150 Mo, une seule fois) ...')
        _LIB[path] = N.get_library(CFG['ldraw'], S.cache_dir(CFG['cache']))
    return _LIB[path]

def scan_plates(base, rel):
    """Plateaux STL/3MF sous base/<Couleur>/ -> liste pour l'interface."""
    out = []
    for color in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        d = os.path.join(base, color)
        if not os.path.isdir(d): continue
        for f in sorted(os.listdir(d)):
            if f.endswith('.stl'):
                rgb, n = PV.color_of(os.path.join(d, f[:-4] + '.3mf'))
                out.append(dict(color=color.replace('_', ' '), name=f[:-4].replace('_', ' '), rgb=[round(c, 3) for c in rgb], pieces=n,
                                stl=f'{rel}/{color}/{f}', mf3=f'{rel}/{color}/{f[:-4]}.3mf'))
    return out

# ---------------------------------------------------------------- tâches
def job_kit(job, p, jd):
    cache = S.cache_dir(CFG['cache']); s = S.find_set(cache, p['set'])
    if not s: raise ValueError(f"set {p['set']} introuvable dans Rebrickable")
    job['log'].append(f"{s['set_num']} {s['name']} ({s['year']})")
    inv = S.inventory(cache, s['set_num'])
    lib = library(job); rel = S.relations(cache)
    job['log'].append('génération des plateaux ...')
    res = P.print_kit(inv, f'{jd}/kit', p['bed'], p['tol'], lib=lib, relations=rel, quiet=True)
    skipped = {x[0] for x in res['skipped']}
    parts = [dict(couleur=r['couleur'], rgb=r['rgb'], part=r['part_num'], nom=r['nom'], quantite=r['quantite'], img=r.get('img', ''),
                  source='paramétrique' if r['imprimable'] == 'oui' else ('non imprimée' if r['part_num'] in skipped else 'LDraw')) for r in inv]
    total = sum(r['quantite'] for r in inv)
    return dict(kind='kit', set=dict(num=s['set_num'], name=s['name'], year=s['year'], img=s.get('img_url', ''), parts=total),
                coverage=dict(param=res['param'], ldraw=res['ldraw'], total=total),
                skipped=[dict(part=a, nom=b, quantite=c, raison=d) for a, b, c, d in res['skipped']],
                plates=scan_plates(f'{jd}/kit', 'kit'), bed=list(p['bed']), parts=parts)

def job_build(job, p, jd):
    shape = p.get('shape', 'sphere')
    if shape not in SHAPES: raise ValueError('forme inconnue')
    lib = library(job)                                                     # chargée avant : build() la redemande via get_library
    r = B.build(p['set'], f'{jd}/build', shape=shape, width=num(p, 'width', 40, 4, 60, int), max_colors=num(p, 'max_colors', 8, 0, 60, int),
                trans=bool(p.get('trans')), ldraw=CFG['ldraw'], cache=CFG['cache'], bed=p['bed'], tol=p['tol'], notice=True, kit=True,
                log=job['log'].append)
    r.update(kind='build', plates=scan_plates(f'{jd}/build/kit', 'build/kit'), bed=list(p['bed']), notice='build/notice.html')
    return r

def job_notice(job, p, jd):
    lib = library(job); cache = S.cache_dir(CFG['cache'])
    if p.get('text') is not None: text, title = p['text'], p.get('title') or 'modele'
    else:
        job['log'].append('recherche du modèle dans le dépôt officiel LDraw (OMR) ...')
        text, title = N.omr_model(cache, p['set']), p['set']
    models, first, custom = N.parse_model(text)
    os.makedirs(f'{jd}/notice', exist_ok=True)
    ns, ni, nm, size = N.write_notice(f'{jd}/notice/notice.html', models, first, lib, title, custom)
    job['log'].append(f'{ns} étapes, {ni} pièces posées')
    return dict(kind='notice', steps=ns, pieces=ni, shapes=nm, notice='notice/notice.html', title=title)

def start(fn, p):
    jid = uuid.uuid4().hex[:12]; jd = os.path.join(CFG['workdir'], jid); os.makedirs(jd)
    job = dict(id=jid, status='queued', log=['en file d\'attente ...'], result=None, error=None, created=time.time(), dir=jd)
    with JOBS_LOCK: JOBS[jid] = job
    def run():
        with RUN_LOCK:
            job['status'] = 'running'; job['log'] = []
            try: job['result'] = fn(job, p, jd); job['status'] = 'done'
            except BaseException as e:                                    # SystemExit des modules : message utile
                job['error'] = str(e.code if isinstance(e, SystemExit) and e.code else e) or e.__class__.__name__
                job['status'] = 'error'
                if not isinstance(e, (SystemExit, ValueError)): traceback.print_exc()
    threading.Thread(target=run, daemon=True).start()
    return jid

def purge(max_age=86400):
    now = time.time()
    for d in os.listdir(CFG['workdir']):
        full = os.path.join(CFG['workdir'], d)
        if os.path.isdir(full) and now - os.path.getmtime(full) > max_age: shutil.rmtree(full, ignore_errors=True)

# ---------------------------------------------------------------- HTTP
class H(BaseHTTPRequestHandler):
    server_version = 'legoweb'
    def log_message(self, fmt, *a): pass

    def send(self, code, body, ctype='application/json; charset=utf-8', extra=()):
        if isinstance(body, (dict, list)): body = json.dumps(body, ensure_ascii=False).encode()
        elif isinstance(body, str): body = body.encode()
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff'); self.send_header('Cache-Control', 'no-store')
        for k, v in extra: self.send_header(k, v)
        self.end_headers(); self.wfile.write(body)

    def job_dir(self, jid):
        if not re.fullmatch(r'[0-9a-f]{12}', jid or ''): return None
        d = os.path.join(CFG['workdir'], jid)
        return d if os.path.isdir(d) else None

    def do_GET(self):
        u = urlparse(self.path); path = unquote(u.path)
        if path in ('/', '/index.html'):
            return self.send(200, open(os.path.join(HERE, 'web', 'index.html'), 'rb').read(), 'text/html; charset=utf-8')
        if path == '/api/status':
            return self.send(200, dict(ldraw=bool(os.path.exists(CFG['ldraw'] or os.path.join(S.cache_dir(CFG['cache']), 'ldraw_complete.zip'))),
                                       chrome=bool(N.find_chrome()), version=1))
        m = re.fullmatch(r'/api/job/([0-9a-f]{12})', path)
        if m:
            j = JOBS.get(m.group(1))
            if not j: return self.send(404, dict(error='tâche inconnue'))
            return self.send(200, dict(status=j['status'], log=j['log'][-40:], result=j['result'], error=j['error']))
        m = re.fullmatch(r'/files/([0-9a-f]{12})/(.+)', path)
        if m:
            base = self.job_dir(m.group(1))
            if not base: return self.send(404, dict(error='introuvable'))
            full = os.path.realpath(os.path.join(base, m.group(2)))
            if not full.startswith(os.path.realpath(base) + os.sep) or not os.path.isfile(full): return self.send(404, dict(error='introuvable'))
            ext = os.path.splitext(full)[1].lower()
            extra = [('Content-Disposition', f'attachment; filename="{os.path.basename(full)}"')] if parse_qs(u.query).get('dl') else []
            return self.send(200, open(full, 'rb').read(), MIME.get(ext, 'application/octet-stream'), extra)
        m = re.fullmatch(r'/zip/([0-9a-f]{12})', path)
        if m:
            base = self.job_dir(m.group(1))
            if not base: return self.send(404, dict(error='introuvable'))
            tmp = os.path.join(CFG['workdir'], f'{m.group(1)}.zip.tmp')
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
                for d, _, fs in os.walk(base):
                    for f in fs: z.write(os.path.join(d, f), os.path.relpath(os.path.join(d, f), base))
            data = open(tmp, 'rb').read(); os.remove(tmp)
            return self.send(200, data, 'application/zip', [('Content-Disposition', f'attachment; filename="legokit_{m.group(1)}.zip"')])
        self.send(404, dict(error='introuvable'))

    def do_POST(self):
        u = urlparse(self.path); path = u.path
        n = int(self.headers.get('Content-Length') or 0)
        if n > MAX_UPLOAD: return self.send(413, dict(error='fichier trop gros (40 Mo max)'))
        raw = self.rfile.read(n)
        try:
            if path == '/api/notice' and parse_qs(u.query).get('name'):               # fichier .ldr/.mpd envoyé tel quel
                name = re.sub(r'[^\w.\- ]', '_', parse_qs(u.query)['name'][0])[:80]
                if not name.lower().endswith(('.ldr', '.mpd')): raise ValueError('seuls les fichiers .ldr et .mpd sont acceptés')
                return self.send(200, dict(job=start(job_notice, dict(text=raw.decode('utf-8', 'ignore'), title=os.path.splitext(name)[0]))))
            p = json.loads(raw or b'{}')
            if path == '/api/kit': return self.send(200, dict(job=start(job_kit, clean(p))))
            if path == '/api/build': q = clean(p); q.update(shape=p.get('shape', 'sphere'), width=p.get('width', 40),
                                                            max_colors=p.get('max_colors', 8), trans=p.get('trans')); return self.send(200, dict(job=start(job_build, q)))
            if path == '/api/notice':
                s = str(p.get('set', '')).strip()
                if not SET_RE.match(s): raise ValueError('numéro de set invalide')
                return self.send(200, dict(job=start(job_notice, dict(set=s))))
        except (ValueError, json.JSONDecodeError) as e:
            return self.send(400, dict(error=str(e)))
        self.send(404, dict(error='introuvable'))

def make_server(host='127.0.0.1', port=8000, cache=None, workdir=None, ldraw=None):
    CFG.update(cache=cache, ldraw=ldraw, workdir=workdir or os.path.join(S.cache_dir(cache), 'web'))
    os.makedirs(CFG['workdir'], exist_ok=True); purge()
    return ThreadingHTTPServer((host, port), H)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--host', default='127.0.0.1'); ap.add_argument('--port', type=int, default=8000)
    ap.add_argument('--cache'); ap.add_argument('--workdir'); ap.add_argument('--ldraw', help='complete.zip LDraw (sinon téléchargé dans le cache)')
    a = ap.parse_args()
    srv = make_server(a.host, a.port, a.cache, a.workdir, a.ldraw)
    print(f'legokit web : http://{a.host}:{a.port}  (Ctrl+C pour arrêter)')
    try: srv.serve_forever()
    except KeyboardInterrupt: pass

if __name__ == '__main__':
    main()
