import os
import json
import click
from pathlib import Path
from stash_basic import utils


@click.command()
@click.argument("folder_path", type=click.Path(file_okay=False, dir_okay=True))
@click.option("--file_name", default="records.json", help="The name of the JSON file which will store all the data. Defaults to 'records.json'")
@click.option("--currency", default="€", help="The currency to set for all the accounts in Stash. Defaults to €.")
@click.option("--reset", is_flag=True)
@click.pass_obj
def init(obj: dict, folder_path: str, file_name: str, currency: str, reset: bool):

    '''
    Initializes the Stash CLI for first use.
    
    FOLDER_PATH is the directory path where the JSON file will be stored.
    '''

    # Run initialization only if no previous config found or reset flag is set
    if not obj or reset:
        # Make sure file_name contains the file extension
        if ".json" not in file_name:
            file_name = file_name + ".json"

        # Make sure directory path exists 
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        # Make full file path
        full_file_path = os.path.join(folder_path, file_name)
        
        if reset:
            click.echo(click.style("Re-initializing Stash...", fg="yellow"))

        click.echo(f"-- Selected Directory: {click.style(folder_path, fg="red")}")
        click.echo(f"-- Selected File Name: {click.style(file_name, fg="yellow")}")
        click.echo(f"-- Full Path: {click.style(full_file_path, fg="yellow")}")
        click.echo(f"-- Currency: {click.style(currency, fg="cyan")}")

        # Create an empty JSON file (main JSON file to hold all data)
        with open(full_file_path, "w") as json_file:
            json.dump([], json_file, ensure_ascii=True)
        
        # Create the config object
        config = {
            "path": Path(full_file_path).expanduser().resolve().as_posix(),
            "currency": currency
        }

        # Save the config object
        utils.save_config(config)

        # Update the object at the context level
        obj.update(config)
        
        click.echo(click.style("Stash initialization complete!", fg="green") if not reset else click.style("Stash re-initialization complete!", fg="green"))

    else:
        click.echo(f"It seems like {click.style("stash init", fg="cyan")} was run before.")
        click.echo(f"Loading config.json from {click.style(utils.CONFIG_FILE, fg="yellow")}")
        click.echo(f"Previously set JSON file path: {click.style(obj["path"], fg="yellow")}")
        click.echo(f"Previously set currency: {click.style(obj["currency"], fg="cyan")}")