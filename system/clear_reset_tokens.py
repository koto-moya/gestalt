from modules.db import *

def clear_dead_tokens():
    # should filter UPDATE the reset_tokens if reset_timer is < or equal to NOW()
    # update reset_toekn method to insert a reset timer value in the DB
    with get_db_conn as db_conn:
        with db_conn.cursor() as cursor:
            cursor.exectue("UPDATE api_users SET reset_token = NULL, reset_timer = NULL WHERE reset_timer <= NOW() OR reset_timer = NULL;")
            db_conn.commit()
    print("reset tokens have been Nulled")

    
if __name__ == "__main__":
    clear_dead_tokens()