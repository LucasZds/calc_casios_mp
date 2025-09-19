# conversion.py — solo conversiones, + y - para navegar, prompts en 2 lineas
import math
# ===== UI basica (7 lineas) =====
from ui_py import view_text, view_menu  # usa tu UI de scroll horizontal y avance con Enter

def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _ask_float(label):
    print(label)
    s = input("> ").strip()
    try:
        # Soporta coma decimal (ej: "3,5")
        s = s.replace(",", ".")
        return float(s)
    except:
        return 0.0

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



def _dispatch(title, items):
    # corre un submenu y permanece hasta que el usuario elija 0
    while True:
        fn = _menu(title, items)
        if fn is None:
            return
        try:
            fn()
        except Exception as e:
            print("Error:", e)
            _pause()

def _make_conv(factor, label_in, label_out):
    def fn():
        x = _ask_float(label_in)
        print(label_out, "=", x * factor)
        _pause()
    return fn

# ===== Angulos =====
def _ang_deg2rad():
    x = _ask_float("grados:")
    print("rad =", x * math.pi / 180.0); _pause()

def _ang_rad2deg():
    x = _ask_float("radianes:")
    print("grados =", x * 180.0 / math.pi); _pause()

def _menu_angulos():
    items = [
        ("grados -> rad", _ang_deg2rad),
        ("rad -> grados", _ang_rad2deg),
    ]
    _dispatch("Angulos", items)

# ===== Temperatura =====
def _t_c2f():  c = _ask_float("Celsius:");    print("F =",  c*9.0/5.0+32.0); _pause()
def _t_f2c():  f = _ask_float("Fahrenheit:"); print("C =", (f-32.0)*5.0/9.0); _pause()
def _t_c2k():  c = _ask_float("Celsius:");    print("K =",  c+273.15); _pause()
def _t_k2c():  k = _ask_float("Kelvin:");     print("C =",  k-273.15); _pause()

def _menu_temp():
    items = [("C -> F", _t_c2f), ("F -> C", _t_f2c), ("C -> K", _t_c2k), ("K -> C", _t_k2c)]
    _dispatch("Temperatura", items)

# ===== Longitud =====
_len_m2km = _make_conv(1.0/1000.0, "m:", "km")
_len_km2m = _make_conv(1000.0, "km:", "m")
_len_in2cm = _make_conv(2.54, "pulgadas:", "cm")
_len_ft2m  = _make_conv(0.3048, "pies:", "m")
_len_m2ft  = _make_conv(1.0/0.3048, "m:", "ft")

def _menu_longitud():
    items = [
        ("m -> km", _len_m2km),
        ("km -> m", _len_km2m),
        ("in -> cm", _len_in2cm),
        ("ft -> m", _len_ft2m),
        ("m -> ft", _len_m2ft),
    ]
    _dispatch("Longitud", items)

# ===== Masa =====
_mass_kg2g  = _make_conv(1000.0, "kg:", "g")
_mass_g2kg  = _make_conv(1.0/1000.0, "g:", "kg")
_mass_lb2kg = _make_conv(0.45359237, "lb:", "kg")
_mass_kg2lb = _make_conv(1.0/0.45359237, "kg:", "lb")

def _menu_masa():
    items = [
        ("kg -> g", _mass_kg2g),
        ("g -> kg", _mass_g2kg),
        ("lb -> kg", _mass_lb2kg),
        ("kg -> lb", _mass_kg2lb),
    ]
    _dispatch("Masa", items)

# ===== Velocidad =====
_vel_kmh2ms = _make_conv(1.0/3.6, "km/h:", "m/s")
_vel_ms2kmh = _make_conv(3.6, "m/s:", "km/h")

def _menu_vel():
    items = [("km/h -> m/s", _vel_kmh2ms), ("m/s -> km/h", _vel_ms2kmh)]
    _dispatch("Velocidad", items)

# ===== Presion =====
_press_pa2bar  = _make_conv(1.0/1e5, "Pa:", "bar")
_press_bar2pa  = _make_conv(1e5, "bar:", "Pa")
_press_bar2psi = _make_conv(14.5037738, "bar:", "psi")
_press_psi2bar = _make_conv(1.0/14.5037738, "psi:", "bar")

def _menu_presion():
    items = [
        ("Pa -> bar", _press_pa2bar),
        ("bar -> Pa", _press_bar2pa),
        ("bar -> psi", _press_bar2psi),
        ("psi -> bar", _press_psi2bar),
    ]
    _dispatch("Presion", items)

# ===== Energia =====
_en_Wh2J = _make_conv(3600.0, "Wh:", "J")
_en_J2Wh = _make_conv(1.0/3600.0, "J:", "Wh")

def _menu_energia():
    items = [("Wh -> J", _en_Wh2J), ("J -> Wh", _en_J2Wh)]
    _dispatch("Energia", items)

# ===== Potencia (W <-> dBm) =====
def _p_w2dbm():
    w = _ask_float("W:")
    if w <= 0:
        print("dBm = -inf")
    else:
        print("dBm =", 10.0*math.log10(w) + 30.0)
    _pause()

def _p_dbm2w():
    dbm = _ask_float("dBm:")
    print("W =", 10.0 ** ((dbm - 30.0) / 10.0)); _pause()

def _menu_potencia():
    items = [("W -> dBm", _p_w2dbm), ("dBm -> W", _p_dbm2w)]
    _dispatch("Potencia", items)

# ===== Frecuencia / Periodo =====
def _f_hz2T():
    x = _ask_float("Hz:")
    if x == 0:
        print("periodo = infinito")
    else:
        print("periodo [s] =", 1.0/x)
    _pause()

def _f_T2hz():
    x = _ask_float("periodo [s]:")
    if x == 0:
        print("Hz = infinito")
    else:
        print("Hz =", 1.0/x)
    _pause()

def _menu_freq():
    items = [("Hz -> periodo", _f_hz2T), ("periodo -> Hz", _f_T2hz)]
    _dispatch("Frecuencia/Periodo", items)

# ===== Tiempo =====
_t_h2s   = _make_conv(3600.0, "horas:", "s")
_t_min2s = _make_conv(60.0, "min:", "s")
_t_s2h   = _make_conv(1.0/3600.0, "s:", "h")
_t_s2min = _make_conv(1.0/60.0, "s:", "min")

def _menu_tiempo():
    items = [("h -> s", _t_h2s), ("min -> s", _t_min2s), ("s -> h", _t_s2h), ("s -> min", _t_s2min)]
    _dispatch("Tiempo", items)

# ===== Datos (base 1000 y 1024) =====
_dat_b2KB_1000   = _make_conv(1.0/1000.0, "bytes:", "KB (1000)")
_dat_KB2b_1000   = _make_conv(1000.0, "KB (1000):", "bytes")
_dat_KB2MB_1000  = _make_conv(1.0/1000.0, "KB (1000):", "MB (1000)")
_dat_MB2KB_1000  = _make_conv(1000.0, "MB (1000):", "KB (1000)")
_dat_b2KB_1024   = _make_conv(1.0/1024.0, "bytes:", "KB (1024)")
_dat_KB2b_1024   = _make_conv(1024.0, "KB (1024):", "bytes")
_dat_KB2MB_1024  = _make_conv(1.0/1024.0, "KB (1024):", "MB (1024)")
_dat_MB2KB_1024  = _make_conv(1024.0, "MB (1024):", "KB (1024)")

def _menu_datos():
    items = [
        ("bytes -> KB (1000)", _dat_b2KB_1000),
        ("KB (1000) -> bytes", _dat_KB2b_1000),
        ("KB (1000) -> MB", _dat_KB2MB_1000),
        ("MB (1000) -> KB", _dat_MB2KB_1000),
        ("bytes -> KB (1024)", _dat_b2KB_1024),
        ("KB (1024) -> bytes", _dat_KB2b_1024),
        ("KB (1024) -> MB", _dat_KB2MB_1024),
        ("MB (1024) -> KB", _dat_MB2KB_1024),
    ]
    _dispatch("Datos", items)

# ===== Prefijos SI generico =====
def _menu_si():
    mp = {"p":-12,"n":-9,"u":-6,"m":-3,"":0,"k":3,"M":6,"G":9,"T":12}
    print("Prefijos: p n u m (vacio) k M G T")
    val = _ask_float("valor:")
    print("prefijo origen:")
    p_from = input("> ").strip()
    print("prefijo destino:")
    p_to = input("> ").strip()
    print("unidad (A, V, ohm, F, H, etc):")
    unit = input("> ").strip() or "u"
    e_from = mp[p_from] if p_from in mp else 0
    e_to   = mp[p_to]   if p_to   in mp else 0
    out = val * (10 ** (e_from - e_to))
    pref = p_to if p_to in mp else ""
    print(pref + unit, "=", out)
    try:
        print("cientifico =", "{:.6e}".format(out))
    except:
        pass
    _pause()

# ===== Electricas (solo conversiones) =====
def _mA_a_A():    x = _ask_float("mA:");    print("A =",    x/1000.0); _pause()
def _A_a_mA():    x = _ask_float("A:");     print("mA =",   x*1000.0); _pause()
def _mV_a_V():    x = _ask_float("mV:");    print("V =",    x/1000.0); _pause()
def _V_a_mV():    x = _ask_float("V:");     print("mV =",   x*1000.0); _pause()
def _kOhm_a_Ohm():x = _ask_float("kOhm:");  print("Ohm =",  x*1000.0); _pause()
def _Ohm_a_kOhm():x = _ask_float("Ohm:");   print("kOhm =", x/1000.0); _pause()
def _uF_a_nF():   x = _ask_float("uF:");    print("nF =",   x*1000.0); _pause()
def _nF_a_uF():   x = _ask_float("nF:");    print("uF =",   x/1000.0); _pause()
def _mH_a_H():    x = _ask_float("mH:");    print("H =",    x/1000.0); _pause()
def _H_a_mH():    x = _ask_float("H:");     print("mH =",   x*1000.0); _pause()

def _menu_electricas():
    items = [
        ("mA -> A", _mA_a_A),
        ("A -> mA", _A_a_mA),
        ("mV -> V", _mV_a_V),
        ("V -> mV", _V_a_mV),
        ("kOhm -> Ohm", _kOhm_a_Ohm),
        ("Ohm -> kOhm", _Ohm_a_kOhm),
        ("uF -> nF", _uF_a_nF),
        ("nF -> uF", _nF_a_uF),
        ("mH -> H", _mH_a_H),
        ("H -> mH", _H_a_mH),
    ]
    _dispatch("Electricas", items)

# ===== app =====
def app():
    items = [
        ("Angulos", _menu_angulos),
        ("Temperatura", _menu_temp),
        ("Longitud", _menu_longitud),
        ("Masa", _menu_masa),
        ("Velocidad", _menu_vel),
        ("Presion", _menu_presion),
        ("Energia", _menu_energia),
        ("Potencia", _menu_potencia),
        ("Frecuencia/Periodo", _menu_freq),
        ("Tiempo", _menu_tiempo),
        ("Datos", _menu_datos),
        ("SI generico", _menu_si),
        ("Electricas", _menu_electricas),
    ]
    while True:
        fn = _menu("Conversiones", items)
        if fn is None:
            return
        try:
            fn()
        except Exception as e:
            print("Error:", e)
            _pause()

if __name__ == "__main__":
    app()
