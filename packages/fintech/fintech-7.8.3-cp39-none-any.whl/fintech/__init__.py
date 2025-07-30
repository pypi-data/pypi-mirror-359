
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
        b'eJzcfXlck0f+//M8eXJAwiFyCF7RihJIAEHxvsUCgYCC90ECCRiBADlQaFAUMdzifSt4I14I3lp1pueu3ba2u9vSy9rTttvd7na7XXe3/c3Mk4Rwqe3u958fefHkyfPM'
        b'9cx8Pu/PMZ+Z5xOq2587+p+O/k0b0EFLLaG09BJayzQyOp6O1dHlTBO9hJ9NLRFoeVp2I6URavlaAfoWlXiahWZROVVO09RCyjCdpXRuxSU0tcSdpkpCtEKde7pYK0JH'
        b'CTn3IEdPnfsGeiG1mNIKl7gvdTe4c9+RVCS6kkq5rZS5PRrknrZSJ00pNq/MN0jn6A1mXeZKaYEmM0eTrXOX8R4KUUMfivCBhw4ddHgm7fI8+JrQ/m0ajw42KovWoifa'
        b'KCqlK6lyqpQp8bHS5ajNVqacoqm19Fom1eUctYQiLeGpMl07SoD+cXn9ccEs6axUSiZVdVB/w7fTcnGTXhzKprQz3qhL1blH02KpL7i8f5nWTPXaSlLYZNxKxkbZeFk8'
        b'Z0vpX99SRwVdW8qqLBHonB04HOwDx1MVcCdsSIOV8gWwEtZEzI1LiwuFdbBWBqtgLY+aPV8Az4FNK/VVZ0/wTWEoY3bSga/VX6lzs75RhyTN0Mm3hmriNN+o72b4Zq7M'
        b'ymUubAgc/xa1YbVwoVeajDEPQzng1YUJYlRoGC4yyaJIB1tCYXUEQw0FbSw8pxxjluJUFy1wK6gBm+HmEfCmEqUEdWCzkPL04Q0Bp6HN6IYSyXgdTIjMiImVO+CLj7wn'
        b'ZxnzS3QGaRZHJVM7PDUmk85oTs+w6HPNegODewAPHBUooT1po8SRtZnXwWZZDJkdwvR0o8WQnt4hTk/PzNVpDJaC9HQZz6UmfGimjZ74XIwPuJAgXPAgXPCX3oyAZmgB'
        b'OTL/Zhg0ODT1E/5lGYHur4K1sM4ITyrl4SpFKKhKdu1leTQfNruNysVNyo9/hb7Lp8bfn14q31d0hv6aIhQ1KNDCmEU/Dhar12d8yH95rp2i7k8jd4tTVln09Ek+JVU/'
        b'tzBiLZflex6PfYGHz9SS2dEW7uJCX0GImBpAoZSJF9UTKAseU4s+QgxOylFjKuHm1Mh5HCmEhCtCYGVE6KQx8Uk0tWypKBFeWCajLUNQjvBxc8XoOZQK9xArDavBOXCS'
        b'pYLATRbsXQWrSZJSuPMZPJ4R+ElvgjP4XEiJkxm4Fe4psBDKqINnwUVu0PGITwdlnYOOGlEt41l8cbpmeMJbqZBNTUxI4lOCVMZ/eoAF970VVsNdStKV8VPHxysYSgx2'
        b'M/Ckm5KUD3bBY+CKHmyBNcmwOiEpHFYlghaW8gHlPFhWDHei8gfi8nfAQxHKeHm8AlbljUYN4VOesJqnWgYPWPxJOSNBnRbsx0n4FMvS4FA/eM4yFN2KAzfHgRp4kCPu'
        b'pHhYJ4tHFcBtPHAN7I5A3TUYpUqGx2FVNDisjIpGKZSwPhmV4zWMNwlUgTqUhjTixEx3eEyCk8QncSk84Vne6AmgRcZwj7M9FVSL49A4gY3wUAGsgbVK/My+cD8PHs8F'
        b'VYTSaHAZ7BDD+ghFgsqC08TDi7AqOXFMJk47dqkgPjgFPTem2nS4zQBr5CpYHw92wwZ5uAD1XxsD24rAeZIgZ/QQsBceDYP1iWiE5DJFAp/qP4QHty0HJy3DUYLJuVJ4'
        b'AV5TJiviw9AoVMXLEyLC45IElJziwz3ABq+RcYJXY5S4KWHhcTGhSeE0JYaHGXjZAI5aQtHtOeASrOAS4EdPCVEqQg35sB7xzObUFIWAmsUKYBm4AtrIE04Gh1FdNfih'
        b'5oaAnRPiEmG9KjF5Pk4pn8iPhcfg+S5IyLhi9nEiDGw0glqejbXxbQKb0CayudncbWKbxOZh87R52bxt/Ww+tv42X5ufzd8WYBtgC7QF2QbaBtkG24bYhtqktmG24bZn'
        b'bCNswbaRtlG2EJvMFmoLs8ltClu4LcIWaRtti7JF28bYxtpibOOyxtsBnarkI0CnEaBTBNBpAuIIxlNdzu2AntUd0L3siNMV0MtVlmdwFx8KXdU7uOTDzRhfpnlYCM62'
        b'ixHwY75UKWQK1KvXQCVmOR81D5yFGwUWP5xo04AkWAPOuiFq5VHMOno6LJ9iCUB3BhaAtjDQLI9DfCCiwUYalsMr8Aa5B88VKcNQmZWIdAVxsB6cYsJyEFViFhar0/GI'
        b'ydHYs26x8TS4OSabZALPw9bJSsSY+A5shbVuNDgm9LME4nuXloGtCIricCtY2KaNo0EbbAaHLT64ujZeUFiSW7iMoRhwiV4yyp1rxVkG7leCU4ibBZRg1tJcJgTuBeu5'
        b'Arei0/NKhBoIcVB9oCzwGRqcGZ9K2By2LwLn0WMfyUaESKNC6+nEsGmkQzTPCZWE4uQ0JQCV82OYgNHRXHUtsD0sLAGxYjJ6agrWTGc84flgC4JYajW8RROqDlHgbNdA'
        b'3RpmNLywkKttD7wCNirBzVRYH4IewUBPBe3jue5vKNKhguQRCbgVu+k5sBIc4ECibTTcpoQXRbhYGWZoEbjFANsEWGPBZAHXh66GNcFgd5Ickb2VnhZdSiqLRLh6CrTk'
        b'wSOwGt8BbXTa0kWEN5eBNtCmxCAAa1nUym3gUBDjDk/A7WTg6Fx4DVXWmBMHzqCMpfQcb66fp02BB/ANeDw5HDezmn4W8eUxgv3w6lAET3JcZFh4POobFZ8KgAdB00o2'
        b'SjGQDMVYlUy5FpwKw8IjAY+vm4ABO0CLeybjQvKYyrsqSEg9stFOBYmpRGpQKQ/xE0P4iUd4iFnLS3U574uf8F9PBYmn0i/Tp/FNU9GFf7iv/lr9m4wv1ZXZX6p/056e'
        b'wd6rnb7XLS6a1mdJPV5YLBcvWj95Z0VtrWTw9H9mNUy85LlJLfidP/U233PfpM9kQjOGK9QLm2ADJ+VgXbIM1sVzUg7UTvMPZnmI/w6ah5JhB5dAdac4DBR3SsN8uN48'
        b'ElPwEbieJewrT0LwWNWpKA0FW8SwkYVbRoIjpDgLqIfrcdJkRLegHmzu7y2k3GEDGnywG1wxY8EkTQBN9iSJ4fDmSCSPcIU83rBcUGbG47QCSYbrYYq4eLgZnMfiTwTb'
        b'GbBxxWozxv8pw+Ep0hqnhJgxP4FrT3AoPzkJnrbrbd00KXKV6FEdbJ7GlEM0NKxbUWtFNPfxpN1pY39HWhnbwdOazB08kzHTiIHQ6I2vMp1FonNMr0Y/R8kk8zrKoaGV'
        b'P0ZDI0B0Gm4MgjVJiGoFFFtsliNgAM2WvvX1iRw5MlnMr9DWs3sjRrY3Ykw48z5rwn29zW/g1+plt9+40/DiO3caXmpv2CKd3+8Vz6z7uTQ1fT5/wMbJSOHGHI20g4NY'
        b'0wyJw7rGTh6NQKKFKQa2QqJpzwQn0cdJZf2AzUXpugqPcP3N9D5YFrM+t1OdXkeJvGmjP9WpTvPyM1b1Pj5IeR7gHBqcpRIXg9GCKqMeefY9OJgKRXAf2BSmwBINwXYg'
        b'vGWkwS1EmZe6DA9t/091NNDKdTWt4h4h0PkwnU/kachPz8/IspgyNWZ9vqEWZyUIxFhG4b6sGRuLUI70VnJCmEKlwmoy0kt4VBhcDy+CNj7cu3rJf90MN0cbdA0uLcAs'
        b'Cupn5SH9ldSNdOJWzIM+sJwHbvYDe/qmTgxfSMnBFiUvi/1f2JM01Rtc8rsmcgD2UGcbCGDbWGcbfglk9+AS3Ab33riE+k8Ka0pEF1rDjS0+X6q/Ub+i/VK9BLzz8oDf'
        b'ed+9DVJAysPbr6T8Fv0Hv3lnGXzj7qLfpsA32O11r/4DqRXVfxz9aeGMlTxpIv3Vx3eRRjrEa8RHPBlNDFhwBbbDZhM4E6dCFlEVeH4FRwD9YAMPnAc3R8toDoHY7ijX'
        b'jXv46ZmaXI59JBz7+DO0N0I6EV0SZFqpzzKn64zGfGP45Nx8lNI0NZxkcAAgqzFmmzoEOavxtwuT9TBTGSMmHOMQJ7thANzpwm7f+PTNblhRDkXmD1L6YWViGNImFdhc'
        b'R8Z5G6L8qmQVUjyQvr4NCbMdoEY4bwIFqqe5wctwE9ijb/7+AmWSoRKqdhTlZK/Mzs1WZao0iZpV8NWPT+q+VJ/SfKnOzXLPup8opHTnBWcnz+Me7ik7UOzSSa4o5Oct'
        b'MEqdST166xRjP2dv4JTbXXrj28f0Bh7/sFl0l87YmUncFwPBNRYBaQvY3DcX9vA8PT3/9aquMD1on1Wl6T9pO8Y3YVXD0iRRarC2Eqdht9bKpDH9d2u/VUePEJEOz35H'
        b'sM7wg4zlvDKXwUlIxECySq4YPEDFCYF+oJ2HdIV2eNAcjkm/DWyHu4mED1eEhCQowpFSsVWSjLpjc1g8OBPCKQyL0kVZz8ETnLpzYRRSY4hO0TVRENyxEpxgwYYVZqI7'
        b'gFPjh8inkLJlCYmqpARkxmE1RUiNeIY/GJaDOlfacKECD4shc6VGb9Bp03VrMl3ZaaiA5j7GYY4sMiSTUKpOdmm20xptHO6kCJz6oAtFfCp5vDcnGu6EFcjgVRYHw/o4'
        b'hAa1yiREGwghBFRwCT8Z3b7VZewcRIEVDQcsEvvzfwPNLNWb8iBS5eJ+ObdAJNLOoaS6da8Vy5VXl63IjpnSHshQxEQRge0zwhTxcBu4iBTV1chqP0yDiyVC4ovaW/o3'
        b'ze4hIUOZlPv0TwOWI+2B+JDuxdAMlfuZmCrQrLuZNIa7+IGoPzVC+h06Uw+6OmQUpU84GsmaDOj3p2cnKDVazUndSd036gJNpeKk7isEBF+pDVmh85o1S243gPaGfqEv'
        b'iXzFpzTMqa3NurOa0xp/4VfMPclw9cSKd+m4gCC/v74d6fcd9eKeeYu0NwYNON9M/+Z8R/TbUX4C+vdRguiC48hMXTH41e8mI8zG8hW2UbBciczgzSvt7hYRaGDyn4vq'
        b'HWOeiDzsSo1pJSE1KUdqo7CO6k4+nL4qYVhawp3RxhGd5MdhcSda914/zSUj1IgzH3ehxvcfg094DDWwCVm0NXFIc0VkMMjqhyxo0AiPPMHVTHdzNTO/nv5wx7j1oD+J'
        b'yoJBd5Iv3A23ofojKBWoiFiuI/SybDbf/QBNXOSJZ6KmcUS0LIbxLeZclrm+qumUEeN7b4cOOl2fcncda6pGP579Y4zi7mhPEOk9+809Fw+84Pv2p8zb+zeIj05PGxO2'
        b'ccNsWl+5v/qlB74/JLXGtr8YVvT9F3nbX+k3xX//X95ZnLj/09A/T5n7Z8mLZTxmTltk5GJx67EE/7FThn/7efHpn+cVNM9tCVe2Ls5beH3Vpy/u+ODWvVOvW0uVF5VT'
        b'I7ftjqHXbxkK7w28nz9twplnfKaekok5bG2IAjtCZvZi8mF7rwgcIPg3bSY4JICHTXKZDFYnhiriLQrOLx66lA9uwQ2g0oxNfuUkMWxTgTNmRWgCOEMSeMAy3hh4JsOM'
        b'CUSlWtypzMM2hOud2vz1ZWasaXsmTQoLR7pjlRwNIzwoAPWMYtRoczAG4TpTWF/mJGhPRuZkMDhPOEoFW6NzfcMSsH8nEdnzYtDKwAMZ8JIZaxewfAZombYYWfvyUFk4'
        b'3Iy0ZIoaIGVXgHMzSZ+sABfAPrALbuFEA6qLkwrEIL2UBm6aMSkHDPYjdst+sA2hq91wGQ+PkJtgP3806s/mMJUiHnUaQ0lEPBE8N7mLFfgYS1NQYMnI1XMCQ85x8UQG'
        b'aV/eiGcFtC/NoiP7M8uwP7E89j8sy/5bwBcg/pZgjh7pLCug12oCneyLU151Yd9XH2N44lw5CHxtYc9OCklCXFyVKEDGznkGlOVPJdVlClz4DLu9RA4+C+Fhy8JKB1Kl'
        b'gkqhVVBJlTOlQqvQlFjiaeU1UlZBE10qWkgZfFjKTBfH0KTexZTBPxJp2lYRzmcV4BImU1oa5zT+ZOUXLNBTpXwrv5FpomZTy3cvY0rdSt1x+Va3csaoJjWx6OykVdDI'
        b'ayJlNLIk7YBScSUPpRNbmSyenrK6H6XraZoqrDXMJrkkqH2SSjeroJxGLXavFOGzcprkFJGcom45X7JKjN9USrgcjrai648K1Q2MYQQpVVzONKDhqaQrqSIKn6H28LVM'
        b'E82lbqAN/ybpaLMgiyFpUyrF9rQplQwu25nyHkkpIKmKKvn2VOisS6rTWl6jUMtq+RuRDTubKqdRP3toBY1Cq0ejSCvUipoYfMXqgfKe0rpZPfypUg+b0CZGmiBP647y'
        b'iaw8nK/UE/WBZzmtFeXgGt+xemrFaFQ8DcOd11l0/QetBNdo9Wyi/fFdVutR6mllGhjjdNRemrSXMQ7RelpRjgAE11kMSudlkFppK5PDQ/ditF743H5dpPW2cmfDXfIv'
        b'0fbj8jvT4Nq8rF5an3H42wOlqbR6kqOXtr/V0+qBy8P3DJ5WL3ynYKvVA/82c2PsjZ7CGz2FL3oKxvi91Rs/ndYP9SljfIH7hfJ8iM5Ezuvvc7/wdfSU/bT+6DelDahg'
        b'AilrP9J+b1T7gEoPXMMqd6u3ow1WXgPPGGSmrV7l9AbaIDKLuTO7wApUpT0S5iIT36AY/YiRS7vIRsYuH4nBjp1I2YixlruX0lZ6FbWFKWRRERvtymiHKD3doMnTpafL'
        b'mA4mPLKDNne35d0n5+pN5sz8vIKpP+KLWOyWDMpcqcvMQZZbp3HXmewRT5pvfETLH+JWPXLPz5Kaiwt00mBTj2byHdwvdTTTH89nW7H4ZkxsJWpyOW1vclZnwxBEhhKx'
        b'WfQYgDRiUPy3o8UPcZWPvDTSIk2uRSdFbQoJNsmI9H00wKQrtOgMmTqp3qzLkwbr8e1RwaZRj/qRC/jUeYklx/4uKR25H7lJ8ywmszRDJ33kpdObV+qM6JlRV6DjQ85/'
        b'9Ige9Yge/sgt2LQ0PDx8ObqOVdpH/eTS7Hyzo5cmon+ZpIOvN2h1azrcF+AGx2IbEV1CtZo62Mz8guIONkdXjOxnVHO+VtfhllFs1mmMRg26sSpfb+gQGE0FuXpzB2vU'
        b'FRiN2IjtcEtDFZCSZD4dbpn5BjM2O4wdPFRSB4vJoENAusfUwcdtMXWITJYM7oxPbuALerMmI1fXQes7eOhWh8DEJaBzOkR6U7rZUoBusmaT2djBFuEjL8+UjbLjZnTw'
        b'Cy35Zp3Mo1f19JcckIaZ7KRQkYMYX8OktIkQF9ZmWRrLQwkt4GE9lkUfEZKOnI4roQcw7uS3P7mO0jP+tA8dRK54C3zRuQBd9SeeWyRVGSxPJegq+sVgKerJcNqxD+NJ'
        b'/LsDaN+fUY0/M4wvyoUkLUPmOKYgxWCbEttVVaAtCdar5AlInUnnTSgd1GVuAAtCgYMdHqADElyMlWqkiDD6HRJcvFLWyjMFFUrMSKfF/3ok6PbzsHizMlbeZMQ2xhQk'
        b'CukiCn0joRFINTIIKHmBVBMSP0gksUgIsFhsmLRWNptG5bGo7BQkvnhYpCAxuBcxHxYOfC0uj69lURk8/At9I7GIyylcyYkZ43EtW3BSi4U03yokdQns9/lc7aQcZjJF'
        b'frP23+xkqlBiZYhLgK9C/KvC40gGMwUfVM4zfE3GN87EQ8wz6cwdPI1W2yGwFGg1Zp1xNr4r6hBi6svTFHSItLosjSXXjIgWX9LqM83GJEeBHSLdmgJdplmnNc7F17Br'
        b'TSZ4Ap25eFVx5IU23VHuEARjppGEzFhELpjMvDlSQGQgIIYUJi9vGn98aM7zut53jH1qH1RF4CnHJG6WMAycAgfBZT4ysp+H53rYIbh+TEakvh7TvBSe6M0SO4weK+3w'
        b'Mna3lZxqlhYdKvFY01VI3K+iCrwRnaGMxjGINjzQFRoL0XJajIweIqYQVSDhR1fyKsX4vAqH9LCoIbh6d9QcSZbI6Qp1szKYinpz92DSxr1KPKnf40awVqwzUCWnUMU8'
        b'fE50pzRE9AyqDDWtnM6hULPQmRU1pJRn8CfNEyDynoPP0BUWkVuulUeu+VdinQYxAta5KgWY7O16l78Vlzy1lGcl5aK01ZUCRK48pNewBgk+R9fJLytrLMBSB7ERKcfK'
        b'2ssoQJpnJNI8WTM/iyl+QCOtkqZKfFFn8bFcJtFf6NpavsGd+8bRX4hREJNaaVyG3WeOqA6bxh3CIo2ROEB52YiyEboac1YbZ2CKS+Bos9PnieU4R8pawgo6BOeip0bL'
        b'TiqWpBOcLEAV55lmOGkY0SvDeBOgRIDIYDAMIvApYSSItoMQBQ+hSyI1mZm6ArOpU95rdZn5Ro25q3+3swIkozNw1fg5EJeTSCNyYRW+IP61uM/rEOJuQ8zMFZnpfDw3'
        b'Z4PG047pNx4nBoYgMA4KLAnq+xkcaoUGF5eLz91/lVDSOJsjtFc2lrY7ESie9Bni4DCCXcnKRJUK1IsUITIBJQ5n4FF4Ym0P96ib/dsUhw46agnS/pYw24WcqwMhgCiL'
        b'z7FeOb2ER66TeDs7PrghxsTRjfgua6NYagmfA92Ofvb4wzn6XF1ivkarM/Y9S43Rl4AOn0SZCLIETm5nn3ri4yknX4QqEoQE94EtEcq5sMEZQgMbeJQnOMXzhttBOQn4'
        b'WxOpxvNYJMKvM9IGVoKjoMLhorg4j6KWhQjh9hnLLVgXHAs2WbhMISGwOqJEHqeA1aA5LSQhCVn44fGKhCSaMni5TYkF5y0hKIMH3ANrUxUL4mCtLCEpESXFXofkRFTX'
        b'ZniFpsaAnYIRoFGmP6dsYkyYTYdNLPha/WrGSd1JzaLbu8GVhtZFxzfKKpo3zdjftKe1qrW8eRHvlezxYwStOQMmLvrtgOrcMuvOIMHo81Y3k3CW0BT9FrPTc2dF7R3J'
        b'fj311zU+f2L3yvict6Ac3BTAGiWsFcMLSXyKHUKDw/D5VcRpooOHQXMPZwXYBG+sgG0FXEDiwanoHNYqYGUE2MoLLbR7Z4IsKB0PNprxRPNIuNUPXl0QFq6IUzCUABxl'
        b'IpMGEn9H4rJlyvCEJHk8qHP6gPhUMLgMWp7lL1kDbzrmPJ5eqHpkGnVIkKfn5WstuTrixsDGCrUOfbKJo4Jh7Q7IkqE9KDa8S27nnJJJl5uFjhgeOn2U/L45ljEW4PNC'
        b'R6uM+ZgYaYdjtAx9Dvr36fB4Yrt68JVzti/BwVeuwpxGTOvu5C/+r59Y5FMutpWTvzxVXDjLoVXgImxKU/bkLzW4QdgrPGtlL+xVDBsRA3TnLtgUalHg+iLhbhf2ilNI'
        b'YEXv/NUPbH38DLMdNOwzzMhKpbO6W6WiybmavAytZupztN3Cs8yncDTA3lSTs8UFnQGDoALsTIxXwK1KcCYuCdQ7qRju6DITyIvyMYFt83zgGRxCsakfKMvwIL1WADYX'
        b'gROU3QtaC2vk9uiSebzRA4Z0eR4+5TJrTACUU5kYPNROAOVVomEsZdEA88gAs2RQeWuRrdt5/jgAdep0rgA6AZ2HwaPPKPF8Tjg3uQ/OwMbUuDAcJzYfsb9CBusT4+c7'
        b'h5JPgUadO3zeMoF4rcsLWer71P4k2ht6L6AseOZsEdxCuxaZipFwHB5sWGkPJMBhtXnr3AaA7V6EhgrhjWlKJZ5Nik+aGwKrFnLgOddZLxqvZbAVNHoK4blQk/7gnAi+'
        b'KQ9lbG3+ucX4kAQqvZoV7iPTJGpys3IzvlHLjV+pX8v4TcbvMuI1W7WvZJzRfTn9we8jqfmT6PnR5Wm26E9fbY3cfn7+yNFRZdKU/cfKY/fTIwK+2v5qw8ta6u337jS8'
        b'+sadGxtbN4/evb4NIejMwCkjLDIhN3t3BtyETb26uMetY3kacI7AYCzC1FoHjCIMnT3PBUXhBbCHm2E/uojpgZaDQQUCTASW7vAsAW2wCZwcZJ9ZTLbX5gEvRI/iDYAb'
        b'BpF4JkloMrIcHXOP4TKBFrRRPmt5sPYZcIO40xHwlw93pMHzQuJxq+BpBtZZZhDYnx0Dtzmn+sk8P9wLNjrm+ut9fzlse+I5/PQCI7LjsT1FcDvIgdvrKBFDzGtkFzE+'
        b'xNXsQ5eM7YmSujW6TDtGdmpjXUvmeJ/PqXmd2vCTpp7sM1SezgwE1s3oUIFhfbgD1suo//QN7JbluG/3FAzrFUueBkdwyPTWCaBuBmzlx8Kr08HFYNAso4bDHb6rkBW4'
        b'Oxc3NjMkkP3eh1L/zH486q/MpdHPBP1Ek6nKfwbuoc8LKWlk4Hfy941FI0IocvmrQX/z2u5Fh/wlZb7gpwF/C9hJ6TseJNOmU+jeigNiv9pJZNpode6on47GJkB6vGD1'
        b'feroolgQXHXygeDZv94r2DT7QeP4F+P+VhxUuGXqiPb1rZkTX6/ekZIcmF95IHzs17Dt46zgwtVTBq7/8fSlOe97vm1440HGvri3Z7654Orp0HeNS5/7GURHfXBy9z3/'
        b'0LVjct89E950dth8o0jsP/bBjHtxr/z4cc3RL1R/78gV/Kt/4ZeyPb9Z2Vrz8bcJR37jbr7x6O9ePl6KPwX9RibhAvpWgNoRYE/nbI/LTE8dfJ7Mw8wBtUtc9ZrJoJGb'
        b'h4FXR5JCsmD1KBd+tHOjN7iGGTLc04z1PneU4AjHaHgwA8AZPJ6gEg0dGksOxWO0guWo/tNmPB3ixcJbnA4EL2VyahAScxsIb4dPg+3dh55PDQQXB49lQU0mOGHG4cse'
        b'oKLEDiaEXEA12AwOwlYh5QfX82B7GNhBprLk4FgIUeqS/HLsOh3YGk7C3uAJcBReDsPx8bAF7kPqwzganEVMu5GLrtwJdpnAcbDTGe/YGew4HpwiaUagB39+1LBeRRa8'
        b'kENagCPRUmBNItgKbYj8x+P4zv1Jj1OZfp1hJHACiNiF9wl6hDjQw+zU+hh37FdBjOmNzljGx0uAjr7ISi0Z/FgsseuBRKnrENivdSLGU1vNSC8swucFTgCxYInWRS/c'
        b'MqRvvfDxrURoS/yx7un2C+npyDhPL7RocjlfPNFCSZUdHngFj8ZkytQhbEznns/tF3V+M93hZi8EFUAeBscxZOCHwfJexDC0vwRhHnapg5tu4HhfoMdQE+EpN2SHgD0B'
        b'43pYqyL7twnrCw5rVYcsULvXCutAfKT9MFreRrc+bdIUjRn1mgH1mCqTdSkd049zTh7bw07FmajNJC7Qza5ZsZUipFnxkWbFEs2KT7Qpdi2qq/O8r7gkrFn1VJ0FKi56'
        b'sWnuOqQ298eQ01VzBhv6WabjFDbVMiRwQ+KSwpHaY7cXFfOQlpQagr1+80Vd17LQ8Bg4oKSoqP5ebvAoOG5fHJMfCXehikbDA86KkJSHVSwVNJuNCwWVnKV8brFYiaM5'
        b'VzhThYXGCaggEzsfton0P+RUs6Z0lDBsy9uDX73er0zqHfvmB58didFuWz1sYuYqMMB7eGb7yK03ohpT37z/4ae357u/Pz5vz53zsadua26/czcpQb9+YbVg3qf72zzm'
        b'/ai5og7/ds6h2H98FDC3o+5eQtO4wRFbzwZsPsBHShTunangCmjg4Bq2LHadNh8B2wna+IL1sBVB64I0p4E5DuwiUO/Dh5VLYC0xSpSgilt346PjgdNLx5MZe89norlV'
        b'Mkj6Pg8r8FqBY8yaCHCGKDrgZBCy/NGw9FvVVRYQzew6h6ngAGiAB8fAZg5zHYi7H1zjpusDQSXYDm4S0HUA7mV4wKEk/TK+cw2HzUIUnY6tUgJ4/g7AW0cNd5fgmXoJ'
        b'LeKJGF+6ZGAPNgh35uWYX9DBy8w1dYiyLLkELTrYApS2Q2DWGLN1Zhewe4JKh1ByLT7HIeXGMnxY7wS7UnQ41E1b+mRQ33D3uFbLGJXKDnjG1fiwBveImOBRns68Ml9L'
        b'qjMWO7rsMbLHWOJsohUdDjhcaxjCLLgGeANuG9kJXyI8kJ0ryybB6+OkAnAC7Isjls6qQh6CoPte7pRa/kmyD9XD+e70guHJhq6rrLKEzjVQ9FOvgdrYm1e8Z6RRoMoy'
        b'Gp1Pg0dTTIik28WFFngJ6SuXYau5CKsU8KK4CNR5FUhgK0VNgcf58DzcAzdYpqBc/nDHMyhTVaIK1oWp5hPzPR59VSUrHItikT1YKQ8HrePgjnl4lRloB9fc4S24M+OJ'
        b'y3l5ZNL/f7RAoCfM8jkPYDS4agoDJxO5gQS3YF0SDgbrn8ZDYFc3j6wQA43wJDiHEYF7UrgjDDSH0BTYIwwCW1gjuDFHX3yqjSFh1B+uW+5X3dqvLFLywodDgwZUb/C7'
        b'sEFcL39h03XfPR+/Cz7cfmWbyuejWZIRU6s/2TrFv+bezoBxb76258y1yLz9M3MtA17wfPbltT/f6/DZ9aanjE+gTAdOTEYmGVmAJPAYBk4z0ePgHnJrrgaedmAI2LOC'
        b'wMg+d2KvlQ4iy4xqImC1gkvhBdbzhtGr5hcT1RNsXKpB9/GKrlpEnKFTJtCgNc/KBQHWw3MmJWyO55ZC2MOJYuCWJy5KEWsKCnSIHzFSdHW0raPiJQR/vMm0VUkowpD0'
        b'XH2mzmDSpWcZ8/PSs/SuJppLQY5aCXb0Hb6NwLPMybXl6PByN2C5/piAIjwFOD8IVCuTFaAKUz431qAumXgz0DcnRrvaXgXgAtxmXzCCJAnXz1pw0DsPbM8iQUpBsNIv'
        b'DPdxdAxTAA5RfHiQRlywey7nILuSJRwrR0zUuroIthdKRAWFkkKW8p/Ey4YHlIT6FmbAsybYDlvdPIpGwWoPd08RvLAaM2shnxrhw5aOjSLL0cDpxcVKJBBxXeByBg+N'
        b'2XkGbJoLr1om4Zouw+e9QQvchk6qEkPh9hEJcnAKbl8tD8GqQ6JjeUaqyL56GdH3UdAmnhWxlHh6VsD94BConuko4Mm5d+a6w4ocJVH24HVY6wVqCgrB5tXwkglZXZcR'
        b'3piRtXAZAcplC3qSVBasN4DtZK0lPQaeI23dhVWRzfDYUCSsE4WUF9zCm6cHGyx4Oils7DRniZPBbkeJq2GrxF1AjYhnkSnUOIqYA9wSv+vgmgdoQ1Q5iVoDTk8Cu0aT'
        b'aXMGnkOcsi1ZEY8snXOpa+PihZRkCgMP5vkQcATXwfYRYgVek6dcCG+h8a/shnngIgG35XC9ENwITbZg6nx2cUAqqnoEBSpyRsAtwUQM/GGk2+QSHnpCtTpx7UARF7s5'
        b'qVgwU0WTleW5r60ORxYBufzlWmbBfZqEdCaWZNmDhRmZUOTBrULPjQlfR5EGTl8zkmiJ2ANWBW9OIo6vXluYD8pEpQN89IY1StoUi7hjl/KHpJRWFYz0tb6uunc8Sex7'
        b'8v4o71yJX/8M9akXyga8s9Tz4JLmHcPH7ti9/9iMU4sbD6kjKiPuK3fv/rG2/sYXx+fr3r361gfXf5y8adz5V9lBPiXyO9MLX142IW/6mttb7v/z9pzwkbrG1yXD8hcX'
        b'VLmtad55PnHO3jGx517zycu817jmVHXFnYlTvlvUanp54MCDX9x5T/vn7De258y79vd5YWu+XZ36p5u+hVkDV7QM/qrks3kT/7JG/Hrg5Rm8w6+vnfB1yhsDEnTrf/+P'
        b'/xhe3Hv94pcr33vtpah/FC5YdWT5e7MCpzAzXmi5Zz30od/pgrUmtwF/6J/f/+pd5bexgfvesazZdCtMvunutbf/9sqVRR/nrvS9tUS+rp+/atLSpXlpFebJ87/5V1S1'
        b'6nd3jg1hPaS3zv79rYAfAqZNunx+WvyIk/1v/e3u8L8fi68Qj/mKvvfmtJmtxRf6bZB5ES/bKNAE25R4u4YaOYYMHiWGF3hrkf6I1L4TZgyEhTmFYCM8hTCGppgiegbc'
        b'BDcSME4CdavsOI7M9+NEH4SbZhFdcRJsnKdMDA3nbotzGT9YBo/OTOZs9y0WeIosRcfDrHTDywxrmFIFqCFCIA8cCwhLxs3BmokQteh5Btx6Fl6WeHJAXwv3qOz4tQ4e'
        b'dix4OzWWi02tAe1wexisjJfHI/4bg0QJn/KazMsClSKSgIUnAPZRoPy1SplChTSfgMTFZnb6DHvsK9wPW2c7QmgZM0UiaJFmvoXcXYbYnTQM1ggp2LCWVeClg5XgeU5A'
        b'7Y4CVWEJSYkIS2zB7DAa6dS7QDPRwX3Gwi32YjEaoyIQdQeASyWgjo3Lg1e5iawyI7xsF5ygAlxBtSPRmd6fNH1QGrjQfR4L7B6G/T2BT1Rohb/UE+HXq7AjAnJep4Cc'
        b'hsUjS3yZ3ow74+2O/hkfGh/ded7o2gDnvLmEBAuFkMB5H5THE133ZHBUCA4gkjDGjQ653My4iMynabhLXBsu5GY3IfrigL6FKEajcQiLDnaVomJwuYcg5VMrzCKwA5ww'
        b'ynhkGaka2uROYwkcz8H2UimoJhAdBk7NhzUqcCYxVmF3PoOLDLJnz80h89zgFtgGL4UhAgwVUIJYeAM0MtEqeCmT100H9HfogTg+oMc2BpRzIwO6y1YGjM0vy985l8J/'
        b'qrkUHplLYT8egQbZXeryN0+XrTeZdUaT1LxS131/nnD3LmnjzVK9SWrUFVr0Rp1Was6XYsc1yoiu4u1X8MJLaT4OJ8zQZeUbdVKNoVhqsmRwvp4uRWVqDDhcUJ9XkG80'
        b'67Th0oV6ZBFZzFISp6jXSu3USVrlKBvdMBejJnQpyagzmY167Dfv1tqJJBxDik3FiVK8BxE+w2GLuEh78egJe8mSoyvGoYVcLvuPbhm10iLUZ6hNvRZgMaGbXHZn+tiZ'
        b'8bNSyR2pXmuShqTp9LkG3co8nVERP9sk61qOvbcdUZUaKX5GQzYOqdRIcbgpbo6jrHCpKh91XEEBqgtHKPYoSZ9FcnEdisYqQ4MbhMYKjY0p06gvMPd4kB6eIU+qu8ki'
        b'Vlli0LkVtICyfrNTIxyTnfMWxiFtNDUugT9vwgTQLHOHV4sngB3Th0/wQ6gKT0oCwbUJPVjB21H+gq6sQNmZgXYyA2PzyvL+FVOJPWxQDCw99+FQqFA6Ajo9g8l6Bodw'
        b'zaScc5v/lWmIq+u5/ItvX26M4Vv/sELPNxnR2YfBw75WKz6P00iyvlQ/VOdlfaOO17BbHkpeq9Un6iSxSwbXSr9T/WHyJc8/mKUf3Hn7DuWjz8rbbNZU/r6F/3WLpkFL'
        b'fa1blSXXyasztNQ+kX/67fPedy9oQtofqpffvtKwfktTeaB2ZiQvW0wdXDMk6PQDGUNCJXKALS9MEYLdWOvgNQHYyyjSUsgdUGfUhi0BDbAeK9yshYZVHkt++TwbP321'
        b'UVNAhNGQTmG0jhqM41iRyMHOcdqXFiBBI6JLZEY7gLkEY9lJ3eUKLtG+tJ2Lg3xqb1EzzWUgAsiGKQa1jCzStAugMurLx0yn4TWC8IKPJYzjDiSDbHgOrduMGajpNPFi'
        b'fWQRCXI8A3TSS+8Fy/qOUJrKcQr1q5dl93AB9x49IVRZ5lDE8LgMt0RHjomKGT02GlxGOpXZWFRoMRGjqR1egJdgK7wI27xEEndPNw8xUh0rQS0zEjZSeEbHDZ6ZCQ8Q'
        b'u+EluRKv3PXuGKpOYPyKOWNi+po4qgF9Hc5WJ2SPiLITfGzaDb4JT0paP6z2e3mYZ1mkN3v7g68/0wTKBT+6My96nb+/d/oGpvTEqke1P5zwHbsn7mW3bM/FUdtOj/98'
        b'+bLJ2t2z4+9JbvGWJWVe+fvyvVE/Za+/Y54Z/N33c8V1OwZe+5p35YRv9phox44LTavAMWUg3NrF0QDqQD25/Sw4TDaWWW9x+imwlwKUj37ctNGTliSK0o355vQMZJDj'
        b'Xh/gSvJhmOR9ELGLSMB2ifypiN1enGNKyBn3+zhfBcOl6CT1anQI6UHqHY9ZwohjOAuNxWEOOfBYKofXvBChw+oIUJUcFcOjikCNd7gb3EsoAQxiqOl8vPxbnThtdhDF'
        b'baZTDzcgS2Mbos9weAY8j47tHOHIxgqoyW5DsRUq+WfwBO6iiWEpVu6Hgzkkn8wu4KiJ3EnNE1Gi8VJs9UrUy924i/NDlNT0/jKa8laHfrx2FndRp+pHnR8aS1EFagmS'
        b'xxS399BN8bRUWAe3zx8bCaujMllKMI8GpxPXcMtnSwZS7f1zEG2rraFjn+XKGTislf4mRIAY9/7qAeqJ84iCmacISB0IdwFcEqzjUzw1PTUDNFrG4WctR1bULaeLj4IV'
        b'yHJGdg2slCdgZya2cUg4CdwcRoy0qjB3mWoemSr3mCekkEUhpRYcDXh3wL9V9RRZPSydNlIkWkxFHtfJFhgzFeMKUn4Xo5r6iYDbmG0f2AqOwzYkgJJGgp1U0mBwkrT8'
        b'YspESrvoW/w4xk+ZcdzjXIyZSslniWkqpcy4aMA+Ebn4vt9UanzAI4qKVEf9y7CQSxmeJqenj7vNUtIy0+7s8VPIxUb9H+h/j88TUt7r8xeNPhpLLt5cNYeOGxaBBnd9'
        b'ziJd2GJy8e3BvnTapCwERGWli9atTyIX34u1UItyPkNNLSt6R5Co5PbIK51PS5cs5FPempw3JsZwtd8Y10DfSJsroNRl2e8MW2AiFzdlLKJCSk00alLJ7tD9meRi8Krh'
        b'9O2YAyxVUFa6e+2pRHLxTcFQ6i5TQ6HHtL7DfKLlHnNlIi1KmcVH2XN2PxMXTS5mD/SnN05ejB5TXSp0G8HVPjHzDdqXmSWk1Jpkr+kG7mJb/gvU29P9eYgq4z9Yp+Eu'
        b'HuOXUmkB36H+VC+IHDOQu+iV9j4lmVjEQxcnjMxjuYv6WA+qffUY1CR17sTwldzFoIEF1O2pNNJP7mf4rvZfqv8cWfOmI6iDPjzWNH9uUv7bkd4HWgePeljU9tuFO+Uf'
        b'tW/fMP57YcE3EWovEXv5xGfn7yXkXvF994TvizfTJvyw+3vhdznjn3lJNnPmzuzPb06e9vr4Yee+GLZl+dumv1QvWZW379K2olsHzip8vy/+/JmcjneXQGm/u4PX3TL6'
        b'/nVTxF8b4ALzFnE4G7C1/6vxccM/6n9PM3vKMwPfaVnk8elF7VjvbZ8MPPaCtXZxrHhVmvYjnx9K5tZ7vtRa8w37/az5h2+vPfJCxF8P3/l+2opJdbnxo3ce/XRq/oYv'
        b'Y45/UhJe8mHKaQYa3k4Kbt3495J/uVXs36dw+1usefeOjdYZOfOrN/e3fRB+8kPJ26OuBEcHq66PuPbN1E2nL1+Zcv7ujn/fzJu09tia0Gu2m+qjSx/2W11w+c0PBXXP'
        b'hbTeLk1b9IAe8qDfkE/cDj4IPPjJ9JGTzO4Rnx7bfHTfrt/d/1HpV52z9tldn771ztz/9L/33nMdQ4Ie7Syy/lAjC//uYMw3qa+eG/GeV/v8Ub4j13zwF1lpuNW/XXnk'
        b'8Cfnbh2wPJyz+tTa6AXfn4s60HGgbMGY4cFfpv1UcePeklt/Phfy13/+c+j48ZtXP/cvmYgTPDYfuCkMHs1yLO/lPBOV4Cznt7gFD4HrYXj7MLg7Au/71USngGugldzN'
        b'ARtgVViCQqkIVcFqsI9PSQQMvFnszrlkDohBrYtnfUIKbEFCC56eQVz2GWA9vBYWuQDhdDw4jcAslxmequMaVT16Zli4LIHbE5FPIWUE7gnj5UcwZNITGdbbizu9OYlw'
        b'F+fQgZdBQy4JGVGALfCiSxDWImQWd+63Ug9afuHEosz7l0dgPLXaKXJIUiKGM1zFcKCEZhl/T293lnbd1Qp/D0HfA9DHhx6BpOIgpJV6knVWvjTL86H90bf7TwzD/CTi'
        b'CUguEVluIEH5WDzrENS3QOfUVT5Z/9AhtFuhHXxiWrpI8v9+RRlSievwOVloUe9UABDwUX49FIA/hfatAOCNtODesbRdAxgFdjxBCeAjugdIL7wBymEFCTxH0rAcCaIa'
        b'zn0sMaKUSM5hTwvnZ4kA7Xx4mifltkDcA+pLO2f8SGAuqFR5wwq8ARbYRNAxyo2hbifhJ1JLTIvmc5D5zlSW8h7tQyI9V0Ys5y6+qRNQa5QDyZaqiToepZ+TLuCbDqE7'
        b'3r6+g2uneIJIyZw/jdS/1f7ZOFHhqJgFR8MXvLt0jloaV2SgF97fuNsz+cK0aet8XvrBfaPboZCw8HfOf7Y17OzVj3cG3PjUI794nDmtofifG1c3GCbOnli98PADn/1J'
        b'3154/bvjAd/5bHv1Y9rn+Iyyb95///kt+08HpxSXbXzuR+mpKWtfDDOFvhPwaPPNNz2/OTNm78J1S8edaDt0YOt99u+fCb9lIpaX/kUmJKFX4CzYMFUcOgyc7dyj13WD'
        b'Xrgvjfgh4a6lYJ/TzwlOlBI/p/cIrpCtYL+yc4zgcW886QQ3J9JUEDjI5o8GJwjzG4bCva5DieBh0VCfUB44ORpcJinGwuYYnKJz8DxRC+tn8mavgdUcgLRMBftBTYRC'
        b'pYDViTIB5TUIIUwFLx1eh21ca3bz4DFQk8ypPrBpeoJz166BYAsLjow0O+xL//85NDw1cDh4mABHqCtw+OKILoYeOUdCmJ7BCy4Zf7LGSECgwoh3CbPb93jLMln//+t2'
        b'b3YyOK76527e1PKYx+9xANaHzEbs7fscp+IzlFcMLwseBXW9TnHjP5OE7gyK0tJLeFpmCavlLeFr2SUC9C9E/6Jsaokb+nbfztvOavl13HZnONaA1Qq0QrKQR6yTaEVa'
        b't42U1l0rrmOWeKDfEvLbg/z2RL89yW8v8tsL/fYmv/uR396oROJYRWX6aPtvFC3p56yNdtbmq/UjtfmgeyL80frX4W3P8OaAAdoB5F7/Xu4FaoPIPV/774HaQagGP/uv'
        b'wdoh6Je/liVOn6EdnokcxCdpDJpsnfFjYXenLHYcdk0jJWEjXRI9KYfehD2ExE2rLTZo8vTYWVss1Wi12I1o1OXlF+lcvJJdC0eZUCI8NWD3enIuR6c3k+QIl6bk6jQm'
        b'ndSQb8aeWo2ZJLaY8NbuXRyQJpxEqjNg96RWmlEsta9ZDbf7lDWZZn2RxowLLsg3EBezDtdoyC3u6pecb+Jc1agqjdHFu0p80Ks1xeRqkc6oz9Kjq/ghzTr00KhMnSZz'
        b'ZR+OY3sv2GsNJ51pNmoMpiwd9nNrNWYNbmSuPk9v5joUPWbXBzRk5RvzyM6D0tUr9ZkruzvKLQY9Khy1RK/VGcz6rGJ7TyHJ36WgR4NXms0FpokREZoCffiq/HyD3hSu'
        b'1UXYt0R/NNJxOwsNZoYmM6dnmvDMbL0Kb3BQgChmdb5R27cHaTpF3Jgst8bNsaiulCFe1Sf7kHjEq8o+qujpuzbozXpNrr5Eh8a2B2EaTGaNIbP77AL+s/vPHS3nXOjo'
        b'hz7bgPpxRkq881ZPf/lTbMMpUFkiMYptziYSsHPFDlmuA3fA3T2W7CAxZ+PWMe+GG2dwmkkRUqhrsWoSEicPD4eb8f6+MWCX4DlQFiujSSAPOKYBbXg75GQFXjhSl4xV'
        b'+us+YD8Proe1U/TH48byTXixd27VK3jhXMiDZdMeom+5/0N1nH3VR/iCEE2ChmkLDIhcHRmhXXb7QkPTtqvlspqL5VfLR9coKq7uai4PPjilYtju9dGDqQ0r+h2sf4QM'
        b'Cozn8eA6vOIioEtHdxHjoH0OtxRjXzI80FNK7/XnzYYN88jM5Eoa3hQjZUyWZFHH2hUKP2BjRfCkD5kYhddQ7+0Kg/VxY1hKsoYHr9MGcGIut0qjPgDUoG5YAU7inqDJ'
        b'7l1gPaiEW4jLOAJsKIE1ShwaoRCSnZqVz3oRLWXtCLABlWmeFDcmaiyPEpbQcC/6tJKbE+X55Nkqk2CzPFFAIZ2QhlcnznliGJ2rup+uR0Sant49MBF/JBKykgMr6yUB'
        b'Xak33JGPk9rNXMi1cQdFPXGFRjPDJeuMrd6FDhsYx3rkMueH8u075LCv9vS9sAwrt1ZqFefxpTE0uDmMDF0zzTWn6yIzowkdtqCGcXuedK/SsQLtUWCf02qoEp42P/Op'
        b'GpXNNUqUbjdyjPv6aNF2R4se+bpMrTlm6MKfqrKNjsow9uq1pj4r2+WsTI4rcyh5vczkZebqEaYrTAjaZU/XCPsTi9N1awr0RiI2+mzHXmc7nsHt6MyB5VL3ju9avQPr'
        b'yW6F06nOTVxtfBes/y+2ce2yk40rymKnYvqMpamwDl0FJ5CtfxGhbm4JuQGaEAaeAC00XpwL2kup0mfnktcUwAOwfRGsAVU58UTPj2YRXtQwCeACaNcPvmpmTUtQqrZh'
        b'5wfXvOpxWyphV3tMWCmtO8afPWJV5Dnrsk0Px3ieG1xXJN9jvmEd31gQNPKf29KW/DCmUJH6YpvAY8DYn1rvjftolGDH2tmFfxhzdVXJ4qknX627N9VbvtEvkMn3kLkT'
        b'7OTDHeCWq3FDkHNdnB07E0EDcbswk70QcE1Ctkk8N1cArzOgClROIxBl9oFtStA+pctMAtxZSiBzLDwJKx1uFVZFw1s+4HxUKsm4Quvl6q2hZyHzuDUUlpM6h9OgwY58'
        b'HOyNVCDggzVzyV0tOApalLA+Ar/Fg42h48FNcAOehptJwQyoLQ7LBFWKuPjO/b/hxtkkK2j1W6L0RlKxznWbRXi6hIgJK9g1GtbEgTNxYG8+J9Royge08OCm+eBql33b'
        b'nhJ8dYZMY3GBmYAv2da7E3yH4e0YfIh/xZ1EZ/aEPHtu10UvT7c9o31H3U4EPooOB3pB4M9+CQLbm/N/qmet7FXPmrVSY8jWcbEbDs3IAQndtC6kPD2twmXQrX5aPQs/'
        b'cs/luCxCN8LRUcNLuyhBwjkUpwOBM9H6xYkDaLLu1aPprl/tMJ/ySF/+R7/9OeWrUxP4N5mF082nVkVVVu5dkrJ74dwrM41vbdp+9d3FbRkvShZ//MdP91wY5O6+UPRX'
        b'7cDNaz8Dn4qLvL1mr9FFPyi9/km058WDk1vcm5ttl6Yn7nolveHWtUq3P/7T6x/b/OW/OSBzI37PILDfzOksMXAXRZQWH9DI+SVq5+QgJtsGNyXjdb/glDyEpjxhHU8H'
        b'Lui4FHVZIRw/2JkhN9PODuCsjHC4AJwuwq4NWE37wT0UG0GDtlDQTLwaE8ZNVsImuJtsOatMBnURnWpkJGwUTJi+2B4whri3EalHCiE8Iee0I3gKbCAV+AXJlP3gLQcz'
        b'cnpVgok4bsPAOdCKHg5swA/oVJ+yYR3R6OaB6+BqFxRBAIQQ5yq4YfrlvOyVSWgw3UEw3cOs8SfKnbg9Q+iSId14p1tmuytkd58cbNzjZF28terJXli34zGs+4TqZbwO'
        b'wcp8k1mv7XBDjGE2YBWhQ8CpCj1WZXVlb9axTMLJ3iyJzXryaixHbNZMupsbAP/N0GqxCYVZ0kXv4ExQp9Tvk6+5h+G4Og6dx892oEOGxpDTk7edcGB/di5nCvcTZQ5R'
        b'WgzIgFXEz+4lYMkl+MmRE5vrOFuXYCdZb+016swWo8E0UapOM1p0ahyzxG0ooZVL1XM0uSbumiYXXdQWIzUIa2MG86+CJ55K3zzjZZ4Je7zf32L7Wr3i9ht33rnz9p0L'
        b's39uuLqzqbypfEJN657W9FM7WzeNrmne1LR52P71VcMq1vNF+/YEBm4IlARWKyQDBtyJ9KlMLcvYr6AS8zzSZv1NxuMCVTfjFw64ggfSYA5jACmZxEnbS/DqWMSBW3MJ'
        b'QnDwAFvAIW4v112IQS8p545KjAdVyUmwOjEc1EeQcFYZqOWDM+AiPPbLGdVTo9Wm6zL0mSai+xI+9e7Kp7Mwl5YM7sYkXfPZ7R4BJ0RP4MNJfGjuKn9d3xjBuiQrcKYl'
        b'TNyCDhd7YeLXHsPEj2/f/ymbZiE2fbY3Np1H3GmIUw0caeJgPRd+dXGk/f/HsThbfGqylHOBmTmPGbFMsvQGTa5Uq8vV9YwwfHpeffSnBQzh1Q/ZqYoxLtz6q3hVTyUm'
        b'e8RcVSNeJR6QY4HgPGxf25VfibA/Afdx3HoR1NLwMii3C3SOXWPBNjOeslKAQ8FhCbAO1kUoQV0Xdl0OD1HTQL3QB+kStb+cYftxPton8Ow8wrPdtL3wHlntkvV0N940'
        b'nnGy4jl0eKEXVnz+Maz4xGqf8Nod2ka5vHbn6XYud2jDGb0wIaFIwi0GS14GYjxEhC4u7k7HcabFaETiI7fYxbD/tfR55N/DeKZn0YX2VCF+s8/5hiZCl6N7p8tIswtl'
        b'1rlQ5kPqnQhxzc/PI8qUYilyAWwANehzGu7uTpuwAm7iJvN2g0PRoGYd2O9CmgngIiFNsAmWxWN7EBmxnCTRwnIHdYYKEG1eFUoz4NVur1/qlRYz8y0Gs8vAmnqjxSWi'
        b'3mixR1aVIxSzoE+ZwblDCF22osNbvdDlub7fNfTkJvwf0SWSD48MfdJlZ+j2U9OkNCQUq356g7QoJnxMaC8Y/nQ0Wh11iSI06pXc4EKjj/qk0j5oVE+9Ey6ufq3djp7z'
        b'jdiSSIZteKlqV/S8Ao9wsSuXBaAenoU1XdATbppoJl71etgCD3KvFHRRdkrtiyfGA5sAtBWveAoK9cZ9+yQCzeA2VetGHd1z2rHyQt802Y4O7/VCkyceQ5NPqlUW0H2t'
        b'uDA9XZufmZ7ewaZbjLkdHviY7pj46RA7V/Dotca9OBN+9YmxER8OU3bvcoeowJhfoDOaiztEDucsCffoENodoB3uLk5I7A4hhhVRzIhIIPxHHphzt/yKXVBcPJpb0CEP'
        b'dxyOKBYxrJilXT6MiPb1QN1HMz8JeH18sz5ilEoiob098b+niKy+XABugMbOWBB4MQmHJCUjlTkEHCoE6/nrwB7Y2GOKCKPAdEwneEf+rrPUXHx0R3/7khj74JFNpB9J'
        b'Y9fgLS6xEzYTr3cxGrC+56LfqZD12nUwjRedHdHNyXsTHT5hnAv6Wft+JBvAzsLOBf3wvOPRHEEdCalqdyHYnD/REouS+4/zfOrIbFABGp3R2Y7QbGR9NPUARbEDSnBw'
        b'sH29A9X1Vaude/D+Ny++wZX1dCRLVDIeF0A7Q7z2cwZPl0lzdxuW8EmgayTS7pG1VfBFEiV5d9FdMZ/KJQZdv8n8hwOuZv8cO1B2NScl/dTQkznXFm0I2at6afyYxXXy'
        b'A8lnJh2buHzwWwnvxc+O/dfi7wf+HHR3XFBJcZhmrkiY4/v64L8xcIpkjO/4K6MrxrxcWpQ0PnhdSP9JIfPXTLvEpvscKzg3NCP9PX27cPj8o2rd+IScu25/ip8S5hGw'
        b'cpGRXzb889lF7l+ZigpCAt6NPSUO9Li27mdkh4RMnibi3vxZ028CrHH4t4ENtnM+btiSwYWiqhmKpRZNdaPUkrDxaVxo0rwAH2oEdV7hRamtfO9w7uLLKwIoObVooYdU'
        b'vaw02cgtvp0Pb4EGWJOkCMdv0nVsPgc3K4VwC2guhlVTh8SCHfxgCmwc6QabkuWkqAF+fCQ23pjkOV0tf3bxc1z5zb5CSkLFlUikasnCaBO3sewB0y40cO/9C+Panwfr'
        b'N7/0Ot+EV0WMe/BRcN11D95oySzZq/8o9B8/8OSRxSMnafnDkq7NSrheNVAnfu6tV67MeeEZ/rxm4N//+tip2+Jtf208tCgk5dU3Cp49knBp75jQo0owaf9mr4cdX379'
        b'ux0jvtyZ8u6VgiMtL/7w7Zj/zBAmeq6JeC3/jysfiJdu+mjKkarn3rt77ceEQd/Uvpr8wh+HttSP3Dp8tow1c2uokYWsdPiyYctSuzu7Fu4i77byB5ULXF9lTjgKaUtN'
        b'9lApNCxnOUffNXgM7gxTJGT54Xgp1JF8Sgyv4RjH45GcArYX1hWGwepQ7IWD12gBaGQmDAY7e4bY/9qdf123MzCaNF1c5yR0p1O8mVkSfIh33xYx3rQU4yk6N95yFINf'
        b'lI7DGVyUrl/brGbaeMeJYbiCb3uRh9ulfccTSVHKtWDvwLBQFai1K7jgEGjEKsRAcIAFLZPyeyBS152QeiCScyek/wqNep/Wcneg0RF/d8oaMY+g0TtrvxQQNFo2AaER'
        b'yxcgcYLQ6Nj8cg6NxMqnRKPQwxn/kT9KWufx+UCP0hvzz4dsnDU24QtV8YyPhwiC3Ae9v2jmkk/oiv8RGhX4p3M8Xp/DkJkK7+EF8tqYqdzFuVMw2lDU/bxS68V1Gm72'
        b'kdyZOQTjBCW9bVopf2PgFO7irmABwgnK+37/53J9g30osv2DCJwb64Q5eAbU2qfyAufoF/gJOLf/pAcXFL9t9YCREvb2iRUX6pr299vY/u4rYd6Ge1cTNAtnlr3u/8Px'
        b'JmrciB//YZ4krfxgbVrgc7YTgi/65xsiXhdvNxx68Y173qZVX9bmXjtTPeSHuo8Mtti3Bn3i/tvDp0/86ZmDfympmxow+Q/TxiYN3hUuldHEbZ4OmqYpufeyg1OJ6GmW'
        b'MzpQPauLfvmrdzsi7KnVdbLniK7suY4S4qACX07RISwqIQxrhM6Cbv+KFgAnH0I7n3Tnww1972FEtvcqtcAtHB/GJyE29AabCReqWdAUOqjHokn8T7Z4TUPsWcnntrO3'
        b'0o0UZr4mppQh5zwti855Zhrfn0010Msly5hSthRves+vpMwMfh+D0VDiaeU38rT8JrqUv5AyDMJbzRev4l5yRO7g1x/xF1MGxK6G21b8gp1wUgLOfd7KM1ajVPwm7mVH'
        b'AvLOiCBUj6BUWElbhXhbfK2wDqW3CiZThVsNa0lePsr7Dcr7En5DA2o9H7WST7bhx3lFPfKKUN7fGWaSvNxrhcJ75BzUV84GulBUKeBSoyuUFb8JIoR7DYD9lUEqK6V1'
        b'C0QoY3/FrLsK4bROVzDHOAv1c9ojvsWcpRhvxBYTItUX8FDjG0a83awxiiJL6bMxCbrpDJY8nRG/JwJr2B0CvNG7VtchmW/Q4xOiv3J5Z3KU1rnBaGexZON9shYMr8Y1'
        b'YsWig171C5frd0jwm1lMUdzSZR+e3bbGW9NL7K+M4N5Sgt834m5/R4m/y5nE/i0i7yER0RayX23tVHhTmQSOkDfDx4Ti/RTIXhLSIfi18wd72WHZud86ltdWyiTS0qkU'
        b'fs8UGQDG+doG0pHGiY6HwLsvm/owNj3Io6Wb89Nz8w3Z0TzHK0x52IyxYCf+stmj8MvrYQXcFa9AFi2s4jbFxKoYNRJU8IvBkYQerwVyhqyNIU3V0jm0UYJtES3Pil/o'
        b'RGvZRgq/Jgg1nO9PNdFWOoDCwg5fIY8hsD8GiRhhgteQdW8PGe55+CVZ+txcGdNBGzrolX09G34k/GjkGSfiZ3O3jxtL3gtDXp0JK8Hx4dhuh5sZtRK/ORw9YDIZFAE1'
        b'cgi/GDarn7B+mu51/fR/8fpC2rUKl+WrnWv/HqgLqPsUNb5Rp53z/CA5d7HU9wVEDpT0ftRzsiqrXaq1JwmJVCsQr5ZXDeJT+h17VtHkJSJ3J2z+Wr0ce1C2XSxvLr+4'
        b'582KYX84tbNpU1N5U21rXEu5hc70mOX+yczjqj/MXB+0iZ8oDqzmSw8Plg++O1byWq0s0We6z2Em5CVRVHDFYknIpbIJFbqlXw/LJGutJ8cGbpszAumxWFqlwMPgCFls'
        b'DW654W0D9zKKmXAvF1p3NaWw21v8DingAaTu7yGTUGGgdR7ZiaUqEW6W0yhFCwPOgy3w7CQr0Vyfg2V+oCUBm5iwymMUTQnWMsPHg8pfvmK7X16+dsI47h0Y6Vp9tt7c'
        b'fXNk+45bIsLTmJeDaONbzkIqn6a6Kkd1JOMsnmP/1DKXz63HrMTGRrXHMHgFPW9dMmgdQzaOjsP74dYnO/pofBCyik8I1sYt6xtEsNLMQQeWd00c1zGqDr7GlKnXI634'
        b'Zcohkp/p2k3Clbo1ufqs4iTcdhIrwuNiRXfBE34knABWWmAdagxoYZGZUcHAawXgYt9NwaiN3/1CRKEvfmUSblCpvXmEQxiV8W2KKOuxjmY9br80N4vB3sh5nZiGNRSy'
        b'NydYD8/6h6EWcm1FvH82nrQV7093YCrc/4t6baOjccbf99VjbhkxY7jXfC126TMyxbp/DTyqjIqOJ0ZeogiHLHkN400C+8BjWvHEDuts0x+fqrtQ+zgBu6Jbd2HaF8Ct'
        b'C3ATif9m22ISXAvP8kYnRvaI0nO+tQ7vqKGlEc5jLYoyhpixFOCVM0i3oEp53DutrAzCfKZQZGUKoqw0fr+U/Z1SHSMiR0dFjxkbM278hBkzZ82OnfNsXHyCMjFJlZwy'
        b'd15q2vwFCxctXsJJBIzhnOZAIyVBX4RYWMZ2CLhpkw5+5kqN0dQhwDuFRMdw+oBb92ePjuHGRoefnby5mcf58fCuP9x+ctsHgVZlVAxnisOtsIWMUwBvItwEtvc9ThI7'
        b'tWi5dypl41F531E9wqcPe6WV6BhuLPK70Qq4QoG9uBVk9+sDAdxAHOVFgrLBfe98SV75TTtf+Y3a89S7Xfb6yu+eb31hVeT1EWsU8HiqfRk43DEflhuS3ObCi+D8PHS4'
        b'OM8D1DNUCLzC5sGb4KA+/cZrjAnrbP1EF75WL0JiSENnImHzklrwO//L+6lR/2TnRYyXMQTiJfOC8Uuh62FNhBCUz6DcohnQ9Aw8wkUpHA6BNd3Wd/LS4a38WHizrzd2'
        b'60356WZ9ns5k1uRxW3SQtw25gnyJ8RNnpgqqL3c9SWTuFcTrH/PSbqwB9o/GswlyWJ81mKgdqO2K8HhYi/pypJG/DlY8N6dHJF5XRybPHonn4sZEIy3+FRGxPfaUIUu3'
        b'e4x0PxVZPYXGsylHiURyPaxl4bksShDEuMONcCvROHhZ2J9HeUeufZiTH6+kOHfhTrgDnokOgHVRoDUqkhpOCVU0ArkKUEcwBlEH2B8NziRGgUtR4CKL7oNdNLg0JYoL'
        b'tT2Gdykj74gnGydQ4aZSUlnRvEAqkqIiI1VM/rrsSLvOM1VGpeCLtPfIr7zUlMWHcM+cxFHQZt+pcBIfcjsDvDHeDe/ZExk5MjBLHmFfcR9VwvkHIgVHC/ckDEIUxG3d'
        b'0D7fqPQvjQen5QKKHUSDC7lwA8nw+eLpONx9fGRxfeI/iu07ENaNm4p4nxoQWXw34YWZ9j0UfnTjvAyR/rOt+REaSh+fdoY2fYDuJCWeiU25k/DCdElS1Ft7Yha8vnz5'
        b'Ku/NQ170+kvE5Mr7o195MNPr9zVbr44XvVv+YFT7ulW/CQ/7eAoTERHxwo8X/a4Ic2o9QpN2vRQtCr+SLX6rrrXsjYA89euZfw5KaLjS0PLukpqfHyXeky9qzqCVL/lV'
        b'FI3J8xDX/3EO3+/zAmPwq88ufK5AUfmXO1+lTvvL/YDYNTW3flxbcX7nhi/MLZ/IfEObZs8KfrgxJzJ7wr9eolfsvRd3znPCtAdvT/lHsP6edPJtQcIfThZ/4fZW47uX'
        b'09+/M2zSnSMn1k3cbBZ/nX/tT0Mbn5/526+3yQREEXxmxWAluGl3XNi9FudBC+FjcP1ZuN1FE0RimrzSGSk6lSQcUANOwEuOXe+QDN/GrS6PgbX/r70vAY+izBatrfdO'
        b'ZyUbW9izs4Ng2NcQCKsgoLZJqhMSOp1Q3QkQu1FB7W5WRUVFVNARBQEXQFxQr1WoM67zHMelxxnfeB2VcZuLM6PDXOWdc/6qTockqHPn3Tff+y75qK6/6q9//89/9kMC'
        b'ujnarepTFfNSz1NkHjqU0MwhM7TrdfMPZJMmtxjmH5PqyIegenTNgAr12QoyHhca+EnarZf9BHfz/wSmaFIzHFUeN4Cmi8YMG05Aafz5QGmDxDPWKBxOopPvhbExBYnv'
        b'zwtEW6bx2fSMxcdUPjIq0L2nxOy1TUqNx03hF9s5p/9IPABB+QPHJfpZwbrWdQkHN1+Ad0oU2CbtuRB6aTypPllIOuoAE9UTw0YOk7iBvKTeqm7Oa8HWLlYfmAYn+OVp'
        b'XD+u38VlNYZpJv7roCC1ikP0CANvRoEOw1CJESQ6TUFJKQ6a4L8Eh7Ipm8uAXFmQJyjs5UmhWReVR0RZNL7bJLKIypBLVKoj0l54HhT3CVAyQ7Skyk7UbzwKKOIOFBQ3'
        b'g9G2QSgwi6Iy6iFxV3UKiUs4SjdnDcbCuEvUieK2vGpvE9ApTFupqyi+DC0SY6aW5maPoqDUPCYR4WyOSQHPugDgGliEv77NE7P5PahEFcAgtWvr5cAq5RPML8qeziF6'
        b'oXkYjVf5NL52nYltuVU0NGdFq878kPg+5yQRfTCSlFN9WNuq3lYxTNuIIcbnM9oFXSrPA+Klr3a3pB1Tr+vRCbuMjytOMGKXhANzgANnE6cOw1zDhO/FkYYDSxZxpImP'
        b'JyjVMMmCLEEOMShioHCMhhoScTKphBXwlMJ043vIDaekbCLSw1x5Nr/ssknrGr2lRZMIU6z31U1Y2X/I5fkrr4BrUQHelxZOumzSRMK5T2NjGUvrBY4oQqRZYma/p0qp'
        b'WRUz1SlNLc0xE/KT4MfbtBYm5yXapTERaolZmlH7TPHFTDCY8IHVqPRCKHwKusKEr91G5vtEwwuTKBmuHCiuKQMfunh2PpzM5FUSpiSibVOj85m0iZx/WriLtJ3qrQVm'
        b'9bYZpR1wkQ5yzltoNgCDFzI4xOgZFaIE0EhIGYjXvfw+zl8aFGTA+IOcG82HBGUiXunN9CDQCG74Px02d4goGyhNzIJ54bk1sym3N557O8vtyw3yynZ6Fzn/nY7TSJUx'
        b'3n5WyMujyYDRowV7hvZBoKreC3tD8ng9jTAJnlaP9wJbL+ZsVjwBtHfFMT7aPrROPSJxCoWNZQKrDAbX0tUt2gNF6o3atflzSgqIGla3smHmuX7qvab8ZYu7NzfHSN3t'
        b'gnyAStwK0SNRPEgY3BWmW8QGc4NlhRWemWQzPbN4LA022WKkADW0AERDY3PrCrvcH2NLQtohO6+zrXDIA/R0kuyCtFOPPSlRTMpkOQW+SerwLFVOg2eu+BNJTpcz4Ely'
        b'h1w95Ex4lkJG5tyKVHlgWATSA83IbSvS5EGU6iP3hVS6PBi+MUML8uR+kM6gaCI9iOwYEnPMgHnx+AJTgXDrsPIM7uJiA7628+spxjEnS8a9QU3yIZr/0+fg31l+PJAD'
        b'KHQ7oEcOXBif6ITN5KbNSYHV/c1VNZ6fx0kxoa1XQtNKz8/YJS1IbUUCAyl1WKsGt4WvhNUm8QhmA1V1XVnOxWzN3qp6nxtev5rQhB6JTYjn6FS3YNSdxjGTvSaXsRv1'
        b'8HwHhJjJjUcB7Youbfdwz/yqnRJtS0msGz/tND3xap00Pbjh4/EAD/CKFeP9iXzXNb3b3stOxE+cqeyNTzsBfJ4xkkl4MRuFNizacFCUhdWCMkpGdoNQhlGEYfe0cv5M'
        b'2RQU8RdAPo9iGXhiYV9lckZemcfQ2/pEWSvP8kNjfOFZoXQoTBk5IMadqgg4efxVZ01XFYYG+fGsZTHb7UBYKgH/2no4R/HcNYy7ruH0Ez7GN3fHtnYDqIGj2EM++t8X'
        b'DeUv3YgMIyvlCml8W06HZZj4TWUHp6Ri4sj1MRYhjVyAyQ4ECjIOm8aw6BSVNOyXyd8CeAOiDD7ZUHLEDsTs8eXejVxByYDvPxV10hGb3nHZYIn/hUbWtjdSSceWWrDA'
        b'Kq9X6cF3izxlwavPOzQp/fwmQQldwhpqFQZFisBSikiIb0RoYTfAEtwmUBt5o40YQV0P4y3Aco+ZfP7GqmZobk68uWYWhEGPXRqzeFg7fpQ2tZILJfxJ1O1wORbanm9L'
        b'S+wLK777AR7GuiLEuyLEuyIkdgWHGzoj6KxhJZunUzShI/Xo4ClQoC+OyXjpyf9IvXClF+T8a8eepJ3XE1Z+p0mJ86AwqEkEWhoRoSeFBkxQ8hAZYeHPQ9AbRAhxJwcE'
        b'fSmJ8Z0tws6ezNADSUnBjqH4kfXO4XYDUlUf8DS63cZpMZf7YU+YCoaX/8+4vIkQLkS72rI6bNn2wrufqSsSF13phfrH5spXGJ/Xmfq8wlFI8yrq8yoZeeNIktKbN/DV'
        b'bDZ5NBBYd8Jcw2j4jQYbEx73tfnjJjyPR2TUYLbp4+IS7OSeoOPYxKv6gTizhnRgCaumqyPU6nZXNzV53e4kqf0EzehYHctA6PqSDrNhkB3IQiADX4pmz9UiussjQrsH'
        b'zhk9Ojwy0WbC0HzDxRHG9QCY632BWDJi5rKnxlvFFFTRcj/QxCTKxtmAnykDcLxJin0eW9iseDAsU6oUX1ZOXjgnwf+OO4Zlm9llJ2hJ5cU7IdOykYVtEtFEPNN0IMgF'
        b'WJNUM3yUDw0JWYynmM2zrsbb4q9v9cSS8FxzA42Jtfq/xkbmQQd9/gn9+xNtCpBtIMFlOJW8cEwYXczH3hXg5c+du6gMhhc9pAR4IJwzCx0PDmxTB2iAQxEnRF6HSz2H'
        b'Agek/QEbuIJ1jA4SCdY/UO/7UFbO53CXCSFTyBw0BYVWDuh63CumHAwFJfgXsfs6Hn/L9DcAM8wI2tc4g2b2HO64BglVNqCmPlCeJWSFms1BC9RmCVpxaIOWLA5ytkJO'
        b'S8gWtCmPB3n/g0COPha0wXuxjPNJQRviLH41KPhVmVrfAN/WG9wFJgbHLXrWNADxrQJbzAl7A0jJeq8M0x2zBJrccn1NgDQh6HyAEyYAa6s6ZsOMuJH8hGcyAsjME9OH'
        b'zh57TZPPz0wQY7yM8hIoNMbXKCYsRqiRmTs9QpI/5bo9XEshd65kcH8o2IKd3P2ywAl2Po12uZk0huwUakE67wDWO0EeJRAvpr1YIMycWcDPLMg8XwuZevOk0RvlnNE+'
        b'wi6R1EYKmmEIiIvQ6U9DQ6cOQWgCR0o/vAzi9eVHHUmIZPajGYAJgc2wLS8YuktW0SoJvF1C92l2CQhw0eVMkVKkDHOGOc2SYbdKLsllYuLT/epB9SE/RqLdNk/bVrRm'
        b'jra7d3GlicuZLM1cs2ZJAVPIaB28LMFMi+L4HFP3s08KzNwI2bxkrruAqUOla4e1ZyqoRHWnej1m4TnHBkF7aLEW7iQyQjBB6lBpcRBRD6hMHLoxXx+NVas9OsKi9O0C'
        b'UFn0SR3XDm2Z9Gpn2wDWuYwrWUPs6t2CtkXdrj3dpZAJ//mXcAlkcAqFnkStdiB6gbyUgIDlmWe1FSZmD1kr6gSvGf2rQR6L7JST4Ncqu+Tk69A/Gzv4U2PO6S2Njev1'
        b'1naNM8dFmYyKgfOXTyA1+XZSkzEd4CoSA0LS3YyYKhUufrbyvE4wwGGJu4uoULZ8P6WBcyMG74tjU7QDzezZ+aQSmkRMaQeVZr4P/G/rkdijn+ZQh82uMp7v5hC1AbLC'
        b'mjIrPq98W2aHCuNZusfXdIEoYSI6Im9EU6E+z+tiQTE0DAGa2z0nofLs83obz9R99RNpKmUeyEInaqgR6gggXxkYoYFA2hwbBhMtIC9QGYETmdDg6+LqVb0ZLkwTSaNG'
        b'OFNf/oKCdoI789oxICux5FzEkOuqPz8aBSJ5/4h4XV3NoMXt9np8bvfShCHMOK9KytA9GwE7E+DquE1x9gUfk/CE6Q7vwndu9/KEGjstUcrxI3s4s9veERi/7AL1MAQP'
        b'm2w//yjBvaSU4exNjB8Nk/AyJX4+0FlwgWkdB5kmGtNqFe1mq+gUU2wA/EWC2epNvv5+bbu6pQABt3o4EAfyPNdHfVLSbtN29eweCKLBiAEEbxEbxAZphcnDNM2Q0yd5'
        b'pAYLIG96ioT9CCCtK6yMNwdAkQFJG/HY7IQzW2Np86sbPDUBcjGoj9RPZCEht0CxdAMzCKrVxudEbMvqXN9PZyAptguxj1a3Hzo/GgitMoCQMoHvjJTimmhKWFh9uujE'
        b'hWBP3IoRw1G3pQU4nQwjpHQZ9EoCsnT9KKYnTFBIDJJsYpNg5paz96b1Pl2PmN9rJgLwSshjaScC9/Esr9ErlkpQL2wn8QClSTeWecxeDsTCOqZLS5AMt0HMNYWQx5aA'
        b'rmXbThb/GPCmSHGOlQD0vBPQQEQGMy8wdDpR6Th/Z06No6zWOLo3puNGbUfVOjWrHSPDcq6Mb88EXMwpthTh9jyE5i9H52ub58wrRR26LXPnrYF9eqM5vkunqg9YBmjX'
        b'NXW/SXMTNinhJSRKBFxFt6eN9TS6b4ClaegKdW5T0+qW5g6yTJO+dNLj+04/siIwnfqUArjvGYdMJobLS4H1zR7lLry1xTl0XR6pZi/Veo0UZ4dZ+bb+F2hfKfugC3PA'
        b'2fGdeN7GwTiIIWPjABxEWbYaXdsvYZzVh9oB4RptezmvPVZcqj2OurjajtISyH/rGru2W31Ku7aT9CnOIsFy4RzniOnRi3YXz0jAIErzYPCU4ggSgVzEjNRthKN70z52'
        b'nvNnv5tG/lnQrLmmxR9oaqxv88h5XiBo80gir+TlewKKx4OOZJvaV3BB905sKft4dF5BPm7QLrq+ztekQB3tnNO8Kp+ch4Q0+tqokuV6Fhksr1AnhPILCvMY6d3RVjqh'
        b'CR2rqPJ6m9b6yaWOUoVRvdCfra/E8DCTpyPt/o7FAaVF0knx0nlzYQ8hXR5zJNRBbImfGuBuDsx9VDK06azMBRpJf8mT/3btRnWXuuVq7ZD2iHYcAJv2KKc9NkKNUEAR'
        b'9QDXrG5Rd7B34sAyH79Q3bK2084zGzvvioSdJ7cLrcy1JhKX2VaIpCllhmMQRWVWOCIlEo6JskW2Iu0g22Q70AbmBBGZdYWFDksrbTdXzKlvinlA/iiVMzt5Z4mvRzQ9'
        b'loFwigDeskcMSXH23UAgEPh61Ink6ngSUyBJISiROMtuYlDQ3wD2mcMBWSEhiyAo+n14R2kpB0pHpgT0hTEAhaAwHTUMTPCdychDDArFYOY2CLVIyklIyvEGCDEjDx2d'
        b'wDAm31i8EArZ/oyJTWN2N/Gw3chhp8MDUaYC3XMOZcwkDmGz4qmtX+dGZUsyx4gJPv+P4wxigXslw9II4DP8fWc24cJBB+MSORpHNYIUPTRjXARG89FO6ySCCQuXoBOC'
        b'xuB1MCX34gALyB/iIY2qqDB4NzDuECoC+EcQx0giXk92QAhKqCxAhCcnS9twqJcavKO9Epr7KAH6ApYWmxAARuZNMNFUwkx4bgHYvRXzsDf6cwJJaM6zSWBP1mSj0gHg'
        b'VFYAszHTYpQgxcQZPjkmVWKYeNPSKm9LZwFjHFliAkbkbclCq+HmkumACMpCnKXF8ROD70oVltx0Po+6C6RfUtJxhGuafABUAgSb/InqJsyHKhRJ3OB2XnIxkbrIAyRg'
        b'pDOm/BQnkbGqELEA0EKHl+j3rImZmhTZoyCv09/iDRBt0djOgLqQ+oOrY/uOS4ZRKUW3QH6TXbDzgoDG9+bvXaJd6IV2a/YMvq3nBfrZSQYZZ6POpPWEmxVWxJiQCKgX'
        b'6QyRMVgxrjDiy4v72Hxbg6LMt/KKFdVQ8Ck9M5SCkbZBVisgwx6Yb6u71osqID4aM4N5uhRH9lK8LP8BNOwyeP9WO5XJHACnkU7Y+ftGr6jL45VWFdo0JJjEwTWI/cgO'
        b'ksLwXkRBxX2o1g3vmLyhFXcE3olwNzsA4CgoZMKhvJEnNQ0AW/t4QnNhr8DOkJHn6UsxnmAelMDKJnYHT2BMMw2QxSSugttNa+xs5iW+1b6mtb72czWv/yB//7Pmqwb5'
        b'USBrVopwwJJp6TEopswj2o7TcVqD20KrbH5nsiKW5PahVhP6AIcCfovDSl6WeeZbOUUXY2TyZiGFb8vtOLyJn3aCTXF+Wy2XKPCkdYOoCyIxArurB1SKqS3ppn0If/AL'
        b'MjcMmoMSAfzCgMQkXA1wGCD/+l5+URzw66QOjEkVry8SZQVeaC+SjAdIdnSuD7i4JYEHZTU4zcpQTNoYbxl6lLA1u2YLV0P+z9rpARgpEZm/bMw6gXC9arESNoOtSyp9'
        b'Rbzh1IXqjhTAj0JS2qmCufD1HkOcYpUye6T0BZLdxQj2XerT2n6/eiv6g9ExVO3RedpWdF7XJ0tSn1Zv7t+lo3b8R8GH4xhJMhHkBibCIikYeAi+OR8HQdpBx0BIOQd5'
        b'l2zyUmLWuU01q2fWez2VChIGHbCQDioSczjGwmV0pj8jIMg8bUFGTQv0jsSgmci2hMUFVxMxL83EyLSgpZ7bqjMypcqz6RhaOU9u8ugxEBCtPGsZ5C9FzT+csGs4kgj7'
        b'MR/tr5ilqtqPCgkxK2kHyvVKzIJa900tgZjJ3UhxgChic8zixhyAVCfoScQkzKGs7oIox8XwXfu6chKakEaogplvSzUGqWsWKII3O5egu8ZURZH3hzaIbSkR3HYAjhBI'
        b'L+N81WTJew0PYIrn2uYEYXMBOSYq4zfiN2alchlQ2wjENpDemV4av1pSqgMWWcBRh2dWWS/PyLvGxX6HIZ0usXFfzOFToktMladTCcLVNLV4ZRryqhqKw5CHQ/XJ7jvw'
        b'34FJSwpsQPjBoNJAxUyNq2GYlQaSvs1fTAR8zORRFIBEPnzoXNTiw+z6G7/X42nWYWDMAocPFVXf7ZaOSVi7xWSYxfEuOFJTiIUpUCQYnAtU+G1Lis8CftG9jUwxxxhL'
        b'ymCZ1iasTN4Yf2UwzIVkzEWc9J0JSCV2hi0TU70/3mWT0oj3xI06n+Zt8WFDsk0JXHNscFtyvKEsxw9hWAx3lNv9nyuh7rjm6PjIAzCtj6mdgZSSsDrpZfdDU5hQHy5P'
        b'nU0tMDY1SRtgaHRja4LtktKGbfEag6M0xpt2vpmR2w2gF5mv/UxxkbKVsGyYvLSERurZOmk54/9lnI6z0wxmGqxBHB6m54kC18TBEqlFMVONtwlQQhw4QwtGcnvW1XTB'
        b'QwZAAzs4P3Ha7OfvcpYHmSIIFbs5PGhkaKo24OVqvGz8MdxdD2T6m0HNWiWX3ZXqRA6vhUXvelp7YDJ6bJqvXaue1La36nHYkxpEu3qz+kinU8Ki/5IRbpxjhAroElCk'
        b'ca4RKnqukOSUMIsiJIbNYWutmRi5NjgtUhkNS3GAUMJlg5ODeXtDOVci9VpXkBaTZi6YPrMTFIwjICiJCnA66gBnBKAMAqMVjRmEX2hbRGiQ0Fqb0iZZCJhZSj8xDEui'
        b's44F67HCEXmtg/xnkyChh2OHpMF/ZE690OVpc1WdJ+b0ewLuZqVJbqkBAsCJX7uXzli0uHx+ZcyB78iJLkAsh9utRyx3u5nSuhuD1hhoXNwLwIUmFOse2b7qM0lzFyBB'
        b'ElbbNS3ZHVtaF02cTV0MLclrrPKRy1B0TYOAYUv7+mZOZs7HLbFn8T6Mj0MJoS2NmtLhdWWHBiGTMM5b3pMwf7j/0CN7UGB8sAZBuSICRCzeoXY7EKEiEK5w8m9iuvB0'
        b'HxIBsRezONS6pqeAC+w1M40QQkV5ZVcEkErZtEnYkQvIqLTXEhTYiSbDQpK4TSLP+VKGc/6twzjGrV7O6cpjhLijZvzX2GL7oEGLZyyYkvc1DgFTlFyneGrthNHHhLXV'
        b'+hKJmQFPaG4J0CjGTHJLY7OfWf+iRiVJT2OmtajdoDNAGcSjcaZPhNpVP974W7kJZTgmQ7GbjLvNqJ5E2H0aca/y+TYHzQtrWMw22+Nt9QTqa6oUlCwyg1ScmBqDN4X/'
        b'0HQl7u4HT6kgYQiA6PM0V4jIk4o3zIOo7zQad7oH4gmQexHfRPiACchIUwaHyq7ooYOle7K0VTaHbLIlZGdshpAD1oCDlGLPhFBpxZnDhZKCNuWUkS+YBDNshVP2dtkW'
        b'SvL1obQd0o/LDnhr1G3Futc0d2xL0BkEHDWbW80p72PZsjOLy+GafwcluYKuG3mlTE4Kulp5vAu6WD1w3yfohCuWbdGhCpQpu4IWLFMWQzZohYu1gr6E96iMzurE96gc'
        b'I1uCpmBS0A6Ygq0Br44Gp5y6zQzl2ZVmzAWtNdPGTKs8jYYop3EOlpzGGf8knPne698s/sukmcQaOStOmDCBJi4mugGi8EsYYcnnxfipMcu0phalHgASX14gxEw+z1r3'
        b'OvazviCJGRLYSeHXW+/z+BmgaqxS6up9/lg6JqpaAk0E4NzVAL9Wx6z4sLbJB/iv0tTik5ls5QZcrVKNx+uNSZcuaPLHpLkzZi6JScvpvnLGpUsKktkKJ0UBiQqQyGzH'
        b'5A+sB/zZgQ1wr/LU162Collr7JjB7YXmePR7IH+hCpPigVbEzNWM2WLztTS66QummCzhPTz1rAvQ4x+M++1g6qakRj7XpNumcnp0USepp6aQwYlVJ5klnZ9HVmzoO0Xo'
        b'RXw9FlmUbTrcbs5zaNsGR30KbbqEarpky9BJto7ruL9IWtaL5PlIB82RhSiHVlgBkegsPGWtyMLZpHsiyUELFl42B/lMplopyRaEcgGTzkk1dyCsRZ2jaqXVZjubO7VK'
        b'QdPtvJFNteMYd5+8SfhbGhUHzPLZoh9j2V5SmjdwaNGgThhXXNENQRTZlblC0BfGONAtyuoMBt9krt2mbFQXNBTi3W1QImP29aUhxqaPHNeVLdlplJOdlQoH+Qtp31QC'
        b'tf0xp/Pw0EJJJmX3mAg9jbloldcDNV/T5G1SdGjOCjcoPBLrtZ/WiX6reOWDeCtV+DRgMlhZ6G6KzB1RnqDDYr1YQn5vJeGgAYqVXXy3yOA2Xgf5ylO8Xk0CJ+En+q1q'
        b'5ylsgnKGmuI8hRSLVcp2ZeSTDXP9FZP9juY1IifkaM9ou/l+2rX9UL8vjhOQ4ptYWVmJGm9iC5J/6m6xAnZljfYg2jymqZvwpR6nXET/itME7krvlOQFMGoz65Ne6Cf5'
        b'dwJmNzZlw7wlf1+cXpfx29c+frTc+tU3Kxe+dfbDVCljxtyBG/f+vmrvryrveen4/rdjS1c3jm2s23nHVV+L58TvH5jwwUtjG8O/f+Sqr5786ui/vfPZQsF21yDziv6D'
        b'/xK5/c3c4Yc91TO3nFpwIrL8cJp//KxXP0uqDh9Jdzw19/O3Lq++7XcDWj8re3TWiegzbVvefeDOUxsmDHZ9OvrDvUdSw39OXXPp2MiAp3IHXbH12BDP0rvPhDJqDj8y'
        b'4dUT5c9uq7m3x5iT72oD96+44ldN3wbvfnHc3/dEJpy5wVNmb+4z8vAjp0+8tLXkzBo+64u/P7H9ppFDei7atvP2Fwat/mLIZ/2/+PvWk1uLXnzbWt33uZvfGzRh0S2e'
        b'5XVzy19+rOiSA79YuOTfLrlstSfnt9M+7vtm+dsh5eVFW958YnvPt9/JuerR+ff8Ys1vXkweqT3Ra9a490/tOTB96bMflq+ofXfKwqWeBS/K93xdO3zH9UsjprvqzV8c'
        b'+8N1u46n3v9IpH9oxoRZ7gevavnqrZd23tA3/dkhOcqcMwse/+jRz2fkvK+OOPGu4+EJ2Zbd7xz87sB/nDj069tsvtY/DJz86hPFAybdZDp964bKy6qHej5+r+qNmjr/'
        b'0a8nHvrw8Tu2r5zz4pQX3rr4jSfKTrTM+vLl/DvCe75yvf3u71eMfN529Ibw00+8c6b5q8Z7c3656/m2O08cyyqYfeLVp3snP/pZ798N2fH3d5t75racdL39aeuhxvd+'
        b'v73P3sCL9T/7/MhrL2z+cuno1694cdpt971y1nLq05b0HnVfPP72zrm/PGtd+fr46TOyRx8e+cqYq8preu44XPrmrquv3x17/khN8qW/ueShg9z8P7313pBD34148pLP'
        b'x618PlY67suJrj3PaO+uidTNfOXQzY+ebHnx7eaPBjsPq1nvnR4+8fhv5QPnbrjkzxuLv3/of81b/+J3V9/wxmu35o6782/z21r/cM3o5/7tti/b1p94NGn91L8v+zb2'
        b'lzfrBnxffcq6OrSp6Y1vv7jp3U+Op6f9/M2r3dMyhHWvV0x65/62K4f2/FNB1Dq08j//ekvlXfu/vftt7oO7vu0b+uCtPR9eNnThCbdbrf3LvG8+//Cqk9VHli0d/ezX'
        b'H/1s6hvJ6+a9sfrwWyNzR938508OTXrpskkfJoWaLh0yqveo8d+/8/yxynv2f7h9f93qO3/xfe250J69U++v/MWoS86kb2i9uOCU6Zlr3G8X/6ryzmNthT2/u/lvmV9d'
        b'evqu3x2qmzeo9abA3K+P937sDfd/3L31m1rh488Cv8sYPXFI0Z4z/NgTg55+68umbyd/bLn8wCeXlX7/wa/LS+d/f9d1a/+3Z+U5Tiw6duaXfyxwUCRx9eRwdR+6NS1X'
        b'tw6dre3U9hdrUY5LU28Q1WPace1WsmQvXICupMdqT2hbiypLCtGS/big7hqeFcAzTrRqO+PByGdoD7I4wnow8sPjKE8fk7a9gybp/eo2Q5X0CnUj2duvo2gBKGW1zS4u'
        b'VG9fjrzNZPU50b10bWAkNnaXdlyNQAvIKrS8chUrDVPby4tL1e3MDxgT1QfH26UpQgDPhpUN+Ql1l8+rKNa2FWjXa/vX0HeJAv6rK+yc+uj6AJ4uQDffWdlZC0O7paaj'
        b'Fob6+PzAaMy/c8JsfylFZNrRom6D5iTqEnSsZ62226Y+PkvbQ4GLVsJAXeNfBV3vmrc7TbudYitB9++ersPsZZMIZP9M3Qi42E86HS54Kbjon1jY/1eXgn7sEP9Xvxh8'
        b'Km9TlaxH4USNc67KTC4PfsLfx1Jvl82F6uIi+59mA+TYIvAZaXCfLvD5CwQ+NxOF4/2LBl7cq6fLlD1ZEgQ+mx/jFfjBLZDLKpHwfGAKXvPo2qsvXtNMdIXSsm14lyLi'
        b'NcN0/r3TajzB//17YSrTSe9ddIUyBzc5EYU/J0EObG92P4HvAzmzLYC0U1l9XFb6HbwSr7mj8FpYqWhx+dr1/7P2L3RpR9NxyK7kdOMj7t627n1pINyfrR7BkI/MReP8'
        b'uer1tWpU3WHhXDlib23v3PqPgldI/sGwSKdNeqVk50vKb4al3MBnRg8u/eq1x9+/5PJVD5iKep9xPvvxLc9flL75iYsqK3cm31S34fOSHVc+N8W1/payBbsi4ZHfTvxc'
        b'uc3hnOQYNGBD/qh9O1eW+/dr71c99WrZr2pct088+vzc4Q/P/faSYQ8N/s+dzZMO7Nj5cn/fgunrPjl4zH638PIBp2nwgvd2TP3DwY2hKzceft+afuiFl7/7628WnXyz'
        b'5obVX64yf+BJW/y3gQ+cGXzp+m+uXnLtxln77HNOlZa82v/Mkn0lS9b84f1zoT/9+vWl398y5s7Y7JtXvpL/Wnrvlf/etCh6x77ob+vWf1D38YOvr77bta7kl8df6zHu'
        b'tuMv9j6w+vCp1lPPVKxZvmz2nKr7Ltm+/dCv36089Ov3Xj80+t2/Hhr9t1PbC+98wV+xfuiIhnMpb624eOWUI2suub/k50f9az9967GKrFcb3v9V6OBpvsefb3R5lDMr'
        b'yt4ccPDTyws/m/DULeeaau55veSlt46V7b38lWm7V/RZ+NKZ29tebQveO7/As7rn53UfPffXO7yX3f3Otv1l62OxrSXak7Vl7zjS2sq3h070uOczR+4fK3afLmr4OvTq'
        b'vQuOL/ty6Cff35w26uh3R8b+LnbVs+tTFw37IHvixdte+/Zvh/9YdvKq31d+/tUlt/17dOi9yceuu+Y6MavPufKJi2YPmGxe/tGNs/iL8/dttR98cN928+5V+7a5nvp0'
        b'3w7+huyqrKvefSnbctGp1O1rNi7eU7WxoPb2mmsHvb7m2orL+p36y2+3/fHA94sf+Y93vt/1SfDPtz7R446nrw4djFkyzxRMJGxiiXrrpfqi2qptKZ4D92xVLRKHr1Mj'
        b'lMfRpv5Me2QZZjPQA8ySqp4U1ZtzxpD3H9/6Mf7yDkFB1UcnaY9QBGX1iUvVHSO040XqkWIzJ2jX8lfaltNprT2UsW6wdriooqQQHU5pOyjk39YKbYuF67fYlBZUbyfc'
        b'asQw9enZUzq5Q9ddoY9QH6FIH2O0g+rDFZBJ21qgRdV7tJOAZJm55LHi6hHqXnIF5HbMXVapbQH8bBs0cjavHuVT6YXSuly9b3GFtj1f4AQfP1F7XN1FHVN3lU4smqNt'
        b'Vfc7K+abOPNkwaWF1YPUsbK2Aop+UHJ5fgnPmdcJwz3afeSSSN3mXa5tVsMV+L6gHLAPq/qcoIYv0u4NIJmfOmdxuboJsEUg1YUgP0k9NJmer0ouMhWqD2mb8Tk0bslC'
        b'Fo1Ne0C7xltRXKk+dyl55iK3XOo16h7m4P2Q+lwxDP1t5PUQvgzxM7WItjmAIhPvkumV0OX5pTyUuJmftbSAoppo18JIb4KqIoDBFc7WdqH3O8DMEBcbNMqkHcueru3V'
        b'TtLwaxud6jMOQFcrSuz52p486NnDGL81V31GUneXaftomWiPqDeoD5DbM5jKjX2K0ONZBWCmWaukEQsLqX/aA3Plq8fCBMzB1tzOzxzei0ZykbZFvXmY9mCRFhmKQbYf'
        b'5JddvZoQtaZsmM8ntd3alnKcM+FqfrK2ez55vs+rVvdXEDSck6U+DeNs5hzqtQIgxI/BwOCKWAKI4jbtMfVBdcv8+SXlOI/zTFzaxaL6kHpTX8qiPQ1Y+4EKFkt3fqV2'
        b'XQsV5NogTlfDHDV6nhmaN9TMqWHtPn4xp93nmMcm5UCStld9QgsnhMkF9HM7x3xebTfBIjwOM7dFPcA8g0jVvPqsGlbvpT4PqFCvqSgpWKPePQe+NS8WMsdqW2n19NUe'
        b'aWXruFy7bxyuHod6u6A9qEbKWNil69X96u6J2s9gWtsVbiWgNTaJ2jXr5lIhjubxFeXF5SXQiC3aPmqfS9ssVqpbp9GKr6xdoD5xcQUF2pUkXr0nH0gUHJFk7UZtx9AF'
        b'rFPzYNQLyqFo7WZRfUp91kPuunKbYDeXq4fzC4auu3xOMX5znwjL8a4QzdkA7Tpo7H1SRdHscthmuTwM8ZFVzCVsWHtIu197WLtX24J7HsgbaSGvPt2gPUur1T9+ZdEc'
        b'E6du1m7kKzjt9l61NJgj1acnwOLGpRWZCS2bC0MSFLQ92k51H81FP22Tdt1l2n70KIYRQ6UUXt2tPac9SBukXjumHuzZUDGnuHL0SJ6zaDsFs3pYC7O9eqxfqRZeFPfU'
        b'afjpzNBuoPet2qPq4TzFcJMZ95FZpz1B636hehta4qGL5+JKWKhH2A51qXvFaevV66n9w80NcY+kSeq+BO+ppaOpkKmcv3B6ot/Sdqel6h1QEdr1q3dqe70IUEpglxTC'
        b'9MB23QkwZC6OCtReoh6U+m/g5qkPWWB335lEszk/d4wDxi2qHklqxm8rcDllaHtEbb96bypB4T5TCxza9qElcypbSMAJxCogGL17Ys7RK83ll2oP0X4rVR9XryGAVzp7'
        b'nnbTPIAoDu1eQTuhPaPdz9b8LWo4mTz6bi9P0h4oLsUdeVTQjs7SbqHWTFWPqofVo6lF2va52o6K4oISmOz0PqJ2s3pCfYpaU6YeUgB+HKnADYuuZsuL5wyFCs1cMWfS'
        b'7oDJeJoCZPRSj2p36kfXNm0fkK4FQPMBsQhHU+YgSVRvAihNO3yfdqI3uoGeP1/bMQm+Qu9HDvUx2FDaJhsBuOXqHemwOKBRrWR1eY12N0DuuRYuRzsqLVf3plH/lVWD'
        b'tbu0ndAw7VEsDUP3pGpwCO4LaVEGER5O124DMHE9jTSeYlIJrx7251LP1Nu1m+uwxUP18y75KjzxsME9B0pwHGz1sSPnsLZ1ZEX5PPUm7VjhPAtnlgTrLAAaFAvweu32'
        b'aeQfGHoLGTajL2uHdj+sJG3flB+SiRl+ky/6FyCu/jUvcSEyUXsHOQSkgmDlz/+zCykmiYQe2UAtAdrO/gsSj7ldLI8uCmE0oJ1pEwp2/Q5KAFTfSmVnkEF1+5+TSqY8'
        b'ZGMjCaw8eC6Yxbaruc5/RWaesb+ZygMqgfg9gZZmt7vdHaAhPzjFJ/YUbxgJ8k33bk0pZwd9hySECBzTNvCfgms1J/MN8BddGlmKGmnRIfArwK8AvyL8ZsKvBL+XRJbW'
        b'c/BrjyxFg8NoX8zfgDn5MB9eaujQhTjUn/OKjVI0udEU4hvNIaHREkJpoUW2ea2NtpBE93avvdERMtG9w+tsTAqZ6d7pdTUmhywoiwykQOk94DcVftPhNw1++8BvOvzC'
        b'e5SqRvsFuUgy/CYHyelQ1BFEh+58NAXyZcBvGvz2gF8X/GbC7yBU8oZfS1CK9pct0SxZjGbLSdEc2RXtKSdHe8kp0d5yasgqp4Vscno0NyjKXCQHFcmjA+SMaIHcI1oq'
        b'Z0bny1nReXJ2dIGcE50l50bL5Z7RQrlXtFjuHS2S+0Tz5b7RmXJedITcLzpe7h+dKA+ITpIHRi+SB0VHyYOjo+Uh0QlyfnSyXBAdIxdGy+Si6Fi5OHqxXBIdJ5dGR8pD'
        b'o8PlYdEKeXh0qDwiOkceGV0sj4rOlkdHZ8hjolPksdES+aLoQnlcdJE8PloZsW/iogPli6NTA1lwlyqXRefKE6LT5InRJfKk6DCZj04PWuBNXkQIWoO2WhyljLArnBXu'
        b'G55XK8mT5Skwf/agPeokDZd2L7aucHI4I5wJObPDOeHccM9wH/imX3hIuDQ8NDwsPCU8IzwzPDs8J1wRXhxeEr4E1kM/eWq8PGvEFbFGCjYJUVuYxatn5Tqp5JRwajgt'
        b'3EMvvTeU3T88KDw4XBAuDBeHR4RHhkeFR4fHhMeGLwqPC48PXxwuC08ITwxPCk8OTw1Ph5rLw3PD86HOUnlavE4T1GmiOs1QH6sJyx8cLoIvZoXLax3y9HjupLBIAQOS'
        b'IF9aOF1vTV54ILRkCLRkGtRQGV5Qmy7PML4JOSKuoINqGEzfOqCWJBrPbBihXvD1APo+H74vCpeEh0N7Z1I5C8OLanPkmfHaRWirSCVJG+w4jyFnZFDEGSmMOIPOSPkm'
        b'AXU56EkxPSlmTzY4gw6yZZvFIhGQ5JDp+iPM6F6PLY9j7srRn2YLr+QG0PUI18AbWuG6f6GzPQb58wvy6pmCaVVedUu9N1DvKxCUtQiLSIyHR2S3jrPctT5iw6G62i0m'
        b'3XqYI3my8qJh3lIgAdir8wRqFTSqsHrW1ZB2DVm4o5S8qTbmNDSMSLOIRxcojQAn4c6OnrkbmxWP3w8p0dtUhybQqImmoPMRtH3kTpMaCLbrNMobT6NyzmnOUK9ukj0A'
        b'bckTBaqmx8TmpuaYHUqXPbVVaPRgrXUz8SszuWz3VBGH0DFzLZUTc9Q0uauUOgoKipFN3avXNvm86+OP7PDIxwqLOeHeH6jSvX1aIVXrrarzxyxwR4XZ6MbnD/jpLSnU'
        b'Uw2tVUp7ArV1MUXf0Y2Lnip+0oHwNVE5XpjAqmr2geLxtKIPdkygigMlTDVeT5USM3urYIKHx8Tq+jpSQ0evOCxeR8yOsabZPdP6eUmf5IBSVePByJFuN2SvdrOJtMAd'
        b'6izEJLfiqY253HK9v6ra63HXVNWsYgrGsDBk5rYNVbzPCvkFnWL34fwhdsVcZAksIhDqVaGDKXQIizoB01HuLpCtrbAJyOg1uUHDQUbXuoQ/6DAKF+eXcYU0HTdwskXb'
        b'oY2oeWY22ngS3kYsAOmcsLFysCVBHmCQUIsmGH1kisJDhhliJI+0waSgFLG3cMrGiDNkCgoRx2pBmQ33Zl8+pTjliojTwYVMEY5pj0XskTR444K+O7NwLMwRC6R7bxKC'
        b'5kgPqFHw/SwoKDvhWZ9IZi260tmFGl9QTzrUc4RyZ8PXvbA03zp43jeSSvk+jqQC3LGQ7Vp2yAo5LZEMyCnBWQFjvQkNZE4FJThBeCrP3MLdiPrAZvjKRuX2hFyG6x07'
        b'lKB/GbTBnR3vKGIRpBdzrP8RnsrYAN8mR5IchvWcGEmht0nZ6CQYKEaZCzrwXVAAeJuUxTGzLvJsamMxC+LadTSeUObdMA/2SC7ULuC4BE0ZaNSSzcYB3j9OLc4yRiJo'
        b'uNpj68X5X5ST/L/nV/8kljau6m9xtVcSeHYx3FUwDLXMgpVUgdLgL0VkQZSYchALoWQGbDebl0SX4ALMtxd+J9op4JJL6LBZUvXzhzbLW4K+WVww1QX6ZslI3CzwVsTJ'
        b'i0hwRg3rsH1w8orgG4nucOGbgpL/04gJFqM5gn+ZMOkiKuUFLcrGoIUsdKxBqI0tHtguuWWcT470jAyIDIZNkFNrQn9QsHwXhOwRVGizQ6mOoD3SEzbl27Dwkh1cDh7M'
        b'Ity78D7opG0H5QQdgCIm6wuY1PzYu6C9jFtzi88XGRhJivSU+cgA+D8Y/veN5NfykVSsJ9IXN1cGoJjwPDfCR1IiKYia1Vtoc5twEcNmSg1aoTdJsODhNwhbI+LK5kKu'
        b'SBogBPjElcXBtkkiRMEBXxVTMLF1VALck7mpGZWjQibf5/DUHCmEcpODyZFsygNAAVqcHMmjVJ6eGkipgXpqEKUG6ak+lOqjp3KNtlKqJ6V66qkBlBqgpwZTarCe6kWp'
        b'XnqqP6X666nelOqtp/pRqp+e6hsfO0zlUCoHU7XJcECUIIof5LYj6ERAAH2NDIkkQY9Tgik3Cv6DQYmuFrzSesnC9QJlwPjXop9xvTdZHNoPwpim4zqDUkVyCiHh6CMA'
        b'p+dFQQmfByUjpEi7D/HU/yt7t6D0XwB+/PfDqOFw0vo3t8MoVEsUrLr/bLPoImiVJpGxMv79XbLiW/TQmoEGl2YjGjR63nZ+KznRnBldfzmFTNEO0MvFd/v3JynNKabw'
        b'aaIV5a/fSyaniPR+B/hmGHwRfGOeMAGCAfEcserwzRzhEuCbGDHRoQ5oS8QGaD/ANaYCnugEpWtc5Z8Q34CG9B6z4RSADamIA9KpU1ajUyexUxJsEsRABADLaawjm0i7'
        b'E7ABE3QyBV1/0nMpSDmhi0kRM57QMBTJAKiSEGxjCnXbI/Ydw3gs1RFJw02Ig0VATDQBkI3YxgIiWNZZq31zolY7AEEApwDwRf0+BUohDW2MbETlcT9iUNP/e9fzEbPB'
        b'w6GVjMZPksXO9xLR6KdUxBVm77jC7ImT0YroJqCGkWREheOTIemTkU+T0QMQNNFfTG8wnYlpcsA/HVadEy2C6Z19x0AaOrSXt2STyQGmuhj41g4DDyhfxJKD1rASnDfN'
        b'QdF/t4GI81ijBGglns4m5Y8Y2BLhLJxrJjh/YLJDljY7siTIrC9N4gLc+veNsjEsJ32Rjd+veZAIdFc4BYjzjHBWrUUPqmNNqMOKUP9G7HkSPjO+ZmciYBq2WmE1a6UJ'
        b'r/HSbcgOoS+r4Ut4Bm9s8S/jbQDkdUx7GKaubHfiznzjwSCRUoHuwpBTvAn0KoFxgNDJZVMxYq2tcRs6gwcoBKqVd5G+/D3/kx19xFz1fndTda17rYLa2cpZc9yoRtKd'
        b'QNLKK+CJhP+HIo3k/CsdCa9jB6cnbKEUuDrpcEC99cEA+s3oWUjAI8Iu2ikuCyCvNqeYbcGnaRaXzuZN4wuyGVfiKiydonOI/vV+5SV89nO8/AIvLzPlafTt41deIUuB'
        b'Nm99tfIq3TZWBVYpr5FZNtx4qjDyg/I6Wb/Uy8pAKhQo9phYVQ20/qoqPxpvxyy6v6qYxW/c1Hmbqqu8/oKkf86QFSz7F+DT/8/lHxFs4Jq8HsmzGK5zQZDOF2q4TNkk'
        b'fEBBQ2ehh1X3uNH5z9nl03/8z6z/j6fNTjHNIolzR+Peq23Aa55TEof1wruyabgvBauZCEtBoH5WomXNcY5CPrgTuX5ut74jG6uaYVsGFGUzzwx6yUkBk6K8SPtuxroa'
        b'TzM6b1LQ4QjKVGqqWvwetzuW4Xb7W5qJW4isNbRcgacOd3tC+aKjx4kEy9eyxia5xetBV2fMB6kEgCVFAJSpK8nO1ZxJf94fgxG74pqH/weeEYt6'
    ))))
