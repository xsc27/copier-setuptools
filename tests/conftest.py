"""Pytest shared resources."""
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pytest
from copier.main import Worker
from pluggy._result import _Result
from pytest import CallInfo, CollectReport, FixtureRequest, Item, StashKey

DATA = {
    "email": "pytest@example.com",
    "full_name": "Copier Template",
    "github_username": "Test",
    "project_name": "Copier Template Test",
    "project_short_description": "A test of a Copier template.",
    "template": "python",
}
LOCAL_OUTDIR = "COPIER_OUT"
PHASE_REPORT_KEY = StashKey[dict[str, CollectReport]]()
_LOGGER = logging.getLogger("runtime")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
    """Report test phase results."""
    outcome: _Result = yield
    rep = outcome.get_result()
    item.stash.setdefault(PHASE_REPORT_KEY, {})[rep.when] = rep


@pytest.fixture(scope="session")
def tempdir(request: FixtureRequest) -> Iterable[Path]:
    """Generate temporary directory and cleanup."""
    outdir_base = None
    reuse_dir = os.getenv("REUSE_OUTDIR") or ""
    if reuse_dir or not os.getenvb(b"CI"):
        outdir_base = Path().cwd().parent.joinpath(LOCAL_OUTDIR).joinpath(reuse_dir)
        outdir_base.mkdir(parents=True, exist_ok=True)

    if reuse_dir and outdir_base:
        tmp = outdir_base
    else:
        tmp = tempfile.mkdtemp(prefix=f"{datetime.now().timestamp()}-", dir=outdir_base)

    yield Path(tmp)

    # Teardown only on "passed"
    report = request.node.stash[PHASE_REPORT_KEY]
    if not any(hasattr(report.get(phase), "failed") for phase in ["setup", "call"]):
        shutil.rmtree(tmp)
    else:
        _LOGGER.info("OUTPUT DIR for %s, %s", request.node.nodeid, tmp)


@pytest.fixture(scope="session")
def copier_project(tempdir: Path):
    copier = Worker(
        src_path=str(Path.cwd()),
        dst_path=tempdir,
        cleanup_on_error=False,
        defaults=True,
        user_defaults=DATA,
        overwrite=True,
        # pretend=True,
    )
    copier.run_auto()
    return copier
