import os
import yaml
from pathlib import Path

DEFAULT_FILE_NAME = "sap_connections.yaml"
DEFAULT_DIR = ".offlinesec_client"

class RFCConnList:
    def __init__(self, file_name=DEFAULT_FILE_NAME, file_dir=DEFAULT_DIR, ignore_errors=False):
        self.file_name = os.path.join(Path.home(), DEFAULT_DIR, file_name)

        if os.path.isfile(self.file_name):
            self.content = self.read_file(ignore_errors=ignore_errors)
            if self.content is None or not "sap_systems" in self.content:
                self.content = self.create_file()
        else:
            self.content = self.create_file()
            if not ignore_errors:
                print(" * [ERROR] The '%s' not found in the '%s' folder. Please create the connection file first using offlinesec_conn_settings -f <local_file.yaml>" % (file_name, file_dir))

    def read_file(self, file_name=None, ignore_errors=False):
        file_name = self.file_name if file_name is None else file_name

        if not os.path.isfile(file_name):
            if not ignore_errors:
                print(" * [ERROR] File '%s' not exists" % (file_name,))
            return
        try:
            with open(file_name) as f:
                data = yaml.safe_load(f)

        except Exception as err:
            if not ignore_errors:
                print(" * [ERROR] Bad YAML file: %s" % (str(err),))
            return

        if not "sap_systems" in data:
            if not ignore_errors:
                print(" * [ERROR] Bad config file %s. The 'sap_systems' key not found" % (file_name,))
            return

        return data

    def update_content(self, local_file_data):
        if not "sap_systems" in local_file_data:
            return
        if not isinstance(self.content["sap_systems"],dict):
            self.content["sap_systems"] = dict()
        for conn_id in local_file_data["sap_systems"]:
            self.content["sap_systems"][conn_id] = local_file_data["sap_systems"][conn_id]

    def delete_by_id(self, conn_id):
        conn_by_id = self.get_conn_by_id(conn_id)
        if conn_by_id:
            del self.content["sap_systems"][conn_id]
            print(" * The connection '%s' deleted" % (conn_id,))
        else:
            print(" * [Warning] The connection '%s' not found" % (conn_id,))

    def print_file(self):
        if not os.path.isfile(self.file_name):
            return
        with open(self.file_name) as f:
            for line in f:
                line = line.strip("\r\n")
                print(line)

    def create_file(self):
        new_dict = dict()
        new_dict["sap_systems"] = list()
        return new_dict

    def save_file_content(self):
        temp_dir = os.path.join(Path.home(),DEFAULT_DIR)
        if not os.path.isdir(temp_dir):
            os.mkdir(temp_dir)
        with open(self.file_name,"w") as f:
            yaml.dump(self.content, f)

    def get_conn_by_id(self, conn_id):
        if not self.content:
            return

        if conn_id in self.content["sap_systems"]:
            return self.content["sap_systems"][conn_id]
        else:
            return

    def get_conn_list_by_groups(self, group_list, group_mode):
        return_list = list()

        if group_mode == "any":
            for conn_id in self.content["sap_systems"]:
                if "groups" in self.content["sap_systems"][conn_id]:
                    for group in self.content["sap_systems"][conn_id]["groups"]:
                        if group in group_list:
                            return_list.append(conn_id)
                            break

        elif group_mode == "all":
            for conn_id in self.content["sap_systems"]:
                if "groups" in self.content["sap_systems"][conn_id]:
                    flag = True
                    for group in group_list:
                        if group not in self.content["sap_systems"][conn_id]["groups"]:
                            flag = False
                            break

                    if flag:
                        return_list.append(conn_id)

        return return_list
