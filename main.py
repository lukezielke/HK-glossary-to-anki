import csv
import sys
import argparse
from pathlib import Path
import re

def clean_latex_text(text):
    if not text:
        return ""

    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())

    # Convert LaTeX formatting to HTML for Anki
    # Bold text: \textbf{text} -> <b>text</b>
    text = re.sub(r'\\textbf\{([^}]+)\}', r'<b>\1</b>', text)

    # Italic text: \emph{text} -> <i>text</i>
    text = re.sub(r'\\emph\{([^}]+)\}', r'<i>\1</i>', text)

    # Handle mathematical expressions (keep LaTeX math notation)
    # Anki supports MathJax, so we can keep $...$ notation

    # Remove other common LaTeX commands
    text = re.sub(r'\\dots', '...', text)
    text = re.sub(r'\\ldots', '...', text)

    # Clean up any remaining backslashes before common words
    text = re.sub(r'\\([a-zA-Z]+)', r'\1', text)

    return text.strip()


def find_matching_brace(text, start_pos):
    if start_pos >= len(text) or text[start_pos] != '{':
        return -1

    brace_count = 1
    pos = start_pos + 1

    while pos < len(text) and brace_count > 0:
        if text[pos] == '{':
            brace_count += 1
        elif text[pos] == '}':
            brace_count -= 1
        pos += 1

    return pos - 1 if brace_count == 0 else -1


def parse_glossary_entries(tex_content):
    entries = []

    # Find all \newglossaryentry commands
    pattern = r'\\newglossaryentry'

    pos = 0
    while True:
        match = re.search(pattern, tex_content[pos:])
        if not match:
            break

        start_pos = pos + match.start()
        pos = pos + match.end()

        # Find the first opening brace after \newglossaryentry
        first_brace = tex_content.find('{', start_pos)
        if first_brace == -1:
            continue

        # Find the matching closing brace for the key
        key_end = find_matching_brace(tex_content, first_brace)
        if key_end == -1:
            continue

        key = tex_content[first_brace + 1:key_end].strip()

        # Find the second opening brace for parameters
        second_brace = tex_content.find('{', key_end + 1)
        if second_brace == -1:
            continue

        # Find the matching closing brace for parameters
        params_end = find_matching_brace(tex_content, second_brace)
        if params_end == -1:
            continue

        params = tex_content[second_brace + 1:params_end]

        # Parse name parameter
        name_match = re.search(r'name\s*=\s*\{([^}]*)\}|name\s*=\s*([^,}]+)', params)
        name = None
        if name_match:
            name = name_match.group(1) if name_match.group(1) is not None else name_match.group(2)
            if name:
                name = name.strip()

        # Parse description parameter - find "description={" and then find matching brace
        desc_pattern = r'description\s*=\s*\{'
        desc_match = re.search(desc_pattern, params)
        description = None

        if desc_match:
            desc_start = desc_match.end() - 1  # Position of the opening brace
            desc_end = find_matching_brace(params, desc_start)
            if desc_end != -1:
                description = params[desc_start + 1:desc_end].strip()

        # Use key as name if no name is specified
        if not name:
            name = key

        # Clean the text
        if name and description:
            name = clean_latex_text(name)
            description = clean_latex_text(description)

            entries.append({
                'name': name,
                'description': description
            })

        # Move position past this entry
        pos = start_pos + (params_end - start_pos) + 1

    return entries


def parse_acronym_entries(tex_content):
    entries = []

    # Find all \newacronym commands
    pattern = r'\\newacronym'

    pos = 0
    while True:
        match = re.search(pattern, tex_content[pos:])
        if not match:
            break

        start_pos = pos + match.start()
        pos = pos + match.end()

        # Find the first opening brace after \newacronym
        first_brace = tex_content.find('{', start_pos)
        if first_brace == -1:
            continue

        # Find the matching closing brace for the key
        key_end = find_matching_brace(tex_content, first_brace)
        if key_end == -1:
            continue

        key = tex_content[first_brace + 1:key_end].strip()

        # Find the second opening brace for short form
        second_brace = tex_content.find('{', key_end + 1)
        if second_brace == -1:
            continue

        # Find the matching closing brace for short form
        short_end = find_matching_brace(tex_content, second_brace)
        if short_end == -1:
            continue

        short_form = tex_content[second_brace + 1:short_end].strip()

        # Find the third opening brace for long form
        third_brace = tex_content.find('{', short_end + 1)
        if third_brace == -1:
            continue

        # Find the matching closing brace for long form
        long_end = find_matching_brace(tex_content, third_brace)
        if long_end == -1:
            continue

        long_form = tex_content[third_brace + 1:long_end].strip()

        # Clean the text
        short_form = clean_latex_text(short_form)
        long_form = clean_latex_text(long_form)

        if short_form and long_form:
            entries.append({
                'name': short_form,
                'description': long_form
            })

        # Move position past this entry
        pos = start_pos + (long_end - start_pos) + 1

    return entries


def parse_all_entries(tex_content):
    glossary_entries = parse_glossary_entries(tex_content)
    acronym_entries = parse_acronym_entries(tex_content)

    return glossary_entries + acronym_entries


def write_anki_csv(entries, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write entries
        for entry in entries:
            writer.writerow([entry['name'], entry['description']])


def main():
    parser = argparse.ArgumentParser(
        description='Convert LaTeX glossary entries and acronyms to Anki flashcards',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python latex_to_anki.py glossary.tex
    python latex_to_anki.py glossary.tex flashcards.csv
        """
    )

    parser.add_argument('input_file', help='Input LaTeX file (.tex)')
    parser.add_argument('output_file', nargs='?', help='Output CSV file (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)

    # Determine output file
    if args.output_file:
        output_path = Path(args.output_file)
    else:
        output_path = input_path.with_suffix('.csv')

    try:
        # Read LaTeX file
        print(f"Reading LaTeX file: {input_path}")
        with open(input_path, 'r', encoding='utf-8') as file:
            tex_content = file.read()

        # Parse entries (both glossary and acronyms)
        print("Parsing glossary entries and acronyms...")
        entries = parse_all_entries(tex_content)

        if not entries:
            print("Warning: No glossary entries or acronyms found in the input file.")
            print("Make sure the file contains \\newglossaryentry or \\newacronym commands.")
            sys.exit(1)

        # Write CSV
        print(f"Writing {len(entries)} entries to: {output_path}")
        write_anki_csv(entries, output_path)

        if args.verbose:
            print("\nProcessed entries:")
            for i, entry in enumerate(entries, 1):
                print(f"{i:2d}. {entry['name']}")

        print(f"\nSuccess! Created Anki flashcard file: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()