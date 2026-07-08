#!/usr/bin/env bash
# Prepara una carpeta lista para subir a GitHub como repositorio del agente.
# Uso: ./prepare-repo.sh /ruta/destino/reviewboost-agent

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${1:-}"

if [ -z "$DEST_DIR" ]; then
  echo "Uso: $0 /ruta/destino/reviewboost-agent"
  echo ""
  echo "Crea una copia limpia de los archivos del agente para subir a GitHub."
  exit 1
fi

mkdir -p "$DEST_DIR"

# Copiar archivos y carpetas necesarios a la raíz del nuevo repositorio
cp -R "$SCRIPT_DIR/.github" "$DEST_DIR/"
cp -R "$SCRIPT_DIR/reviewboost_agent" "$DEST_DIR/"
cp -R "$SCRIPT_DIR/installer" "$DEST_DIR/"
cp "$SCRIPT_DIR/build.ps1" "$DEST_DIR/"
cp "$SCRIPT_DIR/pyinstaller.spec" "$DEST_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$DEST_DIR/"
cp "$SCRIPT_DIR/README.md" "$DEST_DIR/"
cp "$SCRIPT_DIR/.gitignore" "$DEST_DIR/"

echo "Agente copiado a: $DEST_DIR"
echo ""
echo "Pasos siguientes:"
echo "  cd $DEST_DIR"
echo "  git init"
echo "  git add ."
echo "  git commit -m 'Initial agent release'"
echo "  git branch -M main"
echo "  git remote add origin https://github.com/TU_USUARIO/reviewboost-agent.git"
echo "  git push -u origin main"
echo "  git tag v1.0.0"
echo "  git push origin v1.0.0"
echo ""
echo "Después de 5-10 minutos, la URL de descarga será:"
echo "  https://github.com/TU_USUARIO/reviewboost-agent/releases/latest/download/ReviewBoostAgentSetup.exe"
