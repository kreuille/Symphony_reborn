#!/usr/bin/env python3
"""legoset : numéro de set LEGO -> liste de pièces par couleur (données Rebrickable), avec repérage
des pièces simples (brique/plaque/tuile N x M) que legokit sait générer en STL imprimable.

Données : fichiers CSV publics de Rebrickable (https://rebrickable.com/downloads/), téléchargés une fois dans le cache.
Usage : python3 legoset.py 10698 --out set_10698/      (ou --search "classic large")
"""
import argparse, csv, gzip, os, re, sys, urllib.request
from collections import defaultdict

BASE = 'https://cdn.rebrickable.com/media/downloads/'
FILES = ['colors', 'sets', 'inventories', 'inventory_parts', 'parts']
SIMPLE = re.compile(r'^(Brick|Plate|Tile) (\d+) x (\d+)( with Groove)?$')       # pas de variante ni de motif ; "with Groove" = tuile standard
MAXDIM = 12

def cache_dir(arg):
    d = arg or os.environ.get('LEGOKIT_CACHE') or os.path.expanduser('~/.cache/legokit/rebrickable')
    os.makedirs(d, exist_ok=True); return d

def rows(cache, name):
    path = os.path.join(cache, name + '.csv.gz')
    if not os.path.exists(path):
        print(f'téléchargement de {name}.csv.gz ...', file=sys.stderr)
        urllib.request.urlretrieve(BASE + name + '.csv.gz', path + '.part'); os.replace(path + '.part', path)
    with gzip.open(path, 'rt', encoding='utf-8', newline='') as f:
        yield from csv.DictReader(f)

def find_set(cache, query):
    q = query.strip()
    if re.fullmatch(r'\d+', q): q += '-1'
    sets = {r['set_num']: r for r in rows(cache, 'sets') if r['set_num'] == q}
    return sets.get(q)

def classify(name):
    """-> (type, w, d) si pièce simple imprimable par legokit, sinon None."""
    m = SIMPLE.match(name)
    if not m: return None
    t, a, b = m.group(1), int(m.group(2)), int(m.group(3))
    return (t, min(a, b), max(a, b)) if max(a, b) <= MAXDIM else None

def inventory(cache, set_num, spares=False):
    inv = [r for r in rows(cache, 'inventories') if r['set_num'] == set_num]
    if not inv: raise SystemExit(f'pas d\'inventaire pour {set_num}')
    inv_id = max(inv, key=lambda r: int(r['version']))['id']
    colors = {r['id']: r for r in rows(cache, 'colors')}
    agg = defaultdict(int)
    for r in rows(cache, 'inventory_parts'):
        if r['inventory_id'] != inv_id or (r['is_spare'] == 'True' and not spares): continue
        agg[(r['color_id'], r['part_num'])] += int(r['quantity'])
    need = {p for _, p in agg}
    names = {r['part_num']: r['name'] for r in rows(cache, 'parts') if r['part_num'] in need}
    out = []
    for (cid, pn), q in agg.items():
        c = colors.get(cid, {'name': f'#{cid}', 'rgb': '808080', 'is_trans': 'False'})
        nm = names.get(pn, '?'); cl = classify(nm)
        out.append(dict(couleur=c['name'], color_id=int(cid) if cid.lstrip('-').isdigit() else -1, rgb=c['rgb'], transparent=c['is_trans'] == 'True', part_num=pn, nom=nm,
                        quantite=q, imprimable='oui' if cl else 'non',
                        type=cl[0] if cl else '', plots=f'{cl[1]}x{cl[2]}' if cl else ''))
    out.sort(key=lambda r: (r['couleur'], -r['quantite'], r['part_num']))
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('set', help='numéro de set (ex. 10698 ou 10698-1)')
    ap.add_argument('--out', default=None, help='dossier de sortie (défaut set_<numéro>/)')
    ap.add_argument('--cache', help='dossier des CSV Rebrickable')
    ap.add_argument('--spares', action='store_true', help='inclure les pièces de rechange')
    a = ap.parse_args()
    cache = cache_dir(a.cache)
    s = find_set(cache, a.set)
    if not s: raise SystemExit(f'set {a.set} introuvable')
    inv = inventory(cache, s['set_num'], a.spares)
    out = a.out or 'set_' + s['set_num']; os.makedirs(out, exist_ok=True)
    with open(f'{out}/pieces_par_couleur.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(inv[0])); w.writeheader(); w.writerows(inv)
    tot = sum(r['quantite'] for r in inv); ok = sum(r['quantite'] for r in inv if r['imprimable'] == 'oui')
    print(f"{s['set_num']} {s['name']} ({s['year']}) : {tot} pièces dans l'inventaire (annoncé : {s['num_parts']}), "
          f"{len({r['couleur'] for r in inv})} couleurs, {ok} pièces ({100*ok//max(tot,1)} %) générables par legokit")
    by = defaultdict(list)
    for r in inv: by[r['couleur']].append(r)
    for c, L in sorted(by.items(), key=lambda kv: -sum(r['quantite'] for r in kv[1])):
        print(f"\n{c} #{L[0]['rgb']}{' (transparent)' if L[0]['transparent'] else ''} : {sum(r['quantite'] for r in L)}")
        for r in L: print(f"  {r['quantite']:>4} x {r['part_num']:<10} {r['nom']}{'' if r['imprimable']=='oui' else '   [non géré]'}")

if __name__ == '__main__':
    main()
