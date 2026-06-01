

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .utilidades import convertir_tiempo_a_segundos


MetodoInterpolacion = Literal["newton", "lagrange"]


@dataclass(frozen=True)
class ResultadoInterpolacion:
    """Resultado de la interpolacion."""

    tiempos_segundos: np.ndarray
    latitudes: np.ndarray
    longitudes: np.ndarray


def _interpolar_newton(x: np.ndarray, y: np.ndarray, x_nuevo: np.ndarray) -> np.ndarray:
    n = len(x)
    coef = y.astype(float).copy()
    for j in range(1, n):
        coef[j:n] = (coef[j:n] - coef[j - 1 : n - 1]) / (x[j:n] - x[0 : n - j])

    y_nuevo = np.zeros_like(x_nuevo, dtype=float)
    termino = np.ones_like(x_nuevo, dtype=float)
    for i in range(n):
        if i > 0:
            termino *= x_nuevo - x[i - 1]
        y_nuevo += coef[i] * termino
    return y_nuevo


def _interpolar_lagrange(x: np.ndarray, y: np.ndarray, x_nuevo: np.ndarray) -> np.ndarray:
    n = len(x)
    y_nuevo = np.zeros_like(x_nuevo, dtype=float)
    for i in range(n):
        term = np.ones_like(x_nuevo, dtype=float)
        for j in range(n):
            if i != j:
                term *= (x_nuevo - x[j]) / (x[i] - x[j])
        y_nuevo += y[i] * term
    return y_nuevo


def interpolar_ruta(
    tiempos, latitudes, longitudes, metodo: MetodoInterpolacion, num_puntos: int
) -> ResultadoInterpolacion:
    """Interpola latitudes y longitudes segun el metodo elegido."""

    if num_puntos < 100:
        raise ValueError("Se requieren al menos 100 puntos interpolados.")
    if len(tiempos) < 2:
        raise ValueError("Se requieren al menos dos puntos para interpolar.")

    tiempos_seg = convertir_tiempo_a_segundos(tiempos)
    x = np.array(tiempos_seg, dtype=float)
    x_nuevo = np.linspace(x.min(), x.max(), num_puntos)
    lat = np.array(latitudes, dtype=float)
    lon = np.array(longitudes, dtype=float)

    if metodo == "newton":
        lat_i = _interpolar_newton(x, lat, x_nuevo)
        lon_i = _interpolar_newton(x, lon, x_nuevo)
    elif metodo == "lagrange":
        lat_i = _interpolar_lagrange(x, lat, x_nuevo)
        lon_i = _interpolar_lagrange(x, lon, x_nuevo)
    else:
        raise ValueError("Metodo de interpolacion no valido.")

    return ResultadoInterpolacion(x_nuevo, lat_i, lon_i)
