import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os

# Daten einlesen
data_file = "Rohdateien.xlsx"
df = pd.read_excel(data_file)

# Berechnung der notwendigen Variablen
df['KI_Correct'] = (df['AIPrediction'] == df['TrueClass']).astype(int)
df['Human_Correct'] = (df['HumanPrediction'] == df['TrueClass']).astype(int)
df['Interaction'] = df['KI_Correct'] * df['Human_Correct']

# Funktion zur Standardisierung einer Spalte
def standardize_column(column):
    return (column - column.mean()) / column.std()

# Zielvariablen standardisieren
df['IoU_std'] = standardize_column(df['IoU'])
df['WBCE_std'] = standardize_column(df['WBCE'])
df['JSD_std'] = standardize_column(df['JSD'])
df['SoftDice_std'] = standardize_column(df['SoftDice'])

# Unabhängige Variablen
X = df[['KI_Correct', 'Human_Correct', 'Interaction']]
X = sm.add_constant(X)

# Regressionen mit standardisierten Zielvariablen
# 1. IoU
y_iou = df['IoU_std']
model_iou = sm.OLS(y_iou, X).fit()
regression_summary_iou = model_iou.summary().as_text()

# 2. WBCE
y_wbce = df['WBCE_std']
model_wbce = sm.OLS(y_wbce, X).fit()
regression_summary_wbce = model_wbce.summary().as_text()

# 3. JSD
y_jsd = df['JSD_std']
model_jsd = sm.OLS(y_jsd, X).fit()
regression_summary_jsd = model_jsd.summary().as_text()

# 4. Soft Dice
y_softdice = df['SoftDice_std']
model_softdice = sm.OLS(y_softdice, X).fit()
regression_summary_softdice = model_softdice.summary().as_text()

# Ordner erstellen, falls er nicht existiert
output_folder = "KI_Mensch_Interaktion"
os.makedirs(output_folder, exist_ok=True)

# Funktion zum Speichern der Regressionsergebnisse als PNG
def save_regression_as_png(summary_text, title, filename):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    plt.title(title, fontsize=16, weight='bold', loc='center')
    plt.text(0.01, 0.99, summary_text, transform=ax.transAxes, fontsize=10, va='top', ha='left', wrap=True, family='monospace')
    plt.savefig(os.path.join(output_folder, filename), dpi=300, bbox_inches='tight')
    plt.close()

# Speichern der Ergebnisse
save_regression_as_png(regression_summary_iou, "Standardisierte Regressionsergebnisse (IoU)", "Standardisierte_Regressionsergebnisse_IoU.png")
save_regression_as_png(regression_summary_wbce, "Standardisierte Regressionsergebnisse (WBCE)", "Standardisierte_Regressionsergebnisse_WBCE.png")
save_regression_as_png(regression_summary_jsd, "Standardisierte Regressionsergebnisse (JSD)", "Standardisierte_Regressionsergebnisse_JSD.png")
save_regression_as_png(regression_summary_softdice, "Standardisierte Regressionsergebnisse (Soft Dice)", "Standardisierte_Regressionsergebnisse_SoftDice.png")

print(f"Die standardisierten Regressionsergebnisse wurden im Ordner '{output_folder}' gespeichert:")
print(f"- Standardisierte_Regressionsergebnisse_IoU.png")
print(f"- Standardisierte_Regressionsergebnisse_WBCE.png")
print(f"- Standardisierte_Regressionsergebnisse_JSD.png")
print(f"- Standardisierte_Regressionsergebnisse_SoftDice.png")


# Funktion zur Erstellung der 4-Felder-Tafel
def create_four_field_table(data, measure, filename, title):
    # Mittelwerte und Beobachtungsanzahl berechnen
    mean_table = pd.pivot_table(
        data,
        values=measure,
        index='Human_Correct',
        columns='KI_Correct',
        aggfunc='mean'
    ).fillna(0)  # NaN-Werte mit 0 auffüllen
    count_table = pd.pivot_table(
        data,
        values=measure,
        index='Human_Correct',
        columns='KI_Correct',
        aggfunc='count'
    ).fillna(0).astype(int)  # NaN-Werte mit 0 auffüllen und in int umwandeln

    # Kombinierte Tabelle mit Mittelwerten und Anzahlen
    combined_table = mean_table.round(2).astype(str) + " (" + count_table.astype(str) + ")"

    # Anpassung der Index- und Spaltennamen für bessere Lesbarkeit
    combined_table.index = ['Mensch Falsch', 'Mensch Richtig']
    combined_table.columns = ['KI Falsch', 'KI Richtig']

    # Erstellung der Grafik
    fig, ax = plt.subplots(figsize=(8, 4))  # Größere Zeilenhöhe
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(
        cellText=combined_table.values,
        rowLabels=combined_table.index,
        colLabels=combined_table.columns,
        loc='center',
        cellLoc='center'
    )

    # Tabellenstil anpassen
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.auto_set_column_width([0, 1, 2])

    # Zeilenhöhe erhöhen und Felder grau hinterlegen
    for (row, col), cell in table.get_celld().items():
        cell.set_height(0.1)  # Zeilenhöhe erhöhen
        if row == 0 or col == -1:  # Kopfzeilen oder Beschreibungen
            cell.set_facecolor('#D3D3D3')  # Grau hinterlegen
            cell.set_text_props(weight='bold')  # Fett

    plt.title(title, fontsize=14, weight='bold')

    # Grafik speichern
    plt.savefig(os.path.join(output_folder, filename), dpi=300, bbox_inches='tight')
    plt.close()


# Erstellung der 4-Felder-Tafeln für jedes Ähnlichkeitsmaß
create_four_field_table(df, 'IoU', "4_Felder_Tafel_IoU.png", "4-Felder-Tafel (IoU)")
create_four_field_table(df, 'WBCE', "4_Felder_Tafel_WBCE.png", "4-Felder-Tafel (WBCE)")
create_four_field_table(df, 'JSD', "4_Felder_Tafel_JSD.png", "4-Felder-Tafel (JSD)")
create_four_field_table(df, 'SoftDice', "4_Felder_Tafel_SoftDice.png", "4-Felder-Tafel (Soft Dice)")

print(f"Die 4-Felder-Tafeln wurden im Ordner '{output_folder}' gespeichert:")
print(f"- 4_Felder_Tafel_IoU.png")
print(f"- 4_Felder_Tafel_WBCE.png")
print(f"- 4_Felder_Tafel_JSD.png")
print(f"- 4_Felder_Tafel_SoftDice.png")