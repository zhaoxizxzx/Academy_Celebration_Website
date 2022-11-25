import requests
import os
import time

# 转化后图片名称是 nobg_ + 原来文件名称.png
def AI_img2nobg(PIL_name):

    key = 'c6vLHWNS7fDFAvoMXk3uo4mB'
    dt = time.strftime("%Y年%m月%d日%X")
    print(dt)

    nt = dt.replace(":", "时", 1)
    nt = nt.replace(":", "分", 1)
    nt = nt + "秒"
    print(nt)
    new_file_name = os.path.join('./static/img/nohuman/nobg_'+nt+PIL_name)
    with open(PIL_name, 'rb') as f:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': f},
            data={
                'size': "regular",
                'bg_color': None
            },
            headers={'X-Api-Key': key})
        with open(new_file_name, 'wb') as removed_bg_file:
             removed_bg_file.write(response.content)
    return new_file_name