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

import contextlib
import json
import logging
import os
import pathlib
import shutil
import tempfile
from typing import Any, Dict, Optional

from circus.sockets import CircusSocket
from circus.watcher import Watcher

from dynamo.sdk.cli.circus import CircusRunner
from dynamo.sdk.core.runner import TargetEnum

from .allocator import NVIDIA_GPU, ResourceAllocator
from .circus import _get_server_socket
from .utils import (
    DYN_LOCAL_STATE_DIR,
    ServiceProtocol,
    reserve_free_port,
    save_dynamo_state,
)

logger = logging.getLogger(__name__)

_DYNAMO_WORKER_SCRIPT = "dynamo.sdk.cli.serve_dynamo"


def _get_dynamo_worker_script(
    dynamo_identifier: str, svc_name: str, target: TargetEnum
) -> list[str]:
    args = [
        "-m",
        _DYNAMO_WORKER_SCRIPT,
        dynamo_identifier,
        "--service-name",
        svc_name,
        "--worker-id",
        "$(CIRCUS.WID)",
        "--target",
        target,
    ]
    return args


def create_dynamo_watcher(
    dynamo_identifier: str,
    svc: ServiceProtocol,
    uds_path: str,
    scheduler: ResourceAllocator,
    working_dir: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    target: TargetEnum = TargetEnum.DYNAMO,
) -> tuple[Watcher, CircusSocket, str]:
    """Create a watcher for a Dynamo service in the dependency graph"""
    from dynamo.sdk.cli.circus import create_circus_watcher

    num_workers, resource_envs = scheduler.get_resource_envs(svc)
    uri, socket = _get_server_socket(svc, uds_path)
    args = _get_dynamo_worker_script(dynamo_identifier, svc.name, target)
    if resource_envs:
        args.extend(["--worker-env", json.dumps(resource_envs)])

    # Update env to include ServiceConfig and service-specific environment variables
    worker_env = env.copy() if env else {}
    # Pass through the main service config
    if "DYNAMO_SERVICE_CONFIG" in os.environ:
        worker_env["DYNAMO_SERVICE_CONFIG"] = os.environ["DYNAMO_SERVICE_CONFIG"]

    # Get service-specific environment variables from DYNAMO_SERVICE_ENVS
    if "DYNAMO_SERVICE_ENVS" in os.environ:
        try:
            service_envs = json.loads(os.environ["DYNAMO_SERVICE_ENVS"])
            if svc.name in service_envs:
                service_args = service_envs[svc.name].get("ServiceArgs", {})
                if "envs" in service_args:
                    worker_env.update(service_args["envs"])
                    logger.info(
                        f"Added service-specific environment variables for {svc.name}"
                    )
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse DYNAMO_SERVICE_ENVS: {e}")

    # use namespace from the service
    namespace, _ = svc.dynamo_address()

    # Create the watcher with updated environment
    watcher = create_circus_watcher(
        name=f"{namespace}_{svc.name}",
        args=args,
        numprocesses=num_workers,
        working_dir=working_dir,
        env=worker_env,
    )

    logger.info(f"Created watcher for {svc.name}'s in the {namespace} namespace")

    return watcher, socket, uri


def clear_namespace(namespace: str) -> None:
    """
    Check if utils/clear_namespace.py exists and run it to clear the namespace.
    """
    import os.path
    import subprocess

    clear_script_path = "utils/clear_namespace.py"

    if os.path.exists(clear_script_path):
        logger.info(f"Clearing namespace {namespace} using {clear_script_path}")
        try:
            # Run the script and wait for it to complete
            result = subprocess.run(
                ["python", "-m", "utils.clear_namespace", "--namespace", namespace],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"Clear namespace output: {result.stdout}")
            logger.info(f"Successfully cleared namespace {namespace}")
            if result.stderr:
                logger.info(f"Clear namespace stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clear namespace {namespace}: {e.stderr}")
    else:
        logger.debug(
            f"Script not found at {clear_script_path}, skip namespace clearing"
        )


def serve_dynamo_graph(
    graph: str,
    working_dir: str | None = None,
    dependency_map: dict[str, str] | None = None,
    service_name: str = "",
    enable_local_planner: bool = False,
    target: TargetEnum = TargetEnum.DYNAMO,
    system_app_port: Optional[int] = None,
    system_app_host: Optional[str] = None,
    enable_system_app: bool = False,
    use_default_health_checks: bool = False,
) -> CircusRunner:
    from dynamo.runtime.logging import configure_dynamo_logging
    from dynamo.sdk.cli.circus import create_arbiter, create_circus_watcher
    from dynamo.sdk.lib.loader import find_and_load_service

    from .allocator import ResourceAllocator

    configure_dynamo_logging(service_name=service_name)

    namespace: str = ""
    env: dict[str, Any] = {}
    svc = find_and_load_service(graph, working_dir)
    dynamo_path = pathlib.Path(working_dir or ".")

    watchers: list[Watcher] = []
    sockets: list[CircusSocket] = []
    allocator = ResourceAllocator()
    if dependency_map is None:
        dependency_map = {}

    standalone = False
    if service_name:
        logger.info(f"Service '{service_name}' running in standalone mode")
        standalone = True

    # TODO: We are signaling by setting env vars to downstream subprocesses. Let's pass flags on our invokation of serve_dynamo instead. That way the API is defined at the top level.
    # Signal downstream workers to start system app by setting DYNAMO_SYSTEM_APP_* env vars for each worker. They are respectively consumed in serve_dynamo.py
    if enable_system_app:
        env["DYNAMO_SYSTEM_APP_ENABLED"] = "true"
        if system_app_port:
            # Throw if not standalone mode. Should only be set in standalone mode.
            # TODO: This might still cause issues if we are running in standalone, but have multiple workers, need to figure this one out
            if not standalone:
                raise ValueError(
                    "Specifying system app port is only supported in standalone mode (i.e --service-name is set)"
                )
            env["DYNAMO_SYSTEM_APP_PORT"] = str(system_app_port)
        if system_app_host:
            env["DYNAMO_SYSTEM_APP_HOST"] = system_app_host
        # Only set use_default_health_checks if explicitly enabled
        if use_default_health_checks:
            env["DYNAMO_SYSTEM_APP_USE_DEFAULT_HEALTH_CHECKS"] = "true"
            logger.info("Default health checks enabled for system app")

    if service_name and service_name != svc.name:
        svc = svc.find_dependent_by_name(service_name)
    num_workers, resource_envs = allocator.get_resource_envs(svc)
    uds_path = tempfile.mkdtemp(prefix="dynamo-uds-")
    try:
        if not service_name and not standalone:
            with contextlib.ExitStack() as port_stack:
                # first check if all components has the same namespace
                namespaces = set()
                for name, dep_svc in svc.all_services().items():
                    if name == svc.name or name in dependency_map:
                        continue
                    namespaces.add(dep_svc.dynamo_address()[0])
                if len(namespaces) > 1:
                    raise RuntimeError(
                        f"All components must have the same namespace, got {namespaces}"
                    )
                else:
                    namespace = namespaces.pop() if namespaces else ""
                    logger.info(f"Serving dynamo graph with namespace {namespace}")
                # clear residue etcd/nats entry (if any) under this namespace
                logger.info(f"Clearing namespace {namespace} before serving")
                clear_namespace(namespace)

                for name, dep_svc in svc.all_services().items():
                    if name == svc.name or name in dependency_map:
                        continue
                    if not dep_svc.is_servable():
                        raise RuntimeError(
                            f"Service {dep_svc.name} is not servable. Please use link to override with a concrete implementation."
                        )
                    new_watcher, new_socket, uri = create_dynamo_watcher(
                        graph,
                        dep_svc,
                        uds_path,
                        allocator,
                        str(dynamo_path.absolute()),
                        env=env,
                        target=target,
                    )
                    watchers.append(new_watcher)
                    sockets.append(new_socket)
                    dependency_map[name] = uri
                # reserve one more to avoid conflicts
                port_stack.enter_context(reserve_free_port())
        else:
            namespace, _ = svc.dynamo_address()
        dynamo_args = [
            "-m",
            _DYNAMO_WORKER_SCRIPT,
            graph,
            "--service-name",
            svc.name,
            "--worker-id",
            "$(CIRCUS.WID)",
        ]

        # resource_envs is the resource allocation (ie CUDA_VISIBLE_DEVICES) for each worker created by the allocator
        # these resource_envs are passed to each individual worker's environment which is set in serve_dynamo
        if resource_envs:
            dynamo_args.extend(["--worker-env", json.dumps(resource_envs)])
        # env is the base dynamlocal fault tolerence o environment variables. We make a copy and update it to add any service configurations and additional env vars
        worker_env = env.copy() if env else {}

        # Pass through the main service config
        if "DYNAMO_SERVICE_CONFIG" in os.environ:
            worker_env["DYNAMO_SERVICE_CONFIG"] = os.environ["DYNAMO_SERVICE_CONFIG"]

        # Get service-specific environment variables from DYNAMO_SERVICE_ENVS
        if "DYNAMO_SERVICE_ENVS" in os.environ:
            try:
                service_envs = json.loads(os.environ["DYNAMO_SERVICE_ENVS"])
                if svc.name in service_envs:
                    service_args = service_envs[svc.name].get("ServiceArgs", {})
                    if "envs" in service_args:
                        worker_env.update(service_args["envs"])
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse DYNAMO_SERVICE_ENVS: {e}")

        watcher = create_circus_watcher(
            name=f"{namespace}_{svc.name}",
            args=dynamo_args,
            numprocesses=num_workers,
            working_dir=str(dynamo_path.absolute()),
            env=worker_env,
        )
        watchers.append(watcher)
        logger.info(
            f"Created watcher for {svc.name} with {num_workers} workers in the {namespace} namespace"
        )

        # inject runner map now
        inject_env = {"DYNAMO_RUNNER_MAP": json.dumps(dependency_map)}

        for watcher in watchers:
            if watcher.env is None:
                watcher.env = inject_env
            else:
                watcher.env.update(inject_env)

        arbiter_kwargs: dict[str, Any] = {
            "watchers": watchers,
            "sockets": sockets,
        }

        arbiter = create_arbiter(**arbiter_kwargs)
        arbiter.exit_stack.callback(clear_namespace, namespace)
        arbiter.exit_stack.callback(shutil.rmtree, uds_path, ignore_errors=True)
        if enable_local_planner:
            arbiter.exit_stack.callback(
                shutil.rmtree,
                os.environ.get(
                    DYN_LOCAL_STATE_DIR, os.path.expanduser("~/.dynamo/state")
                ),
                ignore_errors=True,
            )
            logger.warn(f"arbiter: {arbiter.endpoint}")

            # save deployment state for planner
            if not namespace:
                raise ValueError("No namespace found for service")

            # Track GPU allocation for each component
            component_resources = {}
            logger.info(f"Building component resources for {len(watchers)} watchers")

            for watcher in watchers:
                component_name = watcher.name
                logger.info(f"Processing watcher: {component_name}")

                # Extract worker info including GPU allocation
                worker_gpu_info: dict[str, Any] = {}

                # Extract service name from watcher name
                service_name = ""
                if component_name.startswith(f"{namespace}"):
                    service_name = component_name.replace(f"{namespace}_", "", 1)

                # Get GPU allocation from ResourceAllocator
                if (
                    not worker_gpu_info
                    and hasattr(allocator, "_service_gpu_allocations")
                    and service_name
                ):
                    gpu_allocations = getattr(allocator, "_service_gpu_allocations", {})
                    if service_name in gpu_allocations:
                        logger.info(
                            f"Found GPU allocation for {service_name} in ResourceAllocator: {gpu_allocations[service_name]}"
                        )
                        worker_gpu_info["allocated_gpus"] = gpu_allocations[
                            service_name
                        ]

                # Store final worker GPU info
                component_resources[component_name] = worker_gpu_info
                logger.info(f"Final GPU info for {component_name}: {worker_gpu_info}")

            logger.info(f"Completed component resources: {component_resources}")

            # Now create components dict with resources included
            components_dict = {
                watcher.name: {
                    "watcher_name": watcher.name,
                    "cmd": watcher.cmd
                    + " -m "
                    + " ".join(
                        watcher.args[1:]
                    )  # WAR because it combines python-m into 1 word
                    if hasattr(watcher, "args")
                    else watcher.cmd,
                    "resources": component_resources.get(watcher.name, {}),
                }
                for watcher in watchers
            }

            save_dynamo_state(
                namespace,
                arbiter.endpoint,
                components=components_dict,
                environment={
                    "DYNAMO_SERVICE_CONFIG": os.environ["DYNAMO_SERVICE_CONFIG"],
                    "SYSTEM_RESOURCES": {
                        "total_gpus": len(allocator.system_resources[NVIDIA_GPU]),
                        "gpu_info": [
                            str(gpu) for gpu in allocator.system_resources[NVIDIA_GPU]
                        ],
                    },
                },
            )

        arbiter.start(
            cb=lambda _: logger.info(  # type: ignore
                (
                    "Starting Dynamo Service %s (Press CTRL+C to quit)"
                    if (
                        hasattr(svc, "is_dynamo_component")
                        and svc.is_dynamo_component()
                    )
                    else "Starting %s (Press CTRL+C to quit)"
                ),
                *(
                    (svc.name,)
                    if (
                        hasattr(svc, "is_dynamo_component")
                        and svc.is_dynamo_component()
                    )
                    else (graph,)
                ),
            ),
        )
        return CircusRunner(arbiter=arbiter)
    except Exception:
        shutil.rmtree(uds_path, ignore_errors=True)
        raise
