#  SPDX-FileCopyrightText: Copyright (c) 2020 Atalaya Tech. Inc
#  SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#  SPDX-License-Identifier: Apache-2.0
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#  http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  Modifications Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES

from __future__ import annotations

import collections
import contextlib
import json
import logging
import os
import pathlib
import socket
from typing import Any, DefaultDict, Dict, Iterator, Protocol, TextIO, Union

import typer
import yaml
from rich.console import Console

from dynamo.planner.defaults import PlannerDefaults  # type: ignore[attr-defined]
from dynamo.runtime.logging import configure_dynamo_logging
from dynamo.sdk.core.protocol.interface import ComponentType
from dynamo.sdk.core.runner import TargetEnum

configure_dynamo_logging()

logger = logging.getLogger(__name__)
console = Console()

DYN_LOCAL_STATE_DIR = "DYN_LOCAL_STATE_DIR"
PLANNER_SERVICE_NAME = "Planner"


# Define a Protocol for services to ensure type safety
class ServiceProtocol(Protocol):
    name: str
    inner: Any
    models: list[Any]
    dynamo: Any

    def is_dynamo_component(self) -> bool:
        ...

    def dynamo_address(self) -> tuple[str, str]:
        ...


class PortReserver:
    def __init__(self, host: str = "localhost"):
        self.host = host
        self.socket: socket.socket | None = None
        self.port: int | None = None

    def __enter__(self) -> int:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host, 0))
            _, self.port = self.socket.getsockname()
            return self.port
        except socket.error as e:
            self.close_socket()
            logger.warning(f"Failed to reserve port on {self.host}: {str(e)}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_socket()

    def close_socket(self):
        try:
            if self.socket:
                self.socket.close()
        except socket.error as e:
            logger.warning(f"Error while closing socket: {str(e)}")
            # Don't re-raise the exception as this is cleanup code
            return True


@contextlib.contextmanager
def reserve_free_port(
    host: str = "localhost",
) -> Iterator[int]:
    """
    Detect free port and reserve until exit the context.
    Returns a context manager that yields the reserved port.
    """
    with PortReserver(host) as port:
        yield port


def save_dynamo_state(
    namespace: str,
    circus_endpoint: str,
    components: dict[str, Any],
    environment: dict[str, Any],
):
    state_dir = os.environ.get(
        DYN_LOCAL_STATE_DIR, os.path.expanduser("~/.dynamo/state")
    )
    os.makedirs(state_dir, exist_ok=True)

    # create the state object
    state = {
        "namespace": namespace,
        "circus_endpoint": circus_endpoint,
        "components": components,
        "environment": environment,
    }

    # save the state object to a file
    state_file = os.path.join(state_dir, f"{namespace}.json")
    with open(state_file, "w") as f:
        json.dump(state, f)

    logger.warning(f"Saved state to {state_file}")


def append_dynamo_state(namespace: str, component_name: str, data: dict) -> None:
    """Append additional data to an existing component's state"""
    state_dir = os.environ.get(
        DYN_LOCAL_STATE_DIR, os.path.expanduser("~/.dynamo/state")
    )
    state_file = os.path.join(state_dir, f"{namespace}.json")

    if not os.path.exists(state_file):
        logger.warning(
            f"Skipping append to state file {state_file} because it doesn't exist"
        )
        return

    with open(state_file, "r") as f:
        state = json.load(f)

    if "components" not in state:
        state["components"] = {}
    if component_name not in state["components"]:
        state["components"][component_name] = {}

    state["components"][component_name].update(data)

    logger.warning(f"Appending {data} to {component_name} in {state_file}")

    with open(state_file, "w") as f:
        json.dump(state, f)


def _parse_service_arg(arg_name: str, arg_value: str) -> tuple[str, str, Any]:
    """Parse a single CLI argument into service name, key, and value."""

    parts = arg_name.split(".")
    service = parts[0]
    nested_keys = parts[1:]

    # Special case: if this is a ServiceArgs.envs.* path, keep value as string
    if (
        len(nested_keys) >= 2
        and nested_keys[0] == "ServiceArgs"
        and nested_keys[1] == "envs"
    ):
        value: Union[str, int, float, bool, dict, list] = arg_value
    else:
        # Parse value based on type for non-env vars
        try:
            value = json.loads(arg_value)
        except json.JSONDecodeError:
            if arg_value.isdigit():
                value = int(arg_value)
            elif arg_value.replace(".", "", 1).isdigit() and arg_value.count(".") <= 1:
                value = float(arg_value)
            elif arg_value.lower() in ("true", "false"):
                value = arg_value.lower() == "true"
            else:
                value = arg_value

    # Build nested dict structure
    result = value
    for key in reversed(nested_keys[1:]):
        result = {key: result}

    return service, nested_keys[0], result


def _parse_service_args(args: list[str]) -> Dict[str, Any]:
    service_configs: DefaultDict[str, Dict[str, Any]] = collections.defaultdict(dict)

    def deep_update(d: dict, key: str, value: Any):
        """
        Recursively updates nested dictionaries. We use this to process arguments like

        ---Worker.ServiceArgs.env.CUDA_VISIBLE_DEVICES="0,1"

        The _parse_service_arg function will parse this into:
        service = "Worker"
        nested_keys = ["ServiceArgs", "envs", "CUDA_VISIBLE_DEVICES"]

        And returns: ("VllmWorker", "ServiceArgs", {"envs": {"CUDA_VISIBLE_DEVICES": "0,1"}})

        We then use deep_update to update the service_configs dictionary with this nested value.
        """
        if isinstance(value, dict) and key in d and isinstance(d[key], dict):
            for k, v in value.items():
                deep_update(d[key], k, v)
        else:
            d[key] = value

    index = 0
    while index < len(args):
        next_arg = args[index]

        if not (next_arg.startswith("--") or "." not in next_arg):
            continue
        try:
            if "=" in next_arg:
                arg_name, arg_value = next_arg.split("=", 1)
                index += 1
            elif args[index + 1] == "=":
                arg_name = next_arg
                arg_value = args[index + 2]
                index += 3
            else:
                arg_name = next_arg
                arg_value = args[index + 1]
                index += 2
            if arg_value.startswith("-"):
                raise ValueError("Service arg value can not start with -")
            arg_name = arg_name[2:]
            service, key, value = _parse_service_arg(arg_name, arg_value)
            deep_update(service_configs[service], key, value)
        except Exception:
            raise ValueError(f"Error parsing service arg: {args[index]}")

    return service_configs


def resolve_service_config(
    config_file: pathlib.Path | TextIO | None = None,
    args: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Resolve service configuration from file and command line arguments.

    Args:
        config_file: Path to YAML config file or file object
        args: List of command line arguments

    Returns:
        Dictionary mapping service names to their configurations
    """
    service_configs: dict[str, dict[str, Any]] = {}

    # Check for deployment config first
    if "DYN_DEPLOYMENT_CONFIG" in os.environ:
        try:
            deployment_config = yaml.safe_load(os.environ["DYN_DEPLOYMENT_CONFIG"])
            # Use deployment config directly
            service_configs = deployment_config
            logger.info(f"Successfully loaded deployment config: {service_configs}")
            logger.warning(
                "DYN_DEPLOYMENT_CONFIG found in environment - ignoring configuration file and command line arguments"
            )
        except Exception as e:
            logger.warning(f"Failed to parse DYN_DEPLOYMENT_CONFIG: {e}")
    else:
        if config_file:
            with open(config_file) if isinstance(
                config_file, (str, pathlib.Path)
            ) else contextlib.nullcontext(config_file) as f:
                yaml_configs = yaml.safe_load(f)
                logger.debug(f"Loaded config from file: {yaml_configs}")
                # Initialize service_configs as empty dict if it's None
                # Convert nested YAML structure to flat dict with dot notation
                for service, configs in yaml_configs.items():
                    if service not in service_configs:
                        service_configs[service] = {}
                    for key, value in configs.items():
                        service_configs[service][key] = value

    # Process command line overrides
    if args:
        cmdline_overrides = _parse_service_args(args)
        logger.info(f"Applying command line overrides: {cmdline_overrides}")
        for service, configs in cmdline_overrides.items():
            if service not in service_configs:
                service_configs[service] = {}
            for key, value in configs.items():
                service_configs[service][key] = value

    logger.info(f"Running dynamo serve with config: {service_configs}")
    return service_configs


def configure_target_environment(target: TargetEnum):
    from dynamo.sdk.core.lib import set_target

    if target == TargetEnum.DYNAMO:
        from dynamo.sdk.core.runner.dynamo import LocalDeploymentTarget

        target = LocalDeploymentTarget()
    else:
        raise ValueError(f"Invalid target: {target}")
    logger.debug(f"Setting deployment target to {target}")
    set_target(target)


def is_local_planner_enabled(svc: Any, service_configs: dict) -> bool:
    """Check if local planner is enabled.

    Args:
        svc: The entrypoint service instance
        service_configs: Dictionary of service configurations

    Returns:
        bool: True if local planner is enabled, False otherwise
    """
    # Check all nodes to find planner
    nodes = [dep for dep in svc.all_services().values()]
    nodes.append(svc)
    planners = [
        node
        for node in nodes
        if node.config.dynamo.component_type == ComponentType.PLANNER
    ]

    if len(planners) > 1:
        console.print(
            "[bold red]Error:[/bold red] More than one planner found in the pipeline"
        )
        raise typer.Exit(code=1)

    # Exactly one planner
    if planners:
        # Get the config for the planner and check environment
        planner_config = service_configs.get(PLANNER_SERVICE_NAME, {})
        environment = planner_config.get("environment", PlannerDefaults.environment)
        return environment == "local"

    return False


def raise_local_planner_warning(svc: Any, service_configs: dict) -> None:
    """Warn if local planner is enabled and active (not set to no-op), but workers for prefill or decode is > 1. This is currently not supported.

    Args:
        svc: The service instance
        service_configs: Dictionary of service configurations
    """
    planner_config = service_configs.get(PLANNER_SERVICE_NAME, {})

    # Resolve no-op setting
    no_op = planner_config.get("no-operation", PlannerDefaults.no_operation)

    # Check worker counts across nodes
    nodes = [dep for dep in svc.all_services().values()]
    nodes.append(svc)
    worker_names = ("PrefillWorker", "VllmWorker")
    worker_counts_greater_than_one = [
        node.config.workers > 1 for node in nodes if node.name in worker_names
    ]

    if any(worker_counts_greater_than_one) and not no_op:
        logger.error(
            "Local planner is enabled, but workers for prefill or decode is > 1. Local planner must be started with prefill and decode workers set to 1."
        )
        raise typer.Exit(code=1)
