import json
import os
from datetime import datetime
from typing import List, Literal

from git import Commit as GitCommit
from git import GitCommandError, InvalidGitRepositoryError
from git.repo import Repo

from ..common import json_dump, json_dumps, logger
from .item import TodoItem
from .result import ActionResult, Commit, HistoryResult, SwitchResult


class HistoryError(Exception):
    pass


class UndoRedoError(HistoryError):
    """An exception raised when an undo or redo operation fails."""


class CommitError(HistoryError):
    """An exception raised when a commit operation fails."""


_MAIN_FILE = "main"


def _repo(path: str, create: bool = False) -> Repo:
    try:
        return Repo(path)
    except InvalidGitRepositoryError as e:
        if not create:
            raise e
    os.makedirs(path, exist_ok=True)
    return Repo.init(path)


def load(path: str) -> List[TodoItem]:
    main_file = os.path.join(path, _MAIN_FILE)
    if not os.path.exists(main_file):
        return []
    with open(main_file, "r") as f:
        return [TodoItem.from_dict(todo) for todo in json.load(f)]


def to_commit(commit: GitCommit) -> Commit:
    message, _, *data = str(commit.message).split("\n")
    data = "\n".join(data)
    try:
        data = json.loads(data)
        action_results = [ActionResult.from_dict(d) for d in data]
    except Exception:
        logger.warn(f"Failed to parse commit data: {repr(data)}")
        action_results = []
    return Commit(
        message,
        commit.hexsha,
        commit.committed_datetime,
        commit.hexsha == commit.repo.head.commit.hexsha,
        action_results,
    )


def checkout(path: str, commit_hash: str) -> Commit:
    repo = _repo(path)
    c = repo.head.commit
    repo.git.checkout(commit_hash)
    logger.debug(f"Checked out commit {commit_hash} in {path}")
    return to_commit(c)


def _undo_redo(path: str, action: Literal["undo", "redo"]) -> SwitchResult:
    """Restore the previous version from git history."""
    repo = _repo(path)
    commits = list(repo.iter_commits("main"))
    before = repo.head.commit
    index = commits.index(before)
    if action == "undo":
        if index + 1 >= len(commits):
            raise UndoRedoError("No history to undo.")
        index += 1
        action_results = to_commit(before).action_results
        message = str(before.message)
    elif action == "redo":
        if index == 0:
            raise UndoRedoError("No history to redo.")
        index -= 1
        action_results = to_commit(commits[index]).action_results
        message = str(commits[index].message)
    else:
        raise ValueError(f"Unknown action: {action}")
    checkout(path, commits[index].hexsha)
    message = message.split("\n", 1)[0]
    result = SwitchResult(action, message, action_results)
    logger.debug(f"{action.capitalize()} result: {result}")
    return result


def undo(path: str) -> SwitchResult:
    return _undo_redo(path, "undo")


def redo(path: str) -> SwitchResult:
    return _undo_redo(path, "redo")


def history(path: str) -> HistoryResult:
    return HistoryResult(
        [to_commit(c) for c in _repo(path).iter_commits("main")]
    )


def save(
    commit_message: str,
    todos: List[TodoItem],
    action_results: List[ActionResult],
    path: str,
    backup: bool = True,
    indent: int = 2,
):
    """
    Save the list of TODOs to a file using git for version control.
    Commits changes if backup is enabled and we're at HEAD.
    """
    logger.debug(
        f"Saving todos to {path} with commit message: {commit_message}"
    )
    main_file = os.path.join(path, _MAIN_FILE)
    with open(main_file, "w") as f:
        data = [todo.to_dict() for todo in todos if not todo.status == "delete"]
        json_dump(data, f, indent=indent)
    if not backup:
        return
    repo = _repo(path, create=True)
    if repo.head.is_detached:
        backup_branch = f"backup-{datetime.now():%Y-%m-%d-%H-%M-%S}"
        repo.git.branch("-m", "main", backup_branch)
        repo.git.checkout("-b", "main")
    try:
        repo.index.add(_MAIN_FILE)
        if not repo.is_dirty():
            return
        result = json_dumps(
            [ar.to_dict() for ar in action_results], indent=indent
        )
        repo.index.commit(commit_message + "\n\n" + result)
    except GitCommandError as e:
        raise CommitError(f"Failed to commit changes: {e}")
