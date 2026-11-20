#!/usr/bin/env python3
"""legonotice : modèle LDraw (.mpd/.ldr) -> notice de montage HTML autonome (WebGL), étape par étape.

Le modèle vient soit d'un fichier (--model), soit du dépôt officiel de modèles LDraw (OMR) avec --set 1069-1.
Les formes des pièces viennent de la bibliothèque LDraw (complete.zip, téléchargée une fois dans le cache).
Le fichier produit est autonome : ouvrez-le dans un navigateur (flèches gauche/droite = étape, souris = rotation, molette = zoom).
Pièces repérées « imprimable » : celles que legoprint.py sait générer (Brick/Plate/Tile N x M).
Usage : python3 legonotice.py --set 1069-1 --out notice.html
        python3 legonotice.py --model mon_modele.mpd --ldraw complete.zip --out notice.html
"""
import argparse, base64, concurrent.futures as cf, glob, gzip, json, math, os, re, shutil, subprocess, sys, urllib.request, zipfile
import numpy as np
import legoset as S

LIB_URL = 'https://library.ldraw.org/library/updates/complete.zip'
OMR = 'https://library.ldraw.org/omr/sets'
UA = {'User-Agent': 'legokit/0.1'}

# ---------------------------------------------------------------- réseau / cache
def fetch(url, dest=None):
    req = urllib.request.Request(url, headers=UA)
    if dest is None:
        return urllib.request.urlopen(req, timeout=120).read()
    with urllib.request.urlopen(req, timeout=600) as r, open(dest + '.part', 'wb') as f:
        while chunk := r.read(1 << 20): f.write(chunk)
    os.replace(dest + '.part', dest)

def omr_index(cache):
    path = os.path.join(cache, 'omr_index.json')
    if not os.path.exists(path):
        print('construction de l\'index OMR (une fois) ...', file=sys.stderr)
        def page(p):
            h = fetch(f'{OMR}?page={p}').decode('utf-8', 'ignore')
            return re.findall(r'table\.record\.(\d+)\.column\.number".*?fi-ta-text-item[^>]*>\s*([^<]+?)\s*</div>', h, re.S)
        idx = {}
        with cf.ThreadPoolExecutor(6) as ex:
            for p, res in zip(range(1, 200), ex.map(page, range(1, 200))):
                if not res: break
                idx.update({num.strip(): pid for pid, num in res})
        json.dump(idx, open(path, 'w'))
    return json.load(open(path))

def omr_model(cache, set_num):
    idx = omr_index(cache)
    q = set_num if '-' in set_num else set_num + '-1'
    if q not in idx:
        raise SystemExit(f'{q} n\'est pas dans le dépôt officiel LDraw (OMR). Fournissez un fichier avec --model (.mpd/.ldr).')
    h = fetch(f'{OMR}/{idx[q]}').decode('utf-8', 'ignore')
    links = [l for l in re.findall(r'https://library\.ldraw\.org/media/omr_models/\d+/[^"\'<>\s]+', h)
             if re.search(r'\.(mpd|ldr)\b', l) and 'conversions' not in l]
    if not links: raise SystemExit(f'aucun fichier .mpd/.ldr pour {q} dans l\'OMR')
    return fetch(links[0].replace('&amp;', '&')).decode('utf-8', 'ignore')

# ---------------------------------------------------------------- bibliothèque LDraw
class Library:
    def __init__(self, path):
        self.z = None
        if os.path.isdir(path):
            root = path if os.path.isdir(os.path.join(path, 'parts')) else os.path.join(path, 'ldraw')
            self.files = {os.path.relpath(os.path.join(d, f), root).replace(os.sep, '/').lower(): os.path.join(d, f)
                          for d, _, fs in os.walk(root) for f in fs}
        else:
            self.z = zipfile.ZipFile(path)
            self.files = {n[6:].lower(): n for n in self.z.namelist() if n.lower().startswith('ldraw/') and not n.endswith('/')}
        self.memo, self.colors, self.over = {}, {}, {}
        if 'ldconfig.ldr' in self.files:
            for l in self.read('ldconfig.ldr').splitlines():
                m = re.search(r'!COLOUR\s+\S+\s+CODE\s+(\d+)\s+VALUE\s+#([0-9A-Fa-f]{6})(?:.*ALPHA\s+(\d+))?', l)
                if m: self.colors[int(m.group(1))] = (tuple(int(m.group(2)[i:i+2], 16) / 255 for i in (0, 2, 4)), int(m.group(3) or 255) / 255)

    def add_custom(self, name, lines):
        """Pièce/primitive définie dans le MPD lui-même (0 FILE parts/xxx.dat)."""
        text = '\n'.join(' '.join(t) for t in lines)
        for k in {name, re.sub(r'^(parts|p)/', '', name)}: self.over['ov:' + k] = text

    def read(self, key):
        if key.startswith('ov:'): return self.over[key]
        n = self.files[key]
        raw = self.z.read(n) if self.z else open(n, 'rb').read()
        return raw.decode('utf-8', 'ignore')

    def find(self, ref):
        r = ref.replace('\\', '/').lower().strip()
        if 'ov:' + r in self.over: return 'ov:' + r
        for pre in ('parts/', 'p/', 'models/', ''):
            if pre + r in self.files: return pre + r
        return None

    def color(self, code):
        if code in self.colors: return self.colors[code]
        if code >= 0x2000000: return (tuple(((code >> s) & 255) / 255 for s in (16, 8, 0)), 1.0)
        return ((0.55, 0.55, 0.55), 1.0)

    def name(self, ref):
        k = self.find(ref)
        if not k: return ref
        for l in self.read(k).splitlines():
            if l.startswith('0 '): return re.sub(r'\s+', ' ', l[2:]).lstrip('~=_').strip()
        return ref

    def flat(self, ref):
        """Pièce aplatie en coordonnées locales : (triangles (n,3,3), codes couleur (n,), segments (m,2,3))."""
        k = self.find(ref)
        if k in self.memo: return self.memo[k]
        T, C, L = [], [], []
        if k is None:
            self.memo[k] = (np.zeros((0, 3, 3)), np.zeros(0, int), np.zeros((0, 2, 3))); return self.memo[k]
        self.memo[k] = (np.zeros((0, 3, 3)), np.zeros(0, int), np.zeros((0, 2, 3)))      # garde-fou contre les boucles
        for line in self.read(k).splitlines():
            t = line.split()
            if not t: continue
            try:
                if t[0] == '1' and len(t) >= 15:
                    col = int(t[1]); v = [float(x) for x in t[2:14]]
                    M = np.array(v[3:12]).reshape(3, 3); o = np.array(v[0:3])
                    st, sc, sl = self.flat(' '.join(t[14:]))
                    if len(st): T.append(st @ M.T + o); C.append(np.where(sc == 16, col, sc))
                    if len(sl): L.append(sl @ M.T + o)
                elif t[0] in ('3', '4'):
                    n = 3 if t[0] == '3' else 4
                    p = np.array([float(x) for x in t[2:2 + 3 * n]]).reshape(n, 3)
                    tris = [p[[0, 1, 2]]] + ([p[[0, 2, 3]]] if n == 4 else [])
                    T.append(np.array(tris)); C.append(np.full(len(tris), int(t[1])))
                elif t[0] == '2':
                    L.append(np.array([float(x) for x in t[2:8]]).reshape(1, 2, 3))
            except (ValueError, IndexError):
                continue
        res = (np.concatenate(T) if T else np.zeros((0, 3, 3)), np.concatenate(C) if C else np.zeros(0, int),
               np.concatenate(L) if L else np.zeros((0, 2, 3)))
        self.memo[k] = res
        return res

# ---------------------------------------------------------------- modèle : fichiers, sous-modèles, étapes
def parse_model(text):
    models, cur, first = {}, None, None
    for line in text.splitlines():
        t = line.split()
        if not t: continue
        if t[0] == '0' and len(t) > 2 and t[1] == 'FILE':
            cur = ' '.join(t[2:]).replace('\\', '/').lower(); models[cur] = []; first = first or cur
        elif cur is None:
            cur = 'main'; models[cur] = []; first = cur; models[cur].append(t)
        else:
            models[cur].append(t)
    custom = {n: L for n, L in models.items() if any(t[:2] == ['0', '!LDRAW_ORG'] and len(t) > 2 and
              re.search(r'part|primitive|shortcut', t[2], re.I) for t in L)}
    return {n: L for n, L in models.items() if n not in custom}, first, custom

def expand(models, name, M, col, steps, depth=0):
    """Remplit `steps` (liste d'étapes, chacune une liste de (pièce, matrice 4x4, couleur)). Les étapes d'un sous-modèle
    viennent avant l'étape du parent qui le pose ; les sous-modèles sans STEP forment une seule étape."""
    cur = []
    for t in models[name]:
        if t[0] == '0' and len(t) > 1 and t[1] in ('STEP', 'ROTSTEP'):
            if cur: steps.append(cur); cur = []
        elif t[0] == '1' and len(t) >= 15:
            try:
                v = [float(x) for x in t[2:14]]; c = int(t[1])
            except ValueError:
                continue
            A = np.eye(4); A[:3, :3] = np.array(v[3:12]).reshape(3, 3); A[:3, 3] = v[0:3]
            ref = ' '.join(t[14:]).replace('\\', '/').lower()
            Mc, cc = M @ A, (col if c == 16 else c)
            if ref in models and depth < 30: expand(models, ref, Mc, cc, steps, depth + 1)
            else: cur.append((ref, Mc, cc))
    if cur: steps.append(cur)

# ---------------------------------------------------------------- export
def build(models, first, lib, title=''):
    steps = []
    expand(models, first, np.eye(4), 15, steps)
    refs = sorted({p[0] for s in steps for p in s})
    refs = [r for r in refs if lib.find(r)]
    midx = {r: i for i, r in enumerate(refs)}
    meta, tri_b, line_b, col_b, bb = [], [], [], [], {}
    for r in refs:
        T, C, L = lib.flat(r)
        pos = T.reshape(-1, 3).astype('<f4')
        cols = np.zeros((len(C), 3, 4), np.uint8)
        for code in np.unique(C):
            if code in (16, 24): rgb, inh = (0, 0, 0), 255
            else: rgb, inh = tuple(int(255 * x) for x in lib.color(int(code))[0]), 0
            cols[C == code] = (*rgb, inh)
        tri_b.append(pos.tobytes()); line_b.append(L.reshape(-1, 3).astype('<f4').tobytes()); col_b.append(cols.reshape(-1, 4).tobytes())
        meta.append({'name': r, 'nv': len(pos), 'nl': len(L) * 2})
        bb[r] = (pos.min(0), pos.max(0)) if len(pos) else (np.zeros(3), np.zeros(3))
    blob = b''.join(tri_b[i] + line_b[i] + col_b[i] for i in range(len(refs)))
    inst, lo, hi, st, fit = [], np.full(3, 1e9), np.full(3, -1e9), [], []
    for si, parts in enumerate(steps):
        agg = {}
        for ref, M, c in parts:
            if ref not in midx: continue
            rgb, a = lib.color(c)
            inst.append([midx[ref], si, *[round(x, 3) for x in rgb], round(a, 3), *[round(float(x), 4) for x in M[:3].T.reshape(-1)]])
            l, h = bb[ref]
            corners = np.array([[x, y, z, 1] for x in (l[0], h[0]) for y in (l[1], h[1]) for z in (l[2], h[2])]) @ M.T
            lo, hi = np.minimum(lo, corners[:, :3].min(0)), np.maximum(hi, corners[:, :3].max(0))
            key = (ref, c); agg[key] = agg.get(key, 0) + 1
        rows = []
        for (ref, c), q in sorted(agg.items(), key=lambda kv: (-kv[1], kv[0])):
            nm = lib.name(ref); rgb, a = lib.color(c)
            rows.append([ref[:-4] if ref.endswith('.dat') else ref, nm, [round(x, 3) for x in rgb], q, 1 if S.classify(nm) else 0])
        st.append(rows)
        c0 = (lo + hi) / 2 if len(inst) else np.zeros(3)
        fit.append([*c0.round(2).tolist(), round(float(np.linalg.norm(hi - lo) / 2), 2) if len(inst) else 1])
    if not inst: raise SystemExit('aucune pièce trouvée (bibliothèque LDraw incomplète ?)')
    c = (lo + hi) / 2
    return {'title': title, 'fit': fit, 'meshes': meta, 'inst': inst, 'steps': st, 'center': c.round(2).tolist(),
            'radius': round(float(np.linalg.norm(hi - lo) / 2), 2),
            'blob': base64.b64encode(gzip.compress(blob, 6)).decode()}, len(steps), len(inst)

HTML = r'''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ — notice</title>
<style>
 html,body{margin:0;height:100%;font:15px system-ui,sans-serif;background:#f4f4f2;color:#222}
 #app{display:grid;grid-template-columns:1fr 300px;grid-template-rows:auto 1fr;height:100%}
 header{grid-column:1/3;display:flex;gap:12px;align-items:center;padding:8px 14px;background:#fff;border-bottom:1px solid #ddd}
 header h1{font-size:16px;margin:0;flex:0 1 auto;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 button{font:inherit;padding:6px 14px;border:1px solid #bbb;border-radius:6px;background:#fff;cursor:pointer}
 button:hover{background:#eee} input[type=range]{flex:1;min-width:80px}
 canvas{width:100%;height:100%;display:block;touch-action:none;cursor:grab}
 aside{background:#fff;border-left:1px solid #ddd;overflow:auto;padding:12px}
 aside h2{font-size:14px;margin:0 0 8px} .p{display:flex;gap:8px;align-items:center;padding:5px 0;border-bottom:1px solid #eee;font-size:13px}
 .sw{width:18px;height:18px;border-radius:4px;border:1px solid #0004;flex:none} .q{font-weight:700;min-width:28px}
 .tag{font-size:11px;background:#e6f4ea;color:#1b6b2e;border-radius:4px;padding:1px 5px;margin-left:auto;white-space:nowrap}
 label{font-size:13px;white-space:nowrap}
 #printroot{display:none;background:#fff}
 body.print #app{display:none} body.print #printroot{display:block}
 .blk{display:grid;grid-template-columns:1fr 58mm;gap:6mm;height:132mm;box-sizing:border-box;padding:3mm 0;border-bottom:.3mm solid #ccc;break-inside:avoid;-webkit-print-color-adjust:exact;print-color-adjust:exact}
 .blk .hd{font-size:11pt;margin-bottom:2mm}.blk img{width:100%;max-height:112mm;object-fit:contain;border:.3mm solid #ddd;background:#f4f4f2}
 .blk .pl{overflow:hidden}.blk .p{font-size:8.5pt;padding:1.2mm 0}.blk .sw{width:4mm;height:4mm}
 @page{size:A4;margin:10mm}
 @media print{#app{display:none!important}#printroot{display:block}html,body{background:#fff;height:auto}}
 @media (max-width:760px){#app{grid-template-columns:1fr;grid-template-rows:auto 1fr 200px}header{grid-column:1}aside{border-left:0;border-top:1px solid #ddd}}
</style>
<div id="app"><header><h1>__TITLE__</h1><button id="prev">◀</button><input id="sl" type="range" min="1" value="1"><button id="next">▶</button>
 <b id="lab"></b><button id="pdf" title="Ouvre l'impression du navigateur : choisissez « Enregistrer au format PDF »">PDF</button><label><input id="dim" type="checkbox" checked> atténuer les précédentes</label><label><input id="fit" type="checkbox"> cadrage auto</label></header>
 <canvas id="c"></canvas><aside><h2>Pièces de cette étape</h2><div id="parts"></div></aside></div><div id="printroot"></div>
<script>
const D = __DATA__;
async function inflate(b64){const bin=atob(b64),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
 return await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();}
const mul=(a,b)=>{const o=new Float32Array(16);for(let i=0;i<4;i++)for(let j=0;j<4;j++){let s=0;for(let k=0;k<4;k++)s+=a[k*4+j]*b[i*4+k];o[i*4+j]=s}return o};
const rotX=a=>{const c=Math.cos(a),s=Math.sin(a);return new Float32Array([1,0,0,0,0,c,s,0,0,-s,c,0,0,0,0,1])};
const rotY=a=>{const c=Math.cos(a),s=Math.sin(a);return new Float32Array([c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1])};
const trans=(x,y,z)=>new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,x,y,z,1]);
const scl=(x,y,z)=>new Float32Array([x,0,0,0,0,y,0,0,0,0,z,0,0,0,0,1]);
const ortho=(w,h,f)=>new Float32Array([1/w,0,0,0,0,1/h,0,0,0,0,-1/f,0,0,0,0,1]);
(async()=>{
const buf=await inflate(D.blob), cv=document.getElementById('c'), gl=cv.getContext('webgl2',{antialias:true});
if(!gl){document.body.innerHTML='<p style="padding:20px">WebGL2 est requis (navigateur récent).</p>';return}
const prog=(vs,fs)=>{const p=gl.createProgram();for(const [t,s] of [[gl.VERTEX_SHADER,vs],[gl.FRAGMENT_SHADER,fs]]){const h=gl.createShader(t);gl.shaderSource(h,s);gl.compileShader(h);
 if(!gl.getShaderParameter(h,gl.COMPILE_STATUS))throw gl.getShaderInfoLog(h);gl.attachShader(p,h)}gl.linkProgram(p);return p};
const P1=prog(`#version 300 es
in vec3 aPos;in vec4 aCol;uniform mat4 uV,uP,uM;uniform vec4 uColor;uniform float uDim;out vec3 vPos;out vec4 vCol;
void main(){vec4 p=uV*uM*vec4(aPos,1.);vPos=p.xyz;gl_Position=uP*p;vec3 c=aCol.a>.5?uColor.rgb:aCol.rgb;c=mix(c,vec3(.88),uDim);vCol=vec4(c,aCol.a>.5?uColor.a:1.);}`,
`#version 300 es
precision highp float;in vec3 vPos;in vec4 vCol;out vec4 o;
void main(){vec3 n=normalize(cross(dFdx(vPos),dFdy(vPos)));float l=.5+.5*abs(dot(n,normalize(vec3(.35,.55,.75))));o=vec4(vCol.rgb*l,vCol.a);}`);
const P2=prog(`#version 300 es
in vec3 aPos;uniform mat4 uV,uP,uM;void main(){gl_Position=uP*uV*uM*vec4(aPos,1.);}`,
`#version 300 es
precision mediump float;uniform vec4 uC;out vec4 o;void main(){o=uC;}`);
const U=(p,n)=>gl.getUniformLocation(p,n);
const meshes=[];let off=0;
for(const m of D.meshes){
 const tp=new Float32Array(buf,off,m.nv*3);off+=m.nv*12;const lp=new Float32Array(buf,off,m.nl*3);off+=m.nl*12;const tc=new Uint8Array(buf,off,m.nv*4);off+=m.nv*4;
 const mk=(pr,arrs)=>{const v=gl.createVertexArray();gl.bindVertexArray(v);arrs.forEach(([name,data,size,type,norm])=>{const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);
  const l=gl.getAttribLocation(pr,name);gl.enableVertexAttribArray(l);gl.vertexAttribPointer(l,size,type,norm,0,0)});return v};
 meshes.push({nv:m.nv,nl:m.nl,tv:m.nv?mk(P1,[['aPos',tp,3,gl.FLOAT,false],['aCol',tc,4,gl.UNSIGNED_BYTE,true]]):null,lv:m.nl?mk(P2,[['aPos',lp,3,gl.FLOAT,false]]):null});
}
const I=D.inst.map(r=>({m:r[0],s:r[1],c:[r[2],r[3],r[4],r[5]],M:new Float32Array([r[6],r[7],r[8],0,r[9],r[10],r[11],0,r[12],r[13],r[14],0,r[15],r[16],r[17],1])}));
const N=D.steps.length;let step=N-1,yaw=-0.6,pitch=0.55,zoom=1,dirty=true;
const sl=document.getElementById('sl');sl.max=N;
const esc=t=>String(t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const partsHtml=s=>D.steps[s].map(p=>`<div class="p"><span class="sw" style="background:rgb(${p[2].map(x=>Math.round(x*255))})"></span><span class="q">${p[3]}×</span><span>${esc(p[0])}<br><small>${esc(p[1])}</small></span>${p[4]?'<span class="tag">imprimable</span>':''}</div>`).join('');
function ui(){sl.value=step+1;document.getElementById('lab').textContent=`Étape ${step+1} / ${N}`;document.getElementById('parts').innerHTML=partsHtml(step);dirty=true}
function draw(W,H,pr){dirty=false;const dpr=devicePixelRatio||1,w=W||cv.clientWidth*dpr|0,h=H||cv.clientHeight*dpr|0;if(cv.width!==w||cv.height!==h){cv.width=w;cv.height=h}
 gl.viewport(0,0,w,h);gl.clearColor(.957,.957,.949,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);
 const F=(pr||document.getElementById('fit').checked)?D.fit[step]:null,R=F?F[3]:D.radius,c=F?F:D.center,asp=w/h,hh=R*1.15/(pr?1:zoom);
 const V=mul(mul(rotX(pitch),rotY(yaw)),mul(scl(1,-1,1),trans(-c[0],-c[1],-c[2]))),Pm=ortho(hh*asp,hh,R*3);
 const dim=document.getElementById('dim').checked;
 gl.useProgram(P1);gl.uniformMatrix4fv(U(P1,'uV'),false,V);gl.uniformMatrix4fv(U(P1,'uP'),false,Pm);
 gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
 for(const pass of [0,1]){gl.depthMask(pass===0);pass?gl.enable(gl.BLEND):gl.disable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
  for(const i of I){if(i.s>step||(i.c[3]<1)!==(pass===1))continue;const m=meshes[i.m];if(!m.tv)continue;gl.bindVertexArray(m.tv);
   gl.uniformMatrix4fv(U(P1,'uM'),false,i.M);gl.uniform4fv(U(P1,'uColor'),i.c);gl.uniform1f(U(P1,'uDim'),dim&&i.s<step?.55:0);gl.drawArrays(gl.TRIANGLES,0,m.nv)}}
 gl.depthMask(true);gl.disable(gl.BLEND);gl.disable(gl.POLYGON_OFFSET_FILL);
 gl.useProgram(P2);gl.uniformMatrix4fv(U(P2,'uV'),false,V);gl.uniformMatrix4fv(U(P2,'uP'),false,Pm);
 for(const i of I){if(i.s>step)continue;const m=meshes[i.m];if(!m.lv)continue;gl.bindVertexArray(m.lv);gl.uniformMatrix4fv(U(P2,'uM'),false,i.M);
  gl.uniform4f(U(P2,'uC'),0,0,0,dim&&i.s<step?.25:.8);gl.drawArrays(gl.LINES,0,m.nl)}}
const go=s=>{step=Math.max(0,Math.min(N-1,s));ui()};
document.getElementById('prev').onclick=()=>go(step-1);document.getElementById('next').onclick=()=>go(step+1);sl.oninput=()=>go(sl.value-1);
document.getElementById('dim').onchange=document.getElementById('fit').onchange=()=>dirty=true;
function buildPrint(){const keep=step;let h='';for(let s=0;s<N;s++){step=s;draw(900,675,true);
 h+=`<section class="blk"><div><div class="hd"><b>${esc(D.title)}</b> — étape ${s+1} / ${N}</div><img src="${cv.toDataURL('image/jpeg',.8)}"></div><div class="pl">${partsHtml(s)}</div></section>`}
 document.getElementById('printroot').innerHTML=h;step=keep;ui();window.__printReady=true}
document.getElementById('pdf').onclick=()=>{buildPrint();window.print()};
if(location.hash==='#print'){document.body.classList.add('print');buildPrint()}
addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(step+1);if(e.key==='ArrowLeft')go(step-1)});
let drag=null;cv.onpointerdown=e=>{drag=[e.clientX,e.clientY];cv.setPointerCapture(e.pointerId)};cv.onpointerup=()=>drag=null;
cv.onpointermove=e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.008;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];dirty=true};
cv.onwheel=e=>{e.preventDefault();zoom=Math.max(.3,Math.min(6,zoom*(e.deltaY<0?1.1:.91)));dirty=true};
addEventListener('resize',()=>dirty=true);
(function loop(){if(dirty)draw();requestAnimationFrame(loop)})();
ui();window.__ready=true;
})().catch(e=>{document.body.insertAdjacentHTML('afterbegin','<pre style="color:#b00;padding:12px">'+e+'</pre>')});
</script></html>'''

def write_notice(path, models, first, lib, title, custom=()):
    for n, L in dict(custom).items(): lib.add_custom(n, L)
    data, nsteps, ninst = build(models, first, lib, title)
    html = HTML.replace('__TITLE__', title.replace('<', '&lt;')).replace('__DATA__', json.dumps(data, separators=(',', ':')).replace('</', '<\\/'))
    open(path, 'w', encoding='utf-8').write(html)
    return nsteps, ninst, len(data['meshes']), os.path.getsize(path)

def get_library(arg, cache):
    path = arg or os.path.join(cache, 'ldraw_complete.zip')
    if not os.path.exists(path):
        print('téléchargement de la bibliothèque LDraw (~150 Mo, une fois) ...', file=sys.stderr)
        fetch(LIB_URL, path)
    return Library(path)

def find_chrome():
    cands = [os.environ.get('CHROME')] + [shutil.which(n) for n in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome', 'msedge')]
    cands += ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', '/opt/pw-browsers/chromium']
    cands += glob.glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome')
    return next((c for c in cands if c and os.path.isfile(c)), None)

def export_pdf(html_path, pdf_path):
    """PDF via Chrome/Chromium sans interface : la page dessine chaque étape (WebGL) puis le navigateur l'imprime."""
    chrome = find_chrome()
    if not chrome:
        raise SystemExit('Chrome/Chromium introuvable (variable CHROME pour l\'indiquer). Sinon ouvrez ' + html_path + ' et cliquez sur « PDF ».')
    url = 'file://' + os.path.abspath(html_path).replace(os.sep, '/') + '#print'
    cmd = [chrome, '--headless=new', '--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
           '--ignore-gpu-blocklist', '--no-pdf-header-footer', '--virtual-time-budget=300000', '--run-all-compositor-stages-before-draw',
           '--print-to-pdf=' + os.path.abspath(pdf_path), url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1000:
        raise SystemExit('échec de l\'export PDF :\n' + r.stderr[-600:])

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--set', help='numéro de set présent dans l\'OMR (ex. 1069-1)')
    g.add_argument('--model', help='fichier .mpd ou .ldr')
    ap.add_argument('--ldraw', help='complete.zip ou dossier ldraw/ local (sinon téléchargé dans le cache)')
    ap.add_argument('--cache'); ap.add_argument('--out', default='notice.html'); ap.add_argument('--title')
    ap.add_argument('--pdf', metavar='FICHIER.pdf', help='exporte aussi un PDF A4 (2 étapes par page) via Chrome/Chromium')
    a = ap.parse_args()
    cache = S.cache_dir(a.cache)
    text = omr_model(cache, a.set) if a.set else open(a.model, encoding='utf-8', errors='ignore').read()
    models, first, custom = parse_model(text)
    lib = get_library(a.ldraw, cache)
    title = a.title or (a.set or os.path.splitext(os.path.basename(a.model))[0])
    ns, ni, nm, size = write_notice(a.out, models, first, lib, title, custom)
    print(f'{a.out} : {ns} étapes, {ni} pièces posées, {nm} formes distinctes, {size // 1024} Ko')
    if a.pdf:
        if ns > 300: print(f'attention : {ns} étapes, le PDF sera volumineux et long à produire', file=sys.stderr)
        export_pdf(a.out, a.pdf); print(f'{a.pdf} : {os.path.getsize(a.pdf) // 1024} Ko')

if __name__ == '__main__':
    main()
