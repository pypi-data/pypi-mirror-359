
###########################################################################
#
# LICENSE AGREEMENT
#
# Copyright (c) 2014-2024 joonis new media, Thimo Kraemer
#
# 1. Recitals
#
# joonis new media, Inh. Thimo Kraemer ("Licensor"), provides you
# ("Licensee") the program "PyFinTech" and associated documentation files
# (collectively, the "Software"). The Software is protected by German
# copyright laws and international treaties.
#
# 2. Public License
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this Software, to install and use the Software, copy, publish
# and distribute copies of the Software at any time, provided that this
# License Agreement is included in all copies or substantial portions of
# the Software, subject to the terms and conditions hereinafter set forth.
#
# 3. Temporary Multi-User/Multi-CPU License
#
# Licensor hereby grants to Licensee a temporary, non-exclusive license to
# install and use this Software according to the purpose agreed on up to
# an unlimited number of computers in its possession, subject to the terms
# and conditions hereinafter set forth. As consideration for this temporary
# license to use the Software granted to Licensee herein, Licensee shall
# pay to Licensor the agreed license fee.
#
# 4. Restrictions
#
# You may not use this Software in a way other than allowed in this
# license. You may not:
#
# - modify or adapt the Software or merge it into another program,
# - reverse engineer, disassemble, decompile or make any attempt to
#   discover the source code of the Software,
# - sublicense, rent, lease or lend any portion of the Software,
# - publish or distribute the associated license keycode.
#
# 5. Warranty and Remedy
#
# To the extent permitted by law, THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF QUALITY, TITLE, NONINFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, regardless of
# whether Licensor knows or had reason to know of Licensee particular
# needs. No employee, agent, or distributor of Licensor is authorized
# to modify this warranty, nor to make any additional warranties.
#
# IN NO EVENT WILL LICENSOR BE LIABLE TO LICENSEE FOR ANY DAMAGES,
# INCLUDING ANY LOST PROFITS, LOST SAVINGS, OR OTHER INCIDENTAL OR
# CONSEQUENTIAL DAMAGES ARISING FROM THE USE OR THE INABILITY TO USE THE
# SOFTWARE, EVEN IF LICENSOR OR AN AUTHORIZED DEALER OR DISTRIBUTOR HAS
# BEEN ADVISED OF THE POSSIBILITY OF THESE DAMAGES, OR FOR ANY CLAIM BY
# ANY OTHER PARTY. This does not apply if liability is mandatory due to
# intent or gross negligence.


"""
DATEV module of the Python Fintech package.

This module defines functions and classes
to create DATEV data exchange files.
"""

__all__ = ['DatevCSV', 'DatevKNE']

class DatevCSV:
    """DatevCSV format class"""

    def __init__(self, adviser_id, client_id, account_length=4, currency='EUR', initials=None, version=510, first_month=1):
        """
        Initializes the DatevCSV instance.

        :param adviser_id: DATEV number of the accountant
            (Beraternummer). A numeric value up to 7 digits.
        :param client_id: DATEV number of the client
            (Mandantennummer). A numeric value up to 5 digits.
        :param account_length: Length of G/L account numbers
            (Sachkonten). Therefore subledger account numbers
            (Personenkonten) are one digit longer. It must be
            a value between 4 (default) and 8.
        :param currency: Currency code (Währungskennzeichen)
        :param initials: Initials of the creator (Namenskürzel)
        :param version: Version of DATEV format (eg. 510, 710)
        :param first_month: First month of financial year (*new in v6.4.1*).
        """
        ...

    @property
    def adviser_id(self):
        """DATEV adviser number (read-only)"""
        ...

    @property
    def client_id(self):
        """DATEV client number (read-only)"""
        ...

    @property
    def account_length(self):
        """Length of G/L account numbers (read-only)"""
        ...

    @property
    def currency(self):
        """Base currency (read-only)"""
        ...

    @property
    def initials(self):
        """Initials of the creator (read-only)"""
        ...

    @property
    def version(self):
        """Version of DATEV format (read-only)"""
        ...

    @property
    def first_month(self):
        """First month of financial year (read-only)"""
        ...

    def add_entity(self, account, name, street=None, postcode=None, city=None, country=None, vat_id=None, customer_id=None, tag=None, other=None):
        """
        Adds a new debtor or creditor entity.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param account: Account number [Konto]
        :param name: Name [Name (Adressatentyp keine Angabe)]
        :param street: Street [Straße]
        :param postcode: Postal code [Postleitzahl]
        :param city: City [Ort]
        :param country: Country code, ISO-3166 [Land]
        :param vat_id: VAT-ID [EU-Land]+[EU-USt-IdNr.]
        :param customer_id: Customer ID [Kundennummer]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Stammdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D18014404834105739>`_.
        """
        ...

    def add_accounting(self, debitaccount, creditaccount, amount, date, reference=None, postingtext=None, vat_id=None, tag=None, other=None):
        """
        Adds a new accounting record.

        Each record is added to a DATEV data file, grouped by a
        combination of *tag* name and the corresponding financial
        year.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param debitaccount: The debit account [Konto]
        :param creditaccount: The credit account
            [Gegenkonto (ohne BU-Schlüssel)]
        :param amount: The posting amount with not more than
            two decimals.
            [Umsatz (ohne Soll/Haben-Kz)]+[Soll/Haben-Kennzeichen]
        :param date: The booking date. Must be a date object or
            an ISO8601 formatted string [Belegdatum]
        :param reference: Usually the invoice number [Belegfeld 1]
        :param postingtext: The posting text [Buchungstext]
        :param vat_id: The VAT-ID [EU-Land u. USt-IdNr.]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Bewegungsdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D36028803343536651>`_.
    
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...


class DatevKNE:
    """
    The DatevKNE class (Postversanddateien)

    *This format is obsolete and not longer accepted by DATEV*.
    """

    def __init__(self, adviserid, advisername, clientid, dfv='', kne=4, mediumid=1, password=''):
        """
        Initializes the DatevKNE instance.

        :param adviserid: DATEV number of the accountant (Beraternummer).
            A numeric value up to 7 digits.
        :param advisername: DATEV name of the accountant (Beratername).
            An alpha-numeric value up to 9 characters.
        :param clientid: DATEV number of the client (Mandantennummer).
            A numeric value up to 5 digits.
        :param dfv: The DFV label (DFV-Kennzeichen). Usually the initials
            of the client name (2 characters).
        :param kne: Length of G/L account numbers (Sachkonten). Therefore
            subledger account numbers (Personenkonten) are one digit longer.
            It must be a value between 4 (default) and 8.
        :param mediumid: The medium id up to 3 digits.
        :param password: The password registered at DATEV, usually unused.
        """
        ...

    @property
    def adviserid(self):
        """Datev adviser number (read-only)"""
        ...

    @property
    def advisername(self):
        """Datev adviser name (read-only)"""
        ...

    @property
    def clientid(self):
        """Datev client number (read-only)"""
        ...

    @property
    def dfv(self):
        """Datev DFV label (read-only)"""
        ...

    @property
    def kne(self):
        """Length of accounting numbers (read-only)"""
        ...

    @property
    def mediumid(self):
        """Data medium id (read-only)"""
        ...

    @property
    def password(self):
        """Datev password (read-only)"""
        ...

    def add(self, inputinfo='', accountingno=None, **data):
        """
        Adds a new accounting entry.

        Each entry is added to a DATEV data file, grouped by a combination
        of *inputinfo*, *accountingno*, year of booking date and entry type.

        :param inputinfo: Some information string about the passed entry.
            For each different value of *inputinfo* a new file is generated.
            It can be an alpha-numeric value up to 16 characters (optional).
        :param accountingno: The accounting number (Abrechnungsnummer) this
            entry is assigned to. For accounting records it can be an integer
            between 1 and 69 (default is 1), for debtor and creditor core
            data it is set to 189.

        Fields for accounting entries:

        :param debitaccount: The debit account (Sollkonto) **mandatory**
        :param creditaccount: The credit account (Gegen-/Habenkonto) **mandatory**
        :param amount: The posting amount **mandatory**
        :param date: The booking date. Must be a date object or an
            ISO8601 formatted string. **mandatory**
        :param voucherfield1: Usually the invoice number (Belegfeld1) [12]
        :param voucherfield2: The due date in form of DDMMYY or the
            payment term id, mostly unused (Belegfeld2) [12]
        :param postingtext: The posting text. Usually the debtor/creditor
            name (Buchungstext) [30]
        :param accountingkey: DATEV accounting key consisting of
            adjustment key and tax key.
    
            Adjustment keys (Berichtigungsschlüssel):
    
            - 1: Steuerschlüssel bei Buchungen mit EU-Tatbestand
            - 2: Generalumkehr
            - 3: Generalumkehr bei aufzuteilender Vorsteuer
            - 4: Aufhebung der Automatik
            - 5: Individueller Umsatzsteuerschlüssel
            - 6: Generalumkehr bei Buchungen mit EU-Tatbestand
            - 7: Generalumkehr bei individuellem Umsatzsteuerschlüssel
            - 8: Generalumkehr bei Aufhebung der Automatik
            - 9: Aufzuteilende Vorsteuer
    
            Tax keys (Steuerschlüssel):
    
            - 1: Umsatzsteuerfrei (mit Vorsteuerabzug)
            - 2: Umsatzsteuer 7%
            - 3: Umsatzsteuer 19%
            - 4: n/a
            - 5: Umsatzsteuer 16%
            - 6: n/a
            - 7: Vorsteuer 16%
            - 8: Vorsteuer 7%
            - 9: Vorsteuer 19%

        :param discount: Discount for early payment (Skonto)
        :param costcenter1: Cost center 1 (Kostenstelle 1) [8]
        :param costcenter2: Cost center 2 (Kostenstelle 2) [8]
        :param vatid: The VAT-ID (USt-ID) [15]
        :param eutaxrate: The EU tax rate (EU-Steuersatz)
        :param currency: Currency, default is EUR (Währung) [4]
        :param exchangerate: Currency exchange rate (Währungskurs)

        Fields for debtor and creditor core data:

        :param account: Account number **mandatory**
        :param name1: Name1 [20] **mandatory**
        :param name2: Name2 [20]
        :param customerid: The customer id [15]
        :param title: Title [1]

            - 1: Herrn/Frau/Frl./Firma
            - 2: Herrn
            - 3: Frau
            - 4: Frl.
            - 5: Firma
            - 6: Eheleute
            - 7: Herrn und Frau

        :param street: Street [36]
        :param postbox: Post office box [10]
        :param postcode: Postal code [10]
        :param city: City [30]
        :param country: Country code, ISO-3166 [2]
        :param phone: Phone [20]
        :param fax: Fax [20]
        :param email: Email [60]
        :param vatid: VAT-ID [15]
        :param bankname: Bank name [27]
        :param bankaccount: Bank account number [10]
        :param bankcode: Bank code [8]
        :param iban: IBAN [34]
        :param bic: BIC [11]
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzsvQdYW9f5OHzu1UCA2NgGT3kjkITYYLywsY0Qy4AXHkggAbKFwBrYxtvYBhswXnhg4m28bWy8Z3JOfk3Spm2adCQkHUmTNqsradI0TZPvnHMlIVmSk/TX73v+3/P8'
        b'GVc6e73nXed9z/09eOKHh/+n43/LZPzQgTJQDcoYHaNjt4IyVs87ztfxTjDmcTq+XtAEVggtisWsXqgTNDFbGL2fnm1iGKATlgD/rVK/L9cHZGeVzpovqa3T2Yx6SV2V'
        b'xFqjlxStsdbUmSSzDSarvrJGUq+tXKGt1isCAkprDBZHXp2+ymDSWyRVNlOl1VBnski0Jp2k0qi1WPSWAGudpNKs11r1Eq4BndaqlehXV9ZoTdV6SZXBqLcoAiqHuwxr'
        b'FP4fgf8DydBq8KMZNDPNbDOvmd8saBY2+zWLmv2bA5oDm8XNQc3BzSHNoc1hzeHNEc2RzYOaBzcPaY5qjm4e2jyseXjVCDodovUjWkATWD+yMWDdiCawAJxkS8C6kU2A'
        b'ARtGbBi5EE8enoYqKa+g0nV+Wfw/FP9HkI7w6RyXAGlggVFEejiIlRlY8k0jflyZB2xj8ddIuDsFtaId6VGFeXNRC2ovlKJ21bwiuRBMnMVHj+PgbiljI3XCbti5zKLK'
        b'R7tQWz5qY0DApPUqFvbGD5aytkE4A9ocw6hVE9A9mUoA+HwGHmPhJVs0Tomag46qVTKVHO1QF+PSAhCMdvIKsibiksNwemrYctiKdsrqcU/acOEA8TLYx8IbsCXBNob0'
        b'HG2GF3GO6xbUJ4Ytq1baUN9K8UobA4agDh5sEwTgPpKMurClsBV2xKvlsbqlpKOog4T9wLBxfNgEd6CDlcwT4DjMMV06sm7cqoHvt25Vw+xrxrRgsF3P4jVjnGvG0jVj'
        b'NrD2Ndv65JqRTgz2WLNR3Jotq/QDYgBClfPjynZnFwIa+cVcHiAZlRN+JmgNSeMibypEIBTHKRsijR9YF9sjp/EB/pQoJ7w6ed0sf3AeGANw9Af+Ufy/h+OdOPvDiZ+w'
        b'txLa10qA0Z9MdNlhptcP5PysUJP4VqK++jwXjWo/CdkfwogOLPwd83XUCUkY6Ac2JUloKUNn8aK1xs+NiUE743PkaCc8XxqTm486ZAqVPBfeRifzGWAK8Z8C98LLHrMf'
        b'6Bh4Njf77jsGkLmvCnTOLvuts1vjbUcIPWZXXGAmrXNgexDtyCspls9nAcsDsC0APbNaYwsjKUcnoy0luIb5sGUsGLso2BZJ9kEzOjakpBhHo5Nja8AsDJktNlI96kRX'
        b'EtA+XHE+3BkP4hNxPKmmHm0bhPbhkc9fLAdyeHS2jSw3ujsPdZbkz0XtAsCuZeBj1Dp8dZJtImlhO3o8hGyFODWG4B15c2PgeVkO3ZOKcHQPnRfALejwVNqbGbAPtsA+'
        b'PMSZ6OJkMBk1w07DrAYDa+nGqW9tfHvpjxOCoVK8Tfumqqz5fEnIc9FRhxcu0mYNnlGx/BcJS1tKDy9O7j49Zyzjfz5v5KN//Kgsbs66T8B7f377QXfN1jBewFt3fxsQ'
        b'6/d61q9qBhWtP/21JLJ+dkJFxM1e88F/n5yqWbJq/tu5b/Rcfa9f1Vlz87mP4z/78IfvXJ2YcmzDS8dOTlV9+PfXnhN91BMpz16n+VXLsctmOPaLN4d9IEj/W55eKrAS'
        b'nInahfCqGrXHofZ8ea5MNa5YAMLRHR5qLka9VoJ4GjWVcbly1KJi0cO8AgEIhNdY9Aw6hq5ZCRKePBR2ximkuXFoB0UtITp0A23i1aFe1GcdSabz1qi4QDKDNnkshtG5'
        b'cA8LwtA9HryM7qAe2gS6AzdjdIFxEOpAbXh3ZTBVU+G1cNQlZfvZGKmZQI40kH78Bw8ChF8OnlxlrmvUmzAFobRJgemKvmFqf5BZb9LpzeVmfWWdWUeyWiQEcqeKmFBG'
        b'xATg38H4Pxj/ks9w/BnKhjNmoaNmKa9fyBXu9ysvN9tM5eX9geXllUa91mSrLy//j/stZcx+5LuAPEhz00jngknnkIQVMiwTQJ+UkMCT6OqEuFzUrlbJMfhjDLArPpcB'
        b'6Jk14+E1QTlGE81uG5P88O2flGbqCSuA2QAdU8bD/3wDKBPgT6GOLfPTBTeDKkbH1wm2+peJ6Hehzm+rqMyffhfp/PH3AI7qVvF0AbpAHA7EYYxPcFisC8JhsY6h+Dek'
        b'X1hMp6uATt8HX+OtWclz6RYZr58DZyQDBznHFXGIiNfCw4iIjxERz4mI+BQR8Tbwn4aIeB6IiM+h+U8n2fH04FG254fEA8NniV08SyFOkZ87+pHm5Yr3m4M0e3Ut2g81'
        b'bdWX9O/jmLJnl6De3Qnb5nafOBD2fKH2nNYouMBc0PyQv0c2QjxLMaItcGHmpg+jooujtkSnv8bUvxi64bVSqdBKCF4FepQWh4mknUT2JMcJQQjs4TU2jKLp8K4F9uAM'
        b'8Cw8bc/EA2IZz08YT9NLYCc8qUateZhXQIfgbakQiOBOdjXaN9JKCD7akwX3EAymzoAnVPAyxsHpbPQUdNU6hKS2+M+CrYWqjEEyFR8IUDeD7lnQKVoS3hPDrXHyHJUM'
        b'HV+OWQERusHCrevgLinrApg8bzuMwmm/qLzcYDJYy8vpThKTqS8LZcivkOEzjSHc0iscubgdJOjnW/TGqn4+4fX6/Rr0ZgtmC81kacyEAJ5nHO0S6DcHkUeIc2uQRhY7'
        b't8bZUJet4dFeJfsE/DsBLdEOaFWsHcxYSu94GMxYJ5jxKJixG3h2MKt+EsyADzCzxZFIdBWdCkTteGUwsotHHSU53BqOjJpbRCngNHRCGAaPod2GKYpovoXQ+GE35n2k'
        b'IRD3YlV8eOjsOG2e9mNNaGVNlbGCvzNBrvmzZuGLUS8/+wYLjv1adHC7QMq3RpFJTx6hngb7uPod8JENt1lHk1XeYUXbYIsf6sNIuwN1KOT1FDezYOgGPtw2dwitAt4K'
        b'RwcJoMjQXqUTUsbMsFJqu2PCMvUweKFQzgC2gcmaAbdya8l6BQuMEKv1VoNVX2uHDILPQEUAI2Yaw51r5MzCVcWnK93PN2lr9QPAYA7lmgl3ggKFAkLqK51QcCzYFQq8'
        b'tPBfxzjfHRRiydxeXqT2BgkUDgKLHZDQgi4aPnwpnqHQWa+fMAAJcdoZiwcg4WMNuzPRpnxdeVrJT6q/BcDlZtG6Xr2UR8krqQa22vGFdBw8ZweHYdOshGvH6OUUOucC'
        b'CzkRrtCAHmdTcIhHjwZHweMUIJzQkI122Imgb5SA197iufbVT6y9xX3tBdzSkkXuFzRojTYPCOC5QECkEwzIbNc4waAr1DsYOBvzjQ9SOTAgHDFTxf/f4ATGXrU7IAgK'
        b'bAr8vQAdn0pks1LUIpcr5ubkzkMthSWU44R3ps/LwfynggFW9NBfiO4G2WJwkRUrRvoAnZFwrxOLTPM3rH7tKmspwCW+XlL/keZDDDvGqtjBsdocrZHCTL22pfOC/pz2'
        b'fc1PKl7GMNV1PU6bq72gDa0ELw3eycw6PKTXqpTpdLocrajqdy8DkFIR8oxuh4NzvBMc7MLXUaYuCW3DfJ0RbabEZDa8oeSgrhhdcSIhdHIEB3b7Z8MD3jCQBnUSsNsy'
        b'llKrEtgxxA5zIZkOHIS6KUgy5khCqzD43pE5idUI2Cm10wu+T3aQg0yhrZ5wgQOkyhiAWT4RZfcag+zQwuVxxUgcFXKCowfsY+Q0QKcoVBJBp9YJlZ3hrlDp3o6HiOaO'
        b'l6h47MRLTAvzrSKZBzjyvYIjr8Cw+NRmviUXR/zm81tqbU71xxhgflhRUxWpPSe49lp11BClXEdAZof2gv6Snn1JrrmiXfLiwh8tQaWoCBlRUcwvnlvI+3nYy88eDgbC'
        b'H4TUn4GYGFF+5gi8mkwh4b7NhRyhw/AiBZT60XAfbM2A7a6oBd5Du61k4paET0KtE9AZmQq1YxlMuIwdGz6WQ2zPZI3G++AuvIZZHSefg87Bdu9L/zQshXl3i9Vsx1BE'
        b'SgfWUMztizEwNAYPIA6ShZY6z+PW1zcYYK5lAAKIzGlzQkC7G156onopW2Amgrk0iHBThPhhiSKgvJzTnuHv4vLylTatkUvhUKSoEsNOdZ15Tb/Izj1ZKIfUL6wy6I06'
        b'C2WSKI2kGJICJO2TA9s+VXjihkAmpYQMgWBbEctn7L9ssEgsEAtCRVSwzpo5NZBIH3hfnyMSiEjMalYu9S17ECToJnuwZXwdj8ga3WyZYD/QCY9jWeME08RgOUREAdq/'
        b'XzjLhBH4mi8js/UVBmsdFuHi1Wa9jvv6AccgfECa+DJ8vt7caKu21GttlsoarVEvScJJZDxfivP01karXjLbbLBYz7N0zj/4AR7vZ4fxnKrrTNa6zAI8x5KYLJ1Zb7Hg'
        b'GTZZ19RL5mH50WzS19TqTdJMl4ClWl+Nn1atSee1nElrRQ/MRoWkCK9QHS47v85s+i75vFW2Qm8w6SVZpmpthV6a6ZaWqbaZGyv0jXpDZY3JZqrOnDVPnkc6hT/nlVjl'
        b'Kix5KTKzTHjC9JmlmA4a47NWaHUKyRyzVoer0hsthDoaabsmS0OdGdfc6GjDbM0ssZq16Jg+s6jOYq3SVtbQL0a9wdqorTFmFuIctDk88xb82WhzKe4IVKwivSOSt8Te'
        b'ERylkJTZLLhho0vnJQk+UxIz1XqTqVEhUdeZcd31dbg2U6OWtqO3t6eXzEEPjFZDtaShzuQRV2GwZJbqjfoqnDZDj5nMFaTeGHuU1JEmmaPHsINOV1ktZJRkSj1zS+bk'
        b'STNnyfO1BqNrKhcjzVRxcGJ1TXPESTNna1e7JuCgNLME72HcSb1rgiNOmjlDa1rhmHI8RyToPmskZgWBYXmBrRZXgKPy0Gmi6lhBZo2bfhypmpFVQNL0enMVxhT4a8kC'
        b'1exS+cw6vDb2yad7wWCqwbBG6rFPe47WVm+Vk3YwyqlQ2Nu0f3ebd2/xZO7dBpHoMYhEz0EkehtEIjeIxIFBJLoOItHLIBJ9DSLRpbOJPgaR6HsQSR6DSPIcRJK3QSRx'
        b'g0gaGESS6yCSvAwiydcgklw6m+RjEEm+B5HsMYhkz0EkextEMjeI5IFBJLsOItnLIJJ9DSLZpbPJPgaR7HsQKR6DSPEcRIq3QaRwg0gZGESK6yBSvAwixdcgUlw6m+Jj'
        b'EClugxjYiHg/mQ36Ki2HH+eYbehYVZ25FiNmtY2gOhMdA8bGeiwcOQL1ZoyQMfYzWerN+sqaeoyvTTge42KrWW8lOXB6hV5rrsAThYPZBsIv6OUcucuyWQhBacQ8Q+YC'
        b'dLrGjOfNYqENEKzH0VijodZglcTYSa80swxPN8lXgRNN1STfbHTaaDRUYxpllRhMklItposuBUroGpCUIqqSda1sgIzLy3AvMMKIIcXdEuzlcdJ4zwKJvgskei2QJJlh'
        b'tllxsmc5mp7su8JkrxWm+C6QQgvkazm6TOcc8yWYP6FxVv1qq/MLxkTOr0muWS3ObNxCzNBjclztEjE+s8xgwqtB1p+2Q5IacRQhvRhLuwUT3YMY/WgtVkztzIYqK4Ga'
        b'Km0N7j/OZNJpcWdMFRhsnStuNaPT1RiIVCadoUEhmc3RD9dQolsoyS2U7BZKcQuluoXS3ELpbqEM99aV7kH33iS4dyfBvT8J7h1KSPHCpkhiiu2zarEzGtIBxshbop1X'
        b'8pbkYJ98pTlRmZf0Qu+tEb7LW7wbK+Z7DE9J98WdfZ/Mib5bduPTvks2jCq9ZXMjAakeJCDVkwSkeiMBqRwJSB3AxqmuJCDVCwlI9UUCUl1QfaoPEpDqm46leQwizXMQ'
        b'ad4GkcYNIm1gEGmug0jzMog0X4NIc+lsmo9BpPkeRLrHINI9B5HubRDp3CDSBwaR7jqIdC+DSPc1iHSXzqb7GES670FkeAwiw3MQGd4GkcENImNgEBmug8jwMogMX4PI'
        b'cOlsho9BZPgeBEaQHrKC0ouwoPQqLSjt4oLShU1RugkMSm8Sg9KnyKB0lQ2UvoQGpdt47F2cbdbX6ixrMJapxXjbUmdswJxEZsmsoiw5pVZWi1lfhYmgidA8r9GJ3qOT'
        b'vEcne49O8R6d6j06zXt0uvfoDB/DURKEvsKEHtRXWfUWSWFRYYmdgSPE3FKvx/Iwx0wOEHOXWAf5domao69ADwilf4JtqObi7VyDI5ToFkrKLLIrV1wKe6hdEjyjEj2j'
        b'sJhjJEKx1kr4UkmJDVenrdVjMqq12iyEreVGI6nVmmyYvEiq9RyYYnLoTQ0gdSliIMTdoKPFvjWzl/q9ECXvdXtmpCqmgdmRYOZbYmd56VRWkXT7JHPfE12+E5lwQFP1'
        b'JZNZcF5kJnpTM1GCmomGlTsLIfYYZqKb7xdY6o0Gq3mkU4MX6q7LIyZz6910eTyWYf8tFLAs+zWbxP6Yszm7AJuWWYhxyI58rQye5wNRKrsBboYH/sv6vICsyso6m8mK'
        b'5Yf+4Bl40Tm5Q1uvN34wiNPmET34l0OzMRjUYt6CqEslnOSDgdiAUQ/OQrSw/XzCA5kn4K+fPcAR82o5lqauxqSXlNQZjfE5GCeZ5OpGomEZCA5gucwF6jIJV4xo0gj+'
        b'tBgsNi6CpLmGuV03hyj+OA6fa2jGPHlJZY0RPcCrb8RciWswc4beqK/WkYFwX+1ql4HviXYJKdMxE5TjJyyh3r65HWKbhGOL7MLfgJrKLvZRZp0IfDgz3l5WKhjYa6DN'
        b'GQ04A/1mMFXVSeSSLLPV0RV7jMpESj4RSbIlesuW6JEtyVu2JI9syd6yJXtkS/GWLcUjW6q3bKke2dK8ZUvzyJbuLRvmMgpLShNwhJpbGMLt6mlkokckDkjy9RhjOnSx'
        b'EptCMqCLxZEcLDuUowoJ4dgdcjendB1YRkleXF7mbJtpBTWe1ZurMYpqJGiFxM+YJ0nO4AhtlSMLUQp7i7fDDZfkpcLMMioQkIGba7Uk0Qki3lKcoOKrWOLTinlP5EDo'
        b'KcW8J3Ig9ZRi3hM5EHtKMe+JHMg9pZj3RA4En1LMeyIHkk8p5j2RFMt4WjHviXS5lU9db++ptODTAcU3pCQ8FVR8pNKCTwUWH6m04FPBxUcqLfhUgPGRSgs+FWR8pNKC'
        b'TwUaH6m04FPBxkcqLfhUwPGRSnf8UyEHp5ZY0YPKFZh0rcLE10pZ01V6g0WfORuT+AHsh9Gh1mTUEu2iZbm2xoxrrdbjHCY9YYsG1I12ykkQXpatiijGnEjOQUtxEsG8'
        b'AwRZEpNlauRYYnKih5FxvsGKSaNehzkQrfWJ5CfwsGfhAUz+ZJrZiG5Z7GyCW0oOPd+psmKuxClYUUoip/yOVynAPlI7NcekH1MawkRXUfa5lhB4q96Ap8Xq1BSrMK9r'
        b'NVQZVmhdsX8ZFQSdGmRXNoMTH11OEl3ZpNl6TrbQGypIUh5eNXI0ZuE4G9+Mmqt2GPcbt6w12mpX6GscqmxKBCkXJ8VcXIE51hcTK8OPBz6Z2GHsezbC/y6G7ajHkleA'
        b'dsVTTnatFbWp/cCgCr4YHUnwYGTFDkZ2OePOyO4X7g/cH6hj90fsj+AY2nY/naxZ0BzUHFHF0wXqxFv9MVPL1wt0QbrgrUAXogttZ8uEOBxGw+E07IfDETQcScMiHB5E'
        b'w4Np2B+Hh9BwFA0H4HA0DQ+l4UAcHkbDw2lYTHpQxepG6EZuFZUF0V5GPPHrrxvVHqCTN7P23vJ1Et1o2ttgblT7A/YzVWRkfvTpKDWm3V+noLZwAuqCEYrL+unG6sbR'
        b'siG6eJwmaBZRB41wmjZeN2Grf1kojg3DfZqoi8F9CsNtROik7Q73guDmkCqBLlYXt1WEawm3CwHKflE2scieWTL/y/gAicuPI1rCYRDOUcgtx3mBmVgUmceRE3xqmB1P'
        b'vlHTDCIJSMUfELOaD6i9MTGqGchuTnNkN6eTRwLJQp00qDkAgQapX3+AVteAkZK53KDr96/EqMFkJV+DtZzYUm7EvJ21pl9UacO7xlS5pl9EzE0NWqPdCiOwyoDZufJa'
        b'vGNraNv9vFnzijkzD3MGflSKXEAwwP5PLXRmgCf8mfybhc0BzX5VAXYjIFGLqAms928MWCdyGgH5UyMg0Qb/hUDHo55K/M+IZ4TbrJEfFddNQ6PeQv23nHNtoIYMlXqF'
        b'RxGPiElY2tDWSgamaJLdcwtjFKL+sbuG2edKa7J61EB+YmZgRGB1oCGpQpJFymOUUSmh5n8SW70EI840ic5QbbBaPPtl74Zzdbz3gkv23gPnIce39CHl2/rgDhaTJHn0'
        b'k3RhTnyeI9XeMYv3vhAyQxA8Jg8KSWkNRvkY+vUSi63CqNdV4/F8p1o4CxJONsU1SbS4Chzm+i8x1mHyY1ZIVFZJrQ1LKBV6r7Vo7YOv0FtX6ckhryRGp6/S2oxWKXXc'
        b'S/e9FvbtMEky0/5NUkm0hDHOs0UX7aLUVy2OrTTJAa0W52ISP8E6sySGs1RZgR6YG7G87asiu2XUJCpcEUYEV8PBiB2zxOirFZKUBKVMkpag9FmNy16eJJlNAhIaINVV'
        b'GUx41+A+StbotbhjsSb9KnLQ2ZCqSFYkxEo9p+o72AyLOS8FXnYYkIAWwNRrxC+X1wDbFKKiubpRgFrz4aUi1KJC7ep4tKOIWJDm5ElRq6wgaqwc7kQdeXNz4OWcgvx8'
        b'VT4D0B54XFyHdsFDtNqEmiAQBXpXiIs0sp9HRwLbVKr5sfK9VksMu/IwHYU7nqx16zR0eo0YoIfwIK334UR/EAqUS0I0GiMsHQlsBBMHzYC3HK5V9egx8a7KUchjid8K'
        b'vMIHqUuEFniqhnqH0Up2lQgxRT6eECjR5FUNnwxs00nn9sBj6Jy37qEW1IaHTbrYJp2fkwpvDXQQ3jUHwuvoFDxruPyOXGBpxDXFrswY8fKb/puU4m1v99y+cW/7vjtb'
        b'eKLiv34+5h1+wN4Ea0nHiXrR3p+tm9Ype2vYaJlq/zjr24PK/v2b4bdeby0ID7RdmP+LrMXnFtg6Ngbt3LTlIAi5+Kbf6tKQN0u/2NHfm9o24e2OYfm//MPtcSOP/PGb'
        b'K9aPKibteyHkeKz07syhUjHnHHW0HJ6GrfFqeB/1yZ2+HiHjeVUS1GslarqYyathayG3nCvRFm49GTAUNfEb0bX11BZ3ODxUGYinVJrvMMYdtAzehc18kQzuobWUo7to'
        b'B67Hbf0YMHi9eDQ/MDCRmtoWwZZJcfKYHDm6ZGSBEHaxcnQfXaMdRU3hcBMu77JY4fAKDx1So9bRfpw15o0x6EKcQop2ylA72g5wDZfYJHQcXrFKSA3nFDzYShy8nCsk'
        b'BOENPHRuI3y4Gh6yjseZ5mhLyGDtzBrppH15AaiPV6JtQsUsdMFKHJ7QY6mFjKdVFqsg+XCTHXGTppCcEosgCLXYm42Bp4eTfIT1I83KcaPwIG8aOoi2wf3oJq1sTqJt'
        b'oFl4B52k3myYSxwK7/Bxp3tRF2coGfAfup8NeKpQ+1LCeYCNYJ2QEVIvM6Hd1ywYP4mnmYglKUKmMcxBkJ0eLAWOjlDbUuISZiZ7wpxFHoRZMM8EDvcY4tX5NDtlEVdq'
        b'oJIZzlK0Ei+ONh+Q7hM+HGwCh0e6WrF6dtXNlpmx/1MLUtKndWA5Z5/MFEiZ/sDyAf7BHOWcNhfHoslGbW2FTjs1DNfyKanRpUVH2pd2fG6vy0H7YzCd0MnrTMY10vNM'
        b'P09XV/mdulbFdS2g3MlTeOuZOQc/InF5swp/+XIU1wOuiJcOfJ+WQ8rdOQmfzQ9xNi99Kq/xvTtSw3XEv9xByn12YaizC9EztBa9k/b/5006WWhfTY5wNjnWJ2fwnzUu'
        b'Knf4oPlqWzLQtk9u4j9bdHG5q7Dgq/2xAyv+LSyIj164+RZQ5ze2GTid3/4jzwJHtR6eBc0lHzHUq/ZHR/7IuTDVVH286XXws7Yft70jfk7cbQBTT/Df6E2XshypuMKv'
        b'4nD2AoyMXdE22ob2oR7qP1KLiftOF2LBYezqJXacvQZ1Ps0hza+c7ClXh6SN+HdiY6gLFqMZuDJDnqwpyrkai/BjAp5ZCzmCw1hxE3jLzfnMo0ZpQL+ffV9yxvtCi9Ws'
        b'11v7RfV1FithkPv5lQbrmn4/Ls+afmGDlsqbgZWYTa+r5eRQnlVb3S+ow9Burgx0WQGCtIMdq0DcOZoDnfJjkNO/P5i7W6Eq2L7ggS1ivOBivOCBzgUX0wUP3CC2S5E1'
        b'WIr8tcCLFJml01mwmEB4XZ2+guw7/Fdpt36T6Kmt/ncQJKmYQ2UUraTGVq13Ed3wzFgMWPSRcO4MRAqz6K0KSSGGa496CAKoJUcuhtr6OjOROB3FKrUmLMaQolgEMusr'
        b'rcY1koo1pIBHJdoGrcGoJU1Srp/YTloUZKQGojzDu8tepV1yInV61IGrtlkMpmraI2c1kli6aLHfYUZm20dbQ9Qenn33yB9j1ZqrcRs6ByYi5SVEHWghUohlpY3MboVZ'
        b'W7lCb7VIJ3134Z6D10mSLDeCIllMD0CX+ipGWp4kof4Li7/Vi8FnLdz2mCQpoZ+SxXabOp/5HdtokoQoM/FSUaFzsatNnc+yZONhcRU/JYsLzVbf+bitibNyX2gbMomq'
        b'pFCelJCaKllMFJg+S3P7GQuiWaVyVbZksf1UcGncYlcfDd+ND6ABIlpzAQmpyNUy2GdxjDjwZNbgrYG3q6XSbKi32ukXgVPig033VpbRUofhV6/zqhXA4ERyE2pjpLfy'
        b'0MVWSLI51QDdomNKrNraWuLWZhrjU0lANwMGLNyBevvW0hnovUBaPK2rDJiq6VfjFbdvOM96yE9BnVXPbRO6+fXWmjodxiTVtloMaLgv2hV4A+JNo8ezU6mX1GHy7rUe'
        b'bkhk01Cdh4UbpsHi0iWFZDZGag6E5LUW121HNCQY1MmtR5VGPGDuwiOL3ntJjf3Oo7pK2nPuvGRyjdVab5kUH79q1Sru2gqFTh+vMxn1q+tq4zlOM15bXx9vwIu/WlFj'
        b'rTWOjXdUEZ+gVCYlJibEZyekKxOSk5XJ6UnJCcqUtKSMqZryb9FHENrn6SsYXmCjVPo4uoDO1aOdljxprlxRQPzz4uB5GQDjSgQ1oiAbIW7D4UF4Jwl/SQDa4ATYgk5Q'
        b'uf4dGz+VYbAcMV1jDN7IAzaifIVX4CmZ2kHP56IWcilJrry4qFhuWzO/OIa4ii7AIj7+wKIZ3Auv+qPO6fC2jdi9oKvwNnFo34XFQLTDDwjQYRbtQW1iOey2EdESPShJ'
        b'Rn0KckMGvTYBteLqya0nLBgFz/DRPXgdXrQRgQhugXsrUB+Wp/Pnod31eVLYgZpcR1iEWgpw2Tb1vHr8KMzLRZ18gHbCLYHoNOqAe6jxTJQO3Ydn4f5AhTQXPoDHAoB/'
        b'LouOwRsTqJ8c3A1CLGNQnwrXwAAePMjATUwNvcsjMwLuDEQt8Qq0Q4UZnl2oXQbP52K5uYUBkjkCPmybQucWHcgQo774WAaw0xtzmFS+nM7taxF+sUUMZlAkmrzxs2cD'
        b'2hvUvjTFEoQ60U2uweHLREvYObAH9tKbm5hweIAkBwUp4C54BU/czTx0LQ7t5YEha3jwkj6PnqXY4H0QqMA14HlTydDJ9XhCeGAQussPQbv8DaKDv2QtXTjfJ2UB8p/k'
        b'B0BlqOB3aaovf/t+wQc/abrzScAy7fTeYVLFm/kXlWd3D558Ll7S98XqtxMimgbN//W1O/5jSyfFfGlOP6/+QPyjS6mL0o07vhz7pXLJ0YKml5jWlytg1Q+qjmf8eN5X'
        b'hqxhZcWFcWWvdvX8OKgdvXByxpu3P3r1T4d+c2PeV5/uurt+nW3amTc3BJ16q/duyrBrO/56bEHp1VEqc9yqkAtSIVWYwG35S4jahahcctDdAa0L2gy3WOnBALyau2CK'
        b'2qsqIi5JgDqK0GXOD/oi3JHhVL4okzn1C9G9lKAt9LoFMTwFO7Vwtxc1BNoGt6Jurp7WeehGXIFcpcpXy+IwbEoZMBg94CfibdHBXchwYeQieKlSLYvJwT1hgAheZNfA'
        b'5lC3uzmC/9Nbcnx6xgZodbpyjomj3PIEB7ecI2bEjIgZTJ+uv3x64YeIaYxw8r4DddgVGEGcdqEMOIzXyBUe5iXksZQ8lpFHOXloyENLHhXATZ/h3cc3kKtzoBKNs4kK'
        b'ZxNBzha1znYoN0+uIZO6cfNvTHDl5r2NSOrfL9YRaz47l9QfxPG+jqBQW0s/yfUm+n5/+wlupb4/kHAqmD8k9l1cH5zDrAxwQcNE8RLqQMPEoZ9eijbA1Adjtj7EztiH'
        b'Esa+KtTO1gdQtj4Qs/UBTrY+kLL1ARsC7Wz9VszWd/g9na3XOu3zJNxdR9+BeZ1FfBu43BJMQfF8Yb4UcwVa14v9COcgk1Sb62z1OBUzzFpPilRXW2EwaR08SixmX2Ip'
        b'ceVoK5H2ncacpINOAdijJiIQ/1855P/PcojrNptEFoqLceq5vkUecduXXHkuylGBV6Zs8bfYd/psjtv3XDv2rW6P4/haUx3R25gp52ryzo+uqiOMo6FWa/TB+S5+ioUr'
        b'lie827j67DHBUFx/K+rqVpD+khiFJN8OXVoaltRVLMcLj6V87weGJiIHpacqE+yqMAIIWIgj1S0esH712QkngpwkmWexaY1GujMw4DTUGSqdu3Gxi/HsU0VBO4J1Xwbq'
        b'V7fY1cD2W4U1UvwJgc3NjPP/AHlrhn6VvtpuhPN/Za7/A2SupFRlYnq6MikpOSklKTU1JcGrzEV+ni6ICbwKYhLuYHiXWECvr9NI6sS3/YcDGzFiWVw9XK3KRztlKqdA'
        b'Re6W4qQotFU1IEhthA/9kwNGcRb/++UmToiKQpeccpS4Ht6wEUMZeJEZqVbk5mMe1lu1tM5i2MbJZ62o1R8LQAfhaSpVoeZl6KqlML/QfncREdMWoN2oBZ5bgXvUgoWp'
        b'ACyA4FpxLXdLlsBu2AVP+eM20YHAAngFUAnEOBzuseRqcWvtqvxCNbn3SMkHUTN4qA1enkiziNVqS2w+2hVD2HWFCl6OYdAldBuMqhYIBmfTLAtXo8eB6DbcVSxqTEbt'
        b'8gIsYLEgPIkHT8BdCfQW0GB4HXXjqWiLQ30F9otAc1QyFbxZTG4CTYCtgtUyuM9GDlfRDXQZnrDkkj4NXlaokknJtaKR6BQP3Uf3p9NFCtWwnJNEoyHvNf8FwEYYujmj'
        b'VwZuQPuFAJSCUtgTayO3TsEmfVQgOgoPkEnCA92DbudgEbMd7UM3idjZCi/iUB4RXLDwtSRaNAceQrfoZapF8B4W8frgEfQIh1RAhe7CLnoLKryBrsHzSZlKKoonrB9K'
        b'ry/FtR+dgPaVQiz9gHgQj+d6r/GLb7755uto7kbE3sH14oWTV3CH8Svncrfh/nWSSTY5oBBwy9qCWivJ/LTbhfYc2XxykXF87jwMEzmobeXIkhgpho0c593FUniLzqHQ'
        b'FLRUL6TS8Hgbai5BnUm5PMBk4hFfAuiSMtpG7qlOg8fh7kD7IhUTgOGgReRletADPyy87uUD2DzPf9HyXBsxEURHcOK9AeF3bgzqLBEFKVyF3GmDhIM3BINMGxH94KOx'
        b'cJMlV16YH09AqEAlo2KuNBBeRocE8AY8i+7Qi5Xh442JcdxVm1IhCISP2Wwlnv3H4+m1vcnLC9nnhSCn3ayNeHPhlQgBsJGTVnQaXkUnUJ9ducFZVWDwQjviC/Pnxtir'
        b'm+9qWvEMOlsFz4rR7qVwJ11n1aiNcVgMb50jw8K/EHaw8ehYNHc9bhfaYlAT8TC+HrBmJt2ETkh5NnJ+IZJtIIXuwPvOUrADHaWqhEblMFooegMthJ4ppUqVYngH3nIf'
        b'IbyAesgY6wyD9vB4lqlYVjr7wLR095QCND10W3XDrxq6N369NwoOOictrvcbGqwMKJaN1hWfsKHUpuywuSXp8jnH31lyfvVP7p184/A//vDam2/Me/VocFpkXn7XBzn7'
        b'nt38du9fu3MX/NrYHpVfFflFe8rfxjUMUv2rYx344OcNpwWHNw0/3nNu/c/FtjuGiVOs5yeNEJSsr7mi+Ov9kn+8Khk7J9V68PfT/5E1LHp/6b9fDG28cfLs0bZKv36+'
        b'qTvv8yV9eVMOGmyvvGzZ96L1p+Ziiarg2tvMB9WP1L/p+aH5Ss+8zXtsmy+9tOvimYLjVUWmfb8QVv9r5po9P1Ed+nXj2AeSO78fMe23Lz3QP1j0Zn9j4IXynuOP3vzJ'
        b'm1uWN0/plu0aFqnf8sZHDZKDv/5R95JB1pf/3Rbwl64R98ev8/sm7cL7F9eOu/v19ZQHq9HOisam8jeS9r0y5b2Ppv35qvn0V3+SBlEDDXgGHUPNGGnuM8ar3S1BYBO8'
        b'biU3v8EeuAnd9aGTKIG3iVoCo6y79BANboZbUCenmMhE15yGIUQzga6gDnp7L7qDrgjVw+F1F7uOkPk8IzoBe7mrRG/kwEtxsDkrlhp2AOC/iIVnouFJavIRizHf7TgF'
        b'almKEc8OGYGqXawc3kLd3CWRd+BFqTovVjgKb2h2KZNWvsZKdV+n0zCivZiXL8M4cdUENQOvwxMraXuD1BZMHdqpmQjeInhgwnXsxDp4g575TRlq9bD5wHlQ72hq9JEP'
        b'T1BzDnjMTPOdRpvdTwftZ4OL0XFq1DIGnZ1iIftMjlFVdRQ342FoNw/2roJ3qM5lMNwJr6oLUJOb0kWreMqVWdLQ/5IKxpsyJpioHQakcaqQKSVkZSP9ZcV2dcyAUobc'
        b'YMypZGiIJRYmI3FqJCOkdibE5oS75ywch4OpFUoAS+89G+Km7Bho1a7CEXNqFD15VJFHNXmQ2xfNBvJY7lSteNPe+H2XK5ADuDqrnBXrnTUtd7YT5GxiQI9jxI8yNz3O'
        b'uVhXPY6voVUKXLgucj7ufkW6oNmvGdCjU6Y5gGpfApv5zivSBS3CJrBe2BiwTuDUtgiptkWwQejrAnrSyCjwJGsXzLF24sWUawi9FaKR7ZGOBKU0dkIGZfgW7s3TyEat'
        b'SgOUhOYRomKB7aKVPID5mEHBGI3vlFOChpo2FJbA9lLUPi9/LrpZhG7OC0pVKgHahrrBiCE8uHlYIsX3erQTtZag9tIUJdqZrOSP3ghEKxl0HLZgOkH5w/vodKOjKmYc'
        b'2g8EsQzsksEr9A52jAVuToF9QrQHL9ZkMBluGs3dtn5uDcY0p9AZdjg8h/sPojAdP0qp0urlaLNaoUxOTGHR8dlAuIGBRxfCM7Q1Azwymt49jh5PUA3cPQ5PxRjup/FY'
        b'yx9wnnNpH84qzCzgJ4hv/l71h75nFeEzps/8Uda5mvMfXJo1dFzo4jd/UXTnXZHqhbB0MGjQ+BeeO/zMoOtfdf/jE+PE7dEBMQsr9/wtXNzTe/+aKXvWC8c3N7366ezj'
        b'sbvmMeP9f7nr7/z7mVk9gUXv/qBT/8Oog10H+of6v7ur8jn/6M/f/vo3FuU74xb+sRZl5H12I7zxn8rrP1nb3//7r15bk14/7C3bux8O2ff7tAUv/LTt8QbLutf/NurN'
        b'FbUjs049v65C1eUfOKb0B0uXxf/lrf2Lbq4ODKnuqqqLN/xl/Qu/ivvzp2VffWEd8s/9fss660P+/eao438teu96uDScXoWIupfMpPf9+wEWnlyF2ph5I0U0ZSS6HuvA'
        b'qGjTcoJShzPclc6nxldxKDWudKgDocJz6BZnRteDusoGcOqiWQNYlbOja+dTQrFuAiYJrS6UCYsWlDixsJ2SAgU6nawukGEmryMeXuAr0APMQj/ilQcZKcofvC4Ytarp'
        b'DfH8AOVIBp5ED9BO7vb35ppgcht2Gea4Xe66noeJHr3sGu0sc7lgfjS6DkLIBfNytIOjc53oTqias4+0G0eiYxEYcV/mD4OP0EHOoqQJHjKqB4wfIzA/TOwfw5fz4KUN'
        b'sJOq/NH+QSOdxFVr81T5h8NHtEshs2uIEeuAHWMefAxCRvKWJSRSohGwfpF6gKAGNnIk9fgGuh6ThWivQ4WPDuBZpBQFtU/lis7CHNzARfjZsCuDgdeW5dKia8TokeMa'
        b'X2EWvMVdozkddtN5LI8hM9yOR1moEmjgVpy6m62D23EHvxOu/V/dr++wquFu06dkqWqALMUTokNNGqlhI5+QJJbFnxyJEmOMzP3yKaHizg9IiDODFDnTnb9v80fz2WB2'
        b'MEuIl6uNDdcBjkD5DZCGfj9OE23pF1isWrO1n4fzfV9qJDDXk+8mJ9Gpc1IeSnTIFa+XGbtDEiU6m8AvJD6MgbiO/hdtsuwmOl++56FK4LysrA4fD7tK1mjXlJj1VpvZ'
        b'RNNqJVqi8XdRvHwnbblkhX6NBddTb9ZbiNUjp9Gxq6gsTjW9Xb3jTcv9pAbfyOnFSHcq1lj1XjRQbjRU6DpxLnbzNuJBJoW9cCtmrA/ADrjDWAqvob3w+gLMcl6DF+fC'
        b'FgGIgpt4a+ehTu59JL3wCmxD+wQb4XGM1TBeuwk76bEsuj/eTmBh6wLYDR/K0QG1QsEDkXAHD55HW2AHpc6fBNP3w0yvCNAY3/FP5170gzbzYRcuHOdHi8uFY1BnBXyI'
        b'WdSTiSA2RZA+bRolh7if7WOJmHZisVNKG4qucOLm7pGoHRPfobCDo78c8Y1IoyJc+dwQvPvXrsA8KhHh4O4SOh4/eF2JKXrgBJIfI2tm+Gp0z9Bfe4hn2YyTPy+fl//y'
        b'6OAZCaFb3z7868GrhapPFM/57xZFCgNNn7I/fXvV+kHVNXW5M2Pr9+V9/Zdt09/e+cPtSQ2fjnzhPn9mwIWo/O78mflLQ0TySx9aDe/UT3n74V/0Q9+7eVB6faI6acuB'
        b'b4J+euvw3L7aYf/6zb8///kd8ao//fnVYyHN61a+pZzy+Mbyce//+KhUSMUftKcoG5MhuA+jPo8z0riVFDdi+f7qQox0VZgLue68C1hdaiXbrRBLHffiFFU5+Swe5jlG'
        b'LYAceYF3GoZjysW9GmPVdBYE6jGngXbDVno4iy6UYuJgNyOMXv+kqFCcwh3OtsWi7jgFbIYnXV51QshQATwgFX4L3vBhgqi1lJOdRpHlmAFkaeTzwjmuHH8S1EeOWcX/'
        b'FgoiWRf8YS9c8K32iWb8ePcJpHTUh4WivdLzTD+/Xmut8X07+iRgv4yaHDqStyYInTek8596Q7odSb3NY7wcOA7gKYIyLNoG8s1odMVY390fjQxgkkRVJYkl32IlGN1a'
        b'ONU2wUX61cTLlWh6YxWNhvpYGW3IjhTN3hXFFnKXn86pntaaK2sMDXqFpJBo01cZLHon4qN10AHQ7FpJVZ0RI/tvwWJkuZx+f04sJiqgt76jE9YxcTl4WxTlYIKem58H'
        b'z5fmwMuoRaaQrkVHhSAHbferx1hEjjNnr4NX1HgT5eYr0A7MjpUSLV38XMxzyGPg+XEYGQE1uuUHD6AmdJbillnLx6F98CIV8XlGBh5Cl+EW+AA+pNrDOivcHAebo/H6'
        b'rwar4Y40TnvYg/Zq4kpgUyELmGKAuuChHMPdhcN5Fszjgyl92in5GcFQGdq9NHP6new9B7Pf8Vu3qWh62KQhLax0uiHt9BvBO/Yu/3fJ8Dknj6x9fsmJcamvPmy8furo'
        b'snFNVdfnt87NPPmuuSFQPoZ9/sNxM87+ZNyv1P318185Mn3kpNbX3/6occnN4elRhWWNn09IPLEi4sicUFP+14vEH3UUfrkouOWvdb+qXJz+x/kVU+Y0zPrpX/J7f/Ph'
        b'JHnPV2GLP/7Z77b++aP66Wv+yby6Lm1h28fSEE4ncQCP9wCdYQzraQxbDK9Mj6UYZNQodBu1CufKCuwvSBOhVnY9xjfnKDe4ZrYa9aEbq+wKFn94thFuY+GpCnSIutWE'
        b'BWBmt3USeoTL78D8ubCAHZ6LuWZ6M/r+qZhBa8XxGOWTxEDUq57GogcJIRxvfCkebVXL4K5C7kUAgdNl8BKLDkWWcdqZk6l4zVphE8aaO+IL5bjyDWzsBPSQVh6ArsBe'
        b'tQmz1e1qqQJ10KGFKHnVmf5UZhBUjEKtscUu96qz6DTXrb7CpXFhG+LJ8YFcIWUxqjvGI3fyoy10SHAbM06N7mAmGnPU8VgwE05mh8gSaJ9CM2CnGu4YbYdNIfCPZOGJ'
        b'YbCNw8a7YB/aj7t8bS1qt8/HDDaqHvbRwo2oaZnbe6BgWxq8FoXOcqLMWTHcF4fJ+WnaM9wsPMfKBqELT9PGfAtydkHIfLJh3U1cyK8/p08RUd8cMWZMHfqRUBzbGORE'
        b'nqQ0h47P298TYAVuGg/fnTzPcnkH7otvwI9vnsDaTYPd3hvg1rDU7gI9CxCXeadfMcYe9h+pgPtg8X/EE7dHEWt4XV1leTl18ekX1Zvr6vVm65rv4l5EzN+p1QxVuVAW'
        b'mJIcOgKODY/8r+vDnrqOZvKmhN+TZdwL6L0A/AAG8wSA/YbPAge7/U3keBZLFuzXQt73/OQH88RcfU/WiWsdHC9mhMAldeA1M98Mnzs0LXiYiHudI+Y/dsKHynQLeS+j'
        b'JRizjEEjWHQCbSuxEa5k8tDYQHjOivfJMfgMagskZydF5MxkeCJ/LLwJ9/+XX2Tk8b4sR7XutMivgB5bjUFtC0oA8K8Ao8Fo1DyHUhANujlWrYC9yhRcElOPTnSLWYkO'
        b'wmN0vJGwpZF7jVxeAbyW6FTl7KihiqcoeBAXaFXJCGuVxAc4eEkEW9ncYeiWIfLCi6yFAPbF7tqPNEue7d19Yl/CtpVMpd+Sv/2e7dkmDozOzJL9IbIn8g/b8jSp6oDA'
        b'hftPvNjTlLDtRNOJTtVeZlzEy88eFoLl08LKwn4hFXDGdMfDNXF2nbZwCLxPfRU3o16q7RgCj2PchvEQ3AFbBnDRNeIySNHYFMyAbiWKb07rjU5nEsU3OgZvUUQ1HG0G'
        b'TlEcoLN6ThS/v5iSGklxKDmapWnz4R7RUlaP9i94mreKGEtWmKvRlxNDBYqhSD1ODDWO6G0JRuLjp3mtc+Px+/mkQL/Q7j7m8Q4lcgWceZ1z45CSo1lH7Zvsv2+7MovU'
        b'8ncwFlu2xMXg5bwCz+TIMDGLp8esQIIOCCID5nlA0iD7p+UT10s14sjFEhhMWR1vq38ZT8+nb5gD5N1y7WyZAIdFNOxPw0IcDqDhQBr2w2ExDQfRsAiHg2k4hIb9cTiU'
        b'hsNoOAC35odbC9dFkLfT6WR4izC6QbrBuG2xPW2ILopcoqGT07ShumE4LVinwKlC6i3D1w3XjcBx5OoLppmPS4zSSciFF/sD9rP7eVW8/fz9AvKri65icRz55Dk/uVju'
        b'yedyuDz5T37Xje4OwXUFDNTzZBndGM+4/+ypG9sdoRvXzZaF6cP1Ybrx0eB4xAnQxNDQBEeI5oikZoecH5EIz4mf/ZqPQdQg0Y/Ok0An1cXiuMG6aOrYpuz3L8fkSjsb'
        b'88bUudtDze4uWXCmjUL6/kChU7ku+P7KdfLj6ZIWwCnXf1ZD1Oi7hYHTNeKZxWXcIXflmHYQxbSwfkWa4OyxEi5y4uT1zBfsoQxWqR32ZnAOoK9ugsfr0CPX94TmuB02'
        b'YbTR6gdK5hVVi0KnwZ20npqSMSAbvD9GCDRjgpcEgD86+khd+QyqTzezFtL/fXXjRrRdC9qkFPN/WzBDw791/OWR4umV0ln3nuVn51StMHbd3/jBZ7lDQ2peSZ68Z7y4'
        b'8UTo8vS0pNuvt2bceOVH/xPu9+vTvbaiwTmNqz8b/D+HNxQkRve9++HVPs2j4BeKp507Gr3o7C+l/pSTG4quRnGvV5LzgAg2o85S1jpjBCdvP0SPF8BWeDUvfyzqIpza'
        b'RDZMDw9SgT0Ftce4uJzD87DTcboIH6JO6s0NH6Bu3ZMuekS5TKdmfLSgBrUuoQd7Y1JgE+ccHhcj57LdhudIriHD+ZNxH05SYX007EngegvbqaIaI+awQLQdHSGWG5fs'
        b'FtlL4SPBQK58eAnz4EsqUCcPnpo0iRPnn6mFV2FrPGZeVeRdyiJ0Ax5DO1m41QBPW8m7+uAlwwbYugrXYaVMP2yHHYWEyy5Eu/SwSyEEGWohlhn60DUO135nNnPAC3yk'
        b'Kw5PFDIBAhETRb3B7cpSpjHcuW2eeGUip9rsF1DTpH4+sWztFw8cY5nq+v0Npnqbld67NcCCulqKC8xbyPdN5NEEHNznZrd+xntQg9fcmFAv/fs+vq6CctJxn06uWax9'
        b'Z7i24/T1Hj5waaiHq6vCrCZ7+Xs4oAeVu86ezy5lO7r05UiX5j3dvBXfz8N8YK18NTzH2fAIlSOzw6jye7db7fCxJuBTXmvw7eec62x2MJE3JFXmutr/dXva1T7by3e2'
        b'F0nbIya3/2FrwnJrnVVr9NlUkbOp6FKS0WGa67O9/5dcplng+W5ASi2uNNpfNJ761dKCQCtHimalC7lXkjd0GWMsK4ChafMxxkL03KeH/Ja8qzZHu18X8we1Vlz1vuZ9'
        b'8MmR6JJDz0dviU5ffNwMNK8J/b5aJGWs5E61qcvhdl8ojuK3MtiBUdwIdOoprCmV/yg2oy82c2Cz+YQXbQxzxQ7f3Zu6xAPpXHXTV3pW+8E3+Of/i3e7eopE9rVaM5wP'
        b'QrMP4iY3GRdO+KGWTkdhyeekBmbofsDAQYb/Ucr4FqLLu/mXZPpWYc1u3cJnD8FD8Mbu87yXb1dXaOmbFvP8wPKHwi11w6QsXSjzULjZ50LNYhyk6Ag6xCmFzi5Bd4lO'
        b'KVauICcIW+AduJ9NKpr4NAkjpJxaFhsa9eUVxrrKFQOvwXMs6ZLGaJd5d8/t9r5WATWJ9RQ2iDTuouHYgx8LPVb6gttK+27RbWM6FpvAleP9rTy83Lz/7Ws7vZ0p0eVe'
        b'FfEP5mMemL5kiWajaZkUUOsHwwp0Fl7kY8G+BZMs0AgvCbkX2e+QTYUXWXQ/HYC1YC1PR4+l4EPYRdfJwT9i6fE8NTEtjSmQMyAZ7hAGo+PwEjXI/CyUmnwoh6s04p9k'
        b'KwC1MFy2qEBzUtgSBOq1EW9GvbemmfOjjI9b67gcyc3I0A4xLqaF6KgNwBPocADqQjdiKTK0EYUQ6hyKjrmI40QUr4X3cuG9yYa6xb9mLXiAoP3eT8f/ODMYKqN4msyO'
        b'GUPm/zxTOb9C+67w5UddsvePvfjz0xUB6h+Frtz5bs84a59uoxkO+sdfhoW9rTz8fEvnjGooHTOzVBs1NjvzTy8crpivyMv78Pzzwbb7O8Z2/e3qL0t/m/HeqL4Dv954'
        b'+bpU0vXS/M+3LR68IuHnv31LVb56+w8E+8LeemXjht9eGnPuOOaFqEi+BF4ar3bRdOp5VNeZhO5xFxi1w+vw6hOXJGFuNdQoCsVZyD5DN1E35mSf3GmSIa5IEe805UJq'
        b'LhAGe9cHxtrZWmedo2AfhgDUhK7CTaiNmu0l5GdgdjQBnaGv5CZrDS9hmdmxhYVACS8IhxeN4HbvYbQZtrv5+BXB82u0nHIVc7nX0f4B1QLRK5Rl102OlDpfke1TvSks'
        b'X2U22N926sZ6lhPzMJYZiVnPoXazMTHTGOqy92hB95cya83VFh+MJWve777V95Hl8djqPW4vwfRorqCS77Ib3U547e/mpe5vznfz8unJkwBvcr5zkwvoJudvEDxNzSXw'
        b'2OTCAnqiqkCnw+E+HpZMbhETrVEzU6jsyp3T7hkTHzdXPl8Or/CV6CDwC2NHomOJhm9GxQgsxP7+xB2W6Kp2w9efe+u53t13991turtQtk16aPS2u03nmzLaVW2jD23u'
        b'E6hmgkuTRGvi1mOqTF+Lew9tXYtFE6JQgRg8WisSiL0HA4bV8GEL3I8uOdbh6cpsYTn1iKCrHeq62sZgamXhNuE0K6e6FrqY09HXKlMdkTsyP8/nYp/ISde6kyBCj7U+'
        b'HO5rrWnTvpeaWIA3C/BiC6lygSy43/dY8KrvphAQFHArS/o8Fx2YVUIW9gBxy+7LRPeZ/MA5htzBeh69jFNQq/1Io9a++IeYd1SUyZr5t/c1H2kMVbEHPtJ8oFlR9bHu'
        b'Iw27U5maZLt+Rmnrbeg9k7AjgZ9U38MD1mLxF496BpjR72R24vYqbaLPc1nZSNeVNYs4yxpiujnIZYoHynBVHfANPwed63gIP+o81nFflOs6em/kA3Ia4HtF07nNK7Bv'
        b'X8H3WE2v6h3P7etYTbJP09Lh5ZL4afL5qDMphwcEfgzmh7pLDPo33mUs5F6Cw+/EfqRROZczR/uhRqF9X/MxXtCPNaHamqq8yvBKzJTNP2BkwLkRosHl4/FOJQ2Ohh3w'
        b'gjpEkRcrpMbNsHPld3+bbn9wuf1qUZfVdGOhG8lqNka5TLFbAYfWwX0P9gurtJXWOrMPzMw3H/G1b4nb/iqP9W6NdF1vn52RhnDWuQPGusROtz9oQKReoV/TH9RQZ6us'
        b'0ZtpkQT3YGJ/YCW5tkVP3oma4BpI7BfpDBbuvhVi80teB28l9/DqbVYsSJI7Y8m27BfrV1fWaMmNpjhKKqLHX2aiTTRnkoeXG3/JQVgZrZHYKSX0BzjuVTHoXBzRF9Mc'
        b'VoPVqO8XkTdqkMz9geSbw8GbRtOLm2hNieaTpIwf8TWsqFtNvdD7BfU1dSZ9P69Ku7pfoK/VGoz9fAMu18+rMFRK2X6/rJkzC+cVlPbzZxYWzzJfJ033gSd0GGQRycoS'
        b'Hs1C7um03wkspGbJTLOoSvQ9WF6P7cSzV+2+nSo5lldatI75gn12mZ9SO2yrbSagJgAb/HIt2fA2uhWCoYhFPUzssJE2qmE7E4O6LNYGdAu2oLsh6GYgA/xQFxuM7qM+'
        b'6teDGaROeDyO2EhejsnJV6jy56KWAnhZhjric+fmyHKJN9IuzL9iDsvhMYT2LRbPTEWd3PUXD8YmoX1zAeG1Bbn5w+E92qWUmfB0ErwdlKzkA2YigPtQbzRlw3Pr4Kkk'
        b'FphhB0gCSTmohbuHYxe6is4njYpLVrKAiQGYwl6EF7gxtMHTaBu1CK1Bh4gCkwGBZSy6QiytKXZBRxehq0noAryVrBQCRgrwkO6iZygPDW/Bk7g8NXpN4eNh7wYCdI1B'
        b'+9gkOp/DR8SBUiCZzIRq2DUzxgPO+qyjfmTSBrQvWckAJhbAA+iUvTPWlKlqhVxB3OzyUSvcLkc78xgwBJ7mT18xi1bYlTcaTAfHIwX1miXRKxYDOkklyrSk9bAnWckD'
        b'jAzAQ/5SjsHvgg+r4lBLPOyMVKg4XjIEtvMqFMW0rgvJQ4AMSEYwEs2SKtDAdS5lJjqchC5mJCv9ACMH8DB6BnVxk9gxpl49MwLtoi8J4ssYeA8drKQ1vRo/FawDh8YH'
        b'KDXmjekLuZrmDvdLQi3oRjLsxYKWAsAueLaGptSPiCTGvvlypiIS+Cew8FA9aqYVKYvVYD94ZWlwqCbgJkZhnLtT86JJSXlwN64Ir3Y8gEcCptHzRu1g2MmZkakEmK/v'
        b'w3LwdnYs2oxu0cokE4g49Xo8O11j3L7ej5urZaP8kqzLkzF3SaaqE95Pps6CZfPQcTW5fmXPVOK4yBkxB8OtvKnwKHxIqwsPTwf1YHogT6Mxp0Uu58TBqRtlSSvgpeRU'
        b'lg7x4Hx0hJ7t5vnBVlpfa4FDMc6ABLR3KNxPJIcOGTdFIehOEtoOryanCunIDsFmDR1aDDo6n5QvHIlr4JYuuJ6XDq8son25uyACjAO9q/yBZnJp6BKOqcGixllTEnqY'
        b'mkjgVEYAaw96RM9tw9Ii7UDKoqPwIAbS6wzaj85Vchb9B7L8ksILUpR4UhJJsWtWWmFUUmGcmhjpMeg2fACEBjZ6JdxDe14qQieT8LZOI2XSScd3oDP0lBcegNvGxdGb'
        b'bZrhHRWWta4CIJ7MC4Xbsjg4al2OtiQlo51pZDNOInBxAV2lELsRPWNQc/eznoVbMEa4wAfiUN4geDeLDvu3weS64U2JAo1GJonP5oa9HJ4YngTPosdpyYDWdxhPe4+N'
        b'nv924fnFfSHuhGoBujMCCCvZYarp3HSdyYUdSehBVFoyBqtMkvkQvMzt0FPoWro6GW5Tk3MFto6ZDm/60RS4eRnsS/KfnpaM+z4ZgyLcCs/TKZahc7BFTVBZG2pj4P0y'
        b'IIxg/c3wGO15fmUj+DtomSwK1TQctqq5HQL7RoTDPgyEj5TJAsDMAPBYXAPX8e2wJwC1rlLn5ZLjDx56xMAj5fAcrUu2fg5oA68s8ZdoAkRrJnKAGIE6FLBvZI0yGSOB'
        b'mQAer97ItfEoBm5Vo+4UjEowC7OMiYftg2g1n6dFAyWIWhii0Sz5SLzcvtfOrYG96uLRKmJ5w+cz8NgiAWcH1j4dPkL7BAAdgOeoyWzPSBsRqOFVdGoG9UoozsGiLmbC'
        b'WuDu9cQSDbXkyzDaAWBOuN8w9Hgd3WiwF3XCw05fUkaJHgEROsTCTlyuaeBSaFZA9KLKED7QyEbz07jeTYO98DLaJwRmdBOjLhlGyoe5e582G3IoDm+Am1wOoTCl4YPx'
        b'8ILABh/DHXTVG6ZuQK1ziesLfya8CfjhzFJ4PpoiejPGHB1qdDqwFLVjiECHAeqdhc7RbjcUriU+0WvdvKIZML5QYEDNs+lMa9HVuehIIHG4acHTjv/kaBs9Sp+1VheH'
        b'JyS/GJ5Hu3LkuZx1fwIfTCgVJKIDIXTAKaFDQTI4twajviVClZYbMLpQDG+gI35gxFwAH+M/eFlLTY3hhdmwg1aKN95j11pZMGGeIAkeL6adSoMX4Xb1fMlcTFgZ4nH7'
        b'EJ2dQFOGouPwVokiFlPkdkzW1zLDUc8YTux9OB4eUqOH5nncPJwB6MYSdIIOZUoC3KXOiHV3OmfAKNjKR7fQwwgOn2xfvRodCQJjMK18gP8Ww1N0EtHdjbCH7G+FqgAX'
        b'U8kT+Xgg9cNgF99YU0PRcwzcFo6O8MAcK+4G+WukJaM0qMutIAtWocvD4BF+rR/s5jiF7WjLENQKQEgxMAADui2hJBVegbvRPmIniSn9LmeHQyJ4y+fP4EB+dxhmYPbx'
        b'iOflZqICUGCgoubcd+BOeIBDZQSe7PYPRnhzOLzJx9i2y0JBqhbdw4twRIDHglmL+8R/qhuDDWFH/OFJPWplAb8IrAAr1qBeiiLjrAVquBdtkstV8FJMLtlqEdN5aD+8'
        b'htkKsjbVGfAZdERMenAGwBv4bza6SLHM+lwZ5hBE8JSbJ+dceMcu1h6CWy0quC8oCKMnvPXQ5Vp0ioJXZlwAiAShyX6hGvG9pCgOvErx7FxFrTyA8ftxUAfqYKc/JV91'
        b'fHhLrcA9upxDXNDb1IVy2k3JMD7qxRTkEVVNyivHMa/gHStZZeL3p4dL/gHooKWY8eiFF/lgdgbRkC4UGKo7rgLLvzCTezR+9NJXXzJFZIUKf/fh0a83/M/K8DcjItqa'
        b'n+n9S+bmcVGs9rf+/6oKHr/ZGLnoQMfvAwcXH9v9PxF5j9kQNPavw78q+XPb7OGy+4/OX5EuOOif+fyFi/+a98uHLQ9HB+33L641nM57/W/hO8+rZnae27Did30/zRo6'
        b'7ocXhEc3LvC/9ucPr334Tap26Dsl7+xWz//RVemp/Gffizpc0BP20+ef7/vlvjtb0vJX/iL2SsaO7D9IbBMXZ/9h9OJnkrNvZXUVVOz50+4RBQ07P97yccP1Obq6E59M'
        b'3SN4ccNEv+zgGamZk8eZ77zydtieU9smvZC9a2ZBeobUfKHojzdePLyle1CGX8Zf3t3y4qwXx09sHXNw9IJL1X8c1P6LH4z6vXanOuHwqzFHviqf+YODKnToztczX9h/'
        b'YM0bF/Z8rTp89ZV3DdVD0ya99tkP7hU2LVr2kim0OOsta0qYzf9vsOqtK89e2H1m8qn+z8Kuvhc9r6n97YtvTAnpWxt8t1P4xZXxXVdVN+seTP7lw6BHR2uMMz4/Nv/y'
        b'lo5/brc+6nqmVtL3j9bF60qMtRXnIv4mz7AMs9wZu2/HF1defLjjr/9WxX8wfNqLqftG5W6bsy2gY/w3qg2/Cps2aM0Bdfux1ktvvnRr9lcz3jn4zz/M+urDx7Xn/rZi'
        b'T9o/D98Of/z7f8z/1O/gp3M/jii4+bOP/hgfdr1zRvlU24c7lo3L/9Ok1yZ1Pv6aFxv277ror6URVKE6sRRd4qwFrhBXsCcsKYi5QOh8aus/1IpOxNWJiZachV0M5odR'
        b'C7WskgUoUOtkdI6IEULAz2bgQ9QUy9n5n0I9xOg/pF5sRjdge0hDkL8QmIoi4TFeHdHFUy0xZqlmBcKeMfC8LMeh0Q1D93jwMjyJDlDb2NB8uBUz4N2Yo9/pahp21G4a'
        b'Bm9DjONb4zkTVbirGNOwUyxsFc2lxYfA65gzIA53VK2HumE3EOWzOtTHGYdhXPVojBpvk45CMrwGJgujkB6aNGzSYIfJWWos52qNjmVTMw5MM4+PxPj8ItrK+QASB8DY'
        b'DM6yuWfYGs6KQ8bKUqkRhwU1UyMOHjqH7jp04rAF3nPxEYdnGc6/7jTqLYKtBvT4CbsLanRROYXTrl9F9zNha/Rwd6sLanPhL7ISe9rpuOBuYuNBziSI9EKMmltXr+K0'
        b'm3EZAiwwXVlFdaBVaP8qVxUolwWdzKU6UEynLtKZHjIGncHCQuM4d48MdGo+Z8S8F20ePmDkMQOdwytBbDwaor1dhf+97Uz7eVodp7dZDcCA3mYjUIQzgxk+E04N8ohb'
        b'dSj+t/+y4YzHL4n7UDQilBlHXLCZKFyG/IsZETuUkTDBtAwxOyZ5Q2n+UCYSh9iPRYMbgwaUMrg/rkp6M9G5fV8fN5YrNaC8v4EfF4hiiDCfTsXQJvD6UDdrZLde+D42'
        b'p9o/7k1QoFng1P4xVF3x9MNzD10uaUQCnlRXTLR7TqfjjVk6FXdcY4wrXQE4lSChQSGDUA/E3CqAmyaPBCNn2y/TxDt8HCQnFeMmRIPoJHiAZraMgN1JfOLBDPcngsR5'
        b'nHj8kRILG0Vf+wGNJq9leiWgR3TDskUgdNwsAY40/n3VEI5XXZO1nvli0l3MrmrX/mz1dDsnfSAMXkzCogWWMgE8CdsqSzI5nu7ahtKkZCGOPwjg+Uo9OouOclJ0ih8Q'
        b'5+wll/zI/qnjc3WrB4cCSVSAANRrjGc2qLleLJwaBiST6/1wpPheXhqXM3lwEIgq1fBBkUaWO72ey/nPajGIqp/IksjFodlczlvZgSBSEigAoZq8m3n2OtvX4ch10QyO'
        b'NL4nGsNFdg/BXYrpYkiXOmYLuWtGG+Aj2F2SP9cgQu3zCIctaGDgPcwrHefkqjvwZkKSUhmDmjD3OI5s0SPwJm04YsRYkD39DAYUzYzPqjfaedztqBmdIfwCQLvgZcwx'
        b'pJhowqAidAYdCcAT1a2AtwC8NRa1cyWuaLG4f0RIRN4KeBtj4xFB3Jx3YsbjLNqHgWYBfEYO5PNQF234rVoBEFl7WTBdkzcmbyY3DinsjUX7UCf5FaBNsAezTNsBvDlY'
        b'QA2gx89ZD0lN6KJ6BBgRHsHdQNsJtxGWSSWbi4sOHJzmzsNsKBm93NpYIodX0El4mPDOe5hwXGALrVA4G16Iw2NvHL8arJ6MbnKi5gnYgUnhRdL7bZlrwBp0A7XRwQzH'
        b'FOwBvIiBeyJ6tBashdtQNz29pStzewJuOKacwSOS7U5r5PTKM374W7J5QoYygBnxO8MfT+1mLcl4CD01mto9meTylu3VDX8a95PXVMObQ39TD7KDRrzD3oXxu7t/YA7q'
        b'3PZu4pzX/xTmdzw7Q/AOv2WmctnE52YkZ3668f6n/dI7r2Q0HYwNPDG49P2tbTUxp46//dyQkxE//aJm4eyIv1+qeu+isEz9/zR3JXBNHVv/5iaEAAFBARVUUkVlF9lE'
        b'1CoKVECQCigqCoEEiIYti4JLXUAQV0QKiCvqc0GrILij9s20z9fNqq+b6avdW1urrbX99Glbv1luQgIJxbbv931GJrnbzLlz5557zp3zP/+dHw2d+v3VgNql70aNnHVg'
        b'zSb5QX7Vt3Ephf3/tvVUy8WWv1eUyo/tWFMxuTJUV5yikv508NvzJfP+BT9QnavQ3etz75H7b7M/z1h7vfBaaj2//Fj84ZHlgcULPqtNBBkbS7ZLX70x/IBv4vEWa4/g'
        b'93dHfJpY8aO6/NcTp58M/Cp80i+Bp5Ux4e1Klzecc8Sn0kvrGhak3iyPDq9RDw2pu1B9tf+g+DuzdtS+2dwQds0p8XZpUc7rNl/8z2t3nJYl37j/0s4t2z4D+c+9Ezrh'
        b'+urVjz2+DSnLWfKN9wA6X9whTrKJ6jGEBsdlrEePK+JuHAqG9WS+H7mzHYn+Pjju8CQL6tDAOUdmd4sWIAtaj34B6/ypZfEMWEWe8SPBxqk4rBE9kI/RcM0UVsMqKL79'
        b'yEiwLmYkfrwmYD8UZzbG8PZIPjLjD8E95Hk5BF4sBEfiQBlqEsPXq3gYLjQU1LgR8wvUwpYxjm7d4zX11lcG3E3RPyfBEV8siS8/CKxERsQxHtizfDZpowCpM3wOVeD0'
        b'AH38CRsMDwMKSVoYlmQgMyqANfQlpmuawH2sFzU2mvK8QQ2yBDqZivA7JqbvcD44mg4bqIXVIUQOG7JoYAdcS8wdbNOA46CKWA+OoA3uQcbevm6RosRi8QaXiCjhC+A2'
        b'o7wCTB9XZNMh8wFsdqIGYwM8ohgPt3WNJCU2DXLka2kCnYrgAbBqBTIzpvoFBOBX10hYeJgPt7pPJCbWsJnZRoGtzk64R/VhrXshl2SnZSQ8QvbaFG/lFMQIWB7YhbZu'
        b'IGG42aHgNJ7xHwi3d076F8ZP0+DkVuC0D9xJzEkLoQWwA2zA4QXgtCc57ZFoiJ0k5ulhDQVRUfN0LNyrIWEpL4GjSC11tdOICQaa4GHOUqvLI2N6HNwfTEwsZEhW62Np'
        b'sY0FV8FWMli8UkN9fQKQbXnWKH+QyxJ9vEKv5soEOCKPWFp5ppaWSswTsPrsAc7EznJGH1f0GYA+eNmBZBJwJnv05f7I50vhIPYL4WCcEEfM2vKcGcETER/PnopZEQF8'
        b'LXHotGmwAEaxaz1I3RnKdhIVd80YTrUmc2pdGkH9gg0V9FVNvhLJf9U2vNC/C2yLROiqMI8Zjdol4bw4klcn0sd16n/hSScaDUnwWjj2ikRlkOl6MtdLJgB14oykyBmR'
        b'CRkps5Oik3V8tVyjE2Bwv86O25AcnZJMTEJyetTa/POJI1QvoMKP1UO2+I5OTw3KsnIQONg7CJ1Fjtb6dBFCEsoiNP3cE/TF2/Tr2a7b9Z87grtCHweew29CqwE0aSDc'
        b'pIAXDNreCelyjAV1TOHPQTdmU7d5aT0nC0mRZkIkK6jtQ4hW++i/ZazhF3+jtcwTmccYR9EnRyCzlokMtLI2MluCfhFztLL2ZNmBLGNa2T5k2ZEsiwjtrC2hnRVztLL9'
        b'yLIzWbYltLO2hHZWzNHK9ifLA8iyuFaQw2CpZAN3sLVCjG9ZYC9zG8jsccBIEG7ZXb/cH/3Vs5t4suEcKtyaJEmyq+xT6ZhjQ8hpCWUs2mZDCGAFBDkjmuOIe0P2zEZe'
        b'JXULxJX2yCkYKhtGyGGdZIOI4T+CI4eNT4x+VGcCok7Rk5aiTZQZVuKFiT4wf5O0QIZHv6Irt6TJgk8KxnJzlE3oV2GWulCJWaUxBB0n6KUsmThBsLxIQ3NUEzx6l7zJ'
        b'KhyU5G2ts+G4xzBdD/eTTBiLaM5QTNwjy1mk4y8sQOvy5TKFNh+tExUhyRcXqmSqTnpas7ywpumo9CnAbZA7ZcvNA9sZ0lH1hhkWY/Hv9ZoZFnfyH2aG/X1i2G4ksGZh'
        b'+H+QGNboYhjkwEnEe5ACbbYkQ4FEqizKk/qbE2WsJDsPNZlNUnX3zFPbM02tGUrap+iR36WpReOQZjWOipkpUUqzMBU6+mmcKNo7oEsKZkqzZlYKU9FJ33oFGXWFGeE5'
        b'QdC98DskuZYIcc3nabBEkttLQlyzlXaS5P4JQlz9/U67nS5JFDLuggX/3gXTKwkulTW3JFHJcxVq1MNIOSEdRoaTn0TLXTZtAU4p/Yd4Z/vQNymvpTni1yyBZ0sypz0M'
        b'GM5ocTwN2LACdBhRsMrzulLPYtPRhCB2zSSxIzJqaZIcsdCF8WKYpIdxmYOq88dQMlu4P7zAPOts81JDpYSWxbje3UViuF/6PKn2n8PFDDK3BrTPy1TG9OFRMts+oAw2'
        b'9chmS9B7hirBsSAGnAFr7UDTALCW1PuykKS+zQsPyBQPtJ/LaENxHzQORI5+Z71qUN1ZdaxvspGQYCXcbANejAVtpLpqGxEmdAj3k2WKn2hLKa0tPA52w4PmaW07nToj'
        b'OdPgHiznKTuwD6yCHaTm92faMc4MI5k1JHPaK+PjaL/Ohm2w3FzFXnqnxfjsq8EBBpwDR+xwamZQr3hu4sd89QZUze01zf5vnncCk8TRzyueBNVGPvPTJ+zU2sxcsUuL'
        b'Q4owZJL3O6/MfauiUb1b2Sp752zbaxuPNijP1D746cz42VO+7v9hyycVc4d9ZxtfkO3x1bNL+l2Thaw7UNLv42+m/PDdrk9dXnh5+9IKlycpXx/8dniAS21G7fr6/BcW'
        b'3E27bfNb2e5KV/bjyqrrcapfeFYHw1e0Hva2pe5XSwGhpaWjI8y606GcG0Id43q4FxwwvOI+EWn8hnsHPEE8RnCsxMtQCTfErBgPeFwCGwTw+FBAWWJBMzwNapDrd8Gs'
        b'ewpeBE0kr8Ys6/kUWe6yVE+CW5NGXDkPcA6eoJ4zOJvCec7gYj71AjscMvVOoDM4S71AeAl5gdgdHYJunYNgEzht1seHex3Je/jRYAtozPE2445ihCNFNu6QxFIr1h8N'
        b'i1Nq8s4CLU0jbzD8hUzComxQbg12LnP4y8x7A+QRgzOM/LcVzGRCd8sTdlLfUhpckpjUsKRnl0X2hwUi3Eu4eBkXf8cFwAXExSu4eJVhfp84RtSbSuxNzskbKU019seM'
        b'3LuVzA2TlG/dJX86aKDBerIIZEtFUlCYZGdbRoy4eFUPjLhPjZQUZxiZUhaFStML9WhIFwmIYfCU3KgGAKHebLLY7lxDux603T/HxMsRwgoykLFksc35hjbdaZtGBtUf'
        b'bQ/ZRBbbkxra8+q0mqRd4ahPz/Zr6GW9nWJRAplBAjf8+sLIlPnDbRo8IEtt5pq0iXrZYAAZtenNUiwzeRdiCKJNzOYbiYLD0fHdS6JoY1BBJqNwjgeW81ttSWJfcY7Y'
        b'EJxu1WNwOp/csIKfrfr2mkZJjlkje8uiRHZ+GhIlY9KkblViEiUD4NjHT+JjjHxGywRMjXYypoAhhi0VAzNr9N75MzQUIUkuzMcuBPW1ceo1Dr4szSrUajhuIjUyVi31'
        b'Df6HeUDkuEtkihzCEqPhjHHTk+L6mySSRN2WyyWWM2MH43+xBlYjaU9+3egwI29G4qWnTrHs1xj3K7XZu92kEq/ILJU8O68As7ZwTh5JL2dW0M5xoFYrcgvIUKDcKN0I'
        b'utQShfFZKZC/k2uBgEXvx4wmFzlsrMGdwS2N9vbDb0f0xL54DwOzb7YlD4yMSgU5HvNE4b4LH9t7nqkc0xPCZ62Qq/86ligvzIpE+Jy8JT4++djHRqdT6uPzh3mjJF6E'
        b'I8qfUi09TdU9cET16vinZWySWGCassTYFNA7MUygHT3yNnkZeJtGe0vmjg6yzLtkDA/hLqNWTk9HUUAEJZzrUQkJs2fjMzOXWBb/K5KW5pO0tHIVfkT5EVI2g2tsJFBQ'
        b'zwL1SCZl+qKE3i2j9HeKWbGoIWRMQYWaDw60zCZmDKbRvzYyuk3QWnRHFqgVVKjCHPPkXLIFaGSQ/sAHkNy80hL8u5e8RPhfpEklavLGTJGdp1EQ8il1JzVa93vWYp3+'
        b'ktGY4lmuRcrVUAEawQoJ10VIQ+WjOy461T9FqsmS47eQ5qmy/CVouNBcokpt/kJ5nvn+95cEd9mNtCbV5izRauToyYHzM0tmFqrURCgLdYRESCK1OXnyLC2+9dABkVpN'
        b'IX6+LbRwQGiEJLZAplikQINZqUQHUAI3dZczt3B0mDmRn76DxpirRmEkVv7TiRVurr6n65expCM7u/53et7syhQ6kvHrwi5yP/VIND79HBU6Gy/ctwaZpFlLtLneloef'
        b'8eGSMcMtD0CTHUePtbQnGmYFo7pzY9KNoV2rCbNUTVhP1aBBYTi/HuoIN97N4qmNNanMzHlZfKBxYD+k4bhfxB5ANinSrXpV7pVMn7EWH9idWEJM0Y4ehXQJ2The8WhR'
        b'XoD+0DCX4GdQeA8s7wYUomk1QV2qCeqxGgJYNCEQ9CKsgVH4eRNq8TADwJEeGp1KNDVeIfFCNzk3xNFlt9wNWhUmUsQ09dwvP4mRbRedOkPiNQvuz1OhmxTJEmJZFCNs'
        b'ZWdlhtWcUPqq1Au1KnV3oXoy9yyZl8SU7L3lZzDRIk3e/PfOhiEo0AhJIv6SzA0KnNf7w4LoYUHkMMtXQw8v5UxIbhm7zT2NA4I9RYfgL7Rj9/0sa7GpcpWqYFSMSqpF'
        b'hTJgVIwCWXeWtRbZ3bKuwvVY1k+4AcsKqqeWkVaKzkNGGNL9llUTkQ3ZbDLzYljqPGTFyuUabFngb2RghfVo32UVlkRI8AQysp9ysNWKVqA+t3xR8UEY+kuPkioleKHH'
        b'I7IVGnxDorJHc48invGe9Aep2A/b6f7Bo8PC0EizLBOGGiOB8FePIzJHis42BimVnnYiYGV0hfCXZG6Y5R05NafnSO1hROth1BGSyegXtYTnBo3pcX/DrU0OMZ3Z67G/'
        b'9eBs7kh6fSwrawzKRiba5MhEdHksa8QsRTaqMHYKatrMHdkNVt09rzvH8OS6gp18nY9/ZSo/CZnAUGTSAbhjKgHCgRpwgsKSOCRcqzc57Eq6VeCLfEeGmZQpfsAP4JKS'
        b'XMqHa+MxPg/sAbspRg82LicH+GT1D2jhpeEI4vEdA5Ip4hWcBQeew8g9JoCRJQWAmqUkkjVvKVjTyTK3GxzW457L4E5S2XpmWele3g9WOKr5P06ZDOFZBDut/X3RAZgu'
        b'cDqOGgRH4xJoQiMGtoL1UXD1DKYkxCYX7lISjNAUe0KQWMJ4F/f7MO3y2O0MBYYfhCvhBXMZjHBVU+k0RWcSI1g3mYez+2wTew8qUjwO9BGoP0W1vL6Bv2bThESY5Fie'
        b'+94Th9C4Jc1r6wJG7okeevV4+is1a4Yc8xsXLb5+oCqcF+d5pSJc+P09h0ltc+68uWzcP+rTS/evi91+/rnPb8/YOsx/zDWN1ZHc4gd1aYrZHV4hS+tdrlz9BcxOFD2w'
        b'33vu8/K7MesnNt5vj4mfHn9FVTXnxpseI+e8Nb6o/Nr1EdvCrzfP07nevbyu5a13zrk8eDf3nOiKVNHSfO/i2z+8NS6moCX6dOK1r/PvXKyKXfvp6677yl9xXXzxa8+l'
        b'pSA4YmLl7Yb79uv/sXjCllVF7jYemttPBq6zTim8dHPwc8dsfvUWkfi6knmwxTcBbjfkIsawkIIwgvywh7tAA2WFCp9IMSHwFOUZApvTJviCbfAErJoeC44KGKGSHboQ'
        b'biezapNiWZNEScvASY438IitBqc+hS/Cvahm/SySHdxrdiKJTCPFuNLJs5ULs3C2JLAeXOieMQkeh8eCyIQdLxO0gh3gjIGXz5iVD3bYEwCQM7pB2uKnxYIzqTyGncHz'
        b'mQxPd8d0iP+ifOI43I3MXuHJZJPZqxXMdBEh1xPwHHieJHcS/o0jCG25mSuWxCG6oW9XzFQkNszQSGWyRJMkHp3vrXG8ttF0lc1TCe4tMKqkM6+n4UwWmJ2zahhqPGdl'
        b'IqVlMAfJw4Tjj5hKgSEPU29oisqRkMXoYBM1iYXvToQ3nKrJtqVWWe+xRN/57c9yp1H6E8BO2KzWYsjuRgGDBhEPbgbbl8+BdRTtgWuKh41wpx1anMUgTdY+C7ZrCFoS'
        b'VqbMTyYHIl2zneHB8wxsB4fAHtJce9CyWY+pght3f/lCytbrM2SaHpxhJZYXjCQq9BkZbNJDOXJis8ElW1LBJaG1z1fsAKxuxR7MsxRc8cMIp8BLvEkMBmy4jBPSaH03'
        b'mZNkAUNWiv/Dy6J7Ms72Wf/iBTJMUqbyX9Fz6J4P+9qHLeNWDl82lu5Z1cdu5nc8L0wwPG3Iimi6Z3uYbc6vDFkpbsnn05Vrlwmn2vGpSCt5SyhCfjpcZZuclJSEAwmO'
        b'MrwoTBt60YaCNeqcJgQHBgYyI8Be1D/7GbhKzoHg0U18WpmchC5qeAYLDqAtEbCRJpbYBxvAsWSMHNbjP+ag2/lcKKgn3bVsDNiBKhUwaRMJ/mNZIpfLoxS24qmhZxjY'
        b'4vwMrEwj6JtYeCgIo2+CGCXcFZQDqsnOsmfjCI7Dn4G1Wf5gH9xOHpqDYAWs6wRtrIEnOdAG2IwOJAmNO+LgluQkCZ/JAEcY0OYiBE2gDmwlg0mFTmpzl5x3cKNdXNbz'
        b'FFlB8kCn2rj6sEhNZWaKAyaE0H6d6SXySuKRlcrXvPRg+Y2B3qhfGWYY3MnAMkYKL4whVVQmObN72CQ8kAcNmMPSqzAzCO5ITgJ7vJlUWMdELLeDTaAhkT7Ty/xBmdo+'
        b'OFAwG1YyLJIbXpgAdil2u5QK1MgsYMq2tuRv4dh337Opuu9RGe75y5odZTWrd7ke2uXs1CjQaeXV6aryjx5LEie9ZXPIqfCO4/NRvrPH7e64f7OjtHpaXY1COvOzd954'
        b'seObj7Q5tq0j3v/61RGfJqjWJHquP1r8j7aK1ud96rPejV6bbh/6Dr81J/Xy3/eVnovOXr45x+nREMmVjQsl/9O04NwA/+N5U+a/lTJ1jufgmrt1UU3xx/ZPuP7bRF2A'
        b'9+PMpGs7b46ruN3H8/yjfvt+7n9k0+3Prt7etGLrk5ZvUwd9fl3qceG69OqRWVsPrh49Y1rJpnVrn4gbVk0q+/bZ1d4VDf658z9yvDz/QrOy744zjV9OSH4j/Zua2ffk'
        b'wDvxsHZmgjR91f0JZwUZw96Mz1D/2B5X8vhCWtiTWr8xcKPfGfuzWx5+2b+/SvMrWOHtTJ9e66fCVd1DIOzA0W4Pr9mgnUIONisX+5JHItokgudZWPE82AI6wEYS8TG9'
        b'CDQgu2caLw8eYgTP8JBeao2gz9kTVlEmyfzglvRS0B5MYvH7pcPVBrwHMnt261kGYB2FIGwZNJHaYctTTOEYkmgrG3BGQRGjq0C9Cw0qWT6PiykZ+yyFhe4HLbm2A4yT'
        b'gbLBYWnkIQ9O26QbB73QuJk0uMP9hXS6Qw04CqvhRdiMCceNACMx4BClLD41coE+EgY02pgEw4yHx6kEzaAZ40WwDRISwdkg7S9QsC1oBHvjTSAaDqCMD5qmT14BO2h8'
        b'z8lgeNIEpQFX8sFZ20LQLKE7tC6FF+KNARoOy/mpU6JANXiRCOnhB/bTcBhQASpMQ2LOgPWUZad8BjinD73BUAUu9ualyeQahsHt8JRpzsW05YUzQilx2ab+s/QhObDO'
        b'qktUzkJyHTWMJ9fT4Ag8YhJihOOLrNwtRKT8To4/wrNCDJMl3Q2TIgHH+csic8SRFZFId0cOiooBEo4EIsGib1sjYkVH7o98vhK6s1+KBtnyhKyAA084chHz7EOhDfuA'
        b'RX8iW45AjJgL3VnJzJ9EF34ybJMM6mqTrGR2maYN7NqMSo1tiP8OSRk2UbRdTRTzDF3WlGcQHB3j0oWhC+yAlwwsXRxFlzSR2h+70GcV5tyaOcTAurUanE7VYm6dzJB0'
        b'X0K2BTZElDjOIw9dH3Qn7fIlXFuwBVTgHE57lYpjvybw1c1o88ComxM24nSsjlG57zs4vrD3E0Ft7dR/r7RzrN6z8kp01CrnqYox+2dfkxSv/jlh6zvFfavublx0c1OD'
        b'e+0rMUuO7ZcX/KfVdd+Bg7qIBbeiaxSuTpKZ1k4Rmh3HTnq+PzAymy295ZVVeftHsKrs3v6zuYVD+zVnx30uAhduLRrx0Vfj7kybO/SXOwmFdosvbEt7e8vO/Idtovfm'
        b'7jy4+fAK4LrUOXzfo4hB1fUTxzaHPn/xV+8+VDU2uqf5TgVtYLWecwvdMWWAYrw8wF4HrJiIOk4HDXrSraZgolbyYXkR2gy2wuOdpFp9U4lWXQ4v2ndSalm5ElItFnaA'
        b'SyxN/n9pYkgnYRc86Eg4u1iwDymIVaTxoRNhg4F0C5TFYd4tFjbACgq2F8F1UtyA5wsGyi1keuzXcCmO2tz1aWjR1a02kG7ZhlI0/mZ4vgCJ3k/dSbsltqHHtoAL43wp'
        b'6RY8G2vEu1WRRRr2hesWYhLbPfBwJ+2WMof0Zo4nrInnRlrsUI51Cx5MoEwOp+BON0wCXAJOdpJupSwgcYcFoM4LP4V4oNkon0E2OEAPbUpc5jtKCc4aMW6h8zr7l1Bu'
        b'EZIoosF8umuwFYz/0J5Zt7Aq6GTdUi1meoZmlZg06yHQ58Fd2eXzuRmeLX1TSCuYIjQoXIslX4nefbtCtEoZxhin1YsIw7MMyaGtkeerKdCqC5uW05/yantxTS6g4hms'
        b'kLMYQp8ldCR0V0JjOqsnrt5/lD5LjJ8iTwSoLsnivuNEPOI2DASHkIegVhtMMivG3o2FW33AKm9eoiLNbYSV2h0Zu1u0G6I3naVo5fcXfTas8s7DtepPxtsO7jMp8taM'
        b'X05UD/0bM2ttiHJ/a+mCnI0u7W9dGfNk9MRPvz78xvmXvQ613S9uX3FrnWxRxdnftn865713f3hzz8Jvjm2XlStif/Dw7/fRjdKJJ21r/vPS/FsnZsoyFueFTt7nt/xv'
        b'8SWD+j1aOXLQvdX1g9Sv+14588mE9xPKRW3bP1463fNxVMmV+Z9LN7361mVwy/e1r5p2ZD6fNtS174otxUtCTwgOt2gy38lfU/OT164ToxT3m/wHPlbNV7/qfrP18uMR'
        b'0HZbSfC+jed8vvjo6J752Ze3fOHqVRj5fdyuuh1PtqsDbrgsLg/1KZ4V8+DK1YXuO1uDB55ccyj/YPjDq54fZPruunP1UOTbzh2/sjHzckZ/8qM3n1KEr4GNg5djlmge'
        b'zr6GtEU1MlKx3kuFLwUaXuuEWxvFQZ+HzeTdS8CMgSShdZqbuRc05xZ1f8Xi/t8ZjE9dIJXD19+MZguCIxVlZCgLpbKMDKJysCvAuLEsywvhDXnCIuUi5PVlRW4SZzcf'
        b'54nOI1leBFZC40V8B7sRK5hFLE/1vuEu5OvYjAyjdzRu/w/6gKf6wHATY0mxFqI5ZW9NMqbwwmZr/wBkPmCHdzOsmj5tKdwIqsBma8ZhIH8wrAftirDvz/HVm9GOI91u'
        b'Dq7CNJ5zRjlbPXlw13HSVOW6SVlj+85qmZy9uDa28qeHp0Vjhp9pHJjwWdS2GLe8z+of/fhP/vSIwzdckh9lDLt4Pa7hcJvv/EPPbp1SlRXvOOvDrw74Rb0488ypN944'
        b'0RcK2CmRw8CeSDu7ytCwD7IqJziE7y27bJMrSC961f7Bxfhn1yx2/PVan3Vve4iSvW4EvotsBzyWY0GjGD+Cp+MXzZit184a7AUnWHjICZwmzoUYHIDl8dNhzTB/2Ip3'
        b'xI9qJ9iB3AsbUE92SYQX8mgfYGucD9ZhPxD1QV/+EGu4gbxoDBE6xccm+CRYM6NAi1DAimD9ALIBWRTD4fpRQoaXDJunM3AfC09q8MuJcYGg0jfOiuHFj+jLwAawiwMq'
        b'XBoOXiSsb6gpDJO2Ay+BXd4srF4+nOxQrIDb1EbbbZHTsS+WBS02sIGcsgQch03xREFWzUQPdJKFEq7jJ4JjoIr6WkdgHVgfH1ucbsjQB+phNTGKEkNjCLvrVI7CVAx3'
        b'F/djYTtsyiB9kQLPoKc6sgL8irg9bGH1SNDGgnbQmE3e4CLv5QyBqZ94IVAM1i4u1sK2YnGxlsf0h5v5YANYySdVgcOLwZF4kugAnw+DTnUnPAoaWbgXOWjEISrmwUu4'
        b'50fF+/skDMbnDDfjZWvG3VMAylKnmGQtHvx/f291vdVsfkfdmNE+nSAIwi5qL6IpfkiyfeyXifnPdrV/PKnlQBSOh46vlBfoBDj6Vmel0RYp5TqBUqHW6ATYFdIJCovQ'
        b'Zr5ao9JZEcp0nSCrsFCp4ysKNDqrHKT30JcKT9Zjgo4irUbHz85T6fiFKplOmKNQauRoIV9apOMvURTprKTqbIVCx8+Tl6BdUPW2CrUe+KkTFmmzlIpsnTXFxKp1duo8'
        b'RY4mQ65SFap09kVSlVqeoVAX4nhCnb22IDtPqiiQyzLkJdk6m4wMtRxJn5GhE9L4O6Pc8iy92j/h3z/g4jYu8GyO6hNcfIWLj3BxCxeY41P1HS6+xMVnuLiLixu4+Dcu'
        b'vsHFHVzcxAXmW1P9iIvvcfEFLu7h4mNcfIgLHS7u4+JnXHxrcvlsDRr1YZSRRiXbHolycJBtdl6AzjEjg/vNPW8euXHLkiJp9kJprpxDFktlclmit4hYiZiEVapUciSs'
        b'xI7U2aIeV2nUmLVaJ1QWZkuVap14Bo73y5dH495WPdD3W5eIeZ1ofH6hTKuUY/Q59a0F1kh/dR1iY5wJGP5/ASWxSk0='
    ))))
