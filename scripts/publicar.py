"""Publica en Instagram la publicación del día de la carpeta publicaciones/AAAA-MM-DD.

- Una foto  -> post simple.  Varias fotos -> carrusel (orden alfabético).
- El texto sale de texto.txt dentro de la misma carpeta.
- Registra lo publicado en publicados.txt para no repetir.
Solo usa la librería estándar de Python.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

API = "https://graph.instagram.com/v21.0"
CARPETA = "publicaciones"
REGISTRO = "publicados.txt"
EXTENSIONES = (".jpg", ".jpeg")  # la API de Instagram solo acepta JPEG


def llamar(metodo, ruta, token, **params):
    params["access_token"] = token
    datos = urllib.parse.urlencode(params).encode()
    url = f"{API}/{ruta}"
    if metodo == "GET":
        req = urllib.request.Request(f"{url}?{datos.decode()}")
    else:
        req = urllib.request.Request(url, data=datos, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detalle = e.read().decode(errors="replace")
        sys.exit(f"Error de Instagram ({e.code}) en {ruta}: {detalle}")


def esperar_listo(contenedor, token):
    for _ in range(30):
        estado = llamar("GET", contenedor, token, fields="status_code")
        codigo = estado.get("status_code")
        if codigo == "FINISHED":
            return
        if codigo in ("ERROR", "EXPIRED"):
            sys.exit(f"Instagram no pudo procesar el contenido: {estado}")
        time.sleep(5)
    sys.exit("Instagram tardó demasiado en procesar el contenido.")


def main():
    fecha = (os.environ.get("FECHA") or "").strip() or datetime.now(
        ZoneInfo("America/Argentina/Buenos_Aires")
    ).strftime("%Y-%m-%d")
    carpeta = os.path.join(CARPETA, fecha)
    print(f"Fecha: {fecha}")

    if not os.path.isdir(carpeta):
        print("No hay publicación programada para hoy. Nada que hacer.")
        return

    publicados = open(REGISTRO).read().split() if os.path.exists(REGISTRO) else []
    if fecha in publicados:
        print("Esta publicación ya se hizo. Nada que hacer.")
        return

    fotos = sorted(f for f in os.listdir(carpeta) if f.lower().endswith(EXTENSIONES))
    if not fotos:
        sys.exit(f"La carpeta {carpeta} no tiene fotos .jpg")
    if len(fotos) > 10:
        sys.exit("Instagram permite hasta 10 fotos por carrusel.")

    texto_path = os.path.join(carpeta, "texto.txt")
    texto = open(texto_path, encoding="utf-8").read().strip() if os.path.exists(texto_path) else ""

    token = os.environ.get("IG_TOKEN", "").strip()
    if not token:
        sys.exit("Falta el secreto IG_TOKEN en Settings > Secrets and variables > Actions.")

    repo = os.environ["GITHUB_REPOSITORY"]
    sha = os.environ["GITHUB_SHA"]
    url = lambda f: f"https://raw.githubusercontent.com/{repo}/{sha}/{CARPETA}/{urllib.parse.quote(fecha)}/{urllib.parse.quote(f)}"

    yo = llamar("GET", "me", token, fields="user_id,username")
    cuenta = yo.get("user_id") or yo["id"]
    print(f"Cuenta: @{yo.get('username')}")

    if len(fotos) == 1:
        contenedor = llamar("POST", f"{cuenta}/media", token, image_url=url(fotos[0]), caption=texto)["id"]
    else:
        hijos = []
        for f in fotos:
            hijo = llamar("POST", f"{cuenta}/media", token, image_url=url(f), is_carousel_item="true")["id"]
            esperar_listo(hijo, token)
            hijos.append(hijo)
        contenedor = llamar(
            "POST", f"{cuenta}/media", token,
            media_type="CAROUSEL", children=",".join(hijos), caption=texto,
        )["id"]

    esperar_listo(contenedor, token)
    publicado = llamar("POST", f"{cuenta}/media_publish", token, creation_id=contenedor)
    print(f"Publicado. ID: {publicado.get('id')}")

    with open(REGISTRO, "a") as r:
        r.write(f"{fecha}\n")


if __name__ == "__main__":
    main()
