from rest_framework.response import Response


MESSAGE = {
    200 :  'success',
    400 : 'Bad Request',
    403 : 'Not Authorization',
    409 : 'Confilct',
    500 : 'Internal Server Error',
}


def response(status, message='', data={}):
    if not message:
        try:
            message = MESSAGE[status]
        except:
            pass

    data = {
        'status_code': status,
        'message': message,
        'data': data
    }
    return Response(status=status, data=data)
