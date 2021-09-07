from typing import Optional

from mcdreforged.api.types import PluginServerInterface, Info

from carpet_bot_manager import cmd_tree
from carpet_bot_manager.BotManager import BotManager, Config

bot_manager: Optional[BotManager] = None


def on_load(server: PluginServerInterface, old):
    global bot_manager
    config = server.load_config_simple(target_class=Config)
    bot_manager = BotManager(server, config)
    cmd_tree.register_command(server, bot_manager)


def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    player = player.lower()
    if bot_manager.check_list(player):
        bot_manager.on_bot_joined(player)


def on_player_left(server: PluginServerInterface, player: str):
    player = player.lower()
    if bot_manager.check_list(player):
        bot_manager.on_bot_left(player)
