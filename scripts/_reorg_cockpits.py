#!/usr/bin/env python3
"""Remove st.columns() layouts e reorganiza gráficos em largura total."""
import re

filepath = r"C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri\app.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove padrão: múltiplas variáveis = st.columns(N)
# Exemplo: c1, c2, c3, c4 = st.columns(4)
content = re.sub(
    r'\s*[a-z_0-9\s,]+ = st\.columns\([0-9]+\)\s*\n',
    '\n',
    content
)

# Remove: kpi(c1, ...) → kpi(...)
# Mantém apenas os argumentos internos
content = re.sub(
    r'kpi\(c\d+, ',
    'kpi(',
    content
)

# Remove: c#.metric(...) → st.metric(...)
content = re.sub(
    r'c(\d+)\.metric\(',
    'st.metric(',
    content
)

# Remove: col#.plotly_chart(...) → st.plotly_chart(...)
content = re.sub(
    r'(col\d+|c\d+|r\d+)\.plotly_chart\(',
    'st.plotly_chart(',
    content
)

# Remove: col#.dataframe(...) → st.dataframe(...)
content = re.sub(
    r'(col\d+|c\d+)\.dataframe\(',
    'st.dataframe(',
    content
)

# Remove: col#.write(...) → st.write(...)
content = re.sub(
    r'(col\d+|c\d+)\.write\(',
    'st.write(',
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Reorganizacao concluida!")
print("   - Removidos todos st.columns()")
print("   - Graficos convertidos para largura total")
