import requests
import time
import os
from madt_client import MADT_Client
import subprocess
madt_client = MADT_Client('packets')

class TsharkParser():
    def __init__ (self):
        self.nextAction = self.checkIPv4
        self.ready = False
    
    def contains(self, a, b):
        if a.find(b) == -1:
            return False
        else:
            return True
    
    def checkIPv4(self, line):
        if self.contains(line, 'Type: IPv4'):
            self.nextAction = self.checkTTL
    
    def checkTTL(self, line):
        if self.contains(line,'Time to live:'):
            self.ttl = line.split(' ')[3]
            self.nextAction = self.checkSource

    def checkSource(self, line):   
        if self.contains(line,'Source:'):
            self.source = line.split(' ')[1]
            self.nextAction = self.checkDestination
            
    def checkDestination(self, line):   
        if self.contains(line,'Destination:'):
            self.destination = line.split(' ')[1]
            self.nextAction = self.checkSum

    def checkSum(self, line):   
        if self.contains(line,'Checksum:'):
            self.checksum = line.split(' ')[1]
            self.ready = True
            self.nextAction = self.checkIPv4

    def parse(self, line):
        self.nextAction(line)
        if self.ready:
            self.ready = False
            return {'destination': self.destination, 'source': self.source, 'ttl': self.ttl, 'checksum': self.checksum}
        return None

    
parser = TsharkParser()

proc = subprocess.Popen('tshark -V -i eth0', shell=True, stdout=subprocess.PIPE)
while proc.poll() is None:
    line = proc.stdout.readline()
    res = parser.parse(str(line).strip().replace("'", '').replace("\\n", '').replace("\n", '').replace("b  ", '').strip())
    if res:
        madt_client.send_fallback(res['source'], res['destination'], res['ttl'], res['checksum'])

