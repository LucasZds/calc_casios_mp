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

# ===================== CINEMATICA =====================
def _mru_solver():
    print("MRU: x = x0 + v*t")
    tgt = input("objetivo [x|v|t]: ").strip()
    if tgt=="x":
        x0=_ask_float("x0:"); v=_ask_float("v:"); t=_ask_float("t:")
        x = x0 + v*t
        print("x = x0 + v t =", _fmt(x0), "+", _fmt(v), "*", _fmt(t), "=", _fmt(x))
    elif tgt=="v":
        x=_ask_float("x:"); x0=_ask_float("x0:"); t=_ask_float("t:")
        if t==0: print("t=0")
        else:
            v=(x-x0)/t
            print("v = (x-x0)/t =", "(",_fmt(x),"-",_fmt(x0),")/",_fmt(t),"=", _fmt(v))
    elif tgt=="t":
        x=_ask_float("x:"); x0=_ask_float("x0:"); v=_ask_float("v:")
        if v==0: print("v=0")
        else:
            t=(x-x0)/v
            print("t = (x-x0)/v =", "(",_fmt(x),"-",_fmt(x0),")/",_fmt(v),"=", _fmt(t))
    else:
        print("objetivo invalido")
    _pause()

def _mrua_solver():
    print("MRUA: v=v0+a t | x=x0+v0 t+0.5 a t^2 | v^2=v0^2+2 a (x-x0)")
    tgt = input("objetivo [v|t|x|a]: ").strip()
    print("elige ecuacion: [1] v=v0+a t  [2] x=...  [3] v^2=...")
    eq = input("> ").strip()

    if tgt=="t" and eq=="1":
        v=_ask_float("v:"); v0=_ask_float("v0:"); a=_ask_float("a:")
        if a==0: print("a=0")
        else:
            t=(v-v0)/a
            print("t = (v-v0)/a =", _fmt((v-v0)/a))
    elif tgt=="t" and eq=="2":
        x=_ask_float("x:"); x0=_ask_float("x0:"); v0=_ask_float("v0:"); a=_ask_float("a:")
        A=0.5*a; B=v0; C=(x0-x)
        disc=B*B-4*A*C
        print("cuadratica: (1/2)a t^2 + v0 t + (x0-x)=0")
        print("A=",_fmt(A)," B=",_fmt(B)," C=",_fmt(C)," disc=",_fmt(disc))
        if A==0:
            if B==0: print("sin datos")
            else:
                t=-C/B
                print("t unica =", _fmt(t))
        elif disc<0:
            print("sin soluciones reales")
        else:
            rt=math.sqrt(disc); t1=(-B+rt)/(2*A); t2=(-B-rt)/(2*A)
            print("t1=",_fmt(t1)," t2=",_fmt(t2))
    elif tgt=="v" and eq=="1":
        v0=_ask_float("v0:"); a=_ask_float("a:"); t=_ask_float("t:")
        v=v0+a*t; print("v = v0 + a t =", _fmt(v))
    elif tgt=="v" and eq=="3":
        v0=_ask_float("v0:"); a=_ask_float("a:"); x=_ask_float("x:"); x0=_ask_float("x0:")
        dx=x-x0; val=v0*v0+2*a*dx
        if val<0: print("sin v real")
        else:
            v=math.sqrt(val); print("v^2 = v0^2 + 2 a dx =", _fmt(val)); print("v = +/-", _fmt(v))
    elif tgt=="x" and eq=="2":
        x0=_ask_float("x0:"); v0=_ask_float("v0:"); a=_ask_float("a:"); t=_ask_float("t:")
        x=x0+v0*t+0.5*a*t*t; print("x =", _fmt(x))
    elif tgt=="a" and eq=="1":
        v=_ask_float("v:"); v0=_ask_float("v0:"); t=_ask_float("t:")
        if t==0: print("t=0")
        else:
            a=(v-v0)/t; print("a = (v-v0)/t =", _fmt(a))
    elif tgt=="a" and eq=="3":
        v=_ask_float("v:"); v0=_ask_float("v0:"); x=_ask_float("x:"); x0=_ask_float("x0:")
        dx=x-x0
        if dx==0: print("dx=0")
        else:
            a=(v*v - v0*v0)/(2*dx); print("a =", _fmt(a))
    else:
        print("combo no soportado")
    _pause()

def _menu_cinematica():
    items = [
        ("MRU (solver)", _mru_solver),
        ("MRUA (solver)", _mrua_solver),
    ]
    while True:
        fn=_menu("Cinematica", items); 
        if fn is None: return
        try: fn()
        except Exception as e: print("Error:", e); _pause()

# ===================== DINAMICA =====================
def _newton_simple():
    print("Newton 2a: Fnet = m a")
    tgt = input("objetivo [F|m|a]: ").strip().lower()
    if tgt=="f":
        m=_ask_float("m:"); a=_ask_float("a:"); print("F =", _fmt(m*a))
    elif tgt=="m":
        F=_ask_float("Fnet:"); a=_ask_float("a:"); 
        if a==0: print("a=0")
        else: print("m =", _fmt(F/a))
    elif tgt=="a":
        F=_ask_float("Fnet:"); m=_ask_float("m:"); 
        if m==0: print("m=0")
        else: print("a =", _fmt(F/m))
    else: print("objetivo invalido")
    _pause()

def _friccion_horizontal():
    print("Bloque horizontal con friccion: Fnet = F - mu m g , a=Fnet/m")
    F=_ask_float("F aplicada:"); m=_ask_float("m:"); mu=_ask_float("mu_k:")
    Fnet = F - mu*m*g; a = Fnet/m if m!=0 else 0.0
    print("Fnet =", _fmt(Fnet)); print("a =", _fmt(a)); _pause()

def _plano_inclinado_mu():
    print("Plano inclinado con friccion (bajando): a = g(sin th - mu cos th)")
    th=_ask_float("theta (deg):"); mu=_ask_float("mu_k:")
    a = g*(math.sin(_deg2rad(th)) - mu*math.cos(_deg2rad(th)))
    print("a =", _fmt(a)); _pause()

def _fuerza_angulo_horizontal():
    print("Horizontal con F a angulo (con friccion mu_k)")
    m=_ask_float("m:"); mu=_ask_float("mu_k:"); F=_ask_float("F:"); th=_ask_float("theta (deg, + arriba):")
    c=math.cos(_deg2rad(th)); s=math.sin(_deg2rad(th))
    N = m*g - F*s
    if N<0: 
        print("advertencia: N<0 -> sin contacto. Tomo N=0.")
        N=0.0
    f = mu*N
    Fnet = F*c - f
    a = Fnet/m if m!=0 else 0.0
    print("N = m g - F sin =", _fmt(N))
    print("f = mu N =", _fmt(f))
    print("Fnet = F cos - f =", _fmt(Fnet))
    print("a = Fnet/m =", _fmt(a))
    _pause()

def _menu_dinamica():
    items = [
        ("Fnet=m a (solver)", _newton_simple),
        ("horizontal con friccion", _friccion_horizontal),
        ("plano inclinado con mu", _plano_inclinado_mu),
        ("F a angulo en horizontal", _fuerza_angulo_horizontal),
    ]
    while True:
        fn=_menu("Dinamica", items); 
        if fn is None: return
        try: fn()
        except Exception as e: print("Error:", e); _pause()

# ===================== app =====================
def app():
    items = [
        ("Cinematica", _menu_cinematica),
        ("Dinamica (fuerzas)", _menu_dinamica),
        ("configurar g (actual %s m/s^2)"%_fmt(g), _cfg_g),  # opcional
    ]
    while True:
        fn=_menu("Cinematica / Dinamica", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            print("Error:", e); _pause()

if __name__ == "__main__":
    app()
