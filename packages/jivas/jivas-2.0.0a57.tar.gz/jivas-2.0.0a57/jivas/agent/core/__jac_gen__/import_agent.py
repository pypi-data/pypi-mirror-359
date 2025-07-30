from __future__ import annotations
from jaclang import *
import typing
from enum import Enum, auto
if typing.TYPE_CHECKING:
    import io
else:
    io, = jac_import('io', 'py')
if typing.TYPE_CHECKING:
    import os
else:
    os, = jac_import('os', 'py')
if typing.TYPE_CHECKING:
    import json
else:
    json, = jac_import('json', 'py')
if typing.TYPE_CHECKING:
    import yaml
else:
    yaml, = jac_import('yaml', 'py')
if typing.TYPE_CHECKING:
    import requests
else:
    requests, = jac_import('requests', 'py')
if typing.TYPE_CHECKING:
    import tarfile
else:
    tarfile, = jac_import('tarfile', 'py')
if typing.TYPE_CHECKING:
    import logging
else:
    logging, = jac_import('logging', 'py')
if typing.TYPE_CHECKING:
    import traceback
else:
    traceback, = jac_import('traceback', 'py')
if typing.TYPE_CHECKING:
    from typing import Union
else:
    Union, = jac_import('typing', 'py', items={'Union': None})
if typing.TYPE_CHECKING:
    from logging import Logger
else:
    Logger, = jac_import('logging', 'py', items={'Logger': None})
if typing.TYPE_CHECKING:
    from jivas.agent.modules.agentlib.utils import Utils
else:
    Utils, = jac_import('jivas.agent.modules.agentlib.utils', 'py', items={'Utils': None})
if typing.TYPE_CHECKING:
    from jvcli.api import RegistryAPI
else:
    RegistryAPI, = jac_import('jvcli.api', 'py', items={'RegistryAPI': None})
if typing.TYPE_CHECKING:
    from jvcli.utils import is_version_compatible
else:
    is_version_compatible, = jac_import('jvcli.utils', 'py', items={'is_version_compatible': None})
if typing.TYPE_CHECKING:
    from jivas.agent.core.app import App
else:
    App, = jac_import('jivas.agent.core.app', items={'App': None})
if typing.TYPE_CHECKING:
    from jivas.agent.core.agent import Agent
else:
    Agent, = jac_import('jivas.agent.core.agent', items={'Agent': None})
if typing.TYPE_CHECKING:
    from jivas.agent.core.agents import Agents
else:
    Agents, = jac_import('jivas.agent.core.agents', items={'Agents': None})
if typing.TYPE_CHECKING:
    from jivas.agent.memory.memory import Memory
else:
    Memory, = jac_import('jivas.agent.memory.memory', items={'Memory': None})
if typing.TYPE_CHECKING:
    from jivas.agent.action.action import Action
else:
    Action, = jac_import('jivas.agent.action.action', items={'Action': None})
if typing.TYPE_CHECKING:
    from jivas.agent.action.actions import Actions
else:
    Actions, = jac_import('jivas.agent.action.actions', items={'Actions': None})

class import_agent(Walker):
    logger: static[Logger] = logging.getLogger(__name__)
    descriptor: str = field('')
    daf_name: str = field('')
    daf_version: str = field('')
    jpr_api_key: str = field('')
    reporting: bool = field(True)

    class __specs__(Obj):
        private: static[bool] = False

    @with_entry
    def on_root(self, here: Root) -> None:
        if not self.visit(here.refs().filter(App, None)):
            self.logger.info('App node created')
            app_node = here.connect(App())
            self.visit(app_node)

    @with_entry
    def on_app(self, here: App) -> None:
        if not self.visit(here.refs().filter(Agents, None)):
            self.logger.info('Agents node created')
            agents_node = here.connect(Agents())
            self.visit(agents_node)

    @with_entry
    def on_agents(self, here: Agents) -> None:
        if self.descriptor:
            if (agent_node := self.import_from_descriptor(here, self.descriptor)):
                if self.reporting:
                    Jac.report(agent_node.export())
        elif self.daf_name:
            if (agent_node := self.import_from_daf(here, self.daf_name, self.daf_version, self.jpr_api_key)):
                if self.reporting:
                    Jac.report(agent_node.export())

    def get_daf_root(self) -> str:
        daf_root_path = os.environ.get('JIVAS_DAF_ROOT_PATH', 'daf')
        if not os.path.exists(daf_root_path):
            os.makedirs(daf_root_path)
        return daf_root_path

    def import_from_descriptor(self, agents_node: Agents, descriptor: Union[str, dict]) -> Agent:
        agent_data = {}
        agent_node = None
        if not descriptor:
            return None
        if isinstance(descriptor, str):
            try:
                agent_data = json.loads(descriptor)
            except json.JSONDecodeError:
                pass
            try:
                agent_data = yaml.safe_load(descriptor)
            except yaml.YAMLError:
                pass
        else:
            agent_data = descriptor
        if not agent_data:
            self.logger.error('no agent data available for import')
            return None
        if agent_data.get('id', None):
            try:
                agent_node = jobj(id=agent_data['id'])
            except Exception as e:
                self.logger.error(f'an exception occurred, {traceback.format_exc()}')
                return None
        else:
            agent_name = agent_data.get('name')
            if (_node := agents_node.get_by_name(agent_name)):
                agent_node = _node
            elif (agent_node := Agent(name=agent_name, description=agent_data.get('description', ''))):
                if not agents_node.get_by_id(agent_node.id):
                    agents_node.connect(agent_node)
                self.logger.info(f'agent created: {agent_node.name}')
            else:
                self.logger.error(f'unable to create agent: {agent_name}')
        if agent_node:
            descriptor_root = Utils.get_descriptor_root()
            agent_node.descriptor = f'{descriptor_root}/{agent_node.id}.yaml'
            agent_node.get_memory()
            agent_node.get_actions()
            if (agent_node := agent_node.update(data=agent_data, with_actions=True)):
                return agent_node
        return None

    def import_from_daf(self, agents_node: Agents, daf_name: str, version: Optional[str]='', jpr_api_key: Optional[str]='') -> Agent:
        agent_node = None
        safe_to_import = False
        daf_info = {}
        package_root = self.get_daf_root()
        namespace, package_name = daf_name.split('/')
        if (package_path := Utils.find_package_folder(package_root, daf_name)):
            info_yaml_path = os.path.join(package_path, 'info.yaml')
            if os.path.exists(info_yaml_path):
                with open(info_yaml_path, 'r') as file:
                    try:
                        daf_info = yaml.safe_load(file)
                        package_version = daf_info.get('package', {}).get('version', None)
                        if version:
                            if is_version_compatible(version, package_version):
                                safe_to_import = True
                        else:
                            safe_to_import = True
                    except yaml.YAMLError as e:
                        self.logger.error(f'an exception occurred, {traceback.format_exc()}')
        if not safe_to_import:
            if (package_data := RegistryAPI.download_package(daf_name, version, api_key=jpr_api_key)):
                try:
                    package_file = requests.get(package_data['file'])
                    target_dir = os.path.join(package_root, daf_name)
                    os.makedirs(target_dir, exist_ok=True)
                    with tarfile.open(fileobj=io.BytesIO(package_file.content), mode='r:gz') as tar_file:
                        tar_file.extractall(target_dir)
                    safe_to_import = True
                except Exception as e:
                    self.logger.error(f'an exception occurred, {traceback.format_exc()}')
        if safe_to_import and (package_path := Utils.find_package_folder(package_root, daf_name)):
            info_yaml_path = os.path.join(package_path, 'info.yaml')
            descriptor_yaml_path = os.path.join(package_path, 'descriptor.yaml')
            memory_yaml_path = os.path.join(package_path, 'memory.yaml')
            knowledge_yaml_path = os.path.join(package_path, 'knowledge.yaml')
            if os.path.exists(info_yaml_path):
                with open(info_yaml_path, 'r') as file:
                    try:
                        daf_info = yaml.safe_load(file)
                    except Exception as e:
                        self.logger.error(f'an exception occurred, {traceback.format_exc()}')
                        return None
            if os.path.exists(descriptor_yaml_path):
                with open(descriptor_yaml_path, 'r') as file:
                    try:
                        descriptor_data = yaml.safe_load(file)
                        if jpr_api_key:
                            descriptor_data['jpr_api_key'] = jpr_api_key
                        descriptor_data['meta'] = {'namespace': daf_info.get('package', {}).get('name'), 'version': daf_info.get('package', {}).get('version'), 'author': daf_info.get('package', {}).get('author'), 'dependencies': daf_info.get('package', {}).get('dependencies')}
                        agent_node = self.import_from_descriptor(agents_node, descriptor_data)
                    except Exception as e:
                        self.logger.error(f'an exception occurred, {traceback.format_exc()}')
                        return None
            if agent_node:
                if agent_node.healthcheck_status != 200:
                    self.logger.error(f'{agent_node.name} failed healthcheck. Any memory or knowledge queued for import will be deferred.')
                    return agent_node
            if agent_node and os.path.exists(memory_yaml_path):
                with open(memory_yaml_path, 'r') as file:
                    try:
                        _info = yaml.safe_load(file)
                        agent_node.get_memory().import_memory(data=_info)
                    except Exception as e:
                        self.logger.error(f'an exception occurred, {traceback.format_exc()}')
            if agent_node and os.path.exists(knowledge_yaml_path):
                with open(knowledge_yaml_path, 'r') as file:
                    try:
                        knode_yaml = file.read()
                        knode_yaml_data = yaml.safe_load(knode_yaml)
                        if (vector_store_action := agent_node.get_vector_store_action()):
                            if 'vec' in knode_yaml_data[0]:
                                vector_store_action.add_embeddings(knode_yaml)
                            else:
                                vector_store_action.import_knodes(knode_yaml)
                    except Exception as e:
                        self.logger.error(f'an exception occurred while importing agent knowledge, {traceback.format_exc()}')
        return agent_node