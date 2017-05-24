from mws import InboundShipments
from mws.parsers.base import BaseResponseMixin, BaseElementWrapper, first_element

namespaces = {
    'a': 'http://mws.amazonaws.com/FulfillmentInboundShipment/2010-10-01/'
}


class Member(BaseElementWrapper):

    def __init__(self, element):
        BaseElementWrapper.__init__(self, element)

    @property
    @first_element
    def destination_fulfillment_center_id(self):
        return self.element.xpath('./a:DestinationFulfillmentCenterId/text()', namespaces=namespaces)

    @property
    @first_element
    def label_prep_type(self):
        return self.element.xpath('./a:LabelPrepType/text()', namespaces=namespaces)

    @property
    @first_element
    def shipment_id(self):
        return self.element.xpath('./a:ShipmentId/text()', namespaces=namespaces)

    @property
    @first_element
    def are_cases_required(self):
        return self.element.xpath('./a:AreCasesRequired/text()', namespaces=namespaces)

    @property
    @first_element
    def shipment_name(self):
        return self.element.xpath('./a:ShipmentName/text()', namespaces=namespaces)

    @property
    @first_element
    def shipment_status(self):
        return self.element.xpath('./a:ShipmentStatus/text()', namespaces=namespaces)


class ListInboundShipmentResponse(BaseElementWrapper, BaseResponseMixin):

    @property
    @first_element
    def next_token(self):
        return self.element.xpath('//a:NextToken/text()', namespaces=namespaces)

    @property
    def shipment_data(self):
        return [Member(x) for x in self.element.xpath('//a:member', namespaces=namespaces)]

    @classmethod
    def from_next_token(cls, mws_access_key, mws_secret_key, mws_account_id, next_token, mws_auth_token=None):
        api = InboundShipments(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.list_inbound_shipments_by_next_token(next_token)
        return cls.load(response.original)

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id,
                mws_auth_token=None, shipment_status_list=(), shipment_id_list=(),
                last_updated_after=None, last_updated_before=None):
        api = InboundShipments(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.list_inbound_shipments(shipment_status_list, shipment_id_list, last_updated_after, last_updated_before)
        return cls.load(response.original)
