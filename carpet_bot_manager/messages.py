import re
from typing import Union

from mcdreforged.api.rtext import RTextList, RTextBase, RText, RAction
from mcdreforged.api.types import PluginServerInterface

from carpet_bot_manager import constants

meta = PluginServerInterface.get_instance().get_plugin_metadata(constants.plugin_id)


def _tr(translation_key: str, *args, **kwargs):
    server = PluginServerInterface.get_instance()
    plugin_id = meta.id
    return server.tr(
        '{}.{}'.format(plugin_id, translation_key),
        *args, **kwargs
    )


def _convent_command(raw: Union[str, RTextBase]):
    result = RTextList()
    symbol = 0
    for line in raw.splitlines(True):
        match = re.search(r'(?<=§7)' + f'({constants.Prefix}|{constants.Prefix2})' + r'[\S ]*?(?=§)', line)
        if match is not None and symbol != 2:
            result.append(
                RText(line).c(
                    RAction.suggest_command, match.group()
                ).h(
                    _tr('click_to_fill', match.group())
                )
            )
            symbol = 1
        else:
            result.append(line)
            if symbol == 1:
                symbol += 1
    return result


class Message:
    class Action:
        title = _tr('action.title')
        executing = _tr('action.executing')
        execute_done = _tr('action.execute_done')

        @staticmethod
        def added(bot, action):
            return _tr('action.added', bot=bot, action=action)

        @staticmethod
        def cleared(bot):
            return _tr('action.cleared', bot)

        @staticmethod
        def empty(bot):
            return _tr('action.empty', bot)

    class BotList:
        prev_page = _tr('bot_list.prev_page')
        next_page = _tr('bot_list.next_page')
        no_more_page = _tr('bot_list.no_more_page')
        empty = _tr('bot_list.empty')

        @staticmethod
        def deleted(bot: str):
            return _tr('bot_list.deleted', bot)

        @staticmethod
        def pre_spawn(bot: str):
            return _tr('bot_list.pre_spawn', bot)

        @staticmethod
        def pre_kill(bot: str):
            return _tr('bot_list.pre_kill', bot)


    class Description:
        title = _tr('description.title')
        default = _tr('description.default')

        @staticmethod
        def changed(bot: str, desc: str):
            return _tr('description.changed', bot=bot, desc=desc)

    class Help:
        unfinished_function = _tr('help.unfinished_function')

        @staticmethod
        def general():
            raw_text = _tr(
                'help.general', name=meta.name,
                version=meta.version, prefix=constants.Prefix,
                prefix2=constants.Prefix2
            )
            return _convent_command(raw_text)

        @staticmethod
        def action():
            raw_text = _tr('help.action', prefix=constants.Prefix, prefix2=constants.Prefix2)
            return _convent_command(raw_text)

        summary = _tr('help.summary')

    class Command:
        wrong_action = _tr('command.wrong_action')
        action_too_much = _tr('command.action_too_much')
        add_bot_by_console_no_detail = _tr('command.add_bot_by_console_no_detail')
        unknown_argument = _tr('command.unknown_argument')
        unknown_bot = _tr('command.unknown_bot')
        duplicated_bot = _tr('command.duplicated_bot')
        bot_name_required = _tr('command.bot_name_required')
        unfinished = _tr('command.unfinished')
        spawn_by_console = _tr('command.spawn_by_console')

    class Button:
        action_clear = _tr('button.action_clear')
        action_add = _tr('button.action_add')
        spawn = _tr('button.spawn')
        kill = _tr('button.kill')
        exec = _tr('button.exec')
        delete = _tr('button.delete')
        spawn_exec = _tr('button.spawn_exec')
        edit = _tr('button.edit')
