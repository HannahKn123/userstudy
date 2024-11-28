import os
import re
import pandas as pd

# Specify the directory containing the files
directory = r"C:\Users\hanna\OneDrive\Dokumente\#Institut of Business Analytics\user_study\userstudy\userstudy_deploy_control\1_study_input_true"

# Create an empty list to store extracted data
data = []

# Iterate through each file in the directory
for filename in os.listdir(directory):
    # Ensure it's a file with the expected naming pattern
    if filename.startswith("img_"):
        # Extract coordinates, number, and the word after the number
        match = re.match(r"img_(.*)_(\d+)_(\w+)", filename)
        if match:
            coordinates = match.group(1)
            number = match.group(2)
            word = match.group(3)
            data.append({"Coordinates": coordinates, "Number": number, "Word": word})

# Create a DataFrame from the extracted data
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
output_path = os.path.join(directory, "input_data_list.csv")
df.to_csv(output_path, index=False)

# Print the DataFrame to verify
print(df)
