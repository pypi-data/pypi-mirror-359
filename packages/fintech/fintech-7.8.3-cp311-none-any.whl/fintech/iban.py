
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
        b'eJzVfAlc1Ne1/29WZhj2bVgEBhRl2BdBwBVxAdlEJe6yDjKCLDOMiPvOsCOooKKCuCCKgrjHJbk3SZM27RsMrZQmbZqm7WvS1/Ja29o0ff2fe+8MspimeZ+89z7/cfzN'
        b'nN/9/c7vLuee8/2ee4dfcGNeAuPnH4/AoYXL5dZxm7l1vFzeIW4dXyVoF3KveOXyL/E47irPJGsscgV8TiW6BN+vjl61jdNarOfDeXGucPz1B3hw1kw1QQuPyxWt5KSH'
        b'lOIv8swTFsamKLYW5+oKVYriPEVZvkqxvKIsv7hIsURdVKbKyVeUZOUUZG1WBZmbr8pXa03X5qry1EUqrSJPV5RTpi4u0irKihU5+aqcAkVWUa4iR6PKKlMpiHZtkHnO'
        b'lDGNcof/MtITn8KhkqvkVfIrBZXCSlGluNKsUlIprTSvlFVaVFpWWlVaV9pU2lbaVdpXOlQ6VjpVyiudK10qXSvdKqe0cHo3vVxvp5fozfSWeqHeWm+ut9db6KV6Rz2n'
        b'F+ht9M56B71Ib6V30sv0Lnqxnq/n6V31U/S2ee7Q75Ld7nyuym18X+72kHJ8bpf7+LNwxmP8GR63x32Px0pu6leWlXPbBWu5ch70Mz8lZ+yoWsJ/e9IBYqMprOSU0pRC'
        b'CUhBeQIOLEFx0TIzYGD+Wk7nAye1c9AD3IyP4RpclZqUhvW4LlWJ6xLSlweKuRmLhfhJKKqjt8+eIuYs4PbaaZlJP1o/m9NtgpPl6BJqxP1Sy7R40FCbkB6PenyxPmBZ'
        b'Mj66UoKr4tNBYz1u8AftuD4+Gde/5hufFDsb16ckpab7QpE+GJ6WFr8s3TcwPiGAh7qFXBmqcozEleiuLhIegW6Eov24cTvoH68INNcEp8UHJOJaeHISrk4QcdtQg3QD'
        b'OocacnhjOsXK1CmNcDhuWQkdQ0dRCCMohhGWwLiawzhawFhb6a3zrOgIgn1XCSeMIJ+OIG/SCPInjRJvD984gq8sGx3B/IkjKHvFCHazEVzlakaGwMYg1xWqKzZx9OTd'
        b'KD4ZVu4NSX7A/MA4djLaW8LZcFxISYQ64OmGNezkG5yIg09Fu4W2sDdKwV3hCs3h9K9mOgufb3nszXE/n/EH/p1QBwuOVyglDy89yes14xQhLlbq74adD9Rw9LQh4A/W'
        b'x6x5viPcuYifOCvSHnHDnC4IClJQJ2qFYYJR8fXF1cHxgbgaXVnluwxfTUvGDQFBCYHLknlckbV0Lrq5SRmsc4KbcFMFOq+14OGzCSC0cugEPoqrdA5k5B8Jdmo1ItS3'
        b'A0pqOKQPRod1dlAQFbZdqzHbi3vgfB2Hqq00Okeiqr0kTYvvcDl4PwiNHKrFF8NoSey0Ai2qF65FrVDQwaEz+Dyu0cnJPSfRg2Io46Ob+BGI5zl0Fvek0rtCcQPq1paK'
        b'wNAOQFEDPGnjCh0ZG1dFuBb3iXelwunjHGpUoNdpxbRRuEerE5mlw/mjHKqxlNA2FuBWfFprKUb1GVBwjkMn8UXcSovQXXQB9WhxvzC9HMpaQJkaN9HHo4POe7SolkO3'
        b'wb/jNg6d2oS7WMl+Ia7Syvie6ARpNeibjs7RLsPdqCFFWy4owxAK8AkO1W9KZH1zMwFVaa05R3yB3dLqjGvpLdvFdrjfUqiCCnPQo+hcCL5GC1ZPR49lGhHevxgKrsId'
        b'9riT6bpUjl5HNRY8PurjeBIOXUdH/Fhv9uCLWVp8k4dP4WYythxqQPvErNItMeBm+nUC3CFjHX3MrJDpO4la5TLcK1qdD8INGAE/3MAs4KwI3dOW8wvRBaatOjOCPqgY'
        b'X8JntfiusAw/Jgo4dBQcxmM6OLi/bJbWmp+xkz3llBeqZ4/p2qDE/RL+Bk/4foFDp/FV3M5s8JFuFpSIwHZJt10mNtC5gN1UL8N3QKMoBsafPqjBez2t24KpatxvIa5A'
        b'l9gtZxzgOaTAV5kABTz8ugt5JuhaiA/RSrujB+ge7sd9Qk90Eso6wdiFqIH13NWdYJP9Uh7u3wjSdQ51gGNupNVbgQ+vgyIRrsS9rIPO4ysrWKc+muMPRQJ0egaU9HKo'
        b'cxU+SmvhtikSOluM785mJncUdy2mBWai+TDevEBUz+44jx/m6JyJrof4ElhmP+7n4ZYwYkvQR9AuWodYfC+DFJnhW2Ck1FDOZm9gXVSzYh6MHg9dQ6dY1c+UmrHha0FH'
        b'fGUSHn4IoQYmJrpotZqZae8WJxm+aYa7rUG4DZVwjKW6rHaiW7JtIvSITsYeMlOq99AO4uGO5TAUQnwcXYOiPjKJaxGz1DWgGcrE6j1k9MGE01Ebm1230XUxlIjwYXyM'
        b'Palj3TZWdAhXrdCW8VAzugkleg4dyUB6Zg5V6Aa+LdMK8Y101t+tqCea9XcHPh4uMxdjPbGu+xy6tBId1blCSSQ+ifWoJhI3wkNrRZxgjgaf56Xisztoce5rqBbVbMPH'
        b'UB2qFnHC5fh+Pg/i2kWhzpM8shI/1qGaPeH0ijCTEimq48t34k6lQAcdxa21isM101TgDoq54rB06nI2gst9kIj3b4IYkM1l++MHOls4vS4SXUtElTEQRHK5XHzZgvlB'
        b'dBxdgEbnbzQ2GZ1H/brppALHoqcDDtCjq5HoiigrGdXhC1viUOe65DnoOjdTK0LHdaiZ9dw9bq62TIT70UPSVxyqxEdQt86XwAEJxGijluv4OMx38nUmuoqPC7kpuM4H'
        b'PRZKgxEza3QwCjVr8S1iOFeZw653EOn8SNEddAffZprgexdRFY+uj2pCj3ZbCQUQKm7QZuXj8+goxBB0MNMYQ1CVhc6fNOs83od6TFXqGVOla6xKTbPQHaEYd6L7bOjP'
        b'FuBT4HT5pXlE4FAbOouusDodpsGtOR5dgy4a1RRGageaAlfixwJ8D5+CGEUndCO+jvq1GiH0E3GFlWBx6MxCnRLKMtFNwWg30c5GD7fIFLgGdb1mzy0Ds3ioMJOheyLa'
        b'OlE0vgxhcD26YgyD+ALuoQF3MX4we3J3g/HWkY9uUq9AdNNcIyqFUHjWGCDw43gInlNcjLEzA+t1IaR5negWetm8OkE2qxbqBF9+YQuqWZc8BV3k4vE9Mb4NEYt2V6pl'
        b'IHh7sAjURlwlRDyYaJd004i+moSysZ0Fw+eDKiOFKzg33C/AvaD3dVajy7M2aM35+CBtHwze8czFumhmBA2vjbGBuglD6IP0qCuZPOBasjg7mStFNyToPr4SQ3stEV9f'
        b'p0XVQnSQ1g08YJtDhi6A6H0MCKE5C/UQizKNpAA14SrwLUfyYOadgtB/ToTqvROZUVxBbcsJsMDXyozAwgtmPTH4hQt044yLGWk3M9JmfAGdFuCHs8ERU0d5FrfJtVZ8'
        b'mOwARPEpsFOXNGpb7mgffvCqiXOFWWkltOKS0GwJ6qG2BbPgNrpKEE10oAnQXIKJH0Q9CboLwqiuuvF1489iU2jmThGgBgsaMBc7biEIaP1sI/6RgglTkziHL9qOOoWX'
        b'9nWVKp25dhYz/TDcIELt+GI5Hc4leJ8bYKaV+IwRMkGQpl0VHiUeP6GNTWTTB/cswpeFEvzEnHZVOky7DgKx0MWlRowV7acLpo4KjOzMpFqB0musrXRiBwZPAzerzd/F'
        b'vPY9fM8JtJnJZCyGH0MX89jQHtiGuwCxCSlkJJANbPmkDnqVs+NDaDQ+pps8BmJoBbEQdESBzsM8TUZHcB9+ZBaGL9gyS763NA5Qnhed7wTlJaNLVFVkCmCIcc4VJhY+'
        b'uM430ht3sA7QonMSiGc3EANlgDgUBBR6LjSCQgl+SJsvxd2OJlVXJ0151nZ0AYDrCZEWP5DT5sdDOCEQ02wpDdBnwO4SfejIm0nQfsCRMeDSGY7M4GiFwVKPQgw2WfZo'
        b'PIhTYAiX6CT1UxDbzIKK8BWqaclSdAeAGn7obQRqRa9RTXsWoMcvncq4WjM7EHJBmt3oddEWAMRsljzelqgtF4G3PM1Gvm4nPklnCW4LA3NiyronRZcZUOWHAvw6gKwG'
        b'pqhBhmsIRuRWmSDi4c3UFMElP0LHJ3gnUNRDFLnhO66bBDCyXWksTN1Q4uughpdvzWA4McB2Nkp16HwAQM24UiPURC1uzEj37UH1E+bgy+fIk41zsFQEIeUewG1qir0+'
        b'07XWPAgzlxk+bcP7MPMy6BK+RYbjpcMi30yRR5CHIZzcQB0Msc7DfRkE5qLWRUacG4I7qBrPKXGmOt2YPAE78d2tQjNAMfcpGnSDAaghoBgQfJ0JFFehat1MOqEkqZOb'
        b'57rWqFOIblokxy5CPdM5DT4uAfPbhw7QRpbA1O0kcNoRPzHCaQ51UaeWJAC31U/gQC/QCmqOJ3DVBoZOHuFzFZMiZpxCxM1E7agvUwSU/4aKxd32VVYAv4UQqg+BdJHg'
        b'/Hv4ti4UyqwhOlWPt8YxztYc2Cr13OH4tAjCwevoHh3lilXmBOija6uMQB+dkVHbdl0f/NIP1Y36CXpGUJALnWC5JYKXJjKLysJ1zGAe22kIN1gO4Itxg7x11GujJ4Ew'
        b'KWksAxUTZh1BYfhxJrcC1Zl5QVcyEohPq4DOAIj2x7WsoacSxBReqKHJl3HzZnR6XDCnqiCMc+HoNgQ3dH8uc47N4TDd+63MNqEehnY7lYE0N4QbXJwnTpIw1kVuuG8T'
        b'D4xu4w46rLPQlbUwqer5EJcIUwNIcCmsiCoBd9ErHRfaQA06OIsggSnoAExYJxgdokQBU+Y27i/lo/4CNtMaoBdoi8JRP8zesT5/7ARAlcH4hAA/QD2baS8vDieWWyqO'
        b'oTMJ3F1jSLZuKmnQCd/oCQ1ClcpIPsEkd8mUP5BAbWgFFB6nRA3s7JCRqa2YTZXv2ltAaJojgENG0wAQsX6s2ww+BWgat8dI0lD3HlZSGW5BSBp+fbWRpOHmUh0QNi4P'
        b'tVlOdkPXWQ/3orpS6GLgxYyeVeMn6YTSoYfojInTdeIm2neBgGCBPup4MACX2eRp2r6XArFtVn5Gz9FtegQgPaPr2BEgwLe2rWEG1bp3KagQaaBZFFQ0y9FFOm/wBQXc'
        b'8Ap4wua+JRypVYTiUyLwEqdjdIAuORfgAvehF2+LcQsNPDB3TqIWfIFOnrTt0N8TzII6I6KRSzIqXC1CjejBfOYgz+GrQLkt+YsjWNe3g/oeCvNRH74K/nJcvCIOgsSr'
        b'GTwarZYnmUVDdL9ASdO8DbsJB3byMFJgzxkM8DShBtF4/9Dzss88V7NeC0dPiFN8gs8YOSbuxftBnShjBiOmnSJ0l/abSzQgj7Hq+DlAOxuMlbOBWHov0hbpI3jo9ALz'
        b'FHTRn6G7vs1ixsLrcZ2RhqPbsdQRyrTLJjEQkwdXrsoS4LtADqqpveAruG0jpewyVGNk7Pi6CSV2gxV1fSW2MwKJBQt0opJp+Do1Dw2qCQeaL0b3ljJtbS7oBrXieNQF'
        b'HmeSGV9lZnzf21eAb64GKEQb1xKiJMkCfIQGAJIsAJO4Z2JYV/CBV4JEI4F8sqlAaBWN+5i96teh8zKJeBnqZtT+QgI6S90FzMPbqZM91zVWIeiDDAGQsyfoJoUu7pGc'
        b'TMKzlxhTFIDIOll1ruBzKZNgG8NA99AVZlUBZrM2BVE7cM5Gt2RlACTRceaOm0EXS5it24juk3SH5TJjtgMC+kGWq+pYhK/IzMV2e43pBJtiFijO4lsFsm1CBycykNCg'
        b'ucC/SV/jHivXcah03HxGlTkxAvxEFMImzDFnvF+2TYzq/TmawWtBDfgOtUx0PyRuomXeKDW2EPWvw3X40BbcuY7TFACnKjSl4w7i1iiSntlfZszOuK1kePEKxHXAeag9'
        b'6RXkX2Rn5FTXgCekuzNv1oV60BGa0DlMgyFJ6CD9AlM0LJ7E2V9yQEZst+GTqFlU5rOGVm3HmhySAUJNGmMKiIfu0KkuLeOTBNCijcb0zxxX1sGVmyQyKx5Lbj6E6vjj'
        b'RxTa4Cf4LjCoV3Ix+vRzAPOM3q6D4I7LYHS0Sysj0KWXQzMRXQBsKY0A8nKHt1xiFgmz9Ar1XHt2AxtsBtraO4FFomuibBiIZC5MLkK1AMbOUdPGZ9CN6HEEwGgALJ+B'
        b'bkIYviYUypMp4vNb4fCqlvSw2VSNb60CynUCuCwxrexSEmMnORc29WavRPsE+BE6oGIRoa8ieLL3MLlvBENq6qNmEWqrwJeVEmZBzfjxEpmVAF8m+ZXHHOretZLBtk78'
        b'EF2W4T5eOcxCOhM7duIaelN6sAMUCNZRaHGPZCoeWrJBbFu8XCblx3FsDC/jBnyJRdxamN0tMp1QHssMtSUGsUDpCDW4QVJ7T9BdY27P0ejggKg0oBqZ1iwmgtnKWbSP'
        b'EaigkkJAFL1iIc14PQJPU4Kf6GbRiAGw4zHJmyC9MbmHeowzE+lpMlCI+lehmnRuNcS7no1ifM4ZAJZQ50axEX6wHNckLcO1AqB+PZwAP4ZYgPbjI9R2cX/4nMSYRFyd'
        b'JOb4m3jBsq06d5paIUOXiOuDcZ2/kqyYWYCzOW8jcMQ3U2krJStwp39KYDwAcWtOuIAHFbqErizJGbsQTJZy6DoToEfuuNi0WNrC6Xl0SYyv5+iymEAvy5PSBTEhn6sS'
        b'T1gQE9EFMeGkBTHRpEUv4R6RcUHslWWjC2Kblfyfj/A5zlwx5hVHFn+1iqwiuuqryCvWKLZlFapz1WUVQeMuHCcksDVnv4LiorJiun7sZ1pxVqhB27YsdWFWdqEqgCpc'
        b'qtJsNT5AS+4bpyo7q6hAkVOcq6Ir0EQr1afVbTWtbGfl5BTrisoURbqt2SqNIktjvESVq8jSjtNVriosDDIfdyqmJEuTtVWhhsfEKFbls8VtsuqdPaol6FU3ZKtzYkgz'
        b'N6u3qYoC2F2kggsT4sbVQF00qUXklQMdo9peRpqgysrJVxTDRZpXPoi2TVMx9mFlpmpCV/7rzykj6/xGbUGKZJ22jLSR9PvK1MDw0MhIRWzS8vhYRdgrlOSqXlk3raok'
        b'i1bMj3zzU6jANHRZZSq6bSAzc5VGp8rMHFffybqN9Wc9Tk3L2BbFSnXR5kKVYrFOU6xYnlWxVVVUplXEalRZE+qiUZXpNEXamNEnKoqLRo00AM4uySrU0tOkk8vV2gmN'
        b'GbcILOImLwLbpiyhmCF9JXqgLZ09T2RKsO13o8u7/TIXLoQbihFkZm6Y77OboxdDZGhaT/HfHdzMreXW5nvTi3+tM+ccuPy9ZjaZAf/IDmcLxIvcrLkpXKafRUhmwJRU'
        b'Z476EgGqWaSVQXS/yzcmifBDXKu0ZhCjGx18TSurwHpTISDj87RoK6r11Jbjo6iZLF+SpUh0Hx1ikPkOOl+htUZ9qINjt7Xiiy6sqAZfzQQwjR/PFTLXfU6JH1NvH7cB'
        b'P5RpACDWiRicaV2UwCpxGh9HzbKSCnRZwGh1iwY30uZ7o4fxstK03QIG9E+jloVU15Sd+CyqsSDpYh5bwlwXbMz2oEtA1rT43F4xY0FNqFltXI4um6vFN1H9Ih7LcTVs'
        b'2s7uacF3pwNzWo77BSwRdAy3sVUraHQHrgPAG4WrRSzenMVHc5i+x/hJhKx8BmoTsIB3Vqc1JiV34Ebcr/GcS245DfwVHwD4Rxdr8TV8G3r1bIIZSww22JobU1ES1K8t'
        b'T8b3+MYE3IYCpYBVbx86v1Bbbo/0piJQ0k27JzeQMDTN7DmmB/nLWQ0eQ4/u15ajE+iu6UHl21mUBCARrsX9MkS2FdHc5MpgJZ9WYttrpVCiQ6dNJbjV19iiUm8tqoUQ'
        b'f4Vj1P4UerSG2lxICtlW0hvEV2QGfLjDg1ntFl/cEh4Sio8KCWTgstGBnepqtZyn9YCuD/6wpm7FoxQcYjMvY9e2jflvH7CxFzzkFb8hCwlp/92stCsH/dMODVsKv1O/'
        b'Jlz1XuInhwav1Ex9e0XuLx+fm733QfFfBNk/evczrw99Pk1xfBzzX7tdYv/hFVVdk/33nJH06KAcx890b315RtDn86t72SuK/j0jd67sR+klXZ3fu/nLv/758NWrnxt+'
        b'nvD7PreRdW/yXQsFwW/zI81jzWM7Bi8m6n+0MnZ65O+3//hJ06EvLxu6FuWHWO48dsTxk/f6P5v+xHPwfm2Rq+7uwQfNtb+b+VnQkTKvk4ue+fzioW3T49+v7Xr/7ZCR'
        b'34ZcPfufngUaB/fSwMEcH9Xm6OHqfbnuhX/545q9Htveq0273W8TFzbj0Z2ks6HuPzr92fUfH33vtYtBczI+OXd6599EjhG5PTnvK82eE8NbjC6F+gf6xgcC532dz4nR'
        b'KX7gcnzsuQdHV0XPACcISgjwUwbhhgBc5Ulyrc4K4aa56NRzgkzwCW1SYmogqkql4AMdypal8XE9OorOP6fksmYl2fBT5RcYhPRiHug/wA9HLXnPCUY1w9fJWnE9bnBA'
        b'p/xxVTnbsLMt0A9XB/O5IPRIhG+hm+gQrWnc9r24JjkgAdevwK0cJ57Jt8IP8MHnNGFzIQNdT2S3I9BHkNIa/ETAOeJDZLHtMT6mlA3zfZUaYjXf6KAl+2wUin2m1xeO'
        b'c/I0xTtURYo8tjctiATjecPmNDRkEGHHmO98omI9HF/s40aWizgH5xGOZ+k+JJ/SqBuyl7fENMUcnXNsjn7RkLXdCCeznDHk5NKiblIfLThW0CgYsncf4cxsvdqnXQ4+'
        b'H9w7bcB71qD3LHpqhC909Bly83nmFvjULbArd8AtfNAtvFd7t+JmxRt2b6wcmJUwOCvhqVuCwS1haKpve8SIgJuyjPfiYzefQbcIqISjz8vDkOe0Vl2rbkQA31+8ePGx'
        b'i3erS3t4l9mAS8igSwhcYus15KZojRiSexBhxpCHV7tXe2z71Lb8xqVD1k4jnC20ydXrXOCpwJPBbcGNZqRt85vmt88csPcdtPeFpoEKeveM5Tw4OpuOH5NHj4joCTHn'
        b'5NqS0ZTRvmrA0W/Q0Y82FO4yTI80yMmb1hMa4jzrY0eX8VcK6ZXtBQZ5KLxHLwz72MX9nOcpzy75gEvooEvomLbYy6nQurRrnmFKNLzp6RdDto50iFqntWraea2aNt+u'
        b'IINrFLzZoDm5toa1xraGHcvXk6a3qg3WM+DNCh3cWzcPOkx/5hDw1CGga9WAQ9igQ5h+8ZD92GG3doHqWs4ckns9kwc8lZPr5GGD8jCDTdjHDs6ttq12rXbH4lvLBxym'
        b'dzl0ZfXyunKuuYCqRt6Q3Ncg9+2yHZD7D8r9u8qeysMNNuFawgHelATGRnFvRpkvFAuQiAdHDXhkTmkxLCR2OCwACDhsZgRUw0KCgIbNMjI0uqKMjGFZRkZOoSqrSFcC'
        b'Z/75dLCAQya8TFNCQxy6hnj8sWZ/glx6FA4vyAtMXy3k8aZDH/y3Dx9byfXqqoLagn2yEb6I5zAks9PPqoqujf5YaL0vcX/yoeR9yUMS6yGJvV72YkTEiWzGn92Xyv5p'
        b'CZ85K53J3bKK5Qsg9JFtocUx6EwisPk28Bu4JgXXpyaIOKsSQVQUvkovII4QNSYmpTAyxeNkBah5HR9fx3dKjTtVcPPuRHyFGyVhkRtyTPttyUtoQmr7CI3iMxpFSRQH'
        b'FEqcJ6TUSQDUaQLt2S2k1EkwiToJJ9EjwR6hkTq9smyUOuUBdRriTaROdLfsGO6kKd6qyDKxnfG8ZjyHmcBRVv0TKqVRlerUGgagS1QaoFNbGdI3beEdj3VTTRAYKuK3'
        b'Ap6o3qparNEUa/yosiwoyX01QyL1JdVlLGliI15JD4yNYndMbOGrHkE41ZLCrM0KNWN2OcUajUpbUlyUC1SAUittfrGuMJdQBYb6Kccz8rpXk4LFatLklxwE+GaWIiyw'
        b'TFcC3MLINGivAUXyJVcEkAcpvyFFEKXo5hKr7kHnVOP2y0bhLuOW2aokv2UBqHsV2z1LTqQmJSTzOHQVVcmiUX3SKnX4bwBppYEeW03T6e+Gnelovt365NBRntWp6hXO'
        b'LbyKqz/3Tq49c03W+Klte/P9ZuVhtUv48ojwpIAjVfs7TnSc6Gu+qL94pONIaJ2yteOIV+v+cHfup3+yiluyR8l/7k0mVYtXqcwP5huuwrXJOoIL8I3tAA08Ub8Q38An'
        b'Fz2nm6IebYpPDLJ0WwboANWx6C/gXNEtYRFqxveV4q9xaeLRCE+d2bCMbRxnsXysQIP5co4F8yVmnAOJZ5aLeB85eRumLhxwiht0ijPYxA25TH3mEvzUJbhXcm/GGzMH'
        b'XOIHXeKrlukXNU6jUZ5n6T0kd2td1bjDYOMFYUif+EcyUMxfmw1LTLY7bGa0Qg3BPxqyPUzjNr7qZswbk9ozR+xFHPHYOj8jl5UbPTFUu0DM400jHvVrDt+avyXgvVUa'
        b'xF23miPQzQYhyBOYxsRM2BUgEocA69Wi9gDBxsSZqL4U9djBRZfQI3MuGzdZ4jMSI0+5gx8oZfNwzzYr4GTAGPHVRZgtG6fhJnxfRrKM20pJmR44hM1uyrBs1/C1+I51'
        b'mBB1AvPi4yaeE1CsYzR/5lKObmgr8sI0fI5XzKG7RQHUp8cm40cy3F6ybZsYdB3m8KncGAgYlJOdDndOxM1rR709uudBU3Uiy4hxCTdo4QmScLuLD1NaFLZS4r8L3YM4'
        b'wuP4qJ4XR9atxgUKiWm+6rmX+TYIFCK9KeMmhYBhnicZDRgTc23/MwHj71+Va6Oebnym7SvdJXGt5PKvz1h9RSKJ3Px/nkfKKaTV0qrKJmeOJlSQ9EtxTo4OIkNRzuSK'
        b'mnJHi5fHKuIAgWlI5FgEETKnrFhTEaAo0WUXqrX5oCi7gl5pjGRxKmhPVuEkfQvBdQSNqVsWGRQd/VWN38q4VX4B8LFoEfmIS10RCp9QPb+FYQtpQVycX8AkjWPalFWo'
        b'LX5lBow0kvZzCct7gdZcEsQqSiZ0IHn9S/BgVGNxyWRUQF7/GjIYN3jfauJtFM6NiarWKUt0MSD6lYpe9SOUfxpRU3TR6LCUZjreznbZ/lNBJnHsUw5oUljK7Uq4/Wt/'
        b'58cTdz9Hm+3K0c27pbmbScqOW0t2st5am89juaRG/DgU1filID0CH8K350lREzpC1aQlWc0c4kdxXEhmQOBSH07Jpw4QXcQ1e8LhSyjBBNdCzXJ0NiCtWYV6wqGlYRze'
        b'vy7MQk1V/Oo1W6dLvAUcV5JpkVOxjqggHeGIevAho4rTgaF4P7pL61iCD67B/RCnlkPFli+f4kWV/HmtzOnnnC/H2WQmFc2bz61SF4ne57QfQtGZE8cPp/VZHQixebRJ'
        b'KZoZmvJO+sYvPab/+SfxztVpZhtrrX5dtGF234vm1xYsePrW9GRt+Y3fP3o87/yMkBPx3rrLop91f7hH90P3tacPpEf/5D2PuDXSSruffeGdnRm3UTXwne9M/a1L9V9d'
        b't2U1DO2TCnNHSnX7Ot//WGETlfn9tF9GZbjf+PHZN8SbHLf+8B/PvoxRa20in3805W9Fhh+sjjrb+H5BZd7349+8maP44Z/lQQX/8UG74XNJgvWa83OPVX3+9sFNN80+'
        b'yLy49v6PDz23/Ft04ufNbhePPps/PGKYefjFF+KI8mj0gwql5DkJU2aoAR30D/StwDfjA41Jl5Dlz+l22Msi3DkO86A+fJbmQxjosUYPntMF3nsO6IE/xBFUlUoSMMFw'
        b'TSDdkd6GaxPNuFDcLk6YV/CcLgTV4kdZskRcq2QgCpQ5osp83CiUlGie03yhLX6SKER3UgMhLG3jxeJD+CzNukSuhnrU4KpgK3woldR1D99vA75Py/DDGQDCapIDMnFt'
        b'Aq5nOZm5sc8pYaqM4SXiukSSOMIHdgXgKo6zDhFsxh24Wyn9ZhkYwthGEzAMokkZ1YSYsuPlVwrPkngMnu0CeCYfQ7rtHFuUTcqj/sf89XEUhUktfYCBkxRAPO8j1+mG'
        b'GUsGXJcOui41OCwd4QtsvYY8fJ95RD31iLpnP+Axd9BjbuPSxqUvPmK3jDnQrEFrxIgAvpPcib17Y0xrTnv4gP2MQfsZIxzf1mfIzfvc7FOz27WXK85XdOy8sJMla16m'
        b'Xj6293hmP+2p/bT2lQP2ykF75dhsgZ1e2xhetb12e2tY9R79nvap7VkXpnfFnQ9sD7wneGLxwOKN9IGoxMGoxPZA0x2NobXbWl0M1t7wbs/p8rqQ1ys1TI+Gt/EKJ5bi'
        b'CG8tbbdt1bZFtZdf3n1+d8feC3ufukUa3CJN+anGmVoyia87xgq5N4XmsXaCN215cGRYVcaAKUn0DQsgKr4Kon5lTm1SDoHsrBkzmr8jF9a8BK5rzXg8TwJN/xuHbzV5'
        b'0CYN425axXICJfO3VhH4knFxNhQfMa7NOmeN+2XhaLjYzjH2T39ZKMzjj/6CcAJc+x/4BeEhJf+LH4yLaCtYRPwK8ppHuSfFXmPXPP+v2f5XhmTBK0KyOEU3jzpA1Mr/'
        b'2pjshnomEV2ywYYifk9vdFJbKtpIHBlbTjudRX8mgG+g6/LE1EBcnYxrV2J9Et9uMbqCDqOL6CR8UUahOm65jRm6gy6mqgtKPxNQynyh9r3T350JlLmPUWZCmPvvGSmz'
        b'BaHMmS42N4788YHzvs9ae68kZi2MsM33nN0UEH5kd61sTe/JD97b1x0GlFnALVfYfrhepBQ9p9son0Ac7p5AmoP5qNXVGD9QPT5NvfdqfDiHZP7FWG+KQagNnadp/RQ3'
        b'7di0P2ntDZr3n5ZIGbcHbkBd4wIKkLJDJKgIJdn41nOyrQ+fdcJ9Y9YGsgLp0sBrWUr+GE9AfLbJqZttVpVRl276Qh16Nscc+h7JV/LtcXn0iYlnnmX0R04Kg9esAaeo'
        b'Qacog03UkL37M3ufp/Y+7bkD9v6D9v4GC38NyTcwrybSkBj9SrpNcimZL8k2AXujlXWG+a4toP4KartVwuMRqv/qw7flj/5IsNQxqR/XbRUl+FqHI9Rz/+sOp3vcfF1Z'
        b'Uqgu0456FbbKDq5DQc7mabI201XzCR7G5KWyFDNfmQcbd7FvXGp6yqoVawMUcfGL4xJXpicHKOApiRlxqYsWByhi42h5Rkp68sLFK5Tf1JlQ7Pqf7AfuNjZBpUnKqX4c'
        b'TWqgQ+h1fIH8tt2f/M68Kikt/mUaADcp0RVzdLIC/iegKnQMPajg0BmxOdKX42N0+7M9OkmiyMvbwZHQNBZuQvUeuEuIzjuYqV13B/K0+XB5Rt0B5j4qeILIXgv9alyx'
        b'8f0z7ystlLU9SU0lfeuOuB5JuRT2jvd/2eUdeuyQNf2SqnbBmdqQPfY5M1ZaChY+408vvKML6/ysW3UtK2BJRIvLRx+6viN632IN1/29gy5RH/BG2p1yDtsrhc/pYm7D'
        b'hmV0lRAcxQIH4iqK8SEKLdcF49qxjkCLW/nMD+DqpQwltrvia8aVO4CIGVlk4e72Uro8mIea0a3EYHw0jqBXXzEndeajjhkLlMJXwgZi1KOzb9gc2LjWmKUb8506jW1G'
        b'p7FJyjk4j3EOX7F4Qx3E/AGnBYNOCww2C75mGScULm/3GHAKGXQKMdiEwNmWOU1zjs47Ns9g4fXfciRkZ9rYNviO8yXJ0v8NX6IhZgyQRkHG+4EcHDrFNKgGNwSj6tQ8'
        b'tr3Mda8wvzz/1a5mF3E1QhO2IX8zwbiq8b/jbsiGsI0TVzXGQhya/i/K2krTIa9ANiQZQrbvlKjgBCCg8VgjgTmdwqyyMpVGkZMFMGW8Ugp4snLZwsmkrM44XaMZnq9L'
        b'8LCEzv9PiEvCEBe+j06gJ6+CXIfQma9ZXJDsoX42ReTMHfLMJUxhV0b8Xo7CsPVcMqAwCsGi8DlUjZrxWfYL3q5ytO+fwDCCwSJ3gVWfXU61C8Rm3DELmJuKzMLNUfM5'
        b'tfx7y/jaEih5dMufrWZceQnNGDBLsjjz/pn888qkH2duO5o/4wP+tI8k+65PdU7v8r25T3r6u6oFD11/8Hm2sDvnnUtBh11+uKj99eijuWt7750W4Y+uNZW4317wJDjz'
        b'7TzwwA9+Ev0B94dbU/LkCqWYLnYk2eDDRty2cdNL5GZa62hBVXTTBLToLro7hvin0jVLXA9OOFnEzUoR484te3CXI3W+qKkM1Zg8N/htJ9wRiB4GUNc9E52dbkJ5XQUM'
        b'6FGQh9vxyefEDeBudHW7ybujevR4NHcglKCDqJ5elK4tYygvate4mniiJiE+4+QEbvAreSBxg2MWXiwolAKLJ/NpxziJevWLRq++xPwroSBly7MHrD0HrT3bw55a+xis'
        b'fehCe9hTeVjv7AH5/EH5fIPN/I89lM88gp96BA94hA56hDbKhuTez+SBT+VkK4U8fFBO2Lnt3I9cpxl8Zg+4zhl0nWNwmDPk5tMa014w4BY26BbWGzroFtEoodqDnsqD'
        b'urYPyKMG5QRhjgkCZsMy4tEzijUEJP5zhsyWc8YsRWmSSWAY1xExJDToTKGhFEKDCwkDX3P4VldzTkgDuGtWMQKlICVliZK3RMlPWaLGbjc5bQcM0yWhZV3Tr1fbp9m8'
        b'/bMi8x/P3CF9+4ho5++H+nIEbuZ+Oyy9q83TQqY71ebZ9/5K4TSon74n/r/ii0/Y3LQ9f7r/ye7ff//D++HRxYMuqw78qD0w3zrmnbdKOrxzbf2so3/RZCN93Gx9wSPu'
        b's5/8LNrl8G9PmVe1JcXF9J88+cMvkpw3r7yoyXp67uLnM7eHzVj4qS5yZ3Lu/lm372z3CZz9vdKbmzI6vhOy0br68TuNFz7dfujMI92fFi7TrflFqErZs0NVdCY27rRz'
        b'4wNhof2KId7sKSXnSz5sOvyx/CP+Yt/6eN9Y5dojmpv847mOG3Ijtry7bvCoNqSlrfKvn/IHm2V9+g21PrmCE03f623bsP/4p37Xpj/L3Lro/L/F9Px0R6FiVrb9fZf1'
        b'7/ZcibqTNfvHevdPU37rXZ5jfX91ze/i7O97mr17MGqRxzu2f+g68bPanE9L2/Txfcc+SGj75LGo51N1m9e/fTKlwmPrp6IN034yELvpacyTa9/fubhm2yd+Fcmfi++l'
        b'PBhY/NMFsyrs534a+GHK7D99YvWX8tKG38bN/82bu//AE78bO2fao+2Lvrh1O6Nm3o/85r258g8uR979taQxeKTJYss/znTrPJepc+w2SHKcp24//Gz7wbvbZxVVJWSt'
        b'f9fp+w/mf5DaVuzdX2DnHvgfN232vBf8t7f2+m2ZefjN4ufvpf0iyfzcm5trw2d4pZ558cuj6x7+5b1N2i3u3dWn8gbf++InLjf/emHJnqXr4o4/fPa2V8uf/ROWfPI8'
        b'Ofeh7cqaVVe3rPzeoPkPfx6ZM7P931//0e+/vHRth8971qU/OPPu+/VRV4/fV9X+vbO64k70SNr8pWve+zOesesdee0vrv6k7csTv/j7+vR/3/TdhO+my2f89eyTyl5d'
        b'tyas+y9J/zYyNfO92XGxHo/qvqj68oveuZ3/+Ovd+Zt7X6978acGjwCbnoXSL3lv7A1cEfgb8LdksvHwiRiAODw/3MfxojhcHxlE3aKlzwbi8vBRfHVculQoWY8uPSfr'
        b'q6gD3c2U+TtNJNlGVx239zn7ExG4aTOuAdhbFyjmxHNKN/Gn7gmg9LoMP8Q3/ZcFYn1CUoqIk+EufAn18fGZBXk0eRqh2ZtIAidcgGsT4IIifBnd4IM7PhKvnPLN9rBJ'
        b'vurwjXfCvdJjkeqOgoMF5LVv3Is5dklGRmFxVm5Gxo7Rb9ShXzYz7hCiXp3HWTqOCM2kcubFw6rKa8tbvap36Xe1alu17WHtWRciTu5o29GVdmpv697eafBPc8/rlu5e'
        b'2q3tfUG3gt5Y9Maid+3ejH8r/mlYkiEs6SNngvaz2iJOStuk7csGnIN65QPOUYY5KQPyFMOKVYb01wZXrH4qX22QryaQ3u5o0bEig800sm9sDW/EnLNzaIw95qhfqF/4'
        b'YsSMJ03gDdl5NgZetDAELhlQLB1ULB2wix+0izdYxEMLRszFruYjnOmgtxpx4Oxchmydh2zdRsyELnAaDnrLEatknqP5kIWNwc5nREC+f2xhA/NRRL6OiDlLWxDMqCBh'
        b'gpQK5kyQUcECBIOd74gllayoNG3Emko2xjJbKtmx2+yp4ECLAkccqeREJZ8ROZWc2YUuVHBlghsVphivc6eSh1HypJKCXehFBW9jPaZSiaPHaewCHypMpxcoR2ZQyddY'
        b'GyWV/Iw3+1MpwCgFUinIeF8wlUKMZaFUCmMPCKfCTCZEUCHSeN0sKkUZ6x1NpRh24WwqzGHCXCrMM9ZqPpUW8IxKYnlUXsgzqolj8iKTvJg3ptHsuIRnrPZSVhZvkhOY'
        b'vMx0byKTk3isHslMTDGKqUxcbhTTmLjCKK5k4iqjmM7E14ziaiauMYprmbjOKK5n4gZTvTYyeZOxOIOJmaZqZjE52yTnMDnXdLuKyXmm8s2TuySflYWOqFnZFuOjCphY'
        b'aOrtrUwuMhYXM7HEKJYyUWMUtUwsM9VDx+RtxuJyJm43ihVM3GGq5U4m7zIW72biHp7RDPYyeQHfeHksn9kB31jTOCYvMpUvZvISvmnsmRxvkhP4Y7pjGZ+z9x6y8xmy'
        b'U9Kjl+ntM7KWP7Hz9NKRDXzObdq54FPBA67+g67+4FGkwfRQtUwf1+g45OzzzNn/qbP/gHPgoHMgQcgB9HBU2MhrDB1ydj9necqyPavLdsDZf9DZv1HUKBpyCOp1HHCI'
        b'1C8ecvc8t+7Uui7RgHvQoHuQPqExpypFnwIuydxmSGqjlzfmtGq74npzDdLZA9LZg9LZI/y50pkj3Dc4/KeAM58Dd5JPm1qnESEpgL42PqF1aru2V2iQRgxIIwalESN8'
        b'W6nzCPcVB6IjEq4a1UUKpnNyl5YtTVsMXqsGnNIHndL1so+l1qz6K9undi3qdezV3XvtjcXv+hj8lxukaQPStEFp2gh/OtH6DQ7kqSt4cOvo40nJct7LzjJIXQekroNS'
        b'1xG+hRTGYfKB3OoGF4yqIAVTXqnBSuo9wk0+TNJAChSj3bnSIPUakHoNSr1G+HbS6BHunx2IDm+4dFTXuFK68bcqdv5COw7ZuS4MMC4B2gzzMzL+1XW/fwVQ2LykQONB'
        b'hCadcKFR/DCV4gcTD4rj8Xg2hOl864dvdemwXRrJ3bGKFQrU0yJzRdrvw6nKT1x0jfNlB0Ns3g6+/1a3puxinGzh+i8253d4djV32rRVx/kPxd49sPnPT3/43tvBP943'
        b'eP6tBQrrn/7to9cf/sUnuM/Bc3nSm5bm73bkZUZfefHE7Rf5O1e/qXmtM7DzheLt5Op/OHw+3TzQYdHTz4919qEdeTkRv7rzqPrCyd+s2/nFyrkuznc2/0eV0+VirdX6'
        b'OfwPsot8qkND77cpNv7DffO94u977nvnSvKxKeEL4xeJUy28ct5KaIoLCpSqF/O2xhvqrcpq5d+tuH9q9Zfmm74UucpD3yjdo7SkEJr8oPwR/UuxqbiB7EYoWsvJ0E0+'
        b'4NyLLPewE3ei19fPIPmaPnIZ2Vpgix8KUAc+u5mB7FZUn4lqUAN+iJpwA8kpoDrUYMZZ2Qk80EXcTfctTEG3NyX6FCUk+yWbcWIhX7IQP6IF+Ba+G+a/TMQV4H5eIodb'
        b'LXHfc/KbcUEOapmYlkL1wbYzEgHE1wPubxBwS1GfGTz4OrrJ0iAt+EKa8R4dvjh6m5iTLxL6Za5n9T21IZjmQYKJos5Aky43dFqILqFbq2jCG52a4uKHekmiPxHXmHHC'
        b'QB7qwWcdKOzP2IWO4xqlwAq0QL9VpQIgsE4TpOMmXEN/5lIgw4fhAlocAJVmSwW4A1XyOAW+LeLKyqiiOfjSEv/UAFxNn2OGO9XAMR7z8V10KJNtrL2DmpbgflwLDCPY'
        b'rzQQXREzBuOqE6IjwDpOKL2/mkN8K8zhWzxovSkJmcQ9JrxGqYi6SF3GqAj7RqmImje608CVE9nvSyH/hiwdnll6PLX0OLN9wNJ30NJ335IhoXll0oEkg63XxagBYcCg'
        b'MMAgDBgSWu5LIP8gWLp6GIROI3xz0TrekMTFYHoDfvfwfeYe/tQ9fMA9YtA9wiBxHZJYNciqZT90mD4gmTEomWGQzBiS2D2TuD2VuLXGDkg8BiUeBonHkLXLM+vpT62n'
        b'D1j7DlqTJU0p6Lawa0ipTjG4rRmwWDtosdZgsfbFiz/ZchbyEY4vCnl5GHJ00Zsbn2RwCBqQBA9Kgg2m94gILiHsxalAKAJP/z98XCflLBzAGdJfrIiECyM5FOkV5yrA'
        b'Ljw4spDiOSwoVBUNC8n2wWERXfEbFhaqtWXDwlx1DhyLS6BYoC3TDIuyK8pU2mFhdnFx4bBAXVQ2LMqD8AAfmqyizXC3uqhEVzYsyMnXDAuKNbnD4jx1YZkKhK1ZJcOC'
        b'HeqSYVGWNketHhbkq7bDJaDeXK1VF2nLsopyVMNimp7PoRuxVSVl2mHbrcW50bMy2CaVXPVmddmwTJuvzivLUJG0+bClrignP0tdpMrNUG3PGZZmZGhVZeRXNcNiXZFO'
        b'q8p9GSq1ZCE985+9FAoW+HJNB/JXmLWBPBNn/ooXWLAtj5cvIOHr/+fjtxZ5CXJ501waq+DeVFjFBgm+kJh+ujdsk5Fh/G6EFV+45o3/k/OKouIyBSlT5aYoJeQnU7nF'
        b'OTCe8CWrsBCwT67Rq5DkLJw3B9PRlGnL1WX5w+LC4pysQu2wxdilFc1BzpgbZlliMsRfSOawP2k/T0N2PJHVNe1uOIwIANeM8IU8IaB8OFhwMst9ZiPiJdAdI9yY4wpz'
        b'TmprdBzLmDOByc+LMATMe2P6G9Pf9H3L1xCwDN5DEpshcyd9gEEePmA+c9B8pkE4c4izMXA2jc4DnOsg52owvWn1/h+4xoZQ'
    ))))
