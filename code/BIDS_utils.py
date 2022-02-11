import pandas as pd
import os
from shutil import copyfile
from . import json_sidecar_generator as jsg
# import glob

def retrieve_db():
    """
    This function prompts the user for a URL and retrieves the Google
    Spreadsheet located at the specified URL.
    INPUTS: none
    OUTPUTS:
    -returns the database in a pandas dataframe
    """

    url_share = input("Enter the Google Spreadsheet URL: ")
    url_csv = url_share.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(url_csv, sep=',', na_filter=True)
    return(df)


def result_location(result_path):
    """
    This function makes sure that the destination for the formated file exists.
    If it doesn't, this function creates it.
    INPUTS:
    -result_path: path of the results folder
    OUTPUTS: none
    """
    
    # Results location existence verifications
    content_result_path = os.listdir(result_path)
    #print(content_result_path)
    content_result_path.sort()
    #print(content_result_path)
    
    # Verification of the existence of the "BIDS_data" folder 
    # -> destination of the processed data from the database:
    #    "repository_root/results/BIDS_data/"
    if content_result_path.count("BIDS_data") == 1:
        print("The results/BIDS_data folder is present.")
        pass
    else:
        os.mkdir(os.path.join(result_path, "BIDS_data"))
        print("The results/BIDS_data folder was created.")

    parent_path = os.path.join(result_path, "BIDS_data")

    # Verification of the existence of the "BIDS_sidecars_originals" folder
    # -> origin of the json files to be copied/pasted along with the processed
    #    data files: repository_root/results/BIDS_sidecars_originals/
    if content_result_path.count("BIDS_sidecars_originals") == 1:
        print("The results/BIDS_sidecars_originals folder is present.")
    
        # Verification of the existence of the json sidecar originals
        sidecar_folder = os.path.join(result_path, "BIDS_sidecars_originals")
        sidecar_list = os.listdir(sidecar_folder)
        sidecar_list.sort()
        # Making sure that they are all present (tymp, reflex, PTA, MTX)
        if (sidecar_list.count("tymp_run_level.json") == 1
            and sidecar_list.count("reflex_run_level.json") == 1
            and sidecar_list.count("pta_run_level.json") == 1
            and sidecar_list.count("mtx_run_level.json") == 1):
            print("The run-level json sidecars for tymp, reflex, PTA and "\
                  "MTX are present.")
            pass
        else:
            # run json_sidecar_generator.py
            jsg
            print("The run-level json sidecars for tymp, reflex, PTA and "\
                  "MTX were created in the results/BIDS_sidecars_originals "\
                  "folder.")
    else:
        # run json_sidecar_generator.py
        jsg
        print("The run-level json sidecars for tymp, reflex, PTA and MTX were "\
              "created in the results/BIDS_sidecars_originals folder.")


# Single test sub-df extraction from each participant's sub-df
def eliminate_columns(sub_df, columns_conditions, test_columns):
    to_keep = columns_conditions + test_columns
    df_test = sub_df[to_keep]

    return df_test


def save_df(data_tosave_df, single_test_df, index, test, parent_path, run="01"):
    """
    This function is used to save the tsv files and json sidecars.
    INPUTS:
    -df to be saved in the tsv file
    -df containing the test columns for a single participant
    -the line index (in single_test_df) linked with the data to save
     (data_tosave_df)
    -the selected test marker
    -path to BIDS_data (repository_root/results/BIDS_data/)
    OUTPUTS:
    -saved tsv file
    -NO specific return to the script
    """
    
    sub = single_test_df['Participant_ID'][index].lstrip('Sub_')

    if (index + 1) < 10:
        ses = '0' + str(index + 1)
    else:
        ses = str(index + 1)

    # The next variable ("ext") can take the value ".csv".
    # The last code section must then be activated
    ext = '.tsv'

    path = os.path.join(parent_path, 'sub-' + sub, 'ses-' + ses)
    file_name = os.path.join('sub-' + sub + '_ses-' + ses + '_task-' + test
                             + '_run-' + run + "_beh")

    data_tosave_df.to_csv(os.path.join(path, file_name + ext), sep='\t')

    json_origin = os.path.join("..", "results", "BIDS_sidecars_originals")

    if test == "Tymp":
        copyfile(os.path.join(json_origin, "tymp_run_level.json"),
                 os.path.join(path, file_name + ".json"))
    elif test == "Reflex":
        copyfile(os.path.join(json_origin, "reflex_run_level.json"),
                 os.path.join(path, file_name + ".json"))
    elif test == "PTA":
        copyfile(os.path.join(json_origin, "pta_run_level.json"),
                 os.path.join(path, file_name + ".json"))
    elif test == "MTX":
        copyfile(os.path.join(json_origin, "mtx_run_level.json"),
                 os.path.join(path, file_name + ".json"))

# Extraction of every single tympanometry test
# The results are then sent to the save_df function to be saved
def extract_tymp(single_test_df, ls_columns_1, ls_columns_2, x, path):

    for j in range(0, len(single_test_df)):
        y = [[], []]

        y[0].append("1")
        y[0].append("R")

        for k in ls_columns_1:
            y[0].append(single_test_df[k][j])

        y[1].append("2")
        y[1].append("L")

        for m in ls_columns_2:
            y[1].append(single_test_df[m][j])

        mask_0 = []
        mask_1 = []

        #print(y[0])
        for n in range(2, len(y[0])):
            if y[0][n] == 'n/a':
                #print(y[0][n], True)
                mask_0.append(True)
            else:
                #print(y[0][n], False)
                mask_0.append(False)

        #print(y[1])
        for p in range(2, len(y[1])):
            if y[1][p] == 'n/a':
                #print(y[1][p], True)
                mask_1.append(True)
            else:
                #print(y[1][p], False)
                mask_1.append(False)

        #print(single_test_df)
        #print(j, y)
        #print(mask_0, mask_1)

        if False in mask_1:
            #print("Keep 2nd line", y)
            pass
        else:
            #print("Delete 2nd line", y)
            del y[1]

        if False in mask_0:
            #print("Keep 1st line", y)
            pass
        else:
            #print("Delete 1st line", y)
            del y[0]

        #print(y.index)
        #print(len(y))
        if len(y) > 0:
            z = pd.DataFrame(data=y, columns=x).set_index("order")
            save_df(z, single_test_df, j, 'Tymp', path)
        else:
            continue

# Extraction of every single stapedial reflex test
# The results are then sent to the save_df function to be saved
def extract_reflex(single_test_df, ls_columns_1, ls_columns_2, x, path):

    for j in range(0, len(single_test_df)):
        y = [[], []]

        y[0].append("1")
        y[0].append("R")

        for k in ls_columns_1:
            y[0].append(single_test_df[k][j])

        y[1].append("2")
        y[1].append("L")

        for m in ls_columns_2:
            y[1].append(single_test_df[m][j])

        mask_0 = []
        mask_1 = []

        #print(y[0])
        for n in range(2, len(y[0])):
            if y[0][n] == 'n/a':
                #print(y[0][n], True)
                mask_0.append(True)
            else:
                #print(y[0][n], False)
                mask_0.append(False)

        #print(y[1])
        for p in range(2, len(y[1])):
            if y[1][p] == 'n/a':
                #print(y[1][p], True)
                mask_1.append(True)
            else:
                #print(y[1][p], False)
                mask_1.append(False)

        #print(single_test_df)
        #print(j, y)
        #print(mask_0, mask_1)

        if False in mask_1:
            #print("Keep 2nd line", y)
            pass
        else:
            #print("Delete 2nd line", y)
            del y[1]

        if False in mask_0:
            #print("Keep 1st line", y)
            pass
        else:
            #print("Delete 1st line", y)
            del y[0]

        #print(y.index)
        #print(len(y))
        if len(y) > 0:
            z = pd.DataFrame(data=y, columns=x).set_index("order")
            save_df(z, single_test_df, j, 'Reflex', path)
        else:
            continue

# Extraction of every single pure-tone audiometry test
# The results are then sent to the save_df function to be saved
def extract_pta(single_test_df, ls_columns_1, ls_columns_2, x, path):

    for j in range(0, len(single_test_df)):
        y = [[], []]

        y[0].append("1")
        y[0].append("R")

        for k in ls_columns_1:
            y[0].append(single_test_df[k][j])

        y[1].append("2")
        y[1].append("L")

        for m in ls_columns_2:
            y[1].append(single_test_df[m][j])

        mask_0 = []
        mask_1 = []

        #print(y[0])
        for n in range(2, len(y[0])):
            if y[0][n] == 'n/a':
                #print(y[0][n], True)
                mask_0.append(True)
            else:
                #print(y[0][n], False)
                mask_0.append(False)

        #print(y[1])
        for p in range(2, len(y[1])):
            if y[1][p] == 'n/a':
                #print(y[1][p], True)
                mask_1.append(True)
            else:
                #print(y[1][p], False)
                mask_1.append(False)

        #print(single_test_df)
        #print(j, y)
        #print(mask_0, mask_1)

        if False in mask_1:
            #print("Keep 2nd line", y)
            pass
        else:
            #print("Delete 2nd line", y)
            del y[1]

        if False in mask_0:
            #print("Keep 1st line", y)
            pass
        else:
            #print("Delete 1st line", y)
            del y[0]

        #print(y.index)
        #print(len(y))
        if len(y) > 0:
            z = pd.DataFrame(data=y, columns=x).set_index("order")
            save_df(z, single_test_df, j, 'PTA', path)
        else:
            continue

  # Extraction of every single matrix speech-in-noise perception test
# The results are then sent to the save_df function to be saved
def extract_mtx(single_test_df, ls_columns_1, ls_columns_2, x, path):

    for j in range(0, len(single_test_df)):
        y = [[], []]

        y[0].append("1")

        for k in ls_columns_1:
            y[0].append(single_test_df[k][j])

        y[1].append("2")

        for m in ls_columns_2:
            y[1].append(single_test_df[m][j])

        mask_0 = []
        mask_1 = []

        #print(y[0])
        for n in range(2, len(y[0])):
            if y[0][n] == 'n/a':
                #print(y[0][n], True)
                mask_0.append(True)
            else:
                #print(y[0][n], False)
                mask_0.append(False)

        #print(y[1])
        for p in range(2, len(y[1])):
            if y[1][p] == 'n/a':
                #print(y[1][p], True)
                mask_1.append(True)
            else:
                #print(y[1][p], False)
                mask_1.append(False)

        #print(single_test_df)
        #print(j, y)
        #print(mask_0, mask_1)

        if False in mask_1:
            #print("Keep 2nd line", y)
            pass
        else:
            #print("Delete 2nd line", y)
            del y[1]

        if False in mask_0:
            #print("Keep 1st line", y)
            pass
        else:
            #print("Delete 1st line", y)
            del y[0]

        #print(y.index)
        #print(len(y))
        if len(y) > 0:
            z = pd.DataFrame(data=y, columns=x).set_index("order")
            save_df(z, single_test_df, j, 'MTX', path)
        else:
            continue

