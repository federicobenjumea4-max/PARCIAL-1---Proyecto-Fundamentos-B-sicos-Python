"""
Módulo UI
---------
Todo lo que el usuario ve y escribe por consola.
No sabe nada del Excel ni de pandas: solo recibe y muestra datos.
"""


def mostrar_bienvenida():
    print("=" * 60)
    print("  CONSULTA DE PROPIEDADES EDÁFICAS (SUELOS DE COLOMBIA)")
    print("=" * 60)


def mostrar_mensaje(mensaje):
    print(mensaje)


def pedir_texto(mensaje):
    """Pide un texto y no deja continuar si queda vacío."""
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("  -> No puede estar vacío, intenta de nuevo.")


def pedir_entero_positivo(mensaje):
    """Pide un número entero mayor que 0."""
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit() and int(valor) > 0:
            return int(valor)
        print("  -> Escribe un número entero mayor que 0.")


def pedir_datos_consulta():
    """Pide los 4 datos de la consulta y los devuelve en un diccionario."""
    print()
    return {
        "departamento": pedir_texto("Departamento: "),
        "municipio": pedir_texto("Municipio: "),
        "cultivo": pedir_texto("Cultivo: "),
        "n_registros": pedir_entero_positivo("Número de registros a consultar: "),
    }


def mostrar_opciones(mensaje, opciones):
    print(f"\n{mensaje}")
    for opcion in opciones:
        print(f"  - {opcion}")


def _formato(valor):
    return "N/D" if valor != valor else f"{valor:.2f}"


def mostrar_tabla(filas):
    """Imprime la tabla de resultados (filas = lista de diccionarios)."""
    encabezados = ["Departamento", "Municipio", "Cultivo", "Topografía",
                   "Regs", "Mediana pH", "Mediana P", "Mediana K"]
    datos = [
        [f["departamento"], f["municipio"], f["cultivo"], f["topografia"],
         str(f["registros"]), _formato(f["ph"]), _formato(f["fosforo"]), _formato(f["potasio"])]
        for f in filas
    ]
    anchos = [max(len(fila[i]) for fila in [encabezados] + datos) for i in range(len(encabezados))]

    def linea(fila):
        return " | ".join(celda.ljust(anchos[i]) for i, celda in enumerate(fila))

    print()
    print(linea(encabezados))
    print("-+-".join("-" * a for a in anchos))
    for fila in datos:
        print(linea(fila))
    print("\nP en mg/kg (Bray II) y K en cmol(+)/kg. N/D = sin datos válidos.")


def preguntar_si_continuar():
    respuesta = input("\n¿Hacer otra consulta? (s/n): ").strip().lower()
    return respuesta in ("s", "si", "sí")
