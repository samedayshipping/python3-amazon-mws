from mws.parsers.base import first_element, BaseElementWrapper, BaseResponseMixin
from mws._mws import InboundShipments


namespaces = {
    'a': 'http://mws.amazonaws.com/FulfillmentInboundShipment/2010-10-01/'
}


class Member(BaseElementWrapper):

    def __init__(self, element):
        BaseElementWrapper.__init__(self, element)

    @property
    @first_element
    def quantity_shipped(self):
        return self.element.xpath('./a:QuantityShipped/text()', namespaces=namespaces)

    @property
    @first_element
    def shipment_id(self):
        return self.element.xpath('./a:ShipmentId/text()', namespaces=namespaces)

    @property
    @first_element
    def fulfillment_network_sku(self):
        return self.element.xpath('./a:FulfillmentNetworkSKU/text()', namespaces=namespaces)

    @property
    def asin(self):
        return self.fulfillment_network_sku

    @property
    @first_element
    def seller_sku(self):
        return self.element.xpath('./a:SellerSKU/text()', namespaces=namespaces)

    @property
    @first_element
    def quantity_received(self):
        return self.element.xpath('./a:QuantityReceived/text()', namespaces=namespaces)

    @property
    @first_element
    def quantity_in_case(self):
        return self.element.xpath('./a:QuantityInCase/text()', namespaces=namespaces)


class ListInboundShipmentItemsResponse(BaseElementWrapper, BaseResponseMixin):

    @property
    def shipment_items(self):
        return [Member(x) for x in self.element.xpath('//a:member', namespaces=namespaces)]

    @property
    @first_element
    def next_token(self):
        return self.element.xpath('//a:NextToken/text()', namespaces=namespaces)

    @classmethod
    def from_next_token(cls, mws_access_key, mws_secret_key, mws_account_id, next_token, mws_auth_token=None):
        api = InboundShipments(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.list_inbound_shipment_items_by_next_token(next_token)
        return cls.load(response.original)

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id, shipment_id,
                mws_auth_token=None, last_updated_after=None, last_updated_before=None):
        api = InboundShipments(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.list_inbound_shipment_items(shipment_id, last_updated_after, last_updated_before)
        return cls.load(response.original)
