
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
        b'eJzsfQdYVFfa8L13CsMwFLGBdewMMEPvmogVGIoKGsUCAzPA6DCDU1CxCwrSbFjRKNZgi4q9Judkd5Nd86Xt923CJrvpiTGbZLObsu4m/u85d2YYnBmT7Pd9z/P/z/OL'
        b'XO7p7T1vO+977gfMI/8E8DsRfi3j4aFlCplyppDVslqujinkdIJDQq2ggzUHa4U6US1TzVgGzud0Yq2olt3A6nx0XC3LMlpxPuNbp/B5sFo6Jb1g6hx5pUlrM+jkpjK5'
        b'tUInn7HCWmEyyqfpjVZdaYW8SlO6RFOuU0mlBRV6iyOvVlemN+os8jKbsdSqNxktco1RKy81aCwWnUVqNclLzTqNVSfnG9BqrBq5bnlphcZYrpOX6Q06i0paOsRlWMPh'
        b'dyj8+pGhGeBRz9Sz9Vy9oF5YL6oX1/vUS+p966X1fvWyev/6gPrA+qD6PvXB9X3r+9X3rx9QP7A+pD60flD94PohZUPpdEhWD21gapnVw2p8Vw2tZZ5iVg2rZVhmzdA1'
        b'w/Jd3pcxvmUKQW6p6xxz8DsIfvuSzgjpPOczCr9cgwTeA9cIGOGQYMhTHHmsJpixjYbIEVmRuAlvzsueiRtwS54CteH1uCVz9gylmBk3VYjvqNEeBWsLhawaHWq2ZObg'
        b'Vtycg5tZRlrxZCaHzk32V3C2gZCOGlH9EnVmZKaIEQpZvCMQHUQbULttMEm7BZWTNCXeDMVFTMA4dB43CnIH9YXSZA5xM6pD11ETboysgh41Qy1SfALvR10cujis0jYC'
        b'8kxaiw9Djgsy1LBscthSG+5aKltqY5mBeIsANUvxFejpGFLXxVx8BDWhLVHT0Hm1Mpx0GW8hET7M4NFCVIuexsdK2UeAc7Bj4irIKvJryPyyVSwbbF9BtgGAeDUHK8jS'
        b'FeToqrFruHyXd1jB8kdXkHRkgNsKDudXcPoKMSNjmOjpYcWRJ5ZWMjRy7ziOgYzJdYHF2aeXTuAjP5/uywQxTMgFXXG2JmoOH5kcL2LgryRoenH29/0ymE7GIIXo98yh'
        b'wr9zF8bB27ivucsxT1QuZQ2+kHDHZy97zoeRR4d+4fNqbEqFD0OjDyz8OrAtkA37iima8k5I67xdTDdji4CEFQMZWLmmqJlhYbgxKkOJG+enos6CsKwcvCVSlanMymEZ'
        b'Y6DvBHRyrtvk+znGnMFPfu/tw5CpL/NzTi73700u2R5it8mV5ZpJDygM49NoN76RP0s5H6+bwzGcgMEHsvFhWx9Iy9SjI/lQxSglbmVG4b3TbaQedKUE7cnHR9GBWZBW'
        b'wUydmmHrR2q6LcDn8A6oOQrvSYPHHfw0rWaEZTLeAcNX4m3pjBJtTLSR9U6F7XAkP2cm3gQbpEXEcCvZIQEC21jSwtGEcLIjItQAxZuzZ4ahzsgMukFVuHMJ2ipCG2bg'
        b'dtqZKbAHD6MuGOP4EAEznmwC/WubuljLbkg89b1toZ55OSYARcs2av6Y2V134E/rBOe6nhcFRUjEfmUnLxzzmzfsSoUxiwuetXf8qi93v4bGrfnH+s/eee3eqrZt01pP'
        b'//3Qmk7ZcP3kZVvGxk7avuZY8IqShMVd1njLU6taglJeTvO7nnX+L3/I+svFl2L/WPXXCdyChf/6hvvbvaiPuira16aGfDP394ePvJD3X9Hzvr/rI72StPWpxPWBQxUi'
        b'K8GfuGsBPqfGLRG4JUeZRZBIML6KjwYKcL16qpVgXHxsEtoXkaVETU/hhszsXBHjh85z+ADaj65ZCdabElEToVJkRSzHnXYsE4jXCUx9Ua1VTspfT0G3/Mjk2QAlNEZx'
        b'TB98HXWgCwJ0Bt9AJ6wEAeBWBeqA2W7EW/A2fAo3A85MYdH5dNyk4Lq5MIWZwI3Cj/75Nx4EBB8MGF9mNtXojEBQKKlSAZnRVT/R7W/WGbU6c5FZV2oya0lWC+m45Ikg'
        b'VsJK4WcA/AbAD/kbDH+D2CBOyprFjpoVgm4xX7jbp6jIbDMWFXX7FRWVGnQao62qqOjf7reCNfuQdxF5kOaeJJ0jcC7HYo5jxSx5Clnxj+RpI71OSZFHZOEWdaYSNUZV'
        b'RwASaI3KYpkx6LyoCN9CW3rtTPJPaP9L8a+OMAfAGGjZQgH8CvVMoQj+irVcoY82oJ4pY7VCrajOt1BC38VanzpJoS99l2h94V3K0+EygVaq9YOwH4QBqUBYpvWHsEzL'
        b'AjNRoQjsFs+iM5ZLZ/Dej7A1SwUu3SJD9nEgjWTGQeChIh4bCRoEgI2EgI0EFBsJKQYSrBHmu7wvI015wEYCN2wk5FH9a2pRzWgWUPjE4sgJEUGM/njDIqFlBqTMeemL'
        b'+8V3Sz4t3q5t0HxW3Fx+WvcphAufg/2zNWbjzP0du/q8kKd5RmMQHxedZE8W/1a4LXKobGr40Ga/uWnrPgsJnRWy4fk9XSLmwog+sQv/oBDT/WfGXfhWhJ1Ycuga3hIh'
        b'ZgLRcUEN2lFFc6BGXIdqI5z0VMDIIgUj0REf1IK38Jvnug++psZN2cBBKMSMBErsnsMtR/W4zkqwqxjtmk0wmToTnYFQMjcpLhRtjrcS7mIeJBxATXnAIwgZEd7PQhdu'
        b'4Ou+c2gqvibuH6HMoMyFBF9Ex9AVDtVF4pMKzgVIBZ52G4XZbklRkd6otxYV0V0VAI+gQtg9ALhC2EfChzWBPBSoHPn4/STqFlp0hrJuIWEEu32qdWYL8IxmskJmQgs7'
        b'WUfLpEqzP3kEOjcK0GpmvmOjBJ1w3yhurZZyj2wIJ+Ql2iGvjLPDHUepoADgjqNwJ6Cwxq0R5Lu8e6KCjBe4syngvWrZKj/cAmvRCoQcb8nPgNU04XWwoDNnzFICSXwS'
        b'd4j7FOJ6/eTnmzhLNBSZ+MXZ+8UEBMNKI99XabI1nxcHlVaUGUwbSoSNMcriL4rnvhhy97m9LHMwXmKTWBRCawhZ0jafmb1ghZs5avkCdME6EhI16mEAj5sBCW9RKasI'
        b'usatqAtQ9qA1QrQRiOQmChZT0R10jgINPhNthxt8XYqbrMEEYE9OXaXOU7LM3D5cNZuejTbxi8p5hBDAk+U6q96qq7QDCUFz0hIZK2Nrgp3L5MzCVyWkS94tNGoqdT1Q'
        b'YQ7imwl2wgQFB0L9Sx3gEHDQAzh4aOd/BRfV/SKYmMRa3GCiN0DgTYY+aLdIH7h1BGeJhSKzEvc8AhPWMh4qSj4v5hpjbdFvRh+NFsZVXWaY019Iqj98TiGgNHwpOrO4'
        b'N1Tg7fjOctSZayUSAHBRG/q4QAZuVdtpOQWMTCsFLXM23mVHJcD2t9rBoqS/nUZ6xxIAAxZ3GCiXAYpwWRtLbxgQ8UtMFrtbVK0x2NwgQeACCf2c4EDmusKJHfY9Fhyc'
        b'TXpHEKk8OBDGmS0T/neRBGuvvjdAiHJtUWQVzuLtqJmIcwW4QalUzczImo0b8vJ5zjQDmFQVy1jxLd+F2WJ0vcIGogVTvDCcAlGpzDsY9Zko0neNDGAtuVDgVz7r7xd/'
        b'BkBkKAv/OFKToTFQ4KnSNHx0RveM5tPi/yiJLI3cHlb0liZLc1ITVMq8NMAsmLp34DlrdKRWq83QSMrezRYwMVGB669dAi6T8JCLElEtYQHFElcmkDCAhyt5QtOJO6QE'
        b'AAfhYz0wuHx8NQW/ofhEiQv0oTOVrtCHT06mdaBTaB/awgPgXLTJgZZybJQIzsPbUDvQMslQBzUDSrY0VGGnJEKvbCMPomJbFeEWnWRMapBQ5lDGcg+DuBp/O8jwuVyR'
        b'FE+hnJDptg0AX/XQMAqg/eFR6QDQ4J0eALR3a25CXW9UReVpJ6piG9ifJcS5oSqhR8gU5Oq3DniXtWRBRO5HS9SajPLPAXZ+W1JR1k/zjOh8yMBopZbATpPmpO60jntJ'
        b'WXxWs+DFub9bgAvwDGzAM1784/NzBb9fuqHP3efeAok6NtD8KSFVBCnlo2fReh4rWfFlJ1DMwsf59T4OIF3rwrvMmAXLHYh3W8kMjnkSYKopMhO3gMQmXlQ2nRs1aymt'
        b'Fl1GDRNd+SF0AJ3mQnFztWcoeBzmAnbfYjXbsRaR6oOswQATUoCNmoAeNEKy0FKdAn6hvcMDsDY9oEBEVJsTV7V4AIVHGlFwuWYi0yv8CetFyCOIItKiIl4LB++yoqKl'
        b'No2BT+GRp6QUgKjcZF7RLbEzWhbKTHWLy/Q6g9ZC+SlKRSnupPBJe+bAw4+VuviBkKnJJwMh5SSMkBOy/E8AJ5PIREGifhIqj+PjaEtfP4fQIpENmMcVmyK9yywq5hGZ'
        b'hSsUagVERtnPFYraGK34EMgoHWwtC/KLhKoxfbvFU42A1lc86DdFV6K3mkD6i1KbdVr+9R7PRNwjTTwInqMz19jKLVUam6W0QmPQyeMgiYzogSxbZ62x6uTTzHqLtZOj'
        b's37v1zDib/bCrKpNRqspLRdmWR6WrjXrLBaYY6N1RZV8NoieZqOuolJnVKS5BCzlunJ4WjVGrcdyRo0V3zQbVPIZsEYmKDvHZDb+nHyeKlui0xt18nRjuaZEp0jrlZam'
        b'tplrSnQ1On1phdFmLE+bOluZTToFf2fnW5WZILGp0tKNMGG6tAKgjoao9CUarUo+3azRQlU6g4XQTANt12ipNpmh5hpHG2ZrWr7VrMEHdWkzTBZrmaa0gr4YdHprjabC'
        b'kJYHOWhzMPMW+FtjcynuCJQsI70jQrvc3hGIUskLbRZo2ODSeXmM15TYNLXOaKxRydUmM9RdZYLajDUa2o7O3p5OPh3fNFj15fJqk9EtrkRvSSvQGXRlkDZJB4zoElJv'
        b'mD1K4UiTT9cB7OCjZVYLGSWZUvfc8unZirSpyhyN3uCaysco0jJ5OLG6pjniFGnTNMtdEyCoSMuHXQyd1LkmOOIUaZM0xiWOKYc5IsHes0ZilhAYVubaKqECiMrGR4mW'
        b'ZAmZNX76ITJzUnouSdPpzGWAK+A1/6nMaQXKySZYG/vk072gN1YArJF67NOeobFVWZWkHUA6JSp7m/b3XvPuKZ7Mfa9BxLoNItZ9ELGeBhHLDyK2ZxCxroOI9TCIWG+D'
        b'iHXpbKyXQcR6H0Sc2yDi3AcR52kQcfwg4noGEec6iDgPg4jzNog4l87GeRlEnPdBxLsNIt59EPGeBhHPDyK+ZxDxroOI9zCIeG+DiHfpbLyXQcR7H0SC2yAS3AeR4GkQ'
        b'CfwgEnoGkeA6iAQPg0jwNogEl84meBlEQq9B9GxE2E9mva5Mw+PH6WYbPlhmMlcCYlbbCKoz0jEANtaB4OQIVJkBIQP2M1qqzLrSiirA10aIB1xsNeusJAekl+g05hKY'
        b'KAhO0ROOQafkyV26zUIISg1wDWlP4aMVZpg3i4U2QLAeT2MN+kq9VR5mJ72KtEKYbpKvBBKN5STfNHzUYNCXA42yyvVGeYEG6KJLgXy6BiRlBtXmulbWQ8aVhdALQBhh'
        b'pHivBHt5SBrjXiDWe4FYjwXi5JPMNisku5ej6fHeK4z3WGGC9wIJtECOhqfLdM6BLwH+hMZZdcutzhfARM7XONesFmc2fiEm6YAcl7tEjEkr1BthNcj603ZIUg1EEdIL'
        b'WLpXMLZ3ENCPxmIFamfWl1kJ1JRpKqD/kMmo1UBnjCUAts4Vt5rx0XIAokyjVl+tkk/j6YdrKLZXKK5XKL5XKKFXKLFXKKlXKLlXKKV369G9g717E9O7OzG9+xPTu0Mx'
        b'CR7YFHnYLPusWuyMhqKHMfKUaOeVPCU52CdvaU5U5iE9z3NrhO/yFN+LFfM+hseke+POfknmWO8t9+LTfk42QJWesvUiAYluJCDRnQQkeiIBiTwJSOzBxomuJCDRAwlI'
        b'9EYCEl1QfaIXEpDonY4luQ0iyX0QSZ4GkcQPIqlnEEmug0jyMIgkb4NIculskpdBJHkfRLLbIJLdB5HsaRDJ/CCSewaR7DqIZA+DSPY2iGSXziZ7GUSy90GkuA0ixX0Q'
        b'KZ4GkcIPIqVnECmug0jxMIgUb4NIcelsipdBpHgfBCBIN1kh2oOwEO1RWoi2iwvRLmxKdC+BIdqTxBDtVWSIdpUNor0JDdG9xmPv4jSzrlJrWQFYphLwtsVkqAZOIi1/'
        b'6ox0JaVWVotZVwZE0EhonsfoWM/RcZ6j4z1HJ3iOTvQcneQ5OtlzdIqX4UQThL7EiG9WlVl1FnnejLx8OwNHiLmlSgfyMM9M9hBzl1gH+XaJmq4rwTcJpX+EbSjn4+1c'
        b'gyMU2ysUlzbDrlxxKeymdolxj4p1jwIxx0CEYo2V8KXyfBtUp6nUARnVWG0Wwtbyo5FXaow2IC/ych0PpkAOPakBFC5F9IS467W02E9m9lC/B6LkuW73jFTF1DM7cmC+'
        b'5XaWl05lGUm3TzL/HuvyTmTCHk3VAzYtt1NiJvpTM1GGmskBMn9OQhT1ZnLi3C2yVBn0VvMwpw4vqLc2jxiOrXaoJXltHifgWPEPnIjjxDGSl6nxGSba+HYLsS3ZHIk6'
        b'hYwksQwf5Nag00P/BxV6FQrfbml6aanJZrSCANEdMAlWnRc8NFU6w73+vDqP6MQfDJoCcFAJzAXRmMp50QegWA+4B7IQdWy3kDBBZmL/881NiJhdyfM0pgqjTp5vMhii'
        b'MgApGZXqGqJi6Qn2oLm0p9SFcr4YUaURBGrRW2x8BElzDfPbbjrR/PEsPt/QpNnK/NIKA74Jy28AtsQ1mDZJZ9CVa8lA+Fe73qXnPdYuIqU5ZoKy/IQn1Nl3t0Nuk/N8'
        b'kV3669FT2eU+yq0TiQ8yw/6yUsnAXgNtzqCHDPRNbywzyZXydLPV0RV7TKaRlHwkkmSL9ZQt1i1bnKdscW7Z4j1li3fLluApW4JbtkRP2RLdsiV5ypbkli3ZUzZgM/Ly'
        b'C2IgQs0vDGF3dTQy1i0SAvIcHaBMhzJWblPJe5SxEMnDskM7qpITlt0hePNa155llGdHZKdNsxmXUDtcnbkccFQNwSskftJseXwKT2nLHFmIVthTvB1u+CQPFaYVUomA'
        b'DNxcqSGJThDxlOIEFW/FYh9XzHMiD0KPKeY5kQepxxTznMiD2GOKeU7kQe4xxTwn8iD4mGKeE3mQfEwxz4mkWMrjinlOpMsd/dj19pxKCz4eULxDSsxjQcVLKi34WGDx'
        b'kkoLPhZcvKTSgo8FGC+ptOBjQcZLKi34WKDxkkoLPhZsvKTSgo8FHC+pdMc/FnIgNd+Kb5YuAdK1DIivlfKmy3R6iy5tGpD4HuwH6FBjNGiIetGyWFNhhlrLdZDDqCN8'
        b'UY++0U45CcJLt5URzZgTyTloKSQRzNtDkOVh6cYanicmR3qAjHP0ViCNOi1wIBrrI8mP4GH3wj2Y/NE0swFfttjZhF4pGfSAp8wKXIlTsqKUREn5HY9igH2kdmoOpB8o'
        b'DeGiyyj/XEkIvFWnh2mxOlXFmcDsWvVl+iUaV+xfSCVBpwrZlc3g5UeXo0RXNmmajhcudPoSkpQNq0bOxiw8Z+OdUXNVD0O/oWWNwVa5RFfh0GVTIki5OGJElWsO98bF'
        b'RsLjplcuNlTykY1wxE+hZrUlOxe3RuGWqZERxMJZ7cP0LxHKYle5sbEyBxtrZXuzsW3iNr82Py3X1retL8/Otvj4in2l2sh6Ub1/fd8ygdZPK6vzBbZWqBNp/bUBdYw2'
        b'UBvUwhWKIdyHhoNp2AfCfWm4Hw1LINyfhgfQsC+EB9JwCA1LIRxKw4No2A/Cg2l4CA3LSA/KOO1Q7bA6SaE/7WnfR358tcNbpL4SX4lWWc/ZeyzUyrUjaI8D+NG1SdvY'
        b'MjJCH/p0lBzZ4gvlVNRkTkT9OIKgtI92lHY0LR2ojYI0Ub2EenkE07Qx2rF1voVBENsHejZOGwY96wOt9NUqWhxOCgH1gWUibbg2ok4CtQRTYaBcEd0tmUKsuifnz3kQ'
        b'JZW7/HNEy3lMwvse9crRKTITI0gzcdC5R427idXVPWqrQSQCheweMbW5Rw2WiaFNT3ZzkiO7mRjdmGNIFmL0cI/aBRC4UPh0SzXaakBO5iK9ttu3FFCE0UpeAzS8+FJk'
        b'AB7PWtEtKbXB7jGWruiWEPNUvcZgN8jwK9MDW1dUCTu3grbdLZg6exZv8WFOgUepxAUYpfZfarEzjXnERcq3Xlwvrfcpk9oNgyQNklpmtW+N7yoJNQzypcZAkjW++S7v'
        b'vPPTN8S9otfMkX+ZfFf1NToLdQtzzreeWjWU6lRuRdwiUkHy0FTKe6Yp1e4QBtiF6ILsHmf2+dIYrW41kH9hkwApWB0oSaGSp5PygD5K5dROUG6rkgMSTZJr9eV6q8W9'
        b'X/ZuOFfIcy/4ZM89cJ54/EQfEn6qD71BI1WeTf+SLkyPynak2jtm8dwXQnIIsgdSoZIXVAD6hx2gk1tsJQadthzG87Nq4c1JeDkVapJroAoI8/2XG0xAiswqeaZVXmkD'
        b'aaVE57EWjX3wJTrrMh058ZWHaXVlGpvBqqD+gMne18K+JVLlk+1v8lKiMgxzHjS6qBoV3mpxbKdUB7RanItJ3A9NZnkYb7ayBN8014Ds7a0iu6FUKhW0CFMC1fAwYscu'
        b'YbpylTwhJjpSnhQT7bUal/2cKp9GAnIaINWV6Y2wa6CP8hU6DXQs3KhbRk49qxNV8aqYcIX7VP0M02IZ7+bQV9+HkU+MEzBVxYaZ/QSMjTiHLl+FbuOmHHR6Bm7IxC3q'
        b'KLx5BjEvzchW4KbIXOWqctSIt2TPzEBnMnJzcjJzWAZvQ4dkJnQsldYqFcmYkOXNPsyM4uy8WfGM7QmiBapHLfM8Votb8eZs3BKBNj9aa90KfHCtjIlDdbTejCckTFDG'
        b'u0KmuNiQNlfP2MIgcgHagi66+mdlqJThWbgFHcbb1eiskElcILYE4fPUyYxWEz3Bh5GFfOTDyIuzv/P34wcNjbfYPHUPN0C1TZGki82KORkLF/T0D10z+6ELswP1DQvW'
        b'cpY1UEvye3lD7/7Od1100NTXstfs+PQ/AiLTzwnU55iked+/1TB3vfG47C+//yRouWy/erRf3jSJOniM7zvLNyaujT+h/PZ40wuTDpycbXt1wGez3/mgqHbkoXcTnsMf'
        b'twYM+0/8p4FrDiee9j+S+X3pxB2X/qEc8cHm33z80Z2Id67vee3DfwhKS8L+HLJGIaNuICWz8GbUFKVWhi50uooEjhGUoUtm6yiyEtfwZXQWHx6EmvLsS0oXlGUG4Vph'
        b'DT6LDvMuYTtGDvODSVXk2JThsjhqaNsf1QslqBltom4C+XJ0BCrpWUC0H7fQmgaMEPrhTtxK7cEj8Dl8LUIZhjagHRlKjhGjfZxyKO6wEsUi2oj2TYdK+FWjKxY8bx46'
        b'K8BNaHcfWr4wGa+PUCmgmR24MZL4sZzm4tCVcVaif0QN+CSLmvAWl2USM8HRw6oF6JYkxEqMn0dHrCBj5Zk3Cmf2FQZgQFfQXrxRrDKhDiuh4HgvurkM3Ski42qKDFeR'
        b'3GRQESS33CLyx2dDeH+21kp8neSiek1oWAnNrkD70G4B3piEjtC5Ll6Ed+FtAS6t2xnHQeiqEHq9CZ/lrSel/6YzW4+nCzU9JSNg1opXiVnis8Y/ic+ahPqtQQwnhlgp'
        b'W9PHQZYf8biR8lanxL/MPJE80sljEnlMZhzeNVOYx5syS/hSPZVMcpailXjw07nH2I1CmfXD9niwb3Xvby9zZ9b+S21LSc9WMYsZqhVmcxVst19RDythDnHOnYt/0niD'
        b'prJEq3miD9TyN95R1aVNR+oDO3K31+ZgBMKAaGiVJqNhhaKT7RZoTaW/pHPSIieD4alvZuKS2w/KmzPh5cFwvgd8EQ8d+Fktl/EtBxb1Ziu8Nj/Q2bzisYzHL+5IOd8R'
        b'3yIHXffahUHOLoRO0lh0Tkbg3x27b5GTp/bW5FBnk6O8sgm/sPE6vnFJkcOVzVvb8p62vbIWv7BtO7jJilylB2/tj+pZ8Z/gR7z0opcDAvWe4+oZp/fcv+1+4Kjazf3g'
        b'xt5olrrr+u5awPs+VZR9zrzW/HLz+7LnZftDmSeOCPfM+6Nap+B4V6Z2E5DBR9A3wd1nUSveiDYreVq5Ce9GTR7Rtxg3AAaft/hxTm0+RWRnuTgzMWuZtf3G1QS5YDOa'
        b'gS8z8NGaQpxrMg8eY2F+LSSKWc+sD+j2gCXd6lVIu33se5Q38hdbrGadztotqTJZrIRz7haW6q0run34PCu6xdUaKoz6lQL/bqrkhVSBVVPeLTIB5JtL/VxWgiDyAMdq'
        b'EK+hej+ncOnvvEIggL+9oSzAvvh+DTJYfBksvh9dfBldcL81snyXd95l95t3RB5EzHSt1gIyBGGEtboSsg/hf6ndTk6uo1b9P0PKpDIQFWA08gpbuc5FroPZsehBLpLz'
        b'rg9ERLPorCp5HsC5Wz0EIVSSsxl9ZZXJTMRRR7FSjRFkHFIU5COzrtRqWCEvWUEKuFWiqdboDRrSJBUJiJWlRUVGqidaNtht9irtYhWp060OqNpm0RvLaY+c1cjD6cKF'
        b'/4wZmWYfbQXRi7j33S1/mFVjLoc2tA7MRMrLid7QQkQUy1Ibmd0Ss6Z0ic5qUaT+fMmfh9lUeXovAiOfT09KF3orRlpOlVNPh/k/6e/gtRZ+i6TK8+lf+Xy79Z3X/I6t'
        b'lConWk9YKiqRzne1vvNalmw+kGXhKZ+fZ7Z6z8dvT8jKv9A2IuWZ+XnKuJjERPl8oun0Wprf0yClphcoM6fI59uPDxdGzHf15vDeeA8qIHI3H5CTilxtiL0WB+QBk1kB'
        b'WwO2q6XUrK+y2ukZgVPi2k33VrrBYgL41Wk9qgwAnEhuQn0M9CYgutgq+RReb0C36Mh8q6aykvjCGUd61SDQzQCABR2osm8trZ7eRaSBaV2mByqnWw4rbt9w7vWQf7km'
        b'q47fJnTz66wVJi1gknJbJQAa9EWzBDYgbBodzE6pTm4Ccu+xHn5IZNNQhYiFH6be4tIllXwaIDUHQvJYi+u2I+oTAHVy01KpAQbMX7Jk0XkuWWy/Z8lUSnvOH6yMr7Ba'
        b'qyypUVHLli3j78ZQaXVRWqNBt9xUGcVznlGaqqooPSz+clWFtdIwKspRRVRMdHRcbGxM1JSY5OiY+Pjo+OS4+JjohKS4lCeKi35CWUGooLtzYXAuvdECX4oKtWQrsvBZ'
        b'3KRU5RKXvgjUCfLg6HxRxRTcRa93QbeSpsQxzEJ0g4lhYp7Ep6nIf2MUuXonyCyaWJz9aexqxpZGsnbgS7hR7aDsM3EDufwkKwLfVM4iTrGzwoin6VO4gfwBmo+2o2d9'
        b'8U50G+3jL1U61ZfFXSCVbgEJ8hBwBj6MCO/lZLhVQ+92SsW703CXitzBQTxvoXJytwrHDE+MR8eE+DpuxG02IiONRbszYvFO3AXCds5svLUKBukywBm4IRfKNqtnV8Ej'
        b'LzsL7xQyuBFt8MNH8W3UYiP2O0vwJXTQT6XIQjfRQSnji7c/mcXhgzJ8gF4ehW4p8HnclQkVsGnhjADtZtE6KH7BRuR4dBYfQk/74YYoFd4MrUaiziwQpxtYRp6UNV0k'
        b'FIyhd+pkz5yFu6LCWYZDHehQBpuINo2h07ttjg8jY+TxPvLiyI8rIxl6YKIH8bYet0+3+MPQLtGWGckCbjos3006P6gZd+CDJNnfX4W34UvZ+HwE3i5gBuKraPsKATot'
        b'CKcLj+oW47N+KqgCJjAzMhNtM+MWAdMfXxMGomfROv2K/3pRZNlL2JtJI5T/kSNF0UGid5MyH/z5ZMQx9ZfvDRXeQusOD/a1/cEYiYYcudUZJe/6fvl7MX1r+8+ZEH3D'
        b'd1RBTdifGtJsigPFe/9zbFy9cuba5+Je+ODd+D2fx/xuevabd9+Uxcf1P5GirJis/kw/VV34xsVrHQvHzz/x6rf3H1hvqE3d4T+uwG/fVl0/8HrlnbqZxrnvbG+ZO/X7'
        b'VyJO/jMw8FB40+lGhZj6P6OuUNxKdDMzw5W9dTNHTFZ6dVbrogo7RF6XP6qriIgT4S1z8VWq98Dr8Sm0zqmfAWC6gmsdGpon0yiPC+vala5Gmz2xuRth8i9TPU8WvohP'
        b'ReQqMzNz1JG4ZT6qVbDMAHxTGIuuB/Be2e1MtjoyLAM6AmuInoVNcIpbgY/G9br+I+DfvZTHq1etVKPVFvHsHOWgx9o5aFmGjJWwA1jydP0Rkht54G8IW9PXyQn31MFz'
        b'6v68+qGQcdi7kStCzAvIYyF5LCKPIvIoJg8NeZQwvRQent2D/fg6eyopdjZR4mzC39mixtkOZfC1pApXBn/sHzww+J6GpfDtlmmJGaCdaer251lhR1CsqaR/ySUqum5f'
        b'+8lvqa7bjzAuwC4SuzC+J87BlkpdsDLRzwQ5sPIswuVLe/H5AcDpB9p5/SDC65cF2Tl9KeX0/YDTl1JO349y99I1fvku7/bDpC0+j+f0NU7bPjl/x9LP4GenEscIPrcc'
        b'iCrMGbCqwChoXO8XJMxEpLzcbLJVQSrw0Bp3ImWqLNEbNQ62JRw4mnBKb3lySxQCTktQ0kGnjOxWE5GZ/79o8v+yaOK61VLJQvExTlXYT4govfYmX56PclTgkU+b/xO2'
        b'oV6b4/c+3459u9vjeFbXaCKqHTNlZo2eWdRlJsJL6is1Bi/M8PzHWMeCiOHZPtZrjwmW4vtbYjItIf0lMSp5jh26NDQsN5UshoUHwd/zAaORiEbJidExdm0ZAQSQ60h1'
        b'83ssZ712wokkU+WzLTaNwUB3BgBOtUlf6tyN810Mbx8rHdqRbO9loE55812Nc39SfiPFH5HhepmA/l8ggk3SLdOV2w14/r8Y9n+BGBaXGB2bnBwdFxcflxCXmJgQ41EM'
        b'I/8eL5uJPMpmcv4geSWwQPBXXjyywvDW+ATGFk/Yxl0pperMHNwYmZkdhW445CxPstVadMs3Hm9Cz9oI+zNiYigvWAHPGoyu2uWqxatsxLpGjdty1KqsHGBnM7O914kO'
        b'jQeRrQk3+aIT6ArabJtImeYY1GzJy8mz36dFGngKb4UiW3BDxpMgYUlBGoFKIeZa/gK0H+1DR3xB0sO7/HJX4nX0qtxidANft0j1WbglMydPTe5QihYyIZMEuBlEyu00'
        b'z2q02ccSnoNbwwjzrspEZ8JYZjjej/eVi0TGEF6ePYLX5frhK6h1lgS3KJehtlwQvDgmOE6AOpagQ/TeJrQFXWJgMujx9hpyV3D2THIPH7o0i1xBGoOaRMvxxSH8Hb6d'
        b's/EhC98tyCCJVJCrTPvhIwJ8IwWfoguVOkRAV3GG/yrD+YAMxkb4U3wCbbX5mXCjmGEKmAJ0YDpdP9SGD/f1I9MEM7oNX8kA0bMF78CXiDjaFIfb0SmIyMatGUQcWxAq'
        b'mW5R2YifBWrHbfgm9LoeX4ZgJpOJG5fTliywGLviJpbBK4jn5M4mGo3aFqzEO0CMbiUXtjJRXKzh+4cPH/YT0xtz5RNNJQZ2bh/++P6QlN7CG/Tc6GKDsCiNsZEjxaSo'
        b'HHL832IX5DPwOdweOYfcqRyVNRvgIgM354cpADoynDcoK9BlOoVio/9C9DS+QyHPdynano93xmUJGBafZiLxHnwancDneBuBRnyVXM+nJOs0ywE26tkSD1MEotf2mP5C'
        b'BtXP9p2H7sTZlAy9uGs3OtEjEM8MwzvzJb2E30Vm5sn+4oDZaCeVkUG+vzLOkqXMy4kigJSbSZQCAkaB94jQznHoIgDcOir/jwHx/pT9lk+FGN2sYfzQHQ53lQyilwbn'
        b'ZuZyL8SOC2SqNH3/ODcgNpE3ykBX8Ba0G3dRxYdyFm+O0QxD2RyVlzMzzF7dHFebjAPohMycgbfOw5fojAH8Hs+KUGVGhsP2bWEZMdrCRQWiOnqNjwrdQZvUVGzk8CaN'
        b'mU1Gt/FlhYCWRNdBgr1Ii5rIhda05BB0nF6laxgRYy8nQrugHN4rpYqMtbi91DlMwwj7KNE2Rl/+Qj+RJZlIUAkfL9w6IVeQLtv4l1BTYntOxvfqC/96e92oo8enHT7e'
        b'xYwJnqSekvBGdIviKsMprokmJOzffOWtMxUfT1j59BOvvPnig8QFs8zbIq9s023uewT/Nq4wc8L8NNuuHMVf/eYPyPjhcM6DtS/5jf7Vqt1/zyjL2PXqMCvzcgfWWd6o'
        b'v7/3zbBrD16X7njh2ZKvraJpbOJnraMyArdWF5595vZrIz57bcOwKd8V1l9U3+wz1JRyIZd7Mn+oMvDmS9YLuneenfi64Gb0hjUhqV+ve/d6+enpH+8Lj5n7m+KW+0mD'
        b'cd57ur3T67veylv/1pfPK17xvXXrN3kHEr57/p0Hn9ZOL1nXeadFXDSz392BB74c+9Sp0z8W7q55/Yfpf7848qvb87fcyV72xenFl79/o8aq/nz6FxmvPLlqyrO6qGc+'
        b'Mp6rV8YpFuYvfegTPMOYteYZhT/VUaxF1/sA3ryMO6PUvZUUopHUmgKwxRZ8R+3RnCIiTjQAXcRbRuI6Wlkmbpjm0FGYcEd4jxHJrCfpJVwpFWi7Gu9FjS72H4FzBIYZ'
        b'QisBoPD0gohwVQxqVVDLD995HDqmW0CtQozSaREqguwjUWMCgZ5WTokO4kZ692TqinB1driY4cbhbQvZpGCIpnektxcko1PZOZEcI1SzeM8UdAFfQM/Qrsbg7YA1muy2'
        b'HmgjamUY8SqoYC/aQM8Cx0QBNfBoFYJP4xaLyN9YRvOVkAvHUNNidNmz0QeqraQanDHz8RkL2VlKQrjIDekb8FYB0wce6NywbDo9eBPs68vqyLBc3OZQv5ziVgSg+sfc'
        b't6UI+h/SxHjSyQQQxUOPLE71MnMIf7CWamY4XivTo5uR0kvQhFQvQ0ISLoAdBqn9II7Yo5B8QTQXySHjpLQkt468BbM1A3spPHra5XU5Ml6foiMPQlPM5eRBbnU068lj'
        b'sVPH4kmN4/Nzbl6W8nWWOSvWOWta7GzH39lEj0KHfIyg0FWhE37cg0LH2/hKRS6sFzlH731Du6jep56hx6psvZSqYfzqhc4b2kUN4lpmtbjGd5WIql3EVNUiWiPOd3n3'
        b'dLpOGnK/oT2A5/EmaHnWYbY/EN5MAVPAmxBOpZwfs2FicfYf5EqGZwBO4u2TLahFslTACGC90a3koRYbPVDfMSA9H7UU4JbZOTPxpRmmYHxptn9idDTDDB0oQOvx9Vk2'
        b'opRMgZ35bD5uKUiIxo3x0UIfdJaRLGXxIfQsusa7lT69CrU4qmIZEepA18JZtG8t3mcj2irUukiFusTxsDbjmfFzE2nHzGh7NfBdxwB6RuI9Y5kQdBhd4KnRNtTOqFXR'
        b'8bEJHCNegW6sYYErODuAUle8s2B0RJaS3Hs+BO12Xn2OD1Xrd7JrBJbPIU9U49XKLelZwpigqae256bemzk9fUrguznj159dOO/uxC1hAVeDZg1emf/H2+lm5suKMROa'
        b'G1Rf3//kk79m+paFPSc/kIwGB+25++Ms1NB8cpN/6OWoEek5BUs4w45tay6mvfnnsaNX+jfPP2SclnPq8tnXhh548vqiAzlbBdc29P2PjK/+WTHZkFqwfdXJPxnv9i8o'
        b'/GHxr7VFB1/IenXXGv1rH87r+7cdL7766Y5vv829/HJg4dwn7uZ9mTMm9+GP792xBL5duX6h+R/Zqz4bG9kww9Tv6wfn3lmh77yatrz588GDdxS9eSWqccUB65er0gVn'
        b'Glesu/oP8WehxRvP5CmCKXYebAMWkXxy4Al01Ifh0GF2thato0l44wp8tgfVGtFedCFRS+0TURvaP4BHtKPRJopBCZ5FN9BBaoFnxE3xFM9WopseDfBO4QO86d8ZYMzr'
        b'qKmjg06hnbiVV6g/PYm/Nbstv0KdGwlc35YodFKIdqN1TAC6LSgCtN7Ao9i6+fhZ3KSmN9YLhxEQayK3+ON2/lLtK/gGuuK4dnsuMC38zds+o4bT9AR0Hh2i997zl97H'
        b'42P8vfeD+9JOLsfr8D41tbPEN6KdppYD0BnhYC06Q/NMwafnqHuZweINi1kmeLEAnQ7Ex61E7z15JO7oRXPR3jG9TwYQMJ684eZWvMGXmMT2GESST28EDhMsyszgB3UM'
        b'Pz1e3UNyY9ENSnVT0B3+rv92YFH39Kj8MRGhiMp/A6rlK6hD6/AN+0X9/CX9rApmogmdooTWmCFyuUY4Ax8mF3YOSKQTPseSRlg73JpH7l9FZ1EX2sqZoIGjPw8j/7cu'
        b'/3fY5fBX/VPqddRJvSRRAQQ/UxxNbiYnlIsjPw+FHPejRMD9IBFy/5KIuH/KxNwDzof7Byfhvud8ue84Kfet0I/7Rijj/h7kz/1NGMB9HRTI/TUoiPuK68N9KQzmvhD3'
        b'5f4i7sd9Lu7P3ZcM4D7jBnL3uBDuUy6U+4QbxH3MDeY+4oZwH3JDuQ+4Ydz73HDxe8IRAdwAaCSI0EIX6x6++zwR9OkhP90+vLLb0i2yWDVma7cA8v1SiicyV5F3o5Ow'
        b'mZzUjRI2ciftGULYBtkJG7Ne/vrjjZH47v4v2IdVKAQPPnLTW/DuYFaHA4pd/2uwq2XMOqvNbKRplXINOV5w0fL8LNW8fIluhQXqqTLrLMQKk1cf2fVhFueZgF2X5Eml'
        b'/uhxgYFXwpHulKyw6jyou3rRabHr5LkY9duILxvaiQ6nAge/C21Bm9F5vB1deArY+Y3oAmzQUzNRgwjI3jrBSnQV36TnuqgWH0M38Q5YXRXjN0qFNuF6+sGfOWmonlJx'
        b'1PSUEu9Sq1R4XY2A6Yc2C1An2o73Ug6gJY2rWMaSt2JDqGUVQ78BhC7FoRvOsuKReGcJuoWP4sOxTPDq8ARRMqCKPfw3Xy7jC0X4oI0KgnYpsBykWopmDuGWRT00Hp0I'
        b'FhESj1tQJ5USE9BOPS8mon1TORATU5dTuRPVZQ3P58vgtuUcyKVDrOiO/s2Ct1lLLaS/dHdOzl3YWjFBG9/7LlX5u0XMhWF46ByzIPJq5o6F9Qf/Ont/R05ymH/ncz98'
        b'/DAxWbqsIPHtr8Y/ueGNyen+Wf6/HqsKHzvuar85MYUVzxdfeD/hm7jWv3W/8ulLh38tys15uGnMhMhnMk/8+k+/KXqlZcX32qsrl8UlzX3w1csdRbJld//hp/pkTMvF'
        b'YwoxtSIfCKh2/SPns4Om8ye06AY+QUUddBDtWIE6xrrcY8yNQhuq6QXH6Bm0CQTwHI7Be0Zw6BlWjTYsosWAnQbiyH8EhJuPbzB+Og4fGjCFNtxHQ9B1bwklNcQho2Qu'
        b'4s+rt0nwRjtxUw7o+aYLvoTrFOKfwCNeTCI1liKy3yjqHelEvUJDsIAYqAezwQKCdGX0R/xDiEjIuWASe+GfNJc0w+PD3jgqoP2xOMpecyfbLazSWCu8X/T+BGO/TJsc'
        b'eJIvQoidl70Lf9Zl74Cz3hOwHg47e9AWwSAWTTV5MxhcEdjP950jg0iVZ5bJw8lbuBwwsIVXqxPUpFtOvHOJljlcVaOvCo+kDdlxpNmzktpCLiHUOlXjGnNphb5ap5Ln'
        b'EU3+Mr1F58SDtA46AJpdIy8zGQD//wRSIwvn64bUJHakdg3X4WMRGbBFZmQAR5OVk406CzLQGdwQqVKIZXgrk4E3+VQB07mVFlgcnaiGHZWVo8KbgfMrwA3k01jAzyjD'
        b'UKfQnzD7+LIP2gWC/h2qWcorIQ4mwFE2RjLA3NQxAgMLEvnGpfz3pDrwdlOED8jj14CnA67uBOrgP0C1F29C+yPyOIZdkzWLwfsKDfq/BFULLVcgcdCbkgk5MVIuXZZ9'
        b'YWXNsppv/+vbDVHnzl84dz4o/YZyypTkvHNvVb499kDRiz/+/nNprHD73ruy9gjJhZzvKw5+GP3+4BTL8SpLYsna9pMFv886KWTf/G3Y+uYDM20v73svcnI8OyHjQLHg'
        b'k2+nrN/w17CWcabgEX9X3+oWSgK+nbFvbMraNxe/EW+SrH34/ifl4WuHzs/bvKD/vTdE98/cjc9/GLhP1/81+dt1Eff7y67svhA6/cCa3e37fjfwZZ/kAembFIEUfwxF'
        b'69A+OuUMPlnICJNYdBZfxJ00MUkwlLgO2b8VJ0GH1uAmbnWCkeKNxHJ0G3fhi8vs9/P7ohP40EgOHZmKO3iMtg8QMynP4V2wSiBx5XJD8O0M6hJkRkeAaW6CeFUmTfTD'
        b'5/AuPYdvAsd/lvKfRSn4tjoStebxHzvwm4huoe0c3uOLn6H161AnXk+qiKrAnXnE52gNFz4LdfD88Q3UaiVkQ6HCW8jo0DV0mAmMFpQnoWu8wctxtI10ITITtQJldKBc'
        b'aSAvwOwsQEcjosi5hlKl4J5aBUjxoABtlOFz/KdVdqejA5Sfhz9RIC2Kx3MD0a0lNLEYHcJPqx1wy/iWZvbjUAcTwl9JX49uAzUG2SiXWcnPyyQuBF9GLTzXvQcfUTmZ'
        b'brQVXeG/joU3RPOzuh41JJOOgZDRRL5uIEbPcJHBksfpin4Ci7tgbiHZ0BRtRzrRNrNW5ku0PRLqYSRjg+iT6G6CqA5oyENunfBhjb8TzZI6+Bvw7Z9FsDK9dDLee9rJ'
        b'8Xl7bsWvhsdDguSHOJE8s37AQ08fSujVvsLu3z2VIfcCOJ2mAdXY/ylE/B8Ofvs+ckcWsenXmkqLiqjbUrekymyq0pmtK36OyxQx4qeGPlQ5RBlpSqnoSHhmvt//uOru'
        b'sYtqJuc8HzD2r36Ryw+kQpB8HnIwe/0ecmPEQIphDgW/7G+AUCaQ2msZ8FAWFUTeBUMeDpoZkCQZPIilOhXgTTvTLZkLcB1sI0tAgIDxH8rhDlSvpadjY9Ghcj/0jJUg'
        b'GD9yaDNjLqol5zVDYoWjctDx/4VPNbl9z9NRdW+K5JPLn1ndNOITxMdmhBqIyYhKvJeynmPxlSpglFPQuegEKI0vs0s1+BK1iExH1wbatUiAFIBsNNrVSFfRLn5KuhaC'
        b'ZN9UgdZnRhKGLE4IiLWJyxq5Uq97SSyyEIDturPqfvGC9r8/d25rx46YjUvZUp8PuOMbZX6haemRH/c73u/jjdnFiWqp39y2joyztTEbO2o7dmZuZ0f3vfvcXjFTIeoz'
        b'vmaIQkTxReQc1B6hwnsnKnr8KoG1u01x4BK8fjKPa5biTueH+BbhLTR1FDoxBoq25FANvF39jo/gAxRRiQFT3VHj66jLRdAHIR9vL6bqgbl4e5y6BtjMHHviQk5Xjfc9'
        b'zpVGBsIWcDa6ImIoQbHQABcsJBkdwJHPbQgB5whZ80rnfhJ2C0mBbrHdw83tI1Hk/jrzKud+ICVHcI/glIB3vHxkD1+biusjwrKUGZFZqCUqEx0Ppye9crxL1A9djXaD'
        b'piD7X0sq53IxyHhyJQaAK6cV1PkWCnRC+nE9hnxWr4UrFEFYQsO+NCyGsJSG/WjYB8IyGvanYQmEA2g4kIZ9IRxEw31oWAqt+UBrwdq+5MN82gmwVVhtf+0AaFtmTxuo'
        b'DSGXgGifoGmDtIMhLYCEgOclrjxC7RDtUIgL1D4JcUIoMVwrJ1d1tEnbuDZBmaBN2CYiP9rQMg7iyF+B8y8fyz+FfA6Xp/DRd+2I/YF6RjuyTbSD1Y5qk8JztKMueB/D'
        b'54W3sc63cc63MK0CnuHOcITzLdL5pnS+qZxvUc63aOdbjPMt1vkW53hzHYM2fj93jNUm7OcK++iCdX20iaHMob4dTC1LQ0mOEM3RjxpS8s5SEphbH22yNgVmvz81sfSh'
        b'8y3SpmrTIG6ANpR6TU7s9i0CmqaZBtw29Wx3Oy/oLa/wxppi+glGsfOUQPSzTgk8okV3Hzwpf0oQrrZbguQuk4l9B/Nn9pcrWpgQlgk7F6E11q+M5yM/DlrNfs8xc9fp'
        b'DPN/SC9gbORrdrjJlzJuPe78vSRUYHyafJh8Dp0tlwRBDG/efy9yFEMI7MTitSVvxWiYTxy9/Bt56F8Je09gISc2rfLGoc3p0nXRMmGSfvE3PtIfdgZ+FTzj0zMPuKag'
        b'tZWf6coG7kqIfevO5OLnS+5vHt/xml/trOdTblzLePmLGZNeHngq/vpL794vPv3q91+93l5R/q+UT9/N3vftj6nhc7J/47MjKlR6xqDwpTL5kjGoi/8gkVIgDmEkBZx1'
        b'fCLFfLgFNQeiJvQsuhBClePicVyf1at5V/hL+Are7mLSbT8rLR8lwc8UUftw9Sy8n0jt+KjFfVrGhIqA28XrqHy/EnDvRd4vPiJMyeeCPAOHCFF73vilM2imuVXoBN9P'
        b'8hFJ4mQgwGeLmD64XYA68AklzYT24N2ouSdbDjrNDLRCpp0CdKQI36Gc62AL3oCaooDhzsTN7Bq8n5HgRg7V+YZYI2hvWhH0ZhlUQSk6VIS25AFx2ZyHW1VitHsmk6IW'
        b'o114/SIeb/9strTH932YCz0Qx0pZiSiE+sA7dLrkQ4LOTfOI2zuvQ+0WUTOrbiGx0u2W9ZzGGU3dvnpjlc1K7x/r4VZdzd9FZqJZMq8njzrGwahu6NXPqEcpy4BXPH13'
        b'zr2Xv8S5WFREuu/VszcdgtSz17Udp4P7kJ4rVN38e1VmNcE0v6Ar/kWuc+i1S1McXXowzKV5d9921S/xKZcW9ayYt4anOxsemunI7DAT/cXtOh3LCRAVVeq9O3dnOZsd'
        b'QAQTeZnZVPnL26vr3Z5mudf2cpzt9aPtESPif3NWxUVWk1Vj8NrUDGdToQUko8PY2Gt7/2PnAO40imPcP6BI6cV7ZeQkW6LmmOLsnYE2nhxtzyF2ZSEzfeXF2ffSwhh9'
        b'xqLdnIXcHTfvmXnkk78ZmjZtWFmeRlb2afGnzNftofl7XgjdEJocx8xaVTxa9OEXCgVrJaKxEDfHesd1DLD7nTyyu43OP4blpeKi80ODDswmnUO+mFvTxxVH/HwX8nw3'
        b'1vaUp8s23Cq/9xD+/S+IXB7XzV3ksq9bl0ZEOeh3/fcY3ox9cjmdmNHv/7N00jEKtewXP+pfH/ep0EIuBqq9dY//UPNW7dzn9qA96OLWTsHdKxr6YcqBVXcZZvFtcW2S'
        b'QcFZydWARnQowtuiReM6WDe6Zlq0iYpOw3FzFtEvhSsD8QkVkX82gOy0zfA4ESawiJpO62t0RSUGU+kS58cCHWs7ZEFNqMvU987d64u3Imrz6y7N7GB6aUi2w2Ou25J7'
        b'skPx3m6v3epYdQJmji/gCmDdBf9dUZtlPJ9o0XX/+6Lv2M/TvuSYGcXDfzPVyPCnVhvwrpXoFOStwptqmBpgjGp5wfwWi2+gUxwxZbu2klmpHEZNKQOnx/fiKzPxmYrI'
        b'zIKwXCXLxKPN4oCR+BK1Or1OrE7j+3Lk299/shQx1IAydG5eySs+Df7UgDJkQ/Y13ocU5Ny9I/lro0ByP2l3IXVYUtq3vKv9JLBVe6V4H34227wOyvOnXHvQMQVuykRH'
        b'UXsvuZ8dqP+i6lPOsgkylTxxa8zLMcEbovsJX/1q9TsHhR9yqVV+EX7Kb4T/Vb02MnvqpNBBenPzh8c3WNO6/lkW98XyCWWjX6huu1u3Mcv0QUzHxGOxAb6Lb/riKZf8'
        b'7ty9+3Uf2w/X3/mVb7vvH87MW/3BmP3jjvxlrfJXc4LaFbmBO1fO+eTVZ+8ce+3s11zt4Gkzx792a60Njaj7+juFD9Xv+qCL+ATVoOIOfNiuRaUaVOlTVMXqg/bGuTGy'
        b'a21CCdqLGyiSRPvQNdiUTcsqUIc3TEl3nBHVUmdGzZMz/MLtDG+ODV2x2isejrqE+Fl0VW0luPpJMbG9y6Of9SQLjU6DYJ43bpm9UjETjU6Kh6SiZ3l965k03KiOXIgv'
        b'hrlY16Gd6Djd5DPwzYkwStRicFVihIsVzs+Oe1WWiouWmfX278TKXba4pEjIcuwwYEwH2U3kZPAm/LYmyGUD0qK9v3CtMZdbvDCenHln713fBo8Fj+76oMOejr8ebTS3'
        b'VOiyKXsdM9s/cEyd/pwfOBbSMy8R7Hch3e8iuseFa0T5Lu/eZEiR234X5/Jb+xS6gp5G5HrJ4SYFrHA9ukKlXGqplYrq8L6Imco5SnRWWIYuMT59uGFowzJ9/cUakYXc'
        b'uLnxL2n3ixc8txW9+fzbz5/bem3Htdpre9LW/7hRsWfExmu1nbUpLZnNI/asjxMwp3Iks759GQg3MU5bgOsmoVagz01RxGIfAcRQGxaWGVwhRA1oLzrpWJXHq8rFRdQX'
        b'hK5+kMvqBxiEVEXVa+JpVl4nLnaxJKRfqqbaqd5YvlPIxz6Sk678LnjoH115j58OduuA94WfyFCDQ6ZeTNURZPl9/ieW312FIMrtWeVivB7X55NF3sWCtNzJCPANNmfe'
        b'eP1nU98QWoh2/dl/mu4XqzVhurASNWXKrjzxafH9Yn1Z+MdfFt8rXlL2ufZ+MdcYnRhnu3As2nau+tyxmM0xwriq4wJm6SXZR6FZPQzsz7KM6fWlcqJVdFnlfq573Myb'
        b'DhFT1pr+LhPdU4avard3WNrjXFPi1256dE1DtnhYU89N3SMHDt5Xdzy/rUX2jS36hSvrkYFz39iOlaUGd4dEeBOsLN4ZlyEgrj1hPizaADu+Sb9+wg3WEgd5NszJv1+c'
        b'ya9txpuwuhmaz4pVmk+LP4f1/bw4SFNRll0aXAqcHPBxJ3b4fDu/EPYwWYQJeCM+ErqUt/5eyCbh0+joz/9AcXdAkf16Vpe1dWW/JTVC4l4e4jLVvQo4tBe9d2e3uExT'
        b'ajWZvWBwoXm/tx3dDo9lj65+v3oPq++1S4pA3nC5x46ZmDB3+/eI5kt0K7r9q0220gqdmRaJ6R2M7fYrJXfc6MinZmNcA7HdEq3ewl9OQ8yhu0XVGiu51Vhns4JASm7f'
        b'JVu1W6ZbXlqhIXfDkqhCmpMYS8V0Sx2Xy+i1Lk7482kOq95q0Ckk9HTOTOiPmfBcnm5bzu2WkK+UkCq7/cibw/mdRtN7rmh7seYjpGYf4oNZYlpO/fS7RVUVJqOuW1Cm'
        b'Wd4t0lWSL+1y3UI9lOwWlOhLIeCTPnly3uzcgm7h5LxZU81dpNmLzCO6ELKUZH0JS0cRlP2GZTG11WbrJWWSX8gllz+6uQT26ntvrlKeSy57YhXVp341w5K2JjGHocdR'
        b'QgO+ZcGX0XZ8PhAgisPH2fAZ8+lxFLq1FtVarNX4ciC+hJoK/FjGB+/jAoAr67SR2Zbg0xMiiIHombCMHFVmzkzckIvOROItUVn4aXxqZkZkVhQ5AWqJcPhS4R3zZZNT'
        b'cS21jBDjOyV4x0x4q0FHpjI5+E4cjS9BdeVx8dFChh3HoNoQtGPVUHp1iww3B8QVrAVgj2Pi8HV8neYunT4bMnMMG0Z0p9tRW0A6NRDHHeg8OuOwiEUtgyNYxq+Qw2fR'
        b'M6iOygFpuHUsFBUzrIKZJEY7TRJqb9Yfn9Dw5r4JwqGJgH/Os3hHVA5/c60knCmAgcsnrhh5UTKfn0LgVG/qoSKQL8MZ1ITOoV3oYJSNqBsX4014h1qlVBGXwxwlbsxm'
        b'mYHoaH/cIZwYPIJXfS+TMxMZJrk4etmQLpCb6KCexLuyoUYBw0YySYVoz2q0gz8APIQvxEaQe1gyCcOZskzEBKIWQUniVFqXMWEAA7xz0FeDVo8ft1bKy0HVYUOgKh+G'
        b'VTJa3AX89V7URCmoAl3XA9+KnplMv7okjGTRdWCwt9Gqvlj2BLOKYULOzTaap8rtwBKZuCQuHp0DaUzFoF34OtpHfPiodcxsfBwdjgBOf5YiKwckJt8YDuDkNLpKa9u0'
        b'IIsBrlPy6ozl0o6JMXxtWnwygFQHCx3FAMAcRO2D0QbeaWwLvibnDd4yRbh2MIjPm7hRq0NpZZPKea8/ubImcooukPcoqMZncX1cfCJDpswnEVj0i3gHDwjX0cW+anJf'
        b'TRNuJcs6P0XEBKA6wRML8FFa4VvDkpkqholeN15j/n12Nu/z6IMOSqE+jox1YA7aPXgSNXnMDUzi68rNXoy32nXsLDMItQlRI76J9tDeBOBDuBNKi8nQ1qDNMBXNI/lN'
        b'dWwkarTXQJYQ7fOB3lQJktEejnYmNj6YIbjrOZ1uyI+KCTw8oBtjNHGxBFQjGXTZgnZNXEtnXYnb0UY7sHJ5+DZA6wUWt/XjJ3gK3poXlxANUxJL9sYZWLI21EKTRiSM'
        b'ilATc0IWbQpjxHouFO/GG2lSHMDqvrgkUiyZwbUK6HsD2kk7jy+E4zt28GvEZ/A19Cxsy/GCoEGogffraBm6HIrCpKUyeCfww/t88TNUhtUORdvU/Gwp0NW+6KSQkQUJ'
        b'+uML+DId9pXhEqK6iZ44pVp2sSTR7ibSxqELcUnxDKkPtaGzaG9+LB04vjMF7YSeEBdLtQi29BVGXMoNnrGYlstdgTZCMQCsNKYvOgJgegK308HV4E68X61GpxmGM7GD'
        b'0ImJgEj20gUP1eBbUAj6Pp5ZPRi1x5gpKM7ugy+rCRZrxs1sGG5gxH05X3wxmPb6n2tWMn8HuC4eWlEdkTuVn/Zx+A4IJF3R8SKGncTgS37ooBGdpJWZiXzflD0GH8oi'
        b'J+YCfJtF7XhDIK1sTtR0phl277oso/TVqTa+sifMuIHUBahgMoMP4PXoUAK+RvHhmj42NWAUYGMWsXNGRQ1axG81RQgDaxd9bo12yIHSWQzFaegQaqtRZwIaryVmP0Ih'
        b'iw4GQjVUHXJWCXhZPo1a96pAUr7O+6Kux/vxOuqhMSsDZGPlHN5CDjfkRALyYZjpINrvDfYZjPfhTTxoPw2idS2Rqi+t5T1tiWfAHg7tXBDZc7u2aQVHKWHx+MpsQUws'
        b'D99460rUhnf0x3uA94xkItGJOGolnDsc71Q/csAHJEbIjEEnRejpVBtsrU08ZnxmPD6Om2YSdyAh4IJbjDCYXQgTtpuHpBMDx6gLcAuABN7LcGp8rj/eSZ2i0fq0qEfd'
        b'xVlmTJ4oFrfpR66i3RPJkmCj7crxg+y34T+ui6XOSqiuBG+MgFnJwa0ZyixeGIwRMmMLRMPwpVh8BD1Nx/xByWAmnpCNySVDmIoUO3DvwieEuB3vFgKvje7AfyG6THEM'
        b'3lnh41Yrx4ydLYJhxeFNFh5HnkenAPhnAlklrsiA7/bjW7PRWQo2ePcovCU/x3/iTOLiza1kh6AutI5P2hbylHo2PxXHgMCSc0BJML3nqxxdXuZwyM9FT2c6ZmM4ahLi'
        b'y4DhG/kaOlJh37ajA/imP7Fzgf9ox2QeBk4sn0G2uSozNzEQymYqY4XMYLRPaBhfQalR7Fp8Ebfn4/UCwmDAfyk6Q9fhiWF4g70k2ggjo2U5KNsurESHNRRUh6ArKwGL'
        b'7yEcnZ7Ro0v96Nrr0c5QYstpXz3zGJYJ7CtYPAu30FJy6VNoxyR0hmgLmOH4Er5DB4tv4sPoSgR/qRlujqxUR/Fu+EPQJSFuBDimax+WlIfbtQBuBAvDf3Qige6+SvQ0'
        b'LE0ZkQCWMEtwVwWvqts4NU+tjMNdykx0OiyLbLa+EwW4rQCWlmouWpeLcHsM3i2D94vwX4su0oIBgAcu9HjcoPUjeD/XEfgGb1/aiPZmW/z9AT3B5guOxGf00yhsvTZP'
        b'ykAGydYhlbL+OZEM37kho2AvtvSHIZsYE0Au5UbwhYElwKxlEIf8ZnVeXrSSdlA+WIjPpdqoGnP7uNH6Au4QQORE4zvJ7QOu8vUlJjHoVMU82Lc1wKxtRo161ehWgeU7'
        b'YG8nfTZk4evzTG9MDPL56q1LH4yu3HG1o+76kI63v/vPSet37Zo0/4uut59a/r165/bdYb898rdJdQl/uJj3zPDn/3nm+0GrmNG//uCM7q9BY/72t8+XX4gb+2lwQV7g'
        b'b1/9QXqzj/9OxZju1+fuPXT/V/1ei2wpOC3+S0fg8GNH+0WcKvzXv+obffe98mNievBXJ5oZ3amPnvpVRf6khPfHj+s7JG9aneJ+5oIPviuYcUXqP67jxXj1Gy89sS10'
        b'1w+5hSN95pYdmDLSEulzYEhwyl3zC5nzP6zo+PrmizG7PsjNbdivfev+V20v3ptUXz7lPwZ8tr9vyivm51+auk29MXX31LP9Pjz5YsIu0bimkX+YZ0yeF3ztJfPvaqqn'
        b'9alob/7NleVpI/OH3X9++ORf715Zxnb8I396W8F5w3/OfXj490+Frew+8K4+99ubz//5vX5zXn9r6YI/zq49eeo3M7ckn/3yVwcGzT+gU73yzHerWv+4Yto7X519Nzf1'
        b'g5mpHzCnMjffGXz+1/sK5j/39dnPot43nl7h9/rDLmP/f479IvPP9++9NaD82yvnGv9ZMnjv0gNB7eaypi/fXf92VkP9yC2xz39werd2UN7rB17I7/zq9Iz3rn1458VP'
        b'hrx/7MVTCwYtV16o7Mrx/+u096/84782Lv/uz2Pjv1r04eQ1Hx954eBXby1etTSl6Fe3/9oZ8N2D1eM+NBy7GnXw+stzo7Ydz407sNj2yfDP7z4YafxG0ZdqxND5kWj9'
        b'o24CTmuDafKKsGHU4GHBfHQsgmjSObSPxRvQfuCo9Lwx7KmyeMILXYoD0UHMCKew6BbQneO8B9/TC0tQU2CVzIwvKlahlsBqf18x0w8dFJjwbXSKWkXgyzNRlx/qRHvk'
        b'kRkObXIffF0ADE/LQr6NXTWZxFTNF+jBFqepWoyQ2qJNwDeokyDaIKImu8Bc4iMcakpHO6mn4nzFDBhgQohD1SfJ4bQjZ9JRDcKn0C51HhlWNVFCHUhPx7dopbNRI6q1'
        b'u5+z+Co+afc/v4iP8T3aZsbbgLjiO8Ba8C6Q6AK+NoS3Lj68DK0jNiDEAESHr1IbEFyLD/PfFdiKLqFTbspz4D4bhJIIfIVOXCo66gu9rkK7XW037IYbwgI6cSOHIRh3'
        b'Xg3rYrdht9rAjXnUlR8dxdcHEiMRVJdCTi6IBEOMqu1TEZEiQpdX4xu0X30jpzr1oqHcI5rRS2g37zh4DO8I7fGGxO1Bdo8RFW7iba+v4wujiKHITSAxvLGI3VIEHerj'
        b'6UsCv9iktVug0fJ6m+XwcOhtmLXBqgGskA2mzujEtZy41Dl/uGDW7QfiJJ8FDB1tv1JQSn+Jzn4QJ2cDaDoxdyZ5g0h5LojtB+8cK/k8eECNf486Bvrjqsw3E93bL3XK'
        b'4/hSPUr+S/A4yTnMXtY7fga94cn8uVdfvB+/U10g/10tpl7k1AWyVF3x04fwbuoK0pCceVRdMY5XV7wUQ93Jl9eKi2WG3GSGVxBSIro+zBftEOF6DKLoMGYY2oL286zs'
        b'iXIh2gEoBbZYKBNqRV18dK22Jk4YjNcD+8HEAjReow0kzPElIkeyoLLYEJwTxtDDvaRCKofI20uLZReqBvE860wBtUSr+mOiZmXuwuH2XuxCDcPiQMhg0E7GiM6UzsJN'
        b'vLB2dAjaHBcPnCzazcwP0aHtalrLUyPJLaiMxDy6ODt7Wjhf9dsLgsgULO+oLpZVg5RMO/Hk4j4kMmSquTj7nxOG8Tk/D/JnYFxzby0qzv7BnMzn/HwGjWTy5hfLRi1Y'
        b'zef8zJeyBEEv9yk2hCQP4XMuGOhHIquWDivOHg7108huI70rBzjT4shSwWq7/vUS2ocO5ucA6zib8NqianZ1KrqODsfy467vExMXHS1kVgexo8mlt4cwz+XGLxxJrOyC'
        b'vpEWTzrQfwJjly4m4HPolFAVwPMOdxR0jqqN6Bxul+IGyIMuw/+Mwbwu5TBqj8LtYrwJnSXXz5AbaLrWUh5kZZER72AzbCD1gtzbjDtpo6/kUmXA3JDc4sglgX4MFflR'
        b'Mwifz+IdeCf5ATEMbcen8SYG0NDZUOr8P3qcHO1gi0DQHsoMDcLb6cAnBAD2aeplWj25OAsEk828FOAjzydHSsBc57J4GxssU/+f5q4ELooj6/f0DDAMw6V4omFEMQyH'
        b'XAqIFyCgyCngiQYGZoDR4ZoDRINIREURFOOteF8g8cRb0VRtsslq1pjNl8TJfZhkN64xxmhW3fjV0XMAM4jJ7u/7mB813T3dVa+ru6req3r/96fGSzs86utrB1eApQT6'
        b'A1p6kVuvRBZrGzjMjEFGI1PBVCSoSNEDZ1WBw2x6JbojZlE4OE7WecnTuJBPXCNdrkRm+/00LIFOLH9a+EMu8zWPuC9s8lI+/PAtRoPjgPruhIWNSckw0GXZuLL3hidV'
        b'vRcab3/rzK3+Jat2MPf3TWmOnDps5us+0X+xz57vYT99nFPvg/tcc3KvP769peJBRkbzusgxsxasdZ/anFjwwdrZ0a9XX41RNJTdCKkZ/6cLiT9kjlswZlrrF9/NF/so'
        b'i39xXZ+2SCie9U/NB2tPxhVu/IvttTevDbf79v1TU3IGBjeVFWRLPwS3Uz5c1LB8Yc253U94J26tGVTv/KQZ7nS9FdDqvql3zQdeD3M9XTL7ZO4/cfdQY1uf8cfemlDK'
        b'9mv+5cAJ6dOtV5T//KFquddf16o2Lb8v/m756mGLq3csFY9qdNW+/Lcd8TUOL+Xm2afEuGWdvXa5dNr8ob1L36or+fS1JZNdNxyp/Pnv25pe+P7IzQ8vL/K5z4aVDW8t'
        b'euPwR8Kqx/yH9xbf6RUqpR6GsfawGY1kl7ys+t1Qn5s14DhZ+lUwyJ7C/gDJ/j54CDrFFr2Ift4KT1CMTw1cl2+Gb4frwWmsVGTCFjrAN4FW9OF8PLGH5+BSLdhaRobK'
        b'dHgGmUx4WK1+MQlbnjj0cyKP6RXFB0dehq8RLQBUx/jgAFoYp7+Sx9hKwenFrOcMcJrA/efBXbAT70TL2I6enrvgeRrUZm/mdCyIL5/hg0PgNXiEB3bFCYiYskSwnbqp'
        b'YB+VEWAncVNZG0GqQFARaKSAmjWNzl72nSlwF/tSv89148A5dEIk0nK42AR4Qonp5cUHrQNgLSlcDNqROcfpMoyt3zikyuQgzQ0rKemojR5DGYx0s6CkSMO5+AygfppZ'
        b'+AQ8rUs1BrCfup/OcoCbUSZp4KgFPaYd0uA9YMMsiMQIkMye7DdiBJ6hRnLCZj7SRl4mskwA9QPNvGEnLTD5w46Fh4opvGo11vHIWQ0JNoxgDFzN4iAg1XAHLWTbGHAh'
        b'oQOiAXWPrcVwB6gnPg0vwBpX7HzQApd2ckDo6H6AbOtaeve1oBrdcV2AmWYKW0ADqtAls4k/A9iBRr9jWCZOP0M3vbeLjgba4ulbezAswOSFyylW8DVQkxhNY12sQl3/'
        b'UV+fEcZwSoP7g/1I2iMGl4YeLZIJsDMfUbHyOqhYYrWAJ2ZJxASkCmEFyw19+qJPf/TB+04oZck/S1SlXjS+AvoIbtkOEnwjGixkRTwR68YTPhXxsXOEkMX4MqTEOJmU'
        b'GFy8mbtbNzKbvN9wILo7XfUlN0sLqZ2KQnWDdRP01Ui+ktHWVrzVrxM2jPj4qhfihPj9Eodg7AusFxp8Qg1beKmJelISUBh21CJ+G2QJn6z5kqU/vTgrNSotKikrY1Zq'
        b'bLqer1Fo9QIcfUDvwP2QHpuRTpRBcodUz/zjETLUmM3OD1fXWaw+MC581vV5MWBONujf0c3WRSi0o8/Ylji82Hb6CH5iXQVcjA2RWYwNoS37SGDH/ksoZH8V2rMPhSL2'
        b'gdCB/UUoZu8LHdmfhU7sPaEz+5PQhb0rdGV/tO2Fcvun7R0nHydUfn+b/jFkysoW7Btm7thnw7hkRII6/mywZ0aXlWsDuY0msjNxr2C9MyG0dTZ8y1njFr/ezl4gH4YU'
        b'Z4zWcM4TyO3kQiOJr71cRLA6Yo7E15HsO5F9TOLrTPZdyL6QkPyKCMmvmCPx7U323ci+iJD8igjJr5gj8e1H9vuTffF6gdwLyyUfsJ1db4vROPMc5QMHMLucMN6E23c3'
        b'7PdD//t4DTz5cA7RbkdiSjmscF7hkmdPqIAJNS/6zZ4Q7QoIzkc42wXXh3xIPW8FNRjEKxyRueApH0pIeF3lg4jH8IscCW9CcuyjjR3A3xkGYlj0E2XglXhjvhRMiyUr'
        b'kuM2ouzM39lhxycDY9A5Jiy0VZyjKVZhFm8MncdBjSkTKQ6qrCjR0rjeBEffKda0GruuSu309hylG2Y+4jbJYrKQxlnFHEjyvDI9f34ROlaokCt1heiYsARJXl6slqtN'
        b'NMAW+Xc7Ru8yhE63R4aWiFshdjBG7+opAy8yt778qccMvLiifzcD77MJeLuQ7VoMIfA7CXjNHohRDhx8vRsp0M/WZCiSyFQlBTJ/S6KMluQWoCJzSYjz7vmAu6cDtkD9'
        b'+xw18kw6YPQu0mjQMXHTJSpZDqafR5vmAbalIzqFrqYMdhal6Cg6qVvvYLOqsCA8JwhqD88gI7ZGPGw5xoQ1MuIeEg9bzNRERvwHiIcNbZ5WO92TKOXcAwt51gMzdBRc'
        b'CHBuT6JW5Cs1qIZRB4X6MfI6+Ul03GPTFeFQ3L+L39eZzrFkZJGJhkj3ymy/FeMzGR3unOCGwrHd8fsiO8CMhdd3HgOXRYpd+OAUyfK30j6MN8Nk/5qU/fJ7E105ct9l'
        b'C2RWsgQ1SGOl2RJ6G/NYsjtLxHCfZCLJd8JLYjzTEWiTmu3nHDSa0Y3D+W62gxdNGe8YZ4k3mHhzm3lYnwW1DmB3VjnJdng8mZTJFkmzxalxkTQwtTc4DfcjZaBZZUHk'
        b'eN9089yWwDX2YINXNMltbhCZPRK65mWr3pngxhD6HrgJHgCvGqUETdkd6INNBmAnKU87gL0JkFIbp0+kqzzQI9sveFY5vXvQBtrgWtPtt4JDZjl7GyydDtmeB4cdYC04'
        b'OFb55VGxjWY1ymbRmib/axcc2Shx7NRFv71Ue2jJQO/qvkJh2PG22W+59AlceXVJckVuUkHTY1Wd196/NiVNP5Fz78r+J4lH/7ZtlPa3Y44ORWdHgb8e+yb0gezO3jDX'
        b'pDhNVPrFlZ/fH7qg7Ppd0WWwbdHyPk8zvjv4D68RfdaXr6/bVLh43p2ZP/DaX18DH8r2aIfe/Ne43zb9EPpb7iGpiFhSUX5DQd1I2JRieuWo6SmFNWTuuj84xHeAr4Lm'
        b'LmBIYRLcSalyloOdxDI05kFD+HmA9n5wswAexfY9pcppBbtGmvEUUys2PBTbsYlgBzGUI+A6PG9diCwtE8VwHTxOQZvrM18wWtgHecTAlsELdDJ/H2yE60xGY0kfbDMm'
        b'gbWk6Mr+sBH/1mEWwBs24YkAUKukZmVthgQZbeaG654RxHadE6/FS6HwMlyHKZ2xDusPT8LTGjKzgfYSiUbrb8uC9UwSqLEDTfbw5H/MBjAiK3GbMVl5TJVTtBOHrDTw'
        b'Cos4dmHzPSPLMFI9LLMMX8HJ6zgBOIE4+RNO3sDJmwzzbNIdYU8ycexwS1K+wSe/2vSRWJo37yr+8wABRVlG7ckqXG4akoWCMU1lmZEN40PdkA33HI+Zb+B+NVOlrAo1'
        b'0yDUoxc6SUAUg99N8cupTVbLzTSW60HL/WMkxxzfrSALKUtWy3zJWKY7LdNMofq95SGdyGp5MmN53iatSdYZ9Pr8RMoFhlo26ClWJZAbJRiIZznMVJnfXabRCrJWZn6H'
        b'MlEtGxUgszKlLMVNk1kTo4ttci7fTBTsuo7bMPGxnYISslSFo1KwnO0qIrGQxXlioyO7TY8c2ZE19YtNrx5TUCkwCWdPGajIyc9DQGVOONUlS0xAZYQ2+/hJfMwx1mif'
        b'wLbRSeb0OUS5pWJgVpKeG4DGgiIk6cWF2IygNjcOHccBpWU5xTotx+ukQQqrtbrBf5hDRYGrRK7MIww7Wk4h73hTXH2TuJio2vK5wHgWdGH8F29khJJ1Z9sFhZpZNBJv'
        b'A+2MddvGvF6p3t6loUq8o3LUityCIsx4wxl6JDyeRUFN74FGo8wvIq8C5ZXpQm6mkSjN70qJbJ58K+Q1BlsmiDzk0NFGkwaXFCT1w7MkBp5kfIaRKDnXmhVG3koluR5z'
        b'bOG6Cx/dc46uvI43hO9aqdD85xi2vDGjFOHCkkp8fAqxnY1up8LH53dzbkm8Cb+WP6Wpep6su+HX6tH1z8t2JbHC0mWN7WpEz8ToAP7olvPK28h5FSSVZAYFW+esMgeQ'
        b'cI9Rp6C3oywighJK+5ikpFmz8J1ZipOL/0pkFYUkyq5CjYcpP0JoZzSPzQQK7l6gbom4Ok6W0NYSYGgpFsWiypA5fRcqPiTQOhObOdzGMHVk1kzQUdQiizRKKlRxnmVi'
        b'M/k89GaQ+sAXkFDDsgV4u4ecTvgvqkMmGjJrpswt0CoJcZfGRCvXtc1azdNfEoQZsxU61LkaM0BvsFLCVRHqoQpRi4ud5p8h0+Yo8EykZZoxfwl6XWgsVJWucL6iwHL9'
        b'+0tCOp1GSpPp8hbqtAo0cuCQ05LpxWoNEcpKHiMjJFG6vAJFjg43PXRBlE5bjMe3+VYuGBUhiS+SK8uU6GVWqdAFlPxO0+nOrVwdaknk56+gMEvZKM3EKnw+scIt5fd8'
        b'9TKaVKSp6p9R8xYPZtA3GU8ZdpL7ud9E89vPU6O78cZ1a5RJlrNQly+1/vqZXy4J87L+AnY4MWi0tTPRa1YU0JVXlP44qnM2odayCe0uG/RSGO+vmzzCzU+zemujO2Rm'
        b'4b6sDmgcHBD1cNwW0QeQTor6VkNX7p1Ox1irA7YJbYgZ79FQSPeQjuOdgHYVRegfveYSPAaFW+faNOEUO2YT3Cmb4G6zIZDGDuSL3oRxMQaPN6OsXmaEQNJLY6eRnhof'
        b'kHijRs694uixW68GnRqTUKLRYiK35Scx0+1ip6VJvGfAfQVq1EiRLCOti2KGvjRlZjzMCWXISjNfp9Z0Fao7dc+aeklUyZ5rfkYVLarD7H/PdBiCJ42QJOMvSWZw4Nye'
        b'XxZMLwsml1l/GgagKqdCcvvYdO7uPSAoVnQJ/kIndj3Pei82WaFWFwXEqWU6lKhGBMQpkXZnvdcip1vvq3A+1vsnXID1Dqq7klGvFFuAlDDU91vvmohsSGeTWxbDWuUh'
        b'LVah0GLNAn8jBSu0W/0up3hBhAQvJCP9KQ9rregAqnPrDxVfhOHB9CqZSoJ3ur0iV6nFDRKl3ap7FBONz6QbJGM/rKf7hwSFhqI3zbpMGI6MBMJf3b6ReTJ0t3GoU+nu'
        b'JAJoRk8If0kyQ62fyHVzBn7Zbt5oA9Q6QhKNtqgmnBkc1u35xqZNLum4utdtfRsA3NyV9PlY76wxbBupaNFRyejxWO8Rc5S5KMP4iahoCy2yC+gar+FbXGGLlLGMwAXP'
        b'0mersE8nB/Y5LzbSUfIWwyUcTi4IniAXVcQJGGH4FRxhSPx4vpwiAaeCM/BcQjzB78FTsBVj+CLo2phLeF/GzzsMR9Wck9BnPIcv2wSXjCCkHaANbsTQvk3wAPFzFQ6C'
        b'mymqrgxWE4AXAUbDtWMoWm1hJe/X8aEsEyhb1DK0iqFwwJaQwb7oXEytmALXTMV+hqB1ShIhG83AYLS6NGbBSPt82ACbCJQo0D2FPRbRwEVEkrBPGR0OCDU3LcCwYmUe'
        b'CwnnMpmuVhjCIWVGk0XAerBFLJV5kxlDZUreXL5Gj7YqA/roGq4ng2yXP+U/eKxPi8y9+BOzPXxh8JfSu184qJ7w7dfpI1WznUOHX91/nXnTTpdw/bOy8sUhY96cm/pC'
        b'81vzck5MOh7YnjJqkLJ55ZsDVJ9MCTqTPTRheV30q8VbvhQkXVftn1iVlZP6oerYpf+5va7sR2V5xL22knU/73ojuOCze3WjVvfdGQ23bjz69Y43/npi8bzmr+vdDgff'
        b'iE+ZPsP26s6mx1+Kfru+ZWvC2JxFvace8CiOGRrTpzAt4cfUzyfcusJv+aH6Qd6W5KxLtwLGvHdpld2cTz59eufJLeeTFdFfhr8qFRLYSWrvYA4/ogRnufjJYUryE1g+'
        b'fISBOgu0pWPoiAdsIYiU8GCA169S4kGr4xgBY6tiPQv8iCthOqyb0TV0qNJPCBrAJe0InO1+vpouIoHjsMHyQhK3ihQF6knMJbDRJ9QUdAnjzDoEXdJFU0fRGrg0w8Rk'
        b'eFpAKSMpkSHc66PF7t2BbjYJifE8hk0Dl4bzfCYEdQV7iP9DMc2xNxxZt4rDzbfK/CNMwfAPHEFvGIFy0HA8xOeQrFmxvIHkW7iEfcqyg4zbC8XG5RkjmoML8mGas8bu'
        b'3GYLVvbPJb9UYJYJybMj1mOepVUrz3UWVq06iGod7EHiOWEvJGaFwBjP6TniLapLUQYdOkp8Gx5dOkov2lFOK+JQ/ZHyxKpYbw6KsAReStfo0PvyGkb21gtQ13eUV6mA'
        b'WygaBLvZC+CxWQ5gnwc6MIOZAdaAixQe2w5WV6WPwtyvgRTseoGBbZ5FpLDyDBpauERRNcbTOYPrMI/Ao+B0yEhwQE2xGwoH2ExRCa/C3XBzyEi4DZymeI9ccEJLQdt5'
        b'xH/AhZld7vdwaCoFYPSNJm4V4ZLyInG+bRD17l/s5UIPBleIe4+LpGdma4hXg7ckuFhs14eDaqzrS0Ad3tmSeYkjErzomY/yqQfAu4GFfgOCyumZbSw9WDI3V+w9ZzIH'
        b'IwijIi3RFCa2oBZFbg42wY3u6al8XWoqw/BiGFD9Mqyh/EqbwEWwISTQX4ZJFnlwHwOr48BBivXYOlOTngq38xiM3DuAfplQRh6MP9wTn54EL4AmM5QIOC+CrQQSkeZR'
        b'GBIotcUxPAhEZA/cTzAcYJcbaEgfhn3qhjBDxoDDOkx+YDNWFAJPThYQeE5iECk5ChxAI9KrcKUHjwA+wAp4gSD/UV57tBjaMSaNA3cQYIfKndxMVC9wLj0VVMM9Egww'
        b'PtnHFtM+OlJscnsmOAjr4sWwpkMUPdgIzlEQBq5n32EEFRS4xGleYkQgj1Zpojs9mDq3ODEsfAxXpbXoZduLqqcxKRXvLmVk4+eTPErEbtgHRvLucOWcx0P5HAZ/E1g2'
        b'A8l2WQx2SRkmotIB7gZtk+jLegmcgks0jrCldwiqNBYcRocmwleU7KU5As1wVAW9XSYVNiZguMfy/O37kh5NfnXjgbaLokXhvISiK1s/dXaNnaycOWS0ik1rkCUMql8a'
        b'mDzljT0n5O88fXtH1QvXM6Ym9wmbN3G5/6c3YPn+ge+1fHtG7h4fM2ppv4yK2QMUsROVAXsz31ONXfDmijVXXF8L5S0MaLkYd/ls1EdnW8fFnAqujPmg+cy/343pP/NN'
        b'l/v7Nw6TS+TD5BeH7riadvLdmd9/4zH4dMY9yd+//+xHV+VPNX9/6XLO9PV74vJWD7266LcRTyZmfFJ67WPRi7Ufi5qy3tXtcP32rWNrNZ8suDe8cYDLR+de8Jzp+YZP'
        b'1qxQabJfZp4+LnxU+8azOUm31mxb/2TbFOf8r7Sf/bKkjp9eOu2dY0WHZztcP/+vO3eujn3y840T/W7+ecPtV+5IHz2xqc4q9dgUL3UjWI8hVVndeENIwHHDODYykUIt'
        b'LsgFvgklcAUeHtEgJ4QXWNAI14aR4XYsaiFbfaeUw5qkRB4jGMIDTeCwiDh+FEjB8gQ/ZaV5dEB4yoY6fmzQVWGAiP9IM8wprIdniXcKwASJDQmJdmBHV+isJNbGHjaB'
        b'9RS+cRm0vwTqUgaLiH8JcS5B5RCvlFId3GyCb4BXvNPYEHgabKDg2aWwRoHdWraXdXajgYfBeUqS7CQ3x5gshi2gnfVMUlGkKWpG4CjKATTFd0V42PBJ7aTBy2lIGQFn'
        b'xphwrKdCqACr+6NbNMN2eILdfKT8LuVHo5ZDUS684HQTuqM4i0ODTocrCR6hZLguwYTqgHsVSHeu5MeAXXHEC6gU7AQXMJ6hCR7ujOvIXkxxOKvnQwK1KYLbqAMOdr+Z'
        b'qKDP/ZWxgxJg/Shv8/CNoA6cocrN2aFwB3HcOQdXdYHpwL0LtCSMwJahGFiUEpvX2c+IOhmdmWjFM+UZMQIJ8QvRUsq6aCmCEgGnjYh5LqyQDPEuHGAVoylcCJ6CJbzJ'
        b'rPFjQlYQPMW3tu62t0SDkIbDUqSFC/HAx975gl+F9sKHAhFHf0ZUhS7Eapbl70SxxjeQuFWbf3ptskq1Zl6WBisQ/z2etTyko+g66yiWScbsknU4ZHCeJ2ywTDEGzrpi'
        b'tiZCMZadQgaqOLAszMAXhppt9XBCF7YNbqcg0focuN7XDkeL2YLpwpbDLWSE9I0Ch3xT2MxEhofJwvwmKn++tpanwZ4O9yarxiVdEoFIcbK6+fT/iJzGV2/bdvJw+NmI'
        b'2l0fO34leV80orzuu7XvzDi7KF3j/9akLxLu/bv2XFTMlzWfzgk+eM3DIeiG+PbbffntU1fNHHZXMmiS/VcfrVsctuel+YJXfvpestH+dEnz9W/edl9xXP147jeJnjVl'
        b'+zObmNcB79GB+M/P/+2AMk9Y9VR91+GX83EfTfW8Wt1en//n0gNbWibM6+v7StTZTfO/PxJwKW+7Vl9Z1DJ+gtP7oeExjVJnEnQP1kR5UKIwRpAkwjxhzHzSAgPgSlsT'
        b'TRjq/lDfW8dWZguoX91qWF0Fl3uQMwwsYClRxCuuwhHuJBxgk0C9iQaMhRdh0yCKdWp1UBOOMXB8lIlmjAV7h4SRonMWgEZMETZHaSQJY3FvSqMCoD5+J2gGy2A7YQkz'
        b'UISBpeAwxYIdrrA3pwhjnMfCtYH8/BlgKe13NsT5IhV0UwdKxnh4iILcV4fDRhNBGOrzjsPThCKsD2gll5fFwEZ4ABwhLGFGirDV82lU2nqdxMgQFgN2MvaYIgz11g10'
        b'wKiJgGuH9iMsYUaOsP5zyU1XwM2ofzbBFl+eikclsHUSKXVxAHwNNAzy5dBmhB0MI/T+I/xghMSKdGiBXTo0psrTv0cUYbh7MFKEqcuZ7tFdCzqU7YGOaYZ16YyY6r4f'
        b'W6UEM5SHeruOCA66ywXzxtvJ0l6d0V4VDGMO+brCPNMR8TxDYndrFYUaitnqxP7l+ocs4B48o3aUDMGd9kyG0n252IoJOVffp6z095F9iQV4aBE8FTyV8HuVC8cM5JE5'
        b'sIKXxZp42F5lUNJsGMeBLNLrD8GLUl6y8rTXB4ymH1J8r64qiW0YU7Q0Eim+/Y69/lH/QOfc21/w9911fe8WI1VXZ43cmDYsY+on8kZb9T+u5awv2NZU/Nufn7SOD5g4'
        b'XhAXNbdpzaTHK45Mzsvfuu2x+MMTu6vzh8+dVHU+Nm7mRsHTt4NvzG16mHBQsuXzf2z4jI194Phdcq5i/f7yH/vffWViw4KrQQcvfr3aYXzp35YLj9/5941Fw2++CDQP'
        b'Zju7x1xa89b37m9/u3vaR559e1U1lsaNOiloPqbNGfl+dPxCt4Cbm9reeX/jtcrRP577iu9x8+v0bbIViRe33Ij71O2ebO67h0q/SVU7rK8MPL/uoNd3T7/dnlD2xuCc'
        b'NVM+2XBjb8gv+rj8O4knPfMKh8z7WOo0/oy906E30lPqB96PjnrswM6Q9378LymfkrtuifGBdUgn4YWD42EM6i02gCVE+RqEWnkjN+EDz4NWcxdpsNuFRG/BANwzZkGz'
        b'0TlHhpnN30wCjV1nYdz/O+/gcyeo5+EbG6KlhEBRhVlZqmKZPCuL9Dx4mosdyLIjeRI8ufPUlsWTO5KBA93cfNwmsC9G8Mgk0Fgn/nAHpootC+epPzI2Pr6ezcoym78Z'
        b'+P+gDnjqm8a2iyXFnQ+JNRz5vQVKMjL27IU77ZGOuwaNACtTEsFKTP3uFK0YwB/sPEvpL0uy0axBp8381WvwytFOINDN5unDOy6Rk1WrInNG95pxLO3mYMV7sQufZNZs'
        b'6zXnndV3G4aX7kkc6jjy58zKim+q85ve/2qV9N9HXbOUXn7v3+wTkLHz7d0xx71qDxdq0qfvmeI75+Nbupu1MrZ69y5X2bu7li2DfcfcLr3i+uL2G69//YovW3T26+r8'
        b'z712AreYqvt1X93nC0u8H9zWIz0CK/yOaPxtxQNySgoewBLsGIcgL3CChYfAEjTw4lNC8sGyhBR/NKKik/Cw7Qov8uPBATRArgUrSdPwUME1tAawpo6tQ1QDOPB+L/4L'
        b'AniBNCy4v3xRQnyST5IdYyuYD7awQnCshDa5V+NjYF2ALcMDm+HKdFyh+wu1WKfrHwFafKfgcBPN/RIYuNkN0FgB/N4LcVS1BhzwZjXSM0ALbJSycC3c1IuoMn1hGzyr'
        b'MTtDNFYbz4JjYA8ykkjUnItwD6xNIAYtQcEzTtnIllzFTx5SRoywigCky8QbQvvVwhqwMw1uoaRRa0GdB9FCJ3PwVrEMbujNwjawAm6jKPP2IRUE11DCnSHSwgZwkgVt'
        b'E8F2YuQEeoHd6IwTYlBbjqydZcjuPFkqLtXxmH5wDR+s7uNK5IxEesWxBBI1Ad8Nwzh4OYGtLLIiLw7Q4pG3YjA4hWs+AK4GOxJQd9OAp4LxETvGfZgALO0FlnSIfDz4'
        b'/76NdW5y9s/odiz0QiakBA7dIHQUGUP7Y6tNzBvP76wOCYZRxYF0PB56vkpRpBdgz1y9jVZXolLoBSqlRqsXYDtJLyguQT/zNVq13oaww+sFOcXFKj1fWaTV2+Sh/g99'
        b'qfFCPuYFKdFp9fzcArWeX6yW623zlCqtAu0Uykr0/IXKEr2NTJOrVOr5BYoF6BSUvUipMQBD9bYluhyVMldvR3GzGr2DpkCZp81SqNXFar1jiUytUWQpNcXY11DvqCvK'
        b'LZApixTyLMWCXL19VpZGgaTPytLbUt88s8j1LH3av+Dtn3ByGydf4eRLnGDKNvVnOPk7Tr7ByT9x8i1OMEOp+kec4LUh9ac4+QdO7uDkc5x8jxPM96a+i5NbOLmHky9w'
        b'8glOPsbJfZw8wMkPHR6fyNCzxvzatWclZzwS5mE33NyCEXqXrCxumxt9Hg3k9iUlstz5snwFh0GWyRXyZKmQqIqYOVamUnHMsUSZ1ItQvau1GszLrbdVFefKVBq9OA17'
        b'BBYqYnGdq3811F4nv3q9cGxhsVynUozHM/wkqoGAEdgJ2c6vmlsYS17F/wWpVfXu'
    ))))
