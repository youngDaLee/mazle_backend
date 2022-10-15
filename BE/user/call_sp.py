from util.db_conn import db_conn


@db_conn
def call_one_query(sql_query, sp_args={}, cursor=None):
    """
    쿼리 실행 함수
    """
    cursor.execute(sql_query, sp_args)
    data = cursor.fetchone()
    return data


@db_conn
def call_query(sql_query, sp_args={}, cursor=None):
    """
    쿼리 실행 함수
    """
    cursor.execute(sql_query, sp_args)
    data = cursor.fetchall()
    return data
