import jwt
import base64
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from mypg import call_sp
from util.resp import response


JWT_SECRET_KEY = getattr(settings, 'SIMPLE_JWT', None)['SIGNING_KEY']


class MyProfileView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
            if not customer_uuid:
                raise Exception
        except Exception:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        sp_args = {
            'customer_uuid': customer_uuid,
        }
        sql = '''SELECT email, nickname, birth, profile, platform FROM mazle_user'''
        is_suc, data = call_sp.call_one_query(sql, sp_args)
        if is_suc:
            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyReviewView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
            if not customer_uuid:
                raise Exception
        except Exception:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        sp_args = {
            'customer_uuid': customer_uuid,
        }
        sql = '''SELECT email, nickname, birth, profile, platform FROM mazle_user'''
        is_suc, data = call_sp.call_one_query(sql, sp_args)
        if is_suc:
            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyRecipeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
            if not customer_uuid:
                raise Exception
        except Exception:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        offset = request.GET.get('offset', 0)
        limit = request.GET.get('limit', 10)

        sp_args = {
            'customer_uuid': customer_uuid,
            'offset': offset,
            'limit': limit,
        }
        sql = '''
        SELECT R.`recipe_id`
             , R.`recipe_name`
             , R.`img`
             , IFNULL((SELECT GROUP_CONCAT(tag) FROM recipe_tag WHERE recipe_id=R.`recipe_id`),'') as `tag`
             , (SELECT COUNT(*) FROM recipe_like WHERE recipe_id = R.`recipe_id`) as `like_cnt`
        FROM recipe AS R
        WHERE customer_uuid = %(customer_uuid)s
        LIMIT %(offset)s, %(limit)s;'''
        is_suc, data = call_sp.call_query(sql, sp_args)
        if is_suc:
            for row in data:
                if row['img']:
                    row['img'] = base64.decodebytes(row['img']).decode('latin_1')

                if row['tag']:
                    row['tag'] = row['tag'].split(',')
                else:
                    row['tag'] = []
            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
