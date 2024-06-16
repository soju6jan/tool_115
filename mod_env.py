from .setup import *
import py115
from .util import Util

class ModuleEnv(PluginModuleBase):

    def __init__(self, P):
        super(ModuleEnv, self).__init__(P, name='env', first_menu='setting')
        self.db_default = {
            f'{self.name}_db_version' : '1',
            'env_cookie' : '',
        }

    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'test':
            try:
                P.ModelSetting.set('env_cookie', arg1)
                storage = Util.init_storage(arg1)
                data = storage.list('0')
                ret['json'] = {
                    "ROOT 목록": [x.name for x in data]
                }
            except Exception as e:
                ret['ret'] = 'warning'
                ret['msg'] = str(e)
        return jsonify(ret)
    

