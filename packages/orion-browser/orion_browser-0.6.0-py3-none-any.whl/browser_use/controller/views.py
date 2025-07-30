from typing import List, Optional
from pydantic import BaseModel, model_validator

# Action Input Models
class SearchBaiduAction(BaseModel):
    query: str

class DoDatePickerAction(BaseModel):
    index: int
    date: Optional[str] = None
    date_range: Optional[List[str]] = None

class GoToUrlAction(BaseModel):
    url: str

class ClickElementAction(BaseModel):
    index: int
    xpath: Optional[str] = None

class ClickByPositionAction(BaseModel):
    x: int
    y: int

class GetElementsAction(BaseModel):
    index: int | None = None


class InputTextAction(BaseModel):
    index: int
    text: str
    xpath: Optional[str] = None

class ExtractPageContentAction(BaseModel):
    # This class doesn't have fields in the bytecode
    # It appears to be a model with no required fields
    pass

class DoneAction(BaseModel):
    text: str

class SwitchTabAction(BaseModel):
    page_id: int

class OpenTabAction(BaseModel):
    url: str
    
class GetAllTabsAction(BaseModel):
    pass

class ScrollAction(BaseModel):
    amount: Optional[int] = None
    index: Optional[int] = None

class SendKeysAction(BaseModel):
    keys: str

class NoParamsAction(BaseModel):
    """
    Accepts absolutely anything in the incoming data
    and discards it, so the final parsed model is empty.
    """
    @model_validator(mode='before')
    def ignore_all_inputs(cls, values):
        # No matter what the user sends, discard it and return empty.
        return {}
    
    class Config:
        extra = 'allow'