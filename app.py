import json
import os
import sys

import emoji
from datetime import datetime

from flask import Flask, jsonify, request
import logging
from utils.response import *
from utils.database import *
from utils.sentiment import *
from data.data import *
from flask import Flask
from flask_cors import CORS
from couchdb.mapping import Document, TextField, IntegerField

from views.views import *

app = Flask(__name__, static_url_path='/static')
app.debug = True
CORS(app, supports_credentials=True)

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


def get_emoji_count():
    twitter_db = manager.get_database(MASTDON_DB)
    view_name = 'group_by_emoji'
    result = twitter_db.db.view('_design/mastodon/_view/' + view_name, group=True)
    group_counts = {}
    for row in result:
        emoji_key = row.key.split('\u200d')
        for key in emoji_key:
            if key in group_counts:
                group_counts[key] += row.value
            else:
                group_counts[key] = row.value
    return group_counts


def get_emoji_sentiment_count(sentiment_label):
    twitter_db = manager.get_database(MASTDON_DB)
    view_name = 'group_by_sentiment_emoji'
    result = twitter_db.db.view('_design/mastodon/_view/' + view_name, group=True)
    group_counts = {}
    for row in result:
        sentiment, emoji = row.key
        if sentiment != sentiment_label:
            continue
        emoji_key = emoji.split('\u200d')
        for key in emoji_key:
            if key in group_counts:
                group_counts[key] += row.value
            else:
                group_counts[key] = row.value
    return group_counts


def get_group_counts():
    view_name = 'group_by_gcc'
    db = manager.get_database(TWITTER_DB)
    result = db.db.view('twitter/' + view_name, group=True)
    group_counts = json.loads(TWITTER_GEO_DATA)
    for row in result:
        group_counts[row.key]['emoji_count'] = row.value
        group_counts[row.key]['percentage'] = group_counts[row.key]['emoji_count'] / group_counts[row.key][
            'total_count']
    return group_counts

def get_sentiment_mastodon():
    view_name = 'count_sentiment'
    db = manager.get_database(MASTDON_DB)
    result = db.db.view('mastodon/' + view_name, group=True)
    group_counts = {}
    for row in result:
        group_counts[row.key] = row.value
    return group_counts

def get_sentiment_twitter():
    view_name = 'count_sentiment'
    db = manager.get_database(TWITTER_DB)
    result = db.db.view('twitter/' + view_name, group=True)
    group_counts = {}
    for row in result:
        group_counts[row.key] = row.value
    return group_counts

# result = get_sentiment_mastodon()
# print(result)
# result = get_sentiment_twitter()
# print(result)
# aaa = 0


@app.route('/save_data', methods=['POST'])
def save_data_api():
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
def get_twitter_geo_data_api():
    try:
        result = get_group_counts()
        return create_response('success', 'Twitter geo data obtained.', result)
    except Exception as e:
        return create_response('fail', f'Twitter geo data failed to with error: {str(e)}')


@app.route('/twitter_ancestry', methods=['GET'])
def get_ancestry_data_api():
    try:
        result = get_ancestry_correlation(get_group_counts())

        response = []

        for data in result:
            try:
                data['ancestry'] = ANCETRY_MAP[data['ancestry']]
                response.append(data)
            except Exception as e:
                pass


        return create_response('success', 'Twitter ancestry data obtained.', result)
    except Exception as e:
        return create_response('fail', f'Twitter ancestry data failed to with error: {str(e)}')


@app.route('/twitter_language', methods=['GET'])
def get_language_data_api():
    try:
        result = get_language_correlation(get_group_counts())
        response = []

        for data in result:
            try:
                data['language'] = LANGUAGE_MAP[data['language']]
                response.append(data)
            except Exception as e:
                pass

        return create_response('success', 'Twitter language data obtained.', response)
    except Exception as e:
        return create_response('fail', f'Twitter language data failed to with error: {str(e)}')


@app.route('/mastodon_emoji_count', methods=['GET'])
def get_mastodon_emoji_count_api():
    try:
        result = get_emoji_count()

        top_k = request.args.get('topk')
        if top_k:
            result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:int(top_k)]
        else:
            result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]

        total_count = sum([count for _, count in result])

        # format the result
        result = [{'emoji': emoji_unicode, 'count': count, 'emoji_name': emoji.demojize(emoji_unicode), 'percentage': count / total_count}
                  for emoji_unicode, count in result]

        return create_response('success', 'Mastodon emoji_count data obtained.', result)
    except Exception as e:
        return create_response('fail', f'Mastodon emoji_count data failed to with error: {str(e)}')


@app.route('/mastodon_sentiment_emoji_count', methods=['GET'])
def get_mastodon_sentiment_emoji_count_api():
    try:
        sentiment_label = request.args.get('sentiment')
        if not sentiment_label in ['Negative', 'Neutral', 'Positive']:
            return create_response('fail', 'Invalid sentiment label.')

        result = get_emoji_sentiment_count(sentiment_label)
        top_k = request.args.get('topk')
        if top_k:
            result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:int(top_k)]
        else:
            result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]

        total_count = sum([count for _, count in result])

        # format the result
        result = [{'emoji': emoji_unicode, 'count': count, 'emoji_name': emoji.demojize(emoji_unicode), 'percentage': count / total_count}
                  for emoji_unicode, count in result]

        return create_response('success', 'Mastodon sentiment_emoji_count data obtained.', result)
    except Exception as e:
        return create_response('fail', f'Mastodon sentiment_emoji_count data failed to with error: {str(e)}')


@app.route('/twitter_emoji_count', methods=['GET'])
def get_twitter_emoji_count_api():
    try:
        result = TWITTER_ALL_EMOJI
        top_k = request.args.get('topk')
        if top_k:
            result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:int(top_k)]
        else:
            result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]

        # format the result
        result = [{'emoji': emoji_unicode, 'count': count, 'emoji_name': emoji.demojize(emoji_unicode)}
                  for emoji_unicode, count in result]

        return create_response('success', 'Twitter sentiment_emoji_count data obtained.', result)
    except Exception as e:
        return create_response('fail', f'Twitter sentiment_emoji_count data failed to with error: {str(e)}')


@app.route('/twitter_sentiment_emoji_count', methods=['GET'])
def get_twitter_sentiment_emoji_count_api():
    try:
        sentiment_label = request.args.get('sentiment')
        if not sentiment_label in ['Negative', 'Neutral', 'Positive']:
            return create_response('fail', 'Invalid sentiment label.')

        result = TWITTER_SENTIMENT_DATA[sentiment_label]
        top_k = request.args.get('topk')
        if top_k:
            result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:int(top_k)]
        else:
            result = sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]

        # format the result
        result = [{'emoji': emoji_unicode, 'count': count, 'emoji_name': emoji.demojize(emoji_unicode)}
                  for emoji_unicode, count in result]

        return create_response('success', 'Twitter sentiment_emoji_count data obtained.', result)
    except Exception as e:
        return create_response('fail', f'Twitter sentiment_emoji_count data failed to with error: {str(e)}')


@app.route('/twitter_sentiment_count', methods=['GET'])
def get_twitter_sentiment_count_api():
    try:
        result = get_sentiment_twitter()
        return create_response('success', 'Twitter sentiment_emoji_count data obtained.', result)
    except Exception as e:
        return create_response('fail', f'Twitter sentiment_emoji_count data failed to with error: {str(e)}')

@app.route('/mastodon_sentiment_count', methods=['GET'])
def get_mastodon_sentiment_count_api():
    try:
        result = get_sentiment_mastodon()
        return create_response('success', 'Mastodon sentiment_emoji_count data obtained.', result)
    except Exception as e:
        return create_response('fail', f'Mastodon sentiment_emoji_count data failed to with error: {str(e)}')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5566)
