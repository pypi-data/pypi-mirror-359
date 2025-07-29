echo -e "--- mypy ---\n"
uvx mypy --exclude tools/ .
echo -e "\n--- pylint src ---"
uvx pylint src
echo -e "--- pylint tests ---"
PYTHONPATH=src uvx pylint tests
echo -e "--- ruff check ---\n"
uvx ruff check
echo -e "\n--- ruff format ---\n"
uvx ruff format
echo -e "\n--- ty check ---\n"
# --ignore unresolved-import
uvx ty check src tests
