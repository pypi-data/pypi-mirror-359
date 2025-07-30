# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["ImageGenerateResponse", "Data"]


class Data(BaseModel):
    url: Optional[str] = None


class ImageGenerateResponse(BaseModel):
    created: Optional[int] = None

    data: Optional[List[Data]] = None
