import datetime

from mws.parsers.base import BaseResponseMixin, BaseElementWrapper, first_element
from mws import Orders

namespaces = {
    'a': 'https://mws.amazonservices.com/Orders/2013-09-01'
}


class OrderItem(BaseElementWrapper):

    @property
    @first_element
    def quantity_ordered(self):
        return self.element.xpath('./a:QuantityOrdered/text()', namespaces=namespaces)

    @property
    @first_element
    def title(self):
        return self.element.xpath('./a:Title/text()', namespaces=namespaces)

    @property
    @first_element
    def promotion_discount(self):
        return self.element.xpath('./a:PromotionDiscount/a:Amount/text()', namespaces=namespaces)

    @property
    @first_element
    def currency_code(self):
        return self.element.xpath('./a:PromotionDiscount/a:CurrencyCode/text()', namespaces=namespaces)

    @property
    @first_element
    def asin(self):
        return self.element.xpath('./a:ASIN/text()', namespaces=namespaces)

    @property
    @first_element
    def seller_sku(self):
        return self.element.xpath('./a:SellerSKU/text()', namespaces=namespaces)

    @property
    @first_element
    def order_item_id(self):
        return self.element.xpath('./a:OrderItemId/text()', namespaces=namespaces)

    @property
    @first_element
    def quantity_shipped(self):
        return self.element.xpath('./a:QuantityShipped/text()', namespaces=namespaces)

    @property
    @first_element
    def item_price(self):
        return self.element.xpath('./a:ItemPrice/a:Amount/text()', namespaces=namespaces)

    @property
    @first_element
    def item_tax(self):
        return self.element.xpath('./a:ItemTax/a:Amount/text()', namespaces=namespaces)


class ListOrderItemsResponse(BaseElementWrapper, BaseResponseMixin):

    @property
    @first_element
    def next_token(self):
        return self.element.xpath('//a:NextToken/text()', namespaces=namespaces)

    @property
    @first_element
    def amazon_order_id(self):
        return self.element.xpath('//a:AmazonOrderId/text()', namespaces=namespaces)

    @property
    def order_items(self):
        return [OrderItem(x) for x in self.element.xpath('//a:OrderItem', namespaces=namespaces)]

    @classmethod
    def from_next_token(cls, mws_access_key, mws_secret_key, mws_account_id, next_token, mws_auth_token=None):
        api = Orders(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.list_order_items_by_next_token(next_token)
        return cls.load(response.original)

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id, amazon_order_id,
                mws_auth_token=None):
        api = Orders(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.list_order_items(amazon_order_id)
        return cls.load(response.original)
