# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures
import time
import logging

import grpc

import mp3_pb2
import mp3_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Greeter(mp3_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):

        print("Received Hello!")

        return mp3_pb2.HelloReply(message='Hello, %s!' % request.name)

    #TODO: begin
    def begin(self, request, context):

        t = time.time()
        vmName = request.name
        print("Received Begin from ", vmName)

        clientDict[vmName] = dict()
        clientDict[vmName]['miniDict'] = dict()
        clientDict[vmName]['commands'] = [(t, 'begin')]

        return mp3_pb2.beginReply(message='OK')


    def getValue(self, request, context):
        # since we update values in masterDict when commit, 
        # the getValue after a set gets 'Not Found'
        # use a tempDict to handle this?

        # a while loop goes through the lock queue?
        # the client still hangs after the other COMMIT

        # the server doesn't release lock after client's disconnection
        # the server doesn't release lock after commit

        t = time.time()
        vmName = request.name
        print("Received getValue from ", vmName)
        serverkey = request.serverkey
        server, key = serverkey.split(".")

        print("["+str(t)+"] "+str(vmName)+" getValue " + str(serverkey))

        if(key not in lockDict.keys()):
            lockDict[key] = [['GET', vmName]]
        else:
            lockDict[key].append(['GET', vmName])

        while(self.checkAcquireReadLock(vmName, key) == False):
            time.sleep(0.0001)

        string = 'GET {}'.format(serverkey)
        clientDict[vmName]['commands'].append([t,string])

        if (key in masterDict.keys()):
            return mp3_pb2.getReply(message='%s = %s' % (serverkey, masterDict[key]))

        if (key not in clientDict[vmName]['miniDict'].keys()):
            # Should we return NOT FOUND or let it wait 
            # if another client SET the object but not commit yet?
            return mp3_pb2.getReply(message='NOT FOUND')
        else:
            val = clientDict[vmName]['miniDict'][key]
            return mp3_pb2.getReply(message='%s = %s' % (serverkey, val))


    #TODO: setValue
    def setValue(self, request, context):

        t = time.time()
        vmName = request.name

        print("Received setValue from ", vmName)

        serverkey = request.serverkey # A.x 1
        server, key = serverkey.split(".") # ["A", "x 1"]
        value = request.value

        if(vmName not in clientDict.keys()):
            print(vmName, clientDict.keys())
            return mp3_pb2.setReply(message='\tMissing Begin statement')
        else:
            arr = clientDict[vmName]['commands']
            string = 'SET {} {}'.format(serverkey, value)
            arr.append((t,string))
            clientDict[vmName]['commands'] = arr

        if(key in lockDict.keys()):
            lockDict[key].append(['SET', vmName])
        else:
            lockDict[key] = [['SET', vmName]]

        while(lockDict[key][0][1] != vmName):
            time.sleep(0.000001)

        clientDict[vmName]['miniDict'][key] = value

        print("["+str(t)+"] "+str(vmName)+" setValue " + str(serverkey) +" " +str(value))
        return mp3_pb2.setReply(message='OK')

    # TODO: commit
    def commit(self, request, context):
        t = time.time()
        vmName = request.name

        print("Received Commit from ", vmName)

        while(self.checkCommitOK(vmName) == False):
            time.sleep(0.0001)

        for t, command in clientDict[vmName]['commands'][1:]:

            if('SET' in command):

                type, serverkey, value = command.split(" ")
                server, key = serverkey.split(".")
                masterDict[key] = value

                if(len(lockDict[key]) > 1):
                    lockDict[key].pop()
                else:
                    lockDict[serverkey] = None

            if('GET' in command):
                type, serverkey = command.split(" ")

                if(serverkey in lockDict.keys):
                    if(lockDict[serverkey] == vmName):
                        if (serverkey in waitDict.keys()):
                            if (len(waitDict[serverkey]) > 0):
                                lockDict[serverkey] = waitDict[serverkey].pop()
                            if (len(waitDict[serverkey]) == 0):
                                del (waitDict[serverkey])
                                lockDict[serverkey] = None

                    else:
                        if (serverkey in waitDict.keys()):
                            waitDict[serverkey].remove(['GET', vmName])

        return mp3_pb2.commitReply(message='COMMIT OK')


    def checkCommitOK(self, vmName):
        commit = True
        commands = clientDict[vmName]['commands']

        for t, command in commands[1:]:

            if ('SET' in command):
                type, serverkey, value = command.split(" ")
                server, key = serverkey.split(".")

                toplock = lockDict[key][0]
                if (toplock[1] == vmName):
                    continue
                else:
                    return False

            if ('GET' in command):
                type, serverkey = command.split(" ")
                if (lockDict[serverkey][1] == vmName):
                    continue
                if(lockDict[serverkey][0] == 'SET'):
                    return False
                else:
                    for type, vmname in waitDict[serverkey]:
                        if(vmName ==vmname):
                            continue
                        elif('SET' in value):
                            return False

        return True


    # TODO: abort
    def abort(self, request, context):
        pass

    def checkAcquireReadLock(self, vmname, serverkey):

        if(serverkey not in lockDict.keys()):
            # No one has a lock on it
            return True

        lockType, vmName = lockDict[serverkey][0]

        if(lockType == 'SET'):
            if(vmName == vmname):
                return True
            return False

        ret = True
        if(serverkey in waitDict.keys()):
            for lockType, vmName in waitDict.items():
                if (lockType == 'SET'):
                    ret = False
        return ret






def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    mp3_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    server.add_insecure_port('[::]:50051')
    server.start()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':

    logging.basicConfig()

    clientDict = dict()
    masterDict = dict()
    lockDict = dict()
    waitDict = dict()

    #d['A.x'] = 'Benjamin'
    print("[SERVING]")
    serve()
