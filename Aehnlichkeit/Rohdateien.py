import pandas as pd
import numpy as np
import os
from scipy.spatial.distance import jensenshannon


def load_human_data(file_path):
    """
    Load human-annotated pixel data from the given file path and convert it into a 448x448 binary mask.
    """
    data = pd.read_excel(file_path)
    mask = np.zeros((448, 448), dtype=int)
    for x, y in zip(data['x'], data['y']):
        mask[int(y), int(x)] = 1
    return mask


def load_ai_data(file_path):
    """
    Load AI-annotated pixel data, using importance values.
    """
    data = pd.read_excel(file_path)
    relevance_map = np.zeros((448, 448), dtype=float)
    for x, y, importance in zip(data['X'], data['Y'], data['Importance']):
        relevance_map[int(y), int(x)] = importance
    return relevance_map


def calculate_iou(human_pixels, ai_pixels):
    """
    Calculate Intersection over Union (IoU) between human and AI pixels.
    """
    human_mask = human_pixels > 0
    ai_mask = ai_pixels > 0
    intersection = np.logical_and(human_mask, ai_mask).sum()
    union = np.logical_or(human_mask, ai_mask).sum()
    return intersection / union if union > 0 else 0


def calculate_wbce(human_pixels, ai_relevance, w1=1, w0=1):
    """
    Calculate Weighted Binary Cross-Entropy Loss (WBCE) between human and AI relevance scores.
    """
    human_flat = human_pixels.flatten()
    ai_flat = ai_relevance.flatten()
    epsilon = 1e-7  # Small value to avoid log(0)
    wbce = -np.mean(
        w1 * human_flat * np.log(ai_flat + epsilon)
        + w0 * (1 - human_flat) * np.log(1 - ai_flat + epsilon)
    )
    return wbce


def calculate_jsd(human_pixels, ai_relevance):
    """
    Calculate Jensen-Shannon Divergence (JSD) between human and AI pixel distributions.
    """
    human_distribution = human_pixels.flatten()
    ai_distribution = ai_relevance.flatten()
    human_prob = human_distribution / np.sum(human_distribution)
    ai_prob = ai_distribution / np.sum(ai_distribution)
    epsilon = 1e-7
    human_prob += epsilon
    ai_prob += epsilon
    return jensenshannon(human_prob, ai_prob, base=2)


def calculate_soft_dice(human_pixels, ai_relevance, epsilon=1e-7):
    """
    Calculate the SoftDice coefficient between human and AI relevance scores.
    """
    human_flat = human_pixels.flatten()
    ai_flat = ai_relevance.flatten()
    intersection = np.sum(human_flat * ai_flat)
    sum_human = np.sum(human_flat)
    sum_ai = np.sum(ai_flat)
    return (2 * intersection + epsilon) / (sum_human + sum_ai + epsilon)


def extract_metadata_from_filename_human(filename):
    """
    Extract metadata and ImageID from the filename of the human-annotated pixel file.
    """
    try:
        # Zerlegen des Dateinamens
        parts = filename.split('_')

        # Sicherstellen, dass die minimale Struktur vorhanden ist
        if len(parts) < 8:
            raise ValueError(
                f"Filename {filename} does not contain enough parts to extract metadata."
            )

        # Gruppe bestimmen (t_ oder c_)
        group = 'Treatment' if parts[0] == 't' else 'Control'

        # Dynamische Identifikation der UserID
        user_id_parts = []
        image_id_start = None

        for i, part in enumerate(parts[1:]):  # Teile nach der Gruppe durchgehen
            # Wenn das aktuelle Element ein Koordinatenformat hat, startet hier die ImageID
            if ',' in part and all(c.isdigit() or c in '.-,' for c in part):
                image_id_start = i + 1  # Startposition der ImageID
                break
            user_id_parts.append(part)

        if image_id_start is None:
            raise ValueError(
                f"Filename {filename} does not contain a valid ImageID."
            )

        user_id = '_'.join(user_id_parts)

        # ImageID besteht aus den nächsten zwei Teilen: Koordinaten und Zahlencode
        image_id = '_'.join(parts[image_id_start:image_id_start + 2])

        # Überprüfen, ob genug Teile für die weiteren Metadaten vorhanden sind
        if len(parts) < image_id_start + 6:
            raise ValueError(
                f"Filename {filename} has an unexpected structure after ImageID."
            )

        # Weitere Metadaten
        true_class = parts[image_id_start + 2]  # TrueClass
        ai_prediction = parts[image_id_start + 3]  # AI-Vorhersage
        human_prediction = parts[image_id_start + 4]  # Menschliche Vorhersage
        confidence = parts[image_id_start + 5].replace('.xlsx', '')  # Vertrauen, Dateiendung entfernt

        # Rückgabe der Metadaten als Dictionary
        metadata = {
            "Group": group,
            "UserID": user_id,
            "ImageID": image_id,
            "TrueClass": true_class,
            "AIPrediction": ai_prediction,
            "HumanPrediction": human_prediction,
            "Confidence": confidence,
        }
        return metadata

    except IndexError as e:
        raise ValueError(f"Error processing filename {filename}: {e}")
    except ValueError as e:
        raise ValueError(f"Filename format issue: {e}")


def extract_metadata_from_filename_ai(filename):
    """
    Extract ImageID from the filename of the AI relevance file.
    """
    parts = filename.split('_')
    if parts[0] == 'img':
        image_id = '_'.join(parts[1:3])  # Extract after "img_"
        return image_id
    return None


def process_files(treatment_folder, control_folder, ai_folder):
    """
    Process all human and AI files to calculate IoU, WBCE, JSD, SoftDice, and extract metadata.
    """
    results = []
    human_folders = {'Treatment': treatment_folder, 'Control': control_folder}
    for group, folder in human_folders.items():
        human_files = os.listdir(folder)
        ai_files = os.listdir(ai_folder)

        for human_file in human_files:
            # Extract metadata from human file name
            metadata = extract_metadata_from_filename_human(human_file)
            human_image_id = metadata["ImageID"]

            # Find corresponding AI file
            ai_file = [f for f in ai_files if extract_metadata_from_filename_ai(f) == human_image_id]
            if not ai_file:
                continue

            # Load human and AI data
            human_pixels = load_human_data(os.path.join(folder, human_file))
            ai_relevance = load_ai_data(os.path.join(ai_folder, ai_file[0]))

            # Calculate metrics
            metadata["IoU"] = calculate_iou(human_pixels, ai_relevance)
            metadata["WBCE"] = calculate_wbce(human_pixels, ai_relevance)
            metadata["JSD"] = calculate_jsd(human_pixels, ai_relevance)
            metadata["SoftDice"] = calculate_soft_dice(human_pixels, ai_relevance)

            results.append(metadata)

    return pd.DataFrame(results)


# Define paths
treatment_folder = r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy\Auswertung_Studie\auswertung_study_output_data\treatment\human_pixel_csv"
control_folder = r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy\Auswertung_Studie\auswertung_study_output_data\control\human_pixel_csv"
ai_folder = r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy\AI Model\AllPixels_us"

# Process files and calculate metrics
results = process_files(treatment_folder, control_folder, ai_folder)

# Save results to an Excel file
output_file = "Rohdateien.xlsx"
results.to_excel(output_file, index=False)
print(f"Results with IoU, WBCE, JSD, and SoftDice saved to {output_file}")
