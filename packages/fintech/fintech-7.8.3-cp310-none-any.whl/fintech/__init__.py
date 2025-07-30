
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
        b'eJzcvXdclEf+OP60LSxVRJptLShLt9fYC3VRwBIbu7ALrMCCW1R0URBx6WAvsYCxYcfejTNJLrmUSy7JXcJdLqbcxSRXkmvJeXfm9555dpelGE3u+/nnpy+efcqU98y8'
        b'+7xn5lOmyz8F/E2DP7MFLjpmCaNjl7A6rpnT83pBz1ZwLewSSS6zRKrjdcJmRivTSXRS+JWvk1tkFnkFU8GyzCJGJ0tnBEbvUTKeZZYoWGadj06mV2R66uRw9aL33vTq'
        b'o1dsYnWyJYqlijXsGsZjs8rjYT9FRp5eOa/EkldkVM4xGC367DxlsTY7X5urV6j4L2QA2hdycuHh0s7GZLNuLSDvZI5f82i42JkcVgdt2CwvZauYCqaUW+dhYysAShtX'
        b'wbDMBnYDl+52D1DkqXh1tnu3SOFvPPz1JoUKtGvSGZVS3c78jXzOKCDgfJYhMPCrjFvdtubfg3KZz8W8X09tZXqEkBZGSrVzdsbO5/AuKNmngjK3K5TOwjtDKaitcXAv'
        b'QVdRTXo03oWbxuBLGbgqaiGuwrWx8+Mz4iNwPa5T4WpcxzOzFkjxOXxrmGHMOcyaIyHnVusfv9J8qSnI+aMmXB/1SfThL7Tx2j9qXs8KyM7LKeAubAoZP4opz5MlL7Wq'
        b'OMsgyLF6BG7yhEIjSZEp1ugIXBPLLdIzA9FFAZ9DdXrLQEiFb6JjiagWNeLGQtScBClRPWqUMT7+/IAifMbkAWlUfDsXrjIRtBQv5OVDv8k5pqJ1eqMyR8SOKe0+WrNZ'
        b'b7JkZlkNBRaDkSM9QAbNK8SHFViTlzNrK98u5FiN2e2yzEyT1ZiZ2e6ZmZldoNcarcWZmSrerSZyaWVNPuTek1xIIaGk4AC4+D2QchwrZclVYKWPyNU6FD7MxEfmJEXF'
        b'qKMjUHWqe8dGoQN48ygJbh09qICA8kLvV9jXJcz4+9NKo74oDMj2ZSgWlRRYOIucKZ42/bOiAYX1uQ4suj+Vfj1RlM++yzF+51PeGfC5tK+Y5Q1vniHDHTfs2PAXgwLE'
        b'l5MzpAxA7Be38Hpkw8A1jDUGXkag0+igJzoRBSBV4cb0uDQRB8JjosNxVWxEAr4Bw8Ayy5bKk30mqVjrYMiE9qNjGk9oUFK0IhzXoHPohMCgfXhfKLotoH3o8FDrAEim'
        b'XgNfYDTRmfBYaDe5lTGeqRzehs6i/TQJ3oHvoDvikIvjPYd1jnivZSreSno2A50anIQq10arElMkjDSdC5wWbCX9noNPLEqKyEYnSKcmJERzjCfaw+ETabyVolPLbHQX'
        b'16bimsSUGFydjE4JjD/aOxBV8LhszDQovT+kmoEb0XNJCVEJ0WRU0O0VUIcPruHVCB6sgZAiBFXgAySFhBHw0eUCiw6hEz4i/I36EBGnUxJwvSqBVPAcPoq38+hGcDh0'
        b'V19I5I1v42tJI0dBiiTckArF+I5XDuInoR3LIUU/SDEEN+KdJEVCipjAZxyQ5Vl+BDpjUXG0MZNgoDZ5xsM4FeNaXJeUgA56Q4MD8H4eH/MZZA0jVNZnuOcEtBs3xEYn'
        b'qq0kWQK+jKtTk0nXjFkqTcC3cDM0m0K+Cd3EW3FtFL6OmtW4ISEqRgrdd5HDF+ficmsIQbzC5EjckAwjE6WKTpQwvQctHMDj7XNGWAlJozLT3KTU6IRI6PzqhKjE2Jj4'
        b'FCkTxaC7jATvjUCbaMvw8+i4mUCCL/WKhBQxLOOJD3P4Ktott6ogQcpq1JBEEkSSts8Lx5ueTQL20AA5GtPnRUuZmYIUl5WiOop5wWGowYJvQnpo1fzw+GTcoE5OXUDS'
        b'RU2UzEZ18Z34H+fOpQ9T1m9ngbnydsEusUvtMrvc7mFX2D3tXnZvu4/d1+5n72X3t/e2B9j72APtQfZge4g91N7X3s/e3z7APtCutA+yD7YPsQ+1h9mH2Yfbw+0qe4Q9'
        b'0h5lj7bH2GPtcfYR9pH2UfbR9jH2sfZxOeMdLJypkgALZ4GFM5SFs5RtA+NOd7vvSdD4OnhMZxa+SU0HfB4+jJ938RYgplOd+AvhLWOmUizH59GONEJnsepoVTSqIkTm'
        b'r5m2hEdnV6609oEUg/Dzo3Et4CjPcBvR2fnstKW4zRpE8h7LDI9ErVHxgP9oM96cxuIKvDON4kgyvpUYqYrGVYC0UnQSb8NXuEj0HLpuDSY4YteSwa+OgmEXoGh0hUW3'
        b'Nfg0LRadDUbHk4AuyUcPb3yHRUfxtknit7J+6DDwoXgCjhCPG9ax6GJBvPjNPgdvi4xRcQyHrgCRXmWXAMXtpxUCum2ak4ROAjVLGWnBOlTHhQNB3KYZ06eh/Um4Bmit'
        b'EWocgk9uYNGZXhspjScsRRcoFrJQagO+WcAm490jxOYfxsfzkijKRbGMdOzSkVyQNzpGWRPeZFsZmQjkmArNn7ZhJucTpKSADMD7cRstMDwaMq3FV8ZzI9CFQisZR3Ta'
        b'mA6cIBxaYMxEt9kpkwbSIQB2CaypNjaRALEHX5/EzhlnE8lo/2h0lZKJqhQfJeQsR3c5ZEd2XCVm3VSKmnBtShQgvW0uqmWnPoMvUvAXAYO+iU7hGvIJXfRdzWagbegk'
        b'/RYhQVuTotSE2gRGGrpOxSnQGSiRNI0PWohr49EZyFUKYpqdgxvG0aqK0C1UDWw1hkBZk4jusHPzllqVRLZq0EF8ELUSrgJFRsYkQM+oJUxQnjASYN1MuSE+hK7gfUmR'
        b'RG5kozOJZIQ9pBzaOcwnm3NDfILrnZUiUInsrEsp4qpA9SnlgaI4SlE8pSJuA5/udv/0ShGvNsyTfMubp8CLzwa89ZXm51kPNFW5D+BX+GXdtH0e8aNYQ47S+8VnozwX'
        b'l0/eVVlX59V/2r9ymiZe8Wkq3qKRvmlh3nngs+Hjf6tkVOXBd7IDZ6AtomzD9akqXJ8gqjOBYQJvxTUW0mX4gg2L8u8a2uuUgU4JiA7JLESD8AjCdyntRqUAW6zuSDQd'
        b'NQ5EWwW8dWSgqEBtw1vwcZI0FbAVNZA0CtyErs+GkZ+6TExzFB3iqFiuRqdSCfnBDamQ5wehW54WSkbbeyVHRsdTkYfOTZHjSxwQfpVgGUJxEVeNpeB0CAcCjv8zMiYs'
        b'QpKqQ/sdmloX3Ym+pZpTu1CoNedTnYxoU/INcpb892EVRDfr7UyrEtp5ndnSzptN2SbCCE1+5C3XUSTcE1w19XGWTDNvZJw6WUUPOhlhW/icFZ8m5IIbpIwQBfh8EHgB'
        b'aur/eL18rIiCXA73I7Xybizdid3dEDApZ5dgJmJu2zeffaVZ9sJb95oKEl96/17Ty5eatvZ6xSfnfjLPTBsnPPzmHujVpB1r8Rl8PikqHPhkEouvoK3AF05xJXyKONT2'
        b'NHxSREB/tL0zbuXiVrGPuZ4HyGoxFLiUZmajnxwGJpDpUJr5oqyVPY8JqMjBruEgWapIMeSGKff5Vw8DQjjRKHQzMZJqYMCaTbgiigXVbe+ATsPBOv7SnWDZ4Ba6l1WL'
        b'gIe4mtDRDh9jUWZRVo7VnK21GIqMdfDub6RZAmcdBj9oT8hc4Kq0i1IBgGlWtZqowqB88EwkuijB+/Jx+VNAkfuDUHg4QdA3kXeEDVIlDB1DrbHASqFmqBeIzR8k66lh'
        b'PLoNXPLk43FxIsFFlmAjWInC/2olskxPDFHSOZGTHQ901U/ZsV1w1f+0DDmnp/oVPdFD26OjnHkWvLj/+rFTn9T85YHmj5pXdA80S9D7Pwt+0+/1F9A8NE/10ivzXnvh'
        b'lXkv/ereMvzW64tfm4ffenEPF3AqOzw3Kvd+ActoT3vNTyhXsRaq956aEmBGZ+LVYN84xrkXblqOzvDo/OQ5KlZkK0JX1tWFPCSZ2doCkT78KH1wgX7AvuSAzvIy7tG6'
        b'UHOeIceSqTeZikwxkwuKILV5SgzN5ORsgtaUa26X5q8hv26U1M3i5EwEbtNAF00RfW5XB035f9UDTRGBibak4nLQ4HFVciSoh9ToBtvrIrS7OlWN64rAGABZvB3VytIm'
        b'MKhmqgeo5fvwdcPor1fxZqKc5++6kXw/PzcvtyBXna3WJmtXfnxC/0BzUvsAjH9FDulc/RvS10r+JTbqKTvP061z3FlMH4XUNMiV1LunzjD1cvUCSbnDrRf+1EMvkDR+'
        b'Q1Z07YOaaRzTF90Q0AnUgu2PJ7NuzqL/geFz3RBcUGcYFtZd5s1ExFeixUlaonDEa4VtdSrl2N57dH/WyCnHz/31W2HSDeXjVALl6nlF6BQV8eooVDMnWi3y9F7oEg+K'
        b'a6XKQjw0IBZOijIa7PjwxOgY1JAKndAYmQDGOJH3My0yZnGmPGftPMtwgiqVK/AFqhTsRns7p5QxoXingDaB3rDTQoTTCjXeR4tWJSarUxLBBMOXi0VdY+gQSX9QGNyx'
        b'wW3cva3G7DytwajXZerXUl3P7EVHXjpQSkaOyP7BziwqEDGQqoMwWh3YxZqGuHCApD7YgQNen/aAAyT1xnC8fSzaHkkN8Hig+rqkFMAGYANSJmydJHUirug0YE4sIJLJ'
        b'yeyo1fi/M1uB6Un4y9UFtCuGyeW6OYxSv/GNkoKYWI/3cscmVWdxDNVZggPQiUhUi69GJwDNXmbAzD7MosvSKdR5dDD1r747fBf04+bdZx8t3jilv+j0eWcGYJ7AhP9u'
        b'g3bqrplDxJcfB/ozgHTxMxSaZSHLihnDwbzlEnMRfAkvXpuk1WlP6E/o/6gp1lZdPq3/Esj9S40xJ8L/pHbJC03oUlOviJflAe+c1nInPzmlP6s9rQ2Ufcn90muwZmLl'
        b'B2x8UGLghffi+nzAv7Q3bXG/PpXB51vZn59vH/Uu90bUr6Qnc7wAp2WMV+/+509/CTyZdPEcfCgiyeEcybJIQIdp4opGDu6ZkTyRvQh5WnMexa5hFLvkw+WgV5L/opap'
        b'YLn/ChIvx5PwH65MkJjCOvBOZLcdDLlnKFgxGUVDkvmYGyv6TQ9oSGx4oJRTqAqsKlA7AQv64G2LwOZFW9GeJ7iD2S7uYO6n8SHSKR7dcM9LLVqQ2/DhZ/FdvB1vBwBi'
        b'mVjUhHZTdOk1TiK6sXOm2Ap8A0UcaonhRBdj4F8nzNMHMibCxHu6tLOZBqVUy5mrCQSLI6Jff+boCB8U5zfr7b2X+w+vaogYk/uxoPLr80bN4PgAjUf5foViIL6julJ1'
        b'Ze1LDY9+Mzxh/4ise72unpmtaaq9tXrWzd4BvQ9W7XkDvVKwM2L2u3Xx1/b9+85/8+/9Xn3mxuD3jO+d++cbL148dXPjS1/N+278uysP2V+ZMbhg8ODeU7dcHqf97hEz'
        b'Imzw5wdjVJ7UlkGnQ2PxEZADPVtpqA5dEtM14Uuo2hylUuGa5IjoBOLBPqQlTmwmYqkE3R2GzliIVmfcgGtHzcMX1fAsOrkZb1zGj8ZtsaJGvqX3IFQz2t3h6VTI8XOQ'
        b'hyjOPrhFiIzBVbiauBuApz83kYu24HMWgs5LwHY/0skWfB43ucoRjUHrJAvxGYDNvxmdikzkVhP3TDLY4Z6ojcMH8FVcYaE+oUPpYIRv8wI7PSpCFYMbQfMFNqMUVvRB'
        b'Nym4qGw2Lie12UpTSW2iPACLkkNXpqPrFNyl2eiw0wJhotXU/gCV+gSlbFwtQ5ci1Ytt0QnQdxzjJeflalzfyYT7ATNRWmzNKjCIoiKcEjM30Yf1A9rivpdyAUBXgoOM'
        b'CSFLJQrWC/6DGBnuKieoxypCXLRLUl7voF2/V3qgXdKbfXDN1MjwFFyD20A7r06WMnJ8nkNl+Dl8kdaULXWjNH/4kzspzZ8nRoKNDWFKpVUym7SKqeBKZTaZedg6mY1v'
        b'ZmzSFrZUvogxegiMhS3pyzLk/7OM0XMNaM42Oclnk5ISJjM6luQ0ldkkxZEGplRikzRzLcwsZnnKMq7Uo1RByrd5VHCmUlqTAHcZNmkz30LLaBZoWq9Szyoe0nnauBze'
        b'wNgUR9gGlmVWzTEOprm8AD6vKg+btIIFiBVVcnJXwdKccppT3iVnts3LtLrKS8zhhJWl/GVVHLnScj0Bmm1VbBWzmjFtA2gkOq6FdbTLmYa1SHM4SHe0ypOmO1rFkVK7'
        b'pJJCiitVEpoCfjun0PHNMp2gk2wGy3MWU8FC73rrpM0ym3ezXCfTyVs48sbmbfqFzsPmHciUettldk9Q9HidAnLJbTzJVeoD7fapYHXyfM70e5uPzhPGwcfo53ormP6m'
        b'8yJ12Xxa2EDyjdN5l/rYuCYwgAFKlkAJ9zKdjw3SBwFzzuEgna9xsI21cfk8fOut8yX3jveBOj+beNfLLX+YrpeYn34RIA2pzdfmq/MfR369Ic1kmw+9+up623xs3qQ8'
        b'8s0os/mSL8XTbd7k2SKOKWmDH7QhIF+AXCabH2mbrs9qBp6WiE+QJxfu5M73RTrxibyHVvbSBcIzowuq5EIYWy8Kvx/UHlzlTWpYqbD5OWGwkXZutrA23wp2E2vxFH9B'
        b'MQpRZzyUFYBZbowe8ZCLUnaSgZxDDlIrm7hycoGElktKWRu7ktnKrQJZ57HZoWe2yzMzjdpCfWamimvnYuLaWUtXA1wxucBgtmQXFRZP+Y6UyFEaXdcvO0+fnQ8GWIeN'
        b'1pHwIa8sMj1ko74gcD1UFOUoLSXFemWYuRugEielK52AepKZZRsR1JyZqwKgK1gH0DkdoAEXjKQCcvUP8EBTNFz+44R5APMFqfShr1a5Wltg1SsBqvAws4pK2ofBZv0q'
        b'q96YrVcaLPpCZZiBfB4eZh7+sBd9QW5drwR67e2W0pn7oYey0Gq2KLP0yoe+eoMlT2+CVkNnwPUL0dvzkB3+kB380CPMvDQmJmY5vCfq68NeUcrcIouznybCn8qrXWIw'
        b'6vRr2xULCcCzidEHr6BWc7uQXVRc0i7k60vAEIaai3T6do+sEoteazJp4cPKIoOxXWoyFxcYLO2CSV9sMkWQDvPIgApoSSr/do/sIqOFWBWmdh5KahcIKrRLafeY2yUE'
        b'FnO73GzNEu8k9AN5YbBoswr07ayhnYdP7VKzmIDNb5cbzJkWazF8FCxmi6ldWE2ufKE5F7ITMNolq6xFFr3Ku0dV9MdcQI+c58JSuRMd3yDj3UBkCEc8ohzrQ8Ua971c'
        b'kDuEnp9Do/ViA+G9gidvAh3iEMTj34Tv/f384Y0f6w9/AVJ/+i0Q0hMh6ccKnBR+/eHJh1VwXsR5wcnpGx+OeGKDWRCv33NQdgAXCCVCuRz13xtT8RViRaXgBrUP6AyJ'
        b'oL5k8hPwKXy6k/+eiD+pkzA+gQuIK87GNDNUBOWCuOJLBRtv9l4ltYAeS/4MIN7280So2TgbPxkIyBQOApAFJh9uA2ERwjRzwC75EKYFhA4IIgFEgEDEhXmkTchloTwB'
        b'yg4HocUTUQJCIgXIkAgHiY6UJ9EJUAZPnuAXhCEpZ9VoUcSY0nVCcYaOiGaJTUbrkjq+S8TaaTncZIY+C45nYTKzSmrjqA9QogZKTiXjSQd1Prmkuu7IO5XENJMMNW/W'
        b'W9p5rU7XLrUW67QWvWk2+SpvlxEsLNQWt8t1+hyttcACyEte6QzZFpPaWWC7XL+2WJ9t0etMaeRdCsksfQK+uXlFSVSELtNZ7gDWYSwJnB9FNz/WgQp04AnCBLN+8I0g'
        b'E+hD1GNwcTG+lkSnGxNQdSxqleDdUYAUdDovEl2VkLgSXNnN/iD1EzSi9XWbjGXIdGyOp9PQsbGEzRMzpqt95FKudHCpImPNVoO4X8kUywHPIKMpFHDDG96wRJRWsJ6g'
        b'GlBhBVgBIpCt4qs8yX01CbURABBSvQLA8cqRuxyaHjaOYJETCPe2ENQmvUr9oQ8IEIKNaA3MugVQMU/uqcYUAUjPQWUAWgWbzwBYcGcDQEp5oycFTwroPYTcwRuOZYy9'
        b'bDx9N6aK6DRACETTqpIStHdoWwA4lDywlLfRciHt7CopoCsPeo1glJJ7eE+fbIJpEZE/QEa0HJvgKGM86Jv+oG8KFkkOV5LPgi7JMusE6CwJkc86eN4gIRFYQBxAmDaW'
        b'5HM4ugHTiPHbLlutNVEvJp8L2Ayc1ZS/xjSDYFmSiI8djssMcqHoq6forzeZVPKn5pQdmOuVSXlkMVRcaJ5O8JaEMskJznI+lLkBgwQGFsxyZYR5gj3ACcDKwMh/6C+T'
        b'E+/s9z7cujhtdra+2GLukPs6fXaRSWvp7K7tqApkNRl+2iKgcRoDRF/kkxeeP5X78+0y0oFAymKROldDPVwAjWed02Q8EQYDoI2hnCJkXejj2+BUL7JIcYXkXvGTRFOW'
        b'CxyZo7IxrMN1oOSFIdQthfb64/1JyWriUG/Gm1VSxjOGw0c007q5QD0cv+Z4uOiZJYBkS7gdMtG7AQxAniMRKa+CXcLT9zQMzsEePIAuSYgh+SrYGYFZIiHqlErS3ssR'
        b'EjjHUKBPLtLq9KbHTyST6V3KcyQ0FESaI3URu/DTppN7nj2RqemMOL6Jj7Md4S24CZ3AW3jGB53k/fBpVG0dRXrwFtqHd5NpKBp7h2vRdnzNGRCDq5xeicvA6ZeFy/AO'
        b'KW6wxkK+TFRH5tppuFY4romNjwZzvjUD1aAb4YkpIJpjEqITU4Cj+Ho8o8dn6YRXQrA5PXphPK5TJaYkQ2LiZkhNToBUo/FdfAntkg6dhw4YdjQ+YMxE974zaOZXmlez'
        b'TuhPaBe/sAdda2rbc26zqrJ1y/T9LXvbqtsqWhcLr+RK2/KDJy5+LbjmszLbrlDpiPM2D7Nspsw86h1ul8+uyrp7fx/stT+E+fyG/7l/LFNJqN8ANeCLYbiWOEEkjDCg'
        b'L2pm0WEp3kNnaVAjrp9O/BL9cXln1wR04TXqhobePIlv4Yu4LpoEqq1yuFuQfUWoVUBbcFOphbi1VqLL6FhkTPTwDfHRHCNFR7i4fqIvZum6oqSYxJSoBFTvcP3c4aGf'
        b'JUzYXMmSpZ7O2Yynl6re2SY9SPLMwiKdtUBPnRbEcmE2MhuluYQVEcYkp9rXuoHdcDamU27XLJFZX5ADV8IhOlySkscTLWdaRe5NTqhMxQQlCdWSTmfKmfLA/d1dHE+E'
        b'pxtFuSbs5jgpyl2Ks0CuChdlSX4aZUkYN9PKRVk+auqP8Ub7iQfNSVlDInGTg64WZVtHEBQ6WoQOuRFVDwS1Djc4aWoUOmollhY+/mxYd5LqRE5r8CFCUWvRjR+eF9Z1'
        b'mp0GM5XN6WqWyicXaAuzdNop61mHgScw1sUEjLOoFl83u6AuxrXPQms64vnwtiR0Jj4FiMjptcQ7O2b2VOgKP9LfjLan+eMzDDqNt/RCZbgcb6VMKQOfc8Zc4jpcG4Wq'
        b'Bw+kXsg0fgTaj453apaEcZv3pdxTVJc4Mtou7slXwUiWCjDGPB1jgY4rv0FId7t/HPd06XLu3HMC6YVj+HZWEpm1iYGWNfvTmMD4SBLCtQBoPlqFG5ITFrgGVMKgZr0C'
        b'30mXUQ+1MpFGX2t6J2m8rvYbzFCemYw2YburSFKeGO+KqxyT8FZ0k3DDwo0ewdH4hHUkwaTzvvi5pCQybZSQMj8cVy8SuSZkQrvRTUftCwCTcJsMn2PRLUOT6S+c2QB5'
        b'bwzYfSrtb3e+pOFEr+bEfBKhTdYW5BRk/VETlfZHzRtZP896MytBu033StYZ/YNpn7wXxyyI5BaMqsiwj/rsmwtxO84v+HLUyDLlvP1HK2bvZ4cu8nn31/eaXn3r3q3N'
        b'bY0j9pSP6s+sbQj6o3auSiZyxVa0Ax+I9X6MQxsfny6GHV0pxWddvBPtFZzsk/LOkb60rKH4IK4hLBJfRDfd2KSTR46KFcuqQyfRFTp5uB2TacZUR4Xe+AIf7B9Ffc1p'
        b'eDcHViNqTE0FOUPmF2NAU/DfwOO6IQbRXV01DV8Xk6DqqWIYrOc4DtfL0EVaTyaqX0ln7gfg7Z0m73l0HqzPyh/PsH3IfHxmsQlMeWJKUY49wMGxmY2cnCqTxOgBvi2U'
        b'EdcyVR7HdOeV+rX6bAen7FDHOpcucgGJqOd1KMZPmmdyTEf5uDJQpm6FSyXhGaEOpg5s/WEPnutl8HXdWNTaiZP8GDZCIpm3TcBtktn4+jR0OQy1oFbUqmIG450BK/1k'
        b'BQTGhcZg4e/+zLSve5ewv1mcpdrb5wZL5yQRv4c9L2OUX8/LHvlbU9+18xn6ekfG33x3+LLh9+d8wT4KfkXFM4bpYyJZcyt8u9v23z51kxQ4zm/WmqEfPAxOCzFt+/v1'
        b'mT5+QbWDYrK3J64cXDE25U3NTJ/Q68F7fpH9YsrfB7V41/X/m2H+6c1v7vhmy/vXzz078KD3uMjqm1+9JH8x9/KYT1Y3r64IHHe5etbsfQU7Exe/dnJb9NXL38ZOjk0e'
        b'F3HsUmXNQO+lq08lnciP39lvxqyMIQOG1m+uG3gnft0XL+ac/0s13ruttS6wr/eaRaELFjZ/+t65jQ8mRO965h8qL6pEzMPNszvN5tR6uqL3qtABivsrsB0dikRl67vN'
        b's+Dbk0US2rVhlrsmY5V1ECOMTLUlgpL2dLxVjO1zDiaqwo3o0DNkLMWpmbE66fJprIXMZVjR/pwkfARUH5fiI6DDNDSxGF3HLZ0G3qKnVN13jABypyGfkv+QQXTu5wQ6'
        b'R1kJxRfQLaGWPricx5dUG0U97gJqXeDS49LwpgGgx+GqRDr/gxqj8aHIeNpgIR1tG8eis3j7ejpXthzvMzpCFUkMYtF4ZxRinol2CgAJrMBdTAGVtzkFlSXHQiZZov08'
        b'oTd2bUxmGXY86ISWGT+kHP00K0jqYhiebnTuNikF+p3Fqd8pqAtFClcFGJ7+nNQXzE/Ojwtk1/X/Qb7h0Pio+tYudbzr4A5PbSyDBriG3K9yMYvVcFnlrgEOaOxBA/xh'
        b'6ICrUterItPxIjMTbPHMVVZtgeh6p3omrardmyyg0ZrN2Xrgf5liuzx+VKe3su0ejkKgANoIEp2QRRqhoBoDBx3KeQ1lrVEEU3agTaiK8LiWvB7ZHMdMRLelaC8u69XN'
        b'KpU7fs1kOYzTKtWDpelwThF1RwKKDqfjN3t0sj1z3WzPeVoL9JwRek2dLbiVTnDHNeVOQtlcajJVkmkAn4dDiRKq5KBESUCJEqgSJaGKk7AB6uq472lenyhR3RVlqago'
        b'Z6iHuBugopKMz2f7JeCT1imUzqI3gFwNj0+JAfXGYRBGp6Hd00EpSg8ngf8L5J3XlLBJDDOyt6+HFTepODH0W7LYvRaQ47haYAR0J3SWEO+Ly2gidDxjonuqyIh4KYN3'
        b'aELNwgKweHcZ5tbWCuZMSCmMWd3/1Zu9ypQBkre/Zd8NPf1CWz/PuEGDZ70s7z3imn7a8cP3jCZNZImx369f1OwZvEAzQlOwbv6xay/oFQqV6fVX16pso07/evvNt3Pv'
        b'PVoze+Sf9hmGfPTcwaBVtqALyj4vC6As0QnwM/gKanJMf9smujFmHl+l1iO+M2e6GwdNxDfiZobTvGhXIL5IG5OEqmNj4hW4JgUUGj2PTktyaWyuGm8FC7XWiYFydJQr'
        b'xnfWZukoD0ZtqyO6G6+H0UHK9LPRfloG3o5PJlDmireEUTuZMNeb6LY4u37ePwWYayiqoPyVMFcQ3k1ORejH0Zx7uGoOYHImsTkpkwt2MDlmo2JwgJfA0tAZPgDYm/DV'
        b'ur7dCCDGlVskfWk7n11gbpfnWAsor2gXiiFtu9SiNeXqLW4s7gmKG/BGEthtKiOXcnLZ5GJxG+ByqLM+1O9+D0zuh6BVcWq1g82Z1pJLCekLT8qFCvWWvCIdrca0ztlZ'
        b'PyBpTOtdoJXC5QDrsAkJ4xosOtCjUNkKYFnmDQ5ykLut7QJ0maSUouOoXE1NmWfCuXmvsOROkxxRHMJ086q7/FvTmK6LnHJkriVI7E9bgtSJh7nYS4iaOq/wNXQRVZhR'
        b'M2D7RXzJc5UVaKoKX8VtltX4sudqVO9b7IXboA34mASfxxV4N+U6cQshDWiayWpcH6leQA30BPipTo12LkMlS1GiYlBbGlnehS7harQV3VDgu2lo5xOXz/J0Ov/Hxep1'
        b'C0xmeuSrEjWN3R6ctSQSnUh2sTNIljEX1GV4cQpfpfxucLIvoX+xibFgge+MRK3hLBOKtgomdCzZMKTZJJiTIeVIUJpr2rzL4ryEjwaG7+FGpC9c/6/z4XlNabotuZ7r'
        b'0z/5s3rNJzdry1+cu2rZhZ9lzW//6yfDbky4uCDoWH161Rmfivc/fjD+zwN/9pz/vDELVRKq/22ciSrByKLrfqToNIcP9R2V01tc3rEZ3UZ7gHOkrXQxDtBRz1DXmw/0'
        b'/lbqAsE10aLm5osvjEPl/Eq0OUHkSo34lhqSgB3OFZCVZsIEFrWhc0OoXgf2YBU66lqUcAPtFxcloKrEJ64L8dQWF+uBHgmHoLwn0MV7vBIE6jqT00Uiwr/XRQD3yCww'
        b'ZOuNZn1mjqmoMDPH4G5+uRXlrJdyjceHWgPjLHfR7Wa4/KwzS/G71oOJRebfClEZakxKjQYVtdE53qg+lXgqdoBx2gj3ouTsalw5egkkiNjTOnTQrxA+XBOXz+0ezUcS'
        b'7XfUWHQoiGMkZJXKpbRouqKvKGou0E/bmtX40iovefE61SqvVQITOInPHY230KhXFYybGV/CbR7eq70VPmH4gBxfWEOodJWEGeovlMrG0rDEYKDEy0kJURuUEaQyHobr'
        b'PEcMjxnWyQwJOWuGFpwCUXQV2haRGIVO4h1rosKJppD8rLdzvUS63LFkmGXQEXTRcyauh2ZQN86RIfM650bblc4Cesq+q0CBK1eg63SBaB+rFtUWr0KNa/AVfNWML6Ir'
        b'6KQFrIKrwE2uWqEl6QIqN+N6ukx2ODqSTmHdTVSQxtkFIKKTZYDBW/k0DT5BS0RHwYyxdym0Cu+0kMc2L4WUGZogoJpJ+VTzpyv28FV0Oh9d5IIInU9iJqnRAToI6CZu'
        b'Rqfx9tToBLwLnYtPkEkzGK9nOHwQ7bNQN6SlV5BnNFkNl7RIbK8bu0OXCWtDl1AzGEPlMnQLb8GnrcSsQccj0KF0aQA+yjBDmaHYLqFyoMpbzgDmLm7M0yRv6O0vRmL+'
        b'YYW4rjs4TOOVwKwAA4C+HlVM14BPe0aqSY6aIYhpR4tpx48P1yR/yC5jxPmHc4pRRBWJJGpGdfL8HuBcEEuZcBEqk5fiY3i74a70iMQ8Fcjj5Q2FKfMmqfkRAbZfrPjL'
        b'8KlTyuMzRhczEaGhg42M/+Hm9YPD4yPPDJmePS4qLfmlXudvLmMSz77APuj1s/sl208Pfu2rvQdKhjR67nkh8ppFMcCDXxLX3LjHM9Z71u/uD/3kg5akW4O1mhe9WjJ8'
        b'bCtDJweZ9xxfs21oWOz12btTRqX5zmj0PvvLd8rGTFp6MLqkpH2t+Z8rxuz7ekKf/Fhr6C9WTXrvw/jqN3+37dy7U7w3fS0plNwq+82O3zSXn1gUlls4d3TYBDay3/l1'
        b'dz5I2bjqqs+fTt+c0Ofz361bGPrFTbbA5C14nFvy19K/9t5ze2pb7Nm+vxv2zW2/dPvCkN//e/K94480k5uXv/n96cA5X+e37lkRPZ6P/OpIrzG/bLq5se/09bL7tUyv'
        b'A99867/w4aMhD+7+yvPhuGFv//Xgnz76IHVU+eia/ittL3/yaKAx3Do5db7K16FN4puhSRyw4fpIsnqyhri2PPEFnsO75lFNFJFl9pfxWWQHPsMy3Gp2eko6ZfSKSLQr'
        b'0gO1OKxsysx3GCij7gOq4vNJGlyVHBEjfvYs4PCRQcWix+1CDt4DtalxK75BB1rCyHEtV4r3ZoprZRrzQGSBPN+RSkAiqokMoLrDAe3tmUZFCRhVcmBiMeiyGAAqhn+e'
        b'DKeSANVpcFkkrkqISqDiRIKaZzC+k/mcnLmi/n05Dm9KIqYHlKyKVoPaE5QsrMcnpuG2UNG5UBER6IiFBVvuLo2H5aLD54vqb10/E5FCIyA3rpUxQjSLzpT0od8KcS16'
        b'LnIaPpGYkswywiAWHYD/l8Vg3j34LrrpLLaa8J8kQO4gdAU0b7941IRaRDHXgm+hu6IMHYouiWJ0FKrzFGNjd+Fd+GS32Fkr2roCBuDyE7VZ2Y91PvTpUd5RKUncfBwr'
        b'yklhCgkV8qKyUsH5cQqFH+fPKVi44/x4PzaYc86Re9EFlwq23/deNOSHE4OMvvXy9OMEmddDGir0vSDxemSqdIrpVs5Nfj5NE9wi2UghtztL1GDUg0QlbHNGNt7fs0Bt'
        b'RIfQXadAlTArLHK00wvVqHg6G70BGFljx6wi4G4bWEzrHTMfYDtdx3txrRqdSSau6hPoHPEyo8scPopu4FOU148pmR4JuBghhfFujrJwo6Z6Z/NdNMJAp1a4Ai7dthNg'
        b'XBsKsJ22FODsfXICXTMmkqeaMQGl9OOhMMgKpdu/NH2uwWzRm8xKS56+6444MYpOaRMsSoNZadKvshpMep3SUqQkfmnICG/JxidkWaSyiAQNZulzikx6pdZYojRbs0Q3'
        b'T6eisrVGEhRoKCwuMln0uhjlIgOYRVaLkkYjGnRKB3ZSqJxlwwdLCYDQqSST3mwxGYhbvAu0E2m4hZLYiROVZNcfckeCE0mRjuKhhT1kydeXkABCMZfjoUtGnXI19BnA'
        b'1GMBVjN8FLO70s+ekTAznX5RGnRmZXiG3lBg1OcV6k3RCbPMqs7lOHrbGTupVZI2GnNJ4KRWScJKCTjOsmKU6iLouOJiqIvEIXYryZBDc4kdCmOVpSUAwVjB2JizTYZi'
        b'S7eGdHMK+TBdjRdPtXUM3Bv91qfHOic10xbFgz6ajraOik+UpE2YgFpVCny9ZALaOW3whD4MbsInvELQ9cXdqMDPWXxaZypgHHTAuuiAs/vm+P2vc4WEk3TfCiNaDeko'
        b'l+keJdY97EMEkXFNXP5Pi2a7r+OSOBYBE65tOIv/ypmJG9Y6fslXmuicBK1XzgPNF5rCnD8yF6brJs4clR2aHjJza55sSPyt7WMar1eM6R+/Js4aVzZrX8jy4KyX8u89'
        b'XBk8NOSFdXv3hSSF1FpCQl4YtumloLgo4aJXSUGw4vcTFwfFxeg0ugca6V6/11/4gGM2D+6/v9Cg4qgQjMZV4yOjw0Xv1T5Og09Fg9Q6KErWclyJqiNxA9G4BStuQjdY'
        b'XJ3R/8fPokky15i0xV0mz0AO9RfYYJAgxBUeACzen4amrlOZHLzLLc7KgeVub0iJjpXmYoDjU3uJWlkxA5U4ZOV5KEBm7ueSOEx54Gc9yJxppEuOQ5fsiSRkMRqfIJTh'
        b'vlrWsVS2Qx7N9lfFJoJxPQed8DXg51HN46OOJor0wfy/WS/dc1yETG0l/mUBtQWOihs9cuyIMaPQVXTeYjGtXmU1Dwmg9tIlfAEMnjbQpS76yr0UPh7enqgRzPU6Dow2'
        b'fNUDn0GVqJKaClPXJzE7mLdGyvw0itzACNF+QCvimSbm/nxeo1HMHGZ1IPob32EJ1UGuDNnV52ctvcri/IQXbv7iuQxGviXnAeMZM6pX+FvfRwzTDz3g/+6bwyaO3D8m'
        b'ozXqwqdLUld9M0+77cgrcf9RF48JHpXy8a/W9P35fw55S9+RHHix9/axoZN8X/wPe+pUwCDfpYDTdA3dUbwZjDtqN+O9w10q57UCqrPNRZvQQdE1EQcD5vRNDB/3Q9NC'
        b'T1pRKM80FVkys0aN7eIOBSSPFACxAyhqk4jsdVFPhd6O4pxTPq4Q3h/yTXBiig7kroVLeFfk9v9VD8g9nQAcsyDSyfCfhNa4JhZVp44cyzOrUW3KTL8Y3Iq20fH/3sgz'
        b'eTayNFuT3D9sKCMaq3fQtvV4O6BkDKijMWq0h6bNHy9j7m+E3lKCXZoSKSJQTIGESR4NLZymSf4mZKKIQPTLwhg5U1A0GErWRFnitOLLV55JZDQrwN7x00QM5BzLV8v7'
        b'9mKigmcyTLGm4F2fZIY6MdR4mykdUGLHgjFxuEZg/HGZNI1Fp301Yum9Q5lZKfkgszST7aFxYkH2SW1sGcgJzYA/r9mTczePOl0moCp8NB2RknC9BG3dyPAadsozc6jc'
        b'RHeyl3a49BbEozMjZoTjqqhE4rQklgwxnutxYySxBoC9KlQJuIlOer/uK2NgoJTMnEX9PwgOjf4nQ1f8KnXD5PJnmbhjYddX7eo7Pnyh7RdjAzNvMVay0N1WoMAXQdCk'
        b'FHkzKfgubqNQX42eyHw24kvSFFPvmGViU8bppzKbAR/OF+01vZ83z4++TFszhQlf8G+GidOkJYU4Gj1hcRSr4Ri/4sUN5veD/ulJX24d/yv2Es/Ea6S7ioKn7BxOX64f'
        b'N4fdwTHTmldV5gf3+2o1fblvaAAbB1h3P2VH6ftDv1tDX/432MJ8Db9vZe5a/f7M+TPFfeuGZbDnPRZKGD9t0qZCH7H2balNbDjPxPnFN+bu8TCNoy/1Yc8y16A9bwVv'
        b'Xxe8YtEs+rJ23hA2mWPGl8XWlO7JDplCXzaAiAEuF/71vCbb+yNL4ujLZlky2wwtalq8KX+xJWwjffn8+CBWOSJTAOx75o85DnRqyHibLe4/Q8ZotLFh0WPFl8dlLzG6'
        b'Df48oKTh3SKz+PLT6aXM4oxvWWaeZuFzNrn4Ujr9QyZvyCoeXj7rZ3RgY1K6F/OuLo6Bl1GqCIv48m9LipkyGLmvR3yblRE0Ltbw87njBPM+eDO4+f6CeQkN707ze/30'
        b'G6tjjVteqn9O//7uEn7uimkD/WTGFumraUmXtvqd+FL3wpig0annJxTP+pvsd/f6XvuauVC3eXPim69UKXL1OVHtk5f86+djZUWtx3/3j2en/iXov6bPm5un/mFQ67HM'
        b'P432Ol386GucHjVxSnQWu+gdw6BbASsUS6b3LfylbMZYdYHmsyGynRe2bgrMGDKi5NFXOxYnjzhnSDmQ+GVvVOD3eca9tf9MOFAxpXVJv8WWxC/Dlk9e/Oh4/rmtReEv'
        b'1ez4WnP4u9B3Vn/yhy3tMSOXPe9/5dDHm353qDng+5Uzr51XbzwbMaPt2IGTRzKLfD6f751z5N4n8cPaVqz/zQl8dY+vT9DcXc/+8e/o2y+2+HzeunL/7CEfJqRe2/za'
        b'AZ+YlcumV445e/hl6a+L+48r7v2za5W/uVZxc+Srz5wrzhz772k31j7wHnD7ZPa/dh56O0ixd9yfUuPn/sKwUfeg8J+PgtInpq35YNUrwkDPG0GXPl8T8Pn4L75T3bYM'
        b'amzPffWbP1xdMyX/7yFXL6qe37h3wqeYu3S0WvWBn3ZnwfJ/XnhnaeK6bx76xn9c827RZZWcKk2+DL7sXH47Hd0VPQ7zMkSPwxV8dVEkrpKhbbFkN60Wdh6+g8Vlu2j/'
        b'M6g8MjE6KTpCLWF6TfeScvg2OmcUXQmnStB+IpbQ3jTRx0rF0tLVjqzoPK4DnpGagE4LSbiRkRZwg0cbRHd6ywB0LTJGlSjuMyhhfHHZgnV8Ebo1n3px9FPRpkg3/8x6'
        b'tEd00UThk+Ka45psdNyMzqwt6rLpCY/O56JrP3KaUOX342MonlqVlDtlJRW0eW6C1itEYAM5Px9O4Vzv6+NY0E/i4YPhvz/bD+ReP06g+7AoyBIn1p8PBOGsYLlHHCd/'
        b'JPACDeMing/ukRevgLwC9YAI368LfbzgFhVRCV2+0C5zmJbtEmovukns/30xGCi7ZNGXuE6i0SXoyaZFfboK+ogvehD0RM/EdrxjaDdRjy6hsh7FvYRBdgSK360FRuoc'
        b'xwci8XY6qeXyBju8JQmSInyHiUWXJPi0gJpocAHakd+3YxYvrg8NUvfDlfyANaGUEX6VQ7cJUN720Hg1lTq4o46jGwrkeUzXeF3S5osvj02TEde0pm+MJnlFykDG4KV9'
        b'S2J+Hr708v/NmLoUn03TvOYslW7RMhtHvOy5lm38JM37Oem399OWjx/2p9/OKFr50rW1Cf/+xz96f/QbTz+prfn18VqsWvrm9fvbIg9+vSPo1mcLFqXP+MMX3O+mfamN'
        b'VBt2RL3w9osTb7y/7B+D1fs0h+9WfKcdPu2L95fdbhq5t3b4zfKy/LVDTn448MV/HM+MeH/Yw8Yzb/sUpKtO/HLML+5eMe5902iJujfgUcDnvt98Fmv5T51KJm6Ntgtv'
        b'6tVtn1uyyy26hY8J+BwveidVaBOZGaxD+9d3eC5XysWwp8MeE9wHiIRdJpM5w4NCgLUoWiF6Zs/KUINbKhtqUwNr8I/g0YmFy6lzNa4XqqApNk10DSDjg87ys4YAY6CD'
        b'V60pRbWxqA7vjFZH45pklZTx7cdnohN4h4XuJ4r2m1BtKqg1RMVx7YvVF20VwGY4iJ7HzfiC02AM/H/OF56aazhJl3KNKDeuIQTIWY4bxnrNocGb4hJIjqwLItvN+BBO'
        b'8W/TVldp9aQdvf+vAW9yETap+Xu2C2GP/f4xe9b1w2fROQdhz0gjMQK+Y/kctDerxzlr8s/sxXaENOnYJbyOWyLo+CUSnbBECn8y+JPnMks84Fexg98h6CT14q5iJG5A'
        b'0El1MrrcxlPvpZPrPDYzOoXOs55b4g3PXvTZmz77wLMPffalz77w7Eefe9FnPyiR+kahTH9d783yJb1ctbGu2gJ0fWht/vBNTv7rAuvJDmNkx70gXTD91ruHbyG6UPot'
        b'wPHcV9cPaujjeOqvGwBPgTqBLuIb2O6TLDL1FK1Rm6s3fSzr6lsl/r/OaZQ0BKRToiflMJiJo496W3UlRm2hgfhcS5RanY54A036wqLVejfnYufCIRMkIh5+h/NS9By6'
        b'nJI0R4xyXoFea9YrjUUW4nDVWmhiq5nsid7Jj2gmSZR6I/Ey6pRZJUrHwtIYh2tYm20xrNZaSMHFRUbqKdaTGo0FJZ3diwvMoscZqtKa3Jyk1JW8RltC367Wmww5BnhL'
        b'GmnRQ6OhTL02O+8x/l9HLzhqjaGdaTFpjeYcPXFX67QWLQGywFBosIgdCs3s3EBjTpGpkG7vp1yTZ8jO6+rvthoNUDhAYtDpjRZDTomjp0DWdyroYf88i6XYPDE2Vlts'
        b'iFlZVGQ0mGN0+ljHnuIPhzk/58BgZmmz87unicnONajJjgTFgDFriky6x/uEyNQ64L4grkRzLn0r5ah39MleoTwV/7Cyu/vZaLAYtAWGdXoY125IaTRbtMbsrhME5J/D'
        b'Be6EWvSCw4Mh1wh9OH1egutTd5f3U+xtKVXTxTWj0ZaeFqw5VtdE4F0d69XipOL+jNfwwYmiNjI5VdRHwuOjYmJwI9kkdyzaLV2PzheqWDr3n43aksl+wmgbvpsaTdZ3'
        b'1KeyjD/az+PyLHzC4LO4kDOTRdjyRSqyqC08i1yj/vClJt6xJCMmMFybqOUuhgTFrYmL1S174UJTy/brFarayxXhwdcrRtRGV17f3VoRdvCZykF07cX6fb02rC8Dy4EA'
        b'SzbTIbuouctudAftc8nvIlSDD4jr28onoK0kZSfRjDeN42eloEoqv2MW+3mCCqZyaRF9kB1X4v2CHN3tT40KdAAdTo/EDfGjBYbHN9E+dIg14q2oVbQbKvAeVEn6A/rC'
        b'C+1n6bZaqPwZvI9OG+PnObI7elK0DAyZSoCmgU2KWi7GB+1BbQtpwSPHjETbeEa2joVcJuqAQ9s3htI2VqVsRIeTpQyogyy+HoJOPjEozl3RzzQAqmZmdgnyoaq+F91G'
        b'EYRzILsuqDMOxzjziTq5GC1tIpshPmkhRSsnJusIi94Dl02c02td7vwf8O8e4gYfB8bjV4ARldbGrHSuAVORiGbn/FUrK4LReTWYiZywsZVzbFAqZbpV6lws9jDksRNj'
        b'UA2vK8p+KrByRbDkmQ6LxrT/MTDtAHhMB+DmYYDb5Jhzji3mqSrLcVZG2K5BZ35sZbtdlUWRypyqXQ9zcdkFBmDn0Wbg6qqnA8LRYs9M/dpig4lKjMfCsc8FxxACR0cO'
        b'IpK6dnzn6p1snu4eSNm8Y6tUu8SNzT+d87/HPdx6jPUmRDQsE7Wl43qBBiYdRpcZ1DgJXxJ3Kj8VgPeiUyzeHckwpUwp2o8OiVumNxk9cW0C1e77xIwSgE3UcomGAYb3'
        b'Xs6QmJcyJGj1P/1rX+1VFufFhw3vZyh7OW8Qn7wyfoVt2ZYPVcNi//THvDGto2/dmvCWNmP8v7ZnrLzy2fhjrVnXZd7h6/+TfTT6ykTppMKIE7VZ516dkL9k75QH23r/'
        b'/l+MX1CI8LC3SkHtpkx8CwzUDsa5MdHd7ClC59FpyvEiYicTJ2sCri9AjcT1j29yqBqfX0PZVm98Cp0UZwbkA50TAwV4u+hjacNVaIfDh5JjYwQ1i87jcjFOZogvOilO'
        b'GuA6XofsoneGwY2inXQQ/u938Dx0CB13MT3tXFp28Cy8Nwk3xKITAq5fwQhjWXQLXXBEkUDDKlbTzbTxTlRFQ2zIbtoLvOlXf2C8+xx7H6aNS3DsfViKL1LXDYvLfekm'
        b'7PG4ug8+Rzg5EWineLwFX8C1nbZRe0q+qzdmm0qKLZTvUrOjg+8OUtD9YETnCZ2s68b2HLnd16o83XaJjk1sO7gv2S/xQA/ct6eo7ceB8X+mXOX0qFzNzNMac/VizIVT'
        b'HXIygi6qFmhMT6tlGfVrnla54pieFssKwNPE6Jbd+Cg+L0p8XJnUWQHCm4oMF0teFMwFhIF8ubXP64MCUVzArLf3/idznyLwnv+NXQr1gpQM4Rj3zsnBUrZg0AcGfP3z'
        b'D4YHvhKx+8BHw2J37Jw3//rMptxJ393882/3lOKgF/t7/K7fnMmfVP3jn0O/GXc1wPRrn92KEd9WH1JmZqHNH1u5744ELqvpq/KgLo/RuKK3qKugc/gy0VdY41hQKoiq'
        b'k4Pa0A1Um0pW5aKTUeFszijGB9fzetyCDohOkVO4cpiTEgaizZ0oYTt6nlaxfia6impjQalk41YyQiyLLuLn8G3KYUYtGUACQs/grSTWLBXVx3aokXG4WTphahwNs/Nc'
        b'hq+KSlEmvssRnQg/HyROPG4ah2861CmHLlUD/8s1elr5BHSXdahMVF/Kn473odY5lIHgqiwCGeUfyfgS2uzkH+hQ0I+nYd9sioeZTqTpQYVSjPShEWD9vg/l1g3oQj1d'
        b'sosl730s6Zr2uWj2BFxO9ECz7/VAs0+oVcW3S/OKzBaDrt0DqMJiJFpBu1TUDrqtoOpM14JzgYOLrgUaTPVUK6c+nsF2MfjJv+k6HTGYCC26qRmisekS8o8laLEhIjnH'
        b'w33CLCdbyNIa87sTtYsPONot5pwnPkLm8CSrEUzV6IRZPUQYuUUrOXMSw5xk6xSdpOoJXpPeYjUZzROVmgyTVa8hQUbiNg+6KKVmjrbALL7TFsBLXQloPUT5Mlp+El/i'
        b'1YYXN5/mzcSb3Vr+0VeaFS+8de/9e+/eu9B0fVdLRUvFhNq2vW2Hru5q2zKidkpq65aWxkH7y6sHVZZL5M/tDQnZFOIVUqP/eUhIyLQ4/6r0sqz9XzDJb3ovXGhU8WLQ'
        b'7GZU1wc9j866sw6RcRhFjQDfmUGOoKIsARgCKsdVwBTYUrq+de1IbE9KTkDVqSm4Jnn+oBjUEEtjUFWoToLObETNP542fbQ6XaY+y5BtpoouJU3/TqTpM5NMQAz9fl3/'
        b'LgTSOado30hFgUkWRptOksupzrLW/dQFwS3ZKldaSrdn4HK5B7rtYa/TJ4D1f0aZuUCZc3uizDTqKwPiNIrYSALq3EjUzUv2/z8iJdkS0lOVon/LIrrDqO2RYzBqC5Q6'
        b'fYG+exTg05PnW+mzBUqe0X5Lf4A8uXVAoE9BntFM8lfe5kubgTyJaqtNWtCJMBNTKWkOFAPHLfhQqEiZ+DA+yoriegpqErejb0J30dXIRFyP62OTUD2lUEKfK0QKnYoa'
        b'ZP4F/X88ffYSXa9PINE0B4l20epiumUWSz7bhRRN51yU1waXF3ugvOs9UN4Ta3vC2TSsnXE7m+bptggHsnuY1QPNUQSkxGG0FmYBnQHOubmrO5zA2VaTCQREQYmbpf5T'
        b'0XFKw4c83Rvs7ZkryPE355taKCKOcJMTPaCh8iwgYthrbohoYN7/vedpn/6AiNTZdgU3omYRF/FBwV1OrEVbqfZmxjUD3OTEadwM2DgoxkKXC22bii4S8w4M0zWAl9Uu'
        b'bBSjxKei6zIlOotvdjmYqEf8yy6yGi1uY2ruAf/kSx6Df90yO0MkVz1WLIj+DYqLF+HyTndc9Dn5FLjYreb/A1wkHm3jY3GxI4L6qfFQGR5BFDqDUbl6bMzoiB7Y9NPh'
        b'JVtvFChebn7t2yfgZfLRLgyyE16GMO9/7nl21CnAS2IWLMN3Uh0cUo2PuGFlGNpEsbJoMLqFajPxTidiEovmqlZ0Nl+bgI6KZ+t1xsgRMsDJ8cguRRcHpDwFSvqRfn0S'
        b'RmY5MHJgF7zomlcs99LjkfAKXH7TAxIe7mlPsidUpgrqulhblpmpK8rOzGwXMq2mgnZvcs10zta0e7pWzxh0pudIpmZyIedCmo4wDo9wu7zYVFSsN1lK2uVOtyqNymiX'
        b'OVyX7Qo39yFxY1C7iCpZlN9TQqMNFd0kP2HTETdf5Da4FHKOTRPljMAJngLb8V/OBbCct5TlSKfxPf/6C3LPANbLy4/18vFjfXz85fTwSNSIzso7gjfwZXxiQQoYx2Dg'
        b'ckw4KpdsxLfGdZvcIXQ/zYkhneeWqaubb+/tWI/iGD26T/ND5ey1ZP9I4j/NJotNTEaiyLkpbmqwPjuPpumqqye6+GfvwuVTzrWkHvqEtdJTbw6xw+lOR89kiztMnHc2'
        b'zjmHkqiQoUZ8Bl20ku12x6Nm/x5ipR8fKZ2BT3cKlsY7UEU3Tujp5CFkxByLDpjOx4127HD7lMsPum0/Syrq7gb2Uqt4GkwTVOzJrPUnc13Kgj3stbE0BDVznBiC2jS1'
        b'n9cHi5MmDmIKSEjxwahnJF8EX8/9fnZf1fX8eZknB57Iv7F4U/g+9cvjRz9bH3Ug9cykoxOX938n4nDWf6Mepmz0/kNf79JbC86Hb545JvFzdcn0jwdIc6aODRh/bUTl'
        b'6J+Vrk4ZH7YxvPek8AVrp14RMv2PFp8bmJX5G8Ml2eAFRzT68Yn5r3v8KeGZSO+gvMUmSdngP8xarfjSvLo4POiD2Sc9Q7xvbPwebIsTY9+U0cBeZO8b7/RPj8I7jQ4H'
        b'dTraTFtaI3MedRyy7J/THUtiRxh6kwNumDgf86pG6UDx5Ud5gUwUOf94Q8qYgrXDxbWvmlJ0GdemRMeQY2SdW7vhxiQZmUcrwdWz0U6JDJ8KA2NzmAduQW2OQGhdpuNM'
        b'lLGXZb9cuESsYYkYwuQXN2xJ6C9n8+KurV9EvfGXiGxKOWz+x4YpXBRvtsPjHz56Jqy+zQcrvWb9Ys/meVbfE0nft969f2bpu712/fLefz2/eydY/80XHz67ZkafG+Ff'
        b'nbn+6dnfDjK+dei9IHlu1cbm+WHL/3JlZ98+28I+/lPj53Zd4d/HfJ7oP3RoxvGz1+YsqjV+mPewYnX4X86v2PfRsfkfBM7Y8mH0820l2pwDhWE+uXWvxr74kceu5mGb'
        b'W/JUAlXHZ6G6JOcRPIvxDocfOmMgdZ7NmoBPdo1qQsc5znl8dw1uENdz1o5hIqPJcaikD1ehixLGE98gq0W341t00hFtW5YfiWsiomPYzDyyvo6bMBu3dg92/6kb6rpv'
        b'JWAyazt5u4nN3yHSBIuC+rmJp9uPU1JGSu5N95zFkJPBSfiBm2L1U8FqZU3Yxb1IBX/uLgKVPWzKRN26RfhkZGSEGtW5bCkl3sUyfdEBAZ3CFR7dGFDn/Ya6MSDXfkM/'
        b'eV+MnuegFE7mczXFkwkH4guQKwuC++1cTpnPxkhH/PvYt/p9sLg810dkPnOG/T9gPqGKfr9dPGPJp1NuDtufNjWjetB3U/835hPvkyoVY9j7Uu6SFy5ovD5PnyGS+cwA'
        b'yl3GP/TR2Oq9UxgT0X3plxdCKVdYXDldk/xgQ5j4snYM5Qrz3o7UeH3DTheXK0wHTe62i62JPG3A+kR8ZLbh1O5hEjPZtPnvU/pHv9bmjeO8hBeOr7jwydgD9xdcqFyk'
        b'/O0Rc+GiGWW/CPzmWAszbuh331omDar68E5GyL/Ljks/3zTu2+Of90m86hUz9cW3fulnXvmgruDGmZoB/6z+yHh89jv9PlW8dvj08f+GPbr/j9DSs3uuTo14vn+CbbuK'
        b'FafJDkwOSHKeQi5fzk3F+/XoOt7aSZH8yRsLUZrU6TtocmgnmgSqlMnJuQOUGgldeonhuazpJVdB6CdA8KKL+F5yEAk9qqOD+Jjyfv/pgfxoqOUevA3tEAkwIYXS39y+'
        b'QH4aAbWkZXZboEj+6F6p8UCWVRJxT3gb28wQomvhSjl6z+sEuOctLPk+i1m+aRlXKpSSfeMlVYyFoyfgjFkns0maeZ2khS2VLGKM+WS39pLR4ulA9As5N0jyLGNcsQYI'
        b'1rSN5iY5F9h40wxIIWkRTwiS0iMXvKEOaamsirXJyK7yOlk9pLdJJ5Nzf56heSWQ1wx5NeSAA4BbAvBJKHwkr7xbXjnk1RkH0rxSerbP0+crq5KKaeGZsZFDFALEHfTp'
        b'eTstNkbnEQJcxXHEq0INvFivL55jIjwt46HEasmJHm8i2+8BZr5MRpZ8MJHN4E1ErqtkJhI+3u6hN1oL9SZywMJc8iwle6Tr9O1eC4wGckO1UzHvTBGxOrbm7CiW7l5P'
        b'V14tIheyKWw7u/JHrn9v9yJHm5hHiquCyaFQdLcmOS+u1fdxHPMBv98L9NgPsqQsgBzuwbnfi3fiqQxyp4zoj+pWi8eej40g+xXQlQDKAciOtwm4beC4buERrh3LCdHb'
        b'gIvr2HSGHM1Eh4CrEM+z4NW0M02TnA0huxibH2NIetPmZVqKMguKjLmjeId+TqLufVgrofRpBlwzAZeLgIK1iqvFnSWJvsUMQ5WSkilct8N1XNFkoymkOjafNUmJsaHj'
        b'beRIJFYnNDPksB2AWxLItLA2Noghso28oZEnUkcrCJt+yIWtpWvOvuDE5kjW5RgKClRcO2tsZ/Me1zTSItIy2sSJvHMbQl48U0XOUoNq8Epc54ftxCiHFpHzsavJZrbi'
        b'YfTDBkhK0HV04AlrlNke1yg/nQOlx4N1XcW7LRTtWHT3i4xVzH1oyCyLZs6y3jrxZdqMlwAVmPA/qzUeeHWq+DIxg+4co9QN1XjVjxjEGNCSUAk9fSP0V+u+0iwnXpHt'
        b'lytaKy7vfbty0MIru1q2tFS01LXFX6qwstneMxWfzjim/tWMhtAtkmTPkJoFgw73z1wc1f/1MV5v1KmS/af5H+bCX5aPDKt81iv8StmESv2g7Dg+N5SJSQuJx3bQUun6'
        b'my14p6dzRbO/Bu3jonEzPkK9Kf2Wou2RiY6j7sCaO+E47g5tR7togkx0eAzd7aQ6GTdGsehwOqQ4xeGzvliM1AiJQWfRqURiQOJqstXIPrRrAzd49agfvya6V2GRbsI4'
        b'8QCJTJ0h19BTwAWzUZ7gRQPdxPMqAlnTe65iqp+mwhpnhTTjzJ7kWmAPrmYrMbRR01ToDlyfr0hFbaPJNqz0TB9yUKzYQWAeH5duGIsrH888iFIssgwi31rE80E4dbtE'
        b'a842GEDrfZVxSt+hnTtIlqdfW2DIKUnhHfFuPjw9rRcfRM34IJ3pp9sQ4eYMdEoAM6KSwzfw2S7mdidgCOMmR6ZQEaggJw0RkEodAFIxwqlNv2KoOj7HCdgP7UbmYTU6'
        b'wEwjYNIjX3gSIGMVT1fHzw+KxPUdwBJIe2f4SXl8YMqgH91rFDTTrx/XYx5ZY0eLZ2Q9CyWZPoB3VJP0Uj2bNHJUgsN2kzC+gxYq+Ul4b5dDRX9iV5nan6qjADZRsK4g'
        b'sP3WCdsGdCiEAOdUKH3wWW+BHxGL6roFzLkOeyMb+OlYYOtEV2JMfSyE6fMVHGgSTCkvHv9k44LoYVJmqY0rDrWx5DAm8TAQdfvQuBEjR40eM3bc+AnTZ8ycNXvO3PiE'
        b'xKTkFHXqvPlp6RkLFi5a/OwSUQTQHqbaAguKgWE1EK1KaJeKUx7tkuw8rcncLiUbb4waK+oAHl3bPWqsOCZ63nFIC11kJp7X9ciLp4ukeq/HFUkjxyZ1DFEQqlnPT0R1'
        b'uP7xY+TlwBKdeABRDhmR+87qgSN90iOOjBorjkMR7zhQQMHTjcqAD16QECA6huIIGCAX+biV6Ozjt5OkJ2CzrhOwAaCn2kKym7uKYXo6JEVQU0403yfHud4a71yQ4jEf'
        b'X0bn0/DlqH7ocpo3auCYcHxNKCzAmwx3cl8TzIT40vN+/6nugWYxiB0tmw3CZeXrL2ukb1qY8DJhCpOq4ihHD8CH0LnI6L5RCbgB18bKGI9RHGrBDQtohLR5Ib5JFlbO'
        b'Qrvd1lbyRTa87XEnWBvMRZkWQ6HebNEWFruOf3duveSYPiwxfe7KtoV5nOOdJrL0xLK9qnpg2UTBmI22olOoAd8lW4Q1UAUDoI6OScB10QwzzCTZiI7Om9MtKq6zQ5J3'
        b'RMW5uSNhhD1/ZFxqtxEmOoJvtxHupRbPCNoHUFckgextwHUCIw3lUO0wRTCqF4+j1gQqRnOLyUYB/fbGZIqnXcehC7ht1EjUNjKOGczI1Cw6juvRc1OWiOsOW5fjnfD1'
        b'ykh0WYDPaDfbDzrnCt6CjtBNnNABvClR3JOAWYl2xQzHt8V9ABYFT6nkNWSXgX6HldmibpMyOlxYBcwYXg6uz4wWdzVQRuE76CJHtvvDFyZPQoeDxSXkBnniGl5JtymY'
        b'nJwuFvDXMMnQEpbuahD1fnEiYA49Unnj6JykBHQ6SsoIeNOsfiy6gJ7vSzNcDpyu/Bex44o1/mlDjGIpwSumxGSz35Hl+v61/oPFl2vzZYNbOLqLQpRq/ELG8NxLt1nz'
        b'O/Bl1xVhtvqNRH6616Ntez/4ouFykG/hR/j5oo+nC43T783wPaXc+fpL0+P7lG75cNyYo0f97/h99yjr92EKo/bVmpZvzp8fOSPvcGlbXNQZ+eapJfWlH6x+c6tQ3dta'
        b'NOm5wpxvDg189pez6vsu2BPZ16No7bWxJy/dHnn2SDD+4L2EKddz5v561uZvj5x9+NKBjQHfhK75aDMOv3V06oOBM34funJ02q4ViZ5/WBqzIa/y84ztr783aPfw/ed+'
        b'VvKnS+8o9ZVjVv7qRElve+wbB29fu9d2Fd8et/G+93/fGaj+7bR3PjuiklInxPoN+KK7EwKouE6P9hZSqpWjanwTHUx26XoOPW856IFERxxnYNxPT+aGoq3/X3tfAh5F'
        b'lTVaW1cv6XRCCFkghLAE04SEXfZ9DYFEFlFAbZJUJyR0OqG6wxI7LhOku0EWFUUQWWUUERQVF8BlqpxRx+X5q/+o7fzjOI7j4DIzjs7g4MI759yqTocE1Pnn/W++9z3y'
        b'UV236tZdzz33nHPPUuTTDxE+qOVVQ3/YUB7uq9+hRb3afcyj20P67gntbC60R4ej2YVkA8z0aBDhKnMuTanECXW8X49MBPrkR7hm/xeINZMbYVPyegARjbp08BBCQah6'
        b'006Icp1h1YzbkJgDW5HMS0If4C8dFNUvi89hPpzJJlL4Sv2jWYXhiyTmqG5Qq7weikvYJv38Z7znCyoGLE3wWoJ1rekM6+Wt6wTrkbu+w+OS9bv0+wtnDRxAauGI+x4f'
        b'PGywxPXjJe127V4LLdhBvfUwUhC9Of1x/f7e+j3uKtMQEv+101ZC2UCEx1iUUeCuMHpgBHlJS0hSM0IW+C/B1mvJ4tIhVybkCQl7edIkNg61I6Iimt+1iizIMOQS1SER'
        b'aS8GfBX3CVAy4z+lsg5MbTwwJlJiFDHWwVjWEBSYSYEKjXixyzvEiyVK5AJ7ClpZ3W1u/Tlcc16lrwE4EKZA1FmQW0b+iDFLU2OjV1Vxh4hJxBHLMSnoXRMEmgKLCNQ2'
        b'e2P2gBf1moIYwXV1rRJcrn6C+UXF2zGCLTTwM7z/NA65zsS23C4a0bFQ/GEjY/1cXjoniU5z2vUbri8s1Tfo0XLGlKADybmwpnsBe7DvCkl/tPiyDkRkfFhxfpGIJCKX'
        b'AyLXSWI3DPwM870XBxo2KEXEgSahnKAOgTkWFAlyiCERA2ZjfNAWEeeSSiiCpxSwGt9DbtgRFYshXzhbMO6qiWvqfcWFE4kcrPXXjF/a55KrC5ZeA9dCN94XD5h41cQJ'
        b'RFSfxsYyWdXzHLF5yI7E5IC3Qq1aHrPUqA1NjTELCorgx9ewGmbmRVqeMRFqiVkbURtM9ccsMJLwgc2s9GI0eiq6j4SvPWbmA6Ih/pFExBbp5AvBFLjiH52pavv7aU+T'
        b'J0btQfRto0XLGR1LbjOt3Ci3dmuurG3X9tS2IzzaHVDup+kAOl1I55ByZ3yGOh7tctQ0vO7l93GBzJCgAGUf4jxosSOovfBKb/qEgNr3wP9p3NX2FuJdoDQxEyaG51b2'
        b'o9yXxnOPZbkpFjjKEHl1DuWYGc9R1j4HhepaBws1xjvOCnl5NDcwmAS8f6c1Eayo9cE6kbw+bz3MiXeV13eRhRhzNqreINqa4pA/Ihq8v1NkbqJSKa5qKt1L59KRpzxH'
        b'ErIS/fi1hQWzi9zETWo3szHnud7a/krtoKUAzfQubO6Noa3bjuQBT3FLRK9EURNhuJdYtol1cp11iQ2eWRSZnlm91jq7YjVTQBlaAcehsbdtiUPpgxEYIZ2kONfZlyTF'
        b'08mKC9JOI0KjRJEbU5RU+Ca53bMuSho8c8WfSEpXJR2epLTL1U3JgGepZOTNLemi9A2LwHGgGbd9SZrSj1K5Si9IdVXy4RsZWpCn9IZ0OsXi6EaT1z+WNB3mxusPTgGG'
        b'rR0smmLEBSbGbZPHUyBgTpHMeyOMb4xvIRg4fQ7+neXHACtQwpERIalazY9PdsL68tB6pUjkgcaKKu8LcTwsNOckNK34/Iyd8oDUVmQokTsHuGVyAjIlFFQbj2g3WFHT'
        b'mflazN7oq6j1e+D1y2YTnEJzt8QmxHN0qFsw607jmN1cg9Vcn4YF3SEhZvHg1kAro1MDOlw3b5iSnVSxOTWxbvy0w/TEq3XS9CAKiMfPO8Sr6MhAtfKd1/S2WZND6MD7'
        b'xKXHvvi00x7AM4kxHVL0w0MZFpI3JCrCCkHtrqCgQRiHoXZh9aziAoMUS0jEX9gFeDx4gSdW9lUGZ+ZVeIxPbQh0bGVn+UExfsBZoXgQTBn58cWVqso4efy1Zy3XDmjJ'
        b'D+DeywKcO4CpVIOB1bWwr+I+bNpXkUt6RDUxvvFC8mkPoBvYmr3k7f7XojF9ph2XQ+jOpwrCDQ6+ObsdICZ+VdbOvaeYOHa5JhjS2AXZKYFAsbhh2ZiGlaKahT2zBJqA'
        b'kkAiwq+YqonYhZgjDvAXOEFQu8P3f8TJpACTQKm2Bxws8b/RyHVtjVSzsaVWLLDC51N78BckqDA09qco0+oJN81dz28OfN0ppqEWYUChCABSREICJEJgXQcAuEmg9vFm'
        b'+zDIeMiUAh7iYxZ/oL6iEZqaF2+qzIIZGNE9Y1Yva8cPUnpWe6MjMtEwhcV470htNacl9oUVf+HBHcy6IsS7IsS7IiR2BYcaOsOGWyhTe/G0jyZ0pBYdKgXdBmCgZ0K1'
        b'D/8D1bfVvpDz74k9SevQE1Z+h0mJC5+QWYpASyMi9KSbiRHUVCROWITwFugNUoi4joOCAUaisa5R7nGWn8QIBGAWsGNIbLLeJXk8QGXVBr31Ho+5V8zlvt/DpJoPX39j'
        b'His5DDoslW/ObLdc2wq/8EwtSwS6rIv1j80VYtn4zPYzZha2QppZ0ZhZKTE3cTRqP94kYXux6aOhwNhNCbMN4xEwm2xOedyL5Q+b8kugHFEy9kI2MujXnDkHaD868aq+'
        b'Jy4rb4hTF7JqOttCbR5PZUODz+NJRkodxQ7N6e0rY6+Jfl/YbjZMPoQkjEj0UcB3rhrJXx4J3F2wy8SDqYtlM2BgvubiJONaQMq1/mAsBUl1xVvlq2Capmg8H2xgZ8fm'
        b'zoCfqQNwtOm8+jxhsKx6McBRF8kAK3KAdA5Y7HPtVwzLNqPTThBI5cU7oRDYKMImiZgknukx0DYNNJNUNWS4Hw37WLSkmN27psrXFKhd5Y0l467mAY4Taw18gY3Mgw76'
        b'A+P79KFzWeRtCSfDjuSDLcLs4iACM7x81bGLahG86CbF8QH2DSiddpsGtqkdNsChiDMmr8Kllo4SUBYAtMAg1jHaRCSAfuDm9+GJOJ/NXSW0WFrkkCUkrOKAz8eVYsnG'
        b'oEpCwM3ua3j8HWe8AZwhI2pfKYdk9hzuuDoJ1TKgphQoz9pig5rlkBVqs4ZsOLQhayYHOcdCTmuLPWRXl4b4wELgTxeH7PBeHMf5hZAdKZZARUgIVCjU+jr4tpZBlGSc'
        b'duMCPWvpi9SW2x5zwsoA3rLWp8B0x6zBBo9SWxUknQfaH2CHCQJsVcbsmBGXUYCoTMYCOXgS/9De46hq8AeYWWCMV/CUBAqN8VWqHYsRqhTmvo5I5E+5C26sGEi+O04d'
        b'6nBIhO/S6SzURes7jda4TKpADopWgNxp+w3Y6MQhIolpIbqFGTPc/Ax3xvmqxNSVk2ZXVDHeMyfPGG/kpxlpgEQIbfs0LrTlEHomTKQW4GUgb8Ae9SIhINgPlgQmxAfD'
        b'tvxcNAbCxtlEQQJ2UBKw23DnElOdqVK6lC6nyelWm8MluaQsCwsuv0HbOiiAMVs3zdU3Fa6cPbBMf0a/ycJlT5JmaEcuW+jmmUu/x/UT2vYEayqdon7CN3P0rYVumRuq'
        b'yAv1J/RHID9irQztuFBqFqvtL4WFmXSdoB/ufx7vaRI7pO6UFkcStUDMxPEbc7hRX7HCa5Asal4nqMpqTOtoyeBXUgV2xHqPdkpvjXdRu0n7CTTGoe0W9I3p2q5Oj5jw'
        b'XwDJ5TgnnEqxG1FFHfhe4DAl4GF55txsiYVZLFaLBs8ro4szyGNVnEoy/NoUl5KyDl2kMfarS8w5ram+fq3R4M6JZtpq0A6GMTKwCfMJ3Cbfxm0yGQRcRZJHSIp5iqlK'
        b'8e3Vwhs8A+yXuMSIEWVg/CmNnQdJeH+cpKJlKLNn53NLaOAw2cSXMp8LCwwWVbfEHv041zZEU/Mq2lR3zooCxcKaMtOcWplvzmhXYTzLhYk24yyUiBEDrMxoJNTnsk5g'
        b'itFiiNU8ntmSySHyzVnn9Tae6cLVT6CpVHjgDGVUSCP6EfC+mhahgUD2HBsGEy2ghFDNJqqqrcHL45pU/RhBTBNJo0ZkU3/+oufrhH/mmkQQQ4UuEtN13p8fTAWR2sGw'
        b'eF2dzaDV4/F5/R7PInMIgeBOP69KynBhSQJ2JsjVmJoFhBIk3GYuRHrhO49nsQkxtk5AlHL8QDpvxgV7R+j8KiTxSpC9O78Wg8Ybz3a/87YUXEvqNJy9GfEtAnU+1dL4'
        b'PkF7wkWmdTJkmiAZh8g2ziHaZKeYKtrsNtEpNlEI9qSJATfibe1IMI7oeS5Xe1I7Pl3St49NvjAOROsPEwduE+vEOmmJxct0ylDWJ3mlOisQcEaKTvkRP9qW2Jh0DnAi'
        b'w5F2krI5mFQjllZeWeetCpKTP2OofqQQCUFATboAyiCkVo1TkoxTktmxth8nQCJc4bqY+GgFVpYCL38w/llu4h91Ot+RKEVwaMAy0Z69ObeTDlwM6cQtEFW4NNuDnMGC'
        b'EUl6BfRIAqZ0bXemBUzoRwzRUUWrIHOL2XvL2pGGljC/Vyb2bzDksbaxgPt4ltfsE0sZx/ptrB3QM9kmbMccJcAmrGH6soS+EPZjrslENjYFDU3aNob4h+A0VTJgRABO'
        b'3gkEIJKBGagC++2FB85gJ5POX5Bz2hF1jNqb0H59tlFqHRrWRpBhOcvaVmUbKeYUs0QiqHL0pxv0R8r1DbPnFqOO2sY5c1ey1XnVLFqfU7R7rX2na5ELL87uCYuTyBE6'
        b'VgQSRWQMdqyH2X0TH01FJ6RzGhpWNDW2O9e0GIDTNb7ejJ0qYh5sEJbvE0dIFkbHS8G1jV51D97a45K5TndS2Ue13iCZFnd4OnSuuc9FWljMPunEqG9+fBWet2zK4UWL'
        b'ZCiP2LhUkbxZaxGt1Z0w1trhNjy4Ut9cMrBYfwzVbfUtxUWQ+/aVmeUOfaf2ABCH559GxUUkWC5s4RyJPFy0vnjGAobweA/PizIiyARyERm52whH9xaD0+XPfjuVfKag'
        b'UXJVUyDYUF/b7FXyfMDQ5tHpvJpX4A2qXi+6cW1og2L3hV3IUvYx6F2C/M6gVXNtjb9BhTrapKZ5FX4lDxlpdIZRoSi1LLxW3gCDESpwD8hjrHd7S+eEJrSvosLna1gd'
        b'IDc3agWGxkJvsv4i0+tLnkGyB9oXB8wWHVeKV86dA+sI+fJYUkIdJJb4sbHhFsLsRyUD1TpsLMgrKsY3oU6Htkff1axt1B/SjwNa04+tmMfpD4+4hOkWbavStmsbtS3s'
        b'rejX1q/l512v39th8cnm4rsmYfEpbSdWcrWFzsrsS0TSkpJhB8RzMhvsjhKdjImKVbEh16DYFQdwBXLC+ZhtiZX2SRutOFfMaayKucD7qGUzOnhOiYMjmh4rwDVFgGLZ'
        b'JbZIceldGrAGfC2qQnI1PJ1RIDMhqNPi8rpeIcF4A3RnNgcMhYQSgpAYGIl3lJayoXSUSUBfmPxPCAnTUOHAAt9ZzDwknxhtynLrBEUGPk5CPo43T2KsKD6fh+uXJHwY'
        b'/ZMRj23PBrch2JjDQ3JsD0rYaRtBisltuLSh3DkkI2xUvdW1azyoZknGFzHBH/hhskEscK9kmBEJgoACoG8dFht590biWCZRdyppu6Tx3fn4IRhNShurk4gqrFyCngia'
        b'd9fAvOzHURZQRsRDGtVQYQSnMgkRagcEsklqJJG8xxkUQhJqEBDfySnSJhzvQlN+tFdCkx51DH0B8MVmBRCS3AqzTSX0hedWwOEzMA97YzwntIRmO60Ce7LSiZoIMDs2'
        b'QLYxywI8Q4qJ0/1KTCrDYOuWRRW+po5HjHFyiR0xonxLEVZxiVYfsM6X4ixdHd85+M6UYMlb5s9MWt3JNRe1H+OqBj+gliBhqECiCgpzZgqFkkS4TZ48jHhdlAQSSjLE'
        b'UwEKOcgEVkhkAIKhbUwMeFfGLA2q4lVR4hlo8gWJuahvE0NdTCvC1b59x01osvHMCa2DdyBcCeQv/juHmIP2N0KaQ/iT1LW5x0V62uEkMi5OnUEwhasWoKJHiwhEGOkS'
        b'kdFXBkIZyefFfWzOpZCo8Kt4XOt7BXxKzwRDSRvZGxS5AknshTm3eap9qBvip1EzhajLcGwr8VL1PURZNbx/06R9mBPeNBoF4Qapw+oxqup0oyXYwvBrCaZvcA1hT5wh'
        b'0hfei+SouA8Vu+EdO3dYhesC70S46xcEzBQSMmB7/glPqhuAwfbxRPLCioH1MRSln36b+QTz4EmsYmF38ARGNYNhL7mMnbwKwNEhnJ3NuNy/wt+w2t+2w+b1yQ/0OStf'
        b'mx/Ag1lZHYpD1o3Aj+Ey9Qri2zmDxjVFLgRpizuyF7Fkjx+1ndAfNxTwXziwaAXNDLdSeXackYFoSkjjm7u3H97ETztgqLjcrZpLPPYkyEEiBskZgd3VAlnFNJoMgzzE'
        b'QvgFGRaG5JBEuL9bUGJnXXWwL6Akez8/nzP3AFOWJ6sreANMVAUvtB7prAf4dnRyD5S5NUEQZTNlzuqlmLQzKTP0KGF5di4g9kH+T0xQxJFyiJLAxiy3IyI3qhbLYDnY'
        b'O2XVlXjDqQu+9vzADyJX2niERfD1LpNcsXEZUmq31F42e4aLqa7t4avb5LL6sbn6zei1Kjezt7Ze0k5q92rbO3Wajv8olmacOEkhttwkSlhEA5MkwTfnkyPISRjECCnp'
        b'oACTHVumxmxzGqpWzKj1ectUZBPaESTtVCVmc0yUy3jOgCMoKDwtQcZVC/SODkQzUHYJwAVXC0kwZZJmWtE0z2OLHxae7YqRivOUBq8RiwAJzLPW/EAxagTihN3I0dlw'
        b'APPR+opZKyoDqJYQs5HWoFKrxqyoed/QFIxZPPUUgYcCIMesHswB5HWCvkRMwhxqUyfsOQLDtyZc4UrE0JQy/Tn45i7mIHUuB0X05jDHCV2zMCVSFACi0aGda7ZFcOEB'
        b'QkJEfQXnH0JWu5N5QFQ815wfguWlCCtENfcn+JWsFlwBvDeisetIG80oj18hqUODMI447vDMpkisPDOv38F+V/Or8VSORn4Bt9JG2ksLT3chBFfV0ORTaMQrqigcQh6O'
        b'1Ec7d+C/QxPddmACYUhpmGKW+hUwyGoQ763lC4idj1m8qgp4aA0+dM5v8mN2403A5/U2GhgwZoXNh4qqu+CCjklYudVieGJAc1eBzF7p3I4sZsiW8gbhH7Jd4oUvmpPj'
        b'c4FfXthShhmG1gGqppFA2OXNOVAzYT4kcz7O0/fDvdNCnWNAY6kNxIfAotbjPUmozueHm/zYoCyLsf5ZLBmgNL+VhOaUeKNZru+jvBhNqbT5SFfDFxKmo3cjL2C5XItJ'
        b'bPHNqQnwSi8vPEwDEupDgDWk1wKTXtMhBAyTYXJNgn1JXYdtWWUOkLo63rTzDY88HkDGKJPtbTGNY4n6lklBI6GRRrYOGtH4H42rifqi2UwyRYY4PEwnFA9jeXP2SJtn'
        b'Nc1Vla8BCEUcOFNDRvJ411R1IloG1ANrusASPwNBJsHZft2zPCg0QTx5ge2ERoamKoKXKF5u/iFC3wbI9I+4LJ9zSS6HswsKfp1W8jegrdMPBdAtU7m+eZW+UTuQSnHO'
        b'k+tExwT98Q77htX4JVPcuEQJldUlYFfjUiVUAV0iKalhFt9HDMthW7VMAl477B9dGINLEXrw4MsOewnz4YbHX4ms7Tp3Wkyacdm0GR3wYpwkQeW1IGcQE7BrABEhMEbS'
        b'nEH4hbZFhDoJDbYpDVgxKLOUsYdwprpN0mVrscKheavyA2eTIWHEO4ekKaFknrvQV2ljRY035gx4g55GtUFpqgK2wIlfexZNn7+gpLwsloTvyOktYLEkj8cICe7xMPV2'
        b'D4aTMQm7uC+Ai00o1j3MhPoM0utFpNacjNV2zmNeSGBtnMmc7bIAWpJXX+Enf5/ohAYRw+1t8M3cyZxPbWLP4n0YA00isXZzGjWk3cuyds2xcAly590Js4erD52mhwQm'
        b'IasT1EERYG3xDhXhgTUVgZ0FSqCVqc3TfYsIhL6YyaF+Nj0F2mCvzHRFiDTl1TkRIDIVS6uwxQXEqbTXGhLY/qYAGElcq8iUyIZwgZmreSbLXszFFctkZpv6BWl95Ocv'
        b'mH7Z5LwvcAiYCuUa1VvtIBo/JqyuNEAkJgPl0NgUpFGMWZSm+sYAswJGcKVD1ZhlNWo+GAJShvFonOkToXr5DzcAV+/Cox2LoZboIirDSWDhJJ01lGw5zgE9+x1sGUk0'
        b'P6x5Mfssr2+VN1hbVaFOxILIUBUnqMoUX+E/NMqJu/lB9i5EdAMwADzNGRL4pAIO8yEa643Gn+6BqQKiX8Q3ET5oAQbTks6hMix66mDpHixtU+QWu2JtcTAhREsSwEIS'
        b'Kc0GW5zAOjizuZbkkF2tNPOFkmGmbbDvzlHsLcn+FEo7IL1USWpxxOu2Yd0rR7VvS8gZAto1i1vBqX4sW3FmctlcYwOU5Aq51B1KcsgFbOGOkMuoY2PIqd6IJxsGToGy'
        b'FFfIimUpYovd76KcWPsOfIsq6qwmfItKM4o1ZAklhxxAMdjr8JpU51S6bAI+MeRQH8Bc0EaZFmVa2Wk0VzmNI7/wNM72R+GMd149s+BvE2eQuOSsOH78eJqumOgBbMIv'
        b'ZGwmnxfjp8SsUxua1FpARnyJW4hZ/N7VnjXsZ607mZkYOEgN2Ffr9wYYkqqvUGtq/YFYV0xUNAUbCLl5KgF3rYjZ8GF1gx+oYbWhya+wk5etCKlSldfni0lXXtYQiElz'
        b'ps9YGJMW033Z9CsXulMYdJPugEQFSGTcYwkE1wI1nYQN8Cz31tYsh6JZaxyYweOD5niNe2CGoQqL6oVWxORKJn6x+5vqPfQFU1eW8B6eetcE6fH3xtlOYmqopFw+BxcP'
        b'8ogs1qeTKKxU5vPQ8HwiGTI+ZumG3lNyyGEQk1vIdEjOlpp8Dn0EkgwjlRZbQkWdCmpoH1vDtV9XdJLmokN+5IvyFSHKob1WUCS+C/dYGwp1Wg1XJNlo68IrcojPYEqX'
        b'kmJFLBe0GEJWuR2jLRrCVhuJK+xnu0+pUNGUO29YQ/VoJvcnfxKBpnq1C8zz2cIfYuleVJzXb1Bhfgd6K64ChxZAZIFmbYG+MEGCYXtWY4r9JnNt1mdjO+Gp0Oys2aRK'
        b'M7jmXjTI2PhhozuzOjuNJZ2VBuQHBtDaKQP++2POkOyhOZNCavAxEfoacxGk1wJ/X9Xga1ANbM4KN3k+OvZr260TnVXx6gfxdr4MnwYtJu0lpJNZJIq3+vAGFmbFsiN/'
        b'Sd1Dcm4TDat7+QuSg9t5A+mrz/FGRQnShR/prqpNzrAJyhlkicsZUiWbNUtKd2UUULgf/X7tpBJIalwpcoK+U3tKO8r3XtYTNQDjlEEZkcllZWWoFidSVHH9ePlEZieZ'
        b'om3srYWvxZdka/xlkzB4LI93ywa+uXwKV3tZdLwlsBWIuz57Pp27sHZB18Xpn+WXrs74+/itewv+9Ms0KT065BZbWvJGvvQl7x9idb+uuapmzNneh06M7PVVylflH516'
        b'/vB/7B8VfO/aP13X/b0+S4sl1+ihycGD0s0v5A4e0LRszi+ffeL3N+5+QGw5xHcdKs755fRlsx3PPjpQOHmP49M7Ll+25WXhWq/49iXbb/z2YTlna8tv9+6yul50NF7p'
        b'52feY8u5/cNn106IvfjX4e/9/Ossb+yaGqlh8alNb0x7d8WSfdMX//L4kTv+69HPx5U8/+UjXZf8dtNf1vz29ZU7664tOnnbvMee/WnX4PxntpTKu7KL1aLIa8Pvfv1X'
        b'/ENl2tObXngjOOOdnf7lb0xctiow6KO1tyRF3Ct3HL7qgzF/ttSOmfnRuxP2X/uzb7affPaEq2zHJ5NvLn5t+mefOI68tr78wyf2fzBza8WuM63S1fuzL7c/oPz8d1nl'
        b'+1rHDfoitWZNjy/ODi8N1G/5g3L/h6sqd35Qu2hI5PVxH77/0ktDvhr3Tt2V4UuLImfeOFa0uXXB7+469erjawsjb3iXPJfx9QsfO2862u/gT6//+Kui0s8Otr5S3POJ'
        b'9D6vzvz94t0fTMh99rn8L+fP2D33y12jd/a4+8wbQ6+e90ZF6S2vHbmv+fku25977OhfR+SKgcwvrj7YLfjE6+rgfQ+uCW5a9G7GkeuCS4p9KwcEG0tbbhl+5i8PvPP5'
        b'4BO/ea7l1uDdG6qnVq3fPmVTrh777dxP/yjfvnnUK/f95viJK3/z6/s3v/NS8I3f//FX301e1Hz1gQ3H/r58RfSSZU9N/+QXY5zTC0Z02+oVn3pueat/xdXPDT/nHH68'
        b'5HI9983HAksuL/6vfSd/MWHfZ/f+7Mh/3HHs4PHPtr3vf2PzsXu33b3q9O7Xh3783IgHb3h7zGc77OOP/GVt8ET5maaRE758780Nuz/4x7kRJ35x5qFz1i8vu/rQjtd2'
        b'PKMv+LDnm6FpW175263VVdOfFr/u2lzXfPqtLhNTh2xYcv1re2Z+8+ry5R/EXCdP/eWTFbZxfZrXl0687ab1hwd98jv3FH78xIfGjn6x54zPc7tuvybn7Yn1S//z5Yqj'
        b'2998zbPnwCOx+68Nfr7hmr5vrTjS/d01aVfd+FHyUzd9dGRh95Url3b5qmtsz6Sjq7/MffrMfR8ccu089N6YO7e9qC+/s27xicd2PhD97ushky2zX/m838K/3vjd0LEl'
        b'4drRk69/cPlPd1+6/28LF521ftG3ZcrBcvXQ+4dn/7FP5Z0fr3h3+p49p5OyPG9KL7zlPTVveWj99sEfJvv8dx9+7U9XnJX/MHJxXb85xd+8d/vA74R+1S/Gjn2TeY4f'
        b'9sKjv/75OndSsDeHkan0U/pR9F9aot08aNZAPYoRpdbrN+jHRe3RTD3KItc8s0LbT0EUy+xaa9EANH0/Lmh3zLqWmb1vu1a7I6AdOS86+OJBovaQdrKO5blXu0nf2l7X'
        b'tNsYQ9N07wgWZzyqP9yDHdLa0VQbA9SiG/8Fokd7UL8hiGKaQn3ftMKyIjIiNYrCezzH1zYzV2DsJD80RtvsdEjaVugDfujQbtLuSqi/ZG7pQH2TWzs1pKMWwPWlDkSN'
        b'h4KoUXtJNlTeqa7GNaPbdDVGplEtuWu07YFiCh25pekiegar9Z36fn29XXusOI1iiWg/0aI9OxX5loQk7WSJ/gwLA3+bFtYPxDG2vkd/iO+t3ajfAlTZj9ohLnpxj/oX'
        b'Fvb/1MXdm23k/+4XU1rla6hQzBiZPGpJycvQQYLM//A/6Q+uni476pQLIv5P4wU7EMvWdF5Ig/uuBbxwWXdeyBCABupXmDPW1SPLIk0ShCz+Ul7w9eeFJuBXbXi43o8X'
        b'UgU+j645vNALdbYEC12tWVAqSnMFUUA3hZb2905esLEn+L8PL+QIfAYvOOm9i66p/Xlng0Tm0III7ZOgxN65kDOLd1qdVFYub3PhL7RpqcBDm4cL/ADeWaa+Ej95W///'
        b'of9ilzaCHYdsGWe4YGjuxPk+OY1K1rZ3I80aQMzlc7Rogb5J22LlXNliz7oJtU/m77UE+gJwXtH9fxXd+uL8dyelrq8Z+OIdV5z686Xyy65f+H7iC4+bWnwoZ8HV/W4Z'
        b'kTlFfXj0cwu/fePxccKp2iVdZ1/+RcsbR/x/m3P6cJ+eL+m3bJr14Ig99mFa8r5LBtpb3r8yy/au9sBfYjMmbnuo4kCDe/XrZ0cdeeC3Gd2mrc79sCDkeHLWWlf9rJu2'
        b'bNiQnD/hsfeXPLgteXvd+99+8+l915xOOnAw+OgHnjGb5rlfmffi+qRz3yXdPjq0cGH/29eMe/yLt+9Vy+d5b3lySy8hduUnE2PeRwrrN5b2/EjZL9b8de5Rxxeh3/3d'
        b'8s6WddP9Ly753dWLXwp9oHZ7sduukpm5ow5v+Kz0z3XzhzX9asmTy6fu71oz99jUmqJjVTX1x+preo5eub5u1Xe/zj83/fmn3ttw8qWXlxyrGX//mfSv/X+a0Gu066v5'
        b'b89aX33ql8/NHfaHh9/5/fi7d5/aMefldZ9Ub1xRfdeDX5579+33k553r85ZvfallVvKe5558s9rnp1aUTh6+MxdTcfrP69yXfP1rgfG7XhrY7n3r7se2XHlNerdv3/5'
        b'5cU7Aq8+sfrkizc9+fu5gZ8PC7wy/skti3PmNbz/7X+eGTZ/XOBb/6LvXr/+6ZZ5S+zvXTl6bPlnX/6j6G+9fvPUrEs+PzN865qPv/hK3DN1cl8x5elvSviHX+g9LdeS'
        b'Pm9Kdo/79q8f0335/psuHfPH/eEJclbluiGXDvlZxmPHWt2rjoVbcn6bOnPUL+xlQ/TsP4x63lK88qYV05548uTB3pt2a5c/5PzV0I+qJn182y+vP2cdfMtb11z7knsC'
        b'RWK5RgtfYQDUzfrGgVpUO9idIGq+OKSsC9tJ12ut2m7MZJIFmKFLsf6odkrUbuO0W8gLkLbhOu2ueMhOTgJK6A6M2blG30xegLR7tE1p2u36nkLt6EAZNtsb+WXaoRFB'
        b'ZFxH6kcchaVFA9AZlb6F4vI9oB9Ar+UbrVzvBZa0KdrtQfS3pT+mHdeeSvR8XqA9wAIJMM/n+gltP/mWHLg0WArZ9JvdREEd0k8UylzKSHFFQLuLHJ9fObZJ3zholr4J'
        b'2qrv7T2L1x6x608HKTLrdv2I9mhdz1J9c4HACX5+gi+HXlgmVxW6LehOvdzCyZMEV73+GHWuBRq2W9/Y1AIkXUERz8lrhCF9tOMsKNotemtxKVJ77hIgQGzak/pPtWcE'
        b'oDtu106RC6Oe+lZV33Y9UI0DYUsJ8RO7DCWvS/OAwrlLu1m7TTusb8BX2iP8wqVAuRCruXmwpVTS70tw4eUYNpVaIzuB4lyn30Z+EOGzFn6Gfr++m8Ipagd6z/fq2/SN'
        b'5cU8FLiBn6kfDJBP+eX6zdodUFMEqLiCSQNm6XdgfEYg0JAmyx9umVZZS5EfZ2uPafcklRUNKC1yFOgbtAe1+yRuQnl37SlJ26kdaSG46qkdvIp8osGAoDe0Uv3RxjIL'
        b'l7lcGjpRe4J1YN9i7YDcApMwG1tyJzTysH4/8yp67xX6Ohi3/YV6ZBBGw76Pv0J/ZgbNgbZRrtYevFzfWIJTJ1zPT6oYzHzdH6jVtpbqW67WgUQth0lyy1ySdqOgH7xK'
        b'O8HCxu7VN67UNpaXF5UUzibvcmna0cFjRe3w8CC1erneqt1fysLelpcB2DyhHYdSXNeJ09Zq9zDYODY4H+byLn3TIJnjF0CtpUNYm493n286rZNWafdhNNt0/Va2Nh7T'
        b'jlXrG7VDzHeIFNQ2V/La09oOaBgCQK1ldenVeUXu2fCtvEDI0G6upe+mDNO2AxQfWYqAXILQk6TdKej31Wr30lQk67fOhplsU8WVuLRk/XGtVdRv0A5pj1Cva4DkP1ha'
        b'MrCkCFuXrz85F30NbhDLtI0zaCIG6Zu1A5gBGp5vkXhtD6yiZ6iCYu3mAtapuTDc7hIoX7sfmJnbRO2Edqd2K1UgaevmFZZoRwrcg2bDw50AqSn6AVG7oUbfwIL+3ab9'
        b'VN9ZWjirBNdaOLs7r+3Td2hHGQX+lPbwaH0jrv0tiDYeXjyP105qpyYRuArAK5wo1Hdqd8y2cHwpp985XztAczVC1m8BAIe52IVght4+YXhCgr5Lv1c/Sh1L0TYXw/vI'
        b'3DkyJ6kjU3ltZ199K+PAjgIwPFEKTNOIYTxnXay36rcKsrZBX88g5X7tAb69E89S/WhvcWyRfgtlSNV3D2jvR/Mh/aR+VByinXQR71UAg/pMKfl9xhWq/aQMF6lL2ytO'
        b'1W/SbqTRnXgpOkGcpd8NA9Tmr9TwrHoPwA5m0u9Z2dzRp6keTVsowodPLwsOgUx5K4FnAQxTBOtlAMwXrNpbAZ3MoYG5ubRIu1/i5urHAZ4PW/Ubl+qP04pJcuUmIYva'
        b'iJ+WliwaCQCWru8SAT/dMJpiGk268tokWNTb9M2DimaXNWG+EigGaA8ExhFLZZh2fSONyHDgSO/GDKP17YXFs+YCeknS9wv64/P1O2nIh1+vPQoowZpVRtsILs5HBP2R'
        b'qdrdNJ/L4O2eQn3zHH1L6UB3EUx3V+2OlFwRxuaktomYa/1wRc9SXLwwHNGSgbMHQTUyN3CmvpWz6DskrZUGzDFGP25saZvK3cABapv0pwbjnpWRL4kFixhrfIP2kI/8'
        b'Qt9XXF6OW1apFRr0MCwuGPkDbOQf0H7qAhCBNq1C6AQcPsfKLeqZrT8iLeb0m2gMJ2hbK6FN+jEYlHKM09NF21+tw8a4r4++nwC8HiD8fhph3M0k7emKIl47ot0+iEZY'
        b'OwgAewDbOyhhA8TW6neN79EPOqU/AUCJa2FErf5Mabl2uGTugLlWTpYEW5p+hIWz3TIcmPWN+qbJI6nHRTC4+kGEoocu+b4jMtOV8qh/Ay7r3/MSP1Mmtm8v3iTZBBvf'
        b'/s/BpwqSxUmeo3OAXhd4m+Ay3rAzEVOlyfAmITiM+1RBxtIEDLSQ3q5MJ52rsDxoiiNRLgc7QRGaxUQfg+afXCjzTAJuaH3byQ9DU6PH0+Y50DxGeJVP7B/eEP/hPNOR'
        b'/6Ac7ZQdknGD4JiqQeA5uFZyCl8Hf9FFkUWooBa9BH4F+BXgV4TfDPiV4PfyyKJaDn4dkUVohBjthfnrMCcf5sOLTJW6Fg7V6XxivRRNqbe08PVyi1BvbcHjQqti99nq'
        b'7S0S3Tt8jvqkFgvdJ/mc9cktMt07fa76lBYrHkUGU6H0bvDbBX67wm8a/ObCb1f4hfd4mBrtHeIiKfCbEiJfRNGkEPpz56OpkC8dftPgtxv8uuA3A37zUfMbfq0hKdpH'
        b'sUYzFTGapSRHsxVXtIeSEs1RUqM9lS4tNiWtxa50jXYPiQoXyUbt8mhfJT3qVrpFi5WMaLmSGZ2rZEUvU7KjM5Xu0RKlR3SAkhMdqPSMFiq50QKlV3SGkhcdqvSOjlH6'
        b'RCcofaMTlX7RUUp+dLjSPzpCuSQ6XimITlLc0UuVAdFxSmF0pDIwOlYpio5WiqPDlEHRIcrgaKkyJDpIGRqdrQyLLlCGR2cpI6LTlUujk5WR0SJlVHSeMjo6XxkTLYs4'
        b'WrloP2VsdEowE+66KOOic5Tx0anKhOhCZWJ0sMJHp4Ws8CYvIoRsIXs1jlJ62BXODPcKz62WlEnKZJg/R8gRdZJ6S5tvW1c4JZwezoCcWeHscPdwj3AufNM7fEm4ODwo'
        b'PDg8OTw9PCM8Kzw7XBpeEF4YvhzgobcyJV6eLeKK2CLuViFqD7OI8qxcJ5WcGu4STgt3M0rvCWX3CeeH+4fd4QHhgeGh4WHh4eER4UvDI8OjwqPDY8Jjw+PC48MTwhPD'
        b'k8JTwtOg5pLwnHA51FmsTI3XaYE6LVSnDPWxmrD8/uFC+GJmuKQ6SZkWz50cFileQDLkSwt3NVqTF+4HLbkEWjIVaigLX1bdVZluftOSFHGFkqiG/vRtEtSSTOOZBSOU'
        b'A1/3pe8L4PvCcFF4CLR3BpUzLzy/OluZEa9dhLaKVJJ0nQPnscUZyY84IwMizpAzUtIqoCoHPRlITwayJ9c5Q0mkyjGTBSMgHyBt1iMXVmLDnZJZbEW4Jl5NDpL2Yx1v'
        b'KokbavFnu+UHCtx5tUzftCKvsqnWF6z1uwX1RsRBA7AiZAUv6E/LU+0n6Rvqqm2zGIZvTjpQVl8zDV/cEqC7Gm+wWkVLC5t3TRUp15DVOx6TN1THnKZ6EakV8egbpR7w'
        b'I9w50FF3faPqDQQgJfoaatAsGtXQ1NewIXgUfZq0P7Bdp/G88TSq3p3mTG3rBsULWJa8VKCmekxsbGiMOaB0xVtdgXYQtmoPO3tlFpltXizimDkmV1M5saSqBk+FWkNx'
        b'PjFKqWfF6ga/b238kQMe+VlhMSfcB4IVhlNQG6SqfRU1gZgV7qgwO934A8EAvSX9eqphVYXalkDlXUzRd3TjoqdqgJQg/A1Ujg8msKKSfaB6vavQJTsmUMeBEpYqn7dC'
        b'jcm+CpjgITGxsraGtNLRXQ6L1xFzYJRods9Ufl40JjmoVlR5MTakxwPZKz1sIq1wh0oLMcmjeqtjLo9SG6io9Hk9VRVVy5m+MQCGwry5IVV1Vihwd4jOh/NHoWXJd5bA'
        b'AgGhWhV6nkLPsagSMA2P3QUywxVagXNemRziEw2MO7pV/T5PUgicf4rrYBJN4DSBtl0bSXPVbOOj8DZiBUznhIWVjS0J8YCDhGq0yEghJ5oc2WmIkTxSBpNCUsTRxKmT'
        b'I84WS0iIJK1A71HOFtmfTilOHRRxJnEtlgjHlMcijkgavHFB352ZOBZyxArpnq1CSI50gxoF/2UhQS2BZ7mRjGr0sVOK6l5QT1eo5wrKnQVf52Bp/jHwvFekC+ULRLoA'
        b'3rGSVZuzxQY5rZF0yCnBXgFj3YoWM5UhCXYQnsqTobxbIjJ8Y6dSe0AenAkX9NAB3xvfhexw58A7DFcUsi/gWN8jPHx/Cr5LiSQnmRZ1YiSV3iVnoR9hYAwVLpSE70IC'
        b'YNrkTI5ZeZHzUzsLXxBXq2Mj+TKMvyPSHeoVcDxClnSy1IuPwFvU1kxzBELtDNHdzv/mscj/feH0j5JfIzR/ZTGcHLhMWlVgNlsy3Mtk8ZeGGkPkc9VJHlcziM6Vge7N'
        b'QM0g0SWkCjlE5drEdF6SbN8CghfaLZMuxs5Dy+R1wVgmLphqt7FM0hOXCbwVcfoiEuxOWe0WDk5fIXwj0R2CvCUkBYIRCwCiHMG/DJh2EbXwQlZ1cshKpjq2ENTGgAcW'
        b'SvdxnL8u0iPSN9IfwD+72oIuogB0C1ocEdRlc0CpSSFHpAcsxxUAeClJXDZuySLcu/A+5KQFB+WEkoA4TDEAmPT62LuQA8B9tn9kpF8kOdJD4SN94X9/+N8rUlDNR7pg'
        b'PZFeuKzSgbiE590jfCQ1kopEWa2VlrUFwRgWUpeQDXqTDAAPvyFYGhFXFtfiiqQBKYBPXJkcLJtkIhGS4CsgDtST9D3cKag3LKNOVIvFvwqeypEBUGpKKCWSRXkAGUB7'
        b'UyJ5lMozUv0o1c9I5VMq30jlUirXSHU3W0qpHpTqYaT6UqqvkepPqf5GKodSOUaqD6X6GKmelOpppHpTqreR6hUfOUxlUyobU9UpsDEUIWkf4jYjykREAH2NXBJJhh6n'
        b'hlK3ogswia5WvBK0ZCK0QBkw+tXoiNzoTSaHhoQwol0RyqBUkfxESDj2iLjpeWFIIh1byXQP0OZkvMv/kbXrLv43wB//8zhqCOywgZvjOMpl+DNDHUWZd1H4sDRekASe'
        b'/Ulf22wOctiaTvqOwj+kZKbnmC6gJqP0lcNJ8d8kh5whOAB/wR9/oT/pL860VDENcBset0rfOS1Ocq/eDr+Zll+E35hzTMBgwDZHbAZ+kyNcAn4TIxbazoFgidiB4Ae8'
        b'xnS/221HnVIp/4LwBzSoe2RDIc5A/CIgealDp2xmp05hpyRYJkh7CICW7awjraTWqXZFVfRIKnoDpedSiHJCF5MjMu7QMBQpgKiSEW1jCpXaI44tWTyWmhRJw2WIg0VI'
        b'TLQAko3YRwIJOK6dOrvfNoQLTE9UZgckCOgUEL5o3KdCKaSSjUGOqDzTKuhig9r1fxaij8pxpXaAYQGvDmsOL8MkpPE5BGOO82HMkTgdzUhqAlkYSUEyOD4dkjEd6TQd'
        b'3YA8EwMZ9AbTGZgmN/19AO6caBxM7xxb0mjw0IDemkXWBpjqZOjHtht6IPgi1mw0jJXUx0JioMwkwXmsTwKCEndni9qEES0R08K+ZoEdCCa7xdpsQWEEWffZJS7Ira03'
        b'S/bzqzn6Iot9H7icmHNXOBUY8/RwZrXVCLNjS6jFhphfvS2SjE/Mr9meCJSGvVpYIalPQFtOxEu2oxAEvjkC38ATeG6Pf5NY+12J9m6KadzfqeFO3MtvPBYkcirQaRh2'
        b'CkyB/iYwOhB6v2zIQNp1lelbZoYp+xOClervkL/8hP/RHkBirtqAp6Gy2rNaReVs9axs8DASLxnecAn+3Dyx8P9UMJLsf6et4VXZMPZlCwlV252CkzYG7G7Odw5JIrdD'
        b'GP4TrZ9Z+BYJg4A6pD9npTusNiGNd1rxLW4jcP1Gel0qknh3FpNRhLAuCukhBtYG1P/AZ6/j5Q28vMn0qNENUED9TzIcaPbVVqq/otv6iuBy9S2y2YYbbwVGjFDfJkOY'
        b'WkXNp0KBf4+JFZXA+S+vCKBld8xqOLaKWQPmTY2vobLCF3An/2sG0H3Fv4GM/v9f/plDDYTJm5Bpw5iCgmCT2h9ouIQsi5Nnfx0PPNif1Mmfs9On//yfbPxvSzvlNFGy'
        b'zhGlEQ6+WpTqHHyeKDkHi1KOgx8nSlMd6CDEhuwmkHAC9bMMDW0e5yguhCdRBujxGCuyvqIRlmVQVbfxzLaXPBiws5TXaN1NX1PlbUQfTyoqTODJSlVFU8Dr8cTSPZ5A'
        b'UyPJDlHQhmYs8DTJ05ZQz7R3R5FgBDuuvkFp8nnRNRqj+GCflFLRx26nJzzc9TYL+xX6oGWjqX4ooan22f8Nm7J6qw=='
    ))))
