# ==== tdc.py (launcher) ====
from ui_py import view_menu, view_text_from_string

# --- helpers minimos ---
def _pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def _menu(title, items):
    textos=[t for (t,_) in items]
    try:
        sel = view_menu(title, textos)
    except:
        sel = None
    if sel is None: return None
    return items[sel][1]

# gc/sys defensivo
try:
    import gc
except:
    gc = None

try:
    import sys
except:
    sys = None

def _call(modname, funcname):
    # import on demand para ahorrar RAM
    M = __import__(modname)
    try:
        getattr(M, funcname)()
    except Exception as e:
        view_text_from_string("Error", str(e)); _pause()
    # liberar referencias
    try:
        delattr(M, funcname)
    except:
        pass
    try:
        del M
    except:
        pass
    if sys:
        try:
            if modname in sys.modules:
                del sys.modules[modname]
        except:
            pass
    if gc:
        try: gc.collect()
        except: pass

# --- wrappers del menú principal ---
def _run_basics():
    _call("tdc_1", "app")

def _run_mna():
    _call("tdc_2", "app")

def _run_plots():
    _call("tdc_3", "app")

def app():
    items = [
        ("Calcs", _run_basics),
        ("Analisis por Nodos (DC/AC)", _run_mna),
        ("Graficos y Ejemplos AC", _run_plots),
    ]
    while True:
        fn = _menu("TDC", items)
        if fn is None: return
        fn()

if __name__ == "__main__":
    app()
