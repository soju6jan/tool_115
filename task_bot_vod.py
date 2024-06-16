import hashlib
import io

import py115

from .model_bot_vod import ModelBotVodItem
from .setup import *


class TaskBotVod:
    items_cid_map = {}

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
        
        storage = TaskBotVod.init_storage(P.ModelSetting.get('env_cookie'))
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
            storage = TaskBotVod.init_storage(P.ModelSetting.get('env_cookie'))
        cid = TaskBotVod.get_cid(db_item, storage)
        result = storage.request_hash_soju(cid, db_item.filename, db_item.size, db_item.sha1, db_item.id, TaskBotVod.callback_sign_val)
        if result != None and result.is_done:
            db_item.completed_time = datetime.now()
            db_item.set_status('FINISH_DOWNLOAD')

            
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
        
        now = datetime.now()
        now.strftime('%Y-%m-%d')

        folder_format = {
            'GENRE': db_item.meta_genre,
            'TITLE': db_item.meta_title,
            'YEAR': now.strftime('%Y'), 
            'MONTH': now.strftime('%m'), 
            'DAY': now.strftime('%d'), 
        }
        target_format = P.ModelSetting.get('bot_vod_target_folder_format').strip('/')
        target = target_format.format(**folder_format)

        return TaskBotVod.mkdir(storage, target, cid)


    def mkdir(storage, path, current_cid="0", retry=True):
        try:
            tmps = path.strip('/').split('/')
            if len(tmps) == 1 and tmps[0] == "":
                return current_cid
            logger.debug(tmps)
            for current in tmps:
                items = TaskBotVod.get_list_cid(storage, current_cid, True)
                find = TaskBotVod.find_in_cid(storage, items, current)
                if find == None:
                    find = storage.make_dir(current_cid, current)
                current_cid = find.file_id
            return current_cid
        except Exception as e: 
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            logger.error("RETRY!!!")
            if retry:
                time.sleep(5)
                return TaskBotVod.mkdir(storage, path, current_cid, retry=False)

    
    #@pt
    def get_list_cid(storage, target_cid, refresh=False):
        logger.debug(f"115 list: {target_cid}")
        if target_cid not in TaskBotVod.items_cid_map or refresh:
            #items_cid = sorted(self.storage.list(target_cid))
            items_cid = list(storage.list(target_cid))
            TaskBotVod.items_cid_map[target_cid] = items_cid
        return TaskBotVod.items_cid_map[target_cid]

       
    def find_in_cid(storage, parent_items, name, is_dir=True):
        for item in parent_items:
            if item.name == name and is_dir == is_dir:
                return item

    
    
    def init_storage(cookie):
        if cookie == None or cookie == '':
            return
        uid = re.search('UID=([^;]+)', cookie).group(1)
        cid = re.search('CID=([^;]+)', cookie).group(1)
        seid = re.search('SEID=([^;]+)', cookie).group(1)
        cloud = py115.connect(credential={
            'UID':uid, 'CID':cid, 'SEID':seid
        })
        return cloud.storage()