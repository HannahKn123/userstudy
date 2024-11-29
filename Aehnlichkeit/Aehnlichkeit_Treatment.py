import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np
import os

# Daten einlesen
data_file = "Rohdateien.xlsx"
df = pd.read_excel(data_file)

# Dummy-Variable für die Treatment Group (1 = Treatment, 0 = Control)
df['Treatment'] = (df['Group'] == 'Treatment').astype(int)

# Ordner erstellen, falls er nicht existiert
output_folder = "Aehnlichkeit_Treatment"
os.makedirs(output_folder, exist_ok=True)


# Funktion zur Durchführung der Regression und Erstellung der Grafiken
def run_regression_and_create_plot(data, dependent_variable, folder_name):
    # Unabhängige Variable (Treatment Dummy)
    X = data[['Treatment']]
    X = sm.add_constant(X)  # Konstante hinzufügen

    # Abhängige Variable
    y = data[dependent_variable]

    # Regression durchführen
    model = sm.OLS(y, X).fit()

    # Ordner für das Ähnlichkeitsmaß erstellen
    subfolder = os.path.join(output_folder, folder_name)
    os.makedirs(subfolder, exist_ok=True)

    # Speichern der Regressionsergebnisse als PNG
    regression_summary = model.summary().as_text()

    def save_regression_as_png(summary_text, title, filename):
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        plt.title(title, fontsize=16, weight='bold', loc='center')
        plt.text(0.01, 0.99, summary_text, transform=ax.transAxes, fontsize=10, va='top', ha='left', wrap=True,
                 family='monospace')
        plt.savefig(os.path.join(subfolder, filename), dpi=300, bbox_inches='tight')
        plt.close()

    save_regression_as_png(
        regression_summary,
        f"Regressionsergebnisse ({dependent_variable})",
        f"Regressionsergebnisse_{dependent_variable}.png"
    )

    # Erstellung der grafischen Darstellung
    fig, ax = plt.subplots(figsize=(8, 6))

    # Datenpunkte hinzufügen
    ax.scatter(data['Treatment'], y, alpha=0.6, label="Datenpunkte", color="blue")

    # Regressionsgerade hinzufügen
    x_values = np.linspace(data['Treatment'].min(), data['Treatment'].max(), 100)
    y_values = model.params['const'] + model.params['Treatment'] * x_values
    ax.plot(x_values, y_values, color="red", label="Regressionsgerade", linewidth=2)

    # Achsenbeschriftungen und Titel
    ax.set_xlabel("Treatment (0 = Control, 1 = Treatment)", fontsize=12)
    ax.set_ylabel(dependent_variable, fontsize=12)
    ax.set_title(f"Regression: {dependent_variable} ~ Treatment", fontsize=14, weight='bold')
    ax.legend()

    # Grafik speichern
    plt.savefig(os.path.join(subfolder, f"Regression_Plot_{dependent_variable}.png"), dpi=300, bbox_inches='tight')
    plt.close()


# Durchführung der Regressionen und Erstellung der Grafiken für alle Ähnlichkeitsmaße
run_regression_and_create_plot(df, 'IoU', 'IoU')
run_regression_and_create_plot(df, 'WBCE', 'WBCE')
run_regression_and_create_plot(df, 'JSD', 'JSD')
run_regression_and_create_plot(df, 'SoftDice', 'SoftDice')

print(f"Die Regressionsergebnisse und Grafiken wurden im Ordner '{output_folder}' gespeichert:")
print(f"- Unterordner für IoU, WBCE, JSD, SoftDice mit Ergebnissen und Grafiken.")
