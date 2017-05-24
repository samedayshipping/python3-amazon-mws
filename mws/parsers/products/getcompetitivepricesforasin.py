from ..base import BaseElementWrapper, BaseResponseMixin, first_element, first_element_or_none
from ..errors import ProductError
import mws


namespaces = {
    'a': 'http://mws.amazonservices.com/schema/Products/2011-10-01',
    'b': 'http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd'
}

############################################
# Get Competitive Pricing For ASIN Classes #
############################################


class CompetitivePriceElement(BaseElementWrapper):

    @property
    def belongs_to_requester(self):
        data = first_element_or_none(self.element.xpath('./@belongsToRequester', namespaces=namespaces))
        if not data:
            return
        if data == 'true':
            return True
        else:
            return False

    @property
    @first_element
    def condition(self):
        return self.element.xpath('./@condition', namespaces=namespaces)

    @property
    @first_element
    def subcondition(self):
        return self.element.xpath('./@subcondition', namespaces=namespaces)

    @property
    @first_element
    def landed_price(self):
        return self.element.xpath('./a:Price/a:LandedPrice/a:Amount/text()', namespaces=namespaces)

    @property
    @first_element
    def listing_price(self):
        return self.element.xpath('./a:Price/a:ListingPrice/a:Amount/text()', namespaces=namespaces)

    @property
    @first_element
    def shipping(self):
        return self.element.xpath('./a:Price/a:Shipping/a:Amount/text()', namespaces=namespaces)


class GetCompetitivePricingForAsinProduct(BaseElementWrapper):

    @property
    @first_element
    def asin(self):
        return self.element.xpath('./a:Identifiers/a:MarketplaceASIN/a:ASIN/text()', namespaces=namespaces)

    @property
    @first_element
    def marketplace_id(self):
        return self.element.xpath('./a:Identifiers/a:MarketplaceASIN/a:MarketplaceId/text()', namespaces=namespaces)

    @property
    def sales_rankings(self):
        rankings = self.element.xpath('./a:SalesRankings/a:SalesRank', namespaces=namespaces)
        ranks = []
        for ranking in rankings:
            pcid = first_element_or_none(ranking.xpath('./a:ProductCategoryId/text()', namespaces=namespaces))
            r = first_element_or_none(ranking.xpath('./a:Rank/text()', namespaces=namespaces))
            ranks.append((pcid, r))
        return ranks

    @property
    def competitive_prices(self):
        return [CompetitivePriceElement(x) for x in self.element.xpath('./a:CompetitivePricing/a:CompetitivePrices/a:CompetitivePrice', namespaces=namespaces)]


class GetCompetitivePricingForAsinResult(BaseElementWrapper):

    @property
    @first_element
    def asin(self):
        return self.element.xpath('./@ASIN')

    @property
    @first_element
    def status(self):
        return self.element.xpath('./@status')

    @property
    def products(self):
        """
        :rtype: list[GetCompetitivePricingForAsinProduct]
        :return:
        """
        return [GetCompetitivePricingForAsinProduct(x) for x in self.element.xpath('.//a:Product', namespaces=namespaces)]

    @property
    def error(self):
        """
        Return mws error instance which can be raised if necessary.

        The reason this method doesn't raise on it's own is because it allows for more
        customization when integrating this class into another module.

        Usage:
            >>> resp = GetMatchingProductForIdResponse.load_from_file('/home/user/my-xml.xml')
            >>> for result in resp.matching_product_for_id_results:
            >>>     if result.error:
            >>>         print result.error.message, result.error.identifier
            >>>         raise result.error
        :return:
        """
        x = first_element_or_none(self.element.xpath('./a:Error', namespaces=namespaces))
        if x is None:
            return
        return ProductError(x, self.asin)

    def __nonzero__(self):
        """
        No products means there was either an error or no match for that particular identifier.

        :return:
        """
        return bool(self.products)


class GetCompetitivePricingForAsinResponse(BaseElementWrapper, BaseResponseMixin):

    @property
    def competitive_pricing_for_asin_results(self):
        return [GetCompetitivePricingForAsinResult(x) for x in self.element.xpath('.//a:GetCompetitivePricingForASINResult', namespaces=namespaces)]

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id,
                mws_marketplace_id, asins=()):
        """
        Use python amazon mws to request get_matching_product_for_id.

        :param mws_access_key: Your account access key.
        :param mws_secret_key: Your account secret key.
        :param mws_account_id: Your account id.
        :param mws_marketplace_id: Your marketplace id
        :param asins: list of asins.
        :return:
        """
        products_api = mws.Products(mws_access_key, mws_secret_key, mws_account_id)
        response = products_api.get_competitive_pricing_for_asin(mws_marketplace_id, asins=asins)
        return cls.load(response.original)
