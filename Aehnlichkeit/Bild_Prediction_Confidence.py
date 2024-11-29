import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

print(f"Die Bildanzahl wurde in der Datei '{image_counts_file}' gespeichert.")

