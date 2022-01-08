from dotenv import load_dotenv
import os


class Config:
    def __init__(self):
        self.env = load_dotenv()
        
    def __getitem__(self, item):
        return os.getenv(item)
