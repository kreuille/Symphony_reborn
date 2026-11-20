#!/usr/bin/env python3
"""legopreview : images PNG des plateaux d'impression d'un kit (legoprint.py), en couleur, avec le plateau dessiné dessous.

Produit une image par plateau (plateau_<Couleur>_NN.png, vue de dessus inclinée) et une planche d'ensemble (apercu_plateaux.png).
Rendu : WebGL dans Chrome/Chromium/Edge sans interface (même navigateur que l'export PDF de legonotice.py ; variable CHROME).
Usage : python3 legopreview.py kit_40468/ --out apercus/        ou   python3 legoprint.py 40468 --preview
"""
import argparse, base64, glob, json, math, os, re, subprocess, sys, tempfile, zipfile
import numpy as np
import legokit as K, legonotice as N

HTML = r'''<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#fff}canvas{display:block}</style>
<body><script>
const D=__DATA__;
const f32=s=>{const b=atob(s),u=new Uint8Array(b.length);for(let i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return new Float32Array(u.buffer)};
const mul=(a,b)=>{const o=new Float32Array(16);for(let i=0;i<4;i++)for(let j=0;j<4;j++){let s=0;for(let k=0;k<4;k++)s+=a[k*4+j]*b[i*4+k];o[i*4+j]=s}return o};
const rotX=a=>{const c=Math.cos(a),s=Math.sin(a);return new Float32Array([1,0,0,0,0,c,s,0,0,-s,c,0,0,0,0,1])};
const rotZ=a=>{const c=Math.cos(a),s=Math.sin(a);return new Float32Array([c,s,0,0,-s,c,0,0,0,0,1,0,0,0,0,1])};
const trans=(x,y,z)=>new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,x,y,z,1]);
const ortho=(w,h,f)=>new Float32Array([1/w,0,0,0,0,1/h,0,0,0,0,-1/f,0,0,0,0,1]);
const mode=location.hash.slice(1)||'all';
const idx=mode==='all'?D.plates.map((_,i)=>i):[+mode];
const [TW,TH]=mode==='all'?D.tile:D.single, cols=mode==='all'?D.cols:1, rows=Math.ceil(idx.length/cols);
const out=document.createElement('canvas');out.width=TW*cols;out.height=TH*rows;document.body.appendChild(out);
const c2=out.getContext('2d');c2.fillStyle='#f4f4f2';c2.fillRect(0,0,out.width,out.height);
const cv=document.createElement('canvas');cv.width=TW;cv.height=TH;
const gl=cv.getContext('webgl2',{antialias:true});
const sh=(t,s)=>{const h=gl.createShader(t);gl.shaderSource(h,s);gl.compileShader(h);if(!gl.getShaderParameter(h,gl.COMPILE_STATUS))throw gl.getShaderInfoLog(h);return h};
const P=gl.createProgram();
gl.attachShader(P,sh(gl.VERTEX_SHADER,`#version 300 es
in vec3 aPos;uniform mat4 uV,uP;out vec3 vPos;void main(){vec4 p=uV*vec4(aPos,1.);vPos=p.xyz;gl_Position=uP*p;}`));
gl.attachShader(P,sh(gl.FRAGMENT_SHADER,`#version 300 es
precision highp float;in vec3 vPos;uniform vec3 uC;uniform float uFlat;out vec4 o;
void main(){vec3 n=normalize(cross(dFdx(vPos),dFdy(vPos)));float l=uFlat>.5?1.:.42+.58*abs(dot(n,normalize(vec3(.3,.55,.78))));o=vec4(uC*l,1.);}`));
gl.linkProgram(P);gl.useProgram(P);
const aPos=gl.getAttribLocation(P,'aPos'),U=n=>gl.getUniformLocation(P,n);
function upload(a){const v=gl.createVertexArray();gl.bindVertexArray(v);const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,a,gl.STATIC_DRAW);
 gl.enableVertexAttribArray(aPos);gl.vertexAttribPointer(aPos,3,gl.FLOAT,false,0,0);return v}
const [BX,BY]=D.bed;
const bed=upload(new Float32Array([0,0,-.2, BX,0,-.2, BX,BY,-.2, 0,0,-.2, BX,BY,-.2, 0,BY,-.2]));
idx.forEach((pi,k)=>{
 const pl=D.plates[pi],pos=f32(pl.pos);
 gl.viewport(0,0,TW,TH);gl.clearColor(.957,.957,.949,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);
 const t=(90-D.elev)*Math.PI/180,az=D.azim*Math.PI/180;
 const V=mul(mul(rotX(-t),rotZ(az)),trans(-pl.c[0],-pl.c[1],0));
 const R=Math.hypot(BX,BY)/2,asp=TW/TH,hh=pl.fit*.8,Pm=ortho(hh*asp,hh,R*4);
 gl.uniformMatrix4fv(U('uV'),false,V);gl.uniformMatrix4fv(U('uP'),false,Pm);
 gl.uniform3f(U('uC'),.86,.87,.85);gl.uniform1f(U('uFlat'),1);gl.bindVertexArray(bed);gl.drawArrays(gl.TRIANGLES,0,6);
 gl.uniform3fv(U('uC'),pl.rgb);gl.uniform1f(U('uFlat'),0);gl.bindVertexArray(upload(pos));gl.drawArrays(gl.TRIANGLES,0,pos.length/3);
 const x=(k%cols)*TW,y=Math.floor(k/cols)*TH;c2.drawImage(cv,x,y);
 c2.fillStyle='#222';c2.font=`${Math.round(TH/26)}px system-ui,sans-serif`;c2.fillText(pl.title,x+TH/30,y+TH/18);
 c2.strokeStyle='#ccc';c2.strokeRect(x+.5,y+.5,TW-1,TH-1);
});
window.__ready=true;
</script>'''

def color_of(path_3mf):
    try:
        m = re.search(r'displaycolor="#([0-9A-Fa-f]{6})', zipfile.ZipFile(path_3mf).read('3D/3dmodel.model').decode())
        return [int(m.group(1)[i:i+2], 16) / 255 for i in (0, 2, 4)], len(re.findall(r'<item ', zipfile.ZipFile(path_3mf).read('3D/3dmodel.model').decode()))
    except (OSError, KeyError, AttributeError):
        return [.6, .6, .6], 0

def collect(kit_dir, bed):
    plates = []
    for stl in sorted(glob.glob(os.path.join(kit_dir, '*', '*.stl'))):
        T = K.read_mesh(stl).astype('<f4')
        rgb, n = color_of(stl[:-4] + '.3mf')
        name = os.path.basename(stl)[:-4]
        label = re.sub(r'_(\d+)$', r' \1', name.replace('_', ' ', name.count('_') - 1)) if False else name.replace('_', ' ')
        lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)                # cadrage sur le contenu du plateau
        c = [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2]; fit = float(max(math.hypot(hi[0] - lo[0], hi[1] - lo[1]) / 2 + 8, 48))
        plates.append(dict(name=name, title=f'{label}' + (f' - {n} pièce' + ('s' if n > 1 else '') if n else ''), c=[round(float(x), 2) for x in c], fit=round(fit, 2), rgb=[round(c, 3) for c in rgb],
                           pos=base64.b64encode(T.tobytes()).decode(), n=n))
    return plates

def render_kit(kit_dir, out_dir, bed=(256, 256), cols=3, elev=38, azim=-28, single=(1500, 1050), tile=(760, 540)):
    """Écrit plateau_<nom>.png pour chaque plateau et apercu_plateaux.png. -> liste des fichiers."""
    chrome = N.find_chrome()
    if not chrome: raise SystemExit('Chrome/Chromium introuvable (variable CHROME pour l\'indiquer).')
    plates = collect(kit_dir, bed)
    if not plates: raise SystemExit(f'aucun plateau .stl dans {kit_dir}/*/')
    os.makedirs(out_dir, exist_ok=True)
    data = dict(bed=list(bed), plates=plates, cols=min(cols, len(plates)), tile=list(tile), single=list(single), elev=elev, azim=azim)
    files = []
    with tempfile.TemporaryDirectory() as d:
        html = os.path.join(d, 'p.html')
        open(html, 'w', encoding='utf-8').write(HTML.replace('__DATA__', json.dumps(data, separators=(',', ':'))))
        def shot(frag, png, w, h):
            cmd = [chrome, '--headless=new', '--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
                   '--ignore-gpu-blocklist', '--hide-scrollbars', f'--window-size={w},{h}', '--virtual-time-budget=20000',
                   '--screenshot=' + os.path.abspath(png), 'file://' + html.replace(os.sep, '/') + '#' + frag]
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if not os.path.exists(png) or os.path.getsize(png) < 500: raise SystemExit('échec du rendu de ' + png)
            files.append(png)
        n = len(plates); cols_ = data['cols']; rows = math.ceil(n / cols_)
        shot('all', os.path.join(out_dir, 'apercu_plateaux.png'), tile[0] * cols_, tile[1] * rows)
        for i, p in enumerate(plates):
            shot(str(i), os.path.join(out_dir, f"plateau_{p['name']}.png"), single[0], single[1])
    return files

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('kit'); ap.add_argument('--out'); ap.add_argument('--bed', type=float, nargs=2, default=[256, 256])
    a = ap.parse_args()
    files = render_kit(a.kit, a.out or os.path.join(a.kit, 'apercus'), tuple(a.bed))
    print(f'{len(files)} images -> {os.path.dirname(files[0])}/')

if __name__ == '__main__':
    main()
