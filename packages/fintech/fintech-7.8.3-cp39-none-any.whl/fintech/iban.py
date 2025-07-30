
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
        b'eJzNfAlYVFe27qmRggJEcQZNGScKmcV5FiEgk4gjDlAUhZQy1uCQGAdAixkEJ0RBQFBRUERQI2iyVrrTnc7tl9zuvp1Lj+kpSSedHpL0kKQ7b+19qpDJTvq9/r578atD'
        b'cfa09t5r/etfa5/jL4VhPzL6rKaPeTld0oQkYY+QJEmTpEkLhSSpQXZZniZrlJhmpckNigJhv2AO2CE1KNMUBZJ8icHJIC2QSIQ0ZaLgvEfr9Fm6S9TaNXGarJw0a6ZB'
        b'k5OusWQYNBsOWTJysjURxmyLQZ+hydXp9+n2GAJcXDZlGM2OummGdGO2waxJt2brLcacbLPGkqPRZxj0+zS67DSN3mTQWQwa1rs5wEXvPUj+Z+gzjT5qNodcutgEm8Qm'
        b'tclscpvCprQ52VQ2Z5uLTW1ztbnZ3G1jbB62sbZxNk/beNsE20TbJNtk2xTbVJuXzTt9Gp+36sVpRUKB8OL058cdnlYgbBUOTy8QJMKRaUemJw76HkSrRfMu1Mri9IMX'
        b'VEofN/p4MoHkfFETBa1LXKaKvk+cLBPkwrYkFyHFr26mk2CdRTejA3ZiKRbHxyRgEZbHa7E8Chqhe/MGf6UwN1yOj/HRNmsoVcS7UDGbqlZg5TyqjxWRsVixZeIcalYa'
        b'mBDpF41lWBYVgyVRCmE/VDrvhI7tfNh/rFQKroJqgkqTEvPn3P2CdTfd1ITgcexydkuIpC7LojZHQns0nPbBIr/1sXgqUYXFkZup56GD+UTGYEVcTPxmHyooCiRREyLX'
        b'b/bxj4zyk0CbXLBA8YSFcBNteskwJXN3rMnGr9ikdHf7NkiKpLQNUtoGCd8GKV96yRFp4qDv9m3IGL4NzvSJHbENmeI2nMtTbvhCOpnWICVGsniiwG9ql0kz9grsW0pM'
        b'SFyOePOvAc4uGpmG7qX4/XjsLvHm55Hy0LdkHmQ4KX43EpOE60KmC9ue1VOkpar3ZgvCO3P/JO0J/p0pUZLJ5PCaWyu57SRogqZkH3o05z3/PIHf7vP4eMzpMRKfPwhH'
        b'Y0JWfDM2WugXrP5UsDQDOmlPaE99fLAkMNIfS+A6NDlv8qGdqfQLiPJfHysRssc4r4CCfdpA6wRqE4FnvcyutOh4HkuhVICz06HIOp6JdSYGes0mBX0rhW4nAYpWu/EC'
        b'6xxXs8mJbpdjN1wWoORFaLZOZC3qoAxtZuxh36ugd6UAZU7LrJPYn/Ub8ZEZKmhFsRGveQlwCe/BY7HsJbwygcrIArAJzsUKUE+3WqzjmLJpscWcx2SoTIykoXyn8CZQ'
        b'Cu1YbcZOJZNTCBKgCkqxgM8ILmknmq2sySk4Dc2sbt10Ljg8wHbsMLuxRg2yZwWoHeNhZRud7rnIjF1MtnN45jnqbPoe6xTW4CpexF4zlDEpL8JtuC3ABbgPV0S5WwLw'
        b'tlnNxL6MdXia+oNKvMiHmj8NiswHSH/xLJzAAgEqlF6idHfh9lHzGNb8cgDWCHAee7S8ZOI2Gq7LjUnRHoQPBWjA5um8JB5bPNV8I25gPlRTGzgvFXs7A017oJT2T6JC'
        b'm48AHRuwl+/FMnwAHWa8w3a22pktQyWcdOOzImlv4wPsssr4glfgSQFO4xVo45KPWbxRjbfZYLe2bGVb0YnNfCwl1GKx+QCbbjUhylXaDZdFfCwogtIXzHiPiV6LlYEC'
        b'nIKry3hvK3N8zGP4xmI1nKXVW4E9YpvbUIg0XxUrvALnpALUee4Q1agRH82mEibDVTg2jYTQY59Y1LWdQKLLwopqocvMZnU6govnsm4HdrkqeZsyrGAKVjjL3kjiTEVs'
        b'Ja5hI9vDeqx/kW9hUjStfxd2Msmbn4FLpP7UYxtvtgVOKQjnWLMO7IJ8ARo3wWk+1o6l2EBFfJFWsbGaUuEcL8FWqD1IRWxpb89KFaA5CerFrWqBfKykVefaF7KTFiki'
        b'S5TvNlx0oZ2X8K9NR6i7eKzjRXunzyDxulhJG9Tn0RrheajgOrsw1MCKmB22C7tpTrqt9t700EM7KMrdtJMtxKMXRKs5Dl0r1CpW0oN92MxkeoTtXLyYKLirxjusu24s'
        b'XkcybCE1ZyUJC/GBej+baztpAC1R7V4sFM2jm5ChQY09bPk6IR962WBXsIJvvQTac6mMTbcL65aSPjuNEyXMx1oXKmFddkPJPlpY7MgVTaoPazebLUzCIixgcHQSH8I1'
        b'PmEscZ6lZpCMt7AgnIzgQAa/Pw6LsUztwsZ5kELDtMpmWZlnnwE92AClCwmJuqFMIciwSYKPoTMeH2K3lUBcOLwRbkLpfjwN5VCiEOQZku1RcFxitWr4cFAMD+3FIVjl'
        b'fFDsxhnKpZM2wF2tjAPUHIKxZiyl/c4hI3fJeX4yF+oQVa6OJmFTGTS1pC6H+/w+add9IVrJ3Ap9PZ6WAaXWuXR/URaewBosghsL4bpCFwvleGVvGGlPrBBqXgvdCjiD'
        b'ZdBr9WGS3VBhq6NyB57B0/xrKNzAM3LBO2kllsudlXhWrFzy3GyxLvTANVY5EjoG6o4nq+yTy+DsTF4ZCHZDHD23D+r5Jq8NdWOwWq5UeVp9qfJarCDMrYmEmyTyQN0Q'
        b'NgirWw49/jK8T3j5knUeE6QAm/HUgNh8jtA7Ddv3qjWkRte2eArrNU5qhpbWQCZLvhN1NWKWRB+K4RaWs7ttbCR/kyJvPd7lbcZHEwA7JCrPwSpZKh9lL23RBVpQKKX1'
        b'jMT7StLxQrhrncPkKptKfGbQNNj6yIkRnd4oeGGXjEyyEi9YlzCzx5MzBq1l+aBVwu5lfKGuxbJ+bsYqU2OFPLilggc0/iNrgMDVtiSeDdTBB4K+6ayhDKpJf8/AyXTS'
        b'mAtCMDYooALaXK1ajtTJYBuyH+Lm8Yl7LyV7rpFhL17P4DoEd1UE66PoxXVeXbsKbXKnBbl8pVKysOVJ1fJh/XPlCIVH0P2Cgmy++oA1iElTQ/pxfEBLBwag6uXi5Fmz'
        b'kPSNWKmAy9ZEriUv5tLiDNE/u1B2NSkgtG+Xq7BOzuUKxybvESNQy5tepINcTK6K/mSv5hV4R9SUerTRbXurNtaKwPUQXl7E1hVOagjLPIVY7HMKwWNwiWvjCwfx/lB7'
        b'Iy3BgiSfhaJg5vkEuA0qLJu4lVOrFMKoy44GNwamoVvl0EW7WGcV5lVOfO/iIT9jYOsGLDpMQ6vIdD0+PA3rnQKgQsOVYyM+XP1Ec+2D+MDjgQXgUgXAQ8VeIg2isV4i'
        b'JlJvb9Q2AgawbdxcGT48kMClWTSP7G+YkoeyLZeTkhdR8x4ZIThxKr7T+wg6zwxTj+vD1QOvTcpTkPtshKtcnqPQEfpEvcW6A2hwDy/JZHiLALWSV1466Qne3RqhFdi5'
        b'CZvlTnjBybqQKd6DOeQzhonjDccH2snhjmvsmnXQPkcw4RkVIX4B1HDr3jiXpjIMc/aGaRRCqIRw5LICGqi8QlTvC6v8h27BYBviJjd/OZGyOgVUk1sq5bq3dCp5kwF9'
        b'LR9QQL5rl50Wykgyt70LJAkKp8X4eCfXpVy8MjmawwTVLKK9bR6qIxz1N0K504zZ2CiCeAXh0YMnwoVmcGDjlRmkzWcOomL/Ir7VxKyuQtPwzQ4RZ+BFjgk7aSc20qxZ'
        b'EDk9irBxMGZw+NuZuJE2LZ/0hzhpJzdkYgpFyUNMc8gGt+JNsMnwJTnB6ixOhLBnxXAhpHgdixis3iNtE8LEud3a6z9SMztEzbwzB28ztSkmlsIh7uKiyXYda3NUJkYt'
        b'yiAjJZbh3VA8YZ3POn6Mx0n6UfCwY5D7CIbKw3hBAfXQCuf5lmJNJnHe4UsS6gB8e6v64K0KqHLBm1yucTONQ22dadmArW8I8I9xWgIN+7iph82D3qF61j58KvPx6mx4'
        b'rIBKwyRrMCfYWXuHNJGStHV6+zgeNMz9hWOhaIEE6la7xEH+XHFl85GFg8M9tMPINlLsi/fw8QzRO7VGBY4C7fXEXm4MRjirIherVvJJj4W6lJE7x8HBy5k6eCDDO/Bo'
        b'N5dli5A9qhcQsQoatuJjuftCqBYFryLndH6kBnMJvKZHYYcMOyYSCWV6+Sy2zBmB5IPWnrSn189pET40iGrcAR2zh/iKITqEJQamxo/9iJcxJcoglCgcuvRYqHCsPHQl'
        b'URBcuBebkwTTPubs6wl3mH9JeG7VIBU6SEx8YMaKcXZPf5O8JByzcPCBC7PzRhAvWqvzZFaDFc8fahQWaPLimmp0njC6ux+kqOYd2EgoR7FwodWP2kyD7qAn0y+fZx1h'
        b'HIq8BZINKqeFwW4cTlwIZ5sGiab1sy/ZTUUqzT9WCJmkgLJsOzedkXh4iJe0L67IH6mfMrgjl2+He1yB8KWDOArFs/slb9ejWCJXHYoTvV3fesLAkbpsd3b5Pstk2BdB'
        b'MMHsZY2U1R2uzMNMmED1LtYo4CKcXKGN4SGLkiLS4/bwIyuBgg+oDeAx0HQsfMbMo05Sh0wBbKQUpTxieTEOCs14V8IzHsVIwXkFtOBxHugcJZ97y55cIUEp3jq7C8vF'
        b'8LeTIshGM5Sx8Lc+WEHINg5vi0VnKIK9bzaxSMeWhucFGqtrDY8etj+/2JGQsUEBwUJCJL+vWIPH7CmZRd4Ul+PFtXw+q7bBTTPeET1I5RaBwnQ1j1qiKLw2u7Cxzx+d'
        b'SSNOy+RDJ5DARWYoYUM3QE0ESQWFBr4CVjUWODI7eH2sAGVwLlaU15aEtWZ31tkFqIqmSWK+PXSUS6MGcj538DJRFg1c5MuWRbPsdeR8KLC8yFjcwylifPgIOjbbkz7w'
        b'EjxkE7JFikWXkrDekfaJhi4KrnywSix6HBhKJU48M3ATagU4nUG8nRUdpo22OVJCtXiN1gFvT+ASekNXpj0htJlmB7Vkkm1iKNqBlXkDWaE+sNFYcVgrRvl9aXjKLAbf'
        b'l7B7Is358By+E7NXr7FnhALxFHXnSXyTJ9Mqg7DNnjyZ4UEzGoeXxYJTpHPt5gNMuDO6PQKUzw/jBYHQ8rwjp7KX6c6pjVvEwS9G0ibhPaZWF2NYjHx61Xoxvn8M50kb'
        b'7fmWFgr9L2AXiLqIt6xG8xgJT7bcwBa2sy9Bi9isDHt1jkyMHKpYlqECOrkUaxdQfGFPxaSTdPXpUCAuz52lxKDtmRgD1LBwtgptvOww1pLn6RKt4jK2z6L1SSHvyjr0'
        b'jV6MXa5sVi3OUExDwYMlvBGLXa47Mji+TLsv0b638kCdFvkadA3kcJqggySBO95iVq8scjMNxlMXLaFktRdyk3jBYahfj13u7D75gMUCNE/fx4faDr0LaWG48t0xAulD'
        b'K21DibgfVxalYleelCf8avJoWnpfvoBLjtIa5Sm5MDVI+lpFGtLBxSPRSmjKjjwSVITThLPxBteIfQG0F/Y00k4fARqjU/l9C5yOduSQktUCNEmncQF8oHIggRTNEoTN'
        b'G4+I86xIXehIH21nynVKK06HorImdyoRV/t6sEAh5Um4LipLBZzLojIFt8FSVwFq4pbz+SyMoYl0YTdf70V4lel+SThvtEVLBtLlxtagIwsaBbg8lpwta7Q5fYkjUUVT'
        b'vkJSkzKJNjH2ANGaLjc2UOeUMBIbb2CTKN+lRJbZdKSxLqZzBUvmZcF7WIE9jUWstZw2No8IHFuhZZpsNd5m8rVv1jCFrbTwkebBnXWOBBfkz6D+o4mGcaW8lwQ1apWS'
        b'J7HqsE2AKwQmD/jyrcbW6fbcF7QSSrUcxEqxURM0O6stXCVF1aqB03br3DEZCxxZsalMyZv0OnFdCyDfzZ50ymDxZitU60UFap6M9er9rLvrAUDzOaPbJhZUu2Orej9r'
        b'cmPPbAHOaUkybpo2OG2xZ9hoRhw28AFfAvcVoY70mn8QTVQJTfy+MTTQkVpj6T9oUM7kYySQ0t5xpNZmZJC2ZQji4KeXQb3anU2/F26ECnDNKILtRCc8rnZn2vaI9LRP'
        b'IOd4ER/zNhspOL+sxk6+ZkmHqDPVWF6QDLfH0H3W6D5coYJm51VijrMR7mvUzkxxerGaSA5cTRc91Jax7morT23jsTk0d2zfxLtytsAte1JvAYOD81Azg3c1juKNy2oz'
        b'X3kyT1LC+iOzRHUqpF0qYBDO5t+3hnzRFSjW8ZMuqGDhD3FeKLKn9aDdTvOgiGcC5dA1Hro2QelmYesuJTYEybVy61QWyVGM+hhLY4hmyAQZqQ3FZsSn8aonF1SvH0/C'
        b'NURjSYxSkO6WBEJTpNWLCrygZVI0VgQSl5oPl7TsMMvVQzaBYMB+KNIFJ7LmxflHygX5aiw/JIE2aF4QoWdnS44fpSAePPFDp0iBn3Ox8y121sXOuGQ253Rn++mWvEhe'
        b'ILyoeH7cYTk/3VLwEy35EUXioO9BQposUXBO18rf+QPthotm0E8YOx41a3TZ/FxUk55j0uzXZRrTjJZDAUMqDvkjSjyV9d2Xk23J4Sesvo4zWY2RetuvM2bqUjMNfrzD'
        b'5wymLPsAZtZuSFepuux9Gn1OmoGf0bJeeX9ma5bj7Fen1+dYsy2abGtWqsGk0ZnsVQxpGp15SF8HDJmZAS5Dbi3N1Zl0WRojDbNUsylDPP5l58KpA70EjNYg1ahfyqa5'
        b'x7jfkO0ntmICro0KGyKBMXvEjNiPnhbGcNDCpmDQ6TM0OVTJNOpAfG6mQ4MHszjEpKX8+uNY2Em4vbcATazVbGFzZOueGO8/P3jhQs2amA2RazQho3SSZhhVNrMhV8cF'
        b'82XffDUGUg2rzmLgB+spKZtMVkNKyhB5R/Ztl19cca5a9rloEo3ZezINmnCrKUezQXcoy5BtMWvWmAy6YbKYDBarKdu8dGBETU72gJL60d0IXaaZ32aLfMBoHjaZEQfr'
        b'KmH4ie7YuAjOhMMyllrT7WSTaNlKaOdHtepDUwSKy4JuOx8+/EFsnmAdy9ClQI+FUBrOzHW7sF0/lVdtzlULhBCqPxj2Zpr97ee/31OPEbwFYfKbm3Jjetbk2EH4GIHa'
        b'2VUpdoZIOH8gXjuGw10AVo7BS9DypAiuB3L8SCO+fZ8QsNh+nEgYh2Vq3mgZ1MiJV9vsx4mEnnpsEAlTLbw0m2KgS44DRXaa2IoPxTOInvnPxG2wHyiyA8hbeby7nVgS'
        b'DsehTJ3LBrrGUPpBpEg9ujYvgXIvdR5nJeS+U+CC6DtvERGo3oYl9jNIFl73QInjjLZ7B3tEALvMDKkbGS95eFAExXKs9CJWVug4oSSeJfESWRs1KNyncRxPErvd5c3F'
        b'CzsCLYl413E4SQ4hiSpxt1P2LLQ+AxfVfIWIxdcnEN1lU9UvnRe1H7v4VOsYZatO44OMp5tYutF8gPmXczT4LLzEu1I/G0Suy2Zn6izyuAd9Wpk42VqiVQ+xLOhJKVyD'
        b'm3bqjQ8mjSfX+WQs2sKzYvA4jbp8iaK9gdHw6hSufCHKrA2ejhiDmjgv1ornul67oCT2uUEl1HOL/XAU6tI84LjjUJpxfFs617mw3expDcGjyt+U6T02QRCF7oaT2An3'
        b'sWZ+EHVGHCaVaPYtY1Vrl9zMmNzcIPmKquA42RrX8N/98Y3snxZK09QXfDa6+Pq6xK0OX/M4cuy0E/OeDU+NWOuyfqq0+nu/Vj10e+3nky8em7nu+29HFLd2/qzh9znb'
        b'U6cE9Wg6C6b3JGgeOx90qw6Z95z7ivQjfVXfVxSvaIuL8f486OrhRbKP/8/PlzxnXf6NX8/M73N694e3M9ZNW1u34c7chLfkcTtfLHTOjPL50uXQs4eS2o0Na5cffOUL'
        b'fcU3yj9u/FPgr+c+d+T9Lzb97d6fumbmlKk/3dZ7bunvT7z6m9/taljfh4cDTh1/rueEMeIfgXmXe+rkWzt2Oq/1fK/6Jylu897WPbDWf/Ja3+6rId+YO0vZEK3/IOLi'
        b'TS+c2pL0jvJBrW3i5KTJj76U/MgnfUdShdbJwkPaG6rcef4+kf5SwQUvKuGC1B8fr7SwU0XMn+ECVZp5AVF+vlqyWj8sJjPXyHdjIR6zeHECSHofHe8PxfGMLBj3CeoE'
        b'KcXf3XjawqOFgpAV7LkdX/8AiRC4Ugn50vnYQ4U+nKV2EU+neGKS/QGaA+IDNPv9fbEkUCoEQJ8C7+pnW/jeXtjHHveI9YvCCuq3YYwyVOoevcTyLBulT+UBJ8EWLbYn'
        b'0KgUqc0ELJRR5Na2Wivtl/pomboKWmf+62tfGKR+NmF5uinneUO2Jl18RCuAedyV/S4c/5PZH6yaeQvD4KOCVi6RS1T84y6RSiZKXOi3C/1j9135fReJSqpkV8mTKytT'
        b'Sibz3+wvd/pLzkqk3hKW8BDiuDBaZb+cjdgvIy/e72T3if1y5sT6nZKTTdbs5OR+dXKyPtOgy7bmJidrlf98jlq5iTEyE3tAx8Ssy8SeFDMx6OfjnmVzm87mdkz40Jvk'
        b'lkqU/Cr9QiolFiYR/sH+ss5ke3Enz/PJPpzD5mF7cRO6CWLY02mKBVgYzRJdpXFYkQTX4qMUgnuubDGeh1Z+5L4dz8yKjqHCQDixliinRFAnSbFjg8YRyfdgAx7Dnic8'
        b'FfMFvWyQO2STc3K4w5XCwDNV8nS5nWHKimTEMOXEMGWcYco5q5QdkScO+m5nmHuIYb4tGc4w+WN3gyimKSdLo3OQwqH0byjVG0blNv0Txmky5FmNJpFn5BpMxDqzRELk'
        b'eBZwKCWIdzAFEsR3I41ozDKEm0w5Jl/emY5K0kYnkkxeJq5IJodPYlQWZZ+U2GL4DEcbglHPiEzdHo1RJMD6HJPJYM7NyU4jxsQZqDkjx5qZxhiVSI44FbbT39G5U7iR'
        b'TfkJVSNartOE+FusuUTB7ISMrxoxSR9Ww48NpP0KJqUYwaQUcfxwPNxVP+IRQyzC4hjf9X7Qtkl81pDdiI+JipUIsji4AcXqJYlRm4yXgl6RmVcwBuKZ9UFKwG+0ukhd'
        b'Znpm6ocpu19++5W3X6mCu1VLTl4/2+jz+dnOguuRN042ngwu155vPDnj/PEuheA3W/1K/C+0Ug58L8LtBLUvmQZ7LCTWynDTy4WQ8xnokhPjqMYuywyqtgGrM6MD1hN2'
        b'Qjk3xw4yGzLJqXBXno09cFcrHQIGT4NBjgj9avFJ0yeo5y6iXhrDtXEc3UxjnqCVol/l0Kp+J7t+iHDjyi7sMdAhw8tMjH6aPNjFeQCGWIc/HARDN8Y9HYa4S7gyFauG'
        b'zLmM9qDUPme4hFet7GFeIoS9eHlEEM0eWSiEO1AGl/1kWwJ3RYdCRR60Qyv0uRCnqHbDS4ERIuWoDsKTeMVXvd+dBCDGijfwNHZzYrNvgn8AnFXvz2MlRSzHdgUa7EnD'
        b'+xPM2DMmRC5IsRoLlkgmEl8+K6aYS6H3AOZDgzmEFlCSI8A9NV4TIa8O80nrzo5X79+vpD5PkFdUUxwu4/xvdfSMWfGDsLAT2zg/Xor5cnvQvjhuIGb3tD8m2I5tk6Tp'
        b'8whlJYIUKiRhAYtHQOhARBHBIFTGQVR8JFVqU6WrBqBU/rWhNIOg9O9PC9Y5BgwN1Z8KJAx0WPWvDnmfEomyxv/jgag+k4tlNlhGhp7DBGTrkqPXWwkzs/UjBXUEn+Eb'
        b'1mjCyP+bGKauI9+ht+SYKJzMtaZmGs0Z1FHqIV7TjvFhFJ6adJkj+ltLphswSDYd2xQrf3DdNzFsk68f/Vq3jv0Ki98YTL9JPN+1IWt5QViYr9+IHgfNiQLbnFFDaDZJ'
        b'vs65YuBMvaYxeD+UO2wB2c/XcpwDPebkjvSX7Ofr+cwhm/dvjdwlwmiR+xiK3JmzOIJXKar6F1wOOyuMYj7nCJ7hAdMnsslC0Pg/yoWUFO9vaI+IkXvwCk9hVmg12XuK'
        b'tyQxWuCBWuJUVyhl0HBvBQX+cAbF3N4ibHqRsKkIikKgkfyjp8QZr3nybrKWuAve3quUQlCKX/jWMYTn4kOMjXo8zw6W4SLeChaCD8MlMbXQAHWJ82mO7lgZIoTsnsE7'
        b'2RHsIWhSDkuE3BS/X7vNY52wyrPGr2ZdHMVO6oHiihax61PwAGxiKr3XbYOwYfos3onvDrUwPvRTqeCR4jrB00vYZHzd009q7qaiS8+lxxpmVwS756/2CP/S7zvSvTcz'
        b'31uev+cPLuO/WZHq4jmuZFdq01sRqSF/9k5533+5ymaaFPIfn3/8bvyjqu/U+qoOlf21avKO0v2fV2z79JOmz7fc3bp25oq8tQ+/9171j055vFt2fvnqccHVn77+X2MO'
        b'+n/z6swI06dfTPrpq3f37Tnj8umrUc0fal59SX5V/XlZ7P2pZwMuKuY+hhdlk45v3fr2zz7ULjvxkwtd93wLStrrXo1765exJ37xJ6dX/rygZsHrWpUY/NyencRjtIXY'
        b'IBV4jAYP4SLnAHgOupYNIwGB0PCcgwXM2G5hDwelh8ANhvIUqbFwLZAq+bMG0U5CMMVOp/GyMso9z8Lc61pPrFVHY5nW3hk+gmqpMAFschWcnGvhRwLdcBuLKfCLg0ry'
        b'G/sla+DkGgsj7TugLpRFfIHx/tgHl0jaI1JffIQ1fCKQ7wUF9iguiIIAFsTtojJvvqfPz47G8mgt1EOtI9ocEyTb44tXtBKRHKj+pbBN5CvOYpBG7oKzlSCRrRwVBEeU'
        b'xq5SirZceVzmLpFLWfT1LH0m2z8mz0F85kms1C8j5B5EY74qzJINCrPGD1Ab1vdHg6jN6alPpzbsTR546AftLMQ6AM08yuKhtzAWbTIoS3fRSrjXjwnVDErw47EACdTB'
        b'HawY8c7JQHy0VODxkTRdOvBuieRrvVtid+iffXcIum0U0fEpFD+dM3Tuhwcn0P+nY6KnwrNjtYbCszJOZJGte6Hqn6CzdOko+MzAWYI9nCn6x0DlQF42n+ymBE8t5M/P'
        b'7cRmuEd2hiWxWJaIRTHSceFwHU5AC3ZNg1r6rhU2eDhBD9rwgjH+TKHMvIyavfnGnQ9S/AYFF9tevl/VWCOJnN8S5J/mt2WeLk6n/E5QQMr7Kdu+NfmNl2slQuJct7l3'
        b'nMoatQoOK7OwBG4OhpVJ+8SsjIgqa+Aszx5hcej+ef5roJcnkERkOmfgSOCxIHRE5ihu/e7lkRamxWPgMp4cjDIiwuAlqFdlQhPPLh3AQqx8kl1iuSWNH3s+EHpFW5SO'
        b'avBOewyWAXP3cJj7DGbmPPEiMU0cMOfrMjHhMWoscl0iFnIzZW0mk/GYNaKZHhN+6/50Q2WnbPugbr8o/bNEs+0TYPx94lcYodQm/D8Z4R4ywrYhOpyYm2m0mAcsTTzG'
        b'IHPSsLvpJt0efiwxzOoclqvThI4aQQ+p7BMWvzlu08btfpqwyPCw6MTNsRRar4mLTg6LXxfup1kTxsuT4zbHrg3fqP3n8fZoBsbduilezPYGpb8j122IFXgQjsdnTMDm'
        b'aSzrPo+91VcckxAphjksyMFqLVx3gdpD9CEidIgdKLtAETvL589srmeBFzU1YpujNVkXx8vpeE0OTQvgulFYcFhq3kC1J1QcnPDtzkcvux3TjA9/60CjSf78uynOWzWd'
        b'W/WfGkPn/Mw/JbFzxWvG3z6fV+ISH9kW8iCu52+XC+vUz1R/P/971ye/MN3zy+CkD5NC258pmzT2ruKnWjl3o3BSDo/tyVeynTn+Uv9NntwHu0KXK1nItZEWosLuGDG3'
        b'+ggaDg9kRJWh8HCq1B0v+fDCg3hsbDR38j5KAZvmOE+WQiPY1ENC7dHNx4WCEvOg8H68w4KCVdxFsqQmD/KnDliRadLw7iYP2A2r5TPEbvr/id1wB1e/MXFepJ9vHIXj'
        b'3fjQkUCcCA/lE7AkQysmGrERiuGc6OMogK8MhBKGEls2KYWpR+UZeB1Kn25m9lwgf7tyIBf4r5haIQWwu4bnAge7PJ40y9Zl8VBpFE/HAiV2NphroBvkEYf6nijR4DJ1'
        b'FgvFPXodua2hnXIHqEsT040jIr4hfQ1Ef18V/InB3v9WDywZFSBUcVbm75Yvgsd2BzxP+TUDJOaA4f42DjC7oik6OrxbQdHRzp8F5olHmB6HoYJ5ZVe8Ih6YQl8wf66U'
        b'vZm2jTtl7Ikf7pcHO2U4kSiesEqdBNflWUoKcFxX6VYKxlkRbgrzNuZi7k6Y9nrn2GMaD/nLy6ZL92S8/P2lH+ZPXDnfc23sqz//nXTp5uKF2//Sqa9QvP566W9cz/x2'
        b'4UelnW+9WZuS0fHLv004893eibeOHJ6y6o3Ff/x7btmtyPMfTfrk84kzM9RapXgy0ox9eGp4dMCd+PMHyI1PnsZPYqDFHVoGRQfxPC2PFdGHoItaKYRFccojcHUZhxas'
        b'wRuHCLQC4f4Tn18FLeKR0T28tJy5fayCi0MPjfbHWRgWLIzbzEFNs2MorO0wcIm3z8Jz0UNk4AI8A9VO64kdYP4CRyzwVXlKV04DSKWZwXAkm+hAsnCGX64SF6nIB1wl'
        b'Ju8BLNPK+tUM+5JzTIxEDGIGow5I0kwbwDrWy9IhWPetf5KnZKlZnxfg0hTr6BOm6U6N1Mri4iK0kgitNC7CmP5mmczMnjQ84eG/uWp7vGfC+Nd+3zd/V6v/m2v9f17x'
        b'uftHXv/le39mRIJE0f5ZV0pk5PdX1tZOig45EHPhr5KDGX+/Um+cu85sqvk4Od50tOXo97NeaU2a2vfO4eSSA2/cH/fhJ7nXK/P03z3rseeNRT+oCNy1JS1iwn8nvVGc'
        b'g3/bkrO39+w/rk/6wW/Ob/nj2++0zvjhfwY/vLnQnBgVdjop8VdfvvetlpeFAtesZcebIot1ET5dpS7NZcHfzf7z7XMvfviu4BRe+3MPm2EZJFTk7ezxvPir8VcVDe/4'
        b'vXs+reTjnT9/9tysZc/+yJCX/I7vD+9/1y075D/8237c+s1phzYnfBSCfn/51etXcg0ffXzMtvwXwfHnf/n+n8ck7Ey7+f7iXQtubNk3b86bx/+4OX9e/qWXP4197dNp'
        b'P/vdhZe/+K/kd2v/Ehuu+Ka7deOj9/fuO7yifd31/jV13d/46cHl+x7ePFG7wTbnDZus8UeRH1+ctGP3F/vW7H3tg84392+btOeR7uC3b7x6quLzQz/5wanPXnv4rXHf'
        b'6X2n/W575EfR12bV1qhP3Pb5se/vP/tb5F8Se3M+uPLwu7b2zFvLPm5IX/f5t64+mrikOGLV3L44/PX88ll14f4+OX8P7L/S+tELfyOTFB9phQeLyW2RHizGOjghYMX8'
        b'RG47mhXL7e4eiycP8fhX8KaF+7x8N7yPRZJRDZpl/O/HcBvDa1tYmE3MoNxfKSh3S4lI58+kbq6JRtqGtxPmrffHoig8CXdi4hSCGjqlxL3LsVms0aDdEc3glOocxfNY'
        b'FsWq3JJiGxyb8S+eoGrd/7UD16f2ozAx/B/1wg1elZycmaNLS07mxv4bZoIzpVKpJFQy/UuplJ2tjpOqZCoXKTPFvytV/Pf/vn93lXEeEvZPJRknY3kJ71VSgqjxni40'
        b'l8kSbx8pK3HnVw92NU13AB9hlzQ5eRBkuf3/r7rE9MwAvrGBmB6a+f8u8rM5T8c2pkR+eGMmlEIle7I9hvldImyVToL7FNm0lRHG77hnKMznqNrvnCv9S1e4wOrxhe9m'
        b'LWwMODo14bbHuldm/iogP1W7/OascuPpK+q4P0/877qXvNIu1P5ev2l8/CfvBUXt6/3kP799+przT1ShSR+U/aL+SNshQ1xHRtzErH88UqWOD3jkEturys747dTmmJYx'
        b't771o9A/rZ6498us9//4mXLr+x+q5tx9435rLvofCP3xxy//Ut9S+5uwd4J+UWb6q+Tlt7Qp0z7UunFLmH8UWvn/PBKPlTxbho1kCXekeA3Kg8W8VacSyhgb6GS14skl'
        b'TnUei70yaFT48+M37KZQo1FciQwoZPhOzJatxDjZdOyETjHHVwclWdFRsb6xNIZtilIuVeFDaLYwvhOFFybPW6/Am3hCkEQLeD4nzMLe/dBDGXU6LPEAFXAR6gKjCRnY'
        b'q3SVMuE56HSCSnLlFTy2UHmNH95GiXUThEnr5L67t1mY73LBHnck1++fTNeiQN88O8xMtcrhJOZncyKQ5MNeDZwJVbQuWOokyP0l0P4sVPJJm6AT79CqpEIvFA8Wxgvq'
        b'5NAq38jXbjy0RGKp1j8G26GYFpiURCKMSZBtzsHbHPGgRKpkFVipH1QE8lANiqOomga7FQSeG0TAOo33ls+L9yNKVsq3CeonqPGRFO9Bjc+QoGfavweN/o0XrexpcGbM'
        b'NlrscMZyuIIb4ysUg8nkEgYJ7FESD85hGItxkc1i3CbQpBmAg2f6ZZmG7H45OzjpV/BYvl9OIYClX55m1NOVwo/sfpnZYupXpB6yGMz98tScnMx+mTHb0q9IJzSlXyZd'
        b'9h5qbczOtVr6ZfoMU78sx5TWr0w3ZlJw0i/L0uX2y5435vYrdGa90dgvyzAcpCrUvYvRbMw2W3TZekO/kgcfen4EbMi1mPvHZuWkLVmULCZn04x7jJZ+tTnDmG5JNrCg'
        b'oN+NgogMnTHbkJZsOKjvd05ONlN4lZuc3K+0ZlspVngCc+Jkp5lYLs60mF3YkYGJvdFlYvTWxF76M81mF5b9NbGX1kzsEWoTS7GZ2KtyJvburYkrLssOmJh1mViWwbSA'
        b'Xdjqm9hraKZF7MKCABNL1ZjYq10mpqgmRl5NLBYxsQMbU8gAaHJ7GgDNv657Kmjymp+pHI8Y9XskJ9u/2/3aZ1PTh/4PUZrsHIuGlRnS4rQq9vBPWo6eVoi+6DIzyRNo'
        b'7IrEKDDdd6HNMFnMB4yWjH5lZo5el2nudx0ciplWOZZz0EXUxuXif0O1ksVhPKsmV8plKqZx0eMlzA39X33RApc='
    ))))
