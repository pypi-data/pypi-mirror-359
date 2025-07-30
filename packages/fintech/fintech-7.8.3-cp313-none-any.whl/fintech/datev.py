
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
        b'eJzsfWlAk1e68JsVSFgCCRBWg6wBEsK+uQGK7KAhat0gQIDUEDCLu61rRXEBV7Au4IpVK+5otdpztNN2Or2ktAVpZ25n7W2/mbnUOuPcztzpd855kxAE7LQz371/PltO'
        b'zr4+59nOc877a8rhH8v6+80q5ByglJSBiqMMDCXDnzIwF7PmulBj/imZyQzaF2WNUfNRLGsxZzKVbI3JRH81qGwOczF3MqVk20poGIudJlOL7TVIqDqOS72U++163sys'
        b'8lnzJA2NNWadRtJYKzHVayRlq031jXpJrlZv0lTXS5rU1cvUdRo5j1derzXa8tZoarV6jVFSa9ZXm7SNeqNEra+RVOvURqPGyDM1SqoNGrVJI6EbqFGb1BLNqup6tb5O'
        b'I6nV6jRGOa860GF8QeiPj6fkA+QspZYyljKXspayl3KWcpc6LXVe6rKUt5S/1HWp21L3pR5LBUs9l3otFS4VLfVe6rPUd6l4qd9S/6UBSwMPUKoAla/KS+WsclK5qdgq'
        b'DxVPJVS5qlxU3ipKxVIJVCIVR+Wu8lP5qPgqsYqrYqoYKn9VoMozKQgvwIvO+qDygJFJ1QcHU6qgkbAqeMQvobKCsoLDqJBxYmupqaxJVC3DZYuUWVLtuJT+6E+Ih8om'
        b'q19HSXklOmfkr3Rhll1nEJ/ui3UBlDkMeeHG+SGwBW4vLZoDm+GuUincla8qk3FzwFUqchYb3oN7K6UMcwDKWg/uvmzML4a74c5iuJNB8fKZoDMa9MgB6oPZG+UAXbPX'
        b'F+bH5nNAM2ih2GwGOM5LJ2XBWXhgCU6Swe2oOIdyhztYL4DXSlxUqCxeqULYHQZa4I7YJtSdnfkcigeuMpcVgWtwh49Zgnt6QxqLMlxxBc0rl5vh1eWzE12XmxmUL9zD'
        b'AjsbhKiXk3G2Y3PBftAC9sQVNnjLonFv4R4cdqICwthgs/P0aobDbAXYZms/cqb5L0UzhpaRjRaRQovnhBbaBS0xHy2xG1pWD7TAnmj5hWiZvdES+6Il9kPLG6AKTAqw'
        b'Li+j3MlheZloeRkOy8sctZCMLCZZ3jGx9uWte3Z5fccsbxC9vCm5XMq15iSLklTG6rQNFIn8bgqLYlPfcdCaF52seZmOdJ3qTAma3uNQlZWxPY3+dOTcZA7lPGOASc2o'
        b'LEqriabOUToeihbEidlPvKgZw9VfSB4zb8TDqqWUDiOQ4XXtjB4nSqLwe93wNGGf6iwd/YHyG4/9HoyoYWr6nPfFYZVvUkOUWYbX5d58eBAtbUvcnKgouCMuTwZ3gHPl'
        b'UQXFcE+sPF82b1JBMYPSe7hMBR1eo5aIbxuxCS8R37pEnFHLQ+EFSuLbl4D9L1yC+meXwGnMEriWGPAc0pvg/PQy5VzZPCbFZFEKeBceBTcazV4oZT68CN9UMkEHuE1R'
        b'oVRohReJZsMd8KxyLrNhHdpj1KzVcLtZSOoBt9fAfaypaBniqDiwH14xC1A8E55Wwn0McyxFySiZ9GXSKLyomKosngN3cSjmWgbYXhAoglvNkSglBtV+CW+pGQExhWgv'
        b'bC+aEwXOxebhTU7J4TkO2ATPgDdIk/A12EuBq1zYW0hRU6gpYLendtm5Do7xE5Q4eCGkoe0NHlCIt5Z+WDiUuzwqzXmTKMs3teXVqy2FcmWk5+y3Hj56OL/pqXYdd9JP'
        b'Pkq53F777bvpX/zV492D0zs/ZEbHuLz5xRHVH7Z80LD75wG9cz/PTkpPmOF1QBu788Ykv7q5M4QPC4f+ckj2S0V8yWvbnT8P8nun79v5y+9e/G1D4J7Vd7osqy4+qpWH'
        b'L46eZyq++5sn0x99Kt17uTjj8c/aWHsOp5Y/vF1z6dN+z2zvP5kCYP3kr76EUz7hd7f3C5P/Q//6v1s+iATxm4tmFZV9ZXx5eubsNd9R934bVVB+W8p5MgmP/LYOthTC'
        b'XTFwV7GsAGEwygv2ssAp0Aa3wTulTzBSrYJHg2MKZLA5v6iEQ/HBZaahAB6FPXDXE4xF4BaFT4xcWhBDYzg87ZQH3MBqDJY+weSHBbZN4eOZNyOstCOOSXnC2yw09YfB'
        b'xYT6JxgFoqo64Xm0VjvgHrgTbdx0BkJfW8BleFItdRtiRkkNGAB+pGN0w6At2TDyb8hnSq2hcY1Gj0gmIcZyREg1K6YNuRk0+hqNocKgqW401BgwkDJxDUy0Lf+ygfp6'
        b'HYPy8W+P2Le4OfezwPDO2k8CZW3OrYxBobht6qBkcmtue/y+/Efekzo5ncYB7xiLd8ygJKLb+1LQuaAeY+/MfmmWRZI1Tq5HktDOWSd5DindnO6VfZGpA95pFu80a/KA'
        b'JMEiSehJ7GX1S6Y41mIa8I61eMeibF053ZyTBSc9HGtid9fbaxqUhJ9173LvXtEvSaHz/MY/tC8s+Ra7V/UG3xKW0+8/s0808+sgKkg+HEyJfA+ltaW15/YLQ/tcQ7/B'
        b'OMCAkYDUfYhLz9GQU0WFwayvqBjiV1RU6zRqvbkJxfzIlXJHTuWopTJ44kQvmzMd50pHzn9toJ6uZTAYoqcUcn7p7tuybAN/mMlhiB7xvVrSf8n22FI86OzxyFn4l685'
        b'FEdgC31rxPjqVW4MdZ6fwhqF3ezcI0G3nAPUYsw7Is5RyTCwlEwDG/1xFJSBi36dlCyDs5KnopIYSjZGvS8yDC4kxMEhA53CJX6MpBkqZhJL6UTCroRhYqOwMwm7KV0M'
        b'7nVMRPH4Q9y5ZFa/VKIulJCprmY5dJFtQ8D1uIsMmp87gKunSAM0FWCVOzCvejaiAiwHKsAehe9ZWWxCBcbETkwFWGOoAJsmxF/J2dT+eT4UpqSahLWU9s3e/2QY1Sil'
        b'0INztfrYewIQ+GCDS/aCBRtrpMLWh0egs/BnrHO1b5UHPdgt9Xmvkvex7/vd/A9/+mV985JGRU5UKP8dn4j2Zkaz03w/cIqhCedtXCx8sOvh9SLFGyLxhxtbE92oF7a7'
        b'ngezpFyCithZ8GpMoY35ieFSHuCMERxkrYlxeeKHaYKAj5Jl8A1rDhblGstyWgXOETwHXikF5woRGupcWIS4QSmXcgY7mKvA5eonYpzcPANxhYigFOaDiyELKYqbxvRb'
        b'DW5Yyy4H50BLKeL04E3QyqY48AgD3gabAmgcuQseqo2RgdPwXh7mEylneI0JMIZrl3Im3g8cG+Yi22DIuaJCq9ea0GbzoOFEbosgWKqSIlhq2MSkYhWXpp6b2utricmy'
        b'CKJa2ftd218cFIkPFbYVDojCLaLwzhf7RfE9WRZRMkJfwZOPL+tY1j25O769EeXlDwZNQj+8Xwh9rWU62R+LwodZlEhsENpxAHeIbdToaofYWAoZclqhMRiRwGLAVNng'
        b'Yx8CF2/pSryp6a2MWVVDKHIW4dQk5PwVbWWEYRkhP2AXf4Ph7QA3nDrNV7CqmeNtkRr7FqE3SBLTuj2Yo5gkVvAoFshxq6CNwMxike0xJnbi7WHvgMP2MMcgf3nWUj6C'
        b'gxZwD95E4NcSB/co82ALBrU5ZYRvmg67uJ7wBtylXVR2jGHMRoUu3Jxytfow2jkCIEZ754Kfn9jrv8TiEx3qyW/tfD8gxPW2ztX1zE7BS9GhZZH8Mx9IVhRdFvTKvbkf'
        b'uFLv/J1rUrVK2QT0wfmyMgTbReCm3AG2/eCtJ3gxwOlgcBheRRR8D9wjlzWBjlVWYu3/EhtsBbfhPrIHguFp+BoN5gTEV8/AQH43/QkesRcqfq+wVMagmCXgygpG1rSX'
        b'pUwHaMbLZANlRC3qNCatSdOAoNnLDs32OALQKVaAnokhr910fG3H2n5h9Gf+4X0RGb3lloisfv/sPlH2oG/AoTVtaw691PZSZ02/b0yfIMYBTDkGLO4NsfXqBs2zwMkh'
        b'wGmHTTl24pBTbYPNbzdQf85hMRjiHwqb+7ih1Em+nPW/jr7HyFHjwmc08sMDvvA6gdCx0FkJrtsBtI7Sps24zCbg+Tgs+Cr7Q4LaxwNQB/CsdhaWxfHP/ELANUs6Prjf'
        b'waAWNHDPrPxcyiKA9eK8FwtJa+BGkR064bH8J0S03RCe4QCcNGSGgUM0cMIu8CoN4ofAeW8EnOB6ig0+EXTC84FS1rOIlUVAcQQWjePAonEULMZbYbHke2AxFGHbQ7w2'
        b'XnvShwKJI7YkYGhQ4AY5K9Q68xhgfBZTpmInjcKykQOmLEbQOOkHQKMBy0LjY0gChSw7hsSCJZXE/p/BkpwxUMgpMePJyQfdYFsh3IiXsBw2y2TyOXkFKthcqqSltzwk'
        b'yMkZlAnedeGCZvgKDbo3yicEXQS3s5fTkAs6o7X8Cz9nGhtRmYtrH16t7kCAe+EBAl1Q894Diusv2BGy9dWNIYc9Y8B7aufapK1XlH454q1+U0R+4sfibL/sBZvaxYoN'
        b'yWUNvLLP5ovquTGfuZ4p4y5J4XK35H/mypMIBxXFzr96IOJvfCNrY8jRjYhDERzjf1XOQvJWMO7puZIX+eB1ePdZgQhcBEcqCK8AXkfjukfvBrQV1OAAvRuk8CYR2WKr'
        b'YsdsBrQTwKV1aDP4NdK8yqnaETwtLKN3QgLsJfskMAW2xMgIHwIvgBNWXiQGNn8vK2LnyIe45iYsMw25WbcLHSQ7ZSG9U75ewKLEkzvDutkDvjKLr+wzLGhM7/ef0Sea'
        b'8WmgpHUmQtudSWczuzI/9pV/Fizti552X2SJntUfnNsnzkVAHBQyzKU8vfFmGhCEWAQhnWEfCyIdtpQTvaXCsTN6Lzn024myonibLJGFHYy7GiirLIGQ/NP5GMkPUz8M'
        b'09N7y1FlM5r7YBGVDdGp2bE7o5z1/1JLNha7s0q0//b0Fywj7lFNeBThw9/v/DcxOIHg3geh7CK/kGvyGFZOcJ6b8MxhybzYbzuvKTar39vGY+VIy+ZvFKwI2DQY/zDb'
        b'T/3n38XPjtqScJ71wpsvuroicHcNuVDg2tW08pyi6QyDKgzmp5V9jfgNwhAfDtPZYRicXW3lpbeCHQRAU6bAbQg+18INDqgaHFE/wQuZnVAHW2JBB5UPd8m4FHcpMzR9'
        b'xROsAEwMhdswCy6FhzEXTvPgXmkIFP4B6RKDgkTiwE8j2dVoMiCk7z6C9HGYgPFiGoyH61lUwKR2n67Qzpqzy7qW9U9OsPgltHIHQyPPZnRlDIQmWkITPwlNbitEEC0O'
        b'PM7v4A+IpRaxtDusXxzXmoUkbixmI8AJS/maS4nDO+f1+8b2CWLH0oYJYZhQBgcQzsdOAXLMlJUyYHG4DoGw1w+BXkzSpKwhTgVh4Lm1Wo2uxmiIwLHMki//juBa6oFl'
        b'Dsw5oUniVVTQhxTI71pRsdys1llTPCoqarUGo0mn1Wv0jUj8J1TOuRphhLpGw+ohZ6tsQFduKKJscgBhuFLtuxKPa8gbL4LapK2uUJtMBm2V2aQxVlR8H2pyUBaIbQ4W'
        b'oo0ZeBlfoT4X+jZjjNOcN+jrhxwf/+bZg96+zblP2Vy3iD8JWG6xf+Kx3KRPeVy3qKcCjpvsMYUcskhmXNkssAe08wvwKcBNblwBg3J2ZVZmgRtjqBr+9w3GgdMY46gQ'
        b'WAaOkq3kKLlypoHrR71ATaaUTnM9qDH/lM62YyXbr8FZ6WJwqePRioJZesSdrP5yPUr4VjRTU6U1NRo0+rhCg6aG9n4pIAv5JUYE33rN0xjWmOuMTWqzsbperdNIElES'
        b'7u63rkUa0xqTRpJr0BpN55iGYhT55dtoC/ypwwtJ7o16U2NmCVpnSVRWjUFjNKJF1ZtWN0lUepPGoNfUN2j00kyHgLFOU4dck1pfM245vdoE7xh0ckkZAopGVHZeo0H/'
        b'j+Qbr7JlGgRykix9nbpKI80clZZZaDasqdKs0Wir6/VmfV3mLJWsCHcK/aqUJll+TYlBnpmlRxOmySxHnJ4uLmuZukYumW1Q16CqNDoj5v90pF29cUWjAdW8xtaGwZSp'
        b'NBnU8Lgms6zRaKpVV9cTj06jNa1R1+syS1EO0hyaeSP6XWN2KG4LVK3EvcM6R4m1IyhKLlloNqKGdQ6dl8RPmJKQWajR69fIJYWNBlR3UyOqTb9GTdrRWNvTSGbDOzqT'
        b'tk6yolE/Jq5Ka8ws1+g0tSgtW4OkpGW43ihrlNSWJpmtQbADT9WajHiUeErH5pbMLpJmzpIVq7U6x1Q6RpqZT8OJyTHNFifNzFWvckxAQWmmEqEN1EmNY4ItTpqZrdYv'
        b's005miMcHD1rOGYZhmFZibkBVYCiiuAprORdhmeNnn4UmZ+dVYLTNBpDLUKDyKucn59bLstpRGtjnXyyF7T6egRruB7rtOepzU0mGW4HYbkqubVNq3/UvI8Xj+d+1CAS'
        b'xgwiYewgEsYbRAI9iISRQSQ4DiJhnEEkTDSIBIfOJkwwiISJB5E4ZhCJYweRON4gEulBJI4MItFxEInjDCJxokEkOnQ2cYJBJE48iKQxg0gaO4ik8QaRRA8iaWQQSY6D'
        b'SBpnEEkTDSLJobNJEwwiaeJBJI8ZRPLYQSSPN4hkehDJI4NIdhxE8jiDSJ5oEMkOnU2eYBDJowYxshHRfjJoNbVqGj/ONpjh8dpGQwNCzIVmjOr0ZAwIG2uQSG0LNBkQ'
        b'QkbYT29sMmiq65sQvtajeISLTQaNCedA6VUataEKTRQKztRiFkUjo8ldltmICcoaxBBlzoen6g1o3oxG0gDGejSN1WkbtCZJlJX0SjMXounG+apQor4O58uFp3Q6bR2i'
        b'USaJVi8pVyO66FBASdYAp5SRwyjHykbIuGwh6gVCGFG4+KgEa3mUFD62QMLEBRLGLZAoyTaYTSh5bDmSnjRxhUnjVpg8cYFkUqBYTdNlMueIL0H8CYkzaVaZ7B6Eieze'
        b'RMesRns2eiGyNYgc1zlEhGcu1OrRauD1J+3gpDUoCpNehKVHBRNGBxH6URtNiNoZtLUmDDW16nrUf5RJX6NGndFXIbC1r7jJAE/VISDK19doV8gluTT9cAwljAoljgol'
        b'jQoljwqljAqljgqljQqlj25dMTo4ujfxo7sTP7o/8aM7FJ88DpsiiZprnVWjldGQjjBG4yVaeaXxkmzs00RpdlQ2Tnrp+K1hvmu8+FGs2MRjeE76RNzZD8mcMHHLo/i0'
        b'fyQbQpXjZRtFAlLGkICUsSQgZTwSkEKTgJQRbJziSAJSxiEBKRORgBQHVJ8yAQlImZiOpY4ZROrYQaSON4hUehCpI4NIdRxE6jiDSJ1oEKkOnU2dYBCpEw8ibcwg0sYO'
        b'Im28QaTRg0gbGUSa4yDSxhlE2kSDSHPobNoEg0ibeBDpYwaRPnYQ6eMNIp0eRPrIINIdB5E+ziDSJxpEukNn0ycYRPrEg0AIcoysoBhHWFCMKy0orOKCwoFNUYwSGBTj'
        b'SQyKCUUGhaNsoJhIaFCMGo+1i7kGTUONcTXCMg0IbxsbdSsQJ5GpnFWWJSPUymQ0aGoREdRjmjdudML40YnjRyeNH508fnTK+NGp40enjR+dPsFwFBihL9PDO021Jo1R'
        b'UlpWqrQycJiYG5s0SB6mmckRYu4QayPfDlGzNVXwDqb0z7ANdXS8lWuwhRJGhRIzy6zKFYfCY9Qu8WOjEsZGITFHh4VitQnzpRKlGVWnbtAgMqo2mY2YraVHI2lQ682I'
        b'vEjqNDSYInI4nhpA6lBEi4m7toYU+97M49Q/DlEav+6xGYmKaWR2JIj5llhZXjKVtTjdOsm0P8HBj2XCEU3VECOTKE9LzvEMJVg7VoqdMuzMoawHbYa52MFqwCGOsUmn'
        b'NdGqx3KsGGPQukOsW7PqDefZHKxTM2ba9IZSrDf0a84b5lI+cYPeUV87scXuzXmPeZRPwDBb4ZnDeFrFoDxE2zWtOS0vflPHSPTxb8mlFYdEEX4Z9oKLRmxit72sKBac'
        b'Y1POKcyXcsDe/wXVYb2UP8TLqq5uNOtNSEr58g6eG/dsBF+0iKNu0ui+9KYVh3h2v/WfiSCuAbExWD0uoYUstF+0CMuhLNjwdYiN2S3DUuT90x0UoWqguafGer1GomzU'
        b'6eLyEPrTywrXYGXOSHAEoWbOL1wooYthpR1G1Uat0UxH4DTHML3BZ2MdIy1M0A1lq2TK6nodvIMATYcYIMdgZrZGp6mrwQOhvVYNz4g/wSqMZdpmgggXmPvUWPGITUKU'
        b'0ByYVc4c0YhZJUwiF2DZEmVGO9lEZBBrDaQ5nRZlID6tvrZRIpNkGUy2rlhj8vW45DOROFvCeNkSxmRLHC9b4phsSeNlSxqTLXm8bMljsqWMly1lTLbU8bKljsmWNl42'
        b'xNCUKsvjUUQhvTCYsdaQyIQxkSggKdYg5GxT+0rMcsmI2hdF0rBs08PKJVg4sIn4tH53ZBklRTFFmblm/TJyJUNjqEPYcA3GYDg+WyVJSqdpeq0tC9Y/jxdvhRs6aZwK'
        b'MxcS2QMP3NCgxol2EBkvxQ4qExVLeF6x8RNpEHpOsfETaZB6TrHxE2kQe06x8RNpkHtOsfETaRB8TrHxE2mQfE6x8RNxsfTnFRs/kSy34rnrPX4qKfh8QJkYUuKfCyoT'
        b'pJKCzwWWCVJJweeCywSppOBzAWaCVFLwuSAzQSop+FygmSCVFHwu2EyQSgo+F3AmSCU7/rmQg1KVJninehkiXSsR8TURLnilRmvUZOYiEj+C/RA6VOt1aqzINL6orjeg'
        b'Wus0KIdegzmwEc2mlXJihJdlrsU6ODuSs9FSlIQx7whBlkRl6dfQ3Dc+PETIuFhrQqRRU4M4ELXpmeRn8PDYwiOY/Nk0gw7eMFrZhFEpeeQoqdaEuBK7DEcoiYzwO+MK'
        b'HNaRWqk5Iv2I0mB+vZZw6g2YwJs0WjQtJrtSOh+x1SZtrXaZ2hH7LyQyp11Z7chm0JKqw6GlI5uUq6HFGI22CicVoVXDp3BGmrOZmFFzVESjfqOW1TpzwzJNvU1rTogg'
        b'4eKwsTbNVhuqxueSNTYHs47GNBuXHOrAJacOektGc8lizylPE0Z45NSAERYZWzSBA/BUkbGoBO6OI2wy3FnoRMFL6d5VbFd4PXIUn+xm45N/hTo1TTSWT0acMXcyhVw+'
        b'/lOykCvEfzTvnO4UTAVTyskqjspNJbTZ4L/IsNnXGDjkjqeLP6XkKfnpTIMTCbuisBsJO5OwOwp7kLALCQtQ2JOEeSTshcJCEuaTsAiFvUnYlYR9UNiXhN1wT5KYSjG5'
        b'C+A+qvfC7/lzUfql88h4QlVM64jYSv9nRuQxekbQHw/9MZKY1lqc7L7RdQeku6Caw1S0bSC+ByhA9TspA5+pX6AMR3k4KmdyW9CL5Amy3onwRPGeaHTBZHRe9p4IlZPS'
        b'Gdb7hu4qjySOUoJz2OsUKkMMojonly3SiCHnmfhyTo5y3pe/RklrfHm2sIRGcPTtWN45jgGLTgZst/MltpgxaLEPG+MS4UTq+iUG4y+xcc+X2P5zJLvBYMtuMGJnGc6C'
        b'LwF+ia/gfemKSzsN8dQ1KxCeNFRoa4ZcqhG20puw111Ni1MVOsRumuqHnKvNaCPrq1cPOWPbfK1aR5u9DPGJjUxFA0Ii9SXVzg4wjZsiRlsbKJtFpuM1XXLtj4FWmK1y'
        b'QvNFX/rjJvGsFmXO5TwHizK0ZipnB4syl1G2Y85ZLsSibEys3aKsVso0n0RzxMunO69dozGS68v2WdcS445qfHM5A4k96gbJyMRkWC8mI9SGVV7Wm8/WGVLrTTxsfxWV'
        b'jTCQyYb/pHJJFs6PcFW1hBjGSsxNEoSxUyU12jqtySi3NWOf8/FboZPpFuwHNd/TRvKzbYxezAxJEfnFTcyOK7KlWhs20m1h+oQpA6Irckl5PaIVCC41EqO5SqepqUP9'
        b'G7cUbdVCC7GopESNiqAw3R+JrhHRKYNckm+SNJiRKFOlIaXU1s5XaUwrNfigWRJVo6lVm3UmKbknnjYyV1YgzJDkWH2SaqyZjLKfZzpoNKW2UjaAzZBYV99on1x87bzR'
        b'IImirWGWwTuGNUjQthW0GnhlECkKcxyoGL1G1j0apamTS5LjFbGS1HiFvZjDjsiQ5OKAhARw8VqtHkEZ6oNktUaNGo7Wa1biw9IVKfIkeXy0VM77HoNiV/pW0o61AgTj'
        b'VJqCO9eY/PIkyjwFRcI3vMEu2FIMLpTB5ny4qzAObi/DRsZ5RZMTpbAltkQGdsA9RXPywMW8kuLi/GIGBdtAp2ujPpvUumuRGyWmqChFrnC2NNaPMk/Fte4ErwY9W6t7'
        b'A6kX7obbixB1A9ufrXbLaldqCmgn1T4WuVCI4ioUKzhU4mIeZcaYwzeHWDbvjEkD+603WfPksugC1AB4nU2lLOYawWUGuYhLKgkI5FIIZwkU87aqPlm2lO4b6AAnpo83'
        b'YtiMqmyJxb3bKZ2HOha9ytY1cMvAB1cU8DWt9M5hjvE0qmZG4UtXf43vo/iBY5BiheycERx65CdnHggA48HOM2Xx4qD365O3bgxpw1bU3mcyurjtLhGvvicG7KRtfjAw'
        b'wtXYfrkdbqpxNwoiWVzF1o6fHmMNcG5sntrMb3mxfcmFeb8Vr7gc8ujhiz/tZniXqqsqyyqdaz1+9XBZZubhP6xbpfvi/q+UJWGfZv1u+f2fVTMefz4tlXp3eddwr/qO'
        b'iftBEnWhYNLPb8mkruTi6UvwJLwAWuKsF8IQzOIbXx7hrFq4yZuYUs+V54KW0iKHBWdQ/nVoPjaz16yHPaSW6Ap4l4+mXVpMzLXBeac4JuUNtrGd4bVVxKYbbJg3H1Xj'
        b'uMJUFKrJJ4TND51PrGFRWjPcFiOLAnvgmTwZk+KCw0wZ2AmPPkGwSS2BexaiGhwW1Qu8DvaDKyy07sfAqSci3JF5kTFyaUY53BFLofIXmIkLqScheBTgPNgBWvDdWftC'
        b'cimvFXC/hAXuvgx7n+C3LWbBawY8WJrLgsdhN+mpFRQQzMGtXHkiOPmEvI5wUwo68ZhaYqPlOBsqsQdxZhS4ANopiZHjRq0ibbuBy/A0zoj5Nty2DLUMDoE2+CoLbuXB'
        b'bnK9iAO6/UbatnF4/uAebAe9bNDiAfdKeT/ivigmnM/eFcWGpUOeNmo1+oachaJtelc4USH4VpzbYKislf2RQPJI6NNmbM/Y93K/MLI7pF8Y85l/WF94Xr9/fp8of3By'
        b'DMrrQedJ3/dSvzCi25Nc/kB5Zvf75/WJ8gZDpGeDu4L7Q+JRVneUtdWE7yPhrPbqUvv90/pEaYOTo8/Ku6sGQlItIan9IeljCtjrzu33n90nmv15ZDLuZNhgWBz+DRkM'
        b'CcVlBkPDW9kfj7pk4kYbEq/BzlrsrMMO1mcbXsIOMb99mXqerTHmryut/xxMjom57m7MDeFMGIV+hybyaakTg1HN+DOF3R96CbeLG09d5k9hjTKgZ9jQeCBB4ypqLjX2'
        b'XxiFGENGiZQxxK8Y4T2QsIJHT4QVifXC5BSduqGqRj3NASBsUZ4MGwBR7eUDQbIPg2hr32+thMtasY3JiEIEsEbWqNetlp5jDLFqGqt/VL/r6X7zKuzMzNhuG9qwsxc5'
        b'IhRJrpPhPh6vOFxB93AS3UO6inE6+KN6Vkf3zKNiNAv0vO75jp7C+A+D4ukOSp/LNv2ruupSYeNyntdJ/1FzuPTwUrqLftlqo8bOJv3TXaq1dcnGQj2vS0Eo0nAch0hX'
        b'Qidktv41nXKusLJnz+uTBK+lfZqWHF5i7duEDN0/2TfrRnCtcOABn9e/ULyMI7Am/zBIboW17+EbJ+in/aIM1nNMY1pv6ozcEv7X3tOp/Yfu6XQ8/jvLiO+zndybTN/6'
        b'7XxAX6ss8gtJKucI9f8JvW/PuADud3CpD7rZ07QBUiZhZEJgD9zrQIbBkSwrJUZUOLSS0HQZ3I+YQCsVdgEbHQkxJsLgFqL6E93XdarA+KCiYkjgQFlJDCGs+A4WvvNV'
        b'4EKJA9qTjk/rmNbvG31O2SMaiM+yxGf1y7Itvtl9guwxF3PHo0T0vVxMfWgguISdHuREMEbuu/w53+WH3XchSGAvdzJ1gi9jSXlDTla0RN9W4RpNBo3GNOTc1Gg0YVFp'
        b'iF2tNa0ecqLzrB7irlATeZ9fjQSyxgZaD8AyqeuGOI1o0xqq+Q7L625bXkwyp7HHf3gLQZyb9d6ls8oDyfc8DIEqAZL2XVROSe5WSOSXuztAoiuCRL4DJLqOgjl+liuB'
        b'xDGxjjfGzFMR0PGyamqMSKDEUlWNpgqjG/R/tdVWU6Ih10vI42RIoCXSqVpSb67TOAjdaKaMWiTkSuibQ1ieNmpMckkp2mw8jMca8CmctqGp0YBlf1u2arUeCbA4KxJ2'
        b'DZpqk261pGo1Rnw89Qq1VqfGVRL5EFvqGpHoXoP6hHAQ2tLWKqwyMa6Dh4qajVp9HcGc9mKSaLIo0WgEudbe1WNV0di2eVEmtaEOlamxITicX4I1ukYsbxqXm/Hoqwzq'
        b'6mUak1GawXtGV5AhyRpF3ySLyBn1Els2XFOGhNxeWfS9d1jspWhwzJAoya9kkdWC0p5uA9MMCdYfo6kh4v0iR4tJe14MyBmSHORKFpUaTCPxNGijJNpD6oiV5CtLZYnx'
        b'KSmSRVgnbM9Nwz8S8bPKZfkzJYusB6tLYhY53qgZqXxkm2AlBB2Q4IKOdtv27GgjocHWI1BB4GisNmibTFayg9cV31AjsJWlMzai9dbUEH0IWh6cilG+jjx/RyZbLplJ'
        b'K0UISE5WmtQNDfh2qn6yXT1CgAMtHGqgyQpaNVry4J4aTcNKLSIlmlVoxq0AJyetlTSaNDQYEeDWmOoba9DOqDM3oIVEbamXIQBEQKVBo6vWSBoR1SXl6C5ioCLaGyPd'
        b'ba3RoUm5JBdtOtuGIqUcwRDrdhCo4OcBq3VoAPTLgEYNnbPS+hhgYzXpCX3kM6XeZGoyZsTFrVy5kn7eSF6jiavR6zSrGhviaNYxTt3UFKdFi7FKXm9q0IXG2aqIi1co'
        b'EhMS4uNmxqcp4pOSFElpiUnxiuTUxPRplRXfq3nxKiEv0oG74DW4w1gkLZDJS2LzsWh8LtYVHEH0X8mph7fBZvIMWAW4De4mUnmwl6LiqXhw6wWixVC8wKbQ74L38itd'
        b'GeEayozPGuTKgkKbFDkHNuNXqwpkc/El77lR+Er0fCRmox9E08De+fAsuOQCDyCp+LgZXx7V1yfCq0gSx4LsGokTxYEdTNfKGvIcYEAV2Aaves+TI3E4H6tbUNX4SSwm'
        b'NQmcZqO+HoCXzNNQRthqQiLv1UK4s1gFW5tGD64MNpegcjsLVU1wZ0pZYWlRATzApuAOsIkPT80Hl2iLoG0Z4CBfLi0Ad8BxHugpoVwKmPB4PHzTjK9nwx5wDfX6aj6q'
        b'h0GxImaBQwywwROeNGOBG+yOepkPbrjB5jg53I7ajQXnCtAQmxmUZDaHHUM/rRa3Gl6HVzn6uGgGxcxjpKSsJHPqz3bCmqHKfw+vLLqmK6dIe3O8wDGj2yQpavM63abz'
        b'YubsBfAcaS8TMRMHjStz3eABNzc5bIPXi+DlGLiXRfmuZoELUxeRXPAMau8UX47Ko1nDj+DsYlHe8BYbHoXnPeCuRu2/+7zAMt5HWZdrZjW0FnttUrhu7T/I/O3ZVey3'
        b'd+nF83VHLDl9VwwPu0/GlJx8+idPge/1xIY3DyXl919dv+/QosdvfxG09fyBq0HnIiOT/mMHfDf/D53rNn3GXHS96t0FsV+923NM6fbBr1vqe2b63v029NLhvxxa77u0'
        b'a9vvguOjaguyXJQuBR1J7yg0nTulzN8WffzSlwpdxG/f8ZbmWJIK02cv+WXzdU1D6a/WfvfKwMBvXptTuTftyKnErku+2/70k9t/K1139NIZp44vnGLbg3X+N6VcotGR'
        b'6+C5Ed0S3MMKWU5USyLGE8wMwWZ1qh1SU+CNUaqWmEQO3APv1ZLHzxaDs/Md9EtW5RK12hn2zCPKoenR4IIja3eQOcLagaOwmdSyJgK+GVMiy88vLoyFu6QMygfeYa+c'
        b'mgDvgpvk5jS8Mj+oMDYqD/WBIa+knMF55uo4uEUq+GeeVhtXKYOdUW942e9b89Q1NRU0ZzEktPORI5GElfwPKytZxKP8JZ2cTtPZ9V3r+/2SW7mDQr/2OIsw2iJMGJTH'
        b't+a2T7eIYmitTOq+df3CsE7TQGSGJTKjd44lclq/cBpRouTcr7OEF/f7l/SJSgYnS1u5rSvbPAalScjzkkUQMTgtu5Xb55thEWQOhkWjyNUWrGGJQr4Vbe6D0nhbPkkY'
        b'8pnb3H4h9BuMkncbehjd+MG2dIsofFCW2JPVk929EIWnWUTRgz5+Az7S9sWtrEGB6JB7m/uAQGoRSLtDuw39goQBQbpFkN4b8bEgy4Eb9qS54SuUzXbxKnauYec6dm5g'
        b'5yZ2erFzCzu3J+CfHRYDz3vlyD/JyBMOBoidB7htzFXjFxG+ww+MlLpgZc5TotJ5/IMVO9gisJubRvXys1gsqcuQaw2277RySkNuNH9pC3LVDeSXTZ6ScLEetFdrhviY'
        b'u0E8HTbDowdtH281z4H0CGykpxWz2U7jsdkHyAuZiKXGx2cM8pCpi8oTsdz4oVPynm2SwMpo80Yx2nzEaDscrDky3Yil5mXxCaM9JnYUo93IGc1oq+2WlxL6+TzEns7C'
        b'd1/okATxBGg3IE4U8S1qxzd+MW8TK6kzNJqbUCpiedW86saGKq1ebeOSohEDFU3YBZpbwGoEu3EvbtAuF/OwXPz/OfvncfaOQJuBz/ToGLsi6xkOfxRU0/npKFsBwqYt'
        b'+h6jVXt19K6g67FuBGsczZnqG7G6w0B4UT3NYa5sxKyhtkGts/Kqi55jhos49vENce09wPuRbr+qsXEZbh/HyCXF1tVRk7CksepFNNFIbqQPJ/VYckhLUcRbdUR44pEY'
        b'g4svGjHBtTdi3+4ZEpXRrNbpCKSghVnRqK22Q+MiB4vdUcKPFT2MniZyT3CRoxXvGPEFZ39GhBllG/o/IJFka1Zq6qyWO/9fKvkRUkliiiIhLU2RmJiUmJyYkpIcT6QS'
        b'3Opo0YQ7RjSR0IfCrXoOFi4kinmG2L+V8SlzImatO310hfnFcEdsvl3GIKIF3Ay6nxEvXgZ3XZLWzCNvfC8BxxBb1uZhFy6sosVicNGMlVWxMUKwpbFQXlCMGLhnqn5W'
        b'ammBLS7grCLXjF86Ba8VgrvG0uJSLJAwG621z4etKP8e2IykDB7iykvI4eIt5WJwBBwGJ10ocB4e5Jf4c2l5YQM46W4sgLvyi0sL4S5wBrTkz1GwKXE2C7GtR8EpYoFV'
        b'Ct8Ad4zRxXB3FNw1NagwTp4PLkYxqEl1HM48cIeu6Qw4MYcPb6LG3gC75zrDXbISJHwwKa9EFugC2wrJYbUkEm6Vw7toLnbanl3GL02B63Pxu8vxoIWzCm5spM2+bhb6'
        b'GQuW4QcPUefyY6X4FWcRPMmCb8BDcDtZqLuNTKIrVaw473ZGtZIy4/sOpbNNXsV8tLjlVLkadpgTUJwInuHw8QyhmWyDN/OQ5LUL7oPXkTwWMx+2gPMoXAR352HBZLGf'
        b'8+wYLXn5eV0jfA0ftULMbuVT+aDVw4y5I3BjtisTnsFggWTSHHCd5J4fgeTAE7FwH4s8TY3m4Z7uL999911kgxWcak3iMFUtfQxfz7Iew/u8/8IqeTxlzkGRi+Dr3nha'
        b'dsUFoWUkQmxe7Dz8An1cgQoBQx7cqYySIpDIsz84LwU3yNxx9W5L4AVwkjxHU6L0RjC3SwkPJBawKAa8QKGkzeANM763Am971tbO5FsXaO4IvDiPM0HgdbiXjWRSlcsL'
        b'XHjUjJ/kqQeb4UGjm1UghG3gYOGcKHhA6TxaAJzuzXWvB11mWt4B28BeY4GstDgOizkl8CIqTMuBUtjOAddcwS0i/Xo4g9Mx+B2duAIWuCzlUnxwjwmvVsH95B31FetK'
        b'mQ9qH7pTTWrhpwtuRN+myFaIAPey4VWrvI/NFsAJsDkPwxfcHldaPCeKrpEYMNgtK46Cs65o8K/DbvJW+Px5QQrQGiPPj0VSMRfsYcbBeyVmfLQONsLXcwqxaEQxwfb1'
        b'Bkaas1zKMmOuel4gOFUGL40qdWomgYYg0B5jLbRwNioDtiXSb/6fBh3goHWM4KqTfYxSrnbvuqsM4zbEcO8x/fT03OJSMENw9A9PfaJOizyne2W/Ycoblqxp4+deCi6+'
        b'/UZkSdhLR35/6a2Xf73HuGLo4sGLkfmVN//zZ++vvfNl9bcuH1ZsCHxnDuPPdb8ur3O5skfl99Kv3c7f+vZByU/+KNLtuvcp6/40xuB/uf3xnVVBfzPdS/CLEfyxoDTB'
        b'3zI9eYpfkHZm9y/35e64uUGfc2fr+RfXVJbOTpl8Y9vu3veLfOYn39vTWphUZ5rW+5tX1r+7aHfaf1868/idoNkX269lWz6tTQtYbZlt6rTUVYT9rsSY3b9oeHf5K6/I'
        b'OvK83xhYeum8yTtmTVDQuS8FoQ23Vr+XcSUo5pMV9wLEJVy+4Jbry9/8buZ3wsfHU//rv751+VoIVrcNflDg9PVHby+v7tg115CmSv9L7YOPpr5U+bPcppeNgn59+G8/'
        b'u3X6/OIjRz6N1fxl5u2gCwbzlNOzXdb+6tqBX+r+uvVu+7f6F796+MKyp8fSnu7664zILs+hv+79o++D4K8eOIes2NQYfo+zfPWvDx57/PfHZ5btOl/1yRzLqqMwc/hm'
        b'47nbZS95rpW6kTf3Fi8CXUsEo+R5Is3XwYPk7AScMoLX7fI8EeYT0kaJ8zMribUIPA+PwSP8Qs/EZyV6Z5UL/bxfbyzohXs4hQ7WHh7zWDoO3E4/nHYzThUTLZciMgT3'
        b'YWWZywtMBFGnwHEixzNga8GL4FCMHNOMWAyRu5kyz3Dybhq8h1D/2cKiaC7FLIEnlzBS4SkeSQEdM8AdfhE4X1QcixBqIQNcmbKMbm5rErgWCI/DFpuJB8Vdx4xkg+tE'
        b'jwE6S+BGmyEIvAUvOhqDEEOQPHCUNhnZCa+BFgcrjzx4btT5EjzsR0xGEHG4A1rmg2Yj3qoyTAHJfHvCVhbogZc8aYuZzaidi1aNBdwNLjNoncUkkdT7X62ymFiXgedO'
        b'Yn0zbhyFhjvWXYwIdUO+o5QaIwlEsZHFpBUbL/Ep/7DOWd1J+Inmfr/0Vi6tw5jS7xvVL5R2zxyInW6JnX4/xBKb0y/MIUqMrPtFlvCyfv85faI5g5PltBKDLja131fa'
        b'L4zuLh+QzbDIZtyPt8hm9gtnkmLZ95dYwuf2+yv7RMrBKflY0ZFmEaQPRmGtxnqLINxBDxIZgxUtKLTOIgh7JAxqr+nMGRBGWYRRjwKiukX9AfLWmb/wDaAtWW6F9ta8'
        b'IbWEW9+LR4WtBbGOJmtfxmBqRmtuX0Dih6Kkz61eiyjpUZCk0+fVRQNBcZaguB5Wf1BSK29Q6NMe3S8MOyfsXjggm2qRTe2t7pdl30+wyHL7pbPfCemXFpI2i95ZYwl/'
        b'od9/YZ9o4Wdpmbdm3899Z95bpf1TyvvTVHhkSRZBMlbOJGfi9uItooTPQ8LP+nX5tboPCn0PZbRldLIHJPEWSXy/MH4wPLFHbQlPbS0Z9PUf8JX3Bct72DddLrv0Tuvz'
        b'KWhl4W6FDfhHW/xR56IHgycPBMstwfJuoyU4sXX2I1//9tTOdEuArN9X3hPe75v6WXBkX1RRf3Bxn7j4c9+A9rrOOpQdpQ7GxLU7dTp9KI4a9AvqdOrmdLn3+8kHpTIU'
        b'y+lw/8vnUbE95ferLMH5rbMHYxNbZw6IwiyisE6lRSQdFPi2u1gEk63qo4iPBfEOGiMhrTF6iJ23sfMT7LyDnXex8x5l0xj9g8qiZ4EfN/Ws6siuPRrCzqfIWWjXHuF3'
        b'NJfzGAwt0R5pGU+I+0O1R+e46dQtfhabVW27Eov/2b+Fgi2aHDU9ByiVk8pFxSZfQ2Gq6Mf13VQM+zdROOUO5tB6bjClcnheWcUdpb/hZHGJVmdM7MQH+WNFDHdaxPD3'
        b'Y1FFjVhbVVnENzpR5fTXZtZyKF0ieSPf1W/2QvptQTUSIPYbwSmE73c5L2dRLHdGGmwHOwhntRjuBduVYFc53KUqngOvl8HrKrcUhQLxH77whIGFeJfbuWZMe4rAUbBN'
        b'CXeVJysQ13MY7khCfL7zcgbsnAWbrUcL8C54zVYZQ59DcaIZ4LBcRXhe+Ip/MriKBjTlBXdqCmhZSE5NwFF4CZyAJ+FpxBohuIigxGAHvEvqA/fmI75frkhKSGYiNmsH'
        b'xX2JAY6By7MIp1eVMOqzIRuQ9HGZCY8K4BVt5t9epYwJCHJ+vvnRrnIk4ChczR+m/B/frW7s+g3dXCd5v/x8RMhbHfyqHfsm3d++6O9u3/muvCZ87eeXC+Z89PT3X3yR'
        b'9t6yr93k13mDA6a11PzY+we6vb417sv97lelQd+tzvmPcx8vDokC1YyB7pwn8U8ldZ7yuqzmOysOJB9Zf6xNmPAf3rk/vaN6gfH2olkW6Z6IO//nJ79zevRYsmj7H36v'
        b'e5P6qvK99KLDfzzy1/Xnm3re+c+i8ou/f7ggOWnpu2evfFL4zU3/WUsKoqetmfPX1UsZH/V99eGTU/KIOy1tf/v94LrUn69+4+8Dr+qvx3vNMYsW/vEz1Qr5x/4lOQsD'
        b'hL/y3vIg8s+7l/UKD7805fc93HR/5dq4+idPz/8ucP6K36bfmZP61s60jNDZr3xx99+Zoj+4aPY63bt3/s9Zw0erLfdYe1rX/zc1+GDmwdpKqdcTvIFd4SY04y28qbAl'
        b'zglxrScYKtD7AkmCvZGl4Lxf3QitR9z5PpraX4GvgLujaT1oM0dO5xAaXgFOOuFvUcFNYy0/CbEHuyoImwMuRMHDNLsUle7IMMEToIscSDh5agpLYvOLwVVwDe6JA6+x'
        b'KXfwJqsCHgQXyQuwsAOB0RuwZQo8WUi+jMUOZoATOdVPbCz09BgHZsz1ZdAey3JaDO+Q9BWxiPcm35w5AS5bv6xFvjmzUE/37wYC68JRhr2SWZQPuMgOWBFPTlVQv3ZX'
        b'FU4jL0aPGGYzKK8XWeCCHuwg3M8UsCV3NNcHdyUtcjzE6YGttA3wBbC3BhtpEwtceB3upa1wPYJZSz2y6W9AXFoC9hGuD5xEczLC+QXPIpxd+nJ4zXZC49dIcztg+wzy'
        b'ZHO8yQ9VvhHud/hEDrg8E5ylV3W7AXbYH9uVGa2vpx8Gx2hWahNs8ygkbFRpPgfuX4DSW5mN4OAkqdf/Q97Jy8Y7jf2gy5BTBf2lHUdzIjqGsErHaVZpeIEb5TvpkK5N'
        b't0/fysI8SV2nuuPF7ugBYbJFmDwYIDme0ZHROnMwMOR4YUdh66xB/+C2nM8Dgo+ndaTh6EnH8zvySXRrzqBQ3J40EBBrCYjtF8YOBkzqDMGZhpkSf69Bkf8wC/1+LhIf'
        b'Km4rHuYg/zCX8g5sz2orGBBFWkSRw044ztkad6i0rXTYBcfw7LkiLKKIYT6K+9qV8ha3s467drj2haf0i1P7RWnDbjizO+XtN+yBfQLs88Q+L+wTYp8I+7yxzwf5SBO+'
        b'OCTGoZK2kmE/XLk/rpzXWYP5xKmW2Kl94dMs4mn9ounDAThzIMps7XEQDgej7AOi9I6cTg758s+qfklaf2D68CScKCGJqSiRdda1y7V7Qb8kpT8wdTgEJ05GicOh2BeG'
        b'O4DnJRyHIlD8ofz2rOFIHIqyhaQ4FG0LxeBQLKle2j7zeHFH8bAMR8nxGOOwT4F98diXgH2J2JeEfcnYl4J9qdiXhn3p2JeBfZnYNwX7pmLfNOT7ejrytXKHsxmUX0Ar'
        b'53OB9yHXNteOJd0p/UEJHwkSrRHtyuMLOhZ01nWru14ciEi1RKT2B6V9JEj/dXB4a+6gyO9QUVtRl7Bz3smAT0Syr1nUpIjPfYMOrW1b25mMWOwBX4XFV9Ej7k3v953V'
        b'J5jlwIi504zYLQLY9EmOcYhjNKkNpiEWAuofxnW527iuZxiuYex8jZyLDOu75f+N3y13YzBiMbsV+0Mt4Y5z46hL/AzW/6JV5BYp89sDPPpGqsl2zcx6UqOzKpgNGpPZ'
        b'oCdpDRI1Pkhz0E+TQyzJMs1qI8rXZNAYsT00rdi2at6N9tMwq5YbH0Y9ezCmo9X5uPqq1SbyDU1HFs95HBaPfHYA3FgAkMyLSNoesB3Rob3gynxwBVwG5+eAZg4ldkJS'
        b'+wbWWnCslGiZkBR7FjTDfYivlcPXVZQcHFtJvvAYqphjxJwfkopl8GChXM4CHaCbEoHtLHCuDuwjnKNXKpPqS8Tqz8pYyMulbTfCwS24xVrWiUoBPWxwmgEO5SwZYlQQ'
        b'9RW8DfaCDVbt1VRvor+qLqCZtza4xUu5Fvba2EGaGVy4nu7szhXwCNFuMcoppoGRVgivkho9wYlyJZ2fCZqDwS5GYBG8ThRsWng4FO7D/adYwbAzi7HWH27R/vzTExwj'
        b'Ptd+9Nut2Kq18n7rTwQg+MEGl03t8Q+Luq4pNm9jsHKkQlbOxjLnRYKYM+9Vvl15pixX2e23+v233u96/7ZO4tOXsqLoT57ZZ4rKfK5mtD5Jrqr8vLaMurVrc83N8Kyf'
        b'/87/Pa/3mYbFwdWKmPg/XlP/ptq5lq9xq3WSuv3q7ROIu/bs8uneKzxbIF/1Zc2Btz57W1d576r6tfIqZ02SOok6/DtQ/7bzn17mPfiuyzXa9YiM+jdLwKyHTlIu4RWW'
        b'g5tiBwsMeKdyxAIDHoGvE65rJezORsSffrLeG+zGr9YXhRHtS34k2BQjL2bCraAXTVo3oxAcLSB0HfPpEsRHYUWQl0e+jEnxNUzYGTmdXJsJA+3aMddmFsHDNoXKUdBN'
        b'eC2wD55PotmhV9MduaHJ8LzU+R8m2M52gm0n02pjBd5uDmTaGkPI9EcUTabnehDEiyhmuPRsSVfJQFiaJSztk7CMtiJEdyeFHF/RsaIvIqWX1avsn5TVmjc4KbZ7lWVS'
        b'KvJFRJ/Vdel6EvsjZrTO2lf6tRMVnjnsiuoZCEuyhCUNhGVYwjI+CZtCavIPald3RCAKL/Y/zu3g9k2K6xH2VH8izhgUT+p0soijBsTxFnF8T9TH4kwcheTrAXGcRRzX'
        b'w/1EnDrsxJb4tOYhih0Zc1Z3AjVqicjujUQOadmDCp+KiLE4qNX1RxkpY8t3AwM5v3E0Up7l8QMf5b+MCp5jDLGb1Kb6UZ9tsQuaOoyaOdbPtuAL1PhroPgDV1z7p1u4'
        b'/8JPt2AkfdUBSWN8alSvwD6dzhFdj9wHxn3PkOTXSqKxL1qCaKCRPr7EiFizCj93gE8Do+VrtE3RsaQiK8Y30IeHRvxebI39SFJtqK7XrtDIJaX4hHSl1qixY3lShnSI'
        b'ZFdLaht1iI18BoWP/XKpc4lZijfg1unwtZg8tKvL8hDDXlBcBM6V54GLsDlWjtj3PPiKU3BoE3xtFTkYgQeb4OVChAQKiuVwOxJqymEz/rAr4tllUfhlr0J4wwmeBDvA'
        b'wYVWkRvcBjfAWSTZnyf39lg6RoEP2KQDZ4idnis8/1KMEwXOwAvUKmoVuEWfSoETiIxsiyllUozAmrkUPLyCpV1fKuIY/4wSl3W8f7X61fcEwNOKQrPTiv1CYt268yan'
        b'shJMOUkxRdPaPSOOv9cMy1ecKFLVULd27HP1VYTc2hDTHNDPVkYddUqKafa9uU4w/cxiReIrf3h9RuplKeNnvFoXdfLWV14Iro7KaZXor271m/JALC7oEIt5+3P8Nm+J'
        b'V+VGvZqQtYDn+qaXq+tnM/y754pudvBcv+ytmhuodE0MVLLfUsu3l8r63Lb87bfsb+Y7v+Elf5pXfTV0v8vvfl05T9yyPWRP+P7wPB/l+qhEUPxWZbNoqbx1uKCurKYv'
        b'6y8e3dN25W/MCo5ilQvfvl/509h/a337nUdMqk0SuWbzPqkHEZIQ0TovIeuFmJVUBrzAAa+ngcs0GrwUC0/AlgbYEVti/ZayM2xhrocXwGmSoaJGBK/CaytlgfBNWjHv'
        b'As4ywUl4Hl6kvyDVA2/gj8ai8ttjmeB1HcUtYQYWwN20jHciD76GvxkdK4fX4N18nIfiwx4mvLMaXqW/ZLobXuIXxoLdpTMRpSdfKuLPYMJ2sB9RCSz1rmb44xriSmVM'
        b'eBHco7gvMaNBNzxPBDXz/JlETHsTHJTK4R4ySA8Fq847lR775kZ42UZi8uAZ8mEUbyZ97nAXngY3YuLgjkhwJDZfJpcyEQk4zgJbFfA6Pba78B44UIjF3bgSDtgeRXGn'
        b'MH1hRxL9/S2wEwnMSVo75LuImKArZjWdCK/MxDoDMivr6yluNlOMpuoqqVdcVD/6y62vwNfBZQVopT9EtC05CvcKfxv7TbCZ4oJuZiw85y/l/1ixkk+NUsnThIqNEcCQ'
        b'm51K4SAhUR70l1uHCwSUyOdQalvqoWlt0zrDBoSRFmHkZ/4hfZNttzKF3iR5atvUTtGAMMIijOhOuJRxLqOnZiAm0xKTOSqzOBBLd6+6t3KsquV9U2hdebfPgFBhESoe'
        b'+Yd0hnWzuhf3+2cgyhURg78dc6ahg9fOHhQH4MKd5Z+IFUjMiEz6XOR7KL8t/0Dh5wFBx1M7UvHtme6wgYA4S0DcICJ1zh3OnaIj7qMqeRQU0jn5bGRX5NnYrthuU095'
        b'/+SM3pkfBWXdnzsYGHw8ryOvs/xIyVMWFZzNsARlPcbt/HtQ1idBWd8a8XsWDwVes+I4D+N4s6a50JTOhaZ0LMY/pCYmqlq7jEJTQB9cFN8J/M4moWCN8FpEAcWPf+CX'
        b'lYiEcogbSZ3lJ7BQ116lyHfaRk5UDNjiz3AIO8dwmgttQqrVGA3dOPIEdk7TFBy/8zHEmqWaW0I+bmLA33dF+N/6T8qhf5joz3u8pyTx3aeaxuqKCvpqsXOTobFJYzCt'
        b'/keu2ZKbS8TQkujLh+2MApkr8hCl6H/kIAuz9M+eYY2sXKPNwS+sGNczyKM+X7OZboLHzpS7dxfrnPF+puWFxY+CQ7rT+7KXfs1iuFcyPp+VOzhn7lNWqFvEMIWcbzg4'
        b'dpiNvF8XMCj/yY8EskFRytccpn9ac8HXXMov5JEgdlCUjGL8UpvzUUxwxCNB/KBoOooJzmI0l+AvJEkeCWIGRXEoShzfnDcSk45jMkmM76RHgmg6xjezeTaKCQh9JJDT'
        b'FQWgigr/7Mxwy2E85qLedyi7jJcT3xK+m/goSHJOeCv0rcR3a/AIyhmfz1ENLlj8lCVzy2Z8TWEXj6EcjQH7Hy9l4MGHXla+Ff6u0/1JjwKCO0zt0ZdZqC6lZd4LFrUG'
        b'V1PHQIxvBbaZZZUy3BKeUNjF9aAENvY/rWImu+Uy/kRh9896hp9b0OMU3LFQi1vwU6aPW8wwhZxvWJT7pG9wkH4ZCSPXtNRcI7ae6QJdMqO7O4tyC2LCLg04TCxysj3B'
        b'dj7oNmFix8f2ImUi8CY2FQlMYIeCzXD3/+qXUf+BO49OJYQLgrecE1jwKH6oNYQKgZ1wK31asQ+egccL5aBHgZrwgPfY8AZjOTw9mbayuAJuLYopmAS2OX6ZHB5dAe+Y'
        b'CSm+SdSsLfnwtBMW2nYmsiln0MIsgB0l2ldChSwjvpm6B3xH37QUP3hnA6OoyySvVlQLEs9MKfON0QezlpzZqfj5DPPv27/a1LGpo7ij9aOmqjlwUw1vM7c8qc27ZqUi'
        b'x5nFX3CWx6rjUz9r55fMeizlELJYB87NjCGn+ETK20gebAC7YC+t376DiPGdEboJjsAeotINrydksy6j0X7CjwS9E+SUHxxaSvgA36xwxCY4i2h9rlWZu19IU/kDoCu1'
        b'MB9ccy62pi5hasB2cGrCm52uTQYNYts1FcTYOpxh/eQ5fggXE84ZnpRITFO45pmfC33IB8FnHi/oKHi1qJ88josIYGZbZvvKbpd+YcJIeFW/MKp55i88vAd9A9pnt89r'
        b'Xd/KRmnNhY7S1RAbtzrEpe+af8/nWXHfiBPCdPg868sCBsP/h372bBRcCqy/3/wC1TuN/8yTYvH4iibaIkzrk1bsxZzJlJLlT+EHxdKZBi4Jc1HYiYSdSNgZhV1I2JmE'
        b'eSjMJ2EXEqYfFOOQB8M49gfFcJiP2nNC7Qnoj4UrE1SMJIbS09q6mzXVi34uTJlIUkXWVA8cVnFVLipeElvpbY0VKJNQLBuV8rE9y2V9BAw//MVKwk+k4WfTOLY/pZA8'
        b'Ccaz+lnP+G3ptl+2Lf8zv8/Gk7DSV+6hoJRiXL6CofTD6ejX37ENFA6wlUP+QAd/kIM/WDkJuRKHmBAH/2QHf6iDP8zBH+7gj3DwRzr4oxz80hH/s+NVRsuZsxjKGDnT'
        b'4LVYOJla7KWMxfA7V0qN+WdDmLbnma35Zf9oftKKt/VJMPr6MC/JSSknMOFDHmxzIjDAUcaROF+lwiCuE7rUS5MRp4S4ZHUuEp21SHyhRp2y23UM+EE0rP51OGXHT5Cx'
        b'UUv4U8Vc+9m607/wbH3MxyzHfmmeR5+tN0WyqUimAJ+i6/YsMdP2lsmsXa5XGAomVVbp3pEaQkd2s9c1vsQa5lAK9aIp1QsoIsavW4Ewb4uDgSrWsIHWHLuSDSHlFidK'
        b'WecsCACXaO1r5OT6l5nNGCFVNdc6U1/Y+kiwmbZ9zkWWEbOCr1DxtHAuBnvx+0jvF7iGXDizsyy40D10hyurKML3Hffaa15VlXm/VFOXOy6cUSjCeJsevT/vtzNSUllY'
        b'dl+p4BfVRVc7v/NQvLi291bRW65vXYiVxPv0vijY4731J9wvLjNW/74p+I1p7/x3oOKlDEx43poliqh6QepCX/S6Cw8LyKdfWWBTvoxFOZczTdGTCFmZuRzRhxZwiZwM'
        b'cyNT4B2mJ7wFNxHZtTq/1n4PDbToRwzXmLD1Cf7SKXiDA3rAGfD6szpJerrC/Tj1oANJ0sS295aQop8kiomSEQuvm+WFOJdvIHtK0ULyWecE0A5Pkp7y4Kv5iDbis+ad'
        b'2BDsVWxQ3AxP0/Zi3WAzIvY4nxFeIvmKwQUKZTvAQrL7hWr6xHcz3OYJWuKwWqYLHsuHOxlI+t/BBFvAMeMTrK1fFWUGLSsRN0X4pXxwFv23C+wpRTR4eyncLedS6YVc'
        b'cFAA3pRyv4ebxvtkzJtDXvaNNfrRodUUTUkXe1KTwlrZ+/nYDEr06gvIy/uaR0lCO6f0T1K0ug4KJ3WG9AtDu117DP1R6b26d6r7p80htk+Z/f5T+kRTBsPj8QNAkwcn'
        b'x3TndM/tlONniQZDwslrQNafYAluYjAkrJPTyj7g5kBsaQFviEPM7ofY+BbQkOuIRKVvHHLR6pvMJvJw7HgKT1rks55MOTwLlILQUhzT4VBqkSeDkYZFvrQfKvId5kZT'
        b'r/GTf9ybQNZnYTgVeGgTvCXiuEq2l4CwYd7I0ycLDy+kHxYJHHknf8xTInLDfuqZT//+wIdP3Cocp36il0+moYiZzFGv7MR9GBRHdzDYoYNjHwGS/zNPxvAq7KDwvK7N'
        b'Rl0ztFNWLPhtUL6tkO3ezz/dny22d3Uw1FY0aCd8wwZ3pwB3Z+RdHR+sDpLUGhob/mXzYuuHetXz+lE8uh8i0g986+uf7YUVdrgVpkaTWve8LpSNgulFhxdZXz0qxwVt'
        b't8km7M//7DHwmI/Dj6X7HJruH5xJboNIfFmVrlfWimkSL6gml9rztJMriw5MLaG0p7cxmEbc1i8PFduEuw0um/xe2HiKu/8QeOd+6wdi0Lkl57o0tNx3n/zChdZy9efv'
        b'U9TfUzjJf/lvKeNJDCoLt8C9FaPoBaYV1OpnqAU4Cs5OJFoR7c+QpyNZGHkxB7N5mCrUeFHiwEPr29Z3zhnwjRwMCMS2pUnHp3Zgu97uLIuvrE8g+/Gv5sxFy6pkOhxI'
        b'VXv9iAOp/1U9wpbv1yNYwWO6gUPtV2CeYYNugW6dN7GlWPxQWpSCyzMoRsZTrc+VYoZRgYI3eo00cGyqxOCRLV6wsQYJ/kWKasU+qbDc2/3uVzMSjm5MZFFPAYcTVihl'
        b'Ei5iCWjzexYslsOjz3IR4DCL1veDS2GINWnFSv9omRzb629iJmbrJxTHPSrI3UHtGk1Fla6xetmQnwP8jE4icBRthaMmLyoqFltw96gskZkDkVmWyKz7ofdX9keWtrIP'
        b'ubW5tWs+FISNAaQhDrlp9z2S93wseS9AzgJHybsBgZLfD5a8n8UzmGf9ppayyRsH6OemqSTW/wwwjT0ZtL4b27/+KeP3LGrGonmVk771DKXIwRziZLvQlj/PBqdNFLWG'
        b'WlNSQV8gOgSvscB5JrwNX6GotdRaf3CDvCuSD085jxI1EOCUR5XIGFQS2M4FF1juqzLJFTL3FHKFrPJAbmXRI+d1FLkM1Tu5lPmAS+Up16iFn4qlUVMocr8L3AavwAO2'
        b'x1zJpSiw7yX6XlSeDRAdb0IhjriDBw+Hw25atYhVUFp4GvW6Jd+qG4OX3Gn1GHgtQXto22mW8S7KJLq+7mr1MbRJot7/fPnejSF7QvZnbWYw57aLxetWi8XZ7fs3nDiz'
        b'U2CpzD0vnZHux+1cICh39WMnvlUOfubJPudWeyO6rjLvN7WVzbWvnNdsPFesYT/yAoEPNj2cOW+exEW5/Sv/Jb0tXkclhpD3mw5deWHWjIaaba8+3F0TahREnmk4U7aQ'
        b'sW3Zpt7Lva1v/oFVGy1f8taFG0U3iiQvUzm7fFumRH42e8ajqt9VRZglnz5NYrFS+94nz8BO+2ngL7hSqRNtd3khMA8fq9mO1ETgGDlVmwrPE+sO2APOwYs20QdegOcd'
        b'Lu1owHGaHOwLmm3d9qnw5ghBeGbbw6NImCL3Zq6IwC1+tFVCsl0Egq+DM9QkcBXNNngNvk7X3BEMt5AbNliSQkACLhSAXbaKuaArmVKA17iBYniXtpu9CnqabHaiSdW0'
        b'nSgfniDqv2C4N8Fu6Qm2KqzKwY4IKXtcQQYDvf2RT8RXrDRoTZohgQPKITEE01ylMc03K7yooJDWmb8ImPRILCHUat/qzsR9L3ebLq0/t75XORCXZYnLul/zTjVc9llw'
        b'VJ80sz94Sp94ip2wdXthG0xf2WVWz8yrLhbf9N6cft/pjwKC202vpndz+gNkn02W98WV9E8u7QssHRQHDohjLeLYj8RyfO7m1uFGh7uVH4njB2mLzc7J/aLwbtGlgHMB'
        b'PQv6pdMsomkfi8Ife6OeOqA8Lo3y2GpDnXFcCsq1oT0r3sPIylCDnMUOeO+p2etHHGbt54ZRp/hxrJJq9nikjBh1MGwKF6JuwYiQmcS2okH2KKMODkKDDmjRUe2CEB47'
        b'i0PQ4JjYiVUtYx9xciqhL8K+5s0H+L7rJMpLMikWXCPvTBO1PXiFBbfHoNkx42tvJ83aMjOexZdNUQhBYuwIrySv8UvSphl+zzRmoZTh34dfre6wKds3+eW054iLOkLu'
        b'LP6/zX0HXJvH+f+rxd4IJDPFMgjExixjzLTZYAvwNggQRgYDRoDxivdeEDzA2EZ4Ck+8iRf2XYabNA2K0ghIkzhp0jZpkuLYMW6a1P+7e4UksLPa/j6ff+oeunvv7r3x'
        b'3Hie93m+z19syi2VWWZ5DbG5n4tD5Catll7uySbhWy3KQ8tnkLuZeaBxyFoGupthvahYtJ+1gMuzEbuPzZQBWihE95lBOVewwVZ4FNz+GXpfa0DvxJx9DL2TFELvITS9'
        b'D+fZUxNcNXw/Fd9P6djj0Guk5k9t5nzEcxlwdh1mUXzXT70mnuH084L6bYIMiM1YrxVahxnjOt/nv6zKjSmapdadtItxpkoUyEYZ6h8wJos9gzFxGDHUE3/LcctH1Yyh'
        b'Nt1ZR8R7bANqM0b0hkV7poTmjP9PaO5XfA/i5NDUhYdi1XSwFrQyqDgvypVyrYF9spBDRhw5/kC7rsr1cmknoqP9v9de5tllW3rawkLXrjPaWJL2SXGxiYTxu1pOe1hS'
        b'St1gUtvdxRMki9d5no3cuSoh1GbC78t+jyE0GdTgR6ZnHi8ana5f8RXVmNJ9RaUpyJx8NdGSkYMBGemTCS1N1tLSfHuKO6FlCqKcQZ6Hwkdpr+EFoiv+oIu7gtOR0Zw6'
        b'yPdWFCinqfnhzZwhH78zPv28kH6bEAOyMvsVZDW+2WZ6KtOJrKpxsRoU1BgS2jxMaI9+K6FNHk9out2kmjKUI5NtzVi7sXH+T4jsOV7y+fvdKJHhw9QDbOKLAwvhvnCw'
        b'3iaNRXGMGWC9D7wu43h9zZbHohzfSWMulx5GtPYyTWu/5wIXy7LEBJNjdnmvXyvmvmkt6ZdKi9c+zGqrH+Tz8/nR86hPxZwH2Y5osyK6XBvT0miT3AWMZHAjCrYVorv3'
        b'T5IYZ5TEtBamRVq3FVoa4xvQ2JgnhMxEWjKr0pHZAM9dEX6W1Z3a43MmqzdSJUpU+yX1eyareMn9NskGdGUyjq6GjMolpfU1dS88J00MCIomJyyEqKtHwTJDcqrE5PTw'
        b'N5ITqb3NyI9SmoezhNa0RSOxbSRWjtjecchSLzyrlC4fsmysaSitkNaRkQgdGw0bMi/FWJnS6nppXahhJGzIpEwmp0EwsbHkEKdRUo+du0gb6iVNxEUJ1ukYspA2lVZI'
        b'sEMOnHSJ5MS65aFDZqMgl7IyA6iuyyRHvay+SoqGFWub1DXgoBEHL3A6kzNkgv1G4iqHzPGvUXwskkywaMn7wupWMbA6Cga7KalpIpBgQ5zaippq6RCrXNI0xJEukciq'
        b'hMwhtgyVHGKVyEpRxDgxOTm3ICd/iJ2cOzO1bieeqV2McZwY8RuBl0ktNWpfuY8i35awdik+FqgCswiT/xOe7Lk16/zcmi2lebIa9irGUyYVXRInmbfAyooiCulgN9wU'
        b'JIfXrBH3LytkwpMM/5lwP+FxakHLFHl9I3oGOuvgVXMGZQwPMq3AEdDVgBc36IWbjQKwKdY5v7TsoPTsGXBrDjgngnuCM2akiTKCEWsFd4HrTQGjIBywdZ5FMuxIJlzf'
        b'RNhiAluxjtAKdMtXUNnZ8CCtPL8BnFgWjs0vGb5Ujhi0gmYfWrGzGxy0DGc2ITaACqfC4RWwlmjOw9PggCUqwKQYfhQjG+yF60Av6YK/CCppE7RicAKxEwzKfC62tdwA'
        b'aFALAbzWgAoaUQwh4gvngn3wZdQ5oj6xrwJeCARr4Q5sXzeJTXHgRQZsrZxFhvKvxf5UPkXlbXAsTornmFN0MxThsAPVxqAY/lQAeBns9wSnaKyWXnDeLjMoMAgD1ZiW'
        b'ZgfC7VkMigeOsxPgHnCZ9jvC8aASKMrmh+XF872Y+RQZCn94EJ5DVbIohogCJ91AW9J00jGhHVgfALdmgI7goHRaV8Ea7GKVsMExUturJTwK7WfRLR7F87+b7E/z3+CC'
        b'0SpUmTHFCKQY4Axoz06ltWyvgD6wDbE9xL8uuLKGLWKAG/mgh1QVGDGVWoWqOhtebHcn1p3e+uFacAc0h0eAHopiBGENjEPgINyURwYiYg7Wv+irFWZkI1bdNJSJmu1O'
        b'6korzqT2ot2vkV9sJgxwpOuqQ/N6FleFJjyYwjqkoAMcBDfptm2A7WDTYtBGWw+gfhqBzUyvQmtS350iAnOasC6rOGv+CiHdTbc14FJ4RCSFx6w6Bs1phyPRafGAlyoy'
        b'M+wBcdkCd9N2k1ZgIys+K4WeAn4MhVZw00eVxWF3bKzpBQI7we4EVB2T9HNnPDiAZnZrA75Jh4BN8Homxg/dkTP6SY9BOSGCXQf2ssF2eJJJGrQIbF+AajDC3VuA7tdt'
        b'K+zIJC5E+W6j8q1zSBX0NFrVsqItXiLt2T3TnkLnymylRXHcw6iXaJLIgT3waHgYplkR5Z0B9osQLWMxkBe8Xuk1TUuvTESvlxhwr3ECKRSSDy+GT0J3ckYYomwfsB8c'
        b'mErbJ+9fCa/nwtsBmdj9CIMykjEnwBOhZBozELPcFx6FS0UjxrkatMFdhcRWGlxyAq8EYBDVdHAcbIbbwQWKsohjoXMe7CNlwTGw1x6VRaMWi/aYCEQc5xYSu2a4Fu4R'
        b'Z2qNQtdHC7Ftq4UNy8EurQofpe8vJj588vaUFIsCaKQYsD6PCo9C/COqqr4JtIOdFTQNHocd8HK5N2oIhujJRKRRynReJSY9FsKtdagQIqnJFFxXDQ5GwhO0sGkPeCUj'
        b'MxN/A2XWMOB6x4TJNeQ1S0vBCVQCtTiOgptWg47qVeQ1Up/UVNCZiTeznfi7qJE90xRchzfIFK0qXEk9RlMUYVfseN7LkyYZVjXsBZdDIjgUI4mCJ01BJ+iEXbTe1drZ'
        b'qNE7sjKI3lIXNoK5wwAdiOR3kvp+x59G7UTztcyvOONpjRW9QNxhG1oPqEK0DSRTcDMiGwXYAA7R9HnNCV7LRBsKuiMtZIBj8HQwuCYmla2u5lNo9vivy4pdemxM6V1q'
        b'OuwqzkwXIUpzhTfYbAZqWjOLDIAM7XatsJUD+zIoKogKAoogouU/bzLaIDD2ycw0uC03sJDW2odbs+EleFKEdh9UqZ2x86oAQhtwH9iYj0Uxp8FluIteEiawjQn2gV12'
        b'ejdLzdYszMIU/96sWPThAl+tgHCnNzwFW40yZ1No9xLBzXAvjY/UjQb8oM6WOClD++EcnTZsygec5jQ4o9nFQzUD6yIckMAdMyaFwO1sim3HWAD7wDF6qLrq4ZXMfLgL'
        b'UQVsR3dLNuyhXGm05Vcawa1RkDF4KFe/nH1yOTJE+RdIDQXwOngFdpijDaodFbqD/sGeHLIZTJkI2wPQwGTD3WmBiNxPZ9BsdSibmpjPCUOzdoB0fF2IM4VoOe2se7GL'
        b'd1aT9hTuhFtBO+wwnrMU4wKgf2jbOkP6Ds7DW6BZX/M50DVaM5OaWMAJR92jD7NqEezJnIGOWQxoBfb5wduwcxqpXhwLLojR8bwLTTo4wlzJcIE94BrZAILB1cLMAnpI'
        b'TqCXgVvwCrxmRrqEJnE7PKIHddswYXRQ3MEONry2BLxCllQjA81HhyU4G4Z187B63toZNC3smgLv4LUelI6RxNIDw9iUc4wYHGRXeZeRGfcXuWJfR1t9sYo9xrw+20BK'
        b'BiwGe8YUZFLOYehw7mAvWZBJBCVcK3e4g1qG9gwZotyzNmR5wfUOJZlwmxD2iXQTaG3PWhwObxChy2xwLBy0suojsETGHR1iu2gA5m08kwAaExrRVTCN3uYCdjaBq2y0'
        b'uW3h09R5vtYCdnAaPbEyB/oXDo7SQp7DzrVwB3MSbKGoSqoyLZmcNiHoErI+MzAwHZz1y8DLzQIctU9gwb2weQYZtYw4vIFZgLVsfAKjf27wML1HbJpUkhmUDRRjIY5g'
        b'K9hGpqwIbLOTW1qijQotPXgQrdpzaNnTmjb7rM0pVLlJ34TirFVTF9NHBjwCLjnDHSx4DOxD10CqBp6Iovt9JRgo0PUtDUO77czMrZ4cSJoqcGZjHG3QR+ToERXe5l9S'
        b'CjTSCdUfNgWldGtptg1RihJL89vgTSLOB63wssyov4Mpx19XBk457ds/T6zOs3kjSiY+6MkZ2r5ewDn94MSngcp7hQ/Bazdjth397vWdOUVtd54+uNmZ2HfB12NR6ydf'
        b'1ZUsim3/5odnfR9OmfLhkr7veUlR1I8+ojU8xaJzJzqtq9ZGmkzesWrq9r3TQvyEs2Zbuhz+vPvUvtN/Uhw947n13IdOd+9vv3TLnGLxzvib+/J9b+0vWRYw54h7oXfA'
        b'kxFG41cbPk7/yPTDgGOtKc8cQv8y6Ot/uuuyaLLj+da/v/2gO/3HprO8U7fe3fam6fL96pRb58O2pbMk2z2yvLokgogJSeampyw3Tthca2S6yHLjnM0hWzbKjUBc8uwE'
        b'sJwlafG4Yt75mV3y7Glg+7p+iQmvufjGDN4EsPgT56uv2wQ5xG95y+ITM7vzTiYLNteeG445G77x75tMo/gg2/tPYTbV4WxrU2cj4Lq5lmc6wr1X6Trlg5CNPS//XjT1'
        b'SKIkOzvg0DXXCYHpr7Wtmpzh+9nI3M2K9LIP4uJHIu2+X5yV+2Fi5sjvjpQ/Vj7LLBSc+lex4z9HLs8JmiK/YRxQUz5BduLj5tNzFzZs/SAh9i/ml01PPJteqmlZkJNz'
        b'68DHduKVXh0fpR7NXRLVveC9Yy2Bbk8jLx6Luur6Y8ilpcGq6+WZBfuP/dH+H8fq31ry+d/3XD+7/0Sw26kh3zeuXtrg4/l38cmDS27Bya8UMVIHpCYrYxPjoPMrSdFH'
        b'/vp3h+B3cxY6fvWZg/iNyro74o1RFp8Epgu+2WDCXy/4d0eew8adUz2vT0ltGily3vzlJ1OSB4IHoPHrz2ZY7BWvCntvuF2y6l7QnU8Pf38tftO+E+9c++zJWcUxe8+b'
        b'AWseTf0abt5ucc/136ycgO7DVi5Cexo2fG8s3G/gpe3q8ypW0ZOIWAHeYKwJwN+RmOAgA26dmp0xjVb/ugp2maKrGOJijKgF6H6ewgC3LSKIJhXYEwEOgR3WtRZ1iPPY'
        b'Zd1oaWpEcRegPauTVQO3wGNEk6o61NccdIvSRsHLwB1jW3iDBc7BC7CDBpTYC7egu6FOe3kl2EaUl+dZ00ZQu5aCFqyKtRFco01/0PF5jAl2gK25pI0R8EIk6qTAbVRs'
        b'a5LNLKv0fIy3olJXWWYu7lYjoyosEZywpc2ImhP46HzZNBb2zMyYVBcIFTZaZLMK2EwAT9AtbgOxyn0px00caKDyxrSFl8BpWmPsKriTr/3sgw5gQ6g283iixAZPGGcQ'
        b'vTMD5bSKObR62kS4nx7T42ICkKbNRDTT0PX5OK2dhgaCzOss2LEGq8Phb3WBRmi/254Fduuk1gExHHCtyIXItuFZeCXjBYLtfPAKkW2fhL20wVcPupz0BASB3bXY7tfA'
        b'6FeEZonwHcpKMapo2nK4LdhAHW5K+H9tezUWy4MlKSsbstTLpVCUCKPusbXWwQ6Um6cW8ytc5RqpcU3sRUHO3TnNZn/i8tqMOs3bzTss1dyJSq5GGKMSxvT6q4SpKm5q'
        b'M+Mje+6fnLz6vafd574z4XcT+sX5b7movAvUToX93MIBe1eF43v2vvgbUGZLJv44hGpSpCrD1fxgXaw7XNnYI1MFJ6gDEtX8JH2uyB7f7qm9SWr+VIM0YvFVpQ5IvjtT'
        b'zU8b/2AxquNumJo/bfyDcnXAlN66sdWTBxXqgKl37dT8lPEPFqkD4u8yUIkHv/YdS9QBKXdL1Pz0F7YqVM1PfeE7mGp+8q9+IFMHJNz1fEFV5IHHT/XjRVVJ1QFxvai5'
        b'iT9ZYnzPf3IQdVV9F+js4PgwluJ7KiYqHbuCerw0vEgVL3JQGNgt7wnvNeptfMXqrvw+sz86UxM9QxU9o39mgTq6UB08q184u82orbHdaoDn2lbe8pKG56/i+SvLLizu'
        b'XqzmRZMPlfFqt6n9iByc3TvjO+OVhT3Tuhf2lvVVv1KtDswaEAb3GHW7tbEPWf1ihkFXT0Wk0k/lFY4x7qZpCVTBPGXcZfwAf88MUPEDlNN6ZnRnaETxveEaUepdr7uN'
        b'an7OAN+t06zdTDFVzQ/X8Bf2Gt/zult+v0g1bYE6aaEqeqGGX9ZfUjbAd+1iKaYpp6q8J6sFcSp+HKlV+4nK8brTRafeXHVo1n00aDMGfu6Rq8JI0dhlpRFEqQRRvUZq'
        b'wVQVXg909fEq71i1YLIKW9OPryNbHZpxP5G0+Ccf6buarH2UoQ6dTq+rF5VBazH3+Y5MV4fq6H5cdZnq0LTRB2PKZNznqENz+vNmqPkzny+Wow7NvD9LzS8Y4DsPCx2E'
        b'jo8oBw/eY8rBgY8xayYcyHw5UxGp4gr3GxqrmNMScnwd/W2ILnjXfA7O5RgWwx5HwelRgTn+tDzDgcFwwrh5v8WihQjM242EVLd5xFjNWd13mAqKxgwgX2CwVJcqMNZ9'
        b'gWGMkeb+D0BdxkpzBdR4aa4vLc2VvYQZ6N4US6q46g/8bEr/ZdkZHvUFrRwKHppPuVFuYIsbSZaDDVWglaKYddQEagI8AXpprubOQrg7nI2d0HRSYVSYL9hK6n/KNaFs'
        b'KEEQGvyqxQUTKKJnIwzD0pnhWKvi4qzPXBJoVr6xEMuV87wYIZLJ9V4CLSt/LhvsmOIcHoG5m31UKVyfTtIrwAHQDI4HhEcYYcUfShpdQSrZWITxnqPFxoJiUYt9BV3z'
        b'vHhbNAD8eKPaYovDsgi6De2O2CV1cbEFSoyd7ULnFK3EHqUFhcy84irHUg865+HpFihxbY4ZSvwuP4XOedrTDHFIPUITm2LR5iVr6Jw5a3BiyBJzm2KLNvdoOrEpDTfp'
        b'rgVTUFx1ak4DLYsB2yfFg+22hJsuwOIHTiMD3Ii3Jhy4EFyF+8NDsOQaKECvNwVedl5I3rrE35NKoWbnmlDFJatYXPojrZM/upWdYVPxbph7ioZKWkC1rxSehh1mVKGY'
        b'AtfQP7iJTzNcG8B2f9hhhLhccI4C19E/uKmQjKpnWQhsZVDgHDhKBVLYZGAPeW29H9aLysvEgIl9QjZFOFOwGTaDC7AV7sP/41A82MmAm9GNDiqqtbgKfeim24q9a/Pw'
        b'5+P5S2mR+HW3KhPQpdd6olWe6mio58xKoESXxfNYkLC/DrYw7OBheJO0TgSvxmKchp2wC+M0oHv5dVoFYquVPTiDBXyh1HJquSOkKVLARlfAM0wK3vTCymDwMjxINhIy'
        b'KVgCbELdT2OiHjWki2jEp1rm52jRBEzBWopN3TKTFZNY8ka0lI9skt8uwDDR3FU3r5isNzHZ6nixcKfTpEO9zX+bOnzpwsSF6Vm9y7878HTNh/u/mXn58sbXX/0oNrzm'
        b'o0VDB4Y7ZrbnOYnYn1vv+HyyKqPvnNTJr869QB7qKCowGXYydlncGTsso85y4r68do11MkFzeijhj7PPbzvy2oKHd15OCV0q37Gqqhle2f+decCX1MfvJzlWWV9KXeL2'
        b'RvzdvD1LPvjzDJVXnfNXX7x/sfqNV+a1NZ0sr+8/Ublghc+BGam8yR7fzBpYuPfrjMo3zhemCv79atnSJ4EB5Yd+mPf6rhXUpz/yYjl3PjzMW3y97aaZ2zf51mu6WQ7J'
        b'by+0ijsdsUW8yKrU6p9ne2Mjdrz6WlX1p4/W/tvpbdvcpog9X63+eG11kEXlyZeLVIF5ZsceCx3zP3342Z3HtxY+uvD2lAennNbULt0Vf3TFfruvPnl3MHnnn7P7cr/7'
        b'+rOSIumsf438wfT7Vk7xgzUtS398PCw6GP+XoXfKvvijS8jldzVu08p33VbtPPh398Um8958/7SQ/xiLDTnB0uc0gBeuHq/p2Q4P0jad7eBw9JSlRNsvJ9Af37evMsF+'
        b'eAtepLF+Ljk16HmmOnCb8EwZoIdW6zqEuKq1cEMQzUto7XZi/Wlrmi3gSgjmH7KxdM8NnsPOyTBYYSILnC8rpF/fApReGOYegxBuQxxSCFj/EtMTLajthLHIq4E3tZyl'
        b'T92LTHfOz6PZhl3wkAtuRAALcXLgNguex1vB9WDSzKZCTwNV1oOWWJsV3gZbCUAGbMkCx/QO1WeDLeQrkeNstrMAHCXKdulh+XpX6UAJ8UcR3BEfFjgLd4BNNNDF+iy0'
        b'fnRMWwYHs22bokkFuYg/vjXKb6XBzWONhqgyGhBR6RJL4yHRfNG0TMIZTYNXaI2/jgatQRGqw3fBWHuibrCOMFgTYLcZYp/SREFB4GU3/EUQNRN2s2ArE/UFs34lZtia'
        b'ytDGqQ9e1Rk5gZZGetoP19eTXLszOVQV3MRmYojUXaCXnvYr7KQ1KTqVPa2+3p4SomsMNrrCk0Q1EBxd9kLtQFo1MNSM9LoUXKhNJV7JxnDdtlBBwD3z4CkrHQ86lgG1'
        b'ERMWNFlE46icmYQGf7s9bU1lwDp6we10o18BO81gN0MLU66FKHdb+avspgwQI4bY2ABhyErPO+I4YR5NWDRY9lwexeU117fGKBit8QPOrg9suFiZWWPjrbLxVsxQMi8Y'
        b'dxsPcJ3IP572oq3hCtHlTcMNVnGDexhqblhPWE94PzcKPaZhGpVeKm6ghhvZ463hxvd6D3IFCu4p5y5njUeoyiO0J1TNnaThTlZxJ/cmqrnxulr9VVx/DTdExQ3psVVz'
        b'w3uSepIxGMjPv3QQsbhsDd9fxfdXcwM03FAVN7THQ82N6JnZI+7nxpDn+M7fmktXoUQPRcqZSvQwdHyLxT3e14MuBmnC0lVh6ff91GFiDXdO/6w5/2m+qB4fDXdKb5jB'
        b'CESqPCJ7UftjNdwEFTfhLuppMn7soqxDndJwo1Xc6F47NTeOLuPe5d7jqR+vJDV3Kj0RY94T3TNRw03qnUYe8eguIw6PvrWrUZ89laH93MBfeKab5+Eol1C7R5SL0H4k'
        b'muI6tUS2+antvR7HuNj6DMdStg6j5PGejS8iGDr2ns3EAXuext5HZe+jtFfbix5ouTKOkq3xm6zymzzKdkrarTX8YGWyhh+JeEp2n/kr5o9YDGEq4yHF8EjFsNYO0zDm'
        b'g63DAfMW87bk92wEA4Zv4TkdaGppUrBPWXZZqnlBzWwtrKjCo5/rrVNY7ef6DHj7ncruyu7xVHlP0njHqbzjemepvVO1+vol2BEdz7nZ/HktnV+Bz0JUdMbAs/RhjuMu'
        b'Cr4Z5Tj+iTiOOTwGww6r6PwmoxBf0pghkyLaEkFel4grz8DBdAbRrCRWhnUpOCUbB1MY2NEcueILGV88wzdxbMv0BTYiEU54Ee4KbVxIfKVH4yAGB7G4dpNRY7DRX1j3'
        b'hZhE0UYvxFyB6O4SdUqi6oYVlIYsivISZyZmF+XPyUsVD7Hk0vohNkaPHDLXPhCn5otp1qxPB9DyX0nLnoNawc72SICNr+VrmQRqZcTIGmOooOChJ8V1GbTxHeCGPeQw'
        b'uRFbUx4aUS7egzbBA9wIlOISuTVLj6QSjpFUJhEkFS1IigiDpAQZwqb44xQRSXFwHbTxo6FVHEK3pj4xYVkGjZgxLfMYT0zMLaeOOLEtg0csjCxDv6VQMGLDskxhDFM4'
        b'fGhFuXl0cbsq+l2CB928Bn38Br19BycKld6KuehPt5eyTLFQ/8PbV8lWxI7+8ZioqFdYjMbcPBTebXMHPXHMZdDDW5GvMBv08VdGKLIeutu42A17cifYDXBd2+XDLPTr'
        b'Ade5XTzMQb8wIK9HV3iXHGUNGjbGKSaUg3uXPa5h2BTHzSgHlFvBbcsYNsdxC9Tldrkiom3xsCWOW1EOLv2uocPWOGKjL2yL43aUg2dXMm7jsD2Oc/XPHXDcERVuL8WN'
        b'H+bhOF8fn4DjTpSDWxdLkdK2YtgZx130cVccd9Pnd8dxAeXg1J6sYLfFDnvguKf+uReKP/RGQ467gpVDUaZvfXGij6+LFaKAfAbl4t62Spmuco/UuE9WuU9Wu09RO8cP'
        b'8p3bspSOKpcQjcsklcsktUuUmh/9kMNyttqaOWKWxLD0f0ThcCSNGWLp8phCAW0SQiTiJ0DXAt2NVwQOEww1m3zW3CiwZwxPP+rr/BEGC4m3HQeZwazDcBJsT8Slz7FG'
        b'/zcmMAnWY2Ni1rg4O8bYjRK7ERVR0wLrCLaYQ8NVjAoa6jjzjXRQGyYEagPHTVHcjMRNSNwcxS1I3JTELVHcisTNSNwaxW1I3JzEbVHcjsQtSNwexbkkbkn3Quw+2lKx'
        b'QxBuqxHpmRkJmTNdqOf+EzsSKAf355+Mh3L4hXp4v7aeQIPfKYxIhlhQwCSiHlp9zxw7vowwFU8YN6K0r3krMtpOBCrCVj9zYucYBlHWZWEXmhEcsQvOoStrJ3ats1/E'
        b'Ny0XegyZEOS1zJxUmQe6uK0oJ7i8o2mC0iqJXC7ww77JG6V1ckl1Gd62ZdJqoZmZfz4GeKQdBmL/lzUl8poqaT3txRJ7OqyqwZqX2JOitLaedn5JQCf9g8zqllJYc3vI'
        b'VFLWKJNjLcwhc+1PokxpQjuUQ8mssvLGIVZlNUpbIi2TNSxBaSa1qFXLaurKSk3GUTaRVq2nDHXkR12KEvM0PLJsNKYcNC5GRKHZUuduwiTfwGlotakbVWDgfqLAdIzY'
        b'zCTRlAjTnks1FKZJHqIlZpZeLauXEds/LUzy6NjKquX1kupSqR59UzcYsVp0Tr1fT1xSq1yK3Xb6JdEqrbQrdiHtQS9RoNUrphGTBQ212HQ5SlAmWySrlweNewvt3F77'
        b'Hux89Gfegh6PvqNaIKmqrZAEvuhVMYLSCvSKUuIiVOdiUzuTL+4T/VTgl42IBr1y1Ln8z/Zo0vgeIRKhvUOmTCsUVElKpFUCP/TT0EGmMGicq0oyKXLylrFNIWPhF2bQ'
        b'FaHuRYgMYwVZBPEIl5oenKVzLEp3C60VsaS0ArsKJe8knlrREtFiozaUVEnLtGtibKk8FNZU005GUUkCjYridE+1K4kek/R6natViXZYSqT1y6TSakGEwK+M9lYpJIsw'
        b'Wtfw0aVDDxMdE8jKtAMaPn5AR9eX1kWnNiaoky6SydGIoLWMljyZTpGgQTusDdXYleYvepi3piXI7AgsXX3gi6Wr5WYhFFHqDYxdPGoaqfW4nUcMI7OEcAP2fSHKwdzv'
        b'DENHcZsSLGzgDS9auymWS/lRlI1RQvH8dzJ5lNYTI+KIdyE+vC/pxTXTtRKv8IYVd9ZawOMz6Mb+PhALeE18jPOKLZZWzqJod/J9cLv/C5s76pciAN4ghqMG1py9YKs5'
        b'6AqFZ0m996dg+/e/JVsLikU/SqIp4nOyFLSCPS+sNz1APFoXUJbg6tbCPaZgXyWH1BYRh+XjT82weNqz0Yw2OJXGC19UF9xK5FFwF7jpDneNb+M1c3CM50QqPfcSFk4/'
        b'bWLbFIuMIuVaK9YNYJ/1i6r1wzIXuAdudMBa2AZ13gBnzOFWsNNH1r65jyU/jSrJm/ztpnemWCV5WBgPf5t9j//OA9P5813iXl1ZlWP1l8B/RK8oUs32HnhvYlL+xq7h'
        b'Z1f/+sPal5/kVU2pzR8OumF+PqFg1ep19j843j7yxy+sat+meMm354hHTm4/vXzF/ctJRyTfVh2YLq8s/+bJn//cdG/pzj9PfiPr/g8nV83/sNjnntlOh8lv/fFWZOUH'
        b'ISHOmxM/NPMPW/zle08XwejZk++9ufPqP+dumbVQ7Xj3c9M7z4TDd32EZrTWQWeiiV5EBrfDzTlaEZkp3EakaDELQJuBQ3hwHHSP6iWsAreJKGcW2CowrIQoAsNjcDdW'
        b'tGTDC/AMvEh7OVmfDjeDHXAf7BwVuhkI3CSriY7EAmFcgAwc0cpyCFCdKThFHoFrnulgx3RjIg2kJYFiQCPZxsAOsB6timNSrWyLCLZmmROB5RxwiYOedaNHe7Q0ohdY'
        b'SubRYqbt/jywoyI+mJ5uvXwtG956jGGackBnAX0bDYSX4TU5lr/C4/A4lttlEYlsoBGVDTYag8Nm8MT/mE8jkD62o8fsWEQfHg0q+7BpAuU1satUKTxWrfachMF4Bu0d'
        b'm+sPrGlZo7b3VXqo7QMIfM90tVNaPzdtwDsYw/d4kEwanp+K9veWqLYPJNnS1U4Z/dwMxBN1iZX8YwvUHuEY0oeu86WWl9T2E5W2ant/knma2ml6P3e61sdJRybKaUrn'
        b'XN6yvDVegWr1oV3HqZ2S+rlJD1zcSZbfVLmH8JRbl5vaI/SXs3r5NLP/aCN43i3GHzDD+w4O+nGgwsG7OFDj4L1ftl7TOcQYZ8FGxAOfYLECunLK41Ds2VNsKzmBwZhJ'
        b'PJDN/E2+x/A+ddQojLpkPuU/gx+qGIXO0V3AfgqDSE9WoxBEBagLBkA69PVu9I71AnCf/xx+SAtkY1FkcIH7KSAZjGQ/G7esW9cyt3EtI9ccfbv+O2yd0Uvez7VnHm6P'
        b'HlvHnW7P6K3ruYH6b4Ck2EXoSvhzbVmI2vJIB7Iz5+Acuk3OdJsMrpH/q/agm+PPtUeCx+YbxujY+OnvmJLxSFHy/7pRFaOzNnor/LmWlY2dNScs8De4QP6PBsi0aPSS'
        b'+XNtWfR8W9Bs6a6nBm0RMom8kZY86uzmckpZBm/HYNrEcI44JjQ1MHU1Inwids1gSpwTYteElgVWERY6w1fj/6HhK+IUGwpQY8wSy8qwl5xq6TLDWUerg/jLSUV8BR3B'
        b'zLakrAzdwtHdXaJlq4gbHOxWQSRYVFfTUEvz2xJBac2SElk18eFuhsjJX4cO5i8S+BsCmaE4wUpDmUpqairxqzGvTxgJ+rXYY7yeWdVVFCsQ1yzBLBUtCsDuIbQYYpKS'
        b'mgbaqw+eI2nZaF8wG4P900txl8pk5eWIpUB7AM3MjG2kdjyIpx/U7UVaZxZlOl6oVFJNWKGf40tDIw24OYFfTS3xQlSl5+sMx4HmeZ5bdgK/xJI6aWlFdUP1IrmWSSUu'
        b'LkhD9PMil8sWVZOpCSJ9NKhI62BKIDNstQzxe4i3I7WM8nGhZNAjY3TsHK45VCjCwhZBmbSkHteLcpQiTkyGI6WjHCahAhnJL5fWk75Hx6A5m4btaYmwZjxpyaTyWN2c'
        b'orpl9doM9DiQFB276ieuqarCLGqNUODvvwTz7Oj1y/39dcw+adGYGugkfRXTUXerA4PT0P5a/XNV0UhnWg60Rk4arEU/e2F+TKx0bkPyDRJk65hlQs41JYulpfUCMoI0'
        b'DYlzoyNDQrWCLCynoqk36MWvGWOvHDtOqNBYIyuV6ggmSVolXVSO8wkF80LDFryoijDtMDdI6ebJqklD8CpIScnOnjMHtxR7vsJNrZUsX0L8ZEnr8OYrEixB46JjvQ1e'
        b'GDb2hdrhw8gGY8cTp4wVjNDUFTxKWeS19FUhCTUa0z4ug6oPD1nw/OqplC4fFfMYkBlKRRRaLZfRL60pJ7VKyhajmSH9wRmIsy9JE/5Nr21aADQmk5xIpGSlFfWyRbgp'
        b'8tKKKngL7SxVwlh9mUABmhdxvbQBLXZdBkQBMoG2C2iFLUEUmVoQmC+pL5FiKVyZtiSaDtpfTlXDkkppRZ02OXxcMqlN0lC+oqFeinYm7P1QUFhTJycv1ZaJiBUkNpRX'
        b'SEsaMCmiDIkN9TV4f6zUZpgUK0ivLpM1ytDkV1WhDAVL5JL6FfJxLdfmjnxRE365Q1EvKiYzeO2Sn39t9IvK/3y/YkjH9UMzbmRIkE/PNBaXjXvvczNp2LzyOvR2P9xX'
        b'XZ2SkhUNi4T66TPMLojy0U/gmAehMT76aaoOluinZGy2SB/98OuzoUHVvd8gT7Rhsu7VMWMyo/fqNiwtggFaMdpfZH9GZzBai6NL3U9M75G6DVYPiBArSEYRAR1DZ4Zf'
        b'JopKq9H/0bQK8J4TveD5YmFji4WNKxY2phhBVaC3jMLE/MD0FIFfgbge/cX7yyRdNh3qAp01tYCsZJwg8ENEqZ1iNKz6bjTUoSO/FO0WydpfIoHBWZdaMFPgNwser6hD'
        b'RIbeFaF/lQGgg76wLln70tGi8sqGOrlwzPH3U8cnOTr1J6HuCEscI6l98ZlAICViBTn4j2BeWMiCn84WRmcLI9n0ozGKRaE9MrVxfME2HGcCTIGy4D/owQIz/SpJk9bV'
        b'VQdPq5M0oKAqKHiaDJ1m+lVBHuvXAs6np39cQL8ADEsiqk+tQIcKWst60id1oTOnjK5mtHHo1JRK6/HOi/+iAyJyzPlTUtMUK8DfkdD+X45PSZSA+hAyJhNGzKBzSaoE'
        b'ODImR6msHhMMCsccPzQMCH5C/yAFRfhcDwwPjYxEI61/B0bcQC/Af8bMQLkEtW4aIlrDRILJgUYA/xHMiwwZvyy0S8JwhkbRQGIFSegXfXLOC4sa81xHWiTL2C8BY/o7'
        b'iiGizUmPh35xYqQQdIQkJeag4dCvkBJZKSqQnoyqQhTyC+4wtdL4a7FMit30KfpVbHFz6WT6mzJ8eUoqVlzT2lHDvWA9bUsNT0Ia6OHfyRzKROTBoBKKRUw7Fm2aGQV6'
        b'4drMdHgyByuy0UbehxpJ/pXlPEoU58egBMWr2DOaaI1x4nNZSXxrLisJooJm8ukv2i2TYR88C3dm6s2hafyMm/Aaqc3fcxXj6cRKBhUimbysJp1qwF9SwUZwBewMQNkz'
        b'sBsNrCQJzmbMB2uzaQBHCl4EO2ZSTRGmi1jWxMI0OS0HIzU29cQ843zA9yjeScu44RY/9hicRi1II64kjRZhFqZBJbhg8M1gF2i3EDZmEyGa7PFLCSy5MeI6U1iuh/Pe'
        b'yoAJ3CnLwpY3vPtS0rzkxGU3QmaIHDaed5D7Csoc+v928kfnZ5qOSLVZaaSVBeuvDe/86Y2vnAtr/mb2xqPza33aGg/us9Ssv/KOzWs1RzYcviazcr5kxbmsTnKdc2rx'
        b'rPXTjobU2Z8qrVXOsL0FZ4Qqgrrjjhc9+WLDzZl3avYcWP/nrr+++ff2tHeUZquLQm95tZ/clvv2TM1XGxb/7vrDJT2nDlYV+txZFjj0ZOGKrM8+XuM/3ynX7aOUyrWv'
        b'Hypvf3Q2pqp/0fy3zs66sePNllsHv3d9e/og/Et5fOuGy86DX+/PmPupPa8i7I3XKk5dMpYuilnc8M2r66d0746tWv/jIk7s93t8f/ye4TMnJK21RWhCNERnw+sNxBZw'
        b'q7veHDCslJZZ3yzJBWeyVsMjOv/nxpD2OZ4NjsOLAXBb7hqwKR2cZVNGVUzPTNBH5NHV8VVE7B4Az4ziNdJSd3jR/DGmioVLbCrh0fES6RdIo8EOuI7o3ILToBvsMfd3'
        b'RKQ5FglSiwLpUELE5XOxG1k5OJe0IC0n0I+oku7BKq3NLNAD17s+xhS+3MQvM2vN3HQGxZzJ8IcdYJ/Q+n/pIQp7ljWw7RtrqTJkoRNZjpr3ZTC08HhulECkcQ9RLsUQ'
        b'9s5t9Wp7r4+cfQd8/dosMMiZt6KxS9TD0vAiVLyIQd+AbnGPfU9Zb+TFqrvhd5P6I6drIrNVkdn3S9WRM9WB4n7f/DZ2W2G7BfbQbdQeR3vsbkkZcHBTeKsdJpKq/dvw'
        b'Y+z8u0OX4TMsjZ6qdkro5yZglzPzlTH9jpOaWQP2jm1lGrcglVuQ2j6IgFBqnANUzgFqnqiHo+ZN+pObf39Ajtott5+fO8xkOYQOhsT0eveHpN61fzckFetuEtMiexU/'
        b'cNiIZRtIdBu9VVxvhZgofAa+yw1UcSf1sNXcSU8fG1MuPo8oBqrFLUCZrHYL6eeH/GuYhRL+9diE4nugZ7aBg06+SpbaSdTPFeFntoHfE7RBaOmYwqagt3uKG/Uq2yzF'
        b'mfWqlUmKI+tVRw7+7WaWMon1qp9JSgjr1RAO+k3L2a1pObteUoUNTn+ThdI4KhjjfHqMvRILzfxiLG3Hny4xwNcMZwYjFMvaQzE6YehvUSH8jnoBGDA5VwgYMFsLOs4p'
        b'oAqMdCiY/1vg8XIhs26EGucNyP25482HPt5+YGOkHoG5UUJxFq9BRhEsGLAHHMkAN8F1eQPG69jFptCqZqwOhrf1SIZwmxysNWdRsD2fmkXNmiukoTwuwS3VYroMA950'
        b'tKDglcUJ5E0m+asZT5nKWcwQycoMxkQtBMIOH64L3KmzOgLn4GZibGIGti0FJ7P1dkp9K0ktsY34u7DJMmtBscWc4iradkj9EjE9qmHUFlvYhLrQFiliF5wYEsSpLRbt'
        b'LGfTOR/G4c/VNhWMvGJRrV0cnZMdjRNruZYocdfkJXTOx07E9MiTYVMsOrOskM6pdMAwDs1zUGJWz3x3OvHtZdgeqSefJSjO+vfcUfyu5ulgkzgvL4+iGClwiw0F1sHN'
        b'NvQYvTK7PDwkBOP3wOOzwBYKroP7aFMieBw0g1PiPApsa8BG8CfRM78MGp9ncz1QsFaOM3BC/+sk4xUWBzpRpYG2aNyxfRPcWErgOMBZkZ+YouLmYCdkZuAoSeS/BNvD'
        b'2ZTbamxYBjdlkMuGMbgOt2Brpfkh2FYJbF5IUC9cWShdZ5PEgJvBvhJsk7QPXCaoF3bgJGwR5wnQAgKXHYrgSSPQBe7k097KrsFj9aAX9I23TQIncmjTIYLVw8YWbWtr'
        b'zIuLs363UkYPqnUcTmwuRetWtMK3hDZeK60ToiG1IYgiGygJ2Ab306hapVi7wYbFSiiOo5xLtRZhe0WgXZwHFEJENatBK+w2h11wdzSxCIuG6xfKLcND2GiQz1iAtRS8'
        b'bTFR1nQsniXHcHQ2ZjdP5GfmggSbIx9eu/W5hLHc9Krdd0nD4LWUC3WfXIKvh5s+HCj69I/P/l71wYKQmzZOQ8f3tP/zzuGRLc/MLzTftbO7FmjaE/zJ4KWCf1t90nph'
        b'C2X68fehaXdK2n/w0fwj5u5EdtpVxdX7jo+z4n6XWntwHrPui8AM6p0v92y7tGTHEWXs8XijCS/nKGMen7g+6e5k9cJv7r9l0rOq+avwdKnzqwlzZNHRpwOOrN62X9zx'
        b'Rsbfrp3jdbHE4f/s9npqNnjbZjDkfgd3zu7clPNfHxJlw3djS77glYW2lM67yD2d8Mbpu0s8VjVtdA8w7TKOnLvTdeeCr0f+6Juz/cjW27feOWl15i+D8ZPfEz2duu70'
        b'vy5uWX3r2ErF4vQfWt4uHo7YF8+9+KpHY+0Vl/bqpvqnUe/P/XF3RWmVX3LDvtvbKlf4qK+Ztpa3fvVSTvbk5ZOvn/jDR7eiQrMKaj79avsXv/d/8lnPzj8UisLiVlvc'
        b'eTfwxHWHeFHAAan4pPPeyLJDglnfTGtL/u5f1rMHZ5w0ChNyyb0E9oEN0QbXEnij9qduJqlLaEjs87AHKuApfgDRM0CPTeBNJmiZBRTkCgXPg01gHbr8ZjEotgfYE8oA'
        b'hwu9aNuPLdEx8By4MYpATeNPJ0SSh66rVxv6ggW3KhngImxLoJENjsCroC/zOc9B4HK+MSVI5ZhGWtAv3xdbo7U/YqGGnPZhAEW1O7GlSV2JlhNtfuRPgKyI+dENeJZc'
        b'4FxcHfVKEWD/dJ3xEWjm0iZSR9HbzulspCrAOQZ2wOsZCU+Ta1i2KIkYJwWB7eNVJcAJcIDgbixOKdNiTbAzp9ihu2VdKnm5M7wBdmWOgYrwqLQCG1hJthNpxY9WeJ1j'
        b'aJQEL8BOYpZkBTeQKtio2JlMQyCJSqC0Ws1KgedCaQfEfXB9ArZJ4i0bpzIB2+BBGijjkH+jztqIzeQBBQMciQLt9MNLYH9Ucdk4ayPTUNrN0p3loJPYmMFucHS8zkaS'
        b'Fu4i3TlzvOJJLDzMGdU7ueH/H/ib118y8Ac/ra95ctU08DV/hqlFk3AnvuaxnyPzAYG3RhCiEoTQ5usaQUxzGoYRb8Io4xic3FWgcOiYq/RoX9g87UFwFMYnP7OmObXN'
        b'T1GocgpQcUUPuO60nYqi7tSyrmUDfOcBvpvCsd16gC/Q8APRla8H3fsiNPwpvVwNP/UuFwP05p+a0zWnh6Hmh2n40Sp+dK+tmljId1pjwxFcSClR80N67Hrs+/mT8AMr'
        b'7IieYJbPUPODe5g9rH5+BNbVTtO4hKpcQsdW1ZvUm9zPTyDPO7Pbs9V8fw0/RMXHVkd82uqIHz2+gQm9PA0/4+60F6ZX3E3TpBSoUgo0KQtVKQv7ixapUyp+S05Xut8L'
        b'uxb2oB5EofFQoSFBvUxA49Vlr5h9zFWF4dldyQhq/+EOpBDtFCtFnZLRz/f/qURUyQDfHTVoeJJziOMjytmPNxJJ8d1aGtsq1DzfkShnB+FDa8ojdngag3L37Kxor1Cs'
        b'VLuFN5t/ZM9/4D3x1PSu6T85zqTmn5gc0i2NT6TKB9s88WPRKKj42OYJ41noaWGUJIZtTQNR80x9eCN2+uYpAx7am/pEIrqa2JI9zKX4rs0WzwOB/7ySCwECH78U6pwQ'
        b'0X/GMrDWSXVnMOyGf6u1Tjmui8kY58dF5+yPYM9ztJCvbK3OOPbnYqSDezX6H8K9bkS3bg5j3K37eZhm45wGYgN52xbt1oenE5/veWnouEKnEujOT9N5Kk+Dm41r4cYG'
        b'+irTDDpdYCs4g3XZ6sIpVhUDrC+H+8mlKAE9vRpgjDF2lNiMGyinkvvcXCxzCchlUoyZVEAtPLhKLOu7uIgtf4yeJf25mXboZ4t9CLWFvpYUnT3BQ2SpTNs+gRX049lX'
        b'/5abz/77It+MQOy+zzcrvs12YuebfODw6i7ZeuHeP7AOOry6Y178VndxUJspbJyl6BjYu7acE76l52BSsu+e0L0eaTbXB4GFW4mFxYksCwvOm107E0Gbv9fe7HaBiGNU'
        b'ZGpkVC2wzBdu/yCLs7l+viRot3Czzx/Y9yRB23LffTew33LjD5+zH80yuWkXNJJWetlrr+lf/lzsyN+xzWOPz16fNEfxar9wkH2veCt3YVDzcMaivLL+xKfWyvhd6esS'
        b'3fxY+fav3y1+S/RO8+v3262oiKiJUSMPhdaPMbXagpYgMuyUcy7FjmKA8/CAN7E0FYDuifgEIJcLzgIZuj7sYK5G+/822oT4mj2LPN6GzXfBMXAth+kCLsEdtN5fMzxu'
        b'jk9xURA4uzSdZDKHPUx4yyGCZJg/Fb6M7jFXlgWC8w20tMQUnGKCY/BaEA0wdQidU52ZIrA7F+ytRId0EIMyT2DCNtCRQRsQX0whHh63BecGohbEokPeH2xKogsrwH5P'
        b'fASCQ+DMqE8Q4hCkbBa5f4SuAltQ69PhLnQvMrLOXMj0gufS6AP4CjwL9mB/9ibgNLptBQmZlDXsZKHb0i6ooM19D1gJM7GqZXAOBnrdC8/FMXnwKLxEX7wOgpuSzFHS'
        b'DYfrKVMuE/srBDfICV0ALuNxgrtGx+7gpCQm35lJHk4Bd9J016vqhRSxHwfdE0ir6+RFAVqzXyPYaw6UTBE47/hfQz2NygH0Ht6HLHXns1zSSLsGYWplQRkeFNfxQFRL'
        b'1IH4lniFt8beV2Xvq0y6ML17+oXs7uxeb41oqko09W7SGxn3Mu7Xa1LyVSn5f3Ly6PeMUjtFY1tatFFbtFt0WKET3p5Hux3W2Pup7P2Ujhr7EJV9yKCTh8JbyVLOVzvF'
        b'NicPTAw4VdlVeXJJu1kbG+3YuLAi/31+yEPs8P4Bl3cgvSV9X+YDZ9fOqPaozvj2eKW3xjlY5Rw8wHfqNGk3UXAPWY2pZNDVQ+F5yrfL95SoS6Ss78lXe8b2prznmnh3'
        b'5oCLW2dae5oi/1DOCItyS2KoXBO/xe/52DXxfdfE7+VYF+g1jl2qN+c1b7PUcFNDv4t1rF/UdKQHnvayOMZykziLx/aC7mwDrJiVAgaDj70s/hZfJMQphNBkyLwIW2hK'
        b'sEaMvO7PuP6/4uBLHHyNg4c4eIyDEVyCTcQZNHo5QTQ30Z1vTPI7R8h9oRGnC4MytOT8Fdqg9xnELVW9dImcljqRo9BRZ49p+z+UehqMOx7pteP/o8f/bYY2wMZN8ioG'
        b'sdl8yGZb2nxrgT3Es7qS25ZfLL0n/p393fTBCS6KgFfsXxH3mv4uGfuHn4FtheMTGCMsX8uJDykUYOfwKJWN4zMZo8ackdiYM5oYc2q92WODT+fIrZl6Y85J2Jgzihhz'
        b'2jsP2kwc4IaiFPvwrcn6lHicksAgSdpiIbhYmKFV6GjKtyaoA8MU0yqb0S6/aP+Q/BriOR9M6Zqg8YhSeUT1mqo8kjQeaSqPNLVHhtolc8jNsytG4xWj8orpnajyStR4'
        b'TVd5TVd7pavdMlB/XTMZjygGP4vxkIXrGjFqYFgGPqFw+MgYpwyTlJFqVoyl6zCFgm8bGagR7V4qS7cRJtcyYJhCwSMWZeX+CEdp+0R87Kyqi5Mj9ggeALdo+TuHsnRi'
        b'wtbGl4SMHNkPX/sz5MlockIWmkpnvF29PsHmiINj3g88h6upr4VH/a0rvWPh92x4KCvt4JVJofcqO4//44PBL9ZPrBtq/8eyA5rsz/OrTwRc+PbMA95HRqZ7l5pJ+/IE'
        b'7qf/6r72nWU9K7+q+Oia0utv9se+cEgd2V9q897b3j+wH1Qs6h15HOameuf3Mff3hryqqpia9H7sLsebu77M9Dkn/vBUkKUsSXxQdcjxynGHr/3eTrbQ1Fp9KdjMbbMN'
        b'tRM3V37VMcVq+x/6PuBsvPiOgxVngi038mrjvCrRwGdG8jdT8rY49753rFn8+rtel7JLhvpZU97dzxz63DbntdL3vXlPynmbZsS0XXwz7sl7vSc9Tr1t+ejs4iK7iMlF'
        b'/+CpD656Yr7U46W3Xr/wpMpL/drlJZ5n5lx884rEx/Vb09ePLviw4YtDxdaT/ayFLg3/enL7L19fePbgtUFw/csj/6a++mfG8FZKyHqMZY4vwQsr4Q7EA4I+E4ygvRvs'
        b'aiAHYQjogQcNjBTQEQ2PBpGvJUVgG7FRAAcWwc6xHrBawMsG3z584Hah9/ilaPKzwf/Fwv8Ptgpv+mxMIP89t2eM2z2wkXxVjaSsqKguDG3h5LxMQlT6b3ReRlCWDsNs'
        b'Y1PeoLVdc9iOZW0eO1a1yxVhCknXpI4Vyhkday5699T1elxs6J1xsely0L2U+3YwTR2W9Se+U1tYm6R9UoepIgNxXj08xDz2x+WoeDn9M/P7CwpVM2epebP+5ChQ2LVW'
        b'99t4Y0dFsxnDZpQdtzmxxWFr0kiEran3CIUDP1/TwBEKBcM4GMlnxJk6NRc+ptCfkZcY3qZObY6PKfRnOIdBmdmMMOvYpgEjlD58QkK0YM1shsnD4XpTij9Raa7ihW+1'
        b'GDEyMeWPONaxTF1QdhQ+IeHwYmNS2UxSjT58RIe4sofk4dPhRD7DNJ0xaOd+3KI/cJpaMF1tl9ZvkUaft9sTXVIcqFcd7FP8tN9DXIeYaKz/s+8f/zf0gsU/xWM/rb3o'
        b'mMHkQQInQiMUzfKFMhg2+AuLQfBbzBrwdeKM0WTqpnmiEUv2V08NJT+PkgK2lUh3ppuBBG7KmhXfeJt5RrN9XaoV86z7b4e/n/HU2ObOqeFoH7OPZqXbsCsfnVYe/UNm'
        b'4dnBHukbR1jTg4recwyUrrD529EvcqMeNZw6+tdjCUsfPnur8Meqgneyn1V7N16Z+ZLycubCfE27y0xu5/qNQR/MP5mRdTp12eDniU7bP7DhRliI/KPf4wOv4o2hE9tK'
        b'Nsc4iWwuAiefawOSPfCibHXyiODJ4hFuZ80rlGdl1whiSPAYipYl4kt9Lv4gvzPTmDIHl5hgO+iAygXwHH1BV8BdJmCDJDM3EF7EOfH93xbeYqE79rkcGtS1zxe0gR1g'
        b'D9yDpVdYUGpMWdmhO7yFG1zHJftegD+8kJkeUZrtn21MGbGZJiXgDLllzwXd8BrcEWxEMcQU2Io4omPwTjQpA7eYUwEZHIqRSWHX4rAtDTTTUse+aQEYgXw3ehsWWpoL'
        b'mfXwIGwG533Jc3erHLnBY7N0JjgCb4OeTLiOMCwJ4PK0TCLbpeWGVnA7CyjhKzmuYD/h0yzD4EmCh7+gjNaUAAdABylqzvchnDCtasChLOyZYnAQXkFcxi0aselY/SzE'
        b'S20X1WpzmIHLTHgO7EOczvmVZB+H28CNUJTnkgXYumxpA7y8FPaFWSxtYFA8uIcFdgIlWE8LOG/4gJ2ZBP4Kdwe9HRxkghtwJzwqW0SEhy4e5XjggzPBRRE6Dnbjz9w4'
        b'wZhy9maDDVyp0O9XHwX/X54MBmvej5wRCaP//cwpMcaeCQfkiMA37Wdo/T9yojj2A5ZcjaUbuh8dalJb+q2dNsA225K1Lqvf1uN49Hts0QdsS/TvQ7b7x2zfj9mBH7K9'
        b'Rozm2nDQjqoPn5BwuElAWXDX5hqIp9yHWFXS6iE21ssf4tQ31FZJh9hVMnn9EBsLX4fYNbXoMUteXzfEKVleL5UPsUtqaqqGWLLq+iFOOTra0J86rDaHfcnWNtQPsUor'
        b'6oZYNXVlQ0aIv6iXosgSSe0Qa4WsdogjkZfKZEOsCmkTyoKqN5PJR03Yh4xqG0qqZKVDxrSxv3zIXF4hK68vktbV1dQNWdZK6uTSIpm8BmtaD1k2VJdWSGTV0rIiaVPp'
        b'kGlRkVyKWl9UNGREazLrjwA5XvfFP/efQDBuDrDLNDlmZZ49e4Y/dNsyGGUsvPmODR+S8Lfsx/jMumdilMin7vHNE71Y35uUY+X90oqgIZuiIu1v7YXheydtXFArKa2U'
        b'LJJqAREkZdKyHKEJ4a2GjIuKJFVV6MQjbccs2JAZGs+6evkyWX3FkFFVTamkSj5kMRPrUS+RpuKxrJMwtdNPEwJ9T4lbUlPWUCWNr1vEpE1v5FkoGGYxGIyHqGvsYSvK'
        b'3HKt8bfsKhsGd3ihB2VqqzFxVpk4t2VoTHxVJr79ovh7E6GfWpQxYGIzaObYzwtXm0X0syMGKZtm/h8pJ/K2/wf+3Sp+'
    ))))
