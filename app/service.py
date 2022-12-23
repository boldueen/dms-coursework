from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status

from datetime import datetime, timedelta

from jose import jwt, JWTError

from app.database import get_connection
from app.settings import SECRET_KEY, ALGORITHM
from app.shemas import TokenData, userInDb, CreateUser
from app.shemas import Order, Item, ItemToSearh, BuyOffer
import psycopg2

from pydantic import BaseModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


def verify_password(username: str, plain_password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
            SELECT * FROM is_password_correct('{username}', '{plain_password}')
        """
    )

    is_password_correct = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return is_password_correct


def authenticate_user(username: str, plain_password: str):
    if not verify_password(username, plain_password):
        return False

    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    cursor.execute(
        f"""
            SELECT * FROM users WHERE username = '{username}';
        """
    )
    response_user = dict()
    user = cursor.fetchall()

    
    resp : userInDb

    for r in user:
        resp = userInDb(
            user_id=r['user_id'],
            username = r['username'],
            full_name = r['full_name'],
            email = r['email'],
            balance_usd = r['balance_usd'],
            role = r['user_role']
        )

    if not resp:
        return False

    return resp


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    print(timedelta)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception


    conn = get_connection()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    cursor.execute(
        f"""
            SELECT * FROM users WHERE username = '{username}';
        """
    )
    user = cursor.fetchall()
    if user is None:
        raise credentials_exception

    resp : userInDb

    for r in user:
        resp = userInDb(
            user_id=r['user_id'],
            username = r['username'],
            full_name = r['full_name'],
            email = r['email'],
            balance_usd = r['balance_usd'],
            role = r['user_role']
        )
    
    return resp


def get_items_by_name(data: ItemToSearh) -> list[Item]:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    cursor.execute(
        f"""
            SELECT * FROM items 
            WHERE name LIKE '%{data.item_name}%'
            ORDER BY {data.sort_by.value} desc
            LIMIT {data.items_per_page.value}
            ;
        """
    )
    items = cursor.fetchall()
    if len(items) == 0:
        return {
            'message':'no such items in our shop((('
        }

    items_response = list()
    print('items_response', items_response)
    for r in items:
        it = Item(
            item_id = r['item_id'], 
            name = r['name'], 
            description = r['description'], 
            price = r['price'], 
            balance = r['balance']
        )

        items_response.append(it) 
        

    return items_response


def register_user(new_user: CreateUser):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    try:
        cursor.execute(
            f"""
            INSERT INTO 
                users (username, full_name, email, hashed_pass)
            VALUES
                ('{new_user.username}', '{new_user.full_name}', '{new_user.email}', '{new_user.password}');

            CREATE ROLE {new_user.username};
            GRANT SHOP_USER to {new_user.username};
            """
        )

        conn.commit()

        return {
            'message':'user was successfuly created',
            'status': True
        }

    except Exception as e:

        msg_error = 'error. user was not created'

        return {
            'message':'error. user was not created. try another username',
            'status': False
        }


def fill_balance(usd_to_fill: float, user: userInDb):

    conn = get_connection()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)


    if usd_to_fill <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    new_total_usd = user.balance_usd + usd_to_fill


    try:
        cursor.execute(
            f"""
                UPDATE users SET balance_usd = {new_total_usd}
                WHERE username = '{user.username}'
            """
        )

        conn.commit()

        return {
            'message':f'balance filled for: {usd_to_fill}. TOTAL USD: {new_total_usd}',
            'status': True
        }

    except Exception as e:

        return {
            'message':f'{e.args}',
            'status': False
        }


def get_users_order(user: userInDb):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)



    try:

        cursor.execute(
            f"""
                SET ROLE {user.username};
                SELECT * FROM orders ORDER BY is_given DESC;

            """
        )

        conn.commit()        

        orders = cursor.fetchall()
        if orders is None:
            return {
                'message':'You have no orders yet((('
            }

        orders_response = list()
        for r in orders:
            it = Order(
                order_id = r['order_id'], 
                is_payed = r['is_payed'], 
                total_usd = r['total_usd'], 
                is_given = r['is_given'], 
                office_id = r['office_id'],
                username = r['username']
            )

            orders_response.append(it) 
        

        return orders_response

    except Exception as e:
        print(e)
        return e


def pay_order_by_id(order_id_to_pay: int, current_user: userInDb):
    
    if order_id_to_pay < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
    
    try:
        cursor.execute(
            f"""
                CALL pay_for_order('{current_user.username}', {order_id_to_pay});
        
            """
        )

        return {
            'message':'transaction done. Check order status payment'
        }

    except Exception as e:

        error_msg = list(e.args)[0]
        
        exc_msg = 'something went wrong...'

        if 'payed' in error_msg:
            exc_msg = 'your order already PAYED'
        
        if 'low' in error_msg:
            exc_msg = 'Oooops.... Low balance...'


        return {
            'message':f'{exc_msg}'
        }


def add_item_to_order_by_id(order_id: int, item_id: int, current_user: userInDb):
    
    if order_id <=0 or item_id <=0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='id\'s must be plural')
    

    conn = get_connection()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    cursor.execute(
        f"""
            SELECT * FROM orders where order_id={order_id} and username='{current_user.username}';
        """
    )
    user_order = cursor.fetchall()
    print(user_order)

    if len(user_order) == 0:
        raise HTTPException(status.HTTP_423_LOCKED, detail=f'order number:{order_id}. is not your order or it was deleted')


    # for order in user_order:
    #     print(order['is_payed'])
    #     if order['is_payed']:
    #         raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='order has already payed, you cannot change items in it')

    # cursor.execute(
    #     f"""
    #         SELECT * FROM items where item_id={item_id};
    #     """
    # )
    # items = cursor.fetchall()


    # if len(items) == 0:
    #     raise HTTPException(status.HTTP_423_LOCKED, detail=f'item number:{item_id}. NO SUCH item')


    try:
        cursor.execute(
            f"""
                CALL add_item_to_order({order_id},{item_id});
            """
        )
        conn.commit()

        return {
            'message':f'item num.{item_id} added to order num.{order_id}'
        }
    except Exception as e:
        return{
            f'message':'error. {e.args}'
        }


def read_buy_offers(current_user: userInDb):
    if current_user.role != 'SHOP_ADMIN':
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    try:

        cursor.execute(
            f"""
                SET ROLE {current_user.username};
                SELECT * FROM buy_offers;
            """
        )



        offers = cursor.fetchall()
        if offers is None:
            return {
                'message':'цу рф((('
            }

        offers_response = list()
        for r in offers:
            it = BuyOffer(
                supplier_id=r['supplier_id'],
                item_id=r['item_id'],
                item_name=r['item_name'],
                offer_id=r['offer_id'],
                quantity=r['quantity']
            )
            offers_response.append(it) 
        

        return offers_response

    except Exception as e:
        return e.args


