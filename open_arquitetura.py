"""
Abre o documento HTML de arquitetura no navegador para conversão em PDF
"""
import webbrowser
from pathlib import Path
import os

# Caminho do arquivo HTML
html_file = Path("docs/arquitetura_completa.html").absolute()

print(f"📄 Abrindo documento de arquitetura no navegador...")
print(f"📁 Arquivo: {html_file}")
print()
print("=" * 70)
print("INSTRUÇÕES PARA GERAR O PDF:")
print("=" * 70)
print()
print("1. O navegador irá abrir o documento HTML automaticamente")
print("2. Pressione Ctrl+P (ou Cmd+P no Mac) para abrir o diálogo de impressão")
print("3. Selecione 'Salvar como PDF' ou 'Microsoft Print to PDF' como destino")
print("4. Configure as opções:")
print("   - Orientação: Retrato")
print("   - Margens: Padrão")
print("   - Escala: 100%")
print("5. Clique em 'Salvar' e escolha o local:")
print(f"   Sugestão: {html_file.parent / 'Arquitetura_SRAG_POC_Completa.pdf'}")
print()
print("=" * 70)
print()

# Abrir no navegador padrão
webbrowser.open(f"file:///{html_file}")

print("✅ Navegador aberto! Siga as instruções acima para gerar o PDF.")
