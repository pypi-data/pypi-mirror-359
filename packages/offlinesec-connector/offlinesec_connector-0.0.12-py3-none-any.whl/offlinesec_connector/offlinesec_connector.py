import argparse
import offlinesec_connector.conn_secnotes

def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--request", action='store', choices=["notes", "params"], default="notes",
                        help="Request type", required=False)
    parser.add_argument("-c", "--conn_id", action="append",
                        help="Connection ID", required=False)
    parser.add_argument("-g", "--groups", action="append",
                        help="Connection Groups", required=False)
    parser.add_argument("-m", "--group_mode", action="store", choices=["all", "any"], default="any",
                        help="Group List Variant", required=False)
    parser.add_argument("-e", "--exclude_file", action="store",
                        help="The exclusions (YAML file)", required=False)
    parser.add_argument("-l", "--sla_file", action="store",
                        help="The SLA rules (YAML file)", required=False)
    parser.add_argument("-v", "--variant", action="store",
                        help="The check variant", required=False)
    parser.add_argument("-d", "--delete_files", action="store_true",
                        help="Delete all temporary files after", required=False)
    parser.add_argument("-w", "--wait", action="store_true",
                        help="Wait 5 minutes and download the report automatically", required=False)
    parser.add_argument('--do-not-send', action='store_true',
                        help="Don't upload data to the server")

    parser.parse_args()
    return vars(parser.parse_args())

def main():
    args = init_args()
    if (args["conn_id"] and len(args["conn_id"])) or (args["groups"] and len(args["groups"])):
        if args["request"] and args["request"] == "notes":
            offlinesec_connector.conn_secnotes.parse_connections_notes(args)

if __name__ == "__main__":
    main()