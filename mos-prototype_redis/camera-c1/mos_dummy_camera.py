from concurrent import futures
import time
import datetime
import argparse
from queue import Queue
import grpc
import mos_object_pb2
import mos_object_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
import json
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    '--camera_id',
    type=int,
    default=0
)
args = arg_parser.parse_args()


class ObjectServiceServicer(mos_object_pb2_grpc.ObjectServiceServicer):
    """Provide methods that implement functionality to access the camera grpc
    server.

    Args:
        mos_object_pb2_grpc.ObjectServiceServicer (object): streamed object \
            from the camera module
    """

    def __init__(self):
        self.sample_frame = json.load(
            open('sample.json', 'r')
        )
        self.frame_num = 0
        self.queue = Queue()

        self.out_time = -1

        self.sample_object = self.read_json()
        for i in range(0, 1000):
            self.queue.put(self.sample_object)
        # for i in range(0, 120):
        #     self.queue.put(self.sample_frame)

    def read_json(self):
        """Read json file's content and turn into a object dataset defined in .proto

        The json file is loaded in `:function:__init__`

        Args:

        """
        streaming_object = mos_object_pb2.StreamingData()
        for obj in self.sample_frame['objectData']:
            obj_data = mos_object_pb2.ObjectData(
                object_id=obj['object_id'],
                type=obj['type'],
                coordinate=mos_object_pb2.Coordinate(
                    x=obj['coordinate']['x'],
                    y=obj['coordinate']['y']
                )
            )
            streaming_object.object_data.extend([obj_data])
        streaming_object.timestamp.FromJsonString(self.sample_frame['timestamp'])
        return streaming_object

    def streaming_object(self, request, context):

        print(time.perf_counter(), 'requested')
        # time.sleep(2)
        while True:
            if not self.queue.empty():
                objs = self.queue.get()
                yield objs
                print('answered')
            else:
                # Reset the queue for the purpose of testing
                # This is to simulate cases where camera streams stop for an amount
                # of time.
                if self.out_time == 999999:
                    self.out_time = time.perf_counter()
                    print(self.out_time)
                if time.perf_counter() - self.out_time >= 2:
                    print('Queue recharged.')
                    for i in range(0, 1000):
                        self.queue.put(self.sample_object)
                    self.out_time = 999999
        # objs = self.queue.get()
        # yield objs


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mos_object_pb2_grpc.add_ObjectServiceServicer_to_server(
        ObjectServiceServicer(),
        server
    )
    base_port = 50051
    server.add_insecure_port('[::]:{}'.format(base_port + args.camera_id))
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
