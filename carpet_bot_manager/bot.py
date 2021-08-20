from typing import List, Optional

from mcdreforged.api.types import ServerInterface, CommandSource, PlayerCommandSource
from mcdreforged.api.rtext import RText, RTextList, RColor, RAction, RTextTranslation
from mcdreforged.api.utils import Serializable

from carpet_bot_manager import constants
from carpet_bot_manager.messages import Message


class BotConfig(Serializable):
    desc: str = Message.Description.default
    pos: List[int] = [0, 0, 0]
    dim: int = 0
    rotation: List[int] = [0, 0]
    actions: List[str] = []


class Bot:
    def __init__(self, name, config: BotConfig, server: ServerInterface, name_prefix='bot_', name_suffix=''):
        self.name: str = name
        self._conf = config
        self.__server = server
        self._name_prefix = name_prefix
        self._name_suffix = name_suffix
        self.online = False

    @property
    def desc(self):
        return self._conf.desc

    @desc.setter
    def desc(self, desc: str):
        self._conf.desc = desc

    @property
    def pos(self):
        return self._conf.pos

    @property
    def rotation(self):
        return self._conf.rotation

    @property
    def dim(self):
        return self._conf.dim

    @property
    def actions(self):
        return self._conf.actions

    @actions.setter
    def actions(self, actions):
        self._conf.actions = actions

    @property
    def _spawn_name(self):
        output = self.name
        if self._name_prefix != '' and output.startswith(self._name_prefix):
            output = output[len(self._name_prefix):]
        if self._name_suffix != '' and output.startswith(self._name_suffix):
            output = output[: 0 - len(self._name_suffix)]
        return output

    @property
    def _pos_string(self):
        return ' '.join(map(str, self.pos))

    @property
    def _pos_display(self):
        return ','.join(map(str, map(int, self.pos)))

    @property
    def _rotation_string(self):
        return ' '.join(map(str, self.rotation))

    def spawn(self, src: CommandSource):
        # 'execute as {} run player {} spawn at {} {} {} facing {} {} in {}'
        if not isinstance(src, PlayerCommandSource):
            src.reply(Message.Command.spawn_by_console)
            return
        src.reply(Message.BotList.pre_spawn(self.name))
        self.__server.execute(
            f'execute as {src.player} run '
            f'player {self._spawn_name}'
            f' spawn at {self._pos_string}'
            f' facing {self._rotation_string}'
            f' in {constants.dim_convert.get(self.dim)}'
        )

    def kill(self, src: CommandSource):
        src.reply(Message.BotList.pre_kill(self.name))
        self.__server.execute(
            f'player {self.name} kill'
        )

    def execute_action(self, src: CommandSource):
        if not self.online:
            self.spawn(src)
        cmd_prefix = f'player {self.name} '
        src.reply(Message.Action.executing)
        if len(self.actions) > 0:
            for action in self.actions.copy():
                src.reply('  ' + action)
                self.__server.execute(cmd_prefix + action)
            src.reply(Message.Action.execute_done)
        else:
            src.reply(Message.Action.empty(self.name))

    def info(self, src: CommandSource, with_detail: Optional[bool] = True):
        bot_operation = {
            True: RTextList(
                RText('[↓]', color=RColor.yellow).h(Message.Button.kill).c(
                    RAction.run_command, f'{constants.Prefix} kill {self.name}'
                ),
                ' ',
                RText('[▶]', color=RColor.blue).h(Message.Button.exec).c(
                    RAction.run_command, f'{constants.Prefix} action {self.name} exec'
                ),
                ' ',
                RText('[x]', color=RColor.red).h(Message.Button.delete).c(
                    RAction.suggest_command, f'{constants.Prefix} del {self.name}'
                )
            ),
            False: RTextList(
                RText('[↑]', color=RColor.green).h(Message.Button.spawn).c(
                    RAction.run_command, f'{constants.Prefix} spawn {self.name}'
                ),
                ' ',
                RText('[▶]', color=RColor.blue).h(Message.Button.spawn_exec).c(
                    RAction.run_command, f'{constants.Prefix} action {self.name} exec'
                ),
                ' ',
                RText('[x]', color=RColor.red).h(Message.Button.delete).c(
                    RAction.suggest_command, f'{constants.Prefix} del {self.name}'
                )
            )
        }
        info = RTextList(
            RText(self.name, color=constants.bot_name_color[self.online]).c(
                RAction.run_command, f'{constants.Prefix} info {self.name}'),
            RText(' [{}] @ '.format(self._pos_display)),
            RTextTranslation(constants.dimension_display[str(self.dim)], color=constants.dimension_color[str(self.dim)]),
            ' ',
            bot_operation.get(self.online)
        )
        src.reply(info)
        if with_detail:
            desc_text = RTextList(
                RText(Message.Description.title, color=RColor.gray),
                RText(':     '),
                RText('✐', color=RColor.green).h(Message.Button.edit).c(
                    RAction.suggest_command, f'{constants.Prefix} desc {self.name} <desc>'
                ),
                '\n',
                RText(self.desc, color=RColor.gray)
            )
            src.reply(desc_text)
            self.list_action(src)

    def add_action(self, action: str):
        self.actions.append(action)

    def list_action(self, src: CommandSource):
        action_text = RTextList(
            RText(Message.Action.title, color=RColor.gray),
            '\n  - ',
            '\n  - '.join(self.actions),
            '\n  - ',
            RText('[+]', color=RColor.green).h(Message.Button.action_add).c(
                RAction.suggest_command, f'!!player {self.name} <action> '
            ),
            ' ',
            RText('[x]', color=RColor.red).h(Message.Button.action_clear).c(
                RAction.suggest_command, f'{constants.Prefix} action {self.name} clear'
            )
        )
        src.reply(action_text)


    def clear_action(self):
        self.actions = []

    def stop(self):
        self.__server.execute(f'player {self.name} kill')
