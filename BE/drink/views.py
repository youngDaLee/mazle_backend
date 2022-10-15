import jwt
import base64
from django.conf import settings
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drink import call_sp
from drink import util


JWT_SECRET_KEY = getattr(settings, 'SIMPLE_JWT', None)['SIGNING_KEY']


class DrinkView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            offset = request.GET.get('offset', 0)
            limit = request.GET.get('limit', 10)
            search_keyword = request.GET.get('search_keyword', None)
            is_order = request.GET.get('is_order', None)
        except KeyError:
            offset = 0
            limit = 10

        sp_args = {
            'offset': offset,
            'limit': limit,
            'search_keyword': search_keyword,
            'order': is_order
        }
        is_suc, data = call_sp.call_sp_drink_list_select(sp_args)
        if is_suc:
            data = util.preprocessing_list_data(data)
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DrinkDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, pk):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
        except Exception:
            customer_uuid = None

        sp_args = {
            'drink_id': pk,
            'customer_uuid': customer_uuid,
        }
        is_suc, data = call_sp.call_sp_drink_select(sp_args)
        if is_suc:
            data['img'] = base64.decodebytes(data['img']).decode('latin_1')
            # 조회수 증가
            sql_query = f'''UPDATE mazle.drink
                            SET views=views+1
                            WHERE drink_id={pk};'''
            call_sp.call_query(sql_query)

            return Response(status=status.HTTP_200_OK, data=data)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
            if not customer_uuid:
                raise Exception
        except Exception:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            drink_name = request.POST.get['drink_name']
            description = request.POST.get['description']
            calorie = request.POST.get['calorie']
            manufacture = request.POST.get['manufacture']
            price = request.POST.get['price']
            large_category = request.POST.get['large_category']
            medium_category = request.POST.get['medium_category']
            small_category = request.POST.get['small_category']
            img = request.POST.get['img']
            alcohol = request.POST.get['alcohol']
            measure = request.POST.get['measure']
            caffeine = request.POST.get['caffeine']
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        sp_args = {
            'drink_name': drink_name,
            'description': description,
            'calorie': calorie,
            'manufacture': manufacture,
            'price': price,
            'large_category': large_category,
            'medium_category': medium_category,
            'small_category': small_category,
            'img': img,
            'alcohol': alcohol,
            'measure': measure,
            'caffeine': caffeine,
        }
        is_suc, _ = call_sp.call_sp_drink_set(sp_args)
        if is_suc:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
