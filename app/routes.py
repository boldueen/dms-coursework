import psycopg2
from psycopg2.extras import DictCursor

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_connection
from app.service import create_access_token
from app.service import authenticate_user, get_current_user, register_user
from app.service import fill_balance, get_users_order, pay_order_by_id
from app.service import get_items_by_name
from app.service import read_buy_offers, add_item_to_order_by_id

from app.shemas import ItemToSearh, CreateUser


from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES

from datetime import timedelta


api_router = APIRouter()


@api_router.post('/token', tags=['auth'])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username, 
            "role": user.role}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.post('/user', tags=['auth'])
def create_user(new_user_data: CreateUser = Depends()):
    return register_user(new_user_data)


@api_router.get('/user/me', tags=['user'])
def read_me(current_user = Depends(get_current_user)):
    return current_user


@api_router.put('/user/balance', tags=['user'])
def fill_my_balance(usd_to_fill: float, current_user = Depends(get_current_user)):
    return fill_balance(usd_to_fill, current_user)


@api_router.put('/order', tags=['user'])
def pay_for_order(order_id_to_pay:int, current_user = Depends(get_current_user)):
    return pay_order_by_id(order_id_to_pay, current_user)


@api_router.get('/orders', tags=['user'])
def get_all_my_orders(current_user = Depends(get_current_user)):
    return get_users_order(current_user)


@api_router.put('/order/item', tags=['user'])
def add_item_to_order(order_id: int, item_id: int, current_user = Depends(get_current_user)):
    return add_item_to_order_by_id(order_id, item_id, current_user)


@api_router.get('/items', tags=['items'])
def read_items(data: ItemToSearh = Depends()):
    return get_items_by_name(data)


@api_router.get('/offers', tags=['admin'])
def read_offers_to_buy(current_user = Depends(get_current_user)):
    return read_buy_offers(current_user)



