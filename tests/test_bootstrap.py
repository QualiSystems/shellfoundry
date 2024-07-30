#!/usr/bin/python
import traceback
import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from shellfoundry.bootstrap import (
    config,
    delete,
    dist,
    extend,
    generate,
    get_templates,
    install,
    list,
    new,
    pack,
    show,
    version,
)
from shellfoundry.utilities import GEN_ONE, GEN_TWO, LAYER_ONE, NO_FILTER


class TestBootstrap(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    @patch("shellfoundry.bootstrap.pkg_resources")
    def test_version(self, test_dist):
        obj = MagicMock()
        obj.version = "shellfoundry_version"
        test_dist.get_distribution = MagicMock(return_value=obj)
        result = self.runner.invoke(version)

        assert result.exit_code == 0
        assert result.output == "shellfoundry version shellfoundry_version\n"

    @patch("shellfoundry.bootstrap.ListCommandExecutor")
    def test_list_all(self, test_list_executor_class):
        with patch(
            "shellfoundry.decorators.version_check.is_index_version_greater_than_current",  # noqa: E501
            return_value=(False, True),
        ):
            result = self.runner.invoke(list, ["--all"])
            if result.exception:
                traceback.print_exception(*result.exc_info)

            assert result.exit_code == 0
            test_list_executor_class.assert_called_once_with(NO_FILTER)
            test_list_executor_class.return_value.list.assert_called_once()

    @patch("shellfoundry.bootstrap.ListCommandExecutor")
    def test_list_gen_one(self, test_list_executor_class):

        with patch(
            "shellfoundry.decorators.version_check.is_index_version_greater_than_current",  # noqa: E501
            return_value=(False, True),
        ):

            result = self.runner.invoke(list, ["--gen1"])
            if result.exception:
                traceback.print_exception(*result.exc_info)

            assert result.exit_code == 0
            test_list_executor_class.assert_called_once_with(GEN_ONE)
            test_list_executor_class.return_value.list.assert_called_once()

    @patch("shellfoundry.bootstrap.ListCommandExecutor")
    def test_list_gen_two(self, test_list_executor_class):
        with patch(
            "shellfoundry.decorators.version_check.is_index_version_greater_than_current",  # noqa: E501
            return_value=(False, True),
        ):
            result = self.runner.invoke(list, ["--gen2"])
            if result.exception:
                traceback.print_exception(*result.exc_info)

            assert result.exit_code == 0
            test_list_executor_class.assert_called_once_with(GEN_TWO)
            test_list_executor_class.return_value.list.assert_called_once()

    @patch("shellfoundry.bootstrap.ListCommandExecutor")
    def test_list_layer_one(self, test_list_executor_class):
        with patch(
            "shellfoundry.decorators.version_check.is_index_version_greater_than_current",  # noqa: E501
            return_value=(False, True),
        ):
            result = self.runner.invoke(list, ["--layer1"])
            if result.exception:
                traceback.print_exception(*result.exc_info)

            assert result.exit_code == 0
            test_list_executor_class.assert_called_once_with(LAYER_ONE)
            test_list_executor_class.return_value.list.assert_called_once()

    @patch("shellfoundry.bootstrap.NewCommandExecutor")
    def test_new_only_name(self, new_command_executor):
        with patch(
            "shellfoundry.decorators.version_check.is_index_version_greater_than_current",  # noqa: E501
            return_value=(False, True),
        ):
            result = self.runner.invoke(new, ["test_shell"])
            if result.exception:
                traceback.print_exception(*result.exc_info)

            assert result.exit_code == 0
            new_command_executor.return_value.new.assert_called_once_with(
                "test_shell", "gen2/resource", None, "3"
            )

    @patch("shellfoundry.bootstrap.NewCommandExecutor")
    def test_new(self, new_command_executor):
        with patch(
            "shellfoundry.decorators.version_check.is_index_version_greater_than_current",  # noqa: E501
            return_value=(False, True),
        ):
            result = self.runner.invoke(
                new,
                ["test_shell", "--template", "template_name", "--version", "version"],
            )
            if result.exception:
                traceback.print_exception(*result.exc_info)

            assert result.exit_code == 0
            new_command_executor.return_value.new.assert_called_once_with(
                "test_shell", "template_name", "version", "3"
            )

    @patch("shellfoundry.bootstrap.NewCommandExecutor")
    def test_new_with_python_version(self, new_command_executor):
        with patch(
            "shellfoundry.decorators.version_check.is_index_version_greater_than_current",  # noqa: E501
            return_value=(False, True),
        ):
            result = self.runner.invoke(
                new,
                [
                    "test_shell",
                    "--template",
                    "template_name",
                    "--version",
                    "version",
                    "--python",
                    "3",
                ],
            )
            if result.exception:
                traceback.print_exception(*result.exc_info)

            assert result.exit_code == 0
            new_command_executor.return_value.new.assert_called_once_with(
                "test_shell", "template_name", "version", "3"
            )

    @patch("shellfoundry.bootstrap.PackCommandExecutor")
    def test_pack(self, test_pack_executor):
        result = self.runner.invoke(pack)
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_pack_executor.return_value.pack.assert_called_once()

    @patch("shellfoundry.bootstrap.PackCommandExecutor")
    @patch("shellfoundry.bootstrap.InstallCommandExecutor")
    def test_install(self, test_install_executor, test_pack_executor):
        result = self.runner.invoke(install)
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_pack_executor.return_value.pack.assert_called_once()
        test_install_executor.return_value.install.assert_called_once()

    @patch("shellfoundry.bootstrap.PackCommandExecutor")
    @patch("shellfoundry.bootstrap.InstallCommandExecutor")
    def test_install_pack_failed(self, test_install_executor, test_pack_executor):
        test_pack_executor.return_value.pack.side_effect = Exception("some error")
        result = self.runner.invoke(install)
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 1
        test_pack_executor.return_value.pack.assert_called_once()
        test_install_executor.return_value.install.assert_not_called()

    @patch("shellfoundry.bootstrap.PackCommandExecutor")
    @patch("shellfoundry.bootstrap.DistCommandExecutor")
    def test_dist(self, test_dist_executor, test_pack_executor):
        result = self.runner.invoke(dist)
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_pack_executor.return_value.pack.assert_called_once()
        test_dist_executor.return_value.dist.assert_called_once()

    @patch("shellfoundry.bootstrap.PackCommandExecutor")
    @patch("shellfoundry.bootstrap.DistCommandExecutor")
    def test_dist_pack_failed(self, test_dist_executor, test_pack_executor):
        test_pack_executor.return_value.pack.side_effect = Exception("some error")
        result = self.runner.invoke(dist)
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 1
        test_pack_executor.return_value.pack.assert_called_once()
        test_dist_executor.return_value.dist.assert_not_called()

    @patch("shellfoundry.bootstrap.PackCommandExecutor")
    @patch("shellfoundry.bootstrap.GenerateCommandExecutor")
    def test_generate(self, test_generate_executor, test_pack_executor):
        result = self.runner.invoke(generate)
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_pack_executor.return_value.pack.assert_called_once()
        test_generate_executor.return_value.generate.assert_called_once()

    @patch("shellfoundry.bootstrap.PackCommandExecutor")
    @patch("shellfoundry.bootstrap.GenerateCommandExecutor")
    def test_generate_pack_failed(self, test_generate_executor, test_pack_executor):
        test_pack_executor.return_value.pack.side_effect = Exception("some error")
        result = self.runner.invoke(generate)
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 1
        test_pack_executor.return_value.pack.assert_called_once()
        test_generate_executor.return_value.generate.assert_not_called()

    @patch("shellfoundry.bootstrap.ConfigCommandExecutor")
    def test_config_get_global(self, test_config_class):
        result = self.runner.invoke(config)
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_config_class.assert_called_once_with(True)
        test_config_class.return_value.config.assert_called_once_with(
            (None, None), None
        )

    @patch("shellfoundry.bootstrap.ConfigCommandExecutor")
    def test_config_get_local(self, test_config_class):
        result = self.runner.invoke(config, ["--local"])
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_config_class.assert_called_once_with(False)
        test_config_class.return_value.config.assert_called_once_with(
            (None, None), None
        )

    @patch("shellfoundry.bootstrap.ConfigCommandExecutor")
    def test_config_add_key(self, test_config_class):
        result = self.runner.invoke(config, ["new_key", "new_value"])
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_config_class.assert_called_once_with(True)
        test_config_class.return_value.config.assert_called_once_with(
            ("new_key", "new_value"), None
        )

    @patch("shellfoundry.bootstrap.ConfigCommandExecutor")
    def test_config_remove_key(self, test_config_class):
        result = self.runner.invoke(config, ["--remove", "key_to_remove"])
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_config_class.assert_called_once_with(True)
        test_config_class.return_value.config.assert_called_once_with(
            (None, None), "key_to_remove"
        )

    @patch("shellfoundry.bootstrap.ShowCommandExecutor")
    def test_show(self, test_show_class):
        result = self.runner.invoke(show, ["template name"])
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_show_class.return_value.show.assert_called_once_with("template name")

    @patch("shellfoundry.bootstrap.ExtendCommandExecutor")
    def test_extend(self, test_extend_class):
        result = self.runner.invoke(extend, ["source shell location"])
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_extend_class.return_value.extend.assert_called_once_with(
            "source shell location", ()
        )

    @patch("shellfoundry.bootstrap.ExtendCommandExecutor")
    def test_extend_add_attributes(self, test_extend_class):
        result = self.runner.invoke(
            extend,
            ["source shell location", "--attribute", "attr_1", "--attribute", "attr2"],
        )
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_extend_class.return_value.extend.assert_called_once_with(
            "source shell location", ("attr_1", "attr2")
        )

    @patch("shellfoundry.bootstrap.GetTemplatesCommandExecutor")
    def test_get_templates(self, test_get_templates_class):
        result = self.runner.invoke(get_templates, ["cs_version"])
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_get_templates_class.return_value.get_templates.assert_called_once_with(
            "cs_version", None
        )

    @patch("shellfoundry.bootstrap.GetTemplatesCommandExecutor")
    def test_get_templates_with_output_folder(self, test_get_templates_class):
        result = self.runner.invoke(
            get_templates, ["cs_version", "--output_dir", "some output folder"]
        )
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_get_templates_class.return_value.get_templates.assert_called_once_with(
            "cs_version", "some output folder"
        )

    @patch("shellfoundry.bootstrap.DeleteCommandExecutor")
    def test_delete(self, test_delete_class):
        result = self.runner.invoke(delete, ["shell_name_to_delete"])
        if result.exception:
            traceback.print_exception(*result.exc_info)

        assert result.exit_code == 0
        test_delete_class.return_value.delete.assert_called_once_with(
            "shell_name_to_delete"
        )
