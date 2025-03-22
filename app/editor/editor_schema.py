from typing import Optional
from pydantic import BaseModel

class DebuggerRequest(BaseModel):
    code: str
    language: str

class CodeGeneratorRequest(BaseModel):
    prompt: str
    language: str
