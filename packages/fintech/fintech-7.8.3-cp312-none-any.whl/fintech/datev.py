
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
        b'eJzsvQlYVEe6MHx6Zd+bffGw00A3++4GKrKjAi64QEM30No02IsLiUaNkVZQQaKAS8RoFFwS1BjRGJNUzZJkMjO0mBG5ZsbMZBYzMxmNJt7JvUn+qjrdTTc0Jmbmu/f7'
        b'n+cj8XSdt5bzVtVb71bbHyizP47h9+Fq9OimpFQlVU9VsqSs7VQlW8ZZbUdN+pOyz7CYkMpOymFTMt4ZQ8w6Sm23nI0gfCnXmGYbC73byEx5WNRGnl2DkP/1Jvu52eXz'
        b'FtONTVKtQkY31dGaBhm9YKOmoUlJ58qVGlltA90sqV0jqZeJ7e3LG+RqY1qprE6ulKnpOq2yViNvUqppiVJK1yokarVMba9pomtVMolGRjMfkEo0Elq2obZBoqyX0XVy'
        b'hUwttq8NMKtRIPrngBvhQ/RopVpZrexWTiu3ldfKb7VptW21a7VvdWh1bHVqdW51aXVtdWt1b/VoFbR6tnq1erf6tPq2+rX6twZ0Uzp/nbfOXWers9E56bg6F529zkPn'
        b'qLPTeeooHUfnqhPoeDpnna/OS+eg89HxdWwdS+enC9C51QWiJrfdFMimdvobm3NTkB3Fpp4NNL6jcJAxzKI2B24OKqNCrUDXUxs4y6j1LLvtQnZJrXnX+aF/HriiXNLb'
        b'GymhfYnCFoVnsTgUgkUdcqmODa2qpbTBCDg3SgPb4M7SooVQB3eXClO84e78igUiPhU5jwvfnh8qZGlxidGByer8YrgHthfDdhZlPx++kM8Gg3C/u5Ct9UIJstmwqzA/'
        b'Np9HcbmsaDAAjsJueEjrj6LAoCt8FceJ4E6UnwePu1HOcBenhOWBMk/DKV4BL8PjoA3uim1G6LSjUuzBEDwPLrLB65sqtCEojTYGbEMpLjgC3XqfGWu18OJax7VaFuUN'
        b'93JAOzwFBxCqYSghfH013AfawN64QlE0xhjuxW82FNy7yj+MC54Hh0pqWWYt5m9ssX3osd+vFbUa6kgu6kYKdZ8N6mo71MkOqJOdUMe6oC52QwTggTraE3WyN+pkX9TB'
        b'/rqAOn/SwWg07LQxdTCbdDDLrIPZZl3J2sw2dPAEqKmD6yZ2sPekDg5kOriDw6ccm1Fv0dWxNm58igC/WM6muM1ViAdUOx6dLjQAuXaUa9S3fKq62jEuQs4AOzN4lK1m'
        b'NZuaXV20JqSYGqAU9gh8ap4v99HmckQsn0R+wX4j4eWoRkqBWcZP1L2sQZulGbazqxPvJH6XcIcBZzQ/dHnR5cp69oK7rG+XpobupMYorRh38gA4vRn1blvcwqgouCtu'
        b'Q0OeCO4CA+VRBcVwb6w4X1RQzKKULnYz4NvwTYsecjBWWYV7yMHQQzyL3qFw/9Q5mHqA+2/rgfqJPWAzqQccS1S4CbUCTH/XF8PrZYtEm+jFbIrNoeAReYsWJwd7VsLt'
        b'ZWwKHJiBPhgKXoEva90RfDG8trpsERsczqaoBmpePNxOkgfBF8Fx2MWhasHbVBwVB/rSSfK14C1P2MWilsAzlIgSgVMyrScCe5aB62XFC+GAH9zNo9jPsALg85u1ESim'
        b'GrSF4lEVU4jGws6ihVFgYCE4F5tHhrkYDvDAthDYQwoBR8EQOAUu8inwFuynplPTV4MT8offvUapf4miHdU9hz6YcWTrzmNdF7vWpIRyfDRr989e5uhou9B7x+gRR8eE'
        b'B81Fjo6XHC+1p7Q7KYTtR1akOKbOvhI0s88uIKX9yJ0zvfTptrCyntU+F3t842fbq+0diio8/d/j9/vyFySNflJ3n5o3tMZHIt5yRvPCaelfpQW1284cyK7Y/ZHyN4LU'
        b'npYhecaCkZ5PIuy2FrFr1m2X+ygbWj+ruSedp3o+avjXZ5f+Tfbz4bevbQ8U/4KV3GYj8Y4qr/5bRK7XDsGvYkuKktwSPD58p9eZuvxOVsdXkULeIywgGhcuLoS7Y+Du'
        b'YlEBZl/ucGgmaOfAVvBSEUmAmMkBMBBTIIK6/KISHjgJeigHcJ4Nj4TNeRSEG+0gGIBvxIiFFDxXEMPwOMoFbuE0gd3wZZJkoxa+5gAGYvO0iCXtimNTbvAqOAwOc8A5'
        b'cIZ+5IOSeIE3FqNe2gX3pjbDdsSqM1jgPDiQJ3QaY0cJVa4oyY98qJ3Qg6a3jP997TW9TtXUIlMiUUmEsBgJUNm6mWNOKplSKlNVqWS1TSppi+UrG5f1JXr85xbqwbMs'
        b'ysuvJ6JrhS73TkB4X91vAkSdth2sjpRRD5+OGaN0SEduT8K+/Nue0/p4feqbnjGjdES/52uBA4GD6qG5I8JsPZ09McltOrRv3nF7M3A/r3/9cGTaTc90Q9wtOlFPJw4m'
        b'DXFG6Onm+TU3PWNRmmNz+nnHC467mJfB7W9gyhilw085H3PuXzdCpzIJPvULHQ5LucIdqnjTQR82Z8Rv7rBg7v1AKlB8P4gSeHend6b35I54hA47hj7EI1+Fh77QeYzP'
        b'tMiYTVWVSqusqhpzqKqqVcgkSm0zgvzIbnLGY9Win1RuOBIP+gldMQunz0CPf26hHj/DYrEEX1Ho8Ymzd9uaLQ732TyW4LaDe1vGJ1yX7cWjti63bT3+8wGP4rka375W'
        b'Y351kB9NnXZI4VhwN5O6WI2ZLa+bkmFlEamKUlYlB/3jyqlKHvrlS9mVNlJbHVXHknK221UyIe5220o7EuKhkD1iyywdu44j5aM3B6IhcdGbDXpz3Ii1F7sx/iJSpRLS'
        b'trUcM0y4Rj5bhzFhMVpbNy6RImViVo+U050m5XQTl7B6jhmr55oxdc5mroHVT4BOzeo5k1g9lxG2Sh/uon+yUb/NrlYcLQig5Ct+PUypV6KYXd8+PPTB9CPHujLaWB6a'
        b'C3ns930i6LaMl9wiKh0W/XLbQGZbYNnZHZKU8ir7Ws+8uNB1bwkdU9oX0ct7qkN66aAVssiyTtcFkWleaYnvKqql/dycX/EUGurTaW71NXVC/iOsyYJt/hkxRvVmJxyA'
        b'e2P4lAs4yWmBb+Y+wgpbqS3sZ1KA122xDsShHGM5Nu7wbRIN2p4BZzzAlULYVoQ0PiGfsgW72Bs2gRceYf2CD14G7bmLsNQozAfnECCd7bs5g2SFL8Hja0FvM2grRTod'
        b'l+LBwyzEzV4H+x/54pIPwUvw1XnwUIwoj+iDtvB1NtgemSbkTU36PCOHIhQ/ZltVJVfKNVVVLS4McYiNAMKDqhkedF/DpmLjX5sxMGPIWx+TrXeN6uC+6NizelTg013Y'
        b'WXhLEK4XhPetHhEkDGbrBSkdrNGgkKNretf0h/Qn9DShtA6jgdPQj/1tD29Dnj7uR4Lw+xxK4KPyMA13/hhXLVPUjXGxlTFms06mUiODRIXlpcrLVAU+Hr3VePwyoxZr'
        b'15PQX45TJqPHf22hvlKzWazgpxiyDzHdvcgPo044xHFq2dYGSo1poDDDpI5NBgnbQh/i2FloO+YDBg0H9maOYZBMgJoGScPEQWL6vNkg0cag8CrYCToc4O50sBWR0h6k'
        b'+sG9ZXkMyS1csEiEFKRZ8BjfDQ6UyFcPLmWpZ6JMbeGvHeqe+UEyGkHHuhLQGHoxwevB/ni4AakTjhUKR8czvsH/HZHbJ/YqWrnsbz01R5pXvut4+B51TmXv8w9ayH2E'
        b'9fkmpF1dRcSNqLHfnMDhwZRHIYT+nZCovYjGzl64VyxqNohlv2bYupkLXlgFdj3CXctZrEU2x6Vic0rnPvMIVxaeSl9eWCpiUZHgFHsdK9sb9AjZZiSN+8dIz0g61Ms0'
        b'co2sEZG0u4kmTDBC1akGqp6Lya9Hc/SZ3mf0HtF3/MKHIzKHyvUR2SN+OcOCnFFv/+6WzpbuzZ2b+6Qj3jHDrjFmtMpT4dqNcZWSRtlECuURCjURaCwmUCvI1Bpp9Ost'
        b'1JdzOCyWz9PS6D5+CPWyg4jzv8zMfxidRqFw4KoARKVWSDQdDoxTaWKu/Nf57zJE+ku/GwyTfwKJ/uyRXUlE30yvok1HkBJ8Yd/WJA717Qt2n2WUCDmEVUZMhzswAwZ7'
        b'2WYkCo7nPMJGsUTGsUKgm0F3EyJQAUWURti/eQMi0NOLLFjxsWwhZyKH5RByHKdHtRV6VFvQY4KBHku+hx5DEdvttu+070m+4Uqbs01CiioR/iBvnUShnUSQE1lmsiVF'
        b'mtBpoMy4ZjGiyGlPQZGqcJTROrcklMgxcUtsT1J13P8DHHOSWsGbRIm8EmIkw5718Az2lZRDnUgkXsiBL+cVVEBdaVkUNh8q8pABJ2ZRGviWHd+7iRCvjUPQOPFu3mSd'
        b'w9qDXvlMyQaOWopyXMosOvRBIjHjrnSd75KneHB8BOru+MTZ2fZ/WB315s7zXfoXghfv2XrswLEdx7rC23ayOIjCk76y3T8ItEkfxZefT4inP6xm3ZPa2cKbvT/dKfyN'
        b'3eVDnccQiQdS//VfbqvFTsi6worK5kxwbYLhc9EFXkV2Dx9sIaoGpx4MGbUQnwWGMbC0lnBpRMt7SiYMAjV4iYwDNAjAlbVkHMEX4RsVRnUEHICvMeMgajWjkJwqAScY'
        b'ZcQdRRn0EQXo+16FxKSCj/G1zdhCanEyECfzSobJEmaYPFjKoXxC+sL6uTe9RXewWTFrxG/2sGD2fwTQHXMR0+5LPpV1LOuGt/hOkHA4euY7An30vJGg3GGf3Ps8KjD4'
        b'Pp9y88TD6JZrsN41uC/sI9dIs8FkwwymUPywHEVmSNtQBgZvtBxm4AFliXMjNc7dHy95Su7OjCVzz4yl5sEhnhniOTNwdOyJ4fzbPDE/gKNzSuTLeBI2ofPnlskwkw5+'
        b'IfhIJ6L1V7pEiFWfrds+XHEWOylmpxT1rL6w9Pxfnr8hdjx/2tExYfbKS+2Xikb//l7NzwVnJNtvr/jFClgOF0AFR/q4/+Kdz+Kpjz+o5KxfEs+pd6Dau9w2HngF6RuE'
        b'BE+gUVboUWGpTq+EbzIq8+Fc2GXSl8FVpJxgAvUAhwkXXx/XAtti8+FuER9p3q+DN1axQ8Er4OAj3NP1m+3N1PAlzyFFfH4VoocfYFBieqBpM70amatqjQrxfOdxJovf'
        b'LbTqBg7lP63H61hon/TUmmNrRkIS9b6JHfzR0MhTmccyb4Um6UOTfhOa0lnYMbcnfNQn4KhDr8MtH6HeR9gfNuIT15GNzGzGukaEHZb6gE/5hPctHvGOHXaNnSwepiRm'
        b'IhzMaHkupuUJeGuNxIzM4K/qETG7Pw0xY36LCOret4ighU7Y6MBaEzLm7auqmFkIFHasqlqrlSiYGEaY2daicVTfpNo4ZmuwBdSqMMIl6uQyhVRNVH+iXhGJRkYhQf/7'
        b'GI6ZzY/JosVgGZfh+BTcO9upux7eOsxNdHmj3r7o4eWnmz/q6a3L/ZLLd4p45Mpxin1kz3ESfmXPd4p67MpzEpEm1xJl4fVUeMChoBjuiStgUbaObDBQVp0AX54kmfDf'
        b'w0V4QLMmWP/sSq6UI+VKeYfZlTw2tYQapKT81U7UpD+pjXEyyPhbabPR1q4O2/vzlEiub/xaMFdWI9c0qWTKuEKVTMoE77mSTrmHx/PX7otlqhZtvbpZolXXNkgUMjoJ'
        b'RWEMv3YskmlaNDI6VyVXawbYqnkIeO9niI6/7HWnqMImpaYpqwT1GR2VLVXJ1GrUY0rNxma6QqmRqZSyhkaZUphl9qKul9Wjp0ailFrNp5Ro4DWVQkwvQD3ehPIublIp'
        b'f0g6a4WtkcmVMjpbWS+pkQmzLOKyCrWqlhpZi0xe26DUKuuz5lWIijBS6LeiTCPKl5aoxFnZStRgsqxypB4p4rLXSKRier5KIkVFyRRqrDQpyHeV6nVNKlRyi/EbKk1W'
        b'mUYlgUdlWQua1Jo6SW0DCShkck2LpEGRVYpSkM+hllej3xatWXbjS816jB12R9EGRBBITFdq1ejDCjPk6YQpYxKzCmVKZYuYLmxSobKbm1BpyhYJ+Y7M8D0ZPR9eU2jk'
        b'9fS6JuUkWI1cnVUuU8jqUFyODFk7a3C5UQaQ0BhHz5ch2oEn6jRqXEvcpJNT0/OLhFnzRMUSucI8loEIs/IZOtGYxxlhwqxcyQbzCPQqzCpDPAEhKTOPMMKEWTkS5Rpj'
        b'k6M2wq+WrYYhazANi0q0jagABCqCJ7D/bw1uNab5ETA/J7sEx8lkqjrEeVCwbEl+brloThPqG0Pjk7EgVzYgWsPlGJo9T6Jt1ojwdxALqxEbvmkIW7S7NThue4tKJE6q'
        b'ROLkSiRaq0QiU4nE8Uokmlci0UolEqeqRKIZsolTVCJx6kokTapE0uRKJFmrRBJTiaTxSiSZVyLJSiWSpqpEkhmySVNUImnqSiRPqkTy5EokW6tEMlOJ5PFKJJtXItlK'
        b'JZKnqkSyGbLJU1QieepKpEyqRMrkSqRYq0QKU4mU8UqkmFcixUolUqaqRIoZsilTVCLFohLjAxGNJ5VcVidh+ON8lRYerWtSNSLGXKjFrE5J6oC4sQyZxcaXZhViyIj7'
        b'KdXNKlltQzPi10oER7xYo5JpcAoUXyOTqGpQQ6HXuXKsf8hEjLjL1qqxQGlBOkjWEniiQYXaTa0mH8Bcj5GxCnmjXENHGUSvMKsSNTdOV4MilfU4XS48oVDI65GM0tBy'
        b'JV0uQXLRLEMZ6QMcs4DMIJkXNi7GRZUIC8QwonB2iwhDfhQVPjlD4tQZEq1mSKJzVFoNip6cj8QnT11gstUCU6bOkEIyFEsYuUzaHOklSD8hMI1sg8YUQJzIFEwyT6o2'
        b'JWM6IkeGxHG9GSA8q1KuRL2B+598B0e1IBAWvYhLW7wmWr4i9iNRa5C0U8nrNJhq6iQNCH+USCmVIGSUNYhsTT2uUcET9YiI8pVS+ToxncvID/O3RIu3JIu3ZIu3FIu3'
        b'VIu3NIu3dIu3DMuvx1u+WmKTYIlOgiU+CZYIJaRYUVPoqEWGVlUbFA3huGJkLdKgK1mLMqpPU8WZWJmV+FLrX8N6lzW4hSo2dR2eED+VdvY0iROn/rKFnvZDkiFWaS2Z'
        b'hQhInSQCUieLgFRrIiCVEQGp49w41VwEpFoRAalTiYBUM1afOoUISJ1ajqVNqkTa5EqkWatEGlOJtPFKpJlXIs1KJdKmqkSaGbJpU1QibepKpE+qRPrkSqRbq0Q6U4n0'
        b'8Uqkm1ci3Uol0qeqRLoZsulTVCJ96kpkTKpExuRKZFirRAZTiYzxSmSYVyLDSiUypqpEhhmyGVNUImPqSiAGOclWiLdiLMRbtRbiDeZCvJmaEm9hMMRbsxjipzQZ4s1t'
        b'g/ipjIZ4i/oYUMxVyRql6o2IyzQivq1uUqxDmkRW2bwF2SIirTRqlawOCUEllnlWwYnWwUnWwcnWwSnWwanWwWnWwenWwRlTVCceM/Q1SnituU4jU9OlC0rLDAocFubq'
        b'ZhmyhxllclyYm0GN4tsMNF9WA69hST9Bbahn4AatwfiWaPGWlLXA4FwxyzzJ7ZIwGZQ4GYTMHAU2iiUarJfSZVpUnKRRhsSoRKNVY7WWqQ3dKFFqkXih62UMmSJxaM0N'
        b'IDTLIsfCXS4l2b43sZXyrQgl62VPTkhcTOOtQyPlmzaovKQp63C8oZGZcKJZGNuE456qMVZWyYCtKhe7+ObjRx5lmCJT5eNHAXYj8tTNCrlGVYg9YSzGO4h9aAbPYDHx'
        b'DDI+tE04LsvoGRRiz6CvLu8+n/KKG/WMemDD9XHW5X1hT3n53+fGu81hPa5hUS6CnbKOOW2rH9azkrz8duYy/kHsw/aqh0NqvBRuZywY4FK2qWz4imQz3LHqf9BBWC+0'
        b'G7PPrq1t0qIKKuvHnHMQFTGGjKRZprjnybgHsQf5a7+5iK4akbKCPcI0Y0qhUSFHvAwlwWtRx7hYqVKVo+CX1xCgopHRkZoalDK6rEmhiMtDTE4pKmzBLpvx13G2mbWk'
        b'sJJmsmHXHGbIarlaywBwnPk7M4znY08iYzIwH8qpEJXVNijgNUROCqTmmL9m5cgUsnoprggTNPhxxsOJBpMry9gSxITAOqbMwC2MdiDN6FkGa3Lc72WwI4n2jy1IlBiN'
        b'Vw2xNAwlkM8p5CgBCcmVdU20iM5WaYyoGCD5SpxzAhAnS7SWLHFSsiRryZImJUu2lix5UrIUa8lSJiVLtZYsdVKyNGvJ0iYlS7eWDKktpWXlCQhQyHQMVp9lBJg4CYhe'
        b'6GIZYsFG5y6tFdPjzl0EZGjZ6G0V09gEMBryjBd3vBvpopiirFytcg3ZJSFT1SOe14L5FIbnVNDJGYzkrjMmwV5ma3AD3TBRVgrMqiQWBq64qlGCI00kYi3GRCpTZUt8'
        b'UjbrkQwJPSGb9UiGpJ6QzXokQ2JPyGY9kiG5J2SzHsmQ4BOyWY9kSPIJ2axH4mwZT8pmPZJ0d/wT+9t6LMn4ZEKZmlISnkgqU8SSjE8kliliScYnkssUsSTjEwlmiliS'
        b'8YkkM0UsyfhEopkilmR8ItlMEUsyPpFwpoglI/6JlINiyzTwWu0aJLrWI+GrIbrueplcLcvKRSJ+nPshdihRKiTYXaleLWlQoVLrZSiFUob1rHH/pUFyYoaXra3DnjYT'
        b'kzPKUhSFOe+4QKajspUtjI6NpwgRMy6Wa5BolEmRBiLRTIiewIcnZx7n5BPjVAr4htqgJljE5JEJozoN0kpMlhqRJCKi71g1Kww1NUhzJPqRpMFaeR3RxxuxgNfI5KhZ'
        b'NCbXcz5SnjXyOvkaiTn3rySWpcklba5mMPao2dSkuZqUK2OMFZm8BkcVoV7Dc21qRrOZWlEzdzcjvNGXJQpt4xpZg9E3ToQg0eLwQpsS1VLrWjFeWNtipjhew/HpRs04'
        b'1EwzThv1pC01Yx+36Y8Tx/XiNP9xtZistT6bAN9SF5XAPXFIOXZ3wBs8Cm0ozxquo7TcQjV2NKrGfDZSjQWWqjFRhvnonwP+J2Wjpwf+h9Xls7wzNkxWO/SflNbxdE46'
        b'D7JO3s64FKaSi7dhSm23U1K7s/ZnDAvaKvkE6oCgjmZQGwJ1QlBnM6gtgbogqKsZ1I5A3RDU3QxqT6AeCCowgzoQqCeCeplBHTG+dWyp93bbSieLenp8zz+7sz5n7M1q'
        b'HqxjG+rOlfqa1d3ZsvXQP3v0j1VnbEUbU8iydL8zdsbSpSE6ZpEf3sbnir5gI/U3+4KLNBTF83S2ZKOfO4kP2G5X6YpgbqhugahubiYsPM4GGc0Ww1ZBZ51LHU86bbut'
        b'qUT3jXy7BmHYmO1cvLdmTtnir+PsabM/I5hmeCGzt9UixQBPtQATN7a07uH1MKpVOISX2BKbRuh4DyNxD/fDPbzAczy5qt6YXIVXT6qqcRLc0vfwXrp7mFKFNmP2Euk6'
        b'xF5VVXLpmF0tYnJKDQ46S5hxVKVAWqqmYcy2VovGv7J245gtXsYulygMC14c6uRIMa1qRLynoaTW1mwo4E+RhVmbKeMaS/MNt2T/Hgt1NldngxqP2b3Hr7Mna8YQme60'
        b'N60ZsyNrxmzN1ozZma0Os91sZ1gzNgFqvmbsyy7UOBYti//ymarIW2Rqsi3Z1B9ysg6kViaelGUSIBPZVpJGerwZMw0bkhH/xN4zw45nQ3tKlJpJJeC/qBzE9jRGpisU'
        b'09k4P2KQtTRZN0trm2kkJtJoqbxerlFPxsuAhqkHrWPBRFvHwDRH9D04pHwfDpakk0kXkV+Mwvy4ImOsATG1dVywUMXiDAlDMV3egAQcGiEyWq2tUcik9ag+P6gUZgEO'
        b'Y4mjkmgJKgK9M/jTiiYkbFViOl9DN2qRPVYjs1qKxFD5GplmvQzPkdNRUlmdRKvQCMl+9PSp+8IwZDLpOYYQXYudrFGmqVkz56xwqlKMwy3TSK1qU2fi7e9NKjqKWeiz'
        b'Bl5TtcgUUxZkWKiWSUxJrHahYhgaMXCfKFm9mE5JiI+l0xLipyzGbLxn0rn4hSYvuLg6uRKNGoQjvVEmQYhFK2Xr8TzxulRxsjghWji5qb5nSbQjs9PqA1/XzFOs2RTV'
        b'XO14kXKgtHg9XR48nAPbisHZBVCXD3cXxsGdC/Aq6bwiIWyLLRGBXXBv0cI8cC6vpLg4H1yNL2ZRsBP0OTb5gZOk2HnrnMLaOfEUtaA6tsw+gNJOR8AAsI9rtVi4B+4s'
        b'QuIf7DQrd4EsHxe7faMj5QSPkVJ/F2+Xc4NF43W4iv7MVEqLV8zCt1ztzDfg5olF0QWodPDqJniYS6Wu4KvnpZENxKSMoEQ+fZzlg/dxF320KpDS4g0HXuDF5MmYwQ54'
        b'ubQM/bajWmMM24WLjZVGqIErKgdwIRO+JM/LvMZT96Fy2vXqTXsTnEG847zGUwNd5c2B4ndmXJUGf7yFtfgnv+fQzvrCfXlD9k6nX4n6+p9fPfcg5lr2tfu2lduWHYtm'
        b'33u4dtvDx8X/0I24Pf7T3ekrzn2Vu+gfW3MyfposvHmiJ+KVM4uKvhi+eXbWH9f2RnM/EXyriXm/pNVz4LW8r3Z45+gOrzs0d5XbY/+5t/72p5iafPVned0fXfjrwIZP'
        b'5jud/vzu0Wl3fxub8ZyP0JHs3wH7wPVG0MZs4RdGMhvYXMI5dW7Oj/DyStgOtiXCbf6grdS8x1mUH3ye26KFx5iduTqwa5UDanVhsVYUnQmvkCXonqCVawu3lDEFHZgZ'
        b'jgoZ71/QD3pJSV7BXIeFoIssUodXUMfvixFF5YngllI2xQcH2SK/iEc0juuD59JQEcZO7QRvgle5lDt4lQPb0uFLpD7wLNwFtsSIhXBXLOwBZ/EWu7PsJLAFniWbPZ7z'
        b'dwZtcO94P6LqXBfyKfd1HPDWkvmPInEZ+5VSXF+DJopJ0UAJFBUPX+CXx4qhDlx/hEVzJdiFV8Sj0qLFOCHcDffG4ISwNYVW85xgF7xGmqieD7fghMTti7/8fJgIfRZ0'
        b'c+ALs1Ywq/C3ItS2cjhm3zbowH5giAvashG/+BHbXbGKMHGrK9k052aUxJa7/vQUsz55nQ0VjHf6OY2Gijq4N13p2x5eneqezK7nRjwi+4NveMTc8QsbDs8b8csfFuSP'
        b'hsSgtC5MmoyuzSMeEf1uN/A+FpRm/ohf3rAgbzRYeCroWNBIcAJK6oySdmjw9iqc1FRc2ohf+rAgfTQk+mVxf82t4DR9cNpIcMakDKayc0f85g8L5t+NTMFIho2GxeHf'
        b'4NHgUJxnNDS8g/uRxX4ZJ2ZBdBN+NOPHWvzAJx6o1PiBu1WloZ60Zhr72asNf2ZLp6do1Xs4C+Z636FmfVxqw2LVsr6k8PNp9xH38eORVp7FsdgawDIy9ADC0J+lVlOT'
        b'/8oopKCxSoSsMYeqcS0KGXi4LYiBRxu2hE5XSBprpJKZZhUxgtxYRnKiespvBYpuBDKrnr82iDhDwUZ1KAqJTqmoSanYKBxgjXGkTbU/Cu/tDN72VSa1azLaqh2WTW/E'
        b'WICSkK1yGOOjVQerGHynMfgyBVpB91/B06XKUjX74ch6WzZvwo3ABAZd4ROVu38ZcQNh2FUZdakfjrKfRfuuOriKQdg3R6KWmVSzf1fL2lUZ1bQfjmAgSqLqwgkIYqFT'
        b'qnf/Ior1DIq2VQYF8IdjSONeNzXhyoMrDZhOqUD+e3rbscpMx/zh2IbiDh+nUfGNQLGBRr9HS50Ca9PGomr02M827Gsy7qf+9+5qmnTCj9VdTbp7Dyl1NALUv91+6INk'
        b'vHtPs8iw/RTvaVrgWTRUUc5aG8+pz6SS7/B/8t4NIZtRUJ6HW+EOcyGPJfwqcJ4I+fJZRMiLMpvBCXh1Khm/FpyccnezTRVmKVVVLa5mIoZAiNzGGjDeIFdgR/n49yQf'
        b'ndk7c8Q7eqBsUHArIVufkD0iytF75wy75kzaxmxN0DG7mLFwY+jhOKaHSR+OYI1vDPoy3+7pNgYRxtHJD6aOOcRyhPZjNgbGxuz+4as1KplMM2bb3KTWYJNujFsr12wc'
        b's2HSbBzjr5MQL4pDLTIsmxoZ7wpHI6kf4zWhoa2qdTDramdjV7djOuNaP5gM0Z6TYX+qrc5Fx9bZY1rUueo4OjudTZ0zoUkHRJPOJpp0JDTpYEaTjmbU57DZ0UCTE6AW'
        b'XpOPeVa8JtlSqRqZxdi2k8pqMItC/9caFsvSMrIs4Qc4TohZT2xyCd2grZeZuSpQu6rlyNSnmd1U2OuglmnEdCkapJPKwbyyEU+oyhubm1TYw2LMVitRIrMdZ0Umv0pW'
        b'q1FspGs24gyTCpGsk8gVEvxJYuXipdZqMa6pHLvGEaswFGnwFOAyJ5WBitaq5cp6gpGpGDqadHn0D2iRXENtG7ArcDLuk9JHaSSqevQNqZEN4/w0dvarsdWtXqvFrVuj'
        b'ktSukWnUwswf7sxiqD2TzraQ5/Rysrxh5VTZ8JczabLdafn3bnqashRmcGXSZeSXXm5YgjtleuMgzKTxVAXqKuJkWW6+BHfKvHjYZtJz0JNeXqrSTJ2OGdgoKRMg34il'
        b'88tKRUkJqan0cjw9MWVuhhtk0ouzy0X5c+nlhjn/lTHLzbd0Tf3xcSaCXUnMC40LMt9IMGV2xHZQYzagoYGGq7pWJW/WGIQ3plN8oAkZW9kKdROiX5nUqhcMkRNOjUWn'
        b'ghyuSDpbTM9lXGFkiIaUaSSNjXiHsTJkSqcYGQyIsBACzYahJZWT4x0lqFnXy5GIlm1APW4YcJPLwX8lTRoZM0zI4JdpGpqkiJPUaxsRoSFcJGvQAESDRoZap1ZGNyHN'
        b'x2o5TJXwoCE+PjVTTbnaDCUxnYuYmpEhWS3FfNhhjyAidXx4Za0CVZg5t1Its56z2nB0ZVMtwZyZDZ3eoNE0qzPj4tavX88cyiWWyuKkSoVsQ1NjHGMYxEmam+PkqPM3'
        b'iBs0jYrQOGMRcQnx8UmJiQlxcxPS4xOSk+OT05OSE+JT0pIyZlZXPbX/zb1Ei9WHfHAN7lQXCQtE4nCoK8H7lGPAQCxFhZXxGuCZaC0Wy+AEOKJNopYkUlQClZA6gziy'
        b'nJbzKPQb1TWnuqjCbTqlxRNyfl5ge6FRx1gIdfjktYLGAtEifFrBoii8138J1OEfpHyAfeA1O7gfHgJbmKMkj8FzsBdehHuIOwNe8LOheLCX7SjJJJ42sO9ZuCMC7IAX'
        b'xXB3YT4+FgGVj892Y1PTwCtceBUeDyIORPuyWnixELYXV8COZlI5V/iWqXILUEVRvvbCimb0KC0qgPu5FNwFtjnAE/DkHLKdFpwNEDqIhQXgGjgKL/naU3YFbHjUro5E'
        b'zueWwIv5KK8cvsyiOKCbBbaAU/CkFu/gR2pWvxc8a+MAdXFiuBN9MxYMFMB2qGNR9HweF2yhyUl/2dPKQFcjvBgXzaLYeaxUJ6ZZ56NKO1LU7K7wasWJ3FRm8Z4b7AVv'
        b'q51QW13Cn2VRtivYXoL5QcuZL54AJ9eB121wAicnMeyEl4rg+Ri4j0N5b+SAs+DtDNLX4MVceN1BjEpAbZaPW4NDecIrqNGvcV2WwSPyz4tTWOorKOXq+UGNw4XO2+Jd'
        b'qeHeA+w/lt35bNmKlhfzi5pbxTdn17QfytjywHXFDQk91F88dr3kuZHr0MZxUPJrmcNa31/ecRnmfLL4UbM04h8/vZDUVXk+cO2ytx+pDu4sDX2m+ysN9Rfw03P67X+f'
        b'8c3fN4Usv/JucVpzdEHFlSMVUWUfvbzij3NXVejsK0KiK4ovf7Jjy+mPX9w04+f9IcNrh9cO/f42vSCp79PDP8u4PHPPlxtWPHdS9N2HrzVlD219bhPrH49j5t1XC/nE'
        b'IVfD5YG2OHAAnDCdEso4GDnPPMKHJsIh7bxCK662cvASRcUk8eBesMXoZbwghKdMXkaji1EO+ri2HHiSUcGvwsvgjIUKLssyutnCYSs5QyAhLTCmRJSfX1wYC3cLWZQX'
        b'vLZhGTfRroY5YeAIeHVlYWxUHsIDUf4Q6mFwhr1xfY3Q9V85HNCqaw4/LA6iM50gYC+RSqsYLa/Fw6R1jwOJxv8Xg8ZfZE/50X28Ps2pTcc2jfimdPBHPXx74vQe0cMe'
        b'iaPihI7cnll6QQzjm0vrenbEI6xPcysyUx+ZObRQHznzhsdM4kqb8069Prx4xK9kWFAyGiLs4Hes73QZFSajwGa9a8TozJwO/rB3pt41azQsGgE36rGfLQqF1nU6jwoT'
        b'jOnoMBTSdjrd9vAdjRL3qwZZ/fiwwQy9IHxUlDSYPZjTX4neZ+oF0aNevje8hD0rOjijroJu507nW65CvauwP7RfNeKaeMs1Q++aMRTxkWu2mdHixhgtr1DGJb0n8eMU'
        b'fvTjxwB+nMYPrHSrzuLHuSnMHLPOwO1ePf5Hjx9LorqMjR9r3SDE9k8Oiv3uv7Brzw479R4T196Dp3bw4Rn0U/w06rJDNpsjtBtzlOLFzwYtccyJ0f2Nr3xJI/nFZ6XJ'
        b'xuwM61NqZWMOWFND+jFevco0gqn+tfZmYsjVKIb2YIPIxppB1E2OekXGD54+ZpEDee10bsg4wgf2kpOZ61yJSWRvYRI5EJPI3swkcjAzfuw3OxhMoglQczP9y702TzaJ'
        b'JKYFKDRzUOMPUPzn4W1kTGoaaR+oE5FOjzQqifnZ1ljriqXrVU3aZhSLjA3JZGne1FgjV0qM+l00Uv2iiWLC6CXYqWRaN48RNHlCJpWEPSP/z4b7/7MNZz5EM3FHMRCT'
        b'i/Z7bDmLMc3kZ0DGAqwqtMu/Z+X7lJ9jeAbzHQObMMAYm0DZhB14KqL1K63r8uubsNItb5QoprAalj9h7T+yxayv/p8SY8zdGHxrmprWYHwxREwXG6hLQt7ppprVqOPp'
        b'JusGCCIQZEOmp8YnGHyomBCQAYyLWz6+L2BKJEzMNZOuUGslCgUZGYhw1jXJa02jcbnZtoInmtEG5mzZDWQL83LzrQffa+ji7BOMXYsF7v8X2Ko5svWyesPyxP9nr/5f'
        b'YK8mpcYnpqfHJyUlJ6UkpaamJFi1V/Hfk41Y/iQjlmYWkfS6c7Epmn6xqNpRWbCcQrYqUtyPrwNvFOYX4zn5nUvzTUapNUv0OfCWXXKLG7FCN8NLHJMNSgxQuJ3DdkQ/'
        b'L2jxOU3pfrxCcUExUvRRmeDCoicUC9pgmx0yDC+Ha7NRzvCNYKu6tLjUcJ4fLn8J7ECp90IdskXtkfWmBFcRngh0pWwFOAwOguN2FDgDDziUwINgL7lOAb6BrJMj6gK4'
        b'O7+4tDC2DJ8FGM+lfHI4sH0xvEoufhDA8/A1dXQxuACuwj1R2LgR54NzUSxqWj2PV45SEbulFfbWOyDbZc8iW9iaDHeLSpCpyqbckzjgWBk8T4xuO7h3EWqO8eUtNuiD'
        b'sfng0iJ8wHwCaONt8NmgJZbSFdAax+AFXgkuzY8V4rPqBfA4B76ZoCQdJVtFbqnwiXeudoyqdKXIUfhwCFwCLzrw8TFP5VQ5OATPahMRPNLW1gE3E2rMTng5r6gAbHNF'
        b'TdcFL2HrvQ2cQZ8qgnvysBm7wtd2vkilxXrzbHgxEF6kvFooKp/KLwV7CLQKtoLdSVQ2n7gwQM9S8ukyeDwRdnECIdK18SH8F2Cn4j+/++67B2GEoGibedWxTpUxzMod'
        b'7Qw+tszzNgRXK2DmAor0abN4Dm6Y3QZ/R17sYnzVRlxBRRQ8Cl6FO/Nge1mUEBFFnumCDSF4g7QdX+m0ckYise9Bqzd4qQzuTyrggDZwkWLBsxQ8uxKe1OL9f2UBEgdD'
        b'5yzC9AIOVzAkY2vRPEzboI/u46ICK+yWNcBd2jjcwG/BU+DUuPsAnIMXF0bB/WW2ls6CWZ5850Wgh/EpvLQSnFMXiEqLV8GDcZiASgweAyHs4YHX18GXyNUh8Hl42SuG'
        b'OXZMCF5bxqccwNtseHFFKrkvYn1kKfsnfGrDYIvW4z98pPM4zHqnhXALfBteJN4heGa9aBGzDAufdr0zrrR4YZShQPPlTshEPuUIO8D5Ji05xBruAa0x4vzYaBbFB3vB'
        b'CQE7rgUNEU9iTcMThYUI6Sp4kkWxVax0uDtJyCH5wCvgGOw0yziYyI6bmUCuOYF94HgOzofG54tMRrDVhtTTEx6Ah4z1FKcaqwm7EBPk/I6jXo9sspzdBa8smlEK410v'
        b'HSmNbDx4UhguiMj9Nufn3zrmOpyYW5MXyt1/kT5QOz/2v5//Nv9XJQFjmUVzC569vv7x5//MOHrPW8Kd3gOuhX2lrv547PRpu+u+c23Gar/ZdeTDzwWavb9bXZh3JPm3'
        b'HTLXv3/zu9+m2XeGgdvV04tsv0t594X7ihydx/QU1qL2ZwN/GW+fGni5SR3q99XBmrsdvtM+c02ya4bfvrv1H18cv7fiaPU7v36x+dPdj27O/omn6jfXe6qVp1WlL+UV'
        b'nV3GHln2RefIrx3HMr5d1FnwddFnWX/sOyGbvujIwdUJcXsOe/b+8Xc5N8o++uXN6vf+0RawrfbO2f5nB0oP3Ar6dOjN4axVEW8cPCCZeenhBu/eIx/N3Ljvk03zr65/'
        b'kLO+3f28X333396VB96jlyuP/2VkXUDnHtVJ7aW2V4emPxjo/3zhvDtn+UdfLfn8I8+/goYv33zr+sjywKo1RRlvff6V3/LfH/3ptJ1D/1xXueTqcwOLLuWWLmsvd4wW'
        b'bgz/729syrSqfat9hU7MqemvR8Fe46Iy4vGBp9MYpw/oeITPUgWX4augjfH7gJOIz0xYZsU4fq6IGL/Py8+AIcbvMx0Mmrl+uLbgOONlQp/pgTsKTev9uFQz5bKYowAv'
        b'B5HDHVuyZ8REk0VhiI1mU8vY4BVeNFlx5gf6wSsxYiwoYjEV7vFMYosWZz7CN4yAAwvLCouiQTs8yafYK1lp4FIgKc5lM9gCzhQVx7JXJlHcQha4wIX95IhJb/jKckSy'
        b'xlVg/Gfh/jXsyAou8XVtBgeQ7MCrxcB2eG3iijGyXGwnfP0RGfR7FwWNzxFToM9ymhix6a2Mw+sy2A5eZvmr8egUYaFHHGxusIMDBkvgNYIUuN68yODRYlG2zyIuf4a9'
        b'EV7LEHr+uz1aU7u6cLMRPWLLFmv+LmfsUxm36lu8LZwt4xHE7zWDzfi9NjtQfmF98/qT8dn0I74ZHXzGxTV9xDtqxEPYP/dW7Cx97Kx3gvWxc254zCE+rux3ivThC0b8'
        b'Fg4LFo6GiBkfF5Ntxoi3cMQjur/8lmi2XjT7nQS9aO4Nj7kkW847K/Xhi0b8yoYFZaPT87EfLF3vmjEahZ1em/Su4WZussgY7IdDb8/qXcNuewT2SPvm3PSIuu0f1S8Y'
        b'8Rd3zL3t7c+sdbsSOiR9U6gPN1yIgXIacmH/Xfa+zNG0zI7cYf+kG4Lku4agXpB8O5Du8zq0/FZgnD4wbpAzEpjcYT/q4dUTrfcIG/Dor7wlmqEXzRiqHRHlvJOoF+WO'
        b'COe/F3xDWEi+WfReiz582Yhf5bCg8k561pX57+S+t/jd0pHp5SPpFbhayXrXFOy4S8nC30vQCxLvBoef8j3m2+E86uHdndmZ2ce9RSfo6YQbHgmj4UmDEn14WkfJqLff'
        b'DW/xcJB4kHvZ7rzd0Mxhr4IODkYr7JZftB797xE9GhRyK0isDxL3q/VBSR3zb3v79aT1Zej9RSPe4sHwG95pd4Iih6OKRoKKh32K73r799T31aPkqODRmLgemz6bGz5R'
        b'o76BfTb9vGPON3zFo0IRgvIOOt+Nih0sf6dGH5TfMX80Nqlj7i1BmF4Q1lemFwhHXb177PSuIQbPYsRHrglmzkQPxpk4hB/Y3666ih9v4gfe26R6izI6E3+gH3Ei4eNP'
        b'TfQqmhyLv8K8aSparzQ5F/EZwmvtWSw5cS7KWQ/J82mdi/38dGrIIZvDqTWeLYD/THc+IS3NwhHYTelsdHY6Lrn1ia1zJJeKOOlYhrufeGxqp2m3yCY+cfrxzJx+fDP3'
        b'Hm8z3+D0mwCd+sThyRaGM2NhcJPZswdYOFTt2FXrSZUT6LNLuPT7FHNNyPqVQopRIp6Hp5aqwW7btRx4uJHiOCPto382M4F1ciHYVQZ2l8PdFcUL4aUF8FKFU2p8PEUF'
        b'enNs4RWw1QkeIEZINbwGu5FqX54SD3clI/Xedi0roAj2+UAdiUfa7E6kMTJFwbdckX7Ei2Yhe+EYl0wuhRXCa/iiJ2o6BbaKpoOtLcwNUD0JsA8eh68gXgbfhJciKJ/0'
        b'Ama+a2gx2FIojk9ObATtKWyKv5kFXoKnlpGvRYPnQZvpjiQKts9lrkiCe+rkjcuXcNSRiGi++sWO3WWFJUj7ObLWPW0We56uNIbrvuQT/sqL/m7v58VeyNm/iSpUXJ0d'
        b'EPL7PUXB5wrqFrm9f+Fh3W8P/fn8Nws35XwYuO0/v5Y4V9OLz0dc++Tt9Htv//WXcb8V/WEgaZ93x4Pyd516O66Jp/8l9mdar+0/OTSaHnM87uxNWZBwWffy3V5RH9N/'
        b'/lNi9wOJy6vT/c7tzfUXfRAYffu7FT+L+mvrbz//k9ONhsHfqS/V/UF88nTnl/2PP7199u+SlF9dvVn+7Bc7PvZUll7+1GPk2q9PPJ519vdvn03/7sHaGfcgvUA1mCtb'
        b'GTr4s5wRn/Xl/lWpJ0TbP6z/fPHq+5tLns1ct6evvuzzz8Ouvh36ODFif+03tqWHg/524nhSU/g/NvWyPSs3vf32ms+zH6xYdOmZN2OixprSV0rj/7BY6E40ALAPKes7'
        b'yYVpNlTGUjYSpxXVYCeJa4HbQhhBD7bC1xlR7wKuGHWO55cysj4VnjaIe3YkuAK7yNLwBaCr3LA0PAe+NFnWg33gLebiq51rkVVgri5hXQns86rbqCZfmgN3SQtLYpHZ'
        b'sjcOnOZSzuA6Z2V4FdKe28ntGdmwVwDb8CQrD2zxprhBLPDyylAGybcU8PkYs5Jt4XZ8Pw0iGvJt8LozOBMjFlrcp5UBX2gCx4UkQWF1WKHlyn8v8PZz4BzX38GJaCDg'
        b'sB8cLDSs62clMjs3WJT7ajzd2QvOk7YAF3z9GG0vUGhd1zvky6iOex1QtdrM9lnwKZcgjhJ2rpqZS2oUqIGHzRU9pOY1gzMKeAmeIvN34TVwD6PsIB3tWqFh+g4cZS5y'
        b'SM6Fh5nbv2A7Jx28ylz/tUnK3PLwdpKb4Yj8JPia8XDxmV7kbPFqpLXtJxbJnlLwtju+cAd0sJuE8JDQ/f+g3uRu1JsmX1g1ZlPFXFZlvi6PgRA16TCjJt1f6kR5T+tW'
        b'dCq6lB0crI/U90l6V/dH3/RIGfWnj2b2ZnbMHQ0IPlrYW9gxb9QvqHPOXf+go+m96Rg87Wh+bz4Bd8wZ9fDpSb7lH6v3j73hETvqP60vGCe6z6b93EcFfvc56PeuwKe7'
        b'uLP4Pg+F7/Mpz4Ce7M6CW4JIvSDyvg2G2Rpg3aWdpfftMMTelCpCL4i474BgDxwpT58ezlHHXsfh8NQRn7QRQfp9J5zYmfL0ve+CQ6445IZD7jjkgUMCHPLEIS8UIp/w'
        b'xm8++K2ks+S+Ly7cDxdu3yfFCuIMfeyM4fCZep+ZI4JZ9/1x4gCU2IBxIH4PQslvCDJ65/TxyLVmG0bo9JGAjPvTcCRNItNQJOeU4zHH/qUjdOpIQNr9YBwZgiLvh+JQ'
        b'GEYAt0s4fotA8H35Pdn3I/FblPFNiN+ijW8x+C2WFC/smXu0uLf4vgiDxLiOcTgUj0MJOJSIQ0k4lIxDKTiUikNpOJSOQxk4lIlDWTg0HYdm4NBMFHowC4U6+PdzWJSv'
        b'fwfvrqtnt2OnY+/K/tSRwMSbrkkGQE/Z0aW9S/vq+yXHVt+KSNNHpI0Ept90zfhDUHhH7qjAt7uos+iYR9/i4/4fCUT3OdS0iLvegd3PdD7Tl4J061ve8Xrv+EGfoYwR'
        b'73nDrvPMtDBnRgs7S6iamaNTj/HUGolKM8ZBFP10KpezUeWaoG39gbJcw8qMlXMswx1v3+CbGpxYrFh8x1vs0y5kfYkvpl51yOD8ry1vrheyv/7jJLcts9dfY9x7a5j+'
        b'Uhi80iqZRqtSkrhGWoJnV82c3D9oZpJeI9uoRuU0q2RqvJmC8Z4bpgPUpilRgyvd2ozixNlSBTMHgdGp2aiRWfH2WyiKtlYURXIpFtwBr2A3BDwA9iIV7TzcBy4sARfA'
        b'eXBmIdDxKB+gAxfBFs4zNXZEUQPn5qXBLqQaB3HElBgJiR7i5A1Bwmk7USJB2xIRPFCYJxOLOZQA7OSAAbtkon2GNLIpbsBpFtZJLye6MyuFgsCL8AVDRrgnw4bigldY'
        b'oNu5coxVxdwT8BY4DF8n/q9NoJ+4wNhx08DrxMslAOc3Y6VyBtiPVVSDUgmvgmvEXZoMXmwoJPY8O4eDvWqvJzEq7wuC4jKSAZ5VUWywmxXgA6+SqCLUAKdhVyHCPg3u'
        b'oDjZrGei4Kvyad8EstXn8cBTXdjfMcOeneCaWx/x3Juf213bsbSyhbOc15l9OyA7wmapa9Z516w3V9zgvuy1LHvkQ9ffhv3jkMPKY63U8w8XTHvtszeXfuaemrQlhcV1'
        b'TF7atPpAZ378gSXbasI/a1B3f6tOiYsSDDyiV3d+Jn/14sqHlz9+Y/Re9dyLL9VxpA/b7jnd3iXprn82LSfNrUr6+7HX7nwK166/nL1wya9+VfPzff84b5PgMv0PWf8s'
        b'OSU62zdjOmvvC9Euc88L+YwC0hEIh0D/+okL78maH9Bla7g3BClw2w23f8COED7Fx5d/6LzIHWNgMAsMxIiL2RR7/TrUFYXrRCTXysBVSC/DmsZs2J0vYlMOMjbsA12O'
        b'jI9mCzwz3XIh/1teZk4aBRgimkNxPjxnoWLxbPGlpfDwaqHtD9YDbE16gEn6S9RVeLSacTQDhEj/uxQj/Re5EJaOZHG48FTJsZJbYen6sPTfhGV2FnXM6fEenRZ8dF3v'
        b'uuGI1CHOUNnItOyOvNFpsf0b9NPSUCgi+pTimGIwachmJGJ2x7yeqH2l922o8Kz7jqi0W2HJ+rDkW2GZ+rDM34RNN5TnF9gj6Y1AOoSP31F+L394Wtygx2DtRz6Zoz7T'
        b'+mz0PlG3fBL0PgmDUTd9sjCI1+t8yydO7xM3yP/IJ+2+DZf26shDOkFkUp+U+bg+ImcoEj0M33ehwmcgke8T2OH4o3YyfGEpBQxt9qn5ToZ5Lk95xckJlHGANcZtlmga'
        b'LO7AMpmxeDfOfp7hDix8kAW+URnfHMg33YNlso3/5Xuw6oTsTzgsK0toxqUBZsxqyTocUijM5cIPP40BVzaTzq+jo3EomkbSVM1M1mKOL9uAT7TBc5fR4hZ5c3Qs+ZBB'
        b'9KisT32q8UHgUtOEq0RV2yBfJxPTpXh+eL1cLTOJF1IGqQBJLqHrmhRIln+PrJh8obRtiRbv9QEHwPaZMXmIdSzIQzZHQXERGCjPA+eqwQGoixUjUyAP7rBpXg7f0OL7'
        b'ZmLn2xQiRlNQLIY7kUVWDnX4tu08eBZeQOwlCp/qWAjfsAEHnoMvEm6+Dl4HbyFrA3aBM8QJzVGwwDbwOjivdUHRUmpVDMJtwyxXagM8OIOw64VQB87HlLIp1iL4NjxB'
        b'wYNIoO2Wp/b8gqX+M2bnim27F563B/GubxXeWC3oDAmZd+S/2TbPzdas89L8gvY915dzdYi34qd7/1LaMvoz+4TViZ9uePz5xx//Yr1cdP35xtX39/5pZp1sq+z1pmkh'
        b'rdGav/A4lbtfqww9ve+59bVNH1de/fstz48OdW37fPvDq3/9s+C5L1ckDp7fXzDa33/tPf2WErDLYdSZSm3vif0zX/vrP/vVbXj3A59PDtrTq2ad3dns/M3wOz9f/esL'
        b'20/faHLcfvQ/Pvxr43u7c6v3fHJKvOOKqOLTl30/BbYzvvrnjltlA3/e9LAh+L3n7YqCYeicpR65f/nsJ7ea5155hsr4Y0Z3b7XQhZi4jXAgxQHxWNxFSK1KY4FXU+Ah'
        b'5tKnXfAcvvcyNnFZieFSe1vYxt5U58VYlDvAxVR4Eb6+XoQsbWbuwA6cYoPj4FUhKXtV6Cps36IOZVP8EjbYvzgADoiJsTkL7IFnUKE7Y8XpS/NJCgc4yIbXCp8j8alg'
        b'b3RhLNhTCl/axNwY5zCbDXvgQdBDivZzA2/h7HGlIuzIYTdmR8NDKUS25LYsxwJcKIZ7SZ1c4sPBSU79rOnMRvi9cLB4/LKqVWyb3NBgJE9wjeAh2ANejolDhJQvEgvZ'
        b'yGY/Cl5dyAEvgMuJzFVsl8HuLGKTx5XwKP50Njgl9oanwWnmTtohsE1VCM7NQOoHQ9x2AjY4xgVbGJfBfngAdmDHhqFJctigvdgHPA+vk+xF8Bi86FhusqIZExpeA4PE'
        b'iM4uhRcZ3NCXQT8bdq2KhR3gktDhx5rADpTF1AEj/bh47Lc4mdg4fiVyj89i5F6BKyXw6k7rTOue2TmzL+ymR+Qdv+DhEOP+cg9PEjejc0af4KZHRH/ia5kDmYPSmzFZ'
        b'Fsl8ArANesi5g2dwfndNv+URpfeI6ve66RF/2y+4L6yf079ixC8TmccRMfgir5ONvfY93B7pqI8/zttX3p/8kU88soYik+8KvLvzO/P3F971Dzya1puG9+j1h930jxtF'
        b'wtK217ZPcNh5Qim3A4P7Qk5FHos8FXsstl8zWD4Skjk092Zg9juLRgOCjub15vWVHy55zKGCcljDgdkP8Gd+F5iNgl+r8elDP0l3n+fJ+6knb16QHSMp7RhJ+WgKcTmx'
        b'9bHn2GRJMRLUhoWvu7No+u+MRhR2VT+DxKcPXgD71DeaHuBHUCcdEjhC5kSmMc68ikUl5NIplRzjblti+BPymB82+ucx4ZxfvFFS2lRbVUU25I/ZNquammUqzcYfsuUf'
        b'b3Mky32Ja55YjERhIHUWCv5Hpsrw1OPEWbLxxscX7rWYzrrCCKobWeT8tQdctpPrF7aUs+cxzoD6nSz9shW3g4L7M4ZzVj3isJyrWXfn5Y4uXPQVJ9Qp4iEPA+5zUfBB'
        b'AYvyC7ntKhoVpD7isf3SdQUP+JRv8G3X2FFBCoL4punyESQo4rZrwqhgFoIEZbN0JfjCOfq2a8yoIA6BfBJ0eeOQDAzJIhDvabddoxmId5ZuPoL4h952FTMF+aOCCr+0'
        b'ZTnNYX3BR4j3lh1Tn0961+P9pNuB9IDHldB3k96XYuTLWXcXVowuXfGYI3LKYWHsyxH2OPzFKhaucej5snfD37d5Z9pt/6BeTU/0eQ4qpUy/eJleIsMF1LOQBlyFl2dz'
        b'SllOiV9Q+InLQRFcHH5cw05xymU9pPDzSyXL1ynwi1SMUuhNp6DHbC+nmIccynnaAxwaP8tZjFhbqzofMWK1szOHcgLnlwey4bEAlpbcfnwVXIQ9DqBfgwVTBmh1wEtP'
        b'FuAlJwGJ3FDYGf2/eL30pMtSJ2+HtikhljHsW5NWBg9guRRMBYM20E7Wb0SBV8DRQjEYjIRt8SkoP3yDtbbGh1lGc7wKXDPOU+TG8yhmmqJWpcVO5WXwPGyFbfmx2CJK'
        b'4qJm22sL2tgF8DgYkC9ld7DVePTbvn//ELmeOqGtk8U5u+PGynZh+7IPe76YvfLskPZc3fZ7/NO1x/7w8/Ju8CK4dtAu3ynSKyU272S84Py6xJPxmsS8rR/ZJDWfZFGN'
        b'q9wcaj4X8hjhuBPJZGyQVSIDHeti5IQYPthNpNv6GNg/LtrgHjsi3UAr7GfsyINOpWS1wAWw3bhigC0qBmeZot8KVRlcxEj6wXNK4iJeDvaR2HrYC3rxMjgm9gi8YruS'
        b'LQsCb0y549uxWSVDurasCi8IbbF4I7JuMcXIutlulMCHkU66uXc9vLrTO9N75h4t6C04VDRCzitHwiurM6tnfb/diEfi+PuGEY8o3dzbLp6j3v4983sWd2zq4KI4XaG5'
        b'ZTXGxR8c4zPnWXzPbdceWDZYYBrMNrvn+jlXFsvvaS+PtKBSV8Pvw9/iwx8dzA5/jMN7t8lQscPHQMq4UvZ2Sso5yzUdoMgjUB6C8s2gfAK1QVBbM6gNgdohqL0Z1JZA'
        b'mWMguRZHO3INx0COQ+0RPjYIH5fttpUO0ngdq44ldUW4ORrgbvgYR2kCgXsguDMO6/g6O519HVcqQBAXaSKCcFFaT3xEouE4RnwEI6eOg55c9I9n/Cd1J4cz2hvCnAlh'
        b'Y7zxl2tMP+F3Ipy8S70Ou8gpqTfO38WS+uB49Otr/g307mfMh8L+ZuEAs3CgNAg9p5lBaLNwsFk4xCwcahYOMwuHm4UjzMKRZuGo8fDE+kqFh9mvsKTRh9n40EmZu8xN'
        b'GoOH6upIatKfkY0aD6Q0pI/9oenJVwSG0xiZMwbs62ykIkQFnuTITBvS8zypGEG8NrrbNQiTxuyqkKSX5CKL12LS3uRWwNoM9iubTdrjAx+5qHB83TvfNFVv82+bqp90'
        b'jAaHmig37Jmp+mmpXOqOO5mUL5rHrmDWbt6zbacCQpLY1IJq59e9XBngs4WbWFHcxzwqXvLM+qIllBbv6wL7K9ZYHOdmcWIG3CtkwTYbqqze1hW2bibF/HNWKLVi9S4U'
        b'qg4Zy4ql/mxEkbAz+UOhO0eNlznEUr849EEqkiznu8JfYvF7fDJ7s5YtScrZMNs3V+DL7ynynhM5x7421YMzJ8G746cv/h28syCMkibUH+IsuxN+Nn6TMDZ+RnH7Edqj'
        b'V5J4pEjoKDybrV1EJ3gNrXbd6/nCz/l/Ps/a+LfmoGcy3/tjQPzmcE69H9VT61d2+iWhHTPTeMgDnGMuKhZxKNtyNmxValaA44yMOQPeBNuQmH2tqNgODmITLJLtFgba'
        b'iXn2TKwdXgu3xsdiFyTXFu57jlladx0ehXtBG9wOd5dOaDHcXuG+vAbYBY4wvtPXguqY89DA6+qYKBGTDqXyDuBOV4Az5Mw0Lw94hsFVtgzsJrPY7XiJ2SEOXr+5iaRZ'
        b'hD57gknkpMWJivHZa25wPwccrwOXGUu8C+qQNd4Wh8zSfNjOQmb6LjZ8owBsB9tDH2E3zBqlHLStR2UQfSkf7AZ74Q74eikSxztL4R4xn8oo5IMDK+E1If97lGg8Qiad'
        b'eOZuGk2WR55tpBg5usKNmhbWwX3RAS+xEhxahoL2D+wpOrRv+si0+A7HUY9pfcE3PEL7HQdVN6IyhhTv1d6YuZCsq8oa8Zs+LJg+Gp6Ajx8LGQ2J6Z/Tv6hPjA9FGw0O'
        b'J2eRGX6CaPyJ0eCwPl4Hd7+TmahlTLMxHlngP8bF+8PGHMcXBCmbxuzkymathpzrbc3VyRhrhpmvJ1c8jm027bXcjcVKxxZb+tNabL18ITXgkPzjjiQznJrEq8I1neoQ'
        b'IjPcjacQZbPNz0yqPFjJnEEUMH4u9aRTh8QqHTXhTvWnPH7Kqcq8J54C27lsi3O94m4ExjH4BpnhO/kQMvGPQrbOeFqaiVCeAtP5CFMVPiGHwS8w31iGcbvUv4ye6Sgv'
        b'TOJVjfIpD8qygl0Bxm78LC8vbAPTdaqmxn9bqxnRkmx4CrSKLdESELTw1rx/FSnDSV38Kk2TRqJ4CowWWAyP5QeXG05lK8flGHf8TYne/+Sc9fbv1yV4jC6xoYXsV6Ga'
        b'm+WOf2azGLXhl7ZkH4jr4CatIqjRjZLfnruPq45HMZ//6ozRdmR5nIgvYL9f87OC3IgdJaNfB6xenJTzUWIF6/1q/q+8qBmeNi3DmUIWEUDw7Wh4GYugRNhlLoUmSqBa'
        b'9lQ2G3NQlps5vx0/oktIMXJG6k75BHRv6tzUt/CGd+SofwBeCZt8dEYvXoLcn633Fg27in78MV2Tv17GNpvdqnX/EbNb/4uOiklrQyc7KgxEMizhUY9CsMTbolhq+1cf'
        b'shJkV+hzODdr1j2K9R9p8ohvljIkMlD58TiJaBLz2O/H1hX1Cn4mOPlR0YKK9Edj1PsF/OOf/EpDqZ1tihZTQvYjPPcDT8KD4JWJaso4gSCdaBtDJKkzyBwA7J23Es8B'
        b'RBe4icTYYbCNnZQeN6XN71JF9lTKW2RVNYqm2jUtvma9aRlFaCraQFPN7lRULF54Plihj8y6FZmtj8x+J/Sd9SORpR3cbqdOpx7ZDdewSUQ1xiM7Br/Hqs/BVv3UiCw1'
        b'N/EbEXn5PrWJP5EDYQfTQ+zrZKybbuZOAaqO8z/hCZs8T2g4Izt4xlesv3GoqAXK1VW/lLhSxD0mmb4GnIGn7FDiFqoF9IDTZJ+bg2s0OBMErqG2eYZ6RgZe0mI38xwX'
        b'vLYRvDzPzK5BlFQeVSJiUclgJ995rgPZ+PafzeRQH7qD3xKbWb2GIpu4dvJLmE1c+cWLR31Wr11FkW1pYB88AF8wHltN9nIZNnJVwFYjZVocWH0M9tojOr4uG3dlLoZv'
        b'zIVtmd4mrxxxyW2A2+T5j09TZInIs3cfH/pgOhoy+heC10Vy5ojmOM1JqHXx95gTWeYEV+fy4/MkH66TVEd5nZG8t20X/bwgoudqzVa/HYI/KdT8HSGfu9cNfZc93aHo'
        b'+k43qTJS7eXgVbY0fGtYUfjpbyqa0wQZOUVb3mwXLeco/LPuBKzb3jj7UHpCY6XTK76+g2+Gtfm3/TW9+uTvb+wHle+Wv8v9ghP/4obz76nBJs6LxXUldRdYF55ZdzG+'
        b'PLH5JIf6uTRSsmmj0IZYHjagFZwqBNvw9Kz5jBunHvTFk2WucTHhZifLgM4qk1l1XvQIs+0WQc7UYx6Nd7hvNhry8FQUszTkGriW5ABeWhdtML5Mtto0cJELX4MnpxN5'
        b'4wW6y5D9dYguxaUSegBnC8BuY9F8Kh6c5gdUw25mI8/RUkUh7AQ7TJt58NpWXiUxG8MkswtBHyrb6H8kzsd6sEXItWohYdo2nV2MtIz1KrlG1uJqNsgJhDCZQYbJPFzn'
        b'TgUGd8y97T9t1IcmQqtrY1/Svuf6Na9tGtg0VHYzLvsd6Xu1YM2doKhhYdZI0PRhn+km4dbvrvePHfEWnecMzr1op/fOGJpzw3vWbf+gHs2hjH7eDX/RnRDxcFzJSEjp'
        b'cEDpqE/ALZ9YvU/sTR8xnodz6nVi3vvLbvokjDLrTPtCRgTh/YLX/Af8B5eOCGfqBTNvCsIfeCI0zVgdn2F1XImqXm1VivKN7M54+SPmd5OaYoUZm/tK6/4j5re6+KHU'
        b'cQcxp6SWa02ekUUiLKM3h/hyMN9j13EJ1+NaLBLhEa7HNeN6PDP+xt3MM3C9CdCp/TiTTyazKdHiySjYlQS3A3y5B148PY2a1gS2kmP0yVI0cC7XJga1FzwP2rWUFvbB'
        b'PmbrZze4Bl8GZ1Bp9eA65ozXwRZ57z/e55GrNJerEw59kGj07p+IL7Zbl7g+8WzdjvtXe7J623xjeheh3zqOrC7p5OCHMru6uwoWlXTL/stvriFljUYlVNVWgba4/Fmw'
        b'H5yLAmi4kJXbLMq/gQt09vDQE+h+ixndk536Fp1NIITu4xm6v7/Ag/INvOUTpfeJ6vca9Bzij/jM6uDd9g4Y9Q+8z6F8Aj8JjTjNG/YWD7uKzejOZnxZqwpvWFd5siap'
        b'cWobirHZTcK2bCLxEXzkRuL7b3zSkAeLFfE0MtYWlWlBcyYRRzyIXDOas0FUh72HdoTybP4nKM+aQjdOYDJwEPHTLnAyHVUikAoErcv+v+a+Ay6qY/v/boOltwVW6tKE'
        b'haUjICLSBZYmxa60XWQVAVlQ7A0VO4gFbCw2FmMBKxrrTPKieXkvrGtCSfJi6jP1YYt5yS8v/5m5CywIRl/5fP5+ksveuXPPPdPPOTPne2R3F/3AkONQrr8sSj3wbgTq'
        b'RqfXtu+q29xscedbyYy/vEXpvG0XabbX8IvUSx9sM11lbVv7PjvrNjdT9faHd8MOtNcvDC7QV8/+mmgAUyaZcH5n97fYK2zQ6lIDG7R0JzIgGx2anmSp1XKDyaQ7hWq6'
        b'02wLijemdiLqPD3WTgo3pcV9a+8eO0cF50BSbVwP31WRrYxX8wNRD3PzOOnWae3Xaeqn1a30X6FbDedZf7CXDdjEpuKONjK7pf3WIdzbZuHe9ph6zS7nMbzLDcwvxZS2'
        b'0ZpMc7qaiY7zP+huL+gPL4p3/d0NL7IuwaA503sq3BOYABS2LIqji49qvSGWbakoYcrDUI75zYkH3g1Dfe742vZHgl3+G1rrr1TXMfQb+GFjJsyYGvPPQ4bZpwwN/eba'
        b'ZFrasmKQmKFDpc7Wi1c+RTMXmVA3ZsG14mRPHYppDy7NYYTAq8lIHh+1w3H6O5zGWTZHEzJI0+P4Wk045AnpdCJNpyse6HTd1o6KwFOs1rg2tzeSO4JVoii1R3Snc4zK'
        b'OqbTNEaro3GHdbRencK8gorS8hHXUK5WD6P7F3ZgHJ25JdpdbAHuYn2v2cXIJ/fpuFMtBgEsoQnttUn8N4knJ/bp7DUaNNotkC7tNVpcWllQJC0nHPgPvQ3oNSjAMLfS'
        b'kgppub/2TUAvVyKT0/i02CG0l7M4rwLH8pJWVuRVkZhS+DBJr6G0qqAoD0c8wknHSU58Dt6/V78fX1Ym0UKqO0FyVMgqiqWorvEJl3IsApQvwBe8BT4sxlhqLxdHF8Yk'
        b'ew3wr344OJJMQLLJ9wLK8xn4HAxGF8ovrSKIeL2csqLSEmkvqzCvqpcjXZgnKxYye9ky9GYvK19WgG50o2Ji0rJTs3rZMWkZceXleFbB9qYhyhmuc7wP8aSE6vcX3UeR'
        b'/Sx8ohUvGlSNfiH3f6CmvWAssn1hHBfQalqX/gqxN7MPbyfZerlWabxB14I1C+Xwkkk5h2LCEww9b0+wO5z24TzOBAfkFYvRQ3jRgEHpxiAFaT/TOAFuq8QDXjfQ1Au7'
        b'm532SEjxSUyZAi4iob0mFZwWwZ2+SVMSREm+SOdCon4/oAisn2UYg/Sr3bQktA79bIP1UzA8AFYSU5JBNS1ZtZuVBmKnUoY7BZRhoJ4LNxHlke0PbgSiARJImeQEgu3w'
        b'GCmCKdISmlF+JsXwoOB5cBPsng2u0UWoC5s6gKPJoAzgYXB5JhOekYILREn1zVyCXtShGELKAW4Ae8aY0T4IjenhAm/aeXAcm+LAdgasB2uXk2rkVHh5ZDNQTzXNdX5P'
        b'ytFgxCj9JiBKDIrhSc1bAfaC484Ecwaedc4U+3g7gnM+GHMnxRtuSWZQ1uAYOxJ2rCD01uk6lcez1uAIU7NTvZbT9MKtjRE5FsUQUbMtkfK8CV4nZ0TA+fnwmhdGbk2k'
        b'1RkTsJ3FA/X58HoioXZrmVWwI2M6Dt9kZxbgruGu0doMkdOlGN7UdNAMGtMXkJoDm73BaaQXkYjrbBHDsQpcDREQOk3pEeX/x/iZovxyy9fFptGdBRzJgDcDgwBSfBg+'
        b'lI4VEkF2I7kW61mLYAt8E5/nT0Eau54/E2xDLdEwH7YTar06Yh8PBlr7THM9wxL0aQuB2bRoTAs1sy81ayo4kM+kP7KxNMUhj3ZZIKclNzJdqriEzBonTvoTFr11CqM8'
        b'KNJbpsOjsDEwKJjClRU/E+zRgadJ6MywWeCIGAPbboU7iBsoZQyqWWAjbIoYm0PvjEpCF4uoB3iGNr/jEk6z5TE5ClFj4hLGgh1g3xR74vESVcHHxEQxcGvqYI+yAbvZ'
        b'YAusXkq6dCTogDXoZR1cpGyoQA23YwbdDw7BHXk0M6l0wxmXscBBsCUUNoGThBlfXQubiQx8VC93BafKi6LRYA5J4NnAANxFRWjEgDdQ1zoFb5BeOgu2gesFmZpuykTd'
        b'9BwD7o6mkYPSTDICxyFBnRFA5cBG9NbaWPJSCbzkhFT+Gi8x9ghhUDoy5hjUdFvpflLDMgsMwW+FUlFgK2iwLycHtefBs8maTrcFnKUoQ6CMD2eZcsAaerzeBK2z0Huo'
        b'zsKoSKTx7LeYQ4ZfJWhdIaarSohddA3hXtBhyrKERyJo87UhV3SIKcD1n9yen0KRSrRBA3F/YAgS6hG1ZTggFtizlLAB6hYVwDZ4GbGCQanEqHMUMG1RNZ8iDTcpOBm9'
        b'hrrTBIqdC/aXgv2Eu5hZs8VivO/KLGXYwguRiMI68qEIHbAXvYC4DqdALdLlDsCGafSHri6A6+bBJjGev7bhTVkdC6YeOA/PELbHpi5zdWQ+xL156tFwA5rtFLiDC877'
        b'BXEoRjQFFVzQBG7Y0BBER8zgKaSGJeENYha8wQBrYR04EA320lv/ifFFUSw+A41Yz+np0+kR65AP3sTU0AwQQ9mkAMXcOfSkeQ5uxw63W5KRlDSXAbeF+PraEjL/ih5D'
        b'/YvKxXW5YuZyzYBFauf6HHEiPnXMZjOmwwOgqRIcoRXUm06wjnh2+VC2YLcPE2ylD/03JsQT5+6MBLg5zRseLJlKH+SHNSkiNOlQ1GRzXVs0pvaTCWkpbLYeAJjCm9cN'
        b'THBwNdgDWuHGwaByJdGsVRp4ApFtZT490MzBaTms18EHD6b7isAheIocD+Qu4YuH7dAHB6NVhU25gZOcSlt4mEw48AT6aiNsgmfg1ikYhQDNYOaMOSImGTdjQONScRbc'
        b'jnoDbKQWwnbU6k3wPBmL4grQMIiQhj5UxCK8u6VxZClRpHK43FXwgAE+NkCllYEb8CRsI7hltnD/XC9UGaixE7yTiGodNjnRn02NzeIEgJ1gNymtssrGsIxZhFeI2X9i'
        b'6tL9Q47Wq1Z4QBfXPOUGa8HNGeA0IaoLa2cOIwo2zEv0Z1JjszmBU2ADPS1eA7tBi3gKWkcx+ha4EASv59KtbBcGd2emTMFoZszlDPSVBjt4nU3qYTHYIBVn0/VwnEoC'
        b'x+AFNKedIvBqMyfCWhp/LnFwQnMEW9mgmQUvUaFk9IAjduAiPGCEGaC8rcG1CqCkAxNftqjCYzsO7PBJTEXvJnoHsFFP2s8urtSsLhvgdbgBHmDhI4AU3IlGxPVl9GRa'
        b'CW4G4pfBUXBt4G0mevsAe6Ex2El/+QBa9Y7DreinDIkml2TGqP1sSdvehAexp8kA0yYWrOSw+ZPhTVLTArANHCGGGUe0wsFtjmAjmgpwTYNq3xg8j5WA8z6ka/nSoHOo'
        b'iGy4xRmuoQfNhdVwBzyARgZ4k0oEm8CbSNFeQw+aakt0txWJIAsoeMB0AVS6E5YywWEPsbd3IjjlkYQHm0UkywpxvxtcE9Fl2e0Br8EDhhhagHJzAhdARyqZGzJgy5hh'
        b'fvtTYH0xOOBPD/er02PkRkZoikIDzw2eh6fhwUzSx9Zn6jtfZnngPlZ8Ic2VIjj4vlOD4VZU7lJKGlsKah1pVHU00BuQlJaAoei2idO8CYcCW7Y+Gv9teUbEhL7T0XX1'
        b'WwwF6p2RJZ9UTUpfRQ/RyWDdWGKrWkblwvplC+AeWaZ5FUs+H9XAJt/5e/bOkJtHmb4zb2PkdD9XJz7HosBw/rXSo2PHxn+x8tPL07/aPdW71Mukeubcx5d89/rudVzn'
        b'Kyv9WOZxYsL5DE7mB+rfc5a8/9fFTyb8Pjn2sO/3O/f+Jc6pNyA9o+iDvZM+H6e2PL3tUc3jVR9++Ow9Twvf99/vmdusBKUtgthpGwMaFi7lL4md95tzc+3G7rvPvpkV'
        b'UP3958mrW3MN8rf3JLXtsHj21dOitB8e1k1zfjd+6Q/Zut8uKtJ/kLPtt2dn5hZOft8/9GYimBtQ97Rjvd9t07F16YtNT/CjOXpv2lfLNrbp6i23r/aMUTrlNa33g6aF'
        b'dW2fRjUUcHUzmr4MjwmtqeboNv/V1NjpduVR48Bql9bS+84xoft/sdvhX/1FQuhngoMSbktGE5RtLBs77jNRTOim6ifGgLOxzExvn12128ayMXrTDJun/fNyUrtQMe8r'
        b'he6c7cvTs/w+8VSun8j6VPXDjkvX3/hM9mH1pLi3pjv8uHhS3KmZmxs3957tDlNKei8F7xOsas+O+yXp5vL1Rwq91gVMjfwxxOkNRedzWW6X7u9jdHd2l5YYPkoq1E0t'
        b'Zn/fpeMeOU0ljz+bITdY8ffiBcqnM2fHBeTsq//nsolZoTkPW26WnKOkeryQXWMuRjTkhZs0Oll8fvJGY1Wx4fLIwiex1bOSv/yo6h8/Gn48e0vZPqePz+v9EvG3Fk70'
        b'o1y/nN/8Wr+c8m6SQ+DScKflAXFV75oermN/Pv67vxt+xnm0et27D9yOro5LLdrS98vNE8xsaLuxL1hq9A/+b8t/u+3xbPJk4yb+n+adOrJ2ybd/fq73nmiGW9lH985+'
        b'VJ1e+WDOv07aSAt6eH+7fNMk8Fnu4lihxVMSyPQ4OD5reIio8lStA1w3wEGCRAaugmtGXnjviAn2M+BpoExZuYSGNWmYhpb5rVhJ0aHYsQxwIgRc91xKgnHiFdcCbDUp'
        b'Y8OLhuVootxusthIT4figSZWKTwE1mhw1wxgqwFoFSX0b16YwasscGUROA3O6ZINCeEk4ik06AhkCs+BdicmOak2LhvUg62+Gl8gLjzKRPLjQSRsHZ1KOExLn0zwUWir'
        b'LTeFGQKOSJKqiIXEFGW7hkYwKtdiRgXYFJUFjpNdjlhwHH3yNFsbso3pDU/PJySDYLMJjdeCsVpQSbaAc+DcClJVrrKSfAf6VJ3mSB1s1CWH1+DJlWAX3v6ZCFuGn6pb'
        b'A/aSuF1I1zoNNCfchh6Cgy3xoHk2OEsfqGtxdx3MNHAITh8pVUfRqrCWDjBaZ2KCT93hjTqsJmH/MU0teI3nIFXjJLgE1gST77qh5Rxj6SWCE7EjmLnBhoW0T1eDdNpw'
        b'GBf+3FIuWE8fvVMgyffEsKN3YE0QqHYBm/5jz6yhqCSsPIlkmdGg1QfdEjvUDbbGIdmScnDWgJcFquyD79lHdaBL6q0Ztfof86wbdJoMGg0OGKl5Y5W8LuF4lXB8h6dK'
        b'GKfixdUyeix4H9u4dLrG3+G9P+bumM7MrD/bqVyz1TZTO3lTuy3sFVZqC3e8NSSuE+M9I0RJEacMVPN9B+5aA5WL22Qq30i1V5SaHz2YK7jNvXVSR7SaP0krjXiFFau9'
        b'Ym5lqPkJwx/MRzRuBaj58cMfFKq9JnaUDyVPHhSpvSbdMlfzY4c/mKf2irjFQG88eNVvLFR7xd7KV/MTR+TKX82PG/EbTDU/5pUfyNRekbecRyBFHjiNVo6RSEnVXuEd'
        b'iN2oUd8YXvJRK3GA1DNvW0urR2EU31kxVmnV7NPmct86uEfo3SpvC+zQ6Vh8xfiW/A6zM1TcFTpFFTqlMyNbHTpV7TutUzi9QadhcaNxt7V9Q2Hdqi5rT5W1p1Jydn7r'
        b'/HvWoWTzMkLtMKkT9QVbx6aI/RHKqW3xrXM7JDdLrpTc807uFvq26bQ6NLAPGv9hhh57Z0Ww0kPlEoiR+uI1vVPBbNFt1n2A9zi9VHwvZXzblNake6KIjsB7orhbLrcW'
        b'q/mp3XyHJv1GfcUkNT/wHn9uh+5tl1uFd3JU8XPU0XNVoXPv8SWd+ZJuvn0zSxGvnKRynaAWhKv44YSqZq/K6rJNu01Hmto/+Q6qsSndL3tkr9BRLG427hKEqAQhHTpq'
        b'wSQVHgw0+QiVa5haMEGFvfaH00hR+yfdiSIcj/posKgxmkdJav/J9KAa6R00ENNeLMhktf9Apx9GTqz2T+h/MOSdpDsctX9qZ/oUNT/jxddS1f7iO9PU/Oxuvm2f0FJo'
        b'9YSydLJ+Slla8jH6zph94l1iRbCKJ9yr7RRjQFvG8VL1etg0eMp8AZhmM3GoHDJlnuy3jmOHyimWDIYNBv17HdcZYh1v0PGglAaBQ4/nDmzEFFI0KAHZgsEmXKpGV7MF'
        b'wxhiuv1Pz/m9sAUjoIabbt1p022CJVq6I4+zsf4cOmcCRe/L4KpLDwwAWImHylkOlMOUEGInXZGBtC18+BJemz+GGrMkn6TqWwJFIBtvTacFUAFZYBshfX45lzJNCNfB'
        b'MeNDI1kUOWZTNx4lhgexcGKftRWtxD+QrGD8nJ/Mxu4IgYIw2lCxCOzWCQxi54OL2DWBKpgKW0m6H1IzmwKDdFjzUfo+Sgq3GxMie4N1KEPXX5k4vHzq2PE05WsxZpSg'
        b'KA+bQIsdl8ygeVgnMaUEvGgmTnyYJ6JzFtkYUXx2NvaTKA7ItqBzXp9oSPHTJSSxd8l0OqfZMgOKF87SwQqSfUAUndMrHiWK8jgo0fD7gGw60blIlzLM7cYsGQrtJ1C0'
        b'CUgBmm2IUp0NTrOtwXqKs5iB5Mo6L9ro6AsOBMbBzX7YSu1KgV2zIa3728qcqdiKb3VQS+XXZ3BpNQrsAWuMiB4VuWwZtWwpUlSJ3WzfSiQq6aMfF8Eb4BIFLkXGEw1U'
        b'F0lS7fAAIlKKZNrLGBj4BqwnjeiQFwLrUbddJPSmvKESXqZxywvZFHeFDzGMvm+gTx9dEi1cDevhHrhnJpIN93CQDrmRAhfBwVL64xtBLUC9BJ9ROG5kT9lPBBeIhdBe'
        b'4j3ohAhryukTT7mltG58GV5MzXSB172xtsqAdQxzI3CD1o2Pgl0iDNgATkJFFVUFzhvTfpL1k6YAPALAlpyl1NIocJhkd58PTgDsFQYaI5ZTy0EjuEFmEtIkheNReYpr'
        b'WLg8tS4mNHhVxYWJ5Mji7wyK4dwlO1o3kyPHuzHGGSUX90Slgkjexk+ThesETCYzLva+UvXWcds5S9ln+8xT3nzDNmgZZZwbHuv7zYXGMQt+MRlT8P2RlL/9/n7X85uN'
        b'Fxw/c0+c+edKb4us2aJd8iNZ15Qzkz/wMj45zkr0hel91plFytDKW7I1Mw38vr103vuEUDjTtsPmrpEq6ViGaci0z8evLnlDsvaLH+xvFUkz3pio/DbC7q0b8w5f+sv5'
        b'o08Evbfq059+2H7hk4MnzDdVRf9JVzhH/M0ej6M5Gd9Xd/yjPbPujv0XJ1123Do5EX643Ov6w/Orj/z98NpHJaFS+a2HJeHSxe76Jx98Fv+8b9ObVr6Kd7bectn53q9h'
        b'TxpiDj/MXFfu+8a4Xx0+/2b3v67udzn86KH/ub8/4lWsys0KXPt58kFGi1/qPpeju348mLHs7H0DxV+zfzs3c9oHXvdTnH94y+TZW9bdC3Zd//DmvKynNVdDH6fdFT+d'
        b'+M5qdszKJQ9FP85+t31Wo3L5CqPd9feW8M9cy34eskzxtdr62ZsrHzzsEPLJOa2khDywdUk6qBv9AJgO2Atq4Q0aQmGfxJ94LqV6ezJgjR8Sty8ywV64DZ6in58Cu8Ee'
        b'WnHS8RvAUAAtoI1Gfzg+NqbfO4iXiP2DKuABWE0rKzfBzclYe0jBZj0cdA+jLUYFwzMscCYyi9YG9k6E5zEq/1a4wxwfKmNg8AlnK3iE6BQirnS4ckmrlmCdH9Yuw8bT'
        b'B1cvVq3AXHBFXtiae4aBtIgz9oRBkTE8Ss60wgbDgUOtM8KJ2qgPd6/C5J3gKRo3kmwEWU1n28JjkPYoshbCbVj1o0EjvYh53twNNsMWFjjFLyOfSLKDW4i2FgFu9Cts'
        b'oNWH6K/wBNywagRdDGzzYIHm8RpPKXBkke0QnQi0zyLAS20z6ZpstSt9UVcDN6NZ4Gg23E7OBSaKkDrnmyDy8cE7fYhL2AqPlbKQOnc2jtTlamxu1bhQtYP9w32owCGh'
        b'xm8Yns4h2XaANkMxh2IzGeCwGLaSsmYtkw+4DY8ppw/uwbZ0cvCwMgPvNpLzgavDRz0hOANeJGUOhK0JAzo36ABXab17azZsIKrnYtiEg08j3dOnbGTt8xK4Ao+RhkR1'
        b'sQ2cHVQa4VqwgVYcq4GynPZjawEXy/qR1U3KKT2MrK4Hd72Se5YWpEQvG3sjLDMeFIHwPVEbuSwa7HumNcWzrq2oH69g7IrotrV/YMrDp5q7TF1Vpq6KKUrmWd1W3W6e'
        b'DfnPWiNld/GESHLr4vmqeL5tDDUvoC2gLbCTF4Ie02iTShcVz/seL7jN9R4vosO1hydQ8Fpsm227nPxVTv5t/mreuC7eBBVvQkeUmhcxQNVTxfPs4vmpeH5tZmpeYFt0'
        b'WwxGC3n5R3uQcsvu4nuq+J5qnlcXz1/F829zUvOC2jLaMjt548lzLPDXp9EklOihSJmhRA/9h3Oc2eZ62afdpysgURWQeMdDHZB5jzejc9qMfzdfSJvbPd7EjgCtGghW'
        b'OQV3IP7DuniRKl7kLVTSGPzYTlmOCtXFC1XxQjvM1bxw+h3HZsc258H6ilbzJtENMeQ7oW1j7/GiO+LJI2u6yEi3o0V2NSqzs9K/k+f9B88G2rkvxM7f/AllJ7R4Hkrx'
        b'bOqCGzzUFi5Px9uZufWFUWaW/d3jvqk76jD03X3Tsd0W1l0WbioLN6XFPQvRA41KxlGyuzwmqDwm9CuceY0m9/i+yph7/GCkULJvGlwxeMJiCONwdD+nOMZTimEZj3El'
        b'zCz3GdQZNMTcNxV0a3/F2mZfVV2Vgt1i1GyktvapZWvQURVOnTzXgROsnTy3blePlpTmlDZnleu4LtdwlWt4xzS1a5zm4H4+jrNobVtr8OLRnFcAcCF7UUPwW45hdWPY'
        b'WPuxX9/4J9I3ZlgzGOb4NM5ruYlgy6WQQQR2IeMbJNv8ThyYvsGn+IXWw0BaiF9iuQE+YuKGLziSfDkGr+7l9ruG9f/C51WICxSNzoJ9EcgBXXJQkhxiIyeNeg1z0qMy'
        b'olJysmakx2X2suTSil42RqfsNdA8yIzLyiS6FqmB/8zs9QIuizWu1EF3bRGuz0omAWb5ScfEaOwjZ4pn12Pq3s0LeMph8oJqYh/pUHauPaa+3bwglGIXXJM8iLsSiHFX'
        b'xhHcFQ2kighDqvhog6x44hQRSbG07zH1oIFYLP1r4p5xWUY+z/SZRumMZ1wDo0nPbNhGvs8NdYz8+yh0+cmUZRTLeGRMOTg185qLOu18exxcetw8elzde8YKla6KmehP'
        b'q4tSopg7+MPVXclWhPX/cRqrqFAY9t85OClcG2b2OOM7ux4nV0WWQr/HzVMZpEh+5GhqZ97nzBtj3s2zb5T3sdCvBzzbxsw+DvqFEYKdmgOb5SirT58uTuFSlo7NFphC'
        b'nx6+16csUW4FryGpzwDfG6LCNsoVQQ3z+4zwvTFladdp799ngm9MB182w/fmlKVzcwzmsc8C3/MGn1vieyv0cmMBZr7PGt/zB+/H4HsbytKhmaWIbVjWZ4vv7Qbv7fG9'
        b'w2B+R3wvoCxtGmMU7IawPid87zz43AXdP3JFVY6Lgg97okyP3XGim7udMWr7LAZl59iwQpmocgzucpygcpygdpyoto3o4ds2JCutVHZ+XXbjVHbj1HYhan7oIw7L1rhG'
        b'/Fw/mmHk+ZjC1+cJTD8ju0cUutBeHQQsTAE2FWh7LnAouE5kmsWaCQ7PHaKSG2j+PnHGwBpmWsAaDAynoYGbMEH/6xIABZOhdxLm0PtTrDd0aYJ6lMSOHPHUqzEpZEvY'
        b'1Xr9VoKZbCYl5WgAOXSHAHJwJFyUqqeVqktS9VGqgVYql6QaolQjrVQ9kmqMUk20UvVJqilKNdNKNSCp5ijVQivVkC6xxL6/VBLeQSZJ0yFXAsQx34Z64Z/EkgBC2L/4'
        b'5EUAiZfSsXpVOsu0fh9j7GBIHGqYxJ5DH8gzwJFbC/UkfK16N0HP9WqMSXuMqebONB1s31M2/bTIkVwWjgFbyJHYVg8Ee5hpttRab57QsZdGoRKnxv2ydwjuIoYF7n8k'
        b'KCjOk8sFHuml8orF0nJ5XokEz+oyaYlwyDtDbjyzMPwjHawRx2otzZeXFksr6AirOEplcSk+ZImjZErLKuhArQTCcljw0HJs4BLq9urlSRbL5PjwZa+B5ic5Q8mlA+eh'
        b'ZJakcHEva0EJSlsolcgqF6I0bhnifElpuaSAq1X7A/Ey1lDaB+f7A+cSRzVc/WxU8RxUeTrkbLORJmoG6q6bB0LjrtQjZjWulllNT8uAxl2lpzGrDUvVNqt99og1As5n'
        b'YomsQkYc9DS4z/2tISuRV+SVFEhfHeVzoOrCNCihg9FnMWXNCVQcTNYjmj73ijIslJYLR44rGCXQHAKmIaEFlWXYVzpEIJHNk1WMAD46lAvcagN84JC7L+ECPR6NhxJB'
        b'XnFZUZ73SKyMFxQUoU8WkMC2owZu1fSbkeuEfirwSEHdFbEkLfk3amTcH9UI6rB0DNDY+KmC4rx8abHAA/3UDqsq9BkWsJR0CvmIXAxlndStR4BWVYzAvIYRNGjCBMkE'
        b'GwpTmeybPBD+lq4WNPoz8wqKcMBawhOJZ4wG9ygYsJX5xVKJZnQPpZKOrqUldOhbRIlAwKJ7uqY0c8LIdZxYMRCQOE9TzfnSiiVSaYkgSOAhoWOWCsn0EjpqQfsnBrra'
        b'6TuBTKJpsMA/arD+2UQT+FVzJyiXzpPJUQ2jWQxNdqQ7iQSVmmarLMEBWP8A1fZFvy0T2pY+OdeUEqDljirLFZk621GV4RSJ8XgV7Ov3FdVE4QAtCenEXzR5wGQzRTvg'
        b'34ZIQ9NyeJ7G6pnBozxESOiMzA3PzZ5DVU5EiWAH2JgwjKg2xfQgRBOf3szWJttUZgiPhU4mZOvmGlH89BPYtJ38TqoTVTkJJRrCs3A4rzRZLduRNqegwwccAzUGoBlc'
        b'AgpCOGeSDmWY9YBFCXJFzsJZVGUIroV6jKY7IuVEr0xEELSCcwNE18CdemBPLjhECP7gokeZehgx8ZaBTlkyzSk4DtpGJghrBi11Q1mdAd4ElwzAUbjOkRC+qm+AdIRi'
        b'JmWaK8pfEU63lyu4OnIVePRbpYYQvYoqZiN4wwDWSMFWGe/MEqYcuxpUPIne8L7YmOlkqPPg8Qn19Nxtmx47nG98O/THbbaXfwxd88h0bkbQPafduRbgSN/qH1wioqL1'
        b'//mQ7cv41HMJ0Ev6yjr4M/1r73434+BOal9V9vHAP997c6tr+f7ie08FKe1B14+r3jsXGPjbz8LFCv6J7vmFF/P/7lsrsREaur7jmpM4tkV18MKh74r/biOf5FfX2Bzw'
        b'W9MPK1zsdTIk90rqU5uCzpWs+bOt7boJwW+qhfrENAfaQCPcha2IwrHw6lArIlhPhwVMFoDNtM8uuDD00AZYD7fRdsIrQRxCREMBd8CJSziUI2xgw7PxsJbksgHrwTnY'
        b'iKrtBZMkjmFzOYn2vW2AR+E1L9rUJZxIowYaw33EgLcKrocn54Gt2Jw4YCzNlBIzKtes0gVJ4cT212/4myInRciAF2E9i/uiNZcFzkyJIQdKJOA66qvNGC1qqBkS2yBP'
        b'gSsEkwAcdE2gZXxveB5eSrOWE/M0uk8mMr+3DpUCqnXBoTSw97+s9hJ4IbN++WIorJI1DcX7qGoM5TK2uUApPFqidh6HEZF6LKxqK/atrluttnBXOt2z8CIYSpPVNgmd'
        b'vIRuV1+MoeREMnVZe6joaH5R9yy8SbZEtU1SJy8J6ZnNmUr+0Tlqp0CMq0TTXFW3Sm0xVml2z8KTZI5X20zu5E3WBLI5IEY59eicS+uW1kcoEFU3OjCg2ia6kxf9wM6R'
        b'ZHkt4k7CFodmB7WT/x9ndXGrZX9gKngx9kk7tkucw5fz+HIBXy7iyyV8ufzHHn4DUU+GefmN0kJCJDfK8QTz+8/YoXQMg5HBwIFPMl4rrhyetpp1/Kl2g/B/DwKqqB+v'
        b'aEDOHA3oZrAI/Tg32agIWnBFtJTbLyqOgKj070NAaYCqDHO05NBX53M65vPQAJ8Ow/gkstYgl/9JNerl9Eumr87dLMzdIH6RI81dvyD4QiX+J/XHzkFS66tzNhdx9mQA'
        b'x2jG/hk0h7Y0h1py73/IXXU/d0iUfXXu8nC9dTL6681jUATOGw7rJf/vtW+/EPrqfEqGtq8NtlBqSa//Nc76JdpX52zei5yhdh2QjLU4EzKJbZi2Eg/4JaYWsLR4wWjn'
        b'xDGRBLLU03Iv1iEKOQ63oUeCWeJQlkY1xoWGA87Guv9NZ+NnHPMRVPIoiQTHVyqRLtHuH2iMvVKkpTikQNGZsT0kTyJB6gJSOvI0+icJmITjYogE88pLK8tok0ieoKB0'
        b'Yb6sJA9HdHqBJOqongMgcZ4igac2vB26Jwh6KFN+aekCzCo22xANiWajYmnZa1gRBj4UJsgsXYh1Udq6g+ODaLDl8vJLK+n4UbgHSCWj1Q3+F19aLpDiKpHICguR7oRm'
        b'KlqrG1ooTX2TmFKo2uZpop+MoFDhf0hJLMgrITriywwE/sFaarHAo7SMxMsqHl1B1q5XWvl7YYIQeETll0sLikoqS+bJNdYCEgNlREYH+4FcLptXQrqCD6kTLcKaKGoC'
        b'mXapZEhxRkryiFT7FWJ/0sjB4wf0Yvwlf6EI2+MEEml+Bf4OylGAVFYZvikYTZUnvVJG3pdLK0jdhY5/hT4Tj72xif1v+FCRSeVhr9znEK+yCg0But5JyoBdwSOztLgY'
        b'2xJKhQJPz4XYWIOKs9TTc1SrDynxEIp00iDJyah6S7x9E9C6VPI6pGlQPo1poFROCqwB6nul9/HgpN/WHq4+gpQBqwcZvqX586UFFQLSgiOPgcy00GA/f43tFZtW6dHp'
        b'82psDPGuDxtmfVpcKiuQDnT4aGmxdF4hzicUzPIPmPMqJAM0zVgppYsjKyGM4lEfG5uSMmMGLtlIMebwv7K8pQtJhDppOV74RIKFqJ4HbCxaDAW8nCFN82CsjKHthVOG'
        b'Wtzo0eLbP1JGZIsW/6JRIfHYxzTQ5wP9Rv38EDyDfvuj1jBBqWhElshlNFOlhSN+NU8yH/UMUh/4BRKmL68K/x55bhzZcjmEiJyYXmUFRRWyebgo8oKiYngNzeTFwhfH'
        b'7Kg0vQWo32RWSCvR5DpAAPVgmUBTRWiGWohGXFy2d1ZeRb4Um7Mlo1BC3YUOeFVcuXCBtGjk+vcWBA7LRr6WV1m4rLJCilYOHCNSMLW0XE6YGoVGUJggqrKwSJpfiYce'
        b'eiGqsqIUr28LRnlhXJggsUQiWyxDnbm4GL2QvVCeV7FMPqzko7wdPBLLr19BISORkWmxtfD12Aodid7r1ct4UpGDVf8HNT9iYhbdk7HdeRjfr90TtYtfWI5K44HrdoCn'
        b'vPxllfOEo3c/7dcFIW6jd8AhGf3Hj5YTdbMS37zRu9RQMsGjkQl+GRnUKQbK9xIaodrZRi3a+CHERijXqAuaBm8FzXCaX0QeQDIpmlv7p3KPTHqNHXXBHoRzCRPEoBsB'
        b'fYdkHA8xupWWoP9RNxfgNSh01ClXCwhmKJmAYWQCXkqGYMbQS8bUqCzvxFiBR3ZmBfqL15txo742gDFDvxqXTWZqnCDwQINc08VRs49eDZXlSEQuQKtFjOaXSKAl28Vl'
        b'Zwg8psFjReVokCJegkZnRQveZpDYQLKGqX5S8gWV5fIXmXqZuDeaeElEyVeX/AZEtKghW0ivJsMQwJ4wQSr+I5gV4Dfn1V8LoF8LIK+N3hr9SEAaEVJzj5Xxl/UDAhOE'
        b'XsF/UMYX840+iyVIy8tLfOPL8yrRpdjHN16GpLvRZy2SffS5CtMZfX7CHxh9gnrZl9GsFFeEhDA0948+NRHekMwmGZmN0SoPSbFSaQWWLPBfJGAFv1S+yy+tChPgIwtI'
        b'firEUitKQHU+eqPilzD+Ev1WXrEA37z0jQJZBR6Q6PpScY8GncI56R+EsAjL6d6B/sHBqKeNzhPGe0IM4T8v7ZGFeai08WhSeVkmghiFWgj/EcwKHj2jZprTTHEv69H9'
        b'WFZhgmj0i5aEZwWEvDT/wNAmrwzdIn5pffcjZGnepNtn9Mka42IhES06KhU1z+gzYr6sABFMjEGfHmFE/kGgas027Z9YGmjz+YWidwsL6XNbYDtohpf68UbwqfN+zJE9'
        b'YXTQ6dJwDUDwsgrDtZJYGnsDnnKC7RoYFNCQxWaApsQKkv3MQitKRFGmawqqwhvK0jRwSdcrgALWh4LLBB3FB+zNIFgncBs4A4/3g5P4lGJEKYwmBa+CDkJtjnQF42cm'
        b'Nd3PTGKbZrOcqsQgznBTbIEX3O6VhENcwZ2gBjbDreBUUgoNcYwRQrdmUFVBevPAZkQHozF4G6W5SnRrjKiyPIuPps8xEdOAxsUO0pHQjDGVBHpHawDNGJ4GG/Fe8nbQ'
        b'aCg0ho1kU0X2iL2OKWcyKKpum96e9DdTYaTpwYlNOePdJwbxjimOHG/+0v3htFj+ZtD+eey5zM7TWytqHFQz/s/l7/W+Qh/h9G8q7v31r99/v8Iqx/T68YvOfs/273nL'
        b'NivtSNeWo3O9Enz8v/OiAhx5s7PFH6V9H7hr6e7bj8YlRacfNMzsemLCn7Hz6Ndv+WTf+a5v1futT+Rf/J/k+t5j2+DdvF98lQ1hE5fdvb7PZP4PX+26EWt/0TWuccPH'
        b'RtkmP73bs/S+16Pvf/hrYf58+cf5qbPKp29I2LLnk8cpNzdf/+3UTHGBQ8kvzB/LZ1Zzrc8Gv+MYZpq3adb9DZP3Kr8+dG7L1qmH7PzDLk4zGtcd/37Rw9+3rXimu+Or'
        b'rFOx4Yk8IZdsUTqDbRnYaV4Iagf95kUCEv86gju+32vey0XMAOdKzcme5xKwB573gpvTvKYmglNsSqeY6QyU8DpxjQiNMTZIhx2DqMkDPvPHZz0l3WG3CzyptS05bFMS'
        b'bF8+sC8JWxyJN8VMeAFuMBgRNNkJ9b6zlba0l/0V8AbcKwen48clpHp74LxwJ/YAqWWBtnLY9BRbnWVmc8XJiQyKmcFInOQJ2sYJTf6bURpx3F7BoO/7MGdOwwFjd7/7'
        b'e6ImLmm6AyUQ3XP0Uy7C8WRsGypUFi49tu7d7h4NhhgN1FWxuFnUxrpvHdTj7tWa2WbRJukIbi++FXgrujN4cldwiio45U6BOjhD7Z3Z6Z7VwG6Y2mjYbeuo0GkM77IV'
        b'qWxFdbHdlg4KV5XlWELXswE/bgprDDswkOFLvCU5SW0T2cmLxKHfZivHd1qNq2V1W1g1SLocfFToPwsfAtzcZeulsvVSW4vaOPesx33s4Nnplap2SOvkp/UxWZb+PX7j'
        b'O1w7/eJuWdzzi8PuDcT11kLF9+7TYZl5d/O8a2O7eK4qnqsik3hFeKvwf+Pa2GreuJ+f6lJ2bo8pBqLj4KWMUTv4dfL9fu1joYRfn3IpvhN6ZubdY+OuZKltRJ08EX5m'
        b'5v0LAeYFAVYxQgrqOcYyKSjUi5nEggHcmDAWDOOg328x9WL5rLcMuLEWrLcsOOg3vd1qQm+3Dm4nYLzu1/LhHdYJBvdbX9oJ5rO04C6n2DIY/s8pdHmdA/Y4nNXIoToI'
        b'UD5bE6qDU0PV6Gggo/+74ToKhczyb6hhAfkcX1jX3Oh1bUscWaC4SfG5Is+JITTMG9zosBjUT5dXYiSr7WyKDc8yViY6Drr5whMmcK8Bq2AyRU2jpskd6beOwp1OmfQb'
        b'5eANBnyTgheydenlU7wSL0Vc//F5swIlljQVE1/vwCAdapoDccmdQGNdwYPwilVgEJuaxyIevKBWRiiYsHXx7lHubUGuyHFREO1V+0GQGfZSLju3PDf5d8qf9tZ0kZDE'
        b'KnFlrmFBgManN5VlRKHZcvqVrNzkD20i6ZxvzzMkifOn5CYHe82lcybJ9Skeer3IMddQLE6gcxZnGuBEQbBNbvJfnSfSiZJcwpLHGt9cw8t+uZq621sG92Wmp6fjoNeg'
        b'mhFLgbVTwFni5MqBByMC/fzQuJgpZ+Bw4WtDfYgfqwDsC8tMRy3JLAYbwAn0ANbBU8T/FbQaelDuA66/tN9vFthJJIkgeBruCyRev5XwFHb8hY05dAutLZuUSYH6lSQc'
        b'aPkqGvdpI2wF6wLZGHiNogKogOXgKu0Ue9QHboD1DMNYtNpT3kvgHuJ1PBVsqqJ9drHDLtig8dldDRQ0a6fhXn5mugBjjp9Ha/t5Sx3Q7AybyMNVOdNilmqFDyVuuzZQ'
        b'QXvV4oq+kq+HA0WGNszLLb4yoZyuU1d9Lk5MWFWYm+woj9YITOfAGvhGJq5TaokDXE/lTYJHaCdwPUvKAzWWQXKu3TG9YBocGHZMApsz04FCiL18wbWwlQaweaEGnrNs'
        b'8UK5USCqMSfYyARvIOkKSW7XZEHtSxlyvF9p0up/KOtuKvQztZ+QGHL13oZdezOsnCLWuay+1fhRjb58gW/2VzXy4w4dgogjqzfeX5178E86XzYnJRyfbn/zecCvy39m'
        b'vF97y9C83UfYd8jV0fLnSwsX/w0eqPo/dsKx6krlV1O//8GgXXbMqs2K57XMfe1ez19mpbGS7E8lUUu+bkqXOm5dezLgQ9OjE+tvpBf8KPa9TIn99zHbrvEM5FPvvFNz'
        b'5Ezgz99OLXx0ufsjkU/+5d+WfyANHbdvq0t1t9/y8Y2V7xTzxy6d8/XRC6FTj3+TNXNSlg4ne/aX3cGe4899cvfcyoOsj9y+T+B/0Lwzy2XjJ+f/xctwtM5+Z9WHXhY6'
        b'H4R3e326dOeqtM3fTP3+CyrtYUjQM8FvrWcf/BwU58+L+ly42O/w22eOTNu22mX5grSozOs9G9YUlNy70NYRW9RQ+vNS19/PrPT6aMq8v363+RuP8N9/T5aOu5pXq14/'
        b'bn/YIUb82W8c2n9l+xbuWfFP9Tc7jtovbizxrVrzrdra6OeKj27vF/KeelEYC/Jm2OiSiLf5pH5BhJ1G3DU9PODFmfCwFxFukJTChW8yQR28HEZOdMnABSQWJaUkI7Hz'
        b'DDzHdmKAQ2H55MUJaKa6Go9E5yERGhjgCvHLXQRbwDWt6LLKMbTf7wEPItbAEwsm9svcme7ajrmCOI6ejoTIZEvBdRyiiJwzqwL19FEz0DSD9sc8x3UkfrnePvBwhcYv'
        b'F24qoePGX44ypk/D7UcFGHKmLm0G4Q9uhCeYtN/wNvT1LbG037AlPEA7zG4wdh08IxcNlFrH5MLABhqQ6lC0vUaWjNFnY1myEJ6n4aR2w1PjxYk54Ki2164xWM+KdoAb'
        b'iUjJ8Krw8gEXwMWhQEal8Ci4TBgcC7ZYihMNqrRcdo1XsmITwBu0XHgNVeba/pNyp0GH9mk5uM2IfAQeg03g0sB5PHgWXiZn8pC6cob21d0FmuAajznioZE0jIvoRqqR'
        b'+A8e2LsYp31mD33yIpFjYTW4Ke4/eSiu6j972H/y0BCeFnJfWcjAk5FAoH2kC0ckX2Y6KF3IcySyAjokcCtTg7LkSI2xreXgYIMG3QLXLoGfSuBHI7t0CcbXJuCoG1UH'
        b'J+IwHvYCheWBmUqnxrm18Q98Q3AkjzdW18Y1eCimqmy8VDzRA54j7cOpKG9Z0rykm2/bzXdQWDWaoLe7+N5I1mtDAl/QPf7EDt49ftwtHoawz2qZ0TyjjaHmB3TxQ1X8'
        b'0A4zNYGOaTJpNKFfUuap+X5t5m0Wnfxx+IFxo7EmwMcUNd+3jdnG6uQHYe+nhC47f5Wd/1BSHdEdMZ38SPK8KaUxRc337OL7qfjYI5dPe+TyQ4czGNlhfY+fdCt+xPSi'
        b'Wwldsdmq2Oyu2Lmq2LmdOfPUsUWvk9OeLvfc5rltqAQhXfyJKlQlqJSRqL6aLRTTj9qrcCwTe1KDmv9wAWLJ2URjRbmS0cn3HC0REenm48ArfeNs/ayeULYe1s+DKb5D'
        b'3eKGIrW1+08htpbCPhPKKawvnkE5OjcVNRYplqsdAmsNeiz4D1zHtkxunjxqPRPKozQOKVaXW7DKDfsD88O6+JEqPvYHxihPg32hv0v0mel5I/b03Kyfmw+yp/R6ZKHn'
        b'Foz61di6lD4exbevNXwxVMbLjziSUBl/PBC+ZA1GO3se5/iabqxpWCl4Qg0LeTYQcZfEaOFoYM/ZGi8rHPpMZwDyfDB0wX8h9Fn5T8MF7hfDF+imVpLQZG2wDaz1SkBy'
        b'UTqazTYmoNULrVKgNSsByVM1Ih+hDpUAN+qWwc3BBMwTKNBScBLN5+dhPdKocTB0VjEDrIOnphAIFjQPKqX6sBljnVRRVTFJNMbL7vlpXmlMipExFSle+8F2V9lG7+85'
        b'8q/xPPXQaMOUdn3gZ3pdnL/A0sys7kjqGR/jf615+P3sTm+BJKtZ/+7nVmWWk45M+ibP1jJ/fsCXVc//9sn1P09ctmahZ9/OzyMK65l/fhhqoLSpPAkbshZ5H12ZZOep'
        b'ap52wfuDnyrjntmcVIR9du3bX8bf/dvELsNiicXdhe/MOaqcbXtfseyzLV7dRoxL2xreK9t+8h/yceprudJtZWKOaanpmc1ler+93fnOjX8dmXzywo61fV1/efzFxktm'
        b'ul/zf/v2SKNcuGGrVW611fzPn8jc/9H65XerfihyK9LNbIBm8o21ZvEPv34v8I5/zyQGd0VIy+0IoQkxqehhkJm1cC+pcaSNhTDAGbAmnIb4uDYbNuJFlkgYcEcSRkDc'
        b'ylwJNnjQK/VZq2DyeDPGtkiFCniOaQc3GtFLZSPYGojXcZEPvAhuJJJMBrCNCa/BY7FkFZsNNluiZruwxNs1mDaS6IEWJjgK14MtZKnMBZskYhHYkTYfNXeyD4MyiGTC'
        b'BqBEaznm3Ra0wHb8Cd80b8TAqsljmZ6wI4T+/HpwZC5q+43i4eGy4GGwkbw+YzXYhNhPhNuRdKQzdw5oZ7qEgQ5azqgHW8zBTlsvgkLh7SNkolW8iYW0j1NwDRGg2OBw'
        b'vhiLEb6pHEonXJTBtA6Gl+nF91zkErGmt4JmeFCH0uMxQbNvCam1dC44jpjerqm2aLTcX2byQ03oKj8OziPtZk3UEERKlGW7EeE5DB5L99KgUeoAJbhYykT1e+0/hj/s'
        b'V/7pKUmXYHkNTEnyvMV0CK1/UvTCnORE8az2hdSF7Iuoi1C43rdwV0afndw6+WxKa0qH633RpFvR7yTdTrpTcT8262Mbp07nELVNKAaXQLOzYaPhAWO0qFtY7wurC6sP'
        b'77LwUFl4KK3uW/j12DgpXJUs5Wy1TVhtTPdYr5YFzQtOLGzUb2A3SNAsjd9VZCmDPuD79bEo96AHPOt9iXWJe8QPbO2bQhpDmiIaI5Su9219u/k2TdxGroJ30HgYlR57'
        b'J4Vzi3uze4uoWaSsaMtSO4d1xN63j7qV0W3n0JTQmKDIOpj6nEU5RDM67aMe4c98ah+Ffv4ix4cz3/I2j9PnvK3PibPQ0453XP70D2d+ur7p6MZDoAxGqG1HthZy2nIB'
        b'g8HHgY1fJ1QXiZYkZBObBB2Gg4Tm4A4sVkzyO1VoPhzUQJ9BaSMbvMKZ/pMMEoOxQrpQTkMTPO4vltDsv2iu1KpFXG9rhv+ja/Msrs0Br14nvIzOYRAIg0dstpHpY0PK'
        b'2LKZ1RzTsLS94HbmXYtbiT1j7BReVyyuZHbo3Y15ymIYT8F4GBGRjOcsd6OxTzgkgY1+Pspg9GMbBGNsg1CCbWDr0mPqQ+Mf2AbXiAexDcZhbIMQgm1gYdtjOrab549S'
        b'LAJrYgZTInBKJIMkaV7zw68FaIMk9Kc85iLe+yimcQqjUd5u8Yj86rW23R/bPKbLKUTlFNKhp3KK7nJKUDklqJ2S1HbiXgfn5vFdLuNVLuM7xqpcorpcJqtcJqtdEtUO'
        b'SY9YDHsx4wnF4CczHrEwrec6lQwj76cUvj7RxSl9JOV5CWu8kf3jxQz0/UaX+0YOz5k8I68nSPNxfIR/0a76JOJFO2jPkA/oqBzKqBRssmHCeld4SMhIlbX4yzjyONQe'
        b'Wz+C0rr3U9dHmv5p3toNx5+ulhmc/qD3xrrNS3wj1j/Xc7gms9jTvVUG1sz7IqZvl/FHc3qP2XEnfLri5j8X/zzHquQzy3N9WxXpq/vUBrfXBgjfvEj9pqi6olu1PHSq'
        b'KvHKh/PPfPjj9I+mG11/siM+SpZ2dfnFQPc1BoebxKt0lz45Xd48IejsohvxE7rC/C8cLjW7dPCk2OmZLLZgf+fuwqCW3R9euOu8zfhkhnE48zv/LouMxrd+jMo7u3jH'
        b'sYlFvwVbdP/9lwcG8wPPPp4pvfPuw+RFf15w+kp4z1HjuPccv/1ne2Jt564zRXEhx4oOvR1aCN7666m/rPyJ+UV57a/JuzsUEWn7HYBnZ/Hd99TbzWem3zrGnZe8f1bG'
        b'VwdcU3Q+PVaz3UWaVr9u5YW/xDe0BV6/82AFsEq9Hfvk/UsTekquFoSs7P1506/sfziv+JfuF7fn//n8FCGLAA1HTUULLdLfGKEUWDsf7kAL5GWymlQFjeuPCAnPO2lt'
        b'b1gueIoDecKdllLNTgVaSre8EOIRLaLHha7DRyD3pZf/xXj/N2YIV3pdiyT/Xpgqhk0avdycnOLSPElOzrKBX2TBm4h66r/QghdEGVn2sXX1rHtMzGsDti5pcNqyolGu'
        b'CFDkNY87sEw5Zf/qdte28g6n9sqOKe1V531ux94xhwn3ApI/5ts0BDTkNY47oKdIQopTmzXS/TrDU1XWqZ0ZWZ3ZU1UZ0+5ZT/vYSqAwry/pNHXFkfimM/r0KXNebVSd'
        b'ZU308yAzPdefKHR57uGu5/2cQpefshjheja1U59S6M9PqxiuejYNVk8p9KcvlUHpmz5nlrP1vJ5Tg9dn5IpGrL5pH3nYV6FH8ccqDVTWgTWGz3S4evznVuUsPTuUHV2f'
        b'kWvffF1CLIOQGbw+JldC7BF5+HNfFJ+hl8joMXc8ZtjpHa8WTFabJ3QaJtCL5pYofiyXeotrEWur2cCw72Xm5PybGxb/m/6Chb7coVthI60uZky8uvT3ESyjyqMpWknz'
        b'ZzBM8XYIfcFuaKav44WGBYOTOmHUVYMoDkvGOfsJS34aJRVWvCfdlqgP0vnrPw2/kG16uzl0Ddx8Lfqb6L99dOXChM92/j43vHpf1kz27eIb1dXhHx5LqHcS7wjnbMkK'
        b'j8sGLrZ1se5nPj/1dpPP19/NLc91P/v4+9/3bf+l5+Ta8qoQu+UzfSLu35W+f/Ifyfrjz72/NqZpoWf53bHTTv36/T2PnT2JDI4Ra6u5seWf+rgNuVvGfD09d7ONV2xx'
        b'W9xa+59CH3R/uP0m59KS5ebtK1nHN/nciX0L6RS0kc4Ex12Am9PSsAgr1qUMxojBOSZUguuWRPIHNzNdxWneSHpHebDwbgavseYvA83g0AJipvMD57AnKtgJd2KjE7Z1'
        b'6urCw5SxOcsBXl9FBOloWAdviBNTPOEeeCpFl9JhM7mwBmymbXiXkJAMt/rqUAwBPJxJwaNS0ExmSytY5+mFVBmGI9gqppA6sQPeIGzHgZOgBYfY2IG+iAHGDeAuXyET'
        b'1uINXVo6bwuD5+VaOfQjIxOZoA2cG0NDlF8HDb5isvoRyx+oYVPGcAsrFVyHLUR+d4PXwO6BEC/w5irQBKphK11tG4vgCaLCJmhQbgyt4ZsWTHgBbNEh1TYuKhEgvUBU'
        b'pnmuj/4eBeeZ4MIkNxrhfX2GG8pxzhDULAEbli6qhOcXGS6qZFDWcCcLbOPDLYRO/nLQICbgjrgsFGVQhcqwnwmPJCE2MZ04l0pc+b5itBzswBvT+E4XUTlv68oG6+GW'
        b'aKHHK68I/18uEFpD34MsFZH9/16yWAxxR+UO8ROeiS6/o2ngiQ3Fseg24nUZOaiMHA5WqY081sR3s/U3Ja9N7jRzOhZ6ny36iG2E/vuE7fgp2/1TtvcnbJfnOjNNOWh2'
        b'Hbw+I9e+KgFlyFuTpmVkcuxlFUtLetnYd6mXU1FZViztZRfL5BW9bGw36mWXlqHHLHlFeS8nf2mFVN7Lzi8tLe5lyUoqejmFaOJCf8rxUUccNr2ssqKXVVBU3ssqLZf0'
        b'6hTKiiuk6GZhXlkva5msrJeTJy+QyXpZRdIqlAWR15fJ+/FXenXKKvOLZQW9ujSGjbzXQF4kK6zIkZaXl5b3GpXllculOTJ5KfbG6DWqLCkoypOVSCU50qqCXr2cHLkU'
        b'cZ+T06tDey8MLgdyPAPkvuyfQDDYEOSCQ4PK03Ab/P473pw2YzAkLDwRD732kevrTMt4/bqtqxNlTd22NohyZv3CLcQOSAVFPr2mOTma35rl4Bcbzb2gLK9gQd48qQbn'
        b'J08ilaQKuUSz6tXNyckrLkarH+Ed6169+qg+yyvkS2QVRb06xaUFecXyXsMM7AuxUBqH67I8kqlpfroj0DJL+MJSSWWxNKI8nkm7OpJgsn0sBoPxCBWN3WdMGRit0X3M'
        b'LjZl8PrmOlF6Zl1cWxXXtiHpPte9UxRxeyz0UImSurmmPfpWndaBav2gTnZQD2Vay/+AsiGf+n8PKm6M'
    ))))
