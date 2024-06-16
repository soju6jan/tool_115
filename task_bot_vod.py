from .setup import *
from .model_bot_vod import ModelBotVodItem
from .util import Util

import hashlib
import io


class TaskBotVod:

    @staticmethod
    @F.celery.task
    def start():
        try:
            import gds_tool
            PP = F.PluginManager.get_plugin_instance('gds_tool')
            if PP == None:
                raise Exception()
        except:
            logger.error('gds_tool not installed!!')
            logger.error('gds_tool not installed!!')
            logger.error('gds_tool not installed!!')
            raise Exception()
        
        #while True:
        
        storage = Util.init_storage(P.ModelSetting.get('env_cookie'))
        vod_blacklist_genre = P.ModelSetting.get_list('bot_vod_blacklist_genre', '|')
        vod_blacklist_program = P.ModelSetting.get_list('bot_vod_blacklist_program', '|')
        vod_whitelist_genre = P.ModelSetting.get_list('bot_vod_whitelist_genre', '|')
        vod_whitelist_program = P.ModelSetting.get_list('bot_vod_whitelist_program', '|')
        
        items = ModelBotVodItem.get_list_not_finished()
        for item in items:
            try:
                logger.debug(item)
                bot_vod_download_mode = P.ModelSetting.get('bot_vod_download_mode')
                if bot_vod_download_mode == 'none':
                    item.log += '다운로드 안함'
                    item.set_status('FINISH_CONDITION')
                    continue
                if bot_vod_download_mode == 'blacklist':
                    flag_download = True
                    if item.meta_title is None:
                        item.log += '메타 정보 없음. 다운:On'
                        TaskBotVod.download(item, storage=storage)
                        continue
                    if len(vod_blacklist_genre) > 0 and item.meta_genre in vod_blacklist_genre:
                        flag_download = False
                        item.log += '제외 장르. 다운:Off'
                    if flag_download:
                        for program_name in vod_blacklist_program:
                            if item.meta_title.replace(' ', '').find(program_name.replace(' ', '')) != -1:
                                flag_download = False
                                item.log += '제외 프로그램. 다운:Off'
                                break
                    if flag_download:
                        item.log += '블랙리스트 모드. 다운:On'
                else:
                    flag_download = False
                    if item.meta_title is None:
                        item.log += '메타 정보 없음. 다운:Off'
                        item.set_status('FINISH_CONDITION')
                        continue
                
                    if len(vod_whitelist_genre) > 0 and item.meta_genre in vod_whitelist_genre:
                        flag_download = True
                        item.log += '포함 장르. 다운:On'
                    if flag_download == False:
                        for program_name in vod_whitelist_program:
                            if item.meta_title.replace(' ', '').find(program_name.replace(' ', '')) != -1:
                                flag_download = True
                                item.log += '포함 프로그램. 다운:On'
                                break
                    if not flag_download:
                        item.log += '화이트리스트 모드. 다운:Off'

                if flag_download:
                    TaskBotVod.download(item, storage=storage)
                else:
                    item.set_status('FINISH_CONDITION')
    
            except Exception as e: 
                logger.error(f"Exception:{str(e)}")
                logger.error(traceback.format_exc())
            


    @staticmethod
    def download(db_item, storage=None):
        logger.info(db_item)
        db_item.request_time = datetime.now()
        if storage == None:
            storage = Util.init_storage(P.ModelSetting.get('env_cookie'))
        cid = TaskBotVod.get_cid(db_item, storage)
        result = storage.request_hash_soju(cid, db_item.filename, db_item.size, db_item.sha1, db_item.id, TaskBotVod.callback_sign_val)
        if result != None and result.is_done:
            db_item.completed_time = datetime.now()
            db_item.set_status('FINISH_DOWNLOAD')

            #if P.ModelSetting.get_bool(f'{self.name}_use_notify'):
            #    from tool import ToolNotify
            #    msg = f'115 BOT VOD 수신\n파일: {item.filename}'
            #    ToolNotify.send_message(msg, image_url=item.meta_poster, message_id=f"{P.package_name}_{self.name}")

            
            return True
        if result != None and result.is_done == False:
            logger.info(f"NOT EXIST ON 115 : {db_item.id}")
            db_item.download_count += 1
            if db_item.download_count > 10:
                db_item.set_status('FINISH_ALLOWED_EXCEEDED')
            else:
                db_item.set_status('FAIL')
        return False

        
    def callback_sign_val(db_id, check_range):
        try:
            logger.info(f"CHECK_VAL: {db_id} {check_range}")
            db_item = ModelBotVodItem.get_by_id(db_id)
            from gds_tool import SSGDrive
            data = SSGDrive.download_range(db_item.googleid, check_range)
            return hashlib.sha1(data).hexdigest().upper()
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            



    def get_cid(db_item, storage):
        cid = P.ModelSetting.get('bot_vod_target_cid')
        
        #form = P.ModelSetting.get('bot_vod_target_folder_format')
        #if form.strip() == "":
        #    return cid
        #else:


        
        return cid
    



