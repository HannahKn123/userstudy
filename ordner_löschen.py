import os
import shutil

# Liste der Ordner, deren Inhalte gelöscht werden sollen
folders = [
    './annotiert_aus_polygon_image',
    './annotiert_blank_pixel_image',
    './annotiert_pixel_table',
    './annotiert_polygon_table',
    './annotiert_xai_image',
]

# Durchlaufe jeden Ordner und lösche alle Dateien und Unterordner darin
for folder in folders:
    if os.path.exists(folder):
        # Löscht alle Dateien und Ordner in dem Verzeichnis
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Löscht Dateien oder Links
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Löscht Unterordner und deren Inhalte
            except Exception as e:
                print(f'Fehler beim Löschen von {file_path}. Grund: {e}')
        print(f'Alle Inhalte in {folder} wurden erfolgreich gelöscht.')
    else:
        print(f'{folder} existiert nicht.')

print("Löschvorgang abgeschlossen.")
