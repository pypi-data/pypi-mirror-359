
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
        b'eJzNfAlcVNmV96uVgmIR3HABy51CVhda1LZFXEA2912hgEJKgYJ6VaK2W4NQ7NDggoIoooIIKKKAC9J9TvZMJus36ZCZzjbpfN3ZvnQyX890Jpnv3PuqkEI7nfy+/H4z'
        b'+KtXVe/ee+65557lf8595c+EcX8Keq2hl7iKLpnCXuGQsFeWKcuUnxP2yo2K68pMRavMMi9TaVQVC0fUYtg+uVGdqSqWFcmMbkZ5sUwmZKq3Ce7n9G6fZnnEr41J1uWa'
        b'M205Rp05S2fNNuo2H7dmm/N0G0x5VmNGti7fkHHEcMgY5uGxPdskOvtmGrNMeUZRl2XLy7CazHmizmrWZWQbM47oDHmZugyL0WA16hh1McwjY+YY/mfRK4BeWraGbLrY'
        b'BbvMLrcr7Eq7yq62u9k1dne7h11r97R72b3tPvYJdl+7n32ifZJ9sn2Kfard3z7NPt0+wz4zK4CvW3MqoEwoFk4FnvA4GVAs7BJuyLcJJwOLBZlwOuB04G6SEq03W69I'
        b'zhgrSDm9vOg1kTGi5MLcJug9knM0jKmdcoHdW5NnTmw1LxNs8+gLtsbHYiWWpyRuwTKsTtFjdfyOzfj4YKhaWLheicOFMGCLYh3PQjG0UdcarF1E/bEmLglrdtKgShyG'
        b'zvAtcSEJWIVV8YlYEa8SjkKt+/6JU/jEvqfdBE9BmJAmK/A8mLVbsKXRTRjEDnyGfe5eW+KIRFX8jjjoDsKykE1J+PY2DZbH7SDarpMFxSViTXJiyo4gaigLJ1a3xAVi'
        b'/aYdQaFx8SEy6FQKViifHAVdaM+QjVMwb6dcNn3OBmV5O7ZAVianLZDTFshGt0DOt0B2Wu7YgkPjt8CdXkkvbcEVaQv2+TJJLJ/oqUvLOaWeKfCbsfPYvrw3XSak5dhW'
        b'H5duqgWNMEHYHapNSwt5I1kt3cTlSrodMV+9Js3Tz3hGuCPkeNDt2Wp/5R/8BuO8hJ8s/FjeH2makSLLYXyMJDTK7rsJuus7ji/+Z0vNYneB3y7y+b3PeR9Z0HXPP8v+'
        b'vLsjoFEYEWyhbE/KjvjSXlSGbwkKworwuFCsgDvbg2hHakPC4kM3JcmEPB/3AGx+Havm2ybRiLAEbBY98d4pkjY2CnAxE9t5gwkaoVW04ECqiloqibSQZZvC1vAWVNMY'
        b'C1RMdaNv1QJUYMcm3gRnDdAkYn/uYtavToAqeIxv2ybTN7+j0CNCjRkvKZnOCnC1AMp5C5bvgpvUtGsqKT/eEKDlGN6SyF3HDqJXgL37GQ+1NBNUbbRNZYOGsWSiiL3Q'
        b'AgNq+npBgDrsPcw5j8M6vCbaAkPZoLcFIHkcsbHdDIEneFP0sviwEdcEuLxvBufAil10H/uW7WC8XSJSm/GctNbylTggQhWRZt+aBbgyncyJM1eMzcScdjN0ML6vEzns'
        b'svJ51uHQCbFw82RSWrwoQA1W+3PGZsC93aKPB9Nr1r8RLuJNaZoh6Ddhn5fFwBjoFuAanqdpGG8LNNCrteC17Wwxd9mg2yBtENyeR+Kp9ISOOTJBphGg54xJEugAtOaI'
        b'+ADuWNmm1gtQe3SuzZ+19KIdr2OfLQfbFJKwz+M5OC+J1E5W16DF+4XYzia7RzsRjk18RSJc2ysWYt08uUSwwnKGM54PdStFmu/uccb4ZQHeJu1o4uylHsUi0Yf2qcmx'
        b'rVe275UE17BhDvZpoA+fsJabAjRB60qp6RG0x1JbDgwyDtqJg2QY5ORex8trsc+alKaSJqpdji2cbRiApyTiPk/sn6yWBl31xS4+CBsj4qllno7JoYOowaMVvGG2NQb7'
        b'sNd7OWO7jbQ+Elp4Q4gv3CKXVrCEjegRoPUM2CXptOaTLve5wzN87pDODXwcJ4n1Nlwg0fa5Yw/UMrneF6ANHkziogvPIhn02Qq2OJTu7bUGPggeTSPD6fPCWmiTSWNu'
        b'0NzSXmTiHfKdfdingmbW2ElCwsfxvO0M1OJV1oZD2W6SurTA+RguwAWzsZJ2EC7hWccCruKVeXxl07AGWrSaIJE19Atw6wjU8jFH8CHUavGBGS4zco/Ywm4IfMwq7F6g'
        b'PQpF21TSPJfhej5flFIFF7TYn+7F5NdLswT5SRt40z2V7sNtNVttHykyNEAVb1pIImlnbZJDoWla8bxG0uROJQyIVrw9mfFWJkBp2gLekAUloVpxvkIpCbwRr8I5aUSN'
        b'G9zWeuDTKWyex2QLqyUNz0iaBpVRWEeaVKUSDLsUeEOWEokltulspankkCqPkm1VQ4VKmIzDymwZvIUDG206RrR3Dm2g1L7YSYK25447VMunbpykV/C1Y4kOW7BSQVYw'
        b'TTALZmj2tfnRfWMIticoBSyGO0K6kJ6L92wTWDTHdryYoBYmz6FAkhm5yraA7eFquIsNWAZ3o+COypBEHvXm4Vho26vC8iRhqUjiXQ/3bUGMq8ZdNJ2jbw9ewPNYlg/s'
        b'21KicUEpzMRqpftBM++8ftNGqSv0QwfrGwc9q6FntCsMKRX0sdW2kDrv2hPnpNst0V0IDzjdLoluvVK9Fq5yhrE/YD02xEEX8Sv13b6Bui5ms1DXUAUOpuFVm5517YPO'
        b'46MM88XBs8NaHVZCx86Jgoj2TTo3rRWabRFsedXwBMavj328h9XsrZPRhyFsCrWoCrBHawtnnEMnnBtlp1qRLs1B6OYKyREq90KdfxLFgUE1PpoKnbb5jK3HWPvG2CWQ'
        b'aKKUW2GYYscM7FPg/eP4nAOlgjVuY4RYPUY+XDgdSYxEV5I6PUkogHuaRGiHxx4BtjC2mjuk7+1slh5stI7KSgH1WI4XoDSLlOqKEInXVFAzeT3fhehAuOmyDXGp+Ihv'
        b'Wae0ZQ0KfDbzNb69BLgezRonq31LOVd3pC2zK92wLoLzUnhY96Lri1WwZS/Gew6NWPqmiqz6Fl7icsVbJs2oWr7Yirt8uB/cXCpt92KsVcH16TNsi9iS27OxyFXp6HNp'
        b'oiQriatupYaiy9t8DhjS0e3xk9DQLolJrnsnD4eShYrYcJjDmhPYvdE5pJMNITd6nMkTSnVwg5SK9v1xEg65LcbeKAkIleJQiquFkYJg8d4gP3gaJfFFQU1DgPf6OlsI'
        b'jQiSpzn7331JCzlT+7ExFC6qRCFRWvhbnlNGN27UhmNpdeR0G7iup2CLWxhUhtsieX+sYJbs1FqXmSTRkfcoxWdh8FR1WAPDXD0OmjY4hnRKfadQuHxh+wsV+BSKoJ73'
        b'1USSgozV8ES4yDWpm/Wdgf0K7F1IboVph5+JcKKreoxaxSG861SPAhUhjho/KdPoeCOFq7azq28U0yXHJisUeM8rj6tpDq2i2En8nsT27mVjFaJN6Qb3dnFrg1qoS30V'
        b'J/yOEh54JsWsg26y+J4FggUvaAjdte+UXOOVMBhw8TS1hHfZRsfqVMJSuK6i+PMcHnJHo4Qy7HSV/hhvcynMYW9LsEkF9XFYw5V1fwaF2lFdlRxSLBSNjlMQe16Hl8m2'
        b'qNyWb4VqrnrUMARlCdxJUMdx+kE+Hno8kwTq7TZb8Rp3rrvSNJwxfL7qhT/jnSv3JglL4BF5i9gTfMlGbLa5bDG2YRffhU5pj3tpG7DD1zaXOh9dkeXiLCSPFwjXyasU'
        b'keIcpbjIiJ5aYXIxyDi8TMnii60FuwKf5BMQY0SzfaPGe1H51sMENWbgAOkXnIdiTjSS5mx26fkGFnFt7JE4vU+cToAnXAL7zRMcmsW1PG4XlrAvD1/o1kMoXmxjacVu'
        b'2pFnL8eLpZLuxEGvI2ZE4hUVAaNOCmA8zlyF624vSWOp5OB94YZz1C4V1NHHOsnEn2PRVlcbZ8oVq8OqAoeJb050i8anJEg+yVPspJeLko06XQv5fseClsCwCmqjN3G/'
        b'MB8vyVyGyDMc85BMYDDKl4L9rfBlMmha45FMwfUmj7LQbsDnrhGZHMyjMUamV+DAGqzi1p5yhu3FZzh2ybuthLpQmyqf1t7Jt2Tr2gmuuzcGR8zAxwp8QO6smPsd0cNj'
        b'fAA4DiVjEcqw0jtwo2SzXYkUpl0UqNTIda1LotyjwB7s2szlj+XQnfaSF2fyv5rulH+I22vQTJGbMSL3UrmEibjkyLFqxPR4OBGfcLH7LIP+V4sd+vZiNZ47jG1wL2Wv'
        b'YDmigcdQ5MY5MsCF16QpDgS7qt9dlZ8juHdRcMyFW9yBHIHyF9Gu28Xbv4A38TgUCg0qa0gU52wTYZvzr9Jwzqccn49qeCs5uDexluuejSTe9WL11S+Zh6qAMsZlss0a'
        b'tyi4gtclLRrOMkpjsC1vjK5ClyqdxJAkLJ6qgqqJ0M/FG7FpmUuIjMOmg5J8JcAID5RK6JFLlLuS8ea4RQQ59LNbUooKJQtyEmbs8DeNU+ZaHB6jQSsVOERmf0WKpG1v'
        b'rHtZmx22LMPGUfk0UPoEl+C8PlGqdXhho2iNPuXMMigjucgz5tkJ8aIVzsFllpmUC2AnM5MS36yJISI+xFpBJhU0agJSpUSnh2a+Knpio4+zcDKXbI1nii3wcLpImcbw'
        b'DJbftgiknqVQyTmYtOu0aCGOhllGYxdoo1snSplqEVxeIVr85M5iC9ycx1mDyghooQaodRZb1lFGyll4iM9hkPL8bQcZgRpW6Gg/IA0qy8Vrogf0Rcsl5i7g9UQpW74G'
        b'/ftFSjyrsF8pJaTN0G/kBCPxCXaIlKHZs53lmzQckDLcVngLykVvaMASRvIKrZeSMUfhYDAQhkWooVlGizsxZGWMEy08WkNNml3O2g5tVRGfbQU+jREL4DJ2O2s7tHtP'
        b'uDCS8LafiL2LzjgrOya4y2eatht6WNGnCW+4SWWA8ySFJp5+rTuWKdqs2aM1n4sBUjGkDa/BVdFrva+z6DMd7vFZ3sDevSL2bYZuZ9Xn1E4+5CDl8q3UEqBlk1ylpe5D'
        b'SeSzySU8F7XwAPudNR+4GSSVcPpJAG1iYQI8c9ZINpHZ8KYi2t0nYmEOVqqkBVUHU4Dhe9iHA5tYAeVslLOAAjdEadRw7hlqwesLZFLl6TzcxvNS022o8RZ9oHW5s7RC'
        b'uO+ptPO3rVgi+ryxWiaVVppJrPWSIO4Fp2GfZhU0O6sub5BUeYmJEOt5ajpMnstRdQmZKE1014Dd2GeF66ucZRdPQjmTeQp2aR324cPIVJkkiYvYMl1SsQqy2V5ekMll'
        b'i7rFCjyPJ3OZ5y3bwxpu4wNnqSZpO2/QwlvTqeU1uOEs1SzRSSxcwUFSkj58ELjETaJ2JWk93/HAQhri7bPLTaoOtFkCpREPYigy9UGNFa+wpT4goWQES00VhL2wrwBa'
        b't8slodYScOJNagKHXdS0B56ppV2vg/Mb+VLVtKJGVi4KinWWi9aullpWkSr0uUdgibNcBOVTHP5hK2+CS2uc1SK4Hi1txEVzOLUcw2JnqQhLBd7yxkaK7zZKdtudtSIv'
        b'2jwm0zlxlFNQ02Pscoi7nlT8Mm8rKKRkp49QIStXcOtroKDTxCmukIUS44/UeMEh78sLoVsq7RT6Y58XPFsnlzi/jhd38CGb4HYBtURAo7MqNQWvSUWXtxVkTX1eJ/ep'
        b'pKpP2+4IyTuU4r1cXpGy401nuUoDN/go1dTJrGkOljuLVVsly/QNwVYt3j8J99VSQzM0v8lXtBTbZrEq1iDUOKtY0AetXLDBR6FXq4H7kgY9Eih5bqElMV+9d6ufVhMK'
        b'rc4CF9yfJvF9AwaOaq2GXQ5tbJiNV6WdeECBvVmLDwIEZ+VrQzhXrYSpJ7QeB6HVWV2aPFEa0BGFd7VHRXjGSN1hfrXFyltO46UcLascVamlOu2lDOzmLdE5Ki3xDLXO'
        b'GhredASDN6HFzApi5TOdVbRDS/iQQBJoN2spXe0so6XGSwwUY3MItShynDU0uLRUWmTJjNVab2zHPrb8ZwJ0ZKVKkaV1VoTWGy4EM217LkCnBoclLwtDJOVeyt4dAmvN'
        b'3cpFfJI0spFapmM9GzNIG70aHvMx693wstZ9A96VS5O042MptNLENce1tp1HHQXsS/B8PW9IXrVaKybjW6MlvFLo4w2H8ByWasnNTnfIvqXAIPmPeopclbT9TVDClj9E'
        b'ezyHXBU/w2oiTaXGBig7upJEySt50O2Ae1DGK39K6NsOlTuEXQfU5Pvr4ZZeyQnP9qbQmriJQt9ggUJQ4HOC1JMJPTFuspOhNAErEvHRSrUgPygLx3Yf2wyuPDPRnoA1'
        b'4RSderBqkZ6dUXlOUExONvAdyaAtqV2UHBqHT15XCso1MujcELQhg50bOf9oEfxQiRfS1wj87IqdWbHzK3ZupbC7Z7k7TqyUZcpi4ZTqhMdJ5eiJlYqfWClPq3YLmQp+'
        b'aKj8yf+hDfDQjfmLZcecos6Qx883dVlmi+6oIceUabIeD3Pp6PIlXjpdDT5izrOa+UlpsPNsVWciakcNphxDeo4xhBPcaLTkOiYQ2TgXUumGvCO6DHOmkZ+1MqqcnmjL'
        b'dZ7hGjIyzLY8qy7PlptutOgMFkcXY6bOILrQKjTm5IR5uNxakW+wGHJ1JppmhW57tnSMy85300ephL1qQLopYwVb5iHTUWNeiDSKMbg2PtaFA1PeSytifxkkGOMxK1uC'
        b'0ZCRrTNTJ8srJ+JrsxwfO5nVySaJ8q+fx8pOtB3UwnRJNtHK1sjkvi0ldElkVJQuJnFzXIxu8SuIZBpfyZtozDdwxoLZp2CdkVTDZrAa+QF5Wtp2i82YlubC78u0HfxL'
        b'Eueq5ViLbpsp71COUbfeZjHrNhuO5xrzrKIuxmI0jOPFYrTaLHniitEZdea8USUNobsbDDkiv82EXGgSxy3mpYNyjTD+lNY3eQN3YQc4lC1YA0WjB4cD2MyPYM0x/kLE'
        b'sX9XCmlpq361JUOQavoVgRQvKhkYmrNH2EO4vJt3/k20hzBp3VK5MCEt8fpGs3SIu+eMjzBT80QmRKR5FluWC87Ts7JIgobNeGkUGt7FSr2PdAh0mrCh9k0452yLn8vd'
        b'zklCHdfFQs+5zqPCIw6kGQhdcFP0yYQHguA4LLwAb0vRth8eESpiJ0dpzuNCQgd27o5MkTiotcC5+NHjwh5ocKC8B3hFmx98SiEBrEvksq/zlq1wzV9bgOSaHYCk6XWs'
        b'kNBkI8mxBioJsckdZ4wppyQnXQOPIrFPxMvYqZZQR/0yuMJHGaB6ETt+bA51Hj9i+UYJf5Vhu4awynx47Dx+3OqIRjuhegPF/JVY6zx7TPHh1KLgrExbiE3xCilKteAT'
        b'GJKCYQm2r8Y+ywHsU0mhoU7xuhQMmwiJ3BULI3PcJGhfu2GqNKSUsodHYiHcTXei9LRlegVv23LMKhbiENQ7Wygh7JHIDU8y0TxquOqcR1XI16OiDKxcLDRDtXMe6MUO'
        b'Tm07XoEuim4hGc7swgNv6eXSURh2p1MT9mO1szHUAau9KLS1UPLonyVIAPVKAvRwrfsk0U3w1PkpBV1a4oLlJx16+yjfvCQCm1jYhQYhfTXcMW0t+Z0gepHoT/saXq+L'
        b'TFbEeK7/9e/+Ic/vKzvjtsyr2H5+5lt+37637vr6nR47K76Q0xl0x29e+9d9j66seTdyuWxjWVBvddnt3h9d+615T/rKtK6YdLfXZ95Y8772mFf9x2ujLf87MvyflsQf'
        b'qHuv7aMvfKHXx+vnc75oj248422+21Hz/feqPtYWDR3a1ZK2p/zEuaOtB45PeXTl3fLKTyJKFO4/nzX7m/O+uWjZb2PL3JIuD3+j95m4evuf75y0fvDaP4afP6MfXvX7'
        b'rw1uru3+ZOsHDXXvPWv45fe3Bkamxmf+uDfXcOXt4X3/ue2HSUWLBnqUrXrrV3vul3jN7B0qbPnDl9veb4/44sJ56msJE3/5peaupnem3Hrvx96PD6/18lzm+cnwV9/N'
        b'+q9Ldr2bdZqkAA14eVFoUFyonID9FTk8XBdKKOGyNZBtdCnU6xaF4T2siQ8J1odhbQiWC4K/TnkwGG9ZZ3AIiDfXwp0TCSmhUJ5CiEEtaLfIsQZrEq3MOgk7Qxd7Hic4'
        b'NExGMxTJt8qW4KDcyutZZ18nyNjneCimUHoo5mhoMFaEy4Uw2vp6GFLhQ6zDMk4MLgYcwcqkkHjK7gX1UrkPnPWGK/DcOptzcsZEwKTAzIgAkWTQRiFMxnMKSpmK4ZJe'
        b'PiIP0ltIZwW9O3/7qy/Mu346eVWWxXzCmKfLkp66CmPBd/WIBw8FqewL6ybuZO74jKBXypQyDX95y+SyKTIP2QR6ecjYfU9+30OmkavZVfbiytrUMn/+zr550zcla5HP'
        b'lFncGIDkzOjVI0o244iCAvqImyM8jihZPBtxS0212PJSU0e0qakZOUZDni0/NVWv/str1CstDJRZ2PM3FmZgFvbwl4WBNT7vRbY2doArnBV+NZP4lhNP7Gpjwt+ID1Yk'
        b'SPvnFP0s6HBKPxPvk1NhD5hhbyA0JzDMWZmMNSnklrEDOrzzFcvnnOL4Eh/oCV8mUmM0lBPIXCQTtHvl2BOGZ6VE8ik8WsOQ6WKWJ3Fk2g2NGYoxoZCtxs0ZCqOE0Wej'
        b'lFlKB6pUlCkIVSoJVSpGUaWSo0rFaaUDVR4iVPmebDyq5I/MjYGVFnOuzuAEgq6QzxXejYNv2/8CyrQYC2wmi4Qt8o0WQpq5EghyPsfnCgNSnOiAGAneSjOaco3rLRaz'
        b'JZgTM1BL5qvBI+OXsSsByPGLeCVycixKGjF+ha+agsHNDTmGQzqTBHozzBaLUcw352USSuKoU8w223IyGYqSABGHvw7I+2q8tN7ElvwCnhEUN+gWh1pt+QS7HCCMS43Q'
        b'YxDrEcIm0n8OelK9hJ5UybbX6XNsJmGBVzwmWJ4YvCkEOrezJwbD2cOG5SmJ8UkyAe7CeVLKcm00dIZsN91IVchFRmdC0blfpoV9oDfEGXKyctJ/lXbwnffefe/dOnhY'
        b'F11652Lrxd7iO3HbttwtbS2NrNY3tpbObnxriZcQ4qZtq/6eXm6dQzR84apcG0xmgeVYlWRzuMpZQE72hBLvwWCqVSewJ6s6sTEhbBO5SqjG7kSnM5wOD5V5HvBcL3cx'
        b'/M9yedz6R7TSg6IvPJy35OEymQ/z457M4vPCM6lGNE7FGnFzqIjkWjzZhT3N6TK9wuLLPjPXInXjLocR/P4Yl3PXb7zLwYHc8NElSusjKFgirRG6sce2ioOvuvmOBPlF'
        b'dnwHLxCYeQBVcD1EcSBhKdQUQDfchiEPIT2NkHG9F16FVumRLkJ8Nwq0R72xYgtBPgKleBebpSKHDzw3ao8WwKVNrKWM8AkWxTie6cJz3iL2+yzeqFYKcqyXTcFH+zhE'
        b'mYw9AeJiy66FckFmZk9r3dwjgapLKZu0R4+m+6mJVgmr81WdIafJ6/Rp25nHy4XzkseDdiyRkvEnaE+TkvEcOPsiF1+JjRJeveoBvYvIl670lQlyqJHFJkPRS75yNG1Y'
        b'zXylgntL6RlSuV2TpRn1mcrP9ZksE//TZ2Xi3Nhd8/DP9BjMu7Dun5/PfkaayQb/t2eZGTmcLdFofTmvHMcgk4s5I8NGzjEv42VGnZnl+s0xuliK6BbmPNdRkMiwmi2U'
        b'K+bb0nNMYjYRSj/OezqceSzlnhZDzkv01pKBho3hzcA2xcafLg/eFrs9OITe1q1jb7EpWyPpndgLXrt4LW+IjQ0OeYnimDVR1mp+ZX7MFsnlnC9lxUQ1k/nx4/njBMj+'
        b'/qoIOUrRnP9yYGR/f11wdNm8v2taLhNelZb7UFrOnBNU61dD17S/MbhQYJkIT3kSNOfMNCFCECIiwg5r7vk4nrT+qWaiwJ5PiQg8fuyXC9wdmVE7DkBjKJbwrJ5y+txA'
        b'KXvugcd4CSrTqbkMyigUTpS548NYTumG4C0QavOP2Lm0cK//OvLbNuarsesAXD8dtYQ+RgqRUdhiY946JQiqZ05aQotcLCyeb+EE/m2Kr0DxaHnElIC9ITmBjADrugae'
        b'hRamOsZHHJZS0VZyaxSr2NELobfNwmZs2MmJqKZrBXKDmogpqevfd9snbDftKbsmEx9S08cB35lfE+kNEZTSzUsaKfJ/+0mBf963ZLsX+cS9PWHTih33N8++rLUmh73z'
        b'TsyJBfU7D77/yScDq9vC3feleU74SXHXgS9/bdaJeZE/fT6itQfc1fnPXf0T5cBQ0cGRkQDfj/frDn3znfplTVsGfyOL6fVef67s+b7Vsd+K/u1vK4P9N84zlTT5xy9b'
        b'88WvvVuXvOu7I6WJlk13//RawYXB/pE/TUkZjP51VOb7N+KDP+n/zjd+0Jar/V//5vNGSlT0nyfqNVZeIGmGUl9n4qU+TqlXKAzDBR7lsXMCXtJiReSrIj2F+b1JVvbs'
        b'wAZ4jty9U+aVEhpGmRAh5orwUDYiwU2IxOvqeHZWY2XIe00ilmoTsEov0Yr2JmqTwa7UnMBnVqYhcC9ub8L2wJRQChVHZTEUzK5JSdfwtG0sgQtP4SliJzw5LQ/eAE1W'
        b'6UQsOftFRnZCXCr3hnNmnhlC/yK4loDVCVLe2J7OUkefCMWh1w/oZVLo1/xNCZiERtyldIvCBMciERIWOSMIznyLXeWUN3nzDMtbppSzPGoOvfwdL8vEMWjlRdYzoiCP'
        b'PQakfF7CpBiTME0aBS6M9m/GAJfz08cCF/bDmsXwELpHkyWWM5/MUgu+aFdA1RK4opdJz0PfhrJlUn1+Jww66/PZgS/9DGQ01WFPA1HwlmfJR3/uIfuLP/dgITtLr/z0'
        b'H13811bJ/30GWs/iYJtH2rH17//u9OYzHbBTSq4OWJ3M/e+U5Ul/je+FmtOu7heqUDolhSdwb4JYoGJ56Qbp0L4C7bZgapqHPcqElFCsSMKqbViWKPdbD3dyJ0AJ3ILL'
        b'9FEvbJ7gBv3YbTLdKmhWiStpTPquj36ZFjImQ9j9zmBodF1rgyxuya2I0MyQnYsMyQb11yPC0j5M2/0V/3945wdyYVus19wpX9CreBHkxKp5L6UHeGmSw2+8iY3cauFc'
        b'GnQ4fc92M/M9bvicuwno1GsWhcWHBGPPHJeCD16N5TWhg+zgXXIk+FaM0y9xT4LDK6wB3LVhET7nFaFMdCkK3cFrktnJX2nbboeM1lHLnuC07NnMonm1RGaZMmq5dxRS'
        b'leKVScUdmdTILZKN8SerEf0kizwrfOQ91iZ5HexKwgLO8OnDY/jdix2fY25yu/A3mRsh5E87XbR1W36OySqO2pR03kCGo2N3syyGQ/z8YJx9OW3UoFv6yrTXpXNQbMqO'
        b'5O1b94ToYuPWxyZs25FE+XBMckJqbMq69SG6mFjenpq8I2nt+q36v5wkv8qUeJDOm+EmzJPT7uvSEmPXFQi2FVyqeMWP/RZuUQJ0p2IVWdaWOJ6u8FwF6/VwxwMuH6dX'
        b'PJQfp3xF7QFleAOH+QO2R+HJEWm0NJSsiGexoVATiB1KuIFPE0xf2HBSLm6h3ofTV/4ybf8798lceosjS+7GzC7pvRBf33qxtbS1eHbTUNytc5Eldy73lvcqguZ89f7Z'
        b'O8UFszNCM7wyegM2l06btw0Hzx6fHUvxabpQqfPt6dXqlTxQz9sFj8lWUuCms0YaCnfxlpW5cqwni7/CrUGXmuRqDLeg3sp+ZUHZZhM2sCAJwzjgLF1647WdPLzaaIUD'
        b'CTxuB6kFtE9x95dD6yI3lxz51ebiQXmGOCYvn+S0mEiNzJPbjLeUnU8ftRrL1PHk/EfthPUKcrGTERc74RXhfuzyWxQXEpzsTLoXblYIU+CpcjLUzaLQxeDLaXxMWI6H'
        b'Lkq9a8OhgtsUNGmE6WeU2Ras/GyrctTr+C8ZR+t1f41lnaPc88D4et3YWMYLW3mGXJ7lvCKEsRyHndnlG+kGhTrXoBIv2VeOwWqllCXDQPHIlSiPbIZMqST4UrLmQms0'
        b'cfu8vE3K0/6nhlbZK/2BJtnGQlmkfuGsoL89sYFyaOf+5J2tjswmedXSX+9MlX5/tZbQ7FUebrE2LodF27vS85K7gxY7Y60sZzTajo+1PljCaVu8pZ/vRqgPC+qV8YLp'
        b'YvGPVeIeavFsGHINwB+lZWclGr6WFbL1I/It7717vy6ysbXYIPvu2tLkCd9ohmd1ve/dPje/RNXVMq2rZQd5G1lHyyN11+oSVrwLEFoy//D+FPXVdL3ayh4WP4yD80fj'
        b'M1TC8Dhgj/ZAK/txzspl2DcK7Omyab6WlcyxhjxNkkp4LVl9evc8K0ublmNbzJjjm8OpoYnwQMLffeHBPJLrV2tdAnn/ISnSV8C1JEdGcPjEWNe1d7J1HocCQcHSsc4m'
        b'SlZuj2VgFtQr8Sp0JTiR/OfVED15ZCdtZrbCndUUp7Naz1yUJzkZKcR7yiwzR92VXjGiZe4t1WxhuGBMsH/lhMRNwKg7Y1RWuLizr7jUEJmc4YInDDnXOLq+OTg0usRu'
        b'rNMrkpM36GUb9PLkDaZNNZcF8XdE9kbP3B1vf3/bxC2T7L8devrheWXk2aHCLx7cokj/csWmzd/quBbjdWNNzuDK4PLfhE3/4m8UPl9tOnO7sMGzTfzgH5tTX/cpXLD8'
        b'QsGMf14TM0f8UubIj7YErM1oq5i4rOpDMU/+6z/8x7PGT1T7VK1RMct/Lo5cWrJg8fH4m7r2n5/1P3IJZg3Mv1c25eY3vSt6s5+8/2NV2bfXzE1aOnFhjFabbZwdP5Ld'
        b'Xrw+JMs9Yc+XLDvv1+/oyvI6sufLJ6Luv52Uk6Xd94MNC3/4g3eTj/Y2vf4r46w/Rkd858PLM/91woGZLUty3vWtqb/RFFjz7a8XJOfXb2v+wPPQhz+b+YtHlrcq93/n'
        b'h8ZPH8OOoQMZZ5cWT0/9hTrWU2zYlzn4jYCrv/6nHx74dembmdN+strnWFzNlsDIL2X8acOjj88VLGj83q7SZd+PbWlf9bPolsnhx7466d4Hn676eeeDLb5D6cuX3cwx'
        b'LUr4XsHWDIwK3REViosXfW1nn+U/fS7eqoedeWJ02p0K64X5T8/tPP00Ke+96l0Liw4s/o+fnJv5YdDCD5auyIr6ypH3J83985n33jpuPjcwv/jayLSvB9/Wfy8gZvha'
        b'+voTP53125Xv/+zHP/2wf9rVP/5cc7XqI61X8n5x1r/v/vqbDy7e2F7/b79JORlWevdfWv9r6a1He55/b+k3O46kHon+lyOZSc9/N9TiNffT9fP+OPUPjd+dbKwnE2YG'
        b't20lmWllInNsMkG2XCCVgWs80C+ImzgmwQ4PXe4wJ49EKanvcseB8eB89n6n6evwkYTNbx7bj5WUUFeHqoUUbFcflM+dlMMtFhvZUxuLNoViWQxeik9MVgla6JXjVSxb'
        b'zrH5LijF0gTGWig07iffWhXPutyTYycUy//GQ0+99992RvqZdFQWFiVeeeG+QZOammM2ZKamcr+wjoWVuXK5XLZUFvhfcjk7DvWTa5Ry4RX/ZH+nu39UetAnmfxPag1/'
        b'/5/376E6eYKM/dPI/BSsvDHzDTn5ykkTPUhS/rKZQXLW4s2vE9jVEuj0wORE5ampY3yn1///nsoss0YdLZuIBTfpXOhHC8Y6Waa2k+HCFqg8MRVqsZZFe4rxtW6C9zRF'
        b'gOYNU29jvExspF631/4gtPJ1D1gz6dwvcqOGN0wKUX77SxOPTdVm6Fd9J0i/9MK8qxE/2Jdp/qjnK0uX/OjLHUGB/pFpF98/Ns1YF71l4hPf7If/NO2Loae+P3wh+vH/'
        b'nX195d4//MfQiagi/5LK4bUTw4sWPdlWHP/Bd+yp/3pq+nHdhZEz+449u/3jw3+KLnIPXdITtF/EUK/Cf/79t8KWffc/ty1PXN6WMxy4U//+8o/1XlJO27fSh/+3Iim0'
        b'CFZd08KADzyQYwd0LeLWmbma5/u9rA8rlfniM5uHAlrxIZRKycJjLIVBqFyMbzFRsEgD1VwUfopAtY5b/8rE6QnxScFJboIaH0GbUq7BBqjj9bmDOny+CHpUm1SCLIF8'
        b'gR4HrfxHqm0+UI6Vy+a4Yi2oCU8gF1NDYa1WIWyEXjc2KdRyVqZ6wSWshGuFrmPUwtR1yuDQUH6GCI2Ut/RjH1aRvwkPLpAQwuItwnSbEkqnneL8qo7PZBlaAlxcjZVu'
        b'gjJUBt1eGznWSSf4Vc5j6xhGAmFAmAFNSoITNdDJnVYW9lDGVwll0KCnzpKOyASfLYodODiDwyEDtkMTzXMfe6QuIWx1PCmUCeQ4VQJFab5N0FGATxelhGAFZ4u2yRfq'
        b'8Lmc/Z8MGS4pVcDfx7v9HS96xWe5R1Oeyepwj+ynaIIXg0qU4SmUMuYEWJY3gcMnBqA8FPMYrAq36EYdwKwRRY4xb0TJTlpGVLxgMKKkxMM6osw0ZdCVkp68EYVotYyo'
        b'0o9bjeKIMt1szhlRmPKsI6os8s70ZjHkHaLRprx8m3VEkZFtGVGYLZkj6ixTDqVEI4pcQ/6I4oQpf0RlEDNMphFFtvEYdSHyHibRlCdaDXkZxhE1T3ky+MmwMd8qjvjm'
        b'mjOjX0uVqrqZpkMm64hWzDZlWVONLBUZ8aLUJdtgyjNmphqPZYy4p6aKlNTlp6aOqG15NspQXjg2abEBFlbasyxnF3bEYGEJgoXVyy3sp38WplAWVja2sEeQLEvZhf1O'
        b'1cKqdhaWf1pYJc3CILCF/bzKEs0uy9iFSd/CjM7yGruw30lbWKHDwn4OZmFab2Gh3sIyIAs787csHnWTbDs8Rt3kv68b4yZ526ca53NFIxNSUx2fHZHx0+lZrv/Tky7P'
        b'bNWxNmNmsl7DnvjJNGeQTOiDISeHvL3OoToMb9N9DxK/xSoWmqzZI+occ4YhRxzxHJvyWd5wCnDMRdK/VdJ/J8V+QiNV5ZRqpULDdCxhkoyFmv8H/lzSWg=='
    ))))
