# Carpet Bot manager

[![MCDReforged](https://img.shields.io/badge/dynamic/json?label=MCDReforged&query=dependencies.mcdreforged&url=https%3A%2F%2Fraw.githubusercontent.com%2FFAS-Server%2FCarpetBotManager%2Fmaster%2Fmcdreforged.plugin.json&style=plastic)](https://github.com/Fallen-Breath/MCDReforged)
[![license](https://img.shields.io/github/license/FAS-Server/CarpetBotManager)](https://github.com/FAS-Server/CarpetBotManager/blob/main/LICENSE)
[![build status](https://img.shields.io/github/actions/workflow/status/FAS-Server/CarpetBotManager/package.yml?branch=main&label=build&style=plastic)](https://github.com/FAS-Server/CarpetBotManager/actions)
[![Release](https://img.shields.io/github/v/release/FAS-Server/CarpetBotManager?style=plastic)](https://github.com/FAS-Server/CarpetBotManager/releases/latest)
![total download](https://img.shields.io/github/downloads/FAS-Server/CarpetBotManager/total?label=total%20download&style=plastic)

**中文** | [English](./README_EN.md)

> 一个用于管理 carpet 假人的插件，同时添加了对 [carpet-tis-addition](https://github.com/TISUnion/Carpet-TIS-Addition) 中前后缀的支持

安装后在游戏内输入 `!!bot` 获取帮助信息.

配置文件: 默认存储于 `config/bot_manager/BotManager.json` 中
```json5
{
    "debug": false, // 控制是否在控制台输出debug信息
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
  
    // 控制分页中每页行数
    "page_len": 15,
    // 在生成bot时会添加的前缀, 配合carpet-tis-addition使用
    "name_prefix": "bot_",
    // 在生成bot时会添加的后缀, 配合carpet-tis-addition使用
    "name_suffix": ""
}
```