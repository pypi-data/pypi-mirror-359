# -*- coding: utf-8 -*-

from plone import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from collective.sendinblue import _


class ICollectiveSendinblueLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class INewsletterSubscribe(Interface):

    email = schema.Email(
        title=_("Email address"),
        description=_("help_email", default="Please enter your email address."),
        required=True,
    )

    captcha = schema.TextLine(title="Captcha", description="", required=False)


class INewsletterRedirectionSubscribe(Interface):

    email = schema.Email(
        title=_("Email address"),
        description=_("help_email", default="Please enter your email address."),
        required=True,
    )


class ISendinblueAPI(Interface):
    """Sendinblue API"""

    def lists(self):
        """Retrieves lists (cached)"""

    def subscribe(self, account_id, list_id, email_address):
        """API call to create a contact and subscribe it to a list"""

    def accounts(self):
        """Retrieves accounts details (cached)"""

    def updateCache(self):
        """
        Update cache of data from the sendinblue server. First reset
        our sendinblue object, as the user may have picked a
        different api key. Alternatively, compare
        self.settings.api_keys and self.sendinblue.api_keys.
        """


class ISendinblueSettings(Interface):
    """
    Global sendinblue settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    api_keys = schema.List(
        title=_("Sendinblue API Key(s)"),
        description=_(
            "help_api_keys",
            default="Enter in your Sendinblue key here. If you have several"
            + " Sendinblue accounts, you can enter one key per line."
            + " Log into https://account.sendinblue.com/advanced/api"
            + " and copy the API Key to this field.",
        ),
        value_type=schema.TextLine(title=_("API Key")),
        default=[],
        required=True,
    )

    double_opt_in = schema.Bool(title=_("Double opt-in"), required=False, default=False)

    template_id = schema.Int(
        title=_("Template ID"),
        description=_("Double opt-in only"),
        required=False,
    )

    redirection_url = schema.URI(
        title=_("Redirection URL"),
        description=_("Double opt-in only"),
        required=False,
    )
