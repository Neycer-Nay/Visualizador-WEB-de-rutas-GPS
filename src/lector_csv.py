

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class DatosGPS:
    """Estructura para los datos GPS basicos."""

    tiempo: pd.Series
    latitud: pd.Series
    longitud: pd.Series


def _validar_columnas(df: pd.DataFrame, columnas: Iterable[str]) -> None:
    faltantes = [col for col in columnas if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {', '.join(faltantes)}")


def _validar_nulos(df: pd.DataFrame, columnas: Iterable[str]) -> None:
    if df[list(columnas)].isnull().any().any():
        raise ValueError("Se encontraron valores nulos en las columnas obligatorias.")


def _validar_rangos(latitud: pd.Series, longitud: pd.Series) -> None:
    if ((latitud < -90) | (latitud > 90)).any():
        raise ValueError("Se encontraron latitudes fuera del rango [-90, 90].")
    if ((longitud < -180) | (longitud > 180)).any():
        raise ValueError("Se encontraron longitudes fuera del rango [-180, 180].")


def leer_datos_gps(ruta_csv: str | Path) -> DatosGPS:
    """Lee y valida datos GPS desde un archivo CSV."""

    ruta = Path(ruta_csv)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {ruta}")

    df = pd.read_csv(ruta)
    columnas = ["tiempo", "latitud", "longitud"]
    _validar_columnas(df, columnas)
    _validar_nulos(df, columnas)

    df["tiempo"] = pd.to_datetime(df["tiempo"], errors="raise")
    df["latitud"] = pd.to_numeric(df["latitud"], errors="raise")
    df["longitud"] = pd.to_numeric(df["longitud"], errors="raise")
    _validar_rangos(df["latitud"], df["longitud"])

    df = df.sort_values("tiempo").reset_index(drop=True)
    return DatosGPS(df["tiempo"], df["latitud"], df["longitud"])
