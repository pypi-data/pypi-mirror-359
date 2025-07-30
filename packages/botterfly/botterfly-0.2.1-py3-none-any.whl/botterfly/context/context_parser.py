import os
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from botterfly.context.vault_wrapper import VaultWrapper


class ContextParser:
    def __init__(self, template=None):
        self.vault = VaultWrapper()
        self.template = (
            template
            if template
            else Environment(
                loader=FileSystemLoader(Path(__file__).parent.parent.parent),
                undefined=StrictUndefined,
            )
        )

    def parse(self, file="context.yml") -> dict:
        context = self.template.get_template(file)
        rendered = context.render(
            env=os.environ,
            vault=self.vault,
        )

        return yaml.safe_load(rendered)
