# Use it your own risk
# The Developer will not be responsible for any misuse of this bot/script
# This is only for educational purposes, dont misuse it
# If you use this bot/script, you accept that you are responsible for your own actions
import dns.resolver 
dns.resolver.default_resolver=dns.resolver.Resolver(configure=False) 
dns.resolver.default_resolver.nameservers=['8.8.8.8']#!/usr/bin/env python3

import io
import string 
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, InputUserDeactivated
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import os
from time import time, strftime, gmtime
import traceback
import logging
import shutil
from config import Config
from rvdb import mydb
from pytz import timezone
from psutil import virtual_memory, cpu_percent
from rvdrive import GoogleDriveHelper
from util import *
from rvripper import *
from logging.handlers import RotatingFileHandler
from expiringdict import ExpiringDict
from time import time
import random
from urllib.parse import quote
from datetime import datetime

# the logging things
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "log.txt", maxBytes=50000000, backupCount=10
        ),
        logging.StreamHandler(),
    ],
)

log = logging.getLogger(__name__)

TGBot = Client("TGPaidBot",
               api_id=Config.API_ID,
               api_hash=Config.API_HASH,
               bot_token=Config.BOT_TOKEN,
               workers=50,
               max_concurrent_transmissions=200)

if Config.SESSION_STRING:
    TGUser = Client(
        "TGUserClient",
        session_string=Config.SESSION_STRING,
        api_id = Config.API_ID,
        api_hash = Config.API_HASH,
        sleep_threshold = 30,
        no_updates = True,
        max_concurrent_transmissions=200
    )

TGUser = None

USER_DATA = ExpiringDict(max_len=1000, max_age_seconds=60*60)
# Bot stats
BOT_UPSTATE = datetime.now(timezone('Asia/Kolkata')).strftime("%d/%m/%y %I:%M:%S %p")
BOT_START_TIME = time()
# THis is what the script will look for
CHECK_ONCE = []

ST1 = [ 
    [
        InlineKeyboardButton(text="Updates Channel", url="https://t.me/jv"),
        InlineKeyboardButton(text="Support Grp", url="https://t.me/jv")
    ],
    [
        InlineKeyboardButton(f"About", callback_data="About"),
        InlineKeyboardButton(f"Help", callback_data="Help"),
        InlineKeyboardButton(f"Contact Us", callback_data="ContactUs"),
    ],
    [
        InlineKeyboardButton(f"Usage", callback_data="usage"),
        InlineKeyboardButton(f"Plans", callback_data="plans"),   
    ]
]

PLANS_TEXT = '''**Here You will find all of our Premium Plans:-**
    🟡 **Plan 1:-**
        **Plan Name:-** `Free User`
        **Price:-** `0$`
        **DRM Video Limit:-** `0 Video`
        **validity:-** `lifetime`

    🟢 **Plan 2:-**
        **Plan Name:-** `Starter`
        **Price:- **
              **USD:-** `9$`
              **INR:-** `299₹`
        **DRM Video Limit:-** `100 Videos`
        **validity:-** `30 days`

    🔵 **Plan 3:-**
        **Plan Name:-** `Standard`
        **Price:-** 
              **USD:-** `13$`
              **INR:-** `899₹`
        **DRM Video Limit:-** `Unlimited Videos`
        **validity:-** `30 days`

    
⚠️𝗧𝗲𝗿𝗺 𝗮𝗻𝗱 𝗖𝗼𝗻𝗱𝗶𝘁𝗶𝗼𝗻𝘀⚠️

• Payments are non-refundable, and we do not provide refunds.
• If the service ceases to function, no compensation is provided.

Payment Method:- Binance
For **INR:-** PhonePay, PayTm, UPI

**Contact  @JV For Subscription**'''

HELP_TEXT = """Here You can find all available Commands:-
    /start :- To start The Bot
    /help :- Show Help & Features
    /ul_mode :- See available features
    /plans :- See available plans
    /usage :- See your current usage
    /otts - To know available otts
    /about - about the bot
    /getthumb - get save thumb
    /delthumb - delete saved thumb
    send any photo to save it as thumb


Just send me any DRM links from supported sites to download That I can also Upload To Google Drive..."""


ABOUT_TEXT = """**🄳🅁🄼 🄳🄾🅆🄽🄻🄾🄳🄴 🄱🄾🅃

  ➺ My Name  : HS Download Bot
  ➺ Version      :  `v1.0.0`
  ➺ Language  : `English`
  ➺ Owner        : `JV`
  ➺ Release     : `India`
  ➺ Developer  : @JV

╚════════✧❁✧════════➩"""

async def filter_subscription(_, __, m):
    chkUser = await is_subscribed(m.from_user.id)
    if m.from_user.id in Config.OWNER_ID:
        return True
    if chkUser:
        return True
    await mydb.add_user(m.from_user.id)
    await m.reply_text("❎ You do not have a subscription\n\n📞 Contact us to buy a subscription [Sadiya](https://t.me/JV)")
    return False

static_auth_filter = filters.create(filter_subscription)


@TGBot.on_callback_query(filters.regex(pattern="^(Help|usage|ContactUs|About|plans)$"))
async def callback(_, cb: CallbackQuery):
    if cb.data == "About":
       await cb.edit_message_text(text=ABOUT_TEXT, reply_markup=InlineKeyboardMarkup(ST1), disable_web_page_preview=True)
    if cb.data == "usage":
       user_id = cb.from_user.id
       msg = await get_subscription(user_id)
       await cb.edit_message_text(text=msg, reply_markup=InlineKeyboardMarkup(ST1), disable_web_page_preview=True)
    if cb.data == "Help":
       await cb.edit_message_text(text=HELP_TEXT, reply_markup=InlineKeyboardMarkup(ST1), disable_web_page_preview=True)
    if cb.data == "plans":
       await cb.edit_message_text(text=PLANS_TEXT, reply_markup=InlineKeyboardMarkup(ST1), disable_web_page_preview=True)
    if cb.data == "ContactUs":
       await cb.edit_message_text(text=f"**📞 Contact [Jv](https://t.me/jv)**", reply_markup=InlineKeyboardMarkup(ST1), disable_web_page_preview=True)
        

@TGBot.on_message(filters.command("sub") & filters.user(Config.OWNER_ID))
async def tg_subget_Handler(bot: Client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        user_id = message.text.split(" ", 1)[1]
    msg_ = await get_subscription(user_id)
    await message.reply_text(msg_)

@TGBot.on_message(filters.command(["ott", "otts"]))
async def tg_subget_Handler(bot: Client, message: Message):
    await message.reply_text("""DRM Downloder Bot

⭐️ Hotstar 
""")

async def filter_mode(_, __, m):
    if m.text and m.text.lower() in ["gdrive", "telegram"]:
        return True
    else:
        return False

@TGBot.on_message(filters.create(filter_mode) & filters.private & static_auth_filter)
async def set_upload_mode(bot, msg):
    await mydb.set_ul_mode(msg.from_user.id, msg.text.lower())
    await msg.reply_text(f"✅ Upload mode set to {msg.text}", reply_markup=ReplyKeyboardRemove())

@TGBot.on_message(filters.command(["upload_mode", "ul_mode", "mode", "toggle"]) & filters.private & static_auth_filter)
async def upload_mode(bot, msg):
    my_akeyboards = [
                    [KeyboardButton("gdrive"), KeyboardButton("telegram")]
                     ]
    await msg.reply_text(text="**⬆️ Select upload mode ⬇️**",
                                    reply_markup=ReplyKeyboardMarkup(my_akeyboards,
                                                                     selective=True,
                                                                     resize_keyboard=True))
    

@TGBot.on_message(filters.command(["myplan", "usage"]))
async def tg_infoget_Handler(bot: Client, message: Message):
    user_id = message.from_user.id
    await mydb.add_user(user_id)
    msg_ = await get_subscription(user_id)
    await message.reply_text(msg_)


async def get_subscription(user_id):
    if user_id in Config.OWNER_ID:
        return "👑 No limit for this user, infinite downloads allowed 👑"
    chkUser = await mydb.get_user(user_id)
    if chkUser:
        expiryDate = chkUser.get("expiry")
        balance = chkUser.get("balance")
        start_date = chkUser.get("start")
        #start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S.%f") 
        now_date = datetime.now()
        msg = f"""**Subscription details:**

**    🎊 Current Plan: `Prime User (All)`
**          **Plan Name -** `Pro`
**          Is Premium - `All`
**        **Task Limit - ** `Unlimited`
**         👑 user**: `{user_id}`
**         🎦 videos**: `{balance}`
**         ⏳ expires**: `{expiryDate - (now_date-start_date).days} days`

⬆️ If you want to increase the subscription then see the plan now and contact us admin

  **🥰 @JV Contact owner for updating subscription.**

               **Have a Nice day 😊** """
    else:
        msg = "**Subscription details:**\n\n    **🎊 Current Plan:** `No Plan`\n          **Plan Name -** `Free`\n          **Is Premium -** `No`\n          **Task Limit -** `No Have`\n     **👑 user:** `Free User`\n     **🎦 videos:** `0 Video`\n     **⏳ expires:** `0 Days`\n\n**🥰 @JV Contact owner for updating subscription.**\n\n               **Have a Nice day 😊**"
    return msg

@TGBot.on_message(filters.command(["plans", "plan"]))
async def plans(bot: Client, message: Message):
    await message.reply_text(text=PLANS_TEXT, reply_markup=InlineKeyboardMarkup(ST1))

async def send_msg(user_id, message):
    try:
        await message.copy(user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        log.exception(e)
        return 500, f"{user_id} : {traceback.format_exc()}\n"

@TGBot.on_message(filters.command(["b", "broadcast"]) & filters.user(Config.OWNER_ID))
async def broadcasthandler(bot: Client, message: Message):
    try:
        broadcast_msg = message.reply_to_message
        if not broadcast_msg:
            return await message.reply_text("Please reply to message for broadcasting...")
        await message.reply_text("broadcast request recived, you will be notified once broadcast done", quote=True)
        some_users = await mydb.get_all_users()
        total_users = await mydb.total_users_count()
        broadcast_filename = "".join([random.choice(string.ascii_letters) for i in range(5)])
        broadcast_log = ""
        done = 0
        failed = 0
        success = 0
        log_file = io.BytesIO()
        log_file.name = f"broadcast_{broadcast_filename}.txt"
        async for user in some_users:
            sts, msg = await send_msg(
                user_id = user['_id'],
                message = broadcast_msg
            )
            if msg is not None:
                broadcast_log += msg
            if sts == 200:
                success += 1
            else:
                failed += 1
            done += 1
        log_file.write(broadcast_log.encode())
        if failed == 0:
            await message.reply_text(
            text=f"Broadcast completed`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True,
        )
        else:
            await message.reply_document(
            document=log_file,
            caption=f"Broadcast completed\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True,
        )
    except Exception as erro:
        log.exception(erro)
        pass


@TGBot.on_message(filters.command(["status", "stats"]) & filters.user(Config.OWNER_ID))
async def status_msg(bot, update):
  await mydb.add_user(update.from_user.id)
  currentTime = strftime("%H:%M:%S", gmtime(time() - BOT_START_TIME))
  total, used, free = shutil.disk_usage(".")
  total, used, free = humanbytes(total), humanbytes(used), humanbytes(free)
  cpu_usage = cpu_percent()
  ram_usage = f"{humanbytes(virtual_memory().used)}/{humanbytes(virtual_memory().total)}"
  msg = f"**Bot Current Status**\n\n**Bot Uptime:** {currentTime} \n\n**Total disk space:** {total} \n**Used:** {used} \n**Free:** {free} \n**CPU Usage:** {cpu_usage}% \n**RAM Usage:** {ram_usage}\n**Restarted on** `{BOT_UPSTATE}`"
  await update.reply_text(msg, quote=True)


@TGBot.on_message(filters.command("clean") & filters.user(Config.OWNER_ID))
async def cleanHandler(bot: Client, message: Message):
    global USER_DATA, BOT_UPSTATE, BOT_START_TIME
    open("log.txt", "w").write("")
    os.system("rm -rf output/*")
    os.system(f"rm -rf {Config.TEMP_DIR}/*")
    USER_DATA = ExpiringDict(max_len=1000, max_age_seconds=60*60)
    BOT_UPSTATE = datetime.now(timezone('Asia/Kolkata')).strftime("%d/%m/%y %I:%M:%S %p")
    BOT_START_TIME = time()
    await message.reply_text("Cache cleaned ✅")

@TGBot.on_message(filters.command("auth") & filters.user(Config.OWNER_ID))
async def tg_auth_Handler(bot: Client, message: Message):
    if message.reply_to_message:
        _, balance, days = message.text.split(" ")
        expiryDate = int(days)
        balance = int(balance)
        from_user = message.reply_to_message.from_user
    else:
        try:
            _, user_id, balance, days = message.text.split(" ")
            from_user = await bot.get_users(int(user_id))
            expiryDate = int(days)
            balance = int(balance)
        except:
            return await message.reply_text("send along with proper format or reply to user msg")
    await mydb.set_user(from_user.id, expiryDate, balance)
    await message.reply_text(f"""**🟡 New User added**
**⌛️ expiry**: `{expiryDate} days`
**🎦 Videos**: `{balance} videos`
👤 User Details:
  user: {from_user.mention}
  id: `{from_user.id}`""")


@TGBot.on_message(filters.command("help"))
async def start_handler(bot: Client, message: Message):
    await mydb.add_user(message.from_user.id)
    await message.reply_text(text=HELP_TEXT, reply_markup=InlineKeyboardMarkup(ST1))

@TGBot.on_message(filters.command("about"))
async def start_handler(bot: Client, message: Message):
    await mydb.add_user(message.from_user.id)
    await message.reply_text(ABOUT_TEXT, reply_markup=InlineKeyboardMarkup(ST1))

@TGBot.on_message(filters.command("start"))
async def start_handler(bot: Client, message: Message):
    print("hello")
    await mydb.add_user(message.from_user.id)
    await message.reply_text(text=f"""**Hello👋 {message.from_user.mention} I am one and only DRM Downloader Bot on Telegram.

You can use me to Download DRM protected links to Telegram ⤵️

Here I support Direct DRM links of Zee5, Hotstar etc..................

I can also DRM protected links transloaded from @JV 

If you found any issue please contact Support @JV**


**Bot Uptime:**  `{strftime("hours:%H minutes:%M and seconds:%S" , gmtime(time() - BOT_START_TIME))} ago`""", reply_markup=InlineKeyboardMarkup(ST1))
                   

async def upload_to_gdrive(bot, input_str, sts_msg, message):
    if os.path.isdir(input_str) and len(getListOfFiles(input_str)) == 0:
        return
    up_dir, up_name = input_str.rsplit('/', 1)
    gdrive = GoogleDriveHelper(up_name, up_dir, bot.loop, sts_msg)
    size = get_path_size(input_str)
    success = await sync_to_async(bot.loop, gdrive.upload, up_name, size)
    msg = sts_msg.reply_to_message if sts_msg.reply_to_message else sts_msg
    if isinstance(success, str):
        return
    if success:
        url_path = quote(f'{up_name}')
        share_url = f'{Config.INDEX_LINK}/{url_path}'
        if success[3] == "Folder":
            share_url += '/'
        sent = await msg.reply_text(
            f"""**File Name:** `{success[4]}`
**Size:** `{humanbytes(success[1])}`
**Type:** `{success[3]}`
**Total Files:** `{success[2]}`

**CC**: {message.from_user.mention}
""",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="❤️‍🔥 Cloud Link", url=success[0]),
                InlineKeyboardButton(text="⚡ Index Link", url=share_url)]]
                                ),
            disable_web_page_preview=True
          )
        await sent.copy(chat_id=Config.LOG_CHANNEL)
    else:
        await msg.reply_text("😔 Upload failed to gdrive")

        
@TGBot.on_message(filters.command("unauth") & filters.user(Config.OWNER_ID))
async def tg_unauth_Handler(bot: Client, message: Message):
    if message.reply_to_message:
         user_id = message.reply_to_message.from_user.id
         from_user = message.reply_to_message.from_user
    else:
        try:
            user_id = message.text.split(" ", 1)[1]
            from_user = await bot.get_users(int(user_id))
        except:
            return await message.reply_text("send along with I'd or reply to user msg")
    try:
        user_id = int(user_id)
    except:
        return await message.reply_text("send along with I'd or reply to user msg")
    await mydb.delete_user(user_id)
    await message.reply_text(f"Now {from_user.id} can not use me")

@TGBot.on_message(filters.command(["logs", "log"]) & filters.user(Config.OWNER_ID))
async def tg_unauth_Handler(bot: Client, message: Message):
    if os.path.exists("log.txt"):
        await message.reply_document("log.txt")
        return

#dont edit this
@TGBot.on_callback_query(filters.regex(pattern="^video"))
async def video_handler(bot: Client, query: CallbackQuery):
    global CHECK_ONCE
    _, key, video = query.data.split("#", 2)
    if query.from_user.id not in USER_DATA:
        await query.answer("You are not authorized to use this button.", show_alert=True)
        return
    check_user = await is_subscribed(query.from_user.id)
    if not check_user:
        await query.answer("You are not subscribed to use this bot.", show_alert=True)
        return
    if key not in USER_DATA[query.from_user.id]:
        await query.answer("Session expired, please try again.", show_alert=True)
        return 
    if key in USER_DATA[query.from_user.id]:
        #if len(USER_DATA[query.from_user.id][key]["audios"]) == 0 and USER_DATA[query.from_user.id][key]["audios_count"] >= 2:
        #    await query.answer("No audio streams found, please try again.", show_alert=True)
        #    return
        drm_client = USER_DATA[query.from_user.id][key]
        if drm_client:
            list_audios = USER_DATA[query.from_user.id][key]["audios"]
            drm_client = USER_DATA[query.from_user.id][key]["client"]
            jvname = USER_DATA[query.from_user.id][key]["jvname"]
            file_pth = USER_DATA[query.from_user.id][key]["folder"]
            file_pth = os.path.join(Config.TEMP_DIR, file_pth)
            await query.message.edit("⏱ Please wait downloading in progress ⤵️")
            rcode = await drm_client.downloader(video.strip(), list_audios, query.message)
            #await sts_.edit(f"Video downloaded in {file_pth}")
            upload_mode = await mydb.get_ul_mode(query.from_user.id)
            try:
                await query.message.edit(f"⬆️ Please wait starting **{upload_mode}** upload \n\n**📂 Filename:**\n `{jvname}`")
                sts = query.message
            except:
                sts = await query.message.reply_text(f"**⬆️ Please wait starting {upload_mode} upload \n\n**📂 Filename:**\n** `{jvname}`")
            if os.path.exists("token.pickle") and upload_mode == "gdrive":
                for fileP in os.listdir(file_pth):
                    await upload_to_gdrive(bot, os.path.join(file_pth, fileP), sts, query)
                try:
                    await sts.delete()
                except:
                    pass
            else:
                await upload_handler(file_pth, query.from_user.id, sts)
                try:
                    await sts.delete()
                except:
                    pass
            await mydb.set_user(user_id=query.from_user.id, balance = 0 - drm_client.COUNT_VIDEOS)
            if os.path.exists(file_pth):
                shutil.rmtree(file_pth)
            #await query.message.edit("Error occured, contact dev for fixing.")
        else:
            await query.answer("Session expired, please try again.", show_alert=True)
        try:
            CHECK_ONCE.remove(query.from_user.id)
        except:
            pass


#dont edit this
@TGBot.on_callback_query(filters.regex(pattern="^audio"))
async def audio_handler(bot: Client, query: CallbackQuery):
    _, key, audio = query.data.split("#", 2)
    if query.from_user.id not in USER_DATA:
        await query.answer("You are not authorized to use this button.", show_alert=True)
        return
    if key not in USER_DATA[query.from_user.id]:
        await query.answer("Session expired, please try again.", show_alert=True)
        return 
    if audio=="process":
        if key in USER_DATA[query.from_user.id]:
            videos_q = await USER_DATA[query.from_user.id][key]["client"].get_videos_ids()
            markup = create_buttons(list([key]+videos_q), True)
            #log.info(str(markup))
            await query.edit_message_text(f"**⚙ Choose Quality: ✅**", reply_markup=markup)
    else:
        audio, coice = audio.split("|", 1)
        if coice == "1":
            USER_DATA[query.from_user.id][key]["audios"].append(audio.strip())
            markup = MakeCaptchaMarkup(query.message.reply_markup.inline_keyboard, query.data, f"✓ {LANGUAGE_SHORT_FORM.get(audio.lower(), audio)}")
        if coice == "0":
            USER_DATA[query.from_user.id][key]["audios"].remove(audio.strip())
            markup = MakeCaptchaMarkup(query.message.reply_markup.inline_keyboard, query.data, f"{LANGUAGE_FULL_FORM.get(audio.lower(), audio)}")
        await query.message.edit_reply_markup(InlineKeyboardMarkup(markup))

async def drm_dl_client(update, MpdUrl, command, sts_msg):
    try:
        user_fol = str(time())
        xcodec = ""
        MpdUrl = MpdUrl.replace(" -s ", ":", 1).replace(" -e ", ":", 1)
        if " " in MpdUrl:
            MpdUrl, xcodec = MpdUrl.split(" ",1)
        xcodec = xcodec.lower()
        #if ("jiovoot" in MpdUrl) or ("jc" in command) or ("jiocinema" in MpdUrl):
        #    drm_client
        if "hotstar" in MpdUrl or "hs" in command:
            available_xcodec = ["4k", ""]
            if xcodec.split("-", 1)[0] not in available_xcodec:
                return await sts_msg.edit(f"{xcodec} not found, please send cmd with correct codec\n\n{', '.join(available_xcodec)}\n\nAdd -a in codec for dolby5.1\nadd -d in codec for atmos\n\neg: x265-a")
            drm_client: HotStar = HotStar(MpdUrl, user_fol, xcodec)
        title = await drm_client.get_input_data()
        if isinstance(title, tuple):
            title, is_done = title
            if not is_done:
                return await sts_msg.edit(title)
        randStr = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5))
        #passing the randStr to use it as a key for the USER_DATA dict
        user_choice_list = await drm_client.get_audios_ids(randStr)
        USER_DATA[update.from_user.id] = {}
        USER_DATA[update.from_user.id][randStr] = {}
        USER_DATA[update.from_user.id][randStr]["client"] = drm_client
        USER_DATA[update.from_user.id][randStr]["audios"] = []
        USER_DATA[update.from_user.id][randStr]["audios_count"] = len(user_choice_list)
        USER_DATA[update.from_user.id][randStr]["folder"] = user_fol
        USER_DATA[update.from_user.id][randStr]["jvname"] = title
        my_buttons = create_buttons(user_choice_list)
        await update.reply_text(f"**🔉 Choose Audios for**\n📂 **Filename**: `{title}`: **", reply_markup=my_buttons)
        await sts_msg.delete()
    except Exception as e:
        log.exception(e)
        await sts_msg.edit("🫨 Failed to fetch data from server.")
    finally:
        try:
            CHECK_ONCE.remove(update.from_user.id)
        except:
            pass

#adjust this cmd according to you
@TGBot.on_message(filters.command(["hs", "zee5", "rip", "dl"], prefixes=["/", "!"]) & static_auth_filter)
async def main_handler(bot: Client, m: Message):
    global CHECK_ONCE
    if (m.from_user.id not in Config.OWNER_ID) and m.from_user.id in CHECK_ONCE:
        return await m.reply_text("Your a task already going on, so please wait....\n\nThis method was implemented to reduce the overload on bot. So please cooperate with us.")
    command, user_iput = m.text.split(" ", 1)
    if len(user_iput) < 1:
        await m.reply_text("**Send A Message Containing Link To Download It.**")
    else:
        sts_msg = await m.reply_text(f"`` **🔍 Searching For Data ⚡️....**\n`` Link: `{user_iput}`")
    await drm_dl_client(m, user_iput.strip(), command, sts_msg)

def get_thumnail_path(user_id):
    if not os.path.exists("Thumbs"):
        os.makedirs("Thumbs", exist_ok=True)
    return os.path.join("Thumbs", str(user_id) + ".jpg")

@TGBot.on_message(filters.photo & static_auth_filter)
async def sav_Thumb_Handler(bot: Client, message: Message):
    sts_msg = await message.reply_text("Please wait ...")
    await message.download(get_thumnail_path(str(message.from_user.id)))
    await sts_msg.edit("Custom thumbnail saved ✅....")

@TGBot.on_message(filters.command("getthumb") & static_auth_filter)
async def tg_Uploader_Handler(bot: Client, message: Message):
    thumb_path = get_thumnail_path(str(message.from_user.id))
    if os.path.exists(thumb_path):
        await message.reply_photo(thumb_path, caption="Thumbnail")
    else:
        await message.reply_text("❎ Thumbnail not found, send photo to save thumbnail.")

@TGBot.on_message(filters.command("delthumb") & static_auth_filter)
async def tg_Uploader_Handler(bot: Client, message: Message):
    thumb_path = get_thumnail_path(str(message.from_user.id))
    if os.path.exists(thumb_path):
        os.remove(thumb_path)
        await message.reply_text("Thumbnail deleted successfully ✅")
    else:
        await message.reply_text("❎ Thumbnail not found, send photo to save thumbnail.")

async def upload_handler(file_path:str, user_id, sts_msg):
    user_id = str(user_id)
    if os.path.isdir(file_path):
        all_files = getListOfFiles(file_path)
        for filePath in all_files:
            await upload_handler(filePath, user_id, sts_msg)
        try:
            #try to remove dir
            shutil.rmtree(file_path)
        except:
            pass
    if os.path.exists(file_path):
        file_name_ = os.path.basename(file_path)
        if os.path.getsize(file_path) > Config.TG_SPLIT_SIZE:
            d_f_s = humanbytes(os.path.getsize(file_path))
            await sts_msg.edit(
                "Telegram does not support uploading this file.\n"
                f"Detected File Size: {d_f_s}\n"
                "\n😔 trying to split the file\n\n"
                f"File: `{file_name_}`"
            )
            splitted_dir = await split_large_files(file_path)
            listOfFile = os.listdir(splitted_dir)
            listOfFile.sort()
            num_of_files = len(listOfFile)
            await sts_msg.edit(
                f"Detected File Size: {d_f_s}\n"
                f"File: `{file_name_}`\n"
                f"Splited into {num_of_files} parts."
            )
            for entry in listOfFile:
                fullPath = os.path.join(splitted_dir, entry)
                await tg_uploader(fullPath, user_id, sts_msg)
            try:
                #try to remove dir
                shutil.rmtree(splitted_dir)
            except:
                pass
        else:
            await tg_uploader(file_path, user_id, sts_msg)

async def tg_uploader(input_str, user_id, sts_msg):
    #block drm video
    if input_str.endswith("_jv.mp4"):
        try:
            os.remove()
        except:
            pass
        return
    current_time = time()
    if get_path_size(input_str) > 2147483648:
        client = TGUser
    else:
        client = TGBot
    user_thumb_path = get_thumnail_path(user_id)
    if os.path.exists(user_thumb_path):
        thumb = user_thumb_path
    else:
        thumb = None
        user_thumb_path = None
    file_name = os.path.basename(input_str)
    my_caption = f"**Filename**: `{file_name}`\n**Size**: `{humanbytes(get_path_size(input_str))}`"
    #my_caption += f"\n**CC**: {message.from_user.mention}"
    if check_is_streamable(file_name):
        try:
            duration = await get_video_duration(input_str)
        except:
            duration = None
        my_caption += f"\n**Duration**: `{TimeFormatter(duration)}`"
        if thumb is None:
            thumb = await take_ss(input_str)
        sent_msg = await client.send_video(chat_id=Config.LOG_CHANNEL,
                                video=input_str,
                                  thumb=thumb,
                                  caption=my_caption,
                                  duration=duration,
                                  progress=progress_for_pyrogram,
                                  progress_args=("Uploading",
                                                 sts_msg,
                                                 current_time,
                                                 file_name))
    elif check_is_audio(file_name):
        try:
            duration = await get_video_duration(input_str)
        except:
            duration = None
        my_caption += f"\n**Duration**: `{TimeFormatter(duration)}`"
        if thumb is None:
            thumb = take_ss(input_str)
        sent_msg = await client.send_audio(chat_id=Config.LOG_CHANNEL,
                                  audio=input_str,
                                  thumb=thumb,
                                  duration=duration,
                                  caption=my_caption,
                                  progress=progress_for_pyrogram,
                                  progress_args=("Uploading",
                                                 sts_msg,
                                                 current_time,
                                                 file_name))
    else:
        sent_msg = await client.send_document(chat_id=Config.LOG_CHANNEL,
                                  document=input_str,
                                  thumb=thumb,
                                  caption=my_caption,
                                  progress=progress_for_pyrogram,
                                  progress_args=("Uploading",
                                                 sts_msg,
                                                 current_time,
                                                 file_name))
    await TGBot.copy_message(user_id, Config.LOG_CHANNEL, sent_msg.id)
    if user_thumb_path is None and thumb is not None:
        try:
            os.remove(thumb)
        except:
            pass

async def StartBot():
    await TGBot.start()
 #   if TGUser:
#        await TGUser.start()
    print("----------Bot Started----------")
    await idle()
    await TGBot.stop()
  #  if TGUser:
   #     await TGUser.stop()
    print("----------Bot Stopped----------")
    print("--------------BYE!-------------")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(StartBot())
