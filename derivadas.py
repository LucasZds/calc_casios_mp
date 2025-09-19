# derivadas.py — derivacion simbolica con salida d1(x), d2(x), ...
# Operadores: + - * / ^, parentesis. Variable: x. Constantes: pi, e.
# Funciones: sin cos tan exp ln sqrt asin acos atan sinh cosh tanh log10
from ui_py import view_text,view_menu,view_text_from_string

# ---------- lexer ----------
NUM, ID, OP, LP, RP, END = "NUM","ID","OP","LP","RP","END"

class Tok:
    def __init__(self,t,v=None): self.t=t; self.v=v

def _is_idch(c): return ("a"<=c<="z") or ("A"<=c<="Z") or (c=="_")
def _is_dig(c):  return "0"<=c<="9"

class Lexer:
    def __init__(self,s):
        self.s = s.replace(" ",""); self.n = len(self.s); self.i = 0; self.cur=None; self.next()
    def next(self):
        s,n,i = self.s,self.n,self.i
        if i>=n: self.cur=Tok(END); return
        c=s[i]
        if _is_dig(c) or (c=="." and i+1<n and _is_dig(s[i+1])):
            j=i+1
            while j<n and (_is_dig(s[j]) or s[j]=="."): j+=1
            self.cur=Tok(NUM, float(s[i:j] or "0")); self.i=j; return
        if _is_idch(c):
            j=i+1
            while j<n and (_is_idch(s[j]) or _is_dig(s[j])): j+=1
            self.cur=Tok(ID, s[i:j]); self.i=j; return
        if c == "*" and i + 1 < n and s[i+1] == "*":
            self.cur = Tok(OP, "^")   # mapeamos ** a '^' que ya entiende el parser
            self.i = i + 2
            return
        if c in "+-*/^": self.cur=Tok(OP,c); self.i=i+1; return
        if c=="(": self.cur=Tok(LP,"("); self.i=i+1; return
        if c==")": self.cur=Tok(RP,")"); self.i=i+1; return
        self.i=i+1; self.next()

# ---------- AST ----------
def Num(v): return ("num", float(v))
def Var():  return ("var",)
def Add(a,b):return ("add",a,b)
def Sub(a,b):return ("sub",a,b)
def Mul(a,b):return ("mul",a,b)
def Div(a,b):return ("div",a,b)
def Pow(a,b):return ("pow",a,b)
def Call(fn,arg): return ("call",fn,arg)

# ---------- parser ----------
class Parser:
    def __init__(self,s): self.lx=Lexer(s)
    def parse(self): return self.expr()
    def eat(self,t):
        if self.lx.cur.t==t: self.lx.next(); return True
        return False
    def expr(self):
        node = self.term()
        while self.lx.cur.t == OP and self.lx.cur.v in "+-":
            op = self.lx.cur.v; self.lx.next()
            rhs = self.term()
            node = Add(node, rhs) if op == "+" else Sub(node, rhs)
        return node
    def term(self):
        node = self.unary()
        while self.lx.cur.t == OP and self.lx.cur.v in "*/":
            op = self.lx.cur.v; self.lx.next()
            rhs = self.unary()
            node = Mul(node, rhs) if op == "*" else Div(node, rhs)
        return node

    def unary(self):
        if self.lx.cur.t == OP and self.lx.cur.v == "+":
            self.lx.next(); return self.unary()
        if self.lx.cur.t == OP and self.lx.cur.v == "-":
            self.lx.next(); return Mul(Num(-1.0), self.unary())
        return self.power()
    def power(self):
        node = self.primary()
        # asociatividad a derecha: x^y^z = x^(y^z)
        if self.lx.cur.t == OP and self.lx.cur.v == "^":
            self.lx.next()
            rhs = self.unary()   # <--- en vez de self.power()
            node = Pow(node, rhs)
        return node

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
            return Var()
        if self.eat(LP):
            node=self.expr(); self.eat(RP); return node
        self.lx.next(); return Num(0.0)

# ---------- derivacion ----------
def is_const(n): return n[0]=="num"
def is_zero(n):  return n[0]=="num" and n[1]==0.0
def is_one(n):   return n[0]=="num" and n[1]==1.0

def d(n):
    k=n[0]
    if k=="num": return Num(0.0)
    if k=="var": return Num(1.0)
    if k=="add": return Add(d(n[1]), d(n[2]))
    if k=="sub": return Sub(d(n[1]), d(n[2]))
    if k=="mul":
        f,g=n[1],n[2]; return Add(Mul(d(f),g), Mul(f,d(g)))
    if k=="div":
        f,g=n[1],n[2]; return Div(Sub(Mul(d(f),g), Mul(f,d(g))), Pow(g,Num(2.0)))
    if k=="pow":
        f,g=n[1],n[2]
        if is_const(g): return Mul(Mul(g, Pow(f, Sub(g,Num(1.0)))), d(f))
        return Mul(Pow(f,g), Add(Mul(d(g), Call("ln",f)), Div(Mul(g, d(f)), f)))
    if k=="call":
        fn,arg=n[1],n[2]; du=d(arg)
        if fn=="sin":  return Mul(Call("cos",arg), du)
        if fn=="cos":  return Mul(Mul(Num(-1.0), Call("sin",arg)), du)
        if fn=="tan":  return Mul(Div(Num(1.0), Pow(Call("cos",arg), Num(2.0))), du)
        if fn=="exp":  return Mul(Call("exp",arg), du)
        if fn=="ln":   return Div(du, arg)
        if fn=="sqrt": return Div(du, Mul(Num(2.0), Call("sqrt",arg)))
        if fn=="asin": return Div(du, Call("sqrt", Sub(Num(1.0), Pow(arg, Num(2.0)))))
        if fn=="acos": return Mul(Num(-1.0), Div(du, Call("sqrt", Sub(Num(1.0), Pow(arg, Num(2.0))))))
        if fn=="atan": return Div(du, Add(Num(1.0), Pow(arg, Num(2.0))))
        if fn=="sinh": return Mul(Call("cosh",arg), du)
        if fn=="cosh": return Mul(Call("sinh",arg), du)
        if fn=="tanh": return Mul(Div(Num(1.0), Pow(Call("cosh",arg), Num(2.0))), du)
        if fn=="log10":return Div(du, Mul(arg, Num(2.302585092994046)))  # 1/(u ln10)
        return Num(0.0)
    return Num(0.0)

# ---------- simplificacion ----------
def num(v): return Num(float(v))

# helpers para aplanar multiplicaciones y combinar constantes
def _fold_mul(factors):
    if not factors: return Num(1.0)
    res = factors[0]
    i = 1
    while i < len(factors):
        res = ("mul", res, factors[i])
        i += 1
    return res

def _flatten_mul_node(t, coeff, factors):
    k = t[0]
    if k == "num":
        return (coeff * t[1], factors)
    if k == "mul":
        coeff, factors = _flatten_mul_node(t[1], coeff, factors)
        return _flatten_mul_node(t[2], coeff, factors)
    factors.append(t)
    return (coeff, factors)

def _rebuild_mul(coeff, factors):
    # construye producto con el coeficiente numerico al frente
    if coeff == 0.0: return Num(0.0)
    if not factors:
        return Num(coeff)
    prod = _fold_mul(factors)
    if abs(coeff - 1.0) < 1e-12:
        return prod
    if abs(coeff + 1.0) < 1e-12:
        return ("mul", Num(-1.0), prod)   # deja -1 al tope para pretty "-"
    return ("mul", Num(coeff), prod)

def simp(n):
    k=n[0]
    if k in ("num","var"): return n
    if k=="call": return ("call", n[1], simp(n[2]))
    if k in ("add","sub","mul","div","pow"):
        a=simp(n[1]); b=simp(n[2])
        # plegado constante
        if a[0]=="num" and b[0]=="num":
            av,bv=a[1],b[1]
            if k=="add": return num(av+bv)
            if k=="sub": return num(av-bv)
            if k=="mul": return num(av*bv)
            if k=="div": return ("div",a,b) if bv==0.0 else num(av/bv)
            if k=="pow":
                if not (av==0.0 and bv==0.0):
                    try: return num(av**bv)
                    except: return ("pow",a,b)
        # reglas con neutros
        if k=="add":
            if is_zero(a): return b
            if is_zero(b): return a
            return ("add",a,b)
        if k=="sub":
            if is_zero(b): return a
            if is_zero(a): return Mul(num(-1.0), b)
            return ("sub",a,b)
        if k=="mul":
            # aplanar y combinar constantes (-1*-1 -> 1, etc.)
            coeff, factors = _flatten_mul_node(a, 1.0, [])
            coeff, factors = _flatten_mul_node(b, coeff, factors)
            if coeff == 0.0: return num(0.0)
            if abs(coeff - 1.0) < 1e-12 and len(factors)==1: return factors[0]
            return _rebuild_mul(coeff, factors)
        if k=="div":
            if is_zero(a): return num(0.0)
            if is_one(b): return a
            return ("div",a,b)
        if k=="pow":
            if is_one(b): return a
            if b[0]=="num" and b[1]==0.0: return num(1.0)
            return ("pow",a,b)
    return n

# ---------- pretty print ----------
def prec(n):
    k=n[0]
    return 5 if k in ("num","var") else 4 if k=="call" else 3 if k=="pow" else 2 if k in ("mul","div") else 1

def fmt_num(v):
    iv=int(v)
    return str(iv) if v==iv else "{:.10g}".format(v)

def to_str(n):
    k=n[0]
    if k=="num": return fmt_num(n[1])
    if k=="var": return "x"
    if k=="call": return n[1]+"("+to_str(n[2])+")"
    if k in ("add","sub"):
        a,b=n[1],n[2]; sa=to_str(a); sb=to_str(b)
        if prec(a)<prec(n): sa="("+sa+")"
        if prec(b)<prec(n): sb="("+sb+")"
        return sa+("+" if k=="add" else "-")+sb
    if k=="mul":
        a,b=n[1],n[2]
        # si es (-1)*expr al tope, usar prefijo "-"
        if a[0]=="num" and abs(a[1] + 1.0) < 1e-12:
            s = to_str(b)
            if b[0] in ("add","sub"): s = "("+s+")"
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

# ---------- UI ----------
PAGE_SIZE = 5  # header(1)+items(3)+nav(1)++prompt(1)=7

def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass
def _clear():
    print("\n"*PAGE_SIZE)

def _ask_line(label):
    print(label); return input("> ").strip()
def _ask_int(label):
    print(label); s=input("> ").strip()
    try: return int(s)
    except: return 1

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


# ---------- pantallas ----------
def _derivar_n():
    s=_ask_line("funcion f(x):")
    n_str = _ask_line("numero de derivadas n (>=1, 0=identidad):")
    try:
        n = int(n_str)
    except:
        n = 1
    if n<0: n=0
    try:
        ast=Parser(s).parse(); der=ast; i=0
        while i<n: der=simp(d(der)); i+=1
        lineas=[]
        lineas.append("f(x) = " + to_str(simp(ast)))
        if n==0:
            lineas.append("d0(x) = " + to_str(simp(ast)))
        elif n==1:
            lineas.append("d1(x) = " + to_str(simp(der)))
        else:
            lineas.append("d" + str(n) + "(x) = " + to_str(simp(der)))
        view_text("Resultado", lineas)
    except Exception as e:
        print("Error:", e)
        _pause()


def _lista_1n():
    s=_ask_line("funcion f(x):")
    n_str = _ask_line("numero de derivadas n (>=1):")
    try:
        n = int(n_str)
    except:
        n = 1
    if n<1: n=1
    try:
        cur=Parser(s).parse()
        lineas=[]
        lineas.append("f(x) = " + to_str(simp(cur)))
        i = 1
        while i <= n:
            cur=simp(d(cur))
            lineas.append("d" + str(i) + "(x) = " + to_str(simp(cur)))
            i += 1
        view_text("Derivadas 1..n", lineas)
    except Exception as e:
        print("Error:", e)
        _pause()

def _ayuda():
    doc = (
        "AYUDA\n"
        "Entrada: f(x) con + - * / ^ (también ** para potencia) y paréntesis. "
        "Sin multiplicación implícita.\n"
        "Funciones: sin cos tan exp ln sqrt asin acos atan sinh cosh tanh log10\n"
        "Constantes: pi, e. Variable: x\n"
        "Ejemplos:\n"
        "  cos(x)        -> d1(x) = -sin(x)\n"
        "  x^x           -> d1(x) = x^x*(ln(x)+1)\n"
        "  ln(sin(x))    -> d1(x) = cos(x)/sin(x)\n"
    )
    view_text_from_string("Ayuda", doc)

# ---------- app ----------
def app():
    items = [
        ("derivar n (final)", _derivar_n),
        ("lista 1..n", _lista_1n),
        ("ayuda", _ayuda),
    ]
    while True:
        fn=_menu("Derivadas (simbolico)", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            print("Error:", e); _pause()

if __name__ == "__main__":
    app()
