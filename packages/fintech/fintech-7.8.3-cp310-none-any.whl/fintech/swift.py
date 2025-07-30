
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
        b'eJzVfAlcU8e6+DknJyEkYREQEFDiToAAEtxQLKIiEDYFwbUhkARSQoBzEnBXFAUExAUVFcVdEVQ2cV860/bdLnfpe72tl3q73vvad2vb281Wu/ifmRMUFfu/793fe7/3'
        b'6i+nycw3M9/+fTPzHT6mnvhPhD6x6MNPRw8DtZjKpxbTBtrAVFKLGaPoEGsQHaY5DwNrFG+kyijeZwljlBjEG+kNtNHJyGykacogyaCcTSqn+0ZZRnZifKayqNhgtxiV'
        b'xSalrcCoTF9hKyi2KuPNVpsxr0BZos8r1Ocbw2SyzAIz3w9rMJrMViOvNNmteTZzsZVX2ooRKMcblY45jTyPhvFhsrzhA9BXos8I9JFjEqzoUUVV0VVMlaiKrRJXSaqc'
        b'qqRVzlWyKnmVosqlyrXKrcq9akiVR5VnlVfV0CrvKp8q36phVX5V/lUBVcNNIwjh0jUjqqmN1JrAlc6rR2yksqnVgRspmlo7Ym1gxoDv5ZRzpUqUmjeQmzT6DEEfT4wO'
        b'SziaQamkqRYp+v6zP0OhtvRWSY7ic+tqyj4eNQbDFlgHa2FNWvI8WA3r01SwPnFBuhp2gYsSavwcFt6AFfCiirYHIOilOXA9XwK7E1PgVliXAutoSpbIgA64Hnbn0U+I'
        b'1aMfkSzMFxpx5v/DF5OHg366WoToZxD9NKGfITTTa5mMAd//cfrnCfR7r3KiEuKQtJQ5yX+WxVGksW+tiPpJ4oy+5SSfHh0hNL7rI6WmDx2L2nJCYwLLhMYv3FnKPRbN'
        b'HpuT/NG0UKqVsshQ8705vuy3HlSscuyn479meido2PWUBc/3SVQT3eFExc6dmxN5O/J9Hzeh+Z71a7dGN1rqmfUB/cvCYbY/Un2UPRx1IDEcRcKohbXh84KC4JbwBDXc'
        b'Alozg+KeT0qBDaFhieqkFJqyujnHgIug7Sl2O/XTPQWzG7OaMokeMpT+hxhaMBhDH078kKFygaHvqt0opBUR+RNzLH9aJKXsYZiMGtgbgqioC9EiimqS5yUkhiYuoCK1'
        b'GWCb31DQmAlqwS4qX+wEW2zwkN0LD7kOzg3XgAtoftBKLYH1pebxdrwiODQZbNCAHtxxgDKOKwxmSbsEVINdmkgMsZtKseeVg2sC/BmwbzjcKYZnxBQVRoXBG88TRL3G'
        b'yCm0kPs2zxzFQW2MIM+l4R7UGIR9oVtOwCHdGMqc9vVzYl6PenZcDP8s59OcF0zJ+jdMYR+p9An6v+V45BWYLLl3cpL0vzOpPJL0KvdU/RnjKfq0Z/6nhiT9EmpHXoK+'
        b'2LiD3XK842RE3KI6VYAyK/qbuFdST7jGb7v0oqL5P6j4t4ZuCuu4M1LF2LA1zcwETXLEJVWKXR2MBM5QQ0EVC6tLpLOn2Pwwx0eCw4iVW2ADrBNR7FQanIbtoNMIrqvo'
        b'PiZIpRJxWCYDHgx63PeebuKKVxqtSpPg88L4crPJNqNPRhyazqC3GTEcr0APxSgF7U5L6SD04ST9U6hEfeIyvcVu7HPS6Ti7Vafrk+t0eRaj3mov0emeWldFc1hLODF+'
        b'4FlG4/mxbN3flzAMLaHxk6Ulv+AncSVJwyaHJIQGp4L1WaA+DemImPKGFeww2Ayq4/OYATrIDqLcyJ88VG6GeAsRUm6GKLeIKDSzVpQx4Ptg3qJ/8seVW5JKlNI7CvF+'
        b'J9J/NQVbwFU1bARtduzSwNbc5XAnsrhwyjklHOyD9YIS98IqNdI9rHjgOKwMK4bN5s1fvcry2CquTfmXz3IW39wGmkDPttadrRs7q8dvurQxsZn+jQlrmsL0QbITtbv1'
        b'zwlSH3d3FU3Eb2HYkCQ1rE5MThVTctCpApcYeADshRscQhpM+kQGfXJB1CZLsd5GZI01XhHMIikjOcseypklcusTG4y5ZhuHgTjspFTMANkyHI5uAwSMh4c8FPA7gwh4'
        b'FGZIdzI4IIi4Pg1HGFgLrqSF0pR/EQu2g/1gHzHD6DEedFRYlphKv1l0ywzTiSH7ZYJLvG2SaGoESzG5FDyhDybA09OG0lPCEhgqAgFnn1tOOB8SCzoQsEdeBE0xRgq2'
        b'BoErBPpWvDc9Pe5liiq5WeS7+G/jBDldCc9F0AnuESKKyadgG+yaQKD3zB9Gx8anIu29ueaWba+P3Zv4F7B3NW+bDLbZMCpWCp4GXVIC/77On56N+RR7c43vrM8WkdnB'
        b'8ZkGBB4NeiIYiilG0ycsI9BNYwPohMWuTpQSzZ4aWWD3xQwMhQ087JkIzoMNGHmwEXENnAsjI/gJgXSy7BIKQjfXLHSTq+w+qHEGPEyREbVTI8RoQCUFe3xgPRmg8lbS'
        b'6fHxKEohhOztCwkB8ACsnsdzE0eDY3gFhFE77Ewk8J1Bo+hM19edEOfXLCxs1hN4Ndg+CXbbJygVmF7kqWE3PLJUICFvLL1wXCVm/ppbPvfC7MNQ41qwGdTgAeAErMQ0'
        b'I48Me+KgIIGfx4+nly5uECEJrGla8zd3+1DUmAGq4Hme1yw14SXWUfBsBOwi4NtyVHSOx1dI027yC4slYYRJMeCUDS8Ad4MdWGZgHwUvwk3hZESbJIQ2rGSR0F7kb03a'
        b'M4zgBHfC9aAZj4kCrRFOaMh+CiLTuUiG3B+npgvCmhgkN9431UkuyLkTng2A3byiLEeGiIDn6SjQ5Evg900Mpy1+7gj+Rb7J9KJOWGIzOArPy7lJYP1KwqgTFLwAboBe'
        b'MqRmVgRdYvJlkLD5pudf9RaW2IJY1SOHnRO1Y/EQlDyJZHICP74kkrZFfoOU40V+4SKvHEI32A5PJsllkbASHMSig7tpZ7gL7iCd48D2BDnsnQAvgd1ksk00jTDaQ5QE'
        b'XIMbsnnYXQ7b57tiag7TIfCggTBfqgGXeWcXkT/swHPeoCfBHTGCppyEFTPlpfa0JbCXQl2d9FjYKBNQvzwW1PNyDlSZbHhUEz0CntYJa50AuwN4G7yA8sRKOe6sp0M8'
        b'1jh0D+yHV3lXF+tIxFSRmI5BQFuIgc8OBLgDHLC50pTImY6NUpL2dHhOgtpT40oxURfpsKQVpL3IvELuUuKRA+pYSjSajgUHCsnyyCvXg11Iv/PADWwQJRQ8A5vCBKyb'
        b'YA9SNNsklNxGSSjGhFyDfJQwrGskuIJUUATbiRkhu+uiQDMZpi0t52En7Fba3TDvziJN2A53kq5lixFbe5GJdpeQvtO0BlR7qdyIEKXKKHp5ZKYE2St/K+L0KNKYWjqZ'
        b'Xm39o5jKQfopd55OGrnFU+n1wadFyFB53xkfTiWN6pxoutLDylDuSM1GuDCkUZ4UQ1dLjrHIRPlbbNRo0hhlnkHXeX8qodLRnGWJkaTxrjSW3sbdFCHj5G+V3xGso6wo'
        b'jm5kxkioiBd53wDpCtK4e9QcumnETCdkk7wvz/mRxrNl8XTzC8NZqgRpoOT1BNJoL02gD61NRDHwZmFT/nsm0nh5ZAp9Kj5bgsyn8FZRHE8af/JIo9snnUa+8MVC32WN'
        b'w0ljoyid7pD8hxhZQeEt394lpDEhPoPuiVuFVb3QN/rvs0hIhW3m53i5bGgyVgYFHZs7WXDVW1YHyzlXWO3mgtRnCB0DmicL1rcHJcoXkGe6UF4Mj/Aiosghi2C7INyL'
        b'mnyk/XwI2AR7sEY20qMYcEjFEgRWqV+hm5foxYjS8lt0TDlphCWv0oem/Yy+3SxeGN4q8OSN1NfoY+tCkTd6sbhp6Q+zSOPz5t/Sp5ZcRbsABFm2wuXZaTje0JK9IN7x'
        b'UCbxP7u3watLnspWxqXalZiAreB8EKhNQ9uyBliTmBKWDK7CGpRReuew42eA3QR3pSsTUErjbzmK8YYZQhq8ebZ0sUikxHsdRcbQfIq4F1/YrNKGa+HWNJSWTVojhZXM'
        b'CmRqFwh/veAmWAO6QQ9OzGeDE/QiCrTLF5GBcANskIQEqVHQvwqrw1HeosgXuUU60vldsIUC3Qj3aMoCdkQHwQMcZhnBwz9LrLjDuJPtVZ3SsRHrnO+UU0b74i2bxTRF'
        b'SQnTnEoaBo/6aCLw9x2UvgxeIQkHOBI3WUuS5Qa8O9WChvBEcCaIprLBVaVN7JqhJsMVoNEyVKSJwiMaqVx4Fm61Dyf5SvGUELTvQvtaOhLvicMTWcpTJYJ1yx37FOTN'
        b'1s8CLfn9O4+8ZfAYmZKzK/RgpwZ04Y1KC9rngdPE2aLk8MAseAqe02jwr4NUPjghJ1PJYUU53Ad2aDRIpOAw9cJSuJ5MhdzXwYm6FZpJxIFRBnBNY8cHDCj6XYQN2iSM'
        b'WCoirxk0YNm4loimLIVCYprt5D5zjGYSxmEvZQTtYLPdn7jI5bBbm4wGpbmEw/oQmpIvRm4Nrd6gYsjAkZnDF8AmzSQGY0yZouFJ0jwf9MJDHqGaSRjF/VS+MZw4QXbu'
        b'UFBjgrVo45IiptgRNDgC6hnH/gueyIN7X9BMQlYBmqkCvwABhUPwlGcIFgY4MBvWpIIzLKWIEbkFgvMCn64mglqUWXVrQC/+eYiyZC+z4xQYNDsvQIGpHtYmJ+E9kAhe'
        b'p5EY9oMqewqeuLXIhU9OTEzBZxcPd5xBYarglDCVmpGB40aUl5wAx4KCQGsYuOYdogKN8FiIF2j0HgqP+YCTDIrLXu7gEGgMs/zw4MEDy3I2119Qw1BrLkMRaflnjUUQ'
        b'h0JS1QksxcaibZhSqfIi3DDDq3DPWnCcd+Hs2A8dpEfDxjXEFoajbUATvKqH3a5CXy+tAgdQACexccuUKBloh92OcdfpEDPYQbgBLyx7TgG7eDRK8F6B8bCHSGSFUbsy'
        b'ni+1y3CueIVWRq8VYnD7MNg7DeWFveWwR0wyi5FTwUah77IoWQbO4WSgx4UmYT0Snh/mCJ4s3Ic0qVvuKgcNyMUuppd4g+OCSM7AjSunL+BtsnKc3lyjA7SghvRwWnjd'
        b'GoA78FIVtBJl9psFt4yyrsnocQp22zjYg3O167Q/PBpAKE5DPbt42GWTUCYjjYwBmWnndKI3CeAUOB7mJ5e6oK2FaDKdQK0jE4KdCI1O0BqKcrlSBcZ+Hz0eVABhxyWL'
        b'AseU6+SuCrRjEU2jExE3W8hK42A12BQHr8NuNw7lPyJXejKoDiRjcoODQJ0v6oBdOKaMomfOSSJULZwmRuNP8aVkHdBLjwDnisiQlXBv4pgFvEyQ0w5a6QwPCyJsBIdg'
        b'pTs4Jyd9Ig86IhJsJ4LSaSPhTmQ2oRQ8CmpCs8BhQo90AbgEat3gZdggKy2jKRZlF6B+Ljgp5CsHkRI3gqawASTtzDVXF91g+QZkUIeYu8t2xKTBWMXmz69o4+6F6tQf'
        b'+geP854keS1rpD035/j+Bc4LmIm7XvvIUxRnuFP50m5Fcmh73d9n/TDkJ2b1Hv/0PVPW/nT//Jc7bttyNlyTyxWVqoW2rwJ8E4/Hbvl252z9ic9bVF7p4NPqIzebZ1jh'
        b'59mnRo0da8o/rPP8Ye2rv5jfN59Irxv7WtQYdcbYkKg2j9Ys+8Ukp5XhWd3L/9CeH/9e/qxl3YcvVbx2v/1l+3UXqB0pj/ti+iKFwexu/N7jM1FATMLS3T8t+ug1auxr'
        b'M7q6f9hdvWvtgoBx7+nVU9rlK747NiSBV/xp/1/8M661Bj3HvXz/zQM2zakLlWvv//L5lov+b1wfrv844WxtddmtqJtTO3P/jX07pTz+xk1OdzdjTl997BfzWzZIvow6'
        b'/3P9j3Grig6t8R9y6+Lp19Uj3q3cOerERo9z5ydm1XTvy8nK/7xl89EJmZf4hJ+ft1im//TXhT+kHupsaam8d+OLOtVfPliVxp3iHlyo3uc65+gGybUTSxZsqVw8NrXk'
        b'rd+Wnj7515XSs4fefiBqKNp/sTRWJbUR37bdF6UjtaGpsGb1qmTYgDa4ctCGHGyslBzyMKBWExKWGBqsCoMNqaA7FNag+Kpkn3eFTTaS51euUrv5P37M07kWXrYJ/m88'
        b'6A0Jg62lSDdq0NwSsJVRY023YZUxgT0R2tCgBFivpSkuX4oWXiFJshEv0jUKVGsTPdekBKc4URKWkSK3bsOBbskcL7wtRzG8Nwhhg3wm2qB5ThPB/fDoShsJQh3gCtyt'
        b'TVPTVHAQU0bP9ClQSZ88bHjWQyV+dv+jAwoP4YDCxumtvF44cifnFMuxYcdJaQntRStoKSOjXWkv9JSJpLQHLUVtqJWWkY87+df/S0q+uzKO34zEiaElDxTotzftzkgZ'
        b'lmYl+KzLG80gIfMz611pb8YVteHv7HlOQT06/1IMRG3AycizqVPRnEs/fWSqWZTjjMTrxiBnJCrUEQY2FjmOSMJVKMCFpCaDCtgeJkglRELNBe1OoHHMMBUtZCCXy8K0'
        b'iaGgIhHlJiyFQqHfvKcyUJf+JDGZIhkoPnOnnj51N7k8zEiZfzQj/a4ITS5TDvgvHYuRV+ofvyYhdy8rSozKlMypURHKYo58iQx7bOhjPxJtSs5os3NWPJfFzNvwFLl6'
        b'a6FSn5dXbLfalLxNbzMWGa02XlleYM4rUOo5IxpTwhl51Gg0PDadnlfaebveojSYiQT1nNnIhylnWvhipd5iUWbMSZ+pNJmNFgNP5jEuR+LOQ7NgGMtjU5FzUAEqr9ha'
        b'ZuQQFL4dslvNecUGI8KLM1vz+V+hbeYjLFYoCxBq+FrKVGyxFJejkXgCex4i3Rj97CnUiIcGI6fjjCYjZ7TmGaMd6yqDZtpNCPd8nnf0rVQ9MfLpMUgeOTmpxVZjTo4y'
        b'KM640p7/zMFYBJjMR+vFoRaL0WxbqS+wPAntkNUjYG2x1VZstRcVGbknYVFrrpEbSAePERkcOFdv0SMKdMUlRms0YScaYDXpEeN5vcVQ/Di8A5kiAZfZxjxzEVIFRClm'
        b'1GCgeXYOc2jFI2yy4bECzm4dFBofoEeTJ5rTnleAwHj0y170LKzzLMW8sR/tOVbD/wGUc4uLC40GB86P6UsWsgeb0UpoUOYbc9Fstv/dtFiLbf8AKWXFXD7yL1zh/1Jq'
        b'eHuRLo8zGsw2fjBaMrDdKOfabXxeAWc2IbKU4YLXVRZbLSv+R2lyOAGzlVgpdhRKB2lG62BkkduHX6EqzmjR8zYy/P8GUQNzh+iH4WxgLHro70qKeduTEzg0w8jnceYS'
        b'PORZnhvL2mjOfQbGOHLZ9P3KlY0iF1rKYnmGhjkWfaSOj6/1bNX8T/OdM6IoiowuWom8DIKcD6/mFeYKCwwGj30RIl5XaBwgqn6EEAss8CrPGy2/NtSGAvwzmOiYB0MM'
        b'juxTEVdrtxqM1sEjpmNZFCMHidWPL4xgfm2O/LLH4+5cLG14zGTjkacyoSQGdw82sIRDAkA+Tz/4uumObqNVncqFPQv7x9Z+Cu/B479DEZ7IAR4b/Mx8QBhrRksPPjAx'
        b'bmbqs9VOV8yZ881WrFJP+5A0R18uUUhkwMp4zlhkKH+mrQ+c+R9QaAH8P+lMCvQo2gzq8uYac+FVZNaD+IT/AcSwGRA7w37uMbwyUc+vG5tVX2R85O0cebEyKBU1D6qn'
        b'dq6E5EVPjcgycuVGqwGb5cpyY17hYKN5Y4k+emBijSYYkNUPMmKJ1bosWrnAWmgtLrc+yroNA/cBeoMBNZSbbQU4STdzOEs1cuY8pdnwaxl+NNrN6ouw20Q4ZRY8UTT2'
        b'+MBoxz4nGu0LBosMj0M/dgWAd3Wu1JNXAClCNY7TKlLelTOczVG8GrRYOECvXCjGFwcL78/OSf5qcTBFTqdscGcw6GbgxViKmkZNgxXZBFY8y4lC29b0T8fnWEb7uQmw'
        b'kjBQD3aMeHjkPauc3DeMAa3gSIhjy/pouzoyUAw2iP2WLFUp7GMQWCS8BGpgbXhSohpsCU9K0aqTYL02VSyDVdQEWC8JAVvXkcP3WFfQG/Kon/IABxVgvQh0wAvwJKkX'
        b'gSfhTn9tksdQxwl4/+k3bAI7yFGxn59RmwyrYlDfwGPubbCadMPDYP90WBsC61PG80lqhpLCSwzYAjuk9tHkyCMMVuLj9URYp0XbcdgQngDrRVSgB9wJalnYFDbOPhLB'
        b'jZqidUDBriItKW3YCmvwRceYEPF0WKmzj0VQGd5DBs51HdSlCRcTqSk0pQJXxWCfZz5hpCom3QEJjs8QFsY3DwhsTI441mYQbjYucaAnJAzWo+XCklJgTSiohr0qCeUP'
        b'97Pg6HBwSrjBOOoLGu2w2QGZmAK3hCIgn6FsRGkgwR5uANfdBxMbuB4p9tOAKnIcK4NnJ2fDFk0kvkrYQxnAiVIiAtAGt7o8ISVLHBJSFrgsnP/vm+4HKmSaSDG5MSgA'
        b'7WVCe/eS+XCnEzilpqgIKgIcB9sFhPeBWtCqTZLDQ09IdSa4QE5MLd6TtMkI/tTjUp1LO64uVs+ya0BXiYSik5XTKHDWRUQWDAddxqngKuoi56pUoTRTuE44BRrnCEoA'
        b'akIeaQGtUkmEM92rcNc6jaZERNHafHgUV5RhZMnVVps7qNFoYIeYoufDWlBLgR54Ahwhx8cxcC/o0mg4NC4NXjBQ4FwZvCEcwFfBa+A0GteFxmXBFnCBAr1e5cJlT3WR'
        b'BNSM1WjwdckRqjADHrXj8sUAeEgh5jUazMajlCXVQOzTgOYLpaiC8rCcpUNjJJTdHTXOXu7G08gmKGoONWcCuEEgbyvccWVqzgcrcpJ/P8ZEqUSCCR0A1wLwHUl9uEFO'
        b'mCmFTQzYBTfCawQgeBpo04aBCnhGHYxFDM6ylFuWyALPICPEZM58AezUklotlgXbAmjQ8hy4rnJc/lwLsTs4V5CO7w/a0gUGdMCWhf18A+fAGcQ30L2OWJ0rPAlqB7U6'
        b'0DMDGR28vAjNjk++hiI+7nEwGBz1QAxOziXT+8MD0/u5CzrhBsRdsBHsJu4HHOVgRb+5Hh7ylLmCFlgh3HbsgdthO+wBGx/KYuJS+zjUMxcchCcHYJjk+pQlp8NWgmIA'
        b'rIVnV695KDa4CV4maBTCenixH419sOYpM1eCfQILT6wZGTVRoxGuEQvASdBsD0TtBbrh2kR1ahiy5yBstJPV+MjWH1SxSDvrkxxXthfBOXwDpooDu9SJLOXsxICtk54j'
        b'ClHo5oorNX2HTs1RLAseLdxqSZ+Hrf3CLFEjWUYhKeMjbc8w0CGoCbyQPkBPJsMuwYougc7skCQPeEmtVQen4ipgt3yRcR6yBcyyZeAoHj/wIhaxKwacx9d+/sks2AF2'
        b'o5mIY6spZAe9slXaPCmxK9i1gLjTmVhzhbtPsBWFkXiw5aEPCs4Tgzakw00EddDiA6+Tm2vsoLE3Ee6ud8P15Bo1AOxXOS55H13xgiPlIlhXBs8Ll07b4d7cAfeNE2z4'
        b'xvEGvERObG1znB2sqQ9Boa0hHG5Jxuf2qBGBmalIsEeSCDbAOoKOGzwCDiNk/GFrQmhSmlpCybUMPIgQriH9/ig+ng1JhG3IE54JGnAzanNDNovVe8lUt0dXrcVgO75t'
        b'PQ27hfu7en/QGRJUmKEOfnTX7uFNPD1CuWMC0pX1A4sCHlYEgB1C6RysBFVgi5yBVVEoaFEZCJ0KhznDA3BXEk+Dk0HEtSDI86Td7A+rU1RyXOUJW1FKADcVkHYeHnSB'
        b'O2nYS0om1fAUvEZU7wzvTCFHFTGhICd0RkIiJVxxNqwGJzLBWbgT7nFCyDZQOslkoecsPAq2h4AToDtChB02VWyZYV+IKToAK+AVHkkG1ifOSwddERnzYTWplg5TByEG'
        b'BDuugTOwjVSHZiVgusmt87yEUB2D+5DtaBcglWYpcGPVEJTZnAHt5No3K5fFeZLUEJujiFvhRxEeZsDNsAteeW5wFtbAFodvAs2xItAdhaPQvCzYhnzfolWC62tC7N2P'
        b'u2jk+2Qof0Ikn2TspPagB25biHKL6kTkenbDRlANLk0vI/VMW8CZSeCsGHTlzrflgvMTaSR/ySJwepgQorYuhK39c2JlRZNGLnKoC4o1uyYihQtXzyaGK9ExwePhFeEW'
        b'/jiotCL3jvKZx937sJnENlBO0QO7Hdp92muA4SODF/w/suETY/tJnf08Do81S0gesxrsL3gsQ0kH7Q8TFNAzkvgxWAWqMmEVbBwkQ/GEF1RCdXei82LNpFLk6JNAWzrm'
        b'WOtagc2HkWo0BE/TRElIXmJ0B0JdRimoSddElSF+xA6FmyjQCg9kEnQXuKQgZGEHhWNDLfLJoMunTEULinY5eCnqnID64rPhYZQlgKtOdnxls8yQI8cVB0jmteGwIQN2'
        b'uIDOqAnpCf2qN1+dNT8hlOgTimcVD3UKeacWGdw3B3ltHJpFYJMJtEkCFiHuUKsj1pFlGYsEtE0CnQzFeINdUbiedL1CIO8YCob7QZsYV5hR1FpqLVdEKurLYfUKnhSI'
        b'zw8qAyfw1R32ldmP6XO22gnJqQL5lWloCOsLD8lTU2C9OgtbBDIqbCawJjshaUFCpkAQaE1HlqwOS01OE1PgJOyQgU1gb0a/+TeDOj3cKQYX4W5SS58+goSZibAB9ML1'
        b'EUhzcZE91r42cALiUhKiY9tAbYQ2LAtcfVzF5sPdQsZ3bDWocqjYtoKBOch5pKVEvXcVjMDVCr2kWuGCi4mOAp0BQkXkfhShz/Kwt8RNgvpqjPPpcShqbyRFROYPPNtY'
        b'fhP6uvXchDWZv23wmuO17rsJ//ZnTUy3Rt7l+kHX6tMdp16/ELEh8Er188lRb87eUwlft74xxvNk9junFviMr/z3l8Y0J0zq/HH93LSAKXsLpgxJmb5i4ld31n3wsu7a'
        b'QXHdS7b7351b+/N7bdnn1i64pDp1bL/pwPQJKzZld389bvLrUW9mP/h20rmp+9s6f1f2Sd+fOr9++09xuyrP6WPmvjflSunytyRtf2p84Uj31By4uag1u/7cvcsNSw8U'
        b'ig6s+TSzd8f41NJrc/OO/2ae/kCwaEvTLz+2e85d0prtOfGnIVNz/3Lx30e9NH4NU+62VHR78m3bm+OMuotSzWTt+dMf7rzr3Dv24PuJmZu+VJ52+fIz8FtpuXyp0+3w'
        b'FXVJl5PfsYe/dWzlS92imLdvTrvof2s68/bV0R90fnRgSfzb3yuOrNtWd2XMx34Xp5Z8v2lV1sUFJTFv/dhdcmXTqsDbI0rcNr0bcntoye9dvp1t/H7G2IP5l88sb3mj'
        b'bfnhfT5vrP3QrTom6O62WzDXs3PuSzPC74o7W2/tvuXz8oihq5Lv5HZ85jVixnXjF8GB9zv/cPRI1pEuS+niTQfu5h/+26sBwdyEL7/0LF8TWVfx/YfrXg79gS3U/uHV'
        b'PRK/2zPvaD2uX9tWuunz2WvKFvW8JV17dkjk16/v/0tn29nOmO9fGX/2q9+0zft821z1jJenrPnLxNPxP235tvjO/Jp7gS0RwW80vvmH9rvqwJlO6ncCqla6fTvH+eqY'
        b'wq33ttXtOS3bEt2y/j3F8oJ/vfBVzKjLG8Hhz6cUrFru8uOK+X+791vznXZ65TbPFs7kE/39mdM/3Yt6T+Phk3g78qPfWT8aY2qcXFv9+4p31o67YD1RPa8t7h1R1/G4'
        b'a7R6l2zCOcnLX99rjQz/zRvraq/fX+N3l70m6fFcF570y/0Ol9WJJdF189797OwXb+w7+Hb29375ASdXfXy1+dvJfzkW6JT6w2/XT/YW31jw1d9d9v5O+fuv7/pVZI/Z'
        b'89fXI3+/Ku2Gc++XhyN0P9TeDnxu7yel5w6lqD+Znb8uYUHK3p+zP4i/2e5UFm3dXLr9a+fVdvvcH1Lfy9n1zjKnk7e2ln68bNndP59bcvbjy7fybx1qHmH+PH/Nt0Nc'
        b'pu2eUZzybfb7IbK0gzPOBr/13V89g7cvMZx2N6xbpc0bb7q35a37nvcDv5nXbIu5TN8drg+UrWrPnTtz7jddn1y5+/69P6//ceaKbya+9fGdRZFvjf+hYN6u3/0CbiRN'
        b'nmQreeuX8hvjJPdX3D+jDUzvuuv2zr0Ne7L8Va42HBZghQicWjIS+XtcvoD8FfZYKA3yAb1sQiHYRyogQpzA5ZDgMJUPuIDiAUU5L2LAcTPYYCMxYydoRn7tTMbDIoqH'
        b'FRTIX1UKJRRoV+FO1ric9qhKIm2RjVQl7Ufucg+ukpgrJnUSpEoCXjWSAgvZgnmwNpRfmgprBhZvgJ48G46JEaBhrVAsMaBSAhxyEcH94GQmmWEF2AeqQ1JTQrXgchLc'
        b'ipIIcIkphy2wgdRhgKPL47UoS5wG28LR9ldSzoQllJPKkEJ4CBzQokhzHfHkIWFuEaL82ZxA1lHQBXbjaA4vLngYzt1DbSS32Ah7+JAwFThpIEyTgHZGMz2TVHjAE3Av'
        b'3B2SpIEnB7w+gt8dOQqaCVcRp08GgO3jYTdaG6VIJf0vIE1nRaBhiMrzH632+C8+VC7//DxPve1SZJsaFUGqSKy4JmKddCFLC/9kpCYE/2NphlbgShKGRf+X0QzD0IP9'
        b'k30rdVWQEX40riHB331JNYrkZ6lYQQstAgS7Hs2DZ37gzjC/sCLmZ5ZlfmLFzI+sE3OPlTI/sM7M96yMucvKme9YBfMt68J8w7oyX7NuzFesO/N3dgjzJevBfMF44rWl'
        b'n7n6KGkJWpel3Wlf2l3kivBVoBUC0GoBD7xIzYo7I3sgQf/HtGGqJA8wfgoGY+uBsJSJUQ+DKcQflpEgCAkjYcagXxJHFY2CjJUgOAX5HoBW80L9fohO3C55wDyQsYjm'
        b'X2SsgvCQXc98LXPHK+D6GwWaj8zBcG79IlGJ+lh8EDqgZuafF7aK5tz7xU2W2oHFjPMFqmLMl4NU15CEdv3kQkd1DWxQg06wfzbO9/xKRPCSy4ynXgXDOhOLp8UHS0b8'
        b'GjK1mDHQi0UGJoNUv/S5k2NdUvLCzeG4Yu5+oHDQS/SPc1SwGA1KvVVpxP1hqSq2T6rT4ZNxna5PptMJ7xuj7wqdrtSutzh6nHQ6Q3GeTico9aMHoRcfCeECQHLkK6Wk'
        b'DNmdaOHlGXJXeMEmj3dxxlSqOYcRh8MWiXhWhoqON//x/kKGj0VjrUuXxvzhX1JhrLvkg2V7XkrlLztfe4c6XC6d2FPy4U35T12x26esT0tY2nF80ejSj/aFfPnqlISC'
        b'42nTuh8kdf9ovjax8eiOiso7n577brnbmXEX315l/+7c5iHfZ67vGmr6w+v3PnpuT5B8zDK6bdj3U955U+d3vXL4b9zuKQ8WqT46vlQ3K3hb6fdfWhvH7A8IXh79r7+p'
        b'zDr28VYPwyo/riRuWuRB9uug1Vqvebmvn+pYcNES+ILlOcmtmYpO6KufO+GVrXkbDrzkNa1+WJk3f2e6961o7z+NDe12ae9oWwijJ3XUqC15TlduwRmuJdWjo0pv29ca'
        b'xpRuyGj+MMBn2eh/Tdjxyjf5qi/3Fny445PJC+Ydz5xz/J44W7eDbTmpgnsDbmSM35gcPG/v0vDawtuVWT/5fxk3dAlzoaCKKdK5fRsbz3z0/K2GG9mrXsg/8YWKJZVx'
        b'6mUL0S4A7TS84eYpaCsGt84gHhdcAddfEN7lzA8Z+DanFGyQ2fAhEGyaB5rkwciN40DS/8YnOONNBYJuFp4DHfAgCTmw1g1W8eBMQqo6qD/mDIHb/OUi0EGNQ4ZA7MHj'
        b'v9E3S0hC/ewH8blIqy3FeoNORxzuWvRgvBkmilZiJ/EAuwUp4864SxkJdoxPfbCjfPKDHeeTH+xI0UfCCm5Oeg/5N+KgJT96SZk0BR1EU+uY1d405zPAATHIkh65nyH/'
        b'PWyiOd+HJooXx96IlPuF3XnGO6+udC7ahjakyvFhQloyqAENTpTrMNFw0Gg0p2beZngjgvrz2XeHvzLBdUOs++Y315nKXWy5mzZ/evgqqHzh86BOzb1bSz5ImXD9b5s2'
        b'nX5v8fl3P9IVXr93EKwrz1h4bJ/u+H+s+2OGVjo649NPp2pKXhyW8MolbvSE0k8muG0/uvqyaX/MH3/v9PLvfHv9PlA5Eb0d6jMC1sbDHQidNHKM5YQyhS4GnkL7vzai'
        b'jqCiBFRo09SwE8OkqcEGUM0ghbwqAoeL88gkXjzcjukauww24KMqUE/o8hCNgNWrbJgjkjJwSZvYX4k6Z4h0KDhIciBYmTxTOwNuHvAHBeQqBm6Dx8F+Ul4bMAQc4WHd'
        b'oif/4oAcHiHp1SJ4whySJKZoLdr2n0RWBk6CS/1GMuK/OYv5r2oO+6tmZbaabQ6zwpFI6iJzVL2Giqh11Dp2HTfsoaor+0QWo7WPxcWWfWKbvcRi7GPxrSKKweY89MQF'
        b'c30i3sb1iXNX2Ix8H4trLvpEZqutT0xeD+4Tc3prPhpttpbYbX2ivAKuT1TMGfokJrPFZkQ/ivQlfaKV5pI+sZ7PM5v7RAXG5QgETS8z82Yrb8NVVn2SEnuuxZzX56TP'
        b'yzOW2Pg+BVkwUrjV7XMRcjQzXzxlUsSEPjlfYDbZdCRK9rnYrXkFejOKnDrj8rw+Z52OR5G0BMVFid1q542GR8YskD2Cw+/HcBPwIxQ/8GEyh6Mihy8qOfyXLTisvRw+'
        b's+Ww/+XU+IHPpzl888DhP7nA4fydwyrMBeMHPm3hcHrMBeEHfmmHw28ZcfgQmsOndpwSP7Dmclg7uYn4MRk/Qh76Aiwd535fEH/vaV9AIO5L+9/O73PX6RzfHS71vp/p'
        b'8b9WorQW25S4z2hIVUk57GlwyqC3WJCjI9qAg1OfDImCs/H4+rpPYinO01uQFObbrTZzkZHkK9zUfhY+kWP0SacLmckMuh9zlmIlUgZrHLXOy50h2e7/A/3s5F8='
    ))))
