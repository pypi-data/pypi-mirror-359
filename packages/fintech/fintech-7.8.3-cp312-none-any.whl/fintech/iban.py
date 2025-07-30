
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
        b'eJzVfAlYVFe27qmRKop5KgbFQkEp5kkccUKUGRGcY6CEAkqQoQacFScoZhAHEFAQB5xRHFBRk72Tm3Q6nYZgWiSmv6T7vntf0sPFxG6TdPr2W3ufU8hgujvv6/fd79WX'
        b'HGudffbaa6+911r/WvsUv2VGfQTcv99shstxJpNZz2Qz63mZvIPMer5asFnKTPhk8i/x2G9aaaaAz6hFl7iWYkYn3cCHO+JMoemZ/TygzdQjfXjMdpE0Wyn+Pss8Zsni'
        b'RMWWgkxDnlpRkKXQ56gVK7brcwryFcs0+Xp1Ro6iUJWRq8pWB5ibp+ZodKZnM9VZmny1TpFlyM/QawrydQp9gSIjR52Rq1DlZyoytGqVXq0g3HUB5hmTRok+Gf6Xkdl+'
        b'CJcypoxXxi8TlAnLRGXiMrMySZm0zLxMVmZRZllmVWZdZlNmW2ZXZl/mUOZY5lQmL3MucylzLXMrm3ScMboZ5UY7o8RoZrQ0Co3WRnOjvdHCKDU6GhmjwGhjdDY6GEVG'
        b'K6OTUWZ0MYqNfCPP6GqcZLTNmgy6leyezGfK3Ux62+0uZfjMrskmGr67m77zmD2T97inMNNec3crs02wjtnKA33yEzNGr5El/G9PJiqky7qdUUoT8yRk8eL4DNxTrOWl'
        b'+7mJkhjDdLiJ76BT6AquxOVJ8cnYiKuTlLh6G34Ys2qFv5iZESXEj3CnB+3/RxczxoJhVrQp0vOWz5nCGNJJ/yrUiipwt9QyORq4VMWsikZXvLHRLzYB16dIcHn0KuBa'
        b'g2t9YQRcE52Aa1Z7R8fjmsT4pFXe0GAMxNUxydGxq7z9o2P8eOgiPH5eyOhRuWO4Nb5hmAWDrETtMEblWDboKGpdDQ9XBiZH+8XhKhg7HlfEiJhiVCt9A51EdzJ4o9Ri'
        b'ZVLLNrgctSwD1dD1EsJaiWEtJbCC5rBiFrCqVkbrLCu6VrCDy4Uja8Wna8UbtVb8UavC28Pn1mrc3R9fK9mEtbrArtUTO9D1G3wRo0iPT9FlMPRmD+wcocTBjGHS43fN'
        b'cmJv5jhJGZvCfhGTnm7xC3E+e7NpnpCRWPQKmUXp8V+7apgLTJ453G5QuQhf2DGLhu238z5de9de7q/g5REz9w5u4nWZMYogl5rQ70LOrrdn6O0dk76xPmLN8x5m0vz7'
        b'nFM1f2CGGEMQNKA63EVUT5Tv7Y0rAqP9cQW6kOoNq16Lboj9AmL8YxN4TL61NALdx9eVgQYH6FY02UZngW7g+7AwuJFBx1DVKgOZf2pUsk6L9i0Xwf1KBhl3ofsGR7j/'
        b'Jg8bddppqBnmjKsZVAHLeoi2oNtS3KTDt1HdXrIL6xhU5RVMea3Iwo06VJM7GXSK2xnUqg4wyOF+Agz8ABrQXSkfWk4z6CQ+gXtYbr2T0QNd0RLUSiSohYEC8Gm2pW6W'
        b'pQ5fF+GjYmg5CvQOdIuOgx9aois6Q5yEdKlnUOWsbNojdvEUnSU6gjtIh1MMasLtqMPgRHo0FKl0uBsfQFeIbMeB2Vb8wOBMhjmLDop0qAqdQF3kyRYGncDn8X6qNv+p'
        b'qEcnQ4fsiNxtwNEfN9CGRCupbqsrOgqeHB9jUA2+gCpoA67dnaSzDtrFsB0aUTVYEhE6e7ot7racEUzGv8KgU/noOhUa18xfJtOi2iQymUukxxVUQtWmQw34Oqq0AO53'
        b'eQxPwqCraB8qZ3s144pcHb6BLywjK3qYQbXKXNoiQedRO+42pOcKWF2DPnKoEszwPlsZ7J6OHWSoa2QVGlEnFS4g2Vy3FR3DD/kss4o3dOwwZXPRIx2+I3QiYjcxqB51'
        b'rqEtyStgCaxxB27ilvTEbNTLaqBqtRnulghWk4YzDGpG+4R0PpvRTXwUWjC7284zxFPgGiqAQ9QS3K2PEIvYYWot0Q0qcz6+AmJ2W6xHpWK2TyvqWUDZ4QO4DDZWtwW+'
        b'XER00An8vHA7bUMd6Ig9rPd1O9xMJO8gO74hmg7lruWD01y2h/S5yoCuTrlSuVFT/gZoQCfjOfWctotllVApj4SGAlRKNNoFzHHpNMrKAx1yAVXnibgNV2/HZ4c/uCEU'
        b'Fhtkr+exXU6j/fgYbctH51A9iNaNuuaTxougoXzEbvl1wTLSgluyzdhdctIa36N6QL256Cws3kI7TuxWtB81GeygyTfbRSZBR3NJw23YzjtFdBw/iA+PZLBDunAd4XYL'
        b'hNiO21hzuIMb0H1ZseZNETtOEz6Oq6kWXHJQnQzf9l9I1HYdxsEtS1gJDtqgI9AyGR8ns+2GLSzDh2mfzXsDoSFJKWKHaUfN+A67FSq2mun08iAimpFBpbAXuqniluJT'
        b'eL9MF6QWsqpuLPakg/DmoBKZOerCd8gYdxnQVRU6Q+0Un5vp7rEFVYbjOnQLVYkYAT7NS/INNbgQ4U54pPm7ocpifARVowoRI8zhoX3h6JxhCul6A1fv5BpteCEmBlJU'
        b'zZcn4V6lgF3/Wwlg+ZWwxqhqXQFTAN6zxmBLGh6gB3lxRNJq0SZmkzaBvfsQVc+LAzGTUW8mk7lrEl3BXNhPdTo9PjJtZM7HrA0zqDtDNXm4ARtdYVtcCkcXRKoEcA5n'
        b'NkeijvUJTJhOBGH1RAxVjzNqW6LTo9pFRKPlDCqzMzcoCY+jyLiV8CAMroIxHaFfw9AlfBRdcxcyk3C1UIoP76SyzNsUo8M30e0CHuuma2DfVbGyHIxdxbJBt1En4RON'
        b'rnJsqmGmk9ADoSAtkV3DukW4F2LHvjdNoSPQmgoDWj0HK81Jc2WUNJfx0XQZEeawUIy641lvvg+X7QY3q0SlxC+cZFBLspYKgw8nLMAN0egy6GSESQgRC+0XARd/Ae5B'
        b'DyPo/tiILxbotPge2k+WowwmAnul1+AFTeu32halj+iGKhf1bpYpcCXqXG3PxCrMZJP5dEZrDBCmtKiTMcW8fFRjCCRABYbvwC1gqhNUjK7havLPRXxUyPhrRUWoJIsy'
        b'24p6rUCi0ikjcbLXijJDZ/EB55F5VQs2gUA88Hi9m8F/nIB1R5Ww7NG4R4xvbQC7pL4Bn8FXwauje6iKhgaIbahJYfAEwhJw1unReiJLJsxPWcm44W4B7oIn97GaPjdb'
        b'qTNPRdQxw3odBaB51TCbxHRUph617NXj160zQeVA2F9OEG9KYIrQNQm6i8pxPWUrw+c8dDC9czOErLNriUUnDQFEzFvoRASR7Go4Lo0wLaIAHcblsIalWWBtJ5hgfEoE'
        b'gezRPKo1Z290AiCEdKEJQeCSKQYfQjwKg4A1ek+xOxP0Ho7Lyc5sEOBefBe1sHOtsZyhs4KRjGSyJ2Bz5oA/pruzEx3Kfp2pgHgqdJvszjKh2Wx8m40lLYDF6wlEub3C'
        b'BF7wdZ7BH9pU+IbLK0Ympa2LHWU0QiZspwg17cLl1CNP1a8AVvPyTGBn52pDMBnkriv05Di92uqTwB9donzDyKYXMiG4VoTa0JFVrK8+C0twTFeEy7NNCAkdn2zwJlse'
        b'PVgy1oxNCwnaQgfIHK8IJVYWVOXbZBJAU+ICE5jCj9ABdqPexqd3W7pMEAx4Xmane5luenCrOl+I8TQYHMb7NgM7tF9mxkbsI+iQGesvDhXN0xkM+LwJnOFuR6pH3B6H'
        b'7+EyN9NAF8lAEDO3k02CShXoNJhpAn5gFoIa/NjAu38NLtdZps404TmIed2U1w50GpeNSMwZuxfu2IwPrPcOZ9WoQ6ckuMoOnWBX2Ai+CqBMN6rfa4KAe1EXxdS4dAXs'
        b'UNRmYnhpgtlzGjgmIsbZy5lZBHh63J2NOokKWmHveWZT740qQlIBND4yM4HGuDy6JV1m4pEhrnDe32PZ5shIBURj4qOS8EmzAIh67LofwhciAJSd8DBhMnQAd1KDmxSt'
        b'wK3ETEzOZYzQ7F4QMgHovmizFbrDcruKe2botuJz+IqI3QDVEWC+RCwDrke1HK+L42LKIdwAu2iGAN/H9/MpI6vc1YAHcTu+YkKE+CKAZeLIk/HVsPEOKowa8X2eELzU'
        b'bQG+ji+lUu3NSXQhbNpQDY/F3EfQeR+6fyxRhTcAy7JwE67Ed6YZ/KBBvUg2zgxhlB3isWZYJAIAXaKhnAzua3XWPriBx+LQFkia6mioWAYQ+yHrsF5JSiNOSA5MVyDA'
        b'1/KmsqCjHh2cD5AVHPLJETj7CN+i5ueAruw2SXRtrPVtJAFqEu4QmolwM52wPapF54GTNGwE+x5dbAgj26V9dezEiXHchOiGRcJidNV9KboyndHioxJctwXdpkvhBosK'
        b'LPVyfM4EmxdB7kTwEMSROhEAyZuQ3VzjsdvwGOy3Sjp/1LYKJjE+VEYqBPNFTBhqE6FTiyALpNvmLg+3AsTWUKd/lsy+AV1gjebw1MljdyDxsoc2jqiBhspQ3CxCh9FF'
        b'SFtostUGKVgdwezls0x4HqLaFeqIwDZPAC4c8UPVI16C3hGAKiw3z+Qle+eIzGbb7KICukJUPAX8JLjJlAPsQgdZf9OEr+BHcTSgARPO7LAxfAzuWomqzTxmLWP9zWXU'
        b'4Q9au7Ez3Iyd7omtWXSpQ3IIKCCTxbXakXBOmZAoHopuQXCbgkqpTGvxsSDcbQX4kXoGgLcdfjBFwkfHxw/Hm0gImSMkbUZiI9dh78FU2M13AV2JAaXU4Kuoiuy+G+B0'
        b'8FlrCgcgtpZuGhPfKB6wxNUrIUjuB4ud7kq90Rt8Oe4uCsAlfNbQaue5UVFm4oZJY3z+iBEI/UmcLROAtz6GelhR4EFcCnxQGaoSs+6urhAyaA9onJGgHD8nfpSS4JI7'
        b'xOKbdnBxDB8sJCnZOnzJlJIlcK7uOt4Hqy8NR5WmpAzV+bBNx/A1UKYU98SYsjJ8Zw5drc3o8C6Sr7VOH0nLShZRjxaOShdPdEREScdwLdFyF2iZZL8s7r+Iu/IANTiE'
        b'm7K4VW/SBjcdARPoqJgzoMOzoMcMVhuVUZz/uGgaAN0kuktDd1kPctNhE407O1CHNeFyG10SscCiAdZ1HwcIJkG6MBFrtniGmTwBNaJgfEIE4h5ypGuRiu+oQY+3YFfc'
        b'5WyoCfqepaEhBj+0nrArUE9ImAnvsQzXiFBdECqj05QXR0GumowohLpKTLTa2uBLxKsFZHJgbMRCvejR9lEha0W82ZxsCKPUuK9AayfJey9NMaW9eD/ojAjmisrsx7oL'
        b'EhjK3hytPHAX6JEI1UaksWt/WLGAcGuCCM8mox0GSIdDSdNJksyOZsfP4LyYDUjWEw46PmCLjDN5qHmReSKuRUe45PtmGMmwM1G7KffGFRBVlVR1DSNx8MJYdw7zKoFl'
        b'VQrwHQ1upcJl78R3aRZ/KcaUq+O7aup4rFAvJNO5E5EeB/M4NGEQFeJmhtqoMiYFcvu0YjHLqQWXaykaTkcHJ/oLNjKfQWVkJ98VQBrWiNhqVWqiEtigy1JTjWAd+Gpf'
        b'FktUmb0WKRLUcA5dJcHqkdAqHfJDWt3ywZdlEnzMT8xm9GfQuW3UaUAqUe0y0YHBhFBtLpHnqgBfjeYqW+haAL4AbDpxp6k24baFsslLMYwHbzPw3dHbys9slgW+wBXI'
        b'ArxkegE6yoWgBsh0uOh0PiVRBoDsDt9U4MAdsBfp2IfXmsvMQazKkUJCWxYLBPcB4L0iK8Y9noThBZJUX0FHqVzLbK3GoNNXW3MNLuGc4iP0MJWtQh4vmANsTtNAdolB'
        b'x+fK2L35EBKe/a/fnKh7Pa7GB/1w/WbcsZ7R5kKGtRWVUJE9UDduAobNbqaizEJ8gy5fsqUrJ1b2vLFpv8iOS64uk4yhHB9g9XIDXw6R4du5qHWkitM7iUbtAMjo7hQZ'
        b'xmRYYxNCNsNFDSI9+Mh2yq8I3bYDdqg30FT5AY9zgu6UYMjioGmafqT2c7SIakcFDmqfzMqRFh96GdRprma1cxAiV+NEp+cKljkq5hOn1w5ABGyhlfpKdBff479anBHA'
        b'0YkPjKjjqqhoJm+FxCwc3EMVNSDYLCdXcL1WgHAjGSW6LNoEi5HAhMhFqArdi6Lr/0bE6jE5ALf+ZHvXoSNkA9wQCtGVeOovQsB37HtdhgmDoLNpxKQqhJIc8Fg0ZnQm'
        b'rXiNcyHDlKIKeHieAD8IDKdAaKULrOAE77Fg4TgnjhtEqAU1b1ZKaEFqqWG5zKooigTDhxDUZgez0e26eZIMX38DHeJssD0xnTWrJv5SaNiAe0iPHlIyrd5Au3ihY74y'
        b'Kap24rNLdx61Ktl91RuBK2WGN9FFroh9HOQs4YpnqN5HphMHmAp6JqCPD6NLU2W6WFzD2ejJNZhNoCRiwMCV4K+OmJFt9QDcDLPWMBNashghsL4NjQ3IyJX00BXOJpGR'
        b'VgCFqDsVVa5i1mwUAwCsxBVKIYt8q4J9cGU8YG1jLK4SMAL8EGLAAnTLlAadxaVxa5JxRbyY4b/JC8S9qM3gCk1h4OQPQkIWh2sCcbWvkkzSwkbgaLOOBrfpAKmP+Cbi'
        b'SnTWP1rICBeR87LT6FIGOT8yfcjJDT1U0sPlqNh01nmcMfLoORffyNCzLoFRliWlp1xCPlMuHjnlEtFTLuGoUy7RqPMs4R4Rd8o17u7oU64vhmHVzBWjPpHkjFanUOXT'
        b'w1lFVoFWUazK02Rq9NsDxjw4hohhj4Z9cgvy9QX0mNfHdDCs0AC3YpUmT7UpT+1HGS5Xa7dwA+hIvzGsNqnycxUZBZlqelBMuFJ+OsMW0wG0KiOjwJCvV+QbtmxSaxUq'
        b'LfeIOlOh0o3htVWdlxdgPubW3EKVVrVFoYFh5ipSc9gzaHI4vWmES8DrOmzSZMwl08zWFKvz/dheRMAlMZFjJNDkT5gR+WSAYtTb9GQKalVGjqIAHtK+diA6N+320YPp'
        b'TWKCKv/5cfTkOJ7jFqBIMOj0ZI5E7ylJ/qHB4eGKxfErohcrQl7DJFP9Wtl06kIVFcyHfPNRqGFrGFR6NT3dT09P1RrU6elj5J3Im5Of1TjdWtxcFCma/Ow8tSLKoC1Q'
        b'rFBt36LO1+sUi7Vq1ThZtGq9QZuvmzsyoqIgf2ST+sHdZao8Hb1NlLxVoxs3mTEnuyJm/MmubeIyGpNkUx11RSIIQYvYOpoBl9AzWxzhzEBwtLmYnb7LY8cOhhbxkvAj'
        b'XIMqGRGwWcesS0QP6LNve8sYcHjbNtqk+21JCmYPfXcKrJlJkPilBafn5YZ6MdS/BaPTzjoZn/FDx9kyELqOTiqtWT/UBdnjIdJq7cs1nsYXWYdZCri7R7dVwOCyPezh'
        b'4jxP9jCywFtnTXJo1MaeLSoh4aTOtwLVQJJkKWQ2JLKHi4XzWF7lqAQ9lGlFjNiaPVwsRp20ZepmiNuFAiYF36RZ83F8Hz9kRTvtjyplRQJmG6qnGL4Zt0D2Stk9BKd8'
        b'CFVa8Jg1afQ8Eh+eRls22c3G3ToxhHn0kCY5h1GTmMKt9VvwAR2+waMnIexBJcDJI2wV8QG6lwTJkYBB3bncWeXdbPYErRnS3k5As2S5krnTyrPsOSZuQZBLyoiGOpQ0'
        b'pp2U4AYqxyJ8G2JBN0x4KWgO4DWqmxRP134N6OKwbqsZs2sdLf7VRjtT3bnm4pu6rXwGH1nOVtlmo1qlgM2cszSkpRBd5epvTb60y+z1uJmOsdqLHQJ1hLLrsB/3SMkY'
        b'+HAmOwiPDYIyEb6nw91CRoKa2dIjbtuq5LNKuJ2znrbhCzO5tjMA26kS7qFrIDQ5CzDfzZ1Mn8ZX6JYLShCTV0Kcd/ql5/VaF3OJ9DHQ7uXQIGBmdAPww2wCTT3SLN35'
        b'nkBnDfFf9bJgd31cIg6yKX2v+N8SXflLLp/wj35Lmv6ex9pVednJXnayNZuVm62DPptmVR8XUny4wse6YP7J73745e9m/EV02+3Wmjxf0YEB/cuf3fjzlMvZLr/46FFF'
        b'jUvImeY/nt/7YcnGQ5GlW34Z7T7rtMpbo899Enjac9XegLAu1S8Gl28K7Fn8q4OZcbM9Oq65ZPu+V37xs7ubk9v1l37Y0PLYuXljl0x1asbTH/Y/sPtzfsXRjx4/+ihk'
        b'L35/cUTttSP+PEevpWnPMv5itVv38Xd2/3bWO/U7439v/2r57JtzWh4dtXTU/f7+YEhaXe+3k6el2hyz+X3H4dYzZp906zcuPDTlpeq/vlzxJ15vctf+B0OK//X28XVv'
        b'J6p/t1BUnbxy9SdKsxc0IziITtv4+ntH+/MZMTrBR60b/NHVpBcEFcgXh/gGxPjZTPJRBuBaP1wOKlcI38TX8mkzvhidGJfkj8qTAFBsCRAzsmQ+rsElqI5tbkF1GvKG'
        b'j49/AA947+ej/ehc6DRc+8KPNfVGfA6ySPbtmq307ZpySBBqiv19cEUgH+D6AxG+ia4CP7K+vlticWWCXwyuYRhxGH872mcVhA+8mApNdua4J44wcAHgXQPGUxtP8Y8j'
        b'PkjOzw6iO0rZEN9bqSU7+ydddORVGYWixPT53nF+lrZghzpfkcW+MBZAQu+CIXMaCNIIsWPUdz5hQY7Bvy1hnq8QMQ7Og/JJg/by43Pr5zbMNy59am036ORyXFOvacit'
        b'Ezy1n9zmeT6wPbDL8/HUWcN8oaPXoJvXEzf/fjf/zswBt9Au3Z3t17e/ZfdWysCsmI/dYganeQ8LmEmxvOcSxnVaW2in2WOXoEE3xVO5+6C7R5tH2+LGnLrlT62dBl09'
        b'Tvk3+TcH1pmR0RfWL2wLe2zvPSh3H2Z4M1bwnjM85xW8z6d4Djq6HE+rT2tLfezoA61908P75eGDE+635fbLg8ltl8mnpjRN6ZQ/dgkm49rLG5d3LuifNIcQto6Nno3a'
        b'Nl6jd2dAv+tsMnMn18aQxsV1Ocblg9ZOjZp+6xnkrsPkxux+h+lPHPz6Hfw6UwccQoxRT+2Jqp5auwzKPZ7I/frlpEEe0mcT8rmDc6Nto11ddONW6NTp0Knq4nW69DuE'
        b'1PGeyr07bQfkvp36fnlon03ot8NRPGbS9CduM/vdZn7NgC09neI5LIB/v9eRrOG+59Jw5p1w6yiJ4F0zHly1gNMZpcWQkCzekABQ0pAZhzmGhAQkDJmlpWkN+WlpQ7K0'
        b'tIw8tSrfUAh3/v4eAlfFpMPHtI+0xF9qiW8cvVeOkUfnwOWHEualRsjjTX/BwOULK3llbolsmC/iOTyV2VXO+UJofTBhUGL9VGL/7XMRI7IxUd/riG9sFvsyl2ThAvDj'
        b'5D1EdBqygaNxYA64Mi0lEdckxYgYq0LBbHzfwL490GozNT8rLj6Rhf48Rraej68moDLWC9dDzDsQh3otRpIGiInnM0wvcZKP0IQ5cgjw57PAn8J+BkC/OEtIwb4AwP4I'
        b'dN8tpGBfMArsC0fBesEeIQf2x90dAfsHAewP8saDffoa5ii0ry3YolCZ8PlYJD4WdY9D1al/B/xr1UUGjZaFfIVqLSQAW1hsano3dCw6SzKBNhDEZyWMqNmijtJqC7Q+'
        b'lJkKWjJfj+mJvERcFtePn8RrAS03KbbH+Bm+bgiSBSzLU2UrNGwuklGg1ap1hQX5mQBeaTKgyykw5GUScMviVJqVcJnI62FslIZM+RVqhgxJpQjx1xsKAQ1z2JhqDUC9'
        b'N3nCjwyk/EmgVpRomA/fi/jo2vj3M8m7meXxPrF+6GIq+5omueEuTIqPSQAgdgmVy+agB7gxVbP0o1yhLhbYdP5N1/xBSGt7w63G+wfreeYrnddEPk2oar287kML57aG'
        b'uw3KQ5qZqdNLy/e1H2s/dr3hrPFsaXtpcLWysb3Uo3FfqKC4kQncYdF75n0l/wU5nzDHta4yH7AmCGhVCQYunk1B3fgwbhDia/gEan9BXs5ZgOtz4gJiIaoBJKZBC1+0'
        b'FTCu6KYwH9fGKMX/wLOIR6IT9SlDMvZNZDYOjSZoICIvHJBAtMyMcXB/5jS1b9qSAafIPpvIQZdpT1wC+10CuyQ9M94KG3CJLo81Lq3zJOFJ7taYWrejz8YDAocx7huy'
        b'HqyXNBuSmLbokBm32bTEZ2hJ9Ne6jZXUjPWBRFjW/ZHDkzEiPiGPkTPBv4D/yxXzeJ4/1fUdFXsxZ2VBAsNcIMQWlhNqKBfwUQADN1AVavMTbIwLQzVF6Ao6hx6Yo0Mp'
        b'zCZ82BK3TttLUet6dCFDhjrtiq14DI/A6Uvo3h4WZxpRDwLI5lhcRJqMFOjsoZ0i8YkgHb69xNc6RMjw8WGe02J8hrZY4WbUo5OiuhAtn+EVMOiOHzrLethTuCtahq/j'
        b'ruJiMfA7xOATevyQg+GO9k5xKUmvCjad0Iu69YvkBYSz+N74ig1uyGFrwEbtUl/Uqwe3zmP4qIYXiW/njnHbEpNVFTKv6jXgtkVGU8VGCu7bPEsy4r7F/zL3TWo1f/2x'
        b'Wg31O2MrNT/qvIijI4//44rHjxQiSOf/8TpERh4VS6fWT6w8jBOQ6KUgI8MAfjo/Y6KgptpD1IrFikiAJ1rix5dCvMrQF2i3+ykKDZvyNLocYLRpO32SiyuRapiPKm8C'
        b'vyVg4QGjZFORRTHQH0/4pESm+vjBP0uXkn8ik1YGw78gns+SkCW0ITLSx28Cx1FzUuXpCl5bQSGTpHouZOsmwDWThJTtheMUSD7/VLAe4VhQODFGk88/F6fHLN6/tHAz'
        b'AqJGYpx14jIa5PDRNHLm+s9EORLjNnqbopwCl9FseaGjC6nwBLV5bt/1e20UW7WJ2GvPkFDVJ8nYFb9GyJZ9cC8uwWdR5YwFDK37bJrNerwO3MlDlciIjGDr9rx0Tyk6'
        b'a0XZfBVkRYo/zl2JGX4ZIj0DeT0B1uB3Ty8IxS2koB3MBCuj6N0EVBkZilq3wBRDmJDd6BBl8SzellEwzOw2m2K/Hp6UsLAh3XCdIVROXwUEDnMCWL4PYyJxt5iBaLKC'
        b'WZGPDlIOv5hlTspSEpuNWyyEmWomVfP0VIlI9x6BDssdd68ItkJBFvqWcxpvSbmoXyoV73lL/u2Sl0aPzz6+eNbOLy9r+fzTpzwt/SWOX3ndm3fql88jdjCqjzYvy3G2'
        b'uPjlr90O3zSz2/7G8JsDg/oa35RFyNh+6tcR8kVtf/pFiWeU5UPn+wsOJC+c//E7f5v15X9+19rUVK2+HREw84egE9nzjrfYfJX+yaYvnqO/7lnQcgZfC3v88c7Tdtov'
        b'677OWbl/y6r84zWVt+JLvh30747Ytjzis0W2f/7KyS+7bskvfGY/d/A5V5N09GXA94szlJIXtL5/GdD4Rd+lyPgqYffHzfjRC/pmy1ncrH4t7BDiB+ggwI4GVEPxiXda'
        b'kS8EBsjcSfouWhgID/qTTnFmoPc2cYwNanjhTgbsFs+WxeEqJcsN3UXHgKMjKhNKstHBF/Rt5kxcGpfkD0GmmIeOOS/GJxW0sID2pc7HlWsEuDwwiYi6h++DWtA+msqj'
        b'Op4VrgxFx16l81YrU+mIEKpPoJI4dHYBro4bKTtYBwmy0WVcrpT+tOydnEmMJO8sRJKyGRdEjx2vvlJ49BkHj3YBPJKTvNTO8biyXtnga4wEIPRU7vHMdXrfjGUDrsv7'
        b'HJYP8wW2HoPu3k/cZ/e7z+6xH3CPqFv+XAzAqjGjLfSx/YxBt6mn5jXNa9Od396+vWPnY7dQyJc/t3d/Yu/Zb+/ZlvLYXkkTXLu60MptjSEVe9qmtanap3dGnvbvETyy'
        b'uGvx1qrHs+OIGPBIcHlxo0u/9dS2jE6P9qwuaf/0ObSzU2NoY1GbbePstq3nd7fv7tj7sVs4W2H49sVkxnkq5Ly2Hk/dFJDz2nqwOe9Z2yULGbRQGikTYHMeXFk0J2Oh'
        b'GzntGRJAQHodiPvRAsmE3Jacto5S7x8ZLrUl0G6dGY835RtIbaf8VHzXJFYyF2RhAiX3ilC5L67DlfEqVD/qtGuO9ZjfX4341XSGTU7p76+EWfyR31kJ/mW/s8pR8r//'
        b'aIyLX8mGiB/JrbJoakTByOhDpP/pZPRHY5RgQowSJxoiiGPH1ajjH4Wo5fjuqyhlilFb8WG2ut4px730fKIKP2APKOT29IWSYnQV3wUHgysScFUKNsbz7aLQnSXoArjC'
        b's6gpCl1QMitszNBtdAdd1QiZP4hoTvdOSljzB2GQ010fm9NZkJwufeaRP25ifsn7oHvTB+eD3o5nTvzcSq5eFnI8uNI+JW2GID4K/M1cpqPL8rvCA0rRCwhPzOoYdHy8'
        b'c3Ww4NzrNZ/N1LGFq63ZWio+6MB552to/wvyI1B0BbehTlJPXR00tp4ajupoMohP4tPoAnW3+HDWiP+m3jYOuBCLTF6Er7M1V9QZTNMCWnSdhG8r+aOMkvgzk8Mzy1br'
        b'qbszfaHOLoZzdnsk43PBV9XJ0aXCZ06KPo9ZA06z+2xmD9pPfmLv1W/v1ZY5YO/bZ+GrJUVY1o+ItEQPr00BSRqf/ioBJEnaiEzOPC75+66E+dMWCY9n9xOcwzfEOdSL'
        b'PZh2mZ/gH1q/0Mj8P7F+yGm+vzjGeFIK8zR63YiJs2eIYMcKcjdLq8qmZ4LjzN3kMlSKsNfWTMY87B2ZtCoxdeU6P0VkdFRkXMqqBD8FjBKXFpm0NMpPsTiStqclrkpY'
        b'ErVS+dMsm0KrRbFi5lsH2L+KdD+XuCUM/V3sGlS7l/zo1pf8/LU8Pjn6VQ6KDys15J01c9S0Hf6PQeXbGdQqNkfGwuX09dtF+CYqGd0ZLJp6b3fc6YpvC9HpLeim5kby'
        b'D4xuIxnql3rWjOdU1vMEl0s/3vhh64dKC2XVSotbFjMtWuPVVVHPvD4MWqWMv9S+o9l5XtNmZ899l/1Wxw/MbVJ9tdkl17myPiF9WeMK3Phuzadeb2doLFpcmF+9Y/sX'
        b'uZ9S+IL6njvz7KnVbnPgIBXqNWfBSDM+gHtkcXPNRyCQySAdcDcLycq2oOPcuQQ+iHpYMJOC970gux814B68P47iK28xI3VG7Uv55BeK+IJS+NpwShZgxEaGzCFB1HHl'
        b'nFHfqQWnsRY8/KaUcXAeMdmJFXZquQsHnBb12Sz6sVI7PNPmPuAU1GcTNGjvfHx+/fyGBX0WHv9Xdh1J7HqUsN6jTTtB+tNMWzuPDM4zEA+s9sFnINzDbkGVuDYQVZC6'
        b'SBwjZlz3CnPQ3cmvt/xMYvlCU9wnv7rmCtL/WuvPUvK/2Di+ID06/NPKbb5qC82dXxP1SeZM3hUoVMMNQAdj43AM6wPyVHo9JMIZKgjhY5lSMKDKZGveE0oAY3iNlAP+'
        b'UTWAzf7//0EjkkQD2S5TZqAeDoygC3H/RMpsAiOqFOrzypycmaBtAQKAtbvenu/OvqWKz725keATxhI/oPBkzyYKT9JxLb48Hp5ciCU/GB8HTyrQMcreMsyMscibKwaX'
        b'anHVU8podpfG8HXkj2HMth9k69AXxmCWeIvWD1sL95in3HYQRNanz0hxChWIF3XKxDe61wavIj6xatH24vjvHLIapYteFqKodSue4f3/7r46RrFOpt/rNOucZqaF5GXh'
        b'OUF3GOPwsZM+fLlSTM9N0Y0NkyYkjPgGusChGrs1L+jre/tw05pRCWMSPU3CNeDBE0SoM4qZlSjeIw55Qd+D3ueK9nMY6BQgHOpPd+LOF6RqiS+5CggCGoV/duHLAIHW'
        b'4XsUAnkEo2uj8k3ibPEx1EgcLj6Mz72gfzrioT02xk2QAzfiiyD2YSFuRR2oFxzWj6YsxGGNKppbUAwCW50Y0o4xFHW0OxmubG4+DiqR5G3egPWUtpCPrb3oOWVIvzyk'
        b'a96AfGGfzcLP3ZVP3AP73QMH3IPrZIPyqU/k/v1y/87Mx/LQZ66efV7zBlzn9znMf+rm1ZY74BbSFdzvNrNOQvkE9MsDOrcNyAnaGuWEzYZkxKOmFWgJZvr7KRpbcR91'
        b'OKBNII55zPTmjnLNL4vANbv81JSsQTyN6ZAFCJSCxMRlSt4yJT9xmabCL0CoIz/aSHmgP/T4ZcpAurPZ8Kwv2zTr/+xjlL109/7jvk7jzsr93+TW/+agz4oNZqubHVoc'
        b'iz5f8rvAP0z58k5gwh827sze8TLm1/N/u/vjn6tPh51791lwxH+Ub5/x7tqm6amqXzWeVUa9L4jde8nmwJbQre3fbwuUd/9srSzDcrXFn3+oihda5Xp1N+9/etRG9NcW'
        b'DzN/qfrqRo+orPf3NH3Ai8jp9mlfN7Oj4tjv7AP/4Nh3/miP3H1bcsUN5YalL6RHOqa2t9mtuuk686aT4ab7gqGSZXNlCfrw/+i727gybvl/djQFvLXknqTySzu/sz/v'
        b'arn6Vuw980tful5O8H6W3fr7O+7+ekH4x6vzTjeHFuW9vfqe5adfWv3+zP2u5ts/+9/uNwceDC5/2XHAfdGMCO9vrL8IitjfIfVqevqlc41uN3/Gl8qWc9mFx05GyiNq'
        b'ZTfdIl6cbvnh8K5f/zxkh2jNlzPnWBa2ft8fV9BWK+5LKvjN6uLzn/bgP2181iFwPrP42XnroKVlwUsit0Xjr+dO7ajNfO+9bUtObTqyIPLIgvdkrg1/a/U4Pyv0Voxo'
        b'wTvBpUW97/j2/ptbb6vW62hP/lf77JILz9z4z+L+AY+ld3yWLi3vVD0/9exe3lX/TdaXeFeCZuXJPk356kPD0skvn4p+feiTutDukN8JdtSbf7LDPiHict5vt/cOBHw4'
        b'9+F3jueS/ttnoPxIxF9+/d/hH1jeaXf7ZNmVL/407/mCi+u+WfefxmnX7oVE1H/w8E/RN24PXftNZL1r9vMvgzQJ8idf3//NtAVfhD5M/+C/4vf+4g/D7/X1LHc8fyl4'
        b'V8sfN3yRWHTnkxl//eyr1tbfLX+8KmhNTH9e69OFsu7fnnzjz/o9BYm/ff7p80vRe58Yc5xi/2PegLP+308ObVn1t7/EWnx6752601F/4//1E/m7Kf7g8pyovz6H7pB3'
        b'ZG9l8RjebAacWjW6SJ0P6kQ9qH20+2HI34SgcC8FX6A1NvITStQw1mdewOdeFdquGdAlFhhe4aGmreg8rgRoWO0vZsRv8qehUnyZ5nHZSXlzUJdvrD82xsQnihgZus7H'
        b'rZAsHmRTQWMqeoDrUH0cCWPwEK6KIQ9d4+OLPHxLOemnvcki+bHLT34f5rWehrj2kRi9iHxKxnxYNytJS8srUGWmpe0Y+Ubdq5OYYf4KOHYZj7F0HBaaSeXEr4ZUbm30'
        b'qNjVpGsLaVO1z2ze0Zl8Yu91zy5tj8d1Q0/y9W3dAW8vfd8OR38cEv/MmYBeVdPMZmlbbL9zQJe833l23/zEfnli38rUvlWr+1eu+Vi+hoBcu4b8PhvPYQHjvJY3bM7Y'
        b'OdQtrnc0LvlaLHY1N1oNOzB2LoO2zoO2bs/NhC7mRsthqwSeo/mghU2fndewgHz/3MKmLnBYRL4OixlLWyDMKCFhCSklzFlCRgkLIPrsvIctKWVFKc9ha0rZcG22lLJj'
        b'u9lTwoE2+Q87UsqJUl7Dcko5sw+6UMKVJdwoMYl7bjKl3DlqCqUU7IMelJjKyvF8GqU82SYvSkynTcrhGZTy5uRQUsqHE9+XUn4c5U+pAK5fIKWCuLZgSoWwA4RSIowl'
        b'ZlIinHtuFqVmcxLPodRc9sF5lJjPEhGUWMBJtZBSi3gck8U8Si/hcWwiWXopR38dxdLLeJyoy1k62kTHsHSsqX8cS8fz2LETWDKRI5NYcgVHJrPkSo5MYclUjlzFkqs5'
        b'cg1LruXIdSy5niM3sOQbJrk2svSbXHMaS6abxFSx9CYTncHSmabuapbOMqkhm6VzWDp4WMPSmzn2uSyZZ9LqFpbO55oLWLKQI4tYUsuROpbUm8Y2sHQx17yVJbdx5HaW'
        b'3GGSfCdL7+Kad7PkHh633HtZehGfe3wxn11vPidpJEsvNbVHsfQyvmm9WTqao5/HsHQsn7GfOmjnNWinpFcP039eX6+jTxilw2/wGTfPU4FNgb9y9S2PNUbWOQ46ez1x'
        b'9u139v2Vs3+9sI5XFzzoPPmUZZNlm6rTdsDZt14EnsYl4HOHgC7HfodwY9Tg5Cmn1jet7xQNTA4wxtRlVCQOSxk3P/AJ5jZPpTZ1GY26zsiuzMfSeS/5EdKw5wxcvhEw'
        b'5vPJxWZYCCRRBX24cVqbrkv4WDrzT3xbqTN5IJx7CkgwYbnL8c31m/s8UgecVhlln0utyQApbdM6l3Y5dhl6Vr8V9b5Xn++Kx9Lkl/zpUufnzHSWy0oexwZosrM5yR5L'
        b'XV/wLaR+pNGNewJI8DejH7CSTh39AJDgdFhxUx5LPf7Mt5POIW30KZvnQiC/Hc6Q8KQxvKd2U85Y9PkvG1AsH7CL7rOI/p6+OFe+2DnGg/mZh31MGHdUYTPET0v7Z88n'
        b'/pn4ZfMKKY+NWdpVBDKPhKtp5OEFHFyO5PF4Ni8ZuDwnl58KnFvF/swV2WyBZm7gBwLdO3DHvWl5s8+nHz3+6NlHIa0eh4IPeZS1H2sv9ahs4gmOdL219pKLh94/wzLD'
        b'ad65Dxyme96Ktzlhu2lunDzOPHKq74yD7/3q3Wc/a3m3VoM2e7e+b35zsU3lhp6+z9D7TFiMc+WGxuRU429uX1oryTk+28l+rc30whB9kKGruMtQqJcUB22VGIzF0cVd'
        b'+vf17xveP//8XNetwmdKfbAhRBTqHXok+q0Xl4Icynm7f9n3btVngcrLkm+mueyw+LmLT+M0lw9c5oQyHjU+j7/+TGlJ62Y+GegC/dt+SZAdk0NFGbqBK/BdPu7EV3fT'
        b'cjqAmzJE0jh8nTyX5M9Hp3AjY4t7Bagdnc2jfGbtRXdQJaotwhdxLcnyAKvVmjFWdgJ3QEgUz+GD+Kx5XEyCT4IZI56Pu4R8Cb4/l9b10D18Xesbi48qRQwvjsGNqAng'
        b'FfmN2Tx8WzTh7/pdRTdQTWAcALoaSCtrBcxydN0M1TrhWxSShaP9M8b3mawVM/KlQp84/IhOygnvW0szU3Q/cTQnN9QsROc8IikwtEcHXVEdJn/8sCoOV5oxQn8euoKv'
        b'RdFjArwfn4nHlUrcUQB8QH3lSRB7rJMFq/AFT3p4G2fnDe200Y8ITMuoPEaBb6GL+JaIQdfQNcpqLa6O8U3ywxV0JFgE/BBdxd18fAddDqT5/yR8HB3D3biKIMweXB7o'
        b'U8Sl3a4GISpNRZXKqT8OI/8l4PFfeNFNpTh0Avwc9xlBo5p8jZ5Fo+w3ikYfMvSU8htXRmQ/aOnwxNK939K9ZduApXfJskGheVn8vvg+W48zsx8L/T4VWgICdHXvEzoN'
        b'881F63mfSlwA+Ll7P5kc2j85dGDyzD6J66DEqlZWLnvsMP2xZMagxO6JxK1f4ta4+LHEfdDa5Yn19H7r6Y+tvQct7GoTyxP73NZ+YrHupThXKJrzkiHXYfa6XspYOJQk'
        b'ffuiCL7Iv2b4oqBBRxejOce+zyHgVxJApXCbe7NZuMSHQT6TIqUCLOHBlXWdU4YEeer8ISF5k2ZIRI8XhoR5Gp1+SJipyYBrQSE0C3R67ZBo03a9Wjck3FRQkDck0OTr'
        b'h0RZ4AbhH60qPxt6a/ILDfohQUaOdkhQoM0cEmdp8vRqILaoCocEOzSFQyKVLkOjGRLkqLfBI8DeXKPT5Ov0qvwM9ZCYFh8z6KuD6kK9bsh2S0HmnFlp7KFxpiZbox+S'
        b'6XI0Wfo0NSkKDlka8jNyVJp8dWaaelvGkDQtTafWk7evh8SGfINOnfkqJOiIwab/vY9CwTr4TNOF/J1KXRJc/va3v5EXsG15vBwBce9jr8P0+lOcPYlhb5uJF8uZt+Wy'
        b'xVMF30tMvxwYsklL475zAeZ716yxf4ZWkV+gV5A2dWaiUkJePs8syIAZwxdVXh5EwUxuL5NqDtw3B+Vq9bqtGn3OkDivIEOVpxuyGF1a1R5guGISW1ZibWE++2duF2gr'
        b'GVLY5o4HhwUQ4p7zhTwhZDAyyxKzr8XLYMLDK80ZqS23j2NhV/f5LXh7Ovbu94sdlNg8NXfqk4cOmIf1CcOeMjZ1zp8wrnSo/wPGbPTH'
    ))))
