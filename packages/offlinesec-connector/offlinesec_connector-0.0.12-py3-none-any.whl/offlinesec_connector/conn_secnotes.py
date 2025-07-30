
from offlinesec_connector.conn_func import create_temp_dir, read_exclude_file, read_sla_file, delete_files
from offlinesec_connector.rfc_connection import RFCConnection
from offlinesec_connector.rfc_conn_list import RFCConnList
from offlinesec_connector.offlinesec_files import *

def process_connections(conn_settings, temp_dir):
    if conn_settings is None or not len(conn_settings):
        return

    files_to_delete = list()
    sap_conn = RFCConnection(conn_settings)

    if sap_conn.check_conn():
        new_item = dict()
        new_item["name"] = conn_settings["name"]
        new_item["type"] = "ABAP"
        file_softs = create_software_components(sap_conn, temp_dir=temp_dir)
        if file_softs is not None:
            new_item["softs"] = os.path.basename(file_softs)
            files_to_delete.append(file_softs)
        file_notes = create_cwbntcust_file(sap_conn, temp_dir=temp_dir)
        if file_notes is not None:
            new_item["cwbntcust"] = os.path.basename(file_notes)
            files_to_delete.append(file_notes)
        krnl_dict = get_kernel_info(sap_conn)
        if krnl_dict:
            if "version" in krnl_dict:
                new_item["krnl_version"] = krnl_dict["version"]
            if "patch" in krnl_dict:
                new_item["krnl_patch"] = krnl_dict["patch"]

        new_item["files_to_delete"] = files_to_delete
        return new_item
    else:
        if len(sap_conn.errors)>=1:
            print(sap_conn.errors[-1])


def parse_connections_notes(args):
    storage = RFCConnList()
    if not storage.content:
        return

    gen_file_list = list()
    files_to_delete = list()
    exclude_content = None
    sla_content = None

    temp_dir = create_temp_dir()
    if not temp_dir:
        return

    connection_list = list()
    if "conn_id" in args and args["conn_id"] and len(args["conn_id"]):
        connection_list.extend(args["conn_id"])

    if "groups" in args and args["groups"] and len(args["groups"]):
        connection_list.extend(storage.get_conn_list_by_groups(args["groups"], args["group_mode"]))

    if not len(connection_list):
        print(" * [ERROR] The systems by criteria not found")
        return

    if "exclude_file" in args and args["exclude_file"]:
        if not os.path.isfile(args["exclude_file"]):
            print(" * [Warning] The exclusion file '%s' not found" % (args["exclude_file"],))
        else:
            exclude_content = read_exclude_file(args["exclude_file"])

    if "sla_file" in args and args["sla_file"]:
        if not os.path.isfile(args["sla_file"]):
            print(" * [Warning] The exclusion file '%s' not found" % (args["sla_file"],))
        else:
            sla_content = read_sla_file(args["sla_file"])

    for conn_id in connection_list:
        conn_settings = storage.get_conn_by_id(conn_id)
        if conn_settings is None or not len(conn_settings):
            print(" * [Warning] Didn't find connection settings for '%s'" % (conn_id,))
            continue
        new_system = process_connections(conn_settings, temp_dir)
        if new_system is None or not len(new_system):
            print(" * [Warning] Bad connection settings for '%s'" % (conn_id,))
            continue

        if exclude_content:
            exclude_file = get_exclude_file(exclude_content, conn_settings, temp_dir=temp_dir)
            if exclude_file:
                new_system["exclude"] = os.path.basename(exclude_file)
                new_system["files_to_delete"].append(exclude_file)

        if sla_content:
            sla_file = get_sla_file(sla_content, conn_settings, temp_dir=temp_dir)
            if sla_file:
                new_system["sla"] = os.path.basename(sla_file)
                new_system["files_to_delete"].append(sla_file)

        if "files_to_delete" in new_system:
            files_to_delete.extend(new_system["files_to_delete"])
            del new_system["files_to_delete"]
        gen_file_list.append(new_system)


    if len(gen_file_list):
        json_config_file = create_json_config(gen_file_list, temp_dir=temp_dir)
        print(" * Successfully collected data for %s system(s)" % (len(gen_file_list),))
    else:
        print(" * [ERROR] No data to send to the server")
        return
    files_to_delete.append(json_config_file)

    if "do_not_send" in args and args["do_not_send"]:
        return

    if json_config_file:
        run_offlinesec_sec_notes(json_config_file, args)

    if "delete_files" in args and args["delete_files"]:
        delete_files(files_to_delete)