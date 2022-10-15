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


@db_conn
def call_sp_home_recipe_select(sp_args, cursor=None):
    """
    좋아요 상위 n개 레시피 출력
    """
    sp = 'CALL sp_home_recipe_select(%(limit)s, @o_out_code);'
    cursor.execute(sp, sp_args)
    data = cursor.fetchall()

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return None
    else:
        return data


@db_conn
def call_sp_home_drink_select(sp_args, cursor=None):
    """
    좋아요 상위 n개 음료 출력
    """
    sp = 'CALL sp_home_drink_select(%(limit)s, @o_out_code);'
    cursor.execute(sp, sp_args)
    data = cursor.fetchall()

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return None
    else:
        return data