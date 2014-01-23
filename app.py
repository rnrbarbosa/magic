#!/usr/bin/env python
# -*- coding: latin-1 -*-

from flask import Flask
from flask import request
from lxml import objectify
import psycopg2,re,datetime
import json
import logging
from logging.handlers import RotatingFileHandler

LOG_FILENAME = 'log/magic.log'
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/")
def hello():
    return "Foge, vais morrer se nao sabes o que fazes!"

@app.route('/magic',methods=['GET','POST'])
def magic():
    if request.method == 'GET':
        return "It's a Kind of Magic! Prime Consulting"

    app.logger.info("#"*50)
    app.logger.info(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    app.logger.info('Processing New Form...')
    xml = request.data

    root = objectify.fromstring(xml)
    registo = {}
    for key,value in root.attrib.items():
        k = re.sub(r'\{http.*\}','',key)
        registo[k] = value
    del registo["writeTime"]
    del registo["formVersion"]

    for e in root.inputs.iterchildren():
        k = re.sub(r'\{http.*\}','',e.tag)
        registo[k] = e.text
    #d = registo["submit_time"]
    #registo["submit_time"] = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S %Z').date()
    form_id = registo["submissionIdentifier"]
    app.logger.info('Processing: ' + form_id)

    f = open('queue/' + form_id + '.xml', 'w' )
    app.logger.info('Writing XML file...')
    f.write(xml)
    f.close()

    if "fotografia" in registo:
        imgData = registo["fotografia"]
        imgFilename = registo["submissionIdentifier"]
        fh = open( "img/" + imgFilename + ".jpg", "wb")
        app.logger.info('Writing JPG file...')
        fh.write(imgData.decode('base64'))
        fh.close()

    app.logger.info('Writing JSON file...')
    with open('json/' + form_id + '.json', 'w') as outfile:
          json.dumps(registo, outfile)
    app.logger.info(form_id + '...RECEIVED SUCESSFULLY')
    app.logger.info("#"*50)
    return form_id


if __name__ == "__main__":
    app.logger.addHandler(handler)
    app.run()
