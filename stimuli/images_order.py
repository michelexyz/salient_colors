import csv


from ..data_analysis.file_order import split_scenes_shuffle





# Open the csv file and read the file names
with open('file_names.csv', 'r') as file:
    reader = csv.reader(file)
    file_names = [row[0] for row in reader]

# Order the file names using the split_scenes_shuffle function
ordered_file_names = split_scenes_shuffle(file_names)

# save the ordered file names to a new csv file
with open('ordered_file_names.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for file_name in ordered_file_names:
        writer.writerow([file_name])
