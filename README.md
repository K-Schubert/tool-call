# tool-call

Run a local lighweight LLM for tool call using `mlx_lm`.

# Tools

Nots:
- test if performing file operations (eg. mv, cp, etc.) is doable by writing bash scripts and executing (provide context of cwd, listdir, repo structure, etc.)
- test with semantic search of available code operation scripts as context to the tool call LLM to write tool call
- test only with available tools

### File operations
1. `create_file`: create a file
2. `edit_file`: edit a file
3. `delete_file`: delete a file
4. `rename_file`: rename a file

### Repo operations
5. `create_repo`: initialize a git repo
    - initialize a local git repo with `README.md`, `.venv`, `.env`, `.gitignore`, `requirements.txt`.
    - create remote and `commit_and_push_to_remote` on main branch.
6. `commit_and_push_to_remote`: commit and push to a remote repository
    - commit seleted files and push to remote selected branch.

### Search operations
7. `search_web`: performs a web search and inspects content of individual links
    - search results with lib?
    - use pyppeteer/selenium to load and scrape top N page content.
    - use LLM to process results.

### Code operations
8. `write_code`: writes a script.

9. `execute_code`: executes a script.

### Research operations
