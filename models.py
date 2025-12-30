from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str
    quantity: int

    class Config:
        from_attributes = True

