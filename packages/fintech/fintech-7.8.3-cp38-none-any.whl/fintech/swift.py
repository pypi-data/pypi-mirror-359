
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
SWIFT module of the Python Fintech package.

This module defines functions to parse SWIFT messages.
"""

__all__ = ['parse_mt940', 'SWIFTParserError']

def parse_mt940(data):
    """
    Parses a SWIFT message of type MT940 or MT942.

    It returns a list of bank account statements which are represented
    as usual dictionaries. Also all SEPA fields are extracted. All
    values are converted to unicode strings.

    A dictionary has the following structure:

    - order_reference: string (Auftragssreferenz)
    - reference: string or ``None`` (Bezugsreferenz)
    - bankcode: string (Bankleitzahl)
    - account: string (Kontonummer)
    - number: string (Auszugsnummer)
    - balance_open: dict (Anfangssaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_close: dict (Endsaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_booked: dict or ``None`` (Valutensaldo gebucht)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_noted: dict or ``None`` (Valutensaldo vorgemerkt)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - sum_credits: dict or ``None`` (Summe Gutschriften / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - sum_debits: dict or ``None`` (Summe Belastungen / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - transactions: list of dictionaries (Auszugsposten)
        - description: string or ``None`` (Beschreibung)
        - valuta: date (Wertstellungsdatum)
        - date: date or ``None`` (Buchungsdatum)
        - amount: Decimal (Betrag)
        - reversal: bool (Rückbuchung)
        - booking_key: string (Buchungsschlüssel)
        - booking_text: string or ``None`` (Buchungstext)
        - reference: string (Kundenreferenz)
        - bank_reference: string or ``None`` (Bankreferenz)
        - gvcode: string (Geschäftsvorfallcode)
        - primanota: string or ``None`` (Primanoten-Nr.)
        - bankcode: string or ``None`` (Bankleitzahl)
        - account: string or ``None`` (Kontonummer)
        - iban: string or ``None`` (IBAN)
        - amount_original: dict or ``None`` (Originalbetrag in Fremdwährung)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - charges: dict or ``None`` (Gebühren)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - textkey: int or ``None`` (Textschlüssel)
        - name: list of strings (Name)
        - purpose: list of strings (Verwendungszweck)
        - sepa: dictionary of SEPA fields
        - [nn]: Unknown structured fields are added with their numeric ids.

    :param data: The SWIFT message.
    :returns: A list of dictionaries.
    """
    ...


class SWIFTParserError(Exception):
    """SWIFT parser returned an error."""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzVfAlYVEe2cN3bC9A0iICIuNDuNDs0brjhggLNprjg2jS9QEvTjfd2ixsCorKJIKDiiiiuuKAgiihq1Ywvk0kmk0kmMeQlYZKZrGYmk0kyMZmMf1VdUFDM/968773v'
        b'Pfvj2tRy6uznVNW5fASe+SfCP1H4h5+BH3qwEmSAlYye0bM7wErWIDou1osaGG6cXmyQFIEsKR+8ijVI9ZIiZjtjcDCwRQwD9NIU4JSpdPjBIEtZHrtgiSLbqrebDQqr'
        b'UWHLNCiSN9kyrRbFApPFZtBlKnK0uixthiFYJluSaeJ7x+oNRpPFwCuMdovOZrJaeIXNiodyvEHRA9PA83gaHyzTjeyDvgL/jMI/zoSEdfhRDIqZYrZYVCwulhRLix2K'
        b'HYudimXFzsXyYpdi1+JBxW7Fg4vdiz2KPYuHFHsVDy32Lh5W7FM8vHhE8UjjKEq4Y96oElAE8nw3y7aOKgLLwQk2BWz1LQIM2DZqm28qZhMm2KgUJer6cpLBP4PxjwdB'
        b'RUy5mQKUjolmR/z9h2ksEIMb7gxIM79vGQrs43GjFBWi26gclSbBYnQofhEqQRVJSlQRuzQ5SAomRovRnVHJSsbug8duWbCAj01Ae9DuBLSb2TgfyGJZ2Aw70AUd84w4'
        b'3XuRWEz4wWCO/H/4YXTvoZspEWG6WUw384RultLNbGN76N4xEN2jn6M7SqB79iKp4jLwxoJKCzxt3wxo42s5Iq9oQL6lxZ8d4iQ0XnB2XHufwfJMS4tPNC4XGssWSzY+'
        b'AG5YRdMCD4f7gHPALMPNQUne4m/cQdRXHpuYnaFtYX/0f5sxO+GOzqV1TLMDUIQOs0wb5/U78AdAm/c7/m1Q7SDG7yuQLz+78lL2JdAF7IG4Yz7aY8UCKA9Z5OeHykJi'
        b'glAZPLfELy4BVQYGxwbFJTDAMshpCmqfOS/+OT479BIdQfhMeAyMoiecZP41Tj4B+oSTzgInrUtcwQgAvAtieXntYC2wB+PGsFhYgfHfHaBGu1Fp/KKY2MDYpfDsFhCu'
        b'ThkCa5fAcrgPZEgcUD3cAy/Yh+Ap8NgkXrUalcDreAV4DqxHF2EJ7cmapFbBO6gItpKeoyALXUUddi8ypwQdhjtULrAjnPy2H+jwuON2T/wLOoM64lANPDdYAkAwCMYa'
        b'WkrxDV7kDPAAx4Kp+XI/LlaQp2KVBxiH/09O40fkxkQA017vP0t4LW5Zlx//RdqnaeuM8dpXjMHVftoY7edp7rpMozn9YVqc9jdG5eJYrTJZrb1oOMuc98j4VB+nXQWq'
        b'dTFaq6FaXHaq+Uzo3BW7RbuVIxTLIv82937iadcFVe335EdMYEnckG6fViVrI45jLDyEOpz94QnMMWWCPcgfi50FQ2Cx2HFojm04oagA1W3BTC1DlWi3CIh18Po0Bl6B'
        b'+1CFkuli/ZRKEUeE0+fBEgv3mmHkrJsNFoVR8HTBfK7JaJvVJaNuTKPX2gxkHC8noh4jZ+SMG+PI+DGctBeEUtQl2aA12w1dDhoNZ7doNF3OGo3ObNBa7DkazXPrKhmO'
        b'qAsnIQ8CZSyB70rgf+DGShmWkdGnnZCVk5cUEBPonwgrkmIDMXEVsRLghQrFwzydF+jYPlooHkC1sRt5otosdRIirNrsE9UWUdVmt4l6VDvzWdXuBdxftaWJduKsUNUG'
        b'rGE1WP19UF0QCFqxhKqWBjcWoRpsaujw5hAQAmvRbjsBIIN34HVUg8l2g0eIzhUzJuvetyQ8MYmVH33xRdrKu1WwDrZWnas5V3QlZszO9qLYI8NXMC8ZiYbJjd1mBhw4'
        b'7xhVMkvJ2Ih3hTes6wPiglBJbHyiBDhnOMMrLDqKjaSkRzADSZzyvctZEK/RbNXaqHyJngN/OSPG0uVkT2QrprLqkugN6SYbRwZxxDUp2T7yZDkSx/oIlUwPeCLUt/sJ'
        b'1Zcsgy6i7b1ipZEkcCth5PBsMdw7fop9KOFuBzydwMNTqMg2OVQM2HSATqO2GZTFTrAeFvD6BNzDANYA0Dkwi/qCoBR4gbegatwhAmwGQE1ieEYw+Eb3cF6baZtCYFkA'
        b'Oj8VHaRTpsL9ah7Wr8M9LGCteIoWHaCxaxwOb8d47CRqUeskshAsAqgFVcNK+zACsRLuQhd5dB4dIf0S3L8DoNbMdLs3XQ9VoV08Og3LODoZQ76AdkRTxyROGIda4EFU'
        b'aQ8j6GBnh1rm5tN5sDp/Bl6kBhbjPowQ9lqoFV5KokRkGVL4LAxVRWblA3QJlZjpLK+VcC+eddgNT8KEw0MA3cAOYRelA3vKAqx4LbNQJ+52wN2HAWqH1dgVEmSiUS0q'
        b'xujs38bLZXhFdI2JiFFQ3gSj+uHOJrSboxKApwG6bvOimMwYG+G8PhxdmUQ6cGQXrUUXKbQcrMAdzrBxpiycUI32M07zerrQtU3wmvNUG2qjVKOdDOOEu6iwT8DrOh7d'
        b'dEctua4EhwYmwAedp0igE55wJy9NcnJBzQTiHWby3ATaMy0enXVGTbPX21EbwD1XmPFyE4UHT8P9wTyOCSXOnI1MqmNGzYXtFPVpsCSbTxxvQ9edSU8FEzAyg9rzlGFr'
        b'+ClLXV0wE0QSZmY+rKWr+IahazxshQ2uLq4MEDkxUbB0Ou3xgU2jeXQI1rm6rCcE3WCCF7N0DYcUtNcZ1kx0yYG7xUA0lomaMF8IYzfQiZn80okcVZgcLBsF3EWnpMWE'
        b'8R6DbJMjpIA1Yo2GFbCF0pINq+fy8IoNS10i6OBVuAfVCDpYg4phOSZ0JrqCWgYRzl1iImDVUDpTNB1d5wO3obaervOMCp1Ct5QKGtTkru5MBAv8uqVutjpXn0W0MWWb'
        b'JzOVBd7dG65leSe1hAs5TthQZgYLpnYvW74ldWnEZNr4hcabicIuonvWqxu9Z3wVShvF7sOZ+SxQdG9ztaTO/96BNkbGjmRiWODWHfxrfWroifm0ccpEXyaeBaHdlrqM'
        b'1I2aibSxSjaaSWaBY7flr5a6bOBNG6eNHsMsIXhaunSpUQ8W0Mb4BeOZVILnWjdr6viKzbSRWzSBWU3w3Ga2eg/WrqCNW3L9mDSCpzItM3WY2pM2rs7yx1EBRHUrQ9Z7'
        b'h8NsIfTbA5lMgrzy5Q11UbeCaGPs0GDGzIK07k0v6+tMPvG0cenyUCaHUOQ0y+Id99d02sgnhzPYlSZ3TzNneDsvzqeNnQ4RzEZCpqlh6wNrtSttPLllMrOVBTnd0/Rp'
        b'3htXp9BGUcpUpoDQblq4MXXIaDfaeCsyktnBgphuU6ruwXCNlTZ2ZM1gSghDVkQb69ZvdRTyrOmzmN0syOx20hrrsg6Po401WVFMFeGSk97k7di1jjbenT2XqWVBavew'
        b'fCw4j620cbw6mqkjrIu15aSumWqgjZoVC5gjLNjYvWKUPnXL9cG08dDgWOY44ef4NTmpeX9U0caGeQnMWcI6wzyL95zmXCELzk5iLhDWSWqyHnC8wPnEuGSmmbBuyJlt'
        b'D7LGBNDG95gUppWwTrIts87wdys1iGGwCh7nR6EiZxmxOzkTNWgzjaPTg1CBc8Y2ztUFG+pgZiZsTBCM/toKEWrJz0LXc3kRdRQB6BC6Te1OZTBhz1mDWnjUSqy+lhkT'
        b'5aMUC7rkeZ85IsJkOidtfeCe60sb/2L/FXMcx/Du5VM2elvjN9HGnxa/zDSKsNoM7c71zukWlKFp66vMWRGmfeGhvDpnjn9xwj0VAGGbRzY1wCj5T2xfMp7NTMjKUvBs'
        b'ZjIh0U62lXl5qAmWJ+GkthKVxiYEo1KcLHotQBfSxBNVjGABSeyEhSJhM3M9bbGQ5+ZFOVpeIpvTtDR53VhXQMMHdujN7uoQNdqThHMvx1BYhHawm1AFrKFcd4VHbLAF'
        b'+0ecfjPotvcKAC8MgYeox1dFZwT4BaGLWf6oJARnKPIM0aAoHzvZbqbPw2GtBSMeCZasjkS78znCKorFvTBJcriI7p7kd6PlQuPoCIdRZYywI3t5jA0IQb12FfaK5EsV'
        b'xqcaaG14t0ASdXgBXTeqaS5cSTafalgZEgsv+jFAMTPaJnHFsfEchbABHYcHVCRdxFnTMVgL0sO9aIqyBDUtQjfyAvD+iu5d8WYrVgw8lCL89RY8ThXRHx6Yp6Jbi5Ow'
        b'hmwv5ntRZfNbiPar4FVMHCqUw3pgRvvRXjsmCIyc5qpSEclFwGMgw20LBTMZ1UxSqbAwA/A2rgGsQzXuFDcFvARLVJMJbvuiYB3Qo6YJ9hHk1zJ4aqE6jiCVKEjFNUc0'
        b'ETZPRRV+dOZoPTqmmozXn453UAeBAWcAZTReZE2EVer4xLGOaE8IqghggPNKHDFgZ6CSpajAtqWwSDUZmzeHFz8EjGvzKEB4Zck01WQp2TdF4uwhAx6Bt4TAXQULeVSO'
        b'dyUJkhmrgXgUA0+gunEUWBq6hk6pJmNzyBkBj4BMVBEhKFT7alQWgMXBufqh0kR4UQzkM0WDhqJCGoaXpnmrYBvJMRzhcWCG5Xl0lgu23rOoPB6TLcKJz3EgQp0MPIxq'
        b'ZtqTCCLtsDSEj4+NTSDnEU92ln7BSv+EYGUQK4OnDPA0Tsca/fzgOa8AJayFB3xRY4AnrPUaghqHwjMsgGWebvA4vIoum79//PjxRrV48nvCNt68daQPELab8CgsCUgM'
        b'ihHDqiQgjmLgebcopaeQ4dzIgCd5F84uwglNC3Yzx5ixYcsp5/H+rXQsanElfaXwPO5rY5RY+ZroRH2wD2oh8+BZdBH3dWLX1Smj64WOyeXxLAadgp3UcfmuRcWU97GT'
        b'YRG/3i5jcLJwHWcGHYwC3oSNgi88o57Bo7Zc1CqBJZk0RRutgfVCWgAPK3GehVpdmNQgmjaFYx04JVBwcfUiZ1dnWMniLBiIVjKr4FVYLmSm19GBdN4myxXjhBgTAG8z'
        b'I7BvaKDztuFN9xnSKfFHhzDMQozLsRBhXtEkdAC12DjUismDB/DMTmb4hDV03hR0C+3l0VWbFDDb8Gb/GE6rI3yozm1EHUOcHV1kAO5IAKIpTAxqWickPbvQFYhduX29'
        b'nMGQz+HlDjET0fZpVOuyJLDd2VXuBBaF4wSIiYX7BD5ycEcSzoM4VxYeQSeByJWZEj5agNcCC+Ed3IeuurCwCXYA0RhmzlTUSrnFwzJ0ml+P11oMqzDubcwotBN1CNpf'
        b'CMtROy/DggvEdsaiakaB9o0STKZ6LTzlTLrCFgCROxMqh3uo51vpizcMNdiWAoF2XaAd3aBIjEZ1aCcsh0WGQbL1GxggxokcrEjFVFK73D4LNlOqAqZTquxbTEFvPBTx'
        b'B7B1uUeNW1N9J/GPUfL7Xx6MZZ3/LX/Dr96/x7z7xpiG6Lkl1Xt2pV9vqUp2c3+nqepM5NHa8EknYtyS5t/z+Epe61ipejVb9dGjR4df+27cvo6CrnjNzFC3j7vDHp65'
        b'GzPBIVz/+FfBr1TYX20o9DIeqJ3v9c1n3utu5Zdtarzwy6/DIlNZe9Ub+Z9PX5kp15UvHvyrOMO0SfsTylsfvOc07DPXMxnvX/0+OelczY2hQ/aPDBpyeqsu4De/1m3c'
        b'OPjreS8VV++LWVbe+I/avIt3fTJmlr5V3nif83t9QZp7bIYp7Xe3b1wvee/iqzDm45ijbSfeaLvKG356SRrtbx6jz/jN6OXf1r/c/NNwo+/94bP3Lf/86ybdH9bsnOlw'
        b'P7j55clOX179Yt5XOmQBZgftui+XvvmXNfO3OL00/F1d83EL3/Lvu6x/3yJv/YsHW7/hkXPd2h93t0w4VeQ18a3p1l+8++bpGdqmpo/mG9/gc166ptow67YvV/co4HdL'
        b'vshY85OPL+v7cXLh+x/Lbrb8M/bEmXmf/S7axcv0WeT7+oh16z/2P/JG5fZj3TIvayczOvmUZEuz0pHu0dNy8A43MFGegd0RqgzELhc2EZ97MJAe22yZMycgODbQXxmM'
        b'O1EpAN6bIhXitegmKrMRvQiQoYonpzprIoCYHuqchO201xe1rAtA7SOCsc8rxbClcA8bBOvRURs9/2pxEqsD/WJQhZoBjmF6vPAmD95GtDNmOqteBY/GJvgnOACpmHWc'
        b'BRttJHUYmgAPbkPlZHOOIaJS7EYrRcBjuggdlsO9dC5sxB7ypjopiCRSV302MHMkC5SOzx41vOihlLy4/+nxhLtwPGHjtBZeKxyt01OKjST3mStjHBkp48nIWUdGzriy'
        b'+JuItLkzMoacUDkyMvrjzkgfi8kP64Z/6/3g76yr8J2VOUgZ9rGUlePfvFg3DE8sFdMzLi/8lOKPN4ZPvrsynBw8PfGS90Wtz7nIi6lTMpxLL30U1DzQe0Jyx7PvCYk/'
        b'SSHsxp7zkRBlHLqN3dPugMT4YEEeAVKwEF5wwG74BjyuZARX1LQc7VVnoKbYQJyn4FQMHoa34dHnklGX3pwxBtBklJywg+fP2I0uT5JT9meTUxG9UxB/m40ByxR9/iUT'
        b'AfIKbf+LEHq7sinHoEhYMi0iVGHl6Jfw4H5T+/0Sa1NwBpudsxBYZhNvIyDStZYshVans9otNgVv09oM2QaLjVfkZpp0mQotZ8BzcjgDjxsN+n7gtLzCztu1ZoXeRGWn'
        b'5UwGPlgxx8xbFVqzWZESnTxHYTQZzHqewjFsxILWYShkjLkfKHrmKYzSWS0bDBweRe5/7BaTzqo3YLw4kyWD/xna5jzFYpMiE6NGLp6MVrPZmotnEgB2HSbdEPliEEGY'
        b'h3oDp+EMRgNnsOgMkT3rKvzm2I0Y9wye7+nbrHxm5vNzsDzS0hKtFkNamsJvrmGzPeOFk4kICJlP15uLW8wGk22zNtP87OgeWT0drLZabFaLPTvbwD07FremG7i+dPAE'
        b'kYEHp2vNWkyBxppjsERSduIJFqMWM57XmvXW/uN7kMkWcJlv0JmysSpgSgmjBhqqs3OEQ5ueYrMcNWZydsuAo8lheSR9Yph2XSYexuPf7NkvwlpntvKGXrSjLfr/Ayin'
        b'W61ZBn0Pzv30ZRm2B5vBQmlQZBjSMTTb/25aLFbbf4CUDVYuA/sXLut/KTW8PVuj4wx6k40fiJYUYjeKhXYbr8vkTEZMliJE8LoKq8W86X+Uph4nYLJQKyWOQtFDmsEy'
        b'EFn01uFnqJprMGt5G53+f4OovllD5JNw1jcWPfF3OVbe9iyAHs0w8DrOlEOmvMhzE1kbTOkvwJhELpu2V7mW48iFlzKbX6BhPYs+Vcf+a71YNf/TfOcMOIpio4tUYC+D'
        b'Ry5Gt3RZ6cICA40nvggTr8ky9BFVL0KYBWZ0i+cN5p+basMB/gVM7IFDRgyM7HMRV2236A2WgSNmz7I4Rg4Qq/svjMf8HIyMDf3j7kIibdRotPHYUxlxEkO6B5qYw2EB'
        b'YJ+nHXjd5J5ugyUokQt+Efb91n4O74Hjf48iPJMD9Jv8wnxAmGvCSw88MXbunMQXq53GypkyTBaiUs/7kKSevnSqkNiAFQs4Q7Y+94W23hfyf0ChheH/SWeSqcXRZkCX'
        b't9CQjm5hsx7AJ/wPIEbMgNoZ8XP98FqCe37e2CzabMNTb9eTFyv8EnHzgHpq53JoXvTcjGUGLtdg0ROz3Jxr0GUNNJs35Ggj+ybWGECfrH6AGassljWRiqWWLIs11/I0'
        b'69b33Qdo9XrckGuyZZIk3cSRLNXAmXQKk/7nMvxIvI/VZhO3iXFakvlMWVj/iZE9+5xIvC8YKDL0H93vNoDs6LzAs7cBMUIJzq/nkyKu5HxSxDVFN084T589XQwcwQMO'
        b'RKXF/8oS1XOeXo12oULYwgI53A2mg+neqJCOhhscgBykSpwVafIb1qmAHkqtRTvzVfNhbW9xjRbW2BX4+2BYgW4EoBPeeOfaf9c62lfiM0avlNMyMngedaCdqDwkLjYI'
        b'loXEJagT0aGgOFShTpSAMFQhDVChGnreLYeXkgNwP6pDu3oHuMNjIticPMI+kh6eFcEz5EAcbocdfQ/Fp3rA7RQErByECtTxuAfdntT36PsCqqfHy1PgqRGo3A0eCEAV'
        b'CXFBLHBE7SwsM8BWOylPgZfyUKUalcHLeJVYtFuNd+aoMiQGVYiAr7sY1cVF0nGrYDM6oH46htzBlJKrj3EBU2GVZAY6OMQ+EY8zoTOwrO84uEMvXFckJjBACW9JSMHP'
        b'ZAozNBU1qPsuS+4i8KhxabAU1UiiYBtrJ5Vs8GA6LAkIRhV4zJ28pOC4BFQaqJSC4eiwGJ60owv0bggV+AYIg5JiE1BZIDoHD+NBQ4eIQ1HneAHQLnRFGTBt44Dygwfg'
        b'DeEqu8UV1alg5fBwUnd1AOjhLnhNWOIWLIZFgsSi+gvMhA5T3cmFx2GHSh8TLsFzD4NMeFtKNTAKtaETqMYBwCojCAWhqB4doiLOQsfQWXrnUQur+4kYng6nJ6gs2u9P'
        b'JTw6r4+AXdENJSsciRfmoxoVKoG18GqOFDDxWKgj0FGhUuyOA7qsQkU6eJX8dgwv1wmLaAES2o+a4F5UPjOhv2Y4oZ1KAWd0ArbNVeUEqnJEgFEDeDEellEO5a3JVsH9'
        b'ZNFmCWAWA9hqhMcF3u2LG6kibFJxeE4SgJdh4zzhHKd6JLykcoT1KnQVT1oGYBum/IxQCdGMDq9XwXqJisEgTmAkq9ExeqYcaZmogm1RKsLNk8AsH0mt9nqiFwgEmb5A'
        b'kTbDx8UD0OsVeBidQWU8A9SLQTSI3oKO0LHbODegAJ+GOuakmY+sUQKliNpNKLqBdqpnwiLM+AqBrY6ojoX7UOtaOmBdODqsDg5CO9BRfyJpeEkMBi0TmdEp1CgcXR9e'
        b'NV8dG4iFJRYzGcNgfbBJKRRJTMCaXKeKQQefMM5hNKVzIjzirILl257yDR3Mt4+hHNDAdnUKOvACKxw7BcMmVGaPjFCFwtYn7B3hLnC3yIzOqKLh3qfchQdhCYUdAwvh'
        b'rYFN1wc2SGbkjRVqcDxgswqdVD6RQRG8bJ9ACD2Lrsn7zpelP2vR8bBC0JiasdNUqAHd7BXYYFRILc93SODAlo4KUYEkaka4wNL2qUNVkXC3ihhePTaea3lCocXSQWAE'
        b'yAxzCk0LHCKPA0pPShgsFyerY4MS4TFUG4wt3q/3VHc4LBbDU7PheXpP4wbLZgeMW04KDINixcDJgYV74DnUSQ1EOV7yRIjoCKyB9bAV1lMD8fCBt9VK2PmshmxGe4Wb'
        b'r2Oz4KGAuKDgQHWQfyLazYBBGSLDStxLosA8rMP7e25qNfB0z2UtZhq5FhweL4bVY7CHJne63sPReTWpDB3wWtcmcYXHkqirwHa1G14j7ocb29/7bIUXqUfd4AOPCven'
        b'cA8JPL6wrHegv04Cm9DeAOGmsiN+iBqzrfDJ7Te5+oYN6Irg52rU7sIFsQmV978jnofKKYTo2eggWYld3M9nxWN5U+dyIxfepE5rAdzfx2uhI3rKdp02sefKk153Btmx'
        b'9R70oyfE8PYGwrgepuNIUBmCMSlXx5ObAjVhczg8II1FJ6ZTKWSiC1MxETGBkxfEJQVJgbOaxX7lInZylNDzvCO5kfXzx67u6ZXsKFguuM7tK0f1XPKSK15UGQtPwPYY'
        b'4XrvtEEc4Bfkr4M7n17y+6JqeouOFzgxsX8lwqK1pBYhTTzRhsoE4I3oDrz4RLtWbYD1ODoJV5WrR00IgK3h/XVy1wx6l45h18xwZsHUVTjXSVk4kWJjGeqJVY2H2/vq'
        b'WiI8j90C8ZM5OWg/dn3w0hji+6SwRfD+p2FZhHMuaiXVqOgcTmZQE7ou3OJdQBdgAalNhFVzQBAI0sGDAsdKpq5XT171rNLDAq1Qo5PuBNxAicopLS3w8wgZEJKIcwFp'
        b'PaqugDcGUPW4tdT/meCxNFTjhI3vgANJXYBmImyjEFaiw+hOX81FFYZ+mmuZT9GWi9B52AJvbggVEccErOhqgn0ZjVWbYAePdQpVxC5KhldDUxajElpIHhzkh+Xn33N/'
        b'nkKcREngshgiOaoZi2ICSQ92HeqlyahCjGPmljWTca63tee2vCmQZJRu0+U4o5wocQQ0F0QX0JGl/RVgFCrq0QBYuwnLhcbD5hh/jG9jTgSJzItwKECXJwg9J1ajfbBl'
        b'zNaIHIbGgkuoYYJ9EgHdiVoxI2pmw2uwJBbtxYG6FpZswI8KWAYvToaXJPBq+mJbOrw2icEaJF0BTwt1g4ttEXixyvVPQMIiWIYDHlEgCdwLL6h7yyOkcH+qhvVHBUE0'
        b'2OXDM7AYRzt4GBb3i3YTcOZDXc+dSeiiGt7IeE4vzsFjQgRqSUfHYEsObHxKag2OIIRZVljQk5qhc/yz+RvaO6zHu63W9cvfjib1pG9wR5hSLNziH/TA+cA+1DJ5PY5/'
        b'cYTCq9gh0dCzax46q8KmfzVCStM2w/Q4oWPnkAWqdNQYsQEzJQrr6jbs+mkl65mFS2EL3hgcjUDNgAbNq7AQXVUyPTUPGngStujzIsJw5wLs7mEV6rDPIc5vrIMzub3c'
        b'QsRfHoIqU1CzC7wSEZYc06uBi4OWLX5WsbBu18vQISOqpNEOtcPTdtgkxVRMAFsB9uGThIt5VDIbNmFBNkyGV1jAegF03r+nZtQV7iC1FRJSBnscbAPbMI+b7aQkefia'
        b'wTy6sZUW0C/2I7ecxAyX90NgeZAD3GcJtkfi8cuVsM45MQFVBC3rMRRUujwmbmnMEoEWeC4ZlSQEBSfGJ+n8JACeQc0y7AkPw5qeTASeWjuEFH0HrqDvGTSiE5SrQ9BN'
        b'dBbVoCvoJrwoISIDOO7U++JZ1L2chFeNWNMmPKNo6aNp3NgIq4E6Ofw5LSvp8ZtYxQ5YSY1Hmwu5pL3OoONpEbYUux/VQB9U9WzgmJP3TNzwDBW8ex1qhXU8assZJMWA'
        b'ShkQPAHHv1s0pqzxhFdoTFkD254GlZGoWMjVCnDeVkYSD1Q+a4C8Y95oWvJlOtgIRXwG/lqW/3f7ktcqPaM9L2nem/neGx3TVRcCiz76Wp376FyBX5no5aveaKnH2+Kp'
        b't0HsxJFt9z3Oxck9YrOmvvJO/Cu2D0s3hh6Z6fbasRmPJn7v4J004vvPv314tbQqMTfv26W/33L5/R/XLt88Yd1fizoDbin+MH5t9O++iLOWxdqavjldduTcH1Pfcd7H'
        b'GQNvrzdOyCpcVLNy8NrpqptXZoKmmLe5E19q7h6KOLjyvTdnfX0laXX8ooaHlxO7fJvejC37MT3wVE668cgFUVzMPx63B/gd/HjUsl+j5te3V2QE33tk87v7p+7wnMeL'
        b'3y2rHR9tfrzeacb1rE0p2qRZnt8Hy6Pf+VAV5bH0nxWq8ugZeyfrNpS+M/vuhrqjyx4krHH/oGlbSdx3km9lk5bd/fHs8Af+zLLWkO4rjX869/HwznufWFt+/9NXm53+'
        b'Xcbvbxd1v3X3W2fJnwfzDve+vXvbKfHd2QeH58zPuNf5S3NixcLYJr7y8ktvvn9kZ7FrwoG8G79ap3nlhI/Xl1//e9nBD8zX2l+VBd70GjlK9vkPrQ+B773N6MIPnmGn'
        b'Xrr3+tzC6buOnNY+dCivrzl49kdNs+vcySkHJOXfbBi8ZckvDNM7F75l6Oi4OuH6qCvfj/jb1ty3X3t19/v3bu/L+5CbVZP05nco+Z1H57dfqtV85eR/rbvrI7e3u6qy'
        b'or/Yet1r5CePNn9k8nrDKXNuUbHlH2Pu11xwOev2Q5bkp32vVf0l5chfEs5UbXKx3XS3dX3200u/nffOwzOqjR/8iXeqb8r588wlK97VnP8usKGle5/m/O5Vh665Nc3f'
        b'IAq/Nv8Wc/Ft94zfSBJef9S+4f2M12av/ynkof93ouMfpf5U9eXjZa4FIeH/vP1Q0Va5+uE3IydVhnwny/ObaLQVdPxV9+f7n9xVrjn/p8y7n9bs+mViWNiGwct2TZ8i'
        b'7hxx/7ev2iTbdr+30X79z/8I2H6nWVa/akvQ7VeGRJxN/be9t9GihumFUwpaCmKHGGdZix8FnvHwXvrGv3WmGMY1PbAf36y6r/nsLd0HeTm/ta8ear8/xa8xpParmfVb'
        b'K/4Z/uG7O8fM++Pj2MHH/POHLS95OHzR+YszV/7BUv+FeNaso/5vnlxYv/4XExft9Frzp1Ffvi6dqqsPz3WZua6tfv/CwinrH2d+M2TNoI3eb14fNnpCRrAsaBc7bfGF'
        b'Cy9tK762YPoE/fotzVMyVne8NGvTq48XbVX+bksIKFlg+kVMuNLVRjf5beiaY4BQOIINk3i/eCdsw0NhmzgGu5IbNmL/anTILQC2w7P+wUpswgA4rWDhqcUmG83uDjnD'
        b'E0+rV3DUPUkrWEj9yh54lJa/4LwTVgU8rU+pw7n5HjYItXhR+P7r16hxX/OTKhVSo+KKzttIuB2LdxpnSPEMKh0W2K945qSaIgD3ZDuRMgkN2v5ssQpqQQ10hZXYG58P'
        b'CAtMTAiMQ3sAXqGdzV0IC2mFDLo8SqrG7i8kCACpAzqQywZvRY20MAcnhbtgAU6w1Pq1T4pzBoWKMsSZNpq23to69mmegCoScJ4AWxLomltQGywO6OGYNBHuhBdY1Wp4'
        b'jL7KhTrxjqKTvrYDK+Fe4dUd+uIObNcIfL1pwalNC5YITrxyaKiCDeR1rxli0WZ0U+nxH621+RcfSpf/Opzn3jTKtk2LCKU1PFGkJiUfpDoy4p6PjNbrkI+YYRk5407q'
        b'cPD/MpZlBvx8I3N1pHU+jow3rd0hY73x/64/SSUypu9HgOIqzHsRPOHzhXSoK6NgSDWQmHFjvEVujCutMBIzI/DTE0NxY90eyxgpI9QTiWntEF6XlbMEG3dhdVZG18Q/'
        b'LKk+krL4w4zBLVKCjYATnitlhWolGYbuzXjifh8Ml8wg1Uyu/5SKBQpc2d7aJjfWlaUwWG4Q5mFibzGSmJwv9ylC+q/LT8lwbr0SpGtVE8mRJlAAvhrXt1yJZK42WAPP'
        b'9hQsocogkuNJowHwyRHh7K0QHXzupTqiAlEEJEmRDOTdbbCS1TMrRXpWqHbvcqMn5bSKiIvmOCv3g69wdk7ViespCjLoFVqLwkD6gxOV4i5HjYZcNmg0XTKNRnhJG3+X'
        b'azTr7VpzT4+DRqO36jQaQUefPiitZJdYibGj5WaOLD2jQJV+sMPZFV23OTsRGoO4IFgtEl7BDEH1UgkqhnVKZoHJ1D6d5X3w7Ni8xpmV7Yko2S36g7+1eEx3fuejHZMe'
        b'/tg5r+rT74Fs7oEPX/Lcu7ggYJyP+bOZY//q8Cg1Rfuw4LcR/F9GvHr0EfdB8en0r/fO3/Pmu4ovrtwc8/t159+94zP9b/HDJx7iGr7/hEuY8/7QG38/eIAb+22kfPza'
        b'cbP/VOOd2/jSy983RI+uPvhj4P2d9z7YNe7yzDWvX4ta1OjZUfph4ietQ1NfSS69/YvTcRWRLodaMz96o+HXgfwrLXfHqL9JNe5c+lZqRlFC2wNj8ZrvHnxSMG/PhNvz'
        b'uVeczhxZP+uKh1qdfardsMZlRPCNeH5kyhTJG+G/jHj0+ap1e39TfrM2XPVZXty7Xa+7vPfmtuSPDx1+8Oq2R26n/6m4ccrX+YeGsiXjPAo3er7/60HGuGVLpYuUYhvd'
        b'1rVtIce46DYTj7cbUwHOwisybUSVUAeqQ53OT99zhcfhud53XYPQORs90upEB7Kc/bHvJU4fj3NEzYI8fGGLGF0enEBjHNqHCuF5Hl6MSQzyWwQP90aIwahKBJtHwwqs'
        b'5lTb3f8bnamUprkvflAnifXWbNXqNRrqIXOIiXgRbxXBjHrMsqQSEftE1s3RzQHvdIQP8y99eySV93i7H6WOnknE2/rlg60sww3tNQRsfCy2jqfuZPB/D2MYzvuJ2ZHF'
        b'SUAW6iEfBvd1MOSojcf7z9uwnByX5KEGVJoUD0thpQNwHSYaKQ8wZQTzYt6Ax93p9h15P8x1e5TbrtfzjbkutvSduz5tuAV3rPvS74rq0YNV3QlhnZ/v3Hn+/ZXX3v1Q'
        b'kxWQ3vnoGMzPTUltPKQ59Vn+71PUjmNTPv10mirn3rB2bmzY+k/CBu09ufWm8fDM37/m8MvfeLfVfq50oOkJPJcYTV9eTaJbJwc5OoID+VUWnVUqaS1tHNoLL6mTgvAm'
        b'Dw9KCmKx4t0CJhHeQO1HLXQIvD4/RiALVcMOcsIGKyhd7qJRzEqaaKBmWBGi7q3URUeXso7wIKqmuQSskMJW9dM/sIAKVwBnJYuqsOa30xFGuBsd6PMnGBxQhfA3GNB1'
        b'VGejrzFvz1cFxEnICfwCvCWty3LvtYpR/815xr+qOOKftSOTxWTrsSNyrgFcHHurgkWB+YB8ADfsia4rukRmg6VLTIpSuyQ2e47Z0CUmt684qJp0+EkKC7tEvI3rkqRv'
        b'shn4LjGpTekSmSy2Lgl9fbpLwmktGXi2yZJjt3WJdJlcl8jK6bukRpPZZsC/ZGtzukSbTTldEi2vM5m6RJmGjXgIBi8z8SYLbyPVaF3SHHu62aTrctDqdIYcG98lpwuG'
        b'C7ffXS5CHmXirVMnh4Z1OfOZJqNNQ0Nfl4vdosvUmnA41Bg26rqcNBoeh8ccHOykdoudN+ifWrNA9iiOvFfEhZEH+YsSHPGqHPGZHLnO5cgdJUcUlFOSBzl/54LIg9x0'
        b'cOQokgshD5Lic0TPOHImzZE32TmSwnLkpIEjrzpx5P0sjoRRjrxmxSnIg5gPR7JsjpzkcVPII+CJMyDScXriDB4t6OMMaN8Pjr1/q6DLTaPp+d7jP3/wMfb/iy0Ki9Wm'
        b'IH0GfaLSkSNOhmQAWrMZ+ziqB+SQqUuGhcDZeHLB3yU1W3VaM+b/YrvFZso20PSDm9bLvGdShi7HGUKiMYskNTShEZOKekHX3Dwx1o7M/wPq0l6t'
    ))))
