# -*- coding: utf-8 -*-
from eea.facetednavigation.layout.layout import FacetedLayout
from library.policy import _
from plone import api
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from Products.CMFPlone.interfaces import INonInstallable
from zope.component import getUtility
from zope.interface import implementer

import os


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "library.policy:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide unwanted products from site-creation and quickinstaller."""
        return [
            "library.policy.upgrades",
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    portal = api.portal.get()
    add_stucture(portal)
    disable_site_actions_viewlet(portal)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def add_stucture(portal):
    # Folder professionals
    if "explorer" not in portal:
        obj = create_content("Folder", _("Explorer"), portal)
        _activate_dashboard_navigation(obj, True, "/faceted/config/explorer.xml")
        layout = FacetedLayout(obj)
        layout.update_layout(layout="faceted-map")
        _publish(obj)


def create_content(type_content, title, parent):
    new_obj = api.content.create(type=type_content, title=title, container=parent)
    return new_obj


def _activate_dashboard_navigation(context, configuration=False, path=None):
    subtyper = context.restrictedTraverse("@@faceted_subtyper")
    if subtyper.is_faceted():
        return
    subtyper.enable()
    if configuration and path:
        config_path = os.path.dirname(__file__) + path
        with open(config_path, "rb") as config:
            context.unrestrictedTraverse("@@faceted_exportimport").import_xml(
                import_file=config
            )


def _publish(obj):
    if api.content.get_state(obj) != "published":
        api.content.transition(obj, transition="publish")


def disable_site_actions_viewlet(context):
    """Disable the plone.site_actions viewlet"""
    storage = getUtility(IViewletSettingsStorage)
    skinname = context.getCurrentSkinName()
    manager = "plone.portalheader"
    viewlet_id = "plone.site_actions"
    hidden = list(storage.getHidden(manager, skinname))
    if viewlet_id not in hidden:
        hidden.append(viewlet_id)
        storage.setHidden(manager, skinname, tuple(hidden))
