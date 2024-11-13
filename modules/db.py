from psycopg2.extras import RealDictCursor 
import json
from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Optional, Dict

from .types import UserInDB
from .auth_helpers import get_password_hash, generate_reset_token, send_email_with_token
from config import get_db_conn, db_pool_external_user, db_pool_scope_check, db_pool_user_creator, reporting_db_pool


##### Chat functions ##### 

def push_chat_history(userid: int, new_chat_history: list) -> None:
    # update the chat history with current chat marker selected
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("update user_chat_history set chathistory = %s where userid = %s and chatdate between (now() - interval '5 hours') and now()", (json.dumps(new_chat_history), userid,))

def get_chat_history(userid: int) -> List[Dict[str,str]]:
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor(cursor_factory = RealDictCursor) as cursor:
            cursor.execute("select chatdate ,chathistory from user_chat_history where userid = %s and chatdate between (now() - interval '5 hours') and now()", (userid, ))
            res = cursor.fetchone()
            if not res:
                sys_message = [{"role":"system", "content":"you are a chatbot that helps a user understand their data.  for now just strike good conversation."}]
                cursor.execute("insert into user_chat_history (userid, chathistory, chatdate, current_chat) values (%s, %s, %s, %s)", (userid, json.dumps(sys_message), datetime.now(), True))
                db_conn.commit()
                return sys_message
            else:
                return res["chathistory"]

#### Code functions ####

def suspend_code(code: str, podcast: str, brand: str, suspenddate: str) -> None:
    brand_id = get_brand_id(brand)
    podcast_id = get_podcast_id(podcast)
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("update codes set activestatus = %s, suspenddate = %s where code = %s and podcastid = %s and brandid = %s", (False, suspenddate, code, podcast_id, brand_id,))
        db_conn.commit()

#### Performance functions #### 

def get_code_performance(startdate: str, enddate: str, brand: str) -> Tuple[List[str], List[tuple]]:
    brand_id = get_brand_id(brand)
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute('SELECT pc.podcastname as "podcast", sum(revenue) as "revenue", sum(orders) as "orders" from code_revenue as cr inner join brands b ON cr.brandid = b.id inner join codes c ON cr.code = c.code inner join podcasts pc ON c.podcastid = pc.id where cr.date between %s and %s and b.id = %s group by pc.podcastname',
                           (startdate, enddate, brand_id,))
            data = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
    return headers, data

def get_code_ytd_performance(brand: str, fields):
    brand_id = get_brand_id(brand)
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute('SELECT pc.podcastname as "podcast", sum(revenue) as "revenue", sum(orders) as "orders" from code_revenue as cr inner join brands b ON cr.brandid = b.id inner join codes c ON cr.code = c.code inner join podcasts pc ON c.podcastid = pc.id where cr.date between %s and %s and b.id = %s group by pc.podcastname')

def get_survey_performance(startdate: str, enddate: str, brand: str) -> Tuple[List[str], List[tuple]]:
    brand_id = get_brand_id(brand)
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute('select podcastname as "podcast", sum(revenue) as "survey revenue", sum(writeins) as "writeins" from survey_revenue where date between %s and %s and brandid = %s group by podcastname',
                           (startdate, enddate, brand_id,))
            data = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
    return headers, data

def get_podscribe_performance(startdate: str, enddate: str, brand: str) -> Tuple[List[str], List[tuple]]:
    brand_id = get_brand_id(brand)
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute('select podcastname as "podcast", sum(revenue) as "podscribe revenue", sum(spend) as "podscribe spend" from podscribe_revenue where date between %s and %s and brandid = %s group by podcastname',
                           (startdate, enddate, brand_id,))
            data = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
    return headers, data

#### Get dim functions ####

def get_brands() -> list:
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT brand FROM brands")
            data = [row[0] for row in cursor.fetchall()]
    return data

def get_codes() -> list:
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT code FROM codes where activestatus = TRUE")
            data = [row[0] for row in cursor.fetchall()]
    return data

def get_podcasts() -> list:
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT podcastname FROM podcasts")
            data = [row[0] for row in cursor.fetchall()]
    return data        

def get_scope(user_id: str) -> str:
    with get_db_conn(db_pool_scope_check) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT scope FROM scopes WHERE user_id = %s", (user_id,))
            scope = cursor.fetchone()
    return scope["scope"]

def get_brand_id(brand: str) -> str:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor: 
            cursor.execute("SELECT id FROM brands WHERE lower(brand) = lower(%s)", (brand.lower(),))
            brand = cursor.fetchone()
            return brand['id']

def get_podcast_id(podcast: str) -> str:
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor: 
            cursor.execute("SELECT id FROM podcasts WHERE lower(podcastname) = lower(%s)", (podcast.lower(),))
            podcast = cursor.fetchone()
            return podcast['id']

def get_user(username: str) -> Optional[UserInDB]:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM api_users where username = %s', (username,))
            user = cursor.fetchone()
        if user:
            return UserInDB(**user)
        else:
            return None

def get_email(email: str) -> str:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT email FROM api_users WHERE lower(email) = lower(%s);", (email, ))
            account = cursor.fetchone()
    return account["email"]

#### insert function ####

def new_brand(brand: str) -> None:
    with get_db_conn(db_pool_user_creator) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("insert into brands (brand) values (%s)", (brand.lower(),))
            db_conn.commit()

def new_code(code: str, brand: str, podcast: str, activestatus: bool, startdate: str, endate: str) -> None:
    brand_id = get_brand_id(brand)
    podcast_id = get_podcast_id(podcast)
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("insert into codes (code, podcastid, activestatus, activestartdate, activeenddate, brandid) values (%s,%s,%s,%s,%s,%s)", (code, podcast_id, activestatus, startdate, endate, brand_id))
        db_conn.commit()

def new_podcast(podcastname: str) -> None:
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("insert into podcasts (podcastname) values (%s)", (podcastname,))
        db_conn.commit()

def new_podcast_batch(podcastnames: List[str]) -> None:
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.executemany("insert into podcasts (podcastname) values (%s)", podcastnames)
        db_conn.commit()

def new_code_batch(newcodes: List[tuple]) -> None:
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.executemany("insert into podcasts (podcastname) values (%s)", newcodes)
        db_conn.commit()

def add_user(username: str, password: str, brand: str, email: str) -> None:
    with get_db_conn(db_pool_user_creator) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO api_users (username, hashed_password, brand, email) VALUES (%s, %s, %s, %s)", (username, get_password_hash(password), brand.lower(), email,))
            cursor.execute("INSERT INTO brands (brand) VALUES (%s)", (brand.lower(),))
            db_conn.commit()

def insert_scope(user_id: str, scope: str) -> None:
    with get_db_conn(db_pool_user_creator) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO scopes (user_id, scope) VALUES (%s, %s)", (user_id, scope,))
            db_conn.commit()

        
def insert_data(brand_id: str, source: str, data: dict) -> None:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO data_lake (brand_id, json_data, source) VALUES (%s, %s, %s);", (brand_id, json.dumps(data), source))
            db_conn.commit()


#### Auth Functions ####

def reset_authentication_verification(email: str, token: str) -> Optional[Dict[str, str]]:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT email FROM api_users WHERE lower(email) = lower(%s) AND reset_token = %s;", (email, token,))
            check = cursor.fetchone()
    return check

def change_password_m(payload: dict) -> None:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("UPDATE api_users SET hashed_password = %s WHERE username = %s;", (get_password_hash(payload.new_password), payload.username))
            db_conn.commit()

def reset_password_m(email: str, token: str, new_password: str) -> None:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("UPDATE api_users SET hashed_password = %s WHERE reset_token = %s AND lower(email) = lower(%s);", (get_password_hash(new_password),token, email,))
            db_conn.commit()

def store_reset_token(email: str) -> None:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            reset_timer = datetime.now(timezone.utc) + timedelta(minutes=15)
            cursor.execute("UPDATE api_users SET reset_token = %s, reset_timer = %s WHERE lower(email) = lower(%s);", (generate_reset_token(),reset_timer, email,))
            db_conn.commit()

def remove_reset_token(email: str) -> None:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("UPDATE api_users SET reset_token = NULL, reset_timer = NULL WHERE lower(email) = lower(%s);", (email,))
            db_conn.commit()

def send_token(email: str) -> None:
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT reset_token FROM api_users WHERE lower(email) = lower(%s);", (email,))
            token = cursor.fetchone()
    send_email_with_token(email, token["reset_token"])