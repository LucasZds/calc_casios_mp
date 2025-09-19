# vectores.py — operaciones 2D/3D con menu de 7 lineas
import math
# ===== UI basica (7 lineas) =====
from ui_py import view_text, view_text_from_string, view_menu

# ===== helpers UI =====
def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _fmt(x, nd=10):
    iv=int(x)
    if x == iv: return str(iv)
    return ("{:.%dg}"%nd).format(x)

def _fmt_vec(v):
    return "(" + ", ".join(_fmt(c) for c in v) + ")"

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



def _ask_line(label):
    print(label); return input("> ").strip()

def _ask_float(label):
    print(label)
    s = input("> ").strip().replace(",", ".")
    try: return float(s)
    except: return 0.0

# ===== helpers numericos =====
_MODE_RAD = True  # True rad, False deg

def _in_mode_label(): return "rad" if _MODE_RAD else "deg"
def _to_rad(x): return x if _MODE_RAD else (x*math.pi/180.0)
def _from_rad(r): return r if _MODE_RAD else (r*180.0/math.pi)

def _toggle_mode():
    global _MODE_RAD
    _MODE_RAD = not _MODE_RAD
    view_text_from_string("Modo ángulos", "modo: " + _in_mode_label())
    _pause()

# ===== parseo de vectores =====
def _parse_floats(s):
    """
    Acepta:
      - Separador por COMA entre componentes (usa punto decimal):  (1.5, 2.75, 3)
      - Separador por ESPACIO/; entre componentes y COMA DECIMAL:  1,5 2,75 3  o  1,5;2,75;3
    Evita ambigüedad: si hay ', ' (coma+espacio) se toma la coma como separador.
    """
    s = s.strip()
    if s and s[0] in "([": s = s[1:]
    if s and s[-1] in ")]": s = s[:-1]
    has_comma_space = ", " in s or ",\t" in s
    has_decimal_comma = any(ch.isdigit() for ch in s) and any(tok for tok in s.split() if "," in tok and "." not in tok)

    tokens = []
    if has_comma_space or ("," in s and not has_decimal_comma):
        # Coma = separador; decimal con punto
        s = s.replace(",", " ")
        tokens = s.split()
        to_float = lambda t: float(t)
    else:
        # Decimal con coma; separadores = espacio o ';'
        for sep in [";", "\t"]:
            s = s.replace(sep, " ")
        tokens = s.split()
        to_float = lambda t: float(t.replace(",", "."))

    out=[]
    for t in tokens:
        try: out.append(to_float(t))
        except: pass
    return out

def _ask_vec2(prompt="v (x,y):"):
    vals = _parse_floats(_ask_line(prompt))
    if len(vals) < 2: vals = (0.0, 0.0)
    else: vals = (vals[0], vals[1])
    return vals

def _ask_vec3(prompt="v (x,y,z):"):
    vals = _parse_floats(_ask_line(prompt))
    if len(vals) < 3: vals = (0.0, 0.0, 0.0)
    else: vals = (vals[0], vals[1], vals[2])
    return vals

# ===== algebra comun =====
def _add(u, v): return tuple(u[i]+v[i] for i in range(len(u)))
def _sub(u, v): return tuple(u[i]-v[i] for i in range(len(u)))
def _scale(k, u): return tuple(k*u[i] for i in range(len(u)))
def _dot(u, v):
    s=0.0
    i=0
    while i<len(u): s += u[i]*v[i]; i+=1
    return s
def _norm(u):
    s=0.0; i=0
    while i<len(u): s += u[i]*u[i]; i+=1
    return math.sqrt(s)
def _unit(u):
    n=_norm(u)
    if n==0.0: return None
    return _scale(1.0/n, u)
def _angle(u, v):
    nu=_norm(u); nv=_norm(v)
    if nu==0.0 or nv==0.0: return None
    c = _dot(u,v)/(nu*nv)
    if c>1.0: c=1.0
    if c<-1.0: c=-1.0
    return math.acos(c)
def _proj_u_on_v(u, v):
    dv=_dot(v,v)
    if dv==0.0: return None
    return _scale(_dot(u,v)/dv, v)
def _dist(u,v):
    return _norm(_sub(u,v))
def _cross(u, v):
    return (u[1]*v[2]-u[2]*v[1],
            u[2]*v[0]-u[0]*v[2],
            u[0]*v[1]-u[1]*v[0])

# ===== 2D ops =====
def _2d_norm_unit():
    u=_ask_vec2("v (x,y):")
    n=_norm(u); w=_unit(u)
    lineas = ["v = " + _fmt_vec(u), "|v| = " + _fmt(n)]
    lineas.append("unitario: indefinido" if w is None else "unitario: " + _fmt_vec(w))
    view_text("2D: norma y unitario", lineas); _pause()

def _2d_add_sub():
    u=_ask_vec2("u (x,y):"); v=_ask_vec2("v (x,y):")
    view_text("2D: suma/resta", [
        "u = " + _fmt_vec(u),
        "v = " + _fmt_vec(v),
        "u+v = " + _fmt_vec(_add(u,v)),
        "u-v = " + _fmt_vec(_sub(u,v)),
    ]); _pause()

def _2d_scale():
    u=_ask_vec2("v (x,y):")
    k=_ask_float("k:")
    view_text("2D: escala", [
        "v = " + _fmt_vec(u),
        "k = " + _fmt(k),
        "k*v = " + _fmt_vec(_scale(k,u)),
    ]); _pause()

def _2d_dot_ang():
    u=_ask_vec2("u (x,y):"); v=_ask_vec2("v (x,y):")
    dp=_dot(u,v); ang=_angle(u,v)
    lineas = [
        "u = " + _fmt_vec(u),
        "v = " + _fmt_vec(v),
        "u·v = " + _fmt(dp),
    ]
    if ang is None:
        lineas.append("ángulo: indefinido")
    else:
        lineas.append("ángulo = " + _fmt(_from_rad(ang)) + " " + _in_mode_label())
    view_text("2D: punto y ángulo", lineas); _pause()

def _2d_proj_u_on_v():
    u=_ask_vec2("u (x,y):"); v=_ask_vec2("v (x,y):")
    p=_proj_u_on_v(u,v)
    view_text("2D: proyección de u sobre v", [
        "u = " + _fmt_vec(u),
        "v = " + _fmt_vec(v),
        "proyección indefinida (v=0)" if p is None else "proj_v(u) = " + _fmt_vec(p),
    ]); _pause()

def _2d_dist():
    u=_ask_vec2("p1 (x,y):"); v=_ask_vec2("p2 (x,y):")
    view_text("2D: distancia", [
        "p1 = " + _fmt_vec(u),
        "p2 = " + _fmt_vec(v),
        "dist = " + _fmt(_dist(u,v)),
    ]); _pause()

def _2d_rotate():
    v=_ask_vec2("v (x,y):")
    ang = _to_rad(_ask_float("ángulo (" + _in_mode_label() + "):"))
    c = math.cos(ang); s = math.sin(ang)
    w = (v[0]*c - v[1]*s, v[0]*s + v[1]*c)
    view_text("2D: rotación", [
        "v = " + _fmt_vec(v),
        "ángulo = " + _fmt(_from_rad(ang)) + " " + _in_mode_label(),
        "rot = " + _fmt_vec(w),
    ]); _pause()

def _menu_2d():
    while True:
        items = [
            ("norma | unitario", _2d_norm_unit),
            ("suma / resta", _2d_add_sub),
            ("producto punto y angulo", _2d_dot_ang),
            ("proyeccion u sobre v", _2d_proj_u_on_v),
            ("escala k*v", _2d_scale),
            ("distancia p1-p2", _2d_dist),
            ("rotar v por angulo", _2d_rotate),
            ("modo: " + _in_mode_label() + " (cambiar)", _toggle_mode),
        ]
        fn=_menu("Vectores 2D (" + _in_mode_label() + ")", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

# ===== 3D ops =====
def _3d_norm_unit():
    u=_ask_vec3("v (x,y,z):")
    n=_norm(u); w=_unit(u)
    lineas = ["v = " + _fmt_vec(u), "|v| = " + _fmt(n)]
    lineas.append("unitario: indefinido" if w is None else "unitario: " + _fmt_vec(w))
    view_text("3D: norma y unitario", lineas); _pause()

def _3d_add_sub():
    u=_ask_vec3("u (x,y,z):"); v=_ask_vec3("v (x,y,z):")
    view_text("3D: suma/resta", [
        "u = " + _fmt_vec(u),
        "v = " + _fmt_vec(v),
        "u+v = " + _fmt_vec(_add(u,v)),
        "u-v = " + _fmt_vec(_sub(u,v)),
    ]); _pause()

def _3d_scale():
    u=_ask_vec3("v (x,y,z):")
    k=_ask_float("k:")
    view_text("3D: escala", [
        "v = " + _fmt_vec(u),
        "k = " + _fmt(k),
        "k*v = " + _fmt_vec(_scale(k,u)),
    ]); _pause()

def _3d_dot_ang():
    u=_ask_vec3("u (x,y,z):"); v=_ask_vec3("v (x,y,z):")
    dp=_dot(u,v); ang=_angle(u,v)
    lineas = [
        "u = " + _fmt_vec(u),
        "v = " + _fmt_vec(v),
        "u·v = " + _fmt(dp),
    ]
    if ang is None:
        lineas.append("ángulo: indefinido")
    else:
        lineas.append("ángulo = " + _fmt(_from_rad(ang)) + " " + _in_mode_label())
    view_text("3D: punto y ángulo", lineas); _pause()

def _3d_cross():
    u=_ask_vec3("u (x,y,z):"); v=_ask_vec3("v (x,y,z):")
    view_text("3D: producto cruz", [
        "u = " + _fmt_vec(u),
        "v = " + _fmt_vec(v),
        "u x v = " + _fmt_vec(_cross(u,v)),
    ]); _pause()

def _3d_proj_u_on_v():
    u=_ask_vec3("u (x,y,z):"); v=_ask_vec3("v (x,y,z):")
    p=_proj_u_on_v(u,v)
    view_text("3D: proyección de u sobre v", [
        "u = " + _fmt_vec(u),
        "v = " + _fmt_vec(v),
        "proyección indefinida (v=0)" if p is None else "proj_v(u) = " + _fmt_vec(p),
    ]); _pause()

def _3d_dist():
    u=_ask_vec3("p1 (x,y,z):"); v=_ask_vec3("p2 (x,y,z):")
    view_text("3D: distancia", [
        "p1 = " + _fmt_vec(u),
        "p2 = " + _fmt_vec(v),
        "dist = " + _fmt(_dist(u,v)),
    ]); _pause()

def _menu_3d():
    while True:
        items = [
            ("norma | unitario", _3d_norm_unit),
            ("suma / resta", _3d_add_sub),
            ("producto punto y angulo", _3d_dot_ang),
            ("producto cruz", _3d_cross),
            ("proyeccion u sobre v", _3d_proj_u_on_v),
            ("escala k*v", _3d_scale),
            ("distancia p1-p2", _3d_dist),
            ("modo: " + _in_mode_label() + " (cambiar)", _toggle_mode),
        ]
        fn=_menu("Vectores 3D (" + _in_mode_label() + ")", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

# ===== app =====
def app():
    items = [
        ("Operaciones 2D", _menu_2d),
        ("Operaciones 3D", _menu_3d),
        ("cambiar modo global", _toggle_mode),
    ]
    while True:
        fn=_menu("Vectores", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

if __name__ == "__main__":
    app()
