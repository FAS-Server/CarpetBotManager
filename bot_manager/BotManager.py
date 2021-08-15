from typing import Optional

from mcdreforged.api.types import PluginServerInterface, CommandSource, PlayerCommandSource
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RTextList, RText, RColor, RAction

from bot_manager.constants import Prefix, bot_conf_default
from bot_manager.ConfigAPI import Config
from bot_manager.bot import Bot

import minecraft_data_api as api


def query_player_info(src: PlayerCommandSource) -> tuple:
    # 'data get entity {} Pos'
    # 'data get entity {} Rotation'
    # 'data get entity {} Dimension'
    pos = api.get_player_coordinate(src.player)
    rotation = api.get_player_info(src.player, 'Rotation')
    dim = api.get_player_dimension(src.player)
    return [pos.x, pos.y, pos.z], rotation, dim


class BotManager:
    def __init__(self, server: PluginServerInterface, config: Config):
        self.bots: dict[str, Bot] = {}
        self.sever = server
        self.config = config
        self.sever.logger.info(f'debug:{self.config.get("debug")}')
        self.setup()

    def __debug(self, msg: str):
        return self.sever.logger.debug(msg, no_check=self.config.get('debug'))
        # return self.sever.logger.info(msg)

    @new_thread('bot_manager#setup')
    def setup(self):
        if self.sever.is_server_startup():
            amount, limit, players = api.get_server_player_list()
        else:
            players = []
        self.__debug('do setup')
        self.bots = {}
        for bot_name in self.config.get('bots'):
            self.__debug(f'setup player: {bot_name}')
            bot_instance = Bot(
                bot_name,
                self.config,
                self.sever,
                self.config.get('removePrefix'),
                self.config.get('removeSuffix')
            )
            lowered_players = [i.lower() for i in players]
            self.bots[bot_name] = bot_instance
            if bot_name in lowered_players:
                bot_instance.online = True

    @new_thread('bot#add_bot')
    def add_bot(self, src: CommandSource, bot_name: str, position: Optional[str] = None):
        self.__debug('add_bot@bot_manager')
        bot_name = bot_name.lower()
        if self.check_list(src, bot_name, accurate=False, should_in_list=False):
            return
        if position is not None:
            src.reply('未完工...快去催他写awa')  # TODO 接收玩家指定的位置参数
        else:
            if not isinstance(src, PlayerCommandSource):
                src.reply('运维鬼才你来啦= =|')
            else:
                if self.config.get('removePrefix'):
                    bot_name = 'bot_' + bot_name
                if self.config.get('removeSuffix'):
                    bot_name = bot_name + '_fake'
                self.__debug('do the bot add')
                bot_conf = bot_conf_default
                self.__debug('init the bot conf')
                bot_conf['pos'], bot_conf['rotation'], bot_conf['dim'] = query_player_info(src)
                self.__debug(f'loaded conf:{str(bot_conf)}')
                self.config['bots'][bot_name] = bot_conf
                self.config.save()
                self.bots[bot_name] = Bot(bot_name, self.config, src.get_server())

    def del_bot(self, src: CommandSource, bot_name: str):
        if self.check_list(src, bot_name, accurate=True):
            self.config['bots'].pop(bot_name)
            self.config.save()
            self.setup()
            src.reply(f'已删除 {bot_name}')

    def add_action(self, src: CommandSource, bot_name: str, action: str):
        bot_name = bot_name.lower()
        if self.check_list(src, bot_name, accurate=True):
            self.bots[bot_name].add_action(src, action)
            self.config.save()

    def spawn_bot(self, src: CommandSource, bot_name: str):
        if self.check_list(src, bot_name, accurate=True):
            if isinstance(src, PlayerCommandSource):
                self.bots[bot_name].spawn(src)
                return
            src.reply('不允许从后台召唤bot哦~')

    def kill_bot(self, src: CommandSource, bot_name: str):
        if self.check_list(src, bot_name, accurate=True):
            self.bots[bot_name].kill(src)

    def list_bots(self, src: CommandSource, page: Optional[int] = 1, reason: Optional[str] = None):
        if reason is not None:
            src.reply(reason + ' bot 列表如下:')
        page_length = self.config.get('page_len')
        bot_names = [i for i in self.bots]
        self.__debug(f'total list size: {len(bot_names)}')
        max_page = 1 + int(len(bot_names)/page_length)
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
            left_link = RText('<<<', color=link_color[False]).h('这里不能点~'[::-1])
        else:
            left_link = RText('<<<', color=link_color[True]).h('上一页')\
                .c(RAction.run_command, Prefix + ' list page ' + str(page - 1))

        right_link: RText
        if page >= max_page:
            right_link = RText('>>>', color=link_color[False]).h('这里不能点~')
        else:
            right_link = RText('>>>', color=link_color[True]).h('下一页') \
                .c(RAction.run_command, Prefix + ' list page ' + str(page + 1))

        footer = RTextList(
            left_link,
            f'   {page} / {max_page}   ',
            right_link
        )
        if left == right:
            src.reply('这里看起来空荡荡的')
        else:
            src.reply(footer)

    def list_action(self, src, bot_name):
        if self.check_list(src, bot_name, accurate=True):
            self.bots[bot_name].list_action(src)

    def clear_action(self, src, bot_name):
        if self.check_list(src, bot_name, accurate=True):
            self.bots[bot_name].clear_action()
            self.config.save()

    def check_list(self, src: CommandSource, player: str,
                   accurate: Optional[bool] = False,
                   should_in_list: Optional[bool] = True) -> bool:
        self.__debug('check_list@bot_manager')
        in_list = False
        if accurate and player in self.bots:
            in_list = True
        elif not accurate:
            if self.config.get('removePrefix') and 'bot_' + player in self.bots:
                in_list = True
            if self.config.get('removeSuffix') and player + '_fake' in self.bots:
                in_list = True
        if should_in_list and not in_list:
            src.reply(f'{player}未在bot名单中!')
        elif not should_in_list and in_list:
            src.reply(f'{player}已存在!')
        self.__debug(f'{player} in list: {"yes" if in_list else "no"}')
        return in_list

    def on_bot_joined(self, player):
        bot = self.bots[player]
        bot.online = True

    def on_bot_left(self, player):
        bot = self.bots[player]
        bot.online = False

    def exec_action(self, src: CommandSource, bot_name: str):
        if self.check_list(src, bot_name, accurate=True):
            bot = self.bots[bot_name]
            bot.execute_action(src)

    def set_desc(self, src: CommandSource, bot_name: str, desc: str):
        if self.check_list(src, bot_name, accurate=True):
            bot = self.bots[bot_name]
            bot.desc = desc
            self.config.save()
            src.reply(f'{bot_name}的描述信息已经被设置为{desc}')

    def info_bots(self, src: CommandSource, bot_name: str):
        if self.check_list(src, bot_name, accurate=True):
            bot = self.bots[bot_name]
            bot.info(src)
