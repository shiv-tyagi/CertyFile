import math
from random import random
import redis

class OTPLimitExceededException(Exception):
    def __init__(self, message, email):
        self.message = message
        self.email = email
    def __str__(self):
        return self.message

class OTPManager:
    def __init__(self, redis_host, redis_port, otp_attempts_limit_email, otp_rate_limit_window_email):
        if not redis_host:
            redis_host = "localhost"
        
        if not redis_port:
            redis_port = 6379

        self.redis = redis.Redis(host=redis_host, port=redis_port)
        self.OTP_ATTEMPTS_LIMIT_EMAIL = otp_attempts_limit_email
        self.OTP_RATE_LIMIT_WINDOW_EMAIL = otp_rate_limit_window_email
        return
    
    def otp_db_key(self, email: str):
        return f"OTP_{email}"
    
    def otp_count_key_for_email(self, email: str):
        return f"OTP_COUNT_{email}"
    
    def get_otp_attempts_count_for_email(self, email: str):
        key = self.otp_count_key_for_email(email)
        current_count = self.redis.get(key)

        if not current_count:
            current_count = 0
        
        return int(current_count)

    def increase_otp_attempts_count_for_email(self, email: str):
        current_count = self.get_otp_attempts_count_for_email(email)
        current_count += 1

        key = self.otp_count_key_for_email(email)
        self.redis.set(key, current_count, keepttl=True)

        if current_count == 1:
            self.redis.expire(key, self.OTP_RATE_LIMIT_WINDOW_EMAIL) # reset count every 30s
        return
    
    def is_email_rate_limited(self, email: str):
        return self.get_otp_attempts_count_for_email(email) >= self.OTP_ATTEMPTS_LIMIT_EMAIL

    def generate_otp(self, email: str):
        if self.is_email_rate_limited(email):
            raise OTPLimitExceededException(
                message="OTP sending limit exceeded for the email. Try again after some time.",
                email=email
            )

        key = self.otp_db_key(email)
        self.redis.set(key, str(math.floor(random() * 1000000)).zfill(6)) # store otp in redis database
        self.redis.expire(key, 180)
        self.increase_otp_attempts_count_for_email(email)
        return

    def verify_otp(self, otp: str, email: str):
        key = self.otp_db_key(email)
        val:bytes = self.redis.get(key)

        if not val or val.decode() != otp:
            return False
        
        self.redis.delete(key) # delete otp to avoid replay attack
        return True
