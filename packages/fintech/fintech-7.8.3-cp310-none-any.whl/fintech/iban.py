
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
        b'eJzNfAlYlNe5/zfffDMsw+aOuI07w6qIuyYioiCrotEYIwwwyCgOOAvGfQFlX0RQQUERUUTZBHFF0/dNb9u0WW+bpiRpmqa9TZo2zW3Sm9y0Se57zjeDoKRJn/99nvs3'
        b'D8Mw5/ve855z3vf3/n7nfJP3hUf+KelnGf1YltBLmrBJ2CpsUqQp0sQ8YZNoUJ6X0pQNCvPwNMmgyhVyBMuYZ0SDOk2VqziiMDgZxFyFQkhTJwouGTqnL9Ndo5aHxWl3'
        b'ZKXZMg3arHStNcOgTdhtzcgyaVcaTVZDaoY2W5+6Xb/VEOTqui7DaHFcm2ZIN5oMFm26zZRqNWaZLFprljY1w5C6Xas3pWlTzQa91aBl1i1BrqnjB/g/iX4m0I+GjSGT'
        b'XvKFfEW+mK/Ml/JV+ep8p3znfJd813xNvlu+e75Hvme+V/6w/OH5I/JH5o/KH50/Jt87f2y+T/64/PHpE/i4nfdPKBByhf0T97jsm5ArbBD2TcwVFMKBCQcmJg54v4uN'
        b'WRmXOnAyRfpxp58RzBmJT2iioHONy3Sm9y9alQL7zGvM/oDuycMF2wz6AzuS8Q4WY2E81OPNmDVYgKXxOiyNWp8QqBZmRkj4AI9ZbPPoUmiEYqika8uw3J9uwLLIWCx7'
        b'iu4odl0QvCYyIBpLsCQqBouiVEIOlLtspqY63nXEWrXgRj137MgJmLB3qmDbwuz1QDfewC4X9zWRZLUkan0ktPpiQcDqWDye6IyFkevJwODOfCNjsCwuJn69LzUUBJOf'
        b'ayJXr/cNjIwKUECLFA61ghUKR81LWZSqeCTIPBzzEvcdi5TuYV8GRYFIyyDSMij4Moh86hUHxMQB74daBhf6cX1sGTrkZXg+3onPRcI0c+Zns+cK/MOspSJfm+TxKZmT'
        b'NSHyh15rXQQvQZilTcqJUYfq5A9f2KES6Lc2e1Nq5ltBw4UrQibr6mTsWOn59A+mC8J7M/8q9syeNjlOyGR+ZNtqFB1OgnbW2LJZb5pzloTJH79k/KtnlafC9xMhad4f'
        b'vU/HjRP6BFsQNeyAVjxMy1Fs2BC8xtcXi4IjA7EIrqzzpWUpDwiKClwdqxBMni5L8Qw06YJto+imJ+AKllvcaMrxNLQnCnASDu+yDWeLXOazymJWUUPxxmcEKDBH8hv2'
        b'hOIdi9mJPi6FUjgiQBHUxtpGU8taKKYm7GGxWeEDDQKUYJXS5k1/j8JLUGyBMpoobMBmuChAHfbgWX4f1sBNrKRWygG84BIiQD00WHlTJNzHM5adzInySDhBneEN6ORN'
        b'cApPUBt2qqmxestUASqgIpW7mIDdbhYbu+k4XoUzAvnVup+3RMI9uGJxZ7ecw7wRAtTAubm8ZZF+mAW7mH+noA7yydpiPGcbSS3BeHiyBUqYo2eT1QLU4t1h/BYsxzo4'
        b'bNEwt89bl5Ax7F1kY5GzzwW6LLsodPEk3htNM2nbLt/RDkVKiyd7dz4VTwlwOg175TmoW4u52OXOHGiFzoUCnMPyA7x/uANHPTV8Ia5SzMLpMKixDaMG/cx1UEwrp3BO'
        b'3C9A20J5FWLxDjmF19mKVi5FmulyODPTNoZ1Uoy1OuyyMccu4C0sF6AKa7dzl+HouGwNdrBe2rdl0BJY5d4nzcH7ll1siJUTNGyx67CajwVKvWZY8CZzuGYxdghwPA3b'
        b'5FHewbtQZ/Hky4k31tOULdrEHVCMxVLscmYNF6npigBn4CbU8bu2QQPkUyPz4DLmUyTWL53OXdu7YTh2WdnnNVgbR+OZNYFbg4JsCbvc1PyG+1BPMQW3KTpY20zs8qE2'
        b'NgnNUMnCtJ7i9SwfUk7CLOzCTuZ5o4D3KeT9VsuLkEfhdplgjd3W5kNB37AM7shRjw3QSC18fhasFeACnpjCW6ZbNfQ5m9IOLNvAoLYaDvOgp1k4bqPplqOtB7tpjuAW'
        b'3pJX9WTUWFpv1lOHVU/2tkM3d8KGLVhL/nWxphZykuaowls22IO35rImln2teArvsGFVDZcbj+yBK7SC3HdsgSKWYoewmzfCXTiEhzXOCm7kLHQK0AQtcFMOi3ao26LB'
        b'68zqDewcR87AXazlc5/oiQ80OWzUrSaJpUvdGnn178P5SA32sEnsnJbGpr7RX57EZsqxU9TEht01ZQmL5PNa2cV2GksLNal4T4ewjWY4C0/Jq3kB7oy0WJmHBVS5KgQ4'
        b'hjfxPLc5lkCqXsPwmEycg6OUBBtpoXmwnV/qqnFlfd2G014CXKLx3bGNZQYPQ9ECKJ6HFXADSlSCEi/ExCjiJ6lsPtQ6Zi4WQ3EOVhGIFakEKQML8YQCDq/aZptIzUbs'
        b'sdmbQ2QDC/CCSnCBUnFMygSdkicgNh+AHix+ah+tfpaQtcWf46bXSiiOhhMZ5G2KkAJt2MovDsVOqIkePknNakraQZpfFgZYtX6sfdCQl0lj3oUltunM+6sJawngCuDq'
        b'PLii0sdCKV4c470tHBo3xQqhFhVU42l3eeI6KCu7LDxBCuEaJUg+zeBdmy9ruwzFwx1m2rAaq/jbULiK1bOobI3HUsklEy7LiHoF27HBgt3MnYpl2EXA9VQ2t0NgUb9F'
        b'tkO1v5kZioQ22c5wbCVD0CspNUlyBHQswlZ7SRmGTRTqWIHtNh01PR0JuQ53Wge4cw2r4QbWMYcqJXW4fW1tFCSHCXoZXtQnUySd9YZ2zn3maqATT0TCNZqcfjMhzDHV'
        b'ATISqMRbcMOZz/A+uDDXYmahk7+GJUUeVi/nvph88Uz/1PAZhnvbNFoKi+anRgirtTRfPU6aBQ5Qa8Cb2+3l8BmCtAK8h1dt/qzaPDvEDEM7wQ39asFqSQg0x5lVO/HK'
        b'SB4fT67CKnsBtVkJUX0UvHrvpzy51j+mUmWK7BChTi1e3AbFtOyReMtlthpvhMFFvvJO2APXCOqZe2VYMYIVujIotU1mi9k+funAGWLLJa0VxmGXkuCvY6OSp3cAdGgs'
        b'rmx+T2P7agGqk5Nsi3jcYMsaPqqexfYlL310zZpjmfFrseqUWGEntDvDbfK0VJ6sgi2RFihik34ObsfQwj2F5XyUe+EiHsUToU8zfxxrpyRuWkgRcCydEq1WmI3nVFBG'
        b'HuXJUHNlFOQ5aAUcP0C0wjKSryDcCcUjg8JJDkqadGyIZUF5Qon3oOcJHggBPvMtHmyotQJDkJNwnbxlwT0Nq8KHyhHm3Tke3JgvOQ1L4lYMqmEOHuPvzyD2FpyyzWa+'
        b'XaV+ux12HlDmtQ2Ys/5skYTQvSpiCsU2PrhkrDrgYD5w3pPw3IhXbHOYvdsUie0Oe8XbBwQ62SmVl4DZC8FyFZwnqtMhT1fDUjhup0yjqMAROBRb+XRhJeStG5zEjqXE'
        b'6lXQxAbaKjlvNstgfRS79Q56hV1AdbKCiuMxWzA1xiTSzDjQyWGIjF6Th3yNRz0UeY5UWSj77YTtLjGTNrLIQr9mNDQT+9CPlH0ueWaynbCN4HyNZq+RxwvWQ2e2oye2'
        b'rlVURHezWIFjWrhAiRqLvdiz1CkE2+gWDqmn4d4BO8czIWV8zfgpPFGxeclEh6miVDuqUoph7ibfefJcWuCcM5YkJXCvJB3ecHDCWLhB40/HS3z4kesfwtjVx3LePvqT'
        b'NIM3VRY87SWXI0IkPGWRi3cdXscWBoyNRBFYX75wBIvsVBKvQCF5vX8uX7XtQVPtXbnNglZ7JdgWHq7FExyo4rHeKYhowB374LE+2M7XsHEVrX70OlsgC3LrvofgMshv'
        b'ORYkIQjursBm1TY8O1uG8QLIhxuWXWxZqtdtIcKHRRRjLGOSds+zG2sZXFMIUYmyjJ+pxLuUDze5S9PHwlEHUYx2oeVzhSoO4nt8qC48AlGhLF0WQJVESNWjJJI2muPU'
        b'xPXuZIJVlLPr2cRVhW7mn++HujA70YwZzah55RLbLOZ7pwcxTfsKUYf2VLzyaCruVMFpmrJu7uhmuGu1eLJOLsLZOQRaUcTVmKN+znifOdo2wAIvNlQFrtJwlUpsT83k'
        b'6xjuSpbtDHftZuJuJBIuytnXRMztmMOn9sHZB8c2suxrlJyejOZ29mmW9XPhw4wo1y8mnhTK4ujQ6rl4Iv2gA69KB+XgPAmuu8WGrYDWGYIZq51phovxHl/PZ0gxdTqI'
        b'9NNwnIh0OF6Tc/0q1CaTe7zyn5f58knsduajhzxfqiuPFkqKvwfYqBJC4bwKzoWPl1P8KIPyLje21k1eSWz45B5fEaiCpjD7al8KcQThQLjlpXIOnlFBpQQNfEX84ezo'
        b'fobfs47gVkqwBVCDtzn1IfyU9mMD/0RJM+C+be78WMUaldOClFCZABPiEqG0KwJSo3VMZfamcGDI2gQno3kxIyNyMenPM8631kLpBNFpMtasko01eBKvlwlzE9Vgqia1'
        b'RIh7uWtUEArIzAnohpJBxZxbY2V8Dtyg+kZUuINX8WcJS0j6eTBr7XFYwCREHcEC3+Np0ELXozkSwgabOoelSCdF3t7pPGJmLU0nlOaV5Do2OjEmfDTENpVz9WmknAYW'
        b'ODsZGA9HlIvX4t29MnOntovTsGsnM3EWC40UIMuoButkUt85dxDg9+fAgvms0OYrSfXVwDWeldhrGUF22LLVjfQh3Nx80DaNrRocpfB4ZDQiIyU3lXCFmFlnzBI+Fqcn'
        b'hvcrNMxlmxImml3WsnE0MQW7QCP1TZPVEBEiw1UlFhgcCm3NKKbQLkMXv2kCAdlRh0gLRlr6xrD9cmxXb135OATRHK2EI2x+O2h+d8iafiG0THKIuR27CcYUsqYXSe7U'
        b'UwNPnflEX6Byiq9tJjOenzTcDhstDuMUFSzd8xNl2OjGymBZg12aSXqoi9dAYppAGX8Cj0TJYFazI9I+99uhbVDOtA1gmbOxVgX1G/G2PB23sCCOJvEGT55pLiwDcnfw'
        b'UoBX8HCs3WDEnIcREepgebK5DSrSndmysbatBOhd7iwy2lKCBKIbvSTNeFEthOP9PHrLFHvmMIDor1AJMU4LiSjJPHqtmhbOrntpiU7ROnkssSMEXmNlla3GgamOvG4d'
        b'PHOEEPBABeVYZJNT8TjmEnHucmcT1wl3J9PaEqBXcUo2kgj1STwxDQ4NKHxiqt0/L3Lv1rxhUDBXAWeWucYdhAfygiaQhHTo70jGoM7MfIJnwRK4iVcfkx0cwOm/C7Sk'
        b'OiXezIAjfEkJFjUPxXoLUk2v10EJBwnnbCrzj/InB6+zEwjbMsxVZevHyIz6DHRtJnXPVrM1hpXAs3s3ydKsfuWCx0OY1eLjLIPG4W0lXo/GSjnFzzyJd/o3CcqxmCA1'
        b'ZZzNj8kh7J46JDkkUwrk5PCB5ME4jkzZ6vxzNM7MnRskxc4KcBHqn+KztACqoftxzGLY2oG8sLcpsS2dBDBTQ5M2TLNvS0AT0ZWmZRbujR/ck/q5GvQ+JGsDwirAaT7e'
        b'sW/FXSd22aOx8sIDPfMoe/w3yFhUO22UY29jiY6iLSSHl5aZUKCz7xvsZIhwSQ0nHXt0zRmaHInnSQ/QDFWvfIb7RGA2cxAVfRiWmI9H7TD4AA678x42YdNITY6aV9ci'
        b'bBXg1IytPCwDsPBZsnNMOVRUQtcmYi5527Bxk2DezkTVRQP3axmx5x77VsyCMLYVcx/ligNnzQQWJ7AyYgidrxpu11TXSCSETeBRMHMj9Dr2boZjJdu86SQOxLBh3PZl'
        b'j+nzh/JPVrNwYu8mlRV63bhfa2LxqmO3B29ks+2eDicZNS7rsM2x27N2F0E1HCZElne/sHusxoOt+71VtFrNJrgrg0ABtDvAjhTkI3psINg1UH4pBU7H4cgkvPhwZR5j'
        b'Fm2qnXMVCc54e4LTPGxQc3DOGEkQGDL1Ee0I11QptAKxQsgYFZTgJR2vEh7e+wexffu6s02L+ni27NclaXw0v3S5STuUlKQO4AhTpFgkOZsX8cTdBLcThgAT6oEg7BJd'
        b'u1iJvXA/gs/LKhI81XbLUXGPoM/AaTmhgrNwe7JO3vyAquc2azxY3btPmE08pUUVIG8aHcGmLA128syLw8O0OJiHF2RM7aWrK6hRyctIO9sIavTDu9yiZkq0xoXVgXvQ'
        b'+hzbJyAdKAPCPcqWyxqbvIN93p3i3SgLiSmk5y7Yd++82abzaSLYpXxTLPap/RoLz83kZQSP+5+QnWv3pywsltGuF64S8bu4GQ5z+jss0JmxUSiwb91BayLm2vMRCvhm'
        b'nwRd66B4vbDhWTWeI9lVp5NkBdaKJXq4txiLY1ZjiVJQ4n1Cfjy9XYbGbji8KxruzcOiGLUgblEEE2rf4HuFeMk5ORrLgrHUXwctUgb2Cm5eylEe9r1hvJ9gjIAK/7jA'
        b'SEmQlinImY69K1PZoZDjHw2EHy3xY6UVAj/FYqdX7CSLnWAp813SXexnV1KBlCvsV+1x2SfxsysVP6+SDqgSB7zfJbik65TvfUIr4aod8C+cHXxatHoTP/HUpmeZtTn6'
        b'TGOa0bo7aNCFg/6Iks9b/bZnmaxZ/OzUz3HaqjWStRy9MVOfkmkI4AZXGcw77B1Y2H2DTKXoTdu1qVlpBn76yqxyexbbDseprj41NctmsmpNth0pBrNWb7ZfYkjT6i2D'
        b'bO0yZGYGuQ76aFG23qzfoTVSN4u06zLkg1124pvSbyVoqBtSjKmL2DC3GnMMpgD5Lubg8qjwQR4YTY+NiP1LpYkxPGdlQzDoUzO0WXSReciO+NjMuwd2ZnW4SVP5/fux'
        b'sjNuu7UgbazNYmVjZPOeGB84Z/a8edqwmITIMG3IEEbSDEP6ZjFk67ljfuydn9ZAoWHTWw38yDw5eZ3ZZkhOHuTv47bt/sszzkPLPhZtotG0NdOgjbCZs7QJ+t07DCar'
        b'RRtmNugf8cVssNrMJsui/h61Wab+IA2gT1fqMy38YzbJu4yWRwbz2LG5s/Doee2wuJUyJh2G07Pte2FEx5cTXNzx4mexE2Z4C4Srs5JTjUs+jU0X5DOwbmyAViheDCfo'
        b'r6eFp+NT+cWXZ2gEwj5n7fxtAZdd98mnuTc9PITxpGkq/NMyv94yX5CR6wqBcp19H4fkMB6Gmg1wSecpF0RGBK46WreTZKyBWyEyUB+eONp+YsjEVhmUGcfZNwiLUu0n'
        b'hsJWQvrTJPKaeF8HyNUHjiNDAs+9rPJik7wNdHQrHrOfGQrJq+G0J8jnOYEkZTXZrJ9mYT8V21OjzDL6FcAdLNbs5BJJSJ9H6rQcm2Wvb+ORYfaDRsGHuEIbkeCb8vxW'
        b'YI0/dlkYTjcIULgZKtcc4P0kY43VcQgpxM2E8k3T5X66FlLpsR9BsqOto1C1d5js83HLVscJJNWdBVDvL8oUrnrtHg2fmx4hdBjUL7DvdS0x0ni7+CDPCMFwGyq2zJEB'
        b'uQ5yZ1h2sbpySpg8DcppdM28RUk9XrJvjwnGEFqONqjUKe1zluLjaLIQaSrygWOyNruGzVJ/R0/SIlRgMx7lvm1fF+ToiJbtLpSbYnhHBryX7tg7FJal0h0tWKITZXt5'
        b'0AUn+1vxYgBUQGUgnx8txWCb47SZAgguQ61qDQ+4kDXykxjCVHNm9erR9pC9ZYOyObPYMeEJYT42p7gYjKsCrCoL1Qmh842Aua92rlaGeal/U1P3zuLGwoLRk6tLPZMX'
        b'RSeFJUrFG90LXKS3Vb9fvlaFF2+MMf3AyZa+ouf2V+lbv+6t3vjbmVPed5v2Xwnveav+2nvoYO7FJetXeYz61GqZfMVzuP+2utML3ui4sG+O00fn8MuQbT8Kybnp3FP/'
        b'9pPLPrv36hNVi19puPDpwp2fjp2RPa3h3rC/Lvnrtae6Jh794ncTPs21XWt/x+mPr/zx8h81n/t/PudvTV8mfPWL3rljWjb+eknnS3UVb957+aPw6twV6om/mnDP/MXe'
        b'3INde6MSvjF7Lh/xwYmv/u7Rk3D/2cSvXxtjjOmdP/uLJT5vmV74SU7qmw2hz7w99Vw7uKmDH7TsePbCyVidk5XvJniM9w/0jQwUScAVqqFWDMT6aVb25A/0LIHr/kFR'
        b'AX66oKdJKpYTNaeU1kpbtHDBOo6uSAjGwmhKudz4QCiM59RAs0Zkpy2hVk4NTkL+s+whHL/AIIWAVZPUcEQkiQq1Vsbx5u7dSaxYfhBmF5ZFQjscjcWynEA/LAoWhSDo'
        b'VWE31PhYGT/Bc5spropjA6KwjG+55KpDRY8MvGadwnxtzIKaaPlhGiCLaXhbpjGjME+Jtw5CmU7sE311LEwFnQv/9b1fGIx+OWpJujlrj8GkTZcfuApiVfaJPleO+Uns'
        b'D3aZJYXh7kFJJymcFezHQyEqRivUCukbD1GtEL9xFSX63I23ubJrRPFrVyW7lrU5fstXiIdG8mvZpx4Kif/nqhgvuinYAZnsl07dJ7HO+5RUxPuc7CWxT2I1rM8pKcls'
        b'MyUl9WmSklIzDXqTLTspSaf+58PVSWZGxszs6RszSy0zewTMzEga7/YkGybLRuHw+I/UokiDY6+SQv01e5U31Wqgx2nAcvSvBeTDSVqP1VhBuMKCDBuH49FoasbiOCyL'
        b'j4JT7irBI1u5gD3uYGMPpJG4r8Dc6Jg4mWMq4PhYQbNJJIVek8xFctqEkdHQ6N/PTBe7pioHFEE2JidHEVwk9D8jJaVLdk6pLFASp5SIUyo5p5Q4j1QekBIHvCdOuZU4'
        b'5ZuKRzklf4RuAKk0Z+3Q6h00cDDhG0zuHiFv6/4JxzQbdtqMZplZZBvMxDN3yBTI8VzfYBIQ7+AG5IjfWurRuMMQYTZnmf24MT21pA1NHZm/zF2ZPj46iCF5k31Q8h2P'
        b'jnCoLhjZXJmp36o1ypQ3NctsNliys0xpxJE457RkZNky0xiHkukQJ792wjs0W4owsiE/JGdExPXakECrLZtIl52C8Vkj7ujLrghgHem+gzupHuNOqjgbe56TaILfUA8M'
        b'Fsb4rQ6AlnXs2cFg9sxhYXxMVKxCgKtQmAR1moV4efs6Y5Cfh8KylIWld/VHyUHp/vpIfWZ6Zsqfkrc8/+YP3vxBBXRXLDx25WTDyc7cK5HdxxqOzS7VnW44Nvn04Tnu'
        b'gu5+T42moPEnOtHKjrIzN2I1OVNKjmBJrM2OnZOgK3CBRDqxIZVfBT07sTU6DG8ErSYEhVJHSvpAt2QiaXpDJw5CgG+DQQ4DfRr5udGHqOcho16as2K4QkY+s2c/Qqn6'
        b'nB1h1edkDxAZYtzYC3uuc1DvSjMTv2Yv9uLSDz3M3i8fQs/wliGgh4/0ATZgTfQQ49wID0zLoM7GZh6uTXZ5RCnzjQbIg+tQAucDlM+yfZ/oUCjbSUzyEvS6CilY6Y51'
        b'86Fc5inntkGHhnprzfEg8seY6VUo2C0T3UK4aNIQ4Tmcs5O1FRBdgZObedvsxZBLxLfIgj2eIZIgYqViNHaO40iWKGyxxGJvCM2bIkuAm+vcOe1ZDZfYLtKF+JwcNVk7'
        b'KmDtLjjkIGZF6xKioTWqH/42QbuMrOwhjLMDlDmUO3FlTrypQz7Yuk4unvPH3kWErQpBhDJFOMFq3mPw2a8hljP4VHIAlR8vFfOd0537YVT6XjCaQTD61bdJc57/g4X5'
        b't4IIAxx2+XcL3G/Rnezm/3PZmZrJ3bIYrI8LzUccZPOSlZpqI7w0pT7uqENqRiSEacOp3JsZnq6gupFqzTKTeMy2pWQaLRlkKGU3v9KO7+EkRs36zMfsLaesDRrgm54t'
        b'io0/gO6XGL7OL4B+rVjBfoXHr51Nv8k9v+Uhy3lDeLhfwGMWB4yJZGzWkIKZDZLPc7Ysk8lqGoP23dmPTCD7972KZr/FrOzHayX79/3q5aDF+1/V6QphKJ3uSTp9Mf0R'
        b'nk4o868Vm7ZJUKhZ6PMMl0Y/mDpWmLXEVSEkJ2/OOpAiC/Qli4YL05acpJ6T9+1ySxQ4/ix7Dh9AMb3ZitdJ4G+ARo4/K7BzCxSTTCREIQgTRyhcNHibmylUeQrjrQmi'
        b'MCs55u97TATkfOcyCi5jKXtOZ9K62cJsKJjI5dhWvIGFc5gau4i3QoSQEOzmRkwrhwnagDZByE6OWbjGwIwwb7AVSzcwI9CxfTY7wIvkH3vjoeHyudE9LEkQErzXciO/'
        b'CHEVRj63TBS8kgN83TYJ64xjC6KUFrIqVL/84vSyXg+Y5Zb3irH2VXi+7/j8D/5tsbX1hVdMtisvVKyL0G5srvhZZdAzF7NWv/7iT3c9cc62fMucG16up/9z6uy20X/+'
        b'XNlZ+0F4vP8i34aaXy94/6ltbr96f1mkJWL1ryfXeHeeMP9NE1bs8t8lNft6/xExS/fn8uIXj8747bUNbcNSnj38aXWuYUR77Q3NWx9krvwi8XdTzAvh2dHxt4M+7sl8'
        b'0FLkd+PjOb+cXr4rsOhjz3cXhFg8N+icrfxp4BQs48IMKhaKAhdm0In5XO3gxRm+rOZDbehjZZ+KPjb7WdlTkrsXhvsTspM0Y/osmK4IZFdHO7EDDwnPq6PwTAqXeouC'
        b'/DXRJMFlQ3gIm8nYKMiXnPHiJCtbO1dnvBodH+gWQnUiRxFGVfISdxObomKYwguOD8RbUE+eHhD9Jj/B2/bB3ZF2xRb3hCAwvQY9cJtLR8zzIIFQGq0LsutKT7JybpZy'
        b'6+p4nULmAc7/kkCTmYmLLMeoPHBeMkvmJQdlTsJeRVJSbgpZiTFNxbTWFPrtbf8h5jLiIXN5qIT6lATUAwjLd4ko5QARNbKfxDDTHz8kMT4nhiAxWoEfFp0R+vUTV9Z7'
        b'JwrDMF9J5OQUXNcp+Nb7pCfgOHGJK4/s2Z/C2499S6RfAbFvvFABF9PF/m+DKL7Xt0HSdcovXx6EYWtlDPwWEp/OOTivtgM3xf+vVc+3grBjpgaDsDqOY/BSPDOxH4NX'
        b'RX9Pyq9ZCE1hHLQiXPG8ZafKJ1DebC2aJfFD0z3QAq2UVlgUiyWJWBAjDo+AK0TQmqCG3ugyE4UELyfoWbnP+NZn50ULc+XDP137KDnAIRqeeI9kw8bnb1U0nFBEzmma'
        b'FZgWMDpIH6dX/3RWUPKHyRt/7P2z52vUQsI+tz+NadSpOHwY8Zz7Y5IB6qfZ4QN6lVYWnylwJoYQCLrxCtse4hAUPlfeGroTC7X2rSE5f/HSar41BHWTrewR8ahlmgGI'
        b'EiziXeyREYXsXeK7QxrsXRc9cOcIDmOniGUbZsnZJw6Z4U5bDdb+/Pbi+U0ZPtnZvp/iqjCPdtxwRSnvXwwpM64o5Eael+wWb0oZizfPS+GwxwdDZCbbjXDHk3DqodfQ'
        b'THSc73nNhQffkXRivvAvJ91WSrqWQTGbmJ1ptFr6M0s+iqD00bJP0836rfxo4ZEsc2SqXhs6pCYedLFvePz6uHVrnw7QhkdGhEcnro8lsRwWF50UHr8iIkAbFs7bk+LW'
        b'xy6PWKv75wp6qITi5Tp4GtuvdVcL2mS33FR3gT9Yja1wfwP7ypw/+8pdYcwaPD8s8qGAwUodXHGFmt30EwWFuwWoU7sSLanHTv4EFZbAhc2Dbi+QcXEiNm+FsxJcmJBt'
        b'/LE4UmGJp6sX/DJl1E8mDz+kHRnx2q7JT++YNvr3e71HO6fbYs5deP9nu8Z0JHbWvx9q610QcXTmtPU1m2e+tS8BXjrqGbXtBx+uK1laXviNd2BOYO0bnscahuW9UKmT'
        b'rFxTVcJVbJZ3VKFkp71wXzPzoncATxr7s2JDGC/ZPCcOhvKbD8zHbscWJ7GfAl4yV8Nh3phCMr06mlVxLynQVy24eIvQsAtPDNLOQ+eMK0kNywC5PtKeNs6z2eaiM99c'
        b'ZL/NPv33jXnUmnd/srCLfAcly5vfVsZO73Dxjwzwi3soxEfDXcqgDmkU1mIZlTGGR97QyL6ryS4gTV4eDEUyIvgclLARujPipn97Ztk39PhXHvs39L5vduWREn320Q29'
        b'gVWN73yZ9Du45hmimDHFw470sg30ARW9weUlSs6xTL3VSgImVU+VabBRXuP0afKe4WPSbZCtfhn3XSpOVm3/vxZZxZCY4CwX2dnheP6fCB0sTv2WKmudxjGlNI6Ezki1'
        b'REJn/CvjAgS+PzIRLvpZdqZssB9zFsFZOMdrr6hIH1R54bZpcPGVS68/tnPjd9hXfccnSARYMYuX2gRjSFaA0rKOWrp+lTfhRQKSWW7S83e7DerCFz7R3ffKb6xO9p3y'
        b'jwtf6bxupJfu9k14akvo7HUtmW/PTE1f0dhgOdoQ9aNPx4Va/6NpRenXud+Evv/C5//+3sF7SVWuo+bvSNap+bbdTKzK4ZV69piheP7t3Zzn23ZCr3+c755+qh/P99Ox'
        b'jKAmViXMj1Mf2PoMx5C1eBOP+AdS1brn21/ToVbP0ckPHkCBf5DfhgFlndf0zSa56DfghRhNNFT5D6jrMn45h3JH4CI0QzevjnD34GAvJkGlhHX78YKD3n/XJqMbL/QU'
        b'zCxVOGyNdlT7CGfi8FTtRVbx2TvzeMe9OmWfhuFcUpaZsYQBtX/I/siZCf3AxowsGghsw/9tCGDjlaYKzkB99KC5Hjl+wDiDsFqnjItbqVOs1IlxK41xXW9IlpXkYNfq'
        b's+tfd0ocEeat/s07vdGRzs9KnSlZzc1vrlnTuWtN56G/zT3k6/rCsV0Xpu3ZlTHypTfXjAjN+abxLztCSl5+aYkl6Z3emGO5yr+Zjo8riP6xqfHBywfzW4aVuE849YeU'
        b'0wdeDnRa/NW+mJLPVf4q1xbV8tgDZfvfWZm0P2bK+FPh19d/ltf0yaSbUy4leJ86MG/+R6pF0pTU1+esyUupOm/9eUfEqWVjX0wcPur0Mv/Zx59qqI1b7l5XorP6XXrt'
        b'w9Nh22efeBkyFzlZPlzys8uajoogSNmUP92qO/nanoD4qPqu5X95plB9x/Xqhz7Xmj76x6I3UpU7Xlh5x+WMcUTPq6137ri/ZF2c82rdmxG7Uj3fufr3z/VPLj2Uq6v5'
        b'W/yiPCwpP3904g9n7xnf+pkU93rigti3Xo175YMz537x7t64Da+8L/Y2Zyk3X1hjfTXO+tpPP7i0IXvuwbWebbPvl23pyz/gg+57Rtz8YMfbDcpb0YFfmT7649LenV6f'
        b'f6h0e23B8M8mT1yz6puctvu9f3glffq2WSU/eu7ItPrfjl35yb7Qqup68/q+H6+2FaS/tuWtS5lG/+jfve+civMCq+cFYsicF5+aev2mIjhg/fTM35+8pDz5YuSGp6+v'
        b'6Vj7h5O3Jt+MeVJ/sXLGgYWqMmvViJ1FE+b4vBB9b3XeV9+cmOD9F/f3ba8/n5Wz8oJr1ifz3h322efvP7tyz2/P/fpz7x867Xthpina8nH51AVP/3hE0dmQ/wjx/ulL'
        b'e0PmH30lqubdr1S/WhH5l6Av2i9t/HtR1u3arb/b/q7F8vb2FbH/eP6Vf2Q6X4jIW/yNeOTisPnq8wQP/Cj/qi/bGopRCIoFsQcE9vU2PGRllRdu0R89gxg4y9QMuEYE'
        b'/A62W/kpXR30QtEgJQA3IwcAzAG1zGmaoHMZFhMtKQ1UC+otcB66xKmL53IWvxsvP+2/OhALomLiVNOgUdAAkfi6+Xibg8Y0LPCJZpBOV2BJlApKNtIV7SK2kM1/8SBW'
        b'5/Gvndt+qx2VmdWgIV849DgnJWVm6dOSkjjsZBMkiFNFMVShZdsI36hFYk2is1J0FRWEDl+JTuzQlh3kSkrxK0kS/yGpxL9LavFLyUn8b8lZ/EJyET+XXMX/kjTi3yQ3'
        b'8TPJXfxU8hD/KnmK/yl5iZ9Iw6S/SMPFj6UR4p+lkeKfpFHiR9Jo8Y/SGPFDyVv8QBor/kHyEf9DGif+Xhov/k6aIL4vTRR/K00S35O04m+kyeK70hT1r6Wp4jvSNPFt'
        b'abr4ljRD7JNmir+SfMU3JZ34S8lPfEPyF38hBYg/lwLFf5eCxNelYPE1aZb4qjRbfEUKEV+W5qhfkkLFn0lzxZ9K88QXpfniT6QF4o+lheKPpEXiv0mLxR9KS8QXpKUi'
        b'Sk+IID0p/kBaJj4vhYkPpOXifSlc7JVWSPfECDYzD/9z7vaK81J4KdjxkKj0UIxXiE+6KUYqXEeIojf7y5e3ePBXL2eFj8I8cQCgi0lJA3Dc/f99/RXmSf2gzzpiycBJ'
        b'8Yx3hwB8di1WeimhGC7hOSjHcsY+qMSVOwkeY5UTNmOXce+oIKWlhi488+WKwOJYV5g1Mu8PTca+L3NVY4o+cFlybFX25KCj+bcqTAEFr3+cZzS99vbPV6TNm/PuM/d+'
        b'1Oz78Qev6avekD5sOjE7ccTdYRnX3xj3w+kH775r3hKXsa2457k/q3Su57Y0pYdJW0M/mqkee9UrqfDm7t8ej/n512+F/mZngenSk6tmNTa9fwRqo9sybr138u5Hm+tG'
        b'n3s99flhv/izpinC9y9zf6Vz57qcJNY9zOP/Y5R4GgjbDNTAdTw7X8TmhL1WVgJXbYNCxow62TXxxBKG4b3VeEoJDUuf46wE21aR6iKdhcfYbLD6DqV8NoYrJ9Jnx638'
        b'oa3yMO/oqFi/WCdBLYkLscjZeQnfShyN+ZL/ahURuruCIppEQsxBK3vym3RcNXY9SgChLDiaAKyMeitX0j01wirodILysZjLkS4MjpOnj9ykjh8pjFkh+QnQyS9KhjN4'
        b'lGyXEAoF+3mv3GmHRB+bBMfwcpT8tAppDW6qJDpuIxY7CVKgAlqxCQtlSK1My+QVPzhaF9HvkTAOzkgUF60zrCxOiI828d36Djyqo2vlWFEInmuU6xOwRX5W5f6U6Vi8'
        b'AM7LFwSwEXK9qhC0eEMlrErkpjzI3xP+8QFYxF2idcL7hO/HReJwl7BikOyb8L8DjP+LLzrltyGr0WS02pGVPQTk7O4qP+KiFOm3G3/URfzaWXK1b+dMU3LKF2zW9iPC'
        b'pD5lpsHUJ7EjoT4V38/ok0gTWfukNGMqvZIeM/UpLVZznyplt9Vg6ZNSsrIy+5RGk7VPlU7QTr/MetNWuttoyrZZ+5SpGeY+ZZY5rU+dbswktdan3KHP7lPuMWb3qfSW'
        b'VKOxT5lheI4uIfOuRovRZLHqTamGPjVXY6n8XNuQbbX0DduRlbZwfpK8DZ1m3Gq09mksGcZ0a5KBqaQ+d1JVGXqjyZCWZHgutc8lKclCejM7KalPbTPZSDw9RDp5sBPM'
        b'7IED8wL2wg5DzOxbJGY2c2b2FWAz491mts9tZl84MrOnwM3suwpmpnHMbOPJzHLWzGirmaWZeSF7mcte2DP5ZvYdAfN89sK+LmFmgtrMvgNgZqhoZgFrZuLMzI7NzSH9'
        b'uMmWw9WBmyu+eBw3+RVfOjsel+rzSkqyv7cX1y990gf/v6u0piyrlrUZ0uJ0zuzppbSsVJoZeqPPzKQioLWHEFME9LkrLYLZatlltGb0qTOzUvWZlj63gZrU/KRjGge8'
        b'yHG4RP4fZD3BBKmF7dBKgqR25rE2MlrksuJ/AISObR4='
    ))))
