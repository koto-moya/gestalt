from modules.db import *
from psycopg2.extras import RealDictCursor 

def clear_dead_tokens():
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT COUNT(DISTINCT id) as "count" FROM api_users WHERE reset_token IS NOT NULL')
            counts = cursor.fetchone()
            cursor.execute("UPDATE api_users SET reset_token = NULL, reset_timer = NULL WHERE reset_timer <= NOW() OR reset_timer IS NULL;")
            db_conn.commit()
    print(f"{counts["count"]} reset tokens have been Nulled")

    
if __name__ == "__main__":
    clear_dead_tokens()