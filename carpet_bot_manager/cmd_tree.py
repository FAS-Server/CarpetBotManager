import re

from mcdreforged.api.command import Literal, Text, GreedyText, Integer, UnknownArgument
from mcdreforged.api.types import PluginServerInterface

from carpet_bot_manager import constants
from carpet_bot_manager.BotManager import BotManager
from carpet_bot_manager.messages import Message


def register_command(server: PluginServerInterface, manager: BotManager):
    existed_bot_node = Text('bot').requires(
        lambda src, ctx: manager.check_list(ctx['bot']),
        lambda src: Message.Command.unknown_bot
    ).suggests(manager.bots_in_list)


    player_node = Literal(constants.Prefix2).runs(
        lambda src: src.reply(Message.Help.general)
    ).on_error(
        UnknownArgument, lambda src: src.reply(Message.Command.unknown_argument), handled=True
    ).runs(lambda src: src.reply(Message.Help.general())).then(
        Text('bot').suggests(manager.bots_in_list).runs(
            lambda src: src.reply(Message.Command.unknown_argument)
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
                lambda src: src.reply(Message.Command.wrong_action)
            ).requires(
                lambda src, ctx: manager.check_action_limit(ctx['bot']),
                lambda src: src.reply(Message.Command.action_too_much)
            ).runs(
                lambda src, ctx: manager.add_action(src, ctx['bot'], ctx['action'])))
    )

    node = Literal(constants.Prefix).runs(lambda src: src.reply(Message.Help.general())).on_error(
        UnknownArgument, lambda src: src.reply(Message.Command.unknown_argument), handled=True
    ).then(
        Literal('list').runs(lambda src: manager.list_bots(src)).then(
            Integer('page').runs(lambda src, ctx: manager.list_bots(src, ctx['page'])))
    ).then(
        Literal('spawn').runs(lambda src: src.reply(Message.Command.bot_name_required)).then(
            existed_bot_node.runs(lambda src, ctx: manager.spawn_bot(src, ctx['bot'])))
    ).then(
        Literal('kill').runs(lambda src: src.reply(Message.Command.bot_name_required))
            .then(
            existed_bot_node.runs(lambda src, ctx: manager.kill_bot(src, ctx['bot'])))
    ).then(
        Literal('action').runs(lambda src: src.reply(Message.Help.action())).then(
            existed_bot_node.runs(lambda src, ctx: manager.list_action(src, ctx['bot'])).then(
                Literal('clear').runs(lambda src, ctx: manager.clear_action(src, ctx['bot']))
            ).then(
                Literal('exec').runs(lambda src, ctx: manager.exec_action(src, ctx['bot']))))
    ).then(
        Literal('del').runs(lambda src: src.reply(Message.Command.bot_name_required)).then(
            existed_bot_node.runs(lambda src, ctx: manager.del_bot(src, ctx['bot']))
        )
    ).then(
        Literal('info').runs(lambda src: src.reply(Message.Command.bot_name_required)).then(
            existed_bot_node.runs(lambda src, ctx: manager.info_bots(src, ctx['bot'])))
    ).then(
        Literal('desc').runs(lambda src: src.reply(Message.Command.bot_name_required)).then(
            existed_bot_node.runs(lambda src, ctx: manager.info_bots(src, ctx['bot'])).then(
                GreedyText('desc').runs(
                    lambda src, ctx: manager.set_desc(src, ctx['bot'], ctx['desc']))))
    )

    server.register_command(node)
    server.register_command(player_node)
    server.register_help_message(constants.Prefix, Message.Help.summary)
