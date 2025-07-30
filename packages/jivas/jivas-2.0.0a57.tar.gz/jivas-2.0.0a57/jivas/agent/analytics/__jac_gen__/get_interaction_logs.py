from __future__ import annotations
from jaclang import *
import typing
from enum import Enum, auto
if typing.TYPE_CHECKING:
    import os
else:
    os, = jac_import('os', 'py')
if typing.TYPE_CHECKING:
    import logging
else:
    logging, = jac_import('logging', 'py')
if typing.TYPE_CHECKING:
    import traceback
else:
    traceback, = jac_import('traceback', 'py')
if typing.TYPE_CHECKING:
    import json
else:
    json, = jac_import('json', 'py')
if typing.TYPE_CHECKING:
    from logging import Logger
else:
    Logger, = jac_import('logging', 'py', items={'Logger': None})
if typing.TYPE_CHECKING:
    from datetime import datetime, timedelta
else:
    datetime, timedelta = jac_import('datetime', 'py', items={'datetime': None, 'timedelta': None})
if typing.TYPE_CHECKING:
    from jivas.agent.core.agent_graph_walker import agent_graph_walker
else:
    agent_graph_walker, = jac_import('jivas.agent.core.agent_graph_walker', items={'agent_graph_walker': None})
if typing.TYPE_CHECKING:
    from jivas.agent.core.agent import Agent
else:
    Agent, = jac_import('jivas.agent.core.agent', items={'Agent': None})
if typing.TYPE_CHECKING:
    from jac_cloud.core.architype import NodeAnchor
else:
    NodeAnchor, = jac_import('jac_cloud.core.architype', 'py', items={'NodeAnchor': None})

class get_interaction_logs(agent_graph_walker, Walker):
    start_date: str = field('')
    end_date: str = field('')
    session_id: str = field('')
    channel: str = field('')
    timezone: str = field('UTC')
    logger: static[Logger] = logging.getLogger(__name__)

    class __specs__(Obj):
        private: static[bool] = False

    @with_entry
    def on_agent(self, here: Agent) -> None:
        try:
            start = datetime.strptime(f'{self.start_date}T00:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z')
            end = datetime.strptime(f'{self.end_date}T00:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z')
            end = end + timedelta(days=1) - timedelta(milliseconds=1)
            collection = NodeAnchor.Collection.get_collection('interactions')
            match_criteria = {'agent_id': self.agent_id, 'time_stamp': {'$gte': start.isoformat(), '$lte': end.isoformat()}}
            if self.session_id:
                match_criteria['session_id'] = self.session_id
            if self.channel:
                match_criteria['channel'] = self.channel
            pipeline = JacList([{'$match': match_criteria}, {'$sort': {'time_stamp': 1}}])
            result = list(collection.aggregate(pipeline))
            Jac.report({'total': len(result), 'data': json.loads(json.dumps(result, default=str))})
        except Exception as e:
            self.logger.error(f'An error occurred while fetching interaction logs: {traceback.format_exc()}')
            Jac.report({'error': str(e)})