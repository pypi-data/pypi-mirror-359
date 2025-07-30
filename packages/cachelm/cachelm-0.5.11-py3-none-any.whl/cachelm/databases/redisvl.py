from loguru import logger

from cachelm.utils.chat_history import Message  # Updated import
from cachelm.databases.database import Database
from cachelm.vectorizers.vectorizer import Vectorizer

try:
    from redisvl.extensions.cache.llm import SemanticCache
    from redisvl.utils.vectorize import CustomTextVectorizer
except ImportError:
    raise ImportError(
        "RedisVL library is not installed. Run `pip install redisvl` to install it."
    )


class RedisVLDatabase(Database):
    """
    Redis database for caching.
    """

    def __init__(
        self,
        host: str,
        port: int,
        vectorizer: Vectorizer,
        unique_id: str = "cachelm",
        distance_threshold: float = 0.1,
        max_size: int = 100,
    ):
        super().__init__(vectorizer, unique_id, distance_threshold, max_size)
        self.host = host
        self.port = port
        self.cache = None

    def connect(self) -> bool:
        try:
            self.cache = SemanticCache(
                redis_url=f"redis://{self.host}:{self.port}",
                vectorizer=CustomTextVectorizer(
                    embed=self.vectorizer.embed_weighted_average,
                    embed_many=self.vectorizer.embed_weighted_average_many,
                ),
                name=self.unique_id,
            )
            return True
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            return False

    def disconnect(self):
        if self.cache:
            self.cache.disconnect()

    def reset(self):
        """
        Reset the database.
        """
        try:
            self.cache.clear()
            logger.info("Redis database reset.")
        except Exception as e:
            logger.error(f"Error resetting Redis: {e}")

    def write(self, history: list[Message], response: Message):
        """
        Write data to the Redis database.
        """
        try:
            prompt = "\n".join([msg.to_formatted_str() for msg in history])
            response_str = response.to_json_str()
            logger.info(f"Writing to Redis: {prompt} -> {response_str}")
            self.cache.store(
                prompt=prompt,
                response=response_str,
            )
        except Exception as e:
            logger.error(f"Error writing to Redis: {e}")

    def find(self, history: list[Message]) -> Message | None:
        """
        Find data in the database.
        """
        try:
            prompt = "\n".join([msg.to_formatted_str() for msg in history])
            res = self.cache.check(
                prompt=prompt,
                distance_threshold=self.distance_threshold,
            )
            if res is not None and len(res) > 0:
                response_str = res[0].get("response", "")
                logger.info(f"Found in Redis: {response_str[0:50]}...")
                return Message.from_json_str(response_str)
            return None
        except Exception as e:
            logger.error(f"Error finding from redis: {e}")
            return None

    def size(self) -> int:
        """
        Get the size of the database.
        """
        try:
            info = self.cache.index.info()
            return info.get("num_docs", 0)
        except Exception as e:
            logger.error(f"Error getting size from Redis: {e}")
            return 0
