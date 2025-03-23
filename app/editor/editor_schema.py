from typing import Optional
from pydantic import BaseModel

class DebuggerRequest(BaseModel):
    code_session_id:str

class CodeGeneratorRequest(BaseModel):
    query: Optional[str] = ""
    code_session_id: str
