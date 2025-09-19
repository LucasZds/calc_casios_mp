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

# ===================== RESORTES / MAS =====================
def _hooke_solver():
    print("Hooke: F = k x")
    tgt=input("objetivo [F|k|x]: ").strip().lower()
    if tgt=="f":
        k=_ask_float("k:"); x=_ask_float("x:"); print("F =", _fmt(k*x))
    elif tgt=="k":
        F=_ask_float("F:"); x=_ask_float("x:")
        if x==0: print("x=0")
        else: print("k =", _fmt(F/x))
    elif tgt=="x":
        F=_ask_float("F:"); k=_ask_float("k:")
        if k==0: print("k=0")
        else: print("x =", _fmt(F/k))
    else: print("opcion invalida")
    _pause()

def _mas_params():
    print("MAS: w = sqrt(k/m),  T = 2 pi / w,  f = 1/T")
    m=_ask_float("m:"); k=_ask_float("k:")
    if m<=0 or k<=0: print("m>0, k>0")
    else:
        w=math.sqrt(k/m); T=2*math.pi/w; f=1.0/T
        print("w =", _fmt(w)); print("T =", _fmt(T)); print("f =", _fmt(f))
    _pause()

def _mas_estado():
    print("x=A cos(w t + phi), v=-A w sin(...), a=-w^2 x")
    A=_ask_float("A:"); w=_ask_float("w:"); ph=_ask_float("phi (rad):"); t=_ask_float("t:")
    x=A*math.cos(w*t+ph); v=-A*w*math.sin(w*t+ph); a=-w*w*x
    print("x =", _fmt(x)); print("v =", _fmt(v)); print("a =", _fmt(a))
    _pause()

def _menu_resortes():
    items = [
        ("Hooke F=kx", _hooke_solver),
        ("MAS: w, T, f", _mas_params),
        ("MAS: x,v,a en t", _mas_estado),
    ]
    while True:
        fn=_menu("Resortes / MAS", items); 
        if fn is None: return
        try: fn()
        except Exception as e: print("Error:", e); _pause()

# ===================== ROTACIONAL =====================
def _inercia_tabla():
    print("I tabla (eje por centro):")
    print("[1] barra delgada (L): I=(1/12) m L^2")
    print("[2] disco/cilindro solido: I=(1/2) m r^2")
    print("[3] aro/anillo: I=m r^2")
    print("[4] esfera solida: I=(2/5) m r^2")
    op=input("> ").strip()
    I=None; m=None
    if op=="1":
        m=_ask_float("m:"); L=_ask_float("L:"); I=(1.0/12.0)*m*L*L
    elif op=="2":
        m=_ask_float("m:"); r=_ask_float("r:"); I=0.5*m*r*r
    elif op=="3":
        m=_ask_float("m:"); r=_ask_float("r:"); I=m*r*r
    elif op=="4":
        m=_ask_float("m:"); r=_ask_float("r:"); I=(2.0/5.0)*m*r*r
    else:
        print("opcion invalida"); _pause(); return
    print("I_cm =", _fmt(I))
    use=input("usar eje paralelo (s/n): ").strip().lower()
    if use=="s":
        d=_ask_float("d:"); I = I + m*d*d; print("I =", _fmt(I))
    _pause()

def _torque_alpha():
    print("tau = I alpha")
    tgt=input("objetivo [tau|I|alpha]: ").strip().lower()
    if tgt=="tau":
        I=_ask_float("I:"); a=_ask_float("alpha:"); print("tau =", _fmt(I*a))
    elif tgt=="alpha":
        tau=_ask_float("tau:"); I=_ask_float("I:"); 
        if I==0: print("I=0")
        else: print("alpha =", _fmt(tau/I))
    elif tgt=="i":
        tau=_ask_float("tau:"); a=_ask_float("alpha:"); 
        if a==0: print("alpha=0")
        else: print("I =", _fmt(tau/a))
    else: print("opcion invalida")
    _pause()

def _momento_angular():
    print("L = I w")
    tgt=input("objetivo [L|I|w]: ").strip().lower()
    if tgt=="l":
        I=_ask_float("I:"); w=_ask_float("w:"); print("L =", _fmt(I*w))
    elif tgt=="i":
        L=_ask_float("L:"); w=_ask_float("w:"); 
        if w==0: print("w=0")
        else: print("I =", _fmt(L/w))
    elif tgt=="w":
        L=_ask_float("L:"); I=_ask_float("I:"); 
        if I==0: print("I=0")
        else: print("w =", _fmt(L/I))
    else: print("opcion invalida")
    _pause()

def _menu_rotacional():
    items = [
        ("Inercia (tabla + Steiner)", _inercia_tabla),
        ("Torque tau=I alpha", _torque_alpha),
        ("Momento angular L=I w", _momento_angular),
    ]
    while True:
        fn=_menu("Rotacional", items); 
        if fn is None: return
        try: fn()
        except Exception as e: print("Error:", e); _pause()

# ===================== app =====================
def app():
    items = [
        ("Resortes / MAS", _menu_resortes),
        ("Rotacional", _menu_rotacional),

        ("configurar g", _cfg_g),
    ]
    while True:
        fn=_menu("Resorte / Rotacion", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            print("Error:", e); _pause()

if __name__ == "__main__":
    app()
