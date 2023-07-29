# Carpet Bot manager

[![MCDReforged](https://img.shields.io/badge/dynamic/json?label=MCDReforged&query=dependencies.mcdreforged&url=https%3A%2F%2Fraw.githubusercontent.com%2FFAS-Server%2FCarpetBotManager%2Fmaster%2Fmcdreforged.plugin.json&style=plastic)](https://github.com/Fallen-Breath/MCDReforged)
[![license](https://img.shields.io/github/license/FAS-Server/CarpetBotManager)](https://github.com/FAS-Server/CarpetBotManager/blob/main/LICENSE)
[![build status](https://img.shields.io/github/actions/workflow/status/FAS-Server/CarpetBotManager/ci.yml?branch=main&label=build&style=plastic)](https://github.com/FAS-Server/CarpetBotManager/actions)
[![Release](https://img.shields.io/github/v/release/FAS-Server/CarpetBotManager?style=plastic)](https://github.com/FAS-Server/CarpetBotManager/releases/latest)
![total download](https://img.shields.io/github/downloads/FAS-Server/CarpetBotManager/total?label=total%20download&style=plastic)

[中文](README.md) | **English**

> A bot manage plugin for carpet mod, also support prefix and suffix added by [carpet-tis-addition](https://github.com/TISUnion/Carpet-TIS-Addition)

After added this plugin, type `!!bot` in game to get help message.

Config: Stored in `config/bot_manager/BotManager.json` as default.
```json5
{
    "debug": false, // whether show debug info in console
    "bots": {
        "bot_test": {
            "pos": [0, 128, 0],
            "dim": 0,
            "rotation": [0, 0],
            "actions": [
                "move forward",
                "use interval 15"
            ],
            "desc": "Nothing here"
        }
    },
  
    // the number of lines per page, used in list bots
    "page_len": 15,
    // prefix which will be add before bot name, design for carpet-tis-addition
    "name_prefix": "bot_",
    // suffix which will be add after bot name, design for carpet-tis-addition
    "name_suffix": ""
}
```