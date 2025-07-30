
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
        b'eJy0fQdcW8cZ+HtPAwFCYJbxljcCITB4rwQPNgIzPPCQBE+AbIGwhrExdmxjW2CM8Yz3SrxHPPBKHNvJXZqkaZI2HWmjpm3SpG1W0ybpdNvk/929JyEBJiT//x9+HO/u'
        b'vXffje++dd997wPG74eDv8fhzzEdEp4pY6qYMpZneW4zU8aZJculvKSJtY3gpWZZE7NC7tAt5sxyXtbEbmLNQWauiWUZXl7MBFdpgh4uDymeW5iurrHxLqtZbatUO6vN'
        b'6sI1zmpbrTrDUus0V1Sr60wVK0xVZl1ISEm1xeF9ljdXWmrNDnWlq7bCabHVOtSmWl5dYTU5HFDqtKnrbfYV6nqLs1pNQOhCKsaK7U+Av3j4CyV9aIDEzbhZN+eWuKVu'
        b'mVvuDnIr3MHuEHeoW+kOc6vc4e4Idz93pDvKHe2Occe6+7vj3APcA92D3IPdQ9xD3cPcavdw9wj3SPco92j3GPfYyng6Gop18c3SJmadpkHeGN/EFDONmiaGZdbHr9cs'
        b'hHGjIyDRV3iHlRWHNYo0S0qHtpjRhOutCrh+GUadlE0PMWr/UBXBuEZBJhndwW7cilsK8ubhZtxWoMFt2aWFSfIqdJIZO1eKHxRWaCSuIfAovl+H23KztdlJuAVvz5eh'
        b'G/g4o8LbJHq8N9xFQLLo/ADygGzsWkYqZdHxujT6ZizeVJlIX8pHR4uycZsmW8pE4j0S9Nxih4ZzDYRnZjQqc1PT4N4sdD4X7yjIljHhwyXT1qIDAvB9eN8o8kC2Hm/L'
        b'F+6r8DOScfgoehqqGArPoJtoO7rryIbb+BC+BuDwdpYJyebQ1SL0HO0u2qVDp0Lx9XB804Fa8O06fGMlag0PY5jBi9DTI6VBJeiWhnX1J1M8ciZuzcvB2yXodhEjwfdZ'
        b'dBht6gd3CRKgtgJ5LrocD4OxLRdvRy0FpE2oLVmfpJEzmXOD0NnGxoSx8DTpHDqF7vTHHdCivAIZg56fKmtk8Sl0C+0RgSnRFmtiTpIWbajLT9KxjDJGEoKeV8HdOLg7'
        b'aXp2YpY2YeAa3JJHuhSKd3L4mZlRFaw47xL4S/PO+06CjoHIyPzfoqM73q1xJ7gT3Vp3klvnTnanuMe5UyvTRCRlm4MBSTlAUpYiKUeRlF3PiUi62R9JSWOHd0NSi4Ck'
        b'2wxyRskwcf9MMOadqxzK0MJXlgiYq5YYlWHjjELh4THBTAT8f9tm1H6TNkIo/NkSKQP/s4rzjMpJEU8w1hAoNEoHSP8W+UKElHl/7JfcrXE/HX2VsQbDjfvlB9mrBlk4'
        b'87gx9d3UE8teE4pnmL4K3ztNG8cVvsd+vfCrEbsYD+PSESR8Fj+H98NqaU2eFx+PtyVnweyj8yXxOfnJeCtu1+qyk3LyWaY2PHhG/BjXbHhlOTqR4nDaV610OfBtfBVt'
        b'0uAb+Dq+Beh5E3eEK5QhquCwUNSOmtH21JTxqRPHTUhDt9FVKYPuLw7Gl0vxGVcOAb0RHWzIzcvRZ+fn4nZYqdvxNkDzFtwGjYnXJug0SYnoCjqHLhXB69enWqGdu2DR'
        b'7MRP4j147wKG6Z8SFokeoCs+pCEjSoaH4J8jxUvDJJUScVK5ZpjGdRKYVI5OqoROKrde0tOksuLEBk6qVG8nlN4yfzYjdUyGq6//+89c0+vlHxmrKy+Zs9jry+Ouxx3e'
        b'+Lz2zKB3KreWbVWd0f5R9fLArZVntLE7s1IkVXIm9uXQUfsWamROso5M6IIWhn8b2u+CQdguYaRTWHQNQ6+cZJ0szUY7E3UwOC1alpGjHdwMaxJqQwecMXBzRTXelpgU'
        b'n5XEwa1DXOiUJHQg0kk6jy+Pr09Mwm1542SMvIyVwthexhflzmi4p0EnedyahS4Dz1rXGMpmoDO8hvVw8RqNxE463JmcZx7GTK+02xrMtepKge/oHOY600yPxGXhyTg4'
        b'5GSoZoewkaydXNrJQGmknuBaU43ZATzK7JGa7FUOT5DBYHfVGgyeUIOhwmo21brqDAYN1wkLrgm624NIIiMJqW8OgaEiMO5HcHKWY+U0dZHuzxyIzyVCH1mGw9e06AA7'
        b'G9+tzKjguiADnb9UggwcRQdppdSHDpK+o4PEvzofOkTpXbGEGu7FO2MdeagDH4Cm4/MMOot3WV1kMUtiB+bmBUtkDKthsLsqz0XmwOqEpdNRgG8nQDmQz5sMOklvhCxA'
        b'e3BrAd6C98CducAkFvR39SOEYsljofnr8G0o7cegu40lrkgoHWjnEvMT0TEoncfgw+iZMloLeh4drU3UxS+TM+xiBp/Fd/GT9MYiSxHeMw/vQHcg08Dko1u4lfI51FGB'
        b'D+A9MORaZjR+VjsU3dEEC3eauOnTYEzxFmY2rL4t9fgB7Vfa4vVrSfFpZp4Sn5ZKaP2x+O56dBdqwfuZIdCT/bPxAaFFVyYmY3rjNsBCu/HtpCh6IxG1L0N3YXDxUcaK'
        b'nsNHp+BLdHbxqRB8FNM79xh0LBXfQ1ey6GDjq1HoOLobDlcnGPQsuoRPjES7hHnYgw7jE/hpjsgx6AG+GQp8aiNtL75bF1MMtY1l6leNxbcXU+h4H2pCN/EeQLoUJm1m'
        b'CozMBaGilmXQWegAaouAm6idMQyFW3Rt3W6YhDscuGMVQbxzQKCus6PsDZQs+CgRJyIgxRayzquYRmZpxDq2kW0G6c8ubWR3cSulgGSVdMkI64bzcLoUD1uhYYV1IfWu'
        b'hYch060Wh7PCVlM3cyGpktQvZ1zT6XCsHJwLYoyPW2fhvahjBQKaATKQHm/XoFuS1FTUmgvD3uEIxZcAP/BzoejqmPmWhIIhEsdeqGVT9qDRO+6pNhVGN/1Y07zkB8df'
        b'fPGtV/7KHmgLlrS8dXnXh1NbQiV5v3wJT/vXVa625qvTl9/fNzDkZOT2OMfLmx1nnEsal46VJ6c3HHj7T/McA25kdlRVrh71d8ure9/Z+dQrXy3McVT/YGSW7vZvYo6u'
        b'imuZvzjvpdPRrY0vMev35R9bMeyJD595t+4/Q9d/GOn87Jsrsb+/MCxFOeZJ422RROI7+C7alKjT4G1afLUQOo4ucWn4WXTHOQhuF03B+0HQwM3ZeXoZE4quoe34HgdC'
        b'1OEFzgFwPx1vSsWtWpDDktAxdE7OyJdxI4nk4hwGd52AMLsp/3tiFBHDtuMWdClHxkSNl+DdvJI2AN2Ziw4RIu2l0GjjDCDSaMuKbhRTI+1S0GUiPaHm2gobbzYQMkoJ'
        b'KBHzmCwpK2UV4q+UDYHfCC6SjWCVbBxrV/kRVtbhCam1GRwg0VebHXbC3O2ELHVvCWcnaG8P99FTUk22j54+G+lPT8lQ5CWic4BIeEuIHy5JmYF4t7S+Et3shbBSLhtA'
        b'WHvns90kfN9S8RHWYEF4mqeNYoiUm6I/V7jNPF8QiRbGZDEgEqakxBSuD5mxlsmgpW9q+jFqhpmcMvHmwqtjyoRHHWEhDCx0Rcr8G840cwYjrPpLc9HOtBQpoRf4hoMp'
        b'H4ZPWZ5hdkgdZXC3MWP66NfHhWxIiZjz1jv50dK1MdOzPt+VaN3nvPaLhJAPLk84tfav7xe3JIx56dcDXnmt9o37n/1xRPPmbf33Rq4PPf3a9siGNNtq54pNYfmhup8c'
        b'/fO4yrYDn4cPLIyRDW3XcE7SyVmDajq59uIULumxOoqKIBA9uyhRl61N0OhA8sItIDSq0RZ0SboMX0FnRaLwrRjWr6LaXLHCUGE38xanzW4QGTWd9LI4imcRkAJe9fPD'
        b'K0mFhfcEVdhctU77mt7RijAee5QPrUgti30QzgagVRJZPXeB4J8GlMoCLQbtKNDl5IM0g1tATwMREdYUMPAZ6LAcn8Ht+gD534dkVJRjAc06RTmWotij5fNKfxQj7Rzd'
        b'DcVGCiimdIkoNvNq4pziVBGbdueK2LSKH4zWmpgSWrq9UEaEcXVK7OthzxTmCDi2tUJCEThFrolaVR8qFPZ7LIwBAS4+Zf6fapIfGyQUDhoUQ3RsdYq+36Jv5qmEwpWK'
        b'Icxk8qS+RRlXP0Ao1A8aTtTeySnrL664V7xSKDwSN5rJIq8P/8CyPC9WfFIRzxSSxTDuouOjBIm4QkYlMQtJnfNOLbnGPS4U3h1NFZGIlDGr1ZvzxwmFq+JChQUy5ouJ'
        b'94ZZhcKvcsYyeeTJfslT9oTqhMLX4xOZEvIku30yGpYgFEaNHACcE6DXRjz2qXmeUHhrvoLoMSkp8vTUOIOo3LxREs4MBoxOmb819tacKULhL6sHMeNJnaqyCNnKMKEw'
        b'Y/RQZjp5ctkXa1JN0SIg60gqDKbM+0XNXxS5QuG/82NBXoF2qhpGmjW8UHghSccsIa+bOPUrFfni6zkTmGoydGu+MXwpXSYUbsxJA0yAOjULRmTVOoTCX/cbxxjJyK/8'
        b'T+TKxRpGM0oQd3BHqUpONNJxzDh0OZeKX6Gx6CSoLE+nwfSnMqno/lgqqwWl4jurwtI4osGmAXfZTwUaQPeNIOfvwbfTQA4az4xH99AlWg1IM0fRhnK0NQ2wfwIzQTWc'
        b'gpwticpj0wB3JzIT0T28nT6rKpEAh2pPg/UxiZmEj+Bb9FmnfSq6VpEGospkZjK+J6ftWIPbM1avQR1wOYWZshjdF0Sxy/gcNPrMEtQBzZ7KTEV7HC7CJZbUoONWO1kf'
        b's5hZ9sm0Ctw6KRldjSPyxmyQ/46so43AG+uq4nE7Ef7nMHOAN56iD8+oSMeHshzQibnMXHQV3RQEr/1TkofkOqAfGUxGIwwGqSGqCGTSw3ijA/qRyWRiN0ufXRLUH7cu'
        b'd0A3spisuSA7Ugn0yQi8FZ2LxaQj2Uz2anRMaMWNuXgPurgek37kMDkTpgnU/QTaBXpjSxDugFbnMrmovVKQKK/AbG0D6eAZ3AEtz2Py1qI9FMJqoD0HYRaO4w5ofD6T'
        b'H7eIdqixFtq4CwBD4/WM/onlQnuugMj4DN69FndA6wuYggWipHwNtySgljDcAe0vZArxvcm0U7IZ6Ay+FkwMa/OYeSNctPGrU4NBcN0aCk0vYorwVdwuNP5oKnKDwHMh'
        b'FNpezBTjs+iB0NkDufhOY2goNLyEKYEZ3E9hgsx/227AraHQ7lKmFFT2O7TlYQnolAk9GwoNn8/Mn4kuNajUMzInzQ2FFi9gFixW00qDQQs5vx6dD4UGL2QW2kAJIZWC'
        b'eD0LXcU3UStkFjGLjPgYrXQScqMTeQmoFRpdxpQNM9HS1YDWhwsLUStH+MDiUJ4uo9z5ExkrWZoDLhQV9CtgrP/65ptv9AVSgXyuypXunWwXCkcGi4XyGUP2mdczFqbC'
        b'JnP8HOrYkxpe0z6tdta46Dl/8vxxEJq0piWYDYl9/BX5r1hZ9E/a4ocWnXq+cNTupTOGH9TlvDF1YcSPToRk7K2+sLZ2nGNTyO5Q89MdY36hTFd8cvR61i5044MVc6IW'
        b'JUz5B+JatfM6Xg+52Ghsa69fdDRs4jvlh4fMnPev1zcnN54277d99sX/Ur40vvWjHz9c+1zpL99M/+x187ZfrD7//JcezdtRfOZY9vyqh9evHzdyycef0A8+cuv2ClX9'
        b'/9ZEvbe9TTW7tfUtzcA3vtgVZ33jzMPWz7TNLY0bP5q/6BvJTz6eOvnD3SDTEuPf5JEWkEn1xPoFnP4Oeo4FyfUiB2h1ELmpcm8BFXJPolHSqd8nRQx0qimCA4JsAUkN'
        b'lN98tB81J+Vos2VMJL4jwW58dYQgNDdHgmTbio9xeHtuNlH25ZO5AWgnOibIGofwrXAHupylT1qbGk8MmbhdwvTDOyVk3S7WyHoUMiQ9SQR+oodKFD1cFQYi5FK5g9iV'
        b'GV7JSjkidSi4aJb8RnJSkA8Gkrwkgkok5E/O2qO9NWokIJO4KnoTRVh7jE8KiaZc3SuFHAswFowhi/MUPoR2+Ekh+ZCAmBu5CIZOgzfIgDCfXtqL+EGMj4yf+MH2Kn5U'
        b'f7uEGySIH4poKijEfbbImMcOThTFj8W5VG6NWDLYmLfUkirIreg82oeeEQVXBh1VlRtGWqr+/j/OQexyOw/O+NT42rLXy6srP+I/MX5kXF6ZZ3q9Mn53lilE/mXRgeK4'
        b'soOj0rVboysjco+cfPJk07Wt7Lkdowed2wrM5PmNYXlDXBrWSZTfDHSkf2It3uaHehp0wCt/9jL/A4X5dzjtrgqnCwRQg91cabaDyiPggpKMxhMMpwC9hkqgsX6zLXXA'
        b'w71Pd3/fdJMXN/mme0PAdBMmvQJtQ+2+2U7WaRLydZqknHzUkpyTn5uUA/ryKHQJ9EXgFdtCMDDmmb3OfaDo2fvcB2g35IfrNvdyvcCRtuFttlDoXTa6yhC9/GAabqfz'
        b'3xAiyivZjrmp00YwGZYjP2iVOCbBreMZRZ8ahVn+DP474/NM1soPTfHzPzJ+wlwvOnB90baSogNNA6bGPf5fo/xNJfPNL0N2v/UTUD6IQRE/XwRd3o8u+xkOkwrxeUqV'
        b'8K1yvC1QAwlDd+LUoIC0TBbn6dGzH9dF8Qic+xBh7oMVLNFB7HH+M1/xrTM/wDfz5MUWUmEEnXnm3wFzn0ppWzDaSeYe7ajtqnJs800/zP0adD4YN+Omkl5VW0kXm+F3'
        b'VG27m5DlwsL/OEoQiE/ordab44ME6XPTGoEZvsAblR8liEJ2slnYLIgIXas9nTWGsVj3XZQ58giAmNEX6z4yfmZ8tZyYnz8ynjO9Wpmcyn054PCAoriOARusZ6LHBG/V'
        b'j1G/ofx9EFPqSjmbMiFtW5ozNTp1i+TfLyqPWJjtX05/P+KNE+MAQcj6QoeW4jZ0MS9fC0BzZ1az6DpwoqcofswGGekI8C28I7kgH7fps0E3Zcbr+xdJJ5bY+6qfhtWa'
        b'VzsNvMts4E1OATciBdwI59gQ4A3EBsIBN7AP9OGI1CMlD3uCrWYTD++t+RbLB7EL2Qf7cIZU1O6HM18FKKlEM0RnQIq5glvJBhhqKdDko7YCsu2HT6F7zGh8XVY2H9+t'
        b'kIjzKvNHk4kCmkjpBpXMLa+Ui6gioeZlKaCKhKKKlKKKZL20Jx5BqpR3QxWZgCoPJqVS5vZejtU+WTVTwIr1YYIuumF5vVI1KoKx3B8+U+IwkFdvO4ds16heSFFK1406'
        b'kfxq/Zfun6INF8zzTrTl3XrwTMz4sj9XvxAumzJgxhH+J5/lPt40W7dy5ZZD4x+OD5uw7tPPXj43e9PihxdPfPj2n/+788PaE+VP7JIlz9dP/XzYPwfGDf+wGkQYgihj'
        b'0D58nVrOcEdhEMOhp9jS1XgrveeMQcfptikjleLb6GkWROtz+BaVTCom4qdyyXJsxW0F+E48yyjwdg5tTq6lco/GVgZ3mpOBNknz0UYHix6U9KeVJoDWchu35qNLE9A+'
        b'oKpoM5tZgc71JqvIH3mrK1Yqq8xdkDJOQMoBgI4grKgAKUNYJcdxCi6Wsw/xoaaMoCbgI8E2j7zC5bRV+tOyHlcDoCwRwuxDA9GUVHrQD00/jvVHU7LBmIs6FuYWJPlj'
        b'KDMMuUPRU1LQVPbi6z0zsfGMKMCQ3VOmUvZ9GFkY/MV0Q9BhAoIeXfgjZi/LxKcOMwb/sThOQNBKnZrYMOIPrjcOvlcp6vE7J9M9zskdJqMyeXaWUFgTTY0QcTdijMqn'
        b'JswRCosmUrtM1giVcfrJNbNElX0GNZYYFxYaB/9yPisUFpoFZmnQGyPvJNWJRohB1NpR94nGmBfdXzSW3J1KjSULHVZj+YqsfkLh9qzHmEaoc8Bko71CrxYKm2ZOZ1bD'
        b'639fZkzdysuFwtvTpzFOhqn+4TBj0UR2gVBoHUBNIIomo7Hxo7RsofBzg5YYYJg7i43ciPVDhMLiRdSmFL/kCWPe35LmCoX7o9NhqqHx642pKZL+QmHqDLq2H18026h9'
        b'fsYMofDv9VRSTPl5qdG6Xz5bKPxyxkBiQSncFWFc8s6ATKFwMjeJKF+FG5ONkUfGTxcKF5jmMSdgPCPWGnNKSmuEwtXzeeZVeOHdWcbK87NdQuG75krmdWjnkOFGeWa2'
        b'OJsvGqitRb1vlHHJqpULhcI9ShXhYYpP04zKmVHiHL03Zi3zN5jN/P7G+eYK0fg0RkVJWPV9uTHyNac4dOacEcSoU1itMM56e1IYY1n8r62cAygCM8axoHRXvh6nRGx5'
        b'5dpXf9l9ZvPLYdrJitsfPdU/7nzRyOG7Ylq/eG1Qx6fzJge/8t7g7W2DXqz874wHB78o/n3alSP/Kly2Zlz/1i9Q2pqLksEvJkZHLXxBOfpFJj7z8QnsL6d/sun8kRc2'
        b'xCz831/en/bbbX8feumlQx8yo35lWZhY9Cv9C6WveLbW7r5zcPV66eEPhpzvF1+lu/pBySf/LH1t9ezb4XdzPzt34qfvOn9w4fdfH1r+7pvL//2P4fdCXtuw59aaX3yR'
        b'UTSk5MOha8ee/yIycezk9Khn64+kPbz7XuZzr9hPD39j+ub7Wf/Z97Lr7RN5UTOG/vSlG89NqfzhhDv5N/79leeDnM+O1d/KH1JwZOmDx/bc3/BB8owfXVx4P+t3RYvX'
        b'xdiOjz3xjxFZ04ZzZhUa8PXHocczz/34sa/HW57+eo9G4iREJBJtmtOFL7vQYYYwZnS4XuDr7Wj3glxtfBbIPqy1kVGAurnGHEwF/tFD0aFEeDmBRe4aRupicct0dFwT'
        b'9i3U89uTXmizv8Wa0N5yU+0KQ7XNaiHUlBLgEoEAT1FIgATD3ygqG0SwarorEkHlhEhOKSW7JRzdM4FfSZf/9EolUcLzkWwIEG8Fa1f7iDfInmvMJrsfve6FmbD24T5S'
        b'Tap4xo9U/zzan1RryXjvwK0JAq3OAe26FfLEyaEdVH70ZAPMkFbOzMDX5PhOERegLcjE/45KskKIExlTxvGh1P7NgRLC8ZLNwWUSs5SX8rLNTBNbJoNruXgth+sg8ToI'
        b'rhXitcIsJRygkuOD+ZDNCigJdoNQWRZCBRGlJyid5+1mh0NfIRfhK/w5yFTCQQS/G58fTqVC5CPyZgXwkSDgI3LKR4IoH5GvD3rUPnp3mVimF0xoWyfiLcVoIwKKyAxn'
        b'hk/DdwV3i53Nl2QOB1z95mexQ7aNU3HjlNI/vzH6/bKc5QlDXwz9aDWTLy26UHzCmVD8WccXb72+PPOr3RrtB9U/rVhaeuB3Y8uXHF5l/u2bYS+tsqxGrk9+e3DVnf/+'
        b'emqtKfLTr2eGbvnhW2l7Wio2lfOt789rNppVQxduuvi+7tN/Bk35+ZDF2geaEKo5jV06mi6fowlkBQnrB91A96lQMw9tRwfoFuHRIH8/jvM5dIGhM7qhibonHidbmOL+'
        b'JYe3OwnrR09H4UvU7wodHiTUjO9yqAXfws/ThRuPLrsSdegiPpckKGynuBQXvkYF8qHoHtqCWlE7bs9FrcuSYJG3BzGhsRx2cw76hAldxZtQawGsbtyWqEEXZuADUiY8'
        b'WOLEh+pov5ahuxnwwLQpeIcWnZcycgU3AF/EVyhhSVyKDiCQ8JqTddkgfjXpCqil6bQEbxyPnqRdz1w+BJ7QafB+dCwnP4n4crVyIKidWtxdMlf0mXp0Uocgg6HWXG8w'
        b'dO6WPgFSNd0lVbCxIJiRq0hWLv42hIuYrBPfE1a6wiOpsDrothXomxbnGo+izkZ21HmzR+5w2s1mp0fpqu00XfSmYMjtRGewk10jYSOMWJjsxInOHu8jESMh+a8fidg6'
        b'0I9EdGulT3Bjxb9i8ipZg43MckFbYPUa1qMwiHt0cC11mK1+7gPCcCmmW0015bxpZhjUQlYM0xDhheW99a3ANgvAZAYyUkD4EnwwfIDsiZCovDD6WmOwwTvqvdQa3uda'
        b'q4RagwzCDPZSZ0S3OgMkZOILR8w8QB/7JhtXfruRR6K32NdP5xzEdvHk5NpPjR9Rs42y8r28IOblF6K+4PAPTmpYuggnouZcukqFJbh2GFmEbrRJ9AvpWZG2OPxMbZ3e'
        b'WE/Ab2xDjHfSA57yGnHoMHViOBfA5hJ8I5cMSSTr1dA3wO9fVf5Y3DMQoObkRxMK2GogjmAGgyfEYBBclOFaaTCsdJmswh26TmAx2m11ZrtzjbCeRgcuqmTaXeI4ZnI4'
        b'KsxWq3dVd7cUAYYJj8EjtAsjIPknI1oKFTKGjYxQsvSXo+48DQ3DpPiOIy9bk5OkkzMhy4F24r0RAXMbKv53bGf9WDJbJtkr2Ru+NwL+wvaGW7hKDq7EX55rk/NawrL9'
        b'3FQjgGUSph0M7FdqlgHTDtrMAIsObuOAccv4EJoPpfkgyCtpPozmFZBX0Xw4zQdDPoLm+9F8COQjaT6K5kMhH03zMTSvhHwszfen+TBoWQigexw/YLOiTEV6whPxYGAb'
        b'S9usBFFjED+Yigrh8O4Q8q45nB8Kb0vKImjPw/lhbRyfJNo9JLyaH0771g+eH0FhjaSwIiE/iuZH03yU8PbeoL2KSsleKT+mTcLrqGAheJmT0VK5wyuD+XheQ2uMhhoS'
        b'aA2JtIYYXkJpYjIILhWUIj4cG6L2+xFLBdf3gDsauUdqAWnTIyUI2BO+6SuCxAknK0TlXdgZhEYIElAwGTxxUr0+yapKlUg7gqg8pADaEURph4LSjqD1CqAdQrOl7/8b'
        b'1mtAs8hPdq3FaTFZLQ3EV7/arDaJnbAAXzLVVhBn/66vTK0z2U01atKhqeq5FnjLTl/NnpWuV9vsapM6NcnpqrOaoRJ6o9Jmr1HbKrtVRH7Mwvvx5GWtelb2bA2pIj59'
        b'9uyCUn2JQV+aP2tuEdxI1+caZhfMmavR9VhNCYCxmpxOqKreYrWqy83qClvtKljeZp6cQSDNqLDZgXDU2Wp5S21Vj7XQHphcTluNyWmpMFmta3Tq9Fqh2OJQU2Mz1Af9'
        b'Ua+CMeOBU3Vvjjg8ZKan0naRK++JCu/wgtbBm+2PfFlkuML7YgbGqLggKW3cxInq9LzCrHR1qqZLrT32SYCkjrfVkcMZJmsPA+gFCt0RIcJVzy3uSz1edivU5c19//oE'
        b'RivUJlx/j7oCDOTdrZ5KvXCyYQ8I0NuImVCrA9lze+4C3Jy7SEcOajDD0FNS9HyhgpoR/hXRzhxnJnNMilFfWVrEuIi2gjejS2gLNRcW4uZskKyTcQtcFRRDLVBHaRa6'
        b'nGVD9/T5+dn5LIO24aeC8S10EW2kda61ygf+TgKsWW1U6hZrGerKhO/gs/HQoO2JucRRMG9elk+sluLdGnSeKU5n0JUgEIWv9KfVoIGS+DyqShnzXs6vEMweSzjZmK0s'
        b'iIWPG/M+Gb2GcZFNJrwFbx7oXzduJkc1oLXJRVl4W56cQYfQoUx8Wo6vQd+2CzuCT6Knahwric9xezXeDL3IjLDM59+ROF6Hu2nK7NHtubXcuIg5v1714/YCRjPIzu14'
        b'ccivMl57eVb1zkrTwkNh984/m67f6agb/9qbf1y0fqnu2X4pBw4HKW//+O6cqs8//klM//+V/myjruRPP9v127fX/ezTCadGritu3Os+saW87evP3jirbPvzsoyq3Z9X'
        b'Z/x47e39T6xY//Z59/qvPpw2pOmHl/I04x0N/zHbDA0dpx5ozV/v/Lj1h2O+LPj4B9bF76S/sU+lfeKhdlS9uv9fP0yN7biwZMH6klr1kaC6Avu8Z1OrTpsXR92NHztA'
        b'Zzu5PPPdlApNJNVH8DOP47ZQGCFNvisvMykBb0vmmBjklipgzM9SjWfKMNSKW7XoEG4S99d9e+v7CmgleamDcnU5+dps1Ibb6XkYZiC6MbRIWgvodk5Q2PZwIfh2P/9N'
        b'sgh8yElkFXw+Fm33bS0q0AVvHTF4swTfQffwTarYAbwbeJewm6ZJ6fToky5L0TmJhaCcnQTzvQO3J2Jy1kbcqsxNInZuuh2fia41PBGE2qehFurpivajQ5LcgqWTiVGB'
        b'okToPA4evguNJvc1s/GFNfgIdF9skQwfYvFzaBM6SjW1laCkPkukTIpN55dJ8GEW7YCiXfR1fAGdceDreBupIJcuMxl+jmPRjUnC2J8sRLd9qiQ6jDYSvKe6JNod5ySc'
        b'c2ZxONEW2zTUo2DLNHGMhcoSUYcMsPwAPibsRN7DB9JpdXmw/J6eJcHHWbTTZKFKrxJvzYZ7unw5g5+uluBbLDqMd8wXhuEmOlNE2phPXRv2xBAruKpKMnXBYOrwizZV'
        b'OeFdItGhXYuIUKeaLcnoh9rpXV3aY+RdLQy1fspa4uCqQuckc5bz3v0r1f+11auroA5SsAU4u6jCZnhl9HEK6oyp5AT3Bymr4pRsLEfMWkrRDTgC/uRdfjkifsOvkgPF'
        b'TqC5Oi8AvSAWBwsiPDmeYp/CeJXULkJ1p/TfZ61cEyRUEhVYO60zwVcxFbunQTIsQHP4YIy/5tCt6d+q61V6dVIi6/Si6S3003tFGF699+HoEp9oRJgWiBFerhVvN5v4'
        b'JFutdY1GB1AkvK2irzqt1FBuqeilQYu9DXo4ioAHsapX6H0fCCLL9AJ3mQ9uYu+Sz3cDL+jcdg3TqSv2ANzkA67zF5u+L/wQEf5y1jvuHCwrk6B9UqTspS184ED0JlB9'
        b't4bQmeDsc7yLoJc2VPnakNwXQez7DIjQjrG9t2O5rx1J3y7CfRe0EOxTtA29gK/xgU8poVoJQPa3uqnFKVVb6THmHlvw/Q03ovL18KluEulsok041JYu69JhNtfQY9Og'
        b'wlAlo9uL5Ci1qFkVgyYDPZrrstvUhaY1NeZap0OdDj3oLgDHQzehs/Diqom6VF2K5tEiMvmRMd3t5SUaloqAdfjmpER9UlatXMpIH2fRBRY9a3nh95ES6r/y1TtBnxpf'
        b'X767PMv06h/jiz4yvlpOnIa48j9Gvxx9ZtkfVS+vlqvbhx/YmCZhXjobPOFMg0YqMPtddajZxyiTstLRKZFT4ufRCSfZCSnBG+oi0WafKBQoBy3FzwjceHvpAOHU8TK0'
        b'QeI9dbwT36a7/aNBONmai5+cRGUSbhmbvB4f7M3oFUQsTd6zM6JP0RPMqhA2lthURXovPqP/jtYuciq1LoBn7VYF2mwD64eXCf/rxXuI2AYYN9sn7yEJJSjSh+5uuFBs'
        b'dgr2AJfVaQFtWKTlLoeo/tJgAU67qdZh8jv0X76mW0WkjqnUIjLVmA/PQFXwz1Rltht7UdLIT3frpuiaUljUzgxmmbgUrbk2Q5LEuIiL2oS5C3pWvPCT6JRP+QrUvDLR'
        b'TUtkyBwJPVQ7Zn30p0cfN+YA0mqLPqa+jJ/xnxilb2m2v6OdmzBaqXl8VVThqaYpx8ZtEZA34fPQg9MHaDgqelsG4mdASbg+j+oJ/lrCEC2VU/PG8Z1yqp+QinYit1dQ'
        b'lePzovPRt21fOsxOg3dqKFOmyBnhRc4nGNYr0zUM8KJQt3f0XmAUH6cEYmwPLk70iU7cJd5gDQG42+zv5NQL4L7uPKgCX+uFyG8N5DF9xVqd92wRIQw9+1pRRxbqxEKs'
        b'hT5Hlt48rbwGN1AyuhvcfCvLZrdUWWpNTmiXhX8UO6w114ske5xuXA9mjUfbcnjBYEK77PWPBEA6dZF5pctiF0eEh6sKp5o3l1ucjh7tR2RdQwscthqvSGUBLmmyOmy0'
        b'AqFqYVArzXbHo61LrgqhRbNnZQP/tax0kfpAHIknvFZt97YKYGU7TYT79k4eum/oKvT0cCo6OQY9n6snG+A0xIA+aV6WzxuzCDfnzcuSFGnQ+Wz1snK7fb1lWTAzY+Gs'
        b'qvAavN3kIrMtQU9RP/ZOk0vn6wy6jveVgoJ7FhjVPnYlvqlYgI+jzdSuj27hZzNwBzqITihh6vE5Bh2bjI+70uGeoRTvcqhc87PIOcdS3KydT3fmW9H5kiwtgbM9Ow9v'
        b'Y4EyndKsRk+Owme0+HwJR44L31YW9kfHhINtG0z4YIDF5ha+UeertnBB0vwgpvAJOTq1FGib5d+ZEscKeO3MuIqk7XfDNqREzP5L1PpQfq+Sk/zkSPymvdyBDeMrV+g3'
        b'vnz9v39TjvOcHTmcn/r7H7y8z7aVP/83hWLFut/PuXjk45AxO7PaVnRs69D988y+H7+z5l8LHTG/bUy+X/+T331127WhYUdGaP6vQ/u/OezgzCmaYEFhPleCNkHv7uHn'
        b'qcpM9OXQWg4fjsmljDzTiDaGJpDzBIQaeunlMNQh1fP4Cro/nurr81D7TD97CG5D7UloHz5MTQszk0tz18Mo+MxhjDJCEoOb8BnBsfg2i6+LZhtSfXqVlyCPQm6hjU34'
        b'KRhvEBRWwlvbfYLCU2gLlUfQySfwM52uyaNQh9eagrfhPVTSGD4Db6D2BHQ2E1a7YE9Az+LzgrlhY/FCYlHAJ9CVfDkjmBRS8R3Ri69PfiqEdnZSCu/JyhGdhD5KAYq5'
        b'QOyVIskXcvIuFDigFr23DZSg+khgb/Rf4vdYJxMohKSFEN9oLxPYwPw7+pFsIKARfdd2gZz1QvxP+oj/OKpsdVK73rSM76RkkDa4etO4T/naMK1HIje7dHZXc30PrSHe'
        b'QTV2c6VH7rBU1Zp5TzCQZ5fdDnJ9RoVUbCmxXiu91G+WwJ46gyUx7lDRX0ZZqRSZlbRZBsxKBsxKSpmVjDIr6XqZyKw2A7M62CuzEoJDCfIbpfv+Osuj94hIXwSq733X'
        b'56H/aHM/7bnwFn0FRo2UmYi2plPPNtUS1cgk3itfDvyrR8ZFdqKAlxQXTJ6YMo7uQZH9IZ7on6A1PRK8b8CnqjOspip1fbVZ3OGCDpM+dz7h7dSjwNfanD2AsZuhI7WO'
        b'qer0roKxUezOt3C+7qpZiJ7ymNgleKOX8aGLZoH34WaRAJdmATssEnkZmxqJ9qA9uCMXd+Qwo/EpFT7E1wvBHZrD0fVcXVJCDtDVztcL8JnSLB9XzcopjRcDIIA8jU8P'
        b'UeJzaPNI4cjx6mzhrLzreXuEcybjmkAK8U58oWcJPSknv5gK59H5onjeWhyMH+DLCXRXJRZdxRtxK32Kmq6zCbdMJPyzk0OXq0Al1Obk6bKTEuQMbtUoV8ZUU26O9uIr'
        b'+HIAOyeDQUDH4x15IIRrNUk5MnwNPc004LPBqM01RSMR+PmWhaTNAFmCTioY6UwWXYzEW1zUct2cmJAovJ9P/KcOAm9Dm9biDnxXCKPVjJ/FTyfm5OuS0DPj6FiyTNRY'
        b'CTx1Dx21PAgzSR1b4bkZC6cPeXPnh3fDuHSltHDtg9sZT21L3DTi1VeHv/Peh7k7XTFG7mc4prV+T/Cx8U9fe1n9S8m0hPU/GRi0KNO+9xcT8t6YH7323T3v7vj5z26U'
        b'r/xo6B8+f/Ls6JF3q3eeLR35g2H5wTrbyDdDdPyrc1+8ff+3iR1B9zOWxFg//vv2Tx5b9qPVX2y49T/W+q+EnAmnNYJTJj6JThCUIOZxrpwN0oxDG1CLk9i6QFY5hXb3'
        b'zLLxVXQMBtk9VTgGeH2mCyaaYA0+vdDH+IdDRZRt4+fw/dzs/AQQpzhGgVo57Vy0ER8Ark4c1NHl5fiUH9sWmbYFPa0AXr2davBoXxI6Q2WK0UuEEGlo/2yB4x7D92HU'
        b'dXm4pYCeFJFbuRFoUyWVCKJWENlJC5ISbnXOT8bb8rUwJckSvK8Wn6Jts0+S+oz8Wim6KRr58c4MgV0q/x9Z50MJKxSJB+Xn2k5+Pp5wc5XIyZX0CIDwp6RnVDjBDB/l'
        b'z1TFmkSeLhd4VClJ5pNkQSBjD/5u7rRSoaYFPrY/38f3FkFytgvv//UIf97fUzP7yvUV3hd64bqv+rjucMIugJhS5uHjNgEmdin1EOLgj83QxNrJDqh9HEmI3YT4/PG2'
        b'CoOBbiPYyYE+ut3gkZRbKh65o+EJ8tqDiSGHasSesACdlQpIfpLTIvqW2D5hwvr9P9r9eRS62clxoQFkpJbBhUIq5aIBoRh26ASOio59TjlVyNBQjoiXXAgbHet/J5JV'
        b'DyNXLroNeZ3ugx8a5cjTC+I5y4Q0kG3D84EObCHif8fXXZyc+NIyKS8tk1mYMjkvKwuCPwUvLwvm55eF8GFloXtlexV7I/aylZK9EbyqjeMXgMwT6o6olPDhfAR131Ga'
        b'w/h+fCR1Topu48pUkI+h+ViaD4d8f5qPo/mIvSpzPyGoDMhSxMsm3N2vUsEP4AcShySoMXKvCuBG8IPaqF80fa5fpYwfzA8Rn4iCOofyw6j3czQ8Q5ydiIOSoiwG2sby'
        b'I/iRcB3Lj+JHb2bK+vNj+LHwP466HDFlA8Q3EvhEeGogr+WToHQQr+OT4f9gPoUfB/+HuOVQUyqfBs8MdTNwPZ6fANfD+In8JLivpmWT+SlQBtocPw3KRog1T+dnQOlI'
        b'fib/GJSOEksf59OhdLSYm8XPhtwYMTeHnwu5sWIug8+EXDyFkMVnw7WGXufwuXCdQK/z+Hy4TnQHw7WeL4BrrVsB14X8PLhO4heKhhQJX8yXbA4u0/EyuuYXeeTpNdSr'
        b'6kKA+EPWtXBDcKwSIomCZEeCw1XZTUSkE+SxijU+n58unjWBblp2qKDG7LRUqIn/n0kwX1YIYiUUEEkR6hQsI9Y1alutIPv1JJt55IZVJqvL7Ak2eNvgkcwtLdI/nF7t'
        b'dNZNTU6ur6/XmSvKdWaX3VZngn/JDqfJ6Ugm+crVIA13XiXxJot1jW51jdUjmZ1X6JFklWZ4JNlzijySnMJFHklu0QKPpDRzYYaG88gEsAovVJ/tivz3ubesJ0SVc4QQ'
        b'wrqOa2YbuSaWZ1dIHOpGbjnbBFqEXevkeK6Ri2VIVNhmrhHQeB3LSxrZFXL7kkaW+A7Ce+xyCYklywcPgOfimGhmErOOrVXA/SBy1cyQ9xoZgxTqBeUCruS8gm7chbxv'
        b'6Emx6Op2Js5wp9dZ1xceJa7TcRCUBZNQBy3pxQwlDNhU6thVXJA0PnXcJH8E4kHHyK4ksrvaUWeusFRazLy2Rwnf4iT6AHA2r4MZhexV8gRkBZXDbil3PUJHmEpuTzXy'
        b'5koTMA0fChlB6bBUVJPaLcI4ARqKcAC5uvftYzLrD2MstXTDqLM3Y0c7xnpYnYdN+ZiIGR8TbvtQoktJ0X/8DfxogjwRXWGT3Q6Tta7a5AmZT7oz12632T0yR53V4rQT'
        b'4u2RuepgldjJ4VDvPkcNSWqZXs9qU776W5+0ECIFbhErmivUHBFxGsIFLOj7/rwgKdBm9SIk/N23O+8F4NucT+qKN3T21tSZ1UaYlQpg41bdHOG/0agDGDOZPriIC7vl'
        b'wgg9uln/8skug6iLQM+42DOwCMa7FdvELOdCfWMhoVPhUZgcBuqB6VGYV9fZakFX7aUh//E1pIJu2rtqykHfhYEQR0BdZzVVkJ1Rk1NtNZscTnWqRqcudZgpnpe7LFZn'
        b'kqUWRswO48gbjQRNTfxyFzxIHgis5RF7qvSwD0ujHvhiP/sO+7DU1v7o/dUqjfT9z3uiMqV1RMoSKIx5dUW1qbbKrLbTonIT2RSwCduo8JRJXWe3rbKQLdLyNaSwW2Vk'
        b'k7XODGxiNgynHTo0y1S7gprHHU4byICUHtT2ae2L697bJANtkpGMqYuudYGyEBLkM4vDmBKH1B7210gkbrOz2tbJsrRqhwWIqFgNeY3scvu7tT6qj2JFU0ks76lGkZv2'
        b'sFHXq1Wj3GYj0VbVlf7mExedCr7LNPRIFevNdliUq4AZmsrJdv0jDCk+SZKsvO6xTlR6eiauDj2Tmpg0GbWC1k8U19wFxNSAd2TBZUFpfI42O0nO1EQq8AOn8AK6hq8R'
        b'nzN8Fd+cF5+TRCLhtifqtfg0uomfKkrCZzhmfKasCp1CF2lYanxlPb7g0OXn4H318kgmHO2XPDZch3ahLUK44+diR1LrA2jQt0QLRLw+KSE3qchbe66M4SMU6G4cukYj'
        b'VT8G2vB9R7wQIJyRoXZ2WhW+mlkjGBbaVk4vRm14L76Et5biNryvlBggClh8Ix23ZNAN+mn4WippkazBwkjQARZtsE2kkvkaWSh6aqUjS7Du5KJnpEw/aC+6xKNNgsnj'
        b'FAnD7Yin4X1k61jUHoEvZxeUWB4c/ZfU8WN44n/rbw9pm1E7K125+ZX//Khp1Kltf9PtLH48c9/EuReaXy4aVZxeVLj68IHyArRmMlvVMmlf5rGDtobYlAH9Gvp9kr5p'
        b'15zZs3+8e3K89k7m+vPpww8+nVj08Lf/i9ZnPPj50yWj30y7s3Dnltuzr6QOaPhV8tFnl+9akWuo/vd/z4wKfz7F874jbfL0N6pP41/YhyaWPj19+bifNjSfTbxSVvSN'
        b'5Z3HO6aHuet+Hl5d9w9P2u2T//h01/QH//jwf1X4G+YGyk0sGz/sk49nKhZvf/2Lz3/ztx0ffxl055UZb9x8VdOPWj6GlgaRScrFrUH1uImRJrHosrSYbhOo0MH1iUl4'
        b'G25JzsJtEkaZIUHP46tyvHcM9RtUNASj1uQksnlzv4aRJrOoAz2JNtNqh6AtVYk5+XksuohuMdLhLDpahC9TI0Z/bQKxguQHMXIph9vSFfg82iFYYQ4X87m0NSy6lMdI'
        b'+7PoqUkh1BEU3UPPKokRBvDoeA+GmCtzC4UTfpvQfleiToPOhiV48SgcX5esmY7OC9Ga3fhkFTWhxKFDgg0FP4kOCfeuLtcIdcuGo1ZGqmfR1UH4GbpvA4i3BR8jRpLs'
        b'aXqtDrUkJ2XRzR21Wopv5aPb1Fi0ZChqyu1cZqgtma4zdA4/xSTg52V4kxQfEDxWD9q1Ql+JVa+FZUJ5Lhwfw4dRW6YwGLvx5RpypnUX2sgy3Co2HTeLUVjxOfwMvpmr'
        b'jccP8ImszhOSRqibDFYDvodu5Obn5ubrcIs2VwxeYEX7mAS0Q4au1OIb1GiEToWiS7hVjy5r5ehgKCOdw6J7eP/S7+Ck+H0OGcYIJNEQyAWoOYhIGaI56AlGFUKDshIJ'
        b'ifhuRlP/THIYMYIahVS0VCWWRrLCdlDDYFHU6RGIz0uFHif8Pl6ZrPAqlSGaIPmmixmoKeDkYa+NgbqI6NizSwuNdELjYIFUwPpFOuHoFx16dWt5/+2eZILZAlMTT7sI'
        b'oh8RWIDHED7lk75E0YDICQ5Rpu/OgsR9gC6yRRdJomfJoTtDK+kupZgIJwxg3F4+aiMMnmyCrCEiSPeWmSqqhc30GnONzb6G7tlUuuwCL3bQr3h8O1PvqjIFyql+voRO'
        b'k70K9BPvk73uetT6tj0ErPDueniFJyLymB3+an0vvF/C9OwJQDciJOFC9IprZUZrwjQx3FFOzmAazqNxoXH6hpFiQNTP628xq1km/qr88ZULJ+rDhZMObYvnOMLCOIYl'
        b'dOwegy9zGa4sQng24R2FuV3ECO/2ipezlpDN+OS0BcDgyX5J5x4/EMuGoRFT49FFy9O/+ZHMcRZqTH6oy28bp0IpEdJ/vqkaHjE1ut8Xlxo3oFm7fjMg5+wPJ2S+Erpa'
        b'Ef7e0l/Fyn7z2fL5Fz8bvvrq9bKCjR+cWDWrctmJlwe9OCt4Rm3b1P3vvjPnfj/pS1N+lvHeR69c/sD4waW23+Usqh87uXjQp/Vcwm/Wnx/2pjzKsCVy1qDj//zthNFh'
        b'EWWalQm6tskj/7Pkz+121+9+8YfH9mQO7tj/q2GvNe2uWzb8D6f/uvnzh7JM28QdG97WqChNjkI7U+i2PL4SLZ5UGIU3Uhs7ek6B3Lmd4gU+jpqY8PkSK34a+B4Ne7RV'
        b'kdI5dujCSB97EFkDvo23CeEjTk+LortNNNIPMKgHbOlA9JyTbH6noevomJe24/1hPvIu0natg354ID8c7RGDAqE7LsLlhq0S2nlrKTqX2BlRKhRtAb5yncMX0ZWZlCuk'
        b'4lP4pi8sEL6O9uSz6EH8CjoCc/GTrMgiGakSHyIsUit4NqBmfJIeFcim7BHExjP+LHJcf3oQYwAImacTk5AbnyM3ofEB7JIDeNtYQ7ICnaq2UYhjaicl0l0RdD1RxsiX'
        b'c0PRPnyB+inIUAfeSrZM8L2QLr5n6G4Q7S6P2tH2RG0+EUNpsPHV6AxIqnskdj063tNh874ysSBRR6BsK9WfbU0UGJacMiQVqPoCayLxMVR0f0PwWFCxDSqRO4hVBXql'
        b'1QZyqF5iZXDCs52uCVsgiYeGOWI7+dIGxuMf4agr7ABtm9RKtW0ixhNtG/6IWWwgzzo5uJY0sbHwAM8F5LzRJx5yoy0PpaN1qcCJaMs8SkOtzSBqww6PxFTuoNp6z5q5'
        b'J8Lg27IWbIw5nPe0NQfDxjX091pLujwXYAr07RWTrYlm+imAJs6e0cjS3jArJPbHSa/sCVBCesEQ819trFPCs400T56slAjmQbiWks8JUK8ITv9wrI9Z1lgc0ISKaspm'
        b'RgOVJ5YnqhuTC5g1OgBRlpo6q6XC4jQIw+2w2GrpLHmCS9bUCaYmYUgEu5JHRnmyRyHYaW32Rzjoqgx1djPwKrOBPj+P87pCkvBZBPs4KY3W0BDjHbKA57tNOh0wgjQ8'
        b'sWzSQSGDVMnFCpMLXY8Uaoon3dMKnYTGddrBhDnt9lEFci4HQNsNhiWc+EkFxt/uJdzrGQsjaYO8eOjfmCCCZTDsPbSgK1YFGciheQM9F+QFr/KBp7d8ghjnDz3OuwZY'
        b'nm3i1tEBaWRX+NrATgfo5KNJwgRyAvQdPTRBbjBYnQZDOSdybAbmqCHM1wZy7zs1QTgVAU3gps/4Lm0wGwyVj2qDuYc2+Hz/fctohHeBrOBsaqE1QCC4YrGV5EpwH/Kf'
        b'F79WPQKdoXHmlQbDck60KgpoHNBAcj+ggZx3kJR0kAhwpdcU6fVt7200aqHHdX440Qmqtqex6G0+pN75YGd+h+mogml3PGI6qr4rSsi8WMnN/C4oARqJof5RbTB3WZc+'
        b'93Qy4l4y0XkoxY+y90gFiJHMYFjbIxUQ7vl6HCDjjuqxx/3J9g5DKTbXxPkmIBEIqa/zXgN95wjU9Ng4IBEmnjcY1vv4DYxEiD+ZoLd7Q7/ldD+o8+DWyW8Ze0IVaaVN'
        b'PVPFQIB9GI+4ruNB+RWb9D3Hw+EqNxi2PnI86O2ex0NFmxfaOSKVfR8RWm1rzyMSCDJgRIhzgo9EqZwMJUeQj+6OI2THwKPS25zZwJjN5PSQme9tbB5xPsZgqHEBwu7w'
        b'J1jSwCGiD/QJZcQ9nbN9GCBa6d6eBygQYMAATfcfIHV35BnkG7JBXYaM72R3yX1ApZ6HK9RgcNpdZt6yymDYz3mPFFEaH8LBoEX6OuF77Pv1Y6CvHwN76gddElzy9++I'
        b'Ehio1Waz0yYe76EnUb6edD73/boS6+tKbE9dEajd6O/dkyAaKchgONtDJ/xw2OZPhaSM365DIdNdLBDa7yQ9INvq0NbO6yXcOm6dROyHpIn0SCJcVfr3ySOHMQOwoEHQ'
        b'jl0J7J20s3ceWX21zWom/sI1Jkstb36UrBxiMAh1GgxXOHH1iQIGR45+N/Tz9df7XM/yMRFHBbYXSqeGkpTNXaWdR3FAGmGtymC406McSm99G9iQ7we2zuYwGO72CJbe'
        b'6hlsNAXrFECyXUiovSVwXnqBDkqfwXC/R+j0Vp9EjM19EDGCyCY6yE0v9giL3uoTrMo+wAqmC9wEVb7kBy3Cf/WTm3Yn08XM61s/ZP2TFbOCsUc4QaOmzigsL+GlhG/1'
        b'J1opWSlERyXnGYW1I64YKmbI9B+TSh+OoHvQltoqdZ2tXtjFHpciOHO46upsJBzQQy5F52HHwepp8E6bR7HSZap1WhrM/gvLEwQ1VVmcoKubV9d5FdNHmkJgFChwg+GV'
        b'TjKioOFDVf6jIT4E+EqsmIKXgNxeRa6rSWIhyXKSkKM7disdcjIHZPg0yV38Fu1LRNgOq81JIpCtJnlVoIkd8pWV5gqnZZUQbBpIt9XkcBoEY7JHanDZrfZmUtt2knR6'
        b'QPpw2qPwGS5CqfVW2Cmmtn+qwtu3kYRSqd0kIR/4sz9JkgMkITGm7YdIcoQkx0hynCREELI/RZJTJDlNEsL77edIcoEkl0hCIp/ar5OEfJLHfoMkN0lyiyS3SfLAOx+a'
        b'yP8/HpVdHFpMkLxO9j1I1FRFkJSVclLW7xfoaXRMNydKCceq4+FvuDJIFaqUKCQKqUKqkgv/lRKlTEH/SIlKQX+DoVT8dZFDR/hmFt7rwNtxm+BaqVDg63Gca6QtwLfS'
        b'e1rE8asuvpXeaKqVUhrXVUHDwtG4riQ4nBgWjsZw5YNpPoiGiZPRMHFBYlg4Jc2H0XwwDRMno2HigsSwcBE034/mQ2mYOBn1xAwSw8JF03wMzYfRMHEyGiYuiHpqyvg4'
        b'mh9A8yQU3ECaH0TzEWbic0nyQ2iehH4bSvPDaJ6EflPT/HCaj6Kh4WQ0NBzJR9PQcDIaGo7kYyA/hubH0nws5ONpXkPz/WkgOBkNBEfycZDX0nwSzQ+AvI7mk2l+IORT'
        b'aH4czQ+CfCrNp9H8YMiPp/kJND8E8hNpfhLND/Xz4BwmenCqqe8mUzZc9N0cwT9ORbh0Tzg5mlPSeab1/atdd728x0D9HhJj1HV5jDiLUM+VClMtIZnlZtEhz2mhe05e'
        b'/xIaFM3rqkdcTITNHXPgNpS4+RXoUkI0Ob8DuEZCoE3C6SLeVuEiKoiv5oDabHZvhRanYAwUXvXuJc1Ozy+ZI9ZgfIQfYUAmu1L0jzGpy6npEqoTtgD9DwhrBZDevope'
        b'ok67mQxIQH0mB3VKJY2jXiuroCaT1ap2EWHMuoawpICTxwEv+1gx0S8JcSFHIRzVLOGKShB6CG8cwDRzK4LtA7380UkttsAZJTzwQoOQSmkqo6mcpkE0VdA0mKYhIKWS'
        b'/6E0p6RpGE1VlSQNp9cRNO1H00iaRtE0mqYxNI2laX+axtF0AE0H0nQQTQfTdAhNh9J0GC+BVM2zkA6nJSNWVzdyy0c2MXOYpUtANpaukzVKl4/ipU3sTtahAilA2p9Z'
        b'J60dSEtlpNQez8uB/49ulBJL6DqpcwzIA9ImDp5/3AnruFEq2Kyd8aS8UdYkYZmVf13ANAPs5apmlj5Z7tRsglZQkUqht5MvFD+cICyBbgum9yWR4WENHs5geCgzjHaM'
        b'djwc3fX9ahNx6Or0CRNsxgkeZRFIBZYa0c9SLmyFCgFKJQYL75EZXGannQSeEU5SeMKFsOW+c3R2IjvZHyMJOQNGg+QIYVnyqSQQeOQS5EJhzxtqrHPZQeI1AwgqBQTR'
        b'7QOnySM31DiqKOgV5CiizGAW/tGDiWHe1+jntuClimqyX0vj4ZqcLgeIInYzse2brCRuUm2lDVpMh9RSaamgztYgfQgEw3fbVOPs7JAn2mC1VZisgWf/SRTiarLL7ID2'
        b'0QUL1dD/QnRiz2BDlyEHKRcWo/isDK5rHJ4QaKTd6SAu5FSO8gTBvJA58ajSvTMjzESQw+wUbzgcZjupkN4AUY16PhA7h0e+op58adwvfkIN8+3RG+js/o7IiGVURoyk'
        b'vh1dY24pupU84pcT/kdSqxTZUCO2YhJ6vqF/lxH5joGf7T9jenVgjZR4/WrjugLyOdhOL6E+FLUrOg9+aoV4DE6beECW+DvyQLUtlWuAFvvRyD7724r60PTemxvjbe7D'
        b'MYEhuYjLQY3N2XkulwYj7cPRYBHuY73DjfPBDYzF1R0siX7a56hH6b1DHRTYW/9IXF3AiqFI++rV/C1BuIb64Gp6CML1PUFX9SnQ03Af6F+nq4UAtA5XuXhohDrUE3ii'
        b'448Y86nXdlHJSaiI7qwSQacOXiNCCo2N00MUKZ26uLOs0mImAEWpAWqHBzrdgny8wKFOEMcpQQuXFif9743XlUD3UROEsFkJfZ6n/N4HK943WOO7B0x5BH6mz1qQngzJ'
        b'3L5j6c97b0WirxXTA07uk8gk5vLAM/xdWzO7aO6c5DlzZ5X0faX+ovfW6HytKaIz78e+RUcx7+mALh5MOvUcGkBF8Ney1pvWOMRj7Opac5WJ6N19buPbvbcx1dfGBC+S'
        b'e32w/Jor8mh1fPH8BWV9ju9n/2XvsCf4YI+lZN1mW0HEWuEgPki7dXU2cigLpCKXcHS/z2jyq94BT/YBDi/xnbPpGwCxZ+/0DmBaINWqgXVqqjL7IV9d9RoH8cBTF6Zn'
        b'62FdW/veN0/voGcGDmonSKutKhCiOj63aG5G38Ml/rp3wOk+wILnYS2f5LQlwb9OVq2On9s3iGJX3+0d4hwfxCE9hoRQx+f3DZy4VH7TO7hMH7jhgmsliIO15CCKuDiE'
        b'wByFpUWFfe/hb3sHmeMDGUnpGZWNxRM1fZ6393uHkd9JAbpSKSJPE18gch0/q6AgN1ufWTJ34XegkL/vHXahD/ZfusIOlPF16gygCJlmaE0tlf8cPm27p9DwQKgWZGeU'
        b'kADvWnXm/NladWFRdn66vqAkXasmPcidu0ijpd5FGQRVqsU6H1XbnIJ8WDVCdRnp+dl5i4Tr4tJZ/tmSonR9cfrskuwC+ixAoBaAeouD+NbWWU0k8JUQLqSvk/dB7wM4'
        b'3zeAI/zIt6AOCQhpogvQ5IAx7Ouk/a53mIt8MCd2nTRBZ9Op0ztPv2XrMwpg+OfoMwlNJ0jUZyL7Xu/tWOJrR/8Sys8FNREmjydYY+vDChE7/KfeARk6qbkYwoWephTA'
        b'mDstPv66Rl8JwIe9gy4PJHGdpI24mKuJkaoL8yDbIb5tkPkiOIeeOuXF0e1C6uxVN5hcCydtybYH/EmbIDWQ52XUiU9G3jTQdDkxjQQ1sawfcj6cViS4YBMzlU9+EYSp'
        b'ToNZz8KWTqOw/5R0cSlJusR4prYG4l5oJx8C9e7ZT2Z62ikKJZ9dEys1S0T/CAY02DjqoEdcQxsGdVUm/d7peZaI0Yxnxa35EmELoOcpIlsONknnHlU3xdXnfNN1byzA'
        b'3ciuovtjDNnSrWI6PV04O9mF8kiJ4eERDngK0SxhIEMjupPQAxs9NEV4sOc+Rwc0hYTk5b2OcNSO5W2LjI7bo70BreZag6G+S1t6MBzQ5/SakT1tP1GDBt0w8qi6GKcm'
        b'+7CmE2GWeXHFExZom5KLpqkgkUPTb+p65KJZSiZYpaTUKCUlNikamcSjDDBIyUV7lJTallRdLE+h/oYnuWixUnQarARjkSrQIGUPZUXUsZMPXNnJt6L6HsLN/gokbxFr'
        b'D9nlUiilXGRqH2JtyLpH3/iO0Tq6p9Leo3soQxQShYx+m9iCnkRHQ1eF1Sk1OcRn/HKwPk9HA+y3S5iEahm6WoQuBGw3eZ2OHWT/sXO7iec2M/TDgRJe6vtwoEy8ltOP'
        b'CArXQXwQr4BnFW6ukhU+GFgWzIfySigLoQFtOT6MV0FpKH2ChPlQlCmFEB9lYXwUJdHRnqguqJtnAS3auxcm9V/MxHWeEFMD9cIwsGQ/2cBVkeAFEt5H8aVUfvcE+z7U'
        b'C5c1Nt5kJd9zG9HV5kigGfw3OBxeJ41Ylm6ieitReOvoSqHI3usGic+RSvzA3OAe4PT9mHzfFJGtPnNej9D6/CE3URgYwfYKze2F1lfBamTv9TX3WF+Ak5nXe6OTWpMo'
        b'nfZRj66YLPdtfuziUdPQnU5/i3eoH8xuTJLSlzY/qF0ZogiVUuRvYYiVfWGIO7+9hyJT9C7yAN8tPdPp++SIdAJg8awA9d1aIXGMF88WSOg1uZKukNinO2XCPhbk5cuD'
        b'iPcf2/mdu4dJ/mJqDYklUN4ZnGFsl1aODXyct5mF0/PCmQQaMMZ7VI9SeBBn2ryLUvhw+2hyNYYk1CmEzA+wo7o6UIe9hxFC/UDQRx/hYSUx8fwen2wjhu5S0v/dGCsd'
        b'Xni+Z9wJEXHH54jjP5Pd8YZ8GfGI31wO6AlYdzHK50wdTdeIQLMbmTlMk9djVaIPEFd9L5AjEoReLlWSUyFECtnFrSTu31Vel3PyIT+v4x35op2HdXZbY5Cc8LZazjQk'
        b'9dRqp81psgIJIvtCjplwQai6raZuJvluhsNV8wj5RkbfO/5tY0Kf0mtUXWWbTj8YiiidONIpBlCpIJEVR9+u84kGvQRCGQ4PrZOIAw4sVy58GlAhId4gxNvDRQjaajtu'
        b'8XFgdAftS/SxYNyBW7QAag6+HJSH71gCGHGs+N+xgw1gxDCt9FdyRFYmIf4exNuDfAiQDyFslnzyj1cRtsr3O6IqI1/ulQHLjeSjgM3K6PFbBYmI5Y50D6gM4qP5GCiX'
        b'm4P4WL6/+LXfID6OXJOIWdQrJIgfRPODaT4E8kNofijNh0J+GM2raV4J+eE0P4LmwyA/kuZH0bwK8qNpfgzNhwstqpTwY/l4aEuEOaiSMUc0MTvYsgi4Fwmt1/AJcKcf'
        b'9ITlE3ktXEfS6yReB9dR/BQx3hcJONL5yUQV9DOC9jTKHe2Occe6+7vjKmNo/K3gsui9QXtj+dQ2lp9KoMBoSGgELhJzLIZ8XpCfCPemUTiT+Mm0PJZPo7R/ukdJ8M/r'
        b'p+BhCz1sgUbm4TJnebjsuR5ubjH8L/Fws7M8klmZeo9kTm6uR5I5q9AjyS6Gq6wiSGZnZXgk+gK4KsyDR4oKICmeS26U5VIXMngju1Cj8nCzMj3cnFx7KqFmXDbUnVXk'
        b'4fKyPZy+wMMV5nm4IvhfPNc+kT4wuwweKIXGZPuWuzcSOnVHED8vIITvkvrioEsfGQddkD2+9aOlUr0rG64XNeLTBOGduKVAh9vySfTRzoCjNNqnLpseYMzTZufPy4I1'
        b'kENOf6LzuLVOyszEm8LRDXQYPWkZ9es/Sh1kn2rfRx9/avzE+Oof4yPjTVkma6W1XGt6vfwT43L6SVQJ09RuzpYfLB0mftMcPzMcnwlF57VZwilK9HQpx/TDz0nQZXR3'
        b'Oj0WuhJdqELnQzD5pBWAJyEHDnOrxw4WohmcmYwuid9G9n4YmY0hn0aOFslCX7aGOS8x9p2lFH4nE2fChmh/DAr84LCsc2va/leS9Pz9CYnwxCjfYz7I1wlVIh1hNgT8'
        b'/iQgrn+PLahQiPNLwAV+v1JBUSZE/Ia3sMaEED+d369UNAcDGgUDGikoGgVTNFKsD+7p27dSpqcguIP0LqJt4ufx9om5NPBgKjoshLBNStKRiLU05iuZ3dLCerQ5C52T'
        b'MHhHXSjeibegJ11EQS1Ez6GmXG/UQoJjBUnzxRPcObgNyG977oJ43LJAAYgqZdCz6EroIFXYqgJ6ivxPNXJm4UL6Ab+8TxQrGRrMBZ/GG/BhR1gY4EMzPUvO4MtpeBt9'
        b'Y3VQMHNjPMyE0Widt7yBcREuNjUmLjD6PODiPnzG71h5ELOoOGiNQ0pDtigy1qvRqdzs/FwtbtOwTKiew2dWq11quDc0FT2XmEVOnuM9aXpLSgrabMxlRqCbEnQf3cV7'
        b'aIQatEkzI1FPDh+35dMQ8uKZ9XhdUjxuNqPnkxNIVF6bRoE74tJpp3Kh5825uDU7L1nOyPtzWnREha+jqy76Ibs2vFOfSMY5CW6i57iYxonjQ1wz4NaoLHQqUZgBLxzX'
        b'NC8kAmZePP1oXWG80B60JUvCDEVbwtDt7FQKORTtaHCswtdhmjdIGRYdJJFpD6KjNADyMnQG3/b/emMdPFkSDxPXqtXmlwpB8rPggbP4VnJRVmd0SnxKosTtaRIXIXR4'
        b'bzXejY/j87libHm8LQ96EpUpwUeL8SUhSPJh8hWZzlFL6gzn79cZEhKAQ9vw6SqOfELuQegEqPi6i5xNHbRiDd4zDy4ahiUx+dx6Ol14Tz0hINuBwV+rX4VvoJZ6fN0p'
        b'Z8IGceggujGTBjQeVFzvgFIAiK4u0s6Pz0mCeQdSSKEVxXc2Sc6gPfhOCFMM80KkmJVT8LVEMhYwNq3JuL04Ph4wqzlZLw4MuoZ2C9iFNqDzwYwTH3aRs/ZR6PC4UPKh'
        b'AQe+vRK11duVK/Gtdegcw/RPk6DNFdgtNP4uOofOQiV7cCv5sEmSDgZYxkSifRIEdHUPRfivl8mYl4bEkO9QalvmTGZcNBQOPosuiZ+UHDGKfJ3lebzPEvvMRJmDfLzp'
        b'tb/mlhZl6/HjEZ8NsLX8+RLv+NVX8jcbN72LT8a8tHDEriHDVW9u6VeU+fuILyKOvRS1mhn72psj/lCU9pulpb+Zcevnc4IXHa1f8NJrF+pHvxaf+2/+9KIF1/b/Lpcf'
        b'/MFTvx937auTUeW//KRtrOuLS+XJri/Pr375dnTxPxSnk3+7IcF14ImWV2ovdCy4Ix086kbjB55Dr330844XBh+uOx5+uezirD/8ru5i7h1H4t6VU4403X47cjQ+fOh0'
        b'vnblyck58WHXh9X1y538S/fnZ94Muxj74KOol2+c/iz8yB/furhFp3/fWrqqPrVlj9ysevfW5nfHzXt/oavuD7Uni4f9XTN+3JKVkq8+Szl951XtD5ZOSNg/evmMlf/0'
        b'fL3sP5qwn93gy/4QG/mGJ3nmgqqTG4Z8Nj7rtTut654a8PzGe9veulJ39WcfTHypNax95kjN31v+9cK16vem/B/2vgMsqjP7+96ZAQaGJiBYETtDx95QRJEOUu1SHFAU'
        b'ARmKXVSUDhZAECwoihURBCygm3PSNjE9m2KSzaaZsul9k0383jIzdDT57/97vud7Vh5h4N773ree95zznvP77XW/ZW6zOf/KtQ9WeRzZ/FvE+8UzLCrfury66Nklf6ku'
        b'dvpdL2JCoFnEiQfS8TPz7wWOUY7l3AfXsGI4Vszvshlqd8JQqGRgyetGj3Ehoq1Qw9ZEMRSuSIi0OxzL+RdaxuARDZAzXEvuikowOjGdTZhCIo3w9hQozDI1MUrDFjW2'
        b'ppvoC1abpOFkSbekc7rRBdhM8X9uYjnH/1k7jLM3XIJjWIt3rDjTk469oRmr2HUjKB21g85FJ6JDKDGPVbBBgqdnJHGIpGI4sQgKzTKxNRVbMsh7FTZkxR2VrMuUcZTp'
        b'Kwutu5BPjAt0xpwJ7FG9GVDCeSFMsaMryyaeMkqnCSq2rm4BLkFe0KQvSLaIc/CQNQcsOg8X4SCcTSVLsIBIC1Jp2UyRrJiytel0L5s8NjOAyBoo8OO8VLBvQjpj/TiG'
        b'lSp1pvGmDGwzgwIoMpObGGGjWSZZjNiatYnUPUgmpOnDjS14k2kprmTnu+zojMWB7qKgv0zE3fZ4CfME1rBJWAmtWOgLl2PxKlE3doiLUhIZqgbZorKN4CDeoZwWhXDJ'
        b'NwjIjufiH0TZSltkWURNYkNbgfnLPfEcY76gLEaFgUTR8ZSQv5+z5Z1bAWfStZyezqkmXBRYB8pMomM4UHfjNjwIha50eukJ+jES2GM6Rk9DKrodqpcDkW7kukaa6QmK'
        b'EAmW69mkU63F1xpva3jCQuiWTEQN2SihhUi8UXhGhs3QJGfVmLWMzKNOQjHGJrYJL0kX2sERVg0DH6IyUvCu4kDST34SbIqzIaL9EJ+fxyTSEXCGIYI7uwQHhjDuVlEY'
        b'hjWyTT7QwFuai9f8KfWnbi8xDV8DTdIg3D+F3TAEj8/GQxGUB8SZqBMBUjINCyRE4l2ES4xDJGEJVJKr/k5+WEL6/grZ0WdI4uCGEwOxssU6O93VPEqECue9yHv8yLR0'
        b'sNfD3bbRXHW9PlVC7gt2gnxXjVj326lH+qNNTy94EL9lbyQ0eU1nNdHBv1lAgxQLt8PtdArBCLVkCuynq6KbHg75UOrKPMHBcGS51gx1JBtM8VgjOIF78FY6w7rLc8Yr'
        b'Eue+nyd6el6gUl8IFAygCWvwCJvbWDB4ZyclLRxc0w8rrQGUek5lACt4Aa/O5VODctKeTuZP6BPLV4p3ZuHevpXs/zzJKvMPMGU9ubey7mEkyimvqkQmDqE4p+SntThE'
        b'YizKuLFPYzQlVgxJexjF7SKfaQKescRISpRtiX6XiFB6Kqbf5TfmER7cQwnnrmBuBxhp0pe0IcMy6jRLo6pNGuVHvadYE5uui/7VV69ZF78xvifQisGjwZ6FiJpC00Lp'
        b'N1YIe1EY/ZX5ZBaLXfurrR8T49luVK19t+5RaUoNonmbBgJf1Tm7u7/qkb3cGkdu+MBe6V90x8H2jM5Em+LA62enwUDpwQT7aEGvGl4aRbQmWCl6QIqc33QVceorwClR'
        b'3Vm3P0EMyw6HB3g7tdj4220jWGQTjWv6U0S067QjvCYjPSUhYYB3SnXvZOyn5H5n8oAdjbXvjLCi9WDRyX+m0Q+JQtDXVcCBRSEkJmjCDjbSMA/S4/HJNFNE9WeocO8Z'
        b'R3dZwwNUwlBXCRYDReMf1lI4OF2A4B95d84j4Rob6145sX9c4+4v1ryXCVMd9B91xuqw4rmXQKCZKzvErfrb2eE7hQMWhZ3CTnFpJ+5St8J0hxQ6L4G805ct7fo2J/a2'
        b'BPHRKV3fyxD7gBek/7rxBnWPpFDbqdelZCSpGLtrfBpDF7eLXRtL4y/6LEtHvrQgKT6WRiLZLWQpJ3QQNci4LHxPAxSuieNJ7BtZV4MhHhMTkZYRHxPDuWfj7Rw2pCSn'
        b'p6yhfLQOdkmJcWmxpHAaq6XF4O2XGDC912qmQPmaQ32OP8hjwLZ0Ca16OJh6TMyi2CQ1qWFv5D+WLSV0+Sf2GmJpcGK5j7lETXXdXSn4z5in4+TvPZbwD6KkyvPF1oZX'
        b'lSLT73asS9WqEcOxMqSbGoE5WKo9belxviNLWBvP8c4Y7+WuHl+2W8d121HUa5KiWdd2Hl/QAvojihW1+JqdOGYUQN9cpjmx7rFtZgvfGnfZODNoMM5EcVAPPyoedNRo'
        b'S6yNWEGp7MhlahkRU+BwADWwrkwXiVqObSZucFT9HyKY7eW60y7MXh5g6lSZDkWLOnVBXlfqV8kPdPB3ggsR3C1F/xASyHiiSjYTLTpfMRMvzk5s+PCwRE3Pbvb/uuGf'
        b'MS4Wn8bcjftHrL2FMjaQOX4/j/kkJjnh85iCtf6x8oR/3BWEv0+vbpePWbKHWDWu5DnSQdmhPV/P9NBgrO+hikZDPTOYVsRMVThAB1FJ+6JFuuIPTYzUaKXEsVNh1U0z'
        b'PAu3yFSbu/ORXMNk3qk18866r3k3mpG9PnzukUK07+vE7h+Q9rXzNjYdY8h0HNbvdPykq6s4w4eWANch749OSMdgZziJ1WRGXh1uMoeYJaeUEuZctFJhNp2uoiAz84Ny'
        b'EeohF64wN9I6R3/6HLkyGevwggjNplCQ2O5oL2EkrpXv5m1Y6zvVbE0gmRHr3zsXv27turVJa/3XBMcGx4rfDt0wZP2Q8KUfu+lNTm0VhCd8DXe8a6E9x+zqPO93gAx1'
        b'3d3/KFkbG5nLtlr3PUrat/U/Gl2zz8kwmPU7DN+Zd1Wn+3nff4DenKskD13gRCQ/sLGQqam9G1FU9U+yFu/GrUsw9pzCjmEsv5aA2SQilimTswqq4bIAZQNZob1M0BUb'
        b'ew1Vj4iK/iW2fa8TDRZa0Y+A7o/Jm75jdL/j8Z7pQCco3UM5/qxe0udY9N4eZcERiXHSJTI1/XNTY3NALD0LM5MaCDJ7UXl8V6dO1zvE4IQwUEc69rLbeNzIo291tPxx'
        b'/Xbi340HshF7BG7+R3uxzxldeGacqKb+sI8LohxjKc/93bj1Cevo0eJdwVsQ7L6Unpj8DdldqHAaihXzsHDxMifquJF5itBiAcXp9MAqFErs+pnrO6Cs7+kO17CMOY82'
        b'W2MZx4V11hfkeEsCR6EEDsYr+hlAkwFXgktvw5vHqj7yANLyJ/Y7gG8NOICad9HqdTtNHKHt/DiBnSbSk3pjZhloz+oluYOYWtLtxD5XL3coO2Ucljs8d0TCCN1Jo+LR'
        b'Txpp9JZVr7GfFMz2G8zG2iFdDsF8Q01XpmVQF9UcyMMKRRq2YIsZPTFhhzjmUBcA1yR4Ezq8M6grxMAeWthJji8WwQ2sVIbApYHPc3D/ZgW0bMXyDFohH5tQNVL4EzyQ'
        b'tVOAImNsZLjVfiFqbM7QJ38/AWelAhyEKi92UmgShY0KbKXnLC14FMupu68RrrHCNoqJ6nSRuvC2QqEA+9VQyRqZBlVrFbTpeAWL4YQAlWl4glNFnMM82KOmgIl4CC6H'
        b'CVAAB+AKO+YJNTCgfWfuNuGztPSAkQKrF16Qr6cnW7Sw0z7bBKiIDsmgEh/P4Um4BXeWsd7o0QHYmJ6G18J9HanLnJ9qHYBKwx0WK9h54Gw8PQ/boGEyHpjsJhNEPEHH'
        b'5Yox4/IwCvfpdpLKMFPGz6RHu4uXYPlk/3ADIRIr9bFl0pwMuiKwaPyOFdBMT8vcBXcowApe85tQA3s98QbSwC5XwdUfW1k7czbIKP2InduEFv05ruECO4VcsRL3BWjh'
        b'WYi66su4votd/SPtMZ/UIdxemTIbS5f4+lHVpyiI6TxhtGX6ySarluH+DErqi1VjoYHGPnS9j04Vqii5hmh6xxc7VnWBHKdz5CLcMsYmLN6UEUuKWYqteMuEPHPQBLLd'
        b'5HqYHYnH9bEkwmSRxTD5nDCssSNd34HH8Yr32s2GCTabjLBdP0sOBYYhxtCIe7HODTu2KUdh3mwXPKoPRxYooXnuFKwaApXYAYczaBD2NCiCOj3cjbtNBHe5FBojydxr'
        b'gKblWK4P+ZgL5Q6Qgx1YCiURwxN3kqmTPRw61o8ZDm3kyX3QmrANc6Tu9qQaxaPw6kLLIDzgxCQB6+ZPVg0Tp0gEeWPwP8fUJ0YJ7KDfVO7WF59s56EmpZSlhLKYO47Y'
        b'Cg3YplhDZwM/eDf35Ry13t8vtB23RsgIoV1+clUabUSVoWBnTD5Erd4Ah+AS3sRa0R324JnZk0kBh2OgBS/h0ciJeHo5qXD24AjYE09WfMOytXgSrxusg3bzLTLcxyIK'
        b'4CqWze+rnr7O/noWg2n4Cvnaj6VKOK+kR58XDcl0vgqVEUqRyRLYi5eIdkwpfUtdscTPicgDMsw2cjw2X+YGRcsYSS6c2zEOKicHDMyS240jt0BpnAj1EzKozYT1qWQf'
        b'GeBsePGSGP3Ok+HZ60jlGDvHfjimZqr8/ixRkECJuCALLmd40xpVLYfrjr6k+4qC+DpwdXP293MO4xEYXUMM+Fk5MfBS6fpfHOYcJRG2RJhtsXTNiKAKAVRv5EfxfqGa'
        b'WAxmNtSMJ+ahb2AIa6hLqDwTW0N9/YOCnZyDIzmzcJdAACaCsShsEJwhm+dNNglO+0iYfeu2aF+Cx+wpZCdjhD5SMujZAfy0Bss2Ssm+2iiBvES4wGbJRjiRGh6iDILi'
        b'EIsZlEp4SR8BJgKZ9RcgmwzvISxaaUfM1OtQ5zsa7viOngxXZAJZoLstoMqJCGo6yMMcoIqIxmYzQzk2mWFzOpGlezZliIKVWhpCFzPv7Uav4I1x4VRwSYmkuySQaXg7'
        b'i0ULrsO6jQFKZ2YsB5M62StXGndTHaTCKjs5mcOlizl98QknaAuH4ggsjgwiPSgKeg4i0R3yoIBHrbSRTjisyDSFk5EieVcFkSt4Gk+yepgshorgsaS+18hGYyBI8LLo'
        b'nGihHJTBk5jIWwoDyUMzLCCbWNVpqxlq1Tg4ZaKNrMGOqY6ioFguwQYLGSvSMm6V2rb7Sa4H7OU7U3IUPRWdrdQciu7Gm2z/ccFqvYU0PCyAw/DbinBqMzEF6cvigldp'
        b'gzcmwym4IBOMzaWD/eE8y26Ac3AJLowaRya8klntFICfn1XqCRMgWy8hBa+xqQDtSxbpRDmeHEqZnislUD58GO+l0ylzHPlC8cS9wXqC8VqpGZy1YjunCNfx7Gqphn6A'
        b'cg9MwxzO7wQVeBULnYPZcaL+KgnkZA2Ga848euY8HoV9Cx2xkJ27yqaJcH75ZtZiyoJQRZ6soMtcylp8ehq28KoUYxXcwmZvzlfNyaox14aFZsRv2aipZjCZtXRBEwO5'
        b'Rk8YDYf1DOFIWgb1tZJtoIwIm0JuhlPqAto7Kyf16J9g2G2AB+DUIk5+dYvI7w56GK50hvNj9QXDmRKywhqgVqnPts40KBO1Wgpe8yRqyhgv1j1SKPTTqimYPYioKd5Q'
        b'zK5Yz8VmrZqyDO5QLaXOmF2BnFTcr1FT4EAIUVOwIJ1NEjjklqJRU/RmECUljpTFwgcuQnmKVkc5t5EI2LCQpJ8fPHjwpatm585sSJkz2EVgf4ww1eN/jHpdGDHaVkh8'
        b'Xj9eot5KnjY5Mdg7/EaJ5XzzL76cOce29PXVV764+tPt6xWOY8e8kTcqW6j926Lxih98E6ZmvrHAc/j5EUvTsvPyBr3r+XTW5xO/FnPak1/wevGVyCurOz678OV7B62X'
        b'H6qRX3R4rDaqWU85tuB6e6WB1de+uQtiP5roF+Jo6Pqyu6H/vItXz1n9/KDjL/aWVvNvCPcax1g25xsW5bwM9usHf4Zvy6ysHSw/ktyrMpz2zIirJ1vL99nfEd99/9yT'
        b'T4349HH/d+pKyiN9V1laf7O8otYww3+V46dDP1v09uRBn1+TP7viw58CN9dfXLF02THLT1tf2TRt6WyX5d+1zvx41d+r7C+a73jC4/mO1cILQbVfLftX+YX34583sZxd'
        b'/ubUMVKbqpIZmUNj7nzQXpB4/W79aJOLbzx+c+O+vzetOHdKgm8+nTLT5ceg8nb5wbb9rz295NOZGcO2fT/7xVWlCV8nHzz4W+FvXkkplnvjFv2a3hj2++PJ+rlzX97/'
        b'U+5b3wW/lGr99djk1z1K07MuP/Psc6v+VgG/75m99a03Y77/ZLNeUmb+XcvcjWn1yp9+MD22XKlXP7RpbYoblt16Tbnu7++nX05u+NR42I5Z0efjZ32x7ck3Js/99kD4'
        b'Xbsflr6yJnrG36R3Py6pmpH+45q5ddt+b9/24jPvbEOnV58LuRli9vbs90Z8V3Bxf6LdXAhyfPcB3nzK/d/vJl859OnOy+5P2oR/JDp8+dJYx41Lx99+q9Dr8t5vyxb+'
        b'7cO84z89MenohHM3rphl+5ouHv/92tTvDH8Y/dqg19x9Jiy6v2LviuOeH9w3urXQZuyOOIvnAw+/9fu7M88+9b3qbxdXfhgRsPf1VS2BG0bevd0kmfzRbpMRp14oai63'
        b'OvvR9QlblCtzf3l7yttvB/2yfMq7D/QW2UqmvjpXOZ7HXORupax02oCLpUR0aGIu4Mw8ZmFihSWeCwhxJgpfO4+UsYM6HsmyPwAvUhk6DI5yIboEeYgDMTtyrXqxrUM7'
        b'XpHJ8Tx2sCAJy6jZ2kA3OAaXyBKBFknmptUsVmMbHI7QinWivezTynU8qmQGKpZkwmGs295dtuPxIN6qW9SG0MYQrYFqXRhRCNzmrboetZ4buIz1JAvabA2ceAjJBSJm'
        b'Tjk6uCixwInKQMNlRPSsGM24YybASTzuSNn18p2IiIUSycJpzpaTWeAS0eULsEQe24WmhlHUWEo4Qc1VQ6ymQR9U4wrp1L2tYZ++MCpAhse9IJ+3rY5Iy7OOrAICeckl'
        b'CRxbPzkYmlnk0pQY8y7hQzZw0HnnWOZodldBjhqK5ZtMsElNg/x4OA/esu4W0YMt+nAb6kJ47MYJ2D0Lat0duzuRLfykcHJ0AHMyp5OizqfgsQCt5zqEjLi+MAhzpVCU'
        b'6ceCUZLw1mqiCecB0fEKXJ0ZIaKBYBYiXWchZwOyiRhXex1DnIixRVRlvGJJLivwtgTb8PA43uiTWZCj1Y6q1mm1o6F2rNGuyRlLoKzLngcdnIGGWAsSso32EU8mhzI2'
        b'npnE1mjtGowD59fayKAhnW1O58mWXaNxk5iRjW6A2BKixFQy7zxWQjvs7R7LFDRSF81kCbvTJ7CN+qhJ9xAb0kHHusbYEDvnEo/guihZgTXQSsbc31HHq5ctTcmYz66H'
        b'SOEgUfYpnZ0TeXcJ6QVFsgSrsW4wY/GBhmA4ZQslXTfpsTFsxqYH4NmtcLybOhNDJhqLK69dDle0Cg0ZoQ6tRhNJliiNEhqPDROz6LlFfwqNZC4P66vB6qWkgl3Dmaxx'
        b'/+SZMgvM3cLcrwEGNOSpf9erPRzv5Y7aRcQJs5M7lO4BgX64B08QCRQmOmDNMr7k8skqOhPgZE9p+rAFyzRUfZ5zlMb/k2Ac5Yj/RaTX/0Fo0D2zHkCXzOf2IvnWy+c2'
        b'iXqG5YyjxpzxIllQKDcJB3Ez0sC5DSPX6VXqO6NgcRSZXEY+yzQEyqb8v0RfU4KchRJZMLpAc4mR1EpDtcwh4uTkiin7SQOUTEnZNCzJSEJTjPlXJ4qthJQgYT/5F00j'
        b'ppw6xpqyeMagzovXo9ld45F4rBDLCLOk32xYKFL8Zl0YQ5cEq04f4+D/a6OnjWay0OV60RoydiBeKUtdSBNzdcaRXx36dXW+4dWNAHGgTlKKLL8seIAzV3rqKjLI3oef'
        b'uWrZD9+U9BGeMD8hnZIcxiYlMUDSLuTBpFKJtDaxSd1wSjmklUrFEfti7ZLjs3oVysNa7GNiFm9M90tOiImxi0tKWbNB6aLBlNUGPGSo4xMykmjUwZaUDLusWM68qEqk'
        b'ZIm9iY27ViIxmd2YwDLyNUmc8Wqe2clRBO0oNpJdokr96LyGFEhglp0fCzwg80+dSHFbyXtoEEKs3ZoMdXrKRl6srml+qpgYJYWZ6TdWg/SPtj/ox8Rku8zpLpQv24t0'
        b'YxbtzPR1sem62naGg/RZoqZtDEyWRS7xoAtSAIWW7dZF2hzZtWkpGakMZK7PEknT0xPXZCTFpvGwEg3HPcdHUNvZ0+x0J9IF5LUMtmRLKvk1Pn2Ni5INQj9hJbRD0+O1'
        b'46IZdxZUltyTwFIz+qoUlqGbSmGI+yqz2wAMQACpzWDt7qE3DOYOkyLI3qTx0M+BUuqkN00SM8bRHakRjkUroEDdM7FBk9UAdVDP3D1wBLOhiPs2oRzKBTu5lDpRb24i'
        b'BsgwW1/L8Zt24JUw2AeXF0DZCi+/dGJ310Kj3CPYaSTWYC3WLIRbo7bCBXM3qIhijidHcz/hgJuzvhAT4yBbN1rgXomrWOfJrP5wStlbugQPTKb6K9nHDYQx62V4EfeP'
        b'Z4/7ziQ6eMxhmeAZk/TTjKFC4l7D50R1GrnyTGjV+GeumuR4Guu9lPJV0wgrz0FTPL1szFd5xR074Peil9wwOPB1u1XTtg5bu+/Qi2ZPTswxc1L+9PwzN97Zm9MWJz1d'
        b'OGLFV/MVeyc4m0wfseX714vHubiX/upT8GDcuzd26j0f/tGI2pY606Lz1sbn7hvM+Oew4x/6KRVMQ8nEK0RH6BoPvmUXs06SiZJFx2bRmMAAPIdt9OSesfieGMLUDcgf'
        b'HvVoJ71YvV2jbsjwFtN4sWGkuxoLN1FHr7O91s81CA9IoXGNhkRyWxZc1Foveu6J3HYJ3MGJjvcOXagJkoebqSxO/pI1tjJVZqJjChaOhhO+cJmHyA/HA0xNjcJbUMEV'
        b'eyyAY5z+MgFOamglMTuZ2lPjLXowMQZDOw+xL/QbrtNI8QRe7x5hnwpH2G1ZExb0UEmL/Wd3KqSwb4r29O1hYSOGND2PLUymg9j3pYPsEmZQvYHqE0SvkFJdg2oZPeIG'
        b'dAV1Z2i07r5h9xFAYt1944wnv56mG6ddXxtntvCuRf+xC7o60CBQsp9Ekw1FB0ugzVbtL3xQmiftN1dVu2v+LOtj1wyPT9bghnZHKs9Q8100nskxInS9vfwWhHdBH+9v'
        b'64mPS1yjjl6TlEhK4bS6WkSmBIqguGadC7vDxZt+X8Bu6w/UvEupmv6YxQIQnXQRiBRpVx3PqpmSpqJ/IEK9T6GrAWnvtw4uiyIDYxgKW0ZqUkqsStt6bYf0WSiF89Sh'
        b'qtH9QBN9q85ITOdQ6bpK9b0VPLRWCxZExDj92Ucj//Sjfov/7KPzly7/029duPDPP+r1Zx9d6j3pzz86OcauH4XpER6e0k8MqF8CZ3Xh6ku8ysnOQTP9HboFknaPdGVR'
        b'cH3rG/3Fry5Ki2Wg1Z1z+I+Eqi6hGiqXCpmTXdy6rRYWYsvBYvlyIi/MTIz9cz3lFRHZRxU6abepjOH14MstUTWAUiUT+kqwtuas2rvn6vOzfdNNSSuUMfxsH27OxTy1'
        b'QuKD16iLSICqndO5CnYSzq3BZje3cD83PUHiJ+BxPOjCT9XvYIu7Y7ALUQhsoAAqxADDkeyZrbBfcAz2lwgSopwVwB5xBlyAg+yZVZincgz2I4/gie2QJ85Zh/VKngcN'
        b'NzzI9ksP0VwjsUlPkA4TPfBsOD8dyYFreJpcbEwfYoNtZEfHcnH0bM0h5tloKFZPSpMI4i7ckyJAG57E0+x1zkHLiIJoZryU7FwSPCs6QMlgHihQR3SUXDw81psHBMxZ'
        b'xo4hsCQimJ52uG2i5x0CFPkZs/OobZiNDaxuUDJPV7kTwM9uRuI+O1Y3KE3VVW4x5LIiFy50plXYvkJbhfThvMdLnLGN1zp0O630XDjCHhgaiZcUmYaJcJAMndRQdLWy'
        b'5M1sgXNwUmGSlgy3zYjS7CTOM8FsfubUBq1Au+eaYtRqU1GQGovzEmIzlpBLXuuhLIAqoXDAMZwF39ID4iWYJ+ApOLSdqL1FpHPboQxqIsgvZdiOdXiI6L1l0G6hh+Vx'
        b'eibkWxDsw6I5dpZEgbMwg3PCRKWEHx81Eb2xkHUMdpCHtD1zah07pYRK2I1XeNcUheq6hnT9BaWUN+qOtR973BGua5+em87mgw9el7NHF5vpnsT2+fwxmn53lPQSnnLQ'
        b'9NJgLEj84K9vC+pvyPWiZ20jX/QIRjcrg69/Ov7KlN0VZy/nPP7k48rr3tamX0eMvvVtjLvbjJHrR1cV7z4oTZU//vjdu+IMPcsH40Yu37Ll9w7XN6ucl0WF7Tzk+Jl9'
        b'4aGLkDFu8MQXDo3/OTDq1RmW7dYzLJ0zfolaevhN6/zZJSNal79p+GX8h8V/kX0zJXTtiyu88yf4Bfy+rWaY7W82p4a9tHbegiUNxlfOXZo8MTmxcWjTV43NY6txbszH'
        b'p//1zskN6Q/GHN036sP7uVubbHIv3Kpd/96H+2DU9k1Tru5OW3fyuU+TPzFJ33Jz5FbFquJfGl97e1P8g/tzhycSc+4b211vhu14YHbPctmBWwqlFXPueoRjI/fmewaz'
        b'ZEbmy5+IN9hVAz9r5savJ2PV6crfh3U8E7LFAq85sqw9aIJmrowbO0kN5kAtU6mHQJ03i9yVYB4UEBuAGEnMKxou4h6KCkDjBShTe46Ie5ckMxV90MZVPFkWKrfr8mWj'
        b'p3Gv6AE6G6lyj41wg6eJMvVehW3c63ibiJUOR38sVhkFUN1ZjoUS2A3E9KBHCyuGr1UrsEUURDiEl7BQwHM+61hDoYCIKShMnUoWF5EGBzCXvAxaIJ/VyQGuUBdp6lR9'
        b'crVhHF0KB7dACXfwHsbiLfQaPTRvNsZ8AQ8FJTHf67RoslAKiSTL756QKl1ILD9e8lA4j2fUmab04eylcFbAamIi7GZ2hx1c8FNDEcOQgCa8SsQLXoPTW/kpSUfsNvKc'
        b'HnnuFNyAegFrFiXxU5KjUI51RIIQkS0mD4cGAY/hGbzIajuSLN6j6sxN9H25kAuVxGKevpyVGIS34TS5RN42hLS3QsCCHR4s/3I8WWmn1JSuPhf297K7BkNNP/mXA0RO'
        b'y9REwWbmSVTf5kkMNUioq5ISeVNHKXd5SpiZov0yZrmRRhKta1L3n5g1cnHroO5B0OSNwVrYFJYuadxVKU9L6G7ViNo2JOpsmQRdXiPl6XlsAIPmsW7B2L3rQUqXCBqW'
        b't2ClTQ8Yqnuy6BC/4HuK6AWRYWHewQv8vMM54KYOnuqeIjU2MVmT9MgyL+8ZdWYFanI06c09EjVju8NYMVQr6tVkFhprFe+gYf8vudbTXKn5KNUAz8kNzKV07E2lpnpD'
        b'PCXk0yOjYUrMzY0lppRWTTZts1y0GikXM9gZyXVhVI90BZEY53um+MgSI9d2Cws21vxUO4jdOdZUEpWLylXlppLXyFSGKvcEQTWJfVaoJicI5Df62YTiRqmmaf4+nTJ+'
        b'sc+DKOeXag77bKXyoIxf7PNgladqvsqLfbZW2aiGqIbWKCh7W65+gqgaphqeI6egmmUGZaJqQZlxmbzMgn6pRhQbqBbmUgwvfWIK26lGM0wqA8aKNpbha42nrG70uTJF'
        b'mSRBQp6yJP/NyywS+W8WpDSLMsMyowSZylulJOUtovhgtMRcw1yTXItcqwS5ykHlyEo2ZLG4+iw2d1CCvspJ5ZwjpyCeMmG5gkVX+9yzoItgAaN7YGhsCfFpv0zqppD2'
        b'vkFDWtb1pl9ciHY7K1GdMkudrmI/J7m5TZo0iyrJszarVbPownBxc3Mn/4n6PfmeLDgkLOiezNfPx/eeLDLMZ/E9yULve4b0ZdEhwYHLiOwyEBhyHDVH7xlyXo5E8lEv'
        b'gRjV6j/yQnf2Qr/g8Ig/+NTMe7LwhVHzf/Fal56eOsvVNSsry0WduNmZKv9pNF3VeY0mGdBlTcpGV1W8a4+3uhATwW2SCymZQXul+VCRYBgYsmB+YDSxAX6ZQKuzwMuP'
        b'vZv8XBy7hQqjMOr1VaeTQlzcppDvaVPpc8bhfsE+gd7RXvMjFvg+4qPuv0zvcd+CtBS12ovZHt0fCUxZG6Reyx50pw+a9WjLL8P6r+Avg/tsuFLRrRQ68L2L7fGHmf2U'
        b'1fPPM9mfB65V/9fcf3H8A31xz0AVT9TwpHQ2EGwo/yPpDb0w2fpKEmGWCXTAFcylYYB71LowwBq4lLjvsXMiSyB52WYOTyAhupk4cqJob/T4AAkk9+SU/jSdzNz+U6To'
        b'lw8HPe2+/l20zz56OkIpaZkH+aQe0/fOnC080S0lYaC3Kg34Trq4j+00TLunfkqhzyKCu+Uv6IaJ5vWz/AVBy8HJcdASjHS5CUb95iZoHZR7DPpwUPrx7N/ErfFd3JSc'
        b'TYefElHxOYBbMlxLjmuXyjgPmCahntX7Rme7HgvLzn6ht3Lg2+hieugdM+3sHdSJ9Mgpc7rLNIdHKJKvTzv7Bb4Pv1mzaunNTnYPe0//K9vO3i/iDz3hPsATjyoFaBE9'
        b'K92fB1jjxeLuHp6YreFR0iL59/ck3e/4Yz2nTWpaYkpaYvoWDr1r70B3UMpPRfdQh76dgg50Z6X30M3PgXqAHeiG5qB06TwVneYyycVtluaWvovpPEB1Y7dqSu388zT2'
        b'Z150fw3jQBGapvUBAsH7Z6Ka4UD02z3szGFW98x+tsj6hnTQZOb3W6dO7IZZOnrW3uAMFChBd4bexxE5/UeuMTo96pRnzlB2fh8fm04nlFpLNdYF6YKeIPcDD0AdqqSc'
        b'rNg0zXF/FyYI1jt24fHxtK0ZSV3Yy/osasH8CG+fkLBl0ZReJyTcO5ryq4SzWuqO2jmnWr+dxIUQ7x/GgaQBTdGOm9aC0riC+z6Z7nQPsyMHXkKn99ahh0xx6Pdsn41Q'
        b'Kl+nas7I1kPEOPDWaW9JTO4bu4CjYBCNUss2uy422c47MqwfN3eyXXhWYvrW+LQkNnDpA1SeC8R+1hJZMH7psUlb2IP9SziH/uesBr6DD0gnqged+Zoh0SF88BOnflqU'
        b'zkMVumBzd3u2GzZLv1KLldTrCIB0j0ZjUmunb49y+x4TDUlh53sZOWRcfFJK8lpa0gCucqrHyHupT+ZcffKAImjCC554OABL8IBUkOBp0T7DnAWzj8fCWTw2IQ6bWQKh'
        b'6SZP7p2scsU7ahMT6unZM5oBhtIwf3rAPGuDT1wStU6hCNvIVzPkywQTzJFg4WoXljdmHYcnA7qmhHH8Ujiwsn+YzSA9f4kwFfaaYg7kz2V1iJBBATbiWeYU1riErTYw'
        b'37e+ddQKKFSYpGm8yOuXZ4RRXbEA9uOFLuCpnZUgNSiYqcmRSTUxCaMIqvbOwZH29liARa5Y4ERxMzkuqLM+0TOPWIpw23wRq4mrPjZQxE+ZIA6FbAb4CVdV7CgiKYal'
        b'GXraOscYP2ExXWAoElBtMqkrBqivi38Q5pPWuoZhXmCorzQM8mkOHd6AM1vGwzXcK8AdmQIrRTytlPDjgmY4g3Uzsahr63H3RO5436+eMwPPd7Yf26MSLT79TlRTVntD'
        b'h5TxxY8ZgZv5wqzpGw9f+8Fh80+l7UarK4yUeY/brrDXj23/l/tvnpYdTu3T736+0O76uN2jv14Xs/ixU8EVzWbftj7TuKbZalJt2FD7v0LV+qmn8y9GTS4NmhNS/NoT'
        b'YNpU/3jI/tdXBX85c9PXu6a/sibSLOvqnX9OCndIaXxsQ/WMnck+vuvKr237a+32z9N2PdvwlTJ5S73rcP+J377uanzQ1eTxOUoTHsO7ByuhztHF2dcZDmITjVCuk7hB'
        b'SzgLqxiPR+IoiDG0RVGQQhqdnU+hjE3DpO5QPIIFuq6Fw3BbG1eBRzI0nlfMxXx2PQrPTe4BDzh+mAQrZuJ15gs2Dsej3BcM1ZhN40FucghluIqn7QJcsA3OdY/OXoq3'
        b'WYiFTGKtCMDmbT1i1mVyPIo5GnhCS+ppJXU/ldzd0YrX0ljELxbBJegCIUimVYMWRlCLITh4CStsJR6BYkcXS6ileI9dwR4VkMO8zFgLRwOhDsq6h7iPhWvcl5wLh5Px'
        b'MOkNtmCvketB4iI8t4y5WReR+XeWCIdA0hMCZMeJ7nhxezeMAaP/kbNMB1E3qz9Ta7uFaKSJQKUUBTLmWJWx/5Rc2FQiEUf0YxhpYNmCe0d5DmgjDRQs8icQ5YIGtO9a'
        b'bB9q3z0qupwGeksvmirCAwBgFetpseX6ep2OGtnlEZTt3rhw92ThvvPD7sko8ek9GeVA1dql3SNredwqDWO9Z6Ahzu5mlJpp9yxfQZdUz81SY41hasIhunPNEsweIXVe'
        b'yjpI9t65vszT+SoV4+rrwtGh2Z778PLpFLveVm6C3Syqds6K0UGYxPRx2O+kUZN0+Fo0YLJ3fGlP/kJO0kuN/U7lN512XLrGNHgko0ujLuuYbB9md3HKK/5sH4SzsWq7'
        b'hKSUWOp/sGPsqhoyyf4ibWKTu1G59eSp7a8W3YyRvohk0+M3c007Xce/upEHe/YTvUnuSVRRNbGzKzrJ8Hgb7OwZGzttGlMDx4QtcnFxGaPsR4Hl8RIsEjmWzqYu3Mu6'
        b'kjntJFesO6/3WZ7umU4WSc0U0MRydeeU7LMM+zDvRd70TMY7OjgyyMs7zMlOa+9w2s1+479Y6HH/tKspqTwUe4ASNvdlQvbDcTpAcfSfzsKkPTyQAajDfNPM6j5L05Jn'
        b'92Ur2pFe8Q4Lnh/Y2y7sO1r5EW1FLa8W7wod/TCdsJp5Q9cFMa/jGbd0TExwSjKVFAOEcW9O73w7o6mlfRSbREOnqYDQTd2EtJSNpKtUsf3EWydlcJfc2sTM+GTtzCdL'
        b'U0XjfuzXpCSrE0l30ZJIxyWyv5Je7rdivJiujgxl12ZqyJjj1sevSefyoG/TKTxkxjQ3dztOF8vbQ+vgpMEC1bSXeRbo2iRCsc9yEjLS2Fpjq50Tv/ZrP/JNaJZduMZe'
        b'05Ky04j0LeQtSUlk8cWmcauN39y3bFGrU9YkskHQWY+paSmUW532IulazWCThcCnfd+d2YXe0C6Y2JGxqalJiWtYRCI15Nl66hph3/faWaDhdu8kUKX7s509+a50sqO7'
        b'tJ19SGSYkg4G3a3t7L28g/tZhw5dUgamKR0eIZFBF941XyfqexAcDRQ2qjNi5X0asaM4zA1UrZzO7dSxI7mZCqdnMPNrTbT+5rsSxndh/NmULB4JNhzPxHDbFUvg0Epi'
        b'u0qMuCGnPw9atangjlAqEBM2D49yg+sSVpnqsGGWwVGKIF4BlyIYAQHWwHW42MPqhVPhGsMXWwMyKP/ocppDiYUaGgbK0BFhz4PIA5wdonyd/CP7N4A5sMwV7yWbBkHh'
        b'TjzFIojc8CTNuYX6rmagqzGLi8IybDJ51JctxjLN+zppbELtddgYSn1hlpsVNsKdxbzH28zxkC+UdJqYULAyI4tccdqKdwIYLJCzfwg1snkhengI9xmNHwrnjbS27Tao'
        b'gTOeuBtryLVTFrAP6iLgpCoU8r12wlHYAxfJ12lKYrFhMxyAs15xq6HAKy0xNHT96rTxK6FqwzpzAUs8RkBNQiT3SmQr8PgSrFRga6oxjc1rF11HWzKEDlLgnQg4E9Nv'
        b'1TB/KOR7wsE42NetQvvwFJbRzzSSLMYMc+0EuBQ6aAjkWfJ4ujPKcVDkrcg01ERpzbLIoChQeA73e+lcDcooDTpQakZGBB5INTHDQxGaDu/ihaCeB98tVk7+kVoUES2W'
        b'DuyGc3L2DlPMs8bLC3E3Q/KZBkfglhaiqU94JvpURLeRhCasxBbINfHB1qUMjzMO6ywDuhIZFcOlxWzGkFIDGKQJmUaH9dT+UGBB5vZZbIcCPBxGZl6BiHc2mfiMjcmg'
        b'wQ54EfbgiV5F+XZi4EdpSjRL4GXCPgWUWY3Hs4OhHs5YD5aS1RxEIVAK4QYjZCEjt9egD9glCdaSGV6E1+aQwdmDOaR7WUgfHIoTMDfMdJdxmIcNW3URKmftQETYOob6'
        b'Bvop/Z1dojCvV19pG2rSfbHoC3gswwIOxmItX1lNWDqLwlDE61EgilDfTo/Snyg7zN+K1Loa69kcHoY3t2p8SVC1aSHljrkEl1n0DaN+gcuL7HV8OZ1sOf7BlC+n2YCy'
        b'KdL/iX9/qlBPfZIYV5MHHwoK9Sh91c28ZeTs4MzDHV99ZGo+9f36F8fU/jPK67TziMSU8pXz3RMbD9y/+e9Dv4qv5g17J+Rk3Rsnsjf/eN+8eO39jukvHL/q9Ezt4wUF'
        b'CUsLvV6TfWim/CzGNyW02ChykJNyUvRzxcNa/h09tNFlyGuhpfveOHnuH3EbZr27a8zse+8Mf+3DWa/sSlgQX/Dh7qhLb6YnXPva4fTN6pJjniMiL91s2qV6/dzv3/w9'
        b'vHj4hZaCXwoXRb0icQn5fP9X/6gY+gOGKHHMBYM7v1ZODVo74W8Pdn82PWJj1MzlGU/U/drmGWzRtO1IS/2Lkvjc74a9vSzKJnbmp6MTX/i4+sREx9rqxdPrbg771/FV'
        b'F5p++n3GF3VfyZdWj1nx8+fvqd1/naK65bAl9Z66+tcJXx/JDwk/Pbfx2Jp74WEj7tvs2Pvt+p3vGf0+zzwke54Y/cL0EVXRMwPeFt8urLoIylU+HlV/zxv+7LEz1Vfb'
        b'51mmvpSjfmzUM2EO559QD/3tkyeuvrvy7jFX9ccbd54Z+vcHb011S4wf7DL2d8NfLk4Z2gENgaNerqmeFvL7rLE101oT39i1+IcfXZ+1uFL0mL2SM2/sgJNYp/GKrrLX'
        b'+ZSgEUvY9TRTqNa4q4ZDfhdCC31Plr0UOhJzuLsqcxbUi/M34BX23GglnmKzHyuwwbUzYhKKZvLou2urd8I1Iq26uYaMJjA/2zY4jKcZ+clIONuD/yQYGnnCeelMPMnx'
        b'EcTILiwry/Acc5f5Ll7YC75hCVyTyfHIfB4DeR1PbNMlQFEvXSZUSzJDcQ/zTlkTybV/JZQ4ciIOHnsJx+AWiw9cF7WVQuH6waVVuE8m6CdJxvjDYZ7qnQs5tgEMYUCy'
        b'OjxZdIW84dz7VjiYXNOSbtjgSZ33zQmvMoAFIv9vY31vAg/meVsGFTJsTh3PWm8hwds87R3OwzFHpTbtHVuzWLwk1LqHw81x5BYnOC8TZE4i3JyBl3iq+3XYP56ztHR6'
        b'7fDCWNlqaMXL3DW3R4JlzAuKB6Fe4wXFi3iKVTMFrpsGBPpBftdMtEq6gdNoRze4ru/qv4FT0bRiznI2fci+7w7nQ4guYbpQ6jEK67mHcDfWQi7PNIMiD87IcgnKMY/5'
        b'AEcuhpNQ6BrkrCSTgdTCQ2I3zFEpf+S8ZbP/nTi7OC1UZF5/rsNdwlwj0VjCUtMlxiJNZDeX6EvlooW5KUsop0nqlAHDiCWYU64L+klfk3huLh0iGUJ+0v/DWBq7Oflk'
        b'Jcr1TGkqmoQ5JiWmohUrnaac60u2junDpdYjn7oPf2R/vrG0I93DPB+907smix/pI2O8j2TxA9QvOK4/R2W28K19V1flIzS072CgadShRx15PLpESNDXhQVJB8S0z1HK'
        b'fonpZSSExScT+1T9MG8dcw1ozBFqjMaq7ZYGBQ5gcwwSOFdpd5vDOTjDk66oGtWogK48kD0g7QqX2HdPD8XrWO6oTy2FyyaDl5mxzdzHHm87+m4k9kLP/Zzs5m7LmUIQ'
        b'tlHQ6QMCJaIphWboYJhsss1SeindhchVl0yiAFUtc/WnUeTjVutNx+NQywpY7WZBiyYF2FKb5QgcwNN4loOH5RLBcAzL8UT387+1W5j1ZD9RIrytR+dejFPIfA/OFriR'
        b'6BltG6CGwVkKxIY6LsCdTLzKDt5i1Us5ACVRzeoEVw+8wpRkk+VwU2GYRiHhzguOc/CysYrjk5YosQNuyR2VDhRQZIuIu70dWDoKHMUquBxAN45gPUHfWuIIOcZ4Asp5'
        b'NkihyYZwLNbHahmN6qesUE3QzuPBCibjTbg1sxsG3XCs5gbCLWLxnYI7GzvtlhGYzV6Ip6Im48ExLB2jMxnjJN5gpa6xw/NYxxI9ms20WRwRuIfZk6FKihaJhxSMcZG8'
        b'0yFF5DbjbeiIh4t4p6t1BtVz2TnpatLf1eFQjGWRWIzlkUGiIA/BI9NFvDbLn3W/xKhEeHu1h0Rwi3GB6fEcaHLJ6LHCzzZFdEwktalW/I+rg32FEc4TRCEmxt9U30bo'
        b'Roasr53CdoKGDNmaLDRhvbBdVAkqcZ9kqLBXR4tMdMdPKSUmTV6dr0oLTEyO1xIjy5LoL73xesm3Vfo6dmSGrBhPTAzSHRGDTFLT+dmmoVbhxUM02yFADJs2E29gPuTP'
        b'xH2ZnosSNvml7UyG3SOF7ZPM4SqxC46wlk1MMRZkmdMFYXFMUqpkO29umLG1cHfjSmrVb1+/Ya1GMb4eBZe7IRRSdML48RSfEMpS2TwMc1glt+lqHW7w5PPw2nay5Z9f'
        b'Ry5tMiE6kJU420PNXpVuaSB8so45EJLqDIIFLX3kqXSagdVp9WHLcmaQE+PoQjRZYdXYTOaYgSCdIHrgwUSlyGZKNN7yUgdT3U6iEAUssLPF9j89VjlkrNKOiiyesFrU'
        b'EVin1Yh9wiqTb5e7DBNtRwBcVONROKPIxFYzCW3HDCgfy3pq/SQ4oUiLiZFSzwcxybBlIk9ha0ndQrNGWg3I0josYF04URPyHBlh5FYsHEVrEJq0XAhdB418XVUvhqMK'
        b'e2zf4eCIVwPJJPeXLCfrcC8rTo15C7HZ1R/byBU92Ctm+GPFMNIUVglfe8y1XdG5VlfjcTZcmaPhMOTA1c7uhyKbxDFtn+qpfUiLG96yiY8MUFtFWt1uO/HdM3c9wdNu'
        b'nMQ9Z9CoIYP0vJ+Q512xX7d93KAfhnx/1sHj+8aTl96yKv/RfenyvymirONDfxccFTYNy5Y5rfx5+MoVFd43Uj/KCv7J2DDis8AT3+2IPrHt1+Pq5K2r70a4+ma0bfE7'
        b'GPzD0S/1Fg3PrYmYeOHrVT/veHvvV0tHHqt4Y/y8fSnHjvqvNBqywtBCNWX1wtcK5+7/eO93ysA9x89a/N10m+niS1uClo188OKzSwzP16w38hlsNX6F/zMXLx+fNH7p'
        b'TGe3hMNp1iufHN7s8J3NgyCH1jiH8/4XpjX+bayDoUvk7lc/LD5qstFk6bpnE+RbPmvUfyPhwnsbawvmtMX98F7gUxkXEm6+Urf8wuWG84E+4TE+656OWrE+e6Rea/Fn'
        b'rRMqT3z6ZU3k3fSPfw6o/Xl4QVTtamnrsWGODT8/8/mB6zfej+lwfPXxrUsSAw5+vLVWz+Y3yRf2SR+vcvq9atiLV155zSrSYvvSa3cWtBW2TLkbePXb6MVFfw2vesf7'
        b'rPv9cLOXrkdWvRL52nM1m2XfyII/EptzFy09OPPYN8XuP3c07njaLdG2rGXicxH3F7bt/vLjwLCP/CY7H59k8G2e1cZfn3lva8H9DfPfel/53WLb+a/cO3nD8P5JN7O9'
        b'bx6f/Bfbv76uiizOuLPjdMXUL06+5BoAc2YpVn1Wb3qt9DHTx2xtEhJSJwSnG3xi6WkmXfPR4caxUWuT7777k9Xnn/575D2/W9+2bBqWvNbvxdMv1r72s4f40dURjpvj'
        b'j3/61MW341/41tZ+XorzDxm3LraHfW9Z+cHeCzc3PTn01rvLv0mc3vSOKmP73iefuFL58YHagmTbZ95+9vjlk18de+LBoa0vNGd8N2dCgte3/37spT2Hpxy6v/5YxMv/'
        b'WHr/TGJu3a/R2d88Hy2b7Fj/i0X74arXv9lc/0auTbF05hMhjfVvPnWvwW3e8kD3ed9tsTbbMfeTlBCHXW13OjYb/vZFxvPqXSmf3f/RX/jR6Nd/XHn5+KkTTx344Mkd'
        b'73z2/qvtn0Q99u6hqV/9LfX3I7FrGz9Ycvfit9sqf9z51dN/3XZs3pnfj7/6YMYbr2e//tw/q0b9Lbv9sY7nrkZcSL6/OHHeLOn3QZ+avT35nWkTnijd8mPpR0avvvNV'
        b'zYc3f/ogblTK4Dfvbw77cOa+pKwCv29OfyWrTiidOL50WlDBqMuKe9rPrs1Ziyu3TRgf3VxpNe8Xnwnxo0IK3IZP/ChpV1hOlXJr+W/qZeYtj7V7/HxUrfeT6ZAvT21p'
        b'EJ56IuvOhuHL/pJ1Y4vZj3M/l76x5+2Aw98mSx/MTp2w+YHiZOGUyMD3Dm1sXFsd0zD29xenzXx+j+kLz2zJTy9YsWxNmEvDCxcL7zzv+PYno0Llx299aZku+avL3C9u'
        b'JO403Z5icPntj3+d5fTvj35Nbhpa867sxKhTik+ec1vebPu8S9nwXw/8O+tm47KZF9bN2zqnKOTFdOvMhE89d91/6XJsu91nL/zlw5/e/3i7dPSJLz74+mfZyt+D//2N'
        b'q8OpyBfaxv8evGLShMi1kVv+tcvMY+zzk68qNzDgMrLxn3BUOOjoU+CARTcGFWgz4WZsi9FYx2Ai+q92sWQlmQ54nRud7XgQax1d9GB3zzCN2DnMRtODdscAsjXqrpm5'
        b'YauDdG04ZrPr08Yt7skUaYq7pQshZ3X6RFqBethH7OKuRivUwrFuISNbNZyQeCxzCL3TjnIk64hwKftlVAgHHqkbEtoNnBAr7J3XOLKmzMX9SnXX1CMTvOOG5VJPaIP9'
        b'6ZTVfDmxJm+qXcibndOClYZKbIRWf2xmkTqYLxWm4EX9cKKmXeDvasdaFmLC3RP60RILB4fJQcytgUdHbwgIdCAm/CpxELZO30zUM9rbmaSt2WREXP0oMrA+lEqgbOh4'
        b'aIB6ZjevJ1XZE+A0ZiiDc9NAuWEVdrCHt0/EMwrMi8NaZzJaRQFSwQCvSUJWQVk6d7GNw1IFZYqkF7GZbE0mkIetuI/oDPaxzCJO8ZgJ9aTiXSBwkzn64A7Ig5PkabjF'
        b'inf2I283kiyZtJ2VPSYVs9UOfliSuoyY8ZRitTTYQDCHRmk6MRCO89inGiy2D2DIKmRWYIdkFdZKieKfzYYu0SEWmwOwKUQB54n+fsZeXzDENgppW7lMM7bQAa1qivlo'
        b'6LImAYv1BCMkA1gIHf58Kt42hT20fXRgWPNNoJ3ooJVSSzX3WozygINKPNLN5eIMxxggpwpPs+OGIkcXJZRDs5G9A/VsWAyREh24Q8NaOhsPGClcoBZbArBViYWkD0wl'
        b'K0YZ8lTQ/XOhgahBR1aJXLs4h4UjOYbk+bQkbCbtpj2fFcdwK/WEQdZSij09i+V2LoAOIaArh6ge9dbcGQ57ZHCW6Nrn2QhvgSuz1S5+cMWY3CUIpvqT8ZB0Hmnlfg7L'
        b'Uw2XjRX+zoEUmIfMUrVSFGRYNzRC5oMnoYm5j2JHY5NaSRbtBVrL2wLcmKDHhscBqj0DGLg2w5A0hTIxUDonHk+y3t9MJEJxD/BFD5k0hcIQ8/zbY5g/d9UytZ+Dkqhc'
        b'5GEgq6iGL4RsKAzEZuYnvqkniAoB2sfAbt6iNIUOm/o6HNaBmLamskdH4wWogauju4Ezmgznzp88zF6uYwo/kqH1Uck1rkVowFtTFfakHzYFYrEpqZYRHpWQ+Zu7kjuH'
        b'2rxwPxEGVWQo/YOcRcHQXQKVxBxq4I9XQA4eVLjMhyqlA0WNJpIvUZKIZ0DjW7qAjRJHMlQufhTXmfQIFE+ylcYtMmRTJSAZ68nLNwVTBbCerCMil07gmRHsWTuoH6JQ'
        b'ku5opsXq0QjIPAdsgeZ5XOY2k7EvwVsh3fxrWEy6mnbKGG/yJDFtyVqgbZZivginY13YMOwyWhbAnPU7x7joCwp/CdZvglJe4TK8E07HJy2QQj+YuEIHnpXKPbGWY9Ve'
        b'hPOLiVTwgP10Zlwn/RcnZ02Ba4ZY57OTmB5pNIpOArfF4WQ1HuB1rcPdeABuwY3urlbVZFbqAhM4oDMNyEPVdnh2PkdsatuOx7ojwRIjvkSahOfgPH9vEV6Zxiu8CCtd'
        b'RcHIUwLnx3uxBRPha6omM6qCdEQRX7ZkYlKZZkUkMR7ZPpLdBZXpuFdN7HEjaHAioo7MySZyD9QsH2ouc4Dbi9mLNq8eSYrQXNOLEqHQEAu2QA4T1YZ4O1jrbhU3EpOo'
        b'ZAWf1RWDMuj5TSY2kwEaRGx8v9XxmMsKVCAZLTVDvhfhOEVTOE5jZyfyZp3HjtDAIGIfYL49WSt4nNwzjQhJlnaPDSakvnBuob1/loNEMIDDkpkJ3lyM5GCrMw2wDaH+'
        b'mHw2M8wkI+CSVIUnt7PRUGERXNUgjhNTokiLjL5nDsdlPYYF0K6me5c/kbMaMYnX8OwQuChzx+yZ3PddQETtbr5VMAOmWnRdRDq6DU7zihzwgQqNrMQmKMogNxlhC5kY'
        b'cBROsXkonTifbsQ0ujJKJLM53xnP4U0mpRaJ09RYPMMjwBDzsygqKX2HJR6WwgmiZlSyabPSAy56Q0MXuHVjIgIHcxl3cRx32jKP7fo4u2AOZoD7FuGxjXBYkWFiSLp1'
        b'tDgfG6CFXRpNtrSjaiyi5whWIjFxy8a6wmFWm01wEPbytvhtYneYENXoGmZLxxO52q4BWBixisgfqCFXivluztHooT2C6Sihw7GGYYu5YkGQk9IviFiPN4ks18Anz5ij'
        b'D6fgsAOXKycpyK3Wac091nA+SuqhF5BOU8/htOcgFkPL0OAnQJUWEL4HumwkNshd6VEya0YGKbZdwe5zhj3rNzExPIgsVzgNuVjHJsdEMzzSgzB7IZRKgxK8+P7c5hJC'
        b'pgZZbXAzk642bwlcIBOhksv33fp4cMsOegOV7xUilGAHB21wxNZl/EEmV6bicaiQGo6EZq6/XSYiNbs3QC5k42EtSC7Wp7KOluDu9ZpGzAvcxF5FtCMp1MGVqayZ88dD'
        b'bRdAfVkIF70MTh+zU9gMiYOzTvEWCrZDSrFNJPvwQd5C/0y8o8ACUa7Vj+SCJJRIGY4vh5V4B5sMcb+CbHMiefQaWZdmwBHvNlOcCnUw5k9WKo38g+iEIc9bQY4U83bh'
        b'ZS4RTuIePKJQwh6oEwRxGJmRZJNo5crXDdLs46SAq65GsB/y7R2Y7DZfL4UCrJKxCsRRRfbILGx2cnGhcqGK7HXQDCf5vG+A45sVdDlIlOIIOGpLZu1uJuOGQ8c4NZH5'
        b'mE+klrZlUI4NQ/CAbBa2qvnqOA6X4xTOrGn6tpJxWG+JB9xZt0ybiuUUdNoYzjgGOzvQyU3WcoXfTt4t9XLcp3bN2uWAjb5KKpHaJb4TNIIOaoaHYbNzMHd07CC7FFzD'
        b'cgNrJiZWzPKj/Ctn4HwP1GOZBRSEsinpgc1wS+3in6E0NPLFfKLSSYjGC9V4m5WwUQ4HNfq1n5k9lXcmeGMr5kpnElnUqDlmM8dyqNzWI8r7EFZzRfvsNOcAlyAivLeI'
        b'eGHMHDXR5Fh3nlqA5zXh33EiZMNVd6tY1qR5DlDn6B8mEMnUBbmkOkM56H8H/Fb/Idc5RAVP4tVPY2cC7HBITh1sfR8O7RIc5AxzmH5Zi0aiBQPioHAcVhxrUEIhPfg9'
        b'cgblISf3WYlWkmGUNF1iLY4wGCaOkZiLVoxA3Vg0FcdJxonDyCc7PYpObCqxktCf4ySeMnPRVhwiM2XIx6xsegQlmovDpCPId2vyN1vJMIkFq4W18RDyBnpI5STtq1xz'
        b'8swQ9jxHQTaSWEuMiMweJtNCjXAidzvyfQIpYYQ4QV8ubh3ax5kN76v+6F4f3u2dZ0jHSFePoE5GmsLQzxlStnDfuuspUv81InXZRM+o0ug3NfdqpvMflNhYKetxOW1r'
        b'l4t6fV1M2879pLpL5LMOfoA8ufMRLovsMvkxld9A35aWLbKu29SzKr3ukXTeo70s8isDVFifXzog0sTt4GDyojL6ezn9VsF6gvyV/U1p3AOaJW2lwHLawxf4egd5hzMw'
        b'FpZzzrFZFusAVejQpVESUj4NrP5vQKbQHtDNnWS6TOn5YwL5KZfJZBo0b+n/5Kdcam5O164gWs3hkCp0TemT3213CYYZdNvF3CXQztBU2EkF2YWPdJ5WSIQ5y/WxYDTm'
        b'dEMjMNL8VBv1RlWZqLJXKVUGNTKVXOWQIKgc2WdDlRP57Mw+G2mQV+hnM5W7apJqMvs8SIO2Qj9bqCxVVqrBNYY69BRrlU0X9JTpXdBThhQbqGbo0FNGqEbq0FNsVaNy'
        b'BIqn8gfQU8YU66tm6rBTTBL0VGNV4/pETRmvmtADNWXWPTMGHcT4vxfGxyWm/+LaCzKly9X/AV7KDJ7dP+mebEFImPc9qdckLyYctKKBYqSkZdI/ZNFvm8m3P1K0OwXW'
        b'+GP3z/jjaCjaN7G8WPfuaChM2twzCvMOConwZpgo43oAloQvXBgWv6l7Lj5HRHmkWzuBTHQNHtJfqTqMke41Vhp2K4OOR+9CzXp2U99lDfDy/q64p5XQjvrPQo/kPJxZ'
        b'VY+HHa+2CqOGOMU+1CIf2sexg7VJ8XBOwUHL8ogC1iFgTQpUJ15bcllPTTXR6eIsyvnuG3s3weH9gFijhE+Eb/d8PWrojFfEmUmy5l/+oRSZojwD6sfijendQ5/2bumH'
        b'ObVUGw7DUs3603jolx3VGrYO6bEa/yR6iYUBhZcaaMOnX193QzHp99WPBmFCQ1T+1yBMaI7YaP1HhTBRsUZQjAaa3/CfxC/RrqiH4JdoV9FD75jxyPgl3Rdmf/gl/S3X'
        b'AQBF+lzEfd//B/BDemay8aSL2GSaL0ET0vpJr9I91hfQbC/MkW7jrMEZoTsPxw4hu49D/5lQDwP40Nbkj0B8JCb8F93j/x90D+2K6wPcgv57FIyN7ov2ETE2+lzA/0XY'
        b'+IMIG/Rf7+QkveAIlsCAzetCO9EehkNBV8AHPITFgRqi5E5/I9zBXAWewfqoxL88P0xPTTM9pgvz9B67KmbbGXs/9uFeyVvXC6Vv1J3aZ1j0xPC3bm0cElfjMXWk+wxl'
        b'xDCfaW2pv4yd8uzNTJMzd2wz3/p5Z/oJ499+2KDU4xHJJZi/0tFlnNSZE7/RgOKbcJQdNdioVRRWIcmwN6pCSxI/XDwVQBOOyPVDK7ojF2wyZ+6zECzN0riL8DKepHAB'
        b'e2Av94ZXYSUWS4b2CgeXyUfCQW1I7H8ES2DCwzSgRRxTQL8vVeT/DdCAIY+kVn1mO7Ba9ajIAQkMOSDtkNip4PWBG+BloMUN6PUmHWjAmH52y95AAUr9gUOf1xhoKk07'
        b'VqFdX55UvzPooeEpqI6XoNBoeAZMw5MTDc+AaXhypuEZ7JR3Aanb0ZeGNzAKQFfD9f8LCIDuwGsatUmTF7+RbDQ0Qfm/qAD/RQWw+y8qwH9RAR6OCuDUr3KVRGR/V3a4'
        b'PwQSMIDI+L8JEvC/ltou7VN7HMT54eDqAizR8MMJ4dhIk9v1ojJm0kuljnidx5KE+2J+iAZGLdTXfwbcwGJGy7aE4pjJWV4CHIJCQ7g5Cc4xwnUaD1bTE6bNcz7PVw+F'
        b'MzzNO3f0YpYpj6d8RIbyBsXTMqjPHg/thBYd73x3JLVOGDWJADfhNhzGE4bYHivNoDqEITbs6oRgwzxfJ1bvkXpLMI/T0vrpCdET5fPHKDIoFzEcFmDPIqgL6KEz09Ri'
        b'JywJ4mFyYQoDLIZ90MSTc/ZOhDNallu/yMVLnKOW0PxoUkKDeSCcj/CFy75BLs5+QaQYVwk0KSZBYVi4YAs1pkkuWKnJccerkMP4S7DcVaQEJlPGMh56n2Fwu0fpNOE3'
        b'dVIazfJl+fYywXBWDBQaQDmWGnHy+qM24dCODeHa2zWjFcEf0zV9RYIBnBmDt1nCwIjZcFCRZkpHoMNdOkj0MMMrbF5MzRyPzdiWpZYKRnhQgndExzV4i6UsPG2r4Y23'
        b'/ovXNx4yIXF1eLOgvkuufDX4VmSphym4Ge87VudX/ftVd7X8+Zf2KdyW2p2xuPByyade1s1px23PTI77UD4jbPzjh+bc+elffmf3TDry+R77pzzEiy9f3VkXPSP/fXjF'
        b'uK6mwM223jjeKmu3g2fKdp8q6d2tH80OTvevfLVZHjenec0hy5zJc+uOzFavrTQN3/2vimVf7vh2ZaPLT403Bnul/Ha0LHrzlUXPblOoPyq9NTJs9d7o6V6/lOd/duX8'
        b'N66XcqdPax7nsb1xxyfnx8+PL0v2KXBtVdlPHKm6GxJzJdomxM9Rf6jSnAWJROOpqdDo3JMoGxrwArNX1sChDKyZ2wPoTUJhom/yLNEcPDKdJc6OgSpK+7cNW9iTQaOg'
        b'dAbe0TJ/6/JaoQrOshvSzLb05iW/tVwmx5JhrG5GFDMCWuJ0U0VDtQyN03mkyAXcPYLbSngLd0uIrbQY89ijY+A4nFmNTQGdNiEL93ODM5wBfA9eh6NdopI1VYB6PKMJ'
        b'S67dwY2ustShUDmJN4Mu2HzyOlO8JQ3Ecmjl4RhFo4Zr6J5Je+sZ5bOFJlQDLkA2tgRM8idlX7cR8YqAbXracMVLAZij8U1PsOLe6aF4lEcCnSRL5LCjfxAfGGrT7h9r'
        b'OVGK1VvH8szWVjwHLSy1lUzuEixjlqgtFjP4O6iYDG29UluLoHK2LrMV9q7obWcp/oNJpf4PsyFTWWqpVM7YiuX6+gyTzkrDdkzP9c1FC9FUYiqh17eO6mkx9Z0Tavgo'
        b'OaGdlqZe/4erBv2TBfeR+un9SOZmh11Xc/NhTfoPZ38Ss+2XVQ/N/uzLSvvDqZ8UI7136ufY4Ix55PNCqBnOUj+hI/pRsz91mZ8B2zLGst2AyIE7nUAO0CjELfCQKoQx'
        b'eEnqF4o5s+yYnNdbp1RjqUKXAIqlcAtL2d6wHTqwAg8Pk2lzOw+ss2EbQNRmqRCxkvZ3jNNP+gmChk/KBc53ydncuhPuTPDMoDmuRFjsUfC0zflywXXOJlZ8AJTAGTUN'
        b'PDCzIDss5KfjBbYvToXcCbqETSjcgLvh4KwMTRxqBVQHBAxaoEvbNCZbHt+x4Bxc2hWOxRQ/pyqRJW2q8Cq7pI4K6JKuCbmueGkINrIUsBQsddblVephk4OpJ8uehEIs'
        b'jNJmT7oQDUOTQCnitbWbWC88WFkqPJ08g2ZPJh+PC+KZg1c8xwhLVxbSrombJpnE/6hy8RV8t45l2ZOBmd5/Pnsy4Q9n5N006MzI82EK16AkDbOLE5Gdm/yCsMAJD7KU'
        b'ST9nPATNFA+GxjsqoVU6iWgtAXAIm9UK0m8LMM8sBXdHSHEfa9aUdSZCjI8bTZ0MjEqdx9vqF2stJM1YRvMZVy4O2SUwPpkllurOxEkiuVs1yZM0dXKrPhuHUZ5ZncmR'
        b'Y6fNhn2GrLz3huoL52aOYPmR/5wzgjST6045FpSz+MwubUSzXTxe+NP9uu4P96tU3tmvbGa2QV1qZ5oj+fXWDDwJeayya+G2Bds4iOJWy7Id4/AST14sJboiNjvg6c6M'
        b'x0t4HKtZvqOr3QSW7ui9TQiFXLIq6SPDsQRKFMuxzL5LviM0wAVWj61kaTS76k3vTHgkS3g/3kz8W+R8UX2A1CHybXVGhJ968HTziinPbnshJelu3Jrq58TZTsvc9sdk'
        b'Ns0Qmyqd/3HgH+Oy3RZOOP7UDINRUyKt9sT5Dj7/L70Rae8fqUurS/Pf9EzVgudnfpsRUNp0+Jlan99+eN3j0PITEU9EfvZh2IMQr4CJXz3rMPVl+8s1Tt5fj/355Wf+'
        b'bfeB71N/8Z8YH+FXfG9Sg9WQhaMUjoWzy68EpKPfMWOFatw05StPPOZfafVa6uhFSVWv/TUt6swrp4LvR7zZaPJK+qmke09Pq184VGzLXjGt1fkfb5w9a/BgHU5K7QiG'
        b'f74SZPt6zP3f3w9557P2Fz1MNzy/8Pfp72/IeGuawb7SVyctybv8StXGUOPft76h/0b2kw9meG0Y+Zd3p+nPybmxP/r1F7KHvhdaGTRanTNplfG1oTdW3I16x2Z922OL'
        b'Dn6z/80vx5XOXl/+isuTTr99saSkuHni3WrbxNrX50S86vH8v4pPz37TMuGIz9OfRh/8zqbynbufi82vTc7r+OjjOqdLqz96zidu9WcZW3/bO2FySsjYF8aX3PzW9PNV'
        b'b6xOmLDOoH1t+SjP9FGnDueF3t/5hui4IXJl7k+2n5+88tLw77NPvLX7izkffWL17fpLYYN/Orjl6ackrnffc1n9uXSW14YX974d8u5jp7eOLX0KPivJar7+pUw9Mfar'
        b'X79TO7ya8OKykMsVJ97U//7M/eMVXzi0bvxOLJt57eRn556Wr4qMj/rR5cfE0EkJq368Zxt1L7exNOaVmLn3q+buzrpQMmvi5mIjj7xvt0TJilcHXYycH1kfmvHk9mfe'
        b'9fP4d87Wn4d+rn7DJu/5yub7I9YeN/sEjExWjfOY/fbC1OhX9eOOvzvo1sKbY+7WL5wannHt+z0vOD6ftbvj7toPq64PWfjg9Jldl/a8Wxf+tXHw6C+LXlKmf/OgBpIq'
        b'U/an3/3A9O53Pi9uqhleUnzYZ9aP68pLPvi3TQnp8/TPX3IY+dS/Jr/sPvnBy1dPTP5kxvMnmv8Pb98BV9WV/H/ffe/RHk2aiqLY6SqoiF0UBR5FBewKSFf6A+wNUZog'
        b'AjYEBBEFERRQEERMZtLLZlNdSTUmm2ZiTC+bzf+UCzyMcZPs/n/xE+Dce+7pZ87MmfnOFC72fvqFC6/dX7HOxs3t9veP/fvIjGfjvg+98c6LRx7bKY+2eLkhLSMLuz+K'
        b'Xz7hSdeupPB3H+/OXnfn+w3mN6O3jHOvOeQT8PX6m2vApiPcbbn3xOPiyjWvnDtf8rfZVSffaLjy+ZmsGfe6yy0376603HL7n+niv63uTpvyjfwiBB/+emfVTSeDiYOv'
        b'b0j5cvC/v/6bX9XuBa/NrZqpiqv4Z/XErBUxhqrrlu6jnQ980zbj84Mfv9ykU3Xv8vEP7o58fPin73jkfTS4M2XL5a9zkk69PzHAM8/g3qzPXxof/XJu/ulv37M8c+9p'
        b'/ZuV9kk8KHaDLEoFuVDxG5abs9vLvLh65AAULXekOLyAAShAaIBKliF0GXQyly8rTQZgAEnRBxnn7wydlhIK8PCOPiCgPAZOxjH4FVYTesFQftS6HbM9tLB7hMM4yiQL'
        b'C6tAR5cMPS34nrM3kRzowemJTYsk8B7mY2cfgE8+bwkWMfAeFGEZ1kjoPXtfcghRVE8vdG8mZOnIBkGrEk6xqja7bSIijB5U94H3HOyIgMRwNIUUBkhGC9rj+3F647B5'
        b'DkfnpG1SwxnBSRuiN0zCDC0n/FGjavaWXhCehNCzwHoJJ4YFU3sRegvj+zB6InZBkQEPnWgepAXOyyItqR89gkkekdiBN1SJzuzzXngeecbxW1OmQTMD6Inzkgfi8+JX'
        b'sc+3YOtytS+R3W70A/TkeBrq2ef2tmTwGDzPabUK6vvAeXgOijmqoZUcPlcZOi8kUt+lH50XHc3BeZedoIWD8+RD++F5cnMyuRwxssZApVqDpS7ayLrF1syIey5Zi5oA'
        b'GfVQsJMB6+bNZYtmKjVc57g6KIzjcJQ+YF0DVLCO2RHhr1vL1AiaNLiPvOeIPmyBMmhXBYyHdmdDe4pWrZFh06hZHKJ0FpsG9wJuQvFiH+ZGHpkSzhF3B6PhSi9ubxx2'
        b'SNA9DttbYMeHpgvrl3PUHpHK90vIPfncJWRrjOaH+HmoVsGJuRS5RzluzLXn4L0RCgU067twuRxOQTUH6GHt+F6MnnwW1EkusQLwOuQyiB7kxPaj9ORJk3nUzUnWkNcP'
        b'3xgDLVA40peN75jFSzgSTWZpRcF5QUSCpoMj2iVwH1vVZlrCuuUwtpZ1CNtWooXLw7PQBqfxMlnqrNeZULmDo/PGOWg5kDqAN9h7JzxhxMB5ZMOWpPj1ofOgYgVHo1Ss'
        b'wDxHaMEWFy10HuyP5Xuwez5WqMj6b3fRBudNxqvs9Uiyzzo4Ni9yTR86T75hVRyf9POL3VV2WODXB89DMrbI7z+wZqWfyp5snOMD8HlX4AYW8q8PjMM8LWTeSjKBncul'
        b'EKV4RfTVxuUVCFCTgOc5VKFrNRZTdB5kYrmvcy8+D44F8KuD/dCBZxmQBvM8JCyNXD9NxvEbNXOpwxU/KsYbMnQe5MER1iBD7CBrTAudt3H6MDKQebzSxnA8NQCad4q6'
        b'5aPEjC4KTWCaBruws4+hJYxbBftwSprkuI0w4VpXUM5wgc9PpSfU08bCcaxK9evFC22PSaNWbFgKHVBMAXoMnDdY/wF4HhZjHSN5m1Yv7IfnyXb2gvAoOg8vDWIrhRAF'
        b'LwrPI7s2rw+iR2jYXqjjQ15O9voN9WbCq0oovYl4DU7wuWrDozM1ZJNfDe8D6q2Hugz+Mn8untFQryx9SD16/Eguyk5jt402Rg/b4AZUrt/G6ozAqumaIWlYqIXSSyZn'
        b'IaUa85zn0XExoBun05xegV4hbSaSn8JxvBcbdKttQ1TJntqc9BK4zsoNxBPQriZbs64XmjIZyiGfnw4XI6BeRUvNwTo4R4qli9MAikW4MG08WySpUAs3VHYeRKBkS5BI'
        b'qqMFOeuPMgYZckpDVgOjUQwXWAccaGOlk6SJEvipqN8HDLSZqYDDUDmWrYexsA+bKAA8y7IfFoinJkMBb10ZkbDOciDdpjn2bJ4kTGCtdCEHZ6FFTo74A2T+JWSgczRe'
        b'ZqQ8NREuaMgy0yfLpHHFg7DAq5NY9zwX46V+SODBiQzbVsgGPY5Id0USjM8By/uQfPJxWLGGLSNzPzypppTx4EAMX6R09+icCnsHYPgofi9guTaCb18ox3IVko6e0pDR'
        b'IsdIHR8xQTDFTHkaoeQXGSgr3YSud8rw6GOevTEe85EO/KGwV7EYM3X5deJ5e7yKrVCB12lW1mVdLBfnQ/Y2fgIdGEz4DI7ZI2dzZy9uT+4/maxZ2q3FcD6D38SSpdPU'
        b'fxurwnP8NvZQwHrpFlQxR+ZFGtiwFg/wI3/NDg2pMxCancmyOuRIaLDpVvmOufPY2zWbdjgq4ShZh2RT0EsIPCFuJ58Xsf5hE5nYUxrKq+VOgCrKPdL+yYRBlvKd2ISV'
        b'DMs4H/ZjST+Y8TdIRpeBYMYWDe/0tVm7OQqQ/LvkrI0DXMoJ+LQ0zKTAYLMMTnkoLhiKsYtTpgNkq2b2A9HtoIjU1Ykl/OS4iNlxDFRMjysJCS3Xg/OD+A30BayO/S1Y'
        b'UQIqWnlG40k8zuaO0Btz3srFm5218ZYq6VyPgE7Md4Ti3f14RS20IlmvZ/kEdeqv7Acr2sB1svdLV7O2TluI9SpoNO6H9VHAItmcNYyMmHnitX6s4sooqISW2WwEF6ZB'
        b'KaNB4bDvAbBioood+QvhWLCK8DsyM2yiQEVonZfG3XedwdMMpoglgwy0UYpwaRKnmg3R/loQxTWE9zpNjp/8NOoobczqcarleFWCKY4IhStsd9tj+Zo+iCI0WvV2hyMU'
        b'z/owlYXlRKxROS9L7oUomq+BFskFCWZZYb4bmdiD2gBFy528QeUhZCWujZioDVDEllFSjBgiu5RiqzM5cRr7YIp4JG4rm8SNu2eQzePsEoBH1g9EKCpjWOF26wnT5OKb'
        b'Dhc2kJ3cC1BMseY07+QMt154ItQt6EMoyj2gGsp4/XVG5G9tbCJhmsoWQYF0qufOx2NEXIAqCaM4i7AdF9iXO7HC3hEaPH0HABHJWdVgb/x/Dz1kQCqmPxDpddej9Ae7'
        b'haG96ENT+e/hDvX6cIdm5J8Fi35jStIUc/gf8IZyPQkbqGBYwCF6DyIPzRjW0ILloE4sDRVDZFYyhbjov0IcDhmIOLR6UEnwv4Ub5uhKEI9H6i32CD8NAB3+TqPsxdTT'
        b'VDVSI/sN2HDgmz/ySBs7KOcQQArpST3322+n/m6pv/dGh//d2gcJpD8eCv5LraQZ/yjuz/z/EvJ3itR9m8JFaXC2vwr505Ob6kgQv/G9ED8zkhoyj3nmhxIHu/4bdTPo'
        b'lC7VZYId3FAmQMH4AWa8xtJvTeZvkH2rFaW6pfql5tEi/VlqLP1tIf024L/j5NHySHmBGOnQp+OigYsMs42yjbNNWRxyw0hFpJIh6pRROpE6kbpZQqRepH6BuFqXpA1Y'
        b'WsXSeiRtyNJGLK1P0sYsbcLSBiRtytKDWFpF0mYsbc7ShiRtwdKWLG1E0lYsPZiljUl6CEsPZWkTkrZm6WEsbUrSw1nahqUHkfQIlh7J0mYkbcvSo1janKRHs/QYlrbI'
        b'VkbLaPT2LL3Vluzv8ZETyN9WzHRTzvR/etkqMjYmZGwGsbGxi7QnOQZHiuzi37HHcMF8/+CFkiLvdpv4gNkmtZvSzsEhhX1WP2lJNHqHhueZ6urEf7uxWBf0rykDCuvV'
        b'F2pcbOdrGSRK9nUM1iBZ8ZG3aVGpLBRHUgaNXJw20KBQOyyHk21UeESsbWpUcmqUJipRqwgti0dqJDughN8zKRqotRyQCEiilmQ+0bYsZK/GdnNUapStJn1DQhyzjYpL'
        b'1EKLMGMt8jqc/J8Wmxo1sPKEqLTYpEhmQE/anBSfEcX0q+mUSMZvpUZfA+KO2HrFMfspu/n2kulv/ECrMmp8Jdkl8omYKM1D74g72dp52vdmC7fVRFH7uLSoR00SnUO7'
        b'BfYUYhKuZYMoWf8lpcbFxCWGx1OsgwQrJ0NAcRwPdFSjCY9hKJcoHl+F5OK9t42MSiangsY2iTecGRLaSe886QpLSNIMtCeLSEpIoCbObO09YLQYYC/2yLckxPfoRIQn'
        b'pE2dEiGXSI1SIjtMG0Z9r0qYNd3s3qhnKkY+ZISAiNHGkrJcnqOzT9ip2KazQ86U5QqmLJfvUkjK8lh7xe2fZH8AxTZg8/y+udrvWTCSHnHjxZX+fpL1HQtww8rtnysy'
        b'K8xClWzFh5u12kXxJfR7+/QR6Co2nDMoSCYinOz0MNKkMG5FyAvrK0R7uf1O2KHwyMg4bnMq1TtgudGFmZIeJW1ZTTrZS30k4+GokgGWuTyaEN1x4elpSQnhaXERbIEm'
        b'RKXGaMUK+h18SirZiclJiZF0hPk+fnTsn75zzUhaZAONGRwDNFSOkW3+tPXl7xc962h/Ps3+Wfu2fPs3WvZqhLiderXr47+mnzOrPdzr4wKteJi5qmZ+7tOIkGJPRMN8'
        b'ezwKLcC/gdp1ZowXDmbuoHfjte3QQOoeYbxL2IUd0MaUxj/4iIJCz5w0Jcwv0ttb4Jr+lNnQKjKrqJMzhZlYACUs8z1bpaC3dppSmBcWb2nnI6Qzx0vXSFP2EZG5jnnN'
        b'xlK3SaKg9JAtMdmSTq/VPIzgpAbzjKFjEuZu5qoMIsLqO9jJBFcs1XFMhGvMysEuGjJVmzCLvhD9Ze7UpoL51h4D16CdFtH7fbK5Af0lE0bPUI5WYRfzX2uViEdU7LE6'
        b'nEh5nTKoxxbMSXemnMdJ7MYK7SJSfRyIjI7Njj7qYMh1oeqU5XhcbzjcCGfa4RkpcJyISYUCycDe6k0VE7HNwl7OOm0IN6CUxlZxxsNuk6aKgqGJYqe4icg659KpjKaG'
        b'o1jf/15HMByKV3aJ8USC3s9009u3YHH/e5lgOMNxt5iAXanpVO+jioJsHrXFO9ib5WrA40u9tR09LjTRHTxHwd0tH/JN5pKqF3QvdcY2JqeaQyG9hjowNX0ByWPqHqnt'
        b'Ir033g3m+qnVziKZ74rheB3yLMmQtagtIE+tMsAW84mQ77ssSIiKNnWf55S+hpQThPVbHlIQtQCd6Btih7neeDCIWl6qQ/ASW5tw2ZUuT2aKE+ijNBtnQCT3WqUSO7zG'
        b'Qb294LXZAivwCvBZhEysCcRWk+RUGVaFCCJelY3HPWY8JBQWYLdKLzVDlo5XBSLWOGCTZB0A9XAMichsmJIq08BR8t0F2Vgohzb2oSOeN9Qk0+tiO8yknr/DyJK+yk1h'
        b'rsZiniYFWwxldiPJZ3tkYxV4hBsqHILiERpsI0XOhv2CCF0yK7JvmtkE40UyXCUDZhDOQjaZw+3uzCSYDGTnNO3oO/7OvoEh3n0fsJGzwjwaTxZbBTwVr4I6KIOL6S7k'
        b'66jQFb/5donzcvoN2WdFmCtgsRCJV/UEUkJ7/A+//vprlDfZnJFBcrI5Db9bO4M6bqaXQzMJQdjH9l+N1cP3H9ZwpDychmaoU5HmnOjdgnOwiBRjS19mY1mE9gaaNVtr'
        b'Dxqs5bNwAs5DFt+EenBa2oWeeJIUQuVCbIXMjb+zC7EMDvdvw82LWIFuuJ/q8KDLTHsbpsEN1mMrP9LjSa/p0B6/7JRIRDvu97vChu5duoQ24Hm+hDyBG0zZquAIW0HQ'
        b'MJuvoENYxxdeI4X6sQU0E2v5AsILGayiHh9S0aw5ClrRz/KdAns4xFEh6Hm/JZKHTm9scBCkaNBW0AmVfNVgHeZJy6ZlOKveNziIVwHZeryKYLzOSvvHalKFYr8uLe21'
        b'4R5C3JODbwuaQkKEU1r9E0qeTzSfbHEg4ZDbibEl816dVvTKz84fLgfnBJ89BulPnjczu7Wns1ks9w5xfXZD1l2jo0Wt9f+UrfzSwslUNWKPpePynMVht8Y9/cWU0uef'
        b'8vho7q/3f4wPPKh5PCnvqVedyiZvtc00iM7rGWZponb5XjH3WaNPR9ecGF18HGRHFEO2wM3gyAZFjVCz/3xjSpBgPHSn9c+Zafs+vhLUOvpiXKxj90oL9YZVfl1fWxSc'
        b'8jXYO377Bz/WxPhN/tDHZHfHc4aaYu/CHbmfvaQ++8l7JZEZ914tG+3SkvbvOZ9MSHB1ymk5m+QUVdfiqvKyC3/a45OZPV+7nPRudS016znp2+qz4qSrx92yA8Vnj4dM'
        b'6n5v7bUJLpPt3SwzEz+7fjxjecq7Qz/6tHypS+2r0U/3DH8BM7+2+aXaeca7r6xcc8Dy3IXCI1OPXcx3aroy/eicd1YEKl0vlQQH/POVH9+d7PsRxN9Ux36juTrq7N2C'
        b'J4Z93H1w59cOSS2uJiu+fDt1XWFlxDd+awI9f346YceYgKoDI77Z1Ok1xKMu/EPNSe+RH4U+OWzG7U6dm9WRN4yC3Ss6339tWMSVETf8r7unpJ4xaBHa35v21vynN94M'
        b'XGkxNLNnnd2tkOCGJ76dOulNz5f8jlV/VDNmY84Vm+dfeaw1YXz8l/IJVmHDMr784ML3Lz755o2t3/nAT0tP6v384tT3a27PNrd9vjPq5eBXd2/Z+Mwdr7s3Zr3oNmv9'
        b'N/+4P+XJA3fiRgfOvq9znTy492HorPQP7v/k9GFcd8um57/MWhx194bJ1skN9l/8suuHeS/cap/UfVtn+9Kfw6bPei3yCRPHACO/f4S3uf6w4QfVjPfvV97eUnnUwOhI'
        b'9VmH0ttbAufYXv2oq2LD68YNpt+b6C+Nq255syUy1PmWefFn/xKvPGXyw9907OdzV2Stu+wdcb+Zi79IVnidTE3Oyr08ks7+ydN2p0E+XKRnAjkpME8UVNBFVjvmGLJ7'
        b'3AkrLB2xcomPny75Nkc2G6+vYPeWcxYYUj/HUIqn+o0lwkm5lDp5YIkG8ieSQ71qCFWL64SJo+Ml55QdI8mxkY+5E1OhIJAiaXeJDtBknEaPftdp2Ei+o1p2PxfIDWS+'
        b'fCFnoreTA/ndPJeclbpCKGGXGq3wGLtODoJGbBro/RnyZlO7j248wz28wjE5vT/FaxuxwFlH0FkvjnGAItbOENO0Cf7qQGcfJ6oBUMFlEbsWjmAXt+4hWMgMToyhYIDF'
        b'CR7dzu9mD27G/dyQHU4FDkDlukg+4MaHDdGYyQdcG1ssZKMwIt2DebXbR1iPvitj2DOa3VPDWU89Rx9otJMtCxUUMTI8sCua3XITkl04m2o7/KcZa3u8s8ZyRcpGrOQK'
        b'V7iewNW4G+AS0+Niw2AenSnHEJvI8Pr6q52Z0X8DdgdIRYzFI8qZ0AXlTPkSiZ14WQMXbbDAh06G2jjAGS+rRWHEIgXUwrkEbnLRkAEt1DzikL702ggvYbOXiB2TXbk7'
        b'0CKshFLIH4JnJwY4OxEmRN1boe1kBdZONGUKlXTIMTPALu6mr99J3yV9rig9FxwM+YEuvv5OPv4ywXiEXqx8OuyDBtYIL8zCcs5QSXf+RquwaKpcl6yk/fyGvG23MVMR'
        b'HYQsqFZjvq6goy8aQreau6WtwjNQoqGKmgWOgnyTbAcetGIVrydFFEtq7zg4JfmlPQ4nuQ/T0ljCTXP9LdWpSH5WsQuPs/ezSMOYaspvbhLTjSuxTIadhLst69UqF2Kr'
        b'ykXtImJpAvn6vAxODZvGfKfDSbiS0qfchgrsekC9vTWSb6bDgUDmqQSrtRTM1nBJ0tqfwXbqIxZOY3ufblo2mtW+0WYr1UXm+engCTxBaj8pg8KFo/mAd9jE044dchTx'
        b'HJaRl60yOAcn7biS9QbsGSVZc0DtUmrOgXuwiNtk7NsJRdzG6sJWptRSYqcoI6uEu7oNmLJFA5W+fbYAQzGbKTxFyKRKjMB+NArpUYVgBk1k6/omSEo7QqHKIT96fWAv'
        b'tEMPykTIxQOQxe1csiHPVzU88HdMzfD0YjYus9SQh63MYgQrFpDeXZGRPZJny3owZDMW85dMTtMRjPFyRKTcCy4GplF5buJEf8jfnIGXjVL6GWsK95+Ihd7+WKt2Jt8E'
        b'eekZ70jlo3XSAy5oUqHI0YDwUfYyQXenOGWYJ3uXhi2TNXgasx1T+bLXjRJdF6lYb4dgiRMZEB8nn/VJhE6yIJhKwRLPKwZptvL1V4OVhGSdJsweKZh/D+fF2auRW8xt'
        b'JGN6jRcBBWSV6grG5hMC5POgE3P5wr+kB3karLDwpSZmMmyXmabO4m+6CXdbzrR3sZBPtXd2kMdtV65ZOnEfo1xzNxGquPJuCmTz/p4j7Fw7s6WKILuf2lJBDuRzV5mH'
        b'U3dpiAAheckdA1eHMVuOect9SDtJK3zI/qX04cYoPDTRGwvkwhg8q3THw1DNl9fleANNgL1kWKeWYXayYGojX0r15rTdCZgN56lZEw0Rd5D5Hh+3nG+2Q9iQpGGjtIlK'
        b'FbBftg2ygvkmqtoqd/R1Vjs7BBDyYrILD8fIw2PgAqOZseugQ2rcGLKfWPsoJCqXWjjYr1fCybFwOY3xywdhz7jfrg2sm0CXR+A0InXMhCadADwPNb3uYC/FcrsxEW9I'
        b'Xqqw1pcr7ssXmavoO2kNJ2GTMAg75dBopJRwQDOg0zEogh1A5FjTw2siHF4neZMlrH27I1c8wgm7gYrHeXDe3ui/V0j8j3SED/NCcZn8+A8awN1ClIHMVKR4IR3ZcJkh'
        b'xQ2JTK1BMUVMq6bDtGs6oh77y5jkMpaNkI2X2cnMRFP2TI88oyoQU/LGmjyxklmJFHtkRdJUiziClKbD1CIDnsjoP2P2JUUr8ZKoHnCbpfal4IMOMZRcA9dJFUfXBqKR'
        b'DP+rmZDz4vpL7xtNH2rOT0XU/6Dk2yN0jNdW8z28H//RGUbWH3KG0ajX6wxjYDV9njAm9+om2OW+k21UjIutA72tdJk01a3X4c/DHGP8UW8dIY9u4KXeBv40jLZEuuq2'
        b'jYscUOcfrKxHLzSC6z8eUWNrX42jGJ6dgbijbdmH1CvDn6qXz0KPUWjf3X5o3KMqb+urfPx82/TEuJT0qIe4bvgzLYjlLTAM7b31fXQDOvoa4EB7r0kj3Wc3x32Xxn+l'
        b'ETF8rm8Lj5zrrr66XYKSqIupxOgk5vzCNnxDUnraAI9Vf2X6U2c9uv4bA9ealgelv1LZ3EdXBn2VWfdX5umz4K+sr9T5j67ryb66HGldieH9HsB6/aZwxxF/qfLIR1f+'
        b'TF/ldsEP8Y/V24C/sq0MmN+JUOoF4hENeH7gtDLnEXxb/4U1TEgIqzMt6RE1/q2vxqGSm5G/UF8f6dgQHk/VWaFJyVGJj6j05b5Kp9NKaW6uZYnXVs8+6JXmL7XJuK9N'
        b'EfFJmqhHNOq1gY2i2f9yowYAcP+kQ9TYBx2iyoQHdUnygLicw+/KNJR5dUy+Qn2b6kW/5zf6qK6glytrG/6TvYyLsFc98TTD4k+c66ol+gTs+h2Xpia9xlSUv/6PrNRu'
        b'IWabxQNHfnxUYmjoH3doSiu8SQeeWtL8R25jj9AwwK3pQyv/n0xCzH+eBEVAcNwqB3dRQx+vj/NUhxtGv/eZkZ9cUEyQ2V1+u3+N/XacTwl/bpw3/oa12pCUFP9nBprW'
        b'2PMnBrrO8FGMHa+9b6RpK6hKnQpbXKXe7wi213kYV6vLso36VOpijpLMgZzMgcjmQM7mQNwlf9gcUPWmIfnfbcAcjJS8thRDiStX8AjTsJlpeMZuZOpMV9J95p1j2rJU'
        b'O/tQgV3Rr3HCQxrjVH2ZEAl5Ip6WuWyC0nQW5OQqHraDAyuYxTZ330A9nxxUkz8CqDOUZUuWOS8XhfXzdKEajuEepn8hMqeL2peqcqCw75qMRsrKh8MOEUpowMtYwzQQ'
        b'XkSiquJqKgpNaqZ6Kg2eYPrGZKjcxl28QA4RFfstwXdt4pqX6xtYsKqD7C7KQVQ4y6ARL2IO14gcD3XkMHG8hgUsti9eghss7jCRqMuijAVJWqViu0mMPApKsTaY6TPW'
        b'YLc/7a19Qoqzj0LQ1xWhEKqgkofbDYYD3JuGd7hCQWEaeyexrybBqRB61Yl7odWeiJL6HiLUpgKP4DsJi0gvOCJMDVdYxDYoxw7e1nYzFeY7BzDhUmedmLHAEpvwNBtL'
        b'uO4Rq8ZCH+q+0Q/z2ajzAOtjId9xthILbPHwgJWn6l15C/tX3sB1J+tzVde75gz4mltBltFv1l209rqjy0vvN+tuUgBbXIrtkuuXoUl+bYlrOfYZT5MJyGSAJrgyWwpJ'
        b'Y4btbKVak6nYw0zAcb+eFI5sqTX7LmOUu+MErBg4R7uhmWnrV0DeHHbXiMdU7LLRaSF7Di3jdTXYZEytzYnEahOIJWzSoHY3GcXrGX3IEygwYEO/bLGHBLqBE1AgxcTa'
        b'uZOrx+ohe5WEnIKGNB7UzCaEh65ugYrI3qBmDDS1PM5UbumDF5n9AXdscAhzJwRBLeWyRgmjbObZK/nCLcUDSwZ8q5hLvrX1YEOimLJLAi1hqT+PKLaKLCJ2bXQwEbsd'
        b'8crUgdHM5Bug2I2rbxtxf6DjeszUxmLhwXSmMsdcOGTsiCewBWmEOAd/F3tnX3/qeGa/0mOpH2vaMsjFwzwwGYU9zfdkwKcSOM0GxDwY6lVwZhOP/EOWqp44GDpmMpOH'
        b'IUtMfs8cn2yITGX0MrzBAx4UQD6cY/ANP3qbrKZkBPLY2h+/AkvwkHJTFOYz8kPyduJJquZgsISTRr8TYykA9uqSDbZvF5/sfCzX4UQlfS5TfcsHsfGDYwuwTY1F6x7E'
        b'lsCp6cxa01NY3ku3oBkPa9MuRrd8ItgUOa0y66U767BUYIRn8TK+lTssIZdhX+C8FBGLbPMG7pWgDA6kc4zHrN0C83MTHsK/OjcjA/Nt4vpJgCVeImNAK1sUvZDTjZHQ'
        b'yiM94kU4yexblmxZQhavTJBBld10AQtdR3Dyf2XxaEcadwtPwH5BEU5JX/0INr/WeAaOqXWwEQu9nZ0YPPiouAOqAln3ldAOOY5IJufhUIjSAL6j8wLDHfvCHxoaQn6M'
        b'3AQPTE63ExjA9BickyhWLRx4kGoxkmUKObykGuyiqqp5s7AlQyHIsI4MhSF0s72cugg7NdisIwgWU/GIAEUbd7BeQwHsgWosiTcir5wEp/QF3KqHED4y+3rJ3qlOg6xF'
        b'7m/irrmc0cSiNSlOFU56/GHQRiOB1G73nle60541zvzha8v0BVNCp6vE2PgTbqMGeuFgvAn9nzZ6h7DOeKdshyzZMFJYTkhlihjZy2Bz/kMKWC7LeICt/kl/VkxUYtSW'
        b'5NQ5UfqSgwiFkL6SDsSlSGzXjHJ48NbzMPWHi4ecfJwhj/xxbIADDiyRYyuUmKnJ9jfdMA3roX4r1FsqvTIEOL7UEltHj06n4iUc3QRnqVkF2W4lzi70etiH7OoLTr5L'
        b'lzgv937I4QKtooGMRqE7bxgGdbpscQyCBgU5Me2dMY+rgcjyxwZs1hWGhyjgArSMYkr9we78DJjnvdWvfIi610QgAfasI33ZC4VaMz0W8tjG0Ie9enymIX82m+qd0BlX'
        b'kLhfpnmbDFJgztWodReCryWaz7eoOPH2levrb1zPaAnw9nx/bOHXAgQdVu8WzMzqR9stMu5cdPjOFKuyXFN1s1Gs6vxrFsE597znPz54ydIPVabKzV8k+nka3KvUfNFx'
        b'qKM19a7fXbt3Y5p3frmm9RkdK9cXa8rfss5LWWzgfKa2sWb4HKWrevJ7PcvX9shmfjLG/E5QlOOoiqFWky49phPzzadlxY+fqrH5cOGqZ4wL3l3mOaki+PlqtwUBg786'
        b'/vOPc1+U616L2n530bF77teq3I5NX+o4b9C6wfaOy16rWKSeUeO6ZPzUdyOy/WImzKwL/uluVaPGQTfghcXPv7Jv4zMb5nwXYrVxkZHH4l1377XmnHhrT/hym88iH9Nd'
        b'bFW1t87n1sTa7C0Hvtz0idHCZ0o21rgX119w2jXpbXX0+FXLMwM8g2ruPG/pfOK6a8Xbmbc+2doQ15bu/PNNS+dnm6oPzRecj+MPI5/Q9IQkOj2V8OEG4+4xiUWpUbPD'
        b'qnNSuz1OBW79esbFr5Kf/2HR9rppovmmJfF7Xzv3zMkz05a+iKPTK0Z1Ldxy9MuE1FOjTZ6xKer0+3TCB87L1pxpWvLO8NvTbm+Fhqykpd9PXXnurZFZMy1WVT1z4Dtj'
        b'/0avyBFp4eZtX850qvOML/h60dNvvxb8+Fs5Ha8+a93Rdv/fazqnF9z5zsWmOSpx5yuL3jXu8A1a8UnZJpMbRu65+2dV7Hnc5uOPWxxe7XrjY+dP1Wlv1I5QJ8cfuhH+'
        b'L5ddXm+i4eRXbleu1e9o8rMavTjE0+XNBXdd56ywrPOZ+PmP6afq89Z6fZ8Y65B+OCXy+4stT4z6+G23wHci4l68Uu2940vhV9n5T673TFgX4v9FWs+bP/zN0O3Kv+3j'
        b'vj/z7qqenZufe0M+fvadWVuPXXp+5QfPFb615dCr3zRbf65yT33toOuXSzJKdo7druec+J1dmv/r7w36/OURFeZPbb+ZvvDQ/c8bZmT8WL/jwq7qT58bqffCu0+Y5zxj'
        b'HfbLobXuFkEFgwOD73jcuTu9/aWx25966/FQi83T3j+71d5DgukqHShLAHUKQuCrGaHvglro5kq77A3YoMI8ex99O8J5O+uMX0b24zk5lG8FKSheDtTidZV7kIM9Od8Z'
        b'BG2YuDzelcNNsQ0Pc2U2OVEzeczQJMmJGtQHScrZCBOum52MB9hnsTZYyBXo/rpcgU4OxWMc6tUB56f0am2PwgVJaxuBOVzQbsBuivZmjBUe95H4qjVQy7QyO7EKclX0'
        b'sKFdSvGbaK8jGJGc43dhB1OcL4TqjD69bb/Odj1JUrXtmCCuJDsDZXhYA6dstNS2C9cyHZZy8zQNNK3Tivu5fuxEZhYQhl1jVXg9loHAxGDZHFcs5hiv6g27JYUsOWHL'
        b'mUZ27zLWn9ULJkgBahn+PS+YB6jdDxxpDm2zYS9Hk2OmiRToNRm7uHq/FTLdNX50WghtVSsFA2s4aSgSeaKBMJVsDq46bXGcAF3URIDI5TpwQXRzhzo+0IfgwHQibcH5'
        b'AY4qFCjB1ipGQ7VqyfaBMWqveMN13rC9UDRIlYZtdloIelc4wXVjeeSspgEFqZsJwv8exEZB4SGD5m14QQqAmrZQpdIMQO4Tbn4fG61Z4yBTYx6DeT4+2K4WBd0U0UE5'
        b'gY2warOrKny4Nmzacg5fxuWE8auj8T1TuFbYgKzxyhUidKbBcb6MLy9cqJJhF9QnM/2mEsrIZERK+tRMOEyWRda4ftXnaf4Ga3ZNV/n6O+pEbCFCRKcMDkO9L9PgJRLe'
        b'p5pKCvouahcDX38irpXLhSFEAiMjDLncHqQI8lIk2GMfptrCZTrhrAk72hzHbTAa46BVQj5rwZ7byKlMoc/YHs/VyW3LyCIaA5UDccJYCDxuLNStIiJqq8zcWQvkqLuM'
        b'mcKoYM981RBoeTD0t0iYpKKFfATzllJrCSmiK4VuR65i4G3sJJNGBz+e0IEKFlpVMZIFV4VLsxiFiYDTcEkTBCVYaMesTJReMixYjIV88WeSqTjD8K02kVI4znHB3EXl'
        b'gUQbpokm7CTzT1VnvJPTrOwxeF6FZ/CIXT+MHctB8qJwaANWquAKmfIBsFj3jWwgPLA+jIFiE6BdiuEJV7GBT8hFsvWuMmCsFiq2iQwiRcbOVfZq1/dQKtI8txfFiped'
        b'2FTthqo1DwTaxCvQIcFY4TqZdtov+0W2qqmT+iJtmuN1sh95qGTjdRqyO85SC9L6ZNJ1XbU4CutwP+/2QTiGmRxaCxewSooAGsbh91ZYN9UR9+NJ7ej1zlBDpodO4K41'
        b'0zHfKYAQccLVyQQVZkMp2dBE3K+HNm5MVrqSkAqa56A95jC/n+WR0CRiDZHDmnonaw/UO6ZhOWHBqdlHtWzJiFC2qXWwLN0x0Ins6Xxm5aWChmXYLWI7dIfxrXIswFlF'
        b'pNerDlgopwavU8wkS5ztSqjTCMYDbICmynWJtNrOGubnRRi4B2zcQnZxK7e2JHur/8/QvQfVtf+9r80eAwqiCmVgBsbhP0f5/f98+7hbsODgWAUDy9KfxrLxTE3uJHOQ'
        b'jWBqcwpFpZBZUcYV3RyaKuoYinYyK5mdaCYzlg0RmbJcCv/JfxuK1gxFSBXvNI81+ctaZirSwJ8cQmsqGy63ZopzA5LPVjac/KMlmbLSGKBXpLeV2+wfVD/T3oa6zGIK'
        b'K80cl/7ec7lF0aOftiUyKi08Ll7ToxuatmVDuCZK6xr1LwTHILLQTapKf6NPn/46+UtOpR+KEP0DF697hF+5008D9jNdTb5amobZmr8sKgnT8IQJIYMNTkOw1F7Or3Ou'
        b'Qju2qX37fSoRctNB+KsohsZQYM5MtWRFGbh5Ua/hlDXUKIgsdA2ymVNNzIqN02pEoFTayJmBWKfAUjyPZ4k0RDfhyAU22nXhuY3yJF9WkzoQbvTVhN1hA6uSw3GG7ZhK'
        b'GJTjeB4uOFIzr0Y7b38XH/+lyXRIWDAX6hlDJoRZ6o1Ng0Z2meo3n15DwJkB1vu7xQTYu47dysAJwtuVqbHA2Q7OhEN9MCts8tSl3lI7Z4zVEZTjGBgncI25kpw3fTFl'
        b'1Ct4zXZa1yVroUzPJEHJJEc3IJLew8YlATLJuAzBU8xDNXYbLdU8UFAI5tCIwRQUQrtF+Z/o3XrkJCvDs0zcHO7Ve589bkXNpjFC3BMX18s0FMhj84/JUUGzk16dN2TX'
        b'vR0B8U//uPHVywHPr/jx3wY5g9Lv5iwZN3b0KM+jQQdUBgGvjMKtj1tOU39YULvB0+bE0Bmuaf90/2aCrc4Tj2k+MvR2+u6zj7a+81Hl91+szYmacNGx55yn4XXFS+Pi'
        b'lhm++7cvY+CrvPftx611+9Bu1K2sl049V3FoytvrRhkXxRTL42w6l5XGHlv2XWV1k92gG6+vDak96fpi7bXFHfe/Kl26rcVs6XOaT02vfjpC9vXL929lbGnD1thLPzh8'
        b'8rZ7ULj/bnhc8eX57RNl9fWmK52nrox9PX3fE4PbNtodnv53j0WDfnUte+bC8vbnzm60X3rpavgmWVf4/bbV6iyrjW+37Dx5Lu7rKY+rXt/b0PB2kUHb9L+7ZCRHgGra'
        b'7qgjjaVDrT5947nGhmkv+s7rsfpkvGXQ4sjh/3w3vXbHeecG13sfnzof0/BiyBtu37y5reur51c+5TbB/MTJH1cVve72nPWdeU3PfjtmYn3Pt+3mE78v2v70jH89u7Pg'
        b'bS/fkc9OtNzRXbLiiveqx+84f66eM8hn0ueyr1+LSn+y3Or4hB889zfN0/34xw3/zNd7QTNpxYuVF8Y/5bJqR/z99PyId79agikHNTOifRpfqNpUs6mj5FrE+E09N6fe'
        b'8kiZ8mukRfV3adN7Krrtj3g/2fzpIfzsjf1Hcg9n3Mk6ZuNtFTBy08X38t+t/ehX66uun316uy3jRecnjd9a4v7h+LOD84Vr6Q3J71da+ay7+aLf/uO6z1gVJo4Jnd4p'
        b'/8ZlfMvwaP3F3z9nPef7CZY100JyvUqnHD3XWT3i4LN+1wPxzpncrcnHDGLuy4a23T31SrDJ/Z0GZ8MnWO53mysfNjSjZ2rXB4Nubf/nkKbk6PupgdnnL46o/WF79i83'
        b'Z8WNS3j76JT776WP2t65f9bf/jX87Z0FJa4bC76ef+/HPcYvzBxhuvxW21A49kTsG8P+7jSk6MzgD0b+ohz+qsnfxxTYT0qjVkbqZKql7LWAwzLM/I2FZK95pD8cZjzJ'
        b'4AjCvnNjTAEK8By3xtTHTMZVm8ixQxIuBazjsiUW42nJ88YWzNOk6WkZBDJrQFtTzv3l7ZSsqIXVCiYEjl3BZLSxCzDntx7ARxKyu2eaAi8OXc34nWmENS2S+G8ojqIs'
        b'uMR+49WRzJzRdwpWMQfoYgaRdwtl80fuZM9HQJaZRuL0ocNXNiZmMDPqTVuO9b2GyrTDeJn7QMIjeMBSAZddoJ3VvBmL4AQ2+auIHFIo9UtlLuI+wkB3sZ4vhmzYS03P'
        b'U+wJI75ZRppaR1iqa2RgmC6hVgFXqBlkaLLAjCBd5JwHPwT5Q7EDjmgkB33UHtVgswgNeC2ejbcVlkRzK0mqajrCzCQJ18QjnesRmauNcL46grgiJF02Exo0nDFrtvSg'
        b'bPZ8oF5eqcFnIZRyjrAWmo2IiHFpoEUtNadthIvcOc1Jj3TmNpCcsHCe6Vgyg33Y11ugCDuwwl31ELEieAj7evg2IolrRYef4IFHQmdzf48lpLmFzAQS6p0ejA5fNZHx'
        b'8hq5K0Nb1UOjTS+7DPVjucBzKAaPqvoFBLziNBq7Jkv6eLgGHRoaKoJaqSZMkEO9jAzvnu2cD68MpTAucs5QUR0y8bgcLlMv1EPYPLi5QpHKG8+5+KfyPGmk6kEW8o3k'
        b'nNvLdkUCnsUOFWHh7clANbBR0zMSI6etYKLhFpLvMFk1+7jDxAHuErsJM85AlO1wZU0flGIrYRMeQFNoQSmGsDp1p6+KwBZtGZfKt3h5Izf8PYhteFWlLd6Sg/wG9Zcf'
        b'zYeLnsPFTJYVgqCeC7PbY9i7jC1Qou5lCHRCRawKccCsJawzgdAxCYq9H4pB2QIFXLjuhutYjflqtpth/1BFoAz3jLJmy2+10SzJ+aLuFm5DS0RnfoFB7eKLqGZzTIbD'
        b'QAxH0wa+SM6NwMJ+8MCcrWomtMmEIVGK0XhyG6t9ExGzK6kNsNPosWyh6k0XN8CFNO7OqYJMRQt7K7E+UjdHDhmO1xSE1TkDl9mi8NGYi0v4YiWzTj22GfiJULQZuhh1'
        b'cF1kQ0qhTA7kToQWYy2WZNJqHXPCg7UyA3QsXyDjNDYIKh80QteyMm7Hi3wQ8vDShglLBvCYuoLxavlkayxgUudEKN6plirWqjXCyAFzlHAZD09mE2WBjRQqOo2WFEjE'
        b'QBcpyJ1cPgpO43G2H/3gogHD2khAG10oHiNfaG/2/1Ga+l+5KtJ2RWTUaz1z9Y/JVQlUttFjJsfkf9FUtCKSjRWRfizIPyL9EBloCAtxQOUeMyIOmIl6TOoaLh+RSuQj'
        b'krKQWzNT4yEsBIJIDYpF+j9zN0TKNKRpUU9uLDdkJs86RA6jZstmtEwlD5xgJlOIvEY9uZ74WyNeJkVJEhO3KLn5vzRDliQmhwHD+PafMFWpfbQNMms+NQYb8jB3PT2W'
        b'odSLQkQaFwxDqcsEGpKZue1hXnyY754E8qNHV7LI7THUNpHtUWmZq6Za09zT6Xfr6A+KEmbBB3v0++z/enQls7weQ217uR6jAZZqzDSKme2wAeHjb/l/d+fQb6x0lVTv'
        b'TudjAz3NjRWiQnSSjd/AnP/I/qc/RUO5oZzHa+hegLUPirwyYSiRKk8S4TJqHN54uJ0XHXrm60boC0St22fzJT7S5muA3QfzDS08aPO1LCDdX6Dwlu1uk6a4Tps81Y0c'
        b'mJfS0lIzUtI1hHZewtxEwp+1kEOvGa9gq4meoYGxvpGKnPE5hGEtxiNBS/AwHltOGCUib6tU0zGX6XidoMWErrbJcA6yyc9LIczl/Qp/TzdSuStcXyq44pn53ObjHDbB'
        b'CTdCadxs7AQ3zMIT7PnSmXDMTUcQpmA7nBemwCUsY2WHWcFZNzJYUwkjSSTp63iMWWuYL8ZyNzLB0xwMCddaAWdYjXHxc93IgLpb4yHBPVLyvA8NSnc3XUGYbrZKmI5X'
        b'lOx7kXTxFLSSvzyWzxU8VG6sEZjnDk3QSho9IwrKhRnhmMUaEbMDjtNx9CQn0gnBEy6EsUIyjPEG1QsvGI6lwgIo0mVPDQhPsFdDurIwMkhYOFNqxfCZQzSkG14rBwte'
        b'ZIjrWdbIcXBDQ3qxaCEeExZtgxpWmw5chlIN6cdiPDNRWGxPHtMSCPNzxElDOuK9IUzwjh/O1evVVhFIu+HjjVWCD3Yms7yTp+ymihTBd6m34IvNCSwvnnX1QSpsq/GI'
        b'G/lRt5XPyB4VOc5bdehJljlG8IvGAtY4q2UUMkba7K/EFsFfE8LMNcgxXkl4jFYldY18g/AWAXPMWHZ/POuPraTVgcZQIwQqI1idapLAVtLoJco4YQmeg3re7JoQuMzi'
        b'IYQbCUvJgjvPH2f7QZmKtHsZYYquCsusMvhkQ2OUSqSuHfZNFIJiIZt3p3i1k4q0OhiOQJEQPAHb003I45QodxVpdAicGSGEbN7JCoBDCrygUlJX4We9hOVz9PnCKJ0c'
        b'pSINXqFcLayYjudYqSrSuWsq0uCVQ1XCStKMFm4d1OThAzQUyKpoS2EVXkrjg1GGV8ZCPmnwajjuTn4U4nHekdKJNPItafMaaDAX1ixVs6EO8MFjWELaQX2cnhBcsG0m'
        b'y74a6gjLwoOq+BHepMWVZU/GVidqGTwKLmA2+ZmPpbwxzel2WCJStxGHAgRHwZ0/PZMiDyI9H4cHoFIYN2oWn92SECITlOhSo7Z9eFCYtHW6ZO60bAmWUJuMQVgkOE1J'
        b'5ENSMicuiLRv/JSFwvgErLF3YndCyYQcVDObhHxHCpGkYctM4IBcMMcKOXZC4zQWGgSyEhXsHfkh94G9kJlKclwkOQirmce8NBDC0URGTSpIjocTeCZaDJW+2PWXFx6j'
        b'SK5DLItMsCBkpWEcyeABdSyey5h10f2NwZJEuRkpIZ825ARZSEwYOTBvJW8JyaGfJBcFC3NaQ6GCFYDdWAXVvASSAcpCaQ4ZyTEcapnx0RxsMZbq0IVq0kJCt9qhg+Qw'
        b'cmcmEl5w0Z7VAAeh21F3DP/cN5oHnMkdB9f6GpgPNV7y0dJIGMWyLkILkV4P03Ei/bcVycvGIWwQRthxo8dzm1NZAXgkmmQaI3VQFxq4S5tMKNZ1ZDMhh+pZZIiKg2kH'
        b'ocaDz0QFdkzl7WeNaBmku4H0gbYfr0WxNtri6XDWAZahDvbpmvE+QCacYCZoo6FmOG/DId4PzLeeL5f6IczmXjeKYT9U0lekI9Q1y1w5dLHholWVJrHBdFGa8J7SDHhh'
        b'BnTNkkqZ78tL6YAbUlv58rmAx2mD+epqnckvbI9BNqG/fZ3iTbq0QS6NzSxCaZnUloeHPWh9eBQKYB+2pEoZMH846/m6qDipKtKkeXKWgQ0NkH9seLdCxYre0c3EWjJ+'
        b's/jYmFjz+S1wGNfXEN1N9nC6t8twcL7UiCAo6B1e3VGkBV3JrMf2uI9lSMRGsqvZW082/4exnnV3PjkQaYaFiSo+rHvpqNE+HMIiOEJy2BrwKk5DkSdrIssxixr87WNF'
        b'TOAGYtDtPqhvTPlahONUsyZtltytLJutJx7t6wyfaijeKO8dk3Lgxr/WeMSPvkuMkcO+VD4cOzGTN6XDiRA2vqVhL23rqU2st0lQxCzZJgyG/XTGMuntgVwuWLjT+eiC'
        b'KnaNjplB0C61Uw6nyd/72SLiVKEaCtmgjx2N7Xwd0jyXZ9FVZEHJAp6Eo3xXXNcnR1YvibKM6t32CsxnuwLzttFAFr1rEY6v4dXQ0dhhwfddlRwPsn6ItpTylEE5Ixz5'
        b'nqyjU9djVe+uJv+qw+QbpE3TZMf2TKoHoW/SKtbFMkJkMnvXOqEgzWwwXNdO543AvawP/jGshLIA1k0ja0pqHSUqq4qUb+iloS2E96GNMINrJv2zCqfMdD2lsTJSsU5o'
        b'YP82Pp+7oxx1F/TOdwNW2st4L4+FQJOaBcikEfX0oGYFXBRh785pHzH+sSh1HjOzW6EnFx5TU+P4MD+v4Z7c9m7OUCPB1HsaCxXVvG0jfzjIUk8oNR9HMoY52cnM+cNf'
        b'V5sLZ4wpzxm2Vm9LOn/4np1SuLCQHDbzwuJVu3fzh9V+JsLVOCK2TApzWjN3OH/YaqcrZE22puGiDF909OYPr7gOEq5OW0DOpLD4SZZSUK4gZwMhdoiTIJiGxXt5jecP'
        b'v7K0EC67L6cVzYoNXsIfOpkOFuymr2MhreKiFwvBiz4qO0H/e3buR27sv6/ncrPUy3gVCLUhZ3KS+RQhiczeXnZwpkHbdEdynG6Jhixhy1Qs5CbEbBvUb9P0Tf5uyOqf'
        b'e1ubARaKil7enJ4kMZKNIo9n1R8fTEJf9CjjEiOjtvSGsTIUfi+MlYlBfxir2bQSuo8cA6gpLrMA9PcLxCMPxAQja+TsgLhgcBHLVPPddrDBGhe6UkibEUVjnW1rWj1J'
        b'sDdgj1XWciFnG5Wgw5wy02z5wH6gayjc3cZWheGEVGmy/DfqC8FG49mqUFmE8YdRPubCB8lsVQxvtvflD7cOUgoWohmdLKdXbL34w2ULjYXhyXPoqvCzdlrEHz69QFeI'
        b'X2XDgohBjAN/aGo5SPjYbhFdFYYLHdcK8TQafHuQgaAwtWer4pedLJ/OektBb+kSWs2OUls77ifJcLKV8I+tbE3suKlrTIT64EXsRXiyUihXDqK5DQ2nruW5fax1heOp'
        b'w1j9swR3/jA5TCl8E2LJFvUBLw/+8I14hVAnsJXu5CNfwx8a2yqEInf20DBc35lUFhAQt/9moKhJI3OXPf7e7GX+gRbzTRu/uPX2rXs2R2/dWmd140uVhaXftLG+FilP'
        b'Jo29fSn3cBaqikeNckk+vuDbuCnGuiW5MXderrn/9JavPnj2B/n0oSbLTQ7gmWvn39ke8u22KmN9a+PUZ2qEwV6lSxYpQ15bslg+4qm/PzF9x2XTqgLjzuPzTEqm7391'
        b'+r7W6dn25U8r1z4xbu1TU6KTlSsm52+6+u+4N5YUB5Yv3G/x2S/eAUemN89IM5tQ2mQ28+r9+TEpXxyZ9lxsx4cRrgHFEQUdI5587oNlNjsRZbXb7uQ/q/7GI6W2557p'
        b'Rx4fBWVPOrT4O6uZQ/P8b08d6l5mVZ73+p5p4/0Pv33pMePBK3984slp6V5rlvrWvLvg9kLHLeUpg/19rkYV1S+8lnvS4h8FRz4/8knXlJCMjp5xQXeWnf/ujfis7hC3'
        b'b98eftOvYtPaWylnrFJ++WC5serjN3dl1t3dtvapkq7kv4faZlvZh9R0jPI5Ou/e5dipVwd1TtbvHtVx7umOsRNenRJZNrP72yfv6GxfWZTQ9Zy+Y8jPcxe+ONNu9Qe7'
        b'//X2iG+fOejl3rrzufvNE4Ja1Le+gIiZLT9WHqoNvqGf/FJ064l/G+s/H/6sq19Qht2buQGud7ZE/yvYS5n41Q9HrZ6cm/lV47Cnnu6K87pxKV5MPGD51kfLL/jnrzn+'
        b'0rb71uFPXR7X7fxxYfnR1/PaOpxfH/PFM+Uvroz6x5iX7/1jsOmNoxnfpNi0K96NMmhoe27dtblHaxeffPP4kJ5nl8y9mSNPVLmY7nhjwus1h767svik7pPfX66d9Ni+'
        b'di/jJ+58tDx83hvDLigix0/X26R/P+uXwIUJbgsaVwefvnXo9aPrXyp1vf569bfPD3vl42s7Qp9sH/xZcM+/dce9+NaLNsX2xuwqPBZKWXCFg/5muMcvUCkod8jwDBas'
        b'YffBHoQaZmI+d1Ch8JZBzlBCSgqt+XXrGWxeoWZRLdXOhKQUOVBbmZNykXCGJfwy+6KYQaMGYjsRd+UGMqjCG5PVyB0SwXHvjY5YCBd8lYIiUuYO+6BrtZfkFt9uAXVV'
        b'5ONE2MwSH4WgyhDxpHMS9wZxcjwWqfss7RRyamsH9Xidv60iXH4dKXciaY0iXYatUIS50D2O11lsiN3qREcWU0mEVtlybMcadmcdDG1hfXZ21MaOENAWaN4Oedxm7JA5'
        b'HOZgJOiGQ9SmXkfE63hJCqe1ZYGNmpnzkFppDFwXOL0OLzJlEmEbokZDraQ/k82HrFHcti/LDLMlf051flpxvDBnmf2w/1tLnd+/6tT9kzfKPQaaiPDE0LiE8JgodrHc'
        b'TY+/P2Kws1vwV0geJx7+z0DkXigMmOmNsXw880lPfV1QAx8r5q/CmPnHp74wqKkO93hhRk175Bbk92jmv4J6pzdlpkEiM/kxYL+psZCddHXNL6UVJL+pzEWW+kHfZaa8'
        b'Rx6XEKN1j/wHh+fDPtsaWtY1altDHar/IduaPcLTQ7RuixnDqSEc7akBpzy2rya712q9Qm8znh/gOLjvnpH6jdDCOMoktJkYbdDnMFjxuw6Df4NuNJT+H3jbOCLg4Xec'
        b'VGdO6hSjxb+KZhV/U5eSI9rmmIuMtfpyZYZhs9JeYBCX9XB+IWWFV9hReOIFwtPl+i218/YJ8qa71EcpuG/XsSMCYdzRx6JkGuaawe3aZ2He4S9Ev59jV/xx2AsbYqPD'
        b'Iu3C/cI3RsdvuBumF/3eC4IQt1cnJ6HNXmS6vkTItFY7eve6yNGZJQ4mQtRVHrNmMp7u07zvgsoHHDSpl/XCUB5ye92jioiNitgUyjhAtocm/fE9tFuw4/Egto0MpS6y'
        b'Q6mbh357Mq2Se1e0LE5rPYsDlu1Hfcv2n+QvSwMpNPMfXLZ7hM+NtReuJyV6jZCdDPk0Wjoc7EWoHIOjGx8wBVMzH1OFOpAHtXBmOcVYDlFhBewJZmLpFji2Su1E4zcd'
        b'VGCzr6BjLRrYQ3a6ZC5/FVodsdgIzgaIgjhIJpATKYetFYdwjjUy9drg1zrMvjcW7fbQWLVfQADF0+kFipjnpYnG6+yDf400YIilS6EpTgEbZggaKgyM2nkqyCg5RS6I'
        b'I02WE6LeyoPpbuZmTslbIw3bdi0U4umo7p2qoDgmQVj+6ohbQ+bpHhM09Orvm78dCgpJ/3az3HSKIFfKxv3ynIbKW7Lkx+44fCZSfKjKnbc4LFSHbjNTU4vNfkDYVZYv'
        b'slr3zgfZSopgNtYP0NAL0NtKvPOhmJAgCOOFIcWNGirNWLslB4UYZRglBxMe2Pl+tKwUjmnoaWVZ0eToEveWj5NDvR019jBvln9gfJ4RcQYNXz358qsmzzo9S/aJLpm5'
        b'a66TN7F6a8teftWFqobIyA3bzx75PnX91YMLyZg6CA7iVvbIbuS8fI/jZMGsE9Z1bWWt+3rU7fyXhedBEN4X9n8P7NmMVI/8lxUz3QXhjnCg6DQTUZdCwXbM92EQJzcF'
        b'EVHzRTwx3ReKJjA22jyQD7Fp2C4n+5SZnLfe7MQfVnmlxh9z9hfinje/otDQ2BfB6Ye8il8KeGue4VOfn/BzLYnabP+rWZXJ0s/3Bo08/djeOXuumOVm2XqGmIzQj5v3'
        b'wojzX+zVvT1/23vh297PijG7cuyZn+J3//vWiZhvDTd5eX/68jbbL4cYzb93oHVluqn/YwW5Zxe84uEwXhnh77Vkzb9++SIkrWLD658IkWNd6v5V6276ZMH5CemGkdtn'
        b'GxqmmZl63fMTLt5Tu16oTxxlF5r8imNZ81Wdb8aLw1Ibd5Tsm9hxpmK90e6WOUnn4jNCx1Yc7Yhul4WOm9BUXNIe/+w3l568HVtuO/WU9fGz3m9cix17zXp7TVxYROKc'
        b'1oKjDXvej9ac+rA44Yuhn43MwqWV995UfBb7asg/mhOqlXNLtj1dFmP0wU6jm+8beo7+NrRkjY3w4QzXT6Z+crc40F0FW39Odd7m1L7xB8/tX7kv+ucvhz3uaXoG25+s'
        b'+9h26eHny1uefylkucktn8bnD35y4Napwm3OH+y+ERUy4y2re+80vTd37+KnErOtZxR9MTnxk+S8j9Kc3pxQ6XX6htm/NVf33Gs59fclr/36znM7tjmGtA+f+tQ3p898'
        b'mv2WePPTZdtcHp+9S9j/0glZ6F17U24sfUwwUttTw0adEdAm6MSIDpiZwhm6oiSRMkkc46gHRSKcxOykudO5nfc1M6AXIgX+TtQCtD5lsgwuQDbe4BxWJ561Y2yZD70B'
        b'0iWfV4sGwbsIEbrAI2/VYSPs06RlZBgZQ6GJCbYYGgWkkGMUK+VQEYn1nB3tgjI82serbtaNlEGXO/IocwuhEw5gvj9c3wAXqJ13lmwx1KyVYiNux+OOvpwvxANwRdBZ'
        b'JlqMV/OO7SUdaehjGrEtdbAMTuMxzqnO2BBPuE2pSn2VGL8FSkKcmBWIB5YnkM/syVthkCF1ODrGwZJ9ZDcdSx05QiVpK8eo+EE5N2q5EAt1tMQcHxoKVgXNkIX7RKzA'
        b'i6a8rSWbMUvt4y+N8zoR2yOioG4ER5lccYBOtXTQLcByftbt5UICYZOvYCkDAPvZ62yLF3RmihaTsfS/1LH/FUvmAXxo//HH6NrxP3OGTjBWsmhLjNc0JrylKTtTaVwl'
        b'U5kt4xYp30jjIlGe05D5RuPe1WhOyn3qMC6T8quUz6TG4yJ5y8zHuaGDVD7lSFM/7uMwlT2K5PC02B5FZHhaeI9+TFRaaFpcWnzUn+U55amf0jI/oz8+6TvGaT0Wf/oY'
        b'/2LEg/wnnhkEBQOOcRqNlOwwK3+Fhe64CFFi2miX+nhAysUwLbcsWt7n20B8pD+N3ziW6btD6+MCFQHkEKebGZqwWyBSFsWf50IJlpNThCxlM2iXYyb1ix738pPfyDRU'
        b'mks6YvRZTk3Yx2GfhvmF340yYLzdsGJ5sOp7LRco8t+1L+gxovMycH05/Jn1FZt6t2/GFXx+PhtooKLNiIkPTiP9OORPT2OjqfY0Mje5JzALW/iYaXNkuqm4Xxi3QBmM'
        b'e6D5fzaZWQ9Opvw3kykPiLMpSZSzsBMOz9357CsHNknx0RsivcMJCx4vE0Z+L4/eX/IHp0nz303TptTPH5ymTx81TZ8OnCb68co/PU3nB0zTWDpNzVjo6Rjwm1maOUUY'
        b'h6eUYXgNch8+S9RmKJvOkyxbEa34g/M0QPSSP3SeDCQnNtljoV7tlKTLOXHGhoeOY3zr/LCR4o5kPRMh+fbu6QvUg9lDSBSFcm96bR1m+OHEVfwWd/4iQXxhkUJPINM0'
        b'1mytIDn9XwUXgqCR9j5nIWZRQ1M8y/0FEC59eMwQehXrJChVghSfQU8etB3anclB7e0jF3RWiTIsGBVntGefqNlMMhx995LNwWtG4lJDxc2fvxhjPe/0fkdd0cxTVeRm'
        b'Kttr4zFZf9wSx3sBJ1+MbYv13rFy2ZSlz3Y/lm8ctexN2d5hnu/kZ/39zta3fijqmmSa1ny2RmMyLG21+vEIj5qvJ4/6x7/Wvn3xbJn/tMFN7391p313Z/mla7/KjquG'
        b'N70TaK/H4aNdIdjm6Ay1MXZU9aIDZaKzLnCs2kbco1E7WA3gcZIwXwK6TYfstWrY70LVNjR6NnWHcZBwGSFD2b2ULlkLF9VwGZoHYE/hGhRz+9x9WwRo8CXMxzmG1c2V'
        b'US/ko6EtknNIh/EwoZtHoUZytCPda0EXNrPDPYSQ0n2O3uxuSuEuG4v7oAlqIIdVPheuwMUBl2aEpamB5jFw4Te7kuyfR5ps9RhSkpocGR1Kjz+2Vef8ma2aSG9sjCWg'
        b'1xB2VpvJUr/Q2r4htBbFA3ip3zRTTL1HvwnpbRcrYs2f3sTnzLQ3sS0d6mNO2zil9fYhJycf0pEp0zFLgWexa9gAyqgv/dZYPRBjrlRealiqGy1GigUydocj9vsMitaL'
        b'lEcqsvT2yVYropSRykidLCFSN1KvQFytQ9L6LG3A0rokrWJpQ5bWI2kjljZmaX2SNmFpU5Y2IOlBLG3G0iqSNmdpC5Y2JGlLlrZiaSOSHszSQ1jamKSHsrQ1S5uQ9DCW'
        b'Hs7SpjQOHumVTeSILL3Vg6KU0ULUoH1CoWz1IPKG3lfpE/I1MtKWvDWLHMWI1OgeXf/wRGqX+JPzgMhGNByabQJ/xWO9DYx8RNhESqMfTjGpE0vmkIkZ4rGhpWecfh/t'
        b'VPwu7ZQzgzzFT/v+Y0CtAS3sD6j1e+Gr6I7gEbToXzRQVjgvYsnCRbbRcfEPicXVt5roGtb7Df0eFZBOD8I5eM6DbG5oceVBdwKdWTiciUu9oRFznFxkwmKZrjtZnnvT'
        b'J1IqVqbCWlVyShB515sxWI/eL9DI3AeZx6106BIibPUMoXQ1u1pJUJOiemMme5jIoAHax3NzioNECLnk2BcUGU/ADRYYGS9DGfcFdI784ejrz32l4yUTR5lgPkGOJ6GI'
        b'O0XD03jYQu3qK1J3AMJcObab4SWmyE1ehPXq3rjfcAByJk/ZxQ+Ks7vwlLrXw74qaeF8EU8sTGct0oW2CYzIUuhvPmSn+FEn/HhK7rkaj3MDnkNDlpMOeZMm4RmooEWY'
        b'jJGvJOR1L2vxJiigSAUmKJF3cAMK9aCdxXo+w8615Us8iZDlQN6LwoIF9H4D9s7bwV1OnSGEtLbfsZOvkZWI59LxCnuLRVO3aYWex4IUQmyhFq6w7q6FA5PVvY6zoMh3'
        b'ogyucu89FVBsK/nHEhQjsIaGvjntyT1JbcRGpwE+rkxnY7PccusMds4Guyi8V4hMZ+n3emgs95clw2IDZpwm4JFZowghs+cCATlICjY59jqtkmOdlt8qU7jCCvxcI652'
        b'l7NLrfj1o2UC71c+1rtIzrQEhRM2Yo0MOtdDFRvvuTqQ6Sh50sqAS33OtLB+Nv/6zAI45yh50oIz0MW8aUHlpPTx5O2iNDj/Ow6vOrAT9iijySRyWxa4kWhIVwU5ZqHN'
        b'mk2PMVbJqT+cI+yWaYqL0vZrOVfrmqlV/OrJa4LSbBp/GP/cVmP+0GK9cp47f2g4fK05fzg9SSmWyfhgJlgPF+KCg2cpNUupiWvijJ3FM5fhJNMDV756KqN88/tjrS4G'
        b'fSCUfpM2JTHD7gnD/SXLEiftX/bYBxblJa8vmnfAcMpn92569/wy5buP3S7OfLt0zibL+p3fdd2f3eD0w4V9O8dfkCe5X8uq2jf4S59nGlM3bm9f8Er45JUv2vse/Grr'
        b'21/bu1m/LpsQfXJp4PTBAft/hhPJtw9d+8p4rMmGL56edbAjZ+vYONtZZ/+uGe24oFJ/+PCqH6sO7ztX+snjjrpTplUHHNz22r8qfMvuZ+WWK62Heh1bdMveOfadT5Zv'
        b'z2n4cNjlZ1Pa1Z+eeDVt3JSY1QbO7/8twsHm3bgJ3xaH3j/1t7Urlt1c5lg5zqg1qzXjScfxXSMvnXyrzep5X6eJ/zCzGZH29d+OPnO0s+PD9XbXJ33n+cn+d49aao5/'
        b'9dOxcZUr38/98MUT4ypXLX/5q5d4OTecGpKPOt9/+hWr1NDHf92wftiy78//+pP+1Tsls30321tzluvYFqjq41ywew4NfVAbwViumZTb8nNw4W9V8XAZK0Q8M2QHZ4oO'
        b'YAvuYfB+riuAA/NpxOiduljCMiQM8mHRUCZitv+AaChwdgF3RFEWZ6iFu9uAxwfc/kO2PgcStagpNvkQo46Ed4ZjeNUgYTjjrbZBmwFhE/qoo0oTM0vEMiyDdq7KrKaq'
        b'TEmnSBi74vlQgXsZfEUJlwhjRoOfJEErp52OFA1WqZhBSMZp7pnhHBmP/EBKOuXxw+fIlhP6yoPIbN1OwXOBjHbK8RRWexKCMsiLO07Ygd1SfBLIgUMsRkmsfDqWLGIw'
        b'Nu94squoPkqioH6jsZ1kMXOXQ/XgoSzLLhq7mxTBaagP4RbP0hzb5dTTjAXTK4fhIZE1QCKiqqWk20Wk75BHmFpK1NbjeQsa7kGio6pxSwaLWDXFmbXRCEuhxVHbswMe'
        b'wZPOq7CIx7I5hY2QxR3MknFZ7Moon4m+PI1MeT1bHSOwmMi9NAcjSjp6Yqh6KJnJKxzpV4LNo+jMSP79MHc1vWXAWjnu1d/E5s44GjIZII2RJWrQVwnZIrYvh+vSraVn'
        b'6P9j7j3gqsqu/fFb6L0JqKjYQaqgKChFUUC6oGKXC1yaNOliQ5HeQXqTKl06IiCTtV6SSSZ5SWaSmcy8TJLJy0wmM5PkJfPmpb28/NY+594rKJoZ897/8w+fjHDvOWfv'
        b's/cq31X2WvR8TtIbMlmv4yn2gkVcSmehK40oc97WW01yeWSobocZfVrlEm6xkmCExB7rk8NVDBuLZ0UvdWLELqQa5rj5noIeY37PuMwvqM6iJTPYLyaI/xDa+BYKXdh6'
        b'gWFSGTBdUmJsYaAjZuU1sMVS+cVuJvVXPaGh6IAw9lVQ/i2BhgaH8bW46K6akPfSsaNCXI907ocVVtDg4sXM46Yi1FIy4g4NaXC9EeSf8j9aIj0ubvxVrtcQ5ujJkOez'
        b'jQ9kh41+vdJJoPalHZgi/tZdK5Yp5StbHzVmy48XPTfZL1tj/SeCl5Ye/66GvLuBYgRFY4MtXDsBGcJ9WmL/VToZyKpiq15Ki4tJemlvge/LJ8QPL+8twO6TpGekvlqF'
        b'cKVLEQ4RLxn0LcWgFl4JkhjzuGjzuHS+t+xhh8OKNXiVGvfHX77+bytGNuOqf6dKo+LSk1NfsXtD6msvbxXxrmK0jbLR+IYNr/p276lfSkyOiouOe+mW/kQx6k6ujr8k'
        b'Ld2cvy3yVYePkQ8vzZZGZry8W8XPFMNvUwzP3/ZqYytomTsv97KRf6EYeZecrNKXsRTRF/+IV2pXoXopShpBpPKS8T9UjL+J4yXu+ldrJ6BYcDmFvmTYjxXDbl5B0680'
        b'cKx8YLlb6SUDf6oYePtyQ5utudzKXjm4bGxOiT2b5iJUpLkIigR5ghvCHJXrAs5fIOT8BYKbwtUCHOxRz/ta1V6QUvMVysPLPROnV+0bzdFXVqyUa66dHsu6lj+lslQp'
        b'31KCa26dlJz+vKthhbtBvh3PufVrtnqIueL/Td+3YsX/s+x5d75an/CtmR2WQr6o2G19ltFkR3hnTm72y6ErTuH9F5SmvyQ/xMz1//nyWOKWQDVnk1x1KV70abJMdIw0'
        b'PfDL16tn0/idhuxA55fW1bmC2uV16zOYAwomdofhpMylgnXMBYITTvxyYPWzqTKcFQCLKpqwCB0X/9fCNV8iA4v29bP1rwu5cI3ewaZPwz8Oj4/+LLws5mu/k4drtvxQ'
        b'jF900v6ya65jPqtPZrdsb7FiI7e9qV7/KJqTGv7K26z58m1Ok6avgG+JK7d6ZYzn6RWKSf3XK2x6md6zm64L89j0zK5vcH/RppOJwDZ9lyYWX4YpSxEfNRlRh3FGD7FR'
        b'QoGSLmtl2I9TnKvMDh7DJLtrzV76ylEIk1GQF3c3810RFyTa6dN4OcYn0p/lu33QL42NiY3x/3N7pK8kUCL8g+ll03jT0NO/sld2TIkWCMba1N5p8HsugW31ZLbUMBnl'
        b'8MXEvsquibVUdUQ5+s/tnHzkVXfomZF/+wpbc2951toq468ujrlQG1/JX6AItf0joRxDQjngOYnqyZL00niVTyJ4pbc4zTwtPS4hwTxTkhAX9RLHr1CwmjJRCTzhxTnj'
        b'hpWvCdTomu+bu2aaen3oEtf83QJRGrv70zHTT8P/NcLiI1+JVvTH9NsvJRb1gjf9jzpY+ofrR28s2OJq/t2QHtU1EssxwcCw9OPwQcnH4QnRu/4wIHk9IjFaUGIfNb7X'
        b'8Yf2PvTvDyoe2MdMGm2//Z+53/mIxMHPo00+XPylpRqflPIAH0GN1bJ4iA7MwGKG2HvNCd4TM4f57GgN7wSBJ2ks+tUkYh6KNs7StoUF6Jf7W7EIOln8a1Z0DVsiOWfA'
        b'jS3Qrg1zVssEDudADnPnJzCDNTkyfy7vy8VCGBGfhjLs4SoruXgpue/lO0lwfSTwDnbx/RkLoQvqrYgjj8Ew1uJjJYFKgmgLtmMB56LYhpVk9C9CjR99b60iUDITwgTc'
        b'9ZbrjX8UDVOLS7vE7TDHOke+KusYqnC50dz/uaxpNVYyY5kpKH/8i9TbqvNboe3UaGZ/fQXuKjRY1TZVTMjScLWaF8uKW3ChuVNskcRkmaWydMrUd1mtCzW5PfGemhza'
        b'v6fCo+T3VHgA+56aHFG+pyYHhZyc4F6HX4t/vmHkMhn0HzSxy2yV/OkvNaIhi/P/fMkJHU0tEef+vhAqWb9foTKUBRpQIYL5zdC5Qm8byP5Nu/NsMFHlnuk9QZSonIXY'
        b'VAu1Cw0KDaOVv3wQkb+LAIVmlNZdNRZEjBZI1biwnRp7dpR2uZBLN9ek5ypF6UTpcs9VV3ynTOhVL0qf+1SDm41plEG5KGobd48Bd5dR1Jq76vS9Jn0vYFfcU6Uf0yjj'
        b'cpWo7VzZDGVZyxTtQp1CvUL9QsNC02itqLVR67j7tPjn0o/aPXWa6/pycdQOLnCqzEX3WIsfnUJdNlqhUeGaQuNCE7pfL8osagN3v7bsfu7ue6pRG+n+ndyY7E5d7i5j'
        b'ukOdC0+yO3S499vM3o/eQBS1JWor94a6UYacCWjxno6M6ukfSYw09YM9tDErJPkh85VXMPFP/6aZS0jyL9cHLJ4oSTeXpDIvy5WMOKLuFQ+KJtTOXR9FX0WmMzsuLt08'
        b'PVWSlCaJZEZs2jNhx2PppF+SU2VDKUaRpCnMIFJMSeYS85i4TGmS7LHJqVefeYytrXmWJJW1SHNxeT6uySysZ15QodcOHz1xyNb8SHLSznTzjDQp9wYpqclRGdx0N6+M'
        b'5Mr8ZUEsnCuWkfmKMw9cbRVFXRW27YraKuIi8QtPO4g500zpg7PPbgy3RM9Ec+WqOVH+Kq8U0FWsJDPFaDuXL/+qNhfbc26romzNj3FOp6hkmhHZaObS7Li0dPZJFlvR'
        b'CJm3RroKXJBNSGZe83N6zujOimOTpG+iM+hxkqgoIo8XzCkpiv5vLklJSY5LogGXO6VeglVWACkFVtEOzGBSX/Ma6/bytJCpj9yVbYc1WO7PVR0N8fEP5B36dqos7IqF'
        b'mthre4KvWdqPNVnyB8AD0cpn0J2ygGsmFqrfwBEhH1jMwzFbrE3HeoLMPkoC5Z1CbCSAPssXIRlwxwfccWBBFCxln8XHXBBRD6pxNNQG+3ACex0EYluB7kFRNkxuc8Ye'
        b'7lQKtm6WlQaX9emyYLAnmO/PtRPb9lkqQ/V+WOKriRSY4pyViLklhFfToBzKOOCmIRbFfy7io6j/cuqIgCv3iu2ZRn5P3wmLuBZg5dZbgrAigC/lejxZFXOxW8TVB3E2'
        b'sEi7osxO6B3ASgGUHMOeuOm4ZkHaa/TlF2KDo5XOOmCvd/Tv+684mSeEbNPz/sAgVyl9z2iZ0bbDv97TGBH784tmBY72mZ67u/8ec/W/7K0f/8Wr4OD7xZKTswYPuvwS'
        b'I0Lfbm93if/ue9suflFkq9n22x0uuiWvFecdW8zZ5+o8kf8D8Mz7/oHXwpPi8mwqYv94ZT495HcX/1CfAt9pey9j2y8Pn/Y6/KFE1cBTN9T6+0Pu26vaXHa+U6n37T+d'
        b'++67cb80n/uo6pv+w5/98g917w60NX37jfKQjvWfBbvdlNgeLH5D2dKIO3d38TAU8CkAa6BBFCHcbXeajwB164Vy4bsAWLRcGb7rwCIuuLY2Kc3P332/IhLPmsOPe3DA'
        b'LgkaoYEPK+ISLLKkKBg1IjjKqEaCzZ5+/lIsehpaFGHPZlnITsU7QJEslZDF1/G3MuOrLM54OfjxORcwRFNTEagbiaDTGCc4tJm53hlLScsHsg3epUIweUqM03D7eNRW'
        b'7sln1XZbQa+1HZYwFKAC/SJr6MrgnhymBWPyUCZWGbH8MhbK1MQ27nUu4CB2ETz2FxJ0rRIobRZCGwHaAS4UuD1S0woXvJf3PCADfl5Wax9ua8rCbDjqy4xTYiwbFYEJ'
        b'zCj5YC60citymh42RTb/XRyVQXwVQ5G2WNa7m+D/tAqrBegHlbo5QbJwqz40iKFSC3o5n4HbRWxmwbJAeblBnVAx2clDAVAEi+kcg9dCNbAEdHYUlfV1uBvEnx6CCjs/'
        b'G64AJOtq5A3jqqyolRo3MV8cZilxXEKFGLpk3S/CsZgzDJxubGfFFHclQO+KaopcXhwjIq3sZJb+TGMUJ0TLhlMRGNNjllLg9vNpZV8mZ3u16NiJr4r8nRlMVOHy03W4'
        b'THMtrmc4y1HfyNkBfBwrx2Sl/n1BB2+Fdl1mGrwkGijmr10lhrVek17G5atZCrmCXy0/+PjCKX9ZP7DyP/IBH9SUB7SeHUoR13JUKO3ntfQyjfxKgS5+mqlvCl4ah3HX'
        b'/AoecrmCXeGktucxEcNC4v8/uqk/yFgNdbH/rfBUp0oTk9MVHY4JPsYmZyREMbSTKU3l7EBzSYyEgbFVn6XIw/NMkEpSWdvcIwoEJnN1c2gojkd7zN+Swdwvqz4sTZrO'
        b'UFx4+InUDGl4uDxas+tyclJ6Mnfmcpd5QlxEqoQezkKDmZK4BElEgvSFICpd0bRavq90W3JqXExcEgNyDIJ7S1OJ8q5amyez5ciKS1v9aXwwUjFBL0lCGs3wVd34t3qj'
        b'+R6+B5wGuB6+n38r+uf+fA/fglaZG18Vq9fIpeNy2ah3kVTmPaj4X3fjX8rZ8QzDpkUmXOLW/Z/y5nu+ktRaWuHP96a7N+mTbld4dqfZL/5BNlhjtXyJsB4mjZkr6znf'
        b'vulGHVdSVnUvyfHn3I6FwlfL8Zcz9bMHazJYk/WdWEaQRK5cZXNl2Z/F/rt8rWHwBEsEhV4csGOQszjInznSYAiKNZ1xDPvjHgW8qZzGnDldTpmfhtsa/Dr8OxE/l1gY'
        b'WEoqjf0lCdzh6o/Dk6I/Cy+J8ZUFDVp+rOa2UGMpTmdZp1AI8x4rJnADO16g3bEnmCsxjBNwG3OfL30O0zp8Cla0LX8AcNr94HJK3YslTxU55sEjeVzg5epaEZn4yj7u'
        b'CJbG8qWo9x8EKVZJZF8lUhHwSgQ9bfAsQcMd5pP9MhS9H/JWCVyYHtY5BmNaliLO0onVCWGErn5OFrRQTpA1hN2M+ex69xBZyOLEsTi3vK8rcbUTFkMano1YJMT4RgZy'
        b'EYu1soiFVZMsZvF1a3XJR589H7N4SbhJ8sqbGqaloaeUY/qiTX0+fvEPZnH4lXbtteURphfPhoQe86iuLlvYQrPUfJItyiRdlBXSRfzSLHgW1uh7TsN4kw6SyAHScifW'
        b'ix0lianSaN4p8Vwu0Sq+jFRpekZqUpqL+SFFy3vZW4ebJ0fEk3J/iQ9idVSjHJjBnM7W225xBhij9pPBYTanwlbLlocZ6BdA7h71+IP4JINpMRiAJWj28zJ8xmfBGecK'
        b'0zxEUxXLIc8lLvR/fqacxmpk3Syc/jT8s/BPwr8VERs9KGVRmNcjhiWx0danLCW+wm8XCd8NKNugZT5+9hvrvmEdfd+59Gy99UcJH215YPC20Y6qBO1Ie3GMiuD2Uf3t'
        b's0mWKnzG6DzMmPCW61bs5g3XgGt8HOQJTEH904xXM5znzUS8fZAzwiQJUM5sZuyUWq5MebXER1xCaQ7O6vtBP5TJk+53Y/0V3ra9kxHrB0XnnlpwmmdFOAplOzlDMghr'
        b'sUdTuma1NhUkqA9A8wqGfbH1sbyABjtLJKMYjoVdvioLp/AJhWpcD6ecdc8wz7LHr0z8O7lSKK8eRRHxlz2FGqY0xxOvxOOjRst5/CXTXJ29n0tXeRlsEHPOa6W/TK/K'
        b'2OnPJwklR5tL/r/i80P8mF+Cz4Wrgh2CtnaFlqI05pUwjXjnUwIpH4fHRg9L+yWvR2jtiCaQKxbs+rPSDq2zliK+oUIfToq4A12xKM+/Zd6XddimlCOCPs7LwI679Pkd'
        b'C7CDMj5XmT/xobFDjjhXj1xrvrLquSVg6amrEYJsV15Kr8IXECibT9QrEWi7zj8iUNm8ZIO+p5omyZRekqQFru7PZ2mwMnWkwlmwKl/Bmx+xml0pJ14W3oiS1eD/UqR7'
        b'SBGKkaZLWC6ghM+XSkzOJP3GqubLn/u/Rff8PbIFcmFOfy4IY81svMSMtHRm+/J8mJbO7ESWo8h8Favaerz/YkV+G7MT6eGrhQkULMfmmirJ4peL3vklnMYITe85TtMI'
        b'5NrGuwa7LtOoMKL8IqXKK9TD9jwkHIO64xpYa8WOfPkIsA46rnEVa/Z4n4sM4ovdKAmUmoTpWu/wxaFCWXEYCz9dj3Drq74bBSdSF4kIuKrX+44rq12yCqIHhQiw+cLm'
        b'uCpJm1JaPn3zjRMBAWWdOoePa3nO/3bR215J+Wufe+YKbrc2K33vo1+OSqq+88Gfz9pa+L/1nz0PgkO6t74b/EmKes/52X3N94Zzlvx2h/s/MQ44fN6w3Ns088f/fve+'
        b'bp/Ttu8lJKz7pLvcMiDxD5Yuuw/OfS1LvWD0r/MFb8znvDd8rsH9U+vGLX/640b7W9cF41e3HXV2t1TjtLYQ+9WsfDZghfwILoxGQh2vtfuwOpkhjGVHVXit3XGRF1G9'
        b'8CAF5nGed3ev0NuYi1Ocmzz7zDkrXzOC8KS2OffvOTPO+btuFy7lHLDaJT9JoX5ABB0aVpzZJMF+nCSr8JHcAbzS+7tuB+e1VsF8d+bwJmSx+PSE8DhdeocbQe8UdFo9'
        b'9VlDl5rI2g2LX6A1Vb6s8/Q9VdlJYk6C+nx1CaqnJSvTYcAl+xtwxwy0hEbCHONV5BcNtNJnysnOdaIvAQTEy659KmzN6M/kVxK2tcbLhe0LJksLGSQ/4fyeuiI3ns+C'
        b'UBexM9IJkqSYE16RqjI+Zq9hIOfjQCaA2blY5kDU4GLgLO4uKtQt1CsUF+rLQq0G0QYywaxapE6CWY0EsyonmNU4wax6U22ZYL6ptIpgPhQVxZLok6RZKzOgmHuMj2fy'
        b'4dfI5NRUaVpKclIUc+K9+EgsiUsXSXp6qku4wvYJX+Ea43131jKPmcKJyALszz1M8sKAunmkJIkJ4tRkloAizyFOl6TS+ptHSJIuv1gbrIjCPgOmVo3BvlBHvEyvsIVg'
        b'QeK0FGkk94bW/CqvqiWeHt1IykiMkKZ+6YiygrD4aTw9g5EVGxcZu0JdcW+UJElc3X+ZzLtS5esQm5wQRcS8TPk9kxafKEm9/EwShGLT0sz5MyS25kFynyl/uzQ9NjnK'
        b'3CU6IymSyIOukePm8FUfJJ99pCQhQcpcztHJMl2qOHbOE0EGy9BnGQySVZ+znIZeuJKKvEMX82cPmDxNzpaP+6IkbdmzIhwinn/K8mMq/+B+JhkIeIQGmTs5Otvs5v7O'
        b'IOlCTBgllW+V/FlE+jyVrO5sPiKNlmQkpKfJWUTxrFV3fGeaOfcnyzR5bnIr0ImMMtmrpJBtQL99CWylAC2sMt2650DLLr7eCY7gTGSaQyphhmRWXawGZrNgmk+9rcIu'
        b'HNTMvCIklV0ksLHB1hRol9UX3AKT0MVcY2QZQ4XQMdMTpoI4GGRtEUz3HOchj4WtjQUW2e06FkDoZ/BECk6kn+JzA+CeOnbuUt+ffjWDxVMOw6DdipQI/ijk01yGSC9o'
        b'vKgGnTDlw8GgI3baAlMjE1VWpztOSczXyDTMxgUGGxTJCGS6B2AdVvpZW9r4KgtcrVSwWYfejztqX4QPtKywRkUgvHJRn1VUnILH3LOjHVQFWqd9haxgu1TVjy/qkrVN'
        b'SaAWPKfETkYnRspqs+ueIghw+pwKKyEesDaNh2GOUJOF3aR3Aq5pCjRtMrkSXtzlO9PVBXoJ/qyOeMKUVpiAywaxOAuTXD2BUB/OI3yM5l5mxTCj4j3oCx9rXyhJ87c9'
        b'ZrNLRYClllpXcDiT8+TgsNT8OVdOmaVvgD8MnJBhTksVgQWOwm2cU4fuBBMvSzW+fv5jnDN+egY/N5ALGcNtqOcrC7Rg72bFIXxCOfftYAybuGP4HvAYuhTH8M2gZCOr'
        b'9da/nTvkLsXarKfH8HEEKthRfPEaqLzF5aI4YzdMKo7Ib4BOayGrbIfdXNGC49AL9+Vn5GUH5OEROyQfhOXc4OZaOM+dkccaHLIhJMfOyItglisBFYrNscvOyEthfPkx'
        b'+VzlaCjEKktNjsYDPFlJVb6Wgwa0u5F164b1fJ2BJQt9WZ4udiQEyPJ09bO5FwjGsSNWvv56zyTh7nHg63Xeo83rU1RxgDY7nL2EcxzVwV3DW0/LOMzivd3wOIcbUBfH'
        b'oVNWx8HRhVVyEGFTNLZziTjGuwKf1nHgizh0YTMr5OB8g7tbL910edovThqzKg6F2vy7FGKRgSypOOR4gCylOCSELxTwaH3A00wbkUDHkrAwKxQwBXwbG1jSgW6+xgMU'
        b'QZPC5seFG7yguANP0lmSUAjBZVNHsVR4QB1KuIGTod06lOyfqpPBNmLoVBGo2Aih/bAHv0xNMHmW3qo2SEkg0hJk0PyWYHy/pQZff6FNJTtNJxVyoTMDx7VwXBdKcDad'
        b'VjpefOyqMddKReSUTJfIvrYXsQvScCqDuSz6xNiG7F5WNuESlGKv4kpsxyf0sKz0K+qp2jrEGWIlvHMF8jjii9RlBS8ycOoyDKRd0boC5bqpGWKBoZl4nzCSE1V4Bwev'
        b'pl3J0OCmBC0WujitTk+dymBXy2fgflFFOXoD9ybhW7GBrt8KZRqyt+AvMZSKDxlhJ3eNbfBGxSMVE9tolg2jSjvw8TW+209h8Fm6aM1G+WPSU3GKpnZU7LJ9LXdFBrYt'
        b'ewwJWxWBnslJFRGOYrup7Bkb3TRxBjvgYTrNQ0tdmyC69k0RC9TxdL/xsjvtWHBwsA3exXsqAmWcE0L17mi+7dEgdFiHBmB1KJZjXSiUs4qmD4gAmoU4E4FlnFTJiExh'
        b'Q5S5PDOCdhgvVYZuCtJwRjeVFSwvvIJ9wl1YhaUZe+k7MfRjI5aSCPSzC/APOsl0RYjMerZmwrDsmD+WkEgwhnm4c1I9DdugipfmLXgv2I9VdRcSZY66EBMG6fGV/QrO'
        b'78BJn80kD8ot/WyIgwKVBPrQKiYrrgDLOcH8LcF6wR6lKWWBXvj1Uo1tvLT+4pqV4ITHZ7SG4VtMnbYJ+J4igj+5y36x8LBU4mx4Xcw9C0Ps1YZx/KrgKj12jjfu5yEf'
        b'mmFIiZUwWMgR5GCpPqcijt7MYMl2UJiQLci+BMN8i6slsilnkXXn8lsfJ4g7DAtcpY0OFVrl8Bymeaxv7dnEl9847kIfmnersA+bpdf5D2+EM9/A50JWqGMuyJX/cM9h'
        b'+jAqWsw+LLlxWBDX9iOxUhorSKXvUZ4YciBp/W69Dalhb97s/SJoIuHd+r//2cnL18T58C+UisSPzPYLlNXgvXJhUuQWwYUf/0B4Xsn5SIl5zOvHQ3p8m7x/O+g3Pvn5'
        b'R646hY6R10q+bWhVl/sbi18fXH9vq/FkYr3ZT94Yqv0019Pkd7X6s6KL2V+sG6/3Vn5rm61dQoTm1keunX8Qnf9m2tpH/f99Of83A8beXjebTvYcm9Ye0HnyevD2hC7l'
        b'b3r+crTnwsQPRFccck+O13s9+vHAgaaU+LspF7/d9O0p+66vzW0+5BR24U+unrZ/ud340zfXthn+KvAN9Sx3v4a/2k42Jb77naJj9iZSkzV/vP71xH+5Nmg/oVE1FOzn'
        b'Yi8qCQs2crrsojcoPbHx8LncA291nv3a5VPa3/36Z661v3lPcObtE5u0uqalv9i+aUO21cKFP2Z+/JuC2ZafViy8/4sPv6n2t41/GvDp3z5l4Kvedtf37XUXr/oPnWob'
        b'j38n5vi7yRdHbrz/5N4NUW2OWdc7Gy4O/e7tDW6mNf/+wYZ2gz1vWm2xSOmo+FP/B1vdVC4tDf/mr5XO3Zr9EbYxyc0a77garh3vN2v9hduvDmb7D5q61n4oftht9W8H'
        b'7w7+x1zkTz2SDl8yXO/x+7r355IXzvQ6qfyPNHI68mPbmd9/cfqBZ3O63t/y5soSzn9PmvPzpCMdkfs+/PvA1U9Hv2Z84JTUJe3ax3+fb+h/u++DQ68F/bD9X7Nbsvbv'
        b'k9SJfxdZ+80/bfqPbI+FN64t3PoZvL39k+Bfter8bUa4Ya78Dz+94lqq4voDm1/9uTznE6fBT3L+3vTbiPk7Qx37dNyzXk/8zX9a9HxqUhu18Z67knp8oO0Pf5b8660B'
        b'H8698d9vSsUdi91/ess94M3ff71+i6Wt7KxcOen1QBeTFVkUBsfEcD8jlS8fMpaCuU8Bx23os8MBvMd5aMKIuXpIh+3BBj4TLoi7Th8LxVAGd7CPy2KLCIOqZ31DLTFc'
        b'KmQXTnP+Jx0Y1pHVJDrgJcuFPBDMuZc0CS3Vs1oendEsgW9l+t55vCtruYCVgVyCoUCJpOAo8zBpnucrtNTDtLusXi0xvw6XYJh4iJs/5B9wft65RHKyl0svbLXm3OuX'
        b'aZqjrLydrLSdG46x6nYxFtzQF2E+2SowAMtVaOi8o3uEMAAze/gKHD2ZUCr3PYXCPJcyiT04xpfmbTDWX1bWDsZxmDmuvGS5mvcJonXIK/AK8K4/K8EL09DIF9KtcMF2'
        b'PysYpTmrCNTsVa6KtuEc3ubuPa0FTfKCxPH+8pLEN3FYmb+3n/Bkv7xoDfYfY+6+TBiT5YhiESzKskSvuMhzRAnRcgG4i/ouDJ3ZqZKe6BJCI9SctN/IrXMMzfex7BAT'
        b'SftedpAJuvZxPkSlveFYau2NT1glk1JakABrwgx2YqzL4ntlY+UmfOInj91typFF7w5Hcs7D2PWMAmX4LNh0N04Z8XctQJ+VAirD45scVN6HvTzhjpxzUIBhfGLOgeF8'
        b'H/4ti/Wg+ika1sRcHgxfFXErdAlariigMLYLGBSGPGzij4vV3sxaiYTnSNkSEvbAEZ7iWjbt4ZDwFXwoB8JQuD59G323Gx/B1DIkrEKrvRIJ67nz9RpD17Fn8MFKGiTF'
        b'BHPFyTC4haf3Sqhjab7FdkE2IkHqGaLHXftMucIuOKBLSpShJRlUuoLT2K+ujWNCB7gjtMYuZXUCkw2c8/Qa3D/tx+8Iq19jzRB1M2E2JSjkGMSFyGHEz9pCHx+xuo9Q'
        b'bHeMaxm+3ksJ2ki9F/PZyk4HuKqSe2klFohzBKrYKVJLvMJtHrHmdAqnbmFMl9QtTCtxkudUxC6rQBiGEr6ULl9G13CrmBDnWAQnN1ROQJ1VoM1eXbrANgBLfANsaWRs'
        b'VIJWHE3mU3u7oAEauUI2QdYEI2hbRMTAeYK9Su47YYjL0jmGj48pypriI6+nlU35uqahsMRNyCHEkGtbVsI2g/a7jxWwLhdhJz6ALn7Vb685ynnBi61FgsAbKoEiMw9s'
        b'49O9H2DvumeypzuwBabEx01hIZ1vrVbOmuDoZnJCEOehTCRQxwERjISa8Hw5Lc2gvbCxtCABW8coJ0YEE5f1LHX/+bNiT93B/4e9w5fHxiVRUSti458wdPbVPOROWlz3'
        b'bhWuXYq8MDafYMzKX5sKDUQ6ihRkNZGIK34tkqUe02/PtHnRECsJl//oiNW4J7FRNIS8U1uNK6KtxPniNbiSPazEth43Bx2hjsiAO+4ob/myjivgo8OlP+twhbf1uEj+'
        b'KrHRZcsh8+Or8854hZc8dQNz0Cv846kbV/r2/7ky56qy9GrFg7kRucF2Kcbm4gJb6LcSTVmJyq8UF8gV/Mn2ZWHYZUtgKX5PTR4FfXrSMlKJx/ACFQHvGeO8Y8ECAX+y'
        b'ig8HqMvCAUIuIMDCAaJC/UKDQnGhYbShLBigVKSSJ7ihnKPC4rOhguvKXDBA6abysuzfUNEqwYCTKbIU65WxAM4rLpF5dRXh2xd72OVXrDx8lS5zUC97hLXMTx0pSVrV'
        b'eRnB4hDmXJcj5mh8cdThVRzyLMSx6qi75NPbZc4dsOJ8p/J58J5wfkosrEFTT+K9z6s7w809k6Okjs7mEZJUznvLv3CqNCVVmiblnv3VwtLcAspiF89WXlot6ECPXz0J'
        b'WebSljv0mQ/9H/l8v4qHlzUt0hU86+HdFMiZ1B5Gdn5Pu7cf5/2D0OS8amC6wlIdH0ZDYwZL0yAkcR+7l/tTfZiHEYuCQi14xxjvVc3xycIH6lBuncwbvdNbfLhoNuns'
        b'ahbR1sQGzp7eb64p6I/n+hhah+lF851n8jqNQrVTnlSx3jOnhIKfpmZ4cRgNa2m20M+wchFWhjJvaIA/p0zDnsnUfeoawBkX3jsgPqmNfYaZ/HSKYFaV7/9N8KBCEJCD'
        b'3XzBgDadvwj0nOhy+3Dp6YuD23iz/sdNHie4rxP3nBX8RDAuFITnxmdnmh/lv/bq4luKuiVeFvYEDCkLzMPPxW3YzXt+w6HInWsVnyEVOOzC+xme9OFmMUwvd21jkY1v'
        b'ANYypy5BwmMyTznXxcnvuI+vta/LFh7s4SxWavtiLRRzG5kIoxtwDB59ibQ9PsOAAMuIJV+qGadwNsMvyGYzli5DQLJGAsPQw7ednYZa1stZXqBRDR+u5WoTzFzIYGmT'
        b'x+EeoaFe6xc6my0Ut8JteKJ+A7piuLWK2iMSmO9iFBpufUFbKHOkeMTzK5keHiaYStmnJPDIzflxSomtonUr5ze35Pvce+6BLs7FcjU8WHDVHWf4vuWTjlDO4b0cKUwI'
        b'cnARnvDHGZfg3nnuOOMFeCTIPiLreSoOO8W5V+JY1QNBnDiCc+Zan41h8JZI6Ak0YSnZVk5CeGiMtbL2xM5QwftHPdKtn9ZRJVw7zPmzDuCwJof9bWGQK0krZG190+Jc'
        b'K98VpTUQ3eWuH3Stck0z2q1VsP3f/vrB+490//oHqWHq3eZdez0PHTvqHbLtaIGv2PFJk9E1yw9V9j3ekqKsvFS46WtBnV4XK9bvm/ip95tWxzZt7npUNv/GTs91Fzy+'
        b'8dBC8sez/lNr/+uDKzYjSmdiHJ/UNd0t+6u9dDjazadoNPgvHX8aWe8et9Mx49f/Uh3ys0IlrfEtbZ4/envbgvhOZYr4j69lv/b++q+9X/mg+ZMBjchQs+24Y+aHZlv/'
        b'Hl4TUPHeifHtD9NuEsh2mQmz77/8o+sTPxz6bWzfXzb9yOa7727I8HOUllzckPLZ1IO3J/6a8G2l33/y72c/Gl5SnfzjwEdnBy735pxt/Yl10GfX3k/d++cvrvSZ/EdI'
        b'ccPRuwkhW9+6cGbRynnX2n/ZZHcuzdN1pKP8t2/t+J5NW6LHzr+diN9/fPO/Ohr95v30zt83DP/icGvmHrWJXxb8m4HrTcPXq6p22/56YSFB/+MtGT8ZX3//Jzu++Mlb'
        b'pSMHGvU/nvjvHw92hR3X+PeSgIHQJw+0F6+PHt/5jdfc/t1o5MNb6X03R508HjqlfEfrk19cSr+YeTLmf4z/u2FpeEdVwxdllsYcEt5EtDrNDNSuA4p8FLJau3iYnHvE'
        b'xk8RQlHHNidmoCbEcTjcW8/tWVdDBbO+lNRwlExYDsXXZWxwDZMV1eALakCRBWfd4pQf2dzHrANhSF6Lw24jV6LDwjDCyjcA2iFXnsCy5SJnXVwgk7yIHQHYh7mrZZbC'
        b'+CHOKPQPhCmux2WfVN7mcjINhjlbbz9MHZW3uJS1twwPF4mhlrszPgEXuLZAUGXLd7EkI6s+mrvTCAuhYlkLn1uOmiKohYYs3sNQi48PWNFkOKtc/ab1BhFU4QA84c3U'
        b'0Y1YDYukSWyetgtIT+NsoWioZy05rbHCSfiMxe7uxlmOjjCxlhnQ0O9vArkyp4yuk/h8aDSXcLvLB8Y5qwsrA6x9mZKwUhGshxasgT6yHWHeXj7FQjvMTWQPCGCdQVXM'
        b'REo4DuN8ydAFqL5CTyHFM/2cldh5kbvmVCze5s275TYi9miRmQgjJzmqyMjAoWeNRCiFRbIS1WGKmy+U6GDTKt0vBMciOSvxlBnfhqgYKy7yRhoz0KD0KGejxf6T+Nzw'
        b'/9Aoe8Yy01qeeMCZZoNMtn810+yWwFaLM5Q0ZL0u1WRGkSnXkYg+EdM3IvabHmdsyf9lfYxYDyNWB1WDM6vkBpweZ0ZpcR2O2NEmHVnXTCWuq5EGlyLF/puz/tkzBsve'
        b'R2ZbqfBWzVaFpcPMi2XGlN7/9vpaKi0bbJdiRM6ismSWhpa808RXs6jIprJfblO97N3liV6abCJaomfsKUUTTdYfkT9oIWs9IOJsKjGzqqK1FBaU0kstKJZOdWi1PFe5'
        b'BfW0/4AibZXLdv1fztHm75HX4eHvW6V8pq25J58pw03lBRlAXEo3M7Po0mOhQfud7HczsyZRks7yPNLS2enNF06BLwD0NOvl2QKH/Pdf+WCIWiCH+kUXz3MAzwj6vwzI'
        b'hKYsLy7qJ8YhsTwCfQpGZH0E4C5WZcgKX83DABeDlkAXVwabr2tVhQUZGznFVMlKlCti3KFQLO9VgHkb4raOvSVMu0HXffe+rU3JblbLQel3bwcWdf5KWBRj7lZ98LOv'
        b'50JXyra7Wr1v/bL5w3fO96Q7zuNr7QNFEv2NJUaJEX+Zu1ld97d3r578RuK5e683FuZ87809hS0LtkdujG3NdvhhsVjyF/HxO7/R3v5G6yctLd5ZNj+I+vuBP0amOfRn'
        b'dff8atOmX20p1W62VOZ0t08kFBJk8LRQIIYzsqbLWBLlxrntWg2W56+aysoDRMdAI8MMUABDz6avjkA1X467cR/c5vThwTPP6EN4pMTBihB8xFUQKbVz3s97x09id9qK'
        b'UyX/lI5YJsJ1MjguWyHEA19FiN8SrJOfQOEbFssFORPXORueETYrR10paldKnmWi9quV7iY5yt2vuVKY8sfS6bOrryxHi7csl6MvfzVWuzYnLoW5Wv5X6lzKD6sNPJ99'
        b'mhoZG5cpK4MkK7W7ovDSKoLSk/dcJFzlXB1xiSkJUuaskUZtfqFQlb3Ms8WA6ON/1NhFsKpYUgrkOrVcNsBiPs70XIoT3r6qgOgRJmpx+ASb45Ir31ROYzfWOHHVWV+P'
        b'+Cw8Ptq6xkLiK5z4F9PmtS2mfo0ta5tNQ03vrN1/TtA2rpar7Pyzy5Y8hx128HnaI4os5BoYTcZWHpY9DDmusAk2b+ZjVlgm5YMEQ1DJHyxbyd5wD+fUfJzSWQLJITus'
        b'xknG2eNYxvpXYvn5g8w5cyzgiuwWPxhShTFslLc0fjF/6kn4bZXTUxrHoftfjUOdGX8qKosqnKnPjLDywI31Sh5cpbSotcLha0u/NTG28ngVtsoV/HrFAdB/NE9WfEI5'
        b'MPCEV6ClKJD/v94/qMT3tDqIhP3HlJMP7DeWws75qzmIxckH7m34pVj7fw2pv6S0TtWjKeloys7BqWkqiczNl5fZ09PTEpnpGWtqCI3XMSEsEO64YSC0TTIQmm/KYJaJ'
        b'GQ5JnzsEjb34hGw2i53KmWfVMj6nIeAJ1u4nw6rGNRlb7PWgAGdxfs0+J8iNxIcqLlgE1VCjRvZLG97ZpE12YD7cJ5uy9sgR6NIkXioRrscnMItPtKHJBafIbJ6QwDQO'
        b'nNBmxyjz8KHrQXgCYz7wxJuuqsSSqzALAzBsex26/WH04HVcxAeqOAaD9PN4L/RCN/bFXHHYjk27CUR0JkE73sUBnMCW665kfPVhMYybeF85GGQMpVsx1/NGvCOW4yLM'
        b'xh3Egsve6zZJ1nm5+CmfccBJ6LhmGwTdZ8xsyF6cPki45QFMQlUSDJIFWwozPjDjnLgLKx0uYZk29kXhmCGBmvtQg130M4/14Z7YHOwYD+WROKJCVvwMFiTDOLF8eyjp'
        b'+LGsROyBJzdgHhtOQPVa7Lp8DuuhZ98aHPUhSxXK6P2roUL/CDwMhbydfjSBGWzeDw9v4NBxaBJiHzTjHbxHFmczVsZCPzZDV9ZGsSbcI6u/w8Eau3Emdr/GQTJjCyPN'
        b'INc7Ee5G0WMbAmDBMtIreZMXVjAZ2eKLdWdMYST7ED6CCdqqMVcVaDxueZLeuxTqIF9jxwmcNMVO7KK/ZgOgEFpP02LUQYM1zu532+66zcgQJ07RB63Xdp6zwiYc1DPE'
        b'QqyC6RNp9Gm1jsYWXKI7BsnIfkjTGRNgg6P0ADadhxYHWDDADp2IAKiISXfD3BBs2Aill5zUcAkemRnCowRYWg8FMXT7cArZ0Y27zbArasups652WEu08Aj60iREdvXY'
        b'fEJr7fmcpAPXcMrswgZoDoSutefwIa1PA/ar0ctMEU01Y5cHlqlB4VF8bE/bWA9DzvSWwzS/Wcg7TTtQaeNOJFGSDRMm67GE1mce7+vcFOMCFntvC9iSUcHoPv8aDEFb'
        b'yCGoILrXggWcXHPdgzb3wVHI3Qit2GijtQdHaXvGoV18FPoiJVstoSpWCUrNb9lB7/6MnFhdrCNq7MJ+WtiylPAwWFxzGpo9oBnGoQfyJNi6CxusdhDCewyzYhhTx3vr'
        b'cUainIJtMHXyTJY7ttwITYAhbKF1WLSglyDywJEkvwP0iHYzaMHbwafp2TWnoWEfc0dFEO/dFjkHYA2M2dA1E9gPgzfO3TDUO30rYo93DLbqX92jjyNc6vR9or5FuLOX'
        b'+KrYe5P/tqs7iNIqoQmHdxOFDxFlPsIiCdYkwAK901HWp1MVe92w5hp0ZPgdisORnVhoQYbC0vV9treg4KJ6KDwy3cgqxOED/f1KybgUjhMirMo2lhzFuzCpAWU3faAR'
        b'b5t5Q8UZyMX8KF3ogP6g0JMOkQY71uLAIW8NIwNbe+X1jieJf9r8sSiUdrcRB02hiIRKrgT7nGgb5+EO5ouxJhCqcdwcWwOx5DQOwqSSPlFeiQl0sUpZJJfyLzmwlYUi'
        b'0upTWdlroXwjjTdCBNWfTbRQmKOvRrwwGY2ksa87GEEtreFd1teN5Na0WoyOL3ashVG8f/YU6fp7kI+zmy7AYoAfLMED9W1Qk0bSoA8KnEmOJprBAyw+DYu265i37nwQ'
        b'zK4nkhvC8hCo8fPVP5+F0zRkH9FC+znC/E30Gg/htgMOGe4M3bYmCG6zhIYz2JtAq9cfBBOW+EgZGiO2QScrnpfxQyLJjfvTiCBdyXgigqSJz1nBVIYztp5XYlm8eDdJ'
        b'AvevaBJXNuwNtoY+vXA/GHCDMpyh5VrAhvVESE9YGyKYgIfHoOAcMWv+Flz0cXNzxUZf6I7S08B8ItheIqlZuLsVms0ziYIbRG6wcFXgZHsMay+nW9G+TUIfgaISeEyM'
        b'U0Mc1xJx7kISiY4ua2yJp/WeFxAllRCpDkI31OO980dJJC5ZmYSlX7gI9wNohj1kC05ZEGtUu29xyCYLVB3mlhMssUd98Fqax3QW5tmo34KpJE5a3tO5Ck0kJvsO+Tvl'
        b'bI6EscBr143FF72h1ARuR9OLLdED+kgs5Tm5Efk2qibS6j24BLXatMcD5tpQux+bfOB+Ol1yG9mbdGA76aQHkKsrwjxXEiC9a1Rhdj8+Nt1B1DABjx3wiVEWdietuaoU'
        b'm4C5UEfsWoD3dGmheuj1+nABJoNpL7v0seTMhlgitjwc94AeWvKF8ztJM42eyTYj4u1MdMWqcNJfDZYwkEX8UGZLW9F1yIEkXDGRJenN83su78Vqi3jsv3FYJ4cmmAe5'
        b'RMpdMLnb3CJKApMkbWa1jFjFZszTwiIvaHc4QfQAnVe5JLKHzC1qAdNEM4RNc7BLdf02Wuh57PE6Y0eKvFXDaxe9dAGJyPukuFuOwKR3TAht5iTcSTtDW9pE6rAD5nOw'
        b'NBMaL6hKsd412tuWU+qVfumkbQoySCxU0TX1B71NTmMDtFyGElGmKbQSfdMqEn1D+9l4mukSWfPbk329sDhJG6ulYaobLuLIOmhg1GVHLN3lpU9CtDDjbRErAJlCREqy'
        b'NomDGAv40ApnhEc3hsN9VWwK0RDCOMsMriCuaYSqdJgQkLzdtgZzd9MiN5pdw1FVeAw9Um8LaPaEIUPSBs1r6fIKHWxVTTSLJ8Jp1iVubHSwxCcnbX2g5fg1vGcGZb4b'
        b'95EimNWgtXmCparBMBDO+EUiTDnPEFFbEj7E+QthJDKYBB4mWUAYJNkJWgw9rIivcdQAH56B6vAjcOcoPNbD+963ztHi3N93zRDKQv3PwMB2nLq1wTOc5Mcg7clQIq3M'
        b'ELScuyrEei9HmDthf03HE29DCzS6RZJuvkOb3WWqTytegD1iWNLHmpMmeutI+ZUYQdUFf8kJYuBFx+MuCcTKtaeh1hby/I3sjLA/AYY9iAWL4uHeDrzjKcRc5WB4HHUY'
        b'6rziYNItEOah6LCz59Gb67CJeICkYy+NVyhIJD3QheMqcJ+YodiYmGaClqsSWx1gEcrWEq+2bof5GzhzxY1ot5G0XQXWH7yCXYdoy3KjjmdDgXcy8cH9G1B/Yw1R1nTU'
        b'VRyIMcVGkoOdJCxKDmB5mL4TEtlXYY83QSOWxme+j+bQRr91e+zL9tYjzXhkHUyGEiXOwtTVPcT5izjoiWW0bPmk9zr2saBCaSqURZvvZNSI1UbunEToomnmQnsc1Efo'
        b'52QGYCuNMkXc1QA1cTSbAQIFeSKoyKCFL1t7jV6vhZToEOnOtNPQaYvt2GMapB1K6uJBvDF2SrHuGO1xH86fh7ZwmuKoG4wSLxc5w13W7o1mVX+SHlF4MTaTKSK8nbgW'
        b'J1NIyExg/javsxo4tn631/ENtEtNGdVE2oRQSLS3hdA7KHCEFT4SJmIF4QjX/VYwaw9jmZo7nVVTCcc2ep3CmsP0LnD/EO3wIg09mUqrNMMk0ektUOCIebsl0EZjl8BY'
        b'yjVXrY1+sIgPI7CDrhklIdJwaxPkWp2i7X6ktJ/EYT3M7XJyx6ELhNLqcE5KCLOCdNkgqelpJOGWd8sG7xkQ0RYdvgD3fbE+xIP0a5XUA5pO7iLg0QPzLjRaBUGS+7Cg'
        b'S/zdBp16OOADFbuzsUYnYFNMIkm826rEIu3XNC7B2HaXI/6mrtpEYcNQp2OzQYkWrU3DwBmnNu1QY13ZWrzwzmb6N3c7UX6v/np2aIieO3Ie8y7AvUNA8smNmItEFEEF'
        b'fHwJW7H9wBUSW3WkY5tpRu04RlslDLY5BaXbk0hht8BwEOadxa7zLlDibx1AS5cHxZ7x64O8jzMwU3LhJvRFWOKdSMg1vGaODaS2qs/hTCqRT/1xHArHIht7aBARrXX4'
        b'Y+EhorAlku8jMRfINqkiGV681pSWeSocaw9gIXQk76fl73eAAjcinB6s3n3GKNrJOSgCesLxUfJ5EtD3D+hqbHfcZ7TW0ZKk+5QWFhseCdxJSnFpO7SepKfWaBN1PUmE'
        b'kpBTxCaPz8P9HdBnFIXjSTRgC71m20Viht5z0jUkg2pgxBYearK0RmyIgeJNMHEh5aKJOwwm0EUj0BRNEqJJHE+zyg0lmp9yhEpXWNxJancO794ywieCBGyxwvrLRzLe'
        b'YQL3njoRJFHl7SSOKBeJKLOZPdh/VY3QT57hNVq/2zs2kISeMrM3wFo9wpNhITk+UHVr0/ZrGVAgMQ2+pBVCeryb/UDeXhL/9SRI6DZXhp6u62nDcDbt62PsOOWuSTpz'
        b'BpZ0w8m+bIonnftAGXMzsO6EFBavJdFXLREXCNCMchgCCEPMw2IcUf9khCnmp27CXgsiii7inaETSVh93ZzEQyvDvLE0gaKLLommmnRHNYmOelqM0oAzhPcGb4TeCIvN'
        b'3qIViARbu7F3C0nvB+fdsnVobUuB8W4VPEpKcTOAGd10YpPbqYQrqk4HOqpvw7GIQLwD9aFB3FUzcFcVB7WlWHScNYmlbwpToFmXzJW70J6NE5eIVMfstKx8SUQ1xel5'
        b'xV91Yx0WNhCbPmQ5HOstlGg56+wJd1aZGMG9JPNNR4lfhzfgnDfJrnKyUaZILT9OYsnyWHNlO/ZtJSt3EO/egGYLGxKBj1RpsDzsc/SWOmZvPh9NnH6buCEvgxihWQNq'
        b'dmPFZUds8d9OvDBpqJ8WQSJwAQfP4uAFYpuezUSCrfsIu8w6QiE+SkmC7nQyxYvIZDaxNyKR2eBOcn7ywFaadlUslBNwUMb+k6Qxi4hSa90u4/TJtZjPPFsPpTRuG1Fb'
        b's2BrlmvK2TTjYNri8S3swFgbVEelQ6tbNpRsxWLl81gaD00H6doJmCLs2YDFp0hRlBI6aTXy14EO3x23gohCh3E050wCIcaGULej+5h9NuQMvYdSd52HWaKqygAYvxZn'
        b'FE1CqEmXCHzKBruPX/fGWq9dRBSjJlvwtp1//EmsMI62VOEyQqLdxX6GOHBMWSC0E5B9N+DHn0HLx3KY8rvF+g+LBUJ2bIgQ3BMuu2Q/3Lf1I/zSaSUSCD0EBDR6jPkD'
        b'b9M0wwd+0BpgoyIQurODbIO07uyrczhqhKVXyQYpFQqEvuxYUh628yf/urfRdEuxRt1ayJX6aM/A2gwvMavtF+tDC1VLU6nAZg8tWveHNzU2nVOH+gMhuhJDUk7VtkQO'
        b'XbRSdQy578C7x7wCoCDezdiS5Tdh79oc0lCd0H5M79A5kuFV0BqBlQRbiImxw4n5XsgCr862zfCEQWMG9m5Ar1SChZrQmSohzqmFJTfIDTuOdYG0l/Q98WP+Ufq1Bx4I'
        b'SMIWnjSglWixoy1rczi7jSjv9gZau/FdZ+i5lYIgGjNfSkL1IWnhWtprsnTirkOBLWnY6hNQtYNMhgmiiLMEYap30HqNQI0zWUz56ZcC4IkfkXsPqYpSIqwJM7Ke8shC'
        b'K3K2vA6FjoThHpOgGCN9cB/GNhMu7oem/dL9mWKsVJXqYqPPZRhwwkepVptw7iIOnT22BgZUr2dIA1IvkQythh515j2ARrO1eJsWdojk0W2Sj33nz9Kzymg9688YxRPT'
        b'ztEUqvbSq/a5rtMI08L2yHDO/moWY54D2TO5tCojSJJ0yQHKxDh2ZleQA+ZGYf5pEm2dB3BsB/HOA0cr1siUpG3VAUJFlfRKuakmGUqknarS6DV6YPHIOaK1WijZBe2q'
        b'OByHVT5Q5473T5J1VUZmzKLqGiwN3xxp6bkeh9WgLhzqUolXFi11MnAgMjUV++in5oY2zbjY6dRpMiZHSCBXO+KEp/d1/egomLbQhhkd7PAh3rqzD0fsjhF7D3AdgNuw'
        b'WJdM+Sm4vQ5aL5EogHp3n7OB51LDzpoQLCoidT5nsh/vpdo5kqyYyBSTiOiFYRtjWMqIxaF9ZBRU7TLEZhMmzEnlFdrfIkad3kuYsZg5pSwDo0mlwqwdtKQTTRXC7Dko'
        b'TCIt3gODR4iFR/xuwcglMv7aaVdHfF04P8yCmDRNx7kYMqx6oXKfyfqbVoQ+pwKZPYHV0TCPXfb0nyVcNDeGemmadbopwa4hN3x0URtva+OCENov3jq3NyKjn5SYBw7Z'
        b'PeugITE66mbuoZuJw8Yq67KwM4pY43YECebx4HNY4mtkfIjMlyVoSKWVLNA0Uj57yT+E5ECV4zoinHp4uBb7dpv6bT4Ik9fIKCg8bRpkE3lIlRXTPH6K89RMBG2iQZqh'
        b'1onWY0GD5j+RRFKJndBdjMWZDJixhIdQetCKGKMPW5Poj8rMPdBMao3Ee5UUhhitdsP4Lhi1TybA3+6CE1HnaJkLAk6ZMMSJJKp7w9jRxgXi6ttmxEDj3qTo2pXM8IEV'
        b'Cd9J7DY8Bf1bSLJWQItHqj9h7fYYQqB5HkzAjsPtGwkE8td7EFroXqvLPFz++CDHwFMDBhPZWd8y3iGQFkksUHV5O82MVBp23iRRMGfG4CrZu/Ag4KIgHgsPJ5DMab14'
        b'OIZ0wyS2SmmGNemki/PoDkLm2BYZBQ8TgvfhlIkePNl6lkih0Qh7D9myRdmFAyZSnIsjqmFYf5Dsh4VUXLyofFAPm9bvxpqgFJJpZYbYZUB2WO01wlK5sHSF8M6UOwzo'
        b'B1m4O24j9Xsf686oYad3Mq17i8XOjI2WccbB3gb6eN/wVoaLNhQcFgUSxQ8S+RVD302SBJ0Zp3yg9BzJ2TtW8MhISky5QFwxcyMskbRlElSIcZz+HiagNyfJJGnb6nr9'
        b'NPaesSGx1IxDljB/+CKMbNp+jKRCLdtj2oQnJNiaSDqM6NNrLOLSzWB/emjPXqhJXOMdRGM/Xk/rMe8Jjw6RCC68pLzFPZ2ga0XGj5g7cUGJJEJbKJYqbNwwGr4cGvZs'
        b'YmbumRBNIUwbYFEgPFSxgZFzKsYwgCQEp/YSGTx0PoWLUGIb50w0Ws15Twa32JAcY+66Jn1ryCexRkRaAGNkIOCTrCAbS9qvIVxwOwQDZtCka7aOVr8MpqKIWbvdDwpg'
        b'YC2JlcHtLDs4dzNJuwkYPo0dJ6HF4QxJncJj0Bp1hnTCw1MMonRh55nUncri2INYb4e92VhsCxNbT2Bekj30xB8mvdBDr/yAkGurF8kbZyKSOX8ssT5DyqNlFzH0XZvN'
        b'YbHYu2/N2VR8EkgEV0/qI3+PkRp0xCfBGMmvdhpkLFCV+GApJYgM+GqimTLoYXmepLDWYZ8d1GWQSmkIjCeKIvulwVo7CfI1zF1wxDkOG32NE2EBBjKwxRkeH0rFBlq+'
        b'Shw7tRGWTgj2411tNVwS00QLAtbAnDJzknQ7Q1+MsQ/UH12/zplsrxJ6Kxw5QHJ8gcjiIfHBLNHC4hUyQocNad2bIiIZ70THWpBYLRedPxRzRQumz2FffFBgXPRFgqsT'
        b'OjSFZlK5Qxo44QelkdBwysoEyMy4g+XxWhIcPgGVhh7hF65hu2/Aht1YbY/jG2LPY4WjiMFXEkT5ZEx34IJ/9nV6+9IIPVJfnfhko9J2qDcMwYLI094XDwd4EY+XuWJd'
        b'2v4onNtCQmmUdrWUDESVSyQehjXPmHEihsnte7SQjZF7YBynt1jStjRi91ViuQoYsyAbqFRflTTkYMrpNTRoaRQuBl+hvSlHAghV6jBjcMCWxFr7VcNbujuJv5pI4Dyx'
        b'xqJL0L4vkRRPSIYnIZpj4dor6JrM2xmxyAT7sdpDNxV6jFTid5LMbaM3GSeJWL9b6HviGDOfIvFRJE5qE19N04t3Wh/QwSqzsxuUiMCbSXuXEYgfzqGlrttzQv0kjDph'
        b'82mi7WYS3I81mVEOQ2Ynaa3JsIYKY8wP9WLAx5AeNnJpE/Q64MjRXUhoxncDLU/pFuiw3UTsWXcQWtbQurSkkcp5IIXx02ZE5c2ikD3roXutM+RGQLEdgV9XEoabTlqu'
        b'JzFRE4t56jAuTb1FWisPps44kU6ZlDIJXqqaHuwIA1r7aH0rscn0Eq3QnAF2xazBUTWLnEMHr5hA2z546M96R/aS2uvBprU4k+6LAwaEcypJg87HkiLI0fBMpQ1sp4fU'
        b'bNmfDj0HlHbjiPs26HfTwNZ0HNaLvmAKffp6V6B2DZb5xdCDbsM9a1UH1kiCMAYtyyMl84AUj30h8Ti6heTCAPFPa/gWXPIi0dUAbccOuQqIKUqIIwl/k+CqgRnNaCzc'
        b'S6qZyLPUE8bWqQtJEMxeOk9Cr/cqmZ33yHpphnz9NWGkxMuhWw3uxkKBMw7YkAIoupkJNfvPI3OYdwlg8uKB9SRRHkNB3E5iswem0GlDPN5EHDFGZnVruPravThvAg0n'
        b'9vuleJMK7Yd+HFGiW+7ApLmRM1kd3dB3CAaVzYiTWmFp+5q1hGXLd2HVdaxiq1OcBRPilB0H6NPqg9C1MwznSFFivf62g9uwfT80Sk8T6RRhfSoppsXsc/hwz8GTkJeQ'
        b'ToLxnq3ACfok2UYREbTwCbE4D+URMHaF0HM1gbdyWrBxF5Kr+ducyeSbw8JUF79oVxICRVhyjeWJTmgJifgGtRgypr1sikrLvgGPgujPbmj2p7XqgIcpPjgaxqnFKZw/'
        b'eM4NGixIZZIB7O2KU74E3h5qRu0mFNd4hphjSTWCoFruFpKcSxliZhl0phIOIk66TQTNWGkR561IFDcSfc4445QpYd3TWKsR5wlD27DF0w6qxaTf7muzK1z14shiXLgW'
        b'4+NDYCDP96SzORbkJBO+XsQHh4gCJqBDHRecVBNI6QwJsTMUH2+/Ablk+9Xt8NLVDMX6KC7CNsIc/reuwT14zLxa3TAXQu9IjNLHHEaEcnuhz8cYm66G7DxrR29Xh4MH'
        b'8fYtrMBpM9KNReeh4yShrWkbldhkB1MY89FgLVnownIHWtiCBOKCRV28fwHyCQ+MkWqp2I1V61XpHXvVbXD0eizhv4KIbLjrSkq5Au6LccJUHVtOmXqZEr0MWyjrbcBH'
        b'7iehSsdDjUTmY8z1JjAzxATaXhwVkPquw0p7HWkw5J/zs9ifHq+Bi3phOTtJuhMkd0sMhsoUrHUIJSuOgdBJ59jrRB7FO2FM38WPuLjTBB5rwMzpqwm7sH87ya1ZbIH8'
        b'i/g4WwMLjoYSZ+STVdJPUqeaLJbNtNgNG7FNS0McbYKlZ+PjLlxyxGY/HeFRY7pvBKpVoEbfhDiuFmbjtY5Z2eHMRub+JLWdCwvrYJYF8R6YbSCLryzC3ZWge/seWotO'
        b'GN1gkwTV/luJKSrI8EnLgKY9tAcFx3D6oCaB93lCBa1Hc0ywS+umMr1BjRc0G6pfJ36rob+qYckqKfwqtG8mezLPYH8QTJtCq94+V60svOOL+WaXVPHBCaiJhXYYIiKq'
        b'CDnDXKb4IIP5u2jf50n4jpGCyMMeWyy6eWkzaWhCQKfo2rZAepk7YTiTY0uwDHqJW2pJSRdpniFZWRWRcZZ4sgOYMiFE2uNE77d0A+5txBop4e7pK0QxI1mmRFhDN7Dw'
        b'FhSTMCfscec0NJw8nvG+iMse7BEp+MCDOacqw0gHkxSLdzcP0d2GVcQDYduu0deta2Mi1U2xZ+3+bbTBSzgaA8OqPuE0xgxBpF6RE86shyV8sC9ek14qH++nAwsE3z57'
        b'EGqUoN6UxPlCFjb5QZeYfu2Dx1LSN/03STpWEjvdo+2o1tiI3b4kTYdo9cuw5jouwfxBIyx2gnkb7NoWgKUJLOJ1jHmrooJpffJ3kFAp1lLCQek6ovypq+bE53O7g5KJ'
        b'5HoMHWhuNfbGWL91kyW27Dh6WIkAA/GHJ1HEolEsTmth84HN2KtNdmP+ecjzxDkPGFLPJglTS+injgR0Nyve9VgF2sx8oEGTTIRee13oPLQbmhwJK+SbnliD/Vv3qKhg'
        b'0XFPLNbEO57BZBbP2xLAKnTGcd0UnLbT8nOALkesPeTiQcsyCc1KxPk9JO4LcsLN9dhZrDkSBnNw25zofURIsOxW5m4iudoQyNfkKGPuEknwpcs7SCS0YmEyrVsfEwXT'
        b'9gQ9aqNjoXs/0TRzxNdiiQlOOpFdUx0DRSrQFWsO/Urw0M0FZ5iBjrnHSYJN+WeRTn/iqELIuhvKLDDPmhbmoTF03YAGfSLNoi0srKx8XcUp5gQ9+d5BHawn+KCSxRBQ'
        b'nuHeJLL4CNHfISlRDX2G2HTEJJulV4TSyjXD44uZ22HQBha8oNtSGZo2E7pqOQ0Dl8nkGYFum0uEf0h1O7kk74HHvjuvYNd2aPSFPiv7ozipTEql4dhmsmrbcGI3qbgB'
        b'xiZNoQZHHAliD9ni0sltJNwaQsJ1Lt04se4MkU4R5u71pzEat7pu8rghIHRZdBkHAg/IWx33kHaeZZVxPPay2jisME6IKl9gZgfk80Xa9mF9sgBm6e348m13MzdwtXRw'
        b'Un6LGc5z98TEQj1/D61eObvJQY/vwjbtscfP2Yc5ofYLsF4Tu7nrvdJx1o/gOKsAIbQX0MKO35CVacKiMFK1NezcnZJA6MnKXHT58gewCrB+ox8s5cj9anDnFP8yQ9hF'
        b'mARyb7BytA7sm3HM5f1ghdh3Dkv3e/vTPc7sqN8SVPNvU4b3/f00SGQofHG0lFxtnHhzdoguaJsl3RPEjuIX6HITyFb2oKk1YEcA74mrzoYW7i33wZPNfscwV+67OyLg'
        b'B5+F2gC/DTDjSw+yEmAR6Zw7fI2sB9hN8qIUi08qfHfMl2sp9OK6GHFn1bwyRSw7M9hMNVzrN85eAksx9/Hv3cXsY1NnUXjCBT8fvnzQzSvch/t/oxvuf8ctQcAy0Ly4'
        b'p/EH2/hdx/FtOmwHsVwg30GsMuDeeSsO3pDt4OhutoGiQEuxbNuxabcfWXf58l0kccGffDO9ecgPG1QVu3j5Ar9RM8q05vak7+RbeMNY1qviWIiHHzYGy/cJ65X4bS9T'
        b'YmdtiKiLFBs1ie2WfLs9iaaQZYucV+xHl4vs8OdarnFZ3V75hhjstRRyt2iQhuz2O7RHvvJSuBc3t6tLKe0JLcfnv/z6jdpvJhseMv16TNb7byXurGj77X/+dP6ta5tV'
        b'9XxzlSKyre/4VOea3bnno+b9l0znK78w+v3sHzIXUlN0Xn8zdumPiz/7TssvOi787F/b1j6YDH/t0diT9uyf2b9VMt37aV5Eee4DZ1Un76ClkO2X7Af0fC3vhrmWP9H8'
        b'9I0/1932+dqfJGZDb3h5XnX/1X98+8hUePYnmhlrD/w+JuWAflpdd3B1SFK+41++9W3V/Sqfb6744PqRxx++7nS8eHC+6N/uhoUc+rA4sVNlOut46nv7KkLfdpzw6NW5'
        b'sutHXQfzM0THHKZ7b7quO/3O+OhbfzNad+adn5f5Hv6v/p7qD7TKswOkp9cNKH//bnT8tyq/HXB8Q809/2DdLuWRHsMDvv6f/K3n375/0+TQ/OSlsfNvnXmnzfya65t2'
        b'Pwrxyzz9Cwfb2u84WllNbP1r5gaXqu11No3KuLc1I6a6dft339x8pmND/e7RMz0fbdt5blvWb/a7/ODoxBtbv3V2071zv/5cJWymJ2RH0+R61/Qv/jTa/1vvxXcbH5nc'
        b'+OyLX09HNl+uV5vfPXp+4J3RD86sSdvZ9N+b8wPtAhZatP6y+7UzKhp9638w75T+P8bqf/5zoe+Bxjf/szm68rNtKruPpL5ebGS9Q63uBx/8/QeZIjTdfOAXk5K/L9io'
        b'29+auXfLw+vbIQ+/3ffRp7tLdv8hMud3wrjPf/v9rKQfS8oi78y2fGN9XMyDsL9ENbddzdyx++t/DM5P++Tk9aa3GiXv/zxssnFrw6H2L+5bf172q/HXbi4u7fu840K5'
        b'j/idc//1r2+OwpbU79S+dfXOk/m6uff8kvuzdb/o2ZgUcezzuG+97hRzLFL9jVbpuy0fnpIoD51GF6ex4pG/6s2M5134TLJJ9bHbwr7Pf/Cpe/b8wL/e/Nm6d84s/HvY'
        b'R28vlPzU9L/fcQ8Y+sU75U2hS6KO2m+WbLx3td39D9+J+95fHb73ra3fG/ivH0vbGyoP/qxycXfm8P32gY/fvzT+RVjenj2WGtyxAAsjZj6Tervjz7NlBc7zBUhcovDh'
        b'sqTgMHgkT/vXxcdc9ZNMmFF9vrvPJv9o7mSfKg7zRYTuQ66TZqq2ujbho1Ld1AwtAjWzYgl0CMxylNTivbkyRvDYEvsUV2XhTNYVbRWB6aELHmLSp4X70llNPChwxby0'
        b'TK0rGTire5UkXQmU6appa+CYbqaywFJHiYyC3nVcvyLSYyX/r7lrj4njOON7u3sPXle4gIUpwTZuXOA4HgZsbDCJgwGf747zMyTY1uo49sya4+64XVI79SONiWvAB8SP'
        b'2nEeBb9i4hhdLoYahzjpjGKpjeq0itSoq7ZqlH9a2aqqtqkUV6k738xhu49/WlWiWvG7nZvZ2d1vdu/7Bs3v9+H4XFtoaEXvz7VFsbkTeEQTmiF+nhIhQpsx/L9mMO1+'
        b'lxb8Bl9OvLxGueWHyDxqVkUxSy+5SJVECgMksPr+v+kUT5nQDQc+SgVnHkfjzz6sN0Piwvd78dQ/Cs5cReP/mjyoan6X6M47FOdTr/P/AiwlvCQFw75OSaJr1i8S4Ow8'
        b'zxuqDYspOc/GWwTRYBFMPNkEq9Fms6VkFmSaM0221OxHRD7bmVu44iBXzRtWw+p1USTHLj7IleYtWwdlaYXBwta1+6vZXlsDK5tzn8lbmylYBVtm2UHuG83sWxdfzJfw'
        b'doJ2UyXdo1u6EaiAeQ/9Rcvvr/wWoh/B7TxY/758/od63h4xAzMGXYkOJoLkjqoVhvXTyMP5tihR4nu7EaynHiFhxYDXTV7/ETOe3MlZFwqPohNe5V7RsKDmGTgu4YnX'
        b'xFpahbWZTZe/2fLt+s8rrLn9o+v5/pTC/EPG+KK9vuvvxWffFu2jN24/m9/f+NNP0t/88K8X2sZtOc67Y99qPzL1RXHtr2+mvZvQpsVtU321NdqM/7e9k4pL+vLO5efX'
        b'5ER9gUcXTpzeeTL+yZ2L+QunayuD6scVn09etNeV7NpsvPfVHzvbvqit/sWnMx9/Z+wnweO/axgVtiUy/+z+aKDx9mfbr95dsPXUzKVf2R1XTumnYveU+q/q1iz88Ut5'
        b'amC6cNWmul/uLnPPZDy5SLCciFf0x7JOBG5GftMxuPPODw+N7BdrnzjSmP9ZblZrZDA35VZkOG1H4Yc57dduZoR+1nzY+vvRcx+sKfjDkbLn/vRMTtuP2j74y88PnI38'
        b'LW3l6I5bWxPFixhf7HwQBISJFb34efKTC2RiM5eGEjy+tLOMykEd2N/r8jpIXD2Q2uL1goxXFp4V0DiZcpyjtJUGEtJPsNGgilQxGI138DhntQkFJZsYh7uf+LNroAPr'
        b'MXOPhU0ibyGTwUuULpOFXyCh5VA5ifm2cJCAl8TSh8wsp8MbZN4wYcfDRUCHPmrgUsr4RnQBnWnBM6zfV9fzSemxID7Nia0GFEdvdVPmd04RYyE6WD2ZgJ7nrHhQaF19'
        b'gHpcJ5mhTlAhON7DOPT4xTYmkjXWtoj16tm+24ljxU6Rs+HjApkmk7CekfNfXFXh2lDaWlNl4Mz4GF/dbsLH9lN/jY+iIRx3La8iR6KRXldSfW2JUBdFV2iLdiuehXon'
        b'Ooze9rB6K54UKtFskmnfSNzma3gI8vmNCE/h65y4yYDe9aApRka/hI9Bngsc85RyKLGMEysN6C082cz05CbQWIbdgWNuQw/+Lif2GNA1NGZk3p0ctcWOY3jIDaf1kLsX'
        b'ua/vx+M1InpBRGeo4ZajkQIyVHgYndxBbAB2Tyvm8Wg5uk4v34ZGV6u0PkH8LmuQ6uTJLD6OYtpj7DTT+LU0nPganlLRAP5BBF/tJTFHBrBE4k1LRXMhOkpNXUic+ZuU'
        b'mwXLYM5AryCleIbHZ7PxNLufs1vqk+J5VvROMjVxqJv6dC+Zk11woStFZJRBD41qQ3qdKFbe6ig2cS1N5iVL9qHEUma2G/jwvjQcx1dBlfwljgzTNL6IX2ESBegk0Bhg'
        b'sTnl9zdtN+4z4PN78CQz3DCe9EKlAyTJ56hWeX2WFpHYIL6Axi2o31BADD8IGo1unktZxqNX0tGQhi4w8tc5Dzpv3+AoJS/Myx5HmYFLzxFSO5iSgbB0o4sMjKsMD6WS'
        b'48nLRK7/kSoBv45eNbOnchYdx+P29aUlAfLuDbjpuOBRYL30I6Z6iGHmHLPDLMnF4fcc+DS6rM7lMSqa/1/5/5GvWDAPAceDJNQRcEpWC5UBsNAtm+q8WZJ8VODBgb4b'
        b'aKzZkqprpKUQ+s85dXNbBaOZ0aihRBeCcii6kbg33aj1RYKyLgYVVdPFTsVPMByRQ7qgalHd2LFXk1Vd7AiHg7qghDTdGCAxE/mI+kK7ZN2ohCJ9mi74u6K6EI526qaA'
        b'EtRkUujxRXThOSWiG32qX1F0oUveQ5qQ7lMVFXII+0J+WTdF+jqCil9Pb2LMTo+vmxycHonKmqYE9kp7eoK6xR32dzcr5CJTOqpWyCHQ1tIzFDUsaUqPTDrqiehi88Z1'
        b'zXpGxBdVZYlUAaNdz+oJd65ayRKTSJ3KLkXTzT6/X45oqp5Bb0zSwiQEDO3Shac9bj1N7VICmiRHo+GontEX8nf5lJDcKcl7/HqKJKkyMZUk6dZQWAp3BPpUP00IpafM'
        b'Fcjt9IVAXOtBPMbsXRRthojNBbAeYCMAyLJFWwHWAjgBVgKsAPAC1ANUATQArAJ4EqAOoBZgHcAGgAqA5QCPA3gAtlJyMUAjQDXAGgA3QAtAE8BqgE0ANQCV9CKBeLgZ'
        b'9p4CeOI+jRIepJT7sdWX7Q/FVrTuriVAnhTZ31WmZ0pScj8Zat/NS5YXR3z+blBWA2Yv1MmdrcUWSojUzZLkCwYliT2ylDJ5G743sdyt0VvwzdNzQfA/5fTWLfVk3PuC'
        b'cgOUVJDzEnkSLPz3r862bCqX+HdHDeDJ'
    ))))
