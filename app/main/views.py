import os
from  datetime import datetime
from flask import jsonify, render_template, session, redirect, url_for, abort, flash, request, current_app, \
    make_response
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, CommentForm, ScoreFrom
from .. import db
from ..models import User, Role, Post, Permission, Comment, Group, AnonymousUser, Score
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from werkzeug.utils import secure_filename
from flask_sqlalchemy import get_debug_queries


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    # if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
    #     post = Post(group_id=form.category.id,
    #                 title=form.title.data,
    #                 body=form.body.data,
    #                 author=current_user._get_current_object())
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)

    # show_group = request.cookies.get('show_group')
    # if show_group and show_group != 'all':  # 如果cookie中存在类别，即用户选了哪类文章，则进行进一步判断并返回该类文章。
    #     print('show_second:', show_group)
    #     query = Post.query.join(Group, Group.id == Post.group_id).filter(Group.post_type == show_group)
    # else:
    #     print('all or none')
    #     query = Post.query
    # pagination = query.order_by(Post.timestamp.desc()).paginate(
    #     page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #     error_out=False)
    # posts = pagination.items
    # return render_template('index.html', form=form, posts=posts, show_followed=False, pagination=pagination)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    hot_posts = Post.query.order_by(Post.read_times.desc()).limit(10).all()
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination, hot_posts=hot_posts)


@main.route('/other/<type>', methods=['GET', 'POST'])
def other(type):
    # posts = Post.query.filter_by(group_id=type).all()
    form = PostForm()

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(group_id=type).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    hot_posts = Post.query.order_by(Post.read_times.desc()).limit(10).all()
    if current_user.is_authenticated == False:
        return render_template("need_login.html")
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, group_id=type,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.other', type=type, _anchor="#"))

    return render_template('other.html', posts=posts, form=form,
                           pagination=pagination, hot_posts=hot_posts)


# 新增选择文章类别路由
# @main.route('/group/<group>')
# def show_group(group):
#     resp = make_response(redirect(url_for('.index')))
#     resp.set_cookie('show_group', group, max_age=30 * 24 * 60 * 60)
#     return resp


# 主页仅显示自己的文章，暂时去掉show_followed、all判断

@main.route('/score', methods=['GET', 'POST'])
def show_score():
    form = ScoreFrom()
    hot_posts = Post.query.order_by(Post.read_times.desc()).limit(10).all()
    if current_user.is_authenticated == False:
        return render_template("need_login.html")

    # # 用户点击查询，则返回相应专业的成绩数据--json格式
    # if form.validate_on_submit():
    # #     major = form.major.data
    # #     score = Score.query.filter_by(major=major).first()
    # #     json_data = {major: score.major}
    # #     return jsonify(json_data)
    #     return query_score(form.major.data)
    return render_template('score.html', form=form, hot_posts=hot_posts)


@main.route('/query_score/<major_id>', methods=['GET', 'POST'])
def query_score(major_id):
    score = Score.query.filter_by(id=major_id).first()
    all_score = [score.year_2013, score.year_2014, score.year_2015, score.year_2016, score.year_2017]
    json_data = {'major': score.major, 'score': all_score}
    return jsonify(json_data)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/hot-topic')
def get_hot_topic():
    query = Post.query.order_by(Post.read_times.desc()).limit(10).all()


@main.route('/user/<username>')
def user(username):
    # user=User.query.filter_by(username=username).first()
    # if user is None:
    #     abort(404)
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    hot_posts = Post.query.order_by(Post.read_times.desc()).limit(10).all()
    return render_template('user.html', user=user, posts=posts,
                           hot_posts=hot_posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.school = form.school.data
        current_user.major = form.major.data
        current_user.about_me = form.about_me.data
        # user icon
        avatar = request.files['avatar']
        filename = secure_filename(avatar.filename).strip()
        # if filename:
        #     print("here")
        # print('filename is none? ',filename == "")

        if filename != "":
            try:
                filename.rsplit('.')[1]
            except:
                # 中文文件名无法读取，若是中文文件名，用用户名做前缀：✖️✖️✖️.jpg
                print("头像文件名为中文:", filename)
                filename = current_user.username + '.' + filename
                print('文件名已更正：', filename)
        UPLOAD_FOLDER = '{}{}'.format(os.getcwd(), '/app/static/avatar/')
        # print('当前工作目录：', UPLOAD_FOLDER)
        ALLOWED_EXTENSIONS = ['png', 'gif', 'jpeg', 'jpg', '']
        flag = '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

        if filename and not flag:
            flash('仅允许上传以下格式的图片： png,gif,jpeg or jpg.')
            return redirect(url_for('.edit_profile'))

        if filename:
            new_file_name = current_user.username + '_avatar.' + filename.rsplit(".")[1]
            file_location = '{}{}'.format(UPLOAD_FOLDER, new_file_name)
            avatar.save(file_location)
            current_user.avatar = '/static/avatar/{}_avatar.{}'.format(current_user.username, filename.rsplit(".")[1])
            # print(current_user.avatar)
        db.session.add(current_user)
        flash('您的资料已经更新')
        return redirect(url_for('.user', username=current_user.username))

    form.name.data = current_user.name
    form.school.data = current_user.school
    form.major.data = current_user.major
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.school = form.school.data
        user.major = form.major.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('资料更新成功！')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.school.data = user.school
    form.major.data = user.major
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()

    # 增加访问次数
    # is_authenticated 是否认证，即是否已登陆
    if current_user.is_authenticated == False or current_user.id != post.author_id:
        post.read_times = post.read_times + 1
        db.session.add(post)
        db.session.commit()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        flash('评论发表成功！')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config[
        'FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)
    # 参数之所以传列表：[post]  是因为我们在_posts.html中使用的是列表，我们想重用_posts.html中对渲染，以实现对文章页面对渲染


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    # 如果当前用户不是文章作者且不是网站管理员----若是管理员则应具有编辑任何文章的权限
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        # post.group_id = form.category.data
        # post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        flash('文章发布成功 (≥◇≤)～')
        return redirect(url_for('.post', id=post.id))
    # form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/delete/<int:id>')
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    db.session.delete(post)
    flash("文章已经删除！")
    return redirect(url_for(".index"))


# 新增写作功能--- 单独页面
@main.route('/write', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def write():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(group_id=form.category.data,
                    title=form.title.data,
                    body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        # print('group_id in write:', post.group_id)
        flash('Article has benn published.')
        return redirect(url_for('.post', id=post.id))
    return render_template('create_post.html', form=form)


@main.route('/add_like/<int:id>')
def add_like(id):
    # print('here add like .')
    post = Post.query.get_or_404(id)
    post.like_times = post.like_times + 1
    db.session.add(post)
    db.session.commit()
    json_data = {'like_times': post.like_times}
    return jsonify(json_data)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                         error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, fan_counts=len(follows),
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/delete_comment/<int:post_id>/<int:comment_id>')
@login_required
def delete_comment(post_id,comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user != comment.author and not current_user.can(Permission.MODERATE_COMMENTS):
        abort(403)
    db.session.delete(comment)
    flash("评论已删除！")
    return redirect(url_for(".post",id=post_id))



@main.route('/moderate_user')
@login_required
@permission_required(Permission.ADMINISTER)
def moderate_user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.member_since.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    users = pagination.items
    return render_template('moderate_user.html', users=users, pagination=pagination, page=page)

@main.route('/moderate_user/delete/<int:id>')
@login_required
@permission_required(Permission.ADMINISTER)
def delete_user(id):
    user=User.query.get_or_404(id)
    db.session.delete(user)
    flash("用户已删除！")
    return redirect(url_for(".moderate_user",_anchor='manage_body'))

@main.route('/moderate_user/chang_user_role/<int:user_id>/<int:role_id>')
@login_required
@permission_required(Permission.ADMINISTER)
def chang_user_role(user_id,role_id):
    user=User.query.get_or_404(user_id)
    user.role_id=role_id
    db.session.add(user)
    db.session.commit()
    flash('用户权限已更改！')
    return redirect(url_for(".moderate_user",_anchor='manage_body'))

@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response
