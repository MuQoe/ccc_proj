import sys

from flask import Flask, jsonify
import logging
from utils.response import *
from couchdb import Server

app = Flask(__name__, static_url_path='/static')
app.debug = True
server = Server()

# 创建一个 logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 创建一个 handler 输出到文件
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# 创建另一个 handler 输出到控制台
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)

# 创建一个 formatter，并添加到 handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# 添加 handlers 到 logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


@app.route('/')
def hello_world():
    app.logger.info('Processing default request')
    res = create_response(message='Hello, World!')
    return res


