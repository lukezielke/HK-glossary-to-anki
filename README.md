# HK-glossary-to-anki

A Python script that converts LaTeX glossary files from Prof. Holger Karl into Anki flashcards for efficient studying.

## Features

- Handles both `\newglossaryentry` and `\newacronym` commands
- Automatically converts LaTeX formatting to HTML for Anki
- Generates Anki-compatible CSV files for easy import

## Usage

### Basic Usage
```bash
python main.py glossary.tex
```
Creates `glossary.csv` in the same directory.

### Custom Output File
```bash
python main.py glossary.tex flashcards.csv
```

## Supported LaTeX Formats

### Glossary Entries
```latex
\newglossaryentry{signal}{name=signal, description={A change of a physical quantity that propagates in space and time.}}
```
Result: Front: "signal", Back: "A change of a physical quantity that propagates in space and time."

### Acronyms
```latex
\newacronym{gds}{GDS}{Grundlagen Digitaler Systeme}
```
Result: Front: "GDS", Back: "Grundlagen Digitaler Systeme"

## LaTeX Formatting Support

The script converts common LaTeX formatting to HTML:

| LaTeX | HTML | Display |
|-------|------|---------|
| `\textbf{text}` | `<b>text</b>` | **text** |
| `\textit{text}` | `<i>text</i>` | *text* |

Math notation is preserved for MathJax rendering in Anki.

## Importing into Anki

1. Run the script to generate a CSV file
2. Open Anki and go to **File → Import**
3. Select your CSV file
4. Select comma as the field separator
5. Set field mapping: Field 1 → Front, Field 2 → Back
6. Enable "Allow HTML" for formatting
7. Click Import
