from pydantic import BaseModel
from pydantic import condecimal

from decimal import Decimal

from typing import Literal
from enum import Enum


class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None



class userInDb(BaseModel):
    user_id: int
    username: str
    full_name: str 
    email: str
    balance_usd: float 
    role: str 



class ItemsPerPage(str, Enum):
    ten = '10'
    twenty = '20'
    fifty = '50'
    hundred = '100'


class SortBy(str, Enum):
    price = 'price'  
    balance = 'balance'  
    name = 'name'  
    item_id = 'item_id'

class ItemToSearh(BaseModel):
    item_name: str
    sort_by: SortBy = SortBy.price
    items_per_page: ItemsPerPage = ItemsPerPage.ten

class Item(BaseModel):
    item_id: int
    name: str 
    description: str
    price: float
    balance: int


class Order(BaseModel):
    order_id: int 
    is_payed: bool
    total_usd: float
    is_given: bool
    office_id: int
    username: str


class BuyOffer(BaseModel):
    supplier_id: int
    item_id: int 
    item_name: str 
    offer_id: int 
    quantity: int


# class GetUser(BaseModel):
#     username: str | None = None
#     password: str | None = None
    

# class User(BaseModel):
#     user_id: int | None = None 
#     username: str | None = None
#     full_name: str | None = None
#     email: str | None = None
#     hashed_pass: str | None = None
#     balance: condecimal(multiple_of=Decimal('0.25')) | None = None
#     user_role: str | None = None


    

class CreateUser(BaseModel):
    username: str
    password: str
    email: str
    full_name: str 


