from colorama import *
import configparser
init()

PLUGIN_COL = Fore.CYAN            # Schriftfarbe der Plugin-Namen (ElderHilfeTools etc.).
RAHMEN_COL = Fore.MAGENTA         # Schriftfarbe von Tabellenrahmen.
FEHLER_COL = Fore.LIGHTRED_EX     # Schriftfarbe von Fehlernachrichten.
BEFEHL_COL = Fore.LIGHTYELLOW_EX  # Schriftfarbe von Befehlen, die in Hinweis- und Hilfetexten stehen.
TERMINAL_COL = Fore.LIGHTCYAN_EX  # Schriftfarbe der Ausgaben auf dem Terminal.
ZEILEN_LAENGE = 120               # Zeilenlänge der Tabelle.

config = configparser.ConfigParser()
config.read("terminalausgaben.ini", encoding="utf-8")


# ==== Hilfsfunktionen für Ausgaben ====

def setze_farbcodes(text, standardfarbe=Fore.RESET):
    # Farbcodes \[Farbe]...[Farbe]\ werden übernommen.
    text = text.replace("\\[F]", FEHLER_COL).replace("[F]\\", standardfarbe)
    text = text.replace("\\[B]", BEFEHL_COL).replace("[B]\\", standardfarbe)
    text = text.replace("\\[P]", PLUGIN_COL).replace("[P]\\", standardfarbe)
    text = text.replace("\\[T]", TERMINAL_COL).replace("[T]\\", standardfarbe)
    return standardfarbe + text


def entferne_farbcodes(text):
    # Farbcodes werden alle entfernt.
    text = text.replace(FEHLER_COL, "")
    text = text.replace(BEFEHL_COL, "")
    text = text.replace(PLUGIN_COL, "")
    text = text.replace(TERMINAL_COL, "")
    text = text.replace(Fore.RESET, "")
    return text


def get_umbrueche_index(text, max_laenge):
    text_unformatiert = entferne_farbcodes(text)

    # Index des Umbruches bestimmen für den Text ohne Farbcodes.
    if "\n" in text_unformatiert[:max_laenge + 1]:
        umbruch_unformatiert = text_unformatiert[:max_laenge + 1].find("\n")
    elif len(text_unformatiert) <= max_laenge:
        umbruch_unformatiert = len(text_unformatiert)
    else:
        umbruch_unformatiert = text_unformatiert[:max_laenge + 1].rfind(" ")

    # Bestimmen des Index für den Umbruch des normalen Textes.
    i = 0
    umbruch = umbruch_unformatiert
    for char in text_unformatiert[:umbruch_unformatiert]:
        if char != text[i]:
            list_of_colors = [PLUGIN_COL, FEHLER_COL, BEFEHL_COL, TERMINAL_COL, Fore.RESET]
            for color in list_of_colors:
                if color in text[i:] and text[i:].index(color) == 0:
                    i = i + len(color)
                    umbruch = umbruch + len(color)
                    break
        i = i + 1

    return [umbruch, umbruch_unformatiert]


def erstelle_tabelle(text):
    print(RAHMEN_COL + "+" + ("=" * (ZEILEN_LAENGE - 2)) + "+")

    aufzaehlung = False                        # Wenn eine Zeile in der Konfigurationsdatei mit \* beginnt.
    neue_zeile_in_terminalausgaben_ini = True  # Zeilenumbruch in der Konfigurationsdatei

    while text != "":
        # Prüfen, ob die nächste Zeile in der Konfigdatei ein Aufzählungspunkt ist.
        if neue_zeile_in_terminalausgaben_ini:
            if text[:2] == "\\*":
                aufzaehlung = True
                text = text[2:]
            else:
                aufzaehlung = False

        # Nächste Ausgabe-Zeile schreiben. Dazu gibt ‘umbruch’ den Index an, bis zu dem ‘text’ ausgegeben wird.
        # ‘umbruch_unformatiert’ ist der Index, bis zu dem ‘text’ formatiert ausgegene wird, wenn die Farbcodes
        # entfernt wären.
        if aufzaehlung:
            [umbruch, umbruch_unformatiert] = get_umbrueche_index(text, max_laenge=ZEILEN_LAENGE - 15)
            leere = ZEILEN_LAENGE - umbruch_unformatiert - 11
            if neue_zeile_in_terminalausgaben_ini:
                print(RAHMEN_COL + "|    " + Fore.RESET + "   • " + text[:umbruch] + RAHMEN_COL + (" " * leere) + "|")
            else:
                print(RAHMEN_COL + "|    " + Fore.RESET + "     " + text[:umbruch] + RAHMEN_COL + (" " * leere) + "|")
        else:
            [umbruch, umbruch_unformatiert] = get_umbrueche_index(text, max_laenge=ZEILEN_LAENGE - 10)
            leere = ZEILEN_LAENGE - umbruch_unformatiert - 6
            print(RAHMEN_COL + "|    " + Fore.RESET + text[:umbruch] + RAHMEN_COL + (" " * leere) + "|")
        neue_zeile_in_terminalausgaben_ini = False

        # Falls der Umbruch in der Ausgabe wegen eines Umbruches in der Konfigdatei bedingt war, wird die Flag für
        # eine neue Zeile in der Konfigdatei auf True gesetzt.
        if len(text) > umbruch and text[umbruch] == "\n":
            neue_zeile_in_terminalausgaben_ini = True
        text = text[umbruch + 1:]

    print(RAHMEN_COL + "+" + ("=" * (ZEILEN_LAENGE - 2)) + "+" + Fore.RESET)


# ==== Standardausgaben ====

def print_hrule():
    print(TERMINAL_COL + ("=" * ZEILEN_LAENGE) + Fore.RESET)


def print_befehl_nur_nach_aufforderung():
    print_fehler_nachricht("Standardausgaben", "Eingabe (nur nach Aufforderung)")


def print_befehl_invalide_gebe_hilfe_ein():
    print_fehler_nachricht("Standardausgaben", "Eingabe (fehlerhaft, hilfe eingeben)")


def print_programm_wird_beendet():
    print_terminal_nachricht("Standardausgaben", "Programm wird beendet")


def print_programm_ist_beendet():
    print_terminal_nachricht("Standardausgaben", "Programm ist beendet")


# ==== Individuelle Ausgaben von Plugins (müssen in Konfig-Datei stehen) ====

def print_fehler_nachricht(plugin, schluessel, args=None):
    text = config[plugin][schluessel]

    if args is None:
        args = []

    for arg in args:
        text = text.replace("\\[IN]\\", arg, 1)
    print(setze_farbcodes(text, FEHLER_COL) + Fore.RESET)


def print_terminal_nachricht(plugin, schluessel, args=None):
    text = config[plugin][schluessel]

    if args is None:
        args = []

    for arg in args:
        text = text.replace("\\[IN]\\", arg, 1)
    print(setze_farbcodes(text, TERMINAL_COL) + Fore.RESET)


def print_hilfe(plugin):
    inhalt = setze_farbcodes(config[plugin]["Hilfe"], Fore.RESET)
    erstelle_tabelle(inhalt)


def print_beschreibung(plugin):
    inhalt = setze_farbcodes("Willkommen bei \\[P]" + plugin + "[P]\\.\n" + config[plugin]["Beschreibung"], Fore.RESET)
    erstelle_tabelle(inhalt)


# ==== Lesen der Konfigurationsdatei ====

def to_color_code(farbeingabe):
    if farbeingabe.lower() == "türkis":
        return Fore.CYAN
    elif farbeingabe.lower() == "magenta":
        return Fore.MAGENTA
    elif farbeingabe.lower() == "grün":
        return Fore.GREEN
    elif farbeingabe.lower() == "gelb":
        return Fore.YELLOW
    elif farbeingabe.lower() == "rot":
        return Fore.RED
    elif farbeingabe.lower() == "blau":
        return Fore.BLUE
    elif farbeingabe.lower() == "helltürkis":
        return Fore.LIGHTCYAN_EX
    elif farbeingabe.lower() == "hellmagenta":
        return Fore.LIGHTMAGENTA_EX
    elif farbeingabe.lower() == "hellgrün":
        return Fore.LIGHTGREEN_EX
    elif farbeingabe.lower() == "hellgelb":
        return Fore.LIGHTYELLOW_EX
    elif farbeingabe.lower() == "hellrot":
        return Fore.LIGHTRED_EX
    elif farbeingabe.lower() == "hellblau":
        return Fore.LIGHTBLUE_EX
    else:
        print(Fore.RED + "Schwerer Fehler: " + farbeingabe + " ist ungültig.")
        return "FEHLER"


def konfigurieren():
    global PLUGIN_COL
    if to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Pluginnamen"]) == "FEHLER":
        print(Fore.RED + "Das Programm wird mit dem Defaultwert türkis für Pluginnamen gestartet.")
    else:
        PLUGIN_COL = to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Pluginnamen"])

    global RAHMEN_COL
    if to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Tabellenrahmen"]) == "FEHLER":
        print(Fore.RED + "Das Programm wird mit dem Defaultwert magenta für Tabellenrahmen gestartet.")
    else:
        RAHMEN_COL = to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Tabellenrahmen"])

    global FEHLER_COL
    if to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Fehlerausgaben"]) == "FEHLER":
        print(Fore.RED + "Das Programm wird mit dem Defaultwert hellrot für Fehlernachrichten gestartet.")
    else:
        FEHLER_COL = to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Fehlernachrichten"])

    global BEFEHL_COL
    if to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Eingabebefehle"]) == "FEHLER":
        print(Fore.RED + "Das Programm wird mit dem Defaultwert hellgelb für Befehle gestartet.")
    else:
        BEFEHL_COL = to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Befehle in Texten"])

    global TERMINAL_COL
    if to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Terminalausgaben"]) == "FEHLER":
        print(Fore.RED + "Das Programm wird mit dem Defaultwert helltürkis für Terminalausgaben gestartet.")
    else:
        TERMINAL_COL = to_color_code(config["Farben und Zeilenlänge von Tabellen"]["Terminalausgaben"])

    global ZEILEN_LAENGE
    try:
        ZEILEN_LAENGE = int(config["Farben und Zeilenlänge von Tabellen"]["Zeilenlänge"])
    except ValueError:
        print(Fore.RED + "Schwerer Fehler: Die angegebene Zeilenlänge muss eine Zahl sein.")
        print(Fore.RED + "Das Programm wird mit dem Defaultwert 120 gestartet.")
    else:
        ZEILEN_LAENGE = int(config["Farben und Zeilenlänge von Tabellen"]["Zeilenlänge"])
        if ZEILEN_LAENGE < 50:
            print(Fore.RED + "Schwerer Fehler: Die angegebene Zeilenläge muss mindestens 50 betragen.")
            print(Fore.RED + "Das Programm wird mit dem Defaultwert 120 gestartet.")
