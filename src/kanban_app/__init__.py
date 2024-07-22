'''Initialise config and database when run for the first time'''

from pathlib import Path

if not Path("config.ini").is_file(): # default config if non exists
    from . import config
    config.config_init()

    from configparser import ConfigParser
    config = ConfigParser()
    config.read("config.ini")

    # below requires config to exists first, so run after config
    from .database import database_init
    database_init() 