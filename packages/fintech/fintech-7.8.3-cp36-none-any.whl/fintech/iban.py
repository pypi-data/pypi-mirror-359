
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
        b'eJzNfAlcVFeW96uVpQANouJeGheKVVERjRIRRHZQUdFEoYACSpClXhWocUfZFwUVUdw3RFEBxQ2xc06STro7Pel0Z5JhJtPdk05nOp10JzOT7nyZ6e7v3HurEJD08n3z'
        b'+83gr17hu/eee+655/zPct/jI2nQj5I+y+kjL6VLlrRJypE2KbIUWcqD0ialSbVVnaUqUxTOyFKbNGVSnlYOfElp0mZpyhQHFCYnk7JMoZCytGsll4MGp2+yXWNWhCfq'
        b'txVm2fJN+sJsvTXXpE/eYc0tLNBHmQuspsxcfZExM8+YYwp0dU3JNcuOvlmmbHOBSdZn2woyrebCAllvLdRn5poy8/TGgix9psVktJr0jLoc6Jo52c77NPpMoY+O8Z9F'
        b'lwqpQlGhrFBVqCs0FdoKpwrnCpcK1wpdhVuFe4VHxaiK0RXPVXhWjKnwqhhbMa5ifIV3xYSKiRWTKiZnT+Frdt49pVIqk3ZP3andNaVMWivtmlomKaQ9U/ZMTSXp0Dpz'
        b'DKrEzMHCG0ufMYwBNRfgWsngmpjvzG6sVUnq1A3UJz3+pN8YyTaLbiZjQwD24j6swaqk+NVYiXVJBqyLWZccoJXmrFTjkzVYaQuhnil4M5F61WODH3XF+ugErF9P/WuC'
        b'Vkf7x2Et1sJZvB0Tj9UxGqkEGlxexuNYzme+OM1JclNf10r69PyfhD0v2V6mm6YZW7DbxX11NBGtjVkXDR0+WOkfm4BH1jpjVfQ6Ij10Lp/oeKxPjE8qSV7nQ02VQcTm'
        b'6ujYdT4B0TH+CmhXS1aoGhsC9+FypsIuEBV9PBwCifoLO5LtYZe5olJJMleSzBVc5kouc8UepV3m2YNl7kKftc/IvEXI/EQOrVzaHqPVp/snvRgk8Zu/W0QbIX2Q7iKl'
        b'uy0fvUHcPFTqLI2WPshUpqe7FeaFiZuvz1BLztI7K3XL0/OzZs2S8l3pZvjMCer/8JSWfzFmx/S4ST3z/hgcIeUzLn5e2qK47VQ023V5evA/Bf8qcoW4HTXl30cdHfWj'
        b'QJfknyn+mPr9aRelfsnmTw0v+WITCZ820Mdnx4tYHRQdgNVwLcWHNqHBPzAmIDZBIRWMclk2CyptbHm5i8Nkt3HwhKSLJyQ4DneTbF50H8+sh1OyRQltGvpPjQSVziob'
        b'00NomAK3ZcsCPOVEDXUSVOdin2i5gFfxuIw9i7wZgcMS1GbEi0nwgU6G+tkpJEs8L8HpiLG2cWxE57RIug/HkkiD8YIEZ/ACPObE8PiO0XKxPxxn0zfQLPgEbtjGs0HX'
        b'8OoMGTvx5iQttR2T4DD2wTXBwnm4BhdkGx4azcYdkaDGSc1ZeDETemX3uOVsyFkJWnbAAX4fq9KWytg9x4ux1ky0Fk7mlCLGb5ShFk7CWdapVaLfrnoJzjpK8Yqsexmu'
        b'MqbPEa092CGWc4zM44FcOgGfqNgKJKjPhnKbJ7Pg9DnyKLg5VxJDToxTiBE9cApqsdsd70YxBjokODtvN59mK9yGizqL+2S2kOs0BB7AGc4yXI9OgRq3nUqFpHCW4CZb'
        b'ChMM3od9E2TsgnbYz7azkfYKTvkKwRwcNxG7bXBjs0pI+mgKPhAbfQgfT9ThbbcENtEt2gNrFJ/GaRbckUtL4KhS0KqOWyHW/yRntIz38HAm47hFgiPYq+Okxm+Pp0V2'
        b'QL19N0/igecEZw3RNKDbGXsLWNMliVbdgEf4ILhfFE5NE6GLzX+V5i/RCNm0b8PL2G3N2aoR8zRAN3ZyFrbstGK3Wxae04ohp+Ec9IpBj/BOCrWFwTEmgjYiB/vG8EHe'
        b'qUXICEAd4/si0/XOKM6eBeugnYALDlnYoJukRtiIrWK1tSvhCbVhd5hdPhc8Y8WiancSQtKoa9DChHpbgot4x5OP8lyNVSRubISHdoU7smu60N5jq4l2tzvUYLdCjLqw'
        b'By5y5lUGPEwsds+GKtbUTmKaC8fFZDfkRNaEh8Y7CT05A81wn0swYzE00gZi+ww796eDXuI7GJ2wS+eMd6GP3e+R4PK6aZy7ILwJtTrsSoUmRuwusZC3UXC3H29ita6E'
        b'zO20RszTAvtC+Ki9UAktOuyxbWPy66RpAkmanLnKqdhDLbThvWy53aTFeCqCM7fdKZtatAs1YqLzcIAEyywCDvttlq3e+Yy3SgnKs7bx/sHkBh7p5OnwQC3EfWKxzsbw'
        b'BJpwP/TqXPEcdLJJHkhwBc9Cs415angYAU+ghjmKFjwMd6FWI6nwgiIJHgbbJjKNwe7VUFMCx8hGj0IdVGskda4C9ruNtjEPv4CUuInaWVuwg8C83S5QpxxvxhMGFWc5'
        b'NBYeYI2KgVGHVCgVLvO0PccnX4M1cWrJh9AwQ8qIep7fDacduhunlSbT3Swpa3w+981wN2s8IXQlXA+BaxpjAtThJb/QrRFwcVOCtEDWEHtn19gMTKgndul4zzJoZL1v'
        b'InHOBy6A63hMzQirXbZAl82PervhQWxm3QkXL8F1wpU21j8abg50h8dqFfHUbvOh/ntoh9pZfx9XRrxjEPEbgnijWou9k21zGNO3SjXYFI2VK+AGsT3QN5hNQn0DVAQ9'
        b'x5bYZnMEdklidHdrOdN8idC7VafHGmhbP0aK1TvpXjTaAjmOWYUsHsOBoSuEW2SR9NXOyAdYNMVjoIMPWb8brjJOyn0EJ3WqDEGfTO8kXtoKNSTGaLyvJa2v3yok3ghH'
        b'Z9OYAdbh1BgmFvUaaRJ2q/A27IMq2xLquUhH4uN7w8VXR9fW4cJpS2B0biRoMxKkYrjlTKB8DA/bAmi4Gury2Dw3B0SkgkaCgWNQnk0KdVKaC5Xz8KyG/N25KJsv2+Ij'
        b'UE2M05RLsG1gJrFn7WLPmlTYm0wTMI14Ee9iK+utIYkN04hrYtMq1E5wOo+z4+wxoGg3hTQ7hmnEgizc/4oGWtzwki2YA/tesn6Hcj7djOt8+AKx2cF4GruwQUOI27iZ'
        b'a0csPjGzUaUFT/XOIS3BVYfa+UVXG/d9nSuRL1ixY8gkNO6GYJJrXwDZp0w73cdXEoYPtJytToIYoRV4lBB1BxMtlOvhAulVAj52Co6Baq4mG7Ad9g01M9IRLNvkEyJ4'
        b'kvEMudezzhTg1iXwSWbjgTA2YtdWseThqmjn67hG9iMACxCO8zR1tM/SYTfmrREReoISpupJePV5POMUiBSS2IJ4gBRLzDdFvzTRrr1DphKyU0uB8EizFZuhR9ge+Qly'
        b'g03RGU5sUPszKDBHhY/GbxC2d2XbWOq5LGZA18Vud7COk7BHhZ0hKAwJe1+YMEw9rg1XDwpmqoo1cCJUzTkJgAOhRN1AfvjmoN4OEFCp8BbRa+TwsnlPCqM+k5bBRfiM'
        b'SlwkRS3HczwL2Uxa3TPATAGUDeKH31RDl1tCeCR0zCZXfcyZnORtMtmZbMUP8Op0NnRdxBC4idBrCNPPaeBsbigXfdDM3QMYUDfceLitzZdIzKc0BBePoIzbw1ryffsH'
        b'tIgGdg+gkn2oihhz37pQsVrjFIoHKDzjsPaA/p2PI405Axe44gzXEA72a6DOafocMxdXAR5wecoexzTej6GZYtt8uEugQWR6OKC9aGSbXDRzyCYHi0VMwk7aBjhcIPSh'
        b'2RWeCpZj3xnssoPfZDhAmgPXSjkHeH0BQ1asnJsxRBccuwsVKnyI+41c6gSunXhiMKbaoJ71VjJMvUdqNjaUAxxF5sehiwH2ef0wnbwp2L3NtKYbTwomTszD89R7LIHL'
        b'TbucOZ7eeapjd+BeIt+dVXDMNmRt9s28Och1zIM20qaTGlr2IawWCFRNIeL+IQMFQ22Dx82ZtkEDh8n1XuTIO3Mvucshhs50bMDQk3eVxjstxsdwhyuAj2fyUF3rGL6Q'
        b'+XAuFJ5ooCEUW2zzuOXiPoZYYlRYBB+nzLRPNJrmuR/yHFQuVMCp5a6JcHY3t8j5uymKbor2x/ND/bLDygwqirprvDlauWHDAh4fHHUaEd7tAGfTFOGNAk4d2/CRiu3d'
        b'afWwvbsu9u6BCrvcF/PwI5E8eDmXUAtB8nA3YA9Xnqg9tpGrYbQT8UE2I91Cac1QNb4haN9U4c2Nm0QgdHy7wy8PAvNB0h/7ir/TojVwUqhcnw05JznQN2CsQ5SIqfIT'
        b'OLmKC57yW2bj9t26UDpU8NC9Cevw4Fa8uEmy5JGzHyN8azwB0NGRlO+6xpO7+hBsnYc3yEmmUIDKN/gWdGVy+V/JGRJT2EONgWAHmjRWvAGtfBR2xlLrCPNcG6Lk+wm5'
        b'zhPWSRM5d7u9KQimQcGkwbzTM4B3U1O8UJHs7BSSkM5FDBVKMhGHgg9I7IYmgyRAgc7M4PEaqM3Bx9xMJ2BZIeu8GtoGHJhdwiJ2hC61OgZqxX40pkVwyucpQB/GRofQ'
        b'i2q1M0XUZQICTiaTqTZFj8P64TottOgFFdnZYyW35QC4Ssb8TMAyzJahfhc2aaA19jlDPA/jd4fKshXL8hyZxwuhPFtahfciZOsL81mmUkUiWUzGz1PntvF4VsY7wXBI'
        b'Icoa9cs385ZSuASVshu2bRuonvSM5VnMwrGjZKiNxCcs3T0jQSvemcTn3ot3XpYtXgEsuamgrNw7SORddRTa9MgW3K9zlFvwHD4S2dVF2ptm2ULq46i4EFS3i3GtcBQ6'
        b'KefHS4Wsaz2LF84FilS4DhvwoeyqxEqlYO8YXl7Nlzq3OF+G6pjRapGbtm5Ge9GlZVuojD1TNjjqNwTNLYLY+TyslT1IrhcZsZO01hQ8zgfNhaOlMtRPggZHdedl6OZS'
        b'cIK7uI+aijc6yjuF0WKexrQlcjEFEscc1Z0X4TAfshzbXpKxEypSHbWdjR5iFzqKoI5alG5OohpwdA+5HSbScck2mTyBj6PgY9vN1+i3eqPsLsMtR8EHD5lEvaHLOEbG'
        b'bguUOyo+M734Eqf440VqWAyn2QynaYXk8dr55IRVO2TdeCh3VHzwOknMiyPB9VC5FLrhoaNKsjKKD/GF9nlyKd5frxHrYBWGB5zfVbODZLyXPcVRPckVC8yDQ0gLvAfN'
        b'skJUnI4qhDJh5foIeRT07XGUVTIpG2INm+Ah3JBHJUxWiKIKZStWoTKtBsruup2x4RVHvYUisSs8j6YZqmhh1HjV1VFxIcDZxykmBZDtdFuTrI6SixHKbROY1MrhDoFX'
        b'N/nfW3BRIcRwfDNeFTQvIhlJtxtFKU/Ysi6zCctJddjC0ii4q6PGF9wd1ZoS7OYSxwYtY9MNWnc7ijVLSa6MYjiPCbtJsTux3UmQPOmJbfYKFJwNxW6PeHcnUSO4GIUH'
        b'7IvDfSnYTSnWHRtbeRfzrJdIJ/h0p/fAJewunoY3lULCDdAhymMp0TRfd/EreE8r9v5wAnYJC7uDj7CFFY6SXB11o7lwxK7GZpkVgI5jh6NuFF4kpjqAx5KpKRSPOqpG'
        b'WLueN6mhQhSb2kY7qkaT4YSg1+6FFO7bVLmOohHcCuL7kgLtYdRQsNwu+Ua4k8gb8rK30v0UOKIRtteEdaWc792EtLRYvLsF7trl3uKHVXxQGKHLKex2nxyiFGyfS5nG'
        b'G16YSuLqdh8f76hMReJ5wVnlxiBWpTwjaUTt56KNHBtbTtgCguBu7J6ATxw1K7hfJLTwfC5Jj9rGr3PUrGg3D/GZxj6PbTq87QdntKKpVRkmZuqaj2XU8lKqo5g1Ae7Z'
        b'a7ukLCd0zm7YoRXFpEvqrdzUjXg+VOecpneUuXRYJ0x9PysD6KzLF9iVsik9U2zqA5LNCR12wRVodpTANhQLa2uGxsk6V7iU4qgyOW/h89soNq3WlVDSxwuI1whPIwwC'
        b'HDv2QIuuBNry2ZDrFHeTD+vhrK3DB/hQVxK+wlFNm2kUCvKE5rmtw56JcNNRTtNaBAOPoFNJLauyHbW07WsE15cVr7Aq22lKv+3VNNwPd8VS62LidR4hS5gIesllkaCv'
        b'cK5fJvW/r/NgvpCpW58E7eGvcBwqjfXUYWeqr11q58Nni1keUvRNsumEju1sxH3abCe8LRZ6Gq9461wo2GtQiomuljrKuLVkJa062/Zwex27eWOMoPckGFp1MtzDRkdF'
        b'D/sIi3jxvTt2vU5O09q34Aze9+fzGOBEITmy25R1nWdCeEx7nbTIFsoTFdqzCmpsgsoSUcqDDnuYB5UhrHanhm6sgvYUqFknbdisZUVCLDOoOY7h45enUPh/AGviY7FW'
        b'Jamwj2JqOO3NhVWQCifisDpeKymgWblFEYSt8NA2hWcbtXAvDuuDsM6PVLrewM6m3EarxhLodoj65EUClwPYjMf9EgOi1ZJ6uQLaN2FPFCuT8x9aicQOe/ipEjsKrZD4'
        b'gRU7vGKHVqoKl2wX+3GVulJdJu3W7NTuUvPjKg0/rlLv0aRKWSp+XKX++Re0B676QT8R7DBT1hsL+CmmPrvQoi8x5puzzNYdgUM6DvlPjDhD9c0rLLAW8vNQX8cJqt5M'
        b'1EqM5nxjRr7JnxNcZbJss08gs3FDSGUYC/L0mYVZJn6iyqhyerJtm+Ok1piZWWgrsOoLbNsyTBa90WLvYsrSG+UhtEpN+fmBrkNuLSkyWozb9GaaZok+JVcc1rJT3IwB'
        b'KoEjDcgwZy5hy8wxl5gK/MUoxuCKmIghHJgLnlkR+8kkwZi2W9kSTMbMXH0hdbKMOBFfm2XH4MmsDjZJlH/9PFZ2bm2nFqhPsMlWtkYm97VJAfPnhYTow+OTo8P1wSMQ'
        b'yTKNyJtsKjJyxnzZb756E6mGzWg18WPw9PQUi82Unj6E32dp2/kXEueqZV+Lfq25ICffpF9psxTqk407tpkKrLI+3GIyDuPFYrLaLAXykoEZ9YUFA0rqT3ejjPkyv82E'
        b'XGqWhy1myLG4tzT8iFafKM6u3F7EdrlYpXKEl3CjiB++RqVNkChzmLs5M33p2hxviQMhHt7oDDXSfLwnSRuljdAyh/fVjHWVCNm8d3ul589fbRant3K4hzRZkqIjF6fH'
        b'R7v5SwLMzxDIXpV1y0QUyAJE6I0VTY+h5wUKENvwoeNIcBG08AOC/J1KeVQoT/PYiWDwfHGGhodmk6ddsNRxHIi96wSO3sdq7NFZKLI64TgSjCN04q5xP1zdqiuCpjCV'
        b'iKOaN9nPCl1hn6QrDmFQxz36qbAFAnnPbcqAGrdZOfYzROybZ58lgAK3bjkEy7UiomiEB1DNZ0nFJwZ2vHhop+N0MRUu8JaYADzOThcrFzlOF+HYaLs3TYskbx6Oxxyn'
        b'i6O0wpXcY0m9rnQJnlYJB3RGCSKIgw44SLkhhejtwE+hTlE8lgz1Ij44BHVBFFiXBTuJ8L0hAO8Jig+xAp5Q0zmocQTjS0cJ1H9CDuM8xWqUJZ5xhP2UHQmvlkLNPeyw'
        b'9waUSyIwPDlpA99uxU6t5EZZyU7/dLcxkb6ScHUUsDXMn6vOU7NTKSmD1n7DMIo3LSF/1Cfr9k536EEehVxM3ia4XSSXplscSoBX/PhyLFgfRbH9Gbjv0AO4OkHMUjM+'
        b'lRShhKIcuyb4zhfrbJqzQWchV3Nv4GT4HF7is2yMnKErssIjhxaY4Si/vwAPr9AVGzIdSlBM9/nunNiyhrQA78fb1UCNHZytULwQQlqA1RsHtKDPjZMqjcEyUoKkcQ4d'
        b'mB3LSYXg0XHsxPPhHocKhOWLDSvPyyUNSElzKAAchtvi3HImntWVUoDU5tCAxTqhzlWuUWz777FTOLH9HnG8ZRUFm6fk0sVejs2Hx+SLVWIx16avpd3vdHNsfhg2iTi0'
        b'DsoCiR5ehg4HPWhLELp2gYLEMhpGQYmDJoUn1QalkHU1np9IeoPXXnKoDRwv5FS1uG8OU5rz+MShNHAbn5g//fyEJLuTdN4v2ZRwuDNWPW90eU7wW78xT18feP16Uvrn'
        b'Yyovvz1u0+Zitw35Pwttir2vmu4sfxh28Guvfyn72jnsUFN48rvxfYXBfxr95Y5XQw987eI6uXf5zuduT5x56Zgla8PcjjO3ZsYn7gr/r9tfvfZa3/3oX93s27Pvasf7'
        b'f3zrux/diWy7+m+rPmit/J1ubPO94xEbP5F/9sv3virSn5/QtCZuZlzews83VwZlnPrnT0+93fHl/I/Pfs/p42lv3Kor1eREp20NzLz+3r0HP/50wYbNITM6Zruv6Kpc'
        b'v/H9L+KWqX5vu/in3zX8/bLXWx7M++jgzhMr/lC37LP0N3YVLs397po/nb/2xmy19lTc5sdfTf60o2xZbDce2DX1Q2e35yd37JUers2c3fhrg5OVydPLa4VfgM8OOBId'
        b'oJS0cFIZQKZw3cqOcDekrvcLjPH3NQRigz9WLSbLkrz16i3QA2es7AiX4rhWPBuXtCM3AKqSeJSmW63EekURb6atOEHaUINVvmF4NCBQQfQPKOfPhS4rq0MF4gU8xyI3'
        b'PLWdP4JUKh5BKgnwxeogpRQIjzV4B2vgkpXt7iLoZMQS/PHJ+Bisp+1eoPSImWWdTm05JjwZJ0YT9w0skCxdr5LG4kF2DtqLVwzKfqWPwcK8ksGFf/21l2vSN2OXZlsK'
        b'd5oK9NniabZAFu6E9bty55vG/sNcn5zKnOBeyaBWqBXO/OOhUCrG0fdo+rgq2H03hZb/rqRvLX0709WNvtlVTf20Cm/ei/X2oP+pWS/lZIWFLEFKtGgY/9p+NZuzX0VB'
        b'VL+TPSTpV7MYot8pLc1iK0hL69elpWXmm4wFtqK0NIP2zy/RoLawJ5gsLBK2MIy1sEfrLCw45vMeZ6sbzVa3T/psslLLuOdX23QOkfHOJHu8kjlY/A7hY3sJgQHThhlh'
        b'ljhqwJpErE+K0bBnUdo9ilShgTrejEfg8pa4eGoM2jyBQnqFpNukxJsboYub/Vo8AwdEIgD7oJplAjp4xOCT/2gGB/LB0sATaOpstT18V1WqKHxXU/iu4uG7mofvqj1q'
        b'e/h+kML3DxTDw3f+BOKg+N1SuE1vdETcQ2ProXH0sDg55c+E8xZTsc1sEUFckclCIf02EW06HoscGm8lOcIwYsR3Dc1o3mZaabEUWnw5MSO1ZI0cpTN+GbsiUh++iBFD'
        b'VPuixIjhKxxpChbXR+Ubc/RmkV1kFlosJrmosCCLwlEe3su5hbb8LBauisiT5xn23GLkwHSlmS35aRxMOY9RHxxgtRVRfGuPdrnUKEz3YT382USGPxOmqp8JUzWJNpb/'
        b'RRO2lY/0/GVVvG+sP2WwkXBcPI3J7iXFxyQoJLgOVbrFmRkp5p1ef1DLy4jMMd0Xv04P/KXBuDw+2pifnZ/xWfoP6fNZerRxa3a9sd3UZvos3ffddmObMT7TNbvN6Jz9'
        b'sx9I0vQf6VZHRRiU1ueJxrZxq3S+LLetwloog+YEmx0Xp0G3Gm/BY2izsgdl8FZQWFxgbIJ/DCsvw50kYX4T4Y66ABuJ2hBDHwkDNA5r79eJR26fYpqHwLQshmaeHNMs'
        b'o54ikabf2aFT/U527RBQ4sYu7qzP4OlVFhZlWxiUiG4cYhjB9wdBzHXPwRDDl9gHFXDSsciILAfE8DWGz7IxkeMduBT+TBHiGh6jyLWLPNE5f9XmuAVQX0yx7BVyJPen'
        b'u1Kc2OiOp/HsTg4x5udZXchDIQVAjYJCQrxOEHWDBzJz45W6kmIFhbpaBVZSaBHrePKxYQoB041oGXtGBaslJTYqxmGHKBKrV1PgGWxRSht2KgopuoYqCpiZ1sWVYJeu'
        b'pEQrpS1U4CEJT5qSCCNZy2zsXW8Huc7tDOPWrefgSNAIl+y1Du3CgUqHG4g4ezXlITf8CDoV0pSJSqhXRJAEvgUc2WM1FSoOj+LRXGWFc7bzAEiq/yxI5hBI/uHbahzc'
        b'uodWOL4VIhicsO5/uVLwLQk8G/w/nr9n5nO2ZJP12Yx9GINMLoWZmTZCw4LMZxl15Owrk8P1EeS3LQwtI8krZFoLLZSFF9ky8s1yLhHK2MF72tE7grJ6izH/GXoryCwD'
        b'B/FmZJti40/n+66NSPH1p6/ISPYVkbRmHn0Te74rglfwhogIX/9nKA5akzFfLhyx8sAWyeVcJOoNRDWLAfeOomECZD9/lUscoFhY9KwnZD9/nTccsnn/bQUP9vi77hlP'
        b'4pkYZQuTWEm/Gy78OVcyoh/B0/BoMdSE8lzXY9qEJa2qdElKT981Y8dGUe/of2GM5ZgUTb+l7/rt+JX2BPgutARDjcTKJWT7BzeWwDUBUJWwD09BDX1Xku8bkz5L4eKE'
        b'rZxSWJyHa78ilOAtPX5GqFISj072bp05n77nSTHQMU+GUxyYLHgBKufTGoMpXYV7wdgxiZO4Y3punFq1XJKK0v3D/baL6s0rcGMGdlPkmCzB1SnJS+A87zvKy3XNHyQf'
        b'SRqdHr9n9ktSCmV0DPLx4qoSMaP/9Hkr8Dq/uc4tX0wHHYuDoTXV3ldPqYno67J8HpRP4fOtnEl4LubbC93JcNTbfMXrsFq+TW2vzlHPqp/nAXPdVn4+M+Gcr8n4qzc2'
        b'3l/h5P3C9thLHh46T3/1THn/1LL9Zf8RP7Ojt/dPT/q+0nxUftspfJRLmM9xp3lfbl+5xuXs9rzXt8868YUix3uU9vWim0t+smuFz4aT40cHrH95zdJ/enVSZ1/s4bke'
        b'30/7oufOR/fb2uf+6tx2z5k/Vqzze2VViFG1tCPvzY9vuIfsmf9+y+9f/bfCt7z+7h/y3ny8rnndP0xZ8HezLm4e9Y/vT5vhOb/3gsngzJMduIRXV/kF4O0on4G8DMsX'
        b'8sBgHBzYORAZDI4KoBKvU2SQSdkZf06tD9s9mVeg3CyJErQg6heAVXlwDGvjnKR5eE4bA6desU6lvmMXYIsuDmsNCTbyl5V2mmOhQu2cD01WpgLzldgclxSgkJQl0LZX'
        b'EW6CB5xVmb2vQjleND4OSmK87lH64tnJVpbLbyvYQRkbe6DSfyBlA3K41kls33t2bozDujiWXnrDYcowSUfmqnKgMdmgEAGD81+dqj2NYVxEWkZuhkcwc0UEs5f8sT0v'
        b'Y1clZVcePAPzUKiVLNuaSR9v+8cyZlCM8zQ36lcR4g8Kbf5SWqUalFZ5DYQ7jPZvBoU7RycOz6iWw024b09nl7KoQaTWz2GFigKZ+/DYoOCVkmysgocuy4cenKyDe0Pe'
        b'yxlw/Ow5KHL7ymzlwPs3im99/8bu7L/54RDkWyOQ81sC+2wel3MfPfhM4n86ExoRutmP8hno1ibaFtPv47cu2zz5b0buxQErOBSTXYXKxVA2Z+A1mbMG/kTWZt0Osh+s'
        b'TsDatVgZr/RcCdfgEFyGFvbLBawwSMmjnaAnGarME2f8WsNDtfXvX/91uj9lEo484s2M/Ox/zZLejTfEv137+tZZPzD8IH3CG/7HPcqz30jX/tDVapWWurq5ql4xaDha'
        b'BMEl3+FoAftyB9IIsnYrq+Otg9seBDht/k8BJ0BrZaXa+MiSwWWgBQmiCpSgsLJjODzqvciOHIJ2DV6xI8fWAlEl2ueJp+OS8vHU0CpRwSZhYcoRzdgpx2QdMOLRDiOe'
        b'zozXmRdOLOOeGqlKlC1GzjoUopEbHxvjTeYhewrj2yd96jHY/Di/7QHQGscQMwlu6J7yuzzgzxiWskL6mwyrfYheri3KN1vlAesRpz1kInp2N9tizOGnN8MsyWGNRv2C'
        b'EXPhIZ19IpLWJaas2eivj4heGRG3dl0CJcnhiXFpEUmRK/314RG8PS1xXcKKlWsM3545q0YwGu7dr+VpQ2IVBEv6dLdNG8MlfjRsmAzt7MVDP/bmYlX86miewuA9Fz+W'
        b'w2CjAa65QssO+sRA1Q524O4KlRlwVLwm8Aj7prDRcHamgwDZDce6qdimJpOpNJvdkso1chJ191/4n2Pf6nTfN9dN/Z29V5fXHj6zOPXA2JcPTmjxWLPEXftWfkLubxvL'
        b'v/P9Syv+T/TKiuc7k777bptn74kI3/jGVxM/eVBv+FNohzrkB793yu0b/c6jFoOaezA4gtexzC+AWQU+LBGG4U1RCPOaauh8YbDuK9lJehXXfTxqFI68Qj+RFS2Z+1uB'
        b'FdwDTsFy3pY2YUUcd8o+Wmk2VLp4K+E81CYPUd6RjcOVEhB5UJru5bCPec4KN24hHiJZ9/5/sBE2xmeIjfR7DM/Ioc7H2y8azuJFf99EVncQ2zIOHqnHQg35b/FUcguF'
        b's5eFfyJcaAiaiyehWkDAxL3qXDyC5SPblL2Ex18hHSjh/RV29fPNw0t4g30Wr3UVGLfxPGgEV8WyIHZeWmSiG+TShjqPGGFd+UarlZKaTCP5naFEuQczZokq4TPp3BBa'
        b'A6ndX8rsRCb3v9GFKkZ0oc6Jthck9nrp5bXMg0LVc3+bE1WO4WjSU+rNToVT12ekT74jG8Sh7rpgbMdmvCgXD7jWKrzPfevUSGgO3/3t7tXuWuE81nD6kVHsjWHJucsv'
        b'Pb5kdLxk/teyJI28nlo+SIwe6nA/Tc/Njjd+L9t/zafpP8hQf3lgwhLvrhMnJywJXyC7yis75md2JrjEuepSl81PXXZ9ZkSAKnlZnnvqbtcIimV1Ul+Q149Pxhq03Bnj'
        b'faxajj2WEcN35o2b/XjoHpsIpwZF7jvxSRIvnWM9oU2CRlqUqN2TAy38AAeOY7evAChJG4nHGEC97Mkj7IKdygHPnbqaB9jMc+MJGsp8d9Ay3DeAXwrc9zTo1+JBK7fg'
        b'auxZiH2pwh0O4WEaNKrxdDEccQTrf6m46MY9OqkzMxYOW+McsLWSgZWbwlUpXLubwjJxEHD16xjQpRVaWDwwCMBGnJC4mTQAZYzKkiFQ9uaQ4qKe7q5wU4+wusiJYn3O'
        b'gQZVYmKUQRFlUCZGmTMevK+UvyaKm7+5uu6Iee2Y8NHlOdnfrVo0/efaI/hSb1JvUkpy7+rVP9l34EKYNsFLc0H74VfpP/pw5cXte25/7fLH6FeavC6/t3Dth799b9rO'
        b'kLCFnilO85Iudv/9L5b/JLP/6A/WFxf4vP3Bc+MWXPq44YvWTe+8ftLry3ErV244WBWYl1D7iwUuSUm/Pjox7z3f9nPzcqJ3Llnh9F7qx8sXT69dHTP2vZ8kx035asE7'
        b'b844mRo/P+DOu294Hu+q/fhG+qzrqQkv5KV+f8nfd++vy8+Y/9IH3wvp+fGrHiVdNR9+Zgz6zw/+bv+P6t/5pb4iNP6T3o9964uOZlp/9HZx4jsYk1h8cn7rx5M/+dXH'
        b'B+aOfxB51tr8YMWLGy4/esO2xu3NpW+6FwS/Nvfe/bedS1/7x1kfbl79U9VvmrKPOi2dGXF81dLs+C3rT8xZamp1+YfgmamLmn6x/Q15y+Gc6uZ/f3z+rd9rZmfuaF/l'
        b'/nu3CRsezf7pb9qC3/Wv/Li//q0P6j/+4Ezx261T/9S0ptcS321JSG6uWhz1m6zJH147+J+n14RvO+z8ac2x1wwf/NcXfrs+n/Tke7e+/Nza+n5vi+GfX68LyG3qDUj9'
        b'Ly/Tuv4v6n/VNWPqtu/8u7Xtjz/64RdnRn2tbhxX/dvmW69tNExq/8POV7P/T+q/VTz8xb+sDW/u1u06E+PV7ffHj2qL0k74FZ9f98u+47sa8y5v6/vy8WcJ575ZZ/mP'
        b'oGbFu58cnkWGzI/QywLmk1/DJmxSSIpQCeud4DYvx8uUhZ/VxdkoexgUF3CjgpPQw48r8VjqS89CALaMESiwLY6HB4XQhQexxj+tOAbrArSSdovy+YkUeTD13gVtoX6x'
        b'AVgZAyexKT5RI+mgU4mnM/AGj0zIsx4OYqdyDdQni/rUxrAut5TYDved/8YjUIPH39T92+loLMzsR7xwhHBOS8svNGalpXF0+Bdms88rlUrFAoWen5x6Kp3V4xTin6tG'
        b'SRbszK//+/45Kz0V7J+zwkvFag2TX1TSCrzGuNJqvBWTfZSKiaPo85xSYZnsQEkCOmVa2iB8c///l7jCMmUADNlEzAmJQ52fzh4MhKzXKLU/1EADNmAVXEhPiocqaHCS'
        b'PCaopkjYbfY59B1JbqZut++UBNQ8coXlXpFnAj8pCEl63nXcgdyPxn8dNO6NNfd9ImPOmw9e2mTs2vv5zTcXzP9krm+1U5Rb7uVFiVETLiX85GCBemLHV1HFMT/9qtC0'
        b'JfFffzdu955bZ+r0UT//6NY7r1X9rPY376Q39lh/Pn7H2aip0Zd/99Nsj1uG+5v21qev+H6tzrX55eIEdL/3T5s/OWn+o2Hp7Mmr/7lvVuScMJ8nBneebK7Qvcz/yEoS'
        b'LaN2XF6cE2l9lxLbgkZxu4iCe3CdhQmdWBUJt5KSWMXqOexVUeR9/kVuwFCGNxKEIOKgB8vJQqGOS8JTNTXQIqL6FqjC6qXQFheT4JvgJGnVSudCKOf+OABO40WohgN+'
        b'sRpJESeRt+3Cait/2/RBMLQOKSzAkRB+aB4URyBAiIENKmkVdDpBA1Tt5uxs2kwrGTzEdR6N0ErjI9W+cEcnjgDL1idjN9aSrQf5FgekZApAmWhTQ/kSuMezeDzruwV7'
        b'N7B8Kg5rnCR1gAI68CY+5ogEh4qhhbtBzkn3agczk+CUGq5sLeXS24gHCFhqDNQNbsMZpilJ8Qpp1GrVuuexiUc4E6H2edEDG/xpXaGuInNTSHq8q5HgHIjUyYdE2OaX'
        b'5E8BBnGEHSFsp7BPifegD3uH5CZT/nvQ57/xQrnUt8CXucBstcMXe91TcmcBDWVkKrWCAQDLykbzIIeFOa6qmSz4CbJMHYCAaf2qfFNBv5odmfRreFbfr6b8wNqvzjJn'
        b'0pVyk4J+lWy19GsydlhNcr86o7Awv19lLrD2a7IJPenLYizIodHmgiKbtV+VmWvpVxVasvq12eZ8ylz6VduMRf2qneaifo1RzjSb+1W5pu3Uhci7mmVzgWw1FmSa+rU8'
        b'M8nkB7umIqvc/9y2wqzFi9JEeTXLnGO29uvkXHO2Nc3EMoZ+d8owco3mAlNWmml7Zr9LWppMuVdRWlq/1lZgo0TiKbSJxU6xsAqXhb1wbGEPXVpY6GthcrOwP5xjYfpk'
        b'YdUVC3sjzsJyQgsL9i3stTTLAnZh2m+ZwS7MviyL2IWdD1hY8Gphr95ZFrILe97IwioSFlZZsDCVt+jZhdX7LCxjscwdAEq2Ha4DQPl15CCg5G3fODseBOofnZZm/93u'
        b'ub6ZmD30T17pCwqtetZmyko0OLMHdLIKM0km9IsxP5/wfqpddVhUTPddSfwWq1xqtub2a/MLM435cr/b4MzMsswhwEEXoX9Lxd/VYn8WRdTM1Eq1ypnpWJwXc0qK/wuy'
        b'm3on'
    ))))
