from .setup import *
import py115

class Util:
    
    @classmethod
    def init_storage(self, cookie):
        uid = re.search('UID=([^;]+)', cookie).group(1)
        cid = re.search('CID=([^;]+)', cookie).group(1)
        seid = re.search('SEID=([^;]+)', cookie).group(1)
        cloud = py115.connect(credential={
            'UID':uid, 'CID':cid, 'SEID':seid
        })
        return cloud.storage()
