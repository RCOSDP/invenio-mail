# -*- coding: utf-8 -*-

import sys

from flask import abort, current_app, flash, request
from flask_admin import BaseView, expose
from flask_babelex import gettext as _
from flask_mail import Message
from werkzeug.local import LocalProxy

from . import config
from invenio_mail.models import MailConfig

_app = LocalProxy(lambda: current_app.extensions['weko-admin'].app)


def _load_mail_cfg_from_db():
    return MailConfig.get_config()


def _save_mail_cfg_to_db(cfg):
    MailConfig.set_config(cfg)


def _set_flask_mail_cfg(cfg):
    current_app.extensions['mail'].suppress = False
    current_app.extensions['mail'].server = cfg['mail_server']
    current_app.extensions['mail'].port = cfg['mail_port']
    current_app.extensions['mail'].username = cfg['mail_username']
    current_app.extensions['mail'].password = cfg['mail_password']
    current_app.extensions['mail'].use_tls = cfg['mail_use_tls']
    current_app.extensions['mail'].use_ssl = cfg['mail_use_ssl']
    current_app.extensions['mail'].default_sender = cfg['mail_default_sender']


class MailSettingView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        mail_cfg = {
            'mail_server': 'localhost',
            'mail_port': 25,
            'mail_use_tls': False,
            'mail_use_ssl': False,
            'mail_username': None,
            'mail_password': None,
            'mail_default_sender': None}
        try:
            mail_cfg.update(_load_mail_cfg_from_db())
            mail_cfg['mail_use_tls'] = False
            mail_cfg['mail_use_ssl'] = False
            if request.method == 'POST':
                mail_cfg.update(request.form.to_dict())
                if 'mail_use_tls' in request.form.to_dict():
                    mail_cfg['mail_use_tls'] = True
                if 'mail_use_ssl' in request.form.to_dict():
                    mail_cfg['mail_use_ssl'] = True
                print(mail_cfg)
                _save_mail_cfg_to_db(mail_cfg)
                flash(_('Mail settings have been updated.'),
                      category='success')
            return self.render(config.INVENIO_MAIL_SETTING_TEMPLATE,
                               mail_cfg=mail_cfg)
        except:
            current_app.logger.error('Unexpected error: ', sys.exc_info()[0])
        return abort(400)

    @expose('/send_mail', methods=['POST'])
    def send_mail(self):
        try:
            mail_cfg = _load_mail_cfg_from_db()
            _set_flask_mail_cfg(mail_cfg)
            msg = Message()
            rf = request.form.to_dict()
            msg.subject = rf['subject']
            msg.body = rf['body']
            msg.recipients = [rf['recipient']]
            current_app.extensions['mail'].send(msg)
            flash(_('Test mail sent.'), category='success')
        except Exception as ex:
            flash(_('Failed to send mail.'), category='error')
            flash(_(str(ex)), category='error')
        return self.render(config.INVENIO_MAIL_SETTING_TEMPLATE,
                           mail_cfg=mail_cfg)


mail_adminview = {
    'view_class': MailSettingView,
    'kwargs': {
        'category': _('Setting'),
        'name': _('Mail'),
        'endpoint': 'mail'
    }
}


__all__ = (
    'mail_adminview',
)
