import os
import csv

# Set the directory to the the script is in
directory = os.path.dirname(os.path.abspath(__file__))

print(directory)
# Get a list of all the .jpg files in the directory
jpg_files = [f for f in os.listdir(directory) if f.endswith('.jpg')]


# generat a paht to the csv file in the same directory
csv_path = os.path.join(directory, 'file_names.csv')


# Create a new CSV file or overwrite an existing one
with open(csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write each .jpg file name to a new row in the CSV file
    for file_name in jpg_files:
        writer.writerow([file_name])
