from flask import Blueprint, jsonify
from flask import current_app
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from models import db,UserInfo

from utills.captcha.captcha import captcha

user_blueprint = Blueprint('user',__name__,url_prefix='/user')

@user_blueprint.route('/image_yzm')
def image_yzm():
    name,yzm,image = captcha.generate_captcha()
    # yzm表示随机生成的验证码字符串
    # 将数据进行保存，方便方面对比
    session['image_yzm'] = yzm
    response = make_response(image)
    # 默认浏览器将数据作为text/html解析
    # 需要告诉浏览器当前数据的类型为image/png
    response.mimetype = 'image/png'
    return response


@user_blueprint.route('/sms_yzm')
def sms_yzm():
    # 接收数据，手机号，图片验证码
    dict1 = request.args
    mobile = dict1.get('mobile')
    yzm = dict1.get('yzm')

    if yzm != session['image_yzm']:
        return jsonify(result=1)

    # 随机生成一个四位的验证码
    import random
    yzm2 = random.randint(1000,9999)

    # 将短信验证码进行保存，用来验证
    session['sms_yzm'] = yzm2

    from utills.ytx_sdk.ytx_send import sendTemplateSMS
    # sendTemplateSMS(mobile,{yzm2,5},1)
    print(yzm2)

    return jsonify(result=2)

@user_blueprint.route('/register',methods=['POST'])
def register():
    # 接收数据
    dict1 = request.form
    mobile = dict1.get('mobile')
    yzm_image = dict1.get('yzm_image')
    yzm_sms = dict1.get('yzm_sms')
    pwd = dict1.get('pwd')

    # 验证数据的有效性
    # 保证所有的数据都被填写,列表中只要有一个值为False,则结果为False
    if not all([mobile,yzm_image,yzm_sms,pwd]):
        return jsonify(result=1)
    # 对比图片验证码
    if yzm_image != session['image_yzm']:
        return jsonify(result=2)
    # 对比短信验证码
    if int(yzm_sms) != session['sms_yzm']:
        return jsonify(result=3)
    # 判断密码的长度
    import re
    if not re.match(r'[a-zA-Z0-9_]{6,20}',pwd):
        return jsonify(result=4)
    # 验证mobile是否存在
    mobile_count=UserInfo.query.filter_by(mobile=mobile).count()
    if mobile_count > 0:
        return jsonify(result=5)

    # 创建对象
    user = UserInfo()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = pwd

    # 提交到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except:
        current_app.logger_xjzx.error('用户注册连接数据库失败')
        return jsonify(result=7)

    # 返回响应
    return jsonify(result=6)

@user_blueprint.route('/login',methods=['POST'])
def login():
    # 接收数据
    dict1 = request.form
    mobile = dict1.get('mobile')
    pwd = dict1.get('pwd')

    # 验证有效性
    if not all([mobile,pwd]):
        return jsonify(result=1)

    # 查询判断有效性
    user = UserInfo.query.filter_by(mobile=mobile).first()
    # 判断mobile是否正确
    if user:
        if user.check_pwd(pwd):
            # 状态保持
            session['user_id'] = user.id
            # 返回成功的结果
            return jsonify(result=4,avatar=user.avatar_url,nick_name=user.nick_name)
        else:
            return jsonify(result=3)
    else:
        return jsonify(result=2)


@user_blueprint.route('/logout',methods=['POST'])
def logout():
    del session['user_id']
    return jsonify(result=1)

import functools
def login_required(view_fun):
    @functools.wraps(view_fun)
    def fun2(*args,**kwargs):
        # 判断用户是否登录
        if 'user_id' not in session:
            return redirect('/')
        return view_fun(*args,**kwargs)
    return fun2

@user_blueprint.route('/')
@login_required
def index():
    # 获取当前登录的用户的ｉｄ
    user_id = session['user_id']
    # 根据编号查询当前登录用户的对象
    user = UserInfo.query.get(user_id)
    return render_template('news/user.html',user=user)

@user_blueprint.route('/base',methods=['GET','POST'])
@login_required
def base():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)

    if request.method == 'GET':
        return render_template('news/user_base_info.html',user=user)
    elif request.method == 'POST':
        # 接收数据
        dict1 = request.form
        signature = dict1.get('signature')
        nick_name = dict1.get('nick_name')
        gender = dict1.get('gender')
        if gender=='True':
            gender=True
        else:
            gender=False
        # 为属性赋值
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender

        # 提交数据库
        db.session.commit()

        #返回响应
        return jsonify(result=1)


@user_blueprint.route('/pic',methods=['GET','POST'])
@login_required
def pic():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)

    if request.method == 'GET':
        return render_template('news/user_pic_info.html',user=user)
    elif request.method == 'POST':
        avatar = request.files.get('avatar')

        # 上传到七牛云，并返回文件名
        from utills.qiniu_xjzx import upload_pic
        filename = upload_pic(avatar)

        user.avatar = filename

        # 上传到数据库
        db.session.commit()
        return jsonify(result=1,avatar=user.avatar_url)

@user_blueprint.route('/follow')
@login_required
def follow():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)

    # 获取当前页码值
    page = int(request.args.get('page','1'))
    # 通过关联属性获取关注的用户对象
    #　对查询的数据进行分页
    pagination=user.follow_user.paginate(page,4,False)
    # 获取当前页的数据
    user_list=pagination.items
    total_page=pagination.pages

    return render_template(
        'news/user_follow.html',
        user_list=user_list,
        page=page,
        total_page=total_page
    )

@user_blueprint.route('/pwd')
@login_required
def pwd():
    return render_template('news/user_pass_info.html')

@user_blueprint.route('/collect')
@login_required
def collect():
    return render_template('news/user_collection.html')

@user_blueprint.route('/release')
@login_required
def release():
    return render_template('news/user_news_release.html')

@user_blueprint.route('/newslist')
@login_required
def newslist():
    return render_template('news/user_news_list.html')