import logging

from lxml import etree


def first_element_or_none(element_list):
    """
    Return the first element or None from an lxml selector result.
    :param element_list: lxml selector result
    :return:
    """
    if element_list:
        return element_list[0]
    return


def first_element(f):
    """
    function wrapper for _first_element_or_none.

    This is equivalent to using `return _first_element_or_none(xpath())`.
    :param f:
    :return:
    """
    def inner(*args, **kwargs):
        return first_element_or_none(f(*args, **kwargs))
    return inner


def parse_bool(f):

    def inner(*args, **kwargs):
        return f(*args, **kwargs) == 'true'
    return inner


class BaseElementWrapper(object):

    def __init__(self, element, mws_access_key=None, mws_secret_key=None, mws_account_id=None, mws_auth_token=None):
        """

        :param element: Etree object of response body
        """
        self.element = element
        self.logger = logging.getLogger(self.__class__.__name__)

    def __str__(self):
        return etree.tostring(self.element)


class BaseResponseMixin(object):

    @classmethod
    def load_from_file(cls, file_location, mws_access_key=None, mws_secret_key=None, mws_account_id=None, mws_auth_token=None):
        """
        Create an instance of this class from a file.

        :param file_location: path to file.
        :return:
        """
        with open(file_location, 'rb') as f:
            return cls.load(f.read(), mws_access_key, mws_secret_key, mws_account_id, mws_auth_token)

    @classmethod
    def load(cls, xml_string, mws_access_key=None, mws_secret_key=None, mws_account_id=None, mws_auth_token=None):
        """
        Create an instance of this class using an xml string.

        :param xml_string:
        :return:
        """
        tree = etree.fromstring(xml_string)
        return cls(tree, mws_access_key, mws_secret_key, mws_account_id, mws_auth_token)
