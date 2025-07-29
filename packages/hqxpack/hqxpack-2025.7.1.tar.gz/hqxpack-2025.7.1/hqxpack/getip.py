import socket
def getIP():
    name = socket.gethostname()
    # 只能获得内网地址
    return socket.gethostbyname(name) 
