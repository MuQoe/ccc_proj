from couchdb import Server

TWITTER_DB = 'twitter'
MASTDON_DB = 'mastodon'

PLATFORM_DICT = {
    TWITTER_DB: 'Twitter',
    MASTDON_DB: 'Mastodon'
}

SENTIMENT_DICT = {
    TWITTER_DB: False,
    MASTDON_DB: True
}

class Database:
    def __init__(self, server, db_name):
        self.server = server
        if db_name in self.server:
            self.db = self.server[db_name]
        else:
            self.db = self.server.create(db_name)

    def create_document(self, document):
        doc_id, doc_rev = self.db.save(document)
        return doc_id, doc_rev

    def get_document(self, doc_id):
        return self.db.get(doc_id)

    def find_document(self, selector):
        return self.db.find(selector)

    def update_document(self, doc_id, document):
        doc = self.db.get(doc_id)
        doc.update(document)
        self.db.save(doc)

    def get_all_documents(self):
        result = self.db.view('_all_docs', include_docs=True)
        return [row.doc for row in result]

    def delete_document(self, doc_id):
        doc = self.db.get(doc_id)
        self.db.delete(doc)


class DBManager:
    def __init__(self, server_url):
        self.server = Server(server_url)

    def get_database(self, db_name) -> Database:
        return Database(self.server, db_name)

