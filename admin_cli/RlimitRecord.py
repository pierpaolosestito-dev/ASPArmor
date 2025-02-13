class RlimitRecord:
    def __init__(self, generic_apparmor_profile, flag, n):
        """
        Inizializza un'istanza di RlimitRecord.

        :param generic_apparmor_profile: Profilo generico di AppArmor associato
        :param flag: Il flag RLIMIT (ad esempio CPU, MEMORY)
        :param n: Il valore associato al flag
        """
        self.generic_apparmor_profile = generic_apparmor_profile
        self.flag = flag
        self.n = n

    def __str__(self):
        """
        Restituisce una rappresentazione leggibile dell'oggetto.
        """
        return f"RlimitRecord(Profile: {self.generic_apparmor_profile}, Flag: {self.flag}, Value: {self.n})"

    def __repr__(self):
        """
        Restituisce una rappresentazione più dettagliata dell'oggetto per il debug.
        """
        return f"RlimitRecord(generic_apparmor_profile='{self.generic_apparmor_profile}', flag='{self.flag}', n={self.n})"



