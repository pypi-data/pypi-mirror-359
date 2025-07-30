"""Hatch build hook to bring dynamic metadata."""

import importlib.util
import sys
from pathlib import Path
from typing import Any, override

from hatchling.metadata.plugin.interface import MetadataHookInterface


class AboutMetadataHookOld(MetadataHookInterface):
    """Hatchling metadata hook that loads dynamic metadata from the `__about__.py` file."""

    @override
    def update(self, metadata: dict[str, Any]) -> None:
        """
        Update the metadata dictionary with values from the `__about__.py` file.

        Args:
            metadata: The dictionary containing the project metadata.

        Raises:
            ImportError: Metadata loading failed
        """
        # Dynamically load __about__.py
        about_path = Path(self.root) / "src" / "kajihs_utils" / "__about__.py"
        spec = importlib.util.spec_from_file_location("__about__", about_path)
        if spec is None or spec.loader is None:
            msg = f"Could not load metadata from {about_path}"
            raise ImportError(msg)

        about = importlib.util.module_from_spec(spec)
        sys.modules["__about__"] = about
        spec.loader.exec_module(about)

        # Map __about__ attributes to metadata fields
        authors: list[str] = about.__authors__
        emails: list[str] = about.__author_emails__
        metadata["authors"] = [
            {"name": name, "email": email} for name, email in zip(authors, emails, strict=True)
        ]
        metadata["urls"] = {
            "Repository": about.__repo_url__,
            "Homepage": about.__homepage_url__,
            "Issues": about.__issues_url__,
            "Changelog": about.__changelog_url__,
            "Documentation": about.__documentation_url__,
        }
