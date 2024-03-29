from math import ceil
from typing import Dict, Optional

from mcdreforged.api.types import PluginServerInterface, CommandSource, PlayerCommandSource
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RTextList, RText, RColor, RAction
from mcdreforged.api.utils import Serializable
from carpet_bot_manager import constants

from carpet_bot_manager.constants import Prefix
from carpet_bot_manager.bot import Bot, BotConfig

import minecraft_data_api as api

from carpet_bot_manager.messages import tr


def query_player_info(src: PlayerCommandSource) -> tuple:
    # 'data get entity {} Pos'
    # 'data get entity {} Rotation'
    # 'data get entity {} Dimension'
    pos = api.get_player_coordinate(src.player)
    rotation = api.get_player_info(src.player, 'Rotation')
    dim = api.get_player_dimension(src.player)
    return [pos.x, pos.y, pos.z], rotation, dim


class Config(Serializable):
    debug: bool = False
    bots: Dict[str, BotConfig] = {}
    name_prefix: str = ''
    name_suffix: str = ''
    page_len: int = 15


class BotManager:
    def __init__(self, server: PluginServerInterface, config: Config):
        self.bots: Dict[str, Bot] = {}
        self.sever = server
        self.config = config
        self.sever.logger.info(f'debug:{self.config.debug}')
        self.setup()

    @property
    def bots_in_list(self):
        return [i.lower() for i in self.bots]

    def __debug(self, msg: str):
        return self.sever.logger.debug(msg, no_check=self.config.debug)

    @new_thread('bot_manager#setup')
    def setup(self):
        if self.sever.is_server_startup():
            amount, limit, players = api.get_server_player_list()
        else:
            players = []
        self.__debug('do setup')
        self.bots = {}
        for bot_name in self.config.bots:
            self.__debug(f'setup player: {bot_name}')
            bot_conf = self.config.bots.get(bot_name)
            bot_instance = Bot(
                bot_name,
                bot_conf,
                self.sever,
                self.config.name_prefix,
                self.config.name_suffix
            )
            lowered_players = map(lambda s: s.lower(), players)
            self.bots[bot_name] = bot_instance
            if bot_name in lowered_players:
                bot_instance.online = True

    @new_thread('bot#add_bot')
    def add_bot(self, src: CommandSource, bot_name: str, ctx: Optional[dict] = None):
        self.__debug('add_bot@bot_manager')
        bot_name = bot_name.lower()
        bot_name = self.config.name_prefix + bot_name + self.config.name_suffix
        self.__debug('do the bot add')
        conf = {}
        if ctx is None:
            if not isinstance(src, PlayerCommandSource):
                src.reply(tr('command.add_bot_by_console_no_detail'))
                return
            self.__debug('init the bot conf')
            conf['pos'], conf['rotation'], conf['dim'] = query_player_info(src)
        else:
            if 'x' in ctx:
                conf['pos'] = [ctx['x'], ctx['y'], ctx['z']]
            if 'rotation' in ctx:
                conf['rotation'] = [ctx['pitch'], ctx['yaw']]
            if 'dim' in ctx:
                conf['dim'] = constants.dimension_map[ctx['dim']]
        bot_conf = BotConfig.deserialize(conf)
        self.config.bots[bot_name] = bot_conf
        self.__debug(f'save up config:{str(self.config.serialize())}')
        self.sever.save_config_simple(config=self.config)
        self.setup()
        src.reply(tr('bot_list.added', bot_name))

    def del_bot(self, src: CommandSource, bot_name: str):
        bot_name = bot_name.lower()
        self.config.bots.pop(bot_name)
        self.sever.save_config_simple(config=self.config)
        self.setup()
        src.reply(tr('bot_list.deleted', bot_name))

    def add_action(self, src: CommandSource, bot_name: str, action: str):
        bot_name = bot_name.lower()
        self.bots[bot_name].add_action(action)
        src.reply(tr('action.added', bot=bot_name, action=action))
        self.sever.save_config_simple(config=self.config)

    def spawn_bot(self, src: CommandSource, bot_name: str):
        bot_name = bot_name.lower()
        self.bots[bot_name].spawn(src)

    def kill_bot(self, src: CommandSource, bot_name: str):
        bot_name = bot_name.lower()
        self.bots[bot_name].kill(src)

    def list_bots(self, src: CommandSource, page: Optional[int] = 1):
        """
        Reply given page of the player list
        :param src: the CommandSource to reply
        :param page: page num
        :return: None
        """
        page_length = self.config.page_len
        bot_names = list(self.bots.keys())
        max_page = ceil(len(bot_names) / page_length)
        if not 1 <= page <= max_page:
            page = 1
        left = (page - 1) * page_length
        right = min(left + page_length, len(bot_names))
        self.__debug(f'list left:{left}, right: {right}')
        display_names = bot_names[left:right]

        for bot_name in display_names:
            self.bots[bot_name].info(src, with_detail=False)

        # <<<   curr/total   >>>
        link_color = {
            True: RColor.green,
            False: RColor.gray
        }

        left_link: RText
        if page <= 1:
            left_link = RText('<<<', color=link_color[False]).h(tr('bot_list.no_more_page')[::-1])
        else:
            left_link = RText('<<<', color=link_color[True]).h(tr('bot_list.prev_page')) \
                .c(RAction.suggest_command, Prefix + ' list ' + str(page - 1))

        right_link: RText
        if page >= max_page:
            right_link = RText('>>>', color=link_color[False]).h(tr('bot_list.no_more_page'))
        else:
            right_link = RText('>>>', color=link_color[True]).h(tr('bot_list.next_page')) \
                .c(RAction.suggest_command, Prefix + ' list ' + str(page + 1))

        footer = RTextList(
            left_link,
            f'   {page} / {max_page}   ',
            right_link
        )
        if left == right:
            src.reply(tr('bot_list.empty'))
        else:
            src.reply(footer)

    def list_action(self, src, bot_name):
        bot_name = bot_name.lower()
        self.bots[bot_name].list_action(src)

    def clear_action(self, src: CommandSource, bot_name: str):
        bot_name = bot_name.lower()
        self.bots[bot_name].clear_action()
        src.reply(tr('action.cleared', bot=bot_name))
        self.sever.save_config_simple(config=self.config)

    def check_list(self, player: str, for_spawn: Optional[bool] = False) -> bool:
        self.__debug('check_list@bot_manager')
        player = player.lower()
        if not for_spawn:
            in_list = player in self.bots
        else:
            in_list = self.config.name_prefix + player + self.config.name_suffix in self.bots
        self.__debug(f'{player} in list: {"yes" if in_list else "no"}')
        return in_list != for_spawn

    def on_bot_joined(self, player):
        player = player.lower()
        bot = self.bots[player]
        bot.online = True

    def on_bot_left(self, player: str):
        """
        Sync the bot state when player left
        :param player: the player name, empty for server stop
        :return:
        """
        if player == "":
            for bot in self.bots.values():
                bot.online = False
            return
        player = player.lower()
        bot = self.bots[player]
        bot.online = False

    def exec_action(self, src: CommandSource, bot_name: str):
        bot_name = bot_name.lower()
        bot = self.bots[bot_name]
        bot.execute_action(src)

    def set_desc(self, src: CommandSource, bot_name: str, desc: str):
        bot_name = bot_name.lower()
        bot = self.bots[bot_name]
        bot.desc = desc
        self.sever.save_config_simple(config=self.config)
        src.reply(tr('description.changed', bot_name, desc=desc))

    def info_bots(self, src: CommandSource, bot_name: str):
        bot_name = bot_name.lower()
        bot = self.bots[bot_name]
        bot.info(src)

    def check_action_limit(self, bot_name):
        bot_name = bot_name.lower()
        action_length = len(self.bots.get(bot_name).actions)
        return action_length < 10
