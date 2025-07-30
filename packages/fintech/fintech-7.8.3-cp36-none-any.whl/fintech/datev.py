
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
        b'eJzsvXd8U9f5MH7v1bC8jTHDTDFjech7gAl72JYXmGmGLVtXtrAsGQ2DzcaAtw0Ys2eAMMxeAQKkPSdtkzZN09046bfNt80goUmbpk2ajrzPOUeSJSw7JL/+8f4+nxfh'
        b'K509nuc86zzn3D9wbv8E+JsOf9Yp8NBxhVwZV8jreJ2wnSsURMlqqU5Sx5vH6qSirI6rkFvVywVRrpPV8dt40UcU6nie08kLON8ylc+XG/1mz1g4Z7Gy0qyzG0WlWa+0'
        b'lYvK/BpbudmknGsw2cTScmWVtrRCWyaq/fwWlhuszrw6UW8wiVal3m4qtRnMJqtSa9IpS41aq1W0+tnMylKLqLWJStaATmvTKsV1peVaU5mo1BuMolXtVzrCMaTR8DcS'
        b'/vzJsHTwqOfq+XqhXlIvrZfVy+t96hX1vvV+9f71AfWB9UH1wfUh9QPqQ+sH1ofVD6ofXD+kfmh9eP2w+uH1I/Qj6VQoNo5s4Oq4jaNq5RtG1nEF3IZRdRzPbRq5adRS'
        b'mDQYfrlKklvqPqfD4G8g6YCUzmsBp/LPNSrg98tyCSflyjfwXHF2XfgQzj4BIjei7atxM27My56PG3Brngq3Zi7KR034coyce2aOFL+E6ypUvJ0METVI8AFrZg5uwy05'
        b'uIXn/DIF1DkSXcU7h6sE+1CS5TI6Eq3JjMaX8bFMGSeV8ug4qkMH7KRXK0ZpIQldwcczY3Aj1CHjgnCTJDcsHkoPJ6WbdetRM26KroIutUB5P3RDCBuFbqYF2ceR9CMc'
        b'boAM1wNQw9o1dnxjTcAaO1+IbnNDcLsEteD6GdDVsZDTkCqiZtQeq4mJJL3F7RDavxi1+3DDx0tRXQpqK+UdcyaBv+HOOSsmQGMg474Z0PTDHQDjGwBfNwoAMJ4CTKAA'
        b'4zcJDoCVuQOMND6iF8BGMYD9k/fhAjguJG5i9ajqDfkcjfy7nUCR4+KqN8x+zi+cM/pAIGquLxcCcXGL/yT93kKaLy9IysG3Mk4+aNqSigLO6EfyjRkq/Sy0GCb+nWc+'
        b'FW7HjyjWc0ZfSPiV/aBkD18czE0vTnjb8qugeBb962mfrr82KmK0kP97/j9DZweEcN2cPZYgGT4RBDBqjp0fEYGbYjPwcbw3Bjeh8wsjsnJwe7Q6MyYrh+dMwb7P4gv4'
        b'tsdk+zvHO51Ntufq4MhU6/1dkyn0O5m9sF/WazIDci0kwU5izYlpBQs2rY1ZLHCChMNHteiCHeaNC0d7BhcI3NTx3DhuHLpqsYeSqvB1dLZggcAFVHDl3BzUFWYPg2jc'
        b'gerkuEPCod1oNxfLxZbjJpp/+pTZuIPn0F7UzsVwMfj56fZBJP8lfDKzIGfktPm4VcYJ6/kR49Ed+0RIseEXNxNEj0JbBmkASRuz50eg89EZi/Jh7anxeRnahrp0tO6p'
        b'6JQU3ZDDgjjATeGmFKNDhoXhY2TW45AW++qRlT+JD0JxATu0bxm6t1+blffdAUPD3xy6tPjG9MiCrqCARzP3/eDZNEXJe/nj405cXfblv36UMOzOK6lra3L2nk0eOWr9'
        b'QcN738kqS1V3viNcKi+f77OzPcG0UPj84tyuiJGDTB1RG36/tHrQBxGv/vnWwuWXToWlH/lXUPDh1P/Ubv3HZz+xLbv5j0e6X2h3N7eNLaopX3v64ZVPU5d/ejY1c0jo'
        b'0kmLdnWrZDayvNZlxmtwaxRuzYnJioalHYr3CfiOBNdHaGk63o332aOyYnBDZnaujPNHnWvQNQEf1aAjND0NHZsfpVZlRTkoB2qQB+MtEjO6vNhGVlAMF+RPJs8OK74p'
        b'VuAG4BYZvidBlxaiM6yBF6fjHTDdTfgOuoTbcQuso0k8uqZBL6mEbiFCZSHIqfKnX9/8cZ77cvAUvcVcK5qAL1COowZuIVZP7Q60iCadaCmyiKVmi44go1VJ8HWqgg/l'
        b'FbwffAbDXxB8yHcofIcIYbxFTuomeKySdMtZ4W6foiKL3VRU1O1fVFRqFLUme1VR0bfutIq3EPJhIauGNjeNdC6IdA4rBTkv8HL6tI8h1PeiDZ2MysKtmswY1BQL67wt'
        b'thbfzuK5CeiarChrkGshkn9Sx7e1HB4iYe3A1nV8oQT+pAauUAbfcj1X6KMLrOf0vE6ik273LVTQ3zKdfLui0Jf+9tEp4Lcf46R6ic5X5wdhfwgD3YCwvy4AwgE6nlKD'
        b'oG75AjpRuY/+AzSnVOLoBRmgn5M0xHFOzgzlGZ2RNEiAzkiBzkgonZFSOiPZJHXQme1P0hlJLzojZUR7h4+M0d3Fb47+fMAqzqDY8kPOmgsp2x6rPip+reSD4j26Bu2H'
        b'xbNHt5RdFD+AmB+WXNaW67O1YWXnROlfCoauHrp86+otkQcSZozX+Mza7Z+/85bkXNvuMTvGHNiaGMgtLwv+ZW2XSm4bRcB0FtdHrcano1ycLkrOBaPnJbXoBdxhI2wX'
        b'30RHlT3pEi4gejbaLvHRVdoIy96I747S4OZsYPwqOYdvj1WgJmFdZqAtHBKLw/EBQqI0megSx8nTBHxjYjh6iK/aBkOqzzodas7LjM6UArE8wi8w43tD8QVaEN/Bx9FL'
        b'UTEZmWSxo/qlCnxTQNsjDCrBDf0kTyKl1ImN3YqiIoPJYCsqouslgMx7YQhPPnJeytcGMzCrnbnYOpF1S62iUd8tJXJat0+1aLGCSGchcLH4Mnx3tEtw3BJIHsGuBUAa'
        b'We5aAGdD3BZAr/ZKBTc8d2GW2oFZesGBVwLlXxLAK4HilYTilbBJ4g2vuD7wyh5NVt958Vl/3ArAaAO2i9sLMhjM5ucvIOxsGj6Ht+OT8gHoCDpjGPRugIx2ZmdlwkfF'
        b'BMde0ceGRmmztY+LQ0rL9cYSaVO8GL+We/PDj78bcMTAHflEMcH2lUpKYTcbvxDTgxEKfG0IwYgs3GwjZGBqEtqDbwAVbsft6pgqRm5Xop3csE1StGMgrqNYhfagS6kM'
        b'OdDOKoYf+J4QYCMs1ISuoFOSbE1eDM8J1fwM1I53MgAKXnEBaF2ZaDPYxEoHOhBSxZX48QF8bagLMK4srCopBW+31KStFHtjgGAZ4MIACnwiBpS6gH88yB34Xtr4r1GW'
        b'sqfHgLP4HnroxIErK72jAaDALLTXkB2VLLEmQKkTWTqGAXHCkzjwuFhoSrDH/SbudJw0sep5nrtkUKzqOqCSUCzYDLIIw4IV6BpFBIIFY/AumxJSV8viXUigQ3udeMCQ'
        b'AN1aaxtCEClpEEWBItyZ6UQBK+pw8LS+1z7A29ob3mVPwNvqCW8ZAyYBa7esWmu0e4G6xA3qA12gJwJWuQv0h0K8g97VnPeln8BAT4RZXi/9Nsufd1TpCXxZrp0s5Fn4'
        b'Ad4L2lPmQtwQE6Oen5G1CDfkFTB5MXptBgiPah4kyge+8ip8wR4FRRLxc/hynyQDv1TgQJdV6L4hq7VEZs2DQovfLv+o+ENAGKM+cnCkNkNrBES5mP9hcZW2ofOCeE77'
        b'QfHrJa/pY/dEaLO0s8QL2pBS7tUhWdvrXj54Y+nkLRvm7gzbWSx/fTBXsyKk8M4hEP6IUhyIr+JrRDzDuwa6SWhEPEO38UuMY3RqJjipznzc5sA3fMHXRlW/87WA/0+S'
        b'HXxCzjAOn0StlO744Au8kyeV4t0M52rwNioColv4xljGk9A5fBAYNWVK6HnU5sQQqVdZqQc15fYqItX1MCWjn0OEC+FrAx3IwvK4kyHGb3rw8UnkB3rUw5EoUhI6WelC'
        b'ys5Qd6T0bMdDufIkRVSPdZEivoF/es1U6hUbJbkGfuevpVSeSf14gkabUfYYkOWHJeX6MO058dwbwvXwGwcOha8YWiKWHFgdXnFw+vW3n132WnLLj1tuvZacnRyQ/FpK'
        b'wI6EdwJGtiRPX0l5T/KgYLQhGHgPgd+zHKpz4z3T8EGCBcMiqCSDTqOLqI2CN7LCRVHQBXydspWxsWNwc3Qmbg2aDgqUfJUwLnuVjahgkZNEJsTMkjjEmHDRzzuo+yNL'
        b'IHtbbRYHSSITzdlC+DAgSkCWgnroBMniJHGBXwN23g3ipKd2F8RbPcjQE9WrhFwLUaNVgUROIhwONAK/oiJm04LfAUVFa+xaI0thNFFRCrhSZrbUdCsccpGVyj7dcr1B'
        b'NOqsVPyhbJASRIqAtE9O8tqnJuGaIQuZlAIyBFJYIUh5x0cIUgTIAmQhCjthC/gkPo2O+mcl6IkKAfqDIkAoHrGxFxck/6gU46E+CIVSIvTrfI4IhbK9nE6xWq7zrePr'
        b'eFAl/KgSENgtn2MCYl3zZdhsscRgM4P+FauxiDr28xEZ4yPS6S9DF4uWWnuZtUprt5aWa42iMvERGciXAdmirdYmKudaDFabSqDKxKPvA+D/dhAmR2M22czpuTC5yogZ'
        b'OototcLUmmw1VcpFoPhZTGJ5pWhSpbsFrGViGTxtWpPOazmT1obvW4xqZT6AxgxlF5stpqfJ562yCtFgEpUzTGXaElGV7pGWrrFbakvEWtFQWm6ym8rS5yyKySadgu9F'
        b'BbaYTF2uRZ0+wwSTJaYvBH5njJ1RodWplfMsWh1UJRqthAsaabsma7XZAjXXOtuw2NILbBYtPi6m55utNr22tJz+MIoGW6223JieBzloczDvVviutbsVdwZK1pLeEZVZ'
        b'6egIRKmVhXYrNGx067wyvs+UhHSNaDLVqpUaswXqrjJDbaZaLW1HdLQnKufh+0aboUxZbTb1iisxWNMXikZRD2kzRRAhK0i9EY4olTNNOU8EzMGn9TYrGSWZ0t65lfOy'
        b'VelzYnK0BqN7KotRpWcyPLG5pznjVOlztevcEyCoSi+AxQudFN0TnHGq9JlaU4VzymGOSNBz1khMBcHhmFx7JVQAUdn4NLFRVJBZY9MPkZkzZ+SSNFG06IFEwM+CJZlz'
        b'F8bMMgNsHJNP14LBVA64RupxTHuG1l5liyHtAK0pUTvadPz2mHdv8WTuPQaR0GsQCb0HkeBtEAlsEAk9g0hwH0SCl0Ek9DWIBLfOJvQxiIS+B5HYaxCJvQeR6G0QiWwQ'
        b'iT2DSHQfRKKXQST2NYhEt84m9jGIxL4HkdRrEEm9B5HkbRBJbBBJPYNIch9EkpdBJPU1iCS3zib1MYikvgeR3GsQyb0HkextEMlsEMk9g0h2H0Syl0Ek9zWIZLfOJvcx'
        b'iGSPQfQsRFhPFoOo1zL6OM9ix8f1ZkslEGaNnZA6Ex0DUGMR1CBnoMoCBBmon8laZRFLy6uAXpsgHmixzSLaSA5ILxG1lhKYKAjONhBBQYxh7G6G3UoYSi0IC+lL8Oly'
        b'C8yb1UobIFSP8VejodJgU0Y42K4qvRCmm+QrgURTGck3F582Gg1lwKNsSoNJuVALfNGtQAGFAUnJp7ZU98p6WHhMIfQCCEYEKe6R4CgPSRN6F0jou0CC1wKJypkWuw2S'
        b'e5ej6Ul9V5jktcLkvgsk0wI5WsaX6ZyDVALSCY2zietsrh9AiVw/E92zWl3ZGCBmisCOy9wiJqQXGkwADQJ/2g5JqoUownqBSnsEEzyDQH60VhtwO4tBbyNYo9eWQ/8h'
        b'k0mnhc6YSgBtXRC3WfDpMkCiTJPOUK1WzmX8wz2U4BFK9AgleYSSPUIpHqFUj1CaR2iSZ+txnkHP3sR7difesz/xnh2KT/YipigjFjhm1eoQNFQ9gpG3RIes5C3JKT71'
        b'leYiZV7S87y3RuQub/EeoljfY+gnvS/p7JtkTui7ZQ857WmyAan0ls2DBaT0YgEpvVlAijcWkMJYQEoPNU5xZwEpXlhASl8sIMWN1Kf0wQJS+uZjqb0Gkdp7EKneBpHK'
        b'BpHaM4hU90GkehlEal+DSHXrbGofg0jtexBpvQaR1nsQad4GkcYGkdYziDT3QaR5GURaX4NIc+tsWh+DSOt7EJN6DWJS70FM8jaISWwQk3oGMcl9EJO8DGJSX4OY5NbZ'
        b'SX0MYlLfgwAC2UtXiPOiLMR51RbiHOpCnJuYEuehMMR50xji+lQZ4tx1g7i+lIY4j/E4ujjXIlbqrDVAZSqBblvNxmqQJNIL5uTPiKHcyma1iHpggibC87xGJ3iPTvQe'
        b'neQ9Otl7dIr36FTv0Wneoyf1MZw4QtArTPh+ld4mWpV5+XkFDgGOMHNrlQj6MBMme5i5W6yTfbtFzRNL8H3C6Z8QG8pYvENqcIYSPEKJ6fkO04pb4V5Gl/jeUQm9o0DN'
        b'MRKlWGsjcqmywA7VaStFYKNam91KxFo2GmWl1mQH9qIsExmaAjv0ZgZQuRUxEOZu0NFiX5vZS/1emJL3untnpCamntlRgvCtdIi8dCr1JN0xyex3gttvohP2WKq+5NNz'
        b'VYKFmNwtSmZWJlt2FuISpVJYyJ6thVjgLMTUyvZCiOndQoyr3TJrldFgswx3mfz4J817xM9io9NCSc17EoFXCIIgjaf+W3j/dHTOilvxIVsUboxG56WcIkXYhF9CHf8l'
        b'4952VWC334zSUrPdZAOFojtoJmABU0S0VaLxEbFXPiIuDV8Omw1YUQmiBjGbKpkiBDhtAEr0iNhiu6VEIPIw7d2H+EWVTMwxl5tEZYHZaIzNADplitHUEqtLT7CH8qUv'
        b'0RQqWTFiXSM01Wqw2lkESXMPs5U4jxgDmdTPGpq5KKagtNyI7wNGGEFScQ+mzxSNYpmOjIb9dJhien4nOLSmdOdkUC2AiImiY8E7VTklE5UcCmGP6cqhClIBniiBkBmW'
        b'nI0qC44aaHNGA2SgvwwmvVkZo5xhsTm74ojJNJGST0SSbAnesiX0ypboLVtir2xJ3rIl9cqW7C1bcq9sKd6ypfTKluotW2qvbGnesoHkkVewMB4iNAwwRAIWaWRCr0gI'
        b'KHNEoKJO+6zSrlb22GchkiG002CqVhIp3qmLM0NsDxiV2VHZ6XPtpgrq3ypayoBs1RJSQ+JnLlImTWLMV+/MQgzF3uIdeMOSvFSYXkiVBDJwS6WWJLpQxFuKC1X6KpbQ'
        b'XzHviQyF+inmPZGhVD/FvCcyFOunmPdEhnL9FPOeyFCwn2LeExlK9lPMeyIpNqm/Yt4TKbjj+oW391RasH9E6RtT4vtFlT5SacF+kaWPVFqwX3TpI5UW7Bdh+kilBftF'
        b'mT5SacF+kaaPVFqwX7TpI5UW7Bdx+kilK75fzIHUAhu+X1oBrGstMF8bFVfXigarmD4X+HwP9QNyqDUZtcTiaF2tLbdArWUi5DCJRFTqMUE6OCcheDPsemIscxE5Jy+F'
        b'JEJ5exiyMmKGqZaJyWSXD4hxjsEGrFHUgRCitT2R/AQd7l24h5I/mWYx4ttWh5jgkZJB93z0NpBKXMoW5SQxVOjxqhk4Rurg5sD6gdMQwVpPRepKwuBtogGmxeayHmeC'
        b'/Gsz6A0VWnfqX0iVQ5dV2V3MYCql2+6iu5g0V2T6hmgoIUnZADWyXWZlkk3f0pq7xRj6DS1rjfbKCrHcad6mTJAwSQtxqibyL/F+sUQz+TeG/FY/hfxreYY8+pF+I+Bx'
        b'36v0G24npz4W4UOozpo9bkouboslrs6NuEXjww0qkQaY4jzk34FO+Xc17yn/7pXv9d/rr0vaO3DvQF2yLkUX0uqjS62X1QfWD9RLdAN1YdtBGi6UijLdIN3g7ZxuiG5o'
        b'q1Aoh3A4DQ+jYR8ID6fhETSsgPBIGh5Fw74QHk3DShr2g/AYGh5Lw/4QHkfD42k4gPRAL+gm6CZuVxQG0l4OfOLjq3um1U+XVi84eivVRehUtLdBbFR7/fbyegFy+tCn'
        b's1Rkq69uEvWZk9EDFiFQ1kcXpYumZYN1kyFNVq+gxy9CaVqMTr3dtzAEYgdAn2J1cdCnAdDGQF18q/M0QVB9sF6mS9AlbldALaG6UNAd9Kr0bsVs4pI9q2Dxl7F+Srd/'
        b'zmglozrs/I9HDqZUEW3qEfXLJjj2iHh29CgQj4gjziPiHfKIog5BvUfEJeIR8dV4RPwrVD7dflpdNRAsS5FB1+1bCmTDZCM/g7RMqykygtxnK+9WlNphRZlKa7oVxOPU'
        b'oDU63DX89QYQ9YoqYTWXd0vmLFqQW6pw4JMf5+YANJV74vyRb7283q/eR+/ncAdSNCjquI2+tfINCuoO5EvdgRSbfJdyOgmdL+nfOmAgHtNA/mWy/hhqRSs9Z+WaPAP1'
        b'cCgV1b2K9IqYDCqHtlLZMxeTHSesgKwQu5DjCJdjUrQmW68ayL+ImUANbE5apFIrZ5DyQDdKldQDUGmvUgL1TFXqDGUGm7V3vxzdcIHBey9YsvceuHY/vqYPyV/XB0/4'
        b'T1Zm02/ShXmx2c5UR8es3vtCeA2h8sAj1MqF5UD3AZ1FpdVeYhR1ZTCep6qFuZYwBRVqUmqhCgiz/iuNZuBBFrUy06astIOaUiJ6rUXrGHyJaFsrkt1fZYRO1GvtRpuK'
        b'HrBL6xsWDryfrJzl+KUsJebDCNemo5vZUdVXLc41M9mJrVYXMMl5PrNFGcFcWCrwfUstKN19VeTwlZpMNSwijUA1DEccpCJCLFMrk+PjopWp8XF9VuO2aCcr55KAkgZI'
        b'dXqDCVYN9FFZI2qhY5EmcS3ZAa1OUSep4yNVvafqaxyGA9hRBDExhFNOH+vDVRVnKwfXcHZyugO/gB+uxs056GI+bsjErZpY3JhPXEkzslW4OTo3BjXh9uz5GehShhV3'
        b'5ObkZObwHN6NTgSY0X50mlZ8MSyQG5q/W+Dyi6MjS+Sc/VmIVFpX4MYKrzXjNtyYDRwRNTqrdta7vSaAQ524gVY7N9KXCxnxMs8VFxv36CZw9JAUuo+aLfSUlGbzenZI'
        b'KkMdE0mOoaDLUi5lhdyqRcfoES9aSUOGDxcQIZNzyuLoCvky1je8UxjvrWe4AWpsjia9a8HX0B7VYrfOobsWf3R9cbDhF/+TKbWug2refLlg5Gtv+W6JC9jxzvMv3Ly3'
        b's+PONoniZz6XYsfmFs9JuP2D/DTpw+NZg4+1huwbnxW6et2O6s1B+2Nu/zSn5GTuLy9M/kDxtwuXv9TnS8NWSKY8/njF7+c/O6LinWG3tJVDc9Do2EMXf2zOnJJi/uq3'
        b'j/7+veyJ00ZXtp/ao1L7blYF0CNOqMOMD6DmWE0MujnddZojeIJEn5dDnbIz8FF0FzUnTs1zhyXPDcN10lpct8lGxBR0ujzeX4NbVAvwjhynL+4gVC9V4IbBtBq8NxN3'
        b'oOY8AjbcFuSCHM8NHiP154fTsx/o2jD0QlRMRMYMeYzAydEhIQYdzKRnUuJz8EuoGTXW5LkBKhRdluDmULSVls4eim5FqVW4iR8HcpocXRQSN+IrzNP3HG7Cz8Ew8S1y'
        b'SssJHpWcC62WoAf4KrplU5F8XXgnPgbdzM7F+6YxkYt00wFfjovDO+TqJeiUjVg/8cnwSjKk5uja9ZFqkg+34vYokk9plQWirs206xmKQuj5JXQwjwpwpOkYaBjtl+Ad'
        b'Y0JYTTei0C7UPHEwadhd0BuG7khRMz4yjcmPft/iTFaPsEmEBepnOp4s8c3cBjkv50N4heNJTosp6IkxhUBS5HztACcbdp1RyXV2hPqYEnnAQiiAZTp5zCCPmZzzAMws'
        b'rn9HVQUr1VPJDFcpWomXozSPSPeJryW3hTs4yt2btXdXXT7MvOOPepGS/mzgVjNPeT5XxXf7F/VIDE7nWanHzHUrphi1lSU67dQBUI+V1OnWnjPtSwcNd9Tm5PcRwBt0'
        b'MWaTsUYFjUl05tKv7ZiedcyvyCVDeO+XZR48wpxd+nI0a58V8tL817ZbxtoNLvKUG/ppfIircVW/ssU36oYDLr5FTrbdTweGuToQPlNrFV2c/tuM27fIyeH7aXCkq8Fx'
        b'fUoB36BpB6gVRQ6ZoJ+WlT0t9yk3fIOWy1nLAUVuYkQ/rY/rgfTXiBpe+uBxioAeaBPqOdeBtq87Q6D/+uNMklyD+G6LhJ6BfVz7HjudVK5/zP205cdv/bXlfwPoqYCp'
        b'J6VvDv+rSqAcSUC3Igj1dtJkH7zLRZZxPXpgo5JCBzqCHzKG4EGXcTs6RWkzasP3+jtn5lNEVpH7maPN8HmmNsSNXtEMfbj3C3149i+Gx0QCE+JYD9RwC/e2x/myXvWr'
        b'/Lp9HKuSOe/LrTaLKNq6FVVmq42Iw93SUoOtptuH5anplldrqRrpXwpCubmSqZcSm7asW2YGfLeU+jvgQXoV5ITJXAJef5eWGOg6iR/ELj3QBznA7t8QAGAPALD7U7AH'
        b'ULD7bwpw6IrbQVf8rcyLrjhDp7OCMkAkWp1YQlYc/C91OL8pReqm/xTqIlVmqCaiVZbby0Q3BQ1mxGoABUfJjjEQXcsq2tTKPMDqXvWQpV9JdlcMlVVmC9ErncVKtSZQ'
        b'VkhRUHQsYqnNWKMsqSEFelWirdYajFrSJJXtieukVU1GaiB2Mlhbjiod+hGps1cdULXdajCV0R65qlFGUmBFPsWMzHWMtpxYK3r3vVf+CJvWUgZt6JxUiJRXEsuflega'
        b'1jV2MrslFm1phWizqiY/vQrP8HSycoYHG1Eup3udK/sqRlqerKTHF5Z/7SGGPmthy2KysoB+K5c7XOr6zO9cPpOVxG4JoKKq5XJ3l7o+y5IFB0opPJXL8yy2vvOxJQlZ'
        b'2Q/aRrQysyAvJjE+JUW5nNgq+yzN1jGomzMWxmTOVi53bACujFrufkSj78Z7lj9RoFlASSpydwzuszgQDJjMclgasFytpRZDlc3BuwieklPVdG3NMFrNgL+izqvuD+hE'
        b'chNeY6R35FBgq5WzmQGALtGxBTZtZSU5vmYa26cpgC4GQCzoQJVjaekM9JYeLUzrWgPwNHEdQNyx4HrXQ/7lmm0iWyZ08Yu2crMOKEmZHbR/0hdtBSxAWDQizE6pqDQD'
        b'c/daDxsSWTTUsmFlwzRY3bqkVs4FouYkSF5rcV92xA4CqE7uICo1woDZ9UNW0XvJYscNROZS2nO2NTKl3Garsk6OjV27di27bkKtE2N1JqO4zlwZy6TLWG1VVawBgL9O'
        b'XW6rNI6LdVYRGx8Xl5iQEB87Oz4tLj4pKS4pLTEpPi45NXHS1OKifqwO3i9ACM21E16N74UK1mxVVow6l5zFi0Lnozl0EJ/kxhfIypfiZjthaHgb2oJvJoK0U8PFc/GT'
        b'ZlHdfZqR3J1QpQyYXhxwJHcBZ59M2PoudAl3apxMfT5uIJeIZMUsIKdYF0SQE6FLQI9vRPvxNdwO/B7tQVd8cefU5fTSIflacuoTVNn2qInoJG704WT4oBCwFB+m9x+V'
        b'++I6fENNLrUgJ2Wj0Iup8N2aAzrtaHRGiu/hHegitSFYrFJ8A/TmnEV4V5Xn+PJxQy6UatEsqoJHXnZWWjbulHK4CW3zx6fRNnSFnntbMCjPX63KQvfRcT8O3VntmyXg'
        b'47HL6MVJeH8c1HAjE8rzXPU6CdrPwwztSaD3Hg1C+9BNf9wQq8aN0GQ0ah6IzmeBbtzAc8p5MinabmVXzVzEV1fgG7GRPCdk8Mvw6ZQYtI3OrHmFnAvgFEs5ZXHAuZgK'
        b'jk6NCl3SWQNxJ74FzeJTUdCyYoUwDzVr6H0feJ8/OkfSAwPVeDe+tWhBNr4WhfdIuCE1EnTRrKK7HuZAfBQ1hPurSR2tOZlkTiTcIHxXGmxbY3ij8JHMegiyHfrluJjX'
        b'nyWX1MiK06dV/nzi1a331oRMvPydQdFbfyab0/Knmdv/WBC3Jn/V+L3vdFw6OyXKcGVMQfLwS+OndLyRsLfjQMrRzAdtPxwUrBq8/vT3On/084aCqdJ/5787JGrco922'
        b'q3UjH78j9SnXbpGM0P6zZtv5DUm+mRsO37Wfvd0R8dnxtQf+8Ieof16yv/V48cN3Xn+85LOEj+8vuPMVN/V65I38DsdFGujwM3g3Na64LCtBeC8xrqDT+DYVMCej+vEu'
        b'PPQwNaDzhqhEGciZ29ERVlu7fya+jbdSQ4unlWUUiKt0eq/g+4CqzR6WhmD80CHV7simNp8Z6DTas6kkKjcmMzNHE41bVTw3GN+XJuA9z9IDs/gUapisiY7IgL7wUOl6'
        b'BeoSamYmewijQd/yfpi+z8L6aXW6Iia+UWl5olNaziDHYRX8YPp0/0jp5R0KvnagS9rtqcNhqghkQvMSzrk7t5Q8lpFHIXmQ2zksK8hjJXmsIo8iTxnc+6lef1ZnTyUr'
        b'XU0UuZoIdLW4ytUOld+1VKB3l9/fnOguv3sbkcq3O0BH3Pgc8lF3IJN6nUG5tpJ+k6tKxG5fxzZtqdjtT2QUkAyJExfrg2uYpX4OAkzMKyFOApxFhHg/DzE+CAT5YIco'
        b'H0JEeX2IQ5D3o4K8PwjyflSQ96eCvN8mfzdBvt2nf0Fe6/K/U7JbiZ5CXJ1DDjOw3ErgmTBPIImCHKB1v1iPyArRyjKL2V4FqSAia3vzIHNlicGkdUolkSCwRFJ2yrgp'
        b'0exd3pukgy6Ft1dNRAH+f5rH/581D/flNZkAisW47Flfo4F4rEdWnkU5K/Aqhi3/GufNPptj652141jijjgmyZrMxE5jobKqybsEutZMREVDpdbYh6y7vB/3VdAgvDuw'
        b'9tljQplYf0vM5grSXxKjVuY4sEtLw0pzyWoAPOj13jcCTUTzSUuJi3cYvggigNpGqlve49raZydchHGycpHVrjUa6coAxKk2G0pdq3G5m2dsv8qfg7B6goEepFvu7j37'
        b'teoZKf6Eiubho/l/gYY1U1wrljk8bP6flvV/gZaVmBKXkJYWl5iYlJicmJKSHO9VyyL/+la9iDzS+1oWJdvwVSyX5sYRwWB6sXFC8hrOTi4lwqc3zdZk5uCm6EyXDsVU'
        b'p3kBLuWJKk6b0QPfJPQ8u4sVH7WiffhGvJWqTi69CZ9D2+zJkB6rT9Oos3JAcnVWi/YmO2v2rBc142ZfdBZd8rGTXSO8pwidtObl5DmuJiK1L8G7IHs7bkA3RdCi/EDp'
        b'gEoh6m7BCnQEHUKnfMmG3z7/3Bx0lF5GK43Ap61ZuDUzJ09D7jSKW75Byg2dKcEtE1bbia8OSOMvKayRObgtgojp6kx0KYLnRi8cXyaTob3hNI/Vz+qPX0BtAupcoMCt'
        b'MbnR6LzAhSZKQFO8gdrtxOVrLurED0GD3I1ukE1oxxY0uULo1gJyUWc8apatC0YH7UTuXyFFO0mvbCOgX5nRKnLlZxg+JcEvom24iwLpi+mSEeES8qs44KYtmF1MCqm3'
        b'N/vLOW4hhx+uWAhC/yl7EhlECz6t8ieTBHO5G7+QkQ2V4w58i+ibzagLQtm4LYOoXCvCFeGL5y2HgrTCy2gLqsc34Gcmh25qMhWT6U2n04y4CdRuULoL8ZH4RQPYlabb'
        b'/NFdcqUpF8vhLfhKLKqPp329tUyeVsiDmqEsjv7VuhjOPhsiffE2fJ3MQ6tDH8+InoIaFpPrg2OzFgHsM3BLQYQKMCDDdVewCt2mkyU3Ba5EHWi3nd749BCdQccKcGdi'
        b'loTj8UUOHwnDF1Gnnu3Zd0zH+/0dQFngxA/NuLBFCi/zgS7jPVIO1S/yXQb69UM78b3CZ1ALvmKNS3TquJr5EbizQMHUWacyO22QPAidG0dtF74GvNeaFZOXE0tQJteh'
        b'zKrwAVnuNHQz0I9iXj7eic9EJeGz9AbMLJWc80cvCYAhdfgAvTW3ISpXeHlsSDBXpR341tJLsceY5wXakYKfwzcc1gvmGAHIhBtj83KgYw34uqNCdycEUK7PBuBdA/E+'
        b'dr/yUXQ8LApfw/fUmdGg5stRuxD7DN5KYZ6Dr0/VUDVQwM1TLHxaRJpKQgE8LuvZKLRD5VZmbhBNGLMJ73MUQUdioAi+nMJgU58YErVg7JND3FNt/OKrr76qyZetWiyh'
        b'hCZgK1fMGRJTWiXWKaAiXRh+cOWuZ3Px9JAdZdU/qD6y+T97hqJB51QLqnyGBcUJr+4LSTj/xj2tSt449rnnT7ynWHikuen93wz68ev3U4//z+uXdwcaVyywBS7TD9SM'
        b'nbcT/1Bz4fTD30y27/v1qeiITxOXh2b8+/lx/572qfz0gU8ygxP4STNz5tefC//wjvEZie18Y85zXb+LTm38V+TE9uOvvLI78LfvKz4YU372VNOH5pGz8lJs094w/Hpr'
        b'9W7NT5f9cad91J2sj4p+JOxvfH3cRzVbxz/7nZ0vZUwL2PhpSvKvxlkvNbVcLNX9uHrFlUq5XZgg/irtyJ+C3x2krQ4/8mnT73PX/qvqTPM+349/lTp1XT6OlP3tl9Xf'
        b'HfILxd9DVn6cunSRrz7vrd2D//2j2Xn+3e8/XOv3SeHjFxO/EL46W3DUbJl37z9/Drz/8c5A+6MJmyYkdPws+d3YzXNXr8ExE1SBzEHjMlkEnqaI4AkSfDxAH2e3ES9V'
        b'dEaKbnm3RBAzxE0N0L6H+Aq1RJhwF36emCHwDtUTlgh0VsP8Sg7i1nkaN1+N4MUSvC/ciPfjA+zerUZ0PTcqUg3V7lEBI4GFskxAZ6aiI/Tmtjl4y8Ao3IGuqgnJjyYY'
        b'1ibEZOAj9Fau2SX4iCY7Ug5I2blkJZ9KtumoDwg+OHYh6srOiRY4qYbPBQJ7Hd1S0xrRFtw5ATfnK1xOGvINwjMj8C4bcYfAXcPRTebM8aQrR/Uk4syxBTdQE0vqJHzz'
        b'yf3ACfii01UjZxSz1eyxDbCSFRdD+BZM9zKNhBuAd0nQ1Wp8mhpZpvkBCY2OkBYzKws1sRDzXD+3YqlC/ks2F2/WlyBiZ+hRw6kFZqHTArOZEwIc9pceKwy5oY7ZYGhI'
        b'IM4joyA1jJdTFxLiThIKYXL9sEIIog4mfgIJ1w7xsG70tOqw2QQwu0kJeRAxxUIuvreI5KEnjzKXLcWbucbnaW4p9mN1lroqLnHVVOZqJ9DVRI/hxgCPQg/DzblId8NN'
        b'X0MrlTnELXKU0PO+clm9Tz1Hd0f5ej9qbvGvl7ruK5c1yOu4jfJa+QYZNa/IqXlFtknu7b5yUvnoXrJcEJPlOjfCslB8CKAtjrYumMSxW93LTDJOkbFKBoQ32rrYzFEi'
        b'jhoHop18oBW1KtZIOEkQn5aTy3znbuMWsQC1LsStafjBopz5+FY+vrUoMCUujuNGDpGgrfg4OkTFvSLUWlWAWxcmo50FcbgpKU7KKdbw+MR09BKzTz9flsRqWgRcSRZZ'
        b'iW/w6JByIO3A5DD0HLmdnEPn0MMp3BTUhh8wKeTQuiJ8Cp/h0D0YyERuaE4mY2N1qHGSRh2XlJAscPJNkOUKj47NT6b8VY/vA2t2uwn8moCu4JvACdtnG54r/QFnJZ5F'
        b'uhlhc/JezJ0VH3DrD4ffnncyJnSmclHJu7MOLA0/cG/ZpbDxIUeHPlYFjPpHy6aZ07Y0Nu7+yXcfPRh03XLEuuFx2s5wv4ilpbv/Ig/I+s1vl+2f/9P46++V//7EZ9fD'
        b'zjWVLpqeue3WwWPaz5Wv2AKb3r6TkPPqmh8afnhp9+fVI/wH64bifz84/t2GjuKjL/guyf+wcuJn91I/DZxsqmj/a91fq/435c5Hr/0yduIPzJfbjo/7T+27//rs+5uN'
        b'pltvbpvbWGPKPDRZdjLh409Luq2TLnwS1fz51Ye/sNk+3zP33wN/tzjvOxtXNXw1vujP37kROurkV19IbGm5TfW3VaHsQt2H6DpMArlz3weY9XP4cgK/CN+bRBMj0B4Q'
        b'Ga8CFFz0FHKf9KW3sMbOGQnFHCRyQRAlpUNxPXVmSwTJ6bZ3UmpNqZEFrlExDnF2NYCWcCR8R+fheRgeR2/WjDHiZk1udOYQfDoHt8eiC1IuCD2UFKnwJdb7O/Gaiegl'
        b'yEQvb5eO4qGve/FtWjuA/8VczwuqJc+iWz5oF9rCmm/Az48ll7/PtTuvf2d3vzeiZuofAuL65QmabHwAX/dwfByMLkmH464oZnCvw+fxYY2HMypfjDq40NUSdLEEHWRe'
        b'JA+06IEnb/XF193Za3sp6qSDDjaVE8dUaNAscfooBo+SrEIXBtD00bgLnSZ81Qc9dGOtRrzNj914uj0AHXeZ7hVEvwFcrwkfR5mufBn0CJ+gN9b33FYPQL7MbvXeNafQ'
        b'7aJMGPBV3CKsQ8en0rprC/BVItjhtrxMIBkwlScSBbMctz8dxf22F8p7ONOwa+8pc9L1MKdYwnqozyL1XJQSxiQI8M0YVQDQZfaRUnbFtg1IiPk5Klzpzo9ckApBwmDB'
        b'D5iZuysNa54xKZ8e9tDtw8zQ1m6Z1aa12LolkO+bciSZhdzNaqlwMR6ji/tQxrMaHpd4x0WYlPFs4X6p7MPnh3X0v+CA5TDgf/luL/sBOzdlcx7YcNhhjQ7ziEW02S0m'
        b'mlap1BIzv5u15alM5MoKscYK9VRZRCtxaGRmHIddyuqyzTtsOt5M20+a7Y3MGEa6U1JjE72YnVx8VO74e9IJ3h4Jv81D0APUDCurHajFNbwHXV8CcuY11DUfNciA8tzg'
        b'hqItkvXLcCdlZcvRPVBzOmQc2i3h1Jwa3ccv0t1QFW5BDyiLRc1LYnArqJb7NGq1hAtDjRJ0fgjjz7FyIL7cLp8Arjh7R2wiZyfyalYpPkFL4oM8KSwfiztL0AN8Gj+X'
        b'wEUmy9LQsYlU6bJAN/dHMS0N78EXqaaGj6DzdLt27vIAoHNX3LkwsGB0Dt+lvLYKncH3HbrcwhGgyi3daCditgrdGFlACqzHu4ia18qPQHemGUbssAnWHZCe0vhZTsvJ'
        b'oLrpIbPL1n6StWZRzheNm/jrwwq2nvx4mWnWz632hpV2+fdS184KufPqa/c/31H6aElkxMK/vPzP+Gsdf21CWT+cu2jFwuyPqxqPDw1fknLgsy9+Oze64OajE/UnOso0'
        b'hyanGaauj/7ozKxXuxc2bfitdblh6t33l6ZMfowV2P9P7wdnZ4x/M1aqkjMSXY/3jvTYEgUR5pbT009EF9g1zkfxcfyAXfUbI+fQXXyQXPYL47/JmE0XPghEX50jwHDr'
        b'cT06x2tIfsZstoEmTLzL96GX2LssBM5fFPCJFeg87UNoCKCKS2lALyR7+nevL6Tk1wJKU537+0hy5lCWtFitkn8N7ejD91BrLSKrruf1IIxcGqWSMCqdh8E3IX5kfzUU'
        b'yJ0bBXEUzf2GbolmePzxCSJ1rA/HREcTKr5bWqW1lXu/Az2Fc9w5TXYeyWsQ5K570KV93oPuOGr2joT3suvYQ7cICbFqq8kvo9Gdgj39YTPS8cnKTL0ykvyKVALZtTL7'
        b'NqFN4jpyjpWYeyPVtYaqyGjakINIWrxbi63kBj+dy0attZSWG6pFtTKPmNTXGqyiixDSOugAaHatUm82AtHvh6p5vFjARdUUuXZy+AHfTcFnojJgieRngNyRlZONzi/M'
        b'QJfwvc24IRpwkMvAO32qkqvZmwP2rUHXNLCisnLUuBGks4WgqDfHzs/Iwp2whCLIRS0afNsH7ZuYSEkNPi4D+vbCUFDqu6i+LzHyaBs6jffStxGhF0V8agLaEwUazDpu'
        b'HT4zjtLOVHwGn8TnQ6PyBI5fwOFD6LDd8B2/X0usVyH1k+q3n22lHiA7jh8Ni9hc8gGfNiv4Oy/LuMYEruD5gAzZzqDG7XGzUlL0bVl7sozH//34E5moVZWfrLCXzZqZ'
        b'52c4++nltovrm1Tv37y64zvjytNDfnNyfvzG7R/ETZ6+96zpUfG8bcm5v9z97Pp3X9nXdjR04s335WtG+Sv2b/z40Omdbz3zadKAk8v/HWg3K47Els1IH5yy48/r37n1'
        b'8+pRnbMv/eXU1u/Kl494Y9PAT/Ifblp7KHn42TdUwfTu8ICRayajTjrVgO2pPLqMGvSUDPGj8XFftIXIm47XlSlws7ARXwFCQuw4eB9uLAJmcnMtNbrgnaMEzhedFdAp'
        b'3BTBzBxXsvAdWr4xGsTwl0AXyhVG4PsBzA70vC2GvJotWp0JjzXoIRAqfFXA99EJ/DyTuvFdfEkTjdryyPX/+C7Pc/7TBXxgGWpiZ3RacJuBVBGbFxPPEU1LiJwyhpl0'
        b'tg+NHIVvEX6hUuN2OrrgOEnZ3HQmfOKdRPSkFBY3ot3sOnWQQztY1xrx/exV+GpULNlWiFGrBBDIj0uAsB7AVxkNPrcBdVFZOzYXb0f1Mk4+RRjCq5jgezlSi9uTNICv'
        b'DFl9wwR0ciW+SNsm75e5RDQWOi0XAqHfM4WhuA29yHr+QGHAe9GRJwXjm8+wMe/PzWLdWrcCGkXnhOgBaHt/hpqvodduNFpK1q+nuwv5+DJTi4KeyAHiDPIqM52EQmxt'
        b'oIuGktK5Hm8FqPIk1P10UmB5e4i3BR5fPUG86wZ7vCXAo2Go3HWC2UK2Ftgp+WRWOaHcllSOmnPSyO9J5EHc7/osxU7Wp5MHeYOj5Vk2ApqdbBPkskpJbUC1HP9UMvYl'
        b'wN/AJ87jE/d7nbm0qIieHupWVFnMVaLFVvM0J5eIhz1106EmHyp+U/ZGp4lNedh/3R7XL7JYyN7bHziHf45CKhWICY7jw8YLDi3ma59CkCQAMIrjB6sD+DBhRP6w1KDh'
        b'1H4yAL+gk5VYM2HtWYOCJFzgSAGfnIsPUUl1NYiWD/zRORuhSv6ZOXjPctyWT3ZfRiRIx6HOjf+ldxc9xVEPn1wqmk4BUrgnAp0lx1rGcGNAULtkZ2s1L1CjRlfj5i4G'
        b'jJLi2/wa3DyBcqBhswc5TUAgtd9jZiB8FB2ex94UWRe/HjdnRhPhK1EK+m2zgG/iF7Nw4xxD8KS3ZFaCgfnzjpEXbpVvmK7/QJetfa3kMYRW68v1j6XXDhQcWHDg8MHv'
        b'GPeFDb4aMWt3jk+p3yyfWVEd4yUZEw9sTZRwI74XfOdEhkrGyNlp4Jf0wCI+EuQ8sYi3j6UGFmNNJXQb7/KgR+HzGYk/hK4sj6KGcVyf4LSNL8UtjJYdkaOTHmq6gG6P'
        b'MKNGkdKyQQMmkp1blrZSQEc2iBp8t78TLAGggIGwIxYRJwZKqQa7U6rxxLRLKJMUnha7a21Iu6WkQLecHSLz9rqktSSq2oXdpOwYwVn/FsfnHXfpke6ooXp0yi8qIism'
        b'IzoLtdrQqVi2D6vE+2Rh+ajeA4EGOb6tn7rfixFH7oYArBR0ku2+hRJRqpPqZNs5nVzn0yoUyiCsoGFfGpZD2I+G/WnYB8IBNBxIwwoIB9FwMA37QjiEhgfQsB+05gOt'
        b'heoGkvfM6RJgRfD0tg3fwgBH2hDdUHIPhi6Rpg3TDYe0IF0SpMrpqRmpboRuJMQF65IhTgolRuuU5M6KvX57hb0SvWSvdK+MfHThegHiyLfE9c1i2VPKcrg9pU/+1o05'
        b'Egx1+fXU82QZXUrvuG/31EUcGahTHREKB4ih4gBdZDi3emAdV8fTUJQzRHOEUWdEdp5IAXPio4vWxcCsDaJuij50nmQ6tS4W4gbrwqnlIrXbtwiYlnYuCMzUbuRhh/dU'
        b'M5izo5y+BVDusr7L+rW+PwXF8mPWd9NE4om+K8hnerFxsyyCHS3/ZFQLN5TPjxbyi4M+GZzJIh+YNvBfCG9M8o/Trh8VYeHs5MU7vvhwCjuz7nAXINokEdxc21BAKZp9'
        b'uIIyRQg6i87Tmq4HjeOAbNn8uOKSInMq976zl38lD0PT2UOClfQ+edTJkS3XArfEBUh/1zarWHr7xGujAqaXztitjuMH7HlzWP17HxfVPtj9qtx/8PK8P/q2rhq61+/1'
        b'7/14zurq+tDVD5ee+WmOvMindMf369//n9npf/jJDJ+wuLKf2T779fxrJd3Tzh0NX/r6GZUv8y0+h7dMBl04F3UQViPhFAsFG+qKoFTPhC8ny4gFFl2hNmf5M8IA1F5O'
        b'lezNmk3uns+o0bnlmIg7qZV1Kj6Ozjy5NYfbMxGdlgnhsnIQ8M7Q7bk1+EEUaiaUNSoihuVrnjbdhxsyQjol8Vn6eqn5Ixc5XjXXSi3YQINN6MQAfFiCTiaBLEzyRMzH'
        b'13oy5aCLMLzm1AG4U4JOVaEuJrE3LgGNvzkWX0e3QHDNJO84VuAm8oqo9hAbYZD4Cj6Oz6HmtVAP5a+Z+BhuQa2oPQ+of2MeblPLuUkaOdqHulA7I65PLV/2HPoe5U60'
        b'E+S8n0zBD6WHvx2mU7421LVSnngHIjN1dsuon1K3lLi5dgf0bG2ZzN2+BlOV3UZv2PJuJJBZyC2flvXksYlzip0bPPoZ24v4/9xD+vTSv6c9YCsrIp3u53zrDMF5stut'
        b'FdfR7hE994P2OuWqhlozCWF5ymPGgUXuM9dPl2Y7u/TlKLfme5/rVj9ty35FLij10+w8V7MjM53Znd6V36hVvfNYNUGbokpDf4ebs1yNDiYqhlJvMVf+f2pNu66f1nJc'
        b'rYXR1ojf7bdoS15kM9u0xn4aync1FL6QZHV653pt7dsb6b2+9FHger/3jzIFlO543ffggnRptIrxnJeXO14MXn3B8uWiPM6QVPw5byV2ocEpfkTkzdDu1UW8p9EG6D8o'
        b'/oD79HB4wVsFB14O3xaetpwr/rnc58L/qHh6iYYBHwl1p2YuSjY7y42WrceN/QidVPmiZIu+uMxJthYTKbN2gDsZ+LZnpwt60ZorHmZKL40QtfO/pOc8xRs6HcAq95Nx'
        b'IdyftXJui/FA4udBdEL+uKBp0WelFDn5keWGlrsfC1bixIMjb7LXAe/SvVKSrc37bbZ2tf5D7q+VQxcMBUAlcrrJ8tiXr6oEG9nGWIq61nkFFIBJiq47IRWAd1DmjM+E'
        b'jyWGn8gYNVE5thVFC4mB+EF/qkNwEXUnNtSKRSVGc2lFz1vunBBdURvuNtGeuT3euSqjfrDetIgWzsOI0UxG1gu4FzyA23ebrsXohC8ZufMdrBKAsOTbaLKk0t67SQ6v'
        b'jOVL/s4/lnAR3Pg1m9fNTeKoORS/iO4VoK7l6DRkr+VqdUOY80Mb6lyFuvAlK4xwPbd+NG6gRw5r0Q32UmV3Z9KFEbkxPJc0ZyhqlAetR5dpa5tCpfRd0m8s0QVMHMxz'
        b'1LuwaFCe8LKcW1dcsWngW0Mf6fexY5L4TjKRKdkdR8THcCDudLkZOkQTj9uNTuKDfvgQvme11EJxqnQPRlsT3LXqAURkErIC0HHq9RdfyF5tfdVUaTwsH8fRyN3JLHL6'
        b'sOKAoJwqzrDxp4uk1jaobd/ZVya0ngxFcSGzP9+TlD/99wf+I2vzG795y/R3TCFDfnlzm3bbOyEDMqYe2H7v6JufV3/yu5aBm0IvH38m9Pt/+n3ihIh4WerHA6XGvSkN'
        b'G4W3ikunDUg/M0T84dyAK/dm/uT1oF82tXfvlY3Ovp+zb8jm7oaCkAvjAmM733vtI/nKmsE/ufQzfvC8gP8I3w//0z99jrWM/dPdCSofKplOnYV2aXAXanjS8CmiTipu'
        b'zkLX8Mknju1B/mYivQ7bYCPmL3wR3ce7vK/Gipk9ZBNfzKE3GoHkWe0fCZLlySK2W+SseDS6IcVX0C580kbN9J3z8GnqjEGEXEANdBF0Zucqx3smyrk4dEE+Ar2ALlLb'
        b'9PBpCT3uA+ME4pXms5GufzM6PNPNrjB0BNolmENW9rwHt08bp7xorcXgeMGphxhaROi5wCtBDB3mcCsL4GtD3FYnLej58mWtpczaB5EXLG2exKAVHit6EYPnPd6D2au5'
        b'3FKpY93Kud5v46Xn4Vxv45XSXSgZkAEpJQMySgakm2TenLOcdMWTDMhzmcdVGz6DTyHiMV2zaTQ3Gp/EO6nCynylzoTi5hr8UtT8mMUxxOnDZ4Awyhe3Gpa+UyizxkOO'
        b'xfN+wNj04+KPi8v1H+s+LlYPnjdVo/XTZ2g/Lv6wOLc0tFSh/72R554TFBP+twjYNTHtbawdhreiraCiECsKArSgDiA8N7xcihoScZ1z9vu3Y8uL6AEJCuMQdxgbg6jX'
        b'hcc006xOTabHyY6+PpkahXqReSmLfyIvhXE7PAy9YHwwtC8Y08a9g5hw+HoZAFlO7QkE0D7fFtDeODqDJ1lMZYNkBQSS+3hOgl/ELwp8DupApw2Jr7/JW4kh+pWdmz8q'
        b'1mhfeS/ifzOZzFX8UbFBH7nvo+JHxRX6tOGPdR8VC01xKYn262fi7Ferr56Jb4wn79yWcLYFAV9MLe+RR5/K/8TjXdnEcucG0DB3gFoUzMGG+HEOcpvXnjJPB1nvp2r7'
        b'AfQueJh7AbpjqDugvXfoEfEV8g7yJLaqZY51Lfu24Jb1C+5ZQM0fAsBxZ8SCxAwJJ/Ph0TbfTYYRc9dIrOTsxJ35ho+KM13gztB+WLzyVbX2g+LHAPTHxSHacn02W7/Z'
        b'Ptw5zucftwth/VKD91a8G28n3tB49yZOIN7Qp/HJp3/BbndQkeNuUTeAe0jdtQTgtUPdZtajgHdod8v12lKb2dIHpZZaOvoC8x54rO0F5uYwdzD32RlVMPPm7XHuJX69'
        b'3YE9KneFWNMdWG22l5aLFlok3jOY0O1fSm50EcnbUuPdAwndCp3Byq5iIT7C5JXwNnLjrmi3adfRS2PJPlJ3gLiutFxLrjQlUf3ueqkG0kPk3TLi0xTf7ee8asWgczuh'
        b'vpTmsBlsRrFbQd6nQTJ3+5NfzpPfNJre4URrSrCQ+xG6fchhxBLzOno8vVtWVW42id0SvXZdt0ys1BqM3VIDlOuWlBhKVUK3z4xZs/IW5S7sls7KWzDHcoE03cW52TWc'
        b'IjHZLLGSETkuAZZT92W+XqFXfBv1h+DD0F6rp5QJx7GziCmUW8qFVC5/PW8Jx/Z4nquYZp24Cd8OBowR8PN8JLqHL7NNnC6QL7ustmpIxLf8gYuhgz74kBAkSu0EEkNx'
        b'R3IU8Zu8FJGRo87MmY8bctGlaNwemzU/IzorFoRc3BolReedp4twx/KAWQLuoFI5jx7Cz/nwS4N31HI5s9fTOzKGoQObEpPiInGdlOOf4VAH3oNfZF4NZ/DhoYloBz4G'
        b'CJ3IJcbW0AHgtkX4FpTAHRsFjo/g0F6Q/5qppzJqxqf9Xb6iPDcCtfoXCvgyuozu0MbQ4Ry8A8oW4ufkHK8CCQ+dmkFdvdajK0RcJ+6wyeRF5tdMw3jcgevmsgtWx0Vx'
        b'CzlOcSLDIvy0bAybSXzRjA+RjtzDh0CXjORAwjywhF7CMTpsg0Ydo8aNRqi0PScGN2Xz3BDQR6YnoWu0xohhSm46x6WFWNZteNdW63Acr6tGB6DGtJUSjo/m0IG5eAcd'
        b'2DR/fRS+BfBpiFVnMhkyGLVKStBx9Byt7ppkCAcia8hV2doRcwxFjHCic2hbCFSH7uIXfDg+hkMH0SF0iKbFoCPopga/VI3b6HuBpNE8uqceSCv7m880bgOA+8++laH/'
        b'XDKDVYaPol01iUno6rP4RQCmmuyknUT1dua8AGTzDPG+ygGlyRftRJ3xAjqAz4fT+lbJNNxemL1dpgq/f+trOAqKwRXoIKkO3xUA8LEAGtSsYt0+nVjB3M0yicPAziJ8'
        b'Qxg3ZDGt6s5ihwZmWBPdKKxl0xaI9uCtiUkpY9Exjs5b58xpFAyBIKUfBrE7l9zN0ozbmLNzENoumZocROsbWZHGVXFc3InK6tBHk0ysa1DdzQioDx1VC3Sk+5PQVrqV'
        b'u75CqclSA8ZBdbk9eDYM7ZWiJnwe7aaKpg3vnQjFK1GbnI7swKAMur7i0PPoOc2yKNqbXAbGoCpJGjo2jnbmg5xQjvgncom2Ka8N8WUnEXMW46uJCXFoZ6qcjm3f8lls'
        b'zrfgS4B5DGMFwNjrs3ADj/cO2ECL4bq0ZYnJcZFAy/kEKJWNt1GkrVilidIQTz6ekxtwPWoUwsdAt+mpwzOL4xJT45aArM6nQa/xfsdZhLRa3BXFUK8JXSGrCB8LmCIJ'
        b'seBTrOBtdGYJlCxHt2C+JgNmjAukBaeUousaNkkq4oI+F28PCJEMgm5fogMOLPclp2Pjfq9YHRA4JJJBU4If+iWmJi3GILKQyg7iJgtdoqgRXU2CfpCDhxrAjNIZ6IYw'
        b'HO9bT4vJlldDqXR0HbApHboAqnQHQ6cbeCsQLQ26OBqBuCuY+en4AjrMLuh5cd06KLUOnYaOTyEDO4FP08aiAInbNYSitZBdB/lA3LhS8MUHNtGO+4+o5T4DjI4bbEzZ'
        b'V6R0LLcH+BgsihtxSaiuVMbxMzl0PBa3M2jtw/crAAVP48vZWWQ/BEbJA8q/kEHrq9fN5VrI8l1VFfmsGMsmYvEzoNRCbeXxQA1mceiEEd+jvZ6L6vBFDdAUfFAj54RV'
        b'fCx+nlH83JJwLg4m9I3amg2f6jIdVOXsM8M0q3EXaMcyTirl0XHrAHr2FG3lrLijKgQkBzWnHlZip8p0O7qFd9BzCwsyQNGNWcx803BDTjSQHrIpg8/MC/UZniynytV4'
        b'S5rr7ClovfwsfEBAnRtX9twAvSxNoOzvhH5N9m+tEtYpHbqOOoHAHkcPQKSM5qKt6BY7I3MTb5dr3Pah9qDzdC8KWI2Um4AuyOyoSUObDsfXs3Dz/OQ43AQELBTdQFf4'
        b'lcXoAoWGCj3vq1mIW/Hd5YAR+CCHr6Iz0Aa9Mvh50PL3uI5L492LXEt5Qp7MUIb30ComoHpYZYfxc/iCPznwQc58vIguU0owAW8jBzOaY3NwW0ZMVu4ipvnFS7mJC2UJ'
        b'A9A9Bo8lw7kkQvmyxBWTZkjYis404KP48MhSH6jzJfiPt21m9zs9BOy72FPnyCGOOgVu4iJZYlUoXcBja8Zr5segA+ionJ3RfYAP4O2MRB/Bh9GWggEZwJlbgbmv50cA'
        b'8nfStLXQ36uaRTAfXYvJfJzh8M1IdJ9eZ4Wvz8FXNJk5w9Ad91PpPDcaNUthcT+PL1CYBY3gYDa2jQkkt4CTi8DbgO8Sm8SYUhMs8yTUBSQiF0pmxiRIQXg4JDWi/Xgn'
        b'Y5ZXFwD6H96Et0nISiGL5SI6Q0ujLQvCoXgJauopLkDxw9JK9NxqJgrcwO2FuHkGPgwBA2eYsJ6uqhX49nxNngGA6Opy8EDJarRnLJto9PwCUAy3oDMScrBr9CxcR8eb'
        b'j/fjh0BI0D50jVzhBejl8IIYgW5JgcbtY/6T+EAyvgVTWhcqIz6W8H/iVNqdtRw9+XMW1QGSV3AVNg2Tn66iWyM1MTGZ6GJEDD6XRdbbwOkSvPeZTNofS+E0fHggOhVA'
        b'sBz+oz2+dBhpuN2mQbef8TzxaVyLjjCJbYeIG62BgXELgEjBCgS6vxsdpPi1U+LHQU8VV4esD1g3Ns9h/mwZhepxs1oGozZzZjXqYuh1rFwFolvGOPQiOaHeosmLoT1U'
        b'Dpfiq/gGeolaM+t9JvBvQEHls3NMv03rUo3jKKlY44+6UNe8aGZQXTLTYM/U8dZ/gHT79htfrPzZm6af54fIfz/pB5rDKWvezp+58lcz3/z81nTNifwTjzVvvlAVL7y6'
        b'L19nefR21fY/Rv3R/+W6P6dN4X7y3U9ePS+uGTDhrzX6hGNWy7SJixtzJb+q23V0QOCij7/XvWv+3dHp4XOS5o3rPH8z1famGPv3BHHhkJ+8dL5l6TP38h+Z//jlF9lX'
        b'fzJw7o+uvLri/VGpY3WFB2dOGTkgtXXcGv+vkl7dOv/t26FNr02fvPh2w2szbxc+ajLWvbascfZ7Y9669DjkTd83RfGFV44Vvi/b/WDXxsWD5/x9VsozU5SWqynvjNmN'
        b'b02dN7ttZtuySWrLc796//Qr5w8dGTxJMqni3SOv1Lwii9KMHTJmf0upftCgD390/O3vDo6dt7f0J7/51++OWJakBJb+7+trR85/+/fvWj6adu6zQcOmtZ59wz55jd/R'
        b'n119Nepd35mFOZGf/brmrUFrtqWtfLvlnzFLlZMeRD6TseKPF5dMmtG2HC/54Y1RnWV/ssb+/c+/fT2pqHOTZJX6M+W7FQe/Xxnxu4pfRnyR91D98yv7bq3UBW1a025u'
        b'uNQauHHmQ1XyC3M3Xm1+6/rRXb+e83HLjk+61x55Z70Y+Lv9QcGrR47K+s+pD+/P2hT96ek9KdMGvXk1NeWPZaHTrpiKXon9z4sDKjepPr1woSbmL8M3VSS9dGPSJ9+b'
        b'euJC+7Jpm4J2Xwp7z6L6WFfbmPS39Ozhv/jis+Dx49//6vRd1UAbsZ6jlpWAGm6eAyBru3lUENeBgkIbFUnaFjwTlRuDtvPk2MMhPmeIgXo1WPElBCymKpEoE3JOOpsH'
        b'4nDNYf5dhO7NQ83B6NjwqgALvolag6sDfeVcGDouMQ/Pcfjl5sn90fnoDHsMPruIWXIH4HsSdGkM6qJOXxK0Cx3FzYmhHh5hVfgmO812fTkwveZY6qQq4xTP4Gv4lAC6'
        b'xDV0jxZfga8nUzMws+0p8tC+HEEnR6fpsFAnNxXW0lp0F4ZVzc/Au/3osELWrIpyO4CNmtAZIQa/MIQmZpDL9FEXj7f3nA8E6XAn81Hbj7eQm/Rdjhwgq3cIAzY/y05b'
        b'dJWnMHv4sws8jo9bpNQmiR4U4W1Oz4pcWOwODwzmfpGHztJ5nVegdXlf3FvscMBg3hfJuJGeal8zCe2HWXhAqiAbGESLIa7NjmmImiRDt/G9PHYJ/310PZF4arzk780S'
        b'is+XsL4fkuLTUeVD3M5p0FMa09F9drteEbmBL9bl61GAX2DuHnfRVW934H9jL9BuiVbHrDQ2Imhvdn3UxDdYyodSXzw/6jMc6vwIoXyvD8QN8wnhx5Pj2fwwKEH+AniF'
        b'MIxX8kG0RAgfRHOG0NwhfBipXagN7DG/QF883I+JV9U3PfkmsFI9ZnuAI3eBmIAInrlMQFu43wzzcEb26IX3bXRq3mNvcOLqZS7zHk8NFE+5mU4qHsU9aaBQMXH1WAqT'
        b'DOMWj1z319kix2x+9D7SjoFx+Mxy1CEjxUctLGI7eCeWgZC0Zwki9q9wkP+2hTIJ964Bd6EH6GYi1JbAJSBY5LSBorVMwYgb/OqokvFhTB797pSN1CxyNXBa5OL89Uwo'
        b'K5Rj0LylZDnjO6lcqR49x2SA69lEJSdnqfebQG4RQ/BJWkueXs72/FNUwxLjN7Cq7y4O4ZTA0OMW/zJxpGQZi1TOCiA2mog4+anQ/dkjWORcNePccSnqkQfWT+Ko0mFG'
        b'R9cV5KCXMkF+W0TEXVk1aOWw9phaehPY+onEuDgpKNxz+PGgp6aPppV1TaGealzcmH3jNTMXsBGRA2uZa8tRF+PZqAsfZVLiNbQVN6PdoOwc9iNn0smx9C3r2Gg70ang'
        b'Ben4MBnvC/Af7RxHZYrh+A6+NXwW7gB4xnAxeBcD4NFqpo7HDV656kOVgu1agmDYhQ6GG0G67yQfUIXwTg7dWjWatjEd1ZtB8TyLSF0juZEgRnUy8enQSgxyS6YSb3f3'
        b'I85CF6qZHNSEjq0uoBs4QFHaebybDy0TKLrk++nQDtTiOP8yDd9gM9CAT8YHkGt5IFDD1aBrStqDSUB70GVQ8LrYRjCoWSfppis13frrphR/6PAPePAfuqfa7EQj/Wdz'
        b'4wpD2Ebr3uEDGKz1o32+ylnFIsMnOmE9mS9Ph8h/QOTjcgesJyrtO+00n3qYw2Nk8ePiOdZIVli/1jGbi3+jC7NuYpGvD5Q5pvi93CNLqlmkLcQRqVfHdVZN4Qz65ptS'
        b'awxM6Os3tlTuzsyVxIfM6Xr8WmnZxO01heN+dXXWCuWSL0L33DCIgVF1v/jRCOkabl9DgTJ3S5r0d7kDCxt2/OnLnyRfSPjxxSUfoOiBB+7qftV4auca+eAJezMvRt1N'
        b'iPzsrfophwx/vnDi3tUfVfziZ8N/kTjwwYXydX9YfT/5w8mnDrVM/s3sZb9WVuwe+d7FMEvNhMqOUYPKExe8h/5y/MKVm4WXW9v+T3tXAtfUse5PFiBAgIiACCoRtYZV'
        b'AUVwBQUVWQu4oiKQAFHWLAgq7oqIqCgqKAoi4triiigudeZ2sffaW2vVNter1m7eWqtttbW999Y3y0lIIInY2/d77/d7z8jknJw5s505M9838/2//62ndpnwrlyt+O31'
        b'e/UPmlM/fujfftTpnHSMY7jjVMdt6istEx8PhlN2fP2gZdiFtxiZMGPZzWcPBriuufNblmvGyjuPNmx9evzLG+52ScKGube299o2flsvzYSYkk3F79yu2Dw2bdfp+gDb'
        b'v+w6/sW1Cd86/Tjv1hrr54s9Du77WXBh1qXBvywe6Tzi8tzbG+99m/id1P9ZWb4Tf0mflgYvVxUGTfjAi5imx7gxB9gCm3QbyJVwHZ2hV44OwzGLc5FA442NEk9z0eUt'
        b's6kV+Zkw0IRk9JWdIDGLF5O94HlgcxEWJ1qc9Iw4z+VQ4HxVLFyFrStjkWrqBS75YufHMRzGMZwH3uSAChU1C2izx66mKpDEUIn3pTkYSeQJDiWpsIMslMA6pMRUgMOw'
        b'i0GnViRDOuMOsmXdkzNciDcw46N88KIEyqNhri+dq1uRmnSSGK0gzXoda7jCDeLCw8SAk+jTq7HkhyH+EtAUR5c5XWbw3QeA9ZS5qA4c7sMyF8Uw+aQcuDaDeOAokrLa'
        b'qFVre5yKCDtwa7zOcLUW7KLSzFmwI4yVVI7Bgx0GpVSc8WFdxtSDPcSBwT6fzqIFOCUlRUmGKyfRdODRsTqTUyrxgDXwEKmzoK83Ej8m+/qDvaH+eF0blRUe4sGt4gkU'
        b'D3tWhEqmM36tiGXtX6n1K2wLJA8Y7ARtc5ctJvE2RlswfC4H7CmaRiu7JTUgGlYOT9KDGOS7gh3EqMghbqApc4N29LWRtTdA8iiFzjbBo3JUXnAGrtQKr0RyBfudSU/g'
        b'oc5bg4uhL74tn2ogwYEDcAN93o0D4TmUWjYa6g1sbSOmk57y2kKBj/cCZ389h0MOWdot5m5tlvGx4R4RvuYZCl8KIYfP1ToacCKilxP6uKCPK/rgc3vidMCJxHBk//BH'
        b'6z1HyLXhiLl4Z1XIFRD41yL7DhEHZ2zCzs0Mxkvf7O0NFHxnRKqqNtha65QlSoGwT6IR+wU6fpMkGkf+K6oYIsG+HNwV59WrM1EqtvdVYAGW2gAT42BsF6wRaK1FtUd4'
        b'u4rYWVJEFrbvInYdZOOfbAqTLUONMDUhPDE8NjV5ZkJkkoanlKk0fOxCQGPLXkiKTE4ioiVpCdqW/7lTCgVmcfPFzYqLL+CJenQLhmVhz7e3s7d0EoistO4nLElPsDT4'
        b'2PBoD6Fn3E5XtR+RhT3HiecaQXYMYtALsUp/KrBgvMARUTJvFlihMtiz1vK3KMd25ozlVzsQTlUH7bd0sO7IqtJKKkESNcZbOGRiZIytjkFWKLVbzUjtpQ4sg6yInPcg'
        b'55hB1pGc9yTnmEHWiZw7k3PMIOtCznuRc8wg60rOe5NzzCDrRs7dybmwmp/J4FJJ+9Rxqy0xDma+nbRvb2a+PUaMsOf9tOe90N8O7kaO1IuFk1sRj0u2ZQ5lokxrqVja'
        b'n7LDomvWhOuVL/WUDlgtmCXCrSEdWMkpo5qEsMwO6RGEtxbF7yH1IOYA3iwPbHRc5K/bDRDYyVo6U3SJksCKJZgcBDM+peVJcSeXd2adNDjxTsZAcJbiCR3lpyvzczDp'
        b'NMavYxe/lD8TuxiWFaiol2sCZu/kedk0WNNKY82ylmG6H/aQ7DILqCdSTPwjzSzS8Bbkod9yZVK5Ohf9JihAtVmYr5CSMYIayOoTxxq6udL6ErdGypgNu29sq3Nz9TLq'
        b'2Cwv/mff87pLHYvb+ndTx76cObYLS6xRKP/vZI7Va39dObA3cjOlQJdNlSFPnJZTkJ3mZ6wooeKMbJRlBvH5bZ7I1jyPrRHO2ldokZfy2KKuR90jR0ycJs5JS8eE6ehQ'
        b'3+O0l38nX86Um81oKQyLTtpWEqjXFEYKzxYEdf+XsOiaYsw17uvBFItuNxlzjSbawaIr/v2MudpXnDY7PRPLpewDC3rZA9OOC6xPbPZMrJBlyZWohdEYhYYy0p18xWr2'
        b'sanzsG/qVyamdaBqvFhJly1EFtk5UdbTtTwvHNBujpgWyZMG3LFrRgaGCUV9ITVwOBjqzCAZVJzgXDR731RnRo2HMU/YmGM+SbydDcrhqan6KdcXCGETUkJW0D37CXZE'
        b'x27gqGLUjnaUUVYIzpfQlC2LTbDdEtNuPYPrNrDOFuyFW8AFkmyRL1XJ53GzhbeKZ1FnzeMXD4AVtrOMlDjKJ0k/seVwkzXY5gtbSVqZnnTBoGFQZozn3BhGjSHzrqBG'
        b'SYuIFK7WzsS3WOGj2l6nQrbaIgVlUx5J18bDlqwk3MvNEk6WpDJqjPSHNd5Y1SNlrPIxTFeCdBl/aqCjl+g5cMQWrkPK23Z5eJ2aqyxHqVy3v+/3l/Ye3ADh6rQr+R7V'
        b'4f2XRj4N4wycEhK41uaJxeG1iQfLn22ccPXnliU/fhGoOvhze/H3Fz8PLG2+9eUbLmuXfnzAwi2v4piP77Wvxh4tlfa8Jh22tvlY+WI37l+fClue8O486D3t+aE347cN'
        b'8n8ouSQZsT23dL7q6CP+i8t/ve5x/dyV2F+/t/ooZMQtzmQvG6JeesIzi5Dqchq0x3f0N6pdwnOwlcQBJ7B3KFtwaUpXWhc12EDpaw/A5XCfVk2Ni+OzncyC8YA1fNjS'
        b'D9IFcbiuIEKrqbJ6Kly3iKqqopHEWnDyVHcfBWxiNSAKOd8lpyr/SVBDckFqNNJSj7Cq9GBYQ9cLGkGlo1YfhNt8qEoYDFpJ1hZKbGZOdX5W4Ydns6jOX9yD1NQelsF2'
        b'qppSvRQeLmRVU/QYD6iG4Brsh+dKqOzqhxT3ViVZxsAKbz04G0OkWT9LJhastgK74frwP0yG16EksWCkp9UtY8YTQlyOZQc5LiXKJf5NdWda/lkkdpigym3DwVkcnMNB'
        b'Ow7O4+ACDi4yzMtNYwXdScTOoE5e6EYlfrh66t5y5lMDr3FdS95dhlabVJ3AZAYDN5VnyJmLc9LjzMU/meXMfSVwpTBVT3oyU6gZ2kL92q9TCYg08HvIY7VykplcU3S5'
        b'etBc/2OuXn4qko3M5DhXl6M7zVFPgvo9uSEByExuabrcJB1CUlpn7OqrsQFna9tXK5KYyV+qy98NL2LoyS2/i39YK7eYyTHLIEfUvjpZR78PcynkmSxy6Oxq4zJ4bEGw'
        b'QTp+W4lhLTb+J7tV2PMDl9VSbYhPYGGmUGeebmHSPF1LuWTh2G3KJRnmlOwu4xKJ/CqES/oES12SxIRLOlSyt6/YWx8cjc4J2hpF0qeLIbIrLQZm4ei+fqfLaKQ4KT8X'
        b'awlUq8Ye2liEc1p6vlrF8hgpkTxqqm3wP8wZIsNNIpVnEkYZFStvG1aKbW/ifxI1Wxbrf86IqIv/RekYkNLMqW4BwXoKi1iipVkxrbrotysVy7u8mGJJeLpClpGdhxle'
        b'WD2OeKEzWtCOfqBUyrPySFegPCpdyLyUYrl+reRIpckyQdaiVVUCyEMODtVpLDinAC9fvA6ipf3FMXS8vxmmlCzSK+XkfswphdsuJLT7nFSZhhXCtZbLlH8co5QEMygR'
        b'7icvsbd3LlajUXVKvL1/N8eUWEL4pPwoLdOrJG2GT6pb978qu5PYBCuVKXYn/+4VwwDdYZbjSaLjeArwEqcEBJrmaNJHiLCPUS2j1ZHnkYISNvaI2NiZM3HNjPmjxf8K'
        b'0kpyiTdbmQJPTL6EwE2n/eoVKNB8gcwSTxmuhdC3ZYj2TTFaLCr26NNVoeyDhppmHtPH02hXhvReE/QreiPzlHJaqPxM40Re0vmoZ5D2wDcQl75pxfi4mxxG+F+4QSJK'
        b'sigmz8hWyQlRlbKDRq3rO2syTT9xACaAlqnR4KpLAPVguZhtIjRC5aI3LnKqX3KaKl2GFxqN02r5iVF3oS5Hc9S5C2TZxtvfTxzUKRrJLU2duUitkqGZA7tzFk/LVyhJ'
        b'oUykMWykOFydmS1LV+NXD90Qrlbl4/ltgYkbho8UR+VJ5UVy1JlzctANlOxN2anmJu4ONlbkV2+gEcaSkesVK/fVihViLL1Xa5dQ0pAdTf+Sljf6YzLtyXhFsFO5X7kn'
        b'6lc/U4FqI8FtqytTWvoidZaX6e6nf7t4xCDTHdAgYkCoqZiom+UN6cqjSS8O75xMsKlkgs0lgzqFrn5m0gjRj2ayaqEGiRmpl8kJjcX7oRGOPSLyAJJJ0diqHcolSXSO'
        b'NTlhd8AJMYE7mgrpGZJxJNHoVJaH/lA3F+M5KMQMB7wOiGiYTGCnZALNJkMwiwZkgxLCMBiB55vhJm/TYRzprZFTyUiNfxBL0EvOdnH02E03g1qBSRcxiT175CvWk+0i'
        b'pyaKJdNhU7YCvaSoLMNMF0UPXtmRmO5ntlDapJQL1Apl10KZE/dMiZdElOy+5KcT0cINFve7J8MQQOhIcRz+EqcEDp3T/dsC6W2B5DbTT0OLNGVFSPYcK8vm+gGBoaJb'
        b'8BeK2DWe6VFsskyhyBsyUZGmRkGO/5CJciTdmR61SHTTYxVOx/T4hDMwPUCZyxmNSpHZSAhDY7/poYmUDclsUuPFMNV4SIqVyVRYssDfSMAKNivfpecXjxTjrWIkP2Vi'
        b'qRX9gNrc9EPFN2EUML0rLUeMT8zekSFX4RcShWbFPQp6xjHpAUnYF8vpfkEBwcGop5kuE0YdowLhL7M9MjMN1XYiGlTMRSK4ZfSE8Jc4Jdh0RHaY0/KpmunRWkT1SPF4'
        b'dEQl4ZTAEWbj615tcovh5p3Z9tbitNk76fMxPVhjfDYS0caHx6HHY3pETJdnoASjJqCsjbyRBkjrrobMrBuivWJe8QMu5ZC0T05kCK4JHgIVoEoPHAc2DxYQdBysBqfJ'
        b'fbvS+fM9Wd6+zYVDWIR22zxQGc2i9YrFHFCPUjpL4o9Z0su1gTcD8z8uOZ8+n9pK86fAWsyQwfgzTr394YVplDBwRWEYhdH14ZLcKRL6yBiSkEvREqv3mCcWzNC0xaOy'
        b'ihjCzwjOwPUzfVBkzDIYj40FwdEpsdQdEjYbrkhkiodZw722WbDNm6CFmkvjBFWW6+wos+I27mlGjR1QwwbQhklG6bZZzlR9ikWc2GS6GWHAq1gJaoVeC2fI5/lWWyg/'
        b'Q4k0lr1Ys3HMfMxc+PXVKUc8Vv153rNDGzbd69lk96fCcevEKwTuw+23VPiuKMxQcKePTXkScH7XmLD1Kz67MOLu6LfbnevER2+n/Nz4fEZ5aPgbJ6R28kefjjl0LfHH'
        b'JkHUb1ft1ANvwh9rGy/u/6KoRl5cfX/TV9w3tgV+GPPu2JIvs5t+eA4ibK7OCspYOW3OzV7fNUfeHt303adz3p3tElAyw0t+Y+3tQUtty61TNNeOfZB9qvTR0vCgVWN3'
        b'nKsJmftttsdiy2fvtQxbHTq6qf3DY9kTbgWJrHdFPF+R8uKvokXN31xd/ch+btSkKVPe9hJQ5+vVWajRD2UbkPVhw0rC1jcpNFPHIeU7BaNE3lxAzPG40S4+k2NgeXwU'
        b'OMpnLHO4nmJ4gRpmnob7wKmes227borBM3ADMXkNA4dGGNsqIttEGWBbx07RIHCSmD72B3sDsdMk1mPSLNBg4DRpwiSylVUwGBzR4+4DDaGYP4qS9+VMIwWHbbAaMxBG'
        b'cRhuIgc0wibvrNiu4A7hH+T2G9uskd0pvAVrsDu1jIkXEA4+PseeM5C4UMLH2H7Qht2Z4hLrQzf07cJx5CwS6vZg0qTSOAPfHR1r1NiGXG87yvqVCu7F10ukw9Wnribz'
        b'je5J1Xjq70kZlNI4soO4Y8LmREwZX+eO6WVMRln/95iM+EYHfRa98tiSGuEvn54tfMd+BPU1Bcqc4U6lGoOSK/kMf0AkbOGUeoOdFNpCyTrgJi9bBjahJzKdmY6iUydV'
        b'F8H2BUnkNimoYjiwnYBMbalHhkEUsjIvPTclxSOJ9T9xGr1grUEqUE/hKYwM7oPrCcKhL6iCjUHggpIiWpiMaFBDElo9kaJWnowsiRHFD6JYlMBMimQQJ6pjZi9W0B/v'
        b'SamVRRg3OyY4qJT+WDyRIhmeTJLFRE0bw1aoFp4CjUnwUhhD3MmPdybFmy3kBA0dOpRJAGdQbZrQhAR3o8kAJzNM4sD0YRjXBGWh7/WSAoYSXFfD85OTYnXQF3AeHsLw'
        b'F3hkKYW/NMODIwj6hQM2gHUY/uLQn0yAoG7J2CB4Hqyg6J9kFwoKOg0vYScAYH8IBa2AVaMIPiUA1r6mw6bAQwwLTwGr+5HCiVJzmE9QxQtmFrwWMHMsLRyocbA28G/f'
        b'FoyhKbAZXiTIEXKnr7OAWH2E2WcI6yLZxn2kpnYwTxKy+zTzLeiP3wx9i1nOYUKOjZMG/DRoBvs8j3tnK+2ChvJTYTPDBUcYeGEO2EvwHp9kUAMdseVi35sh/SgI5FgE'
        b'xZo0DM/N2eo2if7YJ5paiDRMKfTd7exFf3TgUtMWZmG+cF+RmGYnx57ukhISEhiwfwDDiWDAih5wP7kUlwV2JCUwhITYHjSjR4f6E8WAJyOhYCu9ljCDXJqQRy5MDofn'
        b'SGqvw6M0NdVCkjmnL22VhknFMVHz+9E+UyhegCKjgznD4SomDRykPMY/qWhPbPDI8X2aFM7Iy2ukHOUo9Pykgr65VWfjYJhT5F33dz/t+97KCeDilz6SX5iBNt5Ngjle'
        b'6dl1HyZ8ckNwZf84v/s80fC7YZd3h5QniqMH3F0+Lyj/TumfK6SBW2NsS+u/emf91MELEx9cL81URFVeP3Nl9Ff1IWvsB9kmZlTuWxu1akbeoKnu4mPOyaJF4J+iG9NP'
        b'1jRuH71vj8+P064VvHOzeNHUM3bDah+7/pA2cfxHA+VVdUfLF1rv3tIaFb8we0FkrVXWoL//6le4Z0njyRt32yYvPagJBhev2w2Rfl/x5/FbvaMOnJ+wcOqX/f6+ZNud'
        b'IN/2TRZzIh58//BrTsaSU2EXflzG580O+G2e+GSAzyPPom+SZf3G2axt3ZIo26kAFUPGDb/4+Hj9hK/a/P95+eoHq197+EGpunTDtBuV7+1T3HwYBGqWPqtMfX9M4bhJ'
        b'tytHT874yerHeAUno6eXE/VmeDG0yOSUr53vPTzBbie4nAgmCrf+PkSEQNcE8JQAtnNRN2iALXQaPwjWgjIkKsZwUnMZfn8O2O3iT8xkFvdapkeieDwJu0EsDqJQ2xVT'
        b'sDcJFhUDD8A9LFlMI3iDoDS4JbAi2ghmRVxSFGlhHelAnalehGf9qa2NCyhjTW0WJlNDnIshaMioQLeeFHnrMCvwGKwlWGEuXDlOZwvkB9eDhhmsUREXHiKJp49NB0em'
        b'2KHBtaIDWsPtQ6Sb2NEiuCayk5UQNRFSwb2kWWLBZlhGJbZB/Siud9nrpO480FIaDZYPNXCLbg9W8cbHMtQCqQ6sB8d9wDHQ1AXEUpFDMBo+Y2F5tBqu0feabl/Ki5gL'
        b'1pMkUsBJeMElWt9QiLUSgptQFEKdPBLu1lkiXQCV1BQpaya1Uzq/eLiem8pgeATDUySgiWJxymBzQTg42slWiRoqgXNgGzW4OrW0v34Ts8ZWSHK9SAyuJsDVJt3XmRfl'
        b'8rWiXF5XUa4Ai24sIRtXxKVQARGL4sVAEhES5fqgX0VItOvgqhSxf1yWyM0Gs1eyABMRCxnAnC8s8xoRqsyTuxmvWheaNyzH9eksxy1n9hh6XuycKUoH0w79wWxvq/+f'
        b'7a2L5Gec7c0qjvrI2Q/POxtje1sHVoCTHXRvoGU0mU+5pbAMbs0r1idvGxhDhafKWTk+cC88QqGrTqCSiDTBy0CbT2aolritRz/52c+aLZRYBShh3hpzlfC2WdzLGmzx'
        b'fr1rCJMu/YKJmc1slvByekywbOJOKJNerhg8I9Q/yud46fZ/77lRXJzo83TG/OCsu9OvNF+/PtJxUZXLRVHEwWdjVjweFfe3iUk3e6+pmXzV8y0Hfsrsr7I29okVp1ra'
        b'T6xJ8PBpKpGIb2981PL6P3/ePfoDz2G7lsFzCxLyhgyez7Md5fOv2kj3o/XNoqE3qw/eOwb7Df747re89x86XJMH/rTlmZcDUWJhVbDEZ24vPc62bA8yWjukIJGV5WtL'
        b'Byu1lG1L4Uk6HO12DyaXL4KdaLhh6djqYTPVc3eAOnC6g5GNy5TCYywj20pQRgbMmEL3DsY3LtNnHEv4VgvbSQ7j7MAqHWEbh3GC1YSwTW1BgXyHQ9DMgfnaYI1LvB8l'
        b'bEteSqeyivmDo2E90l87OS6GxyLITFAKG0MwY1tGJmHFxHxt4XkUaXdCDht9wPLizmxtVr1JttGL4XFC1TYdVg2Jo0xtsHIiuRc2uoNGlqgtHqzWcrXBVrCX3DsM1PUh'
        b'XG2hYBdtsvFc1+j+pLJJSMNA4tuemQao1BR4hq5D1ILd8zBTG6gC1b5RLFdbJvxjuNoI8RcZvL27Dt7LGD9P83RteAz8w+naPPhan8rLO30+N0Lcpi2COeI2PsXykOsE'
        b'2celmeOvOC/Hzjg+bPymB+brhoXqCYa4c1fJcpUUjdeJVK3Hf7Rq0o3H2IqC/jx2OUVgyeeiOZbrIuk+hxp+wK4c8ULHUcSzoT08Cy+5wiNKnVxqwdi5cZHAsm+sFydO'
        b'nnjCw0LpjianLRHiyI3tSAEQRWbdKro/yfHd8rv9B9aPf9cqQXTOaXrzumrubXHV2tPDglOvHj0e5jNzVNbXdz5//OTz21ml85w+frtk3KejVJGBoz5f8nz3Z7Nuerj9'
        b'MuvOR3f37HDMtEj7bV7tt3PqziiP3HN/tn/PP2Z5nzgwrnWAi9v940/XvPmZfL4rd0/hn3w2llx1v6N4P/TxLx9GCHqof7s3Zsv5wSDoJzcHW99RHtH78gcO+bkS2Bzf'
        b'/HzrhqCD5W9UCaInTvx3nKR80vd1pfKUja3SH2SzFW8Pv3v83X++9rZlypW8yuBvmjf/VFFnWdl30ke7+j9eeXnbWL8xL17UFV5+s2mAk2TQHLcxIftuue2+UhvTfjYn'
        b'5cDA558MPJgQ3dyv0u1pxOWHDr7bMx2+PuzFI45oZg3pBytiUkATB/vvgxsnwV2URWdVgtw2Ws3ruhq4HB4m3lsWI838gN7iHrgwx2Bxr6eR9Tn3/56e9soBGoK42jfN'
        b'aECgx4LU1Jz8NGlqKhmCMDaaceNyuZxhHDEaciw5jlyBm9jJzdtpnNPg0XhAGiPg2du+towpUnyke7l4Gm5qqt544/a/oPYcxXXdu4lLimdV6oH4QZg+9xvuCBZJ80EF'
        b'2ITG/nPwFCyPjwHlYJMVY9+b15c/SV71hTeP8ARIVpX0Lb9iA8JEFu1Z9a7Olysb7v0Q9RsQ9f/L7dGvDV6T9eJ0YdzUyEFx1fLGKsulh0bEj/6hYevOOQH7Xwy/P6LZ'
        b'543VtSPb76/5Jii0WtLKLzydm/f++GT5mgXt5319AmLEQ52GeQrdTh0rmJGxyq/ok8+XDxhZXFcw8S2L6bcLHrd/kfScfy313w3P/8XZ1yYJ2DMPiRB4iJ4BD4AdeCqO'
        b'xxsTmP7ZFpzguuUiNbQd1lFw/hmktLVEx/vB4zganq97wPNwJzzBA3vBaXCcaJjZSJhYRZthLrhE4EaVpBUcef3gFkDpOsAecAqeiAa7QUNUrHesFYMGOsEADxWW2GYV'
        b'IR3VacYQS4aTxMB9YNts6t1qgyNo8QG7F06xYDjRDKxxpqy0ktDehDMQZYQh9bZeXNAEajE5IYscaQX7bZV6MWyiuL1V4NiyUiJm9F0Cd0RH+cKzJVF+rEZoD9fz4sAe'
        b'2EbyFXvZoeuB4IzWuWMMhzoHaIyGK4nAOZkFMgt7cj17wFPg0ngKnjkkxQ78UIQCNoINOMmFLah9TmEvUdi5F2qQMuIE6oQQrFtYqIYnC4WFag48PYzpBTfxwAbUUIdo'
        b'dltcYW00YdHAdWHQ49nJdZ8JG/vCBpKUnx8SPVCzD4lGQwuqK3a5BXfANtz27gP56Jm0gz0Gbq77/s+/Xp3fNuuXjDVGhp4OeAzhqLUTUD9RhK0B66dC3tjOwtBAKhOQ'
        b'McdDw8uR5Wn42FZbY6FSF+TINPwcuVKl4WOFUMPPL0CXeUqVQmNBVrM1/PT8/BwNT56n0lhkokEPfSmwaQdmgSlQqzS8jGyFhpevkGoskWqkkqGT3LQCDQ9pXRqLNGWG'
        b'XK7hZcuKURSUvI1cqUUCaywL1Ok58gyNFcVKKzW2ymx5pipVplDkKzR2SMtTylLlynxsfaqxU+dlZKfJ82TSVFlxhsY6NVUpQ6VPTdVYUmvNjnGUVrSv4jE+foiDr3Bw'
        b'Gwd/wwHeDVR8goPPcXAHB5iMT3EPB3/HwT9w8DEObuHgCxw8wMGnOLiPg0c4+AYHd3HwLQ40OLiJgxs4+A4HT3DwpcHjs9ENqs8j9AZVcu1XQSY2yc7I9teIUlPZY3ay'
        b'+dWNPUfKb8aCtCwZizhPk8qkcV4CIv9hll2k6rIsu0RC1NigFleolFg51ljm5Gek5Sg1wkRsHZori8StrfhB226dcBUawejcfKk6RzYW4yLICgOfi8auzl1shBPxjPBf'
        b'FIWz6A=='
    ))))
