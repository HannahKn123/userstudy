import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Datei laden
file_path = "Rohdateien.xlsx"  # Passe den Pfad an, falls notwendig
data = pd.read_excel(file_path)

# 1. Vergleich der Klassifikationsgenauigkeit zwischen Gruppen
data['CorrectPrediction'] = data['TrueClass'] == data['HumanPrediction']
accuracy_group = data.groupby('Group')['CorrectPrediction'].mean()

# Speichern der Genauigkeit
accuracy_group.to_csv("accuracy_by_group.csv", index=True)

# Visualisierung der Klassifikationsgenauigkeit
plt.figure(figsize=(8, 6))
accuracy_group.plot(kind='bar', color=['blue', 'orange'])
plt.title("Klassifikationsgenauigkeit zwischen Gruppen")
plt.ylabel("Genauigkeit")
plt.xticks(rotation=0)
plt.savefig("classification_accuracy.png")
plt.close()

# 2. Analyse der Selbstsicherheit (Confidence)
confidence_mapping = {'Very Unsure': 1, 'Unsure': 2, 'Neutral': 3, 'Sure': 4, 'Very Sure': 5}
data['ConfidenceLevel'] = data['Confidence'].map(confidence_mapping)

# Boxplot der Selbstsicherheit
plt.figure(figsize=(10, 6))
sns.boxplot(x='Group', y='ConfidenceLevel', data=data)
plt.title("Verteilung der Selbstsicherheit zwischen Gruppen")
plt.ylabel("Selbstsicherheit (1=Very Unsure, 5=Very Sure)")
plt.savefig("confidence_distribution.png")
plt.close()

# 3. Analyse der Markierungsähnlichkeit (IoU)
iou_group = data.groupby('Group')['IoU'].mean()

# Speichern der IoU-Werte
iou_group.to_csv("iou_by_group.csv", index=True)

# Visualisierung der IoU-Werte
plt.figure(figsize=(8, 6))
iou_group.plot(kind='bar', color=['green', 'red'])
plt.title("Durchschnittliche Markierungsähnlichkeit (IoU) zwischen Gruppen")
plt.ylabel("IoU")
plt.xticks(rotation=0)
plt.savefig("iou_similarity.png")
plt.close()

# 4. Unterschiede bei falsch klassifizierten Bildern
wrong_predictions = data[~data['CorrectPrediction']]
wrong_confidence = wrong_predictions.groupby('Group')['ConfidenceLevel'].mean()

# Speichern der Selbstsicherheit bei falschen Klassifikationen
wrong_confidence.to_csv("wrong_confidence_by_group.csv", index=True)

# Visualisierung der Selbstsicherheit bei falschen Klassifikationen
plt.figure(figsize=(8, 6))
wrong_confidence.plot(kind='bar', color=['purple', 'brown'])
plt.title("Selbstsicherheit bei falschen Klassifikationen")
plt.ylabel("Durchschnittliche Selbstsicherheit")
plt.xticks(rotation=0)
plt.savefig("wrong_classification_confidence.png")
plt.close()

# 5. Scatterplot: Zusammenhang zwischen IoU und Selbstsicherheit
plt.figure(figsize=(10, 6))
sns.scatterplot(x='IoU', y='ConfidenceLevel', hue='Group', data=data)
plt.title("Zusammenhang zwischen IoU und Selbstsicherheit")
plt.xlabel("IoU")
plt.ylabel("Selbstsicherheit")
plt.legend(title="Group")
plt.savefig("iou_vs_confidence.png")
plt.close()

# Speichern aller berechneten Daten in eine Excel-Datei
summary_data = {
    "Group": data['Group'],
    "UserID": data['UserID'],
    "CorrectPrediction": data['CorrectPrediction'],
    "ConfidenceLevel": data['ConfidenceLevel'],
    "IoU": data['IoU']
}
summary_df = pd.DataFrame(summary_data)
summary_df.to_excel("experiment_summary.xlsx", index=False)

print("Alle Auswertungen und Diagramme wurden erfolgreich gespeichert.")
