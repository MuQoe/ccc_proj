import logging
from utils.database import *

ALL_VIEW_TWITTER = {
    '_id': '_design/twitter',
    'views': {}
}
ALL_VIEW_MASTODON = {
    '_id': '_design/mastodon',
    'views': {}
}

TWITTER_GEO_DATA = '''{"1GSYD":{"total_count":745874,"age":36},"1RNSW":{"total_count":212506,"age":43},"2GMEL":{"total_count":749772,"age":36},"2RVIC":{"total_count":171677,"age":43},"3GBRI":{"total_count":310471,"age":35},"3RQLD":{"total_count":255633,"age":39},"4GADE":{"total_count":161673,"age":39},"4RSAU":{"total_count":45356,"age":45},"5GPER":{"total_count":211509,"age":36},"5RWAU":{"total_count":43756,"age":39},"6GHOB":{"total_count":40397,"age":40},"6RTAS":{"total_count":33441,"age":44},"7GDAR":{"total_count":19540,"age":33},"7RNTE":{"total_count":14049,"age":30},"8ACTE":{"total_count":71872,"age":35},"9OTER":{"total_count":53,"age":42}}'''

def init_views(DBManager):
    add2DictTwitter()

    twitter_db = DBManager.get_database(TWITTER_DB).db
    twitter_doc_id = '_design/twitter'
    if twitter_doc_id not in twitter_db:
        twitter_db.save(ALL_VIEW_TWITTER)
        logging.info('Design document created for Twitter database')

    else:
        twitter_design = twitter_db[twitter_doc_id]
        for view_name, design_doc in ALL_VIEW_TWITTER['views'].items():
            if view_name in twitter_design.get('views', {}):
                continue
            else:
                design_doc_full = {
                    '_id': twitter_doc_id,
                    'views': design_doc
                }
                twitter_db.save(design_doc_full)
                logging.info('View {} created in database {}'.format(view_name, TWITTER_DB))

    add2DictMastodon()

    mastodon_db = DBManager.get_database(MASTDON_DB).db
    mastodon_doc_id = '_design/mastodon'
    if mastodon_doc_id not in mastodon_db:
        mastodon_db.save(ALL_VIEW_MASTODON)
        logging.info('Design document created for Mastodon database')
    else:
        mastodon_design = mastodon_db[mastodon_doc_id]
        for view_name, design_doc in ALL_VIEW_MASTODON['views'].items():
            if view_name in mastodon_design.get('views', {}):
                continue
            else:
                design_doc_full = {
                    '_id': mastodon_doc_id,
                    'views': design_doc
                }
                mastodon_db.save(design_doc_full)
                logging.info('View {} created in database {}'.format(view_name, MASTDON_DB))



def generate_gcc():
    view_name = 'group_by_gcc'
    map_func = '''
    function(doc) {
        if (doc.GCC_CODE21) {
            emit(doc.GCC_CODE21, 1);
        }
    }
    '''
    reduce_func = '_sum'

    design_doc = {
        "map": map_func,
        "reduce": reduce_func
    }
    ALL_VIEW_TWITTER['views'][view_name] = design_doc


def createView(dbConn, designDoc, viewName, mapFunction, reduceFunction=None):
    '''
    Reference from "https://stackoverflow.com/questions/61528697/create-view-in-couchdb-in-a-python-application"
    :param dbConn:
    :param designDoc:
    :param viewName:
    :param mapFunction:
    :return:
    '''
    data = {
        "_id": f"_design/{designDoc}",
        "views": {
            viewName: {
                "map": mapFunction
            }
        },
        "language": "javascript",
        "options": {"partitioned": False}
    }
    if reduceFunction:
        data["views"][viewName]["reduce"] = reduceFunction
    logging.info(f"creating view {designDoc}/{viewName}")
    dbConn.save(data)


def add2DictTwitter():
    generate_gcc()

def add2DictMastodon():
    pass