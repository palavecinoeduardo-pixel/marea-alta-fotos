# Marea Alta · Chapadmalal — publicaciones de Instagram

Este repo publica solo en **@mareaaltachapadmalal**, todos los días a las **19:00 (hora argentina)**.

## Cómo funciona

Cada publicación es una carpeta con la fecha dentro de `publicaciones/`:

```
publicaciones/
  2026-11-06/
    1.jpg
    2.jpg        ← si hay más de una foto, se publica como carrusel
    texto.txt    ← el texto del post (emojis y hashtags incluidos)
```

- Si un día no tiene carpeta, ese día no se publica nada.
- Las fotos tienen que ser **.jpg** (hasta 10 por post). Se publican en orden alfabético.
- Lo ya publicado queda anotado en `publicados.txt` y no se repite.

## Configuración (una sola vez)

1. Sacar el token de Instagram en developers.facebook.com.
2. En este repo: **Settings → Secrets and variables → Actions → New repository secret**.
   Nombre: `IG_TOKEN`. Valor: el token.

El token dura **60 días**. Cuando vence, se saca uno nuevo y se reemplaza el valor de `IG_TOKEN`.

## Probar o publicar a mano

**Actions → Publicar en Instagram → Run workflow**. Se puede dejar la fecha vacía (hoy) o poner una fecha.
