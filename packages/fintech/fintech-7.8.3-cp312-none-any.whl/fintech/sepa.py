
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
        b'eJzEfQlAk0fa/7y5uO9AuAmXEEi4PThUEFRu5PDCAwIJEkXAhKhYtF6VIB5BtIBHCWoVPCpqPWovO9N2ey+IrcjaXdvP3W27+7Va7bZ1u7v/mXkTDIKtdne/f8Rk3ued'
        b'd85nnvk9zzwz7/8Asw/X+Ht3Kf5qAwpQDJaAYkbBbAbFHCV3qRUY9VFwjjNsSG2l4HKAkn/ceGcl0Fgt4GCKQMEzxdnI4GsL5fAzDKjnW1VIBPeXWhdOn5UiXl6j0FYp'
        b'xTUV4rpKpXhWfV1lTbV4hqq6TlleKa6Vly+TL1FGWFsXVao0prgKZYWqWqkRV2iry+tUNdUasbxaIS6vkms0mFpXI15Vo14mXqWqqxSTLCKsy0PMih+K/9uQGv+AvxpB'
        b'I9PIaeQ28hr5jYJGi0bLRqtG60abRttGu0b7RodGx0anRudGl0Zho2ujW6Oo0b3Ro9Gz0avRu9Gn0bfRr1Hc6N8Y0BjYGNQY3DiuMaQN6EQ6b52Hzl8XpPPTOes8dZY6'
        b'C51YZ6fj6Rx01joXna3OSueq89IBHVfnqPPVBevG6YQ6vs5e56Nz17npbHQBOoGOo2N0gboQnVNFKO4Ly7WhHNAUZGrntRIrwAENoaZrHJaYwgxYF7pOUggCx6CuAqu5'
        b'88EqxqpSwsktN+/TGPzfhTQKj7JBPZDY51ZZEv4I54RqOCRUmr3cygVog3EQtmetRc2oKS87PxFeQjq0PU+CtmfMniUTgJDpPPQ6XA/PSLhaLxK3ezF8PitDmiFDTWhb'
        b'Dh/Yo61cETTkrl6odSP3t9igV8l9vhxdAjweAzvRq7laMb6lRbvQGbjLJZw+mZOBtksyeMAZtXJxpi3oiISj9cHR3NAl2AR74cWsmFgcJwvtyMvgAwd/bqI7fI7GgE1x'
        b'aCPcB18kMTJy2Aj26AVuNOywMKbigxphu4bcFMGLODu0jQHWGRzYizPfpQ3AMYKq0Cvr6mzQGQd0TgOb0IVa9OIK2OxgB4B3IM9iBnpWwmg9cMSZaCfcgZqzM9E2Lmwr'
        b'AFz0GgP3TYUv4vuE+wLqc7PgyVDcIluz0DbYFANfyyNlgtsjc2USAZg53aIBGnD9GK0IRx8nhgfQWVykRag3O48P+A0MOjwnGt91x3f9LeGl8EyZFL5WmCOLYICtK9ca'
        b'F3onvu2JbxdWwvXh6dKw6OWoKZvUyQbpOeiFaNRZzpj1f6yp/yH+2hPTiHkAsycPs6UAs68lZlmAmdcGM68dZlQHzLhOmLldMOO6YpYVYcb1wKzuhVnfB7O0H2Z4f8zG'
        b'gXgQEPYO0YXqJLowXbhOqpPpInSRuihdtC5GF6uLq4il7I2FRJPNMHtzKHszZuzNMWNkZh3HyN4PUYfZe8nD7O09ir3zWPb+banAdjcHt6O41PaPKVxAiXcaOBPULM9L'
        b'j3KMxG5ry0nvcjBblpbafsLUs8S1XrzsfK4jAMml0g/jJ4MeUGVNCjzTnXfPGSTfdqlnZvufj/aOn8hUEUnqtrKD6bUA4ijJlYAb6uWrHAAlP+N612G3AxN6O2qy+z/n'
        b'uSZ0gCGgjSSM+wLaC5/HQ605Mj80FG21jY5Mx1wDe4pCM3PQTmlEhiwzhwHVDlaT0Wb0inYafkYkR6c1deqVK7QadAH1ohfRGXQenUbn0FkHS1treys7G7gT6uC2mKi4'
        b'mAnR42PhBdjLA/C1BVYNK9DJLPiqNpNkvdUKvpCFeXjnxNyMnCy0Ew/zbWgr2oHHw3ZcnlBpWIREFg5PwW54ogCncQa14UG5B+nRs6gV7Z6LSxJl5zwHnR7BaKQDCFPf'
        b'VRBG4xD5i1mNwezFr+BSVsDzRxNvmBW4ViM6Goe5Zp3OWcc1ssJD1GFW2PwwK/BGsQIvV036UtU/R8Ro0nHoWk70vveSDvg/E93cwnDrYl7YsvWTz2flI/1b2ySXPGek'
        b'ahWnP59T+H7fu/tnnn5rx1vVRzy3fJw96x/e7d/+8IFtxc0qBkT8zm5V4AwJ/x4ZoYHiBtyDW3ELbuMCXjyDh/ZL8HSUPb25MiAhPAI3bZOUAQK0AXf3Do5sETp6jzQS'
        b'fLYcHQ2XhabLOPhmG3wO7uXIYovpgxNy4dZwGdqeHc0HAlvYVcygk2gj6rnnim/mwP1TUXM6PIlFXwTgrGVmlKMDEt4QJ1SixtwKHnxpSDOI169ff981qUJds0ZZLa5g'
        b'J98IjbJWPmWIq1Up1pAvDok9C3/9sB7cnsEBQre2iS0T2+NaJ+vSBl1c2YvOhI6EfUkDLqHXXCL6XSIGXKLITVFbQktCu6pbOOAScc0lpt8l5prLpH6XSQMuCX22CXdJ'
        b't6gt8JdEMGRVLV+u1OB5XznEk6uXaIYsSkrU2uqSkiGbkpLyKqW8WluLKQ/KLyDDtFSMq6B2IkRn/EXLm0buxuGv++vB36ZzGMbnM3tR87L1Nrc5fEZ43ca5Of4znsPm'
        b'nEFLh+uWLj/cwYLV0XR1/y7hiFZBIDhkE8Et54zFPxWEgblGBuZRFhZU8IZZmP/fY2HrUSzslKslhBB0PEWTzU+DjQCgHgCPFrlrCTukoZPSrGw+6oUvAEYCUCMeoMfo'
        b'HbQJz1Ud6GwePxg+Axg+gOdmKNk7rfb1qDmPDw2wDTDTAR7Zp9bSXNAFeNzBJoePXs8FjBOAL4d6U7oHnhrDc/gzBYDJB2gfWo8OaYWYHgm3rgqPIPzbCZgFAB1Fz6+g'
        b'NybA9iWoNR/ANrgHdxrIqUCXtKT/0pEBtdbmo1bcuVIglaIXJVb0CRmWZTus0LOJuEfQM/gPdnvTGzPgdvgSerHiKXLjefwHDwaw8KKpIAUPuAPwZZwWagNUSB2lz/jC'
        b'fehc/jxE71zAf2nGRrGDe2AXAw/DlzE6RgfwH2xcSVNDu+AmeAGdTkT01qv4D+od2IwuwU3L4U50Cr7sgG8Z8B96cbKW8GQgPIa6A93RIQ5BnjZlxVrCuXYx6EVtVCFO'
        b'JwSEVMM22obwZJovbo5u1IrHQxSIgp2BbMZbp0bhTmuzQCcLcaydoAR34gsUbcDtE4LQWQ06u5IBHAy9NqNuJghX7RQr1bze3cPXvEqSaPxorT7aHkbZTvcJyVlQPC/8'
        b'68vRaza9UHcs+PC2orCsM6fdp0+z1T3jdW9XmmVRGndx0k9//qam5GO7ed+/c4lx3hyUkT9tb8F7oUffmrwqZSKnYvxr9zM0Z/7wpkfYjDtHuqdrFJMvv2Z9eJteWXqn'
        b'2fW1M6W7/vDyssrw9cvbNVB+47p1c+vZkvCbVw+38LI+8bOaM64z9sSySe/br+qTe9WFnFSMT45sqPgjf23Xxs9v1X33rz+M3+D22yburd9YbD8QiUIGjKIUHcsWh0dI'
        b'0FYp2o8bUwBPcGLx/HP8HmkILjoxXrgSYyGky8jO5QMbeJqDDoShznukBfMm46mrWYoBogy9zhUAwWJOYGLuPTFpwZ55qINOsmgrxn2oyScHnsjkA5c4LtrliJ5lZfH6'
        b'JEczMe4mxIL89BSZxPIhgfrILw3pDrGYSCqjrBqyUVaX1yiUJUTSrjG/oLJ2gJW1d2ZhWes6KHLXWw76+HcLe4suCx8EvP3u8Dkif93M2wLg5Nxm0WLRaqVLue7gMSh0'
        b'bZvZMrM9tTVbzwy6ebbLW1SD7h6dVh1WhqBu7oC7VJ9ymwtEXu3yXSr8sG9w56KORc+VtFjpefpy8nRGS0a7wpA6IAxtYXBMX9lNR69rjsH9jsGGim75gGOULmXQkWbZ'
        b'lTLgHt+V0r6i26l76TG/vU6GlH73+AHHBBzDRUhmhtb4PlvvH7/lAo8EjS1pTS+rVGAJg3n4mxX9FkOMZsi6uqZEg/W4SqVGTTpNLRqjHS2GJb5R5JM+HNF8GWai//s8'
        b'LPq9nlT07xYEgcM2kY8j+gl64Y8Q/f+n6MWKBbJh3s4gCP9GTVnPXznRjoWnt93SgR7TosZffLosYhWYQalVyxwBbrJJUXMOitM8StioXSobgIWiZdSEqxlfr1oCTDLt'
        b'FHw+NgpnBlsB0sP2stWwWfXbzbY8DbEXlK+8vu+9mAMbmrpaX2pdMT6Q6344qiI2OkqoOdQUo3w5KkoYPYfz1hlD2Tul43d/XfZXRZgzZ2nLMfnbRQPv8mJPulflWmdZ'
        b'bxJy9RXp8j1l3Zyt1zbegAUIXNgjW7Bpg3/7hlg7MPOo61neRAmHDkJ0rgLqKSCCBieMiQgegrqke0TRTJTFhEdkSMMkERgYoyYA3MU81Dl7MXyRkfAfPSr5gMU/xiHp'
        b'VF6pLF9WUq5WKlR1NeoSDH5Gk+jwLDUOzzoOcHTRxzavbvff2tChMcTuW90dsHftoMh70Nm1TdIiaQ3XpV53cGvXdK7rWNe95KrfBHIPP5Oin6a3aA9sL2tf0R7S7+iP'
        b'x61LkCF/wCWkO67fJbLPNlJN+to0PrjlKsWQRXmNtrpOXf8Ew4OonGNUYoH5INHgQeL5BINEHUi6/2FgTzmzzDg4qAb5ANYzIwbGv6vhVTw8MPijBkYaOzBsI13IwJi1'
        b'zqo06Y0StXEMLAl1ImOgVvdUqa3ngmJQRKdktGMcPBILnHCzRoPouMU0auJCHsC/oRezS6uezfEBFKFAPdyNTsTy6tFBYjyJmZ1H437izCUNYenKlFZ9P3EuoHN6mDMy'
        b'xOKZmUSNBbHwENxNI2tt7QCe1NLFc0qzY6Ib2ITRQbhdGivA2jwAcSAObmWxFboEn62JZdBL6BAA48F4dEBE0/jUXkgNWmBa6UJfx3mAViMNnufH8msTMMICE+TwFI1Z'
        b'I/IBk7AseGtW6ULH2fMBhUBYKTyFNsdy0e48ACaCibAXnaWxrRPEIBlX+uqq0oVLpPaA4hjUK66MtfBfjWUHmIS2wG4atWxFMMBa06ytGaUcT0UKW2cNPDcOngUMfAmA'
        b'eBCP9sFdNPKsWaEA6xDzPlWUclyjw9jIsIOZD8/y0PZUABJAAsTgjUb+V4UUzMMNdGpOKae1FhcZAyuQO3+1hheLFd1pYBrq8KKN5gW3wZMaDnwWYnZJBamO82ntLPGs'
        b'3qsR4EbbjBuFoGD4Oq0I3DRlpYaZiF4BYDqYzqAOFvEehQdht4aPjqBOjCjBDFzF07RBtXmoS8PFzANmgpnlaD8lJtfHaCy8sChIB+lYoT5Ds/SDragTnQVw10IAMkAG'
        b'BpGdNMsguDcRneXNxC2VCbBSbcuyUVfBMnSW4wbbAcgCWULYRCMvLQhEZwVa2A1ANsheCnfS5njGUgDw3Fn6J2lp9ka7RLYHYVvcJHSWwdyow2ofyEF7jNxVUGVNBHrt'
        b'bLfSqpKsUralA8thCzrLh6/gGTIX5KKz8AKNPHFOCM4JpBeGl3I+ldmykdELWPpvRGe5vmgvxk8gb5kTjfx2ThgowpwU5lta1gscWL4dB09NRmct6tB23MlgFtxiQeNm'
        b'T3DHMBaIe8pKF951yGDj2qC9aIsNQC9jbA3yQb5GSuNaOlkC3LChP9aUSt0Ftkae24MHjA2vQYlrBAocYA+N2jnOgdh0ao9HlVYFrE00lrcJ7kLbbfBIkwNQCApVsIVt'
        b'ZMwWShsBfHYmwOUugtsDaBoOtZ54hAH3V/xKveWeGnboKKrSbRj4XAwAs8FstKWUxpzk5QuScIXHxZd67/DwNw7UTRrUZIPVpm0AzAFzULOMHTgBAYBonn+0Ly2zrl1s'
        b'lBavwY46Gy4XaxlgLpi7DJ5npQXjhtUbUDk/oLRhdXk8W+FIPM1us7FYhuX7PDCvHrGjd31KBMAcFfrc1NJph1N8jePmQpQdbAbwGMTpzgfz3WAXjbw7YDyoxL/e00oL'
        b'fDnj2An+OccYoMCZvWVXqm7wHc8Sd1lEATyPWR5eUcqZWrkaSDhsS55G+1EnbOZNxU8Ug2J0roTNsMcJbYbNHPgqxtsLwAK4f23VD//6179KKvhERLpn5pVWcVwt2bRL'
        b'siaAKpzhPXGpOjHAA6h2SzJ5mmQ8Z3R0bdD2v5vLSXEU3Dz2ZceG/BUlYJXFxDfXvuGT3WDl/Oo/op1q0jemrvEt3Tax7JXVf3wzqzjONjr6b5/95fDL//y67ruj9wOa'
        b'D6bdWtn+AXhd2LTUe16Lzcb3Cs69fvepuvt3wy1W3prz8b9cv/k69o0NvysL0gsn2zahWZ9bFnwe+vabK7J1re3OR6MDPyrLzd5X9bbi7LjEmjM2zdJxL1eeyfr0xI2z'
        b'VVfCx7269Mqy2295f/KWXdXWBYNudwedbAZdv++N9F3/Vqp3028mOeWtGOe2ImLxzYJXoLb5d9u8bhy8t/xcfFBQ6t+6v37zmwmLwpdIvv7z5Ml/avKVHuyz3nP+5sRF'
        b'X9YUa24VuTz99yMf3wz5+tKeD3cH/YiunVBGpm7aszFn71Pju3zihz66Vx256s8/OEy2rur86t0f7nl/LCx8hnM8pebYNLu/PbcOzG6Ql7wbj5UhP9JLWx1RE1Zp0BG4'
        b'P5dYd3dKGaz0HOfggfss3EW1nnHEVgePiExGJAKYPObf88W3RHgO681C28PR9hxZpjSDD5zh3gnoIhc1JqKNVKNCPbloPWyXYb1nW1YGPIk1rkkcD9SWT/N3zEedGngy'
        b'PVcWSgz0aCcXOMHNfkjPhb3l8NVfoRkNY5YheyNc0ZaXEFS/5qFrCsDmclgAls41AbDorQR23XRx06vbGf3EtqktU6+6BA2KvMyQGEY3HvYEfeXf5pKQu1e7MSQONBhD'
        b'oeHdxlBUbK8xNCnxYgEbSkm7XMaGMnPeUbOhwjl984rZ4MKSPnk5Dd6kufBJiOZCQzQXGqK50BDNhYZoLjREcrlDQzQXGmJzoUE2FxIkip8Q52PBhj2824fD/kGGAlM4'
        b'TNZdZgrHTuhVm8JJUy8zpnAaM5N5Z/gqm8lj+mYNJ1bEzGVI9sbLRUwpQ4pALy1JEQpuW7FhT5/2MlM4cJxBbQpLI3s5d4zhhKTLAd+SsC7jti1wddNNv82xtfO54Rfa'
        b'7dJd2F3W7f6JX0zLTIyR67Dq2x69S3vT3cfgdc0/pt8/pjduwH/SRRya3O8+uYNPau1r8OiO6/Lrd4/C13ZAHHvbHvgEGKZ1ZOqtBl182+v7XSTdhb3OPXOvuMQNeomx'
        b'Qiscj8shdP/hHh8Ifb4FjJ3PdZH3bS7+va+h0i4oxSY1BqAYq9QpXDSZwd8mKyUXM+KjETg1SZoBcLK49jAHE/M3Rd8/Euskl2GcnlRF3SUIAAdtZNxfROFkFQeYoXDu'
        b'f2+dZbR6asGi8I9L7ConcDESmFVqu8BqpRGFDwZa131H8Ktjqe2Hi1yMk+U2BdLFRgWtZbXOshCVKvPYTUaDATE4rLQglvmu1nhimT+x5Uo1XPRBtu2BbQc+ON61tMD9'
        b'bIe7+1b38I6EjsL2QvfD6+8Xuhe0P+9+bP2Zc7bJH2ePt639WHrd09b2Ddv9HuDNzfZRWFAzrGVpKzyGOh6IyQmwkyMrhc9KeGNKLJPVnJVWnmzfaurU2vI6LVaxStTK'
        b'CqVaWV2uXPMz96gUmw5Yi/o0HuZFYidvTdKlXXdw1sc11xsF2qAjHt/6Ar1le5yBY3Bqn9TvGPizuqJgiKfBuTw+h04iHPozJd1ozq0pPIZxfhJdkTz4GFw6Ulf8z3Hp'
        b'qMVu7iguFbD28xmwazrcPMtGTYy7J7BewvGkfHo8iQKq5L6UUnXXxEIwQ+X4UiFPk4JvVXS6sRwZbeTIRduS6yuyfxS+/fGsRdNvvB+CuTP7QO0668LzNrN2n97lEfrR'
        b'ekeHipvZXLBigW3Y05+aLBt7uajVyH4T0Ak6UVehl+6RlUv0InxlHTyUMMq8sXhliIT7cN+S2g1zpvtDav8DvnzkHcqV441cOcucK8lCDp5SDXFXXUJ7Unt5xzMuco7l'
        b'Yga97iLrVgy4xPbZxo7kwvIn4sIphAsfWa4mcx7M+1U8+DjGPL6O+f9nzBOw0nL1CqLeWDZYYvVmYVYBi6cT+QRkz6uwSy6V7p48jyV+70sMDsliPiiVLlSHAdXa5ASu'
        b'ZjG+88xnE6ltrpVY595a2YMZlHE5UbG57xwWl+NtldumWydrP5h3NeVL4dtV4wRbAn6f+yfhkbAIwZaICnGzh/TtD6ziAt11G86fPhz1RvYLnM8j3vYN+cgNaL9xjjS8'
        b'hbmWSs1XMDQ8Bo9n50g56AB8AfCyGHjGWX6PeFQ4wJMYFWJ8uiMyLwdtz82AJ3hAVJ1cwJvgMP0JTHJ21crVdSUKrbJEIa9Trhl5Sbm12MitC3nARXTdS9pddGp+z/wB'
        b'r4l6S8yz7av7sZRMO5XXkzcgnXyZuSJNGRRLulO67PQZgyKxIXrX2kF3n5suIl0WRgXu3h2qbmZfVb8oTM/DSMJFNMIIxyOZDllVKeUKnH/9k5ipiVr4UOl3AjMb3ALe'
        b'k61RsjY4kwMX+QhMDFVFeJrHOjdhruboBNRMbaGzrBBQzuaOWKHkWY3gWxzmmfEwdx3PyNkPUR8tYa1GcTaf5ey/pFEtFER5lFlOUQSzTDy+gFrYxFErU4Su8z2B6mjj'
        b'nzgaMud4Ov9l33sTsHSVGaXrOdvxtvM/WH3LI3F+873MefLPD5yQbDveIf6ru3jR+0Xv33g3HxXxb61aAT4sQ3HHt8QnbtnQpXt5S0tTl8eG1vBnVOOvTp5dejdrkvyr'
        b'9Wf2j992wDvq7hsNr7zA7bj27o4q3212sYeefX5LcPuGs3ywKdZ76Y9LsK5FV3964Bn4LF0jsgCcpVgiH2Rm28bTe+vg2RXUgYl4L6HzWB3vRDvgRWqURp11aEMWapJO'
        b'DsUPb89jgCXaxoGbM+AmOoAmwWdgF76ji8Ryn5fDzIUvwtdXQD2b6RZ4AG1GzTnwBO6UQngUbmZmzpgpsXlcxephliRubyY9a3h42S5Rmo2uEVd0cG0yDq5aPLi82qQt'
        b'0tYIXeqgi1vbpJZJrQm6tM8cXG+IfNorDGUDIkkLT8/oowe9g7uZjhyCvGm09hW7Jg96+XXhQXdI2u8VoU+7JfL8zNGnXWHIGHCMIKHyzsqOyn1Le+J7i45P7fdNGHBM'
        b'vGvFd7fXpWP1QOityzMbhVZkFOKhN4MUX1CuraupePQsw9bcig7GUrPFN3UuGY4jqttBYsbjr7/j0ViDR2PwHYC/nhSYtwlCwFGbmJHAfNg+Tacb/jAwJ+5VoIL/fwF7'
        b'3EYNSj92UDY5vAduT5dgNbo0w3nlAnZQzpT4g97FeBDWli48W7uSJS7xsgJFOSGkLaVNCRyWeHqeNRDnhxMUn92WFsISy9ydwYv+WaTZk/7BS2CJ1VxvkDZOTbSAhjuJ'
        b'61jiDLvxwJA6QHyoCt5d68MSnaosgMHBl/hlSd9ePZclyrGqoK/pIrlPa5gbzhL3hU0FP838CYuUUudxEieW+F7SZDDo+jeSUcGHK6ezxGxZInCf+RdSzpgV1kksMWK5'
        b'BxAHKUmaSVwbOUt8TSsDN8edJY+Xbcu2Mtqz6hxB3LTppEGkNxuMGS2VpIBbKobBROehigks0WYSH9TmOpEaZa91zmSJDXNsQXpGHNWARPHZLPGWzBPURi4jRWqY8FQa'
        b'S/zQdgLITv09qbt6/6rlLDHGNR+ExiWTjJamBhhrdHW5Auxn9jA4owo3JyPxOw/MYhn7GPz4jNVPG0Ws3tkNnLCcR9JMiuHYs8T8pQ7gptNU0nTSitBSlnhz7hpwO/0L'
        b'Bhdpwr5EY8xdklhQGf4h6c2YWDsZS1w0JxDMq91OiAHJT1cBlftP93gaLOJAt/VP21uzclGy7ZYD2eO+WVJ/bv3V8l75u3Zr+FmGOWX9/OZ34i+Lz+tSb+0aHMgoDk4J'
        b'mL/tz2f/9YfYHd+efPqyRWHHke8vT+ncrsr+kZm5PHOgqv2vl+O+ODcl2eKLQwGV48GxZzXulhdaVia9+PI73+4e7/t2s+e738X++Nf9L/rPtHYpKEh97mSGzC70cvax'
        b'+g8/3Wu3tGDe4LzO3D6VVKLXvfhp4zvff27/Px7vXvj9ntW/+6fTHGFB0B3+9o63PvHv4v0F2Vw+fUvi+nlw2rE12r1z2147GnE0NL7wNz/4uFsdj/Ydt/wbfULCRyX3'
        b'E/73qxPaW9aHPF567oc/LEyIX/ny5a/dEl7Iz/nJ60b2T9+I6jz/0VS9/bvNQpsL9e0t+d9d+upM/o+TPhp/tOGb+yVTXl2Q7/PcD8uWSzrzvuss/mZZ1vXFH/4l1O9G'
        b'0k3rf1xovfXHb+rdZp/fdOt/RS0vbAyMnSLhsm4KW+Bm+IoZoIpDr7GYCiMqtJ31J3saddpkSUPT0fYsBuTAc5bwOKceNoeyE8oxx6pw/HQYPEJcQXlaBjUtRhckzr9y'
        b'QnmcOcfZNOeYPmZTjxORvmXy6mUllTVVKiLT14wm0UlontHWV8sHQpG+rjVel3ZbALBevLbfIWhQFGQownitzzGMGMNc27ktNtQ3QS9v929REs8HQ0q/K/Fc6Hbqzu9x'
        b'7XXu8bzI6Q9N6KcuCo5O+vx2p5bZ7fkt8w3R/cKgfscgQhbq1S1WOODkope3uOGkPNvVdJmWPFHQYtEebeB0TDTkdwd0ze33kvY69ZadFvV7xvc7xo94Sjdt0MlZr2gv'
        b'MuR3zO93G9ft1O8W1i3vd43sd4pkb5a1x7QsMTi1LOp3CsAUZ5J1CA44OOmnbV113YNMlSkGdfe0rlUDHpEtgs9MlAGPML3gjiWutb6oPbpdPuAoHnR06/AwRO/zxvXF'
        b'YfPL67hOpmhsOKZdPeAYYB4mTSjCT8Ts8+l3HMc+PTpsemLFgKP/HcHo7M1jRbeX4Vhj5Wf+9BglifUkAODOJPMIuGWdXVgYYki54hw8KHTtsDL477PF/aYnfiouQtPd'
        b'Aefgm7bCnXlNee0pV219STinKWdb3s2AMF1Oe1C/rd+gi9cIZGE5xKtXytU/DyYe2KxLzblZPZcAitH8+4IJVWC99fv5fKy33gZPqLxSoG8+lfOMv3e3ApMBRUl2bYBi'
        b'jBqsgMKCuiNyqDnFqpjs0eApOJuBaQ9GMZ9SuGYUAaXwzCgWlMI3o1gqeViV4FZwFILNlibUUWylA6uZYutCYFWB288iRaFQKzWacoFZcS1NyGMlMOnapk0XGAYR73IO'
        b'1U+ox3mFJQVDuEBN1sNgyIKCIYEZGLIwgz2CdRZGMPQQ9dFgaLS/AD+Xrr/NnTKvEOP2/agT+AP/fHSWdaML1QdyNTtw6F7p0n3vRR/wP9D1bFfr2fTeLf7USVj9wpat'
        b'MTF1O/3VwljtGbf5z0dVRJfnv5v/xrwP3nxHzynilj8f/UbdtZiyia9viW52Lawbv23G4If8lf6Jbk+95Hgsc9LNgx8cqHr18+S9J7fIx7tctcs+8Nfx2XeqasefSPa9'
        b'8Wauvdihq9Plnf/Z/PIuSfuGWC6Ys9jv/Cq5xJpK/Qp4EJ1EnWXDkp+K/bREugbkzVtBHNfmxD/wQD49N5edELr94T7WoY71ppupjEUHwD2yc2AlMsD9ItRKtyqwiaKX'
        b'ObDJaco9svCchY5mh0fIWHPpYY5gRhTjQdeV4Fm0G3bC5nzYBXeinVkyuBPutAA2bhzUGFZEtaJVqH0lbM7DMxHaHi6Bx3gAngpxsOLWyavoulMA3JFD70thDw8ILDno'
        b'GdTsgXZNYde9jqWiDtgciZWmiAx2L4czzqsFPc9FGzK9aA518ATWwZphB7oQGSHJzJGRjQ/NHHRhqdu/rT6tX2+uPlmUlFQrV5WUrHEwcn6EkUDnLaLgE+VptQXw8tFb'
        b'XHfxGBR6teW25BomXBWGXXfx6qgb9PLtnNQxyTDv4OJe596iM8UXC/qCkge8UvRpprhxRxO6Eg4lXRVGXXfxMxHJ5Q2Rd/tcQ3m/KKY39qLFgChZzxsUh+h5u+0Gffzx'
        b'j/WgvwT/2A/6BeMf20GRl97GTNzZDHHLqzTqMFIPXrmqrn7IsrZGU0fWJ4YEmjq1Ulk3ZKutfmARfrS1g7RNKf2YWTyWEIn4cLv8RKIn4q9/YnmotWCYZOYuIN9PIBGp'
        b'9N0vkIITNhNH6lmMaVx703HdAJaC0R8sqyolTG4PM2RZYvSnkjBDPI2yqkJDEhCzXWuZVCVfXqaQT1njaKqDiWLHGKeA9aA77VTOsRzaqr+6JDh3fgnpAAmjriXt86AU'
        b'6hWkEUcVwB7HuGssgPCU5zHPX1+AJWwBrEpMff/YhXAwK0TRqcXHFv/6QmxmC2FRwrLdYxfB0awj4k4lHUsaXYRhM2spYLecsKsNeBr7/7LWwM1VvVeLeBqypaxJ/tW+'
        b'9+KoAyVZQWh/nzXR0uWp5et4vueOSRgqEe2Q/ikqEVG7p0koeqBWtEnCMRuEROQMW01VGrOlnDWupoYbQaYyivg+EWxdaQncvdvTOjM7MgdEIX2OIWaSgk+7Y6zhT621'
        b'Zvsv1pJuGjs3Z+aBBf87ueWTgSDKZy0Cf9BlI+XiyZp8sACzxFJFvlxZUjJkXVLC7g/FYduSkhVaeRV7h4ohLNnUNbVKdV09FXdqFfkivKheZir1kB3ZYSLH2EVZVVVS'
        b'IuHhIcESzDecPFj/Sx6Wc8T+vMaEfL4n9wtILTeD29YgmUljBmMmfM91sPO+EwBEfv1+8QNuCbqZWPj3e8cOuMTp0q5jqjhxQJSkS7/u6tPvO3HAdZJuxk0713scrl3o'
        b'XS6wd6Mh2iF0TyDan5utyc6QZMoiBGscgPVSPLlOgC+OYD0b4+/dONzNe5weQEQFQyDhXNDLxf8d8H9H468d+VVxKjjG6xH/T3COGzEdhZjBBGBi5GbaFeiIcRtvs9Uw'
        b'LOSRjcEEPioEJyyOG1deKMzkKywx1cqMakGp1phqY0a1pFRbTLUzo1pRqj2mOphRrSnVEVOdzKg2lOqMqS5mVFtKFWKqqxnVDtfGGssEt82WxfYPWkeB4e4JkQkC0xrb'
        b'YljtbgaAHWh6HpuB0kHhiVM0WuSLHUe0scMJL1NeinE4HeIyzlV4m7WYE03HB5fL16xczpTqh6liM6rLyLTxfwv837KCUHgn/E1lUIRgVM0x7uAk/WSvc6iwUgSY5Sqk'
        b'6Qfi9IPM0net52KRHIrhfDmdIO+HWJvr8EYqu+d6xB2y6qfC+s8Qjwy+scZabrmFGZPaA6N83Iy/9liO3I+NBbUVFtVcXHRmeOspaTqgE2CGs6cC3GKEomBpNUINwGFL'
        b'M1Ftsc7SKMAfopo7Fn/2I26FEZUin4xqVZ1KXqVaQ7aYVyrFcmMTqDA8kleXkz3qDz+SUCtXy5eLSXMkiKer8FNq+mjGtJRccY1aLBfHyOq0tVVKnAi9UVGjXi6uqRiV'
        b'EPko2edDycNS8bSMVAlJIjQlNTVvdm5RSe7snGnTC/CNlNysktS8tOmSiDGTKcLZVMnr6nBSq1RVVeIypbi8pnolFoxKBdk6T4pRXqPGgqy2plqhql4yZiq0BnJtXc1y'
        b'eZ2qXF5VVR8hTqlmySqNmC7h4vRwfcQrcZspMLIZXRxj8xA+SaDlIiHTQQCm5sVatEKpfuTDRvTGPm+8wG1UmCeLjZ4wQZySPSs9RRwjeSjVMevE5iQOraklZwrIq8Zo'
        b'QFOmuDrGHHFo7BI/TjomvMWmZbr69emx0IlNjQ3/irRGTCHDivswerHN1ZJtJvDMpJVkQUsagSHJtqy5SJdFN/f7wYO8dNQKXylBrKfubxQ7gDeTbsuNKo0IXSkD2gmY'
        b'mAQPz6PLWrOQjqiWkagJh/IKaSqwcU7O7HTiV5iTk5HDALgVHbRC58ezTsInJRbAFhjKLcSlttXWKcZt0q/AXXAv8VIMzyL7t7Lz0x/olmiXBPaAwhSLhXA9akNH0Xaa'
        b'kCqKrJy7L7ICpbari42G/1IJWWOfFGKRXJr9g5cWaCMA8QtHB9Ap89SRjuztx8WNRIeTCtLR1mwBmImeF6DToWLqlR1Yi9o1KzAyQjsB2jYFboXdZaoL79dyNFZ4JrH6'
        b'7fa1uyZXb45yfMZi04/RU732pgtfgpkL/siJfzszbo61/vztI028nN0VXxyazGu78UbpWfug6r/+9u5PPwnuFt5YzwhCZzjcc+dtXXb/tOP6e9l/fD9Q+UpY8LI/gKuH'
        b'Pik598XxJScvPBVTWfL0lz8ea+vLywi4Na/0249mTJh71eol2/Di8VOq3r74wTHY+9nvEg5sP1b/ie/b2puiHT99cGR23sfj7v/uqZu3Dvy1ftUnv/2x7M7QbItjf705'
        b'9XvfiJmXpn4apihruGoT/M5569lX/imP7IiP/27LfJ99mRZp50VvxArT4K48headjI743YlFkxSFfV5XfveXp7d2CPcWNKpTy3tvPPdx3o5y1Rcuu75JPLMjozq9TOJM'
        b'LQZoF3oFtdvgxpXkaGXoRGQY2hrJAa6wkWcZG0T1+bmL0QnULDW5uVrYGR1dkWEWtQnAXtSCTmZFZOZIM+D2ZD+0k56+ADzhi7zq1YnUSAL3wAvwJdbHBvPLM6w3bFr8'
        b'PYLEJ5fDU1loR3oO2gF3oJ3oMDzIpuCKNnPRRXg2mvo0lMDNTiY3nF3xZp44cBvae49yy+mImZhXcBrhqCnPlGJkliyMjBTiJDsTnraAu9EuuFPEWlrqpqL9WXkyiKNj'
        b'TkJ6eAzY5HPQDmEZvb22AF6EzcYaJc8CfLSXQZdw3V+mqgF83hduJLoBefb4EsBF+xi4Iw4104fRhjK4mzxNx6cAdePHL3EYO7SB1gf2wL0WVLGAO+XD1hhiioFHF98j'
        b'x6ZUxuQTW8t2CT2Eg7SuMS10CB4G4fAsHz2TizpZd5CXObiRSWrZTAA8j4vSyUC9Zi5ra2rzkuJ7ETmCheRIjPMM3IfbuY2Wcibcm0EKmRMCdxFXY7KYbr+Em1CQxPoh'
        b'vwabfPCz2RWpLOQF9qncGWifI3WP8oLPoUbytBS+psBNnStL5wF72M1NS1shcfhPrmWQ/SfD5h9zIxDWQlQYH5SUYAWVFbURJgpVsQoZVsVabAXcAw1xA6JQPe+6yOuG'
        b'Z5Bh8YBnXJ8w7rqLG1nWaFfvmnLLM6gveNqAZ2qfMPW6i2eHxjBxX0P3iit+UTfIncQBz6Q+YdKgm6eee92FLAPM7o4zZF91ib4p8mpPaVnV9nTL01dFoYN+Qdf8ovr9'
        b'onqFvfLTootBF1e8FDLgN62DdzMotMOqnddePijyalvTsqa1Qc8bFHlfE4X0i0K6ed3lV0UxNKuEAc/EPmEiLtugp0+npEOyL7wlddDVo62kpcRQdNU1rFt7LXLmlciZ'
        b'g55+nbIOWTdvwFOmTzXZnrz98I+V6cpolxoXpudddQwc9BbTm8YfcRC5eV0cMij0ui70M/AGhMHk13JAKCG/ggFhyF0rvr8ziXbbFvgH63l77MwUVCdWQdWRL+IpNqaW'
        b'98tm/Yd7nPRuqZldy8zc3wmoPeKh7vYjOi5xZPvXevD9U1jHnfo9wF/EkWDqkxq4DgliwVmbKb/OwLWENXDxSwj8fLQ5xVh8kzll3gOLTntRZ/HeYtrE94OLhmErARQY'
        b'4pkQRahaKVfIaqqr6iURODuuoqb8V9t/8PO8kjJV+WOXdsGI0s7fO58tbRApLUbIP1vYf6eUfGpzeOxiLsYx1IfIfVq88J/Huv9+KYlFUV2Nw49dQvmIhly0dxFb0ghz'
        b'VP1rCxv1M4VdyhlNM1kkOViqylmTCh3Hj10ZBRmC9sOV6Vh0zSfyik+kWeP/HGz/79VH/SIwSqPHrsqS0VWJveLDOtnej3wcreG/XZ1lT1KdpaOrE33FJ5qtjuyX1ZZ/'
        b'd2CwMpEW/LHLvJwM3tPANHijiqjCjgtovi4iNjKquIoeTPfIgv5fmqI3Szj3D45S71KJaq4Rqx6SjBqlcjk9Oq9MyWrsox4kx+kZzRSFquoluA2ma9U14lny+uXK6jqN'
        b'OAXXebQ2GYobBjcPfnDlhIiYiCjJz+ubY63KFkkYuj0XHpq9KJxiO/RqNS+ZgceC0GHVkfHrGA3ZvvDJureIKb2L+jnHfbEyRhFdvpU7+2ypqxIJc+QLP/4OvbjX40iA'
        b'7/zxbl6bPCYNAM9vrd1/P1HCoyAS9kIdVtMoiqQQ0lpgBJGiBqphlC2zGtYPYMsSk4LBqgexARSnesFNcLPx4DcQF8ue+wa3oFP0UKbZqCMhCx5AF6m+yFnMRMLtro+0'
        b'31sQ0zk5F8TBxJFGAgWUZP2MrCtW2hD//Mktk/tcQgeDJNeC4vqD4nqLLsw/Pf8y7zeWb1i+U9cXFDcQVKRP251D4N7alrV9jkG/yrL/JqCreSNLU2tu019k84SODevY'
        b'kUgA22M45xNvSQaPlv+Gc/4SPFoaRzFnobKOtfZpq+pUy+V1xnlbqzEat+gJlnVqebVGbnYSZVn9qIRIGgnUWppQmoPj4KTwj3yJUl36CyaY0QtIRlfqeIZYVkDyh+NL'
        b'q5t8JgMtGQUzMmNHG1YwDzYajStjWVZQI7qosrDawdNMxSls+rKX7Bvoau3J39HU5ZJ+qkIBNkWME3c61X36Rp78g5Xy0tDPIzZ8uyGg9qVxhku5f1p9MTuYu0QAlkpt'
        b'K3OlEg6rVz5fCQ+bNPrVXDOFHh6ddY+cWABfhAe4Zpql3Wwz3dKoV0ID2vQzG7DMHMk0yroSUx9RcLbGw8Soo26N2ODSQAZQn0vgda9xhroBL6k+7brIsz2utd4Qs2vd'
        b'Dd/QPsmMAd+Zfe4zqeLysWOg+W4Adug0PWL8PGIbwHtkGD26dGtMA4psCViBB5T7v3UsxxOqC/YjC/PYs+QWAiDJuWRkZr/mE3XFJ8psVn/c0ROBpaGEZEKOoxyxs2F4'
        b'YlgKHngQtQHqPk1WOEwu1P/ZfQ1kMSCbGWMxYFgu1KhVS1TV8jpcG5XiUbClWrnKOANGR0SPYXJ9tJ1ZwRpzaUOZdkThjCLEBcoVWpXa2I4KHCqvEyuUZao6zZi2bSKV'
        b'cAk0NctNeF6FYYq8SlNDE2CTZruiQqnWPNryrS1nS5Q6LQMDINUKLUkPo89QAnbEalOpcF4ZdXICf35euI3eAWWZqyXaM3wNbuRl5ZL9Q/Tsy1wZ6kQd+ekRmTmoSYqa'
        b'IguQLjs/nVsggT0Z4sVlavU61WIrMG2Jw/LVyKAlO26DYOfCESZh+izcA/fQ5wE8g/bMxhP+HmYFOmc5NwkdpmceVcGjK9FZdAS9bot7HnUD+Bw6XU1P1kTb4E60R2Ov'
        b'nZNO3I5mI510DtKhnagZ9hSlS0k+2zKy0VYGC9bDktXw2SB0ZPKkIg5Ae+AF21nwjJNWhpOJwWLuNVoyC7TXWLja4URnzZXNsQCznhbAw6gd7VVZvWDPaIhZY0NL8L73'
        b'Eohg7j/UGoxBjnBFWxQalGw77uF/YtzbuUekc7I/Pt5VJ3JxSQ3pKzJ0VM0rik75ouw159yL17MPZM9OPpc+IWriffCdRv7Vbz9/S5gl3/Kl9E8zYvbwrye9ElEhuOS+'
        b'r7dbUG195nfzEjv6bwjuzU9KzH6t1eOd/1l/J8xjUiyothQ3f1YksaKAqQKenoCnGmqtw5johQw+sKnmoH1wPdpLLaoQt8NpmzC0Herj2RN8tTJ2HvAjh72ccrGk3mlT'
        b'4G54MFz2NHhwQIES6Sicils1Lstox3ddReySto5cV9gD2V2RDSJ4zjTD4HTRETvTFCNMoDZjFWzDZIzG4F50lCAyIx7rRifYbZWbEtHxB3sqvSaZbLkOOAIxZ2bAC4nU'
        b'milDXVgMsNbMtfAQa5PcUoYOE3sm3MbNEZgMmodR4y/tbFv/0LT1QISQw6ZGTAwjbtFp64Bx2iq1JX7QUwmia9jVcMM3rC98zoDv3D73ucOWOn0q2QlX2Bt0QXpaetVr'
        b'Kp3MUi+X90syBnwz+9wzB13ccApefp3xHfHXvCL7vSJ7eVe9xtN4uQO+eX3ueSMSk3QHXvWKoLeTL8f2D0+MRjMf+dljZe5My06PwwL90XMkXXoZMUneGDVJjmiLJsZs'
        b'p06eLcN4E59a7yd1J3lWMA4csYn+dQa2CpPFCovpx54nu4g2eQyYtMloao14INh/TvH9Nw1CElpU7eMb1w6PLGrimGI/dXbqw4urYxRawh3iLVcrK4YEGtWSaqViyApP'
        b'WFq1GiuO5Tyzotqa6rMGf+2xMjkD0HnectjXhNHZ0ZPFODr7Cls66/PwrD+85L+WbzViTsdhvtn8zlvHN876D1HNFefPOn521mcPrmdhPJ1AzXXpRzsCkCZgp0/Ts8Ob'
        b'mx+9pksbjH2KPoIbm9DkxO4QIU6VVxOVXW68V7YUA4ExEQBxN8CTcmHepAlR0dTRgDgBKIjBBWvzj8x+uJ8SxDOq5EvEqyqVRjcGXGFS5wcxTJV6VPbVNXVjZKNW4opU'
        b'axLEKQ/rR6XG6vwChBje8zoMIaxztamAQojj6NgIDJGPdOyElTE7HZMKjHCCiXH2htthK2xFZ7PQ2UwQjA7bo72pwdrJgEwTE+HJrAhZWCaeiMxTGE45PXN2aCZqQcfY'
        b'k0exZoWe97FF3fAAe3zAWWkG0IPQxValpWFMlhu7Bo4uwpPk+J6xVsFl8OWszJxCc1WtudAKvZ4v1CbhRyeiTeRYHxmJQhcaMwjyCCdYxHwBPF2amR2RIQsTYPzhiZol'
        b'tit80XEKjeBJ2LtoBDYiFSJ5h6Id2VgHk0pkmXywBh2Fx7hWcHuiQsJlj6E9hY7OojlzAW9KJNrGwOMSD3oOfe66iHD68Hx4LiuHOIt3cJ6Ce5Vaal05HzYrPDPH2IgM'
        b'cAnBMGE/F+2zhptUN0A30BDz+P/+6cC+92Ixwol9GN3MMCx1kx5zPd285LRTVIeVPAZDnGUhXts64f7/5cx532ru+xtvWU8wLK3Y/FWVJu7cidA/nalTa9WnKjYO/ZYR'
        b'yr+5tbHni883HivdeNzxi1sBYe99/nbdj0sF7faGpW9LF98Ii7rx0ZbPfbfkTjDY/XTxu1Xqw72/xdjoy1vb/ry+57LvR2/Y7leByFIZWO+LwQ+1Re1AW2RZ8Pw0stIJ'
        b'OGVMNDy8gkU9p3N9COgZRjy+GIM8AD3oQDG7L3ifB1ZujfAJQ6dMSwqe8L9Wdq16Z0xhVkZOmB9GnE34aUty6taGiTPpRrBC3HXPmEEffB9dQAdY9XoX3ESLOAntDjLt'
        b'Ss6EGxnYmW/aVrzXZgpZm86AJ+DziPiSVnEC0pbQpBeg3aF0h1keexquFPdVJOpBZ7hoD4aj3RQ4eRPAS5drTcWHHQ1kuRbuSZbY/lsrrGQGGL28akMAgFG8rHExRwVG'
        b'IsVGQ4DFRmV2xCY2adekG57j+kJmDXjm9wnzydkVSbuSDGlHs7uyrwVNvBI0kd7OGvDM7hNmmy2/3jBbfsVPdSRSu8AVFym9MXPAM71PmE4WXisM5Vddwq77hHVPGPCJ'
        b'0c9gaZVXXSIHfQI7F3Qs2LdIP2PQxYN1qd2XfcUllCaRPOCZ0idMIYud3uJB36BrvhH9vhEDvlGD/mF3LHgS57uA5+9CFzqtgbt3W0NLQ98Iu4MDC6z+SL7+RL7+DH7N'
        b'4uaDNe2Ry5tGCHaPoIKxGvuoCXz9hMFXlh3DhJMlzvAnBV/PCSLACzbxv351U0Lc941lemxU885Ic74/mVfxrENn2eFp2dx+L+ERT+MeTi7Ob4bETf00eXY9+doA2O0f'
        b'iprykhK6HKwmZxbQNeghbpmq/JEL0UMWpoUtYlOlFqEhuxGGFwqAzaDzPfqUqbJO/52tmk4PDT4zZtgCqIcz25gehAFaiUvDZnCHx7Fz/NYS2Lt2xHbxu8p7gno0fX6x'
        b'fZ5xL8W+y73u6dPDPZ16j8vYx9+MnTiYMOV7bpxd8F1AvviYeJuHQ3eqGCD0vu4YMihMvMfnCCfr0u4IgIvXdcdxg1iX43NcknSpmGKMk0LipDI0ksjvumPYoDANk0Qz'
        b'GN1MY6zIkbHcxdcdYweF0zHJfSajS8ckN9/rjtGDwlRMcpvO6GY8SGsGSSsdp/WdpaVd8LdCWjUDrz38qt247zhWduHEHzvkNgndEQKf4OuOUX0xqWxSPjipHLY1XLoC'
        b'8QN/47jaiY0P4NAdqalaM0m1MhhaLyMpn5AKMYlNILBL0xN32rJvXPwbRVftMr/n+NoF3QP4iySXxdwm13emmEo9kZQ6vmkm6yJOpph0tNFJk53LKtAMPAr3Aus1HLTD'
        b'Hu4a9TYBQIcccRN3HukmruAU8xTcYr4KFAsUvGIL/N9SwS+2UgiKrRUWxMF6LujlE9djoxs5Q12QHU9YDjs7R2LAbqNzrOAqrMzcjokTtp3R5dt22O3YnlLtMNXejOpA'
        b'qQ6Y6mhGJbnZK52M2wYtqH+wg86pwlLh9MA5ezg/ZxJ7uLSOJ5yHXbqJIkGed6rgK1zGeNIF5y3c/OBaSF6FU8FRuG62LHbF9WKoy7ibQrQZFIsU7vjbnTiDF3sY43ni'
        b'u54KL0zxUnjjb2/i4l3soxPgJ33xPV8dwCE/HPJTiPEdMb32x9f+igB8HWBMJxBTAhVBmBJkpARjSrAxPA6HxxnDITgcYgyH4nAoTVGCQxIaCsOhMBoKx6FwnRUOSXFI'
        b'qrPEIRkOyRRRdEMm2UEasdmqOKKeh5XI6CFBynLqDX5sBCYnMpS9wTqEs6/ewuoGeZHIErWc6BmsklBeP+xt/JBP70j3cjVOYLmyTlUuJns25OzSSjmr62ACUV9wmqzd'
        b's6peXFPNKiRjKQwSzpCgZKW8SqscsioxlWKIO312Qe79pMq6utqEyMhVq1ZFKMvLIpRadU2tHP9EaurkdZpIcl2xGitpD0IyhVxVVR+xenkVOQYwNXvWEDd99owhbkZa'
        b'wRA3c9b8IW5Wwdwh7uyZ82b0cIb4bMaWpnxH2LSHnWuDGGLTxrMdR2M79ozHLnY1DL9ETcEsm4hlsGMDZyl3dGwTq2rs6/gmmoLTwFmDdSXz17I18RsY0/VaRsFtYFYC'
        b'dVADo+Ap+DQ/ZqkFGPVRcIdLISCGMNPVGixI1vDJEUcktWqctsKCDZNl7Qc5NYCSYZ0fl98GjPqYyo9jDu8irrfEernVZyVj6eUPu+YbefGBZ/7DDzxK26W9xeracjYN'
        b'SvkZczjbrQnU+b0wTxYXEz3RnNUVWEXPqCCqr1hTqyxXVaiUCumYCrKqjqjTGGWZnPBpzibTCjussMauVpVpH6FiJ5DbCaUKZYUcQ4lhVi/FOruqvJKkrmLbCQ8YYz54'
        b'EIyu25eEo+67qqqpH8CD2oQEa0KGmIghJupLIoK//Bf+3OdGREXlSiyGHB/Olqxfy6tqK+VD1nNITaar1TXqIb6mtkpVp+bgXhzia2vxUFZzGXJUHItoya5KNdnZ+DAy'
        b'IWwgNjMPUt87B7afh13vfk9gyW7AeloK8aQ/6Bd4zS+u3y9On07w/erWyYaUKy7B3fOuySb3yyZflU2leDzp4ur+YVzv7tU+fZ+1nj/o4tYe3JI0KPRoLzSk9HC7p5/K'
        b'6sm6yB2QJl0s6JcmD4Sm9Ael9PtM6xdOa5l+E0eb3ZKrn37dN9ig3FeNwbvNoL/kqG+X74B/tJ63x/7f3R9K2+xRKNfUEiaQ+90Id64FexeYrcWZMzZlr/papbgUs005'
        b'Rp9VEWnsb2lphPr5f6fEPQzbs49Z4h9GlHjxXnYn6X0v6nc49sAaUTSOqWi5P1O0n5OVS3mj79mYzLwSLmXNIUu5poRu2BmyVK6uralWVj9yo+rDFfw7YU5PtoKKzqUd'
        b'S6/5Rvf7Rg/4xl7zTerHfz7sztX75dQ7ULu8TKkm3WPsF3FtlbyceBbJ68RVSrmmThwjiRDP1iipeCjTqqrqZKpq3I9qnKsCa3N4dMsVS7U4IokwMpWRTTc8DdFD4yyH'
        b'X/0Hhl/9Z208koEZsbj6H3iFw2dfjyXOZ9cSJYcV5crV5ZXy6iVKsZqSyuRk7biGdUPCseTiWnXNShVxMSqrJ8RRiREnpVolRg6puLPUuAmmyauX0fVQTV0NVsGo4K1+'
        b'LCFrFLCmIpXQIpWSXtBSocqKcCLrh9dBcS+Q3VFjuIOQt5kq6yprHqAYqVijwrOVMRnyGPErM99j9ag6GhNKIO9DTSg1Aqwx/Ep+1vpaVlND3q4mrjA382ppVyge6oYx'
        b'p59VSjUWLisxOpKXEQe5Rxh8f8Hdyz6XLpEuiswKl6VnSIkRLWsuvAQNxBaKdqTjy7zZoZnSDJkALHe2RK87wC1aoibzJ8DXYDPqRefyQzNl5I16O8Nz4bll8BA6WCBD'
        b'RzggbiZ/yQz0EtWNbNEOW01ETibas0rgDE+ik8ABtnEj4LPwAN3yk1SmNjePhubKwrJkBaaEs/hAAVvhSUdL+DJcD4+y7znVQV2ahp6EnoMaYSMf8OFOBvVCXb2WbHIp'
        b'S4OthXA72j0bbUd7ZhMLKS7vyTyGnO6aPYPu6q3Pm0lKxQdc2M7ANrQZp96NtmvpqRctcAM6pklnbahZ8AUecMJlVqM98AQ6IaI2WHQcnYQHNaR90G64ERdhLYNOzucU'
        b'qTquRfA1Fni0OV9wXzvr/UxetONfP1LEtHasFdvAAOt1z4hcHf65Ycn1rFlfvPrS5z2aO27tx39w+nvrkWs5js4T24IWzV606B8fP53a7jJthffXO2dv7jUcUWzeUDc/'
        b'J+yrsME7f/tcFf7cVvmpXcc3lsZ/f/dycvn0AYUg5uu3v6+fUTdtSvS2F6Xntr2wyGYgaG5CYvQ566zif+xslMcmrxuof/fe9r+8so7/h5grl6pu73o+z2UqvPuPmoAl'
        b'z3yRc2OG39ObflJ/vsPrUvetmKY3Pv2b4GbOS/3LdlRNuFCw/Mtvd1vL1/RdDjtyMay+ccecvpzf99zb6fLR50nXng9Y/kXepQ5FGfpfi69rv1KeeTm1TeV04DuXwTa/'
        b'hAtTBJ9dlTixG1ae09TQw+1RswXgyRh0LgKeDER6aqOFR+MmhsvQVtQUmY62c3FfPAdsZ3AFcL0rfdgVGtBW2ByJozCAF8nA41Ph2XHwOD0eJR5dSA/PzMnGd/yZ0ER4'
        b'AL02+x77JjcJPEhMuzmwydkCCHgcy8lwK1uaVnhqdRYtD35MxKATcC88GDedNSzvtUHPjbAsD5uVHSegU7Cbw56+0hoGN4dHSMJCja/bdcAsfBCd4dbD9Wgba7zWPTXn'
        b'wXmVvbAHdtrNYq3Oz6FnQsOND/JymRB0HPZq4AvsFqum5MXE6JshjYBNkWR04hTEYt6Up9F5tD30XiBlQFCV9WCkwu0BQZHsYA1Dr/DRRiFqpe5hqMUS7mBrStYumphl'
        b'6FlgoyAW8FPLaPtBAx5hu7PyZAzgrGRs4PEUv2T2oOTWZCF7zE31ItNBN+j8U/foe4kPwRbYm5WTlZUTgZqkWVCnhNvzaEHD4A4+PIWewU1N3wYXlImac+FJqQDw0hh4'
        b'RAhfhU15Esf/uE2NfJlk30ijtisrXEtGzidrvI3AYcy71M6dzm4mul3kCJxEbTYtNn3e4686Thh082mraakxlB+t7KoccIu85hbX7xY34DZBzx10dGuzbbHt84npTb3q'
        b'OOm6m0d7YGslpos821a3rDbYDIikxg1J4/pCpg54JvcJkwe9g655y/q9Zd2K3ok9yy8WD3inX/PO6ffOGfDO01sNBoYcje+KP5So5151FA+6e11zD+t3D8PI2cNXLxj0'
        b'9NZbDHqLO7M7srvdPvGO0qdhNG7I6veLwmDcK8AQ123RNXnAKxrTRd5t9S31BvcBUVi34oooZtA/uF1A3O2mt4e25JmOu5n0sVB62w74RN+2B0IfA/eaOKZfHHPFJWZQ'
        b'EqNPvSocR/YZzbguDjLMPlrcVXxo4SfiGH36oMjPsOqKKGLQ298Q2p6Hk+4Q3LYA/rG3LYG7r958B5GNmrwz5VfsEaJH3zy8OygJd9LP9+W/TGZ0ci7YUw4M40SOwXmS'
        b'1wCo8wFF2ERjGuE+O7wmSr3l+MPvKOXTM4DB8CnAxKog+E+60H72yViALpVFJMZ986z+QfApBggEZAzDeiOuIyBPY9R8R+MH42LzQ8DwIRg4NuwbjUaKRkNMOYExI1CX'
        b'CQTVEHRGVtrrCX4cXTJ5eSXr+rZcubxGXU8dAyq0ahZIaehr7H8ZkT1sWBipAJlt9KiTq5dgLd4U82eX1quH19ZZhjQtrZuQL8GrSo25me5X+O3Rpe7lFfSdZqHrZfLs'
        b'rTONr87em0BfPRbq6Khe6OdpPDX200kXwGoGRAUKkle0L7w2kQIY2Au3w2Mau3B0yY4DGLQDoJPoVbhZm0ElP9ooy3oIB5oW8jEq8kU7KTAqIi50czFQI0vzD7zy8CSw'
        b'xtcxAe2PVf09rZ+v+R+c5O/5Cm3LZPJO1GcOvKiycXUVb/jhJRDoVSXdv953/fOFZ6brujJFb5atfNN/TcaN7unTMs6kvff3358tf73VwaC33T/wt++zDJeL1G2zEsGH'
        b'0bIN9wY/9rqcduSzW1s8+uZ+WxFR3v4Byp3+6Rc20a1RhdFZB3RhC499/lX2V76x8TZLZtVo5p78za2dJ57OfDPgr0sWwSsfe33dWel6nPu87z+ObUgcOP67+zMt/lYQ'
        b'cjXl9X6L2BvrO/+y8asbKwPvv+clPL/+buadudNXOz+jbf5o+cUbl778Z2f5jW/lAu+omKKnVkvk937iVFkmzE9eIbFnJzzYmm18vcDkpex7E8+gPXTWT5o0LosHu8yA'
        b'pcMcbtWkGXT7L2yEm1A3bfWe+cPT+ohJHaPOl9mF5UvFOHIzai6CB8kx2eSMbLjBgU7NPLQFtuOZGe5H+02z88ip+STaSuEJalZbYHiyahoLUGAneg6dYvdonMhMweXZ'
        b'EP7gOHkbeIaDjvPhXuqTl4Dxwwl6mjZsGsceqA1fxzjiAC1eIOpAPRTdBMITLMCBvczT7NmqB5KtR4IbdAC+ygIcdD6u5h7RMcpi4V6qlmTgopv4cOI82iAcdAZuZUoi'
        b'LeFhr2C2Hht5k8PpIj0f46I5gqUcX/cs9gC7s7DXYcT6PdwAdazvoi1qouCTXwEvhfNWSnOwFoKa6OtoHWArVy2AByRWTwZBrIDZsXXGzSVGJXGNvXGGMl5TfBFmxBcK'
        b'J+Ad1DmlY8qAVzg5SN+rva5zbcfaKy7SQS8/fdagu/c19/B+93A85bv5tlW1VLVW67nXRd7DN7rLT1X2VB5fesV90qC3X2dWR9a+nO6UK96y3sALoadDLxackRGIkNGR'
        b'sS+rO+haWGI//vNOvFh+xTtlUOh+TRjRL4y4KozCCXZad1CjnIjsdTFMv+IiMW5m6Z7eL4qmPonz+haUXFtQ2Y//JJUDvqo+dxWZ9ad3B52S9cj6gyb1e0/STyfV0F4h'
        b'L4XyM2j7RVLTo+X9kvIBX0Wfu4J9KLQrr987Fsd39+m077A31B1d07Wmd/KAe4qef13k0640zBsQRfQ5RpifS85aMakB8zFOEGXPJB9xhGguQQ0P9Ukox4gTyIaAHCeG'
        b'8b7zhL6O6k/Bo45E2w0ebS5rGHP/30qgdlcwDxYWcCzB6FjDiwICYhFUcJ4svlWlhJt7nxOsus8LjoipkPBomw7ZllTXlBhNWZohrrxMQ81yo01wQ44lwx5u7NrPGpHJ'
        b'WPzQjUzSugmA2OVuGrkr7VrQ+H785zIe8/nhQIPi6NKupYci+72i+4TRN738D6d2805Z91gfyuv3iu0TsrsxR6zsDL/+wJKs7HDaALua0sQ1LV6qVzYwj2jyMahkrUed'
        b'P3Z3qL1xSvzR9LFTerDaUy2pG17bUTANnH2MgjP2M/voytAj7vAOWDxYUcKxLEfHWovp1I7Kz13jNoz1lqs0uBvKKylKWsNNEIessQihdrmQISZEwmd73EW1vLZKVa6q'
        b'K2EHg0ZVU00HyZBVUX0tu6jA8gC7jW2ITyHlkCW7bIhvjvS9Fg/vZhuyL6lVKzHaUpbQR9a4mhhkBDmfsAepOxaIxL9HaZhzFcs/rLKsa1nXLTzl0+NzRTQB88k1r9gr'
        b'XrGDQZKjOV05vUEXZKdlA0HJHdP/GBA+FDnxovB1n5d93uH/1v59+9tcRjaPHHkZOJ+5DRif+cxNb38iHLGwEXnrbUevFAybybLx1x4M5RXEEsv8fBcbO3QMliEdeoBP'
        b'nWh4uWss2XqHhqzhhUhxL3BCJGqy80HCYaXZ8MZE8YOzLnALqemJp6YFGJawkGO0cf+wAVyPjOmNu5BwOuHk05d5v7FDdn2i3D7H3NGVG97fRgYhqdqTCKMKjlFgkHfr'
        b'3LcgwkIcrGHLP1oqWJSQwwhxwe2HC06vSzjDtnnyPpi0o5ldmb28C3an7foCp/SLpvQ5TmHLPeYWxRnAKEKZUcUDDYyCMY35tczYdWhglnGG6zDEJPVw1ORcA5atjZ0w'
        b'nzF1grEqgpKSKnLciN1wTchlGY5yN5CtyPAkPL03dsB9Ip482cM+DHjClPQ5Sv67NfI0inHcK5ykyeryX6qLcmRd8GXF2HWJG3Cf9KAus9lT33+mLs+BYQmMpVgTZ1gC'
        b'xz2Cz8aUdMtCAVZW1B7MI/gQPzUGlTxV+KjJlWHv0vUllmF5D9rnoY2OD6QWbivlihFtRS5J5pp08LCU8vHvLO4o7h5/KrEnsd9nwrdY2ExjBv2Dj/p0+fQGX4g4HdHv'
        b'n4zFkWsqc/OXGnR4gY0UijAHWwFb06kYLAL6mS6uHtnF5LKWY/Q/xF3s5WcY3zG5TxTa5xj632XNNKMDIRlsU36RM5eMHGXkkkRRKxmjC+F/rZwLh8t5nzPll4fQkpHt'
        b'Sy5XkYKqhgs6ptQl3olkSvnlCWV4y8sIyTTW9ECWkkZMDyzhKY7xdRCES0Veo06aHbslq40F/HfakmwnocYubgOZE8dY6jWlMSyGw3u4D8QwBSMjxqcdM3J8mmqPpxj5'
        b'/2PuOwCiSrK1b0diA0pooAlNEprQgIAKRhCQJjRKMCsg3WArAnYAMcwYUEEMmMEIRkwj6hjGbNXuzuzs7GwjzoLs7I6+3bdh3gbG0Zld3+68v6ru7QSNozj73m+4fW/d'
        b'unXPrTpVdU7VOd9RKCymGHL9Dh7N4ulvtzI00woO6n14AZVWLwpOL2hf0C2M07vEDa4dY/ONol7FZ2ZNx0BfrHwVF+GZnabebGYnCRsw+cQ8lCIuZztXt6V1f9/Q+4O0'
        b'nP0btFwZabkodd0btJZGt8hSIMDXm3DHWWW1hxtrPoypeYfXq3v1mu+reZoSs5onCU2407jSNe/l28LD4F5tum5hlN4l6hV1j5eyrSoefK0xc/6Qkxk243qDWscGEn1O'
        b'8iqtDEnrSgwHolSY9RuetZawKpOj9limq7BoD3K9HVcCdlyxmN8+F0n0bpL/pb6DxMnN39eCNO1mLUgS9mBmevfV04WZlGLZXAFv1XkcXtnIDm/ctaLprvX6DepQVKRV'
        b'65QKVQ2qmJHGijGm7cfjSg41UHDxEff4RHf5RHfyOjXdPuORYiTyP5rUmtTB6xJF6d2inviI8dzR4d7lI21OeywKaAuhdbFu0Vi929j//Ypmv7Ki2W9Q0fR8H/3GNe2I'
        b'JOaKqio1XdWuxqo2JR7FneiVda3t9plgqmv3LpFU7yY11HUIyvP/RV3zX1nX/Des6z5WyJtWtQ0BmrccpfD1adzRt1nt6EYN/vemOuGhOuEa6yTsdepEa1xksv5tq1mm'
        b'r3v9vPMJfxLoDC6pNWvrc0xekofz6jxlbEb16+MjxkNVg+ZiIkrttZSn+KYa7+PVLq6qUGK/4GUlqkqF0nzhhjH+NNa/fVERXS5qghHGJjAkXcRsjp1shmTzFd0+U5rT'
        b'PkecHHw6vD28Q9ktwgicvwuN6lBcXHJmyY2Q7tApOJpUWkviY5/AtgR6BbnbZxy+SkSZlp1ZhroK0px8JvVTLPdJr4g5gXEjXi1fOwzBzBaMatARh5K6SRSacgueJNc3'
        b'8ADrzdQGmhu1R1e2rmxZ2hF/ceKZid3CRL1L4lsRf4H3vcSXvQ7x1VUaC+LJ9S3coQ5a1V+MHSrPjEStMccQRBkt0L93YCA2n/mW/PoK8ksWWZJPru9iTvQx1v2hUprf'
        b'DlZ1aC+uObOmWzhR7zLxh1LNCOaj7nvIVFVqLcgk1w/YjOsXIdO7JR6P/rvf1buM+t+jzY5MVCU0gK7Z1IVTfmShNvpgWNLWud1DLBQY+aKNYnwq0ACK19fUDibuULBN'
        b'a9Z4IFZwFFxa6F1pRviaIZZPra62sxv5xmGa8zqDJKkWnvxP+PxlILHaVVWWi6uramm739gY2mtAV11dhbH5X7JjpH2sWDSUehu4ss92ua6kUqtaqaT5k4aj6rNBJZWr'
        b'tJo+jnJF9YCpzARJRQ+opuonFFhUP5PyIa7+6XT197p6t8zYNZ5Yzcu6vTP1bpmPPTACcWnHtPZlXX7x3R4JzRxGImd03Kmdvt2ek4eSzM8Qydodkx89wLVS/ZIhTVNR'
        b'pcUhWDzxNztZGtGg67IyZalWVUOH8EVyUEWJRltE22z0cYt06gp1Hq6DWfhgctI0dus+W+OOkgMxkqCtaYkBD9lqUBfgA5nAFuBDMT5gjFH1YnxYig8EJBJD4anxerO6'
        b'Bh+wqq1+Bx/W40M9PmAVQo3BS9Rb8aEZH7AjpboFHw7gw2FCJz6048NxfDiP6+ffHaRzkOcnsyeJzf5XMo5fn2C1p4pFe37yuQKXfnvKK6ZB9sQ/WO/o0+vr3yDv9Q1A'
        b'B5F/Q3av64yG1F5RGjoLDNU7+v+HwK01rT2ovVwvkn7g+kgw8Ru2q2A09mac1I/Pvgqn3H0fu4TRrpTuaayGNMZ3M6LXLRb7bsYR102cMqGfzfKYznrO43jmYYdOe8pJ'
        b'2Cvw/JYdIvB7RqEDLtYLH4T9XHT5FWpJJ2EfoqD0kSAQ+1JG45tBTA502T8F5fD4is0VxJOAO/347IWjncD3uQdLkMt6xmcJJj/jswXhz2zZgogXtlxBxDNHlkBiSntu'
        b'yxKEPedzBPHP7Fno0nAmfYGqKh5njnjB5wvGvXAxHWwEk56PZAmSnvOZwyR8CMUHybd8niC+n0IH2qsT7ylLCxdq4Fa4jTh1Urae7CX5uhmV1oND4iX0vTxLh06ClsZp'
        b'4JbhgJC2TJQeTj2l4J7nDYjSw0epNmapNmaxe0yptmaxe0ypdmaxe0yp9maxe0ypDmaxe0ypjmaxe0ypArPYPaZUJ5LqgVKFZql0XB5PlOpllupCUr1RqsgslY6944NS'
        b'fc1S6dg7fijV3yzVlaSKUWqAWSodRycQpQaZpbqT1GCUGmKW6kFSR6HUULNUIUkNQ6kSs1RPkhqOUiPMUr1IaiRKjTJL9SapUpQabZYqIqkxKDXWLNWHpI5GqXFmqb4k'
        b'NR6lJpil0i6qY4iL6ljsoqoYh44BikTsnlqXhES88X3OGBSnwATm97STNcAU0IBkZ5aJCSA0IBt2fyC+GKUllXgSXKRkfPm0KmKIZ/CYIDFnDF5+2GmCtnhTWtrmMRaB'
        b'lk4SeFXTDHmwGE+5JTSuj6KqVIfXsIwlW5RWpTYUqNLSW8z0owYDu6nJOQWpTAnFQ7ggWlzIyhiPjxLxIrIhjoqj7SLNkREj6VcavpVxhdWqlbhCLMor0RDPW0wc8cOo'
        b'QSWVVFSIdVirqqjDQoYF5KLFwxbCHpZesLnS11OQ2LeXi2UptQ2Wp7CpVaOtjjWUTKU1Sk3WLROMEhZHQa3mFBkVVXLFtbjiWVzxLa5sLK5sLa7sLK4MLu6Uub0rSnew'
        b'yOVocSWwuHIyXnHQlbPFPReLqxEWVyMtrlwtrtwsrtwtrjwsroQWV54WV14WV94WVyKLKx+LK1+LKz+LK3/jFZJji8TGKxa6CrDIGWi4Ws1eMo0a9MdQ16nUAiWz0MBd'
        b'w1vNXSIbnFfBM/CFhq9AecimDbcycIjcfENu9QgFVkIzB+c5yFrNPcg6zFnD1eYY6eSsNi66aJy0ucbybNAbLfyjtTPMn1nNM8RUY1Fby7mYk+xWc5YY69T0p9EYRU3D'
        b'zsRWMRyiUdrK1SdR2S8T6KFt0ED46qGObK+m97GK+thFRS9DBj69uAQ7npl814izrkTS55iHhDbVMsb7lk9b/dLxEDlFKkUfr0in1Kox0D6N7NHnTMeuNuKSqY/hGj6D'
        b'DziOtboKHwjw+88pYkRjAcuHdEzavBuVWK1TIyVeiV5BJHEbYm6lLenjFy3TlJNXL8WIcLwiJf1D8OEEhseKSAxam6LSxdg0mYQFLdHqNEgdUCuxHVBJBY5sUVlWhSgm'
        b'FaoqU5USnACkAdDTgPF2yTKt6YP63IoqqkpLKixxbnEc2MXYoFqD6CPDMCqG/NLxYft8igZUOVKe0RDL5OWh82WaPntEpFqrwegHRJfps0HtgtukzynZ0DJ0S9holFp8'
        b'Q2JPOx3gzt/HX1qLSNCYgQpbUd5oeR0PaPSIbZLTSbBd4QAyDUF3v8Ba3BGWce9V25bcWquXTuryn0R8PhZ2exfp3Yo+F/piw6a20m5heDMXm3ly99gaA7iQGC29oRE4'
        b'gEuwMciL2CLIiyGOy3E7i2gvhl//IBKHWBxoHqOYSfQLJG7TTKLlT4gEPx9oyMr84Cgwe5wMeQyEBYfh3wDjdWQM/pUwtD3xCyKvCQ6hcxlyB0lOT2ifcGrSzqzm1JYQ'
        b'vAg+uXVyR9wjUXSvf2BbQevKVm6vl+9R/1b/DrfPvKS94VEXI89GfsDV+09s4X5OPFrcCDxmpD6qQD9rXlfUvG6/+XrP+Z+7iVpS24I7eJ+5SfudqeDRX7lQnoFtwacj'
        b'2yM7+Y+EY/UuY/XCsabYzG8RP1cNWEP7XHsO5A2Db/JIjgV4sykkw4QC4o5RudQEVBhJwzdrqxgcSOz3qkCyjqqsDkkwZpLFW/qPq9upYXyJO4cyj7QyyjJsDXZ0WFal'
        b'NSFVkmCKw8TUJMuaHcMh0hMTaQLWtIxWM5hGHOrxLUi8MBwSRVbq0TxizQAamSCNwyfyVcFqhiTSDxNpgvKSWAlW8wPSSYycbg2HzgBLOn+VLKaDfmp0ixi4HALQgYlj'
        b'XKSYYCKv/AiiTtEFEUNmrP1Uo8ew5kIiFlgJTyIV55vSylRK/EJGlUClowwmByqjKKERhzOVGh6JTlVa8msIOxNOTHbD6bAt4W8RruiT4dRsGK7ZT401Gz8Ya36IPpWc'
        b'Mis5Gh3S3iKQDKIWDme0jbAkeoIFBDBGc1cusgQDHkj81Ly01OjUtJSCt0IDVv9oOMRLOeY4HfMPzKc/Io8wo5lAynj5GfBFBrifScWpBKuedrarqC2p0zBAt+JKZXkJ'
        b'Xs0dfidF3/Tj4XzaaMtuGm7opgZ/O7OvY4RUcVj+zFlz364VfjIcUhMsh+dQMk1XVS3Fyj0NBIx0/urqKoy/hXQIHQ0d/FZ0fjgcOsdhOr8ybOC9dC4w4hq9NT0fDYee'
        b'8ZgeP5bFjLEMDXsl5Uqz/la9uE6DXT/F05NlcjRMVgyTUsbk7qfDoXSSlRY2UVhRVW5JoDgsKy8t/e048ePh0JlsSSftUFupiNJWRaEfk9goDksbPoGM2enPhkNgqiWB'
        b'vlbRt8VhOcOnjpkLPhkOddMsJW9TmLoA2jMZqZiVGLaHGW9ozPXphXnT36ImEZE/Hw6tmZadeSSZt4h6zsAVDZ/7UOPqh0NSjmXjhg+chfAKAPb2wudhKbm5WTL5tIK0'
        b'2cOdOJmW7hoOqdMxqU+Mtfe3gaRaLmJIxeloCJ+mRMRXEgVMY1wkthYwHk1Es2TpBTjse6R42sypkeLpebKcZHluQXKkGH9wVtocSSRxtUrHDL+YKXOo0lJzc9DIQheX'
        b'npwjy55Dn+cXpphfFuQly/OTpxbIckle9AaycF2r0mA/+eqKEhxyhsaXf5vZ/OFw6numZc+SPvSlPTVfBprN6/RCEd2tSshwVaJBZbwNc3w6HGLnWHatMQOZg178koqT'
        b'TbBtMnl6LmrmVPk0PNlj3n4rsn8xHLLnY7IDjWQLC4iwSi/PIZ5SYGauegt1Cw0LvxwOXUUDpnkmcgFBQaSpUpq2W8yXLN5m+uweDqWLLEcFX7oGDbMSxsgQ4w0lK0KI'
        b'0dBlNctoZW+FPs1x60YsK1jYnGIIy8AhXO1WsDSOQz1DsOHYq1nWjV5QqhXHUMOC+mqqyDyn/eCcapH1dOvfXMR79f0lgsFpKKfT4FTDZgDrlTPqy/F5NNIG3ngzajq0'
        b'tmbaArSuzUkltuoHuP3/G3/mgOjVZJ0dg4Or/4UOEo5ZiGuyCozrz+jL4FCu1BqW8VeKBjKc2U0lekyDl6f/vpbCbl9rdq3Bq53jWsc9FE3scLvodcarM/V6xqUMfdjE'
        b'h6LM+24fej3wak59HBzRkdoZfF1ySXKj4N78D+Z3B2cag0qiImITrvte8m3hHhW0Ch55SnvdPPfn7MzpcYvrcovrTO2JT++KT3/kNm1ADEoLnsZ/CE9jFtpP1RFIGXkB'
        b'7Vo2uGthK5vBXcvgbVSFJwASbwm7rLzClC2PGrp7q12sm+Ua9rXMzWzLzU3e6ukQub0opY+LdwqsuKPaMnsIRdY+gr6jxm3FOEG6CntcgzFyAXY2juwSRXYT++zPhaKW'
        b'lN0rmp1fsXac+apP9HiT2L91JDwOvZVl+D4eYSvr/rYVykr0fVZ2JciNWvx54iE+r0c0uks0Wu82ulfoSb5NLgmyZiJGNj6IUVef04DNK9JVSM8ydap/Ukx/6hNY7l3x'
        b'ma0rG0baVqfhTHxm24pH71pxyaYVF+9ZkfgLfY4WG1Z8Zr+KS/aenAbsTDmYb0zxmR0tW9OGFr2Z5GS5YaUWsRleV4vxWRCbGKsPacplGWJMfQ13koG2GV14NwiDxBIz'
        b'LjuBy7ceUoHPVwoW5TeKwOLnPeex/QpYDXIT6v4EjKc/6dXI/GZ5GFj6yRiWPpkG5idJ/Wyue/RzHl8Yg9KcaPj8XrdMjJ2fzWrIQdmYJEyCbwGdhMH6Jf1slnvicx7H'
        b'I6kh/Stbwwum4BekmJD/ERUTMRWTCRXkwV63EIzyH0pA/hkLM0yXezJtYTb4MSZlDE4ZZ54Sh1MSSIpPMAkzgHH3fRIbsk0vC8MvCycvY57CNLql0KEISAX3sznuM1jP'
        b'eTy/PFzHjpQo6LELGjLHoYyipIYsU2HZuDA5HZ+AsYSLwpZw0cQSzsrHMA2ICfVLaJA/p2MYsAQ+z/gcgfhre47AizYmC0YHl9Www6FGUO0oyYRbI+TZUgyOA3dwqPDF'
        b'vFHgJOiE62wGBaPFf77GgXuxea3JtKyemsthU0psVmYcCOfySArHLIVPUrhmKTYKHnrWtoFdxlLw623n2ils0LU9xp8vYytsUYoDuWeHzhyxodlcQZ0DGoUc+1wHsHW2'
        b'SmMZT4xtGAAn0QMgy0LUYKMr43CJ7XWLjENeORZKjCN7HTOec8laTp9dkULHWJvaYc+PkgqVtq4vcOAOMaamyNzISGPwSQxnE7NTQyG2hjIM3oliM5BrHyulGhGv1+Lx'
        b'058eP5lN0AAJ2RJlfkaFmWLWDls9UP/zFaKtVfqMUWGxeIsdDt96X3Mce5gkbMYk1L4VCYyKlDhcEhqGJsEohEgJCa/rwGAgiq32x1NCknXK8HQxJP8Q8WILx+hcisWI'
        b'VNpFplsYo3eJ+SGN/xFxhMYhzP/JnDZIZmUoJYLCNkwotpcy+Cj0iKRdImm3MFrvEv06gmT99wqSQ1QULUw24yb0ZRua0Bzrx+gs8x1l3d1NY24lxzLZF1nHjLDe8CTa'
        b'Qxh6wrq6ZkXlIk84E3cuK6oXQRRy0Jrs38ys99ATjoOfWOI8OM3kJMvCY2QZBm2KMl+3WIbxxxeZYOZDB9RxqGV2RZWSxs+mkYFIFBED3iORjZCyNJvFDKBEPFOPx2cT'
        b'8IG4RWAuQ4JcdbWyUmGABHIwewWddUjPPk6JQjFIWCWMgG7sxjyI4zgRHgxoi+h495Fw8ufeQfrg/G7vAr1bQa+rX49rUJdrUJv2dF173UPXmF7RqB5RRJcognb5eSia'
        b'0CvCd9e0o/N44kdR0O1dqHcr7HVx63EJ6nIJ6nEJ73IJ7xj/mcvYV3RBbB9o6oIDfW3MsTgGdbZA3Nm8rH0kkeMP4c8UUKautrtO7yIeTIoRYxQbMFkOXanUDlYpu5wq'
        b'ZS/wpPGfrPrRWOHlneyt3lz03Boz9+tSNouk1DKTAaePo9EtU4/CLWmGRNHH0lo4ZPO0VdqSCusfSm4dxR+KIQ7x4Od9KbVblHgptWN5S/LRjNaMo/KD8s7ULlFitzBJ'
        b'75L0j4eiRDI7b/GV2solTgP1EJNfCWFNE1caRXZags9gMw2gzmETjX6A8I7b1yi6j8ENZU3GWYMpxzaRSHx/xucKJEiCdPPp8onrdo1vSH0s9O8Sj+8WTmjIMDt9xmUJ'
        b'YrFXQQx2ZPB5wbcRjMOOBwFfo8vxtEiIx3XYAI8orMiE8ApsjJSyqFR4ITjQJtsPnrQQDA32ql//B16O8jYXDNFfNvnLOcSby8GxZRR8hY3CVmGnsFc4KBwVAnTmpHBW'
        b'uChGHHKay21gN/CQ4DcSiXs8JATyGmxxWKeGkQ1eZTY4QBMRIW1ISCaDCGlLUtzrKYXHeaGFD4INY/8vtPBBsGHs/4UWPgg2jP2/0MIHwYax/xda+CDYMPb/QgsfBBvG'
        b'/t+U6kzTX8ZRBCPKXUgeqQp1W6WLYQ3hBGs7a64LyjeSCek0An0/iwR0GknOcDgnVzs6kBaHoPjyjbFwBQ1OqHZcSP24Nrg1uDd4NAgbPMvcFWH1dtgnYRbVaYP+e5yX'
        b'GKP2xOB3odrkKCLMAnK5G/Pano80z0tCQpnyedSFo34Y2+eIGdNg6d7Hmt7HypXw+tjTUvrYsrQ+dlo++i3oY0/N6OOkTJP3cVKzsvo401Km93Fk+egsIw8dpmak93Hk'
        b'uehsejbKkpeLDvlp+MbcLDVGq0dPyKZLnPrYKdP62KlZ6jw8vrNlqOyMvD52tqyPLc/tY0/P7mPnod/8NPVMkmHqXJShEBEjG+TXSgzaaXQMOrzwforAIlNIx+ASUGSO'
        b'BSgy184C8tg8sDCLeofzDpcBRR6QagRFxn7Qg1QoMm4aoXO5cgJv6wv2w2u452lhY64UbsvB4WZNQWZJcFepjMCBZkfKcmZkwPaFqE9mYjBVcIZLTYLrncH7seCkamtP'
        b'IUeTgIosObLm4Mejccj43e172htu1e9k2ed5zpr6OGdrSHZMV+RMvqP+p9x8r0/utzpRzQH/Om3rv+6MhEMDyd+E9XwHcCYyg2CUgs7aaDY1At7kgAs+4BiBWwXrixxg'
        b'Uy7cgmhgUeAkvGYLDrJXeI0lGO+8ULAONIEdcEdWFNghgxvADhvKwYMNN0vBPaQKWVu8wHUywKLVzZzPDOasuHtpMCQriffpS7kJWyK7XEeRyTi323u63m26uSmrAaeG'
        b'nhhtTDa3ahwzyBpWJ/GRZKJifh8xl/FwjLF9cDDyEl8Wy/9NQ2Hu5YdQJx1iOKXmopqTgVFw7MW9NoZg2Ju5m3mb+ZttEN/aI77lokGA12CDBgZ6KOCTeHYuZU6El9HA'
        b'2Ohg5GU7wsu2ZrxsZ8a1tu/YMbw8INU8MLYlLxtDxxh52V9OghsnwKPeWYbYg4h1o6Kk6lU4TjKJMYyZqnB6LajPAB0cCm6vdoDNcBNs0Y1Dj9qAbSzToxmoL0TNZLCc'
        b'M+E2NBntyJoVBhtn2VYmo77CpcAH4KKDIEBDQKVvxfEpRxliX3Fx5N/8l9Iuc7B+ziSNQABPJhsgpcFFuIvkXzPTltpTE4qb2rFQ7UPpIjFbd8KmMhL+A7YGGgIkG9GR'
        b'Cbq0DTUn36YuGJ6hw25cg+fTs2Q5WZFwm4RFOcjZKyPgKa8knRjfPBdqXwNPRWRgHGq4Oy4mBtQXZ1GB4CoH3JWC9bpolGnyLLgpQo7xhLflFJrBV4dJo8JgQ3Q4DgH9'
        b'LthQJbFF8/DB2SRYCHgP1gdkwSZZdjSf4sNLciHbCV72JTyuw90TdrLBsQhc2VE4w45l4CZ7DNwOd+kw68fWJC8Nj6CbwoayXc62twONOjxqgA1hgfmWBJQmIRJmhMEd'
        b'kbBxepiRUBsKHAK77WfB3XU63GsWgYtgaz4iIKzGiwqTqEntRMMGsE5TAy/D28u4FAu0UnAHuAIu0UG6b4EL8DCq7G2RUkTa1qxZ1ShnQRiObx0ZmVOYAbfn0hjf8DLY'
        b'kZdhjGdJwRMcR1zQGjrA9IHViVn0LQncko0+2PVduHEaBx72mqTDTjFp8DS6Z6Ccohyy2FGwA+xbtJiEj7GVgx35OLYLDm1cwHy1PdwXTgbapug8isp1salODiJVD0+A'
        b'y/AqXAvOwd3YS2QllQNOgaskTguoBzfkqJUu1dbA90FjLbys5VOCaaEiNmgNRF+NBwrduzINSkd8HTkzLDMKsY02FA3k9JtM1Yu+AuyGN+wpeBG0kAfBXRwtJgLXDqot'
        b'VCk78sPC0PDcEC1nqormTtgwFqwFZ+woeHiiLoiM5pFggwNi1Pc18PpysK1W7bgcXksAWylKGMcB9cvBdR0JzHHOpRA2IabPiZKiyuZRIxPANbCXg5itOYB0mV8s51J/'
        b'nDGSoqYUV2R6BlJ0hawDx+B+cBY2aZYjnQruoMAWsH6xam2VLU+Dt8S9X57YWzCxCsS4XHVlx/q3tMtB7dprHfm3xLovf/Odi8e5wm2PAsSPZpb8qebPhTY/in6S+03K'
        b'JdmXzfbOsiNrav/268Oaon8enM398skUVfnOfx3o8djjs6/tFvw2lDet70ezxx+74/MX5cnbvf/0mDBnzMSQuG+bjy/5q33gn1kj5j490P57fsyPAw89nhjev+6n6etS'
        b'juTN5n+z7kBe0j/+OaIl7OeVtnXHd06zO/v7xLnhAbLI33uEgAWHO5PGXm/54+d/9xrxwcN7x2J//rsP15Z/3aRayJ3hnvDj25fv71+nOv7l9W8e7DjTEfqPaNWj7EsJ'
        b'97+Y/mDdb7t/lfSnsx/PdDp3MfKY38yTy+YqKvP7qzxyFtiMv3b8Fsj8VceaQ1t+03eusmn7n1snXboQWPXHa9pHATcvXQ3uolpfJn7ZffiP//oL98YM4ec/njKn7cj7'
        b'a/w/P3/H9tv5rra/2/jTkzeDon9+5Vjl+rEvPvvN0jRFdfYI3rRg/tOL0/L/sm5HRq1H/6dynfDbS0lejz7btzGx7eRfWd/xdh/a+ukv8r61KT80VpBwNvDhxLWjj7X/'
        b'ckJq/MNyaeAF7/Ls2KMz/76rLWLjEdf4mbZ/mMVb8uzB1vor5Rm5n2z5/F3VicotK4N+cTVpTeif/2TzF9FW25BcSRDBY+eCznyThIDFA7CBRyQEUfRz3OngnaW5qB+D'
        b'7dHyqAwM1n6RTYGj8OTKd8jzsgC4yd/PMpA5AUGHF0bQQOn74NlS0FTrJLBXw6saeE0r4FNu+e8u5+SDa7DzOZ57cheWZuVGeYBOEigmGXSADUQ4gScrJsCmbNgCG5Ei'
        b'w6E48C4LHCwDbUS6UYNbNogyJF1JYAMh7T026rmn4HFwA16jw/80+meBJucaeK0aXtWhFzsIYbsDezE4kUwQ9cPBWiGDqM8He/0wpD48WkIe1WbDUzochkcWGS6RklGT'
        b'ojzF3IVjVj7HHoHBHMcsaQ68mMGn2HWsCX7wHF1dm9D4eQZ17S2xi9BIhIjmJrLAJXhXSofE2aWFzVlodJsFm9GDC1nR8eOf4wlrHmwK09Q4LtfB686o3211thW4au1h'
        b'p3MN6ujwWu1yRHwOlw8+gBvH0YGG1jmAnRFRcFt2LAvNDPXwyBwWPK+KJ7j16aB+KmzKABc84D0kJKxhpY9E9AVgAvaVw/MACXxN4HxGDkBTsTQzh0N5+6ER/iq3dsQi'
        b'OrZPC2hbiHNtR1M1agEk9E1hT4yB+8BVsJeOJHQefdQ9cBycw5D7ZoONRzZXkDaKli03wNtolmiKxvzFo/gRcGMxO3A82EiaD4kFcBe6yQyVPMohlw1PgRa4F+wGd5/j'
        b'vQ24QwfX4/IR++VisQG9BM3k8Ewyn/KHJ7nwymQhHVVgn2QNk49mUyfQMQZs5KRGgfOkQla7jSJRnrZlo8qKAgdlbOGKOeRDCuHpAPwoKlqenQu2wR0oi3dWGjzEXZ4O'
        b'PyCNOnUEG1WGad5yysfsmBMNtpDaAptEiOimXGkUknSyOIgRt7DhDn94Gg2oDYSZpiCx4R48C95HuXBgr+1othrHXoRmzmPkQ8H2lbgu6HugIZd+EQ/slCHODA/jwXVJ'
        b'mSTGQYBQgbLJI0FjNDNnCOARHqqM6zwe6iY7CD1u4JwzIccYDGJk5grwHgdx5fmI5xiGHm5G0tr7uGdYqCqgEeyItlwziEDz1zZ4b3mQPTi6DO55jhe54fvw5PKBD4N7'
        b'1fTziPsbsiV8KhuJgZdT4XnyiAQ0pYIT4DSZ83Yg9Qd9YkYO+tbt0VnoO7bTW1bTwCUbsGOliHzqavC+MzgGttAsAgxP8CkPNA7cG+X6bwfTMLjmDQTTIHs67gO0CHoz'
        b'h+g077Pp8KUVvthHLLRj7CNhHNFqmPikT4R+GAHykTCMLB6md3tP07tNeyr0J7FOo7v8o3v847r84zqnXc++lH1/5P0AfXzqfWW3f/brx0B9KvTt9Q/tSOjyj3noJ+9U'
        b'XF92adl9WdcY+UO/Un1eafM0DCy8oHVBj6+0y1faUXtx9ZnVN1JuzNBHT74v7PaVNac/8fI96tvq2+MV3uUV3jGm22t0M/+x0Je8acr9MV0G8Jhe/xCMR9UR2jm6239M'
        b'syODQrx7dTO311XYUtNW3vpul6v0197BD/NnPZxTpA8p7vYu0buVPHH16nEN7nINbit85BqBPjbrchYpPbPbO0vvlvXEJxCD1rWt6vaJa7Z77OrTJjzt0+7TsahjuT4g'
        b'9oZXV0AKKrQvJKKj4OKcM3M66x5FJfdzWKOmYlx2USrGZXdHRzTZ+LchxVLaWXt91eVV5A2p92u6QnK6veV6N/lTV7+28Y/GZHcFZTPfNr4rRN7tnat3y33iGtA2v8s1'
        b'FhUSFomDRxxf3RM6tit0bE/oxK7Qid2hk5tTP3MLfhIa0Zz6CP36hxCXxsCwDlFXYAI6dza6R9J3DI6KjBsmDe58cD7JEhR6Oqk96fSk9kk9QWO7gsZ2ByXizOJecSjJ'
        b'zBTBuD6OCqWdMYOj6RLNAtUye4bEVRO/3fFx4Kg2XU/o5K7QyQ9DS+5P+zD7QXZP6ryu1Hn6+cXdqSXdgYuauXudzdTrEQwMkcGlmIuX/tUYQUgdh1dnHEpLtEbvYL6m'
        b'dLFymfJ1Y2aY9TLcnYqZP8a+9r2d7DrW1TGs2f+gXvbtUqSs57K+pfDxK3J8A81dg6XhE/x46n2HyZy3sHHEzs2kEobaXLT8EmPEXAub0eG73h19xbam9Te/tLRWDcNG'
        b'i0bQDPpTxEysBnGYWlmiiKqqrKiTvHVA4T6HIsZZo0ileDOS/2VpDRz10JcGz30Zac0FRKUxfY/5B7yNIeuDV+yhW6cZL1ea+SP5FRDHD+z2YfQEe1vaaHcA7Gav01aV'
        b'lb0ZfRyuBRtEE38AnTYKFSTGmAMmZxVMM/EifmuCye6W+xtzLB+TajIIDicGwaoyxgJ4GTb/Rm2urMSIKYq3p5I2GOhzLDIb6d6MYDtMsJNhv5n2BsFmy+U4rpzR++yH'
        b'YE11wBszpiMmzmT2HTp0jG5LEs3fbtw1L6ZoQyIGlYpDli3xtqYxDuEaFlm2pMyWLVlmC5TUOyxm2XJAqnmg6e9bgufLrQNgLsTUsUhIbIyAZAiCzfnBgmAvlrCfYmRE'
        b'qyGV081DMVvaDWvEmsVVugoF3l1HY62qTIW9fMtLsLWx1bK0DPiSeGqFsgS7ZIhTCbQIZigmVjNx3sLTpAr1V9rRQGU91rNGSQI4FhcXqHVKNP2q6J4evrSqUluFJoDS'
        b'peHiCtUidQkqHDutGKJCWy0MO15oB41t6DGDeSYdVJF2hqkz8zGxWhrtJmMkML2kQoMoHBzOkKAdmTOFsdMYmYIjV9XW/5inwUrYfP2sgx+P8951uH13QBPLlRtXfYpF'
        b'je9m/1a0RcIiKkco2AivmekbcqmZxgFulqI+5mLoY4y5AbesXKldGWzRyTSlFUWkBlF3wxWimSTFuYhygJ/HGx4VYspHjOEp9G7m+xqMdZmlFEW2VIoNVuJqDKn6em90'
        b'4TK7Gv9YSz1fIGaxRr7prkYzX0y1OURwrKNDl5GOz4Qm5ZF9CxazA4fxm7k/WFjS19uBG4/O4ZlE7kAlE+89NGaHZ0aCswX0kjhOyM3GK/LgHGh0UKUkjgftqvzDe3kk'
        b'Shv/1l/pPbcPMm7vjkW84qbZHwN/86JXsvWcV8D5UemjNsnbpJ73dkuO2J06u2tdHIc6X2g3/3qBhEO0XXB7Bbj1SlVXmMIouwqwi0RdBpuC4MZBoaEzCklwaHgRXASn'
        b'yfoN3AdPpGIWTasYrBSD/XDf6+zKIa7VvBbXahiuDaO59iu1mPL0bSvsCZn4MGTi537h+ojMbr8svWfW41HhHQnHlzan7s212KUj3Cx4lWLA7NKZkEzV4PX4G9HmbeBv'
        b'HFZvOeJvrzeJqIerXcIm20tgH+r3F7KyQJMWR6vmOrPA6TAOvSy+C5wF17Iilsvk+E4cC1xBCfWq1L9co8gG7RPhiYMff/rZhMPrdrdvkGyL3Xhp43GPj74s/muxrFRe'
        b'wn7mudRziWd+yx9ieGjA4VA9AXbdn/6Orp/vMQE3R3c11sBKD+s1Q9rJj26nXq7t87li2xER37hxRozut6UCQjoUXSbEVsPbh2wTy7erIW6RId7rbGgD9N5v5qE2sHuT'
        b'NsA2yNan7WKK3t8nQY+pMva/YeJ+DaECzR+flfC4GoyRFgM5Bz+OP7yusX13+27PGjwunC+r1z9wPKSilq3m+nw3BU0jeOd0UgVe9Rxqba0Y3h6wvIbX1gJmSthmDcAm'
        b'3dXMsnLgrjUxqSRtLmT65pQAylNkxarS0NhWJhZTY5ttkg/9ugCz6eTFu284nbyiqf/tEtqghqYGNTRXXqC6uTGVo8GrxY/2r0GSwuH2XTvjfKmfltq3sz1/u8lgeTpA'
        b'AqAtTweuVNAmp6R97Oj26U9H7ePzhlP9K8oONp/b0wLesDFus//PGmOQBcLgQNSo13VtukJbh2yZ+5y0BbZ7SfK63OIZM8Uj4lTvEk/BZ6JP7rfyv7hPfb6QJ464i+Ze'
        b'XJe+YG82bIrEC+fc4NwpLHAV3ARryao3OI9m5fVceOO1F75xzwR7i8kmQC5YC/fRwYCj+JStG7gGb7HBTjm4Z4UpiN32oOUrYrBNmEJMM8XzbMwUBqPtHp8xXT5jun3G'
        b'mYH6vz6vvOKVoea8kjUsXjG3avExNBgGFtzrbtWqBRu2ORGgYoNpG7/BlRi+GQ3cGrwavBtsGkRIaaQafBp8G/zKfIwWL4IfzOJlUOcfbPEyQU6sHELADdiYBTrBcYNF'
        b'BjbHOJ1Pm2PgJhu9HAlpanjNFl6FV53xHjwxDXABJ9jw5lzQQaxfCvkhxDIgA7FKLjhvMA8wGgfwwUYL+wC4aYUDuMoqlPCJUceSVWC3Bl6De8EGdAWbKbB1hJrcKU4E'
        b'W+EVXXkkH6UfpcBO+B5oJHfgukkhDkiEOQj34a37qxRol4Xo8Efm58HNGu2aYBY2C0VSph24qsMbkbCNH+SgmTMH1QG8SIEWcBKeIzdE/vCkphZuqGFj2YcCW+DWfGI0'
        b'IA3mU46o9lTS4opN8RMo8mKw03MNNpTwAEdwSceRJPXuCtqg5gi8Hoe/4zRsMnwH2APbdGPRlQNoAgdIJQ2oG9ipVcP38zMi4Ba4A9cOPD+LAs2gxW4N2DCTvDLBnws6'
        b'IuJgc1wMl2KheoBrV/F0WOz2jVxATH4M9j7gPFxrwNmeMX0W3BuXmW9DFcIWPryaUqbDezwowxZ4MY7io0+lYqnYycUk2Q3sz4e7OfAa+uBoKhqst634+//8z/+kJ3Ax'
        b'93g2yYorTjvOoHRTUF472fQs41tgQ0YkVje2RWcWhsFGxAL5YRK4Y1aGLAdL/jmIJcC1PLBHgxueXylYMLNcl4wKWY5aoA0bCZrnxByEBqPG6FymdjKkUSPBFaMRE+ad'
        b'c+CWI7ycUqErRqVkg13wggA9slMA1sbY8uBajXshPMKH2wsE6SO9bSfkgVvgDo7Fnla+wq5MuNwe3ubX2oItdrmOoBNugCdi4J1VEn/YMF4KD/DB/qkScGVSPGz1ROTt'
        b'A4d1hbjJW+FN0MyD6+A6ARVrywGdheFIIr48F+7lg0a4GewNB/XwDtwBtheIVO+ADrhWBO4sCRSB64gDNoJrZatgPSc2DJGxzR9eSnXNQe2pxhxG2OyYxJsVz6bGhfsX'
        b'+64ND6R0ZOQ+Cm9Vw6YccH46bJChz4+GjdOJHVpYVPiCqbTtDLiQIc/JIUrde/C6QynqHztIkV/yZFQzkt8qlMWZP1axKV0uKXIBB39Eqx0ldkQnMxcuBbsQx9yE7axY'
        b'sB6eHB+H2mN3MbgKP7CB5+GBwlB4fC4ieq17AVivBA3lsA3esFkMbrvURaJOhdlaCt+DG62RmRGVaQ+beSPdsZknOCNB/3DPOmcHr8PtjgUSlg5L7onzbDALRID9aDaC'
        b'22WRaJBAbSy05cZowD3dBJRlPLwATmZFZebkZxDtUoYt0iJmEsNSA9ujpyIzs6UypEKeRLxOwS0SRxXYWqCLxQy/1ddmCNsjUY2Z9RFjetTpgGjDw0LEajsdbMPGVyyK'
        b'Dbazpq6A+4nJ6xzUwJsjcF/bmkP3gGjYDLZlyqLyaCPBgVZwqF+eLajGfX96XtRMNlVX4FwHO0CLLp8MSyKvLETaVXga9SfZDMZqkNHjM7JzyfdKZ9jWwGszMjJz5JFR'
        b'cmKQiPuc0fyMDMpwa94IcFLpSlggcgkbyxmzXzoUZ39lL0dyHG1edyoZbsii9+0Xz+JQttjermEWXKfDe10VcL1tfq4kB2zLlUXKCmcRG0hLC0gKcfxZJBg0op63db4Y'
        b'nAM3wImMAHAvIyAOXORS8DJcN9J9JOoz9fCqjijwt8EFgE3xrzjb2cLLzvCKdrmOBTeB9yg3DSd3+VQyekagMs+B4+/k40GLg4a58xQ8rwCXiHFjAfrMc1mSKLKsIY+U'
        b'vQsPFoYNdP9cILYF6+dWEB12Xiw/H2wrgNsKc9JhPYvihbPAAb6GNKwiFh5zLnSocWKht+xDAwqsX0MrvpvBHdCEzW+uwk3o5jgKbs8C7aTeQH0WP8tkD+EwF14JYcP3'
        b'lojIk1UhFLyRg540M9qpBFdoQ847oAHchVeQtg23ZNMmMOM96BfehvsWTwKXads1HsX1Y4FjnDRi+gc6bTUG20Bwlks5uqD5sY3j7umjwyEA16BZ5ipiawlZPImUYTMO'
        b'XAho9OZRo8BaXhkaXdeSkt6Fm2qN43UE2MJCjd7CBnv9GY64iXS3IxFMp+BRjuXg5GiO80pXMpuGwEuTbWZnIW5A5HFZ4OiIVPJVXJE9bOKCm1FyYj7CX8B2B+8voE08'
        b'3wfH4EmwsQA2EUsb7hgWOPNOOT1tb540Sp6AuzOHfO1xsAecpSv4gg8xUDwKm+i7k1iIty6BAzQPXfNNgwdhp4FMxKC46/KoALCbZ+cN2ohBalYo7ET9vDFXDreCxmhS'
        b'OyPRwGxeQTxKDtbZoLkU7KU//9ZEpJ5KZZGSKHAbXOFTdolscFIKd9BzemtqWBjchZj3fQ28YkOx4QVWFDwYqHq2YDpP44rUZ65f78aZObm/muLy66u+H8oyGuw8x0/5'
        b'e/XfwzfmZTpcOHstJaPwF3fU809+eerjB8lu7S9OXn+qdzj7Mgjs+HPvJd/xt9oTKw7VVZV9sfVozz+uvNw/Zb/rP6Au8Sdh3el9f08K1v9u0yde3yluiscGV1/82Zwj'
        b'61bNHv3tp8GK1A977oVFbHSrK9y4L3GjB/hkjF1CQazos42jnn/nFfBA87uf/+z2jGe+ninC+Lyo+Jl//VvJiWBtWdosmP7e7i36prMPfmn7yaUl3n/67er1q9MFf17E'
        b'f3b9we9zNh6oh/O2bP99Xnz87AWeHTqx490Txb/MH7V0xYh79eNrUiVNB/71M8m2r0HLX7eMVyu33lS77f1z08iiukzNA0GOTqfKXPoEOp3/dvQveNNmhD75Q1LjX5dF'
        b'zfrVpy+eFJUsXPyb/275bGTZFsdfJX6XUvLhRtlf2rjvLL78yzuT9bMj4jee+TLmhXPRwW0bR/099z9/8nJf6PgP7329QPqTbyO++M+8ZF35Q5Em+K/qysDK0cnf2t09'
        b'+IcPP57/+4nXuleJc1aHfPgt2+b2f8m3/Fq//mczHxxUz9lf9ZHG7p1//mHOnbyjEx5Mm/30rs+sK8v/9p7PmvlZ/+3z1z/sqX2UcOrm4ye3Rm++cNox875d+KWLvrN/'
        b'PuEvJScEn0b5LtnTKXh09bT+auuzvx1ed/hR76dLZns+ZodqmnfH7Bu9SeA0ufm/yvy0/CbZp4vGrOt7UfLLH898sPxWx7OM905NanqQs/LrObWrPdbv2J7w4eLZHsrz'
        b'NZF/+LXbmmsL+n/e+Inzl1+uWCyQly/dnvtb6cNLk/fu1E7u/dHjwz8d9yuZV1DQr2V/Cb8mujcjMh3Y955fPgs0/opj8wed9Mo/xqc576z6MuaL41/Y/cr1P20+/qa9'
        b'8b/iXnwyInH6Ko+df1zw94WNPoHPkht9Ap7JGm9Top7Skt88vN+W+kTV092//b/+WHtv2ohVdk7vhY476KDcOAuAF27z5xc12b9XdR++qPjJPdbV7Zpvvln33akS9ytS'
        b'9zlb/icOfPybMwkzRDOX/0RQ8jSuM/Fh6PLv5uycs/HPjT86svTLiRvdt835S+V3aQ+icz+1n/GvzPAvvmPlnnS6Kv5CEkKb1DWB67BlgE0dODWNDff5uvS51AXmR4Vl'
        b'4cVHbAFpM5HYRXLB3VR1kWmghO8HkrI8bCsdskLQFDHQ6BI0wLNEWQVt4Nw4g6n0DHCZR9mCq+yaEriTtlJsd8i3GL/BoRlo/PYEF5+TAbz83dVokLYYwMEOB9qk8soK'
        b'NAJYGITOmsmGJz3APmKXiEa7M1VILnmPaMo8ir+E7Ycmkt1EOeeBnQsiwqUSuCWSj6Z7uzlocClwoI0F35PCSxGjwXEpntYi0SAKtrOj4LV5hODFmWBflhSegrdMRm3O'
        b'MzkVqhG0/dz+oKVwtxe240P1vCPXJEPzKf8sLpLaDs4j1I2G5xdGgKY4QgKF3nGeHQda4PuEukxwGGyJgLtCDBahB9hR9pOe46C1cA+8C85r0LB5A16wXS6AlzXYMtzZ'
        b'VjDQRhNe5YO70+A5sqE0Dm4ZATfB5ghLC7aRMg6ajy7DO7RJZicPtiOR+VqWYaMgl7T4CLiZgxS+cyGk3hdVIG0PSWybXFFzR+F5LsuGcs7lLC4cRcwp4QZwAt6LyI1E'
        b'Ck0TuekA7/rAO2x4PRSuIx+PhMB8Rtipg/sN0k5VxnNmCbxeEeRqNrchkm7Tew43kMB4Bl4Gty0thYmZMBLN79AstxfuR9JpE7wzzmBoKWML4Smwk+yJ1MB7GuvrLiaD'
        b'wcnwqg24DK7AU+S97KyiQZaq8BDcSXljU1UF2E/aflo1XDvAdHIPomVbhNF2MpXmocgUcDdCmqeQZNJ7LDzKGa7lVAWCW3SfODw6D8nuqOpIFThUglOZbHhwJrxA6gdu'
        b'dwWdU2Xm83E6PEG6C7gIbgvmowo0F1w8i4ll6kiwGbw/QHK5VcVxByfB3udYdAniI4nfiuTSAa8yogtqd9rmFq4D15BI35QTwTc3VvWAm7gjYYfTc6yCyJCQsHFgPUvh'
        b'hlcucS2eQoxkkWp4eDLiuK1Z2TI0DuWxwuG5xXTbXssGR7MiwzJw19sM1iKhCZxj18nBMUnYv88K83/3QDa5zLeWBwdTG2AJ2uc8IAQRDUBgXH4bcJcs/Dnx6NXgggBK'
        b'HHx0detq2uKz0+bGyG7/Cdh80m//ql2reoVBbau7hHGf+4XpJdkfaX+x6qeruiRzu/3m6T3nPQnL1ruF9AaHnc5uz+4JTugKTuhc1LlcH5zYnNMbEnl6fvv8zsDOWH1I'
        b'QrO8Vxjc4fRQOAanF7UXPQoZc0Oqz17QlbSgN2R0p+JhSNKNd/QzCh9OLiSvyvhoUpdkTrffXL3n3CeuXq3T2tIP5j50jWAMTGu6QtK6vdP1bumPfcVtHtges9tX2uOb'
        b'0OWb0Fna7ZvUbN/r6tES3uUa3OsvYT6N0+0f35nX5T+uOQM7o4/bvaZt+UNhGHnfdH3+gi7Jgm6/hXrPhb1CX2wY2zGqJ3xiF/onnHg/7EPpA6l+RsGjFJo+uX7GrJ4Z'
        b'xV3on6S4269E71ny1NW3pbyD16FoW/3INR6/Yezu1YY39LNZvmmsrzls/3RWP8X2SscGodFjutwimuVt0x6LEjorH4nSSNELu/2K9J5FT4WoMR4Jx/VKYlqcegODW22e'
        b'SCLQWUB0T0BCV0BCd8DYnoCJXQETuwMmNzv1egccjWqNOhjdbPPYO6StvNtbis5cPZprd09oC3roGkIqzlBnKP2dbtdRHSMNNZrX7Z2vd8t/6ipk3PTbRu96h1CT3u03'
        b'Te+JodZaV3XE30h95J/8UJhMbmV1+2XrPbNfbbgq3D9p16S28tNV7VWPRo3tZbjKP/jou63vdtReXHVm1X3uh4IHgpZ3H/nLPw+M1EfN0y9U9ixUdaF/UaruwCV6nyVP'
        b'PP2OOrU66UPnPfKcT9CL2pM6Ft/gPAqa8Ng/oiPjbM4N1v3gDyMeRKBCdmY8dvdvs+0IeuQufewf2TEbmwNn4PC9iztsH7nG9vqHHl3TuubguyijV1BbRofikRdtFz2v'
        b'23u+3m3+U0Pg0rba06vbV3cWPEzIvLGgVxTQlt46uWNa58KvOSzPNFYzF30dyjihdUKXayjNmN3eE/VuE59g/DFU6UEEfwxDNuxMfSryowPmnonr0PZEp3RFp3RHTMW2'
        b'0Z49kqQuSdKNcd2SVFSyTzqrORVbC3vun7hzYlvaQ1cJjp2S2usb1Laodd7O9CeiQGyv0SOK7hJFN6c+9QztdQt+xnH1GvlUKOrnoV8MfBXcb4PO+m0pxBg+B3z67fCV'
        b'PeUlPupwwKHfAV85Gu4J8JUTeuZo7oHcfmd85UIFhfcEjn0YOLZ/BC5xJOUT2O+K77hRvhEPfTI6ne7b6KMzHvrM/GjWR5l/73fHuTwo78B+Ic7lSYn8j0YfiO73wune'
        b'lLdfvwif+eAzX3zmh8/88ZmYCozqD8BPBVKSqIuOZxx7wlIehqX0B+G7wfjNIeismdcfiZ7p8Yrs8ors8Yrp8orpdOv2GkPMwR/7oovOFfc9u30zm9N7XTz22++0b0lo'
        b'C3vkEtEbObqZSwNitKV2uUh6Xdz2O+50NKTgcC5Cn2ZHs20Of3qb4wA2miPYEKH4EEEsjpUrjHZ4ZtgMb2Ju/ANNE3gmHmS0bM1P4IURu2eoGSEc78tkUIwl84wAFiuf'
        b'WDJbHt/EnhmjwVzmJ7OpB2yHZAFHwiJgFvLXMN9hNWCkBv6/xXynTMJ++phtxUIuuUyrVItLSyoqSEw7bLXLxPhDNaXCVVRSYRHqjo42oFDQ4WtKxJXK2kGF0hahYcXF'
        b'05dpZZVlqJUWVVSVLpVImbCEBps7nUZZpqvAhm91VTpxbUklsTdTqGpUisF2aRZEqCpJxjIC78fg2ig1NNgNHVJHjLHcxSqFZrDV2qCEpOoSdckyMUYlTBLLiO0b4nKN'
        b'Cof+Q+/BdnAl4lKdRlu1jC7W+GkyRXGxBEM+D2kuiOrHUB/4VFUprhkrHY2qIgVVYy2uTO3iEq2RWpNFotUSmW8j8QiJeTBt94cKwNEJLarIABtUrq7SVZOQJFZLRJ+u'
        b'VZXqKkrUtGWjplpZagRb1IjDMLhaJKoC9FqCpltXjS6V2lKphDTCEJaNuEK1SkO7MO1OLMIrEc06VJGofMx1dYbWV1QR0KJqHMnSWpkWDTC4Tb9nP9ue3l9EavAReAq7'
        b'e4MDxcb9xVt29P4iNjFBCmhj8iAXX9q/t8EW1C9boMNR8MA+sM+L2YERL4YbbDlwbSG8uTwG7vH2y3ANWb4GXsxDasCFqWDPvBSZFpxDCman7UR5pC/Sn9rhoVRwy38l'
        b'OOsSAy5Uk/XxDeWykevZYhYa2TK/y+dTxOHYvQwex6uWqfBWTn4Y9r/DHuXYe9+GClzChedyg8nDniu4tjtYLtid2PHOhHmU6srf+lmaw+jOR/XRtCFdYhPLVRFbuuVk'
        b'zKmYC2XrO5d65bUs9fzYc8s/176cE/OZh2xPJ3xxifqsuvjsmUWlxbN/blsyNrZmtMdS7WXF8tKz8wQaV2eP2me/nfkFL/5KxtZGDIcxoizXfuk1B73u85D11T2XAm61'
        b'r7/U0rgzgOcZ/tWhzadi3A9/4r51TmDLNyc6Z301OiY47seaB6nhXuPmUfm7/HIl9yQO9MLMJbgLaanmCzOejg5T2HAfuBFPq343wE540bA4kwmOJyPd/9rzJNwSZxaC'
        b'XVbUWngWZRnapGAjbCbrAzPg+hkavG8VFWZYtx8BmzmJoAl0wnPgDK2Y3srLjDB6SeJ1nBHgdg34AO4iWr0DUsi2YEdQcBYeJM6g2BE0WUKrpvsWwbvEE5S4gcIG0JwO'
        b'Oin63tF3QiPQi6/ONK52wKvgNI0ccko0Ezv1ojo5PnCN6bLiOeZVeN11/GBHUvgB2EzUc1/QRrIVZbwzyLGR0cwngTa4zjvxe83gTAqXHQbrIN16gDmaMZ0oWTicAFay'
        b'FoZYV7J6Gb8uJF33CMMfCsN/5xfaT7EkU1i9KelYnP2Kw5LIsR+Zfy72I/PKZT0V+SPhEJWGRMmDqw1uegld/gnd/mNbuEiCb53axj0o62AfkCOZtK2o2ztB75bQGxR6'
        b'bEJHPO3IReDBHiLZZ3mXS9gvGUhHC0vJ8FfJNIMtJXmcQXZ5xoo4bm4bOTWExfJ8Y9tIVp8NmiOL0CRpHS2PyA8sIwQPDcDDMQLw8H4wAJ56JD/8nWtFfshXVjLxtizD'
        b'/uo0tDyhJCM6mn7SUmRT881C+Q41CSsXqUo1RaUVKlRKEjGmN4CBl+FAPKWLpSSHNA0fp5JsQ0UINiuVqcUk4g0QaXQHwAH4NEpCZpVagRPQ9GZ1+mEiHg9JgzS9MLuY'
        b'xIbQVVdUlSgMX2+oEKuF4lBVxlgPeGZknH00OpWWjjtsJMr6pPi9VE2dWlAcOdxHC4f9qGz6cB9Nnj132G9NTR3+oynDfXR22ujhPxpXLB5CdHyNh+OHcMiQlRFJihHk'
        b'lIpIcTjD/uEWXh2WbifEqtu65DWUM0m6uoTEsjTx8Jv4jczCsjo9KtTESWMsegvxd6EjmtHdCb2wRlUyvJpKKSi0QkISDSOuoccYmg66u6kU3yNeDjZfc5cTMSwx2AYb'
        b'aK0oHFUc2RPMpmg7r0NIZDuoccDWXG3zIinQ6ptG9qUzZyIJ4kpMTAwPG0HtYssoeEQKN5F96TJ4aXmEXIrEHXgMiQT7WFngbAUDWMSGFyLkmWx0qx6eButZ42AzvEnv'
        b'3x8AG/Ii5HjpGOwGp0EDawLYCjZLuPTdpoJFxOoBXuZRY+BxjjdrIjhbSe/u350dj+51auF1dNECD7PhXlYA2Au3kG8IGp2iGa1mUyxwzbWKAtfBFnCT0FkE7oRq4DVn'
        b'NY/SgtNseIoVPn4U2ah3AXcWYAOuq1jwwRZch2pp84Ot8PAkDRapKdicjDFutiLqJWx6e3sPyn/YSKTPakLjjYmExrAJSHA20AibwW2axlawnhTsIccyOyFFB68TUuBN'
        b'ASG/3JlLk18MOgn5d+ERCeNcsBnezDK+EJ6Jx290CSIvhB1scMdUK/tBG3kj3DCPfPsscKnOocZOw6XGwtscO1Y0KvgIbVWwYeoIB4HaGZ2dhWs5kazJBYBu1zWrM/He'
        b'vYMTi5oD9nAcWZNnoK/HVjzgfdAGzmZh4T6fuMdg6yAk7VPwGNi1GqkSW2E9uA32gEMF6GIPvA1PIKn5ENwDbo9EhO8DnXnJjrNhyzxiPrdEl58Pm/EJuD2JQtpOEfmi'
        b'CNgZDXfDK6AVu+FszacoDmhkJcODfqpvJv6TrcFogVM/+ergxxOQxpBANIYSpDGciMmMfTRaezmh85foXLk0JkZ7SXfZ3b3msuJS8YxfHFr26f3pe/YAdv15SYXkz5rZ'
        b'l3tjP2MtuL9OcvPAiJSe0b+MkRdHZmY9/eg/fnJ2v03++5tit9m9d9SuY5N/0z+m39zn9ceVyZFlMZ/FXNy0KSWG88m9tGxXz6/d1k6Qx0T73fpV/g2kpHDX/d6+VBP7'
        b'ifLBuNVHgGCM6ETRnsh/TSj+V/m6lz/+6cNfOGjv+E2Xs/Od/hyuYp+6rPjpLmW0/+dfPFP86Q+b/2tWcNbkwM/3omycnotbit5tTJq/g/rGbcLB2DSXW1FTvNq9xYn7'
        b'BWWTxix0DSrnUzLdrKPnKYkb2RQNAx+4GPZpYX082aplw/c0QnI3Cx4G6wy7tPAaOM/g48wnd0Xg1uIIg8dR63ysWzhGcmyinMnWcoQrPEJrNHDTihpW8mR4nN6GvYUa'
        b'824EjdjiAhq5oJ4FN4B2R1oVOQj3umNwGxraJngUAbcB22EHfXu7PNGgqaBiTjO7zuBkDdFUUsD20gi8eyuL8lWxKVvYxAbrEsAeWsk6kpajcYBXWaibX0XDThPqAONH'
        b'0ibdbMR6TdUJeATYCE/Bzaj/2dQQHQbemoTGGnSPj+59AG9hjt0pcqURctaDJnt8D1s2nQc3YSOFNT07QmrRoul4t1g12RwyhpMKN/IITs9SR7hDQ2yi1LARnEIfXpNA'
        b'tmGRLlgP1mnQwNaAkegugvWI0eH7qOBOsoc2H905jJ7kUawFC8BpNP6uADvoDdaOReCOhpiUshyrwXsUPAyPrKFvbQKnFmpqlqPXBWaBFjRKof52lpSHmvjSFHQLvUwH'
        b'N4N9FNwyeTnRHVFFXAo0KI/HeOb6I1Ie70xFOsVrrGZinQJPMSbXMA2SqVeOsHT2QUlEscIwYFixqhxlVKxiuvxjOkd2Buj947Fi5d08udc/okPb5R/XPO2pq3fLagbM'
        b'pOah/8TekPDOtN5gSWcCUrB8k75ImvhB0A3FPdUHqlvSfg7l7v0fQp/eoFGnx7WP6yi4OO/MvBsh+sgp3UHJLba9/kFHV7WuOrimhYvKZ/Q52xvB3f6T9Z6Te90D2goe'
        b'ukseu3kaTnGQmrqddfrg+C5hvOkRbrd/gt4zAYcB92r1ait76BU55E3lQ6+IwTfdvfbP2TlHH5jU5Z5kCJwzMNOTIZ5qG/XQPaxXFMoASqd2i2L1brFvfzPkoXvooJv/'
        b'6eHfGzf2+vgr4+9zP7SDdo/jJvfz2AHJSK/F4Tb6KfaIFJaZDsqnQT8czXUgNZ8z2O+ATxlwNWk1FAdxtsIxDwwa6H+vpb55F2mgkjfVQA0uN1i6UV/ATu7CAajNfdyi'
        b'XJm8z6FoamFeXpp8qiwtn44lY0Rz7nOoLlFVMvAc6sN4L8HeBEFB7zVgY08CbKI+hA8EyARaoj4TEGi8ok+UbvLJEu//Dzat8Vj2PdvU6ly8EWGB9XscQ6jMooPH9DtR'
        b'Ir+2/E7Ojbj7pV2umQ14F0zo05bQybtR+FFIr4do0OlXNlyRU0PWC0eOIOJb+0mCUtYzCh+/msImYVAkX3NYooiGrKc4uImk120SjoAyhY6A4h342CWq1y0FJXmnshoy'
        b'TXFm4nEYmDEkCgwTOSUNPzeNZR70BcdhcU+h46QwEVdw+BZRIom4woRXwWFgPCc3ZHxj6yyI/0pMeQV0eUa3Jx4fj34aZC+4LEEMhtH2wYekflsqmTWV9S2nliXw/ZYy'
        b'Hb8ix2dqDuXk3hr0SOD3DVskQJ9GOfn347NnSfhGwSNB4HP2eEEKC98J+oqc0ljcxCzn2PwsS0DgGLAPzePe07iq9CQLwd6A2P91PcbfdsMuWCYE7rkcjL5NI28f4jLY'
        b'2/Q5RuC2Q3/xOUbixjjcdLrp3EUxQjFS4UrO3RTuxnMPhRCde5JzL4W3QqTwOeQwl6vkNfDLWArfeqPbDUbsZrClWQoHdHTEKNPo/0jD//N+52zovHboryKU2U/iKPzN'
        b'kKdt2JSSx+BuBxoRtm1NZaP/uHR2GZsp15X5dcG/KlP6SIYG/GuH/tuXcRVB54MtaAjDOOSYiga7BkHDyAa3MltFiBk1dgSLm09Ad0eU8Qlet30DtYI114FAgEj6RuJe'
        b'M5VE9iYA7mVK9cvRFvrZ4Ax0HFCLTC+lSNlLUmmqkjRaBfkdHRMzenQS1hmTVmgUSXiMksbExKL/SBuNk3D6uPLcvJw+boZsWkYftzBv2vQzrD52aho62uFXFuXKs+ec'
        b'4aqxsNLHI2s0fXZ0kHcVOuWVVZSUa97ktbH4tVw1CccuwYdwDh5eZfJ8OubGG5aFV3Uty1LHkwLzU2cmv0xZrNVWJ0VH19bWSjWqFVFYe1ZjeJmoUgbaQlpatSxaoYwe'
        b'QKEU6dgxo6XofRK2qfwzbAIari4nqDJ9dtm5U5Ozi5BS/XIUJnpqioxQiH6nl9Th8S8PbyhptKhQaUw8OqI5Bhd2hqUupGOc4BjpfY75Mvm07LSilOSCqRmvWVSshEPT'
        b'Zfzkl2MHPDhVXaXRpBBt37KM7KryHE05KSkWl8Q2lYQInIDLch5QHy+9h/6ol+5WK0/iYFEKZjf1ZCtlJ6pxYOiBhSSSQuLUU/C9oV8e+zLiDb60z0ahLCvRVWhJ9ZO2'
        b'/D9yTi1/HU9hovCPA2fhAQe4IcnkOQHW61QXO3N4xIf4wecBBh9izq9fUvbH2F4/eX8IH+I+2yJ1lU6L2J6OoGM5nkgNNy3ciVdKKE/fN3QRxeGfX/mGiTwzR9FayTAc'
        b'Rc/Y0CLVQSty1WGDcGXhTWpvqGE6HtkQ3qQs4juKMdIJOnqZvdFT1PEH8xRFjf90vY2VbQYZDaijWqk022woJVVI73rjUf8Vmwv5uurqKjVet6wm8ZSJLKpJGpwxSjyg'
        b'Z4rDUtMkr86Ge/b35kgUh4VrVHgLvWasdEz4axRJDxbisKkZ35+ZGRRw5kjx971n6AFLHCYreKMnYl/xxOuOPbiIgUQPtY/DrEXTi7Y01pFCuUhbpTaGgh3qSTxB048N'
        b'ZJtqtapKrdLW0dGVwsLxtB+OCMITf7j1pf1wLA7gPHhyDsf7OOF4Vg2XSE1WHmOko6UxSUwW68WYDEJiSFamVFPyGJJMFz3Uh9Goc8ynWUGOo+snVEPA44asHrJjmWQJ'
        b'lkU6mXV0NwbsakiaTJBtNGF0fx2IvYbRzYw2QVZMfvAfdE+H9w/x1hrZ0iD2SMoSLWYo9FF1A+HxsEXMEIhbeFsElVNbombMl8xCCZPaEecrlfhbdRVKcYkWCXKLdFrr'
        b'ZE1NLkiblps3p2h6Yd703Py0Ihy7PZ9QaTQdIuhfVuyPmEqiByG6fqYny+QG1EdDuxk0eWZDx7qljWmTh2wc0iWY9mDCB4wp4UPaKpEWqqb7qYZU4oBnE8PprzNkUVVa'
        b'hwOjoeuQCEzvC2HrpEpxWmHeEJtVleL8WpV2pVJdQRpO+wri6QFxiL6EOoxMW1JRRx4ceoQLH5pnGcw9ukFMUHyY85kmMcLy0fvGQ3yRlja9Mgu/ZvGsBaDjkKMWKWnQ'
        b'Rh6qHkZO0xjYd0C51tuEaCXmPUWWkiwXL1JWVFWW45K+Z8PLbpAI5iLXEVekC2XwFNyN/YWbORQbHgfH4SZWGDgLztGbVadzIiRgU5Y5msNN0EKbW5EMl32iNQIBAbQ/'
        b'RYcVgcdgPfGxBNey4A2suYOt8Dr6e0UG7oJGLiWA9WzYBG7n0rEWGuLqsoxA27AxsYCiRsJjHLBVDfaQcA/vwhsh+RY+0HHwmrVIHBQG2r5ubzcKthhQqW5Iwwz7NRxH'
        b'dNbKmjzOhuzkuMOLYCe9ycOJBFvnsybz4Dri1x4m9DQLvWIKeWJ0Xq4WCPJw8JWwKHlhWBjcArdGwy2ROGIGHUgER6y4GsqC+11ZufBSOtnCcoP7y3D4Dy41UkpH/8jT'
        b'kT1H2xqb6gMsTxKs5a9VBRTBYBOA6yrzcCAZ0swc2Aje80PfG50HG7JnZHDyQCOGNoAfgJN1IRS4x3WALfBAsuqPc7JZmk9QIftK1cuac+xBjMvG8iV98Y3uqTuP2Sz/'
        b'i+xzrnB5z76Uk7++IXpw8kbYkbb98Sef2+x6HBz3xSpYOumZA29r2tkE1k/HXo8OSovd6LZT/Juv1gU2xzseWmm3LThz8Uq/Dz63rT3FufPl+qdftL2Q7dj0619Qj9M2'
        b'J+xrPrxFEbjzi65jvw+e+89LTpt/6ir7U+/NsQ7XxS86E8tzBP9Iz9o1a5LqpdRv/M+uB3/y6e4Z2+aNPv/nX3/ym+OsO5O+uZ5445NRWRcidLL3PBp3Jy7luTf8yv/4'
        b'0eirQfclArKWLwmFnXlgb4Q0ija4OsGOqbMja/ng8oRldJwlHCoqEtyUYXcdG8opjxMLO0AT2bKoBdfLTXZg78B6enPlOmgjnkaLwLUYVMYpuN4Sth/uW7mQRCyA7RM8'
        b'yZYPOJ2FnQzLl5DnYDPcp2Z4GGwE542+dTJwhob63wPvCkwRHu6C02bGYJ1+NAT+HnAQnjNC8JdUGHdU3CEDcb8lMGEwlD+fglddaCj/JAa9vg60rDZGXQBtoN4YeQHu'
        b'kdPeSBcxwIOZeyIXHGaBg1XgIr1Fg87q0atwr30f3c8B++BZVjrYDM+Qra+ZY8rRkJHNouDNd9mLWLHe8KDE8a0WYfHKnbkpuBmEtVVtyxwtnk1vqTxXRFAjPPQeYR3B'
        b'XS7jbgjvB3/E108v7E1MvV/20eLnHNaI2dh1xdvvqKhV1Mzv9fJvG6P3kjTz8MaIFTciV6HJjUEY2FbRJRz9a7+w3nET7gluCR7U9HNY4bnEwG06MXCbznoiFOlRGcJo'
        b'7DVDscKJLdxXKNs0ki2DZMtgPRWJe8OiWriHBL2RsS3cR56Sp66eLek9PlFdPlEdykc+8U/wHozP/vk757cFtsXq3UM63C56nfHqch99Y+y98TfHm4Pe93OoCdNYevfR'
        b'ZoqswMwJ4JVa5NCGcjj0pYWJ/ms2SA5WfzHMBrHHnxWO0cRfvCmmOMHNbOPHUJ0O44eHKc5AZfOKsEowFK6vte8woPtuQ9+hxkaQNLqv9DX0joEY33gFMj8jOa+Pm5qW'
        b'UtDHnZqXliqxseaaof7GEC6zz6Z0cYm6XKmx0O+dDV/dgA57bYdEi8JYUTYNTki/x5q+M0GFcmkYUeb878GEetphTdNPViiQ+Gluym6QdKys8xpl5MELBmXiJCzBJxUb'
        b'cRKLrVg/RTISpxH9F9vSD3Y9QG83J6gUSbSLkOZQpdOa9Agtrngto2W9lv7KaB40X7yGCluyzPSsOTl0urhEIy6rqCrBq0hIB1GhlErdskVK6+I+fl2lccUEC48GM8tk'
        b'Upo1iymaCgu9zpwMg1anVa6glRZcKzQC8jLaD2AIw36UR6XAErepKtRK4tmBKKO/QRyGCFWTTyMSdWBeulQqDZQMoQvQBmTESaUEc5NGq9aVanWodFPJUnG6wf7S7L7V'
        b'8ozPEM7UVVcoDSzAGLci5QN/LNKPlqGqtFpGWF5aehreIE0rkhfmpKTlRYoNqmNB2uwCyZD1rSReKbiylZWKKG1VFPoxq5+wqmraS+cVJaywpo2jVKUae/eYa+OvLA7/'
        b'MSrruIZfpUsbEakZrrZa2uKqCgUaNa2q3WJUK2l58uTswSq2dUeW11S7FTplEXZqoasCXYnxFWFYhm9wv9AqyxFfIAYpLpZXVeKR4hUePiu0prfjwnApSMvCXjV4gDCy'
        b'bpm6ahmqKkXJEK44FTp6dbNcVaOsNHA+6poKbAgZVlpVqVGh6sIloYpTkVRUy0MSRhdjviYkMf9MmtSqRUv+H3vvARfVsT78n92lLyC99750RJQq0ntvAjakK0gXe0Vp'
        b'iqioYANUBJQqKqBSnEliiUaWVUGjiaZoqlExmu47M2fBxZLyu/dzf+///V9z77I755w5U57pz/N9khPz6f7g7avQiBD76dY2RLhR5ZD84DSY83088PNLNmlw20Sd4lvj'
        b'SSnIJW2NtHZiXfTupTg9iDnqRPCXvnk6hWnpaDWNjZWWo7dkZKDGl5BLL4Dpm9/et+TlZSWmk0qYWIhn52ahhkzU01HR8isbNQRa7N9emK96OUudYLQkT8jOzkhPJCra'
        b'eE+EtCdB46u3tx0Pus9I4HeK6O14fNcxQZ8ccx08yuuYhESFc3Bl4NFex8TdK/gd7dBUwJpsOsf0b9i4Tei7uk109a95xf4zPfq/2A/Qpo9k4AYTYXqxT/gZeL0fBQ6R'
        b'WSVZrN5IEKEkM7YLocVq4OUAI5pgmOHjiLcAwGa4he9ZVAic8qbX3wPi8BBfWfSoCE0wbEqjVUXb4Ml0DD4UwrYy8AghHyaB7ZFk7yDDG1YLbh2AUiHYAo7w9w7g6VBi'
        b'xQVLMmfBcr67SjF0eySGeJWDdmwzFGBhGu1r7h8lwE17w3UnXqm3e8mCcnFYSqdqKzgHzvC3DGBpDoVVPMF6uYJonJsdoDr5zfe97V2hYRNve+WyOMxkAvLGEaEcrRVg'
        b'B2hVpPdRNoEKsI9sR4AOsI/COqf+oKhgGbqWDI/D2gDiFNPCPwRvStDxCMMdcJOEoSpolni1FTALrof70YVDcijKI5GgLikMlLqvAXvBBnAc/XcY/d28eBmoBEfdF84D'
        b'Ze65SnLpYWGL5uUazgE1i9NkKFjhogH2L4aHSQ0aOsMeNjydLclMY1NMeI5hhV59iMYYboAtQe9MFyxVBaWzwPaFsA/WgE2TErUJHoJV+DtWjF0wBRbrUKAlTFYFtmQR'
        b'iWJEw3qimesFuymsmQuLwI6CBFw/GxPdJjZnZEE1J5oPuswuKIiEldlSU+COSH7BC2zd4B0bXD/jMLxxKCRYD5rEiAqwNCxRgq0a0gWuOGfFscveDiCNi+ODJPFTkZPq'
        b'E54CxVI+cC/cVIBdK2laiAbw3VabeRCF4K2gJZQIDYo1gHD5kCTtFM7zB2VySMLL4M5wUA7KGHAgR8oHnJEuCETRzAAnYUOAoP9rHI3vq/V/9KTYwCY2qFIwhEcVQSNo'
        b'UFJkRTpRoCZIFjSANmcC2wR9SNLaXyOHgiMROFdMWA+r0KtOOqO62QCLUMkSBWWwYyEFi8Mlw0FfOOH6RYMTCwT2yAL9OP4WlgKOXF/RSPnpkprcWESwVmYHPFogB7bD'
        b'o7CRbl6ttnHjtDUUZzDodfwXXhDurwDO5cA+2m60fyY8QrbfAsGxce+79bCU6MXRm5VlsGHRuHtiL3hqsofitbCfwwyOTN9kv1Mo7wZaSCb1ym6N/DAYWsucPJC678jX'
        b'+4Z3S8iIVt67slX73kXRSF8l3+ZIt7hjEg6iPb1yPu/5fGF8q6fAt+PXi4bff/Tddy19+354LCr73r47D5f4Vy5LsSjpkUn38V1tsHjXfc/39QO2hgWWXgmQ+eLWXueY'
        b'ncVNXB/xB59IV62b96O1tmTjss/Bvf42p0VTPy81z84INbNpDNrc7NLrabJUtb7ip+RQZZnyBO8TL0vFHzGjOHfP7bGXtrkdHWQy+yQYYr6/OuXqijFrn+NDsXOvrijm'
        b'7Vy9auG9aXaXDz5eIVE2z41r9cWmLuV55Y4fH2gHXy8rX6FzPeSP5hGJbxhSxt2DvWb3fuxrU3d/sSE2J6w79uLYoba9Mblc06iwS08rwn4TWxbyvuuS6gYfT5/Dq4wW'
        b'DX5zvKXauuuLprm5R7gNN+OX/np0XkikxTcFfzy7J7I7NFP3qM3nfVrZ7neHl0vbaf4ko/19mINpQcPHaQdyC9mF80/Na96bYnbI1s57W3J0xmOdzsai5/Ir11jmzLv/'
        b'ffvKZSsfn1r8xDHrceWt5i5v+WLRK6rduc/vF4guv7u4+svsh0pS9xZ/fP/uV/7JF4OqFt0z+jTm95Yh3SundgYN25tYF9h236xLAUe2rVZN/Ih1zPklM+FQ9bXoIo4S'
        b'2RxjKsKzAQKuH6e4wr5oVoYzbKetXbcoexBbVzFQPWmTENaCJrJLmQVOwON4nxDJUh2hkWmhZ3HU9rBSG7ebDQWvwGFM2JYNNtPeWvvgAdTq6G25+eAAHxw2X5zsyoUs'
        b'VJAyesMPbA4rQjmC3tQ7t1aEYMXiwLpXrmZhw2oFku5geA7W0JuQ4LjsJINUZWlac704f7YZqIqYZCm7FJaJEkXxTJS247RauxCborXaF8IOOuG1aMjciD11+KEe8bit'
        b'ECWSwdSDRWlEFdwFbFIhCLbMmQTChka4VtpGtkgCbHvN62gdPIY3PVfB4mcYJwQHQBm2D35j2xPsA4f5Lkxx10iSyHTRxKCo3PhXqCiWoootueYAujAX1Rw0CzHhACVk'
        b'zgBnmGAvKZoA1GufIDumsBGWTvJVK59DM9nawZHFZNsZon6Rv/UMd9HsNCMGaA0IxBvO/aFWr1NErUGPiFWGLK3df1LSn4gOGotC0NxDGu739mS5oM6UlCILbof9tENa'
        b'FjzBN0MGZyFNfgPr7NHYXW4VZMGxckApcGHqWMJNHOX/DZ1ZXKDjM8t3kzv03rLB9jaiE1YFxv4XUiywu0+jJqPryja3NPXrvJs824OagzAUyfve2zdpdQwaJeslR3Rs'
        b'uDo2hNikY1cpNaprIuDnslL6noHJiME0rsG0EQN7roF9jybPwGdIRndUXnWP63bXJruhqR5Dpp5cec97esbbA0YV9eqShhVNm9YMKgxbed3TM9oe8FiEMrDpCObqu1cG'
        b'YGCRVY0VT81sWM23Q6R7SueUQTuutW+l6GOdcU+ZnYV31AweUwyj6Xi/mN3LfsJiGHkSt5pexK2mF4MG5Thsd6gTGZY3uqWux981diObxe5ks9idcV9dn+/W8rBzjdg9'
        b'AU32V09EkydiyBMxjHvKWug6Hw41jrsSfE5Zi/+cF3nOmzznzcBwHqe9TjRTiqcVNqQSNr4FHjVk7jJkMJMrPxMlWkVjz+rtq4eUrTtiaP7RsF3QPR2LDoVhHbsegxHH'
        b'gGHHAG5oPAEiRfH0ooc0orFDU/RMkzBX2aLDbFBhxC2c6xY+PDWcvIzPyrqvrFW/smP1RenhGdGjAmkJ5GkFDakEjWroY8ZPh2i35AlJfgbcSQY8SAY8GPc0dGoDawJH'
        b'NKyHNaw7IrvndM4ZsfMetvN+692PJXDxO213GpHncOU5TYbX5a1HtY22+97T1q30/UJRbUjdoimfq+g5GHMxZSh67tD8xFGv0KHwuKE5SWMshlIKo5KJSkPbqJJZxcYF'
        b'NRHVkKnTdXnnW7omSHr9mv16lIbNXW9p69VNo2uRp21d6V7lS0hL2HdrkyRXftqoiS32f2o4yi/xQC5KjYFZpWdV0D1l1Upxgc19uXcSfl5tI+cmvWlz8HeaNT7jehPM'
        b'889adKWwoG/RueYMRjih8IQznpLPf3IOgNepDSJ21Cm2GzX5IEBkfAWbhj52iRB9RloTWbRErIRKEZnQbBT+t2k2pnGYvyx4Y2EdnrwkKTk37692uMl2Gn8JjzdwEvJ0'
        b'ZgcF/sU6XYt6fZ3OCaYn8dWgUSfgFS4j7HWWeXmMAM5aHK0JaXgG3A9apRT1UugpbwWsBCfMfGPl6Fnv5CkvqBejV/eZcJ3bYvromp44S4OzBfhU012WgYPzLdFEwhJN'
        b'E+y1rfwxl8JgnvAMZbCHpjD3gT54CE21y3H8KAYtClTCathApuWWaHTfLYZGVAENBIZJZDTZazi/lgDHKeulg963spdQZDka6SwJj8wgrgtQ/cCDFBjgwD3khB1syEbL'
        b'4PW+cCeLGKyiNWMZyUGAGmxgwvVs8VyMAW/GKgpdKvT2RIs7HIida8YxxczJ5Qy4HuyAJ+idkMPLVAPwZClYGLOfKRElpmRsOm0detoe1EbArZI2eOviFAW2hcBK8pC7'
        b'jyHYKjyJOA4GjFbIznGaY0+N6xowXNfk0WVT7APLLAgMmrZQpe1ht8fQFr0lcB08GwUHJoxbaVtaeIbkVguWuy+HpXiPRIhCLzPloKUOvmAlL7vE4JXOA8MV9kQW8A+Y'
        b'd+vLws4IsBVWRcGtcFdUEIMSC2HAk+4ypMTNPLZRGgxKxVq0VVbRU4Le8vGU1qc8cTW4OcS5ZjHoQP1c2h+Atd1nJiskfOnA/lxJCtWqiXVKvaqw8UI6cGuKEmVOUTLW'
        b'0uyZe6fI0U5A0Gp0v944wB0trsYZ7oTfzkHVRqZcx+BuBXggm9594O89dMBusl9iQg62181FF3OkWBRLgeEEu0EteeWWhcSKW8Y6Wsd/1NQdeyijHW0EpwaA7lfVAIvh'
        b'TlJksRy4Cw7E0LbAeLshB3QTG2g9H3/YIQW70DOiFMuI4RK6isMgkaGZWTmaqJ7NC8YrBCabobMMttIyVaMD9oDecPZSeHoKE0dnD47q04JzwCaTnYvNC9H3FuwGogOe'
        b'InkVQ+J/xAc10y5JeFoUic5OdIM4HKBdaTjDSjRBXY/JZGFUGNy0iN6qakkBtWwTUzPYGQhOJ6Cq9GfG+YMDRLEHbohBotJl5Q+7Axmm4BAlDDYy4G6wBZSnuzdkM/M8'
        b'UTd99WV6X+yvizWiFPoLn/d17Vv9RV+n0W2j02Ub0vYpybJPR3qm1W8w8a7c4rnE4LOjHzTZmgjv8r1esruspE7n0PENCrKKiVe365lKHCq596neTxtTH32E/v38yJF3'
        b'8zsr27xHP/eP3b1wZ+VH3/X+tjyhtLW0tblC4ZfuJbXij4qyk66tiF4SxAnoqL2csy/xx9CDvusvFzVN6zyhezn3y6MZ1/wirjBnPVyR5p5yJLu17PHUYC3bDDGrAAuv'
        b'T9y/Eqnvym/96qfkRx5XHBrvfZl+0ufAwqYzs64lFjVle34VkZ/8q2NAj5fHtUV1qQ1atzmBPr3+Sy6ZtX+fV37sfFiSprDjZytKDn/4za7uoxWlmiu/lrn7cVvrB1fT'
        b'2j97cPeybdSZD2trJPVvL3J0e+9YfPZxtfjsDxeJmH7Kau0aXHTcQSZic3XfuRscn9sPlztdvcLsHl7RcST7u6DeR/PNdItbfspMHE51og5FpR95KhsU9lJ93UuxrcHX'
        b'XX1kf1fkrLpzJidoyWXNW0p7f/T+RM2zNf1ZkM6izIKwFzlutnckfYTvf3P8V9jZLJrIUxmaaZ6ivDL0wjnhJstjG0t3XdfzX7R+R0qI3w+LBitERh1ak2ya5VKnfaS9'
        b'ZSzh7kOo4ZY58q1Kd8NXFvdKL3yf5FHxMaPrq4rifeKff8o4l1FQFX/jwJ0HW97/XP7llnPmIsP5Gmmmx+Tv+CfmKpfkzej2eqCp++j+9N+1rn5j4yj+7CfbZZF7fwrW'
        b'7X++5urSvd2GqTlFtp98s+1GtuIL6bCc+QsV122KDHwvMj/2h5Arv1BJBzK8Rs6HL5xuvXZ1wS9BzkkaDcU931cvy0y6FSf74c1hoQMh+ke+THj0ZYXkRx98e/N55G7r'
        b'T3yNLy5yjB7dk7zO6phPXcGmeKnb2l9Oh8HTDj9MVZzqOr2o4dONF+pvGq+7ce2WUsG5gpLlcsd8R11TL9cs6Zw33D92KGfzjJ7W1f7tt5e3Pv36vRVUhOf5nKvPv9u1'
        b'IH6fodG27s/tPj856iAzX7h3wcM9dzU3Lju40bH4QNPyW65uLfeKDtSnuhZfEr4WU5An78g4OONFW+KUmSvtRo7ut+1+NuPuyO+332893pVyrutCzPW2xHbR9KsrpNp7'
        b'b2Z/VbZ6w5zur29K1jxkD/0id3IJY/HcvoybIdUxOg+ilkhNrb45uGTlrF8+cbrotIz36brfKNmP/IzAp89SI39Qj8r73qN1/r6nV+ZetbRyTT23wqOoQCttit5HG8xz'
        b'Z+Sd/UTy5x8el+rWfCmb+Hztl3Y/PrynkTRzSkvBj0rdx7rlV24Y+2Zn7yd+7xeeu/iz6HPnsifS3ZvNC360zJJK/cllUNQ26gr07mz75OG8r/brCGe23mM1UQcuc+98'
        b'uuyRYYyMw4sHQQ/nrZje0TZT6NxRG2/u5kiWyHuGMSyR/qobs3KV5kipPOYcX/+FefoxButbw2jWpYfb0MXvHkWytBmryhYN1rm42T3WNnuZuOQw90zUtQeNoXOfvpDJ'
        b'ZkXVugnfvfs8r4naP7da9DsLZeq025NPrj/pX/ekv+hme92P+46UHVhcfUbkt+lrMr/4dqnH8d+Uln0v/OPHhbMCNv5s5/FJ+eCA6osp/X5KN1549K0cuXyv68j+tb/W'
        b'tox2dm9L2hQf7bquX6Hkd+PBeZGueWbJFgPZi5M+WPtla2TWlgsDweoD9x+I9l/a239HaeG8AbffXz5Utoh0iLh7/envax9mOr78nftywOOHbcoNCa4Sf3RSkukFP/24'
        b'p8tqx8g10djn7nsvxzwE8h9cfjllyWGTlJeuva0vNRviCxtKp30hdfW9T48s+0Nt5oXgKV+3j/h1X19bfGfHL+yvpNsav5bc8YvGCtPcmLiflQPLgrkPRjkZBLS91E6P'
        b'kfiG89Fx16P18AhNfm+HtenjCmjaYNP4DssRQG8tgT358LSZJdgyla+8NbENAXZr06pm28DOXHh4SQDcGjBxwxRrVuosUEUTrus4BB1y+LVtFWyZvxUee2aI79mfB7bD'
        b'fuO3KZPROyqpYIBOULkzOIZvy8VKoFvQTb6BwcKUUqCQFFOPbKvMtnIx4/PmYctqGjm/ChSTpwthNTgqhd1UTUxUGZQUHGDNMoMHnhnjlByHxfJ5lujVFrm60sEccQ7G'
        b'a2AFPljKoqbB4yIRaLpYR96kxICVfAw4Ax6TpkTmM03noWt4oPbH5AJwfH5AoKkIxZzLmLE4k2zbyKAJZh2qEis0M2aAWoyr38Y0dGfR+2Wb8XRinMldBbfymdyLVpFn'
        b'PYzBOjYssYCdcEuAkR6LEoUnmSG+U2mNvoNa4Kyq5sR12BWIsgZK0CwFnoQn6A2bOrkEWAoOC7otERejX30CtsEy+mkLP9jpgl4twYyBdS70vlil39xQsCvP1A9WZBNU'
        b'xLZgUUoGdLDyp8MKGtuwC26aE0CgcFT0NEoY9jFZEXA/iV1KaS3sCoAnQqLAPjZoNhGhxGE3EzTMWUOkUBf0hOZhfD8oA3XiqGKEKQlYwYTlBvq0jJ2Jj18FenDqxDlo'
        b'irIlgIWydo4lvxicoLF3WxfOhesK+YgLeicwH+4mda4WBbr9c3AlmllyJExMQbMQJafCQnPZQ7CH3iss1geH2ZYB8DQHlufD9Sjr0sz4FFBO9k4tYTk4lhe8GOxg0JOk'
        b'JtAWQtMaauBZF7DVFHahPONCN8N5EKZklVigxhuJNqmXIgm4JyDYHJRaicD1Ez5o1MEGIXDUNpdUrJEc3Gi3Js/SD7RLojsoSlqE5QrOGtAR9KA5J9vfIjAHtBWCVl8k'
        b'mnkcBqUaKeSDJlSVRNriGGBLHge2LMdJ7KdA7zx3krOFHBl4MDpg3N2RMGp2VSznFHCaXHU1VgrLRGmezM4Pg40k33rwdOxcWJnnZ8pBk0ZQxQBbcxTp0m6AzWp4k9MK'
        b'rhemGGwKnIP1oJFUpfpMKXIMg1YJZwX2k+FGJII4Vn24U5xKmUTVd5Ona+FUWDzdmtQcXu2VwrZFRIIiwsEA2wTlHZwCLTmBKEkScC8TnJ1F7zTPBGWwCmclyALJeyuD'
        b'ErdhoiXpHlhF4l4O12WxLTmmqJLK4WFd1MulM9PBVnCYVi7dDfuilAPMUM1Y+tFOd6aArayFsJKf33Nq0ujdOcEMcCAHzVsbGbBWErVz8mw13AlOsTkQu38qF/aNQYJf'
        b'zYCnYE8+eXMsRP2eGmjkb/TSu7xo0XuI3sTt85CB7VpI9nF+WbCUgRrnFniYZp1ULQQNAfigCezyt7AUodj+TNiYQHe7oNgJtucFctDicDFxHIGajCQTrUBawVl66/wE'
        b'bLS1AFW4/nIDMfhJyoolNh9uIdUQPAOeRT0ErLDFEtNDgbZEcJxkdm60KzjkgFY/uVjRlgn6Geqou60gcWagWu0Dp90mexERReklWKpz8KjPzPhXC5CZYAdds3vi9fx0'
        b'Jx1gRLMyXEAtfXWLGTyLU1kAK3MDrRiUxCwmaAa9srQP7Ro0Wm3Kg+VT4RlUMqQVo/zizk0B9chwj/MsMty5gGbXPFjBkQBtoDnJHJ7GvfsJdJeqjJApbIcD5F0W4XAz'
        b'ioO+FI5GKuFoBiyzBgfp7rEXUz6LYekr7yyxsIWuiw64MwUfUS6FXULy4AglJMuYl4VqET/n6wUGQD84mkd8lDHAQTQoRrNIaXoVglpb1EFYwVIT1IrgQXQV7E2iM96G'
        b'SqwDJdrEv9B0ITzIpETBTqaD0TTSbdk5g4ZAcArr3IfgXZRSIj5TmKwkuNWO1KEyNR87ixKRGPdqxZoS7E+eVQT1Xnl47HJY7Y+6W36PqQKOC9l4JdHjfgPcaUL39oGM'
        b'SHgWSfU+JNVoOtBN97jHsuEBurTjYT2HlKQEPIXEYco8uqyKwO41aPVfTtxVMKMZFvAE6lYIRPQUmhNsyYNbQQ07QByWFqJKx6+h5OFOFqjVBKdIkS4C+8F6UAsqBXxl'
        b'oRUzLYVo4bkrnz5aYIJtUuRsAbYVknybo5TtcYU72QVS4qhMdRluYP0s0g0uT4UbdbPy4BbMQFJg6IMSBj167YQ7YadfLJ0hvxxygxRsZhnCIniaPkNrBuvWTPgQA+1g'
        b'y7gTMdCvQ5x6gCOaJoSNagXLgmTdzTl+QahP53vEsXcWAYdQuuhDNVhpOG2h0aRzFXyocgQ2PMNOvAy1zIhXm9IQeCZLwJHXa168omCbmFUhXEey4IASDTqx5gO+0yKH'
        b'9MqyqImCwwWoIeG3LlOIm4b19UNeOQGSjmAFecHtpLzX6IIBJBScGLCRbmZeTHBsFoqeyOImB3gIdYjb8R24u9/NABVYpknMpqiHPAarYC2+yu9M7Fjiq5D849mbQxJY'
        b'9xZ3J9jVyRb0H3Z3cogeyMEpY2fQHD2eCfIuWXiaBY5IrSCykwZPgf2wB7a83Q1aOthJxMMHNqJxoBPsZZPhkgW7GaDJj0PPZA4mLWLjbSw8CwL1aJpAiVHMMEl4js7p'
        b'ITNwEtbBM2g88GegR0+iJonHBTLY+qPm2ZEXDPfLcDgS/kFYYFDLUQBFLDSjPCVFpAy0ZINNbI5WIkUx1FDJgXOFdJtZrwL2OoBS9HinFZpokD5dZhELlBnPJq+WRF3Y'
        b'piW44zW3tMS9QQ0a/cA5UEdToc6B0+CQ8mw2bg1MDkML9oIi0rcFgTr9PDQOoMHvDDggPp431KJhpZAj6DCiPb2URkxlW+BMwZ75lIgWUz4CnqUb+wkpd+JENRiVaRM8'
        b'iyUbNeXdsMKRP/8BB5LzrExhhy8H7gB7cUd0juk71YwW5u2gCfbCLotgvHOjiwYL4dUMuEsJNJPEhaHeZQP2j3kWnnvDgw3K3CH+EBCklmfpXwCOwiYO6hPQaMVkgqos'
        b'U1JyrsvgFj9d/jzbb4oJ7umkYC/LAW5IJr2NrKVaTqig+QfDG24pILWBoWQHZYwDLINQj72c4RyPxj8FUti1cO/UpbRVCDYJ8eSPRikLkbTSxLL5YGAcWQZLdDiq/7vY'
        b'H5y4t+jlCTqnEckle/srVN9y6kFfIseX2Wz6+HKVNXEfX7X8jprRkLE/Ty1gSCEAk7DUa9RHVK24qlZD1m48VfdKkVEltT2Lty8eUTLnKpk3RfGUbCtZoyoatewa9oiK'
        b'JVfFcsjKlacyq1J4VEV9WMWvTqiRXc8e0ZnG1ZnWEcXTcUJhg16D4vi6Vp1Bo1m92ZCKBfpFn7MNK/s3JQ9b+vUIjdj7ce39hjj+lUL3tHUqJW9pG9Ut3bcWfVHQqVNo'
        b'1K7X5inYVDLuyyvdUlOv9qwNqAngm6Ek8jSmdthwNex4atMrPUZ19Lf73VNTrzWtMR1VUR1RMeWqmPJUzMdYTHWlSo/HIpSuQZ1bvUil3xdaepXeo/qcRud658MzKwNH'
        b'0YsCuQrWlYF39NG7sVeSw2t4+tMFr4xqGo1oWnA1LZoS2tOa09ALaiVqJOqmNzrVO/FUrPBvsRqxOsV9U/BXVEZ1no3+9f7DBg4d04cNPHtieCpeoxra1aLDKu51bo1+'
        b'9X5NSR1zuJZuPAN3frgnPzylYxXX0oNn4HlPVXNYdVZddJ0a+oPdmsziWs0ao6RV1QYTLiw6v2hU16A6ZljTmba86UjhcpyfUkxNrUFdDLce1TFoFK8Xb4rm6tgO68zs'
        b'ERnW8R00QqXhwdBChaGlN6xpXxfZGFsf22HENbQnT/YkDKT1po3q6DYK1QsJXBw29OiJHjYMGlzK0wlGUbhqPZZBMdTG1sQ2GXE1rYc1QjoSuhd3LkavNjhvMLgUmvOm'
        b'h6AaqfYZ1pjfJDRiYs81sUdfe8IG4nrjLjKuCV0Suhg5EjSXGzSX5zuP5zJ/TF3ah6H2WItSVauVqpGqW3pobYfiU4phHMAYT080dm00YujCNXTpWcQz9OPp+D9lMY09'
        b'Gfe0DbHDmxHtGVztGT0SPG2PMWGWqtpjMRyZSI3IqIZmrWeNJ5ImjXqNEd2pXN2pPA3b0YmzWK6G9RglqqnVEdYd2xk7qmM0rJPcNK3dudl5xGwm12wm+jloc8H+vP1F'
        b'z2uBlwJHAudzA+cPLUgcSkgcCkzieSTfw4+kjT8yi2s2C/0cDLsQcz7mYuS1OZfmjAQt5AYtHEpMGUpKGQpK5Xmlkbf4N9m0z2ie0TGt27nTecTWk2vrORgxuHDI1o9n'
        b'5o+zLVIvUpePBXLE2Ilr7MTTcR41MK2TGNZJGQqLGgmbyw2bOxKWPByWzLNK4YYlX1ToYHSLd4r3GPTkDTJ7ODesPYfCkrlWKWNSotO1xoQlUaGo4UJBsssvlNfeYs81'
        b'tufpOKA61tQiTQbXoHMTo124WbgpqT2zOZNn4jwmLowiksQRideI44hQOaLaHtaJQXdKNUshYUjtTO1JGsjozRiZGcKdGTIUGjYUHjk0M4o3PZpnEoOkTXce456ZFV1i'
        b'TsNmTo9ZlKn1MCeow63bp9Onx3MgsDdwxDmQ6xzImxY0zEkbCgsfCYvmhkUPxcSPxCRyYxJHYlK5ManXw9JG3dwvKJ1X4osVEqh4ntucMVEhTa0xlghKqQylprVXvU7+'
        b'KYWkokm33aTZZFRT95X0anp3pJzIGhQe1gi/6I1kTtMTyZzBoSlNSsM67h3Tu107XZFAmamNLWY4WCmNUQ5aypXez5YyKG3DaiZ2PZRLePGuTQnD6laj0+27F3Uu4mrY'
        b'Vgc3+9yzsKkOHjUyaVxUv6hDtj6z2gd7W8ICntCYWZ+Jy86nxgdXAm6reu1GzUY8HRv8W7Jesim8PaY5ZtjCq0eKp+NNJMa3aWq7fbM9+tLDGBDpFenJHVjWu4xn70uy'
        b'i+pEy2BY07/Js0kM/elRGHHw5zr4D9n5P6XENLVQJYyExnFD40Z1DRtV61WbUri603BV6PXoDpj1mmFfY6gH6lDiGswYNnDv8R42CBxMQbLgpIdlQa9RrF5s1MCw0bPe'
        b'k+5zhqZ7D3G8hzmRF6ddc7jkMMyZNzR7Hs9gPnpElzxiOKJjzdWxRoKB2lZcZ9wg44LQeaHByBGvKK5XFG9WNM8uZmyKWBjqkuQoTR3SCdV50oowdI8kO6DWq4bLQ6Je'
        b'ArWWac3TOoRGrGdxrWfxzNx4Ou7oVY5YUjW1ar1qvMZvnNru0OwwYubFNfO6OBUnbSRgLjdgbp0ET2feGEsClZQapWd0SL1JfkjDYljDp0O326TTpGfqgFOvE2+qz6iG'
        b'1oiGLarCYY2FqJzZvexBtwue5z0vyo34LeD6LeB5JvDsF6K78GhUG1IT8pRCpU+3PX7djRqaHZrfVDBsEI7K1rjXeFAPd8oXrM5b8RzDhw0yhqJjRqLjudHxQ3PmjcxJ'
        b'5c5JHZmzmDtnMS86g5TeGEvIRuuxBM6Xd433eBcY3hhfHz9iaMc1tOPpTB/V0aMHXVvUx6MeDNUjY0C8Vxz1EcMGqU252P/XiJUb18oN/URjRtr5tIu52MfcSEgCNyRh'
        b'aGHyUGLyUEgKzzv1Hn5k0fgjHlwrD/QTNSjRS6JDoeEjofHc0PiR0CRuaNJQctpQStpQaDrPdxF5UVBTTnthc2FHbvfKzpUjM3y4M3wusi7KDc0I5FkFYXHxrvdGFeLU'
        b'7ET3pjwD11ETyzo0NqYPRcWMRC3gRi0YiUobjkrj2aZzo9IuRqIuwK/Trydp0HbQvSf9xjTfoag0rm066sQc9FAnRmoPlYt/jT+/XF57ixPXzIln4DxejpqkHLXpmYMd'
        b'mi8Ma6TQAo/KJOl8EpIQp0tOIwFJ3IAknncyzzEF1yyq1WGNIFSnIp0iHTnd+Z35Pe4DIb0hPJQv6yDccH1rfEd1LJ9SbF29Dpvu6Z3TcTIC6wNHTTjtQs1Co+YW7QHN'
        b'AaPWNt1CnUId0V2SKEEWlkhWLZxGzL245l6DSTzzgGHzuaRdRnNDUdc2hxc6F3WvHFPUlDmmpNddwjNxQW3E0Ag1EUPzYQNvlCapTqmeVJ6195gie5oeTsH0x0qUkXFj'
        b'TH1MUwzP0G5MVQp1foUMP4ax2nPKj6Gq/lQW9VaP3ZiUtv7jFCFKVm1ERocro1Mni2YdvvW+owqKe3y2+6D5Fco3T8Ec//bb7leTuS+Lp2DJ/1WdVDeHq2XDU5g6HpBS'
        b't4qrZctTmIYD/Lf748mPUI1QdWTtnJo5I5qWXE1LMjvSqJWskRxR4XBVOE16TTZoJtih0K3aqTqk4viUklDVGrTrWU6+8EelWzq6aM7Iqec0ebYHNgeOmLtwzV16Fvbk'
        b'DJm7cfXcBxO5en7DetEX04b1EobiElCZGhphCeAXfVME6jTH1au8uHZewxaxFxWuaVzSGPGL5frF8kziRk3Mhk3CO4S6JTsl6f4E/URDdvT56ItecC7q7w2NxkRFsQCJ'
        b'o6IUlVJUGmPLG8o9o+Rl5Z+YULKa1RHXZXRHldX2rNi+YueqIRn9n596CFHWqYyfny5gUtMWMYjB+LCB+jIxy2/M1JdJWdPKUeJvQ3i9ew2A9YsWTJrz5z7CgK93T/g1'
        b'RNBjDhTBe70osGYw5J5Q/5Dxlc8kpFgMpvtaGsUUGRwczBFCH7kJGKAn+RqfNfcXiuDNIjx8vYK8IgiRlWDIaEDrvgmqKk557kZcCoq5Rf+pVRReCs96NzfVEJfmWwiQ'
        b'FFYSW8tAxVhEPRFiSsmgJqkXzhjVtBvVRfMHsyfiwgbYsR8JcxnV1X89zIuEaU+EpaAwi1FdC/o+04n7Xg/zR2FG5B2OKMxqIszutbB4+lkUZonCZjFwoIbFqNLUUSWL'
        b'J+kMOxXpEt/HSxiUtNIYkyGlicGlSo/xt6daGGkaM2QWwp0df0tduzmiV/583jMWQzqQcc/bf9TN6znLScqXMSaMQx4L4e9PVjAoBY1bMsajCp7PhJkK3owSz6diJJ7m'
        b'5E7vpnnnEy/ZccMiuVGx3Li5Q/7zhrzm31LTbLbt1e9NPG9wftmQQ+iopi16VNoONVdvBsqRX8gLlg9TSm2MIp+i5BL++iJcyJ0lZfAjhT9pyio+iVsN2wsJZZWQRszF'
        b'wQkwMG5NwaSc40RgGVwPjk9ST2Pz/44lYdyq/F/gVllJYvzv4gLfJdB3dpIk+S6Fvkvzw6cIfOejV/eLT2BVFd6BVWW9FauqOAlpqjmBVVV6A6uqXEQlqbSo/ruxqi1q'
        b'x0UEUqA1AVWVShFOUv8TnKrGJJxqGkf79hQCIU7PTU7M90xemJ7/i9UbLFWBq/8CSNWe5udN5TBvC3mEhHvdZrlPdc81w52MBf6wYv19oqk9DYCa+o8wqPyH7P856nT8'
        b'dYQ3ZYNRp7n2mADKIlDSXAdMJpUI9woKifQiiFOD1/CiEZ6e4ck5kyl31rlOOMN/51abCQ7oeEJ+UXlXrBNw0Mlp5ohPigPXQ+4fgoTR8cLJxSqSuS/xpXe9wybXB+f6'
        b'f5sLmvY6F5RJva7cKhxM20JuhEWFoEad7wyEeAIxhxW0El9H9Ew2wfzDbtCGfRXsZ2mkZyz8ksrDvZhL7SKCDN2pW86QP2J99uOUxdbWCjbRUxP2TEm5FyhKXfcX7vu9'
        b'mcOgj5ka9ZbDVtA56SA7ERx/Ey9Kcz9VXmtdk7GieEMbY0WT7AUV+0fVdcY5+jI6/xPY6DtfKicqQBpNsP8fkEZzA1j/15JEscMyXZG/SxJNIuWDUYnYNv7fiREdb35/'
        b'gREdb75/eYf938aITu4R3oURfVfH8idcz7d2Em+//x9gPF+noNAG+wlLsK09hpm8A80x8djbvDa9gf6cVM983CcenGiEJxqgTN9N0fgrzuZ4Sv4JaTM95b+Qzf93IJvj'
        b'Le4tjEn87++gLic32r+JunxrA/4v6PLfAroUDo4kJv1wC9xhBLrR3OINrCJmKsIdcGsgbVHu++pAHwzAYjZsgFvV0u+sqWLkBaOI1o6J7btsd6C+iCHiqOrosOLW+mkR'
        b'xqnG8cZ5xgHGK42/XbS0xFz/TKWHRKKxj7P8HLsIJXWWiMkDy/tFnRHV0bbus4O27JLcn04VzpPqndfBESYnrqr56H2voIawSc0aHg8gJ75wA9i9SpBsWIRVGCbQhnvF'
        b'aIWKrmVrJjQ+YRM4OKH1CVqm0+foxalYM4Scz6YvXsiwWeVNVB1gSRY8+opNiLVWwT4DYhYMd6Px6X+wKYBnEW9F+b05lxHk+HnTE6hn2Q6UrFJlVl0+V8auI7UnfzD6'
        b'YtTodLfB6RftMcUvikF2vyuFqqRGlbX2rNyx8jUenor+f46F984cqYgKgvAy7f9HILzcOazX5ut/F4BXxGEE586j3R68FX73RsLHyXfuKOEC5Du9dwy7b9DuRP7cJDFR'
        b'VCCB7EnTTOHJ00w0yRTnTzOZfJSdFEbZpbDJNFN00jRTjEwzRQWmmWICE0rRNWL8aeZroZOA9avfNs38c4yd4BL7/wmG3WQIO3/uxge7ZaLRDhO2/ou1+y/WTue/WLv/'
        b'Yu3+Gmtn/s4ZXgYaN+hl13hF/APK3Z90Gf9Jyt1/mM0mF0yMUR3dMxI9BEnsQktoDrsjnsWdUoW7aEXxCF9YGmIRzUddgUZ42h9uxSY+ATEYWi5GLIYxUkUcnMmArcSU'
        b'ew176ivamsUcwlsb57RvgCVk600f1CUT1DsDVrDhQQq2qsDeAlt0RWE12DihzPsWYvra6YSZzsSawbXi8BzcrlBgRmFOTqMvTZESS8ZPwhJfc9p4HZYEofk5saGYbyzm'
        b'Nn9xAdbkhc3y4FzAa3N2WAKq4WY0p4cVQcQahgpni8Kt4Pj8AjcKWwCVgn5Yzo8uKjTGIjoGU738gwJBc6QvaPUNsrTwC0LRWDGdQBk4wZ4KysMjKC2wXzoDTbn3kLwb'
        b'w80GtAfiLPS2HRToDgIbCmzwtPqgaMRE9Fagl34DBlVlT83FdCoCixOiFoByUbALrFtYYI1zckIZboqIsQDNFH0zv7Yi6YcmMh+fIgoaHMAAEQAFFdjEzpVG5ciSgy2y'
        b'DJfUNbSh9FZYpQS7YHdhHoti+sJGOMAwgx1qxBj6grow9VMemtvOWiC5S92SSndZJiuU9xJdyW+OPLDjWhmwlvkgNfz7l6aHSkpe/PjFjc9nvtfvPvvIJ+Gy25/Xdcs6'
        b'l03h7rkT9nFc4YmO6g+LrD7N6ve7aHhmA7Pson5jZPb8W5WKxbsMhHsXjXy9tO2L5bd37fVuXdRG5UZcG+4+FntSXO0jzpNOp0OPvugQtjW8Nn3Xo7Y91NGrZ0J2y3tc'
        b'Uqj+PGDvC4PcwES/6k1zH+75yu/Gg5ajGtNq/gh4ECp39WxgXOTgJ9ufPZr7vPvXrQ0PH2eOXBX9dKFegeYnqUsafca4PzSmrm28srbhvZeBNf7XpLe6D12S7or/XrHs'
        b't0Wfuv68L/b7w9KGD0PaLF8+r2ZKXLoWFfv7R1Zi0a5hn/ts/vUcR4bWty3VhB3EWGKttoC5BKgQpVdHxaAvGdSAk0S9fBLuSQ1soHXzW9iglnYEvBSUwmaGG9wJqoim'
        b'rRqslgK7aSiTIJEJ9oMGogCdCA7C7ZMXX4peYDNZfLXAc3QK9y8VBT1eE0ImTLGXMOG+LFhKv343PARaxxVvwW5Fho08uoSfDNN3AgfAuoBXC1piHQS6tIn2tzrYN/WV'
        b'yaInPDrZahE2OJBMsCLn0xkIACVh2DQCvUganmUFwnZn2u/w3vnwLCyn7QqEU2YywHEl0ENrSW9XgwcDpvrTjn6PW1CwO1OCNjloENca33eH5RTZeodnNMkbZ8+CG8z8'
        b'g0g/sgGWkZTLG7PgPlAqRx4OAz2wXypZ0A0A7ITHiXq85moFwmJ6G4hJDp4SsYL1sIQj/W86/8YH+DqTGEgCtBTt19dYb4Mf5dL0+ieeTv8UfoRhPNp71m5fe13ZhCyB'
        b'PXhqnkMKnvfktQiEiNauG0wetg0gl915ah5DCh6PJSl1PUwwqhTFLCB8xYWnNnNIYeaovNoepx1OdTOw5m2HQbd5p/nIVHfuVPdhfXei0zx+n7LWiLIxV9n4ujKHhIcN'
        b'RcaPRC7gov8ZL+CpJQwpJJC4tjsNyZvyF+l1+Y3L65d3eA0bO9zRMh0y87ooek3ykiTXLJKnFTWkEjWqaVAbvze+KbI9tjm2x3DYwpXc5n1RGeuWcM2ieFrRQyrR99T1'
        b'RtTNuermw+ozOpSG1d16pleK3VPX3+tSl1Mp9oWyRvX8piSussegz8Xooag5Q/MWjnqGDIXFDsUnjrEYKskY/yObLOi0V/rvAHX+WqOEiMJkds4/EAUvvF2APX+8XEe9'
        b'8HFkMPwYzyn8+S/tFvxvUHLQivqXuX9JyXnbAvrfhMjRCSYbfonyAX8bkCNIxwFlWoqgT7MA95BzV8JezITUy6H5OKCDWujhwmJTerCFBYsM4CYa+bEZnl1CE3J8RGlG'
        b'DiySpqE0OyP1afINbM0g8Bu1UDIuu1EsfPiapim8QLJ+QRbfm06fuNYE22Y9GCB8mzmSBViOLMD6BLiTheZIhG6TqUHizwbbwLm8HGxWWEHFo1ldKYNFp2mfHizlg20c'
        b'FAnaZgs4RiYz8xQNAuJgGw23IWAbC3iankm0wwqwNwJu5YNtauFBsE0DNBXw7VAHQPc43EbIieBtPBLoY9meNcv5KBqwDrZRDFN90EKoM5agXmYScQZ0edHQGXBiGSmJ'
        b'a/MqMHVGzGXmAukGWyaNjSmT1sPUmdmyIgsWWqzmU2ditXwxdSa0JnWBRDzHmA4skCbUGSpv3oLAQ7HBdOCPjoQ6k61ttWCVbGgYjfhEE8/jYAuNnYn3FJtMnYGHYB1d'
        b'cPvhcZlxrAw4Oh2TZfa7klj3zRHBYJllHxkskGzIDqY4DBoVVKQeSJthwmOwHJtigl54kCa+HHeEZ8dJMBLm4gx7Q1BEJnNKYMdKdi4NgnFGI3hNkjOBAsGdhRjcQjAw'
        b'8HQETYKBp0EJEQI2ew2b8oXrCQgGNICTJAEx4EgcHwRDKDCUTxys9KY5MEW+4CSazm+AdTQLhg+CmQl609s/jxfKa0BVbTujsm/2r+V3IhU+uhqYkvKwl3f31tJUC7O0'
        b'9OMmJu/Hua3qMJUoG96wwfLQ1vb4OcnR3x+bUTal6vymttmKsuUSSgVxngoKnkdK0D+TEr2f2pflGl9KyutXz1q0eI3f07t5/WN3X/S++PHyvopvJVM3923PftZ1e5n5'
        b'L7ka89/7amzh6M42qPV1zpXCxPZBzr0o/3NFcosXdugEfhJ1b27wubmfsv0jG9MHdixI/uUHufitK42mH5TbeKDtsLPHdZGSuK19q7NmXo0K21V3Jrf/aVL5StnbDMcT'
        b'K0oSr6hFFvcZph7ub/nq7NFFJxY/lz4a6Rfk4hW2US72oy9m34yKvXEqOTYqeco3dyS4y9fdTNJ+T6702tJ534yEf1l+bv8v9+dUDF/M3vR5SGvpjcdzQ+w9bc33Kep+'
        b'vFwnbuPthh3DVac/ZXy377rjrqCC0UutYneluGxGotkD/5x5Sd8GtebY+DA+N1zXaWRl96u3RU7vwayVPZq75tbFp2cxWtcZHy+IDLZ/7nY1Jjty3iWbAam4+6ZNP6o1'
        b'/Rgnk1qaaHP2/OcrKlpLpWxmX88s1B+SP/3dDfBeofxn6t8NZ8wYm7pS6dMnTr/7xX95vMfQ5/3Mm6YUu7n6oyaVrkfdKS5U7Nnfn9n33N0r9exTzwMHdfeoxn8tXWHh'
        b'4KMmeld0/8ZHTzVaO6WGc427w7de7Xty7Gx/a+BMt0SF77frz2j+cOrjF1/clekrPizy/YvcLVcbn0h01v36cObFVWulPzwiMsWttZhSS6FWFpwrrr+mH7op+fffLP4I'
        b'rL2xY2nVni0uv5lcEOn+Juysx/E5VzVP3WRVh0u08TK21Yqf3uW10PHKh0+qn6Te+uVKzA3j9fOtov44mTnNnVUS963dyQu2GgFfr5Q+MTAY1h9z4fDoqP/Vqy/dIm6Y'
        b'LB7bvY1baHalMyqgPy364TXN216Ji9Ti73pxNy4div36l2cfTA87PRoW5DH9xVTPYpnVwnUWvUtuhsz0qbsm4nP4TubuVpn7LQO6xlNuGV9ZPlrzUbDRjyukrLu/CKu4'
        b'PKPF4vyK5QsXL2pYxbZe/jSzpJ91WIsV9qnw6K8aATd+3/jyvdUaC06r3vEZtLz03Kdhy+qANVe+33nlRwMreEvnQcI32ex1p6q9V/i99+vD4rgPjUPZt1mthyWlm9KC'
        b'OTOyfE6knry1vazrwCbNryMubl6p1Hz10piUVuOBh+o/STz4+bm5/bUZPylfGfs+tuyLn0Vu8tC3X7c9/Fnk05fG115K/qR8cUzqtsXT39aq/lybtyVu8bZHV63qHH9d'
        b'Ltaz/phV/YYnai8VI6nna6+wbu5uX5+17zPNG0/61z8JdnsWX7Im9fjopx9cP3Vf85vfku5q5Z+6/MP6KO39V9ZQcbevtO18/IfYd06xK2+7fHDT9cu4Cz988GCt262x'
        b'X1Ymo1byR8atsKifbZvKfb4boJaG/HE57PJvaz5PO3Zh7cOGqt6sS59cVctSCahR91jVPvuj2b8zfqy9etY03+iovK/ryZc797jIVjRGgA4Jr8IHg+1pzx7/9plV0cO6'
        b'r3a/2P/VkY4+30/qQmTzPtj523yNwyYpv56TT1ZJL+z0dRg7UXXA9bsrqi9Tn0vKVgzHRtVc0YjavpZ1l7vS9Xtn9x9mFkfMj5jyB+unRqGZ0T9zsml2ye5cuHl81dIE'
        b'u9+ErfRD2ggyA7RHm01C2cI+uG+pfRZZY7CF4a4JH1njmBVwYs48cNiWRiCA+hBBygo4p0VAKxJ5NCdiDygVwyduk7Eo8JSEFBraSmkowAapOWbgHGziA1JoOsoccJY+'
        b'smtKcxIkoyiC3TQcBW4DB55xKLzrcCqSD0fh+Fvm+JnCI/AkNkbl81GcQJEI6FoAK8gyTGoJrAnIVh1f6mE8igWspBNSIQsqzNbAKj4JhcagTAW9fOt00AJL+RwUmoGC'
        b'VrA9y+GZZURNKmbVmgnOCU1BMXMLiQVHSTmoCIP1kygosAhu45NQQLkBzV3YgqYy9eMYFFVYgkko8JDZOIWlBdaPo1AIBwXUwLqYZUZ0OTeDU5p5qL793mShRIFiOv7O'
        b'WVIB4Ciop3EoNAwF7Mim7YTrlKfQNJRXKBRrNBtq8AEVJPuu4AjYS3gor1go+RQsT4c7SATLHUCXIAsFVoESmoeiupzkQBf2gkPjQBNCMwHVYH28Kuin18Bb2KA/L5jG'
        b'maB0gKYU0EiIJqL2cA+mmbR5vAk0QdOU9XTmjmutmlBQWw8byEoZHCigL5aBs3PZmmBTsIUkkhhhcJgB21CstEu8A+As2DkZaYBmiDtprMERBinfeDTjILwUZbDF6jVe'
        b'CqgPJOIzbY70K1oKOAi3EGJKCKwnzAhYB/eCPoJMWQK24Wk2LOXQ1BQtISHQORsWk2KaLxP2Co0CNsIeGo+SDgZINXiARrBZAI+SmkcDUsC2uUS8c8FJRb65fC7YQFvM'
        b'H2YS42MdtgjBgRA4yqkEcM4YdQFEsjdkgM7Xtj9OoD6jzW4miXN+ouQEGwVss8F4FFTxtO18rxHczccNjeNR4BHQo7gSbKflaj9sMCGMlAk+Clo/9ICzcH8cqZvpsBe2'
        b'0ZAUAkhJhY2gGq5fQkt9kxboGGekEEAKKpGt6Rw+RQecQHO2vQKIFEm4iU9JqVtEkp4QAE+y42EZAaXwKSkSdM+F54Wwlb3UYhyTwoekLLYnmydacI/0BB8lFjRiRIoK'
        b'PEDvylT5547jUYTNaEDKaVhE8mMM6/BeEiHx03SUUgnY6Gc63odsSiSAlFd4lFxQDOq8QsjDSnCP7QTOAJZHEKIB7JMjLUSxAFQQxghmo8AdK0Eb2CtCJE8aloBDr+go'
        b'3dIEkNII22npry40fQVH2YhkHQNSlsTTfJQqxmp6Vi4Cj+JJuT7gwxf2+BYK0FFghxQNSJlG64SWsuA5OqU0tUEsHBxzhh1kx4wFijBqo/wtaJRlaN2wx1eO3GbNBhsI'
        b'HQVuAjWg7TU8CtgKTtAbe+vzwS5UzzuZ45cJHwXWedH9RlUhLKHZKEa+BJs+AEr5O4Ih4EgeOAWO8REphI8CdoM28uAMR32ajYI61jM0H8VFi87c2fSgCTqKDDxIAClB'
        b'oIGOtdMN9VM0H4WGo3jDww6wB1aRnVAbcDAXl4snaJTAxKGSIHgKJVkFdgiZ5crQJVsEmp0EFyLZsDMO7oANJFnZoA8U0fuUsXAHZgRYgU0kalXQAUvZ45FigZUAO5iw'
        b'Aq0hwclwIu62cLMeG27I5XMe0KJVzwuNezQH0wUcMJvouiRTWdo5U2TBFpqOcgwJWR4ePT3AgJ+p+ASeRdNJCGyHbbCVxGHlAnrZC+E+PqKFz2cxMaNb+kG4KZhPtJpA'
        b'syTCA6CfvZhOQRk4Dg/z4SzJ8Ajhs6wHfaQpzzKalYck7XUyi48fqGXnE0nV8CvgQ1lCQT/msoAyFnnxKlAsLQhRgbVaNEcFnFKkcUjrwGH5iZMXGqESg3qpXcI2BK+m'
        b'jMSvE5TPgnv5IJW3YFQWwz5S/fqwfE4eB9auJTMNVFD47GQDK18/lRQk6EI91XpM8wngGAaJwzKOH39CoArWC/mAEzNJLHmpoJO+ieRUFO5nogGjyE2f3kuGB2DxdEFm'
        b'CtuDUFNgOdhK52gjbIfVk/e6TSNRxTR7ECFyCERDDH+rOSwbbzWro9GO9Hrb1ujncVSTYWcIEqVtZqhPllnOWgXP0TQQsMksygwJH5qwYeotrGEKL1oJdoFOur9dJwUb'
        b'8uCW6flBqE2juSXOGoOSVWStNkx5hk9sIuB2uI3PkflziEwu22oGEk0SbWNBGhtuVYAlrwNYbGAznaxDRqCXhkbRLCbY5gyaXcAeujuugCfl+Egw2KBNqGBwvyoROvFV'
        b'sGuCNgUqNAhwKhqWEnqOJjgDThFITDeaSrwJilknnAKKCugTjiJJUIkSKcZ6nXQDKsE5uhFtgzvN6RYGz4DG1zExaPZGUmsWATeME2KqYSWhxICzQSS1aB6gzn6FUhGj'
        b'mPFZYaH8mSs4MduJz4cRAw0EEZMLyujpXzs45o27ncl4GFA6H40MZ5PpjvI43JnG5tB8mHY00dzkAjYTaXIQRYPOclD7OiEGNFrQpd9lnD+Bh+kl7qHRcFMEWkm7RINw'
        b'EdxLADHw0HLMiJlOtwU4gATgFGHEbHfFeO3JiBgZsJcGmXWBEljFngMPEU4MgcSASmWSMtQAasYhMXxATDWsB7tDYT/dpRxWA7V8SAwNiFmm4Qu2JpDyCldAo0RXgRrN'
        b'iKEBMWwh0sAkYZssaj2vo2FireTC59F9dAvYV4jZMBNcGLh+IahykyHC4AaKUZ8oSIYBp2bw4TBtNnSZNYEubQE4DCzNCmJ4g+OJxEOyULAOYcPMhMUYD5OMBg/+9ODY'
        b'aj4GhmbAaIG9aDa7EzZzlP7D4Bdcgq9vKb9hAar0+n69AO9FS4I+sYl0/td4L+rDKk5voF0qhR+LUDq6/0ZWixlXxYynYvFPWC1vD/x7mBaFfdL/PkwL/yV8i/C6sMbI'
        b'+sgmo8NzUI5xGCqDJgYxSianRsen8DTs+diHOu/GkPoQnsa0f0ZKeUXfkK6RrlvauLZ+7YixK9fYdVCCZxzAUwnEKfov9uT/99gTaZxSLO5KPBUTLBNSNVIC2efDPASs'
        b'5iPb5zTPGbFw4Vq48Exm4lDxZnGMMfBp9unwPh6CiodjOiYsbGg0xpqwjGexVdXGwhjTMBhlGgGjZPyrYJQl9Uv+CRhlTJiFak3sX+aH+Nf41+XiA+ARYzeusdtg7oXl'
        b'55eP+MRyfWKr/XkacfzWjCOTqpfCZedb74uSEt8cP2Ixi2sxa8TCi2vhxTPwxtcC6gM6mN3sTvaItQfX2mPE2p9r7T9iHcG1jhiKnMezns8zWDB+nyjPwH5MVBgXKWqP'
        b'j2UoTe2/wx/R1K6Nr4mvnV8zf1hzRodHh+hTShhlOWwgtjeWX1L3zCwwE6Pd9ZgrkjRji0NZHcLDhhE9NgMzemcMTr3gdN7pgut5V55TxLBh5lDM7JGYOdyYOUNz54/M'
        b'TePOTRuZm8Gdm3E9JnN0ltsFkfMigzkX8s/nXwzi+cTxZsWjgsdJFp6JwTP/BZX8F1TyPwWVxDIcMafEcRxTUsjAmJI1rP/bMCX/36aTFLBoOkn4KzrJR9bqec6WDwzU'
        b'8xmW/1Y6yTvmpiWiAmiSIOd/AU3yHKNJsGM7giZhYTTJY2xKovCf4Irk4aXX25AidAmM4RJ4HYJwH1NZgt+CEzF/C07E/C04kdfDUugwi1FNrwl0iO+k+CzeFYYpIdaY'
        b'EhLG4BBKSDRNCWFJ6fIpIejbUwlC92iaeV7/HYwQQwFGCP7+JHiCEWKPGSGO/xwRgl8Qzrjn5Tfq5PqC5SqFdaHwJ35NOHoN/v7CnZnBxHQQ/EnTQcge/8Aa0ELwILDU'
        b'3D/IMscvCJaZMygTMCAM+gozC8H6SVo50vy/Y79gMoji61yQOKEJrgYmZMgTdoY4n6khPSlUYdIviVe/0lkprBbWOKkjyZCYC2FjIWw8JFkiVSJdIlMiV6KQIpkkJEDY'
        b'EGZSySJJwkVUkkiL6ATnQ5SEiqFQcYFQMRIqgULZAqHiJFQShUoJhEqQUGkUOkUglE1CZVCorECoJAmVQ6HyAqFSJFQBhSoKhEqTUCUUqiwQOoWEqqBQVYFQGRKqhkLV'
        b'BUJlSagGCtUUCJUjoVooVFsgVJ6E6qBQXYFQhRLhFEaSXpFYnCL5po++KZVQqMRZqLxFSsRK2Ki8p6DyliXlbYCuKy9nihdxjG5LergFRXryNbzun2a+ZmqFbR0E76CB'
        b'JROa+vlZ2GV8Hn2P3VRz+q8tcbCOv02bFNm4IlmepY6bgBER3yaG2EPzLW/Q1fzkXOL/PWtpci76NdkISNAXvLlOckJimk5ucnZucl7yEoEoBKyUsFHcpBjeZQYwWZ1t'
        b'0o/gLGz94ZeCckd05QqTc5N18goWZqYTe4b0JQJm5sTAAl1OQP/PT8tNnvzyzOT8tKwkYnmL0pyVsTSZKN4V4GEiYzk21Jjk7F7HK53YPJi4cfimfhmTLUGwwQTfloiu'
        b'CCt+PYyXuLmOiTtn/LYEnbxkbNOSn/xnlYTr0MSDg23TEwTshvgWO1m56anpSxIysJE0nxmFigAbgL+W0by8hFRiHp+MQQMZ2HyOzr1OUnI2GhfzdLLohBPjHxP+NXcs'
        b'YZlZeZNtQBKzMjOxSSORvdcMjYI5zNusZZkZt0USEzLz7aYlsl7r7ogS4ir0sUuStmfcQ5HGIYo6JCaxZ6Q7pSmo4ciUMFKkie4li0mVTtgmrhYiupcsAd1LIQEtS9Ya'
        b'Ib7u5WuhE7qXKRzmfdzj/iU0Y1KTe7dhyrtslVA50GZKs4MC+XY2uBEkkHhf1TCqS2KLhhrw2w3YTJJpwXtX6/4TmAOpBEdsk5+YgPqHBShJC2h7ITqyiUgEhTRhydtN'
        b'/ZKS0mnrMv57JwkpFuecgmR+Q88rQC1woqN5uxH7JBu8wrR09ARupwkF+VmZCfnpiUSsM5NzU/m2SH9iDp+L2m921pIkXMJ065/Ucv9cN1aUel03Vis4D59L1FVu6OK+'
        b'MOMcy+dc4pwu59w8sT6PypVIXy3WAHroUd8UfYBdoC0KdMHtsBufgedzYCkHnAblHLgbnADokagV6BHQkCdD/KhHEm91S4LWgOP64KAwRa2h1sBOUEZ0Jw/J094cH/vm'
        b'Z9gazqeI9iocAMdAN3pDbSYaGJwoJ7iHmfHTy5cvVTOFKfSUzr2ctIylKxUpop06K8SOOKmEVeBMoK01kxJ2YISC7ggOswCfecw2Ao15sEwalhbSOjOBwZbipiYMCp4B'
        b'DVNhlYgZOAX2rpBhLw9m42Cm0uwgxgznmehxPMWxgZ1wp8Dz8Iy6hQSOh0HpOQrrwbOgjKjBKsF1HmxL2CFCLrHwCWsz3BeEYsEmTYHmWeNxwBZrkgw/05xgDuw08wuw'
        b'xEo70bBaTAPWgEMkT3agWwt20dfAgCuLErNjLoE1czgs4gTSwFQnIBhusYDbba3tYmAHk5JczVwMe8GpAv5p2XHXVzegNO4QoSTXMDNcppHrouA46H913SmdQUmuZWaC'
        b'/aCDpBY0LkOJL6dNj3zxfWG+YqBC0F2T5xRRZbgJbqP9Nh6GReAoDccPs4CnyZmHPKhQhN0sUJsaVeCHE9UD9sJiOXhIUP3ahChRhfrC0sCAAAtmjgs4oAH7QJkiPAFP'
        b'BCiAsgC2BDwByv3DI6jkFJkZoAW0E7kJkBYikiDjtFKyVUSJKojD6WjPDH9L7LAEbrXyjzKBpb5wSwS2vQqIgh0TokvUvkP8hOUMJVCOisAB0CAsDHu9DEEzh/IqVIAH'
        b'8hejcsdHSqEzjbDTzbNp2blIUGAPwwhUJ5MrTEtYxBaDW8Gp3KWo+oUYpmDHKiLMKkp5sEsyCO7IIc+0MAx82UQ9V8QL9uZlx4IdRBuBJclYADbBTSS27NDIvJx0O3hC'
        b'Ej+yjmEAdsAeJEpY0DQs4L48eBr0gE4SIzjHULIFvSRKfXNUb12SYLP1xMu0QBstE/1icL+ATKwL4ld6eXaBPbouC7bCOnydrndYEmThHxLlSz/AWoUe4RcnWAe7KFib'
        b'wQZN6OZ+okK9hgO7BJ9dAKrI4yhFK4VgVYFjATnl3Qh64cYIfq2AYnAAiaI4A/blwar0eVKjQnnGaPSsK511NebqEt4smU8K7tgvuXNyyZq9QtIWn4Xo1EvUKzHcNUyl'
        b'NUzDcmY1hXruYcYr1BtFGsaVS+Tk3DD7LHTZBmdqhssH7338WC0wcOl3iy7cON0kd0n3edKDfVkp/XPbByL7pxa/f6NHM0RKY/eq04uebPniyk9ilvt7XEx+6/t4ceEx'
        b'hzXC91N+p9ZOXVJus1Xb5v3PHqh5mxrNlfdaIZSbY10mN8/sWmPRzD+GRKfqrrhTZagXceuklPVnofkLVjz66Mu6YLk7H9h1LyiZ47kyVmihe2S/ol5bj+TYz+adjWZb'
        b'Wt2N9Y1Nm9xzv/RO7Dv2PDKw9wxvbv+nVxJiZmRe5n535mDuiV28r7gJKx0/1Us9MJjcp9qSFa6/9jPr74/WOD2tMv5Y6FrXUanqhKyonCNFsd/O/s7yg4Pd5Xfv31UK'
        b'OWwZl9ry9eLZ4lJNY2VzjzxS1ZlW2WXcHtvV2pjxfpXatxs/ifvZPMd09v0CPZ55wtmEq2nbtbVXnx/e1ibR6vOgz2v0kczps0uXW5ieurrsmqV+pGNj+7YrZz1HH8U/'
        b'HNyVm1QhenNZz+Yi0cI94fmjD9eAttBww/gDnv1Pt9W/F1u97WXW7R0zgr59oOfs+mFf8S/zimoOtBvEXBFreqbRoV3cV3/0gy/1eazaVN6+gEsHP7l8LyZilbL999m9'
        b'GXoGo0lLNe/WLsi462fc8fLDTZzBwLYUazX7Hy8Y7VjlPlrS3/CQmnWhL6Po0cNDrk6MX86d1vtBOUXo2csZzwZaLofLOEwX+3hxgOWp7++ffFB/WnzWnqVhJxubpvyc'
        b'uij+4k+F5j9Pm2610fHbUv9P5F7++vvXnsIlUmrz7X4/8+Glk5efam4v/LDiwzThYZWqq3F+2c9NegM1vgn7oa+f+aDgumq9SJ/Wsx84xxIfKNzIcfp8rVxBhvzLxQU6'
        b'05s+7/36xfxjrMINWxw7KmZAp1XPP7h/c0pTS0iS7kdXDjXvYp5dU3Qz+oyZcVZMgvNW9KFxeZvRjpn3f9h04LLJUa3u6RrOHyp/9ljx041pQ184pk2l2ssk8o+ahJ5/'
        b'EltolTS7++szU3rsPRK1H/+w5MHPSrN+q/hauPPs0YLRx7/vsfyVmv9yTFv7uoLsGgOOG8G3wH2gn2lmGcSkmAwWaGIE+CvT/v5qYbEdKAftuPODpWprQ2AZk2KDc6hT'
        b'WAaPkINsU9AIjpn5BYpSTBXQDkoYLisTaP2CY+BswLj7PsrdnOinBiyiT6+bV04B5Va05uH8/8Pce8BFda3rw3savQpK73WYGdpI79J7BwEVlKLYEbAg2KIGBRWsg6IM'
        b'ojLYGGyAFddKjnjSZoPJDMacmN4TTDPlJPnWWntATHL+93pO7r2fP3/DLqu8e6139ed9XqFGCdsRXof95HQ6EGznoy5gh1e6iI0GBSeNDWwPeA4cJv524BnQHoNiYjBj'
        b'SjBo9gQ70gkwEzR6JQg9CPOOJlWMJg7nQIsaeyRocJqCtQVX4GXGq+FKR+bQutfYFZ9Iw10iDWykckRjHtsJbpk4XG7NAXuS00WJQtgJT2GMhS64hB3xHV9AEq8B7Ya/'
        b'h/pqr+TOs3ZmABCtYJfd72wwwfNxUM7VqgV7yPfOEWhPOGyRgH61wxZwXJu8DKrJnXDXggZU0EGO44E0g2ATXGG/jiAxAPWB59CUg7uQBbcv4xF05volQRhOkiqCWxym'
        b'nNZbwnZuFegBhxhow0nYnjsBjVtfQ4HzhfAIg0E4mwefR6WclJoswufqvOQ0dQrO8AAvBGyxZ9iDzoJLXtVwVyKuDUMgTTZIE8FLyWzKNo6LEu/VJjgVB3AL3MJI1D3a'
        b'5DU4gupVP5YNB+eDWyS7oloXlFmaSJgKmsEllN9EbvY+XHgSSsE5BhxwS1+TgAtQzd544njGYhoDajhfUwya0j2TUoWJqauAlEUZLOIErg8kyAWu5TpmYsF4EroBznIw'
        b'SFATpb6fKOSGCOL/CsOMmzSpovUa2mw9uE+XwA54hnnVKfCoA/aVxFnCqs+3YPRGvgTsgBdr4E1w7omDNdgezIC+vDUxGG4vd4q3MHgS9DJaIUUZP08wXQRfCLeB/Tx4'
        b'mIUmk/1wkMAwNubOQBPBK2HJBD5ymgU64ABsY6C3W2Ys+VOcoKEBBx7KXsO0sCNAFqH2YhaLxkwM1ANyPbXvSLv1Ew7QqKR6jO+D7ToM0OkceB4eQ+XoDVoJOpADj7DQ'
        b'pO2Muk3vA81Z6Lt8SuEeARbsIgt0e8eRVG0EGHDIIGWdwC3sSfAYbGbQ6FeABPUxTRMYIdgMBnjwKhunvJmBw5ythT1qd3N8b12WvQ/cR6Jmu5biWn3ib24aOM9B/2ET'
        b'kJsyYNqzQjNiQE28fR2EVzDK/DAb7JgJGxkMcVs0uD5pi1wMpb8D9cP9s0mVRcJDoBHNl2Frg9qH32UWahNVDNrqGJp6XkRvJyZ8dfCWBmVQxokFl0Tf4gVNZFo6aFqz'
        b'Gl7Sr9q4+sn8EdNpecHdCakivgaVHatlwPEirW/tbMdqgQ6ay/NXopmwZgN7Zh6QEcVaj4qrv1qwCoNo0FxwK4/SLGf7LoY9pE+ugO0B6HMTMeYqXYAx6zxqOjytBzZz'
        b'jeEJBkaD5orgiC5OGyVhCy6gFMBpdlhsDFMbp+DejIkkvFAePfM0KYM0TiTqPVvJeLDK0K86CUP5WdHgKOxnGcVqk5awUhfuZ7BQc9HKZxs856V2BQZOuj7tKgvsCcRY'
        b'qIp8Eq+gykqNUYfyaRSQhcxgbLt3obVeq9rHG7xuYspygpLwb/HhgA72RY9kRFIkokaZBo454z7BKwHu4lBO8BQvwD2FKGzdCri1Oo2P7RcYWJ2RJjhkw8msZeBbELUn'
        b'EUaLo6krXjaCwTB1AwMni12q+Ragn/QkHLCNVWerdgabBzsKBEmiZJFHWipsymVRhgs582OyGNdxg/DCYiQY2A46JoXDiDU0YKXxKP48HjiyZjqxsHDHsGG1RlQ3PK0R'
        b'6f5+LCoEnNdIs4HXSKbZDfCsAPXNkpgndLGh8AIp4HDQGKCLB8sJxTUGfQbwKgecW1tKSsGVB3cKyCgjqgeDGpQWvMYGraAT3iDxzcOD/4jbCljKnQaOFPGt/nchUv/6'
        b'bAYPt0/tN/zZEQ0hRps+dYvpaZ63dh6Dn1o8C3WJtpJSqd89E77K0rrDtc1V4RA2UD0UPWqZ0Br9cOJR6MCCIadRy7iW6LEZFhInSc2+5S0clZ1jC3e/nsrGviO/Lb9j'
        b'bttcmXjUxkvOom18lTaBtE3ggMmoTdjAAtomCgXUwV5pCtsKGQgTCkiemZgpTUS0iUhh4qfyD8YQCqV/Iu2fOMwf9c9R+Oa0xNwz9XxoH6KyD1LZRz/S5FpMa+GN61CO'
        b'bt1WnVanbFoTW6IlpipH19ZkdDHjgZmtpFoa/bqZu8rOCcMzlHYzabuZ8ux7dkEqvlAS0570wNZFWooktfWScB44uMtMZBWjDn4SjTFzm3FDytELNUYrF4VL8KhliMI0'
        b'RGVh3WHZZtmioUZkKZ1m0k4zW7j3jOxVLgJZVGdB95zOOUoXf9rFHz91VDl7yHw6E5XOwbRzsNI5gnaOGHEuHPIfdrgdpIzOpaNzldGFdHQhDuwwZi+SVfQu71mu9IzC'
        b'OCz7WYRUz8YJwx6UNj60jc+ITaE8byCqr2CgfriCjsih/XKVfoW0XyFTpE7SqLaCjnlt85iDXqWNmLYRM6WPYg7EDfkMJt5KG0xThqbSoanK0Cw6NEsZmkuH5ipDC+lQ'
        b'JhVrR6lPW2JHWlua0tqLtvZSWgfT1sFK63DaOlxpHU1bR49YrxxaPTz/9ro7G25vUMYX0vGFyvhyOr5cGb+Ejl+ijF9Jx69EaWk/JZE3beM9VSKc2UMHNxmr06LbttNW'
        b'6SCmHcRKh0DaAb8yUNnaoT+6b9o4tcSqrOw7gtuCO8Lawlpi8Nm1dps2RoSNmIfInHv5PfxeYY9Q6RFCe4QMce/o3NYZMUsidAWzR20LFOYFKgfXbssTlhLemJWtpLZj'
        b'Q9uGUStPufGole8DR0+F16JRx0qFdeU4j3IUjmtQ0y0OJe9N7hRLa7vrOuu6ImhT34PJSBtsnceNKAc3XCljjl5yDXlVnzZzYq30jqe945XeKbR3ynDZqGM2CmNIqlOe'
        b'1bNY6RlBe0YoPeNozzilZzLtmTycM2qfhdN5aOUgdWgL6ghrD2uJxkfYq1tXM1wOSjMP2sxDaeZFm3kpxIkjZoljIrE8GiOn+lP6Uoac7rjddht2ve01KsqScO+Ze6is'
        b'bHH5KK1EtJUIUzEEqKztldaeI9aeckfaeubr1p64FWw8vHHMM2Qg+lbcYNyt5MFkBoA1EjpPkZHNAB6UGQV0RoEyYx6dMU9RUjbqWY4aSjrTIKz549MoD0/cDl3ft3Lq'
        b'jJHNkLN7LHtte2xHnQPfsAr6f3yFPGLEbNaYJ2p+/fl9+RgSMCS+E3A7YNj/dsSoZzb+CMG/+AivEWsvuS9t7fe6tRf+iIbDDWPCoAGnW66DrhgzogxOooOTRoLnDJe+'
        b'VnG34rXKu5WvLb+7XDFvwaiwFEmfqpY+GEkv8MLSu6lssHrpjJlYqPnAlWYC2kwgS7pnFvDA1k3hnjpqm6YwTxszc5C6ypzvmXmpHNy6bTptuuzaNMZs3GQaclN5uVzv'
        b'nk2YytFdai7ReNPORcIZs/VQ9yaoQ+xY27ZWaedL2/nKg+/Zhb/lKBg2fc3iJQtFTr4yZ85IzhyFcO6o4zyF9TyVX6CES/Cb4u7wzvARc99H2pS9K5LZ1HIKN4Yxg1g4'
        b'gknm27n/fezCfzGM4GHiCU3Gf3fwSNRCUTG1w8+bqMfps1gslt1jCv1gmIPdM8AcqvG+YoeGF9WrG8z5t9g1F/1X7JpPf8AEteY5lPEUak2ficNPcnootC9f6GnvgQ82'
        b'PL39xBNUxH9k2vy3JF6IJT7BflaJ5VjiU+wJia2wxOozN/vKsqdk+7fF6mHd1youZQ5nn026i1i6vsnydCDEeYQtrsKeJIjpH/9jGXFl81n39YsnDymLK59R0CtYUO5k'
        b'MbpG2dcur6yqLf8TPsm/okSRtHrFE4dWzyzsIBbWYFJYD1yq1TWoWMmB2ORZ2F8lMGlL2s+smdefbkue2SswpffyihWE59N+/oIVtTVPMYT/55ISTt1O6lklvfW0pFY5'
        b'T3Nb/zViyZ5ZLIDFOj0pluUTsWYlRv81erjq3DNL9eJThbWql/pP+I8dWM+a/TDO3pE1USjuOX/Chz7BkftXNVUdQvtZjEk4n03Yl/B4iMeyTZQkp6P4cPEUBSPcnkxn'
        b'+Fd1gFqMnDUrnk3KV5/upC3UjLF/kWxbJzrnBfOXYgxD8YqV5cufTUD66c45EAuIU2GO3JdORfj8noz4L5PfYFL+0qUrqsuf7QPu4Q94lXrqA3Ay/9EH/O85Btr6e8dA'
        b'k2U3CVvgpFUefuEQi2w/vKX56MjfvzCbcPLDFa88xaJCRtnvCXP4LGa/P65qcrORbDSC5+ENNtgRw/kTxz5OmJ3N9HfzzaXly9V7FTgMduqzNI5FmVsfWt+6XmHk+Ixu'
        b'fP51Fkrcgv0oxoXPkjjWv+HD5/8vlUb9odK4aTmVobNe5BEfgVmqN4/83X8HqrW9rWIOpXOcbfEOlynCP9bJatafrAEWrFixVF0pOupKWUUq5Rlr4/+R+P2p1VH1n1cH'
        b'hoVhlf2mjpqAhaEK4aphYVqNLDXRPQMMoxoN1aAwNqqqSUr7Bo72UxUxFSCGKoW9gaOuqt89/deOtzA4XfxUVdmlEVSBpxh2VFfBC3rZCRNwhD3wCgHk6KUxgJyhojI9'
        b'S2NDhq4O7ocHwPlqg1XasNsbxzjO8qwDOwhu44tpTARF9nq95shYihD4NsBzBeREJJnwiGbCRnyasyMlDdP5ZmVkifLgcdQTz4vUBJ3p8EAt3maGUtCllZyEMQdg9+Rx'
        b'V1peEY/yKOWBM+AWYLjWQE99fPXKNHAedCxiYBYmsIvgEawWEZYPsBUcm2opDw6Aq5qEdA1cBX1e+LgmGTYFg05NiitigXN+oJ0AO/xnwHbMpGdiwaO4mElvDuwh6Jwq'
        b'9C0y9S40ku9GCtmGLs8FkhxSPsGhPoJkcK4MNvNFiVxKW5MNdmvCZqbs2ufB09jEHXSCnShdLj4+OunOcMAdswHnBZ5wi2OikC/SoLSD2OAkbIX7SS3p5cGbhEuHSuRQ'
        b'XEylAzbDmyTRChFohE0ieDMhjWwha8xlT18N9hB4VB3cvyYZ7k7Evk9SYBMpc8x7CHrXcChBGA/ugtvh80/pr+6E/tZg/dV5Sn+f1t4J5wx/reYu/L3m6v5Bc0VpRD1r'
        b'HLiUSsuEsBz7sRMoRiHOLgTXGMqYPFsOYYzxLmMY+666gBuMXX0lOMMhdvV8ISn7JUAqmKxSXJ/wKpRyyk1WMLU2CLZBWTU2uceHdVfxWSPY4UiyM4Ny2FWNzfjhKTZb'
        b'i2UDb0E5Qyl4Hg7MZ5g84CF4BHN5wNNCgtYBUnAjYYLDBO6DuzmEwwRKQBuT4WbQu3SCo8bQk4sparzgJSLqipXFDEEN3GE9yVEzPQhKCRqv1hD9iNhV2eiPw6osygFe'
        b'COTziN5CeQ1WdRzVevmTmOCMNhG3AOwENyYYYpbYcTFBTC6XEbclf8UUVhpMSSOC1zkL4AlvpiHtgf0aSHNPwQOTvDdA4gp3EC5IsCeeI8COblBj8uSLklJZ1GpPR7CN'
        b'F1QKjzLgpR7UoDdjkpkUeGOSZ6Yb9sCLBC63DLZt0CXECyJMYnUC7tZim2XCc4Sts8FnhWCSlAEe4f2e8cAzkjQEJy58nrBhpDCHyVsYNnGwkzQZ13zeEtAC+xma7nN1'
        b'8CwGOvwp5QPYDvYxyaeBzZqwJc6S4cm8AOQzSEfEpeBx0Ih7ogVwkPREUUibJLjz64DSp7ui5eWkt1tTDLomOzvUlXVNdnjq7g72xDB9xI6ZdeoeS5MCx8Eh0mWBi5oM'
        b'7ahMWMRwiviwsM50BcEmUoDwAmjMUhNogKOgiYspNMB1a1LxoUt00Ct112FtjzoPcBQyeog6pwPGagYvcAXKSL8TbkEUvwa2WyMVZlGsQHjAjoK7wX6kvfiNxvQkQaoI'
        b'tbJUeI07H3OQ9oEdRI4FsEUTqRg85ZAgEhJ6toPserizjlRkLtwLN00wukxyTSA97yZ8E2D7AlKYYDe4BjtJuE7ULCfYXwxR93iU1DRsTXOd6PLQMNExtdtT93ngbIIa'
        b'bpeXBW+AJnhhNaq1G4UsKKNgdwU8Q4pzZkVwNezTQCmi8Y6HWgHYPK8Wzy2muS+D+9BzYYITJRTDTWTo+16kS+VoeVKUUYneJ4H2DCPpTDTrGfbCQ2+Jnn29DvPwkQWX'
        b'Optpirst4XvrjdQP6/QovWBfisooEYrnljEPEzK1qGa2A942TQnLm/30PIMz0S3iM+5k1IviBcdcNEtqYNWz1rKq2SyqjDrIOsRiUc16XNRtnuOQeQFaIpNpE/s+29P7'
        b'Pmt1NZ5d2TMLjvvaoQvLl5evXbkqvC7099uxNeWriovR+gNvF1SHe5J7gk5+8mwydrk2mlThXudjPGdTxJTQs4sV2TlDmaBg2BkWoLsfyQxti9E0FmHstwAdQIIBhph2'
        b'ROSZSJhgkjIzRHkJ01Gr+ZMR7CJbh4WpZU7rlYBNoJvAedGwipPojEKdOV8Ed06BjljncsFZcHlD5auvhHOqV6PS+7gz8PX8oiUmUabHxt56MDrzlXOph/+mWrL0pKmx'
        b'sfbJpIxM41bHwrM7bayCW8OXDiW3rfvGxeiE1/2Ih0XfRtRViI+MfJkouXRT8vznX778uOGjkIWvvewcMW2PtovbiexlLe99/KWjw96apPa9Q93dvXtXezRfWbx1wKEi'
        b'sWlsJLzm4Ztb3IqMlvMGR4z3B8UOLHFjvcM1Xp4cCBZ0Og3kB9oaLFhratGkeeem4nsNF426xDI96OBTlrA1uDp0evsjj/e0iiL9TvDGTj1nvnKGbeBL9sbVFZ41p8ya'
        b'Mr2bWCs8s/KVv336y6bPZF/dH+2IWutSeiu27nTZMFuzT2zw96hmvSbvXvPPXjwwb9+wlvx0VMxzn7Mj42JrEmbMcBHeNttS/ev95aNfXm8cd3EOPj02+jPX5a3U52ef'
        b'yM7wzL3ycOWYd693b5tDwd7ezn9+VlF/iz00225P34of23afPhZnYvxjGK1buWb/yZ/mDrlu8/v4+5dqS9uOKcVf3f227dgLeaMavqsHDwT6yTb9skdQUixlW7ym/06A'
        b'0d9Syz6f8an9J19cG25v3iEpMvERXi3a7ue767Ud5i+dTqn76Z+f5+yedezt9u/XW+2Ybla1QfNRc74o5sC8fxR1rHz96nc+P/Je8Vr7z8C3Z77HKS0UX2m2EB+uWpGy'
        b'J/aLPtmPu3x+dHnFq/LXhtI7Fw8/Ukgy32iO/1tz0C8fHrNv7q7waKk8YDC6tuLzE8ePhhq++veYbIfzaxu5b8fNLLYv9XplwUsnEoJMrn6T9HbRL6odB6wv53ccmxN9'
        b'/QvunYf126qj05qbgzcP+lWPvLVy/xFltFN3XFzaXE/fz1Py6xs2Voz/qrXxuUVODY5uL75vHqYqXpZ74/7p2obc1+7ca+AVfvXyJdXr6Tv7Prj4o+2Wtsff7K0cXp13'
        b'4peFVxRb5iqPmlSevSCsKuTvj782VNY074Fh1M3iFWs0M5JtTwexvxuK//Hw+oNXzzyOP3jvu/am8q8i7lgORJifF3S//Pin1QkpP4bU25dO/6xh46Wvvnrw4HvpjK4L'
        b'10NkL8p2nuMsju2cPauy/+Kv3yTk5X3ne6bhuTo/9ltfPh57Z3H3y0VR01e/cv2zfy7/bOyXhSviY3996+/Nw+N7Gj9ce83v/PyBopeE44b6fUGty4ocP4qLyXv/e9Fw'
        b'de5jkNI9kG5o/03xtyEH1kXF/PrFw0M7hn874bZ/73uL1rzoUHzX7mfxLr/f2J9P9zu0x4AfxFA+7QC94BKejgAZF0OSNuHB5TpsB1sImibJEG7WxXxT2u5oqYABgI1g'
        b'0Bh0c0A7OKYm+kHjihwO6HqATrgNc9ARjiErdt5qeJFgl/LQCHlwAkcXNhvNyPT0CaAoBbTNm+CXA73wOgMQO8fApdAgf0hLkEige1GglaD3jNeQV0Gg136CSc01jsGO'
        b'5aSQV/WGtRMTukg4wMznlgUx8LiDtr7kU6pSvPgalD7Gh9VwXDVsCaAmAVzi/iloDFxCiaGZ42FwlAHl7IBSbQY4VmnOELwthqcYTJkUHnOfBI5x4bF4Y9Y8TiED4JJm'
        b'm+tiTh/0YUDKzmGFawrIixAgcZiAhVXCs6gOluoyULNO0D6XcBxCafwkzSG4Nl1ACm8jkmmfmi6wDlzgEL7AZeAMgTDN84E3GELAHnj+CSkgEvAkaCTRnaA8j1BeCtFM'
        b'AfR6grNsMeyEz5MPCahnJwuzQcsUUtJ14XAPweaBQ2gcPqY7hd7wCoqHKQ6R0twiaRtUwUHdCW7E5+Flwo+oDfpJNdiL4RlUzphLFFVSPejlBrFAnxs4xqAUd+VG6HrC'
        b'o75TyBkrwaFZDLquO1K3Gu5k2SQmwv5kNqVZxfYAXauZsu+Hx1J13aPh+ScMeIVhawm8JwNeAn0YRlWFVHUnBqdpUDr5bHAVnmXgQdbw6AJd0LOSIK144LgVOIxdZtyA'
        b'J0naZmgEO8vAsNB0+Bwb47AOgBsEQFWfA/bqJqUKNKisJRxwlQVawcEMkmhtUI0AnsbLFW3PZE8dPHkzB5e5AfEMTyE8Cc9nMqDLJ8R4pkg5OkATB+5LBDsImHElmvzt'
        b'/RMOOw14ggM6Fq9jWuCmvA2Y+K0QXJ/C/RaFClntxaQHXC2bxMnyYoEMw2ThADxN8kAKckn7KR5ZzCELLoHdbHg9Ee5legrZnHqmbXCynjDxgZtc0EwKIgwcr9Wt1ddm'
        b'U2BwNseBFYVmuydJnS6E/VCCuQ0J9pWXwI5lobnfnloSrSEdXmN4y2B3LIfQlsWHkTdc1Gk8r4bFYZdHQBYN2ogKBSCVO6k7wUYIT4FtM9iOqPe5SRqoo6YQNfNIxyl0'
        b'Z5lOyUzb7QZ9VQzZWVE4h3CdgYNVjFpfa4j+A9VZUBUHNqJpfwdB6ZWAE2GEkGwhG/ORwdYE0nPAVrgVPIe6q4Pq2vwdIxlSM6YfnO0s0lWTkSWkYjqyXjVwF5XGTtiC'
        b'NHtasAHSQvTJmslsB9Abz2j283Yb1DxpPrCPQ2jSwEEXUrHBYDM8I3jCcNwfh0Hk8MgEgdsx1E2jZiRMQ1V8HlxAiy4UTBdzDJ8PAM+RxrESnINbSZBmvh4fNhI/OefZ'
        b'sGsjOE4KbSnYysXLTuzGFfSyQScrA26ZzyAl2z3hCUG6EO5sQGraRLDluvAmG/aXwEPkm/WWe+l6oIU1xYHb2amsmWh1t4mo0wbYZjUFcozhxstRL6YJDyQRnfSEO2dO'
        b'IOtBuw5aBT6B1qMK2sN3+L9H5P130BYO1B8Jz/6A3mMm/TpPpvJ1/P/2rJ9sys5FS4kfyBz/25gEFiX0k2qqXIQYntY1T8pWObnJfI8Hq0RiaZxK6NsZ+1B9JY1Vefgw'
        b'SCqp5kMnF+ni4+Hy/P55F+apBL5y/4G4vghaEK0UxNGCOKUgmRYkKwUZtCBjRFCvyClSzFmgKF9Cz1lC5yxV5qygc1Yoc2ronBplzho6Z40yp57OqZfGqNwEspredT3r'
        b'RtwCVYFhA6vlPJmGSihWCkNpYehA3lD54DxamKIU5tPCfKWwiBYWKYUltLDka4oSFbEVZUuUZTV0WY2idv04GvVYMexHFLWa+VPOimU/xn8ymLsM5i6Puctj7oqYuyK2'
        b'lC3169RWiWbK8wYq+oppUaxSlECLEpSiVFqUqhRl0aKsEdEGRd5cxbwyxcJl9LxldN5yZV4VnVelzFtN561W5q2j89Yp8zbQeRtQav6dOiS1nuIJmqRoWhTNJDoiKh2O'
        b'V+QU3k1XpsyjU+YpU0rplFJ1JA8fuWuPl9IjivaIQjXlHcDQoUTR3lEoRFCnvspDiJ4Lxb3pZ9NREboLMWHVaUN5ltItnHYLf90tUuXu1WvQYyCv6V/Xt+5196hxHiUK'
        b'faRB+QSqhJ6ydT2pKr53r02PjZIfQvNDkJi9c3vmKkURtChCJfDsDewJVKegdA+h3UNG3KMGVv3xyTiP4+f6DcURuj3WoNxFnbVda77W5AgDxjUoccC4HuWLZpEGPo6M'
        b'0OO2VED4wMJhDTo8jfZPV/pn0/7ZSv882j9P6V9E+xehGg2IYiuKKxQLlyuq1tAL19DFa5XF6+ni9aimSlhRuKbwH5ReBG0vVvmHoYpaofRPoP0TlP7pJNEc2j9H6Z9P'
        b'++cr/efQ/nMmwoZir0Plt9Pp0Bxl6Gw6dLYytIgOLVKGltChWJfCYrEuKZZWK1avp5eup8vqlWUb6bKNjxk1UmuTlK1wCqTtgx6i0rPrsVPyw2l+uJI/i+bPGuFnDi28'
        b's+T2EqnGmBNfVtG75PSSMXHQAMGkDa0erri9YVScpyiYS4vnSmdJ13amPHTzxCxsUq4qIIShZVIGpNABKSMBZYqMLEV2KZ1RhjMU0/YzUQ0xtaMUxdCimBFR1jB72P+u'
        b'zoSa+fQWYzWLokVRTx4Rgi7MaqZ+5Onbu7hnce+KnhUjnilD04bib1uhNwGdujjwZP2PiFKHfIcqbgerY02wtoXSglD0aGanFg5e0FPQO69nnjqMl7i3rqeud2PPRvQg'
        b'sFPvoV8oxvT1F/cVK/0Sab/EEb+y4XyGGq+YTi1WppbRqejjpOG0vS9WRdseW6mGytuXURXUATHCMw0mnhbFK0UptChFqjPmJFI5u0rXdaYqnQNp58ABS2VQIh2UOBqU'
        b'fM85ReXlxxBkxd3zipPGPx3S7Jb1oLUyKJkOSh4NSn3dOW2cQ3nHY4/VnjN755ydg7q7p8JPxxRqk6m/7pyCwnsGv+PtJ18wYNG3bNQ7Ri0tI7+SH0bzw9BXBIThRte/'
        b'oW/DSMDc4WmKlDl04tzJinRyUbj6jzoFDExBXCoy5o6Ezh03orx8FD5RtOcspWcC7ZkwbDLqmSqNf8dDJFt4RjhgPOIRPNGuV91zD37EoQSezJtRj2CkTbKqzjqlWxDt'
        b'FnTPLWRIc5h1W0cZmUVHZt2LzEFfOYuVyBo2vm05nK/IzbtbqHAPl2nKWT068viBqL6kMZTWmjOhAz4jglCVOLg/pC/kYpgsBl0qxbG0OFYpThoRJ6nCouRsuX+fzjtu'
        b'HrKArnp5Feq3B7OHzHDC14oVGZkjYZmoxxpg9ekovWfR3rPueccMmykys+5aKhOL6MSie4lzVT6BA8Z9lgOrRnyihvKHM28XKmPz6dj8e7EFYxExNNmGGo0pGY0okbEV'
        b'AtTVhD5098SfrQgowqX7hMZMXbjfclj8YlyRAt9ezx5P1Dd6+PQKegT4RukRRnuEjXjkD5ndsbptpYzKoqOylFH5dFQ+Caf0CKY9gpUeEbRHhFRzzMmjZ6EqKHLITRGY'
        b'hJppA+3s9457gCIwgXZPH56FfqS8h94BUt4JfZWr4ITuo2IOGk5/JMRIzyXwSrxYw9pZlujPfec4XfRH7cbsvnbN2rLymvmVS6vvaxbXrF0wv7r8P8Frqh2aTZ0lMCeo'
        b'STyKeobZAQdvAGIfpT9toh5HJ7BYLHvs2sz+GY5WvyHelzQE1Bldfw6fQ/ZrTaN0kpPigWyqy4dm+DyxUw9cHZisNjmcxAGsALstQRcXTeiu25NdZnhsXj6624MmpIki'
        b'sDMdngCn1Q4k7EK4cP9KOz6b2Wo/sRgeT06Ch+qm5AXbwFaSDGisgQf+kBvsFzO5LYTHiak97KrME2D7qHPuCameiamZK7HRSWaCmpfbFXazqJLpWs7B8BRjQ31uLRh4'
        b'Ysa9Eb8nZtwHwJZa7AjFG33tQDLcxSkVoTV9DknOxy8zQf0Jwc4alINXrYjIvwAcxm4g8MYpmujmM1m7Tx4tgP0hPGoOOKxl6JPLFM0muA/cnFo4VNLUolnGqvXEn358'
        b'cWb179M6lZSrdmaKPw2v3Ss2aoHjlJioaeWn3FNUdQyHol4LzL+R/9aS0QzTWwGpVy+lRihrl+T3B7+wy8HR0cN3uyFH08SOG1vWtUV5fI3i+bIUGzepoySp9cbHkd9/'
        b'/OZ4wT9L/1kcmlh9cf+DgTNWX3ZafPTg7a/qOx7UezbIlhklGQyXHNv3/tuWY68tD9o6wNVSZn2bnpGuKX6Q8Oke0H2G9cHYiWNHEi263kzeqrI41XD2u/zf2Ie0q4Lf'
        b'nbFap/VBxkcqWB1f8+1vITsDk/Uf7wzOTYp8r3xHccFtLcuXzj/MdnoueFX+vYEP3MZiTDbuAYf1Fq+PG1pxvtnosng8xOybELOv3zhpbemi17F636n21jcEXyl1B3Xn'
        b'p73qcMXh9qvuXxc4Wg0X6P2y7JcQu7+93llpvczPIMDkhQNB3+sX6FuuVVmvK9QJO7rPe/X+sGWKmQYF8ZVnrQvntth7JryriPrI7MCNxK96ks52e2w2DC7Oeq9W3/tz'
        b'X/OBnoP77pd8f4afdwacfm3zwTMbG3/dG7O6wPEz2bpdbyzu9NO+eOS77za4BUY4LPltk/DWKp2iVd++/htYm9r2yHSsueJrU+uwufdeOPLtp//Yrxw/daOg94tX1vv1'
        b'jr508e7jUyGtIzbKfb7KFyxWzLd7O+e4/u7bJ369eYSX/W35vY6gz78sSmyee/ubVMWLgyub3pfcvLFdVr8xTHGkPvZdeDrm1A9fagc09dSF73QyXPfzrojK1Gm5r7zf'
        b'7yLcOWqXKvpyl0nQ9IADqijJtSAJdbH7RuRYwE87rm579FNk5/p50gyxn+TLzIooA52zGyTaPjMkJbVd5z952+qjocIfQ07fqP5Iwpcn3VnSlHs0+F5ce2b4uV8dJWnJ'
        b'qrR4qVnNy02zPne9F3jzzZKOc8kXLrXu76vcfL/7VXF707W74q4Q6uPlxjtPT3+r+3uPDxWfeupofzj6adyisqu9fzux/GJ357aPv+jcDZeGpSSt2fFL8vnMhd+vHxPN'
        b'd9v/Q9eJg5dj48+3nutde8H625yCnBd25K9xXV0t+uZOon+3sTS5b/cLX8z3ejHwsFuV91uPAz+wqeeMfTzOml2fPa0hgG/ytqa5zYdLTL5KWP7iuVnfnbtdmDHmYmAz'
        b'gzbUtuIWRS7X3tJj6/nZD+Wj/TXTmlb4z+j4bpttxs5ib9h99bdrZ/Yp31//ocsrYb/pz3hJ74dMNKn5FrdDeANeXz1hxvYHs0aws+KJZSOULyIr6vXxGoyh5DrQPWFG'
        b'6W3CLPZ3grO+zHZszRouQRhcB4fy1M50wHYofdqYz4YDThlnFjPORfBpOTxJ9kwXw6tqi2cDbWKLvALFbXvicLY2mv+Ujaf1GrKg1yv43Y4VPFFBNq1Q0lcYzx4XwYEK'
        b'tcNdFlr4R8E+xpFCvQOQqE0VTVmpoNlpAZSR/RE2POk0sdIX8DVAKzgNLzFuIOABLrgEjgEJY0J6JhpIdNHbix4CxicP+kJdEzZ8zh/2kQ80BLtTdZNngc2wuYrPonhr'
        b'WLC9DDSRQtWAV0BPNR8eQMWJrRkpMOgFdjP7K/uTsqtNNdX+i9agmDpr2OBMuRmJGA2wBaQ2RBUGbqktHf3DmU3bHrhrsa4nqj52Pqscng/RRqIyfgrnwvbqtPVwC+NZ'
        b'CMjAYbUTheQFq6ZYwYKj4DRjBlsNmO2pqsiyao9E7KkHHMBOTQ6ywJa5LFIAK73Tp+7CgTZmIw47c9qdwXzJUVQRTfCiSMdzCv28P7zK7GH1wQtrnzJkzA9hKOingcti'
        b'Zms2DG/F7dQE+6bsNEH0ksE7bAAHdd1r+U/8fMBBtYeHmaCvtBo7Moe7fMAB7J2xh4UK7Dw8zmxWb4IXwGm8gb4LFdrp6dgX5SUWaDNZQFTXeZ2frmfqKuZ1DcrW2BT7'
        b'quxevA4cZXYoL8EB0K4LehzA7pXMDq2WPrtsA2Q2qfTAZSukeXtjnnYlBU6CnjXf4hHexAgcmaA9eJrzoNjxKdYDizJmN7MddIMt1cZQhreFp2wJr09jdlTbwADYo4sd'
        b'YK2e2BYme8L74sjmpG4yJNu+CT4aFLPtWwJPM8cMF7LgNtSCRfD6E19g8DzcTnZ9c1AB7AJN8DzYPMEaMWVjC7TDLmYbvAVuAq2wCc9YQvNQS05nwU0s0EmqyRucnEWc'
        b'UhXPnzCEhT2gm2GkaAdXYqbyLcCDsIW4V5uHcpOQrTWdVL8pO29kt5NFYSSXeTnXEZxfRD5DiwW7MZCzA25VTz60AtkLAuBmZvN6W/gibH2snniBzcKJuZedOReeBheX'
        b'M4bPffao2kwK8MYzqnvsskYnhQ1aUOd4lYhiwLZDyeCJFtjhlRRb9gRv4V2oYVKzgdgJO6xORv0rOJzxJ13sEzthV1T+tmQ/8zg8OmX2BPakgSZNyqCQ42ML20iPBNrr'
        b'YHfyRK6Tk6fdCTzKAzbyUJd0uY7ZGG+G+3g4rXS4A6sVUngZPsQ24HAcUFfbRRp0QZ4TbBLawucZhgzMjlEOtvyP7k9q/U/vT/6OApZZetiz/8w6jCw9yCZkG1qa/Eg2'
        b'IcfXxrEoW8eOuUfntsQSc8yTlhKeysEdE/Z32Uo0sIlnRFuE0sqLtvKS+49YBaFlc1uMysbxifWrPG/EJkTl5NwW8z4224wfdnnN666XMmkejf57zRt1LFZYFz8UBzI8'
        b'+0pxIi1OHBFXDue9VojWvrMXjaZWSjQUdl60ufeYwEfu0s/v4/d79nkOudzh3+YPx9GzskcFOYr8IlpQJNGQrKXN3VV8T2a/TMmPpPmRI/y8obg7SbeThlePxuShMKvb'
        b'DFSeYsyaP+IZPVAzIlqIhBLdFSmT5tBJcxQlFXRSBQpWR5t7jAnw/oLVoNUt20FbZVAKHYRtRQXZEzk5unWLOkVKR1/a0VfpGEA7Bow4Zg343QobDFOGpNIhqcqQLDok'
        b'S6I5xveXrxnijvJjR/gFwzMUGbPpxAK1LALv3qCeoCe7NyOCtCHeHe3b2ncMbhuoc3po79Jt0GnAUJSjSuB7MnsZoTQ/dISfNaSBLWiH/Ucjs9SJovCE0tybtveW8Mbs'
        b'nGU8uWm/XZ/diHukytkDu5WQrRl1DpDEqjy8UJw1bYaoFvrD+8KV4gRanKAUp9HiNKU4kxZnKsV5tDhvohoeIk1ACoCq3w7vkYzYBQzGPbR3xdk9EVHFPGDyZx4p7QNp'
        b'+8DfvQim7YOV9hG0fQR+odep123Yacj48hixTx7gYXL5WwaDBsrAZDoweVybF2gricNbNNYzHxusZFkIv6Pw73gZh3Lx6E7rTFM6B9HOQRLtMVe+zKVX1CNSeoTSHqEj'
        b'Hmm3OUOJ0GDUNV2i+9DKTmnlN2LlN+YmkMV2rR9xi5UvGYrqW9GW8EiDchfKEhnSbKUwmhZGK4XxtDBeKUyhhSkjwgUKbGg7l86Yq8xYQGcsGHUrlSS8Y+X00HOmPB9v'
        b'2RUOWdyxvW2rjMqlo3KVUYV0VKEkThrQlq4SieVxPfNGREUD625tGNygjMijI/KUEUV0RBEK4d+WNubkIQuWr6Odkofi0I8kZowvlBWcscVW72POqFC9xzlslzBVYOiw'
        b'QCXyecRDNw/9QshfSey4FiXyl8QeTR2zsZdaHJknqxqx8X7f2b3HUmXPRxE9olljPn7y8otWKmEAioPuH4ZEMRffUGyXGFZbLPp8R8E7zmLFzJhxiuWSz7obo8jMeylZ'
        b'FZn8iIPvVem5zAXKT4MS+eL8mJY96pigsE7ArlecO9a1rVPaiWk7sTzpdbsI9MxNqHQNoF0DRlwjB/wk8So7146Gtgalnc+onY/KSyzlndBT+UVKeffsfR8GRd6yG7RT'
        b'BqXSQanDa15ruNug5tkPXIAD+KmcPLrDOsOUTn60k9+AKd7+o52iVR6evR49HvL8/rl9c5V+8TT675EgjVZ5BstKe5f2LKU9Ywby7nnGyNhjXr5y37NrHviGKyKyR31z'
        b'FMKccR3K21fpFTniFYnfis+sHXA4Xf/Af5YiumjUf47Ce45K5KUUhdOi8IEqWhQ1lHOn+HbxiChHJZz5MCTyVvhguDIknQ5JfyMksydZFiN3UXnNlDUMGSiy8kYi81Tx'
        b'iXfW316vyM6n42fLef0GfQao4/GOGedRoVksVOh8z3EHyiuW9a0r5RWiCMkd9cxTuOc9tHVq1/26GtWJ8BGHshX8SFjRtxboF2qzxqYFoF9m48qIAe2n8P6A3P93BxSj'
        b'P2xc/TfGj7cmrIvxNtUaDP63wtbFVti62OpZzAC+wxmdw6Zn5qs24utN+Gcz/vkJ/dyfXowZU0trmN2xYkyPWrl8ITF8XrUF/xzBtkhOHBRUU20We19vqu3pfd0ptp2r'
        b'PHHoRhzvZ/yzA/8YsDCAb9Ks7L6m2nLrvt5UM6n7+k8ZHRE7FWIeQYqJP/1/74QST2f/hPF9otbauKjWniKSDsCV1YBE/QETvuvpG41bUy58hZ7Du/qmbS6dHIlVT3lf'
        b'9KDpYO3t7IEld/3orHx6dpEicw49bwFdVkkvXqYoXa4IXKEQrbynX/WYXczSD3pM4V/M0b6KNU6ePIrhTHCux2PO9URWYwxSd0vHMSORytQHPbIUNyahJ2Z2Y0YeKtMA'
        b'9MQsqDEePbF2HjPyUpmGoifW4Y0p6ImV05iRp8o0Ej2xmsVqTEaP1GnH4LTjmLTVj3DapmLyxMRqzMhVZeqNnpj4NkY/CROFw0Qz0cztx4wEKtNw9Mg8ktWIBwILhzEj'
        b'IZOShbgx8YmUXlhKn6lSpmEpM1hETBuXMSNv5pENepT6rRZL3+lbDZa+9WONIo6+82MK/46TX4YpFs/5rRdlVT89NTaqRDNxCyjjli+GkqfQqpOstNgk7oAmMVLCPOKU'
        b'2ipGu0Jz0mCJ+5cZLP3BlkCP+r3B0sK02jR0bQmvZ4m9Z/r6+/iJQT+Q19SsWl1VW42WD3K0RLwAr6A1y+WNM+FFQy09HQNtfV00JW8EzXAvPJCdAVvhoTwehRZbg7q6'
        b'4BDYSfaj3UzqYRPYi1ayTbBJ4AX3CNAitolDmcCjHHi1UqMWq3l4BdwsxkiYeMqH8slR266IpzmQwOiHA7asQlF6OTNF8CroAq0kWrKli5hLxcF+ypfyhV1gC4lWwAqe'
        b'yEsd7SjHZjVaue+CRwlNL9xfD9rEbMoKSCgxygUMEFx2KpJyH8qLRGR5xFGmLkjCtUKSFXxOAE+JNSgwoEnNpGbqppCsKmujCFqXyWwayqqJgwrkCrwaHUuysgWtkWK0'
        b'vDsA91F+lB84kcvAt7eDi2nMt+GIbMrUhANPw7Pwqn0iyQ70e8BWMY9ynEX5U/5g+3yyGx+8KpnJTB2JxYHbLVAhetXi2iQ++66LOZQxOE0FUAFF8BpR0HhwFVvNkJia'
        b'oHMVOAUPUCZgEH0cOAEHSX6OWkAq1sRWGE1UIBVYWMiYPDRjf7OCVNBIRNV0Illehc+BvUyhdMaYg4sUFTKNCqKC4PWZtWQf5Mhyt4kyQeXhSOoNtMCT8Cofyoio0+BF'
        b'L3CRS4HjsVQwFYwkamNsIC44wfPq6rZnR9qotQScAieITceiyDXVXGrDfGoWNcsCNDGWFc1wC7ZUSIe9jKo4kWpAYu6AzxExQyMCqtlo0VxMRVPRoAe2kuouDAHXBEQd'
        b'OaAzdKYTqYOr9UGk3sAheGQhGr9TM6kYKgZ9TSPzaWdB8zSmKPH3aS5gyrHHB+W2WZ+IuNISSqpZVPF8KpaKLZ1OqtsUXlpNaptEmoZLERwG1+HVdUhlCcPlFXDMqRr7'
        b'nr5OxVFxoBXKCeesObiFi/LKGvJlTIEyjacXF8tuY0bYy/A8OFDNoUBbJBVPxZeHkZYHN81B9YvDgy2YahhcR20BdHPgJrATXnVOYeL2l8Ib1ajmN/tSCVQCPOjGxD0F'
        b'tuUxFcFEDWVqcQAV8tUV8DqjpNIMe4iqv9aZSqQS4fl88rHChaimm4jAWGcWkDqcpw2vLge3GObrHeDwYgzRxGhIKolKikDNGePW7UBrLIr5PPOVaj1nPhfXJ7gIWhjj'
        b'pgNgF+qQLrIx3/IFKplKhrcyaxlEFDwSjTJGCoVEfw5eWDWhC7vgDvK9Ncbo8qIGho0dpFKolPJg0kZKQGODWmjyyavUFZuLad7AEUbu5+BZMAgvsigX2EOlUqlQ4kdy'
        b'DW+Apyc0CcUNJa3kcD1pKBJSUrGBGILLw5OsNCptMapdrE02UGo8qUya4DhTPUAyD2V6wYgoRlg4BnpysBmVjEqn0itBM1FezZA5Ewql6bAhTq0QnvFM+TSCbfAGvKhJ'
        b'zYcnqAwqA5yEfYz10x7vxUykWfZsJzCobl+FsJtRw6uoaM/oYvfpmlQmlTkbSJlivcKPZhRpM9aGVbDZCol6AMWMhZtJsRaBwQZdLrUOyKksKgucBFeILgSsgntJsZB4'
        b'ofCsszrHUNhEjEhAy4oYXTaqUSsqm8qOFDP2C2dBD+oxm+Lz1Vqk7iYn9GAn6n6I7p5E7aZPV4NaibLNoXJy9RmryWOwMRdF2g82qctW3aerOz3UGUqYCr0Eu8E5XdQ9'
        b't8NdVC6VWwEPkvPVFaAVHBAU6pMR5LlVTK/nokEkjuDDVl0eNQPsp/KovFQvpg86gBK9OTHmbF4FOkvVVQIPazOdczvcrKGLKrLJisqn8sEW1KMRTOTW9UWCFVqkR0cz'
        b'rgAUpRxcIz1JWOlqXU2qik3NpmbDQ/ZEZQrAzZXqQuGA46RF4/Lc5I6KZZshk9NNd7gNNGFHuFupAqrAEeVEKvcM3Iuy51L+eVQhVQh74CXm+b75zqCJjR2lU0WoIq+h'
        b'8KR0b2aBs3Afj4rJpDwpz2DUCvDjtSKwH+7joKYWSnlRXqA1hGj4jIVAlk1RS9wpB8oBHkBpE03cBE7Ph/tQQ70I91ACSoBGlF11BoWCmmwWpbmecqFcpq0hxbo8ejHc'
        b'p0lxKylvyhvumMF0MDfC7LCNEbheTAkpISeVSBAOr67KRvOMLnCFcqVc4Z5ivg6jps3zYYd61MGFE4pHcNA9H5XNTQsyvmTUY/My9SyEGXYN4DlUS9tLSQrucHPok06A'
        b'Kd4mjhjchFf9AkjDs4dnZzBjtj0LNPoxgwbqakl0HtiHirVpsp9eQHr65/LgVWzkh0OIwPHZk10j3ML0qtUrSOfWzEwNpB6ajAhwM/oEsB8cUI+6g5VMgF1c2M0oNfnS'
        b'BSQN2wZ4VVhNdESbCy49aTiasxgVuQ5u4VMkuwl93YNaZBPch3p0Eip6onFdjeOzmMFfBjqxE3ZsIZggYmvNpbQw/nQzPBLwEZlFtqyK5OsQC60PtbGDg8ZiHapk6dz5'
        b'YsZsa8RNnzKn1mpzMkqEDulzmIdr67UoIypDgG25Dvh6Mw9lGiaUMyVnaVIl9V+I1A/p2diIWpXGjiwR1hRqMQ+70g0oa0o+U8+7JOVjvQbmYfMGTTSjNc/Usi9JCSqL'
        b'YB6W8I0peypwluHKkpQGKyfmoVONLmVKrY1mG5XonVwQxTz0djWl3KkMXf3IEusXXfWZh8NhmHo/IVcP5X5u9lrmoY4dB32mvQ6PKhHujsymiPnt4kAzpJsZq3TtS0Kv'
        b'+zpRfHZOHHkx5o4/YCVlEFmytKmwjgn94gwsq72Jjn2J8JF7CfXR4Tb8724EyaC1Hr+dvZBnX6K3sFib+khM/n0TQfSeh6Yu2/FwiOqDWkGtaIhST8KiQK8AG0LqUGup'
        b'tb5pjAmsLZk+HMEHVr9Tt2l45gFaKkiWhtVY/CEXCon/4tpo5kPfXjsdFcns+RQqEocV/szDX1kFlJxyFxuWlBS+O3M5+tC0tMo70d+wq4VovX7J7+tt++9WW8Wa/u1a'
        b'0d5zrxwsWzezcKngVfb8xNlsbsLwFpuDgdrJC1Ym7Od+eyC7+cyqlh4gm9cRuOOwxwyzF12U7e23GgX5p38w+zp1T1ymQ1SO361PPrjRe2vDW11vL/wtQ5HXcKak5b4y'
        b'wSn61ZKDLzvGf5hp3yRx+ijT8SVZi65sb9P4sGX9hd0aYzFNc4Dv4Bb/dVpn3p9vPaac85H77r7H1sfc9rzH+zr2eszNZpP3E6/PurlTOays2lnPWbF3xTszf/T/h8Pb'
        b'L1p8LfyH02vvhK5jmd193Bd3/r2RmxtOPGKFvxD/g/mhvs2CgZ1LfuB2hL8cMZJn5Tfb5pLmS5sP/9NG8sONonfqF6/aoAhXVH3W/b3UpszVqWX+hy+//8N7r01bdqjt'
        b'aPPAK+uWLN15cRv/1e0rjpz6LXov+KghzmX5Ug2l8nWvU9Xbv7CIs57/wq4N8/htrSkd4V3+/o9iH4SYf/nKB2e9F35/80LBoYXTXql9veDdlLQLtx+csEt86awkIXlV'
        b'w/dWn/ZYnQMHLoFDOcqjt3pau+tYf5/RNf0H64NLp1ldsy76JvS9j5wF1a3Hjx6q9zL7zjxgzosHbc3b+l3aDr37auXJOn2+flFTluTD6QHHgksrfEJdeEu/aAsbbbTx'
        b'7j7y6eGLn28zG915Ued0z9KCv0d9cuu1LYvL4/7R7NiVXRUi2LP6+wNnalbNms5P5vXPedFjW+dP5w02/nze9/Qn7o+Lk/q7Lu62veZ9usShzebM0Y8W5zcucdMNuZ65'
        b'/urCS7MWpn8V91UIffbN7tdMrlrldLd/njCWV5D+1W/f/5ayLXZpQfrpCwPLPv7Kq/uTFxdWhi29X7jb8o1Dix+mf/rw2L29vX9748T2VxbFh9nYwu3nLv52ebRSPl3w'
        b'xol/XOPr53csfvf2B3O6no+rVz5oW7N6d3XNrtK3B14+9bHUp9zt5b0V+2zjwz/NurP9pTcMd+/0qj30VTa/KvurH7PDTLvrFO8U/vCeymZ8XdeVw6GvdBTNrS6uTX1+'
        b'+hVRZtSSnbfyLoBe129Hmq90Gdf8/E+7C8nvar6U7XtAuGvjxTCvgrZX819I/lt/6qHHFf8cPA8iRv95AW5MMDkffCz5jJ1RvOqNxx79v3BnsNrlxgEDqXxD5jT51Aw0'
        b'LF5MhSdgc2pKOo/i1bPgiXngLHMavB00+8OmReA5hlWYm8ACF2fbMSfNx8F2bBi/G40BydiJui48wgFtsI0N29SnlHNARza86A+wmVA/WllwdFg+VfAIOVfnWFQIgmLh'
        b'bnA2iUdxy1jgui6POXY94gXOYzb5RGEil9JdzQZn0DzyCBwEzDEzmlhfBl3JQsYwCUpzGdukBWAr+SBsvH9cgMaN83C3F5KKW8tCa7C94Ao5qHNmQ5nACB7zhLt4FBtc'
        b'ZOUBOdhMIi73gtdg0yp4a8IuiRglaYPtzGnsNbidq+Yl4FF6GuwGJNSNGg/m5PswPAYGk9GM4xSxgEC5mmFH9vstiNEIaM8EW5N5+WrERNScKOZDToBbaHLTVIIWj83J'
        b'ieAcRWkEsi3gZVPmePoKWiQ8h1n5bS0nifMxJ394ON/5/96q4d/YZcTz4j+3g3jaHEJtClFdOn95ceWy+QvL66Zck2PGD7gMAU1NKouaPovVGDvONjI3UBlZSbLHOfjK'
        b'USSrZq5mRgyZkKuH5C0PX5G35Iq8xVfjGpSxNXqvyVw7eaIQ6mu/SBYKRG60mEDazDUJpL5mApEbHSaQLnNNAqmvmUDkRo8JpM9c40CP1NdMIHJjwAQyZK5JSuprJhC5'
        b'MWICGTPXJJD6mglEbqYxgUyYaxJIfc0EIjemTKDpzDUJpL5mApGbGUwgM+aaBFJfM4HIjTkJ9MiCufYWD5mobOxl1U//+drOCPvnfOSoJqHGfuzvmXipZlgdWty6WGqy'
        b'b0ULRzVt+iFBq0BSKnPB5zMtgtFpfo3RKms77Pd3R2pjbIu/arr5oaLWon1zG+PeMTZtyZOUtc4dNXZqnPXA0qtFA28X20lWS+e3rZVpyFb1aNN2PnIfeemAY1+F0iKs'
        b'JUplad0SPWbjKPU7NkfCUplbEVJWf5mDLLbHTR7VI6Cd/F83DxjnULYe7wsCJYYqe0cJT+XkJtEac3DtrJaJu9bKHTrr33CYKYlSObpI53e6SqLfsfNUCTxlVXLjnuqe'
        b'wE6thwJPqZbKzlG66PBGeeDA2hFxPD5kxe6+M08YoqAoiL2LdEGXtiyz0+CE9rgZ5eiHis6Z32MsDZRoqcztsf/wdkOVk0AWLcuShqHs7Rw7xdK1XWFyX9rJb9TOX8LF'
        b'b2NQnnHyGLmfwikIB3JTWTt/q0GhvN2PLOuplgeeaRiopr1m0bbREg7zCX5ddW84+CLx3YQo+7Vyp84NI25hA04jbjFDJpJYqcPhBPT9juKHdg4da9rWSGuPbEB5mduo'
        b'RbJ37Nbs1JTxugxQwTg6SzRVLnyUZqokRuUqkrM6l0jiVY5OkmiVo6vK3UPKU7l6dFd2Vsp1B7JHXaOkHJWTq8z4eIDKma9y85ByVe4C2YIeLRyOL4vqXCjljLl6yGr7'
        b'qgdmXlw34hU5lDPsosjIvOt2e64ir2AktkDl4SV36OFLo1UCMT4IH+AO5A6JBwyHp40KUhjro+rj61XuIpXQRx7TkyKNxRezepKksY/0KfT2X6U9GluAmpGL6IHAc5g3'
        b'XDq86q7OqFf2XZ0hHzkPez8fiLpsMKxDezEgggJaUIAq2ckdE/rKXQa0+rzuOc1SCbzlJnJHWXBfzUD8xQaFIEbpHKNwjhl3o5zcvtakXHy/jqCEQV9rU5bh45qUlfd4'
        b'HYsytf8RvfLOYVVroO7uJWPzFHcj5rBO5z6nctnCZzqnI3RdJU/3rqsOYwz5lG712gRIHDsvrk5lsVjGX1Po51kO3t5C0Z9yy4gzJlv8hL9I83duGbWIx1iGw4iq0Jl0'
        b'x6jxl7lj/MOZwx8d8lmn/TmBWwmWmM0QuDVyK9j/AxRuf+AF4/xBOl4aWfVwivDSVprAQkvbExsLqFo3Crt6qWF2VvPd1Wxe7gnCyMTsBDwFSeRRAes13EGPoHKbZj+r'
        b'OgBF2DX93pG/z8S0fdt8juzY3JlwdZ9PUyuLoxd5dvtIs57Ly959pqdezziQ2nxU77Ze+ydU2iMto5a7fDYzx5HAzhA02wNbYCvjx0EjlG0GLoFegi2tMkzCyFLYgU8v'
        b'CLr0KWxpQCyfPUUj8SA+Mc7rli4qL11SXLm8rHxtnV0xdl1ajHlkn5gyTAlARn93ihn9F2WgljK9pWqvn9p1+v7EB5auCrcJ7n4z8xatKeR0vPusyj9rOGhiqm4fTNM4'
        b'jpvGfyXIdJ0nVHXfLcxA7cXwWZrKBhST4QPalh2ZLEzD8EQupVEH91mydcAOICV7g9XwJDgsgHvT2NFeFNuYRVXAzUQhhA2MM0dv//4NX8b5UHwWk9jFGaAxOSUtrQQ0'
        b'Yu4mrXR2NZoJM4RwN8rxvgOl5e36tpaOuxlDrVgoOpytv7KKQ7HzvrzFouLryAbBqUqGO857hnzWPHtXain2hF4Rz6NQJt6n9Ci9MfPgjZuoajy5rcuZm51b+90aDsVx'
        b'D+exXDbvIrntWM+4DfTOq5qZKVrOGLNssP5b8KvvsTGPmG4J45by/lINfBJo5K1hWCYNjWXCHfr1ve3UezxM4Gdwb3o13od8GDi+Yvl7H6C4rpT54g+ILc5j9rrsXP3V'
        b'+itz0Mz5F46Itf+6aTWuYNNj3xD8Y487xi+b9FXWc953fo5sSVRjfdifVj5qeFd46Ye7qJ1osti+W+eQfA3elxgdHcW6QvHLzpFH9l2vdkpHUVl7UB6yRvLowLHCjPlN'
        b'qNeYS81N+phIt/hjtH5qotHVu9S2j3eTZ2NvD/18vIlGUd+jtq+9RrazcnLgZtiUiF1snUeLhmYxKiTQxE6CfbqV7pffo6ofo2RP/axRm5O65M1Io6NzE9/4FPZNfzPx'
        b'vYy6BEOHb0eiP+EfUmxsyf7yuU7f96X7XSVj0VLF2bs9Rl873bMbG7uszPNIjNN85XrDNx++srZ45O0fBaE2oR/o7nj30Mgm6Ta+rdfLJ0wVdSmZK7o+A6blijjpAydn'
        b'SdU33I2GrxhrXH4Qc3PTwYq8uGUz9pY/2P3Gzbjh7pyQ3wJO9+98Y/Cu8UpvzeZDxSwPl83UAaXj0PvlbxRHaUZsv7Z7lo53wcn2tz59o7O8dHtm/G/8bbYfnflk+H3T'
        b'+RVB7oefs1VQ33wQ9JnltZdX7huzn/3N5pcSrYPeX1se9O6XdaZffVYZqwNdNuZ+9ItOW5+82Sb4x+tpKZkNX+fuij7f9KZ4geYr+xfsqT1870oSnbstp+ntVcVVd7RX'
        b'HQq+3PzzL9Kt+794+2Zw6RuJmksix07fHq4WutcmVX9pk3bucMHP7R1nHv7y4fLFTafKDD6oivg+6kEi6+0vTtnlbRxv+c2sYUPaP3765EPpwbfXGkRce+v2J/+weTnv'
        b'4Y30ugcvWLiEfP9C0MCY65cvNbP2PNje9ObmpuAXvol/u3OG89/3GfyttP1L85+9v1r5vUb1/c1BY6nKn765uWtR3YqNx+hXz199aGP+y5ozNbmVDzzqxQ2LnA5bO9tG'
        b'/0O3r0VpfWu7+Ae9Ne8e614Hc3mhxeHcgJVee1+M+CWj/TmXX/lGZF1cqeGfzIe7RO4alEYivLqQ7THfm6wH3cBe2IWXg3D3enALE3JpgRb2CrgTMAwVs6EMb7nCXalC'
        b'NI75gG3LWeDsHDWU+Rw8NzeZDAzwiC3qpps0UexO9oZaXYLlBVf0plXXrF6NOvlGfQOw29AQXtCr4lEz4DEOOIrW+UeZRfBmH7BbMLlm1wF70LJdA7YyL6+Dg/AybEoF'
        b'ZymwFRxGy+utrHhzWyJcFexoECSpF8ca4KRHFtvUHe4k73jgELyWPLlwtoBn0drZ2JLZnjgG9lBo2Y3y3KRFstXWZYN9WeXM2/MOmGCuiS/C4GQNcGBRCdsJnALniECg'
        b'F2zOmeQ3gVeWYX4TIHMiJWI0Gw7gdBsTU9BQprsI9bR9bHgUA6KJUGhINUxOTEX98oAbKeu57HK4t5y8mw9awpInvBlpgOPgDBoJa3PURQSOoQESU9al8FEVTgcDIWzT'
        b'wHK+2f8B2rcaS/svML3qRfaTYa5uyjUZZm+xmdGtIoPF1bdAy9fpFo2xKkMThaEd9qBR11ondR41c2vh4rv1reulAaNmghbumJm91HTfxhbuO8YWEmcp756xq8xRZWp+'
        b'KLE1UbKgo7Kt8sgSmY88R+kXR/vFtSSOmsa3sFQmpi1ZLfNb/CTxIyZOY6Z2Uvb+dDSAY8ci+9a2cB9YWEsypVxpbafeqIWoRWNshoPUodut003mLo8bdQwZnRGKFosz'
        b'zCQcSVQbT1LashTdmsyQuOwNlUZJS2UOneWyaDmrJ1aaJi8fcQ5RWTq0RKssbaQ6tKVHi6bK3KJDs01TqimbMWru3cJTmZhLfPYGjVm7yVi9mj2aco58Ke09ayhu1D15'
        b'1DqlJVZlaYdWjWZWeElXSNt5yZ1pO/827kNrh85omWZXCm3t3RI7ZolWg90VnRWybLnLqGvgqGUQimRiprJCi2NJjiSgJQa7p6k5EiTjyMp7dGmrmS0xeCqT0JogyZHG'
        b'tBXdM+Wr7J2lNZ26LVEt5S0VLYmTMx2VlV1rzEOUUq5ULAll/KeMWnmNWPnJfVG6ZvbMOtXegazNOLLKHsOBGaP2keiZlb3U93CwytmlO64zTjZTPn3UOWDAgXYOkcSq'
        b'HN2YdZqrGxE8Ry4edQ3ASzRnabbMuDNXJpaGyv1GnALxam1ifTaujdYySEFcXKWomKUpKB1nfndqZ6rcdcB51Dniz+9TOlPk5qPOwejOyPiQZqvmfu3HBSxqmtujQhZl'
        b'ZDqpR0+r1+9Uz9BUYWiPnklyWzAztMrErDH58UKcisLY9adqfaTIt6n4gEQx566YlxiqyUwF9e5zV86vWXSfWza/Zv597YXlNcU1lTVLn81cl8App3pRYaaPl8jK6klb'
        b'MtVRr6yw15RyPFN0+g6trJyeZbqYitIsZU9ZKkyuU8ooZp1CmGF5aEVFVXAmmWC5fxkT7B/opicFmEI3jWahGMYQqQX2JqdjuwpybIeZI3fAS9NAPwduqYW9ld+8Z8cj'
        b'e4EvCE4d+Xvo0c07Ovd17uvZdz+9Sv+9xa4a3loVD1M4VFos9/ORs0x9cX5f9HipNNmJ6eP6e9KPPX1LujI8sGKPZ4uyiMezMlnlPZNAhV7glNWBxqrLGADb/y9QsGQh'
        b'XvL/EfcdcFEd+/5nC71L70sTlt4UKSJK7yrVTi+KoCyoqChYUUQXUNmlyAKKS5EiKtjNTIq5N4UVEjHXexNNubl5Sa6aYsq9L/+ZObuwCCZ6n+//9MOyzJkzZ86U3/zq'
        b'9ycnJVzB0zz9UUkymeCXCurH3OVops1fZpLx8fF/OskzBNKZk8yKy59f8xWTTF+KcNr0bZ6nyzJy9xz5PtFzUyeLCnubnZv1rxeaPt706ePNmD4pCPzjQjR9Gob8EkHi'
        b'B+rWM+fu0ovO3XUyd9Oekyo/dxvx3Bm9mrnLwXPHks4dg3azzGH/L8zeDGWHwozZU40jniXGpbBiSuY0Ac0sJHOesCTyWIiBBXP1/H8rU5se7N624loaKXyjANuct8Wg'
        b'UYy5GZdNm2Kv+jCQEDqxVQ2NYE14IEX8ONbbrk3AhgwK7oMDbhQ4RUWQyv+ci43K7uXKnLQC/2gTingSaoLL4FCCCzzpFBGJE7qzKMUVTEYIqM7/75M1DF4zqnKIua7p'
        b'T54tbfXzsKai98CdNb0x6i3OQfPeEaxfbpQSXAq+XHlgTrKgQCNYdWz9XHFUTuRAgV+wS6ZGcC33sKOBoNtoLr9xZafJmwe/cN7ifGnwQ/ekQQ/3rM0ZtZnBW1VsRj+z'
        b'ftMiQbTi/ki5UuL+v7r+GJfMX6M8VtF26+Qbe7s8q7USeut9WwYPbNb5dOWlQP5u473GC1ZRfW9YzdO7w1WmmdAL8Ao85eTiEOHCRNxgI7gGDjJdwEmK8IOm5gE0zx4f'
        b'CRvBCSnTvtWVjtQ7jUT9c8S7AfHt8WAPqMNwxEcQ54yY+TPEYmWTYCK1dQWDc1IcvoAc0nZBALwOeghXDQ8htnrXenCSab1lPdHX8CLhNTgEBuVtVqj6UXCMNOvAMHSK'
        b'ICYluJfJ9mEgebQX7KENT3uD7abQ+TCWMLGEgT7YzVV6kXMR70mpNYfe4eqYTG7KylmHD93t0/4i+7uTkppzMHk2avCr9asPqAq5p20uyGrdINwgth+z8BzT9qpa/Jm2'
        b'AX+zwG5MmyPSkWjbVC2e0NVHFefofmZoLkjH7EItm8/ge0xo6zWo1aohJmqxMPWumbPEzFm8bMzMbVzb/YkSpav3SJnS0DkWcyjmSNyEuvax6EPRAmWRt1BrXN1hQteS'
        b'79ngU+vTEFAbIGKP6jqLSu7oOleFENZCjugoFX+O3439uzAfZCykLAJNe25j2jNtCFbJkZ6nvJcmPdhZbdq+V5H+/g6HEpzQaKCyqZWMLGolM4uxksWkUqgBFvpRRz9K'
        b'OcxeZo9U/1lFEX0s8QDHOtkc5SzWPmUZsVnJZlLZClnsfVSWQq9ij5TUrVQkpUqoVFmuVImUqqBSVblSZVKqhkrV5UpVSKkGKtWUK1UlpVqoVFuuVI2U6qDSOXKl6qRU'
        b'F5XqyZVqkFJ9VGogV6pJSg1RqZFcqRYpNUalJnKl2mg0sObXdJ/ySh1SwyIfEeBsHdmYnGYcZazUQbWwPlsFEXUzVHNOmblKDtfyI6XY9EIc9fGLi6q8BJYQunQxZyN9'
        b'iUNywbhOu85lkLNs2lmiIiPkm9DHCWW5NACTk0V4ApXJU0XxVfIEv+yd1kP8L7IwvyQ/vSB/ezaPpGSa9lb5hbwSHNXiqjrjPr9N6cXpGzl41ftxcJoc/I1TUsRJp5tY'
        b'GhLGyckvyHadceeMFT79ZLOIK8VhwvMSlhGqtjQCyd8uyVIcFHAOVjnDPnjelUGFM5R8IsBVAp+iXxiktmlzArooq5mojLWJsCoWZ0Df7xrpjJjXTI6yOuyGrbSnZIUu'
        b'OITh2wuXx6IzEYO3l8AW4tYKuqywf/7RGHgsOpaxGBxBlFzI3BEGhsnlJFCx3Skqls7S7cSgdO0Xgw4WbGIW0HkG9uAME9GeUUwKh5g3hOO0zGJX2oGxEtQroiMkhkEx'
        b'M8CeQoaHJ2ihkXFuqGREu4IGUEVSujMotSImFMLqMMKIr4XNieRggYcwXDe6rAnOgyuwlbUE3oC0cyxsgp044fy5CNQ13IIWvJZsw0qFB2AlnVFgJBbclGo7YhnlUIiO'
        b'oGHmDvNcotCcz4Pt0ZGxjugqE4rgVaLOxP0FB8h4bTNeFx2TAGojuVPJBMJ2027AnaFwDwbqzQXV+KChgXrBadBF+8Xyd3jQKRuYa8HhHIYbaMwhHdoMKrHVA+cTEcEb'
        b'SDIiORmcgJh+Hz486Ea6C/bjaPTJ5ArR4CDRbYOt6AzWvs+igtJiUiw3U8TxMzYnFadpKACnsOPofl3Cs+xcyaaUHVZgcPiCC/M2U1LxhhECr8mSKIAacECaSIGkUQCH'
        b'SsitQauwrww6aqg055oAL5rdQcNSBc7jvA7Yr6aLTZHEDuCKMu1R2WoIe6eldoB1G0ANK8MOdtJzvQ/0gH70WJzXAewrpFM7gPYo2t+4kc1DvXLwkU+QIJd7AfagdUhU'
        b'gafnZEe7RsXSSReYaElcdYci1hpQkZ5/tfF9BV4zOg8ONf7zTNLVQuCud1HXXrsuqHKp6IRj6dcV4/3/aHwj49EtfvIJR1/zK8LrX4WPun0lWH1f6x+lA+aGpns+Ur/8'
        b'3mPfpw90b+94Usm0nVN76G+uQe8mhVr36IT+peA7jqL6ZUO1NTFZ/tfWbRyy6f7y+Fce5V/lH8+ouZH+Zd/H59e/bufl8Y4ouzgEnnlH2NA5R5xw69Dr83R/zLz+vo7p'
        b'5TWS2w9/9B8ZfCPWb2Rhtf9Pf+1o+PjuzuiGU23RAVe+Vv/rrY4/++dEuXw7KnqSP95WsOYNs5R13n//yTipf3Td6x7mUe9zjmatVhq4svT2yGYv76S/+Am+KD4W91nL'
        b'X7evj8tv+/g7v4qowQ93vhfj09b3GiwuKFb6tbci1vnr5ekJZ5WuJwhaln729ZvfdDX/44Mvvr12z+q9pNXikYL3bLe8//q6+nOr1c+vvndTV/0jG/P3f+h+XJbu+VP5'
        b'jfn20Qu6bryWm7Fz7vrkjBy79ckPf7r/odXuR8JtO+f+9kjY/P3Pf+OtPxi49T3NzX0Pl7wR3Pqu8KcN28vn9r3fu6ksvNP9t1WP3r395zO7ti9++xelsofCtlg3rgmt'
        b'3RSDE7AbUTvQAG9iPo4wcapphPnLzgVXomPgDXDY0ZXm8tQKmIjbPKFKOLy8leA4gXsllkK4H/ARrapmlsNjm2gUlpZ40KRGcqVLzXimTEofHGQrr4DHaIXxsS0rp5Bk'
        b'QGfQdHMf4C+n/cdG8gIw8D9JdwEF6oomTFXYuIgGhmiG+7aBajdwZr6MaFJqPCZshI1lxG0KCp1BrxRmZuE6xmI7PRrQ9iIQw3p04xQxDURyhgE8xfYDB5NpCJ1mcAzs'
        b'A9XxnmDAFZFUVgEDkfg5NDhHmw5irnF+MsA3RySVBVsZgA+P2UthlBHjewZddpVSVE0MHJ3HWsCJI3AQC2HXHJLKQI6qzvEBR/JYoA3HPpFXWwCvwlbUxhRVnbNDO5wF'
        b'huHwCho0t7E8BnfhNOiQUVZKbRl+91OgimbCB+3hMVzlWIGUvFJqdojEFoFmMv1BsG33JOgvrPZQxKC/4FwQ7Zp3DfTijAtSNDRCA7VA+3IVVgk8rEf4f314PIhUIElm'
        b'HE0UlZnGq9i0VHIEXAJCNMByxGgOPAP7zViwsmQJ3b198BK4gOoUgEGaIlFqaAXB4XkmZAE6oBGtQ+3HSAm/JtzLCWaFJcPK73GODFgJWmCDUxySKXpdZuR1oclWUKmS'
        b'jk82GS4r7AKIRz2W5KJA/dEMB325LD+0FmpJDU1/NE1k0mR0bc4CeH0ZC1xTR3OCexwWVIK6GxGJP8iOmKMJBbEs0Bmzmqv5ihzciMFQzpFtWk5lbSlDOJlOmYg+S1m0'
        b'amN9Aq2ZEoWM63InTC35IVIFr3mrj9AHA2WIvcdM3XExXRIoDBTbjpu63bdwGOUGjlksGjVadM/UQaw3ZuqK9cqWJB162JhF+KhR+IS5lWiucDXJf23pLE4ccOhaO2YZ'
        b'gP5Wx85u9mcd2hzE/mPWPjiN+YQZB3tXiZKa4klK9+l/4iTnWf15XXkDZWOTKevvWbmKS/q3dW0bUR1zCx6zCsH53GctxMm8twm3iZXHLD3w4z+xtMG/JozNW42ERiKH'
        b'MWMnviLJ0c0RhUkMHR/Yu+Kc8mHCteLkgdCuNaNm/jhf/XxhHP7lKzFz+U6J7WAiYDerP9KkuG7iMomD74i1xGHhXYdgiUPwreDbOmMO0QKNe9bcgS0j+RKfiHHrSIHS'
        b'hJPHAFfiFCBQGjdymHCYN5CB7hMoNWtMOPuOWEmcyQXuhKP7gLHE0X9kscQxEF3VmnD3EbBb1YXqHxi5/HHX5P70k5i54t8LkCj6nYaStMfaOPV8TG3MXT1PiR5GW3aT'
        b'eEWN60VPOKOZxhfG9bifWNmRgTO1bF0gXCCKGjN14yvf0zXFIxQhMXR+wHWfMLcT5UjMXcTbRhS6do+aLZowsxUloyfh3yskZm5ojBzxE7HrINcDvZKD/8gSicOiuw6h'
        b'EofQW5m3PcYcYukx2nZLReITNW4djcfIayBS4hT4R2PkOeArcVw4ki5xDCJj5OmLxkhTqPmBkduLdE7+75USM3f8OxUNFxomaafJMMXVxt3V85boeQ+kjhRJ5sWN68Vj'
        b'1AZuFxcNFbqIU7zjoTqhKSekq9PYBhf/I2wDqYJ/ajv/3m7eJFPzYyl+TQKW4r+nXk6UJ7lkhYpcqkvN+3+QF53xO7mcJ7sty136Luq2XHJka5JgXCrITSXHfjU50KV5'
        b'bJXW8fJzC5+fa3xGH0dxHx8zpvVRlmYcN5VeUlr8ClLZ5tDdY6/L8Mx44b6N4b5NZXF2CCtIz+Xk53DySzj5PCTWLvFcMjmeryan88fUS0zvh9O7Z0ZS0xZnZ+WXFBW/'
        b'kgTyeNCKv2C/RJfu4S5N5SO2kHaJThb/SpMSq6zbWJSVn5P/EkvtPu7cVP5pe5KUO51XwqFbynyVvcyR9TJ7W3ZmaclL9PLj6b20newl3dKr62KubMcSgJIX7+DD6TvW'
        b'UbYrSuSoC9oedKuvLEG20rqs7Ay0sF+4m59P76YlISykiVeXZDxPNsuybffCvfty+ixbTdu7rzoJusqkOvqF+/df0/tnJ6/PwxMtU+ZN76P846enS8aewcwqltTXlmJS'
        b'hybVluUMosak5NSYDDmFJbWLIVVjPlP6fPv1TF9bxed4Av+vp3LO4TJ/SZ2h8MT/yLbZmpeNRrMYDSnaMXKbpxht9WJ0PJdw0HIoLCqZqTOdoTedNbH3x5f/QZHE3l83'
        b'lTf9aTKtt5uKFzbj+o8zP7vxCZcGJ4UVG12mCd5E6oaDGX5KoHKWPNJXMdqTpWzdTHZ4yqE2Jze7ZFqa74wUBmVGcAFH9RxfMrH0Cz3tn3J+u9+vSvmPUky/iI2eqmL8'
        b'/3HEmLmQ0Zx+bsJh8TBIedqCg8RGr36eWOnz59mwjEo83/S6FWTHyjWhst5nwyUsNLtEsVIPjoIz9PwmgpvyU+wHxA6/b8UvBn84+jzpXM+hpCIvmmt7J/G8jg38kBPx'
        b'08z5ZLI1GC9ozn+hR/8ob+DPxxNv/LIGfi6TqOMLU8Gl6GjYAZuwboqtxQBnUxyJtnszaIPCaCco0orDV7wYYAj0heQ/3J7B4OH8oA/DhrAHfmV9215ujcf+wf0dBre/'
        b'SovLjEpnnjfeYLTeKEHwd3cFr02XBEsp6rVOlYyMv8mW/2ziCZ7xqVHA8fDbdWaMAhlyc3rIJ9jK36emMNg6Tj9oMnQ8P+HYirMkhl6j2l7TttpsY/5Cz/pWNsboWT+s'
        b'wGOs8j/K3z59c7EJDaazX1NSF4pXS4lzESWOnUFGg7HXP49mXxDdnW7r4nF4JfkFBZwt6QX5WX9gtprpTqMYlxhGDAaV+TsoZQbHVJHibEnV+cU1n32jkMErRleOXBDQ'
        b'HhB2iCrreSV7MrMF7tmHt1U8dE593dhJWOFZkPrOQ4XDvE/GK0M79wwKDtYyrv774kCAeox6yzvz1FtietrOhzLnqa+4L3BMgaUlnjmPH57sTxc/zEi7/RAm1oLmb5ib'
        b'c+1sctUo/b1GKx/u4SoTJWYhB1xwktOXaYJL8CTsZIUvA5ekefo0d07au6hkUE/sXXkLiJZ1UylJYS3VbYIDG4jVCLbl0wrKRngZDBNzWDm4OWkRY8EmwAfHiAbRCCen'
        b'k7dL2WxWY6WCHjhAwJeDtGALOBdCawNJ8nZwXOoyfHkhaHaCh+IjQS8bJy0WKRYwra1hFZ3+7SaXCQcAPxpddVak2GYMcH5RNFfh+UoA7EYj58ugnM9bRyZ7iiGSlZCt'
        b'tpVe/o+2I+pmZNZQXlc+YUr8ZXfU7RBlnd3QvmHCFDssNuyq2yW27XfpdkF/f6Jn1BBbG3tHz12UeHZV2yo+454udmgwGtd1xL6pikLFJmX+YuxFG1UbVR8j8pDo2d7V'
        b'dZToOooT7+h60E1Oc06Y5byc1TdBzk+j2ExRns+TvdavckfmU95LH5l4qUjzHOvOhscoB7yIHSqKv8CjzEIyeDG26BbvVsCDLhPkPlKWCUsfKdLSw0eKNMf+kbKMN/5I'
        b'WcbKEjpF3oqr8T/X7mJf0lnAEf+MHTpk1v4NeKwMZLiITA3tJ4qUpr7QS1gicBzXsHvKXMHQmPuEwp8Y6HDuI1LweAtTBiq4AIMK+hFMQQOLe9pcusTArypsCooQowzq'
        b'BjEIFqG0yBMXeZMSKcqgN0YZnE9QBqXghAsxOOEigk0oLfHDJQGkRPowjI5osIRBniYtmoeLfEiJ9DYMs2jkK9+QPy5ZWBXxg7KqhvdjA8rYSmLk1ubb4Y9+VUU+ZWtr'
        b'mD2i0AcNWEjsLAes4D6MO0Ar9D12UargKBNcdYF7ptHMOdLf3wWi3XXCeBZnFkX0Y4R+qF6mzHWDeEZoVM2p0s1R+M+dWOhWEBensk9Z6rxiRBxAlKc5gChP9aJXddKZ'
        b'Bh9Tauj57Cw1ueerzFpXAYkV6nK1VKe9l1GvhqxPWcak1TmkXa19KpN3qE3eQcnuwu490h+jXu0eRbqmCvqfZVLFIICPtOeIRpVmlXaVTpVulVGOepaOXKvq0/sh/VFG'
        b'Pyo5rN45PdJQzyxT4jikQHxR1KrUUXtauI9VelX6VQZVhqhd7SxduXY1ZrQrbRP3t1dPrl0FaYtapDUD1JJKlr5cS5py42kwNZ5ofJhZhnIjqlWmiQ53s480pdsU/UrP'
        b'zS5+4I1umXZmL+ZMr4EPevSbx0lHZ7z8yY/9XtJLOOnFWE26uTQf0Z5pDeUgoYzUz0KXMkuwWiG/hFNSnF7IS8/EGhreM+4xkSWIkygqlj5q8inpvEk5GrEghZx0Tm7+'
        b'luxCabNFxWXPNOPqytmaXlyYX5jr5zfT/waL6M+84CQHsyQ0cbErJ6So0L6EU8rLJm+wqbgoq5R012q6lxKTVqk3Mp+J+J0MsC1EHycUJiN+mTJsUeKopDQZ66vwymJ9'
        b'kRT9YOWz00kG9hlfJRnrtlE2AP+Ru9Lk+GP5HC0C+UmbVRDHK4VMcJYrJ5Loh7OKUI+Q4M7J3pbPK8ElW/E8ZEjVodmzsJPSDkmVP3SfZqiEtubjTqIrOaWoufSsLLSo'
        b'ntOnwiz0w0nftKkovxA9UF41/Ae8rCL1LC+rEVfqT2GwQHBNPtdVBG2T1dmIWEFYB2tiSF6q5RExcbJ0EeAmPKgGz6gsLnWnMKxMFNw7SwPo9uURoAkOykzKW+BBlXJ9'
        b'CyJ46ZqugvVOBdFxLhFsSsGeAQWwA7RKsSUjodjJGIjQ0txGbcsEe4m7zWp4DVYkuMBOeB6e8aRY8DS85kppBTBtqbTSuagCT8WBpDqeiq2Gh5YuBTfBseUuyUzKh6sA'
        b'ah3XkEf4wWOWTqB3K9oMPIoHDsBWwtM3LWARlp9vkaG+tsSSImnIAneAuin3m+WwKmaZfSZOAuIMj8bSSTaWFSnBCnvQQRyq3bbZxqbzNitg3BucGUgI6vOrwoJYvDlo'
        b'rTeM3mv6UyCSDXyxbMBrcIcT3CM9xla9c8NE6w2Y3UJ+4lDuYHr3ew9f1/uvzyr+8dXDW23Vpk19el98EKO9xYWlWX7tpwKnLcyvHr51dk8tduQ/d8Bqv0JOPRd7UGee'
        b'5HT26SV/3bZCocQQXNNz3yd88zb/7h74ORBkzNvEO/wzHzSfq2fdOzo3TNx0T3Lf+XD+w/WCjQ+3fWa7+c9nNlXYbhCOlu9faPuV8Py7xkaH+WNq9su3P/jys98OHjn4'
        b'VooGi/+W0qelnqyyRwLmL8fO1M+LZowdUH3TOn/gmyhB8YpuQQZ3tfuv6d6jFttup3g6eBl56nmd9PLwDGGWv3F7VHf1a2ZvL32vymqtis7f36Go39zCHrzN5uoR6QB2'
        b'o0V4ArvMrd6IneYYHv7wMFFh+e60mnJsOQUuEKcV4triDelU1WAYnlsXHTPlsWaOBJ+zKxOJ+BAJj4BTUsdpts9SkrZJ0Yf2HNmL1tCx6Bg5jxvtLFQ0DPYRgWYzuFEw'
        b'5VbN9tXC2VwGoRheoFOImIXN0Ykmroo42ZCKHhO0aSTRipnWUNgOqxGvFIfXjSPogMcRWwkusJaBeniW7vWeJXlObmAE9fUwFokUgZjpDGrVpCmir28AZ8CxKZ8f2t/H'
        b'NYeMViHs2YJksRgGxbaCnTsYoAWeKyJ+NHFGBk6uceC8LEc8DqCsQwIa6VVlCOySuqDAQ9h9wzk02gXxn+ASOyI0nLzUlpB52MPnZAQ9JIq6TI2tsIeIgFrgsgvO+5IC'
        b'z0fj5Cp0t3RAAwsc27adzFUiGtIm7EQiJRXwGJtBaSawMBRw2/duqEYuOAv2JYMadDeGocKJdI5GxMKj4KhbtAvJ+YMRN8PBoBI45gaqafnwTCjox36HUqfD5GwMGVUH'
        b'rpBZVAWXsiZz5ySuJ93GmXO2wX7y1jmG8Bx6JdQjQB4GT7ij5yFmGTV1UyGHq/ofCBYYJoPzTBQZMTIbTj+rp3uOLGPQgmbYCiRoWmLx8r6J7ahd2JhJ+Khe+IShRcPu'
        b'ut2kaNGYSdCoXtCEoXHD1tqtDbtrd4tKxgyd+WyZL0mAMEDMFueOmc7nK8tq7ardJcoaN0TMvUFDdG20iD2uZ3fP2FyQJ2aNGzsPMCeMTFqVhcqjVp4DKcOrBldJrILG'
        b'jRY/ZVEmLqPGzp8Ym7YaCg1bLYQWYuVxYw/SjwUj3hJZZx7IN2XBac0V5jbltxYJi8Ys3O5a+Eks/MYsAkaWSSwWCVik0U/QC+EowMw7hlzi87JozCJo1ChowtwKu7VM'
        b'WHGJlwTHnvijWM8Vld61XySxX3THPv1W+Fsxr8XcDVklCVk1ujptLCR9zDqDzz6h9dSY7u0vT1WlX3hkL5lZhs1hwfnuYRasN+cohJkqvWmhEGYvjR1UlXMpwPzPC/gV'
        b'0Agsk54ELzDDpmpyQYO8VCRzW2E4FquX9SYQKDpQYjWv/9ybgMv4SOF3zULPvoHMOhSgNs2xwGuSfZrJL8nxRq/I04BYpbt+xw/ieb1epCZvnC5mKz4TWzEdH4ZFW6yq'
        b'2FJV/6u1Wb0APsz/pc2qeIT5zODMal5ibolgE/OSX8EIbV7qtSMGJq9NORTl/wHz84dvchkEQyYFHCjFx0UjrJ6kr1PEFVYWPs/ENPeZ2eRlFqwjWC2/Y2lavvJ/aGl6'
        b'wYcGq8kZnIJXvjqD07TAQqITr2L8/wksnLkO2XGlgRQOgQCHwBl4EXMr0w9kHGBxKMYxyhl0J9KxFrggPgZrdkEPOKTmW+yW3x3yLpPni+fnUC+t874cca3eYwZvO/dA'
        b'nMjV6GY995RK57m3uusqvVhUb5LKapWHXBbJxwlOL3F9tgecgNmYAozKTNYeYgad5VJjTnkz58CTbNhfvJFOBtedUix/+mN8iGtgQLpCg71/x1AzRfjBi64emcGMSy/Z'
        b'x6loyRqZi5Lu2i28Y7eQ+HdGjVlEjxpFY4C0mXY0pd+3oz0nQO1luherNmVUe5qy8mWNajh0jcskcs5SN7iH2hAdPWlS46XSkEZnNsABWAHORztN2tSQ0FaRL/6nDoM8'
        b'+hs3P2LinG5U+zYtMjMunfnEaIPRrxumDGsUdTdQ5dGYrRQR6g+0/lODAvGgGD1vUMgsWVKTNraglQxlHacf9Vg6no+UKSu7WaxsCs+fkZd69BK1KZPbj4tXvqzJDeNQ'
        b'IaqKFe/TqMxk7HAeRVvepCFnilWMKiV0pihM0hmFV0ZnsB9E5wytQ3h2CSddxh3Ia+Cer6/ZWJydQ+tGZngyzqJSKc4uKS0u5PlxFnP8SECeX5p0sNM4RRnrszNn8az4'
        b'A7OeQlwpNveqmrkSqQ1ruJOWRoK9KS7JKTMj01wRCazwVlkPB0AX0RGUZ2hOqQhoncl0DcFyNXU4ogRrHG3zNbf3MXmYC7L/6UrTn/xINP7l+jP1Lohq9ubsGb2o3tI7'
        b'8dmQwOON9UbJXktS39hp1+su0Xsz7qTjfMWR1bo2o2vn7vto5ZsmbzrPjxmr+PbhrQw3gxP3chO/UFcPvW93f5OpUHvLB+6KZO/kvqV7uW49V5HIhmpgaLNTBOzVcp6M'
        b'PoEdoIeGtm1WBNcnpU1wyVEqcJoUEcFuUZn3tOgSLIBz4UW2MsQZdMm27wG1sB4L8KiFPlqEB61ATFr33+AQPaU+UlsJTkUzYR8YABWElOcYzqDkVnCfLDQlBPa8TBSz'
        b'HFaOGg7ala6o7SbPbEi5a4Qa5Elpdgmm2baiELEt9lQeM/TGCCbTJSwiGy25lSixixwziRrVi7pnYiWybXLhK03omjT41/qLbM86tznTeSLv6HoSjLuFYyaBo3qBSMzj'
        b'y/s7K9MknxjSft/4pzxF96WEJglb/37nvRJlMgkm9tmY1Bg9ekkP5+KS57IzGRTNskpxEiipG9grR7j45eKsJKZkputfUY4sLPV/n+Ispp/5ghRnVp+f4Uef0qzCl577'
        b'aZxHLsZMKPHsO3D4Q89x96xqyiO9m8ZW+dBNYc+3IVwmnci3BofjEMQWsG+rXJCNCWxhb4d1oJ6Om+pWATWyWE8atg5cBJUxWbM7Bk36ipgyn7OspONMtosVvV0eJa5i'
        b'UKaWd00cJSaOYu8xE3e0CZDgj7bKqLbdtOPzeeucRnOc4tX/6PFZcizMD6GrXjb63hv3hklDASjx0rdkr0vnxU0ziUxqygso2VFKTCL0UaqMBEgqR/F/wSCC2PYHGbMZ'
        b'RGTLHduVsqT5/F5osS+etIFll6RjD+N02g9xY9EWdDbjRIeydl/VTqHvkQ6rH7abEOuXMzaWbCzllWBjCb1zeSX5hbRzNlYyzGrtoBUP0zxTsfELNT6bpWVyk+K+Fqdv'
        b'pYcLvfNLG0ZUaW4AHNaArVP8QGT00j9gB/YXEHczX7AH1sN+UyccGh5BwRPgLKgiMJZvb7xO41+yqfc3sIWMkok6Yni4nIGO24Bv2FRQmnqg824qkTa7kzw7p2NAtVme'
        b'UzxqazkFG5OBMJ9KKmXzXkcXDVPXboxfrArctZv/6p1fLd7a/5AV8NOceIVjvp936jvWcaoaKlIe6/z7dOwGvY9s92kMDQ15uf2gCHPX/nInbftKi+697yeU23QKQqNh'
        b'/9q/RTRnh8wrK0v66Ydvx79JMmj89Ki52QrPMvDGsN+Hyj5x2oUFf+KuU2sJfa8SNusmC1bs4XZY2l/w/C6kMS46c/+i98/r3/1bjVtcEx8Y+lmeSZ17fMF67Td9nf/5'
        b'6/CbBvPmxYj9jj8KWBuy/8Cb2z7RbHnymHFwuRsrRperTAeANoGTxlI9PRhWIdxJIjxIMyc3rBfJacKtQTMd/HrcljAn8Uvg2dWgagaDwlZeAlto60IX7PWiFebrV7Ot'
        b'GKCFA07RYZF1seCQk6MsLhPsL1HxZyK+5RS8RlgTWGkA94J6UD9Nbz6pNV/BIR20ADdxBh+ZqSAFniUALEboIYQ36oa1sMfJTaroV4zCqn4dKP6f6J458qCASlJ0ku0G'
        b's5BNVE4otoSm2I+LV/0HDI4+RgZkj+vbiedIddBNvvyQpyzKYO4jRZw1fJVwldh4YPGY+fxaVT6bn4UdpuT01oYmDdtqt4nYomWi5SLlMUMuwYUTZNXu4LPv6ZpgPXWu'
        b'qEReTy3Sa9aU6pFN+Wr8Er7aU330tFF9u1+easuKafXva0o6wcos4DgnWI8FlRWCdZSgnkKwhVT9qyJ38qxS/EM2S4WS0/zSJ1Iu5rOeM7RF8nrfVfg0snr8knrf4mUU'
        b'8aElumlyLqlMBknRDlHmihi3piC9MDdTSY5yzZFRriP4oFKnD6qDrIPsgwoHFdGBhd1FMICVOnEZ0arSRkeYTtUcdIDpIskQ5xDVy5lDDjIldJCpTR5kyuQgU5I7yJTl'
        b'jiylXcrSg+yZ0mmW/V3sWQ6yxVlZOMSqMHvrdKdMbNamTei0xT+zqLg4m7epqDArvzD3dzBG0PHil15SUuyXNilep5EjAh+YRZy0tMTi0uy0NGdpcNeW7GLik0Y8QWY0'
        b'lv5czw9OZnohPriKi7AfmyxaoiS9GK0BTkZ64Ybnn57TDP/PsKuzmv2fe6b+3jmMBwL7JfA2ZWeSN3SmR3nWU3UqSLCwdGNGdvELOzFMLkq6G1OBfFvz8jPzph3v5I0K'
        b'0zdmz9qDIjquSDYOeUUFWWhDyTELz0QdbUwv3vCMt87kpPE4dGyiKyceB11szefRPUAcT15RFscvp7QwEy0PVEcmFaXN2pCs95npBQVojjOyc4qkvMck9g+9CEpxABR2'
        b'tUmftR35NfTckZz0v/bjPBt+OBUkInvu84JFpG1leGbMbEU+iPEP7sdUBTFqCfGc+V6+Lh7k71JE4dAmzMqWTZWsLbT06VUye+xKSHZOemlBCU+2RSbbmnXG7Xkc8id2'
        b'iZrRuWncnHRl4lfZhKQv9O0FeNFpTJ7uDCbPPo4wa7AVXIACnmcx4q+KKNCxAwzzthPOa+PCALUtmxkUA1ZRO+EgbM7dyGXQmEIXFm91ioNHGRQTHGXATnA5GFzyKPWk'
        b'sI7llD66axnNHzq4ujjAKjfHyFjEKnYnboLnS5KXLtfVxP4o4LijygJwRpMokCDf2WDKhQbyWdEpEbTgtjxC5tiQuVYZtIVmEYYxPFFjbSvDnaKWpjnXbCilSjHCPhDH'
        b'IL4FY8udCJ30gqHdvZ25LlEK1EInRdjot4ag9UTDGicnWKdIMXR2w2oKnALD60jTwnVKq60Y6FjlpKlbLFpCQwe2ebIDapjaGFnH+XUlDl3IWcNcUMkkaomCd0IVKJJX'
        b'jpUfDTsIYLwpPKAGqrcQJGRSv9hIxdWPycHHq/oX0UZUaQBhsHy4GJ4pNiGCqP8jUb+POGH+etKTB18Y4kU4R8W4Rro4KlKwmqu+GaNDlWJZbiW4pD7FpC8rlDLpR7iI'
        b'3QNdiRGTDhqgEl5WAR2wEnaFcZUJolEBqMD5nGJyYGuUHKLRIVhDxmh5BjwrQzRiwIvubjvAAEH22QEvgyOwOhrUgIsE+oIgGkFBHo1odNkDtEfLIXmoa7PAeUt9cB6e'
        b'JOtnldFmnJdBxHWeBBWCvetJy6t0lssghcz1CKgQRhQqBSPkRs9sfydX0GtD43cQOCF4cxGd/bQnLclJisoRvHgmnBCoYXDV6BV/eju8iYa83CZKhojlnUQDPAlgky1G'
        b'CxdtlMYIkACBYFBDAx4NGIJKpyh4TlEeFAuHABzMIi3nwUMaMkAsailshMMJoIrGhtoHBlxkgFiM8DUe8MRcGoPrlDY4G+06BYaliwZWiMa1hqQiZMDj8OAUItYucIWA'
        b'YhFArHYn0isu6IdnpGEH8AxsoEMPWKmgDbQTg0TwVk/8ZNQuHdpA4hrAvnA6pWXvciiQ6m7ngj4aYAmjK8FBcIXMiL8WvBYdWQyEcnoUUKkEmknjYAAMwI4EyE/Cb9mC'
        b'BAjYWgj67Qhy1Tu5CgH5FNk16itTS2lQKXgG9ILDOIlmPJtiqlMeoAneBOfAda4qeWXYr2vJ0ywuhYPqHDgAB7VQ5eESNNLrWZF2Gwh0VDpaxW10nZ3wuLq0Dg9eKMUq'
        b'oE4WbHGzLsXBZKANXo2RNoZqwatbwOGtJZtVijU0FSkHFhvuUQNdJHOzC7gMjsOhUniBt1l9HuzdDGq0iktZlK4ZyweJr92lLqiSnr8Kb3OpKnmeFryogojiBXgKCkvV'
        b'UXVZBxatVVQA50EbeZliQ9Aju2WP+1QvdbNZi1UNS4ky6yyoA7W8zTbghLTpyR5agD723AQFAuLFBhe0pC0ZwyoyJsXwAupgKMsPdG0mdUA3uJAtrUQBAWoJEVxFSlsR'
        b'K5v3ONK5wo8VM9XgpezlJagv6ioaxQqUxi4mGEK3kB4XxcPDCbGwNgHWwBN6OgmgBmd8aGTAS/AQ2Esngq/SzU9YuhR/20v5KqZnOdJ552G1hhoG2XF6tunahWSthKNJ'
        b'7+ShGjXoYegiE3YyHMGVNaXzKaI/b0HTXY3oX7RbbEz8GtCTtHS5S/JyqabBGRPDI5Ex8DAiCmBPkgoPtsAmGm3upAboj8bZ/hh+mkYUPA5a0KzSwEBwYCEcitiigyhD'
        b'tAvaQ3FsSgc0s8BJsA9U0boHG5OSMmYeRWmnmc2xliYy/YVyKviZKcaFzIWmKRSdupX6aZH0i0MQl02eHYxk236A5YAyTD6GymAHHCEIbWZLVUEPOm23Ux4220FvCCmE'
        b'xzU1nYhfp1HmtjCwj3b4bIZtOugMoqh8irclvxi2EsEtv7O5SYFnwqIoG+MVLcl/3TAepP3xu+V2l+9fvLzrc9eNvO36XVXin5a93q68PPR0hI7LjW+r/zK8evCMrfiN'
        b'BpfQnTqWH9045HZ397u/vRbZ+NmdbwsirhfHFv7oc/Pjd77O8Vzkf7Mq9bOQ//7Jbf+7816/4ZhTFnvp0zzJvTM3wlQ6rpYYrbk49ieH1zRavgk7nJl0f3d/3O2qU3/9'
        b'Z8KtLz1zJt55PF6c98//6g0LSdnWVfPBcBB8/1NT32u/fu72iX2bRWcv+N77219tbRkPXIy9ovp2tqe9m9y/3/uwj+idL+s2/61N8cPAnX937XPnuT2tjn/7ncqTfWE3'
        b'jnU4PfCK2PKuXrjN62Z7BrYZPjjb9bHv7pQWG7uMU26cmH071vd7+Ff/dud6xccuzn3vHxf2/vXP/9Jc/WCJwtn9TSsvWaxdoKL7aT112/gB8P3SRsfuT+kKT4I+/Jl6'
        b'+1xd8a/fND88vcmt+Z/cXRrLYvrS9TOefFK2cp9Jys+l8+rceu7W/Z1fpSCpVC/iGN8P8RQbbDboB7vuqZ5ZdT628vXtakevrTEpG/Z+sjb/s713bp+4czv8fE3p0dIv'
        b'D6T++1FgQUfpoMRkIu/G/Mammi/SezJyEt56dyB519/B9p8bfyos+1onO3nponb7EwOa8TviHxy6tvF8332H3d1BG/3yBoSFO3cvP/Rtx1ozp45/XogJfeupQ84478gv'
        b'xp/anfrySntHblHIl/O/DFyiNCj+JcQqeX/dKe6ah7b2/95w8uLE/UFjE/Dd1dHdyTpJ9p8fXP+anvbdt9Oun36iu2LdvDPcNzSawOMGRI1vX+v6uNKm+ZuzK+a/6/BG'
        b'/Pi6t0t/KnsQoatexy2J6Aj/7+DoTDWlujULJL+Nqva2+9pe8GZW5UZ4R1tGpv2r82PuJsG/Lh9Rdr50O+BDkyTdPoNPPsxq3rTCMnktx+TfecXpKRMfjL3mIJz74FzO'
        b'k5SqldXzvkuIP7KjpqsluNem6k75383GTG07PzJqE7Dma/cXaCr/RbV/uCrF/weTLUcivlmjM/foT8G180O+LuQzLgcfKFGK+3VuqsPPyxb+a2jVPVv/kqBLH59dG/36'
        b'0+PGBm9FPa1s3/Dzpo0HmwdNPv5vRkEs+47GQa4rHeZ9IMnAKS584TQfnDmRLCBSg40Emi1XGbZPsjI5yW75LFq9dRLxVkJ0POrF0V6Y8aSODjzIAkfQCdpCo8sJPOCI'
        b'VL3mNl9eweYAa+lcU0PgcrK8Cy4iZtfh2QgwLPXV6IQdGF7tbGjcDN9RxEJ1EN9TUAvP7XSKAnxwmHZtZYAWR2vaWfYG4iYqplKD9O7Enq3ZGaR1cDq9aFI9lweF0zR0'
        b'sAJ2EWvIHNSHc/Lgy2vA5V1Ma71Ion5coAL2IZa+BzTFwhpFiu3NAF3bQQ2NidcCr/hMau+g2Amr75Zw6RevtYY9WPO3ZYFcDlKIUc7oV7I2mUp3kp2WxrTxgH20wvOw'
        b'X2G0E2I5jkQrUoqbQVMZ01ZZiiUH9oILy9B9mVk4/8tU8hfQGUtbds7AZnjBKQLcdJCz5bbBo7S/bOMy2II4IlOWvGsyYiG/l4JankV3V6NTRQnJL+1okMFQErzoQ2tK'
        b'xbCSEx0Jz5hNhmk67SaLQGPFKljtrIPYabRIqtFoxDojpsSNBU+AoyX0MqmCV7ym2XmZkI/46z60Oppl03gW9E3ygeg193mgCkfJRcVUWId4cTAcKseLG4DztAr4KtiP'
        b'Fkp1tDke5kmO+ybYT2+AvWh2Bc/w3BHwsj4chj1kJpIcIB9dT+ZN8dxsKCBxs56FsEnGdMPK5EmuGwmGIjIorBhjJ1dLWCfHdod4fU9APC96Rcm4blC7aha2u49FZjTH'
        b'1gkDgTohJuJ0ALmsBStYRUiKEZDVEBaP80whBjMeY5LDrrxdTEfYvv17zMUZgyPbZKwZ5ss2w4sacIDhCfYwnGG7Qsh2lUXwMr1uek2zcF6e5hDp/CjDRiY4DBrgHjJM'
        b'K1VLpNDkC9TBIbdIcM6BQZmGsdESEGiQsYB1iBUdwNJJNeiIj5yHthClBNuYygagg2Q7QoJiD+K/6JMd7N+9HVxeR4MQXvQGNU5x4Noq+UQSujYsnAkInCTPtzNxcYrD'
        b'l11zbWLh4ahYV/R4KGCD5gRwhn7+CVjtTerEOztSiGNB88KkDOexF7Etv8dyTnGqF90EWsUDcS4RiK1HCyIabxE72KqQlgzbiLd6GOyCpwhQ+2F6OtRADROtogbYZoBG'
        b'Ay8JI+NgYlU45Ixh4FtWxDHNFsNhMpBLEFNeMenAH2fv7Ch13/eNJtcDYKUfHNLaIqWFKrCL6YyR4S1APVnLCaAnCG+SHgMXrgNeM7lMJP2JFnGtXg1w4f/yB7HuPqNO'
        b'qZjxT+pkkZ6V9VwnC7lrxAZhqEBbjXetJrjxgXWBolxphDVBTPTp9+/yH0m4suZW0p2FCbezBYvGTZOI83jEbZ/3/d/2l3CTxyxSRo1S5N3lZa4Vumajug5dCQPGPWtH'
        b'0u+4LKJ92MdMfEf1fCd0DfkB94ytRLZnXdtcB2zHjX1GPCfo9KhNZa27hbvHLN3vWvpLLP3HLBcK2PesbEWJYqu2lA4zgeI9a7u2TLGteHOXfUfBwDLJ3Plj1j53rRdK'
        b'rBeO5IxZhwrYgmVCJWy4wDmJGM2qkzaMs8ZtxmLvDstxIw9p2dTFOfhih+m4kctTLcpkwSNtyswCW1ZE3mKG2ErkO2bqwg/5RNdQ6C8qGTN1vqPrTF4ofMwkYlQv4p6h'
        b'zXQbjq4+AcEPrA0U2Y7r2s+w4UwYWDQU1BbUF/JZn5hxJizs71gsEQf3R3RF9ETddQ6SOAeNOS+5YxF1K2vCynHC1ALjFwYIA+6aOklMnSYsrVvLheVNuyc4Nmc12jQ6'
        b'tCY4thMWNp9wbHFO3LscDwnHA0NF7hTuvGvpJrF0m5h2xcb+bEBbwF0bH4mNz/Qrtg44r9BdW1+Jre+E9VzacWaexHreBNel36zL7C43WMINfqyjYmXwyICycsC3TljO'
        b'bd0h3DHBsSd/2TieXdS2SPaXrdNdW2+JrfeENRdP9QTX/S43UMINRE1YGjzmWhjN4bMfBVJWdlOd4Gug5YHTB9zVdbmj6zLh7j2sPqh+1z1qzD3q7dhR25X82Hs29mJ2'
        b'v3qX+l2HAIlDwJjNwlFtzoT3guGYwZi73hFj3hGjUStHV625E7V21H4duiaaI9G2vWdlhxZ4UVvRmNV8vuaEp++w25DbrcDR5Yl3gpNG7ZL5moJiibb1J7Lh8ZLYeE3Y'
        b'eU44OPerdKmMei4ZcwhGYzfh7HXXebHEefEd52W3Ut5a/dpq/M7oDlliXs2xuYtkRei1ndqc7ljPH9CfsLJ5rK9mMIfPfGxE6ZlPeM0fDhgMuKX6gVf02ytG56bwl/B3'
        b'1MbfMzCpz+GzJgxN6soFpXcMXcWK2ChniBeAn9CvKYAfMmFoOm7jPZAosfGTGPqRDRl2W0/CjR2ziBs1ivvE1JqEpDDFOqOmTndNPSSmHmOmXs/eh9aHgH3f0EGsJ0EP'
        b'KZHQpkeSHap+J/5qzS/BISMSQwfRcvSBioxMW7WEWmK2eMOI50jxmNESvsKEtm6Daq2qwFvkKdbt1+/SH5jTZTLAG8niq45rB+OrGrUagmzRYmHeuLY9/lurVkvEHte2'
        b'w981azUFJfQqdZdYuo9re6DSu9pWEm1EGnB9A6OG3NrchqLaIlHWmIETHhfaOFpeWy5KGDfkPmKy9a3xHlYTqomCx40ccJJxPbpL49oY1oGv9nQ3E+1oibHPr99vYVJm'
        b'Nk8oJrqHpjZ4H4kTxi09JsysHrMojucjFrr4C3FHBaZLAlMWsu4a66SqUncXKqQqKU2o2qV6siY8GOiTNmjq0wbNSXNhcR62ak4aCovz/9DI+cLnAOZ+0uh/008A2jDa'
        b'MpsDmhzNP4yNo0tQzd8qqKfLVjMYjCWMpxT+/IF8vkxwDLbLnlX0oYbVFjNZXNZHyjJPmCkQikw2NfVvUuNfhT5OaMuMo8SPR0lqGlWTmkaZxDiKTaMUiVtnVenn6BLD'
        b'KJtJHZo0c5YrqEzz30HfFeRMoOxdClLD6DOl8t5sDxKYsxhGkzZJ42qm20WJhTBdauGadP15vrVRVmN67HOJ1Fgn14Sz1GaXmV44qyEnA9tkOSTPNDa6PN8C+58YJ7G5'
        b'd9anOsq658gh8c3EjiTrB20VpLuETbyo64W0JW52wyAnuCgr28uXk5FeTCxZ9AsXZ28qzuZlk7ZfzqWJDKDUjvsslOlsBljU/Oz4blLznsy4ie2Jf2T/ellrlzL1rLXL'
        b'Mo5oGS1iQDNiiuNdYQ2Sc52W/Y5H01GuSlIE7Eey25VSD8yZn6dInPiUWQbbW2BVfIK8jclTl9oOz6qAGp9FtOK/Z+cKJ3AUDMl8oWLhMNEw1kWq4uTG2t/rpjlfiNtF'
        b'h/m01q4myY0t3qaYyQyq/rPSUFTqswmeQDI39r2pgscSsGkoNoZw/SkzglSm6Ulh2y6KlaQBO13BKdKbJCRvVcAhBjyApJFYKhbJCAIazmnT1l8obSZlNGD9/kaBS5EL'
        b'reecEAYlksuK6auo+xTlHhTqy9u2vsOJvhzWHkSuOiZuYIwzqbwghzTTz20LaMetMiQ+nvJiW8ADSMKkPIEQ7ikNxlIHaAId8uHysMolKhbWYzMXkl4jpaZDkhQ8ellE'
        b'lHMUAXQHdSE4wcgxjais9WQqXWA36JbzVsczCRvhtd/xT+uC+7gMYvaAIs950zL+lW6n6Hx/quAobZjZiySrE07aRpN4UcQWVAovEatbsq3Hs88+BVumzG4Ok7eBSnBD'
        b'pRxUgTYyVt+wSSJsozdYac6WKyykmuWg9fRIehSnUBeQ6BFknrPRKNAsuLgKB23iK1wFMqouoAs2gh4KXF6KVc5lyfAoMTtCQSFWN4NBMyyXbudEkVJwDknYTkrgxnoC'
        b'JWC6gnapE5rCIVhNFW3AGud8JJIfoM1fleA6OIqlcLSEqhX9dCn2fAboh8JSMmaRsCFVLg8HOAFFtKkIDMFrNETORTiA1mU1EThRR2ukWooesD8/P0+FyVNCtL8sq6Wm'
        b'PrZo3F37wDcLPr53zPYvJVf/2qmcpKxtr3l/wROtBUkP8374JMqsLiq0ZzD54Rf6Sq5VlrUWP1ceGSoN3ORQcDrWs+yLlrufPj72QXz7h3smFr32tSDKdPvObsOtpw4V'
        b'd99pia/6+ccT3effG1/CVuBdWvLdtkXHW70OinWTuv/8pu+b3do2ud3efgef1KZuCemO0ll45vD39aVFi0RRno++/b5v8KOuKF+vD/6mE1lR9Xryp31vP/zbN05LbD8P'
        b'WTe3vm7hud1dZS33371qtnu09XLqR93lW8+wjt6e+5WijfXwofgvgzz/8WTp9lvbxvt83jpx7tbnHgPmfTl//2HH/ixb43j+lp8LgrwCle62G7emH+i8vn6/pupfGO6b'
        b'ipr/dtbxq+jE+0GGYxZa+79/rd9zPDW+l/f4/TjncP0D/o2av6yuqmn5S2x05Q3PJPF3XT/77ODu/W2RpXbMKa1ej0DLVJ+DFfZal7vufLvKwUb556hVfQd+tt/9xafc'
        b'if8uX7Py0+s3xroTDdsvRJ5oHytMlrxrwFT+tcox8Ksv33GIUk0MGCrd1tZ/QBiwyzGz6mnfKWG5/wbPyn39f7l8+GfhLmj8ev9b95Y0Hv77pW//JrminfntFw+uPa4J'
        b'vJMyX6P2HzHR1wSpRR7Wa+Py9u3s+fU9t+9/q9q1MPRYlY9uyKjulaaUz1y6/nE9+O15YQ4/f7vzzzcHNhTHdzR9/OXbTTffglwDoo3TA52gl3Z7hJcRqaA1edfAGVrr'
        b'tU89InoNOD4dZADd0kSrXPbvggfk3B7hkJZMMYsNWkTJsS0cXMBap33zaXg1DK0WmEoulcGr4CxxHAdnwmhdH6zTpFWetXPgQeIwiTaEkFbFuoEhooEB58AgrFCDJwpm'
        b'i75jw34DJq3sa9AKRkQoAtaw4BFwgWJHYHTFAVOi59GIIWpneMwJ7IeD0S6OOB1FE4sJaiGfVo/eWBQtTVwNOuEQxc5igGv60XTLNTEpTvBEIskyPZliWt2G1m+KuApO'
        b'oBn2oB4Rp3gVcybgR4I6utlOeNPVyQUMZcuy/zFdQKcLPZxi0GoDq53lFJxgvxqt44QjC4jix3GtEdYyAnGMNBXLJS6lNZ+12g1204PTBs4sIQoqeCwWkW50SjkpUqag'
        b'iQ0qYAtoAZe06JndC9tIWqQjDrA/NiZegVI0Y7LhPnCB1meOgD1baD2XlECXF9G6NNgVSgIbN8PTyVJdmrwmzQDUoHfvhgdIM5FGoFuqTCOqtHXgnFSbtgI0k1ACL2dH'
        b'upUZqjT1LQpp4DSqRhJQupjBai1w001OnZUBu7iW//e6qucLL3hO5VmkmRosWbZDefew7abPRu7JXSRKrDeYtBKrII1BGZlMOs7mjRu6EaVL8K08iV3cmEn8qF78PUPz'
        b'CXOr1pXClU2ra8Pu6VuKFMWscX3ne+aO4vlj5p78MIwbmINu1nWbMLfBbrRNa/hhE7rGgpDWKGFUU8wdXQfSatCYyeJRvcXYE9dBFDKuzxUvl3riijya/MSGElN3fjB2'
        b'yHV8YGhyz5RDok2XjVksHzVaPmFi2eoodBSljpm48oMfoQVp0eokdBJljpk48oMnbO3PRrRF1MbyQwXzPzG3Ro83NBOU1O3EOrBkcelAaVe5xG7hmFWgQHGCYytQmLCy'
        b'Q98MzUXsuvJ7HBtRqDhpILlrrcQ2YIyzUHYZf+C3t7BqXS9cL7YbUBRbjFksELAemFrec/Ac8OrREmoI2ILce6bWE9Z2Zx3bHMUJHW6C4E9MzOU6d8/QlLx+9JhJzKhe'
        b'jJy6YIYC7A+dmC2cxCEjIeMWi2vV+Gx+9oSuoUC5LnCmoszK/q6Vh8TKY8zKC9VLrdW8p2swoWfSEF8bL4oQZ43red3TsxLZitnjei6PLCgjM77aY1PK1LJpLhpMPUNS'
        b'b7Fos9hqXM95Al1dPGFkLAgTqoqSJEaO6C9DI4FX3dYJM46AMWFmLlIQRooVJWau6C90M066nilaJrYSbx5YPLKEHzmutwiXx9bGiuzG9RxkDwjBqcbR97jaOJG3WFVi'
        b'4zUQJrHxH9cLQKV39ewkenZoGPSccJ2o2ihBybieLa2b2MxAi0Siz/2FpMsAWvpR3qw/eStEBUodpg1o/cIpRUoO4PHVKBRm3ae45Zkahiktw1WsZfi9XamK3oO3CFX9'
        b'F1YzpDEYDEesZXD8EX+8VHAti+Q+Ji9tiV+fo/iMVgGPGJGstqOPEypyWgVWlVIVU5rdkdYsUFi3kKM+qUdQfGV6BOxgvXi2SCGZHmEqxeNk4A+JF3rFcXH0PTKAT/q+'
        b'WdIauHKCad9Z0pXn+ASTMDqsbEBVIxPiF8x398DC/cb0Euz5ySspzi/MfW4XaGTRKT/YZ6HX6esvHRasHEeEHdAMekD7M/IOlrNMUmaXtGzB5TDa22gvuArr5UBxwX5P'
        b'4pxWWUZnGKxNcZgC3VUGw2GwirnDCLQSjyJ9sNd3ejpIEzfi+7YTVuWbzPVn8DAkTcY/FPcf9dAE7uqhLa/n6zo0MzerHtVV4bKCKxjHNUt+/boq+Ps6o6i0PJ21D3/b'
        b'+Nu1VTz72IFNgnCTlP6Dw3Y/dZV5Z7ol9B8ovBkw8VBRYWvfl17/dfxfq8q3rlLQ/CWiS/V4krvp4y0bNq18e63Gm+0Dtvbvqa927Vc/+gN7x4Oys4vXOV9w2MXV/fc/'
        b'mxaV/SjkHD+mF2uQNKLXcrvI8sM3bCSbLnIVaLbsKLiykzC64AIQSE3W4DocIuyQlar+dKgreBAMMstj4WXCx2wGJ4rkw3s8QLWUz4X9ioR3K4SV26Ws203nZ8zT3aCN'
        b'RhK+lJk1ZfcGV5QYSaBv4SvOJTaTu9AsJZtykr8wf4aSTb9MOIwBig7VWZL1H4TqGNqKEscMHbFFyFRQKtG1nbB34ocITO7o2d7TN79naCVyEAePG7rfs3EfMBqz8RMo'
        b'T9i73bX3ldj7jtn745oSdFLoGo/q2k3Y4TuNauMmbJywbaEj8K6NPzpkxmwWooNxpUSbQ1I+i0I+0ObKxXpqyUXcTJLR//AA4WnNPB3oY+F1fCz8/mCWqUuDc/DBUJQ5'
        b'eTC8zJnwA34jxkdK2/M3YRXo/2kuAQy40DUzqqY4My9/ixSHVJqhZRry6SzkPpjWQhaUEbVl/sZNBdlY8ZqdZfXco0E6AM/iaqLiF8kAPJO4suMIfCTsArWq0cQr5ww4'
        b'N0lcZ/pvZxgq5wNxYL5CoDGDh13HW9cGN527+KcAaQKMLI/Mw6We53L2DRz+KSo1vZ17pCUmqUBd3f3y3DfnbBHcX68oMMr1o77uUtkmLOayCUmIySnHNKkD9k+60biC'
        b'KlpC6wW9y+Xg/UCPBRa+g0ErDYheXwjO0TRp+9JpQYdgD2whoDaZ8JwxVjS5wUF4xAVWRdJK18jYzURYF+9Gd0SDHiUwABvgld/P1vCRdjo9y7KlzZvMnzBpd3mmAqEk'
        b'HjQleRSUzaD0DCYNxPbjuo400twt+0nKcd+AO2bgNKrtNDOzwxvP2cAzMju8qyiX2eF5PROqy2V2KMpC29L0ZfHJSe+KzzGwYjAuLjEsrvhn3F3tP8Arn8KAwyAtBECB'
        b'xJuTED9iziLcJqEt5F24xv+3Mqwx9QyE+Uz22A4P+TM4yZrY8JYiQzVX0dB+YoBRzW3ato5ruD1lmmtkMjCaufsj8vVxoAzMPBKDmUczCJq5FJYcY4cb+laF/6ispeH9'
        b'mPMMUvhDDT2hzbiGxY9MDQ1L3KTlI/ztiQV5HLrwHVOZRk5HF9C3J3p0P3jjGk5PmUYaZviS8yP87Yk3vpTS5XXZ5p6lTZfeYPD3LIam7ydBIRMBQU9ZOxkaZk8p/Pmd'
        b'Aip+xMZfn+xk4Zsyu1iDCZf1LueNeoePa0Q8ZcaTyvjzO/oTVYtkPCLlT1aTe2y6dLsSBx1GHfxfCxnXiHzKNNBw/J5CH7huFKqLvj4JxDUTxjWsvmeqajjjK9aP8Tc6'
        b'Phs7Z8FT8DSoJLjo2PsNsYfwIuYTY7Ajl4O9whZ0+Uzpd2iNwT54WQm0gLqFRbDJXRscgMPwqr7PfFCRibgYP1gFakGdMjgEW+AeSw3Ah/uBCPSC+pAQ0K4G6sBhhim8'
        b'AYbhDQ0g9IMXEEN1Ph1chF2JGti9fS/sXxgAboCBCHAjHNU6Bg+XgWHQBXpdd4KOGNAXsBN7ZCrBAcQPdYMr88AZ0AE7czd72kEhrAUVHrACthWCU3Af7ILnYdPOhaAa'
        b'dCJ2bdAwfHNAvAGotoEVweXrvWANvA6G8wPggQ3hJpbpJmF+0QorPHe4xoOOFWYuoB5eDACX4VkwBPiFoBs1XQ0uRYBLvhsd4THPdfCIBuzMggO6iOsVgTrYjv5fhSfT'
        b'gmHjUq/1oAYRTUVwClyCB4rAIKyFpxLgOTCwdSMaxhvliJluSAS1xrB9wyp4Epz20Yd9EeCqOziC3r8WHNUJAf0JYK99NOrAJdi4APSXw55lQIhjtBrhHngccfKN8Fge'
        b'EMNG0L7VgqUGjoMLsNUTHwGX8haoBsCL4GCmGagI3wj2ZaFmG2LBNW5mWJFlGDyaD2/Apih4YoUROLdtMRwB59FUDSxUBIJl3CT03tXgBNivOjcRDhnBNtiO/hqOBQdB'
        b'cyoajBOgwRkOLwi0W2irpwvPJ6OC5h32q5zQ2Hdr68KDkA8uJvJQaa2mqjW8ie7ohoOgH3VngIINXtn+ULgaNHmCa3Ngq2ZGLDiaWxIIK5bDBgtQvW6+MrwJRsx0wUgB'
        b'uGkKDuSi23s3wUNQ4GEG27Osk1cudIP1aC2MgE5eOlp2J2Fjorrx6u2F/jvgBbM15qAxDrQbr4L9aHwaoFgZvcwFtKYaYXsQPKIMDobCK+5oGk+CHiSPgF7Uv2GwNxXN'
        b'wDGXRWg5HN4GzhuaoiPtBppKkeYuFrwGD4XbRpeXHsXrvm0H7AAtyxeDfeA8OIrWvjq4Bof0dwahCT4bCiosQDMUuKh7ow2yB730KVYo6MxMt+ECfh4bVHN2u4EzC0q3'
        b'52nBE2g1tkMxGtwjm9JSwHX9VNAYBBrBIDgN9qbDZkfY4DQXjsArYJgFBlTgcVN4KV1hE2wBF5JWbF0Em8oTCkAPbEJjcd0BvQhaIvBcYbQ/auKUGWiClUtTUdt1qaDB'
        b'BwjAwQy0/yqZvrGwDgy4oDrnoRh0l68q19VO3Z3hHZ4Lm3XKvHXgOYjNoiK0Aq+DPfPQ3joUbhljWzYXrbZjQAh7PdAq70GrcwRWpcO6AnANvVMovAoOKcEzgbBuBxL2'
        b'ohfnw3P28KADEiZv7vRx3Q0OrFVJACNGFhjRGp7VWcAugjfT4Hkm5G8zSA+F+8CQKjiyKwIIYKVZODi6AlTA/VlaGHApPiHJM3POXGPYtThcVW+Oq7uCqVcS2kMtMbAq'
        b'Ac2wAHYbgSpEWCrSYed8NJVXEcOynwXr4kAtHOTA5jh4OBV2gyG2Dlp9hw2RpHQMYNq0f50nHllQhTijC1u3GYMaC/S8c2hRibeh9XBwu44y2g9DOfA4vLzTUw/UozHc'
        b'h+ZmANGui8q5mlGw1Rj0QdHKZNiDtt1+OGy5BlyPjQY3wVkVW1DHQxShExzwzYZDG+GhVHDd1QQbF1bHg2FTtOZ6YM1yUBcdpbN6K7yInteJFsKpVYj0CtE79INKT9ij'
        b'a59gqx8PKtGAX1wBzxSgoRPHYyzkEQUgyLAFbdFwoHQMLcm0kAC0IBeCY3gxok5fdgIXSn1h82o2alQE9xWmA9FmNbQrG+YtdQad2mnRoCsQHIGX0FBdgw2maBHdAIfR'
        b'e50H/ZHgwCq0Wfdbw+sRgYELoSAKdGRpq8L9ECMrtmE0aRvQyNmCVm8DMxBcK6Pmu0bC+g0lTmjOhkAn4jAPgyto49TBviWwATRlrFpTiKhHuzNsWo+G+yoO6DmMVmo3'
        b'6AAn4fHVoYgq3nQyTClZsxaIYlEnT0M+vOCAdkbtImvPbfCIngpGap5ar2h3nFxqjLpycSvc66KyG1woJATzuGYZECJK2bk4Zv52q0wwELdjpwFrbTioNgSVOejdbqIG'
        b'OhFl2js/EK1egdJGUAPOrgP1GmiKuzgaoH4BFEYAUQmqUont6qAVnkLH0llQocWEexciGnJGXwkML4BXjOaixXAeXPGEN/S2wo5C/TJ2XgGsACfQbj0Aj2tht2j0ep3w'
        b'GhhaimazXQceXmGeh9baXjgYBE6jUb+22h4dTH0rtpmhtdu2cSHkp6EjrIELurai7XDEFc1G+2JPAmjZCtDRudp7wzxY67AeisuXaG5HHdwLKtBKbgdDHhyHrHQwhIjN'
        b'sLoerIdX4F51WBUGTnkmoiUB2spQBw7BYw7gImgDPeDYdtiuZGqLBvkqPB22wg3cgM2qYY7ohQ8gCilC53ZTCBgKz12O5nII7OGtQDMqRKdhK7i6HVZvAYI1Stnw5MKc'
        b'cFdyph+LLkGHzYFSRBH4qM7JgHDDVDztG8Bh5hYj0IxWNxpBtLrBqZXrUS9vwlaWXVFUGDxUqAFrs1OUzNfCcyagAS8uN7Sb28N0UEeul95B61odtqHthkhtIeEwrsF+'
        b'J3iJEWqRBkRKULhclQEGcTzZUbRnBIBfAs5TiNTa6kN0+F+DArMdsE8JXAGns8MdQGMw6NFFh0GjMap+VBM2K200W48WTaMW2osCTy68keQaAZqW7YDHzcCRKAsfdA4M'
        b'q6KxuQGrlZaCrjS8XdIZm1ZjdqilEAlYV9ekIGqBiW8vIgOIBSmaD5p0g5yWz4H9K0BtWgjYEwquaENR+O5VaGBEPjt0wZGEmBWgyw5e2G0enIbIRjeaj56NaFR6QNOq'
        b'MgY8GeYFLie679AMhpWgCQgCM7HlDE1yu5EOGu0D8DQL3NSBdUmG2ibo3DusB/hrYtIT0d697rXMrwDt4vpUUO8K9sbouelBcQHoDUJbr2o9OD4X7glmwAqFpeBK1hJw'
        b'IiwfDAXGgaugaolvcOguEyhEax8RxTPoeQepjYj8t8NBRSBCm+CQAdos59FQHYPNnuA6OGKM9mizHbhaDi9tDkRrVoAOuaPwZMBm2L4YkZSKrGXbwIHwIrT+ReXgZLk+'
        b'WlUXs8pgV64RFCAK2IboxGF/WJOiMx+i5c6Hp8MRV4QW9BmOD+pDC/rWEeSzLVwbHYghJmAoAa3CYXChzBvt+OuwOxgeQcO2Hx13rT4WmBsrBkdyOPZ4JcJavUWEErSj'
        b'blaAU/ngZIbO9i2xsBk95QLaVQ2gLh/1pgvxA3uZ4GgpGvgjxjvQ6zWhs7MHHZm8VNDmillgo3iNBHRKnF1vANuy4YlINL+d8Opq0JKGutgXCPrQHq7yBftgRzoDXbkO'
        b'TybhuOG1eVvwCQQrNyJJeRMiL+fh/v9X3pdAVXFla9edgMs8T4IMMk8qyCSCIIrMCCqTAjJcBUSGC1dRUUFklllABhGZZJ5FQJDO3hm6k5jGmMGQpNMvPabzvzTGJCbp'
        b'fum361476deru1/3Wv9a/a/1o+vculWnTtXZZ+9vf/vcOrssAuIVcWrT9oBIYxdtST2XXW495EBaTV34nj3Y4wLnFNYRe/D2sIe722DqtJK1p7yY2Ov1gGhs2kNdgR4/'
        b'GuAVuvKsmIQ0zwJQrDmUu2Dp9mS4QReuhqnc897Km0NgBSdT8CbVmSDsaLtkAsX20TTaC3wPQsFWWLRz242jCcTPWnBRRNyyjjzYCDnnO0iYVnrJEa9pks5W7kmAnmBs'
        b'jfIlr9og8oX2w3ZEN/rh3k66Wh0RkR5YViPTvgG31HE4EOq2F2KTapjJiVMEdCXyZB3d5xWTYMpy595QfW8VUrAxaFF1NOaTxG4oanrinImVAi8AL5uREIstSekHNDaR'
        b'c6+jNsePYmkCXPMDgiUfcoGETEQOcCkJu7DbK49AogVukx/pJ44/RaPEOeAYDTWW2eSiO2EsAkvjsffoTqgOdQgjsZVClX/mpoj9kSx9qU64CIMptng5FYq1zptiGzmr'
        b'xiM4LybNaY3E0WNY6bgN2rjs6udQrPAj5VolSB8/kUARSQPBdpWBPol47hg2e2EF3MzxINEPOUO5D+lMPzZuj9M+7uYZkQL9x3Ah5yhhco+XmqKli7u2gYstAfqcMlZp'
        b'7Q23Jj+4agldh6nVJhVSrPunoDoqmixk6Sj0WMGgdhpOZ9MFO6mbNxLJDgaOiHQIeppg3AkmlaQLr9tOQJUJzCTkJurthhG3sCyqNg7txwke2nmZdF/FB0nh51yg3htW'
        b'rMnXLuKVS9p4n8liVwm1UlwieZcrXfHWJscqZUm2VCdXSCcLcVSEQ2cVCINLtc6TCEusjInbzhlt08RmdSKRMVHnAqHhkonleQmUJ+sfSFKOIu/dx/6DUlcC/laCETrN'
        b'm6VMReoqMFZIQ7uEN6N3K5GnnIdVtWM4gO2Z5nvI194WYLEEWw6JYOV8Nh3sTEkgLjMh5Q5A3OEerGSQ+s+m6GOZ2AQHbEgzesl4Rg9lY2ORKcFDF0t10+kWKhN3ntJX'
        b'ojMaCTpaSR41YXFE80YuHLwQk15orhyOxFb7cMCckPv2UZ9CVRJwDbCW2wAL2bk+mjCvVkB2UiImPtEQG+4itMCplHC8DK0Hqco8XJHHERURVkbas8+MXIaKXOhQozDl'
        b'CnQX4kwSKevUVmX7YMKn9gz1gMyzPhQ49RqTkU4S2tRssuGTNFu2Edds0NOGa9mmJvvIWseMcXE/AVctxSZz5I+XstkFkNiUZ4mDWyi6HcErF6DDxpHwb0GeLlaKgy77'
        b'RS6FZkePk52XkD2USsgUOhShaTvWnXTBzlBLsoZZLY38FMK/ZRyJx5EEMpx+M1LCLnciLHddoAIXcrOhr4BC8EoKk/W2aRNetu0mkJ/12kK33ZAOtcQYBDh0mFxlJelq'
        b's89JvHPYAMv4cA0nRXTdG6RtHcyWM9658fm6B2iEp83tyGBuQGNaAXT5FEL1FqwSHMWaTGjfRXVnYI44ZxtWRZOXqCFa0qUdqgo3g60uRZCGjuHEubgsooltB332ubNx'
        b'2agnDPiJ7Y7CXVKq+jCYPp+hfZwgqF2NFHzOEfsii/Zjc4AdacSEnjmWbA3NPEyym0qwlZM+IseDFv+QIMEBrGA4WxmK7KbcpA9QJsBsELvSHOuhieHsJGrqbi89AVa8'
        b'okPsucGnGY4vQ/SiFydkySbmaPx6QhzloCOe4eymQ9B3VPZk6IRyAPtrDEfgznCCGexUgXrZKYvksVaxxoFjB7PSh0a7FRUkgTy6SJ/eAZJRM9aSVXT4KpPIJy8qmhwR'
        b'QqtXlFqyFjmlRifShF4SUgtL1q3wSlBAGJRn+ujaEtLcxQGDc+SZbkF3kLrfEQLvBuhKob5cJXidxZtu7HQLBd2NhU4SfxjRZQneBRgQJWOFEtwSJ5PFNMOqDxTHRGJL'
        b'OA0jHSc7LNtHm/1wmyF4rTisSeytcyuN1g3neAtSuhJjCgWm7eKo3Xomgq5ZJiJEnSTv20zDTLFNRhGUO7FZAg5BgxVFCTOkDPFEXRqtSFjj0ORJAVJZQVIY3GfzjfST'
        b'j6ghnZoxomCplAKySk/bIqhwId62RBAxRc6gB6bMiAcPQbuHyOM0jZW8SA2vB56EYTdcENub4GIijsYH6cCwfJFEFCZOIgBthH4hO2EA140MsIQEy/7gWUIgN3g0ntq6'
        b'SvJsjdPOJHtdpFtocKWuDnobKsYoY3fqMWnE1cHDUmecIHMsJwJMILrqDFd5OBVnF+GMZbGEaLe8cMqKbOa2iz2wufKGocGLqFA99adYrCfhk19qyKc+9MPK3iPEI5uh'
        b'2g665XEsAxsCoWU39hymaOoqxSwr8jpYc8ws1dZ/E44pQMsxaBGTjazYqkpwOFUsxkH613RBhW63yi06lmLHccLhRhec8d9fpHE8De7YqMC8Kt4MJJu67I7jW4PIrIeh'
        b'HNkpnSo1CtvnoMQQupIIAqB1d2B8+BFxTLwecaFKcuKLeh54TbzVhTBi5jSPzaAPY466sCpJx1F3igIa7LSwQ4/FcHJ2FXhFYdslstE7rsQVq9h5KNvw4+RP4e5W6Cwg'
        b'naqAu0egIptceD+M7CXrHQ+5BONJFOx106iOB++UTr0s88jH3DxyggKpAah319t00Z5Y51w4G0Ng43G4h73bqFjFFVNdaBXlOxToE90a9cGFRBUsUcFlDnQnErO+CwOS'
        b'Yem0DMzmSKdl/mJKhkB0wsfUV+00junKGZ7BW2lkHSUpBMvTB45gdbC2rh9FLavQJiZ5litpC+KTQqMIeBpcDEl3WmHSAAe364eY7YLZ8xQLVMTqRzim+smTT1uIjJbO'
        b'zcxEmNBFOqDZjUSyrEhdmMkmTOolh7KSjvMSmLeFSajZZU+2MYhd2fSl/vQO6CCPRgDVwOpqH0zbwcS2HCL63TtxJu0ISbo8LJrohh5LNpGAeiCGQ4xvmQy7xIh9XnE/'
        b'+bhuvhHetifoncU+rWgYMidcrYNOX3Eo0ezuE0Q9S31ZeJ2GkgtZxO83+RJb6DNQY+e1QvH2OU1/RRg5lUBIfFU2DZCfSlbQcNKS7owcGt66SGiwaETGcINCXLgdlshk'
        b'YsWeLIKdrsQ9J8gzzGKXiO6wqYDccCmdQaQcb6SmwWTWAXec01OH+1viSRuua+OAnxMrFDsc1hPhYgYpDkvzRyh0WBbjSqJglzq2b9qOTRG5BGtXtbBXk8Kv5vPEpYph'
        b'NY/4ztxuGNaIsNntYkHOtwdb4hTw1v4cknunjbVks22G7oH9mhrYo3VJslMFyvdww0nvR0gDq2DwIoHBLUl0INQcIai9bA8L2iI2HybZxvyFmFPkK7OhjofT9H2MiN5i'
        b'8mkC3C7volgciHMkZOrAUVu4tycRxk0sgwgYmtkxpkG4T9jWTgAxrkHdWMHViwdCqdF+V2g6pbM/gq69tInkcc8fFvwIhSuSBOa7CwjPqiXvsHRrJI5s4cZBrPk+tI2h'
        b'y9dC2w4TNrqNi1LiwB1NrAyHSTlHGD8ipwvDSDg450pqMOkZjStQ7ZThSTraKJ0wGTFnU96wE3TtGg5QRshGSloOUxQc4P0zEY62NF6juOzjB8NG0K5mZEjSvwpzaWSv'
        b'fbt3MTBsQOAyYgntnlhsRoA3A2OxePMwdDrHEfZUBEFXWhy5hclolqD04q04sbWAl74LW7fiQCFWOcHMlkNYmr0N+jP3kGvopy7fJubaFUCo40UDuBiK1Q5x5D867cim'
        b'rziaxaTjgLtOvBjvh5PCtZIHKduhrQA3M7Olvx9200WmwuXJFFZzIyhubySduQr956jf5LMMcXArtEjIq7SFZ5JGUezS5qCSDWWKpjtx3DMDrwfrnoJlGJZgpycs+Ymx'
        b'jcRXj1PRm2H1EOOBV1QUcJVHN1oepgOLAnZupM8TBk/oBkLrvk2GnhR3VVOvcNyL0HyZ1GKS7OAu6cJKHnnzMS2Se3tKKms7x9NtCFxruUf9TuQpw50jOJgZEZ5xPJGY'
        b'6owq3UIHed1RRfYdYzWp0BZtrwcUZlzG2kzlZBw7BPVavscSzmN3cJjxdmzchtPG6UexzoXLMlcCojKKo2/icmhhEfW+JkWdPNgtvL+ZbwmtWlFYnhq7P3FPWADZ+FVv'
        b'bMn3SMNFcwIlNndCDQWHckkED2NKcUZSlGHR+xoJ8nrqDjalg7kt2e517DtLJkdUyYbNVqAhT05yJDdWhy5ak4YrB/JobGqROEKDEOY1vZwI1rrPal1Ssyb7aifAue/A'
        b'PoXb7X6KzHLVUbKXWE3kCbraX2o2BbfzPK4eDmGjr5oY+rXlMq0JdW9QX6YJE1u3c4IPBbEBVCoupOKsClnWHer6LQcvVWwwijfmk4p3kAu/yv6EfY6E3bLjkPAwTLhh'
        b'RyxpdwdB95ISG5HDqNFhkjaF1VCni2UHA1j2o0WNjSeZwIAzju+zQ6I0wcYkoBpzuOlkQgbasgs6dUgynYdgPp9cz20RTMcakap3cKN2bII+A08oToGqrcR/vQkRTQ7b'
        b'biKsaErHUiFMi8SXyHuVwlycGzmWWRGL5DXyBQdcYFjZnYRcj+36SSSmRU3sPaGDEwo25/x25enBDXeYDC0itRog99eP7QY4XxCMw5rsegvypPfSySGcU/QX0yh2UyNN'
        b'5h4F0O/F347juy1gyEcRuwpwTP14gj4MaqjnQbMOXg05QQ2VwDUHeecwGlGiGySZBb5pWK6ve1QmTpgTOAyTEXUdM8fVAMKvNrgR5OfNkGVUk1kSBSf0aoJ5peNY4Uou'
        b'mnS0xh+mDIUcQoO7SUcJ+QZoVBao1TINnRhCr1roU4Ar6VDuicOO5AIqL56GJo+jyE6S91JAmei1iTBlCcozrMnQbuvDLUey8nayiSkKrLuOCQ1c8Z4etB3yCMndT050'
        b'CIZwnE+nXIZZU21Pijr6YNAPRgRGZEtdsGqpY0CEttYOG4qwgRVN1RmY4eVaedHexl3Qax2Di+QqsVXDYpcFdnvAdVEsqU4ltorJNa0UHsHJHbsOQ2lWAUHjNSfGDQaT'
        b'C7VTUkjqWel4D2pTYCqPKHQjkbhaktb0TkLWMgtPigoXsUK8M+S4N8FAJVafdyThzihzSPlGlFl6TAPZnpZfeAEWIuhrH3SEUpB+EyZzA3EiRuoY5/DeriM+0GZDTpPi'
        b'3/3eOBdMJG5SKW07sbnrcWQcq/IpRNmKzdndEj4ZEvY6sbOfB2lUya+TKa3gPXs2Lwgp57wnzukT4Y3FZsUMfxi1wE7/rdDIIw/Xo8LW8FbPoIhx+fyJwECiA6XBhz1N'
        b'sfxcDpHsFbztR8M/AzeFuOwmn0VuZ5SDtw7ikuUFKKbYr8UqQE3pILamSX9ZG2cn+i+dh2uwxE5o9cFiFPWRrGSQnS4itjsAg4G62H42yjp+K/WuBUd2YcklrMM7RuQd'
        b'K4/CzcPEt+44yqXnOOvDVKAiWf4YVax1JsGWZ5EJrKhhTwKUESOYIudSBxPe27Fhkzx1c0DoiBNF6cQDy1MK4Yo3eeY66OHhjL4QO6P1A/RJZcZsBOrGuLD7MDSo+ioQ'
        b'bi5h8X5iNKMsqrniBEM+vAXrt6mKDkDZkRAbj4JMRVxRjzlnTRBP7Nzn1AGoz8Vm54MUV7NkdNYzvYg0pMoapjR2hpAV39KDJUWYjz2bZYdDlgRdd7ETyhJxqVARy/cd'
        b'JMsoo+hkiICnkSIXM5J322a8oazIO66HNfGZGQlJLtgRosrZp0vnjUOjHDRp6JHFNcPdTOUg+604v5md/iTfXQzLhnCX/e3utpExRX5XU3Z7E4vv3kGyuAUTxo7Z0Bi6'
        b'heyijgKgfAm076BhKA/CO7uUiMffI2rQte+cHvYqXxRQD5oCoENLWEQm10TfGmHVPvvYWeg2o7iyVNMjAu7oQ5e6u7fyGbwcjGVGSfJ4+xA0pbMpUUiP6qLi2ClTvC1h'
        b'J71o6O8R/k6RlyjFfiesvJhkRm6aaFA01b0RTp25HIPz55yIm8EAGUwzeepKpbgUSTyZ5E1gvQlR0n43Nj3gBbi2GZtERLzv5JHCjJ/RJ70avYAVl6CKsJzIx+VYwqcZ'
        b'KJd8QGSJq6P6vRn4slNT9THkhAnBMnebRqlZYAOZQIzFeTrcZXAiVaiP/QYeFjS4qzhxAsbkA4/RNeaJIw1w3XB+E8Xit90zlahDZdhTAOzvvyXxu6CJD636BOXLZ7A9'
        b'BHp5tDkISyJyN0MXCRnr2Xee0lA0Km7GvmBC0lGS/FVsKsJVuLdLG6vc2FfH91qEYU0W+ytXEDtTlXaAZFNmRZhSpczHEZEhKf7cWVMy88XtETmkbv1aznRvTdt0sXWL'
        b'iS12Wu3LCyHGQObhT9qwop2Od5Sxw8sMB1QofCw7CqX+uOgLo8JCAphmoj8tBM59DKn8khzcMAqENiWKEQa2qcEtv+3Q7kJkoUz/kA4ObdkhJ4eVkf5YpYSX/Q9QaHzP'
        b'iRhWhSdOq+Xina3KIc7Q64LNfjt9SSyz0MEnw+8ntC8/d8xUnV2sukhYsAglpqTr4xziZZdObyd1a46CMiWpViwmEYCvnrQiROjCihyS2yCLBHe2ERtoPp4OfR6kz+wk'
        b'fDNW6+GsGwU2jSegUg56001hiA+TPjtxng3SsTiSAGwu9Ay59PsuckSt++CqDZY6kGAmdaH3ArRpkFpWmrO/JAuK5NxOHKKWr+1SxVZiD3JnWApUquWaTSEfUfrLhBCN'
        b'MKiF7Xv1CtmnKg6S5DpgKfG0JYw4wnIA9NkKoN2M6FVnLAyfpJhnHPock4gAkdt225mzA5aCrfOw1xKuB8Og/bZ9OCsgn9IWZEaR7Q2c2U4ebpg1kfaDmntdiGOPOuHq'
        b'YQvCtraoY6pJFw4ZxpHqVGKxayhd4/oWbxPfCwzRy8qTOFwAk7ZciXSB2hh27cjHeTVcifo+leKoiXQuypDALd8Zbkc+z+l7N1HXlifNNJhjmR/iwIHrHIbjweY+u3JA'
        b'ls93FYatQ7COIUrUy3C2MXjVBwdlh+7BjAa7JJTvgjcYjj/DvlxuSHYL/Wxmo5AgARGmKtk0GYF+H92gNE/SaiROhURwMyMZjjN7qAKvyVokesqm9AoVFOQyHE+G6Mok'
        b'zsgOldAQdbHza4mRstk14lkzf+7xChHIcayxFeTAJMOJIHfHLieTTZk1kfVVY02YnLNQOsvWmIB90h7LHz4TYs8NYc9g5+XUsNSWI5t+G6ChvhUSLICKEwzHnsFKJ13Z'
        b'TVyGqkzpxBz7XmzZ1FxRjC0nQPpu0eevq+BePCxdZH4s1NHBhrHlSXf77+cdmuLI8gF/Eh0lyyT5nStX1UqWJNih/aIiE27LDaempGt6M2o0GG7+Z4RYuSEflB16Jft9'
        b'X+2jwRaWwdFbW9NCPlt5Zvgssenr6/6qcpu1LRYt93ys/4bltqn6q5N+Tt/x/iutXDvIq7VGlX/iZ53/0fnh29+1N/oNB4f9ztkC32zQMGhxdLb6hbNZs7PlI+cts87W'
        b'T2cO66ZFtqZ1ZrWJ4r6xv6imb276uuXs6oTCb/a/+huB2f1s11hF7Re+udNzsHPff96J2fLlxYoEswf+4WcWf21u1vHHL0JUfro28F+b7x/qUn3lp9EXq9653N2kHPE0'
        b'ZHuRyejN3ug15aia/zz20oNPIpbSv70x+vMt9Rs7v/56S9F1+W/GDHseSx6PrPm8UvJRdKn2qtuYkTHj+MT+5/zc6lI3ueBer1+8G+Ub1zN2MIQ38Im6x0+tf2Rg8/5v'
        b'FQqb3v/R0DXBo28jYy1ztY5+7Dll+Kue1+RfvH9M5Y821775dNudjtuSMyKHBx9IPv3qLf9dr9q+8aPkpvxdrz29frz97teVEaO2dr5HxuQNX13qfCfqQUL+gydri6Xn'
        b'F3/6ZfsvDUIf5sb+h8Sn+LU81zDLhTnvgicffqEGwV/X2f36Tc8Xnv74TdWEb4ISakbTp1cru3QKzux4YJif4OVR/Ya+VZjH7OD0G7WvjwdecL/T3GX/+IGmBKZfy5/r'
        b'/WxpOPx34W4fvKV18TPBK6mv5HmMHh/e9O1ml9+NL+9ufvIj28+7Drr6r2x8cv5F649/3/+GWf+nTx/VPnnrUvv82Y+evBq5e1muI9r2xQ+/yshzPf+2usrHRncebX9W'
        b'bPJrjUT+quJFhdtOVVo+Pw7qepbc0/sHH+6+9vDil89q/WF7dfwLESMfvubx0r6iE8JPHyV+mnn15W0PCx/tTU56r+y9c3+cXX88yzX67PQpfJL5G2cTmA7Uyu0q+u3X'
        b'B9e0wx4pP3jT6MEjGA+vmdv72tye0S9efeHk3ZL80ndOv/iHnN/GpBvnCJYFmRm/v3lxwMP9cfl/Ff04URD9ZNl2+LLbzUPZKz0fXIxafHpZ/CzoVz97+mqn0uE/qnvv'
        b'mf79x+6uDz7tqzxT+rMP+/VeOPPxvZSjf+LZlMStrUTaKspy7bVcjCcc4OzDZSke1RGXWpAt/5yGYrf/8T4TGNkue7rYeass52GfhtlfvTMNOvO+X4J78Yg0PZ0Pxas1'
        b'SmKKNZdUhCpEE2rUxBJl8u13eYzROb4CYf28rLklnLBXEj+vdAbnz+TBInaoyDH6vjyYyM6SJqKz0sDa/NPKeRK8qwbVcFVNQUXRNAGn1E4LGFtVPjvHCZ1fsJmCoWQH'
        b'Dv51VbYi1Eobp4bD+HIUbMKih7f0cWtFgvhlpee1BGZQwyjgbe7WIrj3hfQp8WpXqM2HWoU8usN8cpZVf6NFvCMHyzoUylXv+MKaYZOxj579B4nzCG6vCGHsjG3UXz96'
        b'q/D/UPFvX0f7730AOoqRLuL1/Qd/f/f56L//J3umXiEpKSsnOS0p6dz3W9KH5j+lYPJPf/rTH4uZjWgOo6KzwZcX6r2nptngXHPmull1UXt+j3NP8i3XznNDkR2Xpi2m'
        b'xAtm05KFyOnCWacX9v5YEwPfdA79QN/wuvP15HbXTmFP8EN9pym9h/oea7vCH+qFr0UdWjsc/TAq5k29mA90TXs0m7PX1C02eIx+LGdDkdHUbvBr1KncsyHH6HlXKj3W'
        b'MV3bEvxQJ7hSkfbo272r5/5Qz71S+edmLu+a7X1otndNYbN02+uhmRdtfynHE3o9U1QXGj+zkBdu+0rTSKj/1S4BbanyhTueKSsI9Z9pqwuNNhi2sGIMNlWqPOMHcNg9'
        b'bPksimsitNlgqGgQfcF+bOzlMIrqz7g5XKHnM+aH8nNp+ZRHBzekBzfSBLT9WKj3jHuRR9difiifykqqqy87gc9+39ijwBhtXlPQ/7lQTXraCa7Q4CuGLf+yKvt94xC1'
        b'rf+May70+oKhQnp8g/36LJgTLxCymaX+xscXso+Nc4rSLiTICy2eMT+UT6Rlj9FT6efzrrCbG75q0hOiBGzVH8oNaXk966n08/kJ0gOZsiv4yrFVfyi/kpbPK0p3ByjH'
        b'cISmnzNs+UzM3S3Uf8pQ8dUeLkfo+aUcR7jlmZyKUH/DVNpeEpeGhGHLr6Tl85bYzY29AmmVw3JCh2fMX5efS8vn1dnNDV8Va3n+xiGOFZVRHNm2DZXRz/fQ9pMMORoX'
        b'7kaggi3tiv0flf6qfCKR28tX4D4JUQhRMOauKRg8jVVnNM0q/d7XsW7gfGDnteD30M5noeCh3d631M16zB6qW/REvqluTXqua/MLHbP/rY75P1fH6B/VeUJ1jJ+o0W19'
        b'veFfwOEIgzjvaZr0K685Bjwy3f9IM3BNOVC2DLrHTz9UkXldUSvU+HmaNVfxvX/0Hub/jwrpWp1jfzOBwj+Ds+LH7AqV7yHW/s+w/k0x8+wgh8NRZ9fk/c2CXcCt/q8k'
        b'iWNH8gWunJ8m84Kmkp8xL+MsU8DLD6Fx7C91FTX8JJjnp15+/p1ux/a0pvYXLbL3mjkN8fWO/gxKf7nZIvDZPu6THvdb32knvlSxYWnsJaz8xKfo0qMkid6XnqY1WeIf'
        b'W9YXNWkfCNR46dqBspFrUbW/uxZZ2nHt4BPLl9+JtXlilfhS85Z33nkrYSDnpF/4r3/SfNT9la9M3k1ci1/+TPz22i9eX/tNQND+IEfPNU6IsfjRwkR1wev3wx8feedX'
        b'LdEebmPil7b9CqZePhsU8bbk5dbsqdSiJFfJG40/mXldUNGq8FpCN+/tN0/NP0gY2rn0mqR5y9uPOruc/vT+x4YOc2vltSoev/3RPj3vwo3pWuP/s8fc18TsK43kYp6R'
        b'+csadY09l7W6Plb2P5RXp6238KJO5tAWdDVM/1ju7oJ/3cd5HnUf8U7/5rOV39Z8kuu66P3Eoe3GtZW6F1/B0GWPLdtnv4tbfarx8vWxq7mf8wQemXtHPrA1kWYggWFo'
        b'O8SGxhERMEbhLZs7RJ441wwXh9hHe6X5UjbDZHzY6ZAIR5xmK7KLYjRwmQe3TttJiWcs3KQotgbqZVmT2XlkeUZVk8c+OL8Z2qFbmnTYzw7vhwSFqSjYhckzcnyuAo7F'
        b'yCh0FTbaYU1O0VY5hnOQwT4sxXEpn3Qn0ltsj3U2bOKTqxxGuAWnnLjQcdpKmkLmMEykyrizYCesMvxwDkxRH9qkyWmMYBIn2KU8jrIajCpW86AEVsM9LsmyyPTDSLI0'
        b'cw5W5j3PnNMDy9KFgdgGvaGBhbLGw4Kw1jaIz2hiM4+d2d8qy65zbQe2hgQ7hLu6cBj5AANs4soFYK2M+t/fh6vEy1tDnF3o5BBp8i9GzYznlYMd0p4FQZX5PqhljweF'
        b'yQ6r4gRvewwjXWjtCm3sNIEdm1yHZ63E8CM5cI/NwCZLnTOkn8ouKQ9zYEjqMwx/OwfGUqBVKs1QKFG2d8TaUA7Mixn+KQ4sXLgkHWt1aNK3x1oYVKGAhb1mGHWez2y6'
        b'wIfLOPI8jzZ24QSUhbA3tcOHOs+KXcmWzQE+fVBW4bYq9OSzx3fpPT+uGMSFKZzBUWmAAXNwBVfPY4cSzqjhnXyowru5OJdHcYsKDcsWvnwgtsqaqsE2vnTVqD3Wp7NN'
        b'snS/g4u9jvGyxOz9O7GZbpbNJY538Oaf3+1zze0L9pW7OKqJkyEwbkNjzCaIhqoAwwi2Y1C7NdzRVo7Zv0++iHZflS1eH8IKAd7GBiWcwjn2lVCNDA5C0wXZ6x0XsF6N'
        b'XagRpr6PzeQjKOJgP/TnShemm7rTETpWmOfIvgkq7/lKUUMJH8qhIVXaGTes3ktyr2ZfLhnKZpOex+tWXBofNo08qzAxeBWv2Ac7OmTZhTk6cRhlHZ4i3DeXLURt04Ob'
        b'l9JDaHhCnKgFsiS6fS0XHnZHwk3ZUtb6rXDbPtDBjuPPZhJghwUbuDhhskdmRHUKOGoPJReCBQwnhH2NxzDM2e7+d4RC/3ZX93/JYbLJSP5OzPKvuU526SrrOjOyMwqe'
        b'RyevMWx08l0x89SIEWg9VtF+V2XzQ5XNXYWPVGyKAx7zFStCS0LXNMz6Pd7iO7zPV3mfr/E+X+0jvvNDvvNHfHva/vN/3Y/4Th/yLT/k221w5QQ6G1ye0OBDZbMvFRmB'
        b'yYd8Mzr3mVzkTsE+4tL/68eXso+N4wWkntrFEV9/cZa21Dd9znDYRvU3ePT5h18q6dIOgc5jde1qAe0S6Hybb8cqsZKcvwGDBir+tjy04vo7MGjDYbdteey2g5L/Th56'
        b'cqiUcTO7dV6WKFvcSQJZFxRIcrNE6/ysjPyCdX5aRiqVObmi7HVefoF4XZBytkCUv85PycnJWudlZBesC44TD6EPcXL2CdG6ICM7V1KwzktNF6/zcsRp63LHM7IKRPTl'
        b'VHLuOu9cRu66IDk/NSNjnZcuKqQq1LxiRn5Gdn5BcnaqaF0uV5KSlZG6rrxPtoI+LPkknaycKxYVFGQcP5tUeCprXSE0J/VkQAbdpDDFxU2UzeYjXVfJyM9JKsg4JaKG'
        b'TuWu8wMO7A1YV8lNFueLkugQm/9kXeNUTpqnu+zFlklpGScyCtblk1NTRbkF+esq0o4lFeQQrco+sc6LDQtdV8pPzzhekCQSi3PE6yqS7NT05IxsUVqSqDB1XZiUlC8i'
        b'USUlratm5yTlpByX5KdKX8C8LvzzF+qOJJtNSPoD65UOz7F/8s/U9AetlRZs0t78aKnC0h/xPTUOJ0vAcru/VT6Vlv8y3zOW83NkXnBU8vPgfatwnIZYlJrutK6elPR8'
        b'+znv/Nbw+XfT3OTUk2waWTb1AXtMlBZuqyBdKr4un5SUnJWVlCTrgnQx+Tqxx3W5rJzU5Kx88QobEpiSDsoWoEsXysvmEnbRWEmyRD5iC3k2bwP1O5gK0nEO5wmXz+Fv'
        b'KDNKKsXyn/MlOznaG7kSoiQa7ypseqiw6XrwWwrWaw4+L1ihzUOH4McK6u8p6q7puTxS3LHG3/Eeo96g/zZjKL3WfwOdxvng'
    ))))
