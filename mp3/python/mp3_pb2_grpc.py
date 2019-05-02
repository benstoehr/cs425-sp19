# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import mp3_pb2 as mp3__pb2


class CoordinatorStub(object):
  """The greeting service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SayHi = channel.unary_unary(
        '/mp3.Coordinator/SayHi',
        request_serializer=mp3__pb2.HiRequest.SerializeToString,
        response_deserializer=mp3__pb2.HiReply.FromString,
        )
    self.checkLock = channel.unary_unary(
        '/mp3.Coordinator/checkLock',
        request_serializer=mp3__pb2.checkMessage.SerializeToString,
        response_deserializer=mp3__pb2.checkReply.FromString,
        )


class CoordinatorServicer(object):
  """The greeting service definition.
  """

  def SayHi(self, request, context):
    """Sends a greeting
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def checkLock(self, request, context):
    """Sends a lock/commit/abort message to the coordinator
    The coordinator will reply OK or shouldAbort
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_CoordinatorServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SayHi': grpc.unary_unary_rpc_method_handler(
          servicer.SayHi,
          request_deserializer=mp3__pb2.HiRequest.FromString,
          response_serializer=mp3__pb2.HiReply.SerializeToString,
      ),
      'checkLock': grpc.unary_unary_rpc_method_handler(
          servicer.checkLock,
          request_deserializer=mp3__pb2.checkMessage.FromString,
          response_serializer=mp3__pb2.checkReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'mp3.Coordinator', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class GreeterStub(object):
  """------------------------------------------------------------------

  The greeting service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SayHello = channel.unary_unary(
        '/mp3.Greeter/SayHello',
        request_serializer=mp3__pb2.HelloRequest.SerializeToString,
        response_deserializer=mp3__pb2.HelloReply.FromString,
        )
    self.SayHelloAgain = channel.unary_unary(
        '/mp3.Greeter/SayHelloAgain',
        request_serializer=mp3__pb2.HelloRequest.SerializeToString,
        response_deserializer=mp3__pb2.HelloReply.FromString,
        )
    self.begin = channel.unary_unary(
        '/mp3.Greeter/begin',
        request_serializer=mp3__pb2.beginMessage.SerializeToString,
        response_deserializer=mp3__pb2.beginReply.FromString,
        )
    self.getValue = channel.unary_unary(
        '/mp3.Greeter/getValue',
        request_serializer=mp3__pb2.getMessage.SerializeToString,
        response_deserializer=mp3__pb2.getReply.FromString,
        )
    self.setValue = channel.unary_unary(
        '/mp3.Greeter/setValue',
        request_serializer=mp3__pb2.setMessage.SerializeToString,
        response_deserializer=mp3__pb2.setReply.FromString,
        )
    self.commit = channel.unary_unary(
        '/mp3.Greeter/commit',
        request_serializer=mp3__pb2.commitMessage.SerializeToString,
        response_deserializer=mp3__pb2.commitReply.FromString,
        )
    self.abort = channel.unary_unary(
        '/mp3.Greeter/abort',
        request_serializer=mp3__pb2.abortMessage.SerializeToString,
        response_deserializer=mp3__pb2.abortReply.FromString,
        )


class GreeterServicer(object):
  """------------------------------------------------------------------

  The greeting service definition.
  """

  def SayHello(self, request, context):
    """Sends a greeting
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SayHelloAgain(self, request, context):
    """Sends another greeting
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def begin(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def getValue(self, request, context):
    """TODO: getValue
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def setValue(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def commit(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def abort(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_GreeterServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SayHello': grpc.unary_unary_rpc_method_handler(
          servicer.SayHello,
          request_deserializer=mp3__pb2.HelloRequest.FromString,
          response_serializer=mp3__pb2.HelloReply.SerializeToString,
      ),
      'SayHelloAgain': grpc.unary_unary_rpc_method_handler(
          servicer.SayHelloAgain,
          request_deserializer=mp3__pb2.HelloRequest.FromString,
          response_serializer=mp3__pb2.HelloReply.SerializeToString,
      ),
      'begin': grpc.unary_unary_rpc_method_handler(
          servicer.begin,
          request_deserializer=mp3__pb2.beginMessage.FromString,
          response_serializer=mp3__pb2.beginReply.SerializeToString,
      ),
      'getValue': grpc.unary_unary_rpc_method_handler(
          servicer.getValue,
          request_deserializer=mp3__pb2.getMessage.FromString,
          response_serializer=mp3__pb2.getReply.SerializeToString,
      ),
      'setValue': grpc.unary_unary_rpc_method_handler(
          servicer.setValue,
          request_deserializer=mp3__pb2.setMessage.FromString,
          response_serializer=mp3__pb2.setReply.SerializeToString,
      ),
      'commit': grpc.unary_unary_rpc_method_handler(
          servicer.commit,
          request_deserializer=mp3__pb2.commitMessage.FromString,
          response_serializer=mp3__pb2.commitReply.SerializeToString,
      ),
      'abort': grpc.unary_unary_rpc_method_handler(
          servicer.abort,
          request_deserializer=mp3__pb2.abortMessage.FromString,
          response_serializer=mp3__pb2.abortReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'mp3.Greeter', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
