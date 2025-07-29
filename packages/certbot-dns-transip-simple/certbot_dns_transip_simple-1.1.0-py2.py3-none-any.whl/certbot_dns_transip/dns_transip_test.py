"""Tests for certbot_dns_transip.dns_transip."""

import unittest

import mock

from certbot.compat import os
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

FAKE_USER = "remoteuser"
FAKE_PW = "password"


class AuthenticatorTest(
    test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest
):
    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        from certbot_dns_transip.dns_transip import Authenticator

        path = os.path.join(self.tempdir, "file.ini")
        dns_test_common.write(
            {
                "transip_username": FAKE_USER,
                "transip_api_key": FAKE_PW,
            },
            path,
        )

        super(AuthenticatorTest, self).setUp()
        self.config = mock.MagicMock(
            transip_credentials=path, transip_propagation_seconds=0
        )  # don't wait during tests

        self.auth = Authenticator(self.config, "transip")

        self.mock_client = mock.MagicMock()
        # _get_transip_client | pylint: disable=protected-access
        self.auth._get_transip_client = mock.MagicMock(return_value=self.mock_client)

    def test_perform(self):
        self.auth.perform([self.achall])

        expected = [
            mock.call.add_dns_entries(
                mock.ANY, mock.ANY
            )
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_cleanup(self):
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        expected = [
            mock.call.remove_dns_entries(
                mock.ANY, mock.ANY
            )
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
