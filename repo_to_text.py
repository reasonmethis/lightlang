import os
import subprocess

OUTPUT_FILE = "output.txt"
IGNORE_DIRS = [".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build"]
IGNORE_FILES = [OUTPUT_FILE, "repo_to_text.py"]

file_path_header = """

----------------------------------------------------------------
CONTENT OF {relative_path}
----------------------------------------------------------------

"""


def is_gitignored(file_path):
    """Check if a file is gitignored by using Git's check-ignore command."""
    try:
        subprocess.run(["git", "check-ignore", "-q", file_path], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def is_ignored(file_path: str) -> bool:
    """Check if a file is ignored."""
    if file_path in IGNORE_FILES:
        return True
    if any(file_path.startswith(f"{dir}/") for dir in IGNORE_DIRS):
        return True
    return is_gitignored(file_path)


def write_files_to_output(output_file):
    """Write the contents of all non-ignored files to the output file."""
    with open(output_file, encoding="utf-8", mode="w") as out_f:
        for root, dirs, files in os.walk("."):
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file))
                if not is_ignored(relative_path):
                    out_f.write(file_path_header.format(relative_path=relative_path))
                    with open(
                        relative_path, "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        out_f.write(f.read())


def test_is_gitignored():
    """Test the is_gitignored function with some example files."""
    test_files = [
        ".venv/pyvenv.cfg",
        "schemas.py",
        ".gitignore",
        "non_existent_file.txt",
    ]

    for file in test_files:
        result = is_gitignored(file)
        status = "ignored" if result else "not ignored"
        print(f"File: {file} is {status}")


if __name__ == "__main__":
    # Call the function to write files to output.txt
    write_files_to_output("output.txt")

    # Test the is_gitignored function
    # test_is_gitignored()
