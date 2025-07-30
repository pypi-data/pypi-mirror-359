import time
# Simulate heavy imports
import matplotlib.pyplot as plt  # noqa: F401
import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
import sklearn  # noqa: F401
import requests  # noqa: F401
import click  # noqa: F401

time.sleep(5)  # Simulate slow startup

import argparse
import argcomplete

def main():
    parser = argparse.ArgumentParser(description="A slow CLI tool for testing tab completion.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: foo
    parser_foo = subparsers.add_parser("foo", help="Run foo command")
    parser_foo.add_argument("--bar", type=int, help="Bar value")
    parser_foo.add_argument("--baz", choices=["a", "b", "c"], help="Baz option")

    # Subcommand: data
    parser_data = subparsers.add_parser("data", help="Run data command")
    parser_data.add_argument("--file", type=str, help="Input file")
    parser_data.add_argument("--mode", choices=["fast", "slow"], help="Mode")

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.command == "foo":
        print(f"Running foo with bar={args.bar}, baz={args.baz}")
    elif args.command == "data":
        print(f"Running data with file={args.file}, mode={args.mode}")
    else:
        parser.print_help()
