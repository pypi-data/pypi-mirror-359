
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
        b'eJzVfAdYVFfa8LnTKEOvQx86w9Cbig0UlI6IYpc6yAgMOHdG7F0ZRQSsg6KOHfsIFux4zmZTNoUREweSbIybtrvZXUxM38T/nHsHhYTk2Tz/933/9/Mkx3PPed9T3n7u'
        b'ee/8BQz545r+/XIxLvaBMjAXLAJzqTJqE5jLkXEXW4Bf/JVxzlJsTWlRxuUAGf+sqWcpoC3mcXCLoIw3CLOBws9msuc4FFjOt9gkEXwvs8yflT5lhri6pkxdJRPXlItV'
        b'FTLxtOWqihqFeIpcoZKVVohri0srixfJIiwtZ1TI6UHYMlm5XCGjxeVqRalKXqOgxaoaDKqkZWLTmDKaxmh0hGWp15CVe+P/hWSzPbioB/VUPaeeW8+r59cL6s3qzest'
        b'6i3rhfVW9db1NvW29Xb19vUO9Y71TvXO9S71rvWierd693qPes96r31A46lx1ThozDVmGpHGWsPT2GosNY4aK42FxlkDNFyNncZJw9fYaNw0Lhqhxl0j0HA0lMZD46Wx'
        b'L/fG5DVf7c0BWz0HSbfaxwJwwCrvwWdc9xmsU2CN9xqffOA/QmsdWMadA+ooTFJOTulQNtnj/x3JZnkMZ5cDiVlOlTmu/7CA41fLIbUiqxQbIVAH4modWgdvowa0NTcr'
        b'D2lQY64ENc5HTekzp4ULQHAqD92Fe2MklNoNw9Zy/On0bLQDbc9G2ylgCTvV6RyoH+tZSg2Z32Fw/nW42GNfj9eAyQIwqfiYGGaYdBaYZEJMMmtMJltMMHtMUMdyB4Y4'
        b'WGq2Pper1RyGONQQ4nCGkIFawzER52etv4c4WSxx/JUCYOW5kwvERWGdUxIA09hRxQG8pA5CsayelaVs47Foc2DnVM0DRUVhuoxYtrE9mQ/MwRIKJBWFtbgUgdOgyhI3'
        b'5xWLeE+VL/kB8GHwF5yr0R/Nmk9VEdWaEKyl9GZAHOWmWP1lTGfNWsA0D0R+YbvblgoZAD4Jz2Y/8owE/UAdiTvQaXgY7cd8aojMCwlB2yLTwtE2eHpGSEY2ahLB/WER'
        b'6eEZ2RRQ2FqML0KbhzGEN7jnEsIQLsMQwgxQzn1Ocu5/H8nNfkFyIUvyydNsgScAoiiBTPZVqQdQh+FGeDg8Bm9zuzQTbUdb16CmrLy09LD0mSAmM98Z7p4BG+AesIhv'
        b'hg4rQ9ROGEGGtmXGwms8gG7BmwCeBkvUArUzIdlmtAHpYuFlHnCMBvAgqJSjnWpHlph30fnYGADiFwG4F5SqFGoitXCdOCgW6dEuPgARIAK1VjPr9E63BHgm8yjBvdSg'
        b'6GCW4WfLHUEA/jcqJ4xKys8D8vkvr+LTy3DLp7qkA6+NO7h+65Fdl3Ytj/fnio5HlR+IjXJ6sifpuyT7kzmfhCYIBNptQbq/OX1S5SrYYvlHv6ApW5z2Wv6xxO6NuX+a'
        b'hsAM4Yzel9rg3pdeX0etS3SbbjyRFLfS0l9bnvVhc0la/bsfvGSlsnWE4+9ZtWnFfwU2Xq6GxGwJ5ymmJvBAbfFCTDxJtjo8FAsKB8ArY5xhPc/cz+upOwawhSfh3cVw'
        b'L6byNtSEtnMBbwwFL8GNPhJePydEorTGQC8KmrBNvG7duu9dxpUra1bIFOJy1khH0HXyctWEfkvGAheWFatkK4bUOQS5FhffrgNPUihg59gc37BCm7dt7Xsu4h7fxK6Z'
        b'Bt9JvS6Te+wmG108tGUtVfddpDrVfZfYdpVmqtHJQytrydWkGp1c96W1pGllukm6PK283bl9id6+3V0/syu6K08/t8crqdcpWZPa5yjWOfc6BvdYBX9JpE5JxE4i6Ocv'
        b'La5Sy/rNCguVakVhYb+wsLC0SlasUNfilp/tVEAUXUz2qrQhjba4GLojfwIUh4vv1oGvJ1MU5fihjWtD5TrhAIdPOfUJHRrGfMiz3ZRtNLftM3f89gkf8O0Gn76nidTs'
        b'FPiBo8JwbilnJP0sI/rJIf6J0VDquYZyhhlFrsUw/cN17hBd5KzhmjT0Z62/rqHPF/BcQwU5amIpzdZy0S5sSsJtUSsIR/vyGI2Dp+BleADtwiFE5CIrEIk0cB+jV/7m'
        b'aC+rPPAOPAAiHOFuuXj2ZS49Gne+37+MqMWRXZKGFop7POpk1PnyDfqnJTe1iW4Ns/O1Y1vPdI8L2pKju/D2tAVYsP8Kpm22aP9qkYRipBbemjtfmjETXQ9HmvSsHD4Q'
        b'wkscdDAbdkq4P+cjiW0GmdgvZPlXXlVTrFox9IGRzzBWPgdmUMDZfV92S7bOX0f3OkmxQNk6GUVYBluFzfw+R3dt/K4JPVa+SrsXsqUkJOrnl8lK5ColsR9KxxHkiREo'
        b'Vp5ciTwNXYJ0UKC+xwKVjwXK/fcK1C6BPzgmjOAyNinN3CG1jKrggWnd1bNlJ6LVZELYBTfBjXQMvK1KiOIBTglAJ9HFGAYhdKKz3IZbywNR3dXaqPVKxm7aOc6k4UZ0'
        b'GINTgCMj1rLJgwFfbOFS6AaW8UAtBud8ZcUwPaJQSY/xwcBcwFkE0FmoncYAW9m4FfaCdVikulfPFk+YzIw9HzUG0VboimoUWYoCoDPwYiQDHrjcY56Oo+GBJAzuIVWw'
        b'JvxmcQUdT2NoDuDU4MFRIzzNgHMcPCNVnGYeEHev1tpq7NUistWbGfAOjbZEo8vxZO1wI0Cdy2ErgzFhgbfHa0CL3Xb3alHo3+LULmSCncoSGm6PJwh8jLAJoMsB+Qz8'
        b'3jFiCxFXxwN2eAb74tXsgs7USenEMCUzPF7QOdgIdzPgLfP8ZG9R7YT2q7WjahaoidCiVtQCW1AnugHvqqPJlrHzQp1w40oG5+UJgdTfKT0h/+rZozNKGH4tQZetMEZX'
        b'EUbAu8buCV3OR0cYhLUWwfl60EUYsFpk4+TBIKDb8MhK2hHzOJbMsBagC9gVtjMIjpSEX0x1EybQs+0rzBkyTSlDp1BnIjyIZ8BMg/sB6oJH4TkGY0ZGaPRn3Fcwxj1a'
        b'NKd0FkMm0VTYjjrz4QWMYYYxDgB0vSiQgc9JD1v5MeghfKNnC51XM4EivIUZuxl15qAO2soS7wJdoeIQ9rkMStLkSOclHCNGwVN4PfZmdlGImuEOocMMJSOk8CRA19Am'
        b'1MAgHEiNnvky9YgwmzZmzE9kdoHOoENwkxDA6+hSPMHBISnXAh5iMFJsYuVXqM8wxj169iz1aMZuobYJ1UIzuMEyhnAP7aUsxsYzXMXeMl9oj86jqwyP0GaK8slgaXsj'
        b'poqGW9JRZ50N2cYRSgq16AhDlMnwNLxJj1VbWCM9Ge8ulbAQ1bNo29DVHKHztCVqdBXLKrpEBaLzWATIZKvjo2l0FbUKlSqCpaW8i9BJpmfiUthFw31LVeiakHQ1UtI6'
        b'b2blAnhtFo0OhNhYY2Jy+dT4FLSR3dJ2TIZWWuFrY21DAa4FlZQtZzosrUJpaZyN9RKyny4qAl2Fm1lzcBnHPkeE8ORU61q4nQe4/lTSRHSK6YtCB9BBGh1Hp5WMOtQC'
        b'dN4JbWV2OwOr3nE6BTWrEuIEgFOOzUIQusag1aKtebQINmH547NK14GZ18GyFW5PpdGJ1egS6rQlFLxAxeWi28yQQWhvCC1bionBdp2hYuFNe4ktw8HXouMiFWCAqCut'
        b'HRXkyTROrU2om0p9ixvv0caCD6KYxh/Hj+Zji8/HikobqSzWFG4MGDtrAcccN2JI6eQKptF+/DjpQq4dH+soPXtsSjrT+EHdxOg7lAg3YlEp0+YxjZZlyYX3KDEfayZt'
        b'pD+VM43jpk1WfwRCcCMek/KwYhrzglPVszl447V4nck2/kxjqmJK6buc0bjxHq2tzJMwjb01abOaqCTsHrsrjeN+Ytf56pIsbh53Gh+rT+XsrNcWMI3XcnLWfkfNxo33'
        b'KrVxk1hFm5CXN+cfoIiPlaBS6/PvMqbx3qTprmKqAjfeqxTlvZzFyFEJakTNNNwzS2hJhMKKSoK7bRlbnbZiprB6vNLGGkuRPTUeHkINrFBsho00tku7lqFrddh9EmGW'
        b'jp/KcEmCdnNpuHcS6qTRZSKWuym/+QskPGb+MvuX8RFwtBneaN3sUqMT0yha9apPPzcJO8nuGm2RahTbOOe14GfcNNx4r8Y4x4sls2/y66tduNPM8O5rREE/Jg07tvAH'
        b'o5JyXOzhm86RPOYMCcr5/xOnRQH4eWAUlKP2wXV30Qp8EGmB13PxabgJbU3PjkBbcajtUsQLtkOHmc2hZHx4BMY8LK1Zbn5R7LGhZBQ+PALzUWZFRVnBQfMBQ36fSLgr'
        b'MzIT7chNx6dIS7QbbeIs57mxZq6rCm5C1z1hJ9ZcfJSh5gB4Du5YwnQuQdtcpCHhofB4FdJE4qDIahHXFm4UMsHbMrQrH3bic9GlXJAIEt0ClWQBzCpG+fPwaTVKbZNU'
        b'lDU+uYZt1ArwCRgk2VvjEzBwmwoYWYL7sXoei12GbkaRp52gGF6PVvsSuUgMyGQOEE3khUAmbIpMSUqH50MoIFbxbabB9cwiahPCYmvVJMSBu0EJ3EmpybsYeANuWyrF'
        b'x1jmTcLqZfhUm45PaRIu2g6PZbFB5mG4bVYs2pAbQx7wGU2Jg0zGBetDq2N90QXYwSNQoAqdQ9cZlHTsbo/Fwia4O5bgHAKLpInMuS4TnlgVi9qTYzE/4RGwONOO0YYa'
        b'uLEuFq6H6xMIuBaUzeeyq9PAU+hsZgba7ob2oIYcli82tdzROPLdzmzLJbQsVh6YQFbQCmTw+CTG3S9LgEcyszA80hREokYpBYRzscVLh2ckHEaX4G20AZ6PhdvhrQQO'
        b'IS4oh42ubCRyEu6Hx2Nj0JUEssoDYBHSwvOsCOyArdX4tLYuCzuqbD7geVPw6BJ4nNkEvAb32cSiLocErDuwDVSIypm1wCsBaJOUMGQKQFtz4HkesBrPtUXba1jytteE'
        b'xMLWTHiVPOgwFfdL2Bhqu10dnutYaFYGORpy0R0KHiiFh9SZpLNjbCqdle7rlp5NXhaZDulZeSERktDsCEk4xxKekMGTeC/HQ0LgaRepBO5Gx6VOcLeLMzruCk/hw+g2'
        b'Jzuoc5BUffvs2bMiRg6n2QiTisLGLB0DmKXl8UulVd454Wk8wEui4Bl4CW2VOJnCtVK4g4YdwdZKNbFShyj/SegGg7UyX4ojFHTchu25SkmEYpbmF+FVT9QpXGjCuUNJ'
        b'a9A+lrC7cNizhUYH0S6Mxto2n/FwLyNnk7E0XcHuOGCJ2pLEkjcpcdoclkRdWCeu0tGZ6GodusxnIg9fdJTPdNqgjgBsSS+Pxl3WFOP7Y+BOyC4Sbk+BnULOWBshbMIm'
        b'eC41jz+H6SiEu2tpdMNVZVlHop/blOeMOmb1sSRUoDNm4w4y0XpKjKO720yQhY7DliV4qr3wkEqJLpNI7g7lMR1HJwz/98MNsBUdRvto1KESAArrA6Os21iLr8OR62Uh'
        b'NiV3zK0tAeCOotLQGTP2AID2jscR6JUY9RIrsoP9VPAEGWsNzi6GO4Uz0CkbKwuMM5ZKj8LUYiKeY5XoMl7MHXjUVolDJa4NNQpeXcX02cNNWXi8NthpizqI6/GjktEO'
        b'9rBRmWRGIz28u4SZCl6lvDORjuW1Ft1cQqOdUyxZvu2kxLDeiZF5QcIqoQidZzq4DlQUOskeTPH5YAvciXYJsJRFgzAQBncrmBUoAvEcDbaWS5ZSgIcueGCGwcaqeFYI'
        b'mqAe7hWi/ejG813B06hFXtxTzqP/jLVqwfffNeZnKh4k2Z3/yej9VvAuC17MJ46wqrl5NGV/IK3K2JmecHzTpqkl0f6pVL+Z/kFDn87T73FWWlWfr03335X9Vh2bH29e'
        b'8OOZv719VvnVw4+2/e2JRfXTPpu81B2z37DYa/lO9JiXEtvmdEo2PLzzB8kq7tzQv417OOqDr7S7EiboT9zrb2+6+G5V7xuffP79FvrKw3cSsjaH/LXW64ku60ZYTqrL'
        b'0yPGtKn9p2P+vvXt6L1fTgsua+vpiywT1b82jldebP1SZdvHhi/cnp54M+nV0SFPzJKC5z346bMdOqGu92NJD++df3Z0z9iiL9/grP+ac7Xf1uvVlC+8Vwf9Lf+jD8Sf'
        b'vllw8Ob0T8N7fgx/ekj3r3V/vlthtFW89BPfjf7QrfJM/drVRSGbev0f3ys4Ub9h4Zgf7mZXlBys2vCsoOm1vFF7fcb8MCY15+wf5eKjUbekjosu709t8Cn8W2af3R+y'
        b'NG++cb1K82zN35f/dPWpr6pO9MW36XuiZspf/6OL5zHlJx3K+8e+DfmiraRJOk9e8WDaooL8RQs2vNpUNqX+qP662dWMH+l9F/asNay4f7Xh88MRC+e0rhx4wNX/452N'
        b'yw6NepbyxXdy2vXfTQmJd3VXBF/E/nF3r/ePDV+f/Gvj12feXNnnCi/8+Pr94Nc+eEZ1zWkz/36exPypBxYD4Rh4BzWE5aCtqGl2FmoKw8YbnsXWu1j1lFwlBKP9KVKk'
        b'gdcj0sNCJREYAG3FUY2YtxDu5z4lgpQ0ZQlqgM3YLg59rcbzZl9fbIcX0TlpBO7diocWwB2rqjnhON7ewnZvxPp6PTMsJA01ZlLAPGoMnns59mzHnhJdSPOEtzPTs0Oz'
        b'zYCAJ0WtHHPsHk8+Jc4qZDUeNi0sFA+Ltk/Aq9+OmrjAcSwXHYAHrZ4yHvM23FeIY/L9mbnhWMmWUskSuF5i/bO3Jr+/oEkhNv2tW/f8jYsD+4ZDpSxW0MXsPc2KEdqY'
        b'9y/XOcz7l6cpHOAW2MwzunposwyuElxzEmk9e5yCjL6BuuIjru327dE6z2Ze8+wWGwKU1rLmoWu4wTX8gWvko8DQ5hStqCXHGEQqbrtyjc5u2pCWhQ+dIwzOEe30A+fY'
        b'R95+uujWRbpiXYm2EgPZt0x9Dj0gAJ7eh0e1jtLFHRjfnGJ099YuaQ1unmz08Dmc2JqoKz0wsT26PabHI6I55V3fQC3fKA7UleiW6CzYKh6TqXqIdSn7xxtjR2tTdN73'
        b'PaOMXn66sv0LjFHxuMHjvme40dtfp9pfred3OXVYGwMk7TOOZutlXaqOaqOnWOfWmvvQM8bgGaOPf9tzzCByZBxGdr/vGTbYEBGLG9z255LnKoNXDEF1ac166Blp8IzU'
        b'89/2TDBBfhgRrQ88u/gFNMGWRuFnl/1Z+PnwgtYFbYWPQiNxi/P+zAEb4OV/OKs1awBQocmUcXLaEy4Vmk49BZRXBvUoILg98EimPtAQMEqbavTx16XvX2sUB+jmHLHV'
        b'c3rFsXq1QTzugTj2Edv2UJxgECfo1W+Lxw+kU8AvaCALB4Z+mIEFLVYDHL67Q7NgwAr4BzfbMntvy8WEDwm7aHPaRk/3how1OAU2p2pjdfw+V/dWdbuzPui0D9k6T1vQ'
        b'aqWbaRBJjaGRrbb9biFGkSfTVtgriu9yMojGPxDFD1gDrzC8ISxDFi0Te4ISDY6Jj8KSup265fd8DGF5mO8uLVk6114nCREVSUthT8iEXucJmOM6Qeu4hx5Sg4e0fco7'
        b'HrHGyNTuslfG3KsxRBaYJi/oFYU9mUXkdcjLQPN+q6GyPdLrwJ9rD3MRN1RxlOT98kiaMpmAjwHMe+dvJnMoyh3z6Pe/K9wtCADHhZFcCcWGMbtd4MVMeB1uSw/D0Tc+'
        b'WsAD6Do8OewQZj14AlqKiz3WpkMYucgDv7zKK7d+fijj/ZcdyioknK+q8TIsxUP+phEa0eLi4de+zF3y8lqZOHvGmLgocY2SqcREDEMd9pCuEitlKrVSQcaqktMqMkRJ'
        b'saJSXFxaWqNWqMS0qlglq5YpVLS4rkJeWiEuVsowTq1SRuNGWdmw4YppsZpWF1eJy+QM54qVchkdIU6uomvExVVV4vzUacnicrmsqoxmxpEtw2wuxaMQmKphQzHXFixU'
        b'aY1iqUyJochtt1ohL60pk+F1KeWKRfRv7C35xSqWiyvw0sg1e3lNVVVNHcYkA6hL8dZlib8+RDimYZlMWaiUlcuUMkWpLNE0rzgkWV2O176Ipk19KyQ/w/wlDuZHUVFO'
        b'jUJWVCQOmSRboV70q8iEBWSbL+abhFuqZHLViuKKqp9Dm3j1AjizRqGqUairq2XKn8Pi1hKZcug+aLKQkYFLiquK8Q4Ka2plikSGnBhBUV6MCU8XV5XVDIc3LaaaXUuK'
        b'rFRejUUB75QQaiTQUrWSUGj5i9XMQscrlGrFiNDkBiqRKfGY6tIKDEbjJ3X1r626tKqGlg0uO1VR9v/BkktqaiplZaY1D5OXAqwPKpmC2YN4kawEj6b6370XRY3qP9jK'
        b'0hrlImxflJX/S3dDq6sLS5WyMrmKHmkv+URvxFPVKrq0Qikvx9sSR7JWV1yjqFr+P7onkxGQKxgtJYZCbNqaTDHStpiLu9/Y1SRZVTGtYtD//9jU0Jgh8bk7G+qLntu7'
        b'2hpa9fMBTJIho0uV8lqC8muWm/BaJi/5lRUTz6UqHhSuWdhz4amqqn5FwkyTvhDH4XP9umj+brorZdiLYqVLFGMrgyGno1ullSXsBCPBE1uEN19YKRvCqsEFYRJUoVs0'
        b'Lav6LVQVdvC/QkTTOARi5MX+wuNmqhVlMsXIHtM0LfaRI/jq4RNjmN8aY9HS4X53KuE2Ol6uorGlKsdBDOkeCbFWiRmAbV7xyPNOM3XLFOE5yohfW/2wuX+x7pH9v0kQ'
        b'fhYDDEP+1XiAxZXjqUdGTJ+UnPPrYldYo5QvkiuISP3ShuSa+koYgcQKLJ6ilFWX1f2qrg8d+T8QaBb8dxqTimLsbUY0eVNlJegWVusRbML/wMKIGjB6RuzcsHXNwD2/'
        b'rWyK4mrZC2tniovFITm4eUQ5VStrmbjoFxgFMmWdTFFG1HJFnay0ciRsWlZbnDg0sMYDDInqR8CYp1AsSBTPVFQqauoUL6LusqHngOKyMtxQJ1dVkCBdriRRqkwpLxXL'
        b'y34rwk/ER8XiamI28ZpmVPwsCXY4YqLpnJOIzwUjeYbh0MNuwWzAz2/BstkEvjQfLghxtiLn2Cxnx1r2GimY5oHPvDF8UlHVDuEcwLyxXSWYCDs5AIyFGnQClzdRJwOs'
        b'yTADWRPdABAXWblLlSzwPC94gCTngXy4jtz8wAYPtR95j3UL7UbnpJKMcUiHtktzsiLY111SAfD14bujjakSKzXJyYOtgmDUEJmRHg63RWZkZ4ZnWJLUkcwcPohGjQIp'
        b'6oQn1CRXrsZqlpTpZzsdHKEGHuJCPbwIL7Nv0W9kLSIXQaghJ8b3xT2QGu1Sk5eG4XAPPMTc+DDXPWgTPG+68olk8z/2qOpQgxQ1ZmeEc4A5vAnPoescuM3DTE3O+lCL'
        b'NmaT4WHjjHS0PTMHNqKmyDTUyAU+DjykTUTnmKu25Ok2mRkusAVtN0GRW8et5L4vQMofh84tZzJ5YXNaJhnsOQxzOZeTTQEJaq6Gt/hw/4T5DCHhFiW6mZkhEz4HxpAN'
        b'kekYNKCIn4TO0ixYO7yIdkgjUCMeLSIjG20Nk8A2dFcAPNABHjwW7M/chWJqHoIdJjB4ySE9G20LkwiAqzMvqhIeU4sxTAy6mI4ZB6/CphE4x5Mw13SYR1cTY2OwlOWV'
        b'wH2gLDiZHX89PIyJOJRPeJwjDKPQcQs2o7NpTGxsDJ/ca8yDB0AFuiViL1w60HrUhnaZARAVjZpAlAhtUZPXufblcIOJsfASPD3kiu+c6QKFRtfQ9Re8VaNWlrUr10g4'
        b'zNWFPTwWEQs7avFSdggAlQXghTgZs5G5Fda4g1TgZXgIVGZmMtIGm1EbvDZEHkSYCkQc4PqpEoEpRWUMaomNrV2K6rmAygTwfByb5ONujrbFktzUFnSND6jpAF7GDzfZ'
        b'm5L1cCfcFxurTIDHMFYugBcXoysMWrEjPIXROuBB1ILRCgC8irToKEOzTHNxbCxFLlTL4FFQiYl8kqXZbt/C2FhCyysyeAxUoaOwkVHWbx1cwLSVC4iyjhu7MIFVVh/Y'
        b'gDppPEwq3IPugtQEyCb5LI6yA/MDUgCoLaq6PCsVSLiMxtgEw5vk0rCRvR81R7crkZaDUa96MP1o9yp4OjMiPDQjKgkzG17gAdsCbhVqQJcZonsSvqWHYWbxxsF6HgUP'
        b'K1DL4O3q/mB0ExNvNWw0EQ+dhfvZDJ84Z0I9eALeHaTe0XJGyFXwtDURhHEeI2kg3I62mtidPBftxjRGB+BWE5HRuvlsVgW3nNA4U2GicCHSMEI/arFHZoYlZ2SthW1Z'
        b'jKzMjkIXGDZUlxMuBKM76hDcHIC2lP+aMh/CDCfaDLvgdlb6z9MZDMeQzoFwLA0eZRaAbouw9aoJGlnNnSawq58HD8XGYqVDd1fAw6BiAhYDgpwtsMtMD8+JwMocwmor'
        b'vIX2coEHJjs84cfedlq6opvkElgSns4DFnZTzDhwByZMGyMC8eW2IE01EateUZh/eCRgmOSdCzebGBjHMpBoMaNxQXBd+DDZ0MgZ2UhcxSaV7YmDF6QZ4ZnhkiWhOeQD'
        b'BNtFXBm8ukIdRPZ6A95Ft4ZnJGCCwfPwCtrJAx5ZPLjTr5D1I63O7izg/vEvshde5C4UjWWt8yXUspq1EXBH5BDzE2q7rJQPz05Arcy6soOwSD/P3oDn4G2SvoHO1jDJ'
        b'BCIzj+eJDqY0B2xDb5NUh1LYzBBxOdyYgBoG79tPuTBX7mhTjDqULLYer/I5VeBWLJ5oWxZqqp2Dl02IEAP3CdKxfh9mFD40aDFeSVpYRm64wAZdAcJMDjq02Jf1RrvQ'
        b'eQcmJYBNCEBt5UxOQEIoVk7mKvRyFDYqDaYsA7TBiiQawKYapnNtCLpKck2YRBM12sLkmsSjM4yHwla2Ae6GDaZ0GD94ZmhGDOyqZfPrW2OgVojDgHxzuBl7dz0f6xZ5'
        b'hx4LdxcyNiQOaUHqGlMakz+6KVSSZIgzaAM6DeBeH7iNdRSH0Mm1bGJyLtoAwn2TGXm7EmwOZof7kpzbrCfLJWw2QTw8NRdvfB/2AHOxOWgChdRCZviwpXjJnVFcPP4d'
        b'eBK2g5o6dEo9E/cUYN9GY4agxvS8abAjKn860jDfXUSEh+DdO6G7oab8h3yiGZqwgjSybYayeWlhpAfrS+bMaaiRB+DdlfawcWwgk+9gcOGB1+McSGwUdnbcUsDQDp5E'
        b'rfOfkw62ow3DaLfR0WSAUFsSBTvjauHNSuxu8rB5C0Ba1gHo4HF4ivShDqw4xL5d4EjU8UzMhIOMDWgX1KSjq1gVWtBetBtqluKiETue8wnwAh92lExXlcAr8RTmvGBO'
        b'iQN7139iMQ6E8Jir0DbTmOmFWFBcGU29MieTcYxoYwieUVDICfWAmxgpG4sORTMGPEc61IAfQh2sE9yADqCtQ9U8opbR8jloAztv21K4nsxrJTFtE7XYM3rrHINu/Cwa'
        b'0aEjg9EIPAvXMzOgMyJ0wARXO3poNLKalvAYAbLMropNWJI6ERvyDLwvtD6MtaOtFfB0bBwWOXQ4HUcgMhceS9+LvOWxcUtx1LEFUyIJwNN4F2fY1e6BewR4tUivyAWM'
        b'+e9QTZBQjOgVoG1uuCs6EtbjrikAHiqYqMYeEbgAdE2IadeAWd4QiZrykd4aXoqLnpY2KHXTwwumD5ckuAVd4QEssoct0X4xusgu+MZa2ArP4gWvQneswSo77D3IqjIs'
        b'KHg2AV5KIbm3LiTLWotaGIzJmPoX4FnsK9bg+OYcWCMYpY4gI12FNzl0eGhSMNoWOT2EXCgTuzhrmCzPCjfDnroJ3VYnEp8aOkGYk40awwtM6oG2zkrLmJk2g90N6kBX'
        b'4OlpSJMdHpGTlcsH8BTSW8LN6OBck0DDDbAN3jB9MHARdoGIRfAuQznPOdVYZM+TGORcNA684Nm59hiJBG7oOravXYyAYQruGyJiQWgvAwH3paP1QwUMNuHQmYiYCB5i'
        b'PclB2FCEOuvQVZKhAzdhMbpGYeeyjLWC28JhG42u1toKcOcVbBG3UkHp6C6TPidPXfoQ0B9hq/F5TcSJgkw6f5TTXpWssHBiWpWjx4FbtTD2Y/sQfsayy9nCspejwrTr'
        b'+aj1eLxX5IXWR0/ShMbrf9m8SHRywfGze2cWvP/1oq9ca1VhrwbdsTmYcKhN6rU6MfIgffybzYVzLt7/qOpxzQdr1p7+POqNdfIdzzhdNiv2ZCc0v7VmUVbmvRUv7/7c'
        b'633Xyaq25Dfbdv5QcHRvRsLGv95fMh4Y4o8lvZrwr8NTVy12sF2/a7Tdk4kai11R4oNeuXmncv562Wam+/TIt3QyV+emTw03lr/kuyA2YfbWNsk724M+lkzYYr4++6el'
        b'ok0rl79hdvSr4L+92nxo2uZ2337xvHl3fSdm/ru3Of/DiIZPZ2orVr8pXxm6XfFKTbP1NP3O/oCHb6yZcn3q0oNX3f60esd7cz6akDKx6dgbqUXq0rGjfpr0qvFDv03v'
        b'xTj93apF7SkMebg65dFnC5NaDnzpHlqAAj8qGP+N9uNDKYrq13+48fHD5rXvDTx58NrlmJpZX3R1JEnHrfm348bUon+NDptTOTqs6VzyTxZzq+0W+N7IeBpg0HwmOXpq'
        b'6yHf/cFzxSv2fjbmaGXK3ShVfatP2wfCCbUHk9/4U9D0N9776Luu7Y1n/zwl/dKChLzPd3y867Vui78EOqkfvPa46nTCmwvesZ/id9TxepHfOqlU9U6Lm9ua+pc3xDZ7'
        b'/Tnhg+LVZW9E7Dkf29X1p7hPdr625s13lmbIXl66KDuh4vL8T5fsffb5P7dPvheY+O6W1+bJny1e+/oPV7gOy+62tP3oHbyK/5dZrqq01vnTxhy+5lYx7fLrFhlV5x6+'
        b'sertNx82rn0DHld1fV4pFVvMOPi9+Y6cvtBjO5qN/JhjET3fCzu/tlzecZL3yb/iPT/ugTGrTm9QrNjNrbm+y2LW1jXxM9eMDnpm/drdLW9feX9e1ZsB3y7xMiTYrBB8'
        b'VfB2Vqd2nWPOybdeLWv7V6/Tx2Wv39jXssXjL168O1cXPA5KDcj+6nbx4765uifh7rPsl3isfnzeYcc/e9qTom+evR9qdDF7vPedErunD51rarKvC+8s+WyZs/3HvD9c'
        b'szFE5CSv+lQmqp4YWrfjgNlbLV0fNPUFf2j29MiTwhqHul1H35n43k9fO71/+BO7r4OjP2998kG+31/+1bxsneY6shMvVPjl+F5YIbowJ3P2bas73rZ3//Q0bMVVELQt'
        b'Pv7v6j+t/iHIWPaWfosqumRxgfPp3Md1Rtkrn07bN//Eu2Mbz7yXeeNacJRZZu0HnxYJ3my9hfalWHiLIu6EXrBb2/jtqIA7C79/a8mdtEu59/a65ft010xV8fp8bxrT'
        b'F/Iiee/P7vjgpc9sK+9u6PrrV2FTFzXe/HPw4XNlz/4eD70vOX995p/vFMyZ/zhoQmZ6/5S5hZ05A5tuf2L4eurVpNqv+W9IbJ6SUBhu8+WYUndKk7E9JBYxHLsUeJWX'
        b'hg6iQ0+JTyxFu32koRES7G4AsBgfPYcDT4TC40ySDjbfl+B5KUkdWiocljyErqMDT4lNWoMdfzs7yXjYwqYIccLR/lwmP2g+1Mx4kR0EW/GJ7ixnObb9G5nkJNSJTsNN'
        b'bPoSk7sUON+UvQQbFjIrSDdH6wfThAZzhJzgRpImNAfeZfKX4JZciM/m2WEZaAcA5k7W8DqnDu2rYZaHZ9CYZeLQMxL744vhAAjqOBHoCDzAjI7Pjqfhlky8OkkEJF+q'
        b'shu0jeIuSkbNDHnm18D1bMgAW/xMIYMlrGf6MtApdEFKSGcTE0a+djjHiUVtWcznjNhBXEdaHPazn30JUIvpyy+4qZZlTj1sm4OXtz0Tx1/oNKqvNX326DyOx81AlyTi'
        b'/+tEp//mgibb+OU7VDYzZPBv2Mds1aoxcVErhj4wyVQ/CdiP2RQC4CTaN7FlYq9jgCbF6OyqmWJ0EmlSjW5emgyji6tm6nsiz2Zen6OXtkyX+sAxtM8juJ3X6xHenGJ0'
        b'9di3smXlrtXNPKO7ry65Vdps1ufqYXTyNDq6kiF1sW87BhuDQk8tPrJY76gv7g0a3ZLbnNys1soeuXrqeDtX93mI+zwj2tX6hYbIlAeeqUZPv8PZrdntgQ88ox5Fxhkl'
        b'4caQMGOwFA9iDIsyhkcbI2JIKY00hkYYwyKeuFn7uu/nD3gCdx9dwH4vY3iMlq+t7BWFGt28mQYPb11g6zjjpKkvS+9JXyntnTTd4DlRm6oLNXiG43nn9EZOxBPhBkmv'
        b'ZxhBCje44cEj8TAVB2xxQ49fhsEt48OgaH1gF6eLqw/tknUnX694xf96TW9QjjEkvL1Yz2kX9gWQbeTpl7Sv6A1IfGLG83XX8gcsgaevLsfgEWOMG4PniOj1jCbZVQqD'
        b'V5wxPhG3RPZ6xgzmWyWM1ab2+MX0esYyLQcWDAEhuzngNcBxEbsbPSXtcQNcXHvkGYAJ66xf0mWvd+8NGjfAx40DAuDlr0sZMCN1c+AVqCsbsCB1S+CFOTcgJHUb4BWK'
        b'B7EldTvgJW1PGbAndQfgFdLuNOBI6k7AK7y9bMCZ1F3YcVxJXcTCuJG6OzumB6l7Aq8gnWrAi9S92TX4kLoYeEW0qwZ8Sd2PhfEn9QC2HkjqQSAw2BgsMYaGfSHFz1re'
        b'QAShnH3raDa/6oFHeJ80Xi/rSu4q1i/ujn/F/pWY7rGGhJxeaS5JUmvNMgYEtaY+kkbqzU9PGGwJ1KYawzDfTmd1TTaETdTytHMNohAms649wxA86n7w+K7k+8GTuu0N'
        b'3pO1XEw53yCdrH1yjzhKn9kjnqjlG30CdPmtKx76RBt8oh/4xD7yC2ynjgRrJ5NcvlJdmU6IYbx9tFwy6OTWxQ+9owzeUQ+8Y/BSJ19a3D35fsJU4yDOABfg4Z5Dvf0C'
        b'qjdh6qOQ8IvC00J9apf/pYxuqjdkUqu1VqDj90ni9AVdM3slk/HyZ7faGCNi9cn64vbF+HGBQSR9lDAWE2WSXv4wId2QkP5KQG9C7hMu5RanddJWGtxC2ycbPcU9vtEG'
        b'LEQiL63CIAp/KIoziOL0M94WJT7XksB2p/uYxn4xA4CKS6eMmdPxIHH51JeA8p9B4UavGdQjE357iUEUrQ8ziCY+FE0xiKZ0q98WZZORIgxuUY88vQ+nt6b3BCV1B/Z6'
        b'pmmpDwND2u0vup521dufdT9WaAyRXDQ7baanzlr2YZ3yvRZ8KbjLt5Nolfq6ojcoe5jqpO6fQHIkU3Xh97FBiBmFa2H3PSMZtRxvcBv/SORJJg7BG8XVD70j8EqjEo3j'
        b'J3VP7RmXhbcQlU224JNDtuCWQz3yDdqZ8aGbNzFda1vW6ugHrlK90zWvS15d6gfRqa84veX1qlfPrLkP0ud9KBL3uXr1eUf0RE55xdUQOa3XO69HlNfnHtojzep1z+5x'
        b'yib5gPMMziF9TkE6dftCQ/C4B07jjU7st8GBD5xCMOmbU42+gTszHnmIdd73PaJ+MR7JBPU2eETpHQweccSm+upm3HeVkHzSia0T22MfeETqU65lXMroojtzu4vvx001'
        b'BoScyjiS0U4fy30YMNYQMLYrpdu/N2DKw4AsQ0DWK/m9AXna1L7A0Pbo06UkqbPL953AcTpqgMfzzaKMMaO6qEshXandvt3F9wKvZ7UHYj21BNEJ+uIuSm/ZFzGmK7Cb'
        b'6uZ0SXojUp7wuRI/HR+bkYCQ9oSjE4wTJutSeiSJ9wPGGgMl7QXHFmKjpUtpdzua+4UXCBqPdR0DWt/3TzAmjNbxdAsM4liSsunV6xmpjzN4jnqb8A6r3303KcnFnG8Q'
        b'hT4URRNxCnhHNOrDnxNnII8P3LyezOADO+c+Oz9dfLu3wX/0A7sxRjuXfdYt1lrZA7uAR45umuxvn0aDkJgvAAfvsS90lGF0mjFkYnewIST9Sy41JpMIgTSLCEEgLrkE'
        b'6nuaXEYZ+Nb5XrxeL4/80WZsdqZdP49ckv0HWZn/sc8mr62KRvLRSvI10TDfvJPATwBs+mYxj6IcvgG4IDmcDr83h7NNEAbOCUdxh13QDSZsfkn2tw/IyO/4gLmcMmou'
        b'dznHokLC7bdjbgaZrEllqlJZo/zeh70rZJapNCVBysrExQqxjPRH5Eh4/eaFheRytbCw37KwkP0JHly3Kixcoi6uMvWYFRaW1ZQWFjKEZhNiGSqQdNUVv5i2CS+VJh/2'
        b'bQKPraIZcObGDp21WCu0QddUQgscpOaEK00xXCQ8gk/5hwV8OeyQUFPkE1+6wKEr8SDr9z+VtUzNRUlOm+reLzn1DWeTy4rI9T2ZIesPd68us1jCzUwKiHhl58NPNHb7'
        b'5o/Z7PNq51auuc+Ef/3z9ZU3x/6wV93lP6bj2Ogzx253uqIiB7r3wp8/Dvu2u8Z9+/vxd2f5zqw4f/HV9QXB550WT1szdhV/8WjhezPPjir9vHDi+fMO/tVrz11b/sj8'
        b'++/2XIvOtJEWb4p/673PvnmisneWt8TL/lD1fn6txM9vcYbm3S2nFsYGNK/6OM03+3Vx5ut2+b65Ybq0sCNZ54rWjdb4ljijP9hvd3g5Kudc8YbRWyWP48o1nVr/N0vX'
        b'd2kCH8cU6LfFnzu2w7rq6PrwqlKzm0Y0wSbxtO0/00f/wX6H4Q/pU5+U+Vq0vnnIyS3/JcnBBTS9e8Hr4TeW5H8/TlgjHX39sV/ym07vz7A/05Oy0CmlL+vRe+/cvL0K'
        b'PnP88ofLorkJaPOJzd+pP747oWlih/tfflq5J/zKYWXce98E/8Psu23v0+gnzj931eyWPJbwmK8IYGMFvI4asihAjQb4/HEL7UhzZU4fmeRLpOE/OUJ+bwRuKTNfrXpK'
        b'3twtKUe3haGloahRSk4fz8F8YCcPXUS30TXmGOE5GV6lUWMlPJ+WEx4yeE6xR81cqC8IlLix6mf+m8V/X5ROjkHiJOZv3S/+2PAcK0xVTXFZYeGK5zUmMP83ltifcGAe'
        b'BqydB3hmFq59tg7NMQ11Wt9tq1ppXYyu+Ej8gRXtefvXXgrQK7t8L6m78i4t64y4l/KKA0q7H5P1nshdG6Mtbo0/YKHLMIgi9K4G0eiecTkG15ye6TN6ZhYYps+67zrr'
        b'PRexzmGXoscuAMclotkUdgIOTs3JLc6aSV/zBBYhX9vxLPwGrMzFlkYr22aXAS6puXlqy9lakKQ9ga3FJnQJ2FrS5O4CpvaIweCTGoPB1BgMpsZgMDUGg9Rw7GVth3HM'
        b'2Lq7F8Yy1YNDMZ6pHjcKY5rqyVQKhbGZJ3MW24KtM9imelhMl6C7wGjvqi1vTxip+oUtBuwx98RxrYMIt7D/PREK/HCr9zd2WZTFLOw42H8WcoClXZ+FXTOtjW+ufGDh'
        b'9w1nGdfC/RtAyi+5wNKfFHYDPPI8sNQM159yKIuYtuXYAVnEMJ1PSMO3AzIhZZFO9Tn4HLfqCZ/SK57a65DWY5XGuqVtyaIUAfiDwDHFjcu6Jad+Djac/3VOaUSxdRrB'
        b'Ub1wVuTTghfCSl520+NNnkpCUXbEUdl9RYrf66iOCKLBJeE4rlywYiyXXoVbHJVPZI3jLTcmiVLuTpx2Jr6/dUZ6z7Lgi/o0u94TWYnFL/9jY/3ATr/MpNr9o14q/WTW'
        b'yq8fv/1u1g4v66cnbL/KqL/1jw9cdlglyg97ZQePneW3fN7DewvTi3bkyqOieBbTPwqZ9ni70GnWe7X1RyA3e1aiR25ykFyy9sKfr3gc7gyVmLEvEy6ofJjfOsslX2hl'
        b'mgFhbhrs4KB2eETOmLLscPfM3HB0iYDkhnPQddiJ7c8tLjwCb4UwNqouER6GDeRukVyTBaA7sBE2mQEbB6437Mh4yl6gj/VkvtaqhS3kgy2O+aq5zPRyuCU+c8gPqAnJ'
        b'L+lIOKgZbRrLfISGbliLhv3CWjLqIL+whk54syOfcEDXpBl8QGXibbQCpE02k/j/uln8f/5qY0SJ9B80pL80oyOaVLlCrmJNKltjTOpUXPx7HfjSHfAdjdZOD629Ddbe'
        b'bct6rUPWTTHyLOuz1mf12PseH/2AF/Y+z+ddnvU3gpV8fsw3gJRPmXJghRBYOa3LHfIZj7ifWyVT9PPIVyT9fJW6tkrWzyPpUjiAlJfiknwJ0M+lVcp+fslylYzu55Fk'
        b'0n6uXKHq5zO/6dPPVxYrFmFsuaJWrernllYo+7k1yrJ+Qbm8SiXDD9XFtf3cFfLafn4xXSqX93MrZMswCB7eUk7LFbSKpI/3C2rVJVXy0n6z4tJSWa2K7rdiJoxh09X6'
        b'rdkAU07XjE6Iiu4X0hXyclUhE7v1W6sVpRXFchzPFcqWlfZbFBbSOL6rxdGaQK1Q07KyFzaHefdU9Jt/YjFrKrIGC/JDdXQuLp49e/YjNhS2FKXkEksxvHzClL/HbhAr'
        b'ec9CkOwG7rkJkwO435sP/tJYv11hoaluMlXfu5cP/6lIsaJGJSZ9srIcibmSxNskOC2uqsI2lln7WNJkicmrVNEk165fUFVTWlyFKTtdrVDJq2VMiKqsGpSGF9Fsv/k4'
        b'NvydoFQCNt6m03ExwKUo6gmHR/EGrIDQep3ZF7wMAeU0MNcKWNg/NPcwmHtoMx6YB/eETbgXhEIMYRlGc7s+S5ce19hey7geXlwfsGsWvQ3cman+Dya97HU='
    ))))
