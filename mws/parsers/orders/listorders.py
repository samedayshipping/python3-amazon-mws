import re

from dateutil import parser

from mws.parsers.base import BaseResponseMixin, BaseElementWrapper, first_element
from mws import Orders

namespaces = {
    'a': 'https://mws.amazonservices.com/Orders/2013-09-01'
}


def mk_ship_state(state_value):
    """
    Converts customer supplied state to the uniform state abbreviation
    :param state_value: customer supplied state
    :return: uppercase state abbreviation
    """
    # When order is cancelled, not all the data is in the report, so we account for null states here
    if not state_value:
        return
    states = {"AL": "Alabama",
              "AK": "Alaska",
              "AZ": "Arizona",
              "AR": "Arkansas",
              "CA": "California",
              "CO": "Colorado",
              "CT": "Connecticut",
              "DE": "Delaware",
              "DC": "District of Columbia",
              "FL": "Florida",
              "GA": "Georgia",
              "HI": 'Hawaii',
              "ID": "Idaho",
              "IL": "Illinois",
              "IN": "Indiana",
              "IA": "Iowa",
              "KS": "Kansas",
              "KY": "Kentucky",
              "LA": "Louisiana",
              "ME": "Maine",
              "MD": "Maryland",
              "MA": "Massachusetts",
              "MI": "Michigan",
              "MN": "Minnesota",
              "MS": "Mississippi",
              "MO": "Missouri",
              "MT": "Montana",
              "NE": "Nebraska",
              "NV": "Nevada",
              "NH": "New Hampshire",
              "NJ": "New Jersey",
              "NM": "New Mexico",
              "NY": "New York",
              "NC": "North Carolina",
              "ND": "North Dakota",
              "OH": "Ohio",
              "OK": "Oklahoma",
              "OR": "Oregon",
              "PA": "Pennsylvania",
              "RI": "Rhode Island",
              "SC": "South Carolina",
              "SD": "South Dakota",
              "TN": "Tennessee",
              "TX": "Texas",
              "UT": "Utah",
              "VT": "Vermont",
              "VA": "Virginia",
              "WA": "Washington",
              "WV": "West Virginia",
              "WI": "Wisconsin",
              "WY": "Wyoming"}
    states = {re.sub('\W', '', k).lower(): re.sub('\W', '', v).lower() for k, v in states.items()}
    inverted_states = {v: k for k, v in states.items()}
    sv = re.sub('\W', '', state_value).lower()

    if sv in states:
        return sv.upper()
    elif sv in inverted_states:
        return inverted_states[sv].upper()
    else:
        return state_value


class Order(BaseElementWrapper):

    @property
    @first_element
    def _latest_ship_date(self):
        return self.element.xpath('./a:LatestShipDate/text()', namespaces=namespaces)

    @property
    def latest_ship_date(self):
        if self._latest_ship_date:
            return parser.parse(self._latest_ship_date)
        return

    @property
    @first_element
    def order_type(self):
        return self.element.xpath('./a:OrderType/text()', namespaces=namespaces)

    @property
    @first_element
    def _purchase_date(self):
        return self.element.xpath('./a:PurchaseDate/text()', namespaces=namespaces)

    @property
    def purchase_date(self):
        if self._purchase_date:
            return parser.parse(self._purchase_date)
        return

    @property
    @first_element
    def buyer_email(self):
        return self.element.xpath('./a:BuyerEmail/text()', namespaces=namespaces)

    @property
    @first_element
    def amazon_order_id(self):
        return self.element.xpath('./a:AmazonOrderId/text()', namespaces=namespaces)

    @property
    @first_element
    def _last_update_date(self):
        return self.element.xpath('./a:LastUpdateDate/text()', namespaces=namespaces)

    @property
    def last_update_date(self):
        if self._last_update_date:
            return parser.parse(self._last_update_date)
        return

    @property
    @first_element
    def number_of_items_shipped(self):
        return self.element.xpath('./a:NumberOfItemsShipped/text()', namespaces=namespaces)

    @property
    @first_element
    def ship_service_level(self):
        return self.element.xpath('./a:ShipServiceLevel/text()', namespaces=namespaces)

    @property
    @first_element
    def order_status(self):
        return self.element.xpath('./a:OrderStatus/text()', namespaces=namespaces)

    @property
    @first_element
    def sales_channel(self):
        return self.element.xpath('./a:SalesChannel/text()', namespaces=namespaces)

    @property
    @first_element
    def _is_business_order(self):
        return self.element.xpath('./a:IsBusinessOrder/text()', namespaces=namespaces)

    @property
    def is_business_order(self):
        return self._is_business_order == 'true'

    @property
    @first_element
    def number_of_items_unshipped(self):
        return self.element.xpath('./a:NumberOfItemsUnshipped/text()', namespaces=namespaces)

    @property
    @first_element
    def buyer_name(self):
        return self.element.xpath('./a:BuyerName/text()', namespaces=namespaces)

    @property
    @first_element
    def currency_code(self):
        return self.element.xpath('./a:OrderTotal/a:CurrencyCode/text()', namespaces=namespaces)

    @property
    @first_element
    def order_total(self):
        return self.element.xpath('./a:OrderTotal/a:Amount/text()', namespaces=namespaces)

    @property
    @first_element
    def _is_premium_order(self):
        return self.element.xpath('./a:IsPremiumOrder/text()', namespaces=namespaces)

    @property
    def is_premium_order(self):
        return self._is_premium_order == 'true'

    @property
    @first_element
    def _earliest_ship_date(self):
        return self.element.xpath('./a:EarliestShipDate/text()', namespaces=namespaces)

    @property
    def earliest_ship_date(self):
        if self._earliest_ship_date:
            return parser.parse(self._earliest_ship_date)
        return

    @property
    @first_element
    def marketplace_id(self):
        return self.element.xpath('./a:MarketplaceId/text()', namespaces=namespaces)

    @property
    @first_element
    def fulfillment_channel(self):
        return self.element.xpath('./a:FulfillmentChannel/text()', namespaces=namespaces)

    @property
    @first_element
    def payment_method(self):
        return self.element.xpath('./a:PaymentMethod/text()', namespaces=namespaces)

    @property
    @first_element
    def _is_prime(self):
        return self.element.xpath('./a:IsPrime/text()', namespaces=namespaces)

    @property
    def is_prime(self):
        return self._is_prime == 'true'

    @property
    @first_element
    def shipment_service_level_category(self):
        return self.element.xpath('./a:ShipmentServiceLevelCategory/text()', namespaces=namespaces)

    @property
    @first_element
    def seller_order_id(self):
        return self.element.xpath('./a:SellerOrderId/text()', namespaces=namespaces)

    # Address Stuff

    @property
    @first_element
    def state_or_region(self):
        return self.element.xpath('./a:ShippingAddress/a:StateOrRegion/text()', namespaces=namespaces)

    @property
    def ship_state_abbreviation(self):
        """
        Convert the value in state_or_region to a state abbreviation. (ex. Massachusets -> MA)
        :return:
        """
        if self.state_or_region:
            return mk_ship_state(self.state_or_region)
        return

    @property
    @first_element
    def city(self):
        return self.element.xpath('./a:ShippingAddress/a:City/text()', namespaces=namespaces)

    @property
    @first_element
    def phone(self):
        return self.element.xpath('./a:ShippingAddress/a:Phone/text()', namespaces=namespaces)

    @property
    @first_element
    def country_code(self):
        return self.element.xpath('./a:ShippingAddress/a:CountryCode/text()', namespaces=namespaces)

    @property
    @first_element
    def postal_code(self):
        return self.element.xpath('./a:ShippingAddress/a:PostalCode/text()', namespaces=namespaces)

    @property
    @first_element
    def name(self):
        return self.element.xpath('./a:ShippingAddress/a:Name/text()', namespaces=namespaces)

    @property
    @first_element
    def address_line_1(self):
        return self.element.xpath('./a:ShippingAddress/a:AddressLine1/text()', namespaces=namespaces)

    @property
    @first_element
    def address_line_2(self):
        return self.element.xpath('./a:ShippingAddress/a:AddressLine2/text()', namespaces=namespaces)


class ListOrdersResponse(BaseElementWrapper, BaseResponseMixin):

    @property
    @first_element
    def next_token(self):
        return self.element.xpath('//a:NextToken/text()', namespaces=namespaces)

    @property
    def orders(self):
        return [Order(x) for x in self.element.xpath('//a:Order', namespaces=namespaces)]

    @classmethod
    def from_next_token(cls, mws_access_key, mws_secret_key, mws_account_id, next_token, mws_auth_token=None):
        api = Orders(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.list_orders_by_next_token(next_token)
        return cls.load(response.original)

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id, marketplace_ids,
                created_after=None, created_before=None, lastupdatedafter=None,
                lastupdatedbefore=None, orderstatus=(), fulfillment_channels=(),
                payment_methods=(), buyer_email=None, seller_orderid=None, max_results=None,
                mws_auth_token=None):
        api = Orders(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.list_orders(marketplace_ids, created_after, created_before, lastupdatedafter, lastupdatedbefore, orderstatus, fulfillment_channels, payment_methods, buyer_email, seller_orderid, max_results)
        return cls.load(response.original)
