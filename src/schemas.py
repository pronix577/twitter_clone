from typing import List, Union
from pydantic import BaseModel


class Item(BaseModel):
    tweet_data: str
    tweet_media_ids: Union[List[int], None] = None
