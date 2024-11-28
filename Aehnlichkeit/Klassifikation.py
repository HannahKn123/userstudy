import pandas as pd
import plotly.express as px
import os

# Ordner erstellen, falls er nicht existiert
output_folder = "Klassifikation"
os.makedirs(output_folder, exist_ok=True)

# Daten einlesen
data_file = "results_with_iou_wbce_jsd_softdice.xlsx"  # Name der Rohdaten-Datei
df = pd.read_excel(data_file)

# Berechnung der Übereinstimmung zwischen Mensch und AI
df['Agreement'] = df['HumanPrediction'] == df['AIPrediction']
agreement_percentage = df['Agreement'].value_counts(normalize=True) * 100
agreement_percentage_df = agreement_percentage.reset_index()
agreement_percentage_df.columns = ['Agreement', 'Prozent']
agreement_percentage_df['Agreement'] = agreement_percentage_df['Agreement'].map({True: 'Übereinstimmung', False: 'Keine Übereinstimmung'})

# Balkendiagramm für die Übereinstimmung (Prozentwerte)
fig_agreement = px.bar(
    agreement_percentage_df,
    x='Agreement',
    y='Prozent',
    title="Übereinstimmung zwischen Mensch und AI (Prozentual)",
    labels={'Agreement': 'Klassifikationsstatus', 'Prozent': 'Prozentuale Häufigkeit'},
    text='Prozent'
)

# Balkenbeschriftungen anpassen
fig_agreement.update_traces(texttemplate='%{text:.2f}%', textposition='outside')

# Berechnung der Richtigkeit der KI-Klassifikation
df['AI_Correct'] = df['AIPrediction'] == df['TrueClass']  # Wahr, wenn die KI korrekt klassifiziert hat
df['Agreement'] = df['HumanPrediction'] == df['AIPrediction']  # Wahr, wenn Mensch und KI übereinstimmen

# Übereinstimmung nach Richtigkeit der KI-Klassifikation
agreement_by_ai_correct = df.groupby(['AI_Correct', 'Agreement']).size().reset_index(name='Anzahl')
agreement_by_ai_correct['AI_Correct'] = agreement_by_ai_correct['AI_Correct'].map({True: 'KI korrekt', False: 'KI falsch'})
agreement_by_ai_correct['Agreement'] = agreement_by_ai_correct['Agreement'].map({True: 'Übereinstimmung', False: 'Keine Übereinstimmung'})

# Prozentuale Häufigkeit berechnen
total_counts = agreement_by_ai_correct.groupby('AI_Correct')['Anzahl'].transform('sum')
agreement_by_ai_correct['Prozent'] = agreement_by_ai_correct['Anzahl'] / total_counts * 100

# Balkendiagramm erstellen
fig_ai_correct = px.bar(
    agreement_by_ai_correct,
    x='AI_Correct',
    y='Prozent',
    color='Agreement',
    barmode='group',
    title="Übereinstimmung von Mensch und KI nach Richtigkeit der KI-Klassifikation",
    labels={'AI_Correct': 'Richtigkeit der KI', 'Prozent': 'Prozentuale Häufigkeit', 'Agreement': 'Übereinstimmung'},
    text='Prozent'
)

# Balkenbeschriftungen hinzufügen
fig_ai_correct.update_traces(texttemplate='%{text:.2f}%', textposition='outside')

# Diagramm speichern
fig_agreement.write_image(os.path.join(output_folder, "Uebereinstimmung_Mensch_AI_Prozent.png"))
fig_ai_correct.write_image(os.path.join(output_folder, "Uebereinstimmung_nach_KI_Richtigkeit.png"))

print(f"Das Diagramm zur Übereinstimmung zwischen Mensch und AI wurde im Ordner '{output_folder}' gespeichert.")
