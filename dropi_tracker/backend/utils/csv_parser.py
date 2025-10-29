import csv

def parse_csv(file_path):
    """
    Parses a CSV file and returns a list of tracking numbers.
    Assumes the tracking number is in a column named 'tracking_number'.
    """
    tracking_numbers = []
    with open(file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if 'tracking_number' in row:
                tracking_numbers.append(row['tracking_number'])
    return tracking_numbers
