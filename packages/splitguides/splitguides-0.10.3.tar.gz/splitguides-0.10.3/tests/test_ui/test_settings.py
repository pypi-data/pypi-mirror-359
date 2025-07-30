from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QTimer

from ducktools.classbuilder.prefab import as_dict

from splitguides.settings import DesktopSettings
from splitguides.settings import DEFAULT_STATIC_FOLDER, DEFAULT_TEMPLATE_FOLDER

from splitguides.ui.color import rgba_to_qcolor
from splitguides.ui.settings_ui import SettingsDialog

test_settings = Path(__file__).parent / "settings.json"
temp_settings = Path(__file__).parent / "temp_settings.json"


# Default settings for each test
pytestmark = pytest.mark.usefixtures("clear_settings")


@pytest.fixture
def settings_ui(qtbot):
    settings = DesktopSettings.load()

    fake_hotkey_manager = MagicMock()

    settings_dialog = SettingsDialog(
        parent=None, settings=settings, hotkey_manager=fake_hotkey_manager
    )

    qtbot.add_widget(settings_dialog)

    qtbot.mouseDClick(settings_dialog.ui.hostname_edit, Qt.LeftButton)
    qtbot.keyClicks(settings_dialog.ui.hostname_edit, "TestHost")

    qtbot.mouseDClick(settings_dialog.ui.port_edit, Qt.LeftButton)
    qtbot.keyClicks(settings_dialog.ui.port_edit, "2112")

    qtbot.mouseDClick(settings_dialog.ui.previous_edit, Qt.LeftButton)
    qtbot.keyClicks(settings_dialog.ui.previous_edit, "1")

    qtbot.mouseDClick(settings_dialog.ui.advance_edit, Qt.LeftButton)
    qtbot.keyClicks(settings_dialog.ui.advance_edit, "3")

    qtbot.mouseDClick(settings_dialog.ui.separator_edit, Qt.LeftButton)
    qtbot.keyClicks(settings_dialog.ui.separator_edit, "/split")

    qtbot.mouseDClick(settings_dialog.ui.fontsize_edit, Qt.LeftButton)
    qtbot.mouseClick(settings_dialog.ui.fontsize_edit, Qt.LeftButton)
    qtbot.keyClicks(settings_dialog.ui.fontsize_edit, "25")

    qtbot.mouseDClick(settings_dialog.ui.textcolor_edit, Qt.LeftButton)
    qtbot.keyClicks(settings_dialog.ui.textcolor_edit, "#BBBBBBEE")

    qtbot.mouseDClick(settings_dialog.ui.bgcolor_edit, Qt.LeftButton)
    qtbot.keyClicks(settings_dialog.ui.bgcolor_edit, "#AAAAAA88")

    return settings, settings_dialog, fake_hotkey_manager


class TestSettings:
    # Test the Settings class
    def test_settings_with_file(self):
        """Check settings are read and updated from a settings file"""
        with patch.object(Path, "exists", return_value=True):
            s = DesktopSettings.load(test_settings)

        assert s.hostname == "fakehost"
        assert s.port == 12345
        assert s.split_separator == "/split"
        assert s.previous_splits == 1
        assert s.next_splits == 3
        assert s.font_size == 22
        assert s.font_color == "#000001ff"
        assert s.background_color == "#f1f8f1ff"
        assert s.full_template_path == Path("fake/html/folder/fakehtml.html")
        assert s.full_css_path == Path("fake/css/folder/fakecss.css")
        assert s.on_top
        assert s.width == 1000
        assert s.height == 1100
        assert s.notes_folder == "fake/documents/folder"

    def test_default_paths(self):
        """Test if the paths listed in the settings file do not exist that defaults are used"""
        s = DesktopSettings.load(test_settings)

        # Check they are not what is listed
        assert s.full_template_path != Path("fake/html/folder/fakehtml.html")
        assert s.full_css_path != Path("fake/css/folder/fakecss.css")
        # Check they are defaults
        assert s.full_template_path == DEFAULT_TEMPLATE_FOLDER / "desktop.html"
        assert s.full_css_path == DEFAULT_STATIC_FOLDER / "desktop.css"

    def test_save_load(self):
        s = DesktopSettings.load(test_settings)

        # Change the output file
        s.output_file = temp_settings
        s.save()

        s2 = DesktopSettings.load(temp_settings)

        for key in as_dict(s):
            assert as_dict(s)[key] == as_dict(s2)[key], key

        temp_settings.unlink()


class TestSettingsUI:
    def test_settings_ui_basic(self, qtbot, settings_ui):
        settings, settings_dialog, hotkey_mock = settings_ui

        button = settings_dialog.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)

        QTimer.singleShot(0, button.clicked)
        result = settings_dialog.exec()

        assert result == 1

        assert settings.hostname == "TestHost"
        assert settings.port == 2112
        assert settings.previous_splits == 1
        assert settings.next_splits == 3
        assert settings.split_separator == "/split"
        assert settings.font_size == 25
        assert settings.font_color == "#BBBBBBEE"
        assert settings.background_color == "#AAAAAA88"

    def test_settings_ui_cancel(self, qtbot, settings_ui):
        settings, settings_dialog, hotkey_mock = settings_ui
        button = settings_dialog.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)

        QTimer.singleShot(0, button.clicked)
        result = settings_dialog.exec()

        assert result == 0

        default_settings = DesktopSettings()

        assert settings.hostname == default_settings.hostname
        assert settings.port == default_settings.port
        assert settings.previous_splits == default_settings.previous_splits
        assert settings.next_splits == default_settings.next_splits
        assert settings.split_separator == default_settings.split_separator
        assert settings.font_size == default_settings.font_size
        assert settings.font_color == default_settings.font_color
        assert settings.background_color == default_settings.background_color

    def test_settings_ui_colorpicker_font(self, qtbot):
        """
        Test font color picker
        """
        settings = DesktopSettings.load()

        settings_dialog = SettingsDialog(
            parent=None, settings=settings, hotkey_manager=MagicMock()
        )

        qtbot.add_widget(settings_dialog)

        with patch.object(QtWidgets.QColorDialog, "getColor") as mock:
            fake_color = MagicMock()
            fake_color.isValid.return_value = True
            fake_color.name.return_value = "#EE012345"

            mock.return_value = fake_color

            qtbot.mouseClick(settings_dialog.ui.textcolor_button, Qt.LeftButton)

            mock.assert_called_with(
                rgba_to_qcolor(settings.font_color),
                parent=settings_dialog,
                title="Text Color",
                options=QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel,
            )

        assert settings_dialog.ui.textcolor_edit.text() == "#012345EE"

    def test_settings_ui_colorpicker_bg(self, qtbot):
        """
        Test BG color picker
        """
        settings = DesktopSettings.load()
        settings_dialog = SettingsDialog(
            parent=None, settings=settings, hotkey_manager=MagicMock()
        )

        qtbot.add_widget(settings_dialog)
        with patch.object(QtWidgets.QColorDialog, "getColor") as mock:
            fake_color = MagicMock()
            fake_color.isValid.return_value = True
            fake_color.name.return_value = "#AA456789"

            mock.return_value = fake_color

            qtbot.mouseClick(settings_dialog.ui.bgcolor_button, Qt.LeftButton)

            mock.assert_called_with(
                rgba_to_qcolor(settings.background_color),
                parent=settings_dialog,
                title="Background Color",
                options=QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel,
            )

        assert settings_dialog.ui.bgcolor_edit.text() == "#456789AA"
