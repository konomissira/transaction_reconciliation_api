from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    metadata: Optional[Dict[str, Any]] = None


class AssistantChatResponse(BaseModel):
    action: str
    result: Dict[str, Any]
    explanation: str