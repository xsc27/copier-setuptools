"""Tests."""
import os
from pathlib import Path

import pre_commit.main
import pytest
import tox
from copier.main import Worker


def test_precommit(copier_project: Worker, tempdir: Path):
    """Run pre-commit in Copier project."""
    _ = copier_project
    os.chdir(tempdir)
    assert pre_commit.main.main(["validate-config"]) == 0
    assert pre_commit.main.main(["run", "--verbose", "--all-files"]) == 0


@pytest.mark.parametrize("test", ["lint", "py3", "pkg", "docs"])
def test_tox(copier_project: Worker, tempdir: Path, test: str):
    """Run tox in Copier project."""
    _ = copier_project
    assert tox.main(["-c", str(tempdir.joinpath("tox.ini")), "run", "-e", test]) == 0


if __name__ == "__main__":
    pytest.main([__file__])
