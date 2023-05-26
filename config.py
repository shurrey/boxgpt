""" Application configurations """
import os
from dotenv import load_dotenv


class AppConfig:
    """application configurations"""

    def __init__(self) -> None:
        load_dotenv()
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")

    def __repr__(self) -> str:
        return f"AppConfig({self.__dict__})"