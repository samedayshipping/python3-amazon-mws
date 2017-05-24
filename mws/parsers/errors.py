import re
from .base import first_element, BaseResponseMixin, BaseElementWrapper
from lxml import etree


class ErrorResponse(ValueError, BaseElementWrapper, BaseResponseMixin):

    def __init__(self, element, mws_access_key=None, mws_secret_key=None, mws_account_id=None, mws_auth_token=None):
        BaseElementWrapper.__init__(self, element)
        ValueError.__init__(self, self.message)

    @property
    @first_element
    def type(self):
        return self.element.xpath('//ErrorResponse/Error/Type/text()')

    @property
    @first_element
    def code(self):
        return self.element.xpath('//ErrorResponse/Error/Code/text()')

    @property
    @first_element
    def message(self):
        return self.element.xpath('//ErrorResponse/Error/Message/text()')

    @property
    @first_element
    def request_id(self):
        return self.element.xpath('//ErrorResponse/RequestID/text()')

    @classmethod
    def load(cls, xml_string, mws_access_key=None, mws_secret_key=None, mws_account_id=None, mws_auth_token=None):
        """
        Create an instance of this class using an xml string.

        overridden so that we can remove any namespace from the response.
        :param xml_string:
        :return:
        """
        ptn = '\s+xmlns=\".*?\"'
        xml_string = re.sub(ptn, '', xml_string)
        tree = etree.fromstring(xml_string)
        return cls(tree)


class ProductError(ValueError, BaseElementWrapper):
    """
    Error wrapper for any error returned back for any call to the Products api.
    """
    namespaces = {
        'a': 'http://mws.amazonservices.com/schema/Products/2011-10-01',
        'b': 'http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd'
    }

    def __init__(self, element, identifier, mws_access_key=None, mws_secret_key=None, mws_account_id=None, mws_auth_token=None):
        BaseElementWrapper.__init__(self, element)
        ValueError.__init__(self, self.message)
        self.identifier = identifier

    @property
    @first_element
    def message(self):
        return self.element.xpath('./a:Message/text()', namespaces=self.namespaces)

    @property
    @first_element
    def code(self):
        return self.element.xpath('./a:Code/text()', namespaces=self.namespaces)

    @property
    @first_element
    def type(self):
        return self.element.xpath('./a:Type/text()', namespaces=self.namespaces)
