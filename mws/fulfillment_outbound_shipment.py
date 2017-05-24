import datetime
from ._mws import MWS


def remove_empty(d):
    """
    Remove elements from a dictionary where the value is falsey.

    :param d: The dict to remove falsey elements from.
    :return: Dict with no falsey values.
    """
    return {k: v for k, v in d.items() if v}


def raise_for_length(val, prop, max_l=0, min_l=0):
    """
    Raise a value error if the length of the `val` param exceeds the `ml` param.

    :param val: The value who's length to check.
    :param prop: The property name to display in the error message.
    :param max_l: The maximum length.
    :param min_l: The minimum length.
    :return:
    """
    if len(val) < min_l:
        raise ValueError('Length of `{}` cannot be less than {}'.format(prop, min_l))
    if len(val) > max_l:
        raise ValueError('Length of `{}` cannot exceed {}'.format(prop, max_l))


def to_iso_8601_format(dt):
    """
    Convert the supplied datetime instance to the ISO 8601 format as per API specs.

    :param dt: The datetime instance to convert.
    :return: Supplied datetime as timestamp in ISO 8601 format.
    """
    if not dt:
        return
    if isinstance(dt, str):
        return dt
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def from_iso_8601_format(dt_str):
    """
    Convert the supplied iso 8601 timestamp into a datetime instance.

    :param dt_str: A timestamp in iso 8601 format.
    :return:
    """
    if not dt_str:
        return
    return datetime.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%SZ')


class DictParam(dict):

    def __init__(self, **kwargs):
        super(DictParam, self).__init__(**kwargs)

    @classmethod
    def load(cls, d):
        raise NotImplementedError('`load` is not implemented for class `{}`'.format(cls.__name__))

    def flattened(self):
        """
        Return all nested elements in a flattened dict to be able to easily convert to url params.

        Flatten all elements which have a flatten attribute. If the element is a list, we enumerate the
        params and create a prefix based on the list index.
        :return:
        """

        def _flatten(k_, v_):
            """
            Flatten the object if possible, else just add the object to the dict.

            :param k_:
            :param v_:
            :return:
            """
            d_ = {}

            # Check if v can be flattened.
            if hasattr(v_, 'flattened'):
                for kf, vf in v_.flattened().items():
                    # Dont add any elements with a falsey value.
                    if not vf:
                        continue
                    # Generate the key so that it matches API specs for the encoded URL params.
                    # (ex. DeliveryWindow.EndDateTime)
                    kf = '{}.{}'.format(k_, kf)
                    d_[kf] = str(vf)
            else:
                # Set original value since nothing needs to be flattened.
                d_[k_] = str(v_)
            return d_

        d = {}
        for k, v in self.items():
            # Dont add any elements with a falsey value.
            if not v:
                continue

            # If v is a list, enumerate the params so that we can match the format for a list in url params
            # (ex. Items.member.1.PerUnitDeclaredValue.CurrencyCode)
            if type(v) is list:
                for i, e in enumerate(v):
                    i += 1
                    pfx = '{}.member.{}'.format(k, i)
                    d.update(_flatten(pfx, e))
            else:
                d.update(_flatten(k, v))
        return d


class Currency(DictParam):
    """
    Wrapper for Currency elements.
    """

    def __init__(self, value=0.0, currency_code='USD', **kwargs):
        """
        Currency type and amount.

        http://docs.developer.amazonservices.com/en_US/fba_outbound/FBAOutbound_Datatypes.html#Currency.

        :param value: The currency amount.
        :param currency_code: three-digit currency code. (ISO 4217 format)
        """
        super(DictParam, self).__init__(**kwargs)
        self.value = value
        self.currency_code = currency_code

    @property
    def currency_code(self):
        """
        Three-digit currency code.

        :return:
        """
        return self.get('CurrencyCode')

    @currency_code.setter
    def currency_code(self, val):
        self['CurrencyCode'] = val

    @property
    def value(self):
        """
        The currency amount.

        :return:
        """
        return self.get('Value')

    @value.setter
    def value(self, val):
        self['Value'] = val

    @classmethod
    def load(cls, d):
        if isinstance(d, dict):
            return cls(value=d.get('Value'), currency_code=d.get('CurrencyCode'))
        elif not d:
            return cls()
        return cls.as_currency(d)

    @staticmethod
    def as_currency(val):
        """
        Convert the supplied value to a Currency instance.

        If the supplied value is an instance of currency, then return the value. Other wise create a currency instance
        from the value converted to a float.
        :param val:
        :return:
        """
        if isinstance(val, Currency):
            return val
        return Currency(value=float(val))

    def __nonzero__(self):
        return bool(self.value)


class CODSettings(DictParam):
    """
    Wrapper for COD Settings elements.
    """

    def __init__(self, is_cod_required=False, cod_charge=0, cod_charge_tax=0,
                 shipping_charge=0, shipping_charge_tax=0):
        """
        The COD (Cash On Delivery) charges for a COD order.

        http://docs.developer.amazonservices.com/en_US/fba_outbound/FBAOutbound_Datatypes.html#CODSettings.

        :param is_cod_required: Indicates whether this fulfillment order requires COD (Cash On Delivery) payment.
        :param cod_charge: The amount of the COD charge to be collected form the customer for a COD order.
        :param cod_charge_tax: The amount of the tax on the COD charge to be collected from the customer for a COD order.
        :param shipping_charge: The amount of the shipping charge to be collected from the customer for a COD order.
        :param shipping_charge_tax: The amount of the tax on the shipping charge to be collected from the customer for a COD order.
        """
        super(DictParam, self).__init__()
        self.is_cod_required = is_cod_required
        self.cod_charge = cod_charge
        self.cod_charge_tax = cod_charge_tax
        self.shipping_charge = shipping_charge
        self.shipping_charge_tax = shipping_charge_tax

    @property
    def is_cod_required(self):
        """
        Indicates whether this fulfillment order requires COD (Cash On Delivery) payment.

        :return:
        """
        return self.get('IsCODRequired')

    @is_cod_required.setter
    def is_cod_required(self, val):
        self['IsCODRequired'] = val

    @property
    def cod_charge(self):
        """
        The amount of the COD charge to be collected from the customer for a COD order.

        :return:
        """
        return Currency.load(self.get('CODCharge'))

    @cod_charge.setter
    def cod_charge(self, val):
        self['CODCharge'] = Currency.load(val)

    @property
    def cod_charge_tax(self):
        """
        The amount of the tax on the COD charge to be collected from the customer for a COD order.

        :return:
        """
        return Currency.load(self.get('CODChargeTax'))

    @cod_charge_tax.setter
    def cod_charge_tax(self, val):
        self['CODChargeTax'] = Currency.load(val)

    @property
    def shipping_charge(self):
        """
        The amount of the shipping charge to be collected from the customer for a COD order.

        :return:
        """
        return Currency.load(self.get('ShippingCharge'))

    @shipping_charge.setter
    def shipping_charge(self, val):
        self['ShippingCharge'] = Currency.load(val)

    @property
    def shipping_charge_tax(self):
        """
        The amount of the tax on the shipping charge to be collected from the customer for a COD order.

        :return:
        """
        return Currency.load(self.get('ShippingChargeTax'))

    @shipping_charge_tax.setter
    def shipping_charge_tax(self, val):
        self['ShippingChargeTax'] = Currency.load(val)

    @classmethod
    def load(cls, d):
        if isinstance(d, dict):
            return cls(is_cod_required=d.get('IsCODRequired'), cod_charge=d.get('CODCharge'),
                       cod_charge_tax=d.get('CODChargeTax'), shipping_charge=d.get('ShippingCharge'),
                       shipping_charge_tax=d.get('ShippingChargeTax'))
        return cls()

    def __nonzero__(self):
        return self.is_cod_required


class DeliveryWindow(DictParam):
    """
    Wrapper for DeliveryWindow element.
    """

    def __init__(self, start_date_time=None, end_date_time=None):
        """
        Specifies the time range within which your Scheduled Delivery fulfillment order should be delivered.

        http://docs.developer.amazonservices.com/en_US/fba_outbound/FBAOutbound_Datatypes.html#DeliveryWindow.

        :param start_date_time: The date and time of the start of the Scheduled Delivery window.
        :param end_date_time: The date and time of the end of the Scheduled Delivery window.
        """
        super(DictParam, self).__init__()
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time

    @property
    def start_date_time(self):
        """
        The date and time of the start of the Scheduled Delivery window.

        :return:
        """
        return from_iso_8601_format(self.get('StartDateTime'))

    @start_date_time.setter
    def start_date_time(self, val):
        self['StartDateTime'] = to_iso_8601_format(val)

    @property
    def end_date_time(self):
        """
        The date and time of the end of the Scheduled Delivery window.

        :return:
        """
        return from_iso_8601_format(self.get('EndDateTime'))

    @end_date_time.setter
    def end_date_time(self, val):
        self['EndDateTime'] = to_iso_8601_format(val)

    @classmethod
    def load(cls, d):
        if isinstance(d, dict):
            return cls(start_date_time=d.get('StartDateTime'), end_date_time=d.get('EndDateTime'))
        return cls()

    def __nonzero__(self):
        return bool(self.end_date_time) and bool(self.start_date_time)


class Address(DictParam):
    """
    Wrapper for Address elements.
    """

    max_name_len = 50
    max_line_1_len = 60
    max_line_2_len = 60
    max_line_3_len = 60
    max_district_or_county_len = 150
    max_city_len = 50
    max_state_or_province_len = 150
    max_postal_code_len = 20
    max_phone_number_len = 20

    def __init__(self, name='', line_1='', line_2='', line_3='', district_or_county='', city='',
                 state_or_province_code='', country_code='', postal_code='', phone_number=''):
        """
        The destination address for the fulfillment order.

        http://docs.developer.amazonservices.com/en_US/fba_outbound/FBAOutbound_Datatypes.html#Address.

        """
        super(DictParam, self).__init__()
        self.name = name
        self.line_1 = line_1
        self.line_2 = line_2
        self.line_3 = line_3
        self.district_or_county = district_or_county
        self.city = city
        self.state_or_province_code = state_or_province_code
        self.country_code = country_code
        self.postal_code = postal_code
        self.phone_number = phone_number

    @property
    def name(self):
        """
        Recipient's name.

        :return:
        """
        return self.get('Name')

    @name.setter
    def name(self, val):
        raise_for_length(val, 'name', self.max_name_len)
        self['Name'] = val

    @property
    def line_1(self):
        """
        Recipient's street address information.

        :return:
        """
        return self.get('Line1')

    @line_1.setter
    def line_1(self, val):
        raise_for_length(val, 'line_1', self.max_line_1_len)
        self['Line1'] = val

    @property
    def line_2(self):
        """
        Additional street address information, if required.

        :return:
        """
        return self.get('Line2')

    @line_2.setter
    def line_2(self, val):
        raise_for_length(val, 'line_2', self.max_line_2_len)
        self['Line2'] = val

    @property
    def line_3(self):
        """
        Additional street address information, if required.

        :return:
        """
        return self.get('Line3')

    @line_3.setter
    def line_3(self, val):
        raise_for_length(val, 'line_3', self.max_line_3_len)
        self['Line3'] = val

    @property
    def district_or_county(self):
        """
        Recipient's district or county.

        :return:
        """
        return self.get('DistrictOrCounty')

    @district_or_county.setter
    def district_or_county(self, val):
        raise_for_length(val, 'district_or_county', self.max_district_or_county_len)
        self['DistrictOrCounty'] = val

    @property
    def city(self):
        """
        Recipient's district or county.

        :return:
        """
        return self.get('City')

    @city.setter
    def city(self, val):
        raise_for_length(val, 'city', self.max_city_len)
        self['City'] = val

    @property
    def state_or_province_code(self):
        """
        Recipient's state or province code.

        :return:
        """
        return self.get('StateOrProvinceCode')

    @state_or_province_code.setter
    def state_or_province_code(self, val):
        raise_for_length(val, 'state_or_province_code', self.max_state_or_province_len)
        self['StateOrProvinceCode'] = val

    @property
    def country_code(self):
        """
        Recipient's two-digit country code.

        :return:
        """
        return self.get('CountryCode')

    @country_code.setter
    def country_code(self, val):
        self['CountryCode'] = val

    @property
    def postal_code(self):
        """
        The postal code (required for shipments to the U.S.).

        :return:
        """
        return self.get('PostalCode')

    @postal_code.setter
    def postal_code(self, val):
        raise_for_length(val, 'postal_code', self.max_postal_code_len)
        self['PostalCode'] = val

    @property
    def phone_number(self):
        """
        Recipient's phone number.

        :return:
        """
        return self.get('PhoneNumber')

    @phone_number.setter
    def phone_number(self, val):
        raise_for_length(val, 'phone_number', self.max_phone_number_len)
        self['PhoneNumber'] = val

    @classmethod
    def load(cls, d):
        if isinstance(d, dict):
            return cls(name=d.get('Name'), line_1=d.get('Line1'), line_2=d.get('Line2'), line_3=d.get('Line3'),
                       district_or_county=d.get('DistrictOrCounty'), city=d.get('City'),
                       state_or_province_code=d.get('StateOrProvinceCode'), country_code=d.get('CountryCode'),
                       postal_code=d.get('PostalCode'), phone_number=d.get('PhoneNumber'))
        return cls()


class CreateFulfillmentOrderItem(DictParam):
    """
    Wrapper for CreateFulfillmentOrderItem element.
    """

    max_seller_sku_len = 50
    max_seller_fulfillment_order_item_id_len = 50
    max_gift_message_len = 512
    max_displayable_comment_len = 250

    def __init__(self, seller_sku='', seller_fulfillment_order_item_id='', quantity=0, gift_message='',
                 displayable_comment='', fulfillment_network_sku='', per_unit_declared_value=0.0,
                 per_unit_price=0.0, per_unit_tax=0.0):
        """
        http://docs.developer.amazonservices.com/en_US/fba_outbound/FBAOutbound_Datatypes.html#CreateFulfillmentOrderItem.
        """
        super(DictParam, self).__init__()
        self.seller_sku = seller_sku
        self.seller_fulfillment_order_item_id = seller_fulfillment_order_item_id
        self.quantity = quantity
        self.gift_message = gift_message
        self.displayable_comment = displayable_comment
        self.fulfillment_network_sku = fulfillment_network_sku
        self.per_unit_declared_value = per_unit_declared_value
        self.per_unit_price = per_unit_price
        self.per_unit_tax = per_unit_tax

    @property
    def seller_sku(self):
        """
        The Seller SKU of the item.

        :return:
        """
        return self.get('SellerSKU')

    @seller_sku.setter
    def seller_sku(self, val):
        raise_for_length(val, 'seller_sku', self.max_seller_sku_len)
        self['SellerSKU'] = val

    @property
    def seller_fulfillment_order_item_id(self):
        """
        A fulfillment order item identifier that you create to track your fulfillment order items.

        You can use this value to disambiguate multiple fulfillment items that have the same SellerSKU.
        For example, you might assign different SellerFulfillmentOrderItemId values to two items in a fulfillment order
            that share the same SellerSKU but have different GiftMessage values.
        :return:
        """
        return self.get('SellerFulfillmentOrderItemId')

    @seller_fulfillment_order_item_id.setter
    def seller_fulfillment_order_item_id(self, val):
        raise_for_length(val, 'seller_fulfillment_order_item_id', self.max_seller_fulfillment_order_item_id_len)
        self['SellerFulfillmentOrderItemId'] = val

    @property
    def quantity(self):
        """
        The item quantity.

        :return:
        """
        return self.get('Quantity')

    @quantity.setter
    def quantity(self, val):
        self['Quantity'] = val

    @property
    def gift_message(self):
        """
        A message to the gift recipient, if applicable.

        :return:
        """
        return self.get('GiftMessage')

    @gift_message.setter
    def gift_message(self, val):
        raise_for_length(val, 'gift_message', self.max_gift_message_len)
        self['GiftMessage'] = val

    @property
    def displayable_comment(self):
        """
        Item-specific text that displays in recipient-facing materials such as the outbound shipment packing slip.

        :return:
        """
        return self.get('DisplayableComment')

    @displayable_comment.setter
    def displayable_comment(self, val):
        raise_for_length(val, 'displayable_comment', self.max_displayable_comment_len)
        self['DisplayableComment'] = val

    @property
    def fulfillment_network_sku(self):
        """
        The Amazon Fulfillment Network SKU of the item.

        :return:
        """
        return self.get('FulfillmentNetworkSKU')

    @fulfillment_network_sku.setter
    def fulfillment_network_sku(self, val):
        self['FulfillmentNetworkSKU'] = val

    @property
    def per_unit_declared_value(self):
        """
        The monetary value assigned by the seller to this item.

        :return:
        """
        return Currency.load(self.get('PerUnitDeclaredValue'))

    @per_unit_declared_value.setter
    def per_unit_declared_value(self, val):
        self['PerUnitDeclaredValue'] = Currency.load(val)

    @property
    def per_unit_price(self):
        """
        The amount to be collected from the customer for this item in a COD (Cash On Delivery) order.

        :return:
        """
        return Currency.load(self.get('PerUnitPrice'))

    @per_unit_price.setter
    def per_unit_price(self, val):
        self['PerUnitPrice'] = Currency.load(val)

    @property
    def per_unit_tax(self):
        """
        The tax on the amount to be collected from the customer for this item in a COD (Cash On Delivery) order.

        :return:
        """
        return Currency.load(self.get('PerUnitTax'))

    @per_unit_tax.setter
    def per_unit_tax(self, val):
        self['PerUnitTax'] = Currency.load(val)

    @classmethod
    def load(cls, d):
        if isinstance(d, dict):
            return cls(seller_sku=d.get('SellerSKU'),
                       seller_fulfillment_order_item_id=d.get('SellerFulfillmentOrderItemId'),
                       quantity=d.get('Quantity'), gift_message=d.get('GiftMessage'),
                       displayable_comment=d.get('DisplayableComment'),
                       fulfillment_network_sku=d.get('FulfillmentNetworkSKU'),
                       per_unit_declared_value=d.get('PerUnitDeclaredValue'),
                       per_unit_price=d.get('PerUnitPrice'), per_unit_tax=d.get('PerUnitTax'))
        return cls()


class CreateFulfillmentOrder(DictParam, MWS):

    URI = '/FulfillmentOutboundShipment/2010-10-01/'
    VERSION = '2010-10-01'
    NS = "{http://mws.amazonaws.com/FulfillmentOutboundShipment/2010-10-01/}"

    valid_fulfillment_action_values = {
        'Ship',
        'Hold'
    }

    valid_shipping_speed_category_values = {
        'Standard',
        'Expedited',
        'Priority',
        'ScheduledDelivery'
    }

    valid_fulfillment_policy_values = {
        'FillOrKill',
        'FillAll',
        'FillAllAvailable'
    }

    max_sfoi_len = 40
    min_displayable_order_id_len = 1
    max_displayable_order_id_len = 40
    max_displayable_order_comment_len = 1000
    max_email_len = 60

    def __init__(self, access_key, secret_key, account_id, region='US', domain='', uri="", version="2010-10-01",
                 auth_token="", marketplace_id='ATVPDKIKX0DER', seller_fulfillment_order_id='',
                 fulfillment_action='Ship', displayable_order_id='1', displayable_order_date_time='',
                 displayable_order_comment='', shipping_speed_category='Standard', destination_address=None,
                 fulfillment_policy='FillOrKill', notification_email_list=(), cod_settings=None, items=(),
                 delivery_window=None):
        super(DictParam, self).__init__()
        MWS.__init__(self, access_key, secret_key, account_id, region, domain, uri, version, auth_token)
        self.marketplace_id = marketplace_id
        self.seller_fulfillment_order_id = seller_fulfillment_order_id
        self.fulfillment_action = fulfillment_action
        self.displayable_order_id = displayable_order_id
        self.displayable_order_date_time = displayable_order_date_time
        self.displayable_order_comment = displayable_order_comment
        self.shipping_speed_category = shipping_speed_category
        self.destination_address = destination_address
        self.fulfillment_policy = fulfillment_policy
        self.notification_email_list = notification_email_list
        self.cod_settings = cod_settings
        self.items_ = items
        self.delivery_window = delivery_window

    @property
    def marketplace_id(self):
        """
        The marketplace the order is placed against.

        :return:
        """
        return self.get('MarketplaceId')

    @marketplace_id.setter
    def marketplace_id(self, val):
        self['MarketplaceId'] = val

    @property
    def seller_fulfillment_order_id(self):
        """
        A fulfillment order identifier that you create to track your fulfillment order.

        The SellerFulfillmentOrderId must be unique for each fulfillment order that you create.
        If your system already creates unique order identifiers,
            then these might be good values to use for your SellerFulfillmentOrderId values.
        :return:
        """
        return self.get('SellerFulfillmentOrderId')

    @seller_fulfillment_order_id.setter
    def seller_fulfillment_order_id(self, val):
        self['SellerFulfillmentOrderId'] = val

    @property
    def fulfillment_action(self):
        """
        Specifies whether the fulfillment order should ship now or have an order hold put on it.

        :return:
        """
        return self.get('FulfillmentAction')

    @fulfillment_action.setter
    def fulfillment_action(self, val):
        if val not in self.valid_fulfillment_action_values:
            raise ValueError('`fulfillment_action` must be one of {}'.format(self.valid_fulfillment_action_values))
        self['FulfillmentAction'] = val

    @property
    def displayable_order_id(self):
        """
        A fulfillment order identifier that you create.

        This value displays as the order identifier in recipient-facing materials such as the outbound shipment packing slip.
        The value of DisplayableOrderId should match the order identifier that you provide to your customer.
        You can use the SellerFulfillmentOrderId for this value or you can specify an alternate value if you want your customer to reference an alternate order identifier.
        :return:
        """
        return self.get('DisplayableOrderId')

    @displayable_order_id.setter
    def displayable_order_id(self, val):
        raise_for_length(val, 'displayable_order_id', self.max_displayable_order_id_len,
                         self.min_displayable_order_id_len)
        self['DisplayableOrderId'] = val

    @property
    def displayable_order_date_time(self):
        """
        The date of your fulfillment order.

        Displays as the order date in customer-facing materials such as the outbound shipment packing slip.
        :return:
        """
        return from_iso_8601_format(self.get('DisplayableOrderDateTime'))

    @displayable_order_date_time.setter
    def displayable_order_date_time(self, val):
        self['DisplayableOrderDateTime'] = to_iso_8601_format(val)

    @property
    def displayable_order_comment(self):
        """
        Order-specific text that appears in customer-facing materials such as the outbound shipment packing slip.

        :return:
        """
        return self.get('DisplayableOrderComment')

    @displayable_order_comment.setter
    def displayable_order_comment(self, val):
        raise_for_length(val, 'displayable_order_comment', self.max_displayable_order_comment_len)
        self['DisplayableOrderComment'] = val

    @property
    def shipping_speed_category(self):
        """
        The shipping method for your fulfillment order.

        :return:
        """
        return self.get('ShippingSpeedCategory')

    @shipping_speed_category.setter
    def shipping_speed_category(self, val):
        if val not in self.valid_shipping_speed_category_values:
            raise ValueError('`shipping_speed_category` must be one of {}'.format(self.valid_shipping_speed_category_values))
        self['ShippingSpeedCategory'] = val

    @property
    def destination_address(self):
        return Address.load(self.get('DestinationAddress'))

    @destination_address.setter
    def destination_address(self, val):
        self['DestinationAddress'] = Address.load(val)

    @property
    def fulfillment_policy(self):
        """
        Indicates how unfulfillable items in a fulfillment order should be handled.

        :return:
        """
        return self.get('FulfillmentPolicy')

    @fulfillment_policy.setter
    def fulfillment_policy(self, val):
        if val not in self.valid_fulfillment_policy_values:
            raise ValueError('`fulfillment_policy` must be one of {}'.format(self.valid_fulfillment_policy_values))
        self['FulfillmentPolicy'] = val

    @property
    def notification_email_list(self):
        """
        A list of email addresses that you provide that are used by Amazon to send ship-complete notifications to your customers on your behalf.

        :return:
        """
        return self.get('NotificationEmailList', [])

    @notification_email_list.setter
    def notification_email_list(self, val):
        valid_types = [
            set,
            list,
            tuple
        ]
        if type(val) not in valid_types:
            raise ValueError('`notification_email_list` must be an instance of one of {}. (Got: {})'.format(valid_types, type(val)))
        for elem in val:
            raise_for_length(elem, elem, self.max_email_len)
        self['NotificationEmailList'] = list(val)

    def add_notification_email(self, email):
        """
        Add an email address to the notification list.

        :param email:
        :return:
        """
        raise_for_length(email, 'notification_email', self.max_email_len)
        if not self.get('NotificationEmailList'):
            self['NotificationEmailList'] = []
        self['NotificationEmailList'].append(email)

    @property
    def cod_settings(self):
        """
        The COD (Cash On Delivery) charges for a COD order.

        :return:
        """
        return CODSettings.load(self.get('CODSettings'))

    @cod_settings.setter
    def cod_settings(self, val):
        self['CODSettings'] = CODSettings.load(val)

    @property
    def items_(self):
        """
        A list of items to include in the fulfillment order preview, including quantity.

        :return:
        """
        return [CreateFulfillmentOrderItem.load(x) for x in self.get('Items', [])]

    @items_.setter
    def items_(self, val):
        valid_types = {
            set,
            list,
            tuple
        }
        if type(val) not in valid_types:
            raise ValueError('`items_` must be an instance of one of {}. (Got: {})'.format(valid_types, type(val)))
        self['Items'] = [CreateFulfillmentOrderItem.load(x) for x in val]

    def add_item(self, val):
        """
        Add an item to the items list.

        :param val:
        :return:
        """
        if not self.get('Items'):
            self['Items'] = []
        self['Items'].append(CreateFulfillmentOrderItem.load(val))

    @property
    def delivery_window(self):
        """
        Specifies the time range within which your Scheduled Delivery fulfillment order should be delivered.

        :return:
        """
        return DeliveryWindow.load(self.get('DeliveryWindow'))

    @delivery_window.setter
    def delivery_window(self, val):
        self['DeliveryWindow'] = DeliveryWindow.load(val)

    def request(self):
        data = dict(
            Action='CreateFulfillmentOrder'
        )
        data.update(self.flattened())

        return self.make_request(data)
