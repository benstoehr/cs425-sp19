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


class Coordinator(mp3_pb2_grpc.CoordinatorServicer):

    def SayHi(self, request, context):

        print("Received Hi!")

        return mp3_pb2.HiReply(message='Hi, %s!' % request.name)

    def checkLock(self, request, context):

        t = time.time()
        vmName = request.name # client's name, not the server
        message = request.message
        print("\nReceived %s from %s" % (message, vmName))
        print(historyList)

        if('COMMIT' in message):
        # flush everything of this client in allLockDict & history

            # delete allLockDict
            for serverkey in allLockDict.keys():
                tmpLocks = []
                for operation in allLockDict[serverkey]:
                    lockClient = lock[1]
                    if(lockClient == vmName):
                        pass
                    else:
                        tmpLocks.append(operation)
                        
                allLockDict[serverkey] = tmpLocks.copy()
 
            # delete history
            # tmpHistory = []
 
            # for operation in historyList:
            #     if (vmName in operation):
            #          pass
            #     else:
            #         tmpHistory.append(operation)

            historyList[:] = [x for x in historyList if vmName in x]

            return mp3_pb2.checkReply(message='OK')


        if('ABORT' in message):
        # flush everything of this client in allLockDict & history

            # delete allLockDict
            for serverkey in allLockDict.keys():
                tmpLocks = []
                for operation in allLockDict[serverkey]:
                    lockClient = lock[1]
                    if(lockClient == vmName):
                        pass
                    else:
                        tmpLocks.append(operation)

                allLockDict[serverkey] = tmpLocks.copy()
 
            # delete history
            # tmpHistory = []
 
            # for operation in historyList:
            #     if (vmName in operation):
            #         pass
            #     else:
            #         tmpHistory.append(operation)

            # historyList = tmpHistory.copy()

            historyList[:] = [x for x in historyList if vmName in x]

            return mp3_pb2.checkReply(message='OK')

        if('GET' in message):
        # check if the operation has to wait:
        # if not: update allLockDict & history and return OK
        # else: check if deadlock exists and return OK or shouldAbort accordingly

            get, serverkey = message.split(" ")
            server, key = serverkey[:].split(".")
            print(serverkey)

            ret = "OK"
            if(serverkey in allLockDict.keys()):
                for lock in allLockDict[serverkey]:
                    lockType = lock[0]
                    lockClient = lock[1]

                    if(vmName == lockClient):
                        pass

                    if(lockType == "SET"):
                        if(self.checkDeadlock(vmName, serverkey)==True):
                            ret = "shouldAbort"
                            return mp3_pb2.checkReply(message=ret)
                allLockDict[serverkey].append(["SET", vmName])
            else:
                allLockDict[serverkey] = [["SET", vmName]]

            historyList.append(" ".join([vmName, serverkey]))
            return mp3_pb2.checkReply(message=ret)

        if ('SET' in message):
        # check if the operation has to wait:
        # if not: update allLockDict & history and return OK
        # else: check if deadlock exists and return OK or shouldAbort accordingly

            set, serverkey, value = message.split(" ")
            server, key = serverkey.split(".")

            ret = "OK"
            if(serverkey in allLockDict.keys()):
                for lock in allLockDict[serverkey]:
                    lockType = lock[0]
                    lockClient = lock[1]

                    if(vmName == lockClient):
                        pass

                    if(lockType == "SET"):
                        if(self.checkDeadlock(vmName, serverkey)==True):
                            ret = "shouldAbort"
                            return mp3_pb2.checkReply(message=ret)
                allLockDict[serverkey].append(["SET", vmName])
            else:
                allLockDict[serverkey] = [["SET", vmName]]

            historyList.append(" ".join([vmName, serverkey])) # not record value here 
            return mp3_pb2.checkReply(message=ret)
            

    def checkDeadlock(self, inVmName, inServerkey):
        # TODO: check deadlock here T_T
        ownDict = dict()
        waitDict = dict()
        for operation in historyList:
            vmName = operation[0]
            lockType = operation[1]
            serverkey = operation[2]
            if(lockType == "SET" and serverkey not in ownDict):
                ownDict[serverkey] = vmName
            else:
                if(serverkey not in waitDict):
                    waitDict[serverkey] = [vmName]
                else:
                    waitDict[serverkey].append(vmName)

        if(len(ownDict)>0):
            inCurOwner = ownDict[inServerkey]
            for serverkey in waitDict.keys():
                for vm in waitDict[serverkey]:
                    if(vm == inCurOwnerr and ownDict[serverkey] == inVmName):
                        return True

        return False

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    mp3_pb2_grpc.add_CoordinatorServicer_to_server(Coordinator(), server)

    server.add_insecure_port('[::]:50052')
    server.start()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':

    logging.basicConfig()

    historyList = []
    # ["client1 GET A.x", "client2 SET B.x", "client2 GET A.x"]
    allLockDict = dict()
    # allLockDict[serverkey] = [[GET, vmName], [SET, vmName]]

    print("Coordinator [SERVING]")
    serve()
