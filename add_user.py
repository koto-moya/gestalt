from psycopg2.extras import RealDictCursor 
import argparse
from modules.db import add_user, get_user, insert_scope

def main():
    parser = argparse.ArgumentParser(prog = "AddUser", description="insert default credentials for a brand liason")
    parser.add_argument('-u', '--username', required = True)
    parser.add_argument('-p', '--password', required = True)
    parser.add_argument('-b', '--brand', required = True)
    parser.add_argument('-e', '--email', required = True)
    parser.add_argument('-s', '--scope', required = True)
    args = vars(parser.parse_args())
    add_user(args["username"], args["password"], args["brand"], args["email"])
    user_id = get_user(args["username"])
    insert_scope(user_id.id, args["scope"])


if __name__ == "__main__":
    main()