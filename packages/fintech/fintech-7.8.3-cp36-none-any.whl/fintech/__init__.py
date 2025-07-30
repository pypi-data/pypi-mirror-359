
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
        b'eJzcvQlck0f+P/5cCQHCISK3Gm8CSUBRVMSKZzkD4lkvEkgCAQyQAwGDgqjhkMNbvM+Kigfet+1M7223927Ltt3etdbud7e729263e1vZp4kJEDV9r//7+/1+pmXD88x'
        b'M888M5/P+3PMZ2Y+o1z++aP/Sei/qQYdNNQSSuO9hNZwhYyW1XJauo6po5cI8qklQo1AI1xPqT00HhoR+iuq9DV7mEV1VB1NU4sowxMcpfUs8jJW0NQSL5qqGq7x1Hrl'
        b'eGu80FFMzn3I0VfrtY5eRD1FaTw1nku8lnotpgzMYnQ1j/LUScUPIrzmF2glWZXmghKDZI7eYNbmFUhK1XlF6nyt19ceqJJfi/CBRYduWpFH278DX3vZ/5pk6GCjdLSG'
        b'1jDrRdV0PVVHVTNVQitdR82jrEwdRVNr6DX4vejas0DKKvMcDSJE/yeh/wNxQRxplHmUdKiym/orfjy/GL9+YBlH4b/nMlTpnX551Fd83j9P61MfUkwsrg9jo2ysjnXW'
        b'iX5onXSudXIU6F4nTmmRo/MlkXHz5HAHbJsP62ULYf0MUAubYuYmz0+Ogs1wkxQ2wE0sNWuBEJ4ds1K/NGouY4pG2ZpGTfhGdU9VrLuveulL2ZYodbL6vurV3MC8Al0x'
        b'c35LwLrQSUupdcs9TJsKpYx5JMoBbsjBBm9UaDQuMsMiByfh5SjYGMNQQ8EFDp6dBTaZJSgh3AM36kATaIWt8CroSkOJQTNo9aB8A9ghnvDECUrKdjORUiNuIP7giQ4P'
        b'/BN1xpIqrUGi4/v9iW5ftcmkNZpzci36YrPewODvxx1EhYppX9oodmRF5XE6iyGv2yMnx2gx5OR0e+fk5BVr1QZLaU6OlHV5Ez5IaaMPPvfGB1xIGC7YFxd8158R0gwt'
        b'JEfLCPw1Nu+ANJlCKU8BO6NAQ6Zrq8riBPAEG1yM6/Cc6SX6VQE1KXYspP+1eKo4lCKkctbPzJhFVGlSWW7ZR5OB1E4qH08jTxeVFNLvMJRkuUK1OnDkSj5LYzFLoV7O'
        b'etFLJd6imsvf/GKUkEJVrfCWq9JPr5pCWTCRg86MBd6gQ4ZqUw9b58Vmq+ToBPV+pEIeCetjolIyaGrZUlE63PGElLbgzkn0gUe9lfKoNLlXJGyE7XAPOAs6OCoM3OLA'
        b'bmspSQT2ge3wOO7CGPS5+K8H5Z0JDwoYuAXeAOcsw1CiGWADOMV3s7OLwRnYRLoZNMF6KWsJxIWdGl6ZJpemBi7KEFDCeUwQPDXcEoEezM4QpZHWTEmRM5Q32AVvg/UM'
        b'7AC34CnLYJTAF7aHxiyFTZmwMTVDARvSwSmOCgB1LKypGINKD8fds1cyOy1FliInRCkA+yegbI2sErQKLUH4eWceuIITCJLBBYrjaHAAbkywDMGPLi5YBG4m8eSckQKb'
        b'pSmoeLiVBdfBtaGovUIxw8ParCSftHFx6HkabMlMEVB+w9gp8zPsz0XWAvEi/Dglg3/qC8+wYxErSBnSlIFgH6zxtoDtyaiXSmET3JSGvzYQ7mXh07PAdcsolGh1Brzk'
        b'DVti5KlKC06SAi/Bhsz0FHhLhtJOWCpMAbuHoA/GL5SqtLBJpoQtKTKFELXahaeUDLyQBPaR5vCInDEQbo2GLemoV2RSeaqAGjiEhVtBVzj55jUFw9Iy5SnRw+ajhm9I'
        b'kaXGKJIzhJSMEsB279UWzAiLElbiOkSjBwqa8oaH58JrDLwC9rKWSPR4wiq4Lo0kwF+cFQlrrWnyKNgCNyEKzJILqZmcENYsGGLBmAHXJY1GadG3zI1MTkeJtsFTyvTM'
        b'BTidLEEwG96CW5wwx7hC726C4TYa4SZr42wCm9DmYRPZPG1eNm+b2OZj87X52fxtA2wBtoG2QNsgW5At2BZiC7WF2cJtEbbBtiG2oTaJbZhtuG2EbaRtlG20bYwt0ia1'
        b'RdmibTKb3KawxdhibWNt42xxtvG2CbZ420TdJDs6U/UChM40QmeKoDNN0Bnhc3/o7GcHEHd0rlUS9FCGRBLw6EGOIHjHBTyS4T6eFrcUQMJMMUq5VA7qMccFKApVLOKo'
        b'9hLLIMxHB6fPg02IDMHTsI6lmLV0UvJMSzB6MmQ0bI0GJxaBI7JkAcWB9TSsy4S7SK6KxdXRcXlShAuINoXgJBMNNsVbQnB5dXArjTsH7lfKUE9zKTS45QsukCLZUPh0'
        b'GmwAV0Tp+JEnDY4hZq8jGRGbnp6AUGYQ7EqGzQirkmlwAbYVWXALJIKnq6MVUm94naEYcJleMmct4UOf0fBE2vyF4CRiVSElLGYiYTs4S8oT+YKrabCxEGEGwhL0thE0'
        b'OJ0IjpLyYvR5hNjGyGhUXgudHjeUr8Q+AaLwYAw4iLzQQ2E8EwwaUwnkJLCF0XnVqYjXMtFHJzG+8GQZ+SywCV6bj3Jcr0RFRspRrgpmbL6UZBoPL4M9iMUjFw5DVTfQ'
        b'T4BbC0jVEcKtj0PfmwruhONK7KLnDAFbCK8kw21e4DK4RhhCihlbBO4wwJYYQBp/KWK8vbApQwaOgkZE4FZ6GqclXAyOe8Mz4BRslIFmuB89Ahfo+QgBW/hqXoEnAtLG'
        b'WDCbw00cJQxjvMBOMQ9oZ8FNAWxKBqfhulyUsZqeI4M1PIUcSUtEaKlYDjfjejbST8KNCoJCsGMmkspH4QYEHbjIaEUKahylgAou4MbBRhOBW9gFLpeAPbArLRo2grOp'
        b'uG89hQzYDo7DzXmMndy5PpoN0mtstFOzYeqRLlPNIt5hCO+whHeYNWx/2paD7d15h1Xqtfu+FJimohsFtt8MeuVZH0oiZpI63n3uh4hnzn4dtiZkqbXNm549/b2sQPnK'
        b'9869lrD93Q+/29L2j3+tnbl411dL/OlXB/lGL1or9SAKych5oMuujzRnyoKlsDmFV0iCRnHsQnDDjDkwFpyx9pJmlC9jQLIMHkZJRuP2tcH1kwiTyjIQ3DX0iL3d8BhS'
        b'gjZzcLPoKfLKRfB4NE6ZiYgTtOCyvGAbA9fBOnABXIQ7zbjByxBL7bCnSleABvLKrJksO2wAuGDGZAJbwNWA6FywW56MRRglghcZsP5J2Ew0sgngbDhimosIElpjeiCf'
        b'r/uoKEEmqF1q1496aUDkLtF/urmValMR41SA1oho/udLe9HGAY60Uq6b1ZjM3azJmGfECY0Y9qSMi1LFGAPw+UBHySTzWmfBdW6aFWbhYA2i4aYMHdyJaFJIcTLE9vAI'
        b'3N+/Eq3gSY3RMY+pQq9/tAqNCO2LjfcpE1ZnJn849BukAN9VvZR7X5Ws+1NeoU7Dna8LnfQ2nfAOd1z2JlKDca2FYzLSZJEI+PJAcxqN+P0UUwmugh2EiGbAy1VOIkKa'
        b'TKer5hvMtyTTfzdYzPriHgV3LSXyp42BVI+Cy5bkFv5My9PGQc5Gx1nqcTHYsqNqqAe+vZt9DlL6zkTLwR6sNm5CcGukwR3QVeRsdtr+f56jNlZe5tFKvi7213m6f4Cv'
        b'oSSnJFdnMeWpzfoSwyacmWAGYxmDG370TISRpGkyU6PlSiV++7UorDWwVDS4IIC7ERK2PqIS+Y+ohKejBto2l/djTpoUl4ygkX8zYqQA1VIkRMGt1er+qW0cpjYa0xsy'
        b'2rhfY7TR/VKcoCeBA0iHOt9HgNTGOd/3i6AUv8+/PwrX1R2jTKnoxkdnik59fk91X3VXdS9PrFOpI9UvfRl1XqXp0KL/AfdUZ9QFuk5th7ogV5xfr0mma0eAJRsTNoo2'
        b'Jj4tkkzZVRvHUiDQR0t9IaXNw1GB4IwS1prA6WQlsjYQLSFgO4i7cwBsY8E5eBjuR91EKJTrjT+9qF+Qk6cu5slfzJN/EIPwxx/hUFWYqUCvM+dojcYSoyKxuASlND2h'
        b'IBkc0MSpjfmmbmHRKvzXhUn6GH6MEdOCMczJLpghdriwy/0AV3aJR/cCZgxE6jSsT49GKpwc27twC1J3GjCwbwU1SiT3wWUk55s8sidToHGaJ7yigbv0Kp9sgUmK8kfO'
        b'fr4ovyC/OF+Zp1Snqws/6dDeVZ1U30Wmt5fO/7uPX6UobZfw7N19Drp+rAbzdmkUV9QY5C80hvegBm/nPqRBXC1hnG+bS1v8ya0tcIfPBus8UBc39moQhgoH1znQAVtE'
        b'/XNTH4fMw/noMVQETjlfPy//ImfCcjAycnZa3CXUpPX5yWpuyyapJH7gLs2fVCLdx8U0lf934d7qO1LOjFEenoXnYSeRuUqZXMlL72PwCjUAXGRBi98ccxRKlTtTQMQ8'
        b'sqIj40FrqlwBWjLRN7dGp4DTkbygXpwj0iVIzNh8AzeLkIJH5Lh7mukDw+B2DqwDN2Ad4Rh4bSJcV11ACpempiszUpFRxOsHI0cIBsMrE12pwKW/fSyGvAK13qDV5Ggr'
        b'8lwZZaiQ5n/GiJ5+72ZRKpd+px29PdjZ2zj1fpfe/lzs2tu4WQcjAdYwE16LJpZvMoLqTWkZqM8RwwupUVWCzHBw0NlNjv4OdkEzYro9Nnq69Tpn/+/e6yJlMf7qYLFI'
        b'pJlDSbRrX6ssVsSsHJQfPz1QLaSISg6OjKqKlsNaeDoFceUlClm2h2lwyR/UEzdNx+C/+m3zoyP/TP0U9/vFJ1Q07175QYSIjKNC3l6jHvq8dzF/88knAyjUECHFfqpl'
        b'VMAISv/xU68ITBUYaN+bnKbWqDu0HdrOgruqUnX96Q7JRO09xNj3VAZdVPYp9Su5yepC3frGsczzw6NmFO6quacpbC8KKdr1fG1C7fg60S6lupx6a4PuE/EG66CECemz'
        b'5UmTnw4M8hAW36sZ1/m9+FL6hrmSv38inrDpWfFeOfX5rGE7Q95AwEvUwq1C0JZGumVtNXY6iEAbUzILnu4fNx6JJlyB2lRAiErCE9UYEUJfx49og4gsxOQMqSVDXAAm'
        b'1B1g+n8/zScjdIczP+1Cdx+4oQwmH6tJie2b67AF6YWIDAYh43MtbHqIb5Xu5VtlHp/Q8FeL+xCaWEmMT8TO54YhKrrugd4ZQ8VAG00IY4+vAPt/JX+ONxXTi9U8taxZ'
        b'Tdx21MdFecXX56ZSRgzJ/R266Rx9zLD3OdNGdDF16RfyV8f6glj/WW+2X9r3nLTjZcGkVEUbk7B70IyWWQM+kEzeHt40L6+poGnR/btrlbO92NH3r35quVy/6bs2yweK'
        b'WVOeXxcesO799pDO7FFNuz0Fp97/8vuzguCES/fOz78B/1NaEPTR8g//HX3rwav/uLLQ9vHAuIZJo0cG6WD30o8PTHvxdMJ3w5hZ2VJvHsjWg/Pwaaep5GYogXbYyMLj'
        b'8KwZ+zXADXB+iEkmlcLG9Ch5ikUObwC7MzhqqQDcmQg7zFieJC1VwgvwULUSnDbbZYUPrGHHwxrKjBUfcBp0zgBNa5f2MrywC3EbbCUaN6g1gy3RClgPG5Cdnwe2CEEL'
        b'I1+dRqq8YOYEZAJtq+xrlNkNMngC7jFjYMiD5+CV6FTsCUlHlq836Bo6lIH7/MBtUlOBXziyimVRUgVsRbopYnsJB46DMyuWZRLVXg9bS3iMRy/h4R2ZdKM8GXB5FGgi'
        b'RTwFroGbvHGQRoOt8CxvHcDr0LYkcER5XLRSnoKajKHEonkaVmQKctPiH2KjCUstucV6HvZH8hyawCALLYAAfyDNoSNvtXmhMy/EqWLaKHHh0kHuXNqPGtBjQeB811wY'
        b'9GU3w41A7PrwYBW8ER2ZARuR5SpEZuk5BtRkgQN5QjtbYVPQ18FWChar71Y6lKoW1ntYhfVUHVPtYfUwKSt9rWwhZRXW0dWiRZQhkKPMdJGXcRJN4d9TlCFoMVJ7rSKc'
        b'0yrEZSRSGhrnbaONnFVQukRPVQsqDlsFhYjLZ1HLdyxjqj2rvfBbrJ51jFFH3sehszNWYSFSoKuFFTp0xpHUgdXe9SxK6W1ldKzVq4WmqbJtqB6zSC4xqqW43pPUTlgx'
        b'st6rXoTP62iSU0Ryilxy/nYRZRUbv6sX8zkc9c2iynSLqDbGMJKU6l3HoLrL6ul6qkiIz1BtBBqmjuZTt9GGH0k62izUMSTtwnpve9qF9Qwu25nyLZJSSFJZ6wX2VOjM'
        b'LVWnhi300HAawXpkGc6i8BdU+2iEhR5Wn0IRHs/Do3zVPlYflPecxtPqE0RV+9g8bN5IZWM1XiifyMrifNW+qAV862iNqAi/8SOrr8Yb9YyvYbjzPofu/6gR4zfiO0H4'
        b'Kafxqfa1Mm2McQ6qL03qyxhHanytKEcwwmcdg9L5GSRW2soUsehZosYPn9vvizT+Vv5suEt+lWYAn9+ZBr/Nz+qnCZiI//qgNC1WX3L00wy0+lp9cHn4mcHX6oeflO6y'
        b'+uBrM9/H/ugr/NFXBKKvYIwPrP746zRhqE0Z4yv8FcrzOTpD9KgJJ/c/5a/wffSVAzTB6JrShGxgQinrAFJ/f/T20Hof/IZCL6u/ow5Wto01Ssy01a+OXkcbRGZv/szu'
        b'uohQzn/gUYwsaYN87ANGJnEKP8YuAIldjI39fMRay72qaStdSG1myjhsh9qVyG5RTo5BvVKbkyNluhlFbDdt7mUwP/BKLNabzHklK0uf+Cdlt5iFVFVEXoE2rwhZUz0G'
        b'V0/CB6ykxPiAln1NkxJKdBJzZalWMsrkVkmBg/sljkoG4ZFYK5bOjImrRxWuo90q7HCPjCQysvwhgGjE3rgfe+r7NX7pAz+1pFxdbNFKUI0iR5mkRNg+CDFpyyxaQ55W'
        b'ojdrV0pG6fHjMaNMYx4MIDfwqfMWR44DXVI6cj/wlKy0mMySXK3kgZ9Wby7QGtEXo4ZAx68xUj6gxzyghz/wHGVaqlAolqO7WK14MEAmyS8xO1ooAf1HXzgBf0M8/7U9'
        b'5+Jugd6g0VZ0ey3EnzEb23boFqqLqZvLKymt7OaKtJXIzkX1KdFouz1zK81atdGoRg8KS/SGbqHRVFqsN3dzRm2p0YjFdLfnfPRiUpI0oNszr8RgxkaEsZtFJXVzmDi6'
        b'haTRTN0CXEdTt8hkyeXPBOQBvqE3q3OLtd20vptFj7qFJj4BXdQt0ptyzJZS9JAzm8zGbq4cH9mVpnyUHVejW1BmKTFrpT79qqC/5ICEVIpTIoocBPoaZQ9eoBgs/Tga'
        b'y0VfWshiacjLxQC7FutLBzFe5BpLTCItmSB0FYZ02iDaXxhI5KkInWPfpy/tz+D8YpLfl8FS1ZfBudAdxpeUF0JHoLKCsMxlyJAm3DsEbsHGUgZsUcpSkSKTAw+BTnby'
        b'MNjg9KCLXLnjHlYtkLZa8ZGVKqSIVHoLyTC2mrOypogyXzPSYfF/PZJ7e9lqgVVgZaxsIuIjYzaSjHSREP1F8iOUKmQQZrKhJCIDySYOyQMOSxCTzsrl09VcxWIrh0rP'
        b'QjKYxfIFycT99UT2ovy4RIGGQ6Ww+Ar95fjYjrJiXuYYT2q40k4NltsCqwd5m5B/vohC8obUgJTEJPLXnP2aS6TKfJFkZIj7TqBEbJ2Mu5H0JXZL8ZepjntSgTER9zBr'
        b'0pq7WbVG0y20lGrUZq3xCfxU1O2BiW+lurRbpNHq1JZiM6JZfEujzzMbn3QU2C3SVpRq88xajTEN35uDMwsfQWYu3kwccqDJcZQ7BCGbaTShMg7RA6Yyf54SMK0R+hLT'
        b'IYw/uvZHFEEGdcNBk8o+vg0aYsAJGSKKhjywAQ+oRYMrArgD7J/rZofgN2M9krypz9AnhQc/dd4OI8dKO3zcrnaRyEFXGnSox71MNyCpX0iV+iMqQ5mM4xFd+KA7NJal'
        b'dbQ3MniItCKxPgih2XpvfN6A41U4VAn8ai9UFbFO5HRLeloZTD+kR3vFzmCnP/Fo3scV4KxYbaAqOypWoNeyVsquPimrGVQEiytWRxch/MNnVlSNatYQSConRISdjM/Q'
        b'HSYLKYHkTkg9VmsQA+jQNSZ2oniFLKIqZlhxuQnVrJWUitI21gsRkbLo/ZxBjM/RfXJl5YylWPwg9kHlWDlSRukiHMakQAooZxboGKSEfkQj1ZKmqnxRQwmwaCZhS+hX'
        b'LVgj4MOWEGughmuhiVFJKxF9YTu326NcbSQeSTYf0TCCUWPRKuMUTFuzeCrscUJm4AMh2hWE6LVGo1T02LDYQ6/iHAKIpejFK03TndSKaJRhMI2KMQIyDLoOYQi1MmJE'
        b'xSGIVsPoqlh1Xp621GzqEfYabV6JUW12d7j2vACJrWX41SQewe5kJDcw1Um9fy3As90euNkQ2/JFLnd+nqezQpNox4ASy+P9EIS9YaFVYT//DQ69YikuTofPvX6V9Fnq'
        b'rI6H/WUTaLvTgGIlI8jorHDm8rR0pVIeKRVS3tPAFgUDj85SuzkzPe1/TRimtNQSpPItYbZ58E4MxOsinYBntDp6CUvuk9AxOxJ4IjZkNRx5ytkojloi4IG1e4A9XG6O'
        b'vlibXqLWaI39j9liXYNAi4DEVwh1Qidfcw8dblj/6OENDyWJZgD7B87oiRGBbSzlC06ycD3c5Q+uRlvG4iT7IiEeu+dD1XriSZCVb3c8XMqmqGWRHvCcBG6DGxdYcNTa'
        b'qIhVfJ7ISNgYkyyHjeDE/MjUDGSyK1LkqRl54A5NGfw8p4YryahTUBS8OU++EPsuT4J10tSMdJQeOxIy03Fo1HiwQzhyAryi/yqDYUxYpb7zlOUb1cu5HdoO9Uu56epi'
        b'nWyHVJ2qPqn2zy/QFefeV0X9jvquffr9sI2+vyu+PDxccuDYxuliWQ74YNjbz77x7Aevbnv+rWffejXk1Wfafan3KgOm+0mkAuJ+AGcD4H7YhN0TOEbjNqgbQoPDsANe'
        b'NGPNYdmT4IjD/3AefbDTB7Fi1kDiuUZt6gEvwE1yHNcFuuDeMrs/JczCgY0p4KyZRAdc8iiOVsiT5Qw8KKGE4CgTOxFuIy6bvBxQk6ZIzZCl4IE2eysLqFFPwiugWbAE'
        b'ngPtDj/x48tJnzyjFsnmnJUlGkuxljgosFFCrUW/fOKKYHhVS0xXDe1DoAq33M7RHJO2WIeOGAd6fBaCn2dNxliIz4sctTLqMT1i3sRuCKoG/fYHuTgxHlmT/hnnCQfj'
        b'uMpkGnGkl5OBBI/PQALKRQt0MpCvkoRxCeZm2vlHA5tcWMhfssASg4mhyyx7CPOELethn21aeJXPYysHO4PgrocyEM89cC/Y8vMjsZpew8HdtK73OKwosVi9MlejfmI1'
        b'7gVcimUBrkKjPNUUCfY7a1zqGu0mR6ozOJ2cAVqc5Am324fa+GE2dlyACWzNDoCnKdAJNw4ANXDvPAtWN0aDy2F2v+Um2AQ2gAsyezxFNjs20OD8GAHlMuhKkJDXchjc'
        b'pU4kZOuxp4hDHcmSjuRIR7JruJ9DQu/+kHAy/uILGrA+LRo2g4agNAUeJIWt85KjYSNsXYAYWS6FLekpC5ygJ6DAQa0XvL1cSlzK74/mKJH/V0IqSSWDMyooEvA7aRhs'
        b'wSU6i+NDPmE9Ht2G+xPwADfqx5VrPUOYFRY8FAPPglZNGo5I2JSSMTcSNiziIXCu872oc5aBJngTdnnAs3CzQF/95hLOhBnqu+3qU+avVa/k3lW9rFMESNUYFDEQyoz3'
        b'VK/lvpL729wUWqneonkp97T2btKn78ZSC6bQC+Lq5tviPpeei912TmsadCx2XI0ka+Oxutl76ZHhL7e9GEi/8yGGyxcxUAqpdyeFnFzeJfUgQDdvONjVnwt6Ddg3imNh'
        b'20LiOIYtywYROCwrwoDoBoawNoeMtoWCluV9EQ/sBXsQ6gmWFMDdPLI+DZ6GB+zjd5n21/mArbnwPBsCD8NDvKe6A1xcjEw7xyifAq5fioR8wBoWbloDDhAH8HhQxzqS'
        b'5IEuPDLjPZFBnX+sin/Tpnhww2XAHBV+sWfAPAVs/OUA7IvHwXNKjcjGxsYOQeAwBwKvpUQMMX05ZMwGYAMWGShVE/qin7ZCm2fHvh4Fyr1kntkFvGbWo8A+aujHPkLk'
        b'48xAANqADhtoh7CoIb9/u0K0BauTcHclvG76tWCBA3m3TIZdgtnwWpKeBZdGgRNSajjcHlioBNeKce0kk0O4vwVkjfSjPhnzHXN57N+9R1BklPC38e30OQ9KEhv6p4r7'
        b'457xKOJvvz/LMXiYk/HiYmmsD6UP/pQRmA6jZ/vaIwZtmuILY8UzR73/l5iiWtnUpNY3p/yNek1SUXpl9JFb8+lOxVTTvlrqh+SsmbUxkYGawA/OTBkrlUn+Of3vf1ip'
        b'MVVdThx88BN9+amOuR3pYVzZuXcLIs/UZh9+Y8OntnVvLE4or3tx59rgjR7mPyy3Dbmgff0Tkc+Te7oXnzmRe2xTgj7gR3XcvzpXtH0mmCR/4/7d5geFlbdnjh62/q9j'
        b'v5x2b5Is8MgHUjEZyIA3B8FrziClwQtchlwU4BRRRuAhcNjHro2APaNclBGPFYQZlgxGTX0BXjPa9RE39hvAmXHgQ2A+vMAzFenAqsWoC0E96i3UfTw2x2uEy8G5hWY8'
        b'6DcI7jXxigtiWxtRXMARcJFnm05YF54WMapXfwuo8AkcQq2G+fz8hB1gW4QdOEjwdDu4JQeN+EWDYC0LLxYifsfDHLPhZiRViwR2VQyrYZkTiPaEJNM2n+hEOpl8LzeR'
        b'BmfgNn/yxRUIlO44YvXKQZ0jXI9lhyFd7gbBm1RwGN3tkUI3wG0XKQSvwgYzpvfM1aARNqXTFD2JKodbEZrsr3iYevPrrBWhEyK8Xbib4EOkAx/MTg2NwcE2HGI9f3TG'
        b'MQF+QnT0Z/zpqsEPRQu7zkYUsG6h/V4PJjy2KYt0uFJ8XuiEiBJ0KHPT4TYPcdXhHl4vhKDE/+mVY7+Rk4Ns5Jwyi7qY94gTHZG8pNsHzxVRm0x5WoR3OfwXef7C5u72'
        b'tBeCCiDVL0CHXId5KGJCfCyYJ5YLJP3g2X4ZD2kMlQBuCUE7Aza6WYwi+18SA+mwGLXICrT7iLAKI0DKC6Nh13u62YUFLnZhltqMGsuAGkqZx9lLxETi1G+x282p2xLN'
        b'lkS/edqVIq5ehJQiAVKKOKIUCYhSxGFfSP9KUX/xG0RZg7vBxiHu9iFogLeJgpsFD1mmoTT5SCIfRqIyMjlDgZQWu80mz0ZqzrxI7ExbICITJsB5YHNOmqDTKGrcQD/P'
        b'oCgS9SxdBte7vgaJZtjAUWFwg2wWlxwv4ue6nAxf45ooOipZSIWBOlhj4haAIyYpQ2a7yMFNsK+/wkBDOipMM558mRJ2gda+pQ0ah8taX61/Lnoqa8Ki7avf5Q5+eaxv'
        b'jUQ855PLWW96V/pnLFu+e9fHGzddfe+LaZfv/vmj76bHhU7ZeXpcyJujvAM9j9j2PBcetl0w80iERPH7ZUca/gqz3o6zHHn9/H+GLgv79tCbqb/b0xK8/MOgL770R3oU'
        b'DvNBIHN9DgZxAbzmNqq9YiTYQTDXC+k9zXbQRYhrhg1MbCq0kdywvtyXfEjysDTQwM8SCdCyoBNsgaeJQQtvwENZ4+0B+Ol87PsxpiII6UskQqAd1sHtTovVKSFAPTiJ'
        b'pQQ4kUYqsRocNzrN4iFwbwy2is9PJCP/8A5sl0Q70DgEXMCAvBFsdqhJv4xLXeNEdYgRcrCFSQAxyAGIa6nhXmI8OiCmRayICaSrwvtwj8KZl4cKYTebV2zqFuksxQRb'
        b'urlSlLZbaFYb87VmFzB8hFKHUHQVPsfxRcZKfKhygmE5OhzopS99FuEKhw+rp5RRKu2AaCzDByMRCwSvVmrNBSUa8gKjydFID5NGtNHsrJYFHfb1gBxS2zDIITnZKuiB'
        b'ORE/86kB7nbOfpoiEYLjluHExvlNOkN15uAGUsm+Kgqi3DziTmzC84LcpwPpPJyTdeiHTtZZ39tF3ddYC1MSnxQ8FwAvmBDJXvQus8DLSFm5ArvM5Xhu1gnQXA6a/UrF'
        b'sIuipsKnBdhdMpogVTDcB46iTA3pSsRNygXEHk9Bfxoy5Qt52wxP1qiXKUBXNp74BC6C6/A0aPaCd0bA7Q+dMsqSIfhfGTXZF38FSjLRoyRYHw060p09hLHCNHA+C5si'
        b'wTYCiuNBQxxsWgY2OL4Kbo8GJyJpxL6bOaOc0o98awVtSkcpO+7O+0b1ylf3kIVYoLuruaeKQnbhq7mvMud3h9Za/fdcq5NuGLvhRHvoyD8+2/bait8f1/z+2bbnmexn'
        b'X3rj2cBX24A/MQB3Xx6QVPq+VEC4XuCFUUkKG2Wov0AnA4/j2rRJiIpWAm+k2REhLZDX0I6DdqKijUTgxHs3YKMcJ9HBLRTlB2rZQnAWHiaRc+FIl8SI1YhVNJaaauIm'
        b'06ALtBWTpwGScEf4DoX0vVN8cL8NNj9yFoW3urRUi9gNs767F2wtlSImgOJPwnOqohAo5BTr87QGkzZHZyxZmaPTu1pdLgU53krA4KHRO5VOlrSiw4u9kOKGWwRPFqb0'
        b'LYNAXVqmHIndVkcXg+ZM4pdAf3lx6mJOwdPlxKKytw4SCHwXaMB+/5WjQRMJsfeGxwOiYWsV3AY3xcUzlADupxGt79MTnzAjHIGYpGtVOdxRBC+WiUWlZeIyjgqawuaD'
        b'awEk4DQCEaAJWcRdnj7lPl6+ImSYHILnV2GGLBNQIwO46gkZxD1Gg02gIQ2ZJ/PgZr4jReAc0ppS4G4LHmeBN6qR+nAK6dZX0NdFpcrASbjNAltXySKxIpFOJh9g14nI'
        b'Pk8WdfdRcMF7pt7LgrUgLbgGr7nn7i8rOAEOOLLvKPaCG+AlcJ6HwKuzIbIESstA6yp4GV5BoGKm85BhcAUHoVnQx8zjQK0J1hDdAnQsmURquxMrFVh/SPeAB2dTfnAz'
        b'mw2b4Q0y8dIDXtT0KjIVXsFXXWIvITUyhUPGznG4j2j+JHxxBrgFroILDAXOsdQUagrcOIefbNhaNh5uzZSnwB3gbHKKBwWugI3iqQzcDzpggyUOJzmPur/RW44ni6Ut'
        b'4r/cBd3AJYJkcBdctxzWeoCbcGeRBSvqEjy9aR7CuLNPUiOpkQp4lYC8ssiT8qciAzxVqvQ2bjUfMPlMgAclpt7z9JWo0gPjl/I3fZ/CUZQdEUJKVTxyYSrFO7BOZ5Zg'
        b'TSIa+7AaiN+qAe73769KJaBGVB3lLWVIaWWeOKp3UoIYlbY4Zxj/iqih+L0hAg+JSvzK0DJKnz4yWmCagZjmbwmdGW23lDA2cMPrlv/sjpfficrN13xMj1u4qf7AMFnx'
        b'osBr2UefThPaDp3paH9pROzYv0rEidTr2eox+ndf/uqf1ieu/37eTbg+YMuu8QuyIs+cDn5rXuntN2+/3fTOP8epDsVebmn7h4+mI+xWUFEnzG+d+v2iW43pI0f46g4v'
        b'jrrXPTOj5YMfOv5e+ea5qb9ZM6G9bWrLFdk/wr/U/aPw3O8/feno37+YvdOv8uiGTT8kvc1lNnxo6/b8am37N1PMVY2p20qEOyo+/OO5OV1dU77/oeDGEc8P/v1ix3fb'
        b'xniEbT9QW2ZbnXg4fXvMwCM13y45czJJYCwwrR7doR/btea5Fy9vbdy5+8uBo+7nCM68fU18pWPsHzWx+wN2/1MzWvbDCe7A/pkvhCmPvfS2YtqeDfE/yWNW3fxWumZZ'
        b'9JGif/+2bczGig+Ud0aOGuJ/9j+0ZbMZ+p6V+hEfA1gH1mvSchHUNkfjKYeN2MvlDc+zDHgaXOFt7QugBexCGERbwTqKKaenw1rYSB5plxYjze9EtKsZvt6LVzqPIu1w'
        b'Q1rs9PQoBf/Yu5hBN/fOIA44bfFcMjm6CWxBomATmTHXxFQjlKgnjg31k+BY9ChETrhKWBvxQLW6zcArKfAGkT1+OcUE4zrgMdgzvat9Ism9GjTDp6NhfYoshQgZAYVw'
        b'6JJfIqtbbFe5LyPd51gatlpQ2VK5Euk64NL84HQuybOClK8BBxdEK4rAHXs0Kwll9YN15OPi4WnUYu0IaHHVYJMHxclpcBqcXE78FnBrBFhvgRejUzPSaYobRoN9lSx5'
        b'b1V+lD0+FgM2yosYYdH4YHCZSy7yIlp2hRi7LCVcj1SNgxvAHb6z2ofR7qGvSF3Zig0FVOSxR6qtHr/UHzGoXwlIpGZ2j9SchmUmR0JZ/Rkvxt8L/WcCaHz0Yv3RvTCs'
        b'pDMcCdXBATt4mFtEQnuQpGV8ybC3Px3AiBljtUNYSxkXOfo4FXeJOcOF3OolWZ8PcZWs2DyH+9VTEVFXRj5MtAqoFWYR2D4vQcqSKXmhcMcEZAOBjrgelxSiguskpsgI'
        b'jubAJiU4nc4vMOC9Gm4Dlxh4DNTp+BnBrfDisujZCxC5RQlR3x5k4kDbmjzWrgbiIY8ghyq4EOuVvSfUU84p9bTbpHrGNkgX5BwSEfzskAhLtGzuk5GoD70kLv+ytfl6'
        b'k1lrNEnMBdrey7kovNzSppglepPEqC2z6I1ajcRcIsH+Z5QR3cVre+BJhZISHMeXq9WVGLUStaFSYrLk8u4dt6Ly1AYcp6dfWVpiNGs1CskiPTJyLGYJCRDUayR24iO1'
        b'cpSNHpgrURXcSjJqTWajHru/e9U2gQRCSLC9lyDBS9bgMxwviIu0F4++sJ8sRdpKHL3H57Jf9MqokZSjNkN16rcAiwk95LM708+ekTJzHnki0WtMksj5Wn2xQVuwUmuU'
        b'p8wySd3Lsbe2I5xRLcHfaMjHsYxqCY7yxNVxlKWQKEtQw5WWonfhIMA+Jel1JBffoKivctW4QqivUN+Y8oz6UnOfD3HzEjmjxJ1WirfSMhGdrwQ3PefFOIYmsxclK8eC'
        b'7XDTvORUQfbkyeCE1Ateq5wMticNnzyIgm2wQxwKjoA6N7p3TohMdad7yk75tJPyGZufzv8xh//cgp4wQEj6fINM2b9d5wy+4GtCOYccf9Fs5v69a5ySgKy+ctYp2oS9'
        b'qXFH0r7xkankXybniXR3VV+rVuruq1LyqM1fJ41rlu45nXyqbsDIj17e/eLvnt3tezS6OGFXQkhS7mubFOKuhEuqfRPEW1TV0qQ3i397OPJcg+pN2UZd7G82HnpDEfHS'
        b'K7nFOpXmrkrYjuy39xnq27tDVu3fJmX4GITtcPOQaHkk71bazZimy71hBxFD4DqoNUSDG0gTbsFqM2ehYYNi9i8f9hLkrDKqS4nMGNIjM9ZSgzkS1uSFAJkP8wzEU0il'
        b'RjsQuYQz2UnW5Q4u0WFykZjBx3fd0HwGIifwlPcwxuFVqrH/7rqNbmEj4ykh3B1NyHvAYgUez+o1ekWWw7ALkNkB0phUJLjngA4/fRbc2H+AwjieyKlfP4m4/6AED6Vl'
        b'Ju68TbGquNjx4+LHTohDFsM5s9lYXmYxEZvmIjIYLsMOL9gFL8ELfiKxl6+njzdoBfVgE9KBjsIrnvB04hKif58IT8XzTEWxKy1RkyqreKV8lDSZaqOo2NKqssLkHCs/'
        b'U0qfPPUobVKhs9Ezhw16cZhvTaw/98yH34Qmev55UCBT+6TqmQnDpOOVXoGfKge9mc8WjtvcMvi3q6MOJat3DFh6p7HJxmyNfOoJWMIuejvE99bGTP1Pcc+quodtnfSN'
        b'YO7A5va4k18JQs8Efn9Rb5/cDzr0sVj/85/uov1thnfIQ8aQ1OM54CYjU6SNBl1h3g/zlj1q5p0ox1hizsnF5jJq8RBXUo7mCPkGkvCZALpK9lhEbC/OMS7jjH19+Kxo'
        b'kqKHhGvQIbIPCXe7zdRLQk9WTwInoh0I3Q8BJy5yI2HYGAMaMsfFs1Q5aPJXjNaSns8ZiG20j4soZKNFi2ZSFhxCKp8C6+BWATU0klJQCnB9GEm6cxJeBKttBCVRyQaW'
        b'Decp58cpeDG2Dqlvkir9nmo5TznkSSCFrc6sWJFKJdYJhfzNeRlpiPpqBvj4qwrfHW83Cd+rGoBA/KVVbKlKfNJ7IT+TFJ6etnQ+uDIPWeDbFkyIhY0cJcymQefAYJJH'
        b'HxROjaeohQJ/VWJIiYIvKHRBF10TPggB9MerQobFLCITGmXDZ8wDzXPBOlQObBZQrIp+YirYQqaX++lXYwe6w5RFpgOsl6VixyE2I0iEBtLciVLegEymG9FeUhE4Tkaj'
        b'56qF1N8qEvECfuL3Q+55f0KR2bERsaNFoqcoyfri9DRjnnxiadZv428n/okmLoFkpIRuhhdoys9EZVAZ8CzcSOpdXJVAmalnUmh/VcBbY9L5j5kzfhq1fpmSobJqjCGL'
        b'IweTm/+ZN42yUhVrRLEqY9AcJZ/yfL6cVnmdFlCSGtN74xuSyU027nf0xZJmJIVrSxaPMMwiN/89Yg69reoWwpbaol2igEJyMzsykI5VYmFdU72r4M8cuXlbb6b+rLmI'
        b'xGdNeUgGnU1uHtctoDsYfx/GX502xV/Ev/25gjY68sl3PShVTf57FYtLyc3raU9RV+c30qhKVbsi1vvxL1oxgk43fuhBldZUvxc9ZwH/mVOGULPEH9HoM62Lxybxn7l5'
        b'dDp90LBJiLIXvTfk9gxy8/nBQbSM+ecCVqKq7pyVy7/9z4vepA+yuwYzKrVfhnAFf/NGzPNUPT1psjBJpV/DBNjXcFtbTf2TKhjsmaWK//Pi6fzNl7I+oK7SpWvRzafM'
        b'qVr+pkLkQ4VQu6YwWarieekz+ZufTStD7aNHDfJx7vzMDLn+3zu/Zk0diNaaQhMXZD9reCfWf3Drt5Pe//DppGF/kGVFvpH9n5qZrVYq20/gqbgrtc1a8qzi5EGjUtG4'
        b'+oTx8+cW/WVyRMj/LHzfkBx5Pv/LL754bc97Xf9MbFi48NqZJJ+X38of/0abj2GX7wX18ZcPPrOo8kBW3P34sLA5hRNO/s+0qc8P7/hmeNC5CcuDs3dm7ww4PSt8JVg6'
        b'4/LpJYLg+a9Lvd8paohI3rxo6dP3f9CtmvCatHRGpufsUyV/37ToiUMD3/A7s6FWr3oz7Wpp7L/8fr8CyiO/HdT1t28yAlfkz7n0UfDte5Hauc+W33xNt67TV7X61o81'
        b'g384v8y//KuUI52iH/aGnZn1ctML98YZi5hLQas0Ud9c+uPdzieev/la6cTI9lc/+v7Gezcz7u1Mmao8PODOpwH/OBdsPjC7+V8VNV6m+0deYPz+ImotqxlT0Tgzcev7'
        b'+1e/4P3D75/89Mv3wm8W31v8n0/D7y3/7sJ/fMrKlb/Jm5mzfOLmFWsDjz15Mf/TN1ISN++6dXzUnSMlTZOeP3XwozdePP/6ke+/Lv7gpZzvTN+1r9o3pPLfVVvfvPPq'
        b'ppsJgn0rQ2XvLp28+a1vzKaAFePX0geLWrRiP6mIDwXdC7fAE9EKVZyrFwC0w7PEzk8AJw3RsD4Grwp1SJxCZ4GLcDvJKMU6ATINr0enytPkUUoBJRYy8NZkeI4vdz28'
        b'4usUUStgO8V7ty8WEeVrUfRIBCRieC4zBXRyeA2u4WArOMRHfOyHm0XRCmka6ErlF8QTUH6whi1JBJf5BJthW6llaXQfzwm4Xc0HaewFN0JcY5taWXgQrLPHNoFzT/7S'
        b'MXX/Xx728Njqo8ghOYnYXeYqdkPFeFqQr78XR7suhYT/DkF/Q9AvgB6NpGAELSRPvLCeyQbQQURYC8kUeRHxSfiiHNg/URX286LbMd6G5wB0e9jtwW4BMfJcZPZ/YfoU'
        b'a1yHz8lkgzqnqK9Fh0F9RP23Ua6iHrvUwQaktZ8iwh4p8W0/I/B7xL2AAjaAlL6bGWOI91oLbsNDZMSJ+HDBZS124/Z4NWLARQHsnJHLj8m3RaCyHENqiDE6lCSe1R9u'
        b'YIf4g/MEDi8sZBWpND5Tyapn2KV7gZfA8C9s9iWpZGU+9sUd2gKF5aUIT5HaIG6uHEzpRy7RCEyH0BOx9frgTVN8QZJ41rfFT+zJABNFZaHKpCebtum2Dx+UGlm7rvnz'
        b'978pnZHeOOb9z76qDf/Go9L3R3XxyAEjTnyenSzd/s75LZfua2Jst//SMPGCz4+dTcPH/yOu8y1lsKbWMDr+zRe+PxG8+OKzs/4x+uoJjx/M+jMe34deLn1i2tyPj4DC'
        b'1pzF2pRnlx/+6YPQbz9WzD5W+Zcrlt+YLzdtXX09e/JP1HN/iOES86QeZDAdHgD7wlzXXsWD6SvATsfSq7BDT0yvtMSVTt9hRRbvPeyMIcFJo4fg1TpdfVKwtRwcS8dj'
        b'evu5kvnwIFm4DDwNLoFtPQnhOUu0EoFBQBQLOoLBBeJmpccIcAq+90DtNLLuJTjDztJNIJpyKryWCZpi5Eo5bIzOTpcKKb8INmf4JDJjPwd2xYCmTLumww+n1CLqaGWp'
        b'cLCZQzb8BbDBYREG/ddB4LEhwsGz7iFT+BeIA6YinxQT5ySD5xIyQQw/9x5DgnE9Sqt0ZWye8wjT9bD0wP+fv+VnGB5X7qdebsy6eFd2J8uqXocd4JhTt2cov3i4DWxk'
        b'dXqJ2xizwP7XJKZ7QpM09BJWwyzhNOwSgYZbIkT/PdB/UT61xBP99drGbuM0gmZ+eS08lM9phBoPMqXFWyvWiDSe6ymNl8a7mVnig67F5NqHXPuia19y7Ueu/dC1P7ke'
        b'QK79UYnErYnKDNAMXC9aMsD5Ntr5tkDNIPK2APRMhH+aoGa89BZeXC5YE0KeDeznWagmjDwLtF+HayLQGwbZrwZrhqCrIA2Z0Swd2u2bzkN8htqgztcaP/Ho7R7FLjz3'
        b'NBISk+GW6FE59CbsqyMOU02lQb1Sj92mlRK1RoMdekbtypJyrYt/0L1wlAklwj54u/+Rd/45/Yokh0KSVaxVm7QSQ4kZ+0zVZpLYYsJrcru5Ak04iURrwI5CjSS3UmKf'
        b'oamwe3fVeWZ9udqMCy4tMRBnrxa/0VBc6e4hXGDincboVWqji5+TeINXqSvJ3XKtUa/To7v4I81a9NGoTK06r+BnXLj2VrC/VUEa02xUG0w6LfY4a9RmNa5ksX6l3sw3'
        b'KPpM9w806EqMK8n6dpJVBfq8gt4ua4tBjwpHNdFrtAazXldpbykk+d0KejC4wGwuNSXExKhL9YrCkhKD3qTQaGPsK18/GO14rEOdmavOK+qbRpGXr1fiOf6liGJWlRg1'
        b'/fuEkIWKuYzjZ3s5ppZVM8TF2b9XyO7Of7Chr9fYoDfr1cX6Ki3qyz6EaDCZ1Ya83n59/M/uuXbUlHdeowt9vgG12/SsFOejvp7qR4S0CJVkcgvcDA4gYdXP1JagmN6T'
        b'W07CPRY8OxIeXQy39qgkeIlimUIBW2NSaSo+HFwGO4Wrq4qlNBkztybhkL+G9Ew5nnbRnElTAUiNrwGnWFjrXan/SX6PMylxpSysdyOeQvbSV/fQURb0tSrZPmNCsTBS'
        b'napmLoRe2DVl157QC4t3hya0T9l1fvGUXbW5xdJXb6UPlv3lvlRM1nsqnjbAd9cDZDCQ0OZaZDDs7C290+GhArv0FoF1ZChvKhLdp3pEMy+XD4OjWDbH8+vYIIG90d8b'
        b'fbHUrkYw1CBg4+aCdSJkXphx684vwEveJVemjOcoFt6gDQMLSXgMQArSbnsj0BPgKbLsFKgNnkV0jxhv0Amb0uQeeJ1e0BBGp4Gt8GmS0Q9ZJnW4yPHjJrCwdTHlUUXD'
        b'3cmgkWgThaipedWkPiNdSAnA1hWwk8ZLpXU+KhrNTaXP0SPyzMnpHdGHf2IxmQSB1fKqYHe6VTjyKV1jmY0N7sK6/8kNDJ+s0Clcm9BhHePw5NU4f1Sga6zez9Wg/ylX'
        b'WIPFawPYJ12RWGPHCBNSkwqdzdAzVLkSHTYz9plXfV7nmJv1IPRnB67QS1hNSd4jK7Ser5Aox264PKQ+2xz1eRDoMnTlGAFTPP6rMJrqNaaHvGqn81Uy/CqHItfPOFle'
        b'sR7htNyE4Fr66CrYm987R1tRqjcSMfCQWux21mIErkVPHixpejd5z8sd6B3sRG/7sqA2gQt6P9ynv773Cmd9Z+oi3MQK4FKwbcw82Ixug0uUAIcTzc4ia0nDgwjcroJT'
        b'qXhFbqqaqgYnwXWiGuaCnbADNqXIhsDbWHmP4xAONDGpYMNC/bTO1QLTIpSoLqxZ/pvf+NTEius+mSRvVTyT25lV+3noW/MmaYpnPP/yAdm/586QtoTPTK9P/mxr+Sxt'
        b'2eQv397+bvZM5qeo4DMKVmh4KlZ//9Yknc/lH44rph6bGrPpx6Ca8f+SehFbZhQeUOiBw0AvOyDa0dAMdvM+i9bR4A52oyID6XIK79GHNxjQAM5NIR4RthxcSJNFWsH6'
        b'5B5//7JEfo29BngT7if2ViC8hUfllTQ4B2/6EcySg7PwEu9qAWdj+AEB7GrZDGqJK2Y1sob3OzENtCajxsWY5i8mL54B2k1psCXGYznee4GLp8FN0AFukmcLwC54OFqe'
        b'PGuGy5LPYT7ktfBsGuwkC//th0/z+E6W/oPtEn6SGhIKF8ni4NZlyXagRoIKCamN8ASsdVtv7DFRVWvIM1aWmgmqRrij6jAxCbvwIoGNZK3WPshmz+0GrY+1ZKB9pdYe'
        b'aN2ODvv6gdYvHg6t9gr8LyhHMwvUhnwtH+rgUGccXN5LVUIaz+NqSQbtqsdRjhzLh/QeEUbaC3HOXR0CT9glN2gCJ3tUGKS+gGtwo37I5K9YEh3yzk9JPq9EB+CRtjfb'
        b'R7629seIRSw3KZ27lJ/8zu7p1KLR53MuFWSZP5r7ckfBs590+i+Z+NOXr8xIE8TUDw71XhiRde7Mh7dmXhz2V8/Ur3Z1qa+vWeIxMPPfu6SexLVZVA66iB7AUYY1RLUo'
        b'ALsIr/rB29grMDkGT2wFJ2WRNOULm1ktYoYdvGMCx1ifJ7SNKRtsAEddqHuglB+/uzF5HnY8wEaaAm3zuBgaXAC14BJZvh0eRpku8kuZpmWC5phkeFjs1Phi4UHhZB94'
        b'lfAgbAKbxtuVGbgftIMWOg3eGMl7WTfDPc7GTE2l7VoQPMtHeK0B9ThIjOg6QyNYXtWBd1YTUJGDdYjTnarOSCuPCiFJv5wz/fIIveU4iKN31DH+jfMiS38E0lVDevFF'
        b'r8z/Dd1nJzp09MOg3W4M+oiKSNluYUGJyazXdHsidjAbsKzvFvIyv/9pS4SJOcfkACcTcyRgqf/pSiwZ9+Y+wTGffXhqukaDrRvMeC7qAm8NOsX1z3IvX3med5PRecos'
        b'Bwbkqg1FfTnYyfT2b+VzZvGXKHNkmsWAbEl5yqx+onhcIoIcObHljLO5RQBJ+6uvUWu2GA2mBIlqvtGiVeFAHn4RBI1MopqjLjbx99TF6KamEukvWIkymB8BQp59QIhV'
        b'6i0xYbQJe5EtA099o/pt7l3VfdU9lV53RntXdRddF0/+UHf/qxPaTvWruSfVd/NEOpFGlFuvSqbPT1pKRbLek77/UMoSnJgDauAW0GSAlzJ7IYVfJS+394DDyBpsAocH'
        b'8DjAg8CRbN6R+jQ8MDxtUGF6CmjIzICN6QrQEkPiNKVgkwCcTkF20S9mRV+1RpOjzdXnmYhySjjR350TZ2I+rBrci/jd89mZUMjz1C58aMeH3e7s6Fo9ziVZoTMtYce9'
        b'6HCpH3Z8zY0dH16j/yrD4QjBJ/tjuGzio0I8Z+CJDMeiuXCei3fq/z3ew9lS5mVKeL+SmXdDEeNApzeoiyUabbG2bwDd43Gd9P1TPNdVj/Trl+swz5UefAjXqQukfIAx'
        b'2DYY3EDi2Z3lkGzer9VPJhKzBNRr7JK3EtzkmQ7a8slMcICUVUF0KmxGv43gVkwaaHbnvWmgxSMA7qZ/OesN4B2cj+C+bMJ9vbQwRZ+s/10GxIurP9cPA952Y8BHVuoh'
        b'u6HQNsplN5SfX/TaLu4e5PbDeoQOCY8YLCtzEbsh0nPxFvf4YPMsRiOC/+JKF3v611ClqOU1gQkvetkdD/GGKwW6DkKPr/L0iKix8i996TGO+lDsWf6JwU6PsHbQkzw5'
        b'wkvgjqsUyASneF/VYXAJNs4CNoc6SChSCI8SVVC4YgQ2v/DgopsYiBIiWrzmUQoaJavBqV7b2/RLf3klFoPZpbtM/dHfElF/9Ncnq9IRfVj48wRHu2hcB9Hh7X4o7Kzv'
        b'wyisz2v/SxSGrSLDz1JYT2TxY1OXJDIKK2F6g6Q8XjE+qh8MfjS1JaweyRJq2zn9aUxtX9X1pbefo7YDnyFqI/PVr8CTYD2mt9Pgei+tA16P5SNbt5RLvEGjG7XBuuE8'
        b'/tnADnAVh3nJFH3oLT5iEl7v4gI4ADY8BsH542Z8FL3l8utt9er43jl/KbnhVU7+0A+5HXcjt0e9VRrceyKyR06OpiQvJ6eby7EYi7t98DHHMfDR7e2cKqLXGPGuQsZW'
        b'fNiMD1spu8+1W1RqLCnVGs2V3SKHE5OMfnZ72N2F3V49DjjiSyD2CtGSCFITZiKfyLfKr1h0w8X/twEdVjL2eG+RN8fgWE7nj4nwZUigSJ8jE+Ad4RPhF+HnK+L3T9wE'
        b'uxJ65hbDSxnIdE2fAlsykdSMBLWCtUsptwESzMpJlH3VDPfxWH6Dou6B9mkY9m4iawM/kMyuwAsaYudkHp5jYTRgJcxF6VIiSefebcYjzk/u5fw8hQ6fMc5Z4RxN9ipN'
        b'Bq2g2XXxixZ4zvFdjoGIVC8P0CoFZyyzMdc0LM1wDzceAep6Rxw/LNwY1oG9btjmdJDgFrJH4VPuW0v2rK/6S/Z6woX3DZv2U/KhgEHeVGRSEbotKX5vhGolid2snSrU'
        b'ncW7XeLYzcW/Zy9QxXgp0PVDEwVfh1zL/2l2uPRaUVbOyaEdRdcXr4vcrXxh0vinmmX7Mk9POZawfPDbUYdz/y17kLHW58twn+qbC85Frp85IfUrZeX0T4YIw7wiPlg8'
        b'Y8lnT9wYvTd72vyGwduibg5dOiMmJbvi935dJd+O72Y3R2WXjos4NuHLWd8HClKmRvsEFyw2CmqGfzmr3Oueqbw0Mvj92Se9Q32ur/0JCctnOE5AZvhO1qix4xf7RAWV'
        b'Tr9vDTxHPjRrMUNxmi0MDuTNeiqcj715eVkANbL0nge6mZggsM/8vFISTMmSCllKokrUzBHwkzyzKjxhU4ZcgfcHdaxRBlvTPOA1HJwGTlTChtlgu2AUBdaP9oSHwPrx'
        b'pKywkageWdsZKkklZnLt8ahH/D0o8aS1QvSC9O/nL+dXDOWGFuIem1xJU/Q/F0pZklIcg3ondhXpncX0ogGkd37iPLL+w9h7J+Sw7+d873y29H+9d0bWpz2qd/ytgwT6'
        b'jN9d4vcTeas0bFQzvwyV9Dc/TPp2SPit9P95I7og8gP53YKYdw9/lDDufH3F0aRXbsHReX8YH/H+1RmH3zogj39pvuSvbOq+4viFhSPTXhgz5PWYl0/+zfRV6riR2r+p'
        b'DgmOnXr+d/fGW48NfmHKzZ0vXCka9/2G+R+vis4qLwl9SptzTV/6gvL4x8Fv/YubFzpK+02LlONnax4YBc7y+9RkwithDm81OCAjbvz01UG9Y5rsAU13TPAs3A2v8SOW'
        b'm+BOUbQ8AZ7HO3piohBQeH9ReAXsg7fJkkpWwRPRsDFKOgl7BPEMuMnpGX3j3H/twrSu8/yNJrWbSxx/h4vkNXMkItCfzEH0pyUMnpHoTxtPOwUL283hSAMXefur18ul'
        b'jWecoItf8Kd+hPM2iWtoD/YFV4DTsCWRjY5Sgk0uBl042MeBU2AzONq/PpjYL2Y6Vwf6RXjptj+AEy99eLx8PsiLwuFW/vG6qpBxr6URjjQZhFTk4sl2vGz3hTxHhqT+'
        b'r3OkZv+Cjd7jZdeYpAGmJXP65ci2rAJf8ikiPZsaQZZvUhWPFRfy2GT2GcglUnjxX1Xi8MlVlBHvak+ezC4UBGbQJHix+IeZI/mb+VFC1TMsCV6UbTWVUfw689fBoRDY'
        b'BFpAOw/HDjBOBdvtwLZ2ojffjHNKVy1e+FImacYnFnhQk6oS7M1YLLvGN+NvDVP/LzbjXwU/9duM//Ss9NE/+8frArIQ5Z/vjZa/QoCNzXrl1dev1b55aeIrg9aLv/7y'
        b'xMxxoYL3li6S3qz3H1p9S1L/2u13Kr7yHOpltX78/IO/6euyPbP+MVu8z/tThaD5zYwPdW/CJ6RVN2Q7vrx659z0bZfm//FT+vWfpk78/N8ek62Dl2xcI6V5R/86pPbv'
        b'SQNbwAHH5t6i5YzWF55xU5F/9SJEBEs02h4sGemOJWspD46f0UxQBOOJmKCL8WwPmvAQ0AMmv3ThMhcIOWvn+d4Qss51oSGygMyouSLQMZVHkJQMB4CoOHBoFdjgNjMS'
        b'T0gha60WIFCpF/DLweOtSjBs1DHVDDlnNRw6Z9voikgzjdPMotro5WHLmGquGi8bL6inzAzeywAp+L5WQSGrEaByBIsowxC8YHuRl7GU3zGIPMN7uQieIgu0G1614p1q'
        b'kkgZOP91K2tsQ6mIq7LiDDoTkj0X8LuE1R71tNUDLy+v8WhGOazCRKpsN3rLRpJfUId3hWGNb+D9DfA7KgyotgKyoD3OL+qTX4Tyd6P8c0h+fp+eJGfuSGfuiJ/L3Ubj'
        b'xe3rhXwOdI+y4v0UZIvsS+vbd+LJtVIaz1AMu/z0VC8lEjJabekcI95Cef4DgcWsk09ybiiDyPcc7nD80IgNVCNW0KUeRjUmS0+twbJSa8Q7LiThayFeSF2j7RYvMOjx'
        b'CbEY+LyJPMX1rAbaUyxZ2J7MKMPrzRjx4t3ddOEvnHPfLcZbnJjG8ROUAzBtJhAiFZHQW7xRB7/dRwDZhIEjE+VCXM7E9r8isvapyD4YuhV0gLY0shV5fBReaAipFStA'
        b'swclGcLBLoZxCwRxhk5grrBSJpGGnkfh3ZtI+zN1drtKSdrQON7JmXQ3bfoZG96HfFWOuSSnuMSQH8c6tu9ksXVI7D7vISvAbXCGryNoiYEN/LKWWB+mRoMNgsqnKvps'
        b'CeR0ziNqoItooxjbfBrWindIojVcIYV330F1FgThnTnoYAoLbXyHuAeF9i/A0ugBM6qCTKP7muE/RVCl0xcXS5lu2tBNF/zcZ+GvwV9FPi8Bf5aXvbc4sq0K2RYD7oM1'
        b'4PKMHLLzfGsa3rkafVymfWP40UMElXC/+SGTp+l+J08/fMe//N6Tp4VU3zmuPfMG36oso2ShkKZKVbp3q3T8TV3V89SsicEsEs6e3d6D+Zt/S/GgnssOx8I5/Zh+BaWf'
        b'euAsbcJ7DJzftvob1WtkTazTpd+o7qlW6szq+ksntR3qu6qXdDFvfY2edqpxbOA9jTzwpPql3EJdZNC6+vJzQpE59vex4+Oejk2hUuobS9siR7y0N1A39mBBkMkrLS4v'
        b'ls0Po5bVhXx94EekZ+NhdR9wqoifcO2xiEy5lmvAJeIGFTCgPjpVPmN+z653DNy3AvCaNTgEN8ONeMUUT7AFGeOwVUajJKcYeAa0V/JC8JQRXMBhQE04RpJeC45QwjXM'
        b'8BhY98snbQ9YWaKZPJHfSCJHo8/Xm3svV2xfMEtE8/vriOgI2viMk6X+P03LxsXMZB2vq3H53XGbmo2RqiAKHkUf3JwJusaTxZzxfj6gxW9ypqORJoHjwjVgK+xwwwrn'
        b'PrXYH8cjBJZ0hMPypYyyW6A25en1qF4XKafw7bvZq0eBtqJYr6vMYO07XFEsEbvD4J0cEgBB1mMCpzjKm8mEGxh4PQNu6B+0cC/jPVOI8AvEcWy4OtX2yhHoYpTGZ/lq'
        b'THOp1EPWOvO0GOwVzO6BLqyXkD2Cx4Cr8Go0jsV1rejA2aBhPot4vw7cfuwmK3Cp20MbzDM3fjy/KdZTLk2GO3r4xOVp4+JSeBMUKXB+FrhlGDtlITz0K9sr/1e0F6od'
        b'L0NX9GovIjPh8YG4ig4V03dQDDzDjoX7891CAp17vmEBqKERoCPlqWK4lTJGmTHgs3UMUiKoapbfBMrKIHhnyrzwxkul8VYab8dEelug7B4ZO3Zc3PgJ8RMnTZ4+Y+as'
        b'2XOeTE5JTUvPUGZmzc2eN3/BwkWLn1rCwz+WRbxyQCM9QF+OGFjKdQv5oaJuQV6B2mjqFuIlP+LieZHv2fvb4+L5ntHibyd7FhMxJySr8xCyZuFFcCFtXHxaTy/BG+BW'
        b'MJsAOtf0301iO7FoHLsQoU550YkTtPHlnyGTuHi+I0pcyATbU1bYsQjXwNkJ8Ci4Ao+ysWDjkv4XpCRbWtPOLa1RbR66COVjbWlNlvcPBttB+zzQTOaKw+0LMjznwkvg'
        b'XDY6XMr2AS0MBbcURsKr3ErQtVSvKRzGmnAjPnvr0Deql3LbVAU6fuMSse7jdKTRnGObF16TMnxoxGWwTxctT4EtsCnGA9kbnnEMODQK3iSxheAA2OEdrZC6zv8EtiC2'
        b'ZJL3z21KrTeV5Jj1K7Ums3olvxgH2ZnHFcurjL919gvT/yCDi+sYpzX3C9ItbttTk93nu5aJwIGBeHmxFqJFoErLFSlwE2rF0UbBWk+fOW5Rf+7eX9Ye9efi+0Xd6f2Y'
        b'AbZu3gysCAT06c4BSrK0Ezg/C5xIk8N6mRKvpcdRwjDGC9yOJ+rDT9XBFCKkWMMIVcS2iCEUWS1AyIHWuHGga1wsNZzyyB2lpMGeRLCZgMU8uG40enZ5HLjEoYewcxzY'
        b'SYPL8GSOBePnuEQkz7cK1o6m8KoJlSnkJcMCQqhYilr8V60qcbXFvrX1yUgphRRz0Qt5quGFeVKKLN4nm4t6/AIDrkkovFygL9jPO7Bj8TIKVIi+QFUc4GVfp2+simyB'
        b'XLAvXSV7p8qIqIOEDRcCW1ka3GZNAZ0yIcVF0OB8WDTJ8HZ+Eg6ET15YrsoOKq3gSwnW48UEqOQvE1TjFLPtyw4EhONVHqisZIVKnBq+kNLLd35Bm95DT4KO585u60rl'
        b'pos3/qTRrSr/rFBbtmrx0gfc7Q3N67T+72+QLwwf9vYHkZ97Pf9kedDrW9v8//nXL/zKKr8OXPXnF56fW3HNGHpo/t3xnpIhO8KDN3znUVLWVtkRpn9j8dWTL09p/enB'
        b'S92BUcsi4dKdM14ZGPO6sv3Loq/SN47d27Hw7c331pyYsf7Kb++9s+jWmE8nKL/L+E3LuY2HHvwt+i8h475qO7K16/uoURWnq75PCd+UYTCf21215tV5/xj/+e+WeEeF'
        b'F2/eOjttXqfvzh33vm9a+mPl//ylpv1/uv5zbO1PdJpsekjaDqmQzKAYO1jsRCARsMH25Yx25jLCulVgW7bb3sWMTA/3VcBrJOYwnwGbo0H9eIXbfPITKSSrId4bx0Db'
        b'459noXJxCDTcEs87V1vN8HSv6SD6WGDjRPAEOMSvO3cuZkJaClk49QZHMYX0NLB3xC9Y2v2/4Hb1KUWCRpuD8GZSfOxYgjQJvZFmDUfzzleO9mXFSHMUI7Tg6OE0Q6Zk'
        b'B5DdGsX2qdzG1/9Pe18CHlV5NXy3ubNkMllIQggYwp6V1QWQHQmEkAQlAuIyJrkzIclkJtyZQMCJC7HODKsLolhFcQVRUDYRq9Z7rUurtlXrMlWrn/VrqVZbl1rR1v+c'
        b'8947mYGg2P/7v6/P/3zkYe59733vu5/znnPesySwEnOSEnd4A2qTx02RBnvR1L/ie19Qf8Vxye5UsK6uPrHauhTpLLnNvr2zHnaAx8rmlZeSUjtit0fGThgrccN5Sbtx'
        b'vvYoOUjRtzZchPTAEO1K7VpuSKu7yTTFlLkk/gbd0Ed5DCwZAyYJwwFGkR20hCW1PGyB/xJso5Z8Lgdy9Yc8YZhe0oU2Tv2joiKa3/WILHgw5BLVxqjUCs8BMwpQMqMk'
        b'pdoUnjTRCFxnFAE2h3GcYSisP0UdPGn8VyImTrJJoALHbeYGLnNrihp9AWAomApVXwFrGQUjxi2dHR0eVZ2J0y0RQyvHpZCnKwSUARYRbFnjiduDHtTsCmHs1VUtSmi5'
        b'+jLmFxXPiRFpoYGv4v0riYXqTG7LjaIZvoAEFrgKYT0K6NSQ5toxoqQaI2jXIXNRRy4la8rbZJ4brG+X9AP6wSQqFfeVhMgcZxVpQKJUOaBU80mMxgI4wgzCEGOkQhGH'
        b'mIRsgtoIMysoEuQQwyIGwm6lYG84g1TCMnhKYajxPeQWF3GKxRAMHCuectH0rnbf6LLpRMu1+JunXjh01MXFF14Cv2UleD+6dPpF06cRZXwUG0tyJUPwBHwakspxOehp'
        b'UJuWxy3NaqCzI25BsQ5cfIFVMCtE4EtxEeqJWztQF071xy0wivCBzaz2u8jsTHQrCV+7zcx3JWSZomT6aaBAnQxJSIa38rvH9SNPyNpedLajxUiraFOGVEeeNK0cNF+7'
        b'Sd9jSxATKae9O2kqgMAWcjgkuRmjoF6NrIOTCxbjtRWoQSenjg8LCpDlYc6NBkUCvK3Eq/F2QViAN0JXQRjlkdndxIZAuWJ/mB6eW3HeEvOrcNJXd7Kv/IVhHu7Z+1tP'
        b'fG9YBUm1cd5xTCgqotmBwaSF+w7BQ6ihxYeHUx6fpx3mxLPS4/sOIIw7O1RPCC1cccj39460kyTWDvKE4SAfbDYhny13PVKpbS4rnl9RQkyhtoGNuJzJAxa701Ic1nb3'
        b'bVuOkal7dRkALXHLRI9EYRBhrJdZtoitcqt1mQ2eWRSZnlk91la7YjVTQOpZAaWhZbltmUMZiiEVIZ2mOK+2L0tThhnpdMUFaacRclGiUIwZSiZ8k57yLEvJhmeuxBNJ'
        b'6afkwJOMlFy5Sh48yySLcm5ZljI8IgK/gDbj9mXZyghKFSqDIdVPGQnfyNCCImUIpHMogEcucTaj4mlzYEo8/tAsYLMSizAlDjgZqCaE6hTGF4XqeG8ZwKZehqnvZkDJ'
        b'Tz76LfxTP+aIqJ/F9YbQq05MchJcuQlOKZJ4sKOhyfNcgnkS1gxKatvo4zOewOhTY3FzRagII1wkQqcK6ieEZkMNzX3b1MXtHb6GFr8bMryQ1IDc5AYkcvRtypdt1Bxw'
        b'mVCZqD1uceNGQLBwEps+hJVXevnGNZnJNePHKXOT6K6T5gaBXklUx6uffvegU2Vv9HYzhZFJGEF3JKYdEX/XUpJK80aI3Xl4tsJC6oZhKbQJ6pkKCgeEKdyKfHhib5M7'
        b'ahU5LOIVkD+vWHv4YL5iY1/lcWbeJVA+xpY2xB+O2mP8mDhfekwYPYY59UU4Vf+MU8RfdsxyWWk3xThPvMKNl8UldwCfqIaCq1pgU8VN2LQ3Ie/1NVRAx8lky27AN7Av'
        b'e8gx/luiqfNGOMZG8YsKMFzHgJT1mPxNbcIxqMgdJ/Ch1UhjGGJyfYFiaZuyfR5jVn+NrbAEO4GAQNrBr5h6c9j4uCOx5k8i81f/AT9/FA0GEZudun6wxH+xgc29DVS/'
        b'wcZYsbAGoG6SWqj+kzspPfUt/HyU0rR+xzcNSktZ3YkliFqiUVhWUQmpkCitdFyQGwVqK2+2FUOFh02ZHh4o+IPtDR3QQoRO1myZRT4woCJu9bA2nJIeuArFc38RDXNd'
        b'joVv59dkJ/eDFZ8yyIlujGXdEBLdEBLdEJK7gUPOs1jmXuoItT+1Gy3o1SlkDj6yKarAn6I+uypCzr+l9iP7uH6w8k/YCBJKGlFoZxTIcrXUxA1qEdInLM53N06QceoT'
        b'EozFJCagWwTonsGoA0n9ClvUkFhXaW43kFgtIU+7223irkru+51cqhbo1DeJ4yAjWjoss/4pwNpbeN9zdEnyUhv9XX1js+QvTcxopTGjgiLSjIrGjEpmXgM1S7WqxBu0'
        b'qzm3FjYMS/Gnd5ZhLIKJsRB7x4KQ+alNNdD5QJiaMjNjVFyCg3wUpI5MoqrvCMpqAle9Kazraw+1ud2NgYDP7U6XerfQnNTKWAaDdK9PzAXOA1ZEAepRZkoh2zkv0r48'
        b'Ura3wj5zk7DJXEeVMCzvcwlKcTUg4xZ/KJ6BFLriafI1mAb0cVsowA54zf3gfRotHOsCri+5o6x6MMBRlpTAWc7jYIRlqDyh8bSQihKNV2ixKMJGibginikiEL1kqY1L'
        b'TeNO96NBIouRFLd7upp8ncGWlZ54Ou5hbmAuscbgZ+QDGjrmD04dOpROUAE+0njEYrAD+WBbMLuWgb3KxJ93++qamg6vciXzlICEFakbBbYpAfv4cYITicNPC3AgXa2I'
        b'u0ir4RLWLdo6JFjzwLL34Kk1P4C7SOi2dMthS1hok1WF4ANIRWD0hWA9u2/m8TrFeAM4QkYkvsIVltnzFa4lXFc51CWhNgXUVghlWrtt8EQOAy3RbQ3bcHDD1v4c5A4T'
        b'/2Lttoft6hNhPvhQGLUx7JBDnML5pbAd6RXgWF4KC/irQE8gP5TQwpuwSefTCKDHLMOQ4Cqxx50AF8BStvgUmPK4NRRwKy1NIVJMoD0BdpUQrK3GuB0zIhAFidBknM9f'
        b'ORLx0H7jaAr4g8zEMc4reLYBhcb5JvUv+FZoUpgjrWrz45Nspuj6tUAyPYahLIqYIeYQMFNw8jkUalEmpR6HwIIcpG64RieIUETC2AZF1pcIlZUlfGVJ3vFq2NSb+8ze'
        b'qB8mOvcpx1hu5KQZdYA0CO32NDS01xBuJlSkWvEH3XjRIqSOJEUEO3VxX3KAMGzNz0QD5myiTXJabILT4pJczkwpU8qRc+Rsa47DJsETC4tNc1e/vNn6fUGM57qxRt9Y'
        b'tmJ+ea2FGzBDqtQeWlhfwlNcd/0e7c5SZlFG1mQ6RQWtaZ4JH5TI3HhFrtfu1h6A3IiptJ3ZGGHOLJHn0nL1ay4X9N36/YNOcJNB2kquBIoI85v4JNcf7Q1tHpMwEXoV'
        b'X/o4wzVmdFIvoqXDLn1/uCaY1BSHHhulbRf09dqt2qYU9tfEXcF6Lon9zaQoj6jQD8wusJUSMK48c5+2zMJsMr2iwejK6EQN8lgVp5IOV5viUjKuRidsPOG4rLjznM72'
        b'9tVGU0+kkGl3Qa0LxsDAnssnsZh8L4vJZAzwK5K8QTIOSeRa9SPO2E+JQyCekzGeFgIs4j7Zyn2Fhs2NBLs/QT4R8Mns2fE8Ehp+zJQStJLMF8L/NbnJXTp11zrMvYw6'
        b'hD/p3mkH+oQ1ZG5iTvk1eSnVJbL0TZ4Zx5ZEfBi8oCn0pBrn9rmUGN2FeMztnp9Udf5xPU1k6rvyaTSPCg+coBP1xIhOBHyvDo/28uMCnl0CnSQAZTUeZzGpuVcntJwk'
        b'RvTSBOKIEYmUQhKeXE5HGKeml+6x8SyEC4rk+urSKRE+V+MBcLlZz0km0Op2+zx+t3tx0hjmHFchZehbboHdCHHNphoA4QMJd5WT01r41u2+IKm+E1Yn5TgFsq7yO3pG'
        b'qPui76iFkXTYZMfx2wcCkToM53B4YjsYgT+jEnuC/XsmtAgyTTMn1CY6ZJvoFDPtgO5Fkvst1/etDJYgrtYeDCVQXz8XzxVqj0r6TSP1DX0jPtQcNBHfFrFVbJWWWTxM'
        b'5wulepJHarUiDmIpOo1HpGhbZmNyOECEDDHaSZ7moHmzxbPrGls9TSHyHWiM0Q+QFzWzTRl31++TFnkTUyKu6X9ipacuNGo+daFRW+9+c0o46OpTwkG0OAJJK6ywj+6c'
        b'DAMlDt598LM6M8QZ3JfBhUrAh7Y51LFMg5dwkRim4wlsILy1wFvF0O/lW2Xi+pYhLdnL+WE5vZ1K0vpL4udsxLnRCo87qoA/6GKarH8xISDumkm0YmfI0HFN8L8/BLWp'
        b'UkI2JQCh56L/KKU6+ZgZbGTa8bBZzCfTcozIOy0VVHsJtD6iQvbSYVjSpZKBxGwSo8GcYmcphyfAFdnabRX6/jp93fya0ajhtn5BzYokGmWWdp91mP7I+L6htCAJSokY'
        b'oYNDIFBEdigYH2j228RIs9HJ6YJAoK2zI3FqaeGSdGII8IytKgpTaRxfAI4XEgjJwsh2KbS6w6Nuwlt7Qgh3ko1U9lGdV/byjcBdDf2O1o1mH/Rh/Dg60Y4TQKUM/aWZ'
        b'oAIoENWhtbVaRIsmDbG2GzGhtl47bFC5+qaq8tH6IdSJ1TeProBPblzh0G/R7tK2pRw8JeAYBUuwhXMk4BhEIMUTy4Tqr6Rkr5ZHkfnjUPEcwYPuLabM8Ng/ZpO3FzTN'
        b'buoMhgLtLWs8SpEP2NgiOm1Xi4o9IdXjQQ+xgd6VW3Jy77SUfTI60CCPOWjb3dLsD6hQR698tKjBrxQh+4z+PhoUpYUF3yoqNdie4pLSIsZwp9p7JzUhtYoGny+wKkgO'
        b'etQGDJyFjmr9Faa/miKDXA+mFgcgTWeS4tKaBQA77+J9WlIdJIT4oSHiAIdxMcnUc7Mxx2h03EuqQNeM1q7R1usP6QfnhAGb6Q9z+r4r9GtJ60e7T99WCOthc/MVmIHn'
        b'RD9/7jnnpoCcbILcJUkgp/QeTcleCx2K2ZeJpN8kwwaIB2I22BwlOgITFatiQ05BsSsO4ATkpIMw2zIrbZM2Wh+uuNOAhxpgedTayhRfMAmh3N0cqju1wOpS+FvFbikh'
        b'oBsO7ADfgnqKXDNPRxHIQAjqhoRQblpYMN4AuTmAAyZCQlFAWAz68Y7SwGYoHIogoB9MxCd0DQoL56AqgQW+tJi5SCARWsL1Cmu98GYTz5u4Q0YZeQVCLQnxCvGHCMbe'
        b'Z+xMNO5wk2zaDeuK7RhIIplOQSjjP2mxdKgeb0uXG5UfiRGMC/7gqUn+sMA7JNN4UBBQQ0XAxYL+wyXyI55JYQydJDtInHHRTPSyNCZasHJJwq19OCG4L8JCaJbw6B9l'
        b'QTzQrd1i1/VhPBlax2RBeOwfnEjyIYkkO4Vd/pAQllA5gJ2jKtaNONSLTVlRq6TYYO8N0ze4hGhKAAnJPTDVVEYtPHcA2t6Cedgb4zmhIrSp6RHYkyVQ4xIuzHaJtNq4'
        b'ZRGeDsXFOX4lLtViIHXL4gZfp+cEDdCkU0SUZClSm2yotrIZPQvnaBJP23bi3kTWfSipkrfOp3A+sJY1Famj3RTwA1IJEW4KJmuXMCeqUCTJfRN0himbsqDsj9CRIYgK'
        b'UjBCJpr6iiEX2sHEoGdF3BJQFY+Kks1gpy9EfEV7r8Dpu9QeXKktPCgZ0haOdxq8lQPWliCgym0O3A9CQzJHPr9m4Hf0M+W8MSFhnM+hHg+A4DRaR2d2i0BzkXoQ2WaN'
        b'xrVGEnjRmHUHnTwCEkXlE3yKz5aw85OrSUYsoJw4LsOAeWDabW6vDzU//DRkpsx0Kg7tdPyZwX83/TUb3r/ay1pKxvkJuf09DoiMik7YW2lxRbnk83TUtQ7z0I18PMEi'
        b'IYhg6FvDO3awAG9DdCfC3bwQ4KSwgGY2a3lSxgDs1cMTYQsAA+ChoHjTn2k+wTx42KpY2B08gSHNY0SsXMsOVwW3my2wvPP9bf7AKn/vplo0dERw6DH5shFBPHuV1Wwc'
        b'LNSaiMsMmakT8An6gmL0rNhL66tn8CdARDzd7UcNJvT0DQW8jUOal7SmMo3TijxeFjL5NQWpQ5v8aQqSwsVE4jWFSz7TpCUjGNSLwO5agITqGsk0lQzzOkRB+A0zhZPD'
        b'EuH8csD5knGMBTuCF0raLiDmN4V2sjqPN5aGOhN/CADpEAc4dHSWD6S3NUnaZDPFyWoewq2dCZChL0nw2Lfstwryf9hL/sMYiSjhzaaxOgGLG1WLtQAC9j7Z8pmJhlMX'
        b'qlIJ/lOMu9vLBIyH72/tZQLycjMHA5fuImXqVm2DvrZXLqk/XKNvqK2YPk/gCvtL2mPNes8JftjxHwXsTVAiGcSCmxQIC4pg0h/45njaA5kFg/Ig1RuUULJ5y4zbFgSa'
        b'2ipbfJ7aP7Cq3p2eoEBMe4gEUooSe46rKZgTEpBBXMsb7LNA7+iAMw8FlFIYmEu3hcSUMoksrWgi57YlVKSO9cNwxEVKwGOEM0BC8ph1RHA0qvbhXNGRv9wSxHwEVHFr'
        b'Q2MQlQziNlL/U1rUuBUV4wOdobjF3U4hfSjKcdzqxhxARifpPsQlzKEu4vtiJ3Al/KN3UTmJTMgmUkHm12SZw3SipBNHKBH/FB3nMD1QhDY0/etauTozivAGo4OIeQnn'
        b'X2wY067kATvx3JrJYcRcfJuoTluL3wEokUiQlcO3SepFISuKCtcC1dVqU4xyLkDdQygBze9WZAIzLrGxXgSpJab+vKX2aBYhs6ZAp0+hgW5ookAKRThAf7hlG/7bNb2+'
        b'xA48HgwlDU/c0t4Gg6ueR2drdYuIT49bPKoKSGcxPnSe1+nH7MaboM/j6TDQXdwKewwV1XRSGI5LWLvVYpxxcmRhKpA/Bwe56JFoBtAiek16Yuzxm76tmsoNTKeOVGg9'
        b'Ihdmjrk6ElKSOf4JHrcSiEjsClsalpZgosMWtR3uDYFTH+xtpx8bkm9JEomjmc2ajERDWY6+pV2mXhZSi0qSSNxzcpE4em7yABIrtPRKhjKTViS97NuCpzSpNlyShhRa'
        b'YFJoOkmAgUlYNPPIgzfiqNSbQ6Oe39uwPmx93G7AtShcHWJJaB7YiLKGqctOaqSRLUV1Gf+jG3Myyaf5yzNFgDg4pgpnYqiWMx2c82mWmnwBIPo8fEJuFJfcnq6mPuTD'
        b'gFoAYouTJ8xxPFSzPCj7qOHJ2rqvnYJGBmtUvfjTjD+tpyK7XQCZvjI5VpvkcriynCi/tdJhVY52MIDep+r0TSuNwOXprdpV+iHRcVFLyoZgNa60tSekQahKLgHTmZAI'
        b'ocbmMknJjLDYP2JEjti8Mklp7bAxZDE2laL34JGVHTYJ5oIOD65SGdTsuFS58JzKFHSXOL87h0NZvUEW0CE/soLmlOHKUlBRWkISjdIWRQjJLGVsCqYE8VjawtVY0fii'
        b'lSOCx9IhYYQxh6QpU2QuyNB3akdDsyfuDHpC7g41oHQ2AU3vxK/di+ect6iqrjaehu/Izy6gpzS324j07XYzxXM3hpgxybPe48XvmEGse0LvEs8mNXMA+nSs9kRm8WRi'
        b'ZuMU5VjWImhFUXuDn/yQoqcaxAHB3sXMHEYcTy9irxLtn5xAB8KabGpGyuvaRGOQs7CbGCGaMmdoz42iApMsVC+JSiQXJhV14CxF4EZJ15F0HOi+G7iNsNifQ51pegrb'
        b'fKvMlDqoHF5dGwUiUbH0CJszuyXgda1hgW1aCncudx63lPEmZA3/FLTnMwRLx4gRi+YsnFn0GXaV6TB2Ae/vIGo8LqxqNJZBXIbtvqMzRKMVtyid7R1BEjKRsiOddMYt'
        b'q1AJwRBeMjRG40mfCN7lp25Nra7GYxeLqXhN1tIyuTlAajObNqocfk0ajT9rWNw+z+Nb6Qm1NDWoE7EIsvHESWgyRUsZyTPi4xkbhJaNyPbAVSYtKmSA+B7RgCQaX7oH'
        b'pgfIchHfRPmQBbg/Sw6ZjKBvC5YeyNI2Re62K9ZuB5MRdKd1fQOznUaaq3/pdgJ57xzAdaeH7eozZs5wOswlyh9uUezd6f5CSjsgfVhJg7dm7TasfYWa2pqwMwyEZj7X'
        b'xqnvYNmKsz83gOt4F0pyhV2Bj5T0sKvNei2vTgm7WC1wXxh2wi+WbDWwBpSouMJWLFERu+3QBhdrA30J71FbnNWI71F/RbGGLeH0sAO2ensr/qa1OpWsjTKU51BVzLVC'
        b'BY6YSTCya4+iN6ujOAv1R3G+/xDJe/OlLxd9Mb2SZBvHxKlTp9K0xUU34Ay+3lDpLorzs+LW2YFOtQVQDl+FGs1+zyp3F7usLklnav4O0sT1tfg9QYaK2hvU5hZ/MN4P'
        b'Ew2doQChMHcjYKi2uA0fegN+IGLVQKdfYSciflyrUpPH54tLSxcGgnFpwZzK+rh0Ad3XzllaX5LB1jcd6UtUgETGNZZgaDUQwWnYAPdyT0vzciiatcaBGdw+aI7HuAfG'
        b'FaqwqB5oRVxuZBISu7+z3U1fMI1hCe/hqacrRI+/N+J2GtMDJXXvBRaDgeCMOJ9OOq/JJOsQ5oCAuWx0GP5FyN+IMIhyypSDgZxkgBxqaxHAJVWSIkuRzR1K5VJhC/FX'
        b'oIDO3pGNma8IMQ7tpEIisUm4c9pQ6tJjePAYgNYmvCKH+Tym9yih/jbPhSyGAFROMMMiiUHZrmk/VjCrQUUT6KIJAe8kJognhwzBznb1c1xLZadiHl4xumj4mLIRKURT'
        b'QihMJolo7+Xq5qMGm59i6QU7Ch5fmLZeA/tkfNDMa425k8jcmsE0sNj0CZP6svI6ip4bjkmlI4KlBCu1wCH/mjOEbWhCpJDmeVyEnsZdtLJbgANvCvgCqoG/WeEma/ZK'
        b'6h6c6hb154l23g+tD1lMoRO6aiKrQxT9G9jXKJZo2G6kyhLIV7385DRdJ28gefVO3qgmifv/wX6eeuUAbVDSGEtCDpBptUn5rpxidkZxg7Zb3xlM0+7VrupYIXKCfgs/'
        b'pFSLEn1bW1uLKmgiGQvrN5Ro28gC0VOOVoj6dnxLBrznTBS5ojNxOC51np5bCrVXttwx+G4huAkItKsy1Zr6lmC/uZlv/+ZPS6u2fvK13PPoU6MOPbxxbHbemWc+Z91X'
        b'ljPJvbVo1nPvZV7/wKdz7v/Ta9Zvm9/ZcN/1r27dvvKI+3dT09yfnGMfHtqavzx286v9Gue3PX1ga2zAxUOvOTL7hdYbb35lUuMln2SffWBe+R8dDy/6MnbxsWvfePCz'
        b'pwvfHvG3P3U33u7v9/UXWybe8Uis58jMQS/f93TD20M3/XHZlq4JL2/fcsHqpz4rfmZZw2U331e1/Zlxv3YMvOSjhuxFFXuPnhV+ou7967vrni5crY8vtBzesG3xG5//'
        b'tqky76vDa3f/bcqept+/8PzW+ruGe1e8eP2K+V8/f2T+V0Mq9r5/zXVnrH0j0v+vQ0a2/HrE1H3Dy867u73q5/vGnL/r+ar6n9a81eo5ek8k74r5oy7Y/FxJdcX898/8'
        b'eOnFzR/9bFrnM8+KbdMXZLyvFnzQ0f/LBefs+zS37uXx+oKtSo3sWeC6YFVe8ObAj25+fZv3V7UX1i6/4MJzHWlL7/afO+bc/n+a+fbur5e+/NC2v0x9/tpF14/aN+yX'
        b'vy/6+aUDvnzzxUu6/vzUxF/9ZPGfF72/94HfPGJf2fXBlJ+6D/zi5U/vLZ+39/P9/5EdLHnll4XBwsd2/njblw25bfdOXlk2wJrb75Pxf/70o9eO+H5evO3ZBz7hX9v2'
        b'3poJTzn2XxNJ9x2a4ts+4hbeM2CKL3jvyvGWo1tXv/7+EO/jz0764Nynh72+49xnP7x0g//Z+I1T/7Y8bfOYiRu3/Pngtjeu//H5Gw/etHDltCMPXD7jhXemPXXohpUX'
        b'tlSNLH7w3V03uFZMeGFx7lHPTY/e/XDPxY8NbvnFk0+9veaaqc8WPrTvwpWPCR+9/+gNdUu/6lTdd/xJsZQ99p+HrRNDn7qGPZu16cXaCbXPfLruQHfslt1jD/z4iecW'
        b'1HW07n/+08Jv2s+6bGbet2//un318/+84qol3vkbb/1i0KL9Y+Zu+KrAfeToBxc/e+j3kz5wv9d2U/XtB5f/qvHqh5946pH+3/xt3kfBuN2ufPXkbzN/9HfXu3fv+MUX'
        b'P609890Ls383bPKXv100+fy6v976Ghd46ejPzhp339LXM7raAg3ami9q/vbCnZtWff7FS/6Nn5w+adfCz4a9s+izS8q+2CC/OPyLSbt/+evX6/4+423rM/YaeeOmbz1j'
        b'H3zli/q3fv25z7fozekvPLk5t/7wrkXjX6z4asCTh7fn/MfaS57aO3Bry+6aeHfpj/8x6rOzbh338rZ3djfXDPdeF1oQ/O2mbX/45O/znpm7iP9H5+T2dWdPG7X7gU/H'
        b'nf3IsK/fenv6X2Iv1B1Z9stJ7m/++afh345677TVb77W/JvLDjz0E3dJGvlTHzJIvxedr1ZpG8bMK9djHJd9ca52jagd0O9PZxEAbtafAORw9VTy4FtbUYqxtA4K2lbt'
        b'Ue0A5bhCu3t1avxvLuuKMRT9u62EQvjoN+lPZmk3ahv61O68yUEBPrS1+n0z2CmpHW2gMfbsmsHak6I7oy6E3q20dfqRi6AFZKlpFKPF9MNz6+gMXdvEHGWxU/TwZId0'
        b'vr4xhC7A9a3aQf2epLqraqrL9Y0lx529a7fqa+HLK6odnF/fF8JdRd9XC918Qrvp+5QkPKNCqC6p7dXv0G8PjqZYkZs7zVyco49z/lX6LXbtkHZIX8cClGzVnzj3BEGs'
        b'dru2yxDFXjiQYjTqd82aEEyraE8g6StcQHX9kD3he3aMif+Fhf1/9VMyhG3d/+4/ppDJF2hQjKiYyAJwDTL5Gzj1P4fosrskJ/zlODJtef1ycgR+7EKBL8gT+OHlw88e'
        b'NNBlyZ8hCQKfz5/pK17p5G02TI3MEvih8L+wSOBzZPhvK3AIfLYk8Hly79Vlx3tMDR2EotY8J/zPwLuczELeEUD9eJeQaSkYmsM7B2XyDquTd4r4vtBlg+sg3nkh/J4h'
        b'8EW8s1bdnZB6JXub+d/FfLKfXnobR+5SzqRj71yT7JkCWZYZF2s/QgUVRK91C7SYttmqP6jfw7kGiKddrN/ZsiP3SktwKKyz8OhnKq5/1D9wXOY1z0+9+zfdv4t4qg51'
        b'vrEv/OBtu5+bcLgmN9Oxb9mZm6qfn6O8+4fQ6i05q7dMWegd0MRfPrj5uTeHPLV31vPR6Y6anb+f+fKIVxq23jx6wi8/v3n2vb/03dIx7OZVI7/Z/pBXC9hHPf/P4jcv'
        b'eFpcZztrz/xdn7fNmJS78FLhxq/K6w+NfCMycuJzj499qtb39uAnK342cKr38PvrvIdfHD7uxmq1tHntg19+PveDkq6s0r3nfPRy/IFhdR+cPSv30Euv/K7ZnZvx6X0H'
        b'Jl3x5quX3PJWbWXLx8u9G7+t8niveenPU37xGT9hbnrhZyGt6aqP2zd9uPC1ZbEHmx98YeUzB6tXzFlSNb/hrjM2bXrgN2/+52sFvuq2mkMPH8y7/Y1zPR8fvu2t5lff'
        b'vHfn40HX2ovev3/+3Gubv/74ZW3f3LNeaH3rdfH+D4fkfp51289///uDXXfPrf/Ns/W/bjpy47eBplmvb13UesH2Xz38QcnFS7ef+7pa2e2duv1Dyz0fvSN/ff03j0z+'
        b'w2U3fd15V9rHU9rbf7b1vYsmPPFqW/axdYMeO5Tr/nDg5JcfOfDyqlff+3rpnB2tgbfdL73Sf8Ryz4dvf/L4bf2nDro654VVI1dXL5qw8Z3dL30WEZc0frvzyKC68Gnd'
        b'd5bZ5k3seO+v1Z9eN6uAH//c0MgUR/GODY77d+7YJN+yfMdG15E/7tjMXzNRsz2b37S2pLZj3YQXxj4rVN/6vlB2UePGsovelx85PDv69Ys9f9r1z7aHvlx1+ct/WL/3'
        b'6bue8/2TP/LzN8ovLyqZxuiByGqMKkRLaoO+vpytqZvaOdd54rgVsPdiphG10/SIdgtmMzd4yMVlaT8RtRsatAeZ76qd+k79RhaPU98gwv67nwXkzFxC/sHrtZuUMm1P'
        b'ud4zSobt8ir+0rMuoe32TP3AmrLqii5tXSm6Z9I3U3C+DdX6eis3ZJElW183JTQE8i3Rei5AX+WVrj68le8dqcWoGRdoN1xaDbn0DSWYq0zmtQiXcZbYVlxKDn7C5+v3'
        b'6evHzNM3isWTOGker+0fo20lJztztVuvqNY3FZdoDwic4Oen6T3aPSyyyO4x+toydH2u3XlxnYWTZwguST9IBRZcrj1IBFlxQWsFz8ldwrggFIh01AT9Ef3eanxZUgU0'
        b'lE3fre/SnhS0SLd+D41JcY12NdB85drD2rXAt4b56cMXUaEXT9b3ABe4rrxMewBeaPv5ev2RWnI0VKLdqe+tJldWd2jbTHdWNaPp5SrtDj3K3P5dq++AL7v5Sn2L9jjr'
        b'xbpV2g59fd1obUcVD4Wu4+fqV2q3MprnvqwLocIo0GKl8/StMAxIXyFRNeJ0i37PsnMWh8lfvL5Nu6o2DWjP6gpHsb5Oe1Dbre3FAKoF2uOSdksVzAIiqnztbu0h6Pjj'
        b'ueU4p2XoE6waqMz+y6Xx+dpOaqt+H9ChB2Eu5mvbtK3YoJuhsRucNBdaVEor06Nj9OvGYjDrnfySNu1+Fhdyl34v0MTrgTrTHpsKlNcV/Ix6/QZGIe/Tb9L2VRN6hNkq'
        b'kbk07SrLAEG/Z4X2ME1Jf23H3DO1K7X1dXUVVTijNRYu+2wRerGlntaPY1ZWNQtrW1eLJWjXTeBcl4vnnKdFmSemW7TdK/T1q/VHx8gcvwiIwIu0CBvevfquJYbjthEX'
        b'sli12t2zGXD0aNu1/fp6bRcOMa9dfz4nNfJAzm6ZTfNdNkq/p7qiZH6+vg0aJC8S8oDE3kOf2rU92lVsRVfhKkrTbvaeIQCsHfDRjGiPa/fUaPfpV8LM9qq2Sly21iPC'
        b'9N5urMVhbn1PdVV5VQVrYJ0W5Vz6OrFWv1/fS03QnpgwDjNYtB/puzlJ4uHTB9pZSNud2h5XmnY961wNjHxJFVSg3yBqR/Q7JrJwUFfqe7VDZVXag8UlY+aXc4VLuAz9'
        b'LhGG+iHtSqpgCJDYh6vL5lWJp+v3clIBr+3Q7mhmHk5/cp52rb4e4X8zNvpJTjqXB7z0QAONeYv+E/3xsmJ9z3wLx1dz+s36tdomFhbox/rVwCysn4fLDB1dwviEAS72'
        b'Cfqtdv12FpB0w8wZsBQpCPAe7R5OyuQBlz1wMVtN945bVg0M0BkTeM6qbZD06wW5RLuBhmy8tq3Fq0dSnVcOEc+Gpl5Fjrsy9NuA+bpRuybFeSS6jtQ26DvYsNx4WWk1'
        b'eTc2nM/psdWcS7tDnF2uPUQ5Vuk7tSeOcymq/2jOKkE/MiWDEJ9+XbEe0e+dfKJHT3Lnec2w0BjI1TROv2GVvg2xTQUATinMFUDw9YBeFtDYbKiu0O6XuBptt1W/anIb'
        b'w/47oPJ1aTXaIeQ4O/DbalxjOfqton7v6aeH0Fuw9uMmPZqmbxpTMb+2k44g9YNIflTVLYOsZ1woV83UdzO+8V79fh/hwtHzakbz0I87h2qHMUjErqEswx57Pbq6pU0E'
        b'gXM/AMZBQd+v789i4aK36tdOHTujTN+0QN9cXV5SATPer1DUb9B7gjQWrrCtGiEXxv0uGI5YVfn8MVCZzJVzFn3b2dp2ggmLtisDgPgOwKu4sW2sK0FN7424aeWNkMSQ'
        b'fhPVlrMSWW7oSx1tOFZo0D6tJxeASxhJ5ZSdrz0BqwNasxKXZrV+N6DV9Qus3AB9v3QB7Ilb2CQfmaT3VF8MDdMfxtIwMlCWDpvjDv26hSwKxzr9ngYaXtjVYJeEBV7B'
        b'w0zuslE9mdrGetxdx1RXGHtg1zxMW7mBwyWtR99YxDAMBrDaVl1VU6o9DuvZysmSYFsykjmR2wc4YBd5zMXOVsDo6vdoB3lYRop+wym46TU4zv95punf8ydx0Etc3B3w'
        b'w6UJgo0//s8BfBJTUEFfdxKPeVzsjXGEYXB0TH9PcBh38J2A0ads5LwpJ6VMJ5VHeeCNk+yWbXTG6BRkcc0V3Il/QPcwETbTPkBdjKAn1NnhdveyZOY5wAN8cv/whvEf'
        b'Xyb7+6R3CX2DdA7dW7LT/uDT8NuIHmrgL7Y4uhhPT2Kj4CrAVYCrCNe86GIvB9fzo4tb8OqILkY7vthgzI8nyjE+wkcWewVmP9bNoUaCT2yXYhntlm6+Xe4W2q3deKon'
        b'Kzafrd3eLdG93edoT+u20L3D52xP75bpPs3nas/otuKZYSgTSs+FaxZc+8E1G66FcO0HV7QvluE6JMxFM+CaEaazklhamIw4YpmQLweu2XDNhasLrnlwHREmNciYNSzF'
        b'hipyrL8ixvIVZ2yAkh4bqLhig5SM2GlKZrdNyeq2K9mxgrCocNEBqK0dG6b0i5UoObHRSm6sTsmL1Sj9YwuV/NhcZUCsSimIlSoDY+XKoFiZclqsWCmMVSqDY+OVothk'
        b'ZUhsmjI0Nl0ZFpuoDI+droyInaGMjE1VRsVmKMWxM5WS2BSlNHaWUhY7WymPTVIqYhOU0bFxyphYtTI2NkYZF5uvjI8tUibE5imnx+YoZ8RmKmfGKpSzYucqE2PnKZNi'
        b'tVFHDxcbrkyOzQr1h7ss5ezYAmVKbLYyNVavTIuNVfjYOWErvCmKCmFb2O7FUcqJuCL9I4MjNV5Jma7MgPlzhB0xJ2mY9Lp3dUUyIjmRPMiZHxkQKYgMjBTCN0MioyKj'
        b'I2MiYyMzI3MilZF5kfmR6siiSH3kfFgPQ5SZifJsUVfUFi3pEWL2CAsaz8p1UsmZkaxIdiTXKP00KHtoZERkZKQkUhopj4yPTIicHjkjcmbkrMjEyKTI5MjZkSmRqZFp'
        b'kemRGZFZkXOg5qrIgkgd1DlamZWo0wJ1WqhOGepjNWH5IyNl8MXcSJU3TZmdyJ0eEckvfjrky470M1pTFBkOLRkFLZkNNdRGFnr7KeeY33SnRV3hNKphJH2bBrWk03jm'
        b'wwgNgq+H0ffF8H1ZpCIyDtpbSeWcGznPO0CZk6hdhLaKVJJ0uQPnsdsZHRF1RkujzrAzWtUjkFYAPimnJ+XsyeXOcBqdTFYyB/zkPYMOtfvWG0PKgRk7Rbk2u1oQQice'
        b'XCtvKlsb3qCP5Y4IFpcUtTAVzoaixs4WX6jFXyKobkQ4w5K2nZM5nHJ7/SQ7Q+WwLZaESw487lX3mOYjJRJgt2ZPyKuiwYLN09VEKi5kLI6H2AFv3Gmq+JBqD4/uRNoB'
        b'HcKdA51Rt3eonmAQUqIv0Iwmxaj7pT6GDcED1aOko4HtOtqFPxiw8CgOCWkvBxQPIFXy5oA633GxI9ARd0DpisfbgIYENq+bnZQyPz693h4SiDgue6mceFpTwN2gNlN4'
        b'UIxr6m5bFfD7ViceOeCRnxUWd8J9MNRguMy0Qcrra2gOxq1wR4XZ6cYfDAXpLWmqUw0rG9TeBGrEYoq+oxsXPVWDpKLgD1A5PpjChkb2gerxrESf45hADQRKWJp8ngY1'
        b'LlN4k3FxsbGlmbS80bMMC0YRd2AUaXbPVHIOGJMcUhuaPBho0u2G7I1uNpFWuEOVgrjkVj3euMuttAQbGn0ed1ND03KmxAsLQ2Guz5AXOCYUl6SEA8S5Q7KJAnKgnZ7p'
        b'RR5dM0WZw7Y8cvXoIqeR5Iiom18xaInpJ4uv7Vt773vdLeHi/DihEUYkgMNctIk2ouqXbLbxGXgTtQJ6cwJYDcB2hHlAPIIX7RoKFQosQ9YOYrSIVLKksBR1tNnUtVFn'
        b'tyUsRNPaBHUe3Mv+Ykpx6iVRZxrXbYkya0Qh6ohmwxsX9N3ZH8dCjlohfVqPEJajueij1L8HHb8Et8DTwmieF93S3IzKWFBTP6jpIcqfD98PwvL8V8LzwdEsyvdRNAvQ'
        b'jbWriCzD8rttkNcazYG8EmwSomFw9ByMrISOaahMuc12La+Ojcrwpb1rNJU+EHKajmwcUIrxddgOdw68o4A8aMBiX8SxkYjyVE4Uvs6IpqcZNmphMZpJb9Pz0dtuWhid'
        b'Y6Thu7AA6Da9P8dMp8hhqJ356k8ou9HIQpk7YUYc0QKoX8ARClty0GYkn40HvP8ptbm/OSJh01kdWzXO/8sjjv95yfQPEl7j2v47rvlaQtIuRqgSqYpaObJgI32dbPwT'
        b'JdKRdBIhnE/ErMzn8QW8JLoEF5C5g/A70QHPAG6EBMhkGXsQgcyrggEyLpjmEgNkcpJBBt6KOHFRCfapsSlAhBNXBt9IdIfL3xKWgh9FMSqVHMW/vB6yl+qGhayuDVvJ'
        b'/MUWhtrYwgGgKZjC+ZdHB0aHRUcCIAzwWmAZPxe2w/Jd2O2IotaZA8pNCzuiAwE434Bll5HGDcBdWYR7F96HnQR+UFI4DejDDGP5pmEO9i7smMKt2LqE8/ujw6Pp0YFe'
        b'LjoM/o+E/4OjxV4+moU1RQcjiOUAhQnPC6J8NDOaiZRZi5XA3IKLGMApK2yDHqXDgodrGEAj6srnul3RbKAH8ImrPwdgk050Qhp8VU7xsrqoBLj3Qq838d0W/0fwRI6W'
        b'QpkZ4YxoPr0HxADtzYgWUarISA2n1HAjNYJSI4xUIaUKjVSB2U5KDaTUQCM1jFLDjNRISo00UoMoNchIDaXUUCN1GqVOM1JDKDXESA1OjBumBlBqAKa8GbBNVCB1H+Y2'
        b'IQJFJAB9jY6KpkOPM8OZ1woda8MS/VqvFYL303rpj+sFyoCx96KzbqM3/Tkv+beL9sN1BqWK5GFBwpEnn2D4vCwskY6klOIOIuv/CciWjP43QBv//ahpHGy1wbW9qAlV'
        b'BgWb4YhaFl0sYJkk8OxPpvAwaBOcAzlzZDNuNDqwzpTQUhh9ZzmFbNEBCMvFn+wvW3CKmYDwMLp0gegUkZdPoDPTlSyhM+Y4EhCWBIvHZqAzOcoloTMxaqGdHCiVqB0I'
        b'fEBjTPk6Zdn0SZz8F4QAoGG8XTZt69kwijgQKR1KMzt0P3ZIAnhAkkMADJzNOsH0LdEzN2qCRzN7BLWc3khhygsdTI9i2A+EogzASOlRK0uhTnnUsXkkj+WmRbMR4nCo'
        b'CFuJFsCnUftZQPtNSdImB8wGONLQiMb7zKiNaUeHyXU+QqNh3/Jdw9fvv3e17pGTzJ8kgazRrQ5+kIh3bB05etcRFpBtDjvqBgPliOIMWCmJYZfYsAdG0qDnAtUlBtmw'
        b'YzoP00jBkEt0oBBhzc2nt47NBTRwaGZuzSelfkylDDHQbFErbFtAk8J2sTwsBjeY9DSP5UtAHcL22VUZtqhvYfBFRJawMVlgE4FJ7LaudoRJwRu2uRyJC3FtDvUl5m6G'
        b'BZGkb/KxjBU3L+GIyXYBw98vkhPp77UaEWNsvTUB1WghlfBB0XR8Zn7PNjYgGewAVdTWrilhC1y9iRrsKNSgb5fCt/AM3tgT3ybaAVRo+ZKkSDTJNjApPm0T8QqR8YAu'
        b'wzBTBAZ0wIBBbtD7Y6AcSU+yob+619GUGBdCjepPkVV8nv/BnjDirpagO9Doda9SURNaPSYnDFQkUpZ2MHYEeHDkx/+lMBsD/p0Q/EuyYXWUBDIC0wxHDfFsQOWyJJEp'
        b'PirUoC0h8mSy3SXmW/FpttVliGmz+ZJ8JmAglV20HYmLwdVBdS8+ewh/HsaffeRVoAn93wTV/aSTv8bX0qgeoNv2htBy9SAZMMONpwEDIqiHyMqkRVELqVBgvuNiQyOw'
        b'7csbgmjmHLcaHpzi1qB50+wLNALLX5L+XzNkJUv+DeTp//vzrxxA4Jr8kcXwNMsJgnT84YPLkk/HBXg0cOLhBPuT+vhz9vn0X/+Tjf+JtOwUs62SuOAMgEDR24q/RU5J'
        b'HDsI76bMRrgUbDJxh4JA/aytLxFVPG1REaeSJK4kQ72Lo3gI7mSJntttgGh7QwfAaUhVVZ6ZxpJ9PzsI2UOAOKerydOB7o5UPLjDY5Gmhs6gx+2O57jdwc4OkgSi2AzN'
        b'RuBpmrs3of4m1U1Dkh3plPaA0unzTKPzEFQ/lQQgEwWgjvo6nLmCsxjPhwrkktZU8/s/0Rl+9w=='
    ))))
