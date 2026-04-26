from typing import Any, Literal

from jinja2 import Template

POST_ANSI_TEMPLATE = """
{{ post.header }}

\033[1;97m{{ post.title }}\033[0m

\033[90m{{ author.full_name }}\033[0m

\033[90m{{ post.reading_time }}\t{{ post.publish_date }}\033[0m

{{ post.body }}\n
"""

PROJECT_ANSI_TEMPLATE = """
{{ project.header }}

\033[1;97m{{ project.title }}\033[0m

\033[90m{{ author.full_name }}\033[0m

\033[90m{{ project.reading_time }}\t{{ project.publish_date }}\033[0m

{{ project.body }}

{% if project.repository %}\033[1;97mRepository:\033[0m {{ project.repository }}{% endif %}

{% if project.website %}\033[1;97mWebsite:\033[0m {{ project.website }}{% endif %}\n
"""  # noqa: E501

ANSITemplateName = Literal["post_template", "project_template"]


def render_ansi_template(template_name: ANSITemplateName, context: dict[str, Any]):
    if template_name == "post_template":
        template = Template(POST_ANSI_TEMPLATE)
    elif template_name == "project_template":
        template = Template(PROJECT_ANSI_TEMPLATE)
    return template.render(**context)
