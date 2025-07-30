import keyring
import getpass

class OfflinesecKeyring:
    @staticmethod
    def get_service_name(system_name, client_num):
        service_name = "%s_%s" % (system_name, client_num)
        return service_name

    @staticmethod
    def save_password(system_name, user_name, client_num, password):
        service_name = OfflinesecKeyring.get_service_name(system_name, client_num)
        keyring.set_password(service_name=service_name,
                             username=user_name,
                             password=password)

    @staticmethod
    def delete_password(system_name, user_name, client_num):
        service_name = OfflinesecKeyring.get_service_name(system_name, client_num)
        try:
            keyring.delete_password(service_name=service_name, username=user_name)
            print(" * The password for '%s:%s (%s)' deleted" % (system_name, client_num, user_name))
        except Exception as err:
            print(" * [Warning] The password not found in KeyRing DB for '%s:%s (%s)' " % (system_name, client_num, user_name))

    @staticmethod
    def get_password(system_name, user_name, client_num):
        service_name = OfflinesecKeyring.get_service_name(system_name, client_num)
        password_in_storage = keyring.get_password(service_name=service_name,
                                                   username=user_name)
        if password_in_storage is None:
            x = input(" * [ERROR] Password for system: %s , client: %s, user: %s not found. Do you like to set it now? (N\y): " % (system_name, client_num, user_name))
            if x in ["Y", "y"]:
                print("Please set the new password for system: %s , client: %s, user: %s" % (system_name, client_num, user_name))
                while True:
                    x1 = getpass.getpass("New password:")
                    x2 = getpass.getpass("Repeat password:")
                    if x1==x2:
                        break
                    else:
                        print("* [Warning] The passwords not matched. Please try again")
                OfflinesecKeyring.save_password(system_name, user_name, client_num, x1)
                return x1
        else:
            return password_in_storage
