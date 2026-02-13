
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_architecture_diagram():
    # Setup the figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Styles
    box_props = dict(boxstyle='round,pad=0.5', facecolor='#e6f2ff', edgecolor='#0066cc', linewidth=2)
    tool_props = dict(boxstyle='round,pad=0.5', facecolor='#fff2e6', edgecolor='#ff6600', linewidth=2)
    resource_props = dict(boxstyle='round,pad=0.5', facecolor='#e6ffe6', edgecolor='#009933', linewidth=2)
    llm_props = dict(boxstyle='round,pad=0.5', facecolor='#f9e6ff', edgecolor='#9900cc', linewidth=2)
    arrow_props = dict(arrowstyle='->', lw=1.5, color='#333333')

    # Define positions (x, y) - center of boxes
    pos = {
        'User': (6, 9),
        'Orchestrator': (6, 6.5),
        'LLM': (9.5, 6.5),
        'DatabaseTool': (3.5, 4),
        'NewsTool': (8.5, 4),
        'Database': (3.5, 1.5),
        'NewsSource': (8.5, 1.5)
    }

    # Draw Boxes
    # User
    ax.text(pos['User'][0], pos['User'][1], "Usuário\n(Request)", ha='center', va='center', fontsize=12, bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f0f0', edgecolor='#333333'))

    # Orchestrator
    ax.text(pos['Orchestrator'][0], pos['Orchestrator'][1], "Agente Principal\n(Orquestrador)", ha='center', va='center', fontsize=12, fontweight='bold', bbox=box_props)

    # LLM
    ax.text(pos['LLM'][0], pos['LLM'][1], "LLM\n(Claude/Groq)", ha='center', va='center', fontsize=12, bbox=llm_props)

    # Database Tool
    ax.text(pos['DatabaseTool'][0], pos['DatabaseTool'][1], "Ferramenta de Banco\n(DatabaseTool)", ha='center', va='center', fontsize=11, bbox=tool_props)

    # News Tool
    ax.text(pos['NewsTool'][0], pos['NewsTool'][1], "Ferramenta de Notícias\n(NewsTool/WebSearch)", ha='center', va='center', fontsize=11, bbox=tool_props)

    # Database Resource
    ax.text(pos['Database'][0], pos['Database'][1], "Banco de Dados\n(SQLite - Dados SRAG)", ha='center', va='center', fontsize=11, bbox=resource_props)

    # News Resource
    ax.text(pos['NewsSource'][0], pos['NewsSource'][1], "Fontes de Notícias\n(Web/API)", ha='center', va='center', fontsize=11, bbox=resource_props)

    # Draw Arrows
    # User -> Orchestrator
    ax.annotate("", xy=(pos['Orchestrator'][0], pos['Orchestrator'][1]+0.6), xytext=(pos['User'][0], pos['User'][1]-0.4), arrowprops=arrow_props)
    
    # Orchestrator <-> LLM
    ax.annotate("", xy=(pos['LLM'][0]-0.8, pos['LLM'][1]), xytext=(pos['Orchestrator'][0]+1.2, pos['Orchestrator'][1]), arrowprops=dict(arrowstyle='<->', lw=1.5, color='#333333'))
    
    # Orchestrator -> DatabaseTool
    ax.annotate("", xy=(pos['DatabaseTool'][0], pos['DatabaseTool'][1]+0.6), xytext=(pos['Orchestrator'][0]-0.5, pos['Orchestrator'][1]-0.6), arrowprops=arrow_props)
    
    # Orchestrator -> NewsTool
    ax.annotate("", xy=(pos['NewsTool'][0], pos['NewsTool'][1]+0.6), xytext=(pos['Orchestrator'][0]+0.5, pos['Orchestrator'][1]-0.6), arrowprops=arrow_props)

    # DatabaseTool <-> Database
    ax.annotate("", xy=(pos['Database'][0], pos['Database'][1]+0.6), xytext=(pos['DatabaseTool'][0], pos['DatabaseTool'][1]-0.6), arrowprops=dict(arrowstyle='<->', lw=1.5, color='#333333'))
    
    # NewsTool <-> NewsSource
    ax.annotate("", xy=(pos['NewsSource'][0], pos['NewsSource'][1]+0.6), xytext=(pos['NewsTool'][0], pos['NewsTool'][1]-0.6), arrowprops=dict(arrowstyle='<->', lw=1.5, color='#333333'))

    # Add Title
    plt.title("Diagrama Conceitual da Arquitetura da Solução SRAG", fontsize=16, fontweight='bold', pad=20)

    # Save
    plt.savefig('architecture_diagram.pdf', format='pdf', bbox_inches='tight')
    print("PDF generated successfully: architecture_diagram.pdf")

if __name__ == "__main__":
    create_architecture_diagram()
