import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

if Path("config.json").exists():
    log.info("Found `config.json`, loading constants from it.")
    with open("config.json", "r") as f:
        _CONFIG_JSON = json.load(f)
else:
    with open("config-default.json", "r") as f:
        _CONFIG_JSON = json.load(f)


class JSONGetter(type):
    """
    Implements a custom metaclass used for accessing configuration data by simply accessing class attributes.

    Supports getting configuration from up to two levels
    of nested configuration through `section` and `subsection`.

    Example Usage:
        # config.json
        {
            "bot": {
                "prefixes": {
                    "dm": "",
                    "guild": "!"
                }
            }
        }

        # config.py
        class Prefixes(metaclass=JSONGetter):
            section = "bot"
            subsection = "prefixes"

        # Usage in Python code
        from config import Prefixes
        def get_prefix(bot, message):
            if isinstance(message.channel, PrivateChannel):
                return Prefixes.direct_message
            return Prefixes.guild
    """

    subsection = None

    def __getattr__(cls, name: str):
        name = name.lower()

        try:
            if cls.subsection is not None:
                item = _CONFIG_JSON[cls.section][cls.subsection][name]
                if item == "!ENV":
                    return os.environ[name.upper()]
                else:
                    return item
            else:
                item = _CONFIG_JSON[cls.section][name]
                if item == "!ENV":
                    return os.environ[name.upper()]
                else:
                    return item
        except KeyError:
            dotted_path = ".".join(
                (cls.section, cls.subsection, name)
                if cls.subsection is not None
                else (cls.section, name)
            )
            log.critical(
                f"Tried accessing configuration variable at `{dotted_path}`, but it could not be found."
            )
            raise

    def __getitem__(cls, name: str):
        return cls.__getattr__(name)

    def __iter__(cls):
        """Return generator of key: value pairs of current constants class' config values."""
        for name in cls.__annotations__:
            yield name, getattr(cls, name)


# Environment constants
DEBUG_MODE = True if os.environ["DEBUG"] is not None else False


# JSON constants
class Bot(metaclass=JSONGetter):
    """Bot specific attributes."""

    section = "bot"

    prefix: str
    bot_token: str


class Guild(metaclass=JSONGetter):
    """Attributes specific to the bot's guild."""

    section = "guild"

    guild_id: int


class StaffRoles(metaclass=JSONGetter):
    """Roles from the guild of the bot."""

    section = "guild"
    subsection = "staff_roles"

    admin_role: int
    mod_role: int
    bot_team_role: int


class ClassRoles(metaclass=JSONGetter):
    """Class roles from the bot's guild."""

    section = "guild"
    subsection = "class_roles"

    freshmen: int
    sophomores: int
    juniors: int
    seniors: int
    alumni: int


class Channels(metaclass=JSONGetter):
    """Channels from the guild of the bot."""

    section = "guild"
    subsection = "channels"

    roycemorebot_commands: int
    bot_log: int
    mod_bot_commands: int


class Categories(metaclass=JSONGetter):
    """Categories in the bot's guild."""

    section = "guild"
    subsection = "categories"

    clubs: int


class Emoji(metaclass=JSONGetter):
    """Emojis that the bot will use."""

    section = "style"
    subsection = "emoji"

    ok: str
    warning: str
    no: str
    green_check: str


# Groups
BOT_ADMINS = [StaffRoles.bot_team_role, StaffRoles.admin_role]
MOD_ROLES = [StaffRoles.mod_role, StaffRoles.admin_role]
CLASS_ROLES = [
    ClassRoles.freshmen,
    ClassRoles.sophomores,
    ClassRoles.juniors,
    ClassRoles.seniors,
    ClassRoles.alumni,
]
