from __future__ import annotations
from jaclang import *
import typing
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

class purge(Walker):
    purge_spawn_node: bool = field(True)
    spawn_node: Node = field(None)
    logger: static[Logger] = logging.getLogger(__name__)

    class __specs__(Obj):
        private: static[bool] = True

    @with_entry
    def delete(self, here: Node) -> None:
        self.visit(here.refs())
        here.disconnect(here.refs())
        if not self.spawn_node:
            self.spawn_node = here
            if self.purge_spawn_node:
                self.logger.info(f'deleting node: {type(here).__name__}')
                Jac.destroy(here)
        else:
            self.logger.info(f'deleting node: {type(here).__name__}')
            Jac.destroy(here)