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
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function
import logging
import sys
import grpc

import mp3_pb2
import mp3_pb2_grpc

# serverVMs = ['10.193.240.202',
#  'sp19-cs425-g58-01.cs.illinois.edu',
#  'sp19-cs425-g58-02.cs.illinois.edu',
#  'sp19-cs425-g58-03.cs.illinois.edu',
#  'sp19-cs425-g58-04.cs.illinois.edu',
#  'sp19-cs425-g58-05.cs.illinois.edu']

# serverVMs = [
#  'sp19-cs425-g58-01.cs.illinois.edu',
#  'sp19-cs425-g58-02.cs.illinois.edu',
#  'sp19-cs425-g58-03.cs.illinois.edu',
#  'sp19-cs425-g58-04.cs.illinois.edu',
#  'sp19-cs425-g58-05.cs.illinois.edu']

serverLetters = ['A', 'B', 'C', 'D', 'E']

serverVMs = [
 'sp19-cs425-g58-10.cs.illinois.edu',
 'sp19-cs425-g58-09.cs.illinois.edu',
 'sp19-cs425-g58-08.cs.illinois.edu',
 'sp19-cs425-g58-07.cs.illinois.edu']
# serverLetters = ['A', 'B', 'C', 'D']

def run(name, numVMs):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.

    serverDict = dict()

    for i in range(numVMs):
        channel = grpc.insecure_channel(str(serverVMs[i])+':50051')
        serverDict[serverLetters[i]] = mp3_pb2_grpc.GreeterStub(channel)

        response = serverDict[serverLetters[i]].SayHello(mp3_pb2.HelloRequest(name='you'))
        print("Greeter client received: " + response.message)

        # bensname = serverDict[serverLetters[i]].getValue(mp3_pb2.getMessage(name="BensMac", key='A.x'))
        # print("getValue received: " + bensname.message)

    try:
        with sys.stdin as i:
            while(1):

                command = input()

                goodCommand = False

                if('BEGIN' in command and len(command) == 5):
                    goodCommand = True
                    for server in serverDict.values():
                        reply = server.begin(mp3_pb2.beginMessage(name=name))
                        print(reply.message)

                elif('COMMIT' in command and len(command) == 6):
                    goodCommand = True
                    for server in serverDict.values():
                        reply = server.commit(mp3_pb2.beginMessage(name=name))


                elif('ABORT' in command and len(command) == 5):
                    goodCommand = True
                    for server in serverDict.values():
                        reply = server.abort(mp3_pb2.beginMessage(name=name))


                elif('GET' in command):

                    split = command.split(" ")
                    if(len(split) != 2):
                        print("\t Error in input")
                        continue
                    goodCommand = True
                    get, serverkey = split
                    server, key = serverkey[:].split(".")
                    #print(serverkey)

                    reply = serverDict[server].getValue(mp3_pb2.getMessage(name=name, serverkey=str(serverkey)))

                elif ('SET' in command):

                    split = command.split(" ")
                    if (len(split) != 3):
                        print("\t Error in input")
                        continue
                    goodCommand = True
                    set, serverkey, value = split
                    server, key = serverkey.split(".")

                    reply = serverDict[server].setValue(mp3_pb2.setMessage(name=name, serverkey=serverkey, value=value))


                if(not goodCommand):
                    print("Unexpected input, please try again!")
                    continue

                if(reply.message == "shouldAbort"):
                    for letter, server in serverDict.items():
                        reply = server.abort(mp3_pb2.beginMessage(name=name))
                        print(letter,": ",reply.message)

                else:
                    print(reply.message)

                #print(command)

    except KeyboardInterrupt:
        exit(1)




if __name__ == '__main__':

    logging.basicConfig()

    run(sys.argv[1], int(sys.argv[2]))

    if(sys.argv[3] == 'ben'):
        serverVMs = [
            'sp19-cs425-g58-01.cs.illinois.edu',
            'sp19-cs425-g58-02.cs.illinois.edu',
            'sp19-cs425-g58-03.cs.illinois.edu',
            'sp19-cs425-g58-04.cs.illinois.edu',
            'sp19-cs425-g58-05.cs.illinois.edu']
    else:
        serverVMs = [
            'sp19-cs425-g58-07.cs.illinois.edu',
            'sp19-cs425-g58-08.cs.illinois.edu',
            'sp19-cs425-g58-09.cs.illinois.edu',
            'sp19-cs425-g58-10.cs.illinois.edu']
