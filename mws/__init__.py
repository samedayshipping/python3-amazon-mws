# -*- coding: utf-8 -*-
__version__ = '0.6'

from ._mws import InboundShipments, Inventory, Products, Feeds, Reports, \
    Orders, Sellers, Recommendations, OutboundShipments, MWSError, DictWrapper, MWS, remove_empty, DataWrapper, \
    calc_md5, XMLError
from .parsers.products import GetMatchingProductForIdResponse, GetCompetitivePricingForAsinResponse
from .parsers.fulfillment import ListInboundShipmentResponse, ListInboundShipmentItemsResponse, \
    GetPrepInstructionsForASINResponse
from .parsers.orders import ListOrdersResponse, ListOrderItemsResponse
from .fulfillment_outbound_shipment import CreateFulfillmentOrder
from .parsers import RequestReportResponse
