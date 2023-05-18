import json
import os
import sys
from datetime import datetime

from flask import Flask, jsonify, request
import logging
from utils.response import *
from utils.database import *
from utils.sentiment import *
from flask import Flask
from couchdb.mapping import Document, TextField, IntegerField

from views.views import *

app = Flask(__name__, static_url_path='/static')
app.debug = True

DB_URL = 'http://testuser:Linshimima@server.muqoe.xyz:5984/'
manager = DBManager(DB_URL)

# Create Logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# check if "/logs" exist
if not os.path.exists('logs/'):
    os.makedirs('logs/')

# check if "/logs/logs.log" exist
if os.path.exists('logs/logs.log'):
    # change the name of the "/logs/logs.log" log file to "logs-{time}.log"
    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.rename('logs/logs.log', f'logs/logs-{time}.log')

# Set File Handler
file_handler = logging.FileHandler('logs/logs.log')
file_handler.setLevel(logging.DEBUG)

# Set Stream Handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)

# Set Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add Handlers to Logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.info('App Started')

init_views(manager)


def get_group_counts():
    view_name = 'group_by_gcc'
    db = manager.get_database(TWITTER_DB)
    result = db.db.view('twitter/' + view_name, group=True)
    group_counts = json.loads(TWITTER_GEO_DATA)
    for row in result:
        group_counts[row.key]['emoji_count'] = row.value
        group_counts[row.key]['percentage'] = group_counts[row.key]['emoji_count'] / group_counts[row.key]['total_count']
    return group_counts

@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.form
    content = data["data"]
    platfrom = data["platform"]
    platfrom = platfrom.lower()
    if not platfrom in PLATFORM_DICT:
        return create_response('fail', 'Platform not supported.')
    try:
        content = json.loads(content)
    except Exception as e:
        return create_response('fail', 'Invalid Data')

    db = manager.get_database(platfrom)
    try:
        query = {
            "selector": {
                "id": content['id']
            }
        }
        result = list(db.find_document(query))
        if len(result) > 0:
            return create_response('fail', 'Data already with this id already exist.')
    except Exception as e:
        return create_response('fail', 'Can not obtain the data.id from the data.')

    # sentiment analysis
    if SENTIMENT_DICT[platfrom]:
        try:
            sentiment, prob = find_sentiment(content['text'])
            content['sentiment'] = sentiment
            content['sentiment_prob'] = prob
        except:
            return create_response('fail', 'Sentiment analysis failed.')

    doc_id, doc_rev = db.create_document(content)
    return create_response('success', f'{PLATFORM_DICT[platfrom]} data saved.', {'id': doc_id})

@app.route('/twitter_geo', methods=['GET'])
def get_twitter_geo_data():
    try:
        result = get_group_counts()
        return create_response('success', 'Twitter geo data obtained.', result)
    except Exception as e:
        return create_response('fail', f'Twitter geo data failed to with error: {str(e)}')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5566)
