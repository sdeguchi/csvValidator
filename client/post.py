import requests

file = 'DAG.csv'
with open(file, 'rb') as f:
    r = requests.post('http://ec2-35-161-0-241.us-west-2.compute.amazonaws.com:80', files={file: f})
    print(r)