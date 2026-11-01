"""Commit data only. On conflict fail visibly; never force-push or discard history."""
import subprocess
from pathlib import Path


def git(*args, check=True):
    return subprocess.run(["git", *args], check=check)


if __name__ == "__main__":
    files = [str(p) for p in (Path("data/store.json"), Path("data/price_history.csv")) if p.exists()]
    if files:
        git("config", "user.name", "github-actions[bot]")
        git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
        git("add", "--", *files)
        changed = git("diff", "--cached", "--quiet", "--", *files, check=False).returncode
        if changed not in (0, 1):
            raise SystemExit(changed)
        if changed:
            git("commit", "--only", "-m", "Save OMTech observation and delivery state [skip ci]", "--", *files)
            # A concurrent README/config edit may advance the branch. Rebase only
            # if Git can do so without conflicts; a conflict needs human review.
            branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
            if not branch:
                raise SystemExit("Detached HEAD; refusing to save data.")
            for attempt in range(3):
                if git("push", "origin", f"HEAD:refs/heads/{branch}", check=False).returncode == 0:
                    break
                git("fetch", "origin", branch)
                git("rebase", f"origin/{branch}")
            else:
                raise SystemExit("Cannot persist data after 3 pushes. Recover the failure artifact.")
