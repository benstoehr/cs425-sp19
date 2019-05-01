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

# serverVMs = ['sp19-cs425-g58-01.cs.illinois.edu',
#  'sp19-cs425-g58-02.cs.illinois.edu',
#  'sp19-cs425-g58-03.cs.illinois.edu',
#  'sp19-cs425-g58-04.cs.illinois.edu',
#  'sp19-cs425-g58-05.cs.illinois.edu']

# serverLetters = ['A', 'B', 'C', 'D', 'E']

serverVMs = ['sp19-cs425-g58-10.cs.illinois.edu',
 'sp19-cs425-g58-09.cs.illinois.edu',
 'sp19-cs425-g58-08.cs.illinois.edu',
 'sp19-cs425-g58-07.cs.illinois.edu']

serverLetters = ['A', 'B', 'C', 'D']

def run(numVMs):
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




if __name__ == '__main__':

    logging.basicConfig()

    run(int(sys.argv[1]))
