# 📟 Casio FX-9750GIII Toolkit (MicroPython)

Un conjunto de herramientas interactivas diseñado para la calculadora Casio fx-9750GIII con soporte MicroPython.  
Incluye utilidades de matemáticas, física e ingeniería, optimizadas para las limitaciones de pantalla (7×21) y memoria del dispositivo.

## 🚀 Características

- **Menú Interactivo**: Navegación con teclas `+`, `-` y `Enter`  
- **Módulos Temáticos**:
  - `fisica.py`: fórmulas de cinemática, dinámica, trabajo y energía
  - `integrales.py`: integrales comunes y polinomios de Maclaurin
  - `derivadas.py`: derivación simbólica con funciones trigonométricas, exponenciales y logarítmicas
  - `fundamentos.py`: conversiones de unidades y constantes
  - `despeje.py`: aislado automático de variables en fórmulas
  - `trigonometria.py`: identidades y funciones trigonométricas
- **UI Optimizada**: funciones como `view_text`, `view_menu` y paginado automático
- **Diccionario de Fórmulas**: precálculo de derivadas/funciones para consulta rápida
- **Portable**: pensado para scripts ≤150 líneas y uso modular en múltiples archivos

## 📋 Requisitos del Sistema

- Calculadora **Casio fx-9750GIII** (o modelo con soporte MicroPython)  
- Software FA-124 / Graph 3 para transferir scripts vía USB  
- Python 3.x (opcional, para generar diccionarios de funciones en PC)

## 🔧 Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/LucasZds/calc_casio_mp.git
   cd calc_casio_mp
   ```
2. Conecta la calculadora y abre FA-124/Graph 3  
3. Importa los archivos `.py` dentro de la carpeta `main` de la calculadora  
4. Ejecuta `amain.py` desde el menú MicroPython de la Casio  

## 📱 Uso

### Navegación
- `+` → Página siguiente (Horizontal) - slice 
- `-` → Página anterior  (Horizontal) - slice 
- `Enter` → Seleccionar opción (Vertical)  
- `0` → Volver  

### Ejemplos
- **Derivadas**: Ingresa `cos(x)` y obtén d1(x), d2(x)…  
- **Despeje**: Escribe `v^2 = v0^2 + 2*a*x` → aísla `a`  
- **Física**: Selecciona "MRUA" y calcula posición, velocidad o tiempo  
- **Integrales**: Consulta integrales comunes y polinomios de Maclaurin  

## 🎨 Interfaz

- Pantalla de **7 líneas × 21 caracteres**  
- Textos con paginado automático  
- Menús jerárquicos y simples, pensados para cálculo rápido en examen  

## 🛠️ Desarrollo

### Estructura del Proyecto
```
casio_fx9750giii_toolkit/
├── amain.py          # Menú principal
├── ui_py.py         # Funciones de interfaz (view_text, view_menu, etc.)
├── despeje.py       # Motor para aislar variables
├── derivadas.py     # Derivación simbólica
├── integrales.py    # Integrales comunes y Maclaurin
├── fisica.py        # Fórmulas físicas
├── fundamentos.py   # Conversiones y constantes
├── vectores.py       # Operaciones y análisis vectorial
├── trigonometria.py  # Identidades y funciones trigonométricas
├── conversion.py     # Conversión de unidades
└── README.md        # Este archivo
```

### Tecnologías Utilizadas
- **MicroPython** (Casio fx-9750GIII)  
- **Python 3.x** (para preprocesar diccionarios en PC)  

## 📊 Funcionalidades Futuras

- [-] Gráficas básicas en ASCII  
- [-] Módulo de probabilidad y estadística  
- [-] Modo examen con fórmulas rápidas  
- [-] Librería externa con >1000 derivadas precalculadas  

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!  
1. Haz un fork  
2. Crea tu rama: `git checkout -b feature/nueva-funcionalidad`  
3. Commit: `git commit -am "Agrego módulo nuevo"`  
4. Push: `git push origin feature/nueva-funcionalidad`  
5. Abre un Pull Request  

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE).

## 👨‍💻 Autor

**Lucas** - [LucasZds](https://github.com/LucasZds)

## 🙏 Agradecimientos

- Comunidad de usuarios de calculadoras Casio  
- Librerías abiertas como SymPy (para preprocesar en PC)   

---

⭐ Si te resulta útil, ¡no olvides darle una estrella en GitHub!
