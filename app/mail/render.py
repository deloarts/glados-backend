"""
    Mail body render submodule.
"""

from pathlib import Path

import jinja2


def render_template(template_file: Path, **kwargs) -> str:
    """Renders a Jinja template into HTML.

    Args:
        template_file (Path): The j2 template file to use.
        kwargs: The keyword arguments to pass to the template.

    Raises:
        FileNotFoundError: Raised if the template file doesn't exist.

    Returns:
        str: The rendered html template as string.
    """
    if not template_file.exists():
        raise FileNotFoundError(f"Template not found at: {str(template_file)!r}.")
    template_loader = jinja2.FileSystemLoader(searchpath="/")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(str(template_file))
    return template.render(**kwargs)
