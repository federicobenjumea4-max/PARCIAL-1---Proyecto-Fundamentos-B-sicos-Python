"""
Módulo API
----------
Se encarga de TODO lo que tiene que ver con los datos:
leer el Excel, limpiarlo, filtrar y calcular las medianas.
No imprime ni pide nada por consola (eso lo hace el módulo ui).
"""
import datetime
import unicodedata

import pandas as pd

RUTA_EXCEL = "resultado_laboratorio_suelo.xlsx"

# Si el Excel trae números enormes en P y K (por los decimales perdidos),
# con True se intentan reescalar; con False esos valores se descartan.
REESCALAR_NUMEROS_GRANDES = True

# Columna del Excel -> nombre corto que usamos en el código
COLUMNAS = {
    "Departamento": "departamento",
    "Municipio": "municipio",
    "Cultivo": "cultivo",
    "Topografia": "topografia",
    "pH agua:suelo 2,5:1,0": "ph",
    "Fósforo (P) Bray II mg/kg": "fosforo",
    "Potasio (K) intercambiable cmol(+)/kg": "potasio",
}


# ---------------------------------------------------------------- texto
def normalizar(texto):
    """Pasa a mayúsculas y quita tildes y espacios sobrantes (para comparar)."""
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFD", texto.strip().upper())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.split())


# ------------------------------------------------------------- limpieza
def texto_a_numero(texto):
    """'5,26' -> 5.26. Valores como '<3,87' o 'ND' no son números: NaN."""
    texto = texto.strip().replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return float("nan")


def fecha_a_decimal(fecha):
    """
    Excel convirtió algunos decimales en fechas (6.05 -> 6 de mayo).
    Se recupera como día + mes/100.
    """
    return fecha.day + fecha.month / 100


def cantidad_digitos(valor):
    return len(str(int(abs(valor))))


def limpiar_ph(valor):
    if isinstance(valor, datetime.datetime):
        return fecha_a_decimal(valor)
    if isinstance(valor, str):
        valor = texto_a_numero(valor)
    if isinstance(valor, (int, float)) and 0 < valor <= 14:
        return float(valor)
    return float("nan")


def limpiar_fosforo(valor):
    if isinstance(valor, datetime.datetime):
        return fecha_a_decimal(valor)
    if isinstance(valor, str):
        return texto_a_numero(valor)
    if isinstance(valor, (int, float)) and valor == valor:
        if valor < 1000:
            return float(valor)
        if REESCALAR_NUMEROS_GRANDES:
            digitos = cantidad_digitos(valor)
            if digitos >= 16:
                return valor / 10 ** 15
            if digitos == 15:
                return valor / 10 ** 14
    return float("nan")


def limpiar_potasio(valor):
    if isinstance(valor, datetime.datetime):
        return fecha_a_decimal(valor)
    if isinstance(valor, str):
        return texto_a_numero(valor)
    if isinstance(valor, (int, float)) and valor == valor:
        if 0 <= valor < 10:
            return float(valor)
        if REESCALAR_NUMEROS_GRANDES:
            # se asume que era 0,xxxx: el punto decimal quedó antes de los dígitos
            return valor / 10 ** cantidad_digitos(valor)
    return float("nan")


def cargar_datos(ruta=RUTA_EXCEL):
    """Lee el Excel y devuelve un DataFrame limpio."""
    df = pd.read_excel(ruta, usecols=list(COLUMNAS))
    df = df.rename(columns=COLUMNAS)

    df["ph"] = df["ph"].map(limpiar_ph)
    df["fosforo"] = df["fosforo"].map(limpiar_fosforo)
    df["potasio"] = df["potasio"].map(limpiar_potasio)
    df["topografia"] = df["topografia"].fillna("No indica")

    # columnas auxiliares para buscar sin importar tildes/mayúsculas
    for col in ("departamento", "municipio", "cultivo"):
        df[col + "_norm"] = df[col].map(normalizar)
    return df


# ------------------------------------------------------------- consulta
def filtrar(df, departamento, municipio, cultivo, n_registros):
    """Registros que coinciden con la consulta (máximo n_registros)."""
    filtro = (
        (df["departamento_norm"] == normalizar(departamento))
        & (df["municipio_norm"] == normalizar(municipio))
        & (df["cultivo_norm"] == normalizar(cultivo))
    )
    return df[filtro].head(n_registros)


def calcular_resumen(registros):
    """
    Agrupa por topografía y calcula la mediana de pH, P y K.
    Devuelve una lista de diccionarios (una por fila de la tabla).
    """
    if registros.empty:
        return []
    claves = ["departamento", "municipio", "cultivo", "topografia"]
    tabla = (
        registros.groupby(claves)
        .agg(
            registros=("ph", "size"),
            ph=("ph", "median"),
            fosforo=("fosforo", "median"),
            potasio=("potasio", "median"),
        )
        .reset_index()
    )
    return tabla.to_dict("records")


def consultar(df, departamento, municipio, cultivo, n_registros):
    """Función principal de la API: filtra y calcula."""
    registros = filtrar(df, departamento, municipio, cultivo, n_registros)
    return calcular_resumen(registros)


# ----------------------------------------------------------- sugerencias
def _unicos(serie):
    return sorted(serie.dropna().unique())


def diagnosticar(df, departamento, municipio, cultivo):
    """
    Cuando la consulta no devuelve nada, dice qué dato no existe
    y qué opciones válidas hay. Devuelve (mensaje, lista_de_opciones).
    """
    dep = df[df["departamento_norm"] == normalizar(departamento)]
    if dep.empty:
        return "No encontré ese departamento. Los disponibles son:", _unicos(df["departamento"])

    mun = dep[dep["municipio_norm"] == normalizar(municipio)]
    if mun.empty:
        return "No encontré ese municipio en el departamento. Los disponibles son:", _unicos(dep["municipio"])

    return "No encontré ese cultivo en el municipio. Los disponibles son:", _unicos(mun["cultivo"])
