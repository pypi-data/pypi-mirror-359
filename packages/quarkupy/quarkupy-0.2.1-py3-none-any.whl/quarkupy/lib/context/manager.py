from __future__ import annotations

import pydantic

from typing import Optional, Any, Union

from httpcore import URL
from pydantic import PrivateAttr

import quarkupy as q
import pyarrow as pa


class ContextManager(pydantic.BaseModel):
    """
    Manage context within the Quark platform
    """

    # Pydantic model configuration
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    # API configuration
    base_url: Union[str, URL, None]

    _client: q.AsyncClient = PrivateAttr()

    def init_client(self) -> None:
        """
        Initialize the Quark client with the provided API key and base URL.

        :return: An instance of `q.AsyncClient`.
        """
        if not self._client:
            self._client = q.AsyncClient(
                base_url=self.base_url
            )

        return

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization method to set up the client after the model is created.

        :param __context: The context in which the model is being initialized.
        """
        #self.init_client()
        return

    async def get_files(self, source_id: Optional[pydantic.types.UUID] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> pa.Table:
        """
        Fetch files from the Quark platform based on the provided source ID, limit, and offset.

        :param source_id: The ID of the source to fetch files from, if applicable.
        :param limit: The maximum number of files to return.
        :param offset: The offset for pagination, to skip a number of files.

        :return: A PyArrow Table containing the files.
        :raises NotImplementedError: This method should be implemented in a subclass.
        """
        source_id_param = source_id.__str__() if source_id else None
        limit_param = limit if limit is not None else None
        offset_param = offset if offset is not None else None

        client = q.AsyncClient(
                base_url=self.base_url
            )

        raw = await client.context.list_files(source_id=source_id_param, limit=limit_param, offset=offset_param)
        buf = await raw.read()
        await client.close()

        return pa.ipc.open_stream(buf).read_all()
