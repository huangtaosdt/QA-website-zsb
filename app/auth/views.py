from flask import render_template, redirect, url_for, request, flash
from . import auth
from .. import db
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, \
    ChangeEmailForm
from ..models import User,InvitationCode
from ..email import send_email


# @auth.before_app_request
# def before_requeset():
#     # if current_user.is_authenticated \
#     #         and not current_user.confirmed \
#     #         and request.endpoint \
#     #         and request.endpoint[:5]!='auth.' \
#     #         and request.endpoint!='static':
#     #     return redirect(url_for('auth.unconfirmed'))
#     if current_user.is_authenticated:
#         current_user.ping()
#         if not current_user.confirmed and request.endpoint[:5] != 'auth.':
#             return redirect(url_for('auth.unconfirmed'))
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))



@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect('main.index')
    print('该账户尚未确认unconfirmed: %s \n' %current_user.email)
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误！请重新输入！')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("您已退出登录!")
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # 暂停邀请码功能
        # invit_code=form.validation_code.data
        #
        # if InvitationCode.query.filter_by(code=invit_code).first() is None:
        #     flash('您输入的邀请码无效！')
        #     # return redirect(url_for("auth.register",form=form))
        #     return render_template('auth/register.html', form=form)
        # else:
        #     #     删除已使用邀请码
        #     code=InvitationCode.query.filter_by(code=invit_code).first()
        #     db.session.delete(code)
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)

        # 发送确认邮件时需要用到user id，虽然设置了自动提交，但为了防止出现延迟提交，我们要手动提交
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '请确认您的账户', 'auth/email/confirm', user=user, token=token)

        flash('激活邮件已成功发送到您的邮箱，请登录查看！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已成功确认账户，欢迎您的到来~!')
        return redirect(url_for("main.edit_profile"))
    else:
        flash('您的激活链接无效或已失效，如您尚未激活，请重新发送激活邮件.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '账户确认', 'auth/email/confirm', user=current_user, token=token)
    flash('激活邮件已成功发送到您的邮箱，请登录邮箱查看！')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            # print('equal old p?:',current_user.verify_password(form.old_password.data))
            # print('equal new p?:',current_user.verify_password(form.password.data))
            flash("您的密码已更新！")
            return redirect(url_for('main.index'))
        else:
            flash("密码输入错误，请重新输入！")
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    # if current_user.is_anonymous:
    #     return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        print('提交邮箱：',form.email.data)
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            print('存在该用户')
            token = user.generate_reset_token()
            send_email(user.email, '更改密码', 'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
            flash('密码重置邮件已发送至您的邮箱，请登录邮箱查看！')
        else:
            flash('该邮箱尚未注册，请重新输入！')
            return redirect(url_for("auth.password_reset_request"))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    # if current_user.is_anonymous:
    #     return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('您的密码已更改！')
            return redirect(url_for('auth.login'))
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '邮箱确认通知', 'auth/email/change_email',
                       user=current_user, token=token)
            flash('邮箱更改的链接已成功发送到您的邮箱，请登录查看！')
            return redirect(url_for('main.index'))
        else:
            flash('邮箱地址或密码错误！')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('恭喜您！邮箱更改成功！')
    else:
        flash('请求无效！')
    return redirect(url_for('main.index'))
