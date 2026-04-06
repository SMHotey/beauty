import logging
import secrets
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SMSService:
    CODE_TTL = 300

    @staticmethod
    def generate_code():
        return f"{secrets.randbelow(900000) + 100000:06d}"

    @classmethod
    def send_code(cls, phone, code=None):
        if code is None:
            code = cls.generate_code()
        cache.set(f'sms_code_{phone}', code, cls.CODE_TTL)
        logger.info(f"[SMS STUB] Code sent to {phone}")
        return code

    @classmethod
    def verify_code(cls, phone, code):
        stored = cache.get(f'sms_code_{phone}')
        if stored and str(stored) == str(code):
            cache.delete(f'sms_code_{phone}')
            return True
        return False
