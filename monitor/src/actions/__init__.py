from monitor.src.actions.digest import append_to_digest
from monitor.src.actions.pull_request import create_pull_request


ACTIONS = {
    "digest": append_to_digest,
    "pr": create_pull_request,
}
