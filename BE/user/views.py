import jwt
import uuid
import base64
from argon2 import PasswordHasher
from datetime import datetime,timedelta
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from user import call_sp
from user.util import password_validcheck
from util.resp import response


JWT_SECRET_KEY = getattr(settings, 'SIMPLE_JWT')['SIGNING_KEY']


class SignUp(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            email = request.POST.get('email')
            nickname = request.POST.get('nickname', '')
            passwd = request.POST.get('passwd')
            if not passwd:
                raise Exception
        except Exception:
            return response(status=status.HTTP_400_BAD_REQUEST)

        # Check passwd validation
        is_val, message = password_validcheck(passwd)
        if not is_val:
            return response(status=status.HTTP_400_BAD_REQUEST, message=message)

        user_uuid = str(uuid.uuid4())
        hash_passwd = PasswordHasher().hash(passwd)

        sp_args = {
            'email': email,
            'user_uuid': user_uuid,
            'passwd': hash_passwd,
            'nickname': nickname,
        }
        sql_duplicate = 'SELECT customer_uuid FROM mazle_user WHERE email = %(email)s;'
        _, is_dup = call_sp.call_one_query(sql_duplicate, sp_args)
        if is_dup:
            return response(status=status.HTTP_409_CONFLICT, message='duplicate email')

        sql_signup = 'INSERT INTO mazle_user(customer_uuid, email, passwd, nickname) VALUES (%(user_uuid)s, %(email)s, %(passwd)s, %(nickname)s);'
        is_suc, _ = call_sp.call_one_query(sql_signup, sp_args)
        if is_suc:
            payload = {
                'id': user_uuid,
                'exp': datetime.utcnow() + timedelta(hours=1),
            }
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256').decode('utf-8')

            data = {
                'token': token
            }
            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignIn(APIView):
    permission_classes = (permissions.AllowAny,)

    @csrf_exempt
    def post(self, request):
        try:
            email = request.POST.get('email')
            passwd = request.POST.get('passwd')
            if not passwd:
                raise Exception
        except Exception:
            return response(status=status.HTTP_400_BAD_REQUEST)

        sp_args = {
            'email': email,
        }

        # Check ID
        sql_exist = 'SELECT email, passwd, customer_uuid FROM mazle_user WHERE email = %(email)s;'
        _, is_exist = call_sp.call_one_query(sql_exist, sp_args)
        if not is_exist:
            return response(status=status.HTTP_401_UNAUTHORIZED, message='User Not Found')

        # Check Passwd
        try:
            PasswordHasher().verify(is_exist['passwd'], passwd)
        except:
            return response(status=status.HTTP_401_UNAUTHORIZED, message='Invalid Passwd')

        payload = {
            'id': is_exist['customer_uuid'],
            'exp': datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256').decode('utf-8')

        data = {
            'token': token
        }
        resp = response(status=status.HTTP_200_OK, data=data)
        resp.set_cookie(key ='token', value= token, httponly=True)

        return resp


class Logout(APIView):
    permission_classes = (permissions.AllowAny,)

    @csrf_exempt
    def post(self, request):
        try:
            token = request.headers.get('token')
            if not token:
                raise Exception
        except Exception:
            return response(status=status.HTTP_403_FORBIDDEN)

        resp = response(status=status.HTTP_200_OK)
        resp.delete_cookie('token')

        return resp
