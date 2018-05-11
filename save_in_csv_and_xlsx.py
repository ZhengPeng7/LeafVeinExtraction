import os
import glob
import csv
from xlsxwriter.workbook import Workbook


def save_in_csv_and_xlsx(images, curvatures, angles):
    # in csv
    with open("curvatures_and_angles.csv", "a", newline="") as fin_csv:
        csv_writer = csv.writer(fin_csv, dialect="excel")
        for i in range(len(images) + 1):
            if not i:
                csv_writer.writerow(['images', 'curvatures', 'angles'])
                continue
            csv_writer.writerow([str(images[i - 1]), str(curvatures[i - 1]),
                                 str(angles[i - 1])])


def csv2xlsx(csv_file):
    if csv_file.split(".")[-1] != "csv":
        csv_file += ".csv"
    workbook = Workbook(csv_file.split(".")[0] + '.xlsx')
    worksheet = workbook.add_worksheet()
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()
