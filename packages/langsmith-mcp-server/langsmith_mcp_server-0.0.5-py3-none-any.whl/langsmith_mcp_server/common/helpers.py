"""Helper functions for the LangSmith MCP server."""

import re
from datetime import datetime
from typing import Any, Dict, Optional, Union


def get_langgraph_app_host_name(run_stats: dict) -> Optional[str]:
    """
    Get the langgraph app host name from the run stats

    Args:
        run_stats (dict): The run stats

    Returns:
        str | None: The langgraph app host name
    """
    if run_stats and run_stats.get("run_facets"):
        for run_facet in run_stats["run_facets"]:
            try:
                for rfk in run_facet.keys():
                    langgraph_host = re.search(r"http[s]?:\/\/(?P<langgraph_host>[^\/]+)", rfk)
                    if langgraph_host:
                        return langgraph_host.group("langgraph_host")
            except re.error:
                continue
    return None


def _parse_as_of_parameter(as_of: str) -> Union[datetime, str]:
    """
    Parse the as_of parameter, converting ISO timestamps to datetime objects
    while leaving version tags as strings.

    Args:
        as_of: Dataset version tag OR ISO timestamp string

    Returns:
        datetime object if as_of is a valid ISO timestamp, otherwise the original string
    """
    try:
        # Try to parse as ISO format datetime
        return datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        # If parsing fails, assume it's a version tag and return as string
        return as_of


def get_last_run_stats(client, project_name: str) -> Dict[str, Any]:
    """
    Get the last run stats for a given project name

    Args:
        client: LangSmith client instance
        project_name (str): The name of the project to get the last run stats for

    Returns:
        dict: The last run stats for the given project name
    """
    try:
        # Get the last run
        last_run = client.list_runs(project_name=project_name, limit=1)
        last_run = list(last_run)

        if last_run and len(last_run) > 0:
            # Return the run
            run = last_run[0]

            # Return just the trace ID as we can use this to open the trace view
            return {
                "trace_id": run.id,
                # "data": run
            }
        return None
    except Exception as e:
        return {"error": f"Error getting last run stats: {str(e)}"}
