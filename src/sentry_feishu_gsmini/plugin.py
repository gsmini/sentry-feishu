# coding: utf-8
import json
import logging
import requests
from django.urls import re_path
from sentry.exceptions import PluginError
from rest_framework.response import Response
from sentry_plugins.base import CorePluginMixin
from sentry.integrations.base import FeatureDescription, IntegrationFeatures
from sentry.plugins.bases.issue2 import IssueGroupActionEndpoint, IssuePlugin2
from sentry_plugins.utils import get_secret_field_config

from .forms import FeiShuOptionsForm

logger = logging.getLogger(__name__)
DESCRIPTION = """
飞书机器人通知插件\n
你需要先去飞书群聊创建一个机器人，然后获取webhook地址填入到表单中，点击保存。\n
触发一个你项目错误就会在你配置的飞书群聊中收到一条消息
"""


class FeiShuPlugin(CorePluginMixin, IssuePlugin2):
    """
    Sentry plugin to send error  to FeiShu.
    """
    description = DESCRIPTION
    author = "gsmini@sina.cn"
    author_url = "https://github.com/gsmini/sentry-feishu"
    slug = "feishu"
    title = "飞书群聊机器人通知插件"
    version = "1.14"
    conf_title = title
    conf_key = "feishu"
    required_field = "webhook_url"
    feature_descriptions = [
        FeatureDescription(
            """
            添加飞书通知机器人地址，把sentry 接入你自己的飞书通知群。
            """,
            IntegrationFeatures.ISSUE_BASIC,
        )
    ]

    resource_links = [
        ('Source', 'https://github.com/gsmini/sentry-feishu'),
        ('Bug Tracker', 'https://github.com/gsmini/sentry-feishu/issues'),
        ('README', 'https://github.com/gsmini/sentry-feishu/blob/master/README.md'),
    ]

    project_conf_form = FeiShuOptionsForm

    # 检查参数是否填写
    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option(self.required_field, project))

    def get_group_urls(self):
        return super().get_group_urls() + [
            re_path(
                r"^autocomplete",
                IssueGroupActionEndpoint.as_view(view_method_name="view_autocomplete", plugin=self),
            )
        ]

    # 报错的时候函数
    def handle_api_error(self, error: Exception) -> Response:
        msg = "Error communicating with gsmini@sina.cn"
        status = 400 if isinstance(error, PluginError) else 502
        return Response({"error_type": "validation", "errors": {"__all__": msg}}, status=status)

    def get_configure_plugin_fields(self, project, **kwargs):
        webhook_url = self.get_option(self.required_field, project)
        helptext = (
            "输出你的飞书机器人的地址 比如: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxx"
        )
        secret_field = get_secret_field_config(webhook_url, helptext, include_prefix=True)
        secret_field.update(
            {
                "name": "webhook_url",
                "label": "feishu webhook_url",
                "placeholder": "e.g.  https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxx",
            }
        )
        return [
            secret_field
        ]

    def notify_users(self, group, event, *args, **kwargs):
        if not self.is_configured(group.project):
            return None
        if self.should_notify(group, event):
            self.post_process(group, event, *args, **kwargs)
        else:
            return None

    def findrepeatstart(self, origin, matchlen):
        if matchlen < 2 or len(origin) <= matchlen:
            return -1
        i = origin.find(origin[0:matchlen], 1)
        if i == -1:
            return self.findrepeatstart(origin, matchlen // 2)
        return i

    def findrepeatend(self, origin):
        return origin.rfind("...")

    def cutrepeat(self, origin):
        repeatstart = self.findrepeatstart(origin, 120)
        if repeatstart == -1:
            return origin
        repeatend = self.findrepeatend(origin)
        if (repeatend == -1):
            return origin
        return origin[0:repeatstart] + origin[repeatend:]

    def post_process(self, group, event, *args, **kwargs):
        """
        Process error.
        """
        if not self.is_configured(group.project):
            return

        if group.is_ignored():
            return

        send_url = self.get_option(self.required_field, group.project)
        fields = self.get_new_issue_fields(None, group, event, **kwargs)
        origin_data = {}
        included_fields = {"description", "project"}
        for field in fields:
            name = field["name"]
            if name in included_fields:
                origin_data[name] = field.get("default")

        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "来自项目:《{}》的sentry错误告警 ".format(event.project.slug),
                        "content": [
                            [

                                {
                                    "tag": "text",
                                    "text": f'错误内容:  {origin_data.get("description")} \n'
                                },

                                {
                                    "tag": "text",
                                    "text": f'点击链接访问sentry web ui查看详情:  \n'
                                },

                                {
                                    "tag": "a",
                                    "text": "点击跳转",
                                    "href": u"{}events/{}/".format(group.get_absolute_url(), event.event_id)
                                }
                            ]
                        ]
                    }
                }
            }
        }

        try:
            resp = requests.post(
                url=send_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data).encode("utf-8"),
                timeout=10
            )
            if resp.status_code != 200:
                logger.info(f"request uri {send_url} status !=200")
                logger.info(f"request uri {send_url} response:{resp.text} ")
        except requests.exceptions.Timeout:
            logger.info(f"feishu request uri {send_url} timeout")
        finally:
            logger.info(f"process notify feishu job finish.")
