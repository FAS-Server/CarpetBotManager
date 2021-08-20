# Carpet Bot manager

[中文](README.md) | **English**

> A bot manage plugin for carpet mod, also support prefix and suffix added by carpet-tis-addition

After added this plugin, type `!!bot` in game to get help message.

Config: Stored in `config/bot_manager/BotManager.json` as default.
```json5
{
    'debug': false, // whether show debug info in console
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
  
    // the number of lines per page, used in list bots
    'page_len': 15,
    // whether remove the prefix 'bot_', design for carpet-tis-addition
    'removePrefix': true,
    // whether remove the suffix '_fake', design for carpet-tis-addition
    'removeSuffix': false  
}
```