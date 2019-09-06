import pandas as pd
import os
import numpy as np
import statistics
import math
import re
from configparser import ConfigParser
from datetime import datetime
from openpyxl import load_workbook
import openpyxl


def dev_move(configini):
    print('Running outlier correction : movement...')

    dateTime = datetime.now().strftime('%Y%m%d%H%M%S')
    filesFound = []
    configFile = str(configini)
    config = ConfigParser()
    config.read(configFile)
    vNm_list = []
    loop = 0
    loopy = 0
    configFilelist = []
    use_master = config.get('General settings', 'use_master_config')

    criterion = config.getint('Outlier settings', 'movement_criterion')

    csv_dir = config.get('General settings', 'csv_path')
    csv_dir_in = os.path.join(csv_dir, 'input_csv')
    csv_dir_out = os.path.join(csv_dir, 'outlier_corrected_movement')
    if not os.path.exists(csv_dir_out):
        os.makedirs(csv_dir_out)
    headers = ['Video', "frames_processed", 'Center_M1', "Ear_left_M1", "Ear_right_M1", "Lat_left_M1", "Lat_right_M1",
               "Nose_M1", "Tail_base_M1", "Tail_end_M1", 'Center_M2', "Ear_left_M2", "Ear_right_M2", "Lat_left_M2",
               "Lat_right_M2", "Nose_M2", "Tail_base_M2", "Tail_end_M2", "total_bodyparts_corrected"]
    log_df = pd.DataFrame(columns=headers)

    ########### logfile path ###########
    log_fn = config.get('General settings', 'project_name')
    log_fn = 'Outliers_corrected_movement_' + str(dateTime) + '.csv'
    log_path = config.get('General settings', 'project_path')
    log_path = os.path.join(log_path, 'logs')
    log_fn = os.path.join(log_path, log_fn)
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    def add_correction_prefix(col, bpcorrected_list):
        colc = 'Corrected_' + col
        bpcorrected_list.append(colc)
        return bpcorrected_list

    def correct_value_position(df, colx, coly, col_corr_x, col_corr_y, dict_pos):

        dict_pos[colx] = dict_pos.get(colx, 0)
        dict_pos[coly] = dict_pos.get(coly, 0)

        if "1" in colx or "1" in coly:
            animalSize = mean1size
        if "2" in colx or "2" in coly:
            animalSize = mean2size

        currentCriterion = animalSize * criterion
        list_x = []
        list_y = []
        prev_x = df.iloc[0][colx]
        prev_y = df.iloc[0][coly]
        ntimes = 0
        live_prevx = df.iloc[0][colx]
        live_prevy = df.iloc[0][coly]
        NT = 12
        for index, row in df.iterrows():

            if index == 0:
                continue

            if (math.hypot(row[colx] - prev_x, row[coly] - prev_y) < (animalSize / 4)):  # the mouse is standing still
                currentCriterion = animalSize * 2

            if ((math.hypot(row[colx] - prev_x, row[coly] - prev_y) < currentCriterion) or (ntimes > NT and \
                                                                                            math.hypot(
                                                                                                row[colx] - live_prevx,
                                                                                                row[
                                                                                                    coly] - live_prevy) < currentCriterion)):

                list_x.append(row[colx])
                list_y.append(row[coly])

                prev_x = row[colx]
                prev_y = row[coly]

                ntimes = 0

            else:
                # out of range
                list_x.append(prev_x)
                list_y.append(prev_y)
                dict_pos[colx] += 1
                dict_pos[coly] += 1
                ntimes += 1

            live_prevx = row[colx]
            live_prevy = row[coly]

        df[col_corr_x] = list_x
        df[col_corr_y] = list_y

        return df

    ########### FIND CSV FILES ###########
    if use_master == 'yes':
        for i in os.listdir(csv_dir_in):
            if i.__contains__(".csv"):
                file = os.path.join(csv_dir_in, i)
                filesFound.append(file)
    if use_master == 'no':
        config_folder_path = config.get('General settings', 'config_folder')
        for i in os.listdir(config_folder_path):
            if i.__contains__(".ini"):
                configFilelist.append(os.path.join(config_folder_path, i))
                iniVidName = i.split(".")[0]
                csv_fn = iniVidName + '.csv'
                file = os.path.join(csv_dir_in, csv_fn)
                filesFound.append(file)

    ########### CREATE PD FOR RAW DATA AND PD FOR MOVEMENT BETWEEN FRAMES ###########
    for i in filesFound:
        if use_master == 'no':
            configFile = configFilelist[loopy]
            config = ConfigParser()
            config.read(configFile)
            criterion = config.getint('Outlier settings', 'movement_criterion')
        loopy += 1
        currentFile = i
        csv_df = pd.read_csv(currentFile,
                             names=["Ear_left_1_x", "Ear_left_1_y", "Ear_left_1_p", "Ear_right_1_x", "Ear_right_1_y",
                                    "Ear_right_1_p", "Nose_1_x", "Nose_1_y", "Nose_1_p", "Center_1_x", "Center_1_y",
                                    "Center_1_p", "Lat_left_1_x", "Lat_left_1_y",
                                    "Lat_left_1_p", "Lat_right_1_x", "Lat_right_1_y", "Lat_right_1_p", "Tail_base_1_x",
                                    "Tail_base_1_y", "Tail_base_1_p", "Tail_end_1_x", "Tail_end_1_y", "Tail_end_1_p",
                                    "Ear_left_2_x",
                                    "Ear_left_2_y", "Ear_left_2_p", "Ear_right_2_x", "Ear_right_2_y", "Ear_right_2_p",
                                    "Nose_2_x", "Nose_2_y", "Nose_2_p", "Center_2_x", "Center_2_y", "Center_2_p",
                                    "Lat_left_2_x", "Lat_left_2_y",
                                    "Lat_left_2_p", "Lat_right_2_x", "Lat_right_2_y", "Lat_right_2_p", "Tail_base_2_x",
                                    "Tail_base_2_y", "Tail_base_2_p", "Tail_end_2_x", "Tail_end_2_y", "Tail_end_2_p"])

        csv_df = csv_df.drop(csv_df.index[[0, 1, 2]])
        csv_df = csv_df.apply(pd.to_numeric)

        if 'video_no' not in csv_df.columns:
            videoNumber = os.path.basename(currentFile)
            vNm = videoNumber
            vNm_list.append(vNm)
            videoNumber = re.sub("\D", "", videoNumber)
            csv_df['video_no'] = videoNumber
        if 'frames' not in csv_df.columns:
            csv_df['frames'] = csv_df.index

        ########### CREATE SHIFTED DATAFRAME FOR DISTANCE CALCULATIONS ###########################################
        csv_df_shifted = csv_df.shift(periods=1)
        csv_df_shifted = csv_df_shifted.rename(
            columns={'Ear_left_1_x': 'Ear_left_1_x_shifted', 'Ear_left_1_y': 'Ear_left_1_y_shifted',
                     'Ear_left_1_p': 'Ear_left_1_p_shifted', 'Ear_right_1_x': 'Ear_right_1_x_shifted', \
                     'Ear_right_1_y': 'Ear_right_1_y_shifted', 'Ear_right_1_p': 'Ear_right_1_p_shifted',
                     'Nose_1_x': 'Nose_1_x_shifted', 'Nose_1_y': 'Nose_1_y_shifted', \
                     'Nose_1_p': 'Nose_1_p_shifted', 'Center_1_x': 'Center_1_x_shifted',
                     'Center_1_y': 'Center_1_y_shifted', 'Center_1_p': 'Center_1_p_shifted', 'Lat_left_1_x': \
                         'Lat_left_1_x_shifted', 'Lat_left_1_y': 'Lat_left_1_y_shifted',
                     'Lat_left_1_p': 'Lat_left_1_p_shifted', 'Lat_right_1_x': 'Lat_right_1_x_shifted',
                     'Lat_right_1_y': 'Lat_right_1_y_shifted', \
                     'Lat_right_1_p': 'Lat_right_1_p_shifted', 'Tail_base_1_x': 'Tail_base_1_x_shifted',
                     'Tail_base_1_y': 'Tail_base_1_y_shifted', \
                     'Tail_base_1_p': 'Tail_base_1_p_shifted', 'Tail_end_1_x': 'Tail_end_1_x_shifted',
                     'Tail_end_1_y': 'Tail_end_1_y_shifted', 'Tail_end_1_p': 'Tail_end_1_p_shifted',
                     'Ear_left_2_x': 'Ear_left_2_x_shifted', 'Ear_left_2_y': 'Ear_left_2_y_shifted',
                     'Ear_left_2_p': 'Ear_left_2_p_shifted', 'Ear_right_2_x': 'Ear_right_2_x_shifted', \
                     'Ear_right_2_y': 'Ear_right_2_y_shifted', 'Ear_right_2_p': 'Ear_right_2_p_shifted',
                     'Nose_2_x': 'Nose_2_x_shifted', 'Nose_2_y': 'Nose_2_y_shifted', \
                     'Nose_2_p': 'Nose_2_p_shifted', 'Center_2_x': 'Center_2_x_shifted',
                     'Center_2_y': 'Center_2_y_shifted', 'Center_2_p': 'Center_2_p_shifted', 'Lat_left_2_x': \
                         'Lat_left_2_x_shifted', 'Lat_left_2_y': 'Lat_left_2_y_shifted',
                     'Lat_left_2_p': 'Lat_left_2_p_shifted', 'Lat_right_2_x': 'Lat_right_2_x_shifted',
                     'Lat_right_2_y': 'Lat_right_2_y_shifted', \
                     'Lat_right_2_p': 'Lat_right_2_p_shifted', 'Tail_base_2_x': 'Tail_base_2_x_shifted',
                     'Tail_base_2_y': 'Tail_base_2_y_shifted', \
                     'Tail_base_2_p': 'Tail_base_2_p_shifted', 'Tail_end_2_x': 'Tail_end_2_x_shifted',
                     'Tail_end_2_y': 'Tail_end_2_y_shifted', 'Tail_end_2_p': 'Tail_end_2_p_shifted',
                     'Mouse_1_poly_area': 'Mouse_1_poly_area_shifted',
                     'Mouse_2_poly_area': 'Mouse_2_poly_area_shifted'})

        csv_df_combined = pd.concat([csv_df, csv_df_shifted], axis=1, join='inner')

        ########### EUCLIDEAN DISTANCES ###########################################
        csv_df_combined['Mouse_1_nose_to_tail'] = np.sqrt(
            (csv_df_combined.Nose_1_x - csv_df_combined.Tail_base_1_x) ** 2 + (
                        csv_df_combined.Nose_1_y - csv_df_combined.Tail_base_1_y) ** 2)
        csv_df_combined['Mouse_2_nose_to_tail'] = np.sqrt(
            (csv_df_combined.Nose_2_x - csv_df_combined.Tail_base_2_x) ** 2 + (
                        csv_df_combined.Nose_2_y - csv_df_combined.Tail_base_2_y) ** 2)
        csv_df_combined['Movement_mouse_1_centroid'] = np.sqrt(
            (csv_df_combined.Center_1_x_shifted - csv_df_combined.Center_1_x) ** 2 + (
                        csv_df_combined.Center_1_y_shifted - csv_df_combined.Center_1_y) ** 2)
        csv_df_combined['Movement_mouse_2_centroid'] = np.sqrt(
            (csv_df_combined.Center_2_x_shifted - csv_df_combined.Center_2_x) ** 2 + (
                        csv_df_combined.Center_2_y_shifted - csv_df_combined.Center_2_y) ** 2)
        csv_df_combined['Movement_mouse_1_nose'] = np.sqrt(
            (csv_df_combined.Nose_1_x_shifted - csv_df_combined.Nose_1_x) ** 2 + (
                        csv_df_combined.Nose_1_y_shifted - csv_df_combined.Nose_1_y) ** 2)
        csv_df_combined['Movement_mouse_2_nose'] = np.sqrt(
            (csv_df_combined.Nose_2_x_shifted - csv_df_combined.Nose_2_x) ** 2 + (
                        csv_df_combined.Nose_2_y_shifted - csv_df_combined.Nose_2_y) ** 2)
        csv_df_combined['Movement_mouse_1_tail_base'] = np.sqrt(
            (csv_df_combined.Tail_base_1_x_shifted - csv_df_combined.Tail_base_1_x) ** 2 + (
                        csv_df_combined.Tail_base_1_y_shifted - csv_df_combined.Tail_base_1_y) ** 2)
        csv_df_combined['Movement_mouse_2_tail_base'] = np.sqrt(
            (csv_df_combined.Tail_base_2_x_shifted - csv_df_combined.Tail_base_2_x) ** 2 + (
                        csv_df_combined.Tail_base_2_y_shifted - csv_df_combined.Tail_base_2_y) ** 2)
        csv_df_combined['Movement_mouse_1_tail_end'] = np.sqrt(
            (csv_df_combined.Tail_end_1_x_shifted - csv_df_combined.Tail_end_1_x) ** 2 + (
                        csv_df_combined.Tail_end_1_y_shifted - csv_df_combined.Tail_end_1_y) ** 2)
        csv_df_combined['Movement_mouse_2_tail_end'] = np.sqrt(
            (csv_df_combined.Tail_end_2_x_shifted - csv_df_combined.Tail_end_2_x) ** 2 + (
                        csv_df_combined.Tail_end_2_y_shifted - csv_df_combined.Tail_end_2_y) ** 2)
        csv_df_combined['Movement_mouse_1_left_ear'] = np.sqrt(
            (csv_df_combined.Ear_left_1_x_shifted - csv_df_combined.Ear_left_1_x) ** 2 + (
                        csv_df_combined.Ear_left_1_x - csv_df_combined.Ear_left_1_y) ** 2)
        csv_df_combined['Movement_mouse_2_left_ear'] = np.sqrt(
            (csv_df_combined.Ear_left_2_x_shifted - csv_df_combined.Ear_left_2_x) ** 2 + (
                        csv_df_combined.Ear_left_2_y_shifted - csv_df_combined.Ear_left_2_y) ** 2)
        csv_df_combined['Movement_mouse_1_right_ear'] = np.sqrt(
            (csv_df_combined.Ear_right_1_x_shifted - csv_df_combined.Ear_right_1_x) ** 2 + (
                        csv_df_combined.Ear_right_1_x - csv_df_combined.Ear_right_1_y) ** 2)
        csv_df_combined['Movement_mouse_2_right_ear'] = np.sqrt(
            (csv_df_combined.Ear_right_2_x_shifted - csv_df_combined.Ear_right_2_x) ** 2 + (
                        csv_df_combined.Ear_right_2_y_shifted - csv_df_combined.Ear_right_2_y) ** 2)
        csv_df_combined['Movement_mouse_1_lateral_left'] = np.sqrt(
            (csv_df_combined.Lat_left_1_x_shifted - csv_df_combined.Lat_left_1_x) ** 2 + (
                        csv_df_combined.Lat_left_1_x - csv_df_combined.Lat_left_1_y) ** 2)
        csv_df_combined['Movement_mouse_2_lateral_left'] = np.sqrt(
            (csv_df_combined.Lat_left_2_x_shifted - csv_df_combined.Lat_left_2_x) ** 2 + (
                        csv_df_combined.Lat_left_2_y_shifted - csv_df_combined.Lat_left_2_y) ** 2)
        csv_df_combined['Movement_mouse_1_lateral_right'] = np.sqrt(
            (csv_df_combined.Lat_right_1_x_shifted - csv_df_combined.Lat_right_1_x) ** 2 + (
                        csv_df_combined.Lat_right_1_x - csv_df_combined.Lat_right_1_y) ** 2)
        csv_df_combined['Movement_mouse_2_lateral_right'] = np.sqrt(
            (csv_df_combined.Lat_right_2_x_shifted - csv_df_combined.Lat_right_2_x) ** 2 + (
                        csv_df_combined.Lat_right_2_y_shifted - csv_df_combined.Lat_right_2_y) ** 2)

        csv_df_combined = csv_df_combined.fillna(0)

        ########### MEAN MOUSE SIZES ###########################################
        mean1size = (statistics.mean(csv_df_combined['Mouse_1_nose_to_tail']))
        mean2size = (statistics.mean(csv_df_combined['Mouse_2_nose_to_tail']))

        bps = ['Ear', 'Nose', 'Lat', 'Center', 'Tail_base', 'Tail_end']
        bplist1x = []
        bplist1y = []
        bplist2x = []
        bplist2y = []
        bpcorrected_list1x = []
        bpcorrected_list1y = []
        bpcorrected_list2x = []
        bpcorrected_list2y = []

        for bp in bps:
            # makes the list of body part columns
            if bp in ['Ear', 'Lat']:
                # iterate over left and right
                colx = bp + '_left_1_x'
                coly = bp + '_left_1_y'
                bplist1x.append(colx)
                bplist1y.append(coly)

                bpcorrected_list1x = add_correction_prefix(colx, bpcorrected_list1x)
                bpcorrected_list1y = add_correction_prefix(coly, bpcorrected_list1y)

                colx = bp + '_right_1_x'
                coly = bp + '_right_1_y'

                bplist1x.append(colx)
                bplist1y.append(coly)

                bpcorrected_list1x = add_correction_prefix(colx, bpcorrected_list1x)
                bpcorrected_list1y = add_correction_prefix(coly, bpcorrected_list1y)

                colx = bp + '_left_2_x'
                coly = bp + '_left_2_y'
                bplist2x.append(colx)
                bplist2y.append(coly)

                bpcorrected_list2x = add_correction_prefix(colx, bpcorrected_list2x)
                bpcorrected_list2y = add_correction_prefix(coly, bpcorrected_list2y)

                colx = bp + '_right_2_x'
                coly = bp + '_right_2_y'
                bplist2x.append(colx)
                bplist2y.append(coly)

                bpcorrected_list2x = add_correction_prefix(colx, bpcorrected_list2x)
                bpcorrected_list2y = add_correction_prefix(coly, bpcorrected_list2y)

            else:
                colx = bp + '_1_x'
                coly = bp + '_1_y'
                bplist1x.append(colx)
                bplist1y.append(coly)
                bpcorrected_list1x = add_correction_prefix(colx, bpcorrected_list1x)
                bpcorrected_list1y = add_correction_prefix(coly, bpcorrected_list1y)

                colx = bp + '_2_x'
                coly = bp + '_2_y'
                bplist2x.append(colx)
                bplist2y.append(coly)

                bpcorrected_list2x = add_correction_prefix(colx, bpcorrected_list2x)
                bpcorrected_list2y = add_correction_prefix(coly, bpcorrected_list2y)

        # this dictionary will count the number of times each body part position needs to be corrected
        dict_pos = {}

        for idx, col1x in enumerate(bplist1x):
            # apply function to all body part data
            col1y = bplist1y[idx]
            col_corr_1x = bpcorrected_list1x[idx]
            col_corr_1y = bpcorrected_list1y[idx]
            csv_df_combined = correct_value_position(csv_df_combined, col1x, col1y, col_corr_1x, col_corr_1y, dict_pos)
            col2y = bplist2y[idx]
            col2x = bplist2x[idx]
            col_corr_2x = bpcorrected_list2x[idx]
            col_corr_2y = bpcorrected_list2y[idx]
            csv_df_combined = correct_value_position(csv_df_combined, col2x, col2y, col_corr_2x, col_corr_2y, dict_pos)

        scorer = pd.read_csv(currentFile).scorer.iloc[2:]
        scorer = pd.to_numeric(scorer)
        scorer = scorer.reset_index()
        scorer = scorer.drop(['index'], axis=1)
        csv_df_combined['scorer'] = scorer.values.astype(int)

        csv_df_combined = csv_df_combined[
            ["scorer", "Corrected_Ear_left_1_x", "Corrected_Ear_left_1_y", "Ear_left_1_p", "Corrected_Ear_right_1_x",
             "Corrected_Ear_right_1_y", "Ear_right_1_p", "Corrected_Nose_1_x", "Corrected_Nose_1_y", "Nose_1_p",
             "Corrected_Center_1_x", "Corrected_Center_1_y", "Center_1_p", "Corrected_Lat_left_1_x",
             "Corrected_Lat_left_1_y", "Lat_left_1_p", "Corrected_Lat_right_1_x", "Corrected_Lat_right_1_y",
             "Lat_right_1_p", "Corrected_Tail_base_1_x", "Corrected_Tail_base_1_y", "Tail_base_1_p",
             "Corrected_Tail_end_1_x", "Corrected_Tail_end_1_y", "Tail_end_1_p", "Corrected_Ear_left_2_x",
             "Corrected_Ear_left_2_y", "Ear_left_2_p", "Corrected_Ear_right_2_x", "Corrected_Ear_right_2_y",
             "Ear_right_2_p", "Corrected_Nose_2_x", "Corrected_Nose_2_y", "Nose_2_p", "Corrected_Center_2_x",
             "Corrected_Center_2_y", "Center_2_p", "Corrected_Lat_left_2_x", "Corrected_Lat_left_2_y", "Lat_left_2_p",
             "Corrected_Lat_right_2_x", "Corrected_Lat_right_2_y", "Lat_right_2_p", "Corrected_Tail_base_2_x",
             "Corrected_Tail_base_2_y", "Tail_base_2_p", "Corrected_Tail_end_2_x", "Corrected_Tail_end_2_y",
             "Tail_end_2_p"]]

        # csv_df_combined = csv_df_combined.drop(csv_df_combined.index[0:2])
        df_headers = pd.read_csv(currentFile, nrows=0)
        df_headers['video_no'] = 0
        df_headers['frames'] = 0
        csv_df_combined['video_no'] = csv_df['video_no']
        csv_df_combined['frames'] = np.arange(len(csv_df_combined))
        csv_df_combined.columns = df_headers.columns
        csv_df_combined = pd.concat([df_headers, csv_df_combined])
        fileName = os.path.basename(currentFile)
        fileName, fileEnding = fileName.split('.')
        fileOut = str(fileName) + str('.csv')
        pathOut = os.path.join(csv_dir_out, fileOut)
        csv_df_combined.to_csv(pathOut, index=False)

        fixed_M1_pos = []
        fixed_M2_pos = []
        currentFixedList = []
        currentFixedList.append(int(videoNumber))
        currentFixedList.append(csv_df_combined['frames'].max())
        for k in list(dict_pos):
            if k.endswith('_x'):
                del dict_pos[k]
        for y in list(dict_pos):
            if y.__contains__('_1_'):
                fixed_M1_pos.append(dict_pos[y])
        for y in list(dict_pos):
            if y.__contains__('_2_'):
                fixed_M2_pos.append(dict_pos[y])
        currentFixedList.extend(fixed_M1_pos)
        currentFixedList.extend(fixed_M2_pos)
        totalfixed = sum(fixed_M2_pos) + sum(fixed_M1_pos)
        currentFixedList.append(totalfixed)
        log_df.loc[loop] = currentFixedList

        loop = loop + 1
        print(('Video ') + str(videoNumber) + str(' corrected. Total frames processed: ') + str(
            csv_df_combined['frames'].max()) + '. Total bodyparts corrected mouse 1: ' + str(
            sum(fixed_M1_pos)) + '. ' + 'Total bodyparts corrected mouse 2: ' + str(
            sum(fixed_M2_pos)) + '. Percent body parts corrected: ' + str(
            totalfixed / (csv_df_combined['frames'].max() * 16)) + '.')

    log_df['%bodyparts_corrected'] = log_df['total_bodyparts_corrected'] / (log_df['frames_processed'] * 16)
    log_df['Video'] = str('Video ') + log_df['Video'].apply(str)
    log_df.to_csv(log_fn, index=False)