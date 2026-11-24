#!/usr/bin/env bash
# Corre todas las pruebas unitarias de los scripts. Sin red, sin navegador y sin Instagram.
set -e
cd "$(dirname "$0")"
node --test ig/test/*.test.mjs web/test/*.test.mjs
for carpeta in virales anuncios guiones negocios web adn; do
  (cd "$carpeta" && python3 -m unittest discover -p 'test_*.py')
done
