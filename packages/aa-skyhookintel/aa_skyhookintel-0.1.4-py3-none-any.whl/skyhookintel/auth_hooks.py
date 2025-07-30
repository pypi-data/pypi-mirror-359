from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls
from .models import Skyhook


class ExampleMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Skyhook Intel"),
            "fas fa-snowflake fa-fw",
            "skyhookintel:index",
            navactive=["skyhookintel:"],
        )

    def render(self, request):
        if request.user.has_perm("skyhookintel.basic_access"):
            self.count = Skyhook.get_next_hour_skyhooks().count()
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return ExampleMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "skyhookintel", r"^skyhookintel/")
