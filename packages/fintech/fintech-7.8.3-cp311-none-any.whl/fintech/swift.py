
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
SWIFT module of the Python Fintech package.

This module defines functions to parse SWIFT messages.
"""

__all__ = ['parse_mt940', 'SWIFTParserError']

def parse_mt940(data):
    """
    Parses a SWIFT message of type MT940 or MT942.

    It returns a list of bank account statements which are represented
    as usual dictionaries. Also all SEPA fields are extracted. All
    values are converted to unicode strings.

    A dictionary has the following structure:

    - order_reference: string (Auftragssreferenz)
    - reference: string or ``None`` (Bezugsreferenz)
    - bankcode: string (Bankleitzahl)
    - account: string (Kontonummer)
    - number: string (Auszugsnummer)
    - balance_open: dict (Anfangssaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_close: dict (Endsaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_booked: dict or ``None`` (Valutensaldo gebucht)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_noted: dict or ``None`` (Valutensaldo vorgemerkt)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - sum_credits: dict or ``None`` (Summe Gutschriften / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - sum_debits: dict or ``None`` (Summe Belastungen / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - transactions: list of dictionaries (Auszugsposten)
        - description: string or ``None`` (Beschreibung)
        - valuta: date (Wertstellungsdatum)
        - date: date or ``None`` (Buchungsdatum)
        - amount: Decimal (Betrag)
        - reversal: bool (Rückbuchung)
        - booking_key: string (Buchungsschlüssel)
        - booking_text: string or ``None`` (Buchungstext)
        - reference: string (Kundenreferenz)
        - bank_reference: string or ``None`` (Bankreferenz)
        - gvcode: string (Geschäftsvorfallcode)
        - primanota: string or ``None`` (Primanoten-Nr.)
        - bankcode: string or ``None`` (Bankleitzahl)
        - account: string or ``None`` (Kontonummer)
        - iban: string or ``None`` (IBAN)
        - amount_original: dict or ``None`` (Originalbetrag in Fremdwährung)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - charges: dict or ``None`` (Gebühren)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - textkey: int or ``None`` (Textschlüssel)
        - name: list of strings (Name)
        - purpose: list of strings (Verwendungszweck)
        - sepa: dictionary of SEPA fields
        - [nn]: Unknown structured fields are added with their numeric ids.

    :param data: The SWIFT message.
    :returns: A list of dictionaries.
    """
    ...


class SWIFTParserError(Exception):
    """SWIFT parser returned an error."""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzVfAlAU1fa6L03CfsqOwQIsoYQtrAoKqKAsoOAeysGCBKFgFlEUStaK0FF2dSAqHGPexRU6orn+Ld22trEpjXDtH+ZLn87M502bZ3W6XTad869oKjYN/97M/PeH6+H'
        b'c8/5vrN859vOOV/yCTHmwxr5+90WlOwhKolFxDJiEVlJbiYWURKWlk2M86mkjpEEcYocfZc7VLIoQsI5hvKnHkGtIhQOiylUblXJfhJ+E4lKrSVPtUISlZwSwraKb/Wj'
        b'xK5kfvasUl5tXaWqRsKrq+IpqyW8ojXK6joZb5ZUppRUVPPqxRUrxMsk0XZ2pdVSxShspaRKKpMoeFUqWYVSWidT8JR1CFSukPBG2pQoFAhNEW1X4T9mTgHovz0mxBco'
        b'aSaayWaqmdXMbuY0WzVbN9s02zbbNds3OzQ7Njs1Oze7NLs2T2h2a3Zv9mj2bPZq9m72afZt9mvmNvvvIdRctZd6gtpGba32Vjuq2WpntZ3aTe2gtlV7qAk1S+2idldz'
        b'1E5qH7Wn2l7tq7ZSU2pS7af2V7tWBSDS26wPoIgW7pPkXB9oS1DEuoAnS1FJ4JMlJPFSwEuBJUTwc+saiNWshUQDabuZTxVUjF1YV/TfDRPBaoQbSgi+dUGNDXr7VMwi'
        b'MDPEJq0Pu7fBhVCFoZcw0Ad0cBtsKcybA9WwtZAPW7PnFgmtiHA2uJbJhjehDhzlkyo/BLwS3ChSZIvBpny4A27Ph9tJwi6bAno5vFBBjhnEhNFBaFCyy7UZDQTRjEB0'
        b'5CBKWSO62iJ62iN6OiIaOiNquiJqu1VNoCmHWKvlKUZcT9GUI5+hHPUMdciXqBHKjVv3iHJV/wjl8hnK1S+3JhzqP6cI3tKabc5pBF24YwJFsIs+RdBLHcrmpjKFb/nZ'
        b'EC4R8yli6dKav1fmMYUX8jmEDRFqTaQtrdmUXUucIGrsUPGahT5FNjZfhBLE78O/pS7F8ePkZI0tqni/XEPqFXZOCD7+g3ivhmKCLhZmfufctWyvL1U0TP684MCMc8QQ'
        b'oYpCFRKw2x8t4baYORERcGtMlhBuBSdKI3LAZl4+3BkVnS3MyScJmbPttAXUE+vEHp1yI14nFr1OeI2IKtajlWD9y1fiGR62Hmcl7JmV+HGqM8HldrCJ2KVRzglVhCoG'
        b'FYJe2MdGBNguyIXbYUvenKzsqOy5BDgJd8bnlniArlKwDewilnGs4QF43FrljpcUHgTdInDZvgARAZxArN2TqcKdgiOEiwj0r4ZHcMU+YoWzN10+JxZeFcXnrMYgu4kK'
        b'cAxuphtaCLvARtjJIQh43DaaiAZ9UE8P1bPcjnD3nkcQLkvzNPEuDCuc83EjQhw2UohpuJ1UIiHdWnmeVOBG31nxyd7fTN23seVg5/nONT7BLLict6XJ/bWaKpcXQ0op'
        b'L9bWeFX8/PNxsdqTtdQfC8R3q8hTy/qGc8T8pXniMxKdmDjJ2aqMO64XpsWzyKYr3sXmxd0h7ZnmEm9jhnfJpLbMe8YXhv7DQTnd7crfXvaZJCIEL/u+9V4In3qAFSe8'
        b'7JJsj8jHz1cJIxETwUuggyI8QDPbBm4MfeCLQZoWQS0i81a4E25nEeAybGJPJsH5+CQ+e4iK4MsdEdDjRIG5i9fU1PSj59QqeV2jRMarYvR+tKJBWqVMHbKjlXpZpVgp'
        b'aRyTpzByM0oeNhGWDJJwcVMr2hJbGrc3auZs3aDe8KEnzxCUMjDXGDTT6Jlu8kw3uKSbPf00lR01Bk+BVmnwFOmU6tlmdz+NpL1QnWl299qT1ZGlkWhnaudoZ/ZKdR66'
        b'lXpXneK0r37uQNzAnAFR/yKDf5rRfYbJfQaCd+O1TdN6GN3CTW7hBofw7zBPyjFT8q2GOKvENSrJkHVZmVwlKysbsi8rq6iRiGWqelTyFAEw+y7lYRLInXChM0rGTjQY'
        b'A9XjieKZppMk6WYhfi0ZdvJSS1tWbF/RZG+hOKS72X6COrll8vbJw2znptyN+Zvzm/LNNs5mGze1/UMLh+C4PFnaVMj8U2BW3GUrIE45TWbNqqDGUwnrMAiFzSitFMhH'
        b'SoEaRz2zbMcRc1TCekbwqZdYI0ph3LrnK4VHAxujFKwKaNGEm+GrsytsYCfSbUJCCE6Cm3T54pU5cDM4BTuRixRDxIBDsFmFTdOSUHh9CthLCy2S2OnworTy5jccRRpe'
        b'r6/ey/gLFsSDnVKSldQGNKB/e8tGcaJb3pFtJzrPqxNfebXzhN1bFeVfsP+45DWbUmhT4vbWYDdJDE21F4r28ckHXNSMP9CHCHKEUJ2dV8Ah7MF5CnTDi3Af6IKb+Kyn'
        b'GQW7cKNcMmTPMEhVTZ1Y2Tj2hZaLSSNyUUoSHr578jvytcFahdFdYHIXIM51dkd84hhi9kas323fxjG7+bYlaxLbU7tSDQ5BcpfHjCzH5m6IUykplyrlmChyt3GYl+Ze'
        b'hnm9MPOOHY4AQ62kuRcPqASxry/m0ucn/1T23W0bRZx2SmHRalWrdCMTqLTZ1kWDtQvcYoJozexdvEChTIq1A+1sgion4LGZ4BoNvcnNnZxExfrYxw7WaqzLVqvw3MB1'
        b'sAfswgjgwAqSoCQEPFEEX2YQFniRU6mmJFb9YK33jE5HunmwlSIwOHcRi6CWEfAUuGBPQ/dU+ZBplAU5TIPrNS5/KFZ5osJEcMxRoUyO5QENGo2MgCfBRbiTcQ/C/MgM'
        b'yjveKg3BJ83kqbxR4XJk1PZgBNgF2yiCqsMd7IKv0Bgr5f5kFpW2yIY3uH7BSwSXxkCsvglsUcD+xFig80AzAC8TsK94Eo3xh3UBZB6lcbRdijA81wbTGGA/PBhOI8BX'
        b'2RyEsJmA/XC3L42xzppHFlHqF51d0KhEX9jTswDHKuEJhRwhHHYn6UGdhgNSGv4N1USylIpotCpCPUz9Q4YKmwxwEE1jH+xTxcXClwPRxJEZhn2wF/TTOEl5IeQCqm2D'
        b'dSzqY0Z6BtPHeahPoVHyHdDEkbGF/bYv0vCUQzj5AjXgals/uN572dAUGh4enAkPKRSi2EiA/AJqAwHPwl0cGr6kkE8upSI2OBKDCu8Ft9fQC72kEY2AHtEueAItHegh'
        b'4MDsBBohIFxAVlJfTLEmbikWTO+OZAjbAs5l0xiJYLM1QthLwFcbQAeNUVUSRVZTupes01AX+dEk3QXcCy6yYZ/CwQ5eDURzgBfJBEegoRF2h0WTNRTR6JB2S6FZWsdn'
        b'5twdLLSXJ8XCbRWYSMeQOS6CZxh4r1iyniJ8HHmogzV7G1QeqNDOOckenk+M3QA3I3jkh7MWwa00+CcBIlJJ1Wc68lDzZS/LaXB4YArotreLjy2RolWDu0nbZPAyM9IO'
        b'aYo9vISI0crFLb1CkuAIOE0zOHx5AuKOvgan5UF4DgdJwYwShm9eBR0xCltHqIdbwG7c4k0ySQkGmL509nb2K1XwEi8ZLRg8T4bWgQt0TTi4DPoV9nKlJ2jDSBoyYGoV'
        b'Pf1SoLdSKOFl+yrUEqppJQVwSz4ziJugPUXh5GjnOokiWBxyGgU20q35BYLLqNwJbEYjI1i2ZBrYF0a3VgdaZKgGeXQKPKUBMhqegseYpdy6AV60d6wH28EW2M0mWMFk'
        b'GpLEXkYD3LTypHl7AGxE0lBPwDOIFu0MnfbbIyZTJiUgqT1vRVBVSDsUAC09kpXTrDD7rYI6DiN0F+BOF3rw0+ZtUMDzsM85dBGm4FkyIWZkvfcv8FDAS6hmMsDSDU+S'
        b'osnxfGd6CTc6JJKrqYfRjksHFeZAQxFdOMc9mVxHDVRxlt5SeHtKZtOFStEksolymWXrMqjQ5G10oQuDg6eQmykix9oF8XDtVC+GsR2mkmrKJYhThLiozpURpy/5qeR2'
        b'KqKQKkKQnilrmV0iN41so5YG2sQOKhb4vmlDF26ISie7qAWlRCzq3asunC78oySD1FCDftb1qM1ZpxfQhe/FziZ7qfoK23rEf4vWMOp5EzeL1FLVpfbE4IoFoaKJdOFv'
        b'g/JIHaVNp9JQoe2BZLrQL6mQPE0NN9ql3VrhLVrqSRf+tKSI1FPDUda8wRWamAQJXfi75BKyn4rl2fIQ5Is3JjG64Bi4MlVhb+cE1I2IKRzQ6naAkwzJt4JX4AF7uZOj'
        b'AN5ErORKToMHljJccXYmOIeUwuUGBeyNY9H8LICHV9Ern7YQbERSgNQkC6gxc3aRE+ERTz6bHkXm1NfIXtbgXHb9rQZvWQSfLjxG3iG1LHUIhxis81bsSqMLk1e8SR5h'
        b'PUyyJW7VLVjw6kt04cfub5M6lsXLIQ1B1j/Me2J3xhn1eF5CyS7OyC6aTe+giSrOv3GvvOxpZ8yKeNYZCytQ8dDbXLB1MdhWiJTwTbgD7RRasvOjYUsMRXguZYfbwXZ6'
        b'3osC0N45oxP5dEuj0m2WMnujZBu0d37hgRVyO6IGAgMImvxzQhbmxsCbyblwR2E22kbDzdQauCOREdgdVDboA/2gn02QCwmwBRwHp1PC6aMKsBvoYZMgAm1m1OCyXwzy'
        b'whyWsZyRytKqXGlruRqoQR8aQSA/hUipYsnxEOhxfEGxCZupTRy0/Y4yzstlCrvSrAmHKBcrgrfU4VpVHkFLPtAh9/C6KBa0ZuK3DkIMm6ersFsPt1fBrlx6q7QTn5Xk'
        b'gp3uJTHZ4EwESfCUHCd4ZD3jup4LjBMlAC2yKaiBLqJcJlfhMy0bdrwA7eXpQxa0sc9mE+nVbnwW3A6uwA4ak1rqIopHm81eYmRDurmU1jk5wfC8CFyA/Xy8fz1A1Pgj'
        b'9YYrqmEr3ChCW94KWgERy+A5ZisMNkbDVpHI1sMKG2xiObKL7XQXQrgR6kVJjfS2WENU2oI+hrbt5WBjbg4emWJhAbMwTvWsSQ7wGqOzDzsniJJAE+zBQ+gmJIHwIo0I'
        b'X54uys1DGDFzwA3YKiAJ+0VILcLDsIdP0RSl0A69l8Y9g9xdZJqrwHV7ZpRdcH8oqtkDe/E49xLLVswdkd5Y0Aa3ob1rPgc5FwvZASQ4BG5OYIbSnDxBlOQKBkh8TEBU'
        b'g9PwCD2UUnADXBTgBUHmvc+lAJxhEw7TWM5yuIXeI4DOgHkicKkMHygCLVEzyZ9GC0UrcB1uy8vBO2C4B3Sy4A0SbSU0yMAU0nYCNsNdirzs7Hx8nPboRCIimh+ZH80X'
        b'UnbgqAQcQ3rqSEQEOOEp4OfCJjS1IwJ30OXpAY94geMU0lXuLkALWwtqHv7yyy9nixE/RsWwET86fEb6EvTERFKwV1AgzGIT4JozO40EJ8WT+e6MEtztAq8oHOUqNMKm'
        b'xRTcTwbPApsZM9YHzoEB2OeEK2vCKXiJ5M8CbXSLef6rYB+DdSqSQtMSBJfTa6KYBpoUCIMkCmAv1n+BOXA/zSD21uCCYqXKjiTW+FLgKslbk05j1IXEIuvWAPs5BLgx'
        b'BfsnQYGTmMXSzUaWtw9VOZLEdCvsH8TDa4ilaXFqesHW3ske7KSIBWA7axG52Bspb1rSL8JN4LRCadfAJuaBXRS4TnLhBQVdV4V0dweuQp2111NwI8kDuyEzXzu4fyXs'
        b'U8qR8ibg8fUUuEH6wY3ZdJ2NY6kCXlBaESQSBuT3HkCSegj1h2mxoI5tb+Noh9kAXGIlk1kT0ZaSHkifH+3PrnQgiXUFFOwhw5FffpFhmR0V0fZODrZIk1WxppDZHrXM'
        b'cmwkKWTo5U4UcijgNZYTmewHbzC+0i6gDUR18IIjRRRsYE0kZ5RMZKxVTwDQK1bibiSII8AlMgBoS2mkkAa4X2GH1wlpvosU7CB5pUmM8IjBQfuRGmfWBDIW7oU7GDVz'
        b'MTYDdiK5iQE9UUQU8kk6VD64m1fAy2vBNme7lavIKHCRYCMfBbSCqzU0FWbBfauYCYHDVnhG8MQKafHsV1mKz5A4Fe37aF/ptMJP0lw+jPldts1HLjYfzX6JoBZ9Ua29'
        b'/n2xRDlhK7sjOIh9NfSVUK8E9ce+Xtz5Bgvrof9PAVX3w76JWtyr76r84e27a+uqXl+jDlj4fqr4h0O/3I99u6nht59XDHwYKHp7Rl6RC+/r5WunHt5x8iPbRXrDd9sP'
        b'7PlGZtpS3Vt7sfzqlc+9CgO8nFfO+Hb7wzcn7T67JjU09mO3w2Vd0QfnqF2u/leX/9pbM95vDE6IqYwtMeRVFwfutv3b23/726zlD2yEE+aqL15zOOGR57jvnYT3J/z9'
        b'8plfrjU/TLi1jHuj+eGXsSfrOYr0z6tMr/1l3Stff9x48Pa7jr9rX3Rzrj46+08fRwXyXp9oLJP/uEcd43btE8vi2/PP5lx/r+6Lv9/6SfYfUwQL3v/2Hd7XPSWN/9H5'
        b'p9u3tsCP+iNnlv9n5e7JQ/lVP+/P95gTYZ108UpL3P3vTnA+Pkv9rTbkz7IrOT/oVcKzf1JE1h3z8buzMWJZwtfrvl4V+53lg1WVv/t2cEdLU7dGvk//84lsZfHtWz++'
        b'VHS37N7d464L2rP29Od59d9z/c/Pt//JsurMlm/3zQu7+4Oqd9W16i/n9poEd/12vvOlsODQQpbHlYUvH/r0l+OvOV49u2Li9B8W9NyRp73jma3/Y8CZxv6OxF9Krs6X'
        b'/sL6vjNxwwbij+8e7Zqezbd5gM2RLeyfCrdFFSBVNg2cgTujkOYGp7DqPgE7aIg4uLdeEA114FR2VCQ/GoHAFrQF57GXwKMF9PGhAJ5Hm8FHx4fwbCV9elgETjzAmqEA'
        b'HGajBtSwJYqEu2sIK2TdhaCVeoD51Gs5vJIbVQ97IrJgay5J2KDO12Dn4gHmblXCzNzs/Mh862y4ibBiUzb11INAzN1nwT54VZAVFYkahS1IE+9EonE8320KC+61E9K4'
        b'+cH1uYVC5NetIlPBuRlQC/r5jk+dz/z3EwVOeCOfpqZHZzsTmPMTpVwsU4iZy63Gccrok54e1sgJKNr8hVqIXNJxPvkN86eNbfby0+SZvPgo5+6t4Rrcw8xBoVrxES+d'
        b'qy5O53aE28ZuW9DuhMGyul667yW85yU0esWYvGIsRJxr6nBoZFuGxru9wByGMz7the2FZg8fTUTXkvse0fc8onUKo4fI5CGyEEIEHTBRG9e7TCvWlmvLe1cgBNf22WMw'
        b'LVYEN+BAck+yNqF7Wu+0tgyzb4BmZW94W7rZL/BASk+KtqJ7eu90NLB4XbzJLxoBBKEZhXikfoMTDcfMC0VNr9SWH7FlXuie6Bc/njajZ5pmmlk0SZOhDTByYw3cWLP/'
        b'RG1lz4uaF82xiajUz8gVGrhCc0CwVtlTq6nVcwbcLzjqHc0hfF3poXxtvl4yoLxQq681c3lan97C+9z4e9x4faKRO9nEnWygn8dNxiSgJn2N3CgDN+pxabQIlfp0F2oK'
        b'cVmNwT8ePbg9z968+9yYe9wYPcfITTJxkwz08whzODpOV6EPPbH89PKxLTCtCmJRmWd3niYPlR14sefF7rLeMgvh7JM6HBmDqjy6czW5FifCP/hAXk+ehSAjZ5Dm9Kxv'
        b'WGRkNmIG0j+HfECnFjodDgnXhR7M1YcaQ5I1mebAYG127wYLwfJPNfNCtAuPOOspA0+EHhNPpFcZeVOZNyP9DDMg93lJ93hJuHaaiTfNwJuGMsOBQYif5rU7WCiO74Q2'
        b'K4sDERze5jxCTgth5ZpKJ2hhI6LOOZ100iuMEVNMEVOM7qFtmRqRlmP28rUQbLTWKvqPzkMfpgvUBWKysjXzeh20c43eAjOas7PG2ewTgabjkWr25tJVZQbvRPSYvBMH'
        b'3I3e05g3o3fiQ7Obl8a2a7ohLMXghp/hqLRB90Hp7UBT1BzEm55deVovozsfPZi3+V1lhohUgwd+EF9qrXqn3vcT3PMT6GYZ/UQmPxHudD5pjskcrLwz+XadKWbeyNjm'
        b'Gb2j/mqZT9GyNyKJY85SbYYcxgrveKepT6sHvKNYOlYzyPGmYTxVkI7B8fUcc0dA/W8PWf9Fx617bIXEGacpLD7JHAE1gT1An5sdlQ0PAy2bQBsw5AVvXfnEBtZxdJe4'
        b'AyW7HEc2sPgKmHj2ErjK8dGGlv3v2ND+pRYNz4435lOEia/giZ+MMqBDF9bUS3j5pZMTYnl1cjoTH/0E6hMv2UqeXKJUyWW4rRqpQombKBfLVvDEFRV1KpmSp1CKlZJa'
        b'iUyp4DVUSyuqeWK5BOHUyyUKVCipfKI5sYKnUqjENbxKKc0SYrlUoojmzahR1PHENTW8ksyiGbwqqaSmUkG3I1mN+KcCtYJhap5oir67YqAq6mSrJHIEhYMrVDJpRV2l'
        b'BI1LLpUtU/zK3GY8HsUaXjUaGo7qqKqrqalrQJi4AVUFmrok5flNCBENKyXyMrmkSiKXyCokKSP98iJmqKrQ2JcpFCN1jfynMJ/FQeuxdGlBnUyydCkvYqakUbXsuch4'
        b'CfA0H/c3E5XUSKTKRnF1zdPQI2v1GDi3Tqask6lqayXyp2FRablEPnYeCjyQ8YHLxTViNIOyunqJLIUmJ0KQVYkR4RXimsq6J+FHBlPLjCVDUiGtRayAZooJNR5ohUqO'
        b'KbTm8WjmwyPVcpVsXGh8DZlCp6hNVUU1AlOgN1Xt80ZdUVOnkIwOO1NW+T9gyOV1dSsklSNjfoJf5iF5UEpk9Bx4yyTlqDXl/99zkdUp/4GprKqTL0P6Rb7i/9PZKFS1'
        b'ZRVySaVUqRhvLiVYbnizVUpFRbVcWoWmxYthtC6vTlaz5t86pxElIJXRUooVBW9kahLZeNOiL1R/ZVYzJTVihZJG/58xqbHOSMojczbWFj3Sd/V1CuXTDYxwhkRRIZfW'
        b'Y5TnaW681hJp+XNGjC2XUjzKXPOR5UJd1dQ8h8NGOn3Mjk/29XzW/G/TXS5BVhQJXQoPaRkEWQyvVawoZzoYDx7rIjT5shWSMUs1OiBEghp4TaGQ1PwaqhIZ+OcQcaQd'
        b'DDH+YJ+xuLkqWaVENr7FHOkW2chxbPWTHSOYX2tj2aon7e5svNrwSJVSgTRVFXJicPV4iPVytABI54nH77dopFoiExbIo583+if6fmbc49v/EUZ4ygd4Avm5/gCDK0Vd'
        b'j4+YPXNGwfPZrqxOLl0mlWGWelaHFI7UldMMiQSYN0suqa1seK6sj235H2BoBvy/qUyqxcjajKvyZkvK4TUk1uPohH/DwLAY0HKG9dwT4ypFNb8ubDJxreSxthvxi3kR'
        b'Bah4XD5Vyetpv+gZjHkSeYNEVonFsrFBUrFiPGyFpF6cMtaxRg2M8erHwVgsk72YwpsrWyGra5A99rorx+4DxJWVqKBBqqzGTrpUjr1UiVxawZNW/pqHn4L2oOJarDbR'
        b'mEqrn4q5fhIxZWSfk4L2BeNZhiehn7hBdCKeG23bsmIkTnlVSkj4Eilz/3Y3BcfQErxYz5WRlbnZzCVIANRJQCtoA30UQUwhpoCjYCMN7VpmRTgQhEus1fLo/f4+zG0d'
        b'VQtPg1fBTVE8MXJl1gEO0HeWK8A+uYCfA7cLCvKi8UGhG9TDnQIrIiiQ4wv7RXwH5lKvlTULbovJyRaCrTEvTM7JzxXmwNbcAg4RB1utBOASPEtf3sHmItAtQNXwtNso'
        b'xASwnwX088EuOi5GBE/EOIHTzB3amBu08lrmnmy3K9QxF2Wjt2RFbvAsaAat9O57VnQk3CaArfnFiTlCirCBr1JgK+yrU4Xgme2F+6fhlrPh9twC0Ap3xkAN3JGFRk8E'
        b'TmBDjSfoVgVhwF3yxNycYvEjyEK4A7bgm9IQAWfqC+CSKhwfvc4Cx5nWjsDjo3D0vWZBPknwwTUO6CkBeppApVXwRm6ONTg/pnN8e4kAQ5Zy0uA5eFk1Ec9vIAC04tNi'
        b'eA22ovaic/JhSxTfivCDe9ngMNg6RYVjUtfDg6lgH1qVaBoqOx9uxUBeHuxYqHelW6qHW8GNJ5YO9IKBR2u3DuxlrlM2w064ZTbYKorHV5KI38B2tBT0ZeZZ2BmFF8vx'
        b'qbUS+DM3iB25fHCJLYrn0LeO1UADNzHXPQcjhOlwH+y0RqxKxPrBVhWXZhJ4OrMRnHxmbR0RHgYAl8HNdU8uLhyIRKurA718iu6zjPQQwTPu4EK9FUHmoSEWgMvMhVFP'
        b'I9g0Cx4WgQsEfYm7AugU9E1OmciNYQm4t3EMT3Tb8K3oJtPgMZbIGu4T1bMIMpfAh/jzGdJcgqemiMC5SSKo5xBkMb5V6ufTOFngikAEB+A2kRwhFRLg3Gxr5hbsRCE8'
        b'JIK74HERvICQ5qFWCHiOodceV/AyPDhTJMJXroeIFSS8Qd9BxcH9k0FrlkiECXmYqAEnomlZjV/hSURhWV1SOyVWGE0wxD0dBvZ55CpQG5lEJtgET9Gw5REuBBLYSbFV'
        b'V0vlsXMIPosWJ3j0hUZ80doawwuiaWoDNRTYBdud6CXOQNJ8yBu8nBstjMRLDM6yCed5rJoEeJCmaijogp30Wda1WA7BZpPgwIJ6tBR41A7BLiJvcOoR2RrABYYE2zLA'
        b'HhHYmzSGbDfAq7QEVoOroOlJCeTCvY8FEO4Eu0eaB4ejVCLYF/CIwqvTmdvug0G2IsQwj+nrsIRm+MRk2JKbMx+t2rhSOxlsHLm+loNrnlGPFiHpRfrbHvDKEkQGemSH'
        b'HJ8jzIXuzAjORsCOcNj1aL1gJyNylUALLufmpAeML+QCpASZkDaklw8gSrSIREwkQnUqYhHcAtDCAbAlNxvuZwkLopFQR4xezviBZjY4WlozsqqIkY7iG3R+UJowm03Y'
        b'WlNgB9gD99C8MBDsRCB58o618nT+6+JVBHMueQR2QC1eS3Aoa2Qt4XV4gJaRNfCAK8MmE3zGsIlfOSOXexDHHITtoFeQI8wVRhbgr7c4L2NJFsGrqlA8nv1IGV3JhVsX'
        b'zh8T1oFIh2MH/PLYoAOeUjIquAm8PPPJ6I+Y7FXw5KPwD3A0jwZcj2WI0RQ+SCPtiBljUyIrOOAUHKhgLEI3vAmu5Mbkwh1z4NnHkTDbwWFaVQbAzfVMwAgYAAOPgkbo'
        b'kJHMCYyiu4HE4AATu7AcHGURI6ELryJFH4m7uAnPrmbIg4gDWqrhWWw6tubh+7pcTIx4sMcqG27LoQXAdzK8iUaTFZVTKLQi7HOp4Bq4P9+eWbk9gStGYitGAyvgwWBn'
        b'uNMZCSx976yDRwOZmA3Q6YfWCcdswF3gBM068UsmMYE7I1E706DWuXEhbVqDwZ6gZfE4vuiZ2KLcGIbz9VkC0FdljzyCEqIEImWLRA1XWMFtjuAVeGZUp/T5MypVAw+v'
        b'tgL77eXIE4EnkGMQD3sYTXYZ9oBD5Yj0I4HlISPexXf5NoQLUvqxSaICw8oGxhdZO4EN+uYhM7MH2QOwkyiLG4lqkFc6IK9jK+iLZeGJE3XgIrimmk9bAnhmrgKtCGzN'
        b'nlMELsSWFEM1/TWeaGEEmn3kSBBJCZYPddS8LDxpmq5RdXOyonAdkpvcuUWwlU2Am2tdkSh2Qj0dNPJCzIi/VHVyflzMTIIRvFa0phdswclxCQg3wZsjYThw37pK0Ics'
        b'/vUEbILmIMW3YREj1gelSAb7ykBfQj1J672zoD1BlYCq+OC0H+wE6mzYDnfDLqBehZJWNPMzSeAsB1woL1aCK+BwObiYSKKVt1oI+ri0EoxsWAv6Mu0eN7h7HeITOlxk'
        b'GzwFunNHTaXVDNsyKpIP9zCW9gxUV6P63qf1+jrk1mEAbhW4wTD0BnBtjMCD00ii8WReFICDaJr9sOXRNNORx4BdQngd7G4URNuD/eN5KPkNjKPXnwn6feaO45+Aw+F8'
        b'Nk3KZeAGS9QAtyStRBo+B8+uCR6lGZIDtsADqWtECVa0SyJxIujItApZsYgXm7AKESMNWVppDhM8WwFaQB8fXEyAeoK2CBcmNPBJehozQQs8D/qABmxPiEOVs5BnME+p'
        b'mokdYdBqZY9ckm1oubfFwJ1rwOUSqHcE5xPiirJGOa9YOK/4aXaC28ABO9gzx49m7iXwBtDHo8U8hca6jlgH+uERuuvC4nCkpLTrksB5iqA8CXgSXgGn6enB0ynwSk4A'
        b'OIXsx0vESy+A3SohZqB+sClEQX/HqDgCX81j/Th/tO/ljXTv84XWYNcCoFVNxg1tQmbIPllYkA9bhfNGJAS2zM/KmZtVykwGnCiC6nxhdEFeIYcAx6HeDrxSkjziTXnB'
        b'HtgMN8Njo1/4SIc7GBt+CBmYi7BpNuLaM/gLXN0EOJWYjtBoe6ADncvgXnj+afbKRBPESixg0Yg1cRCOZa5j1XTjMZnI7vQ1wEuOAH85koKXyYQpiGqYraNhv78CXqp3'
        b'hhfADitU10KGIe/hMB2DKDVcaKUUbGQz//xh5RnPN2WLM5VVX/1uZ0hBT0L23tvSe2l7DR2X3O1+778oIDeJd/RUQOjJyIX1rfciesQbb4NdRxfNVLd6NaQneej8kvRb'
        b'/G8SNwet9cMfdL76/b5vrtduXf7m66LPp32e+N36v1u/3529wPi5zYadVletRWvz4pZu/aSQmF+wrGrvX6797pfI+fq7p5VTju9g56jzJp6d+NKiK7O556fCyPlXbJdx'
        b'At8N+HYyz+ndXcEfJn29ZPbkOSHWO6QHP799k3eu5C37s3/4zOlbfuFfI9tSV/9gE/hR29Ql6V+/k+P08weGdOi0rCNU1u7xxuxJrKWHP5pmNePmsdXvSNdveT+9dlob'
        b'OdR66YuoM4VtxcYule43Sw/8R75PV++55Yv+0/VEctHvJp7TnlVFd75Sk7zT87XvRVc/8Z2yw2x7+9Af7vo8uEl+uThuO6f8Yb115+sBPecz9/OrPz1adH9qOSfvs/PH'
        b'3qk/+XVR0jHr1LfbCg/9ZUp5obO+z/dvgvLPt5vfXvGbwqzJh/kBc+4uz9nU9UpFzs7Xb34o0dt8OcUpdyjd6W25c3td98A7ri8EDeRYpt5SD/ve8rK5kaWfpS+wULe2'
        b'se/byo7U7zxatvrE1z/dmaven9C8JGTJnLtv32iZbx1ef2Zd4tsvcHf05m7R975m7Ru5/L2Vl7s636nO9xCHHH7hqxj/110nz9PdPaRMPPI69UHMwFef5UQKBGumD3+b'
        b'WrLg/oVva8Jr117oeHdR3J9KxOxSx28uLjMtf2PwzYVfv9Fz6fvp/alLIt//cfX1053Cl8T5whdOXLHTJf/pwvK/vGjzeYSb1KPGd64LOHmspuebnJ8mxgxvTSzk3pvR'
        b'l936++X5hbs/6Irqbjk4zW3xBrHzkveMH3ZQf2uf6Lrz9yeODfcondZfnXnz99++eUy4OvTyjZ9LAze5Bv74BTw1ac6Nr6LCZojZS9L5wVeWc/8+Rfh6p76tTJN02knQ'
        b'eUGW/ZsVPl8fO/pus1/mu15L7iseOPpXHAgbntdzfl7n+3X3Uvb9Uid2WL3Cd37du8s3yS07HhztE9h9NywwKq5qdn5f8Ie3fzrL96jjLSu989f9b/x2f/Rn6z661914'
        b'Xth38rfRZ30PrY+VW3nJPpYm7/88/8D1NsOp5mN3v3ebFnVuxTVOxldneyJbL6l+eH1D8LLPQnp5Xxn/8PH0okONE1qOzLuj4pzOVl6YvzXnVC15L+rtN2zfTP7BRjXV'
        b'94vfVl2+WdqqfsP2t3feTvzAv/Dznxy1YYs/n2+e/136m6ei9n8mbRDu+hzcfWv9quF1d7/6zig9WTbr/ZCLP918z8v8SqdFfNY+fUCzakmD1zeBn/1neNBpt9Sv1nx4'
        b'YOVlzakA59SCuIS6b35J4376+ZW1C5Z9uUMx2/C31/70c0ti59vvcz7d8GON8s85s4S/TH21/MB3ft3rf3Pow1+I1E/3bc5/i+/0gPYoX4bd4CryAfeNxEghdYkVJnK9'
        b'vNDuNAtZ2YN0GFUx3C0XREbzwQl4CZkjgrBdSIGjqYXMlzw7qYnIjLwsiH4mSOsY6KLxwSaxfDQMC7lMrzjSYVgdXKbycBmVGxWRFYBc3cdhWGc49Ffe4JW6iJEYsccB'
        b'YnsL0cb2aCYTjnUS7IC76HCsbY5jIrLocKxgGd3DBLAlR1CQH4VM1tEcuINAXbxKNRQXPMDGZjo4I8xFHmmMEHtzVyY3UNEN8MwD7Nzaw3NQPRVtjdC4Hk3MOZa17KXa'
        b'B7Sqb81OfOxGVGUiNwJHh9F91oJLiwTRfJpaVjJ4Apym0H4YXqNntQbp5RtPfZNv+yy07d8D2ulZIR9xB9qEw6OwD60Hcs7qadtGER5T2ayVa/i8/+tgsn9xosDuzrOn'
        b'rUxwyujnia8m1ionJ8Q2jn2hA9b8bZmANZkV4e69Z3rHdKNbiMktRJ1h9vBSzzK7e6szzT7+6hyzp5d6ttmbayGqKcdi8hvmTxvb7ObflqKp1GYa3SJNbpEWgnSNNvuF'
        b'a6bq2EY/oclP2JZh9vLbs7Zjbfv6rvUI3jdIO6Nb0GaNSjGwv9mda3bzwj1rRcy3d78hxJRrMWkOizy+/NByvZtebAybZAqb1F7YNqNNpZEMe3G17I71bevNfjwLQfnE'
        b'mbnRBm60TqVfYorJMHIzTdxMAzfTzJ14IL8nXxdq5Maa6Ai04ZgEM19ojogyhwtQ6+aoWLMwzhwdj1NBjDky2hwVbfFxDPK1ECjRcLo5Fi7hG6gN6fHX+JuF8RqOZoXR'
        b'OxI9Zp+AkVK/AG2oZqpmqnnm7NcFQHCnwjiz2DSz2MidrsnURhq5QjSshcaY6ehB3aMyvpEbhR7cgtDgE4MeHEHF0VR3O3c7o1LDxByDD36Gw+K0K/ShA9QAa4DVHzkg'
        b'GZxxrfpO8JU6Y1iBKazAHCHUifWUrvK0vTkkWpuD+pmjX6kvOd1oDEkxhaRYrNl4Imw8EYsdwQ3SFhj84tFjTpiMhhFt5MahB0e1yQz+CegxJ6ag8hgjNx49j6PdkqZo'
        b'Mg0TUZkIPY+LHwH/dYQW3f4WypPna+bydQkWFsoNc0O0y7XL9R76lQOuekW/rzFsqilsqoWD6ixWhH+wNsNijfM2hH+ottJii/N2hH+4jm2xx3knwj8SteWM8y6Ev0CX'
        b'YXHF+QmEf4TO3eKG8+6Ev1BXafHAeU+mHS+c92ZgfHDel2nTD+e5hH+YVmnxx/kAZgyBOM8j/KN1SksQzk9kYIJxPoTJh+J8GBEabg7nmyOjLAL8TowmGrYlGhPYtXcS'
        b'E5zGcL6F4PiEmQWJuhS9ZGDGgHggvX/5YOId1zvxd9xvTzEmFRgFhSZBIRNMaA4J02RqMocFMXqb06mjZaGaTHNUnD70dN5A+r2o6Rq2ZpHRO4KOmdTlmMKTDeHTBmYY'
        b'wmcOuhoD0jUsRNagMK1El66Vmnix+lwDb7qGYw4M0Zb0Nt4PjLsXGGcMFJkCRVhqIocnhurIg+GadBy7WaGt1FYesUfQAYEaFu4gvXf5/YDYewGxxoB4U0A8klWfSDQP'
        b'PIf0e0mzDUmzzaMNWFgE6uN/jzAcITxnf9JenzkQ3J8zSBojZpoiZnY7aqy0HDM/Qeennzcw18hPN/HT0UQXdDuZo0X6GXqxPv30clTwotFbMJw0BVFy5sDMfun9pOx7'
        b'Sdl3QoxJhaakwm9YpE+Cxh3Jp0+kLt3M5RmC4jAbe/trZCZv4X3vhHveCfpSo3eKyTvFQD9jZDhU537PT2jwE5onxiNeR0NPyCbNucWo1YQSHLIZXIpDNlGKQzZLyeGR'
        b'ZnXlJu84fZTJe/p971n3vGcNqoze+SbvfAP94A6iDT6x6BnmBhzI7sk2hKUNInWUZeJmacjh0Ahtic71nNdJL73rCd/TvgfLjpSZI/jnrE9a68kTdqftzLQGCLocfiF8'
        b'IOh8JK0DVFdkxrB8U1j+s/Kd2ZOqScUht5laIRNyOxyfjF6QuokxcGNo3TLN4IOfYW8uHl2EwScSPehtOCDaEBCNZhebYp42c3C2YWoemnxsPp58YAGePErxkhaQw0Fh'
        b'bTntOcM+ARaCj/U0Uu8bOjZoFUYvgclLgHjLI0jvftn/gv+AyhiXaYrLpIvuuL/j/xt/w/xFxuzFpuzFdNnvvXlmL38cwomaoUdgiJl1x8sYU2QMmGMKmGPwnmP2jTSg'
        b'R5Bn9M03+eYb3PNxWOhig0cEeszuYQb3MK1Kt8QUPtXoPs3kPs3gPs3sznzHPtToHmFyjzC4RyB+aMs0B4XS4/bjaQNMfrG/3usIkH6CyS8BW7Agbek9L77Ri4+Do6f3'
        b'TNeJjH4xJr8YC+HuM0mfcTnnQs6A4nxhf+Gg+F7CbEPCbHNIxPGcQzk6xcHCI4X3Q6bcC5kykDEYbAyZZQqZdT8k715I3p0SY8gcU8gcJOOhkdq5ujhdxWjQ8UCQMXSq'
        b'KXSqhXDyZxItaWGzg/JIc3zyANkfMZA5GDQovhV6LU8Xqs3QZjz8MDwOkRQBjE3Nkck6oWFSFnrMEdMHw40R2WhVJ+fi9UQpWltBHs4LMAIZilIWRnv48CFSynFJevEA'
        b'qa/otzNHT9atGAgdJAepQeoa3xidYYrOsHBY/IkWAiVaDoIOidAlHUrVpppT07UZBn6KMWSKIWSKOZSvm3doiXYJMiPaDJ3PwcKH3/jjKfEwgqMpOAkL1GRz0iQtW/ui'
        b'kSfC0cn+BppfTdwYfYKRm8y8GenH7IM03z0fgcFHgAONXzB5R973jruHhDDE6J1s8k42eCejzPD4qzqMf2mBcgw1u0w0uEzUJuoCTMGTjC6TTS6TDS6TzS6eexw7HDUS'
        b'o0uIySXE4BIy7Oajzlc4IDfpPX+3uXHs9+ImznOzZuKHXYbY+Lb1H4gb/oddOhycvHQ8F06eRDz+GQfadevA8IeIkQBjMZskJ+Do4X9m8k8LRMa/gnTANpG46DSDxXri'
        b'Onk07Pg7fOCzh5DgH0AjFlGV5CJWJVVC2C7js4Zc6JtsOspXnimX18l/DGTutmlqyEeCdiWVPLGMJ8H10QV89pBNWRkOBigrG7IrK2N+oQzlHcrKVqrENSM11mVllXUV'
        b'ZWX0ejKR4TSx8elV4zPd7kSDVeD9TNOjf8MOcYbRh8anLxxAjxfotneCl5X2tmjXVAC08LJQPrK9iIEHrDiR8DKfnCV9oFnAUWxCza6U9q5vzy6EsS6v/HlSdufMhuo3'
        b'iy9d6Fr/0Q8XmwZWfqx+4L65bVJaaFFotK64tz5DbT+/kT+9w5aTE8nrmD7l+73Jou9LPvivS+X2iy8mLt5Q5XzsDff/yvA//JbPKYPupWEvsPdc4anjRYtu7Fiwr3hd'
        b'5M6s7m8FB3/2+Ex68K8/pK6Xv/K1/2s/v33aK7Fc+8WZ1om/FP1yZ8Ffrm51z3jb+dhHn+zfq5r8wiev+MZ3Sj44Ffui4aUMq7+3/yX18sebP6z36Zrjc5ntm7Pl1MdF'
        b'VpWGYpfI7rOr7rrM+rQ9eKt33A72edu3b4cU305YpD5THXwpOP3LtPDz9h/eDqhsuf5F8PcVTRrIW2kDb7tun/B6bEHvYMix2Faft8qdvlswOHG3frvH6XLHP8W0z/8q'
        b'0jwYdknfus/rPY/i9k3Lnd/UHBXvWX5/H/vDtJc7lb7Cz2rf+ejMgx9ruoLuzdaVzV1evCf/wsJjZ1y+DT2c15Pz5/fWbWh4S3FX9OUebye7xj9vefNBgcc3a7vevLWj'
        b'e833Tm/FrZZZfcRnP6Bvz3ZXr4Xb8kgC7vIkJxFwB+ifQu8nJSvhDvp3liapRn5pafRXli57PcBn9FXKCPtItE2l77KPg9ZHUIGgjw3PrYVXH+AN2yr4SqoCnMkqEI5c'
        b'niWBNhbhCttYQA+1UM33YdSBza8m/7pNJT4g5aXRn6ZnPsxuEklWTZ24sqys8VGO3kcKWfRvyjxkflcminD0sLCtbb3MzhPUirb4lobtDZqgrevU6zQKjUIbrxUfSexu'
        b'7G3UzenZoNmgD0H/5ANB/aqBOf2rz0f3Rw9mDGbcmXAr63bWvfg8Q3zeh96+mniNuDex27bXVptj9I7Wexm9JxmmFhi9CgzFpYa580zF8+95zTd4zf/Qk6ed0C7rkiEN'
        b'jjxT7wUkco8muLfN6PJQz1TPfGixJm2RdzchsE141MEgnGXkzTbxZhsnZJkmZBkcsmjjZ2UbYSF+NXFh2yLr96uJgw3Pzuzg3OZpYeGcD1dTxeTC+LokJidKGrBicmnp'
        b'g/Po3DCNwcE5GoPO0Rh0jsagczQGziGv39EF4VgzeV9/hDWSD49EeCP5hGSEOZKfQWaQCJt+s2GwbZk8jT2Sj4ofsBqcZ3b10lTpksbLWpwxIDGaGGy4aOM1wRvVMY/F'
        b'3moiqkKJwSbA4pJH2uKv4vwf/llCEXYuZlsXtVebQpPYtsJgO9FoO9GECE2tZtkiV/hflX7DIuyCUT/4r8t2Twubrlpljd4sFGmLtwvPJPvWfIP/PMDJKN6TsLRfsXXG'
        b'9JluBHDznSlkMX6F+xCFTNI/z6sYV87dx/E0Hnsb+NtLj6Ub2zzFlVFXg0+SLtg9+Lck/1QX5IhtCnHFaYYNSxqqbeYoXkZFUftqa1unOW1K8864Od3GvHGXt2HKmlda'
        b'zw/eLZ7S4X8pub804YXi7TNmglLRG2u7Gz777bb5df6TV5W+u22/SVT7qTg3MKz8p5IZi/+senPlhQuVFyqX/LTeNPTVnKU/X3/91qBLhrq9vNlh8vdF3KJhm/QWt7v3'
        b'31rYyZZ+NnP7wj/8mZXb6F/qAfjWjIFJjME/5zkPtBQW0jf31oQ9uEBBHbwqZA4sr4L9ZG6hEJ6HCATsm1gopJDhuMbCd6HgOA2zdk0A2IZjG+gb+lZUvhfstCacJrAC'
        b'wDVw/QG+kZwOOsFJ5nu3hNXc9WzKBuor6cPYcLANHs7NToIdj38n1J5PIdtUzxxDX4N60K7Ihgeh5qlfEi2F2+jG5eA62CfI4RAk1Hnk4kt6PdDzg59v0/6fH6OOKx3B'
        b'o1bwWRs4rj2UyqRKxh4yOdoe/o4YsYdIaHwJjltTAf5ndnS/7xhwzzFg32qjY4TJMaJplplt15y3Kc/gGnR0kpEdZWJHGdhRZnag4cnHzHZsysb/LFZrORykQv4fpY32'
        b'hIN7U+GYb1Lyhlg1EtkQG3/fboijVNXXSIbYOLAU7ZCkFSjF35kaYimU8iFO+RqlRDHExmH3QyypTDnEoX+VbogjF8uWIWyprF6lHGJVVMuHWHXyyiGrKmmNUoJeasX1'
        b'Q6xGaf0QR6yokEqHWNWS1QgENW8nVUhlCiX+os2QVb2qvEZaMWQtrqiQ1CsVQw50h/FMYO+QI7ODkirqJiXFxg3ZK6qlVcoyetcw5KiSVVSLpWgnUSZZXTFkW1amQDuL'
        b'erRPsFLJVApJ5WOdTJ+9L/3VD4/HqNK80QRrIEUC+chHes4HMYszScpZWP39z0//afobm8pbDrYzJhK3JjrNiGX9aDP6o6RDLmVlI/kRe/Wjb9WTP1TNk9UpebhOUlnA'
        b't5GnYqlFez9xTQ0ytPQCTcFFdoiH5EoFDr0esqqpqxDXIPYpVsmU0loJvQOU14yy/OPN4o82U5ndZapcTjAbWsV6lFhYJElaKDbJRq4gShwIe8cmaws7x4p0txBj0kUO'
        b'hK3rfRu/ezZ+mhyjTbjJJtxCUGSiISp1MGww7FbE7QhDVA56zDYuZjtPdZTBS2S0SzDZJRjYCWbCxUC4tHkbCV8T4WsYfejh/S8B2cAb'
    ))))
