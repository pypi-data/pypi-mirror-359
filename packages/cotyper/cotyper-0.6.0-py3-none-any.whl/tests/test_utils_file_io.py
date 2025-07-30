import tempfile
from pathlib import Path

from cotyper.utils.file_io import load_json


def test_load_json():
    # Create a temporary file with JSON content
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".json"
    ) as temp_file:
        with open(temp_file.name, "w") as f:
            f.write('{"key": "value", "number": 42}')
        temp_file_path = temp_file.name

        # Load the JSON data from the temporary file
        data = load_json(Path(temp_file_path))

        # Check if the data is loaded correctly
        assert data == {"key": "value", "number": 42}
