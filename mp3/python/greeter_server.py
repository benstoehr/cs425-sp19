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
        return mp3_pb2.HelloReply(message='Hello, %s!' % request.name)

    #TODO: begin
    def begin(self, request, context):

        t = time.time()
        vmName = request.name
        clientDict[vmName] = [(t, 'begin')]
        return mp3_pb2.beginReply(message='OK')


    def getValue(self, request, context):
        t = time.time()
        vmName = request.name
        key = request.key

        if(key in masterDict.keys()):
            return mp3_pb2.getReply(reply='%s' % masterDict[request.value])

        else:
            return mp3_pb2.getReply(reply='NOT FOUND')



    #TODO: setValue
    def setValue(self, request, context):

        t = time.time()
        vmName = request.name
        keyvalue = request.keyvalue.split(".")
        key, value = keyvalue.split(".")

        if(vmName not in clientDict.keys()):
            return mp3_pb2.setReply(reply='Missing Begin statement')
        else:
            arr = clientDict[vmName]
            string = 'SET %s'.format(keyvalue)
            arr.append((t,string))

        if(lockDict[keyvalue] is not None):
            if(waitDict[keyvalue] is None):
                waitDict[keyvalue] = [vmName]
            else:
                waitDict[keyvalue].append(vmName)
        else:
            lockDict[keyvalue] = vmName

        while(lockDict[keyvalue] != vmName):
            time.sleep(0.000001)

        # check the lock first
        # if no lock, access the lock and write (but how to trace locks until commit?)
        # else wait (2PL)
        # what is the format of request?


    # TODO: commit
    def commit(self, request, context):
        pass

    # TODO: abort
    def abort(self, request, context):
        pass




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

    serve()