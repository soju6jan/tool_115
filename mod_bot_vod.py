from .model_bot_vod import ModelBotVodItem
from .setup import *
from .task_bot_vod import TaskBotVod


class ModuleBotVod(PluginModuleBase):

    def __init__(self, P):
        super(ModuleBotVod, self).__init__(P, name='bot_vod', first_menu='list')
        self.db_default = {
            f'{self.name}_db_version' : '1',
            f'{self.name}_interval' : '5',
            f'{self.name}_auto_start' : 'False',
            f'{self.name}_target_cid' : '0',
            f'{self.name}_target_folder_format' : '{GENRE}/{TITLE} ({YEAR})',
            f'{self.name}_download_mode' : 'none',
            f'{self.name}_blacklist_genre' : '',
            f'{self.name}_blacklist_program' : '',
            f'{self.name}_whitelist_genre' : '',
            f'{self.name}_whitelist_program' : '',
            f'{self.name}_item_last_list_option': '',
            f'{self.name}_db_delete_day': '30',
            f'{self.name}_db_auto_delete': 'False',
            f'{self.name}_use_notify': 'False',
        }
        self.web_list_model = ModelBotVodItem

    
    #def plugin_load(self):
    def scheduler_function(self):
        func = TaskBotVod.start
        ret = self.start_celery(func)


    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'option':
            mode = arg1
            value = arg2
            value_list = P.ModelSetting.get_list(f'bod_vod_{mode}', '|')
            if value in value_list:
                ret['ret'] = 'warning'
                ret['msg'] = '이미 설정되어 있습니다.'
            else:
                if len(value_list) == 0:
                    P.ModelSetting.set(f'bot_vod_{mode}', value)
                else:
                    P.ModelSetting.set(f'bot_vod_{mode}', P.ModelSetting.get(f'bod_vod_{mode}') + ' | ' + value)
                ret['msg'] = '추가하였습니다'
        elif command == 'request_copy':
            item = ModelBotVodItem.get_by_id(arg1)
            if TaskBotVod.download(item):
                ret['msg'] = "복사하였습니다."
            else:
                ret['ret'] = "warning"
                ret['msg'] = item.status
            return jsonify(ret)
        elif command == 'db_delete':
            if self.web_list_model.delete_by_id(arg1):
                ret['msg'] = '삭제하였습니다.'
            else:
                ret['ret'] = 'warning'
                ret['msg'] = '삭제 실패'
        return jsonify(ret)


    def process_api(self, sub, req):
        ret = {'ret':'success'}
        if sub == 'manual':
            data = req.form.to_dict()
            db_item = self._process_data(data, False)
            db_item = ModelBotVodItem.process_bbs_data(data)
            if db_item:
                ret['ret'] = "already"
            else:
                ret['remote_path'] = P.ModelSetting.get(f'{self.name}_target_cid')
            return jsonify(ret)



    def process_discord_data(self, data):
        self._process_data(data)


    def _process_data(self, data, is_discord=True):
        if is_discord:
            item = ModelBotVodItem.process_discord_data(data)
        else:
            item = ModelBotVodItem.process_bbs_data(data)
        if item is None:
            return
        P.logic.immediately_execute(self.name)
