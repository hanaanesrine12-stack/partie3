"""
TP1 SSAD — Partie 3 : Mots de passe
====================================
"""

import time
import tkinter as tk
from tkinter import ttk, messagebox
import itertools

import passwords
from passwords import caesar  # Import to access get_secrets


# ===========================================================================
# Helpers
# ===========================================================================
def set_text(box, text):
    box.config(state="normal")
    box.delete("1.0", "end")
    box.insert("1.0", text)
    box.config(state="disabled")


def update_monitor(box, text):
    box.config(state="normal")
    box.delete("1.0", "end")
    box.insert("1.0", text)
    box.config(state="disabled")
    box.update_idletasks()


def fmt_duration(seconds):
    """Formatage uniforme d'une durée mesurée."""
    if seconds < 1e-3:
        return "%.3f ms" % (seconds * 1e3)
    if seconds < 1:
        return "%.1f ms" % (seconds * 1e3)
    if seconds < 60:
        return "%.2f s" % seconds
    if seconds < 3600:
        return "%.1f min" % (seconds / 60)
    return "%.1f h" % (seconds / 3600)


CASES = passwords.CASES


# ===========================================================================
# Fenêtre principale
# ===========================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TP1 SSAD — Partie 3 : Simulateur de sécurité")
        self.geometry("1200x700")
        self.minsize(1100, 650)

        self.account = {
            "username": None, "password": None, "record": None,
            "iterations": 200_000, "case": None
        }

        self._build_header()
        self._build_body()

    def _build_header(self):
        header = ttk.Frame(self, padding=(10, 6))
        header.pack(fill="x")
        ttk.Label(header, text="MOTS DE PASSE",
                  font=("TkDefaultFont", 14, "bold")).pack(side="left")

        ttk.Button(header, text="↺ Réinitialiser",
                   command=self.reset_demo).pack(side="right", padx=10)

    def _build_body(self):
        body = ttk.Frame(self, padding=(6, 0))
        body.pack(fill="both", expand=True)

        body.columnconfigure(0, weight=1, uniform="col")
        body.columnconfigure(1, weight=1, uniform="col")
        body.columnconfigure(2, weight=1, uniform="col")
        body.rowconfigure(0, weight=1)

        self.zone_a = ZoneA(body, self)
        self.zone_a.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.zone_b = ZoneB(body, self)
        self.zone_b.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        self.zone_c = ZoneC(body, self)
        self.zone_c.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)

    def require_account(self):
        if self.account["record"] is None:
            messagebox.showinfo("Aucun compte", "Créez d'abord un compte dans la zone A.")
            return False
        return True

    def reset_demo(self):
        self.account = {"username": None, "password": None, "record": None, "iterations": 200_000, "case": None}
        self.zone_a.reset()
        self.zone_b.reset()
        self.zone_c.reset()


# ===========================================================================
# ZONE A — Le serveur
# ===========================================================================
class ZoneA(ttk.LabelFrame):
    def __init__(self, parent, app):
        super().__init__(parent, text="ZONE A — Le serveur", padding=8)
        self.app = app

        ttk.Label(self, text="Cas du TP :", font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        self.case_var = tk.StringVar(value=list(CASES)[0])
        case_frame = ttk.Frame(self)
        case_frame.pack(fill="x", pady=(2, 6))
        for name in CASES:
            ttk.Radiobutton(case_frame, text=name, value=name,
                            variable=self.case_var,
                            command=self.on_case_change).pack(anchor="w")

        form = ttk.Frame(self)
        form.pack(fill="x", pady=(4, 4))
        ttk.Label(form, text="Utilisateur :").grid(row=0, column=0, sticky="w")
        self.username = ttk.Entry(form, width=22)
        self.username.insert(0, "etudiant")
        self.username.grid(row=0, column=1, sticky="ew", padx=4)

        ttk.Label(form, text="Mot de passe :").grid(row=1, column=0, sticky="w", pady=2)
        self.password = ttk.Entry(form, width=22, show="•")
        self.password.insert(0, "111")
        self.password.grid(row=1, column=1, sticky="ew", padx=4, pady=2)
        ttk.Button(form, text="👁", width=3,
                   command=self.toggle_show).grid(row=1, column=2)

        self.strength_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", maximum=100)
        self.strength_bar.pack(fill="x", pady=(6, 2))
        self.strength_label = ttk.Label(self, text="—", foreground="#555")
        self.strength_label.pack(anchor="w")

        self.problems_box = tk.Text(self, height=3, wrap="word", state="disabled",
                                    font=("TkDefaultFont", 8), bg="#f6f6f6")
        self.problems_box.pack(fill="x", pady=(4, 6))

        ttk.Button(self, text="Créer le compte", command=self.create_account).pack(fill="x", pady=(0, 8))

        # -----------------------------------------------------------
        # BASE DE DONNÉES (STOCKAGE)
        # -----------------------------------------------------------
        ttk.Label(self, text="Base de données (stockage) :", font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        storage = ttk.Frame(self)
        storage.pack(fill="x", pady=(2, 6))

        self.storage_labels = {}
        rows = [
            ("Algorithme", "algo"),
            ("Sel (Salt)", "salt"),
            ("Chiffré (DB)", "hash"),
            ("Master (Hors DB)", "master"),
            ("Pepper (Hors DB)", "pepper"),
            ("Mot de passe clair", "clear")
        ]

        for i, (label, key) in enumerate(rows):
            ttk.Label(storage, text=label + " :").grid(row=i, column=0, sticky="w")
            v = ttk.Label(storage, text="—", font=("Courier", 8), foreground="#333")
            v.grid(row=i, column=1, sticky="w", padx=4)
            self.storage_labels[key] = v

        ttk.Label(self, text="🔒 Le mot de passe en clair n'est JAMAIS stocké.",
                  foreground="#a00", font=("TkDefaultFont", 8, "italic")).pack(anchor="w")

        self.password.bind("<KeyRelease>", lambda e: self.update_strength())
        self.update_strength()

    def on_case_change(self):
        charset, length = CASES[self.case_var.get()]
        if length is not None:
            self.password.delete(0, "end")
            self.password.insert(0, charset[1] * length)
        self.update_strength()

    def toggle_show(self):
        self.password.config(show="" if self.password.cget("show") else "•")

    def update_strength(self):
        pwd = self.password.get()
        charset, length = CASES[self.case_var.get()]

        if length is not None:
            problems = []
            if len(pwd) != length:
                problems.append("Doit contenir exactement %d caractères." % length)
            if not set(pwd) <= set(charset):
                problems.append("Caractères autorisés : %s" % charset)

            case_num = "1" if length == 3 else "2"
            if problems:
                self.strength_bar["value"] = 0
                self.strength_label.config(text="❌ Non conforme", foreground="#b00")
                set_text(self.problems_box, "")
                self.problems_box.config(state="normal")
                for p in problems:
                    self.problems_box.insert("end", "• " + p + "\n")
                self.problems_box.config(state="disabled")
            else:
                self.strength_bar["value"] = 100
                self.strength_label.config(text="✅ Conforme au cas %s" % case_num, foreground="#070")
                set_text(self.problems_box, "")
            return

        if not pwd:
            self.strength_bar["value"] = 0
            self.strength_label.config(text="—", foreground="#555")
            set_text(self.problems_box, "")
            return

        problems = passwords.strength_problems(pwd)
        score = max(0, 100 - 12 * len(problems))
        self.strength_bar["value"] = score
        if problems:
            self.strength_label.config(text="❌ Faible — %d problème(s)" % len(problems), foreground="#b00")
        else:
            self.strength_label.config(text="✅ Robuste", foreground="#070")

        set_text(self.problems_box, "")
        if problems:
            self.problems_box.config(state="normal")
            for p in problems:
                self.problems_box.insert("end", "• " + p + "\n")
            self.problems_box.config(state="disabled")

    def create_account(self):
        username = self.username.get().strip()
        password = self.password.get()
        if not username or not password:
            messagebox.showwarning("Compte", "Renseignez l'utilisateur et le mot de passe.")
            return

        charset, length = CASES[self.case_var.get()]

        if length is not None:
            if len(password) != length or not set(password) <= set(charset):
                messagebox.showwarning("Mot de passe invalide",
                                       "Le mot de passe ne respecte pas les règles du cas sélectionné.")
                return

        if length is None:
            problems = passwords.strength_problems(password)
            if problems:
                if not messagebox.askyesno("Mot de passe faible",
                                           "La politique signale :\n- " + "\n- ".join(problems) +
                                           "\n\nCréer le compte quand même ?"):
                    return

        record = passwords.make_record(password)
        self.app.account.update({
            "username": username,
            "password": password,
            "record": record,
            "iterations": record["iterations"],
            "case": self.case_var.get()
        })

        # --- FIXING THE DISPLAY ---
        # 1. Salt is bytes -> display as hex
        salt_hex = record["salt"].hex()
        # 2. Ciphertext is bytes -> display as hex (prevents UI freezing on weird chars)
        hash_hex = record["hash"].hex()
        # 3. Get Master and Pepper
        master_hex, pepper_hex = caesar.get_secrets()

        self.storage_labels["algo"].config(text=record["algo"])
        self.storage_labels["salt"].config(text=salt_hex)
        self.storage_labels["hash"].config(text=hash_hex)
        self.storage_labels["master"].config(text=master_hex, foreground="#0055aa")
        self.storage_labels["pepper"].config(text=pepper_hex, foreground="#0055aa")
        self.storage_labels["clear"].config(text="JAMAIS STOCKÉ", foreground="#a00", font=("TkDefaultFont", 8, "bold"))

        self.app.zone_b.on_account_ready(username)

    def reset(self):
        self.username.delete(0, "end")
        self.username.insert(0, "etudiant")
        self.password.delete(0, "end")
        self.password.insert(0, "111")
        for v in self.storage_labels.values():
            v.config(text="—", foreground="#333")
        self.update_strength()


# ===========================================================================
# ZONE B — L'utilisateur légitime
# ===========================================================================
class ZoneB(ttk.LabelFrame):
    def __init__(self, parent, app):
        super().__init__(parent, text="ZONE B — L'utilisateur légitime", padding=8)
        self.app = app
        self.guard = None

        ttk.Label(self, text="Connexion :", font=("TkDefaultFont", 9, "bold")).pack(anchor="w")

        form = ttk.Frame(self)
        form.pack(fill="x", pady=4)
        ttk.Label(form, text="Utilisateur :").grid(row=0, column=0, sticky="w")
        self.username = ttk.Entry(form, width=20)
        self.username.grid(row=0, column=1, sticky="ew", padx=4)

        ttk.Label(form, text="Mot de passe :").grid(row=1, column=0, sticky="w", pady=2)
        self.password = ttk.Entry(form, width=20)
        self.password.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        ttk.Button(self, text="Se connecter", command=self.login).pack(fill="x", pady=(4, 6))

        ttk.Label(self, text="Temps de vérification (César) :", font=("TkDefaultFont", 9, "bold")).pack(anchor="w",
                                                                                                        pady=(6, 0))
        self.time_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", maximum=100)
        self.time_bar.pack(fill="x", pady=2)
        self.time_label = ttk.Label(self, text="—", font=("Courier", 11, "bold"))
        self.time_label.pack(anchor="w")

        self.time_card = tk.Text(self, height=5, wrap="word", state="disabled",
                                 font=("TkDefaultFont", 9), bg="#f0f8f0")
        self.time_card.pack(fill="x", pady=(4, 6))

        ttk.Label(self, text="État du compte :", font=("TkDefaultFont", 9, "bold")).pack(anchor="w", pady=(6, 0))
        self.lock_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", maximum=100)
        self.lock_bar.pack(fill="x", pady=2)
        self.lock_label = ttk.Label(self, text="—", foreground="#555")
        self.lock_label.pack(anchor="w")

    def on_account_ready(self, username):
        self.username.delete(0, "end")
        self.username.insert(0, username)
        self.password.delete(0, "end")
        self.guard = passwords.LoginGuard(self.app.account["record"], max_attempts=3, lockout_seconds=30)
        self.lock_label.config(text="Aucun verrouillage actif.", foreground="#555")
        self.lock_bar["value"] = 0

    def login(self):
        if not self.app.require_account(): return

        entered_user = self.username.get().strip()
        expected_user = self.app.account.get("username")
        if entered_user != expected_user:
            self.lock_label.config(text="Identifiants incorrects.", foreground="#b00")
            self.lock_bar["value"] = 0
            return

        if self.guard is None:
            self.guard = passwords.LoginGuard(self.app.account["record"], max_attempts=3, lockout_seconds=30)

        attempt = self.password.get()
        start = time.perf_counter()
        result = self.guard.try_login(attempt)
        elapsed = time.perf_counter() - start

        attempts_per_s = int(1 / elapsed) if elapsed > 0 else 0
        card = (
                "Temps de vérification : %s\n"
                "→ Imperceptible pour l'utilisateur.\n\n"
                "Si un attaquant volait la base, à cette vitesse\n"
                "il ne ferait que ~%d essais/seconde."
                % (fmt_duration(elapsed), attempts_per_s)
        )
        set_text(self.time_card, card)

        self.time_bar["value"] = min(100, elapsed * 1000)
        self.time_label.config(text=fmt_duration(elapsed))

        if "verrouillé" in result:
            self.lock_label.config(text="🔒 " + result, foreground="#b00")
            self._animate_lockout()
        else:
            self.lock_label.config(text=result, foreground="#555")
            self.lock_bar["value"] = 0

    def _animate_lockout(self):
        lock_s = 30
        steps = 60
        step_ms = (lock_s * 1000) // steps

        def tick(i):
            if i <= 0:
                self.lock_bar["value"] = 0
                self.lock_label.config(text="Verrouillage expiré.", foreground="#070")
                return
            self.lock_bar["value"] = (i / steps) * 100
            self.lock_label.config(text="🔒 Verrouillé — %d s restantes" % int(lock_s * i / steps), foreground="#b00")
            self.after(step_ms, tick, i - 1)

        tick(steps)

    def reset(self):
        self.username.delete(0, "end")
        self.password.delete(0, "end")
        self.guard = None
        self.time_bar["value"] = 0
        self.time_label.config(text="—")
        set_text(self.time_card, "")
        self.lock_bar["value"] = 0
        self.lock_label.config(text="—", foreground="#555")



# ===========================================================================
# ZONE C — L'attaquant
# ===========================================================================
class ZoneC(ttk.LabelFrame):
    def __init__(self, parent, app):
        super().__init__(parent, text="ZONE C — L'attaquant (Hors-ligne)", padding=8)
        self.app = app

        ttk.Label(self, text="L'attaquant a volé la base de données\net attaque le chiffré César directement.",
                  foreground="#555", font=("TkDefaultFont", 8, "italic")).pack(anchor="w", pady=(0, 6))

        ttk.Label(self, text="Méthode :", font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        self.method = tk.StringVar(value="dictionary")
        self.m_frame = ttk.Frame(self)
        self.m_frame.pack(fill="x", pady=2)
        for label, val in [("Dictionnaire", "dictionary"), ("Force brute", "brute"), ("Combinée", "combined")]:
            ttk.Radiobutton(self.m_frame, text=label, value=val, variable=self.method).pack(anchor="w")

        ttk.Button(self, text="Lancer l'attaque", command=self.run_attack).pack(fill="x", pady=(12, 4))

        ttk.Label(self, text="Moniteur d'attaque :", font=("TkDefaultFont", 9, "bold")).pack(anchor="w", pady=(6, 0))
        self.monitor = tk.Text(self, height=6, wrap="word", state="disabled",
                               font=("Courier", 8), bg="#1a1a1a", fg="#7fd67f")
        self.monitor.pack(fill="x")

        self.result_card = tk.Text(self, height=5, wrap="word", state="disabled",
                                   font=("TkDefaultFont", 8), bg="#fff6f6")
        self.result_card.pack(fill="x", pady=(4, 0))

    def _reset_cards(self):
        set_text(self.monitor, "")
        set_text(self.result_card, "")

    def run_attack(self):
        if not self.app.require_account(): return
        target_clear = self.app.account.get("password")
        case_name = self.app.account.get("case")

        if not target_clear or not case_name: return

        charset, length = CASES[case_name]
        if length is None: length = len(target_clear)

        method = self.method.get()
        self._reset_cards()
        self._run_offline_attack(target_clear, charset, length, method)

    def _run_offline_attack(self, target_clear, charset, length, method):
        target_hash = passwords.fingerprint(target_clear)
        MAX_ATTEMPTS = 10_000_000
        TIME_LIMIT = 10.0  # Maximum 10 seconds for brute force

        found = None
        tries = 0
        used = method
        stopped_by_time = False

        wordlist = None
        if method in ("dictionary", "combined"):
            wordlist = passwords.build_wordlist()

        start = time.perf_counter()

        # ----------- PHASE 1 : DICTIONNAIRE -----------
        if wordlist is not None:
            used = "dictionnaire"
            for i, candidate in enumerate(wordlist, 1):
                tries += 1
                if passwords.fingerprint(candidate) == target_hash:
                    found = candidate
                    break

                if tries % 100 == 0:
                    snap = time.perf_counter() - start
                    update_monitor(self.monitor,
                                   "Statut   : En cours (%s)\n"
                                   "Essai    : %s\n"
                                   "Durée    : %s" % (used, "{:,}".format(tries), fmt_duration(snap)))
                    self.update()  # Keep UI responsive

            if found is not None:
                elapsed = time.perf_counter() - start
                update_monitor(self.monitor,
                               "Statut   : Terminé\nEssai    : %s\nDurée    : %s"
                               % ("{:,}".format(tries), fmt_duration(elapsed)))
                self._show_result(found, tries, elapsed, used)
                return

        # ----------- PHASE 2 : FORCE BRUTE -----------
        if method in ("brute", "combined") and found is None:
            used = "force brute" if method == "brute" else "combinée (force brute)"

            for tup in itertools.product(charset, repeat=length):
                tries += 1
                candidate = "".join(tup)

                if passwords.fingerprint(candidate) == target_hash:
                    found = candidate
                    break

                # Check time limit and update UI every 10,000 attempts
                if tries % 10000 == 0:
                    snap = time.perf_counter() - start

                    # --- STOP IF 10 SECONDS REACHED ---
                    if snap >= TIME_LIMIT:
                        stopped_by_time = True
                        break

                    update_monitor(self.monitor,
                                   "Statut   : En cours (%s)\n"
                                   "Essai    : %s\n"
                                   "Candidat : %s\n"
                                   "Durée    : %s" % (used, "{:,}".format(tries), candidate, fmt_duration(snap)))
                    self.update()  # Keep UI responsive

                if tries >= MAX_ATTEMPTS:
                    break

        elapsed = time.perf_counter() - start

        # Final monitor update
        status_text = "Arrêté (limite de temps)" if stopped_by_time else "Terminé"
        update_monitor(self.monitor,
                       "Statut   : %s\nEssai    : %s\nDurée    : %s"
                       % (status_text, "{:,}".format(tries), fmt_duration(elapsed)))

        self._show_result(found, tries, elapsed, used, stopped_by_time)

    def _show_result(self, found, tries, elapsed, method, stopped_by_time=False):
        if found is None:
            if stopped_by_time:
                text = ("⏳ INTROUVABLE (Temps écoulé)\n"
                        "Méthode : %s\n"
                        "Essais  : %s\n"
                        "Durée   : %s\n"
                        "La force brute a été arrêtée car elle a atteint la limite de 10 secondes."
                        % (method, "{:,}".format(tries), fmt_duration(elapsed)))
            else:
                text = ("⏳ INTROUVABLE (Espace épuisé)\n"
                        "Méthode : %s\n"
                        "Essais  : %s\n"
                        "Durée   : %s\n"
                        "(L'espace de recherche entier a été testé.)"
                        % (method, "{:,}".format(tries), fmt_duration(elapsed)))
        else:
            text = ("✅ TROUVÉ\n"
                    "Mot de passe : '%s'\n"
                    "Méthode      : %s\n"
                    "Essais       : %s\n"
                    "Durée        : %s"
                    % (found, method, "{:,}".format(tries), fmt_duration(elapsed)))
        set_text(self.result_card, text)

    def reset(self):
        self.method.set("dictionary")
        self._reset_cards()
# ===========================================================================
# Lancement
# ===========================================================================
def main():
    App().mainloop()


if __name__ == "__main__":
    main()