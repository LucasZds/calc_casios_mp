# maclaurin.py — Maclaurin y Taylor (solo imprime resultados y snippet py)
# requiere derivadas.py (Parser, d, simp) en el mismo directorio
import math
import derivadas as ds
from ui_py import view_text, view_text_from_string, view_menu

# ===== helpers UI =====
def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _ask_line(label):
    print(label); return input("> ").strip()

def _ask_float(label):
    print(label)
    s = input("> ").strip().replace(",", ".")
    try: return float(s)
    except: return 0.0

def _fmt(x, nd=10):
    iv = int(x)
    if x == iv: return str(iv)
    return ("{:.%dg}" % nd).format(x)

def _normalize_expr(s):
    # Solo para mostrar; el parser acepta ** (lo mapea a ^ internamente).
    return s.replace("**", "^")

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



# ===== util =====
def _fact(n):
    f=1.0; i=2
    while i<=n: f*=i; i+=1
    return f

# ===== eval de expresion (AST de derivadas.py) =====
def _eval_ast(n, x):
    k = n[0]
    if k=="num": return n[1]
    if k=="var": return x
    if k=="add": return _eval_ast(n[1],x) + _eval_ast(n[2],x)
    if k=="sub": return _eval_ast(n[1],x) - _eval_ast(n[2],x)
    if k=="mul": return _eval_ast(n[1],x) * _eval_ast(n[2],x)
    if k=="div":
        b=_eval_ast(n[2],x)
        return _eval_ast(n[1],x)/b if b!=0.0 else float("inf")
    if k=="pow":
        a=_eval_ast(n[1],x); b=_eval_ast(n[2],x)
        try: return a**b
        except: return float("nan")
    if k=="call":
        fn=n[1]; u=_eval_ast(n[2],x)
        try:
            if fn=="sin": return math.sin(u)
            if fn=="cos": return math.cos(u)
            if fn=="tan": return math.tan(u)
            if fn=="exp": return math.exp(u)
            if fn=="ln" or fn=="log": return math.log(u)
            if fn=="sqrt": return math.sqrt(u)
            if fn=="asin": return math.asin(u)
            if fn=="acos": return math.acos(u)
            if fn=="atan": return math.atan(u)
            if fn=="log10": return math.log10(u)
        except:
            return float("nan")
        return 0.0
    return 0.0

# ===== coeficientes a_k =====
def _coeffs_at_a(ast, n, a):
    # a_k = f^(k)(a)/k!
    acoef=[0.0]*(n+1)
    g = ds.simp(ast)
    k=0
    while k<=n:
        val = _eval_ast(g, a)
        acoef[k] = val / _fact(k)
        if k<n:
            g = ds.simp(ds.d(g))
        k+=1
    return acoef

# ===== strings para polinomios y snippet py =====
def _poly_str(a, var="x"):
    # muestra Pn(x) en una sola linea: c0 + c1*var + c2*var^2 + ...
    parts = []
    k = 0
    n = len(a)
    while k < n:
        c = a[k]
        if abs(c) > 1e-15:
            if k == 0:
                parts.append(_fmt(c))
            elif k == 1:
                coef = "" if abs(c - 1.0) < 1e-12 else _fmt(c) + "*"
                parts.append(coef + var)
            else:
                coef = "" if abs(c - 1.0) < 1e-12 else _fmt(c) + "*"
                parts.append(coef + var + "^" + str(k))
        k += 1
    return " + ".join(parts) if parts else "0"


def _poly_py_expr(a, var="x"):
    # expresion Python: usa ** para potencia
    parts = []
    k = 0
    n = len(a)
    while k < n:
        c = a[k]
        if abs(c) > 1e-15:
            if k == 0:
                parts.append(_fmt(c))
            elif k == 1:
                parts.append(_fmt(c) + "*" + var)
            else:
                parts.append(_fmt(c) + "*" + var + "**" + str(k))
        k += 1
    return " + ".join(parts) if parts else "0"


# ===== pantallas =====
def _maclaurin():
    s_in = _ask_line("f(x):")
    s_norm = _normalize_expr(s_in)
    n = int(_ask_float("grado n (0..8):"))
    if n<0: n=0
    if n>8: n=8
    try:
        ast = ds.Parser(s_norm).parse()
    except Exception as e:
        view_text_from_string("Error de parseo", str(e)); _pause(); return

    acoef = _coeffs_at_a(ast, n, 0.0)

    # Mostrar resultados y snippet
    lineas = []
    lineas.append("f(x) = " + s_norm)
    lineas.append("coef a_k = [" + ", ".join(_fmt(c) for c in acoef) + "]")
    lineas.append("P"+str(n)+"(x) = " + _poly_str(acoef, "x"))
    lineas.append("Python:")
    lineas.append("Pn = " + _poly_py_expr(acoef, "x"))
    view_text("Maclaurin", lineas)

    # Evaluacion opcional
    x = _ask_float("x (Enter=0):")
    # Horner con var = x
    p=0.0
    i=len(acoef)-1
    while i>=0:
        p = p*x + acoef[i]
        i-=1
    real = _eval_ast(ast, x)
    err = abs(p-real)/(abs(real)+1e-12)

    view_text("Evaluacion", [
        "x = " + _fmt(x),
        "aprox = " + _fmt(p),
        "real  = " + _fmt(real),
        "err   = " + _fmt(err),
    ])
    _pause()

def _taylor_en_a():
    s_in = _ask_line("f(x):")
    s_norm = _normalize_expr(s_in)
    a = _ask_float("punto a:")
    n = int(_ask_float("grado n (0..8):"))
    if n<0: n=0
    if n>8: n=8
    try:
        ast = ds.Parser(s_norm).parse()
    except Exception as e:
        view_text_from_string("Error de parseo", str(e)); _pause(); return

    acoef = _coeffs_at_a(ast, n, a)

    var = "(x-"+_fmt(a)+")" if a!=0.0 else "x"

    lineas = []
    lineas.append("f(x) = " + s_norm)
    lineas.append("coef a_k = [" + ", ".join(_fmt(c) for c in acoef) + "]")
    lineas.append("Pn en a="+_fmt(a)+": " + _poly_str(acoef, var))
    lineas.append("Python:")
    lineas.append("Pn = " + _poly_py_expr(acoef, var))
    view_text("Taylor en a", lineas)

    # Evaluacion opcional
    x = _ask_float("x (Enter=a):")
    usex = x if (x!=0.0 or a==0.0) else a
    h = usex - a
    p=0.0
    i=len(acoef)-1
    while i>=0:
        p = p*h + acoef[i]
        i-=1
    real = _eval_ast(ast, usex)
    err = abs(p-real)/(abs(real)+1e-12)

    view_text("Evaluacion", [
        "a = " + _fmt(a) + "   x = " + _fmt(usex) + "   h = x-a = " + _fmt(h),
        "aprox = " + _fmt(p),
        "real  = " + _fmt(real),
        "err   = " + _fmt(err),
    ])
    _pause()

# ===== Derivadas: mostrar SNIPPETS de funciones Python =====

def _pythonize_expr(expr):
    # Convierte to_str a Python: ^ -> ** y funciones -> math.*
    expr = expr.replace("^", "**")
    repl = [
        ("log10(", "math.log10("),
        ("asin(",  "math.asin("),
        ("acos(",  "math.acos("),
        ("atan(",  "math.atan("),
        ("sinh(",  "math.sinh("),
        ("cosh(",  "math.cosh("),
        ("tanh(",  "math.tanh("),
        ("sqrt(",  "math.sqrt("),
        ("exp(",   "math.exp("),
        ("ln(",    "math.log("),   # ln -> math.log
        ("sin(",   "math.sin("),
        ("cos(",   "math.cos("),
        ("tan(",   "math.tan("),
    ]
    for a, b in repl:
        expr = expr.replace(a, b)
    return expr

def _derivada_adelante():
    code_lines = [
        "def d_adelante(f, x, h=1e-6):",
        "    \"\"\"Derivada por diferencias hacia adelante.\"\"\"",
        "    return (f(x + h) - f(x)) / h",
        "",
    ]
    view_text("Snippet: derivada adelante", code_lines)
    _pause()

def _derivada_atras():
    code_lines = [
        "def d_atras(f, x, h=1e-6):",
        "    \"\"\"Derivada por diferencias hacia atras.\"\"\"",
        "    return (f(x) - f(x - h)) / h",
        "",
    ]
    view_text("Snippet: derivada atras", code_lines)
    _pause()

def _derivada_centrada():
    code_lines = [
        "def d_centrada(f, x, h=1e-6):",
        "    \"\"\"Derivada por diferencias centradas (O(h**2)).\"\"\"",
        "    return (f(x + h) - f(x - h)) / (2*h)",
        "",
    ]
    view_text("Snippet: derivada centrada", code_lines)
    _pause()

def _derivada_real():
    s_in = _ask_line("f(x) (para derivada simbolica):")
    s_norm = _normalize_expr(s_in)
    try:
        ast = ds.Parser(s_norm).parse()
        d_ast = ds.simp(ds.d(ast))
        py_expr = _pythonize_expr(ds.to_str(d_ast))
        code_lines = [
            "import math",
            "",
            "def fprime(x):",
            "    return " + py_expr,
            "",
        ]
        view_text("Snippet: derivada real (simbolica)", code_lines)
    except Exception as e:
        view_text_from_string("Error", "no pude derivar: " + str(e))
    _pause()

def _ayuda():
    doc = """Pn Maclaurin: a=0; Taylor: a general.
a_k = f^(k)(a)/k!
Entrada: sin cos tan exp ln sqrt asin acos atan log10, ^ o **.
Salida: coeficientes, polinomio en una linea y snippet Python (Pn = ...).
Evaluacion: calcula aprox, real y error relativo.

Derivadas (snippets):
- Adelante:   d_adelante(f, x, h)
- Atras:      d_atras(f, x, h)
- Centrada:   d_centrada(f, x, h)
- Real:       fprime(x) a partir de la derivada simbolica
"""
    view_text_from_string("Ayuda", doc)

# ===== app =====
def app():
    items = [
        ("Maclaurin f(x), grado n", _maclaurin),
        ("Taylor en a, grado n", _taylor_en_a),
        ("Derivada centrada", _derivada_centrada),
        ("Derivada adelante", _derivada_adelante),
        ("Derivada atras", _derivada_atras),
        ("Derivada real", _derivada_real),
        ("ayuda", _ayuda),
    ]
    while True:
        fn=_menu("Maclaurin/Taylor", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

if __name__ == "__main__":
    app()
