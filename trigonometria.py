# trigonometria.py — funciones, conversiones y triangulos
import math
# ===== UI basica (7 lineas) =====
from ui_py import view_text, view_text_from_string, view_menu

# ======= helpers UI =======
def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _ask_float(label):
    print(label)
    s = input("> ").strip().replace(",", ".")
    try: return float(s)
    except: return 0.0

def _fmt(x, nd=10):
    iv = int(x)
    if x == iv: return str(iv)
    return ("{:.%dg}"%nd).format(x)

def _menu(title, items, cols=None, lpp=None):
    # items: [(texto, funcion), ...]
    textos = []
    i = 0
    while i < len(items):
        textos.append(items[i][0])   # sin "[i] " aca
        i += 1
    sel = view_menu(title, textos, cols=cols, lines_per_screen=lpp)
    if sel is None:
        return None
    return items[sel][1]



# ======= modo angulos (global) =======
# True = rad, False = deg
_MODE_RAD = True

def _set_mode(rad=True):
    global _MODE_RAD
    _MODE_RAD = bool(rad)

def _toggle_mode():
    global _MODE_RAD
    _MODE_RAD = not _MODE_RAD

def _in_mode_label():
    return "rad" if _MODE_RAD else "deg"

def _to_rad(x):
    return x if _MODE_RAD else (x * math.pi / 180.0)

def _from_rad(r):
    return r if _MODE_RAD else (r * 180.0 / math.pi)

def _norm_angle(r):
    # normaliza en rad a [0, 2pi)
    tau = 2.0 * math.pi
    r = r % tau
    if r < 0: r += tau
    return r

# ======= Funciones trig =======
def _fn_sin():
    x = _ask_float("x (" + _in_mode_label() + "):")
    r = _to_rad(x)
    view_text("sin(x)", [
        "modo: " + _in_mode_label(),
        "x = " + _fmt(x),
        "sin(x) = " + _fmt(math.sin(r)),
    ])
    _pause()

def _fn_cos():
    x = _ask_float("x (" + _in_mode_label() + "):")
    r = _to_rad(x)
    view_text("cos(x)", [
        "modo: " + _in_mode_label(),
        "x = " + _fmt(x),
        "cos(x) = " + _fmt(math.cos(r)),
    ])
    _pause()

def _fn_tan():
    x = _ask_float("x (" + _in_mode_label() + "):")
    r = _to_rad(x)
    view_text("tan(x)", [
        "modo: " + _in_mode_label(),
        "x = " + _fmt(x),
        "tan(x) = " + _fmt(math.tan(r)),
    ])
    _pause()

def _fn_asin():
    y = _ask_float("y ([-1,1]):")
    if y < -1.0 or y > 1.0:
        view_text_from_string("asin(y)", "fuera de dominio")
        _pause(); return
    r = math.asin(y)
    view_text("asin(y)", [
        "y = " + _fmt(y),
        "asin(y) = " + _fmt(_from_rad(r)),
        "unidad: " + _in_mode_label(),
    ])
    _pause()

def _fn_acos():
    y = _ask_float("y ([-1,1]):")
    if y < -1.0 or y > 1.0:
        view_text_from_string("acos(y)", "fuera de dominio")
        _pause(); return
    r = math.acos(y)
    view_text("acos(y)", [
        "y = " + _fmt(y),
        "acos(y) = " + _fmt(_from_rad(r)),
        "unidad: " + _in_mode_label(),
    ])
    _pause()

def _fn_atan():
    y = _ask_float("y (real):")
    r = math.atan(y)
    view_text("atan(y)", [
        "y = " + _fmt(y),
        "atan(y) = " + _fmt(_from_rad(r)),
        "unidad: " + _in_mode_label(),
    ])
    _pause()

def _menu_funciones():
    while True:
        items = [
            ("sin(x)", _fn_sin),
            ("cos(x)", _fn_cos),
            ("tan(x)", _fn_tan),
            ("asin(y)", _fn_asin),
            ("acos(y)", _fn_acos),
            ("atan(y)", _fn_atan),
            ("modo: " + _in_mode_label() + " (cambiar)", _toggle_mode),
        ]
        fn = _menu("Funciones (" + _in_mode_label() + ")", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

# ======= Angulos =======
def _deg2rad():
    d = _ask_float("grados:")
    view_text("deg -> rad", [
        "deg = " + _fmt(d),
        "rad = " + _fmt(d * math.pi / 180.0),
    ])
    _pause()

def _rad2deg():
    r = _ask_float("rad:")
    view_text("rad -> deg", [
        "rad = " + _fmt(r),
        "deg = " + _fmt(r * 180.0 / math.pi),
    ])
    _pause()

def _normalizar():
    x = _ask_float("angulo (" + _in_mode_label() + "):")
    r = _norm_angle(_to_rad(x))
    out = _from_rad(r)
    view_text("normalizar", [
        "modo: " + _in_mode_label(),
        "entrada = " + _fmt(x),
        "norm = " + _fmt(out) + " " + _in_mode_label(),
    ])
    _pause()

def _menu_angulos():
    items = [
        ("deg -> rad", _deg2rad),
        ("rad -> deg", _rad2deg),
        ("normalizar 0..2pi / 0..360", _normalizar),
        ("cambiar modo aqui", _toggle_mode),
    ]
    while True:
        fn = _menu("Angulos (" + _in_mode_label() + ")", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

# ======= Triangulos =======
def _clamp(x, a, b):
    return a if x < a else b if x > b else x

def _ang_line(name, r):
    return "{} = {} {}".format(name, _fmt(_from_rad(r)), _in_mode_label())

# Rectangulo (C = 90°)
def _rect_catetos():
    a = _ask_float("cateto a:")
    b = _ask_float("cateto b:")
    if a < 0 or b < 0:
        view_text_from_string("Rectangulo", "longitudes invalidas"); _pause(); return
    c = math.hypot(a, b)
    A = math.atan2(a, b)  # opuesto/adyacente
    B = math.atan2(b, a)
    view_text("Rectangulo: catetos -> hip y angulos", [
        "a = " + _fmt(a) + "   b = " + _fmt(b),
        "c = " + _fmt(c),
        _ang_line("A", A),
        _ang_line("B", B),
    ])
    _pause()

def _rect_hip_cat():
    c = _ask_float("hipotenusa c:")
    a = _ask_float("cateto a:")
    if c <= 0 or a < 0 or a >= c:
        view_text_from_string("Rectangulo", "datos invalidos"); _pause(); return
    b = math.sqrt(c*c - a*a)
    A = math.asin(a / c)
    B = math.asin(b / c)
    view_text("Rectangulo: hip + cateto -> resto", [
        "c = " + _fmt(c) + "   a = " + _fmt(a),
        "b = " + _fmt(b),
        _ang_line("A", A),
        _ang_line("B", B),
    ])
    _pause()

def _rect_A_y_opuesto():
    A = _to_rad(_ask_float("angulo A (" + _in_mode_label() + "):"))
    a = _ask_float("cateto opuesto a:")
    if not (0 < A < math.pi/2):
        view_text_from_string("Rectangulo", "A debe ser (0,90)"); _pause(); return
    c = a / math.sin(A)
    b = c * math.cos(A)
    B = math.pi/2 - A
    view_text("Rectangulo: A + opuesto a -> resto", [
        "a = " + _fmt(a),
        "b = " + _fmt(b),
        "c = " + _fmt(c),
        _ang_line("B", B),
    ])
    _pause()

def _rect_A_y_ady():
    A = _to_rad(_ask_float("angulo A (" + _in_mode_label() + "):"))
    b = _ask_float("cateto adyacente b:")
    if not (0 < A < math.pi/2):
        view_text_from_string("Rectangulo", "A debe ser (0,90)"); _pause(); return
    c = b / math.cos(A)
    a = c * math.sin(A)
    B = math.pi/2 - A
    view_text("Rectangulo: A + adyacente b -> resto", [
        "b = " + _fmt(b),
        "a = " + _fmt(a),
        "c = " + _fmt(c),
        _ang_line("B", B),
    ])
    _pause()

def _rect_A_y_hip():
    A = _to_rad(_ask_float("angulo A (" + _in_mode_label() + "):"))
    c = _ask_float("hipotenusa c:")
    if not (0 < A < math.pi/2) or c <= 0:
        view_text_from_string("Rectangulo", "datos invalidos"); _pause(); return
    a = c * math.sin(A)
    b = c * math.cos(A)
    B = math.pi/2 - A
    view_text("Rectangulo: A + hipotenusa c -> resto", [
        "c = " + _fmt(c),
        "a = " + _fmt(a),
        "b = " + _fmt(b),
        _ang_line("B", B),
    ])
    _pause()

# Ley de senos
def _senos_ASA_AAS():
    # dato: A, B, a (lado opuesto a A)
    A = _to_rad(_ask_float("A (" + _in_mode_label() + "):"))
    B = _to_rad(_ask_float("B (" + _in_mode_label() + "):"))
    a = _ask_float("a:")
    C = math.pi - A - B
    if a <= 0 or C <= 0:
        view_text_from_string("Ley de senos", "sin solucion"); _pause(); return
    b = a * math.sin(B) / math.sin(A)
    c = a * math.sin(C) / math.sin(A)
    view_text("Ley de senos: ASA/AAS", [
        "a = " + _fmt(a),
        "b = " + _fmt(b),
        "c = " + _fmt(c),
        _ang_line("C", C),
    ])
    _pause()

def _senos_SSA():
    # dato: A, a, b (A opuesto a, B opuesto b)
    A = _to_rad(_ask_float("A (" + _in_mode_label() + "):"))
    a = _ask_float("a:")
    b = _ask_float("b:")
    if a <= 0 or b <= 0:
        view_text_from_string("Ley de senos", "sin solucion"); _pause(); return
    s = b * math.sin(A) / a
    if s < -1.0 or s > 1.0:
        view_text_from_string("Ley de senos", "sin solucion"); _pause(); return

    B1 = math.asin(_clamp(s, -1.0, 1.0))
    B2 = math.pi - B1

    out = []
    for B in (B1, B2):
        C = math.pi - A - B
        if C > 0:
            c = a * math.sin(C) / math.sin(A)
            out.append((B, C, c))

    if not out:
        view_text_from_string("Ley de senos", "sin solucion")
    else:
        lineas = []
        i = 0
        n = len(out)
        while i < n:
            B, C, c = out[i]
            lineas.append("sol " + str(i + 1) + ":")
            lineas.append(_ang_line("B", B))
            lineas.append(_ang_line("C", C))
            lineas.append("c = " + _fmt(c))
            i += 1
        view_text("Ley de senos: SSA", lineas)
    _pause()


# Ley de cosenos
def _cosenos_SSS():
    a = _ask_float("a:"); b = _ask_float("b:"); c = _ask_float("c:")
    if min(a,b,c) <= 0 or a + b <= c or a + c <= b or b + c <= a:
        view_text_from_string("Ley de cosenos", "no forma triangulo"); _pause(); return
    A = math.acos(_clamp((b*b + c*c - a*a)/(2*b*c), -1.0, 1.0))
    B = math.acos(_clamp((a*a + c*c - b*b)/(2*a*c), -1.0, 1.0))
    C = math.pi - A - B
    view_text("Ley de cosenos: SSS", [
        _ang_line("A", A),
        _ang_line("B", B),
        _ang_line("C", C),
    ])
    _pause()

def _cosenos_SAS():
    # dato: a, C, b (C incluido)
    a = _ask_float("a:")
    C = _to_rad(_ask_float("C (" + _in_mode_label() + "):"))
    b = _ask_float("b:")
    if a <= 0 or b <= 0 or not (0 < C < math.pi):
        view_text_from_string("Ley de cosenos", "sin solucion"); _pause(); return
    c2 = a*a + b*b - 2.0*a*b*math.cos(C)
    if c2 <= 0:
        view_text_from_string("Ley de cosenos", "sin solucion"); _pause(); return
    c = math.sqrt(c2)
    A = math.acos(_clamp((b*b + c*c - a*a)/(2*b*c), -1.0, 1.0))
    B = math.pi - A - C
    view_text("Ley de cosenos: SAS", [
        "c = " + _fmt(c),
        _ang_line("A", A),
        _ang_line("B", B),
    ])
    _pause()

def _menu_rect():
    items = [
        ("catetos -> hip y angulos", _rect_catetos),
        ("hip + cateto -> resto", _rect_hip_cat),
        ("A + opuesto a -> resto", _rect_A_y_opuesto),
        ("A + adyacente b -> resto", _rect_A_y_ady),
        ("A + hipotenusa c -> resto", _rect_A_y_hip),
    ]
    while True:
        fn = _menu("Triangulo recto (" + _in_mode_label() + ")", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

def _menu_senos():
    items = [
        ("ASA/AAS: A,B,a -> b,c", _senos_ASA_AAS),
        ("SSA: A,a,b -> (posibles) B,C,c", _senos_SSA),
    ]
    while True:
        fn = _menu("Ley de senos (" + _in_mode_label() + ")", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

def _menu_cosenos():
    items = [
        ("SSS: a,b,c -> A,B,C", _cosenos_SSS),
        ("SAS: a,C,b -> c,A,B", _cosenos_SAS),
    ]
    while True:
        fn = _menu("Ley de cosenos (" + _in_mode_label() + ")", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

def _menu_triangulos():
    items = [
        ("Rectangulo", _menu_rect),
        ("Ley de senos", _menu_senos),
        ("Ley de cosenos", _menu_cosenos),
        ("cambiar modo aqui", _toggle_mode),
    ]
    while True:
        fn = _menu("Triangulos (" + _in_mode_label() + ")", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

# ======= app =======
def app():
    items = [
        ("Funciones", _menu_funciones),
        ("Angulos", _menu_angulos),
        ("Triangulos", _menu_triangulos),
    ]
    while True:
        fn = _menu("Trigonometria", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

if __name__ == "__main__":
    app()
