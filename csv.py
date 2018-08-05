import sys
import logging
import rds_config
import pymysql
from flask import Flask, request, Response
from collections import defaultdict
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

rds_host = "mysqldb.cdcmdv6mucaf.us-west-2.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validateRow(row):
    return len(row) == 3 and '-' not in row[2] and row[2].isdigit()

def parseLine(line):
    return line.decode("utf-8").rstrip().split(",")


@app.route('/', methods=['POST'])
def post():
    if request.method == 'POST':
        for file in request.files:
            if allowed_file(file):
                f = request.files[file]
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file))
                f.save(file_path)

                # struct to prevent duplicate insertions from one post request
                d = defaultdict(set)

                with open(file_path, 'rb') as sf:
                    for line in sf:
                        row = parseLine(line)
                        if validateRow(row):
                            parent = row[0]
                            child = row[1]
                            quantity = row[2]
                            if parent not in d:
                                d[parent] = set()
                            if child not in d[parent]:
                                d[parent].add(child)
                                with conn.cursor() as cur:
                                    query = 'insert into graph (parent, child, quantity) values(%s,%s,%s)'
                                    cur.execute(query, (parent, child, quantity))
                    conn.commit()
                    return Response('Uploaded file successfully', status=200)

            else:
                return Response('Bad request, wrong file type', status=400)


if __name__ == '__main__':
    app.run()
