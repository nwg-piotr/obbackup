import os
import gi
import zipfile
import ntpath

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import values


def select_file():
    dialog = Gtk.FileChooserDialog("Please choose a file", None,
                                   Gtk.FileChooserAction.OPEN,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    # Let's start from the default location
    dialog.set_current_folder(values.backup_dir)

    add_filters(dialog)

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        values.restore_path_display_field.set_text(dialog.get_filename().strip())
        set_restore_button_state()
        check_backup_content(dialog.get_filename())

    elif response == Gtk.ResponseType.CANCEL:
        print("Cancel clicked")

    dialog.destroy()


def add_filters(dialog):
    filter_text = Gtk.FileFilter()
    filter_text.set_name("zip files")
    filter_text.add_mime_type("application/zip")
    dialog.add_filter(filter_text)


class Handler:
    def on_destroy(self, *args):
        Gtk.main_quit()

    def on_close_clicked(self, button):
        Gtk.main_quit()

    def on_select_file_clicked(self, button):
        print("Restore clicked")
        select_file()

    def on_backup_clicked(self, status_line):
        backup(status_line)

    def on_restore_clicked(self, status_line):
        restore(status_line)

    def checkbox_toggled_rc_xml(self, checkbox):
        values.backup_rc_xml = checkbox.get_active()
        set_backup_button_state()

    def checkbox_toggled_autostart(self, checkbox):
        values.backup_autostart = checkbox.get_active()
        set_backup_button_state()

    def checkbox_toggled_menu_xml(self, checkbox):
        values.backup_menu_xml = checkbox.get_active()
        set_backup_button_state()

    def checkbox_toggled_tint2rc(self, checkbox):
        values.backup_tint2rc = checkbox.get_active()
        set_backup_button_state()


def determine_paths():
    values.home = os.getenv("HOME")
    values.path_to_rc_xml = values.home + values.path_to_rc_xml
    values.path_to_menu_xml = values.home + values.path_to_menu_xml
    values.path_to_autostart = values.home + values.path_to_autostart
    values.path_to_tint2rc = values.home + values.path_to_tint2rc
    values.path_to_backup = values.home + "/.obbackup/obbackup.zip"


def set_backup_button_state():
    if values.backup_button is not None:
        values.backup_button.set_sensitive(
            values.backup_rc_xml or values.backup_menu_xml or values.backup_autostart or values.backup_tint2rc)


def set_restore_button_state():
    if os.path.isfile(values.path_to_backup):
        values.restore_button.set_sensitive(True)
        check_backup_content(values.path_to_backup)


def set_backup_path_label():
    if os.path.isfile(values.path_to_backup):
        values.input_filename_label.set_text(values.path_to_backup)
    else:
        values.input_filename_label.set_text('Default backup file not found')


def backup(status_line):
    filename = values.output_filename_entry.get_text() + '.zip'

    files_to_compress = []
    if values.backup_rc_xml:
        files_to_compress.append(values.path_to_rc_xml)
    if values.backup_menu_xml:
        files_to_compress.append(values.path_to_menu_xml)
    if values.backup_autostart:
        files_to_compress.append(values.path_to_autostart)
    if values.backup_tint2rc:
        files_to_compress.append(values.path_to_tint2rc)

    zip_file = zipfile.ZipFile(values.backup_dir + '/' + filename, 'w')

    for file in files_to_compress:
        zip_file.write(os.path.join(file), ntpath.basename(file), compress_type=zipfile.ZIP_DEFLATED)

    zip_file.close()

    values.path_to_backup = values.backup_dir + '/' + filename

    status_line.set_text("Selected files saved as " + values.backup_dir + '/' + filename)
    set_backup_path_label()
    set_restore_button_state()


def restore(status_line):
    if values.path_to_backup is not None:
        backup_file = zipfile.ZipFile(values.path_to_backup)

        restored = []

        if values.checkbox_restore_rc_xml.get_active():
            backup_file.extract("rc.xml", values.path_to_rc_xml.strip("rc.xml"))
            restored.append('rc.xml')

        if values.checkbox_restore_autostart.get_active():
            try:
                backup_file.extract("autostart.sh", values.path_to_autostart.strip("autostart.sh"))
                restored.append('autostart.sh')
            except:
                backup_file.extract("autostart", values.path_to_autostart.strip("autostart"))
                restored.append('autostart')

        if values.checkbox_restore_menu_xml.get_active():
            backup_file.extract("menu.xml", values.path_to_menu_xml.strip("menu.xml"))
            restored.append('menu.xml')

        if values.checkbox_restore_tint2rc.get_active():
            backup_file.extract("tint2rc", values.backup_dir)
            restored.append('tint2rc')

        status_line.set_text('Restored files: ' + str(restored)[1:len(str(restored)) - 1])


def check_backup_content(which_file):
    if values.path_to_backup is not None:

        values.checkbox_restore_rc_xml.set_active(False)
        values.checkbox_restore_rc_xml.set_sensitive(False)

        values.checkbox_restore_autostart.set_active(False)
        values.checkbox_restore_autostart.set_sensitive(False)

        values.checkbox_restore_menu_xml.set_active(False)
        values.checkbox_restore_menu_xml.set_sensitive(False)

        values.checkbox_restore_tint2rc.set_active(False)
        values.checkbox_restore_tint2rc.set_sensitive(False)

        backup_file = zipfile.ZipFile(which_file)

        for file in backup_file.namelist():

            if file == "rc.xml":
                values.exists_rc_xml = True
                values.checkbox_restore_rc_xml.set_active(True)
                values.checkbox_restore_rc_xml.set_sensitive(True)

            elif file == "menu.xml":
                values.exists_menu_xml = True
                values.checkbox_restore_menu_xml.set_active(True)
                values.checkbox_restore_menu_xml.set_sensitive(True)

            elif file == "autostart":
                values.exists_autostart = True
                values.checkbox_restore_autostart.set_active(True)
                values.checkbox_restore_autostart.set_sensitive(True)
                values.checkbox_restore_autostart.set_label("autostart")

            elif file == "autostart.sh":
                values.exists_autostart = True
                values.checkbox_restore_autostart.set_active(True)
                values.checkbox_restore_autostart.set_sensitive(True)
                values.checkbox_restore_autostart.set_label("autostart.sh")

            elif file == "tint2rc":
                values.exists_tint2rc = True
                values.checkbox_restore_tint2rc.set_active(True)
                values.checkbox_restore_tint2rc.set_sensitive(True)


def main():
    determine_paths()

    values.backup_dir = values.home + values.backup_dir
    if not os.path.isdir(values.backup_dir):
        os.makedirs(values.backup_dir)

    builder = Gtk.Builder()
    builder.add_from_file("glade/main_window.glade")
    builder.connect_signals(Handler())

    window = builder.get_object("main_window")

    if os.path.isfile(values.path_to_rc_xml):
        builder.get_object("checkbox_backup_rc_xml").set_label(values.path_to_rc_xml)
        builder.get_object("checkbox_backup_rc_xml").set_active(True)
    else:
        builder.get_object("checkbox_backup_rc_xml").set_sensitive(False)

    if os.path.isfile(values.path_to_autostart):
        builder.get_object("checkbox_backup_autostart").set_label(values.path_to_autostart)
        builder.get_object("checkbox_backup_autostart").set_active(True)
    else:
        values.path_to_autostart = values.path_to_autostart + ".sh"
        if os.path.isfile(values.path_to_autostart):
            builder.get_object("checkbox_backup_autostart").set_label(values.path_to_autostart)
            builder.get_object("checkbox_backup_autostart").set_active(True)
        else:
            builder.get_object("checkbox_backup_autostart").set_sensitive(False)

    if os.path.isfile(values.path_to_menu_xml):
        builder.get_object("checkbox_backup_menu_xml").set_label(values.path_to_menu_xml)
        builder.get_object("checkbox_backup_menu_xml").set_active(True)
    else:
        builder.get_object("checkbox_backup_menu_xml").set_sensitive(False)

    if os.path.isfile(values.path_to_tint2rc):
        builder.get_object("checkbox_backup_tint2rc").set_label(values.path_to_tint2rc)
        builder.get_object("checkbox_backup_tint2rc").set_active(True)
    else:
        builder.get_object("checkbox_backup_tint2rc").set_sensitive(False)

    values.restore_path_display_field = builder.get_object("restore_path_display_field")
    values.restore_button = builder.get_object("button_restore")
    values.backup_button = builder.get_object("button_backup")
    values.output_filename_entry = builder.get_object("output_filename_entry")
    values.input_filename_label = builder.get_object("restore_path_display_field")

    values.checkbox_restore_rc_xml = builder.get_object("checkbox_restore_rc_xml")
    values.checkbox_restore_autostart = builder.get_object("checkbox_restore_autostart")
    values.checkbox_restore_menu_xml = builder.get_object("checkbox_restore_menu_xml")
    values.checkbox_restore_tint2rc = builder.get_object("checkbox_restore_tint2rc")

    set_backup_path_label()
    set_restore_button_state()

    window.show_all()

    Gtk.main()


if __name__ == "__main__":
    main()
