setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': None,
    'menu': {
        'uri': __package__,
        'name': '115 TOOL',
        'list': [
            {
                'uri': 'env',
                'name': '설정',
                'list': [
                    {'uri': 'setting', 'name': 'Cookie'},
                ]
            },
            {
                'uri': 'bot_vod',
                'name': 'BOT VOD',
                'list': [
                    {'uri': 'setting', 'name': '설정'},
                    {'uri': 'list', 'name': '목록'},
                ]
            },
            
            {
                'uri': 'manual',
                'name': '매뉴얼',
                'list': [
                    {'uri':'README.md', 'name':'README.md'}
                ]
            },
            {
                'uri': 'log',
                'name': '로그',
            },
        ]
    },
    'setting_menu': None,
    'default_route': 'normal',
}


from plugin import *

P = create_plugin_instance(setting)

try:
    from .mod_bot_vod import ModuleBotVod
    from .mod_env import ModuleEnv
    P.set_module_list([ModuleEnv, ModuleBotVod])
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())

logger = P.logger



