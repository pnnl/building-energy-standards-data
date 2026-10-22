"""Locate, and if necessary build, the SQLite database used by the MCP server.

The database is not shipped with the package (``*.db`` is gitignored). It is built
from the packaged JSON files on first use and cached, so the server works from any
working directory and from an installed wheel.
"""

import logging
import os
import sqlite3
import tempfile
from importlib import metadata
from pathlib import Path
from typing import Optional

from building_energy_standards_data.applications.database_maintenance import (
    create_database,
)

logger = logging.getLogger(__name__)

DB_PATH_ENV = "BESD_DB_PATH"
PACKAGE_NAME = "building-energy-standards-data"


def _package_version() -> str:
    try:
        return metadata.version(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return "dev"


def default_db_path() -> Path:
    """``$BESD_DB_PATH`` if set, otherwise a per-version file in the user cache."""
    override = os.getenv(DB_PATH_ENV)
    if override:
        return Path(override).expanduser()
    cache_home = Path(os.getenv("XDG_CACHE_HOME") or Path.home() / ".cache")
    return (
        cache_home
        / "building_energy_standards_data"
        / f"openstudio_standards_{_package_version()}.db"
    )


def ensure_database(
    db_path: Optional[os.PathLike] = None, rebuild: bool = False
) -> Path:
    """Return the path to the database, building it from the packaged JSON if missing.

    Args:
        db_path: Database file. Defaults to :func:`default_db_path`.
        rebuild: Rebuild even if the file exists (e.g. after editing the JSON data).
    """
    path = Path(db_path).expanduser() if db_path else default_db_path()
    if path.exists() and not rebuild:
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Building database at %s", path)

    # Build into a temp file and rename, so an interrupted build never leaves a
    # partial database that later runs would treat as complete.
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".db.tmp")
    os.close(fd)
    try:
        conn = sqlite3.connect(tmp_name)
        try:
            create_database(conn)
        finally:
            conn.close()
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    return path
