# FAS Bot manager

**中文** | [English](./README_EN.md)

> 一个用于管理 carpet 假人的插件，同时添加了对 carpet-tis-addition 中前后缀的支持

安装后在游戏内输入 `!!bot` 获取帮助信息.

配置文件: 默认存储于 `config/bot_manager/BotManager.json` 中
```json5
{
    'debug': false, // 控制是否在控制台输出debug信息
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
  
    // 控制分页中每页行数
    'page_len': 15,
    // 是否在生成bot时去除其bot_前缀, 配合carpet-tis-addition使用
    'removePrefix': true,
    // 是否在生成bot时去除其_fake后缀, 配合carpet-tis-addition使用
    'removeSuffix': false  
}
```