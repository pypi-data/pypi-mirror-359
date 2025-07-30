from __future__ import annotations
from jaclang import *
import typing
from enum import Enum, auto
if typing.TYPE_CHECKING:
    from jivas.agent.core.agent import Agent
else:
    Agent, = jac_import('jivas.agent.core.agent', items={'Agent': None})
if typing.TYPE_CHECKING:
    from jivas.agent.memory.memory import Memory
else:
    Memory, = jac_import('jivas.agent.memory.memory', items={'Memory': None})
if typing.TYPE_CHECKING:
    from jivas.agent.memory.frame import Frame
else:
    Frame, = jac_import('jivas.agent.memory.frame', items={'Frame': None})
if typing.TYPE_CHECKING:
    from jivas.agent.core.agent_graph_walker import agent_graph_walker
else:
    agent_graph_walker, = jac_import('jivas.agent.core.agent_graph_walker', items={'agent_graph_walker': None})

class memory_frame_walker(agent_graph_walker, Walker):
    session_id: str = field('')

    @with_entry
    def on_agent(self, here: Agent) -> None:
        self.visit(here.refs().filter(Memory, None))

    @with_entry
    def on_memory(self, here: Memory) -> None:
        self.visit(here.refs().filter(Frame, None).filter(None, lambda item: item.session_id == self.session_id))