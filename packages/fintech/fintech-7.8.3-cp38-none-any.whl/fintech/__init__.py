
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
        b'eJzcvXdcW0faKDynqCBEMcYYXOWOAAHGDffuUAXGDVckkAAZEKAChggbG9uiG9u4V9xxBXc7rjPpZTfJJtmEZHeTTXXi5E2yubtZb8o3M0cSoji2s+/9/rjox9HRnCnP'
        b'zDx9npnzMej0J8P/0/C/uRxfdGAJ0DFLGB17kNVzel7PVLBNzBJRFlgi1nE6fj3QSnQinRh/S0u9LRKLtAJUMAxYBIxTeKD3yJGZVjFgiYwBpQqdRC9L89RJ8VVO773o'
        b'1VsvW8csAmOATrJEtlSWChYDI5uKf80DHllKjwf9ZPOz9YrkEkt2vlExx2C06DOyFQXajBxtll6m5O5JMJj3pOTC4UsbE57BuPWGpEkc3+ZIfLGDTEaH+7NeWsZUggpQ'
        b'xpbKbEwFhvgQOw/Y2ArAgNXMagIBwBCsV3LqDPfhEeP/aPzfk1TI0yGaB5QKdRv4B3k8P5eAkpnNg0kDffFAasJscyPB50LZb6c2g26ho5WNJtCxdmDnMjkXhMyTQ+is'
        b'uCOEvNoage/h1amB81RoO2qYjyrDFqJKVBMxN2Z+TAiqQ7VKVIVqOTBrwXjUJEbn1Gid4XDih6w5FBe8c2jAV5ovNbmZ90OrNC9+FrYlRBujva95Nd0/Izszlz2/Lih6'
        b'FFg3XbLo5EdK1jIElyhGh9FpT1xxKKk2EYy0qkJQdQQLBsILPDoHj6JKy2ACUjmqgZdhDdyENsXjjLAObpIAb5xU7ccNQNvgdZMHzqbk2thgpYmgp3AhiQ98J2Wa8kv1'
        b'RkWmgBlT2ry1ZrPeZElLtxpyLQYjS0aBTBoIkjPejEnuLNrMtfGZVmNGmyQtzWQ1pqW1eaalZeTqtUZrQVqaknNriVyaGZM3ufckF1JJH1IxSQJf+LJihmVk9GodhlOy'
        b'8uD++LBwtSoEViW5De0AdAiEjRKhZliJjuYSKP629CXmVRGILkh9iflP6tf5EkAR6EiAtXQs/4Uv0KxNH+DZ3+JAoA+n0qcRmhzm3b4nRUChWfo3n35Ckcv9WPCBjQCk'
        b'SZAv9hISK4dKwIcT+wKcU56nFgGrigx4wxxo94QnwjBMlWjTvMgUAQ2Cw1XBqDJiUt+Q2EQGLFsqTUCblioZ60BcZurgGZ5qFbwcEhKvkgWjangOnuBBH3iTh7vR+aHW'
        b'ATjPKLR3IpnGCNxj8i0BnkksvIBuoy2weZx1EGm6Aq2D21xzjQ5Cu3O+8VxnohNKzhqA8/WDe8bHq5RxiSIgnseiC7AlYCHabe2HH6EdsE4STwc1NlbFAk+4k0WXRehE'
        b'NqwQ2qhBZ+ABJUGrJFQdlxiOqhLgKR74wQoOlaPtA3AbtKImdGl0fGxYrApeGUpRVAS8UTWnjkPXrb1xhjRYAStIBpEHXAt4noEH0H50hfYVbnwaboQtcwXcToxFdcpY'
        b'3ATaysHrQ1biQSPoMaEHqu8dHR81Cj+OR/VJsSLgM4ibiLb74wx9CQh1/ROKE0mG2EThuTc6y42EO+FRJWtV4Bxz4IUJnjF4pgpQDaqNJx32R3s5tHskOoa2wqNWQkFJ'
        b'GRM9UX2EKk5tJbli0SVUlZRA8o5ZKg63xE4airtMoT6CTsDDqCZMjepjw8LFePAusHD9XHQB3URV1v44y4AU2Ag35oeiejz78WFKVZwI9BzA4bZuoyMUJLjDBx6MT1LF'
        b'huI5qIoNi4sIj0kUh/uBMCBCu5RmYXC3p8cSWELxs3AGeKJDLHwG7kFXlsEaioSoAYNij6d5SOeTg+Mxe6jHOLEJHYdH5yWrxGAmL0blmE+csBJ+gk4PQidwfty1ucEx'
        b'CahenZCELmQvIDnDJohmJ8P6DnyQdefU+ynrtzOYwXJ23i6yi+0Su9TuYZfZPe1yu5fd2+5j97X3sPvZe9r97b3sAfbe9kB7kL2Pva+9n72/fYB9oF1hH2QfbB9iH2of'
        b'Zh9uH2EPtivtIfZQe5hdZQ+3R9gj7SPtUfZR9tH2Mfax9nGZ0Q42DipFmI0zmI0DFxtnKBvHjPxhbNzHwWM6svEKtXU4GYtmeH2qk8PMRRvcmYyDw6yHm+mELkfnzZQq'
        b'1SqlKjwUVhJq89Nw8CyqGG4NJBN6El2H21ENxlJOA88Ddg0zDT89TinRlgivhcLmsBgR4EVT4XoGVUyBrbQcqodn8OwpVagSY64YnmSHPR3qha4KD8vl8BqZrTA8/Ty8'
        b'FhPLwJs6eIxS1kDMBzD9VyWQZ+jKbA8GHp0ENwrQnGb7Y24Ug4HBz3Z5xTDwAtwBqyk0c9GlcaHhShbuQEcACy8zS+B1dMvaiwAKz8J18fAkpmcxEOey/SzBxp7WIIo4'
        b'cC88GY+qMWptwg0GZAxhMOQXWVqlGt7OoljIGCCps55JCEGVAiiH0/h4inFhDBCPZeE6uL83ql8gPKxFN1BjaBymyiTc+2ksOgkrvIPmU8qH5yZiBCe1Bqtw0VUspp/G'
        b'kWgz3E7bRGczF2CGEMyi9agOsEZmCrqKH1Fg1+Nh3YEHIA6PCWrCAO1k5qBKTDWEgNE1dAvtpFSjxPQND+DpksLbLLSj/Xj8/EnTt9RwC6pJDANFTwPWxkyFm3sLjTb2'
        b'yoenUHUYQBen4HovMPPh2uX0EStFN+IJU0C1PBD3YWfkyVaiTXRYMWB7ZqOaGHgGiGANYMuYOav6Ck8ualjMYsOZklm4tmrmKYxy+wU2sx+dD8BchtQXGh6bga7jQcLS'
        b'p3c2H1XG0gHyQq18fCiRI3F4omH1UOAhZuE21BSRwboRAcH7jgoSVo/sjEtBYiuxOlTGYcpiXZTFUcpiV3MOysp+PAWJUxuaT8Qy5ik44Z199q80L6d/oanM+gJ/82/W'
        b'TtvtETOKMWQqvJ7tW7g4zDN17aTtG2pr5f2n/TuzYcJl740a8R8CwFsi7z2iJqWE6jV+iU6tBtUlKVFdLKzDLG8jIb+AYTwH90ZbCH3CrX39scg6O7CT/oPloWWqhWgT'
        b'cJPvQErBeHwuhCViFlnVnm8g3MyjzaPUFjLw+ZiUqXRNmqHBWAvrSQ4ZasCTXQqPWoggR63Kxbi5c7AK5yIUSG5wcxw3CO1EVy0EtcPy0Y5QVQyRfECqnoUpBa7H+HWY'
        b'qnVoLdoXB2t6YLAi2oWEAMywEFESjw449LVOGhRNpfpTG5+nNedQzYwqUKuljPDxZmSMqaczr5Jv43RmSxtnNmWYCDs0+ZJUtr1KfE9Q3tTLWTMtvMZVcUUHzYxwHrR3'
        b'bDQhDlQvxtzlaL8wzAk0aMfDtfIoAenYTPYJdPLM7lCO7w7l/vp9hchMsGX3mxu+0iy78/rdhufevdvw/MWGzUu/7/Gid+aHr2IrYjz/06oxWK0mPZjlaY4PC44hGkX5'
        b'OAZT/ym2JB4dsCgoicNdgu7VjkpF6IyATfDqOGFY2e7nxGox5LZry2uA1JcxBYB2bZnLT1/Z/TRg3TjQNQOkSCWphuQC5eCBd+c5YNEJRaiKyCoiGZrRIRMDbz8l6jAH'
        b'jON/nhMgm0DKjFoAOcgFfHsPvI35afnpmVZzhtZiyDfWkqKUmbDWEEJGTagBtmDWSYcnKS4Uq3eHVGo1UYOx1sGBUHhBhHbHwYbHgCTzNyHxcIKhb3ADgupFz2RghbkG'
        b't45bNqBDhMT8UAUHb4Z4PxwJxxIkZAgaYuOQ/2+MQwZ0x/tEHTM5ue5AV9uU69p5V9uPw3e7EAFpW9YdEXw6+VXOHE8Qaf6ZU3+/p7mv+ULzZYY8S5qp0QZrX/ws5D+5'
        b'59N1J/Qa3Qm/LzRntdmZp/UntNnsy3uijoDnvgocHDg46Pudg8tvYCZsAX/+2WtT03ElQ7lrCjq9xAzPBDMxamzcOCa6B2rgYEtfo5IRuAjfmVN1Ig1RWoY2V6ANuUAb'
        b'ASwjZ3wxxyrtY842ZFrS9CZTvil8Um4+zmmeEk4LOJkYrzVlmdvEOcXk242CupiYrImAbBrgoiWCMdvdaOm+nzstkZnpiy7Cw7BiDNbXUWVCKDY3qZGNLa4LuLdVSWqs'
        b'KMDLWPuokaSMB7B6qge6MqzUYCluZsxKXP5YjyU5WdlZuVnqDLU2Qbvyo7A9J/RfaE5qv8Cmvizzw1wG6F8TvxIvFTrzmAPm6TYo7iyll6/YpHBl9epuEEw9XL0nORvd'
        b'ev9Nh94PJdR0FTWbOnWdBX3hdXgeXuPhCXQZHXg4VXVxBz2anrrVJdguOM2r5xsac3ezZgLk1+c847VElYjR8ltqlYqxPXfqvln1o0aa+WGCBGS9K14TY1LyFFvno7Nj'
        b'qfhWh6nUob6CUO0BL3KwfuUsC3HDjFCjZ6gugG314DhVOKxPwt3fFBqLcVyQ5KlpCWppJjqrsNARakkcSWtE9Ra0tUPGPmgbD9dhfKDaysBIuJtWrByEyuMS1Ilx2MIS'
        b'FIihQ0RYI9e4Y4DbXHtZjRnZWoNRr0vTr8pwJ5KBYkb4mAY5iyixGMG52omg2YFRjGmwa95J7v1u8/6J3H3eyVN0IXphKLWpYzBF18Yn4smHZxaujhGDYaWipIChHebI'
        b'OelE9jjZGTUDn4iVdpl6HnQn06XqXNJ9zyipVDcHKPRTTxn2mN9btiJrrLUuTwKo6TCl2AfLv6boWEyXlwC2mg8x8FI2KqceoXeL/+HT6MMUPL3gQ+aX1IhJHwqenCme'
        b'GM94sKrFp2VCeoBVSIw0+AEyy5ErfpH/sKoEGGbnTWHMRpyyYcnEeK3uyD+1J/Qn9Pc1BdpK1Qn9l5iuv9QYM0NSmrVL7jTAiw09Qp6X+nue1LIntzTrz2pPawMkX7Jv'
        b'ygdrJmx4j4np3afX929F9voOPLcrJbVfYEsz83JL26i3onqJmbejxKMKMjHup/V/Oa4fZrbU5js63CfeN8rl7JDCBjYfbY7rnl88kovw2VpzNkUohYBQI4iOKKMfQV+U'
        b'szzmw/SOMQ1tRzKBj7Zz2u7bZ4RsFOdI4WNuOPdBB15D7b0aHdqPDSGsOuJ5h1d69MIG2mp44REOXaaTQ5d9ckQjQ+DRBdHkaqsfvg+Cx2El2oobjihG1SAi+mmKGbMH'
        b'iMAPi6gHOtcaOEtAl8GjWHAjiNxpElYFW4CJsOXuLm1MmsHvP0G8uRr/KPr7INWroX4w0n/DR+bvs/fIbIuZ+LuLgMwseeMPijj/rScHD06ddX7elibzcyO+2fVrWWWI'
        b'CZb36j1pk3j/islvfRAx4tBfvdb1WMQnlOo1UTPmLq4a4Dvyq0+X/XpUO2/InNyFz2Ve+cvXJzcXLy36NS40/B//R/V2+LU7CfBfzNrN7LQ9mffqCg4M3FI15NUdLys9'
        b'KavKhs2LCKsaQi16p23ltKuw2LtgIUxiJTwNK81hSiWqTghRxTq9zyFLeXRGBG+HTqIsN1wagy6o4RmL47EXKsef3dxoeBEdoxbTGtSKTfvO7mk/2DAC69TXcy3EkTcD'
        b'7YX20HBUiaogzkvcBbCeVWGz6TA14Xynwr2Uu4bBfehqtybcMh8LEffwGGqB1aFxqjAGVcYmYKvZE7ayaB86gxopwOgGbMkKDR9YGBsWogxHm7D6CkCggl+B9sFd1AqE'
        b'J7zgUcr0pxtISwK7p2bg5eI8C/VPbEKn0EaHHUGNCCxFTrMlyWJqY6Dt6Jh3qFoVPTkWjx8L5FJOOghu7GB6/YZ5Jy6wpucaBFkwWiDdCSw27vwwoYoZf4bHVxawv/Is'
        b'vv7Cc/j6M8/j609ikRgTt5yQ83BXnb27bS7IRbsk5zU32n2pg9VHuiuGdtgaGpyIEaYqQfz0SiBFLSwsX4hqaAsZYjdqI0QldVLbYI7o+zYmCJSJKyU2cSWoYMskNolZ'
        b'Xept4w4Cm7iJKZMuAkZ/HliYHJkpmgHksxgYA1KxSmyTkpI2MaljEtAxpKzpR5uoINUAykQ20UG2CcwCyxuWsWUeZTLSgs2jgjWl07Z4fHfMJj7INdE6DvI0r3+ZZyWH'
        b'83na2EzOJqtnGFBYb5xGS8gxdPJKD5u4gsHwyiql5K6CoaWktJTUrdSzNrnps0q5kNsJI07/oTC9gTUOpTV6VrANjElRyVSCHDG5w3CIdGwTI+RuYIw/0XyMRZzJ0rxx'
        b'lZ6OvHGVLKnblfNNmlNMcxVUihy58F2HXKd13EGJjteJ1mMzchaoYPAIe+nEByU2r4NSnUQnbWJJis0Llz2i87B5BYAyL7vE7olVOU4nw+WkNo6UK/PG/feuYHTSHNLi'
        b'mzZvnSeeDW/jYFc6j9O/1clJizbvJiaAPOV1XmXeNraBNU3A8DIUXtYUqPO24RK9MbvOZHE+H6PCxtjYHA4/i9T5kHtHulTnaxPuBruVn6/rIZR35SGt+dh8dH7jyLcX'
        b'zrPO5k2vPrqeNm+bF6mPPDN623zIk4Jamxf5bRHm1xf3whf3wh/3gjV9Y/MlvdP1wmPKmm4Jv3CZd/Gd1JX+jvCLpONe9tAF4N9A13sDGwRsPSj8vrj1wEov0sJKmc3X'
        b'CYONa+BM/hbG5lPBrGOMUouncOcw9ILU8x9IcrHVbVSNfMCGKTrIRNYhF6kBTdw1WZiklsvKGBuzEmxmC3ki8xzKZZs0Lc2ozdOnpSnZNjY8so2xdLatZZNyDWZLRn5e'
        b'wZQfnQJRjBsp7ZeRrc/IwTZWuxnWnvUBp8g3PWDC7hHIHsjyMxWWkgK9Ypi5C6giJ+0rnKAGkJViGxHdrJmvxGBXMA6w17cDh3ljCJWcRb/BGU1h+PITcBhEBGoZuEca'
        b'fuCjVRRpc616BYYseJhZScXwg0CzvtCqN2boFQaLPk8xzEAejxhmHvGgB00gt64knl57uuV0ln7gocizmi2KdL3igY/eYMnWm3DP8YDg6z3BmfOAGfGAGfzAY5h5aXh4'
        b'+HKcTrTYBz3CFFn5FudYTcD/SnmbyGDU6Ve1yRYSgGcTGw8n4VbNbXxGfkFJG5+jL8H2Lm45X6dv80gvsei1JpMWP1iZbzC2iU3mglyDpY036QtMJmKEtnnMxw3QmpR+'
        b'bR4Z+UYLMShMbRyuqY0nCNEmpsNjbhMRWMxtUrM1XbgT0QckwWDRpufq2xhDG4cftYnNQgYmp01qMKdZrAX4IW8xW0xtfBG5cnnmLFycgNEmKrTmW/RKr25V0ie5YK0y'
        b'yYWrUidKvkbmfCNFMaLB8gwRh96MmCO6K48/UsbXodfKGX9WRn/70XScnw3A931wSgDjK/bH92KcGkC9pd6ML0vEqRyn4l8sEZ7erKAR+7He1KcayPj/ilv8lWX9cSks'
        b'YAUXPNzrmUIsqERs513VqMPisFaTxo2PgVs6uOClQAh6oDTxd3zBkou1gYOASqM/YMnFlfE2ztynUG7BSi35N2BJt5cj8s3G2rhJmHZMyVgWMjli/I2lRxA4yGKOyQWB'
        b'JiyHsFzisTTgifww62x8FoPr43HdyViGcUS2YDm4G1MgkRIiHalPpONxHRz5hb+xXCT1FGYL8sZ0TMcXnNAROS2ySWhbYsdzkdA6rYedBOhv3vGbnwQK5TaWRp2I1JiI'
        b'1WQa6Vwmk4vadUfSlCLTDDLDnFlvaeO0Ol2b2Fqg01r0plnkqbRNQpAvT1vQJtXpM7XWXAvGWZKkM2RYTInOCtuk+lUF+gyLXmeaS9ISSGHxI9DMzeNJghx0ac56B2Be'
        b'Zh5OsYzH2EKwzFfABIJr1HaSM4GsL+NLsUtYSWxE6+EJx3o6rIrQoutktS9RWJwLhVdEaLs8qYs9Qponii9trsuyKiALq5meTqPHxjhdkZ1tJZeipcOXSjLVTBUW+ytB'
        b'gS9GM1zQNBqjhhdOYYgwrWA8sfFDxRVGCiwEmUqu0pPcV5HAGR4DQpqXYXDkmVKXr9LDxhIk6s62IphNBpW6Oj8jQPA2ojuA0kO4YY7cU/0pGeM8ixvDoFUwOQCDhe9s'
        b'GJAyzhhAwRNj7J5D7nAKT7DNxtG0gEqi22A6yMS/Cc5T3SvARmqdUMbZaJ0438ZKMcZUDus2vFFO7nE6/WXjTblE6mAKwnXYeFo+F+uc4Vjn5C2iTBbrne8yWJ9kQKkc'
        b'D5OISGYaUYXTVoucEVWYOvCw1TMOPzpGM2JOtEmKtCbqoOSyMCpjbmrKKTZNJygWJyBju0+SSHABd3UU9/WYfUsfmzu2o608jfLFAtxwnnm6C2kxgrIYOb0xkmIGyBLm'
        b'F0DZpZyVY2QOwJZDH6Y0UpuRoS+wmNulvE6fkW/SWjr6X9sbwJI5nTRN+oHJmkbx0ISVJMHz9/J5rk1Chg1Tr1Blhqt7Hi6AohnnShQnsP0BmPn2CSrt8/A+OJUJLaku'
        b'l9zLfpcQ0rrAkTgaG8M4tCXAKYYIi2EHFyXEJ6jVqmClGHiGs7Ml6EgO2tjFwenh+DbH4IseLMFq3xK2USL4NjDJSzNFAq1VMEs4mk7D2BwMwQNTIgkVJE95O+DBEhFl'
        b'B6K2Ho5wvjmGXH1CvlanNz188XcCAILXTkTDOMSZYhd5849cinjMZRCJmkZMTJuEDqBtg9tjU1ADB7zhSc4XHuesxGuc3Q+dLFxGlpJo8Fx7EAuqdPojLqUAsCxYghrh'
        b'QbTfGg5INEEhvCGUCQ5G1RExKlQNm7HVPT84LhHb8eGxqrhEBhh9PCaj4xMocy6F9ejCPNVUz4UxqFYZl5gAm+cTH0NSAonQGg23i4fC6kLD6z2H82ZCnIfWT/lK81L6'
        b'Cf0J7Vll6p2d8GpDa+qx9coNzRun723a1VrVWtGcyr2YJW7NCZyQeuG96txy2/Y+4pEtNg+zZKbEPOpP7Hbv7Rtq78r3qsB3n/UUBxQrRRYhKmPQVFRDfRZ70ToR4Acw'
        b'8BA6oKTeBN0yffqi0PDODokgdJH6IxZM7o0uoFoVqowIKXS4WfqgbcOsPNz4VC/qcDDlYLxDdaHhqhgVi831I2wkOoyaqB8HXoFXjfHhcYlhZAV90yp02zHGIjDsKdGS'
        b'WItzVeLx5aZXhkmPZXVaXr7OmqunfgpimIA1+JNFPRAs73Arlg7sgqThHUq7VnnM+txMfCUMod3zKHo4jbKmAnJf6ITKlE+GkhApcUGAcvzZH+DmyXgkJF2Ix7XYNsNJ'
        b'PO4imsGUKXMRkejJ1/NEwM1achGRt1pY6NwgCnCnoKWzHDRUilqto8i0XugJrz+ChOBGdMxJRlfhJSsxn6bNJoVcVDQEXhEIqSsVzQ/87YVcB2twLORi45PJ7GxsSifl'
        b'avPSddopT+OSJsKMrAtJ57YtR/vMLpgLOkTdoS3x8ExMIiZdp3MSbeuwGsdF+Znh1hQ/dAaTFdrYA573huXwRCINtJyWhvY6okZqUU0Y8d2lomqsmqdwI1dh1dy9RyLg'
        b'tk5LGaSgA7Fkll0MkqvEM1nG47nlXHPL07nlVvO/xSBdypk7g5xIpu4cvKWOJwsw4cKS6ryYUOKLXYD2D8ZErlKi+oTYBa6JFAF4UC9Dt+BZVEX90F8zPKk8OWG6Rn47'
        b'JBhQnjopFR2gdcIWVOesVwhMRZXCenkY4Xp5azwCoR1eoYW8iwPi49E5GjdYG5s4NxhVLRIY5FxX8wswBqFWCTpnhMcNK3t/x5hzcMl1C9hTpns0yOelzHA/pTZBm5uZ'
        b'm35fE2b6UvNa+svpf0iP1W7RvZh+Rv/FtL+/HQkWTGQWjKqYbx/1ibIlsrFFb+51NDKqXJG88WjF7L3M0L4vNbzgz7z1l7uQf/3uBy8Evnpnlxi8fTLw1KZmpUQInNmM'
        b'zo7sFBAEN8HmAIffeie8QvkdOjcc7uvKMKWwkjBMeHuSUFsrvI1uUbYIj0gpZ+zAFtGBdOq9hufXZJBGV6JbSWRVRnA5e6HzXCBsgnupSzkXVo/BliBdJUSbQsOxNgDr'
        b'UvxWc6h2Wgr1SqPb8FSeMwtZ2vGcgLaNY1HdSlgvNLNx4gozRnu3VXZ0LU5YaPeBF56cRXuTFfS0AhO2yol5RHl0HyePXgOkLDWWsZnD+hGTF5szpWO68kf9Kn2Ggzu2'
        b'61odaxaIXyQoce267qMWjxxrTN6uApSFW/BlA+MUJ+X087M7E7cuw+n9VsNjv5t7kBDjLeNRq2g2ujYNXhoGmxMilWAw2ua/EjWhLbkEuiVrgvgf/L6Qy8FHI75nL4+c'
        b'Zn0Z0MXFcaJdJdWsxgdM00R9YDodP0pIjon6Pn5w/+CBbDJZc5xQNAMYQix3Rebj+Fnqxzt61U70hpG+s4r/rP4ptmYWYqLFxR+CI6milyxDj/7lw5gVff7Q8EFj4sg3'
        b'X93zRmXSt6K1XkHFeyM8R3rsbfq75LnXFr322be515ZO/wmFLUyecfRMz9tDQvrW/fhWb9+XG/a+vOhN/R9vfv+t6X+eLbBnJqYu/dvBDS+dz7j9YF3b84deGZn56ugm'
        b'i1/oLy079b6LNiOP6P1NqV/XXc0tuXp31jbf+he+/YlL1oTdnNeqlFNUVg0ydFyqGcgK0U94OHdSVPaDW2e56ypo4xDH+smJ4UKE3OFhM7qSn5Vfjk7CjUOjLcRjZY2N'
        b'FFbVnZMIK3EDeAKFtRYO1o7ViZd7oN0WEg6VDw/Dkw7dBu3nqXqjGysoN+d6ZXaecBHoO4aHW0JhDaYomisNN3bewToolsBq3DjuWS+0lkMXZRNpM5MWFQoqmghgCrxA'
        b'VTQvKX20CFaZQmOoZhYJ7fw4Bp6dhDbS7lqIwS90xhENiGrhGSEiEG7uL8SV7UB7IjtJJdiArghiSTGb6nDwCNpNFNwEtB2eYQATDTA3OaH9LRXo95k2YheT8HSjb8oh'
        b'gp0cwuLS4lgZcYVg4vPFdzzr5yPGV19sZ5b2/01+4dDrqJLWJnaktXOFx7Z7sZ5XRO4LXEzCii+FHfS8zQPc9bzfhgvzUOozlaU5EtLSsEGdVmjV5gqec6pH0kbavMiO'
        b'Fq3ZnKHHHC9N6JHHEw13M9Pm4agEV0DBJ+EF6QR8IsqlLMsEyDFfIzCFwP19u/K12RnO3QgT4E0x3BWALnSxMKWObzMxlJwWph5bjQ7XEtFrRFijYXXceo+H2pHJWgse'
        b'NCMeMHUG71Y7QRjXAvo0fHHpwVQLplF1Hg5tia+UYm1JhLUl3qUtiai2xBNXCtWWsrrTlrpqwmLBnBw/Fu7vaEvC9WFUFUbnx1uJpwXux5R1xgY3k0i1mMRwrMg4rDxV'
        b'CtZ95gUTj9wCacctHkw8AFE9fTxgLdyvZOk+EHjDH112bwpLbFTFgz6T4LlZfMwcdFAIz77tqXXPFRoSIwZ9cmea+QVWWGNYvSxcZF5BOnFiTP+XrvUoV/jPfuN2S/bM'
        b'gEOjjhkOD+e9M2Mqq4aek3/x1rCr48a31LHF6pzMyIRtw1u+Dby+Yn7wawUbDs04uXfe2Okhf5P3/eHbc29kvfFL8QJZ3pLspm/HfuOzBfSuHToFa0UEmDJ0FJ3rbDvC'
        b'deg4v6IvWiesRp9fACso++wLNzqsw5HoKuX3C9E12Ew7Ew+r6EYU4KfnemHFOgBdp5Zr0cw+JITff7yAg1J4lF0F6+FWythy0BX8sKtxelBOdK2ekynzREfhpiUCZ81g'
        b'Habv0HALCTrGBkpFLGWsizhscxG+OnK0U9l5MkpzDx/NxEicRixJytQCnExtDRgsk5Plczkj5aSsP1Patwvmh7vKCuQubuMycs1t0kxrLuUPbXwBztsmtmhNWXqLG0N7'
        b'hGqGOeFqck+Cq03l5LLWxdDK8OVAJ63n437uLO234FSyarWDqZmKyWUVGQNPynPy9JbsfB1twFTiHKTfkCimUhdQNnzZ53R5ETZFWRS6EoNutvMoqbC16pjVtbtqokIM'
        b'j8OqFGqo3B/Fglfnkeo0ufnBYtDFDe5yT00CnfcXZUpcu3+YR+7+6WJbO/3SHTlKkJp6klDdaosZY+1Fz0IruoxVjyuo1VKELnkWwTqfAjlqBWAyOgafUYhQS9h0K9nR'
        b'kIEq/WEr2o1LVSWoUV2oegG1uWPxV1WSyrkRFJ5BlWHhsDWFbKqCF+F1GbqNTj71yE2rHF18/y8D5LtyUJGa2sRo3whYHQpPJLjmDWecz6GqbFQzEzYJvK8uFW0xRBFS'
        b'F/qHtoXC5mAG9IGbeRM6hK4b5ldvZ83Efd1/QcJXmpc//1Kz5E5LQ9PW5opN45pfbK4YWVPINFxq6PGipHXXxJ0pgfN2BkRVfDIx8Px7NfcnBAa0lM+PjLJEikYdieRH'
        b'FVwG4M1VfmennFGKBO2nBdYOwKYT2V+DWdRpFm22jfKZRxnIRLQfHaBcYtliB5fIx8YetZsOobWwPFJNPRqoWiXoaD5wLbcSVqArFrol6PgStAFnINFOtb4jOMCPZ2Cr'
        b'Ee4RPHO7Sse5AnlWonN0QwA27B65CcNTW1CgxzRI+EFHF9gaECunXMaXrhmVhmBOkZZryNAbzfq0TFN+Xlqmwd2gcqvI2SrlEA8PdcYsstxFqRX48kIn9vFMhxgeslQG'
        b'D6f0iE9SwSqiA9MphhtFaliXRF0P+FuQi52NJcfQYOEgDK0O7vfNmyoTtl8eglWzQ3Hhc9NR7aixLBCh/Qy8iPagE1RQrvYuxPTSWlyELhbKpQWF8kIeBExE51AzlzXc'
        b'0zoCZ0lG5WibGW1BzegiavXwKvKSeUvR+WJCnYUiMNSPL8M68QmhuYYBPvFY0JFp5LAgalkE7SyWIPvRTepWwap1PdwBT6GtmKCrEkLiwuBJ1FgcFkyUgQTnPoV5UmGb'
        b'bkgYy2CdG17wnJk0zkr4D9a7azGF49LQjht9dA24/PZcGdqQjU5R5ggbUZ0PrOk9paAQbipGl9EVzGUsWDe5glrQFSvuzjwerrXAw3QfKLqKbmRTaHfEL4JriesAC+IE'
        b'CfBBm7mUCF8rUcbh1j69YA2xnDrVWYxa5TIxGBrLY1vmsooq9XT/Wr9weBOS/ai7MVJOxLSzCbVQPQrVTce92pqkisUdPRcTiy5OkwD5ZBbthztzqDcoElUHeKqIMyh+'
        b'kdBjN0YHL2GmBo/kicFytFYCb2jRISvBzZEhU+ctT8DNDwVD0UZYThn/lllSgB9G+optuSikUAiftAwQAzkAvtOMxQm5xf2xZk+TP1nAUW/rQaM1rERrEvL+bJXQvC3z'
        b'dQki3XxgJYwSD9W5AKJthMajPVNJaB51U3UDpxjbjOXSsqnokGHJ/HTWPBaThy7JI7FhshpN892Q9c6vVRm/DCn0mDDU/+gsf8s0RmQ5PKt6WPxIr+euVm2+MX/WXs2V'
        b'jwL7lQ8p2NL46oT6bZn/mnwzf39RkffAg0gUOPRiKjOzZMiKoE13/73wP+rb6kv5bIo8o1D63LQKj2tv16086JE1oOST2y/0+jK7x9yGU6bn3r1kD8gZ9PTAvOOwbO7F'
        b'3LD7xXuUPeedzzC8HnXl57cKzj23+d47xfcqo04lzJAEnPto2La8hrufvjL13gTLSu9tbyruvf+L8dM5RX1ff8M4rv/Va388/f27o2Z6bvtVuqNA8q9v+ft73rq+sSbk'
        b'wzu1Q7c9XffprGVzXgiYPfVc4XjtsF97Xp3yeduFZcaLL5ycM+GlbQVpp7/4oV9C+t1mpf+i5au327f8+sPFhB23z24+mDN69snNz3/z2pizDW9zQy+subeiaP1XO5WO'
        b'sMozyP5UPDmLoCaM8AsOeKLzlgUcC+sjLATtijFu7cL8hQFsEdzpx0yPgueoiufjN5GybngzycG7/dA2ypd1vljDTggJFxiLZ64PamHREbg7SAix3NVjGN1pTSZVBKSo'
        b'JgM2smXwFE8jRq2z4brQJAIL0TwkGJxbMXADi64Elgqx1Oflie7xmU/5syVoH2ykD5O4olBUGRsWS4VGwCoR8JnEZRYKEa3ZqKkonhgSuF6lSq1Cu5ayoHcCPw2LqDoq'
        b'q5iFyaHh8MpwgnuuUNWGOYKwKYe3kylMRDEeIwG8ioFn0mAVHSV0A+0EoXGJCaV9GcAPYuA+/0U0JnccaoQ7hABYwmUwn4lXoWNYjekNL/NY5YIXKODzVqOm0PCx6ES7'
        b'nBwFz8HtQtzqIbgJD4qbLdAHnhV8M2tg0yMVVMmTeg96dSvWqChMaReFU4kg5GlMqi8rY31l+J/1Y8hVxvnitEDXarWchuT40ZB0ErzjjdO9WT8a6uPLylnTeqcEbmbd'
        b'hOPjAO4WQ0YqudlJXD4X6C4uyZ5FeAxegDc6CkwiLel5HG4CUwRWWKRwWzy8puRoWBA6Dbeha05HEo9Ooxpi8AyAG4UdyFi4jEQ1angmweEJhpdYeBLz/6PwWgzdTZwe'
        b'UBCK8S5EjOf3INk0fXTUDLQvg+uk6gU41b0l+NJlVz5w7ctnOuzMZ+29MgNcKxui31zZ4Kitzn80FM+pTOH2l6LPMpgtepNZYcnWdz5UJlzWIW+sRWEwK0z6QqvBpNcp'
        b'LPkK4j/GBXEqOT+EbDVU5JMYvXR9Zr5Jr9AaSxRma7rgnOlQVYbWSGLwDHkF+SaLXheuWGTA5o3VoqDBfwadwoGMFCpn3fiBpQSD0KEmk95sMRmI+7oTtBNozIOCWHoT'
        b'FOTgHHJHYgFJlY7qcQ+7KZKjLyHxekIpx49OBXWKIjxmGKZuK7Ca8UOhuCv/7BmxM+fRJwqDzqwInq835Br12Xl6kyp2llnZsR7HaDtDFbUK0kdjFolT1CpIJCcBx1lX'
        b'uEKdjweuoAC3RcL+utRkyKSlhAHFc5WuJQDhucJzY84wGQosXTrSxafjDTpbJJ5q6xh8P78HbJ0X4VxwTFkUg9XNeTFxkStFKePHw2alDF0rGQ+3TRs8vhc96UIeBC9m'
        b'daEAX2f16o4UABw0wLhogLX7ZPo+wXpelzgnwj66niahUuN8lLV0Dc3qGnkhgAdcC4u/y9AjzXTdNSVybKYlzNmg+/xnYDbhO9XKe19pVJ/FaOWZX2juafIy72titfzm'
        b'e/LXag0J7+XOXtK/VvGd+p1Jl73fsSj+cvetu8DPkGnRVr59SvTVKW0Dn6MDX+lXZr76WVh1ug7skQak3WnxffW8NvjiPc3yO1cb1m5uqgjSzYjksiaAvZL+/9xwVclS'
        b'MZWAmeDGUCzSbqqChYCE3VhCXoik1pzBE64NRfURIQvQZSwErQyqWgNPPvkKlyit2KQtoOJmQLu4WQP6k3jQQMrLfRl/Rky3TZQqTQ6e5Rbk5MButxRSo2O/thBQ+Nj+'
        b'nWZGKEBFjJ1gC+t0PZU7Pl90WMiaTITM7YgxWBvw8RfooJtdp+2yZ7afMiIujJxoc8LHgAXGzofH+owVyAE88ZbjLmjffYiCRG2dje/RLXiudFTk6KixI8eMgldgi8Vi'
        b'Kiq0mqm5cxGdx8ZKK7qELvhI5TJvD68k2OyJFZRKWMuStY4rHugMvDSAavtbo+NAY+DzPPDVhHxVViSYAKsnxYIG6QkGaDQh8rmDHMi9Zf+vvHk5vvsp6X6vFwb5lUfK'
        b'+TvPjBbXMLfWTfuOC7v6B0XywZ4LZh1445fGQ0Vj3yyEu2Zuf3Vo6PSU+pLevX2Chs/dMhr9D1j0p8Dwsu3Han9drInclxz7QdlbMzI+3fjNz+Aq8q8I7YnxmChzhfAU'
        b'XBcfhg6iynZNki0BJYKqdwI2T3H6FYhXAQxmYGsO1gR+Y8nmUZv2pGmmfEtaOrGm8ZAHuiN2KEFsP4zSUhreXBr2WCjtqM65HOMKk/0t7wIr5GhH6Gp8Ce6C0G0dNvlN'
        b'w0+mLYC7Q51sXTbiUQiNqiNgVVLUWA4UwRrf8D5pdOJLzGzqOY5us5M3zs0TzFoWHoZX0VaMjOFkC9cz4fDocpr7C09JSD8ukB7R9dUgB+6ULRYl/wTo9j35H/yKBNyh'
        b'T/4z3kO8DShw3Zqwvb3lQmIwF2eyssEMxr+4f3IjhMQ/zvbtZ+Vwrwo0CdfDFwOq3alhRRxsNM9DdahxwRhsMPNAnMLA01HDaZnd5j4T/sNkY9GksX3hEStUtGR8K1PO'
        b'geC/yT4sfjdN0lc4p2YfOrtkHiTVoDrRU3LAaZgpOPEm3ZYeHYIOU1ccvDLaYdxiiwRVhsURVyOxTmh8BtoUSkwnWBUqU8Lr0+la9AvzxABbbAow/LvA9wK/D08DdEPt'
        b'p0OGS6WLQeSx2cUxpgzVuILkP4w9mZXK06NoYBM8sxhdwLIlEQMG9ybCVrSdwu6XM6GoH/iCdChqSlSA0CGbfgrAWnTB0SXlpp1lwwNpYuiyKaveAD9io18TFd3fLOSs'
        b'LgxjNCwI/iKi3PyuYU4/mljY78/MRQ5Mk/Rbmx84/FKqYPB7P8U0smDaFtnanNSZcDVNTFnuz0SyIPJnr/KywPxAOU0coLOCbwGIKRaXFwV6XZHRxMmz50sCuWQR8NV6'
        b'Xg+NEFpfOK6BCeZAdLauPCtwkUZME8uDFoOrAEg9FeWl707bFEIT9/UawiSwIPWGpbxspyK9P038dcAAMAt38/155bZ3facbaOKCSYnMQdyj9UPKc959KjOdJv7t6d6D'
        b'fNlUHuNg2aaJMqH1hmVv9DzITJMAjTYiJqivkPjO9GdH24Av7r1GuUmlERKLV9pmBXLfMiBZU+ThlSwkalM/WLiHLeBwYtDWUgdevzZQ7qthIwFOlH9m7unAL0kBKGfA'
        b'qm1eH6b7az4TGTKefldkPohnU95wd8HcV4xvTfO9X9L219dKe7N/XcWtz1pVyQ1syPhF4zONv7IlYvvCl3f33D0+6JOXRP9+duT5X+1//KjfGx8rhuquPXNq2by/TPZe'
        b'fEG28W83Fk/PbT78h6LYcf/jfX22flDTraNTzl9fulDWZ2PrF8/9+UD9jHeqT4XpWoYt19eanx+fhd7je/57bUNtzz78m3NXBZ3afOPvYU/5ffLsmS0ZY5+7eKTnv8Zc'
        b'ijqftf69Oy+/NH3iR4MnSsp2DAsteD3unzWTclp+3LRIPegvybWi2G8+t2qWn3n6jdOpESurF/i2XLpxJjqgZcXXUwZ9bn7FS3up3vuVdQ1nmreI/hNd9O7/VPT7Iabi'
        b'bv+/vhT9aYLlvbT1lparE2V/feWnry/vuZUyqddfUFj2/u1Zzw765tLL7x8sGCh6J3pGlVf9d8DnO+mIVbUjVlVn3XjPPOK7dfkPGo+X3Bu9YoH+xXOf+nwfu/f4v0X7'
        b'70/+Wj2mLPbLoH89UAVPuX8ze0NS9O3Pcqe+qV59MPKFPQv3/unzD45PvzY0pLSw5OPT8SvffuWzr+e/cTvuX6ZfvS8e9Yid8/lPET9uD7l09MWstwcmGzbtOP6cUkoF'
        b'yeqVsMVh+zNwD7oseBRy4C7qQPH3UoVimkfPRBAu2MQko3Noh+C6vj6Ex8QaGqeKV4WoRUAuZtFNdDtAcIDcyjMIwmlikSCesHDyRKeEeFF0eRhmHUmx8DSPrsEN5MCv'
        b'wekjqGcFnZrVKzRcGRfqONPPB5VzcOtT+Wj7PMEVtLkInY7Td3K+sOiKF7wgBIBs9BW5xzKtRc+0nxqSxT/hup7S98mDHB5bh5Q6BSaVtjZ3aRskZ3g2wNtXxjPuxyuR'
        b'7wH4OxB//JihjJjth1VMb7r5yJ/hOT8mgOzN7fxpT/uFZdlfxJyYynApjdaX4xp5slDQ5+ESXdBKRXT7QJvEYV+2iajR6CbK//sNWFjzrSP3dJ9CvUsDqMGXXl00gK9D'
        b'3DUA4kSPRldgq0sF+A0FAO1FW0Ix0pJYRA90A12CJwUneqsCbaQLVfFOD2+7syQCnV0AL4rQaXRqLnVqw3Nwf2z7ohy8lCL3wsIKbeAGFAo7+XtgqPnUP2JuqAlblqYE'
        b'uURN7ks8itmXREQ/2LaA5psRTLzTVyWYh+ce6jkSGH6cnsKbDxAZOHtz/9rJ3jBSPufr4YY/Xfx0nLRwxNiFR8IXPvdBFMtNP2/2vMqOeNayasvP//731sjLixQJP85a'
        b'XHh3o2rHssLXvK7c+HBY/qpXnmk6vO7VV0bcqLD8ae4Nv147Psw17SirH3ezcsfOBG+fhkgvVvf5Z/+s+0SnWvsyN+bToR8gydyvvwtdsWve3Vuvr7lfV6TJP/rGjQfv'
        b'Xx+/7+f7jfyIExFTv+EiVtw2KyU0xikpfLDrsFi0xZjY8bTYYgfL6DdE73BOTkAtDuck2o5Vd3rYSQU8jXUrNx0N7YBVJDQygawD7ufzjcXU05iG6jn3bInoKNorAn4h'
        b'HDwRlyAwgca56CrJgydvODrtmD9veJabBXehjUJUZCWsmwxrIlRq2EhCCKoTlGLg049LG472U4DSMMLshTVJDt0nDO0a54yO7As38/DwErjVaTgG/K+zicdmIk6qpUwk'
        b'xJ2J+JMAKpYZPkdOyZwlOxJZYVOOmLINEzngymG8kwO3lD3/b8O9yUXSpOlfOzlCK8a6EzQVB9fhWXRboGjtqHCyxu8zlstEt+GhblegyZ9ZzrSHIemYJZyOXcLruCUi'
        b'Hb9EjP8l+F+aBZZ44G9ZI9fI60R1wvFcZOGf14l1ErrdxVMv10l1HuuBTqbzrGOXeOHfcvrbi/72xr+96W8f+tsH//alv3vQ3764RuoQxXX66Xquly7p4WqNcbXmr+tF'
        b'W/PDz6TkowuoI8d1kTPreusC6bOe3TwL0vWhz/wdv/vq+uEWejl+9dcNwL8CdHSfs3Jgm3eCwMgTtUZtlt70kaSzU5U4/jrmUdAYjg6ZHlXCYCYePupm1ZUYtXkG4mwt'
        b'UWh1OuIGNOnz8ov0bl7FjpXjQjgT8eQ7vJaCy9DljaQlwhXJuXqtWa8w5luIp1VroZmtZnKeeAcHoplkUeiNxL2oU6SXKBw7OcMdPmFthsVQpLWQigvyjdRFrCctGnNL'
        b'OvoVF5gFVzNuSmty845SH3KxtoSmFulNhkwDTiWdtOhxp3Gdem1G9kMcv45RcLQaTgfTYtIazZl64qfWaS1aAmSuIc9gEQYUd7NjB42Z+aY8elaeojjbkJHd2dFtNRpw'
        b'5RgSg05vtBgySxwjheV7h4oe9M+2WArMEyIitAWG8JX5+UaDOVynj3Ccyf1guPNxJp7MdG1GTtc84RlZBjXZ/1+AMaY436R7uHeInOmLcZ8XdoI5t56VsdQt+nD/EEfx'
        b'mH+woavP2WiwGLS5hlI9ntMuCGk0W7TGjM6rAuTP4fd2Qiy4vvEPQ5YRj9/05FjXo65+7sc4HVKsFg5KroDNRrcNL5Fow8M2vKT0pDEJ6DQVem4qSHBMWHg42hSB6rzi'
        b'GDAW7hA/rRzoONl7NNZwKshZvEkqsuuiLhNeT2KAH9zLYcX3+khD2boUxkz2Pf9wdR/ZXBb893v4GhZwTxNDdkz89X76fU34wmBtnJa9ENQ7sjgyQrfszvmGpq3XKpQ1'
        b'lyquVYysUW24tqO5Ytj+yRsG7Vw7ygusW95jnzwAGw9kI8MkcqKtuzBul9czZvD5aA8UIv3QxVFjHPI4AV5f6SaPB6ELVKqjKq88T9xjpUt36IXqyRHjvHSWIxIbnUUH'
        b'U0NRfYwGjOYBh55hjOjKKsFsOFQCjwjjgLWIw+EMPb4Krl0M11EzJhdumIRq4lUSbAicJccEx8OrgvkDd5XBS6TS0VHwRtEYDkhKGbQbVhUI68A7U8k5sLh/lYmoJiVB'
        b'DLD6x6BrtkmPDGZz1/PTDBhL09I6BwSSj1xOd0IQXby0d0f0DXeWE0R0sxDObNoGwCN3ODSzQrb2uOUd+LKOdXr1yl0f4O8e6vcwCB6+F4u6ZMBK57GaShJy7FyqamYE'
        b'ADruyzKZ8WUzBoVuyerSpHPT1oOgh66A4UY4XX7GkwAlTXNYLaY9D4Go0QnRA3+3VTDnYlr4kzVG2KxBZ35oYztcjYWRxpw6XDeLbhm5Bsy+VWbMxZWPB8R6AQjPNP2q'
        b'AoOJSoiHwrHbBccQAkd7CSKCOg98x+adbJ0ezEfZuuOcUbvIja0/2u3fZfdah3Nc3BkqIeQMeEg2D9Utg9vxE3iJnIV19SkryZqvx3z1FGxAFzGUZaAMHZI73hQAa1ah'
        b'mlgaPzWKx4yhBlt/59i4nuiSYYL5HyK6hD316pn+NS953VHI+WKv8dmKuqMi/6ErI8/Zlm28N9r7XP+6orBdlhu5/ZKjvbb+FNtYE6J6evfV7c1/X1whru3za+q9Pf/T'
        b'syJu6qHonN3LxtwMG/jDi3VvTvENCOLefVkpEzaGnR+LbnXDKUWDqW3jMVjwm+zKHUscrLGCvx89Mz+ehVWjhQUBdBlukLqHlfigzWwJbCyh3FEWD284vSZw2zRezcCW'
        b'wbMod4TPoJNoV/tiAa7oGvXI+Fno8+VwK2pwcDnC4vT9KZNDm1Gd0HBNHPEB1UeQ10bArWX8WAbeQBtQqxA8eXjYINeB0+hiaiEL18NGQJ9JhkbHu58oiOyAzR9cRDl+'
        b'7zURCM/Mrhh4JkaQYERyneKwAX4TXe1wXNljslm9McNUUmChbJZMvRubHSSnwR0yGhNJz37twuocpd23jjzeUYSOk1/bee0RfNnXDa/99Ld5rQOA/x+Vp5nZWmOWXgik'
        b'cKo7TqLvpEphjehxtSijvvhxlafuT0fkMf+iDpY4dGYGulrgpuC4tJt+VsNu1ecC8b6+7SWvlycGTIv051/fdeNH69iMQcFfjB5ffXpQyGvBLRt0xz94UB10Hr7yySj9'
        b'e738B/h+cnif7T8VVW+MmKQIWLJYHjhSu2HZ6V+W965s9bix76d3xK9+8U+fpl3+xjl/VnpQNB4H7Qs9UCVVExyaB6yHzwgeyZtzn4I1SWQ/LTwZFswAdHOoN6rj9HAj'
        b'EHaJrYPX4I55RAvsBtVrUCUl32Hw+ozecC1xSKBqBvARDLywsgdVsmAlOrGSHPbjoyHvK4B1EQ6NEKuDkeigePzkBcJWi82L4FGi5cDT8IoECGpOdW9BkdkPr69wjuNW'
        b'X6d+lAKv09az0NZ0QQka0z/KoQN5raIlUVVqiYs3pI9wKEBoA9z55CTqk0ERLs2JHZ0jl8knSkbdkv5M6YBOBNKpsMNxsfOhhGna5aJIcjroiW4osq0DRT6iQSXXJs7O'
        b'N1sMujYPjPcWI5HxbWJB1nfZs9SRannn/gIX1fI0/unhe5Wc8U8zmE6mOvmbrtMRc4dQmpvCIJiJLnH9UHIVOiEQawy+j53lJPp0rTGnK8m6qNzRZ6FksvATFw6Otxqx'
        b'kamKndVNUJBbgJGzJDGpSbEOAUXK7uA16S1Wk9E8QaGZb7LqNSQuSDg1QRem0MzR5pqFNG0uTtSVYP2FqFFGy2NwHVkXrsOpDc8vncKbyRlQksDxX2lW3Hn97rt337p7'
        b'vuHa9qaKporxNa27WtMObW/dOLKmeWPTpkF711bdbRzUMKhSO3Jm5M76+l80Mcz56D+BF5Z7qf81X8kJ/GHbBMwBKINAVbMdPIIyCNkaKvMXLpgO16EtHSgfG1WnKPPo'
        b'mxUenxALq5ISUXVCOGY6p1IiVGoVC5SwVgTPrIl+ciL01up0afp0Q4aZqqmUBn070uBMQoGl/TuRQ8dyDqNELMg9stnYdIJcmjuKTPc3DfBu2QpceSmBnsKXS90Q6Gsd'
        b'CPS3Ifq/QoJYcH70VHckmELdWZgKjQLakWA3N1p0c2T9v0eNpFjsvCSF4IKyCB4rai5kGozaXIVOn6vvGqH3+HTYA65kKR0e/6ikOzr8MOS3KVGgQ+aFFV5J9wIwHVIX'
        b'xCXUCI93kNSECm2lenhgsCA/98JDrBsZoitD4YUx/hbilhkOL6aExqE6VBcRD+uc1CiQ4tQMWAfrJX5wJ/fk1NhDcIs+giBTKEF20snCuxR1iMTTnQjPdMZFZ+fw5dlu'
        b'6OxWBzp7ZEOPeOUKYwdur1z57VOzHXLuQXo3FEbRjZKC0ZqXjqkKY5ib/7jdK5thNZkw388tcTOlfy/y6bf+A9AXCR18f9FXfd/XLCP7zCjijXyEAKBotxRkHfZ8vniL'
        b'E+2Ow9toXRe0C+yrj0abqHU1Au2DO2ENvPa0uwBoQjX0sAJUgQ6iG8T4IpumqtwwD25fRsK0p8JrEkUCPNfp1Trd4lpGvtVocZtGc3e4tkTaHa51Kap2hioWPJThC24H'
        b'inet+PKnbvDunPdv4V2XRv+X8Y5YRcaH4l173PJj45wiOIToZAajomhs+OiQbhjw4+HglmNzhJdZparyvtIsO3TjyXBwFMiye558+zsHDsKbS8UuDERnYl0aCDwA11P9'
        b'f/RccoyEE/8mhRMMbFRYyCYwA7LTt6FVhYV3RL/dswn6RUO7GGfesOYx8M+XjOej0C9dOLirEyZ0LungdOcfjnEX8eX9bjDueAeMe1Q7yt6d9zZL0tJ0+RlpaW18mtWU'
        b'2+ZFrmnOtZE2T9eeFIPOtJsUIi/DMB0kl0PA4YdtkxaY8gv0JktJm9Tp1KRxD20Sh+OwTebmvCPuBGrBUC2JsnBKT7SLgrvid5zF4eYJ3IwveWSo5gCy25r35Bm3Dytl'
        b'/L1Ycur7L2LuId+8nyfOJZczvt7k31sqrGXcQreecouPOADr0aVEbMNiK5QFwXCtaA20o+NdllMIkU8DjjM2Oq7kCnHCbT0d2z4cs0dPH36gmL2KnJVIvJcZZE+HyUh0'
        b'MjcdTI3txI6zabrkGolO3tGb+PIx69qBzjP0NVQWVBNKNqBvKXUewNDi7J1z2SJOJoGbRvtaZxLC27wq7WExyrf03YQpd45Rjp/ZheN5OvkF0Y8cof2g4zsx2w9v/T1v'
        b'mSKNdPW/ytVKTgj4k8kA4Qu+Y++v2rly2koa93mIF4N+0X9n8LTJ30v9yOsTkEtCeJqzJ4nuBV7L+nV2X+W1nOS0kwNP5FxPXRe8W/189OjFdWH7ks5MPDphef8/hRxK'
        b'/znsQeIar8/6epXdWNASvH7mmLjP1SXTP7KFTJWP9o++OnLD6BfKihKjh60J7jkxeMGqqZf5NL+jBecGpqe9b7goGbzgiEYfHZfzqsfXsZNDvXpnp5pE5YM/m1Uk+9Jc'
        b'VBDc+73ZJz2DvK6v+RVbBnesRUI8LTqE1saSrXIdvMNsXGAP2tNefYS9oZELvQLM8wocIbwyx1tbjG/6Ji8fLCS+FdAbhOEhifTun7c5ahagm7jGpPRANYmqcHVC0gLn'
        b'0WZoU7wEbYbNJfh2R/JsuE00DMD1wz3I4U/wiBBSnCgiJ6ooIsVLlqfk+AgN+BqF3auRw5dkKOetEs4lbQxLvXskg9ILo9tlUOhLGDMJ/vf5quewume8uJHymcqX/lUY'
        b'EN138fCJOhGjfLN/SlviB8FL393zdemc58cMHqBsiOt1eee7Z77blTChUfLzszPWxm3cOLHPgvNvH5k7aLnfXz+y2WL+PCet+OzQ6VfWv/z8hr7LVZeLj9/zmaAx3Xna'
        b'sPqZOT3T3o366ZugxA/ez3znuUV/12QlrB5865dTm4ZvPTRUyVP/USEsT0PNcfGdXixzAR2lzq2sALStPXToHDzTKXYIbooV9Kj16MD0UBV5Y6dqDhlIEfBE11lMStvQ'
        b'dirDcnOHhKLqEOJbo1vXtnqPR3sGd40v/72HxrrvvjeZtR28zWQXpZsMs/A0JI+c1CxlfRkFYaH43nTbWQ15fzVZ5HfTm34vWM2M6a6La5EGvulG6DUq3CNryMrxCnQg'
        b'ODREDWvdFNO+cF/yZB6emoJ5cme20/EIni5sx3UEz+/aV9T9ko/MyXLujfR0spwFk1c/N4eynMinhFDzabYB8vcCQ8q2CyznxqzJv8FyvJYfXzxh4NLiOOv1CccWzJr9'
        b'n8U/9P21z6vj+pSWhGrnSiU5/n/s/w8WTf7fZjkF8ZM9aVdeHMgln2Po9oLcn8PnC9R9elnPPltYcj6vZlKUrkBYkaNPdon5cIxHdCvBh6lLhETpQHH608Kmg7D355YC'
        b'R0h/r6Xe0Z05GdyfbPgwIoczk8OIV5zsqXql1QuRTSvHV5y/32P9xfdeDG0xfx4ye5mSmYLZwkb2g4YP//anr8sVRf+Zq78/btKY6IHvXp06+Vzy9bKAmfEzX21uGnX+'
        b'3uWQ0nfPHhu3+pn+AYnm2tCwmvP7/7ljFfxqzINlrbZfxuT0v5QrcrxUqngerMFc9mK88xXZ0uWsvh880kFZ/N1H7VAy1OnbyXBoRzJcAyRkZd1f0GEoKcopYZqQq6I7'
        b'vwMC6KI35CCPzvS2rl/nSLZV01mB3GITndSmKfTlYZOoV5e9fuSfHgu6EFNhpUg409zGHASExprYMpbeczoe33MWhjyfBRqY5d7L2DK+jJx8LqoEFpacyW8qKPW2iQ5y'
        b'OlETUyZaBIwDyLnjOTJTrvCuG/qMvAdHJJwzbrxjI+9biaR1kPLnbZypFucSNQnvvBHTNwf0wS2JyySVjE1CTkfXSepwfpt4EihsNK6mZUUV5L0mnOlFck4/hl+E4RTR'
        b'09hJWWmXslJc9nXjDFpWeMtMZJeS/R5WsoEplFWKhdw4BdjI+wCChdPgHW+QSbYBnUcQZis2QemRqTEH1usL5piIojb/gchqyVRFm4jaipHzWTK55IEpglyIOFdKTFkE'
        b'6Tz0Rmue3kTeFkDU5TYxOf1bp2+TLzAayA3VRYWyMwTcaj+Xsr1aeho73eJEjqQ1jSQ1MSufcDd5m5y8nsMcJWy19eMc+z3JeeVyx4sDhFdVkJdOyBwvqghwu5M7vqX0'
        b'ZRRShh7G8zTcDi8K7+IeG0LOxCFR9h5wG1AM4LGyuhnu7RKG4DqNm5CBDZilOmYeIK8dohPAuk7vpwNpmuDsBDm11/wQW9GLdi3Nkp+Wm2/MGsU530PJEZuEvj+ydNVY'
        b'AUpsjqIq4XhF/H8M7oyXgOFwg6gkMbfLC2JckVqjKaQ6JocxyYlZoeNs5PU+jI4/CMgLYzDcogDQxNiY3oAINZJCEUfs6AWNmmCHraK7u+6xQndEpZmG3Fwl28YY25js'
        b'h3WN9Ij0jHZxAumazDFt9Nh8xkpfHG1HFxXE7sY6I3lbM3nlM+ku3NRXJQbDB4hK0IWpj9j4y3S78fd3vMWOca/abStm+9a244WF4EMAoqMKNXMmePQXEm8nP4vRAAR7'
        b'zdDE7o5xbDjKnEhPV4kZEqEJu1tWBgwFF04I75Cofv+zrzTL6bFOlyqaKy7temPDoHdObm/a2FQxaM/NmFMVVibDa6bs4xnH1O/MWNtnoyjBM6haFN5Hcah/WP9Xx8hf'
        b'q1Um+E3zO8QGPy+NGrZhsTz4cvn4DfpBGXST8IRjQYXxf8RaKfH19klEx0LJ/mBYgS459gj3QPvpik1vdGhZaJwKVcJ1aK/7W9xOon00XmJIIYnQC1Ojqp7eCWhTGIMz'
        b'nGLR2VCsiRIKmIROAngqjgTxoapVsAErpKvZwUvVT77NuEdevm78OOGFCGk6Q5bB0vksXceRT1JKy4SG+zCmP7kqqXyc5qqczdGCMzlnA+Vun9sdtg+Tl5nCQ4N9cA/r'
        b'kmDraHqyMH0XTT280IecRUpHJRoeF68OR2cezi+I5itwCSLcmoTXW7DqNpHWnGEwYNX2BeCUt0M6jowkW78q15BZkkjApRETnHA+YiND3tFMD0MjWxhP8dhO2MDqxqDr'
        b'qNrj4ZCQsuRlH1To+ZNX5BB4yhzQUaWVVZveAlThnu2E6reO6PKwGh0wprRzL6J9WOkR0PvhIbKDss4FK7qxkIJLDkfbh27CJx82Cp7p7YcNmUf62NHCe50Wuw0a3S+x'
        b'BZ2BN+KjRsVSKw1ug2eIsuYziJsIb6DG/2LUslxg/fmxxgyDKMjTFZ3GjNBdZh48SIAkyqS+Fw0hRWe5keg02tglNM310jKyo1XHYMZO9CZgCrYQts9VsFiXAGWc8CYj'
        b'G4uZPFsotbEFUTaGvFXI8SahtqGRI6NGjR4zdlz0+OkzZs6aPeepmNi4+IREdVLy3JR58xcsXJS6eIkgAohMEjQFBisFhiJMukq+TSysXLSJMrK1JnObmJxkMWqsIP89'
        b'Ond+1FhhfvSk8/RFvJzghCNCnA7BoljUEB81VrCmZ/Whs9Sbm4D2dnpXcodZkjvQRed8jw6ekw+cbWOm9NdukWXUWGEm8t2QhQbUHULlsIUAQeZhHrwiTMQRLnJc1sPP'
        b'WKTva2Zc72vG8Dz5uYoAdPfiD15NXXNRUz2cO5rRtgWJHnPRJdiSgi+XUrxgPQuC0dUUMZ8XgnYawgtfFJmJVsacrPpKk4oFjpbJkO20fzzjefoS8hEf8GOe+0TJUkkx'
        b'QIR2hapiUT2qiZAAj1GeU1jYNHYW9W2kBQXAVlnn/Yr56HLZw963bDDnp1kMeXqzRZsnHB9B3zDjzstLTR+7Cm0AD3Om00yWbnl1fYdXLhOVDu0JjiNnZ9VTRQIDqgqP'
        b'RbWWBBUAw02iNYVo25wuUWcd/YycI+rMzcuIZ9Pzv4nzJLqAT5fZ7KGmL+y1oRZtPJaw9aiWx9J5X2YfVoaOwpNUgwhRBYAwMM0oU2gmbZpucTjz9qFGeHpUFGyNigSD'
        b'gUTNJKEmuCcYHRYeH1HL8cPLUfASj5/CHQy8PQBeRruC6Jt4o/vDI2SDfxY8AcJBeCQ8S1sakhsEIsG3jFyjsRlXDhEUmLUxwSAZRI7w0mjYysEFwEreei7Xa+AFlpxK'
        b'2EoOvvMtoFkbozyAL4iWMhpN7j+XKoXypQvJGxROTPSepsk1jPDGaCK8o3gtOgGPxsfC03DflDAx4Psx8PxktJ+WGb90Op7ZFwu8CjRRci5DqGjr0KmYqn8c7xWp8Yvx'
        b'HickXtQQ9SqG91Bowh7kZQADdyWWNxMSlw58Y3Zyaxw/XZ4YdWHUM4WXbvX0DI2/fed2S/LdqBc/ggGntun6SAYtCl4Nvzmw+9P6rd8OWLtjR+/0n96RfVAx5nnxtmOh'
        b'HwfxvT+4sOHeO6nTvqi53PJ5a7HXsJhlL76de+a5NWXDDQGn57eWD/u4egaXOBGt+7hu7vQN4/cui/3+jbcHLPMcbGt58JbPpB9n9/jrx3duRy8fcvroh7F/+bLEe0Nc'
        b'8BvJsRM+6vPq4j/cKuTOJRqOLLLvHVj45YoHW0YbfP96JyDunRMllfsLmt+7kvbB3UGT7T/e3fr5mgmbfpB+VXz9LwPD1s7Ur7yvFAsRtCe1aKO7uyHBTw+vwXOUXudO'
        b'7xmKjqEDRLlzU+z6wx2U1OcugpXOrdBAPGsYPVqtdQpdpY2ToeoOkbmsajSskqJNwu6F7YvgerJ9YSXa6raDgexeQBtswmnDO2AlrCTTywN2JQMrxk2dvPIJTiL/X3Bb'
        b'ehVgEaRPwzwoemzkSMp9JnTmPqt5RnBeYqHDyZl+WK8UszwzmDCU/6+9LwGPosoara2rl3Q6IQlZWcKSkBWUTVH2PWQBBFFBbZJUJybpdEJ1hyV21DFKd7Mq4oaooAOK'
        b'CoKKuC9VDo7L6Iw6qD0uz2VUnuuvM6ODM/rOObequ0MC6vz/+9987/vJR3Xdqlt3v+ee/VDguWx6xoIdqh+aFRjOPaKOhja13uOmYHpx3ua/4ipeUP/McYluQLCu1X0C'
        b'vHU9uJuoNtVyXlrp3LISUrJGsHfolDHTtK2nSNxwXtKuXaRdQW49AMnapz2KR/EQ7YlMboi+Td9Ub5oR4r8eSkQXcYjrYOjECNBQGO0ujBSjJSipZUEL/JfgjLVkcxmQ'
        b'KwvyBIUdPOnpGhLpsKiI5nfdIguOC7lEtS4s7YDnQXGnACUzZE6q6UW6xuI44oKj2KYZjDANQoFZFFjPiGza2CuyKeEbJzhIMC7PzSKXEIw1v87bBvQG0+7pKyArQ3PE'
        b'qKWjvd2jqnNw5iWifOWoFPCsDgD6gEX4mzo9Ubvfg0pHAYw0uqpJCVykfoz5RcXTO9oqNBFDqqqfxNasM7Et14qmvqhoM5gXEj/oR0lEF3+EVmt7YAorMVT0fKRG5pOP'
        b'xeoyPiWLG6zfIukPzKvshSrGBhZnGFFFwmg5wGizidGGIYthxnfgUMMhpYg41MSGE9Q6mGVBkSCHGBQx2DMGtOwScTaphKXwlEIu43vILS7iFIvBRzhWNPH8KatbvSNL'
        b'pxDa1+RrnLRs6IgLipZdCNfSYrwfWTLl/CmTCYM+io1l/KjfcETWIRkSlf2eWrX+oqilUW3raI9akBkEP962VTAzz9LWjIpQS9Tajqpaqi9qgZGED2xmpSdDyFPRzSJ8'
        b'7TYz3x7jdoqS6XeAQlMymCEZxGFE3yaR/0LtXvQVo0XmM/kPOZe0cqcXyw3aY9r1+lVyD8Sjh+xxK00H4ONCBof4OSMq1ADauajD8bqD38n5RwYFBfD3IOdGCxhBnYxX'
        b'ejMzCBi/G/7P5C5I6yJCBUoTs2BieG7FXMrtjeXexHL7coO8uonehY9/ZzBHpJoo7zgm5OfTbMDw0XL9mnZBoLbJCztD8ng9rTALnpUe70k2X9TZrnoCaJ2Jg3x/fGyd'
        b'RlDZVJ75akBBUgZD5oov1u8oLZpXXkzkrbaBjTBfPwug2G2WIqd+04lNozHoclygDlCJWyp6JIrwB0O71LJVbJabrUtt8MyiyPTM6rE22xWrmQIs0AoQDQ2jbUsdylCM'
        b'FgjpJMV5hX1pkjLMSCcrLkg7jWiCEkUZTFFS4ZvkHs/6KWnwzBV7IinpSgY8SemRq7+SCc9SySCaW9pPGR4SgZJAk2f70jSlgFKDlMGQSlcK4RsZWpCvDIF0BsWa6E/T'
        b'NiKaNAtmxeMLTAcirMe6M1mDi0z4Gue2U5RaTpHMeyJMgDLku2j2j/4I/47xZwCujwKcPUZguIWxaU7YS27amxQj299eW+/5bYyyEjoHJDRt5PEZ+yTtqK1IPSDZDSuV'
        b'8QHIBE1QJR5BbKC2sS/Tr6i93Vvb5HPD6xcTmtA/sQmxHL3qFsy60zhmc9bmMveiYX22R4ha3HgM0J7o0/gMd8yrccKyMzWxbvy01/TEqnXS9OB2N7YjVMirNozxJvJ9'
        b'1/RGvJe96JwYR9gbm3aC9zzjApPgYS6KXFjA2KCoCC2COlZB1oEwEYPBwu5pkf2ZiiUo4i9AfB5FKvDEyr7K5My8Co/Bk3cyTrKt5hg/KsqXHBNGjoIpI9+2uFNVASeP'
        b'v/iY5eKSrgI/nrMs6LYDqEY14F/VBGconrmmldJlnHHCR/n2E/Gc3QBo4Bj2kKP3t0RT78qwhsJAO7lCGt+Z02MZJn5T08MDppg4coPMRUgjF2B8f4HCRMOmIVYKj0GZ'
        b'07BfFn8H4AyILvgUU3sQOxB1xJb7CWQCagZ8/4mJqWDTey4bLPE/0cgr4o1U07GlViyw1utV+/MnRJ6y4NVnPZqUfnyToIQ+YQ21CiNChGEphSVEN8K0sJthCW4UqI28'
        b'2UaMgR002ZB7+KjF52+tbYfm5sSaKzNP/kZoyqjVw9rxs9SQ1Vwo4SvRMCTlWGxyvjMtsS+s+BMP8CmsK0KsK0KsK0JiV3C4oTMxTlQ2T2doQkea0OVQoNhYHFPxksf/'
        b'TIVqdQDk/FvPnqQd1xNWfq9JibGW0JVQGFoaFqEnJSZMUPMRFWERrLugN4gP4k4OCMZSEmM7W4SdPZUhB5Kaih1D0SHrXZLbDThVU8DT6nabp0UV99POGVUMEP6PmLCI'
        b'8C3EujqzemzZeOEnnqkLExfdyJP1j82VryQ2r7ONeYWjkOZVNOZVMvMaMZakGnUgb6Kr2WzyaCCw7oS5htHwmw02Jzzm/vHnTXg+j7ioyUkzxsUlOMiivufYxKr6idii'
        b'Jud6MaumryPU5nbXtbV53e5kKX6CZvSsjmUgbH1xj9kwqQ4Kwo48VQpIzjUgsssjOrsdzpnrhU3mapoNQ/MtF0MX1wBgbvIFoimImCueem8t0xRF0/NAG5MGm2cDfqYO'
        b'w/EmCfRxXF5Z9WA8n35SbFk5eeFHCf733DEs2+w+O0FLKj/WCYWWjSJslIgk4pmegok1SfWnjvWhIR0LDhS1e1bXezv8TSs90WQ819xAX2Kt/m+wkfnQQZ9/0tChJG0F'
        b'yDac4DKcSl44JswuFmHvivHyl95dVAvhRX8pAR4IP8pCz4MD29QDGuBQxMiQl+DSxKHwAGl/wAYuZB2jg0SC9Q/U+06Uc/M53PlCl6VLDlqCQosMdD3uFUsOxhAS/Gex'
        b'+0YefycabwBmyAjaVziDMnsOd1yzhOoWUNMgKM/aZYOa5aAVarMGbTi0QWsWBzlXQk5rlz1oVx8M8v47g6isYYf34kTOJwXtiLP4taDg1xRqfTN828RWlGTIsHGLHrMM'
        b'Q3yr2B51wt4ASrLJq8B0R62BNrfSVB8gLQY6H+CECcDaqovaMSNuJD/hmYz8kXli9NDZ46hv8/mZKV6UV1D2AYVG+XrVgsUI9Qpz8EZI8ifcCQ/XkZA7F6eOIgOSH38H'
        b'eaBlPvkdfBrtcpn0exzkxV867gA2OkEuERAvpr1YLMyeXczPLs48XhuYevOw2Rv1R7N9hF0ipY0ENMMQEBeh05+Ghk4dgtAEjtQheCngjeVHHUkIgfWzmX4JEbGwLb9B'
        b'6I+hxW2iTRJ4h4TuvRwS0N+iy5kqpUoZcoacZs1w2CSX5LJQoBdtn3boYj9GIt1YrW8sXTGvrMbC5UzVbtfD0my9u3JxMU/Ryh2jtMsSDJx0imiJXxTL3GhF36pfKy+u'
        b'mwCZEVyt0q7T9lfGCuW5pEsEQb9Jv7tLu72XCAhhBmkzuWIwIshvitEqfDSptbbFY2Ar6uA+oJTVmNEJcVBLzbhUv0O7y5/QDId2i6Bdfqa+/sLMPgVH+M+/mEuggVMp'
        b'KiGqlgPFC7SlBNQrz1yALWXB6oUG0aB2ZXQEBnmsilNJhl+b4lJSrkBHYuy86Bd1zuxobV1jtLZvhDkmk2QkDBy+fAKdycfpTMZvgKtIvAdJMSlPlYsdrDxvUAtwUuLW'
        b'IhKUrd1PaODciL77YqgUbT+ZPTueTkLDhGlxOCnzg+B/Z//EHv0ydzDMD4l6Bn+CE9QOmAprypzYvPKdmT0qjGU5MbJmCDcJDUkMCW7iVtV9LCiGgyE0c7vnJVSefVxv'
        b'Y5lOXP1kmkqFB5rQiaplhDcCvFeHh2kgkDDvJunmDgH5gOponMgeDRYToDHMFE0kjRohTIP5k4rMCehUx9EfG7HjXMSM66s/Pxv/Idx8dKyuvmbQ6nZ7PT63e0nCEGYc'
        b'VyVlODEPATsT4BqZssBFDB5IeLycCOnCd273eQk19lqilONn9BBJqdkn7B3B8PNPUg/D7rDJjuPPEdxL6kScvcmxc2EKXqbFDgc6CE4yrRMg02RzWm2iQ7aJTjHVDpBf'
        b'JC7gWWev8RcjuNb2BuIQUH90MTdIe1jSr18+7MQQEB2CmRBwq9gsNktLLR6mH4Y8PskjNVsBbTNSJLVH6GhbamNcOYCIDELaibvmIOhni6bNr2v21AfIEZ4xTL+QeYQL'
        b'QLWeAGAQSGuITYjYmdW7vl/GOmogWHEyxlFL/MT52RDoIhMCqZP43ugoLoi2hFU1qI9OnAzw2MxaETXoTAtwBgFG6Og50CsJCNIWhzqe6fcSEBKDJJboFmTuPJbDAjlU'
        b'QwOY3yET+adALmucBNzJs9xmz1gqQUEwTuABQpNurvOoowJIhdVMC5ZAGe6DqGsaoY4dAUM/Nk4U/xz4pkoxfpVAaq0ZBOEyTzJ8BkmZdPzWnB5DWG0xZG98z50aR9R6'
        b'NSuOj2E5y2P7MwETc4okAdF365F0/f75+rp51SP1yAptT5W+vqp6RQK2Ml27wzqsTL/rxBs1N2GjEmJCgkRAVgzj1Wie2X0TLs1Ap51VbW0tHe09JJkWY/mkx/aecWaF'
        b'YTqNzQDwPi8GmiwMk5cCa9o96s14a4/x5/o8U2Uv1XqZFGOG2fjOoSdp30j2QR9GeXNju/G4zTMLXnSZmwcAIfp10LemZsXHuUq7OzBqVBzd1TdVlI3UHyTN4M0jy9Ed'
        b'xwqHvk27paKX3CnGHkGZOBzjHDE8BtD+4hn5F0RBHgydWhZGApALy0jZhjm6t5hcxGP/nEE+StCCuL7DH2hrber0KPleIGbzSQKv5hd5AqrHgw5P2+Lrt/jEzlYp+xno'
        b'5IH8vKAJclOjr02FOuJc0/xan5KPRDT6pKhVlCYWgSq/xCCCiopL8hnZ3dMsOaEJPauo9XrbVvnJrYxai9Gj0O+qr9z0spJv4Oz+nsUBlUWCSfHc6irYQUiTR5MS6iCW'
        b'xC+NmzYPZj4imVpxNubHi6S+5N1ok7Z5pLZe368f5LUrJI7XD3D6fdrD2h7SrLF2lmrrtc30mhP167UdPn7hmfrGXhtPNjfehQkbT4lLrOQGC8nK7EtF0oiS4SREOZkN'
        b'TkmJJGOiYlVsSDsodsUBtIGcIB+zLbXSeWmjZeKKOo09UQ3kj1ozu5f7ktiC3MGhclQTLDSF3y52STHe3XAgEPgmVG7kGnmSUSBJIajhGL9uclAw3gD2mcMBWSEhfyAo'
        b'+n14R2kpB0pHjgT0hXH/hKAwE9ULLPCdxcxD3AnV5OQ2Cw3wfBPPmweCjMxz9JTCuHun4YXQx/gzJi2NOtzEvHYja53ODUSXig1HMpQxk1iD7aqnoWm1GzUmyYYiKvj8'
        b'P48liAXukEyDIADN8PdP2YKrBj1fS+QBG3UHUo1wfzHZF81FnM5JhBFWLkEZ5C6cEjwrYTk0SjhgyBziAZNFnVIYvLWMNYRKAP7xxC6SiNEzICAEJVQUYAJWxboRh3qJ'
        b'yTjaISk2OItX0xe4iGhCABrJ3TDRVMI8eO4A0H0V5mFvjOcEk9AOp1tgT1YMCLKTIqkmalmEwqOoOMunRKUaDCZuWVLr7egtW4xhS0y2iGwtRWiRE0kV2OILcZ4WxY4L'
        b'vi+NVnIx+TRqLZCnz/KeY1zf5gOYEiDQ5E/UMmH+P6FIYgTH2chlROgi+49gkcGT8lM4PsalQqwCIAudXKLfsyJqaVMVj4psTn+HN0CURWuc93QyxQdXz/YdlEwrT950'
        b'2OoQHLwgoAG8/INLdAgD0MDMgXHdT9LPXuLHGAcVjYkacevh6hnfJQLeRepCZMVVhuuLWPLiTjbbtqAIB7hVtaECCj6lZ+wEEmqQskEuK2DDHphvm7vBi8ofPhozk2+K'
        b'1mXquXg57ydwsPPh/WtxGpO5q00jFbDjd45RUZ+nK60qNElIsGWDaxD7kY3SLeKGwJ7aidrZ8I6JGuBtgO5EuJsbAGAUFDLhTL6cJ/0MAFo7ecJyYafAvlCQ3elLNZ9g'
        b'HhS+KhZ2B09gTDM505iHhK2C201r7Fjm2b4WX9sqX/xYzR9a4B96TL64wI+yWFktxQFLoaXH4JhaTZQdZyC0Jq+FVtn83nRFNNntQ2UmdFkNBbyNw5qZsLBSDQlGJi8L'
        b'qXxnbs/hTfy0F3TCMSZO23IuUdZJ6wYxF8RhBHbXBHgUU1gyLPIQ+uAXZCcYlIMSgfuSgMSEW81wFDRAKbcICPRN7o6s1vLG8lCX4oV2IQl2gFRH7++AglsTeE82k72s'
        b'jsKknTGUoS8Jm7JvXnAd5P80TgbAGInI8WWj1Qt8G1WLNbAN7H1S50tjDacu1PVE/H8WdhInBqrg6+2mDMUmZfZPHQykuotUEU8frt0S51HqB6r1DTXlgr4pnRuUJWmP'
        b'Bkb06U0c/1Eg2xgWkkJ0uIl9MDf/Ju6Bb47HO5BcMLAO0sZBfiXjeqRGbVVt9S2zm7yeGhVpgR6YRw+diHkcY9ky8tKfERAUnjYeI6IFekdyz0xkVcKSgquFGJYyMS+t'
        b'aFfntsWkgsfSMUxvvtLmMRz0Iy55zFrgH4lqfjhZl3EkAvZjPtpVUWttnR81EKI2UgVUmtSoFXXo2zoCUYu7lULRUPTfqNWNOQCTTlCMiEqYQ23pgxbHhfDP+JpyEnqQ'
        b'RiiCzHf2Mwepb7YnAjWHOU4YqobphiK/Dy0GO1PDuNkACCFoPofznW8Y3nbyAJ54rhMws2YLgHBRnXg5fiWrVecAiX1bIfEHWVl8i6QuD1gVAcccntkUo7RxHAI5tNc7'
        b'j1vhAqJcYiO+CFKKabxytB9BtPq2Dq9Cg11bT+EB8nGQPt52I/7bM2VxsR2oPBhOGqKopbUFBlhtJkHb/EVErUctHlUFyOPDh86zOnyY3Xjj93o87QbMi1rhsKGimk64'
        b'kaMS1m61mHq8vAuO0FTaxwJZqeIsoPV0Z3Js/PGLE1u3lHGMk6QWKrQqYU3y5sirhTALkjkLhh0Cno0W6gxbIJYmf6zLFrUV74n9dDyB2+HDhmRbEnjkGEWlMyXWUJbj'
        b'pzAqhikqCTzyrhPxyNHZkAcg2SBLnGOUmrAu6eWJh6YkoT5cmAZTWmBMaZItwNDEbKJ5pMU7sS1ec3DU1ljTjjcQcrsB4CKrdYglJj22EV4Nk5eW0EgjWy+FZvx/Dmdg'
        b'6TSDmSYvEIeHKXSibDVxsERqUdRS720DFBAHzlR4kdye1fV9cIwBxMDeLUqcNsfx+5vlQQ4IwsMTHBk0MjRVl+DlUrxc/nN4uR7I9HeTeLVJLoernxP5uVZycpypdfdH'
        b'J0nz9U0rtXX6r43I3snNomNhsNfhYDV+yWA2xhtCRXMJiM8YfwgVOpdKSmqIRbYRQ3LI1iAT29YOh0Q/Rq5SbBoUZtnhwGDO01CklUioNhanRaXZC2bO7gX8YtgGGggF'
        b'OANPIOk/koXm1MEvtCssNEtoTk1piyIEZJYyDgnT3OtY0oI1WNno/JUF/mPJkDDCe0PS5DIyD1ro+rO9ttETdfo9AXe72qZ01AOm78Sv3UtmnbWoYn5NNAnfkcNYAFVJ'
        b'brcRAdvtZkrpbgyiYuJrMSv9k80k1j0mvtzTSDcXQEAyVts32XgiBrQhgTjWbxG0JL+11kcuNNEpDEKE9fGFzdy7HI9EYs9ifTgjBh6EzjRqSo/XNT0ahKzAmDeXcMLc'
        b'4cZDZ+JBgfG7mgX1wjDQqniHCuxAa4pAn8Jh383U3em+SwQMXsziUK+ansLxv0NmWh+Ec/Lq5WHAHhVLt7A5FbBOaYc1KJjH2ELuLO5czqBbZGYq+g1uU0dBwaJZC6bl'
        b'f4PdZYqPq1VPg4PQ9Kiwqs5YDlEZ0ID2jgCNWNSidLS2+5l9LmpIkkA0almF2goGS5OBNRpT+kRouOjnG2SrV6NYxmKqaZPBtYzqRnRwpRFHCijAJJoD1rCofa7Hu9IT'
        b'aKqvVVFYyIxFcRLqTXYT/ktJnBU8ioKEAgD2ztO8IHZOKtsw5qKxq2iM6R4oIsDYRXwT5gMWoA0tGRwqr6K3DJbOY2mbInfZFWuXg3EOupJgvpNIyfXrLlRCceZwXclB'
        b'u/qMmS+YDLOJPIkbFHtXsm8QpR2QflBJgrdm3Tase0V7z7YEnUFAQbO5Fk59C8tWnFlcDtf+DpTkCrqu4tWJSnLQ1WLFu6CL1QP3g4JOuGLZVgOCQJmKK2jFMhWxyw6t'
        b'cLFW0JfwHpXLWZ34HpVdFGvQEkwOOgAdsDfjNanZqfTbKEN5DrUdc0FrZdqEaTVH0ajkKM7B4qM44x+HMt986dtFf50ym/gdx8RJkybRxEVFN0APfjGjFvn8KD89ap3R'
        b'1qE2AfDhK4qFqMXnWeVezX7WFCczswAHKfB6m3wePwNKrbVqY5PPH03HRG1HoI2AmbsOYFVL1IYPG9p8gN6qbR0+hUlL1uJqleo9Xm9UOndBmz8qVc2avTgqnUf3NbPO'
        b'XVycwlY4yf4lKkAiExyLP7AG0OMkbID7Ik9T40VQNGuNAzO4vdAcj3EPNC1UYVE90IqoXMc4KHZfR6ubvmCKxhLew1PP6gA9/snQ0klMfZTUwqtwA9XQBrIZUShdhANK'
        b'xFpgdLBksOnIEg39mAgDiF0n0xds0+F2kzn5R7RQgxM9lbZdQkV9clvozFK5njuMJGADSEiPhM48RYhwaFcVEImQwvPUhpyZbsMxSA5apPCKHOQzmbKkpFgRpgUsBntU'
        b'jtHLIjFJbbTS7Mdyp9eqaFWdP6atYQLj1pN3B39Hq5oEM3ys9OdYnJePzB8+qrSgF0oVU1pD8EQ2Yq4u6AXjBBjWYQ0mx24qF7cPG9sHeYSIdacl0TBsMA0wNn/MhL7s'
        b'wo6i5OuYVFLgL6F9UwOE9EecwZhDgyOFlNejIvQ26qJV3gSEen2bt001oDkr3CTgSFAXP5kTvUbx6ruxlmrwacBi8qfQ2ROZLKKMwIDFRrGE4V5L4j4TFKvX8SfE+Dby'
        b'BshXH+GNahKYBL/Qa1ScXdAN5YyyxNgFqVablO3KKKIwNsqw/v6k9hUiJ1iS9G38kAH6ZaiuFzv+SY9NrKmpQQU2kT7R7qmsJiNG/VfaXrjepN+Fr8ka+IJGgfvtTARs'
        b'y50D5mbBsM1usn70huTfAijcuHefr178/aL0xoy3f/fRgQrbl98uW/jasff7SRmzqoZfvuO92h2v1tz67MHdR6JLWlpPa23ccuPF34g/ij/cMendZ09rDb23/+IvH/7y'
        b'/qde/3ShYL+5QF46tPCv4RteyT11r6du9vpnFhy67FD4vL1p/jPmvPhpcl1oX3rSI1WfvXZB3fXvDFv56cQDcw5FHu9c/8YdNz1zyaRC1yfj3t+xr1/oL/1WnHtaeNgj'
        b'uQUXbnhghGfJLV93ZdTv3T/pxUMVT2ysv63/+Mfe0IfvXnrhq23fBW85POH77eFJX6/1THS0Dxqzd//RQ89uKP96BZ/1+fcPbbp6zIi8szZuueE3BS2fj/h06Offb3hs'
        b'Q+nhI7a6wU9e82bBpLO2es5rrKp4/r7Ss/c8t3DxU2ef3+LJeXvGR4NfqTjSpT5/1vpXHtqUd+T1nIsPzL/1uRV/OpwyRn9owJwJbz2zfc/MJU+8X7G04Y1pC5d4FhxW'
        b'bv2m4dTNVy4JW25ukj9/4M9XXHew36794aFdsybNcd95cceXrz27Ze3g9CdG5Kjzvl7w4IcHPpuV85Y2+tAbSfdOyrZue/2uf+75j0P3/PF6u2/ln4dPffGhsmFTrrYc'
        b'vfaSmvPrRnk+erP25fpG//3fTL7n/Qdv3LRs3uFpv3ntzJcfmnioY84XzxfdGNr+pevIG+8tHfO0/f61oUcfev3r9i9bb8v5/XVPd9506IGs4rmHXnx0YMqBTwe+M2Lz'
        b'92+05+V2POY68snKe1rffG/ToB2Bw02//mzf736z7osl41668PCM629/4Zj1mU860vs3fv7gkS1Vvz9mW/bSGTNnZY/bO+aF8RdX1Odt3jvylesuvXJb9Ol99Snn/uns'
        b'u+/i5n/12psj7vnn6IfP/mzCsqejIyd8Mdm1/XH9jRXhxtkv3HPNgcc6Dh9p/7DQuVfLevPoqZMPvq3s+XHt2X+5vOyHu/9QvebwPy9d+/Lvrs2dcNPf53eu/PNl4558'
        b'6vovOtccOpC8Zvr353wX/esrjcN+qHvG1tLV3fbyd59f/cbHB9PTfvvKpe4ZGcLqlyqnvL6rc/movK+KI7ZRNf/429aam3d/d8sR7t2bvxvc9e5r298/f9TCQ2631vDX'
        b'6m8/e//ix+r2nbNk3BPffPjr6S+nrK5+uWXva2Nyx17zl4/vmfLs+VPeT+5qO3fE2IFjz/jh9acfqLl19/ubdje23PTcDw0/dm3fMX1XzXNjz/46/ZKVZxY/Y3n8MveR'
        b'sldrbnqgsyTvn9f8PfPLc4/e/M49jdUFK68OVH1zcOB9L7v/45YN3zYIH30aeCdj3OQRpdu/5k87VPDoa1+0fTf1I+sFez4+f+QP7/6x4oebr1j1vzy3X8qJyQ+85rq5'
        b'OCmQjzv6QNsY9B1aoW0YNVd/VL+1TI9wXJq2VtQe0K7Rn2CBJfYt0ndRoMCa8hJef1y/grPpBwXtOu3OcRQ7Ypa25YJ4KOxHtDALXstCYWtb9DvJdL1Jf1K7treC6GkX'
        b'SLPn6Ncy/9EHJpQz6ap9bllJu3Y5er1P0Z4U3bK2K4CAvnmgfjc0g8w8K5q7WFGYQvG7tslwzUUC+OAZDknbVh1Al2ertF+1JFRdUV1Zpm8sJqH97BE9xPaXVjo47Y65'
        b'ATyT9Me8+hNxkb/erR/qW7eiWnsogH6+UvQr9bv8IymC0OaO9PqTqAes0rfZtQd92jUBFPYUaru1K3szb1dr9zHm7dJp5HlUu+E8/R4Das/KR6gNk7QFsLFfdD6c9FJ8'
        b'+n9hYf9fXYqHsGP83/1isqO8bbWKEQoSdci5WpmXBZn/BX8fSQNddhcqgIvsf5od0GOrwGekwX26wBctEPjcTJR6Dy0dfuaAPJcle6okCHw2P94r8IUdkMsmkVR8eCpe'
        b'8+k6YDBe0yx0hdKy7XiXKuI1w3L8vdNmPsH/QwdgKtNJ7110hTIL25yIxP8oQQ5sb/YQgR8EObOtTt5JZQ1y2ei3cBlec8fitaRG1WNisyv/Z+2f7BJH1nHIlnMmCnxb'
        b'5/H+fpu024tICQZA8XztdrVKi2ibrZwrRxyob9WeaNpsf0nwF8Gy/MPG78q3PHdW3qmpa3ed99l/rPv27cPZ3cnjD3vFN11r5H0Tdi3+9ehBF9jm3DSj6o/3PvHnfi/m'
        b'fXjVnOfEXXN27p737h1fHL3luuYnHAXDLikau3PLsoqPq0IPPxu4cc3uZwec0tXQfWPdOzd89ejyJdXflb9Xe9bggmtnvbUz/NXTZzf1f0zauijHUbXjvluvfP5sy/dP'
        b'Scse7ld47vprv//g0K7Vtz/rfP2tPziX3Dh899cVNX+u3v/1oB/vFCwvT++/NXzB0m2eD/dMX3bn+8+v+cf3H979+N5/FLeOP3h14aHrFm4bsW3pB21nRW7c+fDbjWve'
        b'bfzozpdabtm0uvz3e3/Xf8L1Bw8P3NOy95nx772z66F7Sofv2v+HkjmhI83eEUf+t3dMS/KDVx8svPWNhZ773zq49duS2/9WMmvvwfv7f5h7ztnRyyeeuSpUU/5o4Df3'
        b'HJ709h3bBi2Y9uWrB6pqLlwf6pzbv2uqZ9JtLX//cbzr6CtqVfULw87YP3H3mBfsHWV3vFZ/5IP0rnnFy/60/Narf6wrOtL4xIo1F552xgfPvXok05vz0rgP/I8P3znq'
        b'twe+fPD9yq5Z3x/blnlsbTQ4eH3R4s+v/f6FNf+4TSr3PvmnjYf+tnLVvdMdH52pN95xIOfLd+5+6dXQOV8888PCjgm3fDf62Mys1Kva/5f2wZTn5jiapN/mrx/wddHy'
        b'lIKtC6f1H/faH6amlz/wh2lZk/5y6lOT157+lC2U/YHt2RuWr0vfXrd2wkv7n5pw3UNPFexr35h3xUNdDy2a9MdL7eN/iL779faXn0j7dug3X6W0q1Gusrt4Mvnv1tfq'
        b'a7UrjZW1QV+vPaKtLTPW1lniqdo6PUIozUA9MrEdo0ySr0DCCjBPP+0xUbtGu8/OotQdmIt+tow4lXnaRo7CVDbr97FIk3fq140t1faVjdW7gR7Vf8Uvhwp3BlB+UOhP'
        b'Lq0s167Xdpeg0yh9M8Ws21Cpr7dyQxZZ0vTbAd/BjNpl+q456HFcf0jbzdx29fQ4PkoLEX7lGqWtrcR8G4pTtD2YsVTmUk4TW2RtA7kaghp2NOvrAUPbKDYN5aS5GDVj'
        b'nb4/gMwkLaw9pl1eqW8qSl8jcIKPn2xdSX6A7No9Y0rRjfl8CydPFZrOcS3Rn2Txh+7VdmohwuiKynlOXi3Y553qaaGR6T9UO4ie6jcsm1JcAdiXTXtS0ELavfraAJKA'
        b'6R5tOyCMgD3BXheC/JSUXFbktZx2SLtbX1embRgPb7T7+cVn6utZOOWrtf3euI+tXGGZ6rCdQ23U79VvN7woLhgBn3Xxs8Wl7KObLoRhXT9/pHb3CB7KW8fP0XaNDqAF'
        b'kX6Zdmg61BUGFK5krn4d9B0dQaJW+kFtD1cw1jIzTb/LwG85fxKgi/fq3SWV5Y4ifZ12L8YWzdUeB9xwybmEdeaV6deQ0zIYD3RXVgl4adZFEuDDo702aoxbe1DbCxMw'
        b'r0Hfi425gZ+tXzeQelChP6TvKtXDo/THh2EoxDv5c5ZbaWLStO7T9PWI0bkAXbuUn6rd2k71iS3avkoCjzA7xTKXpP1K0A4MARz7bmNFaDeOWaY6tfXz55dX4BRWW7i0'
        b'M0Xtbu1m6BdmmMUPr2QxXudrl2tX1VA5rkvEmdrjp7Ph230KenwcJXP8Ik67ElDq26dqu2k1lS/S7zO8yOkHB3AUvxVW94NsY+zQnsQIrrAO0dfHqnpOquO1J/QrZOrT'
        b'/AVSZXnxPGiPvEhI0x7N1H7lIk+lFfoNhWwNV+CqSdJuEPTrV+p36o/WEoKr79du0LelwoP1CRq0Eg6SCPP5a/1K6leO9oS2obICfe0+kGZ4unPp68Qa/doc1q+rYFut'
        b'xxyWeYs5SeK1WzNgaeKw1sC327KHsq5Vw7gXV0D5+jWi9khhGwvefasns7RC21tUrD3ePGpeGSLst4tQ4DWzaS79WqS2snRuhTiqmJNyeW2nfo22nw3LXfqmTH097vjN'
        b'Igz7AU5ayGuPantrAyjH0w+tGF86z8LxlZy+w6ff4K6k+ibqD+fB2saVhS5CYViCgravTd+ujKH6CnxLMCxndZWsRaDGVF7bdtoM2k4XabfnVc4r0+/XHqgZN4bnrPoW'
        b'QW5sYAEKtundsIqv1fbG/GiaPjTPn2eE4fUpHXNMB5Yx95Ww6e+hUS7M0a6sJHfLZfr+ZmNfurQd4oyVE9m2eVLfoh3o7dx0cJ7+iL5NO8gyXedbqT+shRNdi8b9il4S'
        b'DJxCTQEYjOCkHLZICUwNbNQtAECqaEw2ACC9S9Lvms5Va3db9V8tVpmTswND8pNg2CLt+GUlLqgMfbuoH5qh7/bmB8hp8aMX6TuS9E2jyufVdJAgUz8Im6EK845bJg+c'
        b'UaE9tpwNxhbt3vkE60bOrR7JQz9uE7RIs35ozCx6P9NuIRe7eFTgXrxf0LYNg4Hfru9kNOmO0aXaVv2mUn1Tlb65sqy4HCY6fZAIa2NtGou7uuWCCZW4U2EgIhVl80ZB'
        b'RbJ24ByujLPoN2qPraLhmt8yxji8Ns4vBkpP24jHUmaBtGS4qK3TtrFQxfpVPLpinj+fzhQrtOc+AYDkfbBx7jklgPjVINgZuDRuqocGrcQFCeC6ysrl6PdL5/HLWZvD'
        b'+q6lQy+ARukHsDCMgtNPhwNwp772UhaN/pC+D30Ls4NrtPYoJ5Xz2t7xhXR06Xtaz8XGjtJvPqeyPHbOYYPzhktat36H/jiLV5ukb6msqC6ptnKyJAAxetAGx8A26rB+'
        b'i7ZPP0See7G/5TC4+i4BdtJl+iPaA/oVPyUMM50Yn/5vQFP9e15ikmIi8u6CC5ckCDb++D+HkGqRSNqRDUSSwMvsvyDxmNvF8hgyEEb6OZhuoOAw7qAEwPBtVHYGWUbH'
        b'/5xUMuWBN06ykbaRmNIpyGLnpVzvv1KZZ3xvptCAKh5+T6Cj3e2O+/IzhQfP8Ik9xRtGeXyb6HyU3vVQYUiG/+jzBBUI/M/AtY5T+Gb4iywJL0HdssgI+BXgV4BfEX4z'
        b'4VeC37PDS5o4+HWEl6C5YGQw5m/GnHyIDy0xteG6ONSE84qtUiSl1dLFt8pdQqu1CwWDVsXutbXauyS6d3gdrUldFrpP8jpbk7tkund6Xa0pXVYUOwZSofT+8NsPftPh'
        b'Nw1+B8FvOvyiGbMMv0OCXDgFflOC5C8okhREf+p8JBXyZcBvGvz2h18X/GbCbwGqaMOvNShFhirWSJYiRrKV5EiO4orkKSmRAUpqZKDSr8umpHXZlfRIblBUuHAOqoFH'
        b'hikZkWKlf2SkkhmZr2RFqpXsyAIlJzJHyY1UKHmREmVApEwZGClVBkWKlMGR2Up+ZLQyJHKGMjQyWRkWmaIMj5yuFETGKoWRccqIyCSlKDJVKY6MV0oiE5XSyGlKWeRM'
        b'pTwyQRkZGaOMipyqnBKpVE6NjFJGR+YpYyKLlLGRucq4yCxlfGSaclqkXDk9slCZEDlLOSNSE3Z0c5HhypmR6YEsuOunTIxUKZMiM5TJkcXKlMgpCh+ZGbTCm/ywELQF'
        b'7Q04ShkhVygrNDhU3SApU5VpMH+OoCPiJKWVuK9ZVygllBHKhJzZoZxQbigvNAi+GRIaERoZGhU6JTQtNCs0OzQ3NC9UGVoUWhw6G9bDEGV6rDxb2BW2hYu7hYg9xCKo'
        b's3KdVHJqqF8oLdTfKH0glD00VBAqDBWHSkJlodGhMaGxoXGh8aHTQqeHJoTOCJ0ZmhiaFJocmhKaGpoemgk1V4SqQvOhzpHKjFidFqjTQnXKUB+rCcsvDJXCF3NCFQ1J'
        b'ysxY7uSQSH76kyFfWijdaE1+aDi0ZAS0ZAbUUBNa0JCuzDK/6UoKu4JJVEMhfZsEtSTTeGbDCA2Ar4fR90XwfWmoPHQqtHc2lbMwdFZDjjI7VrsIbRWpJOkSB85jlzNc'
        b'EHaGS8LOoDNc0S10o2IBPimjJ2XsySXOYBLZfsxhgQBIzZ/p6iOUOLFeGp5DzK4qzLXY1dwAeg3hmnlTq9tQ0zvWv8BfVJzfxFRFa/PrOpq8gSZfsaCuQuhDEjukQU/o'
        b'88rd4CN+G6qfbbUYtr8ciY7Vw6aBSrEEgK7RE2hQ0SjC5lldT0ozZJ+OAvG2hqjTVBwihSEevZe0AmSEOwf6yG5tVz1+P6REb1sjGjCjZpmKfkPQcJE7Shof2K6jKFo8'
        b'uh0vnKkk3aZ4AL6SEwlULY+K7W3tUQeUrngaatFowdbgZpJWZi8ZdzIRg8lRuYHKiSbVt7lr1UYKm4nRPt0tq9p83jWxRw545GOFRZ1w7w/UGk46bZBq8NY2+qNWuKPC'
        b'7HTj8wf89JYU4qmGlbVqPIF6t5ii7+jGRU9VP6k7+NqoHC9MYG0d+0D1eFaiK3RMoDYDJSz1Xk+tGpW9tTDBp0bFuqZGUiZHhzYsTkbUgSGV2T1T8HnWmOSAWlvvweiL'
        b'bjdkr3OzibTCHaonRCW36mmIutxKk7+2zutx19fWX8RUhWFhKMzjGuKux4Si4l6B8HD+EKNi3q0EFooH1aXQNxT6ckXh/0wUswtkKCt0A7G8IjfIJxoC93Zz+lO+nnBx'
        b'fhHTMzOwASdbtD3aiAplstnGx+Bt2AqQzgkbKwdbEuQBBgkNaEIxSKHgN2RYIYbzSclLCkphR4tNvTzs7LIEhXBSi6DOhXvZV0QpTr0w7EziuixhjimFhR3hNHjjgr47'
        b's3As5LAV0gO7haAc7g81Cr5fBwV1CzwbFM5sQC8416FyF9STDvXso9zZ8PUALM23Gp4PDvejfB+F+wHcsZLlWXaXDXJawxmQU4KzAsa6Gw1cnglKcILwVJ7cYrsK9Xtl'
        b'+MpO5eZBLtNrjgNKML4M2uHOgXcUKAjSizjW/zBPZVwC36aEk5NM2zcxnEpvk7PRvy8QhwoXTMJ3QQHgbXIWx4yyyCWpnYUOiCnN0XhCmbfAPDjCuVC7gOMStGSgUUo2'
        b'Gwd4/yC1OMsciWAPw/Fi539SIPL/njH9i3jXuKq/i+sEuRi2Svgq6gPJgo20ftLgL1VksYuYHhCLXCQDfpvNS6JLcAGuOwC/Ex0U58gl9Ngs/YzzhzbL7wVjs7hgqouN'
        b'zZKRuFngrYiTF5bgjDqlx/bBySuFbyS6w4VvCUr+TyievBzGv0yYdBH174JW9fKglSxsbEGojS0e2C65EzmfEs4LDwsXwibIabCgKydYvgu6HGHUXXNAqUlBRzgPNuUR'
        b'WHgpSVwOHswi3LvwPuikbQflBJMARUwxFjBp9LF3QQdF5PKFh4eTw3kKHx4G/wvh/+BwUQMf7of1hAfj5soAFBOe54b5cGo4FVGzJittbgsuYthM/YI26E0yLHj4DcLW'
        b'CLuyuS5XOA0QAnziyuJg2yQTopAEX5VRDK8AlQD3DdDjTXyXxfcZPJHDJVBmSjAlnE3vASBAa1PC+ZTKN1LDKTXcSBVQqsBIDaLUICOVa7aTUnmUyjNSwyg1zEgVUqrQ'
        b'SA2g1AAjNZRSQ43UQEoNNFJDKDXESA2OjRumciiVg6mGFDgcyhG9D3KbEGwiEIC+hkeEk6HHqcHUqwT/7qBEVyteaa1k4VqBMmDsG9A9uNGbLA5t/2A803GNQaki+XOQ'
        b'cOQReNPz0qCEz4OSGWwl7vq73/+VfVs88t8Advz3w6dT4ZT13xCHT6h9KNgMr9ey6CJIlSaRqTH+fS/Z8C06VkVnFWmywMHT+H9B4NKMe8d3khNNk9F/l1NIEx0Ax1z8'
        b'Cf++ktKcYiqfJtpQ5PqDZHGKSOv3gHSmERdBOubOEmAZkNFhmwHp5DCXAOnEsIWOd0BgwnYgAADCMR1vw3mr6eO/r/Xwnw9MQAN8q2xa97MBFnFAenXKbnbqTuyUBFsG'
        b'cREBAHQa60g3KXQCXmCBTqai/056LgUpJ3QxOSzjWQ1DkQIgKxkBOKZQeT3s2FzIY6lJ4TTckjhYBM5EC4DbsP00QAknJqitA+gDIApgHjcm3qfCF6SCjWGF6Fuux7ne'
        b'9wCm//eu5H2y4XSSozWMJkyS1cEPENF0J1fE1eTouZociQOvIJIJCGE4BRHg2MBLxsAX0cD3B7RM9JfRG0xnYpoc5s+EFeZEO15659icS0OHNu7WbLIfwFSPQQakLmzN'
        b'QXtVCU6UC4Oif52JavNYugSII56/FvUNjBiJ0BROLgucMjCJXdZOBzIdyAQvQ+ICXItDfZ55vmERL+mbbCxhxVYiwl2hVCDAM0JZDVYjvI0toRYbQndoR2Y4GZ+ZX7Nz'
        b'D7AJO+wq1k4LXmOl25HlQV8ugC/hGbyxx76MtQEQ1OHxEHx9mdzEfO3G4iwiNQIdhgGmcBDo9wEj8qAPyrYyxExb5B7erorFqBCoU99AGvI9/hf74oi6mvzutroG9yoV'
        b'Va3VY3LMHkYyfDTSOivmiUz/l4J/5Pw7gf6XZMPIydwwqXB10iGAaujohFJG1z8CHgUO0UGhUly8bHeK2VZ8mmZ1GczbNL44m3EeLsbSKXCG6F/jV5/FZ7/Fy3N4eZ7p'
        b'QqPzHb/6Ain+d3qb6tQX6ba1NnCR+jsyoIYbTy3GZVBfImOWJkUdToUCVR4Va+uAnr+o1o9m1lGr4VQqavWbN43etrpar784+b9myIrP+Tfgvv/P5V8RV+CavBJJsCiu'
        b'c0GQjhdVuCzZJFJA8UFvUQb7k/r4c/b59F//k43/sbTsFNOsklg1DvdeQzNe852SeMoAvJs4A/elYJOJeBQE6mcNGsoc5CgigzuRs+d2GzuytbYdtmVAVdfxzAiX3Akw'
        b'2chh2nezVtd72tG/kopidJSU1Nd2+D1udzTD7fZ3tBNHENlnaIYCT5Pc8YT6eU+vEAnWqhNb25QOrwd9kTEvoRIAllQBkKG+5DWXchbj+VCBPOKaKoL/B8mB8ek='
    ))))
