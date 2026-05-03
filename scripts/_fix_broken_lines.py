#!/usr/bin/env python3
"""Fix truncated lines ending with operators."""
import re

filepath = r"C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri\app.py"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Padrões comuns de linhas truncadas
# if condition in var. → if condition in var.columns else 0
replacements = [
    (r'(\s+)if ".*?" in (\w+)\.\s*\n', r'\1if "\1" in \2.columns else 0\n'),
    (r'(\s+)= (\w+)\[".*?"\]\.sum\(\) if not (\w+)\.empty and.*? in (\w+)\.\s*\n',
     r'\1= \2["\1"].sum() if not \3.empty and "\1" in \4.columns else 0\n'),
]

for i, line in enumerate(lines):
    # Detecta linhas que terminam com . ou operador
    if re.search(r'[.\+\-\*/] *\n$', line) or re.search(r' in \w+\. *\n$', line):
        # Procura a próxima linha para ver se continua
        if i + 1 < len(lines) and not re.match(r'\s*(def |class |if |else|elif |for |while |#)', lines[i+1]):
            # Tenta completar com a próxima linha
            combined = line.rstrip() + ' ' + lines[i+1].lstrip()
            if re.search(r'columns', combined) or re.search(r'\.sum\(', combined):
                lines[i] = combined
                lines[i+1] = ''  # Remove a próxima linha pois foi incorporada

# Remove linhas vazias de linhas que foram combinadas
lines = [l for l in lines if l.strip() or l == '\n']

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("[OK] Linhas truncadas corrigidas!")
