# -*- coding: utf-8 -*-
from collective.sendinblue.interfaces import ISendinblueSettings
from plone.portlets.interfaces import IPortletType
from plone.registry.interfaces import IRegistry
from zope.component import getSiteManager
from zope.component import getUtility

import logging

logger = logging.getLogger(__name__)


def uninstall(context):
    """Uninstall script"""
    remove_registry_records()
    remove_portlets()


def remove_registry_records():
    registry = getUtility(IRegistry)
    keys_to_remove = [
        "collective.sendinblue.cache.lists",
        "collective.sendinblue.cache.accounts",
    ]

    for key in keys_to_remove:
        if key in registry.records:
            del registry.records[key]
            logger.info(f"Deleted registry record: {key}")
        else:
            logger.info(f"Registry key not found, skipping: {key}")

    registry = getUtility(IRegistry)
    prefix = (
        ISendinblueSettings.__identifier__
    )
    for name in ISendinblueSettings.names():
        key = f"{prefix}.{name}"
        if key in registry:
            del registry.records[key]
            logger.info(f"Deleted registry record: {key}")
        else:
            logger.info(f"Registry key not found, skipping: {key}")


def remove_portlets():
    portlet_ids_to_remove = [
        "portlet.Sendinblue",
        "portlet.RedirectionSendinblue",
    ]
    sm = getSiteManager()
    for portlet_id in portlet_ids_to_remove:
        try:
            sm.unregisterUtility(provided=IPortletType, name=portlet_id)
            logger.info(f"Unregistered portlet: {portlet_id}")
        except Exception as e:
            logger.warning(f"Could not unregister {portlet_id}: {e}")
