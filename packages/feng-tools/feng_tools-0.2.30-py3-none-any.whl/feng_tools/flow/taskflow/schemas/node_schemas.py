from typing import Optional

from pydantic import BaseModel


class LogResult(BaseModel):
    log_list:Optional[list[str]] = None

    pass
