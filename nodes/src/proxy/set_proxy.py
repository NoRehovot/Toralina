import winreg as reg

from toralina_common.load_json import load_proxy


def set_proxy():
    server, port = load_proxy()
    # Path to the registry key
    internet_settings = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'

    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, internet_settings, 0, reg.KEY_WRITE)
    except FileNotFoundError:
        key = reg.CreateKey(reg.HKEY_CURRENT_USER, internet_settings)

    reg.SetValueEx(key, 'ProxyEnable', 0, reg.REG_DWORD, 1)

    proxy_server = f'{server}:{port}'
    reg.SetValueEx(key, 'ProxyServer', 0, reg.REG_SZ, proxy_server)

    reg.CloseKey(key)
