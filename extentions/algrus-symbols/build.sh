#!/usr/bin/env bash
# Сборка предустановленного (prebuilt) расширения JupyterLab.
#
# Требуется JupyterLab 4 и Node.js. Сборщик @jupyterlab/builder уже
# прописан в devDependencies, поэтому достаточно `npm install`.
set -euo pipefail

cd "$(dirname "$0")"

BUILD="../../algrus_core/labextension"

npm install --no-audit --no-fund

# JupyterLab 4: webpack-сборка с remoteEntry и метаданными _build.
# Просто esbuild --format=cjs для JupyterLab 4 не подходит.
jupyter labextension build .

# Кладём результат в Python-пакет, который устанавливает файлы в
# share/jupyter/labextensions/algrus-symbols.
rm -rf "$BUILD/static"
cp labextension/package.json "$BUILD/package.json"
cp -r labextension/static "$BUILD/static"

echo "Готово: $BUILD"
