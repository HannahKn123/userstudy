import pandas as pd
import numpy as np
import os
from scipy.spatial.distance import jensenshannon


def load_human_data(file_path):
    """
    Load human-annotated pixel data from the given file path and convert it into a 448x448 binary mask.
    """
    # Load the data
    data = pd.read_excel(file_path)

    # Create a 448x448 binary mask
    mask = np.zeros((448, 448), dtype=int)

    # Mark the annotated pixels as 1
    for x, y in zip(data['x'], data['y']):
        mask[int(y), int(x)] = 1

    return mask


def load_ai_data(file_path):
    """
    Load AI-annotated pixel data, using importance values.
    """
    data = pd.read_excel(file_path)
    # Create a 2D array of relevance scores
    relevance_map = np.zeros((448, 448), dtype=float)
    for x, y, importance in zip(data['X'], data['Y'], data['Importance']):
        relevance_map[int(y), int(x)] = importance
    return relevance_map


def calculate_iou(human_pixels, ai_pixels):
    """
    Calculate Intersection over Union (IoU) between human and AI pixels.
    """
    # Create binary masks for IoU calculation
    human_mask = human_pixels > 0
    ai_mask = ai_pixels > 0

    intersection = np.logical_and(human_mask, ai_mask).sum()
    union = np.logical_or(human_mask, ai_mask).sum()
    iou = intersection / union if union > 0 else 0
    return iou


def calculate_wbce(human_pixels, ai_relevance, w1=1, w0=1):
    """
    Calculate Weighted Binary Cross-Entropy Loss (WBCE) between human and AI relevance scores.
    """
    human_flat = human_pixels.flatten()
    ai_flat = ai_relevance.flatten()

    epsilon = 1e-7  # Small value to avoid log(0)
    wbce = (
        -np.mean(
            w1 * human_flat * np.log(ai_flat + epsilon)
            + w0 * (1 - human_flat) * np.log(1 - ai_flat + epsilon)
        )
    )
    return wbce


def calculate_jsd(human_pixels, ai_relevance):
    """
    Calculate Jensen-Shannon Divergence (JSD) between human and AI pixel distributions.
    """
    # Flatten arrays and normalize to create probability distributions
    human_distribution = human_pixels.flatten()
    ai_distribution = ai_relevance.flatten()

    # Normalize to probability distributions
    human_prob = human_distribution / np.sum(human_distribution)
    ai_prob = ai_distribution / np.sum(ai_distribution)

    # Add a small constant to avoid division by zero or log(0)
    epsilon = 1e-7
    human_prob = human_prob + epsilon
    ai_prob = ai_prob + epsilon

    # Jensen-Shannon Divergence calculation using scipy
    jsd = jensenshannon(human_prob, ai_prob, base=2)
    return jsd

def calculate_soft_dice(human_pixels, ai_relevance, epsilon=1e-7):
    """
    Calculate the SoftDice coefficient between human and AI relevance scores.
    """
    # Flatten arrays for calculation
    human_flat = human_pixels.flatten()
    ai_flat = ai_relevance.flatten()

    # Compute numerator and denominator
    intersection = np.sum(human_flat * ai_flat)
    sum_human = np.sum(human_flat)
    sum_ai = np.sum(ai_flat)

    # SoftDice formula
    soft_dice = (2 * intersection + epsilon) / (sum_human + sum_ai + epsilon)
    return soft_dice





def extract_metadata_from_filename(filename):
    """
    Extract metadata from the filename of the human-annotated pixel file.
    """
    parts = filename.split('_')
    metadata = {
        "Group": parts[0],  # Treatment or Control
        "UserID": parts[1],
        "ImageID": '_'.join(parts[2:5]),
        "TrueClass": parts[5],
        "AIPrediction": parts[6],
        "HumanPrediction": parts[7],
        "Confidence": parts[8].replace('.xlsx', '')  # Remove file extension
    }
    return metadata


def process_files(human_folder, ai_folder):
    """
    Process all human and AI files to calculate IoU, WBCE, JSD, SoftDice, and extract metadata.
    """
    results = []
    human_files = os.listdir(human_folder)
    ai_files = os.listdir(ai_folder)

    for human_file in human_files:
        # Extract metadata from human file name
        metadata = extract_metadata_from_filename(human_file)

        # Find corresponding AI file
        human_image_id = metadata["ImageID"]
        ai_file = [f for f in ai_files if human_image_id in f]
        if not ai_file:
            continue

        # Load human and AI data
        human_pixels = load_human_data(os.path.join(human_folder, human_file))
        ai_relevance = load_ai_data(os.path.join(ai_folder, ai_file[0]))

        # Calculate IoU
        iou = calculate_iou(human_pixels, ai_relevance)
        metadata["IoU"] = iou

        # Calculate WBCE
        wbce = calculate_wbce(human_pixels, ai_relevance)
        metadata["WBCE"] = wbce

        # Calculate JSD
        jsd = calculate_jsd(human_pixels, ai_relevance)
        metadata["JSD"] = jsd

        # Calculate SoftDice
        soft_dice = calculate_soft_dice(human_pixels, ai_relevance)
        metadata["SoftDice"] = soft_dice

        results.append(metadata)

    return pd.DataFrame(results)



# Define paths
human_folder = r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy\auswertung\auswertung_output_data\treatment\human_pixel_csv"
ai_folder = r"C:\Users\maxim\OneDrive\Desktop\Ausbildung\Master Wiwi\Master Thesis\AI_XAI_Methode\userstudy\AI Model\AllPixels_us"

# Process files and calculate IoU, WBCE, and JSD with metadata
results = process_files(human_folder, ai_folder)

# Save results to an Excel file
output_file = "results_with_iou_wbce_jsd_softdice.xlsx"
results.to_excel(output_file, index=False)
print(f"Results with IoU, WBCE, JSD, and SoftDice saved to {output_file}")

