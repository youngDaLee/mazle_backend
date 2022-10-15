import base64
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from home import call_sp
from util.resp import response


class HotRecipe(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        limit = request.GET.get('limit', 10)

        sp_args = {
            'limit': limit,
        }
        is_suc, data = call_sp.call_sp_home_recipe_select(sp_args)
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


class HotDrink(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        limit = request.GET.get('limit', 10)

        sp_args = {
            'limit': limit,
        }
        is_suc, data = call_sp.call_sp_home_drink_select(sp_args)
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


class HotReview(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        limit = request.GET.get('limit', 10)

        sp_args = {
            'limit': limit,
        }
        # SQL문 사용
        sql_select = '''
        SELECT drink_comment.drink_id, drink.drink_name, drink.img, drink_comment.comment, drink_comment.score
        FROM drink_comment
        LEFT JOIN drink ON drink_comment.drink_id = drink.drink_id
        ORDER BY drink_comment.score desc
        LIMIT 10;
        '''
        is_suc, data = call_sp.call_query(sql_select, sp_args)
        if is_suc:
            for row in data:
                if row['img']:
                    row['img'] = base64.decodebytes(row['img']).decode('latin_1')
            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
