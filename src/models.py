from typing import List, Optional
from pydantic import BaseModel, Field

class ExtractedItem(BaseModel):
    studio: str = Field(description="Name of the studio, e.g., Innenstadt, Eimsbüttel, Wandsbek")
    item_name: str = Field(description="Normalized standard German product name, e.g., 'Nitrilhandschuhe M', 'Tape', 'Kochsalzlösung'")
    quantity: Optional[int] = Field(default=None, description="Numeric quantity if explicitly stated, otherwise null")
    unit: Optional[str] = Field(default=None, description="Normalized singular unit if stated (e.g., 'Packung', 'Rolle', 'Flasche'), otherwise null")
    is_complete: bool = Field(description="True only if both quantity and unit are clearly specified in the text")
    clarification_question: Optional[str] = Field(
        default=None, 
        description="If is_complete is False, a polite German follow-up question asking the studio for the missing quantity and unit."
    )

class OrderExtractionResult(BaseModel):
    items: List[ExtractedItem]

class AggregatedOrderLine(BaseModel):
    item_name: str
    unit: str
    total_quantity: int = Field(ge=0)
    studios: List[str]

class ProcessedOrderReport(BaseModel):
    valid_aggregated_orders: List[AggregatedOrderLine]
    pending_clarifications: List[ExtractedItem]