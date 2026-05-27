"""Generacion de mapas interactivos con folium."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import folium


def crear_mapa_interactivo(
    latitud_original: Sequence[float],
    longitud_original: Sequence[float],
    latitud_interpolada: Sequence[float],
    longitud_interpolada: Sequence[float],
    ruta_salida: str | Path,
) -> None:
    """Crea un mapa con puntos originales y ruta interpolada."""

    centro_lat = float(latitud_original[0])
    centro_lon = float(longitud_original[0])
    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=14, tiles="OpenStreetMap")

    for lat, lon in zip(latitud_original, longitud_original, strict=False):
        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=4,
            color="#1f77b4",
            fill=True,
            fill_opacity=0.9,
            popup=f"Original: {lat:.5f}, {lon:.5f}",
        ).add_to(mapa)

    folium.PolyLine(
        locations=list(zip(latitud_interpolada, longitud_interpolada, strict=False)),
        color="#ff7f0e",
        weight=4,
        opacity=0.8,
        tooltip="Ruta interpolada",
    ).add_to(mapa)

    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    mapa.save(str(ruta))
