import requests
import time
import os
from madt_client import MADT_Client
import random


madt_client = MADT_Client('lab')
server = os.environ['SERVER']

while True:
    time.sleep(1)

    try:
        # send GET request to the server with timeout of 1 second
        res = requests.get('http://' + server, timeout=1, params={'rand': str(random.randint(1, 1000))})
    except requests.exceptions.Timeout:
        # if request time exceeds timeout, requests will raise an Timeout exception
        madt_client.send_fallback(2, 'Timeout', 0)
        continue
    except Exception as e:
        # if server returns invalid response, requests will raise another exception
        madt_client.send_fallback(3, str(e), 0) # but it is unlikely this will happen
        continue

    if res.ok:
        # we're using text as a log and request time as a traffic
        madt_client.send_fallback(0, res.text, res.elapsed.microseconds)
    else:
        madt_client.send_fallback(1, res.text, res.elapsed.microseconds)
