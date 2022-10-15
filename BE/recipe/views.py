import jwt
import base64
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
import recipe.util as util
import recipe.call_sp as call_sp
from recipe.es_conn import MakeESQuery
from util.resp import response


JWT_SECRET_KEY = getattr(settings, 'SIMPLE_JWT', None)['SIGNING_KEY']


class RecipeView(APIView):
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
        is_suc, data = call_sp.call_sp_recipe_list_select(sp_args)
        if is_suc:
            for row in data:
                if row['img']:
                    row['img'] = base64.decodebytes(row['img']).decode('latin_1')
            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecipeESView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            offset = request.GET.get('offset', 0)
            limit = request.GET.get('limit', 10)
            sort_by = request.GET.get('sort_by', None)

            search_keyword = request.GET.get('search_keyword', None)
            recipe_name = request.GET.get('recipe_name', None)
            price = request.GET.get('price', None)  # [0, 5000]
            tag = request.GET.getlist('tag', [])  # list
            large_category = request.GET.get('large_category', None)
            medium_category = request.GET.get('medium_category', None)
            small_category = request.GET.get('small_category', None)

        except KeyError:
            offset = 0
            limit = 10

        try:
            es = MakeESQuery(
                search_query=search_keyword,
                recipe_name=recipe_name,
                price=price,
                tag=tag,
                large_category=large_category,
                medium_category=medium_category,
                small_category=small_category,
                sort_by=sort_by,
                offset=offset,
                limit=limit,
            )
            es.make_query()
            data = es.run_query('recipe')
            data = util.preprocessing_recipe_es_data(data)
            return response(status=status.HTTP_200_OK, data=data)
        except Exception as ex:
            print(ex)
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)       


class RecipeDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, pk):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
        except Exception:
            customer_uuid = None

        sp_args = {
            'recipe_id': pk,
            'customer_uuid': customer_uuid,
        }
        is_suc, data = call_sp.call_sp_recipe_select(sp_args)
        if is_suc:
            data = util.preprocessing_recipe_data(data)

            sql_query = f'''UPDATE mazle.recipe
                            SET views=views+1
                            WHERE recipe_id={pk};'''
            _, _ = call_sp.call_query(sql_query)

            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @csrf_exempt
    def post(self, request):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
        except Exception:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Json Raw 데이터로 보내는 경우
            recipe_name = request.data['recipe_name']
            summary = request.data['summary']
            description = request.data['description']
            img = request.data['img']
            price = request.data['price']
            mesaure_standard = request.data['mesaure_standard']
            tip = request.data['tip']
            diff_score = request.data['diff_score']
            price_score = request.data['price_score']
            sweet_score = request.data['sweet_score']
            alcohol_score = request.data['alcohol_score']
            tag_list = request.data['tag_list']
            main_meterial_list = request.data['main_meterial']
            sub_meterial_list = request.data['sub_meterial']

            ''' Form 데이터 형식으로 보낼 경우
            recipe_name = request.POST.get('recipe_name')
            summary = request.POST.get('summary')
            description = request.POST.getlist('description')
            img = request.POST.get('img')
            price = request.POST.get('price')
            mesaure_standard = request.POST.get('mesaure_standard')
            tip = request.POST.get('tip')
            diff_score = request.POST.get('diff_score')
            price_score = request.POST.get('price_score')
            sweet_score = request.POST.get('sweet_score')
            alcohol_score = request.POST.get('alcohol_score')
            tag_list = request.POST.getlist('tag_list')
            main_meterial_list = request.POST.getlist('main_meterial')
            sub_meterial_list = request.POST.getlist('sub_meterial')
            '''
        except KeyError:
            return response(status=status.HTTP_400_BAD_REQUEST)

        sp_args = {
            'customer_uuid': customer_uuid,
            'recipe_name': recipe_name,
            'summary': summary,
            'description': "<tr>".join(description),
            'img': img,
            'price': price,
            'mesaure_standard': mesaure_standard,
            'tip': tip,
            'diff_score': diff_score,
            'price_score': price_score,
            'sweet_score': sweet_score,
            'alcohol_score': alcohol_score,
            'tag_list': tag_list,
            'main_meterial': main_meterial_list,
            'sub_meterial': sub_meterial_list,
        }
        is_suc, _ = call_sp.call_sp_recipe_set(sp_args)

        if is_suc:
            return response(status=status.HTTP_200_OK)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @csrf_exempt
    def delete(self, request, pk):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
        except Exception:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        sp_args = {
            'customer_uuid': customer_uuid,
            'recipe_id': pk,
        }
        is_suc, _ = call_sp.call_sp_recipe_delete(sp_args)
        if is_suc:
            return response(status=status.HTTP_200_OK)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecipeReviewView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, pk):
        try:
            offset = request.GET.get('offset')
            limit = request.GET.get('limit')
        except KeyError:
            return response(status=status.HTTP_400_BAD_REQUEST)

        sp_args = {
            'recipe_id': pk,
            'offset': offset,
            'limit': limit,
        }
        is_suc, data = call_sp.call_sp_recipe_comment_select(sp_args)
        if is_suc:
            for d in data:
                d['score'] = int(d['score'])
            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @csrf_exempt
    def post(self, request, pk):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
        except Exception:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            comment = request.POST['comment']
            score = request.POST['score']
        except KeyError:
            return response(status=status.HTTP_400_BAD_REQUEST)

        sp_args = {
            'customer_uuid': customer_uuid,
            'recipe_id': pk,
            'comment': comment,
            'score': score,
        }
        is_suc, _ = call_sp.call_sp_recipe_comment_set(sp_args)

        if is_suc:
            return response(status=status.HTTP_200_OK)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecipeLikeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, recipe_id):
        '''
        유저가 해당 recipe_id에 좋아요 했는지 여부
        '''
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
        except Exception:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        sp_args = {
            'customer_uuid': customer_uuid,
            'recipe_id': recipe_id,
        }
        is_suc, data = call_sp.call_sp_recipe_like_select(sp_args)

        if is_suc:
            if data:
                data = {'is_like': True}
            else:
                data = {'is_like': False}

            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @csrf_exempt
    def post(self, request, recipe_id):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
        except Exception:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        sp_args = {
            'customer_uuid': customer_uuid,
            'recipe_id': recipe_id,
        }

        # Check like
        sql = '''SELECT COUNT(0) as cnt FROM recipe_like WHERE customer_uuid=%(customer_uuid)s;'''
        _, data = call_sp.call_one_query(sql, sp_args)
        print(data['cnt'])
        if data['cnt'] == 0:  # 좋아요 등록
            is_suc, _ = call_sp.call_sp_recipe_like_set(sp_args)
            message = 'Like Registration success'
        else:  # 좋아요 취소
            is_suc, _ = call_sp.call_sp_recipe_like_delete(sp_args)
            message = 'Like Delete success'

        if is_suc:
            return response(status=status.HTTP_200_OK, message=message)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeterialView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            meterial_name = request.GET.get('meterial_name', None)
        except KeyError:
            meterial_name = None

        sp_args = {
            'meterial_name': meterial_name,
        }
        is_suc, data = call_sp.call_sp_meterial_select(sp_args)
        if is_suc:
            # data = util.preprocessing_list_data(data)
            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)      

    @csrf_exempt
    def post(self, request):
        try:
            token = request.headers.get('token')
            user = jwt.decode(token, JWT_SECRET_KEY, algorithms='HS256')

            customer_uuid = user['id']
        except Exception:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            meterial_name = request.POST['meterial_name']
            img = request.POST.get('img')
        except KeyError:
            return response(status=status.HTTP_401_UNAUTHORIZED)

        sp_args = {
            'meterial_name': meterial_name,
            'img':img,
        }
        is_suc, data = call_sp.call_sp_meterial_set(sp_args)
        if is_suc:
            return response(status=status.HTTP_200_OK, data=data)
        else:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
