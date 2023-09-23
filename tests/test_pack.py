from click.testing import CliRunner
from pytest_mock.plugin import MockerFixture

from choco.constants import (NUSPEC_FIELD_AUTHORS, NUSPEC_FIELD_DESCRIPTION, NUSPEC_FIELD_ID,
                             NUSPEC_FIELD_TAGS, NUSPEC_FIELD_VERSION)
from choco.main import main as choco
from choco.templates import NUSPEC_TEMPLATE


def test_pack_not_exist(runner: CliRunner, mocker: MockerFixture) -> None:
    glob_mock = mocker.patch('choco.packaging.glob.glob')
    glob_mock.return_value = []
    run = runner.invoke(choco, ('pack', 'okay-name'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0


def test_pack_too_many_nuspec(runner: CliRunner, mocker: MockerFixture) -> None:
    glob_mock = mocker.patch('choco.packaging.glob.glob')
    glob_mock.return_value = ['a.nuspec', 'b.nuspec']
    run = runner.invoke(choco, ('pack', 'okay-name'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0


class FakeRoot:
    class FakeTag:
        def __init__(self, text: str):
            self.text = text

    def find(self, tag_name: str) -> FakeTag:
        if tag_name == NUSPEC_FIELD_ID:
            return FakeRoot.FakeTag('okay-name')
        if tag_name == NUSPEC_FIELD_VERSION:
            return FakeRoot.FakeTag('1.0.0')
        if tag_name == NUSPEC_FIELD_AUTHORS:
            return FakeRoot.FakeTag('Author One')
        if tag_name == NUSPEC_FIELD_DESCRIPTION:
            return FakeRoot.FakeTag('Description')
        if tag_name == NUSPEC_FIELD_TAGS:
            return FakeRoot.FakeTag(' tag1 ')
        raise ValueError(f'Unknown tag name: {tag_name}')


def test_pack_normal(runner: CliRunner, mocker: MockerFixture) -> None:
    append_mock = mocker.patch('choco.packaging.append_dir_to_zip_recursive')
    chdir_mock = mocker.patch('choco.packaging.chdir')
    parse_xml_mock = mocker.patch('choco.packaging.parse_xml')
    zip_mock = mocker.patch('choco.packaging.zipfile.ZipFile')
    glob_mock = mocker.patch('choco.packaging.glob.glob')
    glob_mock.return_value = ['a.nuspec']
    NUSPEC_TEMPLATE.safe_substitute(package_id='okay-name')
    parse_xml_mock.return_value.getroot.return_value = FakeRoot()
    run = runner.invoke(choco, ('pack', 'okay-name'))
    assert run.exit_code == 0
    assert chdir_mock.call_count == 1
    assert zip_mock.return_value.__enter__.return_value.writestr.call_count == 3
    assert append_mock.call_count == 1
