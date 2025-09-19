# fisica.py — menu agregador; carga submodulos solo al usarlos
from ui_py import view_menu, view_text_from_string

_SECCIONES = [
    ("Cinematica / Dinamica",                 "fisica_1"),
    ("Energia / Trabajo / Potencia / Circular","fisica_2"),
    ("Resorte / Rotacion",                    "fisica_3"),
    ("Poleas / Colisiones / Pendulo",         "fisica_4"),
    ("Formulario de fisica",                  "fisica_formulario"),
]

def _run_sub(modname):
    try:
        m = __import__(modname)
        if hasattr(m, "app"):
            m.app()
    except Exception as e:
        view_text_from_string("Error", "No pude ejecutar " + str(modname) + ":\n" + str(e))
    try:
        import gc
        gc.collect()
    except:
        pass

def app():
    labels = []
    i = 0
    while i < len(_SECCIONES):
        labels.append(_SECCIONES[i][0])
        i += 1

    while True:
        sel = view_menu("Fisica v1", labels)
        if sel is None: return
        if 0 <= sel < len(_SECCIONES):
            _run_sub(_SECCIONES[sel][1])
