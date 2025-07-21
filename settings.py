from dotenv import load_dotenv
import os


load_dotenv()



api_key=os.getenv("API_KEY", None)
api_version=os.getenv("API_VERSION", None)
azure_endpoint=os.getenv("AZURE_ENDPOINT", None)