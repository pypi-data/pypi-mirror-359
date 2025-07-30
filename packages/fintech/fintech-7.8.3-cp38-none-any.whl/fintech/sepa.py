
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
        b'eJy0vQdcHMf1OD67V+HgQDShfuoc5UCg3pFAlKMJkGwhWXcHe8BJwKErakay+iEhhKzem1UtyerdspyZfG05cZx8nXy/iS/Njn9J3OI4zUlkx/6/md077miSku8fPiw7'
        b's7Pzprx5bd68/RB1+JHB33T4c06Gi4AqUA2q4ARO4DegCt4qOyYXZMc5xzBBblWsR4uVTsN83qoUFOu5dZxVZeXXcxwSlGUopFqverQotCy7JFNXbxfcdVadvVrnqrXq'
        b'Sla4au0Nulm2Bpe1qlbXaKlabKmxGkJDy2ttTl9ZwVpta7A6ddXuhiqXzd7g1FkaBF1VncXphFyXXbfM7lisW2Zz1eooCENo1ciAPiTCXwL8aWg/VsPFgzych/fIPHKP'
        b'wqP0qDxqT4gn1KPxhHnCPVpPhCfS08sT5Yn2xHhiPXGe3p54Tx9PX08/T3/PAM9AzyCPzjPYM8Qz1DPMM9wzwjOyOoGNiHpVQrN8PVqlXxnalLAePYNO8GWoSb8ecWh1'
        b'wmr9szB+bCRkRVWBQ8zBXzr8RdPmydkwlyF9RFGdGu5fXSJDclQylUfmsGqnGbmHQuYKAW8mLXUysrm4YDZpJq3FetKaN6ckRYlGZsvJA3IrTC9z94WS+I5FMOYl48Pj'
        b'8lLIZrK1UIG0ZIusqOl5dww8Jjf64peMJnlecp4CyeUcPtqU5B5IH5zFN8xJ7I3CvMXkLGnV58lRFNkpw3f1K/S8ux8ttFaO1xnTM/JIqzEeHyfbiqGWiMGySQ1T3AMo'
        b'8A3khIE+zyska6EO9lxLXpGNIvfDoI7+UEZN1mQ74fk2gES2cig0D786nseXSTO+5h4GBcaRa/hFDb6xjFyNIDec0PFbjeT6EtwSEY5Q/6Fy1UByRc+5+0DR3slkL2kh'
        b'56YV5JOtMiQjr3H4IL6Mj8FzOv8V81RGfDEBRmKLkWzFm4tpi3BralGKXoly8F6yLlvVRF4dAsXjoXi/2VPJNWgWPmgvKFYgRRNHTuLTuBke96a9ezlCnZSfklyYYuBQ'
        b'WCzZPlEWii8vhqe0X/hGDD6UlJucSDYX0H5pyHby0iqevJKE71ZxHRZYhm/2d1HkDEZN9J8ipyfBo/ckepI8yZ4Uj8GT6knzjPKkV2dIKMs1hwDK8oCynB9leYay3Gpe'
        b'QtkNHVGWNrpfJ5Q1iSjbf5oShSEUGcktD7P3SkEsc4Ke4jHkLnUX5CaMFjO/lxuCIhFKK8lbFlbRv5+YOXSlAsF/3fu5zoKCwhp0DtWFQva0gnj5X6PQ9C+i7wz/hr85'
        b'6nz8KFQXAg/+lb+Puzzot6Foujn9F46ZS/qI2YUj/hKxa9wHffiS97lv4i9zD5EXuQ0Ua6/OigYsaUnFp/Ch2QkJZEtqLmAEPleekF9I2pINeSn5hRxqiAiZMhmfcM+E'
        b'VxqFRKfLsXSJ20lukcvkOrlKbpIr5Aagx+WoCHVYqDYkXIPbcDPemp42On3sqDEZ+Ba+LEf4tfkh5CJ+gA+5cynoTXjvJGNBflFeoZG0wcLdSrYA5m8mrdCchGTFokSD'
        b'PiUJX8Jn8YVSqOEq4POLZDegzh6yk+x6BlA8LTwqrDEIgeioqij207kY7aNusmqZNMF8M0znKhlMMO+fYBmbYH61TJrgmq5okrzTBMuLHHTmbXPeHyl3TqADsyfSaFnw'
        b'+o++c3n7lT2DFQ9ftjz7+u3Ih/Nfv779+J7j622cU1UVTmacTo7bnpsmq1Gi/C93NIT3L+H1Chdtr10th6nYAmMB61UemT2Bw1eex9dcFLcK8TGyI8kAo7Q5mYOhXY+U'
        b'eBufgvfie+xdvAavnZyUkpCbwsvJFXh4gE8he3QuSgkG4tPkdFIKaS0YpcCvrEDKCg6m4Ro+7KJUL0E3jrTk4osI8auK8VFuFt4yWc95+QS9XuagnQ248HB5FDu52mFf'
        b'aW3QVYtcyuC0NlqmemVum0CfO5V0yGaGclGcQ+l7SS/3hjRY6q1O4GhWr9ziqHF6VSaTw91gMnk1JlNVndXS4G40mfR8Ozi4p0vAQefToaAXWl8WhaGlMF6L5JUcz4Wy'
        b'K6NCyU6yKwn6ySEeXyA78D5uJt6Hr8yq4rtAETabYymK8AxJ5NVyP5LIHosktV1RgdBOSBJdxFhLEj432klOcwXQDXIO4TP4NY07Ch4Yl1cZyYHnIZ/TI+IhN+az8k3P'
        b'4l2wnq6lA6nlFEA/K8kJVp5saFpIWkp1ND8bkd1CFes44Mx2fEUDy+c2MDWuF8L3yKvkjDuWosYOfKZfErmDr9BHsxE5iA/UunvBk5DsgUn4ImdQIm4+ImdUjQy2nbzm'
        b'JDvzSdtsSKwEzHuRXGWwi2cDJ9oJc5CMFpNzyfhSjD5EbNRrZUsnwRCTjQgfHkQ2ljWI2RfwsZrnaf4p1OAip7KWs/ZYa2BF34NqyF6E9+M9ZG8iOcKeDFyoJezBLUTW'
        b'4INAXjaSF1mb8MHxU/A9GGJyGI3EF8nhPHLaHUdXH3mJ7CDsyX3g73gbMFOyk70zWt0f34uAB8cQ3oi3kmPRuIW1a5k6n7zEUwmIHMKvaMbig2w0CsjLU8qgopEIVsel'
        b'keNtbqDGaEFuItkJ6JKG1A1p5fgogwo0aMMSsjMdJmkvPMNtyETOlzE+ic9X4LvkmpNcWwpYOAP6cJYbhl8azmhFEKniA6kKFU9qUBN6LnIV18Q1g/DokDdxL/JL5BTX'
        b'2Bpil3O8lzekebmqc1z7kmSLwxs6uc7mdFXZ6xunPutbh0qAokbuabRhF4DgvmwE6cTP6HPJLnwNCO7m4iKyVY9vytLTcYsR7yDXZgMOaMgFhF8ldzX4sg1ftL3Vu0nu'
        b'bKbzh5uGt07S4rTIrGUjB383cqqi5gO5/uMZIb9UD57NXXxu7Xd/p435snBz4biM4gM1y29uyjwrT/rfQ1c+OJQyoLep93cjh7+l/vGbg2sMO7eZa26Psc5e+uNNvf5+'
        b'f2/zsPuHlo2Uhz/8yfmc4znnK/9r966w3W+4L0xzzG64var4m4ULD7zw7c3MX/xNdfLqyDLDVKCadC5C59YnGfRkSzL0FkOLt/EZ+JCSEU28r2A1CCVANI/i+3kFRQqk'
        b'wVd4cpicLhGJ5kXZLNKSDBIbyIrKhWSdgR+6HN93DYZnC/FGcp5xRrIFZDGyGe/W4wv5ChQ9WkZ2vIBPuehsz+ciAkj2KHyV0uyJ+Hwn0qmXd6SlHWZPY22osgtWEyWm'
        b'jIyOoDiSK+fknJrjEfvl+G+UMjXkhEKelo/ktFwYF885IgPILOf0hjbYTU7QBmqtTgdl/g5Kljq3iHfQxeDo5aeutJo8P3W9ExVIXQcz2lOIN1MEKsHr23FIjvqSHfJl'
        b'+BZ58BgyyzhxEJn9P+PFIaKwNX1eFBqW9iMAa56sXK0VRaiygjy0vf97HDKb8/8WvhLNYrnZwyKRLmschxrNyXcNdrHoviGhKKZxvQxFmgtWrNAgttjxGnID387Au/HN'
        b'NACId6LKFHLPtja1TO6cB8+/Wv7+p+ZPzLXVBZa3qxP2fLTm8v6r87YIpfvW95k4OS8+Li1Z+Ej4yJycLrvaZ1J87/S4g5lC6bOl8RX7h2Umb4qZG2k8RMWDO0qBnz+2'
        b'jAkGQ38Wu+7+YT3P2DcITA/Iy8Dbye05wN4l3u4hZxiOK/HR0iRyb7AhLzlRbwCJjWxGKF4nXyhT6bknQ71eVbXWqsWmKodVsLnsDpPExxkWVMQzBNTCFRAtOgDRZFU2'
        b'wauqsrsbXI4VPeMZpcaOWD+e0Vrm+yGcCcKzJMhpsuNjQKRyQQ/C24oN+UBDtxeC3EM2p2JYasDdp+CDSnKanB3dSXnwYxyT/TjAuXbZj2P41rNw3wnfaIuHd8K3ISK+'
        b'9cuLRsPQmtFhyNx/pqxQQi1XAqAWipdxjea6ZwuHo3KWu2CkHEjxP/prp5sLBg+KFBHu60iqCPysMRyZkwdoB4qZt03hKB41FoSWmOv+UpAqZp5cGUPVdoVmunny2vlz'
        b'xcxPZ/dH49Hr0XyJuf+O6mVi5k/CdWg6ajQA+MnH1E4x8//VDUe56EdcxHQzr80IEzNnL9ejEtTYGG42D1k8pEzM/OXCZPQsujwrosTMz5lfLGZm5KpAi8l9Plxnrvu0'
        b'bKaYmTgPVguKz1dEmut6J+aImc2rR6IC9LNhGp25su+KRWJm7wVJqBytKeMjzfyOtAgxUze8D3DV6Vlys3kBanpezPxHhBqUoBIHbzYXfFW3SszcCK/0R18skqeZCxYP'
        b'k0r2aeyLRqPcaFmkecFd4wwx83jSIDQZfTRYmWZekAxDwzInjx5KpcZwJTIPmSeTFKv7QhzIMWioVmeeXF5SI2auKExFC1DJ8vA0M7903mQxsyp2DKpF8QPV082l/6pU'
        b'ipl7ktMBEx4uhJl3/GRSupj56/mjkBlFOpWN5hkfDJiP9MOYvFFBduOtoNVOwWvRKDSKbJ/Pss346IQMOUg05AFKR+mh5BWWjffF4RczeIRbwkAVzpiBr4vZzSDB7csA'
        b'2kBeg36P5ge5KUqS/XjL4AwOkRNkPRqDxuBLIkyyrZFsyQDdER9BY9FYsmUxy7YAr9qcIUODp6NxaByoVEdFKXQy2ZOhQnlkDYzZeHIXJCJauYIcyMbXAPb+GjQBTcDX'
        b'yWUmWRnxIdKCr4FGdwtvRRPRRLKpiAlLZcPJK7BIyI4QNAPNsEwWm3gWnxzt5FEJ3oJmopl4G97LaqnEB8hBkFJAQj8D85NFNpHbrJbV+Dq+7+TQkAqUjbJNtSxTlTLS'
        b'qUAC2YZmoVn49DNMZHuOXEh3yhBZB0OYg3JS81hvkgfMdaoQPkvOAsrn4sP4rihDXpuBbxLanXVkHzC6PNycLdp97pOTM8g1atFpRvkoH+/EO8WWbyGXgOJc41HsRGRE'
        b'RrIjlr0wCCTQ18g1aPox0grYXoDvuFh7BFMFucZR+fEKKkSFM2JYNUZ8PJtcUyCyE+9GRahoNN7HSseWLyTXZEjAa1AxKiaHC1julF5U8FeBqNICi7MkZynrUyFIYts1'
        b'IDSa0Gw0m1zHJ1nhlFV6DUzDkXRUikpBCd/Pcu3DiEcDGLQ9H2hVGd5vFlFiB76SoIFGe/B+WI3lC+JY4THDRmg4hHf3Q3PQHHwTX2W5c/GaaRqgfTA1c9FcciaV5ZJT'
        b'cVM1MoRPketAQJ9RjxVRcytum61RIdKiA8rxrBbvYYV1xROgC4jcWInmoXlkg4sNRi2+GYlbAEf2WVAFLI2L+I5Yyd1x5CRu4ZEWvwjcYX7TiLp/fPvtt8MGMfuHip9u'
        b'Dvvbc4niOjOnj0N1qHaUXGcuvRGfg2yDir/inO/Ck7FtN+rbJhXJMiOzztco14fH/2X+s1OX/ka2fQnXMN28Xfc8t2P4sLic2hFXt2/aKov87FdrZUvCZsSrss6eWD2g'
        b'/P5nV1PCD35VveHe3LEbXtjzQ/eNCvfKI1Ghiy/++OCVWW3uyf3+2ufyW3E///bq4Elbf2ZtW6VN054b/5t9B6KLJnz4ddWBrNT3NJpbi/rvfePUcx9/85t3hu9tcoUl'
        b'jTn631crBq2qKUh8LvG9Hz9//exHnz4431T6cMtxw1dv3lhd/1p14tSMKXMzW9IGjf716R0/j30we9Sn075Gv3ll4rjyWSDlUuthNCDFUdJSWZdcRG1obckcIMh5nryC'
        b't+ODTI8ftXRoUoqDbE/wywglk9ir5B65bAGxDbdlgm5cmJJPzZtR5LaMeEYuYhLGUPxiFoixW2HhXzTmUVOAcjzfpwSvc+ko4yLb+joB4zfU5BaBELIZyrXJUC+yXQbq'
        b'4F3yQK/oUr6QdyUMBEgdWknqcFeZqODLRI46ynGFME4Osi2IHbwk9wb+cv9G3tdKpRyEi3ioMUamBXEmEiRo+t8R5xdoZCDQuKt6kmM4R2+/CBPHBAGfCHMkyBBBpYUF'
        b'i8jtdhGG3IozFNL/zOarJ2sUeGc9vvQY4YXaPVGA8MI9vWWya2FZJQovnyRQMQOEirQVBXcGD5aElx8voEwdqd9PXVynHByDRBPCkUHkdgZ5kOATgMlBcs72wQQN76QW'
        b'wffWb/zUXPH65e3Hd55bf3z9uf2jNo46eDx3yEZ9/MNBhUZLkaXWukN+Jb50X2bykk0Vm7Rv9FUem7in7ljfd8LQD/8WfuztZ/WciwKqWTRPNGIxDLY0pODd5IBPju0B'
        b'mfqKyOR0OdxVLjcIsiaHtdrqAJ1KRKwwOhovIF4NChOTZOMDJl7uhMI9z3wf/8zTF9f5Z35N0MxTy3U/ENev+qc+tVhj0CcWGvQp+aA7peYXGlPyQYECTRS/iLeEkrX4'
        b'Ar72WDwIFmIfjwedbFO+ioPxQFkk2o7O4T3khIYaKKjGfx7Y3/5C3MawwZE4uvT76EegWZlL10weiWbZfrpSzTnHwaNFmSWfmhfQSc/71c4r65dwVaEfznhjyB3tae0b'
        b'1W/EnK7bM+RUzO/Mm7TKyGn71maEI+1WzcjlelBq6EQvB9bdPtNuF5+C7yW5qBVktVaRJCozqsYAdaY3Pi/NV/dYEN9BkQnGgVARB0LUXBzggKNvIAZUPRYD+vkxgL64'
        b'mVYYyTAA/TMIB+jeVRLZTS4HajB+7SUQA1aQewI+F0Ka8fE5j9WcZR0MlI/XnDshAdcNErCJXpZKRew1DhWI2MkgjbHMaXmU+X7kDAGV5ay+Usx8uIqqLI3lGmSuy9ZE'
        b'Idsp/iec0whPeu9Z/qn5M/PDytrqC9aPzGctD6tT0z8yP/v67e2DgSBwD6vzLTvMHwn8u2/rVh9/TjVT5Qwty3hp/MyRMwevyCwpZqpvSWnkYmt/CUtKNdPx+YLCZB4f'
        b'zkZyIwcC642pLrolN0MLHKklmcAKS9QVktaiPHxBjnqXysfi0+SlJ9V8wxusy10mwW01CRaXiCWRIpZEhnIxwCDUMKVaztHfjytyr5wW9YbUWS0CvLXiMSYWyoAdA/24'
        b'QytqC8Cdv3QysmTj13jSQnfm8Obi0NX6QtxazDYkh5Origq8dlKVLGBOFYGoMlFEFTnbM1N4lNVKCV1kzJ4tB3SR+dFFztBFtlre3UYsrVrZCV0UIrrU2jOQUD4Cypij'
        b'di6QdKI3p4CGK39VAcQibNL4mciWN+4R76yEJ5/l/GbA1ivha9LC5L9eWpqW+b9vaa/v6qVwzc6/l191U32wcvbhhS9MPLOxt/K/TugmrBzwWdLJ2tH/NFdF9/7tupyY'
        b'vWd/ceeZ4T9sHbn7i5w/x8wfofp2U823D/oojAeW1v1eNaWsT7+HJ0FMojS6AvShQ9RqB+LSrVQV4vEJbg6+S/YxdCIHyBXOSEfTMkvc4MWnil10TsgxsrbJSFdpC2nN'
        b'G1zMITXZyuMNZB3ezwx9VeRFoJItpDk1hU/Ad5C8kMMPyLpkZkckraDhHSAthc5QfAFkdLyBy8kiB3sSjJTdPuqIo2E11g4o2ldE0T6AnrycyTGhXBjP82o+6mu50jHI'
        b'j6wKiqyAoRT/vMoqt8teHUjlulwdgMQUDR26YMSlle4PQNyP4wIRlxa2w2juMRanANq2I+2gJQI+IQdpYdfK7rnceCRJO3SXF1Ur/hNOFw5/sZ2wdpCItZsmfQ/tgqm9'
        b'PMFuGzraKGLtmpXUXILGXx7v7n8rjRczz5nU4l7s4NqChwOXipnfmjVMNPqRqqYu4fkiMfM3o6IQ3ZnXjaueXLBorJhZPpfaZVDC9HGuBX3iV4qZdydROwLSvZ63xPG9'
        b'TKlOTY6KbQ9/sao6eXacBD3NSe0yAH3+an7oBMmwMsUyFTUBL0TP1KVPzxslWTGSJ6PlAMg8sK7UupQTMw/OnoRc0M7ICHPUD3otEDNzKuNRGtS5ffSSyfO05WJmr4oU'
        b'0NhABIytmfFmvELMvKig5is0fjpXXfB2uGSCeXfadJh1ND6t1uFwc9PEzEujxc3pYyuXJv8+R2r8W8owJlYec9QUzBk5Qcz8KLofAmFGfSy1vukPKyTr1ZVlVI1DkcdG'
        b'LEvfEis1vn/ObHQMAEXGuEInFS4RMz/ItaKHFFBj5YgPQpPFzLW5NehtOnQrVlffyIkTM3ctZmadyPdDzZPf76WTBnkSZW4ofrtmVUFZotSk4rDn0V/pKPWyjtXkScav'
        b'CXUZTK4/NqcxivSXOB6ZxexH6IteQuVqeSayfZoep3AOB3ye+PO0OS/+oJ6khW3UG7958eJPlnzyxhbv7LvZc3Xb16/l/7Z/4j9P/Cp9xqvTR37c//BLuz6J/8PGR0cG'
        b'5k352WDNorhBiWd1b1RezZS712XIN+K1qrdLov66xoHKtbd/l9e74JRMs9D8tweePy5P+mTo8s0HhIhhPzs3L6n0Z+PfX1RaXzku7xcTjgx6/ff/mL4IfW+/pm7C7ker'
        b'dqf/6kcDP/w8an7i2evLnrvy8m3Tzjf+dfb0HyN/fP5s8tvv/tQ+4pe5784e/vnlg8P/J7NyjKaoZOTn1e/s/3rmX6OnVN6Z/eCdyf/1WtabrZvq//fEgpETJ1+MbnCm'
        b'X3a+Pfenv1l96pdHf3pkXOXfHV/8wPsn/F74/n7JXx/OWRH74977n6+2v/Kbf+08cFB3Tc0VvMf/aeu3f9n9w4yPvh+xtNV2gbuulzE1kryG75AzEs/2cWwMU02ZNjmY'
        b'JlLSEw0yY3LCYvxKLghJsFRBx11RK7CNHrxxzqQkeDmRQ/IZeJubI5sX4k368MdQ0sdfeqDTgVZySocrLQ2LTbX2Ohulq4wYzxWJ8QS1DMgx/A1jckMkp2NbM5FMhoji'
        b'w+ShQKSBXoq/sg7/xbvfy/uHATkH5RRIOSinQ/yEHCTUFVaLI4B298BaOMdQP9mmVbwSQLZ/EhNItpPpiF/JJxdFsp0Pmn0L3mYdwrwx2sjmApiiZCWaQq4oye1wfKGT'
        b'TqGQ/jur4WKlvnCoghc0zO7Og8rCC7INIRUyq1yQC4oNaD1XoYB7pXSvhHuVdK+Ce7V0r7bKKTuo5oUQIXSDGnJCPCByVoQyMSXMq8oUBIfV6SyqUga0RS39Mco/lbIU'
        b'0WHI70BUrZYYi7JZDYxFBYxF6WcsKsZYlKtV3YlDlGN1VqUVot1zanS/MoSW4FtoMBqcQ06JjiEjsI1zuuHukVo/YMuVXjgtUi7ovy3eI5zZ8N2smEzFOwmvb1aWtuma'
        b'siMX9Ck982rel79b+qW+cN8nb538SjvH0nR488ok7+4lD2Iiv7rx/trjhW3vXK96+OAHbnf0vra/H0kIG/TXh+b0H73+1uXheH+fwxk7naN+Yf3nN+jh24PKFn6pDxX3'
        b'QLfia/iOMTmV3E4IWFPkVXxMlHyO4hv4RMAm5gQ79nD4CtlFzoqbpJvxgSn+Hdb66fgCn0GuzGJSEecIAUlVNichT6yZ3OOh+N2Z4r7Vi33x2SRDiqjj3SD38Ek+jeyF'
        b'aqkAUz6wD27BbaTNmILbcFvGDBXSxPHEM7tUbNahsUW4pRiWO2lN0uOXqcEQn40Ikbnq09j7+Xgd3sVKJONzcgBwEp9X832KyXkXlVXwOXIgGbekgsBmyCPbiofis8zq'
        b'dUpG1k6DrtOhmUlukiNQxqDPL0whtzOpX1oLT25Fkv2dRXn1E5OUdpKhMpkarMtMJkYoBoqEYpVc2r+NY5tq1E1GKf2ujJAQ2yC9Jy5+tVdWVedk+2egqNpcK7zqRjvd'
        b'6BesXqXT5bBaXd4wd0O77aMnjUTpoL6gDrq5LO7IUVdAh55eEv1Ug1qwvg6gGpv6BlCNTq0MEuw46a+Mvk6XYxNaJK4nrugc51WbpA1DuJc7rXXV7Z4N4pCpJ9dZ6isF'
        b'y9RwqOUvtMaVkT54vkdPBLAGAOo5r8JER8yR4ofiB+VIhYsWXnWAWISeqM5asc4Qk2/8u6034qnqldqqMomz2W2tkV3WGiRLU/MDtRgB8fwP7Ib0h0cdiZ2syFa5bxnv'
        b'pIt71Jfffmqudn1kfhu0/bDq9wtkKPoLHg98qOfY8qRrk7zUvj4ryMtKWJ642SoiNd/lggm3OQNseO3eZC/Ab9zKWB8iBJUS3WJkDurNGID5gQBS/KNIDWpRMHjOKBGz'
        b'16AvtIG43TUIIPP0R68B/DVRNzaTyRtqMonu2HAfZjItcVvqxCds9cASddgbrQ5APbbK2KJrX2qjWWep25vF6ayy1tX51nrH9XqOYptYDIqwLlBl4+90ZKjRX61gCPVt'
        b'VK8wjv3yvOj9S+6Tc3JnQZ4+P8WgRKGLyB18GqjrwJWd5lkj/Xdu5QJ4OFch2yXbFbErEv7Cd0XY+Goe7qRfgW9VCsmUxwc440YCf6VcPgT4tdyqAC6v2oCAp4e08sDp'
        b'FUIoS2tYWgXpMJYOZ2k1pLUsHcHSIZCOZOleLB0K6SiWjmZpDaRjWDqWpcMgHcfSvVk6HFoWCksgXuizQV2hpT0RqDzRt5VjbQ4D2aSf0J/JFhHw7gD6rjVCGAhvyyoi'
        b'Wc8jhEGtvJAimVJkgk4YzPrWC8oPYbCGMlhRkB7G0sNZOlp8e5dql7patksujGiVCQYmhYie9XS0tJ6I6hAhQdCzGmOghkRWQxKrIVaQMYqZCpJOFaOXj0aG6gJ+pFzR'
        b'5T/oiV7pldtASPXKKTJ2hXtFVaqAyafrRetb6PmUdogiUwgdQGlifd7X2mqtRFNUTIBSA01R+WmKmtEU1Wo10BSx+fIP/gk4HdQ8+pPXYHPZLHW2lfSsQq1VZ5E6YwMO'
        b'ZmmooocdOr4ysdHisNTraMcm6rJt8JaDvZo3I7NIZ3foLLr0FJe7sc4KlbAH1XZHvc5e3aki+mMV30+gLyfrZuTN1NMqEjJnziyeU1RuKppTOCO7FB5kFhlNM4uzsvWG'
        b'LqspBzB1FpcLqlpmq6vTVVp1VfaGpbDkrQI9g0GbUWV3ADFptDcItoaaLmthPbC4XfZ6i8tWZamrW2HQZTaI2TanjtmzoT7oj24pjJkAvKxzc6ThoTM+kbWL3vlOlPiG'
        b'F5QW4FfdviyxZfF9KQFjVFackjFq7FhdZkFJbqYuXd+h1i77JELSJdgb6eEUS10XA+gDCt2RIMJd1y1+knp87Fisy5f69+sT2bBYm3j/b9TVyfbe2ZgaVuSmghheT3Y2'
        b'UMNjsoGe/DA+Qx5Uk2YjO58yCJ+Q41fxGtIiOrgNb0P9ORSfVrMo7sz8SuSmfufkFt4CCltLIb5QQpqpKJ5KNsNdcZlYy5xcfDG3qLAw74XKQg5B2RMh5Ca+hA+wKm+M'
        b'Ey1QaXPvN347wIXclFuyEwB0SzjJSH0fC2aTNSty24VxskOPz6GyTBWI87ttopFklHikIW3W/2TdU8SLlpMHK+XMQJQ24s/jDOOzkJtKMQUmZkltr7qZnlCBtqaW5pIt'
        b'BUqyn5xGoEQpyRV8HW9xS+7tF8jL5FiYcwn1oG6DXuCX8WnbvrCDnPNHlKxt/nx426SGGaMis9/88tW2f27IOjE4ydzns7VjS/smvbguy5JQuP7gV0u3//mOZcC8ilcK'
        b'nbOmLms6tXb9D6v//MXeP8xZ99bvGtLKe3+W9+GRd8bUfLj2V+9++tZ/yVY9s2r7wWOeytY/fb+6X/Tov354d9L+wheXZ4+b/5rn8OT6KzuP5HykGvntx59tKfheysYR'
        b'p/eavtx2Y1xe07Bz/yx854+/+Gxd6ohvjn/1cdLvuYqCP7z+Z2fBjD8rHZzRMHPM+TfcHxo/VOJfrF22o+WNOWPv3Hz1ZustXc6ffv3t73flj/zj6/ootnefZZylgWHS'
        b'F7pTEslZcpRsSeVRLPbI1RryCtsIwZvi6NwHuQWQzXgNT15JJheYLkS2ThaMhvzC5DzcStrE40B9Z5Nr+Lq8gdzuy4wry8lpFd2PCyF7/C6Gx3Jc1H5QTa6R8/7dLKgA'
        b'nwtndcSSDTJym5yYxpoq4BO4Ocnnhrgq3L9zh7eDvkWlVlAzr2FoKyB5WxKhB45yyfoMcZ/UCP3bJnoW5OArKtyWTS6J3gvbyDFyWzRQUOxAmtn4MN7Aw1vrGiUNl7SC'
        b'OttCu2aYRxumIAc4cpcc49hz0tYX38UvAewWsQYZOchh2pUD4vNz5GgkfZ3iYzM+BatOQe7y3ERymKmik6ZMUuKzwcooVUTJXnzNRfkq3rESHyKHFVTdbNWzY2LiUItL'
        b'OAlfU5CNhfgOU5krsKciHnCXVlfAQVuOcjBA96LZQ3JibsNEfAEeGgppO2/SI1tb8QEmUteTlxf1TqANLQQiwczr2hrZRAe5xdTtWryp/zxyDN71SX3ambJZS/EuUZ/e'
        b'skBPTq2gbyfDcDO/XS0+K8taRO77dsu0/7ElraM8D+KyDdi9pAHn+kT5UWrmVBrGq5mBTM5p+TAujqemsjBO9G+mHhrKDr88/LK7r5VK0ApFUmzwgSgSJegQURGgHu+O'
        b'6cin5XaQv9vVhCdW6/UqsZLY4NpZnQZ/xUxCnwGXQUFKxocjApWMTk1/Gg1aYaJiULcq4rM+FbEdik9tfjS83C8zUW4G8oWPnSU4rBYhxd5Qt0JvABgywV71NG2Smypt'
        b'Vd02ab6vSY+G0QaAxNUj/CfWxNlgMDG3O8gL/ZCTehaLnr4BG6ABDuqs3C1wix+4IVCm+k/gh0rwF3HS2Ot5WGIWUWUV0bO71gjBQ9GTvPX0TdnAmuIo9i+I7lpR429F'
        b'6pNIav9ZS/Q9tWSRvyUpj5fy/h3kOMeJreiuAfX+BqSVM9UFYAca8XTStOrq2Fnvbtvwn1l/ZMz6JH90opP4OpOqHk6drcNKdVqt9eyMOeg7TCPp9CI9dy6pYWWg9kDP'
        b'st0Ou67EsqLe2uBy6jKhJ52l5QToLnQaXlw61pBuSNP3LE/THwXqbI0v13PszMZkEA+akxiXk6ckT+eA4R7AW2y/feEFORuk0h8c+NT8dmWu5eHvEko/Mj+s/AxSfOXv'
        b'8l6IeSPm9MLfad9YrtS1DWZ+S989FZKRu0EvZ+IWORiLXwEuuo2aroM5Kbn7DJOXyH5DliQukT3AzLf5ZC5RXkokLzF+TW7jtXNJi3Q6G9/XsAPa5Mwg5s2Jb+Ad04ym'
        b'uUxg4RdyqbilrifLmYoarHxHhyRPpxfQ0lAujhpsJU4glRE5pWNMx9razWR0U6sxiIPt0AabgINrBAliOhR8jBcTNSQgD/fEXkw+5PR0woUyq0s0HrjrXDZQnSXa7nZK'
        b'ujKLrOByWBqcloAICZUrOlVE65jIzCgTzYVQBqqCf5Yaq8P8GI2O/nQ2kUruMbFx20Q1rbSqYUSWgNy0/0qkf4yO1hRPtbR2HY2swVds3J8scuYiUecxfGrOB4xNLv3Y'
        b'/JF5UfVnH50QPjHL/1u/9b3k7MThYfrpS6NLTq6fcGTURoq5A1DiHzT7Ng/U8+KOyCZ80qjJIS1+fcKvS+BT+C6TZGflkwNdSbGAw61+SfY5ckjyhXrcjqnT6jL5Zohx'
        b'6kAPK/rL+US+lX18GNXpnSIfMCZlUTTr2eOKlTD4UZkehVwZhMrNgT5XPQB+YtM9CCLa4Fe7pfqbgtnOk6KvwXeIiurC3TuAMUca5kRD7Y1+R5rHuX9J6+wDUEc6m+v8'
        b'S83usNXYGiwuaJ9N6I5TNliXSTR8lGFUF0aR7i1BgmhuYV33OXACIIOu1LrEbXNIIyPAXZVLJ1grbS5nl9YnutChBU57vU/msgH7tNQ57awCsWpxcKutDmf3til3ldii'
        b'mTPygDHblrhpfSCrJFAmrHP4WgWw8lwWypYfTy86e1+qi9w0lMzM5/AeYxHdfictqbMTilJm5/qdRktJc8HsXFmpHp/L0y2sdDhW2xaGxOH9aEZNRD0563Az1Xq3bIlo'
        b'U+mzWrSqBFSA8FWyew4wrd3cEnJD/QxpUYsHG++Tl/CRUSZyLYyjx3QQPkK2h7qp+hIXXQNa9jan1j03l3qtzyHNyXOZU0ALPleem0xV5a15BWQLB6TqpH453jOMnC7n'
        b'EdmNb4WVkBfxAzfdTqxfiC8Emnoa/fXZR5Q8kzJXhUpeoDu3h/vZXv+Fhnc2wDs3PktOefse9RXMnv0CtnOzLJHxa944AbTVwr87+eaawit8q/WfH/WtvO7+as3ld381'
        b'qO7QP4WHKRHP8etu1+4Z3f878nfLlqTMcZ3/3PvXD0bf9fww//wXKc4tqy+ZfnDshd//+nfKT66NOXB2/sL5b+h27zmmDxG3q073WwXE2adXa8idsAaeHCR7SkSWvqcS'
        b'n9MkgvbP6KJbTs5L9HMQviYnlxZNEdV3D9mB11IzyjBy029GOR4nmhmuJ5ErxgAbQpgOvxgpi8W7C9mBY7wbX8UnYAr2abqg0OvwDVFq2JP9DN5b7pcbRKGhBbcxLT/7'
        b'ObedtBth/CYYcg4fYGaepRHDM5TBtgeytYQNAdk7Aq8lL5ObwdaHG3ib5Ez4RE4ylIq2UwrfUdIh7SQ/Wg0avEj2wyTiL6aUHWhxUC1FvjYwwu4nhT1xAllAsXZ28Bxc'
        b'NnPS7hljB2vQP2O6ZQhBjXgahiA3AUnrlg0c97OBUUwba6d3PakgT6kf61kr3N0r5if9rZjUJaGbOWdmR4N/F+2hzkn1Dmu1V+m01TRYBW8IkGi3wwHC/qwqeUBbqf07'
        b'zEcBZ4msqj3cFPJoJFedsOowiXHJmxXAuBTAuOR+xqVgjEu+WiExLhDMP9jfI+MSw2yJwh3jAYEKTfe7TbRPIgfwves/TtD9xgEbAfEt9gqMHs2zUJXOoJtpaaB6k0V6'
        b'VrkIeFmXTIzuaQFfKSsePzZtFNvNojtNAlVTQaXqFrx/4CfqZtVZanTLaq3SXhl0mPa5vYSvU92Bb7C7ugDjsEJHGpwTdZkdpWaz1J0n4IKd9bbQIvd0uF+ROzOYCZJm'
        b'iSLPyYWsUomlcelR9IQmuWYk1/KTp6Lh5KSWHCBHs9xTKBk7TM6PNxpSEvOBzgbW4K85N39OQn4KXgfUujmvoAjEbXJqQBg5OxPfYMI7HpaLtqP3dZzZnF84JwK56WkX'
        b'kJ43AHHsSn7fAf9S8gvLfLssVH5vKQshD1xkr3sSvJuBD5PjpIWVYbbvPMo9kyg/9XHGvuTMbHiWm5xfYMhLSVQi0qIPWzLJxo4Ukf2kDQTxAD6aS3tEgScAIQcJPVmf'
        b'kq9A5MDUleRMCG5tfFYvE7dNjuDmRgZZhuRTOdBaj+LzFqMYr+zoqLgk8XV8iLxaSN239vPPg86xgz1fTFrHJeUXSiPJoeiRMtxmIwdn4g22AX8/glgskC97vzrgnXvh'
        b'JC1MXlJqauHSN3oeRn787putiXdGqYsj75iX5g6u75v/g9jlNRG3SV7i63+Pzpj79bGTlcsHzEu+9HL1y3tLRv38l3/60PVeoabS8/meo4tWH4jeMX/M13sSyv9kLNv6'
        b'vcE/aVLFRtUdX9/wnFdzTXV3VsrS7cPfPHrxUdX8N1p6n/w0YvftpMopHwIbF8PEDH3ByHgbX8kpeo/Cd/B+F/WG7EtOBjHwQO79ipVckuETIpPeUkzWBwgCNGyMhkoC'
        b'/Uay52H4DD5kzCtMJJvxlSVQgxq38HgtPoCPMAbcN5Js6sC+JxkYAz8zhokI8P4JctLoDzHXzMOUnCC32UMVOUL2050RkAJOswMtyjp+yDC3eAIU73Yy79liMSZJMkxJ'
        b'qizBTnbPIDtYCRc5Pp5tD+Bz+MXALQKQyk6KDDTs/8iwr6HMUSIhjMMb2jn8aCULGKH28/dQ6S+MHaehNnz+X6GKldGBjFaqS+LzSpFjU9LhoO7YDmswsw95Ov9euVgT'
        b'q8Tgr5PxwRq4nOkgD/x8SKA80FUzn9g4rqcub9JL3fLhh34+PJgyDiCrjI34+U6g7U8vZ55IPPxxs/RxDmpYcFAC5aDKH/U4FOxVJhPbg3DQzWG2V+GVUQM9pbFdbYd4'
        b'VT4TMrX7MI3ZGx6sz1KxKUCeqmFv+frFpqzX/9HmUXco56DEvQ+dqU1wo+bl8hjxiO+3ch6J0/HtwLEMub5Ryv7N/3JtaBgXFQopMdiOPJSLietYJorTDRLvmadVzLhB'
        b'zoIiUa7nUOhKkOLP8GRb6fBOjC9U+u/8poOnlcBXyAVZhcKGKpSCvEIFf2pBUREiKCtCBVWFZpdil3pX5C6uWrYrUlC38kIxiEoaT2S1jHlIUx+iMGu4oBHCmEeVtpWv'
        b'0EI6gqUjWToC0r1YOoqlI3dprb3EeDwgglE3nwhPr2q1EC3EUK8oqDFqlxbgRgqxrcybm5XrVU39rHpLJaKhTuphRX22Y6AM9bjqK/TboK6IhbZxQn9hANzHCQOFQRtQ'
        b'RW/mQYUq4oUhwlD430d6Y5gwHEr1FUYIIyG3H/OKQhX9hUQhCf4P8CihpmQhBcoM9CC4NwipcD9ISBNGwXMdy0sXMiBvsDBaGAN5Q6SaxwrjIHeoMF6YALnDpNyJwiTI'
        b'HS6lJgtTIDVCSk0VpkFqpJSaLmRCKoFBmCHMhHs9u88SsuE+kd3PEnLgPskTAve5Qh7cJ3vUcJ8vGOE+RSiRbDEyoVAo2hBSYRDkTGid7VVm1jPXrpeDJCZKAMQHoneX'
        b'GMYVhEEaa6/GYaFSoCjCVa3wOxx1cOsJ9hVzQAX1VpetSkcdEi2iObRKlEQhgwqXUKdoWKlbobM3iOJiV+KcnvcqTUstdW6rN8Tka4VXlj2ntOjR5FqXq3FiauqyZcsM'
        b'1qpKg9XtsDda4F+q02VxOVNpuno5iNDtdymCxVa3wrC8vk6v9MpmFpR4ZblzZnlleVmlXll+yTyvzFj6jFc2J+fZWed4r0IErPbBDTKDBe2CNFEazDtDKR1exTdzTfx6'
        b'TuAWy5wDm/hj3HHkTHTxAt/ExyEamLeZbwJkXsUJsiZusdJR0cRRN0Z4izsmo+F8BWUfKBePYtA4tIprUMNzFb1rRvS9JmSSQ62K40D1TUpBzeh+yAemrjSSjp5v0jy3'
        b'O751fKE7OZ+NhKhlWMQ6WE4PtixxyCYy37Ky4pTR6aPGBaKRAMpJXjUV+nXORmuVrdpmFZK7VA1sLqpIACv0+bgxyD4tUURZ0FUctkp3N8rFRPp4olmwVluAx/jRyAza'
        b'iq2qltZuE8cJkFGCAwjWuW8f0zl/FGtrYNtQ7b0ZOdw50ssZvFzax5R5fPwt/DySGdLSivQqb2RHsHTjxFLXWGvxhs6lPcl2OOwOr8LZWGdzOZZQNqdwN8IycTgQsykw'
        b'8YEimGMV6vEwOuPAv/JLFqFy4BgxkrlDx1OBaGWEiABP5wbAdjg51rRuBYq/+Z0AfCD8PgApHZGGTd2KRqvODFNSBSy/zpAl/jebDQ6qpj/Nlqejp2b9wy/n9GOeCF0j'
        b'YidwvA9cpASOruFFvMbvOS9jE+JVW5wm5gXqVVuXN9obQMvttilf+ZtSxTwD3PWVoCfDUEhjoGuss1TRbVeLS1dntThdunS9QTfHaWVoXum21blSbA0wZg4YScFsplhq'
        b'ERa5oSAtEFxL5w3b4HNKHAvx4I++7T+nxDG7fc+bt9T88XlXxGZOI5XNREJjXV5Va2moseocLKvSQjca7OIeLZSy6Bod9qU2uv9auYJmdqqM7uA2WoFnzKSDCh2bYWlY'
        b'zEztTpcdJEdGFhqeiARIy9/XJBNrkpmOrZsteZHAUErkN7HD2FLX2C4272hMdKur1t7Ov5J1ThvQUqka+hrdSg90sO2uj1JFE2lU9YlmibV2sQvYo1Wk0m6nkWx11YHm'
        b'FzebCqHDNHRJHJdZHbA8lwJftFRSn4BuDDFBoiVFJjnqaFPRFrlHIWoOwbvwvqSU3Lxkqvkan6FWCup4t9VYPIccIgcS8pPzUpSoPkpNHpDd5DU31Qis+MpM0CQvkxuz'
        b'E/JTaNThtqQifIOcKE0hp3kUiU+NzlHUjMcbWchT8lqowWmoXl6YT3YvU0ahCLxXZiDbs5gn6VhyFJ8PtF0kFKUkGlNKxXqXqUibUQFCqhrfW0i2ilHaT+EN+CxuHutM'
        b'kIK0K3AbRy5X6MVg7JsdA8twK9k1hx67jyFX51DTRTFHrpOD+MEs0e6xm1xPmkPOOw2F+Qokw/s4vAZvWMXisE8sIy9F4A3OXNGyYcSvyFEvaDG+UED2iCFcm/EGcmYa'
        b'bnYmsFhJilUcuUi28OW25qhZnPNNKKKt/ia2dVLDjNlhWX/46reZUaWD79/fvm1AydC+SS/OUOTFvhc+euGmFOuE5DW/ff/nrZNrtt3oGzlxSG3GT/56uH/KJHXtjRmb'
        b'v1Pmetg4k1Mm5pzfNUDR54WlD1q/F37p7HsTh/5Pn7MrrmZf2Ln0YP/RA/Z+sCDvtOG3mpPpXk1K/2WNP9NqCjNyy5qvH3qz7Z33Ft6Z4Jj22+9Pu3iy8Re369eev9+q'
        b'/ODrN/Wvfqr7fOiAn67/cdTPl0UYfzbu3dtLpvzt+1UXppkjf6/aO6XgaHH66GmrWmP1vdimgomcw5uqV9FZMpIWFZKncPgi2Y4PixsDpzi8NSmlJIzGjkvNJa0yFDZL'
        b'ppxF1onulyfJCXKSbIMRbklNIVs4JE/l8DX8Gr7Cgi5MK8pZiu8k5RcWwJPBHD5MrpDbYjiG+6HlZOcKak4pVCGlnFfjHatEK8kFfJPcHT/SyJoE7/Xm8Ikk3MJsOYvx'
        b'jYl+U850vDbYmnMJX8dbRVeNS6Fke5JBnwhohLeSqwyVIshV2QpynFxj2yFkqxm/RM7Ma7fHHCUnnmVNeB6fceDtzyZJKCgv4vBlcoZsFz1qT5fOoJaWvGQD3lzXK5Uu'
        b'L6hAp5OTm3i320XP6GDPSBiF40XG9gWHW1PF1ZZIXlWQdfnhomvmDXxqHPS0FK+jRhu6SjikEXhycKzRRRe1dmSBsTiFQzys15alXCY5YBK3my6Twzn4iM6YHHiyc1qC'
        b'uJ20I/a5OLLRWGg0FhrI5mSjLyRDIt6mwJcyisWBfkBukJ1TY0lLEb6YrETyLA7fxweMT+EX+e8cjIwVSaIpmAvwPo4oGZJeQFrqCCqakKjDaAxzCqUHKEXzklZ0I5Vy'
        b'qSspO0bZXxJ6ugRS5DtoxY5A/juOoJz4KpMldsDl2w7mo/VBpyV7bAzURcXI7v1mWEgXFggMpAMuIKQLz76t0bPvDD2C879dyQYzReYmnb8RhUEqwACvofzKL49JIgKV'
        b'F5ySiN+ZFUn7CR1kjA4SRdcSRGfGVt5ZWrFQjhjEwH381E4ZPd1MWUFFkc4ts1TVihv09dZ6u2MF2/updjtEnuxk31V5PHPvqEEFS64Bzosui6MG1BVfyR53Txr82yci'
        b'dvh2T3xCFBV9rM5AXf8xMkDXp9PVojfSmCgakePZjJASc1h4znzxaMbScBqiRC1HJeYFrkopHO2Hc2+h5YAxx+L/5djnPpknBjs/EkF2O8PDnycHeMSRbYhcnEKOu+lp'
        b'MbxuMj4bQODmUIbp26zxsdfykmdSyE5yZe4z9KBC6uwA7wEgRysHRk7EGzJsb732EDnPQp22Z08WSuHFa36qHdw0MabXkgt/LZ+7vbFm9sRw255N0SXL7d/hxsfftH30'
        b'q62/qt0QHRMRF/f88B8e7z1pSMYPI3durTzd3PhOa+uuvhtz9qVfjNm2uql+wPP9RtjQmHcrvn9zEt7v/dn12SUf33Suavzfg18kxnzw8y9e/cOCstK2jZ/HTIjbqzy0'
        b'fdUrX+bcvvvHT/589C2Z9r2WQ1/+NjN3wqXIvzg+6PXL32qWbxz/av1FvVaMWHGGrCXrfKHMJqXTLX/8ciFjjUPI1QyjIYUcJPv8okbEXFkdORnNWEQauYDbjHh9WLcs'
        b'AsWIR+lP4+02MRj5CXxSCmtE1gCDpgxxNbk12Eiaa7oh9fgQWcP4yDRTmrEvPt7O61SNovPD1Sh8ManYNt8fR0uDr/LkfEm52MO1USrgOxYW+0gMfIQv4zticIBjpNmc'
        b'tApvDGST7uViwI8tMYMYkyS35lM+GcQlyUa5i7pPk+v4eAQTT/Og1YHjQLYPSOXJVbyFM6Wq8cmhoxnD6k1u41NJbIdFgZRkLT65iB9ItrkYW56dTW4G7L6QjeSS34Hi'
        b'Jr7HuG1sSHFSciE+DsLjVmDuLKR7BN4pc5BTxq6Oyz8pS1NJGgNjYpMDmdhYkX0p2cmGsG95PvQbnld/w8si/8XLKcsKZdEotX6vCC23UitxDanSYB+4VcGcq4dQILxY'
        b'tt39gX5SJwHqcsa186s1yBsYzKkj7E76OKU1TB+n1VJ9HP6o5ayvwLl4uJet5+KggMAHpXznzB/xw22P5MMN6cCdWOu8YaYGu0nSmJ1emaXSKRpYutDdvZEm/2a4aIjM'
        b'531nxHkYOH5lb59NpUO5TtZC/y50AVya2TcX1vOOWU0c6w9aLHNMp/1yJDZxx2g/0HFuFdcQ55IJXBNL05LVMtGGCPdy+t0GxnT5okcj/Sy03uaEZlTVMuYzHGg/NU8x'
        b'zZnewNyxIYi21TfW2apsLpM46E6bvYHNlTekfEWjaJRigyJZoLwKxqm9atGka3d04xWsNTU6rMDBrCZWfjbv84OkEcMA87Q8xUglzPvKWN/ABb3R5eSzYWMRUKkRFIaC'
        b'mkEXcdV8nGiSgQGIEmtLoJ1MFrvqeN4/qdrgVqpNJoDpMJkW0PYxWSjQOCY+6x4No1hLfIgY2AoVRTMY9QDQHfBJZaLH/E3sgJIPstYPmT0KEs7ovdwHOJ7h/zHABIE7'
        b'zq9ig9DELfaD5yaf4x1HkWQwhHu2Dg930QylyVTnMpkqeYl7I5idleH+dtBnT90MPzLyk6c4TlFQp7uBbDWZqruDbO0Csh8HDIFLZ4hvUSzm7TqxDUAWqFzK8ukdM9eJ'
        b'k0Hb0g3SQpOsS0ymRbzPk50haygQzoCG0RKdGua3FIaxIaFAw3w7sSKAboagAbrZGIAC7XAauhqAxw293I8BU3sc+RqYV2c3I1/z78y5ghFZOudTe55zUEBMy7qDbO1i'
        b'tfld3enQ+lZ9u923nWB3XtvUJmYyPd/l2hafBfUzSJQd1mU/e9NtHcTIML+eZ+5udLCTzsnalxsjrL6wIIf9uR2aB+vfIggm02o/G2HqZAANYI+7XAIBmEYbeDxgOG50'
        b'N/SU1LEa13dN6jpDe4LhiO84HCLupTiuUbjXu+62011pMm3qttvscffd1rKGaNo7Th0OHTd76jarsaXrbneGJkMBdIbq2346o3UhRlMgHdOx48zlQubVFtldecBRrfTE'
        b'kVVoxwc2GN2doDGZ6t2AjNt4aWcDMbEtaFRYgSdGBjGsj+PVnkaF1bir61HpDC0IGSYHjoquM1r0849Tvw7jJEU4o0iS2o4k3YyLxmRyOdxWwbbUZNrbgSbzMDpR/gb7'
        b'i/37be7rb3PfrtrMEJtPfXyjw4Cl1dntDtaco120Otrf6vZy/36z4/zNjuuq2SJ5Gv7YVqtYTCGT6UwXDQ5AQntHGiEPbGsJCmbK7W110dbS3W5oV/v9An4Vv0omtVm2'
        b'nrZeJt5VB7bfq4QxAtAgtTMa+10USGh9qgkltF7Fslp7nZX6AddbbA2CtTvpNNRkEus0mS7xvojqrMdhPD3/Hfrtyl7+XvtKdi+RUjlQ5EwaNhkSZ/BJHF1xJxagrcZk'
        b'ut2l+McePQm80KeA12h3mkz3uoTHHnUPL4bBc4mwOD/N2yBuge4Lmo/uoINyZTK91iV09uip+L7jcg+QbA0gwHynS0js0RNDqu4RUghbwBao8LsBsCIDVzd96FiPujCz'
        b'Bq1vukoWI0ekCzRX5hfCCTJBTplMb2jIKro6qCbIN/PHxfUirRJGlhRFH9NKHw1h+8G2hhpdo32ZuKM8Kk30q3A3NtppcKBHfJrBy42CFdPsmzKveonb0uCyrbQGLiav'
        b'CmqqsblAJ7Yub/Spf90aIGAkGHCT6c128qFmsUi1gSMiFRJ5Ex0WfWoHL0LHIqk+Z53dReOOUY87rzbYdA3p6mprlcu2VIxMDSS3zuJ0mUTjrFducjvqHHtpbQfphXpD'
        b'iP6Ifhz1qv1Kv4ZZQ8UdWGZTZ8qvgwacFqnNcXp5iV7O0Ms5enmZXs7Ty0V6uUQvV+iFSV+36OUOvdylF8aE79PLA3r5Dr0QeqG7eY6H9PIWvXyPXr5PL2/Ty098Y6yP'
        b'+v/Hv7GD04gdLm/T/QTqSKGWyRVyXs4F/AJdjIntxnlRQX1rB47kYcrjdTwXqtRqwmRqmVqulmuV4v8wWZhCzf5ojlbNfkMgV/oVP9Z8BO8nO5yEhlV5hVwX/RrV8bwb'
        b'b1zYyadRLv13/qyDT6Mv7mq1nEWBVbOYcCwKLI0MJ8WEYxFfhRCWVrEYcQoWI04lxYQLY+lwlg5hMeIULEacSooJF8nSvVhaw2LEKViMOJUUEy6GpWNZOpzFiFOwGHEq'
        b'5iGpEOJZug9L0zhwfVm6H0tHQro/Sw9gaRr3bSBLD2JpGvdNx9KDWTqaxYVTsLhwNB3D4sIpWFw4mo6F9AiWHsnScZBOYGk9S/dmUeAULAocTcdDOpmlU1i6D6QNLJ3K'
        b'0n0hncbSo1i6H6TTWTqDpftDejRLj2HpAZAey9LjWFr0pqS+kdSbknpFogod84dEFYOZJySqGCJMZ7Q+0xtBT9GUtx9J/eByx40l3+nNgEJSgLoOxahfBnMSqbI0UMpY'
        b'aZVc4Fw2tq3jc+VgkdB8znHUm0PcP7EG7/RI+0vB3htUjQo4P2umdNgiHgQS7FVuqhb4aw6qze7wVWhziZY18VXfds3MzMLyLKkGczeee0GJvGrJFcWiq2R2QKhO3GUL'
        b'PN+bLIL09VXyznQ5rHRAguqzOJkzKG0ccxBZCjVZ6up0bipn1a2gnCfo4HDQy0E8l6p9lOZQw7mzkqMM0BFJmWAf1MwvDnHE+xihixlAj3OrZAIwPZN4lbOrgl2V7Kpi'
        b'VzW7hrBrKIig9L+GpcLYNZxdtYIMrhHsPpJde7FrFLtGs2sMu8ayaxy79mbXeHbtw6592bUfu/Zn1wHsOpBdBwH7lpl0AgfXwSxnSBN/bOhxlIWeWwBir3yVokl+DNbo'
        b'cW475wTa0yTvjVbJG/qyXCXNdQwTVMDmhzfJqV1xldw1Ati+fD0P5Se7RgrqJrloAHYl0PwmxXoZh5Z81gy9W6Rt5li5BS79OmgBkw1Dihw/oGLCGHEBdFouPS8Ixidm'
        b'eTmTlzeZHilMw53DnY+Gd6yk1kLdp9o9sETra6I3rBT4v61e8nBUihuOYrBSmckmeBUmt9XloPFkxPMO3ggx2rn/1Jsji3Io+oFYB7WZO2j0cDHGSQWTD4IPS4IMKO4s'
        b'Q42NbgfItlYAwWQDFTPJuyxepaneWcNAL6YHCBUmq/iPHScM973GPg8GL1XV0l1RFiXX4nI7QUBxWKmt3FJHgyI1VNuhxWxcbdW2KubnDDKJSDP8jy31rvYOeWNMdfYq'
        b'S13w2X0ao7iW7uU6oX1szUI17L8Yu9jb39RhyEGihfUolVXAfb3TGwqNdLic1HubSVdeFcwLnROvNtM3M+JMqJxWl/TA6bQ6aIXsgV4p+hlQU4RXuXgZ/WZ6QAyEJvT4'
        b'CAxsdn9NpcEKJg1GMk+KjmG11J1yuvnlxf+RzFYUxj4+TK9R3MreHUbkqUJDS2aSjxDq3nU0CrQg0aM1viMov2vr5HLmq9CwuP2gZrIYU8Fllw62Uv9CAUi3rXoFEOQA'
        b'QvkUnq5MH5nZU2NjfY19NCI44hbd2K+3u9pP07IgpE94pJfZznN7ghvvhxscaKszWBr19Mmgst4ae4LaL7i3gUG2OoCVQpD+H8XXGuiHq+8ivtZ/AJoNdFlPoAf7Qf88'
        b'UycGnnW6K6XzGsyLncKT3GukME49tosJT2JFbLeSyjqN8BqVU1iYmy4CQxl0Ze151TYrBSgJDlA7FGh3vvHzAqcuURqnxGS4tbnYf18YrkS2L5koxsJKfIp5mtfTYCX4'
        b'B2t055An3eBn5oxnMlPhkv0UAbeAhHzcUzuS/O2YHHTmnkYVsVYGn77v2J6ZpdlZqVnZM8qfYq1Cez7pqT0Gf3tK2ewHsHDJJcvnmd/BV8igy2LhT0TPqLpllhVO6eC5'
        b'rsFaY6Ea+ZOvbWjlpz21Mt3fykQfqvv8nQIaLHFqXULZ3Gcqnm7OPusJ+hg/9JGMuNvti6mEKx6fB8G3sdFOz0WBiOQWD9w/TXQExx96Aj3eDzqi3H/M5alBfN4TiEnB'
        b'FKwe1qylxhqAho21K5zU501XkplXBGu87gmBS7tQf+wJ+NTgoW0HWmevCYapSzCWZs96Osz/oifQmX7Qor9fg5DisqfAv3bGrUvIfjqY0N0/9QQzyw9zQJchHXQJhU8O'
        b'UFo4f+4JYI4f4GDRqRFExAZ6JERaKmKIjZI5pSVPFdLD8ZeegOb7gUYxGsckZul0y1Ohzpc9QSlspwkdKReVs6nfDb1PmFFcbMwryinPfvZJ6abUx7/3BL3ED/2PHaEH'
        b'S/8G3SygETlWaE8DkwudflW8q2DxQLyeyZtVTkO+J+ty5s5M1pWU5hVmFhWXZybraB+M2fP0ycyPZxZFmVqpzu5qyyouhBUkVjcrszCvYJ54XzZnRmCyvDSzqCxzZnle'
        b'MSsLEJh5YJnNSX1bG+ssNJiVGPbjaYbwHz0N4Vz/EA4JIOqiqiQipoUtRosTRvFpiPlfe4I6zw91bMeJEzU6gy6z/UxaXtGsYpiCrKIcSukpKj1V///WU0sW+FvSu5xx'
        b'e1GNhCkUKO7Yn3CtiNFvHV/3BMrUTuOlkCzskKMIyNpuFgrURZ6G0P6zJ+CVwUSvndhRZ28dtWV1wVR8fiZsY2SuBNBZxJzh4tmmIfOyauxP78VjsHQjBP7k6+FqouUV'
        b'zHlOQd80sesxJVxVxzkuoPmPJpWKDtHUouWXcUSRq9221rVIZtCrHb+n3VxMLx2CPTObBI1i4KhHbK+1PSJ0h90jDf2mm1SlVebbggQ9N559lom6Za7s11HhDHin+5mi'
        b'1jWBk/ZOy0WQXU0T3bCwy9p3rjqpt34fmW6PRcZLc+TQ0s3e44hu7ta079JB/7+hfZVTI0WXTnBqyYBhop8tk9xBqFmgq8aIBbvvd0xAY8SYvAInOSUx05evNQpRD+nG'
        b'J6/O2mAyLevQmi6MDKxckX5oVxtYzPjBtpy82g6GrGl+zGlHmjofvnjDg+1YSsmMpZI4N/ukr1cpmbAUogVLzgxYcmq/YrFGvGFBxiulZLuSMzuUtoOVShNopFJK1i11'
        b'u3FLNCxpg41XjmGchD6OEfQugZMG8YkCtTl+AZf/ppYhusOllsk1UelPGStD1V0Mjf8wBkd3/5VPGsMjLFQtUyvcQ6BjOfjKIs3S8MYwfT7ZmlRUYKBu6qTNAhJoYq0C'
        b'X57g7jJGI/1xLkeBG1oCvwGxDxnKBLn/Q4YK6V7JPmoo3qsElaCGsmoPX82JHzCsCBFDc1SEsvC3PA3RAbkaViJCiIT7MKGXEAUlwoVoRjNivNEdsL3ABkq6PKCh8kAa'
        b'QM+7UTpsYm4cJo5uTpv4GhqUQCb4RVY5Uwm8If7PCcNtvV2w1NGPyg3paNakEE2B2yhOn5dHKsd2b32VqH11dCRudNN3jczvTiV95a5/F3Ce/gy8I5rrgfNt8tsLu4T2'
        b'b3xJzjGpJ3geH7ynkVEm91Rjc7c1+iedOkr43EF87eQd9Lu0jindVU1pxZYAftPdZHRN5rvz0ZCGqB1qMJ9lxKk1AGpHnipBZeT8CXhqzeN56vbH91Hiqx0PBvj9bYpQ'
        b'uyOVM8oFoCVXf+b0tVjmHA33zGmK3dM7+WKZY7JLIe6bQVp5TEV9AbmA4w8pgXJvPQ0YUNkeg2Fkh5aODC4u2K3i0XjxSAELDeM7f8eYBEhFh5C0QMVPz0+ld9PohXmb'
        b'0BkCjtbYCNq27yyBJgAEK9qNu5bMIgg7ZQEnCNSSWzY9y9IFf2bDDO90j0WhEhat93uQts9pBwwaCS8eCpjTPl0B61om87tnxrD1ItLyJpSF1nOSkCQr6iQB+1+i5xwo'
        b'HX0ujB7woCLNi/wS5uAtclvekURHt0m8p+vCy7k6YmQEXI7JJHdrJQBYmdJV+112l6UOiBPdlHJOhRtK8+31jVP1nFfmdNd3KS4p2FtHHzc2rFSRXttRVGp3zGFI044v'
        b'7VIFEzKyOGkWHDl+SaOH6CcTodAqmTTowI+V4tcJ1TLqkkJdTlhwAPwiPm7qgkGTa2RzsoFDWXgzOU0uqgrIZezpxKrjpP/ObVwQq4YJZr+yQ4oKGfU5oR4n9EuEQihl'
        b'xPSbg4KWMl6h1yFtBf3WsAKYcpQQDYxYwU7aqmk0LE+Up0+1SogRYiFfaVWxyFfi94lVQjy9F/oIfZlnikrox9L9WToU0gNYeiBLayA9iKV1LB0G6cEsPYSlwyE9lKWH'
        b'sbQW0sNZegRLR4gtqpYJI4UEaEukVVWNrJHr0TauIhKeRUHr9UIiPOkFPeGEJCEZ7qPYfYpggPtoYYIU64vGGGn/ZqMW+hnJehrtifHEeuI8vT3x1bEstlZIRcwu1a44'
        b'Ib2VEyZSKDAaMhZhi8Ybi6XfNxTGwrNJDM44YTzLjxMyGIGe7A2jWOjzlfByJV6uWK/w8jkzvHxetpfPLoP/5V5+Zq5XNiOnyCvLMhq9spwZJV5ZXhnc5ZbCZWbuLK+s'
        b'qBjuSgqgSGkxXMqy6YMKo2MpI0o5eSV6rZefkePls4wOI6VvfB7UnVvq5QvyvHxRsZcvKfDypfC/LNtRzArMrIACc6AxeUEL3xdMnblESJ8sEMN3yf2h1OU9hlIX5YUu'
        b'vqbaOfS3vMidA/ezy1R0AbjI5mIDaS2kQUvbQ5WyCKGGPHZSsSA5r3B2LqyLfHrIk35TdSpZF0GO4g34eqnJtuablZyTxu44mKb91PyJ+eHvEqISLLmWhTF11XWVyZYF'
        b'r//kO9e3j2LfBajtq/w858d6mRjLYDveOkCDzyXnSnEUpuEjqBe5K8MX8QF8kJ0/zSJbDIR+PSvfgg8XGmikgYP8cnJ4lRhooWXJosBvObMvOeMT5CzxlJFLvqOLj9+p'
        b'5n1E2n90UvwdT70YV8YE4lPwF5IV7TvlDgWlTl1+BhbIFSsxwl/MD/kqpVTU981/JFL8/VHQpwK6bEGVOmCWKcjgz2mqGQKFSt8gF1edGOen/XOa6uYQQKoQQCq1H6lC'
        b'GFKpV4d0h1QiJ+mIVP2L2Kcm8JEx+IHRF5UQ0CglxUDj3rKQsXSq55Qswxty8VkZItsas4o0gARtLhasdhU5gLdKr748laEjoGbKXOnsdj5pBRLdZnwmgWx+Rg2IK0f4'
        b'Dr6kCa8nzewI+ZyxSjTZCLKHzpys661GbhbpY9sLOmd4uHR8fGMEuTgHX2XFX2kIQZPTYQ7M5oKXa2Yj9k36rLl4U1C426Cz5HNVaF6ZCq8nrSvI4UUsVi0+8Qy5Z8R3'
        b'p+cVGpNJq55DmiIeOMc2ctuto8/XVENtufTYOdmZkZaGN5iNiFwPH4JvyPBri0ez7xJq8DFyL6mIHkBuLZxDAUkH1hMM5P7zKQmkOTWRBve169XkWkWMGEL/Yn+yzkha'
        b'8gpSlUjZmyd3w7XuWQwrWXBIfGMy2ZtERzwFnuO7vJqsHQud2+ymcS7InqmZSeJ0BELzgZqdQNpCyJpksrkkQWwW3pgrQwPxxnB8a6JK/NAN3mhzLiVX5YjD+1EaMM42'
        b'srM/C6dMWiaRe4GflWyEcuUJMIEtycmFc8Q4/PjqfPG4fnsIS3JSFkbarDoWLYfcqseXfFHryZYCVxV0JDpHRg7jl8zs2wXkFXy+un3YyIvkVkr7pwICekPh8HgLT79t'
        b'80AzhlzER90Ue/EVvCeD7JyNUJ/+aCUqJJci3OyDJWvJ8RDo0JVlS8l1vHkZuVoY51Ki8H483r8YH2dhmfuRM2Szk1x1zaUfKEjIT4HZBwLJYJUm+BsFbcY76acK8c1Q'
        b'FE4us7DK+DC+hdcl0fGA8WlJJW1lCQlAAptTi+jgEE8fGB8R3/AafC4ELcx2D6bv3Zw+WENukutOcmsJbl2GyCZH2BJyE6HeGTK8IWQGG7jVo/Ar7FsrhSmG3AJ5ZpEC'
        b'ReHdMshcR84w1H9OpUD/iARhero5bNmYKOSmcvVIciOWfuNSUSd+5TLRZAszGxXOxUCvTK0n55TmFZHpkYcG2v8UtWP8+ffeki3nUx+GfP7/3g39zh70XtzI38+Y/skv'
        b'vt6wf1Lxb/qsQFPeGfLb0qXFKb/88dgb6twL1l57eUu4afqx6S2VFfm7Cv8QExFzes/VkFKVomJaeq/axXeWPBxZE/6R8P+x9x5gUV1r2/CePcNQhi4iduwMMBQxKvYC'
        b'UoYixV4oAoLSZBjsCiIdLAioqIAFBVGkCNiJz5NeT07KSYymv+nJSTsppvivtfbMMMigJuec9/qv73pDhIG991prr/rU+178rf+ejLd+emHWwaP7E6/NDTuQmzX++3Kv'
        b'GT/Yfvtt0flKj9eTYsdN9Xyz1njI4oVzv30+aZbR1YtmFWWi/OXNY33P1j85/kQDX2q7f/MvI9e/bRfWsq/g6+ee9rL4pepXyZNVv7zkeeb54eeeOzuqe/ZheG6G6qlb'
        b'I4wcmlraJg2zbY169oX4HU/VNOTHPnXlZsystsPLyld1Hikdp5rf9tNLr7zzS3CK+rTvLc/vI6b+88blN2e4RH/5bcpTRY1rbgRM/eeAtLhZiXYo9Zs+u7ts85IP17y0'
        b'u3T2qIPfDgg9OvZDoxAH92cTrn1wof3VVd1Drm323KS03/zZKsW7a9rF7yw+8cvI6ITiDwJ+LtkpP7LH+x0X+RjhbGzHRijvORwnYqk7rz0czzoJ8Ei7Ji7EkrUzdWRQ'
        b'MrjAY/0gENgjZ9mm9gaEhjPjGSIB5YGip6fpIjwEJeuXbrS0MMvADhV2ZlpIObsN4gjsgEoGlAS7sRIqBQygLBFkR8xdhscFYIjOFRI9LogdAh3ESTjIAKEjoQnLyexu'
        b'CnIlIoUcC1nrmnk8GQblwtF9GbucoMQqCzvTsUNNKpYNgkIo4BMxF04yiAdHOBGmhbeAah5PYbsCq4exCpZNhUu92SagBU4zxonaFQxzIhR3xSgpnQS/WYRXxs3AKncB'
        b'u+jKasgjTSsm+wRpu8Q7eYoIWpNkmXQRLDWCGqWW+co6xn3arEyqqRJtoRnPq7LMN6ixywqKodTKxAKy48ywxSqLLETs3LiBvEGwRAqXB2xjjXezh6MuCiwL8hRx0mWi'
        b'iBl4DirhDAN/codduBtL/OE8ET22i4IGLYAiyGaIGktxL1yFEmNoDyW72Dn/YKKH7HWjKOpDoEOyEbPhEhtct8dIZ5Vg/qJQiutOzoEgIvvM4bEKK91Z/1rMxf0aalG2'
        b'D5BdgCJR2AdJLPB0KGuiOpkIT+50ihlx0mie9HvJ6ExsFaChGiDPG0oWr3bXbGVGnCyUJ5PhAlzJZNTBV7EcajSsnqH0ZA7GHEsFERBJ543EegmZwbsWsLLWj4fu++k/'
        b'8foMsQ9eHy0MyRk84sQwvMqCSG8F8NPg9CAHOC7ASbUvSYMSazKd9pIXCQkKZVSyIm4IHpVswH0ogGtg2w7SnpLQnsPEMgIPrxYHz8JaNmGIVHhsMGnFruhQNwWRK5Ri'
        b'MiGLeVL1fjggEJw0PAYHSRGBrgFEViCH2EKTqXysHErZwIQMk2qvQWEonnlMqCeATE5nJyPMWQN1DHtkKVakkhtDXKHI3UkhTme7uhHpkS4jI4pNxla3Go/gAcp2opEu'
        b'WqCOIrTYQrMYS5IcM6lWPJ/07gG6QHqJ6GSi7HXvrbK6kCOmbIwZXEqAWjwNtZlUkIFrRLow8LRkDnkeGrEwSC7lgjhjaHPbyqY4Fntjfi+G3D70uFCUIDDkOi1lr0rW'
        b'xBG8TMaN9DloH5FyO5PtyY7Q7eRgWPT+z5O9MksCE+Ez+orwM81EJpTflZeIHCgMKvlpL3LgzSkiCuOBNRdZ89bkuploCPkbz5ncMxHbsjxAc95MTMRwXqoXukodc1K9'
        b'35hdeeB94rlgUGYNbDTTZFRpY5sl1NyWQSd2xlSqEcrWxGTqwpSlqjWJ8Snx9+OsGD9CdzSaZCSJNIVm0DNbKIRVlEx/ZfbzdSL9PuvqR/l4vhdprOG3+zMsrcZRmvfq'
        b'F59VZzTvXdmfspYzM17qgyzbd3VeaSfGk6JNyBBa56iBP+mFev9ncWhvyaI00VRRD2Dh+V3XEFdD8VdJqp62/WkKUE1MEvNR91c/1eGE+kdEssArGnb1lylxhRAMGiev'
        b'zkxLSOi3VrGuVsbBSu5WkNsdaWpATwgYbQkLpf7TzWABw44PGn+prgHOLCQiKUETA5FCI09Ir8en0tyWuL/GCky6wDxKbzX32wxTXTNYgBYNx1hLUeJ0sYx/iRK49EED'
        b'bq6rckL/AMi9K9arl22uOmTASeSbDltesCNwNN9mu2iL2TZOZ0cQMTsCt0PUnx1Ba+y+Hzmuf5JZD1ZzguhPUMxSJEK1yAASIf2vF1VR7zAPlaMqMU2dHMfYZuMzGC65'
        b'Y8zaGBocYrAsHd/T/OT4GBo05ejDkmfowGrAdFnMoQZiXBNulGQYjFeDPh4dHZmhjo+OFrhw4x2d16elZqatofy4zo7JSbEZMaRwGlamhe3tl5cws88qp0D7mmgDAapQ'
        b'CFfbrBcF9nAY9ujoBTHJKtLCviCBLOuLu+8/UZ/hFocknXe7xauosrHxt5NfRD8Ta5LwHjmwTEbuOS161fgPuYjJGo54A5r6iBr2kxKpqDELOgVznOh+z5EkYW08A0b7'
        b'nrmOdt73NWLL2F7njWpNchTr3h5XCC1Aj7ZW8A718NVuJ69kLdH4we87RrO578z1DlJmdPUnMt1VjdkVm6BUK5nhfhf9V8MqaCc3FIVS7Qk68YCS6WDYgl0WHuOg6T/M'
        b'd6v1ET4Cz6wkhBnrjJVQcb+0SG0vRUHOga5wNlKwKNE/hAYxXqomKJKtNPceBI1JyU/milV0V/rn3/GLaDfbyrrPo1+IdbJ3jgmKoSbjL6M/jU5N+DK6eG1gDJkMQWKu'
        b'yszEpvFnuTiTPrUES6FGW/dJ636EVUFSNcYqhneIOUTnu2KQhgkPTZTghSmwi82zFLy0qM80g4s7mEg7BK4+kk2ZTDuVZtrZG5p2o6gH8xGmHilEECIleuj//RMPanG+'
        b'tulm504yO4f0Ozs/1bcxq2mOnasfdmsmZzzmPPLcdAmhc7N1qMWMTDgl5wUo6/3Yidc2Q7UwcyVWIjhDpm+JYJzMhW68BIfhuvCsxIviNh+HQ0ln39zCsxNm10cu4vfX'
        b'r/VfE0Rmxbr3G+IT1yauTV4buCYkJiRG9N3g9Q7rHCKWfuJh5JXeyXFP+ptuj9un9YvqG977Ry3Q9ThTHQwOlL25mbVki73hgRKGhn/AgOgdwrlkJKz6HYnvrfUF7n7q'
        b'+w+Sr/frLOq73skGbVsXJFbRYTO5nPgFWZsvxCYmmJN1acy9/cqAb3kUTyWbNFVZnYjO/yCVVQkn+2ittVANF/oM3H0RHGyEDO7gTn18IyyUo2fD7odnnJY6qt/xeN/y'
        b'Qd6XvsEi/46UIoiPBsai72EpCYlM2mw0hlfRPx/I+5vSURFDBuIFcgTIRc7fyHskvz4nIXOl938QuvTR8oQYlf4PPlre2H478B3zB2mQBuJK/90eTHg01yeZzYoZ5RIV'
        b'tQj5DDjjEvMpEThWPn5x3/HD1EEp5sa8H3NX/H1yADlrGMpsN1zCbCxxDVDwa/ASJ5kjgg4jj0wawBCphjOPbJ+JgkI22duhigH0uuNuOCugySqknIkz7MWrPOyHeqjt'
        b'ZwDHP3AduPVV04XA2n4HkJY3od8BfPuBA9gTtMv18UIO03Z6Ase8kNTnb870Ba3Xny+wYRJKL99/gVHBYOadHFIwtGBYwjCdh1L2UA9ln9VDY2Hs+oy9a4jAGdGOx7FA'
        b'iSXOcFrrPLOEqsWC64zaS+wtsUiWgR3YYYXXdlBHC7ZlSjlrOMXjFdgNl5gEhNfGQy1zAPmTUQyFcw/2AmH+pkS8IYMOaFbJpcw3GUUOwXMq6r7h8OAM3MdBqbeS+dbW'
        b'QStWYbtaynGUMqCWnKaJUMsIJky2Yq4MO8kQYic5hzs4cmwehvOCs/P6JuhUZZKBha6ZWMhBfgAWsgId4Qq2yWhfYB45hS9wcGgH1rKH5kAVNqooJCMem4zlHBTjruXM'
        b'TbRrjjFn7kiuOEYnN4+axgndVwL1eJ06x0hhC7ART3JQJcZsNe3woQ5qzfuchEPsheK81HStYDXkQTfrLW0nQekKTT9hS2YGXozwd6E2ecFltg8OmW5fgUdZ432WuHhB'
        b'ayru8/KQcCLSG5gNu3Yyz+myFaQPS0an6HlsKXoM8z0vXIKVXoERxtwiPCQlo9kOB5jXDwsnLGJeuAZo9eQ8sQOOCn8/MxYakcaZQancnazQ2hHJP9+7d2+62IgzmfQv'
        b'npsTHeSems4xmnLnSLyg1FWFhf6MpLzMPXCRExaRNkQ4yXHvEv8AKi+VBjNBKXyhAsrxOJlwqRarFgxnxSyMY0bXkiVwBI7r3U3nFJWx3EM1faTviKazqQmummPbdqxS'
        b'R9GmX5FHWZD791tAtoeJEWYvwhop7om0WGA7xGRGOFyF61iDF3zXbjJNGLTBDK9JN5pAsWmoObRgLp7yIAPaNGWrfCQWTnfDaikcnC+H9lmT8LADHJoP1epwUsdEPJpk'
        b'NEGCOZhjwXmaiKFlEbQtx0opFGEBVDrDblLKXtgTOTRpBzRg9lC4vm70UOiCUjL0nQlbcbfY04m0omwktvoMCE6GdrZ/sJlW4jVENMktWcxZR888HBmjIb7ttN6MJevh'
        b'TF/m2x5vqR7zbTN2ydaEmLMCrRMCuH0rGyRcdPS6RV4ZnJpmZkzBSqgwIi9w2JRzNCcfFq9eD+VwDq/gcZEn7IK9Kqyf7kXG40A0dOA5rF40AU8uJ23OHhgJu+KhcC3W'
        b'4SXjRLhmvXm7j5qKPGQgcmGPIXZef0Wgke1AGi8DjXLyP11YTaZwAXKwC69OjJSLGKnMQIdoOgHIqYF7krE2wJXsGWSAB5lIPEZBk7DTXOTMlQY4fOMps0jPvNfn8C2W'
        b'myfhYTwmsPgWYQMc79fd3NvXPGATUXcWk8bR9Wy6Hc65zINyspGJOB72iOb7ZjD4fdIPnbiPnHZY5k86sDRYWAXugQGKcCHMo09IgT/RCtPpBrAwXLGY5zZHWm0mrTmv'
        b'DiPFrV2H5YKrPyBME+6hUSn9g0LZ67qFmWRhZ5h/YHCIqyKEhZPQ9aYLMGA7NJYunR1uA/VubmwS2M/iOYk55e6KTm4lAip5Keo29YPGuUq4DHu1fiATbOGhEA8EsHlO'
        b'9olj2BERKg8WwOwXLTEQxMKRNz8L2WR0y7F0pSM0ke44ApfglP8o6PYf5QUXJBwZnRxbODwzinnlldgSR3bNditTE2yzwvbMtRM3qEWcnUocutRN2FlLIXdHBFwaQrct'
        b'MdnoznFkDpatYIEpeHJxrHIbVMgVTMkOIe1y6i1miLlVjiawywGbhdKyXVIjrJygLBLLKE+RkbOIBlWFs0NkOdlgq2RQAwezLEWkpioyjxOhgelmKyKglvRBAdmML6qw'
        b'3Zjj8bxIgaVT5DZsTngE4A0sCSKPQT42T+XIBApm6F14AerXKnsccLLlPrifx2ZSVw1rUnRyIpmB+XpeYxEcGQH7WLFkUeRZKqV+WueruxQPsvPJT70OS0yxSynA/I8Q'
        b'wQmPcFaeo3OGNj4Ezko4c2uPheKBduQx6p/EXdAmInNezvR9ivEv+EKNOLiAbeMh2ygBrm5nMTyRS8RKngygZjendNSHeKgk8/oGq2ddAHa7aBaMEWe+FlqgRmzltZ61'
        b'G3IWDlRCq3UPt8F8a9bHs9PwGJYosNg7hPkrpav4gXhwHXsnOL52JFnzR8cxz65ksggak4zYlcBQtRJvTBB4s8m7niS7xm5hQE/AddKkEvL9mJZWG5oyNwthRlcWWLlA'
        b'8UBNK8nMpevaiBsFB4xMoc1UTQ0DC8PSSf/nSATVHYrcDfVOCOQY4z6s2ciO3vVEIO1yGapyC3CVk13J1JuH+tAtSfWhL/IqiqvcsOdV34jLqW/Psb6zquaEz1tv+D7n'
        b'5zrSe/+tytmOvsWOAYNPDWlwFN2si3QTjfLZFcaJnCMuOe50VM8ak75/WtQ+q/TKLhdv+aljm79/58idt8adOdwwLiC8zNno6uFq92dfGf1TySBZwcoQr41jnX8JKF8S'
        b'GLf64wOO99qHlITn3Jutuvj3kK/tlFlf1NkYfX8zyU/5s2vHCcclT86bbvfxNwVpyukrlvy4dGHksyvt3s3ueuvt99f82NZSri6ZVua6qrhDdmHrV2/YPFl2ym3altuv'
        b'rh737Mt3Phj02tZb29NffK9CfQ6a1nwYdju3Nc15+kuiCdue+b3x7GsL7P9x+8Mntng/M/69EUsXfze38g/n9+f8Wnn7mV+2Rm45PVH51hSzlnfTw+++FjXO6+Dd+gu/'
        b'T0v1uZPiY5pfdDxtqNsbKQfnfj3vJ6PV89+uX3s7Ke6VFXVFvtOf+bru09+afp+juPPGe28e9xzeXHnn2+HOfp22Y37Fb2PdrYIkvx368M7hV5N3nixu+soi5WRQzPZn'
        b't76VU3Tz01eeHfLmb2bP+UnfXrfWxurzWccmh5vtqducZ7rgWtTg3/2+HvLlx4rg9zzq2juW+7bnxJcqTr5n82HNkv1PLrdfs+fzUae/f9zcYlr3qtJPb3/9o8nqos1r'
        b'Du2+8kvIoMykd4wnHKqKkk6bM/PF7VN/f2L1yH+GTF3wx9vn4qdOf2dz6bc7lwaMOPGhzcykuP+pOj7zi1dXphyN9TmR3Op3J2fp5nbrmXvbBziWD8/c8NWIFzJvvxD0'
        b'kV236dZbBd91PDU89P0NuUs8Kqf6Vh/7bN/0K0+2/r56/A+lNRe21jce/Ud4waaXU+68M/X7C+ceL9201Fva6D7pgwUBx9/Ob8L1MSFLoz5/PGiV3z991t8d1HrQ6Ndz'
        b'GfJxzPGfBLkpUNIrCgILbHmsgvwRLA6ErNYj4UprhSaGZS5WywUOsBwowTYy6RfothxzjoUKrCci93EhdGb2LB2bOo2cwVw7FrDAD1/rYgxNutAIE+jgs2ZDl0BLdgby'
        b'Envtg1C1nOyDRLhiD9t5EmWvBE9Dsf4+OEAuhCmcwcM0BFE/pmc8tvNYr8bDgkpKzvLHXJQ7sFtDRbKOH+GOx4QQhsKBcMMFqlKc3eRYTM4N02VkwcKxWFaxGNqwxsUN'
        b'80zpGeJKtiTYwyuMzFk/riHKaZlSj5nOioikRxaLk03ghMAq1gTdY6AEOjJZgN3e0B5pVcqNVEqw5rENQlhSN1zDYlLPWbgstEIK53gvF2hlwS9jscrKRQEV23WBPYph'
        b'eEoIszklH6uCMpMNFtimopF3ViYW94fYYI4JdkjhxpbJLJICmk0SXeAAXu5tsbUNEEMd7p0h3HMtTa7Ek+RLYycOZSNugwViKA0ZLsSPXBxGRFVKb++uYHSFxpxVenqo'
        b'OBELRws31MkxxyXUlRyLJeyyDG9Yz+LJsXXDmvX9oGCFknRZS2+pwhpLhFGrwGt4WWk+tOecICpZi0BXc4r0aLEsluiGPbHQmlgvctbuEoa2meh71bSFZ6BEFygzSDpF'
        b'CPcoC5nX2xYxd4vWGtEr2mM65rE6ZxJRvZqum54go6GbdWFG4iWZ45g+ibtcoMQosSfupXfQC17Aeja1bE3tXdzkgVrOOit1OmaL0yYEsgnhhPuJ1lkSTDnm6NvLUuG4'
        b'HY9HRipY15BzOAJL1sGenlMNTsEhodtyty/HEglc0jv94ehCVqfl2CW9j38in4sHLh/Nmm6HdTKDp/9szBEO/xKoZYFSkWuXkrYp3EK8sEEXXGSP+RJbLMDjzNITAhdH'
        b'9rH0bIOyBwTj1GId1LH9Z8xE2KdMsg0KINtPuMiZ6K7dQtDTXuu1SrIiL/bi0BscLjf/d6Ji5MP+i2ixf/5bj7nd6j5kTGbKojBFfUxZE6nx1YQxxFgzbiLpPZ7+46V/'
        b'sH9ic56m9FBIOQEIzp7cS+/kRfw9iZgCzVHccolISjlmGBCxpfCPlEs/2ZJPNLrHlhH7WdMoH1KGuYbQj/wkV2iqFCmNN9dED1myyCCJmMYNmfEmPEW8pV89CLk8KYtn'
        b'P4UvqYj/WmpPuW7MNeUK6YA6M9p9HSKY/YRwISGUh6V3udJvHixSKH5TT2xBT7ZUj/th4P/auMpN9Fo4S9vCjAJdo1x1EUfM1phPfnXu19b45rxetIUP6iS5iCWLhTzE'
        b'/0k9oCKGAPxo/k8tn/FbvIFIgbkJmZSaMCY5mWGc6lH/ksYl0VbFJPeCPhXgseLiBPy/GMfU+I19ChXiTpyioxemZAakJkRHO8Ymp61ZL3fTwNRqYw/UqvgEdTINANic'
        b'pnbcGCPwJcYlUYrDvrTE+o1ISmU3JrCsfU2WZrxKSN0UMAkdKbqSY1Kc6tHZCCnYwDTHABYDQOahKolCwZJ6aDxAjOMatSozLUUoVvdqAXHR0XIKTtNv2ATpH21/0I9J'
        b'qY5ZU9wo6/U80o0baWdmJsZk6lrbE5lhsETNuzF8WhZaJMQ/kAIoWm2vLtImwa7NSFOnM9A6gyWSV89MWqNOjskQIjw0RPUChoLK0YmmoruSLiDVMoiTzenk1/jMNW5y'
        b'Ngj9RHjQDs2M146LZtxZ5Ffq/bSTmtGPS2MpuOkU2dhQmb0G4CG0jSLOEG2jmWAiJwdwXSBlwO3AYz0m8gNJgomcwhuQg781VT8VAZvD9VMRXKerg+lt9XBytZFgMnQ0'
        b'EVO75JUNHlgxZIT/gHEbtuOFcMiD8/OhYsW8gExowuPQYjIzxHU4HsW6lUQKP+oDV0dugbPWHnhNJJBHbgvgzAeMFnHR0WYXZ0s5NY3NhWxoWhFphiVEnY6g1M17aUYL'
        b'TRYy5kavk2DT8Cz2sDNnxDWMHsDyHkbPCeGSFlQMFatoNt/+junjnrtqk+th7ftKl8uoWUaXTKa8t9vNcfSozfv9HeYmTnjq5t/zXms8POqq6uPqBXHHF5bI1Tvm/PSU'
        b'bXjakMdmbvTbWbnzvX0XHDrfWdlsFvuM+qbp/CFffTd/qWJW2VZMr/3C59BL5xv9vlzaXXdoeuycX38V5y8fenVeqVwmyPy1QXhNo8PgObleMDdUjsxkxpHc7ZivjcIn'
        b'CsLpucNXZjIbaQNUzySiSYbbI4cJ127GRkEszg6BChU1oCoY3bXlDGpEssF9YmiZB1eZ1Gk2Dq64hHhgWS9NJ44IrnSe2EM3NLoolrrqwtzxHO7GGoG8kZIL9wS5D4Wy'
        b'BXgKzgjJAwVQPpkoAR1Q3qMFYLEmccHFExs0mQvRW/XVryFE2qSzD9oxn2gZvaTXwInWuiD5gu0sRD0VrlMPnUHhFXbBHjIx0/CIxtP20JgOU5p0x1YrE12cDYkuO7mp'
        b'TGCh0Pn3yHcxFUyoQHKfT19XVG96Rffe53kfTkheuKPnXC0iv56k56qjoXM1m3vXtv+4Al0baOgmOWaiyDnTC5JAm5PaX9CfuFD8wIxUMQsykLz/s8TAoRoRn6qBKe2N'
        b'ja5WCYdsPNvmyJ7sOy9gfoQe3nl/J1N8bNIaVdSa5CRSisCVqwV2SqBAjWsS3dgdbr70+3x2W38w6nqlavplGgsVdNXFClJYX1U8a2ZaRhz9A9nzDe7JGlj4ftvgtmBR'
        b'UDSDdlOnJ6fFxGnfXtshBgul2KE6qDZ6XGiiZ1XqpEwBnF3XKMMnxUNbNX9+ZLTrX3100V9+NGDhX3107tLlf7lWH5+//ui8v/roUt+Jf/1Rr2jHfuSpR3h4Uj/RmgEJ'
        b'Al2MIN3Ex7k6Omumv3OvkM/eMaksWM2wONJfpOmCjBiGkN0zh/9MUOkSKsAKu0KWl5tHr9XCgmEFXFphOZEKs5Ji/lpPzYtcZKAJPVzadI8R2iEst6S4h8hcEk6P/FUn'
        b'cw0QqLJ/sJdy5j75Ypq9fHWlB6e2IX+0njFuplolo775Og4OJ6YKmbecMbZ7YO5EDw8jjg/gsIactVeFrOAz03E3VGGrS4gb9dhViZRwZgrzLCyAQjwciwUuIYFEtYVd'
        b'oqnzsEpwYZSvG40dUpcQaqKAQtEMPzgnlzAnxqQozKVeK3MsscI2I048RDTTA/aza2FmU8mllsnkTMcucsZjpWgUZFsK3pzLW6E+CXarJpIDTpTGQdf4BKGBhXBquwo7'
        b'FZhnRc4wHk+LnONjWALqFmyawNzv2BxG3e/nNrGiFg4hYuhlc01cAYspMJPzrAVQHgp1tHmWK3Wtc8GL7NrqnWto6/DAHL3W5W3SxibWYicpMQjbdK2AWnchiKIW2qZB'
        b'/mS9pmOTXCw8WAv73WiFcHitrsYovMocZ1jlR8QoWmcXdvZUOmk8ew1vvDhbluU93pSMvNhU5A65mM3CDobhEX+ZxdBNFKpF7CqaPQhLWTtMYqCNlHZxxRCZpYgTm4tm'
        b'4/kINQW8DnbFUiUVbyNYhC116RJ5lzqIyrcRebqUzIBrUAFHI8kv1Ox4CsuJQF0B12zHwEUjrIw1siDfgiEPS2c4DiBSoa0VNJD7CpIcvnrCSEWhNPMdJi362/SQJzys'
        b'pe8d3jD5yJdeMlvb4QPPvGefNPXxxBKHyy1OnelOm/xPn6w7lT7NMqehodGbO1P3QWjbk823S7t/mVk1/PLx/MqK2o+OLi8+ESfbaeP/5HPtPmH/+tYtfMy6c9+GeJ0r'
        b'+nja9ufLi27HDe8a9ua7ifvHv/lJThd/4JmkW2HrR9eP9vc49tpHN55u3PHJjYWVDbN+HTyt/fJO37bS2xuCc198ZXvBi5bJol+zX/RTbcx123B30Otwr67r9ify8z82'
        b'fjGqo+27eX9Y3Zh16FJ+24W617+98zflpx//nPXpwB/iXns74vzdKT/dmbNCtcBq297uc43bfjPOb1r19vGrcoHxPHgJtuis99MgjxrweWxOW8+k2il4dQmRz2OX6Jnu'
        b'12EJs3NOg+NKF10IMu6PF3PmrmJjPGPOhHgxnpqP+/CQVo6fOwuOMjEaymnshAs0wp5Imospgd0izA2IYBejoWMezVZVY5M2YVUErekp7OI2rNqJ7aEuvR0RU2wFO3wN'
        b'mSMHYyHPhZr0qdhrgiU85Cjk2lobsSkKu1Uy7KBO4BIOySwIYEZ6PBY0D86roCT9MQqdUEAWXirksEsjFRLMxuv0kpRcIvNuPzatEFwqeeFx013pFVpeEYflC6CRqTjT'
        b'zYiOJqSAOmKOLgtU7ENacYL1DlyGOt+Rc1XMIQ2nOTwS5y005aAErjrOVEEpFNK27OPwot86dgla8OIMojqQh4zIQ2c4Ms2vzBK0j9OQzS+GarLIzYm2C83kleD6MtZM'
        b'Bzmeg7r1qqwNtKpDHJZOx0pBz2oMsIbSReQKqQmqOCw2H8WMxKIV3nqaEtOT4CTUMF1pRHI/iY4PCD6WqIj8y/SIWMN6RDTVG6jZkaYk8vekRJ+QMIOoYMzkmVah/TJn'
        b'iYhmvNbQqPtHniD33uPvbbHpHVNMag/RIpiw/ERzffk5o7iXIsIiB8nblOmUj2JdGmEp+XTzARrIzV6RzX1bQbQvqnOw9KkQ+aD7MKJuSaJCA0JuyaLmLwoP9w2ZH+Ab'
        b'IYBr6rCjbsnSY5JStfmFNNHxlpleAh6zUuqSLfXyInN7Y0wxyClqpWQqFXsroXuG/P/JiJ7hT/U9sQYi0sTYWsxzmi9Rn0+/S6WWRg5zqOlcwv9F5EuJtbU5b0kJ2iTc'
        b'vcmbTUR2w01EDCJj+yg4fh96kIho3y2BfpIkvDaqTyiuueanylnUm62NomUJSFlHJRqsLOEzRcwyJV/0M0XOorhZwt97PltT8Mq4AeyzXdxA3Wf7uEHkswP7PDhuSNzQ'
        b'uGFHZZQHrkCaIIobHjditwkFz6wwrhDFySrMK0wqbOlX3Mgy4zjPAorEJSVq7ti4cQxZypjxp03YzcU5xckpPxx9rkJWwSfw5KkB5J91hW2S8JstKc22wrTCLEES5xzn'
        b'QsqbSFG+aIkFpgUWBbYFdgkmDBuLlmzK4mClLC7WJkEa5x7nsduEgnVKuOUyFtnqdcuWrpn5jDOCIaslxGfcndhL0Ox7g4b+TP+mu25Eap2WpEqbpsqMYz+J+Dhx4jQq'
        b'/E7bpIqbRteRm4eHJ/lHxGovufiWJCQ0PPiWxD/Az/+WZFG438JG0S3ex5d8N6VVRoWGBC1rlGRQG8EtI6Zs3jIVwHWTyEejBKIyq/5MtZ60WklGJV18VfTbQbqcJQEh'
        b'EQLk4p8sy5vsbb3LyjjOCozwWTz37rzEzMz0ae7uGzdudFMlbVJQNSCDJp4q1mgS+NzWpKW4x8W739dCN6IseEx0I/XJ+Z7yG3kG8JURTVEMSQcFhc6fGxRFtIO742mj'
        b'588LYC0kPxfGbKa7Xzg1F6sySaFuHpPId7IR0sIaRRkhAhDiEdpW84iAEL8g36h5cyPn+z9iUZ5kq67s9cp3p9z34PyMNJVqHlNbepcRlLY2WLWWleRJS+J7SiINbKRl'
        b'Wd3XH3eH9P9Sdwca7Dy5rFcpdLplnDNQtndGM/3rfYV4s0K8Ms7Ta/1X7nnX5U+86S3juPiEGHVyJut+Npb/0fwEg9l1hjI8mLKQJoM6mSY0j+iC2DQY25KaP3lCzDI/'
        b'QqzeUdK8jyAiDE6YFi1yetnlAZkft0wo8WommdD95znRLz8BG7X3RuKmfbb/PAIiO3IzySfVaMMSQDb3ZK9cggfV0mgsnNjrDBzbybqzm07Jz2grIkP6ZB+YabuUSggs'
        b'+4DT8oEK6GcJZrrMArMHZhZozZe7jA2YLwOELN6kLfF6RkyB2EdwMdFN+AFGywgtJ69jOqNZYOKLalrfGxWO9y0URycfX/mDb6ML7aF3eDs6OauSqL8qa4rbZOdHKFJY'
        b'u45O8/0ffrNmjdKbXR0fVk//+4ejU0Dkn3rC8wFPPOpWQIu4v9H92Yc1Ni7BGCQkWGsonbR0Af09Sc9L4bH7p016RlJaRlLmZgGY18mZnsKULIuew86GTYbO9HSm99Cz'
        b'0pnah53pIecsd+txqU52m+jmMU1zi+FieryvHuxWTak9f57M/iwU3d+LCSAQmlczAPEg9M8EFUN56Ld7mGdiWu8MfbbIDAM2aDLs+21TDyrDNB1dbF/gBQqCoHPAG/Cv'
        b'0//INcbsR032zFTKnP/xMZl0Qqm0vGd6OBbU/dxPmj81t5JyNsZkaGIF9OgmWO84RsTH03dVJ+tRqRksav7cSF+/0PBlUZTXJzTCN4pSukSwVur89ALBW7+dJGxCQv8w'
        b'CiYNLIp23LRqm8ZQbNit3WM8Zg4JoYQe267zfXuKc7+BAWyE0oV1qhLo4e7bYpyFt9PekpRqGINAQLggEqmW/TYxJtXRd1F4P0bwVMeIjUmZW4guyQYu8wGNFzbEftYS'
        b'WTABmTHJm9mD/e9wzv3PWQ00hzAgPYgddOZrhkSH3iH4o/p5o0whzkEPubvXs72QV/rdtVhJfRwEpHs0YpNKO33vK9fwmGgYE3vqZUyVsfHJaalraUkPMaRTWcS0j+xk'
        b'FcIMv2PixuEBZzyjxD24T8zxeFLktARK2DU7rHXUw8yEM1hqaQStQlwDSzbIMKdooXgJrwiIoeexaSVTeAfghSgZHrUhOi+UYhf5aociCWeBu3ksUdur53LUcO0wUKmf'
        b'qLXYELAmRdXk8Ig2O9AokOceg1xL3L08WJM7j814hRp/p3riRZ3xNw/zmJkc2708ZHYiC629eIenmuLBQDfkYGsP8qpewpgufyXdwiLcCYs2QMsSJ0XIIicnLMZSdyx2'
        b'pXCZAhqogtr0Dg4Q4QXYs4BZ7APgaBTD+cSiMAb1SdEhTzGfxZ1kKVHs5ziYOUabS0bP4Vi2UhY2p+hjf/q7BQZjEXlp93AsDArzF4dDEU1tw8tQv3kcp8B86JbI8FAQ'
        b'XkqyeapOpKolhTxbfnxc2UwzmGOdtzHhwO8B4bLO1c8ubhnsamv91qmgOaXQ/r3JswMz5q3tGPyzy5wbT2/1cnDYfXgQPwZunsj2u7wl/N3v3pbd3Jj6XNzBeUu/fG6A'
        b'vDI8c/Kd+mGNqs8mTd3wFkRtWpuwxfpEotedSaaFO6dU/+Fm8/6XO6c4pX2jrFhX/8PlEY+njFvw+aB/fv/08l+PXDn9bmb9s7LYPeNndcsLPWzsFsotBHPh5eWDXdwU'
        b'QgTDKd46zIMPYZh1FAtjjwBMDLsxn4Iqu9KQDGPOMlzsCS0JQkhvTRSecIEDyt7m2/XxAgLkWTyyThfZfpXMxJ6wEFKuAM/YFA97qT15Ep5mJmVogjZm/H3M2Z7MRDy9'
        b'syeee7E4mYy3EKNuNhfzZB42veAhWYiFny+z10bhkRXMXos1cE0Ptk/sA7UTWYAt5M7B073g/wTsPziRqoH/g5rlrK7FU+CAS3hAL7BGCtS4Eq8Jduo87CIFlSyboh8P'
        b'j4VwidmpM6DDCko8SS/SRXeRXA8WLViCjUIHNFhOJgs9iMYM3+D4WJFnIBT1QoAw+7cMbjpkOZ/+1KZttoLB7Z5ELEStUmwPicjknpSnP3kaBsIojC15XjSkH/VHg6mm'
        b'wZlJFBkyHqf0gm4LfqDG1THioRrXX4BxM4pi2HX9YUyVGXEaEDdDFerIkt0eQea9H4CNGqMi/OeG35JQKtRbEsqKKjc2FCUrxKDSkNRbxhoy7YxrIgNp6lba8yOI06Wp'
        b'C6qiuUZZtBDAsgusEqweMRldqzI2GFIZ58bFqXpTP2uPTAP2O52w1VfzTHCcRkXBadE6YJBoA+55V43oosOuohGQfQNG76cxFFh8qTbeI5Bm0l7M1Ijrj6QIaURYHdHt'
        b'w3QhgedKeNYAG22MyjEhOS2GGggcGe2qhleyv9iYmNReHG73k9j214peCoIhjtnM+E2C9Jupo2VNEaI3+wnHJPckxVHRracrepjwhHdwdGJ07fTVmGg2OnyBm5vbaHk/'
        b'QqUQ4cBCi2PobNIjZ9aVLLBPCsJuz3WD5eme6SGT1EwBTfRVb2pJg2U4hfsu8KXOGd+okEXB83zDXR21OojAv9lvxBaLJe6fhzUtXYitfkAJmwypdf0Qnj6gOPqfTuuj'
        b'PfwgpUyHp6aZ1QZL07JrG9LfHEmv+IaHzA3qq6sZDj9+RP1Ny4oldIWOl5hOWM28oeuCqLzxjHo6OjokLZXuFA+Iy96U2VM7Y62lfRSTTGOh6Qahm7oJGWkppKviYvoJ'
        b'oE5WC2aytUlZ8anamU+WZhyN1HFak5aqSiLdRUsiHZfE/kp6ud+GCcXoGxfk+q+pYWmOXRe/JlPYDwyrMxGhUyd7eDoKvLHC+9A2uGoQODXvy7R9ujbJpmiwnAR1Bltr'
        b'bLUL/K/96nTCiTTNMUKjQ2lZ22mI+WZSS3IyWXwxGYImJdxseG9RqdLWJLFB0Gl06RlplHyd9iLpWs1gk4UgTHvDnanHaegYQnS7mPT05KQ1LIaQKtdsPemHzBteO/M1'
        b'5O89HKr0sHZ0It/lro70yHZ0Cl0ULqeDQY9uR6d5viH9rENnvRyAyXLnR8hM0AVkzdVt9ffRED0o0LOXYmliULEcGcIUIa+FeIMGxV9bqouJHw15TAhi2lD5fGOiDXm4'
        b'WTpGBx2buoJjGidRANvxEtEp4Tw0aFgozk9KWiCkgZdGrlBhJ1EjOE1oUwhWs7qwYAbQwKvWKfESmvzPQRUcfiySwdPYDsICWZaFK1wyoIlCDuxWK8ldo6EQC0hrBTIE'
        b'ypcRqQEMUCqcF/u7Bi7qq5XqAdZkpEk5uOBrAyUZW9iLeEP5RhqOJOij2Ij1RCe9JldTnla8NH7SA6sat7lvZT0MM2FOOgwJuZSb5mGHLeTFrrDoqGUSqJFpdF3v0aLZ'
        b'Dlivps7vaDixUclAdhSBoVTfFcowwnLMMxs3GBrNiJaZhxe1muYczMGj5OIJW8iDU5FQFxcGRfN2QDXsIqpDE5wkP/PXb4J9cHpe7GoonpeRFBa2bnXGuJVweH2iNdHo'
        b'Zg6Doz42wuh0YtMqGXammxPBH69tg6Midwc/dSQd0utZyv7aRdrRbIZFg6FoDuyPhbxeDcrDE1hBP9MYrmgrLHDk4FyYjcMgbBUC50rIgJ6XZQnxY1DrIHKHM4+pafjI'
        b'lGis1Sn+8sUaHJ10tToS811xX7qFFZZHanpdzyxArQF0cLSAG1rAGTKFGkxYPZZYaE/0zhvzBetGPpxSGAQ8wjYo0YIe0Scjew0odkCBhR+0Zqh9SSkjoRuvKPV5hsrg'
        b'3EI2aWgTOmC/kkGAUDYRI1UgFNuS6V2MB8JJBxSLsHuDhd/6OWrKkBcOXTtoQWT0LvUqzL9HHaVN7SkP8mRQYTcOTw+EM1BvP1DMweFgG6jHajKrqFZFdPQ6bOwFU6Rh'
        b'D8HjWEGad3EGGSEK3l8sRNRBOZZhfSxZr+Hm4WQyHWIti4UGyNMzxQTNVgbIAxVuhqhCtG2z6L1sSLcdU9vCfjnUsCW2GAqAdhmDbgjz1yu7b8nYrHxY4eGBdnDNZiab'
        b'WW54dhw18OChRInGwBMMF1hYDrN8+SZiRW8Gm5RFSk4gsHHCMsqImPTc68+JVPVEzxro8q/gsOkMEGJ4xuVTPs91Jrt8ayxf+bG191znM3u5Ne/tkj0j/Wz0k21F0dFf'
        b'Bvo5bh3kPW+f86J94lN2GRKMf6c50dFi7Ttr873aJ+6PfK36Vp5TXHzZb6N87gxYfzpnmlHFa3KXkK8/81Ev/8NP8voPH/2r7qrP35dv+PzA+ozOy7Gv1jdtXK36uOGX'
        b'D4pSCo/mvnj9x48alOM+a597JzmrMtp80Oo52ZfPbf7u9PYr7TPm3tt2/I27TQsWf2M3c8f8X0XnS8+l7Ax4I1T6r+glB1+JuPk9/3LUpoRX1mx6edyLXt/seLzpp1c2'
        b'vpd48ogs7Ztj84/4pYWHTrlynZs17N7dKxHSd8ekP/vcwGfWp/EZAS98WPNM8+OLRt21277uB+8hv1Ykrxyx5ef0953fmDlvtuWWQyfuPFWdci1kYdeHk959b3npqy8+'
        b'vtPvtvjegN+OtP4a8suA9rqU49eHd1x795MDc+fvtHk1vqki9OqXX8+pO99YK1sdcrpcOeqNtblfnXNIO1iw5n8GOzf+Umja+Ms3W95/3H9c+x+Jj3/x+PZhWR+oVhZV'
        b'vxyD8QM3vuPZ9f7i5//+dujZS38Y289t/dE/VW4vABVUwv5g/ZR/bNxBrURwcaWQILSXnDo3eoErJOAewQJVjCWMMANy5HBWGarwnyTENHoINp8UinSlh4EALXiVhVHu'
        b'nCzkfK8W6cHAYPtMERxxxDJWbepcshuXCKQklWQp6xOTGOM5ZjOSxg3Rw0gIwtMC9ckiaGIZRNAJDVH65CejeI19yzKdPQ95AX7aqMmdUKSxvJEt+rgQG3kUOjkXgRlD'
        b'Artt8LwIcyE7hUUduuLxWBcsGgBtoQFwTsJJk/nRY9Us1zsW820pfQhcHiUgSiwIEzK8DuLpUb0oMPCsHTOn7YQagU7jLDRia197Gl7C01o+DaeRrG+N8cg6/cR3OLLa'
        b'3Fo8EGuhnJkVY+AKVpEbXClTm8R1M+4Xkb9cgRb29AqxRJ83hZyLgjVuG1wWMu67XOm5rIA8nV3TAyviMicIJ0AHpwwKIOffIShyvx9/yAMuSd2hOp7Vgx1TJrGpQ46Y'
        b'UArptgvLLH3EM40gh1nuHlP5uiiyIvQyx+BihtCCItxF2UDwGhQFK+SkDTN5R+sRcpNHzk62+u9E3+VrERirqKxoyBi4k5tlJjLnWTo6by6iiezWvFRsIrK1ponjkntS'
        b'MU1Mp2QUQoo6TS6ncZtSTZq5tdiBdyA/6T97lrpOqSnsRCZGljSrjNczNtKU9HvU0CjhLXkhzVzKbxltwPR2Xw51yMMyzXtsaBndvTPSHn0I9BPEuw1kiRtIEN9HTZpj'
        b'adcaMmlmc9856Rs1H+FF+w/gmUZtftTWJwSFcAlSXSiP+FEg5e9G99EjwuNTiQqrephBj1kPNBoL1VdjVI5Lg4MeopbQVJARfdQS1xAms7gNxGylJgqTbMtHBOK8XkBx'
        b'WLLEqU8yKB6F8xYD4QjuY1oFZvsr7uepo2f8CDxNzoALeJRpLCOtoITKCo5DtaJCOpxlCFTY4LaJXsl0I9utWxb5Fhig4JfhAW7saqMpo1cwUWOyNe6jxWMB3ThFIzjY'
        b'lwaNAiT0FWiELjwguO2wYobguZsq4Pn9msVzEs4xiOeizS2XJQlQlFDvPc2LokJyG/E8Ua1qqBOsAk4xNxlUBEM2TSfBMgXnzrmvmSnkunRByQyZaUaGgiKsNRJlbHM4'
        b'uzBkAOa4yJ2DjVzGcpLNIqIuXDZnio8FVoqV9CgJMeKk9jwcwDPmO2AX645NsHc12cIklG6Pw3Yl7F1JqhcQPDsmRTAgt+RJGig3LxTwJxXLYTdTaYiExjx48mj2OpOS'
        b'oIymj9DUEbwOhUL6iK8nA63Drnl4heHHYZsRlMFBlnoCx/CwkLRyYSdVDizSJdLRZKrTbBa4LHRSKZFUizWaGzRuZc7E9biHiXZE57gAFyJIvRUWcGMRkWUrKVacSagI'
        b'L4bCMdb19WZ7uWGib+abekSHrI2eLOi6VyaN5ny4Q+MkXPToFWlq4Y9u4/25fdybxubR0eumZq3k+lAb69YfnTCM2tierDiujtsmiuPiRHn8YO64juSYyJWfUds/5Y+Z'
        b'G5cRlJQa36ihOZYkk1/u52mmBv1VUj2mY/UCNg3gOpxgkcqCH9KULQSomUEEYSxnqRGi8MneeBmLoMgb87LmLEjYEJCxIxVyhnPbJlpDK17IYK+3JN2cc+BMhvMLo103'
        b'jB0nvPNcm0GcK7dpgYVj9AzF5p2CxAylU8m5rQ/2t0ENLSEC2l+GK5sgPLSuF1RIXyigWiTR5+oyNYis+7CVXNtgIcZ2X05sJ5qulLPaTOTUxHBoiYljtOvvwzM5Oc8e'
        b'cE8dyyYU1OJ1NqNgN3QJmuo+aMJSpjVCLpmjNPPIZQl7yAJqt2M7ec7YAuo58XjRzGVwVoP7OFKaqgqB5gzK7sjLRI5EMjn5b49mBtA9H+m3J0VcH55tOn7ne40fbaUx'
        b'5K6WZWGnFS/Fo7T5U+FGkJBidi4Uy2VUTSGra/psOIz14wRKzhw8Ac00Z60TT0GjMVl+ByiS4g0oYkl1jw0wlTGMg7NcGBcGJ6zYOhkJe+1kTs7QGO+CrUFkDQTyy4km'
        b'fEFI7Tocno7t7oHYRa4YQa5o+CisIn1bnNS9zEas8iVN/jE/On6Rcq/dIrsbXTW/V3+dn5M/OH+ww1Mxj08ZY2Xz9D8aGk7u2TVmdG6x3xPVcWcbxz9xaIVb4msTb56K'
        b'LfXMP3R2uKfbykuxSaWyHbnd2S3RKUt/Phbx+hhxydvql37avv2l86qXL1dOLfrHP67/aOR75YL7Z0/IMhP2V36xtLLTYmv29BbFSTz5wdsffdxS9vrC1uARa1xWlxbm'
        b'DCjfAF4tK9Pdfmk9mHj2B/WXE+wXfvTb4sHDfz9qt2zb2Y+rf7Mx8n0y8oPP100IW2bUVN200iPhw3UfvNj02qobw/8RpGj6H+fmoS+/ZnX2zasLjf/+jPc8/Pm06IUp'
        b'ryebeFYvVUTIbl3O78hZ993twhewcc+6yFB119yylUPvLGy0nHAz9cSoiH82PPYl1/Lia5Msbt6O/Mm+NPZ01+Nppk8qnKbV31VGr2joiC0533b+g64lrh/9uuvWM2sT'
        b'5w+eoOh4D949PvzmkN9Hluyot/+h+5WnVn6y/JuYV97JTh26PunQ4YnfBzs99VFj21fxpzw/Vhm/c+n94e96Zq3zTfl5QMNze5InpMT6rlP7/fPHm6pxWaMg8pvsj2rM'
        b'Tke4/Db001SfNnh114uF9W0z8/yKJ++ML0s/tlQV8LfrsY1f3oTc06qDHzsfKti92eGFql2iH/33H1hk8cbv/yqb1pTkUray2eT7T2e8NH2jSnbr6ZYRT9+a8MKXy4PP'
        b'fTP5bxOyvzZ+KnDW87kLzmRNsvzC+o0DT+5MrOgceDnM4urW8L/h394/9+104/+JMFr8nfP0id8sufx8zcczF4alKT5Z/xP/kt0ffELqV5FffWrm9+X2lCdOf1WYVfn6'
        b'K6GT3LIUm6Q2n3/6+6iI+S+veP7eUy8+4fnie2/dOG1atCH3esTi28VvNwWHbyjZfvhA5+Dyl3ZafrH53KDHX1D6Ru3+l+3E2++virUKeVP03cTZN0fED92cErNj0qHV'
        b'O+xVrvZbtp3vOvbNR1feyTox7ofOV2fevH69+cDGc5ui3dss/lDdWvbjdw6xv6VHnbnVcGjAavdfvij/frXF0zvHhd1sevPb9Td3/fb1mWf/6dp45dXf/V56Z3/jUfGv'
        b'075J+GbB5/kzjNMyotrdz7xmbr/hudRnKrcot4g3BqXZRnyw4NefX5AZvXT7qwyrYYN//p9Z77idVHxX8YxqyCuplREf5B80OhJTcubUN28EFw1dPSDTfcWMcXldqYG3'
        b'vwmtsY35+nD56LXe41I3RZyOGxRa5LEx9NnWmxUmXit+lL/9dERo6o2Nb7zz8aZnFTne5j+smiX68fmfZsUsbxy03eqLma5f5/3UGvLssUnj7qW8fySn+r17Nn+Lr3ab'
        b'8M3FpNb4W9HNj997/OJbodfdbpi8VfDBZ8OmtD1VcbQ76w+r2x+N3G/1tfkbT3/Klw/fVv7m7yek26K2HoOPt95y/6r9pzvR7Q13JP+wfOfMp8rZ1xKHvWbx8onJpReW'
        b'7HG6tfynsj9+PCmedODunfkX13p88Wnk7OV2//L2UMZuf2qK1Qdq46muO7Yeebc17Vv32vzFReu/CX7tucg2xyVPR/7r9s63b/qU5E2Qr2dcg8Nh91DKVYLV8j50JRJ6'
        b'YsNBQYHPsYEGqsa6wEG9ABI4gSfY9ZlhUO9yf9xF+ODVWXBDeP5yLDYqyQmYaK+7w8pDvDYQr7DroRFYylRS7y29Y0AuuLIYECVcooyJ5Iapa3pHgWhDQAqgjCnkcoXf'
        b'fWSU9kES7BhhAWWzmUK+nhwxnS5uesCEcBTzFFC3kbXELWybihK9tA7TJRtZYLd4ThbszXSib9K9HlpVbqRuRUaInJ7x7SzoBovE3CRskmIe7I2As75CwEkbHrJSak0T'
        b'0igeW7DYmWJWs6ieYZA3UhnkjNdWklNolWgKntGglmAT7ianQ5E7EaxpG/fyNI9wnLOaqa2KeGxRujopoV0Pzk2mFMADD0C1tQwLFaRRbdiKpUoxUeMv8qGxcFgI9umO'
        b'xTx2Q7Ydu47t5KSxgEIiGMD1pUxjtoZj4QziRqywEDBjsWy18ELZRPCto4/bGmGrIoBUbsZTSPFqlrwI+UMlmLNR5RyAe9IZ7+neEGNSXIs48zFsFMDoiokIqdQwXxrh'
        b'dR7bXcSLsUmwA+2BNiJGtCuxLVQGjWOh20nKmWIXhZbMx1zB4lKIu6BGRWEnTd3Wk54qM+LMcA+PJTsFE8joSXCMtnAuHDGVkw6nXWAB18QDyHzWAMY0z90p2FxS8aAm'
        b'CRayQ4RXaI7Hw7g3hg6ri5vcjB7UEs7WQYzZeCWVPS4ehd0yN+XCUOyUYwnpAkt+xTQ8z7puK1zEqyqa2UFkBdi7FhpmwlFW8IrlA62IdtNOXpz2uwt9ASPOxl4Mh52w'
        b'g90Si60pSg2fJ0PXxVNDjLihsEsCp0ep2QCsNlmvcgsgze2EC+bkLo6zlIpnQy4KXLdEySqaLwtUBG2A8/5kjqrkGVgs4gZHSvyg2VpInb0Rh5UqOW3hDW4D1MBlTxSY'
        b'Iki/nhyklAcHksXGAKmNyCKsEM/wJ2Il7fnVuDuBNHsOHu+BX6Tgi0TeOcvsVfHQkKEKcJbzE/EaJ4YKEZStggPMXpVEpaR2LDHiRDIuRQbXdq4QNoYLsA+ytfa7QUoX'
        b'TRL0Y3hayMk9gpcnChzTRt4TBFjGCLHQ3L1QM0hrnloIeQI0o3igHRQKYJAb8JLMiXTChqA0bJbzZJZU83AVGscIE7FtDZygo9DoGRisEHGmnjwcmo5XBeRUKMBsmZtc'
        b'hnnOZLRIs02S+CSFtdDmmtnbXMjw4Ek6FAz92ArKxLEroJa1eRVcWE4q3hBCJbgzIjwyCWt3JAsL+yhUDJHJycJgfWGEh0Tm3tihCGQPRpkrNNY0PLaak7hSa1pdoPDg'
        b'eScsJZOevCQpo4kTY5EITuJlZ9ZcJynUK5l93hdq3KScLJDSzRamCBBIjZvgGhkWF6yVZwRRtAYLd7GJH54TDJBlZLrfYJsAh5c4yCM7SDMe2cRmuiu2DiKDn4EXxamj'
        b'iSJxQzSULL8cwbC5Z+YgjWWViL/ntcF0tdjN9ratKrxAJXu46q2R7AtGs+YsssVspZtigE/veMELiazGdR5YT6dQRtDOOe4izmwOT5T1zrEMSXQTFqepKCaqsDYpBAJp'
        b'tR3ZeWeuwING44WAyOpZcEKFe+Rm0OxKGkb28LYgODGFLAJrifNWrBUaT3T2AlIMu0qGabHIAvZi8RiyMdM1YuMDZ5l1tcJZsK5CIVnFrDNLIX8TddtkYbuEk9iIYvHK'
        b'aryGh9kADraGw/Si2VIpJ4IaOkW7UEi9p+S/ZMDa3bHIibcwIt1VQ+7YMEzIrocGV9Jmp2XQGbjRmSe6yAHeG/aKBP7qfDfsonGuoVAQRy0tRczeasWL4+bDLtbe6JGj'
        b'NbDhgcEMOFxs5W3HdtSRcDRSxc4psp+yzXAHFIs5B2iSeELVCtbnzhsS2IHQylSOI6KF7libgTXCbnt8IuZr9kJsm2NNbjHDDjITsD6AVb0Kjg6gB25QDDaKOH6xSLER'
        b'2oSRKMSCgSoyxqZYtJH8YOUPwANi3E2mcO18tRBXeQb3kw2fIrKuThaAyJfPZZ2yxg2vQIm71jALZMU40vOTPWY1miiuagtTHuqiyYYsmouNWCqg/kIbGaBSBVaSV+F4'
        b'O9EYcqacF46Xi0TfPcjeBq9gm1vABnIfPd8bxeOW43G2uO2xzIvRbeANaS+M9htbmPncb/JCBgfmjsXBrvKAYLJZKwV45KkzpMtJVSewhWxA9AXCRjkyu7S7SmOZplZp'
        b'uLwo05Ojwc4lcIJ2XP8Y6VA9lxS7CJtN3L2InEWXQDJRBi/hMTgnY3crNtDdlrMh6xNOwlmsZgcgNZ7jSUpR7YAVeizV4mAsVAnTvwMPDSHTgiwzPLaFrjNfnjxeSOYq'
        b'XbszQ5zoRX7gWLKLV4lgjwKuC5O4cdIGcgWKsUC7lTwmNp22UHAsVEL7doNIuKQz9wpQuMcDWAsloXgV90RrX4LWRV6iUwynsHY4E0yxE674kDmNtXDGENB8MQj+k8VE'
        b'u74iowfhIKwgi6pLRKSrPNzNLqbGqGVYrBi7QiMImXB8GFThKeEcPOq9kOzwgWTCWZEHL5LV6GwkoCQfJWp9Ge0Bs8BgOlvIo3awWwy1Iixci0XsQJuPV6QyOceJhpBe'
        b'Ift0Xkwomz871s91IN0cgq3uRHZgbhPrdWIoXkQONCZ7XHQmo97u6ubGY9sKUvFhcqKt8GVN8oQDeEMWGAwHBok5Xi4aQbbPVjZzrSeOVZH9HYtMyfuwt4HzK8gyxn2S'
        b'aXjdhLUoM4aXKegLcdIRPDSvHhCfIQz2DT9soNumi/3CEIUzndBkAVfBgQUCRTyeSFG5O3uJscVfTreea7y/pbew2Z2eh6ewXREiWCO2k/3dgyyrYw5sfQ+Hc3hcADTu'
        b'hWZM5M4uWyKw7Wa1b8fT5PRxC1TLTTeuxiIiq/E8VEALkQvo/rJtHbNfEQl6Ll5zDbByolubBV4We29VCOdTB+wSkR4TQrKH42EWlR0fnkkNLFgREKV0C54xhuzSm0Uz'
        b'JFasI0bv3E4jtcdQyYcGakPFY8Je1oANYdQOR4SOvXowJXCeLGCb/w58rfQh1wVQCiF9VprBLPvM8bOY2sAMO352cs4mDEFYQCQ2E9ky8A0KwWHHAAGlFJuYRYebaFCJ'
        b'6Wd7ctWOH0K5ye/xYnvRkHu8yRCR4/e8lbXI+p6EN/uDl1AUY0vRWH6saAj5NOwu/wdvQRGHzckTtr/xUvp5LC+95ySy/J0nz1uLRois/+Cfl043YzjHDLGY4haLrEUO'
        b'v/PSYeQnrU0iGka+O/zCm9qSuujv5K8WDqQtFHbE6R4py+gBdZOrw8i9tFwBAdmElGFH2mNCSrT8USoz+YF/0lyphSgRGNcdyffxtGaRwx88be3v/K9SOxPRlsEG/DlC'
        b'z+uxrz5s4PTSkp8mQzWMmhPpJtiPRymb+9he36fUfxtIxSwRvktEs45DQuQS8o0Fljea34dZkrGOY0nXEfP9fYN9IxhKCUuSFkBL1umQRmgLM6gnSvDH2f2vYIlM13VQ'
        b'OZ3LRhpvpgkvkWqAq3+TGP8HP70gncKLLK1MtKgkZEpzgiH5nt1MLcqIA7tqRj5LxNqrI3ZyZmrqDYTruMumjwE/cXuIkmwVM5ZLsXiopE9mvZnmp8rswXAj4jgTzWdT'
        b'vc9m5LMszpx9tiCfLTV/t9L7rIEeOWqqgxWxixuoBysi1oMVsS8zjhuvgxUZGjdMBytCoUi4uJFxjn8CVmRUmTRugg5UxCLBKG503BiDcCIUwKQ3nIjTLSsGwcOoqX3i'
        b'Y5My77r3wRLRu/pvAIlMFRLWJ8r5W5L5oeG+t8TzJs7LOEQnfTX9dlT06IgeU4WMy4l/CgZE89DUPw/1oa2OJXh6UqiPjHohJ4eCcmScZihD4b7BoZG+DOJj7H3wGhE+'
        b'PuHxG3qnlXtkNNAXfpRbPXU4GNqG3HXor1QdOEbvNstNe5VBxyHjdX2EDW3nZPyDvtEb9FJ/dXhmXKT3/C/iYvRloTXSAFPvIwr0XpVyHnbqcPuIXLhXcNKcxXPQKWOo'
        b'XhSWrAAriEbTgEeS3rrRJFZR4eiJ/b9QhnH/mBcSnD9QxpglfMp9t2vw1BWcd5EkZezf4j6Xi5g4uGDoUBciO53SRQCJMNcGmvph5uzQxoWwfKz+xAP65UiPyi0O9y2y'
        b'RwTZsDXWwg73d5rRr296gW30X1UnHc4XKZIG3WT/60gaiXLJ+6Okj4qkEcdaTKECaEj/fxJGQ7saHgKjoV1ND71j6iPDaPReoP3BaPS3zh+Aa2FwzRq+/0/AWNyfvCXk'
        b'GcSk0hQBmoPVT0aR7jFDaKh9oC96jbMG7oKeFQKEBTkvnPtP/nkYzoS2JX8GaSIp4f9AJv7fAZnQrjgDGAv0v0eBeui9aB8R6sHgAv4/oIe/APRA/+ubj2MUEqmeTX5R'
        b'wwXqBcAyV+iAuj5wA1iOZUEa9ly9SORuLJBhPV52Spr4x68i1XxSUOWRdMoE/ul7iQnLH3/z5ms337r5xs3bN/9+852bV/Yd2z8qrzV3TE1jrrzk8pt1u8flNR5+3Ke1'
        b'yDNv1KGcdiMu5x8WYalZciMmOESuglwNIgB24EUWPbsZSpjFeDIe8xIwAXR4ALMjNIgAR4wEM9UWCqyqCxO2TdM4XFdAvQCSmofZnizfneNjlw0UeUI5z8r2wIOjZEps'
        b'gYI+Gf142kgb8PnvBL/qMuFdHybkLNDPiJcakkH+fLq7wyPJPp+PeLDs82dy3hPlopCMyyKtFGYg332eMafJd+9Tky7ZfXQ/p1yfBHfpgwNx1xjftyJk2lXhQ6Uz4/vk'
        b'MxmV0BJkGvnMmMlnJkQ+M9bJZyZMPjPeYaLHfrTdkHz24LR1fVXx/4mc9d7oXRqhR5PInUKOCZpR+39p7P+Xxu74f2ns/5fG/vA0dtd+RaNkcgLo85P9qaz2B2wZ/5tZ'
        b'7f/VXGyxQdnPNoSFBcf4Du3B8VoUyVtiHh4QYLyoRR06sRyahTiICH8sCtUicfkHYhkjBlvihEVLaNaphALhl5haYiFcgYaRQi7E8bDRsiw4Ns8Q1hfm4B4h5v7wuAkU'
        b'LIwldcdgC56HIhc1td44QZ67Uksn3geJC2uwWIPGxXNwAGtN8dpiqFJTOSN1zaqevFEs9HcVsjewMBhuQJuWQDVqgsncxVjCSL2hLYJGblChVwYtPXIvzYV1xT3BQkhX'
        b'uMwYyyyhVj2TPrJngI2OjnXRwog5SxSLl9Cc3sDgIGiM9Ifz/sFuioBgUoY7D22yiVASHsGNgKOWybaThGTkBjgP3TqGjPPQDl0rhqu9OBqwvY+8YE/ptGyanJoOHRMm'
        b'ZtCMVJYmLuGiocQYKvE8dqupNIXFMjwVob1bM1qR6eyR4Hhr7auvSDCGerg+ThiBsxx2yzIsST+K4XSsjWgmHN/MGrhITRrRjl0bVWKOH+iO3SIXrBYY5KasknAm3FQ/'
        b'yZxo83QXTy6psn6pkepv5Mrmv324aG+rBXhY+76c9eUTOXP8nrV7YX++kVNzxlg7b/mx/IUrl4/3//GZsY0247zS7fdbv3jnp+v3uuOecxr1KTl6oiunvzH/dmyF08KQ'
        b'NnH4yeo67w7Ts6tvS8aLnD9UBg6ra65wP3zI39/7TpFjtSzq75tMYfDIDz566bXBWQWT8cvnFzx/3WrHiqyPjJcOGLr7ubvjnGerUku8P0n4MWXHjS88v0tYdvkH2fdf'
        b'RYW+X7v0Nffb6vLM35/6ve7t4abPbfX+OuDbnYrBgQHGH3/sXb+25SerXS8FlplHyq2ZTuLHbVW6KZJ6I4FNVTO9YeEsKNMleN6gva7DGDuOB4VYr1ZsXazlrIAirJoL'
        b'+zVhKLgPqhdr8jB9sVtDV81jvQUIqZx4GY9DkZCIiUVjeuklK6CaubO3qqBFM1+warvAD8zjEZ/RAsRagfUwrcIjIhVf8OT9Wd0zUuCEZqm0wyEN0TaPzdBBGscoCqvH'
        b'QAGNou0bQrtUihewQimEZVy3TmGvsNmDrdkiUpUlXhUHQQ10Cb7uXXgQs7FEoCfGJqykFMUbZgsBVb5LlBMD6R5wgYOjg7BrAF5gvZ60Duu1GaR+UMVMyLaQK6h5cBjO'
        b'ugRG4rFgYW8gjR8wQYxHYhIEXovjo4f04Mrh1RDeI0GTJ4pNsyFfGRRgIP1ylERIwMzDQ32p42T/wfTHhQ/TANNZEqTYhDHpmkil1DcsstMw8VIvNP2y5C15E11C45aR'
        b'9+tQhrMWTR8la7EnYdGofx+/cf8UtgaSE30fSQG97qivgD7slf5L+YmJcsndVQ/NTzSkuf2l5ETqqeibnDgmhJloYsYPUPYwRDwoLxH2ud+XmrgW9gkO4ILV7jQzEbrx'
        b'mJCdCC1c7PyZYhk3Gs+Jcfc2PMc2/XmZcFKVlbiJZi0JyYnkqDjGLsVClSt5Eo5hq4cm8TAJ9rPz4NVUnjFzeSw4tuCQfLCQWjiI7FynWG6hzUpOk1pI9paLLLVwFtkP'
        b'updZM64qd87dHC4Lp1GnM5xRbaARm3vsoJLmMZfNZlc2rp1IUwvJLrDPSJNcWDZHQPo8ZEy2MeyEPT0ZhubQ5cUe88LcIdrswhlAmrDXC88Krq4iPAjnWX7hHDgo1iQY'
        b'emAXe24n7IVK6jEnsk6uhKUDLktVs6DFo3hsiVcQS/jrne0HNdjEuiNu8R5umIhz8DAeurFiUKiQ5faNagxHDQ0ecxumlG5YJ/zxuzkB3D7yNw+jdpFqUvK/l+63+9ES'
        b'xK4Y6yeI+dNXuua1SUNE4hoY7IYHYP+GgGAsdsX9Gt4jIgq2U2gTGtAnh07xRCLPKKEc21Uy0m3zsdAqcj5cZ69kPYSm+HFOHgtWK18c6yW8570B9pwrueYx68Ycm7UD'
        b'OZbuCjl4cFuvFD/VqA1qIcMPT2I5S1EbvBOPszy+1bPELI3PVtPJ0ZMocCop0v7j0JGR7pxcJMyGveTULVWFYAGZuM2aAN1srPvf6FmxiX7PsoO/yZRmTmKnFXTAFZ4l'
        b'3wUIuYNQhdV4SpN8txOucnB4nkAYhzlQDXuw3Vw6DDu1qXexASzxDo4swYZIJ2q6CuPC8MoUgcStG/fhVZnTdlPnnsw7y3mCv7cjwp50cZhe5h1WOeDupJqO1SJVFan+'
        b'VKunOlKpGuhr9/XXnx3+tXr3N/7PWFjPmVNRsMDnxK7nxjjVLbCuXPJBu9HR9449/0TG6+3v79qzeNljykF2j33v57qkQjmoSrb43KqfxU4l300/8+vyoqoS1SfbPpn+'
        b'SVbtrKiNx0sSHQ8+fcN2geVHimU+RecqwjpeyPtJ/PPfn/vB+sPHE6PjYYbTqbkpzTKjBVYfbYTnvlzw/ufzXm2oN73KDz5u8X3DlLBC512PrQtTlb45w/mEd9jnT/pt'
        b'xslnExTfnbZIVi3+SJQuuxTfkSJaP3RRymsbo1tTxo7p2D1lXfVvq3IXPd32blDTvatJ/3gzzfXvs62j1k/r9B617SN3nzcOv9npxO+cmSxOvv3eu1PnXR329M6UHzbZ'
        b'uqhXqeWvRkSf/tnlbPAsVfHE9RYXB19ecTbJ6/P1XdA5as3W73wUv1w9GSmP//riD2kbvTtLZobN/GyfTcKLw1+vHx7x0svD7rxY01CTYeK9xiVjRPbm6sMzo9+YJm29'
        b'nvr/8fYdYFFdW9tnzgx16NIsKKIgw9ARUUAFDUhHBBuidBBFKQPYC4LSQTpYAAFFiohUKYJZOz0mMT3RmJ5res81Pf8uA4IlN7m5/6ePyD5l97P2au9a/s/Al2vbRvXW'
        b'n90Y/9o7O+17kjRebkWhc3ct/3z6Gz3Xrq1WeqvHR/LzrEYlraZrtyOVLliu7ee+Unhj7vroRTUpAxnq/X/MWxVfemdpRqt9wTWDzde+a9ybkLuvyc3m5dnXRPUtLo+i'
        b'uHmHSn68dcX+2vtD62v3qWe88tzFdaM3v1l0DG70C2JbH9+3p+V6f/msmV4Og83PGAdn64fMvj3vStC8b2ts21Me698Y/WTkgghZRMC3FhfRvia1n5X2HFL9TekTvj1z'
        b'NMC7XS+z7UPdtoAF8T/eOfzJ726375h9bvXGzdznF3w1P/6nP17Y8/2Xqr+dWmD6+uVD776NnJfP/feyhHzbwNxtcc9G/LS+rjKg5dGDV79LKXw+6tSBrl9bzo7OeVk0'
        b'K0vl4991/SNy/4jnDX7d+11z5O9fXnUe263+2ffRxV+YlCz8/LoF/n3Rql3lq2ZkbK08lr63ZOG1a2MLP3/t+xmvfXLgta91E2pqK2eMLn7F1sGhU+nfNmfKhsZ+DXSq'
        b'dt11Vi146LuFKAVGv/KYWR35WtaduZ/PM/zhjsqY3snLi564eXn6bcNz3+Ue3Nb/4y/f1BZtnDsvolM40/dGSOwbf8z4WPZZxY3Ws9nOSctGflJ/u6/dTLRLPcPo55+O'
        b'7Dqu++jV04IrkZmHLn38w0tvh//8wi/2WT0nm3uEQ5d0K4P2PnFa5b1Xp2+OPJcys7FjR39V0PJFN499l9PflLgg/pBK3Atfdwa5np75xHtBrwt+WLR6/x1bBYnqyOfC'
        b'7+NQ2/qC7xrTv0iate2TZ28/J0li7sJHMOUoEltobXsQF44uzkBdDEZRjypRrzQgxWRKIORZypRD19kIl+5FsaHzqFO0xRTOM+hHFVRpQ+Z+AmWbAmQzSmH4m0rUKroP'
        b'fwZnNUTqc1Ehc8ct2wZnpVgyHZmMQbNCZ/1oH4JjId8EqmWTs11RABpqQfkMgTaEzprKEWgSH+sUr+XeBKMyDkJzgWxF6IlBco/ty6gBn/uQlzYJhWZh70pHswzXWSdF'
        b'RVjamQQ1M4WT0MvioxxVsfe11NAxn4QzwxISm8l8V9QhRrlb9a0mw8xmulOZKXC3XcAyBiqYCjFDo5HM+7rWZDmFmNktETKIGWTJswXmBaAB/KqattVdhBkHLXR2XDWh'
        b'+wHoMjhhnzbHkla83BVO+XrOmQQwE0pW0dHOR9kmDFoGhQRdNgEt09jB1rYDFbjLrCXqBwiy7C6s7BHEZCl0YdoBaEsno5qKKwtTYp7dl2MFYutERLisCVzYrt1suFXo'
        b'qKocFoay1nFw3gQdY+iOw+vVHwAKm2+MJbcSV1ZxKcrRoxKe7dJxHyFFyGHLcBmKhGJ0BaoDrNQkeMDQJECdu+Tb1WiG9TpFCh2ZihtBNRz1dMciXxvkTIKcobYtNgHj'
        b'kDNHR1qJIRrAfalADTJr78mgszVynIcZqrQS+xzcZOWXQvPK50kI7kzAzRaJ4BLkwiW67fcg/IHK1Hwl/lOwZeqQz0J3e6KcA0vx+KdCy6AVHadzEIn6CY5Fgob0eDko'
        b'AZrkiA8f3Lkj4+AylOXNwQga3klbVRCjSiy7Y/5LvvuZ5D6GSmmtS+GkKQOXzSSu6RRdJoNS2iPzEOil6LJhODEeAInAyyJhkG2X+rTNBF7Wg9c2L8XvLr6sZBtbmUpM'
        b'Byql1lAbJrkLMPOEE3SXb1SHPLH1LiiSTMKXQa8n7XUcjM5OmkUgZlPwZWh0Fx3v2s3JYhs4OQlhVq8LZ5iL+xhqwYMthNwpGDPUtwKG6Yjt4JI/w5iZonyRHGPW6Ef7'
        b'5DcXlVCIWQIqF40jzHJQKx1OFOa36n39vIVwhYSBk2PMZqMcRmby0MkZMLaYYUrGgSHavkyvc3G35TjADF2AAQ46N0I77Y4HOrGXAczwZhcyhJk9qmSE4IohmRqiWQ3b'
        b'Nh6s3ViOs4QqY5RPUBZpE+xr2Ro6ecl4S9fuRBcmhxsjeqhpDNK2YA+HO7nVDndzHPcC5aiGKnJgTMnpgQCzDJQlRNWr4TADNl2B/vQpELMlayiMjCDM4AIcpd03Fi5B'
        b'PUsPTYKYYZJVAwxhA63J6IovvjBq5McQZstny4FpYahchrrh0iSM2RbMpJfTStdDIf4OUbc9ykubgJiNoio6JyvCTRm+TDqPl+PLNunSQatBGWThHu9RMr+LLzPiqeYs'
        b'QQt6KNYlAH+9uf6o1g714f4aoi6RdAbuBHn/EchcIzaHzK2TGGdomsdAzKhNFe8od+hiqjO7bWiE7sWN6Ei6GFeaLCDV9pG9qAplPHSsxF8QJYodRs5iWxs5SgbLoybQ'
        b'up3uGOlcVCY1twpSotAfBmjbH0S7q42qXGQSKPPDJ5+3hYoc1CbkjFxEUBpmT/fqNjiJ8sXr10wGteGTv4WdA7p4dnvoCs/QIaC2CUjbDEc6WAd8Yp6nyKwz0OvHMG3r'
        b'0WXGZ2BpCWU+ANSGypKEUA+VcJEN7QRel/ME1SYJEzJU28IERu+LoHlpAGpjW2wyAg1yoIbuAVcon4VpkiUmakWTIWjLJCw2Wo+59r0QNFxbxV0YGjSiM1vpebnaG+pl'
        b'kvGpwnIgOiJEzZhYQDY6So+AHevdCA7SV6KC8iXe6NIKfNqQ+ZwOmaJVs/GHQSb00Mw15KEMKPeV0BEroVO8uz/uL1nodMj1gSY89oJAv6lwsxEXpvkshXwCQfJHhSvg'
        b'BFOvU9UrnuOLjER0zSZYIjxfqHgNnjCi94yTo21zoAAyZbjdQLybSqSY0GrtEVrO2O9mwyjpStQnRcXbNPww10WUDKiW34dy7JhqtgYVQ4mMRAjNI5wh4UYEnLaeEPph'
        b'6ABqgbE04lehhjmnh2PxOuHUOJKNgvEWWjKVcwkc3nYfhG0rDOJTtVOOdjdfCMdk3hZQO0dObwieFR1VZ+f62W1wjoBd10MbL8dLo0vr2enR7IWO4fM4k4Fhx1G7uwJo'
        b'OIQVeB/WUKhdt9Z9aDuGtLs0j53w51A1KroPLYi54GFoWo+HT2ZpMa6uWGoehBqtHoC1wzcrWH974AqcI2A7dEGfk4PtVrrT/vLLUK4Y5XuaWk3C2uENXEWX1xBVGxCs'
        b'3XZoFMixdqiUAVRRkan9fVA7dGmHEA++F6oooEvPD7oZ1m4VHObQUQk+e+lpl7UaT+89ULuNcAzyp29kR0hvdCrF2rlAHS/H2mHOe5CBxwoS1ol9TN38GdZuixx4WAJD'
        b'MDgZbLcMFdF+UbAddKHiUJ3508LEy80nwHbTFsSw6AiFKQSlSqK3ukgnQe0kzmxNL6J8bZmNNRq0mIS1g+xQ1tdhyFyNp2Bs5V28HarkWYoWyLNDTfdj7SBruUgH5e6m'
        b'FUyHCj+ZtQ/0xafjj3kcaZeyVo59W6uVqiePVTEZZueMmtnB0+kMpeM4OxjUZNlPMDE4Q6n8dGhHI77WNuiIP8PapUMRe2+AWyL1cYeeKZm/oRq1SjT+7zF0FOrETAd/'
        b'BqBjf6ePw+i0hA8H0ClPAOh06F+RQEOghcvGv/KKWoK/CZhTUpYD2EQUpKb8B37+D/r3DcVF90HofudFDC6nS9/QIIYNCrszFOgLRLhWa4EGeV/xH0LnXlFznQqdM3wY'
        b'dE7/XjvDP8XN5SqN+/n9mbHjMPfzFPTcQ7qB2yYwg9Sb49A5IYHOPSWQayAl0/7vIG/P4EbfI5jA/dz/CPL2hqKUF2goPBDetuAeeNv4vT8M3dMJfTfYCC2TNNdMa62d'
        b'KODMYUxhBypDDff5wmrI/5cduQ/WFiqqUKpQqZgWx5OfFRry33Xl/6uy/xOEccIYYREfYzFhXiKJb9Ry1HM0crRodmo1Ao+jcDKFWMUYxRilbI5k5S7iQ5VwWZWWxbSs'
        b'jMtqtKxOyyq4rEHLmrSsistatKxNy2Jc1qHlabSshsu6tKxHy+q4rE/LBrSsgcuGtDydljVxeQYtz6RlLVyeRctGtKyNy7NpeQ4t6+CyMS3PpeVpuGxCy/NoWTdHIU4g'
        b'B8np0d9Jlm/lUH3qSSmkpjflHDGeG008N9p0bsxjJPgJgxieatalN9RWuvuHjGe0f6+fv8eDkrgwTX6C4ekmHHDSkkjmBxl7xtHekv3vQPMkkN8WTqls3EwnszZ2n+Qb'
        b'KHd1o/gAuUMdvpsWm0rTOCRlkEy0aVN9+yandLA0jo2M3mqcGpucGiuL3TmpiknOh8RrdUoND/PumWosnFIISCJOXd5xxjQFq8x4V2xqrLEsPWpHAnVTStg5CXZB/abw'
        b'7Uj8L21rauzUxnfEpm1NiqGe6LjPSYkZsdSsmU7ITeIe4n81JWeFsUcCdWUyd5fIfXETpzp4ET8ouYsgWwgb+TqMz7ilsfkKyfhjkcayWOKqlhb7Z4tE1tB8pYRgNSIn'
        b'uQPKHfGSUhPiE3ZGJhLQgBxpjKeAACLuGahMFhlP4SKxLDcHfoqN3jgmNhnTV5lxEus49ekzl99bQXbYjiTZVNeu6KQdO4jPMd179/gPBkj4G8LdOxJvKEZH7khzXBgt'
        b'nER2FOSkh5qcfPAPOQhMKWc8c5aYkhABJiJ8nIbcVi3MVcziDoj2qu4XTtiqRdRWLTwomgQL+1nwF2BhUz6ih3uQPcypEI+M+RNu8PeTO8TRJCm03rtrhleHOo3iT/LB'
        b'nqbmsWwrPex7/RO4Ep1WZ4I6iY7EX3wE7lIEc+xjlU1UMnnbPSR1TWRMTAJzA5W3O2XbkQ2akh4r/3Rl6fibmiAdD4ZpTHGWZRlpyJcXmZ6WtCMyLSGabtQdsanxk/LN'
        b'PATwkYq/yOSknTFkhtn3/Of5Y6acceryzTbVl8AoQEbk1aB1G3tevCOVtKVJnpb0F0he686UcQkHlF9GZ880UEf8dMKzbIcGLF32YB55gKgH07DEIMFyZYEEVUE3sFdm'
        b'Qg2cPYAqKIsaQqPyLuI5aMdtw2F09iB3EIqgg5pq12phwXf+p/i3CL8j+004+vAm6EWnoYengZouunAuYcaJP/7xxx/hmiJO2Q9LAW4RfrfmrGG+BCvVH6EhlVGFgy2v'
        b'gQo5hSWC1VaoXcJT94YNTjAgQ/kaKG8Xsx5gsVLFwlzA2aMKRTSyQArnwljA00J0clGGs5jc4/0FTug4KsN1EN3XOshB2ZMrUbXWw13MsxJwJs4KJipbqNU2yNpejG8u'
        b'nGlFxL0hEkDunAeugbi1bIDzW+M8pvTD2wLLz+iS1NvXmlgw1qEa5VlBcIzFWL0cDldQz/g9ZTQEmY78TpSNLkuE6US0WQb5MEDSc1ihUgdbR55TQ9lQeoDfrg3ltAoV'
        b'qIaeuw8ocmpuEQf5RFztGI14jIWV9mV37ws4NTV08hC/Y68C7TDkRGF5nqT9CIeCIK8QL/JkkNdkA80jmkoGkKXMIh2PehIlcl8gFSGDrFA/lR6nQbEQ6mOk1JUAitFZ'
        b'Eg/xrr/KeNIUlOfn62vFpyy1XwCnZ6ErkK+HulG3ry7k+4pVafqTNcFcbJyWExRDH903b6xV4JRFYh5vhcTNTuFc+kZ8MdqY6Bfvq5/4atr4rDVHeV6oMJi4SPquRV3S'
        b'rbLx/Ut9ZbDor2Oqio7CWQUFNOhhCq0SzmOXLjqNTprjSaemoVKod0I9mskqwal4k6DLAjPoQ13MZzMPLqEysXIqHHHIwBtAJLCIQzn0tbAFqBz1qKWgEVRF3+sQzEcd'
        b'LE5xPP6MZMkBWEalLglCNUEE9LDI2AYoHx2VpaDuBJSrRl47LJifhD80ngX0vgwNJOZXf4o1OkpqhRGBPmRBLa0WNzlImvSC+vEWoWE+XfhER6iesu7hKAevuxQdTidB'
        b'NuA4Go2YnEDG38oncK3XxAtb98inFX/JPRyqTxTDeSibRd1r4YzrziTUcN/bq63WsXc4VMbFoMvKXCiUJ9g1aPOyI/gjX7BtzY5yl6Rp7lpP7rrz2m2Xd34qW5w37aTW'
        b'29nxXrsXqyzS8BgV7Fh9olR7u+7jmkENt441veFlPpSfD6/PW8Y1NjY0Nq+oqAjR9nnu85/fr1n13g/XDv3e893NH0KHh86frklvH7I1dsv8JOrTzw12zTvpcjVn0NMo'
        b'1S74ER2jz1d7i2Yufvec7rd6R0pzSsPtHDuFjyoNfr84I7P3ypfi9n+dOf7S9ZAwZeNsk0eSjDxMjXZL3jQpGeivjXqmVOOgrPKzX8q8itOU+oeNN/rsmzPfwWXO67qX'
        b'SiNlkk/2fzXre2FN7ie+yLBt5FpBY25X9IqhY2v9biRaPOtj4vPxFsmz53bs8PzlDUdpY03Uuid2Pz90YqWB3zNhtQ03d9/ueV71y0191obBAbEv63veSLhk/vyGdz5b'
        b'3tvz2q6dzacNDDpSU5rDun+KfeqDofmbRy7EP1NeV9u0/5P4l8ciK/z1xDsWnLlV/5vUNvYrNG39pe1Bemlb9B/rq1nR+tyLKbnFCR94bb29WulUrmlag8u57dmlp01f'
        b'We5jcHvLkyenf/uWlpNHzBZR27Prfriwd3tzZ8zza0/9FKZgrzXwuFGKwWcOO5wib1WZnb81rXRjZP+KxPXqPY7fV9xUW/qVlb/6r+rtlSgIOVgt6Lijd1shanPiu3lv'
        b'vm0w82L99dVlXc9r/tp7daQ39I/Rf9uPvlrzxPdz6pY8K/s+vO5nw5KXd4TW7X0ieFVd5WOfPGpY0jPwm8ELqt8uPr3s21kb634O7lm0MHD3678un62malu/5q3f/MdU'
        b'9L5z2bpeVnTr/JWX93fVlh0Y3dTf1oL0HSrfXvBc/fUDnUvqWs6s8I81DNZ75uuYJ9+2eevStjjDvsefeWw0S6tS0UJz5rHPHY6veuzQDzMda7W3HE2RuFN9T/oGA+iD'
        b'XKm1P5Yo4bzAF5UsYJqoTPMtUAAXCSUhcVLzeb1NnBhGSITSGsQU++sVaejYI1JvPyX8dq5gaQjkURUiH3RgaujVQVcrGLSShzhEp4ygwIa5sipGkAD4oyZiOMnudsEV'
        b'qCR5iWwCibfqQR6N6Vqgtn1pxH0yHJVAFupyxq8TE6qfNeQFUhMw5Np4WVpQwKYSF35AGS7ASBjLlNJihY5PteNro2FbYTzqgw7aWVULYhLGtRRZKXKKW3izuHlQge+R'
        b'M2UWOge5voFW3pYSCYkOV4DnoJeEUB1ZTO+741oKpPN978tFnGzDHAVOecGg2APK7k+MDCeW0+aXcO4ym3FNITrKE2UhOqrDbNHHoAXT20mhudB5fMhWmshVtdowhpqk'
        b'3ni0p9PxIS6KF+A3+g9QlbChEk24THWJ+Oi7PK5PnIFOiVIcIZvpegfDUBfxOoscDwzZiYlbNVUXR7jF4nn28fe1Iva1ACgywtuB1DAfVSq4IOLOTa1puXifFMtQkTdZ'
        b'El+NgOlQYoV6fXlutqcIztrCETqURahVgRjAS1QC2F11kcCDxzS7n+UGWmGAqnFzAVaW/qS1g/by7hrbidBZf0Vmfsy2wlwJDTKG8hQUApjqc3oGvbkbtcyEgkBrH39L'
        b'b38Bp7EjYatwcYrciqvvhkqZsleut1ZH3daOQiXMnLAQaJ3p66hloNAXFShxiio8XLFUQ7mxdKM7Yx6iSOYXoIIuWOODbrtgfzTU0PkzIlFde9JSLQ+SRNLUromH0c3q'
        b'PIMn5gg11dmiTvNxW93yhbS7NijLgQZUpDmLFNAJgc5aNLTckDaID+EesbXvRhVr8labAOpJWGOit4bTqMNYBuVuDwyQiar1oZCpmVstoVwH9ZMwlRMWxDqUQ3udGAL1'
        b'k4NbQr3JFrPxXjfsciJmp3xzdMJPEbd+ktjgR9AQvRuzA7LJiEpWQqmU9K1HQHdoKVXgh8KoP+oxSZbHf4URM122bpm24nFvGWKpHuKDMSeRMp2SoMX2eBfAYRJEVG7h'
        b'bQilX25oKsEuB1rDUaO7Jl4d6BSigp3hdFV94VwIC70oN5+dJCGKecjz355GHX0HrdDQZI99TK3aJ/sLoaMM0RBvh1ox8ymB4mBiXhCiPgF0SlWYtv9M+hZ6j3FOipxG'
        b'PKqNEXrYbaIkaS1xEIVSPGe7MlCvespdZozgsW1QsZe/FX4p2ENZIw262Nrg2UyQSVUxYywRcEowjM4c4BfqsGRF1lCxUCZNZap9JUxpymN5+xUSZpHuxq8ehwIzTPa8'
        b'iS0okGbmU+D0UJtIG1VqshXMQ9WoXkxqZ5XoO0Abv9RuP53VzSgTDeNJo+/jranEacBZlBUgdAtEA3J7FRpSmAVFMh/iKiRAAwIt1AA9LDtX03aoE+unyCMiHp22nhHZ'
        b'bKjYRSw0JqZTwyHCeXScGfIz4ZyODMagZDxo8nkZiwwqW4nbP7NIRi2kJI4nGoBSunypEmKqCMTd8MbfZQAhCDaoIsALFQm5eeicglO83KtkOtQ4yQIkPqgzhflI+Qo4'
        b'LSNhEJxcSvcldGyYI0M1uvJoyDC4153aqzbEo1yZRAWzlXVkooRwVLA3fSe9ZR4KTVIfK18riwBMTDQjF8ULI+3WUMMstClrT+kWQbvk2UAmqgpQ4CRbFOAkqkUjaVIy'
        b'l0VRqHfy1tiMhayJ3RG4CHOjLtCpGLAe5TLsCh5xM/EB8kenJgIFoTpUR2mkJ+RiuoDvovOo0Gv8NNFGQ0LijhDEDtAK9/1Setrg00zZeyUa5nGdmegSI9aHUTu0Ydpx'
        b'Earui+iog7/DZon6P7fk/I8sQg8KFtCPf/wHe88hLlZVoMUTYIiiYJZAjdhYeKpc/01RQYtaeUh2K2IJUeSV6W8a+DkNwWyBmcBcoMNrkexZ+O8s+qwWtZQoCvQF+rhO'
        b'Hfy/Bv6rjJ9W5RV5/XuvCMhfDWpxIu8qykEquoK9epNVTvfELJAoMHjI+8SK8cFUyInaP1oLIavubu0T8+lNHLTJ9f9glDnMDZpNNss8eBx/KQZC/H+MgXBBmZPHQJja'
        b'zEQABLtxDThVIVsax8ZbG1sQXZi1raPDeHyW++Mh/KXuZZPupfxZ97rGu/fzTNIPuTrVOCFmSot/OR5Eq+CGcng007M/tM2eiTbnUgAzRe3GGdPXCAz/b7cch1uWCG6o'
        b'h09okcMTHt58/0TzZu7G6TsTUtJjH4DW/y/7oBY+rln8sy4MTnTBgsyALA1PAdVNTqgl/9tu0KAcM/5sxUcm2rYOTiJRgXbGJdGIB8aRUUnpaVOCDP2X7ZOIMQ9tf2zq'
        b'jpsU9Oa/mvNUrz9rDCYam3G3sRXeK//Lgfn+WVuPj7eV6s/9ne+z8M8qfWpiAOYhDwhVNB6F428PJ55tV1UaSCCcwPof2oVnpy4YjQXAPtr/ahIlhETQVtOSHtrm8xNt'
        b'TpfHjfhnLaqHR0UmEoNIeFJy7M6HNvviRLOLSbPkWaalT5xs5rs30Mh/TSw0JnoVnZgki31ot16Z2i3y8D/q1j8NSbn1QSEpBdy9VglhQEKUjRovI0yx6fc1NK5kinLc'
        b'u35KnHKeoL87TCKg4kOog2hC6Ek2If76ROQx8n9IMEnzcVcZwlL/R9bpEBe/V/eeAz4xdmd4+MNDSZIGXleWT81/5CUOc+1TAko+sLH//xFB759+UUBIwq3u13kZuVz6'
        b'0xO+wumRanHvJgo4kYfAU/DT3Z12/xxf4tgcpx4V3Me5hIdHJSUl/tkEkrdv/I0JPK/2Z+wYa23KDJLekjaJrMTMrXejbo7HemImV0GO+oS5lc9VwHMrxHPLT8ytkM4t'
        b'f1Aon9u4e+eWCIkkpaLDlLmdw4JsQDFkryD6fabc3+MlmD97C7VzCWeLnB8XanGcW4RlmJcLS9W3CBWhZplGqgp5uhGNbBdYOxhSWwjvp8DpCujjiTMFIo4GfIDj6Bj0'
        b'Up0Iw92TkBWFvviXABLFYs3qNbaaVut4boubEpzxdUmn6pQCZ9Ts60O091Bs4+NvGizXdilwFtEKJEfRdGoq2y+0lyUHMHuFCfQKIiDPhtoWFqWhYhaZAwY3TXLi3chS'
        b'B6JWVIOuEF0N1SuJrBygXoCFtXqoo1aLlSQxD80Syon2wBFDAcqEqnW05sXofDiTQFENtAcQWVwzXhgLuQtC6H0nojelkl4YZFl5izgVJR5PcDWM0smbjvKFzAVXJNqL'
        b'zhAVUpsvtbJshYFUAn+CFuiRYCFRZQkPZ1caMJtOBbTMYjmhONEiNOolgFaZBzMF1fm5owKrAFQyA2VjiVFxM6+HjiemkyACO1A1HPVFxd6W1qjYDw/3iAmddBZHQLpU'
        b'ARW5odb79qR4fE8+cndPTt2RgomYY39lN8bfuxvJkFTu243WAXTPuVgrcMqc8RwNvIk0wtw5Osq1qBCaSe6LOk/JBALlSiK9F4Qyg4mXb52PZNyPF8pQB10NVTzUi3i5'
        b'3OAk0RmMr1YwjLAssRXoWJLMLwAGd8k1iHOUmA22Vz1ERlyG4Vw6FkaNoBMqqUV4ySw4TXLTKHJQGkmQA6ZxtBPzFpP95OeDxtbKk50L4KTIk6FbsxdYU5wLlvgr/eVA'
        b'F+hay7bi8Rkhk7N8q8EQytUS6imio9RqTZHo6PgOVBZMFTr93FxuboaLRIEZT3tVoXzK62tQNn7bWpfutgQ4vYvgTYL0WY5wAQypLaMvOq9BxQTisjxsCsglHs8bGc7y'
        b'JSsIGsgfzsLIOHhmOdRTcDn+VgykuD1ryUEtC39riZWPv4AzgaMKS1A2tDGz8SjUr2ApkQhWBVWhwwSvAkPQTKt3P0SyoI3EMMdovGmVeQPoTqCbFn8/J6DtQZlMDqEm'
        b'5l7tBo3UpG6J8pdQR3w/qiIm5ATyid4EjsIQZ7ZeYbv3JmoP3I1GPYnxYsK/XEFyf56UAMhUQsctI+g6x6FKI0xadniOG0Mj9ai5GwogR2E85k8SdE5QFtSnyaIYNKgH'
        b'T6JcjG6hATg7Trtc4CjbFSUz1BkFOryFESFMgfaiIpbpdQMU4leh1dNfDmCAfE8WEqAJNeOuF+B6a1C7v9xbPx5lsv1Q4kat5cehkJCEcXpQiY5ROpKC+vYQMoJ6nfzl'
        b'wL816AhDgR+FZle8gwWcIBWVLOZQMfShfHY+XIacYCnJ+HcKf2GiSEwNkw4xIPvFLWgUbzAvK0vIFlA8ZxW/X6BE/R7xZ9jjxBIjoXrov9exPRpdoHUsSA2WZ08iUBN8'
        b'UhyLF2qqQR/dDKhGB+VPomBy8qW5ZoKAAV5QCc9yJ3ehSmIMQt0ZIi4NXRCg8xxqwQNj1m+8rcr2ydAlRY5zQZdRJTmZBlEni+nQAK3QisrxZ30S+jhLzhIOq9MzLUFT'
        b'zOlyi5V4rQi/8PUzWaiAEOIswj2VwnMRlpW28uAJ8aqEcNluV3CLUFPZpMEuwmp1zpCrcVZbHeG3186QXdwsVea0uK7ZGhERasOz598fUYEyhuQfTU/FbdY4INgvSFaL'
        b'4dZhyprCx0yIcpTvkWdLFmTcw3XfUHGNj90Zuzs5dVmsipzSigjqn7gooCJN1Ci7RzeOSlngUktvK8jHv1RPiahAkkf1QLmOL5Q5aEUt0lqD8JztgVY9BY8MDmqC9FCP'
        b'Aj7mSDyQULyAxPKOv8tyK2tvGtXJJ2i11TqvibVsmDmxnKgEenhVAYdOoza1CCiUUGeXlP3RUtyHFh8riRXKn2QGmrVWBB3zIDthc84rQtlTeLwKV1tjgwd33nTTOr25'
        b'rMz809HEZ7qtbn77RdjzG897vWdy4LBxUWlcpFB69XiCsYftpiW2G+ZnLruq8MM099FHn1Jq9jFqfl4pJsNLmhGWu/+r507W3ppuYT376mNLf91hnDGt5oh2inteaaGi'
        b'z4zWWR+c0v1YkrdEOdTQ4GjqysX7vP0851z3aB1ZouzucuPVtzfcWpP6/XeFOVtOvf5T6Q8u5qY1vaGZp5Zk/DzkNfj0odCGpZ9WzYHT1ut3DR/vOe7sLf3EfvBgbMe1'
        b'oEP6F2pm/Sut8tX3tYof/TDvdY13kyNUN1x/+5HCfRZenwbX5J4/8lNz5KutWo8FSu3eGNEyb/F2TB06u3Stz41s51O/rFPIvm0o1Zv1dKvX9qJ5CjXrP3qhX/Z43aq1'
        b'Qd9a/fjYh147t34yuL1H5rL3YMbre6u+eOuZ3/es9O2Z+aHQ6NPOLQ0/zgHxE6sOmTTN/rli5VcbNmSPbjuWbP3Bimffvvj4nqXBjzVu6R39ZlnrF9efuDFrU9QPet9o'
        b'tButKdhbO/y83ZcOdfEj8OWdx1Zm5HR0dv+ct7v6Vev27acGru6+evnJ3ae/Mdn1zvWTp/Y9vrtgnu+sNxc9eulCn5/ldZe967960WkDvPRYXvOrKxsOVH3u+bnnm7KS'
        b'jHccP9pYEbfLqH5xi8e3b8Wviv3X+bdSP3/84IwlBhvjr2t+X9UaVfnCJ4VPNt/5qfi3uc273/es1j3kFf7CM+ZPFv7wYWnoadXggqUdp8V9ixo1XnTqMFXXi/nN+tI5'
        b'xQ/fqr9hYRT12WOz34lpXfntvq31n618ymJnYcynvnXXl4/WffHS0s8ilt76oKPnh80b4rb/Ftz9ZfXRhLGCjl9+L9xxrIH/zNXF+810y3+/WnXjd6+WJQ3bXKUnnvBe'
        b'8Lxp4KsBzgVpisGr3pju8/LVYwefcEh7Mnz6y53+5ddlewe6vDePRhe0/XHVrL/482O7PlG0zyg+/7tB5A3lNw7e4W8muV1tbX/X8ccnDwlmJS3aVPq2ZAkzzJ3dj0bI'
        b'qa5JYtWJKKEesUajDLJTDhXrxQQupmKOmWhUh05iblEbWoRwyhpqmbXhLFS4iS0kqBsViqCFAIJm8uvQGWZWg17ow+ckxYQmo2pqXt4DJexeo850YjmF7rAJ06k1qmUG'
        b'snw0touYtWeic+NmbXQETjPzVo2XGzWq4mOpb8KqCqObmLWuCw7HUf6oweguf4SGUD592V0vmoxoJSrxTvGzkShy6vghMxjzZDCyPlS15QHIUDNHaltFLQ7UNnQA9UIN'
        b'M6xCji+zrS5QZs1fgovQKHNGh6fgOkvRFYYXvGgN3WKKyoGL8XyIYFmM3JfCH51AJ+XgZqixI8ZTjQQWATo6Qp7ekmCP/Qwo+jggXQ4+xiPrI0lSqwyZ4ZKAedejeobH'
        b'q0NtkC3zI6uDiZ+vAqe6FwrUeGgwwHNJ+zMwx1HquI8Y7i05ThE6eAef2azmAlSk6mtJQgIcQlnjUQECUQODGeXBkIoYstHFe/DHGjDEVrdh3XwxtGVMBi+jIXVW9QgM'
        b'Y0mCWC7hSgRZJNESAVxaas7WvkZfR2xN4NIx6yYA023oIkMhFUE/mfp8b2/M6WDph+eUUngLF/lwglFfsticgFe5VDl8NYqBQVFDHBYlUaFVCrPhqi7SXc9jBngEMuU4'
        b'vG2+4uV4t7YmUzukApwQoIuQnUFN1Js2oXxmn4Qua2qibNzOOpsJtVBOUrn1i6WKWCYYEkCpBiqlvh8x0IzGMBsAJ4kDprWvtSqRqgyhT+S0BuVSg+5uOIfOykFoExBX'
        b'3dX4YywSYh4BDdAP0RzK5t+HRYWc+fiYhPqELXQAoWEwwgCe6BIqNx3Hbkp86V0XzK904iO1GrVNRp2pezNfn2bojCbxDoy23xfH4TxqpXtpCf4m6iYSRBIs7QHcYQKn'
        b'DYJ+tpeORc8Vp6vDUXREhWe5GgeZZ8YhdAYGZDBshorNqeuHgocAFUVtYNbm/PmbxeZWcFRiwd1N7DdK510ZTjrRaApzoYuajFHlPrZcvZhrLBJjef/KZFhxnSbdJSGQ'
        b'ayyWJ9DDL54YTwl4YgXbm926MIy3GOQF+0zAFNvNGGx32AGa7sUpFssgW4hyJeoMw9qBKqBNTNYS8tAlgilEzYvocsLgTuiTqcHo1Bx+ckyhK/4sqXPkIagXE8HxLrAQ'
        b'TqFmNht9oijiM4v3IVRE4aEr+fJzNZ3pPW8hOkVQjkJ8rk+gHMujGSE/6gFV0j0qU2ON5DMnJRNUF4EKLAMIES/BN8WbsZjfzqNOwQYWdbHLGKroA4USlEtiLs7DBLWT'
        b'R02LM1j4wNNblYgMRzxw8GdzRrAa87ONzPJfoQuXpYFYQKIihhKWwUjExFEeDWhuoYsYgvohT2yBioVcLGTx/oKFViG0WXNVOIP3PsrZN8ktx1GohC6DPMtxtrvhVB80'
        b'TgznjagTmmWyRP//N87rHkvqP494eEOVoGjCqRc75bzfJnz4f1bJHuJ0GUpRRHGL5KeGwIxasC0FFsTuTBF9qgIdgZaAFzAbNEH4qf2uJuQV+e9UNc0F+gJzXkegITDk'
        b'qS1bnlaQ/a/GzyCWap7YxXWIvRszyYYCLZ6kEzRU1uCJfXuWcAa1a+Oe8MYC1T9E5B+v+jv9JyS1KnKKNES/PsNb8kRNuVdyr7WYzEC4tSu1LcmWWd+dESZjiG6opO2O'
        b'iU2LTEiU3VAKT9sdFSmLnWQN/y+SDmC55Xdi4vttwvz9K/5NSCQVe7IA/1njepj7Y3IgxnRi2MIEd/9ksQYT178p2nCLUK2mJRSHS4TMwbkSS9wFJGm6MqqdCGuzGZ2j'
        b'DueBvqjcV+7sOOHyNAOaRMJkKHDzZOrMajiuKW8e06ka0oVAeYycOS4iVOExDYuw9OQqW6JLa6vFrNV4U6hyFROo6zDlf3Bj0bpYPrqYSIER0RsdpMQt64K5l7+1t39Q'
        b'MpkNmh8DS1EVROkh4CL0lOfjD7qHys070AXpuCM2dERSX+xD/A7oPUhlcLvFqM8XFVlh/iiE1mXnGOTlY0n4UDoC5/mKXIInC1Lch6e7mabqkKfpYI2byxUhfjxR4YbB'
        b'CWVNKN1N5yYJE9kR+dzYoN77pgadiKNVSx1nyKbU5RuwVh49mIyMREiKO3QIFStDI/SkJkRcihDJGvDWjdjwTmzw8M5p7rqna40u7vriB6mmSwBI3XYrPXJa1eMVLy/d'
        b'3AiVIsuFVYXRLQ01CbYvWfv36jV7RTpV5NqHXzVY/a2KeWPG44O7Nhu/2FHywuCdt2TxGT0n9JRMNDUMtiyONP3gnS1x7/k9d3R9wI2r2+Ypbfv1jfOBUZd7YnhbJc+s'
        b'hNnVfq0RN6Mslnu9e/3T0pRt6xa9F+YcCwdKS9fHOC71H5Ses5i2nQ/ttbn6+Mc/XjOy2/XYtXVm4UW775zWilunqOqjt2Wt7dqTh33PPfbq5SHPax8bNA29usxts5te'
        b'k7jtk5d6ndcvSnz507DiFU/M2J/1U9Xmb24kDD/zqfXthNQ6s7Qdr78bmno2rLh+aM26ns+ECr8WfhYq856xbZPvxf4vrs+ylV7rPeB1WZq6ZMmuuc7f9M4MWzl269B1'
        b's6bn7Rec5j74/SWrylafrJCWswsDpAlWeglXwu3a476I/vBZ1wPPrtqYfe3m518vKNi8sDL4k+gPRyvaUxykLksrB2eYWi/a23Ag9rKKdXf1F3pDEvPhH5WyO/PbG25X'
        b'9K886LiX/8ji9JOp4ae0vrOpDY+dHV9lqlF84K0X875/1SSr/d+dse7rPvXNerpz22sv8C2jqz3eN6n+PuPYxQKf5jU1P3/wo/PwUyZ2L/W/ECKb/WJmzNNflxakOg6a'
        b'u/5xMbM95nXlpG05b68+dbXoTf8eu+o9thvf7c34LiJk143Xw4oynsn6hn+z7G2rD333Djz69qOeHZHVzbsGrn496KTcemL1o+lHLw4PXXnHoPe7zMWu36gnvlzzUscd'
        b'r+sfJTVHznn3D0mF81feDmPut+anv2F262rBO5cO97ou3vuBzrDTvsVPGuy7fMfnp3NJg1XaWcoBy5+r2p5aJfv+yyVvKa51eUvg/ILpUoMPM6ffPGW8Z27z4tAlqkW7'
        b'rd8fOCRIl2nt/VpDYptGNJSGIdDAHNIsUfufuiuiemXKbK3GbEcR84CkrpEabgLohFZgudD9zd2JAMmkRzi7CwuQBugCY6baMdN4CnNTk73yvFGXMAgTmDOUadyAqoVE'
        b'0KNS3nLIx4KebBuVxab5oMvUdVMM5Q+I9AZda5mMU407LruXwZ6/2gnGYIw5/51Dp/1JuOlwqCYRp91nhtOmdSGLeMFirl7qzvwOSyGX+thq702mPPlhzHpgxoQMHDOc'
        b'NPoMqhRBbzyWgijvk4+Z3ToxljeKMZdfl0JHKJ7GoywOOliUMv0ZJFZ1iicUSzDPvUuATgWmsTDUFzGtblcOlE34JIatpcxaMvQGy+RRz2BwOfEQVd3FQztUOjGRowWT'
        b'7HMy5tophKMZqFKwV4DFLsqDDx+ATMzaKkIlDHD8eoEL6pHQOzGoIhQNZMgmvC/xAlbTBgNgmGR/Zg6uTlhwpT6uMUIPJca9i1IdaCg2jlhD0HmoFMARVI6ngCxx4gyL'
        b'ifBvcArGJokOeugcfV8RXYhlHuwSyByXPDago1T0cJiORXx08QHppXVwUywqjTdUwSnGFCvA+WQ5UxwFrQxqgPdilZhIAc1QMi4JLFSjb26xRgMyEp2feIwKoVUYKcDk'
        b'/wqul3TMJ2U7kfWLiDQuhN4oLKRiaa7Gge2rlsi1Ymv/VPZAGm5UW9ceTgu3wWlgSgoPqHMWYz5dgnqV6Jwpq/MxqGAm5W0d0PBGFoRODEVJk4LQoRrFNII2W+2xgYIY'
        b'Vjr9OYxBOkse8AtKTeXya5MnE2GJAIvPwSameOiBpiQxFV9R/6EJCRYNsF0jRj3zsMjCZFQstWaT0Oel6BiTpgpRwwFm28FbulAePHAmnKUfoj+WBYbusuHoNMqRs+KE'
        b'D8fcw6U0eajZMhHmXti3HLgfCgTosDWqYQJElWeydCL35eoUAcryhRz2EV1GTbpo2OLegIyiLfPgApWqfKEJi2B3nfepXCbgDGNF0ei0yRLoYhI+Znegm/jlWqJsdIlu'
        b'WOXFfJQ2Ok6diW3gEqLexJZwHJ/+UxibOYYi1BaHRtjKY3ZjDtuwqADyttEwWap+PBw3RHWUPvim4WcKCENnBXnjphcflE1YDttQxWlQlkrXGA2Yb3uwW3igIuqY8P1F'
        b'eZq04WkrvCc4RwMgS1GixGmECu2w3NtB4wEtwr8V+06064BO3rVWo1wF6IUOOMxE+lqUixvC1QViqc9airJIs7g6oXAu1EfLo+ZssWK4F8wX1THsyzxULJDo/H8Uov5X'
        b'wWImB4MxG/dwee2viVM71Gi+dCLs4H+8Fq8vmIWFlhkkczoReLDYY0gDwRBRRwdz/EQQIsKW7q/KSrNTsVCEy7rCGViyYrnNVYlz8R88icpBUk7zJEaHskADi2rkqqL8'
        b'mqpQEQtY/B/kqqJQmVcWagjVqJOyIk8ENxZwRlmBxbTXEYjwVdIjVfzs/U63VIySi0zMu/f3/6XbsFxksp4yybf+hpPK2T/3GabdJ25dhg/Mdq4XTjD10WlMMgwnAHqS'
        b'Y5YmPKf5z2nW81L844aS3H/2htpkd9Yb4smOpQ7kaWIuSt1OfriRHwdIOyoT/nw3lOROdjfUJvu+3VCf6nNGnJ2oww6dEDb/ev93ioi7Lkfv4uadyHoc5GjoGQ0Rbykw'
        b'i5KHiBH+H/0vUhOqCal4hRpRDSq9184n4KbDYchC50Wx1joP9+py5TgWIYWbyAWsNOHhxf99BztyIFhx93p4rQpIJ5kmUDWHshxsF9ovsnN0gAF8fqSlZqSkyzC978J8'
        b'Xjfqx8dMH+rRVFZT1VBRF2O2IhcKURmqDF6Nz8zqGHRsnQKHOtGgWIzv9NNQ5Kh7GjREmRNHEzvOToB6qXfHDCz6XkJHoM0Bd8Kes4cuyGePnw+UQImrA098Uxxmo4vU'
        b'FwBzkaedMTEudlDkuIXcwu2oMV0LX7dcmADnZpFN7Mg5Qtse6qqBD86LkvSdDng3LOIWoQrIoXUoozIhsUw74Al24pwwy3aKxUo/C5et4KKBA570xdxi8QH6tAY+1ivw'
        b'4TAKPRyBIi7ZY816cno2GkyHS5jXxnI354wuSlktnbs9UOYyMqcruBXheJj0albMSuhQkeHRrORWouEodvUUHNtttUqGx/II98gBNJZOwsIviI+UGspIAgzMQVUb0fE5'
        b'iJ2h2FeGR+LJeaLsJfR1kS3qmIZ6ZEKScGaVOTpLRx2ImnRgUFWGR+HFeaEzUMv8a6qh1guaDRAZhjdmGXsRu4G35dABzBnUElsM58P5oLodtE3btORVaxGJuODL+aKm'
        b'ZWxZymal2WFeCXfZj/M7BOdom4tSZkrwwvfgTvtjdugYjDJfmRPJcUaYHe/B/Q7gAkzlyRzQkSholGCpowf3PJALjHJms5GPhpRik1AP7vlqbvUyGZ1nzIVXGoag+vEQ'
        b'9iUoi10vWYIZzWooFONer+HWOKBCWsssLzQAbfFinjjJBqPGnazJ80k2mCnvFeN+h3AhcNyNXrZBl9EVC7ggxh1fy61FXfPoyGP2eTmEi3Gn13HrCDfLRl6Q4YE3f4sY'
        b'd3o9t37BKrpYGaZzpuHO4S5v4DakzGZdK4CsUMxDdUEBLm3kNqrPpa1p++Mv/fxGKMA9DuVCA6GeXk7Gst5xPcwdFuA+b+I2bUijtawNjIJMlIPKcT+sOWv82xU2TU14'
        b's9WsGk+FkR5EK1mLKn3RBeqZRLySluGH6SdwShM1QachKsd1Sznp9tV0gNCN2gLsHYPxsE05U2sF2qAjatsKV9B5VI5HY8vZoiFNWkf4UjiyHp0hHhnUG6PDk14Wwakk'
        b'GLUIxt0z48xQFVRKLKmzgKIdOkEdDgqkNqhESpJPCbkNUDkNnRaioWAoSTeiU1+hYw+V9Db+IYQjqdw0dBE/sQOO0Ce0YMwHdW4er0j+BKkDerSZA07dbDf8btgcel/A'
        b'6Zrim2gQClnmjb5t0IUuLLnbF6EOrqAAPxMKnbSJFRooD5rQMdYL8gTP6U4jlbSjTOo+tcoYk7xLGqwG+QMC/EAgOk8bScJUr5u2UEdyKkmV4AzuJQziR9ajfOaZ07fd'
        b'njUAFXZK89j7cDqNJrVAFyAbb/xM8Xgfcf9M5BOBWy6hWkEtdBZ14iqmh5FJMObl04AKbeg0JG+bS99GJdvQoHCefIwmeBrIy8sx03sU39u1lE7zGVc2Qi3oo1OAcjyk'
        b'QJw5xqdJKUrefzdMu4hkZYFnFEudWNIivaOP6LBBpC+gCx6Lmjh5B9gIyIID/kzpKLAETkdqTQCO66GY3sbfYjfBapK5asEPzYQa2hs4F4i6vNayDcEecZXPhtSKKnnn'
        b'b0AtqAFPDWuQTHnU+HxUQRXVzgq9UdXdAbFJ5fBKn2IzA70RzN/vnHMobSnLHh1F3anyiUNtUEabglFOagQ18pZoh8bXFoseLXRyVromwYiBlO5z+oQrmxp0GEboBhFi'
        b'Yaw0zWyiO0rQOD5oVOZIH4E8LIpcxhXAcDJ7Zu74DshHefLILOp7ya1gOCtVWnF3B7RF0BqW2SISEaAAd/a4EFONbtbTStLT7Dl0sBEZybgFHyiQ33eVV2GHeuhgYw+k'
        b'TEyp/FvgHoGLbEosjSkHswXGN/vd1RYSZ64GNis78FFPhFmHOC16S4mHrFQ2H3FQyQaSB62H8MvrfOknnTn+0VubMQV/m9JeumJYbB8RCjldJzLKk+gSHeZaqDGD/i3y'
        b'XgqhkW4gNhMls+kG2gvnVi5ADfIviTzhysgCVKIOtupng4Ogdc8EdZr45I9o00ZsocpN7HR3yVkbbN+gVtrLLajUQGoDp1Eted1YwCpwRBcYSYBhNKaMiXrBxNcQJd8U'
        b'A6id9lIjFuWLYWBiB6Mj47scRjazXo6YuxKKUYB5rRIhyqTjIHUstKQ1pApcUK0uWwU61KjxLdOLjxXyREQqZsDa8YWJNVVaIZ+s1Gl0GDtQuXxfStWUlVaOj7IiUiJg'
        b'rqMdh1C/L4mQU22Jf5KYpnCRx9unMvw2ZSKPp7pJVKkbXUqUkGV0MtMyC090ZL51yfvlqX30RavUDYXsIlpMHO44W9s4G/2XbWaxi1+pT+OICsL2YFn4Ok8tdvF2JMka'
        b'yBnb6q+IOi1QZxetnDQ4/N0Z2uoHKIV6m7GLNrpKLLdPXPD+4Flq7KKHVJvDdGexrb7X9MoIK3ZxWShxIeSUbeO4GUvUNdnFIwq6nDlp6GC6rX2EIruorCtvPa7PcaXm'
        b'ZnbxhIo8cZXiMf7fakEc9ZJ+VCxPVmS9YOba/a5YMgzxpDd8TOVVmM1d46YhY0/LdOV5iBRdrTaFzOZun6glf55eThv4dNZ4lqIABSM1Le62A/3z3XLKqkVidrMRc8in'
        b'CD3jkrikSKhgx/xQKCr2fESKD+7d3G68LQ8zh2VK4MemwTmByQP2GrqQQhs9f8hAnm1J5jfqIh//ihT5pARsWHUlcOf9jpETQcPIGRcvd41kCZHuJkKSo0FuKCTsjInd'
        b'nUqYuAdlQtJUnZwJiSTMzJgBjdIA4iNMnQ39UaeGXyCq/LO0UphRPyF2h0E4TAfwU9gGrotsNP+t6zZ6hOFlCQhIWJb+qVC2Fjfu6ejuv+bZndPctT6v7bvy75+nx1/5'
        b'bNXuo/HGomRjleOHBX+478xNtlCQuGtnpL57XXbD2Exp/iEu54fKF56qtXn3auYLbuaN8VmWGk2nWzs//dTa6hUVd7RSY4/uu025OnxFkLue4ysvXp11omZVrr7JY1ub'
        b'sqz3briqEPaYadgTepbvW3S+57zzXbOdkSoDKUrPXi6ovPjsscS39677IqhRc3lopcVn/q/mxV9ZmqL3Frpi47zv9ttbmwr7t5yoL/smsdjxyzvmQWY5SitPfHw67+lN'
        b'4dcPnlz8wuDxG9lrXdMGHnvW8Cv/94ymh2+wCFp545MTJr8kZC617lLNK7BL39qmW3Tw/aBzb9iaBomMg/tHrbrqzV9fHjy2SO/fgy/NDf7opUeKnG6JD7yOXtFIDXN0'
        b'7Ezd8075jMuLhhUSBAdumxR+654l7PjII+t35z293tMcQ7UK3ep709pkS39omf/5UMRnt2uee9oyvTZ2XprKwsvPq7tWqc/4qHZbo0bgqvhVHk/+8uTBl5pm1w4mlhsv'
        b'eSEiqF/5LX3XAZu3P3hnt3PQnN8jXj7z5sKxrsqqxTUWL1e8KXR6Vq32yRMqg09/Nxz67RoXhfeyrYXTol7t7Yo12Xku1vWD10JO6g90WVjv/TWjcZV0g/0l4xeO3qq6'
        b'GNy3uOrTwzftIx2Cpu8y/u2mdfrTH38yuuxitPHnGsGhKWu/vHzhkulsuyc3PLOh5f1vsuYVH52eZ/KddqJlfHLIr37DqjZff3v5qdL5w/9yVnv67JH12rXWqxJe1dl1'
        b'a07pnuc3rJPVnN98wTTvjxcWDT6/s+fFNz/+5eOZx26GOP8uPqH/ZeRLjSOXJRpU4a4J2euICtbfb/vGQAVOYb8ANQeiEea+UhwPg6jAhoZoMLUTeQmgZz06yRS0J7aH'
        b'YDGs2Jem7PMlYbPF6KSQ34jOMLecIY8VJBINGsCCIPRbC1UFdtAfz+o9iTmOaikqhg4fBc50lyhGACOr97J666HACs6gYyRMj7elt4gTZ5CY87WojmrGDdEwqva1xMJN'
        b'/uQEN8mQRVXTWnu243ptcG+wENAuShfgT7B7HfP0OQw5qF1qbUqzxPDQI1iH2jfJoywExTEXNha9pZu6sMGpdVSzGgbDrtAYIY8focCpKfLoCozMo7VqQCGxDBRQJXaI'
        b'ushAgGmBGzVVrYjV9Q1ErYosNao7lt0HmEp6DPow+9e69b58RLZQJpn5f+sH83CdodLfVNzeUJVFR+4MT9gRGR9L9bc/Eur7V9xhDnH+Ip7GRxb8z39+o6jNQjeoUocY'
        b'VaGJPFg2C62ti68qUt2uLg0goSvXJWsJdIhKTKiLfzOmgcRVaTBvZYGIF9FgEDQsN/5rRnOXqtISCQRugt+wF6QSmZ4dKMIbwoQd8ZNUuX9xYtX48VOH1DVM/FsWkhn9'
        b'K/4th7knDSd7uBCm2QWq4dikYwoLz6f8/fA3r79FpJxmeF9EV9XxM5OoaScBDAVyQBcfpzoRyVX0p5FcHwjbJNiD+/N3GwU8XK1IvHtw+3wc/0/Ruvx97SoE0HNY5MQn'
        b'G3E0BaPlM6uTuHSauqsLlRuqsWiS683lYERzL+9gL/LZeytwTvsUzRXhbEJBxYsKMhIn5v3ClZ9FeN2xj7wWZ172cUTY1a7jmaVnsu2OttZeyruUNbcm08GIS3pF8aZu'
        b'g4SnJHEbGkOnCS3Ni1AmgBZFV97AChWwKC+DKHs7MZ7vcX5QljRjyB7HczxAs3xDHL01Nnp7OOVp6Gdp+9c/y0OcOYukv3dOOAlqHE7CJdx19ppU8/hWFyRM2uj8lP2s'
        b'MbGf1fFveoSLWvTX9/Nh7guNyTvajWyf5VY0xpgXpsEM5HGfexYBGfmjYkUsA3dAAZyF5nU0R5EYnXbdzdA/3XBODxpRqa8lyaVTKOIUZ/CqcAGxzLAkclYWptjDUlQW'
        b'gOmJtoDIGnSzqC2icsRiD7UItTmqliRLJ7Xad9so+/oFaKGcAIJiUw7kZav30RdChZShj/jRICLxE3c9TkZUZGFxl4PVk1OEJGNN1PucgzvlvK+7UHZ88RH/CMu6eZh5'
        b'J7PagDcGOZA4z0S/rGT3iDhORhjqa9+PTZsZvDb9h11CTqggMH1mDZMUKK6Is33PMyLx0SA/TkZ4WQOFeR/w594iYE2xtow+N6pH2fjktaYRfgar/NlzX/t9/IFC9QwC'
        b'NNYYtJQRvneaed8HH/FEgfbadMOv3GSEyW/7xT54rXqGenIIZoet3ioRVAwYyWj8zvQt1ATcau7jvwGTlmmXhB+6ttDDgiKy1f715cuaTz8eYvk0/n6UBLz9U8/Sdl/9'
        b'UvwylxGDNwwn2ehOL0W+mfiyKAqTPgvOYlsWvdT8VHCBwB5/N5u5zY/epr07/PPnBS+ST497Z/bRpYvptdTV5gUv4hX6gNN2O7ZzFVVwKa1wQAXeljIn8iU54EmGAt5n'
        b'MXQmaIq7OdlZvLpPaD7nscY94JabWl+8/dN+vyuFqi4/8+n0IbcjetVbN1Y4dh/3aW57xHLpmrOr7Q4FlSooeVlfLzcOeNmjum9B+Kdm0UuXq32wfLnLwYUlydHKT7v+'
        b'qCzSLp/38YpDdW0qZSdTPis7eTyxOP9DxQN2r4aoxT3WMvZic/L2N/wyFFN1DEJ+797k1ej5aqCM/9Dl5h01XcVHHl3gtLL3jumS/pAB25oNXe/rXbhc89zhF00jVn22'
        b'brRNy9c64aLDb75P3Lm5eVH7HPOAJPvbO4SX1ph2hkj2/vtDZ8NL71gaZcveuNpZEBPtFdDd4rsjVT3x1oDm5+W3t7kFfTf4vOzpZa9b/jrn/Xmrv5zz2Yfp0llvDFxf'
        b'EaayvOujtcKe5z+7rB+rtQDGVvftVaz4wqvlnXzZ6tMJjgUvfPVCuELgR1t/Lvk+4Pcn3v9p6zenbqtsPrMx3ePJT/Nfe7Pl+cY3jmXZrsw4P/Pap6+krdv/x/TnNj9x'
        b'1qRw952fxw498kSCv5WR7w869dfjDL568ZfpPScP/PC7wvPvTtt/TFobMBK2YHhYvODaR2vaPokYnO15ZUHkrWfNvn4izOc50+ycQ4Wd9cItlRItxtMNSqzNMRMqIX6G'
        b'ipxiPG+hiqooT2cMR2cRBkuQzMCDynCcT4IKdIVBD4YhF50m7iD+WJoU2QlQyyroIAme6Msz0AUFytRtmEsM6gVK+PUz/EGpBiXIO+EEuiJLy8hQ14BiTU1LVIm61VLw'
        b'QYrqhHAaxlA/s8ifQ1k241wu5nGdlsEIJlDMbVwHmnTQCVNU4A8dxO0lW7AKiiCbeX8c34mK8LPtUh85Y6m4htdFx6Ga1uuJ6gm4kd3BDOcW1A+NAmCJKlEJtBlhVhXl'
        b'+MtbVhGTmJxt+rRZL8wDX1GR4bclVsSnQjGCn4fyGZ8LpXAS2hYslk4GkKAjBowvz3REA6TeXG+SHlOM2ePzq3iER2sjH2wYqvL19kenUJ18wjfzseZK9KYauoy6eRik'
        b'B9z48ZaGZ4Lc3IWaIBMdiaBAWz8JXkUXXlcT2v6hyfu/8Syews3ePfHosVn1d47NBRoKNDkN5To1BPoCLXngMC3KT4rkAcVIihjCfarR0GJqcq8BZQEJREZcvrUo5yri'
        b'iWu3iLl20/d0aCAylv5FWZCqOcFrKtwQJUembb0hiolMi7yhEh+bFp6WkJYY+3e5T2GqNqlTh/zQmji3STu6f/vc/nL25HPbGL/5SByU3z24zTBnxQCa+v4iXTQEJdH8'
        b'JF6N9GeCBSQMMLUrC+KEE5EE+L8f12K84ntjhuAjnGhFd8HQDCx/Esh3nqV9BsrD21kHBoToCP64DyccdVoslJGPoulU7GcRH0d8GuEX+Xmsaty7fkJu5r5Zx4VrnEwn'
        b'xRcRPtTsf0OdrNDUfWbxd/bZ1tRpE2svYitF1+zBPBh/74KSl9f+7QW9oDV5QYmu/QAanc7mKwB1oKFJDJkSZ7pSIQRVzv2fr+l90SHIH+F9ayoMSDC6WcvTDAGP2B6h'
        b'y7WsNiIxLirGK1KZLtmcN4VeCqv/4oLJ/tmCbU/VvXfBtP9swbSnLhh5ecPfXrC2KQs2H7/piw6nSAPYgnV5TV0vVK8QAQPQ//AVI43nkDUT5IjiRP/kOyTrdX9CB9UA'
        b'Zn4ZxAfrZRN8vE/mzPGp1sw0wd5z+P0ht1W55PcOXY45oUsvWuxmSm8tp2hLV09Lph5ODeXI1d2HY/aHv+m5laWvn6OKLgTDBY6graajbA7qoAqO0ud97Zlim9u/02+f'
        b'sgELJSJ12hlshaqkXlAT4y3kFDfyArzXixOMtjSIZOmku6NLja4Nq/N2Wtnv1X6z9BGhV5rbEq/mbKlbdabyldJy0zOimF17R33Hwh3O5B+7eOSMT3T0mQ+a1IJLz06b'
        b'pbnY4e3qzTmNJ2d1XjuReM25UWPR0fi+0flbbndGCy+9vmTvLdeX7K1k7z5/bezgzTkXF7uub641ajXtkDCn7rnQjC6iZjQqtTIntg9FOMFbwUnEvEm10IA9YYXwuQwN'
        b'syd4oUY0wnI15kItNPpiUkf4oQMzA0lsikLMkkSaMHXdkY3KDDsaM39c36YDo4zd6DiwG/UnQzvlVFCegMT4NkFHUCPtlyreSOOBV6HKUK47Q437acWmMJgg9aLaLxFk'
        b'wgknAXSimjBWcS8aCbmrkxPBWXSCKOWmWd/3eeIP6UEH2d2PVo1Q2eSYuHByNtJvdtnf+WZ3Euc/DaLwoUc5OcZ1BKl6k75jsqdviO6BNt3XTT5Vn7wTPd4vWsWmv/01'
        b't+jcS37higGqZvTXyxsfrGxK55jhzydbhM5hJu3sfZRSRf6/TP+eVGEVwgq1CqU4PoYvElBtD383gE+ccowwRpStnCUIFcUqxCjEKGZzMUoxykV8qCIuq9CyKi0r4bKY'
        b'ltVoWRmX1WlZg5ZVcFmTlrVoWRWXtWlZh5bFuDyNlnVpWQ2X9WhZn5bVcdmAlg1pWQOXp9PyDFrWxOWZtDyLlrVIOjM8KqOY2dnKodqxCnFcrHYWVywI1cZ3iGZLBZOy'
        b'OTHG+K5OzFyqsTK5oeQfuZM4Ev5sNSUxDclqZbyD3WIpu6YmrsGMJKHZ91HQCX2XGyePkES94+j0kvNPZYKWiv6UlgopLRX9nPUf8yJN6endvEgPy0JEPhCWCIn8RvId'
        b'RbIqVj/iaRyXkPiAlEpTdhbZ1sr30fPZASwlSw3ULKbf+2ovdGor5vat1smhWHAB5VpaC7hVAiUn1L6bBgBD9TCsK05OCbaGbnx3/NEQZaJuIMmJC1lArGhjZTUYmUV1'
        b'L4f2LqL5aIWcGxqgEW6gSoHaj83QkW1SEj9kPN0stMAQv0+kzuyOnUGoXroPZfn4swTUUgE3bYEQnSTRt+lxoRMOxb72PjwnQBdlxIdkAMs57BYMK6JjmLjSTMpQDXkC'
        b'O2g0ZS4CvZoOvuMx7MVJPGqASlQ7GzVRfwyVyDU0zTvKg4bNJEoNCXSP6oUrUPdSatSeC6fsfeGClz8qhQ5rK1KJ5jzhBkwr65jRuyIMHZYLVWRUMIDFr7P8vmBoYyfo'
        b'OTXoxkKZBX6AGMQL0GgID5lRqIb2LgWaoeluuCUfXgZlqAV605nDUv7uCJbIW0iWrozFXoA6d6YXy/ZGNSyiFb8FS9M9AptUdI6qWJxQVxLLz66ASRNqY3Grqg1Yl9r9'
        b'UMOUyFNawlR1PWgKpXqvEwEiTnnhPCEJBfeEZjJHPcAChI7EVQwu283l5oZCHT2k3Xl8jil/RZ60vGBjT7RvxqRfBdAG7SzO1OQoU1C6SWEJHNvI1LzzMD/gFYZ/i1Az'
        b'P6DF8jBBHSqcy7Ksizg4vpmGvQpARSx+0xF8SmbR5O5rlk+NfNVI58N/TRSNfEWjXsHxdTzU6KOydOLnnxyFcu6JS6UCLZPT/g6hWvk2RGegk2wYqMeLlWdJ100DNQg3'
        b'+8YmNEp1BTRDag9sP1A2vAbZanns+qjoo8VfDSiMlWo2NLc0pTSdUXbQDfAZfFTXR1Ae2DVztPxVT9e4wwvb9+3KSE93/feHfeuL2qq2vB7x3vn6/tGBLP0rX3593qO9'
        b'4c7NlVGXHo3/Pu919dfejTi0z7h9xQuZ/mo/dnz+U4Xj9K3HjT5bd3OLQZqZs94tgwset393rUw3d8n6+JcXNZteaJqTN/OpL984di0v7ZjRax9/nf1qWfqw0ZL9fhtv'
        b'7Uve+qTZK3mZSo/fDnmrMLzmKesbpQIXp+sBX4C1y1ppyaXhvY87Lwkcbj61RO9fG57beMHD6v0P37QyemfwZIX093yDssGdzfpr1MdM1ZNUhr844bJe0fmRuPKbi1Zs'
        b'VP7IMbisqbzt7ZqymjVrnU55lHnYFcwvGDUXv3Yo6CVNnyEv7zHzAq+fkuxfL3plxacLYrUzastGJbsG36r+bqym8gkw+j58GffvwzU6JgckMxif0xWN+uT8CJQLRIQd'
        b'sYYLTP1RrQQlvn4W1uy2OJGHcxTgm+nBQPcFa+AcBd0zk4Ay3ofng/gDkI1qmNHvFBw2E/tCoeV9qUO8nCgOJQqTlOLJ6Q0mlPxQYilCFxdDF7Os5irsIRYcKxjbSCgd'
        b'YYq3wzEGLOq3tMAMwASdE8t4NIyqiNfTKhrxfw7kwzkCn+P4DDUfgbuZEcPmn0NdBEhogy4fmkQC9VGdyNnSgVozp6PyeVAQSEigw35homCdqgkL4DK8AxXRCKaY/qWg'
        b'OiGqF8DxWHSGsnGBqJHEYAq09kEj0fJUHluFi1HTXpYCYQCVo0EogFPqBNZF0C2MDOo4CeGMFupioyqIIGCfbagqkBBDRgh19glhwMGVPqALF0jC8cAJSigO4hPE6AT+'
        b'mhjoDPpMVpMsCXJKKDbl93mjBnR+He1kErSgFprh5ggqmxRw4VwkrX2tH0UiYZoV6DFOtTRVhGlQgjqYMrEdckkqcvyINjpK6YeiMj9dHxVT9M6WlQFkveD/MfcdYFWe'
        b'Z8NnsPdSUFBwgwwVFAVFQRSQqQIqojIPS/YSwQEie+8NsvdeAiLJfX9t035tvjZpm/GnK11J26Q7TdP0y38/73tAUMyw7fX/4YriOe/7zHvP0X2MfEiJhxZ2izGLiWbc'
        b'ENcNTbkEMo6AKLNuzD3E9WbdoJezkUWbsnYqXu5n4hJ5Yq3mKHbCMa9kE/pSHx7DCK/NPVX9zhgyOSpjnyKvGYjl3G5uYRZMc61kSF6f3cnzULVwse02mOYgVQ3rb9H3'
        b'946x5ivLNEjriBgewWO95TY4DlBkjlOrxU0tNTFBURWMmsg+366k+KL5EcwHyUnuD5mY8WUl97sCJSWuvgKfIqQg5I1yLFGH6yDN/bC6BixtR0kkIsleTij3Tzl5HS5p'
        b'R4nrJbDyOf/ziZyCBuc0/qrvKAnTNaTi5NPtAqQpPxprLQEKX9puKeJftVhzXPFfWbOoNFid5PPMYr98VfKNn1eC/Tu0Lr4nwMoMK+0AtnNl+KXi6pOy9C9e/99E+LZ8'
        b'QFJkeOznVOT/7vKC+OmXK/Kzt4KSUxJfoO62tL64TECwZfBzp319ZVpjp+igcKPIMKPIZL7j50nLkyun8GK12q8JPucGfrgyswFXUTtREhqZHJf4Qn0PuPv+9efd91sr'
        b's22VzsY3OviXSporBsTEhUaGRX7Otb6zMu8ervp9UFKyEf9SyL9lAZI0SUjK53V6+MnKAnauLIB/6cVnD1uGaS5/7flzv7sy995l4EpehVoEZfwA/8IKQiXBBDTPXcEv'
        b'V1ZgyGEV9/SLl+y/v3zsy9D63InfW5l42xro/tenXjYhPXfq365MvWu1Ds1OflmBXjv9qtk59vZ0rItwJdZFkC/IFtwWpivdEqyYBIScSUBwR/i8GBs25LMmcYXPibH5'
        b'igXZpT2aP7m0brdfDvJuREi4lsjJEazn9BP4S5Tw7Ry4lsSxccnPWhaesS4sX9IzFn78zh5ZrtD+nLWIFdpfKbMv+s3Mt+VMhJzUcgs7NrEOeKSS1jwl4mJJ7HNKwd9e'
        b'TkbmOut8ebnjrkA+3XCZva1s9UnoTFi4JNnz+TXk2bS/Z/yb5dB+af6dKahaXUuei03GUhjBRzgpNZfAQCLWmK6I+CRWPxUvw+kGsCinDIv+d//tTpsvGY1FV/quh52Q'
        b'c9oYzH+NOW2iwn4XWBzuMbfstNk+I+7+EOhqmUxreoo1QduH84KnlRd/zy9y6STefeErVv78K06SJPPTZAmfis66J1w9+UcvcNHFa1w6LOH21jZW90N6zXFY//nXTOoC'
        b'u+a9yvTxko6JiLfpjMPAERg+xwOBjLoQem2hjvN+BMA9bI/BTP5FGSshDdiExZEKh34jyxGrd5QfXg93CXEPcg+K+lmfJCI8Itw9xDXIM0j4J8s6vet6UXrel369X9Yq'
        b'PkwgGGtReOPvrs8Era0fwJYokYIIX93rq9yPWEVeTZSu+cwd8YPff/pW1k754QvcSvXqELV1Jn4+3eVcanzJfMGKS+3LUl+PZ0inI4vMS+K5PtHatVbgJKOk5MjoaKPU'
        b'oOjI0C8w6AoF63EQOU8fJ86QphOYLlCgZzSOmlm3nYi+HNnXfVScFEDfKDt/8NvAV4ONf+UapBL2Hv1mpiWudD993sQ98HjS+MbyUJPXPCfu/clPyd1+IGqTbX2Unq1e'
        b'U0PhsSi9jWMWoYLC/WaB/q+cRaOXy7/WCs3fOa8j/5rYss5KLHjtPT2HsrMmChziG0EJTJgyLdR4q1QPVYMZsTM+JG2X2W3OkY6d98Tuy2rTKGCDKEMZc3k300AMTD6x'
        b'oLpDqQLMijKw5yT3erAPFnJotCFyjVV4Ajr4ajomFzn7bDjMPzHPXsZmLjgp2c4A22FouW0D69kwhMN84036fcSUEPIMDMkI5KJF9E3/dsiO57srjoTEQvkFN/rSTE4g'
        b'YyCECRVDKW/6QmeXQmRSAHezHM6c+qo4o82XGuT+Z/HSXOUMmVXa4PLwq7jXc9b0hJ3to0f/8QL4lKe1rkK6sgQT7fXKTayqK8H52kLZsYiZKsZCFhMZMXlbYVl9eFth'
        b'WY5/W44Xid+W42XVtxWWRce3FVYkP8nydnjq9a93V1xFdXTp1+vslNiCFUQyYhWhgf9/qtKDmrKKiE/e63RVWuEbsgIlKCWRYUoEC1YOz3BqLenfSfeedhrKVetVC0JF'
        b'JcyVJp+nmqeVpx0m++WdhfxbJEooh6rcV2DOwjCBRIFzzymwsUNVS4RcALoyjSsTqhaqzo2ruPKdLImsGqGa3KdK3Gr0QrVKRKE7uXe0uLd0QjfcV6Tvlel7AXuiWp5+'
        b'9EI3lsiF7uLqVchK+5So5qnlaeRp5mnn6YWphG4K3cy9p8KPSz8K1Yq0Vv0ScehuzkEqy3nwWMcdtTx1NlueTt6GvI15uvS+RqhB6BbufVXp+9zb1fKhW+n9Pdyc7E11'
        b'7q2N9IYi54Zkb6hx+9vG9kc7EIVuD93B7VA9VJsj/cZvq0lxgv4KCpck/uwgXcwaiu5gtPYJxgbo7ySjIOIAq/kC8xcGJRsFJTLDS0JKJMH+moHCSEznng+lr0KSmUIX'
        b'mWyUnBgUmxQUwjTapKfcimeSic/EJUqnWpklKGlFFyIGFWsUZBQemSqJlQ4bl3jzqWEsLIxuBCWyTmS2ts/6LZma9dQGV/jbydM+DhZGp+Ji9yQbpSRJuB3EJ8aFpnDL'
        b'3bbWYys1oUXS+T2TCbG2sMlKURN29SuFTcT54s/NgZC6bH92+ekL4o7qKa/tMquOWd7SCzluV06U6WB0rauvYV1li909d2WhFkZnOGtUaBytiJQzI0laZFIy++QGO9lg'
        b'qRlHso74IF2QVNvm1/SMDn4jki2SvglLoeGCQkMJTJ6zpthQ+t8oKD4+LjKWJlxtrfoC2YVd47MZJqqeXKcJqIMZ6FhdctRlxdyNlVjiztUHPe/i7gmlV5cri8ES5ilj'
        b'txPmch7qfdgcvf4I9N4ZKEjhbfWpmKd4OwlHOBn7RkYyVpl6QoWyuYuMQHaPEOuhUUlatCMp2lRegI1mLDEW7ksT7quhF3K9zbEHJ7DbUiC2EIiwSf2YaCeJ7oNcgko0'
        b'TFniJEnoi0+aZRlzfvaz51mLrMMmslARgAN8+u14YLipSGCNZYIkQRLkQTUnyXVtYiFSRttFgkCVQkMZAdf/Rvc63Md8bbcn+8J8rg9XiRmWevDVVs/FyWMmdEIbt71I'
        b'EmTykxJkBXfxnoCmgEJsgarIZlyUTfo6u4fmitNlR9Vgv0ru3V6P9mPfenDQbUDm3c3RV0TlmSW7vCvsO4rfF6mEZZnufONn+5uFe5SzzT+7c2tm04bfvOua+2HyDqfu'
        b'38wZb/C9vMtC8sH7/SFDfk3/NSh3TtJ+PsAmZVhD88j4/vevLv53rtnczPfAseDs/wnK2vDDN38+VfL6XM2tf1ZeBRPNj1pqK76rBWZatltHTH/45/0fmGz+a6/MhO83'
        b'fvEnzZNbR3/QvOWTje8qq9156b8GNrcuvXY0MeT1P/6p8xd75PR/UWb4t/8+kWT6qokOX5/xIS7p847/NBwQBQsPXIAh3h3YedxX2W21p8/uOufrM0PeIZVhCxWYC9Wr'
        b've/Y6wR93MCqRliDVRuWY6OYI9LDiHvP7/LBUBhb44jELqiFPO5bFagJCWCp+ithUyxkKh0LOFnXlARONz7SwkROYAdlijoiaIdqrOD8Ps5HJFhEcoAnu+u9cgIYghI1'
        b'mBKfY0XxOYH2ik6IKSsGXIJtTFSQgz6RmWo0t+E0Fl72xP2J41iogEWi20wv5961CCBwzdIhYZpOS2abEFroq3LOoSmBRhwwtTDxuPQk7BzGt/JdK+ah2cSUr4PONFhC'
        b'M3M5QYipLszIuDhY8Q7RVugQMz/UUVvuTOS0RaoKOJZsJGCuvTpCoCIvTzcoS4J7XtL1aUKdGMqw/7jUuYuZEuZe81xGdLMwNW+xhwkdHDMKkNYwzIoPsExXVrmcSymC'
        b'0n2smVsp3xTtyglnGJeHsivwgA+HH7R3ht5dy/ET0r4VxSm8LzjrUOjaAomY78tqJGInPORTvsZ0YYyFSNM8yxPKCbBPYSMNtUQXUvZseNmXCexez6Pmw2jlV1ERbFjw'
        b'uRwXwq7GhaOrcH25WRj7Vk5h4L1e6bprGfNzemSvsN1Vnq/P8SCK+WfX8XfpK9NmbNlmvryCkSn49eo8yecu+atYxmU/30Z8TFlqI35mshUvmNUKH3+Wca9i0i/oFuP8'
        b'Q8mf57E5sbzExL0sim01T11jpOaMgFyI4IoR8P9fM/V90lJvCZ/azvI5PWN+tN7VKOQsyomv2HXtltqUo4UChR7h62+8bSLkG0TM34ZHK1jqwdpY8IjKYakVTHyBUTnx'
        b'DusvuvspMEgKiQ7gMiu/krXY8YWgf2mNvfgM29MDHGCNKaQKIU6zX9y9zDGPpKJK09UECWvXNR7rbVWzc8DeLwgf5yxdecKvFD6+bsj/s9ZjGU/OIJocBQ1PE20WRFjg'
        b'vtfVDAZ8+HhC9oGX+xkPIclXfSySo0DZxmpHZNxxHVESw4VvFU3/NtBC6zeB3w423rg3yD0oun48LDr4d4HvBcaG/S6wMNw1iPc21CoraNnkmIg5juEOi5C5PscQQNYy'
        b'0+BZhp0lV9H2BjbC43XCf3AwjkvzZafNQV3UsSvPcAYGcI+gjlhDFmQuxxR8Pv1fNnsnZn5ZIFxrz37Gor7WqO3xQvA4vSa2mTU3V2P1sZ8FR0Ns/EJo5EzVeifVzhBE'
        b'V5uI+Lanj0jimXJz22i+YuImSekxV7Fmf6y3m6me1RMDdzl0R0bt3CrLEbpXnD592sAdHe4a4smZuDetMnD3iAVfUwo0VQxs7XzWxP05fohs4YvauS+qKGnIpOs97wpX'
        b'mbu/YPqTL3RpL632RTx/GUQHGfI+ny4wAx6L0ia6IEuUQXaFMoi/MBiaiPsnPc9og86SZFKDpcxyta3j+Xp0TKIkjNdZn4lCWUfVTZQkpyTGJtkaOay0H5fuPtAoLjiK'
        b'tO8vUFHX53yynikM4iAfy+I5kdztDFaQWnjG9+xF8wsXXdaLnIbMg4pR225xahtMhmC921Pq7BqtDR+qCc4ry2PJtsjI2Td2iZK86LUdwxq/Dfxd4G8CvxkcETYgYUb7'
        b'Sy9dwrHy8Uvd901kjXd8/bvffvO/3nz5rLjrOgH8ZH1WlN9E/WRDUbPrJe96+4lDxS+rNEcKqkw1/6vohvlfTeQ4XcYPBr2XFRltfMh0GZkd0lL1tV5rQyZF+Bjnbh+B'
        b'LM5he9HedFmHwmHIXhUxiflQzVcin4vHpeXQayErk38A2o/wlv1aLDrstiLSX90qUL4sYkUcjnASdiDU4oN1oy1lkmxxdCMUrcHb50ukq0stsDwTKdxwmGz7VTE5ng9M'
        b'U+AqjaRvfgqVVg3PSwP90sAxzsz9RHxel/T3i/jHngjNdjSEzwth/IjOaoz/nGU+H9mfCXD4IgFgOedhel00T342xCQubDl54T+P9Q78nF8S69d3qpHU+V1UkEliau/u'
        b'b3/028ArL333ZUK+2vbcbUUH6qPGWNGQfSCTEV9hIuKUW5iBRy5c3g8XzRkPfbwNfzO2sCbhtzhNVCPOicsAqNi1nAQggiwHHF32J63vAd35wszoroBFOq4HE9KLkQqy'
        b'x0XLguwJ0epZQ18IIlvVvggipbOb8GjwtnxSUKokICjJ8/nWXrYIKTeS45Qcua9g6yWO9LPg9Wy9y9DKjOCh0hLqXwpWHVYM9pLkIBY+FsSH0cTEpRJ7Y0XPl8f9dwE6'
        b'/470oGyZSZgz1ZsxO3BMSlIyswPziJeUHBnLB9UxtXVdQy6vyq4JhWKWehp8PSPyCo6xtSYG3eCPi/b8BajFwPhZm6+SZwrTmyJjoVDKT5/hpQPQ+Sw/hVHI4mu6ZO3G'
        b'e6auUHpRJBC6sEadbdDAFTL5xh+c+QooMgKZhj+8Jky2HeDsqQVyXPUVY4l7oNmg7CmBD6dQc4PZQLuOqRfk4BQNdl5AkuwIdkTa/nlekMRqMH//Z9Ue3zZXO+mgIf6p'
        b'56//KeN4VuPYxZ8aZQqymo1aZX4xFORoqVb29qKJspL393oCjHZ+otig2K5deGTgHesbjffNKn65zSHvwJ8Peb17fmr7H/PNU9/8uUz4++7Dg8esDvRff394tPL7uZZp'
        b'/ipeI3+MaR4Z/Kj0w09Ka62tU/7obRfgHL7h5aWMl373J6H9tV0vZ+0wUeCbgbTbwbSpSzr2PrFH4mPI52yOcViuuJaLi2FAdNt+P8fDfTAT2lZbQkm3LJNycQd53nzX'
        b'QsefaeqKebdXbIOs4w6b2U6IxaZ7l9sgKh7FKV0RtG2w5ZMHGnFQ4Snb4C4olxNwxkFo3MZb4or1jzCDqBPOrbKJbjXj5nZllTGYTZOzZzoKmUXTHArX56Amcl/WuPa2'
        b'vDTjlCOhLl+dhGos13rQEmlw9R4UOI+8jjB94zqkjSZaa1PjGL2D6IuFAlIInjz7RDJwpH/GvRAdrtq4mg4/Z7F0kJwRjyPEiitx1rxzfT9zz8tEB8WG+ziFyK9CbbYV'
        b'rWXUPs9oM0ucZOYnJc6Bypy2ojz1PI08cZ6m1EenFaYlpdny+YpEsxWIZsuv0GwFjmbL31FY5Z+7I7MOzXYIDWVh2bGSG2tDaZhzineE8X67kLjERElSfFxsaGRs+Ofk'
        b'TBIltQ1KTk60DVzRjgI5ash4Q5xRYKBPYookMNBMGhCeKknkYhU4D+0zgwU91yNrFBIUy2h0YhyLb1iORE0OSqR7MAoOir3+fEaxxn33lGC1rvPuuezj81gOOwjmXUyK'
        b'l4RwOzTjT3ldBvIkHSA2JSZYkvilXZErAMYv40lc/42IyJCINZyM21FsUIxk3RXE8UHUy+cQERcdSkC9ii8+FWIdE5R4/Skv+sqlJRnxWQkWRl4sPPZGZBK/AmLuEXGh'
        b'RrZhKbEhBB70zLIsHbjuQMurDwmKjqY7DpaExUnZ7Ep+Mg8EKSzam7nAg9YdZzUMPfckVwLZbI2eTll4Es67PO/zwnqlYwVbBj87yurEhy94n1EIkkm8vYysrWzMD3D/'
        b'TiEqQ0gYKlm+quWxCPR5KFk/yviUJCwoJTo5aRlFVsZa98b3JBlx/2ShCs8sbo3gIoVMtpV40hPoty8hdq2RZ9SlBG+tPLPHkzNmkdyQDSVJMjBvSeRfGCeAWRJwujgh'
        b'YzeOQaPyDWhOTRAKhJgvwOZ910yEfFbyfVzCVlNYhBpSj0l1hlKhI4zjBGd2YPXJsVo5NeEcb2IwtjA3xvx9e894kHQ0cAKmfeJxIvkC71qG6r2KR9xOcu5wmMUsXFjj'
        b'EOcS7rACZjmPOO/pDLmmAO3BWMyJSV7uKrGHBSQanQ10H7xwTJDCEtqSsASGmDxh6oZdMlJ/Nh/DZ2Zi7iorsDOVw0Yo4DtYuEATjppipZxAqJymKYDWjKN8TWUrObMo'
        b'Vi/PKDC6W3iJLwVSdFNG9IFYQyCwD1T5IDSI//CSk9j6rJCr+qgSoO0k4Ltw9AuhBztFrFQe1IYqnzzNFYfiXmjyUtyuJjKi5wPdvTW9BCmMT6pcxEou+dzbhbP7nqGF'
        b'F5sy2XLFKU9fuJi5ulucMd8rJ8Ci4FMmKgnXYIE79rs4q7paOIXBWE4+LTZx9XCHfh+XFc8tZOGcInRawaKTiQKXVK2JBWlSVyPUwr1ld2MPPObjehvxfpwb9mhK07WF'
        b'+7AVOvnqh4XYCQPSbO27OC7gkrWxDeu44LADsLBhOVn7LjRL87U34AQscSPv2iSQZkxvMBRwCdMkGj/igEykpmW6Kt+RJUvLiYKhU48D3U12UG0K7QkrKdMiqA/CVq44'
        b'DeZhvt1TCdPL2dJzZixh+pahiTIH5b6GCXy+f7SqgEv3xxLkO0moYRdmm2JW2uqcf1EG9m3kezeU4PD+JwHSrJ/9GB/baQ3F3NY2hqu5EYbkSnP+BTgL5VDKt6d55IeD'
        b'bjghu2x4OrDdkNuzMjzECT7fH+uhR5rz3+B8kpszAfKwR5rwvyrbPxlmTqomcO8HQbWT25MUV/UdYnioegmalbhvD/pAiRvOpK7O9xdlQP417qpO+mKL26qMTZY1rga5'
        b'VzMgk0tvt8IRB7dgvL+qGoAIspLDeLP4A8VjLMTkvLmcQCwRQj02HjWWgghU2eCoNylJ5b5n8cFm1lnOnPVY71flMvaHT8jIFYp4jEp2MOCL65jEQjcW6cA0VnnJCEQq'
        b'rOZx7l4TJa4QLS5YyCapJabguAqOqxPFmk0mfasD+rSjxGd2CLiceX2cwqK1DyXhVIqsYDNMHcAeMbbAtA0HLQdPYdfqB28kJygmqqrJCYzFMlAPFXjP/SRXGQByojEb'
        b'J1NwKilBJQFK1BNTxAKcjtU2EB+GYZjli048gioYS0pIUeIGU8dpRRynidkL3BKwD1poGSeuyckqwEN+4Ic07v2Vd5ZXui9IWyJ2EOFjru9IDA54849A7t3Vy9wKIzK7'
        b'VWhdbKgdOAmNq0ZKTsQpsSAhXvu02BazIJcbCvKhDrJWnrpB1FhOoAE9e+WYffM+FnEVC3ZDt7UyziTTclQUVRNl8ZGfQPWOCCYP0QYYQGzBwkC61rNnz8ob0qXK4pwQ'
        b'KkKhmY866t4U6e2BFd6EUDXeUMIKZTYKnWECZ4ygmn+kD3qhffUUVjjDTxGH+TxYPSa6V5WEM+qJsqfuCkTYI9wLXXoprK+WH3QTISsiKum2z8Pdy/esghZxlPNSs7YZ'
        b'o5jFZ9yxkGgH3PNVTIJOGb7axtBpXHRjFcmFOO5jK0AWH9XFA9YcVFjhpAuRDjdzwjFPmSRngSY0M6K4hKUc6bbS0j+SJogQCDQCb6Hmdp6ed+4xTQ4W9LEPRRZ6jgK+'
        b'Y4Tg4xPSX4ztTWT4RlrlJ+EhDNJvNwVEDG+Gwjj3eco1nIZB4s/pAqzCe+nwwIarXIE9iRF8owMLaEg7bs+RDyeC9TZkqn6kwBvmI4myTEV6aGjJJEUTt6k23Rhz/mjs'
        b'/7HXaLl6/t2AjruV7y9Ff+Pvh51em3tFU2uPvcFLv3xJaGyvYXzx5YlxjcCrb35PeKXc5lShUfgr5853uTbMutn6Kqn95NsZR48etZpv804YklgELl7Z3NUSXPS15Lxd'
        b'Rw8npt56f+z6u+LGIlPhL169tu2H49e+dVCtMGnLb5ItHh7tedegOXxOrzng0++d/Nuf1f6R9HfJ5cqOAX/vX/7sz9f35qjV/NTI8cPzv9n1wU8yDNSCBu2/ebn+zQKb'
        b'TYk+ykFn/ythg+m5oh96RSV3a3VVDci/M/rNUz953S3dsTfZqVnPPO+df5hZxb8xXpri/I2kA6kbO95rf/fx8MOitBNev55ITq7s/UFlYpTwa8rG57fMbokflPh8eLLp'
        b'3lHf2Ol7bwz9cErj9Rvu871bQv3+Wz5QI8ZMe99b7333ctAH89MN0/o/jL28IPnAet9P/v7e377refqkeXvNWdf3dvpMfO8P37rqk9pYLJm1KfrWnT9GZfv+7aSagnvo'
        b'bd3Fj9KG5/xvHnvllT/ItWgcfG3vLeP4tj999sfHv2yqS4n5bHGzt7Wv2S/+kuL/s3nJp5ffuahm8ettex7d0a0Vpu8u8n/1uzVbfpy5d3pO/ONTsY3em6LkCwu/Mzf6'
        b'yNfJNvMzb/kfxHq8kaVm8Tef6u+96fiXw7+aGM4Os6hyTNrxiUG9yWde3zn6xvDoeIhkKHgy71dtZRZncVigNnh7w58tfp9wfkHSAZ8Kmo7BZ+XOju/ePv5TbFKbsRja'
        b'2ne/89ux+o92bJl9L8iq6IcZXbZyb5WkR1sP/M7v01N/Hbv66u++sefjH3j/vGG4xWAu+e/RBhbN7y4YOXzwzYy/zpp+Yq99M8zyxOG3XvpGnMnHH+sa7/302L0cEwvO'
        b'jowNOLVnjTNVDvqwWKB1RgwPsHwb1+L4Dj7UdrPBuRUZwhrH+b7QE5Cl4Lbs4vZi39+5TSJJnhiKY27xBQMKbkHh2ni4DYzHMCtQrDZnidGFmQA+GO4cTizHwymc5u3c'
        b'LVjgLQ3ikkZwnYOs5SCu+dt8MN4YtuAiF18WEM5bkaIkvAVoSWi9uqYpzMOAFQwFckakABiC7mcCzHTToJ8ZkbBlEzeEVyxkr61xdgEytxvwM1+HSk1TTw8skdsGtQKZ'
        b'g0LoTw7my9Pm6ySsWJegT+QKi2aKSnyEYBc+4lrd8JF67pDJG6awDe5zB3LsFNatLtMKzUY7oEOdG9cRa2LcTIHVzSRufFMUKb8zGYr5BrxNx6HNTRbKuXNaVbsWqrCI'
        b't7dNwbg/75Ezi5ca8x7CPF/JYgzazro5pq7ImlyIIN7DTv4ka3GOFT1vDSUiLU96Q4fQF0eggnf0YbEa53/AksN8uks4VnJrCsduYywyI0GQXsNCDzOhR6pAe58YayAn'
        b'gS9B16WMHcvOOii6biqUeuuGd3LAtwea5N3uKK7IWzgDA7xpckpxv1TyDcQeqeCrCHz/CrgPbduksu0JHV60tcYGbkYfc1a+iJdssZuot1S0tcUu7ohdr7Eau5xoKw9T'
        b'vGyrbc5dnSFWBz8t2kLn9mCshV7+2ptxxNzUKH61cCtziXM7ugSErC/ZBptylYAG+X7V3kzGZ/WEeO8kzYGZYrrB8bizy1VgxjXusoq5+7xYub87okDs2Isj3sksHhgL'
        b'oPbCakknAadVcSwVRoSWcE9ohh2yiiS0DEoL+0Zsd8OFQ8tXQ3JyowgKoQVm+d7DY2mhfPU/NyjYxzd3hyKhvpMMPZJ5lS+vMhx22g2qcYIdyCFCHIE8tosU/M5zlWMw'
        b'34VQTsodi53Sb0ErTxUaIVdWWreEId8ZWTl4LNDeISYBt0TCHReJQ/k4yz9j4YGFJLALGabX6mO9DDRvxg5+pIUwLOSe8jIjxk93IxLoem47JHOCaMIDrrrOWejUkVa8'
        b'XFvuUgGrWcVL7E3i8afmOs5ytRALmQjSEePBih2XiLA9HDO5202DUVfO4F1gRifvKYLZHQZn3fiXu+Ch5pogWhZAe0jhHMly49xpi6DfCCfVUxkV3CumZSpiv4ikz3nk'
        b'Y2F9nUOwSPPwPnMTYwY54SKSuHqg2kT9X080emL0/Q92hF7tDQ8KDV3jDf8TE6W+mh3cWoXryCzH9dhYrqDMh5myOsl6Qi2R2kogqoJIJNzIejdLA1DpN5GccM3PxzLK'
        b'MsI1Px/L/E7OUIEbj+8KwhuwFeh/Fa5cjAzrB/2RnIqckNVk1uDWoiZUE2kJ1TibPN8tZDNX/EWNC4ZVE4q4dapxxWaecUauOhap1V6RN72v2MQTTzFz/Io1PPH0Wkv+'
        b'v1YXW56f58nA3IzcZBYrc3NegDP0W6GyNO3lK3kBMgUfW3yeP3bVEZiI31ZYdoM+SdcLkRE8+U9OsMoGxqKVOeM+b/xXlBr/hZz5nxn/RXmaeVp54jztMG2p6V8mXy5b'
        b'cFs2XYk5aaWmf1nO9C9zR3aVu9ZbtI7p3zdeGna71vLP2cCDpDbcFT/u8+3py0+szdFJlpqjVw1hJrVKhwTFrmuqDGZeByOuyQ4zKz7fx/Ai5nfm0Fh31r3Ly9trxOXh'
        b'cJbS5XXwdm9+ScyJQUuP5W3N65u+jRzjQiVWNkbBQYmcrZbfcKIkPlGSJOHG/mr+ae4ApZ6Kp2v3rOdioOHXrzUhNWAvm++ZxfyLLLxf1Z67ftcbQ88UlsJKHHQM592e'
        b'9Ns+9znxXqXWu00UcdQNqlJYjMah1BNSiylvaWRGRMz38iYhO3uN7TQdexWhxBOHOF30TiBWmGIH9LkuO7bvO3IqcXqa0qVckTFTid3v+Jzie5XE6g56v2O/3K1E8IZ2'
        b'ijNj0gNHQ0yhj4nP+VjmzQyeHu4cg734bLhtCZavVe7FvqrYg/XAt9gmZjdIzJBvzkzMe8HjxiU+1Xxp5ycCDZFAbyy4747ehXdO8ar5mw32Pny3k+jLgncEgv32u7wk'
        b'H6tePsl/7dRhz337qsv1i7PiPlmBUeDR+vNRvIWX9dXx4Vt5R+pYYics8tsZhHouh2bFjI355q4eWMXMtyQvnpHaxbnuP/TghNs5F1czV14WxFksU3XFXpzmjLob92H2'
        b'uhEH0BC5XgAftkOftAY9VMjDwnIRegs9s9VF6MfNOcvcGSFMrappuhVzmYkTlqCUs7BADzYffGZ2Zk/WhjlmUjZeeRey4LHibW9d7rDsdonTvfgmSCr/o6kptYbYR/FH'
        b'GahxUTAlEBjZq85F18fGqCXKM4bBTOMmstwV3ibhccVGMg31N33hAW88mYHpZKkcCM2YlX5Ek8t72xK/i7eR0O5L0qD2MJ8NtyDRkxpJHLUjISeMr3g6QCpSNxZt5URo'
        b'LJITyFgLYZSUkGY+m7nZAXueNoPGnbyKPca8y6Q4lka9BLO82M2XJh1LjTzwnW8JkloJ6n7d+VO7crskbQeV3O4fLZYt/vkNmzoN7aiBqf061T7JO0+fD+07qPORe2GS'
        b'awyee+X0S6eVvrW4BGU/7e0q/Wh/a8xUuuGZ0Z1/3by9UD8+438DXTqt3vvjUdfJ26a73xamfuef510jQ99q+jDbvev9hDeKNw02/M9rp+qM/1n26ddTAqarNi34vOvS'
        b'HxAjyK2veLU9OkT045eOfiy6GK9cnPHOY913jtv9orrMV6/oF8Z61uNd7wZMfXRj95s/7VPZ5P8n21+P6vyuLzhDODx/4TvybtO/Kd09cGIwNvJbHz7wbzSu+kt02dXu'
        b'H707N137o8NVu/MvGtZZSlLuhKce/0WzaUq/j8dkZ9PfK/7Z5W/htHTc8y+ia5Z/tPR3jDu57edX/RZN3zJ5K//EFetf34u6fHzzj3pVWt1s/bI8Pxn2yehqPLLFKNLw'
        b'G8opd0M1w9+d6nQot9G98tHmH32m8942o5Dm1yPTs08/mDyb8LWRnOSms0keo9axcbYP/vyXkMHCa6dNrux7s8v2l9cvf++33zBICY5+U/2Ik9vfDVv62oo2fLdpg4Gl'
        b'eV3eewc/GHj100MfG+7rV6jb8LqWyUZO1Tx4FKtNvYxWpcdBoTyvzdyDR9eeJLkpko5Rwqmw06m8sWIKZ22VodrI7ZkynAGwyMn3d/WxZaU0Q/xeuWjRdqhR5OaNxD7C'
        b'yd0496SkQ9hxXuUrwyyJaXjAqvS2CphK5hsR50PReoH91bJcYH8i5nOqrBD6MYdoyhL28R0XuX6LGvHcvvxgWpdvtRiGeU+6LZIG3ce97AM9G01xDLKftJuBR1gZwGv1'
        b'o1iLI6x5i7QjjAI0sKYw12/wOvTibRg3pUVxu1LcvmeLCMqxcCtfFLUAs3BQWlY+Sp0rLI9TFznVMA1a4lf0esiDLl6B5DT7w9DFKcua56CZ6dnQ5y6NEFK3FsP9a1cg'
        b'X4M7HlViCW2cZoZlHkRGiW+Yygn0YeIuNMlwbYtH+B6N3ZvC2QhcyzoisG1yBiIZ2lc+p3n5Qp7qsiqJ0wE8teRUya04zRmR9mIeLD6lSep70oExRdIQ7vGKZDaRH9MT'
        b'm59SJZkiOQr3uTwNGLp0a11FEgewk9Mkq/dzCw7GBRq9aFmVk4Vaps1Ba9K/KMBr/we1t6dUOJXV8QecDjfAWMFX0+HuCixUOF1KSdpHUUGqNelxPW7oEzF9I2K/aUi7'
        b'KvJ/s844rCsOK7OpxOldy5qeBqdnqXA9c1gGE6+JKXF/buTm0eL+TNd/Ohlh1X6kypccr/a4rqhCTP9YpW1p/LvP10Rm1WQWKzNyKpcXU0FUlhsUfDWVi5Su/auVrs/b'
        b'+3LclyVbiJVoHYWLCaqckMryCvmMDGmpehGndImZ2hWmsqJiyXwpFcthvYjYZRXrSb36lQBXLi723xy+zb+zXPWFf2+d2owWRo584Ay3lOcEBHHR3kwPo0fPeHsdsd5/'
        b'gOk9MUHJLOwjKTkxMjb8uUvgy808CYJ5ukIe//0LZZAoeHISoBIusv7b60e8MuFTFUbXyJ9KQU58hEjTZcha44nWhYfiS/GH+crw40Jkvbw0vNc4okdCOcfjQSyTe8bL'
        b'jQUh4pO3fSO/NREnTsqkp7xqXzYvHFeF/Tqnfh/QrFE77vg/gvwDGm4vCXRGtBS3Ob5/sP7dN+HHOju65zPSvVrk/q7YoDzVcNas/e0/fxy8XzUjNKPpStRCvd6Rsj8a'
        b'lJsl73lHPfhRv+70fxdfLAme2fe1134wrSkKMzT8ZPJ69Nd8hx7HPfL4QHL5txZ/aDOMddjx938EmMjyCSTTNlGcLfwuzC9Htk5H8VWnJ8OhiLG3KRhanaNyG7t28rJE'
        b'VShMrfZq2IUu56f0wALHdCSkWtWtNX1z7LEWqoh1F2jynos81TTWW1QPhpaN6lsOr8k++ZcYxip6rpbCodoaiu75IhT9rmDzcqYK3xl3maoz2p2+5SnKs3bWtXR3LRla'
        b'RXe/WqloIqrc+5ZrKStHVM/RZzdfmKgWbF9NVD9/a6wuanpkPDPI/FtLJy7nvvQ/G5maGBIRmSqtsSMt6bqmqs86VNORt3NE3+QMI5Ex8dESZtqRhG57LoWVburpCjP0'
        b'8ZfpCiJYl0bJeHIRFyexnDUfYvi1WkVdG/KE90yCdRUiE7E6UiYaZLn874krh1he9qWX3nx5qnzcpeO+iewrWiERYdHBfz1vFhQbFhHszlJzvy0Q9LYoJHw/0USGE2jP'
        b'RJKwKy3y/wjqOJSPg35OZNODgStPlIcrOMe5v/ZiI4fvO7APJzh8t4PFtbqDPlQms8w7zITp0zjJcH0ci1mzRN6Qc8YjwTwmhX/BDQblYWwbjH5hszGNIP52l8EriUPY'
        b'Iy+GsDYMXVcKVq5YYp+aYW1B8vNrUXJtrcYnT3BY5kO/NahIe9t8ZSzLFLy/Jov0i9bJSi3Ienr6OHmaiDz5/zW+oBbck0ITLNWVy37jEo64aHfO2M2JXxy54HbDH8Wm'
        b'/7S4/SWJd+Jh+lVNWSqRKYhklJWEGw2fLuumoaEiUhDqqCsI1ZTo+80KfCf0z2REAr6Ywme772gJLWK1hEaGCkIu1ArmYJA0y5UKsXMwsZJmLRIY75FNxQnFlD+JOE//'
        b'kgW0QKVdHDbt14BcnMWFDYetITMER+VsMR8qoFKBFLkWvGeoSjpkDjyAIag6dQo6lKESCoX6+Bhm8bEqNNgSWy2FiSCYxn4fVRGOkK40ancMHsOYCzx2pqfKsPAmzEI/'
        b'DFncgk53GDl2CxexV5603AH6mT+01RO6oRN7whMsd2HDAczE9lhoxfvYjxPYdMsOiqAHC2Bc1znhmNdGKNqBmY63o6xI31yE2chjmHvdebNh0GYnWzdZP8sMCy/o9DMw'
        b'J8Y8fQzmsBcmoTwWBljjCZhxgRmbmL1YZhmAxarYE4pj2nRkD6ASO+hnAWsDHbHxrFUUlITgsBy0wgzmxsE4VmCrNw7D2I0Y7ILHt2EB63ygYhN2XPcnGaDr8AYccYGF'
        b'/VBMu6+AUs1TMOoN2XvcaAEz2HgERm/j4DloEJJA0Yj3sBqa6e+yCOjDRui4sVWsDNUwhW2WZqR6zkQcUTqG05AXYgCZzjFwP5SGrfOARyYhTnGGTlgaiY+xyRVr/PRg'
        b'OM0BH9I9t+CYnRzUnzPxZeEBUAM5Srt9cFIP20lwqYFZD9Lqmy/RYdRAnRnOHjm+y26njjZOXKAPmjP2+JuSej6goY15RMSnfZLo0wo1pe24RG8M4DiM0nLGBFhnJTmK'
        b'DVegyRIeaWGbWrAHlIYnH8fM81i3FYoCrBVwCR4aaMPDaFjSh9xwen0onpTv+gMG2BG6/cJlu31YRZDwEHqSggjoarHRR2XTlfTYoxk4ZXB1CzR6Qscmf9LRm0nc6lOg'
        b'zUwRRDVihz0WK0DeaZzfT9dYC4M2tMshWt8sZF+iGygzP0HgUJgGE7r6WEjns4AP1O6I8REWOO88DKUppQT2RzFHB1rOO0ApQb0KPMLJDbfs6XJ7T0PmVpKv681VDuII'
        b'Xc84tIpPQ09I0A4TKI+QgSKju/ug+0hKeoQ61hAkdhADacfi+MCLsLjhEjTaQyOMQxdkB2HzXqwz3Y0PcR5mxTCmiNX6OBMkG48tMOXrd+MENt32jiY8baJzWDSmTRB4'
        b'4HCs21EaotUAmjDr7CUau/IS1B2GesgLJszLEtl4YCWMmdMzE9gHA7f9b2trXLobfNA5HJs1bx7UxEEow2HabRHBcjahxb1DhFkFzobuO2/uJmgrgwYcOkBQPkjQ+RDz'
        b'g7AymlU8MTqNC1Agj93HsTID2lLcHCJxeA/mGZNasXTrsMVdyL2m6A0P9bYSLyzGXs0jMnG4FIgTIixP2xh0Gu/DpBIU33GBeswycIZSP8jEnFB1aIM+L29fyxCt3Zuw'
        b'38FZSUfLYr+svpUv4VCLO+Z70w3X44Ae5BNZyQzCHmu6ygW4hzlirPSEChw3wmZPLLyEAzApo0nQV6gLHbQNRplyAizZ6UI+DsHUjbRNULKV5hsmoOpLI3jIS9dUIHyY'
        b'DMNqnLtlqQNVdI736X7GiHJNK4SruWLbJtIOHly+QMdWDTk4a3iV5AA3WIJexZ1QmUQUoQdybSQ4GYMFl2DRYjMz+F3xgll9grlBLDkPlW6umldu4DTN10PA0OoPWYRB'
        b'S7StLEsc1N7jvXODF2TRgU/7YXc0HV2fF0yY4ENZqA/eySpXQGvK6yJObQkmkLSj6yOQpGXPmcJUig02X5GhYR/g/dggeIBZ0JugTLhZd+isGfRoBLpB/3Eoxhk6sEdY'
        b'p0/g9BgKaXcTMHoGcv0JZXO246LL8eN2WO8KnaEaSphDYNtNgDUL93dAo1EqwXGd6Dg8uimwtjiDVdeTTenmJqGHhKZCmCf0qSS8awr2vxpLBKTDDJui6MQXWJBmIQHs'
        b'AHRCLVZfOU2EcclU92Ly1WvwwINW2IXlOGVMCFJxYrtlGhbrKMLcarAlJKk9u4nWMX0Ds80V78JULEczq9VuQgMRyx4Hd+v0bSEw5plxa6P4mjMU6UJWGG1siQboIeKU'
        b'bX2cALhePgZKoDcAqlTplvuNVKHqCDa4wINkeiQL2U7asJX4Ui9kqosw247ISPcGeZg9gvN6uwkeJmDeEh/r3MDO2A03ZSKiSd6rIaTNxWp1Oqgu2l4PPoLJs3ShHZpY'
        b'6LclgsAtG8ftgYV7Pbqyh3jTiF+aAYFve4wdlgcSB6szgf4bhBHFFnQVHQ6WROcKCDCJd145eP0QVhhHYd/tk2rptMBsyCRg7oDJA0bGoUEwSTRnVkUHq3Aes1Uw3wla'
        b'LX0IJqD9Ji2gAMuMYZqAhpA8HTvk9XfSIS9gl5PfPniMzUpOe2nDuUQkHxDjbjoFk87h5+kiJ+Fekh9dZwMxxDZYSMeiVKi/Ki/BWrswZwuOqZe5JRO/yU0holBOz9Qe'
        b'c9a9hHXQdB0KRal60EwATidIAA6tl6NolUvYJt4V5+qEBbGqWCG5KL/lGg5vhjoGWfsIoTucNEWxHFwTRXFkpDaWky8esbyOGeHprYHwQB4bzisJYZwFCJcSztRDeTJM'
        b'CIjc7tyAmQfodOsNMnBEHuahS+JsDI2OMKhNzKBxEz1eqobN8jEGUQQxjeqEi/WWJnSLkb4WLtB0LgOrDaDYdeth4gSzSnQ0j7FI/iz0BzJUCRLGX2HSUEssjuLC1YtE'
        b'LxgJHiJCQCJInDU0adubntfCUT+oCDwF907DvAY+cL7rT+fy4HCGNhR7u/tB/y6curvFMZAIxwBdx2AMHcogNPnfFGKtkxXM+ezPUHMkdG2C+uMhxJjv0R136GnSYedi'
        b'lxiWNLHSV1djM3G+Qh0ov+oe5EN4u2h1zjaaMLjqElRZQLa7zj4d7IuGIXvCvPwoqN6N9xyFmCl7FuZDT0KNUyRMHvdkfe9P2jievrMZGwj0iSx203x5ghhiAB04LkdU'
        b'YxIKNrI8BjqsMmy2hEUo3kQo2rwLFm7jTMJxAtl6YnWlWHssATsciJxkhp5Lg1znOAL/B7eh9vYGAqrp0JvYH66H9UQD24lGFB7Fkoua1kjQXo5dziQXETx3Gx2mNbTQ'
        b'b532h9OcNYgtntoMk94EhLMwdfMgIfwiDjhiMR1bDjG9tsNbmTyWCMVhRnsYIGKFzgmOEHSwgkvQGgm1wZrpqR7YTLNMEVLVQWUkraafJIJsEfFzOvjiTRm0vSbioIPE'
        b'OJMuQbsFtmKXnpeqN/GJ3qiN2C7BmjN0vz24cAVaAmmJI8dhhFA43wbuI8PxRaz1pSHyrkWkMg6EWTGbcDKeFSPHnJ1Ol5VwTP+A07ktxCYaOBHi0MVIAmvawYoIYYoP'
        b'hTFYSiKE3RFTmN0PY6nKe2zkE0l8rXe6gJUnaSfwwIHud5EmnkykM5ph5OfSdsi1wuwDQdBCMxfCWHyGncpWN1jE0WBso2dGiHLU3TWETNMLdNkPZY4QDayFub3WJ3Dw'
        b'KgloNTgnIeGylNY2QNx5GomiZd81x2otAtn8k1fhgSvWnrdn1Rkl9tDgu5dkji5YsKXZSkkaeQCP1FkOBOvO1u8CpQfSsFLNwzA8hshcljwhR2uGUgCM7bI95a5np0rw'
        b'NQQ1auZbZOjIWpS0bHDKcLeC2AnvbaNTzNxFMN+tqU/cvZTGHL6C2Veh2gGIKB0nHkh0iaQDnA/AZmw9mkC0qgZ6iYt0kZA/RpckPGt+AYp2xRKPboIhL8y+jB1XbKHQ'
        b'3cyDji0bChyj9L2czzH5pfDqHegJNsF7IZCpnWGEdcSnKvxxJpEAp/YcDgZivvl+qBMRlLW5Y54DwdYSEfTh8KukkJQT0S7YpEdHPBWIVUcxD9rijtDR91lC7nECmS6s'
        b'OOCnE2Zt4xUMXYH4MO4KUeQHR9WVdlkd1tlkZULkfEoFC7RPee4hLri0C5p9adRKVYKrxzFQeP4CIcj8FXiwG3p0QnE8liZsom22XCM06PaXbMD2VCI+lTBsAaPKdJ6F'
        b'WBcOBYYwcTX+mu4JGIim54ahIYzIQ4M4ihaW6U0AP2UFZXawuIdY7Rzev6uDjwXR2GSKtZucUt4gkExN28lAMiuWg8hFgsg0HJRg300FkniytTPoALN2byHxdspgvxZW'
        b'aZAcefF8uguU3zXclZECuUF6ZwNUzhPn7mQ/kH2IiH4t0RB6zY5JTLc0VGEojS52HtsunFAmLjnDkjCgXD0Qu7EhijhtryxmpmCNjwQWM2Lp66bgqyTKjHCSA5DksACL'
        b'kQT+k8F6mJNoiN3GBBkdhDyDPrFYccuIqEMzk3cjaBH512xj9JTpjQqiHLV0HEUefiTnDdz2vn0xIm27iieSuNqJ3duJcPdeOZ6mRgdcBAx1y+FhbPxxLZhRTyY8yUok'
        b'aaL8kqeV4k4cC/bEe1DrTY/MwH15HFCVYP451lqUPs6Lh0Z10lPuQ2saTgQQsI7tUzF1JfLUEKnhFHXzOGlOHVsISUeJ2BTpG8vQedbsJ2GzXFcHqmONDE8Ttg5twTln'
        b'olslpJxMETeej2Ux+FiZsAt7dpBqO4D3b0OjsTmRv4fyNFk29lg5S6zStl0JIzzPInzITiFUaFSCygNYet0Km9x3ETZMamsmBbMG2jhwGQeuEuJ0bSMgbD5M4sqsFeTh'
        b'w/hY6EwmDTyf9GTd/TpELutOEI2fPLqDll0eASUkL8hiny+r5kuwWnX8Ok77bsIcGajGUQnN20LA1ijYccMu/nLSxrN0x+Pb9xLCtEBFaDI0H0+Dwh1YIHsFi6Kg4Rg9'
        b'O0Gi6yChXcEFYhJFJJQ067irQZvr7rteBKBDOJLuF01CYp338dOHmWI2aAPdDol7r8AsgVWZB4xnROqEEQlqUCf4njLHznO3nLHKaS9BxIjudsza5x7lS/Sp+oyJHBdr'
        b'YoKVJm5nZAXCfYIEYumFpsC3aaVDXYQqPn3IVuB+hObshEnuFXm4r+BmKhII7QUH/EnCGIVyPmylHrt8WVKA8IQAeh2wIewEl3uYxvIqi7BIKBC6Chw3EzvoJOmcC2Ka'
        b'gsyzWGQmZCFVp3eTRFlllnJGTLOXsgAfOqUqLKHfG+1V6NBH7ygZ+itC7dHz6kHaxJUqLAgWOmiwGiap78b7Z5w8IDfq+EYTojWz2L0pnVhTO7Se0XDwJ/JdDs3BWEay'
        b'CqEwtlkzewvp3RVpFimOMLCRCXi3oVsShHnK0J4YRDhTBUvHIfPiOazxpIuk7wkTc07Tr13QSxvEPF8tkt6a9tF9tVhe3klgl7WF9IDxvX40bpnAi+bMkRBNHSX2W0UX'
        b'TepN5C3ItSDWWuED5azr+ASBw2WSXSp2E40bhkob0pFykgM84LEbwXoXcYkigqoJA9KXskkny7cxuQV5ViS6zROZGCN28IAZSPvpqBqOSI6kirFMXqKO9S7Xod8aHyaa'
        b'GuLcNRy8fGYD9MvfSpF4JAbQuVZAlyKzGUC9wSbW9YMkrA7iL6ScXLlMYxXTedb66UQRxs7REsoP0VZ77DYrXVTB1pBATulqFGO2JekvmXQqw0hUdMkSisU45rfXyxJz'
        b'LhFVaz+KY7sJa3qtTIGlbvRD+VGShcpoP5mJuikyxJnKk2gPXbB4yp8EySoo3Aut8jgUieUuUHMCH/iSKlVMOsui/AYsCtwWYuKoj0MKUBMINYmEJYsmainYH5KYiD30'
        b'U3lblZZbYH3hEqmPw0SLK6xwwtH5lmZYKEwbq8KMGra5EFbdO4zD+84QYvdDLjKrToE6ae5TkLUZmgOICEDtCZfLnv6JFy/rkjCUT2x8TpdAP3GfFVGJiVQxEYduGDLf'
        b'CEspETh4mLSA8r3a2KjL6Dixu7z9dwlFpw+RpFjA7FAmnmHETmF2HzQlE0Dlwaz/TRJr82KJiXfBwCnC32G3uzAcQMpeK93qsKstZ315JCY+0+YfTopUN5Qd1tW/Y0pi'
        b'55Qn0yGwIgwWsGM//bGEi0YboVaSZJasR/LW4HF8eE0Vs1TxkRBar931j4bHKb1MWei5Sif2lGGGqOjIcSN79VQc2ii3+Qa2hxJyZAUTXR4/64+FrjobHUhpWYK6RDrO'
        b'XGUd2csB7ueJCpRbbSbQqYXRTdhzQM9t2zGYzCDCkXdJz8s8xEGe2NrDcxc4C82ElyFN0ghV1nQoj5RoBxOxRJQ6iBosRuBMCsyYwCgUHTNlrXaxOZb+UZZ6EBqJpTH2'
        b'x0C1E8b3wsj+OBL0W21xItSfDjrX44IukzSRyHT3RSHJe48IqbMMCH/GnYnDtcoYYK8pEd5J7NS+AH3bWbtgaLJPdCcC1RpOkme2PSOu45B1O5qEe317EhQ6N6kzs5Y7'
        b'9qZrOSrBQMxVosPFvP6fFEIYUH59Fy2L2Bm23yFKMGdAiNBC6i30elwTRGHeyWjWU/zayXDiC5PYLKEVViYTE86mN1iwUktIKIxGnz2MU7oa8HjHZQKGeh3sdrBgJ7IX'
        b'+3UlOBdJcMNk/AHSGx4l4uI12WMa2KB/IIOOp9IrnqhasTZ2aJH6VZVBwlQmLCWQtDN1Avo1vYxPWO0k7vsAa/wUsN05js69yXhPylaTyI1nnbU08YH23RRbVcg9KfIk'
        b'sB8gACyAnjtEC9pTLrhAkT9R2num8FBHQpj5iFBj5vbFGGKWsVAqxnH69xBJenNBqURvm+1uXcJuP3MiTI04aAILJ6/BsOGuM0QXqtgd0z08JtLWQPRhWJN2sohLd866'
        b'06Bdh6AyZoOzF809r09HsuAIDx2ICOcFyG4/kaxkmvJDglU3mL8LLd5YtKLZXqS5S6DuoCFTbv3OKwthWgvzPWFUzhyG/eU2Qj8SDZw6RGAwanOBuFahRaQNAWgFZywZ'
        b'2G5OZIzZ5xo0zSCHqBpBaC6MkWqAj294mZvQfQ3io+MO0G8ADeoGm+n0i2EqlNC188QxAfRvIsIysAsabDBzGxG7CRi6hG2+0GTpR3Qn7ww0h/oRSxi9wMSTDmz3S9wj'
        b'K444hrX7sDsNCyxgYocPZsfuh66ok8QWumi/vSS3NjsRxYE5dyw08yPG0bSXkPm++baLEdh9+CLMbLiciI89CeBqiXvkHNRRgLaoWBgjCtZKk4x5yhMeLMV7kdpeQTBT'
        b'DF3pjFvD0mbs2Qc1KcRR6jyjCKJIc6kzU42FHCUjWxy2icR6140x8Aj6U7DJBuYdErGOjq8Mxy5shSUfwRG8r6qAS2JaaK7HBpiTZXaRThvoCd/oArWn9TfbkNZVSLvC'
        b'4aNEyR8RTIwSHswSICwmkPI5pE3n3hAcwnAnLMKYCGuJ6IpDeIIKTPtjT5SXZ2TYNZJTJ9RoCY3EcQeVcMINikKg7gIrVJ+I97AkSiUIh3ygTNs+8GoGtrp6bDmAFftx'
        b'fEvEFSy1EjG5lahQDinRbfjIPe0W7b4oWIO4Vzs+3iqzC2q1z2NuyCXnayc9nAjHi+2wJulIKM5tJ4o0QrdaRKqhXACRhyFlPwOOxDDKXU0HWR9yEMZxersJ4W49dt4k'
        b'fCuFMWNWrEJTnhjkQPylDSwfORQXzybQ3ZQgyQflijCjddSCaFrrTe276nuQBeLN4mMzzA+A1sMxJKfMYFuKIxNqcvbfWAPapNvOiEW62IcV9uqJ0KUjF7WHaG4LbWac'
        b'UL72gNDV5wzTn0LwYQhOqhJeTdPe282OqmG5weUtMgTjjcS/i0mAH0qn06456KPoCyPW2HiJwLuRCPe8MtPHYdDAl46btGoo3Yg53k5M9NGmwYYDDKHbEodP70WSZ1y3'
        b'sLKf26HNwpDQs+YYNG2go2lKIqbTK4HxSwYE6I2i8wf1oXOTDWQGQ8E+kn3tiB4a+proE5mojMBsRRiXJN4lvpUNU37WxFMmJYyIF8knn7WCfpXDdMRl2KAXQIc0p4Ud'
        b'4RtwRME43eFYgi60HIZR91sEVN3E+LqwYRPOJLtivxZJOmXERhciiBekKzkm0h220iCV248kQ9dRmQPE8cejTuyEvuNK2JyMQxphV/WgR1MjAao2YLFbOI2VBdVm8pYe'
        b'dKUka9DJPJQx8oi3P3w+Cke2E3XoJyxqDtyOS05Eveqg5YyDnYBQo5BQkyRwol2VMKMchnmHbFnDbyxyhLHNikIiB7MBV4juddOtPKRRczQ3XCQ2XgKdCnA/AnJtsN+c'
        b'eED+nVSoPHIFmZG8QwCT147qE1GZh9zIPYRpvXrQbk5o3kBIMUZ6dXOg4qZDuKALdT5H3OKdiYX2QR8Oy9Ar92DSSMeGlI5O6HGAAVkDQqZmWNq1YRPrQbEXy29hOTud'
        b'ghswIY7ffZQ+rTgGHXsu4hzxSqzV3HlsJ7YegXrJJQKdfKxNJN60mOaPoweP+UJ2dDLRxmoLgTX0BKXpBAfTwUdH4AKUBMNYAsnPFSTBldBpjdsSac3ZaUNK4RzmJdq6'
        b'hdkRHcjHwgxzOtwJFSEB34AKk43pLhtCk9Juw0Mv+mcnNLqTgt4Go/EuOHKR44xTuHDM/zjUGRPXJAXY2Q6nXOk+R5VDD5AoV+9HyLEkH0zyWuZ2FRhOETE8GjGjgyRE'
        b'yiJ4Zpi0iAumXGpEDczY4JQeCbuXsEop0hEGd2KT4z6oYCmhD1TZE3YakaTaPMoId3EhcSDb1dfGCHPT40jAXsReB7r9CWhTxEfW8tHEdgaF2O6N87tuQyZpfjW7ndSV'
        b'vbE2lHOsDTML/90MqIZ5Zs/qhLnztEXCkx5mLCJJtxt6XDZiw83zey7vo83V4MAxzLpLute0AbHG/Cspx6DNl8StaXO5iDhLPRhzUSLUH6JHSyzpZHOjCQ0W1fHBVcgh'
        b'mWCM2EvpASzXl6dddiua48itCBIBc4PT4L4dceVSeCDGCT1FbLqg56RHADNkLKuxBR+e8IVyNXsFIpvzmOlMAs0gI2qHcERA/LsGy/arSc5Cjr+b8ZHkKCVc1LiYvoco'
        b'PAnmx2POQlk8Vll6k1LN5NBJm4hbBB8Fe2BM09aN0LhdF+aVYObSzei92LeLCNcsqXY513A+TQlzT3sTXuSQYtJHZKeClJZtdNx1W7FFRUkcpotFl6MirwZYYaObmvD0'
        b'RnpvGCrkoFJTl/CtCmajVM6Y7sOZrcz0Saw7Ex5thlnmves12EJKX3HwCTsS4FsP0lm0w8gW81iocN9BWFFKuk9SCjQcpFvIPYPTx5RJhF8gyaD5dLoudqjckaUdVDpB'
        b'o7biLUK4SvpXBSyZxgbehNZtRKqztY54wbQeNGsctlO5gfdcMccgQB57faAyAlpJdK/C0vN+zFyKvSnM4kU3v0DUd4yYRDZ2WWD+nYBtxKVJBLpAz7Z40mbuXcSZdAuS'
        b'y6Cb0KWKGHW+sl9wymVCyDZgzIQk0i5r2tvSbajeipUSErqnEwhehm/oEVgN3sa8u1BAlJxkj3uXGKY0pPyYJCU7Ik9jK2hgz0xTZReJCRMBizphdF59J5YTClzcmUFf'
        b'N28KD1HUw65NR3bS7S7hSDgMybsE0iQzJCN1i6xxRh+WsPdwlDLtKAcfJANz/2ZdPgaVMlCrR8T80Q1scGP9Y7KJFM9LiNv03WGZ+YRN1XQXFUpbsdOVCOkgHX0xVt7C'
        b'JVg4poMF1rBgjh07PbAomnm4zjA7VehZOpyc3URSClRkcECymcB+6qYRYfncAa84grcubUtaW+X+jVi7w9AEm3afJnmBUMORgGFRJwKnVbDx6DbsVqXzJJTLuQLZjjhn'
        b'D4OKaURgqkj+qSHi3CkgoJ+XgxYDF6hTJiWhe786tDscgAYrkhZy9Hw2YN+Og3JymH/OEQuU8Z7jWdKLFyxIxMqzwXH1eJzep+JmCR1WWOVga0/nMgmNMoT5XUTtc9MD'
        b'jTRYMtccEYM5yDIiaB8WkmB2N/UAK45zHnKUObiYCyACvnR9N5GEZsyLo4PrYaRgej8JH1VhEdB5hCCameCrsFAXJ61Js6kIh3w56Igwgj4ZGD1ui6wDVxZmnmPpX+43'
        b'iKU/tpIjwboTio0x24zOZnQjdNyGOk0CzPztzJMse0vOOtyHRq4+poa1JD3I3WAyULb2oVhS+Eigv0c0ogJ6tLHhlG4ai6rwppNrhPlrqbtgwBweOUGniSw0bCP5qukS'
        b'9F8npWcYOs0DSAIizm1tG3cQ5l33JGDHLqh3hR7T/adxUpZ4St2ZbaTWtuDEAeJw/QxJGry1TlmRkD1ogUu+O4m01Z0PVAu47bPZj2AnHzMPudMc9TvsDO1vC0i+zL+O'
        b'/VcFJiKu9g7M3MFGvi6OQHSdjqlHyESVWb7YbCuJ9gtJXE23KBtW1Q3rY03EnDHKiHiNGzMsHRFAbwqtaPQmZ3JKIGHgoRsrFSHcLzjF6u5E6HGDkajcc4AVCpARCB2J'
        b'+ati7UYt7pWdMGElNZEdJNgqJCGpgpbHvgpVxA43L5reUgBVxvTVJAym8DUeOvyxyJ1esmGpNERod9A3nGGtCx5HLdvVcFyXsKcam6XjkbzRpoVFJvSel+DKbaLr3Qbc'
        b'F3uhJwyLPHjb2rSYbq4kkdvnjs0yUlscSQIkWB2HUhMh9405FEW5udJIpoJUL8wn1bCQW8AxGNy/Yo5jugdR38xUE6ET15WHS12T2SLiQjE17oZGT566JTARcx+ftOY/'
        b'fsnopplZhIQvCfRWsJj70GhPRvQ2vVgBizFz4kbjct0iew2UhUljRK8m9INvV1300nfQyQm/8aMDXwuMF578ff2PM36voVUpMNFycS7V2ln9bq/CtYkLH8a2/kn88bjN'
        b'0WsN9Xmv/Cn99zZ/a7Lx/nThH9+osfp58ltyxfq//UfO39SsOi/5zx83+4FCWmNS/oPhfygNvKPruve+t1LFIa+Qn5T89YOBQKMo/RMlSSlN1tV/SyhV2h0887P+ut9Y'
        b'p/6s7Kep7d/yLT15rPudveF/mUzZ8lOrtC3vWt3aUrHV5ptNfU4eB961/nmJzzmbV/37HDv0Un6b8Gq608a+73dmuZYYewW1nNrRMD/xk/s6v5X57f2PXn9lbORrsjVy'
        b'b/VWnrZydvl5pavna98XRTiYTv9izy97+tTcXHf3yf9RJaZLP7Wm/vvyLrOdnXoOeUmB/iPvR0fscRm9KNfl9JtXftV17euSypthEt/UXxq12e+Zd0l5qyfmYe7kz8wq'
        b'J7tO23a9Hp5k+XUbt+83m33T+puLt+zmv+c48Y0d37z8488Ma/T/djPbyl+r7syvfnfacOGTT0f6Pur8cYT7O2XCdHH6h/W/urzz5OGvN/w8/cPLH/qa3Kj8pqH3e395'
        b'7duT3wzWcDSQvGL9o/xr0+1/nnV95X9OXLn2cnXPG4cyKr2C9WwqbfYE+7trDDzAzzr/rKr3svFb59pU//GPmDOZfz/633+Xl3Rt/2tjdORjzRC9PSdG3thabv17lX++'
        b'+p1betr1v3g/7A8X3n7/L2eW3F9v6LXKifxxXtSjzmvfabLJ9vuhx51DeTcT/R6F2+00fefnsmavxf3ljbD/nRzQjHz3lumPr/1qcPy+5Fd+P7x5787frH4Vte8n7a/Z'
        b'HKxMP1Yg+U74TtOjBruyNwwlVvvGVWfkHBoKETe9CdapW0+++bWtHyVkOhq8/8nHLz8qfTfN7fbHKXE/vb/0VsakxqLVx2V3W891zx5NOvNPxVvDGJnz2bsFJ3LrNvzv'
        b'W9qf6Yzu/fQNr0/3fer04FWfqY91H7917k3L0yZKXND5njTC3iJ3npKMktJX6oztfFh7p5/7St+Fe/B4dd+Fgqtc0ZyUK1fXS2hrjJd2qrHmMrugPRGylRNVFVVZYRDi'
        b'hUXqiSkqxJpnxQKDdBptPogLkg8heaNb+hwU3cCZGwmqcgI9BW97MbGE3qvJXJRi2QboS0pVsQtKSMFZdSiEYnUFVSUcU0+VFZioyRAb7T2evI+3vo+epieffo5E3cep'
        b'ULI8voeMHMzZYSlff6YSu2KUV8ZTIPpRsVO0j/hMUTKLNd5EQnx/EpQoJNAak2iGAumgF7Fv9Zg4LQeP/bGGW/LNkORni7AILXEgaqUIS+bFZ/u4Wf2/DTj9f/6HiQFH'
        b'Yf9/+YNvqh0QEB0XFBoQwEVgf5cF0pqKRCLhQeHWz0QiloimJVIQywgVxHIi+hGryWppaf3f4q42uInjDJ/u9GFJWFUMbg2xHbDjxrYk28EFN8HtJAWDFVm2KQUSg3vI'
        b'p5N9IJ3OdydiY1OoMf4oGLtJmPBRPA7TEIdPYyBOMGTS3TINaaffnbb7I2nD9EemZDqd6Uxb2h/dd8/YtP/a6Qxzo0en29Xd7e4r7ftK+zyv21/od/mdOZ4li+38knBe'
        b'Ea2/j6sGgZIvwopswc7DfuE+ei5bXsk6OCbytlprvbbE256G563zR5x5Lyx71i/4hBw/bwvu44p52zqrpJgv58voI0BxP3fezmrzQXYEtv3cGTussf6Hc15gPIvJpyw8'
        b'9M3zK54F/XfQ8IV13ysfvlE8NGO0WZ3BVmBDFwXAACBtBfdr7cFcVUBCXRVAEzTAGMWjJfgapBVDw2jUxfmWCgVbwkpBl8ob+TaOa95/ftXIhkbhWX/duSc29NTeqfLl'
        b'9Y/V8/3uovwDjqnHVjx+/ebUjekdg39pnamq+Xh5ft94ojn0YeVNz9HJ+p+7bv5iffBC5ff+/PSHvzn6+pWfVJZMnr2A33zthwVrR43otnsftIuOu2+Oeav/+H79rbtn'
        b'+08lav7w/tSt4djJnoGlL65q/e3Gp14u/9ufXn1i9uwPXrv97o/3+uwXEuca/vrN/MmXDk5sONGU3+L76PStmYnrP6r7dFxRv/Srd5P/bLrzyUef3G4+8stj1Vdybw+T'
        b'j7cYsQ9S/nt5z0z0H1yRPFw1IHxuU1JyFfbeLXqv8Ct373CDQ1q/9P16rW/Td36fX1bxU1RyURtZvdLUDuQ71M7BHvNnPcc3dx7tdSYvferyiPtsgXOte5bnlj3GuFdb'
        b'H+fAZ21qYvRaF+dF02gWzfJ4cm0O4/u2cA2RphC+zHjarzTBSvVH8A2Bxj/Uk7VE4/qKu6zBQK+AburhKPzIQ0cjRyhEb6Fpi7Y9Jnoi4SiNfV4vj7o4p52nX/25lmrV'
        b'1HYQIa6kvum2ok10VtRWWLSwV+kMNhDAR0qBHnzYxrm3eyt4Gqu8gd6wGNOHW6sCG4054S57ow1N0XD5BmNiR9FJbyQcrEyFQ3PlPvwtoRENWfzyFhphXY2godIFfnnP'
        b'o+yq9Z6l1mwbDVfW4JGysJ3LwS8LNBC81Myu+tUvoMHIc8HGVdU2+Ce7Fb/EO/G1xdYtn+hFlyMrq8N4JOKglmmplq0Q1kTRpCVGd5nGacegBu2L6yVWBR++KDypuizh'
        b't9N6Ez5UuxfynY5Sx3ijDc1S3/uMRVynk/sIHa4pDx6JBqmb/aQNnZfRIGvS6p3tAXTKHcIjQIxP2dDbRXjMEhY7o6P+ACjUNdAL7jbCUdpqO/foXjvq243HrXn5nWI0'
        b'DQN0hDYdOttbRvuXx2Nrall/xtCNZuOBYk+4Gw/waEp/hsmHfa0g6BXQMTz9GXzNQMN4RsNXO6kbks1x+cV2Vx46buVjvbQODzEKUgDOBTq+J3LxTR6fNvAou04ITdPw'
        b'7BCaaP63fK7nqa2BYHUBGsSXI+hCKR1WkA1jOorUMEcqG0NlTm7DWnSyztXrRacs6bYZfByPefEUvrqIB3Hub3P4jL/b4uIfxEMJWDQdlRqB6O7oteHv7sBXmEmv2QM8'
        b'DcYrqixX451zjteyjB0NoHF8wBrsQXwRHQ+E4A8NPNzAc+5mPP15Hh3ScZ9FpJ9V4oHnQsFoqMLGLcqlkewxwUNN/QAblTp0ojpCRyVSgYdBoI1+AEdpExZXC3i8id4H'
        b'uwT8Cn4tUB8sB4onjAoew5M6jy/WiGzQ0SlYhBqAKK3NG+FoeH8FzdxPOFT68L/V/09zw2cfgiuykLdXg0nIl8Wo8FlsW8JE0bLmaJjA9wL/AoTIcuakyWhNQf3vuWP3'
        b'tyqLTsW8hHIiJGVV30knNOIwM1pSJvakYpjEHlckimlNVolgmDpxtHWbskHsbel0kgiKahJHgnpT9EmPqe0ycSiqljGJIHXoREjrceJMKElTpi9SMY0IexSNOGKGpChE'
        b'6JC7aBV6eo9iKKphxlRJJk4t05ZUJLKoziIyRmO76JsXabpsmkqiW+xKJUlWQ1ratV6hN+luq14tqyA8RbIVIy2aSkqmJ0ppxL6+ed16kq3FdEMWaRGwuckjqXT8qRor'
        b'R4cYV9oVk7hikiRrpkGyWcNEM02dQ7WdCM9HG4jX6FASpijrelon2RlV6ogpqhwX5S6JuEXRkGlXiSLxqWkx3ZbIGBJLm0Tc91/Q5mRUUJ5a8L+s/i7VQR1Y7wRQAXYD'
        b'dAOYAO0AaYBWgO0AGYA2gBcA4gDgwuodADGArwPsBNAAtgA8z+TnAIBxqO8B6GHsOYAWRrEFgBvTUwC7AHYAvAiwDWArOzMQ7LpgrxcgMU8XBENyz/tSf295wJdiZfey'
        b'EtRSZKmjgvhFcW5/zgm/t2zu9XItJu0C2TEgskKZHG8sy2LEP+ISxVgyKYqWyTJqIFDgiNPKZ6rfgSPfuO/0/kcaZJJVS8c9k5S/DKw5xrizg3Pwv390Ni9hqoL/Anva'
        b'1m0='
    ))))
