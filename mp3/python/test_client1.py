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

serverVMs = ['sp19-cs425-g58-01.cs.illinois.edu',
 'sp19-cs425-g58-02.cs.illinois.edu',
 'sp19-cs425-g58-03.cs.illinois.edu',
 'sp19-cs425-g58-04.cs.illinois.edu',
 'sp19-cs425-g58-05.cs.illinois.edu']

serverLetters = ['A', 'B', 'C', 'D', 'E']

def run(numVMs):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.

    serverDict = dict()

    for i in range(numVMs):
        channel = grpc.insecure_channel(str(serverVMs[i])+':50051')
        serverDict[serverLetters[i]] = mp3_pb2_grpc.GreeterStub(channel)

        response = serverDict[serverLetters[i]].begin(mp3_pb2.beginMessage(name='Client 1', begin='begin'))
        print("Sent begin to %s and recseived: " % serverLetters[i] + response.reply)

        # bensname = serverDict[serverLetters[i]].getValue(mp3_pb2.getMessage(name="BensMac", key='A.x'))
        # print("getValue received: " + bensname.message)

    print("Start the test!")

    response = serverDict['A'].getValue(mp3_pb2.getMessage(name='Cleint 1', key='A.x'))
    print("getValue %s" % key + "and received: " + response.reply)

    response = serverDict['A'].setValue(mp3_pb2.setMessage(name='Client 1', serverkeyvalue='A.x 1'))
    print("setValue %s" % keyvalue + " and received: " + response.reply)

    response = serverDict['B'].getValue(mp3_pb2.getMessage(name='Cleint 1', key='B.x'))
    print("getValue %s" % key + "and received: " + response.reply)

    for i in range(numVMs):
        response = serverDict[serverLetters[i]].commit(mp3_pb2.commitMessage(name='Client 1', message='commit'))
        print("Sent begin to %s and recseived: " % serverLetters[i] + response.reply)


if __name__ == '__main__':

    logging.basicConfig()

    run(int(sys.argv[1]))

