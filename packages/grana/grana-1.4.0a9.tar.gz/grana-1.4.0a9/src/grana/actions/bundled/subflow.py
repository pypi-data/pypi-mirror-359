# pylint: disable=invalid-field-call
"""Separate module for subflow action"""

import dataclasses
import typing as t
from collections.abc import Mapping, MutableMapping
from pathlib import Path

from ..base import ArgsBase, ActionBase
from ...display.types import DisplayEvent, DisplayEventName
from ...exceptions import ExecutionFailed
from ...rendering.containers import OutcomeDict

__all__ = [
    "make_subflow_runner_class_for_action",
    "SubflowAction",
]


class SubflowArgsByPath(ArgsBase):
    """Subflow arguments with the file path."""

    path: Path
    extra_context: dict[str, t.Any] = dataclasses.field(default_factory=dict)


class SubflowArgsBySpec(ArgsBase):
    """Subflow arguments with the spec."""

    actions: list[dict[str, t.Any]] = dataclasses.field(metadata={"rendering": "disabled"})
    context: dict[str, t.Any] = dataclasses.field(default_factory=dict, metadata={"rendering": "disabled"})
    configuration: dict[str, t.Any] = dataclasses.field(default_factory=dict, metadata={"rendering": "disabled"})
    extra_context: dict[str, t.Any] = dataclasses.field(default_factory=dict)


def make_subflow_runner_class_for_action(action: ActionBase) -> type:
    """Make a specialized subflow runner for the given action."""
    from ...runner import Runner

    def _resend_event_via_action(event: DisplayEvent) -> None:
        # These events shall not pass to the parent runner
        if event.name in (
            DisplayEventName.ON_RUNNER_FINISH,  # Triggers final status output
            DisplayEventName.ON_PLAN_INTERACTION,  # Pauses the execution
        ):
            event.future.set_result(None)  # Unlock the execution and continue
        else:
            # Pass modified event
            action._communicator.send_display_event(event)  # pylint: disable=protected-access

    class SubflowRunner(Runner):
        """A runner that intercepts and filters out events"""

        async def _process_display_events(self) -> None:
            while True:
                event: DisplayEvent = await self._events_flow.get()
                _resend_event_via_action(event)

        @classmethod
        def deep_update_context(cls, receiver: dict[str, t.Any], source: Mapping, path: str) -> dict[str, t.Any]:
            """Apply changes to the context"""
            for source_key, source_value in source.items():
                sub_path: str = f"{path}.{source_key}" if path else source_key
                if source_key not in receiver:
                    cls.logger.debug(f"Adding context: {sub_path}")
                    receiver[source_key] = source_value
                elif isinstance(source_value, Mapping) and isinstance(receiver[source_key], MutableMapping):
                    cls.logger.debug(f"Merging context: {sub_path}")
                    receiver[source_key] = cls.deep_update_context(receiver[source_key], source_value, sub_path)
                else:
                    cls.logger.debug(f"Rewriting context: {sub_path}")
                    receiver[source_key] = source_value
            return receiver

        async def run_async(self) -> None:
            try:
                return await super().run_async()
            finally:
                for sub_action in self.workflow.values():
                    action.yield_outcome(sub_action.name, OutcomeDict(sub_action.outcomes))

    return SubflowRunner


class SubflowAction(ActionBase):
    """Executes an independent workflow and passes the display events to the original runner."""

    args: t.Union[SubflowArgsByPath, SubflowArgsBySpec]

    async def run(self) -> None:
        from ...config.constants import C

        loop_runner_class = make_subflow_runner_class_for_action(self)

        # Cache [re]mount is required since the subflow may reconfigure some fields
        with C.mount_context_cache():
            source: t.Union[Path, dict]
            if isinstance(self.args, SubflowArgsByPath):
                source = self.args.path
            else:
                source = {
                    "actions": self.args.actions,
                    "context": self.args.context,
                    "configuration": self.args.configuration,
                }
            runner = loop_runner_class(source)
            # Update context with extras
            runner.workflow.context = runner.deep_update_context(
                receiver=runner.workflow.context,
                source=self.args.extra_context,
                path="",
            )
            try:
                await runner.run_async()
            except ExecutionFailed:
                self.fail()
