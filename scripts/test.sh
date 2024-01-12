#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
/opt/homebrew/bin/pytest --instafail --browser firefox --headed --base-url http://localhost "$parent_path/tests"