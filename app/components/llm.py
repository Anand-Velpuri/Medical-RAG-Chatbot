from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from app.config.config import HF_TOKEN, HUGGINGFACE_REPO_ID

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)


def load_llm(huggingface_repo_id: str = HUGGINGFACE_REPO_ID, hf_token: str = HF_TOKEN):
    try:
        logger.info("Loading LLM from HuggingFace")

        llm_endpoint = HuggingFaceEndpoint(
            repo_id=huggingface_repo_id,
            huggingfacehub_api_token=hf_token,
            temperature=0.3,
            max_new_tokens=256,
            return_full_text=False,
            task="text-generation"
        )

        chat_model = ChatHuggingFace(llm=llm_endpoint)


        logger.info("LLM loaded successfully")

        return chat_model

    except Exception as e:
        logger.error(f"Error loading LLM: {e}")
        raise CustomException(f"Error loading LLM: {e}")