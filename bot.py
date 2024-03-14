from pyrogram.types import Message
from pyrogram import filters, Client 
from io import BytesIO

from aiohttp import ClientSession
import sys
import traceback
from functools import wraps

from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

OWNER_ID = 1168796445

Client = Client(
    "B3KKK",
    api_id="2736855",
    api_hash="c2a44e1526cf253003db804e093d56fc",
    bot_token="7060238357:AAHj1dXF0yNyC9Isi_gFDVn-hVP9_zbJoEA"
) 

def split_limits(text):
    if len(text) < 2048:
        return [text]

    lines = text.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < 2048:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line

    result.append(small_msg)

    return result

def capture_err(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except ChatWriteForbidden:
            return
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            error_feedback = split_limits(
                "ERROR | {} | {}\n\n
{}
\n\n
{}
\n".format(
                    0 if not message.from_user else message.from_user.id,
                    0 if not message.chat else message.chat.id,
                    message.text or message.caption,
                    "".join(errors),
                ),
            )
            for x in error_feedback:
                await Client.send_message(OWNER_ID, x)
            raise err

    return capture


async def make_carbon(code):
    url = "https://carbonara.solopov.dev/api/cook"
    async with ClientSession().post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image




@Client.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(c:Client, message):
    if message.reply_to_message:
        if message.reply_to_message.text:
            txt = message.reply_to_message.text
        else:
            return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ.")
    else:
        try:
            txt = message.text.split(None, 1)[1]
        except IndexError:
            return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ.")
    m = await message.reply_text("ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴀʀʙᴏɴ...")
    carbon = await make_carbon(txt)
    await m.edit_text("ᴜᴩʟᴏᴀᴅɪɴɢ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴄᴀʀʙᴏɴ...")
    await c.send_photo(
        message.chat.id,
        photo=carbon,
        caption=f"» ʀᴇᴏ‌ᴜᴇsᴛᴇᴅ ʙʏ : {message.from_user.mention}",
    )
    await m.delete()
    carbon.close()
