import warnings
from jupyter_server.services.contents.largefilemanager import AsyncLargeFileManager
from .checkpoints import AsyncMultiCheckpoints
def _jupyter_server_extension_points():
    return [{"module": "jupytercheckpoints.extension"}]

def _load_jupyter_server_extension(serverapp):

    if not isinstance(serverapp.contents_manager, AsyncLargeFileManager):
        warnings.warn("contents_manager must be AsyncLargeFileManager")
        return

    serverapp.contents_manager.checkpoints_class = AsyncMultiCheckpoints
    serverapp.log.info("Successfully load jupytercheckpoints extension")
