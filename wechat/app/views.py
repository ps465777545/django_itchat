from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import uuid
import itchat
from wechat.settings import BASE_DIR, MEDIA_ROOT
import os, time, base64, json, random
from .models import *
from django.contrib.auth.models import User as uuu
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pymysql
conn = pymysql.connect(host='120.92.79.194', database='crawler', user='crawler', password='ASDfaeit@2351', port=3306, charset='utf8', use_unicode=True)
def handle_sql(sql, conn):
    # 使用cursor()方法获得一个游标
    cursor = conn.cursor()
    sql = sql

    cursor.execute(sql)  # 执行sql语句
    conn.commit()  # 提交到数据库执行
def select_sql(sql,conn):
    cursor = conn.cursor()
    sql = sql
    try:
        cursor.execute(sql)  # 执行sql语句
        results = cursor.fetchall()
    except Exception as e:
        raise e
    return results
def login_after():

    user_list = itchat.get_friends()
    global logon_user
    logon_user = user_list[:1][0]['NickName']

@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def reply_msg(msg):
    group_dic = {}
    mpsList = itchat.get_chatrooms(update=True)
    print(mpsList)
    time.sleep(1)
    for i in range(0, len(mpsList)):
        group_dic[mpsList[i]['UserName']] = mpsList[i]['NickName']
    print("收到一条群信息：",group_dic.get(msg['FromUserName']),msg['FromUserName'],msg['ActualUserName'], msg['ActualNickName'], msg['Content'],logon_user)
    sql = 'insert into wechat_message (group_name,message_user,message,wechat_user_name) values ("{}","{}","{}","{}");'.format(group_dic.get(msg['FromUserName']), msg['ActualNickName'], msg['Content'],logon_user)
    handle_sql(sql,conn)
    conn.commit()

# Create your views here.
qr_path = os.path.join(BASE_DIR, 'wechat/')


def path_check(qr_path):
    if os.path.exists(qr_path):
        os.remove(qr_path)


class WXBot(object):
    def __init__(self, request):
        self.qr_s = ''
        self.qr_path = qr_path + request.user.username + '.png'

    def callback(self, uuid, status, qrcode):
        f = open(self.qr_path, 'wb')
        f.write(qrcode)
        f.close()

    def get_qr(self):
        itchat.auto_login(qrCallback=self.callback,loginCallback=login_after)
        return itchat


# 获取登录二维码
@login_required
def qr_img(request):
    if request.method == 'POST':
        for i in range(5):
            time.sleep(2)
            if os.path.exists(qr_path + request.user.username + '.png'):
                res = {
                    'img': str(base64.b64encode(open(qr_path + request.user.username + '.png', 'rb').read()),
                               encoding='utf8')
                }
                return JsonResponse(res)
            continue


# def qr_img():
#     for i in range(5):
#         time.sleep(2)
#         if os.path.exists("QR" + '.png'):
#             res = {
#                 'img': str(base64.b64encode(open("QR" + '.png', 'rb').read()),
#                            encoding='utf8')
#             }
#             return JsonResponse(res)
#         continue



# 获取数据库里的群列表 和 组列表
@login_required
def get_group_list(request):
    uuid_str = str(uuid.uuid4())
    group_list = groups_name.objects.filter(user=request.user)
    set_list = grouping.objects.filter(user=request.user)
    set_res = []
    for i in set_list:
        set_name = []
        obj = i.group.all()
        for j in obj:
            set_name.append(j.name)
        d = {
            'id': i.id,
            'set_name': i.group_name,
            'group_names': ','.join(set_name),
            'num': len(obj)
        }
        set_res.append(d)
    return render(request, 'app/group_list.html', {'data': group_list, 'set': set_res, 'uuid': uuid_str})


# 添加群
@login_required
def create_group(request):
    if request.method == 'POST':
        d = {
            'count': 0,
            'name_list': []
        }
        a = WXBot(request)

        bot = a.get_qr()
        groups = bot.get_chatrooms()
        d['count'] = len(groups)
        for i in groups:
            d['name_list'].append(i['NickName'])
            groups_name.objects.get_or_create(
                name=i['NickName'], users_num=i['MemberCount'], owner='',
                user=request.user
            )
        bot.logout()
        path_check(qr_path=qr_path + request.user.username + '.png')
        return JsonResponse(d)
    else:
        return render(request, 'app/create_group.html')


# 删除群
@login_required
def delete_group(request):
    if request.method == 'POST':
        id = request.POST.get('id', '')
        typ = request.POST.get('typ', 'one')  # 默认单个删除
        if id:
            if typ == 'one':
                u = groups_name.objects.filter(id=int(id),user=request.user)
                if u:
                    u[0].delete()
                    return JsonResponse(
                        {
                            'msg': '删除成功！',
                            'status': True
                        }
                    )
                else:
                    return JsonResponse(
                        {
                            'msg': '该群不存在！',
                            'status': False
                        }
                    )
            else:
                id_list = json.loads(id)
                for i in id_list:
                    u = groups_name.objects.filter(id=int(i),user=request.user)
                    u[0].delete()
                return JsonResponse(
                    {
                        'msg': '删除成功！',
                        'status': True
                    }
                )
        else:
            return JsonResponse(
                {
                    'msg': '参数错误！',
                    'status': False
                }
            )


# 添加组
def add_set(request):
    if request.method == 'POST':
        set_name = request.POST.get('set_name', '')
        group_id_list = request.POST.get('group_name', '')
        if set_name and group_id_list:
            g_l = [int(x) for x in json.loads(group_id_list)]

            if grouping.objects.filter(group_name=set_name,user=request.user):
                return JsonResponse(
                    {
                        'status': False,
                        'msg': '群名重复，请检查！'
                    }
                )
            grouping_obj = grouping.objects.create(group_name=set_name,user=request.user)
            grouping_obj.group.set(groups_name.objects.filter(id__in=g_l))

            return JsonResponse(
                {
                    'status': True,
                    'msg': '添加成功！'
                }
            )
        else:
            return JsonResponse(
                {
                    'status': False,
                    'msg': '参数有误！'
                }
            )
    group_list = groups_name.objects.filter(user=request.user)
    return render(request, 'app/add_set.html', {'data': group_list})


# 删除组
def delete_set(request):
    if request.method == 'POST':
        id = request.POST.get('id', '')
        typ = request.POST.get('typ', 'one')
        if id:
            if typ == 'one':
                obj = grouping.objects.filter(id=int(id))
                if obj:
                    obj[0].delete()
                    return JsonResponse(
                        {
                            'status': True,
                            'msg': '删除成功！'
                        }
                    )
                else:
                    return JsonResponse(
                        {
                            'status': False,
                            'msg': '组不存在！'
                        }
                    )
            else:
                id_list = json.loads(id)
                for i in id_list:
                    obj = grouping.objects.filter(id=int(i))
                    obj[0].delete()
                return JsonResponse(
                    {
                        'status': True,
                        'msg': '删除成功！'
                    }
                )
        else:
            return JsonResponse(
                {
                    'status': False,
                    'msg': '参数有误！'
                }
            )


# 编辑组
def edit_set(request):
    if request.method == 'POST':
        set_id = request.POST.get('set_id', '')
        set_name = request.POST.get('set_name', '')
        group_id_list = request.POST.get('group_name', '')
        if set_name and group_id_list and set_id:
            g_l = [int(x) for x in json.loads(group_id_list)]

            if grouping.objects.exclude(id=int(set_id)).filter(group_name=set_name):
                return JsonResponse(
                    {
                        'status': False,
                        'msg': '群名重复，请检查！'
                    }
                )
            grouping_obj = grouping.objects.get(id=int(set_id))
            grouping_obj.group.set(groups_name.objects.filter(id__in=g_l))

            return JsonResponse(
                {
                    'status': True,
                    'msg': '添加成功！'
                }
            )
        else:
            return JsonResponse(
                {
                    'status': False,
                    'msg': '参数有误！'
                }
            )
    set_id = request.GET.get('set_id', '')

    group_name = []
    weixuan = []
    grouping_name = ''
    if set_id:
        obj = grouping.objects.filter(id=int(set_id))
        if obj:
            grouping_name = obj[0].group_name
            group_name = obj[0].group.all()
            id_list = []
            for i in group_name:
                id_list.append(i.id)
            weixuan = groups_name.objects.exclude(id__in=id_list)

    return render(request, 'app/edit_set.html',
                  {'group_name': group_name, 'weixuan': weixuan, 'grouping_name': grouping_name, 'set_id': set_id})


# 组发送
def send_set(request):
    uuid_str = str(uuid.uuid4())
    set_list = grouping.objects.filter(user=request.user)
    set_res = []
    for i in set_list:
        set_name = []
        obj = i.group.filter(user=request.user)
        for j in obj:
            set_name.append(j.name)
        d = {
            'id': i.id,
            'set_name': i.group_name,
            'group_names': ','.join(set_name),
            'num': len(obj)
        }
        set_res.append(d)
    return render(request, 'app/set_send.html', {'set': set_res, 'uuid': uuid_str})


# 提交审核 添加任务
@login_required
def add_task(request):
    if request.method == 'POST':
        t = request.POST.get('type', 'group')  # 默认是组发  群发为 set
        content = request.POST.get('content', '')
        group_name = request.POST.get('group_name', '')
        send_type = request.POST.get('send_type', 'text')  # 默认是文字
        uuid = request.POST.get('uuid')  # 区分任务
        if send_type == 'text':
            if content and groups_name:
                if t == 'group':
                    task.objects.create(
                        message=content, group_name=group_name, typ='群发',user=request.user
                    )
                    return JsonResponse({'status': True, 'msg': '添加审核成功，请等待管理员审核！'})
                else:
                    set_id = json.loads(group_name)
                    l = []
                    for i in set_id:
                        for j in grouping.objects.get(id=int(i)).group.all():
                            d = {"gname": j.name, "owner": j.owner}

                            l.append(d)
                    task.objects.create(
                        message=content, group_name=json.dumps(l, ensure_ascii=False), typ='组发',user=request.user
                    )
                    return JsonResponse({'status': True, 'msg': '添加审核成功，请等待管理员审核！'})
            else:
                return JsonResponse({'status': False, 'msg': '参数错误！'})
        else:
            if groups_name:
                if send_type == 'file':
                    message_type = '文件'
                elif send_type == 'video':
                    message_type = '视频'
                else:
                    message_type = '图片'
                f_obj = file.objects.filter(uuid_str=uuid)
                if f_obj:
                    if t == 'group':
                        task.objects.create(
                            message=uuid, uuid_str=uuid, group_name=group_name, typ='群发', message_type=message_type,
                            user=request.user
                        )
                        return JsonResponse({'status': True, 'msg': '添加审核成功，请等待管理员审核！'})
                    else:
                        set_id = json.loads(group_name)
                        l = []
                        for i in set_id:
                            for j in grouping.objects.get(id=int(i)).group.all():
                                d = {"gname": j.name, "owner": j.owner}

                                l.append(d)

                        task.objects.create(
                            message=uuid, uuid_str=uuid, group_name=json.dumps(l, ensure_ascii=False), typ='组发',
                            message_type=message_type,user=request.user
                        )
                        return JsonResponse({'status': True, 'msg': '添加审核成功，请等待管理员审核！'})
                else:
                    return JsonResponse({'status': False, 'msg': '尚未上传附件，请先上传附件后再提交！'})
            else:
                return JsonResponse({'status': False, 'msg': '参数错误！'})


# 审核列表
@login_required
def check_list(request):
    if request.method == 'POST':
        data = {
            'msg': '',
            'data': [],
            'count': '',
            'code': 0,
        }
        check = request.POST.get('check','')
        if check:
            task_list = task.objects.all()
        else:
            task_list = task.objects.filter(user=request.user)
        for i in task_list:

            if i.message_type != '文字':
                file_path = file.objects.get(uuid_str=i.uuid_str).file_path
                f = file_path.split('==')[-1]
                fie = file_path.split('/')[-1]
                d = {
                    'id': i.id,
                    'message': f,
                    'message_type': i.message_type,
                    'group': i.group_name,
                    'status': i.status,
                    'typ': i.typ,
                    'date': i.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'uuid': i.uuid_str,
                    'fie_yuanben': fie,
                    'send_user':i.user.username
                }
            else:
                d = {
                    'id': i.id,
                    'message': i.message,
                    'message_type': i.message_type,
                    'group': i.group_name,
                    'status': i.status,
                    'typ': i.typ,
                    'date': i.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'uuid': i.uuid_str,
                    'send_user': i.user.username
                }
            data['data'].append(d)
        return JsonResponse(data)

    return render(request, 'app/check_list.html')


# 删除任务
@login_required
def delete_task(request):
    if request.method == 'POST':
        id = request.POST.get('id', '')
        typ = request.POST.get('typ', 'one')
        if id:
            if typ == 'one':
                s = task.objects.filter(id=int(id))
                if s:
                    s[0].delete()
                    return JsonResponse(
                        {
                            'status': True,
                            'msg': '成功！'
                        }
                    )
                else:
                    return JsonResponse(
                        {
                            'status': False,
                            'msg': '参数有误！'
                        }
                    )
            else:
                id_list = json.loads(id)
                for i in id_list:
                    s = task.objects.filter(id=int(i))
                    s[0].delete()
                return JsonResponse(
                    {
                        'status': True,
                        'msg': '成功！'
                    }
                )


        else:
            return JsonResponse(
                {
                    'status': False,
                    'msg': '参数有误！'
                }
            )


# 审核
@login_required
def check(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        message = request.POST.get('message', '')
        id = request.POST.get('id', '')
        if group_name and message and id:
            group_name = json.loads(group_name)

            t = task.objects.get(id=int(id))
            t.message = message
            t.status = '审核通过'
            t.save()
            return JsonResponse(
                {
                    'status': True,
                    'msg': '审核通过！'
                }
            )
        else:
            return JsonResponse(
                {
                    'status': False,
                    'msg': '参数有误！'
                }
            )
    return render(request, 'app/check.html')


# 发送 todo
@login_required
def send(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        message = request.POST.get('message', '')
        message_type = request.POST.get('message_type', '')
        id = request.POST.get('id', '')
        uuid = request.POST.get('uuid', '')

        send_sta = True
        error_msg = ''
        if group_name and message and id:

            group_name = json.loads(group_name)

            a = WXBot(request)
            bot = a.get_qr()
            mediaId = None
            for i in group_name:
                try:
                    if message_type == '文字':  # todo
                        bot.search_chatrooms(name=i['gname'])[0].send(message)
                    elif message_type == '文件':
                        path = file.objects.get(uuid_str=uuid).file_path
                        response, media_id =bot.search_chatrooms(name=i['gname'])[0].send_file(path,mediaId=mediaId)
                        mediaId = media_id
                    elif message_type == '视频':
                        path = file.objects.get(uuid_str=uuid).file_path
                        response,media_id = bot.search_chatrooms(name=i['gname'])[0].send_video(path,mediaId=mediaId)
                        mediaId = media_id
                    elif message_type == '图片':
                        path = file.objects.get(uuid_str=uuid).file_path
                        response, media_id =bot.search_chatrooms(name=i['gname'])[0].send_image(path,mediaId=mediaId)
                        mediaId = media_id
                    else:
                        pass
                except:
                    with open('error.log', 'a+') as f:
                        f.write('发送失败：{0} >>>{1}\n'.format(i['gname'], message))
                    error_msg += '{0},'.format(i['gname'])
                    send_sta = False
                    return JsonResponse(
                        {
                            'status': False,
                            'msg': error_msg + ' 发送失败！'
                        }
                    )
                time.sleep(random.random())
            bot.logout()
            path_check(qr_path=qr_path + request.user.username + '.png')
            t = task.objects.get(id=int(id))
            t.status = '已发送'
            t.save()
            return JsonResponse(
                {
                    'status': True,
                    'msg': '发送成功！'
                }
            )
        else:
            return JsonResponse(
                {
                    'status': False,
                    'msg': '参数有误！'
                }
            )
    return render(request, 'app/send.html')


# 登录
def do_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            try:
                session_urls = []
                role_name = []
                role_list = User.objects.get(username=username).myuser.role.all()
                for role in role_list:
                    role_name.append(role.role_name)
                    permission_list = role.permission.all()
                    for permission in permission_list:
                        session_urls.append(permission.url)

                request.session['urls'] = json.dumps(session_urls)
                request.session['role_name'] = json.dumps(role_name)
            except:
                # 这块表示该用户没有设置任何角色
                return render(request, 'login.html', {"err": "该账号异常，请联系管理员！"})
            login(request, user)
            return redirect(reverse('get_group_list'))
        else:
            return render(request, 'login.html', {"err": "账号密码错误或被冻结，请联系管理员！"})
    return render(request, 'login.html')


def do_logout(request):
    logout(request)
    return redirect(reverse('do_login'))


def forbidden(request):
    return render(request, 'forbidden.html')


# 上传
def upload(request):
    res = {
        "code": 0,
        "msg": "上传成功",
        "data": {
            "src": "http://cdn.layui.com/123.jpg"
        }
    }
    now = str(datetime.now().strftime('%Y%m%d%H%M%S'))
    if request.method == 'POST':
        uuid = request.GET.get('uuid')
        f = request.FILES.get('file')
        file_name = now + '==' + f.name
        video_list = [
            'rm', 'rmvb', 'mpeg1-4', 'mov', 'mtv', 'dat', 'wmv', 'avi', '3gp', 'amv', 'dmv', 'flv', 'mp3', 'mp4'
        ]
        # for i in video_list:
        #     if i in file_name.lower():
        #         res['code'] = -1
        #         res['msg'] = '暂不支持视频文件！'
        #         return JsonResponse(res)
        path = os.path.join(MEDIA_ROOT, file_name)
        destination = open(path, 'wb+')  # 打开特定的文件进行二进制的写操作
        for chunk in f.chunks():  # 分块写入文件
            destination.write(chunk)
        destination.close()

        f_obj = file.objects.get_or_create(
            uuid_str=uuid
        )
        f_obj[0].file_path = path
        f_obj[0].save()

        res['msg'] = f.name + '，上传成功！'
        return JsonResponse(res)


# 添加好友
def add_friend(request):
    res = {
        "code": 0,
        "msg": "上传成功",
        "data": {
            "src": "http://cdn.layui.com/123.jpg"
        }
    }
    if request.method == 'POST':
        f = request.FILES.get('file')
        file_name = 'add_friend_' + f.name
        path = os.path.join(MEDIA_ROOT, file_name)
        destination = open(path, 'wb+')  # 打开特定的文件进行二进制的写操作
        for chunk in f.chunks():  # 分块写入文件
            destination.write(chunk)
        destination.close()

        def read_file(path):
            f = open(path)
            while True:
                i = f.readline()
                if not i:
                    break
                yield i

        add_list = []
        line = 0
        for j in read_file(path=path):
            if line == 0:
                # 首行跳过
                line += 1
                continue
            friend_username = j.split(',')
            if friend_username:
                j = friend_username[0].replace('\n','')
            else:
                continue
            add_list.append(wechat_friend(friend_username=j))
            line += 1
        wechat_friend.objects.using('mysql').bulk_create(add_list)
        res['msg'] = f.name + '，添加任务成功，共{0}条！'.format(line-1)
        return JsonResponse(res)
    return render(request, 'app/add_friend.html')

# 消息采集
@login_required
def wxMessage(request):
    if request.method == 'POST':
        a = WXBot(request)

        bot = a.get_qr()

        return HttpResponse('success')
    else:
        return render(request, 'app/create_group.html')
