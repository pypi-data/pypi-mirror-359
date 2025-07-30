import socket
from pyrfc import Connection
from  offlinesec_connector.key_storage import OfflinesecKeyring

DELETE_NOT_PYRFC = ["groups", "type"]
DEFAULT_LANGUAGE = "EN"

class RFCConnection:
    def __init__(self, conn_params):
        self.options = conn_params
        for key in DELETE_NOT_PYRFC:
            if key in self.options:
                del self.options[key]

        if "lang" not in self.options:
            self.options["lang"] = DEFAULT_LANGUAGE

        self.get_password_if_needed()

        self.errors = list()
        if not self.check_port_availability():
            self.conn = None
            return

        try:
            self.conn = Connection(**conn_params)
        except Exception as err:
            error_dict = err.__dict__
            if len(error_dict):
                error_to_save = error_dict["key"] if "key" in error_dict else "", error_dict["message"] if "message" in error_dict else ""
            else:
                error_to_save = None, str(err)
            self.errors.append(error_to_save)
            print(error_to_save)
            self.conn = None

    def check_port_availability(self):
        if "mshost" in self.options and "msserv" in self.options:
            host = self.options["mshost"]
            port = int(str(self.options["msserv"]))

        elif "ashost" in self.options  and "sysnr" in self.options :
            host = self.options ["ashost"]
            port = int("33" + str(self.options ["sysnr"]))

        else:
            return False

        if not self.check_port(host, port):
            self.errors.append(" * [Warning] Port %s in unavailable on %s" % (str(port), host,))
        else:
            return True

    def get_password_if_needed(self):
        if "snc_mode" in self.options and self.options["snc_mode"] == "1":
            return

        if "name" in self.options and "user" in self.options and "client" in self.options:
            if not "passwd" in self.options or self.options["passwd"] == "":
                system_name = self.options["name"]
                user_name = self.options["user"]
                client_num = self.options["client"]

                password = OfflinesecKeyring.get_password(system_name, user_name, client_num)
                if password:
                    self.options["passwd"] = password

    def check_port (self, host, port):
        #ip = socket.gethostbyname(socket.gethostname())  # getting ip-address of host
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)

        try:
            is_open = s.connect_ex((host, port)) == 0  # True if open, False if not
            if is_open:
                s.shutdown(socket.SHUT_RDWR)
                return True

        except Exception as err:
            pass
        return False


    def get_value_from_options(self, name):
        if name in self.options:
            return self.options[name]

    def check_conn(self):
        if self.conn is None:
            return False
        return True

    @staticmethod
    def parse_table_data(result):
        data =list()
        for line in result["DATA"]:
            line = line["WA"]
            new_line = dict()
            start_pos = 0
            for i, field in enumerate(result["FIELDS"]):
                field_name = field["FIELDNAME"]
                field_len = int(field["LENGTH"].lstrip("0"))
                new_line[field_name] = line[start_pos:start_pos+field_len].strip()
                start_pos += field_len
            data.append(new_line)
        return data

    @staticmethod
    def parse_software_components(result, fields=["COMPONENT", "RELEASE", "SP", "SP_LEVEL", "DESC_TEXT"]):
        if not "ET_COMPONENTS" in  result:
            return

        table_content = list()
        for line in result["ET_COMPONENTS"]:
            new_line = dict()
            for field in fields:
                if field in line:
                    new_line[field] = line[field]
            table_content.append(new_line)

        return table_content

    def rfc_read_table(self, table_name, fields=list(), chunk_size=1000):
        if not self.check_conn():
            return

        RFC_READ_TABLE = "RFC_READ_TABLE"
        options = dict()
        if not table_name:
            return
        options["QUERY_TABLE"] = table_name
        if fields and len(fields):
            options["FIELDS"] = fields
        table_content = list()
        try:
            options["ROWCOUNT"] = chunk_size
            options["ROWSKIPS"] = 0
            options["GET_SORTED"] = "X"
            while True:
                result = self.conn.call(RFC_READ_TABLE, **options)
                options["ROWSKIPS"]+= options["ROWCOUNT"]

                if len(result['DATA']):
                    table_content.extend(RFCConnection.parse_table_data(result))

                if len(result['DATA']) < options["ROWCOUNT"]:
                    break

        except Exception as err:
            error_dict = err.__dict__
            if len(error_dict):
                error_to_save = error_dict["key"] if "key" in error_dict else "", error_dict["message"] if "message" in error_dict else ""
            else:
                error_to_save = None, str(err)
            self.errors.append(error_to_save)
            print(error_to_save)
            table_content = None
        return table_content

    def software_components(self,chunk_size=1000):
        if not self.check_conn():
            return
        OCS_GET_INSTALLED_COMPS = "OCS_GET_INSTALLED_COMPS"

        options = dict()
        table_content = list()
        try:
            result = self.conn.call(OCS_GET_INSTALLED_COMPS, **options)

            if len(result['ET_COMPONENTS']):
                table_content.extend(RFCConnection.parse_software_components(result))

        except Exception as err:
            error_dict = err.__dict__
            if len(error_dict):
                error_to_save = error_dict["key"] if "key" in error_dict else "", error_dict["message"] if "message" in error_dict else ""
            else:
                error_to_save = None, str(err)
            self.errors.append(error_to_save)
            print(error_to_save)
            table_content = None
        return table_content

    @staticmethod
    def find_kernel_ver(patchhist_tbl):
        if patchhist_tbl and len(patchhist_tbl):
            new_list_0 = list(filter(lambda x: x["EXECUTABLE"] == "disp+work", patchhist_tbl))
            if len(new_list_0):
                new_list_1 = sorted(new_list_0,key=lambda x: x["TIMESTAMP"],  reverse=True)[0]
                return [{ "version": new_list_1["SAPRELEASE"], "patch": new_list_1["PATCHNO"].lstrip("0")}]

    def kernel_info(self,chunk_size=1000):
        # R3Trans
        # tp
        # dbslpatchno

        patchhist = self.rfc_read_table(table_name="PATCHHIST", fields=["EXECUTABLE", "SAPRELEASE", "TIMESTAMP", "PATCHNO"])
        return RFCConnection.find_kernel_ver(patchhist)
