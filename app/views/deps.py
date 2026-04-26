import re
from typing import Annotated

from fastapi import Header

CLI_USER_AGENT_PATTERN = re.compile(r"\b(?:curl|httpie|wget)/[^\s]+\b", re.IGNORECASE)


def is_cli_client(user_agent: Annotated[str | None, Header()]) -> bool:
    if not user_agent:
        return False
    return bool(CLI_USER_AGENT_PATTERN.search(user_agent))
