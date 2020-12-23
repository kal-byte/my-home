import asyncio
from io import BytesIO
import json
import os
import textwrap

from quart import Quart, render_template, send_file

from PIL import Image, ImageFont, ImageDraw

from discord.ext.ipc import Client

from dotenv import load_dotenv
load_dotenv()

def blocking_always_has_been(txt: str):
    with Image.open("./static/ahb.png") as img:
        wrapped = textwrap.wrap(txt, 20)

        set_back = sum(12 for char in txt) if \
            len(wrapped) == 1 else sum(6 for char in txt)
        up_amount = sum(35 for newline in wrapped)
        coords = (700 - set_back, 300 - up_amount)

        font = ImageFont.truetype("./static/JetBrainsMono-Regular.ttf", 48)
        draw = ImageDraw.Draw(img)

        draw.text(coords, "\n".join(wrapped), (255, 255, 255), font=font)

        buffer = BytesIO()
        img.save(buffer, "png")
    
    buffer.seek(0)
    return buffer

app = Quart(__name__)
web_ipc = Client(host="localhost", port=8765, secret_key=os.environ["SECRET_KEY"])
abh_cache = {}

@app.route("/")
async def index():
    stats = await web_ipc.request("get_stats")
    stats = json.loads(stats)

    template = await render_template(
        "index.html",
        guilds=stats[0],
        users=stats[1],
        commands=stats[2]
    )
    return template

@app.route("/ahb/<string:text>")
async def ahb(text):
    try:
        buffer = abh_cache[text]
        buffer.seek(0)

        return await send_file(buffer, "png")
    except KeyError:
        loop = asyncio.get_event_loop()
        buffer = await loop.run_in_executor(None, blocking_always_has_been, text)
        abh_cache[text] = buffer

        return await send_file(buffer, "png")


if os.name == "nt":
    app.run()
else:
    app.run(host="0.0.0.0", port="8080")