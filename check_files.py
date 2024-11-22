import os


def check_files_with_coordinates(source_folder, target_folder):
    """
    Überprüft, ob für jede Datei im `source_folder` eine Datei im `target_folder` existiert,
    die eine Teilzeichenkette aus dem Namen der Datei enthält.

    :param source_folder: Ordner mit den ursprünglichen Dateien
    :param target_folder: Ordner, in dem Dateien überprüft werden
    :return: Liste der Dateien aus dem `source_folder`, die keine Entsprechung im `target_folder` haben
    """
    # Dateien in beiden Ordnern auflisten
    source_files = os.listdir(source_folder)
    target_files = os.listdir(target_folder)

    # Nicht gefundene Dateien speichern
    unmatched_files = []

    for source_file in source_files:
        # Extrahiere die Koordinaten aus dem Namen der Datei
        coordinates = extract_coordinates(source_file)

        # Prüfen, ob die Koordinaten in einer Datei im Zielordner vorkommen
        if coordinates and not any(coordinates in target_file for target_file in target_files):
            unmatched_files.append(source_file)

    return unmatched_files


def extract_coordinates(file_name):
    """
    Extrahiert die Koordinaten aus dem Dateinamen.
    Annahme: Koordinaten enden, wenn bestimmte Städte wie Jerusalem, Tel Aviv, Berlin oder Hamburg auftauchen.

    :param file_name: Name der Datei
    :return: Koordinaten als Zeichenkette oder leer, wenn kein passendes Format gefunden wird
    """
    try:
        # Zielwörter, die das Ende der Koordinaten markieren
        end_markers = ['Jerusalem', 'Tel Aviv', 'Berlin', 'Hamburg']

        # Suche den Startpunkt der Koordinaten
        start = file_name.index('img_') + 4

        # Finde das erste Zielwort, das den Endpunkt markiert
        end = min((file_name.index(marker) for marker in end_markers if marker in file_name), default=len(file_name))

        # Rückgabe des Abschnitts zwischen Start und Endpunkt
        print(file_name[start:end].strip('_'))
        return file_name[start:end].strip('_')

    except ValueError:
        return ""  # Falls das Format nicht passt


# Beispielpfade
t1 = 'userstudy_deploy_control/1_study_input_true'
t2 = 'userstudy_deploy_treatment/1_xai_study_input_true'
t3 = 'Auswertung_Studie/input_study_data/control/1_study_input_true'
t4 = 'Auswertung_Studie/input_study_data/treatment/1_xai_study_input_true'

f1 = 'userstudy_deploy_control/1_study_input_false'
f2 = 'userstudy_deploy_treatment/1_xai_study_input_false'
f3 = 'Auswertung_Studie/input_study_data/control/1_study_input_false'
f4 = 'Auswertung_Studie/input_study_data/treatment/1_xai_study_input_false'



#unmatched_files = check_files_with_coordinates(f1, f2)
# unmatched_files = check_files_with_coordinates(f1, f3)
unmatched_files = check_files_with_coordinates(f1, f4)



if unmatched_files:
    print("Die folgenden Dateien haben kein entsprechendes Gegenstück im Zielordner:")
    for file in unmatched_files:
        print(file)
else:
    print("Alle Dateien im Quellordner haben ein entsprechendes Gegenstück im Zielordner.")


