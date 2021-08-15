import re
from typing import Optional

from mcdreforged.api.types import ServerInterface, CommandSource, PlayerCommandSource
from mcdreforged.api.rtext import RText, RTextList, RColor, RAction, RTextTranslation

from bot_manager.constants import dim_convert, Prefix, bot_name_color, dimension_display, dimension_color, \
    action_pattern


class Bot:
    def __init__(self, name, config, server: ServerInterface, no_prefix=True, no_suffix=False):
        self.name: str = name
        self.__full_conf = config
        # self.actions: list = config['actions']
        self.__server = server
        self.__noPrefix = no_prefix
        self.__noSuffix = no_suffix
        self.online = False

    @property
    def desc(self):
        return self.__full_conf['bots'][self.name]['desc']

    @desc.setter
    def desc(self, desc: str):
        self.__full_conf['bots'][self.name]['desc'] = desc

    @property
    def pos(self):
        return self.__full_conf['bots'][self.name]['pos']

    @property
    def rotation(self):
        return self.__full_conf['bots'][self.name]['rotation']

    @property
    def dim(self):
        return self.__full_conf['bots'][self.name]['dim']

    @property
    def actions(self):
        return self.__full_conf['bots'][self.name]['actions']

    @actions.setter
    def actions(self, actions: list[str]):
        self.__full_conf['bots'][self.name]['actions'] = actions


    @property
    def _spawn_name(self):
        output = self.name
        if output.startswith('bot_') and self.__noPrefix:
            output = output[4:]
        if output.endswith('_fake') and self.__noSuffix:
            output = output[:-5]
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

    def spawn(self, src: PlayerCommandSource):
        # 'execute as {} run player {} spawn at {} {} {} facing {} {} in {}'
        src.reply('召唤bot中~')
        self.__server.execute(
            f'execute as {src.player} run '
            f'player {self._spawn_name}'
            f' spawn at {self._pos_string}'
            f' facing {self._rotation_string}'
            f' in {dim_convert.get(self.dim)}'
        )

    def kill(self, src: CommandSource):
        src.reply(f'清理{self.name}中...')
        self.__server.execute(
            f'player {self.name} kill'
        )

    def execute_action(self, src: CommandSource):
        if not self.online:
            if not isinstance(src, PlayerCommandSource):
                src.reply('bot不在线，不能执行动作')
                return
            self.spawn(src)
        cmd_prefix = f'player {self.name} '
        src.reply('执行bot动作中...')
        if len(self.actions) > 0:
            for action in self.actions.copy():
                src.reply('  ' + action)
                self.__server.execute(cmd_prefix + action)
            src.reply('完工力(•̀ω•́)')
        else:
            src.reply('当前bot无预设动作')

    def info(self, src: CommandSource, with_detail: Optional[bool] = True):
        bot_operation = {
            True: RTextList(
                RText('[↓]', color=RColor.yellow).h('点击下线').c(
                    RAction.run_command, f'{Prefix} kill {self.name}'
                ),
                ' ',
                RText('[▶]', color=RColor.blue).h('点击执行预设操作').c(
                    RAction.run_command, f'{Prefix} action {self.name} exec'
                ),
                ' ',
                RText('[x]', color=RColor.red).h('点击删除bot').c(
                    RAction.suggest_command, f'{Prefix} del {self.name}'
                )
            ),
            False: RTextList(
                RText('[↑]', color=RColor.green).h('点击上线').c(
                    RAction.run_command, f'{Prefix} spawn {self.name}'
                ),
                ' ',
                RText('[▶]', color=RColor.blue).h('点击上线并执行预设动作').c(
                    RAction.run_command, f'{Prefix} action {self.name} exec'
                ),
                ' ',
                RText('[x]', color=RColor.red).h('点击删除bot').c(
                    RAction.suggest_command, f'{Prefix} del {self.name}'
                )
            )
        }
        info = RTextList(
            RText(self.name, color=bot_name_color[self.online]).c(RAction.run_command, f'{Prefix} info {self.name}'),
            RText(' [{}] @ '.format(self._pos_display)),
            RTextTranslation(dimension_display[str(self.dim)], color=dimension_color[str(self.dim)]),
            ' ',
            bot_operation.get(self.online)
        )
        src.reply(info)
        if with_detail:
            desc_text = RTextList(
                        RText('描述: ', color=RColor.gray),
                        RText('     '),
                        RText('✐', color=RColor.green).h('点击修改').c(RAction.suggest_command, f'{Prefix} desc {self.name} <desc>'),
                        '\n',
                        RText(self.desc, color=RColor.gray)
                    )
            src.reply(desc_text)
            self.list_action(src)

    def add_action(self, src: CommandSource, action: str):
        if len(self.actions) >= 10:
            src.reply('该bot预设动作数量已达上限!')
            return
        elif not self.check_action(action):
            src.reply('动作格式错误!')
            src.reply('建议使用`/player`指令进行补全, 再将`/`替换为`!!`以规避此问题')
            return
        else:
            action = action.replace('/', '').replace('player ' + self.name, '').strip()
            self.actions.append(action)

    def list_action(self, src: CommandSource):
        action_text = RTextList(
            RText('\n预设动作列表:', color=RColor.gray),
            '\n  - ',
            '\n  - '.join(self.actions),
            '\n  - ',
            RText('[+]', color=RColor.green).h('点击添加动作').c(
                RAction.suggest_command, f'!!player {self.name} <此处填入动作,请确保与`/player`指令一致> '
            ),
            ' ',
            RText('[x]', color=RColor.red).h('点击清空动作').c(
                RAction.suggest_command, f'{Prefix} action {self.name} clear'
            )
        )
        src.reply(action_text)

    def check_action(self, action: str):
        action = action.replace('/', '').replace('player ' + self.name, '').strip()
        if re.match(action_pattern, action):
            return True
        return False

    def clear_action(self):
        self.actions = []

    def stop(self):
        self.__server.execute(f'player {self.name} kill')
