import re

from mcdreforged.api.rtext import RColor

Prefix = '!!bot'
bot_name_color = {
    True: RColor.green,
    False: RColor.gray
}

dimension_display = {
    '0': 'createWorld.customize.preset.overworld',
    '-1': 'advancements.nether.root.title',
    '1': 'advancements.end.root.title'
}

dimension_color = {
    '0': RColor.dark_green,
    '-1': RColor.dark_red,
    '1': RColor.dark_purple
}

dim_convert = {
    0: 'minecraft:overworld',
    -1: 'minecraft:the_nether',
    1: 'minecraft:the_end'
}

default_config = {
    'debug': False,
    'bots': {
        'bot_test': {
            'pos': [0, 128, 0],
            'dim': 0,
            'rotation': [0, 0],
            'actions': [
                'move forward',
                'use interval 15'
            ],
            'desc': 'Nothing here'
        }
    },
    'page_len': 15,
    'removePrefix': True,  # 是否在生成bot时去除其bot_前缀, 配合carpet-tis-addition使用
    'removeSuffix': False  # 是否在生成bot时去除其_fake后缀, 配合carpet-tis-addition使用
}

bot_conf_default = {
    'pos': [0, 0, 0],
    'dim': 0,
    'rotation': [0, 0],
    'actions': [
    ],
    'desc': 'Nothing here'
}

action_pattern = re.compile(r'^('
                            r'((use|attack|jump) (once|continuous|(interval \d+)))|'
                            r'(move (forward|backward|left|right))|'
                            r'(look (up|down|north|south|east|west|(at -?\d+ \d+ -?\d+)))|'
                            r'(drop(Stack)? (all|continuous|mainhand|offhand|(interval \d+)))|'
                            r'dismount|kill|(hotbar [1-9])'
                            r')$')
