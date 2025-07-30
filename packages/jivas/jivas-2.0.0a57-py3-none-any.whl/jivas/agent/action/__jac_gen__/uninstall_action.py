from __future__ import annotations
from jaclang import *
import typing
from enum import Enum, auto
if typing.TYPE_CHECKING:
    import io
else:
    io, = jac_import('io', 'py')
if typing.TYPE_CHECKING:
    import yaml
else:
    yaml, = jac_import('yaml', 'py')
if typing.TYPE_CHECKING:
    import logging
else:
    logging, = jac_import('logging', 'py')
if typing.TYPE_CHECKING:
    import traceback
else:
    traceback, = jac_import('traceback', 'py')
if typing.TYPE_CHECKING:
    from logging import Logger
else:
    Logger, = jac_import('logging', 'py', items={'Logger': None})
if typing.TYPE_CHECKING:
    from jivas.agent.core.agent import Agent
else:
    Agent, = jac_import('jivas.agent.core.agent', items={'Agent': None})
if typing.TYPE_CHECKING:
    from jivas.agent.core.agent_graph_walker import agent_graph_walker
else:
    agent_graph_walker, = jac_import('jivas.agent.core.agent_graph_walker', items={'agent_graph_walker': None})

class uninstall_action(agent_graph_walker, Walker):
    package_name: str = field('')
    logger: static[Logger] = logging.getLogger(__name__)

    class __specs__(Obj):
        private: static[bool] = False

    @with_entry
    def on_agent(self, here: Agent) -> None:
        descriptor_data = here.get_descriptor()
        if not descriptor_data:
            message = 'unable to load descriptor data'
            self.logger.error(message)
            Jac.get_context().status = 500
            Jac.report(message)
            return False
        try:
            action_removed = False
            actions_node = here.get_actions()
            updated_actions = JacList([])
            for action in descriptor_data['actions']:
                if action.get('action') == self.package_name:
                    action_label = action.get('context', {}).get('label')
                    actions_node.deregister_action(action_label=action_label)
                    action_removed = True
                else:
                    updated_actions.append(action)
            if action_removed:
                descriptor_data['actions'] = updated_actions
            else:
                message = f'unable to find action for uninstall: {self.package_name} {self.version}'
                self.logger.error(message)
                Jac.get_context().status = 500
                Jac.report(message)
                return False
            if here.update(data=descriptor_data, with_actions=True):
                message = f'{self.package_name} {self.version} uninstalled successfully'
                self.logger.info(message)
                Jac.get_context().status = 200
                Jac.report(message)
                return True
            else:
                message = f'unable to update agent after uninstall of {self.package_name} {self.version}'
                self.logger.error(message)
                Jac.get_context().status = 500
                Jac.report(message)
                return False
        except Exception as e:
            message = f'unable to complete operation, {traceback.format_exc()}'
            self.logger.error(traceback.format_exc())
            Jac.get_context().status = 500
            Jac.report(message)
            return False