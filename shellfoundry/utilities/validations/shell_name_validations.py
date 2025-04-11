from __future__ import annotations

import re
from typing import ClassVar


class ShellNameValidations:
    MAX_LENGTH_FOR_NAME: ClassVar[int] = 60
    NAME_REGEX: ClassVar[re.Pattern] = re.compile("^[a-zA-Z][A-Za-z0-9_ -]*$", re.U)

    def validate_shell_name(self, shell_name: str) -> bool:
        match = self.NAME_REGEX.match(shell_name)
        return len(shell_name) < self.MAX_LENGTH_FOR_NAME and match is not None
