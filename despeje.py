# despeje.py — aislar x en ecuaciones: x a la izquierda, expresion a la derecha
# Soporta invertir: +, -, *, / por constantes; potencias con exponente constante;
# sqrt(u), exp(u), ln(u); y a^g(x) (base constante !=1 -> usa ln).
# Cualquier identificador distinto de x (y, a, b, k, ...) se considera constante.

import math
# ===== UI =====
from ui_py import view_text, view_text_from_string, view_menu

# ---------- lexer ----------
NUM, ID, OP, LP, RP, END = "NUM","ID","OP","LP","RP","END"

class Tok:
    def __init__(self,t,v=None): self.t=t; self.v=v

# --- helpers para mapear cualquier variable objetivo a 'x' sin romper nombres (x0, exp, cos...) ---

def _is_idch_ext(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or (c == "_") or ("0" <= c <= "9")

def _safe_replace_name(s, name, repl):
    """
    Reemplaza 'name' por 'repl' solo cuando NO está pegado a otros chars de identificador.
    Ej: con name='x' NO toca 'x0', 'exp', 'cos', etc.
    """
    out = []
    i = 0
    n = len(s)
    L = len(name)
    if not name:
        return s
    while i < n:
        if s[i:i+L] == name:
            pre_ok  = (i == 0) or (not _is_idch_ext(s[i-1]))
            post_ok = (i+L >= n) or (not _is_idch_ext(s[i+L]))
            if pre_ok and post_ok:
                out.append(repl)
                i += L
                continue
        out.append(s[i])
        i += 1
    return "".join(out)

def _is_dig(c):  return "0"<=c<="9"

class Lexer:
    def __init__(self,s):
        self.s = s.replace(" ",""); self.n=len(self.s); self.i=0; self.cur=None; self.next()
    def next(self):
        s,n,i=self.s,self.n,self.i
        if i>=n: self.cur=Tok(END); return
        c=s[i]
        if _is_dig(c) or (c=="." and i+1<n and _is_dig(s[i+1])):
            j=i+1
            while j<n and (_is_dig(s[j]) or s[j]=="."): j+=1
            self.cur=Tok(NUM, float(s[i:j] or "0")); self.i=j; return
        if _is_idch_ext(c):
            j=i+1
            while j<n and _is_idch_ext(s[j]): j+=1
            self.cur=Tok(ID, s[i:j]); self.i=j; return
        # mapeo ** -> ^
        if c == "*" and i + 1 < n and s[i+1] == "*":
            self.cur = Tok(OP, "^"); self.i = i + 2; return
        if c in "+-*/^": self.cur=Tok(OP,c); self.i=i+1; return
        if c=="(": self.cur=Tok(LP,"("); self.i=i+1; return
        if c==")": self.cur=Tok(RP,")"); self.i=i+1; return
        self.i=i+1; self.next()

# ---------- AST ----------
def Num(v): return ("num", float(v))
def Var():  return ("var",)           # x
def Sym(n): return ("sym", n)         # constante simbolica: y, a, b, k, ...
def Add(a,b):return ("add",a,b)
def Sub(a,b):return ("sub",a,b)
def Mul(a,b):return ("mul",a,b)
def Div(a,b):return ("div",a,b)
def Pow(a,b):return ("pow",a,b)
def Call(fn,arg): return ("call",fn,arg)  # sin, cos, exp, ln, sqrt...

# ---------- parser ----------
class Parser:
    def __init__(self,s): self.lx=Lexer(s)
    def parse(self): return self.expr()
    def eat(self,t):
        if self.lx.cur.t==t: self.lx.next(); return True
        return False
    def expr(self):
        node=self.term()
        while self.lx.cur.t==OP and self.lx.cur.v in "+-":
            op=self.lx.cur.v; self.lx.next(); rhs=self.term()
            node=Add(node,rhs) if op=="+" else Sub(node,rhs)
        return node
    def term(self):
        node=self.power()
        while self.lx.cur.t==OP and self.lx.cur.v in "*/":
            op=self.lx.cur.v; self.lx.next(); rhs=self.power()
            node=Mul(node,rhs) if op=="*" else Div(node,rhs)
        return node
    def power(self):
        node = self.primary()
        # asociatividad a derecha: x^y^z = x^(y^z)
        if self.lx.cur.t == OP and self.lx.cur.v == "^":
            self.lx.next()
            rhs = self.unary()   # importante: no usar while aquí
            node = Pow(node, rhs)
        return node

    def unary(self):
        if self.lx.cur.t==OP and self.lx.cur.v=="+": self.lx.next(); return self.unary()
        if self.lx.cur.t==OP and self.lx.cur.v=="-": self.lx.next(); return Mul(Num(-1.0), self.unary())
        return self.primary()
    def primary(self):
        tk=self.lx.cur
        if tk.t==NUM: v=tk.v; self.lx.next(); return Num(v)
        if tk.t==ID:
            name=tk.v; self.lx.next()
            if self.eat(LP):
                arg=self.expr(); self.eat(RP); return Call(name,arg)
            if name=="x": return Var()
            if name=="pi": return Num(3.141592653589793)
            if name=="e":  return Num(2.718281828459045)
            return Sym(name)  # cualquier otra id es constante
        if self.eat(LP):
            node=self.expr(); self.eat(RP); return node
        self.lx.next(); return Num(0.0)

# ---------- util ----------
def contains_x(n):
    k=n[0]
    if k=="var": return True
    if k in ("num","sym"): return False
    if k=="call": return contains_x(n[2])
    if k in ("add","sub","mul","div","pow"):
        return contains_x(n[1]) or contains_x(n[2])
    return False

def is_num(n): return n[0]=="num"
def is_sym(n): return n[0]=="sym"
def is_const(n): return n[0] in ("num","sym")

# ---------- simplificacion minima ----------
def _flatten_mul_node(t, coeff, factors):
    k=t[0]
    if k=="num": return (coeff*t[1], factors)
    if k=="mul":
        coeff,factors=_flatten_mul_node(t[1], coeff, factors)
        return _flatten_mul_node(t[2], coeff, factors)
    factors.append(t); return (coeff, factors)

def _rebuild_mul(coeff, factors):
    if coeff==0.0: return Num(0.0)
    res=None
    if abs(coeff-1.0)>1e-12 and abs(coeff+1.0)>1e-12:
        res=Num(coeff)
    elif abs(coeff+1.0)<1e-12:
        res=Mul(Num(-1.0), factors.pop(0)) if factors else Num(-1.0)
    for f in factors:
        res = f if res is None else Mul(res,f)
    return res if res is not None else Num(1.0)

def simp(n):
    k=n[0]
    if k in ("num","var","sym"): return n
    if k=="call": return ("call", n[1], simp(n[2]))
    if k in ("add","sub","mul","div","pow"):
        a=simp(n[1]); b=simp(n[2])
        if a[0]=="num" and b[0]=="num":
            av,bv=a[1],b[1]
            if k=="add": return Num(av+bv)
            if k=="sub": return Num(av-bv)
            if k=="mul": return Num(av*bv)
            if k=="div": return ("div",a,b) if bv==0.0 else Num(av/bv)
            if k=="pow":
                if not (av==0.0 and bv==0.0):
                    try: return Num(av**bv)
                    except: return ("pow",a,b)
        if k=="add":
            if a[0]=="num" and a[1]==0.0: return b
            if b[0]=="num" and b[1]==0.0: return a
            return ("add",a,b)
        if k=="sub":
            if b[0]=="num" and b[1]==0.0: return a
            if a[0]=="num" and a[1]==0.0: return Mul(Num(-1.0), b)
            return ("sub",a,b)
        if k=="mul":
            coeff,factors=_flatten_mul_node(a,1.0,[])
            coeff,factors=_flatten_mul_node(b,coeff,factors)
            if coeff==0.0: return Num(0.0)
            if abs(coeff-1.0)<1e-12 and len(factors)==1: return factors[0]
            return _rebuild_mul(coeff,factors)
        if k=="div":
            if a[0]=="num" and a[1]==0.0: return Num(0.0)
            if b[0]=="num" and b[1]==1.0: return a
            return ("div",a,b)
        if k=="pow":
            if b[0]=="num" and b[1]==1.0: return a
            if b[0]=="num" and b[1]==0.0: return Num(1.0)
            return ("pow",a,b)
    return n

# ---------- pretty print ----------
def prec(n):
    k=n[0]
    return 6 if k in ("num","var","sym") else 5 if k=="call" else 4 if k=="pow" else 3 if k in ("mul","div") else 2

def fmt_num(v):
    iv=int(v)
    return str(iv) if v==iv else "{:.10g}".format(v)

def to_str(n):
    k=n[0]
    if k=="num": return fmt_num(n[1])
    if k=="var": return "x"
    if k=="sym": return n[1]
    if k=="call": return n[1]+"("+to_str(n[2])+")"
    if k in ("add","sub"):
        a,b=n[1],n[2]; sa=to_str(a); sb=to_str(b)
        if prec(a)<prec(n): sa="("+sa+")"
        if prec(b)<prec(n): sb="("+sb+")"
        return sa+("+" if k=="add" else "-")+sb
    if k=="mul":
        a,b=n[1],n[2]
        if a[0]=="num" and abs(a[1]+1.0)<1e-12:
            s=to_str(b)
            if b[0] in ("add","sub"): s="("+s+")"
            return "-"+s
        sa=to_str(a); sb=to_str(b)
        if prec(a)<prec(n): sa="("+sa+")"
        if prec(b)<prec(n): sb="("+sb+")"
        return sa+"*"+sb
    if k=="div":
        a,b=n[1],n[2]; sa=to_str(a); sb=to_str(b)
        if prec(a)<prec(n): sa="("+sa+")"
        if prec(b)<=prec(n): sb="("+sb+")"
        return sa+"/"+sb
    if k=="pow":
        a,b=n[1],n[2]; sa=to_str(a); sb=to_str(b)
        if prec(a)<prec(n): sa="("+sa+")"
        if prec(b)<prec(n): sb="("+sb+")"
        return sa+"^"+sb
    return "0"

# ---------- inversion paso a paso ----------
def _one_child_with_x(a,b):
    ax=contains_x(a); bx=contains_x(b)
    return (a, b, True) if ax and not bx else (b, a, False) if bx and not ax else (None, None, None)

def invert_once(left, right):
    k=left[0]
    # identidad
    if k=="var": return ("ok", left, right)
    # suma/resta
    if k=="add":
        child,const,flag=_one_child_with_x(left[1], left[2])
        if child is None: return ("stuck", left, right)
        return ("cont", child, simp(Sub(right, const)))
    if k=="sub":
        a,b=left[1], left[2]
        ax, bx = contains_x(a), contains_x(b)
        if ax and not bx:
            return ("cont", a, simp(Add(right, b)))
        if bx and not ax:
            return ("cont", b, simp(Sub(a, right)))
        return ("stuck", left, right)
    # producto
    if k=="mul":
        child,const,flag=_one_child_with_x(left[1], left[2])
        if child is None: return ("stuck", left, right)
        if is_const(const) and not (is_num(const) and const[1]==0.0):
            return ("cont", child, simp(Div(right, const)))
        return ("stuck", left, right)
    # division
    if k=="div":
        a,b=left[1], left[2]
        ax, bx = contains_x(a), contains_x(b)
        if ax and not bx and is_const(b):
            return ("cont", a, simp(Mul(right, b)))
        if bx and not ax and is_const(a):
            return ("cont", b, simp(Div(a, right)))
        return ("stuck", left, right)
    # potencia
    if k=="pow":
        base,expn = left[1], left[2]
        bx, ex = contains_x(base), contains_x(expn)
        if bx and not ex and is_const(expn):
            return ("cont", base, simp(Pow(right, Div(Num(1.0), expn))))
        if ex and not bx and is_const(base):
            return ("cont", expn, simp(Div(Call("ln", right), Call("ln", base))))
        return ("stuck", left, right)
    # funciones basicas
    if k=="call":
        fn, arg = left[1], left[2]
        if fn == "log": fn = "ln"
        if not contains_x(arg):
            return ("stuck", left, right)
        if fn == "sin":
            ksym = Sym("k")
            expr = Add(Mul(Pow(Num(-1.0), ksym), Call("asin", right)), Mul(Num(math.pi), ksym))
            return ("cont", arg, simp(expr))
        if fn == "cos":
            ksym = Sym("k"); ssym = Sym("s")  # s = +-1
            expr = Add(Mul(ssym, Call("acos", right)), Mul(Num(2.0*math.pi), ksym))
            return ("cont", arg, simp(expr))
        if fn == "tan":
            ksym = Sym("k")
            expr = Add(Call("atan", right), Mul(Num(math.pi), ksym))
            return ("cont", arg, simp(expr))
        if fn == "exp":   return ("cont", arg, simp(Call("ln", right)))
        if fn == "ln":    return ("cont", arg, simp(Call("exp", right)))
        if fn == "sqrt":  return ("cont", arg, simp(Pow(right, Num(2.0))))
        return ("stuck", left, right)

def isolate_x(left, right, max_steps=50):
    # requiere que left contenga x y right NO
    if not contains_x(left): return (False, left, right)
    if contains_x(right): return (False, left, right)
    steps=0
    while steps < max_steps:
        st, left, right = invert_once(left, right)
        if st=="ok": return (True, left, simp(right))
        if st=="stuck": return (False, left, right)
        steps += 1
    return (False, left, right)

# ---------- UI helpers ----------
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


# ---------- trig simple: sin/cos/tan ----------
def _sol_sin():
    k = _ask_float("k en sin(x)=k (rad):")
    if k < -1.0 or k > 1.0:
        view_text_from_string("sin(x)=k", "sin solucion real"); _pause(); return
    a = math.asin(k)
    doc = "sin(x) = {}\na = asin(k) = {} rad\nSoluciones:\nx = a + 2*pi*n\nx = (pi - a) + 2*pi*n\n".format(_fmt(k), _fmt(a))
    view_text_from_string("sin(x)=k", doc); _pause()

def _sol_cos():
    k = _ask_float("k en cos(x)=k (rad):")
    if k < -1.0 or k > 1.0:
        view_text_from_string("cos(x)=k", "sin solucion real"); _pause(); return
    a = math.acos(k)
    doc = "cos(x) = {}\na = acos(k) = {} rad\nSoluciones:\nx = +- a + 2*pi*n\n".format(_fmt(k), _fmt(a))
    view_text_from_string("cos(x)=k", doc); _pause()

def _sol_tan():
    k = _ask_float("k en tan(x)=k (rad):")
    a = math.atan(k)
    doc = "tan(x) = {}\na = atan(k) = {} rad\nSoluciones:\nx = a + pi*n\n".format(_fmt(k), _fmt(a))
    view_text_from_string("tan(x)=k", doc); _pause()

def _trig_menu():
    items = [
        ("sin(x)=k", _sol_sin),
        ("cos(x)=k", _sol_cos),
        ("tan(x)=k", _sol_tan),
    ]
    while True:
        fn = _menu("Trig simple (rad)", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            print("Error:", e); _pause()

# ---------- pantallas ----------
def _despejar():
    ecu = _ask_line("ecuacion (usa =):")
    if "=" not in ecu:
        view_text_from_string("Error", "Debe contener '='. Ej: y=(sqrt(3*x+2)-5)/7")
        _pause(); return

    var = _ask_line("variable a aislar (ej: x, v, a, R, h):").strip()
    if not var:
        view_text_from_string("Error", "Tenés que indicar la variable a aislar.")
        _pause(); return

    # split original
    Ls, Rs = ecu.split("=", 1)

    # mapear var -> 'x' SIN romper x0, exp, cos, etc.
    if var != "x":
        Ls_x = _safe_replace_name(Ls, var, "x")
        Rs_x = _safe_replace_name(Rs, var, "x")
    else:
        Ls_x, Rs_x = Ls, Rs  # ya usamos x directamente

    # parsear
    try:
        L = Parser(Ls_x).parse()
        R = Parser(Rs_x).parse()
    except Exception as e:
        view_text_from_string("Error", "Parseo: "+str(e))
        _pause(); return

    # detectar presencia de x en cada lado
    Lx, Rx = contains_x(L), contains_x(R)

    # si aparece en ambos lados -> mover todo a la izq: (L - R) = 0
    if Lx and Rx:
        left  = Sub(L, R)
        right = Num(0.0)
    elif Lx and not Rx:
        left, right = L, R
    elif Rx and not Lx:
        left, right = R, L
    else:
        view_text_from_string("Error", "La variable '{}' no aparece en la ecuacion.".format(var))
        _pause(); return

    ok, lf, sol = isolate_x(left, right)
    if ok and lf[0] == "var":
        expr = to_str(simp(sol))
        # Si el usuario pidió una variable distinta de x, devolvemos en términos de esa variable
        if var != "x":
            expr = _safe_replace_name(expr, "x", var)

        lineas = [
            "Ecuacion: " + ecu.replace("**","^"),
            (var + " = " + expr),
            "",
            "Nota: si el enunciado usa x y x0, recordá que x es la variable y x0 es otra distinta (p. inicial)."
        ]
        view_text("Resultado", lineas)
    else:
        view_text_from_string("Resultado", "operaciones no soportadas por el aislador.")
    _pause()


def _ayuda():
    doc = """Despeje soportado (reglas inversas):
    - +, -, *, / por constantes
    - u^c  <->  raiz c-esima
    - sqrt(u) <-> (^2),  exp(u) <-> ln(u),  ln(u) <-> exp(u)
    - a^g(x) (a constante !=1): g(x) = ln(rhs)/ln(a)
    Ejemplos:
    - y = (sqrt(3*x+2)-5)/7    ->   x = ((y*7)+5)^2/3 - 2/3
    - y = a^(2*x-1)            ->   2*x-1 = ln(y)/ln(a)  ->  x = (ln(y)/ln(a) + 1)/2
    Notas:
    - Se acepta ** para potencia (mapeado a ^).
    - Cualquier identificador distinto de x se trata como constante (y, a, b, k...).
    """
    view_text_from_string("Ayuda", doc)

# ---------- app ----------
def app():
    items = [
        ("despejar x", _despejar),
        ("trig simple sin/cos/tan", _trig_menu),
        ("ayuda", _ayuda),
    ]
    while True:
        fn = _menu("Despeje (aislar x)", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            print("Error:", e); _pause()

if __name__ == "__main__":
    app()
