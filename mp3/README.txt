USE THIS TO RECOMPILE

"python -m grpc_tools.protoc -I./protos --python_out=./python --grpc_python_out=./python ./protos/mp3.proto"

CALL THIS

eval $(ssh-agent -s) && ssh-add ~/.ssh/gitkey_rsa