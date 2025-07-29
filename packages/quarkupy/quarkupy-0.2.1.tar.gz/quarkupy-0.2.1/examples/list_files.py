"""Manual chaining (i.e. outside of lattices) of Quarks for RAG ingest"""

import os
from urllib.parse import urlparse

import dotenv
import pandas as pd
from halo import Halo

import quarkupy.lib as q
import quarkupy.lib.context as qc

# Configs
dotenv.load_dotenv()

API_KEY = os.environ.get("QUARK_API_KEY")
API_END_POINT = "https://demo.quarklabs.ai/api/quark"

if API_KEY is None or API_KEY == "":
    raise ValueError("QUARK_API_KEY environment variable not set")

PRINT_DATASETS = False
PRINT_QUARK_METRICS = True
PRINT_QUARK_HISTORY = False
SPINNER = "dots"

host_url = urlparse(API_END_POINT)
url_root = f"{host_url.scheme}://{host_url.netloc}"


async def main():
    print(q.__banner__)
    with Halo(text="💠 Getting file list...\n", spinner=SPINNER):
        manager = qc.ContextManager(
            base_url=host_url.geturl()
        )

        try:
            files = await manager.get_files()
            df: pd.DataFrame = files.to_pandas()
            print(df.head())

        except KeyboardInterrupt:
            print("Interrupted")
        except Exception as e:
            print(f"An error occurred while fetching files: {e}")
            raise e


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
