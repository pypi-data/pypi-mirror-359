
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
        b'eJzVfAdcVGe2+L3TQJqIiNhwVFRGmjKIgr2gwNAUOwoMwwUmDDN47wz2LqIiIGJBUWxYQFGaBWtyTpLNbsruvmRTWLOpm83LJm/TNmuS3eT/fd8dFIzmv++9377fe/Lj'
        b'OpyvnX7O933nzgdct39K8jud/EqTySOHW8blccv4HD5HsZ1bphCUJ1Q5ypO8GJijEtTbuAKNFJauEDQ56m38Vl5wERTbeJ7L0aRxvfJ1Lt8JbmmL4+cs0BbachwWQWvL'
        b'1drzBW3qGnu+zaqdY7baBVO+tshoKjDmCWFubgvyzVJX3xwh12wVJG2uw2qym21WSWu3ka6iJGidcwqSRIZJYW6mIU7UteQ3gPy6U/RzyaOUK+VLFaXKUlWpulRT6lLq'
        b'Wtqr1K3UvdSj1LPUq7R3qXdpn1Kf0r6lvqX9Sv1K+5f6lw4oHVg6qHRw6ZDcAEa064aAndw2bsPQtZr1Adu4NG790G0cz20M2Dh0CWEPITRXp0w2dXGPJ799yG9fioKK'
        b'cTCN07kmW1zJ59UaBUdg2iuKLI/qmTM5x2gCxGPYAhewDHelJM7DnbgdDmF5ig7L4xemhmq40bEqvAsdeh3vGEx77/SDm1J8Elb0wX24Jwn38JxbvAKasSbGxHcToU8X'
        b'EsmUDzzhxP+HD7k+Tnr5nUpCr4LQyzN6FYxefqPCSW/+o/QO+wm902V6N8RoOA+O8z4RkGf5QDWSY8CUkYwJ3OdZ2SGzQgbJQN/Frpw3x43VRqyzhM9cIQO/iFVx5H/t'
        b'5jF5iQf6xnENnMWNgBPc/FVf+3DTtX3eH/2l4uq40AEfcJZepOHMzBq+2WW1W6/pWRH3Is7ptsngF81f9t7fe8BAt9R3+R+WtGlmcJ2cI5w0wBHcjbWheIIwvyx8XlAQ'
        b'7g6PC8Xd0LAgKCEJK0PC4kMTknjO2rvXFNw6vgd7XbpoHkvZS1nL5SofMJD/WQbmPcpAl58w0F1mYMXK3hyRuv/muE0ep6fmcI5xVAWacQd0EJz3BBtwD+5KnBcXHxK/'
        b'kIswpPXDLbAb9i+AMjjA5ald8DjUwyFHPzrq4Apshb0z9HCNrAIN3Mpp0Mha4vvjbV/s0EM7bTjGFWAHnHNQfPRiNNZArT6CMusgZ0rFHQ5fOlcL1KVgNW7FejXHhXFh'
        b'i/AIw7cu1Y0jHVybl+Za1g7zlcVYOsKHCyT/n5i3en1kYABnnmgvVUhGAlnzccWfsz7Oeio30fhSbti+IGOc8ZMsH1N+riX706wE4yu5uvnxRl2qwdgknOcb++Z9nJNg'
        b'TOf2meJago02YZ9q95nmc2NnLt2jG6xdFPPVzOeTz3rN2dvxjMfRAdyCxH7vp4/XKezUJ/SCA3DenTBLl+QIHUNIukkkreD6QanKFW5Cjb0/6RSdiNQKd2Ml7pkwT8mp'
        b'onlo0Vl0fKciSKdTilQ23R4K8vjOb3KuaFsrWLW5si8Lk1aZc+1TO92Yo8rMMdoF2k/yoJIe7sF78N68Kx/Ei5quKXTKTnWx0eIQOl0yM0WHNTOz0z0z02QRjFZHUWbm'
        b'T9bV8SLVFlFNH3SWEXR+Lzr/O94KDa/gNezpoD4R6uCEGBwXMiYZylOIjqg5P9wyHMpVA3DvyjkmhVMFVY/RZ+IyHuizgjkEJdFnBdNnJdNnxUbl4/S5a8Ke+qxJdlCH'
        b'VIzNUIPV/II0jgvlQvHuBoc35Uw4lGG1Mo04knAufIpSVrJ90AI7sFpdgBeYkuHeIPP4vCu8FEZatwVP+XPWsqf3Qg20722obtjWEje8pGNb/FH+hVyqUd9oPXLftfDc'
        b'oUbX6Xcqdbx9IPW/cAZuBSeELpiKO+MTk9WcO7Qo8BjcjHDK4nFCZqzudJclmmuxGe1MpFSzuTEevIoIVHR7IE4VE0+nOkfINttF2kmkPkin6CZChUgDVDc50uHBD+T4'
        b'Rg85Uv3F68TOLwdDi5tTlixahPDcoEIVVMV7Oaj+LocKOCjZo8aqOEU21GVweJaYaJnDj7RNwRsG2sRzCgFvYTWHDVgf5vAnTQG4DZppm5JT5MFuPMbhBdgGFWxO2BUG'
        b'VyT7BDqnldhNB4eNuGUmcw6rg6bRFgWnsA3Ds2SU1cjkFh8YKWH7eLoWbDMUctg2aS6bLF2NB1mLmrRsx4PFHLZvgMMMCzgM+7BFEtkwGwl4Wzi8CA0jWSNWLCSuus0x'
        b'jqIBBzyxmUwKh5Yx0uBGOpxhjQQTOLg2icw6Kp01FWMdHJMkPR22aRie4PBSMe5kU87zxjY2iFANR+Ac1hEmR+J1hqhiCZ5njS6ksVYVzxGHeAE7WBuehlKswDbJw42s'
        b'h1fGBfORfsSR0ras6bjfXWQCgLNYQ+e8ZsLdDJdpajztji3jaSPugRtreSVens38L1Hharjs7hZBaceDZiPfK3gimzAVz25yx6uMbiwRoIrnoRUqWZtaC0clbFvlRdE4'
        b'GYclfDBswbMywy5BOWyVehFO0SnvwuFZfNQmaJMpOAqnscp9pQOvElKxZc0IfqQR98hBog7q4yR30U6H1WT48AFwXmL443HcPlKy4zV32lQ+E2r5YF9Z4Hhso4/k5Un4'
        b'oVRjRQY/ZTW0yGPqiAM6RZq8eE7ZC/ZBBT99JC8r1kHctpi0rKSUXSdKdYwPg3IzGzYcb+Mdd88i2KPilCOw3YOfDhc3saYi3L6WKgnRoCKiH/UcNkFpGGvqAzW+RI0j'
        b'NZwiF6/CIaLiNqxiVE3TpVEtoGq3bSW0c9gaAVsZGp4+eF3CFmzrTbl4KRbK+cjheExWybu4xVvCq87GRqjO5PVxuFenZVGtbXBfvj7jKRWX+nThkiEZeQyoyOrHZ9lX'
        b'qbixBCjdz2XAN/r05/O1q1VcEQHOkWTgLuMAPnDTZuIPnt7wZkY9z4A+CwfyRasrVNz0pzfUxIjBDHg5eAh/3/2gitOSnsuOxjHgAM1Q3q4+quKyCLD/j1kMWGLU8hfT'
        b'T6s4bzI8YZYHA744fDhfNPUCxXODf0TjEBnP+EA+ZG4rxXPDm30ujZAXChvFPzutg+K5oWaMKocBJ6zT8ZMNSPGU/JM/CmNA74hgfrv9VwT4jLQku/caBnw1PYRfn/U7'
        b'irzkP/rXvRnwN1HhfP7c3xPgM9Kbo/gABnx7wDheO/kjSpG0ZOTXkxnwb656/qXsvxAgmXNOURQDRvQaz+8s/pKSKdVMz/CS+Zkdxau03xMgmXOOIo0BVRHRfKBVpSa0'
        b'SzWxY8Yz4C/Gx/CpqW4ESHoOnGZhwDnTJvP1ab5qwhDJf+FbLgy4uXAqf2LNQAIkq88bvZgBP0iazq+PG6kmXJL8BzXLq39hmMkneoQQ4DNSTb+JaxkwPDWW50YQDSsi'
        b'q0/zn8OA62fM5V+YM5kAyepZwzMYMNUvnveYMYu4/acLalwqljFgP1si/5r3QjVhXYF/tEFmXahPCn8ibAkBPlOwxJGuYsDo+Hn8h+Oy1YR1BW8OSytiwP7+83nV1AIC'
        b'fKagJrhGkq1yW5y/5O5GTc8D6gcSGzqcLze02s3uopcnMdc+G/AKP2UGVjIziTYQH9yG11ZJSuo0vNz4YJMom8Iu/yDia4jzpsa/Pwlr+OHYhJt1MlKHuV/wgcOnuBBC'
        b'V72ZnlrIgOoNv+RvucWSIPe0bUlopR8DDvF4kecmJBDgM7Y344V8Bkxa8xK/evU8F0K9zT+CS3x8nh3JcfJmjm5huFz1P7lZ6bE5o6tpfpKbjEp20E1jwCDiocrGQmsK'
        b'8e+VuCs+KQx3kSzRL0s1eoJsYF8vU1qSefopK/HFKaPl9Fajdl3friBhOisrEfqs5hjHlpBE/Kgh3IAVKSTrch0HdbhdsWbBTAdNQ/AyXJkCbdAO7XgXj6s4fikHF+EU'
        b'3nAMIM1Cf5LZB5E8dWd4JF4iWYpHnrI3noQSlkLhoWUkp28j2MdwCSkx0XBOpHxiqGQsUuWf40lGNT0rMWztYhm4aZaL1aAkSGmzPAL7BHBMCaRx/Um+D3dotgf7OCNu'
        b'xy0OmqS7woVIA0uCqwLIowL3GKAyPB6agnhOa1d7EYR3MzxGELfZru89n8oF9nPZLkWOoVTCWDIjmGyk2NaU7KrioSFZxfXVKclfe7GCZQ6ap7BJb4IjXdsKOD2HKeB8'
        b'4tLv6LVwA1rpTuQ4Z1mJzXIk2Q6XyR4YdkC9ng6q4/KgXM0ogWspeFc/rFhPBAsnuafgODbKjDoX6aKHmtgoFmK5nFyjYxAL4IF4zZBAkUuWpeNVpEzqO3E8XGbzpeK2'
        b'ND0ch71RFIfDnBACx5nUvKEEGwyJZFA4lq+Dg8E8576MBI0F2TqFg275/fvBWb3bhCgF3VlyuQMcbL5E3I+79a64K4oiWMvlFeIBpiJpcAWrsIzsSpLUnCqAh+uRcMqH'
        b'7LAoixasxjL9NDgURWwBjnL50DSfIQFncqYFU2ngruQMsnVpUnEeU5S946GeDZPc4aC+YAhcpV1PcBbc48PWWkqUaxeWJRKylZwS7/C4NQpqo+yOFNpx7xC8JCXGxyfR'
        b'44cHm8qgMN2YpDBdqMIN942AMwJJac5CfVAQNPgF62A/1gf7wn6/fljfH84pONjt6w0niGbftdz/8ccfzRqVm0opayK/uIiTE50jeauDk0PjVJxqOh8BjdA4HOp1vqxt'
        b'tA5OSJ6ig7qeOj5jzQgsgwYm+5Fwcii2eclNV3mSm97QDVnAwvcqP7KTa3OOusNPwdvBUAsn5cXa4Boel8g45rP4CNNQR46coOIJQVrpcKMJ6k3ePFELtwIZlzRYgjUk'
        b'4q/CdjXN0nhs8R8GtTOYVWIpNBhIvoXtnnTCFp5swo9EQO0EebXrK4a6e7lDJfGqy3jPjel4Ba+xFrc8kmLY3VbRpPA2D+25g3vBDlmpq/DYbNpEF9tC5D9eO5rQzHK0'
        b'/UvhMLbZRWynCeodXjdyEDZucCa80DRBIl4cjo3UcDyxBax0yZDTt6t+7u6unmQ7oZzAYztWx0FDfxm/zZqJJKVd6UFxP8LrR48eQv6kLeaxvu5eHmSPopzEYzUcjIe7'
        b'JMNklrVtUCZJfkSSYSq9+JFYPyFuNRtiTIJW0oCtNIYM5/GMdYZ7lhxbNo+cIq1kq8BVgsHIgCGTGdKzoTpUcpMFtY/HEtijxYtOrdghQZU7a1P68LB34VhoKmLaLKbP'
        b'xWpiNSEkxYRdIbgb9jMTJhn4HrI3LOstwma3lcU8p8JLPJTjQZB3OxvgEB54QBQ04pV4PDLOvOXdNoV0gRhU6LyXVuy7m3xvuvfzecVvfDOjYrpr0Rf8e5l/4Hcb+s5L'
        b'TdXOW757+YSZWkPc/aBLNWdmxIUFhdQ9nTyjasz4ypnPKT8cVjPEVl1QnLcjf+P3L1/TF7yR+838DtP5lz+87KKBwZN3/GPS2H2/3OLxlstbJR1Vl6IjfwNf79n3wtap'
        b'Q2aUv3H3g+j5r2ev6T8kZEtM3DfHvzu4ttxomWed3Sq25ZQLrw4PtY8PKDh6LCKhdOK374WW9Q/9ZFf16nGNIZO+S6358kDT9b/NLfpq7gv79m5KmDqndXng+IPa3yYM'
        b'e+XV8bum6r4f9dunsnziN0Vsu39t54q3/wQv/LJqbVPsZYdw7ldRwwf5NjS7D8v8aLC48J2FOz7bsHqL8eKbC36oD0sf4n45+NPoscVbFl6Nz699W6OaFvWp5uli749e'
        b'z4j9x+uxX4/n15jXufq9Vmg9OG55ie26XtH5115bUvJeM1cYv3w17+h43WdX7r+49k/l92s794+2OBxHX1h/xKVy+U3Tn1798zCXP1RG/i6g9VJp572vf/HeK0avfvn/'
        b'MPWT/nGhfus3Z97IeC2r6uDtigkDhrRP/GzhxHPTXL8b530U4Y+Tlu47/01hnc7VTg8yorC0EMtCkolfwko4hhfJ3tcdLhDvm4e7WQ+4HoVXgm3Tw+JDxujCsDIEdxGP'
        b'rFVlED9Qa/dnG4Sdhq7zHXa60xf2Q0v6OjtVmfFz1gWHjZtJ/N8uMrUGKhSh7rCDnQulzCFOOiQoDssNPOfqDiVk3TXzJtqZwR224Q5DPFREJo1JcuE0KoXroPV2mk3k'
        b'jhtDD17IdMTx7iFr1kGzkus7SYm1s+G0nap37CRoNqSEBqqJtRTzM0jgOqFzffQE4kkPnfrJ7Q9PLXzkUwu7aLRKRvkYnR1eFNFsaKYX78preF/eQ+HKe/BeCvJJ6UZg'
        b'PrwXT8+qXHk39utLfrzJ/10/5LPCS/6scHPR8HS0G++n8FG4KlRqFRntzfsRmIb8DCTz0s9evOjBPTzz8uiOUrdjkidTpeNFzy662FSzuK4Dk7u+3Q9Mgqhc9iQvc557'
        b'hetI0AtOTgzr6yZLIljDzYWLLkT4jZ46XvbE11yw2hAfEk8iE/EuBTzUYnNwjzzUsyttnC3nofQonfvpYXqu54O8VPHEvFTJDtFVfy0kk7ppu/1LpdKStMaeNxzs2mRN'
        b'kaBNWhAdOVZrE9mHiLAeQ3v8EW/XioLdIVrpXBazZKdTZButBVqjyWRzWO1ayW60C4WC1S5pV+WbTflaoyiQMUWiIBGgkNNjOqOkdUgOo0WbY2YCM4pmQQrTzrBINq3R'
        b'YtGmxabO0OaaBUuOxOYRVhPpmsgstI+lx1TsqFPuZbJZiwWR9KIXOw6r2WTLEQheotmaJ/0MbTMeYrFGm09QozdKuTaLxbaKjKQTOEyEdCHmyVOEEh7mCGKmKOQKomA1'
        b'CTHOdbVBMxy5BPc8SXK2rdU9MvKnY4g8srKSbVYhK0sbNFNY68h74mAqAkrmw/VmEohFMNvXGvMtj/Z2yuphZ4PNardZHYWFgvhoXwLNFsTudEgUkcd3zjZajISCTFuR'
        b'YI1h7CQDrLlGwnjJaMmx9ezvRKZQxmW2YDIXElUglFJGPa6rySFSDq15iM1irM8XHdbH9qZn5DHsSeZ0mPJJN4n85Sh8EtYmi00SutCOteb8H0A522YrEHKcOPfQl0XE'
        b'HuyCldGgzROyyWz2/920WG32f4KUYpuYR/yLWPC/lBrJUZhpEoUcs116HC1p1G60cx12yZQvmnMJWdpw2etqbVbLmv9RmpxOwGxlVkodhdZJmmB9HFns5uFnqJopWIyS'
        b'nQ3/v0FU91Qh5kE46x6LHvi7Iptkf3QCp2YIkkk0F9EhT/LcVNaCOfsJGNPIZTd2KddiErnIUhbLEzTMuehDdey51pNV8z/Nd1EgUZQYXYyWeBnScz7eMhVkyws8rj/1'
        b'RYT4zAKhm6i6ECIssOAtSRIsPzfUTgL8E5jonIf2eDyyP4m4Boc1R7A+PmI6lyUx8jGxuufCpM/PzZFX3DPuzqXSxvpcu0Q8VS5JYmjz4wYWiUQAxOcZH79uqrNZsIYm'
        b'i2FPwr7H2j/B+/Hx36kIj+QAPQY/MR+Qx5rJ0o8fGD9zRvKT1S7TJprzzFaqUj/1ISnOtmymkMSAtXNEoTBn1RNtvfvM/4RCy93/k84k30iizWNd3lwhG28Rs36MT/gf'
        b'QIyaAbMz6ud64LWAtPy8sVmNhcJDb+fMi7VByQT8WD11iEUsL/rJiEWCuEqw5lCzXLtKMBU8brQkFBljuifWZIJuWf1jRqRbrStitAutBVbbKuvDrDun+z7AmJNDAKvM'
        b'9nyapJtFmqUKotmkNef8XIYfQzatxkLqNglOC/IfqffqOTDGuc+JIfuCx0WGnr0fXATQnZzfTy4C4uSim4lZrEAp34fL8oiYME4+RX92LKtFSm2IzfJ4RZHCsRPf4UPh'
        b'KrQpRmETx03iJuU6WNd9S11o1dMS1xFZHpfmh8unXIOwGS+wQhrcgTfoqfcIuMsu94W52BgsYlXXPvXBLnXYUPVAKJ2k83DQGg88Hh2HZeEJ8aGwOzwhyRCagOWGZDVu'
        b'9ufGYbkmOB5K2AlxMrT1Cn7YnjSO84E6JTT7R7GSECyBC326H39Pgf30BHwiXsZd7KAzaWF+1yl3MB8L5fIpN1YmyfVn9bgjE8v88VwwliclhCo4V+xQwG5oxIuO4bRD'
        b'A1TGG2LyyRLxuMdAduBYGR6H5UpuqI8Ka+C21jGSntc0QRvsMXTrdRiq6c3LrvBkNRcYrJ4MOy2s51OCp7MbXFhsYNUP9AynMjmJ53RwSw1HsGKdPOc5vIj7u82ZDvtI'
        b'z7LweNI1MEs9HVpxH0Ny/gY8ExyG5WSysAQsxbtJuCtEpyFSqlXBaTgCLYxZ/liHe539JNgSn4S7aa/+/VRjs8ewiVZBOdwOtkLl46W3CxvZSWafyXBLH6GilVO4Aw5x'
        b'OUoftkBINLR0ExaewVKnuDxAvgjwxUtwRx+hJhrkC7UciVkcu93wmI9XsNplOhH5WG4sNEA1OxodZO/dXbh4FdqZdMfhWSa+HFrq8FC8uGWVLF44D2U6hXz2fCgSm/Uh'
        b'UA2tRRqOT+TgEp6GO2zVmNFuemglH9LzoI4rgK1adnCeOzMZy/LjemoEXpil07DjlTw8ijv1WI7n9EVKjjcQ4VvhqHz42ySQGRt667FZzfHzOWiH02HsKHkiXic8WzRL'
        b'L5IhKRxchnoba/CaPFdPaN+sx1YyZBEHV40T5fPqaqyGJr2e57hCbIRTXMGkUMbDDdiRo9cTFsLZfDjNWcZDBTPUe3F+XAjHxb0SmDU4PHaGbNNwZR1ck3gHXuO4WC52'
        b'/Uj5Ljfdm1aXapdvzAoZqdnE6ZTyZdKJNOgwwO2hhOXljKOE+BoFHIifJ1/XtOK1YYaw0DFUvnBJZcnlei9SWgLxmnzuVIs1eJAePKmhaginUvFwfLILkYN8/I7lkfoB'
        b'gx7wbDjeli8ArqdE6+nAh0zLxvPs9g5K4JzdAEfxxJPMrz7DOX0QdGCJPnDTA/5OgzNOxpeF6kcqHrJ3Bex00BJPONY7uJtx8XCyh70m+bDhBn84xWQA9elUBngFDjp0'
        b'dPh5OA7nnBPgEbz9WFseDMedRSVwcRQT2gi4QoWGx4OYkRPJVpKxD/HoBU09jByb4BhTVgPRmUq9nlidoRCOc/kFglw6ke9FayrzXaOzEr3CZ3M6X2bJOXAStxjiQ5PD'
        b'iJEnw9Eg2ZKV3CAoVcEZbMmTr4H2uDiCZ8NuWkwYGq/ierkooAIuwHn5onwfXMdaJlDcDtdkiU7FGtn1tsOeAAOUzH5UWbCNWCdVpwI4C+XBCaGG0DHJ9PqpDm5wvfOU'
        b'wjisdoyiM+w3YLt8O+u8mj05Hyj76D3goEQVvcCGm7ImnIVDow3YGtG9d4+L3L2jGVYDSDza2t0HNeBupw8yDWaRJxcOaWWnAhW427Nb8OHGmNSE9pOzmOMInjzGAB3p'
        b'Dy696Y13CNazy3W8i614pMfFsGrhaPleuHgwsxUH8TNnujuv4WOY65paIF+an8cjxoeey3257LhmQpksl8tJkc4LTqJo+9klJ9Tq4SLTPRs2LDd0sZ145cpw3J1ILwII'
        b'kF8Ad7gIOKSJL4RmeanWaKKoWBEXkpASqsGOQs7doCDCqBZko68MSOq6gyWMLybaSe9gSQS8Ll8jrsAm572uErexq91TUEqUks69Bm7anJf7hNf7oYHd7sMFMpZFT6Jr'
        b'dVDmLEEgiUJp9zIEbMcWuXzqFtQHyn7jBDbKaoaX17PlF+AFY3Am7OqpoXv6M++GB6KhyV3hN50jCU8aXNQy5sHpQTnd1G6XimkdnowlvoJa0mwB90p8X9jMXCLeQNlG'
        b'C9KwyZ0WoU4hgauB1nRdsclX71V4vD9W81n9WZnnWjjEgk8K7IEzhkwSCB41gGa5BmjjSlYFnqrPzwqZky5wTOlhB5wI7aH0N5c+ovTtXeVrDQOmYTUeciEfTw2ASi6z'
        b'GCqY7/J/Ci526fA44ScqXKyTLzZJNL8MbWOVhDt6OE/Uph22OxbQ8TM3SES9sDx+Xiq0jk2bjztZyXhYaBCR5Bjn1XkadRo7QxbFUfExFZkXF0JbdvXFUwTzhalYruLg'
        b'7ro+UO6awi7Kg9UsryzaasgKgWw1x4oopg4e90AH4GpCDxW4ireJVFgcKAvEDmhLxLZIGqjnkRCxAM/IYXULHNZBG15yiSziWYi41DvGwUonrkwmBl9dzMHOeCKmg0QF'
        b'dxaTRzlJ4Zqi4JIaWrPn27PhynieKJBmKd5ylgCVwLZwkrJVwvEHUxKt3UICIcVl2QSbAY/pnMbJaTIVY7CpD9P4RHtStwi4EVtYCMQSbGC6t8ITmg3LlY+qRHq6rOhN'
        b'ULUa2qLw2AMa4QxsluNROzYkPcjiiI1V98jixAzmeeBOgsnZiSQXdd1zuFnYqFOxDAFvJ+URga+LWkmCYQIhzcWFwf3t2KiPpIUbR7GS5G2Ch8Tg5nS4qe8D1ZHFhBXT'
        b'OWgQEmSR1OHFjdDmpScpFMeiZ2sMbtXxcp09NntBmxFaIseRtjm0c4XdMYO0RM3p7U6sooxIvCwcK9Ow2ZP2So3rUrn5oYvmx4X0n8B06YEiEWU+7oZH5oKz4KU8B/bD'
        b'BU0gniEJC7d+rl6WXMNTWEW89DUxCloUnMKP1vDuxqvyDmaDCBfUcIj4tY3cRigZ4ghh9r5Egva1xEvtDp8fRK8xqd0t7rH44lAXOJCHFxyTaBpMvPNF9+QkLA9dJFsG'
        b'3tAQY1gcl7AwboFMDjSk4s6k0LDkxBQ1TdWb3YhOHZvpLJ6BmxO1WK3etE4u9d7tJvPzImz1pVkdyQN8FuNhDi4sxZtkCNUcO33VoZtqpSYwzbKY5YhThlug1kC2FRcf'
        b'1a3+JCOhyuUg5ByhJR1XPXk1HuMUeI2PXGJjEWMhYVLZE0PGKDwoh4yAfDaTNxCiJbxa1FszBraSiXbxo+ZALeP/2BF46UEw4eGYHEwSY5i/z8BTQ7uSDtgOJx/JOqDB'
        b'jVV3mRfmvaOSJPLx2gvRjgVJlb4LfW//5XTjjcZ1uTdqjTvmDHaZrUmdbvd9dtHs5z2HWZZs7hX47L0XTu2rWGEaNevLjJmWJLdZiT9uXrpgwKGw5a1Z72W/H14k/L3X'
        b'D9yhulUX8mpUiWc+ObbqDzeH/uWOdCGy3+++fnZyYEpixnu/u3jr8JzfVxraZrz68Q8HrwkfWhpG3bi+/Km80b9Kzwte2HcOrj18a2XxV6+v7ncxN+1Cg+4HRZTlzde/'
        b'q/uiqnLD+9kV4oq/f7Tgi7TDMc99sXlUQtXpX8UsdNk/9vbfJwcmF8cEZMwd/d5p9dCbYVs2xAQWrSgacH1Tx2f7Jof9sLLX8GsFjhRTSl7c/Vc8za/5DDrREPAPz9pv'
        b'J9c1Zme8qTb+yP2+39UxLbXrEqd9POOFBM+d33fU5b8765675TBXMNX389lfvF9R1TfA7/vLz/7Z51QGfy3k3sGiuU8fU0x4Yfz1oSWT3C71/o/xRWfvp1037fttzJtv'
        b'lKz4cNSp9w8sfXbxgk+yXga0fRryXdG+A/zCeZ6Vz1Ud7j9p0lsJ0hFhtT00Y4jP39bvPnL1/sTXB+U+d+4FXaxn8ocD79WeNw98fsbnq7d9tmCTlGbfW7IhzD3g25yA'
        b'dfd2vvhNts3aYdm0+PXXXh/R/523prqfbbv7l0O5z9ve+3BG+JCWTxL/ev3WrPeK8/48sPPfNr4y+npT9Bt12+8le/7xzuqkV954/9WIzIJTC8cd3xLmsTr/F782TQ7+'
        b'brPPyWcW/ebdj1e99vfChm+Tzs3boGzP8Ln7wUs+jV8fe+qbr6Jv/em5sD43fYr7F7169v4Vy+Jed90zvi/5txsljSXL+40ZvLep35ee+U2Lmjv87c/95eWvv7oz+4el'
        b'kc13Lnf23pxs+uusL3602D3u73v37Xn9O1YUt+gz/7x0Y8sbH8eOv1KbNHfj9or22I/f2n/5td9Dwpv7p1mXfBq4x/B5xL1Jwz4fbfQY8vLx4RWh1ls3TH/7YcCwjCWx'
        b'L7m4TLl9vp/9fOyL8+bFLfo49d30p5c+fVGaVHsNb33y+YA9N/5deOftP4TqFwmf3vjNnWPvvmP/seEvU2I+uXGptPb5Cedzph9Z/87oVb8RDt459qL+fuDIlLfWVC19'
        b'4TPDwH+/6fLa8CnT0tyyl7/92+tVUzeNir78QcCy9UkxV359fFvbc9J7l06nfXY/enjd0xbl+J1RQz/vz/feppgwPOePn46MiAx8Lb7sxqn3da8P/Mebqb/84pNnbpQv'
        b'Pvl16vG8H786V//7/Rt/HCqqLa80tOu87HK4gQPeJJLQEhE8gdeIpVJvGEpiCVxVxYX4sFdMfHDr4GDcDA1jwnTEpjmu11IFseMK2GKnKZABS6KDaY1KX7jSo0wFq4bZ'
        b'qVObglujg+mbHGHda1GWYJudpZ7HySa3yoDHsexBRQotRynGGtYeNDn3QZlMCI97ZzqrZHDLEvYiVCTsSupRlqIkUx2Ry1KgFQ6zQhk4vlYIxlNrkpNCErCCloR2KFat'
        b'xkus4iUHtvYzSHiJeMPwUJLrrlKELU9npOF13K80EJy66FoOZVzvsco82LaSkUYc8TbJANXuPbKEY7CVldngbi2cCzbanWzTwEWFPgeuMKa6FySQ9FR+Zwe2Dut6bacC'
        b'b7Dan8Qi8rGNyIJkXMuWFrGwpeD6TVYp8VKiru8/W1LzX3zoPP/78/zkPaNCe3TkWFaqE0KrUDZxS1x5lfPHi5Xl0B8Vr+A9eB8F/eTBuykU/ON+5PIe2t9fQQt1aE9/'
        b'WtajcOO7/8gzeMmjnjCX/OOq8OK1vEZB337y5v2V3rwXW0PFB5DxvrQASKF1lgzR96PIagoPhQfDgBUNsZXIr4LiTet2hpO/NayMiOFBRmkUbqwIyY0fTMb7kfaBZEYV'
        b'ofYh5t4KuVyJfqIvTVEKxN6EX8lddUYqeorcrb7ovy8rHS96d0mLrbWPSomCuM3c54HdK5FoKp81EHYGk63hIbkaCStD5fxvYJESO8KKerw2RyU9nc5GszmBvnXNLVPk'
        b'8MuUOQq5kr3Tmx2FszIhMVYUbeJ3Q+XDcaY1orPqR8jRGq1agbaHJetUna6ZmfQ2ITOz0y0zU369mnz2yMxc6TBanC0umZk5NlNmpqyKDx+MTJqgVRLsWPGYq4KdCkTj'
        b'dh93L7xmd+9FSQsVmdnp8YCCC8fjGnUvuKvj55h/WJ6hlPzJ2C3j1kyp7EjGVO/Yd75q6zvp+//YPv7T7+/M2vvxfc5t5qH3X0iq9313x1ZN+tpfx/19xlS/SdrIl+9N'
        b'mivl3bn3t6qGI+sDq0x/jXpp7cW6uCtH/v2Vy8+/MvnVZ3blLg/6oWO5Ye/f1P8x66Mz95bcrpi5q/8vU74NGbVC1xqxMX/ezpyP7uyMN96/NuyXBSmLHVNSfXXPWU9d'
        b'fyP6M7Vfv8aWQ2++dv7VE/FlUUPW3/i6xlSn9luafXhq8MXW52MGWVqfi5r0aesvproMFp/9ov14XPLEP+6RwgJdzxZnmxuaIq9dLNiCIxebL5kGns3qPFszKnOTIfTf'
        b'1sw7NP/svj+ca28a8vZroZ+5CNbr5W9/eqi3cWDl1kmalizvxrjYiD47R7/33DTBc9HKfq/rVHZ22tcMNwSS7pP9xETOhcOKaXCbOTfDlPyHb64631qFOx4qV9yLV+00'
        b'h4RzcBBq3McQn0qd+oOO46xDoU2Fl2PszPfPC82WoCkuOVTOMfeRGEbyzD64VwnNeBuvEMVm+u3zL3SVGpbNPvnBXCBRV4vNmJOZyfwfLd/n/Kg/iiQ+hxYV0jJDb1dv'
        b'lx7eS+30TErfFNJzE7fBgxf7d2kxsRwFUe2HbqDPv4Y8XvR/YDN0cbqFkUsUPw171DFY4QyehjKyob68lO7zUxJhF1S6cF4DlEPgEG9uLLujYN9h8Itz+UOeH+e1dbr3'
        b'jt9uyl3lac8+s+Pdk7fg2SUXj52xjxq6zv16w7OLbzen/u5i5aJ13+e+3D8z7f7GCSWxjd8uPPLD4int28dGlFTUjVCOPqrvfylwzihr5TBxv+0Ny9tcy83v/tT7ud/4'
        b'X/+Vu86Fla2qcTvWsrdLU7BqLNvuuJBw26rA83A7304RJ3uhvf6GlFBsIb3wCpalpIQqiB7dUsJJvOIn96lbCJspcXh2PFbSozAoZ8T5KAOwtS8rfw0YFmuIl8tmbbBH'
        b'pXA1KFiwHzsHSgz0Cw7grNX5BQfuOgXu9ZvDmheuwcvs+w8WQUf37z9INbNZoSlzUHDCGmxU00NzrMGW2V2KHfAvTgT+q1qj+llTMFvNdqcpUD/BebrycmB0VYZs4ugP'
        b'Jw54oOjaTqVFsHaqaL1op9ruKLIInSp6MUoiodlEnrTmr1Mp2cVOdfYauyB1qmjZSKfSbLV3qtnbzZ1q0WjNI6PN1iKHvVNpyhc7lTYxp1OTa7bYBfJHobGoU7nWXNSp'
        b'Nkoms7lTmS+sJl3I9G5myWyV7LRQrFNT5Mi2mE2dLkaTSSiyS50ebMEI+WK601NOdMySbWLU2HGd7lK+OdeeyYJWp6fDaso3mkkgyxRWmzp7ZWZKJLAVkTClcVgdkpDz'
        b'0JRlsgNE6iZE+u0IIj3AEKlfFGnWLtIrV5F+z4ZI9Vuke3uRHpCLofRBDxhFGs5E+oUQIlUwkXpdcQx90BfNRarPIi0qFun5mUjfmBLpRYRI33wStfRB01+R5t/iePqY'
        b'QB/BDzwBlU6vB57g2zndPAFr+86169sDOr0zM52fnS7wu4G5Pb8lRWu12bW0TchJ1rmK1MPQ2G20WIiDY3pAraDTjQhBtEv07r1TY7GZjBbC//kOq91cKLDEQYzuYt4j'
        b'wb7TdbKcIkylf7FURKUg1inrmrcvdbL8/wM1fjyv'
    ))))
