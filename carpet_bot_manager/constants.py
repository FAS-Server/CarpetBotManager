import re

from mcdreforged.api.rtext import RColor

Prefix = '!!bot'
Prefix2 = '!!player'
plugin_id = 'carpet_bot_manager'

bot_name_color = {
    True: RColor.green,
    False: RColor.gray
}

dimension_map = {
    'minecraft:overworld': 0,
    'minecraft:the_nether': -1,
    'minecraft:the_end': 1,
    'overworld': 0,
    'the_nether': -1,
    'the_end': 1,
    '0': 0,
    '-1': -1,
    '1': 1
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

action_pattern = re.compile(r'^('
                            r'((use|attack|jump|swapHands) (randomly|once|continuous|((after|interval) \d+)))|'
                            r'(turn (left|right|back))|'
                            r'(move (forward|backward|left|right))|'
                            r'(look (up|down|north|south|east|west|(at -?\d+ \d+ -?\d+)))|'
                            r'(drop(Stack)? (all|continuous|mainhand|offhand|(interval \d+)))|'
                            r'sneak|unsneak|sprint|unsprint|stop|dismount|kill|(hotbar [1-9])|'
                            r'(delay \d+)'
                            r')$')
