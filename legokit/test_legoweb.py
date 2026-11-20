"""Tests hors ligne du serveur : python3 test_legoweb.py (jeu de données factice, aucun accès réseau)."""
import csv, gzip, http.client, json, os, tempfile, threading, time, zipfile
import legoweb as W, legoset as S
import test_legopart as TP

def gz(d, name, header, rows):
    with gzip.open(f'{d}/{name}.csv.gz', 'wt', newline='') as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)

def fixture(d):
    gz(d, 'colors', 'id,name,rgb,is_trans'.split(','), [(4, 'Red', 'C91A09', 'False'), (1, 'Blue', '0055BF', 'False')])
    gz(d, 'sets', 'set_num,name,year,num_parts,img_url'.split(','), [('7-1', 'Mini Test', 2021, 6, 'https://cdn.rebrickable.com/x.jpg')])
    gz(d, 'inventories', 'id,version,set_num'.split(','), [(1, 1, '7-1')])
    gz(d, 'inventory_parts', 'inventory_id,part_num,color_id,quantity,is_spare,img_url'.split(','),
       [(1, '3001', 4, 20, 'False', 'https://cdn.rebrickable.com/p.jpg'), (1, '3004', 4, 20, 'False', ''), (1, '3005', 4, 20, 'False', ''),
        (1, '9001', 1, 2, 'False', ''), (1, '5555', 1, 1, 'False', '')])
    gz(d, 'parts', 'part_num,name'.split(','), [('3001', 'Brick 2 x 4'), ('3004', 'Brick 1 x 2'), ('3005', 'Brick 1 x 1'), ('9001', 'Widget'), ('5555', 'Mystery Part')])
    gz(d, 'part_relationships', 'rel_type,child_part_num,parent_part_num'.split(','), [])

def call(port, method, path, body=None, headers=None):
    c = http.client.HTTPConnection('127.0.0.1', port, timeout=60)
    c.request(method, path, body=json.dumps(body) if isinstance(body, dict) else body, headers=headers or {})
    r = c.getresponse(); data = r.read(); return r.status, data

def wait(port, jid):
    for _ in range(300):
        st, data = call(port, 'GET', f'/api/job/{jid}'); j = json.loads(data)
        if j['status'] in ('done', 'error'): return j
        time.sleep(0.1)
    raise AssertionError('tâche trop longue')

def test_server_end_to_end():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(f'{d}/cache'); fixture(f'{d}/cache'); TP.make_lib(f'{d}/ld')
        for pn in ('3001', '3004', '3005'):                       # pièces de base nécessaires à la notice du modèle construit
            open(f'{d}/ld/parts/{pn}.dat', 'w').write('0 Brick\n0 BFC CERTIFY CCW\n' + TP.box_dat(20, 24, 20))
        srv = W.make_server('127.0.0.1', 0, cache=f'{d}/cache', workdir=f'{d}/work', ldraw=f'{d}/ld')
        port = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            st, html = call(port, 'GET', '/'); assert st == 200 and b'LegoKit' in html
            # validation des entrées
            assert call(port, 'POST', '/api/kit', {'set': '../etc'})[0] == 400
            assert call(port, 'POST', '/api/kit', {'set': '7', 'tol': 5})[0] == 400
            assert call(port, 'POST', '/api/notice?name=x.exe', b'0')[0] == 400
            # kit : 60 briques paramétriques + 2 pièces LDraw + 1 pièce introuvable
            st, data = call(port, 'POST', '/api/kit', {'set': '7', 'bed': [256, 256], 'tol': 0.1}); assert st == 200
            j = wait(port, json.loads(data)['job']); assert j['status'] == 'done', j
            r = j['result']; jid = json.loads(data)['job']
            assert r['set']['name'] == 'Mini Test' and r['coverage'] == dict(param=60, ldraw=2, total=63)
            assert [s['part'] for s in r['skipped']] == ['5555']
            assert {p['source'] for p in r['parts']} == {'paramétrique', 'LDraw', 'non imprimée'}
            assert len(r['plates']) == 2 and r['plates'][0]['pieces'] >= 1
            st, stl = call(port, 'GET', f"/files/{jid}/{r['plates'][0]['stl']}"); assert st == 200 and len(stl) > 84
            st, z = call(port, 'GET', f'/zip/{jid}'); assert st == 200
            open(f'{d}/k.zip', 'wb').write(z); assert any(n.endswith('.3mf') for n in zipfile.ZipFile(f'{d}/k.zip').namelist())
            # accès hors du dossier de la tâche
            assert call(port, 'GET', f'/files/{jid}/../../cache/colors.csv.gz')[0] == 404
            assert call(port, 'GET', f'/files/{jid}/%2e%2e/%2e%2e/cache/colors.csv.gz')[0] == 404
            assert call(port, 'GET', '/files/zzzzzzzzzzzz/x')[0] == 404
            # notice depuis un fichier envoyé ; le titre est échappé dans la page
            ldr = b'0 FILE a.ldr\n1 4 0 0 0 1 0 0 0 1 0 0 0 1 9001.dat\n0 STEP\n'
            st, data = call(port, 'POST', '/api/notice?name=<b>t</b>.ldr', ldr); assert st == 200
            jn = json.loads(data)['job']; j = wait(port, jn); assert j['status'] == 'done' and j['result']['steps'] == 1, j
            st, page = call(port, 'GET', f"/files/{jn}/{j['result']['notice']}"); assert st == 200 and b'<b>t</b>' not in page
            # modèle avec les pièces du set (briques rouges uniquement ici)
            st, data = call(port, 'POST', '/api/build', {'set': '7', 'shape': 'cylinder', 'width': 6, 'max_colors': 2})
            jb = json.loads(data)['job']; j = wait(port, jb); assert j['status'] == 'done', j
            assert j['result']['bricks'] > 0 and j['result']['kind'] == 'build'
            assert call(port, 'GET', f'/files/{jb}/build/modele.ldr')[0] == 200
            # erreur propre pour un set inconnu
            st, data = call(port, 'POST', '/api/kit', {'set': '999'}); j = wait(port, json.loads(data)['job'])
            assert j['status'] == 'error' and 'introuvable' in j['error']
        finally:
            srv.shutdown()

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
