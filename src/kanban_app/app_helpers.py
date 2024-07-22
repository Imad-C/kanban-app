import ast
from configparser import ConfigParser
from datetime import datetime
from sqlalchemy import create_engine, select, delete, exc
from sqlalchemy.orm import sessionmaker
from rich.table import Table

from .database import Task, sql_url

config = ConfigParser()
config.read("config.ini")
Session = sessionmaker(bind=create_engine(sql_url, echo=False))

ACTIVE_BOARD = config["BOARDS"]["active"]


def add_task(task: str, description: str) -> None:
    task_ = Task(
        name=task,
        board=ACTIVE_BOARD,
        number=get_next_number(),
        description=description,
        date=str(datetime.now().isoformat(sep=" ", timespec="seconds")),
        status=_get_active_cols()[0] # default to first column
    )
    with Session() as session: 
        session.add(task_)
        session.commit()


def update_task(task: str, atr: str, new_atr: str) -> None:
    # clean atr/new_atr for number inputs
    if atr.isdigit():
        atr = "status" if atr == "1" else "description"
    if new_atr.isdigit():
        new_atr = _get_active_cols()[int(new_atr) - 1]

    task = _get_name_from_number(task) 

    with Session() as session:
        session.query(Task).filter(
            Task.name == task and Task.board == ACTIVE_BOARD
            ).update({atr: new_atr})
        session.commit()


def see_task(task: str):
    task = _get_name_from_number(task)



def remove_task(task: str) -> None:
    task = _get_name_from_number(task)
    stmt = delete(Task).where(
        Task.name == task and Task.board == ACTIVE_BOARD)
    with Session() as session:
        session.execute(stmt) 
        session.commit()


def create_table():
    table = Table(title=f"Board: {ACTIVE_BOARD}")

    board_cols = _get_active_cols()
    for column in board_cols:
        table.add_column(column)

    stmt = select(
        Task.name,
        Task.number,
        Task.status,
        ).where(Task.board == ACTIVE_BOARD)
    with Session() as session:
        tasks = session.execute(stmt)  
        task_lists = _task_dict_filled_blanks(board_cols, tasks)
        for k in task_lists:
            table.add_row(*task_lists[k])
    
    return table


def create_board(board: str, cols: list[str]) -> None:
    config.set("BOARDS", board, str(cols))
    with open('config.ini', 'w') as f:
        config.write(f)


def activate_board(board: str) -> None:
    config.set("BOARDS", "active", board)
    with open('config.ini', 'w') as f:
        config.write(f)


def _get_col_task_dict(cols, tasks):
    col_task_dict = {}
    for col in cols:
        col_task_dict[col] = []
    for task in tasks:
        col_task_dict[task.status].append(f"[{task.number}] " + task.name)
    
    return col_task_dict


def _get_longest_list(lists: list[list]) -> int:
    longest = 0
    for list_ in lists:
        list_len = len(list_)
        if list_len > longest:
            longest = list_len
    return longest


def _task_dict_filled_blanks(columns, tasks):
    col_task_dict = _get_col_task_dict(columns, tasks)
    padded_dict = {}
    for i in range(0, _get_longest_list(col_task_dict.values())):
        padded_dict[i] = []
        for col in columns:
            if len(col_task_dict[col]) - 1 >= i:
                padded_dict[i].append(col_task_dict[col][i])
            else:
                padded_dict[i].append("")
    
    return padded_dict


def _get_active_cols():
    str_list = config.get("BOARDS", ACTIVE_BOARD)
    return ast.literal_eval(str_list)


def get_next_number():
    stmt = select(Task.number).where(Task.board == ACTIVE_BOARD)
    numbers = []
    with Session() as session:
        tasks = session.execute(stmt) 
        for task in tasks:
            numbers.append(task.number)
        
    if len(numbers) == 0:
        return 1

    # below is slow, any better way to do it?
    for number in range(1, max(numbers)+1):
        if number not in numbers:
            return number
        
    return max(numbers)+1


def get_col_numbers():
    prompt_string = ""
    col_number = 1
    cols = _get_active_cols()
    for col in cols:
        prompt_string += f"[{col_number}] '{col}' or "
        col_number += 1
    
    prompt_string = prompt_string[:-4]
    return prompt_string


def get_task_description(task):
    task = _get_name_from_number(task)
    
    stmt = select(
        Task.description,
        ).filter(Task.board == ACTIVE_BOARD).filter(Task.name == task)
    
    with Session() as session:
        description = session.execute(stmt)  
        return description.one()[0]
    

def get_task_properties(task):
    """This is extremely fragile, has to be better way to do this"""
    task = _get_name_from_number(task)
    
    stmt = select(
        Task.name,
        Task.board,
        Task.number,
        Task.description,
        Task.date,
        Task.status
        ).filter(Task.board == ACTIVE_BOARD).filter(Task.name == task)
    
    with Session() as session:
        task = session.execute(stmt)
        task_properties = task.one()
        properties = {
            "name": f"{task_properties[0]}",
            "board": f"{task_properties[1]}",
            "number": f"{task_properties[2]}",
            "description": f"{task_properties[3]}",
            "date": f"{task_properties[4]}",
            "status": f"{task_properties[5]}"
            }  
        return properties
    

def _get_name_from_number(task: str):
    if task.isdigit():
        task = int(task)
        stmt = select(
            Task.name,
            ).filter(Task.board == ACTIVE_BOARD).filter(Task.number == task)
        with Session() as session:
            name = session.execute(stmt)
            try: 
                return name.one()[0]
            except exc.NoResultFound:
                return False 
    else:
        return task
    

def show_boards():
    console_string = """"""
    for key, value in config.items("BOARDS"):
        if key == "active":
            continue
        padding = 20 - len(key)
        string = f"Board: {key}" + " "*padding + f" Columns: {value}"
        console_string += string + "\n"
    
    return console_string[:-1]


def delete_board(board: str):
    # delete all tasks within board
    stmt = delete(Task).where(Task.board == board)
    with Session() as session:
        session.execute(stmt) 
        session.commit()

    # delete board from config
    del config["BOARDS"][board]
    with open('config.ini', 'w') as f:
        config.write(f)


def check_task_exists(task: str) -> bool:
    task = _get_name_from_number(task)
    if not task:
        return False
    # print(task)
    stmt = select(Task).filter(
        Task.board == ACTIVE_BOARD).filter(Task.name == task)
    with Session() as session:
        exists = session.execute(stmt).one_or_none() 
        if exists:
            return True
    return False


def check_board_exists(board: str) -> bool:
    if board in config["BOARDS"].keys():
        return True
    return False