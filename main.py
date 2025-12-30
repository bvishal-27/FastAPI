from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import Product
from database import SessionLocal, engine
import database_models

database_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize DB with products if empty
products = [
    Product(id=1, name="Laptop", price=999.99, description="Gaming Laptop", quantity=10),
    Product(id=2, name="Smartphone", price=699.50, description="5G Android Phone", quantity=25),
    Product(id=3, name="Headphones", price=149.99, description="Noise Cancelling Headphones", quantity=40),
    Product(id=4, name="Keyboard", price=79.99, description="Mechanical Keyboard", quantity=30),
    Product(id=5, name="Mouse", price=39.99, description="Wireless Optical Mouse", quantity=50),
]

def init_db():
    db = SessionLocal()
    count = db.query(database_models.Product).count()
    if count == 0:
        for product in products:
            db_product = database_models.Product(**product.model_dump())
            db.add(db_product)
        db.commit()
    db.close()

init_db()

@app.get("/products/", response_model=list[Product])
def get_all_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).all()
    return [Product.from_orm(prod) for prod in db_products]

@app.get("/products/{id}", response_model=Product)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        return Product.from_orm(db_product)
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/products/", response_model=Product)
def add_product(product: Product, db: Session = Depends(get_db)):
    db_product = database_models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return Product.from_orm(db_product)

@app.put("/products/{id}", response_model=Product)
def update_products(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        for key, value in product.model_dump().items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
        return Product.from_orm(db_product)
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")