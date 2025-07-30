#!/usr/bin/env python3
import os
from datetime import datetime
import yaml
import logging
from pathlib import Path
import argparse


debug_log_filename = "scrapbook-debug.log"
debug_log_filedirname = "scrapbooking-cli-debug-logs"
debug_log_filedirpath = Path.home() / debug_log_filedirname
debug_log_filepath = debug_log_filedirpath / debug_log_filename


# See function generate_markdown to know why you need this.
backslash_character = chr(10)

config_file_name = "scrapbook_config.yaml"
default_config_file = Path.home() / ".config" / config_file_name
scraps_dir = "scraps"
newline = "\n"


class NoteTakingError(Exception):
    pass


def check_debug_log_path(debug_log_filedirpath):
    if not os.path.exists(debug_log_filedirpath):
        try:
            os.makedirs(debug_log_filedirpath)
            print(f"Directory '{debug_log_filedirpath}' created successfully.")
        except OSError as e:
            raise OSError(f"Error creating directory: {e}")
    else:
        print(
            f"Directory '{debug_log_filedirpath}' exists. Check {debug_log_filepath} for debug/trace logs."
        )

def generate_markdown(heading, contents):
    # Cannot have \n or backslashes in general for brace substitutions in f-strings: see https://stackoverflow.com/questions/67680296/syntaxerror-f-string-expression-part-cannot-include-a-backslash
    markdown_content = f"""
## {heading}
{backslash_character.join([f"- {content}" for content in contents])}
"""
    logging.info("Markdown content generated")
    return markdown_content


def write_to_log_file(file_path, markdown_content):
    try:
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, "a") as file:
            file.write(markdown_content)
        logging.info(f"Scrapbook entry written to file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to write scrapbook entry: {str(e)}")
        raise NoteTakingError(f"Failed to write scrapbook entry`: {str(e)}")


def command_line_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Display this help message",
    )
    return parser.parse_args()


# Define function/variable where press q = quit the program.

def main():
    check_debug_log_path(debug_log_filedirpath)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=debug_log_filepath,
        filemode="a",
    )
    try:
        project_name = input("Enter the project name: ")
        author_name = input("Enter your name: ")
        project_overview = input("Enter project overview: ")
        log_entry_name = input("Enter name of this note: ")
        logging.info(
            f"Generating logs for project: {project_name}, author: {author_name}"
        )


        current_datetime = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_month= datetime.now().strftime("%B")
        current_year = datetime.now().year
        file_path = Path(scraps_dir) / f"{current_year}" / f"{current_month}" / f"{current_date}" / f"{current_datetime}-{log_entry_name}.md"

        markdown_content = \
f"""# Log Entry : {project_name}

## MetaData:
- Author: {author_name}
- Date written: {current_datetime}

## Project Overview:
{project_overview}

"""
        headings = {}
        while True:
            user_input = input("Enter note (or type 'exit' to quit): ").strip()
            if user_input.lower() == 'exit':
                break
            if ':' in user_input:
                heading, note = user_input.split(':', 1)
                heading = heading.strip().capitalize() + 's'
                note = note.strip()
                if heading not in headings:
                    headings[heading] = []
                headings[heading].append(note)
            else:
                print("Invalid input. Please use the format 'heading: note'.")

            
        for heading,notes in headings.items():
            markdown_content += generate_markdown(heading, notes)

        write_to_log_file(file_path, markdown_content)
        print(f"\nScrapbook journal entry created successfully: {file_path}")

    except NoteTakingError as e:
        logging.error(f"Fatal error: {e}")


if __name__ == "__main__":
    print("Happy scrapbooking! Please use the format '{heading}: {note}' to define Markdown headings and notes under the defined heading.")
    main()
