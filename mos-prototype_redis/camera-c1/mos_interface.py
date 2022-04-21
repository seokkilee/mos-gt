import grpc
from grpc._channel import _MultiThreadedRendezvous
import mos_object_pb2
import mos_object_pb2_grpc
import asyncio
from queue import Queue
from google.protobuf import json_format
import os
import sys
import pathlib

sys.path.insert(
    0, os.path.join(pathlib.Path(__file__).parent.resolve(), '../')
)

import mos_common
import redis_pipe

queue = Queue()


async def update_redis():
    """Read the streamed object queue and push objects to redis server

    Args:
        redis_client (redis.client.Redis): redis client connected to a running
            server
    """
    rpipe = redis_pipe.RedisPipe()
    while True:
        if not queue.empty():
            message = queue.get()
            rpipe.publish(json_format.MessageToDict(message))
        else:
            print('queue empty')
            pass
            await asyncio.sleep(1/1000)


async def get_stream():
    conf = mos_common.MOS_CONFIG['grpc-c1']
    channel = grpc.insecure_channel('{}:{}'.format(conf['host'], conf['port']))

    stub = mos_object_pb2_grpc.ObjectServiceStub(channel)

    request = mos_object_pb2.ObjectRequest()
    while True:
        try:
            responses = stub.streaming_object(request, 1)
            print('requested---------------------------------')
            for response in responses:
                print(response)
                queue.put(response)
                print('retrieved-----------------------------------')

                await asyncio.sleep(1/1000)
        except _MultiThreadedRendezvous as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                print('Server currently unavailable.')
                await asyncio.sleep(2)
            elif e.code() == grpc.StatusCode.DATA_LOSS:
                print('Data loss detected.')
                await asyncio.sleep(1/1000)
            elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                print('Request\'s deadline exceeded.')
                await asyncio.sleep(1/100)


async def main():
    tasks = [
        asyncio.create_task(get_stream()),
        asyncio.create_task(update_redis()),
    ]
    await asyncio.gather(*tasks)

    # requests = [mos_object_pb2.ObjectRequest(
    #     camera_id=cam_id
    # ) for cam_id in range(0, 3)]

    # responses = stub.streaming_object(request)
    # for response in responses:
    #     print(response)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
