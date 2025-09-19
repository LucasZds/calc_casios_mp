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

# ===================== SISTEMAS CON POLEA =====================
def _rampa_sensor():
    print("Convencion: eje + hacia abajo de la rampa.")
    th=_ask_float("theta (deg):"); v0=_ask_float("v0 (+ bajando):"); D=_ask_float("D (a sensor):")
    a = g*math.sin(_deg2rad(th)); print("a = g sin =", _fmt(a))
    t=_ask_float("t eval:"); v=v0+a*t; x=D+v0*t+0.5*a*t*t
    print("v(t) =", _fmt(v)); print("x(t) =", _fmt(x))
    if a!=0 and v0<0:
        tstar=-v0/a; xmin=D+v0*tstar+0.5*a*tstar*tstar
        print("t* =", _fmt(tstar)); print("x_min =", _fmt(xmin))
    else: print("no hay giro si v0>=0")
    muk=_ask_float("mu_k horizontal:"); 
    if muk>0:
        vbase=abs(v0); sstop=vbase*vbase/(2*muk*g); print("frenado =", _fmt(sstop))
    _pause()

def _loop_rodando():
    print("Loop con rodadura: v_top^2 >= g R")
    R=_ask_float("R:"); b=_ask_float("b en I=b m r^2:")
    vmin=math.sqrt(g*R); hmin=2.0*R + 0.5*(1.0+b)*R
    print("v_min =", _fmt(vmin)); print("h_min =", _fmt(hmin)); _pause()

def _atwood_ideal():
    print("Atwood ideal (sin I)")
    m1=_ask_float("m1:"); m2=_ask_float("m2:")
    a = g*(m2 - m1)/(m1 + m2)
    T = (2*m1*m2/(m1+m2))*g
    print("a =", _fmt(a))
    print("T aprox =", _fmt(T))
    _pause()

def _atwood_polea_inercia():
    print("Atwood con polea con inercia (sin friccion en cuerda)")
    m1=_ask_float("m1 (lado 1):"); m2=_ask_float("m2 (lado 2):")
    I=_ask_float("I de polea:"); R=_ask_float("R de polea:")
    denom = m1 + m2 + (I/(R*R) if R!=0 else 0.0)
    if denom==0: print("denominador 0"); _pause(); return
    a = (m2 - m1)*g / denom  # positivo si baja m2
    T1 = m1*(g + a)  # m1 sube si a>0
    T2 = m2*(g - a)
    print("a = (m2-m1) g / (m1+m2+I/R^2) =", _fmt(a))
    print("T1 =", _fmt(T1), " T2 =", _fmt(T2))
    _pause()

def _atwood_polea_mesa_mu():
    print("m1 en mesa con friccion mu_k, m2 colgando, polea con I,R")
    m1=_ask_float("m1 (mesa):"); m2=_ask_float("m2 (colg):"); mu=_ask_float("mu_k:")
    I=_ask_float("I polea:"); R=_ask_float("R polea:")
    denom = m1 + m2 + (I/(R*R) if R!=0 else 0.0)
    num = (m2 - mu*m1)*g
    if denom==0: print("denominador 0"); _pause(); return
    a = num/denom  # positivo: baja m2
    T1 = m1*a + mu*m1*g
    T2 = m2*(g - a)
    print("a = (m2 - mu m1) g / (m1+m2+I/R^2) =", _fmt(a))
    print("T1 (mesa) =", _fmt(T1), " T2 (colg) =", _fmt(T2))
    _pause()

def _loop_estimar_R_tabla():
    print("R desde pares (b, h). Enter vacio para terminar.")
    sumR = 0.0
    n = 0
    while True:
        sb = input("b (vacio=fin): ").strip()
        if not sb:
            break
        try:
            b = float(sb)
        except:
            print("b invalido")
            continue
        print("h:")
        sh = input("> ").strip()
        try:
            h = float(sh)
        except:
            print("h invalido")
            continue
        Ri = (2.0*h) / (5.0 + b)
        print("R_i = " + _fmt(Ri))
        sumR += Ri
        n += 1
    if n > 0:
        Rprom = sumR / n
        print("R promedio = " + _fmt(Rprom))
    _pause()

def _loop_tabla_teorica():
    R = _ask_float("R:")
    print("b -> h_teorica")
    while True:
        sb = input("b (vacio=fin): ").strip()
        if not sb:
            break
        try:
            b = float(sb)
        except:
            print("b invalido")
            continue
        h = R*(2.0 + 0.5*(1.0 + b))
        print("h = " + _fmt(h))
    _pause()


def _menu_poleas():
    items = [
        ("Rampa+Sensor (sin friccion)", _rampa_sensor),
        ("Loop rodando (I=b m r^2)", _loop_rodando),
        ("Atwood ideal", _atwood_ideal),
        ("Atwood con inercia (I,R)", _atwood_polea_inercia),
        ("Atwood en mesa con mu e I", _atwood_polea_mesa_mu),
        ("Loop: estimar R desde tabla", _loop_estimar_R_tabla),
        ("Loop: tabla teorica h(b)", _loop_tabla_teorica),
    ]
    while True:
        fn=_menu("Sistemas con polea", items); 
        if fn is None: return
        try: fn()
        except Exception as e: print("Error:", e); _pause()

# ===================== COLISIONES 1D =====================
def _col_elastica():
    print("Colision elastica 1D")
    m1=_ask_float("m1:"); m2=_ask_float("m2:"); v1=_ask_float("v1:"); v2=_ask_float("v2:")
    if m1+m2==0: print("m1+m2=0"); _pause(); return
    v1p = ((m1-m2)/(m1+m2))*v1 + (2*m2/(m1+m2))*v2
    v2p = (2*m1/(m1+m2))*v1 + ((m2-m1)/(m1+m2))*v2
    print("v1' =", _fmt(v1p)); print("v2' =", _fmt(v2p))
    _pause()

def _col_inel_total():
    print("Colision inelastica total (se pegan)")
    m1=_ask_float("m1:"); m2=_ask_float("m2:"); v1=_ask_float("v1:"); v2=_ask_float("v2:")
    if m1+m2==0: print("m1+m2=0"); _pause(); return
    vf = (m1*v1 + m2*v2)/(m1+m2)
    Ki = 0.5*m1*v1*v1 + 0.5*m2*v2*v2
    Kf = 0.5*(m1+m2)*vf*vf
    print("vf =", _fmt(vf)); print("DeltaK =", _fmt(Kf-Ki))
    _pause()

def _col_coef_e():
    print("Colision con restitucion e (1D)")
    m1=_ask_float("m1:"); m2=_ask_float("m2:"); v1=_ask_float("v1:"); v2=_ask_float("v2:"); e=_ask_float("e (0..1):")
    if m1+m2==0: print("m1+m2=0"); _pause(); return
    v1p = (m1*v1 + m2*v2 - m2*e*(v1 - v2)) / (m1 + m2)
    v2p = (m1*v1 + m2*v2 + m1*e*(v1 - v2)) / (m1 + m2)
    print("v1' =", _fmt(v1p)); print("v2' =", _fmt(v2p))
    _pause()

def _menu_colisiones():
    items = [
        ("elastica (1D)", _col_elastica),
        ("inelastica total", _col_inel_total),
        ("con e (0..1)", _col_coef_e),
    ]
    while True:
        fn=_menu("Colisiones 1D", items); 
        if fn is None: return
        try: fn()
        except Exception as e: print("Error:", e); _pause()

# ===================== PÉNDULO SIMPLE (de v1) =====================
def _pendulo():
    print("Pendulo simple (angulo pequeño)")
    mode = input("[1] hallar T   [2] hallar g: ").strip()
    if mode=="1":
        L=_ask_float("L (m):")
        if L<=0: print("L>0")
        else:
            T = 2.0*math.pi*math.sqrt(L/g)
            print("T = 2pi sqrt(L/g) =", _fmt(T))
    elif mode=="2":
        L=_ask_float("L (m):"); T=_ask_float("T (s):")
        if T<=0: print("T>0")
        else:
            gv = (4.0*math.pi*math.pi*L)/(T*T)
            print("g =", _fmt(gv))
    else:
        print("opcion invalida")
    _pause()

# ===================== app =====================
def app():
    items = [
        ("Sistemas con polea", _menu_poleas),
        ("Colisiones 1D", _menu_colisiones),
        ("Pendulo simple", _pendulo),
        ("configurar g", _cfg_g),
    ]
    while True:
        fn=_menu("Poleas / Colisiones / Pendulo", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            print("Error:", e); _pause()

if __name__ == "__main__":
    app()
