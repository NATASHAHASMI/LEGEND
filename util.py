import asyncio
import logging
from pyrogram.types import Message
import time
import re
import os
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from asyncio import run_coroutine_threadsafe, sleep
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from config import Config


LOGGER = logging.getLogger(__name__)

AUDIO_SUFFIXES = ("MP3", "M4A", "M4B", "FLAC", "WAV", "AIF", "OGG", "AAC", "DTS", "MID", "AMR", "MKA")
VIDEO_SUFFIXES = ("M4V", "MP4", "MOV", "FLV", "WMV", "3GP", "MPG", "WEBM", "MKV", "AVI")
LANGUAGE_FULL_FORM = {"eng": "English", "hin": "Hindi", "hin": "Hindi", "tam": "Tamil", "tel": "Telugu", "mal": "Malayalam", "mar": "Marathi", "ben": "Bengali", "guj": "Gujarati", "kan": "Kannada", "pa": "Punjabi", "ur": "Urdu", "as": "Assamese", "or": "Oriya", "sa": "Sanskrit", "si": "Sinhala", "ne": "Nepali", "sd": "Sindhi", "ks": "Kashmiri", "km": "Khmer", "my": "Burmese", "bo": "Tibetan", "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "fr": "French", "de": "German", "it": "Italian", "es": "Spanish", "pt": "Portuguese", "ru": "Russian", "ar": "Arabic", "fa": "Persian", "ur": "Urdu", "he": "Hebrew", "id": "Indonesian", "ms": "Malay", "th": "Thai", "vi": "Vietnamese", "tr": "Turkish", "el": "Greek", "bg": "Bulgarian", "uk": "Ukrainian", "hy": "Armenian", "ka": "Georgian", "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian", "ca": "Catalan", "hr": "Croatian", "cs": "Czech", "da": "Danish", "et": "Estonian", "fi": "Finnish", "gl": "Galician", "hu": "Hungarian", "is": "Icelandic", "lv": "Latvian", "lt": "Lithuanian", "mk": "Macedonian", "mt": "Maltese", "no": "Norwegian", "pl": "Polish", "ro": "Romanian", "sk": "Slovak", "sl": "Slovenian", "sw": "Swahili", "sv": "Swedish", "tl": "Tagalog", "cy": "Welsh",}
LANGUAGE_SHORT_FORM = {"en": "ENG", "hi": "Hin", "hin": "Hin", "ta": "TAM", "te": "TEL", "ml": "MAL", "mr": "MAR", "bn": "BEN", "gu": "GUJ", "kn": "KAN", "pa": "Pun", "ur": "Urd", "as": "Ass", "or": "Ori", "sa": "San", "ne": "Nep", "sd": "Sin", "ks": "Kas", "km": "Khm", "my": "Bur", "bo": "Tib", "ja": "Jap", "ko": "Kor", "zh": "Chi", "fr": "Fre", "de": "Ger", "it": "Ita", "es": "Spa", "pt": "Por", "ru": "Rus", "ar": "Ara", "fa": "Per", "ur": "Urd", "he": "Heb", "id": "Ind", "tr": "Tur"}

THREADPOOL = ThreadPoolExecutor(max_workers=1000)

def check_is_streamable(file_path:str) -> bool:
    return file_path.upper().endswith(VIDEO_SUFFIXES)

def check_is_audio(file_path:str) -> bool:
    return file_path.upper().endswith(AUDIO_SUFFIXES)

def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    listOfFile.sort()
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)        
    return allFiles

class setInterval:
    def __init__(self, interval, action, bot_loop):
        self.interval = interval
        self.action = action
        self.task = bot_loop.create_task(self.__set_interval())

    async def __set_interval(self):
        while True:
            await self.action()
            await sleep(self.interval)

    def cancel(self):
        self.task.cancel()

async def sync_to_async(bot_loop, func, *args, wait=True, **kwargs):
    pfunc = partial(func, *args, **kwargs)
    future = bot_loop.run_in_executor(THREADPOOL, pfunc)
    return await future if wait else future


def async_to_sync(bot_loop, func, *args, wait=True, **kwargs):
    future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
    return future.result() if wait else future

async def run_comman_d(command_list):
    process = await asyncio.create_subprocess_shell(
        command_list,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    return e_response, t_response

async def downloadaudiocli(command_to_exec):
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    print("Download error:", e_response)
    return e_response, t_response


async def take_ss(video_file):
    des_dir = 'Thumbs'
    if not os.path.exists(des_dir):
        os.mkdir(des_dir)
    des_dir = os.path.join(des_dir, f"{time.time()}.jpg")
    duration = await get_video_duration(video_file)
    if duration == 0:
        duration = 3
    duration = duration // 2
    status = await downloadaudiocli(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(duration),
                   "-i", video_file, "-frames:v", "1", des_dir])
    if not os.path.lexists(des_dir):
        return None
    with Image.open(des_dir) as img:
        img.convert("RGB").save(des_dir, "JPEG")
    return des_dir

async def split_large_files(input_file):
    working_directory = os.path.dirname(os.path.abspath(input_file))
    new_working_directory = os.path.join(working_directory, str(time.time()))
    # create download directory, if not exist
    if not os.path.isdir(new_working_directory):
        os.makedirs(new_working_directory)
    if check_is_streamable(input_file):
        # handle video / audio files here
        total_duration = await get_video_duration(input_file)
        # proprietary logic to get the seconds to trim (at)
        LOGGER.info(total_duration)
        total_file_size = os.path.getsize(input_file)
        LOGGER.info(total_file_size)
        minimum_duration = (total_duration / total_file_size) * (Config.TG_SPLIT_SIZE)
        # casting to int cuz float Time Stamp can cause errors
        minimum_duration = int(minimum_duration)

        LOGGER.info(minimum_duration)
        # END: proprietary
        start_time = 0
        end_time = minimum_duration
        base_name = os.path.basename(input_file)
        input_extension = base_name.split(".")[-1]
        LOGGER.info(input_extension)

        i = 0
        flag = False

        while end_time <= total_duration:
            LOGGER.info(i)
            # file name generate
            parted_file_name = "{}_PART_{}.{}".format(
                str(base_name), str(i).zfill(5), str(input_extension)
            )

            output_file = os.path.join(new_working_directory, parted_file_name)
            LOGGER.info(output_file)
            LOGGER.info(
                await cult_small_video(
                    input_file, output_file, str(start_time), str(end_time)
                )
            )
            LOGGER.info(f"Start time {start_time}, End time {end_time}, Itr {i}")

            # adding offset of 3 seconds to ensure smooth playback
            start_time = end_time - 3
            end_time = end_time + minimum_duration
            i = i + 1

            if (end_time > total_duration) and not flag:
                end_time = total_duration
                flag = True
            elif flag:
                break
    else:
        o_d_t = os.path.join(
            new_working_directory,
            os.path.basename(input_file),
        )
        LOGGER.info(o_d_t)
        file_genertor_command = [
            "rar",
            "a",
            f"-v{Config.TG_SPLIT_SIZE}b",
            "-m0",
            o_d_t,
            input_file,
        ]
        await run_comman_d(file_genertor_command)
    try:
        os.remove(input_file)
    except Exception as r:
        LOGGER.error(r)
    return new_working_directory


async def cult_small_video(video_file, out_put_file_name, start_time, end_time):
    file_genertor_command = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        video_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-async",
        "1",
        "-strict",
        "-2",
        "-c",
        "copy",
        out_put_file_name,
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    LOGGER.info(t_response)
    return out_put_file_name


async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message,
    start,
    file_name
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        time_to_completion = round((total - current) / speed)
        estimated_total_time = elapsed_time + time_to_completion
        comp = "✦"
        ncomp = "✧"
        elapsed_time = TimeFormatter(elapsed_time)
        estimated_total_time = TimeFormatter(estimated_total_time)
        pr = ""
        try:
            percentage=int(percentage)
        except:
            percentage = 0

        for i in range(1,11):
            if i <= int(percentage/10):
                pr += comp
            else:
                pr += ncomp
        progress = "{}: {}%\n[{}]\n".format(
            ud_type,
            round(percentage, 2),
            pr)

        tmp = progress + "**{0} of {1}**\n**⚡️ Speed:** {2}/sec\n**⏱ ETA:** {3}\n**📂 Filename:** `{4}`".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s",
            file_name
        )
        try:
            await message.edit(text=tmp)
        except Exception as e:
            pass

class JVPrimeDl:
    def __init__(self, cmd):
        self.cmd = cmd
        self.log = logging.getLogger("JVPrimeDl")
    
    async def download(self, message: Message):
        process = await asyncio.create_subprocess_shell(
            self.cmd,
            # stdout must a pipe to be accessible as process.stdout
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit = 1024 * 128 * 200)
        blank = 0
        count = 0
        flag = 0
        filename = ""
        ed = 0
        while True:
            try:
                data  = await process.stdout.readline()
                data = data.decode().strip().split("\r")[0].split("\n")[0]
            except:
                data = ""
            if data == "":
                blank += 1
            if blank == 30:
                break
            chk_dl = re.findall(r"Downloding: (.*)", data)
            if chk_dl:
                filename = chk_dl[0]
                continue
            if "WVripper took" in data:
                break
            if "Start Muxing" in data:
                flag = 1
                await message.edit("`Muxing Started ...`")
            if flag == 1:
                if data == "":
                    continue
                else:
                    await message.edit(data)
            if ed == 0:
                await message.edit("`Downloading Started ...`")
                ed = 1
            comp_ptrn = r".*((?:\d+\.)?\d+(?:B|KiB|MiB|GiB)).*/.*((?:\d+\.)?\d+(?:K|M|G)iB)?((?:\d+\.)?\d+\%)"
            comp_srch = re.search(comp_ptrn, data)
            if comp_srch is not None and int(comp_srch.groups()[-1].replace("%", "")) == 100:
                await message.edit(f"`{filename} Downloaded ....`")
            try:
                self.log.info(data)
                p_p = r"((?:\d+\.)?\d+\%)"
                t_p = r"((?:\d+\.)?\d+(?:K|M|G)iB)"
                try:
                    prog = re.search(p_p, data).group(1)
                    size = re.search(t_p, data).group(1)
                except:
                    continue
                try:
                    prg = prog.strip("% ")
                    prg = prg.replace("%", "")
                    pr_bar = ""
                    try:
                        percentage=int(prg.split(".")[0])
                    except Exception as e:
                        percentage = 0
                    for i in range(1,11):
                        if i <= int(percentage/10):
                            pr_bar += "●"
                    editstr = f"`🔸 Downloading {filename} ...`\n\n`[{pr_bar}] {prog}%`\n\n`🔹 Total {size}`"
                    count += 1
                    if count >= 5:
                        count = 0
                        await asyncio.sleep(3)
                        await message.edit(editstr)
                except Exception as e:
                    self.log.exception(e)
                    blank += 1
            except Exception as e:
                blank += 1
                self.log.exception(e)
                continue
        await process.wait()
        self.log.info((await process.stderr.read()))
        await message.delete()

def getListOfFiles(dirName, video_only=False):
    listOfFile = os.listdir(dirName)
    listOfFile.sort()
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            if video_only:
                if not fullPath.upper().endswith(VIDEO_SUFFIXES):
                    continue
            allFiles.append(fullPath)        
    return allFiles

async def get_video_duration(input_file):
    metadata = extractMetadata(createParser(input_file))
    total_duration = 0
    if metadata.has("duration"):
        total_duration = metadata.get("duration").seconds
    return total_duration

def get_path_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total_size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            abs_path = os.path.join(root, f)
            total_size += os.path.getsize(abs_path)
    return total_size

async def run_comman_d(command_list):
    process = await asyncio.create_subprocess_shell(
        command_list,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    return e_response, t_response

async def downloadaudiocli(command_to_exec):
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    logging.error("Download error:"+e_response)
    return e_response, t_response

def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T', 5: 'P', 6: 'E', 7: 'Z', 8: 'Y'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(int(days)) + "day, ") if days else "") + \
        ((str(int(hours)) + "hour, ") if hours else "") + \
        ((str(int(minutes)) + "min, ") if minutes else "") + \
        ((str(int(seconds)) + "sec, ") if seconds else "")
    return tmp[:-2]

