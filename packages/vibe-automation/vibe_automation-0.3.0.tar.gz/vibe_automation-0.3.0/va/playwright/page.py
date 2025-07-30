import logging
import atexit
from typing import Any, Dict, Optional

from playwright.sync_api import Locator
from stagehand import StagehandPage

from .locator import PromptBasedLocator
from .step import print_pending_modifications, AsyncStepContextManager, execute_step
from ..agent.agent import Agent

log = logging.getLogger("va.playwright")


# Register the cleanup function to run at exit
atexit.register(print_pending_modifications)


class Page:
    def __init__(self, page: StagehandPage):
        self._stagehand_page = page
        self._agent = Agent()

    def get_by_prompt(
        self,
        prompt: str,
    ) -> PromptBasedLocator:
        """
        Returns a PromptBasedLocator that can be used with or without fallback locators

        Parameters:
        -----------
        prompt (str): The natural language description of the element to locate.
        timeout (int) (optional): Timeout value in seconds for the connection with backend API service.
        wait_for_network_idle (bool) (optional): Whether to wait for network reaching full idle state before querying the page. If set to `False`, this method will only check for whether page has emitted [`load` event](https://developer.mozilla.org/en-US/docs/Web/API/Window/load_event).
        include_hidden (bool) (optional): Whether to include hidden elements on the page. Defaults to `True`.
        mode (ResponseMode) (optional): The response mode. Can be either `standard` or `fast`. Defaults to `fast`.
        experimental_query_elements_enabled (bool) (optional): Whether to use the experimental implementation of the query elements feature. Defaults to `False`.

        Returns:
        --------
        PromptBasedLocator: A locator that uses prompt-based element finding
        """
        return PromptBasedLocator(self, prompt)

    async def get_locator_by_prompt(
        self,
        prompt: str,
    ) -> Locator | None:
        """
        Internal method to get element by prompt - used by PromptBasedLocator

        Returns:
        --------
        Playwright [Locator](https://playwright.dev/python/docs/api/class-locator) | None: The found element or `None` if no matching elements were found.
        """

        results = await self._stagehand_page.observe(prompt)

        if not results:
            return None

        selector = results[0].selector
        return self._stagehand_page.locator(selector)

    def step(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> AsyncStepContextManager:
        """
        Execute a natural language command by generating and running Python code.

        This method returns a context manager that can be used with 'async with'.
        The LLM action generation is only triggered if the with block is empty (contains only pass).

        Parameters:
        -----------
        command (str): Natural language description of the action to perform
        context (Dict[str, Any], optional): Context variables available to the generated script
        max_retries (int): Maximum number of retry attempts. Defaults to 3.

        Returns:
        --------
        AsyncStepContextManager: Context manager for the step execution
        """
        if context is None:
            context = {}
        return AsyncStepContextManager(self, command, context, max_retries, self._agent)

    async def _execute_step(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Internal method to execute a natural language command.
        Now delegates to the pure function in step.py.
        """
        return await execute_step(
            command=command,
            context=context,
            max_retries=max_retries,
            page=self._stagehand_page,
            agent=self._agent,
        )

    def __getattr__(self, name):
        """Forward attribute lookups to the underlying Stagehand page."""
        return getattr(self._stagehand_page, name)
