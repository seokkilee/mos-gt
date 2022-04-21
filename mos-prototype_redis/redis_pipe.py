import redis
import pickle
import mos_common


class Serializer:
    serialize = pickle.dumps
    deserialize = pickle.loads


class RedisPipe:
    def __init__(self, serializer=Serializer):
        self.config = mos_common.MOS_CONFIG['redis']
        # redis_client = redis.asyncio(host='127.0.0.1')
        self.redis = redis.Redis(
            host=self.config['host'],
            port=self.config['port'],
        )
        self.serializer = serializer

    def publish(self, obj):
        """example
        conn = RedisPipe()
        conn.publish({"a": 1, "b": object()})
        """
        self.redis.publish(
            channel=self.config['stream_name'],
            message=self.serializer.serialize(obj)
        )

    def subscribe_pipe(self):
        """Consume a data from the channel.
        This blocks the execution until a data is available.

        example
        for data in RedisPipe().subscribe_pipe(): # Infinite loop.
            print(data)
        """
        out = self.redis.pubsub()
        out.subscribe(self.config['stream_name'])

        class SubPipe:
            def __init__(self, chan, serializer):
                self.chan = chan
                self.serializer = serializer

            def __next__(self):
                return self.serializer.deserialize(self.chan.get_message())

        return SubPipe(out, self.serializer)
