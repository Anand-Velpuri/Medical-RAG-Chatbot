import os
from app.components.pdf_loader import load_pdf_files, create_text_chunks
from app.components.vectorstore import save_vector_store
from app.config.config import DB_FAISS_PATH

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

def process_and_store_pdfs():
    try:
        logger.info("Making the vectorstore...")
        logger.info("Loading pdf files")
        documents = load_pdf_files()

        text_chunks = create_text_chunks(documents)

        save_vector_store(text_chunks)

        logger.info("Vectorstore created successfully.")

    except Exception as e:
        logger.error(f"Error processing and storing PDFs: {e}")
        raise CustomException("Error processing and storing PDFs", e)

if __name__ == "__main__":
    try:
        if os.path.exists(DB_FAISS_PATH):
            logger.info("Vectorstore already exists. Skipping PDF processing.")
        else:
            process_and_store_pdfs()
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise CustomException("Error in main execution", e)