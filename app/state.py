from typing import TypedDict, Optional

class AgentState(TypedDict):
    user_id: int
    raw_input: str
    parsed_data: Optional[dict]
    validation_errors: list[str]
    is_confirmed: bool
