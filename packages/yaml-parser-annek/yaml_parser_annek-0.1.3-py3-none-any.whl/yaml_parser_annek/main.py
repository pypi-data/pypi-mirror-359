from dotenv import load_dotenv
from datetime import datetime
from pprint import pprint as pp
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import os
import sys
import typer
import warnings

# Load environment
load_dotenv()

# Instantiate instance
app = typer.Typer(no_args_is_help=True)

import_base_dir = os.getenv("YPA_IMPORT_DIR")
export_base_dir = os.getenv("YPA_EXPORT_DIR")

if import_base_dir is None or export_base_dir is None:
    print("You must set YPA_IMPORT_DIR and YPA_EXPORT_DIR or define them in a .env file.")
    sys.exit(1)


warnings.filterwarnings("ignore", category=DeprecationWarning)

logname = "ypa.log"

logging.basicConfig(
    filename=logname,
    filemode="a",
    format="%(asctime)s.%(msecs)d %(name)s %(levelname)s -- %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger("ypa")
logger.info("Starting YPA the YAML Parser CLI in Python")


class Machine(BaseModel):
    """
    A class to represent a machine.

    Attributes:
        inventory_name (str): The name of the node.
        hostvars (Dict[str, str]): The host variables of the node.
    """

    inventory_name: str
    hostvars: Dict

    def __str__(self):
        return f"Machine(inventory_name={self.inventory_name}, hostvars={self.hostvars})"
    def __repr__(self):
        return f"Machine(inventory_name={self.inventory_name}, hostvars={self.hostvars})"
    def __eq__(self, other):
        if not isinstance(other, Machine):
            return False
        return (
            self.inventory_name == other.inventory_name
            and self.hostvars == other.hostvars
        )
    def __hash__(self):
        return hash((self.inventory_name, frozenset(self.hostvars.items())))

    def transpose_hostvar_keys(self):
        """
        Transpose the keys of the hostvars dictionary.

        """
        for key in list(self.hostvars.keys()):
            logger.debug(f"Transposing key: {key}")
            if "role" in key:
                logger.debug("Transposing 'roles' key.")
                self.hostvars['assigned_roles'] = self.hostvars.pop(key)
                break
            if key.endswith("_assigned"):
                new_key = key[:-9]
                self.hostvars[new_key] = self.hostvars.pop(key)


@app.callback()
def callback():
    """
    A CLI for parsing yaml files.

    You must set YPA_IMPORT_DIR and YPA_EXPORT_DIR or define them in a .env file.

    Example:

    YPA_IMPORT_DIR="/my-yaml-files"

    YPA_EXPORT_DIR="/inventory/host_vars"

    """


@app.command()
def get_machine_details(
    filename: str,
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Silent mode. No output."
    ),
):
    """
    Get details for Machines from a YAML file.

    Arguments:

    filename: The path to the YAML file.
    """
    full_path = os.path.join(import_base_dir, filename) # type: ignore
    if not os.path.exists(full_path):
        logger.error(f"File {full_path} does not exist.")
        typer.echo(f"File {full_path} does not exist.")
        raise typer.Exit(code=1)
    try:
        import yaml
        with open(full_path, "r") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        typer.echo(f"Error parsing YAML file: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        typer.echo(f"Unexpected error: {e}")
        raise typer.Exit(code=1)
    vms = data['vm_info']
    machines = []
    for key, value in vms.items():
        if not isinstance(value, dict):
            logger.error(f"Invalid data format for {key}: {value}")
            typer.echo(f"Invalid data format for {key}: {value}")
            raise typer.Exit(code=1)
        machine = Machine(inventory_name=key, hostvars=value)
        machine.transpose_hostvar_keys()
        if not silent:
            typer.echo(f"Machine: {machine.inventory_name}, Hostvars: {machine.hostvars} \n")
        machines.append(machine)
    if not silent:
        typer.echo(f"Found {len(machines)} machines in {filename}.")
        logger.info(f"Found {len(machines)} machines in {filename}.")
    else:
        logger.info(f"Processed {len(machines)} machines from {filename}.")
    if not silent:
        typer.echo("Machines details:")
    else:
        logger.info("Machines details:")
    return machines


@app.command()
def write_hostvar_files(
    import_filename: str,
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Silent mode. No output."
    ),
):
    """
    Export machine details to a file.

    Arguments:

    import_filename: The path to the YAML file to import.

    """
    machines = get_machine_details(import_filename, silent=silent)
    for machine in machines:
        if not machine.hostvars:
            logger.warning(f"No hostvars found for {machine.inventory_name}. Skipping.")
            continue
        export_dir = export_base_dir + os.sep + machine.inventory_name # type: ignore
        export_path = os.path.join(export_dir, "main.yml")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            logger.info(f"Created directory {export_dir} for {machine.inventory_name}.")
        try:
            import yaml
            with open(export_path, "w") as file:
                yaml.dump(machine.hostvars, file)
            if not silent:
                typer.echo(f"Exported {machine.inventory_name} to {export_path}.")
            logger.info(f"Exported {machine.inventory_name} to {export_path}.")
        except Exception as e:
            logger.error(f"Error writing to {export_path}: {e}")
            typer.echo(f"Error writing to {export_path}: {e}")
            raise typer.Exit(code=1)
    if not silent:
        typer.echo(f"Exported hostvars for {len(machines)} machines to {export_base_dir}.")
    else:
        logger.info(f"Exported hostvars for {len(machines)} machines to {export_base_dir}.")
    return machines