
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
        b'eJy0fQdAHMfV8OzuNdpRhBDqp87BHaDeZaFKB1FUULk72ANOAg5dUTOqIAFCqFio996tXi1L9owTy5+dYidfvvhSHCexYzvlc5oTy0n8v5ndO+4AIez//4VYdmZn5015'
        b'89q8efsb5PdPgN+p8OucBBcRFaEyVMSJnMjXoSLeKhxXiMIJzjFYVFiVtWiZypm4kLeqRGUtt4mzqq18LcchUZWPgsr06qdLg/Nn5qboKu2iu8Kqs5fqXOVWXe5qV7m9'
        b'SjfLVuWylpTrqi0lyyxl1sTg4IJym9NbVrSW2qqsTl2pu6rEZbNXOXWWKlFXUmFxOiHXZdettDuW6VbaXOU6CiIxuGSY3P54+I2D3xDahzVwqUf1XD1fL9Qr6pX1qnp1'
        b'vaY+qD64PqQ+tD6sXlsfXh9RH1kfVd+tPrq+e31MfY/62Pqe9b3qe9f3qe9b36++f72ufkD9wPpB9YPrh9QPrR9WGsdGQ7M2rkFRi9bq16hq4mpRPqrR1yIOrYtbp58P'
        b'48ZGQMgu8Q4rB78j4LcbbZaCDW0+0odnV2jgfmuSgOYr6Z3ZwEeXIPdguMWbZowmTaQxJ3MOaSDNOXrSnFaYa1ShYfjB0JkK8ngt2aQX3P1oxfgUuZaRZkgzkkZcTxrJ'
        b'tiwl0pKtQjZuxnfd3aFIVKWJFlAiBT5C6hUcPhaJz7r7wBN9PD6dQBqX9YO3stJIsz5NgaLIbgE/WDFaz7MiGtxEdmaMSCQvjYQCGWR7DlQUPkCYmERedvelbd2DH5Cr'
        b'GSNWk00j09KypAJa8rIwHG9SQCW9oQw5UoB3OdOySvFdsh1gkW0cCk7j8bWCMe5B8HwQOU5uh5Ab4WNXk9tO3EjuVpNby3FTeBhCfQYp1OSVGXrO3YNC27VkCGnKTCfb'
        b'BCSkkrvkEYcPLcyBp0PhqWl0fAa+Epdm5Ml9sjWDbMONObRBuDkp26hXodkz1TV6CxSOhcKTy8gtchNak5mjROQsrlXWcOS0fpb8eDG+k5aQbiR38X5DljGRQ6HdheBo'
        b'chwe03Enh8j1QQmpBnyUbIonjZm0SyFkJ09ehlloKeH8ltRI79zvpCgZiJDo/xYl6+Pq9fXx9Qn1hnpjfWJ9Un1y/fD6EaUjZUTlGoIAUXlAVI4hKs8QlVvHy4ha6o+o'
        b'tLG92yGqSUJUGL9Za3gYGZ0583vT4xDL/HChoOU4hr0VR160S5kvTAjSHUY6yDNXlCWMkjJL5il1/YQIIDDm0LzikegCqgiG7Jv9YxV/y5sGSP/hsL/wd4a/XT0cVQTR'
        b'tazez11TI11yzz+ZiOM181+k7K+X/DW8JZyL+xwdm/Hz+ZmOJciD3IkUMa7iK0pYM01Jc+LiyNakVCPZii8UxKVnkR2GxLRuLxrTszhUFR40GV/GG90z6BTW4ge5Tpdj'
        b'xXK3EzDpGqDDDXKHXCd3qshtcjNcExqsDQoLwTtwA942InnUiDHDR4/Ed/E1BcKPFgaRK0PxPncaregxbuIzMtOz07IyyA5YsdvIVsDzxkH4FdIMLYozxCfqjQnQxPP4'
        b'ch7UcIPsI7vIHrKT7CW7Scs8hHokh0VVzPOhDR18NfxSlHcmeymZUCrI08o3wESuFWBaeTatAptWfp3Q0bRycoWB06rIdtD5ts1ueFvhHA93r/T8IsOy6LUfvn5t5/Xr'
        b'C/YOUD65aJn/2r2IJwtfu7XzxN4TtTbOqS4JI9POGmJ2piYLZSEofWvYuC9D9EpXLzoDp8l5E8zAVhgCWJ2K8Ry5jo/h6/pUF11PmfhQv4REGJxGA6z2hxxS4e28cfEE'
        b'9hAfg4E/l2CMSzXi/Xk8PDvIG8nDha6e9OENfApfTzCS5szhY9KVSFXEkStkP94vPb2DzwBda0rFVxDi8R6yaS03C2bkrp7z8HF6veCgXfa78HB52n1SqcO+xlqlK5V4'
        b'UaLTWm2Z4hHcNpE+d6rowE0P5qI4h8r7kl7hCaqyVFqdwLesHoXFUeb0qE0mh7vKZPKEmEwlFVZLlbvaZNLzreDgnqK/g86mQ0kvtD6Kfk4thfEogldxPKdiV3cM5BSS'
        b'M2kJ5Go6dJeDDu3npgPGXJ5VwrfBDTadlK8AQaHYoShV+LBD6BQ7ytsu+uB22NEtm7GODHIIb3FmKsPwXUDzCwifwydXumnRaaRZyMhU5jsRp0eknmwkx1jr8ab1+CS5'
        b'maME5D6COCXCt/EhpTuaLpOXU8mrpClHiY8KiJuJyJ5yM6srj7w6OyRLiU+UIS4SwaI52Ed64RR+rE3IUpKGCMTNAZKbQo6yF/AeB7mWkKianIS4hYicI9fWSy/sIKfx'
        b'IbJ7DpqfjdAalEVurpVeOKcqILtVCDe4kQFRBNynD2KvRL5ANkzkAXnxcUQ2w3+yP4x1HV8dh3e8CE+2FCByBv7jy6RF6uL1VHISv6JCE/AeRPbBf3wfvyI9OgjreTOB'
        b'Z8DpriJyF/4rwxigeHyCQDEBcPsBMET4n9qHtS0YH19DID8bX0PkVfg/IJrlK0VyFb8SjtzkICLQuONTlrsjKIwtwxaTUzyqsYGgE9IzVergzezB+QIi5/FmNAzEhMPk'
        b'NoOKz5ALQIp2q9E0fB8lo2RYhoyR9iCXyANo7D41PghsHO9AJnIDX3DTJdUfKOFVctNJbq4ADOxNzpDz3GDKCBnF8BEp3p+uUApQhmrQ4oi1XA3XAOKhQ1HD7eKXKyg5'
        b'YutHWkS8h09M9nAleq51ObKF8TR4UoXN6SqxV1ZPmU+rpE9UyE2FUXzSpc6QxQ/GzFNJC74J0k5jTvaACLJNj+8II0bgpgz8ErQ7hFxG+CF5EIKvzSHnbDfPnRece6GW'
        b'xb1rhmx/VbspN7r2B5/OVHzn2Ouvv/vm2LTPuf3NQULju1eGD83+NUa7hx79SqvdN7Z79bJDSZVhP3gjV7PneMkbQSXZB5I/+sOhO8Wa9xrrbe4+o353ZM2PF5ZueXFR'
        b'36eZB/6un9Tvq7zPFg/ijvzW8f7hd5c2bSy/9Xrq4fThPfr0GLMmcfrfdl1yfOfvr3y96+2M+v98vXTAp39U/2q5fuzTj4B80gkhB7JzEhL1ZKsBoSH4hgpf5keSvRWM'
        b'tPbFd8hmKow0pJUvzsxWohB8nSdHSOM0RgLJy7AELpEmA0hoICTq8DHVEn4QOZrp0lH8WlvO+CLZCnIXDNkdvAFfBjLabZRAXiJ1I1yU5QNybiCH/aj3LLxlPIevZ+Az'
        b'7SioXtGWpAZOpCfEWlViF60mSlMZNaUCE0pVcApOI/8ouGD4ieCjuAgulIvlHFo/Kss5PcFVdpMTRP5yq9NB+b6Dkqj2LeEddEU4wn3ElVaT5iOu96P8iSsdDHxvML4N'
        b'mGTL9sMlBepFXlKsJJvI8U6oLOPAAVS2cx5c93weHCSJVq87uqHB6J4yCJkXKcanSAJTniUV7UQRi9Vmc/zBiTPRLJabGREJkpVuNl9tDp1Y018qWi6GoGikWayKMFec'
        b'GC8gdyTNJFeGj0wGUHg3yjUWF463zfubS3AugEeD99T93vyZubw00/JOadzeTzZcO3BjwVYxb39tzwmxMckG8RPxE7NhhHCj58TYHiNiDqWIefPzYosODE4xbImeG5Fx'
        b'mEoD91Uiv7DXh2PyQRLohQb9pPuGBUP1PEPlMHw0nvFyxsiHUl6ON+PjLqoukPoCciYhMc0Qr08kL48A4Yw0IhSrUyzB5zQyTXgugkWWlFtLlplKHFbR5rI7TDLTZnNe'
        b'FMvQTAtXQKtIP7QSSmyiR11id1e5HKs7x6ooet/Nh1W0loU+COcCsMpIseo2EBtAqFRQf/D2nEQQOkHKaUzCbDWRA8DIJ+NDKnKWbMJNAbqBD8WYkMcBkrUKeRxDsC7K'
        b'7rSdQ9oh2EAJwT4aQhEMlUeFmReJC5bJuDRuWCST0l9aYzb8K2EdKmC5kauUCP7qTGnmzPsRPSQMOxsmUPQtPxtiNnyQmyFlXrOHIRDe5mcXmQ03nLKcP2diNNXBU6Nm'
        b'mReNyw2SMm1L+qJx8PpbeeZFs+bMlzJ3TdJRa0PqKyvNfXbmuaXMHxQNRqlQ55QM88ARU81SZmS+HuVCZniJeeDnQb2kzJ9WGRGwifLyAnPxe7EOKXPUGDUKhZLvGc2Z'
        b'VxcnSJlF/ejyQOa3e5szb0QNkjLvmoahTIRy/5lgLr40VCFlehLjUQFCySNjzPzelIFSZtr6WGCcaNXrpeZJsavKpMyxk4MQkJ5x/1thrkgfK5f85yotAp052ZJszryU'
        b'yUuZv5neC41CqDol0lzz3eIhUualOf0Q8DXN1yPNNe+GVUmZFv0gKhiOU6jNxSUr1VLmuYkxILGg8mF686QxwcFSZv+sRLQIoYi8KeaBQ4rk8SSlo1E51Lkv3ZyX6IyW'
        b'Mr+cNgIwAdBDbc77uCZfyqw2DUdm+Pt1jXlaYvZApB+8Rltc2n0kmjcWoeFoeFF3SXZ4Fe8oHqkAGf4lasAYgV/Ctxlp0ZDDk0fy+NEyqtuOJHeDWS6I3hfWjlT1g7Uz'
        b'Co0iu4YwaWVgKL4/kkvELQiNRqPHT2BF+wIbujhSOW4uQmPQGHJ0IiuaTXapRwop+CAMLxq71OCmq7CqesJINehl12Fg0Dh8AW+XBK0H0LoT+CblffUIjUfj8UOQwaIY'
        b'9dlBtuCbihUwQhPQhOF4i5vyhz4jlE7FQJCx0DQ0bfJIVrQHfrXAyUNdx0DYR9Pnk/1ST1rwqUKnasFUKqjPwCfjWGG8oXick8OP8B2EZqKZA/E5Vrho3iynMpzUITQL'
        b'zcLX8FXWl27TeziFuSByodloNjk1QhrQHTBGx5zqWLwF8B6l4gZyiVWdZYkk0JWNeCflXmnF+DgT6iaS673JTQUoVgAyHaXjncNZ5ZOSZpKb/FSyAwR0lFG5jhWejreo'
        b'yE0VeUiagE2gTHK/WmofaUojN7k5IEKiLJS1LESSF0/g7eQiuakcBNiRjbJHku2sJWS7Zh25KRTRSchBOUZyTip+NAdG9aaanwBLBuWC3HiPtWQs2ciHgPYGS3YOmrO6'
        b'N8vMnW8KUeBzQDDzUN5gvEkavevkEa4L4dEUBIQpv1SGB0L1fbwhRIXPATIVoILcflJ2HT64LITLygJ1CBXiV8l1qXUno/D9ECXZXYrQXDSX1A1mAO34TEWIsAafR2ge'
        b'mucYxQZ7DKnDZ0LUZC8G0W8+mo+vQl9YJYfiySXchBaTRwgtQAtWWCWQLdnkJm5SDMe7YNBQUWGo1PM6EIrug35PHldRJrCw1F7xz6+//joCMTI5f+U0s+GoiZMW1saI'
        b'MagC1tfRBHPek/k9ke1WeT+F8114kvPVtcodE6v44bF1v7v7va+yzLXCgDD18d/wP9/AB38ya1Tqrp/mDn5p8YnUs1lHiv8R1achPzfqVEv5xS/Pxq5NUY4Ptp770Zj/'
        b'5lM0n9mtuwa8+Wbd0BuZjsN1ypgFJ0sPdJ+7oORIc/3lt2J+9odrbw/7Iu4PIz8cqb5V8+HOQY/+kz1p/t/+cvvfh/v/+N/OPi/sGPFm6YO5S1b/MfpQ0Hs3d2/InHgk'
        b'5IOod35l/fo3b7xu++qDvdX/+N4hVFbhij12beG/ei4++W7U/06urX2/8EeXdEPf635ygfVFQX1gwjGUAVJrfzo8u8nt1TBCG/BuQzY1g+0wcCCdXqJ2sP2kRVLuT5BN'
        b'/RJ0+FWfSADywAZ4SO2Lc42lII4lgMJ+hTRnGdOpnTKK3BNIfcIkJvsWz8dnSRM+Sk6SbRlpVMlXjeN7guS6zzWAzuZtmF8nvpKK71uzjXHUAEp2CCiS7BTwNXKN7NUr'
        b'OxQmFB1xfj8RQyuLGO4SE5VlmXxB7ctIDOUUfASVMfhojv5E8QqQA3rRtBABkkcEkz5UnCPaJ3sIIHu4SzoTOThHd5+0Ec24t1faOBpgIKBWzlByN8FP2MiCCyhnL0mW'
        b'Vz3ZoIRJ2TqkEzGDGiCRn5jBdSpmlD9fjlVLYsZ6RygIBA0rhFxz5qd6hSxmTLYGA/u9VgrSaeb/hA1HTLsmB8kZB4in+JqeSajFeC++YKstSRac0+Fx4rE//d5c9Nq1'
        b'nSd2X6g94T5ee+HA8M3DD51IHbhZH/skw5JtKbe+pLgem7c/xbB8S9EW7Xd7qY5P2FtxvNf3Q9EP/h52fEIPPeeigLqvGCyJorgJb5dwb3ysV87sZP57SfPvdDncJS43'
        b'CJomh7XU6gDNRsKFUDoa6xGvAfWFSZoxfrOtcELhzqe7h2+66YubfNO9IWC6qeKB981T+KY7KVEfn5WoN6aTHTOycGNSelYG3DdngE6Id+GtwWTjGHKk06kPlDA7n/oA'
        b'FcZbYeDUq7IZmVyftSrEIYzHp2FqQfk+oMFb2OQ3LKZCScQUYao5L53XoVm2hZb9CifIGWj+hdO/Ny9ic3y9dnnWC1xJ8G+mfXfgfe1Z7XdLvxt9tmLvwDPRH5u3aFUR'
        b'L+zfOFJA2u0h+siPQceQjDCqslYdgyevjjJq8SmmYuBXh632ahhMvYjC15mGQe6TXfIUPXviY9voFoHTHixNe5CGi4Fpd8T6T3rJcye9p2/S6YuNtMIINunoy4BppzsG'
        b'6/EBvDmjlNzrSK3wn/fV+EIQacAncUOnyqvQxkT4DQ3IHc08m+G+fcNRn4KfK1GyueJXkTkSI/yvUcAdCxIVaKo5c8ygblJmcQWPFOOARiFz6KM5S0ArMM0QnNnw5GXV'
        b'zy5Vf2L+g/lJcXnpZesn+g3m85YnpUkjPjPPf+3ezgGw9LknpemWl8yfiPx77+jWodxCtTM4f+SpcdOHTR+QP25n/3deO8ChI7rIQf9d68WQ3X3x3pwifCkzywCAMzh8'
        b'Yz2+4KK2CN6xgDQZyPaknCzSnJ2GLytQjzyQ3Q4qxoTiG13VQsOqrKtcJtFtNYkWl4QeURJ6hPNcMHAGaujggR84evnQROFR0MKeoAqrRYT3Vj/HvEFtM44+PrShFe3w'
        b'Q5u/BqiilB8ma/EB0kR3wdZYcGOOPgs357DNvyHkhrJoGL5ZIsizqvRHkjESkijY9pSyXlWqkhFFYLZkBSCKwBBFwRBFWKfoiETQKlXtEEUpIYpZNxLS1eUhyOwwGBMl'
        b'nJhvp2JURCHQB8P1SeHIlvPBLt5ZDE8ej5/bd9v1sA3JoYoPVuQlp/zkLe2tlkila076K+kldzSHiuccWbJ+wrnNPVTfOakbv6bvH8pHfWku6dbjo02zo/ed//n9eUN+'
        b'0Dzs+Bd7Pp/9l+iFQ9Vfbyn7+nFPZcbBFRW/U0/O79n7yDIQYSieuONAFKYGMjXi8UluJXmlEO9cypjHaETuy1unCg4fx1vwsd4jmcktwx6eQRdjE2nO4UAh2saHh+G6'
        b'UbiWGUCK8aFh8KghCaiTIotbBMvzcSa+LhOuXstJUxa+THcr6jgLOTG7DznZmZSieuajthgZWmZtg5CxEkL2BFQEMUULCBnMhfI8r+FjeEdfH1oqKVoCLlJM86hK3C57'
        b'qT8p63AlALpSCdDRLxBFaaUH/FD00xh/FKVvkPPJ4Rn4uCrHGICg/fFJBTk0enLH3GsUkgUXunOKSpXfhoOFwW/3dujZX0LPmVFvoxZu6iB1hDnN3s0poWevSGqjeM2h'
        b'qDbX/N0ib3q+uI7q/p+Ha8zmCt3yJVKmJolKOa/pFBHmioejIqXMpJ5RaDD6Z7gKmRf1UcqGvd8N7UNV2YmKXHMfU3aIlPm3gZRPls/nppods5BsdTk/lloz5uuRzhw6'
        b'Ia2fvGKq4kAF29BXaTYPXDGoRoZuewHVoFV8aLLZsbpsnZT5q4pJaBXSCcpcc5SxJFzKHBY5EbnQzkroZtSgXn2kzEkJ1MSROyLYbK7J6z5Nhj7HAHrTE31QrnnauxPW'
        b'SplBORFIh3aGBVWbM/85RpAtOb2nwkTHUaPkiL2RWVJmzzgFrOzPhwVNNYe+Oz5GyrweRk1G17qHg4TY3d5Tbmc/aiHZMFWIMC9SjhonZf5l1VhQpa51C9KZRywIlfu+'
        b'JCsXHUfzg7lqc7AyXbZ+jppoRU9Q8sKwqebSnRHyHvSQ/mXoHdTQP0xnVqWGyAPyfk9qS0merdSZF12fOFPK/KMhnBptxOBkc2hFZbmUybteRH9Dq2zaCHPMp8qVUqY7'
        b'lhIw3UgFgiYtlSduJzcQzUCfaCGT/y0fi2yFpwsUTlCC0K5/nCvcNTmPJEdsnrf3X4MWvr48+c6guHGau6m7Qv6QGfyD5NqErYUfzXKNn+YQsvHwceqED1cdX7A2x77y'
        b'79/9onHezX/mLlk9vPRHv9o878VxG+bFGca9phiSEhL34lTrxmW93N9tWRj7WpDhP//4vK995i827j6fdmfqpiMv3R64eY/y5aE/iXftfqP5oy/7Ldq68vSa4y3jycH8'
        b'Cx/M038Y5u6x4nfz82d9Wf0j5aVNX23+6Wjbz7cvffrFgFeDl25Y8OAv//1G77QJ55+Ejbl5+r0MQ+nrQf/15HvvjD/1OGTd6Rffmbd034H6H/a4sPCCqUzd8vaM2q+s'
        b'+OWqrW/9Wntvcflff3f7zT0/nfzHRbddk5av+Ot/Mj/m5/3nvVOTmj5tesd4e2TZn79YrbiYuOmdwoapb3XHPf/zacgx9Q/P9R/Ybemx+6F6gfHlzGCyT2bMZN8SP96s'
        b'GOPEx5gyGYr3J2bgh5WGuFQQf4D0gq65OotcY7R1fjE5nQBvx3NIQU6QnW6ONKaW6MOeQ0Cff+mEPPubpSn5LbZULTOV2ytslKAyGlwg0eDxGgGoMPwOZqJBBKdjOx8R'
        b'TEyI4kMVdEeEZ/si8CO0+cvutEIolI/igoF+aziHzke/QfpcbbU4/Eh2J/yEcwzwUWtaxct+1PrH0f7UOoHyq1tk49QMRqvTQbcGLYq5OOwAZR8mp8ZgUKHJ5LqK3Btr'
        b'CVAVlPJfZylcrNSRDBXxYgizcfOggfCiUBdUJFgVokJU1qFarkgJ9yr5XgX3avleDfca+V5jVVAuUMqLQWJwnQZygupB3C0KZopqqEedIooOq9OZXaKS4WvkX0b0J1Au'
        b'Ivnd+PxwSjUyL1E1aICXqIGXqBgvUTNeolqnfpavTHtFWJnNDFLD8dHofPg7IJ1sRANUcZKnxc/2faR0uuFu49wP+m69HomTIxRf5+wVz9W9MSM6Rfl2yvfjXmtU5e3Q'
        b'1cyMWNQz79zDtC8+XvGFPmv/Z2+d/kpbaKk50rgmwbNn+ePoiK9u/2rjiawd379V8uTx99zubvt3/ONoXGj/vz0xj/jha29dG4IP9Dwycrdz+M+tX/4HPXmnf35LsD6Y'
        b'iSYpk2Iy5LWDzw2Slg9+lMRMLePwDnwzwINDAfN9fRlpYkuPbJ5Mjnq3KFUrItgO5VbyQFK6LpKH5CzzvmJ1N+JDIBa9wsPNbhMTpshhZXlCopFpbFPj8Gk+uQqfY8ue'
        b'nBw9BdTzHWRHhhGasEO9jtxHITE8qSfN+BEzE0Xis7gWN+XA4ibN06MS9PiiAoUHCa5KuXGrBqezxwZ8QQEa4WlyWsP3JNdT2NvTtBNwUxLIY3h7VmKaZCiJImcEsjF6'
        b'NSugLcJ7oUSiPj3LyJEt5BQKIU08uYsvkI3txXJNl2lHK21Qm0xV1pUmU+t+6HoQq9k+KNUltewuilPJP2vCZUROlN+T1rnGI5RUONnOFOibNtdqj6baTvfMRatH5XQ5'
        b'rFaXJ9Rd1Wq16Ey7UDnohpFjMPLudVHjkoM6UzrifASCuuf9y49AbOnlRyDatdInu3HyL10FTrr8atBSyTGSy9ZzHo1J3oaDe4XTWuHnICANl2ZShaWyWLRMCYNa/kpr'
        b'XBPhheV99FxgdRIwpYmOFJC9eB8MHyAHJXFaeNkBOI26WmOQyTvqndQa/k1rVZukGeykzoh2dQYIydQRjpp4gDx2TTwubWvg4VFbkiZk20YOvSc4qdYz7y+Rvzd/Yn4H'
        b'tPTQ4+dKf5WpRt3+zJNuq/QcW4Q5pCXcbxVq+Hl4X88o8kj2/OhYi7Y5/axsrc5X6+EnZk1376QHlPIacdgwtWI4H8Dk4n0jRy1fUZxXPd8AP59r/bG4YyBAzOk/fQhg'
        b'q4n6fZlMnmCTSfJShvtQk2m521IhPWHrBBajw15tdbhWS+tpSOCiSmbdpX5iFqezxFpR4V3V7S1FgGFSMSjCujAQLv9AspFQo0RcVEQox3545rKDN/Qk25yZafqJZG+6'
        b'MVGFgpcC+QzBDwJmN0T+69zG+fFkrkhoEVrCWyLgN6wl3MaX8nAn/4h8s0o0UJ7t56caATyTcu0g4L8KqxK4troOAY8OauaBcyvFYJYOYWk1pENZOoylNZDWsnQ4SwdB'
        b'OoKlI1k6GNJRLN2NpUMgHc3S3Vk6FNIxLN2DpcOgZcGA8LFizzpNkZb2RKTyQa9mjrU5FGSN3mIfJiuEw7t96bvWcLEfvC0URbCeh4v9m3nRKJs+BFEnDmB9i4TyAxms'
        b'QQxWFKQHs/QQlu4mvd2ibtGUCi0KcWizICYyyUJyNaejpa0PLw0S40Q9qzEaaohnNSSwGrqLAiMASSC5lDCa+HRYsM7vn5wr+b8HPNGrPAobSJseBUXBjjAuu0QtTzhd'
        b'I1rv0p5FqYQkAgXRwZMn1euUrC3VytRDzQQiDVAPNaMeGkY91Os0QD0ERj0UH34JGBzQLPovrcrmslkqbGuow365VWeRO2EDzmSpKqEe/21fmVBtcVgqdbRDE3QzbfCW'
        b'g72aNi0lW2d36Cy6EUaXu7rCCpWwB6V2R6XOXtquIvrPKr0fR1826KalTdfTKuJSpk/PKcwuMGUXZk2bmQcPUrIzTNNzZszUJ3ZYTQGAqbC4XFDVSltFha7YqiuxV62A'
        b'BW4V6UEE2owSuwNIR7W9SrRVlXVYC+uBxe2yV1pcthJLRcXqRF1KlZRtc+qYuRnqg/7oVsCYicCr2jdHHh460xNYu+id91iFd3hB6xCtjme+LLNc6X05AWOUn2McOXzM'
        b'GF1KZm5qim6Evk2tHfZJgqSLs1fTExqWig4G0AsUuiNDhLuOW9yVerwMV6rLm/r29UmsVqpNuv8WdQVYyNsbPkOz2X7dAtIA8mgTaTYk0tMPGfNIQwbdpVybJRm98EN8'
        b'Ae9l1oRu+dtRHw5FLBphrgrOdyM33SiJiqXOfVn4ci5p0OuoeJ1EGuE+J59VlFWYiq+kZmdlpWVxCG8lJ4PIHXKebGYVPgL1LBSh6jqD2TA0YThi7koOsh/fgwZtS6Dt'
        b'aMyck8rEaiZUk5f0+ALKT1GTg+lk3xRyn1WzdwFPtR3dy2pz5htDZF+dj+3UwoOqP84xG46kzETuJMqIdiWC5t1aN95Dbs0hDfTEBjQ3KS+VbM1UodnkjIpcxw0r2Gbg'
        b'zCm42blcSf13Ed6P7+KtvfFB27mBnwrOH8LjXzRWD9kxsWra8IiZb37xcMeXdbp3d3YXe/5h45i8Xk0DU6O3vDdqufMDbd6UsZdrz3zkGVX2W+eb83qN+2fF0PD1v/jF'
        b'4P0V68K2fLZp8rJ/nXZ+7/1Vx+/+bc2KP0/9oLD/bxM/OTG/ZNL7FSWbtqxLuqmPsn9S+vY/ru3bZ1zx3tuaf//6ty8cWbwr7f6ZH77xt6dv/vL6F0Mbdwwe/fjtj2oP'
        b'Lf78O28Me3DskaPf8e/8WGt4/ObgwXZdj2u/HVFwc+misY9GV+ne6btq2P3yRdbdy97+r6QXf/ZT1fitL/xb+N3u9KG9L+qjJI3pLrnYKwRGSZ/lNuab4snWJB51x/UK'
        b'DT4wiOlFdrwNnyFNbGMdFLOtfpvraeQ+c+6EmWxMzUhMzzKk4Waygx2MoXpdL3xLUUU295MUt5N4TyXbLCMvk8Ne7/pHNtcgNmHJ63zbi2QH3khelo7XdCd1ArmHz5Fz'
        b'TEV6oR9pkXfV8N1CP789BzntojNP6vDlbJh5qCSB0HM38o5lhjGeoj3dlZ+Nr6uhIyfwjqFFktvp5bH4rmRcwOdTGGqEzOGh+JZkybn/wPI43CT1Cy0SkJIc5MgDskHS'
        b'Zcn9pSupuElfE8gmKznE4e38WtZnBX51Kn2TLpAJeIMSXn3AcyOSWF+iagD5ZGVSwvq6YKZN4q2ii+pDKUkzqMLYrGcHqubppNHNYIerEvBNJdm8IoSpzNDfl6DjtK5M'
        b'DhpxezI5xuGdYXiTdCbiMT4dDE8Ts6CF+Da+Q+5w1EEdn2Tdm5wfTNuYRT0bDGlKcnEd0pYJE9KqWfcqF4+HV0GmowJdvwiknS7MIjdGsoGbsDaIvmmA8aUOrGTDIqTF'
        b'54UZZMc67/aV9v/a6tVWVAc52AacXVZiZ3ml9OEa5nEZyku+DwpOy4dyMTw1a4XKrr4R8Ktq88NTARx+QnlQ7SSam+gFkC0JxkGSEE9Ppzio6aZDsbpV/u+yXq5XS5V0'
        b'C6yd1Rnvq5gJ3tT7vH+A7vCbof66Q7umP1fbK/VqpVTW6UTXm+/V9VpheDXfp0MKfKIRZVogRni5VpzDahGN9qqK1fpEgCKI9pKu6p8KU7GtpJMGLfQ26OlgCh7Eqk6h'
        b'PxdsuXcgqCzTCdwlPrgJnUs+3wy8ZIpw6FGrttgBcIsPeKK/2PRt4QfL8Jdy3gHgYVlZJP2TIWUnbREDB6IzgeqbNYQhAO+Y6V0EnbShzNeGpK4IYt+sHaV+7RjWeTuW'
        b'+tphfL4I903QQlqerA2dgK/0gU8uYFoJQPa3u+nkKdVVsLPMHbbg25tuBIa+iqcn20mk06k24dTZ2qxLp9Vayc5OgwrDlIx2L9Lz1LJmlQ+aDPRoptth1+VaVldaq1xO'
        b'XQr0oL0AHAfdhM7CiyvGJI5ITNY/W0Sm/5SovcG8QM8xIZCfEp7AzmIopnIgIZzGF/EOo232H7DAPFjeHXfp9+Z3ilMtT94//HFc3ifmJ8V/gDRf/HH0d6PPLvlY+91V'
        b'Kt2OAfs3juyL3jgbNMr9ql7BeD25MyrOn1UyPknqyNkZiWYXNasMIZvxq/4S0DHBXwAip8ZKQtTuqhjfyWPyiCMNZCM+tDxesm0DYydns8jBDCaM8Eu4pJ4rO7N6qamp'
        b'yXs8RnYqWo9WBHMx1Kgqk3u5TPY3NHdlwKU6gGW9pA002gbWDy9T9teJ9xA1DaB6rkveQ17crG+HCvlWl2QOcFe4bKAMy6Tc7ZS1XxYwwOWwVDktfgf/i1e3q4jWMYEZ'
        b'RCaYs6AMVAV/LGVWh7kTHY3+a2/elJ1Tvpe5gypescnDjvAtcwzIPQ6xc3AGr+LVBbULn8e3yZ0kcsvGf2VQOmkNK5vW/d6cbnnysSHvU/Mn5qWlfxA/Myve1W973zAz'
        b'fkiofuqKbrmna8cfHb4ZMNcQchOky+CQ2/NO6nmGu+tBftwXkhE9UFIS/FSEypUuyiyU5OZ6EFRzV3hF1faCqnmN7Hn0vM1Lp9Vl8s4MY8kMNyO8uLkecV6Jbk1PLwa1'
        b'eyfbC4yh44RAhO3Av4mVaEXdLLisCUDdBn8Pp04Ad1Xs0ga+1gmJ3xLIYbqKtIne40OULnTsbMV8WZgfC7UV+nxZOnO1klfVh6BktDe3+RaW3WErs1VZXNAum/gsZlhl'
        b'XSkT7OGJwzswajzbkiNK5hLWZa9/JABK1OVZl7ttDnlERLgrcelEa7HN5ezQekSXNbTAaa/0ClQ24JGWCqedVSBVLQ1qqdXhfLZtyV0itWj6tDTgvrblblofCCNxlNPq'
        b'HN5WAaw0l4Xy3s6pQ3sfR022ewqiPlsIn8rIptvfLMBAtnFOqs8bM480ZM5JFfL0+EKajlzAR5YUOxzrbEuC0LSy8MpsfFry4t2M9/YLsLm0VoDwDbKnBh8uBD61h1tO'
        b'bmvmLcH7GVe04geFo8kJcjOUo45TCB8lR3u4U+CJeQ2+5dS656bS7cxC0mCYy3blm/CFFeMLUg0Uyra0TLKVA9p0Wr8K7x1MzhbwiOzBd0Nz8S2y101xO11D9vq3qlqq'
        b'ER9cB5XmzjPOVaPc9XQ79TzebBt3slzhrKIrYtNvje+8Qn3zZs5Zj+3cLEtE7IbvKnm90sK/N+nOhqzrfLP1y096Fd9yf7Xh2nu/7F9x+EvxiTF8Mb/pXvneUX1eV7yX'
        b'v9xY6Lr0J8/fPhz1oP4H6Zc+Nzq3rjs75urx9b/74GPVZzdHHzy/cMnCJ7p9g0ANZCovOUiu1AA5lpVlFKIlLVU8OUQeCUxnx/fiSWNIPD1MQCmhl1ziA+R8f3xTQa6S'
        b'0yul8wj3yUbSmGDEu8mV1hMJY1+QNPatpHFsRqtlAIXmxEcI3WeT09JW9cZCstNrtIl3wYT5SHIPfJ3VsB4/BD1flhTIGXxKYEFKyHUjo+n55MYwn3cyeUge+AwpqYuY'
        b'E0thmNZrTwiPEZg5IRkfZBYB1eAc2ZiAm4IEyZZwEh+Xffi65KJCCWcrmfCenBzYSuW7aUAnlyh9qEzvpZSqDfkNqCXb2wZGTX30rzPiL/gVa+UAc+DSSDlAtJcDbEBf'
        b'Rj+TBwQ0oqs8QGECWtYJ5T/ho/zDmZ7VSuo6UzC+mdaroEdLOmnDaV8bJnZI4aYXTm9rqe+gNdQxqNJhLfWonLayKqvoCQLa7HY4QKSfVaKQW0oN16Fe0jdN4k2twZJQ'
        b'fYjsKxNaGipzKkWDEjiVEjiVgnEqJeNUinVKmVOVA6c60CmnkoJDSbIbI/r+6sqzt4doXySS733X557/bEs/67n0FnsFRo3mWaiilqibbqmiWpFFfla8FJhXh1yLbkIB'
        b'I8nPGTcmeTjbfqJbQyJVPUFheiZ434BP0M2qsJTpVpZb5c0t6DDtc2sJb6eeBb7K7uoAjMMKHalyTtCltBWKzXJ3nsP22mtlwdluigfB5Dw5Fsj2SAOjv+TxOENaYSrk'
        b'5sl8jBsRhXcDRb2ZQW6mg051WksOxga7J1KSeq5yXUaiMT4dSKq3Avq2r+LU9MK49Jo5NLxBZjZI0+RM31AAfZFslVxBk1P5d3gdh8zmYO3EUuSmzupLyLWVbWRzcgw/'
        b'kuVzY3pWvr943pQfRB6HkkYWTEID6mUtaWJlmLU6jfLKBMo//XdEUg3pmeQC2ZeYZoxXIdKkD11eXsyOZtipUdzLNVEMK097RGHHAeEGAdygN6Yr0RpyLgg34xO4US9I'
        b'4atewTtjGGgBKaYAozjA4UvT4t2M85wjp8ijBPY+bliYkUX9yg/wL5a4WCCuuDz8akJ6ljyOHOo2DL/qEoD9bSWXbLdWzuOd9DzJX0991Pf7r4SR5FBFbp6piRuxuf5J'
        b'xKfv/ax569QqHnebod/fNy/10JY853eEP1W/FPz539/Y1v2DuAuxS2bHvH3p5bKLBz4bUvDOF9U1Exev+NGmn56o/+iVg8c+rvttXpg9anP8OtvWOauDRn+Qslmx8JPj'
        b'C/v/cfP7wuJTMROfvPSbH8z99/Wk33xHeO+v4XsOJ8zaPQ2YNjt+tQjvymC8jC+eii9yw8kZcp+p3XjTgMz23Bo49Yu4Dph1Pm5g7BI/nkORREIaEKI2UM5P2X4+vsrY'
        b'7UT8Su+MtKx4cgU3gjDF04hlPN6YTurY+/3n44eMX6+KDNSg0vFN1sJ5enzS6+NPGqs5fKyE7GGMOLxbDt3IYC6oqgoev0KuDYyrYsceyQ3ciDcwV9UcKbSGAWYkqaxC'
        b'IHuG451sf0dDDs7zWfdJI66lMKh5n1zHuyV2Gfr/yDAfQlmhTDwYPze08vNRKnYeUePj5sHybyg7ncJLFvhu/kxVrknm6SqJR82ll3n0Mj+QsQd9M09ahVTTfB/bn+fj'
        b'e0VwOdeG9/9soD/v76iZXeW4Gu8LnXDdJz6uO4CyCyCmjHn4uE2AdV3B3IN4+OVm6WMcw2klVNR3UBpBHf5Ee4nJxHYQHFTlYzsNHqHYVvLMzQyP2msKpkYcpg57wgIU'
        b'ViYg+UlORewtuX3ShEX+P9r4eRa6OeimdE86T0somisUfDQgFOL6jeaZ6NjlK68N7hfCU/GSD+aiY/yfRHG6/vSOhQ+ElfYYX3dmZpPtOnItiZG/4DU82b6kXwAjC5b/'
        b'Ov/Txr1J5IsUolCktKEilagoUsOvRlQWBYmqomBRXRTSomzRtES0cKVCS4SoaebFHBB5QuojSgXmZkwdd0KtYWKIGMrcmLTNfJEW0uEsHcHS4ZCOZOkolo5o0VojpYgx'
        b'IEpR/5rw+shSjdhNjKauSFBjVIsW4EaI3ZuZSzQrF1lKnZt6yCW6QZ3UrYk6PkdDGerm1EvsXacp6g5t48Q+Yl+4jxH7if3rUFEP5raEimLFgeIg+NtTfmOwOARK9RKH'
        b'isMgtzdzRUJFfcR4MQH+9q1XQU0G0Qhl+tUjuE8Uk+C+v5gsDofnOpY3QhwJeQPEUeJoyBso1zxGHAu5g8Rx4njIHSznThAnQu4QOTVJnAypoXJqivgCpIbJqaliCqTi'
        b'GIRp4nS417P7GeJMuI9n97PE2XCfUB8E96liGtwb6jVwny5mwL1RzJWNKIKYJWbXBRUligq2oTHHo0qpZP5UFwOkH7qspQeSS5UUSBQEOxoHrsxhoRKdJI6VrPZ5+7Tx'
        b'qQl00HJABZVWl61ER33/LJLlskSSKiGDCopQp2QVqVits1dJol9Hopme96hMKywVbqsnyORthUeYWZiX/XRSuctVPSEpaeXKlYnWkuJEq9thr7bAnySny+JyJtF06SoQ'
        b'h1vvjKLFVrE6cVVlhV7lEaZn5nqE1MJZHiFtRp5HSM9d4BEy8uZ5hMLZ82cBZKUEWOOF67NdBexT1FC6yjuDKW1dyzdwNXwtJ3LLBGe/Gv44dwI54128yNfwMYiGhW3g'
        b'awCR13KiUMMtUzmKajjqNwhvcccFGkxWVPWEcrEoGo1Fa7kqDTxX07sGRN+rQSYF1Ko8AZTcpBI1zAYW9KGpI82ircuZPMetHmdtX3iWvM5GQdIWLFIdLKcTI5Q0XBOY'
        b'U1d+jnHUiOFj/VFIBCUjrZQK7zpntbXEVmqzioYORXybiyoEwNq8zmUMslfLk9AVdA6Hrdj9DCVhAn08wSxaSy3ANXwoZAatw1ZSTmu3SeMEiCjDAeRq37dP6Zw/7W6r'
        b'YptFrb0ZNsQ5zMMlerjkTyk7+PRr+PdUSExOztarPRFtwdJdDktFdbnFEzyX9mSmw2F3eJTO6gqbyyFSxqV0V8MScVhR6/4GtS857KjTQ9qMp/7SJykEK4BTRMumCh1P'
        b'xZs14RICdH1bXpISWLM6ERD+7tuU9wLw7ckb26IMm7jV1VadGSakBFh4ReIM6a/ZnAgwXkBd9g2XRujZzfqnT27pzTwDOkbDAGC8F1iEDIyu3qV8iG9rXGBT4dFYnCbm'
        b'eOnRWFdV26tAT+2kIV/5GlLC9urdlcWg68JAyCOgq66wlNANUYtLV2G1OF26EfpEXaHTylC82G2rcBltVTBiDhhH0WymGGoRl7qhIC0QWEvgVmrgIR+OhTrwxX32HfLh'
        b'mJH92duq1HTxp44ITGE1lbAk4mJdVVJuqSqz6hwsq9hCdwPs0u4plLLoqh32FTa6M1q8mma2q4zurVZbgUdMh+F0QIemWaqWMbu402UH+Y+RgqouLXt5yXubZGJNMtMx'
        b'dbNlLhEVSn189nAYU+qH2sG+Go3CbXWV21v5lUHntAH9lKuhr9HNbX9v1mf1Ua5oAo3jPcEss9IONug6tWgU2+00qqqu1N904mZTIbaZhg4J4kqrAxblCuCDlmK6S/8M'
        b'I4pPjKRIpEBt7SHabBZjOB7vIBcSjKDrU501Yx61MJDtqXCbUxiXbkgz9ohQocooDXlMo0C76RoRUvFBUAKvkdtz4tKNNPztjoRsfJuczDOSszw5ineiUbOVZfjV9Szo'
        b'dBTevMI5ZG1iVjrZs1IVhcLxPiGRnO7BbPX4Ojk71N9YH5dtjM8w5nkrLu2boQRxVINfmbWeWRTIKxVks1OKibNlVJYSKfEOjlwbj6XI3S7yoG8+biYthaSZ7Cmcjuuo'
        b'ySGHI7fI2cpZrD3R5Aze6UzMwrfWpCuRgPdzIIvfJvukWIo3yQN80JkqmSQy5pDT+GUFioQm48v4ItnKNjC4oCAnjI0CHwXtV7mWI1fG4RMFtsbUSwILjHT/vYfdmyfm'
        b'bUqJqHvxi7fC42fN/XePX0XvjzzQK3bB4PyZe2Yc516v4N/qVzL0z5OObrg57pD777/5/dHumbPqlrSs+WfwrF5hYZOX/Vp37Vc9g6p+rPvhO++e3/XDf/zpXPWDd/es'
        b'+XH8G6tVPUIefO7+pHDY9PCvzoycZ3RUfrphb5J92tPXQk71nXK3lvxo29wJi4y/+3PekM9ORQ+68Oaq/3xUmPHroy3Gwb//Uapm2JcbFGVXX/3r2B+vm3xwX1bOo/Vj'
        b'hn1JMhLyBvf//ZdTNFdjj/zoF3c/7fujD/vnLkz5Q+bxoxP0kcxUb8aXaXSAbRkvZJAmNVIYOXwFb42XPD8fpOAHCXgjvmEkW0ljUippFlDoLEEFuLKBbVFw+PES3JRk'
        b'hLE+SLZySJHE4Ztu3OhiUW4fuQYmpGcNK86EBwM4fARvWMPeSsWHyQ1mC3lAWrLUSKXgNeQ6vEWtGfMWlmTQBuFTcRnwXg8On8S3KiUX0Bt9J8umGHw5J9AaoyBX8Uv4'
        b'shS78YyaXExI1MdLKHWGXAGcCic3hNVk/wjJI7MJb1JkpBlU5IAcNOEY2YtvSNsuhwBhdjNzD7k1G95UZHP4Ws9Q1gRyrxifoNaSNEMi2Y/rcGMSXWdQiU6nIHegYY/Z'
        b'hvdS8liV0brscHMSrDtylVwzqlA8eagkm4aSe1JjN4r4YYaAH7BZoCa+Rg6FiDw5tJC85KIK9HL8kFzMyDFyaO5sfgWX0qNaiqZaD41+VTokOT/Pe8S4gpxjZqviWLw9'
        b'IysjIyuRNBoyWOwCVRY0Mx5vV+KreCc+yaxKLw6KIE3Z+Aq5rDeokGIGh1+dm/ENHBS/zRHD7hJdNAWyAmYPopuYsj1oPdIGs6CrVEyifpvRzDeTHkWMYFYhrRw/U8qN'
        b'4qT9oDV9ZHmnQyA+FxW6EfetPDI56VUmSNTC5es2dqDagHOHnTYG6qLyY8f+LCzQCQuABaIB5xfohGefdHi2T0sdCAY/6UgwmC5xNvmkiyT/UakFGA1lVj4RTJYPqLDg'
        b'lGX69nxI3ghoI2C0ESc6Fh/ac7WC9qKKhbLDAO7tZaZ2yuXpLshqKoe0b5mlpFzaSq+0Vtodq9mmTanbITFkJ/uMx/M5e1uVKVBY9fMjdFkcZaCfeEt2uu1R5dv3kLDC'
        b'u+3hlaCo3GN1+iv2nQgAHZ/r1kheQqfH0gBnKC5ZZR7aK0iOVDFyFQtuGpdc9S/j62NekDKnd7+DVnGoSoOmLp+/4o8Gxgt7xONLzrAwHnFk+2IrohZrvMediqg1bUxG'
        b'G2GC7q4k4v10g0Xir/jlArohPw9YPd0zad3hB+qzpl/EBHyAPLIpzpkVzvNQYyHfmNU8UYuTI2aU/Y92QM2E6Mjll/9WMHdnddmcCWG2H5bs3dItd5X9dW5c7B3bJ7/c'
        b'9svyum7R4TExLw75wYkeEweO/EHE7m3FZxuqv9/c3NJr8+z9I65Eb19XU9n3xd5Dbe8VvX1nIj7g+emtObmf3nGurf7Joc/joz/82ecP/7goP2/H5j9Fj4/Zpzq8c+3L'
        b'X8y+9+B/P/vLsbcE7ftNh7/4KCV1/NWIvzo+jPzFRyGrNo97GH1Rr2X0sufs9ARj3FT82LcfT7YtkzbkL1SAzHEhLMM3DAoUPleoSNW4qNmU7AQR5eV2LAHYgYHckjiC'
        b'ArcwGHgr3iW0RvrJmcsVzjOxUxQJS0La0HQYU3J9gUTUc7tJDoDn8VZyS9oqwFvDGXPD9/A11soXYPQfJ7BwUgNnsR2DEHyDJ5cWlDLmO0jEj7wBgcjlcEUWMHjldFbt'
        b'gFkjE+TPtuAt+CxjiuQkqWXchlwH/n1e5ov+PBHRTZI75PE8F5UyyeMCfDBhsZY9hvYHjAZPbuCtnClJg08PWigNxMMXulEZciy+ogewqqV8P4OG+ViEkitT2W5Jsipw'
        b't6TfQElyuTCmhDzGOxMMWSCGUnEBxMJwvFtwFOLLHZ0w7yrvUsv6AeNWI/y51RiJT6mkkwVcjMyRaEgMLdvXkDwVtNwarcwU5KoCXdHsgYypk/AYvFS21SVhM1zioC5n'
        b'TCs72oA8/nGN2sIO0LQpSWGaNtUhqKYNv9Qa1kvkXDzcC7VcDBQQ+YCU9zNCT/khtqeKIYkjSqErtGWeUFOV3SRrwk6PYCl2Mk29Y63cE2HybVVLpsV03nvEmodh49f0'
        b'8FpK2pQLsP/59ogz4dLAIvzX8o5ZNRzrDVomOKbSXjnia7jjtBfoBLeWq4pxCSJXw9K0ZKkgWQXhXkG/EsB6yGc/HebjkZU2JzShpJxxlyFA3KnBienF9AZmjQ1AN1tl'
        b'dYWtxOYyScPttNmr2Cx5ggpWV0tmJmlIJJuSR8lYsUcjGWjtjmc45WpN1Q4rsCiriZWfw3v9H2nQLMA5La9gIRrWdPcOWUD5dpPOBowijUgNmjAI1KS5lCvlYyTLDnQ9'
        b'SqopjnbPIHUSGtdqA5PmtN23EuhRHADtMJkW8fKXEpC/zUt61jEWRrEGefFQbkw5bYyaYhkMewctaItVahM9KW9iR4G84LU+8OyRT/6ifxVe6LFsDRwHfBC5E/xaNiA1'
        b'3DLfgHCTADr9UJI0gbwEfXsHTVCZTBUuk6mYlxk1gjlaE+ZrA332jZrgQ0d+0uRv0garyVT6rDZY27TBhxWJ/stooHeBLOPtOqk1QCD4fIlYsDv5rIjfvPi16hnoDI2z'
        b'LjeZlvKyRVFC44AG0ucBDfRZBUPZIFHgoV7rqNefvbPRqIIeV/vhRCuoqrZj8bz5YB8OYSgx5RtMRxlMu/MZ01H2TVFC6UOJKd8EJUARMa18VhusbdalzyWdjriXTLQe'
        b'T/Kj7B1SAWogM5le7JAKSM98PQ4QbQd32OMedE8HMYrN1/Le3nMJQEh9nfca51tHoKrDxgGJsIiiybTOx29gJIL9yQR73G59+KEfbd4JrtU4f+I5Y0+pIqu0tmOqGAiw'
        b'C+MR23Y8JBpl/Jbj4XQXm0xbnjke7HHH46FlzQv5ViPCqm3qeEQCQQrIj0RR6dpHorQuxMgRpKPbjwndLfBos+2uNGDMVnpgyCp2NjbPOBNjMlW6AWG3+xMsReAQsQJd'
        b'Qhl54+RcFwaIVdrS8QAFAgxAmUn+A6Rrjzy9fUPWu82Qia3sLqkLqNTxcIWYTC6H2yraVphM+3jvMSJG44N5GLQoXyd8xb5dP3r5+tGro34w0YFP+vYdCQUGWmG3O1gT'
        b'j3XQk26+nrSW+3ZdifF1JaajrkjUbsi37omahQcymc510Ak/HLb7UyGFf/tzUaBY0Np+F+0B3U2HtrbeL+LX8msFuR9CLe2RIN2VevtEWahHBWMGYEGDYB27Gtg7RWvv'
        b'PMqV5fYKK/UTrrTYqkTrs2TlYJNJqtNkusp746FLAgZPT3uvifT111uuY/mYiqMS2wthU8NISmlbaedZHJCFVSszme51KIeyR88DG9wKtp2Q1QnYarvTZHqlQ7DsUcdg'
        b'oxlYlwSS85HQcmnDtTFwXjqBDkqfyfSoQ+jsUZdEjLouiBhquoEOctPrHcJij7oEq7wLsILYArdAlW/4QYvwX/30oYPGUOx4/dD1T1fMMuSIcIFGzXxQOFEQFZRv9YCm'
        b'rKUrheqofAN/Qlo78ophaKfM/pRW+nQg23+2VZXpqu0rpR3s4cmSD4e7utpOIwA95ZMTPdxwWD1rvNPm0Sx3W6pctjVW/4XlUUNNZTYX6OrWVdVexfSZphAYBQbcZHqz'
        b'lYxoWMRQrf9oyIWkcaVDok9q44PoWCzX56ywu2gosVU0rQ20lkO6tNRa4rKtkMJGAzmusDhdJsku7FGY3I4KRwOtbRu9tHoz+vDUo/EZI0KYIVba+WVmfKaWO7bSC6M8'
        b'L9FLC73QD/I59tMLjRbtOEgvh+nlKL0coxcq3DhO0stpejlDL5SfO6iB03GRXi7TCw1g6rhBLzfp5Ra93KaXO/Ryl14ee8dYH/X/xzuyjYNKMVze4eTopxq1glPwCs7v'
        b'B2hkdPd2DpECz+ni4HdAqFobEipoBI1Co9CqpL+hQqhSw35pjlbDfoIgV/6RXCWbyav9nWQbaWZukriWnEKaWN6tJ9sCXCUV8l/nT9u4SnrjopYqWIRWDYvvxiK00ihv'
        b'cnw3Fo1VDGJpNYv3pmTx3tRyfLdQlg5j6SAW703J4r2p5fhuESwdydIhLN6bksV7U8vx3aJZujtLh7F4b0oW703NHC+VYixL92RpGtOtF0v3ZukISPdh6b4sTWO49WPp'
        b'/ixNY7jpWHoAS3djMd6ULMYbTUezGG9KFuONprtDeihLD2PpGEjHsbSepXuwiG5KFtGNpmMhbWBpI0v3hHQiSyexdC9IJ7P0cJbuDekRLD2SpftAehRLj2bpvpAew9Jj'
        b'WVpy0qQul9RJkzpboiIdc7NERQOYgyUqGihOZdQsxRNOD9oUtB5P/fBa2y0s74lOv0JysLk2xaj7B/NFKbFUUUJYbJW961w2toHk9Rhh0c28fnfUaUTaqbEG7inJO1mB'
        b'TiJUP/M7S2umZNcinRUS7SVuqlj4ag6oze7wVmhzSSY+6VXvxtD0lKyCGXIN5mc4BQYk0kpljxeLrpgZJKE6aT/P/6yvQQLp7avs9OlyWOmABNRncTIfU9o45oeyAmqy'
        b'VFTo3FTEqlhNGU3AIeKAl30MlmqNlLzQIwjOUo7yOkcE5Xc9UQO/LMgR6+V5LmaFPcGtFUTgbybpqmBXJbuq2FXNrhp2DWLXYJA86d8Qlgpl1zB21YoCXMPZfQS7RrJr'
        b'FLt2Y9dodu3OrjHs2oNdY9m1J7v2Ytfe7NqHXfuyaz927Q+cWjDpRA6uA1jOwFXlNfzxQSfQDLR4Eci7irXKGsVxWKEnuJ2cEyhNjaIHWquo6sVyVTTXMVRUA08fUqOg'
        b'1s21CtdQ4PGKWh7KT3ENEzU1CskO7Yqj+TXKWoFDy/80DzVAD5dqGzhW0uzSb4JWsHUUlO24R6WC0dICaLdcOl8QjC3M8nAmD28yPVWahjiHOJ8OaVtJuYV6abU6eknG'
        b'4HhPaB6we1ul7DypkrY2pXCjgskmepQmt9XloEFkpKMRnnApBLnvYJxjMmVIU+llGr3QgDdSiJVsJg4EnqEEgU/aw4Yaq90OEGWtAIKJAmq2L+CyeFSmSmcZA72Mni1U'
        b'mqzSH3bSMMz7GvtuFrxUUk73X1l0W4vL7QR5xGGlRntLBY2BVFVqhxazcbWV2kqY+zSIIBLN8D22VLpaO+SJNlXYSywVgSf5aUzhcrpr7IT2sTUL1bC/UqxhTx9TmyEH'
        b'8RXWo1xWCfeVTk8wNNLhclKncCZMedQwL3ROPNoU78xIM6F2Wl3yA6fT6qAVsgd6leTJwL4nqVq2kn4m3C8aQhV6fiwGNrsfUOGviAl/EcxXo238LE27nGf88NLfKGZu'
        b'ojtl1AhMw8iv6dFmRLocxlnWHH6EOvVKjQK1R3KWjW0LyOc1O6mA+URULWs9yWmQoiu47PKJV+rEKALhtpWuBnLsRya77EQr21Ind97c7t7mPh0aGF6LuhBU2l2tB21Z'
        b'YNGuxxKa2jncWB/cwLha7cHSSKZdPWHMFnsnUHsH9tY/qlYbsHJY0a729jkBtfr54Oo7CKj1LUGXdylo0wAf6J+l6KRgsk53sXwMhDnIU3iyI48cv6nTdjHhSaqIbZlS'
        b'WacaXqNyCgt000FEqERdfmteqc1KAcqCA9QOBVrdfHy8wKmLl8cp3gC3Nhf76429Fc82SOOlEFjxXQ58lt35YMX5BmtU+/Anz8DPlGnzUpLgMrPra+PHnbciwdeKSQFH'
        b'8WmcEWtx4KH8tq2ZnjdzRtKMmdMKut6a/+68NYm+1uSxmfdj37Ljl9flv41HUqJuBguHIvlfVay0rHbK59J1VdYyC1W+uzxvP+m8jSN8bYz3IrnXp8qvuTKP1sXlz51X'
        b'1IXxkQn+/3QOe7QP9jBG1u32ZVSylU7Wg8BbXW2nx6xANHJLZ/G7vLJ/2jngcT7A4QW+czNdAyDP/PudA5gYSLUqYZ1ayqx+yFddvtpJPep0uSlp2bCuK7oAWh5UT+eg'
        b'pwQOaivICntZIERdXEbezFld5xA/6xxwig+w5ElYJRpddiP8aWXVuriZXYMo4+7PO4c4wwexb4cxHnRxWd+og7/oHNxsH7gBkqskiINV9HSJvDikSBu5hXm5XV8hv+wc'
        b'ZLoPZBSjZ0w2lo/JdLlbH3YOI6uVArSlUlSepk4+9D5uWk5ORlr27IKZ87tCIWXYv+4cdq4P9v+2hR0o4yfqZgFFmG2F1lQx+c/pU7g7CvMOhGpe2qwCGqzdoJs9d7pB'
        b'l5uXlpWSnVOQYtDRHmTMXKA3MLehWRRVyuU6n1XbjJwsWDVSdbNSstIyF0j3+YXT/JMFeSnZ+SnTC9JyWFmAwIwAK21O6itbXWGhYayk+B9dJTS/6XwA5/oGcKAf+ZbU'
        b'IQkhLWwBWpwwhl1Fyg86h7nAB3NM20mTdLZEXUrrkba07Fk5MPwzsmdTmk6RqMt9/1Xn7Vjka0ePAsbPJTURJk+kWGPv+gr5XeeATK3UXI7Jwk5HSmCsrUYff12jqyTu'
        b't52DLg4kca2kjbqM66idqg3zoK/79jfmyuCc2czbLpbtAzIvruo+9F46OUv3M+BXUQtXEy2vZN55SvqmiV2Pq+CqPsFxfhP0dGKe5FJNLVU++UUSplptZh0LW4l6jeM9'
        b'2kUaEaBtvGZma6ChDBxm1LoZPx51tAUUQj+hJldqFWTHBwQabCzzvKM+n2t6t1Um/d7peJao3Uzk5D33AmkfoOMpovsOdqF186md4urzqunwLGWsPD8OLd27PYHoXm2Z'
        b'tAEmb2nS7SWPghoenuFZp5HNEib60TDZT4QdwOigKVLBjvsc7dcUKbyubwSYMcvbFiUbt2e7+VVYq0ymlW3a0oHhgJXL1g/qaA+KGTTYrpFH28Y4Nd6HNa0IY/Liiics'
        b'0Dalkk1TaplDs8/jelSyWUopWaUUzCiloDYpFmrEExpgkFLJ9igFsy1p21ieQvwNTyrZYqVpNVhJxiJtoEHKEcLJqOOgn6tysC8/MSTrSkw2x5tweZdae+hWlyZUwUeN'
        b'6ELwDGX7cBrfMPxG+6ui83AdocEaQaN000Al5FV8mrwcsiKsOlSfTrYlZGcmkkbSMEmK8x9frsTX8CNc1y68Iv3npNuQrXtOIl+H2HcABVHh+w6gUr5XsW8CSvdqUS1q'
        b'oKymni/lpO//FQVJQTmKgll8Wp4G54DcEFYiXIyA+1AxUoyCEmFiN4b+0Z5ubZA30wZ6tHdDTOG/nGnEP0pOTczBwsTRrWITX0bDEQiij90omATvCfJ9eRduK+2ipYJ+'
        b'n21gW6sjhWby3+Vwev0vYji2l+qtROOtoy2NoluwGwSfj5T8wbg+HcDp+un3rqkiW3wGvQ6hfcMPszkGcp1Cq/dC6yrXH9R5fQ0d1uebbOqw4HXMaKXXNO6mY/CzK6YL'
        b'fqsfw3jWNLSn1M/xlPCD2Y5NMgrT7Ae1LUuUoTKa/ByWWNYVlrjz+T2U2aL/oQGf1ws1NXndmpxRLgAsHwNgblnLBOcouGcuTOye3imWCY5JLqW0nQVp1XE1dezj/A5G'
        b'GP0F1UoaIqC4NebCsDatHBZYXLRbpUPx0nEDFgTGe/iO0XgQaJq9i1L6CvsQejeUXpi/B50fYEjV1aAQe88ZhPiBYEWf4TwlWERxt0+6kaNxhbK/7VgrG14o3zHuBMu4'
        b'4/Pn8Z/J9nhDv3R42G8ue3YErL0g5fOxjGZrRKLZNWgGquVkwEJ2gMDqe4GefqD0cnEoPfBB5ZBd/HLq2V3u9SanH+bz+tTR79N5OFe7NQaX495Wq9AaY0etdtldlgog'
        b'QXRnyDkFbihVt1dWT6FfwXC6K58h4SjZe8eeNyasVLZe21a6aXWHYYjSiiOtggCTCxI4efQdiT7hoJP4JgOg0FpBHnBguirpU38agTqFUKcP9mleckEttmXBwH/JTXJz'
        b'IWk0AKQZ5Io6k9xq4/wRI/91bucCGDFMK/sRDiuLBOr0QV0+6Gf9xGDKZukH/EQtZati5GFtEf0QrxJYbpTYDdiskh2o1dAoV/VR9T1L1WK02B3yVVY1i2glfbxXLcbS'
        b'e7Gn2Iu5hqjF3izdh6WDId2XpfuxdAik+7O0jqVDIT2ApQeydBikB7H0YJbWQnoISw9l6XCpRaWCOEyMg7ZEWNWlyBpRi7ZzRRHwLAparxfj4Ukk9IQTE0QD3Eexe6OY'
        b'CPfdxPFyDC8aR6T1A4ha6GcE62m3+uj67vUx9T3qY0u7s5hZQUXRLeqWGHFEMydOoFBgNAQWOYvGEetOPxYojoFnExmcseI4lh8jjmQLaZInlOKf11nBw+V6uBy90sPP'
        b'nubh02Z6+Jn58LfAw09P9QjTZmd7hBkZGR5h9rRcj5CWD3epeXCZnjrLI2TnwF1uJhTJy4FL/kz6oCjDYWMkaHZarl7r4afN9vAzMhwjKDXj06Du1DwPn5nm4bNzPHxu'
        b'pofPg7/5Mx1jWIHpRVCgEBqT5lvu3sjmzCdB/lqAFJJL4YtrrnhmXHPkpR7++Nk+Drci2z0b7uf1Kaf47iKNOYmkOYvGE22NIsrCdyamsXOJmYa0rDmp5MwkWAbp9Fgn'
        b'/R7pFLIpHN+KIndsrt9sUzrpPtV7m3W/N39mfvJxXFScJdWyqrmitKLYYFn02o9fv7Vz+P6NI8NQeU/VH5e8phek848tUWRbCL5gSGWnI1NykngUSR4I+IoKH2EHQfVj'
        b'SS2h36QCsBzCx8hLGnyIX+XAF1ngyJWQszHgW8coBF/ty751fJo89B5ZfP72MO8lx76DktLPOOopuCbaH4cCPyGsbN2ednxOLx1/UEKQSgz2FfNBvkHpEg2t6TsKKf38'
        b'MCBSf4ctKNHIM0zBBX6PUsOQJlj+KLe0yqTYPa3fo9Q0BAEiBQEiaRgiBTFE0qwL6uhrtgrU0Sf5+mS7R1OkxXuDM2g8wSQpJq3RmEij0LIArnR2C3N7GVbiulR8XkBk'
        b'e3UI2TkCn3JTXZXcw4fDWl9NBVQ0zpWPZKcHDSPNQIN3ZMyLI43zNICqCoTv46shYS+42LHwk1NVKDT5v1RIZ85MXDEEsaCw+Wmk0XssHG8jNxG5Qo7gc+yFt4o1KGLV'
        b'BR6ZzaHfSXUiRvcjSoyBkeS9J6PJZXyoQIraviBfvXodvsc+DjuQ7IF23cjISMvKMJBmPYdCsnlyNmqCm6Jkj0ptQio9S052j8RXZycn4zpzBhqIbwv4kY4cdVOOJ+Cj'
        b'5HhCNj1U3JxV6HcMPS7RGEcakuLTsjiycwqy6zXAfc7iAyx6zIuA6Hv74isZpCktM0mFVD14LWB5A0NE1jKyP5Y8JLc0CXTQjVACP+DHkA2kloXdH7SAZw/w7mUdw5wT'
        b'x75DlxsntQxvThVQP7w5DN8lJ+LcdHVEk3OjnCvIDQXi8AHtWkR2pA9k4fNrZpKN/t9krCaHyB4oWBAHQ9VkMGQVSoH1pRjH3vnmEDkthJIdKnyeBeXFFw2iN1g82Zpp'
        b'VCXgo6jbbIEcUbwoocu+GnK7deCMviD9BX69oDB4vJVH+DZ+PDguZHQROeuOkpDtIUd205Cfa5aHoKzk3u4BNHtPPN4E43x95QpyCzeuJDdcKrKjAIX15vEBcpA8dlOJ'
        b'xLKiyglP5tJPA8SlG2HigRQyWHnyeCXPpU1SIbyb3AtGQJMusvDG5GKvJQl0FGBkmpLIjvy4OCB2DUnZ8pAwBMM7RyK8AV8IQngXbnTT2Cy4jhwmd0PIHXLLSe4ux80r'
        b'HaHLyR3AsJFQ2yEBnr8yhQ1b/OBFpIl+pMSYCEOrTCMXUBTeI+CX8/F5hvYti5VIU/BXBZpqzvxzaQ1i4RMi8JZi+TOR+Do+T8/zP+puG5r5OedcBtzI9GdrYV5aNpka'
        b'cbif/c9RL4279P5bwio+6UnQn377XvDre9H7McN+N23qZz//V92BiTm/7rkaTf7+wI/yVuQYf/GjMbc1qZetkft4S5hp6vGpTcVF6S1Zf4wOjz6790ZQnlpZ9MKIyPJl'
        b'95c/GVYW9ok498+p2x3v/+Od/8Ped4BFdWZh3zsz1KGJiNjHztDtothF6SjFGpWuKNIGxC4qSBNEigIq2ECwAEpRihDPSdvE9LKu6cmmm2qqSTb/V2aGjia7+z//8z8L'
        b'OjPMvffr5ZzznfO+c4+fPLqpdcHy/IPbxj474X7eFJfvzb/9NuNKodPrkSHjZ066U6Y3dMWyBd8+FzlXp6XesCBbPLSmepzrxfInJ5ytlBw2P7rjl1Fb3rRYXpub9tWz'
        b'T08x/uXYr7Inj/3ywqQLz424/OzF0e3ziuFZF9VTd0fqWF2qvTZ1uPnVDX+7Hb73qdLKQyFPNd8KnnuteHXeusYTh8erFl376YWX3/nFe2tihevdSff9Z37d1nTHxTbo'
        b'3rdbn8qoCm1zn/n1wJiwuZssUHfp7Hnt2TtWfhj6QsrheaOPf3ty3Ic6PlaOf4to/aCm7tV17UNbd0za7mm547N19u+G1knfWXH2l1FBEZkfuP+ctU95Ise57S0l56eE'
        b'YrK4nerYDh0llnBMvR9aOzJAgURswEb3GWRGaeiXyHYnoRtzAU+i0c1QTacQBc2dEQfIcCzltxxaiXWQlWRibBiPDSpsTDDWFSzioECQ+kdvTaDruzOUQTFD8pFswxpR'
        b'XBC2i7MzNkMeQ9lo7MzcBCcG2rLCbdo6EA5OZwSbh5WYzgpXLcFzhsCxo+ES5O+ALNNt2DgJ22KxIZHkLB8s2WSN+Rzu6BK27SHj/SQj11QDV6z05EwRVWS8n+dMD0Ey'
        b'h06EmWTOXmA4DJZ4Gq57UjoHyY6hWCG6kIUhnWEQWewyxzwyl7Mo6Sctt8xZJGO+IJgBQDnDxR0aoiko2yc6wlnPBBpRPAvbh6m2GcUl4nVTMjsOm+obG2Kt6TYyFTFn'
        b'HDYmxZEKeMt0SbeVYjmDn3AZQDJo0re1x2yvSaKgu1rEy2S2lnCgiApHipTuBleIwLEH2qzEJQl+HJiifTkcpjQVWXDZzRvInudAMc2HkhUsBS7IktzXcXnpICZDmQ+F'
        b'sPClUOtkJ/AiEs98CR7bOJi18Rg8ukXD02kfZs7WA8HSS2aMlyewPgwhzVgHbaQ5shzpSNMRdIMkY7AFb7I+HLcB852NyTX1GqsjyH0lWAi5UMhYQYbM8VKzf/nSnZms'
        b'OGTL1BVGYTkcc5eRlI9DNctnO5TuUt9pNayDKWyxqTVHr8qcskMfzjJQrmwv0lDuksFkWz3DWVjPLCfVzmLJ+3j5MiZWURhKlsPKubI4wZ8DUl22hHJK6OmjB1Wa7cTE'
        b'X+oNjVDG2kIFp+KgBY9Sjg97Ilh4SsmAzJTgBdJXHJrq3GpSVV8KeZVD9MKZmA5lkhBzyGR9Er4Pj2muQjplN10XTjJxJwPTxloH94dKEujusQTS8SC5z8cOMhzVK7sO'
        b'aZDrkGWho4N1fqwswwO2sWJoMFeg2pCs0dVSzJpmlECprTbARaylk6OLPE7m2hFHtTo6aYtaIbUlW0z2WEMi+l6E/AQqwYyFUkXElt6fJo2T7qXUFbwEPbim58wGdggW'
        b'Y95DuWXh2EA9OBJuy/pkqddgPioot2wxnODP6BLlV4rte6Cydyn7P8+aykwETFqP7imtzzEU9SlRqkQmWlEEU/JuKVpJjEQZ1/epo6bEjOFjD6VgXBJzFl5nJDGUEmlb'
        b'otvJLZQejel2+osZhQd1k8K5NZgrAobq4CSN37CM2s3iqUQYTwlP78pDgxO0LsC6qtBN4VvDu8Oo6D0alpmvqE40fjl9YYmwjPzon8wss0zs3F7X+9AxnuvCvdp77R6V'
        b'7lRvA69Tf7CqWnt316we2dCtPvf2798w/UB7JmzNSEo0oQ68fAo1wkk3atdH83xVM97IN6g9ljb0S3zzu7Ygdr15OUWqOsr2pzg11fZ+ekLcT+5UZeO5jwxg7k3Uuekv'
        b'Mctqezg0MSEmIqKfPKXaPBmdKbnfnjygoA73HW5WtBzMRfmvEIk+xBVBV1sAG+aKEBmh9j3YSn09SIuHR9OIkbC/wm1712hDpzncTyEMtIVgjlDUCWIjxXjTegn+eVrf'
        b'hyEWG2mznNg3YnHXjNX5ssVUi+fnRF60EPDcTCDQGJY94k7d3QIzE4jMTCDsFVd1HB50Saw33rfeWVrtWG4R4iNytEYoZe8nir1gBtKfLmxAXd0pVArVppjEqDBG1xoe'
        b'zyDDFcEbg6kTRq9paSmVFkWFB1N3JMViFnxCO1GNect8+NTo32pnnsjeMXPVwOBBQQHxieFBQZxMNlxhsyUmOiEmlBLM2iiiIkPig0ni1GFLg67bJ9dfQo/ZTPHv1Sf7'
        b'HFSQO4Lt6ORf9XCE9KCgJcFRKlLCnnB+LGpK6PQj9uhiqU+k0WszRRWVcz92Spj25hdBz4ToR7x3mwhWmeL1WQ+UIpftrppBllaS0EgRkvVMjtgKRZoDl25HPLKIjeEc'
        b'zYxRWe7r9jty57guO4oqNGoDa9qOEwyaQF/Ur6IGNLMDpYyi4pvJ1IfW3bbNZOE7o04bJ4McHEfEqYpu1lS8gaV41LZzVYlIWUekuAxfqiMRPSrfk+lZWIvXjZ2gHrP+'
        b'Q7SxfOXoZgjWHnN1NgRTSqkh0Dqkuzi4AtO3E7Ugw8vGww4uBnBbEXnN8PViHFCXIEPurLsqcv6o1VKVI0nE8MvkL4IczD8Puh1ibWkT7BVMjb/3gj4Nio64F5S50SNY'
        b'P2Lmj+8RfeWYXN9cp1kpTbAnT4VCCRT2JYqqfLTCKJFEpy9mcvkcLIzm8Lpl2Nyd7UiGNSGDOSFS2xYoIury0R6DjQ01rIp9JOswGXkq9ciz7G3kjWanjA8ffSQRTX4d'
        b'uPz9crl23MYGZBAZkEP7HJCfdrYWM7ax3ZuTug1HK5uHDkZbHzoYrw4zdsFyS6WE2VPn7MEDfJTKTPEEXhbhAlFurifS5iB6wKUg/pRsCtYsEaEOiiwid15NkzFa1uD7'
        b'72/Z6BbqRUbD5vcrwzdt3LQxaqNHqE+wT7D43ZAtVput/FfZHPrESWdKbIUoPGljsGFYvOYks7PxvM/eMdC2dd9dZGlkaCbbadl7F2ly67srOu20waQPTPvsg/tmnaXp'
        b'PvL7D9CVP+LcJivyggkv6qioptt4c8QXZCbeDtkUYcTW5IF/u/Wd5IknpGRVptonHsGalf1pn3AcS7y665+ei3v0VTenir5XbOseRxrMu6KPBbovbm6ax+g+O+R9k/6O'
        b'ULp6c/xVuaTHQQn96bk9ynwCIqcdSNZR0a9fmfyZZ+4bwaQnyGoosxaVinc6ZLqeXgZlQn8NadtDb+OuI4++1dH0x/XZiO8Y9acjdvPe/Hda8RHOLcmQbg78Q1RR+8+W'
        b'tvu2wbiLMtc/9nh97pniSUX763SEcZYy03evk82FLgXYNjKGssoVYQ0128jmi9BgsiSBukbCBbgaRkY8nIPWvm0uPSwup+AEs5PBTWzFq7aeZL1Lo+ZWe11BH1skcNRg'
        b'Th+9aNzvdHDoqX1zr9VH7kWa/sQ+e/HNfnuxw0NW6HKmOFzTAyECO1OkJ/ZGTD3QnNlL0gYwuaTLyX2aTtoQdtY4NG1Y2vCI4drzRnm/541dFAnqxWXRYwDY+bCTMGiF'
        b'XIEfg+EhSOZHYevhJj8JU9A7DmCaqTweG2KIlNBgSk9P6LGOYAbnJdg82IKJPdOweRo706HndakzlL5wua+zHX6yg4e2y6GBIv0rddneuAerrVTYSIdDLQVPFuAw5ONl'
        b'dr6yF85iNdYl6u4ZTy6VCXAUzwWzXXMrHAd6sKMDV4hghw0CnMGyVewhKFqIuaoEcSweJVfSBTi0CkvY0RukYx5ekqtk0/aQKzXkzgUr2COYZ4cnVUkSd0ylfwiQaY3F'
        b'7Njnj7G6tB3Nvpm01e5kfKTAMt8HTXiVnnbJ9kVQE6gAx3D/dtas2AAVUELrg+VwQVOfcs4QCk0WUKXCBgPaYN0aCWsT4rHe382W2tf5GVguFBnseWw5P5Ysw1w4MQWv'
        b'LMDcKU4yQSStgcl4cVAiVTcxbZ4NO3+FEryp5QtVQ64sX7YSC6d4+OsJgVikiw174XAixZB10sOqKXo0AnmSMAlS97LzPXloNOZjUywZx46CI+TA+aif//jjj/pQHUpE'
        b'olDMiPdati1MSFxEcz2zGvZ7arLZZkVEWzfG+Z3t6BFojRmkBP7WSjyy0s2dSkqHvZmI5EfrphttvA4OYxUTs7AJDwnUY6LzjWxAUfpMX3UDqc+U8YKU4Y7ToXQJWozw'
        b'GtR4J1L/bAdMNjcmjxw1hmQnfR1MDsRSXcwJMF5iPlTfxQ9ayAgrxRrXjdsNIgbHGWKrbpI+ZBr4GkEtHsTzTnhzl3IUps92wBJdOL5IiU1ToW7uVCy2gqK5mJxIrQrj'
        b'sHG1Du7H/cbCJH0p1AbCtTVYqAsZmAaFNpCCN/EI5AQMi9wLlZg8DG5uJvL/lTHD4DoZBanQGLELU6STrEk5skfh1cUDva1XsSWDjbXXnIaKUyWCfq3x3hHFnruERLbI'
        b'psG5gYxWlhSypINaltHKdhyDdmKWrcbr8lDMHsHSPBDiLuSSvl42ap/Hy7TjKJ4blK2Bs7QaxQaCwoh8WLF+C6XUILrAGXESmffls6eQ/sgPgga8jCWBE/HcGlLkjAmY'
        b'PCgADoRD+kY8jTf0NkGr2Q48ZJTI5J+sCGzsxn/LCulm76FjPsgKU6nPC1QpyT/KaX7JgIjAVVgcoBQT6XprjflWdBDAkU0DHTHH3Y4sGqSTB+vLnCZDGVts8GgSFHn2'
        b'x5ILmds0RLlqktxMpVEklOownwFXqF/ZzzEyXFmsJpjnx8j+20nR6BI1AZrxBhP7G+aJggRyxEVwEm8kUjcRyNg939aNtN1hb+644ejhbu/HXTa6OQdgpg0Zy0QRjKXz'
        b'f5mf/QqJsCPAdMcEOJ0YSJO6iBV4iB/euy9Xe3CoNUk3L19WWYfl+tuwcbmbh7ePnb1PIOcWpj4DO7w0XgN0jcbDfgOgnBT7ChsF/vskTBlWWEZHWc2fR3Y9Ds10Co9h'
        b'pqeDPRZs4oc7+lgrgXS4ZJ/oR64PwzNY7e+r9OYA9IErtW4pZHSXdrimkEbAi5BM+jcPDz+mIHrtDTjvNhra3UZPgRqZgNdwvzkUO2IKcxaAFp2t1COQrJVtpgb6eM0U'
        b'6xLiEkXBQiX1xVN4mlMFnSHrW70/UO4TsnxJyZJ3WSDD8fxq5nGibw3tnkp7EzeqT3v5kNJZdxU4pMI6hT4Zy5etOJdxlhyO+UN2ACbrY3YgmSg6NiJZLlMN2dYwaK0o'
        b'32aCKUB0KBGPkbXFeR5b0EdDxSZS1EKiBtersE5PkOAV0d5zo3JAIt1XvabDNczyErFoqSDOFDAnegZ3w8i0gyaNU84GaLcVBfkaCVYTYaeKLehhWLKLDMR2l86nwJCL'
        b'7XwPu6yHV+iB6upd1LIjOuIBKGDl2U22zuOYNRgueDKEftlISptTEcUG6nbVao3vx/ihcFEmGJlJB43akMgodfbjQS8y+gcMVDKNn8Ly80NOHTLAk3UiYu3ZoMDrcxVs'
        b'UScrWRM/EtTHIgkU7lrHCpAEp71t+bwJhhofHcFoo9QU8pJYAfCkI5KCXZOq6YspIUEd1LJrq/yXYZa9Dx7xwrN7RUF3nWQQVBMlmEkjx8hW00Lao2QCO7WVTRehKha4'
        b'FGAzytST7LgVnKOa1PfccixmG/FaLLWmBD/OavpqES4tI5sKlV4CVFBKiokXTdgMJyOYTnEd0p/5OgaYt5nRZ62BtvEkU6a9Q4YU80h9e7aOD+zXw1yX5bykzWSS5tk6'
        b'uI+HZjslWaAMnCVQPn5q5MFsU5lqD5Ge3n2tyNW/JfrN+Wats0cqM83D1zr6NQ587ojL0buF8xSumQr3IefX3FCIt04HjBTHeh0IFEQb/xuKfYrEuWNjj87akGsaW9iU'
        b'f9LilS9feOH2O1+OcH5+sb173uYA5aqNm/d6lw7Yscxlw/bzzs9/vyrgu3Pj2gue+c1OseDWxmkDyiV/7Pt4SHjrW7bVq/9+ZYlFmMvY91VbLRriA+0OLw022fdzY/b1'
        b'uPAyHdfC267fGm9P+91+bvA8ue3q61VvPuPnHzW19avD1WMzh7nPSfi+KeY3D7/cLz4Y/NrsJe+2RMQ+2+zz/t+v/mD91eN3GgrtNx4Z+M4nt8ovvrbGcvBbnzyxY8cz'
        b'Fe995bziu/WFtya/f8zApunY/aTK77eGH4sPGhTU/vF5o021XhEluuFBB2ZFL357y2KDQ9lnvl7l8Ib38eDqM79Kao5+8cr1r6Zu+9T4pSfOrAu7vizhj9f3nj4WvTn2'
        b'3ispP6589sufLQulKzOO/v7+9qv516Nkv+V++GXxq1FJVzLvP2+89axX8J5bs/9Rmn3r01cPDqr9xbnA1L7x5RfGjHxDOmvzeYvhC+6bDzy8/fq1B6Zv1d15fVgJBLs9'
        b'bdtwOGLR00Uzl9wKfWqO49i0hhFPDX99rNcnpUPWJOyts3o1480vxVbzX59yMkj84ZTPZ7fbTH2crpyOKrb8PHLk459N/PHBpl1g8N272+zxH++/EXrgj989vtMfYfpp'
        b'3FjbdYe+uuwb3/Bj5qSMa8/P/eFQyGcvLvze5fZI4ei9M1nbdtW++nLxqWcG7PX/0Vv4yPbg7LaUpwetv1X+hNFw5Sv37qS8NW1rzts/TS6/8H3U645bPzp/bMITu74q'
        b'euHuiX3hOhFPnHu2zm3PZrMZHoavXn1s4Hr9XfDgdv2917y/X1E/73edqw26Qz50Uo5nZ+UxSZjc4eCAh5ZrfBwgdwHzT4ETI+09fe2JsHqJuqiIC2L92Pc7/Ck7eqbX'
        b'RCP1unNYZL4ji+A6tlO3mDA/ZVceDjiI9Uyfw5wtWEN3yV1Qyf0e9KGBer9AKnMVsB3lqlkQfSBHsyBiug5zXCE7SsoSzApZ0Hk9DAnmmuIFaA7ROOwYD9W67MzESv5s'
        b'Gt4Ybst8dojCcIrzh0zTY7mS5fmal62Nwwi8qcRMok8brCbzdRBWsKtLyU5/wJZy1WXYYY0fWZUgR2KP+Xo834NmoudGaOjG80J2uWOMImwBZDtRHwvMck6EI74dwquu'
        b'MMpThqVQuJLp0Ds3T7N1oLnr4UmBZHFZQgT5kazoA609macOtMMpDc1MHhYkMKn+NByYqYJs/ThjvKaifnVq7xk4qmAONGrvGWzQhTY4zP1b8OwAQWuh3DWfm2vN3aVw'
        b'2py0FnMDasCSbZ4aK7FbjC/z2xmAaVI47L6PDR/MMCXXstbsdST9bM+oBfUEU1/pJh1M5zccMIbjtr52RFkhaseQMHJZjm0SvE5ECeacMgDOSYlgAVcWdRYsHNex9oD8'
        b'MSRFGRZ27BITIZsXP895l9p9i6gFR/g44/5bkjiW8nBo9FD7vECDyN1e6ABgXhkLyPLc3I8Txxo/jRsHtkEG60QvIvyQqUL0yeKerkOyJCLYVzKeN2jEY35dnVkwO2ZP'
        b'hzMLHiINTOugQzaTg7Y2kOyg9NAQ6ZhisjSGaHRN3Gvm1LzdRFSmLHB2Ji6kDeTREjwBZfOZjxNektKjhPqQjl3N3p+NllisGUYKWYYtnTZ/q9l8+rWSvVSz+9sQ3Ui9'
        b'/cNFZ1Z+PLFnBhV+0+BgHwJAFBQzj3CiQdykm7E3kVsrOnkPWeIhmfm+4QkzmOhoG9Cvq43G7LN6mtbwcxxP8rWncfd6Ty/3NVhFlh4/0QYvDGbDwgsyVnvaWUeFk9VD'
        b'Q3LnNUJp9O94vSiH/xfBVf/8S4fV3bQbsiSza71EXnrYtSZTE6w+o3oxY/RCZpQsT8Ih0/TV4GmW5Dq9Su1TFJqNAnzLyGeZmoPYhP8nKdFP5uQTTcOcke2ZUd8dkoIR'
        b'C/qigGyU7d6EvVNPIBOSNvX/MZTQgF7+2wEcKyEpSNg7/6VBu5SaxkidFo/O01rKulW7s+MPd8ph0VcD6ctg5vMTvl3rL9ApmKnDjjfo/1rvadyGzLVxVbSEjGSHF2qg'
        b'1neII+6SP236NCfeWdiFPrC/RlKKLJbLp5+DTXq0KTKM3IcfbGq4A/8h6cUPYEFEAqUIDI6KYgignfh3SaEiaWmCo7oAg3IAqbAwjo8XrIgOT+qRKPcfsQ4KWrY1wT06'
        b'IihIERIVE7pF6aAGcdV4FiSqwiMSo+jx/o6YREVSMOctDIukVIM9uYE7FyIymt0YweLf1QGT4SoeRckx+xQUiUgRGaZ6dFZAGrY/S+HOTvjJ+FNFUqBUkg897Q9WhCaq'
        b'EmK28mS1VXMPCwpSUlCXPp0iSPto2oN+jIxWbJvhQCmnF5JmTKKNmbApOEFb2g6/i15TVNeNobcyFyHu3UASoFiuXZpIE4+6MT4mMZZBuvWaIql6QmRoYlRwPPffUDPE'
        b'czQClcKaRoLbkSYg2TKQkB2x5M/whFAHJeuEPvw3aIMmhGv6Rd3vzHsrujv9o7r3w2JYNGwsxf3tLc0uHdAPfaIo9EafaOjDFEg8MR3yiIRsE6sNB9mkjnniSvPBacZy'
        b'bHQhUl6PCAIppBChOD+RhhJjKpyxUhsGFfpSantsjnPCgqEj3QaOj9tDREtIJbIQFKxd6J4Al/AM1OrP8YGDRnYj8CSewZOLoWXUTrho5kTkkFJms1m4nlnurNbFBHmk'
        b'6a8VEseRL23MqdMpkU78KeHtERp+QoN79IQxm2W2q/AS1mIme3qGoYwabGN/WBjk9dSoIULk3umBomobuZJX7Tv+2ZvGB50sXN//tTT7lyGKRWH7p0aJg4yft8+NzF1U'
        b'PPXMjqjgmKHjms/5Pj11jDx1zffyZtM3cne+WvlZ0+wHl36Tpv32xDdfPf/RRcWhxwafdDr/ssO8lNc/f/XGDKOfmrxTPnurZOcTOT/IM5vG6tY/N+rQ3GFNL5TV7VPK'
        b'mWg0A1qxvKvn9TzMpIqJHZxVCwcbBnv6QqqpPddL4Mz4BBa2Up+E14jEgblw49EPmyBdwlxm1mC1p4raSO2tNdYhyIGqAZgrhVooFplUZrVgI5GcD8ERjd8211/KQ5js'
        b'tWI57rcl4q3YyS09BEu4QJuKJaupV3oL1nLPdHGJKpbrJmexEY6SB68t7HDIn2fKvfnrdY3VoQYdGhWenSnT3+nIHKMT50Frd5d2TMMctWxqvyiBIl+QGlzECq1o2oQn'
        b'NeJph3DqBbmaE6+HeWsY0MA4NlGZTGLdm0yyT5hJ5QgqXxA5Q0plDyp1dDux1ybUlfjQsusG3ovfhmXXjTSc/HmObqSK3jbSZOFd8769BrRloN6XZH/ZQDYYLSSAJlK0'
        b'L789abq0zzhRzS76s6yXXdQ/PFqN2tkVKjxRxXfVcLaukUXYdaH7Iv9O8N99bUXhIZGhqg2hUZEkFU5Sq8FDiqD4haGbHNgdDq70dRG7rS9U8U6pqttjFvP8s9O6/lGc'
        b'W1U4K2ZMfBj9gizyvS7CapT0PsvgsCTQK4hhoCXGRsUEh2lqr2mQXhOlYJpaTDO6P6jdXlWJkQkcq1xbqN63hoeWatGigCC7v/po4F9+1H3ZX310wao1fznXxYv/+qML'
        b'/+qjq1wn//VHpwQp+hCgHuHhqX04X7pHcLIULs6Eh9kpbNTD36aLB2dXF1PmfNa7/NGX4+iS+GAGGd0xhv+Mj+hKKrHyVWHbFAenLrOF+bZyqFY+nUiG2yKD/1pLLQwI'
        b'7KUIHSTWdI3h5eDTLTKsHyFLJnQiZNUKWQM5R/UWiZ7wI2WpVgR5Rc4KF9hB89515iq5ra+EmrkEKMb6IeyQYJc31s7ASqxzcnLSESTuApaSjfo0O6PBkvn6tj4ORC7A'
        b'IrgBx0RP3cVcirsKJ6DY1sdDIkhGEKnsgDjTCErYpcXQDKm2Pu7koQV4CtJFF2zAs0oZO4OBxp1Y7ciOoupM8ZqOIB0qzsF2PM2u2kI7tkiiyMXaBLxONnUsFEdDKVTz'
        b'E5qreGCYajLZ2EQnSIkR4HoM3mRZxgdjs52+ChtNye4lwQrRBg9ibuIA+tCRwY6Yz87Wrb0dJ2k8AM9uxXJyPx4DShTDXAZUE5QS7lBwxlgfq+FQlzIuxHZ+qHVoxni4'
        b'ALXdyngEMlljjoEreBMr5J3LAukO7OBqJpQZ8OJ7BNPSQ76rUspzbIFkAfOxrUuWi23Z6ZAzafgKLIOybllWQBGvSz5ehLJAuCnfZkAGgtRAdIzEFtZ9lpC1zgdvyI3j'
        b'TQVBaifOw5Kx3J1i1TwiIzWRFOvlJqIgNRLnwX4hcRUtSzvURHpSGdefec7Sc1si9Ap4FvJ2E5H6MKZA6wI/KICTAeTPAmzF80RCPokF0Gqug4UhOsbkxZvIZ4ddFAOJ'
        b'UGhuCpUjoD5yTOEiHdV9ksPHcWMCX5rj84STmc57xXHTT9yLEQwycjL9Y7OmDg8qGLO+qdbaerihWd5n1tbKkzmLFDabN5s8rqzc7t54p/DEtzNeDP3H0bWbV7v/4u5Q'
        b'ec7ao/Gb4/sDLrt4Wnw9puHsU0O/noolkdX3r9sVP7P1DdXT+3/3yZqKc03f0vcac2GH76mMgkzFre/98n8trXgw+6fUi4t/cL79Uurzv9vmhf+zdMvQrRlfzY6KC7K9'
        b'oxflXNwyKjH71fbKFf/Su/nDXN/IOt+3D1dlFw7+bt83X956IsjQvmCPzpWcrw+tX+CbE5O2fpHvxJtzXt28/f5Lxq8VqXb+U++3cO/w+6aHstfdjJmgtODW7XNBcEWL'
        b'GyD6Yzm3yM+AFh6qmg+FeBGPkAnRJVQ1QGCPj4E8rLLtCHebDWmCkZ1UD44EcytmJlyN4xGwYzGLSvKlkMkDF69COzSFbbPlwZMySBHxYDjc4Pb6LKjCEleLboGm6zZx'
        b'u3MxFMEZTfT6LMjQCOkpWM+52XNnTbGlxnp3e8jGSomgj1kS2I9X+CkDJkPBVpUcG0RBhMNjMEvAyjHYztnUS8kITIWs2GkU96CJqAFpZC5OH88l/GsittFruoJoOo6O'
        b'wKN40pxL+AcheS29RNL0scUMgQzAy9DMGskVzkKxOobT0WfZaG0Mp/02nudlMl3SVNtM6KlzLT1+JiqpE9xkLbh361IVHCYqjCCK68mqgPWzoJ4pSX5Q6kce0hHEID24'
        b'IODJGTNYcvPIhCgis92IqL14xhuqBbLm5cEpltxia9yv2hZHcrIli2KRgIehYgf38TsyF1rIJVrvI65wjPTdbjjHbcHlcGYfnknspjxxxWm8oo+QxX68jWUqIhozxWJF'
        b'74pFEFUlqNGRMlvL1CZOivfHzJrqXyMWTmgo0RgZtf+JQqIv7hzQ1XGY5OijgRphEYZGncXp+Iiu+oioqUOkVguJ0IYCbiKfbvWjitzq4sDcsxwkdSnLxIf+G9wNvOmu'
        b'bIOvu89d+YZFgX5+rj6L3F39OVClFtTprjw2ODJaHSfIghXvGnYE0qnDGunN3WIbg7uCPzEsKGqfZLoVqxVvoKH/LxnJ4x2p4idVw7Xp65lJad+bSE10rOZLyKdHRpGU'
        b'mJkZSUwoJ5ls+nZ90WKEvshdHK+TJe6qPBTPdTUpiMLQpbLIueu6+NIaqd9VNmJXgjKKT8WxqU7K1OhU/DPFqDIgv/QzxaqiSFX8+47PZhQMMmwg+2wRNkj72TJsMPls'
        b'xT4PCRsaNixs+Ek5pT5L040Qw0aEjUzRp2CUBXoFYpi8wKhAv8Cc/oaNytYLm5RGsa90iRo7Lmw8w3LSY5RhE1OEMOswJaVEo88VyAskERLy1EDy36zAPJL/ZU5SMy8w'
        b'KDCMkIXZhNmS9CZTXC2aYppBmnGaeZpFhD5Do6IpGzDfVV3myzogQjfMMcwpRZ+CX8qENXKmIk+5a06nwSJGlMBQzCLC4x9M7iJM9rxBzfjV+aYHDkQynRWpipmlSghj'
        b'75OdnCZPnkUF3FnbVWGz6NRwcHKaRP4T0XmKUnpX5uPr531X5ua+1O2uLNBv6TKleFey2JW8GtAsN/j6eK0maxi1AdzVYQrlXQPOaxFJPupEELVY9WeynUSzlcXH0fkU'
        b'T19UdIbK3H38OaDhn0zLmSxYXdOK38kS9F+8YsGDhZsSEmJnOTomJSU5qCK321NRP55GhdqHqmPuHEJjtjqGhTt2K6EDUQicJjuQ/JSSjvTJZwqpFb+UhQbfNfDyXbTA'
        b'awPRAB5MoIVetNCdlZC8LwveQRc0P2oDViWQRB2cppJXsrbF8bDiaTw5Gmh418jf3Wepl+uGhQsCFrk9YlKTyOob16XKD2Z0e3BRfIxKtZCpJl3T8IrZ6K3ayFKaRFOS'
        b'dKRESpZM0zLt1h4PhvZdqQeDem08pbxLKnS49Uy22xfOfaTV/Wtn9nX/per72qQHtn+iee7qhYVHBCdGJbA+YwPgPxKJsPFR4jm4U/aBaXvk23bBZRON513QokjPL8sl'
        b'LM7j9Mklnh1RHn6fKxO+6yfO464+5SBNICO/71Am+ruUw5N2XXEcNM8+esDAEVKrOeSTakzv0kCy8GSXoIH+clXq8d17WS9buJ92H6dj+TOKUxbg0yXMwFDTvBSlioUZ'
        b'CBreTA5aFmGoDSEw7DOEQBMhfECvF5umO4/UjdwZ3smyyelv+EETXbX7sWT6a2hqFbGMpICJMKpZPW+0V3SbWQprsmT3fxudTQ+9w1lhbaOKpKdW22Y4TLd5hCT5BFVY'
        b'L3J7+M3qaUtvtlM8LJ++p7bC2j3gTz0xqZ8nHnUZoEl0L3RfRmO14YtbiHgQtZr4SAO939eTdIPlj3UfNrHxkTHxkQk7OFKutQ3dtimhFN24bXq3I9rQ7ZzeQzdXG2o0'
        b'tqG7oo3SoeNgdbrDZAenWepbek+m4wzWid2qTrXj6+nsa550XxXjoA7qqvUC2MDbZ6KKYTb02TzsmGJW1yh8Nsl6h19QR9H3WaYOnIVZWkrVnkAKFNRAewzfyyk7/SHX'
        b'GP8dteMz+ylzAQgPTqADSqXhBuuESkEPofsI5ac2WJJOUnC82mOgE3UDax2Ff3g4rWtiVCe6sV6TWrQgwHWpr9/qDZQPx9ffdQMlRPFnpdSe1nMStD4biS9CvH0YaZEa'
        b'4ETTbxrVTW097v1wu8OizE4peAodBl+bbmuKTZ/uAayHYvk8VXEKtW5LjA2vneaWyOjecQY4YgURYTUMsZuCoxWugX59WMajFf5JkQk7w+OjWMcl9FN4viD2MZfIhHFP'
        b'CI7awR7se4Wz6XvMqqE2eId0IHDQka/uEi0aBz+k6qNGCdzboROUdpdnu+Co9LlqsZR6nBqQ5lGLTCrN8O2Wbu99omYV7MiXsTmGhEfFRG+kKfVjXafyiEEP+cnUh0eG'
        b'JU+HY5jviTnUJpNmL0jwnGiNmWO5mTpvp4Ma7HLuaubfMB8Ocf8GZrtKhXyosMDrGrRPAa/AyX1MOcZTIwdFjaEB8HAYr5PfOsiQCcaYIsEsyMHzifPJTYO9Ehbt8dQ6'
        b'yAYs00CP9gmJ6a3jIRGmwUETTDHCcqWEmYBtoWyP2v5rAk3cBJwyiMmHk02xhdmM8TxmMLuxLJhFMc0dDTc6wZ52lEEbpRJrbOxHYU+t7X0CrYfjUdIqeNgRM+0o2CUH'
        b'VbXXJbU+PlAMx6olvDmv4gE8ie1YpAXpFPDINMhgRxnV03WFxeuG06MMu70mugIPS6rYsUoD3BlJoa09V7rRg/oMUmtHP0z3Wu4m9YMMGs2GTVC+Y7wA7TI5Fs2C85FP'
        b'/rNNUFGTzFdPVo3P9jSE+WaLL+zK+2Xcann0zby1t7zH5iU/M+45/VuKgtlHch8bPbF+6QzjrwcFztn9rZVVSvFgyVi4dTZ5adNOv3e/e1N+K+mro39zSK29UzjqfIDH'
        b'y/+Y6u7s98krkbEfXEtt/+aF29+PW/xyRPMWc7M/oqf+Pm7A+/f2zbCO+cazYHP5900jHt86fsnng7++//SaX080V7ybUP43eUjOhPXtyijHH97erTRmBkYfKIKbtg72'
        b'bvYSaMazgi6clzhNhQbmWKzwwTIOJEwBkJVL7ahnhp5g4iedhDkcs24d1E221eLi6cdOY8bbphnMuLtlM0m9KyofFigkeMwYmhPomdHm+Xhkn40aVVFcAGXjmM13NjTg'
        b'OTYGoUnVyU/behH3d24cDSe4mwUchhtdnNd91vCS45lojZUWL+DNDqw9knQNc58VoRJbu+L2wYWpWug+GRm92btZNbyhbC4DWYRT0couKIs37ZjBeCo2D1Sb1F1nqI3q'
        b'O6Gemb8XL4NskgudbvXS4VAtSL3FJVAJ7cxQOwzKoELEdDLZvUgbhIiT8Bqe6xLab/hvGdy0yHCz+lKddpuLhmp/VArbIWPGWRn7T4l9TSQScWgfio4aDc2np89n/zpP'
        b'P64ifwHIzbtffa1h5EP1tUcFdeOoU3d1NlCZth/cqWzyiUO69ZadlpbY4RHk5p5wbNQG5u+2wO+ujNKO3pVRBlKNptnV05b7sVK31rt6atrq+AKxWzS7qWYXchO00exc'
        b'0TRSq5rGHCE7zTTC9BFi1jVONJW9KZwLwsJUXemVNRtuL+ZCrajWU2+NUMyiguSsIC2CSFAvJ/52asFHi25FvSh7Op12pxDkPLlUh+8QZxNo6yWohf1HUqPUArCWTPZh'
        b'mhRnneLP9sL5GqxSRETFBFOzgoIRnKr5HPtytwmO7sKm1p0qtq9SdFEveuNyTQjfzmXnBC0F6lbuAdqHSye5JzKMCn4dTdHBR8froLBmhOi0akywG+O3xMHBYYyyD5GU'
        b'O00w9+RgOpo60R9rU+bMj1xU7rjea3raZzqIHNVDQO3Q1ZXWsdc0rP1cl7jS4x3XDT6B3gtd/ewUGg2GM1/26QTG/JH7Zj6NieX+2f2ksL03pbAPmtF+kqM/Wp2RtnB/'
        b'Kp0WcU09qntNTcNf3Zv2pyCt4urns8Crp6bXuwvzI2p/GmIr3hRaBmA6YNXjhs4LojCHM3rnoCCfmGi6UvTj2709oSN3xhRL2yg4ivpT0wVCO3Qj4mO2kqYKC+7DCTsq'
        b'kRvZNkZuC4/WjHwyNcOo8491aEy0KpI0F02JNFwk+5a0cp8F48l0Nk0oO1dTzYccsjk8NIGvB70rQ/6+M6c7TVJwxlZeH1oGOzUSp7q+zFZA5yZZFHtNJyIxns01Nts5'
        b'92qfGiHfiWYp/NUamIYXnbqp7yC5REWRyRccz/UwfnPva4tKFRMayTpBqw/GxsdQenPaiqRp1Z1NJgIf9r03ZieGQYUP0QyDY2OjIkOZWyJVzdl86ux23/vcWaSmV+/g'
        b'MKWbtMKavCrtFHSrVlj7BvopaWfQLVthvdDVp495aNMpjmC60uYRohu0Pl4LtEt9N4ah/nxHtWqpfq9q6SjuWT9ESqX4y1DViWnB2oKJPkyTMpqgx4BVlllu81q124ID'
        b'qwxdhi0qY2iElg5ttG35EjVvwom5FFeFYqFYMx+pOAOmw26lgAUMjUUQhmMxg2MJwcIAhjVgDcVwqrsOCxf9uRrrB5cTPcldj8WMxSw1CwLlyAhQYwl42tuscLPzCOTK'
        b'LNRE9KbPcrCWGtcBkDUNSnmQeDlUDyFFuh7W4dJEMihnMA/mEXMeITNtTpOwjQFpaKhklltr0SaUusIsJwus3UxSpsp+DBRAiTwJM7UuViFYl7iLFqgSLmCKJx7SZYA8'
        b'9h6+VGfmKelgHqYajh8CVYYdSup83E+04Dw8aw6pcD4ATocth4yFe6EEDsAl8nuOvB/ash1yoWJhyHrIXBgfuXz55vXx4x+D4i2bzATMmTMcTuIVzOZmiBKomSQ3ssbG'
        b'WCOJIMFW0THGITGADiLSxdmefZUKM4ZAxnw4GgKpXYqTimexgH6mXmDWk4NMMU0hwOXlA6wgE6vZWJq+Hcrk0AZ5Wkc0rITsRArD5ArXsE5rOlCuUIPuxCYmBmBurLEp'
        b'5gWo+7iTVYEaE2j3cPMGpPl2ANTAfqjUZ9mYYLolXlk6gNlGlhliiQYbqVdgJPpMAK/ucKxV9yg2QJrxUtJgqYmUphbOLx7m2ZlRKBsuL2PDhqTqSb+4hk1sPOXrqDwg'
        b'05wM8UzM9yOKeKaI7XHGS5fAaTbIV88d1yOhUS5uHRj0KzQpstQgVQ4FFuOxYhBcgHLLQVIBir0pqEg25jIuFCxdC6mqnlBGEjyDBSSfehfSPwcwhbQt88eD9M2QFyJg'
        b'mp+Rn9SVhc24EKW6pJMNx8td6WHv0J0fRLWIASSpy2XcdcqQBjuVaA5HISsocSUt1XEsHqnBdFju1mfao6CsM/pSX4n7eVhAazBmcX/Rk3DeQLUNmqC6wzQEGVDCfHpY'
        b'gA6mYj3u17LXaKhrSINUM/oarIAmSm8Ymb3tJ0FVTvSrT2+1ei+/Gf3afLN3Ruy6+eOpPccfyxu739rVY+SBiW46cya6js1tfWX/PQvlG8YTz7tf3CVr8b01VmFj84T0'
        b'vMu3+tbj3/3K2Tx7Y1vZkBdvP7vYb/mwzcfP5hZO+67FLNH3crHu5xbL/C5cnvmLx8aLr343b0xlxcQavbfH572R6V+2e923io0ntkxf19z2TcmUpc9fmdg4Ot5k+k93'
        b'8885FJ5/UfeHyJYaWeiNb54Nf/7gjC8x+yODB594Nry8Yeq1Axc+/XbYXdNN4WFbf/W8tndy5eyWvcPmDHLx/ea3/Rst5xz6xCHyX5JRsta9I/ak5TQ2N32v+65Ovev3'
        b'E35IuPSm53vnvq15cXb4N29Lj19+bH/rjxMUx59w+Srj3tDHBp31ffnCkrIPr/r+7amPzqSZDq4OeXvO9/mn05R3113+x5NfyBJn+Nw3rv5o5ttGvyU94fxz2XsbDr/9'
        b'07Ohtw80Htw2a/OOfY9vPHjoX+MqnntD2X7v2olF+xvP7B293bnYwyF1VZlxY11I67oR2YU1y9yfHzTh/MfP30+Vji28/eBDsUb6k/udjBfjxm9+J814ZeBbO17cbXJ9'
        b'TeE7bf5PPr3PcuHVn0JMlZY8xroaCid4QrNrN0QAbFrIwpt2QeXqThYsso1pYBcOYjJzwhuJaTM8fcksuqo2YmE1trG095hM0M4EyIQaDT5CFuQx09mM9VFkjN7EG10A'
        b'YyqtWHzTFMjFqu6MJJACZy3ipP542Yrl4LbCXMt6ggcTNSgKpLQ5PBypWr6nWzjSVgNqJVuOZ7hH6AVrbFGb7/CqvTZCqpTDHIzaAS22fmM6e3U+BnXM5LWKbIYHbKFs'
        b'I5mX7nBZJuhGScao4hh3iF+0gSdmQhEe9OKYE1A9iZV3oIqydAzFQrX7pNYo52qXMIGW9yhpp7oeXBrr4YrWJgeHwnjHFQ/EA5rgeLiYMEkdG5+D1ax84jY870nmdQbm'
        b'2FFiNpmdCM0DzHizZMYN4qQpWmMeqU2OQrZ+lhd3AD2HNda2eFTB7KLcJgqXXVlsFrbjBaj19HKHDBajBvtjOkMUOcENXUfIncMLWQ9HyMaatcTEl0FY+RK5wmSxdA7k'
        b'jmH5LCX7TI5tgnFnYhRruM4dW0vhOrUcKtc6etsrSSHmSBQ6eE6p/8jBzab/HRe+EA1mYzoVGXuzKO4T5hqKRhIWvy4xEmm0u5lEV6ovmpvxqHMayU75KDSf9Jnjp646'
        b'Ot1MaiWxIu/0vyWLdafsFBaivo4JjU+TMHulxEQ0Z6nTuHRdyc4xvVjaugVd92Km7MtgFn+8qwfpozd654jy472ElfcSUZ5L7Zd0q+nVfpksfGfd2YL5CBXt3d+H4hUy'
        b'wx73HxEidLWeP9KHIcw/COqhNPiFRxN9VfUw6x0zFajVE6qcBqsUq7y9+tFBaFTFyB46iJ0PY1TDVgt9z87MjB2ocZgMyQw5LmuldY/YUTwJV4wHQa0DOweLxoNrOm3o'
        b'WB7YiY4OT8/UAFgdIwsvPTKyGqSRDArxXCKjJroKKdhKLyY4kHXVIXHYNvLmQYMzx63XmYEnNqrjQEYTYY7kIZuLFYI4UiCL+s0hLPkZwyBdc8ZHD/jwqlS09oDrTJUa'
        b'5sDR3ZwmwHhZRAQ/2cNcZ2EKxYqkruCl4XiWHjpBAwtDmbUFyzBNE4ni6DyXnwUWYzNmyg3ipSpoIA9VEe3LHk/za9l4Di7aKm0o6MgOrE8Ucf9GPM6jb7LtsRYKh3rS'
        b'rcNHR9C1lBgNkfNC1EMZXN2+2R+zSQFJqtSpHi/zMJMrQ5b5a5HdoJyyDF72wxKuL5TiMUdNpMgKf6I95UArb6S2dfM6x55sHi+OtgjluRVDzpZOQStKpTgH8t1YuMuG'
        b'7SvkjPxQKrjriDbQDOfZMwOjiLSsDTwh+kqVOC8BixgioSTYBcsh159UviCQ7HiFFDVO31cktUqDFh5mPSRHGC4KVk6Dj0fOnLiHq7aRzmOExbQ/xGi7M8vn8S9f8OVA'
        b'jE7jL4/40XGu0IWcWDvr6Hhj5MSWZJ4Jp4XdYpgQJqZKhghnNDTFlB37M4o8SANaF4TFe0VGh2uIimVR9I+euLnkZZ2ulq2Y6xWH8Nhahm7OjyoNNEIv5rH4CdFvujNR'
        b'LDIgwxlTt81fEhHnHr8XTvpFw/4Rwu7JZnDVBBpYzQQ/IxrcZe004d2A9bZSXt0npZaCHVHvnfYuNV0+y0uNKFuHGZNZuNVVLO6B/Oc8mHV9eAhkybV64ijIFx1XOLGu'
        b'D4GLUE4uxRkT8cfCG1LF2VMxhWW3VM5hWp2m51sVD9ojqI+VMSsuTjOKiPbXIM4ju+QJZk4IJgpsoSZIyVwiOqrgEB+XFdAsxTrymJ4gnYDN0ERGUStmKEUehFYADXBT'
        b'5UNEvyFJgkQuKqzN/3JfRpC+jC/hnqknRC3hdPxJsVf4Y/JypVM30hqKRHkskG/DRlMJqUfsQHEmkTHaWEnnwZkALJ0tp8oJXqbUeO1G7Bl3121YZ4SNelhNT7/zaRRK'
        b'axKnd8zF65izJZKWYrmwHA5vYopPIhG1quTWNrZEAr2IV73INPCQrIEDi9VIjVCku4O0UZ2jB14nF3XgoEhk3vaFkc/cV0hVy0k9/jHldHigp8oi0KLtetn9Z2/PX6gw'
        b'Mx85KSXd9HD6gbMhi59YaTF1bl76TqO7VR6mc+ysv5juGr67/tiKHw4Uuq5++1+CrXxw9erVDo/9POyxtcdcm2I/SvL5KUVmmfTg5Ne/PnjrzU/iJsaZ11xo+dI2M8G3'
        b'5rMn5AkRRwu/WFXYaNxyZHat/Tms++DNf35cm/36sqveI0Nt1x9O3z8wLw5Mg5vee+y7UMeXAz777I6v3ek797eEJ3y/x+/eB/7T/v7PI9bWNhXmK1emDSwMrL3Y9KxO'
        b'6PTqincCWydd8kv69t0bEZtX26+Me3t7xd7HnmySvlM4K3fJC8uHPjXDOKitKkKa/uoTm4vXvPTCtMtbA/I/2XZvbtHnle4/BCTdfe2ZhpeNCz+PNb9nZlz0oPbu4z7C'
        b'mwu8XzW77Z2Y9IJ1RLPqt/Jlvxk/GVu1XtqYv8a28Y7Nm+P37noS9v69Mvv36lcbJ7+Q7Sd3+G3I3QGX306q/XTi5gXtPm+qTm25pef66+yEXas8D94umP2HzpOVLoGN'
        b'1w9PfXb3V48Pm2LT0PzsnapBxrdGLV3xY/ivkemDql4f8ua9g/OSE80GTDjwa9jXGUGTG+Dd5JEfuPl9lBHkYVc4wsHFr/5D+ZaU+0+UOOqcsvQM/2nwyKl4YuqQorHg'
        b'IkRsvCXsqr2TH2j8xu8PCte8UZ+1ZG6N/v2X7D4/1dKk8yWuWnp15ICIiLETV2wf9um5+UfE0I9CVz2d7fNlevvXcZcnZiZtmvGl8scl0++9kHd64ulFV77dNfTZfJ0V'
        b'39nsuvZ1TfzxOU9uPD3m3TWfb0lauePCN0udLky/uHmpcum9vaFPVNxMP3Z1VrN7aMjfD1wYcCbnX6PcvryUU3Xm6ytP/vFBxAdFEd94+b5644lfDt7UsY1+8svXJ1Td'
        b'eLLttuebRm4/zct6cuI+k9uXw37YsWqj34UPv3GPM5k4XPqdZN6t0vBhu96E34KcnvzN7uPVdt//smTfbL9fZv/+5WLPT2MuqI7+ustzxtdrv318feiw3xLvbvjxvnXI'
        b'W60X1m4Ne94gpvA3+3/cjzZ+et+k5becT/5c/l74L3OW6LXVjbvv84lvVfvYH+bp/Djoveffe/0142Hz13/4TsQGm9eNPl4WOcNF7/vEz0zfmvJ2pFfmsG/vldlZVLa8'
        b'6YyJX//6kfM71uee//b8Myrzl6OP539w6F3D6U9a+nq8v7XYYsZjgxNK7EsL4M3Jyurb7wwI/qqkIOTFeL+3vhlVXHDQRQlRpQX3f3cfEFFxL7DR8fz6mcYfP59d07Qs'
        b'Pmb/+w4lnxjWbtj705sVhTt3H9/4ddDNrB9GvnHgLc+B30XL/xjxjME7fxh9Osb7mP+NsDVRxdOLhn3z7oytP/rXYF38cpdTH654o6jguS/uf/6d433DGQ/0/nnwk+pf'
        b'9U/Nj888MrBl5T/3f7015kbtL20/eu76pfRElO4vwz757VZLyjvf47QPFUltb91Z+tG7n72y4qP0s4s+jZs3y9u/6t3icvy9eOn1By8fqJwn+r+VVfadccr2iiP4gdGd'
        b'307NydrXNGbN+Opbf5xbUZGn0zSr5uJzf0iXNS1N3/2rcgujKJEPh3zGZDJtSS88JkS+a2RuFRN9sZorrqfhQAe2x5CRTG33hWps0Kp4cHCi1mWDrGdqWDoi/eVBJRZ5'
        b'kr1RqwiaOkk3etuomTk94RqkLdEG+2m1Vfl8pq3GYAWRK/lVvAg3upM/Um21eQL3WCmbtVDLQOngBvU2GgpKaFErrJjvYLnZTY1cqIYtnAKZ7PHZRLg9QOTF/arOEU3G'
        b'2C6dD3mjGQflvtFQGW+kciC528f7KOnmX0dNg6RWUmEqXtL1txrKlHNZeJLVPE8NN6TuBolN3Fx2YQS2bPH0stGFFB1Bsk6cAWcwhdkp1rhNtYOjtpjhSARtWrIjkvF4'
        b'EHixocU/2tPO2m2VZQfEWwLmM/WXSB2L5Zhuj1dVUISHPaWCHtZLfIlcXcFCEbF1nps36W12C7mOdWSrMYZ0IiWQ9BuYeWV50jgGj0MRZCUuIlRhJV7ggaFnMSOEP7sT'
        b'8u3dSeaGkpWU/4a12XbM26myccecWBZ2esRHTzCD2gl4VJpgCs3MvCGD8t1weICnmutSB29KpJLFrPPXQhbZUj3xGhEmr/nKocpaVzDA6xIonz6A3TAZ2/CSykGJp+Zh'
        b'pgHpEx3BEHMkZDs948ryl2AjXMcSqKdFNFBiLWsAY2iVDiRCO2u7eSvwRkfILBaaiKTaaXPY4z4eLH76sK2D0tDahlowzK3wgrEUk8koS1dbCBaukTt4knzSE5WYRepv'
        b'Ilkbto1dkxAB/BC5kqryEbmwUEmmyTlmWoJkspVnYx2pNG12BmSpIwywDF4uheKJ2MBZVQ9MNfH0mRvehcBzGByQQUXCRDYsxB20CQaqHNyhxojcIggmutJ5ROWjzbMx'
        b'WkfugVcN7L3i4IobGZQqpSgMCZAtFSGdjTa85LoGD8BB+r2AbQI0rdnCkt24bxceN/LUQFTrkClXIHUxW81GlAjNM7Fol213HMbdkMEDkdM98ITK3UZJZCcoIEJ9gwjZ'
        b'cFSfDSXnRDg2TU4aNUtHEOUCEW8OdZDwlrDzgzVkQVDPDGarmwI3Wbqhpnies0lTiEY3vEEhmi8Dhxx1xVZ9OqEUcm6L4pYo0uN8mKZaExnX2gFPrMaMOC9SMkMskUDL'
        b'ADUbR/4qPVqdUSu87UXBYJIEiqBdl2WqA01WcgelzYIY0k2kzPqRkkg8jTW8f27CfjKsj222JV3j4M6hkE0hWxoSAsk87vrQQjIIcuAQyTzOh8pwF0Qs24TJvFhnpsOV'
        b'ZaFyJUmEtYgOFonYYAStLG8baFjiqTWdDcBc0vJ4Sb1U7YETeJaMfVpVKWbsGybCuaF4iKfbgm3Q5unlnoSV1DyvK8g9JHhhFRTx5aJtLbYtSKJdFO9FkR+MHaX6m2az'
        b'ppiOzSPhPKkWXQYEvCFANbQs5f16YCJRMyifAlGWoY0Ir+fFYVBsx7E3DztRq6rWiuoJx0Q44YvnWaqB2A7pTLqHgi1MvCdT8TIr6+g4vLwPLnh2s/26QB1Pt3ywCyno'
        b'EEwlZXUUBcP5Ego5irlsnzLBUmhQUbBUPk0xwwZOsaJbkCUXj7vGs8m20BEzVZhDVnKlIVTbYSNdva+Ru4aYyWywaTvLSX8JNGArWeDrNFd1VoiYOc2AxYbjjQWxjIp5'
        b'OdG3qTk10oY3Sg1eH2KKJ+mJDVmsSEcNENfDeRlr6JVwaJ6KkbZfgoNk3pRS88UFBe+jFGE9Ee0xw5pMEyzFfCggN5BlgTcLaczL00mZrT12QFOSjUTQg3yJM9ln97OV'
        b'SdcED6rwIPWP9aWWlww2SEwl0jA4Bae53TMFGrGVgnUn71AvHRRTHG/AYR6Dno37A0mfVOyjGxVZXdWroxVckk3yWM7SmEhtF/Ohlq/wTAc5QcYv2XPz1ZTdkJPAmh4P'
        b'YC1Zw2izGWIDGR5rIJ813BhrQ7rpeomKZYJkhWg/GAoYCBeeguap1K/UADOSaMdfxbMsi4GYL4WyMYs5QECJBRZ6qiHK3beSMQ6FZHGkjZsUQBbTZgGyOkyzZBrd4CO8'
        b'ERvC5InGBqRtR5M6pIgLSHXbmburAqs9VHjYXgyIFiQW4tiRNup9kHT9WcjZw0eSexy9hWzvVdLxUEL2QYaTkE6mLKfmWKDbCcMdDpKlj7qzRo3ToYfFDFyMjDlvO6W7'
        b'N1m7mfVfR5jpogtnXbewlh3qLYUMin3QzShdBJcY5C7UJCQxEGQ1inoXCHU/Sw3CbCBW6zv6ubPVaDkcMJKz2+zj2Oo7AOut8KoUzhmo95NhZBxem8r4vLUAFYyZmqxt'
        b'OWwSqEjXlqh8lCqsUc83VwlchKr1fDW7CY1wg1xmSzu1zZElKQeKA9YMcrFeGbuFXlGvKNOkBpZzmYSGRyENT9qSgsEFMnR6xchVDGHDKQRyIVVTBZbLAGzcjSlSOO8A'
        b'5aybVuDhCIqTHzujJ/78eDXduqeMqtV0M5TidfOhIlQOxzw2q/ZgpbccM+0ZtE0KG+76gmQ5XA/nk7kIzq4lq72HSJ6shwYZmZFYQp6lnT/AYwqtn6GHN9YNoS7v5GEL'
        b'SJFi+tjFnES9EW9CvTfWy5VkkxxKDy1b1rJsrYdDrsoHrzoSKYIt2Gab7UdKITN2DtuGB/sNwTo7Bwe6EBRPJpmejdrDLpCVGNvkZPCT7GoEiVIcuXsA56pMIUMuTeW1'
        b'U8edtJUBqxGfvJgrmzVxByvPuKioSZgut2f10R0pGQjpcIWVxwZqQhixDUW0LrG3oeOYzNlj68bwtScPLo1XOdpg7SCsdlPStadV4kbWqEKOcHJ4DdkUDpH9p87eh1sm'
        b'9ohYSPamAj6TjltYUJhjNcbxFXJBi3OMZ0U2QV18pqocPLBmU6KSzH8itkkkUDDFmVeuREXmYC6Z6Fx4dje1poubMTZJnckXB1gZDSCPSFYal25BSgH8qsUlAdjE8Q6v'
        b'+2KDp4O37vQYQbJDdFkKx1mbBEEFRWLP8RLh1Azm6g3Je1mCCzEdjjEb3SIopjZkDnHiD2eUA/47uLe6D7nOMS14BK5uPLP0syMffWoX6/3IZ59go8/ghjl4saFozpA7'
        b'KH6HBYcVlFAMEH6PPsP+0Cf3WYgWkqGilWgpsRSH6w0Vx0jM1CTlRqKJOE4yThxKPil0KDCxicRCQt/HSebLzMSRopXMhIEes7TpwZJoJg6VDievluS7kZKhEnNWCksj'
        b'K5IDxR+xk/aWrhl5xoo9zwGQDSWWEkOyPg+VabBJOFm6grxOICkMFyfo6os7h/RyEsPbqi9K1Yc3e8fJ0CnS1MOpbZAuZH2cDCULH1t2Phvqu0QkaxY0nyvSQGMfH6WM'
        b'vDBvcKVRN8iS+HUCi7v2X+Tm6u3qz0BKWFw0xyxZpgUaoSWMnyaoLZpKi/8bUCKkiaZrmyiajkZ6eBZBZSiZTKbGq5b+O+/6UjMzOkQF0cKFQ41YMdZ7QRy5TzBIZMDr'
        b'ZW6Yqba0Y+bMLsZ2ieCyRhcz9w7sEitvqH5XGfaPNCIN01d/Nuj02ZB8locZsc/G5LOJ+nvTTp/VqCMnDbSIIhZhgzohikg7IYpYZuuFTdAiigwLG65FFKEoJELYqDDF'
        b'n0AUGZ2tGzZRiydiHKETNiZsbK9IIhS7pDOSSITS+q4pA9RhRNKLw0MiEx449oAR6XT138AQmclDzycrJXdli3z9XO9KF05eSIZTArfMU2QLNW5I/DY6sJPoy3bx0RE+'
        b'ZvKAysl/ChZE/dDMPw/9ocmOxW9OUkN/dMB9SFmN4vcyPCE/V2/fAFeG/DGuG+qG/+LFfuFxXYPHndSAH4908yQtKIamRA+s+kpXi4vRtfBKgy5p0F7qmahp9xbrPa1+'
        b'Mu/ryqT4HLaS/UfhMnrQn/bkotXxYcdjc503qOjRbAeinze2sqPMeCIn1sgZwBcR/9dhMp7EbDgcucFjj0RFFZmC+7aUUdwt+HbcMxE2H3gGG0Z8Knx3YMjMtYJzhuyl'
        b'VU8rRSZ6hE81tw2QdXbjmQ9lfVByHtG4d7CIqr72evqroPvlTqtuU/Qvgm6Y61Ecpv62Ovr7TRfwjT6zfjTkjbMUeYPaTv9ryBsblbL3R+s+KvJGGKsJhRagTvz/SdgN'
        b'zax6COyGZiY99I6Zjwy70XVy9gW70deU7QcHo9eJ3Pv9fwL2onu4Fo8sCI6mQQE06qqPGCLtY71BqvaAyujSz2p4DLojccgLsivZ9B3u8zBcCk1J/gwyRWTE/0Ap/v8B'
        b'pdDMuF4wGejPo0BDdJ20jwgN0esE/h8wxJ8EhqA/PSNwdHwCEqnyhRl+UzW4BF1BCTAPs73UtLpq+9pkTLUVBWjHNDmWO6yI3D5hpI6Ksvwesd1jG/xp0KfvbYpY8/id'
        b'W6/d+setN269deuVW+/cas49ddT2n6NTrx4cW1p1UJnVdOd0yvjUquKrGZNSRxftnzJC2N9sPPXYciUHXw30ghxbPG7b2U02Dy5yI+v1zdR9VQMewKAD4GCSGj2gFLO4'
        b'Ffdw4J5OB6xQiyfUh6xYCG38mKsGGjDdE07Ha2PkIRMbmVXRBVqCOhycrw/sRGJ3frrG3fPfcXbVhs9PeJg0tISH0ev2Jpb8vxEnb/VIItbnI/sXsR41WD6FBcvH54kd'
        b'wl4vofILSZl4qHyPnLRx8mP62DR7iY3X7d+tN1Sv0xSTa6bZfCrm6XUT9ORU1IuQqwU9PSbo6RNBT48JevpM0NPbq99J0NvTm6DXf8R7Z832/4tw966wYWrpSR0DvpXs'
        b'NzQY938R8P+LgFf8LwL+fxHwD4+At+tTxooia39nerQ/FRDfz5LxfzMg/r8Wxi3tVYg05+amZVg31FMbwu2+WGICZ5Zx/LCZ5MXUE/O5L4W/G2b42vtCphr/y80Dsxk3'
        b'2UqKwKXPfO+JtJdlAM1w05KTqx0jslxVLwBjWI21EszSR+7IbOM6XIV1UzsQynbDmUR6zrBjFSNCxez+EMAklJOiDA5uNsBWT2hJZMy6F/CGF422y4TT6vhQTHez4/Eg'
        b'mM6JWd11hA0T9RdALRxhjPPTl83xZBJ0EqZ0CNE0kNYOc7y5U5ifXA+z1+5NpOKFOeQM1ZC8ugcuW2m/YiUNBPbw9oKqADe44ubtYO/uTRMo3OAogWvyyZDl5y+MhJMm'
        b'UXh9Og9bmGSpgkNQz4g6KE2H79pEev4COVgu7ZY4lDrQ4NbYyfE0nJXFl8uEIMjSg8JRYbzaN0Kw0J/eS29U91MAf4AktRKv82qvjdCD8gSo4qEf9XARWuTxJngDjpPW'
        b'lA4Q56yCizzi4oRjOA1zT5o5W0XjUtpFW2zCCuaSP5M6WQrJ6wznB3klxxsJkb9+Pl+meplcSZ86L/DIVWNwMnN9cdu9J9wV6zwqgnKm2s2P04kfl3KywGdRybnwA2Gm'
        b'E9yzrYv316WnbPqq7evf/xjvv8TglnVLSXLgV6ve/cAyf/H++GPS3JLXjN5u812W/YGNk8FLQ99d9oGQeGk3PrF44bOfLZC9POKXvKc8zV742WxiUsULtbO/HxKxYfrq'
        b'r27ef/Pa2Jpgbwv9Kz94BvzrVpO56oU5d1b+tvuTdf98+1r8ndOfDf74ow0vPjUvTrXj/W255x1jLkc3v5t3eneBv2vmH1v+tsxj1jPOc5Ln7BEOXPOI++0ZJQ8UxHKo'
        b'2eLpYI+VWN6VMLplGbthITbjTU18KJRuVIOcSfCYdC4/DL65c5znJBsNwBlewQPsIDsiGlrVoZtumGOvJcCWYQG7Pmi4QZfAzc3QyPUaQ5EdGa+ESmhUDxe4NM9Owzg8'
        b'Zx/LNnoEVngGk1mn0ZiUSu7SdHy1A49JVUFVh5vbmm3Mh5RUpQiL5cNCqPttL863cBmzmdY2FlrgDCv+VrhIXUwwg+Rjgi1Sr/l4hHODE8UvA7PsPaAE6zWkx1iD+9XO'
        b'rngS2jxNJ0/2oEtADdEW8TweY343y/dwr8gwLNWaq8fGc6e3VDgD1bYe3nxhIMUfOBHyh0vxxB6Nz1Yd5kNlh0K6DeslTtgCpcxHRgHFZh2Rm7Y+eNawW+TmLqjsqWvJ'
        b'/4NBkx4P0yNjWeikVJ9R9urr6jIoNgs15a8howqmYZUmEnp956juWlPvMY8GjxLz2KFt6vR9/qrXN2NuL6GNro+kct5UdFY5H1al/0J047qHRjf2pqn96dBGivLdM7Rx'
        b'rCa0EbIn9RHb2EdcI54y1YY2Jsezo+lQvAKtHbGNUCuELJojdcMKuTAGL0vJTlwCxXylL4P8hTSCUQrZGuQDbHbmUVZFmGPDnr8GZ2Q8cDHagG0CVWMlgpsDHSVBXvPm'
        b'2Qk8VjJvM57riE0UDLAU2vHITk6RdWmDigcmQtFqwTFiJM/+jAPeVFGfBLLLQiuUQwacw2tMRFkqg1RNZCKRD8jasH8UD3TCS95YrwlLtJ1PAxPhXDh7SBdzjLVRiaPx'
        b'LByR4QkOAJpFpJH6jshEkooNXsbTcTzJy9gg10QSikSgKbaJx3Ie3UbkASjWRAsOIeXrCBjEc5jKGuSI6REhRZgrEZyCfB7Xj+HBcv/yGCukSLNoK435h4cL/9I5yk04'
        b'HagQhaCgzS/F6f57AYN/LsisWa9rrGDEKm85J0ixI4tpnLs3ZtrhUTXNEubRsD7u/aeERulkIsZ4kraoU8lJ4y3CdNMh2B4wch2rlG+4kfDPSCK7LQuKem6wHq+pu/5g'
        b'4ec5Gyio6u7ErVYCC740IKmeY8Gc6jhBL3dtpKDfWt7xWLtHGw4oGmPT7J1wlKWYN0hPeM9/FE3RaNy66YI6dm+9DrLIPRpFIWPOvdsd/3KzpvzpZpXqdzQrYz7InyVq'
        b'Q/dEyI+fOWwTj3FtJlNSE7dHWiEdimdDIx9/B4ZsYMF7Iyz11LF7iWQeUHfRnbPgBovbw/IR5CUVS9kTA51Gyq1tFLjfVhu454sX2VAPWZSojdmDmt3qsL1L0BLZ/v3f'
        b'ZaoTpABP/vpLYsDf4i2Wml25uD5iyavmIUdfSve+N/tY+OFvJNuPinXP3AsZGPTYsS8tV5jaj0qozIl1mvDWBMnZ9uRPf8xwjIsdN3PAyZmq926/7Fi3Wf9vKab/KHTc'
        b'ELEy8I1Lz/7ucu+ZX/71bsqxETt8Pw628ywPHD/l/d2mbVMnOz9+59W5ta8s+Pgjv3PT76t0nvr6mfaUo5+deusNneYV7iPqZZMlA8PefyvI4VmzFZcWPzkppK5W3/Ks'
        b'y0kzV6cr10qqCn/wCEv8sPjBjWdc3tONxZ8rxHsnau/dmldS+8xrH7zjAV+8mjjyePDH//o+Nbp+w+elhltyFn+n++1HzZGfH4QlhsXWT6z49Jmp1rr7xkcNipr/4b7h'
        b'ZxpM3ou5NGIkPHYl6Yf8oEM7LD4aetzZq7jQtN6y6Ytnf2h+8fXo5GxFaGhrVZ5LtEPAwpY7IZ/G7FNF2e46+1bEUcud/9jz+tlp/i/MG/72C6XWSatSTv7L1bnm8Xth'
        b'EYOLPjq2IOr6qfxrtTsLX/vDYopfzUu2f1ROqdso2RigMygx3DFq1D1pxJJIvdaNhfeWfr9o8dNm524fCfo12y5g57B3nq6VNi6peUW67SvDqF8nLX366MqgQpubabcP'
        b'Tv94+/K9rzyp2jO/7JWh3yt+enXbN1Nuljz94tufmyTW3fjKSbU0aMOd+5cKLmWfritdaO8yadqnnt7zXihpiin59viIqrSIwPfLB5z5wibr2jtNc+0nP3X5ufWvosev'
        b'hj9Oi5LcnuHy6vLtTxvW7Cn6e+VLUsfiYNeXNr1eHzCoMvPIuc/f/Fm27+mEL0b/8M24exb3pp7N/zbp2yH/+mN12gv2r7y04xVV6gn9ryQf78i84/rKoOC54y8OcWz9'
        b'5fju9XuvSe+Nnzv2uZ8/Uzz4+vn2aYZ7T/ncmjxTp/1mqs+ZrD8+sah4a3f++dCR4+v/D2/fARfVlf3/plCHJs2OiIp0FETE3kBgaEpRsQAKKEofsFd6BxFBEERQQJpS'
        b'BVExe47pJmv6xsTEFNPrbvqm/G8ZBlDjJtn9/+InwH3vvtvLad9zXLee/tDvyUOGZHT3ntuaX/7RP/zNklIWDP19uqSo8sfios+rSZ5/FqQu9JkfHd1Z5Lg79ebN83ck'
        b'/16bZ153J+xg3ynboivq0dIXPk3ZlXFnsMk3SPqx+OrEjlMdGzq+/PHaOuwds/np3o+2lty62vft/N2rDs0aY3turI92m+7HgSbL/r37zJTC4J3dpYafXP33Pu83D86a'
        b'8RU895Hws39HbV1d2B6TpC9SY6d85PKvN591v3jyy59f//6tytXfJOT8pJGyba4d3Pg286sXC8pvfZo0DVI8E6zguw6zj3cIP+m9NPv5X01u/u2LmrN7ki9MzF614Pvt'
        b'hyc/vttg5lT3ot2D6b9UnqluvbH3hZM/jo3p/7R151rrhBTKRU+nPpQoBA5OQ+3D6HDvCdzKvtaVuV4mO7xkRHhrwhmc5tRy0zRovM/PibmUXOnVm/X3cP7m1I4FSvhb'
        b'GTWLVkHg1AgbwtQzGYaE1B8GrilRa1CWrAttMxnFrU1O32Mq2Brk6zDkGl7T4ga5J7BvkRK1BsWQNRK5loNXU2gsatKiYy5K5Jq1N7mNbKhFsRK6tgAy1K1ToBv6VnAC'
        b'vzgOT6jga5imTxFshKzpYm8dcBB7VEg1KHbgYLUeBY/N1xqEdXI7K1M46zmMVnPYx0bTEYsgjYINqDlv5zBazQ0q2WgmY9ehIaTa+m0jsWpwcg1jalygwVuFVRPhNUKD'
        b'NGNVLGvYeJcU+jFhhsqxU4VVOwrVfJirAnePwqphF5QyvJokZW00K0ALyscPAdUI6zjAwGrQq0TSQR90YjUDrDGwGhQaDeHV8AjWsBIWTNtD8WoMrHbIdgiuZo9HWPeC'
        b'qUpOCVXL0BmJVpsE/YwvmzZnvcxBbk9hZSq02QErpQ+kNOwYQpph61aygDtTeMMycFBvNNTMCs9StJmEEFqL2bSMJSs2a0ToSPJ1H6bv0eWcYgt0RMv87HWsyd/n4tTg'
        b'rAgvmC/jqMoz2L1wCIfCfBEMQ1G61Fi3EuOnyv2UGDYH75EoNqydqnSBhDnzOIjNA0+qcGxQ7806sGypv8zbflaiTxIlxzHXmkPZzKRS6BwHNdymnfStlCPWNq4bxqzB'
        b'CRnbZTpucJkh1hZg/UjQGqEnq9nI2jnGqIANoiS4CEWEAL/E4WGXgsgkD0HWXNeQqS+DXm4Lf9UBq4ddrWGPkplfB6Xs0w3i3cOQNVEA9kF9LFlvDO92FrKxedh7El60'
        b'5aA1CeHBWdktZtBKQWsUsbY4dQizRk6CEj5oZdiFdaRTh7HBexi4dgqvcbDGiTiolzlYj1fYDEPXoA3zOPT2mA1kc9gaOQM6R0DXYMCP7xZyWAzB1kKhgSPXSOmDvPXX'
        b'9+O5YeAaHqe+BSl4DbpS2eexG7FWPsLvUyYcgQG8DlfYuCR7mw9j10TYPYmMxqUDbLHtlPjLuVc5sgIrldA1czN+8JwgO72OwUzmQ6UKaRI6h8EltKBLqsKtYZonXNjJ'
        b'sVY4CJV4dQR2TUTOy0sTsUbBz/B0ciqeHBmOdTJkk54WkE3HgB35QYcYgduB2ZzATYE01h4nzFvEkGsLsWKEZGqaBdtT2mSGOjgmxnHuRCWWhhyj7IJhTjyLR2HXVMC1'
        b'eTJS3LkUpsLXs6VRjItUwDU4qj2MXYNKyGEN2aMN9cPANcM4Bl2DJmhmHVi8gbrpyvMhreW+wPAK1HLESyZWrlNh10iqj+LXxiWzSTJdCmfoO3J69agr4WsbHPiQ5UH+'
        b'vhHwNRH0kLacxjps4gCs09NFFL0msfNWgddMoYAbJdRPwBMMSkPvzRxyW1zxxV7S7HHYIbXdCuW8hDbyMpvQ2MamwyS2YSTfkCe1YJCiOObBJaXD/mq8yNblamjykbFy'
        b'SZn0MM0mhyyUiqHNgSPKQrF3nUwJw4HrcJ6wrxYHjfgy6SAjVmurRNomKwFzUEPWLONE0wIWK6y9yVo5Su9HLRVibvICKRzbbsUmYpJ3ogoshxfwFAfMbSDHAT0sU+k2'
        b'UCKKyUxBFrQO4eU0oEx5gVXaM8AcNsJVEYPMQQcM8ha0B0LZCMycCi83zRJqFVDMdgG075o8hJgj37bA2dXzOKFxbMl4JbgNzkH5CIDb1j1sUgO2w3km+IeGLY4j4G1Y'
        b'kJRirWTFw4axbaT1BQ/i2+ASpLPSjMesUXBKgowUlOBVQTDANEnKYexl2E0s9wqlS1ZurYV51l5webzyxh8PR6WrsIocY7TVtpBHdwbdXeVw0pp1WQOrxcvWQAfvVvlB'
        b'SFci2jALzgyj2qbv4Bd7OxSRpg+J9fE4HFEKavECnOUww6tB1IEnH7XFoohIaN1CtipdFCbkxGlTkHr9ybIqtrU2OCwWDPZKDnib8EO6jByBZbZkLS7Dc4REo6IJrBTv'
        b'94Q8dnWtJPuyX0Edy+ZSeS7toQ8Ui4QxJpKDQG4/ivjAy3DFbSTYjxRaPgrwNwruhxfD+c17gprgjIDLQakhQ8xJ4JyeCb8D+mPwCMf5OuKxKUr4rDshDOixMEU2WQXT'
        b'FsE5LIFCN0f2XfBYaGSfYTteV0GEJeQ8pPKtaDLQp20fbN94yFHi+TDLmDUxwRRqR0ASMRfaGSxRAmeDlVtCH9ITyZaThNs8COgbN5O1cxMMbFXh+UQWuwmpUmLMQbQF'
        b'0HCQAvo0yAXdqcLz4ZVFnG7JwFx9FZ5PBGeAkPO6WzhR1B3sqMLzDYP5LpJNm4ONmkyCvwIbgpRgPqghyyUzcCy//GpCKahfBegzhGKK6ZNAnljEx72MkDvDmD5RANSR'
        b'dXAKz7IdqrFbU+btSwa8UcJAfTTaOtsSB7ERSxU+Q5g+6N48EtaHFyGLdysHa5yUuD6swTqG7euKZCPiMTWcIfvICV/jN4zsw6qJ/NP+xPEKRxu9/dihAvZFEeKavjtk'
        b'jFdUkL6NCxmoTxtPckzecTy6cwSobwjQtw0rDQndmckvhfq1cELh4M0wfdhxSAnrg+OQzWiOIHLRFgyB+uBI/Ahc30w3Nm6HyIReHYnqExngWQ9sncSQu5smLJQ7+OLF'
        b'yeoM0xdLiqXtNhl7iArNoDRYPozbm2lgrfd/j9NjcCymYhA/CqTH/40fguoZSH4PpKepAukZkn/GLC6MAUlTgN5/AOdJNJVAOikDzo3TvB+mZ8iAecYshx6F+0nHiUxF'
        b'UrHHfwXPGzcanmd6vx7hf4vNy9FQgkIeqdo4Ivw0CqH3O40itVM0QnL3EDxPQn88FJmXfJpm/KOgPKP/SzxeLan7HQpZXCP8dTyepsRAXYm/sxzC3xmS1LilzB0z4aD7'
        b'CWsySni9yQrz7ESCFVxXiyN0auMoa1o95W9F2gPQu1BpmUaZVplRtJj+LNNT/m2s/K3Nf8dIoiWRkkJxpI1Kv0SD5Ohk62brZRuw4Nk6FMLHIG9qUeqR6pEaGQINGl4o'
        b'DtUgaW2WlrG0JknrsLQuS2uRtB5L67O0NkkbsPQYlpaRtCFLG7G0Dkkbs7QJS+uStClLj2VpPZIex9LjWVqfpCew9ESWNiDpSSw9maXHkLQZS09haUOSNmfpqSxtRNIW'
        b'LD2NpY2z1aJFSiCfCfubBiHXDDVlppMSpnvTzJaRsdEnYzOGjY1VpDXJMTZSzGTstrd1VizzDVqpVKK9c0l8n9kktVsamYNj/lRWNykJNFKEgudxcbLjv51ZXAX615xR'
        b'hQ3p6hQO5stGGAQq7dsYukBpRUfepkQls7APCbto3NuU0QZ9I0NA2JlHRWzdbp4clZgcpYiKH1HECItDaqQ6qoTfM+kZrTEclfBLoJZcXtHmLOCrwnx3VHKUuSJ1S1wM'
        b's02KiR8B2mDGUuR1BPk/ZXty1OjK46JStidEMjt20uaE2F1RTLeZSk+f2L3U6GpUjAtz9xhmv2S1zFppehs72qqLGj8p7QL5RDgq52FoxO3MrZZbD2WLMFdEUfu0lKhH'
        b'TRKdQ6sV1hTpETHCBlBpfZeQHLMtJj4ilkIOlOBmMgQUTnFfRxWKiG0MbBLFY3mQXLz35pFRieS4VZgn8IYzQz4r5bvldIXFJShG23NtTYiLoybGbO3dZzToZy2+LdkT'
        b'F3tbfWtEXIrLnK0S5VGjpjx2mOKJOvZUQsc0socibMnY8SEiB4g4Wk+pqJbkqKcLB6X71A9ImKJayhTVkkPSETbGP4n+AJhs1Ob5fXOx37MgJD3ixoPrfH2U1m8smAor'
        b'd3iuyKwwC1GyFR9uVmoVxZfQ7+3TR4Cc2HDOp1iVrRFkp4eTJoVzKz5emKqQkcvtd0LcRERGxnCbT2W9o5YbXZhJqVHKLatIJXtJdWQ8HNwxyjKWR66hOy4iNSUhLiIl'
        b'ZitboHFRydtGxKX5HZhIMtmJiQnxkXSE+T5+dJwZ1b2mq1xkow0JJvspKKl74dfe7he+D06xtW5JsX7a+lK+9atdRxVCzEHNhgEJs7VPpT8IN4vl0I3HsC8IM5kPdUL7'
        b'WxMeOt+avOgC/g00QI6CUZlBTCdpF4Sd0BquQao/JBwifEUH088aHuAei+9axvhMnyMVWN4p5KrOh+4leI2c8QuEBa4asT/89ttvIcZSGmnG3Nw2ys4ybr/AIzFUYqmM'
        b'u2Muc54lFtTcdBeKAsJpbAV27yculikwTw/6IzB3N9cVEOZQy8ZKJDhhmbotYWRzuKPhRhPol9nAaTfySuwrcsVmrCGFUPEPtE4wpqUMFaGtg5X0t0iwmK9mgTncbXIi'
        b'6fM1GX8u8d+PA9TrXLoWKcOOlY85ASMLSfayIRwwdtp6yR1EeIYqLULwpOYkSI/g5nZt06ljKPqavtN0EQdox+v5WEuYq1XCozRtkevPIMy3PR5znuUiFnQOineuxypm'
        b'WbED0vfIUz1Vb9UFnUPi2ANTUinTo04Yu1q5BC6rXosEncPiOEizTKWKFZlvAo8N4hnkCZnQR7Ot9hzpQnClvsbYna6plCkNgooFhP/TgUqyDFbbEzqKcn9GUCSBWixS'
        b'T11F8nhQH0EjbVSssBiuQyULrIK5PnK5vThpEdRMwmuQZ4Jd2CU3hjy5TBu7IN97TaAQFW3gar+drZiXFXwVHHGKjl2kM0ZI3UgeumAFpJMK8Cy2jKzEjgfMKXT0DrbC'
        b'XE8sCKQGkfJg7FAtXGYiQ9h3wxnamAkNamp42X0GNFsL7ruNsUaKWWTAmQDv2mHSsG79xGSyPA4TlrtfZBk5lr0yxqOQJdOk+H8JDkCVVGSD57bzSczXcMRunST6EZzH'
        b'fmwTTXfGbr7izuDJjYpE6mKMepw+pSMKFwL4mw7JSkUSdhFqVjxOhkdE030hbciT8ZVAyFXgJVbkmMNwVWQag5msskNQun6oMqw+QOuC63iSzTn2jcUyuSm03D/nOdGp'
        b'NMQnXN8O/SOjwvjae/sHe5JNUKn6QjmiVBwoYG2sDM5DA5Yyg9K1OIBHH/g8wD5E+clVrBewVIjEfk3qdKgjZtrJBKmiiOzvCuOwuOPPxr+01DjrQ9MniyZ/f3puQ9kC'
        b'+74Xk702GG7PHNgSrJUbu/ROgdjnnE1SV8etm+ry7QPNPwt2n1WEH133ldC2rnP5QvGzDm7OqSsuxz7x4c8fLlEMjn/j9gvBvkaGz33qnTXvg5VrFfsC7ujH+bkteN7l'
        b'o6tlBpnTX/zVrNyzpCB55pNXN64yuGywNzVw6+2xdrb3Znbi6tcK31rXe9PWTc/n8XcW6+85kf1lM3ztnOvsumrBR4+/9+HKMe4zMmcGNtTNPBb5WMXtX/Omu5kdKL3x'
        b'2cE1gU95ZD3/uvsvPYVZi6fIv9qwYvz5Lrv8Fs26rT7zs0IK3oitf8rS/eS7b6Uc8339ds93Z3Z6ZGhltal/3ZYaN+XKD/12rxj0F+6+8FEbDv7r1VfcGqqtG+0Lerq3'
        b'rK7uHsQlPf96dXfEuU3GFW3Je89t7PwxeHNWqnVRg+T7VwIvpDw3/Z7XxZO/Ta7fcmHdRy8ar1qS/ewBeNPzqs4XO2/1nbcZsLN9d1/aj5EVRz/UXBj4xPF3f1098a0x'
        b'K7ZoLbzr/9V8i+0JWja1b3jOn/Wb+pu3Zr/mmyTP+OANIfXxltPBCcUvv/LDpnc2pT997J8Njl/kXHnXbF7jFT/ves9pt77Iv9V2oLEoNkzSlfrVywPShVPsV6fvP5XV'
        b'INq2wevpuxo+3zye9Y+M48ffcp2Y8POt/R+87m798aq4G8+5vpajn63fs8Hgwox5f/vtq5ti/cKnDu+tatqz/Zsb/5wjO235VVtjyq0Fj6/Yf/HXd9ermd2eqeb/r971'
        b'G6oa7Koyfs1en/n3e+O+ez6reM+dq7LPtzfWje3Rr4ra4DY//N8urQPzPzIIHH/ghc9mLA7/uig68XS59pzyZWnB5ukvnI49Ev73vc6Pn5+8ZsV3+lpLY4523XGKDNN9'
        b'PfD91EOilz8wzNnoYr2Mm9+2uWOarcMSY18x3bci+QxNLs0uw5OTyN1E/ckWkvMM88SCDK6qYZ8Y2/C0L5dmk9N1mq2XCNJ8NMjXOaJFi0K4Hrl8NZ5nKu9zEcPOWhdr'
        b'sJdSKEqBfEdyZZwk7zzVBPVwsYUA1exlgCUU0VBGjnsx259aqB4S20A61KRQc/TNY83Ih1RF6uMAuf5M2Qs5jp52NhTtqbtCriGEkQu53RMaufS5CUogQ45VHvd7sHVc'
        b'zURaLlOhn8m7SuACFtqrC+qbxdPIV9VMZBaOtXBF7m/vZUdVjzLowcs7qDY7TSkyIxk7l9IIZa2Goy0INtsBd0tmjLWrqJXyYiwaEWGGWimHLuAD1QkXNjBvXkMSP+gZ'
        b'67lmLtey9GJ6KBX6zXEY9uS1ZD53WDER6my9oJ1c4VLM37FNhFkrApkGx5nMz3EqsB4lD4zH3AlYLU3Cfj2lV1qoxhNUqQUnIFPpTNIkmmm/4uPgHBlnb1+5PbV388Oj'
        b'wcpSpuMJtQVkBGrYGtm1BrsUWOhFJ0Su52ePPb5yuVgw85AS+uAStvNBqsOTNtTPb7IXFmvRTCSLrruYkCO5M1l1aoSYqiT1+dnb+dLqaF14GgpIfeazpdiwFAe5Bqh+'
        b'HlYMSTCp+HIZVIrJOq2OY3O5FxqsyIJtU/d38Pa18/IVCXrbJfM2YR2bSwvoxAGFI+YwAa5ScqvrItHwV2ohz9rrMCl/AbTgGTnmawjqWmKdKMhkK30H9sF5BRO2Sxbg'
        b'2Z2iA8s3sAm0gFJfle4Sq+EsDIomYj+3adhG1lWlShFHI3FTZdzpoGhWpRTOHWDKpM2QwZSbalglIrfLOTlXe5w0nClzkDMhdasltoigFmp1mCgargbvZ8pJDSx7QD+J'
        b'FVgdrtTzTZimIFd5L1anDKkIEyCfvTOG7jlUfSiBJpVnzH3QzL/rmbyTapLyfNQFyfpJeEoERYexhAvPL0ioTtQRi21pw05JsVsETVC6UVmjFaEXqNIZsrCE+5CF88Fs'
        b'pIKwxYYZyiRhC9OXqOGAWLRRj3XWCbNCFRSbkgNKM0VshhIu3W6FdEJE5ftDmvMIP6SGtCX52lDBFQbleEoZSV2pHIMqusQyIZfQaf1sY0wxjJeNttvHUvNh0/0MC9ZB'
        b'a3KoXSbEKNd/byCbvlcEFwygnaurzkEbNaog37aqCCt1QS9S4g5tcSmU/N26aznk796FPbpJw3QgxXY7YpGnrz2U4CnyRaC7pt6+9WzQ/OzwlMJWm1DL1iJB46CYNLph'
        b'Tuh6rkPJhUaoV9gm8zWvEUVtDK45bYAs3u3aREwjvfbajBepqsefRfVTE0ywRTrGaQwbd0IdEcqKFM5LgBbxdIdFWMS1qhupB998S+ygnoShkKxUDUHPT7I0ZQc/4M8H'
        b'4XWF9zh3aiwkwj6RgXsIuzbssQMHZNYkw1ruTXGfE9vtY32wX+EHtRGj/ClKIA+ylEYXUOaMpQo/ERnxSqXfZaxfxVQIUxIsFNRs241iQYxF03y02fngxCys/MkW8SK7'
        b'lh0PGkhOfSyUCNOwUc3VaRbrS+CGeaTqYzrWSvsouUgwmCxZHTekRuwha7FFYS2Cwd1Kh8qQa85fnV6zRsHHR4K9pLZM0b6V3ExgEgyQ+zFoi7e93N7Gjxwq+tskEWuh'
        b'luna4pfrDDeMLNh2riIjt5efmmC9WQ1O2WEju7mwBtqh8751MYYcNXxp+M8lROoCuKDutyyBH0cno6B5yOKHnEklDORBOKsWNszuhC09LoNmaAqz8xy6V8bggATa16hx'
        b'1ecxUt1RW6b8JfeaJl4h2wHr4FjqCrZyZuFxitSyh2rIuE9tZIiFE6x1/3vB9/9IxfMwXwM95Md/UOAcFqK0RQZiighRF00S6VBkiJiJzylqhClF1JlyRF2syf7SI7n0'
        b'RGYiS5GVyFBswJ5pkmdU1G5A3kwgT0xFpuSNIfmtJ6JKIDNSmjoTv496IqL/9NiXFI/CS6JqnH0mI0VP97s9UOMKlAGqoLgyGm+i81/NhIQXN1y6ajS9qH02dWn7H3Q0'
        b'R4TLliO1NA/vx390ebDtD7k8aCdfcJcHo6tR+TuYPSQBZyJkO/OobQ7mNlQm5jDLxXnIu8vD3B/80QYGP7qBHUMN/GkibYlSoGoeEzmqzv9YWTSr7LZm2FYuZX9Ejd2q'
        b'Gqcy1DKD6kabsw8p9v5P1cs7eVs3TCVBDot5VOWXVJVbLjNPjY9JSo16CED/L/RcJ2xItvjoBlxWNcCG9l6RQrrP5JMq0eRfacR2PtfvCI+c66uquh0CE6g/ofjoBObi'
        b'wDxiS0Jqyij3RH+p/kWPrv/66LU2wl3OXxjx5KWPrgxUlU0Yrmy514q/sr6Slz+6rsdVddnSuuIjht09DXnH4O4B/tKoRj268qdUlVsFPcQZ0lAD/sqi1mbeBcIo1v8R'
        b'DXh29LQyFwF8W/+1I4TVmZLwiBqfV9U4XulM4i/UlzF0dGyJiKVKk7CExKj4R1T6gqrSebRSmpvL8mNHKgHv9z3yl9qkp2rT1tgERdQjGvXy6EbR7H+5Uf+NB8zt93vA'
        b'FAn3aywkfjHf1L0hVVCWf6HPog8+pd4sNaPv3hQEzTxR3/um1iIeSZewl4z5mYD1Kv6HMg94/ne8WOoPGcNQ3cF/pKUOC9v2Gd9358dGxYeF/XEflrTC1yi5QaWo/5Hc'
        b'OCK0jvJk+dDK///4IX1wFqR+QTHO6ifVFPTxefHL8gid6Ls+kn+FC9KZIqu4LcOL7MFxrhX+3DjveIC22pKQEPtnBprWePtPDPR5nUdRdrx21UjT2qjmli46rrkddvs5'
        b'5COKa29F2boqza04R43MgYTMgZjNgYTNgfiQ5GFzQFlBHfK/86g5mMKdc8DAvmVMYeBnQGX/R0TTLfEKU5q94CUVzk0dIwhLw3VmHjBV4m674CyUKfSStaAVLtMv6kUO'
        b'WG7EFCwvbVQjzKkx/cKuZ9pcgTuMKFy5hMlUOGif+qogvF2ujx/1f7EmYI19iFjYvBQr9mpAHdlrZ5nuzQ0vesi9qU4AioblZlCAnWqCzVY1UvfAKg5zPCHGFqYJWYhl'
        b'VBkiCj8ILVxv0W+2SOXZg1n3ukAGjV9xyYp1RScauqjMR475qXBVQ5Dai6AdS0y49qVbH9ooIhivJXNQ8FHMgRweq/AiFOrYcgaW8vH62+bDaUkUtqwN4mNUFWPOGEV7'
        b'MoJaGpvoyVG0A6/ylwNwBdOZaW4/tJCipVQOdTSFR6c0TqHoKWvCYGq5bYejFExTsYA36DK2rWdYn/VRDO1DmNVm7OGazC7oXEOBNZegxI+xneqbxCaheDGVhY8+Alej'
        b'5FjkRX34+WA+G3kqFoiDoxLBdpEaFpLOpY9akbKhFblyeEWOXo8ilaeyobWozdfiWrK8HliPo05m2lOtB9ajgx9bdaeXSgVNY3O6hmIznRcIXGVZgBWQpsBTcEmFWoEi'
        b'7IJ0NqY0etdlhRemD9v3FmIGdLNlYITVcHLkbOFx9W2SKEiDHrYBsB4KoEuxGbu5NHKn6MAGJ741WjAzRkHjghCOFo7FTsZaGOCatLx52MMC5FCAARTNd8Qz2JaqBG2U'
        b'kLnKN4fKkUHWZ6vzwKB16yGTLOqaWSqYDNRPJaUyEcMlLF/GIDKV+0bGdYKC6UwdnmpAM5WPm0YvbGgMmypMddewVmPfrsZivMS+rSW1j/h4MQe/z4V6uCCXy0bGJl8M'
        b'R1OpUD2CjFXJqKBOCXCKgmN04QRHzlc4wBmKJ/IVFg4hbw5BLlPi7oJrWG5LanQgm8XB2t7bVyRYQKYa9ECzm5shG5MgPAYnqBeM3qkjAjTZ4Bk2mC6bvOeOV9pNk5Wr'
        b'KR6LA1jBfAu4QDm03m97DbWzhmOp4LnVLOdOKV5hlvo+VOQsp2cL5GG+DdsNlmvVdkIudrLzCMonJ1GFyOhIMzrM/c6w7bkfHNXAErLClCr+83BtmiLSYUjlKgqHxhmp'
        b'k/nSvDp26JhJhabhMDk5eIWdZYvnQ56cEA5ZD5xnyrNsOvbyo6EVm7dgvst6diYpDyRDLGdAb7+9UCCHhi1DWAc4O86LN+0iVqtj/rTpQ/b80HrIn5Vnin1TsSCOHAzD'
        b'hwKcxgvspSY5bU+R5vStGIIPkuPkGhxjZe5yhPOYrwVN5CvRPAGLsAEHmTOhYOuJtli9jwUhkkaQU3HxKr52r5F29JMF6GlvBz0KhgwtFx8gW6iUQfHN1u8ZgpqMsnqH'
        b'YqlWsAVbJZrRUETy7MTyEQGcoBfOsFHEminb5di+/iHnmPIQS9puLWatN8cBa8jHrl1SQYTnhSA/bJptyG+LWjzuodhO48+q060qQAmcWMmj1qaFeZKTgZ78hOCx88F0'
        b'dqVJ42WCccBGqWAQrvPJ7njubGDTLjJgG9NI5nCdzR72/OHgCtJnn1dE5ODyOWWbyB+uttYVxnnelFBfBQnzIvnDCa5agoFmhboQHq5jPc15tFcGRtrQ/5moWdikd1B0'
        b'QJSoEymEkBM1SRw5xJJx8kUZs1m06z6y/Cethdui4qP2JCYvjtJSegyQcoMHzIVLcERxnzyd7FDmONXOyx7yyB8Voxwy4HEJdsNxQxoFRw6lzgZb5iK5fvZCs4ma+y4B'
        b'Tq42we4YKEil/ssPJYVRVT7Zh8ftHbwYDMV7dYB9iOcDUzeLOveCbrE2s+xv0QlPwSxmNZO6F0+TI9sa8mzsKfiK7Wm6JSYFS6ENs/fGxJQ8LijeI93ac8shKmhBwksB'
        b'xosHLxkteH6BX2hTw997fAOtAk63OH2gYT71hea0d1rcXc97vzRj+fchObu+Ev/zsZefPjbupMH1sxLJ9SO5zdeF2YlfdE4MnX/j18EvD3yY9GWn4evTbG9+a96167Ct'
        b'Zvu4J84U3HrHo1b3jWrrJ3yjzOb9EPmUjxYElM/pN3lstf74iWZyuVO8/zIBjMs7NC5etB7/8+vPlO86afL64HenSmcHeLlo1IxPHrDIvlz720sLI7b2xY6NT/nxULds'
        b'fs2N3NDNxrdSj3WJ3e949Zx3cprmfe6DgQ59mwW3Vza8mX6nPPnctM+eGmeX5HihYKpT1uDNJ4Lbi3QlP9Zdl0z96E1hVmtWqhOMnfv3J1NX6j5z6PFFNwIz3k5MKC4s'
        b'PHf7rr1G5b1M/YH9q/9+Q176gtf2HSkHLtfP6K6Y2X1qy77kt7yr4jY/+2uqu7yr9SPJmJzGk3/7YcoN52dOxN/Isv94i97gihXTPv5nqDDTLuXAwcW1/4wO9vvghv3n'
        b'E2PPhuqntPl1uq2pnZpQcnupy8wPmj81fkcNXsoY+/TBgoXmu5d+YthcW+LqFVc64LPXOWNDxjatiwaD7nfWPj7h3q/mbzY+Ncn91RN9F3c+N+1fK1fF5rzxw+QPohY7'
        b'Zbu1axyZ+NynhR/VFIU8narx/dtBmV6TEr58cUzlvk/Pmv409+ng6v681za+8UNcv9dnNzxnCklre4K9yrdvVnyl963a/E+XjzWctB4Txl3PDnthy5IVBd/8sDhswsSW'
        b'hVWyuPWLZ/+QPOWKzt+j3C4kO37+Y6pGZGXfrWsur56Y/1RIyaL+Zww1zu5eu2TtQMmrGz/vvjF2yY3DR7wH1n56fprt034zr/V+6eO86dPa0l3+P9U03OmzjLUXvoj5'
        b'8IV/Z2x6YnlF348/Wfu9hDtSwvZM0yicZbTk3Zr3F5fuH3cqa3BVY0uXjdlLi0LTFdA/7czu4BXfSN8ebIuoqH3xyU/Gdln+sijrx4l7xKZV+9f9drbuE8PIX+4Frj8s'
        b'Up80f8Fj77j1Nx0WvX1x0d1Be2s3HhQVz8J1uS5UkVsezkvZkX0V8rWUeG4XrJZRaJmWFSGuCQG5Ck+MgSYJVONxDtbbTvaNzMYau7DAEaopeGiiOAQvYRHTf0/ah9fJ'
        b'Hr+6WRUJcSOe4zrIC7bkAujGKudhROlEA67oScUj42wh85BScU615jbYxDXxVwNk2B0O1SNgk6f3w2CKkmJtJXRwvjqmjaSSfFdxZU135BrWlyQfR2t1QRe7jEgey3nQ'
        b'zPRX4YQ6OXYfllQTGofVtbWRrOEKOBLLAhIyVa0TuV6LCW3WyN5FQ95MVxgcFchwszJQKLm7r26UMbiOOEjkOXkxXFvOI4jmhJPMU/eqwnn6YBnrzpw50CKzcjCbNire'
        b'JmQsYHW5+mCbAgp3D0OA4WwCHuMeE+qwaJ7Cx3oKHCcTQ85EuZqgrSOGM+TYy2JDvE0Tz+yGbAZkt6MWeG1i50O2fBTLIecgDYWLhdARNeRdAK/rsFGcuwH7faHz/nib'
        b'xsCjBoZjm8veqFGROqFdCcuE4jBTzN+oxnwDkNmRuomgc1Msn9fLAZhJg4Ri5wocHIJar57CPpyh7ajAPC8v7CM0slwsaCSJbeZAAfvQCZssWPz3TmjVVkJc8Ty0cr3s'
        b'NcxPoIEKHcySuApYe60YBvCUK9e+ncR8K8jAXhk0JzIopxpUUZVn2yql4YwIKlmcQ6rohKb503xXsGUdExgkw5zN3r626oQxGCBkPLTsYSM/AxqCqAECZGO2loPcQZuS'
        b'QeOgV+oK9cFMvx2CV82V+DSOfsUMD4acK5TgcQqUZLmgGzrw5CicatISVWRHSAvmEVtDF3P4J+l9XegQqhMqeFheaNi2BIssR4eYW6fLVdKD2AvV90Us3ka2D3UEMZlH'
        b'/pXCCSzlkSmLoXxUZEoo3MqrIORogIzsgQ5loEjRMnKF5/H9dlyfnAPNcJKCmJk9iZq7CAsXYh8HIDeLnGUx0KUCJcL5nXCCjfvUQ/4K6MVmVchfPKnLxt1UiIAytyHo'
        b'MYUdW+MpXtnFFLJZlEH8sHqrEsVoiT3sQyxaEyOLCx6GMZ4OhD42EJqEc8oZAWJ0hxJVUEKs5sEFyS7KwDoaRJBiDbFxq9kYdz5LdIB66WwGYduDQQSNgzlgsIrMWAHW'
        b'Yv2IQIITuAbZHOughRkENycegAbSYw25eCrhEOpYu3XD6Ay4hqhQkFA/wYtvmBbdhZpQNTrO9kFyckxiM5dP4/za+blT+CZhXkgGMktivLB4JVum2tZYRt9DNaQRWgxz'
        b'mOPGC2I8a6rUw3sSiu4MZd8I8Qh1Im2sC4Cq1Ry62eEFtbb+dlIyvXlM1qEhyHBQjH1LTPlod0pjZDZYJKF2y1BgNQcboJLtOGcRXlKMsu0JgyYXiQZemMIvnHzpdm7O'
        b'po3XRlq0ick6mGpt+v8ZBXa/Rva/d5h4W5uiccKYVTwjwp+hJPl/li8eFow5fFHK4Iz0p57IkmnC7UQ2IjOmGadgQQpqFIu4LpuDB8XqOmIrkanISmwo0hONEzN9uDKa'
        b'If+tI57AAGlUt07zTCB/TRAZiGkcQw5yNBBNkkxgunFtks9cNIn8oyUZsNIY5FJM5ZH7rO/XMNPehjksZDopxWKH4d5z1kJ6WytlT2RUSkRMrOK2RljKni0RiqgRgtK/'
        b'EOWAsCuvUm35KyqV+cvkLwllUCji8A+IVo8Iv3HPjdrsZyr1benmgycewc7oQcUjOBrKzQhzsVLfDrsFawkXd/RMWyP3hp6kEUHaoTGe2/NX+q+XK+0kVbZRcC58Apyl'
        b'W7l1daoFP2zP7xrBUPkr3ehMWaA7RYplHjBIWFV2NlybbiD3xmNBI6oix/1J7tv4GDmJLjxYW2UCr+0wnE6lUmpPEztbasTVbuXp6+DluzqRDgaLzEEdF4iEcJOxOKA5'
        b'Hc5MZ8I0clNCuXyUMbeTlTgOLhsxSQo0bZopx0J7Qv8EsZLgpOdsl9Weyi7Mn64uLAxPZVF7iw3IWToiOAiv2GqEfGMjVJl5aOpjC5zlw5clJD10XNxCybjEYhoXGZ+F'
        b'Sixic+qxdER5wUp3w7Rn1JlS9GFNqCdEZAzY+YsV/WTZPjPFMirwSrzRMuOaiteufNp7zW/SzF1gezUsa0KDT6bB8uVgPE6+PbKuM2rSgsz8SkuP2w25l87mlvgu86op'
        b'tXB5e+nfNALcjY2rK1OPruze/1Tvh28q/r7o++fjLaOTQkMiayPrbXWe/uGzYsu8d29eua7je01tgyHOCd6o5aUR+0/PLv3InivL55XMXCPk6su6Ss7qOjWtMu5surHn'
        b'/Ov1VtdmvOKzb//03tBBw++s832dtlk3G73/8yKx3dLHZ64d05/3WN0737RO/9IvLuP0O0emBqaFaHl6uT9Wf/nxZ4o2XXrqh6Z8G+9xemZ9BV9fvjcnri9va0hw20qP'
        b'J03Gyu4GZ7/2ctWY0POpFXELlnT+y2iaY9DkFrVNT330frND+OGJkqwfGt57pfzlDx5rb++ZsOOl70RdH5RkfR375vTxNYdeMrP5OmhD0da3nztcX54/d+3iz9U3vhnW'
        b'PGNOhJb/yjWeadN9ntHysvkl4MKzP+1/23jT93HvNS1e+OW8zLdjzvziVhNo9Nj3mQW+l16sN1VUdSZt0lijk6G1yj58cOC8w+unljcWGlkEZc5f+Rz4afwW+/O4ymd3'
        b'TWnd2zk1+3rSDwPY2T3nxYDP3isqara+Z5bSvHvGvZg6/6hzkk2lE2du7C4uHxMTturanRc+rdZaq7Pp+pTNqTZzduv0FRqVr31s/Zx9538p8P274rnf3AIa/F55smIg'
        b'5npA7N3b7w68Gfqij8+i2E89nnhS195nfcXnPpUn93xl+m08hL18Re2buZbJbjcNv/3i/dkpX+gtfPbS6iKX3Oabgx/lDbw2c9cnB19cNDf4ZuDjF378RtOs6gvH5pZ/'
        b'zzvs0fiupcn42mqLN7peX40fzHj5zbVPxDm8p4Gvny4K2v91eO6SvjcOPe4Tu2PA8unHsl/Vv9y+9Yd3jjsH9bnE3+hy+ULUu23yP28OZk9Oc1jw/Ipv0gKSb31Skt6x'
        b'Yvpev7S+w6LnpYZZBsutZ6XY0+0xoC37HVtHR0L9UnNHpakj1k/iLED3Kuqticp7D8FFyl1Q60pnwoNR0sAVj22TM3ZxjLeSYQxFJc13dm4YIaaSIlaNMu7DC7PYl9r7'
        b'dzJraKhRV/J1OAgZjJTS9V0se5i7ZmzCXCledDNg9MP6HVBMyWsVab3bgBHXwdjBQ8wXjsNiOfdSnbxWtGwDdLLnawwThuh4qI4TTcPumcw0EBq2Qu8QQcI8SPVwdzR4'
        b'gnAhzVLocSedpjVr4LWNMhtb7v+LdIuQzkuMxJgOtTs547N3nEwO/eSrgiRrQmvvFmH1LsLrUnpoLbkqShXWu7BfpDRpHKt0IbWYEmoKpbM0aliqDfVQvltMKOquGKWt'
        b'LnaEM6tHaPJXI9xGpmjfARhgvXJagk2EZ1IXxGuhBptEC3SV9qBHUoIUfhaQPkQ/O+I1buWdje3kcO0eZRMLncYSdz04ymf+OvUcy3y42e0QuEokDUuhiRHLMdDyANMA'
        b'OZOgjDANO0kd9PKJxGvehOXA43tGcB178Dr3t3IUL87AfF8PPHK/GwzDsSvY9zGaKoKYUcMmCwk9XIWnU7jCoYPyxHAa2od5gAgeIRyLLaBGQYV/WLgWGwj3D80iKIZa'
        b'I1buZMwJoex9ITR7YQ9Z00DYgMpAd+5248TCOJmDb3IEnOJZUkjdY4wlO2LM+ewusKA8Ih8yTd3wceJIzIJ2Dl8oke0e9linLmhRL4bUYx1cOcDi0M+Gc1j+UESEH3Zz'
        b'UMQQJALyI1h7dMj6u0RX7BDbipcnU841DPvZNC07AKdIbTMnjGRbyX14hDMcJyAdjhN+xRavLB7iUM05be5iM5Hu3Vh+6zOngwXLOTPTDFXQdD+YJNqDEd9koo5wvqMa'
        b'szdhPqULoueQTewvwiOYjkfZSxc8hWXMHhavYN6Q0/M93IcQ9kOxA+FXLmDvfa4cN2P2HO7PKHMOdozgD5hXGUoJYdu4KKnFWKWQgbQuJ5Ka9PJ7XnPeNIV4y+4QVoQU'
        b'j/gPvRpB3kwZByVQI8WWDbps0pZuIHQQY4zJfFPHWdq2kO8jhpLt2M1PhiLo9yYFUYoGckdqV2aFkmPrmroRVK1nLp08diaOPl0Docv3AYthPOfJtmAk9k4ZJRTXEPRC'
        b'4QyUSmZPdmXe66F3Nl6X318vNtuqCTaYowY9i6CK7UYpo0dJWf6Ex3Og1ZGyJIZQK5lK+LoBtlC24qAn9UDZgie9VNAZqMJua8P/j3zT/8ptzEi3MLpDljD9f4yDiqNc'
        b'jCazHyb/iw1oXHbCu0ygkdopn0O4nXHMKQzlcAwZb6PJ+KtJErNkwgmRlLFkArMbHsc81oupdbCY/s9cv5AydWharCnRk+gw+2V1wnFRG2RWphr3c28okop5jZoSTfGD'
        b'FrmMX1LyRtw65NX/pU2xkjeyGTWMd/6E2UnDow2KWfOpZde4h0ZfNwmjwPutKZwFDKMoexpRl/l6Ya5fmMOXOPLjtobSvPa2zkh719uyEbanyRNobjf63Wb6g+JEWby4'
        b'21oqY77bGkobu9s6I43fbuuOMjtjZk7MBIcNCB9/k/876cKw4RElCVzpfGwhKU09qVgqthNZbmEeY0T/059iHYmOhPueqaYu8hUpmH4fTSgSxuN5aRQ2wYWHG23RyDrM'
        b'P4qgiiGsoTLgEv9xAy56x9kL9xtwrfJL9SV/r8Gu6c6z5jjNne3iDH3QkZKSvCspVeGBFeS07iAUWhdeItcDIVD1NXW09bR0ZeSWz4ECLMUTgQF4DCtC1KjjwMsy2Z4Z'
        b'zHU/yd8GaWRZHtIRZguz17kyrTOUYRpWO0uFULwmOAlOcD2a5848mOAsFlbbC86CM6ZBJTORwB4LvOysLoSMFeYIc5L82ENH183OIgEr9gkugksY4bCp0hf6dsM1ZzUB'
        b'2sntNFeYO2sqf3xu215nCaHB4JTgKrhaEz6btaLXDAudNSiAvl6YJ8zDwQj+PJsc2o3QTe6qg4Kb4LYcs1kxHpgdCt1SAY+bCPOF+S7Qwx6vnIHHyUiSS/yisFxYHgrX'
        b'UvVZW+btUIgF59nCCmGFXzgrOZx0vEuhLhBap1hYKay0xm7WGXc44a8QCft9BXfBHY+48lZfhLaxCjVhBZ4SPASP/WQ0WDCEhuD5ColwQEtYJayihg88cwNcTlSQvnQa'
        b'CJ6C5wEoZBVuxuvrsZsKafG44CV4iaCIZ8+As3iaKkqMwgRvwTtVi5ddvnYBdosFbFwsyAW5riXLbGUGZ7BbXTgsFXwEH3K517Gyt0MnNmC3iLT4vOAr+CbBAHdhf5lQ'
        b'Mz3YTaahP1nwE/x2whX2wRKyfGqwWyJMxBOCv+BvAeVcVd8I58yxW0Mwni8ECAEx2MEeL9mE12RMtTQgrBZWw3UTNq4JK5fLyGinTRTWCGtmuvMZa4QBexlp9/k1ZDUH'
        b'wjFIZ3lNDy6XqRMqsEUIEoLil7Cxjjq0TyYSUmRCsBCM/djJmzB4EPNkasJYqBNChBA8omB5V63Tk0nIOtkhrBXWYu9i1r/d5IqvlpGhPgNZwjphHekTN+nAdFOKCxWE'
        b'mXBGWC+sJ7RzBXuxFjvhGuRLhSQ4LoQKoXAKalm7yd4gXAjki4XFWCNsEDZYbWPNcTEmY3tcTUiaLTgIDpSH4Y/nQi6Ng7EAzgqOguMOLOW7pkADBwIFYcoEYaow1QEz'
        b'edknyZooweNiwUxDsBVsociF5d4MxYcCRYQaKhRmCDN2Yzsr2hKOOuNx0qmMCGGWMAuqpvFCcqBqMjWjEEcJdoId6Xk2r7IOr2sHqgkTtwqWguVyPG5tx+VBbeZbmbFA'
        b'PgxCgy1FQdKoUxLBCGskOBCawmxs8KiXKXtOfkggLZkWV2KEF0mOCXFMprVVX0ILoQWwDI7JvADBl5mWpMqpj+5i9ppqCa8vmkHdLVQIPOjG1SRyBuWrCjCkNmHHjEgz'
        b'cADPk+FhGqiMuXiMN4LmEQu78KqxEckREcrtgLIcCSvIihh6n2csoiU0keXMqOp0Qo12KevRgLpkwcgej8JlmueSMa+ErC8o57VoTINBbBJYGa5wlllqEb6hwH6onaR9'
        b'FkK0Kx8HhwBu85iBA0HKUTIXC0ZuWMLGASsUvIAyrI9nBZA805ZCoaDsZjGeZAO5l+zGTFs2DRKoWygYu2vQTi6BLNYHGIAzWrwLtBEaWwTsg3Yj1oktEayKVTigzXrA'
        b'MhjS07KCdQKKdnDhaD12qrPX+wnvUcy7wuec9gQKJcywzGh+IHtMmNou7IKrydRz8UkjaCJ53OAEa07oErjMe8vzLKSnai4vZ98CPuqX4biWssd0VEmLW/AsXx1zJrNF'
        b'ON1wm3INdsxSzh9vDhuZCrzERkbiBpWsrnTsSrbBs0Pv26SsudCoRQ7N/KE1SvKQ9urwkYEcCVsjG8hg9Q4NLsmykDIvbGx8cICVsh6bt6qGVwPqk6nH8WO80xOgixtD'
        b'1q1ePzTAGlMFozWbWH+Xk63GlkDvtr383XK6AvAkWXe0s2Lo5gPSj+m2fGSP0lEjy9CVMKEnaF+OmrIagh0sWBPZ+4WkjPMTWBHLlnO5dB1cgAre14ZlQ1NN7bCUQ9KR'
        b'ysZVndwZV3lfptDIXEM7UOCjssqQS9ubFs7h+zY9eSqc4wt+/w6+H0on7hza1UdJQ7EjgPV1E5ziQzEA5Yl8wxHWGdMFY1da/ylywNKuKrDOTTnxEqinS0gXzvOpxw5t'
        b'VsPGg1Cg3Ew0x0JBqm3MzoaOpXxbnyOXw1HeBlu2r8mCamAbP2YWy2E4i9x2qlmnlUDrPj4Qc/V4K4vIiZzHjw1zcvysC6CfU80/a0I89GwY2tHksy3CXGhlg+Cuy9bE'
        b'OrKu+lTrF9MWCmQwe/ki3wYtbNNNggLo5a0gRwrphrHgwvbcSWxlheBFaMQTfA5Yb8k+qI9X7rjMjawhiyyxSFkPWz7CPA8+WGbbWT9m46DG0NJcgdc0ldMNRyKtRXzp'
        b'HXfCs3IWHtyT+Sa97A4XxXAUroz/kBGTJclLrbWZDdy/Paj3pvBQdSHc596+Tdww7uk9OsI4YVysJCDcZ5/TeP7wKV0tgdyta7TCw2PLvWbwhxYOhsJ04aN4PSH8wNYd'
        b'6vxhkSaNFrhdLloa7nN++jz+cFGKnjBJ+GqB5qxwO7fEMfzhYnd1QUf4SiQzD4/1PSTlDzVnjRHMhSNxGonhsS8cnMMfBllpk7E8s1jdIDz2lVXb+MMrC4wFK6EkUX1p'
        b'+KRfTLT5w6srae3zFkmXhsd+KIriD4+KaDcDTDSE8NjP5u4SmInzd3NNyeW4fY+eefjCDK/xhPUL8mAvkLmpOqJFOhD7ykETnrvBUYO09fw8kjt2lv8h4cOqSvrf00tY'
        b'BZ9NpT3xnKxlHm5npzATPnRm//1rCbcNzWRRNshhhm3kxEoQErB2K7+oz0BtrK2GgM1YLuwR9nhABrcxZrfEdW3HUQsOStz4UjGLYLUu9ac9uKVNezBjgw7vq9V4Oiq3'
        b'VmgvDd/ovkU+2qxR5TuMCp+2KQ0beVSk4SBTSsTHbbWY+MioPUPBkHSE3wuGpK89HAyJMqqJ5LAusPWjhr3MZNDXxx9PPCqyFFzEKhkM+i3b4sq6oKFYL3QIHTJxePi+'
        b'9TsInyP284t5LvMZiYJW43FO4b7G1994mUH7F6/feb3ml8jKX74zMnEfk7o6QLTE9XTB1Hc6csf4ObYezehfejMjqDbkvcRZlVMei5j79c2LX999+uzXN48dfyX9b3ju'
        b'Ssvmay3f7zujpzlBb43nNMnY9e/fnVoszrOqK9C2DHh8+oGXA1ZJfHtueWh8mGg2NnFMReL4wP601v6smI1P6t68axkfYdo3e/e8nVY+2X7n58ac250e8LhNyhOfPKZV'
        b'41tps1dj9+DH0/2uveQxfvL8pH0+T2gFtiX1rZgWteaYXlHixVXHNv8W/6Lh5KwLQVd8353TdGCH4QdJb7/l4Zd227Xy+8g3w0MTd5zTPLyv562563e9p7OgOuKe0baJ'
        b'L9d3rpnz80sVRXdNzKbXPGs5s8bsqffTP7+l6/xZUVlNWcdVF7Vdl29ZBL6/8dyut/6huenZKO83rB2qDMe6Xb/n+blRxfPxm6uXveZntPLQFTAzffHF9C8s3Hp8jk14'
        b'/luvLulP9ZmtN+/9Y/Lxu8+Wblj4XKb16412byz8pt3WxEGhVrxSPuPwqybNd2oh5Pazoe8v+fk9vdSnfKR3Vha7zk+N9O7ZEyLzj839Z41NucUvLzzZ9ZzlgppvtGyT'
        b'iq51OgW/cPf1wuedjq+bdehcms7avclnMr9eGTCYij+cdO296xriU9OaZObfP/fVxidcbs7s/m6tlnPj1K8Dl7ne69nUe1fiem7fTd/Xu+ev0fpu3Q+nvlO7cbHB/mDo'
        b'k85/6zv5blp78rOfPJl3c3uixFnrk9dskmomprXKFlcafRwRGba/v7PiF29J5od7vnZ7NvXrPX9z+uapfekVqU5xF558vKQ/7jfDiDd+KNZ2+fc0l1s7tQLh+4GEX2y+'
        b'jflhxeC0r9v7PC7/LWz97LcuHvK01uPWUecI5XCOyljJklbDWmdB7YCIMALdJkzKak/Ys2OY7+jp5019OEg9RdC9ABuU4R6soUzOAvvJqYfshXYyPCUR43nI42qE3njq'
        b'CJtGYIXqZYR9lGiLZkO+MmICYeJrsNqW8HBtcF3LW02QRoooVoa9lGPrdOrNx8vOizC5Xctlu8R4yhZPsDYlG0IRN01jdmlH1lPTtHFxyvArx6Hflgl8oYy0SZoqwtxZ'
        b'0M3E3gnm0GLrgIWboUtNIESLKGQttLOuzCTUxDly/eRhcTwhZIfs0vAY9LBR2kCYEyXQQ42yzFk66mK8RijqPKbS2gO9XnJqBANn9pM2SceKoF4yi6lhpHhiC+kJnFyu'
        b'DJraALnc7iwtGrtovKI5kD3K39E2d+uJ/7cmLr8vOdT4kwLa29qKrRHxYTFxEduimJx2kJ7Sf8TS5bDgK1V6Y3j4P20x99CgzWxW9CSWzN02tU+hljGmzJeDHnP9Tf1E'
        b'UBsX7g3CkNrESIzJbwvm24E63jZgNjViZiujzX5TKxsrFpt0SMYrJfkNRA6i5PdUskHJbUlM3LYRYtk/ODzvq4xSaFlXqFEKlXv+AcEr/ffkuBHCV84qVZjh6dGXkZpg'
        b'ulnqBY2ac9aM8tyqPXQ5UvP5Eeg/kRJvJY7WVnlslf6ux9YHcFb04nwwKPdkv4cLDKn+i9Qpjhb/VZyn+IG61PzYtepjKmGosjNOCTp75yYLqZYkYYGEUcunMUaVwEAr'
        b'T69AT7o/vdTMdguu+9WtFuGxmAXPBqkpKMh45luan4Z7RtyMtir9KHzjYx0lR9cZH6vLmJ3ZXNmZ25k+9eRR58lCwsvqb+jUWIvZETRrXpB8yHmMOpZOWCgeC1fgAg/L'
        b'0j9d9BAtNnbPY86LtLcP4SseIgm+Ldu6PWrrzjBGpbANNOuPb6DDghX3c79vShj1UBxG/R8MW2GNKHloOYtiRixm8ag1+4Fqzd4jf5loK6PS/sE1e0T4XG/kql1JT184'
        b'Db3Md5gnFChhFw+YTlGYjy8WqRO2pgHOhQjUJ6sA18bJyGXRi7mMrTNymS23o0FKCqSU2OxQnyDWhipPJjzS27nfFkv9xEZYL4jHiARZEqdlTcXCypks0GtsqZcujbjJ'
        b'YFHlmINNch8/P3sHdWvMFDT9xQronc6+sSHDkqNG1odBuM4b4R6CgkqbPr90N1A30cA1SUIjygjf7mWEdESkmvDywbEMnVoXS4h+Oqr5m9UIyyFoWmsKOq+v+zU6TFDQ'
        b'Fn6/0jUwOPXb3RLhpXsSNdGMqGAeitZLTfhKhxeRumSioKDIXe/p5RSIItPoJf/nsXwe6urCLUseO/TeEg+eL8nP5D0yV3oRnYJeymYFlTfe9br83j2xfZIgWArjfGIU'
        b'9C6aPwUDZW8H6+7STQwilK29qGyVj4LeX5YODSy0XrMVNacw6kzJk7w/q40d6wxHvTZ55kv6T9s97aXW/r2gIRI7qT/G6nX85MpLdLk0LBKsz65mjxZ8qf8SWUI2/xYJ'
        b'Nk/u4b2YEphP1tCmva8JmyZ6stZd71mT/4Jwb78gvCtkjr/FnuV+05D/gjQ2UhDeE7LW63L+9voqAfO9GKTHWTrdlVz3+WJvrIGqmDfen6CmaCblPqF+233N3+JfXqrT'
        b'u83paZ9dbyx/Nn7Ny8Xn9929sUpYVKbfEWJzrGXu8vMaxUHW7jWLzL97TGP64Vv67zz2ZOInWvu7DCsKvv35558/++HphX97wqB07zdjNC0sV93K/HVTi4dnPLTL41d2'
        b'udmUTvzm8aDA2Scn/3og1zLTMeu57TPNZyYtu6d/JXP6jqCDrk1LB7sP/n1pxFLjAylGK//dO/3J8k9M1Y1kIVfr1cYeHz9rQPrZ9tefWWuy5ekZk1Maf6v5GnfVPvfJ'
        b'qryXWm/uvbO0LSjXNjjv9KLLerv+cfFDPXCLD3/bvWv29Jmv51+ee1n90hcfFBz850Zdqx2LX9vr8Dph034zXyy+92un3+Y+OHpQZn8j8yvJhs1zZn18tWjnavUki5+/'
        b'bwnxP9I1+eNv2uZpvDJ+7PEfrv6Sar/HZnfjkiajHyd2f+ja/eFC/4+0n2uxDW22DY2udXr2F3eP1yZlTOxadSfi1abG7nd//jK7wNv9H+/cqbX94Utzi/f6z5WHrFn0'
        b'ZFPPW09qfLMLPvsw4E5Y7m/FX2ktfvbAu1mld8KyjD44YPvKnjlv65/dXNYxWDDxaYfErQ4NHxjCe0ueq6wtWh5hbcA9eLUnzZRbUzNAdcEcu9W3iW2wWzrkBLJrHqWJ'
        b'GIqPTHo7mfAScQJ0KxELG7E8ltpm+EKGvx0hrmaLoC1iMaM2A5yhitFgXkjYUo1xThSHKD6U7MAO5TDsx1xFyq5dunpQpK+PXTpJatDtLpjiaQnU2MMZVobxGhqjklKk'
        b'p/DEEElKTqgr3KK5YCn1wwVtgiiSkI8ZolW+hJajJ5IXtpraejMraJGAPevU14iN92A6t9056mLP2oUnI4ZoQ2yfw61VMpdYELKS1uitBvWOgpZMDMexD9M4iZxNaOnz'
        b'5GNre2risCZKPVw8zQWL+TC2Rs0aQm7o0BOzTeysv5d9t9Zwki1UWJKCc7xokEsZdIqxZnMKj1TWh8exSu7ly8Y4ZJ2guUkchbVr2QB4rqMei5UXGxRCozq52bATuV3Q'
        b'dmiH6wzg6mOtLuAFyFVfIDbGCov/Uj/9V+x9RxGdw9cduzNP/pk7c6aeGosawwhLPUJIGijD01PTAXNGGlIikcZ3oQSmDnMSxt2M0ZyU1FRnJCUlTilRSU2sxeQtM7Lm'
        b'RgLK8in5mfyhipxUuy1NjEjZflsaGZEScVtrW1RKWEpMSmzUnyUwJckf0zI/oT8+Ul3btB7jP31tf2E28to2J1/uh47p993aGoKprzQMM4whG1q3ipU0mnQkyUfJFqYh'
        b'FkVLVGB+8SMdSzzgYkX6ANEn9SMXNzsoig0dKVeV68hEguTuNIQ+/Z0STFvoEPNcu4tYQVmsjHsXPw3/KPyTcJ+Iz6K0o++mBt8UhImlkqC5ihFuQCS/q5e/rUvnZPTa'
        b'svkza2t78qeq2ZbyuflktGHHSKJLfP8U0o+D//QUthuMnEJ6+O3CowfYaC0X3zePM1aoBS3BI/+zOXyAcJc8MIcSv5hF07TVmHf/gKfv8AmKjd4S6RmhGX03VrT6kjDl'
        b'e0l02K4/OEWK/26KdiZ/dv8UffyoKfp49BTRj9f96SlqGTVFVPFhCjW+tn5kiqAWSu+fJKxVCzfQefgkUVubbDpNomxptPSvbDU6RQ/GX9D24yqUesxbq6S2oWaDVKDE'
        b'9nIulW1MmCI+IBX2fKUvPbwnwMqMPczX4AzZLMtLG/atPcRzvqIhUGH1ng79Kwv142y4vxdCz2c6BsIlqIF2mswQCINQBDnsi2srqGhaMJilXmj3TlSwkKp0snx5cqA9'
        b'ltt6ekkEdcifsF4ssgiJ2evhKFYQWlIQx5tMvrlAD2YZr3yhMmnxM+ol/1heLlHz9c73/HipsfHfv3v/hLWZrnzpd36zY758oaD1zLv2Ta2zupyc35m6IihEZ9X0Ns8D'
        b'z2f9O+bLTa/WZ0zfqtXpOjlgYN7Ll2bE/4tQviY3vjjr+lt+dtw/PJ488cTFxZ+/tOeJb34SWTuZwT+mWGuy21VGSJgztvZWnvZj8YiYtLFKbI/NUMdlbb1LMFdF3gia'
        b'eH4KpW6WYBZ3Z+uizjQcNAawSNBcRkiWAkJmbArmtMIJLA0ZFnvhRS0q9oI+uKaM3ghdeBlaGRWCuZAFFSLqkdtiHx5hpZth+nqVCEsHj4QzCVa7MjSvMzbNtfWkMig9'
        b'zBGkriK4oIXdrOIZBzGLi8awQIKXQ5SisT4se2Bfkh30sFtqeLfq0AM1MTI6jF58bLMu/jObNZ4KZvSUQKhx7JY2FCV/PmIDh9BapPfhiR5opjj5C/pNyFC7WBEb/vQ2'
        b'bjIcuY2nC4xi67aVQwVcYZeTpxe5OdmoEv4/Q4qNcAYujToftZS/Fab3BfQqk5TplGlEiyPFhSImrxEPe8iJ1oyUREozNNNFodIotUi1SPUMIVIjUrNQHKpO0losrc3S'
        b'GiQtY2kdltYkaV2W1mNpLZLWZ2kDltYm6TEsbcjSMpI2YmljltYhaROWNmVpXZIey9LjWFqPpMez9ASW1ifpiSw9iaUNaNAx0qvJkWYZmqFjotSihagx6UKRKHQMeUNl'
        b'U1rkFJsSaU7eGkZOZS7jLG5r+EbEU4u+n+xHhZGhsafM4/grHlhrdJgZQiTSk3rUwamSWlGtDnM/xCzY2NDSm05LdYRKf/cIlbBmSX9K/4/Ri0a1cDh60e/FCqK7gocr'
        b'on/RqEQRvIiAlR7m0TGxDwl8pFpNdB1rPnCMm/mlMp/GRWuxk+1vGtrE3z5ECXeCdsyxcxAJq0QacBLbXLE9muGvNA9jlSwxKZC8HcoapEnFBuQoKKchgVkEWDVhq7mm'
        b'zjgNdjjvmo1pw5FfcZCcQa04sJSx8UFQMZOGdsVi+QzIGgrtiqchgyl3Y1IMbL19ucNwW5FgNFOCpdiGp1LwKNMoJnpiv9xp5zZvsSDCiwL2CTHcV9JZbDYlhylk40Uf'
        b'ZfziY9xBDfXGXyDn3uXnO4sEWYIYKx2xi+nV/bFkJztlMddnKtZgvg/1QI+1kuXTsIxbB5RvhityaPf0dXDENnvqoV5/mmQdYQUbWIdiA6FPyScRZjGX9gj6SI86bdnn'
        b'kzdhB+GwbAgHWwbdjmImtoCjWIsdzGhoEVxyUsbmNoOrSqdFeJ00j6HZ7cjJPyKI9sFJhB0tIi2jfZ6KpZApxzy4ABd9lEGom7x5n8/BoN6IKOnyFMJp9mEL67MMi6Fj'
        b'RJD0Dio94y6gcIAJsbbMlwoL45kESufJCGeBmw5e1dGgPqGm6iYJU/eOYXfzr5vVhCA95r0tNsEtigrTmPVHHVzzGemuSQ2OKD02uW1ax778aoVE6NlC9avhOpc2m/Fb'
        b'PYVCGkdEOF/kBgNwdhMv8zrhgNOV4dUz4PSI8OrzyeKhA+JjtpP5j4q2VkVu74FSZg6EOToTbFNDHxYAmHl4CpFyZuIClm2iawVzkyGD+ncSk9VwRrIJqwJjTM58rKYg'
        b'17FgZbT1YOmVeJyl4+5V2Tnpw18u3X77KY2Uz95qzx87dYV2SqLTM/JrVivyD6Rd+2aBfPYnku2nMgcqzFNTdfb/83arR7D84s6OxBf/vuHtN1bkb96958X64FvZn8/u'
        b'/Mdd2U83PlXfmZjYv6Q0uO7DxyzVD4R8d+CZKp05TxWltsZdlM03qsn7Iv/VesXhymfml9Us++aXj7Jf+PCF4hu6kbtjV3ywcj7q7UzZ88Qnd4omLW5oM1s0r2er0Sc3'
        b'HvP72s3E9b2xll35uyIfe163J/BKx7N+rzyz9bMLmzv9HF5ysN7ml+kWogjZuTp/3t4k+ZO7v5h5L+/6uyciL0xszgzCBBtjL9wA8Vc+eL7wqN6x19+/VBhgunzvs2Xv'
        b'f9TW4to4vTHolcnbjkWuvmnxdL3jM2nfhpV9k156Yc2Ljs9YrPn11M3Uab0lP3mtz9jUeC7hmYMO39/72TG6ofMr4Zc7Gt9tqfjGxN56ApOpGI5bwMkOSnPEQANcWAhV'
        b'jJKaOQHL5D42DvTtVjJNslgxWeAZkzkxVKB2iELXKbEzFVsZMZUvPijHQYYy2QjtjjLmTx26IHNUMI8ZcIEBLOzJrA/eH2MgEztVQQbGwWXWDgXZ4OepnoUcbQFwRsIo'
        b'YE04zZV4deHW5IrnRxupzICcNAoxVuH1/SlUXOwO3cvl/stD7LnyL84xhZvUtGImi9rhsGr70Klniqel89fHMqWho0cs5Ps7kfNOEivagGdCLDCHS4TOjIlnzkN9qAuD'
        b'WhFWbIUSzLJhL/eJtMk7uo578ZQqqkasO0fVVGILHGP6Inbu8UPP0FWyEMqgDhuwiOt0cw7r0/gN9ORjx57hfslqH+hbiyVs4JMd17D66cnnq4tNpL+rSX8hbQr/vAMu'
        b'4yka5YAefo7rEsWCbIYYzxjjRaVbkaXQpHRXYIa9So8FWGXCkWlnCTeQNxQZYhcc5b7m9LUkKasDuPCq2MafvSeHxWJokFKfbuOh2ZJBYbBouROdjGFvc4bYICEE+SU8'
        b'CrWreYSFABEDYXn72vtvpAC+fDH2rcA61joj0q4OGgHdy9owlnmT01sh8XDDNh61vR8viBiP9tCQ4uTb60tTNcZs2s0GKkZKi8JielXKYtllqbdNMt8Ci1lXly1hHWWH'
        b'Dj9xDOdJIGcLXMWMVXwwarDNjpKPwzSkoZ4Ez+pAo8U8a7XfFwdp/VUUgsplf8efockPC9rajCLXYSpXTRGXplE4DIvJzP5RNwHaTIlLJWPqIh2pMQPGaDNn/kNP+T8d'
        b'sQFT5v6Z/NqifQZKGvF+T/1KQM1Ho5l6zT8saBTzT21GDVPin+YVSieNhNA80Ng/6hT8TeGRvrKfI+3i7vhVNag88Vsw//dKWnTYJ/xfcb2vdGWtEaaI2Rb/SGf4t4Ya'
        b'xKsfcoZPv4tISU3+ay6tpWFbnLY8otKXVJVaecRGbDOPiTaPSeEhN5c7LVeNwV+oOnnN/2PuO8CyPM+Fv8XeQ4aioqLIRlAUB4oDkKmACC72lCVLxcHee0/ZQ/YGFZD2'
        b'vtsmPe1JejpO0jRN2nQkJ2mTpk3a0/a0/e/nfT8QFE1ie67zhysIfO/7zHvPF5//f67MbMCVq04KD4tOSUj6yu0GpGXZl4QvnO3HK7Ntkc7Gdxh46drkCoFxCWHREdEv'
        b'vNK3V2Y15grPByenGPKvhb7s9LnL04ffCA9NfXF7hXdXpjdamZ5/7eXmjlqGZS4n7EUzv7cys+kyWKWsQimCL36Ilzp6ucCw8BAClRfM/6uV+bdyuMQ9/0/Vv1cIXIbQ'
        b'F0z7wcq029bA9EtNvHLTy0agF0z80crEO1erxOzMl/XhtZNL5+aY2NPBJ8KV4BNBoYA0eyFp9gJOsxdymr3grnA94ygb6lkbtvxzAl2+QjlzaRPkv/iv206Xg6/rUeFc'
        b'z+GUKNbM+QmUJYXzPRC4nr/xCSnPGgXWGAaWr+MZM/yZtwdkuGr1XVYXpLXq3T+LFAvkC4Uz7tXSavXYF2Qn8OaF1TWiqrX+c6qoBy7n6HK9ar68GJEhkEvfusy1Vvb4'
        b'JH4lIjI8xfPLl1Zny/hEUZqu+KXZdKagZnWJda7qKBPLsnBKavTAOt5WAf1Y4crXA3oqhIUrPQGLskqw6ICV/zLfSu4XB0XRpcq5VfC+lXfe+i/mW4mJ+E1QaSTnW9nm'
        b'5i4WbJ8V91po0uWyZ+JxHMuX73ZzyKrbxaakL3K9JAW99EUrvfiik8NT1shu8Wsve61D5skTK4v640tce+kalwxLKr4csPmZS7/otf6Vk1rArtxUCYvUsEhaLHgfDHny'
        b'wCCBHpxXE0L/0V3SdrlK0M+/JGH5a7ZCmDILjlaq7JLhHDqe7VuuRrqEuge7B8f8/H54VGRUpHuoa7BnsPD3elf1YvR8dK74v28tY5sYIRCM35N/o0r4TEzZ+vFlSf5S'
        b'uOGrYn2VOxMry6mK0jWeubflmde9n6dm/vglLqZ2dSDZOvOvT4k5txhfXF6w4hb7MvTY4xlieoLFzSXz3J6o71qTbrJhckp0bKxhWnBsdNgLrLNCwXp8RNbT14mv8Bx8'
        b'SyBPz/xM3TzN3zzjXLTouyXi5ED65FBv30dBr4Xs/rVrsHJEvd8H9LO5prja/ZS3iXuQQ/KETmWYyfezfx+g6H5sMEb/YGOM3kG9lqbiwzF6OuOWYYJia/Ogi6+eQcOv'
        b'V36zDVr/3Vtb7vtim4YpGcEPJHqXP/y+iTynrZpHKG7AFrNVuqYqzIqdN0ED77iqgNabUgOuB7ZclBpwA2GA05vjiYjkSs2hHmKsllpD9TKkrVeJUBL6QCW2r7HxtuCo'
        b'LW8VqLa5vh1z3Z5YHThj6/wWzhhiFAr1vLVZIlGKE0L7AZjndPkIKLI2Iyw8DcMSgWysCAaxbbsGjHNv3XY54UYfmMsKJAbX9YQwCQVXl9nEF3mp5KOTA7kL5TDl5FfF'
        b'FC2+CB/3Pxe0zApMSFYpfcvDP4+brbu+NcxNjl7860sgU4HmulroyoJMtNar4LCqVAPnMjvPDklMOlgSC2hMepNVbpBf1hzekl8W4t+S5eXht2R5UfUt+WXZ8S35ZfGP'
        b'Iwvcdviz+Od7Ga4iOZ/Qwq6yU3Kn3+QlEuHuS/98AQVVJWUR7yNo8oNxnkPArDkHoIpQLoL5zaI1bFpT+m9y9tMuPtlavVpBmKiMOb7kClQKNAu0ImS+vGuPf4vkB6Uw'
        b'5Vx55tqLEITLc840eTZ2mEqZkAv4VqJxJWGqYWrcuAorn8mQpKoepsH9VZFbjV6YZpkozIh7R5N7SztsQ64Cfa5EnwvYE7Vy9KUXplMmG7aTqwIhI23boVKgWqBeoFGg'
        b'VaAXoRymH7aRe0+ZH5e+5GsVaK2bysRhuzh3pgznc2PtZ1QL1NhsBdoFGwp0CnTpffUwg7DN3Psq0ve5t2vlwrbQ+8bcnOxNNe4tHXpDgXMasjdUuf1tY/ujHYjCtoft'
        b'4HaoFqbF0fjdb6lK4Z7+CY4MT/r5XrqYNaTb0XDtE4ze07/JhsFE6lczAOblC04xDE5iFpVrqdEE32sGiiAJnXs+jD4KTWE6W3SKYUpScHxycChTWJOfcgaeTiGGkpAk'
        b'nWplluDkFZWHOFG8YbBhZHRaeLx02ISkm08NY2lpeD04ifXvOnjwWW8j06ae2uAKIzt+ytfR0vBkQrxximFqcji3g8SkhLBUbrnb1vpXpbYx5h5Zk3WwtlTISpkQdu0r'
        b'pULEheLn5htImfHPLzx9MdwRPeVjXebFcctbeSk368pJMrWLrnP18a+rX7E7564qzNLwNGdgCkugFZE+Zhh+Izo5hf3lOjvREKllJnwd+UC6IKkqza/pGQX7ejRbJH0S'
        b'kUrDBYeFEXg8Z03xYfS/YXBiYkJ0PE242gD1AuGEXd2z2Rwqnqms3yG0Yc4R5i3F+97L1ThdVuzWWI1l7lzZTG8Xd8+VOqJLWKCEvRstUxk3UcXsq6treT5529sFWmGS'
        b'd4TKCtKwQOEO5EInJyOHYbMW1pCM7CIRyBhLLgmxEVtvckH+YpjGOTM55jBgCaZQa8wR5ONYh5k+FtiHk8ZwD3ttBGJLgdphkZHeVq5bEWlx0avbRe3m/OF8m6j9Jrqw'
        b'KANV2H+eL/TSLadjRpzEMj1ZkAzd8pyU5pksFkiMCumnIPOjFpcFqax6zTYohVK3J1vCQvezUICPWP00c671C4vdPZsgh5l7LvNtgbItcSH5GotZLBNghQCK4ZFe9Gev'
        b'tguSv0kfV9j+6VQFC2JSzv/bpxn9KnE3j/a4GpbDToHCm/7b87dvKLLpUzKPyDIzeuPn1q1CY6Uci3/cvT2rv6H552XKRz7wLHXd53bWdHDa9dK/vfUDn1f8p+yKzlt0'
        b'fZjrmvyLH4Zv254YEvz9gvQGi4Ckh/8BJ4rO/ASDylRU71+/9mi8OuHKpNuBnfA4fYNCk7pO1fc+Tzwy8bjg2+9H/ahd81W/ezUfOcufWvBLfv/AuPrRX/7M2X148NNf'
        b'mS1q7d932eqo692I8VPX/iLcCkendD420eaKEwZArr0b560SbXDk3PN6nAdsJ3Y4cQ46rN3rscY/52vCiYQBJFKOui1DBvOPV17CfigVc5+eJlgYWvEbQjUUCGEUOqRl'
        b'wCWWkL3sOeT8hgdwCUkBwwXehzSeobcSzySQ2IdDsRAmBL7cyFdgAPNw7rAbHxlhIitQ0BZB52FHvqT+9FYWAE0s3xNnsJJduaksicrT4rMnLvMFzR9HKJpZYTGTBmTh'
        b'PnTvE5mfOMQtyzEUly6xQg6823LZZ7kZHnKeUBhwSCUpmY5Ksg2qNYUEwZNJXAT5oXiHVSX6/aBQZEsC+QOu4zqJwjK8P03rLMuSYGX+LWQFujArcYEFHOF3XEUAObUi'
        b'2stqOXmKVDZAOV8EvssM2lmNu0hnN1ZFjl+aBjSIoSIFC/jgsuo4yGKOMc9I0mSlSK7qI/aA8tgUrvNRMy6ep1dZLigrGsgl8UC5FYxhsZsFV92QVWdwhgk5qDiPi9y+'
        b'jLVZm6CVOAer/UJouYUD/EnXnMaHLCcFJ26uLRMYguXczq2j8AGLS8ZyE+iH5TllBTo01hKUpD4b9fVlgqnXc4f5flUFwJ5Ji7Jc4LgqFwKuzHW1ZsHjWzh1gHdcpeuu'
        b'ZcLP6TG9wmJXaQgvcP+J+WfXcVptUqLNHPxqCkOm4P3V6YfPXfKXNbPLfJHR97CS1Oj7zFQrjizbFc79LKtexZb/mabS3xe80PFydHmRX8Ykvsxl11ilrXnBiAlE4v/v'
        b'7NJRJHqlrid6sf/WmKaTwuMSUlZ68JIMGZWQGhvGRJ608CROHTQMjgxmEtm6Y62EyJ2IDQ9OYo1dT66IYVLbNicSRfMiH7OypDKjy7qDJYenMFEuKMg3KTU8KGjZPWN6'
        b'NSE+JYFLfjQ1jI0OSQqmwZkvMC04OjY4JDb8uZJUykpb5eV7pdcSkqIjo+OZNMfkcOfwJIK8m+aGCew4rkcnrz8a731cWaBTcGwyrfBl7fbbey4JObv9nT//+tehy5Z7'
        b'3m6f72Ii5Ml6tuMhIo9HYIQo5NPk8WDcv9x2H5i+6yl8TQ6NDeSO/Z8y4Z94KaK1tMaIz3qfwoha1BNz7gz7wd3LAqvNVh8P1q9jyz8KQ0KB3hbVI6448YIYfM7UWCB8'
        b'uRj8ZZR+Ot0l9RA7EyNcZLxVMWw1d2VxmUXupq7mMOjLh2iyP3i5M/MZDEGRkv1ubIu2mntNmGxFg5xx+MNHQZaaHwZ99+6pkN06psHuwbERsSG/CfogKD7iN0HFka7B'
        b'fK/iemV5LZ13TcQpjGhoePiuw9Wf4uj0CFRYx/IVc4exPWXdGt4SeAxNJP7kkpRmxJ5sYa1BeQ6+Fj7hMYlgS1gEZctegBcz6hU/xFe2aYcwZvylAPcLXBLrRJiv45fw'
        b'eClYnlkTZe7Mjq5REVtfAphJmTLDTgLm46qklBiYiLj4y0PQAXlubtgM45yvgvkpoqGWT/8ogT5YcjNzgUbOWcEcFanQEh3RvCDmahiUhZ1Y7amonWC+ithI11BPzluh'
        b'z3krVnwV3zRXCC59/VlfxQucTMEvfbnnlRXVJel6z7vcZ/0WX7CK4y91e19b7Vd6/mqI7jHT6vr0hR00i5sn+iJDFEZmhcKIXxiiHmEi+UvfMzzGmbhQ8LKItNqW9Xx7'
        b'SVxSeARvm3gmfGgdk0ZSeEpqUnzyQUPHlbbs0l0HGSaExBB7f4EpYn25RsYzlV2/TZg5p3wxqD935ryF3/l1g9khExqgd69CzN4NfDORHuyOlGroIsxfsVqs1dC9leSw'
        b'zA/nok9+601Jshe9V+7+g4+CfhP0YdC3Q6IiBsOZ68X/a/44Xjnh35trIrN7x7e+9903v/Fmus/Xz4h7rhKoTzVmxQRMNk41lbS6+vs0HpvcV/p15dZoQY2ZxvU4FRNZ'
        b'TusJhXKWwMTpMzCP3VyuzbabnLNdArOwsFPhaRURF6GGi2t1x3y4z+nNV7Frrd4MmXGc30MWHuiE3pLq3KRxQzY0cpptnJKTm9RCA7NBpL8pXRDhaCAucdTYDyeI5DbA'
        b'+Pq0G8duYt4alH2+BrK6mgVL95HCDIfEB78qEifyUYTyXBui9I1Poc+q4ddG+/mtJc/rO1RE/GNP5A1dGsL3pbB8VHs1lr9gmesj+DMxKi8SHpZRe2Zd1E55NjIoIWI5'
        b'jeR/H9Md+Tm/BKav7xEl8TbO/44omYmw1f+W8VHQpa997+uEcfWd+dtK9jRm2aoIrE5Yf12S/rqhiYjvWNALY8pu0ARDLOWKD7jlnDEb8Z4kHXodOBOIhgXxPz4omWVj'
        b'PLTlEjKidiyLnev7rJVemvlkCFhM6nqAIL2VF8Kr8DkAytYT9lIA2qb6RQAqXZd00rfkkoPTwgODkz3XN+yz2FcpQ5LltFjZL2nWJ8j9ech6uuUy8DI/R5i0uPyXAl3H'
        b'FZ9MeEowCwAM5oOk4hLSiMOxcvDL4/6r4J5/R3pAB5n1n/PGmDM9Ly41OYXpvzweJqcwXZEFJjJ7xbr6Hm/DWBPUxnRFGnw9f8EKyrG1JgVf54+L9vwCTGOw9Kx5X9Ez'
        b'lV0i5EE95KxhqzDr+FzOSlwVuqGOS8u6jDNRZiwnSwB1Liw/tWgzVy0mIudvPqzITFZbokQgaRKmyCZz5vODu1kNSoGhtd3vXAYvHBL4ciYUvprkI5iEejMvluDVcNub'
        b'dUsc94v+kdePJMnEJgXvutl7fHdEVeSoLv6Z5/t3s7ftlm/TFUnkfym5plk5lf/vO3/xu/s/3R/uGGz61mdKuSePbrPdlnJcw7nurx871lTuk42bPLzzA+uIx/WnLxX7'
        b'GbUFvfmLTNvWXtuZ0d/DN3pGe+ceu3pv+refxe357tvv/eTA5f2/3fzT3262iIv98MP+8tdMszP+VPjNz8XnBndt9fvERJ6z1UpwUeVJ2go+vg6jGo58f5M2zGVFW3kG'
        b'DoNYu8zEoQLqOGOqbBoO88kp2HF7DQ/fl8aNfggn9ZYtwUJY8Id7kHeIkw9OQD5UmJly9l6svWkuFCgcEkE7diPfmuf4IZiXZlfg45inzMGWmnxA3yDmma62fwuh2h0m'
        b'SM6v5WM9JnFKFbOxe5UZW2QOVdD6HDYq+2Utqm/JSbN/OZLq8tVJqrqytKiGJhfyr8klGygLtYXpOusQNJporSGVI6b6oi8hGYhXPfuE+m6iXxNeivrW6Kymvs9ZLB2k'
        b'13JW8lsKKxHyfISEvIjlNccGx0f6OoXKSRGbbUNzGbE9GUVmeazMqqjIeceZR15UoFagXiAu0JA6YTUjNKWUWq5QgSi1PFFqOY5Sy3OUWu6u/Cor4F3JOpTaMSyMhdLH'
        b'h19fGwzFbGa8p5N3zIYmJCWFJycmxIcxy97zU1iJfh4MTklJOhi0og4FrbGX8QY9c6kZbcWyyFzvzwwW/FxXu2FocDyjzEkJLDhlOZI4JTiJzt8wJDj+6vPZwxr/7FPS'
        b'1bre2ecyjRcxGnYQzH2cnBgeyu3QnD/lddnGkwSO+NS4kPCkL+1rXgEsfhlPMjGuR0WHRq3hX9yO4oPj1jdqJvD21eVziEqIDSNgXsUNnwqOjwtOuvpUeMTKpSUb8pkk'
        b'loZey4ZU/vXwlKiEMMODEanxoQQe9MyyIB207kDLqw8Njo0NZ3boiAQpc11JE+eBIJXF6bPYhuB1x1kNQ889yZUQxIOGT6eZPAnRXp73eaHa0rFCbEKeHWV1ssoXvM8o'
        b'A0kiPl6Gdrb2Fnu431OJuhAShoUvX9XyWAT6PJSsb4E+GR4RnBqbkryMIitjrXvjxsmG3K8sBuWZxa0RV6SQybaSSMoC/fQlhK0VKUZNSujWSjHGnpz84A91V5NtkkTY'
        b'dUcgTBDAHAxBBS9ZdOOYUCntmvAMky0KBdiqh70mQq4ZRhL0yDGTmdBAXyCCcuGJQHjIRSzon91Br5zlpZ/dlha7sdDK9LQHCUKDvok4efhIih8fNgC1pgoHMFuNS7I/'
        b'prZ5TZgDr254uxyGxWVHdugVeejEIRNOHjqToMIKBB6wPRdknhgpK+A6rpL4MKzGZIeVKAUWdtnnjBVu5iynWnDETBabcUSaDq6DQ1ugFGbNsFpWINRgJVSWoIkb/o/7'
        b'WP1uQZSecVBsxtlkvhLLyAFWSlwQtdUtSNkr0Y3/Y0AUV7Pl2DH5IPfHJ6IEfO+UJW1mOGH51PcEAiWB0m3s4mpuca/EW3Kl013KY4PcVa138EWysSAqiSsB4OOCeVDN'
        b'2Y1P0y5KzZggubIjFyx3MXd1tzxtYSorwBIT5WvwOCyVRRtuwFrb1aLoBjvOxlNqQtIQDPi6rDjlIQsfKtDVjh52MpHno/EqYWbjKm8yiV7VQmiBFizk4CAQimDYDYvd'
        b'ZQ9c4rLmoQA7ubR5f+iB2idp88kwJ4Qu1gaCSUPnsfoIy5rfB/f5xHk+aT4YxrhEfg1cxOwnueswHySER9iL9/k6rb3YZWDGto49KzmpXPI6Ka3T3AChMHKdpa9DOeR7'
        b'LCewk+DYyRUyVYFFHDRbzjaFCmx/JocdK8xNlHhb7QgOxa5UYIiBISEMHYZRbhqYx+pgPoBXz9ttpQBDzjW+uP4Q5ESvrcCgr8/iczt3SNvonHJys3EVYcNlaQEGIwl3'
        b'qAdwMJAzNUE+TnPmJn0c5g5VXh573Cxdtyp5cInIXPkFnMN2rhZBFLRyDS3KjvNt61YVYDhiyr3uAK3WbjBir7c6IBizhNxmrKEO+vhwY6y09VwuviDjz2fz5+CjBDdL'
        b'mJB5klvLZfO7YgU39i0PWhrhpi+Bd9FKbQbj4xw+qaZBDQsh8iapWRwuNDc7hAM4x4ECTlpjgw/pRD02WHnuDGujZyGEtltQy5VP+KU3h1lnJp2DzH8jJ+JrHMFjyPWj'
        b'ndZ4SW5Al0CkzCoa9BFAK3KtE+KwER4lqyal4oQyTqixQJRSnEuhC4gRn4734GCAQLkXi6UPwfRZ7jmcS8bpVGbj6BPjPTp7/tEKI1hYPdx1mMH5lGsKSSqqsoLdYglm'
        b'w4yYA827Ke44lYrTydcI+8rUcMw6KVUs0DIQ74cpyOECm2AhFcqTr6UqckOp4YwCTtCk7PmMy8sLOHpFVgbz6Q1mismAfrWVF9gTBTDOPaUVLnbEx3SObNOHIy+uPHT9'
        b'StDy8rbAqGSXEz7mW548xga5VUOlYJduEk7TCk+JD5oe4p9ZxBn1JyNt98XJFFmBuqwIR7EL63jIHncxUcLZFFqMsoIKifEqd/3OiWDqBgzydzodiXV0p0dw4cwZdqUy'
        b'+FAIVca0VA5QAzb4eOjCFFb5YBk9CGWkwbI2m7NYcop7wpLIY8tTM0BDMk2Bj/fyDGgOZzyTcVaNPhNh3+XTQlN5q1Rm0ieKlLsdS4hCull5uHudO0Ma2QNiK95Srduc'
        b'0cvS0+5YTGQDss8pJJ/V4/BRd6cZqctLbqwiu/CggNUYMeDbDTUrEomcciGK4WZBiOUpEWhAKzRgoxjqPSCbI90ythsFNP1uxS1Bl/4z6ShPz793xVTgSwh9VzvoeLbb'
        b'FQHfVEPw30elP+w+ZiLhuzvUG2fAkACn6K2bgpssFYaLyZPDGVIihyQ2tI50QfppLOEbUU3BApSbyUERzgu4YL1KOe55K2xLwBLaFmYKBNGCaK390f9tKZAkXyVF5+Nf'
        b'vxbnfSie64bQ9NM/f1KeMb/lJ/9d8WdjnU5xuUBWYYe9uX1j3fCP3lTw9npPZmDzm78RGnyWKC/6hv4BRaHGtrFb3zop8fnD4Dsfffjh4PexevCEhZtwU+33t//23Cbz'
        b'vhbzH89X6RY0bPmrnUNX0wPNY3//ptk30l/7TtOus6mDofdel/zJ2PdetpJBQ7bS0NELHwT/+BeJu5bcr3qH/UWlSRD45hmLlGGJs0zSG95WH/zunV/cUL66feem4FDn'
        b'P4Z99/SO3FMK/bvOdWnca99n5BIZITgc+6rTu1o/2HSwT+u978bY//rrkQGZ856pg7cO3isq2q/7I8EGtcvfvPONgnCHmpn+KZv9Sv92VaJt1flq6lupX9tfcv/tAju5'
        b'68O3p3LfMN+/V/cH193TO46EBZg4B6nHWWhZPfjgzYCf/2ZwKm/q6mujh+Z//hvxlQWl//hkoqU498Jxs87a752+Hzb08975no9n9D+6e0un7m/v/Upn6O9NBhqN3/iz'
        b'Q/rm37nemlO84Vv5K4uD26N6fHLP/Mxhw99/ceKVOauP5v8up9IXO9T4nf/6aBTOvZJb9mBCPGZw6duhr9343HJ0x2fufnOXOsxaFmTPfZzkvFD+9t7ug/+5RTv/tw/H'
        b'Fs4aH8z+h49zxFDnRy7ODT8xNYnSNPzLpuSbHd1plu//9Y9On9lP+vy9vXn/2KHA0Fc+9O1NU/vt0tv2J1TmRAfs5k1/ZfHOr4c//cj9m7/aYndT7h933tHX+uT3Wz55'
        b'97Px1Imb9208Fefifqea8lan82/ND34y8WHAL+0+LPrp/fSf/c5n39fSbuoedYD9rw9Hzv3xf77W/533a258fO5dGYUPPd8ZWrr8H3IHG4zt/qDUonL7L/VdXhnCian/'
        b'KRAVm1hyZhtlC3hottYRrXkam8zE0JEKhdIezASrDZwE4QkNvAgxCgNcLBohboGS27J/3Is9Q6JBAZadFBNB79XhQtoy0iGbt/ukWphCltcTuw/2nOOmcFDGTjf30zEm'
        b'T6Ie+72xkzdzN0NlEAvTWxukZ4ULYqiAEijl64M0kPRQvmw8ksFGFkZ4D/k2sPYR0LEqkFAEY9Bty2QNzna0iZ57sGw84ixH166s2I42XeI7Dlvi3EqJOa68HHbZbZfF'
        b'Vi72MRa7Isw8PbBMViDZC3mRQhjAoZt8s95areTV9qSDkGu+F8q4QXWsJavNUdAEi0IiJa2m3Ke4AM34YKUGrmyQ6DxM7oDMKG7KiD1iNzMYJQpK3PimSAEWjKAhkTOz'
        b'QZv2Wb4e8B06E1YSmC8ITLyBr/ZBpKmNzmrZjIflCSyINAsmeDPZ/aMwyEeBEsuuXYkEVZaW9TXHShVWY95KjghcL6kPXcJzUBXF+eBSYSF6OWNJXkEI7f44wgfl5BLn'
        b'6GOteAlISug8PMyJ11sZhYmxDov38+ue1lF2c/ekUceXIy05Tx0WQgcfYtpxDTo4qYt1J+edfC160lrDoddWycAXFJgE3HyKe001dtsTIdcYh0nIvQx53F59YYDrB42D'
        b'tIxVUm68tLwxDB3d+UTIxZoMEnKhPYWvgDO4DydIxj1+eK2Ei/Xe3LSWmLmRCbjJKiviLZSJuFiRqzDPenVIpVssuPSscFsSy8eftkPlbTNLO5g1ceWdkzQLZooTtmM3'
        b'v8J26IlmlYmtvCxEDC4P6ZkqQHkKJxVNX4Kl1cLONZxRwXGhDWRbnRKaY5eMArYEcCBxE6e2uXEXs1WLXY08NotYdLYdh+XhsLBcgBGKrE7vJh1zZLdQsMlJAvegD6Vk'
        b'okNLwtV39NbaR5hDfLFTJH9cjzPsHiW0qSMeCVUwzHFJ0h7mOcC4DmUwL60tIy1oq7VDgXZI9KSO5BqOyHS6QyX/jKUHFrtiPTZ6WNL82CiBVm0+2e6Aaxr3iJc58X96'
        b'eZI0V5FAd5/k6F0CbObp1YChK/wonjCn9WyhUdLcurmhgklbZvUoYcASi/lLUaKrw07SMPmikZ47rnOW7iJzOnNPERQaG0BrAHdjpljozjS5kSQs9VwdJ70ZH/M5f43u'
        b'23BKLc3PSmoBV8ABEYyE3OY/HQvCLLoICxNZ490MbiJFJPE046SJ2j+fIPbEzvu/2P56tRc8OCxsjRf8QyZRfTXTt50y14BalmtRslyfmg8nZlWo9YSaItWVgGN5kYir'
        b'QS2SBhrTT0+1VlEUS4Srv1TF8txIbBZFIW+tludqWUs4I7siV5GHVbpW59agKlQVaXKtV5bbrGzk6vOocsHOqlz9a3XOZ7+OF3TVcUgN9Aq8lX3F/J1kwCzvK4bvpM1r'
        b'jfb/XLVxOX6eJwNzM3KTma7MzRn8t9FPxUrSWpFfyeCfKfhvyxc5XFcdgYn4Lfllf+eT9MpQCS93C2QFq8xeZwQCPpmKt/MrSO38Qs7Sz+z8ogKNAs0CcYFWhJbUyi8p'
        b'lM0R3JFJl2WeWB/BbRnOyi+5K/OkjuXPfUTrWPnPJUoDqtca+Tlzd7DUXLviqH2+6Xz5ibX5VilSy/OqIcylBujQ4Ph1rZIhzMFgyHUWYhbE57sTXsbSznwX685qurw8'
        b'U0Mup4ozii6vgzdx80ti/gpaejxvVl7fym14IiEs3NbeMCQ4iTPL8htOCk9MCk8O58b+ag5o7gClTomnCyut502g4dcPOZbaqpct9cw4/kXG3K9iul2/W9BW3gGd7sv6'
        b'Nki7jzdDDgkgZ18Q21VuooBj7kapLKb1hvOp1ZZSF2Y0lFHEQi+f3XyuOm8xTcd+BShL2s3pr1f3Qg9zWmMP1AiZ1zowkVOAjyuwbowCeeu0DtWKje58t5e6r4f4qISb'
        b'Jkq7vYw+Tj1Ff93vq2YG95mQXIgVPsy85+HO8VAohfvnnwnLXavHi8+pYB9k7uKyzDzk/TVIIpxisaECD83TfDGAUq+/CtRFmWdUrYPCG+01tvAq+JtNx3y5j/9gcUHw'
        b'tsBwi3JQZswBSzUF/mOnrmO8LVd0VfhDkUB9PM7xytDNfQJO2ZbV1waWbU9nz1qcz2MTt5EtJMaVrTZZY6GFqwfWnCWNot2Fkz5PS43gXPckt7MuruauvJCHc1ih4irG'
        b'ei4yLzhGbW0IQTMsvSiGwGz7ctHQgRiocPNSDXyqlr8YszHfl7fsjmMl3FuuPiAU6Ohyxkvowfuc0Xg/jjBr4qrZ98asthrvXnmThPvHCndwaQ93UuqG0krlssev6ica'
        b'SU0ex2L4c4wM8hNMCzrOqBzLTPdXyNmx0mWUs4GbyHD3Zxclf4jkKQFnCoE6W97gkw3FpLUMknQ7JOHEPMhL5WAvBh/sh1YcZ6mLNwQ38BFIO6Y34LR3hiWWCDhTSDSU'
        b'8c1vujAvigm1TvRAKZaQWmUnJKVtMYA/lyktyIW6q26WTxk60zZw9mAlu4NM4C+hK5YWhIUuDWiNNtAekyS3EsiZ/270SKVFjbajcn7Nx20VbT8ee6flULz93g/35h3r'
        b'SswUXMtz3ZY25PndNvdNslUb5MzUX21bgoqf9XecVvuOX0vKO8bfbnGZz8t9z+ntwKN63/9AUfZ/sjX/+Po3jQ7BtrfHeusNP/r6Z1bhu4K/dqLRxs82wcioweRvXv/z'
        b'2uft0zVNj/a+5zLwyWVJvm/la50hkdvvCrLnfqfqIPqFxp+sJH86usXVtN/U/VyatkqLr8/nVm/95ZBWXIrvK9kWN+/94aJp2g/HF7M8Lw/9urvXL9XZ9kf/uB8f/drH'
        b'PRebTWo+f6/wTvdPZ+p/GlljXHh+65xNZOrdSFWH+kumqUO+biVTLb9qujNycXTXksO/fya6ovjp5Mm7b0JQyM4fXA5YNPuxmf432i0vJp2yGNla9rGP8+v7LsceM/6b'
        b'7+Ahn23/7vzqW0P/dfxvVgG9eQd+G6Ue9u0Nb+Q4/eldiWzhq431KU3vRml8YGr39vhHhu/umn37+zX3DjVv+eDgP94c7Dp/VnHOzO6h55/r7T77bOLkvUbRXzX6oyz+'
        b'0a30efKUMH02y6fvF3/Rvvzryz9qylD7+0eBglsNJ20LTXQ4CdtjL7aZueA94+VYExgNxHwuTkMVF7DqSZrijkhOPSUtcYKzaDBnwdkVcwMnYYdAB2ducIUHvKrSGAHV'
        b'SZC9uobGdm0jTlXRS/Z1Ow218IDXYkmHhTpeobMwwkozV8K+huUIlXs4F5nCdW+eC4apZwNIr2AFH0MaCby2tuFOMFOyqqHfZaWpJGbrcorDTZjF3lVNJeGhDtdVEh7S'
        b'qtn8htqEQFjuSNrX8HKLniQH7qPQvU4r3XQESYe5Zjo+tznDiDks4KQZLYdTyzEzSGGzCCp3neTWc/MOKWIzOMbV7ZcW7feDSe4cb+HUWaawz11aq7OTxg7FZ7glHzoB'
        b'7Vh6jmnQcN9daptRsxNfguEoPkmz1eAGp3JhhccNS6KgxCzMZAWboIVpjrUxvOkm7yyOY7E1e59r6CdrIJKoYS63in1HYMnMEx+nr9UQST3EVhjgVMjDlzBPqh3CXBRT'
        b'EJ8oh9htwKl03pCrvko9ZKrhZhxm2uFOfMRdoSc8UpBqh0w1hJzda7VDLeQ7JYXc5tqCWpgw7cwNCnkF7QFM/5PCudb/okb2lFqmvDqcgNPLBhmJ/2p6WYbAUpnTkhSl'
        b'zSXlpRqRHtcViP4ipk9E7Cd1TtNa/pf1EmJ9hFiNU0VOp1rW3tQ5HUqZ6zLE0phUpW0qJVxnIUUu8Il9T9/0dDLBqv1IFStZXqXZvqLmMN1ilSal/q8+XxPJqslMV2bk'
        b'1KndTM1QXu758NXUKVKorFcrVC/a+3L4liJbiJLoKWWKCaOcIHpcwAVdy5D6xDcAEHEKlZipVBHKK+qT5IXqEwuSclwvnHVZfXrSBWAlOpULav0Xh2Lz7yxX3uHfW6c0'
        b'pqXhCT7+hVvKc+J6uMhtpmPRo6d9vA7YWe9hOk1ccAqL3khOYYmaz10CX/LnSSzL08UL+c+/cgaIvCcn6+11MfriDJAkrJOKmTiIk06csJRK5Gp6dYGpGKjhakzBEidr'
        b'bcE2KFwuYcUcyh1xzKcM+bs4p7J+8ublhgFSZzV0XGH+ahyKjo7zzJVJzqKn6os3WRQ7KrL2M+97/eCtD94RF76ibtUpl6iR9Zr6BfUiyx+U/bh0ziU+Jnc0YssnAz8w'
        b'PLotOctOq3in763N7yr3BVfEbq1xi9PVEr+/p01cnfdx7iuOpfs/70pr+nTw7Hf/2Ov/6JHd8a/95hc+GWllIw+Kf/SnsrmBRferP5X5+9/F8UY73jZ4zUSG44P77Mye'
        b'RKe6kroxikXQzOfVNxhh05r8kknWbEB0BxtxiWM1zjhkuVZu2BCCw1yKSR/wqfc02jRMrDFjm+GAlCtilh/fn673PPRcZnIrM5LzBvITV9bkkPxTrGIVJVdN5ZBtDS33'
        b'fBlaniHYuJxvwjcKXqbnjGqnb36K5qyddS3FXUuAVlHcr1adm8gp977iWprKkVNT+tvNlyanRdtXk9MXb42Vp02PTmTmln9JNcvlWnsDz4aWJoVGRadJqx9Jq+muqbe0'
        b'Dr08wVsvYm9y5o7ouMTYcGawCQ/b9lzaKt3M0zWA6M9f1GVFsC51knimsiM4QkQmh/c5EXHCSeh4TvhSiK58dAiMRTeUbpThDs/mT4Msj9v/a29+fe7qdOWES1euicyr'
        b'mqFREbEh5sHxEVEh7tL03P578tf8vEwkKdKGWIMuy6huDMNMP4CycD7fKxhHV9QD0ph59xWOHOJr5RfDfVxcxvNkaFudSlZ5OIUFgFy5Dk04xRB8AkstsHAfzJ1mRpoy'
        b's9Me16S0wQ2G5EhB7834wkZt6sH83S4DVTKHpgdeDk3tGZKuFBFdsao+NcPaHBuztYi4ThVRsxXLL2kBgiaGW8deBrcyBf+1Juvzi9bJak7IeHr6OnmaiDz5/9W/oA7f'
        b'k6IgweybLkdp2E8sSJ0zXHPiFkckuN3wR6H/vy1ef0mSnaRGP6oqSVPf5JUkIkPD1UX21NWVRQbqOkqKQp2NjBILhLvuaAot4zWFhlv51i7tkHXhqRToQ0fdmfdvt7FM'
        b'Whq2p35KU+hqYC2pWNVHErDFWh3ycQ7nN+y3g8xQHJM9SMpyFVTLk152D7O3qkAl5kEHDEPNyZPQpQTVUCzchI9hDh+rQNNBnIZymAwmnBvwVRHhKOTg2JHD8BjGXeCx'
        b'Mz1VgcWsH9sADFvehm53GD18m/TKfjkch0H6erQPeqEb+yKv2ezEpj2YiZ3x0Ia5OEA8uOX2ESiBPuKsE7rO1w576UDJDsw8cSfGFstwEeaiD2P+VeeNW4M3Oh10kwmw'
        b'uWXpBd0BBhZQgzOH4SH2wxRUxsMgVtEwsy4wax9nihU2gViqgn1hOK5Fok0HVGMXfc1jfdAJbD5jGwNloTgiC22kc+cnEEevwjYfHIHx63Gsl9AdmMcGX6jSx66rF7Ee'
        b'evZvwFEXmLdmeiFNVK5xEsZ8IMfYjRYwax+FzQdg7A4OnYUmIQkdzZhNh99K/1ZEEbFphq7rW8RKUAvT2G5jjt04G3VA8TDOQEGoAWQ6x0FuGA3c4AELJqFOCVudsDwa'
        b'H2OLK9YF6MHIDUd8AJN0UeNHZKHxrMk52nkJ1EGe4i5fnNLDTuyi3+Y8oABa/ek46qCBlPYDDjuPGGlr4aQf/aH1lvFFM9YHRV0LC7ASZnyT6a9VqorbcYneGMQJGKPl'
        b'jAuwwTb8EDZdghYbWNDEdtUQDyiPTHHATG9s2AIlgXbyuAQPDLTgQSwsbYL8SHp9OJE06sY9BtgVtt3vwhErrCFIeAB9ycEEdPXY7Kusfyk9/tAtnDa4vBmaPaFL/yKO'
        b'cdFZ9+VpM9MEUc3YdQxL5aHgFD6ypoushyF72uUwrW8OcvzpDiosjhJAFN+ASd1NWEznM48dqnfFuIBFzkZykJtaRlAP+ZdPwT1vRygnqFeGBZzacPsYXW//KcjcAq3Y'
        b'aKG8F0fpeiagTXwK+kKDd5hAZZQESgwzrKD3QGp6lBpL54IuvE8HW5oYdB4WN/hD8zFohgnogZxgbDXFBrNdJDs+gjkxjCtg7SacDZZJxHswfS7g+lFsueMTC0PYQuew'
        b'uJs2McuiluPdDtEQbayhVdYZfxq72h8a9kMjFIQQ5mWJ7D2wGsaZ+XgS78PgnYt3tNT9M0L2Okdiq8bNvRo4QjstIUjOIaTI3kdYVeS81d3o5i6CtAriVsN7CMaHCDYf'
        b'YGEwVsfCAu3pFM5DkRz2OmD1LWhPdXOMxhFjLNjNOrbc3m+ZAflXFHzggd4WVhwO+zUOSBJwKQgnRVh5Qyf4FObClCKU3nWBRswycIbyAMjEvDA1aIf7Xj7nbEI1d+nj'
        b'gKOzorampbXMJttzhEH33LHQh263EQehCwr1oJDISmYw9tnRVc5DNuaJsdqTxIUJQ2z1xGJ/em5KokHQV6xLL1QAo0x5gTbsdKGQxO/p6zf0oWwLzTlCQHX/BsFDQbqG'
        b'POHDVATW4sPbNtpQQ+eYS/czTpRrRj5S1RXb9Un077jgh0OEdnk4t/UyLHq4wRL0KxhBdTLRhD7Itw/HqTgs8odFy43MbnfJC+Y2EcwNYZk3VLu5aly6jjM0Xx8BQ9tF'
        b'yCIMWqKtZdngkJaxj9EGL8iiQ58JwN5YOr77XjBpgg9koDHECDrDsDf1hwSR2nSbPQSSR6CCgSQt+6EZTKfaY+slCQ3bgbnxwdBxTYnwsmHfGXPoUw9yYx1+SnGWDmsB'
        b'GzYRKD2GYtrZJIydhvyLhK5523HRxcHhCDa6QneYuiLmEcj2ElDNQe4OaDZMIxhuEDnAwk2BneVprLmaYkY3N0VqzAiJP48IdaoJ51pCLl6OJ+LRZY4tMXTa8yyespiA'
        b'dRC6oR5rL50isrhkpns+5fIV6PCgFfZgJU7vJuSoOrrd5gaWaivAw9UgSzutP6NP65i5jjme0GehkAHT8RzRrFW9CU1ELfsc3e3St4XCuOet2zriK85QogtZESyok8bo'
        b'I9qUY+dAMNwoFwdl0B8INSp0yQOGKlBzAJtcoCOFHslCtpl2ZE1T+yFTTcTqNE5j7wY5mDuAj/R2EThMwiMbfKx9HbvjN9yURMViJtQRzuZjrRqdVQ/tsA8XYOoM3WeX'
        b'BhYHbI4iaMvBiWPQQ6e+cMmYmNNowA0Dgt7OuCNYGUQsrMEEBq4TUpRa0m10OdoQmWNda4l1Xtp7dR9W7Y7B+3eOq6YDK++SSbDcBVN7DHeHBTMjL84pa2MNPsIcZSx0'
        b'gjYbXwIJ6LxJCyjCit0wA50sdSMdu+Q2GdE5z2OPU4AVPMZWRSdT2nA+0cgO4tstJ2HKOdKb7nIKspMD6EabiCO2w3w6lqRB42W5cKw/EuFsyfH0CrcUYjf5qUQXKumZ'
        b'+sPOuv7YAC1XoViUpgetBN90ggTf0HYhhla5RJr9zgRXJyyKV8Gq8PNym6/gyEZWVAI7rQinu5w0jmEBB9hnaJdDjNbGcwLGAo6Z4azw1JYg6JDDJm9FIUywcN5yQppG'
        b'qEyBSQHRW6MNmLmHzrfR4BaOysEj6Al33g3NJ2BIi7hBsz49Xq6KrXJxBjEEM81qhIyNNib4+JylC7ScvYW1BlDqumU/MYI5RTqax1gidwYGghi2BAsTLzFp6F48juH8'
        b'5fNELhgFHiY6QBJIgh20aB0z89bEsQCoCjoJ2afgkTp2OGdcpHPp2H9LC0p93ANgYCdOZ2w+EURbG6TrGIqjQxmClos3hVjvZAsPfa1vqZ7ALGiBRodQ4svZdMddehqs'
        b'FRn2iGFJA6vP6apvJMZXrA2Vl92DfQl1F23PHowlJK7xhxpLyHHXtiKqEAvDxwj5Cmm1YzFQuwuzTwgxU+YMPAo7DnVO0TDl4AnzUHjc/sSpuxuxicCfKGMvzVkgiCM+'
        b'0IUTstBBeFCkQ/gyScdVga02sAil+oSprTth/g7OXnMgsG0kbleO9YevYZcjUZXMsLM3IN85gVCg4w7U39lAgDUTdhMHIvWwkchgJ5GK4kNYdl7DDgniK7HHmYQjuu1e'
        b'w/20hnv0U/ex/Tec1YkzntwIUz4EiHMwfXMv4f0iDp5gyb9Eckugff8WJpQlQWmEoTEDRqzSPsoRgy5aZia0RUN9iEZ6mge20izThFgNUB1NqxkgoSBHBOWpdPil+rdo'
        b'ey3ERIeIdyb7Q6cltmGPnpeKD7GK/hgd7AzHutN0x304fwnuBdESRx1IGezBQnvIRYbni1h/joYouBKVxpgQZsXp41Qi0ZdJzDNyuqCI45v2OJ3dfNQ1tZwA21A5nMCa'
        b'1r8iQ5jhA2EclpMMceSAGcxZw3iakrG9XBJJsI1Oflh9nPYBHY50w4s07VQSndAsI0D+2yHfFnP2BMM9mrcYxhNvHVHe4gaLdOeTNiHYTo+NEvloyNgKmWZ+LChQcoAI'
        b'YT08NLU7ikOXSUirw4fhOIvlxMYGiUvPIJG1nAwLrNUkuC08fhk6XLHe+xix1srwY9B0zpTkjh6YP0gTlpNE0gELaoTd96BTHQdcoHzPDaxW9dgaGUe0LkuOMKTtlmIg'
        b'jO88eNJd74gKC8+DOlWLzRI6s3uKmvY4vXWXvNgJs7fRMWbuJMDv1dhEXL6cxhy5hDmXodYRiDI5EB8k4kRSAj4KxFZsO3SNCFYd9BM36SFRf5xuSXjGwg9KdsYTn26B'
        b'YS/Wp7Tr0kEodjf3oJPLgaITMZu8nM8yOab48l3oCzHB7FDI1LpliA3Er6ou4mwSQU79WRwKwkILa2gQEZi1u2OBIwEXq5o1EnmZlJJKotxF+np0ytNBWHMIC6A94QDT'
        b'+m0g34Fgpger9gRoR9jZe4VATxA+SLhEZLnjkJriTtv92vq2JkTTp5WxSOukpzFxw6Wd0HqORq1WIcB6HAfF3n6EIY8uQccu6NMOw4l4mrCFtnnvCuFB78XwDXS51TBi'
        b'CWNKdJjF2BAJRVth8nLiFd2jMBhLD41AUwQRiCZxDK0q04fAfdoWKo7AojHx24eYm6GNjwWx2GKG9YFmqW8wWoszRxlMZsVzILlIIHkDh8Lx/k15knlytG7R8WXt2kwC'
        b'7rSBtSbWqJMked473QUqM7buvJUK+cF6ZwKVvYl/d7MvyNlHdL+eSAi9doTJTLfVVWD4Bl3rI2z3O6pEjHIWltSCsBebYojR9stgZirW+YbD4q14+qgl5DIJMqOc7AAk'
        b'O8zDYjTB/lSIHuYlbcXe3QQTXYQ5Q77xWHXbkAhDK5N2o2gBhVcOxukp0RtVRDTq6SxKPAJIyhu843PnfNSN7cqeSAJrN/ZuJ7rdf8nhhiodbQkwrK2EB/GJDpowq5ZC'
        b'GJKVRMJEpb+nrYIRjod4YjbU+9Ajs5Arh4Mq4Vh4ljVkpT8XJEKzGmkpudB2AycDCUzHrc2slM1ciTY1Ras7xdx0IM2pazPh6BhRmpJNuyV0mnXWJGxW6mpDbbzh1lOE'
        b'qcOb8aEzEa0yUk6miR0/Yq0firD62k7s20HK7SDm3oHm3RZE+x7I0XQ52GfrHG57Y9ulCC62ug5yUgkNmhWheg+WX7XFFvedhAlTWhrJIUT7FnDwAg5eJqTp2UYA2Lqf'
        b'5JU5WyjAB4nx0J1CGnghacq61tpEKxuOsmbbh3bQsiujoIwEBhm8f45YZSHBaY3DVZw5p495EqjFsXCa9x7BWrNgx/UjiReSdc7QDU9sNyVkuQdVYSnQ6nADindgkcwl'
        b'LImBpsP07CRMk8jZgEV+xCFKSCpp1XZXhXbXXRleBJ/DOJoeEEuCYoOPw6n9TDEbsodexyTTSyzdByo8YOJWtHYEkZ8mNQLvaQvsPnvbGWucTAkmRnW3Y5aVe8w5Orti'
        b'HDCR5WJJ9m4IdDstIxBaCU5fx2IlIRcxcsbcbDnLB6YcsdaC2AGfnOkjcDMTCYTHBEfYJMRP2rkXCF7asZHF7QuPCqKTsclJj8trM3cgQliCJUKB0JXeJmhuwYpYbqzT'
        b'OH8IS8zpExcBQVM+tu2KTXUWM3NmgQwdUA2WEUo0H1Om8x67q7j1ogLUH/JWC9YiblRlSWDQxSqCMEF9F+aedvKA/BgHHRMiMXPYq59OLKkT2k6rO15kFZOhNQQrSE4h'
        b'3MV2O2ZqIZW76oZl6gkY1GHC3R3oDQ/GAiXoTAomhKmBJQfIPH8W6zzpDulzWnjeKfqxB/oFRFcLzmmS5NZiRVd1z+aCEUFc1mbWxdU0gMatEHjRnHnhRErHiO3W0B3v'
        b'ocXMbYq+DfmWLKvLFyp3kZIwScBwgTZetYtOcgSq7emA8lICPeCxG0F6D/GHEoKpSQPSlnJIIyu0N7kNBbYktz0iEjFOjKADxreRGHwfmg6EH0gTY4VcuBo2ulyFATt8'
        b'kGS2FR9ewaELpzfAgNzt1HCPpEAinlXQo8AsBtBooI9ZdLZDRImyiDD2XbpAY5XSkdYHaMcQxj6kJVTuo932HdmoeF4Z20KDOJWrWYw5NqTBZNLBjCCR0CUbKBXjeICp'
        b'lw3m+RNF6zyE47sIZ/ptzYClWAxA5SESgypoP5lJuqkS4kmVybSHHlg8eZHkyBooNoU2ORyOxkoXqDuKHedImSplKRlyG7AkaFuoyYlNOCwPdUFQl0Q4smiimooDoUlJ'
        b'2Edf1XdUaLlFdn7+pDyOEB2ussXJE863NSLCYGa3CsyqYrsL4VT2fhyxOk1oPQD5yGw6RWqku09D1kZoDSQSAPVHXS54Xkw6f0GX5KBCYuAPdQ9gbZKVLdGIyTQxkYZe'
        b'GLbQgaXUKBzaT0pApakWNusyGk6MrsA6gxB0Zh8JiUXMCmXiGUGMFOasoCWFYKoA5i5CQTynkQ6eJNQdccuAkUDS9droSkdcD3KGlwUxMZj2i5GkRPVCxX7dTXfNSNyc'
        b'9mT6A1ZFwDx2WdO3JVw01IH68GTzFD2Ss4Yc8MEVFcxSwQUhtF0hsbrbN/U+8a5rMKr0tEmG6Oeog+ExtTQc1pHdeB1JW66ArBCiyBNnLmKxq7aOI+krS9CQREeZr6Qt'
        b'cyHQ3ZtoTqXtRgKbehjTx749em7bDsPULVIDCvz1vCxCHeWInT0468fZZia9ttIkzVBjRweyoEgbmIwnctRF3GQxCmdTYdYExqDksBmJ533YGk+/VKTthWZz1nAcKhmY'
        b'dsOEKYxaJ5CM33YQJ8Mu0iHne/jpMgETiUD3nheSoLdAOJ1lQLgz4UzcrU1igP1mRHKnsFvLD+5vJ3paDi3HktxJtG6LJIEz5xgjqxOQdSeWZPpNx4gOduurMYOWO/an'
        b'a55QhMG4y0SBS3ntPzmUoL/y6k5aVjbL275LhOChASHBPdJsod/jiiAGC47HEsVpvXI8kjjCFLaG0wqrU4gB59AbJIjjvdAwGIs9sx+nddXh8Y4LBAiN2tjraMlOxBQH'
        b'dMPxYTTBDBPtB0ldWEjCxSsyh9WxadMerPZKJIpWqoVdmqR21bDow0xYukYyzvRRGNDw2n3U1ojYbgfWBchjp3MCHXrLbuPULSYWMBCtc8ZZUwM7tDJSD6pA/nGRJ4H8'
        b'IMFfEfTdJTrQmernAiUXidBmm8ED7XDCygVCi9k75+OITcZDuRgn6Pdhku8eBqcRuW09ctsfewMsiCg145AJzB+/AiNbd54mmlDD7pju4TGRtSaiDSMatJNFXLp7xp0G'
        b'7dkH1XEbnL1o7keb6EjmT8ADR6LBBYEy24+mEJ6Vc0otlt1JgHs+WLKi1J6n2cugYe9WptcGeCsJYUYTCz1hTNYCRi7K6sAAEgWc3keAMGbvh4tQbBltTyBaxRlLBrdb'
        b'EBFj9rkmDXPII5pGMJoP46QV4OPrXhYmdGNDuODgCAMG0KRmsJHOvxSmwwhZu48eFsCAPpGVwZ3QZI+Z24jUTcKwP7afgxabAKI6BaehNSyAeMKYHxNNurAzIMlYRhx1'
        b'GOutsPcGFlnC5A5fzIm3hp6Y48QXemjH/SSvtjoRvYGH7lhsHkCco8WUsDnXYtv5KOzdv+FCEj72JHirJ96Rt1dbHtpj4mGciFcbzTDuKUdosJToRep6FYFMKfSksyKN'
        b'sLQR+6ygLpWYSYNnDAEUqSsN5irxkKdoeBBH7KOx0VUnDhZgIBVb7OGRYxI20NlV4LjfFljyFRzAXBV5XBLTKvM9NsBDGWYR6baHvkgdF6g/tWmjPWlbxbQlHCGeTTeT'
        b'RyibRTIkIfQ1UjmHtejQm0JCGepERO0mmlomuuQYeU0ZZi5iX4yXZ3TEFRJRJ1VhIZGofTOx3CFFnHSDklBo8DPTBVIusrEsRjkYh32hQutY0OVb2ObqsXkPVlnjxOao'
        b'S1huK2JSK9GhPNKe23HB/cZtOoCSEHXiXZ34eItkJ9RreWN+qL/zleMeToTlpUewLvlAGD7cTjRplG61hLRC2UAiEMNKAQYckWF0u5bOsjF0L0zgzHYTwt5G7L5JSFcO'
        b'47tJ8ynRkCP2OJjov4EmLQnDxTPX6HrKkASESgWY1TxkSVSt7aZWhpoxoRcrNvDYHAsDoW1/HMxu1U89RRJNOF3z2BrIJq12VizSxftYdUwtCXq0ZWOMiejeo71MEEms'
        b'3yN09T3N1KZQfBCKUyqEWDO09U7zQ6pYaXBhs4RAvJmYdylJ78PpdN51e30VzsGoHTb7E3Q3E+V+pMT0cBgyOEenTfo0lOtgno8TE320aLCRwK3Qa4Mjp0yR5BnXzXRA'
        b'Jduh3XIr4WfdYWjZQCfTkkxMpz8cJvwNvAhg6qBZ5L13E3Tr20NmCBRZkeR7hGji1nMmm4hUVEdhjgJMhCdlEOvKgekAO+IrU+GMkJfIpZyxhQHl/XTIFdikF0jH9FAT'
        b'uyI34Kj87nTHw9d04d5+GHO/TZDVS7yvB5v0cTbFFQc0SdKpIDY6H0X8IF3xRBLdYhsNUr39QAr0HJLswZGjRnDfQRFbU3BYPeKyHvRpqF+Dmg1Y6sbaRmRBrbmcjQfd'
        b'KAkadDIPJIYeicf2e8fg6HYiDgOER61B23HJichXA9w77XiEpbMW05WR8E3EqxpmlSKwYB/xZ4LRkhMwvlFBSNRgLvASEb5eupUHNGqexobzLKwduuUhNwry7XHAgpng'
        b'76ZB9YFLyOzjXSRLXzm0iWjKI8iPNiZc69eDTgtC9CaWdUnqdGuQgv4+nNeFBt8DbonOxEPvw30ckdAr2TBlqG1P+kY39DnCoIwBoVMrLO3coE/SbJkpVt7GSnY0Rddh'
        b'Upy46xD9teowdBmfx4fELLFew+iwEbYdgMZwfwKdQqxPIua0eOMiju09fA5yYlOINNZaCuygL/iGdkgInXpsFM5DWQiMXyP5uYrEtzI6rYmDRFnzjOxJI3yIBUkH3SKO'
        b'EGQXYvEtCzrcSWUhAd+gMpON6SKbwpJv3IEHXvRrNzS7k2reDmOJLjh6nmON0zh/+KIDNOwmtkmar/MRnHYl8W1MKWwPyXGNAYQcS3IhJKxlbqcLyUoVEiZBgQOJu4RJ'
        b'WQTQDJUWcd6MiHEjAeesPU7rkajrjzWK0SdgyAhbTlhBlZgYXIcKe+KIejTpigu3Il1cSCDIcT1nb4j56QkkXi9ivyNd/yS0K+CCnVwssZ0hIXb64KOddyCTtL66XU5q'
        b'Sj5YH8Y51UaYhT/jFtTCI2bI6oaH3rRHQpQ+ZiQiObcX+lx0sOmmt/EFK9pdHQ4exqwMUoVmDIg5Fl6C9nMkbs1YyEYl2OjBuIsiYf4wPVhmQwebH0sosKiGHZchj2SC'
        b'cWIu5XuwcpMc7bFXwQJHb0eRBJgfcgNyjxBXLocOMU7qKWCLn56THsHL8G4Z9c344Og5qFQ9Jk9E8xFmOpNAM8RI2j4cZdVB6rDCWjX8DORddNt9ICVGERfVz6cbE4kn'
        b'odwh7gxUEJm28SF1momhU/ZRtwk8ioxhXOOgG6Fwpy48UoRZ/5uxpnh/J9GtOWyBvCv46IYi5p/yIbTIo1u6T1SnihSWbXTYDVvwnrKiOEIXSy7ERF8OtMVmN1XhKR16'
        b'bwSqZKFaQ5fQrQbmYvTvKJ82s8LZLczmSaw7ExY2whzz3PUbbCatrzTk6BES39v20ml0wuhmi3ioct9BaFFOmk9yKjTtpVvIP40zh5VIsJgnyaD1VLoudinflaE9VDtB'
        b's5bCbcK4avqtCpbM4oNuQts20ilzNA94wYwetKrvP6J8HbNdMc8gUA77faE6CtpgiMCo3DuA2UmxP5VZuljuLJHfcWISOdhjiYV3A7cRoyYhyI+evedJ28k+j7PpliSc'
        b'QS/hSw3x6kKlgJDUC4SR7cCYCcmkPXa0t6U7ULsFq8NJ7J65RvAycl2PwGroDhZkQBGRcpI9sv2hQcU99V1WLJhodO8KFhxjNqmK88SGiYDFHDX0VjPCSsKA80a36ONW'
        b'/chQBT3s0T9gRNe7hKORMCznEkRzzJKI1Cuyw9lNsIT9+2OUaEN52JECzPObdeEwVEugXo8o+cJ1bHKDLjH92AePwonb3L9LhLGCkKmWrqJKcQt2u7Kkezr5Uqy+jUsw'
        b'f1gbi+xg3gK7jDywJJY5uE4zI1XYGTqbvF1EUoqUJTgYvpHgfvqmIWH5wz1eCQRwPVo2tLZqax2s37HVBFt2nSJxgXDjBMHConYUzihj86Ft2KtCckTeJcg5gQ+PwZDC'
        b'DaIuNST+1BFl7hYQyD+ShXsGLtCgxCohWKtBp+MeaLIlSSFPz3cD3t+xV1YWC8+ewCIlzD5xhjTieUuSsArscUItEWeslN1soMsWaxwPHqNDmYJmCWF9D5H6/PQgQ3WW'
        b'hvWQCMFDyDIkWB8RklyWkbaHgK3GG/KUOJh4GEjUe+nqLiIHrViQQKfWx8jAjDUJHjURUdB9gKCZ2d1rsFgXp+xIr6mKhEJZ6IoyhPsSGHM4iLNMN8dMP5w9SwRs2v06'
        b'sfTHtrIkWXdD6W7MMaezGdOBrjvQoEFwWbidOZJlbsvaRfrS4LWHVbGepAfZ60wEytHaF08aH0n02UQkqqBPC5tO6t5gIRU+dHjN8OhK2k4YtIAFJ+g2kYEm1mGsxR8G'
        b'rpLWMwLdFoEkABHbtjuYsBceuRpfw66d0OgKfWbWp3BKhnhKw+ltpNbew8k9xOEGGI40+WietCUZe8gSl84ZEW1r8A5SDbzjuzGAYKcQM/e50xyNO45sPXZHQBJm4VUc'
        b'OADFJiLOdgTVMQeSoSx+pYaN0NQK2vnyLlU4sytZFjttkkR84TUXWxMxXyimVl7ixqxKBwThUXRF9zGT731cfBHr3VgtB6G1AJoEdFJZpAKx0eKDSS0qwSKJQHhCEH4V'
        b'65Vhkk+pKmNamdQ8htkRWByJA9Iuy9dIQJh3Y5VjbQQwFE6y2ixOcisIU6RbKXGnl+wFe7eQqJKjxBVlIk1mEKtXquc8IPGtlmjEjHTAUCjWwxITes1LEEoCZhdpdY+4'
        b'pe8jKewBlnhwxrVd2E27H8Mx7iUR4XSZ1CKnSLjYRGdcZMIb8aA6PNjNlcYzEyidZteDpdxwJ4ijZa0Y5XDBkjmgc0yETlwPIi4L7dvHxEF7WFkpQZD71yPOC0zE3J8H'
        b'HUU6r4q4P5u/f+o4X8JnyVocclHMP7t3k46ABZI5caNxKWvRXq5vi5O/RlTr/euf3KkJ8PrJMe28V9LS0uRzc+8E4uNP/qp6OWpT1IDk+1VDOgoDFmq+ooHBqtGf9jt8'
        b'rvD53B9vhOTlF5hW/+rWx3/+uLXp2t20u4eu97+t+krmteg7Rz59N7hvw1W3N/76543bApP/pJE2/cmFDbereo7v7VW/+Om+v1iOWL3/hux75Z/iqwND6Sf+fPRPP3vr'
        b'JOy5/bnv5Z2e2QpX5FwP/8q0tq/2/HuqGZOWx2/nW22/7WQV8v2dzrNFNrXvvrIgu1ClaVowm+fq+9NXFmN+6e/1bYO6mB+eMdH9ldlwzf2dPgEfvLHtm4+KU+s+fmPH'
        b'vz8SGfvGhDW4yqq0nqnwMQ0Y6Nc5vqP5/s6jplanUs942zgdKY2Yrhz9sV+I9yc7flo8+1e9t94+8srv3a97XIffpLq117rt/PGw73ful9q+Pm3+ndnf/PhclLPcgOor'
        b'KcqvJ77x9s2k+r2uLdNysX5ODyLamqtkfmz0MPR8t9Zlo/nb1cOfO97sFSYkhru5hrfaz//HifNePyv+6O7b7d/6xuIHoWNeY/e+d6n7G296JP7KezFN5nXT9kPf/mWF'
        b'SUp69M9+Gva9CqGnfqK7Vd/1uA/+x0NT4fdqOmnWnf917t+3/Pi08nY3m4++ZVCisP1UymcZ05dztinXbFZ9MyrxnfrcxqXFyqXA/GLvsVfzf311T/bZ33enf7It+tNP'
        b'rBNHf3K2NLh1ruVbF6PD+53Tw6vvBaTtsv72J53Kn9xv+PQ7rbD3o0cdzV83f6j8mr/aq5qv31D9w2/ekL1l+48f/6jyh9cWd/7D/Lc25kFVN3VS2xJ/XvGz+IjR/4T9'
        b'tUsFF7wr9k/c//N0WFiJz/f9wabf/K8+H2v7jRfvGw4Vt7yZXhi06dCb39zyx2sdH6HcH7bf/YNcwaYP//bJoV/0bXa+/Z23m9749GLOP/4SGV2XMb9P94dj33s/zPM/'
        b'/rDw6h/eK4p0unVF52Z5+43Xpt8/V/X+51qv/6n1H+6/1P7hRPFPMoSfvnPe6C8XTRS5KivEjDJJXi1x52jM9qNYftOYK0mySwsePxXBDgUSt1T5JLcUFjt4Bar3KO1I'
        b'f06jA+IxrXw2Wwt0uiklqSjg6BYV4vslakmpysSs58QCg3SJPGmI5XxlniySyJSgXpke5Z67jrPXr6nICvSOiYmXPI7hip1YJ0YkpylfS8U5NSiGUjV5FUUcV0uTEZjs'
        b'hXFVCW1mDkdTWDRkIm2rcr1noWx5ZA+JLD4+Bw/PwGO+ZnN+GPFPegxytfhR5bFfZLURm7gRDeM3EP2Wv0arSyb2V7TOgDgji/dOkGZWLeKqhJyFotBna6Yox7CqKXzN'
        b'FDnfZ7ve2P7fhpf+n38zMeBI7f8v3/hm5oGBsQnBYYGBXLx1H30TmIlEIuFeoSGXZKYpkhdLhPJiWRF9iVVlNDU1FdS3qMupy2oqamtJRNqn9bbbZQj2ioQHWeS1RELv'
        b'GmYIzDfuOsl+D7QTyvMx2aF7+Z/OO/C/y+kFbHRUF6uKNdUtMwRGTvxf3UQmIlORGX03k93D/cR9KcuwlLaNq/5PslyJWhYnfYdt50nsts3//VX/n4GYkD8MLoqaHRGr'
        b'PJusyq71jcTVjaJYLs9JK5wgLaKCZJ8iLxyycYciqJATqOqLNyvjQvSPFiXC5E1CgaDB6sG+MmdPsaP6qSFj59ff/IW1ql5upYsoV2G7QY7M+NaJzp8ofWeT2/jUZ5fn'
        b'rPe/Z2iQ3RZxxuIdq0XF/1fctcc0dYXxtrelLS8VmC6KIHE6XuVVERF1KgqW0oIy8DVzV8otXGlva3vrUGE6H0weoqi4iZsOcQ4UVBTwlbHtnGVLtjidJoueLNuyP7Y/'
        b'NGYmy7K5f3a+c4su+2/LEtPk157ecx/nO+f2+77m/n5fV9+K2y823apKH8z85NHs70jX+5dm9Z0ZxP09X3oK9xd0j/7adXMs/G5F0hTXN52drfcqjQU3pC86HW2xuH1b'
        b'c/5ruRvuVU2fXfnL95llmyv3Fx5qevfPeMO6G1VXH3L55bMiltycc2LecPxYcZt3SfBoG/nw9rdb+5vu/X7iszsf3TnUE9+f/bMr7WDsCB78CR02T3z8/OL3du9Jcrdn'
        b'NXNTKh5UT0hofDDzY/XS+B8Nn+/17az4dIWvOfDKDzEp526hXMnXdleKzCdXCvW6h492FMtfbztWualrgBvN+y12z30+1bjh8PqTKYmKAlXPlhwITctQm6eMUWL1qgh0'
        b'UYP7VtcyYpWFJqb91rIsfNyEh2i/MngUfRKos/VUZTFilYDO1CuTAXoQx/GYDf7JobMRwyXwxYwzlYQ7ckGa1KYHHeC3wrQaAxpbyLydiD6YgNsyaehJXUxvhQr3Tk1W'
        b'GF1n0UmaPuOOZBNuqaBZRbtaZczQ0NB3DHczlog5TjUumqWlse5RuxryorXK3heov4JH6E3oIM0clV7RuJWzo5E4xgSnHm+HPaRmVmgFJvgqfE2pdXBZZoXh8BGe7maz'
        b'4H0pFq0qBh/i0LW89YyEMh/1USdakm7PRW/g82a1Sk8dTBg6a2dGTXgBtVhz8vCIme5rDYmHJXEFNNi/qli9YzsesOY04GGzxWJTOkTjc1w2Opsdcnz40gbcBuXo9nN0'
        b'dEfQzpVqdB21F7ORJ6KhTcDbs6VDzYYhmtqq0UDJDGZQoRS3ppnwPiCxR77qUaMrkWsYNaYQdXjTQDCuFE5ooyPXqqY1adHoWrRzI97FQoxpMRV0nvB5tBuEM2xg84gU'
        b'DT5gwVfYhU+nud1AgPZ4c9KTDuEWDboQh7qYf525EV+PwBcn0HhjBI8EUAu+7MPDm2iQEaVSxc/U6o2onx2JTmw0oxS97k4DE6josuvWsOf4Fcm/uHL4NzSk+YZGp+Mx'
        b'NTqGTyXKTE26jya5LVY0mEwneIBmJSDkxUQOyyxoX6bdlBKmKl6ubxRTmb3WoXdQbwS+gIdpTIU7ad5VjE+rwtl5JvPV8Hw0o6bTJLVb16jGp5LxabYUPHhsCmw1gVD2'
        b'ODdoalCriUbNCTKbqu3ojETt3QragnxCqUZlnK2ht0MzPqWo8Z2kC7krrcSE9jam20wZalXkc1y4IyROiPck4m5rGmqpogslgx6C3kX00mPNHD7uQb3MUpmoC+8AMtTR'
        b'zanA04Q5wQdAOW9Ix4pR2+g5LqZBIpYfZ1Xht+egnvFKO8nP/of9f3IPk59BjPG0VLIP/FC0gTHYDewVx/TJDCEOJdC2QJcMtMFiQmphtCcn/XsK2PgrS2FFsUAhlXBu'
        b'QfKXU5dGdHLQ5xaI1i0GZKKtEZ0UaWImES4g+4mueossBIi22ut1E06UZKJz0TCJvvkdUq1AdKLkC8qEc9b5Cef115Awl+iWBdrwOHyE2yr6iM4RcIoi4eqEBtqFHj5c'
        b'DEClW4fkFEiYL1jtFp0kcrnCRrQ56unOkT6/IMuiawvf4HETQ6nXWV8k0os0VpvnChJoQpEoMeDlZdEj0AN5fERbVL6siET5HP6AwNNNQMYmkzzemvw8pVIGXyPWijLR'
        b'O5xOwScHSBQbGC97adQn1RJuja2URATqRJfMC36/10+igpKzziFKQg0vNDiJkecDAjUVz5Noyct7q13BgJOVLCLG8QYdTlACUainIZhi72T/cgjSSgCKAcoAVgHYABYD'
        b'rACYC5ALYAcoAMgBWAgwD2AJwHyAPIBCAAtAJkA2wCKAUgCQLPO/DLAUwAywAMAKUASwDCAfoBxgDkAWawJPbiV8qgR46QnrDxaS8Uk49ce6v4VTbNtjg4uuFMFZl0Em'
        b'8nzocyi6fjw11J7hczjrQREM2KiwTaixpxgYf4/oed7hdvO8smQZw+8+fB+m1Bn1fwXfrB6Pe/9ReZoYFtB5D7qFRdAKQFFbrYZGCP/91qmMYzJ/fwHT0Awv'
    ))))
