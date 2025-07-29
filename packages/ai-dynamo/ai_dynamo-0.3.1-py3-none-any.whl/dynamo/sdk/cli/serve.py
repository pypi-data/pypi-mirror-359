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

import json
import logging
import os
import sys
import typing as t
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from dynamo.sdk.cli.utils import (
    is_local_planner_enabled,
    raise_local_planner_warning,
    resolve_service_config,
)
from dynamo.sdk.core.runner import TargetEnum

if t.TYPE_CHECKING:
    P = t.ParamSpec("P")  # type: ignore
    F = t.Callable[P, t.Any]  # type: ignore

logger = logging.getLogger(__name__)
console = Console()


def serve(
    ctx: typer.Context,
    graph: str = typer.Argument(..., help="The path to the Dynamo graph to serve"),
    service_name: str = typer.Option(
        "",
        help="Only serve the specified service. Don't serve any dependencies of this service.",
        envvar="DYNAMO_SERVICE_NAME",
    ),
    depends: List[str] = typer.Option(
        [],
        help="List of runner dependencies in name=value format",
        envvar="DYNAMO_SERVE_DEPENDS",
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config-file",
        "-f",
        help="Path to YAML config file for service configuration",
        exists=True,
    ),
    port: Optional[int] = typer.Option(
        None,
        "--port",
        "-p",
        help="The port to listen on for the REST API server",
        envvar="DYNAMO_PORT",
    ),
    host: Optional[str] = typer.Option(
        None,
        help="The host to bind for the REST API server",
        envvar="DYNAMO_HOST",
    ),
    system_app_port: Optional[int] = typer.Option(
        None,
        help="The port to listen on for the system app. This is only supported when --service-name is set (only one service is started).",
        envvar="DYNAMO_SYSTEM_APP_PORT",
    ),
    system_app_host: Optional[str] = typer.Option(
        None,
        help="The host to bind for the system app.",
        envvar="DYNAMO_SYSTEM_APP_HOST",
    ),
    enable_system_app: bool = typer.Option(
        False,
        help="Enable the system app.",
        envvar="DYNAMO_SYSTEM_APP_ENABLED",
    ),
    use_default_health_checks: bool = typer.Option(
        False,
        "--use-default-health-checks",
        help="Use default liveness and readiness health checks if none are provided.",
    ),
    working_dir: Optional[Path] = typer.Option(
        None,
        help="When loading from source code, specify the directory to find the Service instance",
    ),
    dry_run: bool = typer.Option(
        False,
        help="Print the final service configuration and exit without starting the server",
    ),
    target: TargetEnum = typer.Option(
        TargetEnum.DYNAMO,
        "--target",
        help="Specify the target: 'dynamo'",
        case_sensitive=False,
    ),
):
    """Locally serve a Dynamo graph.

    Starts a local server for the specified Dynamo graph.
    """
    from dynamo.runtime.logging import configure_dynamo_logging
    from dynamo.sdk.cli.utils import configure_target_environment
    from dynamo.sdk.core.protocol.interface import LinkedServices
    from dynamo.sdk.lib.loader import find_and_load_service

    configure_target_environment(target)
    # Extract extra arguments not captured by typer
    service_configs = resolve_service_config(config_file, ctx.args)

    # Process depends
    runner_map_dict = {}
    if depends:
        try:
            runner_map_dict = dict([s.split("=", maxsplit=2) for s in depends or []])
        except ValueError:
            console.print(
                "[bold red]Error:[/bold red] Invalid format for --depends option. Use format 'name=value'"
            )
            raise typer.Exit(code=1)

    if dry_run:
        console.print("[bold green]Service Configuration:[/bold green]")
        console.print_json(json.dumps(service_configs))
        console.print(
            "\n[bold green]Environment Variable that would be set:[/bold green]"
        )
        console.print(f"DYNAMO_SERVICE_CONFIG={json.dumps(service_configs)}")
        raise typer.Exit()

    configure_dynamo_logging()

    if service_configs:
        os.environ["DYNAMO_SERVICE_CONFIG"] = json.dumps(service_configs)

    if working_dir is None:
        if os.path.isdir(os.path.expanduser(graph)):
            working_dir = Path(os.path.expanduser(graph))
        else:
            working_dir = Path(".")

    # Convert Path objects to strings where string is required
    working_dir_str = str(working_dir)

    if sys.path[0] != working_dir_str:
        sys.path.insert(0, working_dir_str)

    svc = find_and_load_service(graph, working_dir=working_dir)
    logger.debug(f"Loaded service: {svc.name}")
    logger.debug("Dependencies: %s", [dep.on.name for dep in svc.dependencies.values()])
    LinkedServices.remove_unused_edges()

    # Check if local planner is enabled
    enable_local_planner = is_local_planner_enabled(svc, service_configs)
    if enable_local_planner:
        # Raise warning if local planner is enabled, but workers for prefill or decode is > 1. Not supported.
        raise_local_planner_warning(svc, service_configs)

    from dynamo.sdk.cli.serving import serve_dynamo_graph  # type: ignore

    svc.inject_config()

    # Start the service
    console.print(
        Panel.fit(
            f"[bold]Starting Dynamo service:[/bold] [cyan]{graph}[/cyan]",
            title="[bold green]Dynamo Serve[/bold green]",
            border_style="green",
        )
    )
    serve_dynamo_graph(
        graph,
        working_dir=working_dir_str,
        # host=host,
        # port=port,
        dependency_map=runner_map_dict,
        service_name=service_name,
        enable_local_planner=enable_local_planner,
        target=target,
        system_app_port=system_app_port,
        system_app_host=system_app_host,
        enable_system_app=enable_system_app,
        use_default_health_checks=use_default_health_checks,
    )
