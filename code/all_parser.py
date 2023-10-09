import asyncio
import nezavisne_parser
import rtvbn_parser
import rtrs_parser
import os
from concurrent.futures import ProcessPoolExecutor


if not os.path.exists('Parser_rs_media/data'):
    os.makedirs('Parser_rs_media/data')

async def main_async():
    loop = asyncio.get_event_loop()

    with ProcessPoolExecutor(max_workers=10) as executor:  

        await loop.run_in_executor(executor, nezavisne_parser.main)


        await loop.run_in_executor(executor, rtvbn_parser.main)


        await loop.run_in_executor(executor, rtrs_parser.main)

if __name__ == "__main__":
    asyncio.run(main_async())
