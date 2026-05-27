"""Aplicacion Flask para interpolacion de trayectorias GPS."""

from __future__ import annotations

import secrets
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from src.interpolacion import interpolar_ruta
from src.lector_csv import leer_datos_gps
from src.mapa import crear_mapa_interactivo
from src.utilidades import calcular_estadisticas, crear_tiempo_interpolado, asegurar_directorio
from src.visualizacion import graficar_rutas


ALLOWED_EXTENSIONS = {"csv"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024


def crear_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    app.config["UPLOAD_FOLDER"] = "uploads"
    app.config["OUTPUT_FOLDER"] = "outputs"
    app.config["STATIC_MAPAS"] = "static/mapas"
    app.config["STATIC_GRAFICAS"] = "static/graficas"
    app.config["STATIC_CSV"] = "static/csv"
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    asegurar_directorio(app.config["UPLOAD_FOLDER"])
    asegurar_directorio(app.config["OUTPUT_FOLDER"])
    asegurar_directorio(app.config["STATIC_MAPAS"])
    asegurar_directorio(app.config["STATIC_GRAFICAS"])
    asegurar_directorio(app.config["STATIC_CSV"])

    def extension_permitida(nombre: str) -> bool:
        return "." in nombre and nombre.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route("/", methods=["GET"])
    def index() -> str:
        return render_template("index.html")

    @app.route("/procesar", methods=["POST"])
    def procesar() -> str:
        if "archivo" not in request.files:
            flash("No se envio el archivo.", "danger")
            return redirect(url_for("index"))

        archivo = request.files["archivo"]
        metodo = request.form.get("metodo", "lineal")
        puntos_str = request.form.get("num_puntos", "200")
        if archivo.filename == "":
            flash("No se selecciono un archivo.", "warning")
            return redirect(url_for("index"))

        if not extension_permitida(archivo.filename):
            flash("Formato no permitido. Suba un CSV valido.", "danger")
            return redirect(url_for("index"))

        try:
            num_puntos = int(puntos_str)
        except ValueError:
            flash("La cantidad de puntos debe ser numerica.", "danger")
            return redirect(url_for("index"))
        if num_puntos < 100 or num_puntos > 5000:
            flash("La cantidad de puntos debe estar entre 100 y 5000.", "danger")
            return redirect(url_for("index"))

        nombre_seguro = secure_filename(archivo.filename)
        marca = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_final = f"{marca}_{nombre_seguro}"
        ruta_subida = Path(app.config["UPLOAD_FOLDER"]) / nombre_final
        archivo.save(ruta_subida)

        try:
            datos = leer_datos_gps(ruta_subida)
            inicio_lineal = datetime.now()
            resultado_lineal = interpolar_ruta(
                datos.tiempo,
                datos.latitud,
                datos.longitud,
                metodo="lineal",
                num_puntos=num_puntos,
            )
            tiempo_lineal_ms = (datetime.now() - inicio_lineal).total_seconds() * 1000

            inicio_lagrange = datetime.now()
            resultado_lagrange = interpolar_ruta(
                datos.tiempo,
                datos.latitud,
                datos.longitud,
                metodo="lagrange",
                num_puntos=num_puntos,
            )
            tiempo_lagrange_ms = (datetime.now() - inicio_lagrange).total_seconds() * 1000

            resultado = resultado_lineal if metodo == "lineal" else resultado_lagrange
        except Exception as exc:
            flash(f"Error al procesar el archivo: {exc}", "danger")
            return redirect(url_for("index"))

        tiempos_interpolados = crear_tiempo_interpolado(datos.tiempo.iloc[0], resultado.tiempos_segundos)
        estadisticas = calcular_estadisticas(datos.tiempo, datos.latitud, datos.longitud)
        estadisticas_lineal = calcular_estadisticas(
            tiempos_interpolados, resultado_lineal.latitudes, resultado_lineal.longitudes
        )
        estadisticas_lagrange = calcular_estadisticas(
            tiempos_interpolados, resultado_lagrange.latitudes, resultado_lagrange.longitudes
        )

        mapa_nombre = f"mapa_{marca}.html"
        grafica_nombre = f"grafica_{marca}.png"
        grafica_comp_nombre = f"comparacion_{marca}.png"
        csv_nombre = f"interpolado_{marca}.csv"

        mapa_path = Path(app.config["STATIC_MAPAS"]) / mapa_nombre
        grafica_path = Path(app.config["STATIC_GRAFICAS"]) / grafica_nombre
        grafica_comp_path = Path(app.config["STATIC_GRAFICAS"]) / grafica_comp_nombre
        csv_path = Path(app.config["STATIC_CSV"]) / csv_nombre

        crear_mapa_interactivo(
            datos.latitud,
            datos.longitud,
            resultado.latitudes,
            resultado.longitudes,
            mapa_path,
        )
        graficar_rutas(
            datos.latitud,
            datos.longitud,
            resultado.latitudes,
            resultado.longitudes,
            grafica_path,
            titulo=f"Ruta GPS (metodo: {metodo})",
        )

        graficar_rutas(
            resultado_lineal.latitudes,
            resultado_lineal.longitudes,
            resultado_lagrange.latitudes,
            resultado_lagrange.longitudes,
            grafica_comp_path,
            titulo="Comparacion: Lineal vs Lagrange",
        )

        df_salida = {
            "tiempo": tiempos_interpolados,
            "latitud": resultado.latitudes,
            "longitud": resultado.longitudes,
        }
        import pandas as pd

        pd.DataFrame(df_salida).to_csv(csv_path, index=False)

        return render_template(
            "resultado.html",
            metodo=metodo,
            puntos_originales=len(datos.latitud),
            puntos_interpolados=len(resultado.latitudes),
            distancia_km=f"{estadisticas.distancia_total_km:.3f}",
            velocidad_media=f"{estadisticas.velocidad_media_kmh:.2f}",
            velocidad_maxima=f"{estadisticas.velocidad_maxima_kmh:.2f}",
            puntos_selector=num_puntos,
            comp_grafica_url=url_for("static", filename=f"graficas/{grafica_comp_nombre}"),
            comp_lineal_dist=f"{estadisticas_lineal.distancia_total_km:.3f}",
            comp_lagrange_dist=f"{estadisticas_lagrange.distancia_total_km:.3f}",
            comp_lineal_vel=f"{estadisticas_lineal.velocidad_media_kmh:.2f}",
            comp_lagrange_vel=f"{estadisticas_lagrange.velocidad_media_kmh:.2f}",
            comp_lineal_time=f"{tiempo_lineal_ms:.2f}",
            comp_lagrange_time=f"{tiempo_lagrange_ms:.2f}",
            grafica_url=url_for("static", filename=f"graficas/{grafica_nombre}"),
            mapa_url=url_for("static", filename=f"mapas/{mapa_nombre}"),
            csv_url=url_for("descargar_csv", nombre=csv_nombre),
        )

    @app.route("/descargar/<nombre>", methods=["GET"])
    def descargar_csv(nombre: str):
        return send_from_directory(app.config["STATIC_CSV"], nombre, as_attachment=True)

    @app.errorhandler(413)
    def archivo_demasiado_grande(_error):
        flash("El archivo supera el maximo permitido (2 MB).", "danger")
        return redirect(url_for("index"))

    return app


if __name__ == "__main__":
    app = crear_app()
    app.run(debug=True, host="127.0.0.1", port=5001)
