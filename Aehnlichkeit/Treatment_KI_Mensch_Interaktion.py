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

# Dummy-Variable für die Treatment Group (1 = Treatment, 0 = Control)
df['Treatment'] = (df['Group'] == 'Treatment').astype(int)

# Funktion zur Standardisierung einer Spalte
def standardize_column(column):
    return (column - column.mean()) / column.std()

# Zielvariablen standardisieren
df['IoU_std'] = standardize_column(df['IoU'])
df['WBCE_std'] = standardize_column(df['WBCE'])
df['JSD_std'] = standardize_column(df['JSD'])
df['SoftDice_std'] = standardize_column(df['SoftDice'])

# Unabhängige Variablen
X = df[['KI_Correct', 'Human_Correct', 'Interaction', 'Treatment']]
X = sm.add_constant(X)  # Konstante hinzufügen

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
output_folder = "Treatment_KI_Mensch_Interaktion"
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


# Funktion zur Erstellung der 4-Felder-Tafel-Daten
def create_four_field_data(data, measure):
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

    # Prüfen, ob die Tabelle leer ist
    if mean_table.empty or count_table.empty:
        # Rückgabe einer leeren Tabelle mit Platzhaltern
        return pd.DataFrame(
            [["0.00 (0)", "0.00 (0)"], ["0.00 (0)", "0.00 (0)"]],
            index=['Mensch Falsch', 'Mensch Richtig'],
            columns=['KI Falsch', 'KI Richtig']
        )

    # Kombinierte Tabelle mit Mittelwerten und Anzahlen
    combined_table = mean_table.round(2).astype(str) + " (" + count_table.astype(str) + ")"

    # Anpassung der Index- und Spaltennamen für bessere Lesbarkeit
    combined_table.index = ['Mensch Falsch', 'Mensch Richtig']
    combined_table.columns = ['KI Falsch', 'KI Richtig']

    return combined_table

# Funktion zur Erstellung der 4-Felder-Tafeln nebeneinander
def create_side_by_side_tables(data, measure, filename, title):
    # Daten für Treatment- und Control-Gruppen
    treatment_data = data[data['Group'] == 'treatment']
    control_data = data[data['Group'] == 'Control']

    treatment_table = create_four_field_data(treatment_data, measure)
    control_table = create_four_field_data(control_data, measure)

    # Erstellung der Grafik
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))  # Zwei Tafeln nebeneinander
    axes[0].axis('tight')
    axes[0].axis('off')
    axes[1].axis('tight')
    axes[1].axis('off')

    # Treatment-Tafel
    treatment_ax = axes[0].table(
        cellText=treatment_table.values,
        rowLabels=treatment_table.index,
        colLabels=treatment_table.columns,
        loc='center',
        cellLoc='center'
    )
    treatment_ax.auto_set_font_size(False)
    treatment_ax.set_fontsize(12)
    treatment_ax.auto_set_column_width([0, 1, 2])
    for (row, col), cell in treatment_ax.get_celld().items():
        cell.set_height(0.1)
        if row == 0 or col == -1:
            cell.set_facecolor('#D3D3D3')
            cell.set_text_props(weight='bold')

    # Control-Tafel
    control_ax = axes[1].table(
        cellText=control_table.values,
        rowLabels=control_table.index,
        colLabels=control_table.columns,
        loc='center',
        cellLoc='center'
    )
    control_ax.auto_set_font_size(False)
    control_ax.set_fontsize(12)
    control_ax.auto_set_column_width([0, 1, 2])
    for (row, col), cell in control_ax.get_celld().items():
        cell.set_height(0.1)
        if row == 0 or col == -1:
            cell.set_facecolor('#D3D3D3')
            cell.set_text_props(weight='bold')

    # Titel hinzufügen
    axes[0].set_title('Treatment Group', fontsize=14, weight='bold')
    axes[1].set_title('Control Group', fontsize=14, weight='bold')
    fig.suptitle(title, fontsize=16, weight='bold')

    # Grafik speichern
    plt.savefig(os.path.join(output_folder, filename), dpi=300, bbox_inches='tight')
    plt.close()

# Erstellung der 4-Felder-Tafeln für jedes Ähnlichkeitsmaß
create_side_by_side_tables(df, 'IoU', "4_Felder_Tafel_IoU.png", "4-Felder-Tafel (IoU)")
create_side_by_side_tables(df, 'WBCE', "4_Felder_Tafel_WBCE.png", "4-Felder-Tafel (WBCE)")
create_side_by_side_tables(df, 'JSD', "4_Felder_Tafel_JSD.png", "4-Felder-Tafel (JSD)")
create_side_by_side_tables(df, 'SoftDice', "4_Felder_Tafel_SoftDice.png", "4-Felder-Tafel (Soft Dice)")

print(f"Die 4-Felder-Tafeln wurden im Ordner '{output_folder}' gespeichert:")
print(f"- 4_Felder_Tafel_IoU.png")
print(f"- 4_Felder_Tafel_WBCE.png")
print(f"- 4_Felder_Tafel_JSD.png")
print(f"- 4_Felder_Tafel_SoftDice.png")