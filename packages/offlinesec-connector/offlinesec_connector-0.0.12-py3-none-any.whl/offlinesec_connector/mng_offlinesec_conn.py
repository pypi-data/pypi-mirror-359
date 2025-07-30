import argparse
from offlinesec_connector.key_storage import OfflinesecKeyring
from offlinesec_connector.rfc_conn_list import RFCConnList

def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", action="store",
                        help="Set new connection from the local file (YAML)", required=False)

    parser.add_argument("-d", "--delete_conn", action="append",
                        help="Connections", required=False)

    parser.add_argument("-l", "--list", action="store_true",
                        help="Print Connections", required=False)

    parser.add_argument("-p", "--password", action="append",
                        help="Delete password for connection", required=False)

    # confirmation of actions

    parser.parse_args()
    return vars(parser.parse_args())

def main():
    args = init_args()
    if "list" in args and args["list"]:
        conn_list = RFCConnList()
        if len(conn_list.content["sap_systems"]):
            conn_list.print_file()

    elif "file" in args and args["file"]:
        conn_list = RFCConnList(ignore_errors=True)
        new_file = conn_list.read_file(args["file"])
        if new_file:
            conn_list.update_content(new_file)
            print("* Settings updated")
            conn_list.save_file_content()

    elif "delete_conn" in args and args["delete_conn"]:
        conn_list = RFCConnList()
        for item in args["delete_conn"]:
            conn_list.delete_by_id(conn_id=item)
        conn_list.save_file_content()

    elif "password" in args and args["password"]:
        conn_list = RFCConnList()
        for item in args["password"]:
            conn_sett = conn_list.get_conn_by_id(item)
            if conn_sett:
                system_name = conn_sett["name"] if "name" in conn_sett else ""
                user_name = conn_sett["user"] if "user" in conn_sett else ""
                client_num = conn_sett["client"] if "client" in conn_sett else ""
                OfflinesecKeyring.delete_password(system_name, user_name, client_num)
            else:
                print(" * [Warning] The connection '%s' not found" % (item,))

if __name__ == "__main__":
    main()