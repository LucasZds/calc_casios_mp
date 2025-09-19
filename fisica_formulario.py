# ==== fisica_formulario.py ====
from ui_py import view_menu, view_text, view_text_from_string

from despeje import Parser as DParser
from despeje import isolate_x, Sub, Num, simp, to_str, contains_x, _safe_replace_name
_has_x = contains_x  # si lo querés con ese alias

# --- helpers UI minimos ---
def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _ask_line(label):
    print(label); return input("> ").strip()

def _fmt(x, nd=10):
    iv = int(x)
    if x == iv: return str(iv)
    return ("{:.%dg}" % nd).format(x)

# --- motorcito: elegir formula y despejar variable objetivo ---
def _despejar_desde_formula(eq):
    view_text("Formula", [eq, " "])
    var = _ask_line("variable a aislar (ej: v, a, h, R, x):").strip()
    if not var:
        return

    # split L=R
    try:
        Ls, Rs = eq.split("=", 1)
    except:
        view_text_from_string("Error", "Ecuacion invalida"); _pause(); return

    # Evitar choque con la x original: si la variable objetivo NO es 'x',
    # renombramos la x original a 'Xpos' y mapeamos la variable objetivo -> 'x'
    if var != "x":
        Ls_tmp = _safe_replace_name(Ls, "x", "Xpos")
        Rs_tmp = _safe_replace_name(Rs, "x", "Xpos")
        Ls_x   = _safe_replace_name(Ls_tmp, var, "x")
        Rs_x   = _safe_replace_name(Rs_tmp, var, "x")
    else:
        Ls_x, Rs_x = Ls, Rs

    # parseo
    try:
        L = DParser(Ls_x).parse()
        R = DParser(Rs_x).parse()
    except Exception as e:
        view_text_from_string("Error", "Parseo: " + str(e)); _pause(); return

    # decidir qué lado pasa al aislador
    try:
        hasL = _has_x(L)
        hasR = _has_x(R)

        if hasL and not hasR:
            left, right = L, R
        elif hasR and not hasL:
            left, right = R, L
        elif hasL and hasR:
            # mover todo a la izquierda: (L - R) = 0
            left  = Sub(L, R)
            right = Num(0.0)
        else:
            view_text_from_string("Resultado", "La variable objetivo no aparece en la ecuacion.")
            _pause(); return

        ok, lf, sol = isolate_x(left, right)
        if ok and lf[0] == "var":
            expr = to_str(simp(sol))
            # revertir mapeos para mostrar
            if var != "x":
                expr = _safe_replace_name(expr, "x", var)   # la x del aislador vuelve a 'var'
                expr = _safe_replace_name(expr, "Xpos", "x")  # la x original vuelve a 'x'

            lineas = [
                "Ecuacion: " + eq,
                var + " = " + expr,
                "",
                "Nota: si el enunciado usa x y x0, recorda que x es la posicion y x0 otra (p. inicial)."
            ]
            view_text("Despeje", lineas)
        else:
            view_text_from_string("Resultado", "Operacion no soportada por el aislador.")
    except Exception as e:
        view_text_from_string("Error", str(e))
    _pause()

# --- catalogo liviano de formulas (local -> GC al salir) ---
def _data_formulas():
    # (texto para menú, ecuacion como string)
    # Usa ^ o ** indistinto; el parser mapea ** a ^
    return {
        "Cinematica": [
            ("MRU: x = x0 + v*t",            "x = x0 + v*t"),
            ("MRUA: v = v0 + a*t",           "v = v0 + a*t"),
            ("MRUA: x = x0 + v0*t + 1/2 a t^2", "x = x0 + v0*t + 0.5*a*t^2"),
            ("MRUA: v^2 = v0^2 + 2 a (x-x0)",   "v^2 = v0^2 + 2*a*(x-x0)"),
        ],
        "Energia / Trabajo": [
            ("E mecanica: 1/2 m v^2 + m g h = const", "0.5*m*v^2 + m*g*h = E"),
            ("Trabajo-Potencia: P = F*v",             "P = F*v"),
            ("Trabajo: W = F*d*cos(th)",              "W = F*d*cos(th)"),
        ],
        "Circular / Rodadura": [
            ("Contacto cima: v^2 = g*R",              "v^2 = g*R"),
            ("Rodadura I=b*m*r^2: E = m g h = m g (2R) + 1/2 m (1+b) v^2",
             "m*g*h = m*g*(2*R) + 0.5*m*(1+b)*v^2"),
        ],
        "Atwood / Poleas": [
            ("Atwood ideal: a = (m2-m1) g / (m1+m2)", "a = (m2-m1)*g/(m1+m2)"),
            ("Atwood con inercia: a = (m2-m1)g/(m1+m2+I/R^2)", "a = (m2-m1)*g/(m1+m2+I/R^2)"),
        ],
        "Colisiones 1D": [
            ("Elastica (v1')", "v1p = ((m1-m2)/(m1+m2))*v1 + (2*m2/(m1+m2))*v2"),
            ("Elastica (v2')", "v2p = (2*m1/(m1+m2))*v1 + ((m2-m1)/(m1+m2))*v2"),
            ("Inelastica total: vf", "vf = (m1*v1 + m2*v2)/(m1+m2)"),
        ],
        "Pendulo simple": [
            ("Periodo chico angulo: T = 2*pi*sqrt(L/g)",    "T = 2*pi*sqrt(L/g)"),
        ],
    }

# --- submenús ---
def _menu_categoria(nombre, pares):
    # pares: lista de (texto, ecuacion)
    etiquetas=[]; i=0
    while i<len(pares):
        etiquetas.append(pares[i][0])
        i+=1
    while True:
        sel = view_menu(nombre, etiquetas)
        if sel is None: return
        if 0 <= sel < len(pares):
            _despejar_desde_formula(pares[sel][1])

def app():
    data = _data_formulas()
    cats = []
    for k in data:  # sin enumerate
        cats.append(k)
    # construir lineas
    lineas=[]; i=0
    while i<len(cats):
        lineas.append(cats[i]); i+=1
    while True:
        sel = view_menu("Fisica - Formulario", lineas)
        if sel is None: return
        if 0 <= sel < len(cats):
            nombre = cats[sel]
            _menu_categoria(nombre, data[nombre])

# opcional: si queres probar suelto
if __name__ == "__main__":
    app()
