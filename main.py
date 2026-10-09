"""
Programa principal: solo conecta el módulo UI con el módulo API.
Uso:  python main.py [ruta_del_excel]
"""
import sys

from api import suelos
from ui import consola


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else suelos.RUTA_EXCEL

    consola.mostrar_bienvenida()
    consola.mostrar_mensaje("Cargando datos, un momento...")
    try:
        df = suelos.cargar_datos(ruta)
    except FileNotFoundError:
        consola.mostrar_mensaje(f"No encontré el archivo '{ruta}'. Ponlo junto a main.py.")
        return

    seguir = True
    while seguir:
        datos = consola.pedir_datos_consulta()
        filas = suelos.consultar(
            df, datos["departamento"], datos["municipio"],
            datos["cultivo"], datos["n_registros"],
        )
        if filas:
            consola.mostrar_tabla(filas)
        else:
            mensaje, opciones = suelos.diagnosticar(
                df, datos["departamento"], datos["municipio"], datos["cultivo"]
            )
            consola.mostrar_opciones(mensaje, opciones)
        seguir = consola.preguntar_si_continuar()

    consola.mostrar_mensaje("¡Hasta luego!")


if __name__ == "__main__":
    main()
