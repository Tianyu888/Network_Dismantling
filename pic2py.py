# -*- coding: utf-8 -*-
# @Time    : 2018/6/6 18:29
# @Author  : Octan3
# @Email   : Octan3@stu.ouc.edu.cn
# @File    : Pic2py.py
# @Software: PyCharm

import base64


def pic2py(picture_name):
    """
    :param picture_name:
    :return:
    """
    open_pic = open("%s" % picture_name, 'rb')
    b64str = base64.b64encode(open_pic.read())
    open_pic.close()
    write_data = 'img = "%s"' % b64str.decode()
    tmp = '%s.py' % picture_name.replace('.', '_')
    tmp = '.' + tmp[1:]
    f = open(tmp, 'w+')
    f.write(write_data)
    f.close()


if __name__ == '__main__':
    # pics = ["one.png", "two.png", "com.png", "socket.png", "win.png"]
    pics = ["./pics/bomb.jpg","./pics/color.png","./pics/drag.png","./pics/layout.png"]
    for i in pics:
        pic2py(i)
    print("ok")

