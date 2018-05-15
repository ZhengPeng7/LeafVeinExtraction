import os
import csv
from xlsxwriter.workbook import Workbook
import numpy as np


def save_in_csv_curvature(csv_file, A4_name, curvatures):
    # in csv
    with open(csv_file, "a", newline="") as fin_csv:
        csv_writer = csv.writer(fin_csv, dialect="excel")
        row_header = ['A4_name', 'main_vein_curvature']
        for i in range(len(curvatures)-1):
            row_header.append('sub_vein_' + str(i+1) + '_curvature')
        len_table = len(max(curvatures, key=len))
        for i in range(len(curvatures)):
            for j in range(len(curvatures[i]), len_table):
                curvatures[i].append('')    # empty-filling value
        csv_writer.writerow(row_header)
        for r in range(len_table):
            row_material = [A4_name]
            for c in range(len(curvatures)):
                row_material.append(str(curvatures[c][r]))
            csv_writer.writerow(row_material)


def save_in_csv_general(csv_file, A4_name, curvatures, angles):
    # Sub: angle_mean+median+std, curvature_mean+median+std
    # Main: curvature_mean+median+std, angle_with_main_vein
    with open(csv_file, "a", newline="") as fin_csv:
        csv_writer = csv.writer(fin_csv, dialect="excel")
        row_header = [
                'A4_name', 'sum_leaf/parameters', 'vein_angle_mean',
                'vein_angle_median', 'vein_angle_std', 'top_left_angle',
                'top_right_angle', 'bottom_left_angle', 'bottom_right_angle',
                'main_vein_curvature_mean', 'main_vein_curvature_median',
                'main_vein_curvature_std', 'sub_vein_curvature_mean',
                'sub_vein_curvature_median', 'sub_vein_curvature_std',
                'sub_vein_number ', 'vein_cross_angle_number',
        ]
        for i in range(1, 9):
            row_header.append('vein_cross_angle_'+str(i))
        csv_writer.writerow(row_header)

    # angles of sub veins
    for idx_leaf in range(len(curvatures)):
        for i in range(1, len(angles[idx_leaf])):
            angles[idx_leaf][i] = angles[idx_leaf][i] - angles[idx_leaf][0]
        sub_veins_angle = angles[idx_leaf][1:]
        vein_angle_mean = np.mean(sub_veins_angle)
        vein_angle_median = np.median(sub_veins_angle)
        vein_angle_std = np.std(sub_veins_angle)
        # curvatures of main vein
        main_vein_curvature = curvatures[idx_leaf][0]
        sub_vein_curvature = np.hstack(curvatures[idx_leaf][1:])
        main_vein_curvature_mean = np.mean(main_vein_curvature)
        main_vein_curvature_median = np.median(main_vein_curvature)
        main_vein_curvature_std = np.std(main_vein_curvature)
        with open(csv_file, "a", newline="") as fin_csv:
            csv_writer = csv.writer(fin_csv, dialect="excel")
            row_material = [
                A4_name, 'sub_leaf_'+str(idx_leaf+1),
                vein_angle_mean, vein_angle_median, vein_angle_std,
                '', '', '', '', main_vein_curvature_mean,
                main_vein_curvature_median, main_vein_curvature_std
            ]

            data_lst = [
                np.mean(sub_vein_curvature),
                np.median(sub_vein_curvature),
                np.std(sub_vein_curvature),
                len(angles[idx_leaf])-1,
                len(angles[idx_leaf])-1,
            ]
            for da in data_lst:
                row_material.append(da)
            for ang in sub_veins_angle:
                row_material.append(ang)
            csv_writer.writerow(row_material)


def csv2xlsx(csv_file):
    if csv_file.split(".")[-1] != "csv":
        csv_file += ".csv"
    print('csv2xlsx: ' + '.'.join(csv_file.split('.')[:-1]) + '.xlsx')
    workbook = Workbook('.'.join(csv_file.split('.')[:-1]) + '.xlsx')
    worksheet = workbook.add_worksheet()
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()
