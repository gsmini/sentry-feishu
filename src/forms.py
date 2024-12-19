# coding: utf-8

from django import forms


class FeiShuOptionsForm(forms.Form):
    url = forms.CharField(
        max_length=255,
        help_text='robot Webhook url(飞书机器人webhook地址url)'
    )
