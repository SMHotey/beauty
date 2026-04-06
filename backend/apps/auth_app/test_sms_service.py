import pytest
from unittest.mock import patch

from apps.auth_app.sms_service import SMSService


@pytest.mark.django_db
class TestSMSService:
    def setup_method(self):
        from django.core.cache import cache
        cache.clear()

    def test_generate_code_returns_6_digits(self):
        code = SMSService.generate_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_code_random(self):
        codes = set()
        for _ in range(100):
            codes.add(SMSService.generate_code())
        assert len(codes) > 1

    def test_send_code_stores_in_cache(self):
        from django.core.cache import cache
        code = SMSService.send_code('+79001111111')
        stored = cache.get('sms_code_+79001111111')
        assert stored == code

    def test_send_code_with_custom_code(self):
        from django.core.cache import cache
        SMSService.send_code('+79001111111', code='654321')
        stored = cache.get('sms_code_+79001111111')
        assert stored == '654321'

    def test_send_code_returns_code(self):
        code = SMSService.send_code('+79001111111')
        assert code is not None
        assert len(code) == 6

    def test_verify_code_correct(self):
        code = SMSService.send_code('+79001111111')
        assert SMSService.verify_code('+79001111111', code) is True

    def test_verify_code_wrong(self):
        SMSService.send_code('+79001111111')
        assert SMSService.verify_code('+79001111111', '000000') is False

    def test_verify_code_no_code_sent(self):
        assert SMSService.verify_code('+79009999999', '123456') is False

    def test_verify_code_deletes_after_success(self):
        from django.core.cache import cache
        code = SMSService.send_code('+79001111111')
        SMSService.verify_code('+79001111111', code)
        assert cache.get('sms_code_+79001111111') is None

    def test_verify_code_string_comparison(self):
        from django.core.cache import cache
        SMSService.send_code('+79001111111', code='123456')
        assert SMSService.verify_code('+79001111111', 123456) is True

    def test_code_ttl(self):
        assert SMSService.CODE_TTL == 300
