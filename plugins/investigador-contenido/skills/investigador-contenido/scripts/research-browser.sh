#!/usr/bin/env bash
# Navegador de investigación aislado: perfil propio y puerto propio, separado del navegador personal.
# La persona sigue trabajando (por ejemplo, editando video) sin que la investigación abra ventanas ni robe foco.
#
#   research-browser.sh login    ventana visible UNA sola vez, para iniciar sesión en Instagram (pide permiso antes)
#   research-browser.sh start    headless: sin ventana, sin ícono, sin pestañas visibles
#   research-browser.sh stop     apaga solo este navegador (por su perfil), nunca el personal
#   research-browser.sh status   dice si responde el puerto
#
# Configuración (variables de entorno; guárdalas en tu *.local.md):
#   CDP_PUERTO            puerto de depuración de ESTE navegador (obligatorio; distinto al de tu navegador personal)
#   NAVEGADOR             ruta del ejecutable de Chrome, Chromium o Brave (obligatorio)
#   PERFIL_INVESTIGACION  carpeta del perfil aislado (por omisión ~/.perfil-investigacion)
#   UA_INVESTIGACION      user agent para headless (Chromium headless se anuncia como "HeadlessChrome" y Instagram lo bloquea)
set -u

PERFIL="${PERFIL_INVESTIGACION:-$HOME/.perfil-investigacion}"
UA="${UA_INVESTIGACION:-Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36}"

falta() { echo "Falta $1. $2" >&2; exit 2; }

requiere_puerto() {
  [[ "${CDP_PUERTO:-}" =~ ^[0-9]{2,5}$ ]] || falta "CDP_PUERTO" "Pon el puerto de depuración del navegador de investigación."
  if [[ -n "${CDP_PUERTO_PERSONAL:-}" && "$CDP_PUERTO_PERSONAL" == "$CDP_PUERTO" ]]; then
    falta "un puerto distinto" "CDP_PUERTO es el de tu navegador personal."
  fi
}

requiere_navegador() {
  [[ -n "${NAVEGADOR:-}" && -x "$NAVEGADOR" ]] || falta "NAVEGADOR" "Pon la ruta del ejecutable de Chrome, Chromium o Brave."
}

case "${1:-}" in
  login)
    requiere_puerto; requiere_navegador
    "$NAVEGADOR" --user-data-dir="$PERFIL" --remote-debugging-port="$CDP_PUERTO" \
      --no-first-run --no-default-browser-check \
      "https://www.instagram.com/accounts/login/" >/dev/null 2>&1 &
    echo "Ventana de inicio de sesión abierta. La persona escribe su contraseña ella misma; luego: stop y start."
    ;;
  start)
    requiere_puerto; requiere_navegador
    "$NAVEGADOR" --headless=new --user-data-dir="$PERFIL" --remote-debugging-port="$CDP_PUERTO" \
      --no-first-run --no-default-browser-check --window-size=1280,2400 \
      --user-agent="$UA" "about:blank" >/dev/null 2>&1 &
    ;;
  stop)
    pkill -f -- "--user-data-dir=$PERFIL" || true
    ;;
  status)
    requiere_puerto
    if version=$(curl -sf --max-time 3 "http://127.0.0.1:$CDP_PUERTO/json/version"); then
      echo "$version" | head -2
    else
      echo "apagado"
    fi
    ;;
  *)
    echo "uso: $0 login|start|stop|status" >&2
    exit 1
    ;;
esac
