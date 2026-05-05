"""
routes/process.py — POST /api/v1/process
"""

import logging
import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from agent.agent import run
from api.schemas.request import InstructionRequest
from api.schemas.response import AgentResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Agent"])


@router.post(
    "/process",
    response_model=AgentResponse,
    summary="Process an instruction",
    description=(
        "Accepts a natural language instruction and returns extracted actions, "
        "deadline, priority, and clarification questions if needed."
    ),
)
def process_instruction(body: InstructionRequest) -> AgentResponse:
    """
    Run the instruction through the hybrid rule-based + LLM pipeline.
    """
    logger.info("Processing instruction: %r", body.instruction)
    start = time.perf_counter()

    result = run(body.instruction)

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "Processed in %sms | status=%s | actions=%d",
        elapsed_ms,
        result.get("status"),
        len(result.get("actions", [])),
    )

    return AgentResponse(**result)
