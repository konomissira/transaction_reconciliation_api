from fastapi import APIRouter, HTTPException

from assistant.audit import log_assistant_action
from assistant.schemas import AssistantChatRequest, AssistantChatResponse
from assistant.agent import run_assistant
from assistant.examples import router as examples_router

router = APIRouter()

router.include_router(examples_router)


@router.post("/chat", response_model=AssistantChatResponse)
async def chat(req: AssistantChatRequest) -> AssistantChatResponse:
    try:
        out = await run_assistant(req.message, req.metadata)

        log_assistant_action(
            action=out["action"],
            arguments={"message_len": len(req.message)},
            success=True,
        )

        return AssistantChatResponse(
            action=out["action"],
            result=out["result"],
            explanation=out["explanation"],
        )

    except Exception as exc:
        log_assistant_action(
            action="chat",
            arguments={"message_len": len(req.message)},
            success=False,
            error=str(exc),
        )
        raise HTTPException(status_code=500, detail="Assistant failed to process the request") from exc