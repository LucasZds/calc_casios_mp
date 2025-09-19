# fisica.py — unificado: cinematica, dinamica, energia, circular,
# resortes/MAS, rotacional, rampa+sensor, loop, Atwood (ideal e inercia),
# polea en mesa con mu, colisiones 1D, péndulo simple
import math
from ui_py import view_menu  # navegación uniforme

# ===== helpers UI =====
def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _ask_float(label):
    print(label); s=input("> ").strip()
    try: return float(s)
    except: return 0.0

def _fmt(x, nd=10):
    iv=int(x)
    if x == iv: return str(iv)
    return ("{:.%dg}"%nd).format(x)

def _deg2rad(d): return d*math.pi/180.0

def _menu(title, items, cols=None, lpp=None):
    # items: [(texto, funcion), ...]
    textos = []
    i = 0
    while i < len(items):
        textos.append(items[i][0])   # sin "[i] " acá
        i += 1
    sel = view_menu(title, textos, cols=cols, lines_per_screen=lpp)
    if sel is None:
        return None
    return items[sel][1]


# ===== config =====
g = 9.81
def _cfg_g():
    global g
    val = _ask_float("g actual = %s  (m/s^2). Nuevo g:"%_fmt(g))
    if val>0: g = val
    print("g =", _fmt(g)); _pause()

# ===================== ENERGIA / TRABAJO / POTENCIA =====================
def _trabajo_escalar():
    print("Trabajo: W = F d cos(theta)")
    tgt=input("objetivo [W|F|d|theta]: ").strip().lower()
    if tgt=="w":
        F=_ask_float("F:"); d=_ask_float("d:"); th=_ask_float("theta (deg):")
        W=F*d*math.cos(_deg2rad(th)); print("W =", _fmt(W))
    elif tgt=="f":
        W=_ask_float("W:"); d=_ask_float("d:"); th=_ask_float("theta (deg):")
        c=math.cos(_deg2rad(th)); 
        if d*c==0: print("d cos=0")
        else: print("F =", _fmt(W/(d*c)))
    elif tgt=="d":
        W=_ask_float("W:"); F=_ask_float("F:"); th=_ask_float("theta (deg):")
        c=math.cos(_deg2rad(th)); 
        if F*c==0: print("F cos=0")
        else: print("d =", _fmt(W/(F*c)))
    elif tgt=="theta":
        W=_ask_float("W:"); F=_ask_float("F:"); d=_ask_float("d:")
        if F*d==0: print("F d=0")
        else:
            c=W/(F*d)
            if c<-1 or c>1: print("cos fuera de rango")
            else: print("theta =", _fmt(math.degrees(math.acos(c))), "deg")
    else: print("objetivo invalido")
    _pause()

def _trabajo_energia():
    print("Trabajo-energia: Wnet = 0.5 m (v^2 - v0^2)")
    tgt=input("objetivo [v|Wnet]: ").strip().lower()
    m=_ask_float("m:")
    if tgt=="v":
        v0=_ask_float("v0:"); W=_ask_float("Wnet:")
        val = v0*v0 + 2*W/m if m!=0 else float("inf")
        v = math.sqrt(val) if val>=0 else float("nan")
        print("v^2 =", _fmt(val)); print("v = +/-", _fmt(v))
    elif tgt=="wnet":
        v=_ask_float("v:"); v0=_ask_float("v0:")
        W = 0.5*m*(v*v - v0*v0); print("Wnet =", _fmt(W))
    else: print("objetivo invalido")
    _pause()

def _energia_conservativa():
    print("Emec: 0.5 m v^2 + m g h + 0.5 k x^2 = const")
    mode=input("[1] v final  [2] h final  [3] x final: ").strip()
    m=_ask_float("m:"); k=_ask_float("k (0 si no hay):")
    v0=_ask_float("v0:"); h0=_ask_float("h0:"); x0=_ask_float("x0:")
    E0 = 0.5*m*v0*v0 + m*g*h0 + 0.5*k*x0*x0
    print("E0 =", _fmt(E0))
    if mode=="1":
        h=_ask_float("h:"); x=_ask_float("x:")
        val = 2*(E0 - m*g*h - 0.5*k*x*x)/m if m!=0 else float("inf")
        v = math.sqrt(val) if val>=0 else float("nan"); print("v =", _fmt(v))
    elif mode=="2":
        v=_ask_float("v:"); x=_ask_float("x:")
        h = (E0 - 0.5*m*v*v - 0.5*k*x*x)/(m*g) if m*g!=0 else float("inf")
        print("h =", _fmt(h))
    elif mode=="3":
        v=_ask_float("v:"); h=_ask_float("h:")
        val = 2*(E0 - 0.5*m*v*v - m*g*h)/k if k!=0 else float("inf")
        x = math.sqrt(val) if val>=0 else float("nan"); print("x = +/-", _fmt(x))
    else: print("opcion invalida")
    _pause()

def _potencia():
    print("Potencia: P = W/t  o  P = F v cos(theta)")
    mode=input("[1] W/t   [2] F v cos: ").strip()
    if mode=="1":
        W=_ask_float("W:"); t=_ask_float("t:")
        if t==0: print("t=0")
        else: print("P =", _fmt(W/t))
    elif mode=="2":
        F=_ask_float("F:"); v=_ask_float("v:"); th=_ask_float("theta (deg):")
        P=F*v*math.cos(_deg2rad(th)); print("P =", _fmt(P))
    else: print("opcion invalida")
    _pause()

def _menu_energia():
    items = [
        ("Trabajo escalar", _trabajo_escalar),
        ("Trabajo-Energia", _trabajo_energia),
        ("Conservativa (v,h,x)", _energia_conservativa),
        ("Potencia", _potencia),
    ]
    while True:
        fn=_menu("Energia / Trabajo", items); 
        if fn is None: return
        try: fn()
        except Exception as e: print("Error:", e); _pause()

# ===================== CIRCULAR =====================
def _circular_rel():
    print("v_t = w r ; a_t = alpha r ; a_c = v^2/r = w^2 r")
    mode=input("[1] v_t  [2] w  [3] a_c: ").strip()
    if mode=="1":
        w=_ask_float("w:"); r=_ask_float("r:"); print("v_t =", _fmt(w*r))
    elif mode=="2":
        vt=_ask_float("v_t:"); r=_ask_float("r:")
        if r==0: print("r=0")
        else: print("w =", _fmt(vt/r))
    elif mode=="3":
        opt=input("[a] v^2/r  [b] w^2 r: ").strip().lower()
        if opt=="a":
            v=_ask_float("v:"); r=_ask_float("r:")
            if r==0: print("r=0")
            else: print("a_c =", _fmt(v*v/r))
        else:
            w=_ask_float("w:"); r=_ask_float("r:"); print("a_c =", _fmt(w*w*r))
    else: print("opcion invalida")
    _pause()

def _circular_cinematica_ang():
    print("w = w0 + alpha t ; theta = theta0 + w0 t + 0.5 alpha t^2")
    tgt=input("objetivo [w|theta]: ").strip().lower()
    if tgt=="w":
        w0=_ask_float("w0:"); a=_ask_float("alpha:"); t=_ask_float("t:"); print("w =", _fmt(w0+a*t))
    elif tgt=="theta":
        th0=_ask_float("theta0:"); w0=_ask_float("w0:"); a=_ask_float("alpha:"); t=_ask_float("t:")
        print("theta =", _fmt(th0 + w0*t + 0.5*a*t*t))
    else: print("opcion invalida")
    _pause()

def _menu_circular():
    items = [
        ("v_t, a_t, a_c", _circular_rel),
        ("cinematica angular", _circular_cinematica_ang),
    ]
    while True:
        fn=_menu("Circular", items); 
        if fn is None: return
        try: fn()
        except Exception as e: print("Error:", e); _pause()

# ===================== app =====================
def app():
    items = [

        ("Energia / Trabajo", _menu_energia),
        ("Circular", _menu_circular),
        ("configurar g", _cfg_g),
    ]
    while True:
        fn=_menu("Energia / Trabajo / Potencia / Circular", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            print("Error:", e); _pause()

if __name__ == "__main__":
    app()
