# ==== tdc_1.py (chuleta + calculadoras) ====
import math
from ui_py import view_menu, view_text, view_text_from_string

def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _menu(title, items):
    textos=[t for (t,_) in items]
    try: sel = view_menu(title, textos)
    except: sel = None
    if sel is None: return None
    return items[sel][1]

def _ask(label):
    try: return input(label)
    except: return ""

def _clip(title, lines, n=6):
    view_text(title, lines[:n]); _pause()

# --- helpers ángulo (la Casio no trae math.radians/degrees) ---
PI = 3.141592653589793
def _rad(deg):  # grados → radianes
    try: return deg * PI / 180.0
    except: return 0.0

def _deg(rad):  # radianes → grados
    try: return rad * 180.0 / PI
    except: return 0.0

# Parsers comunes
def _parse_value(s):
    s=(s or "").strip()
    if not s: return 0.0
    m=1.0; suf=s[-1]
    if   suf=='k': m=1e3; s=s[:-1]
    elif suf=='M': m=1e6; s=s[:-1]
    elif suf=='m': m=1e-3; s=s[:-1]
    elif suf=='u': m=1e-6; s=s[:-1]
    elif suf=='n': m=1e-9; s=s[:-1]
    try: return float(s)*m
    except: return 0.0

def _parse_freq(s):
    s=(s or "").strip()
    if not s: return 0.0
    if s.lower().endswith("hz"): s=s[:-2]
    return _parse_value(s)

def _rect(mag, ang):  # ang en rad
    return complex(mag*math.cos(ang), mag*math.sin(ang))

def _phase(z): return math.atan2(z.imag, z.real)

def _parse_phasor(s):
    # Acepta: 10a30, 10 a 30, 10@30, 10∠30
    s = (s or "").strip()
    if not s:
        return 0j
    # normalizar separadores y quitar espacios
    s = s.replace("∠", "a").replace("@", "a")
    s = "".join(s.split())  # quita todos los espacios internos

    if "a" in s:
        mag_s, rest = s.split("a", 1)
        mag = _parse_value(mag_s)
        # tomar prefijo numérico del ángulo (soporta +, -, ., dígitos)
        j = 0
        while j < len(rest) and (rest[j].isdigit() or rest[j] in "+-."):
            j += 1
        ang_s = rest[:j] if j > 0 else "0"
        try:
            ang = float(ang_s)
        except:
            ang = 0.0
        return _rect(mag, _rad(ang))

    # sin separador → real (ángulo 0)
    return complex(_parse_value(s), 0.0)

def _fmt_polar(z):
    return "{:.6g}a{:.3g}°".format(abs(z), _deg(_phase(z)))

def _fmt_rect(z):
    return "{:.6g} + j{:.6g}".format(z.real, z.imag)

def _parse_rect(s):
    s=(s or "").strip().lower().replace(" ","")
    if "j" in s:
        try: return complex(s)
        except: return 0j
    try: return complex(float(s),0.0)
    except: return 0j

# Chuleta
def leyes_basicas():
    items=[
        ("Ley de Ohm", lambda:(view_text("Ley de Ohm",["V = I * R"]),_pause())),
        ("Potencia (DC)", lambda:(view_text("Potencia",["P = V*I = I^2 R = V^2/R"]),_pause())),
        ("Energia", lambda:(view_text("Energia",["E = P * t"]),_pause())),
    ]
    while True:
        fn=_menu("Leyes basicas", items)
        if fn is None: return
        fn()

def resistencias():
    items=[
        ("Serie", lambda:(view_text("R en serie",["R_eq = R1 + R2 + ···"]),_pause())),
        ("Paralelo (N)", lambda:(view_text("R paralelo",["1/R_eq = Σ (1/Ri)"]),_pause())),
        ("2 en paralelo", lambda:(view_text("2R paralelo",["R_eq = (R1*R2)/(R1+R2)"]),_pause())),
    ]
    while True:
        fn=_menu("Resistencias", items)
        if fn is None: return
        fn()

def reactancias():
    items=[
        ("Capacitor", lambda:(view_text("Capacitor",["Xc = 1/(wC), Zc = -j/(wC)"]),_pause())),
        ("Inductor",  lambda:(view_text("Inductor", ["Xl = wL, Zl = jwL"]),_pause())),
        ("Impedancia",lambda:(view_text("Impedancia",["Z = R + jX, I = V/Z"]),_pause())),
    ]
    while True:
        fn=_menu("Reactancias (AC)", items)
        if fn is None: return
        fn()

# Calculadoras
def ohm_calc():
    view_text("Ohm calc (DC)",["Deja vacio lo que quieres despejar."])
    V=_ask("V (V): "); I=_ask("I (A): "); R=_ask("R (ohm): ")
    V=(V or "").strip(); I=(I or "").strip(); R=(R or "").strip()
    try:
        if (not V) and I and R:
            _clip("Resultado",["V = {:.6g} V".format(_parse_value(I)*_parse_value(R))])
        elif (not I) and V and R:
            Rv=_parse_value(R); val=(_parse_value(V)/Rv if Rv!=0 else float('inf'))
            _clip("Resultado",["I = {:.6g} A".format(val)])
        elif (not R) and V and I:
            Iv=_parse_value(I); val=(_parse_value(V)/Iv if Iv!=0 else float('inf'))
            _clip("Resultado",["R = {:.6g} ohm".format(val)])
        else:
            _clip("Aviso",["Completa exactamente 2 valores."])
    except:
        _clip("Error",["Entrada invalida"])

def complejos_menu():
    def rect_a_polar():
        z=_parse_rect(_ask("z (rect, ej 3+4j): "))
        view_text("Rect→Polar",["z = {}".format(_fmt_rect(z)),"= {}".format(_fmt_polar(z))]); _pause()
    def polar_a_rect():
        s=_ask("z (mag a ang°, ej 5a53.13): ")
        s = "".join(s.strip().replace("∠","a").replace("@","a").split())
        if "a" not in s:
            view_text("Polar→Rect",["Formato invalido"]); _pause(); return
        p=s.split("a",1)
        try:
            z=_rect(_parse_value(p[0]), _rad(float(p[1])))
            view_text("Polar→Rect",["z = {}".format(_fmt_polar(z)),"= {}".format(_fmt_rect(z))]); _pause()
        except:
            view_text("Polar→Rect",["Entrada invalida"]); _pause()
    def operar():
        a=_parse_rect(_ask("a (rect): ")); b=_parse_rect(_ask("b (rect): "))
        op=(_ask("(+) (-) (*) (/): ") or "+").strip()
        if op=="+": z=a+b
        elif op=="-": z=a-b
        elif op=="*": z=a*b
        elif op=="/": z=a/b if b!=0 else 0j
        else: z=a+b
        view_text("Operar",["rect: {}".format(_fmt_rect(z)),"polar: {}".format(_fmt_polar(z))]); _pause()
    items=[("Rect→Polar",rect_a_polar),("Polar→Rect",polar_a_rect),("Operar a,b",operar)]
    while True:
        fn=_menu("Complejos/Fasores", items)
        if fn is None: return
        fn()

def xl_xc_calc():
    f=_parse_freq(_ask("f (Hz, ej 1k): "))
    Ls=(_ask("L (H, ej 100m) o vacio: ") or "").strip()
    Cs=(_ask("C (F, ej 1u)  o vacio: ") or "").strip()
    w=2*math.pi*f if f>0 else 0.0
    lines=["w = {:.6g} rad/s".format(w)]
    if Ls:
        lines.append("X_L = wL = {:.6g} ohm".format(w*_parse_value(Ls)))
    if Cs:
        C=_parse_value(Cs); XC=(1e18 if (C<=0 or w==0) else 1.0/(w*C))
        lines.append("X_C = 1/(wC) = {:.6g} ohm".format(XC))
    _clip("XL / XC", lines)

def lc_tiempo():
    view_text("L/C en tiempo",[
        "L: v(t)=L di/dt  |  i(t)=(1/L)∫v(t)dt",
        "C: i(t)=C dv/dt  |  v(t)=(1/C)∫i(t)dt",
        "Para senoidales: usar fasores (Z_L=jwL, Z_C=1/jwC).",
    ]); _pause()

def zt_serie_paralelo():
    view_text("ZT rapidos",[
    "Serie: ZT = Σ Zi",
    "Paralelo: 1/ZT = Σ (1/Zi)",
    "Zi: mag a ang / mag@ang / mag∠ang o a+bj; sep. por ';'"
    ])
    modo=(_ask("modo (S/P): ") or "S").strip().upper()
    zs=_ask("Zs (ej 10a0, 5a90, 3-2j): ").split(",")
    Zs=[]; i=0
    while i<len(zs):
        z=zs[i].strip()
        if z:
            if ("a" in z) or ("∠" in z) or ("@" in z):
                Zs.append(_parse_phasor(z))
            else:
                Zs.append(_parse_rect(z))

        i+=1
    if not Zs: view_text("ZT",["Sin datos"]); _pause(); return
    if modo=="S":
        ZT=0j; i=0
        while i<len(Zs): ZT+=Zs[i]; i+=1
    else:
        inv=0j; i=0
        while i<len(Zs):
            z=Zs[i]
            if z!=0: inv+=1.0/z
            i+=1
        ZT=(1/inv) if inv!=0 else 0j
    view_text("ZT",["rect: {}".format(_fmt_rect(ZT)),"polar: {}".format(_fmt_polar(ZT))]); _pause()

def triangulo_potencias():
    Vs=_ask("V (mag a ang): "); Is=_ask("I (mag a ang): ")
    try:
        V=_parse_phasor(Vs); I=_parse_phasor(Is)
        S= V * complex(I.real,-I.imag)
        P=S.real; Q=S.imag; Sm=abs(S)
        fp=(0.0 if Sm==0 else P/Sm)
        tip=("adelantado" if Q<0 else ("atrasado" if Q>0 else "unitario"))
        _clip("Triangulo de potencias",[
            "P={:.6g} W  Q={:.6g} var  |S|={:.6g} VA".format(P,Q,Sm),
            "fp={:.4f} ({})".format(fp, tip),
        ])
    except:
        _clip("Error",["Entrada invalida"])

def app():
    items=[
        ("Leyes basicas", leyes_basicas),
        ("Resistencias",  resistencias),
        ("Reactancias",   reactancias),
        ("Ohm (DC)",      ohm_calc),
        ("XL/XC",         xl_xc_calc),
        ("Complejos/Fasores", complejos_menu),
        ("ZT rapidos",    zt_serie_paralelo),
        ("Triangulo potencias", triangulo_potencias),
        ("L/C en tiempo", lc_tiempo),
    ]
    while True:
        fn=_menu("Calcs", items)
        if fn is None: return
        try: fn()
        except Exception as e: view_text_from_string("Error", str(e)); _pause()

if __name__ == "__main__":
    app()