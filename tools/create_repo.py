import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def create_git_repo(repo_name, create_remote=False):
    path = Path(repo_name)
    path.mkdir(exist_ok=False)

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    # Initialize git in the new directory
    subprocess.run(["git", "init", path], check=True)

    (path / "README.md").write_text(f"# {repo_name}\n")
    (path / ".gitignore").write_text(".venv/\n.env\n__pycache__/\n.DS_Store\n")
    (path / ".env").write_text(f"GITHUB_TOKEN={token}\n")
    (path / "requirements.txt").write_text("")

    # Create virtual environment in the new directory
    subprocess.run(["python3.12", "-m", "venv", str(path / ".venv")], check=True)

    if create_remote:
        if not token:
            raise ValueError("GITHUB_TOKEN not found in .env")
        create_github_repo(repo_name)

        try:
            subprocess.run(["git", "-C", str(path), "remote", "add", "origin", f"git@github.com:K-Schubert/{repo_name}.git"], check=True)
        except subprocess.SubprocessError:
            print("Warning: Could not add remote origin. It might already exist.")

        # Stage initialized files
        subprocess.run(["git", "-C", str(path), "add", "README.md", ".gitignore", "requirements.txt"], check=True)

        # Create initial commit
        subprocess.run(["git", "-C", str(path), "commit", "-m", "First commit"], check=True)

        # Push to main branch
        subprocess.run(["git", "-C", str(path), "push", "-u", "origin", "main"], check=True)
        print(f"Initialized files committed and pushed to main branch")

    print(f"Repository {repo_name} created successfully.")

def create_github_repo(repo_name):

    # Use the GitHub CLI to create repo and add remote
    subprocess.run(["gh", "repo", "create", f"K-Schubert/{repo_name}", "--private", "--source", f"./{repo_name}"], check=True)
    print(f"Remote GitHub repository '{repo_name}' created.")


if __name__ == "__main__":
    repo_name = "auto-repo"
    create_remote = True
    create_git_repo(repo_name, create_remote)
