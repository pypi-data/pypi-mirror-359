import logging

from cms.apphook_pool import apphook_pool
from cms.menu_bases import CMSAttachMenu
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import resolve
from django.utils.translation import get_language_from_request, gettext_lazy as _
from menus.base import Modifier, NavigationNode
from menus.menu_pool import menu_pool

from .models import PostCategory, StoriesConfig, PostContent
from .settings import MENU_TYPE_CATEGORIES, MENU_TYPE_COMPLETE, MENU_TYPE_NONE, MENU_TYPE_POSTS, get_setting

logger = logging.getLogger(__name__)


class PostCategoryMenu(CMSAttachMenu):
    """
    Main menu class

    Handles all types of blog menu
    """

    name = _("Blog menu")
    _config = {}

    def get_nodes(self, request):
        """
        Generates the nodelist

        :param request:
        :return: list of nodes
        """
        nodes = []

        language = get_language_from_request(request, check_path=True)
        current_site = get_current_site(request)

        page_site = self.instance.node.site
        if self.instance and page_site != current_site:
            return []

        categories_menu = False
        posts_menu = False
        config = False
        if self.instance:
            if not self._config.get(self.instance.application_namespace, False):
                try:
                    self._config[self.instance.application_namespace] = StoriesConfig.objects.get(
                        namespace=self.instance.application_namespace
                    )
                except StoriesConfig.DoesNotExist as e:
                    logger.exception(e)
                    return []
            config = self._config[self.instance.application_namespace]
            # if not getattr(request, "toolbar", False) or not request.toolbar.edit_mode_active:
            #     if self.instance == self.instance.get_draft_object():
            #         return []
            # else:
            #     if self.instance == self.instance.get_public_object():
            #         return []
        if config and config.menu_structure in (MENU_TYPE_COMPLETE, MENU_TYPE_CATEGORIES):
            categories_menu = True
        if config and config.menu_structure in (MENU_TYPE_COMPLETE, MENU_TYPE_POSTS):
            posts_menu = True
        if config and config.menu_structure in (MENU_TYPE_NONE,):
            return nodes

        used_categories = []
        if posts_menu:
            post_contents = PostContent.objects.filter(language=language)
            if hasattr(self, "instance") and self.instance:
                post_contents = post_contents.filter(
                    post__app_config__namespace=self.instance.application_namespace
                ).on_site()
            post_contents = (
                post_contents.distinct()
                .select_related("post", "post__app_config")
                .prefetch_related("post__categories")
            )
            for post_content in post_contents:
                postcontent_id = None
                parent = None
                used_categories.extend(post_content.post.categories.values_list("pk", flat=True))
                if categories_menu:
                    category = post_content.post.categories.first()
                    if category:
                        parent = f"{category.__class__.__name__}-{category.pk}"
                        postcontent_id = (f"{post_content.__class__.__name__}-{post_content.pk}",)
                else:
                    postcontent_id = (f"{post_content.__class__.__name__}-{post_content.pk}",)
                if postcontent_id:
                    node = NavigationNode(
                        post_content.title, post_content.get_absolute_url(language), postcontent_id, parent
                    )
                    nodes.append(node)

        if categories_menu:
            categories = PostCategory.objects
            if config:
                categories = categories.filter(app_config__namespace=self.instance.application_namespace)
            if config and not config.menu_empty_categories:
                categories = categories.active_translations(language).filter(pk__in=used_categories).distinct()
            else:
                categories = categories.active_translations(language).distinct()
            categories = (
                categories.order_by("parent__id", "translations__name")
                .select_related("app_config")
                .prefetch_related("translations")
            )
            added_categories = []
            for category in categories:
                if category.pk not in added_categories:
                    node = NavigationNode(
                        category.name,
                        category.get_absolute_url(),
                        f"{category.__class__.__name__}-{category.pk}",
                        (f"{category.__class__.__name__}-{category.parent.id}" if category.parent else None),
                    )
                    nodes.append(node)
                    added_categories.append(category.pk)

        return nodes


class PostCategoryNavModifier(Modifier):
    """
    This navigation modifier makes sure that when
    a particular blog post is viewed,
    a corresponding category is selected in menu
    """

    _config = {}

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        """
        Actual modifier function
        :param request: request
        :param nodes: complete list of nodes
        :param namespace: Menu namespace
        :param root_id: eventual root_id
        :param post_cut: flag for modifier stage
        :param breadcrumb: flag for modifier stage
        :return: nodeslist
        """
        app = None
        config = None
        if getattr(request, "current_page", None) and request.current_page.application_urls:
            app = apphook_pool.get_apphook(request.current_page.application_urls)

        if app and app.app_config:
            namespace = resolve(request.path).namespace
            if not self._config.get(namespace, False):
                self._config[namespace] = app.get_config(namespace)
            config = self._config[namespace]
        try:
            if config and (not isinstance(config, StoriesConfig) or config.menu_structure != MENU_TYPE_CATEGORIES):
                return nodes
        except AttributeError:  # pragma: no cover
            # in case `menu_structure` is not present in config
            return nodes
        if post_cut:
            return nodes
        current_postcontent = getattr(request, get_setting("CURRENT_POST_IDENTIFIER"), None)
        category = None
        if current_postcontent and current_postcontent.__class__ == PostContent:
            category = current_postcontent.categories.first()
        if not category:
            return nodes

        for node in nodes:
            if f"{category.__class__.__name__}-{category.pk}" == node.id:
                node.selected = True
        return nodes


if not hasattr(settings, "TESTS_RUNNING"):
    # For reasons not fully understood, the test environment leasds to
    # the menu pool being registered (at least) twice, which causes an error.
    # This behavior has not been observed in production.
    menu_pool.register_modifier(PostCategoryNavModifier)
    menu_pool.register_menu(PostCategoryMenu)


def clear_menu_cache(**kwargs):
    """
    Empty menu cache when saving categories
    """
    menu_pool.clear(all=True)


# post_save.connect(clear_menu_cache, sender=PostCategory)
# post_delete.connect(clear_menu_cache, sender=PostCategory)
# post_delete.connect(clear_menu_cache, sender=StoriesConfig)
