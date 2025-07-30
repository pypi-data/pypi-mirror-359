
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
        b'eJzNfAlc1EeW/69Pjga8z3i0MSrNDeIZk6iIgtwqikaFtmmgFbuxDxRvUWluFFHwBm9AUEQQ7+S9JDvJZDJHktkMM7Mz2c1mjs1cOTYzmZlkX1U10AiZzPz/8/ns4qcb'
        b'uqvq1atX733fUfXzPyS3HwW9FtLLtoDeMqV1Ura0TpYpy5QfktbJjYp6ZaaiQWZ9JlNpVB2UtqhtIS/KjepM1UFZoczoYZQflMmkTPVKyeuQzuOLLO/YxYsStVstmY5c'
        b'o9aSpbXnGLXJBfYci1m71GS2Gw052jy9YYs+2xji7b0qx2Tr6ZtpzDKZjTZtlsNssJssZpvWbtEacoyGLVq9OVNrsBr1dqOWUbeFeBsmuHifTK+J9NIw/jPpzSk5ZU65'
        b'U+FUOlVOtdPD6en0cno7NU4fp6/TzznEOdQ5zDncOcI50jnKOdo5xjnWOc453vmUc0LWRL5mzz0Ti6WD0p5JO9W7Jx6UVkq7Jx2UZNLeiXsnpZF0aJ05OkWioUd4cnr5'
        b'0msEY0DJBbhS0nkn5nrS35bnFBL7Lmz08xHDJ+VJjmfoA1aGB2EZliTFp+wxYTFWJOmwIjY1OVgtzYhW4mM8CPsdEdRx60popY6VWBWIJbKNSVgZk4CVq2lIWWhKTFAc'
        b'lmN5bDyWxqqkfKjyWr/Wg0+6abOH5CNJQ8NWvxqqDtwlOdLpS3iYg2ew3cs3JYZIlsemxkCLPxYHLU/Aoys9sSQmlciKmXrm8Y+Jx8rE+KRUf2ooDiUeU2KWp/oHx8QG'
        b'yaBJKdkN2Aklo2bjI6g0yNx0ya9HHEu/YT+y/FwSlxXLSeJykriMS1zOJS7bKx9M4l70Shgg8VNC4rHz1Wzx0rSgDJ+JimiJf/nJSDnbhoX3lBk+mUEvii8zfTyloZLk'
        b'P9eS4fPvuYHiy1dnqCT6PfRPiRm5P/SZJjVKud709efSWOWnw8Mme0jvz/hY3hl+QzdNlsv4GDWuTnbT4+frpIUZET+xLsj9pcS/fnXMJ0NqhrwfKCX/XPbl2Ju6Y1K3'
        b'5AihhjwsxFO0AWWhFuhI8ffH0tCYYCyFxlX+tBNVQSGxwcsTZJJ5iNdzL6DTMYopF5bD+RHQZfMhGWOdBCckrOctUARdcHWqv82qopYyCYqxMc/BxJIj4eVdm21WD/q+'
        b'QoJSrA7iIzygcrgVj9uwk+nhEQnK7djuGEkf5npC+aJnbVBJcsIGCc5i+x4+JBqds7fDVWohTccLEpzD83GO4dRijYyC81bbNjZ5FU0yq8Axmr7eg7exZqnFhm1qajgu'
        b'wRG4jm18ErgSjRX5c2wONuSoBGVwLEus5Mx2qMWD2GDzZYPOS3AyP5VTg2a4lwwn8YIN2xlrtURvssSb8FA2HqC1XbNBOft4RoJT3s/yifBYOBGvy7BpGNP1RM4nhU+0'
        b'HQ7gAzgOxbbtpKl4QoLKjRv5kLQ47yS4YxsiiQF1cIQkM4Z9apoEZXZ0YrsvY6BFgvNwCM8JFsrhwmR/uK3hO9DMht3A03wmbMMivAddw6GMNk7mKUHrXAMf9CLU0Zdw'
        b'3oa32I5WS1AFh0IEvZtQboK7eppaIaRdsxWucjaisYPxdUiDN9lcN9hGlNJcbLutufLdUGTbLhfkSvGUSpBr3wQXJCyy4R3G+kkJjj6H1ZwcXIFbBAhlS21DXPt6Ckrw'
        b'AB+2cBLcgKtwAds9WdslCU7vxauCYj1c2LINblIT4+Iq50LNF/z0qnAZVGG7XSWmqiJ0KOMtPrvgcAE8wnYftRhzForGcXKaYVgBdbSydq7c14gcdGTwQabsjXhnJ7Zj'
        b'G2P9Iqk9tOzmrEfiHTiRTdJt92KDWiVowGt4luvkit2zt8yjBpeILhgnuvT+/AYTdWv3YmK9KcFFPLGKt/itx8t4bxcJ3KV4R2fBCcdYJqGKsVgNpSTNdl+ZGHUBi+Ax'
        b'b9wbjlexC9qJv3bW2EQygjNwljduw2NQiIcJNanVQ+jMuWfhBl/yUGzKgzo/2kYX82ehEJqFCsLJ6KXwSOPJWjoluDwXyzhBbMFTUIP1KRq8xeh1MFauwRk+yhuboRiu'
        b'RmryVWKqk5PWCNPpgK4xyTEa7GQSbGM2/RgeiW08gc4XvPEMtbFlt5NOp9LKWNM+qF4NlVBETSoxVQNW7RQEjz+Ptauxy2ZnDBYT/hCWFXEm1qWGYeE0DYNjJvc6qIVa'
        b'Ydnl0JLhhw813myiu6R32GxyjGeCsCyBstl4hNgsV0ngxDIFXpAl4dm5jqeoec6UUCjLxxqogFKVhPuhXpkjgwNwB445tMzpJ+6iduL0BOsT0UPHCyrkY7AZb+oUwgyv'
        b'4DUNkSYbc5I/lizQSFo5lLkP6MTrccqNs8hjSpuGeHJLImioxxNx6gQoYn4lcyaUO6bR98MSsBGPYTE0z4ZGlT5BPwUq8NLmKLi4LkGKtKngOLaMdAQwCgewcwfe2NnT'
        b'uxWPYw3/MxKa8bhSmoAVSi/SqyOOGdQ9ywMOw72nRG/ohGusewy09vaGh0pF6FpOGm9kkc7Vzush3eJG+rogXa1Uk+Ld4KTx8iQDVi3HYzFwnbju7RzBJqHOwQrswo54'
        b'RyDrW72YdrOHZVogif3BZo0Wy+Da6hEEu9C+XOuhIZEdd4RS/yXQgXUDl0joV8F+NbEJ4GJYsFW1jdSu3hHMTA1at/QyU6HYZIA2MQ1Z4ykSJpSRLGOwS40dYQYeKcEN'
        b'O9a7888EoxwKpSukp7BdgTe1eNsxj7F/aU6w4CaAFI5JseJJAV1LYFSuJ6g3JUjb4IYn3IVrcJoztg5L57FZjkcT+R5BKaAaS/A4FGWRYp2SwvG8CipXwUOxyTfwYWQQ'
        b'3ui3E2LXmsSuHVPgAzK3yw4ddR8Jt0m/j5sH04lGsXFOpYcHHuQxwrhVhJXHWJSHD0Xviifm4JoRuUsFJ7fsdYTRkAXh5J8Y8RsruIb2bUgzHxwptjwCq1RQPwGqhTrd'
        b'nZIOTbQ9/XSvR1yCrRalJx6exNnaiAfW9JpAT08adV2wxxUwDJzBZK62nCQ+RIGH+rSqiY0hfC1gQoUiLVwgxRoNhxPwoUcEFkIFV8TQ1eSXaIR+bI+pcRXBg+v8Zwum'
        b'bHDeE8un4CVHEPV/Xkv4dKxnrU/qIWdKJwXDCZVtSgSfgHazlHwTDYnB+1yufA5mzFFaAm6m7kl4ziNk1dN8giUjRvUpbb9ZhMRIzw8Gh8B91eaFEcLsaizzyKZLXKOa'
        b'Btj/DAXeT17q8GfMNMFDYuai+Uklj2TbrSQt71RgW1I852RY5lTGtow8Rp9WND6pFdtUUJcSKzh5LIcDvnsZ7Va3nj32r1CQAtdhF+ck4cXteA7v9IjyxkBVuKj0eJqQ'
        b'ZRbf15Mr+3S5or/KKeGWT8KiJdAynYK3SRRteuIRbMUOzpKXhtD6KpQNgJoorUqKhHoVBVd38SFXaih+Co4R8+SgL7nJ3914uLHNxNMqqF6xmANTGk3qUugbS3rH9G2C'
        b'grjz3TxLlqLymPsc3BYqcWfYyjiODtSNdVpO9tqnFhzjV0CFx5RFG7isIsfhAeKrAB70YllPVwZhM6GDoEJDxKcz4i3PLlXnP7m/EYL1p7CNNiESrnAnA02alf0ggsMd'
        b'Cev4CkKUQlKbFAoGGaBQUHI3ZnpIP3N031pwKvAeya3EMZVFZj66J+eXj8TbDETvkHrRmCZOFY+SO62eTMHBAG1sFdzeZCrTHsC3Eq5MWmqjEFRoV1NPXxJdr3rdtsIF'
        b'DgTZU+EyY3bahCd3sNXNYYRT3Arn1m3jQ3bAgQy+vhJCaneBRPaguxizRgVHgpYJQDuloUCQxmTCyT7LZsrVa9nJ8R7z1pBYmKpA7SIH4/7uKDftanlyHTPhsYqCh5YN'
        b'jnA2pj0Lq/rhgdzgmmMoTdE1exgUz5LtWw6nF3on4l08JNxFaxKeJ708McAX91iXTkG214HXuKE/S/FL1QCo7cFyAWrZ2mCHKi8vmStO7nb/yHkDN61ZbNpdBd6agheF'
        b'iGooKj03ZPmgmO8KTx4r/aBjDt/j5Ro4toWynQHae12QblVgawqWc+1ZAhXLONnLQf2g2034QR5z1lDmxG3uHMsxMnq8z2AKxJT48SiyjUi+WXCU+gwqeWhfhxV4aDNe'
        b'XMdy4rvWLeTdsWkJF6ZDSuRTdGLdgHBMNdzl26+TW1zmcr94cPW2ARFWX0whQptTsmA4prKPlzlm8vCDMtTT3Gd3DJymsZ+KNzCIKzZw3nati+5bPuv0bEh/41BtmyVL'
        b'9vSYrcRmvn36xZQKsGkuj+6vrNdVm0gKCVLEGBWUU+BQK9zLacpAmyM293OQLhmLgBFuKZWWSN55MwnzShAcHSxIaRGaUar0LFjHUc03Hm6Pkw+izkKHnlXgQzwYx+Xp'
        b'Dcc1jGba6v7q/IQd4zEVnEmdpYvn+YQvNpE7qtzYl2rss4t4/vGiKYnYYeNZZgmlDVBL7oJlJ6kkmgq8EmvD2zJR3KjE1jxObRRWBUNDYl8FZTdcE4nVA6zdCIfgrg3K'
        b'Wap7ToIzFHHeFrkApenlW562WVlS46TUOzWUU9uHtfEUoVX1lV1mTBZVhyYo1cOxdX11l527RUN9bi5e2kQJP/tQKUFZnrdoaPNUQInM5i0XjB3H62tE2nR4N5yZYLVB'
        b'qVKkpWfmuDLweQuwzgcvu5Vw8ATlEmzQBgLwk9AVavNj5E7ROnMo6WQt4flYkgNn3cs7VeF8kZmK9Eg851bdSdUIOZ/0XUGkb/aVd7DTxlsmyLEVOqxu9R08kSDywzJK'
        b'Fx5uXE5NHqIGUIMHYvhCZQb9ZGztK/wQIhzkCXuBDZsU+X1ln5z1IkF1QnnGUjjnVvWBFh+RauLd9VD4ok2k1mdplfkZfCkL4Dx2pO/tq/msD+QD1Iuma/FUX3UELqHI'
        b'nMOwHClgvmfbrhIrqSiYxhvmTYYWuL3DrWyyYYarTgXX4dwGmvyOTFScaqZMFmu/jqcJBBrW9NVTXsT9Iq034z0JT9uGyEQxhWikizE3ybVdTiYu+gotAX68aRjWyaC1'
        b'wL3MUg5doh7VRWbzCC8RCvTVWhxDRM2iCpsSsYGVboQVkBhOpEGnqDsNI19/yILtPmxVl1nF4hrc5CzOGQtlUD/ErUITFM4XvDoWLoQSnvTVZ7B5m6v4uG/H+nU0D69I'
        b'XGb1o1ubhFLfhwuGWQps9/MQ1YCLaSrHOGpQwUG4CIfxLLYLfbvFygGXXRVI7MqbmDwC27fJhWSr4PAYUao6Rzn7Zbi6j9rUYsuPLKLMig1aA4eXr13hXiWKFwrnkz9n'
        b'ATmuvhIRXEniUlhOIe85OxS6FYmy8QFXoDkRyfN93GpE8cQZW2pqAZRtIrTqqxHBKSEe6NzoPSKMGlyyriY/0SmYfhyBZV54ldpUwuSOQSEUcjmQCtZQhnCbFLEdO1wS'
        b'PzkdSjhNiw2PrBmK7b5ywXk9pRItnL8EbFkeON6tHLV+PR+h9PQl2qeoQSUKPRexeQRfrC/sh5vKp9yrVHh1tVC+o8OZ+6x3r1FJs8WqSuDRVj9WolKLhjOL8Z7QvauE'
        b'mNdzsNWtfDWK1JwjxvEQOK5ap/FUi7LRJXLZRY5h1JIxKc1ndV9VKypO9K8nF9M5NEhjd6njsQ2U07G989uyFs8mute6bgvkhQ7FUqib3ldLkkMbpxVAxncZ7kRo8hmt'
        b'RgLSDXCPy2wNmUpxilyTrxYF2lofD7H8GxSrU3pR1Fc22wUPBGOVMd7Qku9WN3sRHovll07GM6SMt93qZnhyBefNkukPtSluVTMjHuMzbSaZn8Gb+FjjxyTwQCJNKjS6'
        b'RAYHXoRTqzR+TOUesXTw7njR0rUATqbO1GCbS2oNk+Eib4mdkU6TFlELG9PFNvvCTrFtF+DM9KexQ+MlF/Nchf07hf/bOxE78YjG4Spg106FFo6+aeuxyntYX9lurZb3'
        b'Xwi1ZvJfGptrA8gAlwoBPCadLQ5KJwDnuvGQtjmCxMaCoDE+yRzXi11FO2hhrr2RIjHy+FDMK31KaF8FZanSmg1qPB/upVNy1FIRtrVgWfxyLFdQbvlozUIZyezWAr6q'
        b'rePxfhyWxqsZ8F2Ub5SFrqCAk5nRqCVYE4eVoVgRqGPnUT7K4UMVo8A5hbO6jODtWGBicIxSUi4MJydLwj0DnUsN7MSI/aglcZTEj5HYyadT4idU7LSKnVIpnF5ZXq7z'
        b'KWWx8qC0R7VTvVvJz6dU/HxKuVeVRg50peSVrVO+/3uSurfW7SeKnV3atHozP7TUZlms2nx9rinTZC8I6dex34dYcWQasMVitlv48WdAz4Gp1kTU8vWmXP2mXGMQJ7jM'
        b'aN3qmsDGxvUjtUlv3qI1WDKN/ACVUeX0bI6tPQezeoPB4jDbtWbH1k1Gq1ZvdXUxZmr1tn60thtzc0O8+301P09v1W/Vmmia+dpVOeJslh3abuqlEjLYgE0mw3y2zGxT'
        b'vtEcJEYxBhfHRvXjwGQesCL2YyDBGHfY2RKMekOO1kKdrINOxNdmLXCfzN7DJony75/Hzo6pXdRCtAkOm52tkcl9ZVLwzPDZs7WL4pNjFmkjBiGSaRyUN5sxT88ZC2B/'
        b'BWiNpBoOvd3IT70zMlZZHcaMjH78DqTt4l9InKuWay3alSZzdq5RG+2wWrTJ+oKtRrPdpl1kNeqf4MVqtDusZtv83hm1FnOvkgbRt0v1uTb+NRPydpPticX0OwX3lJ48'
        b'kx2W6IKNduwcyyJJVi5wRZONUMtPXL1M46SwoMtKKSNjfUnsXIl7jGfmEtKU0R+zDWultUOwkXetfUEjjZTWKqShGbkrrLnixHb/HD9pQlicSgrLCArabZKEpxw9nIWB'
        b'wwi8xOkfnNMNES6kDYq8WFv6M6IpCWs4TEdSPMsOBSn8Py0OBuEhFnMImjgBj7GDQajJFmeDtJ5rwotc9VnLzwXxJBSKs8FEuC+OQSmt4OeCUL/ddTTYjsdFbFAG+7FN'
        b'k6dg3DziYVVtNF7giDx/3dOabdRwU8Vd/OmxMVwgBo2MnyOOmc5PEhOVYvqz6RRzttsIG69s4kFG9TLimQfQ5yZDET9hdECDOGTcCQ/59GZa2FV+wojVFPXyU0Y4kcgF'
        b'Z96yih8wPqt0HTFen8nZCltn0JBwDM9yZ3RuKIj140kvItZOq0x0UIjLcoFyPC2aWqxRtu0eEkXStTyAr8Kz0CocVTvNX8oCcizUi5g8MFmnEFHgTYoKWRMcUIumoSJY'
        b'zob6aD4TJTlNYi4PiuM5vUtZ2Xyqi+T6xVSFy/lSp+ItuM1zCNifJNIICju6dHLB4t0cKOSt0+GhK8k4sJkPVOJ9bOTnyno4JY6WKSM9yzUuOEst+eTOUEjajPids14Q'
        b'h9Hk5s6nzQxTsvM8CmuPSZvIuReaavY0qmwsXjtwq/C5I4uWRy3yKTr2+pu7tnYM2X5ZG7Jhh+eYkAX7LQ2BY6Zp/1j/TkFgg6rB81ety3YoJqFhh7wqecH+2FciTr/+'
        b'+YyvJj/dNjm8U7ttv/y+/5GfKf8ypPrjxfOs/nVjboypLtK21f/6lVfaDlV+3JLwM/x2wOavbB9N/9Owl8/9wSNt9oW/Lv7x924scO787BevvLurDisPfVx15BdHs989'
        b'9dmUVy62vvWz2W0P8p9f/WXjbusHtW8l1ezTvfDcx691Jb/8b1saP1kU8+bvfv7F3Xd2vZk9fNyOzS/WZX3wO7+v3sk/9vM3jm9fFbgoxy/qliY3w3fXR5YzM37T9faP'
        b'V13pitqUl35q7az/zHzXZ7b/u+PvfCthzLqMHP1fPtWkxBnf/fCxzsPO5X8NS6ID58O5YP+YYLmkhlPy4Aw/O7vao4B7WwJDYoOgSx6gC8GqIMr1pbFa5UYrtvAO5M3P'
        b'YWVcUjCUZCqTeHygSZFjJcVGh+zseBEr8Nx8ykcrTFgSEBwiI/KF8plwAA7beUmuYQm7D+O68rJdXHnJDw7A0lC5FLIZm+GhCm/jZaiyM32Y5YMXsewZuJgQFEsJvKSO'
        b'lPsl4hm7lilZwL44Pp5yb2KAKIpIZhQeUmBXhLdO3i3317FigaTz4r/+7jcGq1+MWpBltew0mrVZ4v5UCPO4z3d7c/xPZx9YN9tqhsP7JJ1SppR58pefTC4bTb+H0stb'
        b'xr734d97yzzlavYu63tnbWrZWP6bffKjT0rWIp8gY+UMKZEzo1N3K9mM3Qry4t0eLp/YrWROrNsjPd3qMKend2vS0w25Rr3ZkZeerlP/7TXqlFYWhVnZNRsrMy8ru8pl'
        b'ZdEZn/cEWxs7r5X2Sx9NIL7lMjV/56fAG+CUvxC+EDyci3STfaQPoQrTlvV4GMrilqcjpdFYloiVSbEqyS9PMRc6VvLD6EgWZcYnimhSJmngyup1cmzFkjThNU7o4IGI'
        b'QtNXshjUC64bFC7fx1bh0eP7IqTeK0/KLKUrfFQUKyh8VFL4qODho5KHj4q9Slf4eIjCx/dkT4aP/MKbW/xotWzV6nsivv6xXf847ok4bdXfCCetxm0Ok1UEEXlGK4WU'
        b'W0W003MLr7+/T+oJA4iRgBU0o2mrMdpqtVgDODE9tWQOHiUyfhm7IlJ8chGDhkiuRYkRT65wsClYXLk0V5+tNYno1mCxWo22PIs5k8IhHl7aciyO3EwWLonIh8e5rth2'
        b'8MAo2sSW3BeHUcyt10YE2x15FF+5oi0uNQoT/VmPIDaR7m+ESaoBYZIq0fEsy2ci8CwBVnnkE/fwsBhL4gOWB0HTKnH1j32RFB+bIGO3o0o08xb4rTK9duYNyfYcUQk8'
        b'6vVfGSEf6vQx+tys3E0fZWx86b2X33v5CHyquH1kXlHjiYYTbQcbY5qLGorCK3R1DUVT6g7M9JWCPDQX4ZpObp9CNPxG4VVNAFkCOhOwBMsTHC5gnAztSrwh32Zn1y7h'
        b'/oLwuJDlhIhQ4cI83yRpPNxWmqEBr+vk/Yz86+CNW3q3Rlzv7EMzP4FmmQyvhnPUsg7pQyFVt2ePQnV7uFRDwAi7+2dl9zH7Ta+wsiDKymBEdOPwwgj+qxu8NA93hxe2'
        b'xNVaPN9/iXgoSCHWOBIeO1jauAjuZQ9IfBvJ+x+CW1AO9UGKDXGRiXARKrdRLHQFHnpTbFDtS9HQ4QUidChX4x1Nvp9MCp0no8gTm/E8XudN08bAYU3+Nhm7GHZLhsUU'
        b'iUTBZZ40T6TgrcqGnUMilJIcq+ES1MlGY6MXx6tn4NYKWwTJKsUss0hwB5qxSsxVATVzNfn5aikzW4aHJTyFF/AeoSQveF9dhFUC5TbHM5RbGcDRk7SsKL1fpo33NlGq'
        b'jbUgLozhAeLZGUjwKZPkY+VQKYuC9rR+ANmbHMxnAKngECnug8qdnlmevUCp/Eag/OvX5dncwvtn2V8LEwxSWPdvzla/Jolkg//Xc0hDLmfLZrQPzBqfYJDJxWIwOAgR'
        b'zYaBjPbkjdHJi7RR5LqtDDGXkGcw2C1WygTzHJtyTbYcIrSpgPd0IXgUZZZWfe4AeovJOkPceNOzTXHwC+EBK6NWBQTRryVL2K+opBXh9JvYC1gcsZg3REUFBA2g6LYm'
        b'ykktg2a/bJFcznki5yWqmQy8C/KeECD7+bvcYi9FS95Ab8h+/j6P2G/z/mlJt0waLOkeQkk3wyU4DW1Te6+Pf40zwcfRA/3J6mCe54SMpsycUr+wkH221NU5It328hwh'
        b'satZYeYfRf0uIk8SZUQ4+yLuH8MzdsrXoUbPYSEFW/ZQrlsMxZIUCrXyETIvqM/nZE7MpKydIvqw0SkRu3aEEVpzQsG4H0vxARxlBcVwKTwjl1/Vg+Z9WDbVayatMUKK'
        b'iFBzEp8uHCZRCDg3bHSaIiNnGSPBAD1Nl2HBm67xz8znZC3ZnnDUVehOlpKxZCKn8PJob4nQ0jNs9O9XhQZtkVaZsn7bLrexQ7oRBaZpleF+EOYT/ZtnEroL69LubRvd'
        b'+j3Za36TjjztiLmnfXnxocz/nqT90bi5MUOif/DGt//85Zc/zP50ln5I+bDhu490PJX2p7cPPSN/9Pu9GaNUBpixPmNBQN2lrT8d1xAfu/HAtC2zF3W9L0tpq0wtPLQ3'
        b'7avF70z7zb+kntmQWi6LXfd+1tIVE5M7tkVe+uTdB44px852b/7qOz/JNLfkP353hPn1+xNP3vnlrYCWFnvcH3J+FmX7s+KDSbNeXbJP58kTFeyE/VAdyDMqk1nkVFA+'
        b'0f40E+M1rM8Vft3dqdueE24di3Ps/BpKK15fwcAcSpJYfhVKvYLZiNSoOA8pHOvVsSHT7ZNYnDAbT2visFyX4KDEuslFbxQ4lZ4mrLGz3DwNr2MjpWmkWw8i5fmyRaRs'
        b'zZxTGbansMcgQpOC5eD0lNR75QGh2Gbn51hnn8dCLBPJljce5fnWGLzPZ/WmdXSSXl2Nw4q43uRwSJgiGzuxRicTLt/zH0qyRBTiJVIq8hA8BgkTMcg+SerJqdi7nHIj'
        b'P54z+cmUcpYrPU2vsa6XdYRblNKX2XQrCKzdgpNvSooUbknRyN6AhdH+rVvAUjP+yYAFavDKjN6EiPJirJ9H7nwYOhVQnjFHJ+OGaZGxNKi33r5kjgxOG6f3e4ajN6Fh'
        b'R/jkreVZ8t5nNWRf+6yGy0d/8VY/wFohAO9rYvIsHlJz1+pezv7fTmIGRdwe6fRHXHUiB9yR0+YMgFu4QVvwTfE73ha1STneHG6bA4d6j9zh1nB+Wcbk8QKZEJYmYPlK'
        b'LI6HOrgpHx4NjXAYLsNJ+kMnJQ/1gM51WGGKPf+yzMbSiflJyv/KCHJLBNJe6rrfeKThmCxm5uWw4Myg1YH6RL3622EhGb/KSPvW2DdfOimTVs7w9eiK0Kk4XmzDm9jg'
        b'jhfQtcA9D/Av4CY+ayq0MMDx2NFTxIHmFG6pcMaEd1kZx1XDac/qKeNgA960s+e2FkP9QheEMPgYC3d6EARPGnkhhz0/Agd5pcd3hFulRzZSWJl8UFP2yDbaew15aI8h'
        b'T2EGzAsgMuvoPkNViMLD4LmDTDRyA2RjxpKZ2IYLA9wv/drP3QTZxfWdcGgc59bFK9TiNVGZSvkbFiZ3Sv+QhTX1U9CVebkmu63XjMSJAdmKln2bZdVn8xOAJ0yqxyz1'
        b'2shB89l+nf2jklITV61YG6SNiomOiluZmkCJ7qLEuPSopCXRQdpFUbw9PTE1YXH0Ct3XZ7+DWQ93xttV/Kk1qWpaRm7HqAmSYy59mACXPNnjaoHsWbeS+JSYviQEq3XQ'
        b'6A0nC+gVCyUFrPB6JlrtDcVqLOW34vAh3sIK9+FkOwzz9mikSXhNyW5J+JseLo+U2VKo+4JDDf/1l9qM9S/dJBtpOxh+eMrhtuOx1Q0nGooaDk45/TDm8qHww40n20ra'
        b'FP5Pv35zf+PBbVMMwQZfQ9vE5KJxz6zErv0FU6LIC6mlsqeH3ezo1Cl5lXMHHMajzD6UcK7HQLx3cftQYxveddN+pvq++JhpP1zeJ8qYTrgLp4UrfJDeU3qk/PIaJz4q'
        b'MT/OH2q5i/ZXS16UfDX4ZvTT38Htw5tSCJtbvj2yx0TCPWU+3Ej8RNY99v/BTNgY/35m0t3PTDg2XIT2NYExQQGJPLWWwwnujkbDfeUoj3nkqFghYkoyPhKOijLsqlAo'
        b'ZTal8VVL4/cpc+AMVg9uUa4iHH/qsLcI901WlUO55YYni3DurotXq8z6rTyLGcRjsRyGnbjlGekL8mz9fUissK1cvd1OKYlBT+6nP1HuyPSZos43IBnrR6s3MfumvEzk'
        b'Yf8XPalsUCzwTHSwGhbWFuD5r0td1uC9r3elULWbo0lMJs9dMtr1GQu2e9sl7l/NeHx8z322dDwLpc9iBb9Wad0Gxe4OdhDnOnUKUHDpw4mn5/FnTGP+GJQRbxifIpke'
        b'B8YqbWnUMqxOO/GNtmH7Vz/WDlW+9OwkeXbOS+/M/6hw9PMzRyxOeOXnv5HPTy2ZvdZQqXrjjbIPfY7/evZvy9q+/72TGTmt//GnUcffejD6xt7d4154c+4f/ppXfiOm'
        b'7rdjPv3z6Kmz/qxT2/nzMPd98WGPQ95fMKAwh3fhrp3f5G4KhFt9IfwjJOEkseoVyZTgJkElzUlU74VHIeIc5sbOrSJjkMbhfQ5Q+CjAzpzZU1Axw82BC++dAQ82KiI4'
        b'giXC/n1PABih106s8MRTcIdHEXNHKIQ7HI9l/ViYDNVK2oXzY3tC9m8qEvpwn04azeyFo9boHtSKZljlI/OWC+fuI7OOd8Otbg3DuXSLlUUEbvg16ITEzVO9SMaozO+H'
        b'ZN/qVyRkC9ydkSIW2G910YGu9Z2BTp0iMXGpTrZUJ09carr2WK2wfUE0P3O8lnr0X1eOSBnp/N3D+4239499KeS/Sx9eGGlYFp0yosb/19nJi0YWj7dvXzX8pxsiS/e8'
        b'9v6Ugs+rPg15PWx+9m/f/NO7n+RlH3wbzS1PfSvug2vhxz/evur0995Le6liVPmvbOap3b/6ZG3bLzWzNYuDC/PufNf0s2vh884cX/Kxden0V3c0j/yyK2FtdGTonvzk'
        b'8mUr31WHLvTteCclSRE+3rTJ6ztB0xI1Lbfbyv/zesa05rTvjP/hD96a/8P2AxW5m2a++NnQ996Y3dl+8Kz9ZtlPP9KH/vm978r8rMU4deK514dV/uD1tgIcPeFqmXnn'
        b'L/9T6ZVoLX37zPtBv5ibNHlM17XjcZ/a1lrWjP15wL9+mn/2GZ161qOXE4pibGU/9rE578//8cU7u7p9P389DBSTPi5OeW3Hm3OTPn3q7TdWTq/LXJ4eu6W1Nui7O97S'
        b'WOM/qV7zyZ5zb3x2vymzJnrxpRFRb5zofKPjxQtvvDLL8N6Vy8uvGNOy1v5oc2LiX2K9g+JePdzyk6IVL60w/iogLt+75a+J3nf+zfd+2+GSjDEJe+dOWTb/jcZtv54w'
        b'c8QHsyzew75K/+ilC3PgxxdeTvrN9df9s761ZuKir+SHb336ygv/tv3Bv7z86ttb2+d//u1h88e9O2bz2boPn/99W/XnmdOi2/ybf3r+j+s9Q+3OL9+u+eGHf1zx/QUX'
        b'm/a0fGC/cTT8T699vnl2+dihR48+XhLxbugHJWTODPf88O5yXzxJDk4myeZKWDlPz2PitHys6zUqE1b3ZdW74AQHgvFwBw4OzOThzkoBBHAci+yuC1uPmQul6KEiWC1F'
        b'r1RvlE/1GWVn96fkdmgNXB6MxbHxiSpJ8zwehDY5nvVRciagcBmw61VYRT2wPJZ6zC6AG3Jswode/+A5ps7vHzv2/Fo6KivzGYO+cYTwTE/Ptegz09M5Ovw7s9mpcrlc'
        b'FinT8vPN4XJP5WiZ+OetkpMFe/L3/3v/POXDZeyfp2ykglUcJrwgpxWMHOFNqxkrm+Avl40fQq9hcpl1Qg9KEtDJ09Pd8M33/1/iMuvEXjBkE7HnicThzM+muwMhV5nr'
        b'Fm8ogyqsYk4ZSjzwKlR5SH7jFBNnepgebu1U2U5St9p6Y3DZc96wcOShX2yd/XjpyCDl918bsWOMxqBb8PZnP/DXRVYcsUOm5ejDxvtPv/3m7skXL+zIeGX/2p3/YaxZ'
        b'9OGShF8urf/+uuyRdz7d8NXqDz8o/G3O93/x+a9/5LlpZMiX3gkPPFt/meg7/WTc5L1HPzd9cGDV5q+2vv+HU4XNn/3Cc/rtN7su5H3H907kT7Z9N+r+O/GfJL0f9n75'
        b'rb/KJ76l++lzK3W+3KfhwSVj+f/PkUQLqYQDWB7nQWncLTleg0ez+NEXVkPXJBYxtGEJVCUkkZNlt40eKKABHsMjV/KbnCOkwRwCBblO8sJMHMMVk5ZO4ZmzORjvxyVj'
        b'RWxCQIKHpFbKPeHEEO6S92IX3gtcrpJk2IJH4iSso+GtdvbYUhzFveW9wZEVbiT1lHtC4wgHKqmxSiEtgzYPqIpy8ZKPF+OejKfU0pjpo5coA8xp/BbDBnsktmM5GXto'
        b'wLbgAKik5J9hyniHEoqgejaHDLg+EppZRkXUPNjTqZIyWAYt4R6cRHQ43uWeUDDyPFQLXp6C00q48mKawJUaKF6IZTrqxvUEH8gJ/oakKFLxiIaDG96BtrzeHuWZQWxl'
        b'PIGTSVrsUEnQlMJzoz3DUgOTgrAUy6ZNE5uEj+R4Zxlc7JeZTPzngM8/8Y0yqa9BL5PZZHehF3vMRvJl8QzlYwqljNk/y8mG8hiHRTneimdY7BNqndSLAJO7FblGc7eS'
        b'HXl0q3hW362kDMHercw0GeidshNzt8Jmt3arNhXYjbZu5SaLJbdbYTLbu1VZBJ70y6o3Z9NokznPYe9WGHKs3QqLNbNbnWXKpdylW7FVn9et2GnK61bpbQaTqVuRY9xB'
        b'XYi8t8lmMtvserPB2K3muYmBn88a8+y27mFbLZnz5qSLGmumKdtk79bYckxZ9nQjyxm6fSnHyNGbzMbMdOMOQ7dXerqNsq+89PRutcPsoFSiD9nEYida2WGidTZ7Yw/n'
        b'Wdkja1YmNyt7usrKsMrKqitWFhNbWVZoZeU0K3vcycqeKrMyY7ayIM7KTMs6h72xswMrU0Qrezjcyh54tfIsgVUkrKyyYGW5qZWpvJU9fW5l5TZrWC9O8iJ1L07+cYkb'
        b'TvK2Lzx7bvJ0D01Pd/3tclxfjM/q/78kac0Wu5a1GTMTdZ7sjk2mxUAyoT/0ubkE95NcqsOCYvrem8Rvtdu2m+w53epci0Gfa+v2cc/NrM/1CNDtTejfAvFfMT3PdJQX'
        b'zZRypcKT6VjcSOaTZP8D57LNhA=='
    ))))
