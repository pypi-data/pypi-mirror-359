
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
        b'eJzFvAlc00faOD7fXBzhPsMdbkIgHEFQBBUF5EbE4A0iBIhgwBxe9cAbRBTqFcQj3kE8gljFG2farj22JaUtkW2tvbu73RarW2272/5nvl9Qqb7vf/f329/78mnHyczz'
        b'zPFc88w8T/I5eOaPPfzvg+W42A0KgQpEARVVSHkCFWsee7oVeO6vkDWGYmphwy2lfNzKnscNAGOGW8bj/8sx7hTWPF4AKOSMYMipeRYBYN6TEYSgkmu1UcT7WW5dODMz'
        b'fYZwcW25tkYurK0QaqrkwmkrNFW1SmG6QqmRl1UJ60rLqksr5RJr6xlVCvUIbLm8QqGUq4UVWmWZRlGrVAs1tRhUpZYLh8eUq9UYTS2xLvN5Zh+++H8+2fp7uCgGxVQx'
        b'q5hdzCnmFvOKLYoti62KrYv5xTbFtsV2xfbFDsWOxU7FzsUuxa7FbsXuxYJij2LPYq9i72Kf3UDmLXOXOcksZRYygcxWxpHZy6xlzjIbmZXMVQZkbJmDzEXGldnJPGRu'
        b'Mr7MU8aTsWSUzEvmI3OM8yXEXmSp9J3h/ZSASj9fIPN9+lnm97QuBCm+KX5BwP8FrRUgme0HKiirChErr+xZtjni/53Jdjk0pyuByCKvxhLXOUtZoMWW1BbY+I/jAG0w'
        b'YS06BfWoCTXm5xSgBtScL0LNmWiHi2xaJA+EpnHQzWp0WURpvTAsakHX4Dl1Zi7ajrblom0UsM4U+bGgUZxRRj2zAqeRFazHxQTHYrwKTBqAycXFBLHA5LPCZONjstli'
        b'UtljojliojrHOQ0TiJrxjIQpWZhA1DMEYo0iBZXCogn0XOsTAlX+/xMohyHQgzoesAGgihW0IOLjvBhAN1bnswAGnPY1Z0HOlMQkptHJxwo4YOINKBbUFHhPYBqvpHIB'
        b'/nfSoswFOXvdM0EHqLHGzUtjBDPOWH+Dif1p6A+sizETBMdADVG3/KA2ymgBhNEKbfBHqt0O3zHNvrIH9rvsqbChSdc9f511cvxRMAi0UbgDXrWrgVvRZcytpqiCsDC0'
        b'NSojEm2FHTPCsnLRjghJZmRWLgWU9lbJcB/cMYolnJE9lxOWsGmWEHaAOPYTorP/g0Sv+j3RLZ4jOp8h+mSpPfAGQBC99NWkpZJEZqs8uBftw/vcJs5G21BjTkFGZkSm'
        b'DMRmF7rCXTNgE9ztCPdhk2KBDqGX0RUtkTjY6iSRwkt4fNgBMkqWLArUuuJmPwEySOEF0nwAwF3w5WrU5KN1wT3e6AzqkMYS1D3AD3WXwc4irT3+WJjCc5+GdnIBkACJ'
        b'jEUv83GeNcBIltEhEVOuLFIwHJ8R4gSC8L/Rkj12b7u6AcX33iVc9VrcYhvyc3fZwTcdoGHx3191gDVv3ga8W9uKvrSxaVxlY2Oa5qgXFFp2S7zY7Jzc8DJLdXS3jM/e'
        b'EHmUNyM3wJm9gTUlmj85iBsA9/3BwTquxD3s5be833Z79e16qv5EDKe7u77qxwXp0X8UvH0L6u2XySRqS+fzYplg7FywucIxcN1LItZDYvVUWWgHH1NQlKuNDMfiwgKu'
        b'cAsHncq0RD1o/UMPDJIHTwNM6K1oB9rGBhx4zn4cBbsi0UERZ5AVJlLZkmGeFGrCPWF9ff2gW1KFqnalXCmsYGy2RL1MUaGZMGhNG+SS8lKNXEVoySJYdYSA9eB+KgUc'
        b'nFvGNK3UFTSt/chN2Oef2CMz+U/ud5vS5zDF7OalK2+tGXAT6zUDblKDpmGq2cVLJ2/Nb0gzu7jvzWjN0Mn1k/UFOoXB1bDE6GjwNMp6YnoKjHP6fCb1u6Q0pN1xFupd'
        b'+51D+2xCHxCpUxGxE/EGuUtLa7TyQYuSEpVWWVIyyC8pKauRlyq1dbjld1vkEQMpJJtU2ZFG+5EikPTG4eKnevBoCkVRzp/auTdV1/OHWFzK5Q7fqWncpxz7jblmS/s7'
        b'ls6P73MB12Hk089qIi87eYHgKF/CLmO9SDUriGqyyAFFKyf1jHKyRllEtu8o1ZOxR6khK4VNK+dzrf+1RXyyhCfKycujlQd1oqvQiHaiw2xsTSJBJLqAerTY8oGgFQq0'
        b'swA2Yr8iCkRlsBgVbMtxxXpTzGgO6obHFUe+VrHVxEs42f4JoxEur96up9Z7bGjLaRN+O++EQ7qtYXmAeNr2cRsz3QPe0XPe/OX9WusPzsHeNjtgVchrSbQUUQ/J8TMO'
        b'bawTZ0WihsycPC7gwy4WuhCDDsDt6KqI/XsuEn9nhIWDfEYoK2pqSzUq9xGpjGCkcmgGBVw99+a25uoD9ep+F3FD2l17F7MAS14bv4V7x9lTN2bnhD4bf5XDU4lSkUNk'
        b'kFsuX6jQqMjWVc4vkCJajBgpch8pxCNS9DOWokIsRZ7/rhTt4gWBY/woNm2CXrF0puKKgyzAtN7FujzHUi2ZA+1Hp2GDWhMfzQGshUA6GZ2A++ExGqF/gSs11rOGDaJ7'
        b'F89K3O1K83lyJewg4BRgyQHUJ6OOGHiBOdRK3KikxP0cUNe7WLDqeD4Nvhgeg68QeDZgVYLJIagTngijwa+LBNQku3/g3feu1nm+NV7rRpZzfDHcotYkkNUoAWpMRKfY'
        b'6AAN/7DUi0qNP02BSb2rBSX7qrQCAn8IbULbCQILsGoBOomNUyfqLKcxND7eVEbstxQQYgyHtz1pDCwDh4VqdGEM2QHcAIqXYeHbAFtoDK6VL5XDOsIBC3pXm+OgJ00i'
        b'PjwMT9AYXIyxEYwZjy5MRYdohPXOQmpa+gAXOPSuniX/m52W8LYoY5FaRY9fCyxRNzqdYEcDe2UFUjPmXGNjBqzWLaukaALBa7G2qFsbQ3YMd4OZnqhbFk+D77IMomaF'
        b'ePAw+VfPWvKTFU2gKHhDQIPj/eKzKAO2ogtjGYK2ZodQ89Y4sjD9V5vTtxXT8P5oN2pUq6Vk+LUgAOnQWbjRhYY/my6iFijHYCntVc+q2hBIkycY7smlx8f8wucm1GH8'
        b'nmDEcPiuJJwqn56IVeKWWse6MoXGWDsVnqQxLDBGO0DrUDu6vBKeoTF+CI6gqkJCCNPUOseUcGbLBxfaoW61jTXeA3qFmsuLQ5fW0OBhk6OoGs+5HDDplto8pYnHgJ8P'
        b't+KraAGFJ4AyEV2CR9JocN3YaKpuZTZ2jHrVgiVTq2h2VUvhZj7qGkPgseOZBS+yoQEy7KpbGUtpFv2TA4S31AL33TbDItrA5VvHEn6hPRRekFUq7KZ7PND6FXx0keYN'
        b'2kTNzqLWwnq6Z5p7iRp1L7MjOzhMOaAj4nC0UUtOyRzUBA1qK1tkJOPdpGAjPBGPrqGDjHy3JsEb/CVadBFbFtRFhXOC4WaGKug8vBKs5qs0BE9HWQh94bUo2vsohBcW'
        b'qDXoEp/0NFNua8VTOfRoobANXVTb2WJCsrkUWo9eSfaH62mcBWhzEu6xowDbioJH3Sah8wsZajanw6O4ZwnZUw+FLkVKpinp0WAPOoCu823r4DYOYAdSSWjPJG42PdpC'
        b'dIlFRBorQB1IsUZnMtAZukNutRwrdxwPYH8ObVyBOtLRPmaa69FJROy4tJJhVwydj3fVepJ9HkDGcjXqQt32hHpnKXQTnoiDBtRGr6LGBu1To4vDvacoV7ROqpgtsqf5'
        b'F7kkjlqeFczC+qnW2c7wohsDVyRQq6wTuWABZmrykgLGuqwdR9WvnMvGiqkWWA3NZiQ+J5HauEaLXQssvwWPK+nGU4pkqmFpCw9rpVo33mI83fht1gRqW3EVZjQeM+yr'
        b'OYw9XDKJapnQy8IKqZ7leZKRQTvWZGqXnRNuxCIb5M2o4rbkNErHW0FhVVQLimY6Meofm07t5wXiRgxp/x2j5FK3TEpfPAerVG+1TqQW0o1vTculDMo1XKw11bO8LTzp'
        b'RvPSPOo0y4RV6Va1mbd9Fd2YmjiNMob/wMMaUG1ekCKnGytXFFIXJmxlYymv1glZEbRRSkU7ytV8ayIQNlQhapoEFtPtskB0iK+ys8Ui5Eh5pidL0FGagT4h7th0XVqG'
        b'j0cixjW+YniNSzMQHoc70Sks/tgmEoncRcWgpgC0D7aJOPT8M8EfqP0TN2J1u7VMMGFASTd2iN+g9Pm/EWtTq8s+q6EbWxa9SR2ziMZnwK1ac11dJN2YYf82ZViGKTKp'
        b't1Yg2xY36nbCHfE/MG/ABO7whZFDXxZBHPd/5lrIA793gkLytMSLhldtUA9syse33h2oMTNXghqxJ+22ICGVEyoMp3e3O4dNO1HRRXeFTWVs5nZQLLEkl8ToaLfesqTF'
        b'8wFzUr1iHZwdNRNtyEbb8zPxhRFtZK2AXdlM5xl4cyLshheKSsiNhZoN4Gl0Fl1lVKyZ+OjiMOzJN0TloT3LuMCmkm0Pr62mfa8afMafQOdCYTdeSCJIrOWoyCLolRxI'
        b'5JCbqTCaZ+vXUD2PaWxNpm+7DtFL64rnxb8EaMGZELpGGk1W8vJMdAKUolfgJW0AYR/cA69lo61e5XgRO8j9PxvuiMqEZ8LwQazh2hXm0+hwXxrcKyXeDb5ptceDhUlj'
        b'tX5k7Xp4EF0S4ysr/XCA76+ZHOAsYgd64w9bq7XEmwqrmTt8GcNDgzKhP+PKXIHX0TEpPE8ucIf84Fm8UR26SM+GWtE1uFMqpU+fFVNB5eqxtP2Cr6Dj6JxUijkKD88r'
        b'BIvQtml0B7ZP++ANaTyB0dX4gfLl+Ezwpk8jz1J0XJmdRdaWx3DGro49Fq6Hm2hMFToqk8aTNbThu/U1IEc7s2iujBOjV7JzMEoUahbDffiGw5+D7d9S7JOymMPhJmwJ'
        b'k8azCHEwEY6ACtQMjzDmdDe6jMkVT9bZHgIvgkp4QMXw+graDztRUzYhV8NkLuD4UvAIPIWXSzbuic7Ml8ZjDYL70bapoArtLae3ga7DDnhATNiCGvPgGVu4ngNsktn2'
        b'a+Ae5jRYj7ageimeCtf1fBdMzDOwk3G6jKHwFGrKwSRYhDazARvdoGD7sjRtPu6chwlxSZ2TmZlLHome3MrDJKLwXIkokmUNj8ux9J2Ax8LCYAdq83QTi/DpcEzsAne5'
        b'uaJj7vAkC8CtLg5QD2/AXTWPf/vtt87yYaFMj5QuySgGzAK3w8OR4rzIDDzKXg7gTKLgqaoykQtzmG5ehV5W26q0c9FpYsAOUoFWMxgpuYBOoMOo206ljUI7Sd9FSpQ6'
        b'h2adbJUQdWMkj2rSfoMSo9POjJjs10xTY4ycfMbg+clRA8Oyy7GwXb1Ea42F/hRxKK9SwhQneqJp8IIdPsiWoQvwvIRL+yL+7oghLgu112H3AV2wtUcvU7QnELs8gJ5q'
        b'9SzUwrfjwx3VUmyS51BzYVsAvaXsKcTRtV4WhbqJJ3Sd8o6Du5jN1jukkR60ZQWZZx0lDEA7aWcEbs1wQN0aFd70BXSGuHQ3KC+81BZaNtyWRarR+RVlGh6g4EGAdtg6'
        b'Mar5yhJ4nG9pa52ArTU7gcpwq6VHm4KFsge7ekts0AbypMdC+6hQLH1nGKybiky+nY3V2kqMNJ7KtMFrIHSAG8vw/c5eZYe64Ea8JTsqAZuqTnqz00LFuAudt61S4p4A'
        b'KkWGttIEmgm3eKiX4Il2vUSoepHyhUfhZkYVmoj/YK3SLkI3CZtepoQ8FcOlrUEsPu6wR5exUDpR0bBrNqP9+8Xwwmo22onVJwJEwAbsxRFBXgm3wCuwyd56STVrKQU4'
        b'2BmBzYXoBGMB9qFD6WRDC3KZDS1HGxVrWrQs9X2sTtI585oLr+b9dZLDgY//zv7DG8H+12p7krhxGXFxKccm6Y/FzFtxfnpWS4t+kqPTZ/Zhj6nwCfWH9J+d+0bn8Qd7'
        b'Y9Ox2+8cPKD+6u3ll76+AY13N9/wfRWUGevf5G51mUrN2rTvkcE0dtVfvjVtn5lexj3+ian840OnE/y7Pt41btGRP1SXzL8rDz9xev2vrT93qD9e/1FzSl35o+zuLdKu'
        b'uUXd4bKj9wdvuHj+edpc119cLyf+8bX6zugNXx3l2X4myN7dlW6YUpD7TrM2+tvttw9PLbbreqf4iGy6yljQ+5vlDfHjmkeBt0TKpVfjjl95NfLWeKd3Y9ZcD+v/sTwv'
        b'ZdPcnVc+rq8Ku7b08FfX3r/mtOpwfZT1mqjH78WUa/ecPPUg4Jqr6WiHTfXcTerps13/nvDGz3MNg47/OHBfocyD51W1R/JPOb9e2rap+sNx+rc/+qTq60neDyauPvDG'
        b'w9gPLq868vj71EO3m4/U/OULU9KbzVtvnDi0siQtt77lyJSvTkv9El6XQHP2mMHoHmHUjb9/np5m0d4x6Hx945bCH05LL2XPi/xTwXHT5VXnpoVckdzdmfDnbdcb0quu'
        b'f/ul4i/HQg8ErSj+8MxvR//0W+PaX1WrEve3Wkdun/72pnkWl7545c8G9rjQBe80O66a+G5zpfjnjyXX/7Zx2ev4snsp1HXxZw/d1n9du6luSZb7cpHlQ2I3FxbCDagp'
        b'Ig/bNLQjAq2HJ7EZh53YjhfPoJ8e7LT2YklmRLhIQvobARAI5bCTU5wEW+lXNNgYwxt5RcsVYF+APKJhI36J6TXCRrRdLMGmsxEeqIigAA9uZ0VWOdK9aE8eWpcd4Z4f'
        b'loGasylgiSdeAXeg6w+JomXlQ312Zm446oDHcy0Aj8OyRDfRlYckwAGPFawVZ0SEo0a8JmyRd7CB83j2NHxXbi+veEh0JMwencjOx5elSKxwS6kU2OQrsv3dU8m/X6hJ'
        b'IRz+q69/8szixDyzaFSlSnUpE6JRkUcz+rXlLIt+bXmYygIewS0cs7uXLsfkLsI1F4HOu88lxOwfrC897G5wNMTovVs4LbNa7QhQRuuaAfdIk3vkgHuUyT3qXnB4S6pO'
        b'0JpnDgnXeezMN7t66MJaiwdcJSZXiUE94Co1uUrv+QboY9oq9aX6hbpqDO7YOnUYfIgHvH0PJbQl6OPak1tSzZ6+uiVtoS1TzF5+hxLbEvVl7RMNMYbYPi9JS+pH/sE6'
        b'rlkYrF+oX6K3Yqp4RLrqJdSntiebpWP1vv3e0WafAH15+3xz9Bi9V793pNk3UK9pX2zk9rh025qDRIYZR3ON8h5N92Kzt1Dv0ZY/4B1r8o41jvnQe9wIalSc3rPfO2Lk'
        b'o0Sq92jPJ59q+n1iCZpbW86Ad5TJO8rI/dA7fhjuU0mMMbhzkS51BJrgiqP1bu05+NOh+W3zD5W0ldwLj9K7tmcP2QGfwEM5bTlDgApPocxTMu6zqfBM6iGgfLKoe0Gh'
        b'h7ONwaagBF2a2S9Qn3lorVkYpJ992N7I6hdKjVqTMOkDofQe0zYgjDcJ443aAWHy/UwKBIQM5WBHMACzrajVZojF9XRq4Q3ZgMDQFnt6z/vzMbHDIs7ZddgZ1f1h400u'
        b'wS1peu5dd8+DWoNrpx/esK6ozUYvMwnE5vCoffafeITp/MwCb7q1pF8wpsfFJEj+QDDmvi3wicBbwVJj1TqxLySx3znxXsSkXpdexS0/U0QBZrdba47e/X0XEZENUWtJ'
        b'X9iED10nYA7reW1JA15ik5fYkD7gJX3fS2qOSustvz3uVq0pqkjHoecqel8Q8cNMIqTPvPdZDtqMkuoXvPj9XkfoONuz6kGrAl1MIf3jwPBDMouiPO+D/4N3wN28YHCc'
        b'H80WUcOuUzCqz86MwJ41vjoEwFdg+wJ0YNQ9y3bkikOCwBNsh+9ZJCgHng/Lxdk+uXdx/oP3ro3YL860BsB6GjEWamHp6OAtHRFeUScX5s4YFxctrFXRlViJtXWmRqiS'
        b'a7QqJcGpUag1BHRhqbJaWFpWVqtVaoRqTalGvliu1KiFy6oUZVXCUpUc49Sp5GrcKC+3LlULtWptaY2wXEEzslSlkKslwpQada2wtKZGWJg2LUVYoZDXlKtpXPlyzPUy'
        b'jElgaqzpIALTU1arXCpX4R4Sg9YqFWW15XI8v0qhrFTjtaY8nWGFsApPS4LcFbU1NbXLMAQB1JbhrcgTra0j8R7L5aoSlbxCrpIry+SJw+MIw1K0FXj+SrV6uG+lCEM/'
        b'D4dptGBBXq1SvmCBMGyyfKW2chQCIRFZ3tNxJ+OWGrlCs7K0qoZADNPvKUB2rVJTq9QuXixXkX5cWyhXPbsuNZnkKcDC0ppSvKKS2jq5MpHeOgZSVpRiYqhLa8prRdbk'
        b'pMATLWbmSZWXKRZjNuDVkg2OdJdpVWRnK57ONBMdq1JplU8gSFgpkS4xrrasCnep8Sft4mdXUVZTq5aPLCNNWf6/sISFtbXV8vLhNYziTxGWIY1cSa9JWClfiEfQ/M+u'
        b'TVmr+ReWtrRWVYl1SVX9P7Q6tXZxSZlKXq7QqF+0tkIia8KpWo26rEqlqMDLFEYxlkFYq6xZ8R9b47AiKJS0BBMFEQ4vVa4cWSYd9PlvVjlZXlOq1tAo/zuLfPaoSnxi'
        b'Kp+1eU90uK5WrSFIwxySq8tUijoC9l9ZF0J/uWLhM6shVlFTOsLYmdgq4iFrap7h7nPsHz3maFH4l2ikkmPriwU1UYg1DfdOR9fKqhcyA43AEB3EGyiplj9DypHJ8DZq'
        b'0DW1Wl7ze3ANNvr/xeaHcQnE04U8Z7WztcpyufKpBR4eHtvcF9j40RNgmN/jVS4dbbunEg6gYxUaNdbQCnxoke4R4DoVJhbW79IXjz9tuFuujMxTSZ5d2ag5nlvT07Ni'
        b'mDm/Oy9GIYw6Oxh4BZ7ixcCZk1PyRrO8pFalqFQoCWuf16/84b6FtDBgBRCmq+SLy5eN0o9/QYD+ZUWrKsVW8IWqPlW+EF3DqqD8j09KxIuWWaLfo+acgXueF1xl6WL5'
        b'Uy0f9kGEYXm4+YlcaFV19Jn4HFSRXLVMriwnYr1ymbysegRDLa8rTXzWicFIz3hHw1Bzlcr5iUKZslpZu0z51Kspf9aHKi0vxw3LFJoq4gQpVMSbkKsUZUJFOfGUEvGd'
        b'sXQxMQt4vhlVv0vlk1gnDvt8icKUF1oyifWoR3w78PtH/Fwmzehu7fALfXqr66053swT+CnP4SfIeLvKlKJswDwR6RfBXXAjaoDdLJLgOH4F2kFDC52GH8xDPGxuL5s9'
        b'/GDZAY+VkndrfCu/QBKJymAzaqcfvR1t0sSiLLRNnJcjYe7nYh7w90MdqI3rWblIZKMll4HcGegoaorKyoyEW6OmeGXlZkdmoebsPC6IQc08MdoNr2rJZR91wytu4qfd'
        b'cEs2cIIH2dAID82l0/Pm+sN9lWj/c4/YDug63R9GouRP3qopgI6hC/RjtU/GSIDhpBtqEqPm3DmyrEgWsESXWXBrKtLRIQC0XozayeCZaFt2Ht7ljqgM1MwGfk6wo4aD'
        b'dBPstCQXajXaAo3PgJGwSWMU2otu4i0FiblJaPt8bSgG9F2O1nnBPaNAyQPKjrxcCojgNS7cB7vQOnruObAJdY+am4QQ4PpyDBq0gDupJFkrxGAR6Eq6WIKa8VDw4BJJ'
        b'Vi5qjBDxgBdq58Cj6WgLE845WruGAUIHUEN+Zi7aSoDcXTnRErhR609ATiF9+It4B7dCI9czPpMRlKsKVC+N5YCJcD2Ae0E5OuNOP8NHwUtez3AqAnYMcwqdW0DHaorR'
        b'DdgkjeWCtUsAbAdVsTLmRfMaPA9PpcDdaCe+dUaDaIsSmjFx2pfmoYPP8XUROsW8+vfATUnP8vVCMs1W9ApsxJctMvJai1gpPF/HA1TOfAcAz05Ex+ktjEEH4HHcA0AR'
        b'2gbgQVAtWEpPWecVy0gCao98KgrwNDwn4jFyfygBNUildWxAZaNWtAfAM+iCC/NiuwWe1UqlyMgF1HRhAoAXXPjMI++6CHhYKlVhnPw6dBrAc3DDTHo0a7SOhzHOY4wi'
        b'LD/XAbyI2qKYd/BLyeiUVErhJewF8AioRi1w+C13PTJUSqVcgBrQFcxWUJNH0YraUOgGIoiiStrHq1+KZiJbaFe0J9oHG9T4QpwG0tBldJ4Gnj3eAV9RwdjopZOndthO'
        b'AyI2ExHagXQyEuZojpqBztB0tUQ6FubNNl9GWy7C/e5eidmSyHDCZniWA+yL2DVwmxW97GS0pSoFqxu+j3MBh0PBQxp0EXODJlBHgfsw6TiwkUT9OlbSHXPh7hkjhEPb'
        b'azHlsvxopcKT7UMtL1Q+K3QUK58XPDY8eBzW62EaozbYg4mctpqh/rGZsHGEyPB4MKZxnZwW95xyuOM5jbV+aVhf86COIeBBdRzhwzS0nuYDbBDTeoyOwfooLrry3yry'
        b'PjXDzLZCuI1m2QW0jmYZqh/L7PAcujj5OQ3HDNs0rOLw5hh6f44LBFIphwgIptwhUIXtn5FW/gLexOzMyDyJGBvYrRFhIy+iXnALBx5PQAY6OOCVAneS6BVelm1kJgdY'
        b'WbDgdrhxCpPXYmfHpKK6bZPPVq4EzJIb4KGp8HrkM5xcEMtY5EZ0Ah5kZKRwxbMishWeomVkigtcD6+sFWdFZkeG55Hoin0lW47ZcpA2/WizAivP1uGI6qmFdFAVkw2e'
        b'4QCvHA58uaqWoc1xP/VTuFGRV9hYxbXDO9hKJ3PD7jJ/TLpNjKmA26OeOU3Cy7iwk4TxmHB/U4hVdlQ2Hm4zvPgkDo06YBN9dElD4bHR0Vp4cBYJ2KJt8CpkcmLk8CbU'
        b'laJNTMxwJGAog9u0IkDHNpuKGNqQwGijNh2LLNqaQ17IswklYuFeXiZsXEwvZ1oNiXVuz4jIyo/kAdiJLvOzWehgLWpkVtszHQ/yJKzJATNhEwlr8gKxtpJX8rGr8FFh'
        b'cGYCpsPRUrRvAb3OJegAGImacwFshUdJ2Bwd8GRONSPciS0OE92HBrjn2Qg/JxQeZwwo6kYbYP0MWM/HPkEhKESXKrC+kazQqLlBAWNGjMqBTMY4NlmjPXwVD+BB1wHU'
        b'gf2CWegAE1A7D7tmwZ5gtJNJqAxBW5l8F64VkyxQ9Av4bHIW44oko04h2on2WgBXa2yRQMkifJTTFkSPjhTC7mg2SFgFoAHUjofntTPJcxwWrpNqzBLUnFkwDZ6PLpyO'
        b'rSNJF5dEhmEKhA9HcAuJfjTAHruIogyyc5q4BRkRpBMrTrZsGmrGSnbzJUfYnAJb6YDtRGsu4y0VnXD/wAWrBzlNJyntRoh3DdvUUcSbPnX4+OGii1mwO46cPwV+c7DB'
        b'W7CIiTnvQzc9SAeFDR7cQkzCWXgByxcdoe9GFzzQTtiQSc4XtAs2LMVFMz6FzsTDs1x4fuF0zUL4yhisQtuw0G/hzUad8GUmOnkOHsBWdXhgCm7A4zogIxYWOuCyC14V'
        b'E9E/hwlCqy2vhBXOhgbGrh8SQWxRN//esLvJaCeqGDblMmJdiy4+o/M2+DCmY8edqN1vZK+zIXYJzziiqzSpbLwKhp0TdNnrd84JS0GDIB3qLGeA4KXlo3wTeGKBiENT'
        b'UxwyRhq/BBv4rFlwC6HYZobKY0NQqzSOBxLgNeKOyFFjES0s1EzUJY1bikkxyQkbbtiBOufSHZI4eAQvFRkxTJHIBstmVpiISWDMQWdzcFcM7kmHu7KxazATW44p9Onu'
        b'SvGxq9iECdgUhXYUIqMt7IqLmZYxInXTI4umP5Uk1O3DCBM2SIes0b7Y4RyGIngZ+1utsJMHwCqwCl1B5+mZbTyx/9AZD7tYgOW2SgDQKbRvEp0gkixAXYnYYenkArAG'
        b'rMmL0EbQvLZJUNPZ7dPDSCyMGMiZo6R4ZmRtnQXcrUb7tONpDnm48/NgGzLkoubIomH1QI0zM7JkGTOY3cCOaaghN1KSl5OPTcZJZLSGm9DxxVicyULQAaVtmf3IFwR4'
        b'6BiTg7AbtUVjeT2DT7dLanzUETtWvwrj0N+d6Y5dhVrh8d+LFdrBZbzS/ZgXRxjJSsCe4qjTZDOjLZuhPtGFTjG4aEsC9ZeoOOya3GSOqf3otHusSI0u1tnzcF8jFRLA'
        b'ojOAFBxWB1C74suPt2LnmaKPlV5pLhPGj//x50uNf3td+d77S/f3bbxwsd1py2cfcq1fo96YNdjdVPTZkfN1b3GN4afCq16zzfhIJXOofc/LF7zKrrvFH7KZt+Sr5T+e'
        b'/FE5w6FLtfSr9u5PfmqTVv649KepdX+5SInXsv/5jyN3LfwcVm34let548/vV0e/s38PterP876pFx94wO7qm9BX+0cVeGfzHK8qZcmV9+L7/9Z3pfFIZ/oJMfvguPt5'
        b'SnDf3PbBMpONmf3PrnF/qlgszvSS3/u67IcvPp1648uKGOnD25+UrXzL8nqoXWX7tYTozrd5RYP31h8okS9t1m3eZPz5r+w511+u3fbaw5nn28raZ4Pvs9/+XnzztYfu'
        b'kL9tp9cszZn2QeeBrG0nBOZVEbssZg1W5htP/3TQcVn0r+t63o35BH617/WbgasOLGkPuGEuuDvT4dhKz3DVabt80ZoDYyZXz2q9V9N1onefjXrD1y+FfK0OrDh59m+r'
        b'MpYHbi7pe+wDE8oum997bPWpu8febbXV/2gZyrb28+p+lzpLxTt+52F+z9fDvD0pYNWWmeMjls3+rmvVJvnBL+V7fomwn7Vn1p7ZN978oeVL1z0zd3+74efSS5V3x/zD'
        b'e7ays+bOax+stv7L+NNneJO+OfNFziVZ3tWuRLW652jA61sPHXKr+vDNV00XDz06OPTdw/e/c7jRWfd95Ueyb8JOlR0Od5JvfNv99mf7Xa+FKlNYP37wzuO07//81uvR'
        b'oWmXHM4nyVw/L0xa88YvXx0fZ5gSceH+nGl/V2aqf+X7un5+7PKrx40bLuw8OibNzP/mpyF72T/vHio9/rURfZ35t/daZzxITp443TT4paz4mu/BjJ0ej8t/+bpKM/tQ'
        b'7nchjT5B7tqWP6tP/TAwdnvnhQDDZzePxHwJO7T1R8GO+d3tzYu+vOE49Fn9l5mnbMUVn790/n7iodu/vPqnCwNOn11Oqf1m1ePqvA2Llv7xbNA3jfUJpz8pvz4kuZe3'
        b'87TaRVV+v3n597cOfxeVME7q8R3/0ozik5GezcsvpP310rjwhW0fVv1YMVa85Me7P0wY55b901s/L6zJm9D0CXjwUseyd/701rJ3Tr975RXOx+PfuvJg5anvxouvnbjy'
        b'bsi7f2625J+69/GX4QseKiPCG79f8u3V3/4p4StX//DZ94Y1aNb01Su6Ajombk0bOPjPg/s++Czr4cSu716ffSVs87sZD+Z+WLP/uKI25HTxSe38+ZWfGH+9om78LG5/'
        b'7pufr6yab/fwUY5t3pZjMsV7p+Z+Wpz7blrU5zaz1oz5JujnPV9KnGKbX1q/6OrWk5/OfzzG99TWgw8bOrd+L95/c1Pe8r9Zn/uYFfaepPnLLxK+S/ij+9ItIY/XTb78'
        b'qE8dlL5+9c75fyne8fbU9bWycT81XX37yOdxsxKub7ltSHy9LTPkDGtXyW/9j1y+vWW36prr6dnRneEfKbROi6dOSKpvvbPeIv3X/rUgebeLn7JIZPeQ3AHwBRO9wqQo'
        b'oL2wmSQUEAuKvTF3eJGTkZdK5yr4oZvB4nCJCPUsxycTAFazWfA49ll30WkUqMM5k6RJoJeLns2U4BTXwm0PyeGYDl9JEkuyXiKzjGRBTCqg8xxQg8287IiwjPHYcXuS'
        b'BaFZTWdfeEfD/U/TMyjgW84kZ4yBux8Szx+uD+SMzoNA9bCJ5EKgdtiIuuil27HqxHm5EVAHr2Sh7QBPcJm1DI+rY1I01sPNydlR8GVsxbdGRQLAW8aSYDdi30Pa/zTC'
        b'7WOSsA/enP1kX/bR7MoiG3pbsGsCD/sT2YKn3sRLeFzaZuv58IBYEg53i2iC8eBpltQfXWPotU0NW59+owUen0l/qeUAJs8emiloL9qA/b9uzIhMZIDX4Zm6ke9xJXHY'
        b'HOzRCP+vkzn+HxdqwiDh83/1z/6N+pbOYs24uGgViR7TeSN/5THf0lHygItg78TWif3OQQ2pZlf3hnSzi6Ahzezh05BldnNvmPqRwLuFc8fZR1euTxtwDjc5h9/xCjVw'
        b'+r0iW1LN7l57X2p9aefqFo7Z01+f0iZusbjr7nXHxdvs7E5G1UsHnEPfcw41h4SfXHR4kdHZWNofMrY1vyVFJ7/n7q3n7Fx910t4x1ti0BqLTVGp73unmb0DDuW25RqC'
        b'3/eOvhcVZxZFmsMizKFiPIQ5ItocGWOWxJJSHGUOl5gjJPc9bP0993GHvIGnnz6o3cccGaur7heEmz186Y9evvrg9iTz5Kl/EN8S3y7rnzzd5D1Rl6YPN3lH4lln90dN'
        b'xNPoRSRNBKNE9nvggaN0Ve32+GNfQFa/R9anITHG4B5WD9sY3iPvTblcdTvwcm1/SJ45LNJQamQZ+HeCyAYKjEsMK/uDEu9bcPw9ddwha+Dtr8/r94o1x43TS/q9Y0gq'
        b'ibLfJ848JlEf1e8dO5JaEj++LyC231s68pl0m7xjf6K3sN9niOUm9DR7iwxxQ2xcu+cdhCnpalzS42j07A9JGuLixiEe8AnUpw5ZkLol8AnWlw9Zkbo18MHcGuKTuh3w'
        b'CceD2JO6A/ARG1KHHEndCfiEGVyGnEndBfhEGsqHXEndjRnHndQFDIwHqXsyY3qRujfwCdFrhnxI3ZdZgx+pC4GPxKAZ8if1AAYmkNSDmHowqYeA4FBzqMgcHvGDGH/W'
        b'cYYkhGSObWOZfJIBr0iTV+Qd8RijvCelp9S4qHfMbcfbsb3jTfF5/eJ8XSpJ3zEHhbSl3RNHGS07Joy0BOvSzBExHTk9U0wRE3Uc3RyTIMzsG2jIMoUmDIQm96QMhE7u'
        b'dTT5TtGxMeH8QwxT+oTRxmyTcKKOa/YLals54Bdj8osZ8JOa/KT3AoIN1OFQ3RSSqVSu52MQXz8dG4/XtmjAN9rkGz3gG2vyjTXKuxb1TumPn2oeQRhiAzzYU6D+EaAP'
        b'4qfeC4s8x+/gG9O6snqp/rDJbbY63h1RnLGoXzQFr3hWm51ZIjWmGEsNi/DH+SaB+F78eEyFyUbFQHymKT7zdlB/fP59NuURp3PRVZs8wg1TzN7CPv8YLDlmgY9OaRJE'
        b'DgjiTII444wPBIlP1CHY4IJ1905A7BCg4jIpc/Z0PEhcIfUAUIEzKNzoM4O6N4xvWGgSxBgjTIKJA4J0kyC9V/uBIJeMJOn3iL7n7Xsosy2zL2RSb3C/d4aO+jQ4zOB4'
        b'zr3D3ejY6Xm0xBwmOmfRYWGkOq3vYAXyvxTaFdrj301USHtZ2R+SO0pP0tonkLyvyPew1scm6CPe846i9S+53yP5nsCbTBrW7xGOq5/6SvAqoxPNyZP7knLw4qNzyeL9'
        b'8sjiPfKoe/4hO7O+8vAlxmlt61q9esBdbHIXG10u+XT59GgHYtJMMWm3Xd71ecOnb+acgcy5psy5nwmEd9197vhK+qLSb7uboqb1+xb0CQrueIb3iXP6PXP7XHJJ2tPc'
        b'ftewOy4heq2h2BSa9L5LstmF+Ypj8PsuYZj6LWlm/+CdWfe8hHrfAa/o58YjCW6+Jq9oo5PJK46YT3/9jH53EUmTm9g20SAd8IoyeUUZUy9ldWX1qLvze0v746aag8JO'
        b'Zh3OMqiP5g8EjTcFje9J7Q3sD0ofCMoxBeXcLuwPKtCl3QkON8R0lJG0tR7/D4OT9NQQh+OfQ5ljE3qorrCetF7/3tJbwZdzDMFYQ61BTLyxtIcyWt+RjOsJ7qV6WT2i'
        b'fknqfS5bFKDnYgMSFGaIPzrBPGFKnyixP2i8OVhkKDpejC2VweNo/kMfEJKMNRwD2Q4Expvjx+o5+vkmoZQkpfn0e0cZ40zeCR8SDgbqNf0eYpJxNs8kCB8QxBCBChoQ'
        b'JHz6e9rcL+ACD58fZ3CBg+sdhwD9GIOvKXDs+w7jzA5ue21bbXXy9x2C7jl7NOQ+fhgDwmIfABbe353wBNPYDHPYxN5QU1jmAzY1LpsIgziHCEMwLtkE6me1DT703guz'
        b'lTlzPnD2lkVZMAloDoMcEiL7FxLP/uWDmWS3LXjRQUyfvXTxMoGbAJhEtVIORTk9Argg2WpO/2622gFeJDjDH8seFa4bSU57QLys3WAe+UUSoGIVUip2IUvFKWSruJUc'
        b'q0oRd9CBjgvSOWOqNJWqVqXYgZF/9mPChbTnoBrOD5OXC0uVQjkBktDUyxPxBi1LSkigtKRk0LqkhPlBEVy3KSlZoi2tGe6xLympUKjUmhqFUq6sxQ0WJSXltWW44lpS'
        b'QpLLFGUlpRqNSrFQq5GrS0rowZksQZpuY0cKsjQ1+VLTZvCFTQwNQT/kkkf8WXw7dEnDt8L+al6katidi0KHeO5wD1eJekRUuuJvd7+k1JV4EO5PifLW2flwmsOmr5ce'
        b'/faXgPD2X6anRoaFbeVL3j35qPHY66kx/h3nfnX67Vz/5vWv/zL08TsH1CFt/Z37xfNek83/4wfzP29PN3mOa3MbVzFzWp2QV5JaW7bv5hTTT1qTbINyx9Uv5e6Dtc2f'
        b'rPMtWncjPa5NtXjg4doTpUsaG75c277H0uVW6ie/eFae81zpaDv/+yMXdV+0xYZIYys7G2YqKlZ6HpSnvl7Dtbp50Cr/e4eXM65bHmstrWgt+6pggVvBwj0FpWf1b857'
        b'zVPtM6bCx7bCOfIrXnzbXHPFdwv2Xt6y+ivKrs1t8O1ATd025/0w3T15/6feq23q1mXbLPkgb8emk/c8Az+657Zs8R8LjwfI7gqDuy9u/2UBG70xfklezxdBy5uWlGTc'
        b'2rox53z4H68umr53c8TtI6fNmUmPD36XdHTo16DQEv9f3XfIYP+rltJvT63VHnysDxlzu+NC1ZGol7dvyoxy9jul3bf1m4cWB/OnTx73VxHnIRNQ0qKLqCmHPBpqxgK0'
        b'fRU885A8h8O9HLjxdz+kgC7DdXALxxKtj3tIP+bvgMfd+eH4BkDuIAxcHtyPQf1gNwedg0dn0mNlOMDTangmIy/ySYjCEbWw4U4MYkySizwYFbX8b4v/d+46uQwJJ9F/'
        b'9c/9MX46VqWa2tJyLP+pI066BS5/xU56BLB1HeJYWLnfsXdqiW1apvNvWtWm1sfqSw+PaV9pKGhf2xVkVPX4d2l7CrqWd0tupd52Qhn9sTkfCTx1sbrStjHtVvosk0Bi'
        b'dDcJxvYl5Znc8/qmz+iTFZmmz+x3n/mRm1DvtFPZ5xCEPRbBLAqfD04uLSmtrg2TH3F4VmGPHDhWAUOAFDaWQmuzjX2L2xCb1Dy8dRVMLURkiGdq0vgeHlObNKW3iK7d'
        b'ozG4pEZj0DUag67RGHSNxiA17JbZOmAcC6bu6YOxhuuh4RhvuB6XgDGH6ylUKoWx6U+WDLYVU6exh+sRsT283iKzo7uuwhD/ouoP9hiwz9Ibe7xOAtzC/HefzwvArb6P'
        b'HHIoq5nUfUD/M1TMAtYOd6wcWtS6MS3VJquAR6zlbCvPR4CUQ3T5gA2sA0nhMMShW5da4PpDFmUVu38FPqqsYunO+6Th8ZCcT1llUnec/I7Z9EWm9wun9jtl9NlkMAfY'
        b'1hTvVBvwqo1zqh+bOcBcBllYYP5zx9cLhdflBUfa02MtdaQgd3Z18vCxJqIoB3KqOfxIin/3VDvCiwXn+clsxVphMPPLL/Bts7w52W79JEHqzYmTvq23tryyaWrfh+xJ'
        b'f4jd/YZvb/k47sx7N16vycnRfZV7P/bBNY6dU5w572By7gWnqqLEL+Q3f7z3qqHpnddMD3/4OuvIL2f/Wl7mduf4ySRPwXqbcVn7Cw6ns9Oa7JJt2GfrHr05d+r3hbtm'
        b'bExTzlD6ocvOt//xmciCtjLoMNroSP+sUz4dcbMAfHh+ErrBQgbUiTbQXx/xgtugITs/EnVhsKD4/PxIFjZF19jwMNq+kB7FE3ZUwyYSkyQP05vg9VzYDHdYADsnti/a'
        b'EPKQDitfWF5OvqBCfznFX8myhEa0g3neOLDMJvuZH4vii+Be1MwivyI1mwHQoZva0T8nhbaNZ0EjPK6iv75SOh2eEWdxAZUNkuBupMtGJ0SB/7V9/F9/7HihUAaOWNTn'
        b'7ekLbatCqdBgVckdsa1TcfGPeuIicZ3Nti4Dtr4mW9/9y/ttw+rTzRzrLTnrcvoc/Y+NfZ8T8THH708c20e8l7jc2EeAlH+ny6GVfGDjUp//zDcahIPsGrlykENy7Qe5'
        b'Gm1djXyQQxKssKOpKMMlyeUeZKs1qkHuwhXY3RnkkFTLQbZCqRnk0r+kMshVlSorMbZCWafVDLLLqlSD7FpV+SCvQlGjkeMPi0vrBtkrFXWD3FJ1mUIxyK6SL8cgeHhr'
        b'hVqhxC6Vskw+yKvTLqxRlA1alJaVyes06kEbesJYJklt0JZ5FlKoa8fGR8cM8tVVigpNCe3eDdpqlWVVpdhdKy+RLy8btMJuGnYB67DHxtMqtWp5+VOLQz9ELfhv/4RC'
        b'xlDkjhTk57jU5Puvv/322z+xrbCnsGNKjMXo8ge6/HdMB7GRt6x5KZ7glic/JZj9s+XIzygNOhAnlK4Pn7I/e1aM/lk8obJWIyR98vI8kaWK+OfEUy2tqRkWG1UiabLG'
        b'5FVp1CTzbpBXU1tWWoMpO12r1CgWy2kPWrV4RBqe+rCDlkmMczxBpQaMf67OwcUQm6Ko+ywOxRmyAXzbeosfOFk8ymVojg2wchyw9DJZeumyBixDTZahfRETboWgsP6I'
        b'LLOlwx1rtz53ab91XB8n7g5waBF8ADzp2f4/izZcKQ=='
    ))))
