import os

# Pfad zu deinem Ordner
folder_path = "C:/Users/hanna/OneDrive/Dokumente/#Institut of Business Analytics/user_study/userstudy/userstudy_deploy_control/1_study_input_true - Kopie"


# Alle Dateien im Ordner durchlaufen
for filename in os.listdir(folder_path):
    # Prüfen, ob es sich um eine Datei handelt
    if os.path.isfile(os.path.join(folder_path, filename)):
        # Prüfen, ob die Datei ".png" enthält
        if ".png" in filename:
            # Entferne ".png" aus der Mitte und füge es am Ende hinzu
            name_without_extension = filename.replace(".png", "")
            new_name = f"{name_without_extension}.png"

            # Pfade für alte und neue Datei erstellen
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_name)

            # Datei umbenennen
            os.rename(old_path, new_path)
            print(f"Umbenannt: {filename} -> {new_name}")
