import asyncio
import os
from quart import Quart, render_template

import asyncpg

from dotenv import load_dotenv
load_dotenv()

app = Quart(__name__)

async def clear_cache():
    while True:
        await asyncio.sleep(300)
        del app.web_stats_cache

@app.before_serving
async def startup():
    loop = asyncio.get_event_loop()
    loop.create_task(clear_cache())
    app.pool = await asyncpg.create_pool(os.environ["POSTGRES_URI"])

@app.route("/")
async def index():
    try:
        stats = app.web_stats_cache
    except (AttributeError, KeyError):
        stats = await app.pool.fetchrow("SELECT * FROM web_stats;")
        app.web_stats_cache = stats
    
    template = await render_template("index.html", **stats)
    return template

@app.after_serving
async def shutdown():
    await app.pool.close()

if os.name == "nt":
    app.run()
else:
    app.run(host="0.0.0.0", port="8080")