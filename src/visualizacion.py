"""Graficas comparativas de rutas GPS."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt


def graficar_rutas(
    latitud_original: Sequence[float],
    longitud_original: Sequence[float],
    latitud_interpolada: Sequence[float],
    longitud_interpolada: Sequence[float],
    ruta_salida: str | Path,
    titulo: str = "Comparacion de rutas",
) -> None:
    """Genera una grafica de la ruta original e interpolada."""

    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(
        longitud_original,
        latitud_original,
        "o-",
        color="#1f77b4",
        label="Ruta original",
        linewidth=1.2,
        markersize=4,
    )
    ax.plot(
        longitud_interpolada,
        latitud_interpolada,
        "-",
        color="#ff7f0e",
        label="Ruta interpolada",
        linewidth=2.0,
        alpha=0.9,
    )
    ax.set_title(titulo)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    salida = Path(ruta_salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=150)
    plt.close(fig)
