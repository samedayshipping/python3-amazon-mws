import time
import datetime
import re

import mws
from mws.parsers.base import BaseElementWrapper, BaseResponseMixin, first_element, parse_bool
from mws.parsers.errors import ErrorResponse
from dateutil import parser

namespaces = {'a': 'http://mws.amazonaws.com/doc/2009-01-01/'}


class ReportRequestInfo(BaseElementWrapper):

    def __init__(self, element):
        BaseElementWrapper.__init__(self, element)

    @property
    @first_element
    def report_type(self):
        return self.element.xpath('./a:ReportType/text()', namespaces=namespaces)

    @property
    @first_element
    def report_processing_status(self):
        return self.element.xpath('./a:ReportProcessingStatus/text()', namespaces=namespaces)

    @property
    @first_element
    def _end_date(self):
        return self.element.xpath('./a:EndDate/text()', namespaces=namespaces)

    @property
    def end_date(self):
        if self._end_date:
            return parser.parse(self._end_date)
        return

    @property
    @first_element
    def _scheduled(self):
        return self.element.xpath('./a:Scheduled/text()', namespaces=namespaces)

    @property
    def scheduled(self):
        return self._scheduled == 'true'

    @property
    @first_element
    def report_request_id(self):
        return self.element.xpath('./a:ReportRequestId/text()', namespaces=namespaces)

    @property
    @first_element
    def _started_processing_date(self):
        return self.element.xpath('./a:StartedProcessingDate/text()', namespaces=namespaces)

    @property
    def started_processing_date(self):
        if not self._started_processing_date:
            return
        return parser.parse(self._started_processing_date)

    @property
    @first_element
    def _submitted_date(self):
        return self.element.xpath('./a:SubmittedDate/text()', namespaces=namespaces)

    @property
    def submitted_date(self):
        if not self._submitted_date:
            return
        return parser.parse(self._submitted_date)

    @property
    @first_element
    def _start_date(self):
        return self.element.xpath('./a:StartDate/text()', namespaces=namespaces)

    @property
    def start_date(self):
        if not self._start_date:
            return
        return parser.parse(self._start_date)

    @property
    @first_element
    def _completed_date(self):
        return self.element.xpath('./a:CompletedDate/text()', namespaces=namespaces)

    @property
    def completed_date(self):
        if self._completed_date:
            return parser.parse(self._completed_date)
        return

    @property
    @first_element
    def generated_report_id(self):
        return self.element.xpath('./a:GeneratedReportId/text()', namespaces=namespaces)


class GetReportRequestList(BaseElementWrapper, BaseResponseMixin):

    @property
    def get_report_request_list(self):
        return [ReportRequestInfo(x) for x in self.element.xpath('//a:ReportRequestInfo', namespaces=namespaces)]

    @property
    @first_element
    def next_token(self):
        return self.element.xpath('//a:NextToken/text()', namespaces=namespaces)

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id, mws_auth_token=None,
                max_count=None, requested_from_date=None, requested_to_date=None,
                report_request_ids=(), report_types=(), report_processing_statuses=()):
        api = mws.Reports(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.get_report_request_list(requestids=report_request_ids, types=report_types,
                                               processingstatuses=report_processing_statuses, max_count=max_count,
                                               fromdate=requested_from_date, todate=requested_to_date)
        err = ErrorResponse.load(response.original)
        if err.message:
            raise err
        return cls.load(response.original, mws_access_key, mws_secret_key, mws_account_id, mws_auth_token)

    @classmethod
    def from_next_token(cls, mws_access_key, mws_secret_key, mws_account_id, next_token, mws_auth_token=None):
        api = mws.Reports(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.get_report_list_by_next_token(next_token)
        err = ErrorResponse.load(response.original)
        if err.message:
            raise err
        return cls.load(response.original, mws_access_key, mws_secret_key, mws_account_id, mws_auth_token)


class ReportInfo(BaseElementWrapper):

    @property
    @first_element
    def report_type(self):
        return self.element.xpath('./a:ReportType/text()', namespaces=namespaces)

    @property
    @parse_bool
    @first_element
    def acknowledged(self):
        return self.element.xpath('./a:Acknowledged/text()', namespaces=namespaces)

    @property
    @first_element
    def report_id(self):
        return self.element.xpath('./a:ReportId/text()', namespaces=namespaces)

    @property
    @first_element
    def report_request_id(self):
        return self.element.xpath('./a:ReportRequestId/text()', namespaces=namespaces)

    @property
    @first_element
    def available_date(self):
        return self.element.xpath('./a:AvailableDate/text()', namespaces=namespaces)


class GetReportList(BaseElementWrapper, BaseResponseMixin):

    @property
    @first_element
    def next_token(self):
        return self.element.xpath('//a:NextToken/text()', namespaces=namespaces)

    @property
    def report_info_list(self):
        return [ReportInfo(x) for x in self.element.xpath('./a:GetReportListResult//a:ReportInfo|./a:GetReportListByNextTokenResult//a:ReportInfo', namespaces=namespaces)]

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id, request_ids=(), max_count=None, types=(),
                acknowledged=None, fromdate=None, todate=None):
        api = mws.Reports(mws_access_key, mws_secret_key, mws_account_id)
        response = api.get_report_list(requestids=request_ids, max_count=max_count, types=types,
                                       acknowledged=acknowledged, fromdate=fromdate, todate=todate)

        err = ErrorResponse.load(response.original)
        if err.message:
            raise err

        return cls.load(response.original, mws_access_key, mws_secret_key, mws_account_id)


class RequestReportResponse(BaseElementWrapper, BaseResponseMixin):
    # How many days to look back for start of report
    START_DATE_DAYS = 30

    # How many days to look back for end of report
    END_DATE_DAYS = 0

    def __init__(self, element, mws_access_key=None, mws_secret_key=None, mws_account_id=None, mws_auth_token=None):
        BaseElementWrapper.__init__(self, element)
        BaseResponseMixin.__init__(self)
        self.mws_access_key = mws_access_key
        self.mws_secret_key = mws_secret_key
        self.mws_account_id = mws_account_id
        self.mws_auth_token = mws_auth_token
        self.report_id = ''

    @property
    @first_element
    def report_type(self):
        return self.element.xpath("//a:ReportType/text()", namespaces=namespaces)

    @property
    @first_element
    def report_processing_status(self):
        return self.element.xpath('//a:ReportProcessingStatus/text()', namespaces=namespaces)

    @property
    @first_element
    def _end_date(self):
        return self.element.xpath('//a:EndDate/text()', namespaces=namespaces)

    @property
    def end_date(self):
        """
        Parse end_date and return datetime object
        :return:
        """
        if not self._end_date:
            return
        return parser.parse(self._end_date)

    @property
    @first_element
    def _scheduled(self):
        return self.element.xpath('//a:Scheduled/text()', namespaces=namespaces)

    @property
    def scheduled(self):
        return self._scheduled == 'true'

    @property
    @first_element
    def report_request_id(self):
        return self.element.xpath('//a:ReportRequestId/text()', namespaces=namespaces)

    @property
    @first_element
    def _submitted_date(self):
        return self.element.xpath('//a:SubmittedDate/text()', namespaces=namespaces)

    @property
    def submitted_date(self):
        if not self._submitted_date:
            return
        return parser.parse(self._submitted_date)

    @property
    @first_element
    def _start_date(self):
        return self.element.xpath('//a:StartDate/text()', namespaces=namespaces)

    @property
    def start_date(self):
        if not self._start_date:
            return
        return parser.parse(self._start_date)

    def wait(self):
        """
        Wait for report to finish processing.
        Blocking method. Will return once report has finished processing.
        :return:
        """
        done = False
        status = ''
        report_id = None
        while not done:
            time.sleep(60)  # sleep before querying since it takes time to process and so that when the report is _DONE_ the loop is immediately broken.
            response = GetReportRequestList.request(self.mws_access_key, self.mws_secret_key, self.mws_account_id, mws_auth_token=self.mws_auth_token, report_request_ids=(self.report_request_id,))
            request_result = response.get_report_request_list[0]
            status = request_result.report_processing_status
            self.logger.debug('report_request_id=%s report_processing_status=%s' % (self.report_request_id, status))
            done = bool(request_result.completed_date)
            report_id = request_result.generated_report_id
        if status != '_DONE_':
            raise ValueError("GetReportRequestList for report_request_id=%s returned %s" % (self.report_request_id, status))
        return report_id

    def report_contents(self):
        """
        Return report response contents
        :return:
        """
        api = mws.Reports(self.mws_access_key, self.mws_secret_key, self.mws_account_id, auth_token=self.mws_auth_token)
        response = api.get_report(self.report_id)
        return response.original

    def _acknowledge_report(self):
        """
        Acknowledge the report which finished downloading. This is private because this shouldn't be used except by wait_and_download.
        :return:
        """
        api = mws.Reports(self.mws_access_key, self.mws_secret_key, self.mws_account_id, auth_token=self.mws_auth_token)
        api.update_report_acknowledgements(report_ids=(self.report_id,), acknowledged=True)

    def wait_and_download(self):
        """
        Wait for the report to finish processing and return the report contents
        :return:
        """
        self.logger.info('Waiting for report (request_id=%s) to finish processing' % self.report_request_id)
        self.report_id = self.wait()
        self.logger.info('Downloading report (request_id=%s - generated_report_id=%s)' % (self.report_request_id, self.report_id))
        contents = self.report_contents()
        self.logger.info('Acknowledging report (request_id=%s - generated_report_id=%s)' % (self.report_request_id, self.report_id))
        self._acknowledge_report()
        return contents

    @classmethod
    def download_most_recent(cls, mws_access_key, mws_secret_key, mws_account_id, report_enumeration_type):
        get_report_list = GetReportList.request(mws_access_key, mws_secret_key, mws_account_id, types=(report_enumeration_type,))
        if get_report_list.report_info_list:
            report_id = get_report_list.report_info_list[0].report_id
            api = mws.Reports(mws_access_key, mws_secret_key, mws_account_id)
            response = api.get_report(report_id)
            return response.original
        raise mws.MWSError('No reports for `{}`'.format(report_enumeration_type))

    @classmethod
    def request(cls, mws_access_key, mws_secret_key, mws_account_id,
                report_enumeration_type, start_date=None, end_date=None, mws_auth_token=None):
        """
        Use python amazon mws to request get_matching_product_for_id.

        :param mws_access_key: Your account access key.
        :param mws_secret_key: Your account secret key.
        :param mws_account_id: Your account id.
        :param report_enumeration_type: The report enumeration value
        :param start_date: Datetime object of report start date
        :param end_date: Datetime object of report end date
        :param mws_auth_token: (Optional) Use when making a request from a third party
        :return:
        """
        api = mws.Reports(mws_access_key, mws_secret_key, mws_account_id, auth_token=mws_auth_token)
        response = api.request_report(report_enumeration_type, start_date=start_date, end_date=end_date)
        err = ErrorResponse.load(response.original)
        if err.message:
            raise err
        return cls.load(response.original, mws_access_key, mws_secret_key, mws_account_id, mws_auth_token)


class FlatFileWrapper(object):
    """
    Parser/generator for flat file report contents
    """

    def __init__(self, report_contents, convert_numerical=False):
        self.report_contents = report_contents
        # Split the report into lines and strip any excess whitespace from each line.
        self._lines = self.report_contents.split('\n')
        self.headers = self._lines.pop(0)
        self.convert_numerical = convert_numerical

    def offset_dt(self, dt):
        """
        Calculate the UTC offset and apply it to a datetime object returned from amazon since they use GMT.
        :param dt:
        :return:
        """
        offset = datetime.datetime.utcnow() - datetime.datetime.now()
        seconds_offset = round(offset.total_seconds()) / 60
        return dt - datetime.timedelta(seconds=seconds_offset)

    def convert_text(self, t):
        """
        Convert text into proper data type.
        :param t:
        :return:
        """
        # Convert datetime
        if re.search('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\+\d{2}:\d{2})?', t):
            return self.offset_dt(parser.parse(t))
        if self.convert_numerical:
            if re.search('^\d+\.\d+$', t):
                return float(t)
            if re.search('^\d+$', t):
                return int(t)
        if not t:
            return None
        return t

    def lines(self):
        """
        Generator function yielding each line's contents in a tuple.
        :return:
        """
        for line in self._lines:
            t = tuple(self.convert_text(x.strip()) for x in line.split('\t'))
            yield t

    def __iter__(self):
        for line in self.lines():
            yield line

    def __str__(self):
        return self.report_contents
