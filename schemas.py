"""
Database Schemas for Top-up & Social Services App

Each Pydantic model maps to a MongoDB collection with the lowercase class name
(e.g., TopupProduct -> "topupproduct").
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field

class TopupProduct(BaseModel):
    """
    Top-up products for game diamonds/credits
    Collection: topupproduct
    """
    name: str = Field(..., description="Display name, e.g., 'Mobile Legends 86 Diamonds'")
    game: str = Field(..., description="Game name, e.g., 'Mobile Legends', 'Free Fire'")
    amount: int = Field(..., ge=1, description="Amount of diamonds/credits")
    price: float = Field(..., ge=0, description="Price in local currency")
    is_active: bool = Field(True)

class SosmedService(BaseModel):
    """
    Social media boost services
    Collection: sosmedservice
    """
    name: str = Field(..., description="e.g., Instagram Followers +100")
    platform: str = Field(..., description="instagram, tiktok, youtube, etc")
    unit: Literal["followers", "likes", "views", "comments"] = Field("followers")
    quantity: int = Field(..., ge=1, description="Units included in one package")
    price: float = Field(..., ge=0)
    is_active: bool = Field(True)

class EmptyNumber(BaseModel):
    """
    Virtual/empty numbers inventory for registration/OTP
    Collection: emptynumber
    """
    provider: str = Field(..., description="Telco or virtual provider")
    country: str = Field(..., description="Country code name, e.g., 'ID', 'US'")
    number: str = Field(..., description="Masked or full number to sell")
    price: float = Field(..., ge=0)
    available: bool = Field(True)

class Order(BaseModel):
    """
    Orders placed by users
    Collection: order
    """
    category: Literal["topup", "sosmed", "number"]
    product_id: str = Field(..., description="Mongo ObjectId string of the product")
    quantity: int = Field(1, ge=1)
    target: str = Field(..., description="Game UID / Profile link / Phone number destination")
    contact_email: Optional[str] = Field(None, description="Customer contact for notifications")
    note: Optional[str] = None
    status: Literal["pending", "processing", "completed", "failed"] = "pending"
    total_price: Optional[float] = None
