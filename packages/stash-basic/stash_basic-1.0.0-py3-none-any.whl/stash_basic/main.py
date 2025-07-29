import click
from stash_basic import accounts_handler, transactions_handler, initializer, utils

# -------------------- MAIN CLI GROUP --------------------
@click.group()
@click.pass_context
def cli(ctx):
    '''The CLI tool for recording all your money related transactions!'''
    ctx.ensure_object(dict)
    ctx.obj.update(utils.load_config())

# Add sub-commands to the main cli group
cli.add_command(initializer.init)

# -------------------- ACCOUNTS GROUP --------------------
@cli.group()
@click.pass_context
def accounts(ctx):
    '''
    Utilities to manage accounts.
    '''
    ctx.ensure_object(dict)
    config = utils.load_config()

    if not config:
        raise click.UsageError("No configuration found – run `stash init` first.")

# Add sub-commands to accounts group
accounts.add_command(accounts_handler.add)
accounts.add_command(accounts_handler.delete)
accounts.add_command(accounts_handler.summary)
accounts.add_command(accounts_handler.statement)

# -------------------- TRANSACTIONS GROUP --------------------
@cli.group()
@click.pass_context
def transactions(ctx):
    '''
    Utilities to manage transactions.
    '''
    ctx.ensure_object(dict)
    config = utils.load_config()

    if not config:
        raise click.UsageError("No configuration found – run `stash init` first.")
    
# Add sub-commands to transactions group
transactions.add_command(transactions_handler.credit)
transactions.add_command(transactions_handler.debit)
transactions.add_command(transactions_handler.delete)