from mws.parsers.base import first_element, BaseElementWrapper, BaseResponseMixin
from mws._mws import InboundShipments
from mws.parsers.errors import ErrorResponse


namespaces = {
    'a': 'http://mws.amazonaws.com/FulfillmentInboundShipment/2010-10-01/'
}


class ASINPrepInstructions(BaseElementWrapper):

    @property
    @first_element
    def asin(self):
        return self.element.xpath('./a:ASIN/text()', namespaces=namespaces)

    @property
    @first_element
    def barcode_instruction(self):
        return self.element.xpath('./a:BarcodeInstruction/text()', namespaces=namespaces)

    @property
    @first_element
    def prep_guidance(self):
        return self.element.xpath('./a:PrepGuidance/text()', namespaces=namespaces)

    @property
    def prep_instruction_list(self):
        l = []
        for elem in self.element.xpath('.//a:PrepInstructionList/a:PrepInstruction/text()', namespaces=namespaces):
            l.append(elem)
        return l


class InvalidASIN(BaseElementWrapper):

    @property
    @first_element
    def asin(self):
        return self.element.xpath('./a:ASIN/text()', namespaces=namespaces)

    @property
    @first_element
    def error_reason(self):
        return self.element.xpath('./a:ErrorReason/text()', namespaces=namespaces)


class GetPrepInstructionsForASINResponse(BaseElementWrapper, BaseResponseMixin):

    def asin_prep_instructions_list(self):
        return [ASINPrepInstructions(x) for x in self.element.xpath('//a:ASINPrepInstructions', namespaces=namespaces)]

    def invalid_asin_list(self):
        return [InvalidASIN(x) for x in self.element.xpath('//a:InvalidASIN', namespaces=namespaces)]

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id,
                asin_list, ship_to_country_code, mws_auth_token=None):
        api = InboundShipments(access_key=mws_access_key, secret_key=mws_secret_key, account_id=mws_account_id,
                               auth_token=mws_auth_token)
        response = api.get_prep_instructions_for_asin(asin_list, ship_to_country_code)
        err = ErrorResponse.load(response.original)
        if err.message:
            raise err
        return cls.load(response.original, mws_access_key, mws_secret_key, mws_account_id, mws_auth_token)
