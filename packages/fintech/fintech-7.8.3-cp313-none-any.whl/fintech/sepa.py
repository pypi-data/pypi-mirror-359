
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
        b'eJy8fQlAU0f+/7xchDuQcF9BUQiQcKqIeHApN0qIt0CAAFEuE6JitVVrFcUDRAtIVfAErYqi9bbtTLfbe0nTFmS7rf1td3ts29XWbbd2d/ufmZdAEO223d0/xpd58+Z+'
        b'3/l+P9/vfGfyR2D1xzV/f7MGX/YBJdCBCKBjlIw30HGWcvNswZg/JWcSw4ZCzDFqexzLXcofByaZY6bh/6U4bzJnqWAcUPIsOTTMUptxYOlwCVJQzrctkwnuL7dTps5N'
        b'lFbVlBoqNdKaMmldhUY6t76uoqZaOltbXacpqZDWqktWqMs1Cju7/Aqt3pK2VFOmrdbopWWG6pI6bU21XqquLpWWVKr1ehxbVyNdXaNbIV2trauQkioUdiXBVp0hXbAn'
        b'/b+PLwWggCngFHALeAX8AkGBTYGwwLbArsC+wKHAscCpwLlAVOBS4FogLpAUuBW4F3gUeBZ4FXgX+BT4FvgV+BcEFEgLAgvGFYwvCCqYUDCxIHgfUHmofFVeqkBVkCpA'
        b'5aryVglVNiqpylHFUzmr7FRilYPKVuWm8lEBFVclUvmrJqgmqiQqvspJ5afyVLmr7FXjVAIVR8WoxquCVS6xIeTNLBdWh+QHjYx2tcwfqEJG7lWykbAUJIYkyoJA4ENi'
        b'y8B0bgAoY2zLZZycEut3HI3/i8mw8ChZlAOZU06lkGRcxwE4TrhQUJT1ia8dMEwgg+gBr6JGtC03ax5qQDvRU4tzZWhnumquXACCU3noedQBd8m4Bh+cVlQLj2amh6fL'
        b'0Ta0I5uPbgqAE9rOzZkMjxvcSc18eJI85wMe3ALP8Bh4CN7wNPjhR6vRU7PDaLbsdLRTls4DroneqIULr5aiMzKOwRencUOn0NnM6BicIBPtysXFOMOn4fOB3Gnl0bQQ'
        b'2Ay3wadJivRsNoETekqMznCj7GGruRDUhbpX68lzXBfaAU9NZoBdOgf2ytEeQyBOsFT/hD0674wu6uE2dKkWXViJ9sbBRmdHAHzH82ym1MkYgwcZQvgMOoQaszLQDi7g'
        b'8hahmwzs0C7ET2WkKc88Dnsz4ekQPBjbM3E923JJi+DOiMmoM0cuE4A5qTbrBGg3Tu9FJhXawkd9uElZufwCtAHw1zHoKLoJN+Pnbvh5PWyfE5YhD8+WK5ZNYICDG9eu'
        b'OhA/o90+gc7mhqWFh6JtWWgH6kU7GGCPmjjojA3aUMJYvfoYy6t/CV9mRBfg149pk4dpUoBpV4jpFWDKtceU64ip1BlTrQumbDGmWjdMrx6Yar0wnftguvfD9ByAqT0Q'
        b'0/B4PAMIbQerQlQyVagqTBWukqsUqghVpCpKFa2KUcXGxphpm8m3t6JtDqZtxoq2OaOomEnkUNoeEztM25sfpG3fMbSdy9J2wywb0LDcH5dQFP6JRAtoZHExF/TaOuFQ'
        b'Ufge5yVsZLzIFjyrCcJxRZVCx0g2ssGDD3bYuQIwq8ihYXUK6AGVdoRWFF4J54Wf4nnyUfDXnOeivp1+GVQStrqivp3ptQHSSK+30n4XLS76nI2+NPsb573OTMgd8MSS'
        b'3y582W0PGAIGBX4QtaIET7LGiHkhIWh7RBraj7ZhuoE9+SEZ2Wh3uCJdnpHNgGpn2+mYKPcZUslbPw9voBP6Ot2qlQY9uoRf+wV0Hj2HzqGLqM9Z6GCHdsJTTraO9nA3'
        b'bIA7oiNjoydHTYqBl2AvD8CbS2zR6fK1hjRcUvqMqMysjJz07Ey0G8/xHWg7nhzb8FxvjAgJD1XI5GHwLOyGz+bhvOdRK2pG+1ATehq1oL0LAJiNDnlEOro6wT2jSI28'
        b'ADJNvikjpMYh7BcTG4MJjB/LNRMDJ59nRQxc/1GvWsUd9do5iVxKDGNiH83oeGOIgZejI29TGxv/JtDPwaFvt1/sKzn4mugNz5de2cAkeWZ3Ha6Py98czYsq2b4fVnTv'
        b'ks5/f/nXnkltTw6eG3xT8lrRa7x3f7dRZqja/bssN8FbseDLdcK4sndk/HtkEi9Ex4RBeHga8QjuJmyBN5WB5/zg0/c88dNUzEhbwxSoQYiTbAtngADu4sgFi+5JCFs6'
        b'WhceJg8RuqbJOfjBfo48aiotE10tgbvC5PhlHoYbs6L4QLCYQaez4Y17hC2gPjncuTIPNabB0wBw1jOz58JuGW+IEyLTifDzkYueDIJ0w4YNQ24JZbqatZpqaRkrexV6'
        b'Ta16xhDXoC3VYQoHHJJ6Lr78fQO4M5sDJO6tU5qntMW2TG9IGRS7sTeH4tvjOxJM4pABscIoVpjEkeShR2t8c3ybtltiEisGxNFGcfSAOM4ojjOJ4/sd4r8hL0Vngy8y'
        b'wZBttbpKo8diXzPEU+vK9UM2hYU6Q3Vh4ZB9YWFJpUZdbajFMSPtF5BpWiTFXdC5kEhXyyWFPI3Fl/sbwHepHIbx+8jJo3HFBvs7HD4juWXv2jj1I57z5uxBofMtofjv'
        b'd/mAL7Lc3f+G0MNeQRA4ah/BLeE8jHoqCAFzzQTMoyQsiOUNkzD/v0jCY/iZ3RgSdsmh0icLtcBD+izMKBr4mAx6sBCAZ+AGA0kc5YzFZJYB7eADRgbQVgnaZiADhTbl'
        b'OqK+3LUiHM8H8KIw20BIL2kWOokacz3Qszg+FaB98Eg9fRBehE7YZ8Pd6CB+4ALgNU/YR4WRCrWhjrBs2Ig24SfzAOqwQQdoFSuC0OEwBeyqFwBmCUAn1mXTDPAgehoe'
        b'RS3zYC86hu/XguwF8TTD4lL4PGoRwLbJuD4Q7gw3ymxp5VVYvB6fxoFn0Cnc8qfwJ2QC7R0W+ftiHuPAKzNw/DH8WeNI4+MDUS+8JlgFu3B8K/7MS6R1O1XgeXdNMBeX'
        b'AdAl/IEdcAeFIzNXwl3wGhc+jfbhRwfwB7POY7R26SohusbF8r0JP7mBP3BDNM2D+7GJ1OO8CnNO1Ik/6CC6RPPgwGYxOsLRokaCO+3xqD5LW4auoivwppILb8DdAASD'
        b'YG0cm+FIJtyLWmzg9UgAIkEk3I/Yhhng87Abs9dWdA3g6YJzFaJLMgNhIv7wZB3q04vgFtS3igEc1M0EobOwg+Vrby+cxde/jkNdvBnrm3LtN80S/ebQtat/PpQQklL3'
        b'+e0upctHsk/fTxWWN55JTGkNb5qR8eGlKDH34hWHvh86puy+FFXYv3zLybc4Cb+RPslLj351XOpkx1cCV3/18T9avSpUX3855djpxZ9dSHHOLih+J+H7xacz137dpbH5'
        b'MiZiccLzR6/3zSn72w/bev2Y3LIA9aX7UZUXTFG31XZV5au27r78Vtf8mTM2vaGNWZwa90pS+FzhzS+53+2bnPm85kzP64//KedoouGE6Erlnr8fqnyj7uLKjfr1XPuJ'
        b'gWsWlWPeSjqOOkLh+TCFDG0PB0CAbsyCz3JiAuHWewR4wh1Bj2F0hEXXOdSQnpXDB/bwHAcdUKN9lImugW0YXDWGY+SIYasAz5Q9BZzx8OnCe1I2dz6Vvmg7RoRoG76H'
        b'z2bwgTiWi/bAExH3vEn9++BhtJmwdl2EFXN/HB6RCR9gtY+86CnKlhIeZuZiQ/aa6pKaUk0h4cE6qYX7vsly32/nYu7rNujh2SQc9AvslvTmvyAZCfgG3OVzPAIb5twR'
        b'ABfXVptmmxbbhsQPnL0GJW6tc5rntCW3ZDUxg+7ebeoW7aCn1yHbdtvOoG6uyTO8KfEOF3j4tKn3aXFm/wmHlrUvO1jYbNvEI3nTm9PbSk2SkD3MXS7wl98W+QyIJhhF'
        b'EzrLutUmUWRD4qCIVteVaPKcejixbWX38p6AQy5diUbPqSZRPH4ulhAp0TK138H3+6+5wCte70DGOdQ2WSKEUwT4yooBmyFGP2RXXVOoxypdhUavI9Sv83jIyNkMc38z'
        b'+5daLunk8VQz+8/F7N/nDsCXXyoD9gkmgGP2kT9HBhAYwx8lA/6bMGaMDBgLY2xZTHtY6Bor4xIEV5Sg4dqwSPXr8nTOREbK4NGy2+dUCGbT2MBgkedrnFkA1BZVPl01'
        b'jU2aHGvnXs9gLVlU5PCpUzCg7BIdmIHORaHdMZG4OtgCijHX6taKrrtw9Kvw4/ziBX0l7a+J4LMviWDFa68AwYs75ic5OMgSHD79v6z5Sk9P143X6/4selnaHRId+dTb'
        b'V3YEZnnPXXU4rt/3ZWlZ1ruBWZEt6uXKzjKbPl5MLzDwY3h95yM/5WgwyFq41zPJ63a1uu/roqK56tuVzHfbwccxzhs+D5Nx7lHmexRt12KUhDES6spmYVLRHDo9H7Pn'
        b'lcGtYYr08FCZAiNmtA0ATymvIG2JjP/o+cgHLCYyT0aXkgpNyYrCEp2mVFtXoyvEgCjEMiVL2Cl5t44DROKmmMY1bYGN69r1nTEda7rHdawf9PAddHVrlTXLWsIakj9w'
        b'dm/TH3q8/fHu8oGAycaAyeQxzpbYlNRk0za+rbhtZVuwURTYkHhLHNQ5zyQO7o41iiP6HSJ05E1bJge3RFs6ZFNSY6iu09X/grkRYrkssZ4bejw3vMnc8P4Fc0M3Huce'
        b'A+wpOZaa5wTVIa1hPTNqPvynOl7Zg/OBP2Y+pLDzgTNFDLDeFlIsLFr60bgaM+lvTHfBRYJZnvqiyvc4aSCfRREn4TPpMcAb7cd4CURhrWoPTX1CyAP4W2Q3u8jh9wHz'
        b'ASvAu2EL3BnDc4RtxHwSPR7tpYnl+dRgEvetU1H4EQ0XGMjo18bMjuFgOdRF1O0Y1KukSQWeDgCLMWmPssjBbf1sYCBvTgg76mIE4+CzAMSC2HA7mj8dHVTEMPAq5piT'
        b'wCTYmEXzf2YnIfYsz4Wzi9Z9NYcDWEB3ET2F2mP4aH8eAJPB5JAgmnaHux+IwySRl1+UUJFSyDYLnoZnJDHcOKwCTwFT0LOeNKnWOxBgrhCpX1Xkq0irZJsVEp4UY4Ou'
        b'Y90uDsTNQ9doytL5QQCzmpCk5CLOF5NC2ULXr4IXYR9gVgMwFUxdjg7TpEF8GcD6Q8jCqqJxU5wmsmMIn4HNaDfs40XkYqwG4mGzkCb+KEgOFuIW1M8tGrdgQhhbLjqX'
        b'BHv0vHFrMToFSWFY46WvYQM8t17PwdrTVcy8QDJsHM8Ow5MJ8IZe4BNAdIEUtAW10ULK4JFsPYM2YgCQipWvkxq2kFYH1KDnPwGfwaorVl4vwmdoIVVwn1rPxVrtGQDm'
        b'gDkusIUdtu1ZU/Q2izDSw71Pgz25LJPchi7DY6gPoJM8IoHSCaKgxYdGTUV9PHQNHgEgA2RgxLCHzXEMbV2M+jgYUl4BIBNkomdhL614ctUTqE+QjjZgUI9hfQM8UEkm'
        b'tI2PAGASkP5RXuQQ/AQtuwydhodQHzNtHQDZIBvr4jvpEFbl2wGMJ+Nmi4uyXgzBtEXAJWyWFqM+PuyB1wDIATkYgh6nqZ3XBOOKwNzfSIuSihdp2QGfJUxHfdx5cBcA'
        b'uSDXFvXSpI0VoSCfdNy1KKkneB1LdMthIwblfTbwcDwuBcydvoymzQ/xwhgWCAO1Rb7vLHFnKSkVXULP2AMfPCvngXkcVux8tcwW4IdrQjVFWX8IU5rJ83n45AJ7HjqW'
        b'CkAeyEsR0KTZNU7EpFO7I7qoMmx1nnk29qE+eMyeg6kJ43YlUIYl0CLWedTbC/AANePGgHwuaqBF7IvxxpMLeD7tW7S00MnA9mEp0cDtmXFEt8CsayXqpml75f4gAQ/k'
        b'jagi37NZCWzLDGgzfM6e740aAJgP5i+ZS5NOlY0jiufcnc5F4xrzccuccaTCX2PPdZoNwAKwAB6V0YQaV3es2IDag7KihCxVvnniHnRcbG9DOgIw8S+EzzuzAjlSAZbi'
        b'kWmbVsS5GOvJvsjH4WV4EzYCD9LbRWAR7IX7aOqO5bEA45I1780pyqtOn8gO7s6UGIAZ88Jip6I8r8XL2MjPYqNAEW7D9LqipP6COiDjsK3oLEPnYCOvDF3GihhYXLuK'
        b'JdXTmN/heA46piMiZAlWmS5V/v3HH398bhJljnElGUVZWpspbOFcCQ7gF39QWpR3a40d0B7dXs/VJ2ORMeefJYbmV3M4iaItp8r5Lqkr0VPv8j0mu3ns/Q13m0fEP2K2'
        b'2dokFd/5+KXGu+nrCn/UCqKivv3o1L0Cp68NhgWGNyLuvn94TY5ym//c07nNUeVnt3wyq2hxdMO3j+8uk7w+b52t4+t6wZ9/LP/wmasvbInJq3UZ/8eFUnHkq6lBr04I'
        b'b5E923QqrWXFwuApvenV2ilH/lD15VcVqxdce2zozS2Kbz6+cGBgVeLvU/e+st63aWvcuNfjJubWZhzsSpo/b/xf5pZyP/mYr3h14plXVrzfdKmiefXlgJ6bST5+dadm'
        b'F/I3Lew8H32h/Mf3/vaXRdGnqhb7rxgXsOWVx16dMvdk3Df3d8aMu/n1Fxt/uPT4ze9NB7b29wSlcv6W8repf+pQX604FrinKeGv7Qftw3/3rfyx+3sKPD+58eb5JXyv'
        b'l8umLvXq09e/urJmXFVMsNjt0DruJJf0aeOdsPJDTJrwMto0DesvOWibX2AWhjcMVnBOcdCZHLSBakewcV4AC4woKsKq51U5OgPb2dyXylBnJtoZhnZmy8uCM4gB3hVd'
        b'5qKt9kuoehQNe1OwZrMjM51YkQRxHMwGL3iloAv3iEFcgK6jTXp4Oi1HHrIeXidGerSbC1xQExer8y3o2K9QgIaxypCTGXMZSgqJIqQjqxMUcM3nsIArjWsBXFGNBGbd'
        b'Frs36dqYpimtM5tnDoiDjOKgQQ8fK/CFYY2XE0Fb8+5wScjTp80cko7vNIdCwrrNociYXnMobtrlPDaUmPJCMRvKyH5Fx4aU8/sXLmaDSwv71SU0eJvWwichWgsN0Vpo'
        b'iNZCQ7QWGqK10BCp5S4N0VpoiK2FBtlaSJDodxJcjw0b9vJtGw4HBnXmWcKh8u5iSzhmcq/OEk6Y+QJjCacwc5hXhu+ymFymf+5wYfnMAoZUb75dxhQxpAn0VkiakHfH'
        b'lg17+7UVW8LjJ3bqLOHwiF7OXXM4PuGFcV+TcEP6HQfg5t6Qeofj4Oj3fkBIt7hb2V3c7fleQHTznKZErN+2RbUabnv6dfoMBEYbA6N7Y02BcZdxaLrRc/p+Pumzf3ds'
        b'V4DRM3I//64jkMbccQJ+4zqT2jOabAfF/m31RrGsW9nr2rPAJI4d9JFi7VYyCbdB4vn3e3wg8fsGMI5+tzx873Dx9309xSOhia7JMwGaaZfiwH3JnsFXi2mSi4nx0Wib'
        b'2iGtwHa05ULwMLVDfk/skFyGcfmlOmiLYDw4Yq/g/lu8TVZsgBXe5v4v8fZY/dOGxdt/WEoxbe3/LSjKcpLON+PtsyUUjYS85FfkcHnCY6zAE8ELqIGolLlRVKksLtKu'
        b'S+jk6TG6AO+9sY3a4KEvscFnddUp9MIjrnN3yvKzI4/sE3GTxzW1viWBvos/fMP3jRc4ex3LhGVl6n7+a59EbY6URW2OfuHdvoX1kZHdkbXHGfDhh7YnXjwvY6jCCDvW'
        b'LSJs0ReetZjV+fCQjPdQ3mQxkLN8yZvlS/o6naGkzoA1wkKdpkyj01SXaHRxFh5F1mGIlTyJh0mN2L5bEhpSbjm7NsU21pvZ1aAIT92mvCZhW2wnp9OlLc4oGv+Tap9g'
        b'iKfHVf18AoyzXDZZE2Aij2Fcf4miRzL+DMIbrej9NwlvjOGDO4bwBDkUEjloEux13Ah4AIOVZwFshxvQGUp7lRoKiaSRXpuTgh7ngNlart8CRo8RGRice23BjyydeVro'
        b'bPzcg17KGW1GyclMbuieV9ALIniUF+s8UfxG6SR+iNPHx2K2Rkpfx3RVBsC7y4T67btkHLrsUpZdNyJt7WAzR452h1JL5GOeC8MU6RPR/gfsEOhKsIz74JskHRwmOM8H'
        b'jA8j5DbDQm5xZnKba01uZNUFS8LO2AFxiFEc0pPcyzuVfplzKgcT3y2xvLvUJI7pd4gZTWElv4jCZlgu26wpLPdXUdjPMa/xVcz/zLz2M9ibgGVvE1Ox8lExjwsii8IP'
        b'R9axaDcGswlhuJJDFoKXicPYyNsTuYAXyeDBLXJozisG2qaOm4y+mHTqfgwxl5kWS3+LaeslQnsbbLO8Auv8587Y+6L3K5n5xaBH8/Jh9wybmMW2zLt3mXejbGI+00VF'
        b'fhzNXfRG0bzOGZ3rd4TO8oWHXxK9wetL9GjQe63/g5dnnIlRvugw9/tki2msayXc9RhW8k9lZYdzAC+TgefTADVvo6ewynAcNazEABLtisjNRjtz0uGzPOCRx5usQzd+'
        b'gYHMsVqzpq6w1KApLFXXaXQpFsJcbCbMpTwg9rjlE96df3ZRzyKTz5QmISbPtjWE06Wcze3JNYVPf4ExhScOSmXdiV2OTemDHtLOqJb1g55+t8UeDZlYcHv6tmu7mY5K'
        b'o0doEw8Le7HHKJsYj9Q8ZFupUZfiRtT/EpNxiuWyG1iZxZZgMvYjZrFfsmzImsUsDlbkT2Aho2ry2nmsuxGmZo5KQA3GNiphrMBM0dxRi4Y8/1H0quKNol1uIo9S9JjY'
        b'R1O07RiK5rMULZdT5XDNJ/ZFeR/aLzRTtIIqdWmrkooqby55HGhTr8Tx9U/iJ+qnbvWVdLwmWjQBuptZpn9ySLIoxr/+ZdF8x5Bp83ZvDNzvdnzc5kltxr22UMF/m/9a'
        b'oG9X1tVZBQqb/qzJWTHJ7ae/BdkfCc57Jl/e67mpPatLYeL/XvKm7ZQOpe3RLdyyGW27Bw5Iv0kabH7zyXPqso/PbT5P5DgXBJx0RTb5WP8hrxa2oBvogDs6QZdpbAAH'
        b'HmZUeRH3SC9XTvOjPkXweTfAIy5FS1MpJ16D9sDmTLQtHOfZmcsAYSTqQjs4cLO4hpaZDbvwjEANEXKOBHUBXjYDn4fXE+ls8nGDXdNEqDGbmOZwFmYOOgsPyux/rp7z'
        b'ICkSLzSL2jM8mRzKNVZzKccylzaa51Itnks+reHN4S2KhuRBsXtrXHNcS3xDyp+d3d738Gsr6yw2eciaeU3MoO+EbqY9myBhmqhtZcv0QZ+ALjzDjoQbfRRNKR97eH8k'
        b'8msr7Uw3iRQkVHKoor2iY3nP1N78UzON/vEm0bRvbPmeTg1pGKpLfBtyraacLZlyeJ4RITokKDHU1ZQ9WnSw3bWlM6/Iap2Ldo9e2i1z7wc892rw3JvwNZ57E34pVG4T'
        b'hIBu+5jRUHnYMkzlCX8YKhPnJhDL/5+gljFeJ+5jZl8AO/uOTHkN7E2NIsstsse9y9jZVz1dCmYl7BaA2qJ1Dklz2MiPV9sCked1Hh7ErEznTLOdxRHjaslGG5y9clBq'
        b'nrzLvInJu55HloAuyVazkXEr/EBc1iQGzC1KeMHPLKPcFk0CFUKJDRZceWKdExs501YAHBJ+sAHSoqyTGTVsZHhSCJg763GygjRujZuQjcxOnAnWCWMEWBjqBEt1bKRd'
        b'0XSwRnQf4Iry+mabm7S1Jh7U1eUKcDtdtb7mpabQlV4g0uEfhCx8Gz0eZyPrJ4WDhb4K0k7O10qzraoy3wVIJYNkQLK+SDX3aKtsFtiQ9QJZvnKtUNazkedn8IFQmsfH'
        b'Papc472YjSzTOwLP2GwbXGbWVy4MG3lpkg+I9ZTycZOWns8x1/71E1NApedV0nddwRNKNvLdkrmgs86NgyuyuyqLZSPfn1UKXlkDubiisj9NNnfTkFIO3kgQCHD2iR3T'
        b'YthIEOQOwnnFpMx1X5ZGs5Fnlc7AV1RKhi781XzzMt2b6x8D9xZeJqO0av58c48q5kSD0nwhJuMi3dTKKjbSuGw8SAnfhHlDEeeH4gigPfP0UUavwnR/xeOrnS1Xcl6K'
        b'FG05ELe64K31igGdpHfxttDDGX1p15mkobtpv8+TO2rrXdYUll1/qysoLe6p3x765MffHgyK+HzOp8Xj696Ngzt+l7Eg/onjny6z7dIvMwY9t5fJ+dLOaFebeLjb9sln'
        b'tc4Jf56Y9/QPZW6e/i0vb6ydhx5TTJ1zMbd5s3DCJ50luuLk6fekH1XuV04LPuA9oXTi/BPiC3a6e3FJmvdmSOoOLY8bf/Xla0U1ypkb/q/244qXINo6b45n4pUfjhd8'
        b'/E7jjh94/jFvLf+4p6TqH+6/n77NOEt+5ESJ519046VfrK2qFi0Zep45U3nxVOKKV714MboZd5/3nLZo1ZUXzriHnknM+UfY5YN//zD8U8ll8R+8X7N91b1aP238jc+1'
        b'70688fWZv67Y/tkH7wXsfvkt6erCezf9P73w2fWzP+abLn39mtOrBW/po770/evU5H9++fIP/7CZfj701vZP/25f+sf58q+fk3HvBRCJcwD2EGHzIGLSZfIm+6LnqNEt'
        b'EW1LywwPSUM7M+EmByxh4ClOPWyJpw5dq9HG0jCcOTSolgE8A4O2yaJkrr9SgPwcGeNqkTGWPytR40JETbG6ekVhRU2llrLzBRZ5k2+2s9XygcSjqa5lakPKHUyWkqb1'
        b'JuegQY+gznyMxPpFocQK5dbGbban6/9N6rbAZk2bulnbmWh0I94B3S7d83rcel17vC9zjCHxRuoIIHJpmtfm0qxqm9e8qDPKKAkyioJItKRJ12yLAy7iJnWzOy7Ku01H'
        b'10NJjrxmm7aoTk77lM553eO6Fhh9wntdeovPeRi9pxpFU0flakgadHFtKm3L75zXvsjoPrHbxege2q02ukUYXSLYh8XN5Z0uzcuMLuPwvaukORh/Obs0JTWuvuVFZGJi'
        b'p647qWu1ySuiWfCRJcbkFdokuCvEPW7Kb4tqU5tE0kGRe7tXZ1SHL+4rDlvf3sL9sSRjw9FtOpNonHWYDJ8HzhHd4WcUTWRzjw1bcqw0iQLvCsZWb50qqq0Yp3pYfda5'
        b'H9KSGG8i6e/GWSfAo+oqZtFGZ6LJdcKgxK3dtjOwwwG/syYGw3KxxPL0XdcJtx0ku3O35bYlvuPgT8LZ27J35N4eF9qQ3RZkdAgYFPuMghDCIV69Rq37adQwYiAusqZd'
        b'Sqj0csaCHIjyuYiPlc+74BdqoBS1Wwtrnvn7mzZgsXEsJVskgI6jZHRY1/QHSlvq8seJ5So5BD8sZ3Q8sh1CyfUGlq0OWCSSGJ5VjA2N4VvFCGmMwCrGdikf6wfcWI7S'
        b'hpRsQRg6O6VQZ68C0xmdQxCwrZDZDdkklpbqNHr9Z9+RHgiseiC0wI01wKJDW7Y5YPRDXLo5VP+gbt6xQjMGEuTbWWEgG4yBBFYYyGYU2hEk2lAMNCZ2GANV/Pslen4O'
        b'XUybCJ9MUxIvtpu4xEB4UcT6rcnfHuTo9+PQi3JYlXvNiRPloNd//pfJE+cLBJPd4+FLHvfeto2SRkV2/tDxQ+H2y8dd31xQ9fQruw7EeVy63eD1hfPf3y3hBqU8dXxw'
        b'674/bFxmnFl1sGJl4cb033T9cVX5BP/7X7U1GF4/0L20XTVzTt68S5UhN8p8f3z8/IH8knc/fKaX2/HD5NUtoors5ErxjZ0VdbPPNy+b/e5fY77e0/rtnbPOdxI9Jv8Y'
        b'JrNjPc2eh1vQVZbrj4ObMi1cvxmeZ93EeuCGVNYBOB9uHXYTS0FnqeFIGIi6Cp4YdmMjPmzOaroGw8BGKd0vgHa65ZNi0TUO3IZ2st5vsKMIXoIX4cEwhZw1Ox3lRAL0'
        b'zD1//HDC+imwEe5GuzPlcDfcbQPs3VE3OsFBW+EF2EWbHYV6psLGXLQLnjBEoJ1hMniSB5xtuXWrdbR8Kc7QyYcnaZpw2MMDAiHHa3kdNSCkoaPkSQTWlRTpaFcu7ILt'
        b'dAnpGBdthOejaMczx6E+nEYhy8iWk+0Hjeg0fJ6DLjlV/cdq04YN1mqTTWFhtWZ1YeGQs3lOKMwRVJoR1Z5oT2tsgI9fk80HYq9BiU9rTnNO5+R3JKEfiH0O1g36+B+K'
        b'a4/rXHiioNe1N//S4st5/UGzTD6JTSmWtLEn4rvijyS8I4n8QBxgiSS373v4ti3oLDF6RPfGXLYxecxq4g1Kg5t4ex0H/QLxl91goAx/OQ0GTMBfDoMePk32VozQfohb'
        b'UqnXhZJ+8Eq0dfVDwtoafR1Z+BoS6Ot0Gk3dkIOhesTo/GjrBhmbIvpnZeEgeo9Oiy//IEnIRq1/YV5psGGYWcw9QK6/gFtSXnxAIAen7eNG61mMZXr70umtAnlg7B/m'
        b'XJtlTE4PMyQsNLswyZghnl5TWaYnBUjZ1ylMqFRXFZeqZwyJLO/TEuPImAXCBtCdcjb7ZDYdyV/VkjLcElw7v5AMuozR6cj4jLRCpyeXOnxxwpHfmOuUnPU+6f0f12lb'
        b'aHnFP1Wvs1W9+WcLThb8+no3s/XaFLIE9VO1iqxGOPZswsmEsbUOm0epOZNjWQXAMut/oU2PkSRj1wC4Odp5nwRw9ONwBD8y9u2/9ZXsf00EO0eMqxfsuOXeICuNc/3m'
        b'FzKGGnuWoCPEpcHC3FbNIextcraMYzWjCP8YNnRq9VZLP0NuFtIcFU0ZDuHqBD5XCIGnb1vKoYz2DJNHcL8o2Gra8+kbeNhcpgZWq00NG8iFWIBcmRFL+7dq4S/DOZSQ'
        b'9mCJfthezpXxdMRxU7eSXOrJZR1tUw75kzni2VlItmJghmpXWMjuu8Rhh8LClQZ1pfmJc2FhmVanr6vUVmuqawoLKaPBvEtXU6vR1dVThqZbQS6V5FJl6cqQWyEeL3Wd'
        b'tqRQXVen0xYb6jR6XJ4j2eKh1utLNJWVhYUyHp4kbIT1jo+RVblZwwxuseVCcJCeoMLvt4A7dmAWk8IMRk/+juvs6HsXkMs44BFgDJhqco9vmHNL7GP0jTGJYxtSbuFY'
        b'6TSTR0JD2i03P6P/FJNbXMPs245uf+NwHUO+4QIn929JiL496nGPbvrCrfqsdFmGPNRbIQB2y7FgjUeXRpGpvfn7my/we5vhMhpFKjk6nhdYhOcJvjrj/yLztyP5juTE'
        b'csz3o/4ruVMFFH8GE/SJcZxlY54Iozg+i0SHESOfbsXF2FJpoxRO5WD0Se5t8b0dvRfSe3t870Dvbem9I753ovd29N4Z34vovT29d8H3rvTegd6L8b2E3jvSezd8707v'
        b'nXAL7TBP8CDt0jmP9FbJw7GeUxnaAweMob1GIV0RLcfbGywVKX1wSVydy6iRclb6TuUoQ3Bu4nDNVfo90G9Xmt8ftyOAtkNM76X4PpDeS0aXhv/b4P/CWC6+8pTjpnKV'
        b'MhVpG7v5kYyvk8o51lY5/oF63Gi5QbjcCbRcd+VEnUc5D/PaUIzNS6h803rhd7/W2c58y25TtiOrbVqseg/xyFx62EzJKbGxoiQnC8PbQvitcPS2Zcx7bTH35eKWMsOb'
        b'NMnYYPyO6cLJzJNtRqF7of8o7K4SjuK+NolCypPHxFqvy6qnYl5nl16trdOqK7Vryd7rCo1Ube6oFgMWdXUJ2bwdX6vWqaukpMPx0lQtTqWjSdOTEnOkNTqpWhotrzPU'
        b'VmpwJvqgrEZXJa0psyMGCw2bPoQkDpcmpSfLSJaQxOTkXFVOfmGOKjspNQ8/SMzJLEzOTUmVKWi2fFxMJWYvOOtqbWWltFgjLampXoUZk6aU7BEn1ZTU6DD/rq2pLtVW'
        b'l9NctEVqQ11NFWFP6srKeoU0sZqN1uqldDEW58ftk67CfS7FuEFh6R55k/G0XhKy7Gi3DEdFTWWpRjec2Ix92PTmG9xHZa48JmryZGli1ty0RGm07IFSaBvZkqQhNbVk'
        b'87u6UjZSKG6OuUQcengLHpbPAkXYvJa7n5+fhRRsbjb8M/KO4pTD+uqwQHfIMRC93C4eHSZLNcrKcAXZnJ25ADVkkm3kIAAe5sHrc9BVag/tmborp4oTxwGRRdV1uZ7A'
        b'QFbF4+rRTbpcMxc1kO3hEWjbXAd0CDXkKtlSVGnEgS07Oz2bAXA7OmyLnkNn0EbWXp4l8L9PvbOLsv7qLwUGMknXoXP+xCcuLJNsCcqaV+GUhnZZVCe0RwZ7gDLRBrVO'
        b'YB2pL6s5Se9zqPUiy9PDbPm1zeIlHGBEZNdweM6CWGCQ48h4dDzaumDUQLaQw+ezcEsj8tLQ9iwBmIOOCdA52LaCdch8Mhk12ETrV5Kdfrtx82ETOqn9dAWXrycAbv+C'
        b'T9fnJVY/GSnydfB5QfT2M4eX6j/nZqj+1B+RAl/vOZF2Wmd7RfXPtB8+VORURh79m/a302Kmrfj+4n0meFrvmfGDJu17uwdc/8q/s+qaTdbHcQEu5SU75/1Qc9vz/B9d'
        b'pq3a9VvHoos3V+z550BW5pPv3ebotuWkJi5d+a+jyw1frvlt+cqgPmlPh2efsgR+aPeEsf8ZmUKmrtW3xMeLTCc+D3s1Kfv+d3t3vTTt+U/+ULx/3ddXb/Xqpx1dxpX/'
        b'q2PNix+lRrvpt7x64Mjq39/6w+tTVyfkep56zCfu0r8cLyeUnzElNX3YflH65bzwV8pjpvc59EfPUm1YZ7frfkDJjz06WXgo50Jdd071pT99H1i7dFpd0uP3+cKFsaci'
        b'tspcqdejBB7g2eMxlmUb5KFwRyraHsEBbnArT7hAQBNwYe8qeFbEulVaO1WiK+7U8RE+B1tLMxUZ2eHpcCdqDkO72c3+3vACrxoTaytdK5wMm+DJ2lwr70t5LTp8L4i8'
        b'uMP1qDcT7UrLxor3Lpwd7UGXaBFuaDMXXcYKevs9P5pwEqYsy+aVVbBvxG/kYt29CEBcNI/DLZhscClhiJwlkIb26mmxEZnyUDJfiE/mHHjOBu5GN7yoSUFeiTajllWZ'
        b'uXJy+gChK/t5HLTrsXBqEihFm1LQ9mWw0dItPtrPoKuwEd6kCj28CLfBQxgzwyY7mpmLOhi4C255jHZbtj65fAbJzM5RPrrKYWZG0t7AHZWwlYJtMl+46NiwtaEUHrsX'
        b'RlL0os2wnZgUdsrooQ90hHFRvfAgLS4M9vHRU3AHPErNE+7wWVtc4GJ4Bu3KYnBLDjF41M+X0ZZEatE2/LC6WJFNGvkcAzvQ1gXsuJ52IrAf7c4mzq1z4Sni+upUzo1H'
        b'B+F1OgrhcHMAzkzgHdoEz8kxwHNK5s4m2+DZvpx7DF4nJYTjkc6ZFidP4wEn2M1Ngc/ADpnzf9OATzzIh20d1hYPjNC1WPRi3CwyYwuFJYaqIIUMq4IU2ALP8Z2xJo+Q'
        b'Jt4HHj7vewd1Fpi8Y/slsbfE7sSy36ZrmfGxd1D/hCSTd3K/JPkDsXe7vnNKx7rulaaAyPfJk2km74R+ScKgu3cT95aYWMNV3bGdWQPiKKM46raHT1ti8+rWJ5qfGPAI'
        b'MXqEDAYEDQREGgMieyW96nMel4Mur7wSbApIaufdDgppt23jtZUMevi0rm1e27KuiTfo4TvgEWz0CO7mdZcMeEQbPaJpnfEm72n9kmkfiN0Hvf0OydplHWHNyYNuXq2F'
        b'zYWd+QNuoUa30G7DQMQc/Bn0Djgkb5d380ze8qZki9HFNwB/2VruzAaZiaFNvHdE4wd9pfSh+UsaRB7ekgYPSnxuSQI6eSbJBPItNElk5FtgkgR/Y8sPdCXJ7jiAwAlN'
        b'vH2OVsqcC6vM7SSXXeTyMOXn31u6H3z75E0XWRl0rCzgR8jlKL4EEKWQ+GH9uAF89xhWCmd+B/CFLKDP/KWGnaOCWHDBfuavM+yUs4YdfiEBeo8wMIwQq8Wes3DExtGW'
        b'f2jx/sV0VO9PyB8GiARKYPBlwRIhOo26VF5TXVkvU+DquKU1Jb+quRVsc3mFxdqSR5lDuvFlyagGLtq/iG1gEGkghqM/2b7/bBwJjvyplhXgSF0PuaMtCvtp7PmfN4zY'
        b'rnS1OPxTjVKPGq5l+5exjVNYA91f277In2hfHmdsnHkwZRzMLdWssYbOyZ9qfymZTk7D7W9fNuAX8bZfhNUQ/xS4/l90gZoMObqrwMxMfqr15WNbH/O2H+vneT/i58D7'
        b'/0UPKqx6UPVverB8bA+i3vaLYnsg//cqxn9K5CxboG39qWZWkbl3CVjmXmQ+1V9xm6wN9VIz0Ukr6YFlj2zb/3dz6tpiu2Siy+ql2ge4l16jqaKHqGGFmaq4duQgNbNe'
        b'rsR6Mu5lqkFXI52rrq/SVNfppYm4Vwq7ENxV3GGccNVkRbQiUjZawRt2hLRa+8uXMfRgi9kYnG4NyyEgijdLImHgSXQUPqld93gao4/Hz++8M4O15hJL7p6Lnp5Jnpte'
        b'VrdFaTZ8vqh3+3n1dkGMIGZR9NbIP0tPoeIOaue1Xyv4i901GY9i+gmr5w6DNVJLLWpn0doB1HmPWIynYWR3xBqSU+hbjY6YEXljNQWcvnAb2j98uBe6mbQao0rYywJO'
        b'dD0BPptJMTGngEmEpyPgUfjsI23JNsRorKlVDzlbBKI5goI3skhDFqwq7IlP9/Tm6UZxyGCQbCAo1hgU25t/adG5RS/wfit8UfhKXX9QbH9QflPK3mwCqtY3r+8XBf0q'
        b'K/Or5PIavtRaW5mX2f/C1fRN7MQhIOhnuHUTNzwGU/r/xq27HFP6Ajulpo41TRkq67RV6jqzkDTozZYceg5hnU5drVdbnSdYXG9H8sRTg118UTaOw1nxl7pcoyt6wH4x'
        b'dkHC7Fz750W7gS8TV2YXWeR0cnoVMBBXBXQFbdA/aJh4mFUCnvYYMUycRYe1vRve5OmJs/IK/mL2xIW9Qb97QQQ7eaXt0dEbwJ5EhVI4Pnpmm3G5HTd53BRucmw+L0TQ'
        b'mq1xUNup39r4+tEYsh3m+svCr/68TcahykxxvTsH7R1Wikc0Yngdnb9HjzpQLbbWyvD83GbWzEa0MvQk2v0TW2isvI70mrpCy5ugEGfIyzIFxjyik2GSeTKsI5PBKB5/'
        b'y2diZ53JJ7wp5ZaHd1tsS31ndMvj7/uH9Mtmm/zn9HvOoSD/XdF4axdxdhrsesRceIRv+O/IpR9f1jJWvuEr8ZTwJL7hnv/RkQm/EA46jR6Zn5JNWwgEI4dEERE64Bf5'
        b'tl+klfj8ubNAgXkXObRQR84HHOXVPuzIUQlGvEv2AepRS+zmI161/3Wf9rVfjEznGp22XFutrsON15Y+Cg5Ua1abhVKUIko2Yowu0ZayBkvab8v+GlyQQpqnWWnQ6szD'
        b'UopDJXXSUk2xtk5P7a+EOeAS9TVVFkCrxbJdXamvoRnYotiRLNPo9CPWWUMJW2NyUjpGCdqVBpIfA7EQggikOkutuOz0OjXBCHb/ZkuKMMdA9D54opqXmYN2EM9EeANd'
        b'i5gXkiOfl6bIyCZ+7tsi8lBD1rw0bp4M9qRLC4p1use1BbYgqdy5Cm2CVwxRpIhLkyNY8yNsq2MtkFb5ATyP9qmwCN3HrEQXhQtgWy0V3G4Q8yTU58CA9R4AdQN4EB5C'
        b'Nw0z8SMNeipH72SYn0bOt1ShhvD5WMTuxu3ryU8LJzbOHelZaDuDedvRMrlsDXw6CB3P55DzlC45zF1kawgnjdqJtiRbG0Vr2QLR5WRc5twF8vk2YO4TAnKE2Fxt0Co/'
        b'vn4PyfVFYl/JAcIZJS9hzsgJitwg2JvzcVlRQ9mWbYKY/dFJC3t2BGYlPtt2n+z2UgqfdO0XdH5WuTA/qmtoD7S58JS42l4pbFHM9diz7I3WJ9LVRa069X63lxpl7m84'
        b'mOwvbfT5jcC9tO/u/Senbnb51Dnrm7nL3vCGO/5c3Pk7/aD668A3Zvnb7Gh964V2J/CYr7uh4guZLTUqFWvIyaDU5hSe7g2f4QP7ag7qQE+j7nvkTFXYis4V2YeSHdmE'
        b'zVpYMXoGHQqAfTzM/7eajYvoVE4BtSzCa+ii2bq4OpBa9+ChjFWZwyZppxIecBBx3VbBo+ymnxYsR25SVo/a1j3A7Z+Gz7BeRScd8XsdQTkrlhHb2UkNhVIGeCOdmCSj'
        b'Q0fvZINPoedoA+Lxq9pMzXysSS4LtTOwyQkeYs2H3fAw2o8fm61yuKeHSOk7gv7dfqMND0iQkclfqC0dLUFGPaIS5LhZghQ5AIlH80wClNa1rnvfP7Q/bL7Jf0G/54Jh'
        b'G1NTMtmppOwNuhR+LnzAZ6bRZyYVLckvlBhl6Sb/jH7PjEGxOy7EJ+DQ1PapAz4RRp+IXt6AzySjzySaNMfkn9vvmTuqSFn3+AEfhdFHQVPMeiHGOCyszGYq8rXP1to/'
        b'khVZwyz40XKLLjCMElwfkcv/4cs2i+AiGytyHRjGl7hH+v5St4FWQTA4YR/9Hzn88Aoxz/0psdVFVKpeYFGpoqiuPcKYf0rh+w+tLTLaOsNPmoGOjm7dtIdy8mRV8oNr'
        b'dg9pp4w7xKvSacqGBHptebWmdMgWyxiDTofVqRKeVescLF0gvhkzbC2rvlTSCofX/hmVIz1qiaNyinUwy11evtXabjXff5RUVfFHSVheIp/K3TGx1jBaTZaxR0Qve3Q3'
        b'C4mp1LPWIUeELOkkK/MsaYf3r44sHtIhYFPRJHj4SJyaaNAKabK6mqiiavOz4uVYGlMxTNaNsaRU5sZNjoyiK8ZktbeUWAewljpc/PDIxktnV6rLpasrNOb1Z9xg0uaR'
        b'FJZGWoqvrsFdiddpcEOq9fHSxAd1gSJzcxT/TtW1yzEk43BIIrpB5fSVKeZjfbGYRg1miaBKw1F5ZqnLRLvCFtiC+jJRXwaYgI46Ya7Zjp4xEH0YdU2fkqmQh2ZgJm+d'
        b'3wwBIualZdigLlVIhpwee5jNAHTMzwF1r+NTleQJfRpoAhsSHIqKlm+XrwKGKTjSAx0iK0kPU0nkGdlK63XSRngEXlbaoudL0EnaHmY+lkONNBldiUon4j2MCPxhyY0f'
        b'pIVnyOCNLEW6PFQAUKPMYWWWt4FomfDAKnTcWsynkd7Quk/BTSFYkGBNI1wmz+CDteiELdwZD0/JuBSAzENNbrRm7lJ0DPBmMPAUxgL0RG9IjiXfHsbmziYOuccmonbO'
        b'Y3hYd9BjyWEjfykvNywj2zySDBAHc7E4Pg57tN8rpFz9KZxoYFFs3x+JmuX10gbb2M46qlHFZMUm1LUZ97rADA3v85IXj+Tu3Mhc2y6dfLiqJOn8TtW2wM2OLzuXPbef'
        b'o3rTdsGbm47ul2/2WnRDNXXL8vlB74bPurg08P3jWRVnPgL3N/oF2Sg7XuerXt/cNR90Px3W4GOqOe5Qe2Np4I7E65dVRXfFPnvCvGbN4Ay9uPv3m0W7ilZNL2s7KHrL'
        b'16nN7ouVXfCFdgGQbAlIV3VglEGPDz2chi5gBJAFn7ZnAKeYiQqtpjYOdEUkJegCtU8cDTBYcLEEXqbSf0YWPDiMUvhzbViQsnABFd/Z+F1lpmeHYlDIwSPaiXbBRg7c'
        b'6AFP0O0xaCc8g1qtNEmMWXZZ8EWh8h49C9bOnZYsXcDuy8xewx7k2S60I0uYdEONAF6rrOSMw3hnN11yRZtRM7wCT1TSnTe57Jmc4fiFRXDRPkw7Fyg0QcfQAS1d1oNb'
        b'FpvbT5f1HkfPyxz+o0U4wojHrsDZE7Bh5hlDYmsEYo6k2OM2YLFHsSMx5cS1xr3vPbE/eK7Je16/ZB7Zpp/QmtCZciKrK2sgaAr+0MeZJu+sfkmW1Qrd+1YrdDhX+zSq'
        b'ApvE4fTBHJN3Wr8kjazNlXWWDIhDjeLQW36h3ZNNftFNs9noigFxhFEcMeg3/tCS9iUdy5pmD4q9WN/EjiyTOIQWNMvkndgvSSQrYb7SQf+gAX+F0V9h8o8cDAy9a8OT'
        b'uX4DeIFiugpmBzx9W9c1r+sfpWg7s6jlL+TyBbl8CX7NytfI4ufotS8zvvmeXMgPOJywLH79A+ObTEeGCSOLX2FEOw/7pSDnkCACnLWP/3Ugp4KFEULLu/8pKPHKaNtx'
        b'IBF9WLBQQTgsKa2NxTI71nZ+llz+TC7Ub/MzcjkB6GKw2Xqo+yeJu0AuJvI6eMSfs4eTg9s2W+apIxu4dZvJ5SlyId5kxHW+tKaksJBdUdwKzMuYQ9xibckj1zKHbCzr'
        b'KdRsSAwlQ46jDBQsBh1Br9/TXObe6RoAXTT9n+x5c3lgtlrRzQ7LhcAZfRtZIt8C7vI4jqKvhcDJrT2mi99V0hPUo+8PiOn3jr0S8yr3lrdfD/dc8l0u4zT1dsyUwfgZ'
        b'33FjHSf8DeDLN3wceYeHQ3crGSDxvSUKHpRMu8vnSKY3pNwVALHPLdHEQUk8jhEnNCTjGHOaRJImmaGJPAJuiUIHJSnk3N7ZTMMcc6qI0ak8pbdEMYOSVBzlOYdpSMNR'
        b'7v63RFGDkmQc5Z7KNMweKWs2KSsNl/WtUOg44WsJ7Vonry3M6DjxW46tYxhxaQ2+Q0J3JcBvwi1RZH90MluUHy4qmx0Ncdd4nOE7jpuj9A7AF3MuHLobbunbHNK3dIZ2'
        b'zhw1j0QpcRRbyvgufU/sOWH/xKkv5hsdM77j+DsGfQvwhRSXydwh93dnWJo+hTR9auMc1tWWbGRBl+BZeEKflUPVWngQHsWy2m4tB2ONvah3zMHo5O+baMx6Z7iOdbhV'
        b'cnV8JU8niMTcSsnXCfF/W6VAZ6e00WGdX+fgBRbxqWOo0OyQy1CnUJHSdipHGYWhtr1KFMtV2j3gCOq41GnYkdZxKkfnTO+d8L0zvRfRexG+d6H3xJ3VaamreQOWDXXa'
        b'dFa5xAqVrtaOsMPli0n64baJlOKpdPMZzesSy1dKHppLstSJOOOOuKuS3/GI5SjdqTuuO+4JY3bN9VB6egOdJ3HD1XkRx1udtzmtD33uo/TFcb7E0VbnRxxrdf4qAc4d'
        b'QJ8GqAAOS2lYqgzETwNpzDgaM464zerGm8sLonFBygk4boI5biKNm2i+C6Z3wea7EHoXYr6T0TsZLT2UhkNpOIyGw2g4nIbDVbY4LKdhuUqIwwoaViij6cY3snEvwrxx'
        b'L0IZqYss52MWHjMkSKyiXrtvEK/dtXaEM7MxrOMu+6tCWO8gP5JQrlMThYPVHkrqh/1LdVgBStThhFWaOm2JlHjDq9l1hRJWmcERRF/BeVnrYmW9tKaa1UgsGoWMMyQo'
        b'XKWuNGiGbAstNQxxU1V5OfcTKurqauMjIlavXq3QlBQrNAZdTa0af0UQr3p9BLkvW4M1rZGQvFStraxXrKmqJCeZJWfNHeKmqWYPcdNT8oa4GXMXDXEz8xYMcVVzFs7u'
        b'4Qzx2YqFlnpHGX+HXTVnEKd2ooxyQsyPSh3AIwQku66jGv4VKCUTvxqndyOrl3ncsektNDtcshMAS/iWp0qOiiPHatbIb0wRM7OKsdxXM0quiiFraOogXAOj5Cn5tH4m'
        b'z9qp2lIad7hVAlKF5U6OuYkcR8gdSYm5fFyODRsmq7EjtalA5bDSjntjD8b8DSveoHJ4k2a50HazzHbtX8f4T5vJbaz7NH0prJ6sZtPQGCv7Mvu24qnHsjJXHhsdNcWa'
        b'OkuxOp1eRtRaqb5WU6It02pKw6myq60jqjBGrhbPaFqyxZDBUv7wVg2aI57cxheVasrUWOoPU2gR1q+1JRWkNC3bL0zb5nIx7SrsPiMv+76btpquLY+0LniCPniIUQwx'
        b'kZ8R1PzZj/jvPlcRGZkjsxkSPVgNWT1VV9ZWqIfs5pOWpup0Nbohvr62UlunE+L3MsQ31OJZprNlyMlWLCQVE9QlYcbiBfJOrA6fpDhoyJl9D8M+dR8QwNAK2BP4JVgc'
        b'DwaMHwiINQbENqURmL6mZXpnokk8oXvhgHy6UT59QD7TKJ9JMXXC5TXGYYTu6dOW2mHXxB8Uu7dNaEkYlHi1KTsTe7jdqWczezIvc03hCZfzjOGzTCGJxqBEo1+SUZLU'
        b'nHobJ1M15zSl3vKf0KnpqMYA3H4wUHbCv8vfFBjVxNvn9Ot3hrHIlQ7bo5y2LINh8dn62ygfnyX7l1gtL1nTJqWg+lqNtAhTSgnGhpWKFPa7qEihO/VrW8waFNmX+wiY'
        b'HUSg3ahWFuxnd8/d96GeZQ+fH6Oaw7E0J+cnmvNT3CuPN/ZZ6PBmPC6lyCGhWl9INz8MCTVramuqNdWP3JxHOvUDoUNvtlOlh5a3Lx/wjzL6R5n8Ywb8E4z448du17tf'
        b'Qr3BDFXFGh15Debxl9ZWqkuIK4q6TlqpUevrpNEyhVSl19CZXmzQVtbJtdX4fenwWyzFmheeuOrS5QackCQYXcro4RoWDPSsK+Hwz4iB4Z8Rsxveac6MWhf8LxxOqSa+'
        b'cHaqWqJcsHxUs6akQl1drpHqaFSxmix01rB+LDiVWlqrq1mlJT4rxfUk0o54tdRqsIROxq9AhzuZpK5eQVf79HU1WNWhXLL6oRzRzA0tVRbSKovIuBooB2T5K2G8w6t8'
        b'eFzJ/hI7KvUxUKioGUED4VK9FrN+czaSjLgSWe9KsbTZnDGe/BRifJEZgBQRmWFltiyuqSG/nCQts7Z/GuhQlT4wTJS3r9bo8DRehRGDupj4NJktof9mL79TDl20Q8eU'
        b'ojB5Wno4sTFlLiCGQ+KWviMzVxWATodkhKdjyV3lKkTPp4kMxOtb7w57YCPqRRfnhWTIFWSZMCwHXkSH8+ToOF3+uhY7h1+OjsML9Dfx0E3873iOTq/IzkD7VgtcgTNs'
        b'5SqiFtF9FPACPLTIK8DanBiSIw/NlOdZCs/kg1KREF5bjpppeXCrH9qjD2F/nBDwk9AxuJtBvSDFQExa9o7wEtwK25VwJ9qrQjvRPhUxJuYy6AI8hS7PZjcDtsFN8CnS'
        b'oEWwkQ+4sI2BGyToAFVf5sEdMfo0hRw1oyZiaMyEZ3jABTcZPusJr1Az5jp4Hd7Uh9AjmPmPowPrGXRars7XZsVM4egJk/heqlw/LzuTGyU6UHk+4NbF03milL2LeY/9'
        b'pcdfIqkp+Db61Rc2BXf9LV9393bE3R/jezqkQasi0j+43v7dB18ov3FctYmz53cNbzYoXsiZd9zh94czjP1PGY5PPvjWis93lCX2yg6fLOD8pn7XXwc1a0tLha6nXP4Q'
        b'/U2V69TQ2lVwVVzmiaZIzWftqv7f9o3/l/009P2Pht9/taRhdUJue87+oZ5Jl/fwCkrzJr1417fg0BN9Xl/6XX1tcuZfL31y529n225M3NbavlRVNPefd/h33vos65N3'
        b'7qS/e2BO5vX49y5u+Be/848tdjm6Azpn5feF9+/PqH5vxaD4W9ndiV/aPna/ZeXnLY7X5sx+7otzn/zT8bv7kSdm+vl1L+kPmPleWJhmz2MyF/ZkBbL94QQ9pho1MnC/'
        b'DeDJGXga7i+ha67r0Y3VaB/cEiZH29G2iDS0kwscZnMF6OYqanbMg7tnwsYI8qt6LVj88CIY2Ad3wL3sz6g9DXfMDsvIzprlhh8FMvBAGNzDLpE+g5OdIpbQbBsgQM/A'
        b'vTyOEB4Ipg8j62BvJm1RIbqEM3ow8DB8GjZSK2xpDboyao13WrmVERZuQkdou1fNICujiWEKWaiFMp3ReW59AeqkTYMb8AzZS0yceRV81pBavpTuaQ5BW2eyhaMLbvhR'
        b'DgN74f61dPnXD+6ZSgyk6eEKuC0CT1LU60FoTirloecq4FW6PWVpOe4ZnbXwKuyjMxfujGDnbSi6zkebitfQoV8Cz66sXsf2lJj8tzHAvpSDOnJK6Al8q+vR0cyVcH+u'
        b'nAGcVUwiusD+ZBJW5veuJEdlTCG/HGo5KgPtgRvvERcZD9iOejKzMzPRPpCtQNvCM+HOXGrKDYW7+Dhzmz+70H0ev6de1JgDT4dnlwoAL4WBN+AR+JxM9F83KJHLqPOT'
        b'hk3AbiwbLRzN+Yd8zXjpoU+pVTiJ3Z1xJ18EXDxa7Zvt+30nvSOaPOju11rTXNNZcqKiq8LkHjHgHmt0jzW5T27iDorcWx2aHfr9onuT3xHF3XL3ahvfUoHjPbxb1zSv'
        b'6bQ3eYSbd3hM7A+eafKe1S+ZNegbNOArN/rKu0t7p/RUXV5s8k0b8M02+mabfHObbAfHB5+Y2jX1yLQm7jsi6aCnz4BnqNEzFKNTL/8mwaC3b5PNoK/0UFZ7Vrf7e76R'
        b'TSkY9HZmGgMiMeb1GdcZ223TNd3kE4XjPXxb65vrOz1NHqHdpSaP6MHACW2CwYmhbSHNuZajMuLek4TfdQR+UXecgMSvkzsgjTZKo03i6EFZdFPyO5KJZKvG7FvSoE7V'
        b'icVdi48sfU8a3ZQ26BHwrodi0DewLRcXul9w1wYExtwRAk//JusNGPa65eDXGJrZIzMe3FxBXo+O/FrBj5b1c3K80GPODONCTsz4JWd46+YBClOJ5jHKIXJ4nZB6UfGH'
        b'f0qQT88FBVYng3LyBf9Fp8gKjJbmE7SUzMIF87ZdFrYTuIelPUEIw8jYDJoIgtKbdUI7y5LpAyjrAUwlfSimUlCzygM51QRzjII4FoRSQ6AQWf+tJ2DMrkRdUsF6SVVp'
        b'qmp09XT5ucygY1GNnv256DEq8WjMb+X+XqfWlWP91JJy1IJv9fCKLzufLQu+FhhIwJxGb20D+hkuW3QNdk00PSQ9cvK8oqz5jhLz4YEF7C/0eC0qSljlVs5G3mKeA2vw'
        b'2+qM25F6OZqrY382p2N8kr4KODpyAIN2AXRaV2Agv3i2vhRuzbRCXARSmNeV4ZUidqET44984ju1ALNfslY84o2Feexaf1E8PI1atZ+ed+LqP8dFxl3+wNB8zg5GirZE'
        b'nBuY35hqv/3t1JdePPbkk0+68QoDs2fVho7LWfW31Hvrb2wZfHGF3bEJ3/3ph93XlH9ndmaAx7796oeUnfF5e8R/4nce1/tVfapigr37u7b/46vZnoNXf7z/3v78N7Tj'
        b'8/9v9V6vP0x62vuHnoyFX1Ve2avfF/5h/ofznM/tvz/9HfXLp37T4MBd0baw7M9Tnh26/8yAz62ZfwoNKfx4+sKa3D+80Pzcgghw5vWvdpWXpKatv7zsw99o3s1VZ058'
        b'bnzdZ1OPHcnM+HFP0yKjd+8kzx7dwf6ZjN8XmimNL3o7/Gk8+DFncuS6dcw7C0OOSO/JnKgAdUKn4VbqXTUXtpqdq+rQZiq7HOE570wFhoKt8mEo5zyfW2mvoB5cSngC'
        b'XbQafyo3XbxGJCd8CvWyAKIXY4LnUSNsdhw5uhZtraTLnePg5jVEAo6IvxyZlQBsnkzlK9ozPSYzPcWJ/nA2AQAREyl0iOe4hlnOJkTH0CkesIfnOeiULWSdxwKz0VPk'
        b'hNsZj0fIOewBt1VwP+26DLYvwtghBQNsgjhY7LBhCQtciE/YaPDQXDwMHtAldPQeWeupj3MPk/PQs2QNH7d81Fhw0Hm4nSmMEMKjiWm0QtWEGWF0tRhDja18IFjO8Uc7'
        b'4bPs75O0wu4pw2vJyqQRT7Wp/vRleKN217DwzJRsDPXRNvrbjM6whavz9JfZ/jL5bgusTpQyu+ebdakhJ7MoN99T4T3RLLxLXYBv0KEZ7TNMPmHkTGuftrpD69vXm8Th'
        b'gz4BTZmDnr4DnmFGzzAsT939WyubK1uqm7gfePgOP+guOVvRU3FquckzbtA34FBme2ZHdneiyVfeO/5SyLmQy3l9ciJ/09vTOzK7gwZCpxnxx3fa5RKTb+KgxHNAojBK'
        b'FO9IInGBh+zaqVXJg+wW6Ew1iWXm7QDdqSaPKOp1trB/SeHAkgoj/sgqTP7afk8tFqvdQWflPXJjUJzRN64plXTCYCI/nhLQacCIwpKxxCgrMfmX9nuWkiwhXblG3xic'
        b'2tPvkFO7U2fdibVda3unmzwTm/i3PPzaNJ0LTR6KfpHC+sRg1gpHDXA/48g/9rTgUWf+5ZOs5IjTEI6VN3a2C8P4fv0Lndp0fwSPOtGoDTza2KN66AYnamj2JEbtERM1'
        b'TikYm3LYtCwgdiwl55elx5Kbm3OfM0F7nzdBEV0m49HBHHIorK4pNBtm9ENcdbGeGpbGGpGGRIXDblLmtQUPi5XzgQcZZISJb88GcNtMUikDQZOMQZNM4kmYuI+O7yw9'
        b'sbxr+ZEIo09UvyTqtk/g0eRu3lm7HrsjuUafmH4Ju+Vs1MrB8AnkxI41g7MPsDb5fO4k86BarP3qJ4jV/hEv4CGxZC1BvehRr2e4VF9aKn9sioeXOrKakBu+ZHjdQMmo'
        b'OAmME1mDeGgu+oz78NbTZ7wYm5F1C5xOODZdNY6nVkJ+zlr3YRhWpdXjV1RSQQHPWm68NHitTTC1TwUPMcEyPksNYm1VbaW2RFtXyHIsvbamms6cIdv8+lrWUs7SB7sz'
        b'aIhP0d6QkF2mwg9H+91KhzcIDTkV1uqIi4GmkM3iZiGeUdHzCOkQFwHMIYnjiaZz/oA43Ih5ItYRHm9+vFty1q/Hz+QxGZPRgE8M/gwGyU5kd2X3Bl2Sn5Obgma1p/5p'
        b'XNjvI6Zcljzvd93vFf7vnN5wusNl5AuZbwAzfhFzBzB+i5jbvoGEYWIm5OHb5DDW/D1soZqLLzMwtFYy+cy4f/Ouh9/sQ+iIfbMxfLojk5ezVsh2PyR4LS84HL8MTrBM'
        b'Rw7oknFYTje85Us6smMfD5SOHlJoWVxgI5ZyzEbdv28EtyKie2MvxZ+LP/PEC7zfOr7k2O+R0y/KGdvB4T1HZJ6S7v0SnhXLMfMU8vsq920IP5FO0LPtH8s4bMiBXaTh'
        b'TsMNp/eFnGFjNPnJhpQTGV0ZvbxLjucc+8fPMHrM6BfNYNv90I1gs4GZ0zJjmkcW7RgLW6hmHt4HFRPPGe7DEJPQw9GRAWKp2/wSyG5k9iWYuyIoLPx/zL0HQJRH+j/+'
        b'vttYygJSpMPShKUsKGBBQUFQOspC7AICIoqAu4vEboxRFAuKBWxAbNhR7MaSmdwll0vulmzuQJLLefe9y/U7NSa55L65/OeZ991GsZy5/++b8rLzvvPOPDPvlGdmPs/n'
        b'qQTSBJmxJBBcQKJ8EcgVxDg5p3bG6N3HkEmVIytoS+12U+gcFf/dEoXxoGTyVQQTEtRVzypLmWVZSHDh4GWJJUqGqSwFHH3zU8pyieEHaXrYmS8YMEiPG2rgHHzwi09j'
        b'mATW+LYHrEuHqoXB7sL7QUPmyD2lBytcIxaZ6qyfKZppQCP1V7bMov4guBgadSYzyADm4986u2V2R9yF8afGd/uM/pqMQ8lsr3/wSZ92n87ga8qLym7/SWSkcp3MPnhW'
        b'PRsPl8DUeS8zk42fyTDhxjJQlekp373K8rtDsEbA72aQ7+7l95FbqM4x9L/bVjfy5unQ+xKf2VTLLbsdBCGKehnLA+H+a3Ke5bUn6FOJz+5T5ZZ1C8E6EHS5UdBBh2FA'
        b'ycE88+xZhrfpP8VaDFWDzRdwdGMxX3A3Vgl4andoom5eAwgmB6/JSl7Al6lLOGOpEsCYMFM+2PGmIQVjuwg/JTSNylRFseiazqxl1zSUncw4xaWlFjMODa+FwW0UV/JB'
        b'RmpuHUR6HWxi0pXIyXnt8/RuMTrHmIE1Y/x0I5intTGzz8aTA2x7WguCaZ6T3WyapzdeB+EpOpGhJki7VpOF2rPG4R/kq9k891fj5tJIdcMLfClN7QJL3QDCm6DL7Bi0'
        b'bxvrPZSv97Bn1zyY6agbn1XvnCRm9U5vNEB3cebq3cOnWQxURbC6jdQ5Rj6l5oHp5KnLFAnnS90g45C1L36B2gdgQJ99TrU2nejxZcCwUFZq1nfEg32RQbV18l2W1lZa'
        b'fBca3gGVAYjc/tPbp14KnYviv96FOHsr9eFnfUpOeLNPSW/sgVbV9PQZ48Szvps/83K9yfapX9v2ub/2ItrXori+9vxf1rawUKuuLSutWE4qyMlYQcZ7+wU8ZmWAAuMt'
        b'7/GO6vaO6hR3avTe48naycuvNb4lvkPc7RWpc4l84C2HmaTDtdtb2Zh638u/LZgu1rzG6FzG/L+sccFTa1zwQjX+rSDqhavcjqjVldXVaq7OnY11brrZCt3qWZWu1XtP'
        b'MFW6a7eXUueiNFR6MInzf6rSJU+tdMkLTinBL1rnVpR42nIAg/BJGAJODDoEGNf8fzbUDcWF5osG1E3o89XNHOP+VcGgaK4C1lTO549bS/7WBMJ3I3U32LYfH4/GiH5a'
        b'jFiBYRiRkFZIqodM2VTb6rRUuSSmWu8T1y2qriwDm9OlxRVVpWXmOz48FNL4DWwKC7l0yWcYZvwMhlsXoM0DncvT2vyreu9JjamfkmYddDKsPayjTO8F5IO/C4nsKL2w'
        b'+NTi68H6kEngTyb1vndAWxxsRuu9x8LvcReWnlpKegxZUXknPmRY18SnENEnM8/SvsOGaMv9pt+n7+FQPxPlFo2Shq/DmOvJVwWZNLWtK1tWNi/piL2QcCpB7zZO5zju'
        b'pYQfI/5hhK+p1lgIT8O3oEddH3R1Y+xReWYizjHGGEIo1vj0edQd9WzLxvoU8YsXWIpPw3egGXob6/5QCdfSDlZ3aC+sObVG75agc0z4oRZuVA/d9AwxK6q0FmLS8NsC'
        b'3jaJiunZHAuTQNM6neOIH0q2Rc+UzZpOWcUca6jZJAZ33rFYVHoDGWPLbP0Q2wjGdtHG8FYAZNyMJ28X2zJm7UMlsMToq4QqEacQR5qJXjXEjuuge/WCfIlxfBY+e4Tk'
        b'99HBVI75NoCiWiuqyuU11XUcLnZkNAeIr62pqQZu8G8F0co+diQZR/0MrbJPuqy2uEpbsbKMa58cl1CfFUmpvEKr6ROWvVrTby4z8QnJzZDlUP1UAovq5++8a6ZA9Dp7'
        b'Nk9vGk/R4+l6zwydS8b94UC7WtIxtX1pt2+sfnhco5BX1fk18OROH737xMFVdtIeACxNMd6nqPrtCQUZOZg9oJplOUk1ldVacL3gA2H7fggn+7KFC8tKtBXLOUelREGq'
        b'LNZoCznMRp+osFZdqZ4FWQINrZllobGX90mNR1a2FGTBQVk55A096YNWxE1mC+ECvIDqarho4QKYCPUquKyDy+tw2QwXWJurd8FlH1xa4AKLDXUbXCiLwym4nINLF1yu'
        b'wuUmXG7D5R5cMFw+hAu1VPxvu+gbYK7IH3lasfwF7JE0K1jOXlEikjk+tGE8ouvTH/gF6ey8e3386nN6ffzJxcuvPqvXeXp9Sq9XKvkVEKKz8/utzKUltT2wvVznpbzh'
        b'3C1L+FrgLBv1kCEXsMFLfAjBR2GMq899x1DOCtA1la1P5c0Ow3tdRoLZYQy1OoQ7Ex4K2OHT2EdioXse2CLaMPZuvTL3rwXBMt8vGLiQZD3g4vZQRIKPcljys4+IUdIt'
        b'CwALwKiHDLlAjEA+GtybRKINfyQQyWKpz42H8OsrO2uZz5fDWVku+1jCyiY+lghkYY+lAln4V1KRLPyxHStTmO59KWVloV9KhLLYxzYsCRp+Kb8ilRYLkcO/kkhkY79y'
        b'NF2sZIlfOrGy+C8l/CURLiFwUXwtEctinzDkwhkkAvRwKr44SYO34e3AssMWujNSd0EtOoxOD0BIwz9ffMoCvGugLSKlyhIWiGJF4DRusZR31yHyZFRilcTorsOKhKU0'
        b'LDVz3yExuuvgrA4lRncdnPsOidFdB+e+Q2J018G575AY3XVw7jsgbG/mvkNCrRgh7EbC7jTMueXwIGFPGh5Gw14k7E3DnNsNHxL2pWHO7YYfCctp2IWG/Uk4gIY59xmB'
        b'JBxEw8NpOJiER9CwGw2HkHAoDbvTsIKEw2jYg4bDSTiChj1pOJKElTTsRcNRJBxNw940PJKER9GwDw3HkHAsDfvScBwJj6Zhzq5xDG/XOBbsGlXjyDVAFQ8Wjarx6qDy'
        b'CWR2SehzAD6UfBN3WkU3GcyLp5EPb2OgGDN7yvsAIY8A3U9NCUqKq2AWWlDG231pKyj0zWAQQJ1QGCzCwCaAw6iVldrwODtLOwDYbDRjciuCea6Y42wprS6phU0lY2o2'
        b'1WoDWK9Cy50Ac9EN0LfJSdn5KfxbReZmaekLeQOFYvkCei5NXuOQg+YschFc0gbZeQtIrboMCmhTrKHGlJAxNTVYTt4urqyU18K6pHIFzNQWlHQ2FloSTPsA0v9iuRC8'
        b'q4MSYlzgSbmlHPTCfGkWO7RaMseoeAwODTAqKUIVUyCsNC7yaEhkERJbhCQWISuLkNQiZG0RMhgxM+aoT3Lf1iKWnUVIZhGyN4aEJORg8czRIjTMIuRkEXK2CLlYhFwt'
        b'QsMtQm4WIXeLkIdFyNMi5GUR8rYI+ViEfC1CfsaQiITkxhBLQv4WMQMMoQJB3lRmwD+GunZm0rT8Ij21QJSXPjCmSmxoFUYDVQncLRDR8xFRrmKI9yT93yt2pu8xeRkD'
        b'YwPgoEAE1xhhlWhOtuH+zNj+2xnUPDbXmIsVkcPCPHbOdNO7BeI4vg3Lmezl4KRKzuRbk9WFMM9Y56Z/8q0G5EXCbgBdEdIzHmmO+sckn2/juIFswFD39IGNnnNO6WML'
        b'+wSFhd8G9397UTFYTZkMraiZqELRZ5cHNtpLebtPCYfK5dyPCYEOTlxYW6ZVA+k3R8rS58D5OTayT1HWDI5Og3JlUDoNSrEBrBl99v3o5awKOXg0SbGmVk3WzGUkC6rp'
        b'WlG8lLa4T1K4VFNOs14CzF7iwjLuD+X5khleK6ROHa0KSxYBdJh64yvW1mqIuq0uA7BOcSXQ51ctrCYS0wqtWFhRQo3HiYbNDfrGx8VLtaYC9bkUVlaXFFf2Y1aVkpwA'
        b'4Kwh8tFBmiRD/3LOF/u8C/tVOVmrksGYjysmv5dq+myIkGqtBkzf6YKhz4p8F/gmZIVr+DLcl7DSlGnhgcKGQ+PDMNEnWVJHRNCYEbAOslbiVGEY+kxmFibvlX1u/cQ0'
        b'ePf8NSyaQKcni6bP3LyatW1JLXU6ZeJHfonUDGK+3rNQ51L4qZsPQI/aSvRuYY0iAGeK9kiNjiGo74fekHBwDBFkdB4ht3AeYfAPcdTawouE4a9fIHXsKQ8wd/rJ3/QN'
        b'oNa6/E3LP8EKeD/AEJX/A94l9tgb4hgECwqFv/7GcEQ0/FXwsj3wDaTZBAVzsQyxAxUnJ7RPOJG4K7MxBTaeJ7ZM7IjhSAt7/QLa8ltWtoh6PXxa/Vr8Olx6PJQfeSh7'
        b'wyIvRJyJuCnS+SU0iz4FQw8Dd2GELjJfN2NOd+Qcve9cnfvcT128mlM6xL90UT5yYIJGPXJk3APagk5GtEd0SnrcxnS7jdE5jtG5jTG5PH0J55Xq/2GHNlF2799CDLbK'
        b'TkILMlwTl/yEfGrUULXEREoXwdHhaqt5Vj8w3Swlek/FwhVEyzHTRF7CeJk6UYC9+6GsfAWkTbsKGXPPDiMsnWGA5cHSaq2JYpA6R/sP+Q/ptuH5Z8jjDvJ0GuWx9H0x'
        b'UBzw0vafs++ru54hjdcgtWPu96KfOLzrtf+YHfKpLi9AHl+Qx8TnpBjE1cUPKBL9YG8/QyR/S5E+SZJzDvY0tQt4IhPK0wBy8PY/vKeCp8pLzWi4hChMGBYiNeQ1WFBQ'
        b'gvVBfB8o5SrTvYUVZZAhvwogqZMIJmshkzdQeRhff2ER5GeFlv41eK4Io6DXMM4NRNhLuDL56BmVGAqV+LGxEmMHsmcP0f6TkmckRZFL6ks4WiGC/W7o8Y7KF24p3wQL'
        b'wlTgri5bYEmd2l/OyXmpKVEpqcn5Lyfn758hp1JoTsQw98BcTt482prM1D3eBs1AGtHP+EopT6Ek3JypWGVd8QoNTx4qryorL4a9yP+8QxHxP39GKUZZdqkwQ5cyGJKZ'
        b'FYTX9uShqldmzH4pXlr1H54hVZzlWBhCJ7Xq6iWwdOYoU8mKuqamGgiLiN5dy5GsvpRIf3yGSGNBJBeBQSSHfCOhzH+eNU9S8qdnZD0esg5mLUbipWSMKS4vM+sGNYtW'
        b'aMDIUD4tKT2HjEmVLyHUKVb952cIlTjIJzIJU1ldbimLPDQzL3XKS8zmRJa/PEOkJEuR6LheVlUaqa2OJH9MCpE8NPXlZCHV89dnyJJiKYvPoHTB8tDsl66Uvz1DkKmW'
        b'mqLJ65M/Z69KFkZVwH3Cd26O8XlaQd60l+vhf3+GWBmW3cmJjvJ0/cjTu7zU13n0jNyzLb9OWP8xG1ajYDoEv0OTc3Mz03Om5qfO/E9nFP5TPX6GVNNAKqGxTv7RXyrL'
        b'tbNSPoWMglPLiJxVVOPXGHcuB3M7TIbtGelT8sGZcIR86iuTI+TT8tKzk3Jy85Mi5FC2zNRZighqhjMFGuciPs2hUkvJzSZ9m0tuSlJ2etYs7reqINk8mJ+XlKNKmpyf'
        b'nkvjkhzobmpdhQbMn2sqi8HpBEdu/TKT9RfPqNpXLHuB8iMfzorv2wCzCY/biuC6QDEdMIo1pJ5f5pP/4xlyzbLsBqP7f3JuJ0UpTzJRT6XnTMklHy8lZyrMgtA4X2ry'
        b'efgMCeeChArj5OOWTzUubluHNIpSaI3VL9dbv36GCIX95j+e8pxSsnEClJn2683Xsy/Top48Q6gFlp3Vh6sXw8AOjANyOGQYZCI2ogzeZI0g6EFEMW5NXhwKkWJmeOLO'
        b'G54MhtAawlTK9DYwHA71dhWbLwhgZjoOhkYgbwxi52fYiC1gKs1j2gyMaZTea6gYg9dMpfjpz/NkA++RmPYD7xo2k+VPnc++HZ/HsSfAsY5Rf+eWG6bDo8GXI0qFVP1b'
        b'aLoCuPTzpEr3Zqk7JhG0NqGZu1W6cwg1aYSk25aXaY1bv179N4bMHpaR1zRrGLp9CBY7a/avgT2ysS1je7wSOlwueJzy6Ey5lnYxTRea0OOVcc/lXY+3PRpT7geFd6Rc'
        b'U1xUXM+/O/fGXH1QhtH9GklgZNw1n4s+zaJWWYvsY3dlr4v7/uxd2T0uMd0uMZ0pPbFTumOnfOwytZ+3tsE7IDSlvUw5dcGQk89ZBQ3saYB7GLgBZjAWqYYBnbpQAauD'
        b'p2CN5jJD93ZjA3QcCjhpOD0xB0JGmaOTNnJOIL8BYUWwyzyIoaGU338uHKw43BM1fDPevM3Zrcc5iPxHTUkjur0i9BRR+6mbV3Ny06uNDk+p2fznKezwIfvNIONEEHwn'
        b'MHqhByKGkoppQxvcprKyrIqUdJC9bfqgDgoqH6KgPV6jur1G6VxG9bq5cxAfOYCUTZv3XFei3QaW53TvlE4faqBF5I4+YOBWfwUX0EGp0sWdhMCik64huHOSB/ALFEW6'
        b'1FED+yPV6ulyjDtAga0KuoKmWjZVMuh8Sad19W/gAicrdO2YowgeEnhEt/spVKjPvt+RDe3sdGwwDQtClh8R+mSWJzYS/sDGitfW1amQpIQ/rBFzZzUielQjgpMaSljf'
        b'Z2dxTCPhT2lE9MTFvt95jK35cYyEP8eRmo5xuCMUe8tjGnWigO+v6lT4lQ4XijB6bvdH6l6WvwDIQPMty2OCrGWOXw9XyrwfMuTyqJRlfEdQevC8R2KBbz5bn2NiH58A'
        b'vOKJT2coN4vDM3NPBGbuJI6gnN56KBC5Rj0SS9yiyT17jka81yUDOMSz2PpsEo2/BSL45HO3gLRc8VDAuo57JBYOj6+f8khqyGASZJBsYkAnUiSAFBOpFPTFXpdgYDsP'
        b'oWTnPFwJ5HJN4uBKA1/j74yGO2PN78TAnTh6xzuI0q0D9bj3uPosU2ahkFkYzYx/C2R0SeYo2WkFPxQIXaezj8Ri3zyoYzvGK/C+Ixn0x5KIXvH1mabEsiCxHI6nnYdV'
        b'RQKsKorCqgYpDP8BQVDfuPqcLzkud1bm/VgilMm/tBHKPDhQEnDP4A14M75ju1xWY6fIwNvCc7KUwAKHdwqZsEXD8CEx6kyOGOCzEv75AvjwAcJpCVDyJB1rLoVsehpH'
        b'cbWE3hGZ3bGid8Rmd6QqCXnXukAQywJ4abFUbaOSkju2QLwdKwAAE7lnR59TInW1DEBManuVndqhXEa0bfs+535jYlaFRluxhkhs4R9JYBjMx9LBfKajSY2aKa80Dvsz'
        b'oyuNw3UUKFvG+amc12FFdGDrsy4sreXxjNZga1BcWaFd0RfQ/4wUhCk0B9hoDIZyMC30SY2JSA1pGEzm5GYEw96DpGpkG14PY78HN/b7+O+x6fVX7LHnLiNCTb4t//Ot'
        b'bz/B0Edpg0pmOE7bBMp8HcMMghV/weVU0dAiqMvJs82Q08qXyolfoBQ/I6f6oXMyKkdKmtPzIt9NPq9TYIRfMLgAMAUM2Q6osrNVaLRcBKUmhbOq0LtF6xyjfyjUOL/+'
        b'pjIOgRun89QATZqXlCor20FQwAgZwO3cibHeLUrnGPXDKLhDVBSn5DbCJ0w2rDEtaGeMVhZ27NMNpkotMWKsBU3LYEZQgzYBSmyvoCwGgy8xB1ke0nccYNQabJlI6W1A'
        b'NhMCzAy/RlK0G/hOnsPAeyYzTDmMfJRNKNJ8C2Up0DwvMLF2h/Sr8RDL6KXVZRypMUdLQ10jGHgBqfZDFnRFLD8sUgVMDTYEakAQceh6aHNEVaupKasqNfDR2JplwUUd'
        b'0kJMWFxaOkB9ps2CPGiCFgkoFNoi/dvCO9b1uE3sdpv4qWegLkil98zXueT3Ovv2OAd2Owe2aU+uaF+hd47u9RrR4xXe7RXOG494Tej1Cjy5pp38iqV4/Hy9Z4HOpaDX'
        b'0aXHMbDbMbDHMazbMaxj/C8cxzylRwJEztQj+/U+C7aHAX0vDSrJY7BS0qXFISinjDH1vKYVOkf5QFEs6CYtRzJn5hVWI4gi2Tozae4MUz1sUGuMQZrzNEG2Jwch0wiq'
        b'zKx8NQLuzkJ+HBT2CTW1S9U5tIOyxsL2sVoLu1+xtlpLdOdBC0sftUJhQd2B8dDzYorea9yllI5lrWktaa05h3IupnR7jdO7xesc47/5yGscnXa3+kVLFaI+e8sZm84+'
        b'3HIGZoccheOgSxKT4QJtw6bma9LeqTIPYEH6odSrjRq9sL8eD43BqMXPF/AX0Go0gBUkWvxjiUimIDqki3e3d4zeObY+5b6bX7d8vN5tQn2a2c/HIlY2EvDp0QCJ9/5K'
        b'YiUbCxB2f7g3nlMKYQ6Q4i2o1UInLMAnObUQd+EtEUqWScHnrLIESRaaoQHP+QVYHSR69tcMyb9C+q9IKVaLAKyuslJJVdYqG5UtOMBR2ZNfDipH1TCVk9JeLS4QFIiJ'
        b'3udMdT1JATh9l4K7mwKnAo9YK855DdEjpRz43KhHWtM7wz0ZlZvKncLbpUb4uTuFt0uN8HN3Cm+XGuHn7hTeLjXCz90pvF1qhJ+7U3i71Ag/h7AjJ1esECDoRKJh9Hl0'
        b'NDN3mAmHm8KOZtXDSEwno+MaJ1I6lndb40x/c05rXHwZ6jJISDldJUZ/nbICe1J6R1p+5wKXAteC4QVuBe6xrpx7m8Ws2tWDmWVFXf0MV4WNY1WjID9SV0LOuY2Z46Hh'
        b'xphSVSQX0+DqxiyWmypK7V4eTubYmD476FsGPHfFUSF0wml9bK5C3CeYmtwnSE/tE6SqyN/8PsHktD5h8tScPmFKZmafcGrytD5huor8Sssjl8lpU/qEObnk17QsEiUv'
        b'l1xUqfBgdqZaBhO2cGr6NKLLC5Kn9glSMtXAfkHSJWmn5fUJstL7BDm5fYJpWX2CPPJXlareTCNMnk0iFBBh0gfYSlKsNwzpiQKjz3Fgy2XIWkJk9Dgu+QE9joNp7YBF'
        b'Ex1FjYyuopxaoKiZgRtqoKdp8ZZcJd6eDb45TR45qS9MZTplqsyKSM+enkZ6X4Y0Cig+0SkRk4g3OKDLCTUVPov+IdKAQ86dH/++qwQ8T7qgB7jxvQ8bE+45fvgeI357'
        b'24lpy8NKYp2zYuv3ssKN0W/nn46uOcEyTofEs94JUAifAFYaHcY7Ztnmo9fQqYg0g6PHYfimEJ3TeFPqzWRmKm4IBm+KWzOylcDCfVDwasXSJ4Ct9kN70VbUgHbinZmR'
        b'aCfaacWgjSNthwvw5nC0lyx2BtulEHGjmzlq08W8rRkgmzDea4AqlDpF9GFc3JojPnIeQWflXL3nNJ3LNHO4poEchZsjrUy4UjVQMw/GJEnN7ningSZh1MdJxpeEZt6Q'
        b'i31Y1g8cBfq9qKPAfZIRzAnbkcISc2XN3tAyYPBPtDI4650vmi+eL5lvRZqqDWmqIjIAiAusyKDADQMS6sfLMdaeb77SfFuz5mtNmq/UrPlaWzRUaZI1bb4D7g7dfI0+'
        b'OozN1y+nFl4eHVWNzi7J5J2sgVvZyEjl9LQM6oc1FFpRwbQ6tDENdQgZvKPGFjfio6/UQlUWF2WZXiPNOjfyFZ5ZOANvx41ryHSzM3NGKN4yQ0q6h4hBN9AFW9lUvI8a'
        b'QVi5SMDNsWP08ICKJ8MdmVpKvP8WPheroezGozl+Y3wykka/6GHNkG8cHb380aS315YynMuJM2h3gYUDWUumYytmlhbvVFmtQCc1nAuJ0zPQqcx0dN05OzMCb1ewjG2O'
        b'AJ+onlvrT56WZaCL4WlAioybYqKj0caiTCYA1aMr6IoQ3VmNm2ujSSyf4Xh/eA6Q227PLjDjUw5VRobi+qiw9GwWH0RdTLVCSqbaXatowSLQpmmZeNNM3JCeFSVhJG4C'
        b'e5UbbdmcK4ptuB3tDa92gPqOJM/RTcFo1Io3c0/b0XFcH859CytGqkCHlglsJPgM9aKbMdoW7VylGiDF9FDqpX1aqFFWK3Bf0GQzo9CnFgw+fCPwKXQQXVBZwUooFDe8'
        b'Qn1ajMf70G7NcnxJxLB4rwS1MHgn2oy21oKtujVuRHtIjW+PUOId4OajhkTMDyXfuyECNS2MyC5IIyOLgXra0DpYBh8T2hHVow29wfno3Y4P2b/qYvBXj7dmkUI7TxXi'
        b'w3Y2tdS7w92lpMQ56/ARXniia2YK0D6Wpa5DPGVCFbj0wA3oVL6pyOg0apxOs2aYXEerGnQNHaNFRZvUmbgJbCHiZCuZ7Ch8qFZOArMjSbVfSCSf6WLdcnwZbanDl7QS'
        b'RuYlQC3oFrpSOxrywset0Pp0DXlE2nfEK6EZkaTpRGRkczmZqpcUATXh6zYM3oj21UaRV73Tx4VD1ZCqaogiDTE0lAzI9VE5fCXRJjopCXw6nLJmImfVghcG9CYp1glb'
        b'fBVf1uBry9D2OrXdMnyVYdwq8a4YIdroiDfU0pH+0OJVhQtwA2n62ZFKUtdixgntFaLzeA8+S/vMJbEI+r08enTCJO+FGoYyiJeurNYsI8upVx3wToYM9lfQ1orbFw+K'
        b'NLCRv+6X8XvzM1Uo2vGzyy6zGy+H/lPwxm+OWfnF2LsVWuXO9y7f/befNMV0uD34c9Sj72+eKvU/0fZk99qf/H3trxN3r/pGfD1OtK1zlE3bP3PWDncfw8x/x3v98KPf'
        b'fH/wXtobD9YEhj7a2Ttx5uPc3s9dGFXBl0dPvfPrwM9u3j2TtNlVd3bdgaKmURkRrTvOT9xyavK/tyz+9+RrWu2MkeMC12T+OXhOYkvzTfV30pqQv/59iU109KyfOJ2L'
        b'c361eLz9tnM7ysP/OuZcsv1c8Y2klIqug1vmnu2YvOGjc5OV7y/4082qmbIuJuYXj5dW/uikx8Ibujmbfrfpt3eu+vx4xMJryRv2hTbE3d6671bb8ozemCVv/+qPrq5L'
        b'/nU1/PPLX5Zv+mTuuWiHlvInU8tRAG7HV2J+fvbc4/fHL/751x9M/mnp2fNhtmUrxzhU2S25W/SrwqbDn/zo9q/nvdMc0xbqftd79ifJF/5ye+fFv5xz+Dz+Zz+5dnzH'
        b'ap+rPX/unThnjFdzzqhbX8/V2/9M3P5LwZ/wH98t+eTvxVPq/yD8kzLrVcHWmT5Wf7v0+z7v93bfSrn2l7eCjn7Y9bvPur0O5di7/8J6WVRnRsdPD9zauHL1cOcFv3jy'
        b'43N/KHljv+TLyJvRi+5NX/xkw+iPX/er+NPhvwz/x9w/fbD/sw+PHPa65fQ/uiNrJz3+t6zwTOm8r8sVgdQliBwdIcPUDXzcdqCmQLrWes5lx5bc0aRnz0ZvoB1ROZFp'
        b'QCl+QYCPK6poGqidDNBnzdw+U6LuDcuAqxvtR6epb+gw8AWNGursZTZqfEWDr2plEsZlmQ/eKFTZoXbqGxrtWuqbSf2F4CuZy9mkFH+qqtjgG+NxQxZZwQjnFjBCfIdF'
        b'B9ehXTRZ1IzuoH3gF7oJvUnULQWup+KdF+Cja/Bu6iqkMCAWNTgsx1dr8JVadFNMMrZ1EyyynsN5nj4Iw0f4WHwcON95wvfRuItL/jLptJ1Ec4sIUyjpQMow7qnoTblo'
        b'Pu5EZykRe3gB3pepzJYwAnS7YAU7QYt30IR9UtAh0um3ko68TVgVyojGsegii1+nDly88JkRmWTAI2/V4IPz2SjUiLY+gdkMncWbrDTL7ZbV4msOpGduc5DKbHCnw3Iy'
        b'BuCrdctGryLyZ4sk6IZgKiV0xzfH4PZwJ2kk3p41kmUks1h8dvpImstE1LEcN6ShcwwR7iJqX8NOUUVTjnn7UfgN1JBLin42LRuRKVqZkS1kPNGVUHRRVIcuOnJqZGcA'
        b'Ok+ioc3F4Nk9k3wFK8Z2kgDvm4M20hhT8Ea8DWjhzcaf4ej6mCyRbN5iWvuLPMh0Q2oYt0ZBExMzkiJBAPlotylbPSng6wWoIcptGj+AihnbXAHeW4VOUEp9MohuwLsh'
        b'gwhEdFUiKMmFzPESxs8WX8PHRbgr0Zrji98+YjQfj7RR/DpuIg3BnugrKaE+tBmhXcJZJMLWYVFQU6Si0gVu+Hg014SPoFsLqe/wSGVOVi6ZmHaSGJ74EL7jJVq2zI2r'
        b'jRNkCtxEqoOf0CLQdTKn2auE2UReGgNfwoeJQt+Qq0VvKiOJLpQpJG1xqwCfrMStXFd6g8xG+0iMjIh0otkw0lx0faxgwRp8m3q/8Y0N5p6hAxrSXepzuakxnbTLsFAx'
        b'fi0U7abyOqK31pKIORFoSxQ/m4gZP3yRwdfE4iJ0kWu8B7NQJ7pLCp2rNPkrcELnheSzH096AtPa2tRk6Bvm65Z4vCccbUE7oyzPkcLJvLY90Aa1okO5T2A3HK3P8e7/'
        b'Ln1xONpAPjWuz1JImCzGCl0iQ8muJzATLqpV02lwJ7h6J987m5RxR1QmKcAO7qhqKt5M1h4Xrcii4wraQ6sE30Zn0GHSREilI8NbEmY4votPk8HgbiI6/F+nZzB3/GNO'
        b'z0APclz7rXK4Exy6zLknoMucR5U+YBcV0jGmxy2m2y2GrnV4h5AP3HyBjrDHLbTbjXPBPkXvOVXnMvVzNz/qYjKq2y+qxy+m2y+mc+q1rItZ95zu+etiU+6V6f2yXsj1'
        b'5OduPr1+IR1x3X7RPb45naXXll5cei+9e3ROj2+JLq+kcSrw285rmdfjo+z2UXbUXVh9avX15OvTdVET77npfdIbpzzw8Gn1afHp8Qjr9gDf8h6jGiWfuflwjuPvje42'
        b'cJX0+gUD/VFHSOcovd/oRjueDLdpdaOo19mteXlbecs6vbPyV55BetUM/axCXXCR3rNY51L8wNmjxzmo2zmoraDHObzbOZwUOfNaJs0gQ++ZqXPJfOAdAGxpbav03jGN'
        b'1p85e7e5nfRu9+5Y0LFM5z/yuofeP5mk+0lweEf+hVmnZnWu+EVk0kMhO2IykId7pQB5uCu5krnHry2CCNFZd23VtVU0h5R7y7uDs/WeOTqXnM+dfdvGfzw6Sx+YxRdv'
        b'fHdwjt4zV+eS+8DZv22u3nkkSSQ0AjwfHF3dEzKmO2RMT0hCd0iCPmRiY8ovXIIehIQ3pnxM/voFU6u+gNAOr+6AOPLbwWghyD0x2OrxlogczfDBuTRKYMjJ+Pb4k4nt'
        b'iT2BY7oDx+gDx0Fkea88hEbmk+Ct/0aEcPaIQVFcimYuQvmjQ2qtCLnb3Q8Y0VbbEzKxO2RiT0jxvanvZr2d1ZMypztljm5ukT6lWB+woFG018Fs9T2MJ74xQKtEcEqg'
        b'Bn51NVjR99mWFGuNBrISTcmisqVlz+vwwazHQdcq4v8x9jtTh1N/QPK6Bit5WIp8T/rX10vIUj6X/ZqB62N6fYElPXU1cVwSx1yxTWKEL4HOBHNeWuahDlYtRwrDieo/'
        b'LYCtL2HN9JRTzo/Js28tAbShAMM00kFwgst5hwHyUHVZcWlkdVXlCsVLmDpy9hF9toW8CUZhRenTBPzOEnkc+ZEPx876bcRgZhwVGpP05uL+xxV4iqWYqadJCLuQZiZA'
        b'vvnUfgOsN4wmVS8rCXcaCybitdrqhQufJo1QZPFBo6hhQK02krwmB+t4k4UJSEgtXX+QilKPfUZLk4BgJhRyGEUhVyzkYcdLATROvl5ZFXB+lP5gVWZXaDb8PE08axBv'
        b'pLHeqHUHIKPLwZuY0XTrZaWilqyhz2hQdiCKCTIeMrRrYkuBzPMynm8vYAwO2SmtkJDfUmTyzbzFVbG+RGSzLUXWYvOQSWLpluKAu+a+dp+1Iy7JGZzlsAjkY6lfYCDW'
        b'MXgCFv6AnoA3KgTffmczxdzRrSXIWCPXLKqurSyFY24y2FEf6PLi8mKAJttoea4e+eTKsmIwtJCnUJ4KaBe8F1xqKcW7NucNDSo0NryH86KifHVtGZm0KriOF7akukpb'
        b'TUbWkiVh8sqKBepikhCYnRh869qA7YR2wCBCohjQjJynO850ZYWZRYiNhcv2oqIpxZUaknM//3PGtmr8NsKcii/fTBNQpx0txfVdJYfed0Sbzjq+s946331sDKOQCRzX'
        b'+SlYuoCwLllg0LvD0HaT6g1qN6qHhu1oaNj8ibxoYXmZti/IYp7TlFQW0jogMx4UU5OohFhUQYb34RygUs54y4GbQOdivt3Pw6ostQd60lBkAHur/wEd+SG5OJL7GtgK'
        b'/WY98+U8Ocs6vei+/i6JP9NuGyEcnG93Ee1evJtGMd25Z43HToJ80Q/oorH8uY6dwO/LfM3M/isq2H7fkhWWEYFOZ1rlc/vBcCs3Kz2bZchiaovtOAk6WLG7Ol1IVaj4'
        b'WC131HT2bYbdMsrOzn9bkl0zcyLgjYOv+R/wGOH5waL3pcXHR22KDmWzNzya3KyeNrG56PRHHmPnMJXrrbwEXymEdEU4YfzKpy3v0FG0jSzx6PLOCx+j3mbxYXQJXzV6'
        b'xMV3phi3kDiXuHLURTcs3KajW6Qx4h0L+q0DaWM8ia48z7EUaZ+a52qfGr59hnLt8yu1nHH3IYuS4ATy36e+YbrwDL1vps498/6IsI64o0saU/bmWhxT0Xbr/DTVlz+m'
        b'MrFDqr+GlvxPcvEUmfk3W0ZasgccU3m8iH8zWDkrBNxpyv7Y0sxMdKoCdtZEDiw6uQS30yeBeDs6khk+si4HnsSwqAt3CSoy5PtY2o+GrdN0lXyz8cj78ncd3y9F7h+E'
        b'/qjxR7usSjeP2nypOdoq5rVvtg3b9vYHK7PC7A55MIc+k3yk4wh9ngVmNmfENNZ+3/DBvwr9Djy7a69I+uVsuXRY+NcuwmGjHkoZ/+BuE8ulIe8ha9wyb/U3UN/fkouD'
        b'YeSAtcQcUt/WL1LVG5ihaH3phCygE56ITHmC/9aU96yxggz6h8/0CjTAfxXiO6yr5ADp7G3vOCJ3MuxnefhfthGWxzNZgr50we1D18ngDztDuMN5Gb+9M32O5QbPUDtD'
        b'/vi0QmBW3wLa98wQhP0PhCl0kH5gN672H03yZ9y9BkEPGr7tIPOB6duaHflSaM6/gQjDbFb4at0LzgpP+bZFzH9dmRkwCwyczkU5+RU5/1gk0kB3Hnn4y4U3YEZv/Nl7'
        b'LfaM1V723OMeA6Sy30zNQSr7b11xWEr6Qay5D/JwCvkg3i84JVNIFEvaYZD5lJzq/4KV/0jw/7DyBxydD/TlS7qV+wdTBRTM4Bp/jupSANHwt0v6rX+Wnbu83lX1gcuU'
        b'yV9yAI29E4TKgr1kqqSnDodQmw1uiICdXXR8jmgSi67g02jzE8B+FKEr6YPurA7a8ZaUkq6H9/KHHevwZtxOnapO1GRHShgpviVAuyRowyBtgOKPB2xfUuAxbQNyrg08'
        b'yYI2YAAf93iP7vYerfcea8Zq/vxNg+LmrEjTCDFvGpn/UdMwR194G77OMWgaroOiLwB8ZU9ZVw3wK0mBMwVnGUFYBR4FngVWBV5kAcUUeBf4FPjGehuRGbIfEJkxoG8P'
        b'RGZMyKmFWsSn0EXfTANioATfcBPY1+EdHGqAbpAfRq/h/bZqfAVfcYCTYrTenR5gO6JjAnwTNaJLVFXEp91W0ePrNNI4ctHZfmfYReh6v2NsvOlVW3RFiM8oJLXwUd09'
        b'0bFp+LQGjqEZ3MigbegOPk/RArPwLtxO2vQ+3FUrIQ9bGbQLd+HDVM1AZ4LXoI0KW3yVDNL4CoPaa/GxWgCL466JDlJ8QQOMzrieQZvGo500K7Q/eSbehG/bQvPBFxjU'
        b'jC+ga9w7J9Pz0JtuGnDJhXczaOsM3EnPuY+HUijJ2CR5UdatSZEMrT3UJUQtiaSzdOGLkNRRBu1bTVICuaa6aInA+8zLc3tYLXRA3IpuoCZaWf3O+XGnVo0vq9Ki3cPh'
        b'ZI877m9EzdZr8PFpHLhkO7qIL8TgxphogE60zsd3Gbwe75pEYSP4EnpzsQVWhfx5K5XjEp4+bQbeG5OhsmIKcLMEX0EH59cCjlsThM/HMC6FZIhnRuYtoAf4uHWeL24S'
        b'oo2oFaxaohT4VOU/v//++4i19LR/0qfJRZVf2UiZ2hQS2R4dDc00MBbDYuA13JEWAQuF7VEZBaF4C5FCFarAO2ekpWeDsp5Nmgi6mgelk1TJ5qGLaFdtEuTaLEMHbJMA'
        b'1GYeFZoUGZK2ROXy1WSOwIGWdAbdsiNFP+NSWwitZTV6XUbi75Kh9dFSMV5fgI9I8I582RQnT+mEPKLo38ZH8IXU8letF7ots8FvSeqkhQloq3WuHerEr+Nj0fj2KoUf'
        b'rh+vxAckaP9kBepKjMUt7qSZbEYNtbAjg+9azxeTcr4mY0ZKhaizAF2aDTiWLXDCFIY24ttkQbIj36tiLerA61c6eKHbiwO80DXSCN5AVxeuwhuFI0OJFNv98MUU5+x4'
        b'tFENjYy2tBFxnmysgCnK8StKqE6IZmibWSWdhBuy0dlpuD6dlDwKb5lGsVNGsAc6l5aTnT0bHaHLsPP4mm1JCt5DE/w+JY1pJMPk/YVFGd/Igpla4IFf6l8JBWgpQ03W'
        b'jNyO/H5l/hK0G53FN3E7OxJtwMfHx5Av0USmC3wWHygIwUdnE4nXu+ajDWWovhy34etWi9BbjivwhvRasJFagdrgsHyglGmL0WuRGWInV4AjolMK8h/pWfiMNb6GD+GD'
        b'+QqWQqPwHVwP680GMhXhHekReEcEPgxIJTepKJoMBnvoQFM8HW/KjMzIVqXRtWA6QKnCX6EQSGOj35EWgfevy8hSpkeGkfaxVWFX4YRaakdBFbv5DgqXAeCQOWSGB8zg'
        b'Q4uJdNCfFwnwufBVfmQIYxkB2sFOxhfRiVogevWOxyfC00jNbcvmOkBURnpkHgdrMwdMoV3oDgVNpaHT+TXQ/aflRb4iYFbkO6zA+8NrVSStVHw7jEMspU/ngW78ujte'
        b'mZaVSwurnC5djq9OT8vIzomIzKEYOuhrRrQUHZ7xtrxh6Dg6jhtoG8iZKQQdI+2CTZHd7sS5RGejECgY29WZcJhchLrgPFmKOwWoHl9PrAUgE7pDFvTHVLmKbPATH5Fe'
        b'MGMQ5B5DWv1ptJ58291421w5eeM6Opbmj+6m+cegCyIG7Z6NL+HXyAfQTKgFAOjkDCcyYHY5WOPti6X4kgPu0i6rZRkXjTA3Gl2hIzQ+V2qtgtFKSAa5s3hLOIPPOhfV'
        b'Av8tqcV9qDNTEUk3InKIUMFod2h/q8R5cinakPAqV8iDZO64pELb8/H2URMKSP8Qh7HoANqtoGNdUeAE22Gofbk9S/LaR0aT2nHcxHJoEhkp2smY0JBFHo1l8I5VwloK'
        b'KziHj2ZmmoBnqLXadrYAn1+HO7lBummlloeUAKAENaODLBGiU8StmBvQEXwrM4rcoQiN+WyUYDSd51LWEFWLYq3EjMgXvYYOs+jNuXg/B2e7ihvJ5+XRbOi0iAkqsXMU'
        b'upLEWimoyzFpOWnZCqiB7Ah0DF9PB6ABl9oItF68EL+2kopPJLqZyw3Y6NA6WgIpbhagvU7FtL6qUKN3uPHcHx/FG+zKhQ5oL26h36aW9Nl9maQ1ECFFkrksaiUr+4N0'
        b'PixFjV64ITKH4hski9HJeQLXMHSBFo50+FZb3ECRIKLRI3AnS8aCq+gkp4bsQNdwO3Rr8tAX3xrBoqNoUzDXFi5mzSKJ0keJuKmaRWds8fpaWG6uCcI7DJLSLUQiyeZc'
        b'Ipg/ahJbU2QeTItzSeJ3SJffkotO4ys5eBvaEmWsKbNaykGvWeFGSRLNNjp2LiBzFNkKMgJZjxOQrrSJ6BYUK3kzbwJpwZc1uMuKEQB+FO1mI9H6CRWvOqWyGmDkmvXZ'
        b'x9tfyazum+Q4f2K0RPC2/7Is341FaR+dOJa+ePekvtNbwwoS/P/2s4xd6vrGjo9t71wp2Pmdw9++/1vvgx99pbycGPHTn42J+fUHP9v23b8fOLymDH48WfbNtoosvz9+'
        b'sSatLSfbQ3P1n4f/nfzW2z9J+HuIr39uavGPUnZePXv/mtRj0RffuW13TZYtKxN3ycQxKKJpY7x6dmSc73fdDqXOjfX/OrHN63cLml2kK97aGtgbuPEvZ8eufCfh8e8k'
        b'XUe/u7xvy9l3tle6PLg3ZXOnWj2qL/m7szniQ4dyLky+114rviveNNplZFXQR7rSgqofn70bqGr6e6juF6IPF7+RdpI5Z/8b8bLF29dmZo250bJzx81LSyd8+Tt988/F'
        b'jxW672r/mvr3rjjVjH+9/2jcOx98UyOY+lqHqtghaszWYf+bv216XP6otYf2xH3v1Sc91+Ig+2D73vKxHy6uiox795POvV/tOR/ycHJD3MJ/zyzfrvvtvjCvdJ+P8C8u'
        b'6QTrDisvfZatuff9/T9e+x+vn/24s2nrnb07Wm7YPKmy+dsW9381TFi1pPb25aoPPi7JvjrmY9e6S61otP5L9sOTr2y42XNsZcL6hecTb16OLM+a+b/f/FpTnPHvkd+N'
        b'cKjvPXln27S/+HedX/2+/eabHVcrJ17+ePmlRzt8FulVb/zqqEg/4oHNz5pvX3997tjGm1bhsq8C7o/Pjv4ocM0vp/y9PGVl76NprTdK6oovhsx6ZwyjDWjp0IluBRb7'
        b'vHPzydyvAk7/ymeMW98nK/52PfdfG2aEFDicPBz6hduleV+uEk1QrGyt/cMXXqv/OnzJWZnStuGt+uVRZbaPXD54pS5K1dpzacd7yXHnncUBl999+8DMlReDGoO3lI/9'
        b'8V8/e1+9fLdcsvC3FanHj/y4esr4lT2bgmtmntvZVfX5g+96/nR428nAVJfgjgD9h5NuBf11m1tr3FeCP1+/k/9rScbPfjFv/e4ZoSvO7Hky/fF8xY1JP7E6/ru4sdfn'
        b'q5es+N455ua6HaqxOlVB8TsJv7fy/O2Fez/60jPmq7bL32765LrkwW/iHwTPrW7b8pe/bf2Hb9y18aNX/7Lqcue22X6us7f+Y2xVQ/UbNhekf/+j8+KxXy7965v/89rF'
        b'FF2ujVfZOxHxsi+mTV/1h+Wxaz++PWli+MMf/b70t79XKtZ8Z2uX86Ovvh2mCOYgURvR9amAIzOiw/LQZgoQW4XbnoC6nrgAnrThGxTXt5xNKsC3KWxuwUjUmJlJlC/D'
        b'EBsfRpMMQUcijVhCRNLh4ISAJTw+my5x8VHUtoJirwMXU8SYFF0RLHdBJyjCKhidyzMb+XEzS0d+dCuPe/k23k00d9PYXxBPRv501EThaAHo7kzAMPMwx9lTOKAjJlMR'
        b'BdThLvRmHF1dk2wleVGLBb6u8+iCfkHsmvAwpQIdxW/hrREMYz0LxqMtSRSih/YK1OFKmA4jyKi7dBHaIYhcsZTKE5+LXstUOqeaAFoOrwgry/B1uj0ehPeT5V0DhTjv'
        b'zOUVbrR+LRFAwvhlivCRGctoDnGZnuFKBc1Zghp80VlBTCI+RiVD219B+8N5cCMZWc8CwBEewpY93oPq/TRou3SZDF/SAPjZADfMtucBhwA3xFck6E5BIT0V0pDp/na4'
        b'5S68U7oKXRKithh8mcZhcWd8puEEIJd+4mFE8T4ZIkTbFqJ2amUCU/5C1BCVQBauW6MiYazPtGIccoWL8AGSDMyoc/zRxfDcCPhe9GEJPmmL7wjwtTR+t2NZKJnnQTnC'
        b'N/xNyhE6uJZ+rUmjVxlmQTKT7SXz4FjUxkHjrpE0r/fHvKJbMQB7bQ7jWso1MiHeJALycEHVjHSBG3oD36UwTcnqpYNv0RiQb/F4HwW/zcV7nsBM6Iy2onM85DIXn7RE'
        b'XYrq3HA7B3jcISJKOo8PRPW56C5q6QcCHOfMgQ13knmxPVxpg24qMujpCWmTDni9sBq3rKStGR+oI6uEBrJC46oB3Q23rRLggzLcwm1CtaLta0wT90m8mczc6I4DfTiR'
        b'VNklk66Dj+FNRNdZlko7Gb6+jOj4ZprOzGLQdPDuGNpsl9WgCyZNB1/AJ/prOu4+9AO74B3TiYA86FIYSdWS4XiTyCkng8MnolORQ2+FxSwdZBc6BJ2hA8wqG3wkc6ld'
        b'VjoZd/LYMLwP7eIgmCfQEXFmRGga3oM3kj4Htk9nBCsi0BVF6H8PR/j/74UeXMnN/hnoYKoflrHPoZ/XGM7e3rgx2O8p3R8cI+b2iPP9GXlQ6+qW1RxasdPqupPebwLg'
        b'/nz3r9q/qtctsG213i3mU99QnSLrPe3PV/1kVbditt53js59zoPQLJ1LcG9Q6Mms9qyeoLjuoLjOBZ3LdEHjGrN7gyNOzm2f2xnQOVIXHNeY0+sWpHcbDXcL2wt7gkd3'
        b'B4++rtTHz+sNHtVZqg+Ov75WN71AP7GAZpT2XmK3Ypbed7bOffYDZ4+WqW1TDubqncN5XOTy7uBUvecUncuU+z7ytuGAIdT7KHt84rp94jpL9D7xjTa9zsObw/TOQb1+'
        b'Cr5gQr1fbGdet9/YxjQwtR7btKZtmd4tlOY3Taea162Yp/edr3Of3+vmA6jOjhE9YQndYQl6t4R7oe8q31bqpuf3JBd0J3Mi5uimz+iZXtRN/lMU6X2Lde7Fv3H2aS7v'
        b'EHeUtq3ucY7tdo6FfMY0rTbk81DA+qSyXwgFflPYh4zAYwpAGaNGd7uEN+a0Tb3vFddZ1eOV2u2VSjOYr/ct1LkXPhQy3lNYoJ2J7rTqcRvb7Ta2VxHdbN8bENRi9UAR'
        b'Tn75R/X4x3X7x+n9x/T4J3T7J+j9Jzba93r6t0a2RB6MarS67xncVq73VJJfzsMb65omtAXqnYNpZRrqkdxfq3ce0eFkqOU8vadK56L63NmNN0xvG9W0lgo2Re87VecO'
        b'HGgtqzpir6d0+yXp3ZLoo0y9b5bOPevpAEy3/Yn7E9vKT1a3V/eMGNM9Ykwv39T8glrXtazrqLuw6tSqe6J3ZW/Lmtf90i/n04AIXeQc3fyynvkV3eS/yAp9wGKd92JS'
        b'M/JcqEIPv1b7FntdyJyP3ed+Bfw87fEdi64LewIndAdOuO8X3pF2Ifs6ey/o3fC3w7v9cnal3Xf1a5N2BPa4Krtdlff9IjpmAtQ1DdygLuqQ9jiP7HYe2esX0rqmZc3B'
        b'dSS6R2BbWkdpj0dMtweH/52j95yrc5n7G4MnyLa6k6vbV3fm98RlXJ/X6+XfNqVlYsfUzvlfCFn3VLZRRApNIk5omaB3DuHasN4zQeeS8AC4wQLJf5QbDJgLdqX8xsuX'
        b'80B6KqZD2xOV3B2VrA+fDOhf9x5FfLci/vpYvSKFpEyaRWMKgGHd9yfsSmhL1TsrwDtGSq9PYNuCljm7pjzwCgBYBucwojHlN+4hvS5Bj4XOHk6/cfN6KCZ/geYp6KEV'
        b'+fVQypD24n3A+6E1hGwYD3mr7QHbh7YQsjM8k0HInrzTmnsg96EDhByZwLCegDEfBYx5OAxSdGK8Ax46wxMXxie8xzut0/6elS4qrcf7lfdmvJfxz4euEGs44xnw0A1i'
        b'uTNefq1RB6IeesB9T8bT96EX/PKGXz7wyxd++cEvORMQ+dAf3gpgFJEX7E7Z9YQmfxSa/DAQngZBzsHkV6P4YQR5p8cjotsjoscjutsjutNF7zGaAp7v+5BA56v33PU+'
        b'GY1Teh2H77fZZdMc1xb6sWN4b8SoRhHHDNGW0u2o6HV02W+3y85wBxx2uHk32pkdm/hxxyYfwskIJUjIhYuKAmrLXjUi2szIB14ETfsDzSegNA3A5A4GiY8ClGk0uYSJ'
        b'eH+WFKE73Z9lVRSha3l9SK8vgtYFEpQuSZKQeVtom2QvVLCUmiHnOTA7bIG4gCmQ/PcwO8UKIoRN0kJtmVpeUlxZSd2XAVCVd89G5tAKmDyLKy28mnGE9qWlnOeRYnlV'
        b'WZ0NB5UMLSqatlSbXrWQVPqCyuqSJQoAoIHXOAOGrVZTtrC2EgBnK6pr5XXFVRQPVlqxvKK0zMYik4oq+mAhZaLjCVrKNBxrC+ftRA684/KKUo3Sxia+plhdvFQOBHnx'
        b'8nSKNSONUFMBXtpIOoA7K5aX1Gq01Uu514yippcWFSmA/NgG9A4At5Hy8NDPUPhZUSVfPkY5ihQlmRS7DgqvXVSsNeZuQujRFHjZqGs4imrlMHPkBXAUZ1FEA39Nubq6'
        b'toa6laApkKJoK0pqK4vVHLpPU1NWYuTx08hDgasrghSJZEMJaVfUkGCZtkSpoJVG09CUQYVoywz1xn8HCkKuIjLVkoog6cFXX2H4GqXVlB2nBpz9QRoWFdYPqTfwdNkm'
        b'h+5FhtinGQ7/kpzAYBhtRme4wz9YVaADi1hbfFXAbXZZGIqClagHPlybRaIlF3nxhyFyqRDOW24ui8Z7PH3TnIOXrcEX8tBV3IzeQOcmoz1zktO16AzsqkoTciJ88CE4'
        b'2EtBt/xWotOO0fjMDLpbXZJFTyxq/lJWFBZnPYXjoEONIeg1uoGoCgVTrRm4vm4mtf+2YgIWi/AZ1Iyu0tefeIrhlMpxU0ZRREWWmqnw3XRFrDlNnkj+x4MDo3m/s956'
        b'Q/PIH23weL0lq0X+1wmbij6fJlkiDx+5gS2V2J5YKQs9HPr21pB7jh/aj3lD3HFAqLqi9BK+rgjcePh9dyTVHxaUbuwULSv5c/QbN/ZaNfzrm2Vnfp46KmG696L4JqfJ'
        b'0sAP/l70yhnFpGVta7o31Izp8r/1wfDfjC5aFBotEn7Xiq1VXqjyp+5BGypWRd9SRgknj1TZu2UFHX6tS8y8t2X4zFV9Clu6hAlKQxfpDgjaJrEwkcN3JtB1CN65fHlm'
        b'LnpDym+AzMSvP4HDGNSkxsef85gfn3XhFjd5uIEuYHFrLj6ogSOlSLTDPdSwqT4MNwpRZ6KKLv+m4qu4MTynHL9lMK2jGyVkOfYmXR4X2KP14bzVoCqR2g2Kg+huQvhI'
        b'3IQb0nAntAmGEaxhp6DDmfRRckUqv5eADi6ktpLks16kNZGegHf3twLd7DdBJF2K7tJlIbqFLlPzOHOzwwB8zLAGxkfxLi7iRgbvMlsEw0JzvZ/5GliQ+UyQmWlpYw3E'
        b'ExwfpyXIzHifLmfAuASWM/ODB1/O9PJ2P0Rr7XELI//9zjeEzF+KSWxv8hRQDB8JWUUO2Bn55cLE5pHLfu7lR7QrkhrRxQ6uNhhzxXX7xen9xjSLiGbcMrlNdDC9Q3Aw'
        b'hyh1bYV6zzidSxxY/UzoiOUMfSjR1EdEeVjW7Rj6S575zwJnmPc0pWAgznAiTNGTyOWoOc5wcjDLusN07P7COEO2z4rMQ4VkIhqceI3OwqyRsoUjbBEaCVvEPyBhy0Iy'
        b'C18nQtioyqp4z0aWfk9rNdysXEbHZTJJpCanT1aZ+zXlp76yBRUlmsKSygryVjyFfRv4rBeCL5WSRUoaQ5kK18k0mrl7VD4Vvl7i5YBJjzCC0sHDmKaMilGtLoUbZNKh'
        b'kwTvwnXIPJRTCrKKqO+B2prK6uJSQ2kMBaSJgPsfo+8AmJ94SxBNbYWWc7RqzFTzfLlOnpxfFPG8UQueO2r6tOeNmjRz9nOnmpLy/FGTnzfqzNRRzx81pkjOK0DPETm2'
        b'SEmjpi/kXNFz6klZaYQ8jG8+YRZYf0sjA4pZ5vSLocwHpqiLqXM7U5sYynoAkpkBGiHXK5bHKKMtWhe1XuBcL3HNj2SwvKL4+UqanF9AsojneJM1XJ/i8uGaY0VpP6Vo'
        b'ICbKNYeqD04+FOozc19okd13o+w5Sgt0036FxlawKJzMjm0MasEnMrnTSSDx2IK7RvlHR0eLGUE6g49EVnIHyPvxaW24O96TowTIwD42Mx4d556cTEZvkMl4VE6GgDzZ'
        b'wI7NRXcpiUioN74Svio9B7YVUT07YXyiQkRPSIvxdWvcNYxMcV0O+JKYEXqyCbhZyh2tHkCn03HXggTcqcXXyIyK97L+aH8Qh2hqL8UXNAK0aZRawLDVDLpWs4Z78OYk'
        b'tWZ6Ar7qoCZy4xNsmDdTC0M43jLCBzcJQ9B5iv3JH09lnhm1FLBMaBtu5fFMqXi/QsAJcNI6n+iI9fi8mXTo6loq+TJboj90jRtvLhxudqQv4vYk1KHBR/BOMzHmoas0'
        b'R3kiuqxBu/EZo+R1aK9CSBMtmINu4y5RhnltHMb76LPZoY5EmA2Z5hkGoEMcYmsT2ofP26ID+OZya42IEVqzUeiEFQcL24e3oZ22eF+OTO3AMMIIdiLaPow+klWFkyR3'
        b'oE582daeZYR27ES8vqo2jaHH+bfQnUxQRFXUFAKAJUQ3JfWLdq8mKs42vBG9hfagQ/kksIeoS8fwbnzIX4r3oLecxAzehzrtZta8yrWywxWTVKRyw+cwzGImHR/HxznE'
        b'wc4SUhFN+bg+H93A21REOrSFTUKn0M6KzG13GY07yzD6mj91lRwhyq0nVW6jiXK7wWOW+2P35N7dszzckz02tJyd4O6uvp/cG9sW5vRTcmvmhpmdfyy7Kng/+IRwVsSk'
        b'9zw/GP7B+Xed3tlxyumPvvZZ01VTpIffdX9feu1D+0WeUx3HvBLzanTqZI/s5gefR7O/eFhy0SrjDyOF3/nXK/zaK21kHq6SuinrMmtCU5hfCVzEj2Wvrc6Jnijen7vh'
        b'xtmkKjfR5j3Ro6/hTzs2/FRU1SlzdE75yajXrH4iWva/I/7p926xJKrX78dF6zKK3scl1gsaYj+YwNZdEv1k9++dE4Na32sqE0zcbb21tGW9t9/79Hr6n9n1r2z+i9O9'
        b'Iz9b6v6N+wbxxU9E+5xtxPofV0arVB7j9IzNoUT5ZwqFC3decT1TZnZ0Z4vOozfh7G4M2sAxOFxETa5kfVFjPLxj0UHbGO7dy9nLw82YBOxQK9oaIbSaiE9QLTwZb8Zv'
        b'ZE4XGI4hfdEuqs9W4ztoU3i6mOOmEKGNLH7dZT7NLl5rhxu80Q6ewoMj8Jg3hj5b4IXuGuifxFmFnGZtM4+KYotP4/pwOM4j6ioZh84wUtwgICujw9PoyYoEX0VbNPjE'
        b'BFt8BRAtDQzuQJtxE3cmsxXvzkMNxfhsTRzpU3gz6cloPdrPHeU1oe2Ume1UYk2chDytBz25uZw7ZNyCto1ADQkZNXGQ6hYG7yavc8e058fjgyZyjDSRNoyjxiBNdTe3'
        b'SNlWYK/JtKMQG3SCwQft5nJVfgQdQzs02ky0DdWDPI2kpsdNoOuH4jJ0Q4P2Ri+3F5OXTjL40CzcyBXi1AJ8TYN3zMBXyTDNkmEKH0b70Fs0SVd0BW3U4Euoc/kyyK2Z'
        b'ZI4ao2kZgtFhLw26jrcvX0YyQ/ugOrawlPICv47OeWtKnOmap9+CB3ehO0QZfo59LFCG+fMQ3iJIQxTFvmGWtifkFl0RAMs+rAiqRhhXBNHdftGdTp3+Or9YWBF47prY'
        b'6xfeoe32i2mc+rmzZ/Nqnqthud4voTc4rDO1N0jRGUdWBj7xv45PuBF4vfRuxY2KW8qHQsbV83M3797AESfHto/tyL8w59Sc68G6iEn6wKRmaa9fYOuqllUH1zSLSPr8'
        b'QkSq95uoc5/4yIpx93koZYYHtOXrXRX3Xdx7Xf3pT/ApsmLXCl1QrN4t1vSeSO8Xp3OPAze/Hi0ebQv1HhFDPizTe4QPeEiE9Yx44Oqxf9auWbqAeL1rvMHZSf+YDwak'
        b'y73VNkLvGtrrFcJz66bovUbqXEa+/MNgvWvIgIe/H+7XGzPm2vjL4++J3rV+x7ovZuJDscA/iSzNwMHAQ0YwLJk1W0ZJOF4DO3OVX01d5PXDsksYA7Mgt5KaCXHAMdXb'
        b'BjQ7EAuuIyspxQsvopzUawWcWxDtqxWlGs5/Bzjs6LM3d9ldplb/notXUl21sKJcbQ3xHtDd4sKFFa+WlXIOyO0KKzSFpdVLyzTaihL19yDtfYhkQx2Da2qKS8rUeu6G'
        b'yQRLXAhLAnCfXltRarAcAYVL/XMwZPYYjCO3T1SYm55DMp9ckJeXmjM5PVXFES4auXP7bGuKK6p4bgS1jmZqYgTgNr6NJBLqn8OFkkZ8Y8mxS00H6PYyXcDSuqdEu57/'
        b'B85b4WD5GSes6vUC/gKsq5q5nOOOh/aMl2+bqlN4PeZeSbdzRj0cx7h5t8V1iq8XvBfcO9xrwM9HViIv+/rMr+yEsvCvbRJlJaRdw/XRJAH1PqH4Qsh6hddn/gZ8Sih6'
        b'XRLB8cQkzvGEZ8B9x8hel2RyyzOFrc8wufeIBe8bo6nzDd5hRSq8N5U197UB7i9ckzn3FLyjC/Ca4TWOOrrgvVqA9w33ifVpX0sdZLGP5IyHf7d7VPu4o+PJn/r0r0Ss'
        b'LBp4ir3hEk/GsSR2Mvu1sI6V+XzNmK5f0OtjtZCxd20J7Jb5fi3wkikeMuTyBbnn9xCCj+PhaX63LOArwXhZMgtPAr+gPzkWZLpHehA34MO2uFlrudXGMp5TRRXoOL5m'
        b'seowsKl/sQnYj13AysiS/1gtAu5jjvdYKeKZj7nfwH9sQ/6F38CDDCzI3H3T72EqJ5WzyoX+dlUNN/52U7mT3x70t6fKS+Wt8lHaqsVzJQWSWFblC5slRkZfKyPvL6uy'
        b'I1f4X0r+dzL8r/IbZ+XL+DIqBX/oIVTJ+7ECS+dKjHzIgeMEamtTmuR/W/K/IFbAp+fM/3WEv9Gm+0583vAX3reJFamCVMF83mHA/Ay5F1gXyAqcClxipRxnspkUNpQf'
        b'WULJUIfFSngeZVtVqNqugElg1TJK8BDe5wQz9GTq3Jgygy8sU1eAf7iVnjYDn3D+H22+VZKFZnyFpjpeoy2lf0dFR48aFQ/r0/hXNaXxMC4po6NHkv/JSjdGIewT5eTm'
        b'ZfeJ0tKnpvWJCvKmTjvF9glSUsnVGrIpzM3JmnVKpIbVWZ+Y7p/0WXOuqivIT/HCyuJyzYtkOxKyFamXwGAGfknUS4GRWZSeo+KcIbxgWuMU4n5pqetogqqUV5K+TV6k'
        b'1dbER0XV1dUpNRWvRsJKXQ28IJElPOGBsqR6aVRpWVQ/CZVkPR89SknyUwhM6Z8SUMpmdTOlA+mzzsqdnJRVSBb0344AoScnp1MJyd9pxStAscqDIxaNliSqjI4lVzK5'
        b'QGKnWPUmzvnEMpDVTpWeMzUrtTA5KX9y2nMmNVIh5OQyFvnbMf1enKyu1miS6U6DZRpZ1eXZmnKa0khISWBKiQi4DtJy6Fcf33oOXahvXQetPIWtRSrQ3NQbBkl7nHoj'
        b'3O2XyDiaSIz6dXg2dOYjvw1/gZL2WZWWLSyurdTS6qff8v+OueVgtq4cdP8WbsYXbXljALIs2QDmRU24oULHWAmoIeyHr17ZsNzSEPbCjSEMYfukherqWi1p+5x/E8uB'
        b'RGl4aGETu1JBFPAXNHwEBynqHeSSIDYzfKxT/AeGj6esOJ3pZ4MoTjqD9mRhHWljqMz1jOE8fBDrSJbaQgI3NWWljrUxWj7a/bCWj8W7SR3YpHMsKhUry8z26Tn39dyx'
        b'LgzkZvvyqtqammo1bGnWUFe4VJ3UxNvYRMr7dSx5aEqqwvI2dMQBd8bJQ8M0FXDmu3yMcnTYIK9wfVceOjlt4EO+T8LDCHn/dIYeH+Sh6flPjTHSLMbzdmV4pb8QhiMI'
        b'fluY22/liGZKyxZowS8873jTEBPmMy5a/89Qo66oVldoV3B+YULDYJYMIxnCPBnG7YqHwWwJ92DuCoMjiDCYdMIUStOx/2jlKGV0PB+Fe82ECIimj/hUTLdH09tcUgZB'
        b'OW4sXtRBGK+48oVoKOmVsXh0FcWdxBgPYmijG5yXimf8MeZpIpfiMubaa3/eKOBqMoI0SrkzHfK7Fo6a4NSG7u5TAEhZsRY+KBFyRX+aLoA4VHAnM3AiQN6rK1bz+BAz'
        b'x6m0dHJVWRnIXltZJi/WEj1kQa2Wy3ZyUn7q1Ny8WYXgozxXlVoIbqVVVAojloNSGGmMheQ6FVc+6pCe54Uz1Kthh4Q/q+CgEabzCnrGxL1hOl4I69enwozgEFqDNVy7'
        b'1tBC94s7LoyT1hClooq+xxNjEY2LO9IAOEiVPLUgjz9HqZKr6iq0K8vUlbQitU8RhuvgfFskDS5dW1y5gkYcugeHmdoEz9DFVZiJuAtaEl9lRhIv7siPl1DLYVXMHCdZ'
        b'xLUgbjP20sHPiEjx+GlcY2ge/dLh6owqqeYtLT05KUe+oKyyuqoc3ux39mI9YP51zKEHAsJp6ABuysQ7cKOQQVeyBfgoG4pfj+KsxNajLXWAV0Enyw0M9/m4i8Or0E1K'
        b'wFxf1ARXUXZ/yu0/DjVwduzb0E602xYdxu1knYa24Wvk3y60RcTI8EYBWcLddKCM52tQW24m3oWPmmyMGcYJvylE2xw8a2Mgk07nZNUziPAr0BtAJ4+242s21g6rFQIq'
        b'fwI6MA6gNHCEgI/iPXCMgDaXc2VrQEdibOnBAzqEjsHhA25CzZy18THciFvxHvSGmS8Ek3xGm8wamSwPXCGERuYUhIbirXhbFN4aAez1HK1/JGzq7ndma3KmcGdXt/Ny'
        b'NWjjKI6Hn5Lwa/Fr9AzscZKVKIUFb9ZFEfmi+UzteHJz9VqwJzVYmqJj6zJnpCkzsvEWUvKoPFyfNT1NmIe2gK02voGOrwhm0F0RWRmj19dVnIgNFGp6SSKOxR5LGy86'
        b'bYi226SK2HP1t2++e+PVP/zxt7+72PEH57Hd0cvsPz0V8f6fm/5558SCpPOl6R99n/nR7459Nm1DjN20eaIVOzxL7EYmbwlwPndTkj/O6udHPoreY7XVMzMlcVfm9x+K'
        b'Fu4WL/00+rQq0O7Xd5nTManFb/9142LxtBGHfbf3+Ny32zap4rsd5WfX3B758Yh/L2+R3Uz7eM63tT937Xzv599UzAjYnvylo8/Srt6ydaUZdU3frC61/Vv8+KtvvnUi'
        b'/A8Nwzw/2PPJ+BN3PldO2ptZ+Le1b1p9Evzd/LjsvV87/O/cgNxXRAoZtUiqrtaEKyPF4RzZ9zFBdBLaRCmm8PUUFef1BNy2ROCt6BSgcawY+zzhSHL7PN3bXjXN37jx'
        b'D9v+qBk1CpavtaVb/2vm4GuowQu/mduPL7vEiW6z+7F4T2YevmY4hQjFp+h7Vu4BmVxzQWfxWaMZEDqMWrkjhWx0gYfWOPmbwDUiafEq+jwxoMq4vV+KNkQaqK/Rhron'
        b'I8jzGrCu7MeijdbXcUTalEUbHUTXOB7tJnQhjGM8nxBi5DyXi+YDKThsczngk5AadwZTjrZzxzC4Bd2h2/ukI2wIIVlB770sZPK8hdnslBEL6ImBPW7Iy0SHZ+IdWaT8'
        b'C9iRuBG1KexeaucNtmvMEalmzMyDKvTm/Mxibn///2PvPeCiOtYG7j27S11AkN4XpC2wdBSl996bChaqoBTdBRUrsQOioKggKqAiICogSrGBM0k0N43NJi6axHjTi0k0'
        b'mJhikm9mzi4sRu9N7nu/+77f77s33uW0mTN95pnzPP/nUa4DQ0tvTM+u00qk6TWkP2p1U3EsIXV8bsho/s2CRyxKaz7WETcyazFuMq5THDc0b50tMuTVKeBd+meYPWjr'
        b'T2lT61u2Fon13d43sxv38hlRv6IOVj9gUfbxRE0ogagJJVD39I3HzJ3F+s5Yw59B2RONoofosXDyWAR5LIL61Jg7bsdvZB9RH3d0bWS/bcD7VNugMUxiwheZ8DvzJCYe'
        b'IhOPe/hzgMmhzPrMVstW1zFda9qPuVjXbWjOiPeItzxj+gGL4RNOjem6yQkz6nLqyP9Qwni+xhH2RjdNWVgO3os9uMViEciHIVUNTrfHwN4f/iq2lxD72hRdGX0cn3+N'
        b'2iuFvmaznu8K9VktSMbtrUW5EHThRwm70+lPrJufpuriDafkiMCkO+yQ0KCUO+zgpNAQntKzVMEFrlh+zCE7/zkFWYJlecJpEt4MWZ6r8Wig/Fz+DabfKKVqIAkPy3oz'
        b'COdGM1XLY8b/K5QbJNVn3cSyXmBuLlrgyWvrytYqz9i8m1xlqqLVzjy8pp23dPIbxdJnqMI4Std4k0BPrB5MaJ7yL8xBa8RstHZGAv3USroMF2WZVE54psQkXWvTNfsM'
        b'oYl2NE4/K/86+jo3S8jNLyrNwnsIaNVdiK6UlBdn5wlkelooUTIZFy/XZDpmgST00sm3TJM85F8jkzvK8tbSy3KcKxpMWkyrKkt1j9G1wly8Rp3KyqRbcmmauHYoIQKS'
        b'VLImtUwKc3JysuRJV8e09g/RU8/CtSksE5TnlJWj2KZicuKGyZTP5O6T8JPPkJZQvrIoT1YlUk08tPzGiUcr/mJUFCSMXVJoWCj+qhS6JC41Nig0yZErE2ZSQuen8CbL'
        b'J48oquPCySvJ5ZeV8tEfufzZla6kFe/lQqx9ljyHruYJsIK+vDw3LThO1qR4h0vkH0lnXBngVdpqSOiC0iIkzz9bcOOiXIUmxQXG/FFoo3XZnyO4yXxO01lBZ1x8RhqE'
        b'tN5wO0OyKqoXVEFLl8aVluCeI6ekv7ZsKnYcGIdCcgJWnMcdZrJp5AtKi1FWc7Ok2vVF5fT+zbLC1XklspaEmnIu1hKzyyktERai7OKQKOOF5CoqlckX08HkpXiefLLp'
        b'pJRmL8/LKaP7Cy0HJcd7zXZxJY0FFR5JH36Ho5QMLk0/EbtxW0adnoTLLxeQtkl6AzEAmBLm6GF1HjdZKlwJuWsKCpF8hu0HKlAsRUg6z8sS0CIW/TDdt4TCUiTTl0lf'
        b'RSuXCkpRQye6pqgopIWPGhbdjOjMT/ViJ24cEuqyVq4sKswh+plY6iXtUd6+gW57wXSfyZJ2chQ7nkG4duiX58jF8wjXLj41iYcLC88nXLug0Dhpu7WXM8CYzbNXlVPG'
        b'C5wcep5yviqv1PpPJERzWkKEV0BlhsxoAewBl7EUuB5uIesLIrsw1ZQYaowfHbHscihegxYNI2BNtlAmFoI2sAeeNQWHw4gmnKs1rCScLjDEo1XbUleQQEj6NKLZXnAo'
        b'n8Z7gR0mKTSt6IIlxZEXJa8hQWdSnNSDLxDTCNjKhFdhjdSLGPZRlyJl1UTz7dMiHKNS7Zx89Z/vTg0DwHpCtZDg0KxPsm/OR8vjfpkaGjgHB5AMeQlcK0/Hb2vPKvon'
        b'L3v6VVO+I8vBSKLdJMYI25i76MBe0Av6SCGx/cBFjlQxLg/up/z1QHP5anTDDR7BRiTOSXb8qHgsmtKRKMB9cLuqtSHoUp0SCQPgC/AIunF8JtgOTqaA1txEUBW0CRwG'
        b'W0A3+u8E+rtjxVpQB04FZS8G1UGCwsTE5YsF1pmgaUWBJkNND+7xNQFH1pqTwiiE5+E5DhxYqcZEdXXFHx6nnEEv3EKk5rBocPJ56QoHp1RhlSGoCgD12WD7tDRth8dh'
        b'Az7G2ntLZ8CdXAY4k6hl4J1L2kRpFDzEkeoOgiZwgnJGovzR8lx0CwkfSCyTiei8tAia4rayvDwF1q1UnwH3pUhLXU56x0I7rhq4C1TjpuKcOIU7Ay+ATmXyLg24Sw+e'
        b'BSeyygPQi8DORfDcP6DtOSfhUCkkw8eKJisUXgQ71cM14bXyYBxJ5Xw4HC3vRBSJhwmk1aBYowl+CjWl/QrCKFA9z30mauLVcH8SaorVFBxZpR7uHU038boZq+SjAVvc'
        b'SUwRU/6U0qZFCLZzQIOONTylCzpAu54uiwGaYrXQEeyhc3cCCW4XJ/l4BVZT+WLCNtiAXnXBB9XPFrgNle8RrEcJ9mUz4M4ktSQwDNvKsUxB0lMvt18SE8mL4js9y7ue'
        b'LF3q0zsM6nntM1DNzgT1irCe7l8tsGEZAQmh/CZG/NXIhfDwtPiTonTAlVhwgh7XToNOeEo4uRezgAjU8ATRkCEjTjYqmE6p78jLQnn3kdh1JDy3EDu5L3wx+TUF4W9I'
        b'1Fjl6nMgNTYeBGgePbjpQSpHR/P6j7oa2ceVZilZCGaLtp28HBuzW2n3y5zZL9f8fr3G9terbzgVfXHpMns97/6Vim9fv39/9cxNrGIT6uxbH44p/mbivPiBDjVmudcz'
        b'J8H8hc15qzJqb5y7FOaYXXNFx+VN8ce6nhUBqhon9c6eqbpzM/3ua+HZ6mfba5hnvzw9Ky5pqPfGrsO6D1qa54nt+nbNuQQPzHQbf/GzkQUXdiV+ds71Upifkq+i/Qcr'
        b'f7p2PmTzMotRqvHtuTMFh6KjVHYbrjbXfb9o2TzG46wd/Jz3PQ98pLPe4fSGAU3x2Ocpa9VtZ64Pze751AuobV1X5lDS9NUG9Y5vFV+vXPGDpKDkEw/WzD1+ms6zlju8'
        b'WJY91iU82n/lDfODYXEdMwdTNbaORHzZfdjm1E7eNap5Yk91xZXcNx65Ln5Y+foXgg/nHWlfsdprQutrgyezrUeMfD+8C87cMHhkf9i04KyX8JcfZw3/yBxNvi7wF/2+'
        b'ed57B1fnr4l9v/yNK4OuEwNvc97/tT/urNKpjBVCJdNXXvj045d3fml0W2tBk/6VioK6dcnNZcnf/hbBLayabV4yP/3Bp3sKam8VNq4N3qwVu9HI6jefv401e3/O03ij'
        b'vT/1o6JPtd9cJwHfRnqbdRqsKlVWf9T4vtPPTVaXn2z4qabrqNLcCyUgvcBHOHF6fvwTv4bFm6j2v5ddHcrm6RHMiAU4HhAt55/LNhLv/BiCWrIbMx8cBVsXwi3TGDtk'
        b'R8l3/iMspxoyI6Klu0lL/ALDQDcJBrtdQKcrvCyvTYs1aWEzbKbhJm1gKzqdwuAYRlGgWQg7iL6oDti14SlffWGWDJ1VrOQF6Anygi5Y62eJJrcpWA6NykmEfYTuMtcJ'
        b'nCI7VnHgqrw9GFsZXgKnaS3RU/BI2tReWkQZUaJ1LyQJBPtM4aDDpFYuqPag4FbYCY7Qm0ydwYEYMh8JzqCZvwPuUCxiWvpWEB3ShfCcabSMKgQb4X5nsAN0kG2yzDA0'
        b'tsmpwTKU4RWyT5YYRbbJ9NGLWqdtk8EjpjJ/c/Q22UE4SDuu2+WLBo1z8Kg8BQUzUNZIOUNHQRPK/x5H7N6Z7QiOgR0UuAR3GpDiWwAuBOI9NrTIGZLzLMhlL64oIZnI'
        b'g32JDk58vEepDTvINiXcZ0YcoukmrY2OiQRVzk8T9ewDXcCQojO4mkprRFfmoZUYbjdo8opHy5TUCo0Qli+4AIdo1d5DbsUy8z83Q2L+B3oAfQ9egqeLQY1zLJ/HZPjG'
        b'K/oyufACbODp/2/o1uEEPYdjMmVzfsfyGVs1z4KWOLBo0ng+H/tks+m0kei7ivRdb5vOag3rDOmJ7YrF8I+we8/e2uNadai1qUm4riKuK+GScD3r1Mct7OR8kNVp3LOy'
        b'k1h5iKw8JFZeIiuvIVOxVfiYpsW4tuEh/3r/Ts8xt+Ax+xCxdsg9S9v66HFdy9Zcsa5956ZRHbFz6D1Lm/roB4oMK1fRrKC6aIzgcG5yFhs5SIwiehUHZ/TNGPUUuUTU'
        b'KT3gynyYDax5z8jqAYOymY33GDnDnIcsyiaEODwLJQ7PQima8TC3fm6roljb5q6xpXSnMZBsMAaRDcYg6lPjWVKHYyd8GpV/vCengTsVJI0ESSdB0ql7+mbovpSBImW6'
        b'PGAxDHjojXpGU8H1zaTBQ0nwMBI8jMJ8Ce8Wb5qgIjZLHDNIlG2fpo45+o5Z+Ym1/VBUBiaHNtZvFOm79KbTWA+xZ+w9Lr9XR8z1HLKSzItG/24lZBDOR6rYMm3MJA17'
        b'nUNhOhXe0uf3OozqSAKTRIFJYrck8jIpGeZTfbNT63s3iuekjculJEZsFjtmEDtuMqslviW+V2lQbVBNmvwgkvxgkvxg6p4JtyWmKUZi4oL+9aYMZvZlSjzD0L9nPv1A'
        b'FVeCd723RJsn0uZ1Wku0XUTaLuPmNvUR98wt6iI+1jUaM+Z3lol0Q0bTb+aPpS0aW5IzHpowlrRwLDN3gkXp5VN1TFQc5jZ1zAYOLqnJ2Mbs0YGPSNvnroUdaseRXZFD'
        b'emJH/9vmlq0edI2KzV3qghoiCDAEO9nrVBNre4zbuWMvddbj0lKPEaMEWTnUhTTE3tM3rFOR2xme+VxQxdTupKDzj2rTf6aPY8uqP/Il5JAS19FPnYK807dFjhSVRDAS'
        b'SbiU0e9f2T3G0uspxdmMAU4gNX37WFEm12JX836KRO2J1lFUSlVOZXgoTipAKfwbFaDyecx1AapJeSW5eQLhP9sZJdtKUtEdb5RkCbnzY2Oeks/NGE/L57y4cn+8VLVc'
        b'Gz2lBZs4SenNBq1SUG9Nut0fTdCPgLPqukLYXo7tz9drej/lIx02aMnWuWdcyAdTM3gZCQn0cpmPBDH89TIDHiThlwck4TtlTmhd4LQa/USYRGHjbqvFCnPgdk/aBq/P'
        b'ZgWOHmO0X1hlxgB1CqCG5qNeQiLFUTSXd4Mt0i/R5DN0Iagm+wuaaNbalo61npaqqYXn0PsL2Zy57k5o/q5zd8GAumMMMGIJLxF7umJ7MAL3oxbmXA6vMZwtzOlv1b0C'
        b'V46KAANuz8PtsAv7oe9VIUkzhLUsB3gItPHsMR2tAiVQRZ/+Yrt1U2Q02AV6ydpHgaGox1QLMCGBUj3h2WRYy16JzfbARQbYCy5w6UCH1xUlZzhM4nQZaCo+lkzbAJ4G'
        b'2+I4KvDCpMWbmhrRg4tDItxx2I9N1+TN6NRm0ADUfUhC2wb7F+CfSQM8bUjb7YHhUlDJKYRbkMiDpGQ0UOnA/UTGMYYDsA/FWgNH5AzpDpsTLDDcCtpgUzKohQ2psBbu'
        b'14MHMKtXOZ6CF2IySMkPbN7DGM/xZzJclsb5r0+gt3ssV8xiVHKrcHVkL0ENn1yMUo1gLNWzpVC3V1Vm5dIXK9XVGY+wmnPCUrUqm2j64juB+oxWxwX4S7ePICGWFrWQ'
        b'3IwJ0f3ov3qwZYbKU5jieFv6m/01a1MOKomDkzsQlDMfdNKFfi0uAZsZnoQDq9TRGliH8jaDB8kbv1iqxLg/xxC/Ue1sUjr2pIN7UgU8Fs6B1yInq8Iwna6jXRYbOKDO'
        b'bdJe0Qi1U3wjJ9cK9q+HrRx1NIKybChf2KEqhVV7gZ2ewji84GfC+iUciotE5DqaPnxBGy0d4WGV1XBgBhPH52W9mW6QrWjBOcQRsJaAfvTcGSSVK4CtdGaq2RmwXw0O'
        b'KOHtszS4H932saMtFnfBa2GYmpNYDq4xEtFpN91EtiSBwxw7eyRhHHWAfTGoIqOYCxXgHhKh3zK02o0Jco6Cg+gOeg0FD0aoFzrk72UJi9E4fPhbwesLfl1hEmpw7N33'
        b'Hi8WLPlpyGagSnJy4GBK6N4BXl8Qb+5Ji7xP03Jqti9drvCqropuSLW53fFW5Zk69Vu27NqyJSKRFxoSohOiFfgkUpO9+eHmld+sXl1a8sGyAWHhk5vO6yt+2NjyWdPe'
        b'o01rHn/zyGZFrWRB962I3m8+WPw7uLXo5TiH3a71yt+0xF5Y/l7Wx3s77GyOcLtfV7xppNqvKIrasWDPofkx7K/nv3tjfHekL2ttErX35fovVq6Ne/D7pltmMwtfqzj5'
        b'EZf3bd4XvrWrzr/a+Hbdlu+aOioOl0Tl3vki7eIbIbOLSk953jEMXNzalBVz6yve+6Dx0Nnmn09GuNZz1obYtPd/eiXTe8Ttq7yKpvzIC6omoUcjNVouHi1953RR19iT'
        b'Rb+t9j20t6n/3e3vTEzA7w77+Wp9Obxh5/a7D75sL8l/+dUJ3ufrbEM6qC+/M2xtVBauFl+27Hm/5cTjTzrvt3XOjj/yho9WyYwFj+uDbjZ//ro+v/SC90fnN5g/8Liv'
        b'+6n48MTaHb9WZr1o/E1OROFvT4bf0Pxs3Wtnvg3lW9/aY/91hdGylRkprylVvvshGL7md3VR3weBOepq7dttDA7MNDzgdr9+bemvrwW++i2b/+Z3iqH8io2bQz8cmuml'
        b'cU7x2vJtpWE/+RR8lZxyImpHfWbK1fJdgoLEQftfZw383Oj6ZVe92lw9yr3mh5Y5bB9ThSankZ3Hnxi89GLB2/tPzX0ndYhy+uIbr5WHPonWOeB7iz3vcVJMs7fdR+yX'
        b'fj72Q87pD9Iq3Te+tre76QWPuJcLz3ydqrol7PaEis3L+64eu1B+67xg9chF91Hbo7XGRxSezJg/0bLliXbkRg3fgtcVX772mbbf7zuzf/5O7aXT96/Vq382e+DvKQuE'
        b'R/o4m7/zNPqk9tHeu5HLhl9udDgw+8gPEcFHXYzjxsFORvjBlu2fz602euIf5Ppq6qqo2o9OJHy1Qa20J1a/9ZcbjNMtnTPsP1Fv3Kj1c1/R5c4q08i3WHfWDRq665t1'
        b'zP/8p5SPeY3JxWvBHf5Spd+Yd20Ht67JW+i26Pjjh1e09+d+W/3GSZ3bZx+t8j1xxV/h6rtHeJm/nwxPMRF80/hW9urykZ05SVafnvp8buI3wvhk/SyH93/7/d3QNw98'
        b'H3KpIvQ3p/LTmT0vtnh+VnOU0510+UW1Vfrt3auHFy3gcSpecj29r2ttaHDxQ5+QJZWf1zD4Dw+9xq+b6wyPpNtFvbFx/8pBr7GvH8/c7LnHIrNm8dYvuXNM+i1a5379'
        b'ptLQlweKT+fyf0sXvv/A/7R6yZOykW7hfYVS7QDHh67qcU9+f32Bd6P6z6fLwJePNnud8ntvU8vVVe9ue62HdeHFD1rtNovnzbz/efanvdqDAzeOGY/aOx/44HhBZ8KH'
        b'h75Y5OJwV/G13mOju08ein5iarT9h9jXX3X/26uXxzjz/v5iusD1M4X1m7ce1Vf8TGFiwnd0hRHnpF7yu4ZuAxcH3AuKhgf6P7u8uHjZ0juC4mVvDl6888boyEt33th0'
        b'v3i5N+vdkfR3r87wUuz8Wu03/vLLX/lEmyfEfHX58tsFm5U33vH/KEDhx1/sbkX3/rBZ7WrlUT33Lbr3tesybjU4O3zikPBT8q5NGqLugbsvvf7iMsNN+09vLY3M++Sx'
        b'0a4P1Jc/cq7sdqvqZmx3Dsy3Ptz1dWjg3fS+iusXx37/ffeZCwf9J1rOt4PvzH9zdn5zRPHr1yIOlFZGHdwcnVhh88ue43fUfjL7ePc7rxwy/2hwb9kHhzjix7UxVl8q'
        b'ff57y4YV1XcP3Tztebvq9/q7NSnszT8tMfm7/ZNmo4qhD99Rf7L10n0fbrberTDhSZvb7jeb915bl+XzqbooXkfc8JHb5lPzv/0188Liu9Xr7l9y0dm4HK7Q2Xu/+K1X'
        b'Q45WDN9N/vKTH51b+V/Oc1gTsfnQhvm/HFj/Tambxeu88Du8IhqL0wM6mJO+8uQc5V1AawHsLA9WW9Ci/7nV8DjeWYH7sW+PKfTPYTdax+eqCzxF6/jI9h4qyO4DbJ1N'
        b's2V3KZpGw9ponhPYCtqlj8xwYS0D9aCG3gCqhl3hsr0Uj/lxUypH7f5kLyULdoGRp1SO6I0UtIjYRzZTNMEe8rbgLNCBn8R8WL5TREycAuwtYujFsNUXwz1kq0irBBx3'
        b'WAWvTTKUMUEZ1JfQublYYi+kF7RqYJi27FKHI6wA2KVFkoLWMg3WwtB5TigBfEEcTwUtbvtpHa8qFsMDdismV8B22sJ6WwW4HA0HwZBs30xxCdNeW4VojunCS87RMfaK'
        b'aMo+H7eImgP3ggOkvJeD0/CyA1oe9sMqZ7SSxgncy7QGzeAyibUYVAqiHe1gszBiCjgLdjkSfaq58HgCB+7ir52BVl67o1kMJXiBGY8ScIDkLiwYnMG38U3dudFoUka5'
        b'A7vQUsat/BENsTCF7bCmpFwK7qdAF8uS3oM6CDpdcFhQawj7+JHoxarMdHjQiezQ6YGBuUL7SLhnJaxOglfgXrg3TomhCXpZZZvhLrILlVEI90SbFBAME4OhAK8yWeCM'
        b'H01Q3g6q4GHYHw3OwVPwfDwHdNkpMlTgIMZeHw6hc+YcIHQyBPt4sFoFVY4CQxXuwYqc+xVIztzAkXicOhUeOAcOwV6SeXVwhaXNo5namJqR5IDWT/LG+TxwjG6iZ+Ah'
        b'NVyNDk48VXh2FVrIdLEZMw1YsDLZmA5+SFuP4xS9lgsHeLAGZV6DmYGWt3tpkvcWeD5EGEfpwV56KdUJtvJotNZp1I5hP8oyLnKHpEDM1VZgaOmxkAzTPIs8Y5CiGx0H'
        b'WkGfI6hynnTEYAy2sMGppeAief2cXLhD6BQJetQqYAd6hsHQUGT5BxfRqT8Pugs5UUVK/JhV4GwEaphCHsUwTGGHwyZf0tjUCkA9ugaubMZLVbRkh/2KdOdu3JQUTfx9'
        b'wAuwiYCdNUADywfUBpH3BgliUJFEOXjMkWdCr9am91x70Xr3pNALno60R0ISCzRQaDlfq0GqG7a5GuO1vwJq//0MisMAV1zhOVKVNqADNkTHZGtN3082g1tJyKgEVIE1'
        b'K6xktGgKHAfH5tA53YeS0YikNCSJDEzbKYXX8miY9HF4ypBjt2IzKoVVMShVqvAwE1yGB1eQvciNbFuMNm+CF6Ni+RRDxZUJGnPgNhLUFmwDnRx0t8/THtVWDRrnCpmF'
        b'eCAkRcWFDR4OqG6cIuGpTOw5BhUGqGVlbwb9JOrlG8EODtw2085pVRxe5HZQsAWeySet0wMeg9c4weAsD/UMXCio/TdS8CI4DTpJnjWM4cHoYiRoyfZ4KXBpTgLd8Vrh'
        b'MZYQ9oDzTiS3LFiF3WWcXkfXQR9o14+OCcogn6QUGZwoJuzIgw30uNoPh+CgMGbmEh6SOjETHXUbNSZqaxfp6oW7F2QIUeUJwsHpGMytUXdmKYPKhSRNHNg9E48QwaAb'
        b'67NiN0NDsIPe0m0A59fAfgFowB6skMAMrlHGUR70Znt9ljOsAX1ICpAja/jAS/QAs53iyUSVfngAySqwx4HmSuwtAXXk4wUYRIPBFL8ezTt19Fv3aWwQRsLtyijBMc4U'
        b'QzWACbpU4gnRIVnNRIjB7nQnxgiaGCoGXGHooFEZHooKoZVyTxaAHiHcEwq6eargnCPqwLWx8DwaBA012fZIjKV347fBHdkonuPOsrsKaRSsBvXwKt2yq0FrmfSjAA8c'
        b'XExhTPshciuzUEsILkXA82WrYT+qRi1qMTjpTDJum8QVElc9lLEyOMZA7eA4aCaBlsJDaP4SlDjDKjvUi+AxChzzpL/neM/GcI89dmCPX9QaeyZDCexnzkXTVjNJ6OY8'
        b'0IQVtOPRLGGlgOYy3HRmMFm5RnRocAH7AXSwM4KHZaMKdu3iYUUY8qAuEO4TxuHv9HgSQ2OudNQ0AN1sV9ANq+jSOIFm53MceHINmTeI/NaMmjbo5pNqiwU7I3GhB4Iu'
        b'3LNwcanCi6hBoLZ9nAw+MSoz8ISMtXQLwOU0iu8HBkh1lJKGXRutAqvWoD848mTQwNDGrshasDI0CZ6/AvZFm5VKncWgpg+PxtMd4xhaqQyCGnAQbKc/LuBPC4rwCgkG'
        b'zoLqMA4zoVxdBRWqBRXIlg4vpbAWbhPC3fg7VyGs1aFmgaPwGsmrQhY4STegSNC+bBV5Rh12sayL8ujFQXtUJvGkA/oKneU86cBtsJ4sDqwL8CcflnY89jZVHevIi4xF'
        b'Y7rUxYOXjyIayRpBq/SrzTWUcPqLijI4Tz6qkE8qffCFR9jwAA4Z4k91qKGQ78/TndicgGenIPip8JyyM1pMXaX70a6ZYIhDnuWv2pRAhmYt1EnBiRDYQnp9RD6qkHj8'
        b'NS+OQWdDI5kVO38t3Wh64WEF1CwO2vGkvSyUCU57ghP0NLh7LdwpBL3ucTwy4h+kwB60quumx95zqGwGhOiWICGRHk48WSpo6rtMr5yOwW0mkyR/cAlecPyDz6JLRmRK'
        b'zIUHpvIALoFT5HVacIAFTlrAfnpq7fKwn+YNiHgCckLp2a+gkhhARowwWO3KQS1hG5kyWXCQAp0W4CyN7q8NwK6Fqvl4IKIXS8oMZiLYt5webPbCeiMOPIVm7CgKBb1A'
        b'YddLAfR65SIYEuJ8qkbF4vYSzQJn5zJ0wDYW6puHgx7hXejVxrkcHqMknEEZMeB2XXr+Cofduahs+5xV7cC2KHsynmsuZ4FqWAkHSetMgAe1YD+4aubo5IQHgyY0+6mt'
        b'e4S3tEE/pcXBvYC5EA7zKDM3vrQXXQO1whiwG56IROWlgnIkzY4BrGPPU3Yn3cHZG9RywKEyPsmOohlT21NAt+k2uAut+bEXQV3lOL49btOo+x5Eo/0uUhC8NXC30Nme'
        b'0oC9ETw8BF1hRsCTuqSxFMCrWGPqqhY/jt7a2UjBA/AqGijxojAXXEa1POmRAQ8B1vG0RwbQkEq3p33l8IzQKdkqqpyHhgE0PTGZoEGnjIQHp+BWa+niOnIeODLDDg9w'
        b'6nCYNXcNGqtJ+BPL54AaG7BLZiKADQTAbiYxkAAN7s7RTrFomM5cUkH5wMNopiZz0HG0/Iim7QbACxuyKdf1cD/dJi7OmothS2AH6MLAJSlsCdRl8gz/d5kguLS5f/yf'
        b'vNMFRQHZ8L9j+IyPl/Qt8s1yHYf+ZrnBhXhHxoyf94xsxmyjxEbRYzrRmN1j3GQsMXQWGTqPuQSKDYPqFMf1jA6tqF8h0XMU6Tl2por13OtY4wYmLZwmjsTASWTgNObs'
        b'LzYIqFMYNzCWGES2sjs4bRwJ10PE9ehNFXO90bXR0BdV8H2zVqsOhzYHkQEfndFf1ST6UZ15EqfIIbbEK1LkFfk2L6qOfc+cW6d229ymdXXzZnSgw23V6TBvMxfruNZR'
        b'n2rr3TYybgxpiW6Klhos5IhN3HpdRSaeYqPZdcHj3Fn1kfeMjFvsm+zHDQwlBvYiA3uxgeMEi2msVxf8QJFhYdUa2KZYF/mxmWVd2PgsXodPm88Jv7qYcR2uSMelLua9'
        b'WejNGKJ/YpN41uyp6+OmNhJTvsiU35nVU9BVgCJvUW1SbZ3d4d3mLTZwxufKTcqtus0z8CEqn9aQjqi2KInV3N7ZEquQoXSxQei4ifkRJYlBUGtgR2RbZGdub6bIKVBs'
        b'FSS9HiK9nt+7QeQULLYKuWdoKjEMaE07aYT+YAZ/gMg54DFDw9DoAf4Zzbqx/PrycQurI+kSUx/aQqM3X8TzecxgmpqNWmCa7DjXqkOlTaUzTcR1l3D9hhQl3IhRG1Qc'
        b'wZQZKg0zS4mpV2tKx4K2Bb02ImsvEnIoa6RguGCca9HBbmPL3ZRYBw+lSaxjR1eLuXEoCn+zB5oohpYFTQs6bUSmLhKT+N6swRV9K9Crra5bja6GjuLZ8ahKjoRLTJZ0'
        b'siV2XiI7L3Q4lDiycHjhTepN9ivsmymS2EWi2EXiiMVi3yUTxhrhlNEDM4ahUYt6kzqqic29uo8ZlG00JUtPGu23w1dk7Tu0XGwdKeZGPWYxbUOoe+bW2G2DxHyOyHzO'
        b'kKrYPHhCgYWKShlHptikOG5i2hLSFIKak0mbicTCTWThJjZxH5/8+CoycXnMUDI1e4B/ehMHF/QtGOfaSLh5nR49Pl0+Egc/kYMfOh11veF13etmyJsxr8RIYpaIYpaM'
        b'Lc0Zy8oZi8kVB+fdw0EKZEECRA4B6HQ08Ub69fSbKW9mvpIpic0WxWaP5eSP5eaPxS4ThxaQt0R1uvbM6ZrT6zHo0+cjcQ8RuYeMJo9mj7lHih2icN4V2xRby3DDlNh6'
        b'i2y9xVyfcSv7k6oSbv5YYqokcZEocZEkMe+txDyxcz76vakzqNKnMmQ1JBxlDvFuuYSIEvNEzvkT6kqzzSYU1FC5GOFyQW1YWi5PvcNLZOsl5s5F1WxqRroNrkSfTqpH'
        b'oUuhM7enuKtYbOczoaKAIlLDEak0qeCIUFGiCpdw09GT6l3qqD0s61s2lDtSNFwk8YsX+cWPJSSOJaWM+aWKZ6eJ7dJRg7NYTN1zcKbLyxv9e8Bi2LtIeLG9gYPhfeFD'
        b'ISMxwzESnxiRT4zYI1bCKxhLTJIkpokS08bSMyTpOaL0HEn6MlH6MnFiwY/jgUE39K7rSZsWalQZ4sDMCSW2qdkESxElVZPYX7VqP2agltFp0WPXZTduajHVgk3DevMH'
        b'S0cVJCZJN8NQuzMNoXAPmtGpJ+EG9c4e9O/zR43KwWhiBTXXWW+CMddMvy7s0WqKYW7dyMQOMwQE0uzfmSU2dh6f7TW4vG+5yMS9Ma4r/B7ftTFu3MauY3nb8l6ttuLG'
        b'8HsGZqSRZ3UUtxXjwgtvCse1gPurZY9Nl42Y64rP1drUOpN60rvSJfzQIXUxN4w0mIhOtx6vLi90MESNKA4rDglG1g6vFXtFkOyiSjGzkphGdYacUUZ/hnQkc6NEc6Pe'
        b'9ox6zFA2NUO1IElYKEpYOG5h3WHYZtiZL7LwwHVhOWQx4jDsgF3poKGoV09kNUdiFTQUJrGKGc1HjcHbEjcGyw7lNuVxK+uOkLYQetwZmx0m4oVJeCk3Pd6c+8pcCW/x'
        b'2PzFYqslKIgFCWIt4bqIuC6oZaCutbBv4Sh1g32dPZoiCU0VhaaKA9LEnukTM5QT0bA0k2HKJQNRawitAUOPSlojRsNGuDxU21RRZ/Ho8uhlS1wCRC4BYodAMTcIvWoe'
        b'bqqmZi2hTaGyB9165nbNlTiEihxCb7qRpEUvEkUvalUd4y6eYKmikjJiWNp0GHdqv23Cl5iE91oM2vXZDbmNeA97i93Cx03MJCbuqAolJtmonDnDnNHAGyHXQ27OlEQu'
        b'FUUuFYdkib2y0VN4SmqJb4p/zECl30vhzietu3Frh44lneUSqyRUtrbDtqOWeGC+4XzdWTwvSWJVNJaWLknLEKVljGUulmQuE2Uuk2SuEGWuEKcVkdKbYLFdzR6o4nyF'
        b'NYXJhsGkjoy2DIm1p8jaU8ydPc61pGdedzTOo1EMlTn+QSlWGVZB44TEalmnALuzkTgHipwD0SmaPAquF9wUYD9KkvgsUXzWWHbeWE7eWHy+OGzZPRxkuSxIsMg5GJ2i'
        b'XqX0itJYQpIkIUOUkCFJyBUl5I7lFYzlF4wlFIojlpMXxXau6lnTtaZXMLi+b71kTrhoTvhN1s2ZY3NixM6xuM2EtYWhWvHu8qZHVLGV/7id00k0UxaOpaZLUpeKUpdK'
        b'UgveSi0Quxei35spg5F9kUO5o+6jQUOFtzwiRKkFIvdCNJDNtUQDGalAVDRRTVHSonnqHd4iB2+xlY+sKE1JUZrTKwhPtG6QmOTTbR6VSO71XNRIvF/xlkTniqJzxWF5'
        b'4nn5uHJRxUpMYlG1KvYp9q4aLOsrGwoaiR+OF6NcucTivhvRFDHOdXrM4FhY9roOzu6bjZMR0xYzbsfrYXexxx35PdFd0eMuroPsPnZvWr8aShDfCTVXvrfEMVTkGDqa'
        b'K3aMljguIl0zTZSAhrdMccIiNMTy7FFv5tmTkbdEbOeLuom1Deol1o4SqzCUJvU+9aFlYpewCV2OhyVOwewHegwb2470tvTOdLG154ShOhr/1lCRlK3RY0YkZWj8SAsN'
        b'WA8DmQzzWQ/y2QwtI4kmV6TJbdVCK5CItohxHd1D4fXhaJ2F8i3WccTnkfWRTcXNpWIdJ+lZY25rpsjMVazjJruQ37pBZOYu1vHAF6Lqo/BCiN3EbkxpyWzKlJg6iUyd'
        b'yErJpEWtSU1iwBMZ8DotO13HDPi9OoOGfYYig3mPGaqGZqOeVyrIgXRmus21QGtHXhuvM6QnpitG4ugrcvQdyh5aNeYYKLIMGs0RWUZKLNNuFkgss8YWZqEytbbBLUBa'
        b'9J3JaNyUqVWFijxDJfwFN3XeNHnFRBK5QBS5QGy3cNzOQWKX1MseVOtTo4cUdIom7bTraTdD4SI05FvbTCgp4QakgopSSV1Xb4KjbT3zEUNbS/uhHUPLtDH5bU2LcX2j'
        b'Q+vq1+3fMKY566fvgtkMl2XUT98tZTI8llNCDbQGf4dvGhig4vTQGP3RcKEVolSexf15vjyAVY6WTlv/C1zZ6McN/ZgoSlH8P1UyHpe7UNTM7xh/EQ10imZoLcHaUpj3'
        b'yFMkIKsvcOpT4uLieGz0I2jHwC2NZ4EcBRRFcEjJwRGhsaHJBN1IY4uI4e4bk/hFkmhMXhRglQ6erqD6PyVREaeOzwcsFrKkPxgMJ6xB2flpB+Mhm6muiXqhZRI1buo5'
        b'boFWDQ4PVRSssBMqcs133GLW09dCyTXzyWv56Bp/3IJPP2c/+dzT16LQNRvyjnnomvPkNc+nrmXQYdE1J3QtgMIXTfjjem7jevyHhZSngcauiAclFEND7xETsxBZ6OgB'
        b'PvrODAMP08cc4kXzM24bm3clD2tfFz5kURox1L2wqPHA0Mcsb3VsMI5/JxTw9QdsfPxwHcXQMbmtaTuuE/JQgakTRu0K+U6ZxNaV1xfWufh6ziueosQUUeoC0cJFY1GL'
        b'x0KX3DYy7XIfnjWcc93q+tqxuQnjpu4oqIYn6qdhFMpXZPxjVjhT3eh7Bv6dUCK38OHjJHYQS93qMQP/PiC/NI8R+yUEw+BoBTbMKqPRFCoygwsm3A+PMXwWKsJqUAt7'
        b'p2mzcaR/J/IxlVH7T1AZ2ckq0mNVuWMOOlZLVifHGuh4hvS6ptyxlNDopDJJX9R9Ln2R/Uz6op6UgGg+SV/UfyZ90cCIkWyYbPRvpC8az1Ukb+ZOshfVPRSSTf4JddFU'
        b'Sl00m0ZdtLgzg3CRCwV5OWUhedmFZYV/R+PUOn3Vpy7/Rd6iF83pcuMx77CD45NC77CC3IIEJbj3rsQ/AtafBx960SAft79ES5QG8vrrRETZ6wg3yBUTEQXrMT+ARdiF'
        b'gg1YE101KTQ2PiWUkBCtnqIQJoeEJOWtmk7vchFswhn+M4+6TuICZQn52eB5sU4yBKenmacyLQ5cD4JAthyIUFY4gmA8zgfhW897h6ugGuf6fx8fmP80PpDJeFr5VYHG'
        b'B84HzbBfSPsygJfAWeLPAF4BW2ndu2sCGw7GksND+YSufoQFewsjvs1VEPLQbZ/OXIwV1ASaL558WKmyxfCspYHBTENDg7eaersTsu69xmCc+IW9zPI9HkV2hguXr5Sa'
        b'sGSDBvrz9Sqw548QQjLN3jF4qldNhw/iTWwMH8z1ktfkHzfmyqDfmtx/BUkYha7NVJJDEmZ5/QtIQsFe1v9h5OA2HjNrFft5yMFcUuKYGYdNzv8Kb1DWf57iDcr62x+u'
        b'eD2XNzi9i8p4g8/r2XKAwGf2Svr+P+D/PQ2zoO3Ws0qwCTpmVEiJDZOPYc8sf2AETis3KRcQj+Y0+w+N6PY8pz8L7JO96R8h+wrz/0vr+8/R+mQt0v7PM/WmN+LnMPWe'
        b'2aD/f0rUU4hLKfdDJy7RoGeK2iaPbIP7YG0MbaYMasGhiClzTjACd3JgOzyxofDlixtYwmQ8fFvo9390+G+arzNYFmoWJn33Aw7ztrlv42+bu816m++2dxpMLbtHNV8z'
        b'APWQnf66zosvV1IerWWqc1jBHrYxHo2vNGiBqLyYZfdiWIyWvMqPVTpei+MpkG92SnAww8EJTZNN/ElsGtwPLpPPkfFrdWXYtDJtbBA6CU1bMYc84AzrfKSagPCMifOU'
        b'rqCdVBnLExwDJ6LhnkBYKQODNTrQn23rEyuk4DN4Ap6bZkfaDoZ5qv+CFImnpmfywv44AcvDwsLoCfjRyrkMLb260tYykaZn77KhstG0m6njswNHZ9/0wqiwVIrsmdax'
        b'G9SlTqmfIm4ZzPrP0baSUFszUJKnbRV7/Uu0LUEr66nl3Z+lbG3jUXGC4/+AsfWHUpcBtoJQwuUAW5bPmXT+ANVS/McmajlKcgnkTFumKExfpqBcqUiXKUwpMUsdE7M8'
        b'ONJlitK0ZYoyWqYoyS1TlKctSJQClcky5Q9Xp5GRv2b/U1qWvNz1fxKVNZ0uLF1bSPlTxWj2wGCi/9Kz/kvP+i8961+iZzlOrkCK0Mgn7xP7L8G05LrQvxOm9W9GSs2M'
        b'k2KDl4FGjJQSwP0yrvCcMBorjH0pz3KHXTTMIjkCVsXz02j6L9gFj0ZEwVrigzodg3eVicUj2AdqVMClwnnElNANnM3lwF7Q9UzsMGi0JlsDM2E/7BGGwJopcrEDuxwP'
        b'5WArqNclOobP5/66g3ocDuyHLSrwSjJsLufjkMOwcckUAQfuinCkzW/hrli0ECS63fCqyhJb5UBX63Insh4C/X7Rk+vDPGJLgZaImA3kCPfE0pr6SRwlWGsEt5LVJbhg'
        b'og9rpPGlJqTz09IxkygqNgZ0pUSAsxGxTvzIWBSDMxOc57ittgU1SckMM3BEowie0aUNHGsV0oQ2+pNeHuFOuKPcGd+47Jf9VNyYsLM+dqWbAIN1COeKzVgKapTAAf+5'
        b'JAzoEsLqZNmjdEVFpNABpDFRixUYGflKoJ0PjtHWkvC8GkeggUvwqi9Li/IFV6SuJIONw1DFDK4RshhgbzITjlAOoFNqBnwnAnsZvzebGbDUkbPch1HYcOghJdRGCxDv'
        b'mRePJl8tAS6aft51v1cmaAZtbwsynX86bkHAqPeL+ioqrieZVdvVFv1sdaW0J+4jD9/B0w+yv/rmF+9X74bNGS2gPm/bHzm2YkHpyihqTHTVSuma0ZPv+50r/L+dODwz'
        b'avYV1bHXfWucntzUokyYJ+7lHvc7uv1L3d5TyXNPnDzGP/Flz92uD1JXZihEaQrSrFUf1lyWCDj1N468++Bv+gzvLSUrRrtnn3zFz+23TTf8PzFZvV6s4c+91dh/bFH2'
        b'pvRjK1/7qvnYzbdc3Z2/L0vek9B2rL3Z+pJ/TdM3zjd8hbt//+LHUVfjCcuodSN3lfe27hsQnHbYGnX8zdOwe3PjHPtx+PHQiffbl+jmVFr8vP21a5uua7MPzSj72eOj'
        b'dTE8mu6r7wi65HE0qJURhe5LebR+3/4V8Ko8jGYN2ErzaMAecJ52Jdik7xANKnNkjGPQm0GkgFJw3n0KFwOO6EmJMfASoHUPLSi4jaz1wTaL6cgY0IweIeqqO6Ow905Z'
        b'51BZwOCUMGGzIewjGpMW86yxOfiFSb5wGWgk4TTT4OAUCwdUe0hxOJfXEqRKMGyA7dMNq7rAdqlxFTasss8g0ohGEuiis4C7exV6CegBlzXgZVYMuAQOkz2/5bZYNZOo'
        b'PlvDdrYfBbphT6FUv1kYFu0KrrhF4RGkhwEHtdbSOoz14AA4Jd0qBEfgcXqvME0KAQL1ITMdQsALUbF0xSDxT9uWBZuRoCXFtVwBJzgOTvyUsinpbAc88cga3XNREMrj'
        b'YsAxODKFjKGBMQeseBr/pi90+GPjdEyLHKLF/OmV/rP4LOtpJvPDEO9/gc+CSSHmhzbXb5bo24n07YjkFSw2ChnTCbmnbUZgKbQq0Gie2D2a3A4SGwWP6QQ/UGMYW2LS'
        b'Sp0SZpXgO75iI78xHb9xbaND3oe8W+dgfcFeq0HHPkeJW5DILUg8K4hoYcqe0zeT6NuK9G0l+jyRPo/cShxLyZCkLBWhf7ZLxUZZYzpZJLp6b5G2vVQ8bC3rqGir6A0V'
        b'2859z8x+zCH0ptKbaq+oiRxSxGapYwap46ZWLRktGZ0pPQu6FgxZi/n+5LGwm/r4Q7jIIVVsljZmkHbP2FJi7CgydpQYz+nVkxgHDs2uU75nPKvFt3VVnfLH+iaNSzpz'
        b'RfrBo+E308ZSM8cWZ4+HxI8lLhjLyJlgUQZ5mFGilSfvFlHjz/A+/vnHb9ImpqM95LgeBWiqD8USKsbX/44E1PB5FBVJsB6R/zMB9X+H44GEuHW+f+B4PEtm+xchHty4'
        b'8kB0vAmNGdueifF4muGRCQ//AeMBW9aUY4tS2AyPwzaHCFCtLIN5gF5GdrAvi8OwhGdYcJuDM1mArcImAVKWRwW8RlgeLlLGwjAP7JVyOriwDnM6wHnQTmbgvxezFDdQ'
        b'+GhpURNfgUEm87jFm9wxhQPuXy4DcVDmhMOxThst4wiHg6EAzjkHu9CLv0t+oEm4CtUt3AMOwxHs6bZ7Nb0wqUxY7MCzj01Tk1I4mKCZTtS2MtgUPcngiINHmGrgkD8J'
        b'xPMswRgOrDq+HPaiZQPcWUETES6WgLZkTOGAp8A2GYkDVpmSYEI0I5zDn63DPWhmxia4hdBIVgWsmWRiHIBVtpNMDB9/UgiFBXuKxikvzMRwYlF+NNTCQs/SwIOFtSiW'
        b'MsfXbqAvOnpErP2QwcVMjOWVOSH0RZcItdXzGC6YiREzvkKBvqjvrGe3njkfEyo2OAZuZpRzGdiu5wC8hJEYcjgMTjoNxIAvgC00+2NQwZ2DkRdpYJCmXmwAe0ic7HVK'
        b'Ec4s4lFCrW6TKYNHEX6E00bYJzP/qlrEobieNGYTdoADizkYUrEYXKI5Fa6wk/6MthtezuHgz7jwzEqwkwGawEFXmqHYWGwzyakYLCCcCnAKNJHqBwfBUCohVTD0wI7E'
        b'RF+6Vo6Bq6CFY2ePIRXwDJvmVMD6MlLRWra2sH+KUrGYj52C7QkuPOgwhxK+gip55xd6V+f/UpMRqnPsvfeacx+X7Dt1u8j83besBy5cLIpub/vmb/Z+a/jnMpYJygu1'
        b'qjZWzv9W72BStd0uBS0FhbPcbK3AwMCQFJ0iLS1eewRPNZv3KP7BkpXnm9a7D3/W/G7kpeJNkd+9PveDnz7d+IZPo/eNw+/MW3HLyHDgu9uin7LDN76sgTkVVXf25h32'
        b'/Mblu7+bvbRNu2L7mRk9RfcPqLi5N0UkrjjSp6Idb/ZgyHXvrCsu72YmL7PUzynpf+ubOc4Jb46/zLkkGnTXW1uevMH8xTfDfcBE2a3MOs4EJ4O1V7/rUMirAYlJTR9/'
        b'3rvjp/yzf8v/dVj7uzUWdg+qb3ubLDxyuMEVnrnQfWpc3dlsfp9wq09PYO1X3EtUq8I1rZC/vejXXNhtV/B1RsHlI1tVqpc7vFTYo+P6duie1XV/b5xTcrv9l9qBs7mv'
        b'ra+08Tc4/Frh38SGA9SO+qVDO69/9G7XgZA1QWX6Sx3DMo0+O3l20OSl93UUdq+ncl74YNkPnrtf331n5JfOjvzyHqPrv258xHKx+UW0MmcPb7ylsPo7w+qqmQZtO1tv'
        b'7Wy7FR5w5IadXp+xz7HW+WvUlrmfDX/Hzk+l4YsTvw4d1tb5KGDh7lsaulnHFmJSxN9K1lgVH/Atbr9vuCKvMt4+IydB7yFnxW82H/cM/Wy07o3D6q9tTLd9r+Jxx+5P'
        b'LF86fX/B5tu34cGj9s3GOUVfhG9qXKiw6dv7pmWfStw/fTXi1bjP57z9+t2VH5r5zfDy+Y0ZkqHj+fnm+uzcnR9OFGS+/pGrwVdrVUsH450Dv3dmpbyZ+0P3zZ6Ab607'
        b'b5z/Nvts56Vc9oXmB5l/W+gV2Td/ou1Fp/FTP/cWndXrZW3U+rbrnXuLxi2b4sSrr3zzot2w5+cLNiv++M6FH9KLT0Q+8ty18CvP3Te+0hE/ukrd/uCk3etOx8tLTdrr'
        b'7/7+94iEuuHCkrhPt2f1LVrGDt1060zc7thXxZ3WE0uK1kS97P/TB0Ghvb3b+ClxmRphahVfZWhuND7+LePCzQ88vzrk921gy2NelECcKLj0ue3LyWnD4oY73l49mV/v'
        b'Pv3uVzMYwvrNEYm/1V+09tr80iVeeNgvBivXPtHetUn1o6NKD/1Y45/piNf9+lLxqs0qLu9umHBYqi+ZXVsErt0cOfUD96Pfdiz8u6Oe+8yjax1HC89+vf1Jtd6GJUsS'
        b'5o1snyc6uuIsd8+qk48PfnX/9dG+y4/vf/T9mm+/f3O90jdXv+UaLzaNKI6qzXkw/x2jG5o594xuHPs2zXPPC4X4qLTX6Mao/9LaHP/Hs9G1r795x+sD1h6/5SZbN9UY'
        b'faa3/gul6sKcwfjXf4hP6PjVTCmx8lpL8sWQQZFzAudmmsssr+tOzA/26f10pfqJw+4nxiGbd35uPnDnpXXH+9kfvDhnzPhEauI6Z+qX2ta0q2opB3YtMgwZYvq8Ghn/'
        b'tVPNk99ivq+59uvd37XPZzd+8PbtvP7fniR9ll73WXqgv6/hJ0a7Pnw4Ymc/cWeEd/ps3ebKN+/Mq9g455rmMu1vLz9+8qPueOz8Xznff/CKJPhRCbfbebB489EB39F1'
        b't96P9bz8IKXb2Ovn1LfusrM3rNO48lWp5UXxp5vOHz12abnjJ54fK7504WbhsULdIbONj1tFyY83zR52j3zf7Nf495Ykvdp5RiR8/6jBxz/Gjul/fzX17pajzQ+Gfljx'
        b'+f3fL5lvvx3UzVtJ1vOwBWwLmZRVkPzfLAeCwLIKGi2riKXXYn94WIbXXAm3yhgQF3KItLUsBFymERAoSN80Ry9X4DbadLseXoS7aA4E3Dtn6RQFohYO0NbK10D9hkl0'
        b'g7ElgTcQckNiEm2KehDJbrUOctwGWAWuMvmwfhH9iqNwAB6T0htiwQnlKXpDaO4jOzLNJMBeIY1u4EU5rYrEht4ydkOptzfYpgj642CjlLoJd8Ir0VPsBnhci2kP9ijT'
        b'dpL9mqDOQQ7RAPaBK0xrKojmYV7kBEU72mFCw4JYKaMBbs8kAhqPD8/KIAzRZfCKFNIAO2g7aENw1n7ydoCxHKMhCdYRqXCBAayGNU5RsXqwXwpp8AdHyXsLwnh0WH4k'
        b'3E/RjAZwcS0tbu+AWwNkkAZCaADb3aSQBgMhneUj8DLYHz3FaMiA3UwWbAimI+hkwxrYvwhWRT8FaQBbIW0C6gi2Bgqzlzs9RWkwBu10FdeawBYa0wB7Yc3cKUqDthb5'
        b'NliYDM5ynKIJZAFUudOcBdDnQkReA9DgIIyjCK7hmgFKjjE8SSesNdNvCrKAX64BaqSUBQH90dEP7pxDZOJ5YEBGf0CZOUVbETbDo7qcOL4aD2UanAiFWyh4LhrWEMty'
        b'cA2eBH0yO2vUT1ph+6SlNTwaQoR5u2xYGR0nB3AAZ2JlDAdYbS81LqwA22iIgx0YBmdkFAcdcxKFuvtqThQ/Bi2OQVcZtvrl0RwHMzYb9AVnkSgyFeBWGtcQaRk8CWuA'
        b'V8FJungbUCPsJsAGWLWyeArYEAFeIC1nCeyxwHar4FTxpPVukw25ZQY7MRYCswkoVAMM1HG3glpSPFk5Mei87in8ryGXLrv6dE9Yg7ssPKcqwzU0gsN0j92qohgNe0HT'
        b'U1xb2LaUxk80YLNlDjzrYDed18BcRRIVLqzAuYnlg4YEKa1BHe5+RMPlLoFejhOPoBpWJdCwBtAwky6I7bAzSwpr2IOGiV2TtAZDAZ3qs7OiOJOkBngU7MS0hrYQaSsF'
        b'raCNI89qmA1qKHixFGwnoR3hCByhebwLwCEproEDR+ioL4GRYCFmNQTCrZO4hhYv0sFUNUFzNFrBdsfI8xqsYC1tun0anAWnhfC8W8xTwIZE2EUagOV82E8MrGPABTAs'
        b'M7EGA7CPmAhr220i4wUDDgXrMcC5zcZkVMi1B6fRAl4ALyiVSmENsBVcIMmdrxhLb3aDIQcZrAFVy3ESX6HmbNlqvVkVrdZT2FLIBtiqJ93Y04KnJkkNVj707R5wCLYL'
        b'4RmvOHkbchVwjmyQwZMljClWA5phdkl5DVJYA+hZTQybV4OdOUK4ZxqpAXXaKprWgIYiUqI2qHDbUEyTqIbF6ylYPQ+MkP1DB7NNUlIDPJ27mHKGPUb06H0eHLMXTnEa'
        b'kCS7l1qcA0+QUJH8ACmrYfZMwmpw9KTdta2ClUhAgFV2QaUyUgPoB1fo7t0IL7lhWEPUGntwElbJaA0jG0j3nqMATxGTcUxS2hULL8YUZVMMA9jLdkCzWjWJPwo08KWy'
        b'iQFol8om21G7wqPfQrjDUWq0PGs+1mroRTfItNe+RJdTHCOLF7dYVbCPCc6gaqohKhGJSUkoWtL7FPU2wtNMy0ywl26snf45DmbudvJ8CFAP28iwGjhriZDMkpwke5VJ'
        b'PISpNxs9cWUDXY5nYcMGjhwZQrEcdaSFcD/dnqvQ+Iuxkin0sDwFh4An7WlyTqdaiQwOEQRfSKP4LDRU4WEXde9dAhkdAnSqSwERUjqEgB4f4NYQ1Pz4UbHwQpKMDnHa'
        b'h+7ElWH5UpbDKtBlNMVygJXG9NjT46s6+aHFdN4ky6EN1BNAVoSvOd6bfibIAQ6VKILj8aV0+Z81gC10QZFi2ubDYGjCLawyeBE00aiNq6ALdONGGs1TgdW8SDK3L4Iv'
        b'sNBs/wI73NyRTnId3O1JP4Wl052wnkJLgyPMQHgxjX5TDTgHdknZDc5+AZPsBiT30gwbeN7WEsNXIiY/+ZA9bVfUWfBAsAh2BZP9ZHDCEpUX2U/eBQ6S8lgPagRC9OJ4'
        b'Thzc68BjwZ1MhmYFawM8QNHt+zh6eZMDaoFohRY7E5OnYBNzfQgaegiOYQgMgbNCPA9U4fUkzqG7KsXQ0mVtBIe9H+EPTgrrC58NtMhaGvkUzqIETe3EQSe8sFwGgkC9'
        b'B/bPknEglOBROl1D8EiWEC3W6iPluTBZsIduIt1sK4y4gUfnTyKKTpbQq50uNApdIfybGNBdLOPfONgSXEU2Kpl2BzQXXARtk9yN6bgKfXCRJNIDHnaXJRLFtgn1MCly'
        b'Iwe20y3gKGiA7VJcRQSokyNWYFxFKdxJJ7YJvgCvcdBjpq4yXkWZCqm6VXYMjgztAPf507AK/SUkWBzcDhrRXBgVry9DVaiDE/Tq5SpotKZRFWAQ9ktxFVJWBQX3kPHO'
        b'G/aBAQ5a/FBG4HASmj2LlUjRGuUbSmkVePAoB61SWkWxC0kSRoVdhf2OTk7xlIxVAU8n04yFg/BUIk2rQHPPdh5lFgTP0Q2lcxncJoyZxqqwNpPSKvR96HIYghc9OTJW'
        b'BdgGR5japg6k0pTxGhTTKuL49i6gXoarUIsid91gI7wqdLbHrAo075+W8iosvOnRrg+tRHbA/klaBceUggei59MltS8OHJHSKtA6uFZKrJDyKipX0P2rHm53F4Kdmk7T'
        b'gBWwahM9aJ0Hu9HcJ0VWzIDHQPcUsyIKbKEb7C7jEJlPS9gIKqXQig5YReZc2F1RSlMr4sCeCsqHrUxCBQYWYDJFdCQfXAPXZGQKNNx38PT+wywKXEP/AERBbLru6D39'
        b'fUYOQWGlSn+WSfH5nyIojCUG3n+gTdQpPFBkcC3+jfgIB5GBg9iA/+fxEc+69OfIETrNGv8+coT0JVLD1NbEjpS2lE6bE5kot/gayn8nRWwjyfeg7hliEy+pAXprWEd8'
        b'W7zYxOOvcRumQAAaTRoY29C2WWLrL7L1H1UV20aLDWJwiv4LYfgvhAElVQMnFTd5PbGBHW4X6k3qcvmXogXkDHhTejK7MiV8XxHfV2znh6+qdKlgi+rwrvDesO54VD48'
        b'+wkFBWubCdakkS6LY2g0kUh5YEyDB8E0FP1zTEPnP8Q0lLSV/BVMw4QCC1Wb8v+YZhDVFNUqwJ93JbaBItvAUcGNiusVkvAFovAFjVFjJgulPRpHpt6mjssuoi0CJSWj'
        b'K0PCDxDxA1CCRPxQsVUYvhfdFt3LHOT0cSQuwSKXYIlLlMglSuKSLHJJHktZLHZZIrZaKntOSWzlNaGkgIsU90lNhqn5n6EhmJq3ZDRltCxpWiIxndMbfEHpMUMBZTlx'
        b'ZMHwAmlJ3XPgY/P8Hv8ef9TUbPkdpb0KEuvkIdeROcNzRt1ueF/3vuF/3V/snSyxLh5Lny9JzxSlZ44tWiJZVCBaVCBZVCRaVCROL/5xPCDwhuJ1xdFVN8qul92MFYcv'
        b'FAdkoJLHaVbwwxyM/3IT/stN+B9wExZQ8zA2YZ6MmrCGwtSETaz/a9SE/2/DEspZNCwhiYYlYH/sYxqma7lOXzJM11o7/VtRCe+in11KcqiEWJ9/GZVAySgJc1GkX+Dt'
        b'A0JJYGFKgge6xNP5T4ANhHif6FlMAzrXc9jSH2x4LVz4DKSB4zOQBo7PQBo8fS2fvsYfNw2dxBdETIuP/7xrmFTggkkFiRSPkArSaFIBS91CSipAR9+pErZAp9/1Wc/h'
        b'FFgTToG1HKcAHz+Mm+QUeGFOwby/jinAr0mi7oVGjnv7P2b5q+dR3zHwL35NEnoNPn4cxCxiYkIB/n1AfmlCARb9V86EzQRQAKsco2KdVkXGwmpHimEHRnxAlUIxOBE7'
        b'TUlHQ/p34jxmE+g+i0wgUJi078eW+trEhl9FatuvMe2qzrQz1akzF5YHK5k9l5lsSwxSsDkKNk9RS1VP1UjVTJ2ZquOhlqzwlKW/YiZ6a7KiESNZKVl5LlOgTM5V0Lkq'
        b'OVch5xx0rkbOVcm5OjrXIOcccj4DnWuSczVyroXOZ5JzdXKujc51yLkGOddF53rkfAY510fnBuRck5wbonMjcq5Fzo3RuQk5n0nOTdG5GTnXJufm6JxLznXIuQU6tyTn'
        b'uqkKHlTyLMIv0CPHVuRYP5WBSomFykgxVTmVg8poBnZ0T8rImjxhkGwjMFzGUsnn2d1RCw6MTQmRKmYVzlFmMLJs0Bihis0B5G/RoINJZfiyUuwcWkg/4+nmSP91J66X'
        b'8ZGHqkzZS+jEDZSzVZGabhCzUqlBCLpblicg3p9LV+cJ0JlQVd77syM3LyungCvIWynIE+aVyAWTM4DBFlGqz9O6d1JVjSvFRg6R+SiFRD9tTZ4gjysszy4uJGr/hSVy'
        b'1rXEzgDdzkL/LysQ5OWpFueVFZTmEqNIlIbSotV5RMGtHG8SFFVgG4Vp7qq5oYXEPMAukCe12yqqUMX2A1JTFbrQnKVlJispR65dEI8rfSyLK8zDJhpleU8XKC5ju2Ae'
        b'NsfNkjNVkRqRlAoKlxWWZBVhu1MpTxNlD9vIokwIhVnLiNVvHu1yG92hc8bNzVuZV4IyWEonkNig2EnvBeFaLy4VlqnmlBYXY3sz0gZ4TqpxPOYd1triojuKOVnFZZ4e'
        b'OaynxgaiwLcJ/fip0QZmBxikXSqh/sskBmZ0H56B2qxmKuWhIdVMZKXIGYuVsM0YqXLMhFT2NB1EViCbaCb+4eo087Ll1DOs4Kc1cDkDeKlxDMoZbRczPzZGahhCfJqT'
        b'cFPajKjkiTES6g60xZJdHl39z+sbctbhpNjmYSPjnCzUm5aiVy6lDVbowJOB5JuJ1BN8Vm5uIW1eJI2XK99EcANaVZ4n7R7CctS2J7skbcU7zYiKdviOW3xWeVlpcVZZ'
        b'YQ5pRMV5gmVy7t2l9r8C1AtWlpbk4hKh+810d+3TJgklxtOanGZxQrJdXjfeL3rswDtdxrud/QpvoIZ36/wLQkbhRuV25Sx6TsK2IuvhqTWgH9bDQfxNtowHr8DjsIoH'
        b'BkANDx4E5wEdBrSDZniFuCROKScI4oNJwaBbgcHIdd7E2ASG4Qmi7LfNmMlgLz3Pxi7SzKxXMMizLrABdIN+Jja4ifVmeGcKi378/fffv4hTYChrzlBkBCwt8lzgyyBq'
        b'eQnwojJx/gYvGMAGdxcmQ2EulQCbgnjMcvzJcLGKkxBWa8CqNVh3Ax534wti4pxU7O0ohhtsUHTYBE7RuoItArCLgy8zwb6kWGoO3A62ojjIFnw9PAt6k2GtXEx8VfxD'
        b'MSznKVgGm5CkwF1gL7zMccoGQ+QWC16iQFcm3ImiccTRNMEjOvJRCCLtV8XxYJ9DZLQTViNJS9CDjcomoApsobUU9y4HzexQ2C97QNmTWZIB9vFYtPu5ZlTcldijNr8M'
        b'9MB6dxdPJkNtI3PFwjJyv5ilRm6CEdhC7ioy1DYxi0A9aC0n+vzbwACTfuIFVDT4CYqhtplZ7A63l+PvGAL1HNpXd0RKBH4sMcIlfUrVl2KEzFDStzEvp71VuC2id+YT'
        b'+XCAfChIAs3aYA8LtMChxHJstQwvgX2W8rrCMh/nsGqRdUx0NJ+5yhccNYFXQbUuPA/PR+uA6miOKjwPaqKSkhl5+Zpz/OFW0mzuRrEZyj4JLNwUijfaMsoXootOhaD9'
        b'GdFjmyTnqFQ77IJmdzK2BopOhb3S1lvFI0rK8V6qkQozrVVRpbcrKMDhUGvQxWOErtGBR2EX3IoKnGjzbi3E3wBmoApqWClALQUOUTbm2UQNNW4t6Odgp8LdgtWo6tmU'
        b'PRwATSSYkw9AodTAEXBkFQl1hrIyh1eIVqsgdoFwpSOsJ5/KWWrU0rBMEmYluAbPClfBvYvgeTUcppKyAmdmo5ZEdIS2gjYbIRxYB46TGMEVSg9e0yUJKYA7Y9HbNsDh'
        b'yZfBbbnl5PPBedATQip8Y7BcdTNAY/lsEusaSt4/eyw/Kj6VVDx5WFqeoBL2Y//mg3OKOKBzUznpZaB3AbgQD6v+EJzBmLWeDRuWgr10CgbARV/Y6ZUsrRs0HqlQqMIv'
        b'GxQ6NhyghIFozpL8YPlO+rsl4gDNRZ99OrT6rUuRdzw+sWiI1kqNDm3e8lbNWsa2uqiXvll4WjlIhxk6Nl+3s7JOcwP7ifaH23v+fnSBrffqS18tN357p82MgRvuwjde'
        b'O/b+9yUHNs9c3DTrynXbhYYzfz33vfP/Q9x3wEV1bP/f3aUjTVB6r8uyu8DSq/ReBAQBKQqI2GEBe+9iAStYQRRYCyxiAUTBmfjEFOWK5i7GqFHTkxdNjKbnPzN3sST5'
        b'vfd77/d+v3/iZ7l37pQzc870c76nuCNe43DL+InL351mem9Gyc8pF/+W7HhF/E5FXGiIqHZyvt06B5u+5SvrOE3+3tpnvRu0T4UZdX1XFhL1rHytnnDAZmp1fmuUzo4T'
        b'd3JMPIy+lh0Sdxz9xJKRm+/8qrjfWCWac//Cu0WOmflvr88snBh6MHtdkMLxscbixQv5g9HMkoObn915z9KaEQXNu9FScUp2zkZ6YBYz/v3ilMqNU2+abV/cFFcdLyrb'
        b'cd0rM1BkkJ/duLr3bdszvP0+XkvFbT4P1lnqafHWeW0t6mRMloy4VQ+D397Vb9N71GFWlPV0+cxtE64w79mVvLCBRqfPf35TtojZ0TcSWVugEvXJ8I8PY6ee8vWuT9o6'
        b'5/tbd+fqfH/LqPS9oZQC65yUt+bMmm1u9sEe07/LZvpcuVS0Xse7YNcL54f3biv+bl70YEuAwaOm8pADU99d3/qjX+DJbf2F37uoRaVfWZv8YEvj9eleadd//3zrvcxT'
        b'X6fIjeH1W4vchO+mnNwTFX/bpM0swGLbU9eTdkW7Tlh1+yafW/HWknBu89iijWf3Mb7Cn2Jhts0M/8Efroy1tfZ8Wj/7d6e3tmbo2J9dueitxc5n5SemN6d4+SSh+mkP'
        b'bvvyvs2Fnft+HdEY2Xts3KL+VPtCh99AbPeqhAtmWxizD8wjRLerPE16xj1IX62V99P7bpnfXJt5ZHPkulmavw/V3s4w/+lClv2yKxYzgg5cuRZrUG9Z+XvG97Dhitqj'
        b'T29G6Gx4Mb1vV8PxGy1dpifGXJpl0TTb59aF63V9j86u1fLOqZNE599IDRwubT/4/drfZ9z5se1p7Z3LXzUe/PT4/R5at9024s7lL/ZcMfz7J3evdo0cbvtWbBb53ovA'
        b'E9a/L9/+fGfHD8ud8r9sHm684bx7uFH85HNf7wtBG54t9VN/3jxr6XTv5gOBp+2gzolPpda7ftXd9fVTzy1bnekI8ZPoDllgaEZ6xP3DOicSFSetYvpyrzk+z9SrWJr5'
        b'q81PF2aOM79b3dF//mt4f+R39c8+fD/9SAY/jFzNmo6dKBAlcfF8NhW0cRIqwW6iHOMD+2aDGjRhoHERTVlb0IgJN3MpbdCHBgu4CqxkzefOuCwWxCWqU9zs2WAjJ3gy'
        b'rCM3tyUTvF5Tozw0HXvAMgDnyCWpaiL2yyVm7cfUwImphVw70KvE2xfpg1o0NGwSp2DbMHN4cTnXFZyEK58RA841sCYZJcUKeIkisCmF6BGCjeJYN1cCRqJOFYyFW9C6'
        b'4hQaeo6xqnuX9OBeohUK2uBa0WvewVBu5wmxk2EPOIfvU+FWoRql5g035XPtfWJYBbP1YB9oSEjB6o6qbthJhDY4w4V9trCfqFRMKQBH3vRNlgnWY71UV7hG6aAJtFgo'
        b'QUGUmq9oJNvDWgp2JZBKm5SDC/CopvJaWXmlDE7qk6vqUiuLVxfK2anYAcIscJIQ7gtkoFuAKLMCp9CSRKWUA9cngg7WFY08Fm7FyhCgLvd1BwmUGTygUp4BtrK2eKus'
        b'WIUusAXUsj54ECtOEjUq0Ae7VNS8UXvHJyUI8dVwsjILB7hbNRC0wm6iejATnIWdUrg1DrMF9vkl6CYL4ZkELmUVrYIWeF3gBGGEP9iF3bvGwe2acC1YrYyjE8WFPXBb'
        b'FrndDk52RaUlC92S0KJl82sF2niowGNGNuQGflIqXCkVxVfBVfzXLshBgwH5agovYt8jongg009yi0viULozeH6wjlXbAzUB3mT9sRYeQ2sZ1ouFjjdPHaxTZy/wOwym'
        b'Eg2SLQmwRp1S84BnNbljwhezKgf74bbF0kS4GWzBqhy8WZylpktJMmtz0Ay7KuEJnVfeiuABuFapCihG8tglhgfmveaAJ82c1WDaEA0OEQUl4stIFWxCS+V9HNgLO8Ee'
        b'VtN3XxDcqy0C58oSiMOO4xxwWAR3sizqAKs9/+SWCC35YlhNNyd4icgQ6DY2USqcGSKJxhpnFXA/66slFMpe6amBo5OxS6F98AhJF1AViFWUVloRFTce3M8B21RNWck5'
        b'FI11dcWJErhdgOnq4oBWMevaJCYF1LOajeAC2EJcc4HjYBvbofaDPUhsa0b1XFTBiUTYy+UIwRFWYasfHIeblUqBs2Zi/00tpkSAYBNYMx3z9pW971gDIAftPFgj9WBb'
        b'sy5ICHfBS8TmV+lAB+zjokbdABqI0hVsRr2i/6VGOmyx/INC+mTIKlHAVrhNH62p0VC3TekW6ywHtMM9paQkswAgQ1/RF9gGdpMlohqlW8yLQiVtI4PVErAS+99ZUA3P'
        b'6JS/Wm9ivCEx3BabJEQJ0sVgS5SGLuoP/ay22/EgeBweiJUKtNDqn8+h1JdxvcAlpYo8B+2HDoMWsEcqqGBFX72E6wn3epHOE4YEpwlVPA5rEaUIsAa2KgWPeYyDx1UM'
        b'xoEzbOvXwR2oi7eUaeP82TzAcW7wItT6uIO4gItgNcnEAJxA+YjhJnVKN5k3AdakEyXB0HlgkzQea6RzxhjA8xx9uM+D5dsWDSjHKj6gBxwnLmm8QA0p06Aq9TUlHxVK'
        b'HzVBE9byMbAmKV3iYSvWujaHR5W+7bqhnJ1duk3APqUnJafZRhx7Ax/CxHRwclKVFiITERKHuioZJsRovONR9rBF1ReeULrdKwNH4W5pMl+ph5/AQYW3aVjyJoJWUMeS'
        b'vS/fHitBg1NgG+u5zgL0sQK+rihJykfjYgtpJh5Yx1msioZNsoc7Ggr2C+KFCbB9ntA1GY0yeqW8qWBnOCFvfobZG7Rh+/NNphFY/ZGfr4o6QBcaowUoYmUMlP1JQkBf'
        b'FBGSFB+08A4E7WrJUK7UrvaOcBAAmQSueeVgUA8eZzX3DsHmLG08p46Ks4HzMtjLA6eC0DCNaa4GsmR4zFZApiI0z2nAC1w0ER/lkGnKNAI0vulJhwLbRKxqUj1cxzf/'
        b'v1UB+q9vIIinvD8rBv0FQNa414+K3kTHalVl9YNmhnMoI6v6okZvxpBPG/IVZhaHnRqchmyDu6UDEcNmsXURD0aDgrqnDdgPm0XXRoyMN623r6/cObeWp7C2q1XZNUZh'
        b'aXM4qyHrcF5DXptk2FIs59CWnoylH23p1204bBncPY22DEMRtbATiJyGHFZPB0UkYYbGjKGQxv+8FT4BWEeA8YmjfeIG+cM+Gbc8M2ojbxmJHtgEKmz8FTYRT9VVTMfW'
        b'qj7RouycW82bzFss6+JqIxR2TnUJtRF3ja3qpYyxy7Cxi8LaHisfMNZetLWXPJ2x9qet/RV8t/rIA/F3rRwbi4atxPW8u7YubYbDtt71aiMmlk/1KDvxs7GUueOQY8Cw'
        b'WeCQUaDC1OKwWYNZrZpS4Yix96LtvWpVbunbKBwFbWFN2a1TmqYwjj60ow8OtVM4uLZ5NMUxDgG0QwDjEEo7hDIOOQM+g7aX/ZmISXTEJCYih47IwZFtR2yEbdM75srm'
        b'MqIwrGhkE06QyCzt2Tt9D9rSg7HMkWd2h3Vmdy8dnE6HZtDekxjvHNo7h21O+8awhuzD+Q357A0mYymhLSVsy6OU3dEDHj1x/ck9yUxQEh2UxASl0UFpTNAkOmgSE5RD'
        b'B7G5WNg1ejTEHU5uSGYsxLSFmLEIoC0CGIsQ2iKEsYigLSIYi/kD1YNTLy+6uvzyciYmh47JYWJK6JgSJmYWHTOLiZlPx8xHeWm+QZE7cfXxiiJc2ANb5zZOk2mrVZMV'
        b'YyuhbSWMrR9tiz/pKqys0R/tDyzta6MU5jaHAxoCDgc3BNdG4ktZzQZNrPLEmAS2OXTwZfwON5kb4xpIuwYOqFzVuqw1bBxPLO0nD1tlD5lkK2ydWs2OmtWrjphb1Vcd'
        b'Xt6wfNhcJDe4be551040JJ4xbFc2ZFH2VJWyc3uiRo0z3ZuwI6FJ0ljVurhpcXMobeS5NwFJg5XDE33K1hkzZcROLFeTl3dqKq9i3WNo9xjGPZF2TxwsHrZLR3H0CDvl'
        b'abKZjCiUFoUyomhaFM2IEmhRwmDGsE0azueBuW2jbYP/4eADwUhqjc32VtdVjyIRuNLGroyxmDYWD0nibhvHjQgl8gisF3Q+sTNxwP6q82XnQafL4mFhWr3KLRNXhbkV'
        b'bh/GXEibC+Xjh819FRY2jIXopoVIbkdbeN22EOFOsOLwihFRYHdEf3RPdH9CTwKrXsQE5Q+lprM3+UxqNp2azaTm06n5Q4XFw6IS1ElS2A5hwX8ylnIV4T7o9Njcvimy'
        b'bbycKzPrsJJZDTv4vW/u/w9qIQ+9bRw+IkK973xWZxa+6x6QXPW97Dvoczl0WJSOKyH4LyohvmkhlnvSFt63LcS4EssOLxtx8++273fqccLKEExAPB0QzwRMGSy6Mf3a'
        b'9Btl18puzL02dyh/2rBbEaI+SUl9AKJeIMbUOysssXhp3TM0VYLwMsYC2ljQFs8Y+9LGvnetnIdckoatkodMkkeMbRud2hzYWihsnVstmyybrRvURiyd29TkRvIS+RjG'
        b'Mpi2DFbYuTSa1Kt9YO1YzxuxckWDHx5U0Kh4eGHDQsbak7b2lAcw1iG0dciHdoJBoxum75oOZWQxGVOGM6YMueUN2+UPWeQrvP3qVYiyoqQ1pClk2MTzW03KxumJHmVk'
        b'9hrEgwF7LX8f3zI/UPnvX9D/kxkFzxiv0B7+NI9UOKDJIk4DRQxFbz+vpF6khHM4HGsM+mCNL/Ot/4XLfCk+lmxUc6fk2oG8fwuhcMY/Qyh8c9obhSc8hQp+DZ7QY/Su'
        b'kFzCudmUlIpsXPHNhsjdWzIKpvpntMJ/i+JSTLGC+19SXOGEGliO6bvDHaXPHNOnvPyyKSt+g5J/G9hRxrmjUVDE3mL+I1q6MC3nX7aVLYFZI1hk021IcgzG9z+mCDcL'
        b'n3NHp+DlfWBB2T8k6xwmy/llEzmF2VTNLSuvKvkLbL//KW0zWNrGFIzeR/0T0nowaR4vSXPFLSatRE1GbrZeXmr9p8gjKJ1u/0Si+t6UeFH6PAwdPHf6PIKfaDN12ryq'
        b'yjeQh/8zLK1oof4xXf1v0mWe8SYi73+EdxXt/4QIgImQvyTC7BUR4XER/yEauv4JDVfeaIiKs9S/Ob6Qwlw4/7iwQVwYnzNaYZeMv8BbHsUA/U91Hy0C01iAQRT/EWnv'
        b'4LkFzwsrqfqMwwX7Cl4TDILEyA4+/2OqprNUabBUVc77RzRdf3MINFWibf6HKHk59E2bOhtf3xfMm18y9x+RQ7859PlhcnAa9i579usKJX+EVf3PjDaIWt2X1BbNnict'
        b'+Ufk3sLk3qLeIBcn+h+R+3/poWLtHz1UvGyrl/oAvOQyH9lTSorPyuRZU1hPE66H9d9aqZlh4jdM8bW5uvGP+RxyBBQE18INoCZFCxx781zOI+sv/EvEIUbfMfrD7n12'
        b'yVzl5h3Hwb4lZkdzKBOLvUvqlgzp2/2L3iRwERWJiFUM7ny4FbA3iVnRnH/DncT/Ny7N+OdcUknOKHMLt1QhzqjEwzLMptrr88wGG3Qp9d2cU2ea2Db7MxM2cP7iCGXa'
        b'vHmzlVzQUnKhgnDhX2x+nHlFiir24PVa85f/z5sfKzBhgftuKTWqwIQYoKJUYNKYxFFiZLMqTNQkvZfqS9yM19Cw5/Ks3mj411WZEBO4YTzCmj+F/teswYrGkjdYY51c'
        b'xd4OwNOgQ1quvMA/6Ybv8OHORKLL4hCqQmlQnxWoTSic/amtHUWu7sfFwZNS3QpNHH0V2ACPcESgLYwoPHzsiOMXSjUmFI4xWDyTqnKnsNUvaJ9I7gdYHEgMv7olAT0k'
        b'E9D+/vC01DRhJpfKn6AOmsBWG/aqXpYC9yXE43t6sO3VBZAq5eo9rkgVnFgETrLKDqfdwHHpfFYxAZ4fO4ZTCPaAI6zmiSxpxksDaNTjc/nEABochUeIJkwW2AgwRgZ7'
        b'16IC98cIOeDUEtjHqto0A3kghktTpVT0wFmMl+abymJsHQcreYJ4ofvCBKFrMj6L1ivllcATogyiPWANt4Dd5JhTGKdCacKtYJ06F2yDXWMJMhq4aK3BWi6rqCCqOeDw'
        b'Qm1WMWflpFJ8lccXqlGaoBlu8+ei4aoLXiStLgUNCwgmCg9RegB0YlCUKTYkR3W+PqwRJpND0yUr1PK446oCqwj6TVMCOJQAt8VhXwmJsIa0OItlKUgMClaFW+F57Tfk'
        b'V3tUfqux/Gq9Ib9vSu8rXPf/rOT+aejX/pPkCpOJcL4wVKX0y1HbIGHzinGhiDzoesI6aTLYpYKvSpUAIBuAjMVg262BZCXOEG515Y+aSs+YxWp8bIyAJ/CB+kuGgk2w'
        b'n1ciCmZlYXMylEkT4WrQO3rz5lDOYuqtA6fAGim2yp4aw9XgWIKdjkRlRsDlscAM08Febj5HrAs3sEoxx5dhTsxJJvdtLBwFH3awfbEmgQNrEkAvbCd3UwRrxAy2s3pQ'
        b'zYthawLsAKv/gDWiAWVEg60KD3RZcF829m5hKxZTtjagga9K6mcEulckIMHf8Ye0xvNZolYlFCA5AWfBLoL8QvA+ovRJ0tmlsHYUaUSJMlIUxZtmAg6QRp2UB1pZCBMO'
        b'BXpLCYRJVQCrbbURdmgIUHEi1ItEfGF8EoeC54vtwDpV/8lwDckd9oMd8xMwRsYbgCFwp5T9fAIeh63aqM5rWPNzDqWmwTWWgItklIDbY1UFL43s/2C9bgybpwdmExUx'
        b'1GNbwCECdZBILlfxyAM2kx7jlKUK1yTN0gEdBDPaXmcJvv//owH/a3knq+WBVeqwFkNqsGNQq4GedD7shqdf6kfBZlhLxiAnU3D6tTEI1IpZFAZLuJZ0USQ9W+ClPw50'
        b'KrCFjHV4pLOGR4lweIGNFniwKgHb2fEKD1bTYS8hYTE8lpMghOvgdjJAEJyIo6CLjCt5YCNEdRfC46CbfMWoCKAdsp2iPB7lBk5OVo4fePQIAPvIJwNQuxwNOeCSMUmG'
        b'R5xZcBWLi3gAnFeFO/KQJHMojh/GmmwpJZTMhl3BAmyFf0SIOpnKVDRsImneQSjxgEewLsS2WKEbake4w0cD7OEuBY1Cgiw+U99UMAouNAoeAM7DgwRAAF6A/ay2oQzs'
        b'nSMA9QVvQHpkLa5ypojiVk/InwY8GZrj2EEPD3ngopTPJZXwgWfGgxp4ulqFmujJgW2IkbmpLEf70f8nYD9HCjvV8MCBYTr3e7A9vhNeTIE71TAWVD1YTbkZgR4y+YVN'
        b'16Z+kQopSr9wtt/yPBZ6sm86lxpyxIuVQrdvDaLZwIylqpTf8nFk5FJ3GsMGvjdxDLXSwxsjV7p1LyhhA/NMNagzDvb4gNBt+dhJby42eKMjIwF1RwMpXusZUrF6FDXP'
        b'IJjjooxWzMWDbDpVTe1WtaGSDPCQaoPGUV8e0XNGm1eybuLe4Yrc73CqpXh5ZcNuKe5oBpWWzC1ZOL8i5E7QH6+zKksqCgpEQWTbLg0RkXei2Psq7GXqEk00g+GW/Rzt'
        b'MociC29OLhhKz7iaPejwVjZ6/pGsz1Ybm3KqJlAYqmndTAKCsB3uFIriCNJH/MRUuAGeFWbG/sV8Brq4WhyMZ3Z8TOEEcJyMPmMiXNGAzhfCza8UKsIiKYtJKuAkrC0s'
        b'e/Le91zpIdSGvMnzbk+elWIYZnTxwtd7Lq0Mt96V9lnOY9vNNvy2trf07damekgC15sUOXy70cDZyWH585QnFxJ/ibrXcF0kkAgjaL1vV319L/jTu9Jv+s59OJi0Rs9Y'
        b'/4coRfI3v6g80L+1kXfn/vHeCuf6I9d/4gw0qU/I+/tNlZSvnJ/21yzQVHvr9kjQNYt9kdx3TwyiPea0nQE+kRbLVf0UR+/ZLR+fuONmp8OcjSXfK7Sd376gMvnp2d5F'
        b'Ee+ulTx+aPXd6jjPo6F1efDvFieX5l6+ox2wusdr3I9m3o8FI4s23r7g9sXXktwrIvNtXw9Y/HK4ed29Yctv0i7OLLw996veO+Vff7hya4inh3WV5eV0t6iWk7dPh8/R'
        b'/IE6vdRy4tqDlrcSu555n+0+Mn6f/XCA613DhwofXSNzG4layt8ST8zseNp0UbsWzkoti//9iN5nyzI/NREk1y0KdHhv58/Rv/ECL90zfxzy1d4PKqDusy/kf4NWw5db'
        b'rZ6XxW6RJNyc+kn0rMffvPuw967/bxnnDr+3TjHb59SVkoivqr9c6PBF5MPDVXZ0jHP0MbGNQC36Hf3cLz937Hgu5W0unewUEHwl4N16iyiNk64ms6rDOscINwdk3S6z'
        b'ShQuPr1vx/FPNtmu2FNyrbfpyL0Pvy+O0hW+M2571u6PFt2PH3csoy4++/TU1rVbPK4sLHuvzfVv0+/Pvbr7g/JjZ26fT0vi3951U/Clq5NR0dV9E7O25M3621EzJpj3'
        b'6OzB+JPTC07xdt4xn5WS/rYhffjbuzsmeDnYxXDXfJIb8dWAyPdG19IzY/ffTIj4u6Blp+T+l7O7g8IudC9tvfrk2VVfQYhC8mXjtfMHdz5vvp69bdu9Be+F3JL8PPR1'
        b'l/rW6beYJ2VeRyaEmDzTkWzQ6/oo5JPSbqdlZ51+9a/aukL7TrXuisLK+qVnhlsXHKqafHVvzuOdHGbMlx+vK+ReSNX45vNnAZc+t/apLXD//uAnop9nFG9eEHStZUHJ'
        b'86IVdN6jL5Y0VeY2SsaumLlqXsFDGPRp+w9ezKZ3N345bkHXtx/cPn3yS+kLi6Vv/Va8abujueYNw1MCu28WmXzTffHbZy7vi/f/9GLar6c/n5fw8FOVQ59ERj/Vcdgy'
        b'mW8U1j4+oCAif2Ju+ke/fFig8cXjmvaYb0ZufDT/XrtTwIvle+9zfnAxdyxVe2/5Da2ufR9nX64Z/HSPYqwgukdd/jDtVml5VvGxPTV5k2u7ZHfWFvZ97FZUcO6A94a9'
        b'pvJvs59VX3n7/kfgu6mBH/52e+R28kflD9+6duAXtTu9X4Nf0/n+RHtgCTiii9HqN4BOMWhTIbNRH2gAR4j2QXoSPK2NO7qEH6fpgrYWaAltAFp54IA+PMBqTOxfBPZp'
        b'u2LUMaxzZQeOaZhzM7XgJqJVkuqjAxurR5HFKNCeAGVKRQvYgoGNKiu1XtOsOgT3k2ROIkoQl855pfw2Hpxl1VzOgn6wB3aJ3dHc+0rnCs0Xu4nSkx1ssUfDFzik+toq'
        b'EPYuYPW1Thema2MQpfJEMV+N0oFbikU8J2EgqxapGwW2UX9WuWL1rYphHVHUKIQNSay+lbSQQ9St0DKKVTZMivaVgvN+r5DBOPmwF55mFcw64bFUbQLoAne4cjM4Iemg'
        b'g1VG2Q+6C1CNTo0C6GGVqnY7oqk0HdZZaDuBtX9AuINrjElSH7A5WCoaV61UYiJgcWvhGZK0lFMmBauj/wgGB9Y4kZZYlgUOCMBK2IE1+9woSg2c5ErAESnJd8rE6UoA'
        b'Sg4VC7axCJRnA0cB7jZO00aN/zrEHQeehbvBaZLYFraDDdpW6S8R8jjwMGhLI0QJCvFyCW6GZ8BuPHGgpY8/B3Q6K2HQTCLB1lFYPrSI2QmOY2A+eAa2EZrdo0CvFG6O'
        b'i4PnE7iUJ9igXs51BTUr2GZsmeSjxD/jUMmgD+OfjVXqXk13h+3SuQVwi7Cc1ebSyuKC3hVgIym1AhV3QbsS7V5l84lCkirYx4Ed8KAZq2DXrwVXsZpKcC9cwzXi2IPW'
        b'ZSRfbbgPHtGOR4vxI0kCNbTt6eWAOiTV9azGWl8U7JZiWxNRgkgLrfPg8QzKBJxV8YWyMiJxYENV6hJEGgto9BIlzQhs5aHKd8HVrCZgI1rJXkTbh1FEszfhzMBW1HqY'
        b'mmiB9ksAMA41E7YR/K9A2Mnqn7UvnwW75oKjLwGMOIhlbSgtUcA7rV/8Ejh0FDYU7Lfnwj7YqMnqellNgl1BDn9CY7sIO0iPjQGbQI92VYGNjibqlLacMNCRxJZ81guc'
        b'koK9Y+A2F6IYqhrFQdvj9RksTKMh6NR2obwxoiULWoXkp+kZ6+mmb8oUuF4J24m1x1YBVnlxNqhx0M5Wf4lLx7VDMnWWlc/VcJf9S7QrHtqfwJUY7goNAj1sT9zGWa4t'
        b'0gdrMEAUC3g11oAoSo3N1Qc1YBWLePUm2hUS4V6S2hdsBicINhVsgd1cPsfKBAkZ0crdOhHu+QM2FY8Halhwqjg06mHKQ9BKa6u2GGwYBajiGmqj6pIN2RlwIBpbByE5'
        b'RFWGu73VE7i24CBcxUI/7QFr4DHY5YaqekEkegmatWscC3vV4pksMIl+DeCWK9SfziqQrbEvRhuRPaDeLRkN4HA7+q6N+jRsFyrhc8FOtAlshTW681GMLXy4MVYFxWjn'
        b'wmb9WMJcuBf0leKtKkWlRXJBEyd12ViStzaaKNYK0D6gJQUTVkM0tbXhJS48nzuJdTayqQj0abvCbTzKFO7hJnG8jFcQgfKF8iS2vV5q64I1k3jqsHkG0XrUmy/F7hzB'
        b'UaWm+hta6r1gC9/2/7/O2n9HCcGW+jPk1Z/029g9gdarlf4d/n97U0AObXPQTuMHvAV4FhnLody8G9UVjm5Ygas5v5GrsHdu82wOUAgljdEKN8+mqAfKp8YohasHq2vU'
        b'qP7A3rFxZmuIPOt8/vl8hcCzO7ozlBZEMIJoWhDNCBJoQQIjSKUFqYxg6VBG7lDJLHrKLDpjNpMxj86Yx2RU0hmVTMYCOmMBk7GUzljaGKlwFrRVdiySLRp29lP4BctV'
        b'FW4Sxi2Idgvqzhwo6cmn3RIZtyzaLYtxy6Xdchm3Qtqt8AVFCXO5Q8WzmOJKurhyqGrJE4pawYnkPqWoavZPCSeK+wL/SWXfUtm3TPYtk33LZd9yuY3cRu8mTYXQq3t6'
        b'ZwEtjGKEsbQwlhEm0cIkRphGC9MY4fKhzLyh0jl0/hw6cy6TWU5nljOZ1XRmNZO5iM5cxGQupzOXo4x8mrRQRrKCUVScCFoYMZpf0WDMtRQmMZ9OzGcSi+jEImV8Vw+Z'
        b'mHENo13DEFPcfVnQizDaPQx992/SUbi6oXA3SUfKyRTUZC5uGJqoQ0+exjiH0M4hjPOEYecJChdxh65MV155flHnovddwp6qUsKgp2qUh5/CTdS2SJak4Lt3WMosGX4g'
        b'zQ9EJHbkyfIYYSgtDFUIRB1+Mj9lDoxLIO0SyLiEdVf8OeSJKs/b6TuK5+b8Qo1yETZVNS94oc5z832iRkl8n4yhPP2fmut62LF0P7GifEO6SwfV6JBk2ieF8UmnfdIZ'
        b'n0zaJ5PxyaV9chEXfMO4QwXTh0rnDpUvoEsX0AULmYIldMES9KmQE4YZhP+g/EJpG4nCJ7hzHuMTS/vEMj4pJMsM2ieD8cmifbIYnym0z5TRmEHYfUzJ5RQ6KIMJmkwH'
        b'TWaCcumgXCaokA7CAhQchQVoaLZ0qHoJPXsJXbyUKV5BF694wcqOUoQauUP2frSN/wPUdtYya4YfQvNDGH44zQ9n+BMHSq/OujyrUe2ePb9tesesjlkjEv9uoqE1UD04'
        b'/fLyYUnmUHYeLclrDG9c2JT4wFmEEbcaVRS+gSz2DuObSPsmMr7FQ6lpQ+lFdGoxLlBC23gh/rC8YYSRtDASCeEgd9DnmtaogHl0FGARC6OFYa+CCBYTBrBSBok8O2bK'
        b'ZnbMk81jRIkDYwdiLpujL75N2jjyS+4jMR/wHJh+OUCZahShK4gWBKEgryYNHD1blt2RL8tXxhFLOhbLFneskK1AAX5NYx54B2ENt/MFnQWMdxztHcd4Fw9msSBoBXRS'
        b'AZNUTCehyjWG0DaeWBCtZFaNagp3T1ZQ0GDDEs92lhhaGMMIE2lhYqPWPXuhwsGpcVFTEuPgRzv4dZsx/nG0f9ywf8Ith0SF2JtFQYq+JY5ujHkzpnG/RY8F459A+ycM'
        b'+ye975D8lEe5x2CntyKvjiknp6Ch7Y344zBa1svc33dIRPFFAR+5e8undZt2zhl2j1RSy9LP8INpfjCqhW8w7nLnl3cuZ3zzBscOJU6h4/JeMtLeccjJh7H3HbL37X5N'
        b'BXEoNe9WUN4TfUrsMeQRRovCGVEsLYodNBwWJTXGfOQqbCs94dZtMOwaMNqxK265BCCKBCL2y23XACRQbeVNixlnf9rZnwWLG1Af5FzWYiak0RPSmAkZ9IQMVN1wThxn'
        b'0OCy2WDW0KTMazlDLiFt6nKOTEse0x3WGT+CclxwIqjbY1gQpJAEnA/sDOwKbotEj4wkipZEMZJ49E8RHCbnyn06tT5ydm3zbV4qL0cjdk/6gDHO+ELBUOrE4eCJaOzq'
        b'5nRqMe7htHs44x5Ju0cOGg9NTLtmxsTl0nG5TFweahqFh1+3QadZd8WwR9hA1uDEyzlMVBYdlcVEZdNR2SOhkXRkIT25YDiycDi0sI07JAi86RL0wEWEW2HINxe39yv0'
        b'KmVzP+Nx+AWYtQLPDpFMhIZLV48OgUyAXxjXYNo1mHHNGjC+an7ZnAlLo8PSmLAsOiyLxGNcA2jXAMY1lHYNbVS/Z+/aXqrwnzDgPOQXjzruMtrB+yMX3yG/WNolZTAc'
        b'/TSqPnD3bVQ9qqNwEhzT/raAhybTHwk6zppYhyJzzqAg3R39uWsZHYL+KD1U3dGsXFhcUjm1bLb0jnpB5cJpU6Ul/xMdRqWvqteXCOz16g5V9LMT/fDwsV8ACvppJfUi'
        b'IpbD4dhgtUWbf+GO9Tt8DHpAzY06qe3LU1o4jwUHikcx/MGlDFV4kcuLA+uJW5+FkqIEpVkea4MDtoEeAYcyA80qoCbbib0YWwV77Vg33G5xQrA5RZmZNVpCrw9Ugbvg'
        b'cXCRz2UvZc6CXTNHS4MNHqQ0tC8lZ9bRUBb2ZnFwH1j9srhCURW2s5iiu1SALYZOucQmieKSJs7HFhcTYzXR6pxFX+ZQheM0HOAhsIZc9cBjaNO7G1spg3bQLHzNCDpT'
        b'k3iiCtbTT4BbhWinnkHy8vCeGKukMGDWIgc1CmwPJrcZ2mg3WPO6t3S2aJf4pASwGu4bvVSdAvZp6M2fxHq5OopWrnv+qnEq4AHcNlagifWu2ZcTIH2ZHZvVJKWHSlwv'
        b'vDGfPttmhQY4AtpY96NlZ8UeqtLFPLRubjG8mPXO3OEJRpaB1Q8drv9MO+l4mUS6Nh4LLwvjaGkfjVztcnOLepTRKu66eJeFVx/xJky7vOPvP6hdWml5eM1bq8UPtlkb'
        b'tkpkTkYG/NMS6Y2ejkdfXsv/Le7HoJnN9o/bixyWu7YdNhu4HWE0Na/3sMUva5e9l3elpbvfMD/44Ew//t+LEqbY58zbMuTAWfDTl99+dn3soEqM2crK511Lr2aUjqhc'
        b'sBR2r2jiXM+EH77vAy6sGbt6X5qlsYOHk/3c4zuL1dvn3g57cKztk6i5cWknfwicuuHuty2ff5d7kJr4W6vp0SLToxF6tw1HKv8WPU2wc/0N8ZW4wP2f6yxdkd0/rfSX'
        b'zbcdFZOiQgKPj5v/CbDYt+KG8TtnLac7Fc2SdS7SDIVvub1t0m9auf7xuzY/LTX5NVtzwZLPP/ty6jNPnwazqjSNXwPHvqVa/p6kbZVYZMnELXb727PJz5o9nqyf4Xzq'
        b'TFxSe9zC9jZN6ZMdMz69sXtsjlEYf/OA5Gr9ruS2wXHX7uwpPnVqfGjxFN2LcfUXHT4oDfio6hfOubhDTxc81553GPRbLPu63716t2nKxKnXdi7TOtd+OTCzaVJOc1Vv'
        b'ODOjpn3Yc84CydGbkR1u4rMTgi883Ffak7SB/9vfbv442c16gc5Q5tGC9kdeQerBBu/tTl/Dv1u43H6te9PNtz5bRrW8O+Oz3Jwf9jiA4Gv7Hu5Prc/Z47qjtKHJ9BDt'
        b'/HuZa0PsTan2/d3ugusmf7uj2X7FUTGutNjru7tdumb933zxgbwi5YPbfV8tLS2rXiwC3d7qPYK8rQqvpK6jvbs1PJ7/8N2uL+dGfmLaeHi2Fgic3X/jYmt9VNZ+hvvs'
        b'0rlj6gf63n/+mefZhZ9szTaq6dRPEYxP8ak+dOJG8ozGW6uOZr644n16bNMRv5/uXI5ZsThE/9T2wwVtH308I/nslxI9w70HfduCv45c8qgj/Tp3y441588Mv33pQsDC'
        b'R/M8qiwyvm3qXmx4aef9murbIw3PLwa99+hhemf3pzY3N+/KDVszrzD7ye0sv3udvKEJieonOncu5oSObfDXTa4IKQpp+VRcOxJUUPQ335y9krFrSk4/OPBE1yRMCD9N'
        b'NTUPHS98kl4u/GmvSsM8u2dqT/JpAX1T0mZXdtPuS2r4Qe3BCVqemV+kjO+J+eLGho8mrT3d+NDH7GOF957vck6uf55bWXzuo4IPn2QV3k/RMbz8oW3voYWyY3q/U8Z9'
        b'18ujJvLdie0XbJtW+s+sA2fbRmno6i8mW/dIcQ5rb6hC8UCnGzFGHOfLWojWGaVgLzLkXJabi09mYT2sY0866r1B+5sWcLB/mSVvItwXrTy5WjZfEMceoc6DcnyKClfO'
        b'IocVWQuoN92MEivJhAnEThLuAAfZE6y9i8DWVydYK9yTeOwBFugE29nDlCa4G8oSiIvVpVCOvaye0GTPI46jIbZLaeHnDo4bceyT4UViRLcCbKge3fgTM8szrHMA0KQN'
        b'd6uAMyhEafm2Gxwr0nYFa4BMwDpoQZXUNuTCNX7wKAvEvxnWg73YBrscW/ptAC2qCzjwANwEGlgq6hAVG7AVIPbvdp5YAcZakPMUB1U9KdxcCHYQdzbYIlNrARecSANy'
        b'tvG2RAilfKV9YF0RNhGsAjXEdhEcEIMd2iLERm6CUxYnEB7xf4Yn5+xwN3JWJc0lp1V6c0gl0uBecBbzF9bqKRFHlOaktWALKaoK9ImIbx00q4ckYsWK1WCDkDUx74AH'
        b'wG58MhdY/cbZHBf2zVOeeMOVqiovzcjhzkz2ZG8H612pAMqCWOM/2Ls48Q1cctgyiaSXWsMjr46d1OFp2JfAtZ07nj0x31MIz486gAAbMvBZG2iGrUo0crhHX4qdWmP7'
        b'TB6UVwIZB2yPR43PemhRR22Pp0h87M0D/cngDAc0gG64nxWvRgE4ri1KqmCjVKLSDfwjjHgz4X7ladlMcDBHG9HFNppG0DQdbrEbl0i/fxDGIUmoRMuCN/0JLYarnmGw'
        b'Hdg1eeE/ARSYDBsxoECoNnsObAT3IHm1go1vHBMLQS978XAYngP7tEcPiZfAzew5cTBcSbpq6RLQrB1PzoH9kcTio2D0P+soBWwBW8xeeoNaAg+pFXBdjcEhFvi9Ga4e'
        b'h/EYwHYg/9NJl04aaQm/4jlYfYX0ZVCvmsKBK+HGYFZST4JjnkqfvSpeM4jtaIAGO0T0hqAVGsYwqPbkv+5ayx1cIGfLkWhhtP+1QzgCP98ODqJ+ZlKiYgdOw7XsZc1a'
        b'2JSBLV/Z9YoG3Gjkx50WDQ8RmABXsNJ/9OPoYg3V0xqszTdRgcdngHOsPJzUFCFBBXULkawinp/Fh8iJXFAbacsedPfGgNMon+RJDhiSaNPrumnuOWqGsMPmmSuKNwdc'
        b'WvTX4ytrWJsNNhLb2tYppAsUBcJd7JoLrgJdZN0FtqtTujk8D9BeSiow28qfhUF6o0xXuKkCblQFZ+xhE9sbL8CjPjirFNiWCTdhsSI58Xi2iPAd7Gn3CTPEwVHECdAM'
        b'etTyufY28Oz/6nGlxv/2ceUfkEHZzUgU969scck5JTmTbED7lB/xmeSThdEcysrucN7BvNooYr94zKxeVWHrgiHcm63q1bBNZGhDKGMups3Fcp9hc3+0s26IVFjavTIX'
        b'lWcOWwYq7B0aIh9jO8eYQccb4mtiJj6fRv/E+cN2BUMWBQ8kfizoOiOJoyVxjKRsMPNGDtoVT54xnFRWrzZkLaZN3EcEHnLH8/xO/nlRp2jA8Sr/Mn8wmg5PHxZkDGXl'
        b'0oLcerX6hbSJi4IvYg/UGP4Emj+B4WcORF+Nvxw/WD0cmYniVDfoKkQSDKLOiCK6KxlhKSJKeE3IxE+h46cMFU6n46ejaItpE9cRAT6CMO8x77fqsWL8E2l/bFwpSB8t'
        b'yc65VdgkZOw8aTtPxs6XtvNl7NK6vfuDe4KZwCQ6MIkJTKMD0+rVR/g+8gUDKsP8KIafPTh+KHUyHZetpEXg3uEv8391wMMIkgdUr2pe1ryqe1lXWdIDG8dW3SZdFq8a'
        b'MYEvYo87gmh+EMNPG1DDJqeDPsMT0pSZovgE39qdtnGvV71n7dCmKjc6b91pPewyQeHgih0NtC0YdvCtj1K4iusXNOghHpwP6QxhJLG0JJaRJNOSZEYykZZMZCSZtCRz'
        b'lAkPkBwg9iPmW5NDFGvfS9EPbJxwYa8IVLABbOlsEGPjR9v4/eFDAG0TwNiE0jah+MOYpjGtek16rF8HxiahWxUDjffr9ugyfgm0X8ITTVU/q/pofIZj4fVCdz7H1O05'
        b'hX+fFPMoR9fW5KZkxsGfdvCv1xxx4rc5dghlQsY1iHYNYlyTL/MG4qDusFNKvfYDc2vG3Bv9G3EWtEU1L2Gco+SzBsI65zXEPlWjXNza4ljwZMYtgnaLYNxiaLcYxi2R'
        b'HHtPG8J2qXl0ah6TOo1OnTbsXFQf+4m5/QORlzwLn+nlDJhetbpsxYRNosMmMWE5dFhOfXSjb0OKQiiRR8vyGWFu96L+5T3LmdBMOjSTCc2lQ3NRDJ+G5BF717YA2j5h'
        b'IBr91EeO8N3ask9YYfPwEQfUpO5PeFzHYIVf0KBAIfR4qopeHngHkr/1UU80KKHPwaQRS5tG0/35beXDlu6PHVxkZgobPkrmGsEZ8fCWl3SZK9x8UQr0/iAwjH34juI6'
        b'RnIaop6rUXaCjxwkQ16RTyiOYxbnWuTQxMx3EhQTEp7y8LsiZRL7gEpTo4SeB5PYHj1sFztkEYsdcDgcXtSwiLGW0NYSeTxjHXrTOhQFO7sxTr60ky/jNKHbuz5GYe10'
        b'eFnDMsbaA/0bsvZQiCWNqkfHKLwn3LLxfOA/od+6x5rxT6L9kwYX3Fh2bZkSa91vWqPqLRtvhb1ra3BTMGPvTdt7dxvh08Fh+wiFq6jDVeYqzzqf15nHeMfQ6J9rbGOE'
        b'QuTRMfv4bFoU2Z15SxTZxh0Re8o9Mdr6Xc+QodD0Yc+MIbeMJ1qUuycjnoD+4e+SEwu7bU8svesTPhSRO+wzZch9yhMe5R70QChmhCG0MKS7nBaGDWRcLbhcMCzMGHHz'
        b'ehA4oT+kJ4QJTKEDU94PnChLaIuUOyrEXrJlA7pDaZm3J2QqYuKuLrm8ZCg9i46ZLFc9r9up21057B75VJUKSuMgseOLntpS4ijOMydKHDgUOGlYlDnkkvnAyv6g9jMp'
        b'Yo3btzzKSvAjAchem2swxZjzgWkI+mWPsvRZHf/dqn9S9P93JxT9Px1lvT5/VFxFJX04aoOLD7MWYFsBc3yYZY5tcM3/FauBn3EVDO+oFhQUeXvd0SgokM4oKamUVsTg'
        b'6kTinw4U445aATEHq3DDIZrYYiEEP4Xhn1ZM2VMcNoLJO4NfxfiDJzZqGFeAkUeLKtmbtwIMM1o2t7RiGg99Uy9YOGf2vGkzK25gizWzijU46Vr8sw7/rMc/HJzxOzg7'
        b'YoC8Af9cx+WUkhyUJqx3xrxuOXpH+zVbzYpMHHsrTsfFeW0jK1ds0aH50iTtjrrSDuzOmNfNsO7ovGHmxFrKEHsNwgjsA5w/7v/uXhTvH/8Cb3xUOO6pKH8wCrJ0DSLz'
        b'B4w4PkZH/4kF5cgfGmP7UMeowbGJV28uK+mM6DHqqbqc3j3rmjedlkVPzh2aOIXOn0YXl9Ez5wwVzR3ymzcknE/rlL/gFnB0/F9Q+Pcp+cVQ4RWcJyT8aSRvFPQ7BoN+'
        b'x3E2RqIuZWY3oi9UGOGh0kyyMR6FGFuP6LsqjPAQaOy/MQaFWDiM6IsVRkEoxCJkYyIKMbcf0RcpjCagEPNwzsYEFKTMOxLnHc3mrQzCeRtJSIih+Yi+k8LIHYUYem6M'
        b'eBUHj7NGEWwyE5sRfYHCKAQFmUzgbMTzjantiL4bm5OpZGPcKyrFmEqP16lMxlSmcgiZlo4j+u5skCUKSvpeg6Nj/70aR8fihVouD0OT49/vyC8LA4sX67PR9muTFLZA'
        b'2R/W4RzKFLaplMAT+m9o1L6EnZ2NfkLUifUURsWmlOY7ml7qLy2pVP6DllSlf2Wu86YlVWlyVQqFtdMMYJ/E3cvTx8NbAs4DeWVlRXV5lRTtVeTwDNoWn4P1K9AuCW3m'
        b'9TTGaOlq6mijHRvGz9sBd6enwjq4N1OVgu2wR1sbtseywLFnMsBqWJOOGqsG1gjEcLsAbUNqeJQhPMiDvcGwjTichy1LcyTjKtGTB+UBWuH6Krw/nuQDjpLogvmgA27n'
        b'gdUVKF0HSgeaVpB0UUazJeAi3Iqq4kl5LgQHWeOAc6Cmmi1vKqJ3NCEuELsaJgi7qqAObpbEwlouVnRGmaizRgFb9PBZy3ZE6QHQhpJyKCNHlC5lMjGBmAVbDSUmpmoU'
        b'5UV5xcKdpLhglO1achReI4A9oaiOvLGouBpc3Gp4mBBqUAy2SEBvJZIIb8o7CBwnFYSbwEl4iq3iMtiHU3IpI0OUMA62kwJz4JYKybw0NF76UD6gw7yK4P61w6PwoLJB'
        b'e8FZZToOLnCfGgs2fMTEWAL3wGY0qvpSvmlQxhp61DnAfiWp88FJddCEGgb0oIQC1sYDdCdrSALgQSStfpTfNCeiW5+QD1exRKrbm8NVbElwF2xmjY7k4LA66AK1ABvV'
        b'+lP+QO5HrkvAfiQYq1gywbEQwne7UQZ2gTaS2gA13T7Qhe9SEBMDqAAfsI+0DbgEj8FtAsI94s/ShqvkoTZcTWgNg62xUr1ylCycCl8GNrIM3AkvTGFZsZ1nD7YIlJyw'
        b'rmKJ7VEHF6VoA1yH+B5BRSCqL7L3ImukoEdAxBOsAxt4oCmI5QRYPYFw0BY2wG1Sby/E+0gqEh4PJ5c0qIbrYRvborAGHAb9ArH6NGWbIvb2EW7koGg10nS4G7E/ioqK'
        b'QezHtEbB9RRpV1iz3B2lG6ts2Z0ziJkPPBkKmqRhsBNxP5qKRlw/z/ap/oVgJyrsnIDUEncqnAVP2bQTwRlCMFhlXCQF+4yQBMRQMcvgMZbgg7ABENlB7eoMjmKYYdCH'
        b'paCVhzG1jrBp2/XHSOH2yUgMYqnYWNjK9qsTRrCF5QjYkcCmDFKWugz2soJ3zlYEu4BsBnqOo+LUwR42aT+oYzsJSh9jgkVp2miX7IJbWNk7zs2FXYWViKHxVLyxiNCb'
        b'gkS9E9bEL1BKrVg8On6Q/rUjjJhbzIJtaNToAofgKcTXBCoBcaKVtb5q19AkJK+BpysiQYMyIVybw8rDJW+ixlkPViLGJlKJ4Ph0to8d0C5QkusB1mAZPD3aVeCJJSx/'
        b'zofBAyjtObS3p5KoJAlsYtkaYMcKkrsNSRekZOtWJ1JkKGzB3iSFoBvxNZlKhifBblIk3Dsj6qUkHUfjgjo4MsqY6irSuuhDP1gHu2b7Iq6mUCnzEkmJk+DhHKUgQZmP'
        b'QN1WyRSLeEJoBGiBe2FXNjiC+JlKpcaBBpIsY+xyUkV17GU6/GX/igTrWX70T16ozcNHiROpifDCctJPloADkaz0rIIdS7EMYBJ3o2SlY6r0cPWW52mr5yMeplFp08B5'
        b'wn2wKlspOKvgRdSxT+NGYQuDG8B+UjXNFNyzD0IMep5OpYOWpUTY55iBs9jT6FzCitFJZJT/sBvuZhtmG+xYoQ1bQQ1iYwaVMT+fSA+nGO7HEbePDs/blakJI8HZUtI+'
        b'aBBuhAe1l6QhPqL5GBFxXjkZgK3aJAFYUzEHNCr5uBtcIGVO5YGT2nAV6EV8zKQyESOJWZYHYlAvS6bjXFTj0TkLbshkxWaLxXhtcAa0IRZmUVmotNPkMtgMHINHiXzz'
        b'eBPhRcrIFyVKh/tJh9QE/fCQdsVMxMDJ1ORxsJ5IzCw0JtUoG6YYnke9l3Rl0rArprClbUxBHb4G9AGMWZFNZS+dwja3XhSogRegDHEqh8qZCo+SYNMJoShyKziMuJBL'
        b'5c5D8zNpoeMuxXAn2DsPVVVEieAlwE5rsH0ZmgXhKimqi5gSzzEgglM8NzcdHCvHgyYaNlfbshxaXZQNd06GHShnASXIA1uV4wWakNalq4D9qPEdKccpemy/3IHGi21w'
        b'pxc8garsTrmjBRahxLnCHBcIG7GRFOUGTsMedsRq00lLhy2TEYFOlFMgaORrEXlVn+agHCDrwH7SQEHsjL4AriXsAjJfT5ZbUD5J8GoGBqfC2V7ZNXE+O5tQoAV3Z7aJ'
        b'yehzcTFrtNu3Ao/7WE66Y7k2HDYDeHQ6mcic4Gawgy0hB2wgfWcaK0nLYDc71Z3UNR0V77qFqDuuHh1V4S4uu1DYYwb2slSAvUVI5vqUgwo4BlpYMtvBbuy/Got4UDQZ'
        b'I6cpMwmH7BS3Al5wVxYTgDoO6vfhSlnJ8GWboid5qrKjqEeAes3RTnYSHuNzSE31YL9mAtzkBjdJwPpYIZfSAB1csCoq7VOytKytmMDXIsZlg2O4BC9gwH1qotW4ctbi'
        b'bCBeh0KS7uLOnTrGYLEzGzjRTpNCQuM+IX7mbL+EDDZQXcOQwjdlD6Rzl4ZPdGID9ROwBThlM5S+dMwUbggbeEWsS6HKmdTGzxtzf7waGzg+Sw0vc/Up6/luGblubODS'
        b'ifpobUz5FepNH7O7opINzJVqU0jeNCZMXzrG3GUZGxiobkS5oILkZmVBvuPc2cBjdmzpK8csG+OWLGID6xax1aSCFsye4F9MEeNhnokxEk1KX79k0ZRyC2uKz82IJh8S'
        b'zVVJFvr+08ekR0nZ2PXJ6oRWd2FJ4jm/udSn+xrwf9dCSQH3q9mapOrMTtROj6Q+lZD/vgslHQ3ucAyANXaVqPfNo+ZlupKekBsGNwlgLcAdZyG10LyIteAlYrQKjTub'
        b'lTLgn/G6pOVOJeVpLhjP0h62zCIkVJWt5ccV40h7DJVXT7mycC4beGFpNiXHfFu0zIxbzkG1TE4u+yz6JxWpFyLHqNhmXcYHaeYx+gctHfTHGm+KWlBbbLPKr6582sY1'
        b'Y2OXfvRwQO106dXs/YWJ4WBn65RjFd+OC3La/qPh7xMP/frY9ed3T1ZH2dW1zbzx/N3KwyEfDt851RmqYiGcqx275UBArG2SxRUTjzXl08b7P1Rx2pRe7/TJRJvrA47X'
        b'j8S6NSWebIw/2ZR8AAZ1rnLqXGf+lqrboYB3u9bqdf+k/85b45ZG9m3avulwY1LfukkP5yyN/2XMgo2zJjsv33bhLbE87KsHCQ+zFA5zP5r10Lc7pm+7+lsbFCFV5yy/'
        b'KjResnDtvM7tvIU/6G7w6939YfUZw7uT9cMk9S+uPJiXF/3N7ns/9dmoBMeoBa/5pNcwW7wvbDhFb7HNe4O07c/358Wa7zQNWnLlF7Hxoj3mR069eF/WeNbmlsYvPhen'
        b'jQvQ6Z6W9feqsu1qNe/bzyhdp7GiLP1gZ+OTycfem3kxq25r6haT3HEBRc3F7362+aL/oS0ntoT6tzndnXTTXfbUJ6vlF792x771+v6Xnq75eF6dY8JvFmsPufuvVv3k'
        b'2lu/1b0tyLa+ucKzz+vA4viSRxf8ivpBwuIX337+eYSs5VnlDws+XXDo/YU/vZ8TdfxtneEtjR11dYb38h5tmp8+9+3Ko2snfljXPuWTtz/YdLxxw8pYzYNZi2xfrPjp'
        b'pyVNpYcOpWxp7bHNLQmRfSv7esnSXNXdWaoWH+iOn/tcsVP2yGjhCs3yKRulzxb9duWn5gbOd581HO3q+eFZfIr5udaOpN0zWyJ+S3L+/ITXnfKb9/23Vx9a1zHHOufi'
        b'B0Hff3j5i59HzrzTbvz7idDf33GvSTXefWI64+Dd33Xgymd/qzKI32v2eKjk458+DrMKyjr2w+8nEo6r3G7YdPy7yWrPq9YtKd1zIl4wTSiLv7lBOlN2R7e30+4d/Yr7'
        b'k27PSP76wIHK7gXVhb883fmxjH+1Q1e2tfz4niNfRGZHTZLPe9TwSH7q7ePTTN9+vPn2996322mvqq1O6cKqRSt+K1r89oF33K/4L5zyzduTaO8PD5a09I5dvmzjF4sP'
        b'fBm7+Nhnzy+kOV/4oee9b/YdSi9ZsTz2TKo0q189Tnjl0o7Gy5s3d17d91X8zqbf3TS/Sdq1IGtxzaZxTu/Pq6sqt4r67KeOab88DP55H73nmJivR64znaUz8C1kUmKK'
        b'qrkhpbqUg1bA7WqsNkRt2iJYw6IBg7pFKrEc0DVVCX88E2wAR7AZ23aBcGaC0JVDacP9PC5a2Z4lV7BBsAnIUcZd8LxUldKHtTwtjkcsOEIu7cQxoF4At4GT8WgDvwbI'
        b'VYqxCdwe0EOSZhTmEZT4jaA/zi1OhdKu5sL9YH86ezN6LgA0EmupJn2il8VaS/UorZI2wz5jlLMY0QMOpKhUceCmQrhGabGESxCI4FZVigu6OLCDkwn327A36xvQQred'
        b'mEoRM6mxAmIoBc5bE4rmgl0BGFIB7J8tdMV22mpctLA86EfyXVEKTyQQSwwOZQAPqBhjK5F1icQYY4xzOKusUQ0OgAucMLT3vMAqERwAZ+xIojhwiloYRan5cU3nQ6Ue'
        b'SF0o2ESA9tk7ZLjSlsXZB+1gO9/h/7+Nxb9x+oin17+2ynjTOENpmCEtmjq3oGzO1NKSis/QGotcb46osDg5lUkcalw4Z2PUE66+ia5C37w+/QkPP9kJ26Tsk1fogCF5'
        b'ekC+quIn8pU8ka/46YkaZWCBvquzz/YiFEP57D2BgyKRFw02kib7TCIpn9lI5EWLjaTNPpNIymc2EnkZw0bSYZ9xpKfKZzYSedFlI+mxzyQn5TMbibzos5EM2GcSSfnM'
        b'RiIvY9lIhuwziaR8ZiORFyM20jj2mURSPrORyMt4NpIx+0wiKZ/ZSOTFhER6aso+u0sGDBWWNm3SN/98a62PXUc+tVOiRWOX6oyhmDYUK8ab751ZN7PRcOe8Wp5i7Li9'
        b'gjpBfVGbI74fqhUMjfXeGKGwsMbeZzclbYxSjDPZm1uXuzNvY/RHBka1mfXFdXnDBvYbw++aiWvV8BmydX1149SGhW1qMk3a2kPuIS/qtuuczpgG14YpzCxqI0Ys7Rq9'
        b'D02p5yhMzFn37m1RMmd5mExA2/u8b+L7lEdZuT4W+NXrKWzs6lUV9s71GiO2Tk3SNknzQrlt09L3bb3qwxR2jk1O9RGfWIsUApHcQCaV+TVpPBCIGjUU1nb7V8j9hiUx'
        b'+EoXu5qeeFQPRTqi8cDGsXFas2bbxCbdY5pPjSk7b9ReDnyZQaNfvYbCxAb7rj6gp7AXtEW0pTUGo2Kt7ZokjQubg+WetL33sLVPvQr+GonKi5ZHyr2H7P3rNe5ZO49Y'
        b'ODxTo6ztGl32z5FJ5X4nlnVLaXE4bRVRz2NJ925e/L6tJyLb2a1pody+aTnjHNxtzzhHDhjWR+2PRXW2kzywtj28oGFBY9X+5agcE0slOTZ2repN6m2qzbqoMewc6tUV'
        b'jnyUX1J9pMJJKOc0zaqPUdjZ12P8bIWLa6Oqwsm1taypTK7dnT7sFNbIU9g7tRk0+4448BXOro0qChdB2zSZBo7HbwtrKm3k3XNybavqlHZ7dS0aFk8YyBh0HEqdeM35'
        b'ct5QZvZwVLbCVSy3lfEbIxQCCb5y71bpnjQg6dYbHDssSGRtn6TNSxQuQoWbhzxSltgYhR/CZfGNUc91KPT1v8r7dlT2U33KUXhXIBpUHSwarLimNSxOf1trwEOuir1u'
        b'd4ed072mRYtZdYVsWpCNmGvvgvF15Y7dGp1ixj6ctg9XCNzlhnK7toDOyu6YrmVDgkjGIXLIIfKpM2Xv/EydcvR8Fkq5+T/TpMxCnqpT5u5PFqOtm82P36pT7hkcKdpg'
        b'Uu8EmifZ6bMXg1p3eGVzSv+lO0GCJFb45lBKhk/yc2FUgx37z5UmcTgcg+8o9POv3Pc9QsnfcHOISySn+wRlSf0Pbg41iMNSFmmJ8tJ66d5Q7T/o3vBP+GB/drhnkfzX'
        b'wHLTMM1cFlhukooX938FWm76H+nj/Yk+1WSyxfksgt3dpUqnze6d6URVYdiTNNiZD2tAow2syXJRoo65xMalx+LFQ5wq5btEzQWeh91lFoG9XOIeufNuRlfRvrf1gf67'
        b'Mxwnf/nWQK3LewP6wOStwZWcxKYz3AgvSaJb/TWj4567PdaGrVsl0aG+MlZdpDWNzyVLk3y4XYgXdpswIo0aWsbtCuIag50qRHNLaAQPaLuG4EuQPyizElVWT7R1574m'
        b'kHjeHp3TtYtmlBTNKiibW1yy8I51AXbwWYBBZF+ZWL4WgUz4uP54wp+RijrKuNrynd5Kh9274u6aOQ05jwLrG5vUarwGm6d6h1P2V/0GrUOV3YPtGU9wz0ACTo3TegWd'
        b'97w0FfUMvX+lU6xGKdmDmd3gEDiV4JaMFR5VKLW58JIZV8sbHGWRt1aD5hgB3JEM98OdXIprwKGqHQnjs4q5VF8GvigrHLM3jk/xOSw+0PoSuDchMTkZY0lpoMx7U7hS'
        b'2KtL0sxcoE31cQQYosftGT+UxXK8NY1K15nf4VXOo7iZHOrFDLLlPzlOhVpYRNDFEgcjZlCzsZft0mBVfDhCpRaMHTNisrcM5YDPxwzto9InVX2/gEfxfpimynF8+xtS'
        b'2nNzVWpQwwhnMXtRvoi1lzmlbvgI8UlbfZDSfnSUxAsXq1FrNaxQJyh0izUSs/EGwyY+Qq2s+6OQ0i3cKsWnts7HVz8KtfuYi0/PTHbeJuY+nVeG0ifpfP9Ztc78DIpS'
        b'E3J2GbpJMRubv5QLRHGfDLi5ylywJbhhJ++x4go5ZpBirscv/HxY75rbNdQb1OvGcbie+ZGk3A0zGoexPJQBiv88gASVZgwPoy7mKmmhXOUPSdBbzjU1aHTIk31J5Z1e'
        b'Q6iblFpes8aPRk8PqXX35pAwXnhoTdZcGiV+RK0fs4097O+GLXNgTRyB7pGoUBpwRyao4cYH6JWZgvlcqSaqX+L076sy8mZ94G50ccfHP9jHp3/cnOd7rrhll8d0RcR3'
        b'8i3bgv9eIpg8VkVtzR6Dt20Wmz3z/eriul93/Hop71rdp+9WhLvXXQ/+9LO7s5YN9j+NGYrZV5AWdwhsv7VSJWJX9zKdxpZxq67HbLq9vMp5V9sRUfjN8Q+7/U6afPS7'
        b'oempGRfDL6d6dzwU1bRMupmXt0hn/aSyCYHLjb/ufjj28cpVie+/oHw3DqeuTLy43dElX+fnkaRnVbfcPS2vnXy3fME3I+7vrB/zaOXy9oari7wNBe1F/mcsAqYXqi22'
        b'+XHxmusqn5S9iP4+f2vY/Zi5xoseK5q2J7yzc623b6h5qSzZMTdFfu7kDYv2CdFTTXn5dZeL4/vu2OdVL1n28czqh71Dsn3jGg0LJr2/++whDb++Lz874x3Sa+S5ydm3'
        b'p+Q3X4/9930MfpZEPD6k1n1/rzD/q5NDPdJ3PLS75ds++dD1/ueO1wMPfbb94f6CMceHlz8e93R5f3rui/eTvzvqD3nPZ66el1xwbxj25bXe9M788G5EysyKlvTtV69R'
        b'9w8aL/uh57rZb+865tyYst6w6uE9lcTPA8q/1P3uRzDzg53mR+Kqxj8I2t21vkvvu8jreu43uPVdLd/5NH+aF3nB/vmXpnNiNq3ev+vrU16i3/rXhC/+OnBGjrB3o88G'
        b'p/Pvts+oiLvxdJGu+CMdr1+j7+4RTV2Vv+fJx8OTzqwUXju3gtO0fa6BUR5fn+xfq+BKtOnj/z/m3gMgyiPvH3+2AEtZeq9LE5belCqKINJRARsWliqKgLug2GJXEMsi'
        b'KruAsthYbIANFBUzk5yJSe7YrAmLMV4u7VrOaJq55HL5z8yzuyxocvFe39/7v5wP+7SZeaZ851s/XxzypI+oqxzuKGP6wSZ1GjKBE9iNBT8aMozjYgXEzCp/e1pkHIDH'
        b'J2PX7cwsOBiAtrFQBjgHe4uJOG4H+qKJEJqKvWENKI5eMehkvgKGkEjJwy/3lcBdopo1+bB/DdcU7DczgxdNVutRtvAYCxwtpzN+IVrfBwaJYO6Yi0RzWiw/CAZI28JB'
        b'GzwEGzPBuVp4ColkYAdjFuyNodt2EbbX+KeppWB9l5q5TGt4DJ7+hsZK2w+OkMbBc7Ab3SciciE8QFo+BfZAORKu1eoAwyCw3ZgJmuEZcJ0UvXI6uIZe5gdiR2h9cBKK'
        b'C5ieoNeZ1lDsg+ei/LWYKkf4GFZlDo+8WJWVhopd4AfrUzPQTmYM+pjwKNyRRgv8Z8AhRKpTM9U9jc76lzBLIsBhWlew23/q2B4ILoE2tAfqmdAex4NQDnYRZL0MPhpD'
        b'ByCOZVovgEf4dv8HPsUEiuwXPIfVsvTYVitk6atl6ctMercrnc1gcx2QlGrjgGQqMyuFmRtOabG+ab3MS2nnI2bjsw1NG2SRSjt/MXvUjiezbt4sZv/JwkHiJdO7ZzFJ'
        b'7qGytm9JbUqVFHaUS8vbVspDe3NHJicrJieLU4etZ4kZKitr8VyxQDxZMktp5Tlq7SZjHspGmzbO9NFcJ2Y/cHCWzJGxZbWdJkqHQLH+qK27zL3Lp9NH7tubrPSIVdrG'
        b'IYHQ1k7CkiRI9SRF4gp0amUr8W6OkyXIiuTunSXyxF5G90xZVm+J0itW5eguTlQ5usiMFI5+YgOVvUOHgdRAZqC0DxHrqazsJaHN0aPOPnJGj0G3QS+rt0IRMuN2stI3'
        b'XemcIZ6pcnQTJz60c0Lim2yRwi2410uB5a3vP3J270yUG5zIUDiHiGeOOnrLBF2lnaVyJNxEKR2j0TtWdionJABLciWR4iScLKamLVrO6jZWOEWIkzDnktKUIsmV5t+z'
        b'5qt4XrKaTmNxgrhEXCpO1bI1Kie3pqSPUCl5kjg6j4nSKXjEaXJvmDjpoR2PFkR57kQQY8nLu80GbJW86eiaE08W1haj8vLuSu5Mlkf02ii9IgfcFV6xkpkqDx9aKJvk'
        b'Qxqc2xuunBSJ5TEvWY7cojNPHi6L652s9IxSIdFMI4w9MURSC5oX3pNkJbIMVIoXvyuzM7N30oCX0mva888zOjN67ZVeMejM3KLFoMngkOHThQzK0ue7RQzK3Fo7ecbP'
        b'qQnzzcxaYcZD1yR5YoxGrbKyq09/WoZLec9i0g8iLpq9rzJTDNO4rLtcozQnA5rnM7nPrhbULL/PLhbUCO4blpXULKspr6l4saBg4qKpm7+E5hPxoiEHayO1BIVTl5Rg'
        b'PtHzOyRBeb4Is3gEcUJFTB1xQCuNlFK0NEJwavWQ5ERFsLS4tOz/TVxaPepZsGvEg+J9A5wDJ0FLejaSCM5hEFFsi0P00hL0s+A22JxSnjL9EZvEMHw/KetS0TEkdshe'
        b'MwfWwP7tzfXL3zwJbktNKU9HlpOiiB4o1sQ+x+KQllZx8cCNkStDDbnC/CHOMrZ8LskyViwvV1hFDZtE6XD9+kI2Hid9fHge869Padxi6VHFZZNDnob7x86wZXPRqLq8'
        b'yIDireb/eECf8bnTNkEXY/7WzTuUCLsSlhzx1R2p5Xeb4l+j9I1M/mrSHkgF32Ml5rr+prESjRsrE81YqUHln1SiseLaiWskue+ZeDw7UHq/daBwweSwQHegVuGBsn85'
        b'A4Wdh+JZ6oFi0E6SEez/N0P17NozyqIxtDvgNbAT7oJ9YwIlkiaNo4igZTPNlbkRiXWPg8tKo/i3GeSi6QYW+aiQKW8tK8lQm7FHCimsVqjr3cwSOuS5UrQsuh8cn5kD'
        b'9tWB8/hsBwWObaohj++dpbYP235ZkbW5joai9odbwOmcQHjEPyWVhbjWs+YLmYzk5PK/zv+ZIZKhB6bu+/BSkRRNKUday1ATtJLTaJnCDT/dWpCcI8+yP3rH/B2jZm4J'
        b'pzSsZNuZ4lK9t/4W/mnorrDl0/O8FoXKzpRt7Q7We1cvo3NvwhcLKkq4Je+WFBVwPn7N486uRx56+l4/bjn9A/Mf7Na39n1wx8gk6osSM4HeaGOIuD16R2C9Qc4Sc7fT'
        b'9iFs6bcOiQ4sh3dG354uuC0Ht0eZ1MkEm7/1qvgcOkVlc/TGuXb+gb7Yl0AftDID88FpOtrwTLazDuMN2uEezHqDC3AriezzBFdtiCcC4r+zsdGpYT3ci1hguB1eIVxh'
        b'lQHYrgXx44CmHGKWugT30Dzj9RC4a/JqcJawyLAB8civMD3gkAfNPR8ysPXPtKQxu9XWJXgTdNOxjKdDwC5/cCMxhUQTsiNx6tRDYD+5WZHhCRvB0TyN3YpYraBsJt/g'
        b't2x3eDmqLS/0kjbB5Le6uHQZ3kuFdpoVfZJSG14w9bVviWmKaY6rTxo1d5EUd6yUrpT7KF3DlObh9QmfmtuKV0u8leY8mYXC3LM+QWVlU5/00NLqUzsXiQBv/k1sxA+a'
        b'W7cYNxlLcmUJ0gUjzgEK5wD5HKVz8D3zkKcGFGIW3R9zKK7FgYyGjL1ZKhPzA+kN6RKOLEJqds/EF5XYEtkU2RJ3ME7GHrYKkNW8axVQn0TYBB0iYyD8O/4g9q8Cg5AO'
        b'UG/3NK3Bn0wO+ZqtHtMaEaE1j6kXJDiY1o5b64bqv1/HMRDB4R6mFlNCRg4lZOYwhKwcppDtQC1EpAMdTdA/gwhmDisa7RpEiUp8trEiNYKTw8aESUNghHqL9T2oHD1H'
        b'Kkc/xyCaKTQg5xx0bkjOOeTcCJ0bk3NDcm6Czrnk3Iicm6JzM3JuTM7N0bkFOTch55bo3Iqcc8m5NTq3Ieem5NwWnduRczNybo/OHci5OTl3ROdO5NwCfQ1WtjrjrxBa'
        b'kru8EGqx5RjRTGJMYQgt0XNYjWyISLELedYqx1VoXeZmuJzvft8gU1CJoy7KV6KRWm9jlDNzdgJvFX2NRxLBBBnxGWSrGUf0DTX0FofdxHN00gJoe5js1IZa8q//csn/'
        b'+hyj1MrymnJBRfn6EhHJljSu7eWVohocNBJkZBRTLRAKVvHwYozh4cw3+BevpoonoF+ZnZTMKy2vQI8+M83GbymuWQRTfF6Fnz+mIrNTkOwaOI8GOBGAyyngPKwPCGJQ'
        b'sxgGkXEBtYF4bVhNNq5enYOuq59LyeWs4VZDmUUurM8kONaIUBbxOCbTgZxgrKObB2FjYFpmhokGmb0FSui9bCAM3vDHQNcH0jFy/nZnDpQyN5jm0sktdhsX+qdl0smo'
        b'/RmUlQ8rDcpgGzgVRiO0D8At8Hx6WBqTYsAeKocP+6cvpJ38+upSEMnOYFDMQkb6vFC3cLJdOfiC1iiT9KA0Om25cRUTSmeDc8RxrQQchZ3wBmwilBzDMzZm4NTmsIM1'
        b'Y1kZUevNBntAaw7YlQ7Op6BW4SLMPFkL4OUSGlH9lqGTWjeA7sSFcUA/c4N5IP2h54HcMT010w/dZVLwZDQHNDLB1mkx5M2wVeAIOFabPi4/wFoTck8ApK6oKWlwL7gW'
        b'qcHRNayhd+s2OICVIDgHA3MpwxueD2ZOohF9pKnYtwqj+dvAdnWaBTiUr06zAI/B7ZFO6RMyJYBecIMohqcvpX3MQqZsM/nbkgUU7SG5BQymgVtgC8m9QLkHLiJ8gYWl'
        b'+tk1nPD84s2URj6QgK5ibWIEcBIeoZMjkMwIevAmefdftUw1X7Lcr8RHzYKsAe1zUcsCQHfSMnWahrrltB9sG5trXDohUQOrcC04RKvFL6Hh1ORp4GWRNA2wHrQQyJ8U'
        b'Cnv+PpPqAB6Fp+hUCqULo+jOuaEPjlSBJjxLiFSDxssUylhL4DZBOfu9bpZIjoj00IPKU7npWTDE/IqVz6rWHe+6rUqYIbYJEC8Y1pvxsdHhfy3sYxi+dvodPZVQz/RO'
        b'a2NI1qo73R+e3hYQ1ix9+vknLZ+G/nNGHN/8D3VlFrK/Xb9v/42le31LfWft1Y2fT93zoHFX5d4y4xtP3h81nXf5wKkfh05zptbWHBMc3Qxv5C/43rJhkk9ou+xzzmsz'
        b'Ruscj/zZX3m0S6/aoYmxb8fGc18zFbdi+Y0BFf16Tvmqk3of9PXe/Hzv0o3zPwlcup4KfvL4Iqtuqllw1Sj/Su+sSX4dPwS+vWhZQO86nyH3ZuN/8X4ykzu+elnikqr3'
        b'6nenbhrfjp3XlHBq1fJS+WDhkbecne7G3vwmI6Sw6KfMQ4wDja3h1+6UyM82Vk8OydueObWee17VsGdf+6OY8ClS8Z+/eXC0dLLi4Vc/9J5/NevwUX5sT5bnmmz4x+aH'
        b'A6Fy4YrNwXa3Pwx9krvh8MPwnFd7nkoVbZzCb/7d/c0k7s2G++2Sd9Ahav3Ikjfd8JU3p30zacO3t75tf3j14fn87Uf9YnPW5FeJHP99bOnNhrORLoMDLvn3fu4z+eEP'
        b'3ypj0+I3Mz43qjr7NIPvSNxtcsFQOaFw2NpBOCXjAJq92wFbAJo3LekZfkE0I2VcwYQnS2A9Ye/mLQetsBHx2bRRDYjBZQ5sZG5CzFULDUVwGfaAcxj4hA9OWmmtXjZg'
        b'N5tTA2U0qgGQLtZBeUmA4nG2MXA9n8ZIGZo5GzTmIwp3IBCbMzBXH5RP40fcAgfMN2L072AtsTQWMWEr7OMSBrYASuEhtUcRIwYOJIBrcDdpINgzE8jQe2mZAtivJaW2'
        b'8Bg7Bt6CN2ltaTsYTAeN2WFpaKHuYFKsCsY8MEj7esV6AJzyHlU7Nx7j9HYwgBi2raWbJYOD8AxoX4ge0BBV0+WsKNgBemjt8s5pYD/JTaBDUi0jWZsMQCc8CwZJC0Wg'
        b'D9xAJYxRVcsNLLRFDIF+eAE20gg0bfB6rhB1Q2O2lsIaz0EdgEZETI9kF9xTCzoQXc3WkFljbyZqYbMfjerbARui/RGLfHAcNC8cXEjAKZxAD/qugy6kAi1VNDNk1cCL'
        b'4CTNcEtXwEHQKIIHsgl5YuM8LQ4by8iXgt1INNiNx2eMOlnCUyy4bybcuhJuUQsTQB6pl0rQUAiVMkZzCfaDA3AHze/vj6vRM0dN0GwEpomsZCgNpdGMzsGr4Jh/VuAz'
        b'OVvgyRA6bcv0WgMLnH+EHpwWeAJega3TcP9rN2bTMlaMnjF5YGoE6mIycBo6ZxnFMpsGbsDWCtIndXB/ImprCm4wvTYsTVlwK6gHp53BCb7pS/IAw8a28TC8OhnmzdXs'
        b'3Pjk8vNY6uTyObTaR5akTi7v5CZOUutKXToipZEYzEIeoXQKwZfpK/HSeLkXDXDxwNV3mB+vdJ02bD9t1MlXbq10ChInPXRyI2m+k5Wus4btZ6lc3GWTpItxXudRtwB5'
        b'bq9v91KlWxzOSY9dw3y6fDt95bFKj0icnlvlzMOOSLK8tmySqnz8KU7eXdyzvHt57zqlNhX7qHuQvKanrrtuwEgZnKh0T8J5yp97ESeprpPWyTlKt1Bc/UdunviPysGl'
        b'w15qL/NVOviL9UnuaZ4sWWnn9yefIJwrPVm6VD6vd2b3kmHnWJyHfYo0C/+JVjgHfm3A9nWUsNtNHptS/GD5OoVv9ICHwnfqiG+iwjfxduIbFkrfdAl31IPfu2agXBGZ'
        b'ovBIlRio/EN7+Qr/OInBPXtfle/k3kL0nsSgnasKiB5wVwSQG3yVX0ivg8IvdiBB4ReP7pqpQiIl7A4Tqcl79oH/uWk6pzEK5yD8NwoJhF9zDdQtNscp1TOaMkaswxTW'
        b'Yb1TBoIV4Wn3rNNVAWiw8Y171vyP3L1Jxzm5dURJo2RpSqdgMeehlRPuoRSlXcCf+CEqF29ZqcIlUF43oNe9edh5msrZSzYP1YT/LlQ4B6M+8sM1Ykc7fij6JN/YgRkK'
        b'32kjvjMVvjNvF70RqvTNpPuo7rahIjJN4ZGO+yi8N1XhH/+f+iisN1rhN3VAoPCbTvooLBr1kanU9D374N/SON3zRQrnEPx3Aeou1E3qRpNuymrKGrGOUFhH9C4YqFJM'
        b'zrpnnY0BFvjdfNRV6CZOXY676rCpjqhsQiMQsH9BH/ebVOZji1on23ckKrFaV45ekoPl6G9fUI4mCV1b9f2oM8aT/7tE3yQzkNcvJzkeoz6aHN/voGbrZBb2IDm01QLa'
        b'WI7ol5PUW53i1mCZqLys8pfTaUej3hzGzbJmjmuWJp02fltQUyt8eelt2csKwwp/rTlK3JxebS/5JlcIynjlpbzyGl65CAmpM8JmaHvtpTRK+Bn1y7mJcYveH98iZ5Iu'
        b'VlhSXF5TJXwpyc/JVPLX+/VWjOJWjKX8dVW3gs52/lIzEBsuW1VVXF5a/uvT5gFuz1jGZh+SologquHRLxe9zIaVaRpWUldSVPsr6eFxw/44vmFe2obRL7+8VmnXGEHi'
        b'+NU2fTx+jflpJnWNDglAs5su6CW2rLikEE3SX2vZZ+Nb5kZWP3nrpefbNlymWTW/1qC/jB8+93Gr7eU3SaOY/rUm/X18k7x1tWZ4BDUqs/HN0q1xfNph7MvKzGNpfUOp'
        b'XB31XyXDFTVbRx3IGKf4oxIYRB34zNUX8Q3V/wXfVdK6/92kyKh160OMyPxfu7wE9Z4QdSGa+jqrQFhCZ36v4aERr6yqmaCJfG6u6+MWPzNIruuBWT9eUpaQbNfjcl1n'
        b'/oXPoKXB3tRlWNQ6aa+jHSQiLdjl+ZxEy19ifDw3zV6ubduYg2lpWUnNuMTXhfMZlDOBwhu29nvBzMu4NuFiNOe+1HEf/TZ//n+Vefm3GJDRaP6/MiA/Ow/RwAnLM/RE'
        b'GHP8bEbsjoQxE3Lx3Tcoffe90SYh4t9jk1uSJ2v/A091vnIeaJmJxtBt88QhdFz56/Zl4dP/OJoi9WhaUmoxEY2mj7988omV4qTD2eNMzmQ4rRi/0eSMqxYWoKvf6Zqc'
        b'y/HQOryoyZnPpJOTIrlenp6+dBJW3rDNGKALngI3aYVmE9gNGtL9YS/szMJ3wxngEgv0lptX7WKIwtATn736LXbp5t0xv1sM7N/2fV38epNB8e6wjye1heiFb12312Lv'
        b'q2+vz/DDBvz9PP3m1xo00/h5LDse07Fv/Qc63Ld4pptJxzrRHatic75dMJ/BtvD/zpRhEfYRz0thFz5sHj5uwTyvX5+tSShAvfpI06uo7O8W4l41fDmZ4smCYROiSCd6'
        b'prRm/JdLGrEdJ9AoEfuri2jmABHD8WYcEU9UU15RwVsjqCgvnkAXn/XP0M/KTSa6cgf7DRSHQdU94fLWLHBZXFf+dXAKS7QJTxM/Jm1jt0TEMkJWY+TJSozxnM21qpzc'
        b'sM2El7PgsZySAnYu3HVnknsv3zlJsm3mvkDPB86u+voHyvX0vwj6fRFHMK+QU8IRhJXMCM/fwvB1fW1f9x3rzpbQerv+jb7bg+xYieZup/cUlJ7lh4x0hQuvUpT7v6xs'
        b'eP/mc2hI2f16Yf46iiJTrzJwlTUL9KldPY3AkGjMzoONPKkzN4BmuIW2gh+FFwLHTCfYcJIKL2zICKQVWdvhRdBJDEF2GWOmINgGzmTTPpunZ87StcnAE7AZ22WG0mjt'
        b'Ziu8ALYR9dcaIKXYOB95OTxDe7b2RMRgtWw/OJCdCs6xKf0KpgdoB/VEI1sJ5CQQ81yAvp6QYjszwEV42o2v98tSL/ba0LGbc8pFy8g4j0mSmitkHa2n5/rj9YhA2Tu3'
        b'bGrZpHIifpYbWjbIirtWdq1UOWGft5ZXWl6Re/UE9gSi84+s7VsymzJHrENkuV35nflixqgVtqLbj1j5Kaz8sFujvlS/jSNOwA6YaU1pzRmyUIW1F31bnqu0CqVLHWcW'
        b'f86+9lyruI5bgLACqwZWocOPGmmehBCRnQ5bxV9ouyM00UQ4DZf5OS49A/8iyIBz8a9sfEjFh2R8+ALT7Dx94seqJU7COHRBnezX5pdx/8Yg/7AzgPALPFQsJNMK+fj0'
        b'HYwvyNHIT/c5GoHlvj7N29/Xp5nr+xwNT3ufo/WN+Ie2XwiMH/d/rh7Fjo3PgeVz1FcfsJ1bZKuB5WNyzb/Sp0xtpOHSGomfguv9lLmQwZ30NUWOLMp00mNy4ckapgbN'
        b'Lgqj2cUQMDtb11FzPn3FNqY+eQwDD8PbWU1nEBA89aUwfCmCXFHD20VgeLspBN5OjYo3FaPiTSOgeOorMfhKHLmirgzD8tnOYJDa1Jcm40uR5Ir6NYzvZx+tWxCGSbWf'
        b'Wp/yHceIG/HElnJwV9gHd0afiEV/6lOfss25zl9T6EAj5REa1QP3gH3wEq0Lz1uZqofI0n4mGMx2HkeELdV/v8aaoXiH53pj6BNvDHv0j8phRTOJlwA3zzLPKkLvRb0w'
        b'6HcRA2dEfBloLwzHEGqx4QS/B8OxenOMoxlkJzNGNbKxz4ZOjUYTntNDYgB33BPG477APsc0mpnjREqzJOWZ46dXMLTPm2if176D/VDU/+xzLKL1XSlXKsc5j0GwBGlv'
        b'CW6eaZ55nkWeVZ59hAn2ExlXJnd8G9T/OOifIeoLq2hWjgvxb9Ej3hfGeSaoNDPcvjzrPJs82zw7VKo59jYZV6rpM6WqS8RtzbEhpeqpyzMjZdmicgyxl8q4csx0+tAO'
        b'9yHqFyb2XdHpRfMcB6FFmRna813vm6rJO/qDQ9PLTY0pav0XRgm88dcxF4D+ingCxADosgXY30NQwxMIsRpxdW05IixGpUh0Is8Uo9OiGizSl9fwaoSCSpGgCOtAREFG'
        b'Rqk1iJ2oEqqL1JYmEGklWsSHVPIEvLLyNSWV6qKqhOvQq0FBvLUCYWV5ZVlMjJERNsBgoXhCg7XsyoyZuQlBvKSqSp8aXq2ohIdbVy2sKq4lTXE34jNpTfE7zAmRoNqw'
        b'y2p0iNfTRoIyNYCTxK3GQBsDqvcSY0CxpPrDM241GlZsleYbf5NnjbbrsNCLxkm3v0nv4cEjY1EcxEslys7iKlQjkn55JXXlohp8ZS3uykK11g89qKlQrRSh63xGVbK2'
        b'HDcC3SmtRa8LiovReKvrrCxG/3iC6uqq8kpUoK5ScwJvqU9N5C25WbXxFM4acBj0kwRK8Azcp06ilKI1C8KDcF8GSXc0NyUjS5NTAAzB3cbwVGFVbQiFk0odgzKdHExg'
        b'i0inBPSe2p65Bu423AQlM4l44wXaObDZnw+2ZAWmsCk9HwaUgA7YRONoXYTb1/mjuWMG9tVRdc4pxI2morQ4JxCehhfhqTCKFUSZCcCOOKbXZlsSElsHeoxJxmhtOCz2'
        b'aZo9F14zC5zHpCL5GGxTCmloQdiUUe2P5qoFHBBRItARRLjsGjMWxa6Zjn4VBAQ5LqdIbiumDTibXjhv7HtgfcYcnCAiAO7PpBMxzKkygFsi4WUi0oG2lVzRasRFwAMY'
        b'53A32AN2wMHyPxoa6Ymc0Ub9+PyFfXPfws4jzh+si8q1dt/h91rnJEtLg6jPt+WabqRSrp5wNd+dtmkxb/4txqN/BRt3Ky+3JXnN/WLJl1+8vf4r8SvQ3/jfDypGPuPU'
        b'zXH/e5L73z5MMw/6ITLranV3ZtTvS+P+XDv95t9d78mNP8t1//umna4Pnpjnh0PPV574JF7Rj39zDpi5Nee45aneLufPPn40eMtz5+Arj77kfmhybGh9adQn1ywrdj05'
        b'ZtYwsmqK8MS8Dlf5tD/fbLwd6xA1+JdpopjTVd5mf/77reZrN36mbH/cPOf9d89v+u79gQXbjq+uv3FcvvqdWdEbK7h/ljRUpze+df5g+/zRlcdEsxJSFzTMmNv3pGi7'
        b'/4NHzrI9VyIklttfVf49I7PPlmXTUTvz6j8Z18+GrYr04lvT+Wx2QenSdHBiqcaJK3QzaCVG6SXgShZxtxjnawHOgAYOaMyiTf03gEQv3Qd0jvOnAkfATjpPx80gsNdf'
        b'7TU7A3ZhdxCbDUQc0N8Mz6fDXc7jnUE2oxeJsLAPdIBjY2Aw7Dl87FZLLSPG+/RgLIRgfzm+fgU8QhlaM0EnaNUjMowTOBoOGxHnkYXnkB/i0OAhAbjMmlMDbtEBfgEr'
        b'/YPhZbAN7sFmen0gZwbAbj3abQDDlPaNuaEYgH6KeKGke5HOMjOPRdIR6id2Pmh0Z4Cj4CwUk0+tSlnkH7SyTDe1+DZwgfTjVIv1/rQnBBJ/cGLyQMTHgatsff0UR9BA'
        b'Ozw0eOQhiQ7IwCW6N/StmFxwIJ/2K6nHOJc4S0g6zsPRyCwmHjIWoIUFDkw2Iw1nO5I8ImNUwxTcgJdzWJlhs77BvoSwLQa71xCwIJxsZf+6lSmZcD/YH5weSJLDYLQ7'
        b'JEQagAMsR1pSvIZG+gDtD8eiWKKlxB0ONMwivVwATseSLCu6OVbAjpVLDUEfnei7FZzGLg2oQQDXh2tDXCfFKgK9cAjuX8A3+i84dIx1MAGohnZesBu/mY73YZjPoGW/'
        b'5IVI9nPDEt8DR69h72Sl46xh61kqO9eWzS2byaVpSsfpw9bTVXYOLWub1rZsbtosq1HaBYjZGpeGOGmcnC0vUzpNEXM0T73S9IqseMTOX2GHmGXblvSmdBn7nrX3qIOL'
        b'ZLmcdc8hoJepsnfs4Eg5w+5hvfP78/vyFe7T79knPGVRjoHDDgEfOTh12EntOlylrnLOiEOowiGUtCZqIEKhadKfdEtz5XWUScvayjuqpFVK1+AR1xiFa4zSNW5gjsJ1'
        b'moRFyv0IfRaO8CpS2vGJ98U0pev0YfvpKhd37GChcucTez3Ph3hGeEyS1Y74TFP4TBvxEdyedSfj1YyRpHxFUv7w4gJlkkDpUShmHzZ76oAKfs8h4IenRuofIjJ7/d2S'
        b'A1ivGYUkT2X9LsAoOcbgd1ONZhmr48KMdIzbmGX5DRZuGkVDa9PWMWijOUQ5GevEgIkWIBHYHaNouL+oQVuqz6e6jSP+O4O22iSi92vmkGdmpca2HYe+QMe2Ha5lf57l'
        b'd3R4nZdk7Cb20w9/2RQvbEJ9PA23UGs/FeboT/CjHw/gwaJNNHlsrXL85RppngmX+/+VkQa1TvgFc0IHPdfu8uBwP4vYXfacvnFJbXUxmUzsLvkUn88McDrLZxAnt9g4'
        b'tIlOpJ5wdzoioHAInLf6JdPLpAkzTlRUsYxgevyKBWbuov+hBUaKZkeisY4FJnHRy7PAjIsMIwrlPMb/UmTYb7AFsrNqcdIOsBttr0d191M8QthNvyHDLy0AnMmlPfZh'
        b'Pdi1HkepY20pOAsajKNhH7hWHtbYyxbNQAXJJAtojfK5VylGQ5iJifveBBMJddpjZ9tW91aHSY5vL78bJOcIToXtCvFlZG57kigRSgrOvOsQpaQqCvV/evQZn/UNtk/A'
        b'AVAPuie2SHd/hyfgcc0eD2/CUyQBmRfap9u0HrPJ8MgENJn14ArtdNk7xR/NRxHoeWZDx0DfnF+xc4xR8Ke/dYZqrEp8eoZ+twDNUHsXWd6I91T0f+IymKZ0TR+2Tx+d'
        b'5PccY5PBrxubfiHyiJicOtBcztRsMNjkNB/PZQesY30huxPuXD6TuNnPgVvhufR02upkbckAXbPgIXLHBTFZ4nR/2uIUsoiBmM9rM8u/0HufJYrAPXetDJv4nrE57b4o'
        b'CTEI3/pPrc3J4F/t5VT7A/3hxGQ1/s5/0JuPffQ/8ZjY/9KYkFFwobQmqOmLGBwL/6fWLIuwxxzK3fsZI5TeL/f3cyoWYkznGcZjpqinCYte1BSFoX8QNcTq5XEERBvV'
        b'uYKiLVLqKCP9PEaeAdoL9LQkRO/lmnHXlxrNKqnhCTS7tq7yaUzvsUpYUkrrIJ5xagsyihGW1NQKK0UxvAReDImkiilQD1EBr6pwRUnRRDP/s+YsvazacPR7ZUglkYaw'
        b'USZv9vzAefN1I49SwO5ITeQR2BJhuAI2wTMk+Ci5PCx9gmJivBw+F+wFh40N4D4O3FfOzZWyRVXotY8rlZeKjmJ69po5sAS2r20xzJDyalwTOf5T/skrzeibrZ+TzEln'
        b'+R0Ed27jeFSzUhOBoqRoy9m0EhPB3BnvHr5jf9f+tV3lQcM7nRcs3jLzVF40K9EjcjircuBoBueDGQ552Efh2JGmNdwd7EK+Ph1Uuntlkb82OBNuWwsuMIS0weoY30sj'
        b'zoGumTiwlAQVdNFiU3UyEE8QcQOzcUDBEg8SzQBawI0obC67tVotHM+mfdzBLjOP9DFpyzgpdRETXgD7kDSIV/4SRG6lE9LNmsBrYyBdqF0vEB+qAyVijOND1VPmvuOE'
        b'datzj6zclfSqelKD6aeXLEnuhR1RlXYRGPLhGeGFyBwzbucqvFOVjmnD1mmjju4yr7ZAsYHKyrEltilW5tUV0BlAJ+xTWoURALCpSsf4Yet4JESJdT1aOTQFJkafXzd1'
        b'ccbIsJoydGNJ4QxG9delwyWYMtg/edEI0NO/yFgUUzRnqA45p7QORi8d6mF9LaEINc86i1WVagIJ/+cEIoEu8xcIxHPdSd74fAOTQLxF/c6WBqyzxsHjM+wzO4+vM+k0'
        b'SciQ+CHeNKg5n9rHZ737YR2fSTQSS8E+sBNtaKBBG+8AD3rqUY7wKHt99GKiEPG18d7koI3Do4Pw5lc93+FE658Qj3ej581qdYeRWe1Oz+rHufkMysltxNFP4egnj1A6'
        b'hqCJioReNKOHzb3H7Um/NBdpOLoxbhZXL+xBM69YsyehmffdzPwXxTnAmzcSCkj8s4FIsKZkmUCUNU5Vr1URV1Ka3Ymo6undiYOkKSpC/39NUf+Vdj5i00WxOpPpc2dj'
        b'gtZ8UlIjwK6gAtrpbFXVGrS34dRrmnJ+69Sln1H3SgzW3xODSQBW2q+qFdVgpT29VEQ15ZW0YywWjokWnhaQx7kRYrsJKqxYd1XguoWCtfTnoTb/RwW9UVYt7i/QD09j'
        b'EGr1pAbNk5+3Z47bMDty6fQVV8EecMUfB8imUHDHRnh4yUYCjdemL8jJ467hVrPndlBsKaPmTXei/97kR1IDbDSaXlCxwyuOyqXNp7gs2AqPVvtno6LmUptrMGA17Cv/'
        b'0vc4Q/R7dHdv9e5acaYp4JnvdJu93OmEa6dqxccgaPCe5wDlmLlYuvyTM6s/Advrlu3m/9VsSrnFDFfpP0sldxI2Fmyz3tW2QHDd6H451+qHr/ZkFnkbvfvh1U2fXqWC'
        b'Hnw2OTTO7vs5awuTVpyNqO2Zc++kl983bytXZk5u/YefV1bu6zlLw12iPi/5Vno4450457XKexnGk58OXDwawTR5EP3WB6kZn25cGjn9k9eTYpzXLVwfM3ckvfCL0yf/'
        b'/t25XqdXFO/aHE6pWPrx9w8vsW3+mR3xrYvVtFsOZTxJdRefQ6jFJnjTTrODwwPgONYUz6V1svAkPB0+ppJdDRroPRxcWE9UkcvSQe+zauqUNZwwOEBH++1dUqnW2sIh'
        b'eACrbcvhLlp/fUY4xd9PHaYGO4CEMoxlgg5rMESkHm/YAy4+V3crnJmSBo/SrEAz6C7VUVWjl7Cuuhr2ktuWoB3Ni2Ba2QyPwX20wrkPDP1PNKA8XXgxAzVmxH3b51BO'
        b'dJ1QTSVNNZ8I8/87XsAGo42x79l4yy3VytC2aHHSUxZlO+mxPs50nC/Nlzv0JihdpjQZ0ZBSOupTO8eWuqY6GVs2RzZXxlHa8ckTTRvE7IdWjlhTWiar0dWUyqzbTdVq'
        b'TCexsbhGbPzUBtX0no33D0/N0WX0LLlDKyBfNbFINGeBMMtEdxY0N0p0NYDuRokhagWkoQ797/2PITYiQ0pH90jvC4P4rRvoUKWreszH+4L7Vy+oehTOoYg7JFGFkh3C'
        b'UBs3Qvu0VGFXG3aFoLKsyECHaFlqiBbOfxlvQm8ZS1lL2Uv1luqjrQO7AmDzuQlxBzDLM0ebiUUehnCwQmIPTj1oHWGp3lIMco11thQO2lIMdLYUzrjNwyCBQ7aUZ67q'
        b'Cj2CSrS7GSUUF+Ogk8qSteM98bDtlLbD0mbhoiqhsERUXVVZXF5ZpoOhgPaCGEFNjTCmQCuBFhD6jnerKl5BQa6wtqSgIEAd3rKmREgch4hF30jwi9Z7XpGgEu8qwirs'
        b'XKTxQ68RCNH64BUKKleObV3jrMMTmLXn2oaDfsumhzc5bJwWVZcUkRYH0L1EtrSxYKbK2lWFJcJftFxrpwldzVi00drl5UXLx+2dpIWVglUlpIYqOnRC8x3LqyqKEXHQ'
        b'2XknBFasEghXlhTTVm8Rj46JCuJlY/fzteUiugbEDiyvKubFlNZWFqHhQs9oJI8C8qKmNUWCigrU54UlpVXqjVuLEEIPSi2O4cAuDgLynu4Yar9c63UWw5sY4DTm/q4p'
        b'V+MGr363MKzw2bd0w6ImPI/XHeJKcrJ5U8KjA0PJeS2ipmjSFpdoulLzLppK9CgFkcYnlZQKaitqRJoppn33uSPgI+LROXnXTWRd1COPm1aNeHv06zmM1DiOxuoZjsYn'
        b'i/ASm+e4icKEiJUA1+GtKsTgOIJ+gnYBbm62N16zmkFhK+Z+WE/BdtgEGvgMGvCjsQL2+SP5Fkm9BT5gPyPRBPbVTkF3NsKt8CB6cQ7NDfkGBfrC+mC/1EzEGJ3JrYYX'
        b'kczcUzNv9lzsCAAO+RlGwT7YUYuTyoG9oGWhju/C/BRaPNB6LTCmUkVLOaATnPMhPNK6UBOMkLwgfF5BRvAKFxqOG8qXwJtwawxmB7T+B7TDawA/ME2PmuqvD1tzo8nn'
        b'T4EX5vjDg/rzwHaKYUGBY+BoEin67gqSZinqA+8Ck5/j19JAXd9WEZ6MczatICM9yoG+uGgxgfRaIOEUZJwrX07RPg3nqyzhCaZhPkUZU8bwRhjBDiXP+3uR9FYpfy0o'
        b'MPmBU0QRzw9wDe4A5wg2S04K0dGmopbv9cc8pfYr0I2UgLSMIHigOjXQT5+CjXyT1eAc2E54U9gCj+EiJihz9qaa8BFzA7pzUzQ2cQpshdcMwYlVsDGZz6FxklvADpxP'
        b'LCOtYDOx59LW3F1wiORYs2Lx1dgmsN9lKSMYbPUl/hUrM1kE2gTeAmcz1dgm+Q40escFcASb8MdC+JfAVoxtkgMGiAeJKdhqjtFF4CV4HYfwE3wRxMwN0C6CEthXpQMw'
        b'kl5HQ4x4wh00xMs+0OSKYWWHEkj8PsEYiY8niXg3QHHRBIQR7zQ6Lp/gi8Arc/nGdCn1tXA37vVUeCpTA4mzaw6NcdIXixNqoolzIXvMWXoDuOFEbm+ohccR1+hVrguK'
        b'A9tgvReZWIEe8DiNh7N2LuyhYL85vE66bAEchFI1Ig44CM8XMkLBtig6yqA9d5MWEsfFi4DioE7sJKg4CUDqNg4QJx7IaUwc0AG2kCY5w0ugecz9GhwoJKg4XEAnLywF'
        b'20Av8e1OgH1a9+4Nm9EYk5Q2QylcHagV2AV30HAr4CI8QY/JRTQqx5HMDq6W6YrtwbCdbv8+2Amv5kBxHj45Do/Co1RlCegiSDau5WTtzO6bURCQ65ZCI8zELMMpNZuz'
        b'2RSzChw3oeCQOeznG5E8j6ihQ6BFZCqshX2IuJiBQ+Ag2AP7a1BPr2ClToYXayfhZp+C+zboPIWegEOxIni5FusbTrNQK86BrQR5ZpMLbNN9cm3NakMhF7V50FSf8mWx'
        b'4bb8taQrpm32hJdq4WXRarS+9oHT4IiZsJZFWTmzIp3LiPoT3ALnV4tW1xqRgszgFTgoMkSE7HItfgP20/VPW6qvBwdNaBieAwFF2hdQG9Hioh+yKmElwMtO5JuX5cPd'
        b'6CEOuG6k00LUOldwgT0JrbI2UlZytrVuUScRQRXCy6iBM1kxYBtsIAswyZmFHgJ7itVFwYs1+pS5PhNeWOZMvrLQCxw3hldrEFm4glpsYsgV6lHcV5jgEpDlkmSZ6EsO'
        b'WeVkwqYcNLSHc8A+NugDJ9GotzLgVUyZaOyjrUywK2f2bPQzDtyA2ykB6LIiNRSAXm9cA9yzanwFSGaVkdUAtywBYhG8apbpi+4x4WmGH5ovtVhBAm9AOc6OiAhhenBm'
        b'RnYe3jLmolrPmxExOwDTnb2pGXAPhoPZlmcoMl5HFnUOPA8Op8N9LHgE3qQYMRQ8hFbRUdKixbPM4aUURDx2+vLTA9FSymJTFqCdBY6kwn5Cntc6OlG4+kkWBc7XylJo'
        b'mi1c60/lUpT5LtsC5sdo96STG1LfT1P/8J3OZ9P7ogSJ+QfBWSSjg51og6LW1cFrBLRJn2cEzrLBNbCHotZT68H1THKZgWZSu7+BN2gnufnA4Cq6X/agUeiAjVjWP0xR'
        b'5VQ52A6uEnml3PPdUobIC/HTTW+cOjpvVfa96ebHvlu/9uZD42/qrs24uTI6RL7V2OIAZ4/jiYSiHQOD3N/9uIP5x7/M/3nL5lc73txcvej+0rd+P2VmyoLrX8d9/fbb'
        b'j37/qO3fy8w99b/6Q3Pxje8ZvIrTLbx4z8LD75Ww37H6qSjwk+MfGlx4pyzoy9KapbH3LkUbFLyf8c8Hsp8eTaFO3//w5/mOhRm1b7f8Y9ud9fv//JNzwd6VReZLY95y'
        b'mrVp75U3yj+PetST/2nA/hOLFl30i+xKvRGzw5z6+11JedjFnZZt56/uXGQtkjGDnsy7bF5e0Rm0ce8KXv7AlbYfC9Mv/nl69nmLtbGOW8+bj17JaXdz12cfh+9zfl50'
        b'1//xktr98fWzKlLqmJ93LxR9GffvzBHm0GDu4j879tf94Y26yAvVr4fNU2SW7X8lfVDg3u80zyPgEbujnq8wXSkxFJS1Ja25cm/tmhXr9f4x808PP/gx/YvQzqN7O7cq'
        b'1l0Lj9rjX9W7avLuqXkfnLxkXOj7g+TncI8hF49pJ97ecM1mRDnPN/PTaL2Df5sTIewJ+2pdyaeNd9/YfveNlsNNs75y/jI744tjuT/95ZXK5tq+Nx1VxbemSNsyPxec'
        b'Lfw8vXnNgp5bQsGJ9ZkXL4VtTPFetnLqF5sSPB2frpT3x8/raxj0+/uf3vnbhoB5i01bN546tvEfI8d7/rL8zt8+PS/hS7854730nW3zw58s+qk90vrp9DXNhcs85keO'
        b'CGKeBMrur37t3Azl2xFuvcpTWf13BzeG9IEjjy+6fPy7qX+X1L+WOvmT9RcMg7uLG3vuHF5s/4cNl/P+evjTXav+VOx77lq1Kn9h9LfrP+GUfRd0NiF20TvzW2s64iyz'
        b'nsRHf9B5dseH/SW3N/ML/7WxznN0h9VP3NiEri9crD/441vfhT4+P5WzyO0yixtq+6Nv0TZTt9UH1nYlf3y2ccDKwWfxoxOfWTVdcbvZ/r2+29fvwJiH7bY/zvhLzbrY'
        b'nx/uWb2Mf5T58d7puY+W62X/sV7yN9GOj3961XDed//mbDCaN713/dNlgS3f73Kdef3PJX+J+m7hQmv7wUE9p97wp3uPrPzQwGxVfLt9V/+dyWYXrnAlm7L/mTmg8ntz'
        b'cJH+95t2+nV94fjIetHmfzN+t2bQ4ZAlP4j42IG9k6AY86uGejrWactUFpCFwlvESBQCemG/msvJjkFMDuwH+8jL8JSrC9o3U0ptiMk8mzxjAXezwN5y2EmUTMngrDFW'
        b'MqVMGq9m4iyGZ4gHn+lceEqLKgckc4gjJDwUR5zhpiBO5Rp24EMU6yDtxKfjwgfrM2k91SA8KEAsRzSUYF0V1lPBhgjis7gkCWwhGPvg3AaNf2E1PEB72h1BDMJJrKWy'
        b'RWVNVFSlGGbR7nxDsLNUDX46L18Lf3qRVtZDWXymf1YmzlIN9+lT7AgG6M7PJR8WDS5ZE/UVYj6uaPwl82A/uZkWDM7Sqq+QEC34aTHspqvcXwFP03kDOmEHyR1QwPT0'
        b'g300AlN9DuxMxzBRe0FXcLo+pb+O6SUCF2k/zEOLoJjkKwB7pmjyKeBsCgsraKfVocgUrC48aq0FZC1IIZVmhCYQ31B4DHYQXpg4h8IT3qTSyfCWAc52G2yAmLPDaJs4'
        b'zsiDnUBCFzq4AZzA8SqwFX0nCV6bUkUmSC3YAnfCxgC4P28KGjvUG5kBiEsJZsHDsMeNtNgpL1jHHgh7QIMxtggi3mQ/KXxSDryl4QrrXTFTuBN00t10zrGOuFkeRp2k'
        b'Zc3h/il0SN0VsG8h4cFL4ZCGBV9SRL7GHV5do8uAR8/C/LfpGnX/woN8gu53DAxq+W/hEjqs+xQ44arDfcMBKKf571iwl8yIGRmwBc244qwx7nsB3EKMm47wSvAE9htc'
        b'X6jDf4csoytpQV8vxjCBtBVULwZco8zgFlaVNWijP24rPIHTvDcEZ9v4YzzgV5h+tqD7GyzmIa7s1GwdLs0MiQ7XV8MrXNjLCAPbGAHwuJ5hIGyl9biDYBsLzZfgyAx6'
        b'bDiwlYl36iKix7WDu8FRNTQwaAgOhCdSwXlfBuWUzEZrbLsh6bCohGqMPezjnzoZrRvKAHYyOYgj20kbgofAVsQpnmUvxxs52t/hGXP6I7c5gCP+WYErS3Ww2a08WXB/'
        b'KjhJk6YD5SY0llhQJtwzHdxKywxCVUMJG7SvM6GX8CASka6hh+AJ0I/oVwDiXNDgMCm7yexpaJ5e+wazt9U+sJMuKCswBexFvd4KJGil48XhDTv0CkAnl149Q7XwBIFK'
        b'3kOPimW6MdjHhJ0z7cnYzi0vIPr0hk3wTADq9SymMzgXR+hcLbhspus9vWkqkuMus+aAnagRpOwO0L0SXjJboyaC0cGGsJsJzheAM6RsjyVIigkOBC2r+L544pQxwUXv'
        b'DXz3l4Ng9r98IKbF5yfFnBgVeN9YUFz8i4Z4nXtE+e6tR5ssX1lM4JvjW+JlZeqYU4KbFtkT2x07kDO05HbeyNScN0ok0953yiNeuylvRP4h9s1YBX+e0nX+sP18XW9l'
        b'je3dyllh5dud0+twdumAQBk4jXYeVjpGD1tHq6zsmuJGHdxlXl1BnUG9XvccIgfCVHR6wbZ1HZulm5VuISNusQq3WKXbVAl71N1Llit375x/wlmiP+rh3Vkk95Kv7vY5'
        b'UdE7RzFpitIjcsRjqsJj6kCp0mOmhC2ZIzXAKnuc3YPRbqTV3nc5dDrII0643bMPVV8bu2mJb55wumcf+NSMcox6bE45u2J7gixCzpC7y6KVToHipI+s7KSxshqlU4DS'
        b'KoB80CylY8qwdcqoned444UajTq+KV7mNWLlo7DyecZ4obJ1baloqmiuFLM+cuapXH1GXGfIE3tSulPOpo0ETFcETFcGzBhxTbtdrHL3Uzm5YhSzOGnciJO/wslf5ebR'
        b'sUm6qW2ziufZxe3knjBT8bxUrp4f8bxwSskRXqiCF4oB4zZKN464BSvcglXj7nj6dMV1xo14Rio8I8ff8fLF+TpGvKIVXtEqj0m0c8VkhcdkFT+wx7nbeYSfqOAnPrEw'
        b'dLd9bEu5++JXVW6TOjZIN6h4PuTM069rWuc0zZmX/4hXhMIrQuXBx6Ot4oeM8OMV/HhUhJvtE76rvaWY/Tiecvcea4SYi2ZIS1xT3IhVIPq/KiSi36TPZCQk7V5I2t3M'
        b'Ya9F4sxRTx85u8ek22TEN07hG6f0nDpszlNFRPVn9GWMRKTci0gZTls0nL9EmbZ02GcZuiezVJh7jbp7ozle1VmldJ8iNlWFRfcHXw6+HT88N1eZmDfsPU9sKhEqzD0+'
        b'0nRPuMIzXOUdpvIN6DHsNhwOm6H0TUR9pwoIHwlIUAQkjATMuT3/zuJXF+NvRm9ocluaKidN01xCn+3f6T/iMaXXRuXu+cTG2NZSzPzOnrJ2UYVP6Y/ri7tt9H54+t2F'
        b'w5Pmi2eINzRlj9o6NpeKWdg8tUlSO2IXJNfHFik7PAFipDFtceIklZ3TPc+I3lyFZ4zSLoasyeQ3rBX8TKVr1rB91mMWZR/7WJ9y9iSxAUy5xbCT/4hTqMIpVOkUPvF1'
        b'NE0k7Ad2vnJrBaqrRkFb30jyleaN6qwsBzco7Hxlc9EBXbB36jCTmsnZ8pUDYQNCpf0MsZ7K3KrFqMlIEiELk1v12HTb9Fp2O/aKBorFRgrzRHyX28SVlMgSpMvvmfvg'
        b'c7MmMxn7nrk3/m3aZCqpoadqiMIt5J55KLo6Yu6uMEckAj9va99S1lTWUtVUJStW2vrjzqGtg5uaNslyRuz4Cjv+YybbxgMvZ2OpsSzxnr0vTtBrTbfqnjkOeBcbP93M'
        b'RIv7fYfIH79Zw0Td8zXFRO/QhAevJ3nOiFuowi1U5ez+hEXxwh6z0P0fRCTgJXpG/EIXliraYmEwNepitDDAYDTYf5EL674zAx01QefEqqc1owlvYiOd1oAmvPVfgek9'
        b'd1cgsK/0/8bvB7R18Amu6St02IOtg9ir9+ct1NM5ixkMxgzGUwofvyPHFwlQwFZIuX4UNWCcwGLxWfc5Gi+NsUD6IjY19j+tAWAPOsSba6yDxKXEQG0bNFbbBpnEOoht'
        b'gxQJzGXl2URYqS2D7FwdO1+lnus4V5I8vXE2QHaCHrEMPnNV1/lJcIlBUUZ51epohvGGQWJSE6hNTFpHlDFznObK+AjRGrX1S+eVALURrEhQSSwxhdjoyCPZq7EVZczE'
        b'+N9Y67D9kpTqp6nOj0eiQImhR1MPbUajq8Q2S9SUStq0RVvSeIlVxSXh0bxCgZCYkugGC0uqhSWiElLWrzvMkA9WGyYnAg4+z8KIiiMVa+xjGuseNrhNNDj9J/PSs3j2'
        b'blm1URRR018SIVYzOwjuy4RnXZEoMudXPGb28w2RaIQEVhLL6rssV9eIk4KtGrDeZkV2zjh7znrYZYh4b/ESYqowLXbFXjbwMLiFPW0Ou8HrRIVnNcOYsqYKVnPMC0xe'
        b'melKhzc8qF+dw61ezXuFzsa5waR2FqYvnfBygj+QY1G5Hh7IwZrOTHjMPQN7cKTPf8aLf7wqkpXHhafBfiCjFYK7gAxehmiSg1OpVCaViaSeXhpHxoX6kTJnflRgGlJQ'
        b'omI4p9K6RJV0ei653eebTz2gbmdxC7asqPM7pEffTj4+ndz1qF3JuMfkGRryCpyYfoa01ckBbisPZ1PpS6kwKgycBBdqE9FVY9ALzuia1WB9IByckpYJm7FJCYmHqWpj'
        b'HclYmz4nJS0gjcZNhv3wADdNlEdcheFNeI2ha19aNflXXZ9MQaMagh4iMcSL+AOCq6BjYoqq3TNoe8txXwsamAaeKRszt1wEW2pxAENwkLNu3eWwiTZvqY1bvlpIGySI'
        b'3TLcZKge9uVzMbD9G/YsqiBgQ4hGczt9Bd2LO13mU5epXjZr+pb1kpjfLRW+j0FO8B2+HjHjuMJdYDc4i8VlcBCrc+HeaKK3NQJHC5C4R4GjmUSdu4VOdwA65k71N0Ci'
        b'rQvW5sIzoJVcngP64S7YiKGjA7AyN9qDGFRWgO5CLN6i2dOIZnCjPsWewgA9cCuQ013SDftX6sLfB/oTi0wdh45uPgpPetCpBUJ4atHfckF5hiicKXJB+97h1rv7ct+q'
        b'VE63vvnKndWua+b6ZFo1R+jZsEe9G21ftZ3He+foHI++Pbl3/TynpPyLueF7oyP/Yne87hLp+sHe8oZTUd9Nfdr+Y1TzCHS7fcfkbTPR22vjHi5YO3TM9Y8PvqHi62Y6'
        b'B7r2bNzC/FbxsTR50qE/Fm1983r0Q7PRHy2mLWT+4fsT+5aMjPb7/pj7utGjxDWvfcetyFDt3fmUP+fhzSuLN/sck7/ftuSvK5LuhsbsvMi1ZPe+8Wli/xszvvwhcMtl'
        b'83sPOHnFQQUr/2r40+nrgz+kdq+dfGDZnC8v3urOfZR8H5SmJgYmcENDLJbJz/xhZUVqdpT95+E8a7eghAGV7e/3rFi07rNXTjV21oR43Gg86vjw1QvV3BvbXe7Oqcuu'
        b'agyTt947V9q/9IOS1+Pea77G22dY/hf5mR/Facu+b5385sI73Jy/TI3qeuXEig+5q0vc+G2SgPsr+dlvBPKnrYwp2WlW/Pjnrtlss3awo2vzUcDI9L/NMZi/5tYnVcd3'
        b'JvaA3p7wdnsTh7Z/D856fU33o/tv/ejwj+W/CwvffSd3aM20jiDB0ytftcfrP1y4orTcsPGdTNuM966s3hPn/ObV5VVLPru66lGOQwPnzjWfv3ZQ2SWXfzx1fO0Fr8uv'
        b'/z7z4fnzdWunrd5WNv/f22IK7Sal7Xi9WPha864gpePHF7ee2Jkzubq9+0vHHxZaXd9V93ALJ21H68fRN3x/SmjK38AQ7Qn8aN9Pjz7zLzPtn/f9X83e6672+1s735ao'
        b'WCzgkRLiWAdaQbMmd1FbLB11fKUOnqcjqSPnanVlDu5EsbEIbAP94/3q7GEz0XkyaJ+9QnADSHCskQbOqcLSI9SP1FoEd4IG4hZ8IkytSgM7wFbyWu5G0IXd8aAM7tOo'
        b'OcUlRA8CTxcGE695WyB/TmrrCA9aazS0ZAGiRilw3xrQzqLYKThuRpaqVn2g/06lEwt7eg7sDPTD0O9tLCYVTCp3hWcWkOyqaSt8NdlV2yyJ6gNshbuBjE6DehZ006lQ'
        b'SR7UpulEUWfOBof8UXNSoRRcwt58hi5MIIb9caQz56OXtunktQINsDsQbrMjOqAKMLSa6A+z0fbQMV6DaMWl1UQHY2E31uYBeYZaPVwDW82msBbDW1BC1FjF9lBGFEDw'
        b'QOaqjYiGo+3KX59yAm1scNQXdpF2CCPBFfx+Zka2HqXvzATXwS026JhNZwnYhrrqKCmjGA6M11eBE+AI8e6e7m6v1leBY/BQJtyjo7CC55bRrb1UB2+Qp8aUVU6gA+ur'
        b'loDubzBEoQiehf3j9FWIuIeji1p11Ta4nY72PzelDCuN+LAVHtNqjdKgnO/2f68T+mWxAPfVr2uKNDm9dN2j7jtNDLbSuUmURa8zaWVRRQGDsnfUemYuH7ELVtgFE+VG'
        b'4u3lCu8spWP2sHX2QzsXlYt7xyLporbFTcmjNm4yfTlrxCZAYRMw6uInn6J0CRMnY9yyUlSEVbDCKljl4om9NduWiJNVVg6SpI40aVpbhtLKl5Q9XemYMGydgB0+fWVJ'
        b'92z48rlqh09ZaFuM3E7hFCJOxH6ffp/bOT504pFwvDlK17nD9nNVjm4dflI/2QKlY5A4EYnFTq4d/lJ/WZHS0U+cqPLy6UrpTGnKFM/8yMUDVW7nLKlp3ohVTvPktb21'
        b'3ZsU3lOV7vESfRXPS6KncvdGv+xcZOzmTaM8T9lMeV7vvO6lCq84JW+q5jY+4B5wde9YIV0h95a7Kl2jJKzPndxGfcN6w8+aSbkStqTsoZOHysO7y6/TT55zIliS+JGj'
        b'i07DHto5kU9PVzpmDFtn6Ejkz2ibfourrKu/PGkgSeGa0GSM9VN2Ek5L/LM6KXefEfdQhXuo0j1czBYvaDJ9aGWrsnZsyW7KlqXIi+9Zh49aY5ncOvCxK2XvLDZ+4kQ5'
        b'ubVNQv1obUeeSpCtlrvfsw5QobsJKnsHSbLUSJansPdDZ3b2kvDmtSpnnoShcnaRpsr1Fc5B6Dd6FScKLpLNkbvLVw/MEKcqrKfhq5lNmTLve9a+msKTcI5c9DurKUsW'
        b'ITdSeIb3Jis8Y+9Zx6GrI9beCmtvGWqkP34mrSlNUnPP2osW/Fcz0Nx434b/A0GmB1426YGstwKN0uPU/ri2tOT+tT6lgwr3ckT1565TXPKzsvuY/G5mgJ9EByPUXhEO'
        b'7/0Xlt8LkPzuh8V3+vAiLr6ARVJ3ko9bjT9TqD9BXMc9QwSqjegQb6gjrrOQuM5U50GjRXYKC+0RJloBXf/lCujr/6SVzscyoWmDPUhMyAsGJ9HPaMD86OeegykexEuk'
        b'XUBJVWpXVRK7hEV2dCs1JztqSkgoFqFXCWqwQ6SoRlheWaatgkYJHHPvnIiNTN//j6GSnCzikGKPNk7ZrwZL0tJPQjEt/4Dt8Goy4eMD14DL41KVwT1TWAsQx9NMpyTr'
        b'C3Adh7kJd6cwN8CeOcTxayZ67tAzqdCcwGXWjNWwu1x4N4MpwmAPBZ7ulz7BoeJnXjMHFsBlLLTS5xdDK/80rAmtzCGhlcDy7U+hmJNr9bb5Xfu3z5lafxvJEWyVtsj7'
        b'a968bQ5Mayanc4Lf3lkdbSpztksxLV0alM5JN4+1HXr1gfEV9x38Bpsk5j8DCuJF5j6VS9gZxXptt0+8Zv4qR9TJTIxhlcVQ2+7bGzX8wNcjzFZiBdhKeM8wcFnDem5j'
        b'ky0/eBqo18n2xIGNCeAoc5MXn3AgRkhCP4N4z27+xLAODg6ypCPSd5qB/TRPBW4idnEcT8WFLYRVZISDLq299zg8Aq4z8qB0yUtOqPPsjm9aS1aUds93mbDnj79Np4On'
        b'6PiMGcX/XXyGnZcsV2nnhzccJ0ntu1ZeKh9/cZLE8V1rr4c2LqN27jJfeeKIXYjCLmTUM6TXXukZI+GofIJHfKIVPtFKn1j8sALRcCsHhZW3yhu/bN+UpfL0x6r1E/Ej'
        b'nrGI/Cs9p6LNapHCnEdyj75nztcJtDPTCbTQkr3/krCLzJ6l2jS5tsfk2gEd1umS66oiLbl+/KLk+kfceMZ9g/Xl1VhJ+H+MBI5JcrlRgrBoefkaNdigOtPBOBhDRIwT'
        b'ac1exTqi+itfVV1RgpWTJcXuWkKt/qSJCHvo8vPSVj5LGtlZtUGYgnUuxVn88GLV+h3Tipl8Yx2/40I7Trk/OFz+J98ZDFECeo+jbKZByjG6/DZJ6Ir812dIMhzcA7jy'
        b'FA83VmKEf0a8JHRHasu+rYzTfodDW10mld2lrD7JYFGFd/VjPCP4bNo/pdkSiS3q+LBFsAGTkvBEQkn0ckGnGg0MdCVrHT7q+UQeXOXGMS6HZ58JD+NwfL/BKkhwFAzA'
        b'o/ASJh99cG8grAe7QX8qVmbu80/NXK1+JR2cNQC9i+G2/5CQ21xAD5tmZYu06Olay/CEB8jaj6DX/uPpJQzK2lZrzvShcYRpZKrbPtq1/sCWr7T1Hzb3fxZf3dHg+Svu'
        b'GXx1d/ygBzpITXTw1auK0SpyemEsYbbwYwYOZFpWVFq2DM8roRivfAFL3TrhHxhY45aVlZucJcTQOHzL3wIZPAYZRcAiSFw4CdEl8VjE7EJ4N0IRyAcRJGCH/1ux0IGa'
        b'gCL8LMe5Vl99wOClouUaRGFDrvlXthhR2LNzrYIb/JTpwi1iPKbwEeMJhzwmF57Ea+CEUzGccDqD4AmrgYExeq9ddP2spxwzbsQT3gSs3o+51lJPBdf1KZPLdcNFuj3G'
        b'v75yJZWiG98wOTR2MbqBfn1lTbdGpOD6P2Xac52fUOiA7wc8xqdfReD787vDr3mOunl2W/clPmExTKM/mp6kipv+lLWRwXV+SuHjE3L8Wg/dfMzGP7/ayMKvFnWz+nKu'
        b'WV9bPhwxS8FNecrMJq/g47fkiOtKZTwm179aTN7x7Lbqzu3zHfaNfTVJwU19yrTl+n1HoQN+Ng09i35+FY+fzFFw3b9lGnED8B2Pr/EvOsgWezGBbUBSq4EoTtULhFfw'
        b'z4zsQCbl66O3BgzBm7UYlQieN61GVOLg1CrYFmIOdsF+OGgTOQVsKYI9+jGIXjSBgxzQgIjINjcuEMOdQAbOgeakJHDcGDu0M5zgLcTx3eICaQy8DPaDiwLEZ3bncjFe'
        b'xHbYMzUO3AK9KeDWLPTUAbhnHejHyqegjeBEBrgQtxHehF0GsBecQf9dnwxOgRPwdNnqMG8oDYVbYGclOAZ3wG54EbZtnAoawWnYAPrsZq2Oy7YFjZ5wS+KmFeFwH7wJ'
        b'+svj4K6VsxzdBI7JMel6C8M2BGWDEwudA0EzvBIHrsEucAmIK8EZ2ISKuZoCrkav8oMHwpbBvVx4uhj2WiEOVgYOwuPov0F4pCARts4OXwH2FcHz+uAYuAp3VYE+2ASP'
        b'Yf/s3rWr4ElwaxMYhC25oMkBHl+Zj9ivk5E28EIKGAwBe9G3N4H9FkmgJwds90lHDbgKW6NAzyZ4dg6QMuBp0Aq3wUOgHf09sBwxeK3g+FpXljE4BC7DjrAAeAJeXR5l'
        b'FAevgN1FzmDLrFVgRzGOMMoEN/hFyVVuyXB/ObwF29Lg4YX24HxdAhwAF9Ew9U7VB5I5wTx+HvryRnAY7DSalAsv2cNOeBzjs2biBJMLUHccBi0BsD8q3nuql7UVvDgP'
        b'XWjf4JPvD6XwjLkV3A3F4EquCF1tMjXygEPojTOwD/SgBvVSsCW8JBZKF4O2MHDDEnaYFmaC/WU18XDLXNjiChqXTeHAITDgbAUGKsCQE9hVhl4/Vw0boCTUGR4v9pi3'
        b'aGowbEYzYQCcFgnQpDsCW3NNHBavr4zdAC87L3EBrVnguEM+7EE91ALlHPQxl9GMaoXHp8O9HLB7JrweggbyCDgbjb7yHGpfP9i+AI3BgcBpaELsqQMX7ZzgHtRDg1Bm'
        b'+goL3oANs7zAofjavXjWn4YHPcDRuQmIx24LMQE34CWbjdPR+HbNBFtcQTuUBJpEQMTOoy8+xpoJThcJPPlAvJwNGnmbg8GpqNr1y83gYTQZj0M56tm91QXzwU2bBaB1'
        b'OmjFQQZguwC2+8EW/0lwAF4H/SzQawgPOcGrAr1qeBRczlu4dhps25RTAc7CNtQRN33RV6AZAs9XpseiIo45gza4dfYCVPbBBaAlEkjA7kK09LYyozPhQdAbiJ65COXg'
        b'zKb8TVbmCzYXRswqg+0W6yIs4Hn0qY1oKm9Hq2LbZIxnOsstw2vdJDTZDgApPBeKJvlZNDkHYL0AHqzAGVN5M+EgaDCAp+LhwQ2gozY9oRye94G7fZFkOLQxMmgz2LXU'
        b'MAcM2LtiVFzYZRHFroJDBfAiE4rrbAUz4Q5wyQjsfSUFSOBW51lg/0LsUVpsBjqAPDsnL6zIcpID7E6YZWRtGRSi5xSeh5bQ0QzsItuD3jhjD+oRTdkigKenoHEcBNvg'
        b'ThY8mAWaYB8PtmfBPQvgGXCJbQGvWKAVsMcOHEdfginTzmVhuHORrHUOXF5b5wD2uaIqz6NJJa9D82H3egsO5n5K4SF4bWOYNWhG3bgDDU8volxXOGWmabDDAQltskXz'
        b'4Fm08HbCfrcl4GZmOhgCXYZe4KAI0YTTYFd0Cby0CjYsADeDHLHefnE26HdCc+4s3DcXHExPs1i8FoegIOIkh8fywVa0gobQl20Ng2etfHK8bLLBVtTnVxbCUxWo9+TZ'
        b'4CIfDugBSaEX6EybWqtEE9IBHE9B83EqOIDnI2r0NX9wuTYati/+/8r7Eqi4riPt13SzNPu+i02A2JFAIBC7EPsqJHax02xCgBqQEBISCLHvi9hB7KvYEWIVdpWdxXYy'
        b'0mgS2ziJPZOZsRNPPMhWrJk4E//1GiWe+CQzyTn/OfnP+ZHO7df9bt93b92qr766/W49HjU6jHfzUmD4igxZZbdDuBVMKiYHwYw7NOI6SWsHu3VIjx6L9m6swGIAVMeT'
        b'sVYZ4a6/u7sb9gTCWLqiNFaRvk6QRj2Cu0ehz+AqKXC3mDvsXGccbQKw41KRJU3bKkwS3ayHLfZ+bbK4/tT4hDyCjlEr7M8hWW+z+1HqSVNn2RV17LzoQ6C4Z6kRXZSQ'
        b'CMMh1MNxbMU1M7KMNg8juxJsVOXD5n/XV7KOrnAt6sfDa1hpzb8Na3kivOyUvw69BJSTXsGOpYZpsBR646Y6N9EPGjSgIoMGtkcNTBIsVTq6k/b2SF6GJphKgg45mt8Z'
        b'AznocMJefxguoioV5DxWtWAN7uMQOaUpKFcQw0o3wpAJNUl45IRbmqakDCuwZYePVa/hWJ7adV5WLpbDPTLYauxUIFmN0wgncQdWw2k2R5WwPvZIFulaJS57wjhJfefi'
        b'MXJNC7EluqS+I5fdsDWZHFi3OcxcI4totKHZGPWyI5CrI60kx3nx5CUHbDPLwemyM/Kl1MdKKCdNHoXVEwZm6SmwSnjzSFYVO3ALK2Wx1heG7C6QSsDIdfaOa2wxg4cw'
        b'AnPQUoqjkjrGJOdtHPeNtYXHOCDta0FjriaEHCav3X8WVv0yI2guV+FOYSzNaC/5w/uwXYoNV6EnQVKAXW4ZfjYij94SVETuprqYQKGV6nS5+mnEYDf0X4J6sauaMEDa'
        b'TRIk7YahuBzq5R7e55rkB/piXZ4ctgmiJY8k4rw2dLPKZUsGPeqrpIMdxe+yQNtOfmCaRdo8Eb/YwUVLXOf46CXDsCT2RkhzYJndFNVMNtMDrUWwwhDaGqth+QkScI/u'
        b'DVyQhC0YF/iZQZ83zKmQM+jTourN8jggeVmXXaXqUyBb7LEzx8eRNv7Qf+4GdupCY6DeKfIDj6RJNo+xQTIcZpJZc0nhFFxkudBgHi7idkI0oQWLvw8IBoiA5DtCv4qn'
        b'ZYQyLsZCW/JZuOMDW4o47Hc7ngQzfOqGCjSeD46FGRNcu33EO5lgY5bmY+4ySWUO+uOvc7DL1x42Lxy/Ie+NFdAPPe5p5Jjv0CSPaiqRtKtxnAt7StgeqaGoTX6vXhVa'
        b'E4JTLpDt7tqfO51LVtwRAx02UBmsSoB0x1YVp3PhgSdZYG0OdJriHW8OlouHw1b6Gbjnmw2r7qGwDbVnnL19bmljL5kAAeMEXbOGuUxeYBSXJWCYrLpOnWxmhcTVggN2'
        b'sAuNWmSqAyawXYbrV9xJb3vI1zVjl+sVHPUiWClPP1cC1X75ZAPDZdBVpkaa9TD9Os5kamIPoeAIYUW9CzZFKzkiqXwrjvsRNyKlnjA4RX0YZG9+9zxV4qdIfvGsNqye'
        b'J018BGvXT5Lh7+KsNzaS6KrI690/pcdyMiE0ZhgcY7UR21Q9RIAwSt0sh6Fs6EpVKr0aggN0lTWyrG5oz6bezBAnqBSD5mISfqPWDRpeP7nQOfKchTEwYoNDOK4ZJnee'
        b'PMVUjjqOCPBeAM3xJG5fhMFk6uKCOyyQHdc6w11kDX0XuyKpiZrErKusG8KKy1q4WkAYs4JVxr5x0rikc8L33BEafVVxmxh7Cz9zlTSbhvAHEmGJG5zL2Ewkws3JEh4d'
        b'h6WrMsecJYXEYXt8o7D9DA0Fhr1oknfpyqtCEtI6C0IxRlBtj5UnUmCQLn0PBwiAlwpuuMnqBcEuLqbifaq3QBjSfVsfyi2jaMY3eE4EiF2waeHogXMJxNPu4aaAWGYz'
        b'ebJZ8tMPkbCt8rY1diqT7taeSYDhQOyK8CQH2yrwhN5IC2Ie47B9ms1XTZxkGHYUyMQHYUQRZ/yh+UQJtsuH6GdeJsCrkCQrGbohnQRLJqfPBmu6yZGSPYB78tZHeCS3'
        b'QWllZ1zTN5Xi+uIdQxJluQkp/wShwDzJZhrmL2JlAnR6AcGTO7lCQijiCbiVRAMdcrlCqHUPpsiljBPbX6KZ4oRbR0GDSR656n54EIaVcTh68TTUB1uFkOgqoc47RyfM'
        b'7xzLZOoTbsFkqjneSYNylRsG2E2I0xaP60LSnq5zOJeMtdbHoVuMVO1+MNZ4kYLtEbTPZyZQXNJK8F2npUkiXkvGDhesgfv5TiT6aTuodie9Gce2E7GqGY7OYakwnowb'
        b'+RcJm4ddFKRN7E+patmbE7CvyWKdytnQY+QS90xgIJJabZcj5Xp8GeojoshKti7CsClMqqbjch77wHs2+1Ei2cJEvECNIKgd5m1gUYaEWY/dmVCnDysJBYkaHjCbS5Xm'
        b'oTeDQKKXm0O9Kj9PKr9mDy1usHuMnO4m3r2tio+ZXOy3xC4lGC3eZxG3SoNlVxFYkSfSyl3SyhKcE+D0dSkiPpUqN0iAFaZHiOSu6R5Xxg5FYpPREaX+0Hpb3+RGMVSn'
        b'aIYnyUaQGx9j/0GlA8F/FwEJfc2NJU43FeXgQQlN7Bbej/KQIX+5DnsKyTiBvTnkb6fEsbwY710QwO6NPDrVn5pAfGZBRCGAKMQ27GaT+q+mamKVUB8nzEgrRsl45i7k'
        b'YdtNA4KHAZbxZlEHahNPX9aUoW+0EXR0kTQaQmKJ6s2WnS+Lzioxkg1FIq1jOGFE6D11kShGg3uJPAm4AVj7bYWNvAJ3ZVhXKCI7qRAStWiNCbXnG+NSaijega7zVGUd'
        b'7krirJwAa89ZsvkM70BNAfQpULhyF4ZKcCWJlHXJVtYykDCqN1vRN+e6OwVQo0fIUBcJcRp0zHgkz3vHiXO2aqhCZ56Bvg9Z64MjuOlH4NVEMcoa+eWtPDavLLZfMcHJ'
        b'oxTjzuLdMugzsyYM3JCki1XipL2fwL7E8GIG2XkF2UNlMZlCnzS0n8DmS/bYH2xC1rCqolSYShi4g7NxOJtAhjNuSEo4cIqIyyN7qMGNgjwYK6JAvJYCZo3jqoSZ3R4E'
        b'9KsuR6nbrVnQRMxBHKcjyWXWkq52uF/Ch5FaWMWDTlwU0HUHSd/6mKPX3AriCtXDaY6XjSzIYAahLb0IBtxLoP4o1olfxIYc6HWluitEsubI7OqiyFM0ED0ZUA2Wh/uB'
        b'prfDSEcf4EJpbC4xxu7z7j6n2PhszhkmvIQWF+ERqVVLCCzfyFbNIAjqVSAVX7PGsXM3/bDD14K0YkHDCCtsg3MiCZ+qsd5cQnQzWk6BS1CAODxWYDi2DNZzoEd0q5t+'
        b'AJsdoImLffaHm6Yl8bGovgyJdyfIUkxBkuF4Mth7zEB0oyUsn8TpIGuJDA+G40EfO0P5YeKQZpq0NvZXFQ4pzCLDCWSw30LpcKv45jWKoBqsOBcTRXnQhsigWot9uQwT'
        b'dYQEMUgOqYnsos9TlkS+eEtaP54PXS4RCikq5JjabEgTRklI91jSbop3A3xDoDrHXd2ckOYRTmiVkncagaEARa94Au9WGEjFFqIsZMB435FddKHgu63EptgbZtVZolcG'
        b'E4IUrJGBEWEKWU0H7LlDefQ5vBdK00jnyRarfOhwHKYYgteaSGVicf3slsZBuzhjkkrFEQoJli1iqd0WJoyuWSUgRF0kD9xB00wxTvZNqLYh79p2AVpNyS2tkDLE0VS0'
        b'mRLCzUO7MwVKVUVJIfA4iIQ2Tj6igXRqRZeCpkoKzGqdzW9CjT3xty0CiSWCpWFYMiQ+PA29TgKnq1xskRQoYI//JZhxxA2hpT5uJuJcXIAazEjeLBaECJMIQNtgnM8u'
        b'HECPrhZWkGDnCIsqCBwnL8ZRW40kz65Y1Ryy103qQqsDDXXSTVs6WhaH0pJFkVcfFyvtKJQpJ6nMI8Honh00cnEp1iLMDqtiCNNGXHDJlGxmyt4S2P2eM9DqQnSohcZT'
        b'LtQo5pFfai2kMYzD7tl44pMdUG8BQ5L4IBtb/eGeBw5HUlTVSOHLrqQaNiQbppl76+ADKbiXDPeEpBq75vLFOJMmFOIku/ZQJkfdrXOMiqEYcp6QuM0eV7z9biplpMND'
        b'MzlYl8f7/mRTd07hvG0AmfUMVCO7uFOnQPq3BhXaMJBEEABdHv5xofHC6GLojdMgSlRLfnxTwwk7hbb2BBMrV7mEDhPwwFod9oqzcO4UBQStFirYp8ECOfm7muO3yUYf'
        b'OhBfrGNXpMxDM8ifwiNb6C8inaqBR/FQk0cufBxmz5L1zgfdhvkkivuGaFbnA0+LlmB2uORl7sdnUkA1AS2nNHRuWRLzXAtlYwlsy4BtHD1OxR7uGqhDl6DQqkiTKNec'
        b'O24kymGFHO5wYCjxdnyqejGbzrQYxrS/vTRDCLrgbuCpcBUfqEtoX8ORdDKNilTC5OXweKwPVFX3otBlD7qFJMxqGVXxuKTgCEKdVnttUpwuWNTCyROaQYausHqDAoKa'
        b'GM0w6zQvSXJpG+eiRGs0K2H6dJE+6HAkeexIU/9X8giQRsmb7GbhejGsm8MiNLhakmFM4kAevWm5ehL6rNi9rNDKKuoYLFvAwvF8YvtDp3ElPZ5kXB0SpcFSTSSInojm'
        b'EN/bIZOu0CXrWfYjDzfE08UpS2B/ohlTiYJpI0LUZuj3FAYTzRzKZB9e5MkC6zJUlOUSu9fxJJ4wpqXArmwF41Spsrc0zF5OIAxuPFwIKEwj/W+9ZELdIleGI7cIBzZ1'
        b'yQwGKciFqZBEJgdrzuQS4Awknskkn7CqkYUDAupjexG54Ur6DpFyHExLh8Xc8FO4pqEIj4/GkSb0qOKElw0rEwuc0RDgZjYpDUvzZyl02BHibqK4qyL26pzA9rACgrRG'
        b'FRxVphCs4wbxqHL2DsF2WPOAGaUwMw97Y3K8w3gvVgpH/PJJ7P1mx4r1zLPVw/2UlXBY5XbxaTmoPiMWSjo/S9pXB5O3CAhGiqP8oSGeYPaOJWyoCsgsd8gu1suiL5Of'
        b'zINmLi7T+wdE8jZTrhLYDrjdjMGJWGtCpT6cM4ftM4kwr28SQKDQwU4xTcNjwrVeAod5JRrGLu7dCg+mRscdoP2yml8YXXtLh+Sx7Q0bXoTANUniRh5FMOFc/GM2Augx'
        b'o/B28Dw2/CG6jaarN0H3SX02wI2NkOHAQ2WsDYVFCWuYj5dQhxkkCFxzID1YdI7CXai3yXYmDW0TLZvMGlkTirHLdL1KVlBFoEYqWg1LFBvg42th1ubs3dy44+4FM7rQ'
        b'q6CrTcJvhLV0MtUxD1cGZrQIV2ZNoNcZyw0J61bgQQzej4R+u1iCnZoAGEiPJY+wGMVyk1EciRUeE+dmuWKXLU6UYJ0NrBy9gJV5x2E85wx5hXEa8RSR1gFfAhzYDMZ6'
        b'q1jyG/0WZMt3rQ2js3DilFqcEB+Hkrp1keeoOqkqBfdz8mBJlM5pFJdCJckK9grCKG5vI31phPFSGjT5Km2ctIV7xeRNukNzSJsoZum2ksuDKmmD0zjvnI09geqXYQdm'
        b'irHfGba8hNhNsmvBpSg92LvAOOFdOSnc41Ivq0PUYFOcXRsZc4bJTHV/6PLR0XammKue3CQxExucdyEk3yG1WCRLeES6sHuF4s8HKiT43tQ01noysswIWJvELnplXpGF'
        b'h/E4mRMWmp2RSEx1RZ660UdNzUnjShA0pEF3lKUGUIhxB5tyZFPwwQVoUfFMTriBQ4EhR05g23FcPpJ1EZvtxVjmSjhURXH0fdwJLrlJEmhIVSTvNYKP9Xgm0KUSgdVp'
        b'MX6JZ0J8ycob3fBeoVM6bhoRJi3QtDZQcCiRRADxQCZWVwQyLGx3kjB70k7CMj40Mifb7cGx62RyzbBkRvFPg5IkOcjZghg1NgdLOu6GX6H5aULiB618WFd2sWHvRL2u'
        b'clvhGNlXL0HOYyusTYKhU5dhPS9QRGio6UGpP1JtCm7XuWIaOI1tngpCGFeVyDlGoDvIPlKKILHrBCfwQgAbPKXhRhquypFlPaShj1i5yGOrbtwRHul4H7nvRmLwD0pJ'
        b'2PdOXuBHwoIj9sWQevcRcm/JsBE5zOlGkrQprIZmdaw678syHxVqbD5JHybscN7HAonOBB4hATUYwX0bNrHUPVfoVyPJ9BeSz5kSwHKMLil6n1jESR0Y0yJylwp1tkR8'
        b'3QgQ9SPNdQgo2rOwkg/LAuFtcluVsBbrSE5lVcCieINkUbg9zMieIjG0YK9mEsloUxlHM9VwQcqs1Mv1igYMnoLF4JukUxPk98axVwvXiwJxRpmITgu50O0scgal0t5C'
        b'msIhaqTdyKkIxl14J3Dewxim3aVxoAgfKGYkaMKkkuIV6FDDxqBMaqgCOq0k7UJoOolnkFg2eAYhBZ6nInJwwYigYYasaCDZCPd8Cby6YTDAy40h06gnuyTuTdDVDusy'
        b'GVjjQL6ZFLTBG5a0+RzCgkdJFwn2JmhKNtjsPkpq0eTCm0ihpmFYCu5mQbUzzliTD6i9dRXanS4iu1I+ysBqoosOocoWVGcfI2ub0oQRazL1XjKKJYqqB5L5Wg64rQHd'
        b'F5yCCvzIiU7DNM7z6Ct3YNVA1ZlCjjGY9IJZcV0ypgHYM1HTIjbbZIGtN7GVFU/dNVjhFpi60KdtrjB6LBo3yVtSSGvsaoxDTtAjiCHdqcUuIfmm3ZJ4XDzpGgmVuUUE'
        b'jp02jCNMppSopqaS5HOzcBuaUmHpCvHnNmJwTSSx5dOErVXGzhQSbmKN8HRQhhvhQC3W37AmAa/Ickj7ZmVZbkyT2ZteWFIGG2H0dgz6gilCvw+LBf64EC3yjGu47Rrv'
        b'Dt1mxIop/PVzw7VAYnCLMukniMr1xJJ17EmmEl8rN6IWloo5XPYn1hw2gDpPM0uunWxpF7ctCY57SEHXnXFNk9huDHZIZ3vDnDH2e9tCG5dc3LAcW8NNMZvCxZ0bmf7+'
        b'xAgqAyOdDbC6NJ8Y9i5OeZEKrMB9Pu44SuaS45nj4Mh53DIpg3IK/O6Z+irInMeudNHPa/Psav/tG9AJWwWiad+MoB6SpUyya0VEdSdg0l8de69HxLkei7Ol8d3DWVes'
        b'uE3B10NdcpC1F+F+JDGuh9YSWfl2mrDkL03G/4AqNtmRaKtzyRB2FXA4AaqIFCyRg2k+ga06kjTKCb41LtzMIg5YnVoCd93IMzfDMBdXNPnYH6Xpq0ka88BMXPEIbnhE'
        b'Qqu8pxTh5haW+xGnmWNRzQEX2Jxl97DluLwgHKrig8ycinKkcVcxuvQYwTwxc/fL4dBSgB125ymmZonoqnPWTVKQumOwpHQ6iAx5RAO2pGE95nquBU6bEHSxWcyqEnGr'
        b'RBqrfc6TcVSRLUwT8LRR1GJI4u7Ww0FZaW6GBjbE5WQnJNljX5A8x0edvjcPbRLQrqRBRtcBj3JkAyxtcV2PXf4k510OO9rwiP0Jb0r3CEV9jakebsTgh06SLEZg4Yh1'
        b'HrQFHyWzaKbgp5DI+0maheoAfOgqQwR+m7jBgE+pBo7K3hKnEbT7Qp8K/yZZXDu9a4M9y7zk6zBkSDFlpbJTGDzUhAHFU26y1/BOIFbpJkni1AVoz4IhmCM1ao6IZZdM'
        b'caqYXfCimd8m/F0iL1GJ4zZYeyvJkFw10aAoqjsYSoO5E43rpTbEzWCC7KWDvHWtTGxqcRxZ5H1gvQmR0nFHGtteGXTqYbuAePfDK6Qt89c0Sa3myrDmNtQRlhP7uBMD'
        b'3Q7pxT8jrhSCndZ/MAJPdl2qJZp8MGFYjodBhIIxtpIBRBvfoNMDWplpfE0c13Iyprndw4VMeCDpn0yXWCeONCHmiOs6sIdTp3Jk2Ez9OFwE7E/AFXGu0M6DLk0C851r'
        b'2BsEo1w6nIQtAXmb6VuEjS1kS500E23SejgWSFg6R4JvxPabROO2XVWxzhG2rXHUOAQbctnfugLYhar0cBJNlSkhSp0sD2cF2qT0a9cNyMg3T4Tlk7aNq9hR39qPq2PX'
        b'UX1z7Df1IbpAhuFNqrCrmoUPZbHPxRAn5ChurLoIld646Qlz/BIClw7iP/cInMcY0vctCRjU9YduGQoRJo4rwIjXCei1J6ZQpXlBDaePnpSQwNpz3lgng3e8wykm3rYh'
        b'ilXjjMsKBfjQVjbIDkbtscPrtCcJZRX6eGT044T21aXJBorsftBNwoFNqDAgRZ/nEDG7ffUE6VpHBFTJiFRi8zJuJhF+710yJUAYwJp8EtwkCwMPjxP36MjIgjEn0md2'
        b'Eb4D6zVw1ZFCm7ZMqJWA0SwDmObBovtpXGcDdCw/R/i1FnyNXPpjewmi1mPQaIaVViSbRXUYLYNuJVLLWiP2B2XxmxKOmReo5U5Xeewi9iBxjaVAlSoOeRTxEaW/QwjR'
        b'BpMq2HtWo4S9t+I8Ca8PthKvmsCsNez4wpi5OPQaEr3qj4GZSxT1zMOYdRIRIPLcjqfzT8JW4LErOGoCPYEwaXncB1fFyaV0BxhSVDuIKyfIwc2wJtJ7XvmsPZHsORvc'
        b'izQmYOuOSJZPKrugHUu6U4vlDsF0jZ6jbvqeZQxRzNpLSKR70VzscEtjN6PMpgNkkwFG+4rSATZT1CLKen+fiHBjoZ6tKF0tm6o2IsycK1qhKoPVuCArDtzNZzhODHZF'
        b'm4o+VsiPC8JmRv4awznOkKkMJIkakopi97nW8ay0GI431SZ2US1a0cJJDY+gAPHrVw4Xxuhyj6lborWudtiGjqAwMdsShmNH56INRE3lluIYNgSLw0gRw3FmsOUG1B5u'
        b'+23VyRctpvVnvcpAOAkzv29sXPkmNpiL65gynDA2T+a09+EjAgYJ9PuwIUTC+LZoSa3N9rroC5LmTkGWYgYE4aL1N/amgFdpeMn378J2UKB4AnvSkk3qtGh3KMhK7IkX'
        b'LcKFQ8PhGhz0WZhzfEXPJRRtfmWMxJgX6aLnq+SO6qUx5lzRx7rxXEYqW/SERavvuCQcJkDc1BJjjC+IUp/nGjjqMqHmYqHUlGirbPaqqq544WcEUZnyXU2d3837wFOx'
        b'Orrpl7vX4j/zedPR5NFG/GeB/yT7cXpyBZN9/DXG/V80/9nw88dazV2dR2Prioedvn7n6ysZ176P1r9oS/xFR9+Lt8tl32qVfbu28a2exrfvBr/VGfx24ztvDbzz9h2r'
        b't9qt3q5/8NZ+/pWdCyrfyfPWbEjo/kh/48tbUs9nbDvl8/RnQn+M7+sJPmxe+agsMU3wWqbfxSSVf/J6M7V9xsGcd/vZlsLJhIuvn337qxPBiS2/qhr+1W/+bdbZuFAJ'
        b'Jr974PlGas+JtC8qTU1vhSX+vbftJ9q/WNZ4wdj8fPez6qwAV4l3tC+mNna+3JJM7fr8E7vVAp+3bPRa1aPjlN26fAPvlGVPGX3/SjUN9Lzu1Ed9nbo/a2uParT7SeuP'
        b'X7ebSfyemcOHShl1Lxy7loK09NN7Wy1rqz31BT+ua1s9+T2dyoU4h2eZLyKrHJ5KL6QpPzv7i2T14n87d+1GSf0ppycd4cnXlj/VK93OsQ5efHpKvnc05cjHV7zaTm/4'
        b'7MpqfVVyN/qNzR+dD08NvT7w84O19eM/l38WtJut+V29H1xIySyetR91Vfp05mR+06efqhzxU9tsTpltiti78pmTz5zHgFvYs5bSj9Ve0/5VCT+jx/mS/Q+W4rxswzwq'
        b'vRzKPui93W/+8Tsb79o/SYYBpfVrr//C0uk70v/VMDGVMhQgY9t65oePcz6Z0tIY0OrfeP5uembJ99esrOwuZ6c+/O17Sz9sESZ8civmX1cjK4zN4gfG3rFY+Ed5wc/C'
        b'M3wGv8vbVXq7Z/hUeqS5j9ri8iPpa6qPDu5ezU6IVB34Rdnf/evPXjNye/nGPtdNOuSzZYenaa89/2HEo8IfZut9llGhOfZfrhlx4nMlIe8YrfW+r5V5S2OJ078kfrpo'
        b'RPIDa7mryRpfJuv/7DXOd2usX55XlH/2T7889qPtj2o/qy/6+Jb/+0nSRc+jD97bap77JHH002GrszHvSDn1/tK9rOqr3Nmvfqv22e8uvHzz659WJuHXi6ldC9/Zri45'
        b'eP/Xiit7b40tflExZfN4486Hv2MSeF+/N/jYXPrwIcZ95DybCAU4UBUjwp9m2HQV3V183uXw8VG3bb91d7GN8ws23asVH+pliMPs/PGToL55DFTG4bbXNZhJlBE6n5Xj'
        b'yxEnaFAQFsuSJ3/EZXRLeVIesHX4GOCVcA+ZpBDhq0rXcP3aFTkJRtOTCwt+2CdKEaZ+1rHwquyVYnykAPXQqCAlJ41LClfFGXN5njCcXO4w1rywZS/ZTuFH65+qC03U'
        b'MrmSeVHrITwJ2Dyue/ggjjHyZSsyh/UScPYqu29jSsw2DhcO2+ySg/FCaJK6Qh0spEHV/VGbROsPm8SHEvDYr1S0SfQozGn+9yRvf5zg7basOB9rQs0jvn2jrdT/Q8Xf'
        b'fCPq3/Z2Z/YpswYGBp7/w9+fvRv6z/8d3k4vlZSUm5+SnpQktJFkGNGt8jwew3z99de/LWcOojiMnNoBT5Kv8b6Ccqtdw7Uew4abvYXDdsMpIw79pdPn+m8vGy8JNwyX'
        b'izfOLZes2rx+9nvK6P/MLvgnmto9dj0pvQ79/OHAp5o2SxpPNZ2euIY+1Qh9EnHhSWTU04joZxrRP1E3GFbuyHuiaMxmeYrhHEgzyqqtXm1qtWcOJBgNt1qZ99QMnhwN'
        b'fKoWWCtNn2havKtx6qnGqVrZjwzt3zU8+9Tw7BMpPdGxy1NDFzr+UoLLd3kprcg/8pyh4qWxJP/4c4aKl8q6fM2XruJ0JM/jn3wpK8XXfM5Q8VJVka/7OVXWPTBltHRq'
        b'5V7yfDl83ecMW76MENPnmz1nqGgVvGBfDs5yGGnFl2L5Ynznl8w35ReHJZdOHohOHqSL0/F7fI2XYre4dEHmm/KFqGTrah5+gce+PzgjxejqPZHS/IivIPpaphhf6yXD'
        b'lv+9Kvv+4AK1rflSzIjv8muGCtH5A/bty0BOnDifzYr0J15+ffhyUCotGkKCJN/4JfNN+bmoHNb9QvT6aijs4YGngugLEeJs1W/K56KyJ/cL0eurL7CHBzmHV/CUYKt+'
        b'u3xVUfSBr2w0h2/wBcOWL4ViHnzNXzNUvDwjxiERMlR8KcHhH30pIcdOFxUHBqKWk8RocphvyldtsocHZ8VFVSIl+FYvmW+XXxyWh9XZwwNPuWOSvIMLHFMqIziHx2ZU'
        b'Rr36hI6fZ0vQDIkd+EuZ00cxf1TpW+XzYomzPCmx50FSQVJHxJ5IaX0Ro8goG9Z6faB2rJXzEwuXDa+nFu4bRU8tzv6DouGw4VNF4+FzzxSPPecy6mY/VzP83+oY/WV1'
        b'dP+nOjR69SOfK1C3/uPAu4jD4Qdw3lfWH5d9Yu37zMDvmbL/E1n/w73Fw166wU7MO04qITKvsoI5CH/yPz309f+jQrSn50/sef4LsVeEuKLC8vco/5/lzMvzHA5Hkd1l'
        b'9+eLvybLGTuJr3MlvFSY11VkvPS42dHexmKF/jSFS/8SLGj9fqiYl2L1jR8PNaVIZDCc2FHTjbNynKZPuS+M9TR/V2k484aMZMh/qj6+8++fjnPSxr86+K/B323NRfyd'
        b'it33jBtyhd8zCdD7T9Vwf6UfmU2eNumMqOzrPBc6n39Oe8LsjanymJjU/Pl/S+jT0RGuNaoLP7T6gcfC5j9mfbH9g+VJlAvp7lebP2Px/aHPYyzu2/9q32f4zNXIN374'
        b'5eUm7x/wenou9RXnZZsORBfVX3B4Lzxkfe3f1Xvfcn4SG7X55u/8ZWcTBndH50/n/tJl75NZvanTkj5JR4Rl8fmv8WXXnlbUcWM+AV+FMqeCE29IpfmXON1pUeH1fKSa'
        b'KXWlWebs9D8qR298R/VExnRas85PjLzqJT57crb6hutHSs5xq9laV9/c/u6Xf++unrbc91nGsTf7fzt48Uf/Hr6zs/Bmh4PqpZ/f/zgrLOvjtI//I8kjpDzs7eFyc31R'
        b'vg6VZHazLNaFhYnScFD4viHJyMCKGE6XwUNRwpcYHVgJCrPGZbYWuw1GCWojcIcLI1eg93DLbZ1oP0IDtLCbARtD2MVjyVvYw8grc/VOwvohXW4+ac0+9jFEEuugk5Hg'
        b'iUkdxcOcwim4jfXYYCvBcM4zZ2CCYutuaDrM2zJorWeJzWaw58umE2nkMHwbMWLew1gvymoSyf5i+SqNMMODZqgI5cBSuKeo5yehHjvYXTzWhxVwB9oYeaznhjpg7Qs2'
        b'wg7yyhLt8mF4GTZsMpoMKBflfOG5xhw2GhKATeYBPEb5dhZ2cGEr7lVqkgQlvB8UaAWrOBnqYM9hJLFdTIJd2j5MHF4FizgdZGdP3w46zKilIAbzhlwXqIYh0RUscZPk'
        b'TTUCQg4ryONONi5wT+CI0WHykwp8pIkN7EO6W7g0tK2ocxzYxvJrog3MuAibOMTuDg+xou6G3DrBgQfeh6l9cNoaGyytsYnNFi5feplDc7MJk6Kp4hKHH7NkE2cHY3My'
        b'1IYFhND4eYxOGQ/uQAtzmPGmD+bZuWKzhoVgYyDWcBgZczFsxQVNUVrlHOsjhX84zcdF4hYBYrBkCXdE5B16oBoHZXBFAR8WQh0+KsC1KzAJCxTCyDGM7lGepMxp0fQa'
        b'XYkT7R61ZFuTOM3mLOsTw1HYw87DlD6jfNgRJcFmE2CL6YpSYLskvGAfAO5xyTQI5s1octlsxqLs7mEB0GRL0UxLqLW5BOPnI3mT/f38MKdRB8xHyeASrnEYDk5oYxuD'
        b'k9akgKKTY9E+7AYNNjdOBlYz4jc5OI67IaL4ShwqjrEnrdlkNtBi8fu9n9rFPKh2UDl81t9IDnaRyOvtvdk068FiDN9UDBqw7cxhzu1hnM22DLS2CrG2MZHlMLJqXGlo'
        b'xzVR+wISV0cQzUmQDX2XTIi6rkJSG7Hn4pCTiUhO18Nw1dLfyoLNBNAYhtts8qJWNo14e9ihcbVhLTRZBooznCAmE4awB8awwdzjbxEV/c093P8lP8nuIP8z4ctf5zHH'
        b'fl+IApW3GTZQ+V0584UuI67ynpzqu3J6T+X0BkqeyZmV+77Hk64Jrgh+omQ47vQPPKsPeHIf8JQ+4Cl8yLN7yrP7kGdJx7//r/4hz+anPJOf8iwOxCTE1Q7EuHytn8oa'
        b'/lqaEdf/Kc+QvvtS4txpcR/i0f/ry5eHLwcZRaSdquVh//HiOh0p6nxBXJYa1Tzg0utX/yyjTh+Iq72nqFovTh+Jq/2m0IJVPxkJb20GteW9LbloxvG2YdCCwx5bctlj'
        b'G1lvNy66cqg8ZGMW+9xcQZ7wh+xTfcWLigtyBfu83OzCon1eenYalfkFgrx9bmGRcF889Tq7W5qXmp+fu8/NzivaF8+g0I9ehCl5mYJ98ey8guKifW5alnCfmy9M35fI'
        b'yM4tEtCbyykF+9zS7IJ98ZTCtOzsfW6WoISqUPPS2YXZeYVFKXlpgn2JguLU3Oy0fVmfwz3yISmX6MuyBUJBUVF2xvWkksu5+1LB+WmXfLOpk/xUe0dBHpulc18uuzA/'
        b'qSj7soAaulywz/MNP+u7L1eQIiwUJNEpNj/JvtLl/HTnU4fPK0xKz87MLtqXTElLExQUFe7LiQaWVJRPkWxe5j43JiR4X6YwKzujKEkgFOYL9+WK89KyUrLzBOlJgpK0'
        b'fX5SUqGARJWUtC+fl5+Un5pRXJgmegjuPv/3b2g4xXlsGs9veK5oepL/wj8Dg28pLLvuWxglUlj6I5qnwOHkirNs7k+VL0TlX03z9CS8bJjXbWS8nLm/kcqgKRakZdns'
        b'KyYlvTp+Fer/RvvVe4OClLRLbDJVNrkBe06QHmouJdojvi+ZlJSSm5uUdDgE0Vbyr9jPJXLz01JyC4U/Y4OAqyyDFW0/F22TP1xRcKW5Ks4VuAtL6QyHHXcIFaTjHM5z'
        b'MR6HdyDLyMiVS37OKz7NUT0oKCYiovSulM5TKZ2ewHeljj2VOvbEyv11UzR7ZhX4npTi+9LqTzTsn0mffMI7+T6j2Kr5I0ZbdLn/A1Jzh/w='
    ))))
