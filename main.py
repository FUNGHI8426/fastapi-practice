import json
# 1. 從 fastapi 模組匯入 FastAPI 類別
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from pathlib import Path
# 2. 建立一個名叫 app 的 FastAPI 實體物件
app = FastAPI()

DATA_FILE = Path(__file__).parent/"inventory.json"

class ProductCreate(BaseModel):
    name:str
    price:int=Field(gt=0)
    stock:int=Field(default=1,ge=0)

def load_inventory():
    try:
        with open("inventory.json","r",encoding="utf-8")as f:
            return json.load(f)
    except FileNotFoundError:
        return[
            {"id":"P001", "name":"機械鍵盤", "price":2500, "stock": 5},
            {"id":"P002", "name":"無線滑鼠", "price":1200, "stock": 2},
            {"id":"P003", "name":"27吋螢幕", "price":6000, "stock": 1}
        ]

def save_inventory(data):
    with open("inventory.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
# 3. 用 @app.get("/") 裝飾器綁定根目錄路由，定義函式回傳包含歡迎訊息的字典
@app.get("/")
def read_root():
    return{"store":"python轉職商店","status":"營業中"}

@app.get("/products")
def get_products(max_price:int = 999999, min_stock:int = 0):
    items = load_inventory()
    return [
        item
        for item in items
        if item["price"] <= max_price and item["stock"]>= min_stock
    ]

@app.get("/products/low-stock")
def get_low_stock():
    items = load_inventory()
    low_items = [item for item in items if item.get("stock", 0) < 3]
    return{
        "count":len(low_items),
        "items":low_items,
    }

@app.get("/products/{product_name}")
def get_product_by_name(product_name:str):
    items = load_inventory()
    for item in items:
        if item["name"].lower() == product_name.lower():
            return item
    raise HTTPException(status_code=404,detail = "查無此商品")

@app.get("/products/{product_name}/quote")
def get_product_quote(product_name:str, qty:int = 1):
    items = load_inventory()

    target_item = None
    for item in items:
        if item["name"].lower() == product_name.lower():
            target_item = item
            break

    if target_item is None:
        raise HTTPException(status_code=404,detail="查無此商品")

    if qty <= 0:
        raise HTTPException(status_code=400,detail="購買數量必須大於0")

    if qty>target_item["stock"]:
        raise HTTPException(status_code=400,detail="庫存不足")

    total_price = target_item["price"]*qty

    return{
        "product":target_item["name"],
        "unit_price": target_item["price"],
        "qty":qty,
        "total_price":total_price
    }
    
@app.post("/products")
def create_product(new_product:ProductCreate):
    items = load_inventory()
    
    for p in items:
        if p ["name"].lower() == new_product.name.lower():
            raise HTTPException(status_code=400,detail="商品已存在，請勿重複新增")
        
    product_dict = new_product.model_dump()
    items.append(product_dict)
    save_inventory(items)
    
    return{"message":"商品新增成功","product":product_dict}