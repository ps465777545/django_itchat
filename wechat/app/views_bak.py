from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from wxpy import *
import uuid
from wechat.settings import BASE_DIR, MEDIA_ROOT
import os, time, base64, json, random
from .models import *
from django.contrib.auth.models import User as uuu
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
        bot = Bot(cache_path=False, qr_callback=self.callback)
        return bot


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


# 获取数据库里的群列表 和 组列表
@login_required
def get_group_list(request):
    uuid_str = str(uuid.uuid4())
    group_list = groups_name.objects.all()
    set_list = grouping.objects.all()
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
        groups = bot.groups()
        print(groups)
        d['count'] = len(groups)
        for i in groups:
            d['name_list'].append(i.nick_name)
            groups_name.objects.get_or_create(
                name=i.nick_name, users_num=len(i.members), owner=i.owner.name
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
                u = groups_name.objects.filter(id=int(id))
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
                    u = groups_name.objects.filter(id=int(i))
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

            if grouping.objects.filter(group_name=set_name):
                return JsonResponse(
                    {
                        'status': False,
                        'msg': '群名重复，请检查！'
                    }
                )
            grouping_obj = grouping.objects.create(group_name=set_name)
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
    group_list = groups_name.objects.all()
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
    set_list = grouping.objects.all()
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
                        message=content, group_name=group_name, typ='群发'
                    )
                    return JsonResponse({'status': True, 'msg': '添加审核成功，请等待管理员审核！'})
                else:
                    set_id = json.loads(group_name)
                    l = []
                    for i in set_id:
                        for j in grouping.objects.get(id=int(i)).group.all():
                            d = {"gname": j.name, "owner": j.owner}

                            l.append(d)
                    print(l)
                    task.objects.create(
                        message=content, group_name=json.dumps(l, ensure_ascii=False), typ='组发'
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
                            message=uuid, uuid_str=uuid, group_name=group_name, typ='群发', message_type=message_type
                        )
                        return JsonResponse({'status': True, 'msg': '添加审核成功，请等待管理员审核！'})
                    else:
                        set_id = json.loads(group_name)
                        l = []
                        for i in set_id:
                            for j in grouping.objects.get(id=int(i)).group.all():
                                d = {"gname": j.name, "owner": j.owner}

                                l.append(d)
                        print(l)
                        task.objects.create(
                            message=uuid, uuid_str=uuid, group_name=json.dumps(l, ensure_ascii=False), typ='组发',
                            message_type=message_type
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
        task_list = task.objects.all()
        for i in task_list:

            if i.message_type != '文字':
                file_path = file.objects.get(uuid_str=i.uuid_str).file_path
                f = file_path.split('==')[-1]
                fie =file_path.split('/')[-1]
                d = {
                    'id': i.id,
                    'message': f,
                    'message_type': i.message_type,
                    'group': i.group_name,
                    'status': i.status,
                    'typ': i.typ,
                    'date': i.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'uuid': i.uuid_str,
                    'fie_yuanben': fie
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


# 发送
@login_required
def send(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        message = request.POST.get('message', '')
        message_type = request.POST.get('message_type', '')
        id = request.POST.get('id', '')
        uuid = request.POST.get('uuid', '')

        if group_name and message and id:

            group_name = json.loads(group_name)

            a = WXBot(request)
            bot = a.get_qr()
            groups = bot.groups()
            for i in group_name:
                print(i)
                print(message)
                try:

                    if message_type == '文字':  # todo
                        groups.search(i['gname'])[0].send(message)
                    elif message_type == '文件':
                        path = file.objects.get(uuid_str=uuid).file_path
                        groups.search(i['gname'])[0].send_file(path)
                    elif message_type == '视频':
                        path = file.objects.get(uuid_str=uuid).file_path
                        groups.search(i['gname'])[0].send_video(path)
                    elif message_type == '图片':
                        path = file.objects.get(uuid_str=uuid).file_path
                        groups.search(i['gname'])[0].send_image(path)
                    else:
                        pass
                except:
                    with open('error.log', 'a+') as f:
                        f.write('发送失败：{0} >>>{1}\n'.format(i['gname'], message))
                    pass
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
        'rm','rmvb','mpeg1-4','mov','mtv','dat','wmv','avi','3gp','amv','dmv','flv','mp3','mp4'
        ]
        for i in video_list:
            if i in file_name.lower():
                res['code'] = -1
                res['msg'] = '暂不支持视频文件！'
                return JsonResponse(res)
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
