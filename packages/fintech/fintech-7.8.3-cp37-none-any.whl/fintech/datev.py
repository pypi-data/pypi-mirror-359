
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
        b'eJzsfQdYW0fW6NyrgujNvcodARK9GTdcEaIYg0uwHRBIAtlCYBVs425sAwbcwL3h3nvv2Znspmw2m7KbbMiWlN0kTrLZJNuy2ZJ3Zq4kJCOIs+9/3/fe9z1jLnd6OWdO'
        b'mzNzP0Ru/0TwOwl+rePgoUNFqBwVcTpOx29ARbxe1C7WiY5wlpE6sV5ShxZLrar5vF6qk9Rx6zm9j56v4zikkxYg3wqFz7er/KZmFE6bI6+s0tlNenmVQW6r0MtnLrdV'
        b'VJnl041mm76sQl6tLVusLder/PwKK4xWZ16d3mA0661yg91cZjNWma1yrVknLzNprVa91c9WJS+z6LU2vVxoQKe1aeX6ZWUVWnO5Xm4wmvRWlV/ZIMeQhsLvYPj1p8PS'
        b'waMe1XP1fL2oXlwvqZfW+9TL6n3r/er96wPqA+uD6oPrQ+pD68Pqw+t71feu71Pft75fff/6AfUD6wcZBrOpkK0a3IDq0KohtdKVg+tQAVo5pA5xaPXg1UPmwaTB8Dco'
        b'RLllzjnl4XcA/IbTDojZvBYghX+uSQbvvQeLEI2LlX7SN2O4AtmHQ2CK7wrSRBrzsvNJQynZTFryFKRFPXumUorGTBOTR5EiBWcfCBkDtOSUVZ1DtpDmHPxoPmnmkJ+a'
        b'x5fJRYOCt/eCHNOWTdSoo9USRM4bxWIOHyaPxtnpdETjC+QAPkVu02QlaYQaJCiIbBbl4nUJUJhOG77hR9pxE9kcXQ39aUb4OlTkh6/x+Do02c76ql1OHkKWqwG4oZoc'
        b'WbrETq4tCVhi51BfslWEm8l6DvpKM5JLq6JxE94ao0nHu5SRtM9kK43wQQNHinFdvKSMc8PCgc4ZK6EgEwCGfhjIDAMd4OIaAFtX8QAujoGLZ+DiVvPewEUb79MFXEMF'
        b'cGk00nmvoX4IyUuyTy/LQyxyxRhR6iwRfSvJfneaWYi8PcZ3SAAvh7gS0wjpGCFSESuuSOVCYI2VmBpCJqEzyOQH0SMT+4n/EoYyH/Pvj/mavxnXGP57zuRLcTZlD1dd'
        b'aQiG/PG/tsRE3UQsurXy6+DYwYqh/Mz3uP/0+7VJijqQPYbO8UF8GkDcRJpi8iMiyOaYTCXZjM8URmTlkK3R5DCnUiuzcjhkDvYdX0rueky4v3PMk4QJ91wfiE63wd81'
        b'oXyPE2p4Ev+lXSY0INdCW7X3hkctYOy+glnKOfyCYsSLYBjkzmA7zQ+4dXNlAdQwQkL2oBH4Eb5gD6Px27LmFMyC+AqEN1ZMW042MWwn9xfjg6QVKo7BR4agGNJKbrH8'
        b'z/SH11YYrnIpeYSU+PIiVj1+kBVUkJNPWiT5EYhfwQ2yLrePhvhgM9lIMT5KA0jaPIM0ZudH4DPRmWwJqsgZCV6vJDeEnjSTS/PwNRjguMX+aJwOtxiHTu4vsh6BtLcv'
        b'ZC382bAgPClk4/t7jbd+M23OX3oN4hqfHxb73uh+hfv9nn/rcsMLyru+PsMqgn7cJ2zHj3O+fjCxbkDylz87VCz62dv7grY+aE68Wn6i9Y+7X758aM4vkk6PI5LHKZGH'
        b'xrw1+acRSr15R9SBj7ctHfVJxEtf3igceOGobmDu6vq6vSta+q550P7NX37+l2eub5k42O/GvFemadbF/DopfVbKzsvbb/3+YtVK/Vi89KpCYqNkUleCr2lISxRpyXkG'
        b'b1BmUXoRRm6LSP2wPBtdiEOAWJyIIttkWUrSoM7OlSB/fIUHbNsQwSoYj0+URKkUWVGkgVxz0JJgslZUFUN22YayxY/v4L3+dA7tAUNh9W+O4VEouSuCijfhh6wRchNf'
        b'I9tg2jeTraRZJJ2PxGkcvoLP4zsKvoOPUFgo8ij82Z//4kHx8Ns+4wyWqlq9GdgEY0AqYB76mgkdgRa9Wae3FFv0ZVUWHc1qlVPknSDjwjgZ5wc/feA3CH7o3zD4G8L3'
        b'4ixSZ80KUYdUKNzhU1xssZuLizv8i4vLTHqt2V5dXPxf91vBWXzou4Q+aHMTaeeCaOeInJdyPCdlTzvtb1ZycFQWadGolXhzDCz6LTFZHBqFrzyLWyXFVrzNtSjpP7Hj'
        b'r7UCHnrK6IHJ67giEfyKjahIAn+lOr7IRxdUjwycTqyTbPAtkrF3qc5ng6zIl73LdL7w7ifwVYNI56fzh7A/hIGGQDhAFwjhAB0HlKFcEdwhncXmKZfN2+P/wKosEzm6'
        b'Qgfp46QVscjJrKESgfCIGkRAeMRAeESM8IgZ4RGtFndHeERdCI9YoOQfpYuRDFWH8ZNKov+UsxQZB6b+XmTNg5SleeWflbxS+knJDl2D9tOS5vLz+k8gXPTcAnJ5W9zG'
        b'/ANHdoU+n6c9rTVJznJnS14Wb48eHDBNNbjZf1762k/T9/XrP6vf+v6pb3LVL4asbrmskDLsHjR3TJRGmT/ewfiipCgYnxTVYuDutv6Q3rsX3g8ZHMkilIH3BkSLfBbG'
        b'2qjsIMbnUzWkKRvEAIUUyfBmHh/wW4ZPkB22fhQRzq4QU3qlUeMLdCEtkKby/fHaaazmVfjwXNyUB2xejMiByRJygCN3yVl8kRWNCyXHo5SZTEaQkes8uTAYbyBtoQre'
        b'DQVF3tYSw8gOWXGx0Wy0FRezNRNA570ohKM/Uk7M1QYLsFY5cwlrRdIhtupNhg4xFd06fGr0FitIeRYKF4uvgPOOdimeWwLpI9i1CGgj812L4FSI2yLo0l4Z74bsLsxS'
        b'OTDLwDvwimcMTQR4xTO8EjG84leLvOEV6gav7NHwjs+RQ+SeP2kBeGwBPky2FmQKgMvHW4pmUiaHJpIj0lAdPmPMTf2HgOYtN658VkKx7EVDTFiUNlv7eUlIWYXBVCre'
        b'HKcs+aJk3ov9XnluL/e7VnT4R7IVku0KMUMLvB7YOuCFerUbZizDO/BVGxW58D58G99gFHkr2apSVisjlxYx0jtgtRhvxPvHMwSZRh4AEW7CF/BNAUsEFMkdb6M8FR/O'
        b'JXWaPHK/WMkhvobLIDumClDkvSIEEL1yvc1o01c6cILSLFTqxwVwtWEu6LiyCFWJGYw7xGZtpb4rGvCWUBcaMAwACQqVuTDgcJA7Bnhp4/8MeekWDRTwnmkil7wigYAB'
        b'S/FehgTP6o3Rn64QWeOhyO4hfT7LnOEVCz4v4TfH22N/FXs8VpxQbUDowmJZybO8QsTgh++SjcpO6kCuD2Ro0GupbQSkTif1+LYHDjAMwNelAhK0kt2sFhVUc81JJwAD'
        b'yB58C7AgWuNgb92TAIC4tSvEy5+AuNUT4hIBnBSwHZIarcnuBe4iN7iHu4BPpa4KF/D3hXgHvqs57xQgXgA+FXI5g/gpqYCHnsA5qvQEvyTXTokL3jaMHKaaVSFpUCpV'
        b'+ZlZs0lDXoEgRGaSxgx8MlvFIRt54Ctd4W+PgiKryc7e3jBmId6Y70Y2yHV8ydjyEwNnzYdCkwd9+lnJp4AzJkNkn0htptYE2HJ+5qcl1dqGnWf1p7WfhIwtebX0FUPM'
        b'jghtlvasNqQMvdQ3a0Pd83v7XrbFRut0ukytzPCeiUOrVoZc/OtfHBIhaVhTLUhrgC6PYt3EtYChjPJI8PklGrIH0MSdKS17lhyzyWnyLLw+Au/oinYM50pG2PpCJuOA'
        b'eS58wwfwLkZ1QmYytmQEFrU5anyBG2cCtrQ+3oka4m5FPAEnpfZqKtl1MiWTn0OMC+FqAx1YIuRxp0ACv+lExCexHkhRJ0di2EhJZKULG3eGuWOjZzse2pYnFWLKrYsK'
        b'cQ3c02tXYq9oKMo1+tS/JWHyzHdb39RoM8s/L/lk5fMlL5dWGHppT+tPv8Zf7d83VqmjiNKoPas/r+dfUpVc1C54cd5PF5BCMpOYyMyI8Fdf+9E80S96U+aDcv4ZYsrv'
        b'C6yHkgtyH7T3NhfVmTBEQADfYIYeZNNAvMeNmOA74wC2+Bw+xSCP1+LmPNIUrSYtoFBJn9VF8iPwvlECTzupJes7hRlpKtlJ7vL9yYFR3oHeE2UCSdxqszioEtW0kS2E'
        b'6wV0CShTUCepoFmcVC7wexCAc4M91V3tLti3eFCiJ6pX8LkWqmErAqnERNkc6Ad+xcWCwQveA4qLl9i1JiFFIIuyMsCa8irL8g6ZQ0KyMimoQ2ow6k06KxOEGC9kNJGh'
        b'IuuTk8L2qAoJQ6CTUkCHQAvLeDHn+OGDZAGSAEmIzM7ky2ZyN9CfHMIbnTqFLIAvmfqMd3WCEkAPdYIvEutEVH04wBdJ2pBO2g7qwxGujgPVQsboqm+HdJoZCPbyb3tN'
        b'1ZcabVWgjsVoLHqd8Po4hK29x7SJb8Pm6C219nJrtdZuLavQmvTyBEiio/k2IFtvq7Xp5dMtRqsNIqlu8fgnMNq/7oUZ0lSZbVXpuTDD8ogMnUVvtcL8mm3Lq+WzQRe0'
        b'mPUVlXqzIt0tYC3Xl8PTpjXrvJYza23kvsWkks8E+FRB2TlVFvPT5PNW2WK90ayXZ5jLtaV6RbpHWrrGbqkt1dfqjWUVZru5PH3abGU27RT8nV1gU6pBmVKlZ5hhwvTp'
        b'hcD3TDEZi7U6lXyGRauDqvQmK+WGJtau2VpTZYGaa51tWGzpBTaLlhzWp8+sstoM2rIK9mLSG2212gpTeh7kYM3BzFvhb63drbgzULqU9o5q0XJHRyBKJS+yW6Fhk1vn'
        b'5XHdpsSna/Rmc61KrqmyQN3VVVCbuVbL2tE72tPLZ5D7JpuxXF5TZe4SV2q0phfqTXoDpE3WgzC5mNYb4YhSONPkM/SAO+S4wWalo6RT2jW3fEa2In2aMkdrNLmnCjGK'
        b'dLWAJzb3NGecIn26dpl7AgQV6QWwgqGTevcEZ5wifbLWvNg55TBHNOg5azRmMcVhZa69EiqAqGxynJotFtNZE6YfItWTM3Jpml5vMQCdgNeCuerphcopVQAbx+SztWA0'
        b'VwCu0Xoc056ptVfblLQdIDilKkebjnePefcWT+feYxDxXQYR33UQ8d4GES8MIr5zEPHug4j3Moj47gYR79bZ+G4GEd/9IBK6DCKh6yASvA0iQRhEQucgEtwHkeBlEAnd'
        b'DSLBrbMJ3QwioftBJHYZRGLXQSR6G0SiMIjEzkEkug8i0csgErsbRKJbZxO7GURi94NI6jKIpK6DSPI2iCRhEEmdg0hyH0SSl0EkdTeIJLfOJnUziCSPQXQuRFhPFqPe'
        b'oBXo4wyLnRw2VFkqgTBr7JTUmdkYgBrrQR1yBqotQJCB+pmt1RZ9WUU10GszxAMttln0NpoD0kv1WkspTBQEpxqptKBXCuwuw26lDKUWJIb0ueR4hQXmzWplDVCqJ/BY'
        b'k7HSaJNHOFivIr0IppvmK4VEcznNN50cN5mM5cCjbHKjWV6oBb7oVqCAwYCmzGTmVffKOtm4sgh6AQQjghb3SHCUh6RRXQvEd18g3muBBPlki90GyV3LsfTE7itM9Fph'
        b'UvcFkliBHK3Al9mcg1wC8gmLs+mX2VwvQIlcrwnuWa2ubAIgJuuBHZe7RYxKLzKaARoU/qwdmlQLUZT1ApX2CMZ7BoH8aK024HYWo8FGscagrYD+QyazTgudMZcC2rog'
        b'brOQ4+WARGqzzlijkk8X+Id7KN4jlOARSvQIJXmEkj1CKR6hVI9QmmfrsZ5Bz97EeXYnzrM/cZ4dikvyIqbII2Y5ZtXqEDQUnYKRt0SHrOQtySk+dZfmImVe0vO8t0bl'
        b'Lm/xHqJY92PoIb076eyHZI7vvmUPOe1psgGp9JbNgwUkd2EByV1ZQLI3FpAssIDkTmqc7M4Ckr2wgOTuWECyG6lP7oYFJHfPx1K6DCKl6yBSvA0iRRhESucgUtwHkeJl'
        b'ECndDSLFrbMp3QwipftBpHYZRGrXQaR6G0SqMIjUzkGkug8i1csgUrsbRKpbZ1O7GURq94NI6zKItK6DSPM2iDRhEGmdg0hzH0Sal0GkdTeINLfOpnUziLTuBwEEsouu'
        b'EOtFWYj1qi3EOtSFWDcxJdZDYYj1pjHEdqsyxLrrBrHdKQ2xHuNxdHG6RV+psy4HKlMJdNtaZaoBSSK9YNrMDCXjVjarRW8AJmimPM9rdLz36ATv0Yneo5O8Ryd7j07x'
        b'Hp3qPTqtm+HEUoK+2EzuVxtseqs8b2ZegUOAo8zcWq0HfVgQJjuZuVusk327Rc3Ql5L7lNM/ITaUC/EOqcEZivcIJaTPdBhX3Ap3MbvEdY2K7xoFao6JKsVaG5VL5QV2'
        b'qE5bqQc2qrXZrVSsFUYjr9Sa7cBe5OV6AU2BHXozAyjcihgpczfqWLHvzeylfi9MyXvdXTMyE1Pn7MhB+JY7RF42lQaa7phk4T3e7Z3qhJ2Wqm+59FyFzEK9jizUPGqh'
        b'Njdh74OaWi3ULNohsVabjDbLQJd9j3vSlkcN96uc5khmyxPxnIzneXEcs+IV+D1rTSG3qaNHYzQ+I0ayZH51Dtn0P2TFMyh8O/wyysqq7GYbaA0dQZMB1IK2oa3Wmx73'
        b'Fmx41PL97YCpAPxKkCioiVQu6DuAukYgOJCFWl47xFTy8bDh3Yf42ZWCPFNVYdbLC6pMpphMIEhmpaaWmlc6g50kLn2upkguFKNmNEo8rUarXYigae5hYcnNoFY/QbwX'
        b'Gpo8W1lQVmEi9wH0JhBJ3IPpk/UmfbmOjkd4ddhcOt/jHepRunNCmLhP5UG9Y2U7dTa5IBM5NL9OG5VD52OSOtX2IDOsLRvTChw1sOZMRsjA3oxmQ5VcKc+w2JxdccSo'
        b'zbTkE5E0W7y3bPFdsiV4y5bQJVuit2yJXbIlecuW1CVbsrdsyV2ypXjLltIlW6q3bCBi5BUUxkGERgAMFXX1LDK+SyQE5Dl6IJdOQ6zcrpJ3GmIhUkBpp2VUJafiulPp'
        b'FiyunWCUZ0dlp0+3mxczV1e9pRzoUy2lKTR+8mx5YprAZQ3OLNQi7C3egTdCkpcK04uYNkAHbqnU0kQXinhLcaFKd8XieyrmPVFAoR6KeU8UUKqHYt4TBRTroZj3RAHl'
        b'eijmPVFAwR6KeU8UULKHYt4TabG0nop5T2Tgju0R3t5TWcGeEaV7TInrEVW6SWUFe0SWblJZwR7RpZtUVrBHhOkmlRXsEWW6SWUFe0SablJZwR7RpptUVrBHxOkmla34'
        b'HjEHUgts5H7ZYmBdS4H52phculRvtOrTpwOn76R+QA61ZpOWmhati7QVFqi1XA85zHoqE3XaGh2ckxK8DLuBWsVcRM7JSyGJUt5OhiyPyDDXCvIw3c4DYpxjtAFr1OtA'
        b'ENHankh+gg53LdxJyZ9Ms5jITatDTPBIyWSbOwYbSCUurYpxEiUTe7yqAI6ROrg5sH7gNFSCNjDZuZIyeJveCNNic5mJ1SDo2owG42KtO/UvYlqgy3zsLmYIuqPbNqK7'
        b'mDRdLygWemMpTcoGqNF9Masg2XQvr7mbhqHf0LLWZK9crK9w2rEZE6RM0kJdq79X0LWMoY8exNwIeNz3Kub2Z6cWalaRddbsXLIlhkm6pFnjg3qTFnywVBwQjk96SLsB'
        b'Tml3Eecp7bZJ2/zb/HV8W3hbuCD1tvjoousl9YH14QaRzl8XsMEXJF+xXqIL1AVtQLpgXUgLXySFcCgLh7GwD4TDWbgXC8sg3JuF+7CwL4T7snA/FvaDcH8WHsDC/hAe'
        b'yMKDWDiA9sDA6wbrhmyQFQWyXoY/8eOrG9rip1PW847einVy3TDW2yBhVG1+bZyBjsyHPZ2lhrf46lTMIU7CzlWEQFkf3QjdSFY2WBcDaZJ6GTt1EcbSRulGb/AtCoHY'
        b'UOjTGF0E9CkU2gjXKVqcBwiC6oMNEl2kLmqDDGoJY5pCuSK2QzaVOl5PKZjzbYyf3O2fM1ou0Bfh0I9HDoXEQsFsGQaPx8z/mrpPPZYJ6oVLXVAEPKYON4+ZkzF1ueks'
        b'ZUl0lrIk0YeSZqGeEI+pi8ZjihQKnw4/ra4GKJel2Kjr8C0D+mG20dcgraDiFJtAALRVdMjK7LC0zGXLO2TU5dSoNTm8NPwNRpD5iithWVewtjtE02bPymU9tKRCuEzm'
        b'wD4/xy/z4ZmAnjii5Fsvrfer9zH4OdyDZA2yOrTKt1a6Usbcg3yZe5Bste88pBMxPUz8V3oEwmPS6D+10D1jrd7KjmK5ptrIXBzK9KouRbpEjAVVRFsp75yasY5DWEBu'
        b'qGHIccrLMUdas61LDfRfxGSgEjYnjVKo5Bm0PNCTMjlzBZTbq+VAVVPkOmO50Wbt2i9HN1xQ8d4LIdl7D1zbH9/Th6Tv64MnOoyVZ7O/tAszYrKdqY6OWb33hfIgSv2B'
        b'd6jkhRXADwD59XKrvdSk15XDeJ6qFsG3RFBcoSa5FqqAsNB/uakKeJNFJVfb5JV2UF9K9V5r0ToGX6q3LdXT7V95hE5v0NpNNgU7g5faPSwcy2CsfIrjTV5G7YcRrl1H'
        b'N7ujortanEtorBNbrS5g0iN/VRZ5hODDspjct9SCMt5dRQ6PqbFM86JSClQj4IiDsEToy1XypLjYaHlKXGy31bit4bHy6TQgZwFancFohlUDfZQv12uhY5Fm/VK6BVqT'
        b'rEpUxUUquk7V9/gOBwhHE7KAI8oRSpVHG6Kfz+mH7PQw5rO2IaQpB5+fSRrUpEUTQxpnUo/SzGwFaYrOVeLNZGs23k8252fiC5m5OTnqHA6R7bg9oAqNZrXK0gPpwbWI'
        b'ksJSU37IWGSnhAafIVt8yEN83WvdZAtpzAYmihuhco+KNywPQNk2Vu+vFTIUglBs9WBdwPFh0Yi5P+PbZA++4zpC1QilVcrILNJCDuCjGnxRjJIXSK1493R2CIzVs3O0'
        b'D2XHIc8tsmSnzU0X+te7P97nrWukAWptioaKcRM+R5oVc9x6h+9Y/PFVfG+e8erLV0XWWqjnucubBr/yru/aWDkK2Pj+yVvX725qvb1eJHvDJyZmeG67vP+UlL8m9gpa'
        b'96dTOzbOGLFhVOOODeb7k/dPvPtmnxVvTis9kvvLs2Mrgv969ou/Hs4InfnlgPe01hfEWz/VHvZ/lD/wrU2vj/zXV+0vdRRqPriy/MzSY+/2Sdgz7rv2KMXdhX0VAcIB'
        b'qNYMUo+bYlwnPMhucleEgkeJDGQd3mGjbIkcWphBNtPjlHnuUOXQAFInrh2Gb9nowc2xplJ/DT6OL8Goc+wOt9reuF4sI3esrK1JuGk81DFjpQf8ONRnmNif3EsW3Dc3'
        b'kzZSF6WMwA3zM5U8kuJ9vBIfIHeF3p6egE9CFRRmK3EDTDwFWRi+KAKQnh/KPHTxtkR8LUql8MMHyeZoBDWc5xNIXQkbimQJ2Yeb6DkuBiV8zJwN3ZWisBoRfgCRt2xU'
        b'igvE28PoYB2yGu2mA8ix+AqgFNkoVZFjpMk2irb3kNzFDyA71BiponkBm7aCgNcHX0JIbpUE4itm1vtl5KYfzcfsnCKooDFbCU3j3SKycTbZxTo4LW1kr2y3th1y4gB8'
        b'Wwz9bsKNgvDp91+eM+s8qMJcT0fS9b4GrZRyUi6Ekzme9DiZjB0pk/E0RcrVhjp5susAS66zI8ztlK4JCz0AZplEHxn0MRk5T8dMQT37rsqEUp2VZLhKsUq8nLN5TLtP'
        b'vS/RWrR3iLuDa9euuhycOccvcyyl/VmJFiEm93G5Cq7Dv7hTfHD60/IeM9chG2fSVpbqtBNCoZ4/0zrd2nOmfesg6I7anMw/AhiFTlllNi1XQGMiXVXZ93bMIHTMr9gl'
        b'UHjvlyUTHr2o/KaGl2+HCu0Lhbw0/73tVgjtBhd7ChE9NN7X1biiR0HjB3Vjg9AN32InD++hAwNcHeg/WWvVu9j+f9egk9330OBgV4MjuhUJfkDTDhyUFTsEhB5alne2'
        b'3K0Q8cMHHVDsJlP00PqITkh/j9zhpQ8eRwzYaTe+HrlOu33fAYMN33/MSZRrzL+xWcIOyY7+aIpweK3C8Dl6vflnzR/846uAHwUc6I8mHBO/uyRIwQun0c7gU+RoADnr'
        b'os3uhBnvwettlE6S++Q42eaFNJPT/ow6LyR7ejp/5lNMV5H7SaQ18DOmNsSNXrEM3Xj88904+8+jI4X5tVJfe6CGa9GvPc6ddalf4dfh41iVgj+/1Gqz6PW2Dll1ldVG'
        b'ZeMOcZnRtrzDR8izvENao2Uqpn8ZSOhVlYLqKbJpyzskVYDvljJ/Bzxor4KcMJlOwevvUhkDXef2g4RrEgxBDrD7NwQA2AMA7P4M7AEM7P6rAxyKYwUojr+ReFEcM3Q6'
        b'K2gGVLzV6UvpioP/ZQ5XOLmeOe4/he7INBumlmjlFfZyvZu2BjNiNYK2IxdONlDFy6q3qeR5gNVd6qFLv5JuwRgrq6ssVMl0FivTmkFzoUVB67Hoy2ym5fLS5bRAl0q0'
        b'NVqjSUubZII+daS0quhIjdSYBmvLUaVDWaJ1dqkDqrZbjeZy1iNXNfJIBqzIp5iR6Y7RVlBDR9e+d8kfYdNayqENnZMK0fJyah60UsXDusROZ7fUoi1brLdZFWOfXp8X'
        b'8HSsPMODjcjnsw3Rhd0Voy2PlbPDDPO/90hDt7UIy2KsvID9lc93ONh1m9+5fMbKqXETQMX0zPnuDnbdlqULDjRUeMrn51ls3ecTliRkFV5YG9FydUGeMiEuOVk+nxo0'
        b'uy0trGPQPTMKleqp8vmOXcKFUfPdD2x033jn8qfatBCQ04rc3YS7LQ4EAyazApYGLFdrmcVYbXPwLoqn9Mg1W1sZJmsV4K9e59UQAOhEc1NeY2J36jBgq+RTBWsAW6LD'
        b'C2zaykp6ts08vFu7AFsMgFjQgWrH0tIZ2a0+WpjWpUbgafplAHHHgutaD/2XW2XTC8uELX69raJKB5Sk3F4JiAZ90S6GBQiLRg+zU6aXVwFz91qPMCS6aJiZwyoM02h1'
        b'65JKPh2ImpMgea3FfdlRowigOr2zqMwEAxauK7LqvZcscdxYVFXGei7sn4yrsNmqrWNjYpYuXSrcR6HS6WN0ZpN+WVVljCBdxmirq2OMAPxlqgpbpWlEjLOKmLjY2IT4'
        b'+LiYqXGpsXGJibGJqQmJcbFJKQlpE0qKezBBUO7X9eBgWK5w8882fD/Emq3IUqpy6Sm9KHym9wBQ8kYWSCpwnc5O+dk4KzmYgJJxO0JxKA6fT2Vq/E9XSRD87eeTW5L9'
        b'Jd8X2cfS6h7h3UqNk6HnkwZ61UiWchY91zorgp4RnQsaPfwBPo934Eu+5CC+SnauIVfZXUVUVSWgm+J6cg10Wqr0+SAJ2csHyPF+OxMazuF2fJpcU5GWPiM1anqMFpqA'
        b'RkC1HYpPiEHXLrFTlQe34TbSSq5pSHPObLKt2mOI0TNJQy4Ua84gGzSzq0HsyMvOIjvFoC3j9f7k+GqLne5QTAsiD/xViix8Hx/2Q77zyO0snhwmN8gxO1Ot6+LCyTX8'
        b'wF8NFXBIhHdzeC0+TM7a6XFsfDaU3PAnDTHzrCrSCO1G4zNZoBE3cEg+QyKGWo6ye2Wmkn3TybWYSLkvh/hMLvnZfDa94hnMShIxX1mSPXf8QMSugSKHl+Ar1kCyk9wQ'
        b'2pQtwBtJPT8jutZOVWdyBu8jG2kGKz4eGKgi28mNbHIliuwQob7LRfg8TOsGAe4XcavRXwW1wNypo9X41CjSIkK9yR1xsBq3GI3zv5RY91FhBv1Z+WqOH44NkbyXYvz2'
        b'dx0H3zjos+QPve/j9pKUWQtODqyLPbWtz7jTMfJr3yx7Py68buec34X+5uv316OdoZvP7Nv66ayxP7Iszh5er3z987Uv/fzjUwVVV2e07d5zee+1x8YM/6I3ds1JPJZ0'
        b'oWLKmx/t+tufX6jdWFOVcvLdVbVv5n718/SPvvjql1r1rWu/9LmjtS4ecrnxy8N9f/H2UHVh1DPoguO+jQjRQndzi8g6XjC27MAXbcxCtRffwRc1+Cy+6cX+gFBUgoRs'
        b'xbvJfXYeGrcswhv9NS6Tiz3baXSZYLINodJ6Kb7eKdceMbqLtlNWsjoSZqVF5SrV6hxNNGnB9XitgkN9yH1xPNk3kFlUpuO2WZroiEzoAoAQb9Dgc/zyyfi2h0ga9N9e'
        b'f9PtIVk/rU5XLAhxTGYe7ZSZM+k5WRnXhz3df8Tsfg8ZVxvuknk763AYLAIF0fkZ5NzgK6IPem2HZQF9LKSPZ+mjmD5K6EPrKYl7P+7rL9TZWUmxqwmtq4lAV4slrnaY'
        b'FF/GxHp3Kf6d0e5SvLcRKXw7AnTUtc8hJXUECrKvMyjVVrK/9DYTfYevY0e3TN/hTyUVkA+pv5fQB9cwy/wcZJgaWUKcZDiLivJ+HsJ8EIjzwQ6BPoQK9IYQhzjvx8R5'
        b'fxDn/Zg478/Eeb/V/m77QFt9ehbntS53PblwedFTCK3T6AEHIbccOCfME8ijIA1o3a/joxJDtLzcUmWvhlQQlLVdOVFVZanRrHXKJpEgtkQypirwVKrfuzw6aQddam+X'
        b'mqga/P/1j/+X9Q/35TWWAkqIcVm1vkcP8ViPQnkhylmBV2Fs/vf4eXbbnLDehXYcS9wRJ8iz5ipqrbEwidXsXQ5dWkUFRmOl1tSNxDu/B09X0CO8+7p222NKmYT+llZV'
        b'Lab9pTEqeY4Du7QsLK8qXQSAB+3e+96gmeo/qcmxcQ7zF0UEUN5odfM7vWC77YSLMI6Vz7batSYTWxmAODVVxjLXapzv5kTbowroIKyeYGCH6+a7O9p+r5JGiz+hqHm4'
        b'c/5foGdN1i/Vlzuccf6/rvV/ga6VkBwbn5oam5CQmJCUkJycFOdV16L/ulfAJF4VMLmwB7x/Gr2eDsnRnPKAgsyVyJ4kyKxn8EGNOodsjla7tKmuShTeFuOD1uAHvon4'
        b'pMJOHa1q5CueqXhSeRq0lNW6xpfUl5FDGlVWDsiuPdULylkTafLFp0S5drphRK4G4XZrXk4eu7aoXeyofi7ZBgW2kgbQofzIzkCoEMJ3ChbgA3gfPuZL70jb5Z9L2vEd'
        b'O9v3vI3PzbRmkRZ1Tp6G3pEVCxrXCXyo32QRiO7XyV12tSFZi08GWyNzyJYIEJ/X432aGJUaX4jg0NByiWTGHKa/KMieeH9yC2+ZJSMtylzQrWrLeRSWIMJHQCPawLSh'
        b'FXZROdkHk9G5N001nRuz6OWecbhJsgzvzrMPYXonblrq6Jg6WgHNNs6WoF7kmIjcG+XD4GQQCff3TlKURTclliE7leVyplf4Z+FmKUKFqFBETrFp1uH2TH86QzCV28mt'
        b'zGy6G95KblCFswmfg1A22QKyP7lHjorQgv6yGeSkiVW3ok8/cm0WuQWvaqSeH8G0b3IB39YlzMPHEFO/540X7kttq1kDlTZK6RWoKAbfIRdN33z33XcvrWFauXxm5CLT'
        b'd8vihR33ycnCjvvlApMpNMUf2adCZDy5StrovLQ4VPXM6DkAvZaYrNmAC5mkuSBCARiR6bh1GDQifJNcIhvY7EnNgQsXkdvCnTEXIkoKyM6ELHKHNIkQR84jcp7cDWfe'
        b'DL4RihIMarAAo1mdCCPzMkP4ItkhRrh+tu8z5C5Zy67Zk+Fb5GanypsfQXYWyATN1ih26rYTe0uDyM2ZgoXgJN6F11qzlHk5MVTHy1VTpR9vjxBRpJHg62PxOaZMhywl'
        b'd6OycvBaO73pRiFF/vgRD/r8I9LGLt99WZrLP8/X+6Fqbfi7/Qw1RsFTgdTnW8g1h11D8J4A3CKNMXk5+RHCrTluTgqwXK5z9LreUwFk2wRy2U5dIsmWArx9tjFKpY6O'
        b'5JAUb+VjyPqJDK69V5EzGqYX8oYwC5dKdlQqRKxQCd5YFU42uhcai6+x23Al+OwiRyGyCZ+BYiuHMgsFXk9OLoQxztd4DDF4lbFj11LeOgH0o+YNHy7cNj6XTArZWF7z'
        b'ds2BNf/Z0Q/3Pq2YVe0zICh2+KzoYbpZR+wkuW5qaH5BqnJG+wcLzix79e7Rd/b+/aM3331n9huHglJ6Zefse5zZ+ty69y9/eSBr7m9MLf1yDL2+aUn6amRNb/U/t65E'
        b'j39Rc1yyd+2g9pOnV/0iwH7bOGa87czYwZKCVRUXVV/eK/j7G/IRM5Jtuz+c9PeMgf3bCv/9Ykjt9aOnDjWX+XSIzQey/7bgWvb43Ub7a69YW1+0/dwyS67OvfI+97j8'
        b'oea3J1+2XDw5e912+7rzL205dyK33TDT3PpLafk/pyxX7/lNbWPIiPvy2x8Onvi7l+7r7y+/fuOvfQofZWesunXwluSXQStSnxmUEvGy+Nrbf5ykurc77U7kJ3v+2b/3'
        b'b5PSazTfBP2nqvD1ubdG3/nP1aT7y8jm0tq64ncSWl8b/4fPJn5x2XJiao0ikLlq4LNkB71ZsdMMIaZoSe0Q+SK22ZVAHo3UeLE/JOObDhPEskxWFdn3DN7rZoCIwfXF'
        b'DgvEGMG8QHbhQ5SKMzcbDb6owgfFKHiOyDSCtAt3ch0hG+KiIlUK4B6wFvbBKnyGxydUpM1Gj2bNmJqwKitKRUl9NEWkLbyyUM1ugCQbyc2JmuxIKeLxgbiFXIoabxau'
        b'8dqzABjSueyc6IG9eCTWcPgqfoBPMPuLBEbTgvcuAUwX3DQQkq7kx5BjZIOwG9i+ZInTmSMM33Pz5xCcOfLGsgnCjQOBdHfZDCQ35jtcNW7i7czpY6XOx0pXl5JyLHqz'
        b'+KNhIhRKtonwZbyNPGJ9wpvIXbzdYWJ5Fp+jVpZz/HJ8CG/v4bYsRcj/kMnFm/EliJoZOrVwZoAppNLBGvbDBzjML51GGHqHnWCCYSGeepAMgdRenJT5kVCfkjAI00uK'
        b'ZXwQ8zLx42m4tq+HcaOzVYfJJkAwm+joQ08fBvoopw9636LF6DKluMwYbtYan6e5y9hPqFPvqljnqsnoaifQ1USn3WYxPIo87DanI93tNt0NrUzikLbobrjnFeeSep96'
        b'xLZIuXo/Zm3xrxe7rjiXNEjr0CpprXSlhFlXpMy6IlktdeyRl7vvkdPKh6InRbkgQZT7MounIkLJez4lpglzxqNCFvubMYwjTxqaWRI9pahcuAgdb5uxyDoTH8YtsiUi'
        b'JAoCQr92KTMbpwOPPVWAWwpJy+ycfHJjZl4GuTE7MDk2FqHBfUV4Xf/JjHulP0vOF5CWwqRYsjkxViwm+5BsCUfap+ODzHYdRu77s2ruLKc1cUgSyYFQdgtEMSpqrMrt'
        b'h69JjXg7QuPQuMpaZoqeUmaAZXsCcGQ0wnUJ/YL1jMHncRjITewQ0pIYn8Qj6WoI4z34hp1So7IkcioqS0luAgV0vzGcPMC7jJd+sVJi/SOVQMa/Py3vQa4oLuDmh5ov'
        b'Tk1qKhy2LfLK1/Ls8wHZpreGDQ5ryB184HGfreMmX/1KNg6FF7wwIejVv0bq/mF9GHP4j1PjNuzL2CQrOlN+n9v4euWfrvePPXqkacvC47d2TsoPaOK3P28c/1qUaah4'
        b'78Vhw+eefKVAOvHt2LeL1PKkzxO2vFgd8Odbuw6G+fwo/tLSubG73pz8yb816oGfndFs/arqwy+ev5Hw9t4zE7M3PVow6J++wTXW1R1fDf135fln5bVfPZ5cVzjCMDWi'
        b'ef/1A7+783Lr3XdPP6r/2B7Qem9ntW3NBy985Hs7R3Pl8HHNF8u2/2bE9X8P/bh3/vUzzynChLua7/iFsRv6fYAtn8Xr8FFuNlDuY0LiPbwWt+Bz+MJqoKoOmjoTCDgj'
        b'X2fxLnLcRVDxPV8HTW0MY5durpRO9+IeB+RUtBwIakCuwEj247VpHpZxcoU8YjxJgwSudZ3Uk8ua3GgQU7bG4LPiOBA9g/BDUTE5nio4D17GO3EzdOQeqdOwy97FQzh8'
        b'dCzP+MxqsplsiNIoA8e5LrOmN1nHkIOs8NzIIuGqeHZN/HCyVbgpnpMyOzq+v0il8fR+7IMviPFh0jrQXsKGqZiNmzVO10ayF29yuDeGLRLh8/ieSfAWbFk99UnGipuT'
        b'3Gz7ZfguG+4E3PIMdVQV3Empl6IE30fBQ0TP4jML2LyXaHI72aqYbMBXGV8FHaSOscFFJdRsTzbonZZ74ClB+J7gJXkIP4ohTfMWO261F+60Tx4uAHRHLGmnV2hOxtfc'
        b'LlElhxyFA/pFUvltxTSyJY9egoq38VVkD9n7dLT2f+uifKcvjXAtPmNLuk62FEOZDnNZZI6LYsqSeB7+CiwqACiy8CNmjErYL6Ahwc1R5kp3/kh5MR/E9+H9gI25e9II'
        b'zQvsyaeTMXT4CPZna4fEatNabB0iyPdDeZHEUkXfK10sx+ziO4zlmOBxgXNcjclYzlr0S3k3Lj9CR/8H/K9EzP9K/O0fuhgOhLNVNufhDYcB1uSwi1j0NrvFzNIq5Vpq'
        b'33czszyVbVy+WL/cCvVUW/RW6s8o2G8cBimryyjvMOZ4s2k/aa83CVYw2p3S5Ta9F3uTi4NK3SfMzSHeTv2EyXptOIh6u/BW3IivRCaRHfjqXJA1r+Bz+bhBgvrhtaIV'
        b'uCWXaT34QC7ZTVoBhKC0nVYh1VR8RjAg7MUP9FbKWnHTXCXZpVGpRKgXbhT5ivCZkXgfY8sHe8MSzY6m/NqkLZ+GmO6oVeF7UFBELgplpcPJzlL8AGjx0XgUmSRJXUwO'
        b's7bza0RR+HSsmy6WPoHxylzjYuC6uAnXFbqx3ayVjOvDcC4XCYoasOINPChqU6oFeeBAKr4I7FxbRsvwuIUbpB5jfDUjQGwFMoZ+9s7LOa8MCyKxARvfL09/Z8vhOcmJ'
        b'Z3b/ytevSSPNGmuYVvTOvHU/q6vZ9PuTTSfXXhkz/t+/899S9vL1YzN/3PzxqrIxHzfjrJenz15QmG2ufqnw+RdvX/2RDv/z7ge/Khpc++D62GXX27UbWn+y5oWjh6a3'
        b'nf44q7J49YrTbXcfpKTf+HjKwuI5/Yb0e6PviM1jRn5hVgjEm6w10E/65I0O7erfZ5/AmEMqPkX2A7k9SFpct//yI0CLOMmUkEp8Y1KUKoeHqkgDj09zmkX4FFNvRpN6'
        b'fBD4lvB1Cx7563m8DtT/9mi8nnl0c3GBXv25e+NjoCfMwhtZ+zZ8fDVlPz7GKPfvlGSShwrp99CLbtwNtdZiutI6PxkikEiTWNSLyeK94C8leHQzNQxInBvVcBTN/YGe'
        b'iEvg8fsnCNOhbnwRHU0ouA5xtdZW4f0y9GTkuIOabjPSzyJIXReii7u9EN3hMfi+iPOyxdhJqyjZsGpr6JvJ5E61nv6wGe34WLnaII+kb5FyILVWwZhN6ZF+GT3fSm27'
        b'kapaY3VkNGvIQRgt3k3DVnqFn85lkNZayiqMNXqVPI/az5carXoX8WN1sAGw7Fq5ocoEhL4HSkZB5DrM56Jkslx7JLxr8IEJ5FBKVCasjZmZIGxk5WTjM4WZ+AJpiFaB'
        b'AJBJNvlU44v4rnCN/MWI+fRrHBpYTFk5KtII4lghaOhNMfkgaygj6CUuGnLTB+TC9eSGYNtZO2ENacXn6JkMcgXfQCITB5LKkVThg0db8C5llA/S4utoGVpG7uDTwoeT'
        b'7qXhI1G4PTKPR9wsRPaRxmqj7/iJvPUqpLZ+9PL4lgdhXEbIhhWGv1f/J+s9bhwZv/ZF/3Y/7miL+GzQupJbWWk/0sV/9fn+jvGzrx764tClHx9oH5n8hr62bEbgePXV'
        b'8qJLYcf+dmrWy5VFFaGh8jnpoR320SeC1QHlkhZf2+HlFTGl64jt5+vqvjp+orxqePinH/Z5/MWMkFf31yze1vfi4etJr2yuPvyd7y+3yn+dPKN0/IyaaeRP6su//TQ1'
        b'/80X+gRpzl+ecuGZS/lxRQ8fnluZdi3nmCKYCVC5MeQEm2sEiskmJE7h8EVgI03C94YOkoscFTSp9MfumD9JzpEmfpU1jwmGFnx7PLlGri8VztiQU+HIF5/i8TFyCV8V'
        b'7B9toeQEq6ERZHVpLj8kfRBurxTk7KtxuJ1+xS1apabJePsE5E8u8+R+CWljpKhilUITjbfkAZVUUR3sEvKfxJM9+J7w2Za+QO4aaQUxefR8zmoeHyFrI614D+v8hJGr'
        b'KMegcrhCRb/tBfwgOFZUTurTWdfI+pFz3C5Y5/HJ6hES8pDVPAyfToyKIZtDB0WrlSoFDyTwsAhvXL5GGNQ6fK2YydcxoLVJx/GzBvUl66YIU7YbbyPrNS5s9e1Dzvei'
        b'HdtUK3yJ4pyRnKYKimNGJvO6if1gWg8Ikv9IwCvn551SyFlBFiZH01nqQtAo6mm36H3/UnyaJ3fJjWgVvt6TaeZ7aLYbnRbTNezp30J/fAXjiowdxAECDXKqYCwJg9ja'
        b'QBcdpaVzPb4UYPEk1j10khfydhJwGzy+e4KA1/Xx+HKAR8POE8/UPp9rmUZf6flhICqOfwqJ8IeH3/AnjtdTh3hdVVlxMTvP0yGrtlRV6y225U9zloj6vDOXGWZ/YRIx'
        b'4z5sBMJs9PofN471CEcL/XDHh8jhKyMTi3lqD0Ncr5G8Q7H43icfJAoAYCOujyqA68UPmjkgJWggM1qQQ+SMzEq/h2gNChKhwME8SGwN5AhuABGSWmHITrybXPPHp22U'
        b'ZviryRFyM4dsmUn3PgbFi0fE4I3/Qx8c6nIEQ9yFpfjkMpKeBEsSZMTDZBdd2mjYeLJO2H85yY3SqPDl2CSEb+ObSExuckvIjWJmJsrA13FzlOfX3PatIQfxjizGReIz'
        b'00iTOpqKSAmkfaIYdM8mPovcNhknR1eKrBQFL/141mclgy8teO7ytiOtcRuXcGU+H/InNwb490/PiP6o18leH23MLknW+PnPazvy4sm6uI1H6o7sVO/gRoa/8tw7PFq0'
        b'MHTZvy8qJIxO+8nJ4ShmmEbklEk4SojbHCIbbkCY0Y2QBW4qNL5Jdgk0p3WIzGm2Jju0guWabCePbHQdBImHUzpJFehx/R0q9OyZLIncIkfH0M1USMvVQdpCXr9iYk9H'
        b'SwJANQKRRF9M/QoYLenjTktGUnMrpR1ieFqWupaIuENMC3RIhdNd3r5vtJxGLXMhOS07jHfWv9bx8767jMd2TnErYODmqIgsZWZ0FrkF3KAlRtgTlZNdkl6rMj1QqLfj'
        b'r/Vr98suouiFD4CXvE60wbdIpBez77wh+oW3Fr5IAmEZC/uysBTCfizsz8I+EA5g4UAWlkE4iIWDWdgXwiEsHMrCftCaD7QWpgun34jTRcOa4HS9dX2g7QBHWl9dP3q5'
        b'hU7J0gboBkJakE4FqVJ2nkWsG6QbDHH0SgquXgwlhurk9CKKNr82vk1kELWJ2yT0R9ffwEMc/Sty/RVihadYyOH2FD/5rht2IBjq8uus58kyuuFd4/67p27EgXDdyAN8'
        b'Uag+TB+qG9UftYcfQXUcC412hliOXsxBUDjpI4M58XFcv9GbuQ76sHmS6BS6SIjro+vP3AFjO3yLga9op4Ncy85dexjHPbUBwQFRyr7gJ3WZxCU9msSf4tiYn2AS364U'
        b'tqNRZFlA1Ghe2I5u69+M+nEoolpWbdZOHCpEto9bxX3Do3mTDLp0LmsGYmIxeYjXch6Hyz3UPqASTT4gxywrKJeFhAv79KjvcETZ5+WykuHvjpCgj519ZEfsjMNfXcNb'
        b'ad//kTthcPOVwLWxAeLfbZlSIr7Z/sqQgEllGdtVsVzojncG1H/0RXHtg+0vSf37zM/7vW/Ls/3a/F798c+mLaqpD1v0cN6J13OkxT5lG39S//Fvp6Z/+PMMn1feK3/D'
        b'9pe386+Udkw8fbD/vJ2tCl/B1LuWbC0WPpGjxBeDRUhWyNvIPV4Qwk6aB+GmkSC4X2J2YOkYPpTsKRS07E3mFf4acq5XlwPgIJcdYt/8MuWUP6ELLyQHHfMyqr+kAuRa'
        b'Zkq1huFr9Ji2BITa5qgIpTB9kKnvIPE4fGUBa2/y+Ayhm7iFGZWbl02nO2v7RfhILbnC6iF3uN6deXLweXJoDII8O0VQ8Q5yUPCh3k2ugHjbFAOSpZo0x8/lQOTezOMN'
        b'eIvdRq9ggbx7/XDTUqiG8Vc1UPmruAVvzQOZsTGPbFFJUZpGCsrOVXJYIK1PLf91nsUe4k6y46Wcn0TG9WNnsh0mTa42zLVMnvhuoWCC7JAwx6EOMfU77Qjo3GwyV3X4'
        b'Gs3Vdhu7Hcu7Ii+xrKbvK+ljDXKKhas8+hnThfS/6SEdeunf0x41lhTTTvdw7DSDd6wJ91ZcJ64Hdd7v2eXwqQpq1VCq8pSnrQOL3Weuhy5NdXbp2yFuzXc9bq162iO4'
        b'fsUuKPXQ7AxXs4PVzuxOd8f/plXfYoo2xZXGns4cZ7ka7UNVALnBUlX5w1qr8GxNu6yH1nJcrfVirVFH2B/SluMwtbTYVmXTmnpoaKarof6FNKvTXdZra/97h5e7fKOR'
        b'R10/0ifcs8JR361vAoNRScDHqx3f7TaUUaeoebn+8pLsl1cbkTEsOZC30hMj0b1++1mJ7NorpZnaNl3ERxptgOGTkk/Q1/v7F+x5vj/94isquSF57LtJwdno3VLkLD46'
        b'y0nOGshtgaR5IWc+mT0InUwHY4SLfWTMSbjmUCmzNtSdEPy3h5oLulCbSx7GxK6NPP4O/v2f+rJqV0XHAa6CUgk7KTEp2TStPHbbWDYh9XtfgdIvjIBKubnZxuqQrzkr'
        b'3TL4GTdP+IjvNt285/YMmI334OvbzoheuaVl3zt8BaFFD6V1K15T8DZql8On8UOZB+vxhNOIkQxSuGUgUx1SC9PSyqhtJlKpoob+9XxCH3ykJ9UhuJh5+Bpr9cWlpqqy'
        b'xZ1fpHNCdEFtf7eJ9szt8ZFUCXNN9aZFbEEeZoYWeMzrAtyzHsDtvk3XcnTCl8olzo+migDCoqeEcPmTX830ts/DIPz6M3/jPheh6UEzS9ZETh6GmPdBOLkajc+JEWmb'
        b'jmpRLdkZx/wfUwfn4nM8mjAFrUAr8EGyhX24fRA5N9xNMCSHlzDnzsKIXCWHEnGjNAgfIg+YS+TwgdTD9jbnN6kkeuSqOYg5901YmTtOK24IFJz7nsvOQfYUiJ6Dsp23'
        b'EHl4+Dnww+PyoXYbPgJyDNnXO4FRPOEE4zFSD8KVU6UW9GkgCY+yLOSO8daNXLGVAm/Yb14f9TNlEB/XS/ze8ksTLwfN+FvYiz+W3+H4jSt8fWe/e3He60nnjdsOtD9Q'
        b'KD8bvfcf8X9OeX/zC+UZU1Obk/Ofz5qcW18wdVP1kdipDURheTk4vPHZxzmNYY/mZRff2p96tP/EWydrP/vVT4/r/l5sfUuywXB1+6ojyqa4Tz6ruvlG77FT3l//+m+H'
        b'3T6y4j/o5bMj/vXMlwofZvRbgveFMx36Fj7gYWvUTxe27Dctw2udrmmkWewmkPYBHZ2RwoPDyZHul1c6Pi1QQhnIk9Q5bIIv7x/pkFxdIu5QfE2Mjy8ll/BG3MJWrQQf'
        b'JjuYywMVWwHg+HwWbnHWK0XP4Gux+Kx0kCVE2ItvJNvIMbcTduf4lPzl/SMEK8MZfM7sNBUIhgJ8LbiqHJ/u/Bptt8ZFafFSi9HxtVEP+bKYkmmeGwLy5QCHB1cAVxvi'
        b'tuhYQc+PIGst5dZuaDdv2ea5xrfCY0GXNX7S41OUXZrLLRM7lqPHtqvjm7js5Jnrm7hitgUkgdUtZqtbwla3eLWkO6VP0mV1S3PZisUHn6nF9GJCI94wFA2NUjAdlNmq'
        b'8L2BPN5ELkblK+co6VVTPqH8EHJ4iPH5vD8gaxxd2IfPflay4Llt+Fc/+vWPLm+703qn7s68Mzh6o2LPsI136s7UpbWom4ftWZcwGJ0fLFvgcx6YMHMzPIqvTAedg1pF'
        b'MGAF+1ypH97KoYEVYtyQg+udc9+z+VhazA4iMAiHuEPYFMScHDwmmWV1Kiid3mzsE8bM0tOFdouF+CfyMghvh4exC4T3hnUHYda4dwBTo3G9BEAsZTYCCmafpwRzxffr'
        b'9pJcAaDMQ6i9GF8oUM4hTUlKvItDInKPyyEt+Ihxod+7vJWamY/kRHxWotG++FHEB2pBlCr5rMRoiNz1WcnjksWGz3WflfCbY5MT7FdPxNov11w+EdcYJ06oPvn1Hg7Z'
        b'8gP+Pu3bTkHzqRw+PL5YTQ1ybiDt5Q5Si0zwaKEuk73dZrazzNPB1vv51R5AvQMeVV1A3drPHdTeO/RYBwW8Az1RWNUSx7qW/LcA77qunQBn5LNpAdlIAb4zAdeRK5ki'
        b'JPHh8PosstFobH1OYk2gA/rzC5+VqF0Qz9R+WqLSflLyOUD985IQbYUhuyzs0rwyQTw7zfl8e/MfsIopaEaSLfic4IG8kOtDWlPIEcvTf+S2I6jYcbOnG8Q9pOlaCvHa'
        b'fm5T61HAO7g7pAZtma3K0g2pFlt2dgfnNngs7QLnpl7ucO62M4pgwXO205GWwr4jsFOZXqxf3hFYU2Uvq9BbWJE4z2B8h38ZvUJFTz9WGuceiO+Q6YxW4e4T6o9Lv8xu'
        b'o9ff6u027TJ2ZSvdJuoI0C8rq9DSC0UhSiFju1GWNPqgtz14u2iX7ks9w2qk3kRxHX7OO06MOrdD4UUsh81oM+k7ZPRrFzRzhz99cx62ZtHs8iRWU7zlAC3jQ8//lVYt'
        b'YyfCOyTVFVVmfYfIoF3WIdFXao2mDrERynWISo1lCr7DJ2PKlLzZuYUd4il5s6ZZztOmLyA3ywUFIIUqFX+sdEiOq3ilzGWYq5cZZE8p/HosI5GjSs9lVCYIv+Gxq7hv'
        b'zGN5FKudn1UwE7FzWz6LSYuV3AwGvOENpJ2c5CLJPnKb7eHgzXgbabXaaiCd3PCflcUhH7KPD8IHC9gZG7IN78VUXtUA78vMUalz8klDLr4QTTdWydaYrPzM6KwYEGdB'
        b'0FLgm+wAD2mdHzBFge8wp4BAvBHk1tYF5Db91HwtyiHNMYLD0nV8aVlCYmxJthhxY+guxF1ynwnrEtyArycAalOrXgJKWJgv+GTtzFwB+TV4M4+4CITbSF2RcHPFcT+y'
        b'w+WnSU7SUzH+RTy5OEcuHIm5TY4NhJKgvp2RIk4BNZGDQ5nMoIk0kCbqfZokRun4nIRc4UhrLd7IJjNFHIkKoxfxKKRkeO8pemEyQei8C/QpMXY+PgbqYiQChe4wucWO'
        b'epWSe/i+RqVU0YNuOUqyeQ7ekc2hvvi4eNIowWP7pwPlaNLIEzyqLln5bc4gwWN7tpEcgBojyUER4qIR3kO24i1saEMX4tYo0hCjUgsSZTB+0B+3iErJpj6sun+m9kXR'
        b'4nsIyUsWjB2UjwQ/jKs106G66fiOD+KU9MDfnsGMvg7BV8lpkE3Zd3vE5CC5HM3huzDL9ayy6gkT0MqI1RyKLZkVnLYQscmLm0o2JiTiy2QfXgualwrhfcPwPjZ5y8nd'
        b'JOoGlQNqkW8W3hfHwwxfJO2ssjqjBrXF9hPB5C06Yxgk9GwgWYtv09oqVgPQYxDenxjHesaTw8sFZy8YJNmOj0jxJn4E2YO3ssoya0DZyT4vRqBm8XnFQs/wLrKFXEpI'
        b'TMYHQeik87aTnMtmmtJYsitEQy9EaSJbBN/iILKejlQ0QZLIalzsk4aqI7IlqKRk1uWByUL35oTi7bS+I4B8dKS7K/BNOxUAE0anCNXl0utxGx2YxqEBuE2MNwNfucwQ'
        b'NxVNgeI1ZI+UDW6PvELYEb6E969ylBfAGERO+1SLUslhNevMGUU4Gil/AQhHyaC/LawQkGIkvvVsQnwsqQPlg41uF764RBB0b+H2Ygfa8iigVkKucqRtcRkrVoAv4WMJ'
        b'SbH4USlMSjwt9tDkcOrB98j5KA31qAMVcx1pkBr5/llkA8NrchWfxqcSUmLxWmCzXCrFwh2kUVhgp5PwHgcabsaXJpHLCAWME4XADAldJa34PhSFpXcPZm4s4EhBpDD0'
        b'vXgHOaoR5kuBz+aSE2IUECLqHYy3saH/pVqGQnQ5IoCD6WfLliC2Gx071J6QkjgRX0Wssr3kRrYwgltJvtANesxPI0Eh5IG0jB8ITWwU6MMWsr0SynHkNCBXOnRiyBiW'
        b'UATYe0yjwecDiwHTqrhJ+OAaBq+8AJqfNKVAp8cBMkbGCPPbTvbnaihNaybNHIrsJQ3nfUnjENbh6LIV6C8R3yLA6zkvL54kEAWgbxNATUyE9VUvQdxkBCThJnnEUJtc'
        b'DsIHQGXIorvOIoAnecjh/YBGZ4QblX2no+Z5I3xgBWddXpguwJ6c1Y2n9UEfgCJMgR754xaG9FXkYamGbM4mB+jRUP5ZLoZsIHtYTVFr+qHY6jwOpnLBqqFBAkrHVDyr'
        b'UVNnGHEtbhdz+HAS2Scc8jyLr4sED9f2wSqkGodb7YIRi8e78blsclOSEz0rE5Rg5RzBWYw05EQDGUJoRpjPQPxoMUONMRH4suugJ6jD88l9sofHO9fgB523Mu8rESHx'
        b'OBgjKsmOjByJBE3uUEQBaQUps3JkNIouIe3MOaJm2hLNE/twwG3E9LTh2lH4rMRu0bEZDyUXhpGmfHpCRYxqyBVxGLdQjNeyMVcWkweaQtLyTC3gAdkLEKhNYvS5oF/8'
        b'kweUOTSPHB2VJzH2HybMfINPAtnvDy93qTkP4YdTyHF2KjgXFUfBNOSQLZnKLEEFjBOjKQWjCyXxRWQ9G+jVGQNQYioQq5CSBXdGBQh0agyA/DzZD6Mnj4CiPaIXWe31'
        b'YVvvo3H9mi6V8mgI2Tl6tiRhHjktsJwb9LpLTb6SHNJKhTOwD/CZ4Wysi5GoAFhyC7B23IxPrOAGFUsEJL6CNy3TzAZ1aRPeQufhBHBccnIio2dKfA2v06hzRuPb7qfA'
        b'OTQUN4nJzXi8R2CcLYCmp8h+ED/JKajwPsL3S6exng+FiDN0XavUuUDUt0JptTJejAbifWITUOZrwmzexe2gku8X0du7bPgBgv9z2WyWjie7nMU3JQqleSi9X1wJK6eB'
        b'LU9yMncIaWJAGWxERjW+wlBuEb5EblFnRlevgzNSw0WLyNVBAmbDkO3MRhBJLg2Fnj4sZIOeDKvuMqNiFLGm4aMah5vDIHxDTDZPg4VB+9wfN+aQ/RLqN0mPxyB8z0pO'
        b'CRVfxqeo8xlPifPFxWixHTEihy/i62qNUqnG5yOy6FoLt5O1k0SkDZ+YJnhgt5BLIN3sD6Cn7yvxdYSvzx7DKFpieILbqRBg71dxyxyRaU2SMP+tMP/brYGB4yKAQsHS'
        b'IxfwaRnDtB1FfqhX9FscYFpAP02tQDfJ+rRCekwa4TNhVagKHwX6TCe7NnwRiG+ZZnyeHg5v1uQpWTflA8Xkcn9yixkt2/uO5F6DotUrCs2/Sa1aGCQYTgPF+BQ1nCJ8'
        b'u4waTtufMfpubpdY/wnMakypfeEbL5nDM0Kk73166MdLwt4ND2+uP3j5T+nrRvbjtb/z/achaNQ6U69ndm390L/PrMPbfhye/YgPJiO+HPSvgi+apw+KvvfwzEXF3N2+'
        b'6c+fPffP2W89aHgwLLDNd1al8Xj2r74K23xGPWXn6dWL37v284wBI18+Kz20Zq7vlS8+vfLpd8naAR8UfLBNM+enlxTHcp77Q7+9uSdDf/7889fear29PiVnyS8jL6Y1'
        b'Tv1Ibh8zf+pHw+YfTJx6M2Nfbun2P947vm1wbs3mz9d/XnN1hq7qyNcTtkteXD3GZ2rQ5OT0cSMtt197P3T7sY1jX5i6ZUpuaprCcnbmx9df3Lv+QO80n7Q//X79i9Ne'
        b'HDWmafjuYXPPl3/cu+WXPxn6oXazJm7vGxH7/1U85Se71WTP7f9MeaFt1/J3zm7/j3rvpdd+bywfkDL2zb/+5G5e3TPPvmQOmZXxa1tSqN33K2z49cXnzm47Me5Yx19D'
        b'L/2h/+y6lvfPvTM++NqKoDs7pd9cHLXvkvpG1f1xbz0IfHiowjT5b4fnXFi/9R+bbA/3HayUX/t70/yVBabK0tPhXynTrAOtt0e0Nn5z8cUHjV/+Wx3zeNDEF5Nbh2Zt'
        b'nLHRb+uo79Sr3w6d2Hv5Lk3L4abz7750c/q/Jn+w+x8fTfvXp48qT3+1eHvKP/beCnv04d/n/Nln95/zPw/PvfH6Zx/HhF7dObl4gv3TxmdH5vxx7Jtjdz76jygy9N9V'
        b'rx9ThAsHpPbMBgXiCYd5wUOAXKuiTgJk7xq22VGBW/HuqFylGe+jZxD2cTnkIN7P3BTGk70hIBmBTiFFYilun8rhBzmQxixvR/AJcg03BVcHWEBhOELW4ZbgmkBfKeqF'
        b'D4uq8JYswU/2wdiF/vhMdKbTzBs63Z/cFeEL5KjDwcuPXI9xuY0isYQcZW6jxyczu600jLTjphiH36gM30snx3h6WCRB8A47GLOCWYgpfaYOB1stObxuFtnE7AoReAs+'
        b'DGuqbBCMrIbLwPWk3eF/sepZ11lo/yLBp6zNj81HaA05wQ4980g8XUEP6IGUeIMlqckufBs3OZw2kI66bShC2Djn+65xO76N7y9xOW20kgvMaQNk0e34uKerBXW0OIHr'
        b'mLMF2W5n9vag3CIPXwvo0WRyTvC12CxiF+uDnrOLHjynBwBbqDaTTf2MHXMQNRuvS5Pgm9X4IQMUuVG8zGUhDSHtrozMQoobyRbhfPn+YXiL28k9FEz29qZnJ8hpNYOE'
        b'2neZy7kDZrqcbGLeHavJXm830f9gz88OkVYnmG6o86nLdLMGqairrpgLY453fsyFN8z5w4dxXX4gboBPCDeSno/m+kEJ+hvAyfgBnJwLYiVCuCCWM4TlDuF60dr52sBO'
        b'mwz0xcMbmJrbfugBNF4o1WnMvwiPs9QuRKUAl11oLfrVAA/fYI9eeN81Z0Y/4RNMqF7iMvpxzFrR/d55l606OXrSWjFGsFbYx/G6r5mNpCTgqznzkWAJpJbxNRjEPiqc'
        b'DkGJtiHL+gnnDi4MwvdxK+XRyIZb+uPdvYRbTI7ymQlQdzwSkT3xeG8gq/xSkmz0Gh7aLikJ2L9AjNh+3ZRy2dRIEYuMboxLFMTTwKBVa/aiLyUoVjvw4xxfQXDG90rx'
        b'iYREyvl2qoNQGXDmnULC1YWqhEQpc0U6tgTpQd8S1OflK33MX/L9qC4ewCnjhLrVq0Knv8ZNAr5aYvpH2hyhF1FRocse8ywy+qXqGCHnPxcGqJL5WIRmlkSfn7ZGyLms'
        b'X6Dhc8QiTX0CIoSc3xj9Yv1FEVQFyY5LyhBy5g73X/AqxyJNp3QDhcjLSdIKkaNLXxdNEPZJyIaY/IIcO3kIYuNsKltLajh8N8CPjS59ITmUEBsLAnd7ADcS4R3DSJtw'
        b'pq16uKq/qIHCavg7wzmHDH85H6RkKh7UovSs2mH+TGZYMHgg2e8HqTeBlu3GN9ckCFLQ9YpJZD+duFsAMgm+RQ4Th5y5D7jDA9IKyKIEYY9cUUJ4O2v2SrpkXAbdsZ9U'
        b'kh2cnC7YiS3kDlCyVrKT/VycCioX2QRiMjeA4YmF7CvGtLLByA9vHgzCchMTtuLI3hmkST3J4L5/mjUSHxSsJkfVtgK2b5RJdnNkOxemnMMGOUtC7kfBoliGCkjbMnwp'
        b'ijWyGl8fic9RsFMp997yeLJVQNL9cnoTDyzAFSAzDV1BNqSxHVwGj6u1EsMxThjNpxNWCwbkHc9dLmMr5Y827tWpxp/c/IS3JkLvD3/4ZeX2dHp7yqbymg9HvvqmepBP'
        b'+G+r0dTAwR/wd3DMsLSWPww4u/b38TN+9cdQn/apaZIPxA1TYp9N/9HkxPQ/r7n3546X0t6OksbM7jNJGfG2b//XZ07POMblNeQO+MmUN+OL2st79720ryLGXuM/8cGU'
        b'MXO/mO3/m53xlTZl+h81hXlHv70XcdC2IXBDYNRbEZYL8yrktsJjC2eM6vuTNWcfNr2dsCo7+tTA04O/C/lf7V15XBRH9u85uAcYFQ/wGkEjt6CCiMEVBARRUFFQUGFg'
        b'BhgdDucQ8FYkiIAoEsATPBPUeJ947VblcrOJyW42m4yJRjebza7Z7Bo3x7q7ya9eVc8wAzMTzOb3+f3+WEdqprurq6qrq1+91/W+71s659Ftn+/j2tbVhV4d5lu2ZGbM'
        b'qM2d6ekv6Pr/a1n8Hcnyt0LDs7WrqmMqtixZH+1963a/r+vuflfY9nvunX9/eNb792+fXRB8yzG9zeV9zZ8W5R1bUDlg0IOktzrfTvo6Li6nLPhCzop5Ycd9jx2cvve9'
        b'xx//ymvA6385dMfv26Pn/5g9dOeu+6h4xrsRMW9v+tcLI/88r2rz7TMBQ+hSMWomuv7NnmvFEaimp9dMWjiDpNzEl2IhHzqBGoiWEgiT/AUhaskcyo4fHUKMDl59wBvw'
        b'Kd5/HD+nYl7gXbJwMp1ykeCHyZwwo/EmOtFG51XAFDobrE4IJgwY81gRujoWncwhWaB0CaoCuP5MaEAuGdC1AkDq+OLjqIVqWfgqrllkrmWdjzdTtKiWtT+DRWe5uZIo'
        b'/WReDyKPE2mkCJ8UEAvsJK5hkPv2rLnM4QRtwReNTicT8U6qXKxZiy4ZWYPQ7tBUmPEF3KCF4qHolAvNsSIsCdQgI2oeXiP1HyNamUfsiq5hTOXZJERNTHdBh6S8z6nQ'
        b'k2IriVpSnd5bM9kjwvVz0YEkdJh3TCUio4tXEVAz0UlM+ErUkU+jtKDNmYN7Ki9Ec5mehQ6hrXiHjo+6dZqMgrpxScGhofCemjQVd4rWTyNi4+BC6m86tqycsQsF+Yeg'
        b'6goLt1Wi+bQyf9OtqA1fpPm2pRAz/qIDJxZCjIoOfIMNjZ2osyKFXMwZtD/FHGJ/bj3zWrhMjFU77gXgWxCMdw7DNYvpLYwl4/YAqED1AUZ1lOqiWhcd+KbMw41hVlWy'
        b'IZOIUgYaGbqIG1kIht1zoeXj0PVKkz7FXGXPo1bmy0BMu7FBgbixP4NNsFg+I00Lyn1aFxOD9x1VqXItVSqNRCAWGlH8XlSh8iKfQeQzhHxg24Mi+r1ojv78H3yMQWkk'
        b'QleBTAirqBKhM8VYrfLoVlygYhuuanaAVOaea6dI8oUVXanZYhWtR5WkBBErqJ5+pdL/GtBLAgb3pCUFT1zNSkiody512wWPXYOz0Y/T+AuWmagHJANMgd8Vdcyga/d0'
        b'VZcu+RkkOXNi58XOzpm/aE5CukGkVeoMYgDdG9z4A+kJ89OpFkgvj3XQfx7GQQMMaGCPaOEanEXSfn1CSTl4iD3cPRy9nKVOxoANjvT2Olp8XEXstrMtYY+jxo/UwUPg'
        b'JRoST1/mBeFLgBPvFvEORMC8yEnni7JC0AWLVWcj4wkNSmZB0Cpu9qQEpp7Gb4XQ9EvU4KQYTbRfwEF4FogVTgpnE12ri8KVolckPF2rO932oNtA1+pJt6V025nSubpS'
        b'OlcJT9c6gG570W1XSufqSulcJTxd62C6PYRuS5rFBRy0SuG9V9jsCPiUZe4KH2+uwwOQHPz2UOP2YPLXKtwmUIzh0dhONDyRW41njbTAhZK+UipWcsyFEquKKfLFOUsK'
        b'vaEY1SCoYVq/pMad6Py+Cj9KutpPMYw6Wj7Dk66mpCY8abEAMM83soGSQ4xxVeYPdBrAkSQvUcAoV/UkbbTYCJwPOGqeFIn8Ks3TlqqByxng3xAOl9FPQjheZZmORYSm'
        b'WPAeUYrNuV17sLQGOBlceKYvoMjhf9IFYmcWtxPIchQFKw2i5SVkX7FSodIXk33OZeR6yks1Ck03C2wv+lXL0FDG8NsuxH5y5dd93UyhofpAwHr/UZ8JWKHLfzQB6w/z'
        b'r/biWrUKiP+R/KtmN8HUDgjgbacV5LCtNpTI5OqyInmItaZMluUXkSrzaZhs+3Sw9tlgrTC/PkWP/CAbLBl/LKJwfGKGTC3PAzpy8tM8SHNAaI/wx4zUzGorLJtO+9Z/'
        b'vFlXWGk83xDyDPwAF60t3lnrERNscdH2kXfWaqHdXLT/Ae+s8Tln3c62ZCoFf8Mm/NANMwoHPow0vyXTKAtVWtLDRFQRiUaHU7BMz982fQmEc35qeldP9uqkfpaU0rtu'
        b'KFqtHprrzzOkbJQAcn5KhG2KV6IyWnCwVk+TSCfgJlqmg/NAzh/eFUypGObjVsBCkvqJvO1RxuKtlAQlCZ/EO8yKbS+T4MP4fBEt90SchJLG/k2llaxziGTlpuMTqMku'
        b'YSzF5Jn5RF9GW9zGEpX1QBauZTQmhSz0rMxTqW4uGc/pQdYnp6AWq8UmB6V3l5aE9nJoA250Qc+PRPtoaSNXulAK2lyPyuCFzmmcPobsXCFfbJ05ttue69HGi27EKDmC'
        b'DuHt82ix98VunBdRmHJXyWd94jSR3SjcqVptrVx/o7ViUWgXOu6GDvniLfi0UpXd77ZQC4rndy89DClf+6ur7sJYScLc1d8t9a+K+0zuJjuzfeUt6cAwcajIp8Nr2YOG'
        b'iAP6L86FtNRHl0de2T5w5/DWL0M+SvN87+1/3IoMvnz/PecpuOnO+zVXGu/GT/RuOBhw9+XyJ9JnrxZWVN/8+M0YvHX9scfpX/Vvdf3luF++8kbkzyLKT3zFff+LRnxJ'
        b'fvB80+LvHWqj5GuUAa7UokLVZaSxJuJZsB9RPWqmNiSuQ9eZp/cV3K40D0Iq7B/DU8/WE4OX0ttsrKQu2RZjzIEbidvE6KgzPoW3LqWG4ChcXUyyJeLdPW1SdMIJnWU2'
        b'L6wgXAsKxVdEAWYUs50l1HCXRlJLMghM5RvDqLWMtwuocRQWXMibfcTkw1dRPTX7tpewi2jzjIKj2Xh7T8v+pLwfs1IbCnA1GHIX8A5LI5SYjEfVumDauIAZTIUNwefw'
        b'RW0UGd7g1E52zKI6bYgjNxttdkL7fPx/MkXeBGKEx8XMXlvPxVEaWYFjN6Uso5elAUFNW0bWVqJz2CCYvQJJFyRXIbkGyXVIbkByk+N+2MHVuS+FuFtcUwARllowoc0M'
        b'uQ3cBxbB1nq3vK/wNNcck7ZkB6K2gLSBAR+7azJjmoVddplmnwr7KMkxU53sNGqhsVFPRvRoAVUFfhTHK68k2ak121TrSFbrj2e45a9XnEMUIzs1LjXVOJTVaKY+Pf1F'
        b'inOI9mOnNrmpNv9uDUneE1r6dBy6Bcb+NeojdupXmOr3gdcTZkrLj7qjRqXFTo2FFjWS/jUpOuZjWMgQyfRNh8kpNjVfxDcE3MrhaaVeseDCT1eXICqDkLdUXWkQXUmB'
        b'xORk7mDTydzIOOrQv88URUpgYuwrQxHN/DQEReaERL2KBIIiE2g4MFgWaI5dJtsUDE0ymdOrUMWVNQNYK/pu3JkqipallxaDicAsawhyxgOQ5Xmleh3P+6MlyqitvoF/'
        b'wLGhhC5RqAooA4uOV7YtL4rvbxq2kXRbIR/CzYqeC/+STYxBcnt2W3ikmbUi8zfSkti2W8z7lenkvR5MmX9snkaZX1QCjCi8EUcDuVltaPc40GpVhSV0KDDekV7kV1qZ'
        b'yvyqVMSeKbRBbmK0U8LpTY6cbDJXoKbwgGB4F2Iky4UcJrbcfFsWFh2VKno+cDBB30VN7juHU4HlBcFVq5Tan46ByR8YhyhXUoAsMLAYbGhyOZWBgT+ak0nmT/mXQhiN'
        b'0dMUbYd/qU/nPy0bkswGi5MtNqTQvjXDAqJhlxPJ38SJFB4gyw4fb5vTyBzmwd9GvZJdjqqENpRymMfPnr1oEVyZtTCu8K9MXllMg8AqNTAxBVPCM5Ppa9ag8fYbZJeo'
        b'yfJFCHtaxhmfFKvNYmqPOb0TqX5CmG2mLnNQjPG1kNljQvaSJ7JEq2KNKi2wTnylWEZGBu0POIFGwpVXwO8+cv7Av1iLQrT0jZgqv0inosRO2m7asd7PrM0yQ2ThQJus'
        b'1BPhaiqAjGCVjO8iIqGKyROXsCBkvlyXp4S3jNZpqEJkZLiwqJ1qffFyZZH1/g+RTeiRjdYm1xes0uuUZOaAKMiyjFKNljbKRhkTo2Wx+oIiZZ4eHj1yQqxeVwrz23Ib'
        b'J0REy5JLFKqVKjKY1WpyAiNH0/a4chtnR1pr8tN30CRrxajMmlX8dM2Kslbe0/XLZNqR3V3/Az1vded8NpLhdWCPdj/1SDS//AINuRp/6FtTm+R5q/SFAbaHn/npsklj'
        b'bA9Ai4zhk23lJMOsZFxv3kl2MKJnMZG2iom0VwwZFKbrs1NGlHk2m5c22aIwK9dlc0LjQXtEwvG/qD5AdFIiW42i3D+dzbE2J+xuTCDQnpOpkG0RHcc/hWwqS8gfGeYy'
        b'mIOi7DCnm9CElsWM71HMeLvFUOChBTmfP2Xki4f5JsLmaSagIjs1YQGV1LBD5k8ecn6Ik9tuuxv0GiApBOp3/lewzEy3S1gwT+afiQ8XachDStoy0XZTzDCS3YWZdvON'
        b'MhalXa7XaHs3yp66Z0u9pKpk3zU/k4oWa/Fmv286DEVzRstS4UuWPT5sSd9PG89OG09Ps303jDBRXoXkt8FYtjcOKIaUnAJfJGPvfLalWJJSoykZl6iR60miDh2XqCLa'
        b'nW2pRbPbllVQjm35BBXYFlD2aiZSKaGIKGFE9tsWTbRtRGdTWG+Grc4jWqxSqQPNAr6JghVpV7/LK62IlsFyMdGfCkBrJTtIn9u+qXASQHjZWXK1DDbsnpGv0sEDSVK7'
        b'6h5DLkNO9oMWHAx6esiE8MhIMtJstwkgw6RB8GV3RBbIydUmEqFiLxMFHZM7BF+y7EjbGXkxZ+QftTOijXDoaFkc+cU04ezxk+zmNz3a9BTLlTu7/W0EWfNnsvtjW1gD'
        b'uJqoaHGxqeT22JaIeap8UmDydFK1lSfSAibdO4I6z6bUohJxYkUiAC6D166QchRXFB5fziPZXkA3GJqNQtnwi2p6ko/WgXMeMgxAqLM+G6Vj4K6KXHQW70I3eZAdIOyS'
        b'8Bma/87cQVzwYqmQk+U+W+s6neFpVkCgXQq7Q3sqQ7nQFb7Uo3VlKtqW0g3DcssSohcK8Ukh3kKLKpyyRvDtiD87cmHyKUNFgXwAy1NoB2oNIicAM2AaeAOiEzNns1hF'
        b'HO4kF3EG1c3jKia6FIYMoCAfL2Ga8GVHruJ08uy02ws/iRjFVrlIi44AoULv4ERQVBJbichA13zMVw4b0C5JwHD8kmrN2IkO2vukmN+KO6u3zZ4pmivdfPzJm9f+Ubs8'
        b'+euTm2a87vKha+I3b8q8h3wyec/r9W5OB8657J/W/2/qB+Frbk/esOdo57HvuurTllZ2bE1+iPc9quz8YtrjZ45t2v1S7lej77+69/mW21vjHpcvui/+qjBVE//rSW0f'
        b'DZ+hy8z61ztxhyOyEndPuVX59S/vqiIeNYjqWyJKPpl2fOWi7M0jg34dOfdhBspsf+g75puUqgWzf7X2aGl4eFlVSJf+ubuX9N8+kzhqaag6PKnr/aMtc1c/v/rZjjrt'
        b'+sn3XnkuYcDVEbfiL+93GSl5+L331uz5jTcfXZnxRcmiAGfmZXkpCb9gRnJ3FF8GaAc6naPj4blHFvuhDiO8gzLadeIWeu5KdBHvCsK1acnohBjYPfBZtdAXbcVn6LrS'
        b'dNyMnrdYHOMmoU10dUyKz9M1I8k0X/MlIxYE6YWxvZeM0OWJDBLSijvQNYtQSMlaUzAkMooaM2ndmXi3yoL9TlQwxkh+Vz0lSyoVuKYIZbOSBZxwniAwbWxvQIbkJwrP'
        b'Dc5rdIUKFootVqjWc2nOlLhOLPAQjKbBkOA3eAe68qtTQupb6EO+Bwn6C1ZJTOswcoUi1SIIR/d7anDDNluScnmqhgeIzQrpjsZpupJlVtel2nzN16UsWmkdjUEDK4E/'
        b'EVcjNgVW+i8JUC/BD7ekN43eGCb4Y1bRmMH+H87MDb7sGsTiDBWOQZe1esASN4g5MTqBN+JTgrX4tA/Do4DYnoFaUJObCO+JI88Jl+mBNzFs91aS+1Q6PRO1YdL5+CqH'
        b'zw/GR1gouug1NO7wzSh5tnhoMQNpJgx3mYBfxI0MQsIp8UlfWgVqGi6fEBPDECdcPofOstgAntTJYcjj0bnqdp2IIUC63PqB94f0vcrcWWuKebDHvXK60/+sPnfW/dGV'
        b'LOcHenfwvUi6l5EbfHNBKsuJUqhDRpQgK1d9drUjy7k6izoqzFGPyA3eGDGG5RztR3dKf+aVK3m5kN/56jOO0KSkN0NyJSWOwQwC74LO4ab0OXPmcArcwQnigQLiAjpB'
        b'j2lRM74+ISwsjHSYjvTRYY50caeSj+oxf3D6HDJqhSm+6CgcOJXAoj9diMFXKbaZgVRww1jAqXDraC9OT8ZdFKci0IwDmArekU/3h6L9lekAfm6mcezRXlxP94twJ26f'
        b'IMZV+CAAhcZPRecpuGM1bi3AOwX90E3AnoTkurOoKDfmPGvElzh4kEoZvgRAeiwQQRduT06fIxORaRDv4dC5gY7oAJlDT7FRcQjXVpqH6VsQAkCT1WgDQ4JAb7fNcAZv'
        b'k9xBJbmzvlg9kHXsjSi6Uxa7PFf9i8UpPJ3jyUkS0q9Q7rVhZIjJcRtuVYNY0M72An+doqSk3MVvr2YxMVpxw/L0OagjgFvoxkWvdYPQ7mMYIPwoPrxC6z4hTEzuxmlO'
        b'iI5z+PpCtF8lePVPIu1kInN+/uSr4h08Xe97qXl/fO0ffh4u6zduSp8z7515slGjRv19dN3bUQcOLMx0vHWk8fRqv81RXMSMjrz3PPolKG59+c+VMaWfvumnbJ7z6pib'
        b'Hw5alvxcyJJ5t8ozdwUmHd/bfjvzzJq5b30coNyfkbjonTmGuj9tmjjUc/+j+4fub8l4w3F32rK1jRlPNnTkdt6Jbwv6TVzRPtdZWy4qddNKlyXGGeK64lYNfXAlcLJb'
        b'w+avv38nNeGIh2PER0+u57etyz3/25whL9w72HW0JuaN7O+qVtzqHBd9LC2sc9XnfsdW6bY1rPq6LSy2vvPZf1aPLXdsEm7c99fQjgubvJ9rG6t9o2CL6I2WXRmP3O+/'
        b'/W3W/Fezzi5Z33Xtk3s7ZmlGl7z21eioD3Y0PFTXJ/z2g7iKxS9cq2x/5hftrS1/eT3jLYWfbvb9h+PebVy56WdtAV409PTyRFTVa2omW3NRZ4+pGW8rZ84pN/AN7yA6'
        b'3ZNjzviMEl8Voh3LMyiPFWqpRBuIcjdLgK+P4sSjBGhfehY9LxBV4wvdMQhnRVMG2la8mzq1DF2WYYK6zs9gSJWYoRSmuWwx3tMzvgJgHmRTcVOCgwvaqmbELxdxI5n1'
        b'qWeMUsDDSDKW8ryNuBVV4boSfMI8dKmDjCFx96EudBHVxeeaewFRDyANx/gKW9EOX3QcVaM9FPFihLsU4x20hOAC52BfKzATdKIIv8SCnp9A9ZlMuxqBXmIKFr6Mn6en'
        b'z8Sn0ZkUc4xJyWrOA1WJ4lJRLVXBypaiBjMIKto4hMFL1NEMNnEQ73ROMQOXoEYilzzWiuIL0CV6BYERQldBL2gJ3pmEq1j7LhQDkob5Dg0ayQAjpFBaexDR8I6bhYgc'
        b'gW4AXMQTn2SORRsH4vq5C6xBhk7mR1AcjVxabM036jzuwm1EnasYbTNmnH2ta4VR6yrprXWVgZbFU5AJpULm3i/lQbKA6JASrQt0LqIkmjEySvk/5twPrBaOQjGP9JDy'
        b'bv7gacRzjVH9xz6dmfVL60VsBirXsJ4q1wZuv2XAw56VknKAZOcn5jfb/F9+s15KmnV+M6dUPcTIxgfdnHqQm+E6SS9+s0NaNq9tD0bHgawsfgX176NUZXhLJlOqLnCj'
        b'GXaTiJPDFRNRE8N6nsY7lwVRmrKVPkBUth9Vq1I91zhoT5Oj1YLYmIYpHihMGl/4Ow/puoMfc1ua1i5rEs1ZIZg207/jnL//dqFXwOfPTcyOTVHd85qy47O7ywrvbulC'
        b'Oz+b1nhk9Kcvf/O8/6noVcumu19PGt/uELXl6+vcvUnDbl54+eTcTYmTjw0etE56+pXKdXmvpS768oryuHDAsYPx12oEm7PfKWkwfFT+oc9Y33f33JR/5L35zifx5//w'
        b'88RJ/9o1ufhCe+JydXPY+/JGv2OlD0RfvuEp7Jq0TXI7wJOBEHegU0ODksIiaGxdSlOG2icxFNsVvD/cxFKGm0SAKqsTrkXX8Dkq8MetXm1OQbYa7xhGRNhxKvDz4Ril'
        b'IFviQzMwBrKIMN6dcxW6zjOcxRF9CexKxnCG2tE5WkB5Jt7Lk5QVzJtFJgxKUVaAGJEYanLCzeYUZfgg3hWIrjxLWz6XTJaHQVxC0GDUjreZAgdXzKMtL6/AR805yobh'
        b'037ARk9F+XZ/vI+xgYWgl1TdLGVEQ7tOp9jBmficOU2ZY8XgwAgqxNP80DkjRxmqXuTIuQBHmVzL5sDdeB8xq805ysbgxiFrFrMr2uJF7HoyA/vjJjOyId0Aepti8PFs'
        b'c4ayAagjeMiAn4SfjDJqUREe2FuEr+dCfO1TlIEk/MkpykaKjeGMN/T4/N4KWZmxCaRyS5wNg9wJ6VdqQP+eMDs9x5lj7frgO3qOo1HQdcpiLQPL9aAk6/cfvcvow726'
        b'RJJRIv4lh7OjWEimU+Eg/74zkMFdHCKQlfefwqKD1+Mts7Qm5dOBc/cR4gvEitlZiNoDBKmqhkv3RFofMhElzA9P2HalpAqA5YNPT17DfRo2ddPIMUtGyBL2vvXKOJ+U'
        b'0P67k1bsTPB5Pb2wpSP+zudrHo98PHzd4ifXPOs3dUX/tfCfNSeTCgr3PrznfVK51v12fVfLd7pz9WHjXL47pDx4Nbq0NSN2/M133T66uPXzh2kvJRY1Hzmlc7udjqR/'
        b'q/db+mh3fmol9h685pOuWqn8nX9UfRN/Nm3zHz+PGNGyUD81I/FecqRnA/I5s/3bnfUTXqwdk1R9xO/QunHNh2c82rs2OXtb8a13Wx+3BN19tDFmaqR35Osv7/EufnfJ'
        b'qL8OdnD3eW2v07bRl6Z94FAVVJml+a70rSuKzA/7XXzx5SXeMVH5p4p1R99S/HrQwYv7HnycvjO35nrF1/mHHGPS3/43F3+/YFbQVwEiGtGFmPWXp+A6oncJcF1YFJk7'
        b'8rOosPPFLfim5eu5gej0fOq83hlCtbMJC/De7ndtSevNA4/jU1PR3t6vzYb+7wy1p06IoBEZHzWrCcX7OufkqEvlipwcKmggUAznIxQKBRMFMiJYHAX9hc4+Mi+fQK+f'
        b'eY19FsROjLPIw+2Z9dxKzW9MT5fIIMzJMZMqPv8Prl6gedf0cEJLQVtnEX4/m2bOmUZnvWbH+T5oF6ojgr4R16bNQrWo0Ynz8BYNx9tKVV9s+0ysBfDuK/02D6+dTFQJ'
        b'L4fvv/lCOi1JvXVa3uT+mafj8subk2v+/u0l50ljLu/2nn1h2oP4XYk+RQ9an3z5uigtuvODgelPcvxu/HpmW+e5oKUvTt05vTYvRZp559OjwfHPZ1y++MYbZ/tjsXB6'
        b'rB/qiHVzq4mIfD+vJsYj6mDVay6F4sVlr7h/cyNlanW59N/veG69PdI53f+D99uJpgCT6jB8cR7MuGmwaFA/IinFiXNDZ4X4RXwol06cKvIEtKcIV6SF4DOQDWbmfvia'
        b'CB1ADZkU3aDwRPX4cgTrADBBwNglHdBfNALtxNfoTJeFaqfjPaEpybMDZztxRMI5o834FD2EdvgV47pxjpwgHT+PznD4EDqMzupAHUxJwUeCZjpwghR0PoXDbVnoPJtV'
        b'b2pzKNEeqaxwOaDZ3QKEePvgAmZVXo2fpOWPoj1KOOyaLCQ27P4cFpm/Ch13GFmYQuVjLR8SdKsodZ6e6gHkrknYEg7ehU7SZZylc2lXLPTCnZQIly6DDESdJI9kgJCY'
        b'W024nvamSoiOEHtta3AZ5PAPIhlc0TkhOr8YH2RBrGogRFwdPitBWwS4tnyFHp9bIVmhF3CDcaMI1YsGsNhIz7k6p1DeieTZqK4MIi26od1EHVqMT7MYS9VDvKHDx6WM'
        b'QC8SsbINXtLDDidu6GgxqkqMtogdPfz//pnq+Yi5/ICAsSJvuuEqlHLV3ZnFWaLmJBigEtHUnnrOaKYJUEEz0iBSK0sMYvCdNjjo9GVqpUGsVml1BjFYfAZxaRk5LNLq'
        b'NAYH+mbZIM4rLVUbRKoSncGhgEg68qUBVwugTCnT6wyi/CKNQVSqURgcie2jU5KNYnmZQUTMKoODXJuvUhlERcoKkoUU76rSGmG5BscyfZ5alW9wYvhlrcFNW6Qq0OUo'
        b'NZpSjcGdmHFaZY5KWwreoAZ3fUl+kVxVolTkKCvyDS45OVolaX1OjsGReU92C092ocM1f4Pfn0MCvHSajyD5EJIHkHwAySeQ3IPkM0hg0U5zF5I/Q/JbSN6H5A+Q/AkS'
        b'AyRAlar5ApKHkHwMyV8guQPJ7yB5D5K/QvIIkk8tbp+rSZJ+G28mSemxJ84F4CKdXxRqkObk8L/5GeaJD79NrNv85fJCJY8ClyuUitQAZ6r1ATMtsWV5ZlqqFxpcSY9r'
        b'dFqwfg2O6tJ8uVprkMwDb81iZQL0tuaxsd964BwMzs8Wlyr0auVUwCnQVwhiIRFcPYfYJC/6RuN/AH18v74='
    ))))
