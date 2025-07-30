
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


"""The Python Fintech package"""

__version__ = '7.8.3'

__all__ = ['register', 'LicenseManager', 'FintechLicenseError']

def register(name=None, keycode=None, users=None):
    """
    Registers the Fintech package.

    It is required to call this function once before any submodule
    can be imported. Without a valid license the functionality is
    restricted.

    :param name: The name of the licensee.
    :param keycode: The keycode of the licensed version.
    :param users: The licensed EBICS user ids (Teilnehmer-IDs).
        It must be a string or a list of user ids. Not applicable
        if a license is based on subscription.
    """
    ...


class LicenseManager:
    """
    The LicenseManager class

    The LicenseManager is used to dynamically add or remove EBICS users
    to or from the list of licensed users. Please note that the usage
    is not enabled by default. It is activated upon request only.
    Users that are licensed this way are verified remotely on each
    restricted EBICS request. The transfered data is limited to the
    information which is required to uniquely identify the user.
    """

    def __init__(self, password):
        """
        Initializes a LicenseManager instance.

        :param password: The assigned API password.
        """
        ...

    @property
    def licensee(self):
        """The name of the licensee."""
        ...

    @property
    def keycode(self):
        """The license keycode."""
        ...

    @property
    def userids(self):
        """The registered EBICS user ids (client-side)."""
        ...

    @property
    def expiration(self):
        """The expiration date of the license."""
        ...

    def change_password(self, password):
        """
        Changes the password of the LicenseManager API.

        :param password: The new password.
        """
        ...

    def add_ebics_user(self, hostid, partnerid, userid):
        """
        Adds a new EBICS user to the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: `True` if created, `False` if already existent.
        """
        ...

    def remove_ebics_user(self, hostid, partnerid, userid):
        """
        Removes an existing EBICS user from the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: The ISO formatted date of final deletion.
        """
        ...

    def count_ebics_users(self):
        """Returns the number of EBICS users that are currently registered."""
        ...

    def list_ebics_users(self):
        """Returns a list of EBICS users that are currently registered (*new in v6.4*)."""
        ...


class FintechLicenseError(Exception):
    """Exception concerning the license"""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzcvXdclEf+ADxP2QIsRUTAhquisrAUQVHUKNZQF6KiWNmFXWAFFtyiYBZFEemIvReMBeyo2KPJTPoluVySyyV7yf3SLommXZJrMXfJOzPP7rILxJL33n9e+PDwPPNM'
        b'n2+f73eeT4DLjyf+S8R/pip80YLFQMssZrTsYVbH6XgdU822MYtFBWCxWMtp+Y1AI9GKtGL8X1rhY5aYpdWgmmHAQmCYygOdR5GnsZwBiz0ZsEauleg8c7y0UnyV0Xtv'
        b'evXReW5gFgKtRCtZ7LnEMxssAgY2Gz/PAx4FCo97QzznF+rkmRXmwlKDfI7eYNblFcrLNHlFmgKdp4K7I8HdvCMlFw5fbExUHmMfCXmW2P+blPhSC/IZLR7LRmklUweq'
        b'QSW7RmxlqsE8YGWrAQPWMmtJy4C2zKnyHFMixn8T8V9/UhFPp2UeUMhVNvADeT2/mDTvP5gH/Gx/PHlq2ajBAeBzoezfpnWAXj2iFcWQHrG1oJbL55y9Yu7bq42uvXJU'
        b'6N4rXmUZi+9RM9yYOy8S7USt81GdcgGqQ43RTyThe7Q5KRw1oyYFqkdNHJiVJUbnRqL1+lH9FYwpAhf9U/JTX6rvqos/2pv/lfqlz5RbwzVJmq/Ur+YG5BXmF7MXNgyc'
        b'+BbYME2SFa5UsObhuMQKv3QvXGcEqoeX4T7UlG6JDEcN0SwYBi/y6NyyYeYQnCshew5shJvR5lScAzajDtgGN0uAjz8X8iS8bfTAWRScjQ1TGAkICheSeM9vSr6xdI3O'
        b'IM8XVn+qzUdjMumM5pxci77YrDewZAbIIoGBMsaHMcocRXF9fL7FkGeT5OQYLYacHJtXTk5esU5jsJTl5Cg4l5bIRcEYvcm9F7mQSgaRin1IxV/4sWKGZcT0ahmFU+Am'
        b'1OaRqoxSRYbnobOwPsN1VpVxIjy+Gz7FpBc18S8xrzLLfEDZM8xPwctFGwAFGOVKC2uWgrLWKftyD4Z+mGAHmA+n0bfrfVYwaRHtIiBXD/72SYNQ5HdBLPh0Aemeuvju'
        b'iDQh8dJwMdjtMRjgnMpziVJgicaJj8Er6V6wXYm7g1d8XsxcAQDCoiLDUF10eHI6A5YuQdvhJWkaPIZOKRjLSAI1e+ChQC8V3IvORoanRnqGoQZ4DrbzYBB8mod7YQtq'
        b'twwjY7+FTqDzZDWj8ajJfwnwypjVj0Vb0WF40TKU5GkOC3Rdb2Gt4W1PLiRtgIKzBJI89fAG7EiNVKSki4B4HrqRygZGDbUMwa9mwOPmVDqlycmRLPCCu2FnEova4XZ4'
        b'wkLAaRa8noQaM1BDSnrU8oWoPg2e4oE/rOZQFap7AjcwmAyoNWhWarIyOZIsC27DBw/ompZTJaKdFoyqgO3vTV6LQEI4zzPwUJJEGN9OuDkqgpZJT4Y756BmRTKuHG3j'
        b'4HVUOx3PFukiPI82oO2psXHJqDmVGYZaMnBFvsO5yahV5MhybTi6RnIkp8NLqF3I4oPOcmONWQqWtmUJTvNKwutUhhpRU2pyJNwBt7IgAO3n0HEtrLGMJsM4Dk+gBi/U'
        b'Eh2ZorKQjMmoC9VnpJGpGb+kFB0SJ/tK8JgJwC7z16JGpQq1JCujxHjiLuLl3MCii2tjLAPxa2m4RwRqScPLohQBRWSKCPQP4dA2VQbtjSo0JzUjMjkCNWdlo/pkZUp0'
        b'VFK6GCiBCO1JhsdoA2m+y0gXIvCbKAZ4oSOww8CiK/6wxULoRwK6BK+m0hzJ6aglMywVU4MW1ITBMDNSCc+KwUxejKrgNdhqGUHm6Gl0czrOjofzRFhSGmpRpeFVXZOV'
        b'GYnbnSSaHeHrJHmsKyHeSyl6LYNpKFfL14pqxbWSWmmtR61nrVetrNa71qfWt9avtl+tf23/2oDaAbWBtUG1wbUDawfVDq4dUju0NqR2WK28dnjtiNqRtaG1o2pH146p'
        b'DatV1IbXRtQqayNro2qja2Nqx9bG1sbVjqsdXxtfOyF/op1SgzoRptQMptSAUmqGUmpMq+2UutCVUvvaSYk7pa5WCWu7H26ETQIhcaci8HKCQEji0Dm6OHgWd6IWiMGC'
        b'YJ4qUhEJ6wha+as5eDZ8EEWpsFWYAjdiiOQAC0/Ds+uYRBHcYwkifArthtsiYIcySQQPewMebmRQ9WKTJZhUfRXunhqhGO4dieowiIrhSTYCboWnacF09NRgskDKKEYx'
        b'FfDJDF6yenSZFoSXF7CpGPuiGHQa7ge8BwOPwd24w6QguhI9ApOdJNwbtBeuB3wSAy+G6oR3p3GVhyOiFCzuaBdG68vMYjM6YAnA74bAzUtT4clJIzHmioG4mA1LWklB'
        b'bwi6jTakogaEyQpucDngRzLwDLwJb1kG4NejBsOLFPAYwJZUwhYmbT7aR1vLwVSuDQNlZQKGMyUDxPFskAZtFqjQiXHeESkKL4x+GXjoiawPbIUn6eh80C20l9Q4AF6I'
        b'CIvE5crZsfCSt4Us5cT4/FTUEob7j7vTbGCm5ucKI9vrzeBRp+BOwONwF9zNzMEr10Wxb1JMLEUNKzqnIMgrhbdZWBuGmmj/4c1V8ChqTMfCCotOL7Ey00agvbSPibA2'
        b'HZ5CDeQNodsXmfk8OkL7+Ph81J6qhEckKoJlPBAPYj3RFniZllOJ4FnUmATPkBp3wb2VzBwWVtNJTknNw/QTYzCLzmJi3sA8PjeCgln5fEzlGpWktoioZDwruJKb8DwI'
        b'KuRjizFIUMJa44tfROCV2BQOz6UQcPMQs3CHCm3KY+1gz/eSdrCsU8s4pR22Dss3lRzGIZbiEEdxiF3L9YVDfUs7nEr/5+lTGNNUnPBeYvqX6ldyv1DXFXyB//NvNiXu'
        b'9UiKY/T5cu/nFim9stdP2VnTNCugSTY08cf81kmXfTapxa/LwFt3fNZdmK6QmCkHPASPFwtsCzVnKFBzMuVcsB5dA4GjeA5dCjZTDrF76hQnd9Ogq04Gx4VgwD5lDsV5'
        b'iuatoIiqTMfErx7ng3sft+cbBrfwaIsC7qWSkVcAOkpyZmDYhC3kvSdsQx2olYUXtTPMhJsugucfs2dJg1eLozDnJM1x3HC4fbyZgEExqh8YEZkEOyZShiZFl1i4MRXu'
        b'MRMay/uOpF2xE34FPBsbmSJ0ZVS4KGMFumCXl3pIRDSVykM2vkRjKmKdAtFaKSP8+jCejLGfU+LibZzWZLZxJmOekWQ0EuKnYF2ELNZIOK+xv1PSIoXXOSuudpO0yMgS'
        b'zfA4QQrUIkbrpYBXYpTH5ORo32J1lABobD77kEJ1LzDj+wKzvQkGkYlM5cjb0i/VS59549nW5999tvWFS63V7Vv6veST/2GaBCRO5H8qiMRSMaFVj6NDqCVViQ6gm2FJ'
        b'RELAyH6KrfCEN+iKwhZtXm/5CJ0YxoUMnirMJdv3QljM+uJukXcdkPoxxgDQLfJypbkrfmXuGeMA57STInWkGj9STRW45+M68YSQifAs74ugshMjTQK8kYG3UVOhc94Z'
        b'+988R2esgurEqISu2FvzcO+/j6E0pzQ332LK05j1pYYmUpiSDNYyhmCNMgwTSDoxGSkRkSoVkWGx8MCh2/ASiIAXSa8a+v2/7ISHowe6Vpf2yboUT0VtE+AFTBqF1jEu'
        b'+aNqDj6NBbOn+ga5WAJyDAE6rMvxv0WXY0Bf1E3UncFBS4c526O0tJZ3tvcgatqrPc++wLw96S3WlIITbs68cerTu+qv1F+o7+bJ8tWaMM1Ln4VfUGvbdfjP/wv1WU1h'
        b'/mn9L7p2TWGurAAz9sWbJm2SbkraNOW4VB69e/1FEYBHvNdlbVAwlGKijbOCTfBMEmzQq7ASIqwp6IdaOSxH7xqM14lCKN+TAvWAflFOnqZYAH+ZAP6BLKZAfpgSrRlk'
        b'KtTnm3N0RmOpMWpKcSnOaZoaRQs4iBOvMRaYbOKi1eS/C5L0UgVZI2HXxkFOdCGUaKcLunzl74ou48kIb6tGY9Ea1aVFYEGOqsBoKxZI6jFZV2GhDl5G22CjZO7KiAQA'
        b'G6Z5oCt5qEb/c8VM1qTAxWeGnS4qMFgLC4oLVHkqTZpmxUftui/UJzVfqIvzPSl90Z0Xn81e5IDrh5ovL5c5cSUaA/zExsHdRENQfO8zH66qMSm33WUqvnGbCspGn16B'
        b'jvaci6PoNgsGw+s8bBejG32jUi8zzSMaRNheQM2r5uuzph8UmQhLfqW4OFVDJIQkDb+16U9yhTy+/27tN2pp/ofFDCj4h3j/n3gFT1kmugIPYmZMeK5KGakSCHQ/eAmL'
        b'3Ic4/KIj3ky0nXmxWO4lrDUqMmBSWFhKZBRsycAD3xyRDM+ECWw6O0eaDw/qqYCxeDG6KDBymmcEvO3MNgjt4OGGqFBBENmBExtpzYqUNFV6ClaMiGygnCQBoSNFQ+HN'
        b'Ba5w4LLi3hZDXqFGb9Bpc3Tlea6YMkzMCL/GId0rb+NwLpeVZxzrPdS53iT3QZf1/lTWc71hzQh4KASewXojFomTMG43pabjhcf4Lgaj1ogyQgqcy+RY7yAXUkZVuIcm'
        b'nW4cmwd9cWypqpgMOr7CQ1pe+bqMSXxl7T7Te0uXF8RXvFTCA6qco31oP2qPQEfQlshkjJpdhOMdYWAXOiunhpui5d/7bvdlwv4G1ilfTnhs4TnB4JKRzbDKcZwUlGmm'
        b'rTD7C4n/168/+PvYZHynniJeNR7oT0rCOVMFfjaHTE3VaDXtunbd6cIv1GWaujPtursYr++qDfnhc09pFj/TCi+19gt/QRrQ2C7t0LAnt3XozmpOawIld/k3ZSPUk2re'
        b'Y5KC9tbEBXyf9cXbMQO6wF93z20ZnD0k+HwH98p5W9zbsQPmrH+7Nu7tGHFc2XEsio8e/nrFbkx4qQ1ifTHsSqULk5GM2mEbFg5hK1uKlZyuvsnHA4kKX6gxFVLIkguQ'
        b'NUaKabDjl0qFGDZk9A4LJyEudGagO53pu31GyEaBjxQ+7gJ877sRG8LbE4uSsYqDxUOsqG4A/ACsgepm3MfmyvSwubIPbwkmY/boBWwyFTUm5WBVvgNtww1Gj0JdIHpe'
        b'PoWMvTE8OM0EEMOwck+8nwAu+oEcmCUnU6BOq4kaD4yELPd1sTE5+uE37zGmevwQfWFW5KtjfWCM36w/7Ok68Jyi/WXRRM+gJGboa+GzRzzBT0hSzc5b6fnT8YkjbB8P'
        b'mHzv23lbnxvIxb//tylLePEe7Z0/eXUeyn1uaL+L7wXvOTP3WN1exqNx0bmfbgcuNbx9MmJuic+fkeHzyAnffXT3mxz9H4Nu3eqy6YYtSto4dUTsd3nZT478z9+5hX8e'
        b'mfbxCoUXNfxWoJpxsDEBNfTUl6iuBG9GCZS0DpOxnSalQoEa0sIjkx3W4XDYUbJEBG+LhlI4TUbXotFFFTxjxuLBFSGLN6rixg2E+6jEPJHTOwVmuF3vonJNgbfNBGLg'
        b'CfaJiChUh65moXqi5cMWNhI+BavNxNIyHl2CB1w0MrSjvFv0FjQytH+omXA3bT68HZFCbCFpcGeMSgS8YCeLJfndcBuV7SfKMeEYszQqWRmuiEKbsYgKQLCcX16ZTRW6'
        b'2CWYfFMij5shRk4VVeqIQnc5usBMgHb6+GGpoVFKV81gyVyqyAViPf1YhCoyGatpx+ApBQtkUk6aMs9NkL+PoiYus+QW6wXCHyqg5yQWq2n+lPQHMDy+CqqbJ77zxGgq'
        b'Y4xyFxQd4I6ifYgC3UoEKXfNBTtfdtPeyFSmwZboiDBi/jyCGrD2Ksaq6XkWVsGD/WiDeWI7bhEUkjpwK4ojgryVGQgqxXUSq7gOVLOVEqvEpKrwsXKHgVXcxlRKFwJD'
        b'AA/MTJGncSIDyO8iYAjMxsKvVUpKWsWkjilAy5CyrYyRt4rKFutBpaj8iFV0mG0Ds8CynUvZSo9KT9KK1aOaNebT9nh8d9YqPsy14XrK8/EdT3MHVHrVcTinl5XN56ye'
        b'LQwDVm7H/ZhFS8lwL2V1HlZxNYNLhdZ51knJfTVDS0ppSalLydcXAqvM+H2dTCjh6G8mWJm/ELSyhlBaq1c1i/uurGPqQJGY3OHeiLRsGyPkbmUM/6H5GLM4n6V5F9R5'
        b'2fMuqGNJ3c6cb9KcYprLWiey58J3brlOa7nDEi2vFW3EKuIsUM3g2fbWig9LrN6HpVqJVtrGkhSrNy57Xuth9Q4Eld61klovLLtxWk9cTmrlSLlKHzwDPtWMVlpEWvyL'
        b'1UfrhVfGxzDCmc7j9P9oZaRFq08bE0je8lrvSh8r28oa5+D+MrS/rDFU62PFJYIwkc5ncT5fg9zKWNkiDr+bovUl9/Z0qdbPKtyNcCmv1vYTyjvzkNZ8rb5a/wnkvzfO'
        b'02L1oVdfbX+rj9Wb1EfeGXysvuRN2W6rN3k2C2vsh0fhh0cRgEfBGu9Z/cjotAPwnLLGV4QnXOZTfCd1pn8sPJF0PMp+2kD8DLRBNexAYO1H+++HWw+u8yYtrPC0+jn6'
        b'YOVaOaPczFh9q5kNjEFq9hLu7GxqoGr+PUkx1qkNkWPvsUq5kwOydi5INWSi9Rdg1FrmWclYmRVgC7uSJyKVXZi0SXNyDJoSXU6OgrWxUTE2xtxDdb7nOaVYbzLnlZaU'
        b'Tf03sOvOYrBmSF6hLq8Iq1Xdmld3xnucvNR4j1HeYWgNpflyc0WZTj7K5NZJkQP75Y5OBpKNWith0ayJr8MdrmbsHc7v7hYmjKGUU666D1k0Eg7wn+7+3iGN3vPVyFdp'
        b'ii06Oe5R2CiTgrLce8Em3UqLzpCnk+vNuhL5KD15PWaUacy9fjSB3DqTeHrt75LTUfqeh7zEYjLLc3Xye746vblQZ8QjxhOBr3f8aMfvMWPuMSPueYwyLYmKilqG04nU'
        b'eq+fUl5QanbM0ST8p5DZRHqDVldu81xAOjyb6HM4CbdqsvF5pWUVNr5IV4FVW9xyqVZn88itMOs0RqMGv1hRqjfYxEZTWbHebOONujKjkQjtNo/5uAFak8Lf5pFXajAT'
        b'tcFo43BNNp6AgU1Mp8dkE5G+mGxSkyVXuBPRFyRBb9bkFutsjN7G4Vc2sUnIwBTZpHpTjtlShl/yZpPZaONXkStXYirAxUk3bKKVllKzTuHdp7z5KBfMlJKdHFDqAMXX'
        b'gN2PAbCE2/EM4YM+jJgj3E/gg/52kdWHCWQ96TPhkJQ7soH4aRAWYAMZP3EA5Z9SfE8Mnj6MH0vKy2h5H5ZwUR+WlMIprA+tL5gZgusKJDyWFWzmN8sLqXZ0Y246alEp'
        b'U7DwksMlwGtovdNmLgWCuwFFg7tEUMSyaflfrOAwoOznTcysuEreypmGrPQxY4mV/Okxg9vPVYqsIitr5aZghDHOxSyQKRLj/5hRDASHWUwcuYGgDTMdzIR4TPh5wipM'
        b'+Va+gKnky7OtPK49EzNbjjASzPwOYsQjLEGkJTWKtDyuhSNP+D9mhaSmlcUCczGe1PJlp7WEQYusEtqaWHi/EGDGQntAa2KnCM+8/ZmfAlb6YBbIUgImUmH8TSKrSJeS'
        b'WKGExxRHmkJknEIWmDPpzDZOo9XaxJYyrcasM5INAIXUJiGwV6Ips0m1unyNpdiMQZYkafV5ZuPjjgptUl15mS7PrNMaU0naHFJY/AAoczFgErcDbY6j3hBMwkyjKZDx'
        b'GBwIkPkJgEBAjYKXjAlm/fCzHwYI6jygQ7ss9t1tWB9NtuTS6R4a1j03gwh4RYR2zn/MTesgLRMgoi312vQEZNsz38uh0lgZh+LiqgU5hSstvtSRVWbqMXtfAcr8MJTh'
        b'QsZxGC68cQpDmGY144XVG8qWMDxgZsfUcXVe5L6eeK3wuBOkaU/cFVm+1GmF9LCyBH4Iie7pQ0PmkRowvyId4K1EPgAV7eXLcbMceaJykqqSxVVwpGPVTBEwxpM7K+5G'
        b'JWcIoJ0TY8BOInc4hc3E0h5NCa4j8gtGgHz8TICdSljBC0H5DCupd1IlZ6W14rwNdWIMpByWYXiDjNzjdPpk5Y1lhM9g9MH1WHlaR9lC4tAUhSVN3izKZ7G0+RcGy5AM'
        b'WCPDEyUiPHghniotTlsrcjgwYdTAE9fC2I3RGL6IhmKTrNIYqQ2SK8AwjKmosWi1cTKBrVkCFHabHdPJhQLtcgr0OqNRIX1oqtgNr7IcSg/LcMMlpulOaMUwyrIERmWE'
        b'ALIsfg5mKbSyMgzFwRhWBzFrYjR5eboys6mbq2t1eaVGjdndxNrdAObGS0nTZBwOuyJNIFCn8Pqt9J2zSci0YbQVqlzmHJ6Hs0MTGccmEieQ+xBMegcNXDPo18fgECCW'
        b'kOryyb3nb2I+S5zdkdgbG8/YTQSAk4+ke7HB3gtTB6CuNJUqMkwhBl5RLDoqznEzX3rY/5sImdKBxVi2W8xulwgmC4zr0nyRgGjVzGKOplMHMjsl8MBoSJzyyFu+FvBg'
        b'sUggrLZ+dse5OfpiXVqpRqsz9r1LGw+AYIwTUc8Kcb7Yidf8w+/V9r2bIVHR/RVPVAU3d7uHoFYO+MCTM9Auzo+rtBADTegw1E62gIi/WpI9o3oEasnEir3dxtA1F4Cl'
        b'YRK0HXXC49ThCW1fCDuEUmFhqCE6KRI1wA54AT01PywlHavoUcmRKekMMPh6POYD2+hW0yq4Hl2bF7kgCTUpUtLTYAdxjyNeNTjfOLgTa/Ad4tDZKv1RzV85E5Ge0699'
        b'9aX65dx2Xbsm+5nd8GprZ/bxjYqajk3T97ft6azvrO7I5l4qEHcWBU/KvvheQ3GVdecg8djzVg+TZHvtTIkp7i12p8/OmqZnZfsjwXef9ReP+EIhouaAVOlw1JhKfZT4'
        b'EPEaBh5BN2ZTs0haRXJEVLIyFp52NzWgU3CDYISBx+BmeA7dRBdRUyTx7lppN7AMsvBwk2qGmQCfRkFMnVfDoiKTIlkghkfZGCVcT+0zC+AteCA1KiVdmQybnXYcERj1'
        b'uAg2w72LZXqHUfjheaR3nlGH+XJOSanWUqyjtgiieYB1+LeAWh1YQcqSMWuG9QLOKLfSzr0bk644H18JDeg2T4h+HS1Z4wpyX+TolVFPYJHgJbE1gCr8ezDQxV7xwJ64'
        b'IY1z/2yqA2lc+TGDsdHTiTyih0ceEXBRhJzI46OiIiQTleiCOid1duzh/OSMhWx8hw8Y2xNz3PFGm+nAHLjJShEHHka70O1uzEGHh9mRpzfiDEXbf33f1T4U576rjcnv'
        b'uesqnVKsKcnVaqY+iUsaCdWxZBPcbUYXUL3J2eEyNw83tDUVnklKhy1O0EQ74MUZqMZlY42L9TfBbXP90RkAT6NN/WAVOoYaqJ8gOhoy1+7Q0YQalbB+CtpI7YZzubH5'
        b'Fc7hiIDLBislg4KIw5I1dZJBrg6vXSWPV5KjK8nTleTW8r+2yeqUuVzJ4CQy7Yfg7rxUsl8SRfZC5bAGbZ6XRBxqNmdhHI5UoJa05CznyonwOuk80S3YOYDaj6sKeFJ3'
        b'Yp1KnRay5DFACSfcj5o8u+vEFQpen6jOsZedvhY+xYCSdR7B6CS8IXgKb30MHkpNJVs2yelPhKH6hQIRfMLZdhYIR0+DpahTgs6hplR9/9ShnIkgVYq+/ynzHepz83J+'
        b'1It3/BWaNE1xfnHuV2ql8a76tdxXcl/PTdZs1b6Ue0b3ReLHf4wBWZOZrLjq+bVxnyrOx2w/rzMNOBYTWyXP3HSsevZ+JnTwy60vBjBvf/DsG8++/2Lwq8/sYcAfJwWf'
        b'ft7ocM+54Y+q7at5FB3uZXJOh22UJsKLaN+QbnoId8NGV5rokSsYpm8tN1O6Z0FbepG+xbAanaAUWDs+xb5jlyE0hbaMAN7oAhfMTDfLSWtPrYQbsGZn39WD1fBkRBTm'
        b'8P5rOdRUgC5Rk7IUnkoR8qRgYk0dQb0msKgZ7oyhXUZHiFcL2SHH4gEm6Lvct8hHJD86EfYhO985ZUasYhNlh1LhQQ4qvA5IWar58liX9Sf6K1ZQ1ozvTQF15bo8O/3r'
        b'FqDcaxYwXiRIZt0C7IO2eey7Qd7OApRIG/ClhnEwjCr6+19XMm0h4jDagy7BqkejGW478RzcmoA6RbPRtUTYNQo2L4cdCjAC7QhYgTZ4FpP+sTMG8n/HnMKL+WjM9+zl'
        b'salBPBD2BSW7mfMSkLQhRR37fuyaWTOE5OpJP5DtwvJNyz5kfg5+e4gW6Cue78eayO7VLs13A5pueKMYv5nfqi6sNXBXX677AQwcOVlbdXVie+b1d4+9PUts1sdWP63/'
        b'dAP4MSlz6YZo6VcvlX9oXFafrN7QMCzgxvtrFpwoeA2JPz644o8bPo74uvoq13lxUX3q8arMTdobS4/dGlc86V/RP6lkvoXX94hfe/y1nR985vnP+O239s98Ia2frjXz'
        b'u9rZZ556t+Gr6Gc0G448ee65/Nc+GToia8bEYZX/4TJzlDdl6QoZ3Wh5YvB0N0/9fZWOjZZ8uEdwXtqDrsGrEc79jyFovUMu8c2k7h6Ba+GO3gIJ6ooj+DfMxxxO1rBr'
        b'skzALMcqwjq8YHgF6YZ4MDwP4rXiZQw8TmWkJWi7JYLKL8tQlyDCTJsmIHL7Ur7ngovAYFz39vE8EePmU4c8eAgdxzKhQD4onMCGBWgbGdwAtJ7DALUzmwpLWJbakeiU'
        b'x2aZQrA8lhBLd2fgvjnwSkQSFcN4TLQvT2Dg2XHwFp2W4SVah5NeFKyPR2cdTnoI8yO6MzQc7pG4cSNDuoMZwfN5dJhoE7yei2dkE+pIYwAzEaCWBN/7iTm/TWMRO8mE'
        b'lwuGUxoR5qARZqekxhIXGx6jnx++41l/XzG++rF+zJqh96UYdtmNCmI2sT2tmy48tDqLZbkycr/CSSZK8WWlmyy3JcRVlrt/vzAVpSZQzxx7Qk4O1pNzVlo0xYL5m8qK'
        b'tBGbN4kZ0ZhMeTpM83KEEXk84nTbPOyV4Apo9wvxJdehIkrZYG/qOw9rUStc35OqjZzf7e0/CT4thntga383vVFq/0+9Hx16ow7rgnZLEZFlRFiKYbXcRo9f1Q4zNWY8'
        b'XQY8Vao83l4jARPnjjcxvjmlXCrjUpc3D7t0xNdJsXQkwtIRT6UjEZWOeGIT6Vs66i3nilVUaBsLT8GTDkkXI/Uxp6LI+S2dZkkknYKHxJhbhiWlR2G5xa64Rc7FvLUZ'
        b'yzvzwohRLUvqHjLBpAIQ29/XA52GpxUsjT7A2ujhSbgleBZ2OVVSzKdRPQ8GzeKTMkJph55EOzSkP9utzkwR4UliMMjEZ2VO1GcXfc6YcnC+ehMz9OUEnyp5wOw/TIv5'
        b'YtPSutGX40NHvzt8VPybN3XPqIY2PLmP+3NY2eeX8seWi9F8Peu1ue3L2TVvyhaGhR99JUHX/+j3r52f7vvLoMrAr9ctPPbG8ZpAz9JPfgZbfglq/FmLxSAikazJgVuc'
        b'xHcOvNCtFNavphvhaBu6hZoFYgmegM2UWGK55Awtjq6gM550dlNhfXTUvJUkxMNfx8HTcWaByG2RmIWIDHgzWnBTP8aWJ5cIxHbfBLSXkHYF3NJb3YRH4AVhL74WHmIJ'
        b'DT0MT9j1WkxFS9FVSmHhPr/8iCR0kxEIKSGiMnjFIeI8Gna5unXmY/DNIRoiJWSBDkK2DozwlBHDvoyRclI2gFkzuBfMRznLCigutnF5xSabNN9STGmCjS/DeW1is8ZY'
        b'oDO7ELEHCGSY+q0m9+XkQhyCjGucRGwVvhzqIet8MsSVjN2vnwpWpbITMuNKcjFSck7pTInOXFiqpQ0YTY5Juh8XYYxmZ7cs+HKgmzhhkYs4KKKds5CLxCUlTBDeGO8I'
        b'XGLBZLkYnkiFu6mG8kEeh2lMMCbYaqV4wmTgZs12GpxINI97EE++xBliw9w3xGZjX+Zld2oyUEX1IjkWJ+pMGGQvea20oMtYyLiCOs2rUJfXKtjsWyZDnWgfVoUfQ8dF'
        b'6LwOnrIQOtc/dSYuUZ+mwnikyqLadDL+V58R6QimxPJ6nTIcHoiCnXNJsBK8BK97otti1HnfgE+O7pH/Rv/G3hRTpKJBG76wEV0NxaIJbE9zLhHOO5/DtK0x3CLHeRZF'
        b'YIScDm87RoV2RMCOMAYMglt4YyA8q/e6s1ZkImbnaWDpl+pXPr+rXvzM+da2bR3VHS91VI9tXMm0drX2e0nSuWfy7rnB83YHxlZ/Ojn4wnuNLaKvJgUHnq+aHxNrjhHF'
        b'HY3h48ryAXhzqf/W+B8VIoEmnQxEF7BeRINYxPA0K4adcXAT2mgmnoDwmKdYEKtgyzKBIKBT8JDgOlyfjTZQC0U53IAaIgXpyxeu51agNnSdeuRkw1NoK85DQoOauDno'
        b'KuATGNjJw5P09WB4Ym6qMgxdRjtcPG5gFTr4wMAHL01ZmQ5jHMF+d0PWOpAsozTFjzrTrAnHdCGnWJ+nM5h0OfnG0pKcfL2r0uRSkaNVSg/u62tT4cRKK7682INY3HDz'
        b't8nA6VFYLk/NiIT1RMYV1hk2Z1DDAv4vMMKeuhCemcdKybxgdiBMrhYe9CtB7ahOCGPcHA2vR5CZhcfg1bh4FojQQQZeQofQTsHIchsd1WF06Vy9Cl1aKZOWrZSt5EHg'
        b'5DkarsCrWIiXrUPbp5pwlRvQJdTp4b3K29NHii6sJmi5UgRC/fnKPMFjCJ4tgQdSMXejS4lX6jy6Op3FkLI5xkJ2SuJgzSR4Kh+dwVzuCh5jeIoSnkTbV+PlrSNDtgcM'
        b'zJPag10ZAI/Ci14z0YVVFLOxPNEw/0Fl0VZ4qrv8zmJPVIOOwQuClNaGmdptjHANK8pWws2rMVRdweTFjMX6K+g8umLBw5nHw/VZqEXwjm0cg8WMU6gTrsfN7iLSBbGA'
        b'p0mAL9rCzcXp5ymBxbpJjRhrB7fRrR71rkadMk8xCE3mYQM6nkOFdxqDFoYOo6vwImwrwaA5Gf/CzXTFMmU82pYRmYx2wnNJyfA4PCEBssdYdBA2eVKaOBMdS/CKJDFe'
        b'qQuFobvQOdiFCRqYLQbL0HoJvIn1mA0WEqUTVA475iXAE7j5UBAKN84VQpWXewA/AGLAEKvy3KJIwcFxub8YyADwa121Lm3h5H5YgKfJH01hqfE0sUyv/LlimZD3LyaJ'
        b'kDd4bZo2aDqwjCMgVZeSS6SMCGKaqqfmKEcnsYxR59JRMSiFVdJKVPWYfkPFpyzd4powV53eeiOFmx5c8/tpTybHT/iWeTL1OyY0yy/1u7mnmz/YvJ4PvBC/5NUNoTNe'
        b'eOXtBXHNNb65H8X9W/nsuvh9rSte/8hq2h038iZ6Li871zh/xsjbgeeKD39UeWzmuRzx6Ev9IppvTZzxTuz5zrN/nxF5vu4Q5zPRWrRTO+gT8eP9d/x+3B+/7nzqWuuS'
        b'/8v+SXnu3ePnc7KOF2/b5v27Mw3X3vvLim8vlV+4+M/nFx1Yfe3z7enlv//DgIOTLtSOmzL2v6mV/3frTyO3nywf73fk3WW7z2k1jb7xXumffrv2768kSi5/nblJEbz6'
        b'6osjG1KH2lp+GBqkOzryzzuWvj7qrzNXPjbVHLp317ihK0b9EvDjnG/nvp97PUXDnvnsucf7j3r/xAKr1XPfxPLxifHtP2xLVv5YuvLWX4+N+uW7A03Xf5g8+52xz1X+'
        b'8v2hSwmvJZ2ShD61zv+DNQqPZIUvFRXDlrGpJLK/UUkp6+UpHPBCFzgWq9K7zYQOZc+AVZjcMIBdhYF/LzM9D50TZMjL8DAmRQI5QWfUlKQvgDuoMSw9Ce5JTQuPIm8x'
        b'xlwEwKuYRUcxeO4XeEXDOrSLRjGTVSbRbI1PqthK+WJBfj0nnxyRQXpEJI85sE6CO3WLRVcWovWUmYgUM1JdXCth9Xi2Al2bSZteAq9MjUB1ycpkzE9wFV0+IuA7hctH'
        b'V3n6fh7anpsKz8wbics3pSoiVViwCUrjE1FrAOUkI6cS6x6qw6raThcn0114PshrjGottNcYwSUA7pLwkSRC9TraSZX7Qo04IiUd6/XwVhE/nIEHUDu8TO1/c+NhJ653'
        b'93gC6GRaMCFKxbAdBC/zSfA4Okbl5qzVcDPmoVpMghxsNG6SWfDzPg6rEiKiKib0dEo1wPMPlFElj2o0GNAnr6P8cW43f5xGuCNPXUz9WE/WzxP/sf4MuXpyfjhtEJHI'
        b'WZ76SBDHGrIfLaVeFH6YqfnQ/Wk/xp+VscZKB1tWsC4c82E67uIFRip5ugcPfT7YlYcSm/jsyej0A3ioCCzHes1esxTuQPUhCo5GKs7CKFBttxtNxFBNVZ7FmCFQm9kF'
        b'eIWEtjWpVfBMmt0CDLtYdMwArwqByO0VUyMiUeM0VWS4GK/tYTYOHuHyOBfZL9Ah/y0gwmTPuHfgjHxn3GLf2doB+YHOLQzRr25hcFTk5D8KxevoKXf5masr0JvMOqNJ'
        b'bi7U9TyFJcrTLW+yWa43yY26lRa9UaeVm0vlxFiMC+JUchgHCfqTlxLvulxdfqlRJ9cYKuQmS65gh3GrKk9jIN5z+pKyUqNZp42SL9RjrcZillO3Pb1WbgdA2itH3fiF'
        b'uQJ3wa0mo85kNuqJrbpHbydRrwU5UfAmyclJM+SOePGRKu3V4xH2UaRIV0E87YRS9oceBbXyVXjOcJ/6rMBiwi+F4s78s2ckz5xH38j1WpM8bL5OX2zQFZbojJHJs0wK'
        b'93rss+1wMtTIyRgNBcTDUCMnvpekO466ouSqUjxxZWW4LeKw16smfT4tJUwoXqtcDekQXiu8NqY8o77M3GsgbsYcn16qiZfKQnbS0NMj4cF50SlzzfbtxLkLk7DkOS8p'
        b'RTQ3IQF2KDzRtYoEuCNxRMIAgFpRu2xgLLrsBvZ+jrpT3MEe2AGfcQI+W+ub7/eQu3Vu+66ERvQ+pCFShfNQ+qHqW6lzekwIXQLOrcIHqXb5PY1hvYOYRELLlOrq3/7d'
        b'N6yJaPKjGiK+VEd+lqSR5X+hvqMuyf9Knazht9yRvdakT3uveGPg7MVDm+Tfqd6ZctnnHbN8meatZ99+FvgX5Zs1dX/sEH15WtOqBV/mr8h/9TNlA7tPGrjsmfN+r17Q'
        b'hF3yklwIjInSqrVfqMV7/F59Zo8Y/Cc85BePLAUrmHQOw1OhEVgovghvCF4EezHnO4RaBJPOgUh0LK9fBGohIjNvYTAH26V89F0rUc5qo6aMcpKQbk6yDgzlqVeSJybT'
        b'gpNmAIn5VBjtpMnFG8kOxC4ppEaHykVd/h7eesMIBSj3IFHqg1iHYanK/vuF2+YU8QaYuQBdjbBvnstRXWQfYaDdnGW2vyI6BfPyObDdV4+FobN9u+bECpAPHinot+DB'
        b'ngUSlYX4mOVg6etaXMy42Pix4+PgFXjebDauWmkxUY3mErqAdZFO1IUu+kplnj4e3l5wM6yDTSyWe57G6hW64oHOwBvwJJXnl3EpJD400dtPvWLmnGxByPcLTgKtAJSH'
        b'FKhXLCk32KE6K6NcZNIQ9FM1DHixzT8x00/0xpP/KvnDax8uDJ3+hqjmn/l8fehXx8fc/P2HGVte35/0oufnCZ+2jopL3nzswBddzz8/c1Py9tBDH13ZcEov2xfywYm3'
        b'f6lAatuHwzt39T/yl3FThzyxNDr01oCDfm85YPiod79UPKgGt9CbRGQPILowAu53WhGICWF6EOxEtQvvZzl7ULScNMdYas7JJWoznvhgV5iO4CkcB1BXGH9mjfKhoNle'
        b'nWNvxenDev94ZpqjG5ar8CWsFyzb3KLrZhDqfTUEOoH5AZCMOpb4K1BDNKzPiI3nwCrY6Bc1XVj++iBiDgRl+VJ12vAFUwXtFdXkDkLbROTMMACiQFQivEgzPxNIFcLE'
        b'/4aq0ybHTBBqCJpMXR5iMmeo0zrWegsARN+M6yclHGJinU4t4xbMExITRRQIy9WB6vC3zFoh8fupfkAOQFKXVa0skI8W4kAz0DnRPNSMtmeNj0ENPBCjzTFzGXga3kKX'
        b'aansZYMAVkknDvNXD+kf8YRQ1Z9V570/ovj54epgb8s6KgBGxaOaeZBUhZpFgAuBV9TMVNQxxhKHX8qH0WOOHJo2PBOG6pQpkU9MW4DqsMYRRj0u0OYIIrfD+ghPRXQ6'
        b'3VdWh4nLvZiJ5Fg+2XvZ+yd+CWhsa8u0MVLpIhBzfNS1lTtB5YSyzNfjw0cEslRTX4t2z0AXGWYm1rVAeqh9Xp9OmAzMuCN3Q9Sxkx7LFAbyH27q6LGslAGZVcbgKYuG'
        b'0MT3VdOAFQNI53j13Jlj1gg5T8xTBkWwz/BAXmUKnveNkiZamXcm/5UplAC/9aW7IyPKaWLriMcTCrgwTG3WF+0eO8qbJmaNChD9wqkxFFRVvht3p1LIGWCZcxt8iBlg'
        b'1ap3zXOCaeJd43ymnQXlfoM0RewY++FnSxZvKX2fzRQDdVVB8Cj/ZTQRxmR7tnBlDO7Smt0gdgZN3DxzRMJFZjcPyqoqd5caZ9HEBU8Oi3qDHHiRWWV99/HBCTTx7Xlp'
        b'pVuZRBEuXhQ8Fy2midcTgxglC/w+G6Fe9h+PVULr5wf/gTnMAb+mFZqMFWtMQuJ7Ec+DOgZkj0hXJ2frg+yRwMGV4N8ASOfmqBcEZE4UEpunvw+u4kEuWa5OuDUkXEgM'
        b'C5ABDDUxq7PUsvl6e50NM1caX6BCxoe588siAvW+pzcypqO47MejM7OeuNHydqLfVxW2vzz9jyhJ+XffX/2k6pN+/fz8/VtLy6rkEQmdl/yL2Nb8EabvlxqNs+q++uUj'
        b'07/BmptSj0Xf3I360/zVm2e+c3rDRxNKF/gtudt+cdmbr914yvDEoqT2bzs2n/5m544Nmz5a/PeP/+z7+PCi57MCY9/dejb2rOmsaQ4q3FD/n8SkFzoG8W8+UT7w4pab'
        b'udtHehg/Pvzp7vSxkfr0M01fFcFi9V8/PXygbMuB6ijdy55Durb+d8TvByl//mTHvKQJAXnTt/5UMTR74ZfLx0W807g3N5AvjvQd+CL7zqkPHv/Uarg2/PQ7f9As8rsw'
        b'PuuCetiLPj9VtlaH6NuPxlx9dvLAE/vro37yHT5U2fL4s0/uuf3BqrcWNpw48uRu0Wtvfd90tX7Jme/jw96fs378N4efE69e6fuv78CYic/P3P9Rv9J/vps85aN9Uz/X'
        b'H5zUXJA18PtD3++1+n+uX7t+zI3DH1w7Hp382CfLb4uer3066MzfPD4xzfnp4Krvh1Z+sDFh+aWPvStfqRy0PfXI8V2H7mzYb0k+s+a9m/tj7+26s/ybnPWXJTWf3o38'
        b'xfdWR0qJ4vtF/5Corm/eevSAQioYP46bYR2NRKUWAk8VsRGgpyuEDf7tcP2oCFQXDQAL25g12ZnwSqzAfk7DrTTwNDUyXCUCsv5TxCx6Gh4dKrxtQrVrnMyJhe2CiVup'
        b'EAwPzQXoAKYdGcnwNKFhVehAMTsCnkG3qFkDtsTAQxFRihThWDuRbirwRVVcKeZ+1HUBnYtFm7qNKhLgpUaHqVEFnS0XvJw2h8Ozgn8S2jqvxwke8FjAo+6J+z2628JD'
        b'y5BSB9ekLHepK8sdKGN4NtDHz5NnXI8wIv9D8P9g/OvPhGIOOIQR0zeeRNjk/JlAyqjFNKRdSuOIfHAJYrpYM+jX2bZj343IWDaJXU20iaju58Kv/wcRUJxxA7mnAQPV'
        b'Tja/Hl8G9GLzX4e7snliVIfb0Rl0/MF8Hh6IIuxLRPZ3sdB3E+6aZCH+IvAiBtVGV3Ntt5UjKToaXhKh02gbeppuRBGTn8Kxu1YIj0aoqEe3H6rBLPM0qhI4QzCRGGLC'
        b'vIC6+G/5kwXq+JZJhIWAqwqvRHXxiIVeQuK/1MTWXFXCyNXK50auAvp/vaLiTIcIG/sldmjTYz4wRjbn69Elb1366wTpyjHxC45GLfB9I5blOrSfB5aJVHUv/y30px9+'
        b'GLP2riEx+LuaCx9t8F5y9upnm5Z8U/787+8W/eW7g755GaI9z8+2Vv39h0X7/bfHwj8enXot4Js1/cYM3/vpIfnaENFLn332TfP8VxZMyRpTV77R94jtrYX7t857tu2N'
        b'dUOaVn2oPvbHmz//+fqOSTe+ms8HFe4c9s2w6DUzkxUSYUe9tRAdtp+g6jg9tXCO8/zUeLRLwP+dsJlzmBZHVQJqWcRSeadQyQV0LV5YpYVxDpsV2pxGtvcO8qXwkIk6'
        b'IKWhG7lOmW3/QpItXQT8wznYDp/i6Xbb43A9XlycRwW3JzgX0Qee5WbBzegg7UvqDOJIFR0Jdz2ByUFDmkIMfIdwOb6p1JY5ZkUBbMyAZ/KmURHHcYITGAy38PApb3jA'
        b'oRUG/s9pwENTCAfKuns8kd8A4u8U9riMmi1ZEg3IBrJCtDyhCMaNOK/KFa8FxKM4143R/f8/Hsuv4Dvp3C89DJzV8a7YTpjFXHR1Jcb14RjJKbqzwDeey8ew9FSv3Wby'
        b'Y5Ix3W5FWmYxp2UX81pusUjLLxbjPwn+kxaAxR74v+d2bjuvFTUL52GRDX1eK9ZKaFCKl06mlWo9NgKtp9armV3sjZ9l9NmbPvvgZx/67EufffGzH33uR5/9cI3U1onr'
        b'9Nf23yhd3M/ZGuNsLUA7gLbmj99Jya82sJmclUWOhAvSBtN3/ft4N1A7iL4LsD8P1g7BLQywPw3VhuCnQC1P1ephNp80gcCnawyaAp3xI0lPmymx67nnkVPPDLdMDyqh'
        b'NxEDHrWiaisMmhI9saVWyDVaLbHyGXUlpat0LkZD98pxIZyJGOftRknBIug0NtISUfLMYp3GpJMbSs3EkKox08wWEzlf280+aCJZ5DoDsR5q5bkVcnuMZZTd5KvJM+tX'
        b'acyk4rJSA7UA60iLhuIKd7NhlkmwJOOmNEYX4yc1Ea/WVNDUVTqjPl+PU8kgzTo8aFynTpNX+Ct2Xfss2FuNopNpNmoMpnwdMUNrNWYN6WSxvkRvFiYUD9N9gIb8UmMJ'
        b'PZROvrpQn1fY045tMehx5bgneq3OYNbnV9hnCvN9t4ruDS00m8tMk6KjNWX6qBWlpQa9KUqri7afX31vtON1Pl7MXE1eUe88UXkFehUJxy/DELO61Kjt2yhENkox3PNC'
        b'vJYjOKySpYbPvs1CHIVf/l5Nb1OyQW/Wa4r1a3R4LXsBosFk1hjyehr7yY/dnO3oqWDRxg/6AgOet+mZyc5Xvc3XDzh4UayykBPBUHsCcf+Ytq5HeFfvCJUsseBscGnk'
        b'KMIp0U7WIZCEJSmjotBmcixrPNwlflJXrGCoMDIfHUOnyBG2GZHwAuoioRPNGQzwh/s5tF6HLuhnsK+xpkycc8naTST8K+zjO+qXvxmRqwy8o06yxztELQjTpGjYiwOD'
        b'YlbHRGuXPnOhtW3btWpFY1f1teqxjZE113Z1VI86+FjNcHoy3oYn+934cBpWFkgHQhj0lMCS8717M+5kb+HA0VtY/D8ocGUHS16EtlGunIb2mO3HVt8e7ZWK9q/CQpvz'
        b'EPYBsJaXohp4kCoffoGD4FPkmLqkcTzg0A3GADeFUJY+vLg/ngW4EVXhmYhi6CFRcD3aVSz45+yBncQ0lhopwVpLCwNb8cSezRQEkyvwYimuciisTxoXO54DkjUM2psJ'
        b'L1DFxA8dRZtJx2HnNFSXniYGWBRk0LUU84N80twE+hw9Bs+cnJ5+feRXJqNhDEQoXxPkDrdRjnIqV09kY707r+47PIEVsq1w8tZGfNnAOmx4Vc5fEODqsfdrPeg7coqa'
        b'UMAKR+wU9RR2bDthKWmFcxq69zBL8GUL7gYNoOrVnCPE6t7AX93Nwo1w2tK8B3YoX+iQNMeuttynP9sd/bkX4LKf5dgWi3rYsUtzCDXVa033aWqXsyklacohx/WxeZZX'
        b'rMd0OtKEybXiwV3YKHTBK0dXXqY3UjZwn17sdfZiJOlFdxnCaXpOeXfjDuod5KTe9nM8a0Uu1PsRjPpu56a40k2KmLvRcXh2HmrGL2AXpirHsBYPW9E5em4aOjgPJ55i'
        b'AFbfu0AlqERd6DYtZ4pHu1FjMpXb43hMCRoDYRebMt2oP75gOGMiwc5vHlQObXy5X1WMjBs1ZrBiiL7qhcLhXNqKpOXWpZs+UIyO/vqrwvEd427eTHhDM3/ij9vmr7j8'
        b'6cTjHbnXJN5hT/4n71jk5UniySWNuedeTihavGfqF1v7//VH4Bc0kB/SpvAUYrjaU6a7WpcdRDFJRshiCTpKLS2V6FZ/YjxNFoz56MZMIwvr41Mp6UnDhPW6qyfIXFjF'
        b'VqDrsE2gW+vhdm+7PQTgf0d4FQPPo/ZVwtuznou6twJmwjZqbYFXfAVzy23iNL5J0KVcqJoyUYgg2Y5ujU5FLdHk6wkeE/h4Bt7MKqUUeMSijIjIJMchzfIsFm7Uj6It'
        b'qtHBZY6D+ughfbBBwpaiKg/BC3IrPBeG2zwxOwmeSaL8KoqwqVMc2qSGx92OB3tImqoz5BkrysyUpg5xp6nDZdQbw5N6NtLTVXvRNXtpN8L6UMf72c9W7SasO/DlQB+E'
        b'9a/3J6z2DvxPRaP8PkWjmYUaQ4FO8H5wCDMOHO8hKGF552FlJINu9cOIRn0fOsir7PILOq2CW6n8As/nRLqLLxjba/XlzXdEpoU456p/vu39SgRbJQ/gn1kW8vPehfOq'
        b'473q4xLfPC/edPcfnmXzDkzJXX/6+9gfZyxaOWDHwA3WS9Xf7t4TXAm53NnPbBw4+NPcH769PKNp2Ydff/qvqepny9a2zwu4UW5ReAgSQjXcilqpZFESb5ctFtoDozzQ'
        b'8Qx4GN6EjRkkOhWeVIYxwAc1czo1vCbILs2wCu6iR9UnofU57uBd7k1bmAHPZROjAxb96jFF5aMZeBGesQqxXVtl8IJw9mhqBq6sfUp0t8AXgw6LE4pSaCVoGzpB4p3t'
        b'ggw6P4pJhSc9KFKjXcGBdCbRXlTVLQOtQPX0dQY6bKbjQwfgTaecA09CwSYyhIGCHFeXiS51U4TUwEdHTd88CnA5Dujo6XdMfmM96dkdAcyakB6I0aPw/0L02YUv7X1g'
        b'qM0NQx/QEQVnExeWmsx6rc0D44PZQFi9TSywfLeII3cs5h0RAk4s5qkTU9+RRnYs/mgG00MhJz/TtVqi3BDMc5EWBGXQya1/FX2FzgvIm4Tvk2c5iECuxlDUG4WdWG8f'
        b'q1AyU3jEhcNSLQasSkYmz+rDs8fFS8hRkijOpJibV5Cir/4adWaL0WCaJFfPN1p0auLcI5xkoFXK1XM0xSYhTVOME7UVWHwhMpTB/MhUiFPpn9r5shAZ9pxo85fq5c+8'
        b'8ey7z7797IXWazvbqtuqExo793QeOrGzc9PYxo5NbZuH7x7eOrxu+IYV14aLXvq4GCtjEV5NC/6h4OguxQx5MiURqC3BjUqgQ2WU2/dTok6BAgjofwmrRBcxgtLg8Cmo'
        b'BW5JTUuG9RnpqCEtCrZEU+9NBWwSFQ6EZ/zhzkfHRB+NVpujy9XnmahoShHRzx0RZxI0XDO0B+y7l7PjoFhAqd3ksodc9rpjo2v3eJdsK5x5KTbux5euPrDxNTdsvH+P'
        b'/qf4VoDx7fG+8G0utVBhlDMIMEbc01wQz8U29f8/1CPFkudlyAWrklkwQlHVIF9v0BTLtbpiXW+fuodDurff8Ocp0oUrxE6kQ8UPRDuCdK8CEO/rVZY4HCMdFSyJmNDs'
        b'ZM0VaFc33l1DW4QNzYOwZTnGPNge4ES+i+i0xkws52hPcmZECroID2PMbY5Ohc3uCDgNtkj8Ucu0R8e+foKF8wEIOJciYA9BLKpX0f8tDpID0Z/rAwdvueHgAzt1n4+Y'
        b'MLXA5SMmv35KtUNsze0D+ygoUjQxWEpyMcZh6HMxF3cbYfMsRiNmAMUVLgr1bwHMAwv8GOoUuX/P78h3Us63tlGAHHsfgMRc4K7uR5nHZy17MEgSSUuuJyaxblnR1yjA'
        b'Y95wQYa7hq4OsvOBwP52QbBZbabfD9FgJoAVL6wyOhhBsUiAxHAxBsVrEjm6Cqt6fJKmT+DLK7UYzC5rZeoL+BZL+wK+XkVVDvfDFb8ObYyLwHUYX97qA7zO+dwPvHo1'
        b'+z8Cr40YvAy/Cl7dzsYPDVrysHAig+kN8lXxUePC+6DBDwY1U9IKjoLamE8zeoLaoTu/BmxpHLjzjcdL2XUY1GgwyVH41FJXWFuM9gnAFr2MqvJp/ZWwEV6Hbd1ix8WF'
        b'j9MTxeH1lcQuTb6M5ip0BIZSWJsIa8XwYqTyIUDNj0zggyAtVzgtq8eS9yz5qIB2BF/+3AegnXADtAe1qgjqGYYsycnRlubl5Nj4HIux2OZNrjmODQ+blzN2RK81kk8A'
        b'GTeTyxZy2QbstlabtMxYWqYzmitsUofxkm562iR2M6HNs9vwRq0IVFGh8hEl0BSN6BCFWfkNR2W42P1q8IXE2VGgk3rxLPHedP6yQ3xY6h7S68r6ew3xHuI7xNdHSncn'
        b'0C3f8O7YYtSVjnVWrO6yQbANhMH1onXoCLzutjNCsDgR2A+7cN+IFfzYbf3tQRn2daKn+t6Tzy4nZxESq2QeibgwGoj85SJvqTCHc18341POMfewep7Cl09YZ1A4z9BY'
        b'SDM8DQ92B4Wj83hYulw6MMcGRIqnBG6ehjZbyAmXYzPlcTHj0On+j+ho7HQyrkFb3Iial4M0kPmxe+ID969Bdh+M+ig++aTy3pZVmUrBCZ9vHekJwsAXg7yAvHj3jCVj'
        b'qKtmg1kCCFE5qgKy94JvFcaCYhJOHZ43RXQn+FrBL7MHK64VZeacHNZedD17Q9he1QsTxy1qVh7IODP52KRlQ98KP5L7X+W99HXenw32rryZdT5s48zxKZ+rKqZ/FCIe'
        b'5Dnk/ewZiz+ZemP0/rnT5tcP3R5+c9iSGX8fk+N/rOzcsNycP+svSUZkHVXrJqYUverxdfJjEd5BhdlGUdWIz2at8rxrWlUWFvTe7JNeA72vr/sFy/1vLN8FqDdA6Th4'
        b'TTD3LgYOgy+bghehg47Uy48FvHUiTyL5f4qwe+Oi/v4gNOwnPEnqpZNEg4XE5NVBQKm+zQO52vpPTRmgbq9Ry2ArakyPjFKlZWQ5zhdDm1MlaAvsQCfKKlD9bLhDNArA'
        b'jaM9UBuGg6doZaGpIiBNi2PJB5XDx6uFFv6qJJ7BfyUfu5UNDOOE4z6n/H4zWbWUMwxgFj6nn/LOeN5UixM++N2yUc03vLmxspmKl/+1MnDi4EWjJ2tFljs+iq9Hq9qK'
        b'NaWDBv6prvxoYnjWu7m5V14oiL2TGfL3/l6i8IGDvimc/4zh5QXb5tSYk8trfvhu9LLBle9f28p/4B8+OMhg7nr3LweOT/ui6mXm22M/fj0o3ar53d9uFIxbWbpvUVBO'
        b'ffWBsT/W//u/3KnTo8//7KHghZjGa8klgnUXA3ib3cLLlpZHCSebtcMaM/UBykUHu92AnE5A8No46r8Dj8Ot2RGRKagpER1NJRMpAl7oOvHTOwYbaENGuAOdhjvzIlBD'
        b'ODFikUCyBFgNz/X2Cv+tx7G6hscbTRo3Q/IId65l5qkPnR8xIrN+jJyVMgHkozBnnESZs/Fkd96FV/3mU2IZ41knvSINfNMHY9sud/WGITsNZagB3YgIV8EmpxSQim4x'
        b'YDA8wMNTcGecG8FxPw2nF8FxnobzSMSm720cTwexYXIIscE8IHpMcfaSs6mU2BzOEmNic5UVE7/w4EIuXiA26fxjv43YSP0XSiVFAb8f+gOLHpONC5h4dWzNuBcrV6VP'
        b'HLUurP/ksKzyaZf530psYuaXedCheHtw4KWxxIFdnfanQpWA1kt1/iBxiYokLo0wFgk7a/SNxsKD51bQz6oXJ/SPFhI/nS0BSSuH0E9en30iBlDf+9SlT2Iithjectm2'
        b'YlMCC/S58kKRqRjnuLHPI/J3nd4oRsY/c2L5ha/6bbz03ksR502fh89eqmCmLnl33yb2/dYP/++tr6vkq356QvfVhCnjJw579+q0x85lXq8MnJk689WOtrgLdy6Hr3l3'
        b'wtobQwPTTU0RysYLB/+5qxx+Of7e0s6ZC60/jy8a2nVHqmCETaRdOng9NbkEbUi37+osY3WwHXW6yWO/+bwbinxaXTfyhboj3zogIfviAVg6IVeCgDKKjsZz3egn4Ew3'
        b'9j3q2VYuOHfOjiQ9cW6D65k29MSIbDE8KqBccjrFuNmwEWOcmodt8PICt6g88keP5SzEaFgnEo4NtzKHAUG0NraSpfeclsf3XCtTHmZmSJ5ZoJVZNmgpW8lXkuPFRXXA'
        b'zJIz77E46WMVHea0ojamUrQQGELIwd5FnsYy4RMy9B35vIxIOMjb8KqVfLokkdZByl+3csZWnEvURj4kcxbfienZ/KQtcaWkjrFKyDHkWkkzLmEVTwEr9+JWNtHyomry'
        b'mRDO+AY5Bx+PQ1RuwL0V0YPPSXlpr/JSXN6Gy8+h5YUPtyQ6S4c5Sw/5tdKtDDkEvU4slMBpwErO3VcutB/Bbv80S64VaD0GEkIlECdPFSbLOl3ZHONjeO7n3xNZzPmR'
        b'E51fGMHwe56sOHlpJIdXGImjjkJiJMFcNg+dwVKiM5KT+RPJs5gcuK3V2WRZBj25oeKpUHaKAHLdp0Z2V0sPQKcRS8T7xkjETRuz4hFDvm0y8iUMU6wQG+tPgHMShVIp'
        b'9e8k33MQvgrhTw/r52kgVrDLncz+X0pD1KXCphvs9IHHUjHcJkfGh5MzbajPvHy+KITH3L3G183bwHkWNsEKKzBJtcw8QL7mQ6efrbbL8Co6hcZxTsxkbIzpVxRGbzqo'
        b'HHNpTnGpoSCOc3zYkSOqiPBd8U0KX1QFbwidxGopqhfOPSSiFxgNa0QV8KbS7fsrTv+rcbSfWqaIMcqIhqHlrOSbOYyWPwzI91hwr0WBoI2xMkGA8DmSQq0EYvsYqGME'
        b'O6qcxmjdYYXBiNbk64uLFayNMdiYwl8bGBkPGRcd4CQyME/7cvH08xuCf9fNyQiLrMFE98bjIV82xqPLoEMVg9EheGzVafcJ2GX6DNi9/4fgep1e56zSJZayOyjNFlkG'
        b'PgRSzqNMPec/Ko2QeHjuc3jhDyu5RHWyKavCHlYVRNzXpTMkWKYVZa0C+n/c/RdjKsBvLjV++qV6GT2CqQueqe6o7trzh5rh75zc2baprXr4vqeTTlRbmDzvmZ6fzDiu'
        b'emdG26BNojSvgQ018iNDlUNfHS97rUmR5p/of2TEkNBXpLFjahbJwq5XJdToDv48PC+GK/ACVzsHnVpgswuo5Kvn6KmIyDAS24sOlgrhvWfgSSGApH7UCvsn0ezfQ7Ng'
        b'Ze0AqkZH6Hv/RdPogR31aWizksEZTrGoWYvOmuEtwc5yFe5ZBU+lULe8egbARnhDvJYdgVW6i48eJNyvpFSbMEH47kCOVl+gN/c83dZ+QJOUEb7GImWGMMZnnKj1/yoM'
        b'mFQzk3M0V+Xye9stFDgcv02H52AzHnNzBuwcRw8ITsKSwIoU8pVQ+1RNhCfEa+f79E0yiA1IIBSE37UJn5NgVTaRxpSnJwezXwJOHtz7W6CSQl15sT6/Ip2zf/gIcPQs'
        b'isef9EeNjwfTI8zIF8VP8ViJqGHRdXgFney7I4Rpky9sUBYYQD5IQ7pTae+cvVvGZ4VuTHPp1H2O1vKwGOwdnNtNwYh4IhzNuF6CLqF2tCcCNVPHAGdfyalmB+CW0Q89'
        b'ZYUufbvvhHnkxo8TvqC0yGXK6PEqp7BS9TSsikuNjUt2Oun4DucmLxv4G2es8DfMGO6fwEuX95gxesTI7dlwD3w6jXQx2S5w+qCz3FjUAQ+4+aA5vwdGeKGWwaQdy1Hl'
        b'I6zAGG4mpJ+rZrE8ASo54btBVhYTenalJ/lWT1m8lSFf8KEkUaSyhcaMjY0bNz5+wsSE6TNmzpo95/Gk5JTUtHRVRuYTc+fNz1qwMHvRYoEREOlUkBMYLBLoV2EkVvA2'
        b'sbA1YRPlFWqMJpuYHDwRFy9wf4+ew4+LF5ZHR4ZPv2tLWZ6YnhNDF0oyD9bC9bAxNTa+25nKN4ib5OtiOXJbKJkdYLSO79bgZXnRSSoY48u/Aipx8cJSlPYAFTm6Da/B'
        b'2iDSg+5lOMrFLEGX+z4GkX72mHF+9hj35r5HH/b6ZH3vr23wgue0qhjutwckn/HGaLQjK93jCdQFz8/Fl6653rCFBWHoKl8Sgo7pp3xwgTEROCrJlX6pzsZ8R8PkYd7y'
        b'glr8ugyM+WDEIT4+aqo9kB4dD0GtEZHJqGV6IGqMlgCPOBa2adAxgVvU5eXbow2XodPUwY6GG6J9Eb/22WK9qTTHrC/RmcyaEuH4B/opF1dqvsb4unNZ2L5t2y4GS5LX'
        b'3CeZbnH7gDE1yZ5Hu9fCOniLnHTVQuUJ3OnIqGTUFAnAaKNo3Qh0cI6bp5m74ZGze5q5mB3xgno9pEunmy2AyAS+vRa0n+DSidrQtXWpmM+2YDZ6AT7FA/Eg1nMubKei'
        b'RM6AIKAMzSGK8dIbysVA+O7YeSye3oyLhZ2xMVZUA0YAiYqB++AheJK+z0DHJfjt5VjYRTY6ePwe7mLg5RB0WYjS75CMQttEAEShox74shcdoI2pyweCpEItvlEvFQ3x'
        b'FYSZb6cqwKslh0libljJQEC/jAt3oX1r4UVyRF042gYmz5xK865cIAWfpshJ3rRlcfYPKfcL5kFZViD9XG76sCUYUujZSJVwD7qdmgxPrx2nFAN+CAMvoIPFtMRRz+nA'
        b'uoRnQJna/0KMhz2MetBUMH/gTwDEqP2HWmYJianLxeDDrBBqN0gpVQJ9TUUTb/ozfrNa8sbs1mdTnkuUbfpFe/xA/IKMJ98d8PuQSvb/YOOGF+W5bbV3Z7+09PSMfx7+'
        b't/TrfZOet4wK5X+2/jhz6cHBz3vfNK5Mm7L86quZiwujQ16ICKr5XvLt+V1tEYP0b1wte2LbhJBf/rGna3Hhx/WxN0f+sGpP0rXPv/uD4q2yO/tfjqkdmVU0KfO16C6/'
        b'j7o6Y/+R9U19ef3T1rfKVdko02rbcdV3j+mlP7ycvWSHorxjzffJS6ZkXXvz9ZS7d4Zv/mDmrqJTke3FnTNVgZH/6JxYrNzxdcGf/v3DWjRUfOv5e7v++V/J0W9n3PxX'
        b'pkJMMRKdQ8fQVoEekc9jOGwRO7GIJnydDrXxTgEP7Vrk+Obtngi6JbsSHhfZI5rhQXTRfu4ZxpVqSg588tLtbrgx0wVHXBbWoy3ogHBe/Gm00eKVSsISxsa7BSbAQ7nU'
        b'K5aDB1JTaegyu4KB2+GtaRFw6yOcD/4/sGR6l2H2o8vBdGhifMzY/6e9L4GPqroeftusmUwWQhaWEPbsKMq+yU4IBGVVVIYkbxKSTCbhzQRCnHEhlplhFQRE3EAEBAQU'
        b'EFEU7XvWtrbVUq3asVqtthZr1aqtFVv9zjn3vZkJBMR+/6W/7/cR5r1337v7cu45556FINDIcyHQzRLP+JkS7xQdgFM6AIpIfB9eIL3gdPL659D1iZWXY9CKWemI2mua'
        b'lGq3i1zWxcHXv2PAXVB+yXGJ9jywrNZOod3q8xiebvWZRdqWFUXTigtJrBpB3hOXXXGZxPXjJXXLklpatUA0qpE5aO5S3cf15noHgtWGQmAHmSE0ZQ5EDbeTiwANhW7l'
        b'wkgtmgKSUhwwwU+CzdWUzWVArCyIExB28CSTq58+h0VZNNK1i8zbLMQSlaqwtAPeB8SdAuTMKEypogPJGvOViMgWuQzNYARpADLLIu91usPQ289zGEoYxgX2DqSg7zO2'
        b'dTPXllflaQJKg4nydObhlKE1YtTU0tzsVpTxONoS0bvmqOR3t/oBX8AsfHVt7qjN50YJIz+68FxeJ/uXKL/C+KLsPt+FKVTwVXx+JTZPHYl12SIaJvCJoYGTEKajgDb3'
        b'WrCRSeqDlnJ0vAyUB9IcaPNwJhAdvdSV2p3a/ZJ2rG5wB8ww1qM4rIgZEgrLAQqbTXw2dPwLw7wD+xid3onYx8SFE5QqGFpBliCGGBDRdTJ6igyKOISUw0J4S46L8TvE'
        b'FudwsonwGXPF2fzRN4xrbfSUFo0jDK/OWzvm+j4Db8y/fhFciwrwubRw3A3jxhLKfAYrS4wnnTMFFBzi0FGzz12pVC+JmmqVppbmqAn5PnDzNC2HYSHcX4qKUE7U0oxC'
        b'WYo3aoJuhARWo9iL4d+paPYQUruMyLti3E5RMowFkDVDBiQkRgWuyOtL9gTVw2jjRY3MYoipuq+ezDxaOKg+bJJbtTtiKEaH48dtNBaAdwsZHGLijIRQWlF1RemH1x38'
        b'Ts5XGhBkwNQDnAuVWgRlLF7py6SAAG+F1m4B5FSmB4kwgfzELBgXnls6fQFL0RxLsYml8HYL8Mom+rb23G86LipVRHn7WSEvj4YDeo+m6tu0AvyVdR484HF73I0wCO5l'
        b'bs9Fll3U0ay4/ahZiX18NN61bGLjKZKZ1BLwLCmDTXB1m/ZUclH+9JICIg7VtayPea639kiR+qApP1k91LlSM3ovjp+lAyTiFopuiTzoQecuNG0W6831loVWeGeSzfTO'
        b'4rbU22SLEQKMzwJQDFWarQvtch/0xgfhJNlxu21hktxXDyfLTgg7dG99EnnxS5FTIU1yh3dpcjq8c8beSHIXOQPepHSI1VXOhHeppMrMLUyT+4VEIBxQWdm2MF3uT6Fc'
        b'uReEusgDII0ZapAn94ZwBnl96EpwdGA0aTKMidvrnwDkVmzWGWzAOQZMjfPZyfMrJ0vGM6GtQP/xQRr3M9/Cv7P8SMDsJ3Bx52vlsQFOWEQuWpTkaNrXXFnt/kmMgBLa'
        b'eiRUq/TciOfRb1RP3EmRvIb5aXBI+AqowCcEVP2VtZ3rcUVtzZ7KOq8LIvw8oQJdEysQi9GhZMEoOZ1j6mNNTmMNxkqPmlwI9mkdXECPDNfJK3HasS01sWRM3GFYYoU6'
        b'aFhwkcdcrkEBn12806mwN+LN7EDKxBi/zbERRyjfei0xqXndMes0PGlhjlgDoiw0CMpQGfkDwmhuaTa8kRrMvmzZFBDxDpCex1MUeGNhqTI5I+4CyB89EtNY1RRYK87y'
        b'g6J84VmhdBC0gGzM4iJVPsZB4m86a7qpMNjfh5src2FtBxJR8fuW18HGOZ6LqzaQqfSZlKj5QuxlF0AY2HvdZIX9t6IhZUVQxUp+brqhe4icDrMwMU1FzDClmNhzucYc'
        b'pJ7zM+a+QH6XYb0YypSi8jXWwuRrASQB8QOvbEhqYeWj9thMvwDjX/kXXP4k6oQhVrvjrMEc/80K1sYrqKCj9KgFM6sEDCahhso33AVxpm/h8lGHqnU5t2qQ23mgJiaR'
        b'GIbJFJYQ0QjT/K6HabJOoLryRl3RrXTA4J3hmYLX11jZDDXEdcmqbWZm9vW1ELW4WR0uSeBYgey5T0VdMZRjnr75tvTEdrDsO+/ky1gzhFgzhFgzhMRmYJfzzO/17dQQ'
        b'qn/HZtSh9SC/0flIiSgCf4mC04oIMf/esR3p57SD5d9hOGJsJDyUC0M9wyK0o9CACEoeYiDMJ3QQ2oI4IK5hv6BPJjFgsFtFWNNXMXxAUr7CGlXG5lWSywVYFLqud7kM'
        b'iDWF+25DioqJR2t1xomQ7lkbpllWh8Uaz7zzMVqUONVKL9Y2NkrewtiITtFHFPY/GlFRH1HJiKvr50oVisTr6KkxtibWDejvMmGUoS98sb4Q431BIPzShtrMI+5psMv0'
        b'XkGX9M7zeiZW1EW8ePI6B3SuwafrbOe0ulxVTU0elytZim+cGR0LYxF07HxubCwMGoOcmSO3lNx7czWI3fKIv94Lu8tdwnpjHk2BbnmPi+GGKwAY13n90RREwmV3tafS'
        b'UNWOWv1N7JDX2A/eo97Cvu7GdcZyNCtudKiTJsVgluOcNcIiTDmv8jSR8mKVl2myyMI6iQgfngkj6E7to1L15Vd6UfeN+eSJ2tyt1Z4WX90ydzQZ9zAXEJBYou9zrFoe'
        b'NMzrG9OnDx2iwvpI4hGKwQ7kgW3BaFoKtioVL+901jQlGT51lYwTAuJHdNwosE6xtY+JY7TGa3CpAxqjtR63C5JsWMSaRVuHBHMeyPKdeHTN53A3CEFT0BwwBYQGsyLT'
        b'+jDloOsewTeXPdfyeB+tfwEYYUYgvtQZMLP3S50LuNZiWFUSSlRAabmQpyVohdLNAQuUaAlYsXMDliwOYgeIUrEEbQGbcirA+x4NoESGDWKIozmvFLAhluJ7MSD4XpSh'
        b'FRAXUtcZzAN2PI2L86ypL6JYBbaoA9YEUIx1HhmGO2rxN7nkumo/CSbQfgA7ih/mVVXUhhFxAfkItWR0zl854uDQXmOvbvL6mCZdlJfxQAMyjfLVyqf4VaiWmbWmciPx'
        b'BTbSrlBoN8kwS4WsJqIrmdG5VMHBZwiMFEKpHjs5UpbO2Wz1RhBqiKiwFbKcWyBMmVLATynIPFfml1qz12iN8udY4z7jGEWNhDLDDBD/oJ2euob2GYLLBIYUC17QWBRN'
        b'QGpIgvepS+fmJTqjwtr8SNTXm1W0Sg6TVXCYnJLTkSqlShnmDHO6JcNuleCNiWSL1GNVNh/6/Fw3U1tXtHR6cYV6j7bRxOVcJU25YfDcAkY45jdre4uma+uGeHSdJY2c'
        b'R2KSAjM3WDbPHVNawI6U1DvUJ+Ty8Y5YnjyXdLOgHVDXq/d3ONBBOEGiSs4YbAjw6/m4LY2kxsoGt4GRCHGpl06ObvXhHBGHsMStn6tuMfl6T02oil29X9DW+LQd5x0J'
        b'4T/fXC6BzE0lF4AoOA5ELZCPEhCoPLPPtZD5fBdqRJ2gNaOVLohjkR1yMtytslNOuR2tfDHYnBZ1TGppbFyhV/R8xJg2FZS3YNQKbLV8AinJx0lJxkyAq0iMBUnfRk0V'
        b'ykecvo0qf+F0igB2RVxORGWy+foK9ZcLUXRvDGGiJWdm786lhVC5YLwUw47MfC782romtubSzbbUMvqrN3/B3dIGGAmryNTYYPJtmR2Ki0XpHCHTjygJ3dDLNFiZVOLU'
        b'TucQw7QQerlc0xOKzj6npbFInRc+loZQ5oHic6B0GGGGAOGVfmHqBKS7sVowwAJy95TBOIAJ1Y0LN0kMzaUBxB4jpKgDEnhh5hvBmZlxTMdKnDYn8dk6a9IloTp0Bl9s'
        b'lHOBAbS4XB631+Wan9CHGecUSBE65xJgM/xcLacLSREgkHAvuTB2hV9drusSyjtvdlKM72gdymRMuUjLCGDfcJFSGBKHVbafu2ngIlL64hj2i20C/fEyMLYT2L5jQPMg'
        b'0lhjQK2i3WwVHWKqDYC8yHh7J3Ln+QpQqVQ96E+AeLnq3qD6pKTd5dJWdw70UGDQAHqbxXqxXlpocjNJL+TcSW6p3gJYmh6io3cEiNaFVsZrAyDIgKKNeGZ2xqiIps+q'
        b'qndX+8kwnd5J34MxVMP2YtxUv4stVBMbE7Et6/xC/1u4Qw3xneaSgFDNJQEhmh1NCVMst5PmXAgEWY2iUXx7Raqf0wkunfCUgPRssCuXMcFdAkZigA4dsILw1QRfZV2s'
        b'l99hJkJvIcSwxIk9zCfeqITz+AQSzkrEGk3xqL0MSIJWJsD6qbEEos7xhCK2+HXR1hjJ+31gmyLF2FEC4HdO+iFj6sJ9plOOSecuznw+EYVjuF3Pjms1jpd14nUwjn5h'
        b'TmiznaCYVWKol0Mko78p2t3l2tFZ2uoFy6fPLEV5tjUzZi5NWKgT1L2Wvt7Fna/RbglrlNAQOg0E1ES3KBDtbrTaAEgT0X7mjKamhpbm2FGkSZ8qXWLLTt+pwjCQOiIB'
        b'IF6IwSMTw9Ul/4pmt7IeH20xrtsF9lGzh8q8NU4oAjnV5yK1K2UJOlGvK43V47yFAv3FBY2FAhAQWT7l6q3zqYdZ/6oH4mBwqba+rLhUO44SsOpudb+2obQEQOaWpXZt'
        b'e6t6vMNBUoz5gXnC9s0RO6MHrSYeiaQdQJ7tJLF6pTiMpB4XNiMFG+bo2WSwMM/+ayKZEUGl3+oWn7+psa7NLed5gGjNo+NzJS/f7VfcbrQ82hSftAUXtnpK0UeiaQYy'
        b'xYJaw3W13iYFyohzQ/MqvXIeEstoSaJSluuYp6e8Qp3QyS8ozGPkdUdN4oQqdCyi0uNpWu4jyy9KJXppQgOo3hLDEEqejqP7OmYHq5kOGcVrZ86AZfMOPicllEEsh+/r'
        b'kwzAFxeRDHE2KzO5RQe4KPhytViprtEe1R4HIOZq0x7jtCPqbS5m3m1D03xyJo9ftVMjOdHLX6M9rO7ssN7MxnpblLDe5PjJk7nGRGdetoUiSTGZYe/D8y4r7IsSnXCJ'
        b'skW2IoEg22Q7EADmhHMu60IL7ZBW2mucUYe+GGYCnaNUTOlgZSQ2Cx/iUKipDmaXzN8rBqUYO64fUAF8HYojcrU8HTcg3SAoa2MsuLEBQf8CqGYOB7SDhIR/QPR58YnC'
        b'Ug7kjgwHaAdj6AmtPQLCJBQOMEFKkxGL2A/+BZzBmq0XauDLej7GyDMjR7wElyyx7HLxQshi/B0784zaXcSJdsG8YpsFokeGrQmK+A1NlmbFXVPX6kIZR6L+ooLXd2l8'
        b'Psxwh2Qo2AkCipwIOFnQLLVE5qlTyW+eg7gFsXMsGok4OWOABQuXIMJxBAcEt0SYCLUSnuUj54cHnDUotm4K4OnPasb5wXN833DiBknEx8lt9fqFgISn/eyYVLasw66e'
        b'b3CGdkiyFbbdAKXBKURDAkDI3A5DTXlUwHs7wOzNGId90d8TKEItmnaBvVkAJS7gUHIApltSRdQ0B8+CouJkrxyVKtBNt2l+pafF3Tlaxk4KkW8lCw1m3ZYiE90QlGE4'
        b'SiMS4HMnEqhk+/GHKHpAxjdLOvZxdZMXQImfIJIvUUqEmeSELIm3G0MsDB6UCfl7BIR0hpOP/N0xFtRXDKTQpiX63EujpiZFdivIvfS1ePxESTTGGUsXk15wdqzh45LO'
        b'VeF4h05N2WFGCQLK02bAcw/UGLNn823dL9LODieJMebodA7lcWDhjaXZMzQoApJFYj6kg1WKM4y47OJONtb2gAj7NoBOlCHBt/huQcIZiYCs4KgZ+ssNY2111XhQfsNL'
        b'PWawRcdgz47Dy1X8xfGtifD91TgtKelHJGRD9pyVoxd03oZKMyrMJZ6Roxx1AFuRjYdUxPCANbUTZanhGzs7gK9+ehLhaZofAFFAyIRteCVP8hUAsnbyhMjCKoE1ISMX'
        b'05tqvME4eIoqm9gTvIEezWRIq7mCnZkKLhebX5nzvA3epuXe+E6a16e/r89Z8039fXikalbSsbNQEiJqZhBMuQLfoEsIhr+KcdxeGcKftyCiyS4vCiKh2WjI4C3s0syE'
        b'KZWqH0hk8mYhlW/r1rFrE5N2gEzYv8RIk7nEY0uaMYioIMoisKc6QJpaBzB5I12LDuEOpiENv4A5IBGgLwZAL7GTqnrYBmogp/sFBPcGE8esTOP1qaGMxwutPzqnAZIc'
        b'La8Dqm1JYC9ZDa6xkonL1sb4xNCWhOXYOYu3DOL/OY7uQx+JyMhNp746D3TrRYsVsARsndLh42MVpyaUdUTwL9G7axzpHwzp740j/ZldU3sBWe4ktYyeA3rHmavaYzO1'
        b'tWjjKRcQ0ONZknqyh3byPKPe+I/cwsbQjxQiuQ20g1nYN5AO/HIuwoHkgY5ukDgNciMZ+yY1ap3RVN0wpc7jrviAFfXOuBja0UG6AWFSmMhxnE2+DL8g87TuGLks0Dc6'
        b'w8xEZqQUAGLSZSKWpJnYkxZUhHNZdRJRqjjbBZ3e5slNbt02PmKPZy39faUooYdjRaf65jofxqNFFbVUVvlQjiBqJSk+uU6JWlDsvanFHzW5Gsk7DPnSjVpcGANw5wTx'
        b'hqiEMZQ5fGcEBM6Ef8UnlYNwg3TCD8x8W5rRTeezNhGi2Y1eQmssTJwT+Xqo4Ne6bEVqGNcbwCCEyws473xdZ3YZD9CJ59qGB2BNAfwWlbErMR0sJeIBsnz4Bkm5wW+R'
        b'BexteGeV9XxkDqEbqthdxy1NBeJbYn09B0ILuBgb+EwaAbPqphaPTB1dWU1W+fOwgz7Yfjf+2zduboENqDroSuqeqKmxATpXmU3HZ7PmEF0eNbkVBYDOfHzpmN3ixej6'
        b'F5/H7W7WwV3UAnsMZVV9wTUclbB0i0k/xuRIkVQgQwd2svsi0Qig5nNbcqzvMU3nWijFHGMZKQNkmo8wG3mjz5UB0P+S0f86Ywc3RBM1hU0NU50v1mCT0gjPOoOpE4K2'
        b'xYsVyTYl8MBRhaYtJVZRFuNiaBRDEeW47WzFfWEeOJoDcgMQyzXFOUGpCTOSPnbeMYUJpeGU1NnOAmM706kBdIyuuEz8Lkmpwl6Za3SNMi9esU4UeVwugLXITe1tigkX'
        b'WAmdhqFLT6ikHq2DBDL+0Lguqd7T+GUaLD/sHCaLieelvMFaIjGbeTRK1Z4mwPmo23RxFcnlbq3uhCEMoAVWbH7igNnPXdUsDnI7ZvKkVN3ZTkE9gyUqNXipxUv9pTBr'
        b'Z0Ckrwwy1So57c40BzJsLXTmpj2urdSeRqtGsybP1tYv051kJ9eLdu3unA47gkW/094eYwChSLgEpGaMCYRimAslOTXEPMmIIXPIWmMmtqwNdoY0RpySLxg8n7LBLsFM'
        b'muEpVUeyND0qTbl60pQO8C6GYaBVIj+n4wV0kI8EoDFmcIc6hYV6CRWeKWySBb+ZhfRdwVAPPpt09QosaHDesv6+s8kQ0D1lQ9BgIjLDVmiLs7my1h11+Nx+V7PSJLdU'
        b'A07vwNSu+ZNnzymbVRFNwm9kthXgU5LLpTuTdrmYALkLHZYY+Fn8JPEiQ4hlXxGf4+kkVQurPhmLPZ9EvBBfWT83OZs2B2qR11jpJbuWaMMFgYAvPpuZZYhzEUZsVaz+'
        b'I2PwQGhLp2p0+FwRqwzy+WKmV8IJY4YrDc16BwTGyqoXlEVhoEfxCSXNgZ4UgQaFXb2dyaXTc1AETF3M4lACmt7CPr/DzAQ3CL/klZVhwBJlU7uwITUoAYVrCQjGrnUN'
        b'N5u7ltEmhHX/EOrzOa5Le//+cyZfPT7vc2wqk1NsBYrfTuh4VFhepU+DqBn2++YWP/VW1CS3NDb7iLVEAo10thk1LUdhA51fyeAY9SclEWqWXLq6tLICD1pMhjg1qUOb'
        b'yZwBopvptFNl8G1J1P+sYlHbNLdnmdtfV12pDMcsSIETB6HaYCilJI5IM8/ooJ0oPcXTmCAOToLV0N+ivpKof+kZqB7Ay0X8Eub9JqD+TBkcSpqiDQsW7s7CVtkctMmW'
        b'oJ1xBoJJd3Ct38B4J5FU6mdBB2D4jhwumBywKT8x4gaSYTSR73CvbAsme3MpbIfwU3ISfDXKt2L5S/0d6xNwBADXzOYaOOUdzFt2ZHE5XPPvISdnwIn2N+TkgLPBgk8B'
        b'JysHnvsEHHB14vGCDjkgT9kZsGCeshi0QS2crBaUEr6jGDgrE7+jrIpsCZgCyQE77P62erwm1TvktHVmyM+u+DEWMqwCZpp56RVn0Cj4GRyJuWdwzD8IZf7mpS/n/G3c'
        b'FOJqnBXHjBlDQxcVXQA3+LmMLuTzovyEqGViU4tSB2CHL0N5Za97uauV3VYUJDMBfjtJ3HrqvG4fA0eNlUptndcX7YKByhZ/E4ExVxVAqYaoFV/WNHkBk1WaWrwyOwbx'
        b'4nyVqt0eT1S69uomX1SaMXnK3Kh0HT1XTL52bkEKm+N0kC9RBhIpyph8/hWACSdhBVxL3HW1SyBrVhs7RnB5oDpu/RmoVyjCpLihFlFzFeOS2LwtjS5KwSSDJXyGt+5W'
        b'P73+Tu/NSUzek4S5Z5h0KoLT/UY66JAmlRQ9mF9IZgzQrtsSIdsiQg9iypkpBVt2kr7sUCqLFl1CIefxU2iXUriO64uOsnrQiTvSMtNlIcKhzpNfJFoJd08rcl7adWMd'
        b'Oag3wsvmAJ/J5Bsl2YLQzG/SWZ/mGEUsEgPUSri37Wy3CZUKKjnnXdFUM4Kx4Mnqgq+lUfkC51LRpeh/l5Tm9RtU1L8D5hSTOEOgRLpbziC0gNH6HbS2YFfBgwtDb6t7'
        b'p9QPqmy1GbuJmWvrRR2LVb9iRGcaW2fQnsxZqbC/r5DWSgWQyac5neGG2kAySZhHRWhp1Ekzuw7I8OomT5Oiw3CWuUGfvdJxH+5ocPPFWD33Q+39JoPzhHaZSIEQmf46'
        b'BNazJUQ2iKhZDAArN18YsWvhdUCvPMjrxSSwAL63Uac4M6ABchpkijEDUi1WKduZkd+ClnhHDVTX+pKal4ra7dpxTtC2873VlepRlLSLbfskgiZWVFSg7JnY5lywdDBg'
        b'FHwh6hSOGIivSTn3pIL+PlutDm6x4/NxVVCHKXXde30q+DYCunZ4ZO+Zc7+aM6c2I1i+9a51wZR+1tULh23N2zEtHJHuWHKtwx/d9+bf9qWdPn51w9ez7yur+fgXKf9M'
        b'+ccDbac2NEWd2rvP3PTyWy+3e558d9T7P8n45ZY+l/X7+rlHX701rYDftUlsO8KvLeuafVfd4gle4c5Nt+yz7JH5N3p3Xbz3Ee6kbH6j5J7ncp9M/mjLkMUP9OC+/sPI'
        b'5qu23tZ+xNljk9B87dbAB39rHqXN+Wf2J303e1f8pffT7k+HTq8uOVxpynTnv3lk+zLthc+H3/jLlysW3zbs+V2nyrtc+ZvPti8bddBzambWmU0399py5fBXbnhnf68H'
        b'C5565GBw8Y0rg5aNC/60/8iQ3z6359nnPnrf+9JfhQ/S5ryfvuDEi0Pe/nKOf92hJ6rCH5s/b/qYa+h6b/rr/7S+teOe6Otp196W/MCLS6f+OKW3lt/rH0ufmvzK/vRr'
        b'I0d+lHb/JMuIRb/nKz53/nHdaccvjo/evuWne95cv2T93utM42b4NrcPGpj1zufySe99v7ly0NvDfnx8uL1iY69PzePebxw3/Yk6/vqPeh8Yk3pi0x37v9n37hP9fv2E'
        b'c+jJ1g9n33oiu88t71z38btjZ9wwaVD/938z4eUznz95esWgktM9h/Q8nmH/7ZH9w247IR1vueuTv1q33bTtk9KSXdof9rTbqldP/XLJbvfpFx97xV+5Zvapddd/uOah'
        b'E2tqf77ecvpvmR/fuWNe4bbkddmL0oc85Wi484lHd309d/QHV6ptr39YNcJ3oFvNoNPinbvmfP31dWda1r34QnT3wcm57S33DV3bkrr66voX+/5sQFvklwPGvPpUeMk3'
        b'85bUrylc9dbhxteP7b+hbdKGdcEZbx6+9frdjdXldW+6tbd23lg9q3DUX0532e1+NVK/KPexIdFhXdoWvuv70xe33vzqW8/v+HbV/C+KX/7XgdNDbl75r28njTtQNOT3'
        b'Iz8f9+nc1qwht+zc+8c229HHhHEr/5UzZtgzX3wYHhTOnnIw64vP7v1drtNzw5uVd33w7dfdAhvCi9791WH51Mcf/uypVvvGWYdn/WXZ/CO1lU9PfX73sL1/H/bm/CFH'
        b't/255Nd/e/2DPz1y/MPcG5/eNfH9ka/uf2zdwJfcrW+/kjZ66uxDU3/UuOqdDQ239Hhy7C+n/mPsg+v3jlzS79vXf3hi7QM/aJdf+dXjv5Zdp28ZNCB/4r7rckPTb979'
        b'u59XzB4/vfRXn/xs+769yXVjtmz+5oej93SZO3Lj9X/btv/20gmr9p06PuaLryxB4b07t3NfjVw7zLFu1ud99jy94ReNzabov+4c2/7VdZl/Xnpn0rfL+7c/m3Nk2cE3'
        b'7vlETDn2Wi97QRIzR3lcW68+27MnGvgsU9cOmlaM3uvT1VWieiy7P/OUdJd60EEGYuepj1SUFKJy+OOCuvWG8WR9fpx6v/rQ9BnMsfQ5XqW1zRNZKSfmqM90lOicMovJ'
        b'c2q7kph36ge1g4u17eq97LDUhqrN6NZUfVZ0qe3aQf9gjLTeqj5bVFFCCph6Zvi8vqxtenGpup6Zx2IH6YGRdmlMV//luDepK7mE0stmlhc3dtfWFSSewLNEt5TbObva'
        b'7keWhbovPYOO7muzLyIcoT6pbvIP4dCI/nXaI75ScuCzoSXxlB8I66fOKWe5tt2mHm9bQJ5/B6mHtE2dsWRbZGTISupW0rAvlnsRpFZ3qYcYpB6ubgfM6/vsC9+xawz/'
        b'L8zs/6lLQW+2ff+nXwxuk6epUtZ9LSIZwFWayXzApf/ZRafNKTngL8Oeas3skpEh8PlXC3y3TIHvV9xvVI/uTlP2VZIg8Nn8UE/+MgdvtWJoQJrA94Ffbp7AZ5jhZ+1m'
        b'F/h0SeAzzfG704bPGOrTA3mumQ74peBTRmoub29yIOotpJq69cngHT1SebvFwTtE/J7rtMK9B++4Hq5DBD6Pd1QoB2Lsr0SjMv9/Ml/oEse5secWcwYu+2DbuYYmtIfV'
        b'R9BROLM8OGuGGlE3WDhnzs3qZrGn9pB2vG7/cZXz5cNMG3LX70s2/XR298tTV+2+7qO/rv7yrRey25OHvuARf+NcYT40Yvfchwbn3mides/EGb8+fOoPaT/v/v4dU38q'
        b'7p66c8/03+39+Mz9W+tP2fv3vTn/yp2bri/7YEboyR/7716x58c9LgvWtN9d9fa2T08unj/zHyXvVs7u1X/L5N/uDH/6w3l1Xfe98bS0eU6OfcaOIw/84MV5pq+fk65/'
        b'Mm3AtWu2fP3eE7tbd/3Y8fpvTzvm391vz2dlFX+Y+ehnud8+LJhentB1c/jGhdvd7++bcP3Dv39xxT+/fv/AMwf/WdA49PGNA57Yes32gdsXvtc0O3L3ziffql3xu9o/'
        b'PvxSw/3rW0t+efAXXUfc9fgLPfc1HHx+6Ltv7z7xSFG/3Y+eLpwaeq3eM/C1Dz1XNCQf3/j4gAfeuMZ99LePb/6ycNffCycffPxo1/e7LZgXXTl61PJQRclJ/48eeWHM'
        b'W3u35149/pNXHptRsWhNqG1a1+BV7jEPNnz17VDnmV8pM2b+rO/IR0fvueJntpbiva9Wv/Zel+D0guvfXPzAxm9fqz21dMWiYSPf++krr2V6cl4a8p7vmX47B/3ksU+O'
        b'/748OPnrs9szz66KBnqtyZ/7ly1f/2zFPx+USjzPvrnuib8vW354gv2Po7TavY/lfPL2gZdeCS34+PlvrmkZcf8/Bp+dlJV6R/M76nvjfjrVXif9JG9Nj8/yF6f033zN'
        b'+K5DXj19VZeSY6fHZ4354vLnxq4a/pw1lP2e9cfbFq/ucm/VqhEvPfrciK0nnut/qHld99tPBE/MGfPrW2xDv4n+7rN7Xz6V/mWfzz9NaVai3GenCsbSfg9b/e1X6RNr'
        b'rbamWJ9Zs32zxMu1Tdo+Fum+mTdjHNzhi4V62OExUpr6tKjeqW1R1zFDVmsa1Mfjjh6b1fvJ0eOgbD/yVtLVx/KK1EPFZk64vKt2G79YO8X5yQTlcW2z9nBReUkhmWK6'
        b'dRFzcqutLdfWWLjec0zp2skW5ppu1Rj1QTLtTdjNbuu5pr13qk+SicQKbe3l5RBPW1uAMYvMXMqwy7QHxYbh6nGq6lXqaqCz1gyapq0TuSXaUWkaOj7ZoO7wIx2tniwo'
        b'LtfWw2ISuga9/Fh17XLmi/Io11A0Hf3imTjzVcO1A4JT21JIjlRqKoYSZpZfwnPmVm31POFy9YC2k1z+jLpiaDl+LCgrGaU+LXCAOglqyDuIyhqv3T0IcD6gm4WbtGcC'
        b'/DjLtZShwwbo3gFtNX7QHtAeUI/yc7U7kylDbef1RbrlKrRapR4XBLu6V11JlVQPzAMUDq38Qcrruwb5KeoR7SFCXEwW7U5tzaxSnhPUtZPU1fxUdYNEvl60R6CfQlBe'
        b'GLCxm7RnC6dpW9G+OuBaiGD1v9I0CajRlTQXllZoDyRVLFH3lRSWl9jztdXqYfTN2U19RlK3q/dlEjKaqZ5Sj5IJMOgUNP5VXqEdHm/ispZIg9XNtVQdW58sGILpWJv9'
        b'6tPqNn6Ktn8Oa8ND2kbt8SItPMgCrT/WV32YX9Azhz7NrETTYmU4boK2SX36Fv4q9bYaQm61E9oTOeUEH2GQCsxcknpbd22XoO1WT6hhMp/UX9vVS10za1ZJWZH6rHM6'
        b'mVNLHyVCw59RDzIHi1DtTeXMXeqsCsrGebO2fag4SdtY4kexWO2hipug3ouCZo6fw2m7us+mQVFgBa2L+UC9rYVcoKqHJpNNqNzh6iptjbqPGdTQjqv3SlU8dNGzMEWw'
        b'K7ymxvKSgumQ0jynXjskZMJw7iakf+AQfSaXlQEmmqRuk5cLsBnco61jC/Nwnh+GlIm17kXzNGTXMV1tF7Vbx2shZjH0tik3lpcVl5XotXNqq0XtpFih7dSOMqdUD6rb'
        b'tJPl5EpVuz8gSbz6AJR5jBURUQ85WcNmlgEFcAimSBkUod0pqk/10XZQA+fdoG4pKlMP5hcMml6M8sy7mjyieqt6h/YkNbBe27S8vGhamchlV0jdeHWntkq9m5bi0h7Y'
        b'Nbj2gVqBLW6jdA2vnqyEwrvQcByuK5quPqL9wMTx5Zy2raWaylswdyrMcZxeaMoSOibQS3tW0O4NaHto+WQP0GCaMH+yM9XNUiqvbof/rLUbtVuXlgPpM+QK9Q71MZ6z'
        b'aJsE84gsypifP0+3S6ke4+OmKaFvt1Bfqg8PuVK3CnmfemuCZUj1yGCKMDG/rJysGBsL1KnuALriqDhx6CRaGkO0446OVjiTtB+oT2o7Be2pWvUYUSLqKnWPO26ts0pd'
        b'n2iwEx1K+FFDfuDAXAQsJbBQCmGAYLVuAlgyg3plbXmJul/iZG3vTPWARbtNu0ddQzN8VFVVElKXzZi0HCbFvX0ELkO7V9T2jJSYG7Ij6mGo1PpBJdMrWuj8EUoEpANn'
        b'4JDr1c3abnOZegxmIGYHRNVt6koCfqXTZgJsSdIeVDdfhn4U9qxgNsvuTqsii7ZI5OGqPKptQ4toR3GVMZ+lW7R27USRtn6GtqG8WA1pxwpKppu4LrmidmcTzDDqkjB0'
        b'98lyXLrQL1sHaZGy4umDoEgzV8yZtLsnDWN7xP2wM6zT97N1swqAmlPXAWS/TT1s4TL7S6K6bRozrLiutAtaPZ41i/YaC9TrSBvAlIcrR5DXZO3+5Ozy6Tdo62GSzViG'
        b'0xOA+AwLlwO7xXXqcQAoVPPbAWwegVppj6FlqI3acQAuAlDdsDPuHJjOwPUxGR2y6huae5lUwsOgrh5JzVrcXXsUa6tulwcZW+AGfGHhuveT1PaBaQT2smAEtpSXzSyc'
        b'aeHMkvp4m2C1aHcT2JsCO3g7GcbFxpZABwPAu019GI3Qbpx8CfZ4dYrzf59o+s+8xA58iYrbARcuSRCs/Ll/dqCTmKQKmq6TeIzjZF/0YwydomOCfIJdf4J0Avo2spJ/'
        b'gYwOeTooP4oDXxykp2yls0aHYBbbbuHO/ysy84yNzcQQUCjD5/a3NLtccZLMOAt4hE9sHz4w+uPLRLOe9C0md5AMP7Qxgif/vufhWsXJfD38ReaH56MUWGQg3AW4C3AX'
        b'4Z4Jdwnu88Lz6zi428PzUYMv0gvj12NMPsSH5htya0EOZdY8YqMUSWk0BflGc1BotATxZM8i2zzWRltQome7x96YFDTRc5LH0ZgcNNOzw+NsTAla8NzQnwq5d4V7Gty7'
        b'wD0d7rlw7wJ3VCk2w713gAunwD0lQBZ6IkkBNFnOR1IhXgbc0+HeFe5OuGfCvT/KUcPdEpAifWRLJEsWI9lyciRHdka6yymRHnJqpKecFrTK6UGb3CXSLSDKXDgHZbUj'
        b'feWMSIHcNVIqZ0ZmyVmRmXJ25Go5JzJV7hYpk7tHCuUekWK5Z6RIzo3ky70iU+S8yGC5d2Sk3CcyVu4bGSf3iwyX+0eulAdEhsgDI2Pk/MhVckFkqFwYGS0XRYbJxZFR'
        b'cklkhFwauUIeFLlcvixSLl8eGSQPjkyXr4jMka+MTJOHRCbLQyPj5WGREnl45Bp5RGS2PDJSEba3c5F+8qjIBH8WPKXJoyMz5DGRifLYyFx5XOQymY9MCljgS15YCFgD'
        b'thrspYyQM5QV6hWaWSPJV8njYfzsAXvEQZImcROuzlBKKCOUCTGzQzmhbqHuoVxI0zs0MFQaGhS6LDQ+NDk0JTQtND1UHpoTmhuaB/Ohtzwhlp817AxbwwXtQsQWYs7I'
        b'Wb4Oyjk1lBZKD3XVc+8JefcJ9Q8NCBWECkPFocGhK0JXhoaEhoaGhYaHRoRGhkaFRofGhMaGxoWuCk0ITYKSy0IzQrOgzFJ5YqxME5RpojLNUB4rCfMfECqCFFNDZTVJ'
        b'8qRY7OSQSGbwkyFeeqiLXpu8UD+oyUCoyUQooSJ0dU0XebKRJpgUdgaSqIQBlDYJSkmm/syGHuoBqftS+nxIXxQqCV0O9Z1C+VwTml2TI0+JlS5CXUXKSbrZjuMYdIT7'
        b'hx3hwrAj4AiXtQvtKB2Ab4rpTTF7c7MjkETn31OZvX2SxWda4gghOpciy+OYNW60MtlgU7r50WoHV88bote6mPnZrv19+QV5dUygszKvqqXO46/zFgiKC6FO34S950IW'
        b'plw1XmKgoajYZlPMBgee+yqHDA2SAglAXK3bX6OgzoLV3VpN8i6kK46n2U01UYch70NyPjzaD2kEmAhPdrQ73disuH0+CImeplrUKEZJMOUkVgRPjs+QwAbW60wrXtAn'
        b'3hnsEpJlbpLdAFnJhANKgEfF5qbmqB1yl901lahVYK1xsSNTZrgnbuIhBo2j5hrKJ5pU3eSqVGrJ9yQ6zXQ1LG/yelbEXtnhlZdlFnXAs89fqdvBtEKoxlNZ64ta4Iky'
        b's9GD1+f30VeSW6cSllUq8QDKx2KI0tGDk94qPpJV8DZRPh4YwsoqlkBxu5ehdXEMoCgCBUzVHnelEjWTT5PLo2JVXS3JfKMpGeaAImpHF8XsmcnnHNMH2a9UVrvRl6HL'
        b'BdGrXGwgLfCEsgVRyaW4a6JOl1znq6zyuF3VldVLmEgvTAyZ2TdDTOyskF/QweUcjh2SAuSEA1X12nWT8WiLCY2kBvnWTLLi6CQ7kDxAfSHIL+2xgBnGuj2mlXueWud3'
        b'2VfCyflxTDyM8AC7MWljdUQ5MLNRx+fhS9gCMM4ByyoH6xHgAfoINajlkCuTNxnSfRDDeSSfJQWksL3BqqwMO4KmgBBOahCUafBs9uZTiFMWhR1JXNAU5pg8V9geTocv'
        b'Tmi7Iwv7why2QLhnuxAwh7tCiYL3kYCgbIJ3ueHMGrRCsxXlsqCcLlDOIYqdDal7YG7eW+F9r3AaxfswnAYQx9KaR6ph2UErxLWEMyCuBPsE9HY76qC8AP0qwf7BU57m'
        b'BusdvFIaNkNKW2sp5d4dYhp2a+yQi546YIMnOz6RDx4r5GObw7F+CPOUzypInRJOTtKV1AJiOJW+JmejAd2kABrFSMJvAQEgbnIWx3SnyAKojdnkj8m9Ub9CnntgPOzh'
        b'blC+gP0TMGWg/kg26w/4forqnGX0iK5fY8wZx//lKcf/PnP6e/GvcWb/A2d8BYFoJ8NVCVtF4RyzYCWxnXQ0OSoyER8H4cLZhM+a+Uy+Gy+JTsEJmG4PTCfa4R2sGiG2'
        b'YNL0HYgWzKuCvmCcMMwF+oLJSFww8FXEgQtLsEtd1mEJ4cAVQRqJnnDymwKS7yPyzW4O418mDLiIInQBi7IyYCFVGGsASmMTB5ZMt9Gcd0m4e7hveAAshJwaE0zjnwRs'
        b'MH2vDtrDKHxmh3yTAvZwd1iab8C0S0nicnBjFuHZic8BBy0+yCmQBChiij59kzAG+xawj+aWbl3Aeb3hfuHkcHeZD/eF3wD49Qrn1/DhNCwp3AuXWAYgmfC+W5gPp4ZT'
        b'ETmrs9AiN+EkhuWUFrBCi5JhwsM9AEsj7Mzmgs5wOqAE+MaZxcGySSZUIQlSFZOLrFbKAZ5roNXr+aDJ+xG8MYcLIc+UQEo4m74DYID6poTzKJSnh/pRqJ8e6k+h/noo'
        b'l0K5eqibUU8KdadQdz3Ul0J99dAACg3QQz0o1EMP9aFQHz3Uk0I99VBvCvXWQ71i/YahHArlYKgmBTaJEkTwA9x6BJ8IBKCt4YHhZGhxaiD1DsG3PyDR1YJXmi9ZOF8g'
        b'D+j7GrS/rbcmi0MlPejPLjjPIFeRrCtI2PMIxOl9UUDC9wFJx5wS7Gun/bes24LS/wDY8T8Pny6H3da3Mg6fUHxQsOr2pc2ikzkqkwSe/ZnJHQxqBmdAzAyz4Z0Y7VKn'
        b'SqgvjDazHEK6aAeo5eQv9JcuOMRUPl1EH8bdRIeINH0MphlqVQTTmLFIgFpALoetOkwzh7kEmCaGTbSZA7IStgGiD7CMCWN3sGXUKX7yX2DZn7rxAbOhYc+6UcSO6NAg'
        b'm9Ggh7FBEiwKxDoEAMPprBHtJHupDEC58HAqWsak91KAYkLzksPo4AMXUgoApWQE0xhCCfOwfcMAHnNNCqfjosOOIoAlmgCkhm3DAPkbnSBbDsANwCQAc1x6+JwKKUhW'
        b'Gj3yUFruEjqvy//sXD1kTtCGkgRUKZIsdr6HiMo0bBbZ47PIntjpHkQlAe0LpyCaG+t0Se/0fOr0roB4ib5i+oLhTAyT6flJMLMcqFBL3+wbulG3oaK5JZsE/DHUoYMB'
        b'aQtbYN8ClBT2i5qA6FttoNM85i4Begj7Z+uUgEmJosNFhJawM5lgF4EhDFpW2JGtQOpwGRLn5xrsys+ZrRnmOJLSZGMeuBcSoe0Eor9LKCOUVWPRPcNY4yUB2girBOrS'
        b'LZyM74z0bGcDnMEGK4rq2jo6YIK7HCvBhowNSjsf0sI7+GKLpY3VA9DQwphanVhxnj5MzIZtzEkh0h3QZOhk8qqAJhjQmQ1ae2wqRtyTtOhvj5uZEqOCv0p5DinFn/Lf'
        b'2xZG1FnnczVV1biWKygRrZw1x5RVJBKatjNqBEhwJMf/Lc8ZOf9JwP0ls66BZCyYVLg6CMyjpHg6gHGzJJFaPgrVoGIhkmRmm1PMtuDbdItTZ9Wm8wXZjL9AoruoRxIV'
        b'fSt8ymF89yheHsPLEbIwUI3mb3zKUZLNb/PUVSnH6LGx0r9EeZy0meHBXYk+DpTjpHFSJyu5lCnQ3lGxsgqo9iWVPtR5jlp0801Ri894qPU0VQHFX5D8X9NlBQv+A3jq'
        b'///y7xxC4Jz8ARJZUZzngiCdewDhNGXTkQEeD5x/QMH+pE7+HJ2+/ff/zPovFjY7xHSLJM4YAitQrKnHa55DEi/rgU+jJ+K6FKxmIg8FgdpZgbosuzhycuBK5N+5XPqK'
        b'bKxshmXpVxSFZ2qxpNvPzj4O0bqb3Frtbkb7RgoeQ+JJSHVli8/tckUzXC5fSzPx/ZBJhtoi8DbJFQ8ov+5ooiFBh3R0Y5Pc4nGPpSMQtMopCYARCoAIdXYecwtn0t/3'
        b'EcjqrCHZ938ASqkWDw=='
    ))))
