#!/bin/bash
# install_hooks.sh: Instala git hooks del protocolo
# Corre UNA sola vez después de clonar o en setup inicial

PROTOCOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_SRC="$PROTOCOL_DIR/scripts/hooks"
GIT_HOOKS_DIR="$PROTOCOL_DIR/.git/hooks"

echo "📦 Instalando git hooks del protocolo..."

# Crear directorio si no existe
mkdir -p "$GIT_HOOKS_DIR"

# Copiar pre-commit hook
if [ -f "$HOOKS_SRC/pre-commit" ]; then
    cp "$HOOKS_SRC/pre-commit" "$GIT_HOOKS_DIR/pre-commit"
    chmod +x "$GIT_HOOKS_DIR/pre-commit"
    echo "✅ pre-commit hook instalado"
else
    echo "❌ scripts/hooks/pre-commit no encontrado"
    exit 1
fi

echo ""
echo "✅ Git hooks instalados. Próximos commits serán validados automáticamente."
echo "   Si validation falla: git commit será BLOQUEADO"
