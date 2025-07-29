from io import BytesIO
from os.path import basename
from random import randbytes
from shutil import copyfileobj

import requests

def chevereto_image_upload(img_path, chevereto_host, chevereto_api_key):
    """
    Uploads an image to given chevereto instance and returns the image url on success
    """

    def make_it_unique(input_file, output_file):
        copyfileobj(input_file, output_file)
        output_file.write(randbytes(16))
        return output_file

    headers = {'X-API-Key': chevereto_api_key}

    with open(img_path, 'rb') as f:
        output_buffer = BytesIO()
        unique_buffer = make_it_unique(f, output_buffer)
        unique_buffer.seek(0)
        file = {'source': (basename(img_path), unique_buffer)}
        r = requests.post(f'https://{chevereto_host}/api/1/upload',
                          headers=headers,
                          timeout=10,
                          files=file
        )

    if r.json()['status_code'] == 200:
        return r.json()['image']['url']
    raise RuntimeError(r.json())
