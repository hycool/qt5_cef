# coding:cp936

# by ���: bh2#qq.com
# do what you want to do with this script
# pywin32 needed

import win32con
import win32api


class InputMethod(list):
    def __init__(self):
        name = "Keyboard Layout\\Preload"
        _k_id = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, name)

        name = "System\\CurrentControlSet\\Control\\Keyboard Layouts\\"
        _i, _running, _ids = 1, True, list()
        while _running:
            _id = win32api.RegQueryValueEx(_k_id, str(_i))[0]
            _i += 1
            _k_name = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, name + _id)
            _name = win32api.RegQueryValueEx(_k_name, 'Layout Text')[0]
            print('_id = ', _id, ' _name = ', _name)
            self.append((_id, _name))
            win32api.RegCloseKey(_k_name)

    def set(self, _im):
        win32api.LoadKeyboardLayout(_im[0], win32con.KLF_ACTIVATE)


if __name__ == '__main__':
    im = InputMethod()
    for i, v in enumerate(im):
        print('�����뷨%d��: %s' % (i, v[1]))
    i = input('�������뷨(�������ֲ��س�): ')
    im.set(im[int(i)])
    print('�ɹ������뷨����Ϊ��%s��' % im[int(i)][1])
    i = input('��������ʲô��')
