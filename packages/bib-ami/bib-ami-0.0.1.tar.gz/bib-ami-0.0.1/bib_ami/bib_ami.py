#!/usr/bin/env python3
"""bib_ami: A tool to consolidate and clean BibTeX files.

This script merges all .bib files from a specified directory into a single output file.
Future versions will include deduplication, DOI validation, and metadata refreshing.
"""

import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def merge_bib_files(input_dir: str, output_file: str) -> None:
    """Merge all .bib files from input_dir into a single output_file.

    Args:
        input_dir (str): Directory containing .bib files.
        output_file (str): Path to the output .bib file.
    """
    input_path = Path(input_dir)
    output_path = Path(output_file)

    # Validate input directory
    if not input_path.is_dir():
        logger.error(f"Input directory '{input_dir}' does not exist or is not a directory.")
        raise ValueError(f"Invalid input directory: {input_dir}")

    # Find all .bib files
    bib_files = list(input_path.glob("*.bib"))
    if not bib_files:
        logger.warning(f"No .bib files found in '{input_dir}'.")
        return

    logger.info(f"Found {len(bib_files)} .bib files in '{input_dir}'.")

    # Merge files into output
    with output_path.open("w", encoding="utf-8") as outfile:
        for bib_file in bib_files:
            logger.info(f"Processing '{bib_file}'...")
            try:
                with bib_file.open("r", encoding="utf-8") as infile:
                    content = infile.read()
                    outfile.write(content)
                    # Ensure a newline between files to avoid concatenation issues
                    outfile.write("\n\n")
            except Exception as e:
                logger.error(f"Failed to read '{bib_file}': {e}")
                continue

    logger.info(f"Successfully merged {len(bib_files)} files into '{output_file}'.")


# Placeholder for future functionality (commented out)
"""
def deduplicate_bibtex(input_file: str) -> None:
    # Placeholder for deduplication using bibtexparser
    # Requires: pip install bibtexparser
    pass

def validate_dois(input_file: str) -> None:
    # Placeholder for DOI validation using CrossRef/DataCite APIs
    # Requires: pip install requests
    pass

def refresh_metadata(input_file: str, output_file: str) -> None:
    # Placeholder for refreshing BibTeX metadata with API data
    # Requires: pip install requests bibtexparser
    pass
"""


def main():
    """Parse command-line arguments and run bib-ami."""
    parser = argparse.ArgumentParser(
        description="Merge BibTeX files from a directory into a single file."
    )
    parser.add_argument(
        "--input-dir",
        default=".",
        help="Directory containing .bib files (default: current directory)."
    )
    parser.add_argument(
        "--output-file",
        default="output.bib",
        help="Output file for merged BibTeX entries (default: output.bib)."
    )
    args = parser.parse_args()

    try:
        merge_bib_files(args.input_dir, args.output_file)
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        raise


if __name__ == "__main__":
    main()
