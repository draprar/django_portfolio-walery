from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
        Token generator for account activation, based on the built-in
        PasswordResetTokenGenerator class.
    """
    def _make_hash_value(self, user, timestamp):
        """
                Create a secure hash value for the token generation.
        """
        return str(user.pk) + str(timestamp) + str(user.is_active)


# Create a global instance of the token generator
account_activation_token = AccountActivationTokenGenerator()
