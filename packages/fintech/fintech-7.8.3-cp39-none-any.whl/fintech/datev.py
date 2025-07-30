
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
        b'eJzsvQdcW9fZOHzv1UCAmJ54yhsBEnvY2I63ATGM8QTbIJAA2UJgDYzxNmC2jY03jrfBeO89mnPeNrNp0uRNG5L2TZw0jZM0bdOmTdOM7znnSkKyJOLk6/v9/t/v9zfm'
        b'cs9ez3nWeZ5zP2Ce+CeA32nwa5oMDw2Ty5QwuayG1XC1TC6nFRwVagTHWONYjVArqmEqGZMyj9OKNaIadiur9dJyNSzLaMQ5jHet3OvrDT6zpi+YvUhWVq6x6LWy8mKZ'
        b'uVQrm7fWXFpukM3RGczaolJZhbpolbpEq/TxWVCqM9nyarTFOoPWJCu2GIrMunKDSaY2aGRFerXJpDX5mMtlRUat2qyV8Q1o1Ga1TFtVVKo2lGhlxTq91qT0KRrmMKyR'
        b'8Dscfn3J0CrgUc/Us/VcvaBeWC+qF9d71Uvqvet96n3rpfV+9f71AfWB9UH1wfX96vvXD6gfWD+ofnB9SP2Q+qH1w4qH0+mQbBjewNQwG0ZUB68fXsMsZtaPqGFYZuPw'
        b'jSNyHN6jYBJhOorlgswix3nm4HcI/PYjHRLSuc5h5L6Zegm8d1ZzDMQlxTEF0o2z0hnLWIhEJyehm7gZN2alZ+MG3Jolx62pC+cpxFOLmAmzhfjhSNwtZy1k1JZUfNCU'
        b'moG345YM3ILvr2UZn1QOXULX0GU5ZxkAWfDDQfiWKjUiVYTbUxihkEVHVq+1DIaU5Ck6Eq/AjVBaND6b8cdNgswwfyg4gnTjBjo1ATXjpogK6ExLajo+LGJ80FUOKr+w'
        b'3jKaZKnNRHcgyxUpaliTW7Lagq+ulq62sMwgvEOAWjbhB9BPknF9VgpqRjsiVYqwOfgq6S7eQSK8mKFjhagGXVEWsU/A5lDbnOnJIvJLyPy4RSweal1AtgFgeAMHC8jS'
        b'BeToorEbuRyHd+sClj65gKQzA10WcCS/gIUzvdKnsDCbsoKIv4bJGBq5OlrAyRnyVhBxXhLJR36d5F14TCCDuIKIE1KOj3xDK0wbwgbCTizQ353pxXQzeh+IjjaFCP8e'
        b'zMjavN+f8AV3IzohZyar94aEK4IDrHBgUQDkj3k3ZlL1CIZGn5/5RcDJpREjuXnvsd8NTq18h+lhLEqyQFdM6CKsXnNkdmgobopMUeAm1L0gNC0D74hQpirSMljGEIL2'
        b'B3hPqcD3XdbA1zbsdH4NnDcRQ1ag2Nc+x9xTz3Gtu00idpljaaaR9IIH4yPasTnzFSGZiziGEzD4WbQfnbUEk5QTXvhMDtQwhtGgujEmdIRGK+ahKznzIbqUqVDNRifx'
        b'aUsQRFfjfcG4HaqNZCbhrsioagtpE1+ZiutxO4xfwRThHQp8fhFtFUCzA+/NycjO98atIoZbxw5bILeMh5RNqBPtIvsiXAXA3Ijbl6Vnh6LuiBSyURkl7hahrTOW0p5o'
        b'wtB5dBWGN5nBbXjn5PU5un++xYlMHZC21Ofx8l9G+6MoaZ36nYye2u6cgOdCBh9YslQ9feAr51/aq5x1ZsTN0qTUHXN8gucfWDJg8vo/78t+bvbGO4f33u362/pdW8T+'
        b'58xdhrPSQaVzy1pjotbv/vxocFWh4s2xutI/JPxbNLVi2RqxeY/+g98Yy66nX+mp+MegyZ9d+epT0c+7jvyt5PWwb69Fvqm+2t9v9saKvLNHpMsejfnXO0M/aUv6QvWG'
        b'XGQmaMBf7aPCreHoFt6FWzMUaYBImGB8S4Dr0XHUZCbbFO8OHYDO4M7wNAVuSE3PFDG+6DKHn5WihzQ92TQ8XClPC+cRDROANwvQ3aRyfB3dNhNcjXYb0SlfmDx8XJti'
        b'UYQBoHJMEL4jQOeL080hkGPDyCEw1014B76KduMWASOcyKLL69AdOdfDhcqNBGTkvvTPT3gQ6Pt64ORiY3m11gBUhdIrJdAabeXUHj+j1qDRGvON2qJyo4ZkNckIyE6V'
        b'sIGshPWBn4Hw6w8/5G8w/A3kglmj2FazXNAj5gv3eOXnGy2G/Pwe3/z8Ir1WbbBU5Of/5H7LWaMXeReRB2nuGdI5SgyxjBOzHCumT+4bjoP9xzLfkZCF9H4Ers8KT8Ot'
        b'qlQFaopMW4e6gIZEprHMOHRZlD9N4rQ5yT+h9a+pFB5awikAl6BhcwXwK9QxuSL4K9ZwuV4a/3qmmNUINaJa71wJfRdrvGolud70XaLxhncfnigXCzQ+Gl8I+0IYcAuE'
        b'pRo/CEs1LMUSAT3i+XTmMulMPv4ONmiRwKFbZOheNrxBGBl7xTxSEjQIACkJASkJKFISUkQk2CjMcXj3hPg5KxZ0RkpCHvG/my1iJIPvehHMXcUGMboBOfM4UxakTH75'
        b'o08LXin8uGCXpkH9SUFLyTntxxDO/dkyfKktui770LG9Qf+VpT6t1ovOsGcKXhLujBguna0c3uK7JHnzJ4ND5g/eGpL0Blux/L0XAjc2RcjFdI8UAfQ/CAf6yRPPcDET'
        b'gM6loE5B9Wr0gO4ydJgb1ZsBUOQlfEgaIfDCHV50D4WtRadVuDkdmAm5mJGY0C7UxFXhw4Vmwgygzny8jeAzVSo6D8g4icN1s0LUeeZBBJza8NWlqDkLuAUhI8KH2Kg1'
        b'+M6CRDMhiyuMpnBFCuEvGMlcIDbXOFSr8pNzDnAqcLfhKNj2SPLzdQadOT+fbiwpmfbcQJb8iFkhWx3AL7/SlovfUKIeoUmrL+4REnawx6tSazQB52gky2Ik5LCbtbXr'
        b'T6L8yCPAvlNII3n2ndIV6HGnuLRexD2xI+ygN8kKesWcFfA4Sg0FAHgcBTwBBTZuoyDH4d0T4DEeAM+iIJsc+KYaX9wKa7Ud6DrekZPCL2r2vPkKII7P4GP4AbovDsJn'
        b'UKtuxISBAlMUFDvw0rRPCz6uWQ2QGFoUERyuTld/VhBYVFqsLxQ2RSsKPi9Y8sLgV352gGWOLpdsvjpZLqRAlYEO4T0OUIOa8M1orgodx9vNowhk7Ma7JwJH1wioeYdS'
        b'UaEISzVQ9D1koxDV4RPrKHDhq1PS7eCzlgAmi+/gB1EUgPANdAbdV+F9S7MULMNVstPxOXycX2nOLdAA9izRmnVmbZkVbgjyYwp9WClbHWxfM3sWviohhYMeoUFdpu0F'
        b'FWMg30ywHVAojBBOocgOI0f8PcOIm/b+v8NQHgEljMzrNXQ8pBdQ0M217mBFHMQW6C5kviUyxUCZMaPXApQ4w8iQn1Mo+ayAa4qxRP026mSUMLaiU8BcCJRodu6WC8xE'
        b'usF3ItAJG5xIkimkAHLZj9spmASgLoUTlBAYgcBRHk5ChRRDAdxe8+PhBLixkzyqwXcSwq101DMaAYgwuUJEyRMQYXKGCBG/4GTpe0SVar3FBS4EDnDR3w4cZLZL7cBx'
        b'sA8E4qZpzzhkKg8chMdmi4U/AY+4iJ6stQln8BBlWqLhHZ0GAe8BEQAX4AaFQpmdkrYQN2Tl8ExsCm5Mx3fRs0qWMeP73uL+qMsSDqUW4cPogQfsMwV12IFqAzqiWzJ0'
        b'gcCUCYUu5W/5tOATgCt9cdjAMHWKWk/hqULdsOeM9rT644JXCyMovKWpz6i7NIFFzIsDm9jZBwZdMkdFaDSaFLWk+D09yyQkBTy4FmXlS9egO/gMYRopx9iAzjlwjb45'
        b'PEU8hXfiozxUjsPHrAiMq5qOWs1jSHodOlvuApYAkmp8D6ASPcQ7Kfmbiw6gczxcTjXYoFK1kgf8NtyCagkFLMV7KRGkFBCfmie3UiGhR56Th12xpYKwmr0EUO8DfKWE'
        b'8pTVflYI4vM4YjKettkB1mV3AFLrpX4UbolAU2aH2z3BnuHWuVUXsdAZn1HB3I7P2Ab2p4uBQrcAK8jUxSz/N2NKg4j9R99UqVNKPgNgeqmwtLi/+rTo8uBBUQoNAaZG'
        b'9RntOS33oqLgAh6tXvbCkpeX4QV4HtbjeaH//dwSwZtBQOD8GfEvAirkv7ESOHQe35A7E7g2vA8o3B0lTa+Gtb9C1h7kjl029gffQV3oEk/aLgwfgJsjUlEruo9bQfQT'
        b'r+DGsPgkBY5Z+AbZJsBU4ZpUG18VghvRcfdQ0ReKA9nBZDZa0RtREjDmQJA2pAAn1f69eIZkoaW6BfzSe4YQYJN6gYNQYosdOFr7QGpPNCbnMo1ETyD3I8wcoa4g3/jk'
        b'5/P6PXiX5uevtqj1fAqPbSVFAFYl5ca1PRIr82aiDFqPuFin1WtMlEejRJgiWwq5tIc2xN2nKMcPiExRDhkQQdwSTshafzh/iVQkFQVKLGRrj5+x0heE/P1pVvlHIuUK'
        b'UNNwz/IP0ao4yT9crlAjIPLOIS5XtJvRiI+CvHOMrWFBFpJQIPfuEc82APpf+3X/WdpCnbkcJMpIlVGr4V8f8yzIY9LE18GLtMZqS4mpQm0xFZWq9VpZLCSRAX0tTdea'
        b'q81a2RyjzmTu5uikP/4FDPjLAzCpqnKDuTw5EyZZFjpdY9SaTDDFBvPaCtlCEGeNBm1pmdYgT3YImEq0JfA0qw0at+UMajO+Z9QrZfNgicqh7KJyo+Fp8rmrbJVWZ9DK'
        b'phtK1IVaebJTWrLKYqwu1FZrdUWlBouhJHn2QkU66RT8XZhjVqSC9KdMnm6ACdMmLwAqqo+cvkqtUcrmGtUaqEqrNxHaqqftGkyV5UaoudrWhtGcnGM2qvERbfK8cpO5'
        b'WF1USl/0Wp25Wl2qT86CHLQ5mHkT/K22OBS3BQrXkN4RRYDM2hGIUspyLSZoWO/QeVm0x5SYZJXWYKhWylTlRqi7ohxqM1SraTtaa3ta2Vx8T2/Wlcgqyw0ucYU6U/IC'
        b'rV5bDGkztMDGriL1hlqj5LY02VwtwA4+WWw2kVGSKXXNLZubLk+erchQ6/SOqXyMPDmVhxOzY5otTp48R13lmABBeXIObGLopNYxwRYnT56hNqyyTTnMEQk6zxqJWUVg'
        b'WJFpKYMKICodnySal1Vk1vjph8jUGdMzSZpWaywGVAGvOYtT5yxQzCyHtbFOPt0LOkMpwBqpxzrtKWpLhVlB2gGcU6i0tml9d5p3d/Fk7p0GEeMyiBjXQcS4G0QMP4iY'
        b'3kHEOA4ixs0gYjwNIsahszEeBhHjeRCxLoOIdR1ErLtBxPKDiO0dRKzjIGLdDCLW0yBiHTob62EQsZ4HEecyiDjXQcS5G0QcP4i43kHEOQ4izs0g4jwNIs6hs3EeBhHn'
        b'eRDxLoOIdx1EvLtBxPODiO8dRLzjIOLdDCLe0yDiHTob72EQ8U6D6N2IsJ+MOm2xmsePc40WfKS43FgGiFllIajOQMcA2FgLgpYtUGEEhAzYz2CqMGqLSisAXxsgHnCx'
        b'2ag1kxyQXqhVGwthoiA4S0cYBq2CJ3fTLSZCUKqBaUhejE+WGmHeTCbaAMF6PI3V68p0ZlmolfTKk3Nhukm+Qkg0lJB8c/BJvV5XAjTKLNMZZAvUQBcdCuTQNSAp86iG'
        b'2LGyXjKuyIVeAMIIJcWdEqzlIWmca4EYzwVi3BaIlc0wWsyQ7FqOpsd5rjDObYXxngvE0wIZap4u0zkHvgT4Expn1laZ7S+AieyvsY5ZTfZs/ELM0AI5LnGIGJecqzPA'
        b'apD1p+2QpGqIIqQXsLRTMMY5COhHbTIDtTPqis0EaorVpdB/yGTQqKEzhkIAW/uKm434ZAkAUapBo6tUyubw9MMxFOMUinUKxTmF4p1CCU6hRKdQklNoonPrUc5B595E'
        b'O3cn2rk/0c4dio53w6bIQudbZ9VkZTTkvYyRu0Qrr+QuycY+eUqzozI36VnuWyN8l7t4J1bM8xj6SPfEnf2YzDGeW3bi054mG6BKd9mcSECCCwlIcCUBCe5IQAJPAhJ6'
        b'sXGCIwlIcEMCEjyRgAQHVJ/ggQQkeKZjiS6DSHQdRKK7QSTyg0jsHUSi4yAS3Qwi0dMgEh06m+hhEImeB5HkMogk10EkuRtEEj+IpN5BJDkOIsnNIJI8DSLJobNJHgaR'
        b'5HkQE10GMdF1EBPdDWIiP4iJvYOY6DiIiW4GMdHTICY6dHaih0FM9DwIQJAuskKUG2Ehyq20EGUVF6Ic2JQoJ4Ehyp3EEOVRZIhylA2iPAkNUU7jsXZxjlFbpjGtBSxT'
        b'BnjbVK6vBE4iOWf2vOkKSq3MJqO2GIiggdA8t9Ex7qNj3UfHuY+Odx+d4D460X10kvvoiR6GE0UQ+ioDvldRbNaaZFnzsnKsDBwh5qYKLcjDPDPZS8wdYm3k2yFqrrYQ'
        b'3yOU/gm2oYSPt3INtlCMUyg2eZ5VueJQ2EXtEu0aFeMaBWKOngjFajPhS2U5FqhOXaYFMqo2W0yEreVHIytTGyxAXmQlWh5MgRy6UwPIHYroCHHXaWixH8zspn43RMl9'
        b'3a4ZqYqpd3ZkwHzLrCwvncpikm6dZP49xuGdyIS9mqqv2eTMbomRnO8YiU7USLSq/LkKUTUayeF2j8hUodeZjSPsKrxAZ2Ueserb4KTME3As961YxHHcd1ws90sLrR91'
        b'49OmSNyKW8NxYwTqFjKSBG6jwfwfVOeVyr17fKYXFZVbDGYQH3r8Z8Ca82KHukKrfzyAV+YRFfnXQ2YBFJQBa0HUpTJe8AEY1gHmgSxEJ9sjJCyQkRgUfXkPIhaW8RxN'
        b'ealBK8sp1+sjUwAlGRSqaqJg6Q32IrnkxapcGV+MKNII+jTpTBY+gqQ5hvlNN5fo/XgGn29oxkJFTlGpHt+DxdcDU+IYTJ6h1WtLNGQg/KtV69L7HmMVkJJtM0EZfsIR'
        b'aq172ya1yXiuyCr79WqprFIf5dWJvAeZYXeZqVxgrYE2p9dBBvqmMxSXyxSy6UazrSvWmFQDKflEJMkW4y5bjEu2WHfZYl2yxbnLFueSLd5dtniXbAnusiW4ZEt0ly3R'
        b'JVuSu2zAZGTlLIiGCBW/MITZ1dLIGJdICMgytIAwbapYmUUp61XFQiQPyzbdqFJGGHab2M3rXHuXUZYenp48x2JYRc17tcYSwFDVBKuQ+BkLZXETeTpbbMtCdMLu4q1w'
        b'wye5qTA5l8oDZODGMjVJtIOIuxQ7qHgqFtNXMfeJPAj1Ucx9Ig9SfRRzn8iDWB/F3CfyINdHMfeJPAj2Ucx9Ig+SfRRzn0iKTeyrmPtEutxRfa63+1RasG9A8Qwp0X2C'
        b'iodUWrBPYPGQSgv2CS4eUmnBPgHGQyot2CfIeEilBfsEGg+ptGCfYOMhlRbsE3A8pNId3yfkQGqOGd8rWgWkaw0QXzPlTNdodSZt8hwg8b3YD9Ch2qBXE+WiaaW61Ai1'
        b'lmghh0FLuKJebaOVchKEN91STPRidiRno6WQRDBvL0GWhU43VPMcMTnQA2ScoTMDadRqgANRm59IfgIPuxbuxeRPphn1+IbJyiY4paTQ451iM3AldrmKUhIF5XfcCgHW'
        b'kVqpOZB+oDSEhy6m3HMZIfBmrQ6mxWxXFKcCq2vWFetWqR2xfy6VA+0KZEc2g5ceHQ4SHdmkOVpetNDqCklSOqwaORkz8ZyNZ0bNUTkM/YaW1XpL2SptqU2TTYkg5eLk'
        b'wMVlGsM88bAR8LjnkYcdyv3BQrjcSrwDXTSlZ+LtkZSLxS3oyAiVFzOgUCjFO+e6cLJSGye7knXmZHeLd/vu9tVwu/vt7sdztK1emoh6Ub1ffb9igcZXI631Bq5WqBVp'
        b'/DT+tYwmQBPYyuWKIRxEw8E07AXhfjTcn4YlEB5AwwNp2BvCg2h4MA37QDiEhofQsC+Eh9LwMBqWkh4Uc5rhmhG1klw/2st+T/x4a0a2+mgU9Zy1t0KNTDOK9tafH9Vu'
        b'n91sMRmZF33aSo1u9dYoqX2diDqGBEJZL80YzVhaNkATCWmiegl1GwmmaeM042u9cwMhNgj6NEETCn0Kgjb6aeStNncH//qAYpEmTBNeK4Fagq2H+lE9klnEQHxmzqKv'
        b'I31kDv9s0TIehfC+TE45ukVG4hRjJM4+j6mdeCR5o5YaRBSQSx8Tk5vH1OaZGNz0Zjcm2rIbk8iDWHI9JqYOj6k5AIEGuVePj1pTCVjJmK/T9HgXAW4wmMmrv5qXW/L1'
        b'wNyZS3skRRbYNoaitT0SYuCqU+utZhi+xTrg5/LLYMuW0rZ7BLMXzuftPIwT4VEkcQBBH+svtdohRjpOLlfe9eJ6n3qvYh+rgZCkQVLDbPCuDl4voQZC3tQoSLLRO8fh'
        b'PYrRCKiwJfyS+Go4zR75l8p3V1etNVFXM/uc66hBQ5FW6VLEJWISiB3qMlnvVE2yOpkBaiFqIKsXm3XO1AazSw3kX+gMwAhmGz6SK2XTSXnAHUUyalIos1TIAIMmyjS6'
        b'Ep3Z5Novazfsq+S+F3yy+x7YDzt+oA/xP9QHZ/CYJEunf0kX5kam21KtHTO57wuhNwTTA51QyhaUAu6HXaCVmSyFeq2mBMbzVLXwliS8kAo1ydRQBYT5/sv05UCHjEpZ'
        b'qllWZgFRpVDrtha1dfCFWvMaLTnslYVqtMVqi94spz6GSZ7XwrotJslmWt9kRURbGGo/Y3TQMso91WLbUpNs0GqyLyZxaSw3ykJ5i5VV+J6xGgRvTxVZTaQmUSmLcCRQ'
        b'DQ8jVgwTqi1RyuKjoyJkidFRHqtx2NOTZHNIQEYDpLpinQF2DfRRtlarho6FGbRryIFnZYIyThkdJnedqqewQ5bynhIbTUGMjGGSXoutTJ8UPoWxEENXvMO8CTdnoHPz'
        b'cEMqblVF4sZ41DmPGKCmpMtxc0SmAjXhHenZKeh8SmZGRmoGy+Cd6Ki0HF/De2m9j7KlzGCGCX1PXKT/Y/pwxjIFIs3o1KQn6uUrxduJRWtrOGqktU4xOtRbu1bKoIfo'
        b'Lq12qVbCAOWOei2oSs+OWsBYJkDkXLwNNfR6e0EFSkUY8Z9BF4RMwjIxuoX2msqLqLsarUXo40VIc+A07er0fWnjGAvxzQlF13CHu97hBqi1GZ1GByJIL1vkixyGjW4b'
        b'fdEV1LlC124+LzBVQ0Wt2xuHv/KO9+Yoad37nTev3dnWfmurQPJrr8jI0ZlHZSEzE7+M6++/5c9du+rmjqkd17ir1nBvRsczd94YuO6N2YXHMv/7zKTSgC/PfP7lkelB'
        b'8/4y5D216Xnhjk/UR3wfZg99a9vrY7/569EXexaoHl1e273mxDsDY/cPnzn5+6Ph8jubr8ulvMdW0xDUhZoXoZuRDh4nAeMExahuqFlGFrjOsgA1ZzmuJcsM6Q/TXyOs'
        b'RtvKzET5F7cY3fKFGdUI5Rk2v68BqF4owdsn0lq80fnFUAvevgRfdlg/lhk4SuiLtyupA0F6CLoVrghNUXCMGB3k5uCzCtQWZCbcFD4uRfuhAqUiMc6+XsHoggDWsg3d'
        b'5z1f7uEzULFSjpuARROjc1wqOhPrracd8E1DtagZ7yDrkz7ZujpiJrhSgO7jE6jVTOi1OBwdQM1oT78sG99GemldYAAlXCdWLjNRk+PkIWoynuaIMCXJg2qh6la8I5zk'
        b'k5lEfmiHmver2IH3ohskKzCBl+bjRtK0AhpG+wS4DrU9YybcAL6GzuFnyTQ78IvALA4JF6BbQujSOdzFm0z6/ES3uF6XGWp3ShplNjHrxayYer+JrT5w/vAkHnASjqSI'
        b'2eogG0W2O89k2jpCbU7JdjBOI4/p5DGDPGYyNj+dWUzfps0SvlRvJTPspWglbjx+HpPuE/0ys5k5MMKzdatrx53Mn1nrL7UsJT1cz6zkbe/ZTDnb45vfy04YB9sn0cHf'
        b'abJeXVaoUU8Nglr+Rmp0aNGW9rUVvVvrsrECoUA2NIpyg36tvJvtEWjKi56qa6V813zy7SyGu54ZU+DRH8obU+Hl65F8D/gibjrwYyYlIN+ZsfDY/CB78/I+WY8f3ZES'
        b'viPe+TbK7rELQ+xdCJmhNmntrMBPb9LOWXtqcri9yTEeGYUf2Xgt37gk3+Ya56ltWW/bHpmLH9m2Fdyk+Y4yhKf2x/Su+A9wJB564eSOQL3wuHrG7oX3Y5wRXLxnbNW7'
        b'OCNEjK8RUB/gj3KLeG+p0uLPmNff2dDyy5ZH0uekhx4zU48Lex77yzlKhAYmiqyIvDECbS5xROT4OjrJu6Ic3ogOuyBydAYdZ4ZQVB4+oS+POK98srccfZ82wc+E6kAH'
        b'bEYz8GUGPVnTYPuqLIXHeNbm5LwZft7tw/vNpX65T4+Xdbfypv5ik9mo1Zp7JBXlJjPhonuERTrz2h4vPs/aHnGlmgqnvkXAy5eX8UKrwKwu6RGVwx4wFvk6rAdB7P62'
        b'NZlPltvXLmz62S8n8Oevhyj2t4KBb4MUwEAKYOBLwUBKl953ozTH4d0qcpaAyPk7kRuRc7pGYwKZgjDGGm0h2ZXwv8hqMifTUgP/p5A6qUxEBRq1rNRSonWQ82CGTDqQ'
        b'k2S8EwQR2Uxas1KWBVDvUg9BD2XkoEZXVlFuJOKprViR2gAyDykK8pJRW2TWr5UVriUFXCpRV6p1ejVpkooIxODSpCQj1RGVG+w9a5VWMYvU6VIHVG0x6QwltEf2amRh'
        b'dPHCnmJG5lhHW0p0Ja59d8kfalYbS6ANjQ1PkfIyokQ0EZHFtNpCZrfQqC5apTWb5JOeXhPAw+0k2XQnciPLo8emyz0VIy1PklGnh7wfdH3wWAu/TSbJcuhfWZ7VEM9j'
        b'ftt2miQjKlBYKiqh5jka4nksSzYgyLbwlOVlGc2e8/FbFLLyL7SNCFlqTpYiNjohQZZH1J4eS/P7GqTW6QsUqbNkedazxOXheY6OHZ4b70UHRA7nAzJSkaM5scfigEBg'
        b'Mktha8B2NRUZdRVmK3UjcEocx+nemq43lQP8ajVuVQgATiQ3oUV6etsQXWylbBavR6BbdHSOWV1WRvzkDKM9ahToZgDAgg5UWLeWRkfvO1LDtK7RAc3TVsGKWzecaz3k'
        b'X2a5WctvE7r5tebScg1gkhJLGQAa9EW9CjYgbBotzE6RVlYOxN9tPfyQyKahChITP0ydyaFLStkcQGo2hOS2FsdtR9QpAOrkNqciPQyYv8jJpHVfssB6l1N5Ee05f8oy'
        b'udRsrjBNioxcs2YNf/WGUqON1Bj02qryskieD41UV1RE6mDxq5Sl5jL9mEhbFZHRUVGxMTHRkbOik6Ki4+Ki4pJi46Kj4hNjJ04tyP8B5QWhiK5Oh8GZ9KKMxagTN5jS'
        b'5WnFwQplZkQqke26QUwcmyMqRbdxh4Uo89PRVrwZHUP1sRCIZqLREbSbagFW+orINUCyqIGJ0ZdWezMWojvFTanolspG6LNxQzhuzUhTzCcu2YX47vxQ4o+6GDeQPyDL'
        b'oV3oojfe0x+dtFB/0xvFIIuSK5SI0Ogz0osR4QOcFB/hr6UBobIZ7cJXleRuD+KmC5UvwYfJzS0cMxKdEuI76EEm1UakoYt4M74K4nfGQtxWAWN0GOE83JAJxVtUCyvg'
        b'kYUvzU5Pw3uE0Hm01RefrETXqcXNIJ8yX6U8B7enoXvoiA/jncbhI9Dj7dS5Du2bMwBfXTQwFapgGQHax6LN6OQ8CxFwl45M9cUNkUrcCC1GoG50FV9Mg5E1sIxsrki4'
        b'cQ2d2Sp0Ep0Jwjfw1cgwluFS2ITRAjqz06aKqX4lSizKkwk1DO3NfD1r8sN7gKmqMfJtSpZxcxPQDgthsXAtPoi2kQx+fkq8E19PV+EafDkc7xIwg9YK0LnkcRai28jA'
        b'1yN8lVAeJi116RwyIwJmAL4tDEDHVuomTHnI0Jt7Sk9dUbyq8kHTAoWvffLih7H/+jjzxVdrbn3hs+LY9NdbhVdVCf4zjswI/svRtzb//VH2zNeniMMV7wb+rsU7bEr/'
        b'Mdtq7uzefundle0vqFVx73zwef0bb3Qnvj3qJVX6b195++/XjooUupnhmysOvj4tPPeNa7eP/e4vlzOP/emdLx9X7vv9tYXf/G3b7Q3rLcld77z9aMLtAotqqnrA+8/8'
        b'SvKbkWk3wpfHb5KLqXYFXVqB6lGzTUOzAsZsVdIM6mcmWi10cxWAyRM6C7xPyastwmNFeAe+jC5RjU88akb7iK6GaGrmVDjoaibgbbzG51nUVNjL6DZucNJYNG6k7rQW'
        b'fK1/eKYiNTVDJcBdEbhVzjID8T1hzDoxvQIAXUcXJ6oiQtHR4SnQN1hBdJZba0YnnC4U8f+pN/149K71UWs0+TwTR3no8TYeOkXKSlkJO5A+HX+E9JYSCVvdz84D99Zh'
        b'VXb48ZqIXMZm8UbuHTEuI4/l5LGCPPLJo4A81ORRyDjpPtz7CfvydfZWUmBvotDehJ+9RbW9Hcrja0gVTjz+2+M98/juxif37pFqiEGglWfq8eM5YVtQrC6jf8kNLdoe'
        b'b+spcJG2x5fwLcAtEhsxvkf2QRf5OCBlorIJtCHlRYTR93Fi9f2B2Q+wsvuBhN0vDrQy+z6U2fcFZt+HMvu+lMH32eib4/BuZfZrgdnf4dU3s6+22/rJ+FucnoKlnU3c'
        b'JPjcMqCrMG/ArQKvoHa8xpDwExGyEmO5pQJSgY1Wu9Kp8rJCnUFt41zCgKkJoySXp7hEQ2C3CyUdtAvNLjURIfr/Sif/f5ZOHLfbJLJQfIxdN/YDUorT/uTL81G2Ctyy'
        b'ank/YCvqsTl+//PtWLe8NY7ndg3lRNdjpPyswT2XuqacsJO6MrXeAz+c14e1LEgZ7u1lPfaYYCq+v4Xl5atIf0mMUpZhhS41DcvKC1fCwoPs7/7M0UCko6SEqGir+owA'
        b'Aoh2pLq8Xktaj52wI8pJsoUmi1qvpzsDAKeyXFdk3415Doa4fQqIVkTrvAzURS/P0Vj3B0U4UvwJMc7JJPT/AClshnaNtsRq0PN/JbH/AySx2ISomKSkqNjYuNj42ISE'
        b'+Gi3khj517d4JnIrnsn4s+W3vEVM0jx6f6r0sm4iY4mDyFVo9xLUka1KzcBNEal2QYvIV08KV5vQfe84dB43UdkKda1dja+i88lW6coqW+WgrRZibBOQj/eqlGkZwN26'
        b'rRXdxTd7xbZm3OyNuvBD1GIhZ1L4Ctoaa8rKyLLenUTqX4zbIP8O3ABSlg+IJVAnhG/nLEOH0EF0wptBh/EOdBbv9c1Em/FRKp3IjeWmNNyampGlIrcuRS1B24TM4BkC'
        b'3FKK7lLJCl1BVyeZwjLw9lByAqlMRedDWQZ1qEeWiET4PL5N7cxw94SphfiBL76Jts+X4FZFJghhHBMcK0DH8K6FlnEkzwm8/RmQNXtPvVMjUk3x6Pp8csdpNGoWVeUq'
        b'qJiMu9B9fLIEnbH2LTVCTu5L7Y9PCPDdmXg/XawBywXMPAtR5xZIzesXMvQ+1oFKdNJXzDALFuM9zAJ8INwSD7F+uG61L5klmM2d+GYKCJ+tuB1fxx1riFjajM5CRDre'
        b'nkJks2Uhkrm4ASRSehvsjTksvgovqb7oPpOKri+nzeCdi8dT6RztKmaix6Baeu0r6izD+/jbYKvRbSYSPYzUf/X99993xogYaVo/Cla/G17NH+lXVHkxXwWHkKt+098X'
        b'TWMs5NAR11SgTjI7rVZhPiViEbmzOTJtIQBFCm7JCZUDaKTY72iWoxt09li0U2zwWz7JYOHvwPM35uA9sWkChsXn2EoGn0vG+3hLiZsgpV7xta7Q/F6QkTwxP5tQB5ki'
        b'dAHvEjKofqH30gx0g14ZiGpH4RZeMiZicXYo3pMj8VMmw0wSMdgqAz8zQOzvBdBBL3Y+g/eKTWmKrAwYlgofXRaZmcoLwnK8X4SupQ+i109rAEy7w9Gz6AF/f45czPii'
        b'hxy+WoCv0YuJVeJM7r/Eg4cLKtT93lmyMG8nb6WhQZuX4qtWvQeM5yFvokHu0W2MzMrIDrVW52gGAeJllxS3WaroxbyrBo4IRw1rlakRYSwjRju4SDlsYqIySMRXBqmo'
        b'6LjQjzOySagdnZUL6CyjnWOiwvE1X4dSLL5A60vHx/AdvhjahreQgooFdIzo2mrUEo4f4KtPjLEcH9RtrtEJTc+AKNU2OXd525RMQXRgXYm+PKFj03e7ImrD5+WcfM8/'
        b'bliBcP6iGaWN82XlNXJx4+jjnb+9NmxLk+nUo7J7A1pLft+R9auicN1ir3CfztEZltOp7/2sYknVnLrwi2/NaRmf4/PNSwergu+2nPx27u+3mFfm/Xpr+rR/ZCefnvJm'
        b'f8ulleOXm4dbJkk7v3ktffl7a7o+vz1nzjb9xwnPb/l8S8KvI09/s5P9e0XqjuUhP/e/5r0sOeTPtwoPVP1+3u3fvGl69gXN88bdY1K3X35/xOMJDzJWrNn9hwUZJ7gx'
        b'n0qXfqDY5zt8Zsaxd8POS1/9qP7K1qi7/5hTlVkxN2/jnZ1LcZWpPPxTxenfdx570PHqO7EVh8Lqpxx6JWDoh7O3vv3yncg//unlQ8s+NL/wbYvPnw+OuCNa7/V94pmP'
        b'z66T3f7myoB7VXhXYXVr/tvR7a8ptOWb/lFmfMVnmNyP3umGNhPk1auy4PUV+HK0oHgBOmomOAltWYj3O+gsxg11sLSgKgt0aQW9fKtMO4ebbNNYOOgrpsXT5JXsRpWD'
        b'EU/AInx+rUCPW9E9mgxQcHVceJjVKgRvR03eSzl0CjVreT1FA74SHr56nZIg/AgCTNs5cpH6DjOBQfwgNVaVHiZm0M153HI2Ed3GW6ipShqgmxvobHpGBMcIVTPVLLri'
        b'jzfzNd5NKgDEVgvjthmEiNdzE7xN1NIDHRLhNkfLEXsmvAWfJZYjYwT8QeJd6EXrkyeJ0Xle1nPEStxIDUyKx6AuE9ldCkK8WvBBoDAw20G4TYAuoRb8gHYqJx6fUkWE'
        b'ptg2ximqjkGbhX3cwSUP/A9pZ9zpafyJDqJXJKe6mgWETdhEfzipVVPTq68hFzTz2hoa4oihyghI7c+KqbkKMV3hr1ELhrA/NWbx4ei1aoOcNB+9rVq1O1Jew6Ilj2Ly'
        b'KCEPcjOkUUceK+1aF3eKHa+nueHZh6+z2F6x1l7TSns7fvYmelU85NL8XCcVz+kwzyoeTwMtEjkwYuSY3flCeFG9Vz1Dz1rZeh+qmPGtF9ovhBc1iGuYDeLq4PUiqogR'
        b'U+WLaKM4x+Hd002ApLGRzJNcnz/P9amTBMASDpb4AyPx57HDmQU09u8BQkbC/LZUNK0gfeXkYbxKGDWhe2iLCbVKVgsYAb6GbvgDSbiBzlGV8MyhwTmodQFuXZiRja/P'
        b'w9cX+iVERQGnh7cOHyRAW9YCS0VowAp8GHfkYMhZHxgfhZvioqCp1SywZKiNNoPvrSiy1cQyojBWgw6jg6PQIf4W+dP4Qhm5AR5fwi3MZGYy4IBmyoDERKJ7wGWd4ibB'
        b'0o1nBuPN/flu78C3q1TKqLiYeI4Rb2TxtlzgBe+gs3zqcbRf0HvZesBS/rp1n2JdUfunrOkjyFLwzp3ZWcmZwmjp9Q9SP7r6M2XwjGkzX55+urT78bnlurZp+rLFb9z6'
        b'UJL6fFASM2DAuOefO/DsgCvfHPrnF/oJ20J8QpcU7fzrEGnnpYdXDbNmP390S82vX55zNGz7Qnac91vb/y79t9f0zvB5H/5ij/alwfsO7u0Z4v3h9qLnvEP83//u96ao'
        b'R2OX/LEMj0v/8lpw9bdRV15d19PzwTdvrE0yDn3X8uiTQe0fJC5+/lctDzeaqt/968h38soqj2YXTr069pe1oqCwD5QX960xvHQu9159l2/G1Zv7zH958ME7fv9cq/iu'
        b'ef2rgu8fX0yrqt34T6+jb8x74c0z8mB6P2dxFSBB4LfRXlmkF8Oh4+xCMv00LQPfHW9DuPjqfBVgXGB6uqjlXwjQm3NQsBffJiVxE4YspYRmDnAlV10wLuoAXG6z1dua'
        b'wevZ6/HeOYRoof2znI0hjXNpBhaY46uqzIjqAmADd0SiM0LGHz0Q5OP7eC/tZJAOH8HNKno7vrDSNIJFx3EnvsFfMNqAOvo73uu9wY/c6r0InaMYelb59HCl3G+E0+36'
        b'5ejqekpQCwejLap0Od682NEMcyA6Lxxqtqrtg/MGqAgniWqcDCyDVwrQOXQMXaeToUb1BXaiG4y3Odk38gcFXYF0rPhaFkBqM7GXlGnt9pIBIwQr5mbxHwu4phoFhHcG'
        b'Ou5AewnhxQfogJbjE6iX5hB6g2omrcVNo+mSSYR+1g8BkI8AJKLN5DsAaE8mnapB+AB61ukuTw7XFVRpUD1NnikHYkbY2e1Z5J5W1MahTryrHB30fTpk/P/q+wI2Ox3+'
        b'awKUbhX30q1IQpWo6SQ1oBQSmsVx8JenYVKCsumPkFIy/uyBhHhzS4k93f7zvnCUkPPnBnKEujna6fAd4CmYVy/t6PHi9dWmHpHJrDaaewSQ78eSK5GRfHHHaLBTpXI7'
        b'aaJUidw+e55QpdE2qrSZ+W/Pnypw7fb/gu2X9Rzg6z+4qCF4by+zzcXEqs7VW7UsRq3ZYjTQtDKZmpwWOChtnkrTLlulXWuCeiqMWhOxsuS1QVb1lsmu4reqhtxpyJ/U'
        b'/ut5nRrpTuFas9aN9sqJyIodJ9DBbJ/e9IwO4HsW1Iz3oh2oEV3Gu9CVxcCdX0Zns1GDiBmMNgvwaXxmXR46xn9C5TRqBVLWLmKGr2WUjBI/nEdFSUDL27MpAUbNixVE'
        b'g6IUMP1xHb6AGgWoG9WNotR7bAH5ElLbailToM9LMjN82dshrL2oeDTes4grJIoGfDyGCYsXJQWPpOfMleiSH74MDLmDYIcPR/E6nctz0XFH0gydPseig5JRtNcWdHg0'
        b'L/ZxxvkJbFIRaqIkuwK3aFaKcvhCHGplhynQQV2CJkNoqoPk1/7xUcYro/w5EPfe/2dxboHfLk3kc95tkrglFe0ZlcM3/mLUotXbEt4/GneS+2fH9x1BS24fvfSo5fmP'
        b'p/9V+VzbgNkt4189c6zzglfthYhPzN2PKqa8f7u85JM/Xn9WfmWCaszWvd/7/epGSPaVsvC8P2+csiDzd8sPJq/e9seA//ns65+vxn/5msucNH5gU6RczNu4t/gttB+7'
        b'0jNXdGWd7di11Z+iTa8RaGswiAbNRIi3XlKMD+J9ZjIHU1KywpUZHAzzND4dzqrwGQVP1w6h8xzQNfqdEHQBdSk4xlfL4aP4gJLKGqNRAzrqxvqczaeiBt6KzvLeAnU+'
        b'Sxw/AIMOoJM8mTqIDsvFP4BUPFg8qk35ZMNRTDq6F5PqhYJgnqeHvwQvkvNb6bdi0WDOAZ1YC2f+oDmkER4fPoGxDj+VQaS1iW62R1ihNpd6vvd9BmO9RJucZpJvSIjt'
        b'd78Ln+rudysGe1/AujnJ7EViBJ+Y1JXkTa93RGdP7ytHBjJJllosCyNvYTLAySZeZ04QlbaKuOISFXKYslpXERZBG7JiTKN7DbSJ3Deoseu91caiUl2lVinLImr6NTqT'
        b'1o4VaR10ADS7WlZcrgeK8AMojiyitwuKk2RaQuF9FDqRGJ4Ce2ZeCnApaRnpqHtByjLgbs7jhgglcBApeJtXxchRFB8GoT3ZKthhaRlK3Ag83AKQ/Jsjs3HdCuBUFKHk'
        b'shkVvuGF9qZnWAifI8edqBu3o7NUgSDQs3gzOoW2om0gUxCNJAvc39Zwr2x0gWGqmKrwQKq9ypCjhnAoczYLoGo+gw8a8EVd4ztzOdMNSP3yNb8prcnka1HbNiXL563I'
        b'mZDJHmJXs+LaBTcatrDeL+2P2P3c0OAxOUb5qzVvpL3Q/O0zU5snjtn121k3P3l1e251m+aX5p7c9GvfdirXGIKaa5nLq9sC6189/enskFd9cvu9MGZ7cELSongv/1/k'
        b'RExZ176/4vyXQyZkbg5Udn3+q7FvdNz87sBHrX8pL//3jYp9HY1fHvrtAMXDgc9VD/1j2pvfjPBf1BWf9v2519bvS/uVadqiYZWhR56ZPWLSuvXX5AG8UuSUsZDONsB/'
        b'IlsVii5MlvCajzOmfMKe0q/MAWM2C7fjZm5DdQFlYYfhG/g4voqvrbEqcfB+fNEbdXHoBNpTxXvwHBuAb0IN6NCITFghkJgyuWHoVhSPxQ7jrWvI1/QilKk0EXXn++JL'
        b'HL7HxfGanu6ESFUE2p4FuFPJMvjkZN9pHN4vxbWUN0cXBwNehPKDVZFZxMVoIxeWg6/wiO0WPoceEPohV+IdZGjoId7OBEQJSmYNol1LRzUTSM9q0V4HzLslj7LCYSZU'
        b'Gx5JDikUSjk3DV8D5v2IANXhlvFUW4Tuh+ImYFfnBAHEgaAnnswNUibwo9pGvs6gskOqN7oa258Dfv0SepaOqhjdZIlogy6iLuukzOAG43voNk3ORkeGODDSE1m81wuI'
        b'/A58n7ZcbJ4bHokeEuUXrIgYneYi0PUVfSl9fgCLO2BuIdnDzkY25MebV9tIqCeRFNhbmxomEGKr/ex4lZTm8Xa39UMIZsZJseK5k90cn7f31vtKeHz/BHqvGdjHhxGc'
        b'uiG3+nHPZojjv905GtCL9Z9cxP/h4LffE1dgEZt9TXlRfj51T+qRVBjLK7RG89qncY0iRvrUiofqeShbTSkVHQ/P2vf/jyvh+lxVIzl4+4CxSjUSTij0YcXfC8ncfd9/'
        b'HMwmy30nFvzIv0J/AQCAtZaBkQAU3wsFzPfDsock+g+VsLwuZFcyPmIin7E0+fsLGL/h3EBgBY8J+O9OlknxFl902kxQi28quoMPZuDt88j5y7AY4RiQsq//L33TyUWh'
        b'ZavemRB5ZfK88zV8X0UcaUYxsIGPj0LXA+kXOtH5ojEqJboUhS8b4qE8vsGuRpfwDsrZDsB1QVYlELqhtn90rxpvoROThc/Pxc2pEYTnWp8fKwSBt5lLwztG66KlfxOa'
        b'CMy+OP1PnxYs+9mltmPt0XWr2aKom14fcJ11Ut+Q5OkRH/Xv7P9RXXpBgsrHd8nuYy901kTXHas5tid1Fzu23ys/OyBmVj4TlMudk4somqwchpupD2USOm11o4zF9zIo'
        b'gh+LdkzgkQ2qmW3/ep8S36K4JqzYO5yq0XHtQJsmfaA3j5pr8P2FVpEd3xVZpfZy1JVHSyYtIZwprGgWk0fSlnPaofhWX34yUpC1gJXR5hOzB4qDBjrioLFEAUxwjhCe'
        b'xnX2zSTsEZICPWKrA5vL56PI3XTG9fbNQEqO4mz+kputP+975hvpB1fxlcDF4aFpipSINEMBao3kD25leK+ofxx+4AJNA6x/TV843vwRTm6/AJDlNIJa71yBVkg/xceQ'
        b'j/C1crkiCEto2JuGxRD2oWFfGvaCsJSG/WhYAmF/Gg6gYW8IB9JwEA37QGte0Fqwph/5jJ8mArYLqxmgGQhtS61pgzSDyU0fGgVNG6IZCmn+GiWkiqmXjlAzTDMc4sj9'
        b'HGy9EEqM1MjIrRy7fXZzuwXFgt3C3SLyowkp5iCO/BXY//Kx/FPI53B4Cp9814w6FAB1+fTW82QZzWjXuJ/21Iw51E8z9hCXG6QN1gZpxoUwR/sdY2pYGhpvC9Ec/alh'
        b'I++/JIE58bLeRTKAmjx60XkSaeSaMIgbqAmhfkpRPd75QI7Uc4A5po7nLtp6ZxGDN54U0w8tiu06etFT6+hLns5BzofX0X+XQ0zfk5KJNn45580foVemtDKD2Ypl0nkF'
        b'yl3Bw/nIt3zWs19xUdF+Ueq8bm4KYyG3mySjvWOd/O2dbsS5TszWd+BmLyanRBI4H9fQiu6HjGFmMfMmSJgC7szGgcwfbZ2kHoa6f0eFsSZCNI/ndQ5vec5vc5RU8Gzc'
        b'qSgu7y+fjZD+bEJwyrcDxh+d4ZPX/sXtq+NenjN+aMQS/ZSdE+Kq1fPCkgYlDup+e3ja6X8V7pmTGLJ+eMuAISMPr+v3p5ZnvIYfSn3j9/lzq5f/vOnxV8zpIyG5qV/K'
        b'vc1kf3JRseTbQdPRVSBQAkaygDNviuDZym7zBNSMLlLNtDgXnZ/ABXmj7ZStzBVFOp1b4jP4NH92OR21U32s2I86h1snBR/GNbzwzU/KuBBRaTw+SLUDaEviMN6BPTxU'
        b'wedp9hqP7zODhgknL8qkLPaATUr+61aolaq5AUMHxU7DHQLgJy8W8MbdHf5od2+mDHQOJKK56BjeI0AnlOgwrWcobsO3UHMkNLMX74lMxS0sI8FN5HNY19EDMxG5RhQt'
        b'Rs1roBZKkslXk3ZkAWFozMLbleKNYcxElRjtRbc38nj3qZnKXg/1EY74PEbM+ogk7GDqqW5VsLLVwfZt88R3JXl1aI+IGj31CInNbI+09zTMUN7jrTNUWMz0drBehtPR'
        b'Ml1k3EreN5NHDWPjNbc49TPShTK80QfL6aa3P8YHWJRPhuHRAXc6Z90eju3Y/dCH9V506uKGqzSqCM75ES7BfvmOc+mxS7NsXfp6hEPzri7oyh/n/d67cp4anmtveHiq'
        b'LbPNePNHt1ts8/8mwJRfpvPsg51mb3YgkS5kxcbysh/fXolze+oqj+1l2NvrT9sjpr0/cVbF+eZys1rvsal59qZCFpCMNhNgj+3959y53TLgHOP6MUSeBo0jJ8qMZBxX'
        b'kN60JognTI986R0uTPjYgvTB7BBG9yiBE5rILW9pG9eQT/ymqHdrQj9SqaXF+xZ/XPAx80VHSM7+/wqhn+8tuCH6pO6PctZMrn1D90bh+w54D9+Y/wTq4xEfvo3v98G+'
        b'UrmPYjniA23HcosIv1od5Ignnt7XO8cFGV3sQ73p2sjj7+Hf/5IQ5ZbjcBWirGs4SSciLiOBg3w365dEvbCQTtLzF7785bQiCsWs7yPdOx/GCU2EDn04RUY/0ny0paBN'
        b's+Rn+9F+dK2tW/DKTbXtY5Mre8RHvrkj58xE+TccNcl61+8CMCBP0i7rAm6eSan72pFU5RSmUOKWJUSm2crFjsIP+hJNAvKpgbOuWptfqC8vWtX7nT/bOi+rDnGYfufc'
        b'Tt+4FVHLXFcpZRfjpPzYCY8lLst/po/l99y+0y62QQCZCds3bwUAA4L/hCDNMu4PrSgMLPf+J7tk4O+8mHkFzxwJTGB4K88mDT6GzkLe6g2onqnGd+OoBjavzITOwvjX'
        b'xUxn1qF6vJMavab4oCbUyjkxn+QjqaGZCpaJQ41if3xoBrUSlbAipv/EQcRKND1ujB9DLR59xhGLR6aqbZy53ztLRENieKfP9ahroe3mp167x2YNMXu0gpDTnU/H8AEf'
        b'fBBdWEbRJ7X8xbfwPoAwq0gfi48E2WT64+hZ3TbFYZGpkfR/f8G4XxId8WBBQfKOGYMWvZkctahQ/aH4lYiPRwYeOLgg/fGMfQ05YxPHHesY9+/2fhdubRo0qxZrgscs'
        b'8nnWu6tBml2nbgn807WRJU1L/6UunB85rvL0Owe+zxj2esumm51fvyr/fv/1z75btSeDfT39xpXId68saT723UeZX6PYOOX+lve2ffcvwf+0jW6RcXIv/gObZ9aSLwP3'
        b'qkiZgCgfuaAEn8+k6YvRcbGV2w0f5Win5+NtJndpGqahfY4s4yz8wN3OQ91h/JVID3CrwTfMKilYOWj8EJ0m7q9XhfjiaLyN1luGb8+l5h2EJYZlRufSUCvUqsR7aMVi'
        b'JgqdEQ8rRpd4M4zLi2EYvFkC6sIXrJ6J/ugg1fMuH4632GwL5JuseooAdFFu/xS5R32oOH+NUWf9/qsT95pPzNY4dgRwr0Os5mxStjrQYQ/Sgs6ft1YbS0weeFPOuNsZ'
        b'AbTDY5kLAujs49ufLo1nFgkd9qbTgbL1e8bUY8/+PWMhPdMSwdYX0q0vottduFGU4/De1+euRS5bX5xJd/P8/CjULgBwG8+MZEauQdepTEwPVTZlLg/PVixSoAvC3OmM'
        b'VxA3YsgqXcDhIpGJXJ/pN3MC0YK1od8+9+5zl9put9+uub0kok6+f1Td7ZrumomtqXeCWkbt3xLrx5wbJskL/AMQdWojvX0yJu61RE2D9q9GADTU8oRlhpYKUQPeudC2'
        b'Mn3rw8X51IGDrn+g4/rr/am5h9Ok06y89lvsYPhHP05NlVDOSL9byMc+kZOu/h546FxW/0AfnwV26YjnxSdq6noRLL+Y6i8ICHj9p0DAVecgyuQXmyqEz0twTQ5Z7b0s'
        b'I8B3WWCqGjMq8D3dUq/lQqoK2d1V+mmBSh2qDX2UCswbsG4FnxboisP2flrwuGBV8WeaTwu4pqiEWMuVU1GWS5WXfl57Kroxmnz1nGXM96X/Ormol9l9KsMYpy+VE02i'
        b'w5L3d1xyo4S3/SHWpwMcZru3DF/VXs+Atc++wPvhUe6ywO2DPS+w+yYfE6WJ56Wexu9zkXWni37CMru9e8l1p9uWmX53uQFfWIWO5MFK4z2xKQJG5MWiraF5usH/dYcz'
        b'EVeP7FNvfVqQSld5uImsc4r6kwKl+uOCz2CtPysIVJcWpxcFFwG39wrDnM7w+mbJcNjZpMX+OtRCzbc51LlgOZuIG/VP/+HhHv986+WrDovsxK9Xk0WuHuww104FbKoP'
        b'5z3bIy5WF5nLjR5wu9DY4WmfH4THGhcwaO7vGQw8dk0ewFsh9xolE3vkHr9euX6Vdm2PX2W5pahUa6RFop2DMT2+ReTmGi35lmy0YyCmR6LRmfgrZ4htc4+oUm0m9xdr'
        b'LWaQZskdu2Tv9ki1VUWlanIDLETJJfTEzUjEDGMyedADOTLS3puSydlbLq2RGFZF9/jYrpbRaRx88fNoDrPOrNf2SMinSEjmHl/yZvNqp9H0DitaU4zxOCnjRRwrC8ur'
        b'qCN+j6iitNyg7REUq6t6RNoytU7fI9RBuR5Boa5IzvV4TZ85M2th5oIe4cys+bONV0jTxF3JhYEm60z4I9Mcsr8E9sutCEWVFEt+AivtsssE1iacd1kRz0pLzOvZaUO/'
        b'FDFR6nVX9HqelV4/W2sqn4lvBABocbiTDeNW8E4yDbgD3TWZKyEJX/dlc1AX44UPcv7zUSP1nctFRxaEE9bpfGhKhjIVnYnOyMYNmeh8BN4RmZadEpEWCVwxcG02/yjc'
        b'niedyWRRny50Dx2YhNuz4XX5smomY5iOknVcg5vR9di4KGHERoadwKD21f1p/jnoJO6KBZCPXYIfMrEJ6AqPMu7ga7gW8nNQ4U2GDWXQbtSKW3k7sbpJc+wWruyACsY3'
        b'l8MXcCu+xZtwn61ANVBUjO6HMKycQXvw/fHUzgNd1xLLhYv4ALHfjScfiL/M4nbg4Pk7YJTe4czm2IsgmBYUnshJY2h1s9AF2hMWbUln2DAG+PpjI+ghkCBylkoJYmMj'
        b'3pGhwE3pLDMIXahEJ4XTgM0/TGscmS9j3gveyjAVBcsiLQN5HmdFJj4GFQrQNdTJsBEM2h+Xyzv6bcc7cXc4uWslFao4y1u/BqBWQSG6hU7TGt8cOZBZMmYJcW2bXJgv'
        b'4mvEzdxIqNELnxrOsApiD7hlDX8qeX/9ChU6rMbb6SeWhBEsugNs9x5aVRkzlVkf/xXDRBXMP2myDhdfXI12xcahS8x8dJRhlQw6OMpATfeWLUCN4eiyv1KelgHylXc0'
        b'B5L4gUha1XtFKmb9zAgWZi5tfcQyhr9TphsGdIbUJUR7ljFsJIM6tLib+nclzs0Ln4OaqBkcNVvYxo1ZtJLWNUMnYr4aST36Iv6gK7Z2awe+imFVE5jBMXTO9sRBTWTS'
        b'RuFOmYpcR0NcNe+g07xptj+qFUzFVxA/0mtLJzKhWY8YpqAgeNz4fnyVAQrUABVy6HwsHec+dB5voS6SSnQIXeDrzLTDGTME7Raumo+awqMp5I6JmQGlxeocOrD9KnyX'
        b'F/324Sv4pLVwIj7Kr6F/hSBJgnfRzmwa3I85l0UuXy+YPEw0id+tA9GDRbExALO3qujw9mbP4BfwsJ8/bhai2xRiOYDYKyzenczyk7KvJCs2PoqpQLsZNgYKweJus647'
        b'rlsfvhx3qoiZIcuIdVwI2oZa+SPsBiYpNjGKXNHHJkHX8dEBdF8F4oZkK/A1oYsMSGKdjHSyIFDK+/HB/js+GMpx6KqBYScBYKCWZyhKwTfw/XgVP09ydEYIQtclRhoo'
        b'GDAaPaRDLuQkzNHJ48n8RxzLDOaBNhmdiI5NjIOJ30irO4COp9HObxyEdodvhEobiP+kCqCjiBuKt4fxjoGnYbt2QTnhaHSCYZNJN55dxXfwPLrbX6VC5xh0u4Lhytlp'
        b'eH8xTUlEN6ZAEQ49QG0MOxngMB3d5RHNSXywSLVxFcFoLeQQRNyP88anWdrtpOJqZv+KPxOoTvgq3cjw/p8XMyegq1FxIjO+x7AzGHQEXUb3aWVBK4nQn4ea0tPIwYwA'
        b'P2BRxwzUQSsbo5zDvLloJAsbN60tMtBa2X3SW6hNgLasYNiZDDq6CJ2kfU5Cz/qpAKuI0XF0leFWsJFo53xaU8DiEGbeBi2ZzclxAQv5zYZPheI6FSCzLanEDkgoZNGR'
        b'TegBjx72zRURa18A7F24jlHi63gfvSs7Ys1C6nAxPwXkaMUiq5lcQ0ZEKt5OtBjVc4O9hrLj+EU+LkTtKty9xuZBSw6M9nNoD3rYv/cybWUlx3yTRniegvT9E1U8cONt'
        b'hSW4HTjRCCNqYiLwOav+ZhbAXqPK8bgQnxukwjuA1giZceiMyDIBtfPz1OCFbuHmjLJs4tMDiCyYXT5gIk1Kwi0TVAtwqzAaAxHFB4jnzvVC3tW5E7UE97qBo45g214e'
        b'lyXSeQ2ikxNWsAZ3+AL0PMhAx+CJ6zHvnI27ZowPhwnJwNtTFGm4OQ0dITJjtJAZv0AUg7dV0gGPnj+EiVu2ktCMyQPCwq0DfuCbgjuA7UYPC/BhePZbTKucnVjqWCPQ'
        b'tHZaJceMXyiKRXun8oM9jrvxVlW2QozahMTJGMDEJ4F2NmQRPpSTlQkEuRWo+jp2GCwnj2sP4ruoVbUQ5iER1UKhUwy+Fh5BW+03ChCSs4c9y6EaZiRqFuIbaOtwHpk8'
        b'HIcf4g4/SsM7B8BzJBBjgmG9lDPJ5lamZkLJVEWMkBmKDgopRUIX0HnaMV9AzrhDQDCPuh88AJveoUQyCjWhY07FOSjeISwXlKEL43nw3FkALTfDmw5fNMGjCbfTsugh'
        b'Oor3EEtO6DbahTr4xQvoJ1iJrlTzvd4MVKaGaBOYkbh+JDxa8F7et75jE6oL5+8twy0qq4nGMHRdyLK4aQo+TrH4Gr/ZuENEfDFzWHgk4vt8tQdwA3AmzcCYrFLCFl0F'
        b'KK2W8hD4UsxqFdrlo1CkonOhaWSv9ZsmwLtRXSl/wRzuAJzSISXeyPhwNTyLYil2VRjH8k6sNei4ozPN9Q100cfic+isyc+PK0APYfm2M/j8RnyeglhXmC+zf0o4ATHp'
        b'7v5LeGd8fGxmCm6GYZcXZDPl6IKUGlHNg450AeeWQvztW1RZCtLBcnyZkQ0Vwr54gO9TzecfZo1lXxMwBYP9phl+l5RfcNwKtp3oejqvfUUd+Ux1AtqrK2OOsaZ/A8eL'
        b'Fr63/NdvG96YFyh+b+LzjW9cy3i0Lbiw8qUHf+7fExy6e0PXZ3m3vjqVFn3meOi+V/2Cfn17xsCs9/7mM1m642emqMOHcgcOyo458seWCaZffDVla9Pfj/r/LuC91tLT'
        b'6RP/e+8vXvpqSmRnW0/c/MtDzNvG7Z6X+fLlK2d+/quHZ/cfHfPs6efKZ377QdfUTWF/yb6cuzEjpOyl09sOPdYc/OBAW9SqKY2rvumUv3l+Bk6VxTz/a/OVDM1h7d32'
        b'vS/4773RPk8z4WXlhLuz/3HpM8uVLM2mY1+wO0V7azL9G4cVv/3JXxpeeH1G/fOztg/65FDgxBeNL72o2xlbN6lk9qsDPrz3gmhvc6aycVnx7Uea7A/DXo7/9O21sxt7'
        b'vimafPjR/JTOmFfHf/+bNvmLJ9+eVvrda6NOLYzIi3/rGfnfBhyc/KeMv7W+OmvFca+4Qz9Pq6yJiN/+zoXxc4NW37s0YM0qvWXvqcknRuxJWvFy7CfbEsW/ubpuhPaf'
        b'n51o3/uvu0Gr3m1b+T+XDn383XjDLw4mjvp31tlFlyfcGvfsxeKSvENvf1/nb2g+n9HyqfDWmJLPvxj2+Ysa7t1Ba6OCJh/6+65X38++caAqYsDh/mGT93xT8q/lXlXK'
        b'L0bvE69oOvfOizfEVeP++un6v3H3/lU+dEhV+BfKZ/624lHAV6XxU28f+lVh/lcL9q379k5QxY357y5urP7lkshdnYZ+1zL/u3VTWOC3hs/85P3o3fl4Fz6ELjk5EaDW'
        b'VCdThnR8z0y21cLlaG94poIdLQDB/CCbMWIKb0nR6kd2eryGSBNiRjiLRfen4g7q5YyOxE1AzQEVUiO+hloDKv28xUx/dESArqMt5agOX6D2FgvxLW9fxWDUHZFi8xQP'
        b'wncEQPpP4jpqwTaOGA42x+M2B4tZoNAP/XmXtssxwNc0o7v4QWQkbzIrwSc41LxORNND8Al8GTWXoQd2FaEkg9OgBnSHt/N9FuZgD2wsFrB0B8NVstPn4kt0cAtlaeHJ'
        b'4c5e5odhcJTNaH0GXQGG/ll80epQzqIrw9B2WnAxatSiZgFw01YTkwlcUBWqpeOFOT8y9QnP+A2ohSjdR22ilhxeIWthPFeSnjAKoSYh6lzesOSwbhjkaTc624RQgxB8'
        b'VshfMNiCbq1HzdnziYNlK5VniJ21dQ7CJ4rQDdSOdtGlWo3uVdm0qc6q1I5smKm2DXQqORDhLlBfEnRnrKPHo2QaVdPPYtAJ6NWlaZG40dEARTPH3VcEfrSZa49AreE1'
        b'OlUM06vR2cQog9mBrJANpraDxJU8EH6tP1ww6/JD4j6RDA9kxxK3c3YwlCG/UlbCDWFlrD8tQ2ygSd5Amj+Q7Q8h7jPJwGq/XgUN9MfxAMBI1HI/1m2P40v1Hgxcg8cZ'
        b'zmahvdn+89shfZhGO/XJ86n+NHjU89/WYupFdnUhSxUZP/FsnzQmY55UZEzgFRmfz4atYf67mFw7o5u4ieF1iCRrBW4BoYzwsEvxvRHMiGfQQxo/AtWAGE1OR4rQhRAm'
        b'JBTfofFS1LIgVkj4e7Q9hokBsshLIqFLJEzgtKNC4J31oYvFDD0dfGslRI79mESm5w232rq9OXI9+5XPO15MlDrvcmg63w21cVJsXBa+CjWjPdBkPTrOn1s2BK+OjZs+'
        b'VUxuUmW0aDfeRys5bRIzUs3LYnIRTduYcr7mGfIgRlZ1WMBUFER8Vb2O70PwKIgMlYogUj8r1GqE99I8KTNY0kTOSKVbp4XxOTMmQGRUlYhE4g3hfM5Pcn2Z/svUAuAR'
        b'9CPTl/E5O1f6MP1nSYWEcfjkmQA+ctp46NKy14gcIg3ymsVQ5iQCNeMbOYStXEh4b1FlAMhA6A5qmsKzQ22A9Vpic/HpqCjgSMcyaJd8AK96WjWamWUGpMUUFP5ik5qx'
        b'kKMMsUVEuYiAWdVMNe6O4+t4gI8Dku7wIVzKIXSDQTd8K3iRrjYZ3cAdYt507SaDbqJaYM9ITcoQQBztADOVUxSMIllI29w3TMhIltV5EQXBYO98hvJl+bnoEm7He8iP'
        b'CBiobbhpObmi9Cjq4HmbjkkgSJGq9JXDmeHAuJ7mxZq60VDEdlJLj2lxHb7IpeHTGfy9tspNOfjAYnIiBdXuZIPH46u8quvGIHw/HDbLeHSgiqnCF6U8RzkbRKKzpOYz'
        b'krXMWj98iVYzbSbupkfYaBs+vY5ZB2xgEz0wpouyaj3QIckilgxp4ZIxvBZ66dYPyNZZuwF2bvhx3ejcswJTHAyg+vFfy3YmZ+JpgdtKKj+4d6j+b8ao9/28pr352ihl'
        b'W/g388d2XV42Uzvq9itBlev+iw0N6mpIYh8Ftvwm81LgL1/95n8+v1dpfNXyi/eupwlOj/vDpPFjhrwUWhr3nvfrq3FVae4c37+fO/5oYb8/Xc/88+upI1775Z7/p7kv'
        b'gWvq6Nq/WYAAASOiuBN3VgERBBUFAQuyCorrCwaSQJTNhCiuKIgICijgrlTEtW4gLuDaztTavnavbTWtfrXa1dq61NrXt63fLDcrCaLt//f/jExyk3tnzp0798w5d85z'
        b'niWfFr/q/snqvOs/VEU8HvzaxeqP50+7FnqtKb1y4LS3JvAaGns/7rdxds9nB58OT/3gV7/mHUtD7/0n5VzYpfHz/rD/5M6sguvfiFbeTfrRdsC7O7YF77391bRBX8qu'
        b'5S+u/M/q2j59Xw+/8/STB1HLq/Kn//rbeMh9RTDN/op8XcaVlOZYydA5V/Zmlh9M+SbumvMw5furVh93cXpanHzwz+rXK1qKZ3RP6h5yaVFIl+Gxfiu/HNcWUvzLpCVt'
        b'LV23Bh/9ckHEjY8HeR9secr5MaAk86dt7j3JSrI/aIs1H9QYDsr0K9SLwF5iS8AmcGA+CS+I9/bA89PJyAlcsMl2IF0uPwpO+hgic8B+sB/ZGnB/MrEVfCNANY3DJPGk'
        b'U+O4BWCvG5m0hxQgd2Ytmoixa4pJ0DGMPywA7OaBo66ZpO0QWAYO4eRZOAipnIPBTBPyBoJTy2mSmbr5CSZwTjUoNbDEQOVMarBUwQuZWApP/EDiqHUAB+zqF0CMkgFw'
        b'owsb+kLjXtB8XOnfU00Mj9nd4VG85n5sCcsLRR5w9pjO7wMOZtIMQM3zwwnhE01GQJ4zOQ3JgLU8cLiXA228IXi5PnJ2GDcTNnYNp3RRoHluSLtIVuQ7tYEyZLjYjyI9'
        b'7IBuxVZsQix0NcqZoAAbiGHTqxDuNY10hRtHwP3IsBmDTC8Sqr8fliIhfKK8hg/HD7CRkOhOLAUbebDWaQplcCrt44qvBjg5xyj2lgTewu0s+VQMOJ9KwnOrYqwYPhcc'
        b'DuGA+kBQT0fKeXDA3ShjQU4aN08GdtCgsgPoUh5mQxhgySijKAbDEIZBYBNNzbAPnBIiofUmKtyILGlkt4IVxFybBvaAbVgas8Ya3AyKkcG2PIpCM1rADjmJ9dWZWX0X'
        b'IUMrR0RN4gtwPzily59kOwNVvI8L9nYFZ7UhEZ1aTOPjSEHTbAlkpVTI4XO1eRGcibnljF490KsneuFtR5IjwZns4cT+kdc31n25d6z74VxAQi4yvJ4JeHjNVcgVEAja'
        b'Yke9KYObN4ij60BmfVjdSWx0mLGe6jpYcjNpEvURtlLQ23ryFk/+K7fiDRcTIBmJKVZiWjgaZ0wCkHHssUagjT3VfsJrUjRikyDIcAAYCQIhsQBkvZisFmqEaYlhSWFx'
        b'aVNmJEYma3gqWYGGj5MVaOzZH5IjpyQTK5GcLDVA/356DOVybDXgnsORagKeqOsLA8asHPmODo7WzgKRjTYphjWJnLE2fj3gO+HftN9zTX/Xvu7xf7b2cOQ4/mVt1TOC'
        b'XU9RgINE3eMHUqzKt2JEU3gz4TnY0m4ZW0tfoxpnStDLr+tCCGy7aN+lXN0nXqWNdDAykjH0o4ucL7WRCnR0vbZSOwLYEbJ0vQ5k25FsY7reLmRbRLYFhM7XjtD5Clm6'
        b'3m5k25ls2xE6XztC5ytk6XpdyHZPsi2s48sZLJW01w5unTWG5Mx1kPbuxexyxOAVdruPdtsF/e3hVHGkQ1hEuw1JD2Vf1qVMJLclpL+Eihf9ZkuIdfkE7COYKcK9IR1Q'
        b'ySmjzoGwzAG5BgOlgwjpbldpXxIMMpQl3Y2Jj3y6yQj4PUVLAot+ooy7YjfMhYIJsCS5Ujz8FaZcnUYbHlMw/pzlvEKf8tJVedmYrhvD5nG2Yso6irMly/ILaMJugqE3'
        b'SSKtDGQIBa8tS96GmY3Yj2RBWUATqGKOI6l8gYY3Lxd9lyOTKtQ56DtBPpJ8YZ5SqtTT/prl2zVOxKXNi26LnCo7dp3YXpeI6wUZd2896DTjLu7sl2bcfT7hbjtyXbMp'
        b'BF6ScNfgoujkwJnVO5AC/WxJhlyxJDs/S+JtTpRgcUYWajKD5C/vmP+3Y/pfM1S/L9Ajz6X/ReORpnqOmJgizpakY6559NEwe7b7cJO81JSvzqwUxqKTvnUbYdAVZoRn'
        b'BUH3xHPIhy0RDZvPMWGJfLiTRMNmK9WTD/8NomHtfU+7nW6JFVL2gvk/74JplQWb35vdEitlmQoV6mGkpJAuI8PJS6xmL5s6F+fZfik+3y70ecppGxHh853DyfNq8yxg'
        b'1Dj4BjZ4wTKzxLt6S9+Ay9d7NLKPQ4Uif0CXr7t17c64MYw4VKQcmxhayKhx1HjIXD/TGgfON66TkNcYJol9NV8I9/SGFaTWyzwHwhD8ut0yrwmvTKIkvMhs3oYz4XTA'
        b'EUxivvF6x8Yh2njsVrDGHq/kvUYqrnaj7DP5kXNjz9t1Y0jOYuTsDzNbbbQnqvoiaDII714Bq22RR98whFRXN9KWUA6vWJAfmxftReUcD/fONM8VrPfviJSgHJbrxTxl'
        b'DxqRg0MfTN2ebsc4I0vq9WiZ0HryaBqKPm15lrl63bS+DD31GtCmrfQMOGQP1yxwUqhGD+aq1qEqNue/7f3uWQdumDBy8pK/Ut1KJnwvsRc3r1/wjqi7L384r/cu57lf'
        b'VwY0qH9u8d60bvTCwLb13Wv7bX7ofSOhy2cf/uedQK/WW58JxsCaLySTrpW1Vd+MGNmrcrf7zTcXPhWNPZtZWHrxq/dCYEXRa4+SHztttvu3z78vXQkcH7Dw8GPm2RvV'
        b'8LRk94ma2c+syoMk9dDdjjqOpaCyB3Ze+8F6E99yPtxHvM+IAeA8fuoNdtmb0g03jqMhvesTgnWkxaBhCjvCrBhXuIUPj6lAC22rAhzOB2vzuKZ+KnJSUxPposSpRQot'
        b'pTAXNhE4PDidQRxYf9AyAKxNhoe0/jPyngfSlQSwAVTkIY+sGqzT+YTIIQQ7YSt1Kpt7wTVgrQoeM3XzkY8PXoUbyYnGuQUhL64swtg9Ra4pWA9LiO8YGuZNn1h4wxZ4'
        b'SkWeWKCtWGLMwuou3tZMHFhlA3YOAKf+Meteh9HEuSIMXLkiZgLhDuZY63mEKacwSc+q29KS8yKrwwKr8EVcvI6LN3ABcAFx8SYuLjHM85l1BJ2pxMHonNyRqiSgIgNf'
        b'bwVzvYO8du3P40UwhXZpOgvKIvJuKpKJ4jr1bRnQC+OvOqAX7jy0M1PL9mpgTlkUarpWqKf9TSQgxsFLk/qyppPFdmfp2nWl7f49WmO2YX4aMpgstpmqa7MPbdPAqHrZ'
        b'9pBdZLE9ia49N73lJDHFz744dXKWtpe1topFCaQ6CXrjZxkG5sxLt6nzhiy1mWnUJuplnRFk0KY7l0KxyYMRXcBtfAbPQBQc0Y7vZRJxG48KsjyFU1RwWR/WjqQ3FsqF'
        b'uvh2q07Ft/PIjct/bOXUaZ4pGSbb7CzNFNn5RVimDFml2lWJWaZ0SGkPL7GHIWQbbRMUONrJkCOHGLlUDEw90nlHUNfQaHFyXg52J6j/jVPIsbhrSXqeuoAlb1Ihw9VS'
        b'3+B/mChFhrtEqpATGp0C1jA3Pim2v0m2TNRtmWyCPDM2Mf4XraN9knTk4/kFGng2Yjctt4xlH8ewX6n93u5mFbuFpStlGVm5mNaGdfhImjyzgurHgUqlyMwlQ4GSx7Rj'
        b'MFOJFYZnpUC+T6YFhhqtT+NHLnJgsM61wS35uXvhJyZaPmS8h44QOcOSN0ZGpYIcj4m0cN8FBXeeiEtufEL4rBUy1T9Ho+WGaaMI4ZW72MMjB/vb6HQWeXi8NLGW2I2Q'
        b'aHlTLqoXqboDEq1OHf+ilFZiC1RcliithndODCM4SIfEVm46Yis/d/EsvxGWiakMISXsZVTL6OkocomghMg+Ii5uxgx8Zuay5+J/+ZJFOST3rkyJpyovwlqnc5MNBBrR'
        b'sUAdsm0ZPzShd4uP9k4xKxY1iAw5ulDz/r6W6dYMATjaR0gGtwn6Ft2RuSoFFSpPbp69TDoXjQzSH/gAkoBYUog/d5K4Cf8LM6pERZ6eKTKyChSEnUul545rf89arNNb'
        b'7IeZsWVqpFx1FaARrBCzXYQ0VA664yKnek+RFKTL8BNJ81xi3mI0XGhO1Gx1zjxZlvn+9xb7m+xGWpOo5YvVBTI0c+Bk1OKUPKWKCGWhjpGjxWFqeZYsXY1vPXRAmLog'
        b'D89v8ywcEDBaHJ0rVSxQoMGcnY0OoAx3KpMzt3B0oDmRX7yDRpmrRmEgVs6LiRVkrr4X65dg0pH6rn9Oz5v9cgodyfjRoYncLzwSDU9frkRn44b7VieTJH2xOtPd8vAz'
        b'PFw8aojlAWi0o1+wpT3RMMv1aU8eSn8MMK0m0FI1gR1VgwaF7vw6qCPIcDeLpxZsVJmZ87I4obEAQaTh2E/EHkA2KdKtWlXulkznWIsTth5/iJnt0VRIt5CN4xaDNmW5'
        b'6A8NczGeg4IsE2rqkYvG1YwwqWZEh9UQkKMRw6IboVWMwPNNgMXDdKBIemjkVKKp8RdiN3STs0McXXbL3aBWYqZJNFuEs5+8xAa2XeTUJLHbNLgnS4luUiTLSMuiGOAx'
        b'9ZXpvmaF0lalmqdWqtoL1ZG5Z8m8JKZk5y0/nYkWZrQK0DkbhiBHR4vj8Zt41gjff3X+sBH0sBHkMMtXQwtJZU1Idhu7zx2NA4JXRYfgN7Rj+/0sa7EomVKZ6zNRKVGj'
        b'Inu4z0QFsu4say2yu2VdheuxrJ9wA5YVVEctI60UmYWMMKT7LasmIhuy2aTmxbDUeciKlckKsGWB35GBFdihfZeeVzhajBeVkf0kx1Yr+gL1ueWLig/CcGF6lCRbjDc6'
        b'PCJDUYBvSFR2aO5RlDTek34gFXthO93b3y8wEI00yzJheDISCL91OCLlEnS2E5FS6WgnAnBGVwi/iWcFWt6RVXNaEtkORrQWej1aPAF9opbwrBGjOtxfd2uTQ4xX+Trs'
        b'by2gmz2SXh/LyhoDuZGJNiEsHl0eyxoxXZGBKowOR02buSPbQbDxer5ZnqsDE3FWsi05tswcr9+D+jAUal0DjnSPAcdnmkLmYP0YchRnEubBYvz4oXNimcShLCZwW1B4'
        b'DKgDp/VAPlC7jMZHh7kwXsycRAfxnLGXhbYUR5kA1oEdGN43HJQSNo/t8CINbd0BmpOS4Xo9VppFSteDJlLdnzyczjMql+8rmXUuYxqjxiGSQ+H5TE+0M6ZQTMDxhOBw'
        b'qsukOJpZicHgiCSmcKRt5uDJBEqU3p8mUWqKPuL65vTW2aF0QRDsHpHZLolSQhA8nUzqiSKrF95GpJGVYKvQHW4DqxVvfOnMU+GUoH+c61tZdXESTyJ6M/O3s88U3utO'
        b'ytY7b1rEjbEq+VP5luCVoOpQsLO0rElRXL0+qj5+qeCizxNuytmf3v1jwbpDEW2NFe/0ftz44F7SjapNW7JGru5+/urCb71aClvdRv5V5+f44Z23U38TPOllrX7H8dOT'
        b'+zJn3lPsldd/66jse+Lw/G1P/phj3xi5t1J599rHD2Un5H/OU1xbPPeBx+OD5WrnHV94lnzzwc0n7y35vejmJ8rVwa9Frxp6/Q/RTtEX9n1OOjmpxv6nfue5mKlCVYX7'
        b'2O92/Or9iZPPhQflS0bk53K/W7v9i2cbnLu87VL0XcqkAYFp7gI2Ti8KHsMAEnDcV48hATvhCpKglLMwGRxaDMv1AJJouJqsUkWBTRg2Xp4whhMNDvMZ62zuwIR4ih/Z'
        b'IoIb7FXO7bkV+8OjBZhxdDo869t+gWl8kHaJSbe+BItBG1nZUsO1avsFM00SN2mTNoEqhgR4DoZVc1VLwT4D4kI9aeFpeJacE9zTFayMAevg4dhoDsNN4nj0AI3t4R/C'
        b'fyjzOQ6DI8taOOGR0bJWEZMgINyDfI4jZzBJ4YQ/4zhDO3ZJi8vpTfgI8buIs1ioW6yRSKXxRplA9I+wcRi3wTqW7QsJ7s43qESfoVR3JnPNLmZtGWh5MctIZsu4D5IO'
        b'CgcpMWV8XTqoFyFpykSiz0eVGOlPfErteQKHUP3JnchnBvs6kwRtIDeWTRzTCjaEq9STA3zH9oSVfAaNLs4yUCfTw0KKwFZQbc/D8bCHhjDTMLcchcOuBo3JyQG+6Cie'
        b'D8OBZxl4Ygmbk2Gf51LOAfUTnC2jT0vcYqpElXaw2h8cgMdHaiEch70obuCIx1B/sM1hJAv5WAr3k1oiB9kwrzv3x3kYssN4dhSFsV3YlWnynoDTPWSX2UhobL/NdBHj'
        b'Fv4K/tIrfGIG3dNhrJBxlgYyTOIcr2KbsXTP+nwhs04QQL68PoRNbbmlmx0jnu6D0Z+x4WIp3TNvtj2za6IX/tJLLA+jX86YYs14DXXFIgmvq4robAIugBZwLjkxMZFJ'
        b'msdwIhiwkgeqKGR8g0tff19fXxwivRN10h4GrgQrXqEduBK2gP3JiQymVNrHzIYb4MolcB0Bi3SBe0UsVuRQFwoXwViRc3AF6bG5GZP8WZjIAAzbhcd7EsQqKF3cjyTO'
        b'R6rkAjPAszv5NhHUDMFAnRE+8cwIeAhsp9iK046zCe7DG+yeyHjDzRNIy/4OQTqMB5LwDMZ5MODkBNBAxkuaAl5IThTzMJHIGqROu1uDBlANDpNkU6N8ArQwD9AapU2y'
        b'HwfrKQoDd/XBIgETOnkYSVOQOCac9urjYbbMrsAh5MumFD5F33btMQt1Ke7DEmZiksSdEmN9FefMZA1OxIN47Nt+CTTNhHVydHIi2OXOwIoEZvQye9gAmgbSPq5dPkXl'
        b'4O/Lhw1uqJcPMfA8PALKFNeTWrkqNFkz0453y9kQgoEepZmf2ZY/ci0LGvxH6Y6SmuL6HgfqnQVx3Htnjq+frVx147/i+ND3bA90zbsnmhzhOWPMq+ce3Ty3qC52U41C'
        b'kvL11Ssbz/1wQy23ax76+eZLQ2/FKUvjB689PP+tltXNkz02p38auWa2Q8BVXrN86uU3ahddiMxYVi3v+rS/+P3KeeLfGuae6el9LCs89b0pUTMH96v5eVNEQ8zRPSEf'
        b'/zVeM9z9v3MSP9p5c8zqu10Gn33arfGxy6Gqu19/eLeqqPZZ049T+97+WOJ6/mPJh4em1e4v9kuKLayqWPPMK0C4ZWVoyY/jit1Xb/HOTL0hupx6/rVspx2t274JSb4y'
        b'+4eaGQ9kwD3+oDolbuWjkDZ+2qB3Y9JUD09MKvzv+emBz+q8RsFKr1aHtg2/33JxSSm4Zcdxdy7wZTCf/BpYAtaCU+CEpZAJ/XzWAPbTeXc3LAdbPMkUWQQb0Q4CeJYL'
        b'NvjbkzlqYK4cGUOxHFABdjH8ARywcySooUH/bWAz2EAzDYKKqTFsosEQZ/LrAFjip0OHgLPgLEWixjhT8t8jryw3Sn3AYjfEkVb/AkdtwTFwmrRe6AIOUPhG+FI2ACVv'
        b'Oak/1RMe08I3QGk/mrkUDaGzJPAlH55Dc7E2QMYbiXFmARtkA48MJ4CGQnACHtAjTDwWYIzJwL5ySlW2Yo6XFt0xFXWjYeAMPBFFZLOyR/cSIey0jaYWSQ94nOAXXO1h'
        b'eQyBZUTC17TwDkdQwpvgvJQCHNaBzahOjA6Nh6WG2I6uwdRwqewHWmgVYOt4FtzhuIwXARvBJrrHSVg9jwI7rHsYxc5YgbUUkRvsqgVsxIPtND5nAjxPLvoA8Goui9cA'
        b'ZSO1dBVwPTxGTn8gaJFqATqwZrRR8I4HbCQhSLAyKd+wh/XxR2OQRj0GVoy1ELjynDSDhB+GmCmL25sp+XyWIJmLjBMRV0Di4UUshhVDKkQEVMFF73YGJJMi9o+8vrXu'
        b'w/1G0NcOGQl8Fm4hYuPqub9b23KfcNGfwI5lSCPmQnsSNvMnYULHhi0UD1MLZQVT31HmQtNGlSpsSVhMWzyB+Qc42eTodNSmBot5QjKbeDXOKw1XzXdsR0hGOZ6ywHYt'
        b'IRl4bTaZmbgCZwN+MVfYxAHFYD14lU52q2LlnjbgcAhhF4N74RaKKd0PNnXLHOeppReTwaOK72vO8FUYx7H6j6iQyjF23DDh6mdS+aePp86YMXPmD/3etHdbs+vGHMmA'
        b'73ODP2nt8cbE+3x/l4ex8pT1I9Nqng34dl1Uerep/u+8uzVP5ffRHwdOVfU+U+vcHCUQ9Rlj23x3+sWTBz7vFZbBXfRmKrC7/M5Kns1t903156NjW3PVd4eJhu8/lfnh'
        b'gnEnM7eU3194rCj3Vsoop7vBzS0OF/e9sbjP5W0Hnvbrezg+Y+Sf5yMez8haXB/y8JKk5OEDq+Jbh4qDpL98pGUX2xAs0bGLeUzlgKO+SygSqQpunkLpxUaA1ZRhDNOL'
        b'9YEXyf0Ma23gLvI7yxwGD03pKxxEw/GqY9yxNnSL1ZKHUeawQFhLFE5U6mTMTLYAVmrJyVhispOwjNJ0nS4AVTFe8FSBjl+MkIuBEriWUpft7m+PW9BSi4Hifh5wHyyl'
        b'KLNKsAPnOakEe2Ybps/lZcLT8AiRvgusYwxZHWVw2yDYkEq0UZzdME8fsBfWaRnGWHqxBD9yaCaawDDzr5ZaDO6AR1zEi4lYiix4mpKLgVVRhF8Mk4uFepI5oic4ihMu'
        b'wEodr5ivZ0+knCpIn4WBLUivGQAYA0Ajxi+WojmEJvCaC894+uiZxbqCWq+wZf8ItxjhvyJKzqO9kitivAd2TC+G9YOeXky5kOkY8VVo1Kwr+k7l1V4trWBuP5dQTNsw'
        b'UhjGuA+KAuOSt3h3J1Pk1yKGMYR/dSJysY0h+cELZDkqit8yoQ3r+rec4k5cofOoGIA1eApDeMKsRRwhYfXq4f6yLGFCPNU846NaxAudxgg4BLpd2BfWqXTWmhXj0Jvb'
        b'LwfZ+efAOndOvCL4lSq+qg8yhz2vTYusaqO4588XfD2o7N7va1RfjeVWh17mJTL/qkjLHbiXmbZm5OG9zYvmyiutNPLvtj/b8sv9219+t2yO89VLi4qai76vkC54q+2v'
        b'nbdmfvb5/XcPzPshYdQVwaOar8ZPH3pm7aMFud0HP4oJ+UR96O0Lf12du2rijKeTPr+/fFJPbv38Nz1TVe+65wXdLq6eParrQK/RRff7R/9Wfn/H+beg06H3L//7+z7v'
        b'fHt08vRBPZyKauZbBzTzDzYVSK/+Ulrzq1t9i4/iSrP31qfKm8pLY8Y1Xb48FFpvLfRvrDzjfufP3bvCbr++4U4Pt7Nz8ockxLz/7L3gzT9VjAE9NrZ6Ntpk/nSy8v2r'
        b'W2M1E4bkXD2V3HfpXKefmlw+WJ59ddcwuzOuvRbJh7T+5c4roBnQJOA0XCsBjchW4QQhhQrOeFD9tC8FbjLIIzIFXNA+CEoDJYSoBjlf9aBGn48bWZcNxo92YH1k+2cz'
        b'ff7fDMMXLpDq4WlvQ7MFAakK0tKy8yTStDSieoZjHdCby+VyRnL6P+MiJWPNceIKeoude3s4j3cexuWMxsporIDnaD+0iFnA5Sg/191/PA03Lc3g4U7v/wN9wFFe092+'
        b'WFKsf1R4dmO+D+2Y0QycnyvA0exoKihPiAXloNoGvJrKOPbi9QMrlysOJS61UlVj1ebV2K882BH4Ols9e/KzKDQquyI0PdhpWtOEjIV10WW//n5aMGpI67ZecV9HbJ3Y'
        b'O+vrzU8fvs1LGH3wevfkp2mDLnw8acvBFs/UA+Nqw8vTY0TTvvh2n1fExpTWU1euHHeC/Dvh3PCwQWBXmL19WUDgtfSyEMeg3SWXbTP5s/MvOTy5EDOudKHoz4+6VHzg'
        b'Kkh2u57kikwKLH2CGtTguTkBP7FGrlQddqXswXEuPADX5BJ3IWlmTkyCN2xGY3stPJOQgGfxrvAcDzSI0Q1AKELrBo2lXYAteew12sCGvoyjE6+/ZBo1AbZlwf0xcBXY'
        b'GB3nEWfDWPO5AmSmlVPr5ATyBovhWh9ruAFWM5xkBrkqtUKSpjhQAHZ4TrKKBi0MJwbToja7UKNj+0TQRHjx8A23Dl6YjKwOdy5yQ9YVUvxCCar2pEq/R7kdh7GL5oIm'
        b'uBVeILZD0RxlDNGexImCx8IZR1jBi18GW6lYO0Et3Ir3sBLC3ex6wvHp5Izz4HZYR8xS+kB+PNhvxQi7cVGbJ0ZTvXEQ7o5FjlCFVz4FHKzEjOJ2oIULTsSrqCd7DpyM'
        b'QLscF4I1C+Ea/nw1bJkvnK/mMC6wmgfWwdNjiJzegmExJJcCOZm2oQy6QNu4cHd3FVE/KbANHsbd7xPj7QEueOAThtX4Cxumz2A+6oitsM4okXK///83nOn9Z/scHWRG'
        b'JemxFgSD7iCguYUIgwD264S8cabG0WBqSBAt5KrhZctyNXwczquxKlDnZ8s0/GyFqkDDx86Thp+Xj37mqQqUGitCNK/hp+flZWt4itwCjZUcKUP0psSr/5iLJF9doOFl'
        b'ZCk1vDylVGMtV2QXyNBGjiRfw1usyNdYSVQZCoWGlyUrRLug6u0UKi2qVGOdr07PVmRobCjwVqWxV2Up5AVpMqUyT6lxyJcoVbI0hSoPByhqHNS5GVkSRa5MmiYrzNDY'
        b'pqWpZEj6tDSNNQ3oM0iPz6VX+1f8+T4u7uLiFi6+wsW3uLiBi+9xgblNlT/h4htcfI2Ln3FxHRdf4uIHXNzDxU1c4LUm5UNc/IKLO7h4gIv/wcUXuNDg4hEuHuPiR6PL'
        b'Z6dTs79HWFSzZM+nAjmO4c3IGq4RpaWxn9kp6WlvdlucL8mYJ8mUsWBmiVQmjXcXEBMSU9FKsrNZKlpiZGrsUP8rC1SY3FtjnZ2XIclWaYRJOJwwRxaJ+175RNuLJoH5'
        b'GsHYnDypOluGAe/0DPg2SKeZDrhRzgSA/7+5hca5'
    ))))
