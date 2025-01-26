import motor.motor_asyncio
from config import Config
from datetime import datetime
import certifi

ca = certifi.where()

class manage_db():
    def __init__(self):
        self.db = motor.motor_asyncio.AsyncIOMotorClient(Config.DB_URL, tlsCAFile=ca)["RVDl"]
        self.user = self.db.users
        self.col = self.db.members
        

    async def is_exist(self, user_id):
        userkey = await self.col.find_one({'_id': user_id})
        if userkey:
            return True
        else:
            return False

    async def add_user(self, user_id):
        if not (await self.is_exist(user_id)):
            await self.col.insert_one({'_id': user_id})
    
    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users
  
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def set_user(self, user_id, expiry=0, balance=0):
        start_date = datetime.now()
        try:
            await self.user.insert_one({"_id": user_id, "expiry": expiry, "balance": balance, "start": start_date, "ul_mode": "gdrive"})
        except:
            userkey = await self.user.find_one({'_id': user_id})
            await self.user.update_one({"_id": user_id},
                                      {'$set':
                                             {'expiry': userkey["expiry"] + expiry,
                                              'balance': userkey["balance"] + balance}})
    
    async def get_user(self, user_id):
        userkey = await self.user.find_one({'_id': user_id})
        if userkey:
            return userkey
        else:
            return False
    
    async def set_ul_mode(self, user_id, ul_mode):
        await self.user.update_one({"_id": user_id}, {'$set': {'ul_mode': ul_mode}})
    
    async def get_ul_mode(self, user_id):
        userkey = await self.user.find_one({'_id': user_id})
        if userkey:
            return userkey["ul_mode"]
        else:
            return "gdrive"
    
    async def delete_user(self, user_id):
        await self.user.delete_one({"_id": user_id})


mydb = manage_db()
