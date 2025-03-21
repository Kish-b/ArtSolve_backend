from pydantic import BaseModel

class ExpressionRequest(BaseModel):
    expr: str

class AnalysisResponse(BaseModel):
    result: str
