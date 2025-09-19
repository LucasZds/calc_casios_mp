# ui.py — prints con paginacion horizontal (+/-) y avance vertical (Enter)

# configuracion basica
SCREEN_LINES = 7   # alto total de pantalla (lineas)
COLS         = 21  # ancho de "ventana" horizontal (caracteres visibles por pagina)

# utilidades basicas
def clear():
    print("\n"*SCREEN_LINES)

def pause(msg="\n[Enter]..."):
    try: input(msg)
    except: pass

def set_cols(n):
    """cambia el ancho de la ventana horizontal (min 8)"""
    global COLS
    try:
        n = int(n)
        if n >= 8:
            COLS = n
    except:
        pass

def set_screen_lines(n):
    """cambia la cantidad de lineas totales (incluye titulo y prompt)"""
    global SCREEN_LINES
    try:
        n = int(n)
        if n >= 4:
            SCREEN_LINES = n
    except:
        pass

# helpers internos
def _slice_h(s, col, w):
    """toma un recorte horizontal de s desde col, ancho w"""
    s = str(s)
    if col < 0: col = 0
    if col > len(s): col = len(s)
    return s[col:col+w]

def _lines_from_text(text):
    """convierte texto con \\n en lista de lineas (sin \\n)"""
    if isinstance(text, list):
        return [str(x) for x in text]
    t = str(text).split("\n")
    out=[]
    for r in t:
        # evitamos caracteres raros
        out.append(r.replace("\r",""))
    return out

def view_menu(title, lines, cols=None, lines_per_screen=None):
    if cols is None: cols = COLS
    LPP = (lines_per_screen or SCREEN_LINES) - 2
    if LPP < 1: LPP = 1

    n   = len(lines)
    i   = 0
    col = 0

    while True:
        clear()
        print("%s %d/%d" % (title, col, col + cols - 1))

        end = i + LPP
        if end > n: end = n

        k = i
        while k < end:
            ln = lines[k]
            if not isinstance(ln, str):
                ln = str(ln)
            shown = "[" + str(k+1) + "] " + ln   # numeración al vuelo
            print(_slice_h(shown, col, cols))
            k += 1

        op = input("+/- nro o 0: ").strip()
        if op == "0":
            return None
        if op and op.isdigit():
            sel = int(op) - 1
            if 0 <= sel < n:
                return sel
            # fuera de rango: ignoramos y seguimos
            continue
        if op[:1] == "+": 
            col += cols
            continue
        if op[:1] == "-":
            col -= cols
            if col < 0: col = 0
            continue
        # Enter u otra cosa: avanza vertical
        if end >= n: 
            i = 0
        else:
            i = end

# API principal
def view_text(title, lines, cols=None, lines_per_screen=None):
    """
    Muestra 'lines' (lista de strings) con:
      - scroll horizontal con + (derecha) y - (izquierda)
      - avance vertical por tandas con Enter
      - [0] para volver
    """
    if cols is None: cols = COLS
    LPP = (lines_per_screen or SCREEN_LINES) - 2  # 1 titulo + 1 prompt
    if LPP < 1: LPP = 1

    n = len(lines)
    i   = 0        # indice vertical (linea de inicio)
    col = 0        # desplazamiento horizontal

    while True:
        clear()
        # cabecera
        print("%s %d/%d" % (title, col, col + cols - 1))
        # cuerpo
        end = i + LPP
        if end > n: end = n
        k = i
        while k < end:
            ln = lines[k]
            if not isinstance(ln, str):
                ln = str(ln)
            print(_slice_h(ln, col, cols))
            k += 1
        # prompt
        op = input("+/- 0/exe: ").strip()
        if op == "0":
            return
        if op[:1] == "+":
            col += cols
            continue
        if op[:1] == "-":
            col -= cols
            if col < 0: col = 0
            continue
        # cualquier otra cosa (incluido Enter) avanza vertical
        if end >= n:
            # ya estamos al final; reinicia vertical
            i = 0
        else:
            i = end

def view_line(title, s, cols=None):
    """
    Muestra una sola linea larga con scroll horizontal (+/-).
    Enter solo refresca. [0] vuelve.
    """
    if cols is None: cols = COLS
    col = 0
    text = str(s)
    while True:
        clear()
        print("%s  (col=%d..%d)" % (title, col, col + cols - 1))
        print(_slice_h(text, col, cols))
        op = input("+/- 0/exe: ").strip()
        if op == "0": return
        if op[:1] == "+": col += cols
        elif op[:1] == "-":
            col -= cols
            if col < 0: col = 0

def view_text_from_string(title, text, cols=None, lines_per_screen=None):
    """
    Igual a view_text, pero recibe un bloque de texto con \\n.
    """
    return view_text(title, _lines_from_text(text), cols, lines_per_screen)

def view_file(title, path, cols=None, lines_per_screen=None):
    """
    Muestra un archivo de texto (si el entorno lo permite).
    """
    try:
        with open(path, "r") as f:
            lines = [ln.rstrip("\n\r") for ln in f]
    except Exception as e:
        lines = ["no pude abrir:", str(e)]
    return view_text(title, lines, cols, lines_per_screen)
