#!/usr/bin/env python3

import argparse
from pathlib import Path
from ruamel.yaml import YAML


def replace_file_paths(obj, new_base):
    """Recursively replace every 'file' entry."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "file" and isinstance(value, str):
                filename = Path(value).name
                obj[key] = str(Path(new_base) / filename)
            else:
                replace_file_paths(value, new_base)

    elif isinstance(obj, list):
        for item in obj:
            replace_file_paths(item, new_base)


def main():
    parser = argparse.ArgumentParser(
        description="Replace all YAML 'file' paths with a new base directory."
    )
    parser.add_argument(
        "-p",
        "--path",
        required=True,
        help="New base directory (e.g. $HOME/data)",
    )
    yaml=YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False

    args = parser.parse_args()
    new_base = Path(args.path).expanduser()

    yaml_files = sorted(Path(".").glob("gotm*.yaml"))

    if not yaml_files:
        print("No matching YAML files found.")
        return

    for yaml_file in yaml_files:
        with open(yaml_file, "r") as f:
            data = yaml.load(f)

        replace_file_paths(data, new_base)

        with open(yaml_file, "w") as f:
            yaml.dump(data,f)

        print(f"Updated {yaml_file}")

    print(f"\nProcessed {len(yaml_files)} files.")


if __name__ == "__main__":
    main()
