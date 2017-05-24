from unittest import TestCase
from mws.parsers.errors import ErrorResponse


class TestErrorResponse(TestCase):
    body = """
    <ErrorResponse xmlns="https://mws.amazonservices.com/">
    <Error>
        <Type>Sender</Type>
        <Code>InvalidParameterValue</Code>
        <Message>
            Value b'2' for parameter SignatureVersion is invalid.
        </Message>
    </Error>
    <RequestID>test-request-id</RequestID>
    </ErrorResponse>
    """

    def setUp(self):
        self.parser = ErrorResponse.load(self.body)

    def test_type(self):
        self.assertEqual(self.parser.type, 'Sender')

    def test_code(self):
        self.assertEqual(self.parser.code, 'InvalidParameterValue')

    def test_message(self):
        self.assertEqual(self.parser.message,
                         "\n            Value b'2' for parameter SignatureVersion is invalid.\n        ")

    def test_request_id(self):
        self.assertEqual(self.parser.request_id, 'test-request-id')
