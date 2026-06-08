#!/bin/bash
# install_hooks.sh: Instala git hooks del protocolo
# Corre UNA sola vez después de clonar o en setup inicial

PROTOCOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_SRC="$PROTOCOL_DIR/scripts/hooks"
GIT_HOOKS_DIR="$PROTOCOL_DIR/.git/hooks"

echo "📦 Instalando git hooks del protocolo..."

# Crear directorio si no existe
mkdir -p "$GIT_HOOKS_DIR"

# Copiar hooks versionados (pre-commit + commit-msg VC-140)
for hook in pre-commit commit-msg; do
    if [ -f "$HOOKS_SRC/$hook" ]; then
        cp "$HOOKS_SRC/$hook" "$GIT_HOOKS_DIR/$hook"
        chmod +x "$GIT_HOOKS_DIR/$hook"
        echo "✅ $hook hook instalado"
    else
        echo "❌ scripts/hooks/$hook no encontrado"
        exit 1
    fi
done

echo ""
echo "✅ Git hooks instalados. Próximos commits serán validados automáticamente."
echo "   Si validation falla: git commit será BLOQUEADO"
