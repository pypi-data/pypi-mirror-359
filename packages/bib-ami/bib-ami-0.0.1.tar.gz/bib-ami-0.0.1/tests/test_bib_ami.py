import tempfile
from pathlib import Path

from bib_ami.bib_ami import merge_bib_files


# noinspection SpellCheckingInspection
def test_merge_bib_files():
    # Create temporary directory and test .bib files
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create two sample .bib files
        bib1 = Path(tmpdirname) / "test1.bib"
        bib2 = Path(tmpdirname) / "test2.bib"
        output = Path(tmpdirname) / "output.bib"

        with bib1.open("w", encoding="utf-8") as f:
            f.write("@article{test1, title={Test 1}}\n")
        with bib2.open("w", encoding="utf-8") as f:
            f.write("@article{test2, title={Test 2}}\n")

        # Run merge
        merge_bib_files(tmpdirname, str(output))

        # Check output file exists and contains both entries
        assert output.exists()
        with output.open("r", encoding="utf-8") as f:
            content = f.read()
            assert "@article{test1" in content
            assert "@article{test2" in content


# noinspection SpellCheckingInspection
def test_merge_bib_files_no_bib_files():
    with tempfile.TemporaryDirectory() as tmpdirname:
        output = Path(tmpdirname) / "output.bib"
        merge_bib_files(tmpdirname, str(output))
        # Should not fail, just log a warning
        assert not output.exists()
