'''
Command line entry point for the app (as defined in the toml)
'''
import click
from rich.console import Console
console = Console()

from . import app_helpers as ah


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    ctx.obj = {}


@click.command()
@click.pass_context
@click.argument("task", required=False)
def add(ctx: click.Context, task: str) -> None:
    if not task:
        task = click.prompt(
            "Enter task name or leave blank for",
            default=f"task_{ah.get_next_number()}",
            type=str
        )
    if ah.check_task_exists(task):
        console.print(f"task '{task}' already exists in this board")
        return
    
    description = click.prompt(
        "Enter a description or leave blank for",
        default="No description.",
        type=str)
    ah.add_task(task, description)

    console.print(f"Added task: {task}")


@click.command()
@click.pass_context
@click.argument("task")
def update(ctx: click.Context, task: str) -> None:
    if not ah.check_task_exists(task):
        console.print(f"task '{task}' does not exist")
        return

    console.print("What task attribute should be updated?")
    atr = click.prompt("[1] 'status' or [2] 'description'", type=str)

    if atr == "1" or atr == "status":
        console.print("New status")
        new_atr = click.prompt(ah.get_col_numbers(), type=str)
    else:
        console.print(
            "Current description:",
            ah.get_task_properties(task)["description"]
        )
        new_atr = click.prompt("New description", type=str)

    ah.update_task(task, atr, new_atr)

    # below broken in case of number inputs
    # console.print(f"Updated {atr} to {new_atr}")


@click.command()
@click.pass_context
@click.argument("task")
def see(ctx: click.Context, task: str) -> None:
    if not ah.check_task_exists(task):
        console.print(f"task '{task}' does not exist")
        return

    properties = ah.get_task_properties(task)
    console.print(f"Task: [{properties["number"]}] {properties["name"]}")
    console.print(f"Created at: {properties["date"]}")
    console.print(f"Status: {properties["status"]}")
    console.print(f"Description: {properties["description"]}")


@click.command()
@click.pass_context
@click.argument("task")
def remove(ctx: click.Context, task: str|int) -> None:
    if not ah.check_task_exists(task):
        console.print(f"task '{task}' does not exist")
        return

    ah.remove_task(task)

    console.print(f"Removing task {task}")


@click.command()
@click.pass_context
@click.argument("board", required=False)
def create(ctx: click.Context, board: str) -> None:
    if not board:
        board = click.prompt(
            "Enter board name",
            type=str
        )

    if ah.check_board_exists(board):
        console.print(f"Board {board} already exists")
        return

    console.print(f"Creating board: {board}")
    console.print("""What columns would you like your board to have?""")
    cols = []
    while True:
        col = click.prompt("Column name", default="blank to finish", type=str)
        if col == "blank to finish":
            break
        cols.append(col)

    ah.create_board(board, cols)


@click.command()
@click.pass_context
@click.argument("board")
def activate(ctx: click.Context, board: str) -> None:
    if not ah.check_board_exists(board):
        console.print(f"Board '{board}' doesn't exists")
        return

    ah.activate_board(board)

    console.print(f"Changed to board: {board}")


@click.command()
@click.pass_context
def boards(ctx: click.Context) -> None:
    boards_string = ah.show_boards()

    console.print("All Boards")
    console.print(boards_string)


@click.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    table = ah.create_table()

    console.print(table)


@click.command()
@click.pass_context
@click.argument("board")
def delete(ctx: click.Context, board: str) -> None:
    if not ah.check_board_exists(board):
        console.print(f"Board '{board}' doesn't exists")
        return
    elif board == "default":
        console.print(f"The 'default' board cannot be deleted.")
        return

    confirm = click.confirm(f"Are you sure you want to delete {board}?")
    if confirm:
        ah.delete_board(board)
        console.print(f"{board} deleted")

        # switch to default board
        ah.activate_board("default")


@click.command()
@click.pass_context
@click.argument("test_arg")
def test(ctx: click.Context, test_arg: str) -> None:
    print(ah.check_board_exists(test_arg))


# Tasks
cli.add_command(add) # Create
cli.add_command(see) # Read
cli.add_command(update) # Update
cli.add_command(remove) # Delete

# Boards
cli.add_command(create) # Create
cli.add_command(activate)
cli.add_command(boards)
cli.add_command(show) # Read
# Update - must create a new board
cli.add_command(delete)# Delete

cli.add_command(test)
