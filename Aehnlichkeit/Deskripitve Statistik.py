import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os

# Ordner erstellen, falls er nicht existiert
output_folder = "Deskriptive Statistik"
os.makedirs(output_folder, exist_ok=True)

# Daten einlesen
data_file = "Rohdateien.xlsx"  # Ersetze mit deinem Dateinamen
df = pd.read_excel(data_file)

# 1. Gruppenanteile
group_summary = df.groupby(['Group', 'UserID']).size().reset_index(name='Count')
group_percentages = group_summary['Group'].value_counts(normalize=True) * 100

# 2. Häufigkeiten der Städte
true_class_counts = df['TrueClass'].value_counts()
ai_prediction_counts = df['AIPrediction'].value_counts()
human_prediction_counts = df['HumanPrediction'].value_counts()

# Kombinieren der Häufigkeiten für das gruppierte Säulendiagramm
frequency_df = pd.DataFrame({
    "Stadt": true_class_counts.index.union(ai_prediction_counts.index).union(human_prediction_counts.index),
    "TrueClass": true_class_counts,
    "AIPrediction": ai_prediction_counts,
    "HumanPrediction": human_prediction_counts
}).fillna(0)  # Fehlende Werte mit 0 füllen
frequency_df = frequency_df.melt(id_vars="Stadt", var_name="Kategorie", value_name="Häufigkeit")

# 3. Gruppiertes Säulendiagramm
fig_grouped = px.bar(
    frequency_df,
    x="Stadt",
    y="Häufigkeit",
    color="Kategorie",
    barmode="group",
    title="Häufigkeiten: TrueClass, AIPrediction und HumanPrediction",
    labels={"Häufigkeit": "Absolute Häufigkeit", "Stadt": "Städte", "Kategorie": "Kategorie"}
)

# 4. Tortendiagramm: Gruppenanteile
fig_pie = px.pie(
    names=group_percentages.index,
    values=group_percentages.values,
    title="Gruppenanteile (Treatment vs Control)"
)


# Relativen Häufigkeiten der Confidence-Werte berechnen
confidence_relative = df['Confidence'].value_counts(normalize=True) * 100
confidence_relative_df = confidence_relative.reset_index()
confidence_relative_df.columns = ['Confidence', 'Relative Häufigkeit (%)']

# Balkendiagramm für relative Häufigkeiten
fig_confidence = px.bar(
    confidence_relative_df,
    x='Confidence',
    y='Relative Häufigkeit (%)',
    title="Relative Häufigkeiten der Confidence-Werte",
    labels={'Confidence': 'Confidence Level', 'Relative Häufigkeit (%)': 'Prozentuale Häufigkeit'},
    text='Relative Häufigkeit (%)'
)

# Balkenbeschriftungen anpassen
fig_confidence.update_traces(texttemplate='%{text:.2f}%', textposition='outside')

# Diagramme als PNG-Dateien speichern
fig_pie.write_image(os.path.join(output_folder, "Gruppenanteile.png"))
fig_grouped.write_image(os.path.join(output_folder, "TrueClass_Human_AI_Haeufigkeiten.png"))
fig_confidence.write_image(os.path.join(output_folder, "Confidence_Relative_Haeufigkeiten.png"))



print(f"Die Visualisierungen wurden im Ordner '{output_folder}' gespeichert.")

# Anzahl, wie häufig jedes Bild vorkommt
image_counts = df['ImageID'].value_counts().reset_index()
image_counts.columns = ['ImageID', 'Häufigkeit']

# Ergebnis in einer Excel-Datei speichern
image_counts_file = os.path.join(output_folder, "Image_Haeufigkeiten.xlsx")
image_counts.to_excel(image_counts_file, index=False)

# Berechnungen für die Übersicht
total_observations = len(df)
unique_users = df['UserID'].nunique()
control_users = df[df['Group'] == 'Control']['UserID'].nunique()
treatment_users = df[df['Group'] == 'Treatment']['UserID'].nunique()
unique_images = df['ImageID'].nunique()
total_berlin = (df['TrueClass'] == "Berlin").sum()
total_hamburg = (df['TrueClass'] == "Hamburg").sum()
total_jerusalem = (df['TrueClass'] == "Jerusalem").sum()
total_telaviv = (df['TrueClass'] == "Tel Aviv").sum()

jerusalem_percentage = (total_jerusalem / total_observations) * 100
berlin_percentage = (total_berlin / total_observations) * 100
hamburg_percentage = (total_hamburg / total_observations) * 100
telaviv_percentage = (total_telaviv / total_observations) * 100

# Übersichtsdaten in einem Dictionary
summary_data = {
    "Anzahl der Beobachtungen": total_observations,
    "Anzahl der Nutzer": unique_users,
    "Anzahl Nutzer (Control)": control_users,
    "Anzahl Nutzer (Treatment)": treatment_users,
    "Anzahl der verschiedenen Bilder": unique_images,
    "Häufigkeit Berlin": f"{total_berlin} ({berlin_percentage:.2f}%)",
    "Häufigkeit Hamburg": f"{total_hamburg} ({hamburg_percentage:.2f}%)",
    "Häufigkeit Jerusalem": f"{total_jerusalem} ({jerusalem_percentage:.2f}%)",
    "Häufigkeit Tel Aviv": f"{total_telaviv} ({telaviv_percentage:.2f}%)",
}

# Übersicht als Grafik darstellen
fig, ax = plt.subplots(figsize=(8, 5))
ax.axis('off')  # Achsen ausblenden

# Tabelle erstellen
table_data = [[key, value] for key, value in summary_data.items()]
table = ax.table(cellText=table_data, colLabels=["Beschreibung", "Wert"], loc='center', cellLoc='center')

# Spaltenüberschriften stylen
for (i, j), cell in table.get_celld().items():
    cell.set_height(0.1)
    if i == 0:  # Header-Zeile
        cell.set_fontsize(12)
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('black')
    elif j == 0:  # Erste Spalte (Beschreibung)
        cell.set_facecolor('#D3D3D3')  # Grau
        cell.set_fontsize(11)
    else:  # Werte-Spalte
        cell.set_fontsize(11)


# Titel hinzufügen
plt.title("Allgemeine Übersicht", fontsize=16, weight='bold')

# Grafik speichern
overview_file = os.path.join(output_folder, "Allgemeine_Uebersicht.png")
plt.savefig(overview_file, dpi=300, bbox_inches='tight')


print(f"Die Bildanzahl wurde in der Datei '{image_counts_file}' gespeichert.")

