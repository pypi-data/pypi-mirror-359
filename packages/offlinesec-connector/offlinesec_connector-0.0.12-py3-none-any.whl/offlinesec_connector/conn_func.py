import os
import yaml

TEMP_FOLDER = "offlinesec"

def delete_files(files_to_delete):
    for file in files_to_delete:
        try:
            os.remove(file)
        except Exception as err:
            print(" * [Warning] Can't delete %s" % (file,))

def read_exclude_file(file_name):
    try:
        with open(file_name) as f:
            data = yaml.safe_load(f)

    except Exception as err:
        print(" * [Warning] Bad Exclusion file: %s" % (str(err),))
        return

    return data

def read_sla_file(file_name):
    try:
        with open(file_name) as f:
            data = yaml.safe_load(f)

    except Exception as err:
        print(" * [Warning] Bad SLA file: %s" % (str(err),))
        return

    return data

def create_temp_dir(temp_dir=TEMP_FOLDER):
    if not os.path.isdir(temp_dir):
        try:
            os.mkdir(temp_dir)
            return temp_dir
        except:
            print(" * [ERROR] You don't have write permissions to create temp folder")
            return
    else:
        return temp_dir