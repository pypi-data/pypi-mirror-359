from jwt_drf_passwordless import signals
from jwt_drf_passwordless.compat import get_user_email
from jwt_drf_passwordless.conf import settings
from rest_framework import generics, status
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from jwt_drf_passwordless.constants import Messages
from .services import PasswordlessTokenService


class AbstractPasswordlessTokenRequestView(APIView):
    """
    This returns a callback challenge token we can trade for a user's Auth Token.
    """

    success_response = Messages.TOKEN_SENT
    failure_response = Messages.CANNOT_SEND_TOKEN

    permission_classes = settings.PERMISSIONS.passwordless_token_request

    @property
    def serializer_class(self):
        # Our serializer depending on type
        raise NotImplementedError

    @property
    def token_request_identifier_field(self):
        raise NotImplementedError

    @property
    def token_request_identifier_type(self):
        raise NotImplementedError

    def send(self, token):
        raise NotImplementedError

    def _respond_ok(self):
        status_code = status.HTTP_200_OK
        response_detail = self.success_response
        return Response({"detail": response_detail}, status=status_code)

    def _respond_not_ok(self, status=status.HTTP_400_BAD_REQUEST):
        response_detail = self.failure_response
        return Response({"detail": response_detail}, status=status)

    @method_decorator(settings.DECORATORS.token_request_rate_limit_decorator)
    def post(self, request, *args, **kwargs):
        if (
            self.token_request_identifier_type.upper()
            not in settings.ALLOWED_PASSWORDLESS_METHODS
        ):
            # Only allow auth types allowed in settings.
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            # Might create user if settings allow it, or return the user to whom the token should be sent.
            user = serializer.save()

            if not user:
                return self._respond_not_ok()
            if PasswordlessTokenService.should_throttle(user):
                return self._respond_not_ok(status.HTTP_429_TOO_MANY_REQUESTS)

            if not settings.ALLOW_ADMIN_AUTHENTICATION:
                # Only allow admin users to authenticate with password
                # Note that AbstractBaseUser does not have is_staff and is_superuser properties.
                # and in that case the use will be able to proceed.
                if getattr(user, "is_staff", None) or getattr(
                    user, "is_superuser", None
                ):
                    return self._respond_not_ok()

            # Create and send callback token
            token = PasswordlessTokenService.create_token(
                user, self.token_request_identifier_field
            )
            self.send(token)

            if token:
                return self._respond_ok()
            else:
                return self._respond_not_ok()
        else:
            return Response(
                serializer.error_messages, status=status.HTTP_400_BAD_REQUEST
            )


class PasswordlessEmailTokenRequestView(AbstractPasswordlessTokenRequestView):
    permission_classes = (AllowAny,)
    serializer_class = settings.SERIALIZERS.passwordless_email_token_request
    token_request_identifier_field = settings.EMAIL_FIELD_NAME
    token_request_identifier_type = "email"

    def send(self, token):
        user = token.user
        context = {"user": user, "token": token.token, "short_token": token.short_token}
        to = [get_user_email(user)]
        settings.EMAIL.passwordless_request(self.request, context).send(to)


class PasswordlessMobileTokenRequestView(AbstractPasswordlessTokenRequestView):
    permission_classes = (AllowAny,)
    serializer_class = settings.SERIALIZERS.passwordless_mobile_token_request
    token_request_identifier_field = settings.MOBILE_FIELD_NAME
    token_request_identifier_type = "mobile"

    def send(self, token):
        user = token.user
        context = {"user": user, "token": token.token, "short_token": token.short_token}
        to = getattr(user, settings.MOBILE_FIELD_NAME)
        return settings.SMS_SENDERS.passwordless_request(self.request, context).send(
            str(to)
        )


class AbstractExchangePasswordlessTokenForAuthTokenView(generics.GenericAPIView):
    """Use this endpoint to obtain user authentication token."""

    permission_classes = settings.PERMISSIONS.passwordless_token_exchange

    @property
    def serializer_class(self):
        # Our serializer depending on type
        raise NotImplementedError

    @method_decorator(settings.DECORATORS.token_redeem_rate_limit_decorator)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        if not user.is_active:
            user.is_active = True
            user.save()
            signals.user_activated.send(
                sender=self.__class__, user=user, request=self.request
            )
        return Response(data=serializer.validated_data, status=status.HTTP_200_OK)


class EmailExchangePasswordlessTokenForAuthTokenView(
    AbstractExchangePasswordlessTokenForAuthTokenView
):
    serializer_class = settings.SERIALIZERS.passwordless_email_token_exchange


class MobileExchangePasswordlessTokenForAuthTokenView(
    AbstractExchangePasswordlessTokenForAuthTokenView
):
    serializer_class = settings.SERIALIZERS.passwordless_mobile_token_exchange
