from pathlib import Path

from botterfly.browser.action.action_registry import ActionRegistry
from botterfly.browser.remote_browser import RemoteBrowser
from botterfly.context.context_parser import ContextParser
from botterfly.context.template_renderer import TemplateRenderer
from botterfly.plan import Plan


class Bot:
    def __init__(
        self,
        template_renderer: TemplateRenderer,
        context_parser: ContextParser,
        remote_browser: RemoteBrowser,
        registry: ActionRegistry,
    ):
        self._template_renderer = template_renderer
        self._context_parser = context_parser
        self._remote_browser = remote_browser
        self._registry = registry

    async def execute(self, plan=None, context=None):
        # TODO: Improve the way plan and context are handle.
        # you should be able to use the default or any
        # plan and context
        # even a dict that respect the schema. context_parser and
        # template_render
        # should not handle default value. They should rely on a
        # config objet which handle that,
        # we should be able to pass a config ? or directly a
        # dictionary and the handling of the
        # parsing is done elsewhere ?
        context = (
            self._context_parser.parse(context)
            if context
            else self._context_parser.parse()
        )

        with Path.open(plan or "plan.yml", "r") as f:
            plan_template_str = f.read()

        executor = Plan(self._template_renderer, plan_template_str, context)
        result = {}

        try:
            await self._remote_browser.start()
            page = await self._remote_browser.open_new_page()

            for step, result in executor:
                action = self._registry.get(step["action"])
                await action.run(page=page, step=step, result=result)
        except Exception as e:
            print(e)
        finally:
            await self._remote_browser.stop()

        return result
