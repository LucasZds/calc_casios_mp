# atajos.py — chuleta rapida de Python + libs comunes (sin tildes)
# Pantalla 7 lineas, navega con +/- y Enter

# ===== UI basica (7 lineas) =====
from ui_py import view_text, view_menu

PAGE_SIZE = 5  # header(1)+items(3)+nav(1)++prompt(1)=7

def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

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




# ===== helper para mostrar bloques en tandas de 5 lineas =====
def _show(title, lines, chunk=5):
    view_text(title, lines)
    #i=0; n=len(lines)
    #while True:
    #    _clear(); print(title)
    #    j=0
    #    while i<n and j<chunk:
    #        print(lines[i]); i+=1; j+=1
    #    if i>=n:
    #        _pause(); return
    #    _pause("...mas (Enter)")

# ===== contenidos clasicos =====
def _listas():
    lines = [
        "# listas",
        "a = [1,2,3]",
        "a.append(4)          # agrega",
        "a.extend([5,6])      # concat",
        "a.insert(1,'x')      # pos 1",
        "a.pop()              # ultimo",
        "a.remove('x')        # 1ro igual",
        "a[1:4]               # slice",
        "len(a)",
        "for i,x in enumerate(a):",
        "    print(i,x)",
        "[x*x for x in a]     # comp",
        "sorted(a) ; a.sort()",
    ]
    _show("Atajos: listas", lines)

def _dic():
    lines = [
        "# diccionarios",
        "d = {'a':1,'b':2}",
        "d['a'] ; d.get('c',0)",
        "d['c']=3",
        "for k,v in d.items():",
        "    print(k,v)",
        "list(d.keys())",
        "list(d.values())",
        "[k:v*v for k,v in d.items()]",
        "d.pop('a',None)",
        "d.setdefault('z',9)",
    ]
    _show("Atajos: dic", lines)

def _cond():
    lines = [
        "# condicionales",
        "if x>0: print('pos')",
        "elif x==0: print('cero')",
        "else: print('neg')",
        "y = 1 if cond else 2",
        "not a, a and b, a or b",
        "x_in = (x in [1,2,3])",
    ]
    _show("Atajos: cond", lines)

def _for_while():
    lines = [
        "# for / while",
        "for i in range(5):",
        "    print(i)",
        "for i in range(1,6,2):",
        "    print(i)  # 1,3,5",
        "while n>0:",
        "    n-=1",
        "    if n==2: continue",
        "    if n==1: break",
        "for i,x in enumerate([10,20]):",
        "    print(i,x)",
        "for a,b in zip([1,2],[3,4]):",
        "    print(a,b)",
    ]
    _show("Atajos: for/while", lines)

def _funciones():
    lines = [
        "# funciones",
        "def f(x,y=0):",
        "    return x+y",
        "def g(*args,**kw):",
        "    return len(args)",
        "h = lambda t: t*t",
        "def suma(lst):",
        "    s=0",
        "    for v in lst: s+=v",
        "    return s",
        "# llamada: f(2), g(1,2,a=3)",
    ]
    _show("Atajos: funciones", lines)

def _strings():
    lines = [
        "# strings",
        "s='hola mundo'",
        "s.upper(); s.lower()",
        "s.strip()",
        "s.replace('o','0')",
        "trozos=s.split(' ')",
        "unido=','.join(trozos)",
        "s[0:4], s[-1], s[::2]",
        "'%.s %.d'%('ok',7)",
        "'[0]-[1]'.format('a',3)",
    ]
    _show("Atajos: strings", lines)

def _archivos():
    lines = [
        "# archivos",
        "with open('in.txt','r') as f:",
        "    data=f.read()",
        "with open('out.txt','w') as f:",
        "    f.write('hola\\n')",
        "for line in open('in.txt','r'):",
        "    print(line.strip())",
        "# en Casio puede variar",
    ]
    _show("Atajos: archivos", lines)

def _try_except():
    lines = [
        "# try / except",
        "try: x=1/0",
        "except ZeroDivisionError as e:",
        "    print('err',e)",
        "else: print('ok')",
        "finally: print('fin')",
    ]
    _show("Atajos: try/except", lines)

def _comprensiones():
    lines = [
        "# comprensiones",
        "[x*x for x in range(5)]",
        "[x for x in a if x%2==0]",
        "{x for x in range(5)}",
        "[k:v*v for k,v in d.items()]",
        "(x*x for x in range(5))",
    ]
    _show("Atajos: comprensiones", lines)

def _utiles():
    lines = [
        "# utilidades",
        "sum([1,2,3])",
        "max(a), min(a)",
        "any([True,False])",
        "all([1,2,0])",
        "sorted(a,reverse=True)",
        "sorted(a,key=lambda x:x%10)",
        "abs(-3), round(3.1416,2)",
        "range(5) -> 0..4",
        "enumerate(seq), zip(a,b)",
    ]
    _show("Atajos: utiles", lines)

# ===== libs comunes =====
def _math_mod():
    lines = [
        "# math",
        "import math",
        "math.pi, math.e",
        "sin cos tan (rad)",
        "sqrt, log, log10, exp",
        "floor, ceil, fabs",
        "pow, atan2",
        "degrees, radians",
    ]
    _show("Lib: math", lines)

def _random_mod():
    lines = [
        "# random",
        "import random",
        "random.random()  # 0..1",
        "random.randint(a,b)",
        "random.choice(seq)",
        "random.choices(seq,k=3)",
        "random.sample(seq,k)",
        "random.shuffle(a)",
    ]
    _show("Lib: random", lines)

def _statistics_mod():
    lines = [
        "# statistics",
        "from statistics import",
        " mean, median, mode",
        "pstdev, pvariance",
        "stdev, variance",
        "mean([1,2,3]) -> 2",
    ]
    _show("Lib: statistics", lines)

def _datetime_mod():
    lines = [
        "# datetime",
        "from datetime import",
        " datetime, timedelta",
        "now=datetime.now()",
        "dt.strftime('%Y-%m-%d')",
        "dt+timedelta(days=1)",
        "parse: usar datetime(...)",
    ]
    _show("Lib: datetime", lines)

def _itertools_mod():
    lines = [
        "# itertools",
        "from itertools import",
        " accumulate, product,",
        " permutations, combs,",
        " groupby, cycle",
        "list(product([0,1],[2]))",
        "list(permutations('ab',2))",
    ]
    _show("Lib: itertools", lines)

def _collections_mod():
    lines = [
        "# collections",
        "from collections import",
        " Counter, deque,",
        " defaultdict, namedtuple",
        "Counter('abca')",
        "deque([1,2],maxlen=3)",
        "defaultdict(int)['x']",
    ]
    _show("Lib: collections", lines)

def _numpy_pc():
    lines = [
        "# numpy",
        "import numpy as np",
        "a=np.array([1,2,3])",
        "Z=np.zeros((2,3))",
        "a.mean(), a.sum()",
        "b=a.reshape(3,1)",
        "a@a, a.T",
        "np.linspace(0,1,5)",
    ]
    _show("Lib: numpy", lines)

def _matplotlib_pc():
    lines = [
        "# matplotlib",
        "import matplotlib.pyplot",
        "as plt",
        "x=[0,1,2]; y=[0,1,4]",
        "plt.plot(x,y)",
        "plt.xlabel('x')",
        "plt.ylabel('y')",
        "plt.title('graf')",
        "plt.grid(True)",
        "plt.show()",
    ]
    _show("Lib: matplotlib", lines)

def _ayuda():
    lines = [
        "Enter avanza 5 lineas.",
        "En Casio: math ok,",
        "a veces random.",
        "Numpy/Matplotlib/otros",
        "son para PC/Colab.",
        "Evitar tildes y f-strings.",
    ]
    _show("Atajos: ayuda", lines)

# ===== app =====
def app():
    items = [
        ("listas", _listas),
        ("dic", _dic),
        ("cond", _cond),
        ("for/while", _for_while),
        ("funciones", _funciones),
        ("strings", _strings),
        ("archivos", _archivos),
        ("try/except", _try_except),
        ("comprensiones", _comprensiones),
        ("utiles", _utiles),
        ("math", _math_mod),
        ("random", _random_mod),
        ("statistics", _statistics_mod),
        ("datetime", _datetime_mod),
        ("itertools", _itertools_mod),
        ("collections", _collections_mod),
        ("numpy", _numpy_pc),
        ("matplotlib", _matplotlib_pc),
        ("ayuda", _ayuda),
    ]
    while True:
        fn=_menu("Atajos de Python", items)
        if fn is None: return
        try: fn()
        except Exception as e:
            print("Error:", e); _pause()

if __name__ == "__main__":
    app()
