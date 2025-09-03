import redis
import os
from dotenv import load_dotenv

load_dotenv()

class RedisClient: 
    _instance = None

    @classmethod
    def get_instance(cls): 
        if cls._instance is None:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            cls._instance = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        return cls._instance