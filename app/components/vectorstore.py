from langchain_community.vectorstores import FAISS

from app.components.embeddings import get_embedding_model

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

from app.config.config import DB_FAISS_PATH

import os

logger = get_logger(__name__)

def load_vector_store():
    try:
        embedding_model = get_embedding_model()

        if os.path.exists(DB_FAISS_PATH):
            logger.info(f"Loading existing vectorstore...")
            return FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
        else:
            logger.warning(f"No Vectostore found.")
    except Exception as e:
        logger.error(f"Error loading vector store: {e}")
        raise CustomException("Error loading vector store", e)


# Creating new vectorstore
def save_vector_store(text_chunks):
    try:
        if not text_chunks:
            raise CustomException("No Chunks were found...")
        
        logger.info("Generating new vectorstore...")

        embedding_model = get_embedding_model()

        db = FAISS.from_documents(text_chunks, embedding_model)

        logger.info(f"Saving vectorstore")

        db.save_local(DB_FAISS_PATH)    

        logger.info("Vectorstore saved successfully.")

        return db

    except Exception as e:
        logger.error(f"Error saving vector store: {e}")
        raise CustomException("Error saving vector store", e)