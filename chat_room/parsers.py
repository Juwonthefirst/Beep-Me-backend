from livekit import api
from rest_framework.parsers import BaseParser

receiver = api.WebhookReceiver(token_verifier=api.TokenVerifier())


class LiveKitwebhookParser(BaseParser):
    media_type = "application/webhook+json"

    async def parse(self, stream, media_type=None, parser_context=None):
        raw_body = stream.read()

        body = raw_body.decode("utf-8")
        if parser_context:
            parser_context["request"].body = raw_body

            return receiver.receive(
                body, parser_context["request"].headers.get("Authorization", "")
            )
        return receiver.receive(body, "")
