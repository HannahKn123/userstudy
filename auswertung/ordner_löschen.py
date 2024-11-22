import os
import shutil


def delete_files_but_keep_folders(folder_path):
    """
    Löscht alle Dateien in einem Ordner und dessen Unterordnern, ohne die Ordnerstruktur zu entfernen.
    """
    # Iteriere durch alle Ordner und Dateien
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                os.remove(file_path)  # Datei löschen
                print(f"Datei gelöscht: {file_path}")
            except Exception as e:
                print(f"Fehler beim Löschen der Datei {file_path}: {e}")

    print(f"Alle Dateien in '{folder_path}' wurden gelöscht. Ordnerstruktur bleibt erhalten.")


# Funktion aufrufen
delete_files_but_keep_folders("auswertung_study_output_data")
'''clear_subfolders("userstudy/auswertung/auswertung_study_output_data")
clear_subfolders("userstudy/auswertung/auswertung_study_output_data")
clear_subfolders("userstudy/auswertung/auswertung_study_output_data")
clear_subfolders("userstudy/auswertung/auswertung_study_output_data")'''