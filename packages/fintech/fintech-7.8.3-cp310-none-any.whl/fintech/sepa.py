
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
SEPA module of the Python Fintech package.

This module defines functions and classes to work with SEPA.
"""

__all__ = ['Account', 'Amount', 'SEPATransaction', 'SEPACreditTransfer', 'SEPADirectDebit', 'CAMTDocument', 'Mandate', 'MandateManager']

class Account:
    """Account class"""

    def __init__(self, iban, name, country=None, city=None, postcode=None, street=None):
        """
        Initializes the account instance.

        :param iban: Either the IBAN or a 2-tuple in the form of
            either (IBAN, BIC) or (ACCOUNT_NUMBER, BANK_CODE).
            The latter will be converted to the corresponding
            IBAN automatically. An IBAN is checked for validity.
        :param name: The name of the account holder.
        :param country: The country (ISO-3166 ALPHA 2) of the account
            holder (optional).
        :param city: The city of the account holder (optional).
        :param postcode: The postcode of the account holder (optional).
        :param street: The street of the account holder (optional).
        """
        ...

    @property
    def iban(self):
        """The IBAN of this account (read-only)."""
        ...

    @property
    def bic(self):
        """The BIC of this account (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def country(self):
        """The country of the account holder (read-only)."""
        ...

    @property
    def city(self):
        """The city of the account holder (read-only)."""
        ...

    @property
    def postcode(self):
        """The postcode of the account holder (read-only)."""
        ...

    @property
    def street(self):
        """The street of the account holder (read-only)."""
        ...

    @property
    def address(self):
        """Tuple of unstructured address lines (read-only)."""
        ...

    def is_sepa(self):
        """
        Checks if this account seems to be valid
        within the Single Euro Payments Area.
        (added in v6.2.0)
        """
        ...

    def set_ultimate_name(self, name):
        """
        Sets the ultimate name used for SEPA transactions and by
        the :class:`MandateManager`.
        """
        ...

    @property
    def ultimate_name(self):
        """The ultimate name used for SEPA transactions."""
        ...

    def set_originator_id(self, cid=None, cuc=None):
        """
        Sets the originator id of the account holder (new in v6.1.1).

        :param cid: The SEPA creditor id. Required for direct debits
            and in some countries also for credit transfers.
        :param cuc: The CBI unique code (only required in Italy).
        """
        ...

    @property
    def cid(self):
        """The creditor id of the account holder (readonly)."""
        ...

    @property
    def cuc(self):
        """The CBI unique code (CUC) of the account holder (readonly)."""
        ...

    def set_mandate(self, mref, signed, recurrent=False):
        """
        Sets the SEPA mandate for this account.

        :param mref: The mandate reference.
        :param signed: The date of signature. Can be a date object
            or an ISO8601 formatted string.
        :param recurrent: Flag whether this is a recurrent mandate
            or not.
        :returns: A :class:`Mandate` object.
        """
        ...

    @property
    def mandate(self):
        """The assigned mandate (read-only)."""
        ...


class Amount:
    """
    The Amount class with an integrated currency converter.

    Arithmetic operations can be performed directly on this object.
    """

    default_currency = 'EUR'

    exchange_rates = {}

    implicit_conversion = False

    def __init__(self, value, currency=None):
        """
        Initializes the Amount instance.

        :param value: The amount value.
        :param currency: An ISO-4217 currency code. If not specified,
            it is set to the value of the class attribute
            :attr:`default_currency` which is initially set to EUR.
        """
        ...

    @property
    def value(self):
        """The amount value of type ``decimal.Decimal``."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code."""
        ...

    @property
    def decimals(self):
        """The number of decimal places (at least 2). Use the built-in ``round`` to adjust the decimal places."""
        ...

    @classmethod
    def update_exchange_rates(cls):
        """
        Updates the exchange rates based on the data provided by the
        European Central Bank and stores it in the class attribute
        :attr:`exchange_rates`. Usually it is not required to call
        this method directly, since it is called automatically by the
        method :func:`convert`.

        :returns: A boolean flag whether updated exchange rates
            were available or not.
        """
        ...

    def convert(self, currency):
        """
        Converts the amount to another currency on the bases of the
        current exchange rates provided by the European Central Bank.
        The exchange rates are automatically updated once a day and
        cached in memory for further usage.

        :param currency: The ISO-4217 code of the target currency.
        :returns: An :class:`Amount` object in the requested currency.
        """
        ...


class SEPATransaction:
    """
    The SEPATransaction class

    This class cannot be instantiated directly. An instance is returned
    by the method :func:`add_transaction` of a SEPA document instance
    or by the iterator of a :class:`CAMTDocument` instance.

    If it is a batch of other transactions, the instance can be treated
    as an iterable over all underlying transactions.
    """

    @property
    def bank_reference(self):
        """The bank reference, used to uniquely identify a transaction."""
        ...

    @property
    def iban(self):
        """The IBAN of the remote account (IBAN)."""
        ...

    @property
    def bic(self):
        """The BIC of the remote account (BIC)."""
        ...

    @property
    def name(self):
        """The name of the remote account holder."""
        ...

    @property
    def country(self):
        """The country of the remote account holder."""
        ...

    @property
    def address(self):
        """A tuple subclass which holds the address of the remote account holder. The tuple values represent the unstructured address. Structured fields can be accessed by the attributes *country*, *city*, *postcode* and *street*."""
        ...

    @property
    def ultimate_name(self):
        """The ultimate name of the remote account (ABWA/ABWE)."""
        ...

    @property
    def originator_id(self):
        """The creditor or debtor id of the remote account (CRED/DEBT)."""
        ...

    @property
    def amount(self):
        """The transaction amount of type :class:`Amount`. Debits are always signed negative."""
        ...

    @property
    def purpose(self):
        """A tuple of the transaction purpose (SVWZ)."""
        ...

    @property
    def date(self):
        """The booking date or appointed due date."""
        ...

    @property
    def valuta(self):
        """The value date."""
        ...

    @property
    def msgid(self):
        """The message id of the physical PAIN file."""
        ...

    @property
    def kref(self):
        """The id of the logical PAIN file (KREF)."""
        ...

    @property
    def eref(self):
        """The end-to-end reference (EREF)."""
        ...

    @property
    def mref(self):
        """The mandate reference (MREF)."""
        ...

    @property
    def purpose_code(self):
        """The external purpose code (PURP)."""
        ...

    @property
    def cheque(self):
        """The cheque number."""
        ...

    @property
    def info(self):
        """The transaction information (BOOKINGTEXT)."""
        ...

    @property
    def classification(self):
        """The transaction classification. For German banks it is a tuple in the form of (SWIFTCODE, GVC, PRIMANOTA, TEXTKEY), for French banks a tuple in the form of (DOMAINCODE, FAMILYCODE, SUBFAMILYCODE, TRANSACTIONCODE), otherwise a plain string."""
        ...

    @property
    def return_info(self):
        """A tuple of return code and reason."""
        ...

    @property
    def status(self):
        """The transaction status. A value of INFO, PDNG or BOOK."""
        ...

    @property
    def reversal(self):
        """The reversal indicator."""
        ...

    @property
    def batch(self):
        """Flag which indicates a batch transaction."""
        ...

    @property
    def camt_reference(self):
        """The reference to a CAMT file."""
        ...

    def get_account(self):
        """Returns an :class:`Account` instance of the remote account."""
        ...


class SEPACreditTransfer:
    """SEPACreditTransfer class"""

    def __init__(self, account, type='NORM', cutoff=14, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA credit transfer instance.

        Supported pain schemes:

        - pain.001.003.03 (DE)
        - pain.001.001.03
        - pain.001.001.09 (*since v7.6*)
        - pain.001.001.03.ch.02 (CH)
        - pain.001.001.09.ch.03 (CH, *since v7.6*)
        - CBIPaymentRequest.00.04.00 (IT)
        - CBIPaymentRequest.00.04.01 (IT)
        - CBICrossBorderPaymentRequestLogMsg.00.01.01 (IT, *since v7.6*)

        :param account: The local debtor account.
        :param type: The credit transfer priority type (*NORM*, *HIGH*,
            *URGP*, *INST* or *SDVA*). (new in v6.2.0: *INST*,
            new in v7.0.0: *URGP*, new in v7.6.0: *SDVA*)
        :param cutoff: The cut-off time of the debtor's bank.
        :param batch: Flag whether SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.001.001.03* for
            SEPA payments and *pain.001.001.09* for payments in
            currencies other than EUR.
            In Switzerland it is set to *pain.001.001.03.ch.02*,
            in Italy to *CBIPaymentRequest.00.04.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The credit transfer priority type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None, charges='SHAR'):
        """
        Adds a transaction to the SEPACreditTransfer document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote creditor account.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays and
            the given cut-off time). If it is a date object or an
            ISO8601 formatted string, this date is used without
            further validation.
        :param charges: Specifies which party will bear the charges
            associated with the processing of an international
            transaction. Not applicable for SEPA transactions.
            Can be a value of SHAR (SHA), DEBT (OUR) or CRED (BEN).
            *(new in v7.6)*

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPACreditTransfer document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class SEPADirectDebit:
    """SEPADirectDebit class"""

    def __init__(self, account, type='CORE', cutoff=36, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA direct debit instance.

        Supported pain schemes:

        - pain.008.003.02 (DE)
        - pain.008.001.02
        - pain.008.001.08 (*since v7.6*)
        - pain.008.001.02.ch.01 (CH)
        - CBISDDReqLogMsg.00.01.00 (IT)
        - CBISDDReqLogMsg.00.01.01 (IT)

        :param account: The local creditor account with an appointed
            creditor id.
        :param type: The direct debit type (*CORE* or *B2B*).
        :param cutoff: The cut-off time of the creditor's bank.
        :param batch: Flag if SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.008.001.02*.
            In Switzerland it is set to *pain.008.001.02.ch.01*,
            in Italy to *CBISDDReqLogMsg.00.01.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The direct debit type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None):
        """
        Adds a transaction to the SEPADirectDebit document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote debtor account with a valid mandate.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays, the
            lead time and the given cut-off time). If it is a date object
            or an ISO8601 formatted string, this date is used without
            further validation.

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPADirectDebit document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class CAMTDocument:
    """
    The CAMTDocument class is used to parse CAMT52, CAMT53 or CAMT54
    documents. An instance can be treated as an iterable over its
    transactions, each represented as an instance of type
    :class:`SEPATransaction`.

    Note: If orders were submitted in batch mode, there are three
    methods to resolve the underlying transactions. Either (A) directly
    within the CAMT52/CAMT53 document, (B) within a separate CAMT54
    document or (C) by a reference to the originally transfered PAIN
    message. The applied method depends on the bank (method B is most
    commonly used).
    """

    def __init__(self, xml, camt54=None):
        """
        Initializes the CAMTDocument instance.

        :param xml: The XML string of a CAMT document to be parsed
            (either CAMT52, CAMT53 or CAMT54).
        :param camt54: In case `xml` is a CAMT52 or CAMT53 document, an
            additional CAMT54 document or a sequence of such documents
            can be passed which are automatically merged with the
            corresponding batch transactions.
        """
        ...

    @property
    def type(self):
        """The CAMT type, eg. *camt.053.001.02* (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id (read-only)."""
        ...

    @property
    def created(self):
        """The date of creation (read-only)."""
        ...

    @property
    def reference_id(self):
        """A unique reference number (read-only)."""
        ...

    @property
    def sequence_id(self):
        """The statement sequence number (read-only)."""
        ...

    @property
    def info(self):
        """Some info text about the document (read-only)."""
        ...

    @property
    def iban(self):
        """The local IBAN (read-only)."""
        ...

    @property
    def bic(self):
        """The local BIC (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def currency(self):
        """The currency of the account (read-only)."""
        ...

    @property
    def date_from(self):
        """The start date (read-only)."""
        ...

    @property
    def date_to(self):
        """The end date (read-only)."""
        ...

    @property
    def balance_open(self):
        """The opening balance of type :class:`Amount` (read-only)."""
        ...

    @property
    def balance_close(self):
        """The closing balance of type :class:`Amount` (read-only)."""
        ...


class Mandate:
    """SEPA mandate class."""

    def __init__(self, path):
        """
        Initializes the SEPA mandate instance.

        :param path: The path to a SEPA PDF file.
        """
        ...

    @property
    def mref(self):
        """The mandate reference (read-only)."""
        ...

    @property
    def signed(self):
        """The date of signature (read-only)."""
        ...

    @property
    def b2b(self):
        """Flag if it is a B2B mandate (read-only)."""
        ...

    @property
    def cid(self):
        """The creditor id (read-only)."""
        ...

    @property
    def created(self):
        """The creation date (read-only)."""
        ...

    @property
    def modified(self):
        """The last modification date (read-only)."""
        ...

    @property
    def executed(self):
        """The last execution date (read-only)."""
        ...

    @property
    def closed(self):
        """Flag if the mandate is closed (read-only)."""
        ...

    @property
    def debtor(self):
        """The debtor account (read-only)."""
        ...

    @property
    def creditor(self):
        """The creditor account (read-only)."""
        ...

    @property
    def pdf_path(self):
        """The path to the PDF file (read-only)."""
        ...

    @property
    def recurrent(self):
        """Flag whether this mandate is recurrent or not."""
        ...

    def is_valid(self):
        """Checks if this SEPA mandate is still valid."""
        ...


class MandateManager:
    """
    A MandateManager manages all SEPA mandates that are required
    for SEPA direct debit transactions.

    It stores all mandates as PDF files in a given directory.

    .. warning::

        The MandateManager is still BETA. Don't use for production!
    """

    def __init__(self, path, account):
        """
        Initializes the mandate manager instance.

        :param path: The path to a directory where all mandates
            are stored. If it does not exist it will be created.
        :param account: The creditor account with the full address
            and an appointed creditor id.
        """
        ...

    @property
    def path(self):
        """The path where all mandates are stored (read-only)."""
        ...

    @property
    def account(self):
        """The creditor account (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def get_mandate(self, mref):
        """
        Get a stored SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Mandate` object.
        """
        ...

    def get_account(self, mref):
        """
        Get the debtor account of a SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Account` object.
        """
        ...

    def get_pdf(self, mref, save_as=None):
        """
        Get the PDF document of a SEPA mandate.

        All SEPA meta data is removed from the PDF.

        :param mref: The mandate reference.
        :param save_as: If given, it must be the destination path
            where the PDF file is saved.
        :returns: The raw PDF data.
        """
        ...

    def add_mandate(self, account, mref=None, signature=None, recurrent=True, b2b=False, lang=None):
        """
        Adds a new SEPA mandate and creates the corresponding PDF file.
        If :attr:`scl_check` is set to ``True``, it is verified that
        a direct debit transaction can be routed to the target bank.

        :param account: The debtor account with the full address.
        :param mref: The mandate reference. If not specified, a new
            reference number will be created.
        :param signature: The signature which must be the full name
            of the account holder. If given, the mandate is marked
            as signed. Otherwise the method :func:`sign_mandate`
            must be called before the mandate can be used for a
            direct debit.
        :param recurrent: Flag if it is a recurrent mandate or not.
        :param b2b: Flag if it is a B2B mandate or not.
        :param lang: ISO 639-1 language code of the mandate to create.
            Defaults to the language of the account holder's country.
        :returns: The created or passed mandate reference.
        """
        ...

    def sign_mandate(self, document, mref=None, signed=None):
        """
        Updates a SEPA mandate with a signed document.

        :param document: The path to the signed document, which can
            be an image or PDF file.
        :param mref: The mandate reference. If not specified and
            *document* points to an image, the image is scanned for
            a Code39 barcode which represents the mandate reference.
        :param signed: The date of signature. If not specified, the
            current date is used.
        :returns: The mandate reference.
        """
        ...

    def update_mandate(self, mref, executed=None, closed=None):
        """
        Updates the SEPA meta data of a mandate.

        :param mref: The mandate reference.
        :param executed: The last execution date. Can be a date
            object or an ISO8601 formatted string.
        :param closed: Flag if this mandate is closed.
        """
        ...

    def archive_mandates(self, zipfile):
        """
        Archives all closed SEPA mandates.

        Currently not implemented!

        :param zipfile: The path to a zip file.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJy0fQlAVMf5+Lz39uJaEAHxXm8WlgXRqPEEUeQGAS807i68BVYXFvfwCt4HKKJ4a9R4xNtoPOOt6UybpFeaNr9ffu02bZoeadK0Te+mNo3/b+a9XRZYUNv+RYY3782b'
        b'+Wbmm++ab773C9ThnwC/6fDrmgiJiMpRNSrnRE7kN6Jy3iocU4jCcc4ZLSqsyg1oKXL1ms9bVaJyA7ees6qt/AaOQ6KqFIVU6dWPFoWWTi/O0NU6RI/dqnNU6dw1Vl3x'
        b'CneNo06XZatzWytrdPWWysWWaqsxNLSsxubylRWtVbY6q0tX5amrdNscdS6dpU7UVdotLhfcdTt0yxzOxbplNneNjjZhDK0cEdCHRPhNgN8w2o/1kDSiRq6RbxQaFY3K'
        b'RlWjulHTGNIY2hjWGN4Y0ahtjGyMauzRGN3YszGmMbYxrrFXY3xj78Y+jX0b+zX2bxzQOLBR1ziocXDjkMahjcMahzeOqEpgI6JZldCk2IBW6VeGNCRsQHNQg34D4tDq'
        b'hNX60oDrZXQ0hMLKwGHm4DcNfntSEBVsqEuRPrLQroFrVZiA3hXpldlgGFWGPMPgMgrvJIdIM9lSlD+TNJGWIj3ZbiUtObOKk1VoxHQFeUiOVusFTz8oS07hXfhaXo4h'
        b'Jxm3TCZbyLYCJdKSrUKhKtwTSwu8ho/gQ7SAEikUnLECHy0e7RkAT/DeXEUSe6Mgh7Toc16wKVA02S3gO3gzeaDnPX2gUN9e+EZe2igokEe2F+WMSVKiyEHChESy3dMX'
        b'Hi+KJKfp45wC+hTfiaCNXxJGlpADcgU1NVoe33XRAtAS2cah0BweX15EmjzDKRBnxpATYeRqJNmMb5MbLryF3Kwn15fg5sgIhPoNUajJJtys5zy9oXBcFNlDmvNzyTYB'
        b'CeQBR67gK/gQOZILzxkm4FZ8IQ9fTMhJJlvzyDa8Be8ne4sYaC0phcl6FZoxXd1A7syCFyhwy6Cv18g1ACwfv2IrUiJlA0dOkvXkklyAHCOH8H2yC99Jyk02FCQbORQe'
        b'K4Qm4ENQgI5/Hr5VQq6uTso2JJIt+bR7YaSVJ5fwHbKvkuuw2kb50OAAxdT2eIr+U0xtTGjUNyY2JjUaGpMbjY0pjamNIxvTqkbJ+Ms1hQD+8oC/HMNfnuEst5ovDbgG'
        b'/N3YEX8p4H074e9CCX/P16lROGBsquqtJWMGTELs5g9jBUQLpsa95C5dppRuHu2jQVFwLzXrf8a/q1st3YwZq0DwV5c6/JuL3pgbic4heyjcttX3VozO/RTWwkcj/sS/'
        b'PlKo0CF7CDy4MfHgvEe8ORKlm9M+SFsUHS7dLpv+p75fDkwYyBf/jPsq/p+l1ciLPEnwoKK+FNZRc8rMhASyNSUbsAKfKyEHyxJyC8gOgzEnObeAQ3WRIZMK+nim0ele'
        b'Sx4qXG7n0iUeF7lJLpPr5Cp5nVwhN8jddHItUhMeqg2JCMM7cBPelpY6Om3MyOdG4Zv4sgLhB/NDyEVyWvTkQEVVZC0+m5efW5hTkEd2wCLeRrbCAthCWgCaBEOiUZ+c'
        b'hF/DZ/GrJfD6VbKf7CR7SSvZR3aTPXMQ6mXAl1Mjot3x7XCIDqoafnvRqRjno3ZClSDPMd8EM7lKgDnm2RwLbF751UJpwDXMcXUwGqXoNMeKQiedfFvRqz/gXM/D1Xv3'
        b'CvIsC95492uXW6/sG6R8+7xl7hu3ot6e/8b11uP7jm+wcS51ZQSZenrwW4a41uxUoXo8yq2N6JvyW73SzVZTI3k9DCZkKwwJLGHFRLLjeQ6W8JlCN+2Svl9mkhHGakvm'
        b'DAOHVHg7n4wvka3uOHjWv9/zSckJ2eQh3pTMw7OX+OQp5ICbIia+Qc7hHUnJpCUfyMONkUqkKudgKprJDjelgCbeTZqz8UWE+OfxllVcFgz7BT3n5RP0esFJexuQ8JA8'
        b'ip1Y5XSstNbpqiTWZXRZ6y2TvYLHJtLnLhUkoZnRXDTnVPle0iu8IXWWWqsL2JzVq7A4q11etcnk9NSZTN4wk6nSbrXUeepNJj3f1hxc02XgpJPqVNKE1kcx0RVDGcED'
        b'Fc9zKo6mCk71FU0ZUcdH8akeSdBhDvH4AEf2zcmcbMmq5IPgCpvS8RRXeIYtiiqFH1uEp8KWThyNIkVoJ2zpWSiBdnkV3urKh87ArNxMBAI/A7/mob0xlJJLefCA0+Nz'
        b'BooLW/Bd9sqwSnKeXAPqyyk1+C6dzxvkslTZNj1uIs300XQrfgWRvdFkh6cnW6mZhjBgdVyPVHIe4bsD8G7WSEVf3JpE78/ELeQ1BHz09Tz2AG8lG2qSjCrEzce78VpE'
        b'zgxKlQEOw2fI7plwuZJsJhdRwWxy29MDsprFwD52q5CVnEAGZCiboQ/xRMP9wfg8Pj6BR8NzENkE/6sRAymFHB/4Ig/g46PAluH/1Ex2v86zGN9VUVDuIrIf/s8N9VCU'
        b'XoS34fOEPrmIWxG5Cf/xzucZsOTIcNKK7wqI3I+GDPwvSpeAXYtPzCPwQJUOz+A/2YmPsifj8HayDt+NRHi/A9gW/A/FNxm4oXhPKnmFR3MtICaFAb+7w27jewPJlVIB'
        b'rcD70Qg0YiqWbtvJ/SyyWw1V4yMoFaVmRTNgtTAPO4E47QecAvJ3XYVMmeQQezQDqNYBcs1Fri0tHQcISc5yQ+dPZqSjHfXiA4kMJQfVqAG9AJypgWsC+dLJN3A7+SU8'
        b'lSjZimLJOd7LG1O9XOU5rm2BsqXiDZ1ot7nclY7a+slzaZX0STzyTKHjdwGEnl15stDCeH822QNd3wJCVSEBrHpdSEvDzfhEeh7eBbCHkVdhQMidMHyZ3J5g++nOXyDX'
        b'FlpfxPPPtUzQ4tSoacve4n4eNXnssdM/i7udUf5J1qOov0Rt+dalpq9/rI35W8HXMtyjiopGbT6e9pepwz6Zu+Rrw+a8+umP7q2Kydxl6Jn/+Vu7br8zft3FjwaNmvm6'
        b'afOUvtqM6Ktup+2dpj4zDx/jvnH7yHeGvdXy3ZYfl93/5fkPlkx5f3Phy+Xvrzl6/4s/Cgt3JJS5HwIFpSQSv1o7O8moJ1sN5EEKiI/4VX4UPtrDTaWjQrxVBCmFNOXk'
        b'Fyphoq+MNvHkCD7S101RKto6jzQbQI5LLg5XIdVCfkhlolsHD8IACS8yLkm2gnwGq/LVXHxzuRL1HC2QXaNjWN34Vr/RPsK9HJ8E2k0JdwU50omC6hUdSWqHaQuz1lU6'
        b'RKuJ0lRGTQdTvMhWcBr4AWr3lUZQcKFwHc5pHkcJWvgbDzlnVACl5Vze0DqHyQVaQo3V5aQygJNSpM7Q8E6K1M4efgJLq8nxEdjo20EI7CCKQFdXg0B6GO9uj0MK1Ifs'
        b'Uiwj+xOfQGsZX25Ha/+rnDlEkr4e50bH1AnZcGVueH95nSRTfXdsdvoPeB2HzObc+B5VKEtSNGp6RPXk0xGqNxu295gqFf3+wNDVWRzoT1Fm++Pec5FEKF8iZ/C+UakK'
        b'tFSL8G5UIZALtl+qv+Rd8+gibr39mfk35pqqfMt3qhI+/nTt5YNX5239ouTAht7j4+NSV08wiJ+In5gNu1RXe0+I75UWl5cplswtiS8/ODTDsDlmdlTeYSoq3FaJ/Pwx'
        b'pUxEiB4WO/LwJ3qe8XmyZ1U9ZfSUySvxPcrnh5Fj7v4UsCvp1UnGHIOZ7EjUG0F+I7BC43WKheQsvqPnng77elTWWCsXmyqdVtHmdjhNMkfX0rVeTnFQCygQDzjn7BmA'
        b'b0KlTfSqKx2eOrdzRffoRofQGetHN1rLfD+6nQmCbsm0axsHYIpn2aAl4e1FRhBPt0D3UoDPnwXGtQP4/CR8SEVOk6OktZNa4Uc9JhJygHxtIiHHEO/JYn8nxKPQazoh'
        b'3jQJ8Q7M7ImGgjAfI5gnNtSslHEsbWAUAooSdWCF2WC15aAyD11s9jzrKARwb0ZoJBqZnsuKfnM4E/yj5mabDdeHrECsJHmVnMwdpUjvSxXmNCvPSkYPYcrE3Dtqc3hz'
        b'zWAk8a7X8eGwUXyf5VSnGkVOkG2sbCkXARwAZT+30GwfZFBJZWeRS+TYKBV+gM8jNBqNfu4Fxtwj8G3XKG4evobQc+i5UeQeq+E7phhqT1i+pcjc78PQyVINeeR8zSgl'
        b'acL3EBqDxoSRI6zsEGc/BCOe/d5sc79vjMyUypILA8meUUIKIM5YNBY4/B1W9vnnddTWMrfSbV4wumKu3Itt08nmUWpyBAZ+HDDwvUNY2Y9HDUOwptP/MsM8uG+eGTFw'
        b'8ZHeRoB1Cojhz6Pnl2IJBGeRHhXDml4rmqfaBvWVipb3wTvxNQU550ZoPBo/9AVW9P5iAwI2aS4qMw/u4a6XRBaQGA7pXIpavBehqWgqPoVvsZnIJBuyXLz1BbhCmfja'
        b'FAbuECD/11wqPchhIKJOiyVrZTkiB290ceQWIPJ0NN0JUgG9PYrsGuJS4gv4NEJZKGsVOcGAI4djhroE8nANyA1oBn4oSjO/e7XbBQMxAYYTZRe/yIpW6DGIFWjWeEqw'
        b'c9LIFQYyvqsdS6B3p/AehHJRLr41hFXhXF5OrvHDYG3kobxa8horPHkW6PLXVOSlaoTyUT6Q9BY2GHsUTG2t1xvN+QMHTpEIHyh8+/FZco2zUZgLUAFpTWSl33ghFEGB'
        b'uYp+ZkN07Uwk2VX249cU5JoSZNWTwHtRITmMr7Lin/cfDo2hBNUQM//8mhny/J0jl43kmjAxEqEiVBSrZEWXzE9EZdDnc33NfM28bJkAX9KQw+SaGreCIAnTW4y3SuTa'
        b'PqA3SGSofl+tecEvSlbLCPdyhCcM4WtUv5mJZuKrIaxseQRTt5Gy1pxvj+gv97CR7MPbwxQzQMpFJagE1NtGVnp5tRb1Az381PNm+08XmKSa+zTgdWE8VUlhZaHSOfgq'
        b'68kyco3sDFPZB4LejcrIg1JWg3tgH1hcyGzta+53MyVJWtB4nY28EsZNsMMqRLMyprKS/1g8AE2EtnJGmhs21/mYzll8xRqmBF14I0Kz0WyQW26x0v8cMYTqQ1GecDM/'
        b'ccYUaTDJ6/2NYQJej3cgoGlzlLOkce/ZC8R0lLBhqLmhvGesVFScNDtMDeLpbZg/NDeJnGBFPxmZghbAopvwvLmiYcQCqb/TEybhZkQ2kusIzUPzFuCLrCyOH41qgBbu'
        b'n2aOnpIhSlNxyjwKCCLSVKvMaUtgUthN3fyRyAywDltm5jdWzwFuIC2ynXjPBNysIFfwIZgYVJ4+l41ONL7rws38vDLKIeYbBfsXjx8/3jqfEcaExZlm+1drpkgV59jG'
        b'IhjD+FPDzNEf1HPI9q2bFs41CHA96eork979Zq6QEbPpoxcvlKsGFxxu8Z4+8tw717JarvVoEHoN/uT3a5uSKtP3/GZWlPdI68XmaW9P+AJNPnBm8aCIge7YKcoRI7e8'
        b'H/OoJqn3gaScGP6fdYNt2aUvuzQ/uLZ5zK8yBypqa15LGt96fJ77B8a53pYB3ubJ3h3cS0TXH6dGjJz65wctDRN+8+ORH27/51J8c7ft28tON0z63We9Td87kf7r1KJe'
        b'l7P3X86fczn3/y4Xjr2cc/OYu++E600v3GlcVY65SV/vMenNnBfmby09/NGX374+Ok6sWJU0u8V07LCx+L2829/+8KUffv393jFTzzVMKDhpOVKbaJyqz3m16GjhkXF9'
        b'//X41NglrU1hJ9zfcw5d8Pdfl/9glb5XxMk+9746f/LDlilrdv72XwMPhVWs+tr3QW6mts7p+BK5DfJvITXS7TBwCN+OCMMXeOANN8hRScQ9WoI3JoHIcUkWP6jsgbfj'
        b'9Uz46IevpYAsmETugh7XUpCcS+2p0eSWQBpTK5mZIbXGRponW8m2vBy6FlXj+N79St0DKQI8GI3vufDFbPOUwuQEanElOwTUg7QK+PJwfF6vDCqzKIIJGAGSjFaWZDyV'
        b'JipPMzEGMBeFiwouilcwYVrB8Y+f6pfnvwr+q2ifF/h/PdWvgv+y7VcBv5ovFSqeCfIxvFbQcFEgBkG7ivCv6F9nnF/YEkDY8lR2J2Nxzl5+8SqOCSY+c8nLQcQralCv'
        b'wccKQboaNdsnXxVAQqV6JdKTtUq8G2/Ad58gVlFbLQoQq7inEqtqnk6eV0tiVYaeyS8JPxtvte9f3SCLVflVYZT9aIqnVNr/r8wiEUy6MXCHCukz8HEmpZNj02xuzR8E'
        b'VyY8TT9y+TNz+RuXW4/vPrfh+IZzB0duGnnoeNOITfr4t/MshZYa6y7FlfiSAxmGJZvLN2vf7KM6Nn6f/ZjO2+ed0ei7n0fs2vB1Pcfk8VWTyE4mj+Mb+Ka8KAaG+6Tt'
        b'btCzj4SeLrfTU+n2gLhtclqrrE5Q/iRUDaejsUbDh/vk7fgAFFC4oHD3ONDbjwP0Rbr146LwonVRj4NgwUi6DC+EDvXL2ClGfWKBUZ+cjh/kFuAtKbkFecm5oOuB5gzS'
        b'09ZQsk5X9ESMaC9oPx1GdLKv+ypvjxGqQsY7zGQXORvmFIbaqXiM8MFkTuI/UxhT0qXqPxbv5ipQlq20chrnGguPxicd/cy8gM39lQ1LuMrQX0x9c/BX2tPaN6vejDlt'
        b'3zf4azEfmzdf+K5WFTXlwLprShQeFzbsaG9Z/5o3pVpWv/AVcpBNdx0+LdlZr/dYA/pXzDhDe/VLgTfL89Y1NsR3ULva40KohAshcRwlW84+gZhQ+URM6OvHBPrilgBM'
        b'+CIIJoAAhYzk6DjAhMFTO+lbWwMRYQU+FwLL7FDdE5V9oYNh9T9Q9jujgrqwjM35T/syIa24dbTZ/uOYVZJogGYyeaHmR4Xm/I2RM6SbXyGmM9WvjjSHf7OoJ7KN+lWI'
        b'wpVPCUNJ4S9APf+t+e2KmqpXrZ+Yz1oSKg27fm+e+8at1kGb9Ie4t6tyLfvMn4j8Dwy6ySOKZ6VGLUs9k2r/aOyoraPcaTFpztcRmvhJ5I2NcTLGDItagi/kFySRUwYe'
        b'KfI4fBXEzFbGNHnSMgmYLozx+rqUogLSUpiDX1WgXiWKMY6Gp9XYI+qsy90m0WM1iRa3hC8xDF/4yFAuRrYaKfjwx/wjZz8/5ii8ClrcG2K3WkR4c8UTrEQUXOcAPybR'
        b'ina0YVL0n4Jg0hBKU671JdurQEVvptuOeEuRvgC3FLHN1mHkqrJ8DDleKQTMsDIQeSZLyKNgO4HKRlWVSkYggVnmFYBAAkMgBUMaYbWiNOA6mGWeVq/qhEBKibssAT1c'
        b'TLgPZcxOyzBZtPz+BMCfsiUCSjcb8svtyPbox6uVLgs8KSrw9t92JWJtarjiw6UlqRne307LO8hn9Dp1/cLoqubL+rj//fSvZ1zlyy3FhtBdr/zf17Zn7Y4cM2bJTOPy'
        b'aUu2fOtIwZsvzvrTB8tLQtYMLbpidf7Bsfxvjw/NvHzS9tbS1Ya98T95rJZNmgn4ZhozP6oRX0F24xPcLJDBd7nj2fCCYnM6l2zw71/jo+QYXuem84NPkZfn5NGF20xa'
        b'isgOK4c0ZBuPN07Hr7O3cSPZPIPs1cLzphSgaIoCDj8kxydLD/eQexiaLcCvAqKOxofxRm4GaY3sThpTdfmoI9KGV1s74Gwficb11gCuagFnQ4Hn8byGj+ZBPFI5B/ox'
        b'V0kxF9CVIqNXVelxO6oCCWDQ5QIYTa2WTl17LKaVHmzD4rhPurJ2nglblVeULKMvfoivSCg8EJ9QkEMFpLlrTkh9R/z72KhK+YzcsBMJjIDf2E4YPFDC4NrKb6M9MMvp'
        b'M1+0LXshRcLgY88PoqaVcfUptn5z9GrpZu5kabf5Z5WO/P81mqSbY1OZHq/52apa+wqDTbr545poaspC6c7qhtnJbunm70cy007C2pJlE3eVJ0g336iTeG76jDVpIVP6'
        b'SDdvKKUN8PQXqsIv1b4o3bw/IoGaZVLXqkX+G5pw6ebsWVNQA+WYmXVpac566ea7aRPRcmjo8jgx+ut2Gc6vyicgN8B5rN5ZMnyV/HrN1Hiq/KeikBcnfl0bL93k6phR'
        b'JyEq1za4/4oc6aZlZA9qhhuXKjjzv2eQWcI7A9LRWrj5h5Tl0e/XL5Jufrla2n6/vMaSb7f0kG5+3kcSQtf2cRj+tqxcunlhZV+q3mvMaHW/kIgl0s1rM8ZQtTRKV2dP'
        b'W5ExX9aME4vRMWrPeqEq8dEq+ea5NCt6Gxr6Q2RNVWWcWbr5F3U1+g68Xr/EMTx2lUe6uQ7FUSU+6md5yxfME9ZIN9/qzzhf/M8G19i/Ms2Rbq5wv4j+Qm2Ukc4xQyKT'
        b'pJtN05lejv4wzZnWN6qndNOQwmwIKDWxbvCu0fORbf2dLJ6pzxF93521s6CQpEZteuvKn3/x9WEFITmLxoXe/CQ2iz8X3VxW8dxCa2Xd9/ttE+rD3nyz5VtvfvXTewf/'
        b'WPrzUa/F/fHUvT/9vGfVLzbNmTFu3ZwEw7g3wodlRCbMSLeu+97E36w/dz11Xc+5//r8oz6O6ZPW7j6b87f09UdeujF4U4tycsHEQ+8WRC/b9+sZ9c9Pbu3T9O4658f8'
        b'/MJTXy08tW3s9cwfvlCRp9z7XsGcVxN//38nl6yZ/edvNP4l8WxI3Ke/2TF49tBPjw1e9sPkXYtSrpQrRpwdsizs19u+GvTFzgFXPjhbNKroeMoPLn//1ncLE96b1vjW'
        b'aMvYsW8Zbvf8fc/f/X7hiz9t+snNDYtL3gqrHiteuvynZZO//Y/G7yT/cdW//lTw3Vmt8zah0/ZN9Y0PH33r7yF/+WeKY+eiv7/5Hb3ANFi8sRbYerNhAXC7Dowc7yN3'
        b'GEFNxmem5hkSskF2giWKL8Rk8SvwcZAEKPFZgVvx8SR4OZFDCs8soLVkiyVUH/EEgvrkpBtyHWj1p+S4wlK32FTjsNsoeWU0ea5Ek5/XgEKqEYYyaSKK07EdpygmWURz'
        b'4XyoIhQkjFDfj9DhL7tS/Dq8Xzi8F/44FGi6BtRv52A/RQcpdoXV4gwg4t3wGM45xE+/aRWX2uh3zHtB6DcsFpQ9kqyT6Hcu2Uaa8XbmcrKDbMl3DoCJMqjQJHJFRW7h'
        b'18nZTrqHQv7rWgSJlboAonI+hAvhxDC2l8CDisOLwsaQcsGqEBWiciPawJUr4VolX6vgWi1fq+FaI19rrArKGqp4MUQM3aiBOyGN0Fx5aCkl/OFedYYoOq0uV2GlKgAe'
        b'DQrYeJhK2YvkHuV3l6rSyExG1aQBJqMGJqNiTEbNGItqtbo04DoYkxFQMCVcWcgshnPwfUcpojbpkEFo0DC8XnKC2f+967zLSWEz9O+/dSTdElZ8/v6VlrA+QxeNn/x1'
        b'oebVky39vuWafu17l9d8a1PV7AkvFdxJvVGR1nDmfOqAOScmnddaP3DEfn31a3NH3vjsRwe1+f+4eXvSTxQf/3lVXCjpNSTtQL67fuS9nh99Z9s7YbuvxS8seX/g748f'
        b'GTfgWpigD2XeM3jHQHwAVhi+Ms+/yGCJrcUn2frrA0/9vjX4fqW0RZsVyoSseZn4Ads3zqsy+LaNd5GbrN5kfCCNSq/Z5FiOVC+5y+Mt5OJy9iqXQFqTjMnZBfgGs4qd'
        b'5FPJFvyQ0YUifJ5cws14B9mRl4x34B3q58htFBbHk0Z8Ap9lSsDM6Xg3bi6CtU9akvT4vAJFDsTXQgQ33oaPsxbKoLEHrIhh/jJ8ToFUGr53SjUz3OWS0+S4eThuTgEZ'
        b'zpgjGW2iySmBrFOStZIceIkcxxeghFGfW5DM1YOeHEaaeXLTRm50FvU1T01e2siH2mSqsy4zmRjRGMCIhmKVtEkdxzYMQ4FQqOQfBbcyUkZso/yeRAY0XqHS7mJ7g6DW'
        b'2twrvJp6B3VgEK1elcvttFrd3nBPXZvFpDuNReWkbrBO6kIp7TZSL1inniaJfvpBbV9fttGPPps6049OsLYT9Tj5l64HF12UDWgRYi6/XOE5zqsxyVuicK1wWe0BfhvS'
        b'wGkm2i21FaJlcgTU8md6X4VWRvla9D18qiY3QpN6zqs00ZFzJvvb8TfmTIFEC686qYr/VHVWS3WGmHzz0GW9kf9OvWqTNKtd1hoVtNZ28vUYJFmagIg+m2TdSTek/3jU'
        b'kegJhbbcc7eVLmpOi9+26zPzJ+bvVNRUhVf9LF+Nev6xbiRP3juo55iFPJZcqpaWKT6Hr+NL0kIlLbkSfvNB106EzRVgBPS7z6E1aE1o3MpYHy60KyV5/ghOI62lbREE'
        b'NpDsH0gQS1E0jJ8rniE5Wqf9fRA0D94Q0Hz6Tx8GqGyi3nsmkzfUZJJc0+E63GRa4rHYpSdsOcGadTrqrU7AQbbs2CpsW3ujWZept5/F5aq02u2+xd9xAZ+jaCcVgyKs'
        b'I1QL+TuSzRsaxCt5LvpxeA8mVoCqGM95KLEcjk+Sh678HH1uslGFQlWqRUBsl6V1muow+a+rlWtj6yJXLuwR9kTuiYLfiD2RNr6Khyv5R+RbVCFCiCAaKNsP8EaOApZL'
        b'GX8IsHCFVQmMX70RAZsPaeGB+SvFUJYPY3k15MNZPoLlNZDXsnwky4dAPorle7B8KOSjWb4ny4dBPoblY1k+HPJxLN+L5SMAslBYDfFi742aci3tjUhFjD4tHIM5HMSV'
        b'vmI/Jm5Ewrv96bvWSHEAvC2UR7HeR4oDW3gxWba6CKJOHMT61gPKD2ZtDWFtRUN+KMsPY/me0tt71Hs0VcIehTi8RRCNTDCRzhnQ0dI2RlaFiAmintUYAzUkshqSWA2x'
        b'osBoWQoIP5WMeD4aEaoL+CfflQ5AtHuiV3kVNpBhvQqKjsGwr7BSHYAAdN1ofeu9kJIRSYoKoQMoT6zP/VxbpZXJi5rJVBogL2pGXjSMpKhXa0oDriXy8tE/ALPbgUj/'
        b'5dTZ3DaL3baSnt6oseoscodswNgsdZX0+EfHV8bXW5yWWh3t3HjddBu85WSv5kzNKNQ5nDqLLi3Z7am3W6ES9qDK4azVOao6VUT/WaX3E+jLBt3UnEw9rSIhIzOzaFZh'
        b'malwVsHU6SXwIKMwz5RZNG263hi0mjJoxm5xu6GqZTa7XVdh1VU66pbCwreK9FQKBaPS4QSSUu+oE2111UFrYT2weNyOWovbVmmx21cYdRl10m2bS8eM4lAf9Ee3FMZM'
        b'BNbWGRx5eOisj2dw0SvfGRvf8IJeA+yry5dlPi29L2dgjEqLkkeNHDNGl5FfnJ2hS9N3qDVon6SWdAmOenpcx2IPMoC+RqE7cotwFRzip6nHx52luny5f78+iStLtUnX'
        b'/0ZdnQz3ne2u4YUeujbJKXyR3KJGSoORHoLJm0Oa8tg5HWpfw7fJenwPZOd9drp6Xxy8HfXjdBVcqll7zOShG03kphavY4bKYtJEJfQUsgWuikpZNZPw5YJZ2fhidmFB'
        b'QU4BR/2cT4SQ1/H2fsz2YdaoUDg6kMXpzAbl/DGI6YvkENmtAoC2JeVRh8/8mdlt0jnZpcfnUGmGGp9PIvvHuCXTl5NuKNSvgvryUxYUSGaV9BJqPXqjFKWb7cdQf8Q8'
        b'2crIWbwpsGrSlK/pDWopQJtSkk225qvQDHJKRa6MJluYI818chEfcC2hDuM7UFwV3op34bO2h3ezla534PEvs84M2zGhjqRGTdv/y99k/uhqT13LhKNDphe2vnORGxh/'
        b'RlfxBr/gXf2vhtuzbkY5Xhr03j3lhwb13HFfiHGRj+NXDz0gro648/P1R0Y/+P7t39gn/mD+yiMLJv5g7DfUK0LLE7L+8uGYH33BRfwuY/buYQ9emZf84U8yvqp9vfmn'
        b'sSs//uWUF17YN/329LGjVjVcvZly/9rX3zMMW/OtVb+s6tkw5o9h372YvGBCzZhTwqG8KWHf7Ps2t++DjRWv76381SVnpOX3b0z45nHnofzE5BTPL557O+fLv0buGDTj'
        b'o/kf6KOZyjKXbF8YBgOkL/AkJ5KtKTyKxY2KxDWaCbiFFShY1Zs0G4rIIb/Dguyt8BJ5yPQi0lzRP8+YW2DIwS1kh3QkKhLf6IOvK+oWxzCHBONwXtrKw43kobRzGyO6'
        b'qXUBP7CP8++E+t6OJRsF0B33k1v4KtkugYl3KKnHZbv9Pny3z0LcZHLT2babJsFcQxVJZEuRf2s1D/q0XXJymIGvqJXkDiiIa/uwTcQosm1WXhFM8SvUXMHQIWwmT7an'
        b'4QNMiy2vmYibZZDG4xNISV7iyJ36TKYoTsbrh1IBFN4y90YCOcTh7YXkMBNOycOyUfRNtrLI2tXw5h2eex5vYMO1Gq8nD5nsCmN4sE0TpWrouhQ3VaNC8TYTVTNb9OxM'
        b'nDSwrLYoch8l4WtKsmnRAgakA2/Cd1lt+VzfRADkKIdbPWSHtGdxgdyZBA+NBSoN3gcPX+fwIS3ZJJ2AOd6gpFAW4NdHUk8RamXXVgvj42ysExZ8muyBd/MXmGQBT5sp'
        b'ZJFtxawTCvIy0IlmOhVbQcHeLnkka/FZYVoNbvLtp2n/Y5taRxEeZGMbcHVZ/82WpXfNSIXkpM1TU5kC9OBwPg5y7B7TiaPgV9Xhh+d43/WXoSrQBSWKa/Q1IUnLIZLo'
        b'T135nenIp+J2kLXbFIOn1un1aqmS2Pa1szqN/oqZNE4tTwMD1YrhHwVRKzrB/1T6YY2kPitNVOTpUjuc69MO21rxacyPhpX55SPKuUCW8LGuBKfVIiY76uwr9EZoQxAd'
        b'lU+tX1M13lRhq+wSpPk+kB4NpQCAdNVt+89iS1Ay/avLlhf6W07qXgR6dgBoz530tGCXjVv8jRsD5af/pP1Quf1FnM9ewMM6s0hKqoSkXUEj+mwpGnkwupOu/l1gnEX+'
        b'hdEVHNV0VIrpqKQ8jVz2n0Gi7w6SRX5Ikp8s0/17+ClB0RUAtX4ESS1jigq0HWjJ08kTq7Ozs+5dwvDfMf1U64VHJzoJrJlU2XDpbB3Wq8tqrWXn7EHDYTpIpxfp2XtZ'
        b'8SoFRQd6N93jdOiKLStqrXVuly4DetNZPk6ALkPH4cWlY4xpxlR99xI0/adEnU3yZXr5xOPGcY4kxu8U6QvwQQ6fxw/G2oobLgsuerh+9seez8zfqci2JFgToj8xv13x'
        b'W8jxFR/HvBlzeuHH2jeXq3Q7Bh1YN0pAh3cSIWTEh/P1CsaQFw2NzR/KeGo7foq3L3LTnXF8qze5YcJ7g0tLtyYtZ7tbQ/LHBhxLHzUNGD45NJ89wttIY688shUfnQWi'
        b'Dr+QS8EXcXN3BjM1tVD5zkZJnlFoTejSOGA9KyN9jEAuI732XMfK2oxjcyCpb2ccaw1qA25fLYgS6VD8CW5P1HiAGrlndnuqAfRs7IQNpVa3ZDDw2N02UJdlGu9xyfox'
        b'iy/hdlrqXJaAOBEVKzpVROsYz8wn480FUAaqgj+WaqvT/AQtjv7rbCGVvWf+tQgUsxc+V6NUc93KiFrkoQeix5ETpLlL1SxQL8NN0/2q2X68zxZLNiiZG+ErZOxn5lzA'
        b'W0P0b8yfmBdV/Vb8jVnxff22HxmmJ+6ZOixcn760Z/HJDc+/PHLTIOavN0IbtrvveD0v6QFr8cF+kirBkROB2oRmDH7opoyEnFUsDi7YoiRyqCcTbPHLmbLf1JN2Ul1W'
        b't8k3RYxlMzyNkvEUxEJJKATRb2VvH1p1esfXFpO5KKp175zFShj9SE3Poa0MROrozUGQuuvWn0Ue0nYAvCsOsNnPARgLelokNvpOjFH1pmtPMeZlwzxsqLXR72XztH5i'
        b'G/XCR/lcEGOdf9E5nLZqW53FDTDaxK44Z511mUzPRxpHBjGJdG0HEiVjC+u+zwcUGjLqSqxLPDanPDoiXFW6daK1wuZ2BbU90SUPELgctT4pzAbs1GJ3OVgFUtXSAFdZ'
        b'na6uLVOeSgmizKk5wKhtSzy0PpBdEihT1jl9UEFbOW4LZdNPphydHTc1hZ5JcD1sGrmSV0g35lkkisLkmdl+h9MS0pQ/M1so0eNzOTp8qXBhhdO52rYwBE2tjqzF6/AB'
        b'5q+qJudAbQ2010AFVkGuAoG+vncW8LC93BJyQzNnwQTmIT41xUG2hJNr4RwlAQi/vITc81CtBt9NIlddWs/sbLqbWkB2zyJNhtnMYaAZnyvLNtBGtuXkk60cUKyT+uV4'
        b'31ByuoxHZC++GV48Dd9hRiT8IL8gEKZ6X42ziuckz1aT/aQVFa9R4ZN4v2jT5ZXxLge8tSTs28nfuUu9CqfPXIOL/jI6/w1FOEajLyWEGNITBsx/4/TcdW9ebXBHjPSu'
        b'+F2PuPIft7T0HBh++1fH89KjehVE/zP5QPpLPcZ/69LtPj/Zenf0qnHa33907YPEhrx+Mx72evfhnx0u5V/n9S34n8MpQ+8M/PCLz/UhjEril8kWvAUItU/nDqvj8S38'
        b'CjmEXyOn3dTPAq+dPiQskbQk4c0eRid9tHQgPUv3GtlulNwGb5AHITPw+aSAQyLkdXJb8pA+RS70zgvY6Q6PEvBGMXYuflk22gwfRK6R051NP5oXyE1m4qgcuSBAlMC7'
        b'zSBL4DMJ0gHYuyt7k7N4WyeTzMIeZKe0QzedHJTtEtQqQW7gyxxuDcNXGOxDIshdyTBBrRLkBL5CBZV9Ntnv8KkcaSgxbSMWvuOzg9vIf08VJ7GAcJkRSDlVJ4bQrhYf'
        b'CIzI+wlid1xBCCjWxhoWQrKF87lbrqM/MX97EnNoB8mzKPAKE5C2LlnCcT9LGMm0tDa6151q8gyaibzNrKBngLqE4qQfiglBCV7mrMyOZv8g8FAfplqntcqrctmq66yi'
        b'NwRItcfpBAUgq1IRACu1gof7KGGuxLbawnChxjDZjye8KlxmYoomJTAxJTAxBWNiSsa4FKuVpQHX8o7TwW6ZmBSCTBL5GD8IVHS63nei/ZK4ge9d/+mErrcQ2ChIb7FX'
        b'YATpPQtV94y6TEsd1acs8rOKRcDXgjI0ursFPKa0aNyY1JFsX4vuOYlUhQVVq8vm/YM/Xpdlt1TrltVY5V0z6DDtc1sJX6e6ar7O4Q7SjNMKHalzjddldJSlzXJ3noIj'
        b'dtbnQgs96YhG5LHkWSa1Y4mkSabNs7LhVonMIbm0aLwb7ybX8si1XDSMnNSSl8hai4fqH47B1jxjcmIu0NrAtwvXzPLVm507K0GOh1HAIXKqfzhQz1fwQSlIlSobtdJ4'
        b'VJ6dk4Q+o5CHqtvz8AN8qaM8j6/WSiJ9cm5BaeBOS3NpCHmYjI96qHhmwIfxetLMyjCLeA7lokmUrwZus2QbcvONOXhTj+REFfADffgSvHa0h6qw+fglYC6BTJ72h7ac'
        b'APSc7Ohdl2fQJ+cq0UpyJgRE+Ie1eoF5BJAtIfg6a1lAisn4QAaHL2jIfRa/LAdkgztJoLgeV0MVeQXUuesg/2IK2cAeT1PiQ0m5BdIw4vOuJA71HCGQQzORLW3yR5yr'
        b'CcpMVtn6v5MUTVLDFcXf/HCu9WvfOHX8G/enRkZVtC45MHzE2S0rG/l/nt5bEHfv4E/m5SjPbBm38MCVn6uHxZLP3q5YMeu50vsbt/7o5e2f7/92XXnUhL9c/7L4z+8d'
        b'bv3g/EcFJ4q/kVIwMrHo+McTzraaw/q7Pzt1P/XFY4v/p0I9z/nlj85P+Zv13vLM8V9N+ioxNeF/gZVTQ8BCFzkOLJZcGUKDH1VwI8kdvJ3taoST+/hKWGIhT49pdubg'
        b'+AS57JZCtt3DawNlAXwBv1LHgyyw08H4ZD98hZzIy5lQWJAI8hWPNLiZx+v6myQefoY09gAGfiy7Ew/nyHUWaqXHC4t85xU8y9mJBSI5uuFN+FxeA6bgFTEHWpWdH6wU'
        b'mfxBdpGtZC87LVMkx2J5la4A1DNFAMHrAW5l9gp3Hbm+KoZtIQTuH+C7eomFhv+XbP5hlDHKpIOxeKOfxatG0ygZGj+DD5V/w9lJHJ4Z+UP/pVKu7BnIZOW6JChVEsum'
        b'ntpOK02q2nP7kGfzAVZINbFKjP46GQusgeRMe4Fg8A+DCATBYH1q86CeusL5OtgVI37bz4gHUa4BNJXxED/TCTQK6hXULekcXwhVZ+njnJQ2OenhPic1GVB/RNFRaTKx'
        b'TQonNUSwzQyvQG33lMAG2y/xqn3WZWoUYkq0N6K9ckulpwCxqoa91W7ievyXNpe6wjsnVZh60/lajaiBW8HHKFSc4jEPczXgMT9GxSIE8cK/91erCA+N5vhQKc5QqCKG'
        b'4+Pal4hW6Dh+IMPgrxiFfB634oeu/EJJqOdQ6HDy0kqebE90dWJ3ofJf11cdPK5EvlwhCuVKGypXiYpyNfxqRGV5iKgqDxXV5WF7lHs0e6L2cFXCnihR08KLRSAkhTVG'
        b'VQnMcZr6EYVbI8QwMZx5VWlb+HIt5CNZPorlIyHfg+WjWT5qj9baQ4pBBMIXdfWJbOxRpRF7ijHUMwpqjN6jhXajxNgW5uTNyvWoor5WveQSPaFO6mVFXbljoAz1uuoj'
        b'9t2oKY8F2Dixn9gfruPEAeLAjai8F/OiQuXx4mBxCPztLb8xVBwGpfqIw8URcLcv84xC5f3ERDEJ/vZvVEFNBjEZygxoRHBtFFPgeqCYKo6E5zp2L00cBfcGiaPF5+De'
        b'YLnmMeJYuDtEHCc+D3eHynfHixPg7jA5N1GcBLnhcm6yOAVyI+RcupgBuQTWwlQxE6717HqaOB2uE9l1ljgDrpMaQ+A6W8yBa0OjBq5zxTy4ThaLZYuMIBaIhRtDyo2i'
        b'gqkHM72qjFrm3nW+nZxEV770QPLwkgLbgghIAw1WOy1U9pMEt8oVfoejDm497f3FnFBBrdVtq9RRt0SLZBqtlORPuEFFSqhTMq3YV+gcdZKQGEyI0/NelWmpxe6xekNM'
        b'Pii8wvRZJYWPJta43fXjU1KWLVtmtFZWGK0ep6PeAn9SXG6L25VC81XLQXBuu0oWLTb7CuPyWrte5RUy84u9QvasLK+QM63EK+QWz/MKeSVzvMKsGXOzzvFepdSwxtdu'
        b'O2NYu32RBkp8eZeSEuBVfBPXwG/gRG6x4Ips4I9xx5Er1s2LfAMfh2io4ia+AZB5FScKDdxS5Exu4KgrI7zFHRNogGNR1RvKxaMYNBat4uoU8FxNr5oQfa8BmRRQq/I4'
        b'kHuTStSwyQ35yBRMD+no+SbPc5vjW8cXupLu2UhIuoVFqoPd6caaJQ3ZeOZbVlqUPDpt5NhANBJBJcmpoqK+zlVvrbRV2ayiIahCYHNT9QF4oM/HjbXs0w8llAUNxWmr'
        b'8HShUoynj8ebRWuVBZiLH43MoKPYKmto7TZpnAAZ5XYAwTr37VM6549ibXVsU6qtNyOGuUZ4OaOXS/2Uco1PH8O/R4IxNbVQr/ZGdWyW7qZY7PU1Fm/obNqT6U6nw+lV'
        b'uurtNrfTRfmb0lMPy8TpRsymwKQHynqca1C3J9oZ6/0pJ3vrKkJVXIxs7dBxGj4UBKSVkRICPLtrgJ5joHUpSfzV7xjga8LvF5DcEWnY1K2ot+rMMCWVwOvtxmnSX7PZ'
        b'6MxCz+DRfo5jo9QlWF/4BZy+zDshOCJ2ao73NRclN0fX8CI+zC9cCWxCvBqLy8S8QL0a6/J6Rx3otl2C8k9OjgepRY8qmb+Ap7YC9GMYDHkUdPV2SyXdirW4dXarxeXW'
        b'pemNulkuK0P0Co/N7k621cGoOWEsRbOZ4qlFXOSBgrRA+1o6b+K2P8DEsVgR/ojk/gNMHLPfP1XMiI9+H4zkzKqnoplEbqzLK2ssddVWnZPdqrDQTQeHtG8LpSy6eqdj'
        b'qY3uyVasoDc7VUZ3deutwDky6dBC56Za6hYzk7vL7QDBkRGHuqciBDIR8IFkYiCZ6fh62MKXyAylR35TO4wvdZANsp1HY8Vb3TWONi5m0LlsQFHlauhrdIs90M22qz7K'
        b'FY2n0ebHm2UGG2RfsFuLSIXDQYP56qoCTS8eNhVih2kISiKXWZ2wSJcCd7RUUF+BLoww7QRMilCdj6xpC5kpPjKJHF/mSUrOzjFQxTdvDrVSkO2goeYVzUrINeQkq1Bt'
        b'tIY8LMSXJQfQHWQ/3gpa5GVyY2ZCbjKNurwjqRDfICdKkslpHo2eAY9fVVaTqy94mFNbU7rFNTrRWJBL9i5TRaNIvF8wvoA3SdELL/Se2s7l8zK5llCYnJiXXOKrO08J'
        b'kqoG331uDZOqS8hOss2VQLaMJVfYRqQS7+DIZdyqkGLGq2tKcQvZM4u0kL2zCqYO5JCmCLTryf2y2NbGbHxtSc8yF0CjRAI+wOG1cW6PDrFw7WdKXNlG0MrvkbM0jAc9'
        b'pdIDgMWv4pfwIWYvwefJ/TJXQq4WX6Lqs3IVRy7OJ/fKbD+b/J7gehNKZBniY1smlUy1hE/f/fn+t0qvrGrZ9Fnr9tj0370rurPs6TMOZZtO9thqGPKjc/+4M+H2r1+u'
        b'eU7nnvZu1dlPhzxfvjTq3UWbojec+aT1o618+Gz9hNC01ZPWjE2c82Xmd9/vfc6Y/t3dFyuOXP/xL499ekv7a8PBO3uWtX6rZtl15wdf++y9y+9eXzt6U/Zn1i8/Ofy7'
        b'lw8N+Xvpg9/a9uElv/gbv+B3ltGaXyef+UPd+uV9P73V+/C+H05eORdPzvvFm39VpzysvL8p4/CU2/3Md/4lvBE9aXeyVt9D2pQ4gneRc+QmOUPnKI80q5EimcMXycEY'
        b'+fkCfC4pg2xPJlvJlpRs0iKg8CxBhdfXM6MFuT6QHM2Ows0pUIBDihQOXyPbY6VonZcX4lvV+HZSbkE+PBrE4SMvkmb2KJ68RHbl5RRgmJLEAjVSKXjNC0ppD+X2i/Pw'
        b'Q3wujwEE7/Xi8AmyfhnzuCAX0saxfRjJhMOTM+2sOFMlt42BleOSjPpEFkyrIHuuEkWSq8IKqHQns8BEReFNZGdDQNQIp501PRS/xuPNuDVJ/lKCopDDl/PxXnaacUWp'
        b'nhpWcgxGvCUluc/IbPa6Tqcgr5PDZLubHtCJwEdLp+CreW0LDLekSCsMcE5J1ifgPWyzhrRaX8zDm2FMaSepMXALh8JEnhxSk13uaAbL2pV5Rckc4pdy+E6fDNEjHfNs'
        b'wofJK/6T1Ell0jHPm+QAAwA3kdPkNbIvN68gL6/ASLYY8nwRRxLxdiV+DT9EbN5ejMT3FkDJ5kJ80aBCimkcvo9vD3wGZ8l/56hkrEQHTe1JP7MgpVM6tkb6CdVGybYj'
        b'6kQawxxFFcyJlNqRtJzkWirdpe6l9C+/VsGt7CdLPEGb8R21Yqci/x33UE56lckReyB5TOUIajOULEdoXZ8gwaW6hwnqpKJk1740LAoMiy4G8gEXEAWGZ18ceSp/mo/e'
        b'DyYdZErsTT6HIwmFVIwBbkM5ll8uk4UEKjG4ZFG/MzOSdxM6SBkdZIrgMkRn1lbWWV6xUJ7YjoX7OKqDsnq6lbKCCiOdIbNU1khb9bXWWodzBdv5qfI4Ja7sYl+ceTJ7'
        b'76hJtZdgA9wa3RZnNagtvpLd7p3U+TdPJAzx7Z34xCgq/FhdgTr/E6SA4AfXNZKH0sIFESh+7reVqNhsP/h8unRI49fR/dG4mEY13Gw4Vy4HjbpYcBNN6/U3QMn0JXMz'
        b'Dq+UPOwujNa4ckdHRPCII9sRAQaB93qotzc+MRnfyosmjR2kCt9WDds9AE5bRjf+5wC7p3svbV4EQJlWDogan19qy3qoV7rOQo1/yk0oaJHO0P/9HW0U33/qtInrB+84'
        b'9kpO3ibDoI/emVq2f/Pot1J+e7Ti0Oa6pc9dmLU9+4vLV73qFdoj3h4HV6x/qSZ6ePTG0rpXi+3RE3GrbefPPnlrx6lKBzlWsODU1drI+tNjxlzqedb9k7KBh/86fEFo'
        b'yMKYd77XsjjXW3l6bEjeknNv9fjRrxd9uOfCixeNjw9+ULl/0ke3kiNzt/w5dNf+UTtqPjd57IN/MaZ221a9VgoNeZqcJYeTkhOWk5faQkPuxRuk8+fb8alIuhWFz6/2'
        b'iRyRswU7eQ3fklwLzkXpgGGMr+mCZYwbIh0cuNQbuFIz3gack0VDoqGQxuLzjOyPAbr/Sl4BsLWTXZD9zQ7J4fBVsjskL2cVvufnfUPIegYo2UuO4ptJUvyOWWl0AyIM'
        b'X+XJBfK6tPFBrpNL0TRaEt6Bb/kjJvUR2MNJcfhlYJtjyJ42zol3kt1sVyRv8NIA1pmdwy/ws86x5Lyb+YtcJ1vxLSak5gDo7RgoT67irZzJOCRFg0+SAzmsJxOq8AMq'
        b'UqrwPT00qFrEDygkTZJb5mHgrK/JbhRkFz4auA1D7pL9TLJpIPezkgw0pv3NHkksrj3ICXi34OwfEexA/dOyOLWsNjCmlhbA1DRjKDtTyach4rhoxrhoiBAtY2ySV4SW'
        b'ekJoZZYhV9XOH25Ne+7VTawQXirb5v6wD5IEvgPPins/CM/qAEAnrZxSGqaV02gCVCuHX2o/ixA5Nw/XwgYuDgqIfGCORdp4xA+zPVIMM6ZVQYcofN5wU53DJGvMLq9g'
        b'qXBJJpYg2rs3yuTfBJdMkbm8fGI8nIdR5Ff28llVOpTrZC/07z7TuHdN7CMTG3jnkAaO9QUtFpw62idnbAN3jPYBHedWcXVhbkHkGlielqwSJCsiXCvohyqYYyBf+GiE'
        b'n3nW2lwARmUNYzvDgOpTAxXTmukFzB4bgp622nq7rdLmNkkD7rI56thseUPKVtRLZik2KLINyqtkPNqrkYy6DmcXzsJaU72T+gFbTaz8TDpY7JsfzOVGS+PicSqQWdgJ'
        b'eHng2r0RdOLZsLHQqtQMCkNBDaGLuCo+TjLKwABES7Ul0E4apK46V/knVdseSo3JBG06TaYFvGyXiQk0j0nPukbBaAaJDwkDoVBTNINRD2i6Az6pTfS4v4mdXWKHJqLa'
        b'cF9+1E40o9cKX8PxDPePASaI3HF+FRuEBm4x8mEBN/Ec7zyOZJMhXLOVeDQIGCqTye42mSooFLR6KtuujPDDQZ89MxgcMxcCGPzESU7KVZ3numjZajJVwR3nBbgR2Ko1'
        b'SKv++TcGLpsevgWxmHdESe0v4hZTOxW7v5iXjXXSRFA4ukBYAMe6xGRaxMvO7aFMzOcfh/IBgNESnQDz2wnD2XDQRsP9x3f4brpfB92s901/u2GvCzYATxp2hX/2J3c7'
        b'6tUwp64go17978y10tcoP7n7uQa1w7QsWKvWICvM7+xOh9S30tusvW1EuvN6pjYwk+lF2tJlFGCJ9j1p18N2YuvQoD3sRbdyECO8/Abet765pHNC2wJjpNQXFuSo/24H'
        b'4GDFW0TRZFpNp5wxDhZrMWDVs8dBET8AvyiAx7m28z93uhp0StxYjRuCDIazc1tPMRjxHQejmg1GsvMWbfV28E67PBUm02YKw10KQwCRow+67q6WgRDW1mG2oO51111W'
        b'Y7OPloe3o+WdWxNQAFWh+rWfqqjdiFEQyMd07jI1/Xu1hQ53DvBOKz1rZBXb8IANQ1dHaEymWg8g4XZe3sUIZedR2yEBK/DUSCC5Wjpxd6PCatwTDAk6t9UOCcYFjklU'
        b'Z3To6x+lvh1HSSJEKW2I0cWIhJlMbqfHKtqWmkz76cJoo72hICKsjPYD6y/278Pbxw9vn6CIzKc8GeBwYFl2h8PJQDlKB5UaZlf29MPZ9vTfBzTOD2hc8IEd9kQ41Sxa'
        b'kMl0xg9iAIo5Oq59RSB07eTSHoHQuSl8dN8aIGm7XsCv4lcJMpTCBgqvIF1V+YbWq4IRgWZB8mZU89sokHT6FAxKOr3KZTUOu5X68dZabHWitSsJM9Rkkuo0mV7jZXIR'
        b'yhSZKJ6qNorHK3v4e+wr2bVUSWU5idOEsaGXB9snOQTjNiz6WrXJdIsO8en2Q8wePE1roW2tVT+ptXqHy2S6G6Q19qDr1mJYa26pJa4DJXO+1G4uumoblCOT6YFPWolu'
        b'x7YqgrXeHQ933uimJVsdCCJf85OrtnbYg/9SOyFsoVqgwq/7W4oKXMP0kXMTCmIg9a8T6l1LV8Zi5NS4QeNkXh2cKIgKyjZ6ARir6IqgWhzfxB+X1oi8MhiAysJPaaWP'
        b'BrO9XFtdta7esUzaDR6ZKnlFeOrrHTS0zyM+1ejlRsJK2eqbLq9micdS57attAYuIq8aaqq2uUGftS6v96luXdoMYBxY4ybTWz7JV8OCjdLP2wWMiFzoHOM2dFj0KR2c'
        b'/5x2uT6X3eGmscOoj65X297oDPmqKmul27ZUikAN5NRucblNkknVqzB5nHYnjQztPEKTNjdCP356NX6FPYzZMKWdU2YVZ4qr8xBNGJV5hSanaHKeJhdpQsOWOl+jyVWa'
        b'0A+T0MjxSJKj7tPkIU3eoAljq4Qm36DJ2zT5Fk1oABjn92jyLk2+T5P3aPI/NPnAN8b66P8/bokdXD6WQPIduiNA3SA0SCEolApewbX9RPExHB/bhQ+ikucGcPwIDRfP'
        b'8bpQTqsKD9MI8KPQKjQq+jdcES5olPRXK2hUWkGroT/hIeGC9BMnuXu7yNYsF9mmm0VaJJdETTzvGdWr67iuP+zgjuiLpFqlYHFdNSykG4vrSgO7ySHdWAxXMYTl1SzE'
        b'm5KFeFPLId3CWT6C5UNYiDclC/GmlkO6RbF8D5YPYyHelCzEm1oO6RbD8rEsH8FCvClZiDc1c25UivEs35vlaRi3Pizfl+WjIN+P5fuzPA3bNoDlB7I8DdumY/lBLN+T'
        b'hXVTsrBuNB/DwropWVg3mo+F/HCWH8HycZBPYHk9y/diQdyULIgbzcdD3sDyySzfG/JGlk9h+T6QT2X5kSzfF/JpLD+K5ftBfjTLP8fy/SE/huXHsrzkCEndGqkjJHVo'
        b'ROU65sqIygcxJ0ZUPlhMZ+p/hjeSHnspaztT+tHljntBvqOXAYXk+HIdilFnCubZUWmpo2Sxwip7r7ltbCfG53/Bgpj5/NqoC4a05WFtvzkjbwm1d7mg+lDAAVgzJcIW'
        b'6eSO6Kj0UCnfX3O72hxOX4U2t2QSk1717bBkZhSUTZNrMHfhdNcuk1Ml+49YdBXMgAfVSRtjgQd0DVKTvr7KjpVup5UOSLv6LC7mx0mBY14dS6Emi92u81Dhyr6Csp12'
        b'J3/bvdyO3VKllRIcuiftKuco93NqKAfsjZp4D+cM93FBN7NcHudWCSJwPJOUKliqZKmKpWqWalgawtJQkDnp3zCWC2dpBEu1ogBpJLuOYmkPlkaztCdLY1gay9I4lvZi'
        b'aTxLe7O0D0v7srQfS/uzdABLBwLvFkw6kYN0ELszuIE/NuQ4moZeSAI5V7FK2aA4Bmv0OOfaKMJ1L7RKURfO7qmOc85WUQ38fViDghoDVyncw4HfKzbwrkPuEaKmQSHZ'
        b'bN0J9G6DcoPAoSVLm6Bfi7RNIAK6zuei9dAykw1CCp3/S2WD5yTE77RMul8IjDlkeTmTlzeZHilNw1zDXI+GdaykxkJ9ndrcpSRzqd4bXgJM31YrOyWqpL1BKcqoYLKJ'
        b'XqXJY3U7aVgY6WyCN1KKYe4/nuacRtkS/ZqtkyoTTrrNIgUqmc+EgvYnG0HokzaBocZ6jxOEWSs0wQQCNbOhuy1elanWVc2aXkxP+ylNVukPO/sX4XuNfXAMXqqsoRuY'
        b'LM6txe1xgVTitFLjtsVOYxvVVTkAYjautipbJXNNBkFEohX+x5Zad1uHvDEmu6PSYm9/6J7GGa6h264ugI+tVaiG/ZXiD3v7mToMOQixsA7lskq4rnV5QwFIp9tFHa6Z'
        b'SOVVw7zQOfFqM3wzI82E2mV10wd6leQOQC0IXtXiZfSb7gEhC1ajJ8dLYLP5IRX5yhG1PWuChMTSdLrT5Q9P0yg57ryWmTS0kFdwK3t1GIFnCucsxVZ2/hGhrr07o0HN'
        b'kZxO4zs25fc+nVjG3AjqFredoDRIwQ/cDvnUKXX+E4FE26pWAOENIIjP4IxKfWSdmd0BG+sD9tHw9oGy6J57rcPddtSVxQl9hkhAzuzu2o33t9s+PlbnZmlg0mcIT5XX'
        b'Xat92/c2MDZWh2blKKFPP8rdhsUa4G9XHyQs1n/adFl3TQ/yN/3jDJ0UG9blqZCPVDBHc9qe7Pkix17qFi4mJEkVse1EKtPUw2tUHmFRaYJEczLqStvuVdmstEFZQIDa'
        b'oUCbX4yf9rt0ifI4JRrg0uZmf32xsxLZxmGiFMAq8Rmwsry7wUrwD9bozrFJusDPjKlzMlIgmf4MWAok5E/dwZHkh2NiuwPxNPSHtaL90fiO8GSWTJ+WMm361LKnhEf2'
        b'o/9zd/AY/fCUsNkPYNmyt5TPeb6DG49RN43FKJGcluzLLCtc8olwXZ212kLV7mc5we/8S3dQpvmhTPShus8VKQBgmTPrEkpnzyl/BnoGrf+1u9af87c+ghF3h2MxlWSl'
        b'c+0g4NbXO+jRJRCJPNJJ+Gfq+N+6a3qcv+nIMv9JlKdvQsbIv3fXxIT2FKwW1qyl2hqAhvU1K1zUHU1XnJFTCGvc/gyNn+OcX3TX+OT2Q9vWqN1R3b5NXUJeyfSsZ5vV'
        b'f3TXdIa/ackVr05MdjuS4U8b49YlTH/6NuUNw0fdtTnN32b/oLEWdAkFT9+gPLn/7K7BGf4GB0n+hiAS1tEzG/JSkeJfFM8qKX42mvJld43m+huNZjSOScjy8ZOnbwXG'
        b'8nF3rRS00YSOlIvK1dQxhl4nTC0qysspnFE2fe4z0k36rMvWi/2tf96x9fbSvlGXBTRihhXgqWNyocuvcgeL5w7Ea05OVhmNym7QzZidadAVl+QUZBQWlWUYdLQPedPn'
        b'6Q3M0SaLokyNXGdXtU0rKoAVJFWXlVGQkz9Pui6dNTUwW1aSUViakVmWU8TKQgvMDLDM5qJup/V2C404JcXjeJYh5Lobwtn+IRwcQNQl1UhCTAtbjBYXjOKzLPt/dYc2'
        b'8/ytjuk4cZIGZ9RltB0byynMKoIpmFY4g1J6ikrP1P+vuoNkgR+SXmWM20tqI0yhSHHH8ZRrRaY7yu6G2tRG4+VYKewcotSQtc38E6iLPEs/+e4ar2hP9NqIHfXD1lGb'
        b'VRCm4nMIYbsfs+UGXSOYt1o42w1kblD1WnotnVSlux3wq9gAqYmWVzLvNnZG1sTSYypI1ccBK9sQ5tGEEslXmVqu/DKOJHK12dCCi2RGvcb5B9rNWpp0iNTMbBA0woCT'
        b'xvzS8wHhnDtsEIXRL7PJVVoFeX9RxcezDypRHVfFrezbUeEMeKfrmaJWNJGTN0bLpCaDTRPdlXAI8oYbaNKd1Fu/S0uXJxfj5Tlyquku7nFEd22rpe2xjVIMWzVHP/pE'
        b'jRJBvdQ0ssHCRL81xiCXomgFA0Yq2HW/YwKAkQLpij5PMWbq8kGjlPSQLpzm7NY6k2lZIDTBjQysXKF+SLBdKmb8YPtKXm0Hw9UUP+a0IU2dD1+8Ee3tVirZbKWWOTf7'
        b'WK9XJZuslJLFSsEMVgpqr2LRQLzh7YxVKtlWpWB2J20Hq1RYoFFKJVuzNG3GLMmQpG1vrHIaOBl9nCn0aiQnD+JThVJz/gqS71PL0PtI2k2KDuPTnjGuhbqL+4r/LE5G'
        b'l39VT1cuXKEJ1QjhSg9FAHwGX0wLWxpRH67PJduSCvON9OwVaa2l3wdIrFHiy9PIrqDRFOk/13IUuHsl8hsR+w6hICr83yFUytcq9k1C6VotqkUNlNU08lWc9P3B8hAp'
        b'hEZ5KAtby9NQGnA3jJWIFKPgOlzsIUZDiQixJ6OQMd6eHVA+3waauiIAUEUgIaCu8JQYm5iThomj29AmvpoGDxBEP89QML3AG+L/QDBc1jpEi51+E25wR1smbdEUuGfi'
        b'8vlxjOPYPq2vEo2vjo4Ujm7vrhVk5iVZEkO5lf2CtPNsZ9XZ1n/f7tjfZr/RMGhrz/QBOFllnNZde42+9p5FZJreXY1NXdbon3TqEOFz+vBNMXA8WmtWl1XDg6206std'
        b'Dk6XlL4rTwxZJ2prsz2rZfSpxd9mR6Yqt8no+VMw1Y1PZqqttK1kruv+yWy1o+O+35+GfrTK5yDlCnFDw7IrPnPfWiy4+sA1c4Zi1/RKsVhwDnArpe0xyKuOqakHH4fk'
        b'1ScUPkoOFHtr6YH+irYoCSM6QDqifXHRYZWOrUsu/yx4i+9kHOMRIBS9jOSlKX1Tfga9yqYJ8yihswMMrb4elG2fr39YQBOsaBeuWIJFFHf7ZKRQ+ThJKHMj6cSa2RBD'
        b'+a6xJ1TGnjYvnrbZ7IA5qfDiYUF29wSppHewxoKLY36Hyhi2SiQK3oCmoQ3SamGfKewo/PpfomcQKPV8QUUPX1BpZie/hDr11EiMlneOpiO7Wrqm68HLuTviYiQkx3zQ'
        b'x6CVycGgdzvcFjsQJLr75JoMF5TOO2rrJ+s5r+Dy1AaVk5TsraMUz39A11TQcWFlCvXajhJSm9MNQ5Y2PGkTJphsUcDJM+As9gsY3cQlyYRCqwR57DQI2LCKxWLlwwWN'
        b'oBWoO4mHWvXxAy0505kt7yDX4O9pfN8ABGwauajOz6noxJzj5L+uPVw75gyTy36Ew8pygbqUUIcS+p1AMZSyXvpFQFFLWa3Y47C2nH4cWAlsOFrsCaxXyc6/amicqsbo'
        b'xt5VajFGjIX7KquaxaSSPiisFuPptdhb7MMcT9RiX5bvx/KhkO/P8gNYPgzyA1lex/LhkB/E8oNZPgLyQ1h+KMtrIT+M5YezfKQEUZUgjhATAJYoeP68DVmjNqCT3Hau'
        b'PAqeR0MP9GIiPO0BveHEJNEA19HsOlk0wnXPkBRxvByLi0YAafuuohZ6G8X627MxpjG2Ma6xV2N8VSyLfRVSHrNHvSdOTGvhxAm0HRgTgUXAovHAYuk3CMUx0jNoaaw4'
        b'jt2PE0cxOjfRG05x0ecQ4eWKvVyRXunlZ0z18jnTvfz0Uvhb5uUzs73C1BmFXmFaXp5XmDG12CvklMJVdgkkmdlZXqGwCK6K86FISREkpdPpg/I853JGkmbkFOu1Xn7q'
        b'DC8/Lc9ZRqkbnwN1Z5d4+fwcL19Y5OWL8718Cfwtne6cywpklkOBWQBMTrul7wt5zvwe5E8MSOG1FP6A54qnDXje+eOnnQN0Kwo9NEQtuU32kVt0LbjJliIjaSmgMUWz'
        b'/fFJWQhPYw4kZEsuOZVvyCmYmU22GHLpOUz6veLJZH0kvp6Iz9o++ukbvItG23vYeOwz82/MCdaEnydYsi32KnuFwbLgjf/52vXWkQfWjYrY/3NUfU716+z39AI7QJmP'
        b'T5N7YficIdsXUhLvre1B7gj4ooYcYqdQh48n+wn9+lVuQelsI/388yF+Ob6Nd7DDncPJFWPbl5jLKvAOtfQhZnKs1He88Mlb1byPVPvONMonG8exgP4xgTjV/uPGyrat'
        b'cif92G/wz7YC4WIlhvuL+Vu+KvjiSK8L/In+ZpDDi0HhqNQEzDVtuP3HLzUMlULlj4hL60+Kx9P28UtNUwigVwigl4ahVwhDKc3qkNKA62AfFKd96/z9v36F7Pt9+L4t'
        b'J88XQZAi02vkYXKykYanZdFd6aTPKl6GN2bjswIi2+vDSCu+jo+xsLK4mazHu9teB7wrSp4tn7HOJS1ArHfkzUkgW+ZoAH8VCPDhtTDywBKhwNfYWW+tQD8AiFKPG832'
        b'vHGrEfMhnItfIWdd7Kg3Po5PsuPeBrxO+tCFJQRFIVR80mLOT4v2IA89AYpvkPUF7SPQtzv1rUbzxjhL1Stq7SxczKiJpXk5BXkG+s2J/Xgrh8IKeXJ6iMkzkHGeJWSn'
        b'eUlSNj0gTnaPSk3FG815aDC+IeAHw3p6RtIleZNcJ68lQa+z0wfAgpwVcLQ8wZicQJpSEmkMXodeAwzrBt7EjrDPjcCX80hzTn6KCqnItsW9eG2BFBSCQaXBO2uS6Ggn'
        b'w+Ph+Bi+w4/Bm8lmD7VGNIwhm5OkqQjW1MwEFm69OEEg2ylUpAVvyhbQALwpAt8kd+awYX2OrMNbXEvJVQXiyCbyEj6IyI6cKFY/Pp+E9wR+BLIeypUlwAw2GwwFs7Jt'
        b'GSx2vnSkvi3eJDkphJMdCbEeusZd5PpzvvDyZGt+cvkAFeo5QyBHyMsx7Hsk88lOfC1Jgg/GLLktqn9bTwZVz6SN8Hgr0Jgb+GHYc+SU0sOiudzCJ/Fr5BA+RHbPhPxK'
        b'VEBef1Gas3XpDTDQV5YtJdfxlmXkqhu/hNerUERfHh8sz/FQsWY6XktaXfBoNv2eQEIu3iMkAwYAmWQNliS0waVCeDe5FYoAt19m840P4z18Eh0Msn1cbxr/dkdpQgJQ'
        b'wqaUwlkBXxVAeC0+F4KmxHooqcAnq8mDMPI6ue4iN5fk4nu4ZZkzfAkBuanXKAFv/H/svQdYVNfaBrpnzzAMDE1ExY7YGDp2sRekg1LsBZSqCDoDYhcVpTcBFUUsqIiF'
        b'KiCKmnxfejtJTnKSmGZ6MzmpJ4kx8a4yDAMManLKvc99/hhxmL33Wmuv+tX3nTaadVvSlkGYQwlPXFxpz57ZZSRYQ6kUalbiATblB/ajTJbCpK+9I5wjVq0SWG9AkTwO'
        b'r5M30lJTQjZchbp49+lWUk0M2bombXknfEFrouhh9dOb1x4b8s5nn9r7HnLc8b30i+FnzvT/ZPEI60u9jMYEzj990n9O0g+SezN3ujY+P+yVqdvu/Pze1ILq2TNXq1Lc'
        b'+yj8f5GLyqDPPw075bx2laXKr/QnRchQo/NDyxQ/li//1abwpuzHp/3eL0ryv3gtdkXWvQqHyyd32g+9Xv/CkDcrcz+Zu33a6uhh33/52iuKTWY/f3Zyr5Hty253+s6/'
        b'ohkbMc3MQ60epmruM3qhx5Ny96AnzBpMNBdsQn9xtHx3fdp447fKf0vf+tLPP1UG753iUNnwk6/8yenrPh2veuJgXq56wwZsLhpbtP7w0K/MNZ4Zyz+OXvb92fB/JP7a'
        b'5v/eylecbHaFNY0f/erWisOnFqw5VbfY/G3RfcLkXTOe/apvbMG89R/2z/U0qlwWkVT12YrjVX+fcdfM4Y3RYaunDn92c770KeX3tm6/ztjUdqFgUEbS5JXFp9Rbf1Ae'
        b'H7Nr4t9Gb7z31XZNzodLZP+8/05EVppznWo4R9Mpne6rdzpCFjaKAj8eJ8xmyf54mMyhI2QxcR4nZ0cKblAr4hljG47bvB+LsdbPxgD3ggWUcpaIdAXWQ06qhbmpGps0'
        b'2JxsH2guF2w2SkOxaQUDFsKiJQkcs2c6Nm6SzIKreIHTTx7Cg9GcuYGIE5WMvUECR5dGM2QhrIS2ZNI2IlKoMJOsBrhJm1cjYiW2QgnD/XFxsoQcyyVwZhM2b8CmFFKz'
        b'sp8YB8UmDA1hebi/jnPi+kBGO3EBMtmTO43srFO6k0JAxeBkeiCZ4hks9KesD6Lt/C2SqXi0D4dhasMTnmTBZZMtInfDZqkgmyyB+rGp7CFoHWfnz+g5RcyduFLiplmR'
        b'TM0gDqTtFZpNZhtTsMWSLIlcS4W5KdZZbsIKKCbLD5tTN5KWB8rk5CQ6Dvs5rsR52itOLpgXQPQa+bARSyR4cRJWsy4dOngx5vjAJSJ8REDNDsk8uLkk2Y6dm0GelMwi'
        b'By76BJIRL3D1c8YzgVJhADTJUqcu58NaDFVkx2LMngVk7w+AtilE8JkpEpGu0oNJRl47bSf3aacGZVuAkdA3QGZOHjvNxi4GjmED5LjR+WVEDo4WSIsQ7fFUMsfHOreA'
        b'nMc5btrdyynBSFAGi1jqjHWMN5ScI1WrtQxiweQ4rknCAlINOSTlwlA8IyPb5mW8zGZxAKnmKr0VCiZ35htTwinOD3qGnHwlDGsrL4B01Sa45iv2gwrSV3QexW8ZxqC/'
        b'XVyDAoIpjdMuY3LXACyXbYQbcJJzgCztS7rDH4s6DhGLUGmgRwoHK7m6k75NsKsLEST8XfGUlMzDbBGr5mANxzrZg9ehVbGK3OPn7EskA0ExSVytwJvsZfHwGMhil/A4'
        b'7CGXITOY1+JLZqajgxHuxsu7OJDXFUfIJ7cGOUOWmyfUaXdzI9IpLUZGcHUmx0apI1OjiTVIK0/gHjwhIxt0jZTMzQKyvJgMdWUeaVaOZWcZnTSlwK2z+upEjpY8uICF'
        b'w03huDyWsdRCmsMYw89CNWYGqMjEbZYLAYIxNFgP4E9c2YytfrKHc9tCgclOjkhSBjWqEDzHJwq0PyEnurIUb+Jue8Pi93+erZXZFZgYv6GbGG86TcEIWmWiLYMrlYl9'
        b'JbYSM1Em0ZoIJFYSK3LdlHxPE2YV9y2k5IpIr1lL5aJc7Ihe5b65jt/ozyGSrX26iOZ6rK7VptrMqfZwZhk1ualp76lnUb1QuSYyWReZLNesiYteH90VDcX4ETqjWqFW'
        b'S7SFqpPpD1YIqyiF/sqs5xqJfo+1GFY/Rj1hQP0w/I5/hjjGeJX27XrEUtUZzjtX9qcs5iyMMvVB1u27Ove0A2Myac/A4K2z0wKVdIKm/3NhuuRdlau0YVWrHsCV87uu'
        b'Ic6GArHiNR1t+9MEntogAeas7ql+qsHx+oeEsQgsGn/1lylteWQADZBPSU6KiemxVqmuVsagSu52Ibfb0ZyAjlgw2hIWU/3XiG0dHjT+cl0DHFlsRHyMNhhiPQ1BIb0e'
        b'nUiTWaL+Gmsq6QKzVXprusdmmOiawSK1aFxGLEVy0wU1/pUhV+c/aMDNdFWO7hmsuHPFevWyDVaH4EcPKB0OPLckCDTBZodkq8l2gVkSJMx6IOyUhOp9NmSoajd/d0V4'
        b'65kmdhyrPUbyJ0liKZ0S3QwNItR2IhXqHPehsdPEJaUkRDG+2Gg1wxK3i4yNpNEiBsvSMTPNSYiOpFFUdnNZ9gwdYC30LQtC1MKCa+OP4g1D52oRwyMiwtQp0RERnM02'
        b'2s5xXVJictIaynDraJcQv1odSQqncWbtILs9sgkmd1vtFBxfG37AYQV5/NoWvbCwh0OnR0TMi0zQkBZ2B/Rj6V5Cl/8k3YZcGhT/j5JNEg21a4z5bO53d7+KeGa1Iub2'
        b'C0Qgy5a09P9JJWECcKDxSp3MAecDOokdRtxDp2WG13NcyGJioxl+2Q80Q76zkCDskg/ZOqLTqaNZk7CKdW6Hg4QWwAuk7LPcYdRBO0vZMK1kWnyTzieqsNvsy+5nagrN'
        b'ZMLcCYouVlgscmoXp/ok0jfDg0AdFFnBVJWCZiz2Z+oY1mGLuTvsHvzf46ztblDWudL0DcqUwMSD8gS7w5Wu8iM1x2QFOPo5w/kwbmCiXwQHMDapC5ClnDwa98WHT/6b'
        b'REP3qI8yAr6KcP3wzjfNES+sdvjUOTKA2ZHvRHwekRhzJyI71i+STIgAY6Gkt0LYv0wlZbIrNs3bqasYdns8QHaNTOWQsvvhcqwe5q4e4C5cHYq1eAT2cpF+H17e3D7b'
        b'8EZ8ZyEXDiQ/kqGZzD6Ndvb1NTD7TIdReqFHmIEa7QyslunB9vfMGNgOz7VTN0szySwd0NMstb5tYJbSpKOYKVDV8yzFtGmGp6lTEJ2m9QPNp8avU4nc3laCh83Y/CV6'
        b'Yasgs5RAlWUKs2S6msBB9sgQKBFkYyXQCIU7480dmvl+f1cR9lFUXKzPmgAyJ9Z+cM6o4e3+b5e9ejj0cOji7WLa9qcG7B/wlM0/Jgc8blYeLzx11iSuoa7dY6pvjO8Z'
        b'r0DX4UyVoEq8KOk6UmZ9rExNZVv7Gh4pPjbiA0ZE70jOJUNh2dNQWH1lQAjvodb/Ap36I659smH/sCJU1FAl+gf3hq9e6E/W6Qur42LM2Kbd+3vxiZkjyaZNTaUKMj9a'
        b'H67OTl+iVWipMgt1k7sNYZfoDjZWhnZ0U4duPhMW6NGxg/fAH05LHdbTuFi89Qi+me4BJf8J6aWbB4b+1/0QlQWFxQf8+IpEQ7/OrIn0jySDkSARZv8k85LMezOpQzLs'
        b'dkYy53uPR6TMqZsWyKNZej4TaXkjejwTDWF0Gq7hf9OX3WVQMr/7eRyVaagh68NXmpw2Tor8nIgkyx+7XHiyjPo0BwvDf5V+vyySnEPUGUIOChtyDjVAhTO1DclmSqDJ'
        b'i5wRdB3i7uiErtM/Gpt6NOjQ+T+yDze0Fi5zoU4oKO2jCnSRk6V0TYQiPDOth2F0e9C6sHDtrszzONweh5GWN7rHYfz7o5gLdJG+Qjef5aD2bl8rMJ8ljRUwY7pFe7SA'
        b'mNGLSTGdYgYyjDL6M1/mgIyBGYNiBun8mcq/5s80059WuhkwNYgfW2m4b5nOzQZNo/qJFkPduZvNjl7f74UHlWpswibLjdQk3JAsF8JnW8FpEa8mQzpziu6wxTLmK6I0'
        b'isFwkTqMXIKse/QX4f7NSmiyNVPJOVj17l7JGurngWJ7MiUEyDWCZsYNMQ1r52FjilyIiBXwuECmRtV49sh4LE5QYrMRJUSoIFKSACeX7uKenmq4CHs1yeR8LgkVMJMK'
        b'RIXr+LtmYe0wJekCuIi5AtYKcBiP27Py/CDdT5MqCmpoEPAAdQ/V4HHmTuplb0x68BkfhV1EQoLTcO5O6gvXg6gHTSb0chGwUoCDUAi17NI2OZSyl8Fr0MLfJhb3ptDZ'
        b'twv3S2g34eUptIP0uwfrktV4OdTHiRrwuU+tEA6b7PAfyZydUCHBg2OxcKw7dUYed/Al4wa5cC6FSpaQHyft5M0l/zA0mQXzF80bhqVj/UKNhXA8LMcmInnsS6HUPEFw'
        b'aPtYQRi4SPAQPNaTLqYLChrgvCsWS4VeeEVwE9xSFAm/3L9/f9Uw6lA74WQxM8KsZcxigYn3iXieueG0NWGmD2Mdz3PzC3fALNKEUAcVFizy8aXyU24gE5xCVFhFX02e'
        b'aL4CdkN2yizav6SnqSs1R/9eOpGoxOUWHDhk0oJuyOR0Cl2Aa2bYEAK5KStIKb5TepuTB4rMIc1dYYRp4Vghx/ww83nWy6wHKKaGwDW4jhVY6xW72SSm30ZTbJOnKiDb'
        b'JNgM6nAvnnbH69tUQzFziisekcOhOSponD4Oy2zJDDm5M4VmL4fAWbhMLeK7zQUPhRSPYhnUhUPDUiyVE/k5A0odIR2vYwHkhw2M3wnnMG0gXF9rPxBayEjtg+aYbZgu'
        b'9XAgrcgbivVzewfu6Mu2DTbL7pkPkIwTz02QWEUMnrljosAcwHgI90GmPoPtgDmUw5YFGuj8qXoctjXYolyDF0JYkX9s9hUKhWemCxERfv8cniCkUC8wHrDEAvoWZSaC'
        b'nRn5sHDlOjgAF0OxDa/iSYkH7MEzU8aS8SiOgCa8iEfCR2PlUtLotD5hsCcaMmPxBF4xjoM2qy1YDXnMWTyOrJfGrky7tJU+Ln5G1mOwpQ8NrYFqFfmfrC28YIItcC0l'
        b'TCVh/mjcFz2RzgByXGC+rzPZKMgAD5jcTyFzJ4u3gYVOjCdTo9rfICHvLjzSjZOXEfJmq8zicQ+cTRlLKzmciqVap7QBl3QgXunslY4jj0vYip43Fw9TlUAiiJAvgUN4'
        b'dA6e3pBCkTpGYysWO/nQ/YSFGZFFUUSK9PN1CeGRIN0iD3yItriBbpXzQ1wWisKWMMstZIKcSKGZQXBsGTTykADfBdqoEK2u6RMQzF7YdYFiEzYv8PELDHJ2CQrnVMZ6'
        b'YQhseyadfQJzQ3rBGaiATDYZgneQQ1vYMNJMiEjYPF9BjlbGzQMF8Wb+3HskFfCURIF1IplxNZifQuNsnEUxNFgVyLHpwxdhZrdIF4FM/fOQRmo8gLnL7YjeewVO+2Cd'
        b'zzC46TNsLNTKBGzA3dZQFmzFzpNxK0lLG7HR0kSBDZbYmLwxRSLYaOLwmDQYy/E0C73YMR/2hNKNS0p2u4t0e8eLUBfD2I7ghGOCv8qFKd9BpFUOWgljDJZqhQypsMJO'
        b'Qebx8W38HWvxOBSGQl4Y5oWTVdLH3shRAkdg90w2uvbBUK/cZCEhNR0U4DIUkJ0l35sfJa0DoA1zAsjKOg7nJZMEohZWDmMbcsRQbPSPduzwyimXiliTOCKFSTV0Lh/n'
        b'/mPmOzZzl8BRcyxhR80cOKDQOmNXSmA3nnbD4rHstU3Nknlog5EgG4KV0CSBUw54MIV5xBtsocZ/CxkcHjEC52WCmZW0TwwcTaG+PFs4Co1ONESHav0UlJ+7SI2EUVhF'
        b'naBGMXApMIXKe4uhBvbqtm7ycvVQpMDDIpRi0RReWQkewQYnrMaLOkefWazUchw28ePoChbDqXZCHrJxNEpID5VuYhfN7OEk5rgEYQH1eWJT+AqxD42S4l1aOJLMrhxX'
        b'Rm89QQWHJFBtti2FiiZk0rv5c97rIf6BEqj0XclP7Wt4Y7mOEZuuSrgg+LGQkRVwE0qdtE2EPDgB14JpeImRMAyKjUzGQCOLR7EhuzNpElfgIYu8NVm2Rd17Kgh2G2Nh'
        b'HFSx0RiHeQrqh1dRvi2ZyWQRzuBZuMBH+NxQa+oK1mCjsSDiJaiC/RKi+TfFLzf/2EhTTsSnipeGeYU+n9jbw6ZpWkHAqLIRL647cGNV28mZW/rWn3uieUpz3bWw1fZe'
        b'r5/+8rmDVtJXXzzVJyS1rqxo8fAbaeOHPta3eujLBbc3H8h+cdq/vmt9+o03JlhaF/kfOG0aLbuWdeROceWTWT7bnrZonerzzo1nPvb2rSg6vCUreM+9v611yN3zx/0X'
        b'XvGbMnz0u7ETa23s3309/+C3b72R7Ti89MbLFkbDf8GW88fKnLY5O7zwsc9p49vr7rz467BtvoXPtvn9NHvAIfuv4fm4iZYqxxHj6yqfXv919IF7RUfzC9997ZvSdWLV'
        b'6ZUxm7dETQuRej1f88J45aAf7FMtws++mvTOp1eS1a+O/byvn9e9ef13DdB4/VZWvt3o/eZ7V566EV71/uQJ01POfrd4wdO/3Ppb5eyP82bbXnzbQ71uoUn5r6kLvnD7'
        b'5Ue/+80/nZl+5f3bH/bLOnChqt/L//js3tBv9/a3rPI0j/8u7ORTym/9Rw49c2jQ4InBUVtNEssqf/1C7vtVTsCyxmuH86yNLm4cu6RujcOty2rTRGt7zevqxnfqn363'
        b'bc66fSV75nxs9sqFwmVlL77/6f5P8hfGD7ZYcWtS+N83DDqYHVn95gfTP5pXNbZmqXrboE+n/fiRX//Fm77/8krw0egm/2+zv173oWebZVxO89f+t20Hfx/otahu+qT6'
        b'zzbnLK19MXjSE/eOefXOHagpGPbh6lGtGYMPfb512Ng3ZJ8sScpNGDnU57Djttc+z66euKn+M3WDOK9B4/C+8mq102cHEutzNr+9UNa2Zpu0Tbnc6D1pjSQ17avHfrsz'
        b'bPrL0+/tinvn92GbPO+alNweqs68kjNgQlpBctovh7/KDE7u853KO/Nvz92Mfrfi7++1Ti0eJWss8x98+/c3ks1/v/u8n/HnK900zsVJ8bnKkftqllyyWGn6dtX2ZYvu'
        b'vPvFt03ndt41HmRu+a/bs1QjWfhAoAoPQs46PK+Lt9AGW0DrDkbPjidiIL+d1QoLt8/Ck5DL4jyIQHNY0O1iSrlbH+SRqyshfWznqBzIs2CBOdNnsKCIFc7aUECiDBDx'
        b'PQNbFNAkbrLHIhZVQTbEy3DRnxzbN7psrmFQx+NPKhav0dtbneEq2VzxgCkPLcoOJgJdzmY4pwvJ4IFDWAF7eUjESXJYNTixJtL4kHrYv1YcYoVneeGHlyicHF1VmO1M'
        b'jxovkyVk2adgDeuOlEVKJ0qAR4nc5avXQb7oMr8/J2PJofKev05ElQkhWxhrTBk2MatsdJwxjfWgMk4wE3Mv4RUu6sqFof4yrHDCNE4YRmSUS07aBsgpfRhcFMdiNpxl'
        b'gUMjjF3aA4eI2FpFI4dGYn0ytYVOD8QGDeQpNpqTf2lgX3swT0cgz6hdgdgkhxt40pJHMtVFjnLSi3DIgSPUAGztK4UTHrCfU9lfcCdv1m52Dib6SRHuI8PeCzOkkEtl'
        b'atYDiVgDJ4FS3bu5MNpCYyFsoGWwNC4Bj/B4rCPknHVyh8pgZy2NGplseEPEFiI057Gh2eA6sUMY2U0DuKg0Yow3+WRsHEYaoj1zVs4hJ44cL/Owoax5WN4RUIYNA9za'
        b'48mgfqrW0OA5oyMQBy5jta/Yj5wCZ5KZBnUZqoYZsOD1g2ZdXIk2poQ0tzZ5uMCY3RqxrUtIE49nMoE0WaoVZPOIouPQNq49/gYyg6EYrnUJsoErzjycpxkqtpGx92sn'
        b'tLPENPK/NAmP+LPJYe1MhJkcKHUJpCx0tCeUiSLRRPaFcXK/495GuoOSyNtnyUkJDY48PuwQpkN+h3jhuZTS9GWOZ1FRQ/Gqg/86LOwiW0AVXk+mvPN4kiyT/B6ki0Yy'
        b'skS62ARn2GDsGkGHtyOoiUpP57GhL+6XWffzZQYjKPYQOnp71eqHBABRexHu28FD9gpGxPkH+JINKURCBuMwkeSa2fuNxaYkHc0eHsPrjGhPGq0y+3cicVSD/otYtP9G'
        b'XNAtyy7Qm8woJqPGxK5GsTFyUcG4Y6wYbZFcIt6nOWY8Eohi2FmweKG+lNaIfCOSP7L7CilNWCd3SikFEuWd4YRH/C//nT5Ly7AWKeefBaX9kFpL+2rvMmX/WosUU9xM'
        b'5JFKFvw3KYtGEkVqXLsvE8U/ZFLxd7lMvCc3En+Ty8W7cmPxV7lC/EVmIv5sYyqmif+SKcWf5GbijzJz8QeZhfi9zFL8TmYlfqvoJf5TZi37xqyvXJs/Z8Y4/DoZ6bp0'
        b'FTct8vAlHlrE0s7G0x+TWeRS9OaOKIeOTK4O10ef/9mIqxR6LfRub6G6UNeo8boIKGbPLCC/OvZkz5z9siG6wwd1lUrC0tmCHuKHpZ5YCYMg/nN+WBq18JZoIGphVkwy'
        b'pTSMTEhgQKt6pMGkgfG0ZZEJnfBXOXZXVBQHJ4y0S4xO7VYoj4VxiIiYvz7ZNzEmIsJudULSmnUqVy1WbnscRIomOiYlgQYjbElKsUuN5DyLUfGUGrE7obF+I+IT2Y0x'
        b'DFJAm0MareGJpRww0Y5CP9nFR2kencWQIiF42vmyeAQyIzXxFI+W1ENjEyLt1qRokpPW82J1r+YbFRGhosg5PYZwkP5p7w/6MT7RbtNEV8qZPZt0YyrtzOS4yGRdazui'
        b'RAyWqH03BpLLwp14LAYpgELmduqi9hTdWHVSygaGqGewRPLqyfFrUhIi1TzaREt0zwEeNHYONEXemXQBqZbhr2zZQH6NTl7jqmKD0EO0Ce3Q5Oj2cdGOO4tGS+xKV6kd'
        b'/agkliC8gcIrGyqz0wA8hO5RIhiiezTlZnhIW+7CrfDqkXJB3k+0ILJFPTfD07WMaVgCZ3TZEUSkExT6yRFwGHJTKK6kfJ5Ga6S0U0iDB1FL6NWN7lgyYIhP75Ebd2Bt'
        b'CBHdL82BkmWzfZPhAhHo6xTTgpwHYzk55MvnwrWhW+G8lTuUYikzHM2bRq2IgvuGiXFr1yz25q2BG6sgjWnxoZS0t4Am2NDUJeOlcFmwXyvDCyt3cBbL7UY0F8MuTZqa'
        b'8LiRvRD/3sGdRppN5EqW6Ucjn5tisdfdyuuViWt++Nr3WbHwXKNV35k/mH48rmhW9Wzpi1H9/hW0d25qSnKg9MD8c0tSX97x3aw7gXufStT8uOhX46DJT9T969PQ1JCi'
        b'Xs+FRd+LyNy7YqdpzqECXNjY9reffQ6/lFftHbdk2snDy1bPbrwnWbpnwKvrpqmUTEuIg7R1uijzYyZ6is8hKOf6Tdl0ONqu+TjiyVl43jvZk4mxm+AoF17ImJx7hPhl'
        b'5u69hntZzQNnw24Ntdi6MLbjpHhqruqFhVKom+3DBJnhrtDiFBTh3a4hMe0oGm5yMbZyCJ7loffQhnuIKEuD76HahikHW7youYpH3++Q0MD0eXjKg12KxpuQwTSHkKB2'
        b'yss0I9akUKiZ2i2PYiCmyxRwdSRTE4xdd3SRc2cr2yP3vUmH0SkRjxdC9aRcfQnXDM6TKRmLF7X+vIeGlJjQFEC2SplYQ1PWuoo1RLCZxIiERRkTIiykLNRZYt01lkBX'
        b'VHs0iw5s4wGxDCqR39FxsB4gv1bKtJRHXQ9WYbe1IY9vDw2hsaTkjFlFDplOaAntCbM9RSFKM6WPlC5LGYR/kRk4VUOjE7Ugqp0R2lM0/JSNZvsc2ZS9ZvvOCdVDXe/p'
        b'aIpeHb9Gs2pNQjwphZPstsNOxVAYyTVxruwOVy/6cw67rScwd71StX3jyeIWnXWBixR0WBPNmpmkjqJfkE3f4KasBafvsQ2u88IDIhjwXMqGhKTIqPa3b+8Qg4VSZFMd'
        b'kBw9L7QhvZqU+GQOEa9rlOGj4qGtmjMnLML5rz4a/pcf9Z3/Vx+dtXjpX6517ty//ujsv/roYq8xf/3RsRF2PQhUj/DwuB5CR31jOGMNF2+io5ztHLXT37FT/GnnAFkW'
        b'NGdYHukp7HWeOpLhd3fM4T8T4bqISrB8V9g01tW902phkbkcNZcvJ1LhpvjIv9ZTs8PCDTShg4Sb7jG8HXy5xUc9ROiSCXrcsTqhqzfn2N681VjeJCGHrl2E8zEXY4G5'
        b'IXYm9NcoRerib8ETRA7whGzm1sDaIXAYG93d3Y0E0VfAvViIFVLM5T6KXDyY5BTkSl2EB/GErcQf2qCBuXvmwwW5U5CfSK7sgf1wUzIpEY8xBwMUQQW5RI0ZkAmVkC2Z'
        b'CqWQppKx+nbAATjBPGXYYCRIB0iwBfKnpWiY/2HLCLxBrtUlYws567FUgsVwYFg8ZrBXUEWZasaQ806SBEewTYAWswGsKSvNQjXYbElONBHPSqAg0BEOTmGef1J23Sbq'
        b'+RfchImhbqvxPHugt90QFspAjVgtLJRhELSoRNb6XnCFSKN67Quxm+aOp1nzRDfXTq2DE1A9DM/hYS7r1g9M1GsHNjg74vWlvB+bVXBc2/b5NECjBU+THpGyHpk4D4/o'
        b'VwjnsXGaKxSyKuF0/PbOPZLtOgyqII3FkYQN26DcZEImgNREgpVQ4zYeDnFPVi0ZqCtKc4orI3WW4AWonAHNcIoPUBvm76BuHqWFRJCaSeDU0BkKuJmyiF7bP3GTPxV6'
        b'Q1ncL3UpEylYwFNwYDuRsHMxPXwAKboEysPIryXYhqfxABGyS6DN2ghLVxuZkx+UATx3ql1vIiVaW8I5PDIyPtxrn6i5TSqoEr5a8Tf/dTDTyvjbsrd+yfzbufnf5oQV'
        b'7hRr/3Wr73N21iNvh1y/0hqW/vWzjbcjfwj8reA7qyi3xptbPCpC/Zb4/uoc+tyzOa9WJHzoEz1814dPvjT1zKmYNXcChrftn9CUkrPnu/J5Rp/defPG2injvk3yXGkS'
        b'MDVj4azW72xuBZWronzfSh3/+o3ooZmr5676xOzrQc+4zu+/zXWzb+pX9r9ZfPXaRePf0lOcnv809faIryu3ZZyLbXnmp6E/2cibXpJ4FtRFvri/bqzzlltbd+dVNK+M'
        b'/Oi5naOOlBw6ONnb6YfZo//4ZPPvlp5jF+4fOFFlw6TPyWQU9/gHQD7c7Gzuh3rI4xbxK2Z4Xc/gL4EbdnAUGyCNicT98LrGyR/TZnTEQ5s5S40Vq5gcvxLPQYFWjsez'
        b'ZFrMcvBiAjEenLLUieeIyiBdsqgv7k2Ac6xEO8zp155Jy/Jo+8E1qHeCEzyD9LItpDlhzZqgThI6NsIh1lwfyBnn5AqnqSOAyr8KzBFhN+ZhKbPRwn5PbNUosYk6nHOk'
        b'UC3QNMPBzMINmXMsIWfDeDL7MQOq5AIW9hnKrogz59MLcnIhEy6R3adoCqZzm2+FCi7Sa7S8LDyE+wU8IOf+nYRUUZvK2pGciulWc8nesYc9PIgomWka5vyGszugWMCj'
        b'ZPuqZNdmBK3RQC5k0sYUQtYcyidfDDm8oXmDx5HHjMhjVVgySMBy2JvK+tvNZBRZ2mZE24UajbuAxzzxMO/vY1gE+zWbNtK6DtvKyJYJJ034K5TFYQG5QvErDkLpUoF0'
        b'PfV3sEzMc7BnElOYsBRucKWpQ2XCS6k9ZGI+IBpapiFyMFMsogwqFlYR1NZpwbnA7lMrKLWdUpum+LtCJjLWj44/lOyY0cKLppLOf2REIRHJdfn9rb06hzeT+ttxVlgO'
        b'pZm+IK0u7qSbsIhF8joHdfpIsS7VsZR8erxnpcTqigGlpKemSFgskvpd+rlfF3SrW7JVwb5Bt5Sr5oSHhHgFzfH1CuVooDrUq1vKDZHxie15kDQT6ZapXqIgs2HqUkP1'
        b'sjhzO6NjMbAsasNk+hZ7P966Af9fMr6rF1BlUKqdQArBythUSoHb5L9byG2NxJlEK70vin8NlNNKZmVlIVKCOFE24b5ii41EMdhGksLyNQ4LUNORq1CEJ7jdQSIM8JbF'
        b'W0BNt7BfM+2/mjGSzqRxFNWLI3qVy7SYXvwzRfYyIX/oZ4rwRfG9+Pcdn60orGZUb/bZJqqP7nPfqH7ksy373D9qQNTAqEHlSkpHlyGPkUQNjhqSrqCwniXGJZIoZYlZ'
        b'iaLEmv6JGppnbGJvMjzKI4OihsmJvjsiaiTDvzJmVG6j04UohygVpaqjz5YoS8QYkTzZm/y1KrGO579ZkxKtS0xKTGNkUY5RTqTM4SbOUWMoKhktNcMkwzzDOsMmRsFw'
        b'vGjpJizyVs4icXvFyKPcotzTFRROVCYsVbKkx7G3rOlqmcOoLRgSXEy0+u6YThJn9xu0bGz6N911JeKrZ7wmyVOTHMX+HePuPmaMJ5WCPTdrojzp6nF1d/cgf4l8PVYl'
        b'vSULCg4JvCXz8fX2uSULD/GeXy25Jc71Ij9NaJWrgoMCllTL1NRgcMuIaZ23TDgGcDz5aBRDdGfNn6nWg1YrU1fQJXec/jhBF7HMNyiUp539ybImk72tc1nq86zA0LkL'
        b'Z92dHZecvMHTzS01NdVVE7/ZheoDapoW67JGm1bouiZpvVtUtFuXFroSrcF9jCupTyV2lF8tMigydTxFWyQdFBA8Z1bAKqIm3B1FGz1nti9rIfl3fuQWuu+FUMOxJpkU'
        b'6uo+jvwkux8trFqiXsQBG0/TtpqF+gZ5B3itmj0rbI7PIxblQbbqik6vfHdilwfnqJM0mtlMf+lcRkBSbKAmlpXkQUsSO0oiDWygZVl26Y+7A3p+qbt9DHaeStmpFDrd'
        b'1E0Gyp6sbqHfdilkMitkrLqZXuu5co+7Tn/iTW8ZR0XHRKYkJLPuZ2P5/16OCdMXUvy2KTeNd9BGBeIFIvnUxsdrToos98S1egTLPVkgBhgLMgeJ6tCEB+Se3FJQIthk'
        b'MqmZ0GEoS44loXhzFNfOm4lr+7M95zDcIG8xjXzSOBiUAoTdZtcMyAEPqqvamJ/YGgPHdoru7KaT8wvalrCgbpkPpu0dS/EFWOaD0E5UynHaYkx1WQ2mj5rV8MEeYwNW'
        b'TV+eaRy/NVrPtsnZiLjriW7JD7BlhrazBdttYNwQTITReHa/0cWuy7Kxc5jrpXrwbXTZPfSOyXYOjpp46sfaNNF1guMjFMlXsp3DHJ+H36xdsfRmZ7uH1dPzbmLn4Bv2'
        b'p57weMATj7ox0CK6Nrons7HW9MVtRDwJXMtD1c5x0NOT9PTkj3WdNhvU8Unq+OQtHE7YwZGeyZThi57KjoYtiY70rKb30JPTkZqNHemR56hy7XC1TnAd4+ruqb3FcDEd'
        b'Xll3dqu21I6vJ7CvedE9vRgHrNC+mgE4Ct4/ozUMkaLH7mFOC8/OKAJskRkGl9CiAPTYpg4ECU8dl213kAgK2KBzzBvwu9P/yDVGR0gt+cyCyoICoiOT6YTStJO16WFu'
        b'ULd0D1AE1ApLykmNVGtjCPQ4Mljv2IVGR9N3TUnQ438zWNScWWFe3sEhS1ZRMqLgUK9VlIcmlLVS57/nrHQ9dhLfhHj/MN4oLYRL+7i1q29a+7Fhd3eHTZn5KXgJHSZf'
        b'xy57imOPAQNshDbwdarhnHZdthhH/nbtt8QnGsZJ4GgcRD5tp+aNi0y08woP6cE2nmgXmhqfvDVancAGLvkBjecbYg9riSwY3+TIhC3swZ53OMee56wWRoQPSAe6CJ35'
        b'2iHRIY1wN1UPb5TM4x/08MY7PdsJJabHXYuV1M1vQLpHK0Rp2qdvl3INj4mW5rGjXkavuTo6ISkxlpb0EPs6lUpMuklRlkHcZH6u/wIs9sd8aqxpGSeIWClxkMIpbuo9'
        b'v3Aki3gYhtluPORhLVzmEQ/MSnwSjsN1qF/HkU0ZqunwaUwTXoAlO+bAUaoLQy62kD+NkCUTzDFdxBwsxTKWoQZVWADZsd7++oljC3uEAm035/mJwnjYa4HpWItZKpFb'
        b'iaviiAzIDcE03pEag2cMAK05+9I8qGcWZNLgEmpFngHnvVIoa45iNuzXQ3vtaIguk2aDuXkIxXt1WLHRJSjcwQGzMdcNs50pyCfHL3WhRr9DvSVQOGMe79VSbB0AGeZa'
        b'aFIGS0pqPsFcGu+5y4WLEdylYe+9iueRKeJNdFilhxJonpCPq18gZpH3dgvBzIAFPtIQyKL5dtgKZ7aMFOCmTImHd42M7zOml6g5SYqof2vSyLx6iz0zzfa/PWRD6mMJ'
        b'H/pPmtLQP3bimg9fdb8t32/SN+vZfy577Oitv58MvFH79fujd1v1XdJ/T6Zo0X/q9y82/ho0fWX/nacnFy0b2yfl6AsJJev+tWFH5a9PDP8pI/akV8O3l+7EfdBv+PkV'
        b'//I+OvkH2RM3j8bFjbN/5/da44963xvQ9M6VGU4rFK+W+i29Hn1858KDG8Yvspz4fHXovFt+fd52u/yx6/EyB5U5MzNC1ihodnJ18YmKYOCKp0X3LVDMohggH8rNOKgy'
        b'xYJ2XuNMIzaMBYsQqYcSTnPcybO4D9I6wtMVmAH7qHl3QD9mrd4A5TTKmUWO4OVQvZD5BDiWzHIo25YOtHNpjxyZhVXTmVU4WYU3+ETc76yNEGfx4afVPBB7N01k41EY'
        b'eB6vdEK03LWJ1W1PVsO+dnuuOq4DbhCPYXkytcdJYS8264EXFgS69Ma9+uCFI0lfUMvwTGwazTAmoRZbOuFMTlzIo+QPiu5am/tKSNfiX+IROMKDiQtxjz2piC69y9I+'
        b'kwRpoGTeQGjlQ9CqcIYSyCfrPoB0wmqJB5l8zZ2wKkz/LfObDhNvdg+qlPV2aoKTS2lsqylFyKPGufsKUSbhEacU3c5ClIkDaFTrfcOqkD7WnXqjxJBJeVMnzLnAB6lg'
        b'Qy48qgr2F/DnjFYx6L2ewLHyyCeOPmeoQh3ds+sjCMBdkeOonSrUZ1bILRklc70lo7yuKmNDQbU8ZJVGsN4y1tJ/q5+UGMiZt2w/TOYLupx5rjuaabVHc47znWEZY/nn'
        b'M+M/OGdIh5wVFaXpTGDdfoYaMO/ppK/uqmiMnSeVDT0jdAgmEQbc+M5aWUYHuEVDJbtHlnYlY+RcxFRF75BQk2lPJmvl90fSjLQyrY6u92HKEWfr4s8a4NSN1NjFJCRF'
        b'UquBHSOP1bJj9hRDE5nYiYmuKxVvT63opDEYYspNjt7MxeFkHbnseh7m2UPcJrknPorKch1d0cHnx9/BzoGRzNNXY7Kafcg8V1dXe1UPUiaPhGAxyJF0NulRTOtK5hya'
        b'XPrtuG6wPN0zHZSY2imgjdLqTJBpsAyHEK95XtRj47UqKDxwtleIs127UsJZRHuM7GJBxz2zySZt4EHYDyhhsyE9rwfa1gcUR//TqYG0hx+kpelA4LSz2mBp7RzhhhQ6'
        b'O9IrXiFBswK6K2+G45QfUaFrp/XiXaFjV6YTVjtv6LogOnA0I9COiAhKSqQ7xQMCuDcnd9TOuHdpH0Um0KBpukHopm6MOmk96aqoyB4irRNSuN0sNn5TdGL7zCdLM4pG'
        b'9DisSUrUxJPuoiWRjotn35Je7rFhvBh9a4NK/zW1XNOr10avSeb7gWH9JjR40gR3DzvOfsvfh7bBWQsfqn1fpv7TtUk2RYPlxKSo2Vpjq52z2Pao5PFTydMuVKtUtXPP'
        b'01j0LaSWhASy+CLVXLXiNxveWzSapDXxbBB0Kt4GdRKlkKe9SLpWO9hkIfBpb7gz9ZgZ7YKIshe5YUNC/BoWa0i1bbae9GPrDa+dOVoK+w4mWHpg2zmQnypnO3ps2zkE'
        b'h4eo6GDQ49vOYbZXUA/r0FEvWWCCyvERUhh0gVuzdFt9F1alBwWEdtI0FQY1zaFc04SLcIJCJ+TYwFWOZEPUyRnYwEQhphjt8aYwLoKV+/rIBP8lg3msV1isufUcPf1y'
        b'CjbO45E/x7B6Hg19grOLBQ7iAqWwl+l7MyBTYNgvUNxX4OAvYdAYxjRTbziLZ4heOhpzDKimUN6fwSpgOdyMxhwtmQOl+gjTohj4uzgu9HH2Cyf6aRzN/TeoonJ4mFqv'
        b'XkSZ2YNZvANaraCCaah4EfbxcKUZdkQTprgSeNB80sOq61JXB0sOtEHGAgcdxIVKLni622Bd2CqetH8Fi0cR5dcigQdQzTBfmZJK23O5t5M/w/1x8Qumyi8vwQgP4D7T'
        b'kf2h2rRD4ZxJtJ9ycuGUNdFvTofBiagFkDV7J+WkgAvkTyUNnFu3GQrh7OzVK/thEWTPVscvWLB2pXrkcihbF2clYP60QVC+MoJFrQWNXK7E5g0hWGImCiK2SdzCydBR'
        b'DJdBWL6tx1ZhVn/ImolnsBiKVsO+Tk3ah6ewhH6mwV0RlphhR6bcgl62Ip5i/qIQuEoDzIgex2PM3KAtOiVSoFF8Z0J0FgDVQi2+z4aUlDAs3GBuiQfClozQdrmeeYBa'
        b'Bei4tGOAtGPhwG44p2BxbBaY2Rcv4aXRDKJyXYpTN/glfXQhxaYpM000YZ1GEZsgw9x7INaneNHxugCti/0pPELjUh1PUh5cnM+mCynXnwGSkDlUbKTxg2xrMq+zsTiE'
        b'TMFsCd7caO49HU8w/iWbBQp/fbIlWogPV0YpwVKVELCwU3GwTwklNiPxbB+ogjN9+0gFKAvsBWdGO6dMJ8UN8R7BXq3zG4l4EktIJZenkjHZg+mkV8vxGtbQ8Do4sFrA'
        b'jBCzEKidyKwwmB03Qs8KE+Cr8nNx1dKadAZh0jbJnC8RyIZj7cuE9NexFGsoGguNKZQKGaojsK0dUmKBT+fSyXy+8kg1dJQe4mcDbXRf4NvPmbH2w+FyJwtPIRSxEB2e'
        b'gFNNOv44I93ZD9XdiXfwLGRQTsf4H3q9L2gOE0Xr+YjnAxdcT3zb3WqUasFll2fzjx2f4Pv0qW0/T5/5s7AyT8w4Wyfpd8LabZpLyp7lB08U2K0fck+2ZW9Q/zEx3x55'
        b'+hnveZKGwp9/f+e7bxykvl6XAktzZoe90Ov9/csm7h9X9o/XTB3Kqk47tE54+vw/vh/S/1yzx8VlK0YfeKnPmfJ745y+vnng0t8/yRwfrfzoZv2wfolf7g5c0rjksGfp'
        b'6WeX/vTbb+tG2frvWOj0SVXChS/2VUq+/Dn/taX3X8+8W1L5lFvcjBN9ilJeb4168UR4S+KvI7f6bbatMK2I/HHxABfr+8ab3W5/MuLuU9++W//TxNujXzn0wg9fWsTd'
        b'3PbP9QM++edu05BDt5Le2m/7U/O7CQNvv5o06VLzM9M+VysbDj3zUfDcuhetv9kWlzFrTuyUzakbjbPef3LR/TnTvtxqe9e4vPLLXu9k1CyNOP7htPObbs/YtL32rcqP'
        b'Fv4WW5/SPC45JLbfmt0NE16c++3wA/7Bdz+ctG7F1080HP06dUvVpT+qfk93eenees3uopD9L87KuYQ7bO9WBTsZfTIuYKzTR8m1L3xWl7fk8W8CfqpdKRwsOz23oUzV'
        b'l9mHkpR41H87XtdDEKD2IU8o4cnze6Lwsh4vBjM6RcE5PIhlWMpj8nKhEC/AgdkdtqeLyRyc4ARmJPt3QlMwx3NksewljzKLYjq2xjNrzyV7XZDl0R3RHFHhyMLROhqV'
        b'cW6USEVLowJHVrO2L4sP0DG1cLiFQVBGaUrGcLtbNjbhKWrbwkz/LmQtQVDIYzxPhG5jQASNWKAXVAl1A3nQZH5sLxqsuQ6PaOM1ce8CvMHMTYHOQLFxFYHBvnBRJsgT'
        b'RHs4PINbomoSyPnSvEWHU+GGx/Eyq3CkfBpZQZfiu0RHzh2nZtlM2JDg29mQhjcxW9+SNt6RR4Nem+Ls3zltnpxPzX2GwzGesFUCGVBL7nBeCVcpu5zMWQJXfeAsGxkV'
        b'XFtMTlk4jBe60L0M6s0NbQfJjl3m5GqGNS4+7QZNSAtlyAKm5Fw86h/gC1ld0s7GY5tUcIcrcje4yKfXNKh0gZzF2BrMALKCiQBhMVc6DaoSWUfFQtNmJ5cxS7WULjSn'
        b'DPcHs643xj07IcdtBRQFuqhIA6aJdlCHGSrFI6cwW/53gvAK2qEgS6h0aMAKKOwynW4msRCtRAuJGfkrF63IX4XUWmJmRWM75fdNpTKWza6QiGmmIv1Ms9RF7fcsb160'
        b'kbL8dvLXSpRr899pqpmZEU0+sxa5pdGC2vXum9FcepFmotNrW+0NmNv+ZC56h9lM/UznlLVH73/9FPJnDOSRG0ghLzRqT7szYMsUdjt8ZsCa+Qhv23NQDz3pmZGPh4cI'
        b'MXJdeI/0UcN77kZ0UyBCohOJ7qp5mCWPmQ20qgpVVCM1dosDAx6ij/Siwkk3fcQ5iPHD4aFBm/316SftsbkLbF3OIoduyaJEALhk3mfmJKZL9ErFKiyFesPUeimQxkWF'
        b'dMiXaNZCo56ssJhcZnQ8h+E6VlEpItmV7Lmum8gPPxqTDkW9Rqw0mijYcPjNm1PJEVGM+70ZvOQQAQrVSRzmqm3synYHHkVczGUePLioZipVRbRItrMxZApHBPRSTxZY'
        b'YXJT3M+AKsmuslWCFbT0NSkcumMmEZlojgkp74yb4Ea+4Q60WiLqn1OqoMRETQHfqokmJsTypt1IdHRSOZLzQB0l2yLB3dAA9ey9sXUH1MXG+lOXSZCRIO8rmuE+OMKe'
        b'SoBCdz+8EIp5Mkp2KEABpM9nV7xVai2unP8Chix3MRbaWAaMc/hQngXSZypVY4hOwsDjyNA0QqkusUS5mKaWDIPzcIA1fYutqy4jBU+slw6QTMOb/ZhmtNIP65WMxRHr'
        b'NeS1HIM5nBnkLBzbnlMClYFUT4NKBeflOw0HvUIhD0vC4RAVnbGUAtYpgiX08B/OOl2U5QuDFqyXCe4Rib2GOnDl9t1xw4W5g/qQ5RSxutFsOf/yqNJHKHReLlL8x7bt'
        b'/kI3Ymbd6rMTtMTMSrLehBPCdkmUECXZJ/YXTrZTNMcQafILavKnfDezotQB8YnR1VqSZlkC+aUryzS146+QC8IPIlsnzCPrjwfMWAAz9z6a8PmP1yDf3wUPOFHBRxIy'
        b'YTK2Ej0hazLu2zRzXsxGX/XORNg9WNg+xgrqpbbs1f6hMRNs546VCPMjnBNWzeXvO8avn+Ac5SIT7CK2D188RmBLQIG1cFMfbxCqsFqLOSgNJod6SYqWPa25H1Uaica4'
        b'Cs4ypRGO4FHtiI2DY+TiRnOim5QskNpIpvSBBlanMsZYMBv0Ga0zQRPcX1CJbOxjsXkrn00J45g/uKIvK8ktAPfwPCS8CSVMTzwFZ3glB8dgBjaSp4yF0eT8HiUhp3OU'
        b'SsKmLVYooVwTHRZE5UJRKaH5L43/9niqn6c7/wv0x0sSoRtPOB3BS2QE1S+Ti6wZ/RIwQ7kJmy1ppkYuaf6kAcAxDZVwjCgo50yVVEUh6wrK4BJ3nU/CG3QAoNnHDJuN'
        b'yeouJtd9sZqh0Mq9JUq6c2LpAmFBABSlaAG69nooHRyd8AycwfoAsgD8xKUyTOesnE7zh8JebHTzwxZyyQj2SvCgx7r4iPg0UTOZrPfPZ8VGh/smDAq3+v3+z3f+XlH2'
        b'RNbXG8snPR8xJTJw0GgZJD7mbLE7feQw+exsYfAHFT/OnXzi/X5PFcolA9Jl77zqMiLRrt5HMelj+ewPH9s3xWH57ez0SRtuh6dMbCieE3hza+3O3y99GRyW6bfj3Qvl'
        b'oad/uzt+cOnUwQPHZFmE7x98u9xNGHjh9/xfLPr0jli3vI9n2Opv2kyLXnH6ZVvC4++bh6UvPK1enD0u/K6ns7fc+dPtoUsGO8/7wjn6/Kgjz63fl5l9Kf31T7ae/tD0'
        b'4pFzcyctxLVhRxZJG5MnX3xr6XL/sMUtI5e9XwuvtnraTvzArMZlWb/lby38aNjHcY8daf60yXp1ufnl/LXfrygoy9g7/fVrTh+PurV20a//3PP+zDnN00+N+XSO+8Dq'
        b'yBWR2ddzFraeTy1K/fS+xfq5p27smeH34liLwuynn1h3zOPxfq99udP3q6iPU5fkfrdrbsDACRVjH//5tTt/zPyq97G4D/b3+klpP2GjjflYtx+W7/fcvapP0ktPBdcd'
        b'tLm9vv78z1Upe26mja5/+9J3E249tvbn468Pee3rusG2b39XU/Sr53uvzfwt47GgZUbjXN/Jtevzz4BpIZe/S/n7p6G3D3+V/u5InyffODtk9byFTw5KO/DUCsvoceGP'
        b'vVv40rMLXJ92WTm/anzegm1n7J/L++HKk6cP2z7xnuxt87eHP5ew09o2xfTOyjrN7UnqoQk3X5cObjNNHntnpuf+p+JDPVPFpt+K6lrsvpm2MvrbvvZJgZNfMf7W8tM/'
        b'1P3fW98m9ws+8pmbRbLbp2X3kk6+U/G+vXrHS/23HV/y+OX+b9344PPb627ZX/n03d1mKWE/Fl46eeCnENsJp/as35z6r/GBfvnH35oSCTFvLnUtNj16x/+nljuFr/2w'
        b'ou5a5M8zyw71vt7v8+kvfGtcG/LSH0nuP//Q70txzQtfzfT4Y3pOxcdJt47tmf/0FiMcumwFSnvnzl8XcbVy+dPrHFO/2pJrcdZ2zvGz65f8HmT39Dvh47+8/UTuzcIv'
        b'lGM+K/Uov7/bZ4vl6ictt1g+/89B63c9/Uz10W88Wrd9dPxjTcZVxY0PBos/mB72vlLz1qFlazdnbHz+qV0D71SGDLR9q7HvFLOFv7z0d8U7rV+ozQe98HvC4ILotyw0'
        b'h55JNX1r5/NXn/jluOlEzLw24qd/JGd952ZyLadXqu+Xl76w/uj+Eyvsn+uz4sBLZSlZ3+0qdX3rcfL7l66TD6RmOTQuOTZmenbR/dlb7t1/d9CLl0fL8//mdqd4u/RO'
        b'7G87n5tgHFTX73PbO5PuxL9psiXLc0xz1i6x3OSp1MdcXwn7x+6/vTlq+Nt74MKWfzS/OXTSim+e+uyJv5u8tzTPdNq2L+5sbPvb6Kwpd7a8qQqTPGu6MrN851b5vb6H'
        b'5oW8ULthMlbVbn08ZuOm4u2bvl05d4XnH6Obbz83cdrAT9+Y19wnsPLGsdvmRx4f4PbyS21vLKgO+vbG3JuyT6Sz3H54fu/2oZ9Ntfrnex9M+5f5/e/Xx/Xp4/LHF5cb'
        b'St/0f61X+IpfLT/5asq4H99WrWN4dxK3EZ3YU2LhhI5ABWvxLGYxxU5ug+dYnMhEoit1ZAG2rGCKXXK0FGvnGWDx3AenOdRbiSNF1cvzV8El2/Y7LN2lsVgfz29ohAOx'
        b'WhV01xw9DRUvqBj+3AQ8vqKziuq6Awv0NNRZ1sx0ECWOhgLca4AyEzKhiul4O+GsMgiKO7ANKbKhn4wpuL02EwmSSrJh09vTjczxpnQmHLFnmvJaYbjNEI0rkWFd1EEq'
        b'eqQ3sugazJIK4/CCPNSb6OnsiN27fdsKuOzfboWQrxIdsQHzGEGpn/Ewf6yEGwGORE9fIZkYq+WvnIX77In4VU9Gw42IzrRpBeLIAcjDUCiwyn4K+ubtwGDfGOQbVCSx'
        b'hs/GY9iixEwXrF+zDnP9pUSVvSwGk5P+IgeaPDhwHb9sjNfIdWwkxwnpE3L291bzGJgbJtCOVQv74ahsggSq4RJeYpVTrONaXkDCZhdfUrupuMgEDrFOX6+00NC0X0df'
        b'zN/AMkkLgowFK6iTJmPhcm4ZOA/XR4fDXn8tMacRXhel5Oyr4pCGu9d4YqM/NgQrodpBLpgQkbMIW0Q4A/V4kL3AGkovqqFIkSZEzTASTFWk4/NpBNx1PMPm0OpdeJ22'
        b'0GQS7ldhHesEc2iT9l4HxWzgV0PGam0SLNEVTnLDisSOFb8LzhmRc5vyR+c6uapMHRyp+cLaVoppXhNZD1hvW6h09cdmGzivwhzSARbiMsiDem57OQ1nidx9OFITJOEi'
        b'wblAyGEGoR1QoMLG3oHktbGeFY7ZRkKvvlIiNRRjqRbScclYf0Y26uDiaGvEIYgHwh4ZnMWqcdxmdAGPrNK4+kJtChw0I7cJgoVcOgOvu3CT2fWJcFrp5xKwES75uAYQ'
        b'aS5Lo5II/cNk3qGwlyWrmljhOTw1mX4t4A0BWnvhHj7yp4Zv9ae41yqzYAazaEGktamQOYlfPTx2BkVp1Ljo4TRKk7ymc5jKqyMTNL6OKlHYuVAKJRLI2wZHWX8FkB6p'
        b'wzTYR5ZIjpFARB8yGU9rCYMXY120vo0Ozm6lWdDTsZHXWQxX8HQ7fCOcWSobIoFT8+AMv1ow1a+TFSrKlMI3tszlNLR15nhE6UCW6MYA0ixTzTY8IsI1aDPjxrUGTyig'
        b'72OONwJdJIKJhwiHZ8WyJkdA2jSlq8rRuj8ZKdJmRbwYT+b9Xm5XPOWAV53I0Lhiurkvx122hDzp6l5Yxks+vHPdSGwjVW8MoqJalQSP48FpbHlar4FyyMDdShVZHKw/'
        b'jPCwBJvgxAZtJ5OxyaWGMzrt/KCSGc7gaCSfXVewaAaZ+/RlJ6yQYpYEKhf6c4vcKWzC3f7cyi8XlDOxxU/EKtLrrbzgyy54ng6QKWSoAyhkg7mbVGFLNiLW5ONYuBYv'
        b'wUG2HQh4RYAaU9Cmbp+A01hOBkSNl6XCzFQRbkgGem/l2dJYOq49Rx2OLOQW1NQFLCRw7RCpZgLu1wnvs5bwHf4yHITdNCgQbnrrG33x8EBuls33caINVQe4SQTTNZtm'
        b'ilCN+bCfw4/ehFzZGko1kUOWfSNdRlRXJY22IVsvHsLLS3lk4R6oHK7BfPK6Nc7YjHkOKwKxgdzW30rm2IuzbZPN7dLa6bCbFJPHLxotlGA2nIRzHAyrJnqqv4l9hxX1'
        b'FBSyt/aeNWAp5FD/zCZslAmyXpKV5FodG6JIyPLWJGIJQ6SXUJKOgslYwIegbDlVydwwy0Ekb2khxQpyQ2/YzadrERaoSYsd/MiYtaQ6ioIxFIuT3eAm37czg/rQaNZg'
        b'X7i5jnrG2ASxFKVRPmSdMdPAsY2+Th245ZOhJFZqacapx11852vYMUW21S1kjvFN0RYuyDwGLeKdUQ/52OgZybd2pmIcJfOWnJ/5rAQHMm4ZvMNVrK9M8bgPNpHJsBJy'
        b'2ZsnkIFogxwXOwZ+Ki6UuJBjpI2ls4szMQcqoU1DhtsEs1LJP6yO3lgsJYfZ2SlsC1lIPtZwKPQwLKArvVLjzIomc4wsxGvk4HfTmWMtzNgRime3w3llirmJKHibSYdJ'
        b'ZtnGc+7v41t9NAPGYi71CthIhqdADZt+G7Elkr9GX8zw3cium2O1dKQ1Xmej5Os9kYPEU7RXuidxjPgVo9i5v8s0dj1eYLBgbpgd6KzyDSSbtRZVedJUOZyavYr7D9Lh'
        b'AKQz34XPGqzqMD5jIaYlU3h2qCTzspbBI3cgtKtmeHfDmg3HGoUblg/mJwTZO9VKOLKEodK6bGRbbi+yMqFyKR7jR8A5sutTOmqyr1ZAqz6B9hbtCRgK+0aTCaFdY1AV'
        b'4iXC+ZnRXGK5SQSnY/QqmaW1UCCFgxLIt4xjs9QScmzpJThGZivfRsZLTSh0NuueoUSZL9IC5mY7d8XMpXi5xnNZ9/iTg71RuWCF9i1YZb2wWQqn7aCJzZnJo/06IO5J'
        b'L0ITHtVB3BOhgKMjS8mWWK5kp6BbHym2SODc4BV8PV2ijEpKzCbTGY8NYBNeIYgLFKP5VnpqbRLZ4v0kAuwTpXiZrERvOMY424kgUTQT0sbQ9zT1C6SzhTxrA+lSzCR9'
        b'e4kHPB/H7CGjApUqIjoPEHBf4C4eSV0ye4wGytYHYb0bkR3YTm21VgrZ28N5x8fDDWx0dnUVSQumS7GMHGf9oZK7srIisFiJ50zpChBVkiF4iBw5zKJ5jSzOfA3Z3DHL'
        b'hLwRXCevXc/XMBbKPKM3sMKj6AKCLKxSurA3kw8Re2OZF+uO6XgM8hhdThA2B7g40nlNVu9B+3AuVZRhqYfGzZHsDIcx20dFd5820WcxXGNzYgJchDyXsdjoEsTtDzsk'
        b'WIrnYthYbsObgsvGLuDHDPhYDuVsTS3DpqUaV78UFVn8RGIb2F8UoQSb4SCbrxHQ6qIVn+EAnvW1dKBbmzm2SidvxL18MPfhjSm6yGuBzLJrNPZaRY4oulMvM9rlT06V'
        b'm66BZKfeIplKysrgZ1cROdT98QRW6KKyScUcsQSPYLqMWd9W4+kOyJI4PKfq9d9BtZU/5LoWjIJlz8rVzIjPXD1LDQAct/9ROCoYBDCFMqY4gDKGBygjWx51xsgZqDEN'
        b'BucuHHpNQe6if2zIPVYS8T4FLxbv2yoGScQfzCytGLSH+IdMRt06IyQjxAHkSXLtLvnOnJKs0yfEezK5jFyVi6Pui2kWEvF38b6VYggt7w/586ZTrERKzE7hjinosZXE'
        b'ltwxSG4lsaGwItJBtD6p+Ku1iRX7nX5ra25L4ZolDuQz+c6o59rF+4OMbCW0XAZVwgCbbUiLFHLxVwsT+b8USvFH0yfFX0xDTRkwMoVGNpPYkZ+jJLRu0pY/aHvF3+W/'
        b'KWwUkq39DbhweO/rUQs+ZOz0EpNfIaM1SE6GjdK2GPYkCbv73jLgS+q5IaR6lhT/mITmHQcFqWTkB4skrzbrglqiThBY8nXoHB+vQK9QhlPCkqU5bIlGhzVC26mm2J7c'
        b'G2fzP0ETmaLrpqN0UlOH236BRrnJRFEuchjue6Lxf+6T/AVxooVEYalg6CSixOa+OI1jjtjKLOh9f4hSUTLkvrBriGkKzSbBvNleXa31eDmcBqyIwtSlcszeiDe7pdSb'
        b'av/VWD8Yc0QapdB+NtH7bEo+K6PM2Gdz8tlC+72l3mct/ki5iQ5bxCaqjx62iFQPW6RvnrFJf5MBUaN02CIDowbpsEUoJokQNTTK7k9giwzLk5sMICWO1iGLmMcYRdlH'
        b'DTeIKUKRTPQxRWJVDrcsGQIPY82eG706PvmuWzdAEb2r/waayCSepz5GJd6SzQkO8bolnT1mtvokne2V9McZyaPDekziiZZj/hQWiPahSX8e76O9OpbX6UHxPtQ1PAeH'
        b'InOoaxnAUIhXYHCYF8P5GNEFYyN07tyQ6I2ds8nd1fX0hR/lVg8dGEZ7Q+7a9lSqDiGjc5tVJp3KoOOgfl8fZqO9c9Qf0De6TS/1VIeH+jq9538MjtGdFNeIg2NAzrRl'
        b'GmzuO6odwc8xYDXnOSayfppy2hwG8kXB8MqhLDo+/cmrooYKsv7LXCjtuU/kCzFL1jquDo40jflc+H5P/0nLhMmusmfHXFVJuAiWToSbY05QbQx7nXXxPpAFpT2wgt5o'
        b'DwWhImJP8gELCLGjdAZbbbussUcE2bAm3axxf8BZxsA2PjRwnvVc4U06pm9QJA2qNfxPkDTSVdIPhskfFUkjirWaQgXQCP7/JIxG+7J4CIxG+7J66B2THhlGo/NK7QlG'
        b'o6cF/wBcC4OL1/D9fwLGomuuFk8riEykGQE05aqHBCLdY4ZAUrtBX3QaZy3cBT00OIQFOTgce871eRjORHtL/gzSRHzM/4FM/P8HZKJ9xRnAWKD/PQrUQ+dF+4hQDwYX'
        b'8P8BPfwFoAf6X/f0G6OgMJaAAJUxcTqIAYovYI9pOogBPIB5AVoS3w4PB9zEDCWewdbx8dPG1Mo0c0gx5wJsnSI/j/i81Op2XMzSx958/LXH33r8H4+/8/irj7/3+NXC'
        b'Y0XD9tXvHV5RvVeV07r4VPrIfdVl9Vke+4Yd3j1WKqSFmg8O2KMy4ibmK9AEJ5xcsbCXXuDsQeDetcn9g/WAAHQwAAIc9FiO1cw8OokSXHRDT4XzcXNlSdzPc3Y8tPEc'
        b'dyzdwAwqFbbcbHYIWnZ2ZVQoxgwa8Iw1kNse9PkfyYE3TI6glws/j0eo0thV2X0DksifTnS3fRQxaMg7jyQG/Zls9xiVJEgNknaxzECm+2zSMp7p3q0mXZq7fQ+HXbfU'
        b'dvmD43HXGHdZGMr2xeFDBTXjLqKakgprMUqtqGbMRDUFEdWMmaimYOKZ8U5FqN5nbcL6DkOi2oMT1vXVx/9fZKt3BvLSyj/aFO715MSgubT/l8D+fwnsdv+XwP5/CewP'
        b'T2B37lFKSiCngD6F2Z/KZ3/AlvG/zGf/r2ZhSw2KgdZaErPyICjgLGZyYQnU0STs8EAO6UUt8sGYied4lESoD2YFt6Nx+fhhHuMPW0ShsKLgioLFzcMByDGBq4opLB0C'
        b'KrFkZBfILzzo3o76VWDNEwauGDtqMD+mI6d7AF5OoWaxCXPddZznC7AIT/YAxyUKRFY7boJtPlCX4kQeNHbs3ZE9ipk+zgvhbCpL4MBMHQ/rqtGKWd6zGUG90RQb/06y'
        b'L54xD2CZsM6YH8iDvUKUxpi3Ea4w4TlgHN7AHG1R4fMXuSxcRBN5/QIDoDrMBy75BLq6+AaSEtxEaFCOgZyQUGHmpiFQbpEwexeLNw+HQ5M0W2M5b4YALaZQkEIFIrVm'
        b'lH7BMjhHyqZpqRvGqGkuKssIlwkRkGMMpc7DU2gWkMQLMkMXae/Tjk8Yu39PiN4LL4sxhjOOM5lBcKv9csyPU6otSOdJe0mmQQuW8PyRHDg/04cOFrakaqSCiDclTpCF'
        b'LSx43ifESNhgTto/M8LMX6MS4m0WehhpniBXXGa0hRdMs94z02xf8YqDu840fiterkh76533bh1xfd1v9zUfo7zF6cseC3wxf8KEZ/1v/Dymd9Dk1YtL3GznfrLwxwGe'
        b'idmFr9XERFz/YvC9LZk+br/Mzh5l+/jrg5bYad6o6WttDLeO9B/9Y7+3RkSOPZm3ovf5dwISnL+J8VH93uBSfG1R2diNH4/+ZaTpntFXXR3e8Ks5vVx96ZfsXcf/uTOs'
        b'NSjuV2/Lb2ZlvPfKxoUJd4vOv27mPe+lfk3hFz95O3dN0JsBa4MTC6/PMHfxmlwyXmXFjJnGcBpb/TuldYpqaQI2K5jL2CwOj3TO64QDToyJrgxakmmO0UJ1P/9p2NKe'
        b'1Dl2F4+9yoVzkKmfdjnBlvFcJ+FuHvtw1gMKmBICBYM6J13GQDpPCpQt080OI1JxKxyibMLL8RhTcLYn4A1/aCRLRecxvr6SOcGNIqbrh6qti2J8HadCWGCSJewmFetH'
        b'0OINOKIXQrvdjzUwAVoH8/bTZZlFqrDAa5AJF6QBkDaEOa0diCZ1BnMlOk5jCVyYBCU8yKcJDsFF/7V4bYwfXeq1ArY4EPWO7kODgjFrVoAeuwfuxdZlvN+aYyOc/AL5'
        b'eDhJoBwrhN6jpXh0EdRpgc+gAY9QBDmiNS7GvUxxJLpbPUu5xLZlUGco5ZLlW/YfIXcjDb7ZnU9O+R/Mdwx4iMZnuoFmPVIGX5q5KJdTx7ANc3lbMBe0BftL7tBmL24d'
        b'2lVZMpikaPIoSYod+YlGPXv3jXvmtDWQi+j1KOqmXa0BdfNh7/VfTEeMU0nvrnhoOqIhPe0v5SJSZ0X3XMThQQxBYeL4wE6piHp5iEkLH5yJiPnjU+iaXpQCWR1piFAn'
        b'rJ4zTYrF7krBHi9KMR1z3Dk0ZV00FHPUAmO8ypMR8Qxks1Miui9k0MfJwZ6byLIM14awc0C1S2Q8XS9PTXCePqOfwLOALs/BU9pEQglWkJoLaUDWMWOWrTfIMQaLyUFS'
        b'yxir3EZDjjbFcA2Ua6gRg5JQbhAga8RIrVgQvI3nEcq2TMMaCe72gctMZrGSwE29JEJbKDTDljD20Di8atWeQxgpo1mEx+ACTz680RsuaRMJJXgxENMEvLh4IWtD5Ewo'
        b'4nl/UsETaiWOeGJmih19qAiO4xWe3sdT+5bCQW12HzkgT7K+qHEuEAZJBNs6412JISOG8sy2VI/hAs2fm7kodvZo7+38y7MePoyY1W7ENscNgav+vfS+2EdLB7tKDSws'
        b'HcyX9QLWYquWkcSZbKobfQNpsFuRE+c+wgPk9MjiMX0qaJaOGUOEthzI8YcD2KhR4kVhDmZahvWazt6nfpm5QOaQg/vW7QGn+6/hL6mK6SsQmcoqQpMyyCnAUmBpksux'
        b'KYyl9HlhujarryOjr2YXG4VNE+ZqM/akNljYRzJlOtaxErdrOA7QfN9Y5082DxdUEnb/ciwJ1rAIXc/FLMHuOKb/Wz0a92g9KlW09yjPNIyBcm2GndRkaaRkEtRhNmdo'
        b'u6Lx0WbXLZ0mQFniJD4TD0I9NGEjS64bOoOn14UP5n7aazMxU0kO1WPklwXCAiiFJrZMfTF9ptIB6yMcnXT5daSiAr7wMmLgXKf8OitfUsvhtfGb/L6QatJIE36xnZUS'
        b'9nSizSyrr78pC3xv42O365ofH2Vb7DHZe2Cx5qnDb9ra7n36omTj5x88tsfWwud5yxP9RwT5DPpFuVPI6j26ZlAvH7vvzm/t298q40jNz+fXer72Vf47DsuKin+9Nvv5'
        b'7O0jKi+6rTkTbj+n6K7F9viol5998xXXulfLXs46PW/95/NMe7XYHzcZ/vy64csOvdI698sAX7vha8ZEbmqzzZqkfH6kfWT+qcgJz1lknx/QOvDTANeXRtu/MPDpj9/I'
        b'elniKvTLXWf6WM2zT6Wcq7q/edRnb4y2Xrn3pR/+H+LeAy6qo/sfvvfuspRdehFFEVCRZSkKKCKIgI1e7B2QJkhfwI4UpYMIWEBAQUC6SG9KMpP+pHdJTGJMNaYXE2Pi'
        b'O+XSLHmS53n+v1c/wM7eO3fmzpw5c86c8z3n3ZwtZ1+4auVd8OWg8KufV8ar37PbYffbxhM26k/a7XlFJyd9+azFgrdrv7cP36p8IzBGGvusd333Xd1f1Q6ter88PNl/'
        b'48dcsnFcuJOXfV3y9Q7D0Bd/+XxuybMDT+6N/7FA6QPbb542+/i3t99xs3cOmLf1opKzzTvZAU+JW4/ve+PbXyO+E5cHClMrPn3SsvdHf7WNv3/dpH9ycIvfkcqI1OeN'
        b'DpwI1Tr2Yn1HWMenM7+8uOgNtRab3cwQd9szvmxApXf0uWaLO2CbYNuePT9Jru+K8NWo0g9KmfXDYoN7F73Lv7J89nufJwyi9jkpdp94+/y234Rfl8e8HuMU67upr/7U'
        b'08nbHHpVe6+nyAIi2xSXvVU+M2nuGrXsp59btOrImlW3fll47KSTUdLOYzs3L69+w+Qnpa5fbvnMkkXNj2YW5zxnVR2m9EFs612FS36v/Zn5zptxhm2xf77JNN9b1jj6'
        b'1bc3v/XcccD3877ZKUyKxm3j+x1Hjt4/Yrfq2Qazz5Z8ufjJmBW3hZ/9xnwztylnwd6cqHhQeq5/k/n595Lyfi9d/cLyL2/PH9EfvbPpVlphvGKqv2LUr8tnLal6eW/O'
        b'+n/d3P6ibXSy+NLxgZ0/uA/p+bxlZZJS5PyD+wj6aG2yoi6o6F59kOPFDQt+ePlylqM7nFnefMN2kaq87sNv0v/oahw+/tzAh0MOZ5/J0twv/MXp56L4wW81b27Y8Jvl'
        b'sLgjv8Or41/3bJIS27JPd4g/b8w4HXTpi/Iv/+iPctrovswkLq3HOKa5uWKfYtJLm+v1tKWvlTu+863kI12Dt6Y/1Q5jXZbb71dI/WT97emv5n9a9632lQ2xt47/8WPt'
        b'Tzdvj355Oy32+rQN87/ojHD79ZWCkle74g3W/5b9zTOjqbeqt96vOfV5zMXtH91+b0MEaLm+6OPMtYXZa4ZSdsfpPr1XfUexCXDc+eQH3qaGfk8lBOj/oWBi8qnrNhtp'
        b'HJG0F8I02DlV0sZSNjyaTAVt0KpM5HyXHbBO5nsElk1NWNePNAXsqRsGriykSDVjm8lYtQhQSh24G+EAuEKwavTyxlk8VK0B8LrGqcXw4jjAzNpsAmIGB2AtEat9poOy'
        b'KfgynBnR0g2eJU1owwxYKJ8QUhJVeZQZklXaiOBtM3srDzKTeqJ9RgZKzbHfLw80cwRHRaBLN4ZI/5HGGpNBZotBjTloW0iUBitQ7j0FSjYXZM5L1SXXTLVhpZcFPO9m'
        b'5j4BJmM9yBBFOoJ+Mep8HjxvybsbEzCZPswgIIt54eA8xQtQIBm8AtrHwGQK8CJxzY3gMH6HgMmEi9fuZ0HTDC3qftsMGzTx09tgOXrCGJQMHLUhgyuGdaBfPglI5pg8'
        b'DiXrFZI3dtaB5ZNhZPOMBCsAndwk7yQKI1PX44FkBESGpus0uR4UBfIJhgxe2c3DyAiGTIPXEcPcgwiCjMLHlnE8gGw5bKVe3p0poF1sBUdQB2DvBAoM7Z4UOVIFT6fw'
        b'CLBUkMGAxrhI4siNhKEuP9g1CQLWB69MwMC6IYVMwWKYDwonNDnYvwspc0dseOCSOjgr9rWUSNFrgwusyh7Yvg0UEBucHXqjegoT4TEisBVUUpwIOAaHyE0WSK4s8/K1'
        b'QFvkCEWaTcaZmRtSchIuJCAzjDBTNaIYs1UCsgARdXcjYQ9jzEhA8FwpxZiBVthkKBSCy5LFFFKSK0smcDIMJoNV8CQPKDNFb4mvr9VdgPFXdBnDi/AMjyiDhZQ0dUE7'
        b'LKM4BAE4BSs3YhgCSKNmyFo3pLDygDL3WAYMgwIKZAneCkqImg6y9k/Oq1nHw5kU0KLrGkOUCQ0P6LCg1hqW8wA4WLiHrqI1iuORjXS1kwlRbAFp4AoBlBlEUEgZBZQN'
        b'HSBdiuV00VK/qir1HIeThWmTJpfB3JliqzXaUvNJcLLj0aS7q+B5BQImI0iyvTCHB5PB3iTapcEjsG4ylKwwAJ4DeWCEdGl+NMyaCiVTBy2wZzc4QRp2gOdpFCYaggmM'
        b'GLBg0HURfXDVfDjIY8kEMDcUXmbBBdAK2imRlW2DpzCazHYJxZNhMJm3NiGNUMcgih3xtWINeQBIfTK55Ada2DEIGRxeyaAZ7IZlFFYyZIuhVhRFxgGkStSxBkHwMiX4'
        b'wa2IT08kO4UjNiw4G7iHHAUl2AVQGVXjIJZRLTV4QBTIBs0TR0wLYB3FkYEi2EDprwZkahKwSitooUgXDHMBxbCIYsnOw4srJoBkIMdtKpZsPTxDkCgR2+BlDCXDR5pj'
        b'cLIJMBlsOEx5QhsoDZkCJQP9aMnlwTOOFHByGZ6AFTQmFzjuggFlTvAceXtju6loMgxc3olULVJP036fnIDJAkABxZMhfpBJpjB+Oawdw5MJYDXiOh3oDkPYT6bQEymz'
        b'J1C/FRTMPMfhZJIthAV4u4A+NDKgCFRLVdBawSecPajX+rBDKIMX1pIHLJYhNcdsCTg7SV6GIwt5NwCzTdQLAJyAAyTafZsK3RVr1sDjYvJMtK2gx2LKVAElHJqF4VRS'
        b'2ZGbJuaxMUj3BJdXmoCKaDIS83AmVAz7ObyKh7FFCNRhlgJ1MKg7CI7KyUZorow4GwWxgRrHWY5CcGLxTDoNxw7Akikgthi06M7BHDBMTsKEoHAdjxs8eWQMyYZhbLB/'
        b'BumcQygowJs6dnAohK0Yx7aHHt1xruwYgM1SZyqEDQ4dJpOlBc/LKIJNaLgdXEUrCskjJym9FoJcLdoygZ3FwTweeQbOmJKub7GA7fhQMBNcouf1Y9gzR5+k+Vhc0MaK'
        b'5CTkmRG2BkwBn8FT8CqVXtJmOY8NFWJ4maAJKX8wQ5AEMDIRb97+OvACJlcvvWipMsyTevA7/HSQLlzjnkgGa4czLMH3wCrQ6yUl76sIKzlX0AavkC6rxyIOQ4BmRPJw'
        b'xvs/xpnNg9l0NlrtEX2Q01Y4BPPoiSs+bXVRIIM9C7Gco+PnnD7BLGgxjyc1rUElqJejNv0QLR2XgbJliOFq7BccSrYktG+5DbbLYJEYnPJGAhgOFwTLuYOg3YEO9jH1'
        b'EDneVXKxmIglplI/JNxo6goO2y0i6Ds4iN6TB98h7jWOv3s0+m4XOEuJu2kbbBOPg9bQ2AyPA9fivEjH/DXBFQxfhSWgiDIdAmDNF1MumINj2FCgtAAJg3WRLCKMc4cp'
        b'S85FNF1Hsa++Vqs1KEZ3J+wjsqBaGOyWPdxDkA4u8dg6eIbvJsxTh2fE4whBeMloHCS4AbSSxaQPanZNwddhbN1yb4KuQ4JBC81eXLoInKboOgHsW+3GgkZwUkS9ldv3'
        b'6YthHrgCmsZkQ4yui0C8lU+VcdWK4usEsDsGlCDGhHTtHjK3totTKLbuYMBUdJ2tgGI6a5GMnUGhdY4xaEkbUKAZ2tpyYaN8HFuXFTEOr9vLg+P7YSfGKhOAnQCWM6AU'
        b'be9gGHFyfJrgCxoOiUlcg0FlDLCbt5kylvIoD7m3Rzho5PF1k7F1oM6ZdCoFtttP4OoOG2hvNqF4ZiRDwQq8i4D+zTLfCWQdSBdTQbfPB7TIrRGtDZjDjnFoHWjeTbjs'
        b'HFeYNRlXp4ZDW+5wJTsP2mkaGR5YB4dB1hRwHZIX00gDakiey8Hwuj2gmEfYYXxdMNpscQfnoK6c4vF1BFu3ZzaPrtOcywPhQB1B+vLoOoEPPBHOrkbbMXlxR9izxAsj'
        b'66xgIwHXle7mM4KHwGMyTyRTD07J+W0DeqVq//eIOYJnIpaCjX8Bl+NBc9MpaE6DFQoeB5dTegAuJyQWBBUMRrunIRKS+kasEaeP/s74G/A4JUUhD1iT8KA17k8MZuPu'
        b'i95VWfwgYI77U0uoQYBtQtIytmTgp+gr6eGTfs6CPhc9QSj6L6Fyb3K/qqycDJXTfzxUTu9B28J/iZPLwVYOG1T6KysHk6731SPsHI/pC+oBBhYkfjoGlRNgqNzrLH8G'
        b'KdX+v4O4vYkavYGRgLHM/wriJnqXk6mxSgqT4GzzJ+Bs9Dv9+4auJAqcJszc9OA5NSg8ZMEyZmBEIQaOGD/k66rG/5VnPIRj2yosUyxTLtMO5/DvMjX+sw7/V4X+jRSE'
        b'C0IFhVyo+bglCeeykWSrZqtla5Bc1BKMhyO4MYUwUagoVPEog3NxF3JbFVFZhZTFpKyEyhJSViVlZVRWI2V1UlZBZQ1S1iRlMSprkbI2KUtQWYeUdUlZFZX1SHkaKauh'
        b'sj4pTydldVSeQcoGpKyByjNJeRYpa6KyISnPJmUtVDYiZWNS1kZlE1KeQ8o62QrhLI+G0yWfcV5vpa16xEVSQKxsStliNDbqaGw0ydiYhUrRHdNCqX1CNipZ4eqzfixz'
        b'/Y1e7gG3SOyXNPkOCpwb96pJisOJHOT0nkU2FvSvLUl7gD/ZTXnYmDVObmXkOsnhj/dfI/7/vJccupoUlkiyMsSl4EyzSVMd9iZnaLAwCgsO2W2UGBafGCYPi530iEke'
        b'hdgddcoTHueyM9UmOKXgG4c9tTzCjUiKVbnR3rDEMCN58q6YSOJ7FBk7CVZBnKHQ5WD0k7Q7MWxq4zFhSbvjQomnOepzXHRKGLFeJmMGE70fO1VNSUFhtCqS+CeZuUp5'
        b'J9voqV5b2LmJ9/ujE2HNz8PYiFsYmblJx24LNpKHYf+zpLC/miQ8h2YrpBiLETzJx4/3rotLjIyIjA2OxqAAHkuMhgADHh54Ubk8OILAQcJoqg10F317o9CweMRR5UZx'
        b'tOPEUc+Mv+aGKSwmTj7VXyskLiYGOxMT2nvAKdBXyo0K9sVEj4pCgmOSFtmFCCaxHQWe9RAzE84VwQO9FLPHkmGJCQthERPhwtV4s7QgR5TJHBYeUD4kIGZpITFFC1KF'
        b'6yZ9pmbpG3fZvwH9mrKQHu8a9jhvQfR21FFws4837+lG8p6Q507MG5oh4g2KluWjXUjNwig5PW7N/gUkiQztUowsCQlGqz4IdSmIeuzRh40/ZDLpPSYbTXBoaCT17+Tb'
        b'nUJ6mEgTksP45StPRutqnH08GooxxQuWJpnBqy84OSkuJjgpMoQQa0xYYsSkFDKPAXUkolUZHxcbikeYrum/TgkzZZ9T5QluqtvALF851jG+T36i67U7Mt1Z0uYk6fPS'
        b'3nzp253pcibysFL9M7/9iKsT77h98KoicRLqk4EamC0F6G6YKwW9IF8KT4FOQOuAet89RERdTxzWQHkI0vlaUOOpTAoYTAWtAmKdTZ7LbWzFNlEmKHpujCtvFa0DSCgH'
        b'XYjjOzKwG6Y7wlwwFP3r/fv3uwMUdt8XaBAXso45mxkas7cfNkwj8ZJhme0CjlFwYHeDEX84uE3KUWR7K+wFHXKYpwZzjcP2UrsCUjSVzc1YxgaWiWTwkjI1oRaCMrEY'
        b'DMzDVzgf1j4K6ZIcDa6csWI6fQR9gAr+xR6ApxiTpQomsBVUkM7HylbBrPVichEpYoMsUoFrN6NnWBC5JA8OTn5Iooc51qYvyzy8QBsot8LGjY3wjNLMDZrEchuvDpCO'
        b'hK6SK0qLDoJBLhZe3SEVJNNY/bAWNOP0G5bwhG0CPLFgEcdIDnN7QBdoTSa6yrnE5WPXkTKUsWCRiJGkctHwojGx/jqHwZqx67B12YJFLCM5wsWs0iKTjUb2Cj7Hok6B'
        b'7vi+APcJsw0LasBVZqW64jStUGKpXwiuonEm0VoCLJEOV+ClNVPAaIMifFJUuDgZQyVgjh3Mm+ygMpYOBeZ6e3lZcgnLQNVMeAXk6SKNttNLB55Euneel1gFdoJ8z7Xr'
        b'mLBwDXsrQN0n/rVCQRRA6SF6dYwGk7yDIYG2SpEmPWL+iFawW6a15wYzmOsOC9Zhl0ivDbBDNkbGxD3Gz0NBa54KPAbqFRTgwKp5oEnKrNqrA6vgcdiDRh4rr9ucUSFz'
        b'CexSj09ElAL7WVP0xSCN3tuwXgsUgyGxEkbSID3GPBwcp9b7PnsxIugzsEuSQKq1snNhWSIN7N0Ph7frgHx5PDnyFUjYIJgBmui1JvXkRbBCngA7JbhaGjsXpBHKxETr'
        b'q+e9GhTLYS95Jhhm9bg1hBa9QCYsX6Y1uTVwOoDQhc9seHV83jvAxbGJ3wuGk3FEjTDzPTSriyc+wsGJXXwsPf02uPNVFiziBxR1o4uB56LFaJLSwIVkrOXMFILaySlh'
        b'SE1/y424xvzNMJeBJUwo7FfCWVDPR6oc+1pBjjWUuqI1MSWOcdquGs/u/fbtO798+vVTxi5K6oL0j4TxhilpXG5JxikN5cKMzlOtv7JvxcKAVsdN642u6+rkZLzCLFqW'
        b'4ecyPTer5NrPTxu7JBy0vf/bKy/H3fF1aG68/dQtnQ3FWueDmnaF38m3fOeTxR3B7f7Zbrs8THJU9jYZve8ZE2+jElse9EnwJ6eTC5uKu7qLZz2tVvx5XVfM+mkZBasH'
        b'P3ZR0tQxTg3xMt99K+wT52tbDkR7eI2CZ+xLj1Vb5wS598UNCoLDuofmWFz5McBHSztycXbJxpo/zk8Dm90Co55xHwSfrjIMefZMvJ1stv21ldU+P/zq8un3ZU3estkH'
        b'w/dV+r/oqf9K7edfvyq4Wetv8sVbLw8MXyo4+PKFz2/O/q3p0MvA3fGlV77r+uLuIbctdu3yOTG55+xfOHYi8bVPTj/xdI/JzOH6RV8q+/mduPrdS5/M/vXl+T8ca7ju'
        b'cHtHlrJc0XAkY9ZlSZmMS11Us+BaqGC05oszrxf94qdrA2Sb18S5vZO7KkX29bfgyf3/2jdtRdGee0uP/zw77VZewOELH+g3vfX+QN6PvaFmblefifth2+Zzqa7xJmYZ'
        b'ozGGX+mGv/BU0lsLtq3xa4qs+bwmuCl9pEkata/iJPu189P7jT/86KyT4auZ800/WNLwWuBhl/f+df5+y9Y4r/0O16PctO+qv9Ra89t3gRV3lSveyWqofuPNEw15dt/6'
        b'vTr8e35DxRtJEp/DgZdU6+PuTfsl7iL7YphOV0mm3xVH/7fvXJr5tM4vtb+suvxT7Oq7rboz3lr3WnW97PqlvGUXDjfoV4cHrM7LM6ux0Xrt+6LrK95P2PnKq7eqN5h8'
        b'9vuaRjv/gXeeWNc3wu5f+dPNkbuqMcVKZ9+eLXWlNpg20IbNIJUw18qHQyuokfWCdfAUjafXCc55od3oEonPnusH8zhGDIY5OLQTtk4PpaeF6aCPkdnDTA9vRVQ9h10G'
        b'hsBx3nR2BZ6nhnCQA6vHgq3awSuk6YWJsBjkW4MmC1gFqt0VGFEQZxIEGskBmVoy4hX5OBEUOOWCMY2pnDlo3JtkTTgCNvTlW2NTrrcVyPUj5mCQY+1uYQ6LPEEJ4r2K'
        b'TCDaiNtAOxikvrBl5qByzK4/D6SPx6CdDVvoQAylWOOzMlgI0qZZihjRTm4OYg4X6Il2XQw87eVn6WGB7ZJi0M3BUy5wGJyARfQ4cFDJfnIA3OnwGJ/aBGaQs9ltrqB5'
        b'MkrSGXTwDsqojQE+YuZpeIUE4+JPC0HTOs59xSzau3YP7EiGDwwPgNaxWFwuGnzsNodUkIc4uQdoQ1u3MIKFWbAAZJDTRB2QCc7gI+9JgboOIJbNzICVwgSQIyNH8m4r'
        b'wQC25Rf4jAWCTARlpP4KMRZvrD19vCyxyc2XHkbO387MhScVHMEx3zETd4mtHBZ64DnxUvO1hPWgBXZ7cYzhaiGoB+eDyDi6h8Lz2BB+XBndkR1DblBdxcEBzzh69JkW'
        b'qoYa87W08KFtrUwiR59GC4XogWmARtcVg5ygSYHFOC5+LigzBEPUBnIVHgcNIN/PytPHAl4ARz3QK6ntFixBwsQxeqDcAHsS6UYNL6NB76OxYhcJFGHnHtJNCxxwkpgJ'
        b'CrxgDdq+8xUZkTInAVe1aMy2Bng5Bh53lZNYeII97CFXkEu6Nt8PnoalLpMsnqwBbEYETzP7TJcvWD3JdoePx+tmkLUyCzQvIwYoz0S0GRYIGAVYwcJBkL+LVPWHl0Dd'
        b'EdgitvIiZ9zNLBIT+/VI+D1ntP1kPxgacxaoHY+OWQybSOd87WGnHEednRSmEtaBy3zQ1dVggNgjkQjRNh7h8sIyGsA3Lxo0g24JtkRhW6YAnmVBEbwSSZdHDagXwh5w'
        b'Br/bcRnuYBcLLqIXOUbthm3wWBy2VofY8KFgU0AOrXkKnJzPe9PAHNDig+3ZgxwL2hhqFOhKcJNrgEvj8USdkymhVLrgwfGbwBrAMlDGaIF2AcwHLYgB0fCWTrCPIA54'
        b'wxqocAKtHMgVWBBbsLcxbH3ApwiUTfLej4a9ZOCiQL4HyN6PhFHecN7DgnbYvI6+QjeSBPvotSTpzIVIkhIxaqGCVVHiJCwRoHWQBU6D/L0psFs1YUIqw0hsa1jk7qM/'
        b'3xLVWLdKSW13KHX3r9RdLpepIDlZyjKKhzlwgbODrcbkWsQimCaXJVLSVwyD6dM5GydQSC0ahejdT6L39cCGIj+Sfk/RQoHRhc1CzTnwKJ+kCTbEi/Gz6SPQtF5Q4ZaJ'
        b'NSmbzINnxWNPgBfcEKkqMmq+AhcGpBMnF80ocFUOGvd7Yq8iFvaxGluo6wii8gpYJpYi1pPFR0d0Q9yTGoc3okqTgiOCHthLLThwWIU8FlYhmVPuaxM+Fj8Znk6kpFOJ'
        b'lnOWHPYljQf1FJlQQ/6g1AL1FHXEAy1Twpes3WGhYEsKMwc2KNj7wmrKmzsWwXq5rxSbxLCFhzUEDYzGLEEA7FpLaEwmNZdLkVo3MhYZmRHRaTgFq2EzyFWW06ESgGPs'
        b'AdWVvMk6F6bJPC29LM1B/25fxGLUIwTBSVJisoVFcABxlsl989sER9DXudi6Ld2pAM4awf4krBXBckQb56ZSRyD2sqYE4rcYyaaOoF3kG8hHKjUGI9ibDRRPgXzYgGxq'
        b'A7wCT6qJ8RXeQw5chulI9RoUgDbvRdTwU4sYepuMbEZon1OCQ/PncODELniJcEeFuVh4nRzVEfTwtqel06Wq/711539kJXpUfACAfv21DYg5ohKmwapxKqyInclKqNWF'
        b'I2fsf2goKBF7iIhVIbYT7nclRfxZjZ2Bfmayc1lTVovPjKXE6hM7kQaxruih7/TQfzVOC/9G/5VYQ2x7uStS0nvEdyLUhhoJzoifIOLxKjgwo/BnoeIB3cknUlODFkgV'
        b'KGLkNrZsfD0VhSL5r6ZFQB838fTxofVQ4oNt/bW5hkk3bXqEwebRL/O3giAc/bdBENqwRzkJgjC1mfEICAvHTsrJUbOFUViElZE5Pi+zWrDIdixOy8MBEf5+9w78Vfc6'
        b'xrp31wD3gz92NYoMndLi326siR1VCgyh5/GPbbNrvE1jgl4mkN1wI1INY/D/ccsRqGUpO6oaOH7aHBj5+OZ7x5s3dTVKjo1MSA57BFT/n/YhnPZBEjh2+vhXXRgY74I5'
        b'HgF5EhoCcn45fnT533Qj0eSvZnx4vG2rdXE4OlBseBwJd2AUvCsuOWlKsKH/bCoSceyYx7Y/MpXiJgW/+c8ac/+rxsB4YzMmGnPzWPHP29qN2/L6q7aeHmsr0Yf5m+uT'
        b'vEDRXz30ufEXMFv/iJBFYyE4/qPFishVhUQRCMSY/sd24V9TJ4wEAqCL9j9dqEq01aS4x7b58nib0/mgEf9hi7vHWMOu4GhsNAmMiw+LfWyzr403uwQ3i++lJ/nRk82B'
        b'D0YZ+Y97pTbeq5DoOHnYY7v15tRu4Zv/q279L2JUHn1UjEqWedB6IfCNPPjUMCfHgvLyE6M44KRS+EcvMozSr6Z5bJ/EWcpSPSjnMNLGpuhB3I4FIHctPPqYKJMLx9xq'
        b'sIL570Qq5ogo4oDOA/t8dFjsWKClR8WYxA28gwULHMf43wkWTLqk4hGixSOb/P9rLoS+6yMHtn8jlOOvV1r2egVLwj+KZhnhK4Wr2NULLk6Q3sOj3cvQ0U4sYh8SZQID'
        b'd8XFRf/VUOLao/9gKE//DSmNtjllLHGfccuYoKi1diIw51gMKGqxZbNVx621XI4CGmUBGmWOjLKAjCyXKlg36fNevLU+MMrYcw9nXLSdMspGvhR72wlLD1KLALwQzxsF'
        b'qsFZYiezNBEyaDiM/N2PSD5dG8VQK0JHBDwvV0tUZnEYNlSjlrWCl0Q0eeRiWiFIK0LybswqJhlzg40wjbjKFsgoZB8HtSjwQh98LbbDEqTJrfVfa7mRY3a6KIIaeNyc'
        b'pCo3AL1rvHDo6HxQNHFkpgCqYT1jHqIAWuzAaWImUTGFA9TYAWv8ib1jMbqC1dUQmAmGxoN3sAlj7sBwgE8ZaAx65uLDHi+YrwiqYBojtGRBG0jfR+2HvaAG5FH4L2xn'
        b'SB7R7UJqDjsFukC9TDaNqK2+WIFHSmsYOA7y1tMIFrUOS4leaOkhhB2ghVFW5EBROLhMLC1CX3iVRE+AA1qMUMiCc2IxHdps0CHHp59SS5HbbkbZgQP1B2AtmSg5aIHH'
        b'KBII5sEhhqSVgsV7SEVf1bUw39IX6ZipoJ9lRDs4XdgCjydjv9cdMA80e8EiDxxlzxvmo2Hngw8g7XeQkS1TgIXrVz1EoOIxAnWfINCp5MmOByb7u6T5UMBgPM7KD5Gm'
        b'lS+hPodgBUxMC3b5BVkc0prBkLFLWueOfV9T3QmoBZ+c9VHDF6zDZkzs/KsAS4lzMAsKNwQT064mHAEjMk+YGTB1vk6GkmcGIirAB5DKoIOeQcJ2O4qebZdryrEPchiO'
        b'iTCLheXk63kBThSHYCbGMISVsI304DCo2k4xGLoeY9nQVUE2zRRavQpHa8EOx1qeGDfDglqYBUsJOenDUtA+ORETexjDZmAVbCbGb9qXkyALXF7HmIE0RLmMscV8qQKp'
        b'bQgz8IMnagfAQlxdFeSRbpmARtBBQSyWM/hM4uDEEUrI+arwtAytx4uePIKGh88sNyHdNoSVoAKDjDAkJ1CfgHJQNxqJmRY2x8IaGWrVCq0RK6mlpw/LgFpDE3BMwQE2'
        b'21KjeiO8ojmeVQmeMSFAGLQGryTzicpbwFne0xrR7RKQocRNEyhRe/vgYY9HOGxTZ21wUiMcJ34ngQbYsLnEq9+bnDPjADogj5x2m25SMF68B5SAahLYRgm2bsWmED9f'
        b'V3znYzzWfUG6IizWh52EDaDL6QaEwUwDObxB9YIKebmgpQET7IWB54x5/jLiSliY2+q9lIPBKsRVJnMxysHAECgmo+CqDjp5PgTLFypSNrQRdBP+dhhnk8GYCNBvLyCE'
        b'c8GepdziAjyNT9TxtUJdPtCJbTjp9QGYpcdzBDSsfqmIIQSCDFItVbaSsBHE32oFPBupAU00EkI2bPZHNMwy/qCGXcLAIv1kOlHlsB2WyXwspYrYo0IYjJgh7AcNdOml'
        b'+RIKdLe0QMMnjVUCp7hDW6bR+EtHYS77kKM8Iv1e4iofLSbdTVA5MpF6KRwOYNhKoAcZRSNwgiT08rAItH+QgVHmJZ0r5eiAXJ2OrVmwM0XIBCex2Pf74hbQQVpwtsQn'
        b'+5dFqEOH0VrCDvYX4DlqaM+Dtej9SkWwB9QwjAVjsQX2ku3sjomYQcPi/5ZekEX56p00uECNkgAzSPcXhEGSjyT69Mtsa8Krgr7wCIpGMi390mkJiU0Q/+eWoOgTOy3o'
        b'l9c4JUYDfakWHCRJ3+n0cAAGIizinxlEBjnE7FA8zB5i4xVDmY2IlSZwoeN6HpGB+HTKbMoDIvmoslNEWGzYvvhE5zBlnr1yaXpM8hb0wV0dnpM/cIwOT6CxSw/BAU4t'
        b'PCxBHvpwekooBlgqgF2gVMsLlNhq7FoMm3AyrCZdhVUpDDgToAu7fBHN4jzmUtirgs32aJGVWlp5kFhBngH+lhvdH7ENIXpSQaunHwxjhicJms+SuBcK82CdzNNSaom2'
        b'L2I/Coc9eKNmZm4QglbZnkhhrJOC/Hn0ulYzp4etG4h9z0Xj+o48Lekt5+g37hz+rLvqgoZk2jdrFUQZdqvzLEL3Keh3HhUqLdgm9H3SNGuwe26xqU+xSaCm0ezi5e5V'
        b'1s/dtnjpuQTj76/YxxVVzfuwq3HfU6s/Dm3cUpa/Bdgdd3r+4K5Xy9zEX+7+3Cn7Plcu8E6oEljJjQ2sjLUzBc+lF38zV1yeuN534I8rBp6GR9pTnixUaX7VNlXx6BMv'
        b'rH9pRUR15VXzXd/8eL/bZeDdtleD+waT4va6Xoyoajy5fvqOuLUbGxrPrZItVd+/YV7Pu8EXvacVv1P0rseGgx8Ff3ZS8vEBIDp3XsO+oCT+ZavanHKr2QXFNUO51/a/'
        b'tbbd4umYldpnfl4lyjHVPHzSddPc99/84shpiUrnvdeSWs5MD9UV+sRevLew4V2PPdfqiipe8N3kJ6+6/P6HIXkvxZzPb/L3aSn/c/ZK21HFI08p7v/u5J5qTXulQ9ck'
        b'1+pzhk85rMvvDE/WzIt6+de7yevfq8ntkS72u2Xxg/La+f6WzQq3HDz2nfhO58a8xG+N1Z+fVTLofYv9IXLtRY8dNcPTQcvRCOVLmtUXvvkqKjPRTylubWi1ybalSxb1'
        b'6BUrRG37utHx12dOnj8acTjip+Ibqqde9DnjOPeVHcNfdlpFBLz/fvKhp6ztDnxz4kKJg7n9zE0n4uacdvr6xTcP9zS1+Pt8fi/rrklVwmVoYZj7pG3B8ifsw79sC6t7'
        b'Vv3TRJBsmViT8vynnuqOklRXy9jnnvjJ4J3s5TWmmxZG2C/UdQrd89wvz5QnKwVXz4JvL31n0dsHwd2PD997/asv2/JqFJMPXthifdPR7sU3716sux4zArt/j31msZup'
        b'4ObMb7alzMo/NCDtc/7Ibs3mwt6sgw7qtYfuuce+1/ZuzFw1+/d0BlnVn8/0Su9aK99s+8q0dv6v0a7aQ8NZehuXZ5p2D3I/7v1OaJI4eE+y98/ywITrItHXm/xq/si4'
        b'cecr95QX770x8mv4wmdOyaUOxCJyGFwBpXhDB42JsFFIWPQwKAiiZonzK+A5McabKZshEdpSxGiCi4IUtMVVesAaYtcQbgVHxeZSJNkTfF8BbFcy4DaCES2KrW6ztScg'
        b'TdvF1DxtC3upkSZtbgi1tibDc2MG1+M+xHaUCrpZYhOfAVp5s/hKCoPVBWVwhBpiQQ8sGTPGWtKMWsbwTCIViVxB5ZhM5LiCWE8WgloMf887skLqkeBtLRUxqrBAYLoV'
        b'VBM7+K7EMN4Sa4cEu4fyFDbCOtIz+3XgPMV3ctbUDqsLKkjbRvBS6AQqFJQZa7I7Q8FVPlUYaAXFYpIoa9YObj3rHAMryPBsYZwoGBgMBNNUmzUzifHLZh9smsiGCRtg'
        b'Fg9fzge8TXpoPoYRIRHMF1QRTDDaqg1nk2MDXQ1tuTeeEcTxvNCzS2CeioQD51VgITH57YI1BiShqQXDiEDBUtDK2Sq7EGrYMgOSZLUkukAwqCABBizBMTL6i2AnOD0J'
        b'wGyrQrJhzlAkVV2QYHd2HPvcZEcyabqBYjL8PkrqaHjzSDDrq9hMLnRgwWX0PAo3DoWVIpzCkyKunWE3AV03+1PLZzloDJHDPA8P2OfFMUh6aVZM4MznbCAvcyBcjeRh'
        b'x3BHcFSNwF7Ldck47JkDq+WwwDJBSmy74CKsUNnEgUFYTrFeO+B5DTFoiicWSgUkfJ4HFSy8BC8tJPZFs0B4XE6u6YHj2IBpcIh8n6qtJfb0kSX4iZDcP8iCEwop1Oum'
        b'FxSBq0S0t/KyUoHN8DxGr+mDHqE9bLOkueEq0BBcJk4MbTYwdwIYq4PkYFi6F+QTi3AA7F1D0Kvr1j6cgPEMnxItAFQggQyDQinYUwtkELxngoxQSAxsN5uAqu1fQJLA'
        b'nfWiSeA8QnEwhxNHxqNBjEWCMAc1ZOwWwDq/yQkkl8OLFHkbFUAB0hdCQB/O5OgAi9AyNGZdwSVYRj0SzqYE4dSYxEtEAWbCtFUsBufSyBeHQ+AFDFI8BFoJThGjFAto'
        b'dshE0QwchgH0uVJbMqiZRnnF2Tng4jgGOR5263EmcCSONGa/gxVPYABxhA8MbLSF58jKk8h3Y1gjLFcnyEa0ZI0QLePJQhp4VziBm+doPpg2EA4vIgBEO9ixggAQZ8Ms'
        b'DEB09CFM0fnwzonkfvCyju0E/BA2RlCj+lGDxWPwQ1iyB2f2a4HnyazZwMFF2JsW0R16V9gOShW9OGNwEVwi7+oECkEGgUTKUwgoEqlue2A+9VgoRzr00UkRSrK0sV8W'
        b'oimadRQ2k8imFr6IVSOpimXmgnwxWsBImO7YSp9QdfgIuaFACnPchQxoXi0G7Ry8IFOnXOUqUmUycYQDEp2+hENyub+5hLy2DRKMymR+FmgV5xNHrQDEouBVDvaBSjhI'
        b'JnAvLE4Sm8MiAZO6jPNh7Xwg9VHxWzRP7s1y1HNnwmun6ADxCUmEvWjpTPVWQ49sIx5rrb7wrFTv/zUK7AGb6n8fCXFUBSNuAom3OxGxPyby8L8/kWWOqOhgs7KQQBzx'
        b'bzXOlBi2LVhz1pAYuoXEuC1huTRyHojvpKbvP4UC7g9OwIlUfjRV12NNWQ1OjdVnRRw2ctOsg3p8/sEZxBwuQb+1CIhQhdPHRnF0pz6rpoQN7Wr3Z3IzBGo8rNIIfSO8'
        b'j39mcviJEhKwX4/loZmciEN9PnFA+qDVGI9CoJUTsTHJna0mRoWqE8JR5aR9oWFJwZHR8lHFwKR9u4LlYZNs4/9BAgKkoiijZycqcWMHrYrokwArJTi+778/aGXSjb5+'
        b'+KiVRpOrWrj6UYrM39NinKKZxYgVWcB+lvfIXmWVSmPioM3iNJ9efQGopbrsyAY44MW7SI6bAGaAzAXgghDkC0KIwgobrcInt18MT/jxUXZmOwphGWIwF8YU1nPweDR9'
        b'oKWEbywMpJEzDTW0K/c83BhWXXFjSODrS8ZZHKxXqMiw31abmbuPlYdPQDweDGVwjmTOwIEOWCZIV2kuLNGjJz4F4EyKl6bGuAc2ddhG3K6CnBZKwQW8/RRaItlofbz5'
        b'bvy0hYsC3Pk3WDpXxETBGhLydzk8CdInp+8gTQeYeZo6T5x0bEcSizrMhlVkBF1cDCYPTaXzlJEBmWvJgTE4vwI0y/mHjT1qAx9UGL8VEoXkoJMJP6IEamEbJdzIvoEU'
        b'ofwU+nhi1CZs3VCstqtO1bWqnjtfrjH0Xay+UznOXWW0rOaCwNh4XqKtzS4LBwNHo7zpypvrdswIDbjYMe+LL34TfLHuiWn+DS4m8zJs9xYeXXnj5+vyV5bded+xy3pL'
        b'uVnvv545dP9icIXU9/umG2ExH3uXJ9htatcquVN1Iy/pgw7Xg1n9LovrmI9n73+95VW1f/0mK+pvWJmyxrF0sNVnICU0Jvvkxn9tAs5hy8IG1nUqZFWOwDSFxv41uuwG'
        b'4dGsC4ols5w6NQ9kHVYsV9qqWez+9BMfv79L+bJ2fqiizqKyBVb72sNCX7Gc33N9xlPRzXpnHFZxuxufKX21t8LWTbzo+PuOP7xuYm0ZemxrWu3FKzdWHnx31OSz+y6V'
        b'v5Rtmzn8i3f9hVOtzsUObksbwm+WFV69NaqxvMd7/+/n/tRu81/Zc035ltmtl5JUdi45ti0HyDJMLEoydAt3mn3+Kdjz4ZtN3zZ/7zXb9x3/+xck3ed+rDzLxL6TPfKv'
        b'QT2HV1K/dMm7uuCGEftxi/zW8LKTC19xGzZ2W9UIF87+oEe7vl/9mo3NtNv3uqZf1gT2yufmz3Q0D1F9uvpHYcGde5b2AZ+6rrmeX7/twDKrkFlfuFsZDtmubj08a6+1'
        b'aq/MtNLhi+G93a6ewz9Inq0KudicNrSPWR7i/IL5S/cd/D+tM4+3PX278CnR4vmnP/2h7MI3kqFB7o5194Jc39vbv9gviku4Y37v6et7XC6FmL/w80wj+2b9pfbnFv6r'
        b'N+BY/Yt2SSuul3x15PMPwn4fasjNrRj4+o6y1dq7VhW3Fn8wYvTG+S0xH77yXPu7t4069ysvG9xhlTg/JPXXgGej9nQue3rT4Ej352dORX7VG+p3Y9dPO9pv6f3msOrr'
        b'U880be59Zsv5HwwiutMX3Zq1PLRyVla2W+fvFvvuKebPEgeo5koXEI9rp0BsP3ysByP1XwQ9IFNJDW38/VRGOA6q1vMukzAXFPNukyAXSRl4M5fBJhytCyuMQqQpFlKN'
        b'cQlMJ4pLHOiOnOy0dwhcIk57AKdcJ2d7V+A5WEpdnkG6O1XvYsFZ6gnZkOo84dg5I2EsXBx160yIpWLOuc2rx6VsImHDdCS8Iyl7ISggYp8quAAavWg06iNI7HNFfOgY'
        b'f6UNnJLzLomwcw87Bx6LIm6JgTqwdsy5WKYHj6PXh91EVpkFTwpBty/SFPHwLFkO+sVI3yii78eEIylIm0NS7qlAqq0c9YHHsMt4ghQPLBK997Kwcj8SSAmm7Aro4XD4'
        b'LeyxGLUbDGy0JE+VgrMEZIVjp/li99EV8LTKXg60MAuoTN0ihCXUnxEpvmnUpxEJSVlEUJWqxCMxFymlm0CDMusIOnVJY37RPnxYMxymPg80rkmkkeL8kCTZBc+qjUOI'
        b'qOOrEighgxStNZfEcmO2gipq98hYqUOGfs1ymRjtEL2TwsiNKQ4COyJBeq8K4JUONCSlvL/7kvlkduPBaXh+3EcRO3FPCpChAKqox3wZbIMd4xJy9AoGy8c6LtSrFO2n'
        b's6kmMPcgiUdk4s0SuluJCCxXjgP0Q6RIZYIM1PEmHJtpEF4gIyj2hl1YxS9EWrg5RFQNkDpQDnI3UVfXo6AaZIqtfBLpLUm+LOrGRUZTRxBlSAOKz1qxHSuLZLi2wPOM'
        b'kioXCkfAUeqbngWH0QoiUexoDDtPmEPD2LkvTML7VxToEj8W+8ADH+AVUIDBD/0MDTEkPzBJfUU7eRdVXy/yEaVwmDU1XoGdp4O1bqK+DjhQDS3fYD/WU0Xw9BZeUYXV'
        b'W8gwRiib8yYc0WYSfxAtVn/yHinROx+QxOUyKoev5JOLg/rFGF2FRQA2AVYyQj8Wn8hTfWtrigN1bwUX5vIermsOkwdvQBNxnodagD6Ss2oshmP8bEIdoNozZWwBEtIi'
        b'y0t/OmgKE5rADgkhL8clPtg/l2zjNiCXUVrC7eJAFtEjDoIMbuwiyFkJJ/wmZusLYfOm7TTozNDs2ZRC0UzjKFoeW1S8OVDsEEMU9HnGoB7kS62w+GYJciebURZsFWnb'
        b'IGrCctASWLRmgrGCY2sm89YJ599gkEu0TTliJRloYC/AxkmioiKjtlWwEIxoEzjARtANz3g91CxsQ4vQHOYogG4RS2hVHktADscWoJaQpmfFpwYTCIwRPQ9RyhjBsXco'
        b'LMYSVJlSWIwNGJFq/T9Um/5XcWQmx4mxHnNo+ehvKlCSGAlRSkTkR4PT42YipWcGq4P+Y/UHqzg0yjyOPY8VGSVOhSRjV7pnqKiUqIOkfi12hkDE6SNFRwtdITE97gtp'
        b'+mlO9KcSjt2BfY/vi/jvVP4UCSRYV7iPtIb7SgIlTk0gEagQ1UyL0yA+wrg9JQU14neshRQ7LZLQXZgmZPH9TDrXILz/sNMtUZ94VYn6+BLd5n/lPMyrSlZThvv63/dJ'
        b'MS37O57D9CWu4wb1H5n/XDcQ4+9DkqhmGIjB9jjvLEmBTjKikzzoFejXqCLvRzsqmezWOiqe7GDqhO/GlqHEGPzLBf86gttRHvfrG1Xkne1GJZN94EZVp/qeYW8n4qdD'
        b'BobOg+7/3WHEhKfRLdS8PZ6XNIYGpxGqWXCmLLeLhpPhBP83fyVCicBUQJSreFgMiyd0YQ0jHl7NTIeNwrAVIPvxDl14QkhEFWY8P7DiuHMX93dzF0z17cD7pYR50Lkr'
        b'yjcZZ6IALS7LbBfY2SxeuMgWbT4dSUmJKQnJcrQFdCDG3ImkisuwB3apK0lUZjqoKauKwXGQAwpgCTy5zh+egKc3YqccOCAWzzUiL79DRFCO6L8MA6dwjhoB0q/1tWGV'
        b'AA6Ck8toAgBwNdgW5mJQ+kJmITgD0wgAXoDavUzqoF/sUgHISGS04SVU0Rk2JWsw+Bytwd02xhS9hg1jsxL2JBNbzAlwOmqsSXBewNfDDR4Cpck49qYxaNppawX6Oezj'
        b'YqsJz1OviAGYsRo1hesJWEZnngCWGKLtuHoRaWy1TMPWCTSIGMaOsXMEZ0kfNyCBv3PsDUM4VFELtZWP2oJlhiQ6ggRUwRpbpJTXonlexCwCeW7EDyoWdmrQl7OGTUhS'
        b'PC7gGB1tXLH3COkkuMLCPluhDaLrxcxiVVhIqqEt7RQcpu1Zw8Y4Wo9F9QLMSTdB5WovW20wiCjJnrE/sorWagFnbPluKoIaNB5gQJDshBqrdUjGoetd/JRtQU8SIr0l'
        b'zJLV9NAl0uMA7aDiHNQC0ghQI2tBCWklBZ5fBLost6GPDoyDbQBpBV6OshkbeDgQg4bBhJ8w1xk0c0M7PCUDXfAqPIPmbCmzFGSAc8Q1yzoa1KPG8FwZcWS2ZsLTcHDu'
        b'Bhphog1UO8tBGra7MW6M2y5wmR6bnFyElKR8QiCCOXjgA3ZgumqHw2QIDTjYIw+DQ2ieVzArwGAs8ZoQ7IZFMkKNAlDjhAd9pRsc3CchVaxgGivfHIhmeSWzEp5Br0tU'
        b'qQJwfBMdP9QYyLKyVtxFxhAOznekPhodSNToloNWWIPznDCrrEF/Mj2MBoPqZBxRTZGbtaIWna4D4BIZeWloqHzbXjTJq5nVMGcjPawqB1dhNf9iZDTz8cKBNTPocIIa'
        b'UECmgQMdXnL0JDTZa5g1bnqksyaGG8n9IAMpbiLYCYbxfF/E9RqVyEvOBw2Ocqy3ofl2Z9z3bSH1dA1ldApgpxE4j+s58dO3AFE7USvOoBEphF1gCFxBRQ/GA5zwInXV'
        b'YPsSvr8wXwU2yvD4kDUHC/bQOWyBxRthl4sPmkJPxhMpeMXkRG0letm+8aG1tqY8Igjm8stoCLbT6B01oNIACbvHybL1YrwOwGJK2yedYC/peCbsxCs9H4n+uCpoXkFa'
        b'PgyPgn7YpQYy0ax6M95i2EkYRdLWhDHawUBn/N6J/KQegRfIQMXF4hAd8AqS/hkfxsdfTF52vwEo5wkItVKPKzrRSYVpYsLRwmArqdgbhibWl/H1VaC+WSe2WE1Q0SVQ'
        b'pghqx+emeTclpModOP5tNFnBfowfrAInKCFlycDlMUJSNCZTE4iW0uA0AXlNxJlHrGAXo40m1Z/xR9LuKVrvPKLNPFrLjV9ca0xRg61rSV+RsF0yX6wPOhiSWGIm7Kd9'
        b'PemOz/YwHaXjYB24nycFoMcV1bwI6gn57V67UwxqhWhG1zJr4aALYaMH/aaTISW1nEhzErS+YPpSMqRIIwCnxPBKDIc929cl7KIBWE7D7hXjBERZiIBZGkSJANTDLro6'
        b'UdODYm85msj1zHpYa8YnY9k+a3xYef6N9qHDdC49HElVmA0L54g1MABzA7PBB/RQ4skEF0AmqQEyE9EkwvOgGLdYACqog1+m/nYx0qrQPG5EqkcNP6irYXYg30uQTrcl'
        b'/53oJVsA3Zlg5o65Yrf5aAo3MZvgyeXUq7drHeJ/mMQFAkbHXgiHUUsr0LZFajQyMF0sl6LZ28xslhyib3YMnFTmB0UQB9Nx1M+xzQzp1L10AusYXcR86khIAmYLaE8k'
        b'L6y0AO1NSP/MRdOzldlqpkGoZB3o80U3Z8NaNP7bmG0JYIR8HwNzQAcsXQ/r0ZtaoYHuOUCXXRZ6SjoshZXzaXoeAWyjF6pAMUhflwTyGOL5iPhCH+3OZS2IK4yEoxZk'
        b'jGymKv26F3R7rIOVSFdl5jHzYIEO/fqMDVripXrgInrxBcwCZ2vSnaWBs2Ep6lCniLh+gWHQRXe3ho2gYl3ECtRJU8Y0ZotUhfLnMxqIp1PeAUpBPx4nJ7KDDybOp6tg'
        b'AA5E8WKI5epJu22TMiF3xAHaQA/PDTJ0Z/Jsk5CfMcxN5rXF7KVkzjkjFlf3jUIPqAF59AkNqL9D/O6HeRDSKwW7KF8A+UtJP1MNPPjZlKnD44owY4zDIgrPo3to8yzs'
        b'OUp4Szp5CVawHpyDgzpoBDDXkiKJKovSOTyurk7aoM9AL0BvWQKHA8dXEri6Bq17nmaQUl1JOoJeNXf5mECwAr8n7Id4g0cbT6mUpUN2YicO7Y1TH+L8aUrgEqcACxEx'
        b'tEg+J7JkcaKLVIW4z32xgGZ9SrOOib5uEUV96ubPlpAkQPG2u6KF8xXpl+/aKGNHuwVBUeEWl8I30y9lxtoM8SpcemB7k91K+qWZGvVaf0KcanE1cgn98rUodQYNk/6r'
        b'Fgne0n2h9Mvnl4hIGqAgNsTiQ8199MvUBE0GLaElGgt3S5wszOmXx7WJ66BSkH6yxc+2gfTLCj8dxgw15LIm1MlgvxH90jCFuA4aaWjtlzAGfvTL55YRJ0NmgWCfxYd6'
        b'TgxxiA5NnUbSGhnJog/d2DYPKYvrV5MLq1bQR3ynGhJt6ZxK75avo33t0E6J9vVbzHxeUY7/Pb+cNBDuTBMafWQcbNGhrMt8bkv+/bicrJXAzZFoPs/Cy2glxjFx20E7'
        b'ZVGNhmBEBoas0Qrax+zbhhgZDc5FVkadZJzkwLHZk0mu/BAdky20/4xblBO3TIO+aYcxPyYayTOPClQf9occDzWGGVsE7w9J0yeNp00aA9+MKkTGhobtS8TO64/Km6SO'
        b'NHQ5/kqPITk0FdCu1i7zxdGriY+hj7cfkp8fSD81OfUUuBQJLsEKsWsqLCXdv6e4mUH72YIOxSMz7CRCNCe+vpFiAx9W3oTa6XyhpLDkeV+dAJ2sb9tuXa5oONuwRiNi'
        b'ZeX8p1hFjTWV7Co29wexptYugeMrOxY9syt4bnCLR7JkW9837/4gupoum/1E231LpcGkgA+v3Km8XyD9Iuzn1U+mDzVrupYVGPuaFs9dVvecqO751aHPWVQ8N7PieSeV'
        b'UM15nQUq1zI2JiqOPlf17qpvnjFMtP6lLerta8dTrqqdz3TK8f1BQ610TXyZU9bNT5Qr5/rdsNsv2vHJlqTSz+Orh9PyQ9WtTpxOODact7NT/Z3nUrcHvrVnhn28dl+8'
        b'wd4FaUP92b/vS8s+d2VRTNnsn3cEvtJY0dXxvO4nX7n8HrvDeuiq400jz6H8NbOrvps1XV6wuOhb0WuDNu2zNRWPb9vgc1ZJ9PtbeYaz7QKW+37lv8Vjvcn+DRv1n9E+'
        b'2DJQU/vOUw0nc9fV7xkMLLzo4/axq/f23NyXZR5l61e91bPxrW/3zViddGbuHCez0h9upnp/vCjmx+zXqhpcP37dP8DU8vnfzv1SZHz2SbuXHUoWF5acerPV8f62GX2+'
        b'1jnBz3120X7DH8aGq2vfDGncNtC85piews8fBBcVhGbs2xFwtubraw0vHe/IlhzcV91XGjFvzpaCzh+joxyjVll3b7LX097YV2+4Z0PbC3bHtPf1vHTt7LtXIoZON2zx'
        b'Xfph/ve6f/SqW7f2ZJ+KmmaaUbcvOSbx9vtdV6K3VSzc9UNJ6WfS7IGNTc+9d83HEDYU172sM29a3XdrVZKf1alLu9Hxwr33HSVntD681Gj1Y3eAgvS1PquwX063fOk/'
        b'8PLtsKE930QcevvaTyElt/Iazz95oH5XxDNCWVnd0XT/n5PbffLW1ra7/xF+8v5zV7/L1fazMnVulKp+9PNat7z3f89pe/XS7ZcXbFjfsCrPdXTT67vua3/228+bPnUs'
        b'ufSl9Nkb1X/+Ifra6sm47sGAPzb+kfGl68nKPwWe+eLFz+lK1chh7q6UZfiUFy0DBUbhEOwFfSysc1lPT6+RtrMV5hscIbEhGKE7C7pM7WhgiAIJbPQiGQK9dsB0HMNb'
        b'DM8KOPSAclp3eFsCevDgQpzSVa7ACFTYhVuVyaWliqBCxrghWa0VAyNCWTCsD0+Sg+1FEbAchwryQMpbh4WHkBGncPBsoiY9UK1WgJ3jjnHYKw7WivbDkWDyInFwBF6U'
        b'gXykEhdZo+4Ik1mYq2BFnZc6QJ1YZgXOaeHENRzoYjfi5J30LL1HF21P+S57qGcc7xW3IYB6AsFjMSRSBWJt5ji5goiDVzZuokaSQuMdXkhOGSCuOKjBaSyoNYH9xKnQ'
        b'EmkOXn4aoIHPxorYTScZOOtAUOcFcnBGjLE0SWNJkqRSg/9bH5vHn0kq/sMj4lEVeUhwbGBkTHBEGDkpdvm3EcXH/gt98IElOdulPxz35/iPgPtj/EfI3Rv/UeB+H/8R'
        b'cXeFIuFd8leR+238R4n7dfxHmbsz/qPC/TL+I+Z+Hv+RCH8SSqgjj9L3Ek0VErscu+eosCYCGuWbRgXHkcWFHD5/xnfg02V62q3BarH4iE5HoMEakboqJDo4diTiyCcV'
        b'8he7FpmSXKu4TEp3hUomqP5cVvg1er/fuBvoHZcm6nFj552CUUFkTMSkI+e/OUHTxv1v8LOGsP/NUrzL/g3/GyZdv/sRHjhEwGuHLWun7qEKjN5OKxehknTOQ1FqVcZ2'
        b'cxwcYhLqkeWBZVy4ynh0WuHfjU479eARHzoqMQ8ePBr6Pv74E5+Aoz5w4dz/AtHKPdS2gi+RFWy2YKHuVyNFJsj72XA1JlnK4JhTZSTdFRaQN5nxCEkzd4917piTeCgw'
        b'9gdFZqATZEVma33MyfHRJZtV8lWQe/CL4WYffxm0/YmO4vQTNUcXHmsqv5x7OdO4e++ZdFtVJnZE9PLAcSlHmCWOAVkPekCx11joHJETNw30mxE7F7pwDpZNDt8EW5jJ'
        b'Zn6YvnwMa/KIo/BRccjusJA9gUT0Iuud5N39W+udOaJkRp3rDswOxFGbA3GchwnvtElPHqN9NnIS5XNTCHz6OIHro0+6WNhz+tsEzqSrXXsEiWOTRxSswmFDccpsUEBj'
        b'meU/5FWGAVA+sEgE8rDVuB7UbcQnq/piWAWubiMYJC17mO81I8UCJ/cpEDKiGZwKqHWmKLOTIA1egWkwSwZLfDmG02SZACoglwuIxqN/TSFIItzhhFOP4s3IA/aDFpyo'
        b'qxK2+2JwnZIfJ/ehgvaPM1Sw8rHvlRlBFi2mmowca+kD1p+tU41PEDDcRvbyAuZaKdES9kuI6mDW7B4UbRiox0TjsdW0F2J9imFWR0ePeNwWLmXkWPy/UOK8DsRvSP55'
        b'r4ARKLDzUj8krYk4qn1scguSDCkoMnIseO/WKLnJfW+AcaRipSJyX54CUUiCzsqCogWaYfS+z4dlNxX89mFAtJpHkxwL6c+7O9z8lMNqd9Qm/e+U5HgHPdRqs26Daopq'
        b'/HrUniVrcLEsgJXjgTv0iQ+xYTeZefpcdxIw2pcFnzzxFNmLCH48ZV/cG+rP/+Bs8TxaSoosZ2OuSdr9LaD/DSbbG5ENI30vaj35zl/91BtCMeqCOWOu/xb5ak5FbD4b'
        b'voVhdjA7ZrSQ7j39zHD+a+jvx0y837HPy8l3G2Q1+a+hSbrJpAuyah3ogc+l+dgr38MCNOAsObDAFmmZIJ/zXAvaI0cU+oXyFsSQAozDVq19KfZNF0lvxMehpkPXT50z'
        b'ly77TjKzeMn64ZUy428auI1bXZmE7yu50WuC2uPFw4qbqo9u+uiZ+l9C59m9/tTdz378/JWiO7HqfUUnrvcVpxkHm2ZZL9n+WXiGt62h2RtHb3utD5vxdf7Ap1FJy+/P'
        b'O33z4PzYH2wXRG5P+APONmrRs//wukL8u3dvHGOe1Qz4Pjfc/U/5S3Or3zNcfdp84fCNk+u7DBYGiIx33jlw1q25/rPSNoMPdA69MTsw/27TjUMbl6gvdS+UeoR4St2D'
        b'RkHxtMNhTrc/2rziw7Uv2t0+Pew9a+buEyV9J4oz7eY0rzXb4hqlPA++O/Km6ydrHXoc3rWb6/lFTXb32hQd6xa18K/K6jbs8Fd/YcSmLUX05sDuKgM4r+Ll7oob8Nu9'
        b'eZ/dVcu2Ta27H5Tw+76EbXdz3nth50ua587O2Tnt+OgqC+eB0sb3N88cvZ239M7SP0Ycbbx/+/7mufsntVV891z9SP7Sto/nvz/rpvbVystLrp35atOtoddtDxzdcUi0'
        b'99cvv9z09esv7+mIfev6j7eP/+5aMRLtbVtltW3u7oP1raeXTh9OfqdCrvr918uqQs7+dN5SqsHjPOxBgZdYS4qdJEWMKIIzx94tNCLYZb84HBoTNCyhQEclUMzFIUaR'
        b'TpwxNipixlHog5Rg4ULWIBG0wgIbUnGOjie+VHAQ5Hng4HOKqGYNl+oGMokjBegCmfvkSSkpqmqgSF19DsyEnZIEtM3CagGomg2rqKNTPyzaJpuQpB2R/D0M+uAVHh+w'
        b'fGYSlk99sJ8/B46ya+BZEXWO74Q5qjIjdU9eeBWt5XQ0vYhcK4Ele7wmZFrEdKpALahZO5YuKDccScR6c/lGlcUcKEXcrYo8NmUuLPFaCpthvtQSO3mKgrg5C2PJY5eC'
        b'plRZMqgZx7y0crY4FBv1d2sMA0PosTDHA2cEFYPLnBA9tgoOOlIhvTkFVHh5+GiAU/wo7+DC5oNzZBACQDdS2OEgLJ6y1V1SI11aD4aXwnxwQhUxbm8pmj1HTkc58r+0'
        b'2f8nLtFTxOWJnY9sn9X/YPtUmy8kwdaocKpHwqgpkVQ7WOwUElEUC5c0cQ6XJkFiqpCIp2rkXhGrg9P2EPFWg4imEnQ3FkS5exIFCRFTVVjDN0WWtBUVslknzhgXRhVG'
        b'hfHBSbtHhaHBScGjyhFhSYFJkUnRYf9UPBUkzsTPnIV/GYzv47gdnX+6jxuOPmIfJwenI+6g8oF9XJHR8wGnVYQ6ll4h3CQpDndqXEDEjhHEOs6GC8ZjHnB/K+bBI0VE'
        b'IfNw0BMpxb2CSphzEGm9GJyeC4p8kEqIKFwL9AmQDHcaXI080lvCyvEyWcgu+iroi6BbQd7Bt8NUgnPCP/JWZAxOCNZVRU0KkSJ4rAvDqCqerKmkZ/4PSE+yO9FwnAyE'
        b'dNJmTfWFmSyecQ/OLa684Z/OrUb5I+aWCLHNhljE9aZDN3WG561QWA/PgNz/JxP8ULwV/E/w0AQLfCNXv+EqIEkSSgqn05mLDt8V6h6MIw3Fo67Nfk/gqePxN+dO/l/N'
        b'ndqexNkPzt3Mv5q7mVPnDlfe/I/n7tRj5s7PDbSCC7BZ5vuIuYPnFILkoP3xc4d12Gw8e2y2MFz4384enrmHs1uo8NFySuCAo9eYAM+CRizDw35nIt/arTfkDgmZBR8n'
        b'3jiyz2+nEQ0MgMZM6DQgQnKvxaDtMirSf66DlET/99WY+ODl7fNCGGLy3gKb56wDbQxo3I59lhlQDYbpgxUSkOBst1vIGAVFl8U50tsXL9VfZwlPwaPqMncPASPagji3'
        b'd+RX0t8E8r3ocsO+/FkFjmrcQsnKiMo/RE054tbuNR8tfXXt1rzuedGRmyK94XQtX083+wN+cW7mMz7QkjStX6y31Hdho85r3fDEDTunS0eW6u7PgU9vLn3Z1OBWnddX'
        b'84L3xVS9onpYfWT1Hbhy6akQ1dAZI8M3bJ33PzvvPqP6rOEKNbFUiQg6IkcbmaUZtuWAjAgRqOAsXeExikmdG4MFJMuNk+Qj2ALqaczchhU7sBkItHmQJMw4Yk8BklTg'
        b'IMgitdUXzvayMDOAGZOSbSOBJJ+eCJaDs/AcaCFSDMxlGUUTUSpnsk6dyip1Ajgs88S+0DgGDH96hwawmFaul4BmmbsFbIVH8SGc0B572A+DNHq1OEFA0bLgsvMEWLbY'
        b'/aElihbTX/qNjUow040PDQ/EuyY9HfsH61YpVo1V40hOOw5t6n9gz0e8uWNflvHVHIrbET6A23qoo1yiMa4TOtYz8oht/3RNa5U+Yk1jO3uiP6iivNjdA+SDTJBl7U6O'
        b'N2fDo0LYALONHmKayvxf+YwHkqeVCcokZYrhXChXyJKzIm4iDFG4UqggVHhUKZPdKgxTCFUIFR1lQhVDlQq5rSJUViZlFVJWRGUxKUtIWQmVVUlZjZSVUVmdlDVIWQWV'
        b'NUlZi5TFqKxNyjqkLEFlXVLWI2VVVJ5GyvqkrIbK00l5Bimro7IBKc8kZQ2c4A291axQw6NKWzXRVZNIJkwzk6lji9itmugqPhtTRjxtdqgRukMr1JiEzpwzqugTHIvd'
        b'Je9aTknVg3N9GcXQSzSR2dRUPkjqxCz8IVaqPMbvVjJ8rCfiA0iGGG+JyuNMVfh34zzdzfy32aKm9HYiW9TjcjPh9ULTQ+FPOAtUMH2E/8rVRuGR0Y9INDWFwjCNP+pY'
        b'kKDoVsEB0IqXP8kg42dJMrhYK4OWAHfQBnMsrFhmDatonwQyCPQtCHSAGnF8wjp0aaOTFw9NW6+EDyhwLugCEt6LCTFSksALc4kXw/p4MxyqZ95uHz5SD6hPIHtKkD/s'
        b'k+GQKMe9ohXGEvHuh3n0cHUQHoMnZJ4+NDw7qPeUsYz2fAE86wqryXMNsAOXl40nx7DwEmMkgn3qR+iRUjWodaY5prldLGgCFQsloJCGJ0uHp1d74bD+Hj4rQCnLiOM4'
        b'WH4EDFNDbrE/KCP8F6OW871x1P9YxO3OCdz2utH6pdvgVS/Q5o66hZMCqHsozxFshj0i6t3YCa5q8weNC9biNwJ93EF4ClRRv4N+eAmeReqbOcydCyqtOXIqAtKRotpK'
        b'TrZ2wB5LPmTUTlDB50538CCeAsYgHSl2+d6eSEKo45Ods4jtN8KLNBTROfRufTQ6F7eT3QTTrXHyZRrDKEN7HgnBBWvgRR8+CFcy7CCvZKkIL04E0VrpTTPXzwet5JQs'
        b'GC0TJac+RcYlyHt4TgpD3F7cQO/BdeSFphszxqYwjWzWBhHoVqN2fGu05wYPfFxHfEU7VfY/ECsLB8oCR2c77IRnSM3P1iBRQcdYgEWFmy6WdJs3PQxO4eBdYWo0Bz0L'
        b'BrcqknFcD1vBMQwMHw/ctQ/7zAl2maFXwmNhuweWkdhd8KSyJcuQ4F2w0J1IXNOdcdyvR8XWghVo30tTCF+whE7mccFyTCnEOQPNlRpoDIXnBTs2r4tMXprJETRT03vM'
        b'4ZJlicBFcqy+J+hJl18Vrcs9TrZ8InRgXlJTWKUC/dvO9muuCk8UDr0cmXhh99OfRZgqF96rtvj6vVdCTHujo+4uXvdZtOy7+F4/g29u17j2Wla3RWn/HCx/0entXwsq'
        b'L7ddzmCyf5+zX/sge+iztIPvqe1dVZo54+nc2NZvuwPurN+74c6GbW85BDYcsLz1stFvqT/AT378ZM0t0eDBmyGfbXaEejLJ5qu/BzyhXRYnYf8ozE++HRTxiUOA/cn3'
        b'wgazUz954pWZdtrL7+S/vT5rYfJp681hp78sjrn45FMOAbYBsg0/2u1PyDeK+ObZ9+oPPSl7fu07W8Vtvt+8Xrg3d+glz6UGipa18V9G7plnUfbdRiXpq7JT6sB9vkby'
        b'/C11W8o63bu+yO/U+GPavD/O17WU/ZTf6V5239Rrxx7L7tS1egmbzL48m3juq/0/3H/+4Oc3NO8OqefuO7XhjrN0BhF1dJBUVIo4EugD58YFElisQi7OAMX6Xt7mVmRH'
        b'RUxbHM2h5VA5gxyf+HqYkIgCOKXy8f+Pt++Ay+o+F34HG2TLVnGzUXAhoLjYQ1mCiz1FQIaCiILsKUPZe8qSDbIkeZ42N02btje9TdM0SZM0TXqbtE1X0qQj3/M/5wVB'
        b'MTH29gu/KL7vOf/57AmLTMrCElEmzuIDLvFHI8SGb6ByFoqX0vm4BipQjwN8D5IBEyx7rJ3DkjMgVxqHt2znLWEz16GQOX1Y/3EtG96gXXiCdwm3XMA7pGrzhM0DWu2I'
        b'yiSLsAHzPbkMuZ1nOOcu5xDNjDsCU3Lce7KZCVyPFAtcxCGO5pmydLQWqYNmfJccGBJiN5R4WeGoGxE9cZzQPxgnua+2XidcZzlGpufdWXWJViFJlyq8AFe4nVnwvXia'
        b'RwQtVTpafMAeJ/geGO1YJykztUT0sMuZHlPfL4Z2LBFwKUNbYAhyaQwJ3YMJvMMeyRDTFc3jGJ91Nu0Oo9waGPXz2A3ZtO1TbNtz0Mwbt2ZdoYz1hWD0z5IuuV8kUNwu'
        b'wjbdrfxKS6EAu5ZKSuj48Z1+EqCfz7S8Q6T51nIBWq7+hgq23pQXp8RLce/rKGIf970ZEYw92CmQkRPp0pCzXKaSa6APuxQJ0TiPWcy2gN0sAqwHeznYknEw5LLiXD3M'
        b'sdqHefJLRDgtq85duf+GDaxfvaSen7LP7mNiRyg+xTVYD9e34RU4LDMUPElZHFJl1VRJjucOofWaI9dJZ4lTKsMENEeJD6ru46DgnMpV/rI4soMtGQR96gfEJI/n2HLn'
        b'cBrG5WmVTLQksTKdGSIFAnVlMfRkYIOx9NPNTPLPm+/B/ECcuP6ACRPPKK4LbioosIoRSpxTWI6zx3GVIsR8+2z2o0SyswL3jUikzFeP+KemrLLE2sb+Xv6c//lSVU6O'
        b'e0dm5Xff+A775pqqRHB8rBeCJJNJf7UFQO6ZrZki/lWLVaeVyHSJQ+y0nlGXEGQb/HON7KUn1vzsFeY3fl2F+VdpfXzLg+UZlrsdbOG6DEhk00dV95+vvYGk5r5sUHJM'
        b'VPzXNBz48dKC+OmXGg6wt0JSUpOev5C5VFCoVehTp/3J8rRGjnEhUYYxkYYxKXzT06NWR5dP4flq/AcJvuYGXl+e2YArGJ4UER6TkpD03G0dkv70dff98+XZNkpm4/s4'
        b'PN/uJJXp5YMuJYTHRMZ8zbW+tTzvTq64f0hyiiH/Utj/yQIi0iLCUr+ukcUvlxewbXkB/Ev/9uyyfFre0+d+f3lukyXgSlmBWgRl/ADP3clCNig8IpSA5qkr+PXyCjZx'
        b'WMU9/fwdCaKWjn0JWp868W+WJ968Crqfe+rIpamXzEdPnfrj5am3r1SY2ckvacurp18xO8flHg+NES6HxggKBTmCTOE1+esCzgYg5PR+wQ2hz4rf16r1zIZ90iwu9zVh'
        b'Oc9ZZj7SWPxlwJqNjzkIvBodwXWHTolmLbgfwWFSBN+1guvOHJ+Q8qQ54QmTwtJlPWHpL05NEXO9BN5R+pGkl4D7lUKxQK5QODlMKiFfyrGGxMlRXtrlJV05PYmsexBb'
        b'nlLgPn8p+5rx2mcXQwQ3ZWSvbVpic8tbfRRoExkVkfL0wvhs1j8oLNkqn5mdC7KV1mDoqUwmwDIbHMRxiQCId01J1luEBslBYOXjwTWcqgALMoqwIMaK/3+OnCeDueh6'
        b'/ff8SMg5cjZv+hNz5MRGfhJcGsU5ctzFgi1Tr78k7q77NV0zn4p1knM6sluGGZxdqdNgVeg3eXqSCp/3xpUVv/7Gk5duvFj4WGhXiXDl5J89z8WrfrbGxbMMcOyEdphc'
        b'ffOk0zQ+9eZJp2A3b6KIRYnQZSzizCLmUA4tbgEnOLCQUmEtEsss+ZpaNdCNtW5SkM29KGUthPENMBBjPfWqONmKHji62ehX4dFRzmHuIe4hdWOx792THvuF7k/qvOt8'
        b'ArLsXtLL13tJ83Ub9xeVmnQFY7Jy777a8ETs29pxcEmREnjhCJdI+G3uSkmkLKsguqb2xH3xw5c9fkOrJ/3989yQ8r/WkLWfXMDTyTPnd+MbAwiW/W7fhkh7PEFhj7Fw'
        b'v2ReSCCSvNpCnGyYnBITF2d4JSQuJvwbjL1CwVrMRsbT15EztSkaZAjkhLuOCQWGV94I+OvNGKnew+JkJqu+tnf/x8E/DDWK9AhRivwN/Wb2vkyV+4nzvfPG7sGHkkeN'
        b'KsKN1fP+FKjQ5dAfq3uwLlbnoE5jfbFvrI7WiEW4oHiXWfDZl0+i4YsV322Bple9u1ReE1vVWq8TjP5Ju6Q001iOU9LTbpw3leiuTHHFwivKMCV22pjKmwDmbu7B4XiJ'
        b'UXjJJKyJHdy3WxOhwI0p1byJYcm8mnOUd6GVquLCsr2YGYvVcIzZi3FyBx8kVK6BIytst9EhKlvFAcZ4i3PcJWNHuJsL4ecE08q53hTB6bzKvgCd2GJKmOkCg1ICmTis'
        b'xtuiLdAJ9zmzgSm2Qq+bCw44waCZjEDKQAhjWAaNEhb2jX4xuZjkIO5mOQw6/m25m4YUV4aR+1/EVRIRSq1SHpeGf8TknrKkR1zvID369+dBLfU/fp0au7QSSf12jbUK'
        b'cKyotME56CLYEYmZFsds/kmKInZiS5rHm3JLKsCbMrw0/aYML+a+Kbckdb4ptyw0Ri7tjZ//329EuYIabaFfL7IjY5OwqhhKYgOh6Ox/pvaFspSqopaI95Nk4ZjtMlOR'
        b'FiiEsuAZEczhDBY/wdTVJX8nFz/uaJS5o3NHEC4qY6432YJ1BeoFGpHSz+5g5N8iyUMxXClXjnMwbosRRMhJXHpybPzwdWVCLuxdkcaWClcOV+HGll/+TpokXtVwNe5T'
        b'BW5FOuHqZaLw7dw76txbmuHrc+Xpe0X6XsCeuCNLPzrhWmUy8hryGuE7uGoe0pJOLesKlAtUC9QKNAp0IpXCdcP1uHeV+LHpR+6OPK1Zv0wcvpNzrkpznj/WgEi5QIXN'
        b'WKBZsL5Aq0Cb3lcNNwjfwL2/TvI+9/Yd2fCN3PvSkjdVuLe06A15zn3J3lDm9riZ7ZF2IQrfEr6V26VKuAan3hi9qSxBEvorJCoi6b09dEGrKP0Rw9VPMPZAfycbhhBn'
        b'WMkvmI8xJMUwJInZby6nxhAerBookqR87vlw+ioshemFMSmGKUkh8ckhYUwxTn7MFemSQvwnIUky1fIsIcnLKhUxrnjDEMOomCsR8ZJhE5LSHxvGwsLwakgS69d28OCT'
        b'vk6mrT22wWW+d/SE7xELw+MJ8TtTDFOTI7gdJCYlhKdyy9282tMrscgl0fk9kYOxuuzLcskXdvXLZV/EheJnyr4gPv7emccviTuux7y9S2z80tK2nsvhu3yqTI2jq115'
        b'FWvqa+z+uWsLtzB04Qxb4Qm0ItLvDCPSYpJT2CdX2emGSixCEWuIFpIFSRR3fk1PqPNXY9gi6ZvIVBouJDycQOUpa4oPp/8NQxITE2LiacKVhq9vkGvEgrWc2Os8OZ0K'
        b'+rHAf2VBVudlxx1WnTTCMneufKq3s7vnUh02lmiuiN1QBcNchxz1kwr8AJANfY8PQi9KDP9XsEA+E0d0+aCo0njIdaCHq0nidpYSSO8UYt1OHOZThuuOQY+pLI5c5FKG'
        b'oXY772NuwwIo9DHH7F3Yg2PYbSUQWwhU7ETbtLGYK0QbC7UOK5uGGXHOeb5T2EXj/cbSUIkzvpwjdp37PlNWUvsua5ySfApvczKeihmXQu1goRjs3r7OUsA57llLL9dH'
        b'/kxvLOTakZWZYbkHq1JnwGKjTyXIYhY24BBfimTeCxuSLx+CbGnmDhVAMfZcjvmyUkmU/FP6+mNZy4gK21jxEaX8m6/i3Men42SVbBxfSDXZ9EIFPEiy/qmUwcs6n4RO'
        b'fa/n5FsfKFjvn4w0Oaaq/uX2P7oUvqfWYG2j95tGnQt5M0Z+d/94UHeq/salV83P9o7/9tRP76VAjUesq2Pwhvd+0PYvLfsTrkPjgHrd0wU5avp73vufh1vmz3ed+cTw'
        b'xpu+oa82akfs+yR8ceRn9/ZrRm79gV9EufVrx683vPem9l9+u+lnh5O+/697h/7yM7+6878O3LghSk39o3Pva2iYLv5t/nufWA29deD7O7v+9cmn5b//SPn8/iNx9b8w'
        b'1uSkwSNYDllLIQT+2CbcDXMCXswcU4Is3ovIewdtQyRORMVwPka78QzOS7z4PjISJ36cpKQ6ZmNuEBdtYZG2FGpVCgV8nFbdGSxf8m1CiZLEuQnjQk58dbyOd5b6FkAj'
        b'DkpCsXYb81mYI4nn3fiADWMZgbwmTpiLoD3AiffNlcapY4kHTllgqScDABMZ5ncSn4JhzOXD9wuxD0ehj3RHSyxmcoQM3BOZhUIPv7Q2NfslzyrvVc3AflEmlvJdCET6'
        b'OEKSt/shI1I7Nwuh+aATL8733sAWrLUyXRXsngtdfIHVnBv7JN4+pvcSxpnT2ckItGFKyhmLE/i83HRsgtK0ZYVBRkO0zh87efvCmD4sQImXp1s65rEChPzq1KBWDLf3'
        b'HeCWYJNwgfkEh2UeYb6yj9hj5/kUJu1ePMuqWLHsXVZhkstiIiAvh3JLN3OuFCarcuIEo7JwW48fD/JZGy2+s8eJR5091Bz5LfVDDixKSktySa0wDPN8aUnIhQ5u2emX'
        b'L7FIbJpmaU5ZIixaNNIiXeDUk/FqzxJFvpa/7gyjm99GlbCR4xqJK3EV3Vl1d3WhwVcscl6Ji7A3+EpBJCfxqxkIr2mvZtdrNxlf5sUrvGtf46QU88+u4VPTV3wOdUTn'
        b'v9dQR5627m9j/Zf+eiu0naLECv3EZMt+Nutl9v4kP1/Bu5/T8cb1Lc78Op/Q4aUlJu1lgXErWe0qMzhnVuQiD5fNis9qCH/CrPj/zRAeTYCUJ3xsW0vn9YRRs3mnAt//'
        b'ds/vppZs1rICuSLhF7lToylLxsx56Lz+GN4S1sqlMbz1sPwGo3VSAevKuuMxYEgOiwvi8jy/jTX62PMgglLfGkZJJxrjhAvJTssmyUn2i7uXOVaZrtwn1qxplNbZqAy5'
        b'2GK/Ezq+IUads5QVCL91jPozZhlLeXI1TTyhBe4+oudK2MEvn4U0FrmbuJpBvy8fsMg+8HJnRiAYgCJFmygciMnPVBQmM8wwjCEosHj/k+Dpxh+EGn1oFuIeEhcZF/pJ'
        b'8G+C4yM/CS6OcmXm7jih4M4uuQ1eTsZirrw5TVYT9AQzeZyRkOxXRMzkgi7PLvLjE1cFG2n5r8g9DrzMAd4xrLu5DHcWR5Yhj8GdLRYvhTF8PU9YMqUnFT0rHK62kT9h'
        b'pV9tKPd4HphUb30KTEKxO13QtwdKzuytc1Q51NAF5zDfWMSVudKHcn+3JWt5fAj0Jp7mPt+8I8NtyVCOwxth3P1cTMm1i0KO5vy+9c1lU/nEFyESU/kv6l+r82HG8usr'
        b'jeXmgpe+I58vjHnSWP41vo1S4fNbzP1VFRSkruk87RJXGM6/YQFHn+faVPvX4KlPXQyRRGbGezp9YCH3LBqc6IM0UQjpZQohfuaA654nNEeniBRSmSUcdKVt5Ok696Wk'
        b'iEhev30i+GUNtTgpIiU1KT75oOGR5abukhMINkwIjSVN/RvU2bVZobRnKoMHa+wOgkUSzkskOOB38rS5/+kV8dmPgrMha498LOYeTmVcAqd1MHtJyZvU5NRfpvyuVPQE'
        b'Am9FWSyL9Y4xEL0lSvai1z79L4uPgz8J/m3w90KjI/sjHPqZ+T/ghQAcqRgNuJdrLG209aUf/+CN77zx4klx10XdizrjddmxgWN14/Ulmm4BPnUOY3tLOUQo+41aaOGs'
        b'sSS3tkHrgKkz5m0we5RWUqnEN5OfcI2ThYXVKoUok7Wi5hQWfxzwX6ljiQQuWMMpWdgpz/exG4YHnkxBw4esGqgoVLj7WCqvyrRpYqGbRNwX4ihJ/IpnSEneacDR3Gih'
        b'z+PxnS6Qt0RzY4JWIfDTJdWVRSBYXosEaERLLO9bIXSiEperqsyXg9B7DJdWDM/N2ieJWePM44+k6jVZQJ+If+yRLO1MQ/g+D95r1q2B91+z1qej/BORFc8qDpBY9+Xk'
        b'msie8mR8S0LkUprEfx73j/BzPiPur+2iI0FU/EtzcTLj+TUF3h8Hn3vhxy8SAta0528u2V2Xbb1B76DAEqQybPuMRZJgZWjHO25emINT5lC0IqhUD5ulrvnhAI9st6AV'
        b'J/i0A0uRHgwtpR1MXltyUa3tYDVb4lFW3xKgBTdZiOaawCG5HX4WF9GSiOsqWjlp+PPAp3LhM8KnZAnGPGq8KZscciUiKCTZ8+nWYmZilHAoGU4TkvmWtmIC3PdC17IV'
        b'L8EuM6SHS8rUPxPkHlk2+kekhLBIthA+kudSwhVieays/NK4/1dgz78jOayDzKTMmfvNmB35UmpyCrMj82iYnBITz8f3Mf12TUMwr/Ouispi1n4afC0j9DLGsbUmhVzl'
        b'j4v2/A2IxuD5SZuxAs9k4TYWY+7XsFhXyFnNZU1UufQi6MUBfGjK8o6cBZgTjXfxHs5xNVd+kFrBF2uR0tAXSNULU36QwFlkpeykj4+wmpwOwWbtUjEC36Q/EDTwo7VD'
        b'D06betFo3iwwqgobsC4yZmd0hXRyO32vWjzs9+puBdERJekft4a/7qeqqPhdxTcyasyP/9jR+2UtrfvB1TEGuSkXQj7s+eEZ49Yu53cPF1Tvt1d3ehD2h7+8HG60x+wP'
        b'gx9MHO3YaaN/R2Pxo8rSMc3j7xxTi61Svf+TDfm/y5ELU04tTT753yf/9nJlZ90Hjo1HT6VU7fQ/XKydsOtCqcfrk/+Nv/sk9eLZ7u+eji1zu/TPyVJb39/9ZTi17vyh'
        b'uk+Np9t+ZiwnKbIBt3xMeSOd1EG8w9i9tiFPgHqxcCWzF2M+z+/3XuAb3kzjmO0Su8d7oSsTMwpucnXkfGD8OLMwMmkdOpiJMeMKZ4/TUtM1NZGkDEAdtgnkbUXQqosd'
        b'XHqDcAfkrTQxZtPNlbqZS2yM3rjISQyupC00LZlWxQIpnHdillWocOVNqzP0LStbu8o06nJ8bY5rLPOshro3ZSUJsRyNPfmtaaySKt8+UUFo8JWqmOsaIpTiP/lKSqT6'
        b'LynRNa01yB9NuMpCx8kH7qJvliVIm3j07COBwpP+mcAI9tFvSbAF2Vr/WINkP2XNdK6caZCj2fLLkeG8T9+WRQVIxYXER/k6hsmuoABsS+pLFMCfkXGW28nMWQqcr5b5'
        b'h0UFKgWqBeICNYk7UD1SXULeZQvlibzLEXmX5ci7HEfSZW/I+az4XULeb0itQd6PhIezYPL4iKurI3qYH4z3ufEuwrCEpKSI5MSE+PCY+KivSeskonswJCUl6WDwsoIV'
        b'zBFOxkYSDIODfZNSI4KDzSRh7FcikrgwCc4h/MRgIU91ABuGhcQzcp6UwEIrluJnU0KS6C4MQ0PiLz6dp6zyFD4mka3pJ3wqp/k67sQOgjkykxMjwrgdmvGnvCaveZTE'
        b'EJ96KTQi6Zm9nstAxi/jUTbC1eiYsOhVTI/bUXzIpYg1V5DAh34vnUN0Qlw4AfYKFvpYYPilkKSLjzntly8t2ZDPpbAw9GLBvFdjkvkVkBwQnRBueDAyNT6MwIOeWRLE'
        b'g9ccaGn1YSFxcXTHoRGRCRKOvJxGzQNBKotRZx73kDXHWQlDTz3J5Zi6g4aPJ1o8Cj5emvdpQciSsUKtQp8cZWW6xje8z6gEiS8+Xob7rG3Md3P/TiVKQ0gYHrF0VUtj'
        b'EejzULJ2TPTxiMiQ1LiU5CUUWR5rzRvfmWzIC7/p3yTjSCCTbSWRFAz67RkktFWij4qE6K0WfYw8+QTpOcy9lmyVJIrH+wJhAjFgYH1KmV4dvtdf8cplIcxhj0CIhQJs'
        b'gqLzxkLuO1NS4POYDU4oChKIoFx4DGfNUq3pmzANaXrrlMS4OmtkZGFuhIWWJi4ep5yh3zcRx1L8eQc23DGRP0C6x4NUM8b5c7DdZKXfHhc0nHlF5ZHLPeyCHLRnuHGC'
        b'lIY3X+98ZNNFs/8+5iXgUtixDlr8mGjBPOZSWMs5zfkQQjNjc1dpgb2pDElVOTjM734Ys/CeKVbJCNQhS6gmgBZLSQpzsxtfOdxBJ9V9p/ZmvmaJvgZf5U9wNUTpT9pR'
        b'/Ify2pIy5QeuKRko2gu4jHQP6MJx7PTFNhFX/g+ycI6rdsW9si+ML8uepZ1u9jOd9XwdbmjERhIAS8xdPXycOeOxC5bSTvzNwuk0l2MA6CtnM1d3CxdzExkBlhgrXaZn'
        b'Z1OZjwAqoeTqE2JsqTG2HyeBCfp8nZfdwpCNM/LQGQGtjsZyfLn9apy5ynszOVemD/YJoXEv1nP7iSGhrpxLKYc+e5ZVbqm/n6/YomvF5ZNzueTxu4XQgYUmfLuYrKuc'
        b'4xwW/JfTNFk+OeYd54KUU7BV1Y1P0RRImZnAoBBmM6CCy7iWx/LAR2nd0KMpLVBhad0217mvoQGajrK0bhiDEo/lvO4FbE/dzq51HJv3rZXZHYrVgh0ssfsM5BkrciCw'
        b'DqehkDt0VpIg2Y8VJXgQxZ2IqZkyH36K01i/HIJqhqVc9IY6jkH2qiDTnVchmwWZ3oF2boNqrLo/q0oAHVDDVSaggcoO8AEV45lwi4sqkIMFzmaFudJ87PYgDIjcLIJj'
        b'JFm6XFkCkyQugX4v3OG8zstVCWBYXShQZlUJ4L4lt+g0D+hZjmyFJnmhgIW2KsIsf3B5UKvOR83CrdDlwFnI2ca9HBMc9CguJBAfiGjsNvF5F3k+DT4XHzoy40F6MJcG'
        b'z9sOsBOzORAxdIZJH3Ps8TbXy5QRiCOEtmbeHCBswAJopG8e7vPHCr+TJHPLmAuhBR7AEFdY4LiepPi/VbzSp+qJvDKE7WGEECVY7SUVCV0CkZIAF4NUjBW4+mBG2HAl'
        b'WTkpFUeVcFQFinE6RQgVWCfQiBW7yOAdrtWNAzw4t/qhZJxIlb6oLdDDHjE2Y98FrgyADE7GrHzuaspl+aR1yvuDZARGYim8xQCEu/FUbyjB8VScSL6sdBnKVJJSxSms'
        b'A4yBeL+RFEfEYnACHyZfFhEUK3BjqeCkPI7StOwFyQIEhy/ISO+35Ya08MPO5MuShyXfp14XaESIj6Re4Xp6uXvKLD9wFVpxnF+djGAj3JfacQXnuQNJssPRFeOkJOGE'
        b'GDuwQKBxQnwQ5m/yld+qzLdxD+UK+eGIFssIVGVY2NB9yOYgDNqgWFYRp1JoMUry60iuX3eDgK5UBOPxUMZdpw827aTbzIXb/idPstuUxhnWxXMBuvlWNv0wE+LjgZU+'
        b'WIZ3faDMA2ZZ1c8GIU5Fw0MOlFJwLuOxWTbG0hzSF/loqhIohplknFKhr0TYA3mHhCansS3VikOrkYtYQrTRzdLD3cuPMRNvrndOi4zlKWczRiZLXdyxmNQzuOUnnywO'
        b'4zAuGsZZWUqx4CYOCw+yhq5t0MQveAomiA+MOxPFcDMnzPKUokmaYnaIoUYdmziKXRSmJ9gjEMh9qpBsULtDwg5iPU0EvuxDv3jRRwnqAr5Ph+BvhyW/GDkYS/Fdhu5h'
        b'KwH8ANxmylK6IN2b4IiLDOtKPEAf50AOcZBrgmuZTnz3nOagDaZb1PgOE1gKpXzLoXnMsyOsZ0bDGKLIQ3Cf7/qdq/JPcTL79Z2chEve34v/HwfVoSn7X2W+VL/N+vJn'
        b'd+0rH3R8KvuWquHvt6sq651ocRBM2nxHlKqc/UWWwVuFtv9Qv/Wjd1/4+DMpeflAv/v9n89e6+v9UvruTJKC8A/a5UV3zn4WYPD5z0M+h/oPdlpk9BzqOtMkf/ydcI3J'
        b'8letek532J2sfCX2xbe3mqhkfaHllnXqi1PyP7U8aPA/P/zo7+tdYmcb9DZpRffnFne9u8vpD6+cSjZ58MoBvRf3t6dM7Jo8Nm71foBiSEdd9Y7KoyWBLbHqXa/1FDwY'
        b'/p5vq2p1wfAV6bKcuT3pycX9X7TAgb0f27z/juxO2a/sThX99l6XllO8zXc3fPmZ8nnfv5/wt7078NqWix92DZz4Qjqtp+rnJWmvCvb/8YUfvJLw2sUPL09Le/zXL+t9'
        b'vWYCFgOUTjkN/dXdLmpg68d5f3V7/aPXLc8uhv6z/68X7R4offrZVtvNsnG9u5LP5g+94B9Sg3+uvfzTGFv/t69c+qJR+03nK602x47aT80UnP48ffTtwC/tfvC9d3cc'
        b'3JZo8H25F16It/pbiaxWwh9+Oln96d4PL/1w1/r/+vv4n80Dt/34/d++9cLv/1joc2G2tP9khM+pQ+8aJIz98PvBEVNXXzb9jcdev8qkF9O+E/l22IWh0PVbbvZB5LGf'
        b'pN+Dag/dj/6il5aeWzTYFz4z0vxyWvCV75gWRE59FbL40V//HHi/bcqksuhU1xfaZ+c/F/X+zeSQ/Aenxs013nnXw3PydLeVyZW2j83/cTX94vH5V23nM/47W6Yz0qvH'
        b'4CP/jJfv94VrnU/o3f39+JfLiwYb4vX2+tnr/7LKvmzc48bCn9t/9Ysd1nobVewOzlivT7g59eY/C/7+K6UzG0t8fnL1l38Rtdh1ffrFph8pfRmp86qxBe++rscBGDBd'
        b'HRGh7gLZFmJo2433eS9QviOOcDLEdpjlZAiYgVHOfg2TOAOFbkuuci+udo0aFmDWLjGUYjbkcM4gR5LdFjnzECye9lhVt+NYlCRyzhaG3NxhAeckMiMXdIfV4Zx9yfEg'
        b'THJhYqtixMJFYriNkwb8Ku/gQ8ySWJg2bzovhGYTyOcNWw+s0vgAth07JCFsMGjIueYt3Qx469IBzFmOYZMYl6AhmVubvDTcXa7MBg3YJhSw2myJWMSNvhEaYcjU0wPL'
        b'ZARSe6BPRwh9h9U4u9MNkuzqeZsTPkiXmJ2wOY2ze8lABUyssFnZJEG2EEZvZvBhhu0XYcCNrz67C7P4ArSmztybcViJDW4ky9NivaGS+HK6aBu2Yitnq9txBBe5qrcu'
        b'Z4mnPKrHiy3SnN8t8pTZkpFvvwLRVLifjMV8ZFwOThznQxBNcIKPQhRBu503t89gqGHli0g/kE24RMpDh9DPGPI4257Ccajn3RZSUrKxQmilRXEXfzORtWkyI2GQXsNi'
        b'DzMStyxhdJ0Y7zpd5Ob0xCFdN/cN4uXYPs7TJ41dXFiih+MNTtiCKbzLSVsZB3hwmYbGiBVCbwT0skpKD3GUzxMqImgsfSTfHsNxEnDXQSF3QHo4g3doWDXMWSXg6mAW'
        b'f/SN/jD7SML1hDKScC0ucLGjdtAODY8kXByRkUi4mvQyxwKbQ9SZhEvMfFnAhW6Y44rVX4zEvLXkW5iL5eXb/VDLbeC6VzQbhHdxmm6iOTBLnGCH3fwct3BSjQUxWnqZ'
        b'w7iKiIGjCTSopzAh2vAg9uF4hOMjeecyTq7DEaEV3BKaYYe0PDbs5s7hJHQjybLsYhRN2NXIYYOIGHgF1vLxUg9335Q0KYEiSxfWolsb7wn0HaWgWQT8SZvC4Ck3dhJy'
        b'OL+XkEYgi+0iOVcSERibTCCJvoPoSzTPJV2AL+KzjbYtqbZSxJeI1djK5hVjueI27gkl53T+AQsPLCZZXZhpK9DHOilowiwX7olEfSzmHoFb273MiPvTnYgE2nulDvtB'
        b'KUebdE7vXKMmZ0wkX5WTUG+Rj6ydvWniRnidQ1iKxTzEKEKZCNuxdDOHMPFY4cmZvovMgmTosD1FBmq2fAsUJ2NObeMjcvEhtEqichWgkjvia0SfanBcBXoOXJFQPXns'
        b'E8GQ/gnuJhWwYxtdgLkx1MMdIwYvUSIYC3QzVvn3E5seWX3/g126VzrRQ8LDVznRv2Sy1Lezh+/TESpzAayay6WglYQbufLOcvS/wRfqckoiOSFvNWdFZ9S5ftp8QCv3'
        b'm0hmZekYodTfpBRZLt2Kn7/JfCK3SY4bmfVB0eJs13Jc8Wgpzv7OepnIfCajpMU6fnOrYcG0oq/UxcpCvgsKK32jx5WqUeaCbJXpDWXuh+va/ZWCeA3H5Yrj4a338rwJ'
        b'ftkmnuTFzPLL1vCkk6st+v9enW9Zfp5HA3MzcpNZLM/NeQN86bfi5/MGWLz3DA7cFedgLH5Tbsln+ihXMExK8Og/GcEKK1iAQMBn/PAuAHmJC0DIOQGYC0BUoFagXiAu'
        b'0IjUkDgApAplcgSZ0tfkmTf3tOC6NGf0l7oh7bPidz5O8T0f0RoOAL9ESUDvavs/ZwkPkVhylx2/T7eqLz2xOikoRWKUXjGEmcQ2HRYSv6bBMpT5Hgy5/kTMuPh0T8Pz'
        b'GOGZW2PNWU2WlmdiyCX+cPbSpXXw1m9+ScyVQUuP5y3OaxvADY8lhEdY2xiGhiRxFlt+w0kRiUkRyRHc2N/Ooc0doMRf8XjdobUcDTT82vUxJGbsJSM+s5t/k53321p1'
        b'127ws4l3aHucV3dj7c/55uenmCHQ6dJTgsbKjeVxWBsGOd1aAQdxccl+ylkbmSERC70Pe/mssqNew155KEuGXE6N3QtNJ0yVdSV+8LuweJLv6qioKNCMXhALVIPdO6J9'
        b'JC1YZE76rEu8FMk3YRGom6aeYDJCv73IFO4x0bkQb/swg6eHO8drTz8WsusN1Y+r+WK/ddiDRfrcWuRksZnENFZkbq+HwOMYjPDp7j/R+btAVSTQGdniGRqg+9ImXkd/'
        b'o97Bl/vaS/mM4C2BYJdDqkXmAYP/vcF/7djhwH3bFHlR+D/K0zICw2DbV+yCBbw+3qiJedZSrPsTFFkJrDZBT+pxJgnkXApcZckuNHf1wGpmuSU50UViG3fGYVo0aypx'
        b'ytnVzJUvX4nTeHudKyzs4mzpu7Bq0xpRCZiftHbsnzmMGkuK/JdYXViqn79cPH8vk4xuYRf28QbfSSccN93lszrDXgMqeFvyDLSyzqdPGJN3YzdvTDZafhGy4aF8phKW'
        b'cGcVGiQSSJ37B51LcNyBi+ESq4hDLH+Sf5XyF0ywVpf2FxLfsNm0P0mdMQxmGTeW5k51PeZCLQyw872flC5I3wO13L2qkHrUDgPsuLM0SQiU28M19D6rFWcqy+ypDmmC'
        b'NM0gztyySZ91hhVwXXDLYwQxtI98vmbriNxuLmmnFKeuYwnpWfuEMGyJLZxhSweHzq0q8+lN4l6b+Dx0HeYPrA8e4AKnDcjj6FLxVOxKjglRaxAks47zqlX37E/Zxv/C'
        b'QbX55+dv+HcduhNuW/x2j/JbvT+UPiclPKes7iA6VyF66wf7QopPbd4mmzg6mFTc9GLtp0es3Kxfynrhk/nphF/auU4WFL4v88lvOzf/zqL9vzYZeUyrafxO0Pvhi27G'
        b'ZYMZP3nH2dzjdm9kU0Dz9Yods9957c8vH37wWadJ/amIHeV3/npRN2tzZNcfTl7ZJVwUZP/kt+ZwLF3x7Y+cjjv/1e/wS/Gqn/y+3ObXncovbUlXyvcw60v73Wf/ekdK'
        b'3+Du5jC3C0GHXF8sj4wbDhnIMPowp9v1stPk+4fXT++J2v9eTeyvt9ld/FH/0P6fZ1q7BF3/fFvy6/a/f/V7BU1//sxFd735O9fNdr6z6e2re7/8y+jrZvPh70eMFryT'
        b'e/Sl3ED7qzfv/qywVf2HM23Fr0d1nr3zYrJL44aJH73y84eXGw5sMtzcuqf6sxP+lzd7TirdMpt5d8yreVGcvVFk9dL28116e07PKlm3jP7i6Ctbfc/9909f/OdLr782'
        b'lxI6ULij3eyt4Te6/vG/Ga8MRzv94UfpXyqOhhx+942hX9+cPnX4Z7ZtjRvcq81rfa5WfnY99YPFr8RG43dTLwUZa3Gy+BUtuE/aa6Z4OSD1LLZxovRlmFrvBrP7VmTQ'
        b'ke667SInh9vBgrSiidmqeFTO/CB04DP+SqHOSFIfIhgHWIkI0RZzyOWUUBgKvEG4dPL8UlUJ3W18AOskjkO5qatHor67JGvO7DAXtGK0QU1xz/q1a5AO433M5atdXsAG'
        b'IgbOpIpMLnelhBa8x+slfanQJOlLyTWlpG9GucaUddjP6an7cEqd65iDQ9C21H/S9jS34Xi8BROmUBHrar6qvc0kjnHvymGviek+GrLYktPb5TeIiMoc5r6LhfogrgI+'
        b'DMMg6TusBD7e9uRWFRLNAq4eU+iNoZQUeo/T/LrvW6ezYsRwz11iqVGhXXXuE5/DzjDeaFR3/jinmeFtDyKgxCxMZQTYBfP60EiqJVTxdWKxHapZs3PWlC8I6qQFMgYi'
        b'KZwQcpqXJozLPa5CHody0iBj/fkCVTOHvFerkALLZF6FTIPbfNDSLE5Bhyk8DGfPrVYi43z4+MyskJAnlUjzvZLWDpivzd3keViIx5KLOEWa3LIWByXQ9m8K7Rr/QcXt'
        b'Me1NaWW8Aae+3Wfk/1upb6TAWShxChTfMpLv38NqhRp8JSXi64cqiBWEUiI5rl+PlHDpbykha0IpeVfEN5bklTxVyW9800kpFZk/Ky/9Tn9qcXOpc3+SqqH/eA7Dij3x'
        b'OpcMr+34LWtATOFYoWSp/l8fsbHUiskslmfkNK0zTN9QWqoY8600LUH2rnfX0LW+7gCWgr/s2XIOidbQs5hsysmlrgIuvFuaNCu+lL6I07XETNuKVFrWrKSeSbNiVRaO'
        b'rBU5u6RZPaqnvxwIy8XP/h8HffPvLFWb4d9bo5ykheExPmqGW8pTooG4GHGmftGjLj5eB/bt2s3UnUshKSzmIzklKSY+6qlL4MvcPIqAebyYH//9c2WfyHlyAqixn/qT'
        b'8ifU+Dwt96QABhxTJRbgMRWJG9oObnP18beKAxwvcd6/dKyCsaXaTZB/VeKFprk4OWyLwd5HPm6cuM4V32c+7gznmB0fhIiTb7IZ7GXNizdrwa73CjSlPk947eiR7Bfe'
        b'P+UsNf2uwqn1hQ7nY52/m1TyQU/u5/1XPnr15b6f7dqSnL9va/F234wNv1Tq+Vdu3KZqr0tRGuKd30l2GHv392kbv5PmtzO2VdfyzeKfP9QsGbi4VcpdK+HL8YS4754e'
        b'fHhx3u13EWc+3qhTs8ladqux5YixNMdbUqBUTmIEhypo5zNbxvAhxzu3MOvvUqgrjkGVJLclFCY5u2gQVsIdSbBrCsysqkK+gAOcYwVYfcSuZU5JImjrErckVim3nZc6'
        b'7h7EPM6iTiPOy/I2dejVXpXA8m9xkBUEXjmVQ7dVJN7zOUg8EXk93vrGdwVeIvNyXFu2axseo0CrZ11FhFdToxVE+NvVuSYKy71vv5rMchT2HH2WriTp2PttKawge8un'
        b'a9DYr98hq+p6LSaRmWT+U4Uev+x7Mko1KSw65oqkvI+kKO2qgkJrENFjvLUjLp0zj8RcSoyLYAaeiPDNTyW4ko09XtiGPn6WJiaCNUmWlCdf3OThOgHvtXqksq4KfoLq'
        b'KBLqQ7XlYuRhPGb6r1GiZBa68f3Ef7KE74AX3nhxomK0sDfXWPpl9bDoyLhQs5Dv1sZHRod+ECcU5P1V9hXTKGMpvvR/UWY4a05Qd+5RVts9HOFQ8tCBXStrcIhkoQHa'
        b'Q+AeLzDm7ITBpSj3qyor8X4E7nPlKE5ZQT3rnGpJsnopawLJm3JcPC4zMmGFzfSGGwzI0gu5at/YKE01hL/XJeBKFi1Bz3NgrY0Sy+jZ9Lg19rEZVtVUP78aL1dXkXz0'
        b'BIdqQfRb/fOjmuqP10C1Z1ps0ttsPdKenr6OnkkXBZwQ9/VV6R5VtGAptFw+HZe0xAXCc/ZvTjTjqAe3L/5QdP/T0vgzkvKko/Sr8lKCFStUp6CoJRRtWl1gTlVKVVVO'
        b'pCmUU1EWKihoCeX0ZJhvgo53x1fqNyyE6vGGQrlNmkIu5grzoXknjnvAACw+lrMtEhjtlL4SlZj6J5o1A3KUmYZmn4CNu1QhH6dxbv3+fZAVhsMyB7EQKqFKjhS7Zry1'
        b'aR1UYB60wSBUHz8OHYrEaIuF+vgQpvHhOqg/iBNQDmMhpEX3+a4T4X2SPYbt7eAhjDjDQyd66jYWp8M0sc5Bi+vQ6Q737a7jAvbK4gj008/sXuiGTuyJumy1Het3Yxa2'
        b'x5NCm4t9OIaN1+1J/+ohqWdU2+mynZcWlGzFrGOZsdZYhgswHWOH+Red9DaF6DkedJMOtMqw8ILOQANzpiLbwQz2ks5aEQ/9xJhLYMoZpmwumeBtqyAsXYc94TiiQVJQ'
        b'G1RhB/3MYU3wMWw4aR0LZWE4JAMtMIX5CTCKldjiQ8r5yNVLpN4+zIQ5rPWFSl3suHgWa6Br/3q87wxzu6CU9l4J5WrHYdiHiIwbLWAKGw7AcCYOnIJ6IfZAA97CO9BE'
        b'f9+OJmrVAB22h65uFCvCHZjAVisz7MSp6AMKdjgJBWEGkOV0CXLDaeBaD5g3DnNM2OSI5TH4EBtd8W6gDgylHcEHJPE044i9DNSdMvajnZfAXchT2OGL4zrYjh30r2kP'
        b'KICmADqOu1BrhtMHDm2336apgWP+9EFTxs6zpliP/aoaWIAVMOmbTJ9WKitswUV6ox9HYZiWMyLAWusIW6w/B41WMK+OrcqhHlAelXIIs7yxdiOUBO2Tw0V4YKABD+Jg'
        b'UR/yo+j1wURSx+t2G2BH+Bb/M/aWWM3seNCTHEJAV4MNvkq6567F22bghMH5DdDgCR26Z3GYTqgW78nRZiYIohqwwwFL5aDgBM7uoousgQEb2iWzlU9DTgDdwW3zwwQQ'
        b'xWkwpq2PxXQ+c9imfEOM81jktI0EuNLU2yJmVPXA29DsfQTKCe6VYB7H1193oAvuPQFZG6EJ68yV9uB9uqJRaBGfgJ6wkK3GUBEtBSWGNy2h+0DqtWgVvEvQ2IH3mGM5'
        b'Mfg0LKwPgAYH4i+j0AU5IdhkgrWmO/ABzsK0GEbk8Y4+ToVIJ2IzTPgFXj2MjZk+cTCAjXQSC0a0jSlW5ivezZaGaDGARsw+GUBjVwVA7X6og4JQwr1skY0HCe0j5vTM'
        b'GN6D/syzmRqqATdD9zhFYZNa+h41HKK9lhAs5xBa3NpLeFXktMl9W/oOgrbbxMsGdxOUDxB0PsDCEKyKg3na0wmcgyJZ7D6EVRnQmup2JAaHdmKBESkXi9f3W9yE/Avy'
        b'PvBAZyMrgkZ32Qh5agekEnAxGMdEWJGmFXICc2FcAUpvOEMdZhs4QXkgZGFeuAq0wj0vHz+rMPUduth3xElBU91il7S+tR/hUbM7FvrQHddhvw4UEmHJCsGefXSZc3AL'
        b'88RY5QmVOGqITZ5YHID9MC6lRvBXrA0dtBVGm/KCrNjpQiEOwsTVNF0o20jzDRFY3UsjiCi4pibHnBCReAdnrltpQjWdIytzPkK0a1IuStkVW3XhPrad8ccBQrw8nN50'
        b'HhY83GAReuW3QVUyUYUeyLeJwPFLWBQACxZ6zAB4zgum9QnqBrDMG6rcXNXOXcVJmq+HgKHlLGQTDi3StrKtcEBjp8+29V6QTYc+GYjdcXR897xgzBgfSENd6DZohxwY'
        b'S/0pwaQl1pwjkLSH2wwkadkzpjCRaoNN56Ro2DbMjQ+BtsuKhJm1e0+aQY9qsBv0HYJSnKLDmsdafQKlh1BMOxuDYRfIP0sIm7cFF5wPHbLHOlfoDFdVIO2kCLoJqKYh'
        b'dys0GF4hGK4VHYL5dME+CxesvphiSrc2Dj0kMhXDLCFPFWFdY+jZ8/FEPjrMsDGWTnuOdf4pJmDth06owTvnThBhXDTVPp1y/gK0edAKu7ACJ4wIOSoPb7FKw1JNeVKr'
        b'VoAsIUjNSV1ax+RVzDGXvwkT8RzNvKOcDvVELHuOuO+7tjkMRjwzrmuJLzhBiTaWE9RlR9LmFmmQHiJPOfsOERDXyV6CMugNgup1dMt9huug+gDWO0NbCj2SzcJJSVNr'
        b'Ic7UC1kqIsyxJ0LSvV4Wpg/grM4OgocxmLXCh5pXsTN+fbpUdBxmwV1C2ny8o0KH1UVb7MF5GD9JF9qhhsWBG6IJ3HJw1IGoyTzOn9tJ/Ol+YJoBgW/7JXusCCYuVmsM'
        b'fVcJI0ot6Do6jlgRpSsiwCTueW7Pxb1YaRSL9zKPKl+jBeZAFgFzB4zvNjQKD4FxFuespInVOIs5SljoCC1WvgQT0J5OCyjC20YwydwvcPsadsjqb6ODnsMux0BLeIhN'
        b'Co4mtOF8FtJGrLvxOIw7RXnTZY7DreRAutJ6YoqtMHcNS65A3XnZCKyxj3Sy4Nj6bbcU4jj5qUQYKuiZGjsn7QCshcaLUCy6ogNNBOB0ggTg0HImlla5iK3i7QmujlgU'
        b'vw4rI07LbriAQ3pQy6DLkhC6w1ENu3Eu9TWC7HN4X58R23hOxpjHYVOcEp7YGAxtsljvrSCEURY3XE5YUwcVKTAmIIK7bT1m7abzrTPIwPuyMAtdEU5G0HAMBjSIITTo'
        b'0uPlytgke8kgluCmQYWwsc7KGB/6WThD46kMvGMApa4b9xMvmFago3mIJbInoS+YoUuIMPEck4aa43EY586fJnrBSPAgEQISQhL2QaOGg6m3Og4HQmXwcbh1AmZVsc3p'
        b'5lk6l7b9GRpQ6uMeCH3bceLmhmPBrGkWXcfAJTqUAWg8my7EGkdrmPHdlaF8DLMJaOsOhRFrvkV33KGjRoedj11iWFTDKj9tVT3ifcWaUHHePcSXcHfB+tTBOMLi6gCo'
        b'toAcd01LTbwXB4MOhH2FsXBnB946JsQs6ZMwG34U7jrGwIgyjB/yhDkoPGpz7MQNPawn6CfK2E1TFgguER/owFEZaCM0KNIidBmj07qNTVawAKW6hKlN22EuE6cuHyKo'
        b'rSNuV441dpex4whRlazwU2mQ75RAGNCWCTWZ6wmuJsPTsS9KB+uIDLYTqSi2xbLTavuQAL4Cu5xIPCKQ7jbcT2toZikJDvvTnFSJMx7Xg3EfgsNpmEjfQ3i/gP3HsJRO'
        b'Lo/4Xuv+jUwsS4LSSMOdDBaxUvMwRw86aJlZ0BIDNaFq1654YBPNMsH5JatiaDV9JBbkiKA8lc6+VDeDttdITHSAeGdyALRbYAt26Xit8yFW0Rurhe0ReNeFrrgH54jQ'
        b'BtMS7x8iTbELC20gFxmaL2CNHw1RcCH6CmNCmH1JF8cTibyMYd42xzMKOKK/2/HUhmtRqVUE1nRaiyTmNHvTFpbFCFN8ILyE5SRG2B8wheldMHJFcaeNbBKJsXWO/lh1'
        b'lLYCbUfojhdYZlISHdIUI0EBWyDfGnN2h0AzTV0MI4kZ9kob3WABh0OxlZ65z1JGbm6CLFN/uu0HUgdo8hqYMdl3GAfOk5h2F2ciSMgsJzbWT1x6Eomq5dw0xzvqBLaF'
        b'R89DmyvWeDsQa62IcIB6PxOSO7pg7iDNVk4SSRvMqxByN0O7KvY5Q/nuNKxS9tgUdYlIXbYsIUhLhkIQjGw/eNxdx34dAdgg3FU23yBFZ9asoG6DE5t2yIkd8dZmOsas'
        b'7QT33Wr6xOHLacyhc5hzHu4cASJMh4gPEm0iCQFng7AJW2wvE726C73ETbpI2B+hWxKeNPeHku3xxKcbYdALc85gx7mDUOxu5kHHlgNFx2L1vZxOMTmm+PwN6Ak1xlth'
        b'kKWRYYi1xK8qz+JUEkFOzSkcCMZC811QKyIwa3XHgiMEXItE1IeizpNaUkGEu0hXh454IhirbbEAWlVwOOEAnf49K8g/RGDThZW7AzUj99l4hUJXMD5IOEeEuc1WRWG7'
        b'9X5NXWtjouoTSlikcdxzJzHExe3Q5EcDV60j2Hp4CYq9/QlJZs9B2w7o0QzH0Xias5F22nyBUKH7bMR6IkBVMGQBw4p0nsVYGwVFm2DsfOIF7cPQH0cPDUF9JMt6EsfS'
        b'qrJ8COInrOG2PSzsJJY7g7k3NfGhIA4bTbFmO1Hv1wks7U/TmASU2fEcTC4QTKbhQATeC8SOdGbYyNEgrQ+yd2wgOXfCYJc6VquSQHna+5ozVNzctD0jFfJDdE4GKXkT'
        b'G+9kP5Czl6h/DVESes2eiU7XVdfBYBrd7iy2+h9WJHY5BYsqwUTx62OJ3fZKY1Yq3vWNgIWMePqqMfQ8yTP3ORECSISYg4UYgv/xUB3MS9qE3UYEGh2EPQO+8Vh53ZDo'
        b'QxMTeqNpAYUXDl7SUaQ3Kol21NB5lHgEkrDXn+mTeTo6bYuSJ5Lc2ondW4h69547lKbMXLDAkLcCHsQnHlKHKZUUQpTsJBIrKgI8reW34UioJ96CGh96ZApyZbF/XQQW'
        b'nmINUenjgkRoUCERNxda0nAsiKB1xFLJ1JUIVH2MqmNs+iFSoDo2EJYOE7kp0TeSorO8u4skzgptTbgTb7jpBKHr4AaccSLKVUY6CktpmY1nAflYdXk79mxlzeUxNxMa'
        b'jMyJAD6QpclysMfaKcI6bfO5SEL0bEKInFTChQYFqNqN5RetsdF9O6HDuIZacigRwHnsP4P95wlzujYTCDbtJ5ll2hoK8EFiPHSmkCJeSAqz9i5NIpi1h4nKj9tupWVX'
        b'REMZCQ3SeM+P2GUhQWr1oYs46aeLeVJwB4cjaN5mgrYGwdar9olnkrVO0v2ObjEhjGmGyvAUaDqUBsVbsUj6HJbEQr0dPTsGEyR31mKRP7GJEpJMmjTdlaHVdcdNL4LQ'
        b'Qbx/LTCOpMVan0Mn9jP9bMAGuo8kmZyDaQKp2x4wmhGjGUk0qF6FAHzCHDtPXXfCakcTgoj72lsw29I91g/LdbWMZbjkoXMEjW1uLtICoSU0eAuYhge9fEtjvGfLpRUJ'
        b'Dx62YckDWVDHZ/gV0wE8cDMVCYQOWL5XgPWa2MhFuBhDgS9LDhAe3g/l9DmU7OZT3m5vvsCs+EKB0JWgeUFASDt9kwt+uRyQgSVm9IWzj7kAW65DcaqTmIUjFN6gM6rG'
        b'MsKJBgclmnH4hsKms/JQY+utEqJBXKnSgiChAzr1QohUk8i+A3NdHD0gP/aQljFRmmns1r1GzKkdWlxUj5wl+l0BTaGkpJYShR3H1n3M7ELqd2WaReox6NdiUl4mdEeE'
        b'YIEitCeFEM5Uw+IhyDp9Cu960kXS97T2vBP0axf0soIfBX7qJMI1WtJ9NVud2UZgl72BFIJRk0Aa97bAi+bMiyCiOkwMuJoumnScmOuQb0HMtdIXKnaQrjBG4HCGBJjK'
        b'HXRaQ1BlQ4pSXkqQBzx0I1jvYomCBFVjBqQ05ZBiVmhjfB0KrEl6myUSMcLCGmBkMwnD96D+QMSBK2K8LRuhgnXOF6FvHz5IMt2EMxdw4IzLeuiTvZ4a4ZEURAS0Errk'
        b'mekA6gx0MZuOdoAoUTYRx55zZ2isUjrPmkDNWMLYGVpCxV7aao+9nsJpJWwJC+Y0rwYx5liRIpNFpzKEREYXrViEw0igiZcV5gUwj5EtjuwgrOm1NgWWwdEHFbbE32/T'
        b'frKStFOliDVVJNMeumDh+FmSJquh2ARaZHEwBiuc4e5hbPMjnaqUlJcF2fVYErw5zPiYPg7Kwd1guJtEWLJgrJyKfWFJSdhDP1WZ62i5Rfv8A0iHHCI6XGmNY8ecrqtF'
        b'hsOk0TqYUsZWZ8KqW/txyNKFELsP8pEZd4pUSIWfgGw9aAoiIgA1h53PeJ5NOn1Gm8ShQuLjM9oH8E6SpTVRibErYiIO3TBorgWLqdE4sJ9UgQoTDWzQZjSc+F3BrpuE'
        b'opN7SVZkeTC3jD0jiZ/CtCU0phBAFcD0WSiIJxbeBf3HCXmH3G7CUBCpfC10pUOuBzkLzLyYeEzr2SguLeL2fm39G6YkdU54Mi0CKyNhDjt20R+LuGCoBTURyWYpOiRu'
        b'DRzCBxfWYfY6nBdCywUSru9Bfmovs80UWeg/bpohEnr/kKGDyhUc1JLRu4rt4YQZ2aFElEdPnsViV02tI6S2LEJtEp1lvqKm9Jkgd28iOxXWegQ3NTCsiz27ddw228F4'
        b'BmkDBQE6XuZhR2SJnz045c/ZaMa8NrEy61C9j05kXoF2MBZPFKmD2MlCNE6lwpQxDEOJnSnhRQ82xdM/bl/ZAw3Ez4i0VzA47YRRE7i/K4FE/ZaDOBZ+lk4538Nfmwma'
        b'SDS6+7SQpL15lkZlQMgz6kTsrUXKAHtNieqOY6eGP9zbQiSVFF2HJHcSsVuiSPDMcWCUdRSyM+NIttd3IDGhU1eFET537L2mfkwB+i+dJyJcylsBksMI/CsubqdlES/D'
        b'9htEBmYMCAuaScGFXo8LglgsOBpH9KYJ5lIuHI0ivjCOTRG0yKoUYsI59BJzYTaHhcNw3Mn9OKGtCg+3niFgqNPE7iMW7FBMsE87AmdiCG6YlN9PmsN8Ei5ckLZTxXr9'
        b'3VjllUgkrVQDO9RJAavOIDkqCxYvk1wycRj61LyMDltvI9bbhncD5bDdKYHOvdFoZ+pG4xitk07qatimcTP14DrIPyryJJjvJwAsgh6We9We6u8MJWeJ0N4yhQeaEYSW'
        b'84QXU5mnLxGnjGfxQqP070GS82ZCrhC5bbK/HoDdgeZElRpwwBjmjl6AoU3bXYgoVLM7pnt4SHStnojDkBqXub5446Q7Ddq1F6ourXfyorln9ek85o7BgyNEgQuCpLcc'
        b'TjkGZalvMBUgi5SRXmj2wZJl5fY0jNDdDRIrqN2ziem4gd6KQphUx0JPGJYxh6GzMlrQh0QHJ/YSNAzb+OMCFFvE2BCcVnKWk/4t5kTKmLGuXs0M8oiyEaDmwwjpB/jw'
        b'qpc58S2i4fOHjkCfAdSrGOjRDZTCRDihbOdhOwH06RJx6d8O9TaYtZkI3hgMBmCrHzRaBRLtKXCBpvBAYgvD/kxE6cD2wKSd0uJoO6yxxO40LLKAsa2+mBO/C7pijxJr'
        b'6KJt95Lk2uRIVAdm3LHYLJDZAE0Ip3PNN5+Oxu79688k4UNPAroaYh95ezTloDU2ng6ilkhFB454yhIuLCZ6kepeSUBTCl3XaNPEsPSwxxLuphJLqfWMJZAi3aXWbF08'
        b'5CkYHsQhmxisc9W6BPPQl4qNNjB7JAlr6exu44j/Rlj0FRzA3HVyuCimVeZ7rIcZaWYd6bSBnigtZ6g5oa9nQ3pXMW0Jh2yJlM8TXAwTLkwTMCxcJv1zUIMOvT40jOFP'
        b'ZLQRUdYy0bkjUZeVYPIs9sR6ecZEXiBBdUyZltBALHdAAcfcoCQMav1NtYHUjFtYFqsUgoO+cFvDIfh8Bra4emzYjZW7cHRD9DkstxYxwZUoUR7p0a047552nXZfEqpK'
        b'7KsdH26U2g41Gt6YHxbgdOGohyPheak93k0+EI4zW4gq3acrLSHlUCaISMSgYqABR2YY6b5DB1kXtgdGcXKLMSFvHXamE86Vw4gR6UAlarLEIfsTA9bTpCXhuHDyMt1N'
        b'GZKAUCEPU+q2FkTXWtI1bqrsJASrJ6Lz0AwLg6Bl/yWYugKDqcdJqAnEGs1VoE3K7ZRYpI33sNJBJQm6NGVidxLZbaa9jBJRrNktdPV1YdpTGD4Iw/F1hFqTrAiDma0y'
        b'Vhic2SBF8N1A/LuUBPjBa3TYd/f4yvvB/X3YEECg3UC0e1aRaeQwYOBHp01qNZRrYZ6PIxN9NGiwoaBN0G2FQydMkOQZ1w10QCVboNViE2HoXTtoXM8qHCQT3+mNgNEA'
        b'AwLyBpH3Hn3o1LWBrFAosiTZ155I4iY/Y32iFFXRmCMPoxFJN4l15cBE4D5iK+MRjI6XyKactIY+pf10wrexXieIzmhGHTui1uN9OaNrR+wua0Pzfhh2v04w1U28rwvr'
        b'dXEqxRX71EnSuU1sdC6a2ME1hWNJdIUtNEjVlgMp0GUrtRuHDm+De4cUsCkFB1Ujz+tAj5rqZahej6VuUTRQNtwxk7XyoOskQYOO5YGUoUeiw37vWLy/hchCH2FQU/AW'
        b'XHQk6lULzS5H7AWEFsWEkyR+E+2qginFSCzYS/yZZWsegxE9eSHRgemgc0T3uulKHtCoeWrrTxMbL4NOOciNhnwb7DMnBlB44wpUHTiHzEzeIYDxC7b6RE1mIT9mJ2FZ'
        b'rw60mxOK1xNCjJBW3RQsr7sX57Sh1veAW6ITq+IC93BIil65BeOGmjakcXRCzxHolzYgRGqCxe3rdUmULTPBiutYwY6m6CqMiRN32NKnlXbQsfM0zhCvxBq1bXbbsOUA'
        b'1EUEENwUYk0SMaaFtLM4vMfOD3LiUogo3rEQ7IOekDTN0FA69bhonIOyUBi5TMJzJYlvZXRaoweJpuZts0HWfWuOtZhJOugWaU90oBCLM8zpgMeUhAR9/UpMOKbLrA9P'
        b'TsuEB170z05ocCcVvRWGE53x/mmONU7gnN3ZQ1BrRGyTtF8ne5xwJRFuWDF8N8lydYGEHYuyoSSwZW3xg9ZUISGSG7HibIZJ2QTQDJUWcM6UKHEdweeUDU7okLQbgNUK'
        b'McdgYBs2HrOESjGxuLZ17Al71RhSGOczopydia3kuPrZGGL+tQSSsBew9whBwBi0yuP8Ptk44jkDQmz3wdntmZBF/P3uDkcVRR+sCeccbEPM1n8zA+7ALDNpdcKMN22R'
        b'EKWHmYtI1O2GHmctrE/33nnGkjZ3F/vtMPsmluOkAbHHwnPQ6kcC16S5THSClQ6MOCsQ5g/Sg2VWrLR3HGHBggq2nYc8EglGiLOU78YKfVnaY7e8Od6/Hk1CYH5oGuTa'
        b'E18uhzYxjunIY6O/jqMOgcygkbTqBnxw2A8qlB3kiGjOYpYTiTQDjKTtxfsC4uB38fYu5YiTkHfWzehASqwCLqievraT6DvJ5YcunYTbiVht5UM6NZNEx22irxOEFO2E'
        b'EbWDboTF7dowqwBTAelxJnhvO9GtaWyEvAs4m6aA+Sd8CDPySAa9R1SnknSWzXTYtRuxWUlBHKmNJWdiY84HWWODm7LwhBa9N3T+HFTKQJWaNuFcNUzHKrmYWuLURmb9'
        b'JL6dBfN6MM18eL0GG0jvKw09bE8SfMseOo12uL/BPB4q3bcSZpST8pOcCvV76BbyXXDSTpFk+DkSC5pOXNPGDqUb0rSHKkdo0JC/TkhXRf+qhEXT+OB0aNlMWmWO+gEv'
        b'mNSBJtX99kpX8ZYr5hkEyWKvL1RFc4UuqrHcO5BZTLE3ldm86ObniPyOEJPIwS4LLLwRtJm4NIlB/vRssydt5tZpnLpmQbIZdBPKVBOjLlQMDE09Q0jZCoyZkFTatY/2'
        b'tpgJdzZiVQQJ3pOXCV6GruoQWA1kYsFNKCJSToLHrQCo9dqZ+jaT6x8mb1lGAgdmmLp92otGKWVULPawobfKNqwgHDi9LYOeaNKNCpPXwS7dA9voghfxfhQMyjoH0yxT'
        b'JCF1i/bhlD4hc+/+WEXaUh62pQDzA2efsYMqKajRIXI+fxXr3aBDTL/2wGwE8Zt7N4g63iZ0YtV7KhU2YqcrUdMBOvtSrLqOizBnp4lF+2DOHDu2eWBJHHN2uTBLVfhJ'
        b'Op28HURXipSksD9CjyB/It2Q0Hxmt1cCgVyXhhWtrWqXFtZs3WSMjTtOkMBA2HGMoGFBMxonlbDBdjN2ryPVMe8c5BzDGQcYkE8j8lJN0s9dIs+dLIB9VgaaDZyhVpHU'
        b'hO5dKtB+ZDfUW5OskKfjux7vbd0jI4OFp45hkSLeOnaS1OI5CxKwCmxwVCURJy2V3Kygwxqrjxx0oEMZhwYpwvsuovf514INVVle1wyRghnINiRoHxKSWHbzym4Ct2pv'
        b'yFPkoGImiEj44sUdRBCasCCBTq2HEYLJXSx8PzIaOg8QPDMbfDUWa+P4PtJtKqOgUAY6og3hnhQMHzrIovBJUc86RfRrwv0qcfSH1jIkWndCqRHmmNHBDGtBRybUqhFY'
        b'Fm5hHmXp6zL7onxp5Dt2ylhDwoPMVSYB5WjsjSeVj0T6W0QjKqFHA+uPa6ex6AofOrkGmL1wZTv0m8O8I3QaS0P9ZpKuGgOg7yKpPUPQaR5E8g8x7n0HE/bArOvOy9ix'
        b'Hepcocd01wkclyauUuuymRTbZhzbTTyuj6FIvY/6cWuSrwcscNFvG5G2Wu9g5aBMX71AApxCzNrrzpJLttpvcshklZgKL2Lf/jPGIr5eTtZ56EwmEG2HLknJHKEJ8V++'
        b'rGxFADazEm+svtsRpl0zc4KxmLNF+WGDuRszLB2AO4ms6Oydbbz1Kp+OrcaN1YgX7jLBaQGW+mzivoF5gQ/LoZISCI/B2BF65yB0c6awKwmQzdvI3GGI2b/uw1LnBQUS'
        b'FHvdWGVbq8Ox9BXknuUGk3EnMCxxp3dssN5OQNIKAT0/zT1PaJEY1i5iMbOszaXTaFw5nYLDGVhiTG95WaaydhsFOMm9ZIKd9IUHM61h2zYBMr2mlfvGhujfKG+MIwmB'
        b'Wd2wz95YyOfx5QTIuLnSaKZOWCvAQhi14SpxbSVponXZIDdtxexx7TBkLHTkOv9w6WwF60R88bcdyucWNzsIjMXcxzcvST6WEe/VCdvPlwv6XbTkw8hw30rlMwJPY5En'
        b'DcUlv8VYfPa/ouQBRq9+/mlm9Wkv/SOaeVFXzwvF8To/eVFn1xt/eSejQLOqosPOcIONa8WW7X/0kbIMdLu63+sL4T/eaNow7P6DY+HpC583/f3VJuN/2f8j+c3AlKQp'
        b'4a9e//LUX94JiVx/0e1nUZN6Qq/kH6pOpAad+OnfjxrnJTpuHvtdzCdzkw+9Tisdv/Sr2stDDx3X/Tqz6c/FRTt+8en/6H384Y8/MXFq3975VmTUb0tSNd61TtN43/q6'
        b'RuX8uRqP7/z4TNmDt9O2vupr8YrWm2rDjm9L3Q+0fMXkrlSV75kT6Qofa74W/ubHN2StBn81+Ks3/3C8JlX/HW+XV+TvWqQk53rOd3pXecYK/9JWe+a340nWviVVlYG/'
        b'PfKX9taUPzkXuSw4XBPk/FROptnnF0keUadtj1zb6l3hH7PzbFXuD142+LPZ92oMvhdjU775A+dfx/1k3zn8eerrLwe+tjXH6oPx7fUfNu2NDXz911kfXLbJDvnA5UP7'
        b'qsG/usyYH0pIjHQ7E15u47TrlfunFk37/3lvv57G7XaH4baP4l87d/v44d/9Zt/lD7Xsr+p/3l9j+90PbhunXPvfD3+eEmKgYRAB+94uvDDZ/ufPXV/+UdDgcPCFn9g2'
        b'LJj1njxeFP69oje0NHL1fvPpV79JUq+u22L76/GQm4vm8ru+Omn/1QP3fV3v1GS+2ru7TPdP1td+J/zfz3/44z+8ZVqwu8SmJV7rDxFZP7xX+j1R8/qDfw54N7Pwjzs+'
        b'3P5S40zh9tc33Jj8f81de1AURxqfnZl9wLKwggYURNAzistDgu9HgicaeSxEje/TcVkGdnTZXXZnQZEo+Oax4iMao0ajKFqCoqIIkeDZnSsvlauzrip1krkrK7krvSSX'
        b'smL0PDRXev31gJrk/snVVXG1tT9mp3t6e3p6p79v+H6/r26Qd3nPr8t/OaHjetPihiMPbxY+aT2d+dXnFQdvrdhnX3xdd9/55bQZV6/Ud+i+LjtVGirNqx91/uijZvnj'
        b'+Nc/zo9YFiN+En17hS16avdvYh+WVOJt5h2euohDfwn52wdda8a6j7V3Lxr2z7umX303sdS98FiZ7unfb1w4/bC06GzTa3cuxx2e2JNyuEfqdH7bcrhnbeeqb4XX7kX2'
        b'jH//7JsXH0fe+C73mGl+QjDlr5GVrMNMdanIXeQ0PsTgHdNnqhyuTStjjD8my7lW8gay3G9RiVEdkS/mvfkFbv0Bxw0dNdIw+LEyatfiDqPXFGQiy3ttmNcfQm53lzkm'
        b'ppw3cFlqrPyBceuf1ShDuyfjtrISk46JSufQWeLWyJBS0QT/mfKVhpT48eUwVIPqwgymYHwurFTLJIQ6cCePm8fgS7KFVLU4F/604ir8YVgpCpT1tm3ldagjZIVKBnA4'
        b'jc8aM6AjHD7JpqBjRTQp0PCZeJcPBQwlpHc+srpVq81NLvhBa/iSjiwFW9ERKvMyb+DgF/XmevVXIl9+psBiQO/+NEdcWv+Gl/Y7JMTQO+r/C6iJvQXB6bYVCAINvP6U'
        b'AGth2XGaOBAKeapjQzQGlucMGh2nY3VsKBeuDQ83B5ljzfpw3cBgPmIgG5XJDh+nYTawaaxmEk0SxHMQhBsL+yxRmoyRsI8VpvUmEGLtU+gWu6hvT5RuyBLzDNI2x5oT'
        b'4agRGX11R7Bj2ATytrAJTBXfRPfp2ES6h7zIvhMQW6171BcEbjAbNFGaF9/8U/6Rd+WzGGfO+xWc/POY71f6f2L024TUqINBY65hiODm4gNDxnPzP+S9ovz9BhDiJa5F'
        b'PTGJqvPi8OYcVI3q9UzoYG5otF4akJ7F+wZpGKZ5e+74QGYuTjfPapp+o8Q5qiTcYIhPDTI3RO24xp6/jBqnWrIHDPhm5/qvX/qiUR7SsLRTKP/Hleg/7Dye8vh4wHFm'
        b'2LV7U251B060jjz12dJt82e+8/3W2MgDbQ/23ugK7p4f/86dP+7aVfPZgqCpyyfe/u3Yv3507jqHD1msix4uuHY868n3n+zZO8TjuNByfyc3o6l80JfTd45Y0Gp+kFX7'
        b'6dHSf91Ldky9M734liN+37Lo6D+V7nsS6DLezrBOnvjenLunlv/+gyd16+JCUjemm4z27v0rg/XJhd341Wk9k9IrZ26ehFJzj841fzGwaPuuz2Mi2z8aNO/PcTjprqc+'
        b'1vvgXiU7Mvbe5qI3o37XcrA9s4tru/nQuOW+ML58WUfk3oRhlGaRjroSidlYB9ZqXh7l3OoZI7rA4lPrUSWtspj4C9uz85LweaiSl0TcoQ9ZZgDu5NBRzwLKwUZv0wg6'
        b'einIUjYTX7XCAx5yKcK5WOJxn6JckCX4JG4DbdRofNKqZ3Q8a0AB3KQqyh0mjmAjrkX7uRRims5ncAOuSaOE37QV+IQF7xgNlOE6DRMUjxuSWXTgjQr1wOr4DHVh1DJ8'
        b'riaxDJ0rQK1UuGxdRB5E1yehi8N7K4TiGi53Oa6iRy5ErbiyT0lNswR1EkO2XVYJzV3oUoTaqjUTBxIyRxTyTDjewxEvcE+mqt+2F3dUZGcl5o5P0zB61DAF72Z1ZAk8'
        b'r+ZwOJ82LPuVNHIsFexCV6O0TFg8NzUUXVHLAy4vlGdaoTgO7YC+neVSUeVoVXPtzBTiyNVCLrx6juHnQrKGGnRFgwK063PnQNQcDlgTGYZP1eCrc1FzdjQd5Omoapkl'
        b'CQeAJV+sIV9HHEziY6gKhFfgmbUFdOpyyPfGl2RayenzTPRbPNo4DDfTrq2bhBvRyYxs6Bo5fxhyYwJLvOuW9bR86Tj8fjHa5HuhPDiTReeMuJouyKhyKGo14gth44nx'
        b'ccmHqvFlD75YQuwRE8PEjOD1OWib2purxK/ZQybfdspFskCDDJl7B1h8jJhInfR0BuPTq17QntPoU9BB9N4EeRQpKx4zMhudGZ2ZRKXE4LHGtDw62oGU3KQEHfP6LH0F'
        b'OrSUtjMSt6Ua8TliVJzNJjYY3sXgxlW4hV7KhWRALkL0tDUHVYl5WkZbocHH1+IumdI13oWweyhOAo1uVLuypNf8GuLniRlyCe2mdhzxNztRCxn6GpA2zGGZIOLltr3M'
        b'olrcbla5UFXx81AzbrdkJSVak5I1TMggLnjxUHXG7ccBMZtcmuxkcjj5GSUUJ+mYiDQOHy4g46XOmQnxG9DbljmJY4D1CdcF7wRd2qpkKp1gKsK7Ldp14KRlg8j3ftTY'
        b'l7BodP/f4P9Hy8RL/WCZPE8RXErAEBrcy8EE5TRz75aqcRZCddF6t57ylaCfxj6FhMAGjYv7+Tyyvhc/VmVUUbNhjMI5RZfXR1Y2RSv7PU5R4Z2ST1b4AslO0O0RXQrn'
        b'k72KNn+tLPoUPt/tdiqc5JIVbSExscgfr81VJCpayeXxywpnd3gVzu0tUHSFklMWyYdim0fhyiWPorX57JKkcA5xDalCmg+WfJLLJ9tcdlHRefz5TsmuhMxS6YxW22py'
        b'cIjHK8qyVLhWWFPsVAw5bvvq2RLpZFB+2gTRBSJUiknyuQVZKhZJQ8UehZ/9RsZsxeSxeX2iQIqA4q0MKHYXTJ6oZu0QCqQiSVb0Nrtd9Mg+xURPTJDdxGJ0FSncYmuO'
        b'YvQ5pEJZEL1et1cx+V12h01yiQWCuMauBAmCTyRDJQhKqMstuPML/T47zbmkBPV9IKfjd4EK1XODTB3v0d4yMNkqANYCVAFsBthAyW0A5QAOgCKASoBiSpIFcAOsAgBW'
        b'odcJIAH4AdYB2ACAxer1AKwH2AKwFUAGAB6x1wXwFsAagFKA1QAbqaAdQD79IuDYbYKtbQAlz7iDMJGC+oyrpY9+alzRGo8NhWS+iHZHsmIWhN7tXvv88ZDez3Eem301'
        b'CJEBqRXKxILcBANlACp6QbA5nYKgTlzKEQyCGatTU6Z6v4E91X228I9SLiuGaeTq+53iq6Dj7JvDAKeX1xnY//4nNHABS8nT/wbzvL/3'
    ))))
