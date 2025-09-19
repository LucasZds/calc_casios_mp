# integrales.py — indefinidas (con pasos) y definidas (simbolico o numerico)
import math
import derivadas as ds  # usamos Parser, simp, to_str y el AST
from ui_py import view_text, view_text_from_string, view_menu

# ===== UI helpers =====
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
    iv=int(x)
    if x == iv: return str(iv)
    return ("{:.%dg}"%nd).format(x)

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



# ===== atajos AST (del modulo derivadas) =====
Num=ds.Num; Var=ds.Var; Add=ds.Add; Sub=ds.Sub; Mul=ds.Mul; Div=ds.Div
Pow=ds.Pow; Call=ds.Call

def is_num(n): return n[0]=="num"
def num_val(n): return n[1]

# -------- helpers de patrones --------
def _match_linear_x(t):
    # intenta t == a*x + b  (a!=0). Devuelve (ok,a,b)
    k=t[0]
    if k=="var": return (True, 1.0, 0.0)
    if k=="mul":
        a1=is_num(t[1]); a2=is_num(t[2])
        if a1 and t[2][0]=="var": return (True, num_val(t[1]), 0.0)
        if a2 and t[1][0]=="var": return (True, num_val(t[2]), 0.0)
    if k=="add":
        ok,a,b = _match_linear_x(t[1])
        if ok and is_num(t[2]): return (True, a, b+num_val(t[2]))
        ok,a,b = _match_linear_x(t[2])
        if ok and is_num(t[1]): return (True, a, b+num_val(t[1]))
    if k=="sub":
        left,right=t[1],t[2]
        ok,a,b=_match_linear_x(left)
        if ok and is_num(right): return (True, a, b-num_val(right))
        ok,a,b=_match_linear_x(right)
        if ok and is_num(left):  return (True, -a, num_val(left)+(-b))
    return (False, 0.0, 0.0)

def _is_one_plus_x2(t):
    if t[0]=="add":
        a,b=t[1],t[2]
        if is_num(a) and num_val(a)==1.0 and b[0]=="pow" and b[1][0]=="var" and is_num(b[2]) and num_val(b[2])==2.0:
            return True
        if is_num(b) and num_val(b)==1.0 and a[0]=="pow" and a[1][0]=="var" and is_num(a[2]) and num_val(a[2])==2.0:
            return True
    return False

def _is_sqrt_one_minus_x2(t):
    if t[0]=="call" and t[1]=="sqrt":
        u=t[2]
        if u[0]=="sub" and is_num(u[1]) and num_val(u[1])==1.0:
            p=u[2]
            if p[0]=="pow" and p[1][0]=="var" and is_num(p[2]) and num_val(p[2])==2.0:
                return True
    return False

# ===== integrador simbolico basico (sin pasos) =====
def _int(n):
    n = ds.simp(n)
    k = n[0]
    if k=="num": return Mul(n, Var())
    if k=="var": return Div(Pow(Var(), Num(2.0)), Num(2.0))
    if k=="add": return Add(_int(n[1]), _int(n[2]))
    if k=="sub": return Sub(_int(n[1]), _int(n[2]))
    if k=="mul":
        a, b = n[1], n[2]
        if is_num(a):  return Mul(a, _int(b))
        if is_num(b):  return Mul(b, _int(a))
    if k=="pow":
        base, expo = n[1], n[2]
        ok,a,_b = _match_linear_x(base)
        if ok and is_num(expo):
            p = num_val(expo)
            if p == -1.0:
                return Div(Call("ln", Call("abs", base)), Num(a))
            else:
                return Div(Pow(base, Add(expo, Num(1.0))), Mul(Num(a), Add(expo, Num(1.0))))
        if base[0]=="var" and is_num(expo):
            p = num_val(expo)
            if p == -1.0:
                return Call("ln", Call("abs", Var()))
            else:
                return Div(Pow(Var(), Add(expo, Num(1.0))), Add(expo, Num(1.0)))
    if k=="div" and is_num(n[1]) and num_val(n[1])==1.0 and _is_one_plus_x2(n[2]):
        return Call("atan", Var())
    if k=="div" and is_num(n[1]) and num_val(n[1])==1.0 and _is_sqrt_one_minus_x2(n[2]):
        return Call("asin", Var())
    if k=="call":
        fn, arg = n[1], n[2]
        ok,a,_b = _match_linear_x(arg)
        if ok and a != 0.0:
            if fn=="exp":  return Div(Call("exp", arg), Num(a))
            if fn=="sin":  return Div(Mul(Num(-1.0), Call("cos", arg)), Num(a))
            if fn=="cos":  return Div(Call("sin", arg), Num(a))
            if fn=="tan":  return Div(Mul(Num(-1.0), Call("ln", Call("abs", Call("cos", arg)))), Num(a))
    if k=="div" and is_num(n[1]) and num_val(n[1])==1.0:
        ok,a,_b = _match_linear_x(n[2])
        if ok and a != 0.0:
            return Div(Call("ln", Call("abs", n[2])), Num(a))
    raise Exception("no soportado")

# ===== integrador con pasos =====
def _int_explain(n, steps):
    n = ds.simp(n)
    k = n[0]
    if k=="num":
        steps.append("regla: ∫ k dx = k*x")
        return Mul(n, Var())
    if k=="var":
        steps.append("regla: ∫ x dx = x^2/2")
        return Div(Pow(Var(), Num(2.0)), Num(2.0))
    if k=="add":
        steps.append("linealidad: ∫(u+v) = ∫u + ∫v")
        u = _int_explain(n[1], steps)
        v = _int_explain(n[2], steps)
        return Add(u, v)
    if k=="sub":
        steps.append("linealidad: ∫(u-v) = ∫u - ∫v")
        u = _int_explain(n[1], steps)
        v = _int_explain(n[2], steps)
        return Sub(u, v)
    if k=="mul":
        a, b = n[1], n[2]
        if is_num(a):
            steps.append("constante: k * ∫u dx")
            return Mul(a, _int_explain(b, steps))
        if is_num(b):
            steps.append("constante: k * ∫u dx")
            return Mul(b, _int_explain(a, steps))
    if k=="pow":
        base, expo = n[1], n[2]
        ok,a,_b = _match_linear_x(base)
        if ok and is_num(expo):
            p = num_val(expo)
            if p == -1.0:
                steps.append("regla: ∫ 1/(a*x+b) dx = (1/a)*ln|a*x+b|")
                return Div(Call("ln", Call("abs", base)), Num(a))
            else:
                steps.append("regla: ∫ (a*x+b)^p dx = (a*x+b)^(p+1)/(a*(p+1))")
                return Div(Pow(base, Add(expo, Num(1.0))), Mul(Num(a), Add(expo, Num(1.0))))
        if base[0]=="var" and is_num(expo):
            p = num_val(expo)
            if p == -1.0:
                steps.append("regla: ∫ 1/x dx = ln|x|")
                return Call("ln", Call("abs", Var()))
            else:
                steps.append("regla: ∫ x^p dx = x^(p+1)/(p+1)")
                return Div(Pow(Var(), Add(expo, Num(1.0))), Add(expo, Num(1.0)))
    if k=="div" and is_num(n[1]) and num_val(n[1])==1.0 and _is_one_plus_x2(n[2]):
        steps.append("regla: ∫ 1/(1+x^2) dx = atan(x)")
        return Call("atan", Var())
    if k=="div" and is_num(n[1]) and num_val(n[1])==1.0 and _is_sqrt_one_minus_x2(n[2]):
        steps.append("regla: ∫ 1/√(1-x^2) dx = asin(x)")
        return Call("asin", Var())
    if k=="call":
        fn, arg = n[1], n[2]
        ok,a,_b = _match_linear_x(arg)
        if ok and a != 0.0:
            if fn=="exp":
                steps.append("regla: ∫ exp(a*x+b) dx = (1/a)*exp(a*x+b)")
                return Div(Call("exp", arg), Num(a))
            if fn=="sin":
                steps.append("regla: ∫ sin(a*x+b) dx = -(1/a)*cos(a*x+b)")
                return Div(Mul(Num(-1.0), Call("cos", arg)), Num(a))
            if fn=="cos":
                steps.append("regla: ∫ cos(a*x+b) dx = (1/a)*sin(a*x+b)")
                return Div(Call("sin", arg), Num(a))
            if fn=="tan":
                steps.append("regla: ∫ tan(a*x+b) dx = -(1/a)*ln|cos(a*x+b)|")
                return Div(Mul(Num(-1.0), Call("ln", Call("abs", Call("cos", arg)))), Num(a))
    if k=="div" and is_num(n[1]) and num_val(n[1])==1.0:
        ok,a,_b = _match_linear_x(n[2])
        if ok and a != 0.0:
            steps.append("regla: ∫ 1/(a*x+b) dx = (1/a)*ln|a*x+b|")
            return Div(Call("ln", Call("abs", n[2])), Num(a))
    raise Exception("no soportado")

# ===== evaluador numerico para definida =====
def _eval_ast(n, x):
    k=n[0]
    if k=="num": return n[1]
    if k=="var": return x
    if k=="add": return _eval_ast(n[1],x)+_eval_ast(n[2],x)
    if k=="sub": return _eval_ast(n[1],x)-_eval_ast(n[2],x)
    if k=="mul": return _eval_ast(n[1],x)*_eval_ast(n[2],x)
    if k=="div":
        b=_eval_ast(n[2],x)
        return _eval_ast(n[1],x)/b if b!=0.0 else float("inf")
    if k=="pow":
        a=_eval_ast(n[1],x); b=_eval_ast(n[2],x)
        try: return a**b
        except: return float("nan")
    if k=="call":
        fn=n[1]; u=_eval_ast(n[2],x)
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
        if fn=="abs": return abs(u)
    return 0.0

def _int_def_num(ast, a, b, N):
    if N <= 0: N = 10
    h = (b - a) / N
    if N % 2 == 0:  # Simpson
        s0 = _eval_ast(ast, a) + _eval_ast(ast, b)
        s1 = 0.0; s2 = 0.0
        i = 1
        while i < N:
            x = a + i*h
            if i % 2 == 1: s1 += _eval_ast(ast, x)
            else:          s2 += _eval_ast(ast, x)
            i += 1
        return (h/3.0) * (s0 + 4.0*s1 + 2.0*s2)
    else:  # Trapecios
        s = (_eval_ast(ast, a) + _eval_ast(ast, b)) * 0.5
        i = 1
        while i < N:
            s += _eval_ast(ast, a + i*h); i += 1
        return h * s

# ===== pantallas =====
def _indef_res():
    s = _ask_line("f(x) para integrar:")
    try:
        ast = ds.Parser(s).parse()
        F = ds.simp(_int(ast))
        view_text("Indefinida (resultado)", [
            "∫ f dx =",
            ds.to_str(F) + " + C",
        ])
    except Exception as e:
        view_text_from_string("No pude integrar", str(e))
    _pause()

def _indef_pasos():
    s = _ask_line("f(x) para integrar:")
    try:
        ast = ds.Parser(s).parse()
        pasos = []
        F = ds.simp(_int_explain(ast, pasos))
        lineas = ["Pasos:"]
        for line in pasos:
            lineas.append("- " + line)
        lineas.append("Resultado:")
        lineas.append(ds.to_str(F) + " + C")
        view_text("Indefinida (pasos)", lineas)
    except Exception as e:
        view_text_from_string("No pude integrar", str(e))
    _pause()

def _def_auto():
    s = _ask_line("f(x):")
    a = _ask_float("a:")
    b = _ask_float("b:")
    N = int(_ask_float("N (si cae a numerico):"))
    try:
        ast = ds.Parser(s).parse()
        # intenta simbolico
        try:
            F = ds.simp(_int(ast))
            Fb = _eval_ast(F, b); Fa = _eval_ast(F, a)
            view_text("Definida (simbolico)", [
                "F(x) = " + ds.to_str(F),
                "F(b)-F(a) = " + _fmt(Fb - Fa),
            ])
        except Exception:
            # fallback numerico
            val = _int_def_num(ast, a, b, N)
            view_text("Definida (numerico)", [
                "N = " + str(N),
                "∫[" + _fmt(a) + ", " + _fmt(b) + "] f(x) dx ≈ " + _fmt(val),
            ])
    except Exception as e:
        view_text_from_string("No pude integrar", str(e))
    _pause()

def _ayuda():
    doc = """Reglas soportadas:
    - x^n, 1/x, (a*x+b)^n, 1/(a*x+b)
    - exp/sin/cos/tan con lineal adentro
    - 1/(1+x^2), 1/sqrt(1-x^2)
    Definida:
    - Intenta simbólico; si no, Simpson/Trapecios (según N par/impar).
    Notas:
    - El parser de derivadas acepta ^ o ** para potencias.
    """
    view_text_from_string("Ayuda", doc)

# ===== app =====
def app():
    items = [
        ("Indefinida (resultado)", _indef_res),
        ("Indefinida (pasos)", _indef_pasos),
        ("Definida a..b (auto)", _def_auto),
        ("ayuda", _ayuda),
    ]
    while True:
        fn=_menu("Integrales", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            view_text_from_string("Error", str(e)); _pause()

if __name__ == "__main__":
    app()
