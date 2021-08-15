import os
from typing import Optional


from mcdreforged.api.types import PluginServerInterface, Info, PluginCommandSource
from mcdreforged.api.command import Literal, GreedyText, Text, Integer, UnknownArgument
from mcdreforged.api.rtext import RColor, RText, RTextList, RAction

from bot_manager.BotManager import BotManager
from bot_manager.bot import Bot
from bot_manager.ConfigAPI import Config
from bot_manager.constants import Prefix, default_config


bot_manager: Optional[BotManager] = None
source: Optional[PluginCommandSource] = None


def register_command(server: PluginServerInterface, manager: BotManager):
    action = {True: RAction.run_command, False: RAction.suggest_command}
    metadata = server.get_self_metadata()

    def get_command(cmd: str, desc: str, execute: bool = False) -> RTextList:
        return RTextList(
            '\n',
            RText(cmd + ': ', color=RColor.light_purple).c(action[execute], cmd),
            RText(desc, color=RColor.gray)
        )

    available_command = RTextList(
        get_command(Prefix + ' list <page>', '查看已存储bot列表'),
        get_command(Prefix + ' spawn <bot>', '召唤bot'),
        get_command(Prefix + ' kill <bot>', '清除bot'),
        get_command(Prefix + ' action <bot>', '管理bot动作'),
        get_command(Prefix + ' del <bot>', '删除bot'),
        get_command(Prefix + ' info <bot>', '查询bot详细信息'),
        get_command(Prefix + ' desc <bot> <desc>', '修改bot的描述信息为desc'),
        RText('\n将/player命令前缀改为!!以添加bot/添加bot动作')
    )

    root_message = RTextList(
        RText('======'),
        RText(metadata.name, color=RColor.dark_purple),
        RText(' V', color=RColor.yellow),
        RText(metadata.version, color=RColor.yellow),
        RText('======\n'),
        available_command
    )

    action_message = RTextList(
        RText('管理bot能执行的预设动作'),
        get_command(Prefix + ' action <bot>', '展示某个bot的动作列表'),
        get_command(Prefix + ' action <bot> exec', '让指定bot执行动作'),
        get_command(Prefix + ' action <bot> clear', '清空指定bot的动作列表')

    )

    unknown_argument_message = RTextList(
        RText('未知的指令/指令不完整', color=RColor.red),
        RText('\n可用指令如下:'),
        available_command
    )

    player_node = Literal('!!player')\
        .on_error(
        UnknownArgument, lambda src: src.reply(unknown_argument_message), handled=True)\
        .runs(lambda src: src.reply(unknown_argument_message)).then(
        Text('bot').runs(lambda src: src.reply(unknown_argument_message)).then(
            Literal('spawn').runs(
                lambda src, ctx: manager.add_bot(src, ctx['bot'])
            ).then(
                GreedyText('position').runs(
                    lambda src, ctx: manager.add_bot(src, ctx['bot'], ctx['position'])
                )
            )
        ).then(
            GreedyText('action').runs(
                lambda src, ctx: manager.add_action(src, ctx['bot'], ctx['action'])
            )
        )
    )

    node = Literal(Prefix).runs(lambda src: src.reply(root_message)) \
        .on_error(
        UnknownArgument, lambda src: src.reply(unknown_argument_message), handled=True
    ).then(
        Literal('list').runs(lambda src: manager.list_bots(src))
            .then(
            Integer('page').runs(lambda src, ctx: manager.list_bots(src, ctx['page']))
        )
    ).then(
        Literal('spawn').runs(lambda src: manager.list_bots(src, reason='未指定bot名称'))
            .then(
            Text('bot').runs(lambda src, ctx: manager.spawn_bot(src, ctx['bot']))
        )
    ).then(
        Literal('kill').runs(lambda src: manager.list_bots(src, reason='未指定bot名称'))
            .then(
            Text('bot').runs(lambda src, ctx: manager.kill_bot(src, ctx['bot']))
        )
    ).then(
        Literal('action').runs(lambda src: src.reply(action_message))
            .then(
            Text('bot').runs(lambda src, ctx: manager.list_action(src, ctx['bot']))
                .then(
                    Literal('clear').runs(lambda src, ctx: manager.clear_action(src, ctx['bot']))
                ).then(
                    Literal('exec').runs(lambda src, ctx: manager.exec_action(src, ctx['bot']))
            )
        )
    ).then(
        Literal('del').runs(lambda src: manager.list_bots(src, reason='未指定bot名'))
            .then(
            Text('bot').runs(lambda src, ctx: manager.del_bot(src, ctx['bot']))
        )
    ).then(
        Literal('info').runs(lambda src: manager.list_bots(src, reason='未指定bot名'))
            .then(
            Text('bot').runs(lambda src, ctx: manager.info_bots(src, ctx['bot']))
        )
    ).then(
        Literal('desc').runs(lambda src: manager.list_bots(src, reason='未指定bot名'))
            .then(
            Text('bot').runs(lambda src, ctx: manager.info_bots(src, ctx['bot']))
                .then(
                    GreedyText('desc').runs(lambda src, ctx: manager.set_desc(src, ctx['bot'], ctx['desc']))
            )
        )
    )

    server.register_command(node)
    server.register_command(player_node)
    server.register_help_message(Prefix, metadata.description)


def on_load(server: PluginServerInterface, old):
    global bot_manager, source
    source = PluginCommandSource(server)
    config_name = server.get_self_metadata().name
    config_path = os.path.join(server.get_data_folder(), config_name + '.json')
    config = Config(config_path, default_config)
    bot_manager = BotManager(server, config)
    register_command(server, bot_manager)


def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    player = player.lower()
    if bot_manager.check_list(source, player, accurate=True):
        bot_manager.on_bot_joined(player)


def on_player_left(server: PluginServerInterface, player: str):
    player = player.lower()
    if bot_manager.check_list(source, player, accurate=True):
        bot_manager.on_bot_left(player)
