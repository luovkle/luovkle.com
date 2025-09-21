import re
from typing import Any, Literal

from jinja2 import Template

CLI_USER_AGENT_PATTERN = re.compile(r"\b(?:curl|httpie|wget)/[^\s]+\b", re.IGNORECASE)

POST_ANSI_TEMPLATE = """
{{ header }}

\033[1;97m{{ title }}\033[0m

\033[90m{{ reading_time }}\t{{ date }}\033[0m

{{ content }}\n
"""

PROJECT_ANSI_TEMPLATE = """
{{ header }}

\033[1;97m{{ title }}\033[0m

\033[90m{{ reading_time }}\t{{ date }}\033[0m

{{ content }}

{% if repository %}\033[1;97mRepository:\033[0m {{ repository }}{% endif %}

{% if website %}\033[1;97mWebsite:\033[0m {{ website }}{% endif %}\n
"""

ANSITemplateName = Literal["post_template", "project_template"]


def is_cli_user_agent(headers: str) -> bool:
    return bool(CLI_USER_AGENT_PATTERN.search(headers))


def render_ansi_template(template_name: ANSITemplateName, **context: Any):
    if template_name == "post_template":
        template = Template(POST_ANSI_TEMPLATE)
    elif template_name == "project_template":
        template = Template(PROJECT_ANSI_TEMPLATE)
    return template.render(**context)
