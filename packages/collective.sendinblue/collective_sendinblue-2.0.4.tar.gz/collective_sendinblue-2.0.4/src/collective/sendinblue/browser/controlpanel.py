# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.registry.browser import controlpanel
from plone.protect.interfaces import IDisableCSRFProtection
from sib_api_v3_sdk.rest import ApiException
from zope.component import getUtility
from zope.interface import alsoProvides
import logging

from collective.sendinblue import _
from collective.sendinblue.interfaces import ISendinblueAPI
from collective.sendinblue.interfaces import ISendinblueSettings

logger = logging.getLogger("collective.sendinblue")


class SendinblueSettingsEditForm(controlpanel.RegistryEditForm):

    schema = ISendinblueSettings
    label = _("Sendinblue settings")
    description = _("Sendinblue integration for Plone")

    def update(self):
        self.updateCache()
        super(SendinblueSettingsEditForm, self).update()

    def updateCache(self):
        sendinblue = getUtility(ISendinblueAPI)
        sendinblue.updateCache()


class SendinblueSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SendinblueSettingsEditForm
    index = ViewPageTemplateFile("controlpanel.pt")

    def sendinblue_accounts(self):
        if IDisableCSRFProtection is not None:
            alsoProvides(self.request, IDisableCSRFProtection)
        sendinblue = getUtility(ISendinblueAPI)
        try:
            return sendinblue.accounts()
        except ApiException as error:
            logger.error(
                "Could not fetch account(s) details from " + "Sendinblue : %s" % error
            )

    def sendinblue_lists(self):
        if IDisableCSRFProtection is not None:
            alsoProvides(self.request, IDisableCSRFProtection)
        sendinblue = getUtility(ISendinblueAPI)
        try:
            return sendinblue.lists()
        except ApiException as error:
            logger.error(
                "Could not fetch lists details from " + "Sendinblue : %s" % error
            )
