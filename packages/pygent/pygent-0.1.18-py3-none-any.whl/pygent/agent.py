"""Orchestration layer: receives messages, calls the OpenAI-compatible backend and dispatches tools."""

import json
import os
import pathlib
import uuid
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from .runtime import Runtime
from . import tools
from .models import Model, OpenAIModel
from .persona import Persona

DEFAULT_PERSONA = Persona(
    os.getenv("PYGENT_PERSONA_NAME", "Pygent"),
    os.getenv("PYGENT_PERSONA", "a sandboxed coding assistant."),
)

def build_system_msg(persona: Persona) -> str:
    return (
        f"You are {persona.name}. {persona.description}\n"
        "Respond with JSON when you need to use a tool."
        "If you need to stop or finished you task, call the `stop` tool.\n"
        "You can use the following tools:\n"
        f"{json.dumps(tools.TOOL_SCHEMAS, indent=2)}\n"
        "You can also use the `continue` tool to request user input or continue the conversation.\n"
    )

DEFAULT_MODEL = os.getenv("PYGENT_MODEL", "gpt-4.1-mini")
SYSTEM_MSG = build_system_msg(DEFAULT_PERSONA)

console = Console()




@dataclass
class Agent:
    runtime: Runtime = field(default_factory=Runtime)
    model: Model = field(default_factory=OpenAIModel)
    model_name: str = DEFAULT_MODEL
    persona: Persona = field(default_factory=lambda: DEFAULT_PERSONA)
    system_msg: str = field(default_factory=lambda: build_system_msg(DEFAULT_PERSONA))
    history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.system_msg:
            self.system_msg = build_system_msg(self.persona)
        if not self.history:
            self.history.append({"role": "system", "content": self.system_msg})

    def step(self, user_msg: str):
        """Execute one round of interaction with the model."""

        self.history.append({"role": "user", "content": user_msg})

        assistant_msg = self.model.chat(
            self.history, self.model_name, tools.TOOL_SCHEMAS
        )
        self.history.append(assistant_msg)

        if assistant_msg.tool_calls:
            for call in assistant_msg.tool_calls:
                output = tools.execute_tool(call, self.runtime)
                self.history.append({"role": "tool", "content": output, "tool_call_id": call.id})
                console.print(Panel(output, title=f"tool:{call.function.name}"))
        else:
            markdown_response = Markdown(assistant_msg.content)
            console.print(Panel(markdown_response, title="Resposta do Agente", title_align="left", border_style="cyan"))
        return assistant_msg

    def run_until_stop(
        self,
        user_msg: str,
        max_steps: int = 20,
        step_timeout: float | None = None,
        max_time: float | None = None,
    ) -> None:
        """Run steps until ``stop`` is called or limits are reached."""

        if step_timeout is None:
            env = os.getenv("PYGENT_STEP_TIMEOUT")
            step_timeout = float(env) if env else None
        if max_time is None:
            env = os.getenv("PYGENT_TASK_TIMEOUT")
            max_time = float(env) if env else None

        msg = user_msg
        start = time.monotonic()
        self._timed_out = False
        for _ in range(max_steps):
            if max_time is not None and time.monotonic() - start > max_time:
                self.history.append({"role": "system", "content": f"[timeout after {max_time}s]"})
                self._timed_out = True
                break
            step_start = time.monotonic()
            assistant_msg = self.step(msg)
            if step_timeout is not None and time.monotonic() - step_start > step_timeout:
                self.history.append({"role": "system", "content": f"[timeout after {step_timeout}s]"})
                self._timed_out = True
                break
            calls = assistant_msg.tool_calls or []
            if any(c.function.name in ("stop", "continue") for c in calls):
                break
            msg = "continue"


def run_interactive(use_docker: bool | None = None) -> None:  # pragma: no cover
    agent = Agent(runtime=Runtime(use_docker=use_docker))
    console.print("[bold green]Pygent[/] iniciado. (digite /exit para sair)")
    try:
        while True:
            user_msg = console.input("[cyan]user> [/]" )
            if user_msg.strip() in {"/exit", "quit", "q"}:
                break
            agent.run_until_stop(user_msg)
    finally:
        agent.runtime.cleanup()
