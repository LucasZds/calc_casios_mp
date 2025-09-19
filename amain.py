# main.py — Menu paginado con view_menu (+/- para navegar, numero para entrar)
# Cada modulo debe tener def app()

from ui_py import view_menu
APPS = [
    ("Conversiones", "conversion"),
    ("Derivadas",    "derivadas"),
    ("Fisica",       "fisica"),
    ("Fundamentos",  "fundamentos"),
    ("Integrales",   "integrales"),
    ("TDC",          "tdc"),
    ("Trigonometria","trigonometria"),
    ("Vectores",     "vectores"),
    ("Despeje",      "despeje"),
    ("py-help",      "atajos"),
    # agrega mas modulos...
]

def _pause(msg="\n[Enter] para continuar..."):
    try:
        input(msg)
    except:
        pass

def _clear():
    print("\n" * 8)

def _run_module(modname):
    _clear()
    try:
        m = __import__(modname)
        if hasattr(m, "app"):
            m.app()
        else:
            print("El modulo '%s' no define app()." % modname)
    except Exception as e:
        print("No pude ejecutar '%s': %s" % (modname, e))
    _pause()

def main():
    lineas = []
    i = 0
    while i < len(APPS):
        lineas.append(str(APPS[i][0]))
        i += 1

    while True:
        sel = view_menu("- CV1.0", lineas)
        if sel is None:
            break

        if 0 <= sel < len(APPS):
            _run_module(APPS[sel][1])
        else:
            print("Seleccion fuera de rango.")
            _pause()

    _clear()
    print("Hasta la proxima.")



# Auto-run (la Casio hace: from main import *)
main()
