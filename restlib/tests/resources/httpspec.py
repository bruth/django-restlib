from django.test import TestCase
from django.http import HttpRequest, HttpResponse

from restlib import http
from restlib import resources


__all__ = ('ResourceTestCase',)


class Object(object):
    pass


class HttpResponseTestCase(TestCase):

    def test_100_continue(self):
        pass

    def test_101_switching_protocols(self):
        pass

    def test_200_ok(self):
        pass

    def test_201_created(self):
        pass

    def test_202_accepted(self):
        pass

    # not required per HTTP spec
    def test_203_nonauthoritative_information(self):
        pass

    # browser specific, used to update browsers without supplying the
    # entity body
    def test_204_no_content(self):
        pass

    # browser specific, used to tell browsers to clear any HTML form
    # elements on the current page
    def test_205_reset_content(self):
        pass

    def test_206_partial_content(self):
        pass

    def test_300_multiple_choices(self):
        pass

    def test_301_move_permanently(self):
        pass

    # this behaves exactly like a 307 response, except is the correct status
    # code for HTTP 1.0 clients
    def test_302_found(self):
        pass

    def test_303_see_other(self):
        pass

    def test_304_not_modified(self):
        pass

    def test_305_use_proxy(self):
        pass

    # this code is not implemented
    # def test_306_XXX(self):
    #     pass

    # this behaves exactly like a 302 response, except is the correct status
    # code for HTTP 1.1 clients
    def test_307_temporary_redirect(self):
        pass

    def test_400_bad_request(self):
        pass

    def test_401_unauthorized(self):
        pass

    # currently not implemented, set aside for future use
    # def test_402_payment_required(self):
    #     pass

    def test_403_forbidden(self):
        pass

    def test_404_not_found(self):
        pass

    def test_405_method_not_allowed(self):
        pass

    def test_406_not_acceptable(self):
        pass

    def test_407_proxy_authentication_required(self):
        pass

    def test_408_request_timeout(self):
        pass

    def test_409_conflict(self):
        pass

    def test_410_gone(self):
        pass

    def test_411_length_required(self):
        pass

    def test_412_precondition_failed(self):
        pass

    def test_413_request_entity_too_large(self):
        pass

    def test_414_request_uri_too_long(self):
        pass

    def test_415_unsupported_media_type(self):
        pass

    def test_416_requested_range_not_satisfiable(self):
        pass

    def test_417_expectation_failed(self):
        pass

    def test_500_internal_server_error(self):
        pass

    def test_501_not_implemented(self):
        pass

    def test_502_bad_gateway(self):
        pass

    def test_503_service_unavailable(self):
        pass

    def test_504_gateway_timeout(self):
        pass

    def test_505_http_version_not_supported(self):
        pass


