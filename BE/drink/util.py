import base64


def preprocessing_list_data(data):
    for row in data:
        row['img'] = base64.decodebytes(row['img']).decode('latin_1')

        try:
            if row['tag']:
                row['tag'] = row['tag'].split(',')
            else:
                row['tag'] = []
        except:
            pass

    return data
