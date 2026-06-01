

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EstadisticasRuta:
    """Estadisticas basicas de una trayectoria."""

    distancia_total_km: float
    duracion_segundos: float
    velocidad_media_kmh: float
    velocidad_maxima_kmh: float


def asegurar_directorio(path: str | Path) -> Path:
    """Crea el directorio si no existe y devuelve el Path."""

    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def _valor_tiempo(tiempos: Sequence[pd.Timestamp], indice: int) -> pd.Timestamp:
    if hasattr(tiempos, "iloc"):
        return tiempos.iloc[indice]
    return tiempos[indice]


def convertir_tiempo_a_segundos(tiempos: Sequence[pd.Timestamp]) -> np.ndarray:
    """Convierte una secuencia de timestamps a segundos desde el inicio."""

    if len(tiempos) == 0:
        return np.array([])
    inicio = _valor_tiempo(tiempos, 0)
    return np.array([(t - inicio).total_seconds() for t in tiempos], dtype=float)


def crear_tiempo_interpolado(
    inicio: pd.Timestamp, segundos: Iterable[float]
) -> list[datetime]:
    """Crea una lista de timestamps a partir de segundos desde el inicio."""

    return [inicio.to_pydatetime() + timedelta(seconds=float(s)) for s in segundos]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia entre dos puntos geograficos usando Haversine."""

    radio_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return radio_km * c


def calcular_distancias_km(latitudes: Sequence[float], longitudes: Sequence[float]) -> np.ndarray:
    """Calcula distancias consecutivas en km a lo largo de una ruta."""

    if len(latitudes) < 2:
        return np.array([])
    distancias = []
    for i in range(1, len(latitudes)):
        distancias.append(
            haversine_km(
                float(latitudes[i - 1]),
                float(longitudes[i - 1]),
                float(latitudes[i]),
                float(longitudes[i]),
            )
        )
    return np.array(distancias, dtype=float)


def calcular_estadisticas(
    tiempos: Sequence[pd.Timestamp], latitudes: Sequence[float], longitudes: Sequence[float]
) -> EstadisticasRuta:
    """Calcula distancia total, duracion y velocidades estimadas."""

    distancias = calcular_distancias_km(latitudes, longitudes)
    distancia_total = float(distancias.sum()) if distancias.size else 0.0

    if len(tiempos) < 2:
        return EstadisticasRuta(distancia_total, 0.0, 0.0, 0.0)

    inicio = _valor_tiempo(tiempos, 0)
    fin = _valor_tiempo(tiempos, -1)
    duracion = (fin - inicio).total_seconds()
    if duracion <= 0:
        return EstadisticasRuta(distancia_total, duracion, 0.0, 0.0)

    tiempos_seg = convertir_tiempo_a_segundos(tiempos)
    deltas_t = np.diff(tiempos_seg)
    with np.errstate(divide="ignore", invalid="ignore"):
        velocidades = np.where(deltas_t > 0, (distancias / deltas_t) * 3600.0, 0.0)

    velocidad_media = (distancia_total / (duracion / 3600.0)) if duracion > 0 else 0.0
    velocidad_maxima = float(np.max(velocidades)) if velocidades.size else 0.0

    return EstadisticasRuta(distancia_total, duracion, velocidad_media, velocidad_maxima)
