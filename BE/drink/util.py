import base64


def preprocessing_list_data(data):
    for d in data:
        d['img'] = base64.decodebytes(d['img']).decode('latin_1')

    return data
