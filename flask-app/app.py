#native libraries
import os
import time
import random
#postgres libraries
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select


# dogstatsd is called datadog
from datadog import initialize, statsd
initialize(statsd_host=os.environ['DOGSTATSD_HOST_IP'], statsd_port=8125)
statsd.increment('flaskapp.times.started')

from flask import Flask


#trace stuff
from ddtrace import tracer, patch, Pin
from ddtrace.contrib.flask import TraceMiddleware

tracer.configure(
    hostname=os.environ['DD_AGENT_SERVICE_HOST'],
    port=os.environ['DD_AGENT_SERVICE_PORT'],
)

patch(sqlalchemy=True)

app = Flask(__name__)

#patch traceware
traced_app = TraceMiddleware(app, tracer, service="my-flask-app", distributed_tracing=False)


#postgres stuff
POSTGRES = {
    'user': 'flask',
    'pw': 'flask',
    'db': 'docker',
    'host': os.environ['POSTGRES_SERVICE_HOST'],
    'port': os.environ['POSTGRES_SERVICE_PORT'],
}
pg_url = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
con = sqlalchemy.create_engine(pg_url, client_encoding='utf8')
meta = sqlalchemy.MetaData(bind=con, reflect=True)

web_origins = Table('web_origins', meta, autoload=True)

#logging stuff
import logging
import json_log_formatter
import threading

logging.basicConfig()
formatter = json_log_formatter.JSONFormatter()
json_handler = logging.FileHandler(filename='/var/log/flask/mylog.json')
json_handler.setFormatter(formatter)
logger = logging.getLogger('my_json')
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)


@app.route('/')
def hello_world():
    statsd.increment('web.page_views')
    return 'Hello, World! I\'ve incremented the web.pageviews Dogstatsd metric!'

@app.route('/log')
def log_endpoint():
    my_thread= threading.currentThread().getName()
    time.sleep(0.01)
    logger.info('log_endpoint should be making logs', 
        extra={
            'job_category': 'hello_world', 
            'logger.name': 'my_json', 
            'logger.thread_name' : my_thread
        }
    )
    time.sleep(random.random()* 2)
    return 'hello logs \n'


@app.route('/query')
def return_results():
    conn = con.connect()
    s = select([web_origins])
    result = conn.execute(s)
    row = result.fetchone()
    conn.close()
    return str(row) + '\n'

@app.route('/bad')
def bad():
    # this will break because variable g doesn't exist
    return 'Flask has been kuberneted \n'.format(g)

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=5005)