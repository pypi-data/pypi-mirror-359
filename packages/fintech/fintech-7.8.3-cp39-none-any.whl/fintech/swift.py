
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
        b'eJzVPAdYVFe6594p9CIqgqKOnaEMyCAqxogNgaEpCHYYmBmYMA44dwYs2AsgICqo2LAggqiIgNjbOUk2W5LNZrMbQzbGtHXTs0l28zbG+P5z7qComLdv37fve08+rjPn'
        b'P+Xv/3/O+S8foif+SeA3Cn6F5+ChQwtQDlrA6Tgdvwkt4PWSw1Kd5AhnGamT6mUbUSESVAt5vVwn28ht4PQOen4jxyGdPAU5GZQOP+idU9Jjo1MVS/N1NpNekW9QWHP1'
        b'iuQV1tx8syLaaLbqs3MVBdrsPG2OXuXsnJprFLr76vQGo1kvKAw2c7bVmG8WFNZ86GoR9Ar7nHpBgGGCyjl7cA/0FfA7BH5dKAkWeJSgEq6EL5GUSEtkJfIShxLHEqcS'
        b'5xKXEtcStxL3Eo8Sz5I+JV4lfUv6lfQv8S4ZUOJT4lsysGRQiV/JYMMQRrjj6iGlaCNaPXSlV/GQjSgdFQ/diDi0ZsiaoSk9PocCuxjhksTsnhzl4LcP/PalKEkZV1OQ'
        b'0jHR5Ehx9ZSgwypX+JRpKvCdg2yj4ONaXDKJlJOypPjZpJRUJilJZezcZA2pDpajMTOl5DreQnYqORslvIiUkZ3CJNIQm0C2kYoEUsEh51get+Lz+Fo294RkvbrxWEBZ'
        b'wwFz/gvWGLzsLOBKJcACHljAMRbwjGxuDZ/S4/PPsWDYUyyIEllw3+aAXNG6EEdFpulkrhaxxh3pEiRFd1a5AF8yZ84SGz9TOCJPpOBcMjNdv5g1Xmw0TpEhRzRvqFtU'
        b'pqmuYCo6gUzO0PzHFb7S77xa/WXo/THf8J1j5xd9ypmcAHBSt5e7kKH3QFGZYX8Km5C6DrHmIvdvPL7ODRnKJ9/hfpq3d9ynqAvZggDgR8r6gjDKQ2b7+5OtITEeuC2Y'
        b'bMUnUv3jEkhVkCo2OC6BQ2YPp8m6lKf47dBNNLUmxmtkkDzkKPdPczS3N44+nPwhR11EjhbmuUdN5CYgFJppQr6LkC0QGm1By9MXACEVgRpSQcriZ8fEBsXORWGalP64'
        b'JhWX410oR+ZADi0iG2z9oT/Zh096q/F5mDwFPp9Ay4pJp20AhdTharxRjTsARBry8UGUR47j82zUC2S9hzqMdrpKmvBulI3Xk602iiU5NgK3kmoZQipkzVCRI/gIQzY7'
        b'xTnOj/NHyDPTNHyOXBTqCLOXRcPFULN47pZjX2QMXrtdJmjhu88nRZ9l/iXzBUO89jcG1U5/bYz200yv7FyDKevzzDjtawblnFitMlmjPa1v4pr75vxFF6ddiHZmx2jz'
        b'9TulWxtaG0Onza9Q+inSIr+d9nLicffo7RdX+t50PeCLUuP7f7BZqeSt1IGQi6SWtLoAr5QJtuAAkDyP+qt0uETqmEa2WX2hy5oJ+CopxzuSyVZSRSpAYSdy+CzePlzJ'
        b'dfH+SqXEQgXT48HD4wfv5wyW/JV6s8IgOkCVUGQ0WJ/vcmbeLUOnteppP4H6BDTclXPlPDlHzp+zyLunUEq6ZIVak03f5ZCRYbGZMzK6XDIysk16rdlWkJHx1LpKzkJV'
        b'xSKjDzrLCDq/H53/PU9ezvGcnD35H3keFItDP9FvzLuA9A6T6sCYIC1uD0jElUmgMzLkTdZLfb2SorP5Hhop7UXdwcU8VHeeORAJqDvP1F3CVJxfI0np8dmu7jlPqnv3'
        b'Ao+ruzzR1o+K6oierCPVHO7EZxAKRsHL8SmmjLgDbyT7SbUklLQgFIJCcBUus3nSIfUBKaCLhheoNqomFRh/7TxJJqgA0n7qs88yF9zYjmtfXI87tp+oPrHxbMzwzRc3'
        b'xh7gXjFQxXM13Il3QHsqHUdIXJScdSB1HuRsTmBcMCmNjU/0JPUy5ILP8uSgE7lqF1hvmsDk0eUiit1gytdamdyp+qMAV04KUrc4P5S5lMmwS6bTZxmtFtrJQt2Wku8h'
        b'Z95Cw14PYdPhgQ+F/dbPCFsBcE0WPgSiZnIm5WmkHiJQEIcGLZXiHWQvbmc8nUyqZgvWiFDpQlyH+CxEjj+Hd4kOo5Ls1FIQR/b2Q7wekRNGjc0bICp8jGykEMkS0o74'
        b'HEROkp2+zJfgarIbnxOs40OlHngL4s2INJPL49iEZrKF7KEgfkQm4vNh1At4nY1aHt4MPmi/QDrGwWI1kxGPNyLSTmozRf/UHjSJwWTkMqkB4CZEOlxdGSp4PT49S7DQ'
        b'cedD2aSn4sl5BpKTWlxO2m1jQ6VhaTBqF0xkMjLQIlwxgUF4cjUOQLthwvmLRAJ2GvA+QVCHSnGpD+LXItICmLQw2LTVcWyUBDfiZhi2D5ELa3EdI4HUDMaHGdQBt4YA'
        b'cD+4HNyAm8RZt+AryaRdcHXmF4cjnpzjwkkzPsxgMwyk3sUCEgjDwEx8HJHzYKRtIunbyRW834WcHQf4bHaAkRWcxHMsM5PcIRNdnMOA8Pq50L6bcyLX/RifRyT1dSGd'
        b'QPY4HgCbOQ5Xkus2Hzpdg0CqBNJe5M7n4dMAPMIFglustwPJblIjOLmRVi5tLQCvcxGkiZwSEdnbv8hlmY10QkRYB7Cz3Ch8DNeKxF3OJaWCi8XK4Y1jAVbLDcE7cas9'
        b'thSTA4KVnHcBwXoAsBJW3F3MpEBOkfX4kuDu5szjqyFIIuMmR+IaRhtH9sAwdzd3zqUYSZy4KA1ezwB4W5850L5MOk0Ok13gVHi/RVxoF9lIGl3cCnCFNDsKSUZwUaCV'
        b'B0UELw7HB6iSyMhOXIH4AkROk3XeIuxExApQ5XA5uUAJM4CW4+3kBGOkl20x1QQZLiU7RZ1sGzye8WoG6YgUyFnS7sHPxy2ASQsI9DBpYHRNwTWkViCdFJoeBcBmTp2Q'
        b'q1SwSLjB3YsL51HBjwtvLPUZHCFnjZPT+nETeORTMv7G0luTr65hjR8gb+45aNxjubF0ntedhazxVqEPF8WjmIsuN1bX2lqnssYA6SBuBo/mpUTfWH3LMjGKNX6+djAX'
        b'wyP/laOgZ+AnZtbYbB3KxYP/idDeWO1jeK0/a7ydq+CSofEVP+i5WKNjjatDh3OpgOfHi6AxJDGLNb49chQ3j0eeVydA48iTS1ij18wx3CJYfUcxNEbPmMYa509TcpnQ'
        b'mCC/IfgMnRDJGs2zAiB2oJiPZDeF2pRd8azxBPikXMAzceYNoVZjCGWNXyWpOBOPFOOmQk/HfSoRz4JQrgAao0Og58L7Ftb4q5FhHHW0CSE3BR+HhDmsEeeP45bzyLEj'
        b'64ZwS7GLY40XEiK4YljoRRP0dJ0xgzW+9cIEbh2Pkt/yhDl93Cayxu+SJnGbeBR6YPBN4daS++LwSXHPcaXAkMmp0HNpnoQ1Hop9nqsAGX2+5KYwT6eYJMrIN4rbDmR6'
        b'TYTVNcfSWeOatdO4Gh4tXzsRKFp2MII1xphncrWAp+8y6Om3ppg1yp1mcQeAovIiWL14URFrPC/EcIeB9nLXG3nzFv1NzKrM7vFcE4+i+k+/kVcbcNhHxHNuIncKKMpI'
        b'upk3b/XrStb4Wu5srhV6Zg2/kXdrgnY+a3wvPYXrgMbjI2/m3VpiXCV6/dI5yYKLszuHN4UjiStYURPZwyDF+BC+5GJxd+Nx+Sok6cNNHos3iL5vN94Dm5V2cr5IkEhX'
        b'MNcRiBvB6VCTHZzoDC4HHDiXNwNANdzwNF+llGGweOIvuAMStPxc8c2iWkmYH2scP/0V7rAERX3veCPfp9D1edb4fvSvuGMS5J8kuZl/a3qbqPfZea9yTRIUcyMJega9'
        b'a312uh6FkLhvpFsjZJD9C5ugTU/mMExW6MkcZnSibTjVwI24Fpfg8iSyDV+BTV8VKYtNUJEyyDq9M6VjhuAWRsEKL77wIEc/ZZp2pM0VxTp6gaPPHQlE8MxM0zcOUiSG'
        b'yFp8De/VhGg05AjZlgRZmyPZxK9wlDN/NBB83d6pa3A7pEiQxnPzET4FEqlhwDWCOdAfUt5SH3I4JFGGXHMkHng/OSam8bV4gwK3A/6RCMLV1sjJSy2UdaJfmiE1OPCQ'
        b'YMFeLHL5ULFxhdFBvpaHiRWZrtlJTogphweu1KhDwXmSTTSGIi0+iK/ZRjDEvadrWEZdRTe0GlwVAs79RCw+7c8hhVXmPjWcIYJP4KZx6nC0JB8+1yDIXVQ2lrgfi8UV'
        b'3IRA2Kyx7TDs3GKlqK9SQipiIbrSocNIhwtsUqLIeRhK9yilvkzznps2W43bpEsxbT+ETPgcpAYUYAVMOtRqpGIj6lBOMG4Ww0sNrslTq+WZsDI+ArGuHp8RU89mjlSp'
        b'IxBet4KShHRkC77OUmpyFR/ANZo4ilmiKBn3AgnZ7jzBhneLLL6Om4arI6RL8DEYuxfpJzjaBtE5G8g53KqJh1EheJeaVAZyyGUBxJKVEiVvo1v7AaG4WR3Bj7NC533I'
        b'QEqCWDM5taZQHSEfijdA+36UM3EEC2U+pA5iYDlscRJksaFIOoTDR0mbIObUzaSxnzqCk66CIQdQLt5GDjMkSCsQ0BlIxUHKNORaIj4tRa6TJR4LxjDkU8Nwoxp3IqpI'
        b'+DAykUvFTKnix5LNpDweyJaQ0iVIQq5xeD+uWmZLpB3XcbhMiI+NTZid7w/a/3CP6q9SBiSolMG8M27Q4+OwzTzm749PeAcqIWYeC+yHa7z7k2MDcCOP8NZ+npBR7SQl'
        b'pv948OBBva8sKoxjqhh/ZWAYEoN+CzmJDwcmBsdISWUwkkZxuJkcylH2YzLLw+dTBTeLTTJNAL9Tx42A0N7MkMew/8WHSLs7AKcUAbCTU4KhXhPTkmYFPkLa6cBs0Boe'
        b'KAvsJxPXO0hVV4BhHE9OMGc2lBx7QXScx8ieNcIymzOHT9L87zKncMsVVyuJI9chHygiHTKEy1gSNwwfWimuVhkzCxIy0uHG4dZwllmFhcxkqznFkzIXdxdcxZM2yHkl'
        b'C7iF5CAk50ye1UVOgtW5SBqJ62Gxq5xfel8GSPPAdRQgK3CFydZzCtw5iS3kkO5B2q0W0iHB63Qw5Bo3iJQMYyDHRHy+/zKBtFnliANzAEutwVtEquoCI1wc3ZwRvk72'
        b'I8l4LobURDDsdPgCaEC7bZkrhy9IYK193Bh8Pp4hEaLDJ1zcXZ0Q5IgbkGQSF2scw6ZLgYR2PeRFFnceN3ghiTs33i+fQTKKQHfbPUibG2/JRJLh3NQwfIlpYGjiLGEZ'
        b'rJJgAqw7uSGkSSoKoxrvmyM4g5hwcx9YfyfQuhlvZRaS5uLrQiEJC5DEiwslVWNYc34ST6rBZwehYHIgCDDZbKPbvUm4HG/A5R4w4wXnZYUckkI+hytTIUFn5nYtaDaj'
        b'xtiX0SKNM7bvWy8RaiHc3P1x+uKdk5M+inLd8sXeWP7Xf71/Vlf1YXvjzGnlmzxHDXZ7yXxX/nGH19t9X/plyrIxDfGV/l4vhhy9M+DrQf59huQM7Nz71+fW3D03OfZj'
        b'1ZGIDwd4uG6auNz1nm/ozl+ud337QZuLMH2xkHt48yf9R+2QrY7cNHBM1diqmnPzfqp03x01+KPvEu7v//NAcuto6oy2OfMTK/W/H/5qUdG06EvkrxfPBz3/ZsqnI7+c'
        b'uVk/y2WzMuPtrd9WDfvTZJf5/b5p0Sl3fjxcOUWXoWx92Zh09A/DT5z1i+nwrp3xxl5ryJfBWUV5V0N3TkxrrPxLx4nPp72dpru/6pM2P6e365a9Mvd+Y5hpKP584/IP'
        b'G7+JW1wY6X177q2UzM/5k6bq10MKF3r+eKv1M8k7a2oXrOr/t4UDfmfmv3n579Kgpnd+E3T+/Xc0qi/c1v999bQ7v1etdfpw0KFlfzxmff2DV1berVy+v6um0WSzHXjF'
        b'tNLd/WLhy681VnONcx6o30j9LGfx/YFf8UM/Sl5/+8/Ol9p/ij3aOP2TN2a63Z7+SeRtnfXND96cO6F+ivPKDXm1D76XBX/TMN7dU+lopXvkF/rgraQ8KBF8jw85QKpg'
        b'++uCT4KLJa06K/Xe2hRcFaiKxRC3ggKUKuhBysCTKsBZV0ezswCyAfzaKVJuPxTKIhfFcyF9XyvVwnm4ISVQtVYFXq4MZpfjbXwwblnEhobiQxpNkD9uxQ0xpFLDIUdY'
        b'ewXYTauV7YfVeKMmFlfj9oSABAckl/KOwwaww6rlYeQU3tGfbt5hVlIGzrNKgvpOkpD9pGW8lTmAUzlA2kVfTVIwh/hCbire4ax0fPJc4lkPpezZ8EdnGV7iWYbVojUL'
        b'WvHYnh1pLKfpzzRnzpGTc/04V96Rc+XcefgkoW1enDNHj7kcOWf268XJH0jpL+8J37p/4DPvLn7mnR3kHP9AzrvCN2/eE+aTyqXsoMwbnnL48YH56Wd3zuKKHh2bufZE'
        b'rcchyrOpU3IWt2762FTTUfdxyvV+zz5OoYcu+ACpmGk/TwlRQuALTIxXibIJlCtJA5qFTzlAGKvCu5Uc82nTySVcpYkNipWOJ+UI0jK8v3juU0mqW3cOmSwmqfT8Hj19'
        b'gm9we5i08v9U0iphB2/Svy2FBZwVPf4lU6kKCu3jNy/sOmdFgV6RkDoxPFSRb2EfwlSPDX3sS6xVYdFbbRYznctkFKx0iiytOU+hzc7Ot5mtCsGqteqX6s1WQVGUa8zO'
        b'VWgtehhTYNEL0KjXPTadVlDYBJvWpNAZmUC1FqNeUCmmmoR8hdZkUqTMTJ6qMBj1Jp3A5tEvB+lnwyy0j+mxqdhpqtgrO99cqLdAL3rhZDMbs/N1esDLYjTnCD9D29RH'
        b'WKxQ5AJq9KbLkG8y5RfBSDqBLRtI10c+e4pg4KFOb8mw6A16i96crY+0r6vwn2ozAO45gmCHrVQ+MfLpMSCPzMzEfLM+M1PhP02/0pbzzMFUBJTMR+tNgxaT3mhdqc01'
        b'PdnbLqtHnTX5Zmu+2bZ0qd7yZF9ozdJbetIhUER675ylNWmBgoz8Ar05krETBpgNWmC8oDXp8h/vb0dmqYjLDH22cSmoAlBKGdVb12ybhXJoxSNs0smxXIvN3Gtvegwf'
        b'yZ4wpy07F7oJ8M229FlYZ5vyBX032jPNuv8HKGfl5+fpdXacH9OXNLAHq97MaFDk6LNgNuv/bVrM+dZ/gpTCfEsO+BdL3v9RagTb0oxsi15ntAq90ZJC7UYxy2YVsnMt'
        b'RgOQpQgRva4i32xa8b9Kk90JGM3MSqmjUNhJ05t7I4vdW/wMVdP0Jq1gZcP/fxDVM5WIfBjOesaih/6uIF+wPjmBXTP0QrbFWECHPMtzU1nrjVnPwJhGLqu2W7nSIXLB'
        b'UibTMzTMvugjdXx8rWer5n+b7xY9RFEwukgFeBnoOYdcyc7LEhforT/1RUB8Rp6+h6i6EQIWmMgVQdCbfm6oFQL8M5hon4f26B3ZpyKuxmbW6c29R0z7shAje4nVjy8M'
        b'fX5ujpzCx+PuLCptcsxgFcBTGSCJoeDeBhZYQADg87S9r5tsB+vNwYkW1bOwf2ztp/DuPf7bFeGJHOCxwc/MB8SxRli694Gx06YmPlvtMvItxhyjmarU0z4kyQ7LYgoJ'
        b'BqyItuiX6oqeaes9Z/4nFFrs/t90JrlaiDa9urxZ+ixyBcy6F5/wv4AYNQNmZ9TPPYZXKkB+3tjM2qX6R97Onhcr/BOhuVc9tVkKWF701Ig0vaVIb9ZRs1xZpM/O6220'
        b'oC/QRvZMrGGCHll9LyMWms2LIxVzzXnm/CLzo6xb13MfoNXpoKHIaM2lSbrRQrNUvcWYrTDqfi7Dj4TNrXYpdZuAU2ruE3Vojw+MtO9zImFf0FtkeLz3Y7cEdGfn/dQt'
        b'QYxY2NMYz7MyiFDvkRNPqUaL5+vj0qT0bkERGhExoXi4G7LRYrPUvijNFbfDvncSmkQuk3Ws629VtNQKeYYW6l94P24EYodvy5/Hx9VhCF8l2+zH4WdkrB4gFddnB8LG'
        b'9cDAx/euaNhQ2UDclKB0ZdVqZB++IgzAF0l5SFxsMN4aEpegCY4jlZpEGRpLKuWBsMM9ys6O++IDXoFxCbht0cMOXrhOglvnLGHnatlrMx6di/vOEk/GJ+DjuMl+/o3P'
        b'kcvi+bcb2fjo/HuojMGXkhJcTsoDSeV83JYQF8wjR3KRx1vJId42ko5vIY24ma2wmxyIJRUa2JmTqpAYUilBQ72kpLbfdPEKohmfgoWgo71TETmdRLaRMnobMjJQ9tyS'
        b'ZbYxDKHMvmy6nRp7xyTx4iIxgUNKfEWG95GDeJ2Nlr7hXYaRPWYklw3QsTwkFnqOzJRFrZzHVib7s8ieQBWpxJX4FK5OUsUlkLIgpRwNIvuluB5Xk83sEmE+PmMTuyXF'
        b'JpCt0KMYX0AD+ktDI/Axcb0mcjUHpId3kbZexCdLYGelAjnhrA6TksoEGLEH6XB5nI0ebuDNLjkgKR2+8oSkcKkbG6gn123qMBk5HMOuFHLJ2cXi3UXnsBUSWLPaAbQU'
        b'heIyfEi89SgNxOsfCZdsL+qW7lXSwoQ/A4RbZb/c2Danx+XGGiUvlm60eA5Q47aCFfiMHHHx8B2XkDLxtmXnGHIAYAi3urELmjwtqWbXYBZncoCpxMjBPTTCDzcp5exQ'
        b'eCzeQurV6gJ8DTdKEKdB+DQuxQfEBfeRCrxNrSat471liJuDcIeJ2M/895PmWLXakoZPw6gkhM+QvXiXeMx8CV8i+2BUG95EWmFcGsKd0wqYVZKqiEK1mit8DiY/ivIs'
        b'jswA54TgUrVahmtwFbTXI1M6KWfmei7FGwVRczW/pS+c3BcxDktxLd5AduIqgUNoJprpRPazzi9N6kOrXyeERpz02bu0CCkl4nVYI6kjJ+l1SiXeTupDGGMdSS2Pdw3G'
        b'zYzzuGrBco0qOIAKepkTbpEijzSJiYC1iUf6zeFDNLFBc7NBYlIphw+RfaQFZCJejB0bA9wj15LszIvGG8U7jIPkDL5KeWfFF+zMAxexiV12riYnwQpAGTLje7NCXJ5k'
        b'nx7XSckGYDOunGhnc+EIBvDC58dRFkck2xmsxwfZ1PPwFbyrh50ZyPXHLHf5WMbEKWTHahAEvjBKlARul9lGI1rIdVpLR5vxjmdadPUShkI63oZLQGzkIq06o2LzKRIt'
        b'b2uRtAcGmcMeM3RyTs8uCfDZlAlqtbTIgV015pJDYnnCwgHuCAzQJ1TutLQgYjFS9hPnPGOcqYkNTiR7FqvA3P27j3gH4RIpbkgEI2N3viXGInZzdhkfVwbHSpGTAw9Y'
        b'1vuJ6lxixDtAkPjs5G5JPk8OMXOPCMIdTEXIVnygp4rE4hLWgTTjdXhTYFywJjggEdxsCS0z9siR6Nfizcy3ppPtMfZb20C1/d4WuEYvBwfFS/FOCEEbWEdyVFXIOuLd'
        b'+NijK95H17vTyCW25CRcUQguaBTZ8KQLOubIRB1Lzs6ifE4YRMrxtp5RJyBbhk+SpnSmiQvxcVKtCdHk4cYe9+BKKVtkutcIelGcQS4+eVc8uw+zjZAkUvrIbXkm2r0W'
        b'qVsuqvn2JRrRZ1miHrmsIPE+bkgh2UOvPJPJKVodKl55Dk6w+VM2nJuJzw5yZUynDMdlYAJkazy9M9BQ5obhPfJYPzd7uVu8RUO2xQTFqcnxpGA5ctHwpM6NNDEcPNMz'
        b'7dexqwc/vI3F56MZDjOH43p2xQsCOJ8gEy959emiQjQuThcv+vtYu+/5TdEs9OMjYL77WTlCj1KEQbiCVSOMEq8i8VEnBegTGHNdt0K54kaRL/UxZCdVxXzc+UgT0xOZ'
        b'6o8l6/E+fAafdIH0JAWl8HqRyooQd7uGFQ3v1i98jVSDM2BO/iK5BmqzFdfbPR949jbRG7dPwfUuFnkOXg9fTkASQ3aQs2ytieQs+MuaDFLNsdJQLl0MR+dUpE7U+Pr8'
        b'ngpPDpMrzBB3DXNCnhDDQguHLGhbEiAW5uP9/CK7luPdi3tT853knFgmVjGcXCHVZI8DKR1MXSzKgFi4i5mATzSupTqFW8nVXlUXd0xiXkpVTI7g9lAJqDAN6Ci/aJwt'
        b'HdpnxZJSATSLVMbOTsZtoSlzSCkrUFcF+5PSkIDYBPreQIWZ7EqhnqI0KC2GypFpyeyYIAoE/6GZm0wqpQhfX9UHso0TeCu7N5/vIhOzydHfPO+pmY/EILLFueBJZViQ'
        b'w3QBt3ra4/OqNeAK28MLhpEmiM+zaSS9AJkbKz30TqCQof04FglacAPZa1MzPQOrvEyqcWls+EIQ2m5Sg0sL4VEJcj4dgVtkuC1rjjULnxvHgbjk84dOZ7qgITvy6Izz'
        b'o+0zkuu4GSIexcONCwBjSRsoilWewQdAjtEkurEWfGZ+d6gjG/Dmh8HuQl+WQk5XkWamFvPw0Z5qMcpe4cfFkR103Vn4mp3GgZAIUQ9NKsLxDjElGxz9VN5WBoygjEzG'
        b'ZVMez9vwJtzJEje8NwqcEhV7/4QkdcQyLb4CMS8OaJtI6kQDWCchp9XhcnIFdIGma/oZeBvjb58x5LI6vBBvSQZ2RCF8ohiL9aApeAfuBIRJK7kEGSsNlW345DAlxzgl'
        b'kEYbAMeSxoUAi4ZwSxrIDhu94po3OsAFjKMcRF4eQqpSSKsbPhs+NjmmW+3mBKfNeVKVoHv1HHzIGXYEl/EeZn95UaSjiNTjk3KEilExPr2SIZwwLQ2fjIBINJFHvDet'
        b'NjkygBVmRy8frwApnZQhtAatcci1qZjlzyKdQnCAfAzZGjLHn95yUtNLf2zx9GAHvAuiXbVtEh1ywY1ccElMIJXBacw4UsA8SFl6TNzcmFSRGHwimZQmBKsS45Nk4AtJ'
        b'qzPeDOn6XlBnKoX5enKG1hTbX1lQkU0+jGmhkNo0gsaelpG2YbTQFeGTvt4wiOrPNFy2plu/5OBCu9WrGm9iPi6lP65k+qVPfCzMzmXSMuATI2ltR6eGtLhxiCfnuXCy'
        b'a60tgBJ0PhWvd8VX/4uIgZuGiLpS7eUukM4C/UoPWvhaxo1eiXeL2V7FxIliMCG7YIfRHU14vF/cgRwDm9xOc42RSb2kGrgOl7N6L+NlQcMJBvg4IK/Vljq5ym+m5+mf'
        b'ag8efPfi5Xf/9v63+z5urfzrwZs3OPnG+a1jczY5DkMj9zfpHMqjF4VEOr2ZcKd/bkH42AVHBpehYfxHtTeGjx7+wZivJX5eX18yfFXsFV2/d839S5ebL336hxrD1HGr'
        b'c8wpiuOHv34h7WaNYU/zR3/Oubm77HzDPmPR2Tdvv5baeluVmuDj9pmb88vvfHJv1YjWfQmnAz78SRphuvXHH7Y4xeZufvP8hL2535enf2neu+Kl08NerRme5PLZ3MGz'
        b'f/Xde3cjlkX+VnLKuzGz3m3Q96u3fvt27Y2P70TeGVLwVuO9j376u/K5ojzb9Oyk50cXp7+c2vGxa3JD+fUCg+1QwMeRuMXp3qRbda3fel2++NvvKoe83PTm9uWhv1O7'
        b'FVfc2xGckvnqL4bXKZccGnTx/WzLTylnV/otCdn4judrTkX8nyYWkDL596cLxtx0uzHZ/bULUzYNip0xKfOQ5x8/ibj7cv0Hrzb8Ypbu09zXPiBJr701/cov/7zdO9at'
        b'3Lza+JIqv/PtPxkk3qv3J1WW3RsWuPJG49nbofuHTY/3tRQYjt6cvPmAYZlfdPlXbae/u/tVmXtWhPq9Mu9/fP68LPXFIvfipINf+X35afhFt9JRH9XeLbm8JtfwY/iX'
        b'p9/97fN71Csavv/yxV+p0sdZG0hczOwT/d87+NKF1yob0q6MKsr7tvM35wcmlXsfKhntuvwvo09lFUd3cP2nrf2i6foHz39z/9RHq97K091Gi/3LQpYLfr6X6vfd/9Hv'
        b'9t2PFwXcjTuwipsb8eUv2i7HrHC44p7X8Le88oisua+YZ3SmlY4/enrB+78pn53y4xtzJoWU3/2q4acBHv3vOb8ekZbR/9517xF3NBvWBq4s/WLce9/8efeSl99yHri6'
        b'KWDS5GHv/scl64dTbvhmtPzBOvIvlVteSmw+tXDzrr/edFv/XkX254Y1eVNaMlZZzw/5MfDo9QvOh4YOPfddaPrrh70Hj9k2KsA65uu5dxJfPDWmcOJXL/9j+N1vfWy/'
        b'/8WR9MJ5u4Lf2/jpF65rG/YXTX9wsvra3XtN6muzh01/o5982P3Sre27r8078fkej34vNf5maHT/D3/Y5HxVmKF84zPNrhtk18XocfLiuR+8G+3W9WOn9S/rzqxv/7Ku'
        b'4KvD07+4ffUD169V5kPxU+581qeq/u+FfWd89MWosPDRupjyFq/vx/1x4Me3asnV3/2uIvZjr+9//+DHwZ9M/5X5vos60xiTvETpbmVhphrS2eZAsXwETJP6v2A5PrQA'
        b'DcCd0pgRWiv1UStU6YEBqqnksBIsGCGn+Txu8A5mBSxkD67TB6piH1WvDJKL9SvH8BVWZuI8MT1QZbb2LFCZksHqU/zwDrJdAy7hsFvP+pQKvI9Njds88F579QzeZe5R'
        b'PROFr1qH0n1GKC4NjAmC3K/0qUIV3DiVvVWVig/jPYGJCZCDg4vahmCRi3yRguy2iuX3uINs04SsJi0QC4IRkhfxqmErxcqbrfw4DeDFCJuQRQtzPEIlOYGkgQ0lpSNg'
        b'JNnmgg8+Sg3cE9iisL9pxBcDVbg8S2SZHJ/i1Z74OpsY15KGZeL7PS5D4hO7X+/xxXutLFk+iS/5Qaio0ECCVSC+KxaGG1H/56R0u1Kl7PvPltn8iw+l2/98nqfeSFpq'
        b'nRgeysp3omgFylo0z5GT2n+cWakO/ZFyPOfKedESHPjfmee5Xn++c3Z3ZCU+jpwPK9uhfX3gf/f7cpkz1/NHnMVdHPes+cSfz+QD3DkFRwuBpJwn5yPx5NxZcZGU84Nn'
        b'P5jFk/d84MzJObGUSMrKhmBd3pWn2HiJq/PObE345WnhkZynNT3DoUVOsRFxgrFyXixUcobZfbh+AB8IK9ARtJDJ/Se5VKTAne8ua/Lk3Xk2B2/xAB4mdtchSekpco/6'
        b'o/+5/JScxbNbgmytnVRyNOVE69DXI59dqUR30mQdZO5l9lIlUhVsg+Qbkj2EBhZI6M6YXH3qZTyqElF0CZrk6ekr4mgBr+MWSHS8+AJwlyc7H2e1Q5aZFku+5Yeh4ok5'
        b'Uy+LvRRIr1NozQo9hasSldIux4wMesWQkdHlnJEhvgsOn10zMpbZtCY7xCEjQ5efnZEh6uyjB6OdHrNVAXas8syRZzmNnuwb6+JOzltdnGLwrhwgM9hif6UzhBySy8gR'
        b'qZKLNm4MXyQTBsHYz2Wdk6suJpJkz5nvfdved5LL2x9uGvf5pE2rXbwGD43irMpt7THxfZSyC9OO3tx9W+21dnvVS+6OCervX/vdn/aGfL86N2D00NiPYq5O1k9OSz+2'
        b'IMF2Lz07p8744YwUVb8Hi1qUr9zjv1d9O8d8bEnJkRfLP2os7vfhtn7zfad0+M8IEw69dOH1B+9s/+hcY+Alb/+tNVnjZ//p0wN/58t9A87uuZV6Ynbj1GrvpcWR1r36'
        b'bSu85+nKhvz6VOuvBn5mav2l9zuft/56yD2/gpi1b2hGzvITsDKn76SzHW+m7Vv4xz/ceP9AefhbY20pocEp8dUh1xu8P7nSpFGqq283dpwe/O7rCV846FsubHsXQpv2'
        b'0+83DJKfzfRsjpkZ1qfU4f2rP6JpP6QFH3RQSlk1oRpfXgA7AY50ZiJuAoJ0/PgIMbyU4NZk+tZsGq7r8eIsfW12UTbzlnmD8GmXAHDA1PsnDJvQ3WcobpeSM8M5FijC'
        b'XfFeAZ+OSQzuzj9jcQnqQ7aDQyXXZaDtTOm9/o0+Vc7S3Gc/mK8EdTXla3UZGcxRPk8tw5s6rXBuyAOep7WI4Bp5T0dPh54uTvoPuavdhd2TO/ZLoi7Ufy0q5jnLgG5t'
        b'BgviQcUf+Yg+/x4yOYvPQ9uhi7N9Iatv/Fz186+LppJSXIPL6QEIKUsiFfnxsM2tckDuvpLBsLU4bHwp4SckGKDnq2/8dvDLY903RHlu+d1aQ5EbN9Oa1bDlzpEr+MV5'
        b'pw42WEcPXeVy4cSL6Vdbk/9wqipt1T3DqwMyUv5jzfjNM5v/MXffT+mTOzaFhm3eVjdCMuaAekDLyOjR5qphlpr8t0xnL/9w1+Ol130uNGxSOrASXtwk8yflWR6AUxLb'
        b'GzlAuG7jSZM3uWhlbzAclFs1ScEqGzlL+yQF86BYVyT4SOpYlmLhq/g0kMUIo7utU8sTcCUjzEsyhBwg51iWRDaSlmWaWLESl+xwkvKOGW4sW1hNDpMzGo+RPf4gg4uS'
        b'J9vnjRPxqy7CdQI5/MKTf7BhDtnBbCuabMLHA+NkiMMHozX0hZvzY7sVfsi/OZP4V7VI+rMmYjQbrXYToQQiN8fukl9J0FpEf5DF96HiK7okJr25S0qLS7tkVluBSd8l'
        b'pbeoEDaN2fCkBYJdEsFq6ZJlrbDqhS4prTHpkhjN1i4Ze5G6S2bRmnNgtNFcYLN2SbJzLV2SfIuuS24wmqx6+LJUW9AlWWks6JJphWyjsUuSq18OXWB6Z6NgNAtWWlXW'
        b'JS+wZZmM2V0O2uxsfYFV6HJlC4aJt9hdbmKmZBTyJ0SEju1yEXKNBmsGC2ZdbjZzdq7WCAEuQ788u8spI0OAgFcA4UtuM9sEve6RaYtkD7FE0M9j6YP+3QkLjcwWqpAW'
        b'+vcULPTC0UIDukVJH/Qg0RJMH/TewkLDnCWEPqgKWqgrttBjAws9P7FQl2qhx84WeuhmCaUPep5pCacPaswWqpoWah6WcfQxnj4CH3oGKh2nh57hH9HP9Ays5w+O3X/b'
        b'oMszI8P+2e4ofxhoePwPvyjM+VYFhel1iUpHC/U/NMJrTSZwf0wr6GlMlzOIxGIV6LV9l9yUn601gTTm2MxW41I9Sy8sE7tZ+URK0OX4nJhIPE+TFpawSGntvKh5nv0A'
        b'a0fuPwHP72yh'
    ))))
