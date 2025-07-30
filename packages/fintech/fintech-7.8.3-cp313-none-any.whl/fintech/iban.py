
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
IBAN module of the Python Fintech package.

This module defines functions to check and create IBANs.
"""

__all__ = ['check_iban', 'create_iban', 'check_bic', 'get_bic', 'parse_iban', 'get_bankname']

def check_iban(iban, bic=None, country=None, sepa=False):
    """
    Checks an IBAN for validity.

    If the *kontocheck* package is available, for German IBANs the
    bank code and the checksum of the account number are checked as
    well.

    :param iban: The IBAN to be checked.
    :param bic: If given, IBAN and BIC are checked in the
        context of each other.
    :param country: If given, the IBAN is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param sepa: If *sepa* evaluates to ``True``, the IBAN is
        checked to be valid in the Single Euro Payments Area.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def create_iban(bankcode, account, bic=False):
    """
    Creates an IBAN from a German bank code and account number.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.

    :param bankcode: The German bank code.
    :param account: The account number.
    :param bic: Flag if the corresponding BIC should be returned as well.
    :returns: Either the IBAN or a 2-tuple in the form of (IBAN, BIC).
    """
    ...


def check_bic(bic, country=None, scl=False):
    """
    Checks a BIC for validity.

    :param bic: The BIC to be checked.
    :param country: If given, the BIC is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param scl: If set to ``True``, the BIC is checked for occurrence
        in the SEPA Clearing Directory, published by the German Central
        Bank. If set to a value of *SCT*, *SDD*, *COR1*, or *B2B*, *SCC*,
        the BIC is also checked to be valid for this payment order type.
        The *kontocheck* package is required for this option.
        Otherwise a *RuntimeError* is raised.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def get_bic(iban):
    """
    Returns the corresponding BIC for a given German IBAN.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...


def parse_iban(iban):
    """
    Splits a given IBAN into its fragments.

    Returns a 4-tuple in the form of
    (COUNTRY, CHECKSUM, BANK_CODE, ACCOUNT_NUMBER)
    """
    ...


def get_bankname(iban_or_bic):
    """
    Returns the bank name of a given German IBAN or European BIC.
    In the latter case the bank name is read from the SEPA Clearing
    Directory published by the German Central Bank.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzNfAlclEe2b/VKQ7Pvu42C0qyyui+IIsiu4C7QQCOtyNKLikbjgpFNQHEBFwRxwQVFccE9qcpkJrmZBEISCJPJZHlzM/Myk8HEO2YycyfvVFU3gpqZyXvz3u/1L/no'
        b'89X3nTpVdZb/OVXtF2jUR2T8++1muBxCS5AWhSKtYInAHWmFq0WLzdFznyXCKAH/5m+8o5LDXdFqyXgUZbwzA/7Ph3djhaul49ESsekNtWC12Xi0eoSDAq2VmFcopd8X'
        b'WCTMi0lRbCjJNxSpFSUFCn2hWpFWri8sKVbEaYr16rxCRakqb71qrTrEwiKjUKMzPZuvLtAUq3WKAkNxnl5TUqxT6EsUeYXqvPUKVXG+Ik+rVunVCspdF2KR5zlqIF7w'
        b'v5yO/R24ZKEsQZYwS5QlzpJkSbPMsmRZ5lkWWfIsyyyrLOssmyzbLLss+yyHLMcspyznLJcs1yy3LPcsjyzPQyjTI9Ml0z5TlmmWaZUpzrTJtMh0yLTMNM90ykSZokzb'
        b'TNdMx0xJpnWmc6Y80y1TminMFGS6Z3pm2kV60ZleJyv2yvB4OnvF3t4o0+spnen99LsCxXjFePsinxfcLUCzRONQgQBmVJiSN3rNrOB/BzpUMVvmtUhpnlIkg+8NJSIk'
        b'RpWzLFCO5TgzK2SYCDdJTQppIjWkyhYfS01KJ5VkX6qS7EvITAuWokkLxOQhbsCn2fvZ8VJkiYYzzBQ5lkM2ImRYQ98/FZtGus3xvRCr9HjgU5uQGY87/Ull0KJksn+J'
        b'jFTFZwLTOlIfSKpSSV18Mqlb6h+fROpSklIz/aGhMhS6S49flOkfHJ8QJMAXxEiPq5yiyZFlhmjoAe8iJ/FFYD2WBzA9H05qQtPjgxJJLfSbRKoTJGgjrjdfjU8o8wSj'
        b'psTaNCVb4DLbKgumha2WGFZKCispg/WzgPWyhDW1zrSJtDaulCBDPGqlhLBSglErJRyzJoIYIVup5+6OrNTaZ1dK/txKnecrFT+PzjSybYheF7TCfAliN6Wr6PIh9Gps'
        b'YdGXUx34zXuJ5sgWocmfRmgtXab78Jue9hIEfxWt2wqK3vZahM6jIgu4/edVruLH9nPzJeizSd8Ib4Z5r8wUFFGjXxfeJOgyQ4ouu03hH2sjwx4jdnv31G9sDtoI/F/V'
        b'fCn4+/I125rQEDKE0DW/qCdHYUFg8v3988g1Uh0aH0yq8fkMf1j0+qCQhOBFyQJUbGM+i5xOV4YanOhLx1LJPp2lAJFX5iDShPBhciCLt1TgulSdVoKcV4A6IlxJjuOH'
        b'Bns65NnTdFozpN+OyD6Eq/G1OIMzfeEe7ojSkZvwrTMAkQaEa8l1B9YUijvwLR2uEyPycDUibQifMMM7DHSWY7QaaBAiK+iDnEK4ZUY2ewV34u51ujIJIgdxLSL10JGK'
        b'VDDJbPBOfx25KkUvk0pEDiHcsIJ0GxzpS6dIE+7UGSRopTsi+xGukRVzbmfw6TCdlRTBtLQjchLh5q34InsncZ2ZjnSLkUSDyBHghevwAYMLfafZDdfooHNEWnArIscR'
        b'PjoZn2NToBq3SicXoiRyCZFWeNLKk8/ZXjCKG7pNIkQ6YhA5jHBdup4LcEiD7+psEB1OB3unidwQshnYMFVMuq3ESBAJE4fwSRney/oINcM9cph/jT0sLTxfFMzFukSu'
        b'4F24BtYMt1kLZAhfhpU5zNqi8X29jlwT0Id2I3IA4XpyDV/lsp32L4FpEiF8MYDN9EFyYR6bgTUzdHLSJUFbyAVErsAS4AoVX9HDuIXs1G0SIjNyjLGrHkduMG7Ly3Cr'
        b'jtwSw5Tjy4g0I7wfbWYvueGWCTobIQiMG1k/R/F53MPEm7GYdJJumRDmCZ8BgRA+Bjf28mEdzcU90AgL3jMPkXNUjFbcZHBlLG+CtN16aOsmD1lv9aQTGml/PngPOU26'
        b'LaVoFTnDXjxB9tuzJnu8uxRaQLnr1sKKUJZX8AnW3WzSMA6YXRXDGp5DoBP4MK7B9/mwayw9wXnCLO4lFYhchnlOx4dYkytuAxnMQZA9tmyuTpF20CPKkbTk4JvQBhN8'
        b'XYZIF8LtVG/YbGnIWXCG3QYpylrItG8/qSzlfR1ZXA6rL0CO5Cx76RTpIPfYSwmCRSBhtwDl4Z0IlgYfm0WMAt4uJ5dpmxnCxxcwrWmZV8xX+eLMIFhMkP1EMRP9xDxy'
        b'nqnZfHxRJZcJUFgsAhsFg2jw4HI/xA9ItZxcMwNbAqW9QZe0NoFxm22jl2+Ewd7BzayXZlxhXP8UGE+znNwUowgwqqt00k/OY8Il4Go/aKCm5gdzBQoNmrCLr3E1uUD2'
        b'Q6MEtMOTddVG9s1mSui0YKFOL0CLyD0EVo1fAUPewW36Pm5fJdeJ0dIMNuNNc0zcakmVq9wCOrpEDsKcIHyWHCHHDe7QtoU8cMQ10aQB38C1MIBDTiJySpBKDkYbKP4g'
        b'VfgifohrNoI17sPVEpQRLS4U4J3kIMy9D33gUjC5ZGwP51yScL0EmeN9Qhd8CV9Sigzg4JGtSkVqtpE9AOJKUEl0AjNc/MCKHEvEZ3MhLuSi3K34GlsAfDQR307E9/Bh'
        b'KUAzlL8OVpPed5rnTkc+E1/iI8f38gx+cL90aQppJJX4YjQ+L1El433k9LpY3L4yGaZke6ROgg+JcB2fO+EKHRhHGegPqQKtBT2sNUyivo1c0Rh5kNMp4CgOwQgpFQmh'
        b'+5AYeZJ9YnN5AfdQu+JwpY5cF6Ao3M7cd10iqDZFmO7kahFng2+WrsEdlE08vjzCBd8Xi0gr2cn5HMFV4SyiXKbLQkNKOni0ADqrZ8kOlWlMx3At7hwl0CUu0AGxNJxU'
        b'c12+sRmfAwcsRC6gly2g6/isH4NHYKoHMkljPL4UvcgSnx/hEk5lAy7BItKT4cqY4Jp0fFKnFYPpgmbtRbhCTHYbAmnLBbKTnDGJc5lNMb63Tq4gNbhjqQPC97IXKczk'
        b'pAdXc0XcFbGaxkN7vI8HRCUMazJt2Elumo/wGREGXyH76J8LVCQYXm2wVlIGEfoak8scV+LDNIySzhJjHD1bYAil4Y1cxUf44GBo+0S5XC7ySgF4lKOgBLgGdCCe9EjJ'
        b'DQtyjulQwIIA8Pt08uPA2cGg/RUGXwoOycE5I6xAMNxTShdOvBh5kG4R6SIV5ABjMHGdr85CiNbis2zJDqVCrJ9KvasHIArj0sPk7luJb9ExjV64jmTK/lKyNDcZleEr'
        b'MnzbEVdwC90Zb6vD1RD1z9PofpKuYCveySaNHIab+6hsl6NNKyjCB0gVOYRhpDdi8Dl8FIWRkxIIyLvJK9zxHcM1SgYxcNsGI8So28h0VB1CHhjXIArG2flURy9wHW0U'
        b'AUBp0DMLDXTerrMWIkEmIkdBP18ibUw/Z5Cb4KCM9nJqwxh7Oc/Vc6/YDGLIZTY8O3yG3GOoBrx2PYc1gdDGhncBX4c1H1GKfSOzxoQCcL+TG0/kVglunryN6YQv2Slk'
        b'YAi6aOdoaPZ8phORywBnm5zBUw27yPhGRsq43oeTegluJXesmb4qwMO1UwSFK7dwALU1jg1zIthe+8iiVkq4QZtWk4+zUywjO+NY9CWnROQkw1u4kUYiCrggaOxgguHO'
        b'qKc2NCIZsL3Eh8yseh2+FAxeVreCQztSP4c8AIag+zeyWTQ/iNs8WV8QGM+TKgrgwMRPcAhHTuDdhiD63nEbkamrC7QreLycqgt+RYFPUYu9Tc4mk/tm4XFBrCMX0oV3'
        b'MtR3C3dx1IcbbTmvalIxZax7pTa2e6V/dDDMG5sFHWAxUus6kYfJHYAGHjCkaB5tRIq7wPoo8pa5BplYXXzO/NkMgAAHgvFhiW4JvsSWWksuynQ0gK+KR+QEhd0XAHYy'
        b'r3dzhjPFlhAoOFBsxg/jmcz4Ar5GTpp66hyJCbEK0ohbM5nTSiUtZiFR5DJn1Upa/Ch8Wz6DozcI3w8MwZTVNTfNUxczRnBm51TkvfoQfFeyzj+NaZOKNGl1m2gmt4+p'
        b'wL4J+BgzPHJAs9nI6gC5yRdmTIyZJCJ388hN5mZmW2kZalyv5JjRAixPyfB5GbzNuezz4YrErbeT8vAgN0XgFa+RGrauAgeyF9hAiDm1nOHyg+QqLAUdcqAn3s3QZxWF'
        b'LBR9ZuG7bMhWiz2eMcenvWwBpMutsUwCaKV+Bp++HgA+V3U2AhRCbjG4elxTzkKz+wp8l7suddBTNqboIxKRKyX4FuOROg8fYpAXV04xIt4HW/mQL+HD1iMSLQJ1ec4I'
        b'28HZnJ7BDaMbt8PcUnyMz+JdRoC8Z5ohiiGhRMDRLxgc3AFoDKQYX7NMjpmPOyeC5h2SgefU8Oh4Kl/PgfVVtRFXdy3iHbaSc/gqgEwABE7Ue7dSiFwnYfG3HBDGaWOH'
        b'yyHgjwTPWIUEReJWCT65CWAn7UGpngkQHNTpOiDfM3T8JyDkTOaJzP7tY5VwlMMl5/K4544gxyT4wEZ8nplhPnkFoCZF+ytxnRHt15EO5osm43oABWQP4EGjO9o34irY'
        b'HRHMgtW6KEG6xGyq+WwWCXILw1iGUDKfJwhObgwbZK8oTWRRDd59am1VQaNA2GK8z8xnJe7gPrJ6HoTmbgqiS/AVNtCjuAsQP52tGbZ4xzPxnHGpWWlnl4wi8A0IcfO8'
        b'2WwVTcD3SLe1GSC3FoZ223HrDKYuhbiCOm3KhewHcDxK6y5wE7kKakceruKrt5ccJ+2w9BBMXGmCc42i46tbOHrqAXM5Owaw4NNWRlzgiXeBvWrwAzbdE2ZR9S0D9d1N'
        b'HjBTq4eBVTCJDKrJplhZAajgOTPAe0XkDrlFurjTvwbo/z7wAm/caMZ8XoNKxsD2cnI/bTRIUZVRNkKKUW6B2YvlTBQF5HnVPGUju+2MKVtHOB/u8XBwbTRlA1jRyFM2'
        b'chcgDM86MMUDLGu7BUGApW2rAtl8T8aHwljORm4s5Dkb3judjW4arH2Ncb7Pk7bRLukyn+8umO9QvIevfzukFDtZhgdrU8VzvAwYOhNgLwUW3QYBBcDcpx8glxKY99SQ'
        b'+u3ck0CsauG6yiDR9afO5HoR4HA2hxdT8B1gBANpXM/wRuNkcpUZU3rk8ucRaKTRGZCzEEyYloSRoxLcMoO08ph2mVRApktuSNECWuEAa2omp72Yu9xeZjWGIR96B+On'
        b'DzNyWyaBKFhBLnJfcix1IaSytCrSzZaglVyWMGuSgOeuGBu3qK+gcSsKP2BxKy3JbBpM4kEu13XwxldYWjyZZkU0LcZHgwxhtK2WPAgf6zU6R03aNVP4isAPJaCsdyyY'
        b'bNZLAOt2W0mQnxXLVtsBXV5h/HBnwJwx7IR5VLxacpSKaAuRtSfaDldGCfCxuRYpTkYJt5KmAJ6c4wdJPDnHd0AXWEC8TSpsjSzvbhwF10x+XSkit+YY3SOpdvblmbzt'
        b'NJ7I4yMitgBmi1f9KOIzgooKXBFskJTi1umM14pZ2ZD6S2nZ5i7jdTwUkg0mUjM+9ZJRmatmjdbli1yXb4vAPhuceGknczqrIJA9a3gFAfS/ngOQZgjwzSbkCMr8YAx0'
        b'NKaUD8XWOWB6bHTnXsa75DJAjvsDWLp/Gp/ZzjJTO3IZ7IVL1OM42nlc4hJdFsF/ZVwdbkCIuUBrF774FV68AHW6zczUyx26fxbGMc0iLRlcs4LMpriBO3NkS+OP98r1'
        b'YuSwjvnoRlJdxHCJJ7nlyUogy3J5BWSeJ7s/C3fiG7TGsGYVrzBMTOaM2rK95BsB+D+0h+QG8iVyXchUfQY5AFZldItHAMc/b9HULz7Elc7caO6SjhXyjVLk6MGqfEfg'
        b'pROGcB6Am0nb86rpPZ+OEHevhOypYh1pX4m06yHngmeYj5gWSFpYzaYa7+c1G7CmTl4gPjgOn36Rl7goscc3wCbqWMZ1ieYQJ3Q8mW/Hu/BNVuchO3x5oceuiEVbIdlD'
        b'w5rRqMegx6dp7+KUYNwo0ePrKj7a27hxPisO4X0BvDi02Jo7UEBD5BwvDXXgh8ba0INx3O914pP4vNya6mQkIvfoI2eS2CzJAVBcf9GYjL7hGmkweb42QCX43io2FcoJ'
        b'kCuMpBKjsYcvxFnmOSVlUYI0mVk0eZDMNC2cXFs6ZrhsUS9JculSHE9KRuEuEnAbV6W81HGBnDKhO3IaZvfiKD3gpQ58TSwOIieZORSGlZt4V2WNGUcnN6pqsQzfimbh'
        b'Ox7v9eNqsXLdGO/C7W+GiNz3BAdPo0IGuVP0vBMxufFpeK9pbhol+LgY71DK+HwfIN0SubUI5hkyxwc08WghzWwFY/Hl5XJyVYBU65gltoHStHGT2BGyGVpEaFsqIGcW'
        b'SZezhikQR0/KzYUoqoCt3TkFWCPr5greia/KDWKUQHM90NUjGfg+V5RWcsWDFv1IcyGv+m0Af82CaT0k261ynRmNEp1MT1p8IHVyZwpOaiFHrWFO8DK+g8h96nKaSTXT'
        b'lYypWmhrxJXGsh/uNIJDXMkqhXPwZTHuzsA1mWjZGik5GZWjFHPlPF7uQmqSFpFaEQrBZ0XkAUQD3LyQDW8SeTgukVQnQcfNUiTMEoRaLGHSQM/3hImkLlS6jOwLVNId'
        b'NEtbkRPZk8q92tVAciIwJTge5h83i+cKQJYmcj2PbiaZPnS/h21FbaS5k9S0Q3oIZQrY/pgwE7E9MlGmPNLcuDsmzpCO2h2TeKPMUbtlmZIx+2DiGAnbHXvu7sjuWIFS'
        b'qJopRMgilu7n6hSqYraRqygo0So2qoo0+Rp9eYiFRQLfLg5YX1KsL2FbvwGmzWKFBt7aqNIUqXKL1EHsxYVq7QYjIx19zyJXVbxekVeSr2YbxpQT46EzbDBtRKvy8koM'
        b'xXpFsWFDrlqrUGmNj6jzFSqdxSZ1URFIMb1UpVVtUGiA3XRFRiHfc6ab0bkjT4eYHsrV5E1XgNhrNRvVxUH8Sdr5vITYMdw1xUxCBXzyYHDqzXoqklqVV6gogQbtCEMm'
        b'n7Z8NFO9SQSYgn/MT0+3040cQhTJBp2eykznaElqcERYdLQiJiktPkYRbnwxXz3Sr05dqmKdBtBvAQo1LItBpVezXficnAytQZ2TM0YWzsMoD58dtpRG2RRLNMVri9SK'
        b'BQZtiSJNVb5BXazXKWK0ahX0qVXrDdpi3fQRzoqS4hFFCIK7caoiHbtNJ2eTRgeCjtldlaBnd1ftUuJYrBUmBOrIDvsyCeLVqkh8g+2bRmpdETizqTvzczz7xcmI5W0L'
        b'SybiGlp5PQG4B63wwh3s2VU2FgiM0lbkkmO5ddo8vvG6ONQaeSI09050TpDvTC1ivW0hzdt1pTPlQsSLLF74otKG+R7ZenxPF4i7R5ogKeaVels/sQ6f2LBJhPjeHj6+'
        b'lLmAfNKCL+smeNog/kbTAnKMeTg/3OJPutXkhJUY8c090o7PGjcEPXGnnJwi1Vo6YLrBhztm8ULzflLlIMdtIaW0I8hKjyxIYoO2JycK5akBZfQ2YOJjm3jZEMLjkfm4'
        b'JtgZ8li+H0jr/7QlHQLlXcgCj63SSRFLGA7YuBl3pA7hm7rppJ7uFvKdwimruVdugCBxjXRvgMyCdkR3ClVb2fjJ3uWB8gk2dK+QbxRaJzCBt6XDbOWTQ2xiblIMe9KJ'
        b'8crOx8eh+2v4ARvkMVo0O2+EAo3kqK8Od9ptMkOsnFZPri/hwz8YUqZLwbc3Cblg1dakXSliLwWTa6RWR+4JR9rwsc2sRYAP2QCO7nIa6YhcKGIypGeRHh2tVzztaB+5'
        b'wF3wrSjcAG24jpb1eFGPdOYrhYzl6vHBOvIQfPJIWzi5w1jakrPmOtIioHvDfF8Y78B1TNdmTjWjZwQKB31ykm7ap3NljfUk9RHl+PxkMR03yt3ip6l6P1iiU8DUZ/jZ'
        b'blt8dTGZbHnI4T9SVgoHqjr3eIvkeYe1+oIvQhbPUWy6j9/z9nj4Gv4h98bVr2oaN1cF3X/yjW/5qr8Ljq3tOX5f+F1GkbvkzfN3/9RX+p+P/jgFrW38Xe2GuSVeQ5Hl'
        b'1WcvfR0p/FCSmPOrnOqCL/q+/s3GucGT1qw9svnbL66/s2bbx2UPNlrGZX9l2PdZ3amk+Dhid+Uvfx74bdm1VZ6/f3fifzudWvCzixZ/L6xYVVe61u6W92fvLOyZYvdk'
        b'e9NX//n+Fxt1AbsPOzn+fLZzuuH+DxOPjW9dFFv7aFpz0Ff+V9zUH/3ypVcTB78z37htzsCTG6g87APHHxJm+uz8tiL0S4vMCnff2cqQD7uWeCfeOrZJNbN63f4LKwt/'
        b'/bF3zm9Xe34anP1azKHsH95ImOkV36A0e+zGMgmI0DsCg/3j6R5BsBBJ8VFh8FZ89fE4qmeQ8lQEhiQEBShDSH0QZAe3SBVCrgpxFjmFax/Tc0aQunTjjkRyHrelBuOq'
        b'VAjZUiRPF5K6UtL8mKrDuG3b6ZGbgGB83yJEAD3sEkbMwAcfswyqmjxYCgrGT7tsoqddEgD1120MDiDVoUKABfcl5Prs+McML5zF9eNJTXJQwlZ6yAYhaaTQOhG3Ph5P'
        b'G2uX2yfy0zKgd/VJiwoBXAGwcCIVItKDX8F3lPIhob9SSzXnJ1109OSKQrHD9BlymlmgLdmiLlYU8PNbITQyzh6yYL4/mxJaanBC+u5N0MXvdqA/p0mQo+ugi+egg8uR'
        b'6funN86snP+Jjf2gs9sRzX5N4/oG0ScOXq2+50LbQrt8B8ZP6Rs/ZVgodvIb9PAb8Aju8wjuyO/3iOjS3Sq/Wv6q/atL+qck9HskDE7wHxYhz0WCRzLkPqE1osNswG1y'
        b'n9vkQQ/FJy7eg94+rT6tMU2FDQs/sXEedPc5GdwcfCy0wYzKMGf/nNbIAQf/Pgf/QRfvYSSYlCb4Fglc0wSfjvMdltAvw1Lk7H4ke392a8aAU0CfUwA82Dsxut8lehAe'
        b'ESHXKZ86uT3T3rq+3yXM2Bz+qZvXyXHN4zpcBtzC+tzCqFQOLk0LO2b3e04D4rtP7JyafJu0rYIm/46QfvepdHqc3ZvCm2IaCisXDto4N2n6bSbRu45eTWv7HCcOOAb1'
        b'OQZ1ZPQ7hlcu+MSBzucnNm6DLj4DLkF9LrTBJbzXNvxTR9cmuyb7hvimTfBSh2OHqkvQ4dbnGN4g+MjFv8Ou3yWwQ9/nEtFrG/Hd8AIB8pw44BHV5xEF43fy+4gKD3+/'
        b'19G1f83GL84evWFvG+cnesNXAFetGc1zLIfEdJ2HRIB3hsyMCGNITKHCkFl2ttZQnJ09JM/OzitSq4oNpXDnH6sY+DaUAx+TmmlpXGBaxC6H6TPT4PK3HeiJRiwQTPwv'
        b'BJfPrF1q1u+QDwslAseP5PY10z4T21QkD8psPpI5fPdIgiS2Jup7HfWix6VB6JJ8igjcPt2uTyOdmYmAvumpuLrUBLKDVEuQdaloahY5wQH6ri2FiUkpG4IBbQPWFiD5'
        b'SiG5PGGVcVdtbxoF6BDr6jhA15OWPNOxS/oRmzDJOgqzhRxmM5CNAGJLI8VGaC3KGAWUi8UArUWjoLV4DIgWxYgZtH7u7uiDZ6rNAgqt2QHJUdhaW7JBoTKh5LHYeCwO'
        b'Zgcxfxx2a9VlBo2Wg7xStRag9waONE0nNUMsUk0wDToMWAycNRvUC7TaEm0AY6CClvynyJrKQkXh6PpZAUcgqVFI/tSzEo/G33FFqrUKDUf4eSVarVpXWlKcD/CTwXBd'
        b'YYmhKJ/CU446GdZXcKz/FIgu0NAhPMW3kF+oFOHBekMpYFgjomUjB5jtT58IosyV/xSWSlIMs+F7Eb6Ke54ecyzE956edKxKClgUhC9kwNeaUHpIsyo1KSFZgPBFXCWf'
        b'BqjgYoZm2qS5Al0KMIpe+Hl3XvNbtvjCa0ig/NjSsq82zTp2crvy4Im3XLH762/vEMxrim3a1ZzUFn4mydJSUusTNLnffufndrUTkwIs2ywDLI+7obev93wiUz/2Vgof'
        b'09K5z0ZfeQBoPKnaSnaR2mSDMRyNw91iWkH1YuExea59YsgiCEd4H6nHt3EPT2Xd8XVxcT7eq5T+E6OXjsQVZu5Dcn6kl0eQcaYIQk8c0wgSZ4YcvT92Ht87YV6/c2yv'
        b'beyg24QBt9A+t9AuWc+kVyP73eKrFvGo4uLRsKXX1gf8fGXit3QZuNMyG5KZNG3IzKg/Wgq8tBQKaN3HSmfGXRIVkHujcabLgMkb/RW80XqpQOAL8UPg+1O90WHpRHRW'
        b'HiZi+kBO4pOAYp+tI5wHPF0BQLcWX5uFW4NEaxIjcV0Z7sRnAUygXHLAipzA5605Xj9copJvtF6fA3Ad8ghyEd/HuxnAXoUPZcs3liUJaEslQEswSQZUOwTkrI7ctAkX'
        b'A4qPFZIDAmdcG8/gstA8XReuLcV3hUhQgvAtfBfzUk0J6SKH5Rs3Lp0jBW57EDlK6maCR2Ugfx+un8CqFpdwA3eKpMPWQKd3aUISLVq4yUcXLSCL4GcvATvfwzsDwQ8n'
        b'+wqQENcJYlUvj3GmMpMladHTmgU4U0mmqWphDk7VIlI24lSl/0anSusVqtH1CuZJnqlWjHZB1EXRR15cJfiRpJ6+8H81p88rYl3q1Prns/hnOqdjK8nLM4D3LM7jQpjy'
        b'+AVpMYpYCOxa6lHnQyTI05doIUsvNeQWaXSF8HJuOXvS6MljIdPXqooYj3lggCGjZFDRCTSwHwYELInNCAiCP/Pn0z+xqYvD4C+IETAvfB5riI0NCGJcRsmrKtKVvLDq'
        b'QAfA5qqU1xqAUz516OWlMCGUyb8U4ka4lJTyyEbf/Nei2/95UWMEQIxED5uUOMMsIBI24tsvOiTPQoce0sYfjR7nSCfLKH/Q0fJHw2xZTs7Ml80m8JLGshwH5Iu+W2+B'
        b'clbfdyvjaeZ0as01CAWV0pIIqcANzNbVZPcqXIMrwZorwV04CMzJPXKHsUlfSSsjU2eZTc4JSp+/DEHmyw4wXk1fEkGLsDNRGAojd8h1drs0Ap+PECPIl+tROAonVeMZ'
        b'k8+ibMEKC9eLSnOK0lPcR5i0pJA24BLjTJngSnyb1xCu4lP0UIIZEkPmnIbS8l0Yl3edaeVm6npr2xzLiOl+KEPzcVOYQNcPTQ/M67ftT7beNdl2T/aq1ozIEMNvs3M/'
        b'lwzmPLb9o2vy8v3+l/VfJdy7cj0td+7x5MYpv9l6QlP/yOP1TR1fvbVjxoTLblsORX+5u/HxS2VS/6JfmzfI3/VoiVZOudnh7/XniPPqltYc0QHHc/eWDs24+ar5yv8u'
        b'TTxh+e7vG2fcPfvXsFl/mbJwb1109qwJ1xKj3n3rm4ldXzX1KiMu/k4zZ2C+6PbH8V/WP1m6JCR9mjr/0Kmz8/8q1S30jZMqHv1p07Ujm37z8/X/Y/+fEh0/ePdS16Xp'
        b'fta5VQfOfyP6sGl8jsV9pewx9aZp5PgasiuRprWmlFYhY4HdKWYOBPbz41lsfz6w7w1+TLcCtuGaudQXQzpLc9pQeCSYPp5ohnCTcxhplSZAGvqYYmh1dqQ8kdQqRzil'
        b'mTvhvWIZOUXOMVlInZZUJKbidlIRDJ59oyBmErnCc+875LZdKNlNk+PQVCrodmEAaSctLGtOyyaNpIecZfmuKdlNc37sgeghx0bPRLIvkWflVfQMJd5pM1m01nK10vyn'
        b'5ba0FD6S2nIYYs7zWHDj2mATCPm9EYS8BCDEhWZk9k5HlPuVjYGVsQA4PnHx+dh9Yu+kuH73hb2OC4eFIjufQW//Ae+pfd5Texz6vWc1LHwkBfjSlNcaMeAwqc9h0qDH'
        b'+JMzmme06s6Vt5W3bx3wiOjziIDE8VMH7wEH3z4H39YlAw7KPgcldPaRjX1DRM3mpvCa7a0TWlVtEzti24N7RA8tb1u+mjkwNbFvaiIVCZ4Kq9rY5NZvM741r8OnraDL'
        b'vH/iNJYjOjdFNJW12jVNbd10blvbtvaX+z2ieTL+3WMv5DoeMj87n488FJD52fl8r7OD0V63iw1BJMQidoaITBfAlWMoOQdMdIWGRBBPXgSdfrSI8FyCF2y6fD0aUq0w'
        b'EwjGPQZINe6nQqqj0gB0QR4lUgr4+Y0LpFln2mFxdOUbLNb48JifC4042VzEszT2cyFxpHDkZ0Gif+PPggqVwi0tFot5ZPiRBKWA5RoMF4ze0/h/lZWNCUGi50KQNIVF'
        b'oPG4ix6/fXEIwof0/yCBqZJwsHia1OAGHS/Mu+lp1bWDXGSHFNbgO+RmYmowqU4mtUtIZZLQfgE+j/fgxuX4DG6G70qUZmsGIeMGuaCJ+9V4kS4NXpsh+o/uvKOQC3WY'
        b'cqGqxNHZkC3NhpLa9CGitBanJbObzAuE1VZ/KC0v8PVw3T01LFmm2nE+TfVpkhnSPTSPXztOKeGltZt5uMOYD1GfSa4rxrhNlPWYVeXV+Bq4XNLuN+J1p+FO5rCWpb7E'
        b'y4jkjr3JZ9Eq4jJ8kxURl+K9441uFB9YbmTO/Og63PqY7UHuSZ6diA/NeqbGGIcblcJRVkadlcmPma1V65kXizZ5sSSjF9suezaVelqVe6Y49rGzotdnSr/z1F7bqYMO'
        b'XgMOfn0Ofq35/Q6BvZaBWgUy5VYSLTt++qJEiubAo9KoaNPFFaxQFwlf/gIibZAJBPY/wdy/peZ+ACD+KXmw6J/aszgT/V+05y0WS0qLNHrdiNHyDTGwUgW9W6BVrWWb'
        b'XWDAJsNXKSJfWEqw8I9NzUzJWLwiSBEbvyA2cUlmcpACuCVmx6bOXxCkiIll7dkpmcnzFixW/nNbZSCofI0Z6poMa6PISVoSkYbYEfyUchpcSW0g/UFlVVJ6PKmzwKdC'
        b'jekZOaDE5y1wczn8n4CryhE+IbUAtHUBsR8AkDOG8tEvg4mCk8XHF4qQN+kQAxbbo9JUx2okOirhrt9GcLv0fP0X3AB1Mt3k2MkT5LHesf6xssaotA3jp4hiIyOS1JMb'
        b'lRkvB+TJlviLAhucXq/W5Moikrp/tcY7z79dmhEp+SCooGJFW23MH3p+fQa/2ixF39fKv/ZvUIoZ2ggW44qNG0cDH3x/LTMxfHRL/mikgivIFaONFQqY/ZId5Kxd9Lyx'
        b'gMOW2S+5RA/NJDIg5I9foYfWzV2FuM1ADivFLwx3dAlGdH7IAvIvnbGwMdtkjdncGoezzCE2jZjf8wVgZoJz+p3n9trO/bFKMDzT6t3vPLnXdvKgg+uRmftnNs7utfT5'
        b'3zLQ2aaL/2gDTTb/aQaqnUJ7FbCTmC4rrHgUxjWkPhSfJ+24mjsx95fFheSm/sUGXEANWGwKyPTXuyMl03+vEdOSqRMtmY6Oy6z+WKzawHLTF4RjmpnSvexSNdyAsB1i'
        b'kcBNuUil10OimaeCODuWEYvSqnxeiX0ulbYYSaX/WSbNs+j/P+CAjMOBRAD8h8fAAfIAt/5LBc1i7qR2C9zofvxkhfCl1fYFK/h2OqmfL9bZvTyyeY9bAtl5uPmkbeKL'
        b'8AEDB4fgjwkgZDky5n/35r+xRnHlSW+4K5Hm/JNfCnUl0HJjwbu8fnr6RfXTS6/bCr80i1ixImyyr0U4+i9pWEQOqljkpJhR6bRkj/LgO2rxW915b5lFkKS5ZR6TVrdI'
        b'3twQ5F+cJ1lxxEzrNuXs7TZL2ZEyv5SzIvS53pos/VQpfUxP+pMH5CG+MApTUJ9EDuGjI6DCAR/lO4TdQaRlVDKWyjYsSB11vM2TkiVoSop0uye+xlzYsslm1PeR0wkm'
        b'90da8QHmwhzWLHi6kymYN7KPeRnveOxN/WNbrvco/2iOa00QhFSQ5sfM6V/EtfhQ4jNS+M8HIcbhA2JyIojsAz/zoykA9TOjyr2WDJ+AJlPb0C40ucXtyFjvtXgGpNA0'
        b'aEa/zbjW8H4bP7bpFd7nEt41o99lTq/tnE+9lQPeoX3eof3eYQ3yQZfxAy7BfS7BHfkDLhF9LhEfu/v2+s3od5/Z6zjzIw+/1vX9HuFdYX0eUQ0yxiqkzyWkY3O/C8U5'
        b'o7ym2ZCcOu3sEi1DUv8w2eEV41EFbTYmdpkuMKY34EmflIEndaMVY7efmt4clPqi0/JQkVKUkhKnFMQphSlxmtcFPUi3F6Yu+BO/Pe/vXWWv8jQbfmId8ylymrRyqvvN'
        b'tMCurkiPgyuWfnM/8D92BS1c0WDVPWvDn1Rbrzzs/tN9bWFM6s+/fenrT/6678mmJ8jrQUXgZymF5ql4ht/0ml3zQkts74SekpXP1RyzzZ08MfxJ21D5FI8bbxYGtn8Q'
        b'ke749jthE7pWBTaPczw1p9v59iwvn5B01/ArJ3wWFPyiruCPO95YeSxTfiQz6rS4+8TiBwWCzmUJ5Z/tdJntGPXRe6cWtLr6JUi2H3wv/GC/RcZ7AeLCqHW/83w7+eiZ'
        b'mPffm/5+v/Tt9m+v7giZP2FNxc/05offU8v6Jkb2OwelBny8ds8fbtmr3GMC1+z5IHLdG32vROmDhzRmH/alXDrnka+fEN3nGt0f/LtTq/qSb735tz/+rm1GV8T5198+'
        b'sbHtyFdT5xpc9VP+3Dv7D2f+2pv65AuU/Is3G78pt3nrd8i6j2iPxlj2qWp7J0xdtLCs1nthQPcS90k93iRhi8W537vV9nc3tX5Z2pL16oItCVnZh/sCr32Rubp9oGz3'
        b'J6/73t/zq8d1L23a9NvHT94eatqFvv5C4P25nfcX5i2fr2iMOHs6ck2NS/XxCQemHam+HOLzRqbPG3975bvUggUTI4o6ypYVF2RPPZWSfeaDlgCfyPRJwx+nxVp/W5fl'
        b'NKBdbxn11w0Dlmf2f9ny9e8X3V8c+lnoBMWc7fcqnT/dm17UY/VL/4gAy5LBnUc+yH1/2oXlDiu/vL5taee4Jeke269dC7r0+QdzAjz/co6sX3/n4Ff1LSXDzn8a9h43'
        b'9WcL//yDuqcnVjkpcIrw3hPlD7OVtz6QnGxfVHA2tKD4nfl7Xlave/tvR0MjfvtmwfZjX7/pNvMz4Uvv/mpg2vj/+ctbq/oV3//xoy/1q96d9u2V3uKLTqR6/TdTrCUf'
        b'LvqLHjwcVf4IfMQZgr4A2ZPbgqmI1OXGs4KRKs+BuZl83DBSM2JuRkFusWwLXyolF5/xjKHryR2TY4xbyFxdWTg01wBS2xcsRWVe0izhBNxu4EcyLtIfHwQuCsZn4Wtl'
        b'QlKKBMnxVSE54YhPsp0rfAR35yXSYIWPJgRDQKpNoI9cEZIL5AC+o/T8aackZD92+clnLV7oV+i0KUyfufSzY8yHu1NZdnZRiSo/O1ubanKltlKE/hsQZpwAWTkNi83M'
        b'XagPDa/Z1ORT81KzrjW8VdUWdWxLR/qxl6/6dml7fK4aetKvbu4OeW3+L+xJfH940seuFI6qmqOOmbcu6nMN6XLpc53aOzOlzyWld3FGb+bSvsXL+l2WUfhp31jca8sO'
        b'PiwXDFsge8eGmP1OlfO+kUrdLSqthx2RvdugneugnccjM7GbRaXVsHWywMli0NK2195vWES/f2pp2xA6LKFfh6XIyg4IM0bIOGHOCAtOyBlhCUSvvf+wFaOsGeU7bMMo'
        b'W2ObHaPs+WsOjHBkTcHDToxyZpTfsAujXPmDboxw54QHIzyNz3kxyttIjWOUgj/ow4jxXI5HExjly5v8GDGRNSmHJzHK3yiHklEBRvEDGRVkpIIZFWJ8L5RRk41tYYwK'
        b'5x1EMCKSE1GMiDY+N4VRU40ST2PUdP7gDEbM5MQsRsw2SjWHUXMFRiYxAkbPExjZxHJ6vpH+ZgGn4wRGURdyOt5EJ3B6ken9RE4nCXjfyZxMMZKpnEwzkumcXGwkl3Ay'
        b'w0hmcnKpkVzGyeVGcgUnVxrJVZxcbZJrDaezjM3ZnMwxianidK6JzuN0vul1NacLTNOwltOFnA4b1nB6nZH9ek4WmWZ1A6eLjc0lnCw1kmWc1BpJHSf1pr4NnN5obN7E'
        b'yc1GspyTW0ySb+X0S8bmbZzcLjAu98ucnis0Ph4j5OstNEoay+n5pvYFnI4Tmtab0/FG+lECpxcJkcP4QXu/QXslu/qY/vP7ZgV7otJ8eLUQefieDG0O/dA9sGpRZeyg'
        b'q9+Aa2Cfa+CHrsH7xQ2CQVevk1bNVq2qftfAA5JHIuQW8qljSJdTn2N05YJBr3EnVzav7JD0e4VUJjTk1aQ8MkceQeANLGw/MrdtyGvSdcR25feZz3ginGUe+S2iFxGy'
        b'mEkvtsNiIOkksIebJrTqusR95lFPhHbmrvSBaONTQILxurgdWbd/Xa9PRr9zZqX8U3Mb2sGS1gkd87ucugw9S19d8Au/3sC0PvP0J8KJwABN5FwWC4xsgKY6bZSsz9z9'
        b'v4SW5kG00cP4BJDgaUY/YG0+fvQDQIK74eIu6TP3eSK0N59G29hTto/EQH43nCcTmCcIPrIfd9qyNziuX7Gw3z6+1zL+e3bUqirGM8ELvenlkDDZWNe3HRJC5PgXi/n/'
        b'StCyfQqGxwYqFp7YZQJ9brYRFccKBALbJ4CKbb+hl58KjVukIeiyfJpIg12PIt3P4c6bnScMDb+02DXXcc+f/nZeYuf054XnY2r+/NtrWYrCzzYv22VbUZMj/k3bst9t'
        b'83D/2Vua6LXSd2b9pnnryi8j1057eZev/Ttpwnn4pGOrLvyTj3Nzr/vG29/66uBjkrgvbuKJwJA2+53l06rPBLltdPh8ZWCb+YTEI38vOSLTv/f6e3u2TfvbD5fWdE75'
        b'Zf/7zX41t1bEp7fu9q5r+Mx122rFz52krt7S91bgXy+JPLNqcG50yX+u6Un5zTH0sz/8cOCUX0XpRy6l+T6Op59sFrjbeHc4BSmtGGzKJVX4HqkJWQq5cyqpZ3txcnxN'
        b'SDokUSx/C8G3fGlGfJU+QHfT7PBDcp/cE+E2e9LCcJFWSo7jGlxP6gGA0Z+01cPSL7G2F3njdhsGqlap8anEBHIE1ycHJJshqVgow7unMzy3mrSnBS6aQy5LkCARkaZp'
        b'uP0xLdXnkKq1z24D4LrQRIBtdZAj1ofhqyK0EF81w/WlpQx8RcwhO+gbvqR99EtS5DJfHDC9mO1ThoUsYHnmUz4i5IGP4VdwoxifxXfX8h3Ew9HzaRWSHCKvJJIaMyQO'
        b'FuDOLfg6y3jd5uMKUqMELjBfVakQZxaSRpt0UWa6F0tn7ckDLz25aXokiErNqpkCpCA3JPTf9DrO8eRpvItUBuLaotQgyNJr+OSTB0Jya+mExzRZxPX44nIAnbWAJUMD'
        b'yoyw1t1AjmjF+JW4GcrxP44W/y0Y8d940Y1ncPM5lPnMZwR0aoo1enAdWSbQ+Rpiu3jfuiOJw6CV44CVd5+V9/HN/Vb+O+IGxRZ7k3Ym9dr5nJ76vjjoV2IrAHru3r1i'
        b'52GhhWSl4FcyN8B33v4DXhF9XhH9XlG9MvdBmXW9vEr+vuPE92WTBmX2AzKPPplHU8z7Mu9BG7cBm4l9NhMHbPz7bPwHLe3rU6pSej2Wv2+54ol0vVgy7Qmi10fsOrzS'
        b'HFk67kj97nEZfHH5Fgklkwed3CotjD30OoZ8KAP8Cbf5Fuhd8bxQhEO9Ym1ExFoAV+4qxw2JitTFQ2J6kmRIwqr4Q+IijU4/JM7X5MG1pBSaRTq9dkiSW65X64bEuSUl'
        b'RUMiTbF+SFIAIB3+aFXFa+FtTXGpQT8kyivUDolKtPlD0gJNkV4NxAZV6ZBoi6Z0SKLS5Wk0Q6JC9WZ4BNhbaHSaYp1eVZynHpKyQmEeO82mLtXrhuw2lORPm5LNd7Dz'
        b'NWs1+iG5rlBToM9W08LekJWhOK9QpSlW52erN+cNmWdn69R6ej53SGooNujU+U9DgI7aas4/+igU3KFnmS703x3UUc/+ww8/0JO6dgJBoYj69LHXR+z6Uzw8jVmvyaQx'
        b'rug1V3nMBNH3MtPR8yHb7Gzjd2P68717wdh/VlRRXKJX0DZ1fopSRo8n55fkwYjhi6qoyKi6VJNpHQruW8DkavW6TRp94ZC0qCRPVaQbshxdHtVuQ8b6EK8UcUuYyf/Z'
        b'0tnaPUDSejbbbhsWQVx7JBQLxJCryK12mH0jjYMBDy+2QOZ2RlVeNCCb1Ceb1Bs0+7WJxL8/aNGgzPYjC+del4h+i8heceRHyLbB9QPkznr7X04DayM='
    ))))
