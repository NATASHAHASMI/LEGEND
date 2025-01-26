import os
from dotenv import load_dotenv

if os.path.exists("config.env"):
    load_dotenv('config.env', override=True)

class Config(object):
    ##API_KEY get it from dev, dont edit if added
    API_KEY = os.environ.get("API_KEY", "rv2006rv")
    #telegram user session str for 4gb limit
    SESSION_STRING = os.environ.get("SESSION_STRING", "")
    #tg bot token
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7883714062:AAFoQy27Bcc_WwtIw57MvicmWPrO96kcnbg")
    #api id and hash get it from my.telegram.org
    API_ID = int(os.environ.get("API_ID", ))
    API_HASH = os.environ.get("API_HASH", "")
    #Proxy url leave blank if dont have, eg "http://13.42.34.52:52380"
    PROXY = os.environ.get("PROXY", "")
    #mongodb url get it from mongodb.com
    DB_URL = os.environ.get("DB_URL", "")
    #owner id
    OWNER_ID = [int(i) for i in  os.environ.get("OWNER_ID", "").split(" ")]
    #log channel, where to send logs
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))
    #gdrive folder id for upload
    GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "")
    #use service accounts or not, used to bypass daily upload limit
    USE_SERVICE_ACCOUNTS = os.environ.get("USE_SERVICE_ACCOUNTS","False")
    #is team drive
    IS_TEAM_DRIVE = os.environ.get("IS_TEAM_DRIVE", "False")
    #index url of gdrive folder
    INDEX_LINK = os.environ.get("INDEX_LINK", "https://widewine.example.workers.dev/0:/BOT")
    #Metadata and Name at end of file
    END_NAME = os.environ.get("END_NAME", "AV")
    METADATA_NAME = os.environ.get("METADATA_NAME", "AV")
    #ur choice
    TEMP_DIR = os.environ.get("TEMP_DIR", "output")
    TG_SPLIT_SIZE = int(os.environ.get("TG_SPLIT_SIZE","2000000000"))
    ##############Dont touch##############
    if SESSION_STRING == "" or SESSION_STRING is None:
        TG_SPLIT_SIZE = TG_SPLIT_SIZE
    USE_SERVICE_ACCOUNTS = USE_SERVICE_ACCOUNTS.lower() == "true"
    IS_TEAM_DRIVE = IS_TEAM_DRIVE.lower() == "true"
    HOTSTAR_REFRESH = 0.0

#tokens#
    HOTSTAR_USER_TOKEN = os.environ.get("HOTSTAR_USER_TOKEN", "")
    JIO_TOKEN = os.environ.get("JIO_TOKEN", "")
    Z5_TOKEN = os.environ.get("Z5_TOKEN", "")
    Sliv_TOKEN = os.environ.get("Sliv_TOKEN", "")
    Discovery_TOKEN = os.environ.get("Discovery_TOKEN", "")
    DPLAY_TOKEN = os.environ.get("DPLAY_TOKEN", "")
    Manorama_TOKEN = os.environ.get("Manorama_TOKEN", "")
    SUNNXT_Token = os.environ.get("SUNNXT_Token", "")
