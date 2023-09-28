from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Config:
    # Get environment variables
    SERVER_IP = os.getenv('SERVER_IP')
    SERVER_PORT = os.getenv('SERVER_PORT')

