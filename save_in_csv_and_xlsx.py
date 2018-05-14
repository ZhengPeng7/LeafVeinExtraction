import os
import glob
import csv
from xlsxwriter.workbook import Workbook


def save_in_csv(csv_file, image, curvatures):
    # in csv
    with open(csv_file, "a", newline="") as fin_csv:
        csv_writer = csv.writer(fin_csv, dialect="excel")
        row_header = ['image', 'main_vein_curvature']
        for i in range(len(curvatures)-1):
            row_header.append('sub_vein_' + str(i) + 'curvature')
        len_table = len(max(curvatures, key=len))
        for i in range(len(curvatures)):
            for j in range(len(curvatures[i]), len_table):
                curvatures[i].append('')    # empty-filling value
        csv_writer.writerow(row_header)
        for r in range(len_table):
            row_material = [image]
            for c in range(len(curvatures)):
                row_material.append(str(curvatures[c][r]))
            csv_writer.writerow(row_material)


def csv2xlsx(csv_file):
    if csv_file.split(".")[-1] != "csv":
        csv_file += ".csv"
    print('.'.join(csv_file.split('.')[:-1]) + '.xlsx')
    workbook = Workbook('.'.join(csv_file.split('.')[:-1]) + '.xlsx')
    worksheet = workbook.add_worksheet()
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()
