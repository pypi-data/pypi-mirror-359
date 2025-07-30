import argparse
import sys

VERSION = "0.0.1"
DOLORIS = R"""  ____          _               _      
 |  _ \   ___  | |  ___   _ __ (_) ___ 
 | | | | / _ \ | | / _ \ | '__|| |/ __|
 | |_| || (_) || || (_) || |   | |\__ \
 |____/  \___/ |_| \___/ |_|   |_||___/
"""

def run(cache_path: str):
    raise NotImplementedError

def main():
    parser = argparse.ArgumentParser(
        description="Doloris: Detection Of Learning Obstacles via Risk-aware Interaction Signals"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # version 命令
    subparsers.add_parser("version", help="Print the version of Doloris")

    # run 命令
    run_parser = subparsers.add_parser("run", help="Run the main application")
    run_parser.add_argument(
        "--cache-path",
        type=str,
        default=".cache/",
        help="Path to the cached data directory"
    )

    args = parser.parse_args()

    print(DOLORIS)

    if args.command == "version":
        print(f"Doloris version {VERSION}")
    elif args.command == "run":
        run(args.cache_path)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
