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
        clientDict[vmName] = [(t, 'begin')]

        return mp3_pb2.beginReply(message='OK')


    def getValue(self, request, context):
        # since we update values in masterDict when commit, 
        # the getValue after a set gets 'Not Found'
        # use a tempDict to handle this?

        t = time.time()
        vmName = request.name
        serverkey = request.serverkey
        print("["+str(t)+"] "+str(vmName)+" getValue " + str(serverkey))

        if(serverkey not in lockDict.keys()):
            lockDict[serverkey] = ['GET', vmName]
        else:
            if(serverkey not in waitDict.keys()):
                waitDict[serverkey] = [['GET', vmName]]
            else:
                waitDict[serverkey].append(['GET', vmName])

        while(self.checkAcquireReadLock(serverkey) == False):
            time.sleep(0.0001)


        if(serverkey in masterDict.keys()):
            return mp3_pb2.getReply(message='%s' % masterDict[request.value])

        else:
            return mp3_pb2.getReply(message='NOT FOUND')



    #TODO: setValue
    def setValue(self, request, context):

        t = time.time()
        vmName = request.name
        serverkeyvalue = request.serverkeyvalue # A.x 1
        keyvalue = serverkeyvalue.split(".") # ["A", "x 1"]
        key, value = keyvalue[1].split(" ") # key:x, value: 1

        if(vmName not in clientDict.keys()):
            return mp3_pb2.setReply(message='Missing Begin statement')
        else:
            arr = clientDict[vmName]
            string = 'SET %s'.format(keyvalue)
            arr.append((t,string))

        if(key in lockDict.keys()):
            if(key not in waitDict.keys()):
                waitDict[key] = [vmName]
            else:
                waitDict[key].append(vmName)
        else:
            lockDict[key] = ['SET', vmName]

        while(lockDict[key][1] != vmName):
            time.sleep(0.000001)

        return mp3_pb2.setReply(message='OK? (I guess)')



        # check the lock first
        # if no lock, access the lock and write (but how to trace locks until commit?)
        # else wait (2PL)
        # what is the format of request?


    # TODO: commit
    def commit(self, request, context):
        t = time.time()
        vmName = request.name

        check = self.checkCommitOK(vmName)
        while(self.checkCommitOK(vmName) == False):
            time.sleep(0.0001)

        for command in clientDict[vmName]:

            if('SET' in command):

                type, serverkey, value = command.split(" ")
                server, key = serverkey.split(".")
                masterDict[key] = value

                if(serverkey in waitDict.keys()):
                    if(len(waitDict[serverkey]) > 0):
                        lockDict[serverkey] = waitDict[serverkey].pop()
                    if(len(waitDict[serverkey]) > 0):
                        del(waitDict[serverkey])
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


    # TODO: abort
    def abort(self, request, context):
        pass

    def checkCommitOK(self, vmName):

        commit = True
        commands = clientDict[vmName]

        for command in commands[1:]:

            if ('SET' in command):
                type, serverkey, value = command.split(" ")
                if (lockDict[serverkey][1] == vmName):
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



    def checkAcquireReadLock(self, serverkey):

        if(serverkey not in lockDict.keys()):
            # No one has a lock on it
            return True

        lockType, vmName = lockDict[serverkey]
        if(lockType == 'SET'):
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
