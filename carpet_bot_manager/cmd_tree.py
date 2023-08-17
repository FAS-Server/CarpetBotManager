import re
from typing import Union

from mcdreforged.api.command import *
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

    builder = SimpleCommandBuilder()
    builder.command('!!player', lambda src: src.reply(general_help))
    builder.command('!!player <bot> spawn', lambda src, ctx: manager.add_bot(src, ctx['bot']))
    builder.command('!!player <bot> spawn at <x> <y> <z>', lambda src, ctx: manager.add_bot(src, ctx['bot'], ctx))
    builder.command('!!player <bot> spawn at <x> <y> <z> facing <pitch> <yaw>', lambda src, ctx: manager.add_bot(src, ctx['bot'], ctx))
    builder.command('!!player <bot> spawn at <x> <y> <z> facing <pitch> <yaw> in <dim>', lambda src, ctx: manager.add_bot(src, ctx['bot'], ctx))
    builder.command('!!player <bot> <action>', lambda src, ctx: manager.add_action(src, ctx['bot'], ctx['action']))

    builder.command("!!bot", lambda src: src.reply(general_help))
    builder.command("!!bot list", lambda src: manager.list_bots(src))
    builder.command("!!bot list <page>", lambda src, ctx: manager.list_bots(src, ctx['page']))
    builder.command("!!bot spawn <ebot>", lambda src, ctx: manager.spawn_bot(src, ctx['ebot']))
    builder.command("!!bot kill <ebot>", lambda src, ctx: manager.kill_bot(src, ctx['ebot']))
    builder.command("!!bot action", lambda src: src.reply(action_help))
    builder.command("!!bot action <ebot>", lambda src, ctx: manager.list_action(src, ctx['ebot']))
    builder.command("!!bot action <ebot> clear", lambda src, ctx: manager.clear_action(src, ctx['ebot']))
    builder.command("!!bot action <ebot> exec", lambda src, ctx: manager.exec_action(src, ctx['ebot']))
    builder.command("!!bot del <ebot>", lambda src, ctx: manager.del_bot(src, ctx['ebot']))
    builder.command("!!bot info <ebot>", lambda src, ctx: manager.info_bots(src, ctx['ebot']))
    builder.command("!!bot info <ebot> <info>", lambda src, ctx: manager.set_desc(src, ctx['ebot'], ctx['info']))
    builder.command("!!bot desc <ebot>", lambda src, ctx: manager.info_bots(src, ctx['ebot']))
    builder.command("!!bot desc <ebot> <info>", lambda src, ctx: manager.set_desc(src, ctx['ebot'], ctx['info']))


    def get_existed_bot_node(name: str):
        return Text(name).requires(  # suggests 和 requires 共用时表现异常
            lambda src, ctx: manager.check_list(ctx[name]),
            lambda src: tr('command.unknown_bot')
        ).suggests(lambda: manager.bots_in_list)
    def get_actions_node(name: str):
        return GreedyText(name).requires(
                lambda src, ctx: manager.check_list(ctx['bot']),
                lambda src: src.reply(tr('command.unknown_bot'))
            ).requires(
                lambda src, ctx: re.match(constants.action_pattern, ctx[name]) is not None,
                lambda src: src.reply(tr('command.wrong_action'))
            ).requires(
                lambda src, ctx: manager.check_action_limit(ctx['bot']),
                lambda src: src.reply(tr('command.action_too_much'))
            )
    def get_dimension_node(name: str):
        dims = list(constants.dimension_map.keys())
        return Text(name).requires(
                lambda _, ctx: ctx[name] in dims,
                lambda src: src.reply(tr('command.unknown_dimension'))
            )

    builder.arg('ebot', get_existed_bot_node)
    builder.arg('action', get_actions_node)
    builder.arg('dim', get_dimension_node)
    builder.arg('x', Float)
    builder.arg('y', Float)
    builder.arg('z', Float)
    builder.arg('pitch', Float)
    builder.arg('yaw', Float)
    builder.arg('page', Integer)
    builder.arg('info', GreedyText)
    builder.arg('bot', Text)

    builder.register(server)
    server.register_help_message(constants.Prefix, tr('help.summary'))
