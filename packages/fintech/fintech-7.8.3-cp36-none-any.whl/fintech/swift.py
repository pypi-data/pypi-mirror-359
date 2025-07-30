
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
        b'eJzVfAdc1Fe2/+/3mwLSRURsMHaGXmxgwxpgKIoNRYWBGWB0GHCK2EERaSIqCAiKooIiogiIYk3O2U2ym7KbzSYxpLlpJqZskk3ZzWaT/733BwKW/Pe993nv857z4edw'
        b'67nnfE+5954fH3D9/gnkJ4z8mGaSh4ZbzaVxq3kNrxH2cKsFrWS9VCPJ4zPHaqRaWR63QW7ySxC0co0sj9/Na620Qh7Pcxr5Um5QutLqR63N0pURi5YpMjI1Fr1WkZmq'
        b'MKdrFYu3mNMzDYpFOoNZm5KuyFKnbFCnaf1sbJal60y9bTXaVJ1Ba1KkWgwpZl2mwaQwZ5KmRpNW0TOm1mQi3Ux+Nimje0hXkB938mNLyU8ljwKugC8QCiQF0gJZgbzA'
        b'qsC6YFCBTYFtgV2BfYFDgWOBU8HgAueCIQUuBUMLXAuGFbgVDC8YUTCyYFTB6FR3tmjrHe6FXB63w2OrfLt7HreU2+6Rx/HcTvedHvGEPWyhkpiUXu7x5Gcw+RlCSZAy'
        b'Di7llNYxemvyXW0vcOcHU+qS9Ou3xHGW8eQrnJsViSVYFBu1BAuxNGdsrBJLI5Yv9pVzkxZK8TZcwONK3jKKNF0FBd6miGjcj/uicR/P2eAeKIoQoBX2L0zheyiQkB/n'
        b'XgpiKBN4wob/DxNSnXsWyxdKyGIFslieLVZgi+V3Cj2L3fPwYic9stg54mI1Jjlnt2CHnFMk6S/LcjhWmG+RcFKXTtI2yWdJhk4svLp5EOcUVkjKkqKOzR0nFl5ylHLW'
        b'PrEyLixJbz3YitPbkMIrS9zW/cn6kwkc95dJ3widgUt2BPL6QZSzI4/wrVacYnFqctDbQWGSOI4VP5PwjWOFI+/ZuuNH/me37VbAdXMWP1KBV+D0JML1En+4mrbE0xOL'
        b'/cN9sRialnlGRmOZj1+Eb2Q0zxkcB82CC+kDeGvTu+AAylvKVy5V8oB7/K9yL+1h7skf4Z6tyL0Raxw4IvLpOdOSfD4OSO2huhLPwVFC9j5vFe7Doqgl4RE+CyA/YjkX'
        b'pFo6FCqWQQkc5tJkVnjcLsFCB8b2FF0wXJH6jCNIa+I2Qq6DZShF3W1sw/3B0CF1MpPfjnEb8LK92KM+LDE4iPPIIcWVXAoZcY/FhVKkxyNYLsN2OMtxfpwfXMMORupL'
        b'W2w40iA8a1RS1OBBi0TxPe3tzBF0b46yS5r5l2UmTlceE8qb1KTmt7K3Pkv6JGl9apT6xVS/Q57qcPX9JOeU9FR98udJkeqXs6xTlXERauVilbpFe5Y/NyTtE02k+gXh'
        b'd4GnW68ERQi/jbuz1K3e51kXByfvY11HLpU35Q3WGAIkaXIuvHDo/r98pRTM1CDgbYvElrAJTmK1Mtri60VkLHBDoUBqvXOOeQRtcXgYXCLcLMYy3EdwGcLDVeyAS7Oz'
        b'lXy34KlUSoxU4H2PJu5H15mpxsytWoMiVbRefqZsXap5drcNM02JGrVZSw2oyY5KeKwdb8c78da8J2+kkjZSKSsl3bJNar1F222VmGi0GBITu20TE1P0WrXBkpWY+Mik'
        b'St5oRb/L6IOOMo6O70DHf89JkPMCL2dPy0hSEgLtWOEd7uMVA6WxET4O2yNknCvukg5XpS1KEXqAJ30MiomVeIBigdkACUGxwFAsYSgWdkoeZ/B61WIgiuUxDDOeeADy'
        b'sJwg3RfP4A3yPDndQo2TiyvWYDnp549dFs4fGraxYmyxWkUwRvAVAwc4P7yRo4vWfSkz+ZK6YV0lnyX9Pjn8M1t1lHp96n3N/SSfQ+HqL5Oc07i24aHVNcPzhk9/lS99'
        b'xuoPn+UpefNw0mf0eNjlHemLhRFRMTLOFi4JCfF4zASHeiTxEKtZKWN0t60oz1R9ptrMBEpBzXnZ8VIiTqPNA2FKmXC6ZRptss5spI2M1PAohX4CFIzU5PeTIu3u/UCK'
        b'bwyQooKy4TQUO/RKkfkGH56bvnZkhhQOwi4osbjSRsXzJ5nMU+G4S4CUE5I5bIQCvC4qd8F0uEzqMtYH8Jyg5bAJWtewmiD1TNpnn0+AhBPSOGzGAjjEhjPGK03maXge'
        b'L9LhDByxNI2Qy6SogaORpC7BO0DghEzaqVVucaPzHIbb0GLCjinh4+hMkEfsDeTHsEq1C5yhVQvgdICM1O3hiG61wFXLMEY87A4zGadAB5yjPcmo57F6JsMwXCYz12C7'
        b'JRDqYDelhtg0bMd83MsGxnafbFbbiecoRcRKYQden8UW6D4eC02mYI/JtF8OhxfwBh4Q+VXlvpl20+Beunio4fDqhu0WChPImwh7aR0BZWuAFams5bBrDLSwjjLYvxbb'
        b'TXZJcMKGTIeX+cl4aqW4jMocPGprnLoWrzM6G4ljwfo0VheE15xt8dIUsphSWkkctmQJnBdpubUkzNYmCC5ALV09VvKDxsApccijWMPbYmfgECnrlc/zhKc3WLcwuCk3'
        b'YXs23MITDpSUet57TTBbAl7Hk1tNg+zxNnEMrXTM2/xUOIRF4nzXQ/Cw7UbLYBV2kggPL/ETAqCcVVnDRXeTrTETLptpr2reHa7gSUYKFELLdpMZr0zE/ba0spT3xtrB'
        b'jM+4C04OMjnYYwHeJFyRyPhZI8wMLZi3HQ6Smq1wwoHnJIP4sMWzWRcv2If1pCINczfSlV3l/ZbOZTSE4lnMtbXPwkYsg31STjKOD0vUstFcNT4EJmNGUwhlEftAvFab'
        b'SFwRHp1GsUzkO1nOCakE5djsxsaDU1IoJSjI9mPII6hs8yXugNn8QmiUmfASwVMV7nWkTLxA5FmFHSIS2jUZJuwktU1wjNWe44mTxHylgrk1fsUQfrLAed6VV22Mj3vb'
        b'jRW+uWgoP13g3O5uss2pnp+TwAobuWH8TIGbfnfRK0nVmnVrWWHKDjc+jJiTu+6jdlbHyCexQoegEfwCgVPcnX1iR3zQ2CxW+KX3KD5c4Jzuuk/Jih91YygrDAt056ME'
        b'LuDuusjt1Z431rNCpYOCXyxw1ndj0jdV2/2gZIV/cBrHL6N07lykjtct8WWFH40bz8dTOg1bzXdWvL+UFb7jNolfQ+lc93FqvCRXbBmRoOSTKJ3DPYxu+jW2rHC9mxfx'
        b'D1zYXV1nltugb3eIccpEXz6dEh8ipLmNfGoOK+ya4c/rBS7pbsTz6XfibETi9wUE8Fl0Rav2ZtzJ6bRnhe8NC+KJfV18V3cn221q6DxWuCl5Mr+ZLnO429Z4mz+aWeHi'
        b'nKn8doHLuhvyzvo7CRt0rHDPnOl8Ll27ssoQH24WQ6fOhFB+j8CF393Sqa5e8cIqVvjCmJl8IWXIlme33XFv2SBOtG4Ov0/g0u+G1JjiF78Sygo7dobxByiXlO2b7sz9'
        b'fDkrPBM2n68QuPi7Edmm6oX3cljhmCkL+GrKOp12yx3fk55ihJu0iD8qcJvvDvJIro5zWMgKd+kj+BOUn8tzt7qtXWHNCjl5FH+Wsm5CgdrNZBGZ/L4klj9PWTf0G9Od'
        b'ZWmrWWGQsIRvpaxbHrQpfvLgbazQsjqO76CsW56/wy1pNC8qehNWE9NvawO3x1Hts+PD1NjM4jq4EBpka3TQp5NNiGQwP0sBPZBvxMqhBPBXsh2J3kqY5fAmYcQ5Uc3O'
        b'u0AlsTmmcViOHdQIVPBj3XcqpYwG44Ln+KMSstiRe7e5Of1zOCv8i/Pz/Ani+O5O6lLHR1wdxArfHvZ7/rSEgMfKe+udrS0hYkv7l/izEsKBSdvNbh7NsY+PsydznLiN'
        b'o/sXLlX2n9mp0NmGPhKlzIixjKVr7CIhYBOUxJKNVRkWRUT7YREJFV2TpHgOj06aBOcYtWuJmtCuAQvSoyYmB4hxbuMEsnchZV95WOzWhAziGEutnGC/yl+F9XG4P5ZE'
        b'YNa4R9gClXCJySgCagVoJ56vA2vGSjl+FWGynYJZp7W4C295w0247Eni1UJ/ErTYpUkcJxKvyaR7ipivQ0Q2bdhEKAnlQqEe2400PhHBM1JGV6rIHbzVx3FqjFj47lyy'
        b'D+PIBstV7xPhMZxjgVambGcwjfzgEHHnUKweYSXuRWtisEBFA+IEYqzL6EZTBWX+EdDiyXMKs8xBCe2s/1gHx2AqF6ggUbQkOYssjW5Qo8IyvMleim1Pyd4qIgvapNwQ'
        b'pQT3jRUsdFu8PCWU7C3YzmI5XkvZMF0E2Tm4sD2YtuXgOAcnoF4PJ6GMzQSntocGB9MvdRy0uacNl4khThUc8Q8OJvEw1JN4B86vh+ucuH85gl2QHzyVNqrmFnGaDeNZ'
        b'WBHvS4SCFdAYSWmLESXjkCWZLs8Q9aM5yTl4KiXhCJcFZ7V4bK3oWa8aR6vsBkWRHv5Y6s1ztquJz4Bzm5h/0vsvD54qUM5xuBfrU0lgc4wRmB2GxcFTKX0klrgFF9PI'
        b'TqRKdEH5i+EilpCtSbSMk7rzBAkXySZlPzaJK9uPJ32CpxJVgKPEBXunE1acY9yF61A835t4+nwqECyKgRYpZzdL4oi7Vohdb0DHU8HQSb+e4CLxvF4BZ8Wo4gB2bMaS'
        b'qEi60ZHgLX6IGmoNKksUbbprGZwzRUVERNMDiAdbS08/pVe0n9JXsIEGLTSaF5AA87SnJzS5eiuhAk97u0CF61A8PQzOCBwUuzgRfz9UFOduQmOdd4xvuJSThvFwOxLO'
        b'YckMxq9VeMpksjdaqJ2p47E4dNwcG4btzVswF9sdxJpOHvKxVRm4SQz4Ssimdxe293S7xeOVTG9sU7E1C3hUZSLdRNPkDK0ecE4hcuNYGNSZNlpsaGR6nXczK/BMHBuQ'
        b'J8w+Qtx8NnbIWGC2FsrHrIPdYiUUCyTGwg57nkVKJLZsCRoChxn58zF3kq2DLZQRG7qaX+GXMANPs8msCe+rTGabbBoG3uTjRo+CvG0MV1M9VtJyOtEuPsuowNblIq7a'
        b'yZboLLabjdhB49FbPAlpLo8ct4SNZ+sWZ8I2M+6BXXJCUh2HZQ7xjATYpcYjttb2xD5KpvHjoDA8yJNxcOsYLxLDbrSjZNfQwa5MwjapqBMH8KyTrYMd2ZpIZvD2ygjp'
        b'U2wWDdGcSmx3NJJoUuLAq4KmQbOMDWaPbQpSgW3UW4zlyT65ce6kIWJ0VaLGfNNGNhF08jnQ4I5FZlY1AorhlslGlNMh3gqPK/DwZqbHg5f627IKiTM/b1YA7DWLO77d'
        b'o6EEyydiNVEVH84nbA7TERnBUCWUONpA1ZaNm3hOSqI0KCW7yYNKQYw/L8mhpVfzoGptKpm5nvEnW4W5vYoHJZPT4Cqc0f/9l19+GakRraNTZk7U3hwVp3QRjerN6Zv6'
        b'EDkWqsYR9N5mUDASU7u/PyiP4DHlQjwiwutQ2qR+mByf4m2GRrEmdydU9GFylskDmmxFJDfiUbjah0mi6/sUcHESqxyMB2f3ByVehUNjvKGAVW6FU1jRH5awf1EQFjiJ'
        b'2l2Gt6GkD5cjZyYQjWkViSm0hdN9wIQux1HmqWzh07EKavugCVXeCkWPi8qajXn9kYm7AkZOjWdVjnNSKTDNWNqLS+Ku9jBZTp1teYDLiEHhcDlc1Gy8CTf7IXPSqklu'
        b'KG4+4DIewsYHwCR+MmIwiHtYshVrH9EHTRMemSaJYjXrTSn9kBmNdXOXwGUm+kgsT+8DJrSmu0tDWJd1E7C8D5Zz4LzCBS8xmncuWPIAlikbAtLxkC7TnpeazhL7O2ZB'
        b'w9pDXTEfhjntbb721vcEc0eD0uZF/WboixO9BUEYv3tMUpuzdcI8mB8wd0pR/oe5T78/2Np6avdmD+2pHZz77vvGSVF/Wvvdd4k5Ky+/U/O79549NnfDopyZAU4f3w38'
        b'fM6ug1EOmudvPe/3or35pfrcEc9WVSxw/fZTbvX2zWX3wleVvmYyt0rvK96c9t2Q72ww/tTbhZqPUn9n80LjoppP18/snN6VVOGw8dsXElz9a14bMulr/bJVmyavrLnv'
        b'kbDxr453v75yYMuY45GuY1f5lLt6H0hvcrn39bkFcyq+UHWMql7wp+MvKn6ekrzyStyIkJDlF1/75HLj5/Pe3Kp5Tuv1+Yrw2R+1Nt2/96x04r2ES8kJ/6i99rnZ58aF'
        b'1rKn78hevzO2fu2mz5x+utP6Ftc5Um34Yvmff7leGON8oKpzUtLcdxpTh8OOv+/dJjmx9LjT383zjn1st+iN2R+cD/+09dmRnx2b9n7m6qXH2l97bePYv+ncZxq/2H8s'
        b'1mNqyFc7Tzd9f8Ayq+PjS3Pssg0f/TH39dtTA9+4Hen1SfjWLxbaVx49oXvts80HX5lb+sG6vKU/5p3wEJ4Z+uLbO/jUNQ1//cRbaW2m7jGIKAzxM7On+cQQ/4VlPsRV'
        b'QzPx1XFQxxpg7lDo8vaL8PFS+pFqLOI4N4V0sN26ZCxnx0VQ7KAecB44CK7AJSXkm6mW+cLN9d5+xEU2rMciMrgc9gu+s1aaKcA8QtepfDytNeFYquKJM2gWtiyeaaaY'
        b'nAu7Z6kiolebvaKtOLlUsMZiK7OCTlaPF0fTQx4yGBYRn1sG50dLuCEzJFiLrbCf9dbaY6cq1hdPuRFMb+LnQgtcVlo/fGz1pIdS9uT6vqMuZ/Goy2xUG0xq8a6FnXht'
        b'ooHzPAfempfzLrydYM3b8Q4C+SaxIWXOvANPjzeteRv240I+TuT/3g/5LjiI3wUbKzlPe9vwroKzYC2QQJ18pIKUjOHEu5IaOfmMIKPT7w680a6XQqWk264/Yf1O2J68'
        b'NiVvtO9dHRtqPtd71nbbpf9ZmxcFxWFoXN1z1uavjPQhUdw+75goP1Ek3nLuKThvBRWwx0HJM0vsjiegRBXhQ4BSHUECHGIFa/EktA3YvND52V5jAcc2L/TyhXv0+iXV'
        b'/sFmRnjiZkbCNjPS7zLIoDaKfv8WU7mZFOqBF2Lslm1LllYRvSxkcoAi08i+BPkN6Drglwizwqg1W4wGOpZeZzLTIZLVhg0KdUpKpsVgVpjMarM2Q2swmxTZ6bqUdIXa'
        b'qCV9soxaEynUagYMpzYpLCaLWq/Q6JjQ1Ead1uSnmKs3ZSrUer1i6cLFcxWpOq1eY2LjaDcTCaeQUWgb/YCh2Dm52Col07BJaySt6D2gxaBLydRoCV1GnSHN9Ctrm9tH'
        b'xRZFOiGNXkCmZur1mdmkJx3AkkKWrg198hC+hIcarTHRqE3VGrWGFG1oz7wKz7mWVEJ7msnUU7dV+VDPR/sQeSQlxWQatElJCs952q2WtCd2piKgy+ybbx4p0Wt15q3q'
        b'dP3DrXtk1ddYlWkwZxosGRla48NtSWmy1th/HSZKyOMbJ6v1arKCxMwsrSGUsZN0MKSqCeNNar0mc2D7HmIyRFoWaFN0GQQKZKWUUY9rmmIxUg5t6aNmJZ5ON1oMj21N'
        b'L1hC2ZOMaUlJJ81M5DdLxpOoTtFnmrS9ZC80aP4PkJycmblBq+mheQBeVhB9MGsNbA2KNG0yGc38v3sthkzzv7GUTZnGNGJfjBv+l67GZMlITDFqNTqz6XFrWUr1RvGU'
        b'xWxKSTfqUsmyFP6i1VVkGvRb/kfX1GMEdAampdRQKHqWpjU8blns4upXVjVPq1ebzKz7/41F9Q8XQh+4s/6+6IG9y8o0mR8eoAcZWlOKUZdFuzzJclNZa3XJT6CYei6z'
        b'uhdcK4nnIlPp9U9AWM+kfXAcONeTofkf5rtRS7woUbpQBbEypGUc3kjZkCxO8Lj21BaRxSdu0PYTVS9BhAV6vGEyafW/1tVMHPwTmNgzDm3xeGIf8bgqi0GjNTzeY/ZM'
        b'S3zkY3z1wIlJm18bI23TQL/7FJU2nk41m4ilSiVBDK1+XMcsIxEAsXnqx8+7uKdaa/CNMfo9ifoBcz9C9+P9fw8QHooBBnR+Yjwg9tWRqR/fMWLe3Jgnwy4x06hL0xko'
        b'pB61IbE9dckMkESBFYuM2gxN9hN1vf/I/wagxeb/QWOSribe5rEm7yltMt4gav0Ym/A/QBhVA6Zn1M4NoGsZqfl1ZTOoM7R91q4nLlZ4xpDix+LUYsxicdEjPVZojdla'
        b'g4aq5dZsbcqGx/U2abPUof0DazJAv6j+MT0SDIa1oYrlhg2GzGxDX9St6b8PUGs0pCBbZ06nQbrOSKNUrVGXotBpfi3CDyXbV3UGNZuEpmXpD6UHDuwY2rPPCSX7gsd5'
        b'hoGtH9we0Z2cK/fw7dFK8boxyIVeCx0Yb8Ml+SQmKMRLl4+20rPGA8mysCS7HxRunHhyewGv4VloF7ixcJubwc3Q4kkxLzCIXtGEucgVST5vWE8UW2MlHB3We1kClZkp'
        b'yXCWXVfhLtiHt7yVkb0bVahc0bNXHeMhGzEGmpR2FpokNHP+KizxjyQDdUb4QrF/ZLTKNxJLVTEyLhBL5d5Q5GmhmVJwMw1bvCOjV8H1Bw2coU4CrXF4jN087MBdmKui'
        b'FydnNw64O1kDBey8dgaWbfG3Uz18SXIVy8Wz7gYFdmCJN5aGaqIjfQXOGrsEKLYNZHRqQrCeDh6B+1RkF45l0Ik3/cOxVMJ5OEuxOhOusYVvgTNws19Del9XhBdW02uy'
        b'8d6ymaHbLRPYyeGSnbQVXNzyoCE90imLieY5JdyQQc2M4WziWGiAigEz04TAM9ASQVqOT5KF2c1m+TjhWjzn7eeJF7CUDOYXGY1FPko5NxJrpXAK92UxLm7Vw0FvP9Yi'
        b'IjoiHItpk2FDpQF4C3PZMEq4BXn95VY4rZ/c1j8lHtWfxUvS4CB6D1XFbcdmTaxaFNINuBpIhASH5A8JKRYOifAqnTE6OEgm3jhdwqr0HDgvHgFXQhXswnIrzh47uAAu'
        b'AI/AGSYXI5Z40PUnjBogVWW4mIhzdo6BULnnYbHOhQbx9PbGMqiaBHXB0JYl5/goAnC4IN5Dw344mknKOfHeLg+qN4RCPRsVW8dRPhMsLIeufmAIgJusqwV2r4HTcC04'
        b'OEvC8SoOWqAAWtkKd2zE43OhJjgYW2UcH8dBR9IEcen1kLdFMTE42Ei6xHJw0b438eV2sN86uE16tJEeKzjohMPYxfokYRe2BgfTe7aTHOwO3oCH49kd5TYsnhUcTPl4'
        b'ihtu0su1TEc/NrpyPpzTMkGRNOrd4bM5ixMpnBKPDSaeU1tzC7mFsFfMAPCycuIUXOEyLisp6k8B0zilhKkIHME2N3q3Vuo6TGSmNVYLcNh3s8iWGmzBEyo/X4+JXlS8'
        b'cEHKOa6Q6OFWChPiDCgfoYrwkfgQGUmlPByH09jILm2xJhgPD0TxCSKvPv3BU8GsoQq68Noj+lMKl3sVCPNDLRNJQz+8BleZupdPepIKrU1kOhk8J+4RBboa3qs/0ISV'
        b'ooCKU/BkcLB4wYtlqvQlWMaYNcFM81w3D7EKSLJ7ebKUXsqMIcUbiJjqVBHQ6uAb40dUyVM8jpNwI6FACg38AvE65cBG7KD3lbpEpW+ElBtkJRDg7V0vJqeVk9k7CMsI'
        b'4wt6mYZttkwYkqfWMVEo8UJ/WYRjg4j8BriQ4R3pSxhWpfL1iqHJ1o5pEu18ompjmeHID1FhsUmgPOm5JSfMofexI6OkcGjlMMZHbIJzeEglsq73Mj0ETvXdp2MFHhHv'
        b'dstd8QhRbxVZ9kD19k0XrVq+AvOYTHLxJJbA/v7m3CtFBs3YFs1ug/RSbFf5q6zwer/sgzRfC82Md8JWrKRX9IuJPe69pe+5og+LZ4YGjy2xZubzFjQMsAp4Bk+J3DmW'
        b'vQ4qseFhu2AFbaK13+OjYnfNNcTj9dw3Qy2cklqUpDYwgmCL8n4IYQbpDEVI/i+OoofuKsroIKiSE/u5h40Viqdn74ASFe4P94mM9ZVztioB6/BIhKg0N63wsmSh98P3'
        b'4Scwj7FiuxsxvvSmHfOCey7bT/pBuYiPBnepB97wHpBpAV0RDH/EB1126JcRQkx/y4OskEnuUNdzVa8k4o3wCVA8wNetbSILzrjiBYpM2AU3+7CZ7MounVZgrYetwGXj'
        b'CRJHLMUTsFtczVF6zUpg5421/VEngyNMiXzw4EhbmgKMTZzLZiKBLjgupi6c2QEdNM12PpRzvpyvHo6yAbXQBhcYr03m/jDn4SJTvvYYmrzy90D7pCSf369fyFkmMSrw'
        b'OrRR0BYQjDwe3zxRa8rfnVgeieVYZUVoKOOgFYoS6WzMufoTH3SIAfa89LF4dQtgTJyA10dDe4CE+hvOFY9mEti0W1aSmhS44m8iQMLSiCWLoS1gaRwWErwu8fTz9SQi'
        b'8+pJWFhKRE/U/gwW+qwIpwJjcFgS7kNridlQLV+MpVIObm8bDKVarGW+eDoW7ewv39MufeIlSnmCkTbSaVk6MbTtk6l7W0I8EVHoGlbjg4Uh2LiBVvHME10IwAoLDdbG'
        b'+ZmwHAoj8CBWYgUUbiKjte6AUiiGlqlwQQZtyXHmZLg8hSeCka9KgRPEPzBj1qmHQjyAt1W9SiVPFLxUWUySM6dgEfEN9FZ8gHfAG26ic7niYmKC9hjfX9BwQs5WC7eh'
        b'Gm56+62Pf1wEYwxgip+Ix6H0QQSDnev6Qhj3iSLeSfw1ZQ7Na9lI/GwkWXUUtrCaKXh6SPBkOQtaSEjUoMViEHmIZ2zhdhheD568iXAqjIOmHKzuSROBfSqbDMJDbOWY'
        b'cyZohXPMb28YB4e1cJPUBZKqRSSIIN7xqIVe5MAeotN5tliKJUR6Jf5YthRb7eHS5MDF4b1gifNdEReevuYhBBAUHrfBmqCJotLcgnOwF5rlxDNrue3c9gVqRvD8RZPw'
        b'RCI0T4VLAie40kTo6jAxFakOarTQLONIuMrt5HYGJ1hoYjpcc8B6E3u/IM4z3McLbnoxlVk5YPKVvlZw2GWsZQbtcdJ/kW1MNJb6ruhBNBatDI9cjqc2hy8TFwNNi7Ew'
        b'2tcvJipWRviOrTaQD/WYL3rTY3AKimmiPHbFsHcxbtkzti3DTqwn8GuR0TwoztkfmhdAg1IQbVL92CEEQ/F4ZgCE/N2YA8LdUDaWQWjiU/0hRC9VRXtZAU2hNAOhk/jV'
        b'6ywL4Qo/OcRWvEWr9YYrrPf6BU826kSBrogJC9fh8BwTdmaNgnZHORmpiJ8IRemMzBFD8RDk73zI4i8kPcexvQrpe5FEBs14/LGhwZpglg/XkyYSD1U52LK8f4TaIcbZ'
        b'UDZk1IMAFdt2bkjVKOWsz0qsh7pQuNAXgOJhuRjVHiBzncbctf0i0GRxosBR0ASnM/oiULxM4l0G8z3Ej17WBvSLQUmsVyMScUnt2BuCyqBpAxzZLE50MhhLemNQOI9V'
        b'ejJtZW/qS74rHlwJN/voyyJ+YCjzK5d88cymftQZoJr0opiZTkg6a41n+yiMC+5R6nFEES7L+9E3bIxSTNcbjjfxJAlwt5MtKIlwR2WyoSZHQVuvH8L9s6HSFa6zDBtd'
        b'DN31Lt4qDUvSL538FBUCXc36kXie+MHafoZUhsUicy4GkvDsCub3s6RYbVBKGWl+0LkYbkzsMzfEQu0WGXQdb0T0GhyshgotieyPM+pUUBOIJX599gaaY8S5KtbiARub'
        b'AfZmNxYoezJn92ZtJmHfrX4mB3K3kBWwTRnZQWVTfSP4OUAVbu14sVNrGLF2D/Rt8yJojobbYrbRbCnhhVuATViS3bwhXpzOyl0tNdH76QND/2BZllAyaqHLbMunn704'
        b'sXzCl5rkPwcW1bz028+KT56S7xsxrfY75zE2I62N4Ukj5GdWVg49F6bfs2L3t453rAZ77Pgq0HHLV+qvh30Y8dOgn3Nn/vjap+9antnTeP3Wj+fuH116b/uZDcENxTsD'
        b'rvxuSPnKzVO8M2vS//lW95qTE69d+ihjdEhCc2TVxTe634zc8tnny5bveaXV/dC0lw0X/vBc0pTayCmNP9neaVUnfGr/wTiPf/7mt6OGXvvpnaZvzoSaij8YvDzy4Kkm'
        b'S+Ri+PaXe1M3tr36Q2voDPuRSv3n16T32gftGpn7wjOz7tapiq/+9NyEr95u/vPeZ+t+3vPV2uo/+hwODiut+1dpcPPCt89+c6BVov5Fum3hneMbPv94zKs/bHU5GTfu'
        b'/ZT8C5O/KizY1TIk6aVTud6/fS5739tZ0S/nKFd4FLwx7em1Qw2qq0Pu1sl+iK9/5l+ebw+56/qM767gj3b8pa6icMXTsyd8vsQwy8s9293jUFNeiK3jnJumPxfU7ntq'
        b'cqlXvE+ZZYU+u33jttoxPtcqYmMKC2bPj1k6O/+7yuH/tAvUPv/Mp/PytslDXoLpNq4r35z6Y/OUV+a6f981M/7D78Z+f7bwhR+2Zxq6tuesfPfj18e5vvfebNvG27f/'
        b'+samZ//wl4/n+u8IeS3z2xu3YuqvvRN6/1L9v3bHLm6RvdE8T582Mc5/XeU/G7av+PiFliu6F++dsJW4d39dEFA3bEdY0R+TRkye/k9JyG1FSKJpxJvTwrynfP23l33G'
        b'qN5r2jQnZ88PspCq57tG3Ju9qCH6Hwnv1E78KWjzF45vvD66rrFwqM2wPT/PvcH75hX9o+GE986GV/9Q8v4/hr3y9O9vrU+Uhea9Fvubn995c9DdWNlfX5YXfhE9bIZJ'
        b'lf31b9edGrY8Zdpb+4+eGJcxfOvUD654TdA/m3nFZ5PzsxPit6T9de/Tw9AttObiMxafMt+VHu9e2vbLvrv+5+HeS3mV19bs2Bt55lD0Owu0yiX183e9setvuauGddb+'
        b'ANu775ncLG+9sLP1ZsK98/fv2Le+seLv0965+kHZdtPb9m8PXjbivROHBuu+KZndtd+v/dvv5h3Eicot93/OOZh/59aJIz//lLv69L0ZDU8/d33GiKGrPlQ5/83m/oFv'
        b'tv2pqeSn2dMT3h3ypcR87th7ec+VV69d5HDypdqf1E+Xn3j6hcEnjd9PCZo85sOIkmsnv3F4ffW/7hz43T/+nvTuxymesz689+W4nyvMpW0JvwjL6rTfWDsrHcSMm0N4'
        b'cQLL4GEZN0UOc4hzIg5mGHRKw+GstZgDtB8LZnh7+ZGovEBJ3AvHDVolQIPnePZSYfo6uNWbQVRN7PqDLKJ1sGereSQzP0Uk8L0J13om6skTInvjalZP3HgzHFcRt1W/'
        b'tF+2EJyGY2KSUjt0zI9YjiUPZzHB3kFmD+rZsBYavcN9HD37Mod604YasYWlKq1dtdw7JtoBK30icT9NTu0SsvFUIEspsnJaj1d2qIh39ifRizxb8PPLZDPDrhxbFQ0M'
        b'LmHVgwQpxwBJWjacY6OmYZ2B0Nk5IEBdtcLcE8wdcIOq2d5+ItPkcF4IlqUzlm7CMhu8FjfwRTw8pktgLE2112I7EQSJDrJ8Yc/0nvc0Z0ol0KhQDvl3c53+kw+l/X99'
        b'nEfeGswwh0wOYDlUPjQpKIeLt+alPR8Hli9FP1Je4O14Z4F+s+NtBIF/3EfMu6Lt3QSaQUVbutF8K8GG7/8RR3AQez1hLPFjLTjwCl4u0HcZnXg3iRPvwOaQ8u6kvwvN'
        b'yRIUPblc9G1HMptgJ9gxClg2F5uJ/AiUbppKNZb8Lmf5XYwO0ksu2LDsMBt+FOnvSupHkBGlZLV9lDsJYh4Z/UZfgaQrMDoSfsX0pn5J6aF+v5Sv/7qslLzRqVdabK5D'
        b'VEq0iMvlvhr/yIuYrVDr15MchmW+dJNBj/H5EVkS7JqJ5we8BUtFHUaHo3sFLf2jCdxqQcOvlmgE8XWUbid2NcHStowLjcZM448e4mUFg42xJwtLq1GoDQotrfeLUUq7'
        b'rRMT6e1OYmK3TWKi+NcRyHe7xMSNFrW+p8YqMVGTmZKYKGKx78HWSSO5MkIdS+uzFlgczWMuXLF1wCtm20F0fb7Gnhek/fG4HNqnyEyhSn6R7gis5k0jSN8/ZY+dVdYV'
        b'g2EuC9NmbkyepEk82rp3x3vZ8+Y+Z7XY6ZrLU42FFcLbi/+YpApe9L7jN5f28fUH6z6uy/7uy23H333r+WXRYyqfv7R1dGrO0brW1f/65OWLE6sCXx2U8dLm8T/vMKgO'
        b'OErzr+9btenV9+Jv7htbNOwFx394TlyrbEvb/fwzZdpFx39zevpPtQdcOy42X3P3Kq5w9l/+9v0b388vCDr8m1jTsqYlZ+aWu2aESs2fBr4w6m8+rc8776hcpT485fU3'
        b'k8p9O99UV836PuRuVnfshKdGmUCZ9uqa++lNo2sTXr/8x4+O2tZ+VrNXWdOpfPPDF/yb8r+o+nbfd8s+3xl5r6O59lpDXuuLQ98oqnrnG7+oD9ZloWKw3dihzfGNwteK'
        b'n+5lzl27Yniji1LKzCpUjvPAkizIjyJh53QSF+OZKWZ65Ab7fKX0PfSed9DJpvZq73voeHWQeRyLc/fE2nqRHW0nXPSmFv3B6+oe0C7Fi3hsMTP92YtwtwlawqEKz8b4'
        b'Ptj4DMYDEmhNlhNwM4w7/zeaSznbXT35wcwgQaw+U61JTGQ2kL6Jw7lSmzSZ2B2a60lzQJ2snawGWDBZj3WSuMSSljncDjveOKwXyER5BILuPlMw+L9nebzR7YHa0Mlp'
        b'kC9mjn7u1984UMG6boQqKKEHY1gUC9fgfBQUQZkV5zBcMnrwSN20jtWCSUPa1aW2jX420GF3mNPeV3JSs+3NyQ1779bfgN/s9hndsOLQ9s9bptz4bOP9/Pxzs7du6Hzt'
        b'9uvbfwjJ/+Wvja3hU/wbPr16v2nCnoNK87dHh1+9u6Zr46TAoK832x88pV/b/k7d/SseZYvdfM6+r7RiLtwIp5PY++KxbONtxdlOxwZoE/Cs5wLmbOUrkmg68SXaJNZX'
        b'4Ab74iG8IYF6KMcShjF/ssu6KC6LgDYOz0RDKVuVs8R9CbaZxVcmoALqVRHRNKfZA8toWnNEJPP1M0M2q/r9hRJbLJ2mFPBAhhcLfoYNCxjw90ti8Sr78yXlcN5MrWY6'
        b'FmOzd6SMbmtHmbHaNK4X0+7/zXHAfxYw0l/VAp1BZ+7RAmojOHtrXvSL1hKfHI5+OOPwBxhXdEv0WkO3lGbvdsvMliy9tltKr6mJI9SlkCfNwOyWmMzGblnyFrPW1C2l'
        b'STzdEp3B3C1jf6qgW2ZUG9JIb50hy2LulqSkG7slmUZNtzxVpzdryS8Z6qxuyVZdVrdMbUrR6bol6drNpAkZ3kZn0hlMZpq21y3PsiTrdSndVuqUFG2W2dRtxyYMEtME'
        b'uu3FOEdnypw+NSCw29aUrks1JzKX1W1vMaSkq3XEjSVqN6d0D0pMNBG3lkWclNxisJi0mj4tFpftbqQWwhhIHz70QW9YjPQU3kgPVI30UNpIFc5Irw+M9CbLSM/djPSK'
        b'xUjtp9GfPug5qJGC3EhPpIz0D6YYKaKNnvRBXyE00lcejfQ2xUhfXjQq6IPpDQWncQp9TKMP7wdGgEpn0AMj8I9F/YwAq/vRuvcPgXQ7JSb2fO+xfj+OSB34J44Uhkyz'
        b'gtZpNTFKayNVJeq51Xo9sW0MB/SwoduGCMFoNtFMiG65PjNFrSf8j7MYzLoMLQsbjCG9zHvI1XdbzxQDhNn0NxaISAWinCLWnFyofeX/H/EAvTc='
    ))))
