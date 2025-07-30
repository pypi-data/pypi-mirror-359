# paulify/cli.py
import argparse

def generate_attribution(project, author, style="plain"):
    base = f'"{project} by {author}, used under PAUL v1.1 license."'
    link = "https://github.com/cactusflatscoder/PAUL"
    if style == "markdown":
        return f"{project} by {author}, used under [PAUL v1.1]({link}) license.\n\n![License: PAUL v1.1](https://img.shields.io/badge/license-PAUL--v1.1-blue)"
    return f"{base}\n{link}"

def main():
    parser = argparse.ArgumentParser(description="Generate PAUL v1.1 license attribution blocks.")
    parser.add_argument("project", help="Project name")
    parser.add_argument("author", help="Author name")
    parser.add_argument("--format", choices=["plain", "markdown"], default="plain", help="Output format")
    args = parser.parse_args()
    print("\n" + generate_attribution(args.project, args.author, args.format))