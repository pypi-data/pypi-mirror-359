import json
import click
import tabulate
from datetime import datetime

@click.command()
@click.argument("id", type=click.STRING)
@click.argument("amount", type=click.FLOAT)
@click.option("--description", "--desc", help="A short description for the credit transaction.", default="Amount CREDITED.")
@click.pass_obj
def credit(obj: dict, id: str, amount: float, description: str):
    '''
    Adds money to an account.

    ID is the unique ID of the account in which you want to add money.

    AMOUNT is the money you want to add to the account.
    '''

    # Load contents
    with open(obj["path"], "r") as json_file:
        contents = json.load(json_file)

    # Search for the account
    account_index = -1
    for i, account in enumerate(contents):
        if account["id"] == id:
            account_index = account_index + i + 1

    # Account not found
    if account_index == -1:
        click.echo(f"{click.style('ERROR:', bg="red")} Account not found. Please re-check the account ID.")
    # Account found
    else:
        transaction_obj = {}
        timestamp = datetime.now().timestamp()
        transaction_obj["transaction_id"] = int(timestamp)
        transaction_obj["date"] = datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y")
        transaction_obj["time"] = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        transaction_obj["description"] = description
        transaction_obj["type"] = "CREDIT"
        transaction_obj["amount"] = round(amount, 2)

        # Add transaction row to account
        contents[account_index]["transactions"].append(transaction_obj)

        # Update balance
        contents[account_index]["balance"] = round(contents[account_index]["balance"] + amount, 2)

        # Add the contents to file
        with open(obj["path"], "w") as new_json_file:
            json.dump(contents, new_json_file, indent=2)
        
        click.echo(click.style("The following transaction was made successfully:", fg="green"))

        # Display transaction for reference
        click.echo(tabulate.tabulate(
            [
                [click.style("Transaction ID", fg="cyan"), transaction_obj["transaction_id"]],
                [click.style("Date", fg="cyan"), transaction_obj["date"]],
                [click.style("Time", fg="cyan"), transaction_obj["time"]],
                [click.style("Description", fg="cyan"), transaction_obj["description"]],
                [click.style("Type", fg="cyan"), click.style(transaction_obj["type"], fg="green")],
                [click.style(f"Amount", fg="cyan"), click.style(f"{obj["currency"]} {transaction_obj["amount"]}", fg="green")],
                [click.style(f"Balance", fg="cyan"), click.style(f"{obj["currency"]} {contents[account_index]["balance"]}", fg="yellow")]

            ],
            tablefmt="grid"
        ))

@click.command()
@click.argument("id", type=click.STRING)
@click.argument("amount", type=click.FLOAT)
@click.option("--description", "--desc", help="A short description for the debit transaction.", default="Amount DEBITED.")
@click.pass_obj
def debit(obj: dict, id: str, amount: float, description: str):
    '''
    Removes money from an account.

    ID is the unique ID of the account from which you want to remove money.

    AMOUNT is the money you want to remove from the account.
    '''

    # Load contents
    with open(obj["path"], "r") as json_file:
        contents = json.load(json_file)

    # Search for the account
    account_index = -1
    for i, account in enumerate(contents):
        if account["id"] == id:
            account_index = account_index + i + 1

    # Account not found
    if account_index == -1:
        click.echo(f"{click.style('ERROR:', bg="red")} Account not found. Please re-check the account ID.")
    # Account found
    else:
        transaction_obj = {}
        timestamp = datetime.now().timestamp()
        transaction_obj["transaction_id"] = int(timestamp)
        transaction_obj["date"] = datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y")
        transaction_obj["time"] = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        transaction_obj["description"] = description
        transaction_obj["type"] = "DEBIT"
        transaction_obj["amount"] = round(amount, 2)

        # Add transaction row to account
        contents[account_index]["transactions"].append(transaction_obj)

        # Update balance
        contents[account_index]["balance"] = round(contents[account_index]["balance"] - amount, 2)

        # Add the contents to file
        with open(obj["path"], "w") as new_json_file:
            json.dump(contents, new_json_file, indent=2)
        
        click.echo(click.style("The following transaction was made successfully:", fg="green"))

        # Display transaction for reference
        click.echo(tabulate.tabulate(
            [
                [click.style("Transaction ID", fg="cyan"), transaction_obj["transaction_id"]],
                [click.style("Date", fg="cyan"), transaction_obj["date"]],
                [click.style("Time", fg="cyan"), transaction_obj["time"]],
                [click.style("Description", fg="cyan"), transaction_obj["description"]],
                [click.style("Type", fg="cyan"), click.style(transaction_obj["type"], fg="red")],
                [click.style(f"Amount", fg="cyan"), click.style(f"{obj["currency"]} {transaction_obj["amount"]}", fg="red")],
                [click.style(f"Balance", fg="cyan"), click.style(f"{obj["currency"]} {contents[account_index]["balance"]}", fg="yellow")]

            ],
            tablefmt="grid"
        ))

@click.command()
@click.argument("account_id", type=click.STRING)
@click.argument("transaction_id", type=click.INT)
@click.pass_obj
def delete(obj: dict, account_id: str, transaction_id: int):
    '''
    Remove a transaction from an account.

    ACCOUNT_ID is the unique ID of the account from which you want to
    remove a transaction with a unique TRANSACTION_ID. 
    '''

    # Fetch contents of JSON file
    with open(obj["path"], "r") as json_file:
        contents = json.load(json_file)
    
    # Ensure account with account_id exists
    account_index = -1
    for i, account in enumerate(contents):
        if account["id"] == account_id:
            account_index += i + 1
            break
    
    # Account not found
    if account_index == -1:
        click.echo(f"{click.style('ERROR:', bg="red")} Account not found. Please re-check the account ID.")
    # Account found
    else:
        # Ensure transaction with transaction_id exists
        transaction_index = -1
        for trans_index, transaction in enumerate(contents[account_index]["transactions"]):
            if transaction["transaction_id"] == transaction_id:
                transaction_index += trans_index + 1
                break
        
        # Transaction not found
        if transaction_index == -1:
           click.echo(f"{click.style('ERROR:', bg="red")} Transaction not found. Please re-check the Transaction ID.") 
        # Transaction found
        else:
            # Retreive the transaction to delete
            del_transaction = contents[account_index]["transactions"][transaction_index]

            # Display transaction to delete
            click.echo(click.style("The following transaction will be deleted:", fg="cyan"))
            click.echo(tabulate.tabulate([
                [click.style("Transaction ID", fg="cyan"), del_transaction["transaction_id"]],
                [click.style("Date", fg="cyan"), del_transaction["date"]],
                [click.style("Time", fg="cyan"), del_transaction["time"]],
                [click.style("Description", fg="cyan"), del_transaction["description"]],
                [click.style("Type", fg="cyan"), click.style(del_transaction["type"], fg="red" if del_transaction["type"] == "DEBIT" else "green")],
                [click.style("Amount", fg="cyan"), click.style(del_transaction["amount"], fg="red" if del_transaction["type"] == "DEBIT" else "green")]
            ], tablefmt="grid"))

            # Ask for confirmation
            if click.confirm("Do you want to proceed to delete the above transaction?"):
               
               # Remove transaction object from transactions
               contents[account_index]["transactions"].pop(transaction_index)

               # Update balance
               if del_transaction["type"] == "DEBIT":
                   contents[account_index]["balance"] = round(contents[account_index]["balance"] + del_transaction["amount"], 2)
               if del_transaction["type"] == "CREDIT":
                   contents[account_index]["balance"] = round(contents[account_index]["balance"] - del_transaction["amount"], 2)
            
            
            # Update JSON
            with open(obj["path"], "w") as new_json_file:
                json.dump(contents, new_json_file, ensure_ascii=True, indent=2)

            click.echo(click.style(f"Transaction with ID {del_transaction["transaction_id"]} removed successfully from account with ID {contents[account_index]["id"]}", fg="green")) 
            