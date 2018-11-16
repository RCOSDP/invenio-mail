
import pytest
import flask
from flask_admin import Admin
from invenio_db import InvenioDB, db
from invenio_mail import InvenioMail


def test_mail_index_get(email_admin_app):
    app_context = email_admin_app.test_request_context()
    app_context.push()
    client = email_admin_app.test_client()
    res = client.get(flask.url_for('mail.index'))
    assert res.status_code == 200
