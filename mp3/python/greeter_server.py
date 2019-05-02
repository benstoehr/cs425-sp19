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

    def printALL(self):
        print("clientDict")
        for k, v in clientDict.items():
            print(k, ", ", v)
        print("lockDict")
        for k, v in lockDict.items():
            print("\t", k, ", ", v)
        print("masterDict")
        for k, v in masterDict.items():
            print(k, ", ", v)

    def SayHello(self, request, context):

        print("Received Hello!")
        # hireply = server.HiReply(mp3_pb2.hiMessage(name=request.name))
        # print(hireply.message)
        hireply = coordinator.SayHi(mp3_pb2.HiRequest(name=request.name))
        print(hireply.message)

        return mp3_pb2.HelloReply(message='Hello, %s!' % request.name)

    #TODO: begin
    def begin(self, request, context):

        t = time.time()
        vmName = request.name
        print("\nReceived Begin from ", vmName)
        #self.printALL()


        clientDict[vmName] = dict()
        clientDict[vmName]['miniDict'] = dict()
        clientDict[vmName]['commands'] = [(t, 'begin')]

        self.printALL()
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

        if (vmName not in clientDict.keys()):
            print(vmName, clientDict.keys())
            return mp3_pb2.setReply(message='\tMissing Begin statement')

        print("\nReceived getValue from ", vmName)
        #self.printALL()

        serverkey = request.serverkey
        server, key = serverkey.split(".")

        checkreply = coordinator.checkLock(mp3_pb2.checkMessage(name=vmName, message=serverkey))
        print(checkreply.message)
        #TODO: Implement different logic for abort

        print("["+str(t)+"] "+str(vmName)+" getValue " + str(serverkey))

        # No Locks
        if(key not in lockDict.keys()):
            # Key exists in master
            if(key in masterDict.keys()):
                # SET LOCK
                lockDict[key] = [['GET', vmName]]
            else:
                # Does key exist locally?
                if (key not in clientDict[vmName]['miniDict'].keys()):
                    # Should we return NOT FOUND or let it wait
                    # if another client SET the object but not commit yet?
                    return mp3_pb2.getReply(message='NOT FOUND')
        else:
            # APPEND LOCK
            lockDict[key].append(['GET', vmName])

        while(self.checkAcquireReadLock(vmName, key) == False):
            time.sleep(0.0001)

        string = 'GET {}'.format(serverkey)
        clientDict[vmName]['commands'].append([t,string])

        if (key in masterDict.keys()):
            self.printALL()
            return mp3_pb2.getReply(message='%s = %s' % (serverkey, masterDict[key]))

        else:
            val = clientDict[vmName]['miniDict'][key]
            self.printALL()
            return mp3_pb2.getReply(message='%s = %s' % (serverkey, val))

    #TODO: setValue
    def setValue(self, request, context):

        t = time.time()
        vmName = request.name
        print("\nReceived setValue from ", vmName)
        self.printALL()

        serverkey = request.serverkey # A.x 1
        server, key = serverkey.split(".") # ["A", "x 1"]
        value = request.value

        s = " ".join((serverkey, value))
        checkreply = coordinator.checkLock(mp3_pb2.checkMessage(name=vmName, message=s))
        print(checkreply.message)
        # TODO: Implement different logic for abort

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
        self.printALL()
        return mp3_pb2.setReply(message='OK')

    # TODO: commit
    def commit(self, request, context):
        t = time.time()
        vmName = request.name
        if (vmName not in clientDict.keys()):
            print(vmName, clientDict.keys())
            return mp3_pb2.setReply(message='\tMissing Begin statement')

        print("\nReceived Commit from ", vmName)
        self.printALL()

        checkreply = coordinator.checkLock(mp3_pb2.checkMessage(name=vmName, message='COMMIT'))
        print(checkreply.message)
        # TODO: Implement different logic for abort

        while(self.checkCommitOK(vmName) == False):
            time.sleep(0.0001)

        for t, command in clientDict[vmName]['commands'][1:]:

            # SET Command
            if('SET' in command):

                type, serverkey, value = command.split(" ")
                server, key = serverkey.split(".")
                masterDict[key] = value

                # ASSUME first entry is ['SET', vmName]
                if(len(lockDict[key]) > 1):
                    lockDict[key].pop(0)
                else:
                    del(lockDict[key])
                continue

            # GET Command
            if('GET' in command):
                type, serverkey = command.split(" ")
                server, key = serverkey.split(".")

                if(lockDict[key][0] == ['GET', vmName]):

                    print("\nlockDict")
                    for k, v in lockDict.items():
                        print(k, ", ", v)

                    locks = lockDict[key]
                    if (len(locks) > 1):
                        lockDict[key].pop(0)
                    else:
                        del(lockDict[key])
                else:
                    lockDict[key].remove(['GET', vmName])

        del(clientDict[vmName])

        self.printALL()
        return mp3_pb2.commitReply(message='COMMIT OK')

    def checkCommitOK(self, vmName):

        commit = True
        commands = clientDict[vmName]['commands']

        for t, command in commands[1:]:

            if ('SET' in command):
                type, serverkey, value = command.split(" ")
                server, key = serverkey.split(".")

                # Only ok if oldest related 'SET' is from vmName
                set, vm = lockDict[key][0]
                if (vm == vmName):
                    continue
                else:
                    return False

            if ('GET' in command):
                type, serverkey = command.split(" ")
                server, key = serverkey.split(".")
                locks = lockDict[key]

                # Pull off first lock
                commandType, vm = locks[0]
                if (vm == vmName):
                    continue

                elif(commandType == 'SET' and vm != vmName):
                    return False

                else:
                    for commandType, vm in locks[1:]:
                        if ('SET' in commandType):
                            return False
                        if('SET' in commandType and vm == vmName):
                            return False
                        if(vmName == vm):
                            continue

        return True


    # TODO: abort
    def abort(self, request, context):
        t = time.time()
        vmName = request.name
        if (vmName not in clientDict.keys()):
            print(vmName, clientDict.keys())
            return mp3_pb2.setReply(message='\tMissing Begin statement')

        print("\nReceived ABORT from ", vmName)
        checkreply = coordinator.checkLock(mp3_pb2.checkMessage(name=vmName, message='COMMIT'))
        print(checkreply.message)
        # TODO: Implement different logic for abort

        commands = clientDict[vmName]['commands']

        for t, command in commands[1:]:

            if ('SET' in command):
                type, serverkey, value = command.split(" ")
                server, key = serverkey.split(".")

                # Only ok if oldest related 'SET' is from vmName
                lockDict[key].remove(['SET', vmName])

            if ('GET' in command):
                type, serverkey = command.split(" ")
                server, key = serverkey.split(".")

                lockDict[key].remove(['GET', vmName])

        return mp3_pb2.abortReply(message='ABORTED')

    def checkAcquireReadLock(self, vmname, key):

        if(key not in lockDict.keys()):
            # No one has a lock on it
            return True

        lockType, vmName = lockDict[key][0]

        if(lockType == 'SET'):
            if(vmName == vmname):
                return True
            return False

        ret = True
        if(key in lockDict.keys()):
            for lockType, vmName in lockDict[key]:
                if (lockType == 'SET' and vmName != vmname):
                    ret = False
                    break

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
    #waitDict = dict()

    coordinatorChannel = grpc.insecure_channel('sp19-cs425-g58-03.cs.illinois.edu:50052')
    coordinator = mp3_pb2_grpc.CoordinatorStub(coordinatorChannel)

    #d['A.x'] = 'Benjamin'
    print("[SERVING]")
    serve()
