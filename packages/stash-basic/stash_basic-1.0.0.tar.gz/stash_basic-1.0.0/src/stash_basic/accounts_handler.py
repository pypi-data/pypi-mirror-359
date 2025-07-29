import click
import tabulate
import json
from stash_basic import utils

@click.command()
@click.argument("full_name", type=click.STRING)
@click.argument("email", type=click.STRING)
@click.argument("dob", type=click.DateTime())
@click.pass_obj
def add(obj: dict, full_name: str, email: str, dob: click.DateTime):
    '''
    Creates a new account and adds it to Stash.

    FULL_NAME is the account holder's complete name

    EMAIL is the account holder's email address

    DOB is the account holder's Date of Birth. Use the format YYYY-MM-DD.
    '''

    # Populate the account object/dictionary
    account = {}
    account["full_name"] = full_name
    account["email"] = email
    account["dob"] = dob.strftime("%Y-%m-%d")
    account["id"] = utils.create_unique_id(full_name, dob)
    account["balance"] = 0.0
    account["transactions"] = []
    
    # Read the current JSON file and retreive the contents
    with open(obj["path"], "r") as json_file:
        contents = json.load(json_file)

    # Append the current account to the existing contents
    if not utils.is_duplicate_account(contents, full_name, dob):
        contents.append(account)

        # Write back the new data
        with open(obj["path"], "w") as new_json:
            json.dump(contents, new_json, indent=2, ensure_ascii=True)
        
        # Display to console
        click.echo("\n")
        click.echo(click.style("A new account with the following details has been successfully created!", fg="green"))
        
        table_data = [
            [click.style("Holder's Full Name", fg="green"), account["full_name"]],
            [click.style("Holder's Email", fg="green"), account["email"]],
            [click.style("Holder's DOB", fg="green"), account["dob"]],
            [click.style("Account Unique ID", fg="green"), click.style(account["id"], fg="red")],
            [click.style("Account Balance", fg="green"), click.style(f"{obj["currency"]} {account["balance"]}", fg="yellow")]
        ]
        click.echo(tabulate.tabulate(table_data, tablefmt="grid"))
    
    else:
        click.echo(click.style("Account already exists!", fg="red"))

@click.command()
@click.argument("id", type=click.STRING)
@click.pass_obj
def delete(obj: dict, id: str):

    '''
    Deletes the account of the provided account ID.

    ID is the unique identifier for the account.
    '''

    # Load the contents from the JSON
    with open(obj["path"], 'r') as json_file:
        contents = json.load(json_file)

    # Search for the account to delete
    account_index = -1
    for i, account in enumerate(contents):
        if account["id"] == id:
            account_index = account_index + i + 1
            break
    
    # If account does not exist
    if account_index == -1:
        click.echo(f"{click.style("ERROR:", fg="black", bg="red")} Cannot find the account. Please re-check the ID.")
    else:
        # Ask user via prompt for confirmation
        click.echo(tabulate.tabulate(
            [
                [click.style("Holder's Full Name", fg="green"), account["full_name"]],
                [click.style("Holder's Email", fg="green"), account["email"]],
                [click.style("Holder's DOB", fg="green"), account["dob"]],
                [click.style("Account Unique ID", fg="green"), click.style(account["id"], fg="red")],
                [click.style("Account Balance", fg="green"), click.style(f"{obj["currency"]} {account["balance"]}", fg="yellow")]
            ]
            ,tablefmt="grid"))
        
        if click.confirm("Do you want to proceed to delete the above account?"):
            contents.pop(account_index)

            # Save the new contents
            with open(obj["path"], 'w') as new_json_file:
                json.dump(contents, new_json_file, indent=2)
            
            click.echo(click.style("Account removed successfully", fg="green"))
        else:
            click.echo(click.style("Account was not removed.", fg="yellow"))

@click.command()
@click.pass_obj
def summary(obj: dict):
    '''
    Display all accounts on Stash with their details. Included details 
    are account holder's name, email, DOB and account ID.
    '''

    # Load the contents of the JSON
    with open(obj["path"], "r") as json_file:
        contents = json.load(json_file)
    
    # Ensure contents are not empty, i.e. there are no accounts in Stash
    if not contents:
        click.echo(f"{click.style("INFO:", bg="blue")} There are no accounts in stash to display a summary.")
        click.echo(f"You can create an account by using {click.style("stash accounts add", fg="yellow")}")
    else:
        # Loop through the accounts
        table = []
        headers = []

        for account in contents:
            row = []
            for key, value in account.items():
                if key != "transactions":
                    if key == "balance":
                        row.append(click.style(f"{obj["currency"]} {value}", fg="cyan"))
                    else:
                        row.append(value)
            table.append(row)
        
        # Populate headers
        for header_item in contents[0].keys():
            if header_item != "transactions":
                headers.append(header_item)

        click.echo(click.style("Here is a summary of all accounts on Stash", fg="yellow"))
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

@click.command()
@click.argument("id", type=click.STRING)
@click.pass_obj
def statement(obj: dict, id: str):
    '''
    Prints the account statement for an account.

    ID is the unique ID of the account for which you want the statement.
    '''

    # Load contents
    with open(obj["path"], "r") as json_file:
        contents = json.load(json_file)
    
    # Search for the account
    account_index = -1
    for i, account in enumerate(contents):
        if account["id"] == id:
            account_index += i + 1
    
    # Account not found
    if account_index == -1:
        click.echo(f"{click.style("ERROR:", fg="black", bg="red")} Cannot find the account. Please re-check the ID.")
    # Account found
    else:
        transactions = contents[account_index]["transactions"]

        # Check if transactions are empty
        if not transactions:
            click.echo(f"{click.style("INFO:", bg="blue")} There are no transactions to display.")
        else:
            table_data = []
            table_headers = []

            # Populate table_data
            for transaction in transactions:
                row = []
                for key, value in transaction.items():
                    if key == "type":
                        row.append(click.style(f"{value}", fg="red" if value == "DEBIT" else "green"))
                    elif key == "amount":
                        row.append(f"{click.style(obj["currency"], fg="cyan")} {click.style(value, fg="red" if transaction["type"] == "DEBIT" else "green")}")
                    else:
                        row.append(value)
                table_data.append(row)
            
            # Populate table_headers
            for header_item in transactions[0].keys():
                table_headers.append(header_item)
            
            # Add total balance
            total_columns = len(transactions[0].keys())
            data_row = [""] * total_columns
            data_row[-1] = click.style(f"{obj["currency"]} {contents[account_index]["balance"]}", fg="yellow")
            data_row[-2] = click.style("Total:", fg="cyan")

            table_data.append(data_row)

            # Display the statement
            click.echo(tabulate.tabulate(table_data, table_headers, tablefmt="grid"))