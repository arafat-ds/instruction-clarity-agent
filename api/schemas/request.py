"""
schemas/request.py — Pydantic models for incoming API requests.
"""

from pydantic import BaseModel, field_validator


class InstructionRequest(BaseModel):
    instruction: str

    @field_validator("instruction")
    @classmethod
    def instruction_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("instruction must not be empty")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"instruction": "fix the login bug and notify the team by tomorrow"}
            ]
        }
    }
