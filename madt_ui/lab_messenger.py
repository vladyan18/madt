from threading import Thread, Event
import os
import time
import asyncio
import zmq
import zmq.asyncio
from zmq.utils import jsonapi
import json

from .config import lab_path, prefix

try:
    from werkzeug.contrib.cache import UWSGICache as cache
    msg_cache = cache()
except:
    from werkzeug.contrib.cache import SimpleCache as cache
    msg_cache = cache()

ctx = zmq.asyncio.Context()

class FallbackSocket: # extremely stupid, but...
    def __init__(self, lab_name, socket_name):
        self.offsets = {}
        self.lab_name = lab_name
        self.socket_name = socket_name

    
    def recv(self):
        path = os.path.join(os.environ['MADT_LABS_SOCKETS_DIR'], self.lab_name, self.socket_name)
        try:
            fallback_sockets = os.listdir(path)
        except Exception as e:
            os.mkdir(path)
        results = []
        for socket in fallback_sockets:
            if socket == 'lab.sock':
                continue
            if not socket in self.offsets:
                self.offsets[socket] = 0
            
            try:
                f = open(os.path.join(path, socket), 'r')
                data = f.read()
                f.close()

                msgs = data.split('#')
                hostname = socket.split('.')[0]
                for msg in msgs:
                    values = msg.split('&')
                    num = int(values[0])
                    text = values[1]
                    if num > self.offsets[socket]:
                        self.offsets[socket] = num
                        results.append({'hostname': hostname, 'msg': json.loads(text)})
                        break
            except Exception as e:
                pass
        return results

class Messenger:
    def __init__(self, lab_name):
        self.lab_name = lab_name
        self.prefix = prefix(lab_name)
        msg_cache.set(lab_name, {
            'all': {},
            'status_count': {},
            'total': 0,
            'avg_traffic': 0,
            'start_time': int(time.time())
        })
        msg_cache.set(lab_name + '_packets', {
            'grouppedByCheckSums': {}
        })
        #self.sock = ctx.socket(zmq.PULL)
        self.sock = FallbackSocket(lab_name, 'lab')
        self.packets_sock = FallbackSocket(lab_name, 'packets')

        url = self.socket_url()
        print('Sock bind', url)
        #self.sock.connect('tcp://127.0.0.1:4715')

        asyncio.ensure_future(self.listen())
        asyncio.ensure_future(self.listen_packets())

    def socket_url(self):
        return 'ipc://'+os.path.join(os.environ['MADT_LABS_SOCKETS_DIR'], self.lab_name, 'lab.sock')

    async def listen(self):
        while True:
            await asyncio.sleep(0.25)
            i = 0
            while i < 500:
                await asyncio.sleep(0.25)
                i = i+1
                #raw_msg = await self.sock.recv()
                #msg = jsonapi.loads(raw_msg)
                #print('Message', raw_msg)

                msgObjs = self.sock.recv()
                for msgObj in msgObjs:
                    if 'hostname' in msgObj:
                        msg = msgObj['msg']
                        msgs = msg_cache.get(self.lab_name)

                        if msgs is None:
                            return
                        msgs['all'][self.prefix + msg.pop('hostname')] = msg

                        msgs['total'] += 1

                        if msg['status']:
                            if msg['status'] in msgs['status_count']:
                                msgs['status_count'][msg['status']] += 1
                            else:
                                msgs['status_count'][msg['status']] = 1

                        if msg['traffic']:
                            msgs['avg_traffic'] = (msgs['avg_traffic'] + msg['traffic']) / msgs['total']

                        msg_cache.set(self.lab_name, msgs)
                    else:
                        print('received message from unknown host: ' + str(msgObj))


    async def listen_packets(self):
        while True:
            await asyncio.sleep(0.5)
            msgObjs = self.packets_sock.recv()

            for msgObj in msgObjs:
                if 'hostname' in msgObj:
                    msg = msgObj['msg']
                    msgs = msg_cache.get(self.lab_name + '_packets')
                    if msgs is None:
                        return
                    checkSum = msg.pop('checkSum')
                    if not checkSum in msgs['grouppedByCheckSums']:
                        msgs['grouppedByCheckSums'][checkSum] = []

                    msgs['grouppedByCheckSums'][checkSum].append(msg)

                    msg_cache.set(self.lab_name + '_packets', msgs)




    @staticmethod
    def get_messages(lab_name):
        msgs = msg_cache.get(lab_name)
        if msgs is not None:
            all_messages = msgs['all']
            msgs['all'] = {}
            msg_cache.set(lab_name, msgs)

            return all_messages
        else:
            return None

    @staticmethod
    def get_messages_about_packets(lab_name, startTime = 0):
        msgs = msg_cache.get(lab_name + '_packets')
        if msgs is not None:
            all_messages = msgs['grouppedByCheckSums']
            msgs['grouppedByCheckSums'] = {}
            msg_cache.set(lab_name + '_packets', msgs)

            return all_messages
        else:
            return None

    @staticmethod
    def get_stats(lab_name):
        msgs = msg_cache.get(lab_name)
        return {k: v for k, v in msgs.items() if k != 'all'} if msgs else msgs

    @staticmethod
    def get_data(lab_name):
        msgs = msg_cache.get(lab_name)
        if msgs is not None:
            msgs_copy = msgs.copy()
            msgs_copy['all'] = {}
            msg_cache.set(lab_name, msgs_copy)

            return msgs
        else:
            return None



