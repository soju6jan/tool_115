from .setup import *


class ModelBotVodItem(ModelBase):
    P = P
    __tablename__ = 'bot_vod_item'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = P.package_name

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)
    request_time = db.Column(db.DateTime)
    completed_time = db.Column(db.DateTime)

    filename = db.Column(db.String)
    size = db.Column(db.Integer)
    googleid = db.Column(db.String)
    sha1 = db.Column(db.String)
    md5 = db.Column(db.String)
    filename_no = db.Column(db.Integer)
    filename_date = db.Column(db.String)
    meta_genre = db.Column(db.String)
    meta_code = db.Column(db.String)
    meta_title = db.Column(db.String)
    meta_poster = db.Column(db.String)
    log = db.Column(db.String)

    status = db.Column(db.String)
    fileinfo = db.Column(db.JSON)
    download_count =  db.Column(db.Integer)

    def __init__(self):
        self.created_time = datetime.now()
        self.status = 'READY'
        self.log = ''
        self.download_count = 0


    @classmethod
    def process_discord_data(cls, data):
        try:
            #logger.error(d(data))
            item = cls.get_by_filename(data['msg']['data']['f'])
            if item is not None:
                return
            item =  ModelBotVodItem()
            item.filename = data['msg']['data']['f']
            item.size = data['msg']['data']['s']
            item.googleid = data['msg']['data']['id']
            item.sha1 = data['msg']['data']['sha1']
            item.md5 = data['msg']['data']['md5']
            item.meta_code = data['msg']['data']['meta']['code']
            item.meta_title = data['msg']['data']['meta']['title']
            item.meta_poster = data['msg']['data']['meta']['poster']
            item.meta_genre = data['msg']['data']['meta']['genre']
            item.filename_date =  data['msg']['data']['vod']['date']
            item.filename_no = data['msg']['data']['vod']['no']
            item.save()
            return item
        except Exception as e:
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())   
    
    @classmethod
    def process_bbs_data(cls, d):
        try:
            #logger.error(d(data))
            item = cls.get_by_filename(d['data[f]'])
            if item is not None:
                return
            item =  ModelBotVodItem()
            item.filename = d['data[f]']
            item.size = d['data[s]']
            item.googleid = d['data[id]']
            item.sha1 = d['data[sha1]']
            item.md5 = d['data[md5]']
            item.meta_code = d['data[meta][code]']
            item.meta_title = d['data[meta][title]']
            item.meta_poster = d['data[meta][poster]']
            item.meta_genre = d['data[meta][genre]']
            item.filename_date =  d['data[vod][date]']
            item.filename_no = d['data[vod][no]']
            item.save()
            return item
        except Exception as e:
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())   


    @classmethod
    def get_by_filename(cls, filename):
        try:
            with F.app.app_context():
                return F.db.session.query(cls).filter_by(filename=filename).first()
        except Exception as e:
            cls.P.logger.error(f'Exception:{str(e)}')
            cls.P.logger.error(traceback.format_exc())


    
    @classmethod
    def make_query(cls, req, order='desc', search='', option1='all', option2='all'):
        with F.app.app_context():
            query = cls.make_query_search(F.db.session.query(cls), search, cls.filename)
            if option1 == 'request_true':
                query = query.filter(cls.request_time != None)
            elif option1 == 'request_false':
                query = query.filter(cls.request_time == None)
            
            if order == 'desc':
                query = query.order_by(desc(cls.id))
            else:
                query = query.order_by(cls.id)
            return query


    @classmethod
    def get_list_by_status(cls, status):
        with F.app.app_context():
            query = db.session.query(cls).filter(
                cls.status == status,
            )
            query = query.order_by(cls.id)
            return query.all()
    

    @classmethod
    def get_list_not_finished(cls):
        with F.app.app_context():
            query = db.session.query(cls).filter(cls.status.notlike('FINISH%'))
            query = query.order_by(cls.id)
            return query.all()
    
    def set_status(self, status):
        self.status = status
        self.save()