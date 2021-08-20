import re
from typing import Union

from mcdreforged.api.rtext import RAction, RText, RTextBase, RTextList
from mcdreforged.api.types import PluginServerInterface

from carpet_bot_manager import constants

meta = PluginServerInterface.get_instance().get_plugin_metadata(constants.plugin_id)


def tr(translation_key: str, *args, **kwargs):
    server = PluginServerInterface.get_instance()
    plugin_id = meta.id
    return server.tr(
        '{}.{}'.format(plugin_id, translation_key),
        *args, **kwargs
    )


def generate_multiline_help(raw: Union[str, RTextBase]):
    result = RTextList()
    symbol = 0
    for line in raw.splitlines(True):
        match = re.search(r'(?<=§7)' + f'({constants.Prefix}|{constants.Prefix2})' + r'[\S ]*?(?=§)', line)
        if match is not None and symbol != 2:
            result.append(
                RText(line).c(
                    RAction.suggest_command, match.group()
                ).h(
                    tr('click_to_fill', match.group())
                )
            )
            symbol = 1
        else:
            result.append(line)
            if symbol == 1:
                symbol += 1
    return result
