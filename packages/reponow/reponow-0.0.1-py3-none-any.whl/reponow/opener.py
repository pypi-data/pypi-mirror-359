import argparse
import subprocess
from rich import print
from reponow.parser import parse_url
from reponow.wcl import clone_repo

# constants for subprocess.run for readability
IGNORE_FAILURE = False
STOP_ON_FAILURE = True


def main():

    parser = argparse.ArgumentParser(description="(w)es (cl)one", prog="wcl")
    parser.add_argument("url", type=str, help="repository clone url")
    args = parser.parse_args()

    clone_repo(args.url)

    repo_dir, _ = parse_url(args.url)
    subprocess.run(f"code '{repo_dir}'", shell=True, check=IGNORE_FAILURE, stdout=subprocess.DEVNULL)

if __name__ == "__main__":
    main()

