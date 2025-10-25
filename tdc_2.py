# ==== tdc_2.py (MNA DC/AC) ====
import math
from ui_py import view_menu, view_text, view_text_from_string

# ---- registro liviano de pasos ----
_STEPS = []
def _steps_reset():
    global _STEPS; _STEPS = []
def _steps_add(s):
    try:
        if len(_STEPS) < 200:  # cap por memoria
            _STEPS.append(s)
    except:
        pass

def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _menu(title, items):
    textos=[t for (t,_) in items]
    try: sel=view_menu(title, textos)
    except: sel=None
    if sel is None: return None
    return items[sel][1]

def _ask(s):
    try: return input(s)
    except: return ""

def _clip_steps(title, extra_lines=None):
    lines = list(_STEPS)
    if extra_lines: lines += extra_lines
    if not lines: lines = ["(sin pasos registrados)"]
    # mostrar todo:
    view_text_from_string(title, "\n".join(lines))

def _clip(title, lines, n=None):
    if isinstance(lines, str):
        txt = lines
    else:
        txt = "\n".join(lines if (n is None) else lines[:n])
    view_text_from_string(title, txt)  # sin corte por defecto

# --- helpers ángulo (sin math.radians/degrees en Casio) ---
PI = 3.141592653589793
def _rad(deg):  # grados → radianes
    try: return deg * PI / 180.0
    except: return 0.0
def _deg(rad):  # radianes → grados
    try: return rad * 180.0 / PI
    except: return 0.0

# --- parsers de valores y fasores ---
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

def _rect(mag, ang):
    return complex(mag*math.cos(ang), mag*math.sin(ang))

def _parse_phasor(s):
    s=(s or "").strip()
    if not s: return 0j
    s=s.replace("∠","a").replace("@","a")
    s="".join(s.split())  # sin espacios
    if "a" in s:
        mag_s, rest = s.split("a",1)
        mag = _parse_value(mag_s)
        j=0
        while j<len(rest) and (rest[j].isdigit() or rest[j] in "+-."):
            j+=1
        ang_s = rest[:j] or "0"
        try: ang = float(ang_s)
        except: ang = 0.0
        return complex(mag*math.cos(_rad(ang)), mag*math.sin(_rad(ang)))
    return complex(_parse_value(s),0.0)

def _isfinite(x):
    try:
        return (x==x) and (x!=float('inf')) and (x!=-float('inf'))
    except:
        return False

def _fmt_polar(z):
    xr, xi = z.real, z.imag
    if not (_isfinite(xr) and _isfinite(xi)): return "nan"
    ang = math.atan2(xi, xr)*180.0/PI
    return "{:.6g}a{:.3g}°".format(abs(z), ang)

def _parse_rect(s):
    s=(s or "").strip().lower().replace(" ","")
    if "j" in s:
        try: return complex(s)
        except: return 0j
    try: return complex(float(s),0.0)
    except: return 0j

# --- netlist 1 línea: admite ';' | '|' | ')' como separadores de elementos ---
# dentro del elemento, admite comas o espacios entre campos
def _parse_netlist_1line(s):
    out=[]; t=(s or "").strip()
    if not t: return out
    for sep in ("|", ")"):  # separadores alternativos
        t=t.replace(sep, ";")
    for p in [p.strip() for p in t.split(";")]:
        if not p: continue
        toks=[tok for tok in p.replace(",", " ").split() if tok]
        if len(toks)<4: continue
        k=toks[0].upper()
        try:
            n1=int(toks[1]); n2=int(toks[2])
        except:
            continue
        val="".join(toks[3:])  # une "30 a 0" -> "30a0"
        out.append((k,n1,n2,val))
    return out

def _collect_nodes_vs(elems):
    nodes=set(); vsrcs=[]
    for (k,a,b,val) in elems:
        nodes.add(a); nodes.add(b)
        if k=="V": vsrcs.append((a,b,val))
    if 0 in nodes: nodes.discard(0)
    node_list=sorted(list(nodes))
    idx={}; i=0
    while i<len(node_list):
        idx[node_list[i]]=i; i+=1
    return node_list, idx, vsrcs

# ------ Gauss real/complex ------
def _gauss_solve_real(A,b):
    n=len(A); i=0
    while i<n:
        piv=i; r=i+1; mv=abs(A[i][i])
        while r<n:
            v=abs(A[r][i])
            if v>mv: mv=v; piv=r
            r+=1
        if piv!=i:
            A[i],A[piv]=A[piv],A[i]
            b[i],b[piv]=b[piv],b[i]
        p=A[i][i]
        if abs(p)>=1e-18:
            inv=1.0/p; c=i
            while c<n: A[i][c]*=inv; c+=1
            b[i]*=inv
            r=i+1
            while r<n:
                f=A[r][i]
                if f!=0:
                    c=i
                    while c<n: A[r][c]-=f*A[i][c]; c+=1
                    b[r]-=f*b[i]
                r+=1
        i+=1
    x=[0.0]*n; i=n-1
    while i>=0:
        s=b[i]; c=i+1
        while c<n: s-=A[i][c]*x[c]; c+=1
        p=A[i][i]
        x[i]=0.0 if abs(p)<1e-18 else s/p
        i-=1
    return x

def _gauss_solve_cpx(A,b):
    n=len(A); i=0
    while i<n:
        piv=i; r=i+1; mv=abs(A[i][i])
        while r<n:
            v=abs(A[r][i])
            if v>mv: mv=v; piv=r
            r+=1
        if piv!=i:
            A[i],A[piv]=A[piv],A[i]
            b[i],b[piv]=b[piv],b[i]
        p=A[i][i]
        if abs(p)>=1e-18:
            inv=1.0/p; c=i
            while c<n: A[i][c]*=inv; c+=1
            b[i]*=inv
            r=i+1
            while r<n:
                f=A[r][i]
                if f!=0:
                    c=i
                    while c<n: A[r][c]-=f*A[i][c]; c+=1
                    b[r]-=f*b[i]
                r+=1
        i+=1
    x=[0j]*n; i=n-1
    while i>=0:
        s=b[i]; c=i+1
        while c<n: s-=A[i][c]*x[c]; c+=1
        p=A[i][i]
        x[i]=0j if abs(p)<1e-18 else s/p
        i-=1
    return x

# ------ DC (R, I, V) ------
def _stamp_dc(elems):
    node_list, idx, vsrcs = _collect_nodes_vs(elems)
    n=len(node_list); m=len(vsrcs); N=n+m
    A=[[0.0]*N for _ in range(N)]; z=[0.0]*N

    _steps_reset()
    _steps_add("MNA DC: nodos={} Vsrcs={}".format(len(node_list), len(vsrcs)))

    def gi(nod):
        if nod==0: return None
        return idx.get(nod, None)

    for (k,a,b,val) in elems:
        ia,ib=gi(a),gi(b)
        if k=="R":
            R=_parse_value(val)
            if R==0: continue
            g=1.0/R
            _steps_add("R {}-{}: g=1/R={:.6g} S".format(a,b,g))
            if ia is not None: A[ia][ia]+=g
            if ib is not None: A[ib][ib]+=g
            if ia is not None and ib is not None:
                A[ia][ib]-=g; A[ib][ia]-=g
        elif k=="I":
            I=_parse_value(val)
            _steps_add("I {}->{}: +I en {}, -I en {}".format(a,b,a,b))
            if ia is not None: z[ia]+=I
            if ib is not None: z[ib]-=I

    k=0
    while k<len(vsrcs):
        a,b,val=vsrcs[k]; row=n+k
        ia,ib=gi(a),gi(b)
        _steps_add("V {}->{}: ecuación auxiliar, V={}".format(a,b,_parse_value(val)))
        if ia is not None: A[ia][row]+=1.0; A[row][ia]+=1.0
        if ib is not None: A[ib][row]-=1.0; A[row][ib]-=1.0
        z[row]+=_parse_value(val)
        k+=1
    return A,z,node_list,vsrcs

def _element_results_dc(elems, node_list, vsrcs, sol):
    n=len(node_list); node_v={0:0.0}; i=0
    while i<n: node_v[node_list[i]]=sol[i]; i+=1
    v_idx={}; k=0
    while k<len(vsrcs):
        a,b,val=vsrcs[k]; v_idx[(a,b,val)]=n+k; k+=1
    lines=[]
    for (K,a,b,val) in elems:
        Va=node_v.get(a,0.0); Vb=node_v.get(b,0.0); Vab=Va-Vb
        if K=="R":
            R=_parse_value(val); I=(Vab/R if R!=0 else float('inf')); P=Vab*I
            lines.append("R {}-{}: V={}V  I={}A  P={}W".format(a,b,"{:.6g}".format(Vab),"{:.6g}".format(I),"{:.6g}".format(P)))
        elif K=="I":
            I=_parse_value(val); P=Vab*I
            lines.append("I {}->{}: V={}V  I={}A  P={}W".format(a,b,"{:.6g}".format(Vab),"{:.6g}".format(I),"{:.6g}".format(P)))
        elif K=="V":
            I=sol[v_idx[(a,b,val)]]; Vv=_parse_value(val); P=Vv*I
            lines.append("V {}->{}: V={}V  I={}A  P={}W".format(a,b,"{:.6g}".format(Vv),"{:.6g}".format(I),"{:.6g}".format(P)))
    return lines

def nodos_dc():
    view_text("Nodos DC (MNA)",[
        "R/I/V en 1 linea (ohm, A, V).",
        "Separadores de elementos: ';' o '|' o ')'",
        "Campos dentro del elemento: con comas o espacios",
        "Ej: V,1,0,5|R,1,2,1k|R,2,0,2k"
    ]); _pause()
    net=_ask("\nNetlist (1 linea): "); elems=_parse_netlist_1line(net)
    if not elems: _clip("Aviso",["Entrada vacia/invalid."]); return
    A,z,node_list,vsrcs=_stamp_dc(elems); sol=_gauss_solve_real(A,z)
    lines=[]; i=0
    while i<len(node_list):
        lines.append("V({}) = {} V".format(node_list[i], "{:.6g}".format(sol[i]))); i+=1
    if not lines: lines=["(sin nodos distintos de 0)"]
    _clip("Resultados DC", lines)
    def _res_elem():
        l=_element_results_dc(elems,node_list,vsrcs,sol)
        if not l: l=["(Sin elementos)"]
        _clip("Elementos DC", l)
    def _ver_pasos():
        _clip_steps("Pasos (MNA DC)")
    while True:
        fn=_menu("Mas resultados",[("Resumen por elemento", _res_elem), ("Pasos (MNA)", _ver_pasos)])
        if fn is None: break
        fn()

# ------ AC (R,C,L,Z,I,V) ------
def _impedance_of(kind, val, w):
    if kind=="R":
        Z=complex(_parse_value(val),0.0)
        return Z if Z!=0 else complex(1e-18,0)
    if kind=="C":
        C=_parse_value(val)
        if C<=0 or w==0: return complex(1e18,0)  # abierto
        return complex(0,-1.0/(w*C))
    if kind=="L":
        L=_parse_value(val); return complex(0,w*L)
    if kind=="Z":
        return _parse_phasor(val)
    return None

def _stamp_ac(elems, f_hz):
    w=2*math.pi*f_hz
    node_list, idx, vsrcs = _collect_nodes_vs(elems)
    n=len(node_list); m=len(vsrcs); N=n+m
    A=[[0j]*N for _ in range(N)]; z=[0j]*N

    _steps_reset()
    _steps_add("MNA AC: f={:.6g} Hz, w=2πf={:.6g}".format(f_hz, w))

    def gi(nod):
        if nod==0: return None
        return idx.get(nod, None)

    for (k,a,b,val) in elems:
        ia,ib=gi(a),gi(b)
        if k in ("R","C","L","Z"):
            Z=_impedance_of(k,val,w)
            if Z==0: Z=complex(1e-18,0)
            Y=1.0/Z
            if k=="R":
                _steps_add("R {}-{}: Z=R={}, Y=1/R={}".format(a,b,_parse_value(val), _fmt_polar(Y)))
            elif k=="L":
                L=_parse_value(val)
                _steps_add("L {}-{}: Z=jwL, L={}, wL={}, Z={}, Y={}".format(
                    a,b,L, w*L, _fmt_polar(complex(0,w*L)), _fmt_polar(Y)))
            elif k=="C":
                C=_parse_value(val)
                Xc = (1.0/(w*C) if (C>0 and w>0) else float('inf'))
                _steps_add("C {}-{}: Z=1/(jwC), C={}, 1/(wC)≈{}, Z≈-j{}, Y={}".format(
                    a,b,C, Xc, Xc, _fmt_polar(Y)))
            elif k=="Z":
                _steps_add("Z {}-{}: Z={}, Y={}".format(a,b, val, _fmt_polar(Y)))
            if ia is not None: A[ia][ia]+=Y
            if ib is not None: A[ib][ib]+=Y
            if ia is not None and ib is not None:
                A[ia][ib]-=Y; A[ib][ia]-=Y
        elif k=="I":
            I=_parse_phasor(val)
            _steps_add("I {}->{}: +I en {}, -I en {} (I={})".format(a,b,a,b,_fmt_polar(I)))
            if ia is not None: z[ia]+=I
            if ib is not None: z[ib]-=I

    k=0
    while k<len(vsrcs):
        a,b,val=vsrcs[k]; row=n+k
        ia,ib=gi(a),gi(b)
        _steps_add("V {}->{}: ecuación auxiliar, V={}".format(a,b,val))
        if ia is not None: A[ia][row]+=1.0; A[row][ia]+=1.0
        if ib is not None: A[ib][row]-=1.0; A[row][ib]-=1.0
        z[row]+=_parse_phasor(val); k+=1
    return A,z,node_list,vsrcs,w

def _element_results_ac(elems, node_list, vsrcs, sol, w):
    n=len(node_list); node_v={0:0j}; i=0
    while i<n: node_v[node_list[i]]=sol[i]; i+=1
    v_idx={}; k=0
    while k<len(vsrcs):
        a,b,val=vsrcs[k]; v_idx[(a,b,val)]=n+k; k+=1
    lines=[]
    for (K,a,b,val) in elems:
        Va=node_v.get(a,0j); Vb=node_v.get(b,0j); Vab=Va-Vb
        if K in ("R","C","L","Z"):
            Z=_impedance_of(K,val,w); I=(Vab/Z if Z!=0 else 0j)
            S= Vab * complex(I.real,-I.imag); P=S.real; Q=S.imag
            lines.append("{} {}-{}: V={}  I={}  P={}W  Q={}var".format(
                K, a,b, _fmt_polar(Vab), _fmt_polar(I), "{:.6g}".format(P), "{:.6g}".format(Q)))
        elif K=="I":
            I=_parse_phasor(val); S= Vab * complex(I.real,-I.imag); P=S.real; Q=S.imag
            lines.append("I {}->{}: V={}  I={}  P={}W  Q={}var".format(
                a,b, _fmt_polar(Vab), _fmt_polar(I), "{:.6g}".format(P), "{:.6g}".format(Q)))
        elif K=="V":
            I=sol[v_idx[(a,b,val)]]; Vv=_parse_phasor(val); S= Vv * complex(I.real,-I.imag)
            P=S.real; Q=S.imag
            lines.append("V {}->{}: V={}  I={}  P={}W  Q={}var".format(
                a,b, _fmt_polar(Vv), _fmt_polar(I), "{:.6g}".format(P), "{:.6g}".format(Q)))
    return lines

def nodos_ac():
    view_text("Nodos AC (fasores)",[
        "Elementos: R/C/L/Z/I/V",
        "Z y fuentes en polar: mag a ang (°).",
        "Separadores: ';' o '|' o ')', campos con coma o espacio",
        "TIP: si no tenes f, usa solo R/Z/I/V (sin L/C) y deja f=0: asumo f=1."
    ]); _pause()

    fs = (_ask("f (Hz, ej 1k, o 0 si no tenes): ") or "").strip()
    f = _parse_freq(fs)

    net = _ask("Netlist (1 linea): ")
    elems = _parse_netlist_1line(net)
    if not elems:
        _clip("Aviso",["Entrada vacia/invalid."]); return

    # ¿Hay L o C?
    has_LC = any(k in ("L","C") for (k,_,_,_) in elems)

    # Política:
    # - Si hay L/C => necesito f>0 (porque Z depende de w).
    # - Si NO hay L/C y f<=0 => asumo f=1 Hz (arbitrario, no afecta R/Z/I/V).
    if has_LC and f <= 0:
        _clip("Aviso",["Hay L/C: se requiere f>0 para calcular jwL y 1/(jwC)."])
        return
    if (not has_LC) and f <= 0:
        f = 1.0  # valor simbólico; solo R/Z/I/V no dependen de f

    A,z,node_list,vsrcs,w = _stamp_ac(elems, f)
    sol = _gauss_solve_cpx(A, z)
    lines=[]; i=0
    while i<len(node_list):
        lines.append("V({}) = {}".format(node_list[i], "{:s}".format(_fmt_polar(sol[i])))); i+=1
    if not lines: lines=["(sin nodos distintos de 0)"]
    _clip("Resultados AC", lines)

    def _res_elem():
        l=_element_results_ac(elems,node_list,vsrcs,sol,w)
        if not l: l=["(Sin elementos)"]
        _clip("Elementos AC", l)

    def _pot_total():
        l=_element_results_ac(elems,node_list,vsrcs,sol,w)
        P=0.0; Q=0.0
        for ln in l:
            if "P=" in ln and "Q=" in ln:
                try:
                    P+=float(ln.split("P=")[1].split("W")[0].strip())
                    Q+=float(ln.split("Q=")[1].split("var")[0].strip())
                except:
                    pass
        Sm=(P*P+Q*Q)**0.5; fp=(0.0 if Sm==0 else P/Sm)
        _clip("Potencia total",[
            "P = {:.6g} W".format(P),
            "Q = {:.6g} var".format(Q),
            "|S| = {:.6g} VA".format(Sm),
            "fp = {:.4f} ({})".format(fp, "adelantado" if Q<0 else ("atrasado" if Q>0 else "unitario")),
        ])

    def _ver_pasos():
        _clip_steps("Pasos (MNA AC)")

    def _formulas():
        hasL = any(k=="L" for (k,_,_,_) in elems)
        hasC = any(k=="C" for (k,_,_,_) in elems)
        lines = ["w = 2πf = {:.6g} rad/s".format(w)]
        if hasL: lines.append("Inductor: Z_L = j w L,   X_L = w L")
        if hasC: lines.append("Capacitor: Z_C = 1/(j w C),  |X_C| = 1/(w C)")
        _clip("Formulas usadas", lines)

    while True:
        fn=_menu("Mas resultados",[
            ("Resumen por elemento", _res_elem),
            ("Potencia total", _pot_total),
            ("Pasos (MNA)", _ver_pasos),
            ("Formulas usadas", _formulas),
        ])
        if fn is None: break
        fn()

def app():
    items=[
        ("Nodos DC (MNA)", nodos_dc),
        ("Nodos AC (fasor)", nodos_ac),
    ]
    while True:
        fn=_menu("Analisis por Nodos", items)
        if fn is None: return
        try: fn()
        except Exception as e: view_text_from_string("Error", str(e)); _pause()

if __name__ == "__main__":
    app()
