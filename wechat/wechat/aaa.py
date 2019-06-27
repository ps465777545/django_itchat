import itchat

itchat.auto_login(enableCmdQR=2, hotReload=True)

groups = ['测试这是', '测试2']

mediaId = None
for i in groups:
    res, media_id = itchat.search_chatrooms(name=i)[0].send_video('a.mp4', mediaId=mediaId)
    mediaId =media_id

