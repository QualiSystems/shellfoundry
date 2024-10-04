#!/usr/bin/python

from unittest.mock import MagicMock, patch
from urllib.error import URLError

from pyfakefs import fake_filesystem_unittest

from shellfoundry.models.install_config import InstallConfig
from shellfoundry.utilities.archive_creator import ArchiveCreator
from shellfoundry.utilities.driver_generator import DriverGenerator

from tests.asserts import assertFileDoesNotExist, assertFileExists


class TestDriverGenerator(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_driver_generated_successfully(self):
        self.fs.create_file("nut-shell/dist/NutShell.zip", contents="ZIP")

        self.fs.create_file(
            "nut-shell/temp/data_model.py", contents="python data model content"
        )

        ArchiveCreator.make_archive(
            "nut-shell/temp/data-model", "zip", "nut-shell/temp"
        )

        driver_generator = DriverGenerator()
        config = InstallConfig(
            "TEST-HOST",
            9000,
            "user",
            "pwd",
            "Global",
            "author",
            "online_mode",
            "template_location",
            "github_login",
            "github_password",
        )

        with patch(
            "shellfoundry.utilities.driver_generator.PackagingRestApiClient.login"
        ) as mock_rest:
            rest_client_mock = MagicMock()
            rest_client_mock._token = "TEST-TOKEN"
            mock_rest.return_value = rest_client_mock

            with patch("shellfoundry.utilities.driver_generator.post") as post_mock:

                with open("nut-shell/temp/data-model.zip", "rb") as data_model_file:
                    file_content = data_model_file.read()

                response = MagicMock()
                response.status_code = 200
                response.content = file_content
                post_mock.return_value = response

                # Act
                driver_generator.generate_driver(
                    cloudshell_config=config,
                    destination_path="nut-shell/src",
                    package_full_path="nut-shell/dist/NutShell.zip",
                    shell_filename="NutShell.zip",
                    shell_name="NutShell",
                )

        # Assert
        assertFileExists(self, "nut-shell/src/data_model.py")
        self.assertEqual(post_mock.call_args[1]["headers"]["Authorization"], "Basic TEST-TOKEN")

    def test_error_displayed_when_driver_generation_returns_error_code(self):
        self.fs.create_file("nut-shell/dist/NutShell.zip", contents="ZIP")

        self.fs.create_file(
            "nut-shell/temp/data_model.py", contents="python data model content"
        )

        ArchiveCreator.make_archive(
            "nut-shell/temp/data-model", "zip", "nut-shell/temp"
        )

        driver_generator = DriverGenerator()
        config = InstallConfig(
            "TEST-HOST",
            9000,
            "user",
            "pwd",
            "Global",
            "author",
            "online_mode",
            "template_location",
            "github_login",
            "github_password",
        )

        with patch(
            "shellfoundry.utilities.driver_generator.PackagingRestApiClient"
        ) as mock_rest:
            rest_client_mock = MagicMock()
            rest_client_mock.token = "TEST-TOKEN"
            mock_rest.return_value = rest_client_mock

            with patch("shellfoundry.utilities.driver_generator.post") as post_mock:
                response = MagicMock()
                response.status_code = 500
                response.content = "Error occurred"
                post_mock.return_value = response

                with patch(
                    "shellfoundry.utilities.driver_generator.click"
                ) as click_mock:
                    click_mock.echo = MagicMock()

                    # Act
                    driver_generator.generate_driver(
                        cloudshell_config=config,
                        destination_path="nut-shell/src",
                        package_full_path="nut-shell/dist/NutShell.zip",
                        shell_filename="NutShell.zip",
                        shell_name="NutShell",
                    )

                self.assertTrue(click_mock.echo.called, "click should have been called")

        # Assert
        assertFileDoesNotExist(self, "nut-shell/src/data_model.py")

    def test_error_displayed_when_failed_to_connect_to_cloudshell_server(self):
        self.fs.create_file("nut-shell/dist/NutShell.zip", contents="ZIP")

        self.fs.create_file(
            "nut-shell/temp/data_model.py", contents="python data model content"
        )

        ArchiveCreator.make_archive(
            "nut-shell/temp/data-model", "zip", "nut-shell/temp"
        )

        driver_generator = DriverGenerator()
        config = InstallConfig(
            "TEST-HOST",
            9000,
            "user",
            "pwd",
            "Global",
            "author",
            "online_mode",
            "template_location",
            "github_login",
            "github_password",
        )

        with patch(
            "shellfoundry.utilities.driver_generator.PackagingRestApiClient.login"
        ) as mock_rest:
            mock_rest.side_effect = URLError("connected failed")

            with patch("shellfoundry.utilities.driver_generator.click") as click_mock:
                echo_mock = MagicMock()
                click_mock.echo = echo_mock

                # Act
                try:
                    driver_generator.generate_driver(
                        cloudshell_config=config,
                        destination_path="nut-shell/src",
                        package_full_path="nut-shell/dist/NutShell.zip",
                        shell_filename="NutShell.zip",
                        shell_name="NutShell",
                    )
                except URLError:
                    pass

                self.assertTrue(echo_mock.called, "click should have been called")
                self.assertEqual(
                    echo_mock.call_args[0][0],
                    "Login to CloudShell failed. Please verify the credentials in cloudshell_config.yml",  # noqa: E501
                )

        # Assert
        assertFileDoesNotExist(self, "nut-shell/src/data_model.py")
