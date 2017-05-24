from mws.parsers import ErrorResponse
from mws.parsers.base import BaseElementWrapper, BaseResponseMixin, first_element
from mws import Feeds

namespaces = {
    'a': 'http://mws.amazonaws.com/doc/2009-01-01/'
}


class FeedSubmissionInfo(BaseElementWrapper):

    @property
    @first_element
    def feed_processing_status(self):
        return self.element.xpath('//a:FeedProcessingStatus/text()', namespaces=namespaces)

    @property
    @first_element
    def feed_type(self):
        return self.element.xpath('//a:FeedType/text()', namespaces=namespaces)

    @property
    @first_element
    def feed_submission_id(self):
        return self.element.xpath('//a:FeedSubmissionId/text()', namespaces=namespaces)

    @property
    @first_element
    def _started_processing_date(self):
        return self.element.xpath('//a:StartedProcessingDate/text()', namespaces=namespaces)

    @property
    @first_element
    def _completed_processing_date(self):
        return self.element.xpath('//a:CompletedProcessingDate/text()', namespaces=namespaces)

    @property
    @first_element
    def _submitted_date(self):
        return self.element.xpath('//a:SubmittedDate/text()', namespaces=namespaces)


class GetFeedSubmissionListResponse(BaseElementWrapper, BaseResponseMixin):

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id, mws_auth_token=None, feed_submission_id_list=(), max_count=None, feedtypes=(), processingstatuses=(), fromdate=None, todate=None):
        api = Feeds(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.get_feed_submission_list(feed_submission_id_list, max_count, feedtypes, processingstatuses, fromdate, todate)
        with open('GetFeedSubmissionListResponse.xml', 'wb') as f:
            f.write(response.original)
        err = ErrorResponse.load(response.original)
        if err.message:
            raise err
        return cls.load(response.original, mws_access_key, mws_secret_key, mws_account_id, mws_auth_token)

    @property
    @first_element
    def next_token(self):
        return self.element.xpath('//a:NextToken/text()', namespaces=namespaces)

    def feed_submission_info_list(self):
        return [FeedSubmissionInfo(x) for x in self.element.xpath('//a:FeedSubmissionInfo', namespaces=namespaces)]


class SubmitFeedResponse(BaseElementWrapper, BaseResponseMixin):

    def __init__(self, element, mws_access_key=None, mws_secret_key=None, mws_account_id=None, mws_auth_token=None):
        BaseElementWrapper.__init__(self, element)
        BaseResponseMixin.__init__(self)
        self.mws_access_key = mws_access_key
        self.mws_secret_key = mws_secret_key
        self.mws_account_id = mws_account_id
        self.mws_auth_token = mws_auth_token

    @property
    @first_element
    def feed_submission_id(self):
        return self.element.xpath('//a:FeedSubmissionId/text()', namespaces=namespaces)

    @property
    @first_element
    def feed_type(self):
        return self.element.xpath('//a:FeedType/text()', namespaces=namespaces)

    @property
    @first_element
    def _submitted_date(self):
        return self.element.xpath('//a:SubmittedDate/text()', namespaces=namespaces)

    @property
    @first_element
    def feed_processing_status(self):
        return self.element.xpath('//a:FeedProcessingStatus/text()', namespaces=namespaces)

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id, feed_contents, feed_type, mws_auth_token=None, marketplace_ids=('ATVPDKIKX0DER',), content_type='text/xml', purge=False):
        api = Feeds(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        purge = 'true' if purge else 'false'
        response = api.submit_feed(feed_contents, feed_type, marketplace_ids, content_type, purge)
        err = ErrorResponse.load(response.original)
        if err.message:
            raise err
        with open('SubmitFeedResponse.xml', 'wb') as f:
            f.write(response.original)
        return cls.load(response.original, mws_access_key, mws_secret_key, mws_account_id, mws_auth_token)
