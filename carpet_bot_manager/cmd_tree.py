import re
from typing import Union

from mcdreforged.api.command import Literal, Text, GreedyText, Integer, UnknownArgument
from mcdreforged.api.types import PluginServerInterface

from carpet_bot_manager import constants
from carpet_bot_manager.BotManager import BotManager
from carpet_bot_manager.messages import generate_multiline_help, tr


def register_command(server: PluginServerInterface, manager: BotManager):
    meta = server.get_self_metadata()
    general_help = generate_multiline_help(tr(
        'help.general', name=meta.name,
        version=meta.version, prefix=constants.Prefix,
        prefix2=constants.Prefix2))

    action_help = generate_multiline_help(tr('help.action', prefix=constants.Prefix, prefix2=constants.Prefix2))

    def get_existed_bot_node():
        return Text('bot').requires(  # suggests 和 requires 共用时表现异常
            lambda src, ctx: manager.check_list(ctx['bot']),
            lambda src: tr('command.unknown_bot')
        ).suggests(lambda: manager.bots_in_list)

    def bot_name_required_node(cmd: Union[str, set]):
        return Literal(cmd).runs(lambda src: src.reply(tr('command.bot_name_required')))

    player_node = Literal(constants.Prefix2).runs(
        lambda src: src.reply(general_help)
    ).on_error(
        UnknownArgument, lambda src: src.reply(tr('command.unknown_argument')), handled=True
    ).then(
        Text('bot').suggests(lambda: manager.bots_in_list).runs(
            lambda src: src.reply(tr('command.unknown_argument'))
        ).then(
            Literal('spawn').requires(
                lambda src, ctx: manager.check_list(ctx['bot'], for_spawn=True)
            ).runs(
                lambda src, ctx: manager.add_bot(src, ctx['bot'])
            ).then(
                GreedyText('position').runs(
                    lambda src, ctx: manager.add_bot(src, ctx['bot'], ctx['position'])))
        ).then(
            GreedyText('action').requires(
                lambda src, ctx: re.match(constants.action_pattern, ctx['action']) is not None,
                lambda src: src.reply(tr('command.wrong_action'))
            ).requires(
                lambda src, ctx: manager.check_action_limit(ctx['bot']),
                lambda src: src.reply(tr('command.action_too_much'))
            ).runs(
                lambda src, ctx: manager.add_action(src, ctx['bot'], ctx['action'])))
    )

    node = Literal(constants.Prefix).runs(lambda src: src.reply(general_help)).on_error(
        UnknownArgument, lambda src: src.reply(tr('command.unknown_argument')), handled=True
    ).then(
        Literal('list').runs(lambda src: manager.list_bots(src)).then(
            Integer('page').runs(lambda src, ctx: manager.list_bots(src, ctx['page'])))
    ).then(
        bot_name_required_node('spawn').then(
            get_existed_bot_node().runs(lambda src, ctx: manager.spawn_bot(src, ctx['bot'])))
    ).then(
        bot_name_required_node('kill').then(
            get_existed_bot_node().runs(lambda src, ctx: manager.kill_bot(src, ctx['bot'])))
    ).then(
        Literal('action').runs(lambda src: src.reply(action_help)).then(
            get_existed_bot_node().runs(lambda src, ctx: manager.list_action(src, ctx['bot'])).then(
                Literal('clear').runs(lambda src, ctx: manager.clear_action(src, ctx['bot']))
            ).then(
                Literal('exec').runs(lambda src, ctx: manager.exec_action(src, ctx['bot']))))
    ).then(
        bot_name_required_node('del').then(
            get_existed_bot_node().runs(lambda src, ctx: manager.del_bot(src, ctx['bot']))
        )
    ).then(
        bot_name_required_node({'info', 'desc'}).then(
            get_existed_bot_node().runs(lambda src, ctx: manager.info_bots(src, ctx['bot'])).then(
                GreedyText('desc').runs(
                    lambda src, ctx: manager.set_desc(src, ctx['bot'], ctx['desc']))
            )
        )
    )

    if manager.config.debug:
        node = node.then(
            Literal('debug').runs(lambda src: src.reply(manager.bots_in_list)).then(
                Literal('bots_in_list').runs(lambda src: src.reply(manager.bots_in_list))
            )
        )

    server.register_command(node)
    server.register_command(player_node)
    server.register_help_message(constants.Prefix, tr('help.summary'))
