import subprocess
import os
import sys
from git import Repo
from dotdiff.diff_generator import run_pipeline

def get_changed_dot_files(repo_path, commit1="HEAD^", commit2="HEAD"):
    cmd = ["git", "-C", repo_path, "diff", "--name-only", f"{commit1}", f"{commit2}"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    files = result.stdout.strip().split('\n')
    return [f for f in files if f.endswith(".dot")]

def run_on_all_changed_dot_files(repo_path, output_dir="dot_diffs", commit1="HEAD^", commit2="HEAD"):
    changed_files = get_changed_dot_files(repo_path, commit1, commit2)

    if not changed_files or changed_files == ['']:
        print("[✓] No .dot files changed between commits.")
        return

    print(f"[i] Changed .dot files: {changed_files}")

    for path in changed_files:
        safe_name = path.replace("/", "_").replace("\\", "_")
        output_subdir = os.path.join(output_dir, safe_name)
        print(f"[→] Running diff for {path}")
        run_pipeline(repo_path, path, output_dir=output_subdir, commit_old=commit1, commit_new=commit2)

def main():
    if len(sys.argv) < 2:
        print("Usage: dotdiff-all <repo_path> [<commit1> <commit2>]")
        sys.exit(1)

    repo_path = sys.argv[1]
    commit1 = sys.argv[2] if len(sys.argv) > 2 else "HEAD^"
    commit2 = sys.argv[3] if len(sys.argv) > 3 else "HEAD"

    run_on_all_changed_dot_files(repo_path, commit1=commit1, commit2=commit2)
