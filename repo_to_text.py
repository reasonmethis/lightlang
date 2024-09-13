import os
import subprocess

OUTPUT_FILE = "repo-to-text-output.txt"
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


def is_ignored(path: str) -> bool:
    """Check if a file or directory is ignored."""
    if path in IGNORE_FILES or path in IGNORE_DIRS:
        return True
    if any(
        path.startswith(f"{dir}/") or path.startswith(f"{dir}\\") for dir in IGNORE_DIRS
    ):
        return True
    return is_gitignored(path)


def export_repo(output_file):
    """Write the contents of all non-ignored files to the output file."""
    with open(output_file, encoding="utf-8", mode="w") as out_f:
        for root, dirs, files in os.walk("."):
            if is_ignored(relative_root := os.path.relpath(root)):
                continue
            print(f"Processing {relative_root}".ljust(76, "."), end="")
            for file in files:
                relative_path = os.path.join(relative_root, file)
                if not is_ignored(relative_path):
                    with open(
                        relative_path, "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        header = file_path_header.format(relative_path=relative_path)
                        out_f.write(header + f.read())
            print("DONE")


def test_is_gitignored():
    """Test the is_gitignored function with some example files."""
    test_files = [
        ".git",
        ".git\objects\c2",
        ".venv",
        "schemas.py",
        ".gitignore",
        "non_existent_file.txt",
    ]

    for file in test_files:
        result = is_gitignored(file)
        status = "ignored" if result else "not ignored"
        print(f"File: {file} is {status}")


if __name__ == "__main__":
    # Call the function to write files to the output file
    export_repo(OUTPUT_FILE)

    # Test the is_gitignored function
    # test_is_gitignored()
