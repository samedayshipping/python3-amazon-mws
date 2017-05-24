import abc
import time
import logging

from mws.parsers.feeds.submitfeedresponse import SubmitFeedResponse, GetFeedSubmissionListResponse


# flat file feeds
class BaseFeed(object):

    __metaclass__ = abc.ABCMeta
    enumeration_value = ""

    def __init__(self, access_key, secret_key, account_id, region="US", domain='', uri='', version='', auth_token='', marketplace_ids=('ATVPDKIKX0DER',), content_type='text/xml', purge_and_replace=False):
        self.marketplace_ids = marketplace_ids
        self.content_type = content_type
        self.purge_and_replace = purge_and_replace
        self.access_key = access_key
        self.secret_key = secret_key
        self.account_id = account_id
        self.auth_token = auth_token
        self.logger = logging.getLogger(self.__class__.__name__)

    @abc.abstractmethod
    def generate(self):
        """
        Generate the feed contents
        :return:
        """
        raise NotImplementedError("method `generate` is not implemented")

    @property
    def _purge_and_replace(self):
        """
        return text value of purge and replace for compatibility with request url
        :return:
        """
        if self.purge_and_replace:
            return 'true'
        return 'false'

    def upload(self):
        response = SubmitFeedResponse.request(self.access_key, self.secret_key, self.account_id, self.generate(), self.enumeration_value, self.auth_token, self.marketplace_ids, self.content_type, self._purge_and_replace)
        done = False
        status = ''
        feed_submission_id = None
        while not done:
            feed_submission_id = response.feed_submission_id
            time.sleep(60)  # sleep before querying since it takes time to process and so that when the report is _DONE_ the loop is immediately broken.
            r = GetFeedSubmissionListResponse.request(self.access_key, self.secret_key, self.account_id, self.auth_token, (feed_submission_id,))
            request_result = r.feed_submission_info_list()[0]
            status = request_result.feed_processing_status
            self.logger.debug('feed_submission_id=%s report_processing_status=%s' % (feed_submission_id, status))
            done = bool(request_result._completed_processing_date)
        if status != '_DONE_':
            raise ValueError("GetFeedSubmissionListResult for feed_submission_id=%s returned %s" % (feed_submission_id, status))


class UpdateInboundShipmentPlanFeed(BaseFeed):

    enumeration_value = '_POST_FLAT_FILE_FBA_UPDATE_INBOUND_PLAN_'

    def __init__(self, *args, **kwargs):
        """

        :param plan_id: The plan id to update
            ex. PLN2RHD
        :param data: a list containing tuples of merchant sku, quantity.
            ex. [(MySku123, 5), (MySku999, 12)]
        """
        self.plan_id = kwargs.pop('plan_id')
        self.data = kwargs.pop('data')
        kwargs['content_type'] = 'text/tab-separated-values; charset=iso-8859-1'
        BaseFeed.__init__(self, *args, **kwargs)

    def generate(self):
        feed_header = "PlanId\t{}\n\n".format(self.plan_id)
        column_headers = "MerchantSKU\tQuantity\n"
        column_data = "\n".join(["{sku}\t{quantity}".format(sku=x[0], quantity=x[1]) for x in self.data])
        return feed_header + column_headers + column_data
