from configparser import ConfigParser
from pathlib import Path


config = ConfigParser(allow_no_value=True)

def config_init() -> None:
    # project_dir = Path(__file__).parent
    # config['PATHS'] = {
    #     "db": project_dir / "/data/boards.db",
    #     "sql": f"sqlite:///{project_dir}/data/boards.db"
    # }
    # above doesn't work once cloned from GitHub, need to work out why
    # below has problem where app only works if in project directory
    config['PATHS'] = {
        "db": "src/kanban_app/data/boards.db",
        "sql": "sqlite:///src/kanban_app/data/boards.db"
    }

    config['BOARDS'] = {
        "default": ["Not Started", "In Progress", "Completed"],
        "active": "default"
    }

    with open("config.ini", "w") as f:
        config.write(f)

if __name__ == "__main__":
    pass