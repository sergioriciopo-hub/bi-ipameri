#!/usr/bin/env python3
"""Remove blocos 'with col#:' removendo indentação."""
import re

filepath = r"C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri\app.py"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output = []
skip_next_dedent = False
i = 0

while i < len(lines):
    line = lines[i]

    # Detecta "with col#:" ou "with col#:" com espaços
    if re.match(r'\s+with (col|c|r)\d+:', line):
        skip_next_dedent = True
        i += 1
        continue

    # Se estamos num bloco with, reduz indentação em 4 espaços
    if skip_next_dedent and line.strip() and not re.match(r'\s+with (col|c|r)\d+:', line):
        # Verifica se voltou ao nível anterior (dedent)
        if line.startswith('    ') and not line.startswith('        '):
            # Fim do bloco with anterior
            skip_next_dedent = False
            output.append(line)
        elif line.startswith('        '):
            # Está dentro do bloco with, remove 4 espaços
            output.append(line[4:])
        else:
            skip_next_dedent = False
            output.append(line)
    else:
        output.append(line)

    i += 1

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(output)

print("[OK] Blocos 'with col' removidos com sucesso!")
