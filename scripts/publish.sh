#!/bin/bash

# Script de Publicação Automatizada - BI Ipameri
# Automatiza: git add → git commit → git push

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  📤 Publicando alterações (Local + Online)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Mudar para o diretório do projeto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$PROJECT_DIR"

# 1. Verificar status
echo "1️⃣  Verificando alterações..."
git status

echo ""
echo "2️⃣  Adicionando arquivos modificados..."
git add app.py scripts/*.py scripts/*.ps1 scripts/*.bat 2>/dev/null || true

# 3. Pedir mensagem de commit
echo ""
echo "3️⃣  Prepare sua mensagem de commit:"
echo "    (Digite a mensagem de commit e pressione Enter duas vezes quando terminar)"
echo ""

# Ler mensagem multilinhas
commit_msg=""
while IFS= read -r line; do
    if [ -z "$line" ]; then
        # Linha vazia - se temos mensagem, termina
        if [ -n "$commit_msg" ]; then
            break
        fi
    else
        # Adiciona linha à mensagem
        if [ -z "$commit_msg" ]; then
            commit_msg="$line"
        else
            commit_msg="$commit_msg"$'\n'"$line"
        fi
    fi
done

if [ -z "$commit_msg" ]; then
    echo "❌ Nenhuma mensagem de commit fornecida. Abortando..."
    exit 1
fi

# 4. Fazer commit
echo ""
echo "4️⃣  Realizando commit..."
git_commit_msg="$commit_msg

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

git commit -m "$git_commit_msg" || {
    echo "⚠️  Nenhuma alteração para fazer commit"
    exit 0
}

# 5. Fazer push
echo ""
echo "5️⃣  Enviando para o GitHub (online)..."
git push origin main

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Publicação concluída com sucesso!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 Dashboard atualizada em: https://bi-ipameri.streamlit.app/"
