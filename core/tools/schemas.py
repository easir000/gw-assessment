"""
Pydantic schemas for tool input validation.
Bonus: Demonstrates contract stability and type safety.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class HotPicksInput(BaseModel):
    budget: float = Field(..., gt=0, description="Maximum budget (must be positive)")
    limit: int = Field(default=5, ge=1, le=20, description="Max items to return (1-20)")
    state: Optional[str] = Field(default=None, description="Customer state for compliance")

class ComplianceInput(BaseModel):
    product_ids: List[str] = Field(..., min_length=1, description="List of SKU/Product IDs")
    customer_state: str = Field(default="TX", description="State to check compliance against")

class StockInput(BaseModel):
    product_id: str = Field(..., min_length=1, description="Product ID to check")

class VendorValidateInput(BaseModel):
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    net_wt_oz: Optional[float] = Field(default=None, description="Net weight in ounces")
    net_vol_ml: Optional[float] = Field(default=None, description="Net volume in ml")
    nicotine_mg: Optional[float] = Field(default=0, description="Nicotine content in mg")
    lab_report_attached: bool = Field(default=False, description="Lab report attached")

class KBSearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of results (1-10)")