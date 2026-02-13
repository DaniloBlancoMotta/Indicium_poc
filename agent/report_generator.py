"""
Módulo de geração de relatórios SRAG
R400-R410: Estrutura obrigatória e cores do sistema
"""

from datetime import datetime
from pathlib import Path
import logging
from . import config
from xhtml2pdf import pisa

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Gera relatórios em HTML e PDF seguindo as diretrizes da Fase 4.
    """
    
    def __init__(self, output_dir: Path = config.OUTPUTS):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Cores do config.METRIC_COLORS
        self.colors = config.METRIC_COLORS

    def _to_pdf(self, html_content: str, output_path: Path):
        """Converte HTML string para arquivo PDF usando xhtml2pdf."""
        try:
            with open(output_path, "wb") as result_file:
                # pisa.CreatePDF expects text, not bytes for the source, but binary for dest
                pisa_status = pisa.CreatePDF(html_content, dest=result_file)
            
            if pisa_status.err:
                logger.error(f"Erro ao gerar PDF: {pisa_status.err}")
                return False
            return True
        except Exception as e:
            logger.error(f"Exceção na conversão PDF (Detalhe): {e}", exc_info=True)
            return False

    def _get_base_styles(self):
        return f"""
            body {{ font-family: Helvetica, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #fff; }}
            header {{ text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 20px; margin-bottom: 30px; }}
            h1 {{ color: #2c3e50; margin-bottom: 5px; font-size: 24px; }}
            h2 {{ color: #2c3e50; border-left: 5px solid #2c3e50; padding-left: 15px; margin-top: 20px; font-size: 18px; }}
            .meta {{ color: #7f8c8d; font-size: 12px; }}
            
            /* Metrics Grid adjusted for PDF (Tables are safer) */
            .metrics-table {{ width: 100%; border-collapse: separate; border-spacing: 10px; margin-bottom: 30px; }}
            .metric-cell {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #ddd; text-align: center; width: 25%; }}
            .metric-label {{ font-size: 10px; color: #7f8c8d; text-transform: uppercase; }}
            .metric-value {{ font-size: 18px; font-weight: bold; margin: 5px 0; color: #2c3e50; }}
            
            .section {{ margin-bottom: 30px; }}
            .news-item {{ margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
            .news-title {{ font-weight: bold; color: {self.colors['crescimento']}; font-size: 14px; }}
            .news-meta {{ font-size: 10px; color: #95a5a6; }}
            .news-summary {{ font-size: 12px; text-align: justify; }}
            
            .insight {{ font-style: italic; color: #34495e; background: #eef2f3; padding: 15px; border-radius: 5px; font-size: 12px; }}
            .chart-box {{ text-align: center; margin-bottom: 20px; }}
            .chart-img {{ width: 90%; height: auto; border: 1px solid #ddd; }}
            
            footer {{ text-align: center; color: #95a5a6; font-size: 10px; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }}
        """

    def generate_reports(self, data: dict):
        """
        Gera dois relatórios distintos (HTML e PDF):
        1. Dataset (Métricas e Gráficos)
        2. Notícias (Contexto)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        generated_files = []

        # Extrair dados
        metrics = data.get('metrics', {})
        charts = data.get('charts', {})
        news = data.get('news', [])
        
        # Insights agora vêm separados
        insights_data = data.get('insights_data', data.get('insights', ''))
        insights_news = data.get('insights_news', '')

        # Preparar caminhos absolutos para imagens (Necessário para xhtml2pdf)
        # Usar as_uri() para garantir protocolo correto no Windows (file:///)
        
        daily_chart_path = charts.get('daily_chart', '')
        daily_img = str(Path(daily_chart_path).resolve()) if daily_chart_path else ""
        
        monthly_chart_path = charts.get('monthly_chart', '')
        monthly_img = str(Path(monthly_chart_path).resolve()) if monthly_chart_path else ""

        # --- 1. RELATÓRIO DE DATASET ---
        html_dataset = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Relatório de Dados SRAG</title>
            <style>{self._get_base_styles()}</style>
        </head>
        <body>
            <header>
                <h1>Análise de Dados Epidemiológicos: SRAG</h1>
                <div class="meta">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Fonte: DATASUS</div>
            </header>

            <section class="section">
                <h2>Indicadores Chave de Performance (KPIs)</h2>
                <table class="metrics-table">
                    <tr>
                        <td class="metric-cell" style="border-top: 3px solid {self.colors['crescimento']}">
                            <div class="metric-label">Crescimento (30d)</div>
                            <div class="metric-value">{metrics.get('growth', {}).get('growth_rate', 0):+.2f}%</div>
                            <div class="meta">{metrics.get('growth', {}).get('current_period_cases', 0)} casos</div>
                        </td>
                        <td class="metric-cell" style="border-top: 3px solid {self.colors['mortalidade']}">
                            <div class="metric-label">Mortalidade</div>
                            <div class="metric-value">{metrics.get('mortality', {}).get('mortality_rate', 0):.2f}%</div>
                        </td>
                        <td class="metric-cell" style="border-top: 3px solid {self.colors['uti']}">
                            <div class="metric-label">Ocupação UTI</div>
                            <div class="metric-value">{metrics.get('icu', {}).get('icu_rate', 0):.2f}%</div>
                        </td>
                        <td class="metric-cell" style="border-top: 3px solid {self.colors['vacinacao']}">
                            <div class="metric-label">Vacinação</div>
                            <div class="metric-value">{metrics.get('vaccination', {}).get('vaccination_rate', 0):.2f}%</div>
                        </td>
                    </tr>
                </table>
            </section>

            <section class="section">
                <h2>Visualização Temporal</h2>
                <div class="chart-box">
                    <h3>Casos Diários (30 dias)</h3>
                    {f'<img src="{daily_img}" class="chart-img">' if daily_img else '<p>Gráfico não disponível</p>'}
                </div>
                <div class="chart-box">
                    <h3>Histórico Mensal</h3>
                    {f'<img src="{monthly_img}" class="chart-img">' if monthly_img else '<p>Gráfico não disponível</p>'}
                </div>
            </section>

            <section class="section">
                <h2>Análise Técnica dos Dados</h2>
                <div class="insight">
                    {insights_data.replace('===SEPARADOR===', '').replace('\n', '<br>')}
                </div>
            </section>

            <footer>Sistema de Monitoramento SRAG - Relatório Técnico (Dataset)</footer>
        </body>
        </html>
        """
        
        # Salvar HTML e PDF Dataset
        base_name_data = f"relatorio_dataset_{timestamp}"
        path_html_data = self.output_dir / f"{base_name_data}.html"
        path_pdf_data = self.output_dir / f"{base_name_data}.pdf"
        
        with open(path_html_data, 'w', encoding='utf-8') as f:
            f.write(html_dataset)
        generated_files.append(str(path_html_data))
        
        if self._to_pdf(html_dataset, path_pdf_data):
            generated_files.append(str(path_pdf_data))
        else:
             logger.warning(f"Falha ao gerar PDF de dados: {path_pdf_data}")

        # --- 2. RELATÓRIO DE NOTÍCIAS ---
        html_news = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Contexto de Notícias SRAG</title>
            <style>{self._get_base_styles()}</style>
        </head>
        <body>
            <header>
                <h1>Monitoramento de Mídia e Contexto: SRAG</h1>
                <div class="meta">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Fontes: Gov.br, DuckDuckGo</div>
            </header>

            <section class="section">
                <h2>Análise de Contexto e Correlação</h2>
                <div class="insight">
                    {insights_news.replace('===SEPARADOR===', '').replace('\n', '<br>').replace('•', '&bull;')}
                </div>
            </section>

            <section class="section">
                <h2>Fonte: DuckDuckGo & Gov.br</h2>
                {''.join([f'''
                    <div class="news-item">
                        <div class="news-title"><a href="{n.get('url', '#')}" style="text-decoration:none; color:inherit;">{n.get('title', 'Sem Título')}</a></div>
                        <div class="news-meta">{n.get('source', 'Fonte Desconhecida')} | {n.get('published_at', '')}</div>
                        <div class="news-summary">{n.get('summary', '')}</div>
                    </div>''' for n in news[:8]])}
            </section>

            <footer>Sistema de Monitoramento SRAG - Relatório de Inteligência de Mídia</footer>
        </body>
        </html>
        """
        
        # Salvar HTML e PDF Notícias
        base_name_news = f"relatorio_news_{timestamp}"
        path_html_news = self.output_dir / f"{base_name_news}.html"
        path_pdf_news = self.output_dir / f"{base_name_news}.pdf"
        
        with open(path_html_news, 'w', encoding='utf-8') as f:
            f.write(html_news)
        generated_files.append(str(path_html_news))
        
        if self._to_pdf(html_news, path_pdf_news):
            generated_files.append(str(path_pdf_news))
        else:
             logger.warning(f"Falha ao gerar PDF de notícias: {path_pdf_news}")

        logger.info(f"Relatórios gerados: {len(generated_files)} arquivos.")
        return generated_files

    # Maintain legacy support if needed, or redirect
    def generate_html(self, data: dict, agent_insights: str = "") -> str:
        """Legacy compatibility wrapper."""
        results = self.generate_reports(data)
        return results[0] if results else ""
