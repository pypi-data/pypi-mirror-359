from uuid import uuid4

import chromadb.config
from cachelm.utils.chat_history import Message  # Use the correct import
from cachelm.databases.database import Database
from cachelm.vectorizers.vectorizer import Vectorizer
from loguru import logger

try:
    import chromadb
except ImportError:
    raise ImportError(
        "ChromaDB library is not installed. Run `pip install chromadb` to install it."
    )


class ChromaDatabase(Database):
    """
    Chroma database for caching.
    """

    def __init__(
        self,
        vectorizer: Vectorizer,
        unique_id: str = "cachelm",
        chromaSettings: chromadb.config.Settings = chromadb.config.Settings(),
        distance_threshold: float = 0.1,
        max_size: int = 100,
    ):
        super().__init__(vectorizer, unique_id, distance_threshold, max_size)
        self.client = None
        self.collection = None
        self.unique_id = unique_id
        self.chromaSettings = chromaSettings

    def __get_adapted_embedding_function(self, vectorizer: Vectorizer):
        class AdaptedEmbeddingFunction(chromadb.EmbeddingFunction):
            def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
                return vectorizer.embed_weighted_average_many(input)

        return AdaptedEmbeddingFunction()

    def reset(self):
        """
        Reset the database.
        """
        try:
            if self.client:
                self.client.delete_collection(self.unique_id)
                logger.info("Chroma database reset.")
                self.collection = self.client.get_or_create_collection(
                    self.unique_id,
                    embedding_function=self.__get_adapted_embedding_function(
                        self.vectorizer
                    ),
                )
                logger.info("Chroma database reconnected.")
        except Exception as e:
            logger.error(f"Error resetting Chroma: {e}")

    def connect(self) -> bool:
        try:
            self.client = chromadb.Client(settings=self.chromaSettings)
            self.collection = self.client.get_or_create_collection(
                self.unique_id,
                embedding_function=self.__get_adapted_embedding_function(
                    self.vectorizer
                ),
            )
            return True
        except Exception as e:
            logger.error(f"Error connecting to Chroma: {e}")
            return False

    def disconnect(self):
        pass

    def write(self, history: list[Message], response: Message):
        logger.info(f"Writing to Chroma: {history} -> {response}")
        try:
            history_strs = [msg.to_formatted_str() for msg in history]
            self.collection.add(
                ids=[str(uuid4())],
                documents=["\n".join(history_strs)],
                metadatas=[{"response": response.to_json_str()}],
            )
        except Exception as e:
            logger.error(f"Error writing to Chroma: {e}")

    def find(self, history: list[Message]) -> Message | None:
        try:
            history_strs = [msg.to_formatted_str() for msg in history]
            res = self.collection.query(
                query_texts=["\n".join(history_strs)], n_results=1
            )
            if res is not None and len(res.get("ids", [[]])[0]) > 0:
                distance = res.get("distances", [[1.0]])[0][0]
                logger.info(f"Distance: {distance}")
                if distance > self.distance_threshold:
                    logger.info(
                        f"Distance too high: {distance} > {self.distance_threshold}"
                    )
                    return
                response_str = res.get("metadatas", [[{}]])[0][0].get("response", None)
                if response_str is None:
                    logger.info("No response found")
                    return
                logger.info(f"Found in Chroma: {response_str[:100]}...")
                return Message.from_json_str(response_str)
            logger.info(f"Found in Chroma: {res}...")
            return
        except Exception as e:
            logger.error(f"Error finding from Chroma: {e}")
            return

    def size(self) -> int:
        """
        Get the size of the database.
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting size of Chroma: {e}")
            return 0
