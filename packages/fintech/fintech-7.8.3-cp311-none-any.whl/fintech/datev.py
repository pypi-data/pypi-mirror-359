
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
        b'eJzsvQlc00feP/7NyX0m3IJf5AyQcN9eiCI3KngUbTGQANEQMAkeWK03AS9UrFGx4o1n8WhFa6ud6e623e2WuGnN0u2u2+0ebffZpVu72+2zx39mvklISLB2t8/+n+f1'
        b'+oUwme9c3zk+M5/35zPXryibD8f8+8UOZByiZFQt1UTVsmSsbVQtW87p51JOPjL2WRZFXWRZntWeMg6bkvPOIvtFa6jVlMZzKRu582Vc+/BbWMjVRT4uFRYl41VTbk0i'
        b'/tcb3GcX1MxZRLe0ytqVcrq1kdY2y+l567TNrSq6SKHSyhua6TZpw0ppk1zi7l7TrNBYwsrkjQqVXEM3tqsatIpWlYaWqmR0g1Kq0cg17tpWukEtl2rlNPMCmVQrpeVr'
        b'G5qlqiY53ahQyjUS94ZJNmUNR/8euII+RkYn1cnqZHdyOrmdvE5+p0una6dbp3unR6dnp1end6dPp2+nX6d/p6BT2BnQGdgZ1BncGdIZ2hnWOekQpQvTBen8da46F52X'
        b'jqvz0bnrBDpPnZsuQEfpODpfnVDH03nrQnSBOg9dsI6vY+tYulDdJJ1fYzhqDtcN4WyqK8y+ijdEuFFs6tlwe1fkEmHvwqI2hm+MqKaiJvRbQ63lPEWtYbltE7ErG2wb'
        b'OxT9C3AF8M0UUk2J3CuVrujpLRcOxVU2IttyT337Uqo9BlmXwG5wF+6EXVXl86EO7q4Swd0lC+eJ+VTcnCbQzYV3C0C3iNWO063e8JQGDMAtJRVwD9xVAXexKPcSNhgs'
        b'chGx24NxuvAo3F1WklTCo7hcsBUcYIHjYA/oasdNtAFclWE/Drgqhl0oPo/yht2cSngRHkfxI1AQsB2+OgXshDtrYHdSG8rVLpSSO7jOBjeSwK32SBREJQhHAa55At2a'
        b'Ve3wOrgVu8pzVTuLCoJ7OWBXAtiN8joFhZsFD6rBTrA3uUycgHML98KTEdjBhQqLRnkr9W9g2VRbmKXaLiDjYGgnqjrUylzUxhRqWxdEB26IAjwQBXihVvdB7e+HqEOA'
        b'qCAAUUAQooAQ1PphukmNYaT1UZfpchnX+mzS+iyH1mc7tDBrI9vc+k79Jm79ICetH860/mcRfMqTonxTVv+Uz25aTBHHVBUiCfSbsprXwJ4pZRyhryvli9xSss6UDwXU'
        b'M479ZTwK/dIp/OyCw0HF1HlK6Y6c/xYXzH3kT80cFVTl/on9ciqVkEgp3ZDHjcV61qALCh9yRfr9tGORmxhnn7gvfHp9WPGj1N2yt4NvzvyAGqHaU5CHGh6BfajFdybP'
        b'j4+H3cnFYngTDiDiPF8TX1oB9yZJSsSlFSxK5eM2DRyG2+xaz8NS7G7ceh7m1uPZtRyF267Rw9o63P9867g4aR3PSjWu3vYAZEzZ8FT1AvEiNsXmUODuAngM7AW97agp'
        b'qNj69Go2hV4KbsPeqOL2diEm8QRwuxpeAYcWIK9mag68CV5px+kvWwq64QHEK5IpsHtuMtgLh0gEuBW+DA7AA6jqxBTYDzvFbE47JhkXcB7erq6YD3fzKPZ6lgAemgQ2'
        b'wQPtcTiSHvWaw7gvJpahbtQFt2WVz48H55OKySghged5YMsaFXlxE+wOBddR6aZSAXDfVPSK3YrPt8zmaYzIM3dR/NG3px3b3HXiwPUDK0OiOHAFvWOT5Ip/ztHNrKff'
        b'3x7553WeAk6huFDc4NXAWereELfYa6vXvLOdQc2hc70a4v6S1v+3FbH6PVN+Kjwb+n1eceOUme4ad48LnyZk9RybJ3inP/baqcNv+gh/e0U6uz1k2WK6JmhpXHWo4Eil'
        b'XJm3amh35navhdk/2xE74PWj5rNliSs3lbvUr9aGtQ1pQ4yTnq9c5HmolA09f1y4Kijf+yc/fn4w6vxH1JF3tv7Be97vTnZnpJ5tkyx/vdGn40cu6W1oDL20r1j0xSUR'
        b'7xHmOBlTwfNlcHci3F0hLk0qgbvBCzzKHw5xYOekqEd4bAG3wDlwKLFUDHUl5ZU8sF9MeYCrbHgsu/ARHjkzN5QnSkSlieaB0Qdu4viuaM33foSHRXgKDoZ64CpvR4NZ'
        b'dzLoW8am/OBtDri8FN59hAdXD7gNHEeN1I3GuV2oT+eywA00Ol6F1+FRkdcIO16kxnT0LxoaL2TQ9Kaxz9eBUxvVrR1yFeLChL9LEG+Wr54+4qWWq2RydZ1a3tCqlnXY'
        b'P7JxWk2I/L7aRI0+y6ICQ3tq9LH7lvUu0xV9OCmmv9EwSWycJB6lvL3msBhzn2sPqyfTJAjumWaip/QU6VP3lfSUmAIm99T28/o1hoBEY0DiKOXhN4dlomMHAl4MvxA+'
        b'qBmabRAVGEUFBrpgwihuJEpUP6d/zgn30+7jwg3wBtYMx2UbAnKMATmjlIt94Ad02n06bTB9iGOgpxrpqeNfojUEJBkDkkYpnjVeYX/hAO9E6enSEz6nfca/jDvQbPMy'
        b'DokUc877pPfAagOdZaSzLBF+HRo1HJ05xEV/C2953PEwRBcaQmcbQ2cPC2ebBIGHcvbn6IsMgiijIGrYM+oLPOqo8bAj8h7hM20w4lJXp25X1dWNeNTVNSjlUlV7G3L5'
        b'FwnDGxnL7ShD7Yc9/ZExrvFn4PB6ZHyFW389i8USjlLfhfHQO0in6Fq5a+Umj1E2jyU0efjrsrtyd+U+5PpsKttcsa1iU4XJ1cfkKtB5fDXKo3i+9q6bqpg/DWZQx9zS'
        b'qeveBSyO3chtxd31mMHwDlFyjLoR5paxajnon6ugannoly9j17rI3HRUI0vG3eZW60psvG2utYwbH9ncESti6diNHJkLevIgcJKLnlzRk6eMhTB1s8h9hL+AVFolab1P'
        b'/oH6TAPHJkNcCyvZiDPEYpDuIZwwRZLGXA6B/K5xIH8Dl3A5jgOX4zpwMs5GrpnLOfWzcrnG8VyO44TLcRkMsmQRBhGDZR4zl5ezXJSUQt70PFuDEWna7h8ffXvqsRMH'
        b'3v977k4WP++p6F/+PjiWPp77gt/3X+Sdl235PDAlfTkr0/OHmz5dDL88nbJoszZtymfl0gGpUj7LxLnBkRxy++jqPbm++438w0GD9dfPH3B7L7ao/9bry3902JuSLxeG'
        b'aqNFfDJcwysNaxPLxHAzPGXGhol8ygec5XSUgTNkOI4Idku0AkcO5ZkEB2dzXKJyH4Xg6Bfg1qVlcGc5QsrecFDEp1xBN3ttnpL4qmYsw8yyrARcpih+DhuN/FdD4Bk4'
        b'SHyLZsHzYGcVgsFcigf7WGAb2ANvg7sBjzDABi+CXVGJ4uKSJNDVgKCvK7zBRiGGwEURb+I+yLMMzqTrjbjW1SlUCm1dXYcPQ0MSiwMZftspZvjVsqmklEvThoKMiQUG'
        b'3/gebq+nfoVJGNxb9kAYc18Y07/CIEw1ClMHCwzCzB6WKWJK38qBKQOpA1P6WlFgD1P4ZPTjbhIEoU7oF4tiHirbX9bPNQhjjMKYYct3lIM8SQi1wDoY8Ue4GrmycYSL'
        b'BboRl9VytQbJfmqMgdSB1nJh+lm+HI8uzJiCYb1DmZbikGoyqpBxRcNmsSLxsDCx8V2NF19gkj7kJqYue+dzGtjOemeHtXcyfbORTXom2wn+5Lg5QZSOfRX1PvZGjrln'
        b'OvWz9sym8T3Tmi27ntkuQk9+WWCrB9yNKHcPguBwb3Uxou8poBOR+Px5BJPOgCf4flmRiqNVBzma2ShK7p7mo29noC574kAq6rJvB+/cVqr/5bIdwu9X7kjI4u+Q7/L0'
        b'vBgiPVmxa+a08pSfs6O/dB1+0aXrbJx+c7oX9ZXB4/D3aRGXoKMy0LXe3KHMvQluB9vXwjOg5xFudXAoBx5CUKYLoZu9EnEbQUFsLbxChW7kgu2gaxrpta35Ytu+Ba9s'
        b'gLfhXXjiEQa/ebAHHi+rErMosGclezWrAFxYJGLbdCPcgJY+hFhjk1yr0MpbUDfyt5Kc1Y30pHxzT5rNoYTBem3f+mFBAvp+GBozHJs3VGOILTCEzjKGzhoWzjIFhfV2'
        b'HNq4f2O/zBCUaAxKHPZNtOkPPHUUfitXJW2Rj+8FPNILrJ1AjDuBkxzhhtYomX6A8lTIYbGCMbU7Nb7THnDQLZG66J3L+b/CnyboBbhiwbkCcNehG9j0ASQK9eJ+AF+F'
        b'dxUfxhaxSE8AFX0M8/rGnnCs/PKymU+Xp2yM2+pVLC5M4TSFUr+XuL/bahJxHmFJzG+B1KYjBIowY5GDQ49o5LewiGfTByLgWaYbMH0gEr5AWMhUcAIOoF4Az6SOdYTb'
        b'oAveEXHGMw4Oofgxktc4IXmNHcnnmkm+8glIPgrzFHd9hsGXHiZfWwZACF4twS/mrZYq2x3Ifvzgn2lP99ZsNVP2438FIvzJmMgnNr4r6lfHotc6H/cJ1XOs4z7WRFCN'
        b'3P/g2O9A9TwnVM9jqB7eSgRDWDNXA3VisWR+8fqY0oVQV1XNSPnFsKtcwqK08FU3vie3PQG3BtiWOFE3gZfBJgu7aHxG8fn2d9gaBYrT+9M1R99OI+L/rQNXDyhCBIwC'
        b'oP4f/kX8nGLpMv7Hl3fszEhdnXY75Y23308zpmivyV7/3g9xZ1qy71Hqeyk1VyN6U1P6P/vDPs6n9Ts+DxpMWc461rw6Le10Cje97SyHEj0n3C1SIJmcCM3H4XFw1kZq'
        b'ZlP+VYzQDPZ4kc72VHqTubNlAr0FxsUGE5aTgKTnk0x3A92ID46xHaa/8Z5iEFt/Lrhgw3SeATdxdzsBDhK4Fw9uNjJ4bjc8ZgV0dbD7G/GcVZQa4be3Ydm6w8tM/Mwj'
        b'6Y4bzN1xCYcKntLT0R89wDUEiY1BYgy4ClgfYmFxhiF0pjF05rBwpmkSPUqx/eayGLNnNuJK/Rmn84eDJOj7YYRoOGH6PaEhYY4hosgYUTQcXDSK0k1+6CvsdX/gG3nf'
        b'N7I/2uAbZ/SNG7Z8bbq0C9Olo7Fh35dtiuZCmZmZRU6cjru1fclacMDVlIWTLX4sJ/vueRrTq221i/ZojkO0i0QzbOZjWJvI+R/XJjY/CR/jVCr6TgyyNXhUrP2jAHOl'
        b'yO2Rx/ahTnfmgHgn66Md/OdT01IuNW77/MKSkOAVIZv+1LaPV+655F4a/YzXb2+lvHHhDeq999LeT4s8+uqmkKM/Dy2qyV95eKV+RfAKfcum30cs7P/vJSuHlwX86B4S'
        b'qi6FCGsG/BGGwz0BnoNHRAvBLXsctxYMzCB9rYqzEOo32sGz2zJwleA2eIHlDm6iBHZi3ZmYT/GfYUetgD0k3TokIG0JQkDOVqgKAbdBDyK5J9BQYJKjaRv5yAVxD60a'
        b'MTnvMW6Cn0mPajX3qGYOFTZZH9gfhf5kp1capqQZp6QZQtJ6+KaouNN5D6LS70elG6IyjVGZuDfFEmNfWc9sfYwpeFKfx4Ng0f1g0UC0ITjZGJzcU2CiY6w6n6Dong39'
        b'iwxBScagpGHfJEe2OGH3IUzRpvfMwb1nXDGwfKdpo8xqlibUe/xx/5jY+M46TjIuArtSjQc+kReWQzGerasbca+rY6b7kN2zrm5Vu1TJ+DAAwLUB9fqmVvW6EVezJKhR'
        b'x5CRr1EhV8o0RPAjwJegADJmkKJ/0yBqo4/CZNZh1qlUY/83mIa2/D0UBOnweKgrNgWFICMwVDfXFBCkKxrl8r1Q605k+HK8kkYpJ4Y7x0uEbQ6GO98rHsd9jOHL80Ij'
        b'+JMZhHraMbHMbYJbPUor4J7qyORSFuXqyV4OD0ocQAD+fLEcj2SscWosdi1XxpFxZbw+di2PTfVSMn4/n3LykbnYTwXbP9W6yFyrKbdtIrcR/hwVgmnrvhbOltcrtK1q'
        b'uSq5TC2XMdZPfAm9fILHsa/9F8nVHe1NmjZpu6ahWaqU0+nIC+f3a89yubZDK6eL1AqN9jybkNcn30e99cvD/kh0bFVpW/MrETnR8QUytVyjQcSk0q5roxeqtHK1St7c'
        b'IleJ8m0eNE3yJmRqpSqZ03gqqRbeUSsl9DxEjK0o7qJWtepJwjlLbKVcoZLTBaomab1clG/nl1/Wru6ol3fIFQ3NqnZVU/6cheJynCn0u7BaKy6RVaol+QUqVGHy/BqE'
        b'dpXJBSulMgk9Vy2VoaTkSg3GwEryXpVmdasapdxheYdam1+tVUvhcXn+vFaNtlHa0EwsSrlC2yFtVuZXoRDkdajmNei3o90muuWhfg3OHdbi0uaMICcJXduuQS9W2mSe'
        b'Tp3QJy2/TK5SdUjoslY1SrutFaWm6pCS98jN75PTc+EdpVbRRK9uVTm41Ss0+TVypbwR+c2SIxF5JU433uwksvjRc+WIduDpRq0GlxJXqWNoem65KH+OuEKqUNr6Mi6i'
        b'/BKGTrS2fhY3UX6RdK2tB3oU5Vej4QplUm7rYXET5c+SqlZaqhzVEX60rzXsshLTsLiyvQUlgJzK4WmsNl+Ja42pfuRYMqugEvvJ5epGNCgia/XikqIacWErahtz5ZO+'
        b'oFA1I1rD6ZirvVja3qYV4/eg0bVeYn6n2W5X787ccd3bFSLNoRBpjoVIc1aINKYQaWOFSLMtRJqTQqRNVIg0m8ymTVCItIkLke5QiHTHQqQ7K0Q6U4j0sUKk2xYi3Ukh'
        b'0icqRLpNZtMnKET6xIXIcChEhmMhMpwVIoMpRMZYITJsC5HhpBAZExUiwyazGRMUImPiQmQ6FCLTsRCZzgqRyRQic6wQmbaFyHRSiMyJCpFpk9nMCQqRaVeIsY6I+pNa'
        b'IW+UMuPjXHU7PN7Yqm5BA3NZOx7qVKQMaDSWt6NhxPzQpkYDMhr9VJo2tbyhuQ2N1yrkjsZirVquxSGQf71cqq5HFYUeZyswNJKLGXZX0K7BDKUDwaP8xfB0sxrVm0ZD'
        b'XoBHPYbHKhUtCi0db2a9ovxaVN04XD3yVDXhcEXwtFKpaEI8SksrVHSNFPFFmwjVpA2wzzwy1Wub2BgbF9eiXKABIx5Ht/Mwx0deMY4R0iaOkOY0Qjo9S92uRd6O8Yh/'
        b'xsQJZjhNMHPiCJkkQoWU4cukzhEuQfiEuGnla7VWCxqJrNZ026AaazCmIWbJETtusnGIya9VqFBr4PYn78FeHcgJs140Sts9ptk/ouFHqtEibqdWNGox1TRKm1H+USCV'
        b'TIoyo6pHZGttca0anm5CRFSikilWS+gihn/YPqXZPaXbPWXYPWXaPWXZPWXbPeXYPeXavz3F/tE+N6n22Um1z0+qfYZSM53AFDp+gblWNWagIRoDRs48zVjJmZcFPk3k'
        b'Zx3KnPhXOX8bxl3O3O2g2MRleIz/ROjs2wROm/jNdjjtSYKhodJZMDsWkOXAArIcWUCWMxaQxbCArLHROMuWBWQ5YQFZE7GALJuhPmsCFpA1MR/LdihEtmMhsp0VIpsp'
        b'RPZYIbJtC5HtpBDZExUi2yaz2RMUInviQuQ4FCLHsRA5zgqRwxQiZ6wQObaFyHFSiJyJCpFjk9mcCQqRM3Ehch0KketYiFxnhchlCpE7Vohc20LkOilE7kSFyLXJbO4E'
        b'hciduBBogHSQFVKcCAspTqWFFLO4kGIDU1LsBIYUZxJDyoQiQ4qtbJAykdCQYlcecxaL1PIWmWYdGmVa0LitaVWuRkgiv3rOvAIx4VZajVreiJigCvM8p85pzp3TnTtn'
        b'OHfOdO6c5dw527lzjnPn3AmKk4IH9JUqeKetUSvX0FXzqqrNAA4zc02bHMnDDJgcY+Y2rhb2beM0V14P72BOPw42NDHuZtRgeUqze0rPn2dWrthEdlC7pDo6pTk6ITFH'
        b'iYViqRbjUrq6HSUnbZEjNirVtmswrGVKQ7dIVe2IvdBNcoZMETt0pgYQ2URRYOaukJFo3xjYSfpOmJLztB0DEhXTWO3QCHzTZshLqrIR+5srmbGn2dixTDimqfqalV95'
        b'3lVdhLWPc7FRTJlnPNUl2CjFGk6epk2p0KrLsCaMxSgusR7NrLSsIEpLRoeGp3o0C8crLUVYaRmiKx7lU4HJpoD4URdusPcohQzk5k4FhvUsHOWm+BWy/lLPonyE3fKe'
        b'wq4Vu1Z83sRKDwx9RCFDV4T/GC0i1qxVsuEeDV7K2gX74K0kcJ5LuWaxN9Lr/n9TJDaL3EbcCxoaWttRRaiaRrxnIWpjBB5pm1z5SQCjRsQK9K9DZyP6a0GgBivEaUbk'
        b'Qr1HgcY8FASv7xvhYvClrkHWL+8gh4UtDJZqbVbJ6epWpTK5GA2GKnFZB1btjD2ODa/5i8tqaSYaVuHhgVuj0LQzDtjP9pnp7nOxxpERLZgXzVoorm5oVsI7iOyUCA7Z'
        b'PubPkivlTTJcEMZq1veM2dPMolm+pSaIqIGxqNw8qljkRZrBY2apc0w/ZpY3iZSAJU0UGPVrLZFIzCmQ1ykVKACxKVSNrbSYLlBrLVkxu5SocMxxjjhYmrNgaQ7B0p0F'
        b'S3cIluEsWIZDsExnwTIdgmU5C5blECzbWbBsh2A5zoIheFNVXZOKHMqYhsEwW04c0xwc0QNdIUdDtUUJTLdL6DElMHJkaNmilZXQWFSwCPyMtnesGenyxPL8onbVSrKj'
        b'Sq5uQmNjBx7PsPushXRGLsPhGy1BsDbambuZbhgvJwnm1xJJBBdc3SLFnlYSceZjJZWJoqU9LppzT4aEHhPNuSdDUo+J5tyTIbHHRHPuyZDcY6I592RI8DHRnHsyJPmY'
        b'aM49cbTcx0Vz7kmaO+Wx7e3cl0R8PKFMTCmpjyWVCXxJxMcSywS+JOJjyWUCXxLxsQQzgS+J+FiSmcCXRHws0UzgSyI+lmwm8CURH0s4E/iSHv9YykG+1Vp4p2ElYl1r'
        b'EPPVEky8Rq7QyPOLEIsfG/3QcChVKaVYralZIW1Wo1Sb5CiESo7x2Jie08w58YBX0N6INXLWQc7CS5EXHnnHGDIdX6DqYLA4nkpEg3GFQotYo1yGEIhUO8573DjsGHls'
        b'JB/vp1bClzVmmGDnU0wmlhq1CJVYJTrCScQE7zgVP8wlNXNzxPoRp8HovZHg9hbM4LVyBaoWrVVFXYJAtlbRqFgptR39a4kEalVd28IMRm61mcK0hUlFckaokSvqsVc5'
        b'ajU8J6dhkM3EQM1WLY3yjd4sVba3rJQ3W3TohAkSFLcYA1b1EufoGa8M77ABjnew/4LxCDrKBkFnmwJopwg62G/qX9Js8XN2GIbPYfbweTIy4O5npZrySrgnmWBoAbgD'
        b'd5W5UAH1XE+8mcAORHtaQHQsG4FooT2IRrCZ3+vR6yFj9wp6BRhOX+KdRRj3oosluhv6k0XreDovnaCRI/PY5ma/fqiWizd5yzy3UTKvS95n0TsuWtcq1vKJnw/y83Xw'
        b'cyF+fsjP38HPlfgJkJ/Qwc+N+AUgv0AHP3fiF4T8gh38PIhfCPILdfDzxOVrZMvCtrnWepnrRDDuz+3SpLPuKJa7Xc3E6NjmuuHKwh3qxttSv73uvaxGXMcuxLSkGHEW'
        b'yQYX3cZSlMXqmJWceAewL0rVRTbZIVUfWRwKxdO5kp3C/iQUvc2t1he5+aFSRKJS+JE3Cy5NsRd2zLuNvXU+jTxZ1DbXcSn7m0Wh+BHX2XijXWH1oq+T3Wmbj8WZZsZR'
        b'Zg+9XYjzPPU83DFwH/gEy2PqZ7ANr+Em8pDI8xOcnU9w7X+C1waPBVc3WYKr8dIy9XIcBNf3J3jr7SeYkkUuI+5S2Wo0NKvrFLIRtwY0QKq02OotZfpgnRIhXG3ziGtD'
        b'Oxo7VA3rRlzxHg6FVGle7+PRqECgtq4FjVvN5N0jnDkLFzALitR4DWmDKzX2wa8n69+epyyLbW03+5MtwCxEBFydC6pYZgMwv9GdLNlDZNzlPm7JnhtZsufqsGTPzWFZ'
        b'nutGN/OSPad+totwv8TbcO1aAX9KmGIrOuQaclSCte0UZF1Kg1ziEMXBIQ/JcNIWeqzK88yHJKBxGmvzzKcwmOteqtI6pIA/8bPQ8Kq1DO4iCV2A46OBuIEmy7Lp9jYa'
        b'saNsWqZoUmg1jvkyZ8Pa2s5zwXg7z4F1zuob8pD5TXmwJ7M8upz84izMTS63+JozpnGeF8y8MdtETFdC1zQjRop6k5zWtNcr5bImVJ4nSoVZEMRI/CglWoqSQM9M/mll'
        b'K2LqagldoqVb2pHcVy93morUXPh6uXaNHM/Z0/EyeaO0XakVkTMyciZuC3P3yqMLzTa6ASt9461TxTbKYtFEqVi6Zp6FWjXWxsRHcrSq6Xhm4dFKeEfdIVdOmJB5TV8e'
        b'EVkxvEPJMDRiHqni5U0SOjM1JYnOTk2ZMBmbsSGPLsIPNHnAyTUqVKjXoDzS6+RSlLEElXwNnrdenSXJkKQmiByr6hvXxnsyOxZ3x/pSNN4q0ba83Cs8nGrHu1jBbaiD'
        b'PXBnBbg0D+pK4O6yZNg1D6+YLy4XwZ1JlchzQAy64d7y+cXgcnFlRUVJBYuC+0C/Z+v6Z0jCGrknFUx9le02b3m5YWos1T4VOc4D/ZVOk0XYoascIQrQZZPmJF+S6rZ1'
        b'nhS4UUJSvRfgRvlSKdns5cs9G2aup9rxYuZ1TfmFUD+2gx8lIBEnlKL0wRUulbWMr4EH4CZyDAFJ5NNnXRA2iee708s9nxXVMmWGJxeBVxzzxga3qqpRbexCxcZZ3CVa'
        b'ZFNicEvtAa6BLaBbUbzhIEvTjxLaelO4e2++OzvVd2bTn96tXZvjM1gxUxvmV7U828X3g8sv/7QsT5S236ee3pbtVpDyx30PHvG7P26K39nj5iGif5Dvq5r6gfyZavC9'
        b'j7/Y+OwSv4IFX16M219/8w8/+/TcUp8Pz2o+e+/e8pY7f/njH/+W9PzP4p4LUN1ebdh65bPbf97x1ot/ePHl1hFQke/5z0mvrF7N/zzs7JLf7f/j2W7v+i2CN75wgZXp'
        b'ETf7RJ6PMJADF8FBsAvsTLbZBgp64nxiOI3gCDjIbEvTq8FrYGeVudFfATqm0VlUKNzK7ZgK95C9+fDqLNjtgapeVNEuTpjfTDYRBIBOrmuoH3kXvAgOh+I9O9ZW1qhJ'
        b'MoGRXI/oDY/w6k4a7FPBF7ISxfHFYjbFB0fY4lTQRbazCmLASyg2De/aNKs/uMKBO2dUMwusu9taEahOlIhgdxKFYl9ip8Ob8DVSCnhszRKwE+4F5xFdj7Ujn/JfzQGv'
        b'wnPg8iNMRQnp+CSIKgu2xZRoJgOKCstPgdv5kmXglUd4/T88SBXi4uxMSpDgcHA33JuIw4E9GlrD8wKn4C5mj8aumggcsK+SoGX8ZjF6LzjEgdtDFpDc1YDNlWOvheef'
        b'JUckIEgdCoa4YKcSnhG5/wv71jF4GL9nnewv9bPwYvtds17mQwtWu1CReF+TlylK3MM1+tImQWBPeo+mR6PP2/dc73MGQZxREDcQeV+QOCxI/DA0ejim2BBaYgwtGRaW'
        b'mKYkoqg+Y1Fy923s3WgQxBoFsQN+981bqVCUuYbQYmNo8bCw2BQpOhdxMsIQmWqMTEWRvZnIWms02zdlG0JzjKE5w8Ic05SEfslA/YPI7PuR2YbIXGNkrrPItu8sMoTO'
        b'NYbOHRbOfRiXiYsWbYpOxr+RpsgoEjkqhpTYYTOXF7NqHS+dV+OF5+pV2MB7stQabGBsp9ZSj1vYjs+XWG7+2Kxvn6BFPsFRBihmz9dX5o1fVS4sVgMLr2j/7szv9GSB'
        b'U2651C3vAheO3eYSloX3+BPe8yy1wupFAD+rUsQa8agbg3lI0sXVTSRdmlTT165TldKWepl0uk1dWZz8UDjy+k2UvsYYLt5EkZb72syCzela4Fo8Yu0ycatKuU50njXC'
        b'kbU2fIvMNjKZda+zgkHHvKo77ZvUkk0hCkJ2k+Js9tVZcjmZySWToJNMfovcNTG586mzh4lPnsUg+5pMteRR9Fic+e/l1q3OAuaePJ+hdlX5jCWbIbOkGrkVG/6L2Wq2'
        b'ZMuCDp88W+EoiLoXByDZiZoQVf5LGTPTnmudGW0+eb5o3KzW6nraUl1RE6LVf6fiPOtsYOyT5zEKN+kY6UmspPcNOHiCrFp3jq1FxkG2eUOb5XCC/8x2tifals2pVMR7'
        b'z+Jp8Kx54VAWPm5g84ulXZaN1patbP3XdpnkFzfl6Denh1Mlu1395KUi9iN8WpwUAZiXMcLA8CIInLRDGOA6uEbwylOgE5yxgoy78DYz/z2GMoLg3gmPCnCpwyNJXV2H'
        b'rw2fIi4EOODtspg9lbpRwWGI5Wf0TTcEJRiDEgaqB6oHhcbUAoN4llE8yxA0a9h3lsOZAM5YJnMkAGaTDNGcxkTj8PZYTNcrKfM+sBK3/8QWMDLs9LolUBe8czgi9xEX'
        b'82DI7PPia7RquVw74trWqtFiiXSE26DQrhtxYcKsG+GvlhKFkUcDkotbWxhFEkcrbRrhtaIhQt3gYUMv3hZ6wcU/yHV+1iMibC/z/mtXnY+OrXPHhK7z1XF0bjqXRm9C'
        b'8B6I4L3HEbwnIXgPB4L3dCBqj42eZoJ36menDPqQ50QZVCCTaZC0j0VWmbweD4Ho22Bek0zLyeqPJ9AHEW0FUTVI6eb2JrmNBgbVt0ZRr8QnZuL9dFiZopFrJXQVGhkc'
        b'0sFjcQuej1a0tLWqseLIEq1BqqLr5TgqLVOo5Q1a5Tq6fh2O4JCIdLVUoZTiVxLhHa9o10hwSRV4ZgGNT+YkzQoQnKZDGijpdo1C1URyZE2GTiCkkPAENVJkLm0z1oY6'
        b'5t0hfLxWqm5C75BZBnwcn8ZzJRqsTNCsase1W6+WNqyUazWivCfX0TG9II8usMMG9FKyOuTpiaLhN+fRZFfZ0m/cWzZhKkyny6OryS+91LzSecLwls6ZR+OZHtRURHe0'
        b'1Hal84RxcXfOowuRSS+tUmsnDsd0eBSUsZB3JNEl1VXi9NSsLHopnt2ZMDYzSuTRiwpqxCWz6aXmJRNPJy613Tk38cvHBhesIWMeaJyQ7X6NCaOj4QhVZjPqGqi7ahrU'
        b'ijatGSZgOsUHGpG+VaDUtCL6lcucKvcQOeHQmF8ryTm2pLEl9GxGw0e66JRqrbSlBe+IV02ZUNdHOgMiLJSBNnPXkinISbpSVK1rFAgXyNeiFjd3OMd08KeyVStnugnp'
        b'/HJtc6sMjSRN7S2I0FBepCtRB0SdRo5qp0FOtyKM5TQdpki40xDVpYYppkJjkyUJXYQGNcuA5DQV226HFZ2I1PE5wQ1KVGDmiGCN3HnM5eZTglsbSM6ZyeSpzVptmyYv'
        b'OXnNmjXMIYUSmTxZplLK17a2JDOSRbK0rS1ZgRp/raRZ26KMSrYkkZyakpKelpaaPDs1JyU1IyMlIyc9IzUlMzs9d/ryun9Brehf2U6jJ3h4GjikKReViiWVeM97Ijif'
        b'RFHR1eDVIF4zOCIkp2nCg6HwSjq26NNSqVR4De4i+rmDLVzKdVIZh5q53LNqUQrVno0cJ8FbrmUW5cx8qMNnUZaKF+BzaxbE41MsFkMd/kGYBuwHQ2vBi27wID+MnOu7'
        b'DOyPgtfhHqKlcaF48DAb6mM8n4ZHyBHBUA+2x8DrEny0Lz70AyWNEoevLRKzqcngDBfeLoMXiJKwCGwHe+H1MrirYiHsaSv3BkN2RZwHdZUo8q6yhW3IqCovhQe5FOwG'
        b'WzzgadDNI2cIV8Gr8z0kolJwBxx3p9xK2XBHOzy+YC7xhDuEjfD6MnCrBMVnURxwiAU2gf42cuRvDny11QPqkiWwC70vCZwvhbumNUAdi6Ln8rhwN7hITlmFuslgP7ye'
        b'DM5mJrAodjErqwBeIBX7grcL5Rn/ZxeKXp60R6SiyLHFafAUPKfxggfhS+Sl8GV4k3Jdxp4LtjeR16YuWYi9vbwkcB98qRxeTYTPJ8D9HCpoHQdcAqfgXTIzHAEvghse'
        b'EpQGqrwSpQzXCYcKgLe4PvAK3KKIm+7O0wAUMHo/aBkucwczPfkPZREbZtw79sL3lq7dvulkmOhKqcectn0c3QdXbn++/2xU+Krfzfxh9t/jQu43fcnmXcr59d88f3hE'
        b'eG+p+JWFHhF59M++1g6e/k3y+qvG7/9JeCmuN/RR+D9W3//gqDbxjzsPf6hUvX+Tl3bpg/hLr0atvPXOj2+uiu7u85//+5pu/7jE0mNp838jm32r+sPfD8X2f3Ri4/Xi'
        b'2o3VCa5bTqtL2udcWN8b8mj/bv6iRZ0/ePju7tVfLkuJZL/Ouv8Tl8PbUjwrkkV8ovdsL8HaUVsFqg84WB7DaWwEhwnuBnrYvbFsnEYxMo7RKSam8+De9QuJhnM12AvO'
        b'WjSoqrCEMQ2qCzhPgH4HesUrFqBvRvnwBuhlkH4E3ETOGWulOxIrxSUlFWXwVdCdBHeLWFQgvMNNm+TH6En3c8C5sqT4YkTqLMoVXGQHg1Pr8nki33/n9FSnCkhs2J2b'
        b'aT2fwl0qk9UxsK9DYEX1Y452+shydyqU1gf28/q1pzcYQjKNIZk9fJMgRJ9sxKq9NJMktadIP8MgTBzTOmbve7b3WYMg2iiI7tca4/KG5hvipt8XTB8WTCeawMJ7TYaY'
        b'CkNopTG0clhYaZoi6uH3rNnnYxJlIMtGg2+safqsHv5wUJ7BN98UnYAc1xmwmjAe2Vbv8zaJUi3h6Ghka9/nhXKET8jIMcVLBtSDrAH1JXzeaq5BGGMSpw8WDM4anHWp'
        b'FrlMNwgTTIEhw4Ei/bIejslX2Ov9wFd031c0EDWgNvimGX3THvjm3vfNHYo1+BYYfQuGLV8bycmPkZwwGmfWW5/DBtYXqs9jAx/xrcY4XX0JG5excWUCWcumxXDjLB/7'
        b'0GNH9KiHMAU6aysRFsIgZaOpNCsr3b57ZeX/uBITS18X3Aoo6nXKu8CbI3Ib8ZThxfFmeDvixQgtlke+tIX84kMe5SNu5nVJDfIRDwwxEbDHq5aZdrA2QYN1DQf6+Fr4'
        b'J27Jgy7OJLxD5FRvJM3haX4WOZfdTeeHpD18bjs5vb/Rl8h47k5kPA8i47k7yHgeDnKc+0YPs4zn1M/2xMUv97o8XsaTWhck0cy5uE8gyczB2w+Z0DSCU4i+kJCCIKLU'
        b'9l4EDCOT6CZ1a3sb8kXSk9QRnrS21CtUUgtgTUBYNoEgLQZoYS2cdb8FzqBVn+SQEtYv/T+h9P+yUGrbdfNwQzEuVv31Nwindn2dic84WRJwitCXfsNOiAlfx4wlzHvM'
        b'w4fZjRFyVK1YDaomYozKuXCyphVLEYoWqXICMWjpY/aCIOHS+W6QCXOMRz0mv/WtrStxfrGLhK4wU5eUPNOt9StQw9OtziUqRCBIKM7JSkk1q58xISCJHie3dGyfyISZ'
        b'sA66efRCTbtUqSQ9AxHO6lZFg7U3LrXZZvJYvYB50LZvBrL1fantVpRvlNxx9HHSu92Gh/8Fwvcs+Rp5k3m56v8TwP8XCODpWSlpOTkp6ekZ6ZnpWVmZqU4FcPx5vFTO'
        b'dyKV08xinxN+XKpnLYIdM5eX57aVU+34uDF4G2ydV1ZSAbuTSqzytY1YDc6WWCXr58CrbhlI6HmR3KoRtSwBXo9ZaCdXe87b0J6FUx1c6VImKa1AworzVG+Cw2MC+064'
        b'0w2cWytnVuLcXAnOaqqWBldUmY/gxMkvhj0o/F6oQ7K1O5JGUZro+Vb1MtAHjoBTbhS4CJ/3qPTikIt2NoK7kzWlcHdJRVUZ3CvAR3emcKngWRy4KxYcJXLv+oZnNAkb'
        b'6Aq4Jx4v85CUgMvxLGpyE4/HFxEdxgzQs94D3gR7FriifOyHp8SVSOZmU/7pHHACCerk9hBwFGxNhtdtlh6VJJUEgCHw0gJ8e0gq2Mlb+zTobyfHsp/JUJkztQ4eLUkS'
        b'4etIhPAUB74S5E0aaMZ8DnWvAk+ELU8SJjVQRE0CroJt4LAHas4auAPoqZoF8vY0nFzvc8EeuHZQLe6DN4vLUdLwAHwJayB2govoqRzuKcZC+LKQgFLXuSvnMMldAfvy'
        b'4HVkKwGXNlAlsKeGXMESVQfPYmVMaiwHZXvIh1HRnACvwqPMXStzQD+VPPVZ5Vf//Oc/N6fyqOA6hpIOaYqYdVUPvFyoZctQ3dLLk6Yl51Lts5BjIeiGJ3Dd7DYrboqT'
        b'FuF7mBTwUHLpQkQMxXBXdbwIkUSx9dolEXiZ1B5f5fW0fyI5/C09FZythgfTSyfVcCgWvETBS/D5VLKorAg87+4Bd5PWWTBGJa7jqiYSvoBrB1yB+7kU6Fzo9hQFL7Yn'
        b'ogRmLyoa03/Mhzc48fBgtauNumM/h5oRwPeGd1YQwgA3M6dpSsVVFcmYcCpLsKaDSuNQIqjngRtsFdE5hYBNAYn4tLrkUhG/Dj5PeYC7bEQo26vIPUGjMZXsN/jU2kGR'
        b'S+gHwenyN6j2ach5FdgO78DrZuUWszQO30nTlQ0PJldVzI83p2i7CA0eA+c8YY9iCaNB2j3dLRGegF2SkqQEFsUHe9nJ+NohohoKBy+BPWWIPl6djOR/tpqVEwp2iTjk'
        b'8py8BngwMSrPJtqSPEIDIf6gF8VZGmqOMh8lRpZ9vZaPb3wxF1EMj1iKeAWeUbxv8uZpNiDpMHdh1eUFZZUwxffL7K6f1B0JLBUpc4reW0qrUk4uSIwUJgQevC5t+rPO'
        b'a+eV27/cX96Xt3vrT6Uiw9HPj/4i7DnZ8W1+Ue/c25X9xrGoqI+P5l68FLzhb+oDEaKfD+/47VP6E6/P/MtXv+h2D/prZdZ5t5QDfzil+n1Y5vnYe4t1R1e8NaNGEOu2'
        b'qGzwyKULhz3nywyu8+9c0Gh+MKdO/emFpt63NrR0R3zdWfTXv/7i4Pxkjxd95HGfjm45JrqkH5HU/67lswS/R4b8gTtV/ju8P+i7evyXdPHDe282HRSmVdSVXL1kfP8R'
        b'vXX+4cm8X63TPLj11tZPqzK83hkK68tdMmPL+a7nvnjWo+m1wQvlHoqzzU/XlrV81Bi7Y9FHST87of7q9EmjZ13pisMHmtyvr77RuPfOx0caln367MC7hR+8/7epz4ku'
        b'qdlX/mGUvfZSrfDUh5fOvNW+/FfswN8mqX770i/+8Lcff3Q08Nyipe9v/OFbo+0XMjd/kPyMu/hvryXu+MVnJ6rYc9c09v+6h/vmtPmfTb7jtvELY7LIiyiqRGDnnHGK'
        b'qhg17OM0ws0Zj7AuIahNOV5NhZVUs2izmgpeiSLr2RbD06DXrKcCfRViG0VVDDxOTgRucgf7ymzW6fksEoPjHKX/HOYQ1X1i+EJiAjgILpjX6rk9xQZn4PlocogqfCWw'
        b'JRFce06CWUMSJsM9bPGq8kd4yUF7kn9ZOdgel8Cn2E+zsuHhBrJuEOxdWQIullckwcNqNsUtY4FrcFcoKTY4BQ+DQTQW7kBvsCzR4z/LjqsHu4l+bkoJ3At2Vqlgp+NS'
        b'PryOD16Ep0n9gKM5YKfNKr0rqfbz50vhBbLQMdWnQYM7phgzOVLRfrCH0wK7wCDYBC+RKogEW+CRsiTQzbdRw63Dh8CKAr5rLdzE6jk8GhDssGmTMx2dN1bxjEnyHUF2'
        b'up8xD6Kre5nN6Oo2elCh0frQ/jkDGZemGUJyjSG5WFdnUctNNQTFG4PiDQKRUSAamG1MmnEv0pBUeF9QOCwoJIq5gnvlhph5htD5xtD5w8L5pikSs2LOmsY0Q5DIGCQy'
        b'CBKMgoSBGqN45r1Ug3j2fcHsYcFsksase08bYhYYQquNodXDwmrT1BKsycsx+Oaa4rHaboPBN8ZG0ReXeHoDsj9r8I02CcJ78vSy/kKDIN4oiMdHTCebwuL10waEhjCJ'
        b'MUxCDpTGznNYzHLEoSj0J7sluiMyxNhcUxSXaE0xRF+wP68nz5Sd11M0HJZuEGYMCzMejj2Zwml9dX/g4aV9Sx+EJ98PTx7kGMIzjOEZPe6o0PqEYUE0+g4I0F/tA/G0'
        b'++JpQw3Meop7aUZxkUE01yia+2bkfVHZsKiMZKr8zQ5DzFOG0FpjaO2wsPbDnPyhuUNz7xW9uej1KsPUGuPUGkPOQmPOQlwrGQbfTKK5ZPlNNWXm40ylGoRpDyNjTof0'
        b'eJsEQb15/VwjnXpfkDosSDXFpA9KDTHZPZWmoFB8pnaEZJB7w21o+nBgaQ8HZzfaGJrAHJhviphijJAMaIwR6T1zUXCsle3PNYaJDUESY5BkMOZ+UPZwUPaHEXHD8eWG'
        b'iApjRMVwcMXDoDB9U38TinmfHNltSkzWu/S7GILjh4PjTSHh/S4DvNPe90MkwyESk0iM/HiHvb96GJ80WHOvfjiiBH3R25LSe2YbhdH91QahyOQbpHcz+k4xK1ljDb6p'
        b'Rt/UYcvXRqkqYJSqt7BxGxuvYAPvqVO/io3XKItS9Qn1qeN7HH7VeO2qVcH6LjIm7GS1WMn6Y8pOyYq62yp3FktBdKD/WfM71bdedCtgUa+zvAt8OA2WQzfwx3rj4X7K'
        b'Xjd6iNK56Nx0XHLnIVvnSa6X8tKxzDcf8thU17gtThv4RA/Kc9CD8h10nbyNfLMe1KnfxGeVOxO6vBmha9pC5grKngC5snBaGlXD3FbpwyXXTQ5vVCvdp8+l2jGLk7au'
        b'04Ddrqs4FMd7TTorZ0o92d+wAG5nV4PdNXD3wor5CMHuBxfnwZcWemWlpCBIF8QBmxGDuUBONwlL1FbD3TWZKbA7I6UG7kIvWcWC/aX1xLcgXGNJh0UhKNjNS2CBI0gE'
        b'IzjPSwEvg+vwti+533AqHIQvEWC4Cr42Cd7QwlPwDBroY6lgeLGSQE0WEo5ulElSMtIy2RQ8ks3fyAIvgLPRRAKDQ3ALPG+9EJDcBojkmJfhMdgDrio2/WINRxOJCPv9'
        b'Cz8+Vv2KCqZ4no4u2/j9vVcLN/257mvef/1sdzEVVLx5z+ZHLPZtmevtjj/tP570k/e7f10asWLT7nDfyjtRe69pJTNeb+Rse23fRx/1sLxfvhFwLf9m00/2CTqrvnr1'
        b'esW7fVv81LlwX9iq5swfhWz7jWfKLM3Sv9SPrP/7+cTMwlVJV7qnLVfXv1ES6x357sLkUyEB75y+6fnOU83B14YP90966+/fq3h4SgDn9Lz77PvX/+Bx1yfhnd988Yev'
        b'5v/9cumuP+24sfaDZ156uWtt+YNpeRv+MePV/3otfOEzc76ecTfxi0VzflTxt2dnfc6N/enWfbXe7W9OXveL38neidqqD7x+wu2/klWFYVde+X39xblrb2Wv+J7i4nsd'
        b'u/e6/Ai+8OijK15Pt51kl/0zYHrha//Nvv+Xltjrr4v8Cc6ZwVuMYTzYBDYlu1BscJK1EBwuZVDTa57gBsFAGABFgr0YA92JImhDAbpmoXi7UcUP2CAgoGc/IlPfXeB0'
        b'MJ5W1LU5h0BIXNpOpijBLdSeB2xRZI4bxpGcRqCvZeDWrungQFllEhLj9iaDC2DrFC7lDV7j1GWBi2T2sQ68gsSbnWXkBkhuhBoeZ4GTjeA1ghuBPg322t9Jxklb4NIw'
        b'j0l7O7giH7tA8ilwgLlDsnUOPMpsZ7mcCXsaYH8Zs1fFsk8lEFzmhmWDE2QOFd4Kyyuz3WkEb4AhFMh/BQdcQoLjZVIlVQ3wuA0Y9oPXbDaCEDQMNkWRd6aAlzfiXUfW'
        b'LSWgCxziUz4RnGfAHXiNAbyHa+HdMTxcB09iSMxRNshIq2pmwlPW+dglSgIFM/KZmzdOSYpsL7ycBlG7XkVi6hZSXxJwFvaN3UXAWUBuI4DPK5jXHklEXROlCvdUlfAo'
        b'cCjJFfSwW+GeepH//yCqxIOYWSflACld6pjbEm1XcjIuBES+ZwaRS7yooMmHlPuV+1S9KgwrMChr6pf2rRhIMAgyjYJMfFnlZFMY3ZeHANmkyL6ynjmm0Iiewp7Ch2ER'
        b'fTnYcXJfidnRJAjWZxjDku4LkoYFSaawyf2Rh1GQUTYd6m8Sho5y0O9DYXBvxSgP2Ub5VMAkfUFvqVEYN+qCHVzNDr1Vo2742d0aIHbUAzt4UgHBPYV6znHPI57DMVmG'
        b'4GxjcLZBmGMU5ox64QDeVEDIqA+2+WKbH7b5Y5sA24TYFoBtgciG3hKE7cHYXjkagu2hzAvc+2UYM08bjpluCJ5uEM4wCmeMhuEAk1BgnN9w/BCBQg8Lc/WF+sJ+Hrlg'
        b'c62BzjHSOYZJucZJuaOTcSCaBMomgTjnPE96DixhbuE0TMo2TsoejcSBpqBAo1HYFo1zUzEag+2xODcl+oLROPwUb3kS4acEy1MifkoiLxHpZ/dVjIqxgwQXNRnbUrAt'
        b'FdvSsC0d2zKwLRPbsrAtG9tysC0X2/KwLR/bpmLbNGybjm0zsI1CRg9/dBaLCgnr4T30DTjkud9T/7T+6YEsQ3iaMTzN4Jtu9E0f9k23+FUfX3JkSX/TgPT0CmNstiE8'
        b'xxiORQSjb+6wb+7DiBgMiSXE6CkyCUMOle8v7xegv0Unwk6HGYRio1A8TL6moPBD6/ev789kBJMHQSn3g1IGg4dyDUFzjEFzhn3n2GBMbwZjXibdgZnu1IzwNFqpWjvC'
        b'QV3h2wFKbwugHIcl8c3wjp3sMgaRfVYQiS+e8WKxkjCk+/eN72x9NVaNnXDLpm56F/A4/+vW9CPY9/WvHbTvzBEeWstWd/MsptI8uaCWa9vVKuLXQkvxJLnNXMUTTTDT'
        b'K+XrNCidNrVcg3cJMZMg5lkdjXVm2zwj4mxiePykt5KZSsLZqV+HMv4N6/xcnYJbcq1i85pksBM+D/Yi1ncV7gfXFoNr4Cq4OB/oeFQw2MQB52D3erDThyBJ0ANvInaG'
        b'eDclgYMLKIkv2EwuvYc34KUUAn3BzsVi+HyZRMKhhIHrQBcHnEcpHiaYOeAZNnU6jpB9eUykL3Oen/sycNcc04UC1wRccIYFDoHDHiOsOjJLUbJEmsgoNdGrdxDFJtgF'
        b'zhAVZhPYBA8iSAw2gz1mWEwgMQpwhShM/Z+COxAbBVvgS2btJ9TlkvfCu4jHd1XjSAjQvoA8wW7WpDq4j8SrhXu58AAqBhgEhxGcL2CtFxcrPk0ZZWuwcPnO/sKD+6bh'
        b'PcJFTWl/XfUl95k54lc3X1699dqikbc/pjzq4wKnnO7JWF9yHTQWsK9xCve7/fFX+372HmfF6PBQ1KMAX/eA6pt/vXH0Hzs+rL9ITe14z9Rfyo1KfL2469TG33SV/K7+'
        b'lad/xT6YUzA/Nebl3IUzmw++/1nauk/3vXDuxXN/Lsr4bN1rn7/ZuOuvgp92S7OjudWyuNR1L+W0dV34x4Kf1HU3JX9W0j7jQDj3L0u26rN/nnL3raeWc977JWfTwZQp'
        b'GQYRn0CfRjXYMm41Gl6JBq4Fwu3geMcjMpBNBbetNx5RU/CdRyXrCOrxgjqwL1ECX4MvVrBRxQ2wUB2HMEDv1Vx4AaFMDJdKxGzKYzU4JWfDfrgLXCIgbjY83WCzTdei'
        b'hguCt4gmrrSRLISbnJQ07rpx0A8PclolYLvI9YnhjKsVzlhBjFRTh/uvzfhqdiEgJsC8am2BD+FECE7EiE5XPojOuR+dY4jOM0bn4cuvC1iMua8c8fUg0+TI46uPrB6O'
        b'zRriDFUbJhcYJxf0FJsmJyHOPTkb2WITzilPKgfTh1wMsTONsTN75ujj91X1VJHUjdEZD6Lz7kfnGaKnGqOnYmxUyGJMc/Kh4XppXyyBR8Ghx/lH+MOTkwcFgw2G4Dxj'
        b'cN4w+ZqCJ/e7GIPjHwSn3g9OHYw3BOcbg/OHg/OxB6/P+0Fw8v3g5EE+g26GyXfUhUsH9uAzhOLS+2WnUQaHY2eh71Ac82vJ5sOgST2e/9K+ny/sGZm5oj+22/czx+c/'
        b'cvXTGfS+86wRbptU22x3I6JV8N+C2RLPfCMiPunGRedKbsTlW29FHKdT+J+5EfeXHJaT9VljPAqzC410NbYplbbc6smPZMGVkEeXNNIJ2JZAI3yhYVYCYD4kX4uPz8IT'
        b'4wmSDkVbQhJ5kZkhqp3Pq2vw7QQy62y+VN3QrFgtl9BVePHBGoVGbmV6JA1SABJcSje2KhG6+QYO5uKEg7lWtifhAecmOAqvJRajUWxeMZLhSivKwfmaYnAZ6pIkSLAq'
        b'hjui4IBLGxrI9zER9HB7bhka9korJLALCbo1UAd3Js9HMpw4Hh8nWwZfhmcLXMDz5SvITCDc6YkY3wFwkcx3cJRQD3pYYMsqcKMdk/kieBRuSUQ5XBG9lloLrxcxrPJV'
        b'eD0osYpNsRZIwA4kz2WA1xQbLy9gax4h3+Fbwcfm53uDFM+XDjya+9fy8sHXecFDrOzlm0oH58yqX05FB9/fLvZPrH/HGHPoDTp2+UvxMQsSJ8kH//63de/uHXXL+3mh'
        b'gv96Q54oXnXxZ6vavF97qkv15x2Vc39+4Vc1Pyj6W+rRv//oD3pq6qLhmwcPVdcJsn5V/jEsfuYDxVszO/P2zXLhff5SwG8nBeiH1v2Y/fIpr6ipP7w168BXCcLqO/Qu'
        b'uZz7y+mx2nO3ZmzZdmb9J8bFCxf/d8bpV7Qf0H616U8fLC956c2fnv/t8dP6Hy7lX5nRuSxe+vVrK7732fq3372YuK44LmXrgaHBxHcfbnENmVPyyy+X3pL9hR348+KR'
        b'+adFPoSruETBA6S1ECTMBjdXscAVwVLm1vND4MoGLIvvgUcrsVxO7qPcyd6AEMpJRofxYkU1vA5vrCETVy7wAJtyA+fY4BS8BgYZVcqmjbPIWRddSWwKnMnmV7InVcHr'
        b'JHYHOLQIJduVJClBBriBGscDDrLhHfAiHCQKjgxleFkS2FOFLxQFN+ewKI+ZbKh38SMieTwCSTtw/OQqxNcQpjjG38hOgK+g1DGemLeqHMvrohywUwL3kvL5pHCa5MuZ'
        b'hdv98AC8a+WmQvACZqfLy5mC310ObiUmI/KC/e4lYomIjRjecQ7WtYABJmPTwQDRfCRX8ii4GRziT2UHwUFvwivBDQnYX4YIfgCf+0KI3k3IBifAkemkToLAXglWITGV'
        b'Au968Gexg58Rk7jwPOgEh23VFIXwFFZTdFNMa2UuIRlDTVEC9/HBADuJChN5/Kv6BQ/KbtaK4clcPBp0eFn5BH4k3PiamRuX+iIs2Zt9aPr+6f3RzAEWWLTL/TA0cniK'
        b'zZkSggAUaNr+af1C5vgIEmgg7cW8C3mDMkNivjEx32m84ElY+D/s3efdwzMJgg7l7c/bN7V36gNB/H1B/ECgQZBiFKSMUu5+iabQSH1cf/QAZ2CZITTPGJrXU2iKTTy3'
        b'8uTKEy2nW1DiAanEOOyu5+plpuAwnHB/zUCGITjFGJwyTL4mYdChkv0l+8p6y3rI38Ow8L7s49OPTB+INoQlG8OScRpxJsTtXY+49gtxxvTedu9hByQSw/ye8Eh9Tf+U'
        b'03Hnkk4mDWgHawxT8oxT8oZmG8ILjOEFKLWQxHsLTJMijhcfKe6vOVzZV6mvHOUgV+JFjM+x8Yiyc3NmINHTqfMox5InokT6XnRgEZ/3fT63yN3t+14sZDLgwY0BD19O'
        b'gCDG0wtZSbPcTC4MqHBl4QtZ7YjlnxhRbKIsF7Ku93myC1n/h64bP+yWTL3oPY0jMp9mh++7tDkiDvEt80fEY37Y6F8w7hx2vGtb1tpQV0eOGBlxbVO3tsnV2nVPcogJ'
        b'3m9MVvyTWSmiTiBQjFSdSPgfmZ7GLHD8zPRYG8rwaGw9J/BXOEI5x+7cy1Eu28sXkRMyXCnvAN3ifs6A5l7+8FPLTBGRA7nDs55B9Ou9nIXIFpmPiPlwTpFp/oJRThS+'
        b'+/Jxxue8sUijXOxayqJCp+iDTb7iYV+xSZg1ymOH5nxOIeMRNnSlCKuHROpdTb74QlSTMBMFCMlGAUKyH2FDV4ICRMTql5jItKRJOAMFiChA2cPmI2LqKlGYYLpnrck3'
        b'cdg30SRMRmGCU1GQ4NRH2CBnfNoGyMUB8nGAfBwgnwQImtzTbPJNGPZNYAIE4QBBOEBQvm4uChAWpY83+UqGfSVMNsJINsJINpCpKxt1ZXlhGeOxJp/Uur66XzOYfk/w'
        b'ZropnB4QDEXdS39Thmu+htR8DanEGtbD+QtNS5aNcsRes1D8JzVxM1hSGOUS92dYTGNHDVbfi3nT5d5kU1iEXqtPGOSgPFQPL3pqWCrHr28ir28ikZtwZuvwbhJOFcsr'
        b'bZT6102cI2uiXOJez870KkIZ/rdNFSvEK3yUmsjIYuo7atgrwuAVYfSKGGUHeqEB9RuNzzmU92TH8MyJrwS+vgb2LwOn8zQlSSVijbc3h/IKZ8MTHnA/2R3oAc74eoAB'
        b'LQZcHngF3zy86w2v3puUxo1Crpuc3yBP7ppmWW+Qtyjy/jO3xz/RXdMulWRdJLgLeiOU0/ClupFUZLwbmfoEN+FBuL/Jt0wCBlMyUXz4MmuVAmxh1nkOzIVXx2Y+Eep7'
        b'Hs9+wmPgBthO6rSpGa9LKknC6ol0LuUKdrILQH8pfHmJ4oO/zONpnsbZKdyAzwM5MfPNA6tYnKxBT91iuO7pXaJdHsFXz3M+bZpy6bmQeX9cMfQPSVG/pFF5e4F+gf4Q'
        b'652l72w7+TzvYm2gZ3VI91BeSHVwXkjt4eiQngrXxodKFlURGvDlu6dEPAbunm6fC/pc7c5Ni4JDBNqFoIJfRO23GR4aQ3cI2onBCwRTgpPwBfhCnH+i3WKtshiSsEwO'
        b'D4xNP+G5p7lVrUIuQbrwFBwKxAuOGb+n2XA3vC5vghcmPILEs00tR6KnvA4vvu+weyJAD59Egzn3TD9KGGyBX7rZDwWBh3L25+hnHy89Unq4vK+cWXqkm41BWv7+fP2a'
        b'ATeDIM0oSBtzWsss/kEOPgF4KIsxBYXp5+oX6ef2bujholC6MltdxggXZ2KEz5y1NA6SMPoMDD8YtiXA0MMu95Eo+xolZUEez/myWKEYUTg1vtN7rO2o39f8+8VDfFCz'
        b'h81BzWn4cBHUNdnb3PCRzXKujLONIkc12x9jzCN+fOTn4uDHJ36uyM/Nwc+F+LkjPw8HP1fixxzvPN7Pjfh5Iz8fBz93lGcXlGffba61HrJ0HauRJfNH+fc0uwvwUcuy'
        b'DOIegNy9sV3H17np3Bu5skDk4iPLRC5cFDYYH27c697L7uU0cnq5vTz8JxM2spEb/uVYfxlXxuQyIWxM7ni7LKTPR0HJQnt5B1iysF53ZE6ypIXs4UxYZIuw2iZbbbQs'
        b'EplTrM9RVlu01RZjtcVabXFWW7zVJrLaEqy2RIvNtgyypD72GZZM3MfGRzzL/eV+MkmIlYT6BZSTj/0gbH8gtDmN5H8nDZIbofkUZOYQHPdGF1kKauEAcpy1C2lVniwV'
        b'uQTKhOQgrawRtzqEHaVFCqWcHApqt/DIqtDTUcw8k83CI3zeMhe9g9KxzWo9vNzI5T+/3IhDObIrd2a50W9ieGRhUUqWKf9arZxZmT9rzm4qmEXFp8z91P2dtX6M4wzv'
        b'Z1lfsaklg14ei59dPJ1qx3uJI/0q7A5StdOzIy6w0wXcKaOqm1x94Uuwk6SztXUKNRv9psz/ifdPYqqo31pySQZKxfc+uM/TYO3o019+dfTtrGMnDlw9EPMCi68Pzjuc'
        b'/9Qh5oirLtavQ+Z/HDLv168gdrUg+Prrv6+PoI+KjvLekPjzrh2+fvh15T/8Fw3FeIqSBmIzUldvUUp3fPBmL+gBI29Huz1g9co3f8b/fMn8vn+uVbZFhPX8wPu3V89t'
        b'ffYHm+eF/ejeT9nUD+9NuvvGL0VuDOca6oC7wU6gb63CmIZDudawteCMP+FcYC84XoA8XyTLafjPwXNxbL/aIDI5Ueg2j1n87IfAj+3iZ3B+OTlDFB4CL4HrZHrCD2wd'
        b'X3NUTAg+/KKFWYzygksaPpUU1XU8OAV2i5lwKFTQJO5UcGQKWXgMj4LNONhReAXnFewmy3N24XXFR/EulLPw3CMahzsMz6rBzoUBllAV4BKFAh3kAMRtwfNk9Ta4CV4B'
        b'l1HZ7sIzybAruQTuYlGusJsNti0Dmx/h+TywZxkH7FxTkhRQUkIgHUoM7K1CAKCrCu6R8KncMj54Hl5Ti/jfIMFhynQ4fNTf2vHsTx/Fx+ZhBrjMj5oc3cPt9WDWxQoP'
        b'P9X3FHp0H3Wn6Ci9pn+qYXKKcXJKj6dJMLk/8r4galgQNeA5qL4fnzscnzukfLPh/vT5w9Pnk5Ww+YbQqcbQqcPCqaaYVHyy5xTTlMSBwoEFA4WnJeSc0sgYcu6n+SeC'
        b'Jm+OjO7n4QNQe9CfDatnNA8jPLLBa4SL9wePeI6t0VS1jrgpVG3tWnLPh7PJDUYXYZ6uf3ydJGNYsJWymatf6sdi5WAU8MTGdzol3+eWRl3zLqC+zdGe5hMLeXW4qiY6'
        b'CtCm8JazAAvYtucV1m4yHwU4aeyiC4fD/yTqLhTk2+fNq862Ab9FHmez7Y7KTLZkMsImk46HeUq+/XmK7nVWovoW2ZuLsqfebRmBvw4vsaRh2Vr772XKrQ53groWxYSn'
        b'UDrJUynO09jxmIFYe0M3qltbvqPMSNd+i8xU2GdGSDKDt2z/W1nh12lbtVLlt8jHPDtaX2oho5AanI5l//eEmfrfsCRm25NAEx4DTd57jkPpy7BteXlB5joGhQxFuFD3'
        b'1obhTYPK1703UIqffPExV4O3kLKPXicCMDkKc0FwzC9/X39W+P3l/NgdlcIA6Y9+GBwSvCgdvJe+kPXWcv6PM6g5GtdZwbEi1iO8pw/cmAOfJ5zMKR8DnVMsrGzaRGIn'
        b'c+6kn+3wPHbsZSrFcCyZPxU8qXdD/3xjEJlUCDeFTdKnMjseMvrM21UGCgxBWDP4r59+6ZiLarbtNHiD/39sGvyTf6LP/1WdjpkSQzk8ypfbgwqxSRmcOlpI1tKlfTTQ'
        b'QL0WjRNm7RUpjp36HofQofje9DE6zAuJ/uXvebs8l8x0b3D/SVosf8d75W3T4r9u2Tswc0XwlpCcn1Ddha5y8UwRm9Ah7GsOnogMwQ2gt0KqU/MI/HRvc8dzhAngpQ1i'
        b'CdapbGGnw211E6pGfOrINn9Fh7yuXtnasLIjxIZS7L0I3Sab6bbNn4pPOr1hcKExLv9BXMH9uIJ7UffWGOKqjHFVGP3o5Qbf6GHydaDaER7Zyf4N2o5CrO2YODdL7FUf'
        b'LYiA8UYk58Z3q/oYP4biev/iWcoi7h1i7kGiGjn/QeptGk+9zpYsmO/seHnmX1i/51Dxg1V5xb/Z0MjsHUkrAS8XwCPgIipRB9UBbvgQZ9APLk+ZqQVYP7KeWg+2y8iR'
        b'd+Akh2Mn5yECrYmvFLOoDLizAHTxvcFZH7LT+303ZqNKSmCG5HR0LkV2L4fJqthv8FMSvNukgg+CjdKrVHs+Jvat8GVw3XKJht0mZvPAuwj0p9jen3ECHnaHR7LgEUbf'
        b'TLYVH4XbwT6LdhTuSDYrSEvB83MUnyy+xdLgualMYdrRt6eiTmnYHvnnInGhV2Fqg0+ioDCu2gumFaFeOdOTJdr10yT69pLbO6QsTlYP2Hbh1JIbOyK35x4NeUPyUbK0'
        b'aMFbWy5c6/KTNcRpAgXLeBejl2VeqFWqLs5S1+3zeSMp48F1eXrBh6/v+dh7tXaNNi15+eu/uSmfeSf0xw2ymas/Yy+6dOL1zStcb2RdeEH4vvtZ99htkzdL/7/qvgSg'
        b'qSP//+XgviFA5Aw3AcJ9i8gtEC45vBU5AkS5JKB41VsRLxSPiCgRsUZFxRtvd8ZurdtuEzZdU7Zu3bbbbrcXbu222+5v+5+Zl0C4rN3t/v7/v8RJ3nvzvu87M983853v'
        b'zPfzfbT1HU5OeNffQoM9w3zC3qXenRZVQLoFxpKAwEX3yvgG9OZ++dpUstyP1/rBhjjtcn9YPplozgBHZw4H1ICtsdnDE827gc/xJhR4CR4Fx8GOEtg92RBH9yvGYB8d'
        b'BOOCEzhm4kfmowvmwZ3Z2vmrK7jMhhfgbe5zjOQMD/FDSGQLPBdFkgF6M8Eumia4PQ/u1qeCwRl9JwrQGx7AhVAG7b4AjsEOrS+rfTrtg9CSnK2xAcOtlMYMXAc64BU+'
        b'e8IpI34Xh2MjIG1qRYO4UbTKUqcLIWdIP8bUxquwppzd8Nr6dJK0pagdXfHyt5uay9OMwntX7l8pC9u3rm2dvPHC2jNr+wuUQYmqoMS2dffLH5aBpfeXPnHxVfCnKl3i'
        b'VC5xCm7c8Ogtt1Y5BqChW2Uv6GOhv5SLRleMlPYx/ckD9tMV9tPx6lKYtPFwTGeMXG/AUaBwFDxxD1QE5Sjdc1XuuQqnXDXX6TE3YIAboOQGqriBCm4gOtNpRp+TFyi5'
        b'ISpuiIIbosYuCDJ3BccLfVQcLznnguMZx745Sn68ih+v5MTTV5QkHbLVFlena9anu2Z2SUOlZEK1Ql/bPWv65xzcP4+r3AW4W1423C03Wf/vLn4fNAqges1jWTll7IlG'
        b'crLJjqG1yRGLHO6smRVs0lWzJ9hkp0e6ava4rlpvXHfMfkVP01VPeG1yZPeJcFANckj3C+/EoHG+nRGH1GJXyhVeDyQWRxpbow+eANf91wSjhmiimsAV2E3fczgSXTir'
        b'v4ruye3AZXGuQQpLkoCurXuXe+RRKOr2lpEuTf3Ge2/07Ty8oSQiLKt3x41229QbUv4WvtRty412cWTea9W/5hy8EfAr004B1fqxqbUTB2nHWEzCYVs82BGUAc6BW2Cr'
        b'L0A9BnEkYlCOVWzQAs/D1he8o+t13lGCpTNKjMgZ8o5ihrEQ5dlQU5wfc30HuL5yuz7bfn0ld7qKO71NT23vhHVmF7WjszR0iIV+PfXwloXJ9fAf9jC2DNSRcIMR74kG'
        b'rJc14N22Y5UQA4q2sgyrIYVjxZzwJ8Zi3kxpLCwYsNCGwcAbfn4q+cU0ESPE1yghHx7wieGZrSPkBkjMsdHZiIi6wf+iqI+b3U2sU9MyzaFl+gi4AOT5SOYpyplyhpvy'
        b'xMuiBlgkMGmcaODIo3gkvec28LeESDdsP27z8Mvyub9+cL/PocVNJnX0/e3AG9d2Wvk+MrT5opTVGsooCus+88U7X5Z+Vn70LfUbkUdCtogDJWicNKHmNlnFRxZpJeMl'
        b'tpQYUMNbSmjhNSFLcBoJttWRkJHTRIwLNGK8wIbiTGmbRoRVbe/WtkrmJbehRwcsxT5qJ1fsdHU4szOzLVXN9ZSayorkaUpumIobhmTdy1dWIPfCfwr7YIVlsI5kG7+E'
        b'ZI8tjvGIoA/bWGdjWZ+4JHVY4LfpCPz8lxT4/5b8+yJeP8UbeUa9BMNd6WZKd/WF9PQGmr5e7/9mXz+RWq59AYhGtKt2MdgG5AWCWfBAWDqL0jNggI11fPHzf4QwJBje'
        b'6k82bkcexaKX4CR5Cdy2nG6/sXkvw1zKjZ0yde5BRuosmDp1ypk5U7h5rw1Iz5wrUnNpBfIjmfHAd5+jHhy3tclU2MpMFGZp0FAcpqK52aSir6cVfQ24R7Em/KRG9rk6'
        b'EjPqChH/CI34V48Sf1dZ2DmWPFWe2ud1Oqs3qz9SGZCo9E1S+SYp3JOV9skKy2QdATccI+CD+hUlZY11DRMqKoY6kk3L9QIs15NyuQKL9lod0V76c0T7F0MzwGx3GAVT'
        b'febxLL4FjRxBMCQImgTGlRg0GzE3LxWtHDRbXtdUViVqIKUIGX0YOmhShgMViGobRQ0hugehg4blYgkdYQCDUgzqLS9pxAFpRU2NJc0k2Cne1TdoKmouqyrBoTjxqVdJ'
        b'TuwxFjJorI0QIC7XQQ0+RXI0ihurRai98FbDBmzkbMA2pokC5eYMGpaW1C7FJAdN8C8tLi45TcKfkOeFNpQz8IZEDKdYWtdM0IkH9eqr6mpFg6yKkuZBPVFNibiazxxk'
        b'i9Gdg6xScRk6MEhMTs4tyikcZCfn5qc2NOIesYkxZvaO6xzvVfl6K6VFiThEkYVg7H2Bx0uqxbjC8H9xHj9uxHScoMMoo+fxfzRfSxZg6xnl8+NdvWl/Nrj5FdgvgR3w'
        b'Orxm0aBHMeGrDD/YC9vJ5HgW6Ae3JLC1sHE5ugyvmjAoA9jBNAc74LWmaJQhbi684o9dzc/5pmcHZmTPhC054FwA3BOUOTM9IDMIA9vv8icAa7UVGEO8fb5pMuwoIKO3'
        b'E+hohu0zMRc33FZR2fAAWE8upIbDrWHhwWyK4QMPmVKgHfRk0Jujrpjzwua9gt7AMCpsGjhFsNq8wGVwEWVnUgxfcMGAAvuhHN4m3aN4KTwhtHTQriozKJN5THieCqF9'
        b'Hg6Xh6Hb9CkGH17NosCBaHCWlBpNbHeiOSpBDohgU3rwIugAPQzYHgevkZrcKvanCpE4tBmL3H9MTqVoHPyL0yIROQbF8FsMrlHgIOiE28gGrZBIJ2GgIBCjql2Ee7IF'
        b'sDWLQdmDHnYCaPUlBG/b8agEioqmeGKn23kOFCkXPAO64XVEkkUxAlbAdgpIuWAX2dBlAO4J/IMMMTh/Br2vyQLsYpUWwZOE3KfL7Ck0bbestxA7VdQsovV/tyYuomVA'
        b'MQSReqjsoAVsJg6L9YXwrhCc9oW7A7A7CTuAAW6WgI2EkPmKeGoNRXGpaWXW1tmFdEEjMBRAWDjoQ9IYmIoqriMM7iek/EGXwH+OQSA/M1vAoIxCmEAKL4NbhNTNdUJq'
        b'P6qz4PraJYl1ZhS5AV4BZ1MxKdTUQeDoIgocgafgCXojYAc8AM/SDn+ogPpo4sBheoCbGnrRIbShSJa6JutzbqOG3m1wD0rDwlGnzwioACdRowJMD7cCPxxcE4JttpkY'
        b'QQHupmEhzMFmVjw44UpIVgpjqHqKCqYyyhtuR+rTJNHouheeRSSReAXCbgYFDqFSHSPIfPWeC4SEXM6IhDmA/eDYYjZorYSbSXWthfcAakVEjxEEW0ywQ89mISkhG2zO'
        b'EcIDC2gSdDua17OiXUoJOzbTrSkMGyabW7XgNU6hpoTd8GZhWCiW2gCwEV7AcnYPXGoinhXn4AZwVCO3TCS3l8COFAbcPwecIQIfxYSXwiKCUd2Eomrchm4NCSKSBi6C'
        b'y7DLX4hdKxmUvri+mDllSjQthKfhpoSwKHxTNLwC+xD7JvAAYb8ItAj8zUEXLYWt4AJFmcaxLMH56fSdB0ErOI1uRRUXu8ISiQnsBC3kTtAOrwcIF4GbdKXxwRk2ZWrJ'
        b'sq2vIgU3TTXEe8SC169rzrJJi6OlbvVq07CocMRGLDgOL2EBvocqmFC7Nh+e84ctGIlRiASlDLaA20xHeCOCyP1UOyBFdyIJmwr7SxEbVkxCMApshvuFQrxxgVkHd4Kz'
        b'jISpxoTzpXAr2I9uQYzHCcA9DLophedJ9c/kVQlxn7YT72XQt4F3U5hG4AIdLPjImlXUcyThQ81VdtuXc2m2ufF+4HJwuB7FSII76yhUW5sQKfyU+oVhcIcRlGVl4g0W'
        b'LHiXAY540MGM9W1mUDvR+2uZsjjzvXoPTU+9He6CmzEx1B8kg53gBra2XkZ9DGnC8/BgnBD1LEhBW5QIL6PXaQtsI9QGQqYgmaaCLc3q49jLp2k6l24oA+3C8tUZ2FmG'
        b'zWYgzs460AaB3Vx72J7JxW7TVCBqtK4mbKuzBn3wHIF9yU+H23MFs2g/NNiSHQwPBqBuiKJmWBs4moFW2q56Acl9u5CaocXixHs/pEz0QnYkjcRG/pSi0YoSwsqqKb9g'
        b'elaXjERnA2yHh+BZNIoFUAGwL60JvwkLOKBPOGaLUA44g2PqstEwcEaviUHLnh284AN3zMS4RKhHs4bXshgL9dw17nFgOzwrLIS7kETAw2jM2YemkeBV1PfT0HtIajvG'
        b'QMnOhtcQ+165emI0smwhUpUTCHbBI3Bvrgm65y76JC4kruXgUjPc4o8qJhvuThdk0nYOawfUWXkX6oX6ajqvxYkOVDjWJyKWOlkssaY7aF+rCkSxs8QAbwJGHwdwiEQ6'
        b'AZ2FxWMpLokPYVLeRXph2XZ0c0rRC3hKOBMNsQzYCy77UPCOgTWN0HkCXIAHC2yBHI3Ou9AIv5rhBDrBVvq+u/Cym7CIroyTAbAFdcnmDqSy0Vh1CZzVIvXCE3DTcB/n'
        b'Cnaw4bUyeI80l/esQMT3OXjFDPF6G33ACQlhHAlIb4QQ3RSYgQMSZwhC2ZQj6GCsYFcjBeIMEbYpcHMQPBIexsI+iOjDc6AxT2+AzaB11L1MdO+R+Ax2DVgPesi9QkY9'
        b'6smPg6t4pKfEYIcZKXAWf6lwcRZqvmF+LWxYS+x49LrFFNz79EI5bSGLBRtJs+XB/in+dKwbJFVBNDivE7iKZPgOG7YGh9BjwSF4Cw1LR8zBNvRygFvoA+7CXtJ6tfAG'
        b'EtodnnAT0k6WUkuBNInIGx+c1BPCzRECQQbo9c3Eb5tNAgvupxYTfqokzfAIBxw2xcoN+sQupVUQKVJCLgtXwqOjsC1Z1fAazYoXur5XYmaG+ij0vqKXDzXAbXCMSFfU'
        b'HBMKNYyhpWtl9TFjI42pZFsUGh92wKvwOCp6HYW6PFvSSrGvTEHqWzrG7t0pBK0zcgWESZ4jG70W3TZkAWadmRfjdkg3ksyE2ifNFvZhtMRagy7QB84COWyhjYeCBeJv'
        b'Pr3KlKxHdfClf9jJ38+o+0Mwh1q8729tnbHXClb0rPZ8MvVJRvurqy80Btn/Jdnk4aGkoePBHwk3uDTyV/FXvfOG/Y9vxHtd8wxdY3fcIdg6M9fVld+xZ93n9wLqF0R+'
        b'T9Xt+MsFn4Q1Hy7+Zs7rrXWX7pvr/W7N9985ewp2C1ymf9h/8enlT6PPzC/pfX3tl28t70zZyOTA7vMWXb+pvd7z9+ebfjB9MO9f9wR13vVgXw74TPSkyTfxxp5ci5SK'
        b'HsGcPNPq+n3PHt7gxtqGe1uzIp8vO68/62NJ0Rqba3//bU+ngcr0tVh+JGfZo7z30luzU98r9631fk3Q2v9OXqf3azWt/U/y3ktsnWq77NDx/iOcbz9aE7Y6Y1mX+5dR'
        b'nMr0ZbOssmd/x8iPk0q2uLq/BmM+eWbIdyl6ULb1g2X5cXslLrn7Pjjd+YE4P+5Ei2TrB3Pz4061fGL2mklP80yroDdK720/97H8tSl9tltXrzX69tPfvBHvXPjR/zw5'
        b'Arkm9/58OP+dM22t7AXZ01MHzAuuBh5455/9f322I/XjJNWF8lsHyl3e26788Yt3LjZfzbF+uDjx3P7vUiJ+e/f4zsCmC3fsZhZ5zHun8PlHXP7dx4GW+U4bvp59/9Zs'
        b'ecegTWHqttT/Ocz4cOnNz+6uP/mnh+w3P4z55EzQ/tbsc12iGJ8LRo+3Vm4Q+X31l56NawPANyUf7Vq2VypZ+Ievs0NPzX/UcffOl7O77b9q++DJM/f32t8vVSv8vn28'
        b'x9zF9JOnJedjmlMq/hl9ueHT13x6vgsvUJ0XNKe1+k+pTFm79e2Mr1I/jskMuvvPPYNnXL/2z19zdOmbdelfCW63mzXXST80GPinfOfNk71/zy3+7JFvj93r8fckK5ao'
        b'/p5qv+L1t7tti7efafn6z649bwbVVdnwbWjIMRls9R2L4AD3pCHFRrNFMgoeJDARqFc4YuuPFyWZoIMNLjCykf5NLzzBm0HEmXZbDp7d6FPsFAa4A45UkM2QjnAT6AY7'
        b'LOpNG5A+u8tiuZkRdpntAt2WrLoF8BQNGHYQDdVbTByQ4nU6IF27GmYFb7LAOXA5lvZUOGsK96OnXF89ygPCSUTWt7LRqQ6wwy01SOPhaghPMMGOGniD3NxQgBfoUB9w'
        b'Y9i4bpjNLF81jTjGmiDN8KYwF5dtOdgA9jESYUcQ/dCtXvCwrlMF6MtjCuDpFc9xr5EGD1eDs0ssNGBvDHApMolsHFgBtxeMbFv1gZunMa3AsTI6DP2tQkN6OXE1mtDp'
        b'blyF+0E72Y7Kh+1m6ParYNNE+0wNAL3NFI3KMjQD3QE6Vk+w0VRg8twXP+0q2MlHJe9FCs8evAiM51fYK1pTC/4xeuAaOF9PViJmoJndWXopYvQyhCfoxCsRB+FxUtlF'
        b'a239QU/OaEwPVh3YV0kWTNGM8FVbsOMVcHDMxlYxPPYfuxuPxjFjlZSXrzIbMUahQ2In+5OeBvvDlnJxVzkH9YUNOEcqnBP7UZJzf26b8ROOvVS/y6TD5LBZp5mS463i'
        b'eMs5Kn5Mv5+Kn6rkpLYx1DYcbEmezXji4KHwTHvIeXvKoymKgsI3nN50UnoWKR1mqRxmKTiz1DbOMrsBGx+ljY+awz0k3CfEPsiIsixVHqbkBqm4QTon0N/yPrEqKEHp'
        b'n6jyT1Ryk1TcpJHrkX0+vdP7k+g1GZ3TxO25WumfrPJPvp+v5KaruOljLy+hSd4PVXLTVNy0sZcrlP7TVP7T+hvGPZNcrlL6T1f5T79vreSmqLgpYy9XKv3jVf7x9xn0'
        b'3U9/3rNrlP4pKv+U+6VKboaKmzEZ5yFKbqqKmzrZs5lKbrKKm/wzL4uV/gkq/4T77hMT1152e3G5JyEuUvrHqfzj+lHBElXcxJ+4e2yt/USTjCH+TOBoa/ecQsnQmCSW'
        b'4rq3rZJ5y+16Avs8lPaRKvtIvO4+l6HmC+QcuUQu6Qvr1+9fftv8vuQh875EFS18HD1zIHqmIr9IGT1LFT1LGTRbFTRbwZ8j1ZcuP2yutneWVux/BUeOLu9dMmAfrbCP'
        b'Jgvz8UqX6SqX6QoknY6unfH4KdHyWX1pvYv6y2/XDgiyFIIsNT+oT7/XRcruNH+5TM7u0iJZpNxX5RGmAVxO07xKMuYpg26Dp3jh3n+A6y9P65t5JlMREN8fpghIve9x'
        b'f7mSm6Pi5qi5Ll3GHcay6fQCj4K7qN8AXfW4X/GwWJW2UJm0SJW0SBm9SMEtV5SWq7nOMhb6S5NPV3lOVfLiVLw4JTeOPEWzLmp33eGSQ3+uMiRLFZL1EDXATBV3pvqn'
        b'MzjL9GXLe8wf86IGeFH9+kredBUPMTV95JHxKs9YJW+qijdViRF9xlLMVoZkqkIyHyZqC/YTGUaqJlmTIVMZMkMVMmO4j5jkftTH5Kq4ueMLPUMZkqIK0X1XxzxAqAxJ'
        b'V4Wk61wedX/mQz1lSI4qJEeRN1PJzVdx88eTyFGGCFUhwoezldwiFbdIzXUc4tvy7Z5Rtm72z3GCftlyn+NkiCQBlO2UNuF+oSxSyeG3acAWdNY0TOg1DTwo/zzcPjyq'
        b'jAPt20FgCUaNKmfwukYrpd2KMdP2Rc6BL05+0UWOI0Yh1EXz6aN9AYYX7l6haBwksmSHLfFUi4FmyY4xgQX+l9+RPG7JjkeNt8D70Bb49z2wtaOlwQgjylnNouh1PDwN'
        b'XGQFWjHILNgXT7lQLlPAYXrS1jsNzQTbKYwld52aQk0Be22IITwbbHILY1P2blQoFQpbcgn5Km8jypJS2DMXLzbdGm9PkQ11zUvxScOlJosXV0f76tNml9uL8FJA1TrD'
        b'4JKpriFzaB6MKuH2sHA2VYYm1OAAVZYYQfNwCu6dGxauT8FdxWgGTInSAB3eNYynT5lS0mSKtzhrJ7+CpnwtyBLVwHqBQf3iLNYiA5oHR1MrdPLpYtP6xdWzloXROe38'
        b'zSgu1cY1ylsckBNeRufMyjFFJ6PXGuQtzvKe2Ujn9FlkjOazefPMLRcHXF2RTueU8PAk97s1bHRyTpIDfTJprQFiSW5nzFtcPWe2kcZwdg5cmVOAjR9F2E4EXo3XW84A'
        b'N1e7EgNdIDwC9oUFB7MpQQrDEwfzvQjpaXSxO3Y0G3I2oxYzH4n1KVLxS5eV4T2PUFaN57s+hYSGMeyAm+ERYyoHbqOw7f8aOBpHKm+q8xx4BN0Kt1PgOnbjvg630Rsl'
        b'24zCYTuDAuvhFUpACZZl0ejd+did7i8zjBIWm3oEhVLErrsSbmyG7fAA/iuB5/XQlH8rBa7CuxpIpwYb2I83QCyEG/AeiNUZpNg1i411fL7BmTyyqxFeSSWGn0Y0l2gr'
        b'EGCzQhM4xoB7GdahsI/wLARbwXl/AwpshjKqmWoGl8EmcmEGOOsHzuJteLCbWkmtRDP/83SMn6t5aFJxlkkJ55Fdn3tgH+m5SJvMXUIM9UW4SPWz/Wgg0diz76OXxvNX'
        b'ePOzmaeYc/YrtqQZveD9ls3n9gvzNyVYbq3UT0869hEjZHvdtK2rti84fvbK4rIbVxo/dTfoe+9SKfT64kFwlkW23olCK+a6b6PWrch969S3XvvV8l1HMtwabq8LbNs+'
        b'GF/MkV9V9y9zayl8XWqfnne61NZgwVDbU05x6ezLcZEnRCvFm77LMznncfbk1ZwPPl/7/dvWN+fsSP79ks8eLtr6r4YvQr7oW/rtXwY3/9l16Mn1NRZ+d4WzvqWWVl1M'
        b'27+laVWFa1WjWViftOzguz/Y/u6v9lkOby7ZXvxDx9TFNwoevfbumXm/H+qaY1wx/9ylbWmxoVVXtvXGf9VsDdJuuLV/9usNx10TN8hf/WPM71czXQL+fjloqYv9jwH7'
        b'1p+Mef9eOTDOcVu1YO4P1WBWY9qJKnvPLy83Pvo4o2O26+E/HTUJ2/2pmlXxtrrptzONYvRiZn7q/e60i1/bq/8hLDhhe+fa5//6ovPrpcXO8z0WfF15beUfC/4+VZnw'
        b'x9996/jDnc4VsZV33p/12/ket1Q/mK97/8G873Lfz63Zu+LDd/n0fswUNPG8N2r/+GbTibZ5LqToLZdnl+JYJnAnmjX7IVm+52UIrzLBQT9fMrWcBs6Sy2Qy6wP2aOaz'
        b'KzzpOfUN14VoXk67RMLeSOIVeQpuoN0Vu8FJcBE7LGZjQyyOkI2RsxNZJmA/OC+Ge2k4qO3gIMp5NpPAYm9H09dX4HVDprsx2EXHUTkOrpbrzP1LZo/xjpw/RzMHzkFk'
        b'ES/+BeAgtsWfZ6CJZy/spzfPHvbzJ5vkNTvk0UT+LjMM3oLX6Lngcadi/Ay+I7hNsMDJ8p7dHLZjhZB2llwPZfZ4l6sGCpwsslh7sUCXG3pGSzH9kI3gVbhXd0bdA08x'
        b'reB6U7Kf1gleIo6e4ybLZPvycXhoDg1nuSN0lS4QJdgO9pGJK1zPJFNz09iEESrDc+kE0AdOgM3J9Oxd7g5voilyekBgIF7HRbzC0yx3NLtuBzvmkSy5i7M1vqTBzr6j'
        b'PUlT4T5SngRUGVtJpt1CeHydHsVmMsAxeFITlQZ1s3vBqyOQDXDjPLJdl21A/EKhHJ4KmmRjMN4VzDAg+4JFdrQYrkc94ynEssYw0mRAm0bqq2gL0JHcZMyJP9y1Dm6d'
        b'0DywyplUXyPshycRHe2cHhxeQk/r/WEnERTrPNDt76eBrwDn4S0STsgS3Hsp/1QdXKhBNvayWmU+ooHhYzKxn09DCw3Ns6c49m1hbY17Y/bHyBj74tviyWaYp5ac/WaP'
        b'LT0HLD1lM+XMCwZnDNQcB/Kxx/t6hSoO/zEnaIAT1MdQckJVnNC+0L6wvjAVJwpdxlYAjwGMJR3Z56ngxPd7qjm8tiwZp8dR5RbSF6LkRKg4EY85Uwc4U/sTlZx4FSde'
        b'Q9XvMSd4gBPcZ6XkIGJhfUl9yX3JKk70Tz7Uvi1ZylZx/ZQcfxXH/zEnZIAT0uem5ISrOOF9+X0FfQUqTowmW6fx3tz9uY85/AEOX47yBKg4AfJ8eYEc5QkZxX9Bn+eV'
        b'wMehGQOhGQ99laEFqtACBWeuYvbcfyNXVJ+XgjOtP1SnLiL7UUFiVZzYx5yEAU7CfVRqVNhkOoeTvIEu5WNO9AAnut9ayYlTceK0t7v2uY+qxyQaP51uoJGnRvd5KzhJ'
        b'/WnkvL22AkxUXF80BUAVKneXh8jdVRzBS1zVCMBQlFOI9TPKiW/zHCffRlMch32RUl+ljYfKxuNZjJOVF7pg5TVEkljKylYrSUpLH5Wlj8LSB8kXfU5p6a2y9FZYeqtt'
        b'7FU2XnIbGtT+qWbeqidnP/adOuCLp3idJrKSDgsFN0ierOBGopk4+7bJMxaDn4rRiVD6jGK4kdQ2DZ+xxTBDJNVHHBwy2WciTVZa8lSWPIUlTz3++fYOh5r3NcvYPWZ0'
        b'PJ82NsHQl7kpOJ4jW9nVnr492X3uKs+Ix55xA55x/bOVnqkqz1TiX1SKI6rbO7aZjN8m9hLAbmTNbhSuGwaGGPv6folnUNgpjUyg5tq/yEfuv+Uyh2EB+AwysUBf8RhC'
        b'DTuLNszBv+zHwLYRj/AGE7zXyQsn3jjxwdunDLUut9pfeOMUcTel8dqwtxXZ0k82PJOdoGTb3KBpcV5ifmJ2ceHcvNSCQZZE1DjIxoDigyaaCwWphQVk+kmq8D8zlo5D'
        b'arPHrTICtxGAGySEPRqqTd8C46q9MHGnOE5t0WryOqg5oUN6TE74Mwolz3HSkoLE1slTijIEKSyD1JxwlMEpEmVwinyOk5asMfhrYRh/LQLjr0Vg/LUIgr+mC50WgKHT'
        b'AjF0WiCGTgsch63mhzME4AwBOEMAyWDr3JautvRVWPrS6Gy2GJ3NFqOz2Ya0pA4ZsswCh6jJEmOmWR4DQ9a9IDU0MZs+RE2WOLDNgoaoyRJTfbOQIeolE0uWWQpGqf7p'
        b'1JxycZNxZFUKpyC1i4fay1ft6aP25ss9ZfPwl4e8XLZo5Ienj5wti9V+uXnLGmWm2iNEx1M6T+2Oj5wwDEOhzFjt5ScPl2UNuVo6ofcSJ+6cKdZqjrNUMsRCv55yHKUF'
        b'Q3roF65+N1mYTILyBw4Z4DOGlK2rzAaTGTLCx8aUrSNGlZBmDpngY1PUYFKJLFy6ZMgMH5tTtk4K55AhC3xgOXKzFT62pmzdZcmY0SEbfMwZuW6Lj+1wYJAyXIIhe3zM'
        b'HTmego8dKFsXGUuWIl015IiPnUaOnfGxy0h+V3zMo2wdpMkytjR2yA0fu49c98DHnqTepZlqJ1eSyQefpIYTLx8n8yEKJUj2UY/g5CoNk66RZ6hcIx+7Th1wnap0naZy'
        b'naZ0jFc5xqu5jlKWNEtup3IKfuwUMeAUQccBUXKjVdzoIT2WIyKFkhbhkHESw8xviPoP0nRmsJnTEPVzkxE8OhbFHJ4QGSwnKL+Whax5NbBnlNXHRPP99SKMaWWlg2nF'
        b'wEhW+9n7LfYbVDBRqvkuZ2p/9bJeRcPRWQMtKSOq3JXsPzdqsahglxtsNhptgJrHZlIiPQ3ClfEE6Fd65Sbomum4awbkmhm6Zj7umiG5ZoGuWY67ZkSuWaFr1uOuGZNr'
        b'NugaZ9w1E3LNFl2zG3fNFNdJOQ/XQbl9JxMdIc4x8tUSM22ecq4OVpM5NcG/F+M9jaE25T+htmrcmR7Gbka5WwuTmB3p7b8mLRYtlhVG5Y7jWswC5TJqMSft6bTZcJ4l'
        b'LRG9zqNpEo8DVotpi1mFXrnL5jGB5eZZlTsQMBH3QRqMVJiT+v3BUUjkOHyH9hKvrLpEIuH55tVJGpeLGiQlteV4KBeLavmj7hl14FeIAdEr6hpqShp56FddqaSuWtQo'
        b'IjjutXWNvOo6vMWbV1JWJqpvFJXzSlfSoO5+oyHRGyoo7CgzaFRSvlwswVu/B000P8kObkM6Tjk6zSqvWD7IWlqLztWIysVNNeicYT3ifEVdQznRY+jd4HiHeJmhTnMN'
        b'h+yTUroOTNvY2/S26W8zIG7VuHXYqF30UJ3qE48OM03gPiTv243HGIeNiHHYcJxx2GicAdjwFSONcXjCa7rG4T89Y00AkJ9RK24UE/d0TRgXbaOJayWNJbVlopeHxx+u'
        b'4VgNvL4GCaauglDWbJMvwcgeSfTmfJShRtTAnzjaeyJP4+1AR3jhNdVjpJIoXrm4Utw4AWr/aC5w4w7zgX6/iAt0eTIeankl1fVVJYKJWInhlVWhR5YhEpOzoxWvieuE'
        b'vsrzzUZSjVgS1f4bNRLxUzWC5DqWfiHTZvGqS0pF1Txf9FMgRI9bJRKXVaEXMZBXJGkqqa5eSdgS00IhmZCL0ayTuvUN1amKCZjXMILerVheFkGMxFRmBGVpm0NTLaiT'
        b'KCgpq1pah6sC8YSYbhChPmCS4AlNpdWick0nMJpKHkrrakW1GkokdgI6pmtK03VMXMcZjbyaJkkjrxSJiqaaS0WNK0SiWl44z7dcVFHSVN3IJ71Q9KQF1fYfdLXTRzxx'
        b'uabBwn6qwbSdDn279ojXIKoUS1ANo84O9YlEnAJ4TZpma6ptkojKfyIcxEQOuxb0ipBjHl4uoaKD9QsXfOZhROMaMEB7oxbVQBMKMI/AGmSBo3APX2tknKkblH1Lgqll'
        b'ONxPiM5zs6V8MYaC+aPAN/V4FAlb75JdOTFNLT28a7xIl2RXPbi4xhT28JwI1cer8XoN5Rs8K8nJuaKRaoqnsKvEKvGEZLXGznDQQgAfdEAY+kGLCbbMwquErnQaXkai'
        b'LIPTXDOYvkuppnB0MigTdE9IN8O/QJfWerinBvYZgQPgYBqh9rtGI7J3PDiSz91qbEc1YR84uCuWNRE12KK1Lp9Ej9s1ls1rJuAE3AJlhHB2Eb2pMnj537N2hhtQTbHo'
        b'5Moix4no+tK2U3BOjN1gdGjeBGdNYAuiuVd89+PlepJriMZQHmPXnmk4uMaWoz/2pH5Q7yQTbmU6fsCujqFKRX8dEH4gX3x190nrNzK7/vZ9/L3KH5lmJ+FFPW+94A8D'
        b'Ks9mOrzS9Y1F8YBeeeWs2fO/+sOz2ofMuXULLYo4FUsOZnSIHEJ+97esv3Yfe2vFzbxHh5aWVy53fxy18M0/bKz37jzMaXD+cF/Fe7yGMtgk/XT2YeEPfb+L7xNs/PzN'
        b'jPe6l15rWXdtz05hx7LVe1c/fU/yVtZzc5/0Dw2u/GNG8TJTvjG9ra0dXNAn1m9d0zc8HsN2xIZ/Ol7EnaokHXQJei8YvAjvsQ1n1hELLbgAezBSIE0G9rO08qhHuUIp'
        b'G14Au8BuekeYzBhVIralgzuCMeb0XnDWgexNSwO9C3QwhuPhUWYY7C4jtmInuBFuIaZ+YucHh+EtbOvfDrcRA++UaNCisVpjkzU8Y4mt1t1gF1mVAFfgRlRivCoBz68Z'
        b'vTABzoMON2JFjjVcjs3n8Fb4KAs6bIfHap5j0EsRuDCVnlMIIuAheBlek5BFlgy8zxqvugj0qWyw2QC97Sfhrl/YREJAAK20+sZoXMRlGpSL5imUh7fMQ1YmK5Pzj9f2'
        b'1CrdI1TuEQTEkMRGb9y/jg5sIXcbsPFX2PgTBMQZSod0lUO6gpOu9gzCCIhumtwjYdgTB2wEChsByZ6hdMhUOWQqOJl49m0jK5AVyLnHF/YsVLqFqdzCCEii5mmv0BEy'
        b'5FYDJNw3uT1N6TBD5TBDwZmB5qRdGR0Zh4WdQnSTkfamlXvj98fL0BO9FDZedMB3pUOSyiFJwUl66uRKsv6HD3bjn3LpdlG6hajcQn7GbR5euHawsRN9xgdsvIitYzia'
        b'SMNlnFzByVWcXMPJ9Z921h4O1TjGYXuStucjDVWCI4zrhvvOncJg5JMQ3L90+ovtDsE703uMYqmb5omGPwcqchjscFh1ngxDb6SutBB6RaiudLAOacVdq/1OAML4c6Ei'
        b'K2neTIt1FOqX524O5u7YMHcuY7gjSuMIb/8O+qFWsX55nvB6lg74oSvNk1aPHVdhPx9Wk12MVO2X52cR4ufrYRDEues1fDnSfOko6/8WT5VanpDW/fI8leA6UjC0deQ7'
        b'oq2XjEX4lPynLajVkl+eu/LRLeiAzes66vV/1HhGxVpF++X5qRzPD2q5YYVdhx8+kyxn0Asbwz7dOWUsHTaR7kk7de9DyQEjHQwIfWI/wGH1jFqMW0xaTLH9oMW8wnQY'
        b'EWIsFvcvjwhRyWd+o2c9gQUhsbwcR3etFa3QlRH0Tr1UnNdUNN+jM2MrT0l5OZrdoDlSiWa6TMK14vh3AbzKhrqmetrQU8Irq6spFdeW4Hiy40giYfUbRo/1C+D56YLd'
        b'omOCoosyldbVLcWsYmMUmdDRbDSurP8ZRo/hB8XyCupq8NSZtlnhOIAa0NmS0romOnotlgxR+WR1g/+l1TXwRLhKysUVFWiqh3omehI6ulCa+iYRbVG1VWqiHE4w/8P/'
        b'0Jy2rKSWTGlfZM8IidSZxfN86+pJtN7qyefzuvVKz1XHdRI838TSBlFZVW1TbaVEY9wgsQ4nZHREDiQScWUtEYVAUic6hDXxo3li3VKJ0TwfzeknpKqdv4eQRo6MGZ7G'
        b'4yeF8AOwlZFXLiptxM9BOcrQDFuMD8omszwQqRST+yWiRlJ30TEvITNpGOGCWDXHvipikST2pWUO8Spu1BCg652cGTaD+BbUVVdj00cdn+fnV4NtS6g4K/38JjVSkRKP'
        b'okifGiE5A1VvrSAoHY1ItT+HNI3lq7Fk1ElIgTX4vi91P3456bt1X9dAXvawkYa8vnWlS0RljTzSghO/AwW50ZHBIRqLMjYY029n4MuxMQqxJHaMsWx5nbhMNCzwSaJq'
        b'UWUFzsfnzQ8JXfgyJEM1zdgkoosjriWM4rc+JSU7e+5cXLKJIlzjf/UlK2tIfGxRAx4GA3g1qJ6HTUI6DIW+mCFN82DspNHthc+MNhDSb0uQ9k2ZkC1ayUtChcTvPqaB'
        b'Hh8WPOnjR2HEaM2lOq8JOoveyFqJmGaqrmLCp5aUL0GSQeoD30CChJc0498T940TG1pHEZEQS7G4rKpRXImLIimrqoa3UU9ezR//zk5KU8BDclPQKGpCneswASTBYp6m'
        b'ilAPVYPeuNQiQWFJY6kIW9/LJ6GExIUObFvdVLNUVDVx/Qt4YWOykaeVNFWsamoUoZGjthyJ66y6BglhahIa4bG8xKaKKlFpE3710A2JTY11eHxbOskNEbG8jNpy8XIx'
        b'EubqanRDUY2kpHGVZEzJJ7k7ciKWf34FRU1ERqzDVs3PYyt6Ino/r15iSEWOVP1P1PyEJwtpScZm8jF8/2xJ1C1+RQMqjS+u22GeSkpXNVXyJxc/3dt5UV6TC+CojCEx'
        b'k+VEYlYbVDK5SI0mEzkZmcgXkUFCMVy+F9CI1s02adFiRhGboFyTDmgaDCvUw2l+EX0A6aSob9V25b4F9Bg76YA9ApEVy0tGBzz6COk4vkJ0KKpF/5GY8/AYFD1pl6sD'
        b'rjWaTOgYMqEvJENwuOghY1ZioSAjhedbVNCIvvF4EzHpbcO4XfStqUWkp8YneL7oJdeIOGr2yauhqQGpyGVotEjW/Arg6eh2qUX5PN/ZsKeqAb2kiJfwyVnRgQwbITZ8'
        b'WsOUlpRkaVODZDxTL1L3JlMviSr58prfsIqWOGrF6+V0GAKCFsvLwV+8+aHBC1/+tlD6tlBy2+StoUVX06iQmmM8NX+RHBDoNXQL/kIZx+ebvBdLFzU01AalNZQ0oaQ6'
        b'MChNjLS7yXstkn3yvgrTmbx/wg+YvIN60ZNRr5RahZQw1PdP3jUR3pDOVj4xG5NVHtJiRaJGrFngb6RgRb5Qvyuta47l4Y0YSH+qwForOoHqfPJGxTdhTDv6rpJqHj54'
        b'4R1l4kb8QqL0heoeDeSHc9I/COEArKcLwkIiI5GkTc4TxtBDDOGvF0pkRQkqbRrqVF6UiaDwoRbCX7z5kZNn1HRzmi7uRRKtxQeM5SWhX7QmPD806oX5h19tcsvoFe0X'
        b'1rcWdVBzJ90+k3fWGGsQqWhJiTmoeSbvEUvFZYhgRjJ69ARv5KhVZUNq0lXlN1KY1BU9sgqQdc/ahfYigwccwTnhMBpTursGjwn21lXj1YfbC9jUg3REMWGx6VUxjQ50'
        b'A7bCk0ItRFRgGOgC+5rJI/TK7aj9QQtwHJU190IiaDyYReCiBWzHuFEYuo0KBBfKaDSbzbC7FLZUCscA8cFW0E+oRSSuZezP/5seFVziuCQuhGrCsSxC6rL9Ud5MHLkT'
        b'u+yA3sxsOnIAxl/YkQ8umVHN4UaVYG8QAanJl+QwH+hTvseXl9j8YY6502Z64Rv0VMH+8UECloA7BYRYOr3kNkt36XsXOGzKNwd3ybKM+MMpHzMlZgyK8ju26+Teezkw'
        b'wfTXNZ/sC8+umjtl8Qb7hN44PWfLW691uRf9pcVh62bG9l9Nuen2e+PjAWszOmU9K4quz/vb06nvf/XD5z88upto88ObJqG/35oBvNTzQy48SKwx9Nzb9pbRc7cZZoxq'
        b'+YUvDvw9peP0zn/m6JtPF8+/UFJcr5L9re/C2u+N533cdPazi58kr9PbIdw99XHl0c9m1njOs2BHObz11iu/Dt/jnLv9q09ZwidtD75N3OKVGRn1P29Zf5FV6Xqr8l/z'
        b'XaavWPR5eK7zlsbZbow/s/dNkwOLP15pn/qm9R+cA3Lednv72n6TvtdtP72VkXErbmvrH0/fZ/5x41Tff/3DRfnux8FTK3Nvflq8wO2vP771lLrz+nQBT8hem8U3pFFT'
        b'rjvGa+FDmnPpqKwGKbRb1U4fcJ4ghhHsECgFu8ElcA3soyPf3Ytz8ofbczNALxu0mFP61Uz3GHiZOBg5gT3gDl4z9isatWrMNoRnwGmyiApvYQA0ehVVZwnVPHP8Iuom'
        b'cICObncJHoLaqAQjMQnM4S5NWIKsLLLInAg2wQMSLA4AkfElcSH2YHerNhboA8diCDIK2OrqIszKYMSAkxQzn+EHLsHrfItfMii5BTUKDmSM87bpsFlciwhyUbN6m+dC'
        b'8QIUrsHyZThwnaO0UUEC16kdccQgW77ax1dqSgNKe8qW9wT0sZT24Sr7cHyxiKH28Zc1YnebPpu+8v7IK9X3w+4n3Q9TRc54HJk9EJn9sEwZma+KzFcKClSCAoVPoZQt'
        b'nXXYVO3oKtPvjFM5BrSltKWobV1kngpbb/TRPNVf7eMnxbm6YjtiD8cN5/wzXhmdrnRIUDkkKDgJOPrtAnmMwi6ijaW2sZOWq1wCFTb4owmSoHL0V9oHqOwD+vQG7CMU'
        b'9hFPXPwU/jlKl1yVS66CmzvEZNmGqINj+oz6PRXBqfdtUEJ/sAeSr9xGyRUouILvnjh6YrZCRhK1i7+0Rp6sdAlWuQQruMF4GXSIhS7gbzbLSqDmCNpSVBxPWYEK+98I'
        b'FJwI9Olj09/Dn++e2PMwqopgJFE7+EgFcpbSIUDlEKDgBGhIWwnQtyQYCybbKtmOgnbGycEsyDNJ9mdBfz38O5ybYk49MDdO8WU94JqkeLAeeOih3/RqsQW9WjyywIFR'
        b'234WNsAYYRtZLn6hsC3By8UyagQAeaYjg4Er8ZdKfjFnmL9QE4TfIWMmCb/D1oQw02uhWvQ1MR3+18KYNfyVGhMW2XWCAd2LHtAzXPUow/IpBmhsDthZWU3vTAfda+EJ'
        b'SdPMiGDUr17AEH6oC2OsnQ37RnAF4E0DuMEENRg8z5hNzW4ErWRgd/cyLwD9BhHBNPDfLQpeiQbnyKM6mGsY3xkvZ6CheP7D5nCKeJjDrpWlYcFTwvUpggDQWEuG+5l8'
        b'2BsGOkPDUbViwABwajYhkYzymVYv00e6gWnI4kzaiX9wrRXF4xSwqPrF1f/IqaB9w7+biU4WKih0MiDKRI/OaT7NlOKWW+lReYtN+5Nq6JyHfdHJuBMsdDIr2pRP53wz'
        b'1YTiBP/VgLJcXM1iudI571HGFCfdl4lOmv7Txog+ec0JscR73QCHfWtc00SDp8OjaHi6XgDb4Km8vDzUSCkU2JCKqogMXi3gBGwLcwC7goMx+insoeAGpITcoRGKI0wK'
        b'8iiMFPYqpYd0qA3wnITQXDm7TAM1cBzexnADBGuAWUdDKRyznkagBhielCXsBvtgpzEdm6MF3oInMfL/OnDHjXIDUjvasb4Lbk4OYxOH2I2hVGgVbCPNWl0+D4MHUGB/'
        b'hoASwM2ghwaAvTgXbIPt8OBaGixAixQAtibTBd4Hd8EDBfBMTB4PAy5ettUHx8HGKFo/7EtG2p4GMQDcheu1gZDqF9LO/ARDOsmQsvT8lIX6ioBglyS6cue7oJN5IgY6'
        b'aWoW1kzjDa6xYhfgSqXgJgqcAsdKeGATIbE9yJbyrfLGeuaagcQUWpbhSXAPHi1AA+3tPCDjU1TsWhN4HOmNnUReq3Nhj6QeHjcLQ5XHBGcpeAfurhCvPH2GQTYttb82'
        b'82ThDaSYWR5d+P4NJx/Pp/V6dzftmy571fEN9/CZf+luMkjt4YS3mN9o+LCrvPqDouVXvUN6RfOnvn5kdfznuc0bOdbp7/56YcLaUP2t7b+b//AP025/PeNgg7nj/KHO'
        b'cOPT34BrJakGB3ZXZ7+vso77cJvAMCGw96pJ/ewT3/9xTsXhRsWjao8naZ/MmD+0xeP0lxLRyteU80OfvyHc5r7Ca/rD7cXpX4W+3eIsX2a1MSiCeSJtxm9S7P+06/V9'
        b'uYZHWYbTzI5fcM/z/OMrPWcaWR8nQNNd0iezpPNq6+WlkYUe3Ut2OjR/KMrqPHblD1GD02Z+8a/WiKptW9oXdm3eFxp9Jvf5P2NfFfNXc3yiXytY9dtHne0nS956x7Jq'
        b'698vv7vIpWxn/cE3r8xLS/vx7SL+N7+uYlULbge/3bX4TOMjdu/djlcPuHMzit9c23Q6dfnJv9su+nGd8YoiF+G//in3eztCJb6z8qMfvZ/9uK9u5hfCwU3X39HfbGC4'
        b'6B7D+s8tq9fW8DlECQM7jKF8vBI2ooJZw06NFhYE1tM++1J4Q+JPtgMixewM0tIM4S0m2FsJdxN9stEKnPf3Bacys7MYFNuNAY6C/VBGO42fZMENdPwniPRIoSb+E+hm'
        b'0IAC/TwG3JEVMQo8zwP2kK171YtAy1joWOyzzkvVS8wyqoZtNKpdXSjYATbCg9r9gQwkjPAq7WXeBa+AU8NAALArjUTLA6+upHdC7kevYavuVkgPRw0OAN4CS8o2zXiB'
        b'DlhBgLX+K0z3mjLi4A/ugT7jsSAB8CS8QO9sfBUe1YAmoHMycDYYrB+B5FsC75CNh2V5oFs4CiHA3MYYbGIlwRtxdETmk6ADbtYFCLDwBmcJsN1G2EtoLEK67w6hLkCA'
        b'Odg+Yy0rBZyIJbs5TeCGuFHoAOjWTfT+xvQ4ovaDDYEYRAKuzx7eR8kAx5aCHeRqDjiYoA3TdSBJG6arEZwhtegMXwVbx8I+zCmj91fuqqCrqms62Kxb0SM7RcGRAHiB'
        b'N4tv+NJ6D+6ReDzdTXJfUziCz4jCIykuF5c1Eg3bQuOan+9KTXFs08MhnE3UPE8VL5iGw1LyYlS8mCHK3Yr/DCdt6XTIrubD0zqnDYcJI7GmbQ/P65wndzu8qC3taVAU'
        b'jhN2el3vurZUqa9sltLBX8kJeMpxfczxHuB4yxpOreheoeY6qrkuMrvDFoiGiivosxnghiu40/o5Cm7qfQ4dAKawZ24fQ8kNVXFDH3OjB7jR/VZK7lQVgeHqtHjMFQxw'
        b'BfISJTdYxQ3us0Yqvo2KG4GvmWtChM2k4fz6mDgAmYobTvvqpaucQiai2p/Un9yfrOImaLJ1Ziu5fiqu32Nu8AAXAwUQrDINUAA3ehTjCf32Cm7m/bTxJ6vup6tSih6n'
        b'LBpIWaQorlSmVKlSql46m7O2Jhb1ocJEqbhRj7nTBlA9oWInEFZdZDbob85x5x5nJQ6Q5kyqduSDSpLSmXHYvNNc1iBnyBpQgV58wUXNdUX8DUU4Bts9oxx97Z/j5NtI'
        b'iuuyb7m0Smnvo7L3eRblaMvH2HZ8jGiH5AP/iqZc3buqOqpkq5UuYSqXMCRONtwhysQq8qmn96kZ3TNe3DauL25WUg8qL4xkwI1VcWMfcxMGuBjJQAP0NyJQWrkasjIS'
        b'oCIYeaEioORb61FFkPs/szHyikRC6r03e4hDcZ3bTMcHzHrx1lQSMOunX7eP8ByjidK40qe6/i970efh6dRz3KXqBp7Vp3Tjwulpwn+wNf5/OACt/nDoj7Gxgv4rITwb'
        b'vqXGzCEmihdkkEPMaUBmCW75pyP1Lg/ssU5HAzAaYsHpwnRwDrYEBPL1qXS41aAeHAIyogBngnPhsB0ND60B1Gq4nmJVM1BXvw9eJzOC1eCYGClhF/zRE5upZs/FRF9d'
        b'Bm+k+OcyKUY+5YfGrA54SV/sE/eEkjyj8Lb3jF0zb2FHhyvtd4GkdKPZ8gf3XYcMnGXW1Ye5XMpoa3liwN45VktfDfyfDNP8HfnuV3eHPrgrWfNJ5XNm++fHTXc8NfJo'
        b'eGRf9EX4iuhes0+iw7b/+VwbvPxdkdfNdxw7dputXdtwM/WbAdXjtLeiHX8I3vdOReYU6UPDN7Kl7a3d+d0zN2R3/Dj3V7W3vU6F/27Bcdv4raWtn2zm+82wcrFJWtHx'
        b'g0d6+pOFy9f23lu4uyroTmT65t9nPj6Z3yBYXvHXH9blv/mOgPXtHbaz/L75muq/9Uae+uexm+3bvuTY1RsHSm5+/iisn5eUNreh+etlOe+9b3AlrfT6DL7Fc010hTNw'
        b'I6l5qimUYkcxwHnWPBo7qNUZg4YH5BB1CUP67mAiTaBnLewQkfHeAl5aTq5vx6BA4AjoymE6+cBuopFMKdTD6khAYAZKuBImGpv7mPA23J9K+11cAGfAHaSWXVlBDF01'
        b'+kzKCJxighPgTjXRxZDO0tYkDMBoONuzAmeiwdwkgYkUtH5wi463udkX3MSPCMoVoMcHWLzC9IPX4XmafA/cAi8NRxVlu2qDiqJpzT5aWTnk0YyYz4C7kJanj+ZIWxcx'
        b'PczhGdo4eCcz0p8A9ggCi7z5TFTULhbYMjWf3Do3Gul3WBcKytGj9P3gnjimPTbekVtrVsHTwmGpNeIw4RVnNI85H0sXaheQ4egtcJem1uAJcCqJyU2DJ2ktcj04vUCL'
        b'SsVyqab1RNAH5DTTSDeDl/w1UEL6s0OAnBkAr0/5j2F9tZYVutszJACMw92epGQ5HWi0W2PEy3SjOHb7ow7F74uXedK+FtiWFCNP6p1xIftMdr+nMmC6KmA6OXk/6fVM'
        b'kPmwUZlSqEopJKeeOLgp3KOUDtEqh2gFJxoDr5p2mOKxC+ktNvaHYvfF7o3bH/fYxnfAxldup7QJVtkE4yCf/moHN6mPzFPOki9QOsSqHGLbktXe/qeWdi89XtNTM2Iw'
        b'O2wsZUvL0SiCCcsK5eH0+KMgHzXH/lDGvoy9GhzLNuFTR+fOqK74jni5p9IxSOUYhGn4qLkOXYYdhjIOZkxqPuo5TFt/kmie4+wmLZS59/icCugOkDf2FSrdY1Xusf0p'
        b'SudElXMiojbF/36+2smlK70jXVZ4OKczR5ozxEJnySWSPMPJc2rUuYkSbJ6b6PQQS8uTBE/CX7O1S43Sey2KnTrV6LV4BkrpcdCIHge/+cnBkBYPvHQxbHebVDhc2Sjr'
        b'ekqLzrma95OBUv9LcVNJJEk+e4xnNn1Iis8kv3P41mPBZowZlC7izEt4uZxhkOjfjaIaCQ0Z87W2dvhWv6ClXacxcPWvH/uPbpQLuFGGHe/dsILyNnM0tAybbWaJ0U8s'
        b'h0wpc9uW2TKWLFm6sq/sfsFDm/sZ6ilOMv9+m/6CfqOHyUg0zWdiRCSUPifpkD4Vn8AYYvlgFJqfTJ7p6dzJxmfzGaMwZyIx5kw0xpyJxpgz0QRzxtFD6qu2xIFOadQa'
        b'R4xa44hRaxwjW4RjMGciMOZMFMacicKYM1EEc8bGsQ1RIKhMnBCUwSYMZbAJe46TluQxGeJxhgQGzpHAeE5Skkf3KcH4KaH4KaH4KaHjoG8myGBIahe9iebZDKmkz4b+'
        b'RacY5KlRmiJNkU1RuUX1G6nckh67pQ+4pSvdMlVumUonocpJqHZxl5bLYlQeMf3eKo/Exx4zBjxmKD0yVB4ZSpdMlUvmMxbDWYibh5uFKxml6OUffsaQfhPDTDBE/TLp'
        b'MwNM87ku5VpWjJnzEPXTyXIGqQqph8LMRWnmojJzGWJyzFAn9ZPJMxZl7jo+v05g9J0zwM1UcEwybNzRo8wcmLA9FNzhM3LE3335ASWZh16KtX6MtXveytmUZ7nlk4Yb'
        b'9fz/Cao5/s2pa47vP9g1dXZgtveDBw+2RCotb4Vkc+tr1uQyWJFrMwwyxacveto/7JTcjfl2tcNv1DuLql9b3rvu6dk/r2ds7woPY/T96fLavLg3/vnD931FSsPl1k4x'
        b'ok9viz65/WXK1/cKv0wt6jrQ+ZkoghF9491Wzr0vfH98vNf3PQPH67cP/Tb/y5V/UU3pAjGDeyO73rbn/W3rjpOx6ZF/faPst7dub4tKNL96esZaB0VbWvir6yvCLRY2'
        b'Po59R/896jOXt9cOHAcfzyvzD5OWf57u77tg9vH7kWePWjzs//HVm8lLZq069M0fXRd6229JbrBvd/job7+uVT70n/qP8JNhsaeEA+Em0z4Pq8yr2/vs3cIVxUbP9+WU'
        b'hyz80+bB26v7l+ffUp+Q3rt3Idfm0uG/ftBy+sPYiKuPalf6n/38zwdurG9fGZTzO/fPj7/9j6fl/qw/mXe+XvzbnKYNslA+iyw1WnsZgz3wCtyRxaAY0RTc7QXbiAoG'
        b'WsEV12HXWrGtzjLpER695HkQ7AdXRi15mop1A7G3FfM9x/aEhi9M/hv97r/RU3vSWlUC+Teuyx7TeQ8aFhdX15WUFxevGv5F1K3fs4a9HlH/HU6Z2Q6xDYzs1RbWLZK2'
        b'0O0rdq6QurWuaVkjlUglslBZSU/E4VWdq+QzO9ZJ1/V5or+GfrcrTf0zrzRfDLwSeD/lfspD61+lP0gfCM1ShGY94TpIQ6UlnRGHjTqNZJlKbmCfvZIbrYjLUdrnKPIL'
        b'FUWzVPmzB+xnK+xnP7Hjyaz31u6vVVh6DrEo7hzGkDFlzWlL3G/bktSS9N2QAcMog6G2dm0TnDRVCNKUvBkq3gyldbrKOl1hmo51lmgrI88h6hdJfH2MUO/0c5NnOHk+'
        b'cq6QEWfkMES9KGmb9Qx/PR85+wrDE/98USK1e4a/no+czWFQxpZDzAa2EerG/l9Mn5H0Of2bhZjdaadht9GI4nrLTZT2YS2mQ/qGRkhdmyyxa2AZOSF6/9X0GUmf655f'
        b'YkBqN5+U5v9++oykz+nf2rocm0mC/fpaE6cn2VDAxiFJoFk0dx5kFhf/m4vk/52ODHfki0dv85hI/bRiYvVT23nhiazkE0pjHwthMCyxkv//XvKL+XrjSfQ5o0QW9SuW'
        b'eaIVSxw78ys9CQ78dl0tqdkVY8xMtExdXfxrvZR6qLcg5yNb/ZC//Nb09Sx53Z9Ll5R/4OWcVsj2/8c38h+XuMp/s5MjDi1/Y++phL2tZ31F/H3RrZnv9XwXZvD1k6+a'
        b'PnwmdhZ51X3fVXDGVfjOwVXta9aGOx25skB1uv03x4okYfyPHsYbmJv9ofAjuyPvVTzpEx59T+Sjxwk3DZhXX3XCZM96l++5i1usfi1d3NoSY+fb98B4afXy9oEu5h8u'
        b'P2ntX8e83x+8LrqZb0Gbf27Zw8Nwx4JpcHsu3uK2U2hAmYBLTCgPiqYXbA7Bs7nCXAG8iHPkWsGTAhw06jYLHAc7E0kWT9ALpWAHUhD2CKeADWiMx2twBpS5NcvFr4je'
        b'otUPe6OEGcZF2X7ZBpQ+m2kItmkWvMBtuBfegjuCQAeQ61OMAgqegFuLn2MtkBcKbvtnWsJOPYohpNBDjnnSINN716wRws0GGdlwN3ocBko24TNhGzwBLhMLy4JEtgS2'
        b'2ulcN85ggj541oBeSNugvwyvMNmmCzSrUOawlZUDbs4n3LrlgWPaLYdpUMoAXWAT6KNNOycdLMHZEHARtgaka0xmpjZMeKUkl6wewdOwC7aBHStBN8pRr8lhDC4zwRUg'
        b'LyKrRz6VePEIXjIFLSuWNcHL4HbCMtNlTQzKHu5hgZ3wsD9hMvkVcFzouIKAm+OCUKhhOpiwu9n1OdY8Yjl43RPsCRIK/HAp4R6MCo7PGFCOnmzE8ck0vu9L61T/T6pY'
        b'On2UL1G2ErT/XqBujYKaMByFLlLC0EGYwN2WA6Vnsz4H/6nNOI/NXAbMXI42K818VWa+69PUbONtWRuzFFZuJ6OV7AAVO0DBDlCzzdZn4D+dH66K0R8120cx0UfNFigm'
        b'+qjZHorRnyH9eZZ6aBj5/ypt5lGmnPW5OusxroOsalHtIBt7Vg/qNTbVV4sG2dViSeMgGy+xDLLr6tFllqSxYVCvdGWjSDLILq2rqx5kiWsbB/Uq0ECDvhqwI8agHvGB'
        b'HmSVVTUMsuoaygf1K8TVjSJ0UFNSP8haJa4f1CuRlInFg6wqUTPKgsgbiyVaMLtB/fqm0mpx2aABjRsoGTSRVIkrGotFDQ11DYNm9SUNElGxWFKHfUUHzZpqy6pKxLWi'
        b'8mJRc9mgUXGxRIS4Ly4e1Kd9K0eGbwl+6xe/6B+PNyKPJDHGtwlGieIE/5B0WjEY5Sw8iP3/nP5i4y/Wpn5lbJTIo37FM08MZH1vWIGdv8uqAgcti4s1vzXKyfcOmmNe'
        b'fUnZ0pJKkQY5sqRcVJ7DNySGwEGD4uKS6mqki5GWwabCQWMkLQ2NkhXixqpB/eq6spJqyaBpPvZDrRGlYklpSGBqhJsWc9yy3xvG1dSVN1WL4hvSmDTohGQtSoZYDAYD'
        b'l5k9ROHEnDIxW28wxK62ZHCGKJ10kRtlZPXY0HHA0FGaqTT0URn6DFFMRoQiIP6+933vX/k+8FUEZKKP2tBSbWzXEqCwD1Mah6uMwxXscDVlqaAs27hKykFFOSi0H8Le'
        b'/wHfS3Ox'
    ))))
