"""Custom version provider for commitizen."""

import re
from pathlib import Path
from typing import final, override

from commitizen.config.base_config import BaseConfig
from commitizen.providers.base_provider import VersionProvider


@final
class AboutPyProvider(VersionProvider):
    """Get version from __about__.py, in the variable __version__."""

    def __init__(self, config: BaseConfig):
        """Initialize provider with the appropriate attributes."""
        super().__init__(config)
        del config
        self.file_path = Path("src") / "kajihs_utils" / "__about__.py"
        self.version_regex = re.compile(r'^__version__\s*=\s*[\'"]([^\'"]+)[\'"]', re.MULTILINE)

    @override
    def get_version(self) -> str:
        content = self.file_path.read_text()
        match = self.version_regex.search(content)
        if not match:
            msg = f"Version not found in {self.file_path}"
            raise ValueError(msg)
        return match.group(1)

    @override
    def set_version(self, version: str) -> None:
        content = self.file_path.read_text()
        new_content = self.version_regex.sub(f'__version__ = "{version}"', content)
        _ = self.file_path.write_text(new_content)
