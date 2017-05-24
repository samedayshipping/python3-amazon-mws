from ..base import BaseElementWrapper, BaseResponseMixin, first_element, first_element_or_none
from ..errors import ProductError
import mws

namespaces = {
    'a': 'http://mws.amazonservices.com/schema/Products/2011-10-01',
    'b': 'http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd'
}


#######################################
# Get Matching Product For Id Classes #
#######################################


class GetMatchingProductForIdProduct(BaseElementWrapper):

    @property
    @first_element
    def _marketplace_asin(self):
        return self.element.xpath('./a:/Identifiers/a:MarketplaceASIN', namespaces=namespaces)

    @property
    @first_element
    def marketplace_id(self):
        return self.element.xpath('./a:Identifiers/a:MarketplaceASIN/a:MarketplaceId/text()', namespaces=namespaces)

    @property
    @first_element
    def asin(self):
        return self.element.xpath('./a:Identifiers/a:MarketplaceASIN/a:ASIN/text()', namespaces=namespaces)

    @property
    @first_element
    def product_group(self):
        return self.element.xpath('./a:AttributeSets/b:ItemAttributes/b:ProductGroup/text()', namespaces=namespaces)

    @property
    @first_element
    def product_type_name(self):
        return self.element.xpath('./a:AttributeSets/b:ItemAttributes/b:ProductTypeName/text()', namespaces=namespaces)

    @property
    @first_element
    def title(self):
        return self.element.xpath('./a:AttributeSets/b:ItemAttributes/b:Title/text()', namespaces=namespaces)

    @property
    @first_element
    def weight(self):
        return self.element.xpath('./a:AttributeSets/b:ItemAttributes/b:PackageDimensions/b:Weight/text()', namespaces=namespaces)

    @property
    @first_element
    def part_number(self):
        return self.element.xpath('./a:AttributeSets/b:ItemAttributes/b:PartNumber/text()', namespaces=namespaces)

    @property
    @first_element
    def model(self):
        return self.element.xpath('./a:AttributeSets/b:ItemAttributes/b:Model/text()', namespaces=namespaces)

    @property
    @first_element
    def color(self):
        return self.element.xpath('./a:AttributeSets/b:ItemAttributes/b:Color/text()', namespaces=namespaces)

    # ToDo: Add attribute sets and included children

    # ToDo: Add relationships and included children

    @property
    def sales_rankings(self):
        rankings = self.element.xpath('.//a:SalesRankings/a:SalesRank', namespaces=namespaces)
        if rankings:
            data = []
            for rank in rankings:
                pcid = first_element_or_none(rank.xpath('./a:ProductCategoryId/text()', namespaces=namespaces))
                r = first_element_or_none(rank.xpath('./a:Rank/text()', namespaces=namespaces))
                d = (pcid, r)
                data.append(d)
            return data
        return []


class GetMatchingProductForIdResult(BaseElementWrapper):

    @property
    @first_element
    def identifier(self):
        """
        Typically UPC, EAN, or ISBN
        :return:
        """
        return self.element.xpath('./@Id')

    @property
    @first_element
    def id_type(self):
        return self.element.xpath('./@IdType')

    @property
    @first_element
    def status(self):
        return self.element.xpath('./@status')

    @property
    def products(self):
        return [GetMatchingProductForIdProduct(x) for x in self.element.xpath('.//a:Products/a:Product', namespaces=namespaces)]

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
        return ProductError(x, self.identifier)

    def __nonzero__(self):
        """
        No products means there was either an error or no match for that particular identifier.

        :return:
        """
        return bool(self.products)


class GetMatchingProductForIdResponse(BaseElementWrapper, BaseResponseMixin):

    @property
    def matching_product_for_id_results(self):
        return [GetMatchingProductForIdResult(x) for x in self.element.xpath('//a:GetMatchingProductForIdResult', namespaces=namespaces)]

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id,
                mws_marketplace_id, id_type=None, ids=(), mws_auth_token=None):
        """
        Use python amazon mws to request get_matching_product_for_id.

        :param mws_access_key: Your account access key.
        :param mws_secret_key: Your account secret key.
        :param mws_account_id: Your account id.
        :param mws_marketplace_id: Your marketplace id
        :param id_type: One of UPC, EAN, or ISBN.
        :param ids: List of identifiers.
        :return:
        """
        products_api = mws.Products(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = products_api.get_matching_product_for_id(mws_marketplace_id, id_type, ids)
        return cls.load(response.original)