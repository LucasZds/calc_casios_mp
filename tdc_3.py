# ==== tdc_3.py (plots + ejemplos) ====
import math
from ui_py import view_menu, view_text_from_string, view_text

def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _menu(title, items):
    textos=[t for (t,_) in items]
    try: sel=view_menu(title, textos)
    except: sel=None
    if sel is None: return None
    return items[sel][1]

def _ask(s):
    try: return input(s)
    except: return ""

def _clip(title, lines, n=6):
    view_text(title, lines[:n]); _pause()

def _parse_value(s):
    s=(s or "").strip()
    if not s: return 0.0
    m=1.0; suf=s[-1]
    if suf=='k': m=1e3; s=s[:-1]
    elif suf=='M': m=1e6; s=s[:-1]
    elif suf=='m': m=1e-3; s=s[:-1]
    elif suf=='u': m=1e-6; s=s[:-1]
    elif suf=='n': m=1e-9; s=s[:-1]
    try: return float(s)*m
    except: return 0.0

def _rect(mag, ang):
    return complex(mag*math.cos(ang), mag*math.sin(ang))

# --- helpers ángulo (la Casio no trae math.radians/degrees) ---
PI = 3.141592653589793
def _rad(deg):  # grados → radianes
    try: return deg * PI / 180.0
    except: return 0.0

def _deg(rad):  # radianes → grados
    try: return rad * 180.0 / PI
    except: return 0.0

def _parse_phasor(s):
    # Acepta: 10a30, 10 a 30, 10@30, 10∠30
    s = (s or "").strip()
    if not s: return 0j
    s = s.replace("∠", "a").replace("@", "a")
    s = "".join(s.split())  # quita espacios
    if "a" in s:
        mag_s, rest = s.split("a", 1)
        # magnitud con sufijos (k, m, u, n) usando tu _parse_value
        mag = _parse_value(mag_s)
        # prefijo numérico del ángulo
        j = 0
        while j < len(rest) and (rest[j].isdigit() or rest[j] in "+-."):
            j += 1
        ang_s = rest[:j] if j > 0 else "0"
        try: ang = float(ang_s)
        except: ang = 0.0
        return _rect(mag, _rad(ang))
    return complex(_parse_value(s), 0.0)

def _fmt_polar(z):
    # usa _deg en lugar de math.degrees
    return "{:.6g}a{:.3g}°".format(abs(z), _deg(math.atan2(z.imag, z.real)))

def _fmt_p(z):  # si la usás en ejemplos
    return "{:.6g}a{:.3g}°".format(abs(z), _deg(math.atan2(z.imag, z.real)))

# ---- Plots casioplot (import on demand) ----
def plot_triangulo_potencias_casio():
    try:
        import casioplot as cp
    except:
        view_text_from_string("Aviso","casioplot no disponible"); _pause(); return
    Vs=_ask("V (mag a ang): "); Is=_ask("I (mag a ang): ")
    try:
        V=_parse_phasor(Vs); I=_parse_phasor(Is); S= V * complex(I.real,-I.imag)
        P=S.real; Q=S.imag
        W,H=127,63; CX,CY=W//2,H//2
        kx=(W*0.40)/max(abs(P),1e-9); ky=(H*0.40)/max(abs(Q),1e-9)
        def line(x0,y0,x1,y1):
            x0=int(x0); y0=int(y0); x1=int(x1); y1=int(y1)
            dx=abs(x1-x0); sx=1 if x0<x1 else -1
            dy=-abs(y1-y0); sy=1 if y0<y1 else -1
            err=dx+dy
            while True:
                if 0<=x0<=W and 0<=y0<=H: cp.set_pixel(x0,y0,"black")
                if x0==x1 and y0==y1: break
                e2=2*err
                if e2>=dy: err+=dy; x0+=sx
                if e2<=dx: err+=dx; y0+=sy
        def to_scr(x,y): return int(CX+x*kx), int(CY-y*ky)
        cp.clear_screen()
        line(0,CY,W,CY); line(CX,0,CX,H)
        x0,y0=to_scr(0,0); xp,yp=to_scr(P,0); xq,yq=to_scr(P,Q)
        line(x0,y0,xp,yp); line(xp,yp,xq,yq); line(x0,y0,xq,yq)
        cp.show_screen()
    except:
        view_text_from_string("Error","Entrada invalida"); _pause()

def plot_fasores_casio():
    try:
        import casioplot as cp
    except:
        view_text_from_string("Aviso","casioplot no disponible"); _pause(); return

    # wrapper de píxel compatible (mono y color)
    def _pset(x, y):
        x = int(x); y = int(y)
        try:
            cp.set_pixel(x, y)
            return
        except:
            pass
        try:
            cp.set_pixel(x, y, 1)
        except:
            pass

    def line(x0,y0,x1,y1):
        x0=int(x0); y0=int(y0); x1=int(x1); y1=int(y1)
        dx=abs(x1-x0); sx=1 if x0<x1 else -1
        dy=-abs(y1-y0); sy=1 if y0<y1 else -1
        err=dx+dy
        while True:
            _pset(x0,y0)
            if x0==x1 and y0==y1: break
            e2=2*err
            if e2>=dy: err+=dy; x0+=sx
            if e2<=dx: err+=dx; y0+=sy

    s1=_ask("F1 (mag a ang): ")
    s2=_ask("F2 (mag a ang): ")
    s3=_ask("F3 (mag a ang o vacio): ")
    fs=[s for s in (s1,s2,s3) if (s or "").strip()]
    try:
        zs=[_parse_phasor(s) for s in fs]
        zsum=0j
        for z in zs: zsum += z

        W,H=127,63; CX,CY=W//2,H//2
        m = 1.0
        for z in zs+[zsum]:
            a = abs(z)
            if a > m: m = a
        k=(W*0.40)/(m if m>0 else 1.0)

        def to_scr(x,y): return int(CX+x*k), int(CY-y*k)

        cp.clear_screen()
        # ejes
        line(0,CY,W,CY); line(CX,0,CX,H)

        x0,y0=to_scr(0,0)
        for z in zs:
            x1,y1=to_scr(z.real, z.imag)
            line(x0,y0,x1,y1)

        # vector suma
        x1,y1=to_scr(zsum.real, zsum.imag)
        line(x0,y0,x1,y1)
        cp.show_screen()
        _pause()
        
    except Exception as e:
        # si querés ver el motivo real, mostramos el error:
        try:
            view_text_from_string("Error", "Entrada invalida / plot: {}".format(repr(e)))
        except:
            view_text_from_string("Error","Entrada invalida")
        _pause()


# ---- Ejemplos AC (usa solver “a mano” simple) ----
def _fmt_p(z): return "{:.6g}a{:.3g}°".format(abs(z), _deg(math.atan2(z.imag, z.real)))

def ejemplos_ac():
    casos=[
        ("RC serie 1kHz", "V 1 0 10a a 0; R 1 2 1k; C 2 0 100n", "1k"),
        ("RL serie 50Hz", "V 1 0 230 a 0; R 1 2 10; L 2 0 100m", "50"),
        ("Z generica",    "V 1 0 12a a 0; Z 1 2 100 a 45; R 2 0 200", "60"),
    ]
    def _run(net,f):
        # Resuelve importando transitoriamente el solver de tdc_2 para no duplicar memoria
        M=__import__("tdc_2")
        try:
            A,z,node_list,vsrcs,w = M._stamp_ac(M._parse_netlist_1line(net), M._parse_freq(f))
            sol = M._gauss_solve_cpx(A, z)
            lines=["f={} Hz".format(f), "Net: {}".format(net), " "]
            i=0
            while i<len(node_list):
                lines.append("V({}) = {}".format(node_list[i], _fmt_p(sol[i]))); i+=1
            view_text("Ejemplo AC", lines); _pause()
        finally:
            try:
                import sys
                if "tdc_2" in sys.modules:
                    del sys.modules["tdc_2"]
            except:
                pass
            try:
                import gc; gc.collect()
            except:
                pass
    items=[]
    i=0
    while i<len(casos):
        nm, nl, fz = casos[i]
        def mk(n=nl, f=fz):
            return lambda: _run(n,f)
        items.append((nm, mk()))
        i+=1
    while True:
        fn=_menu("Ejemplos AC", items)
        if fn is None: return
        fn()

def app():
    items=[
        ("Plot: Triangulo P-Q-S", plot_triangulo_potencias_casio),
        ("Plot: Fasores",         plot_fasores_casio),
        ("Ejemplos AC",           ejemplos_ac),
    ]
    while True:
        fn=_menu("Graficos + Ejemplos", items)
        if fn is None: return
        try: fn()
        except Exception as e: view_text_from_string("Error", str(e)); _pause()

if __name__ == "__main__":
    app()
