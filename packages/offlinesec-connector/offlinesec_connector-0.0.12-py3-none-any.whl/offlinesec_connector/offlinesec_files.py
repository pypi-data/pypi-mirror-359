import os
import yaml

DEFAULT_JSON = "offlinesec_config.yaml"

def create_json_config(data, file_name=DEFAULT_JSON, temp_dir=""):
    new_data = dict()
    new_data["root_dir"] = temp_dir
    new_data["sap_systems"] = data

    file_name = get_file_name(file_name)

    try:
        with open(file_name, 'w') as outfile:
            yaml.dump(new_data, outfile)
    except Exception as err:
        print("* [Warning] Can't write JSON file: %s" % (str(err),))
        return

    return file_name

def run_offlinesec_sec_notes(json_config, args):
    cmd_list = list()
    cmd_list.append("offlinesec_sec_notes -f '%s'" % (json_config,))

    if "variant" in args and args["variant"]:
        cmd_list.append("-v %s" % (args["variant"],))
    if "wait" in args and args["wait"]:
        cmd_list.append("-w")

    cmd_line = " ".join(cmd_list)

    try:
        os.system(cmd_line)
    except Exception as err:
        print("* [Warning] Can't execute os command: %s" % (str(err),))


def get_file_name(filename, folder=""):
    full_path = os.path.join(folder, filename)

    if not os.path.isfile(full_path):
        return full_path
    else:
        base = ".".join(filename.split('.')[:-1])
        ext = "." + filename.split('.')[-1]

        for i in range(1, 100):
            full_path = os.path.join(folder, base + "_" + '%03d' % i + ext)
            if not os.path.isfile(full_path):
                return full_path


def save_software_components(file_name, table):
    try:
        with open(file_name, "w") as f:
            for line in table:
                line_in_file = "{component}\t{release}\t{sp_level}\t{sp}\t{desc}\n".format(
                    component=line["COMPONENT"],
                    release=line["RELEASE"],
                    sp_level=line["SP_LEVEL"],
                    sp=line["SP"] if line["SP"].strip() != "" else "-",
                    desc=line["DESC_TEXT"]
                )
                f.write(line_in_file)
    except Exception as err:
        print("* [Warning] Can't write soft file: %s" % (str(err),))

def save_cwbntcust_file(file_name, table):
    try:
        with open(file_name, "w") as f:
            if len(table):
                f.write("-"*20 + "\n")
                fields = ["", "NUMM", "PRSTATUS", "NTSTATUS",""]
                f.write("|".join(fields)+ "\n")
                f.write("-"*20+ "\n")
                for line in table:
                    line_in_file = "|{col1}|{col2}|{col3}|\n".format(
                        col1=line[fields[1]],
                        col2=line[fields[2]],
                        col3=line[fields[3]]
                    )
                    f.write(line_in_file)
    except Exception as err:
        print("* [Warning] Can't write cwbntcust file: %s" % (str(err),))

def create_software_components(rfc_conn, temp_dir=""):
    if not rfc_conn:
        return

    table = rfc_conn.software_components()
    init_file_name = "%s_SOFTS.txt" % (rfc_conn.get_value_from_options("name"))
    file_name = get_file_name(init_file_name, folder=temp_dir)
    save_software_components(file_name, table)

    return file_name

def create_cwbntcust_file(rfc_conn, temp_dir=""):
    if not rfc_conn:
        return

    table = rfc_conn.rfc_read_table(table_name="CWBNTCUST", fields=["NUMM", "NTSTATUS", "PRSTATUS"] )
    init_file_name = "%s_NOTES.txt" % (rfc_conn.get_value_from_options("name"))
    file_name = get_file_name(init_file_name,folder=temp_dir)
    save_cwbntcust_file(file_name, table)

    return file_name

def get_kernel_info(rfc_conn):
    if not rfc_conn:
        return

    krnl = rfc_conn.kernel_info()
    if krnl:
        return krnl[0]

def get_exclude_file(exclude_file_content, connection_settings, temp_dir):
    system_name = connection_settings["name"]
    system_groups = connection_settings["groups"] if "groups" in connection_settings else list()
    init_file_name = "%s_EXCL.yaml" % (system_name,)
    file_name = get_file_name(init_file_name, folder=temp_dir)

    out_list = list()
    for item in exclude_file_content:
        if not "systems" in item:
            continue
        sys_mask = item["systems"]
        flag = False
        for item_sys_mask in sys_mask:
            if item_sys_mask == "*" or item_sys_mask == system_name or item_sys_mask in system_groups:
                flag =True
                break
        if flag:
            new_item = item.copy()
            if "systems" in new_item:
                del new_item["systems"]
            out_list.append(new_item)

    if len(out_list):
        try:
            with open(file_name, "w") as f:
                yaml.dump(out_list, f)
            return file_name
        except Exception as err:
            print(str(err))

def get_sla_file(sla_file_content, connection_settings, temp_dir):
    system_name = connection_settings["name"]
    system_groups = connection_settings["groups"] if "groups" in connection_settings else list()
    init_file_name = "%s_SLA.yaml" % (system_name,)
    file_name = get_file_name(init_file_name, folder=temp_dir)

    temp_list = {
        "hotnews" : (0, 99),
        "high": (0, 99),
        "medium": (0, 99),
        "low": (0, 99),
    }
    for item in sla_file_content:
        if "systems" in item:
            sys_mask = item["systems"]
            flag = False
            for item_sys_mask in sys_mask:
                if item_sys_mask == "*" or item_sys_mask == system_name or item_sys_mask in system_groups:
                    if item_sys_mask == "*":
                        priority = 2
                    elif item_sys_mask == system_name:
                        priority = 0
                    elif item_sys_mask in system_groups:
                        priority = 1
                    flag = True
                    break
            if flag:
                for key in temp_list:
                    if key in item:
                        cur_value, cur_priority = temp_list[key]
                        if priority < cur_priority:
                            temp_list[key] = (item[key], priority)

    content = dict()
    for key in temp_list:
        val,pri = temp_list[key]
        if pri == 99:
            continue
        content[key] = val

    if len(content):
        try:
            with open(file_name, "w") as f:
                yaml.dump(content, f)
            return file_name
        except Exception as err:
            print(str(err))





