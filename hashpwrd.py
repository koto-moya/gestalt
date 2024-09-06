#!/Users/koto/build/build_venv/bin/python 
from modules.utils import *
from modules.types import *
import argparse

def main():
    parser = argparse.ArgumentParser(prog = "AddUser", description="insert default credentials for a brand liason")
    parser.add_argument('-u', '--username', required = True)
    parser.add_argument('-p', '--password', required = True)
    args = vars(parser.parse_args())
    add_user(args["username"], args["password"])

if __name__ == "__main__":
    main()