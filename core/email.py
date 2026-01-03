import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import bleach

logger = logging.getLogger(__name__)

def send_brevo_email(subject, html_content, recipient_list):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_client = sib_api_v3_sdk.ApiClient(configuration)
    api_client.rest_client.pool_manager.connection_pool_kw['timeout'] = 10
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)

    # Sanity check / sanitization
    subject = bleach.clean(subject, strip=True)
    html_content = bleach.clean(
        html_content,
        tags=['p', 'br', 'strong', 'b', 'i', 'a'],
        attributes={'a': ['href']},
        strip=True
    )

    sender = {"name": "Walery", "email": settings.DEFAULT_FROM_EMAIL}
    to = [{"email": email} for email in recipient_list]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject=subject,
        html_content=html_content
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        return response
    except (ApiException, Exception):
        logger.exception("Błąd podczas wysyłania maila z Brevo")
        return None
