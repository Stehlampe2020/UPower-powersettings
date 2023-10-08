#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

transl = {
    'de': (
        'Dieses Programm sollte als Rootbenutzer (meist UID=0) ausgeführt werden!',
        'Akkugrenzwerte',
        'Schwacher Akku (%)',
        'Kritisch schwacher Akku (%)',
        'Eingriff (%)',
        'Speichern',
        'Die Einstellungen wurden gespeichert!'
    ),
    'sv': (
        'Programmet skulle köras som rootanvändaren (typiskt UID=0)!',
        'Batteritröskelvärden',
        'Lågt batteri (%)',
        'Kritiskt lågt batteri (%)',
        'Intervention (%)',
        'Spara',
        'Inställningarna sparades!'
    ),
    'en': (
        'Note that this program probably needs to run as root (typically UID=0) to function properly!',
        'Battery thresholds',
        'Low battery (%)',
        'Critically low battery (%)',
        'Intervention (%)',
        'Save',
        'The settings have been saved!'
    )
}

try:
    with open(f"{os.getenv('HOME')}/.config/upower-powersettings.cfg", 'r') as settingsfile:
        for line in settingsfile.read().split('\n'):
            if line in (f'Lang={l}' for l in transl.keys()):
                lang = line[-2:] # The last two characters
                break
        else:
            lang = os.getenv('LANG')[:2] if os.getenv('LANG', 'C')!='C' else 'en'
except FileNotFoundError:
    with open(f"{os.getenv('HOME')}/.config/upower-powersettings.cfg", 'w') as settingsfile:
        lang = os.getenv('LANG')[:2] if os.getenv('LANG', 'C') != 'C' else 'en'
        settingsfile.write(f"Lang={lang}")

if lang not in transl.keys():
    lang = 'en'

if os.geteuid()!=0:
    print(transl[lang][0]) #TODO: Remove once warning banner is able to appear!

class PercentageForm(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app, title=transl[lang][1])

        # Skapa huvudvyn
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(self.box)

        # Lägg till en varningsbanner (initialt dold)
        self.warning_bar = Gtk.InfoBar()
        self.warning_bar.set_name(transl[lang][0])
        self.warning_bar.connect("response", self.hide_warning)
        self.warning_bar.set_revealed(True) #FIXME: Warning doesn't show up no matter what!

        # Skapa fält för PercentageLow
        self.percentage_low_label = Gtk.Label(label=transl[lang][2])
        self.percentage_low_spin = Gtk.SpinButton()
        self.percentage_low_spin.set_range(0, 100)
        self.percentage_low_spin.set_value(20)
        self.box.append(self.percentage_low_label)
        self.box.append(self.percentage_low_spin)

        # Skapa fält för PercentageCritical
        self.percentage_critical_label = Gtk.Label(label=transl[lang][3])
        self.percentage_critical_spin = Gtk.SpinButton()
        self.percentage_critical_spin.set_range(0, 100)
        self.percentage_critical_spin.set_value(8)
        self.box.append(self.percentage_critical_label)
        self.box.append(self.percentage_critical_spin)

        # Skapa fält för PercentageAction
        self.percentage_action_label = Gtk.Label(label=transl[lang][4])
        self.percentage_action_spin = Gtk.SpinButton()
        self.percentage_action_spin.set_range(0, 100)
        self.percentage_action_spin.set_value(5)
        self.box.append(self.percentage_action_label)
        self.box.append(self.percentage_action_spin)

        # Skapa en "Spara!"-knapp
        self.save_button = Gtk.Button(label=transl[lang][5])
        self.save_button.connect("clicked", self.save_values)
        self.box.append(self.save_button)

    def save_values(self, button):
        try:
            # Hämta värden från nummerfälten
            percentage_low = self.percentage_low_spin.get_value()
            percentage_critical = self.percentage_critical_spin.get_value()
            percentage_action = self.percentage_action_spin.get_value()

            # Skapa en dictionary med värdena
            settings = {
                'PercentageLow': percentage_low,
                'PercentageCritical': percentage_critical,
                'PercentageAction': percentage_action
            }

            # Skapa ett nytt fönster för "Sparad!"-meddelandet
            saved_window = Gtk.Window(title=transl[lang][1])

            # Skapa en behållare (Box) för meddelandetexten
            message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            saved_label = Gtk.Label(label=transl[lang][6])
            message_box.append(saved_label)

            # Skapa en 'OK'-knapp
            ok_button = Gtk.Button(label="OK")
            ok_button.connect("clicked", (lambda x: self.destroy()))
            message_box.append(ok_button)

            # Lägg till behållaren i fönstret
            saved_window.set_child(message_box)

            # Visa det nya fönstret
            saved_window.show()
        except Exception as err:
            self.destroy()
            exit(-1)

    def hide_warning(self, widget, response_id):
        # Dölj varningsbanner när användaren stänger den
        if response_id == Gtk.ResponseType.CLOSE:
            self.warning_bar.set_revealed(False)

class PercentageFormApp(Gtk.Application):

    def __init__(self):
        super().__init__()

    def do_activate(self):
        window = PercentageForm(self)
        window.show()

    def do_startup(self):
        Gtk.Application.do_startup(self)

app = PercentageFormApp()
exit_status = app.run([])
