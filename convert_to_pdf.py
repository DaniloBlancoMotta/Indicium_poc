"""
Script para converter o documento HTML de arquitetura em PDF
"""
from weasyprint import HTML
from pathlib import Path

# Caminhos
html_file = Path("docs/arquitetura_completa.html")
pdf_file = Path("docs/Arquitetura_SRAG_POC_Completa.pdf")

# Garantir que o diretório existe
pdf_file.parent.mkdir(parents=True, exist_ok=True)

# Converter HTML para PDF
print(f"Convertendo {html_file} para PDF...")
HTML(filename=str(html_file)).write_pdf(str(pdf_file))
print(f"✅ PDF gerado com sucesso: {pdf_file}")
print(f"📄 Tamanho: {pdf_file.stat().st_size / 1024:.2f} KB")
