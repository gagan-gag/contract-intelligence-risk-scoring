"""Application configuration for local development.

Defines paths and helpers for local Chroma storage and other on-disk
artifacts. This module keeps settings minimal and filesystem-safe for
Day 1 development (no cloud keys needed).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Local settings for the backend and Chroma vector DB.

    Attributes:
        base_dir: Path pointing at the `backend/app` package directory.
        chroma_persist_dir: Path where Chroma will persist its local files.
    """

    base_dir: Path = Path(__file__).resolve().parent
    chroma_persist_dir: Path = base_dir.parent / "chroma_db"

    def ensure_dirs(self) -> None:
        """Ensure local directories exist for runtime.

        Call this during application startup to create the Chroma
        persistent directory (and any other local folders you add later).
        """
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)


# module-level settings instance for easy imports
settings = Settings()


def get_settings() -> Settings:
    """Return the shared settings instance.

    This helper is convenient for type checkers and future extension.
    """
    return settings
