import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. LEITURA DINÂMICA DO EXCEL
# ==========================================
ARQUIVO_EXCEL = 'planilha.xlsx'

# Lê a planilha sem cabeçalho para facilitar a busca pelas strings exatas nas linhas
try:
    df = pd.read_excel(ARQUIVO_EXCEL, sheet_name=0, header=None)
except Exception as e:
    print(f"Erro ao ler o arquivo Excel: {e}")
    exit()

# Encontra a linha que contém o Nível de Gravidade
idx_gravidade = df[df[0].astype(str).str.contains(
    "NÍVEL DE GRAVIDADE", na=False, case=False)].index

if len(idx_gravidade) == 0:
    print("Erro: Não foi possível encontrar a linha 'NÍVEL DE GRAVIDADE DO PROBLEMA'.")
    exit()
idx_gravidade = idx_gravidade[0]

# Mapeia dinamicamente quais colunas (P1, P2, P3...) têm problemas avaliados
# Ele lê os valores na linha de gravidade (1, 2, 3, 4) para saber que a coluna é válida
gravidades_por_problema = []
colunas_problemas = []

for col in range(1, len(df.columns)):
    val = df.iloc[idx_gravidade, col]
    if pd.notna(val) and str(val).strip().isdigit():
        grav = int(str(val).strip())
        if 0 <= grav <= 4:
            gravidades_por_problema.append(grav)
            colunas_problemas.append(col)

total_problemas = len(colunas_problemas)
print(f"Total de problemas detectados dinamicamente: {total_problemas}")

if total_problemas == 0:
    print("Nenhum problema válido encontrado. Verifique se os números de gravidade estão preenchidos.")
    exit()

# Contagem da incidência das heurísticas (H1 a H10)
heuristicas = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10']
incidencias = []

for h in heuristicas:
    idx_h = df[df[0].astype(str).str.startswith(f"{h}.")].index
    if len(idx_h) > 0:
        idx = idx_h[0]
        # Conta quantos 'x' ou 'X' existem apenas nas colunas identificadas como problemas
        valores = df.iloc[idx, colunas_problemas].astype(
            str).str.strip().str.lower()
        contagem = valores[valores == 'x'].count()
        incidencias.append(contagem)
    else:
        incidencias.append(0)

# Cálculos de Percentuais e Status
perc_problemas = [(qtd / total_problemas) * 100 for qtd in incidencias]

violadas = sum(1 for i in incidencias if i > 0)
atendidas = 10 - violadas
status_heuristicas = [violadas, atendidas]

# Agrupamento das gravidades (0 a 4)
qtd_gravidade = [gravidades_por_problema.count(i) for i in range(5)]
labels_gravidade = ['Grav. 0', 'Grav. 1', 'Grav. 2', 'Grav. 3', 'Grav. 4']

# ==========================================
# 2. GERAÇÃO DOS GRÁFICOS
# ==========================================

# Gráfico 1: Percentual de Incidência
plt.figure(figsize=(10, 6))
bars = plt.bar(heuristicas, perc_problemas, color='#3498db', edgecolor='black')
plt.title('Percentual de Incidência das Heurísticas nos Problemas',
          fontsize=14, pad=15)
plt.ylabel('Percentual (%)', fontsize=12)

# Ajuste dinâmico do eixo Y
max_perc = max(perc_problemas) if perc_problemas else 100
plt.ylim(0, max_perc + 15)

for bar in bars:
    yval = bar.get_height()
    if yval > 0:
        plt.text(bar.get_x() + bar.get_width()/2, yval + (max_perc*0.02),
                 f'{yval:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('grafico1_incidencia_heuristicas.png', dpi=300)
plt.close()

# Gráfico 2: Gravidade
plt.figure(figsize=(8, 5))
bars2 = plt.bar(labels_gravidade, qtd_gravidade,
                color='#e67e22', edgecolor='black')
plt.title('Quantidade de Problemas por Nível de Gravidade', fontsize=14, pad=15)
plt.ylabel('Quantidade de Problemas', fontsize=12)

# Eixo Y apenas com números inteiros
max_grav = max(qtd_gravidade) if max(qtd_gravidade) > 0 else 1
plt.yticks(range(0, max_grav + 2))

for bar in bars2:
    yval = bar.get_height()
    if yval > 0:
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.05,
                 f'{int(yval)}', ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('grafico2_gravidade.png', dpi=300)
plt.close()

# Gráfico 3: Proporção (Pizza)
plt.figure(figsize=(7, 7))
if total_problemas > 0 and violadas > 0:
    plt.pie(status_heuristicas, labels=['Violadas', 'Atendidas'], colors=['#e74c3c', '#2ecc71'],
            autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'black'})
    plt.title('Proporção de Heurísticas Violadas vs Atendidas',
              fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig('grafico3_proporcao_violadas.png', dpi=300)
plt.close()

print("Gráficos atualizados gerados com sucesso baseados nos dados dinâmicos do Excel!")
