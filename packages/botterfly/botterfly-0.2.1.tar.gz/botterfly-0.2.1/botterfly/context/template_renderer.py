from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent.parent.parent)
        )

    def render(self, context: dict, file: str = None, template_str: str = None):
        if file:
            template = self.env.get_template(file)
        elif template_str:
            template = self.env.from_string(template_str)
        else:
            raise ValueError("Must provide either file or template_str")

        return yaml.safe_load(template.render(**context))
