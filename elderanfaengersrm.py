import time
import pynput                         # Manipulation der Tastenanschläge (Drucken von [verkaufen] z.B.)
import tkinter                        # Modul zum Öffnen und Erstellen von Fenstern (Grundstückseingabe)
import pyperclip                      # Manipulation der Zwischenablage
import threading                      # Thread für Kopier- und Druckfunktion
import webbrowser                     # Öffnen von Webadressen
from terminalausgaben import *        # Ausgaben auf dem Terminal
from win10toast import ToastNotifier  # Windows-Notification

global pause              # Wird True, falls der Befehl "pause" eingegeben wird. False, wenn "weiter" eingegeben wird.
global listener           # Der Thread (Zuhörer), der darauf wartet, dass [Einfg] gedrückt wird.
global kopier_thread      # Der Thread, der das Kopieren von Portbefehlen und Drucken von Schildzeilen regelt.
global grundstuecke       # Ist die Liste der Grundstücke.
global index              # Ist der Index in der Liste, dessen Grundstück gerade in der Zwischenablage ist.
global stop               # Wird True, falls das Programm stoppen soll (aber nicht unbedingt schließen).
global interne_clipboard  # Interner Speicher, der beim Pausieren zum Einsatz kommt.


# ==== Hilfsfunktionen für Tastaturhorchen und Kopierfunktionen ====


def on_release(key):
    if key == pynput.keyboard.Key.insert and not pause:
        return False


def wait_einfg():
    global listener
    with pynput.keyboard.Listener(on_release=on_release) as listener:
        listener.join()


def windows_notification(gs):
    details = "Befehl aktualisiert\nID: " + gs[0]
    ToastNotifier().show_toast("ElderAnfängerSRM", details, duration=8, icon_path="icon.ico")


def kopieren_und_drucken():
    global stop
    global index
    global grundstuecke

    for i, gs in enumerate(grundstuecke):
        index = i
        gs = gs[1:-1].split("\",\"")

        # Portbefehl
        wait_einfg()  # Warten auf [Einfg]
        if stop:      # Falls stop, verlasse die Methode und somit wird der kopier_thread beendet.
            return
        pyperclip.copy(gs[7])
        windows_notification(gs)
        if stop:
            return

        # [verkaufen]
        wait_einfg()
        if stop:
            return
        pynput.keyboard.Controller().type("[verkaufen]")

        # BuildingDave
        wait_einfg()
        if stop:
            return
        pynput.keyboard.Controller().type("BuildingDave")

    stop = True
    grundstuecke = []
    pyperclip.copy("")
    ToastNotifier().show_toast("ElderAnfängerSRM", "Fertig\nZwischenablage geleert", duration=8, icon_path="icon.ico")


def grundstuecke_ok():
    grundstuecke_copy = grundstuecke.copy()
    list_numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    for gs in grundstuecke_copy:
        try:
            # Auf die 8 Komponenten herunterbrechen
            gs = gs[1:-1].split("\",\"")

            # Komponenten 2, …, 7 auf Zahlen überprüfen.
            for i in range(1, 7):
                if not gs[i][0] in ["-"] + list_numbers:
                    return False
                for char in gs[i][1:]:
                    if char not in list_numbers:
                        return False

            # Komponente 1
            gs[0] = gs[0].split("-")
            if len(gs[0]) != 3:
                return False
            if gs[0][0] != "anf":
                return False
            for i in range(1, 3):
                for char in gs[0][i]:
                    if char not in list_numbers:
                        return False

            # Komponente 8
            gs[7] = gs[7].split(" ")
            if len(gs[7]) != 4:
                return False
            if gs[7][0] != "/tp":
                return False
            for i in range(1, 4):
                if not gs[7][i][0] in ["-"] + list_numbers:
                    return False
                for char in gs[7][i][1:]:
                    if char not in list_numbers:
                        return False

        except IndexError:
            return False

    return True


# ==== Hilfsfunktionen Fenster für Grundstückseingabe ====


def update_label(anzahl, textfeld):
    global grundstuecke
    inhalt = textfeld.get("1.0", tkinter.END).split("\n")
    inhalt = [zeile for zeile in inhalt if zeile != ""]
    grundstuecke = inhalt
    if grundstuecke_ok():
        anzahl.config(fg="black", text="Länge der Liste: " + str(len(inhalt)) + " Zeilen.")
    else:
        anzahl.config(fg="red", text="Die Liste enthält ungültige Zeilen.")


def reihenfolge_umkehren(textfeld):
    inhalt = textfeld.get("1.0", tkinter.END).split("\n")
    inhalt = [inhalt[len(inhalt) - i - 1] for i in range(len(inhalt)) if inhalt[len(inhalt) - i - 1] != ""]
    textfeld.delete("1.0", tkinter.END)
    textfeld.insert(tkinter.END, "\n".join(inhalt))


def speichern_beenden(fenster, textfeld):
    global grundstuecke
    grundstuecke = textfeld.get("1.0", tkinter.END).split("\n")
    grundstuecke = [zeile for zeile in grundstuecke if zeile != ""]
    fenster.destroy()


# ==== Befehle, die vom Nutzer eingegeben werden ====


def befehl_link_oeffnen():
    print_terminal_nachricht("ElderAnfaengerSRM", "Link")
    webbrowser.open_new_tab("git.eldercom.de")


def befehl_grundstuecke_eingeben():
    if not stop:
        print_terminal_nachricht("ElderAnfaengerSRM", "Fenster bei Fluss")
        return
    print_terminal_nachricht("ElderAnfaengerSRM", "Fenster öffnen")

    # Fenstereigenschaften
    fenster = tkinter.Tk()
    fenster.geometry("1280x720")
    fenster.iconbitmap("icon.ico")
    fenster.title("ElderAnfaengerSRM - Grundstückseingabe")

    # Textfeld und Scrollbar
    textfeld = tkinter.Text(fenster, font=("Courier", 12), bg="black", fg="white", insertbackground="white")
    textfeld.insert(tkinter.END, "\n".join(grundstuecke))
    scrollbar = tkinter.Scrollbar(fenster)
    textfeld.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=textfeld.yview)

    # Buttons und Label mit der Anzahl Listeneinträge
    speichern = tkinter.Button(fenster, text="Speichern und Beenden", font=16,
                               command=lambda: speichern_beenden(fenster, textfeld))
    umkehren = tkinter.Button(fenster, text="Reihenfolge umkehren", font=16,
                              command=lambda: reihenfolge_umkehren(textfeld))
    updaten = tkinter.Button(fenster, text="Länge aktualisieren", font=16,
                             command=lambda: update_label(anzahl, textfeld))
    anzahl = tkinter.Label(fenster, text="Länge der Liste: ", font=16)

    # Setzen der Steuerelemente und Starten.
    textfeld.place(x=50, y=30, height=620, width=1180)
    scrollbar.place(x=30, y=30, height=620, width=20)
    speichern.place(x=955, y=670, height=30, width=275)
    umkehren.place(x=50, y=670, height=30, width=225)
    updaten.place(x=325, y=670, height=30, width=225)
    anzahl.place(x=600, y=670)
    fenster.mainloop()

    # Nach Schließen des Fensters
    print_terminal_nachricht("ElderAnfaengerSRM", "Fenster geschlossen")


def befehl_start():
    global stop
    global pause
    global index
    global kopier_thread

    if not stop:
        print_terminal_nachricht("ElderAnfaengerSRM", "Start bei Start")
    elif not grundstuecke:
        print_terminal_nachricht("ElderAnfaengerSRM", "Start bei Leer")
    elif not grundstuecke_ok():
        print_terminal_nachricht("ElderAnfaengerSRM", "Start bei GSFehler")
    else:
        print_terminal_nachricht("ElderAnfaengerSRM", "Start")
        stop = False
        pause = False
        kopier_thread = threading.Thread(target=kopieren_und_drucken)
        kopier_thread.start()
        index = 0
        print_terminal_nachricht("ElderAnfaengerSRM", "Gestartet")


def befehl_pause():
    global pause
    global interne_clipboard

    if stop:
        print_terminal_nachricht("ElderAnfaengerSRM", "Pause bei Stopp")
    elif pause:
        print_terminal_nachricht("ElderAnfaengerSRM", "Pause bei Pause")
    else:
        pause = True
        interne_clipboard = pyperclip.paste()
        print_terminal_nachricht("ElderAnfaengerSRM", "Pause", [interne_clipboard])


def befehl_weiter():
    global pause

    if stop:
        print_terminal_nachricht("ElderAnfaengerSRM", "Weiter bei Stopp")
    elif not pause:
        print_terminal_nachricht("ElderAnfaengerSRM", "Weiter bei Fluss")
    else:
        pause = False
        pyperclip.copy(interne_clipboard)
        print_terminal_nachricht("ElderAnfaengerSRM", "Weiter", [interne_clipboard])


def befehl_status():
    if stop:
        print_terminal_nachricht("ElderAnfaengerSRM", "Status bei Stopp")
    else:
        print("")
        print_terminal_nachricht("ElderAnfaengerSRM", "Status")
        print_hrule()

        for i, grundstueck in enumerate(grundstuecke):
            if i < index:
                print(Fore.LIGHTBLACK_EX + grundstueck + Fore.RESET)
            elif i == index:
                print(Fore.LIGHTGREEN_EX + grundstueck + Fore.RESET)
            else:
                print(grundstueck)

        print("")
        print_terminal_nachricht("ElderAnfaengerSRM", "Status ToDo",
                                 [str(len(grundstuecke) - index), str(int(100 * index / len(grundstuecke)))])
        print_hrule()
        print("")


def befehl_stop():
    global stop
    global grundstuecke

    if stop:
        print_terminal_nachricht("ElderAnfaengerSRM", "Stop bei Gestoppt")
    else:
        print_terminal_nachricht("ElderAnfaengerSRM", "Stop")
        stop = True
        listener.stop()       # Den Tastaturzuhörer beenden.
        kopier_thread.join()  # Warten, dass der Kopierthread beendet ist.
        grundstuecke = []     # Liste der Grundstücke leeren.
        pyperclip.copy("")    # Zwischenablage leeren.
        print_terminal_nachricht("ElderAnfaengerSRM", "Gestoppt")


def befehl_exit():
    global stop

    print_programm_wird_beendet()
    if not stop:
        stop = True
        listener.stop()       # Den Tastaturzuhörer beenden.
        kopier_thread.join()  # Warten, dass der Kopierthread beendet ist.


def befehl_hilfe():
    print("")
    print_hilfe("ElderAnfaengerSRM")
    print("")


# ==== Hauptprogramm / Befehlsentgegennahme ====


def main():
    konfigurieren()
    print_beschreibung("ElderAnfaengerSRM")
    print("")
    print_hilfe("ElderAnfaengerSRM")
    print("")

    global stop
    stop = True
    global grundstuecke
    grundstuecke = []

    while True:
        reaktionszeit = time.time()
        befehl = input("Gebe den nächsten Befehl ein: ")
        reaktionszeit = time.time() - reaktionszeit
        if reaktionszeit <= 0.01:
            print_fehler_nachricht("ElderAnfaengerSRM", "Eingabe bei Aufforderung")
        elif befehl == "link öffnen":
            befehl_link_oeffnen()
        elif befehl == "grundstücke eingeben":
            befehl_grundstuecke_eingeben()
        elif befehl == "start":
            befehl_start()
        elif befehl == "pause":
            befehl_pause()
        elif befehl == "weiter":
            befehl_weiter()
        elif befehl == "status":
            befehl_status()
        elif befehl == "stop":
            befehl_stop()
        elif befehl == "exit":
            befehl_exit()
            break
        elif befehl == "hilfe":
            befehl_hilfe()
        else:
            print_befehl_invalide_gebe_hilfe_ein()

    print_programm_ist_beendet()


if __name__ == "__main__":
    main()
