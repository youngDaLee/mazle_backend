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
def call_query(sql_query, cursor=None):
    """ 
    쿼리 실행 함수
    """
    cursor.execute(sql_query)
    data = cursor.fetchall()

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == 0:
        return data
    else:
        return []


@db_conn
def call_sp_recipe_list_select(sp_args, cursor=None):
    """ 
    음료조회 임시. ES 구축 후 삭제 예정
    """
    sp = "CALL sp_recipe_list_select(%(offset)s, %(limit)s, %(search_keyword)s, %(order)s, @o);"
    cursor.execute(sp, sp_args)
    data = cursor.fetchall()

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return []
    else:
        return data



@db_conn
def call_sp_meterial_select(sp_args, cursor=None):
    """
    부재료조회 임시. ES 구축 후 삭제 예정
    """
    sp = "CALL sp_meterial_select(%(meterial_name)s, @o);"
    cursor.execute(sp, sp_args)
    data = cursor.fetchall()

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return []
    else:
        return data



@db_conn
def call_sp_recipe_select(sp_args, cursor=None):
    """CALL recipe detail select SP Fucntion
    Args:
        sp_args (dict): sp argumentes following keys::
            dict: {
                'customer_uuid': `(Optional)` for check is adult,
                'recipe_id': `(int)` recipe_id
            }
    Returns:
        res (dict): Recipe Detail Data. following keys::
            dict: {
                '':
            }
    """
    sp = "CALL sp_recipe_select(%(recipe_id)s, %(customer_uuid)s, @o);"
    cursor.execute(sp, sp_args)
    data = cursor.fetchone()
    if not data:
        return {}

    cursor.nextset()
    drink_data = cursor.fetchall()

    cursor.nextset()
    meterial_data = cursor.fetchall()

    data['main_meterial_list'] = drink_data
    data['sub_meterial_list'] = meterial_data

    return data


@db_conn
def call_sp_recipe_set(sp_args, cursor=None):
    """CALL recipe Insert SP Fucntion
    Args:
        sp_args (dict): sp argumentes following keys::
            dict: {
                'customer_uuid': `str`,
                'recipe_name': `str`,
                'summary': `str`,
                'description': `str`,
                'img': `blob`,
                'price': `int`,
                'mesaure_standard': `str`,
                'tip': `str',
                'diff_score': `float`,
                'price_score': `float`,
                'sweet_score': `float`,
                'alcohol_score': `float`,
                'tag_list': list(str),
                'main_meterial': `list(int)`,
                'sub_meterial': `list(int)`,
            }
    Returns:
        res (bool): `True` if out_code==0 else `False`
    """
    # 1. insert into recipe
    sp = """CALL sp_recipe_set(%(customer_uuid)s, %(recipe_name)s,
            %(summary)s,%(description)s,%(img)s,%(price)s,
            %(mesaure_standard)s,%(tip)s,%(diff_score)s,%(price_score)s,
            %(sweet_score)s,%(alcohol_score)s, @recipe_id, @o);"""
    cursor.execute(sp, sp_args)

    cursor.execute('SELECT @recipe_id')
    recipe_id = cursor.fetchone()
    recipe_id = recipe_id['@recipe_id']

    t_sp = "CALL sp_recipe_tag_set(%(recipe_id)s, %(tag)s, @o);"
    for tag in sp_args['tag_list']:
        tag_sp_args = {
            'recipe_id': recipe_id,
            'tag': tag,
        }
        cursor.execute(t_sp, tag_sp_args)

    m_sp = "CALL sp_recipe_main_meterial_set(%(recipe_id)s, %(drink_id)s, @o);"
    for drink_id in sp_args['main_meterial']:
        drink_sp_args = {
            'recipe_id': recipe_id,
            'drink_id': drink_id,
        }
        cursor.execute(m_sp, drink_sp_args)

    s_sp = "CALL sp_recipe_sub_meterial_set(%(recipe_id)s,\
            %(meterial_id)s, @o);"
    for meterial_id in sp_args['sub_meterial']:
        sub_sp_args = {
            'recipe_id': recipe_id,
            'meterial_id': meterial_id,
        }
        cursor.execute(s_sp, sub_sp_args)

    return True


@db_conn
def call_sp_recipe_delete(sp_args, cursor=None):
    """CALL recipe DELETE SP Fucntion
    Args:
        sp_args (dict): sp argumentes following keys::
            dict: {
                'customer_uuid': `str`,
                'recipe_id': `str`,
            }
    Returns:
        res (bool): `True` if out_code==0 else `False`
    """
    # 1. insert into recipe
    sp = "CALL sp_recipe_delete(%(customer_uuid)s, %(recipe_name)s, @o);"
    cursor.execute(sp, sp_args)

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return False
    else:
        return True


@db_conn
def call_sp_recipe_comment_select(sp_args, cursor=None):
    """CALL recipe comment select SP Fucntion
    Args:
        sp_args (dict): sp argumentes following keys::
            dict: {
                'recipe_id': `(int)` recipe_id,
                'offset': `(int)`,
                'limit': `(int)`,
            }
    Returns:
        res (dict): Recipe comment Data. following keys::
            dict: {
                '':
            }
    """
    sp = "CALL sp_recipe_comment_select(%(recipe_id)s, %(offset)s, %(limit)s, @o);"
    cursor.execute(sp, sp_args)
    data = cursor.fetchall()

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return {}
    else:
        return data


@db_conn
def call_sp_recipe_comment_set(sp_args, cursor=None):
    """CALL recipe comment Insert SP Fucntion
    Args:
        sp_args (dict): sp argumentes following keys::
            dict: {
                'recipe_id': `(int)` recipe_id,
                'customer_uuid': `(str)`,
                'comment': `(str)`,
                'score': `(float)`,
            }
    Returns:
        res (bool): `True` if out_code==0 else `False`
    """
    sp = "CALL sp_recipe_comment_set(%(recipe_id)s, %(customer_uuid)s,\
         %(comment)s, %(score)s, @o);"
    cursor.execute(sp, sp_args)

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return False
    else:
        return True


@db_conn
def call_sp_recipe_like_select(sp_args, cursor=None):
    """CALL recipe Like Insert SP Fucntion
    Args:
        sp_args (dict): sp argumentes following keys::
            dict: {
                'customer_uuid': `(str)`,
                'recipe_id': `(int)` recipe_id,
            }
    Returns:
        res (bool): `True` if out_code==0 else `False`
    """
    sp = "CALL sp_recipe_like_select(%(customer_uuid)s, %(recipe_id)s, @o);"
    cursor.execute(sp, sp_args)
    data = cursor.fetchone()

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return None
    else:
        return data


@db_conn
def call_sp_recipe_like_set(sp_args, cursor=None):
    """CALL recipe Like Insert SP Fucntion
    Args:
        sp_args (dict): sp argumentes following keys::
            dict: {
                'customer_uuid': `(str)`,
                'recipe_id': `(int)` recipe_id,
            }
    Returns:
        res (bool): `True` if out_code==0 else `False`
    """
    sp = "CALL sp_recipe_like_set(%(customer_uuid)s, %(recipe_id)s, @o);"
    cursor.execute(sp, sp_args)

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return False
    else:
        return True


@db_conn
def call_sp_recipe_like_delete(sp_args, cursor=None):
    """CALL recipe Like delete SP Fucntion
    Args:
        sp_args (dict): sp argumentes following keys::
            dict: {
                'customer_uuid': `(str)`,
                'recipe_id': `(int)` recipe_id,
            }
    Returns:
        res (bool): `True` if out_code==0 else `False`
    """
    sp = "CALL sp_recipe_like_delete(%(customer_uuid)s, %(recipe_id)s, @o);"
    cursor.execute(sp, sp_args)

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return False
    else:
        return True


@db_conn
def call_sp_meterial_set(sp_args, cursor=None):
    """CALL recipe Like delete SP Fucntion
    Args:
        sp_args (dict): sp argumentes following keys::
            dict: {
                'customer_uuid': `(str)`,
                'recipe_id': `(int)` recipe_id,
            }
    Returns:
        res (bool): `True` if out_code==0 else `False`
    """
    sp = "CALL sp_meterial_set(%(meterial_name)s, %(img)s, @o);"
    cursor.execute(sp, sp_args)
    print(cursor.fetchone())

    cursor.execute('SELECT @o')
    out_code = cursor.fetchone()
    out_code = out_code['@o']

    if out_code == -99:
        return False
    else:
        return True
