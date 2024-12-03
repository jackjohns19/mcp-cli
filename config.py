# config.py
import json
import logging
from typing import Dict, Optional, List
from transport.stdio.stdio_server_parameters import StdioServerParameters

async def load_config(config_path: str, server_names: Optional[List[str]] = None) -> Dict[str, StdioServerParameters]:
    """ 
    Load server configurations from a JSON file.
    If server_names is None, load all servers.
    If server_names is a list, load only specified servers.
    """
    try:
        # debug
        logging.debug(f"Loading config from {config_path}")

        # Read the configuration file
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        # Get the mcpServers configuration
        mcp_servers = config.get("mcpServers", {})

        # Determine which servers to load
        if server_names is None:
            # If no specific servers specified, load all servers
            selected_servers = mcp_servers
        else:
            # Filter to only specified servers
            selected_servers = {name: mcp_servers[name] for name in server_names 
                                if name in mcp_servers}

        # Validate that at least one server was found
        if not selected_servers:
            error_msg = "No servers found in configuration."
            if server_names:
                error_msg = f"Specified servers {server_names} not found in configuration."
            logging.error(error_msg)
            raise ValueError(error_msg)

        # Construct server parameters for each selected server
        result = {}
        for server_name, server_config in selected_servers.items():
            server_params = StdioServerParameters(
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env"),
            )
            result[server_name] = server_params

            # debug
            logging.debug(f"Loaded config for {server_name}: command='{server_params.command}', "
                          f"args={server_params.args}, env={server_params.env}")

        # return result
        return result

    except FileNotFoundError:
        # error
        error_msg = f"Configuration file not found: {config_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    except json.JSONDecodeError as e:
        # json error
        error_msg = f"Invalid JSON in configuration file: {e.msg}"
        logging.error(error_msg)
        raise json.JSONDecodeError(error_msg, e.doc, e.pos)
    except ValueError as e:
        # error
        logging.error(str(e))
        raise
