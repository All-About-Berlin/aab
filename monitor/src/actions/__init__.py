from actions.digest import append_to_digest
from actions.pull_request import create_pull_request


ACTIONS = {
    "digest": append_to_digest,
    "pr": create_pull_request,
}
