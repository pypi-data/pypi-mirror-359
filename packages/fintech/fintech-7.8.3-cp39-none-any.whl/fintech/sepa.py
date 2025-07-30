
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
        b'eJy0fQdcVEf++Lz3tgFLEUGxrwVhZSmKsWCJCCKwNEEsxLgsvAVWFxa3WNGooIsilqix11hj7zXlZnIpl1yu5Ep+e/1yJe1yd0l+dxcvl/y/M+/tslQ19/vDh+HNvPdm'
        b'vjPznW+b73zf+6jDjwB/0+DPORkSEZWhalTGiZzIN6Ey3iIcVYjCMc4xQlRYlI1oKXImPcVbVKKykVvPWdQWvpHjkKgqQUFVevWDRcElM4rSdbV20W2z6OxVOleNRVe0'
        b'wlVjr9NlWetclsoaXb25crG52pIUHDy7xur0PStaqqx1Fqeuyl1X6bLa65w6c52oq7SZnU4oddl1y+yOxbplVleNjjaRFFwZF9CHUfAXD38htB8bIfEgD+fhPYJH4VF6'
        b'VB61R+MJ8gR7QjxaT6gnzBPuifD08kR6enuiPNGePp6+nhhPP09/zwDPQM8gz2DPEI/OM9QzzDPcM8IT6xnpiauKZyOiWR3frGhEq/UrIxviG9Fc1KBvRBxaE79GXxJw'
        b'nQLjCCNSrRcKKgOHmoO/MfDXm4KpYMNdgvThBTYNXP8yTEBiby1cleftXz0IuWkH6/E+cpC0kE2FebNIM2kt1ONdeBdpzSktSlShuBkK8jJ5CTfrBXd/eBpfC8ZnjDmG'
        b'nMSJHNlEtuQrURjZLBRERbij4LZiiIreVCKFglO78BF8D193D4IbyuqSBPZ8fg5p1eckj1KgSLJTwHfxcXxRz7O6n8b3VhnHpMIDRrK1MCd2mhKFDxUmjSC33f3g9tCp'
        b'IfRuTj69OXUsbfiiMJqcL4HXB1DQGieSJie9Dc2QLVzkEBScw+PL+PxU9zC4n04u9AohV8PJDSfeRG7Vk+tLcEt4KEIDoyOGK9QRZLueYw31IU34LGnJyyVbBCSQlzi8'
        b'H+/DB0Yq4D5FgVHk4BojvhCfk0g2G8kWvGn53EIKE25NLkjUq9DMGeoGvIU0y9VV4WOkkVwDoPIK8QleiZQNHDkxh6yF+zFwP5qcjEjITTTkJyZxQ3EL0kYLwfgO3gS3'
        b'B8JtcpqcdSdkG0aRTXnQq3B8B4WQ7Ty5+BTZXcl1WGWpvqk/SDG0PX6i/xZDPfEevWeUJ8Fj8CR6kjzJnhTPaM+YqlQZb7nmIMBbHvCWY3jLM1zl1vAlAdcy3jZ1xFsK'
        b'/IBOeGuS8DbCqUKAtRH1FnNeoV6NWOFqo4Dog5dTRcNPUmKkQhOkEQil6JavzJubWCYV3rIpEPzXoUWLtbnjI9FZZAuGYsuCfoovItG0v/VesZDwN0f/S9GXswXBjYSE'
        b'vdz1mdXhaFr5mF86mnK+j1gxF/F5eObE+CF80W+5r+ddcv4LeZHbQGeomV8JC6gleVZ8PNmcnA1ogc/Ojs8t751PthmSchJz8zlUFx40JYRcd2dRTG3FZ3Cr0+VYusTt'
        b'JLfIZXKdXCU3yRVyg1wL12iDw4JCYV1cCsHbcDPeMiZl7Jhxo59IxbfwZQXCLz0VRC6Qi6HubKjKPXaEMS+3ICffSLbB6t1CNgP6byKtAE28YVSSPjEBX4LGzhfDy1fJ'
        b'HrKD7CbbyXNkZ808smsuQn1TQiPxZrKtHSbRYVXDX18fzWa0TqgS5Jnmm2E+Vwsw0zybaYHNLr9GKAm47olCKTrNtKLAQVHAumlDX6VzIlx9PllpNC945Yffubz9ynND'
        b'lW+8YJ73yu2IN5565fr2Y88da7RyTnVlKJl+ytBne3aK8NdXqtNQbm3ogPHD9EoXXVVPzR0HcwI9Izsm03WsmMjhK+S61sVIxWkYpc0JSTBimwwcUuGtMeQ2n4g342Ou'
        b'PnA/awC+k5AYn53Iw7396klwaxM+6YqGW0NK+IRE0po3WolUZRp8mSMXnp7tousc3yVH8Q3Sko0vIMSvxgeAcmTBjL6k57x8vF4vOGhvAxIekgfRk6sc9pWWOl2VxLyS'
        b'nJZ681Sv4LaK9D5gPvxkBHORnEPle0mv8AbVmWstTmB0Fq/C7Kh2etUmk8NdZzJ5Q0ymSpvFXOeuN5n0fFtzcE0Xg4NOrENJE1pfJm2Dkhn0UgSv4nhOxVL+K56HmeLQ'
        b'1zTnpnM1xzY8AfrNIR7v1aVxGXhLalYl3wXWsImdSrGGZ3ijqFL48Ub49nhD0SO4E970LmB8J9mENzjzlCiWXETkLMxvJL7NoF40Z7ERyofgM5weEQ9MyiFWPoi0rCHX'
        b'CpUIb5nCQXqjaoibTq+VnCslLbS8cQ03A8FqOUCaWRNR5LmMEGB3uIm0cL0QvreQ7HTTFQIr6zBen0BvXcX7uFmIHIDFe87dC+7lxKOEJBVKHcI9BYTchl9kpXhbdC3Z'
        b'OQvmJA6tRPlP92JNk2PkON5BdsK0GBCs++cMpHGYPog17sIevGcSjDbZgCaQ+2QDvrOK3VCuJPdW0fKTaDpuJSfx8/gO6yA5FK/H96AusgcVB8HKfzaWtRJUiTcSVn4L'
        b'kZ3Qv1t4M8eqCh8I+HtPoK8iyiYP1eP97JWZZHcSYTdeBCQH2eDFWLJFGnZydzS+Fw53jiJ8KZ4cjSDrWesT8Ikp5HmeikuL8dYQcobsY+XVeCu+UwJVxSFyA5+Ig5XE'
        b'KgI54cZqshPQJwXNJrdTQCJ5mb1QHBUPUO5Ro7A5MGzIRJrqGNMkJ2fgM+Sak1xbyqEKcp8nZ7gR+PlxjIq0I2Z8IL2hYkY1akBPR6zmGrhmEDYdigZuB79EQcVLtrhY'
        b'cpb38kkpXq7yLNe2Vtmq8QZPtlmdrkp7bf3UeZRO0TbcUyCJx2uHGmXZJRNvZ9JANtmFrwE93lRYQLbo8U1hzBjcYsTPAuQh5DzC98ndEHyZrFtkvf7SRt7pgWo++8P9'
        b'2NZJYTglInNZHFehObL+Wv36Xa5jTXWKJ3QnryZsf++X6/BL+isfVv0p53PtD177Ycju8u/uT91+8J075Rmv//HnytGZOWPwF0ve3nfuxPD3+qv0LVcPjdtye8j9zBEf'
        b'/uHqk8Nrpp1aOCV4yvzohIsXxtZV/GfHOcdbv1r12bLPfvzVv2/97+/rnjzVGjd33kAgo5SojSPr8fmEJD3ZDJxOBZgNvIRPTSR7XHQozcuNILmQ5pw8vBFfLVCiEHyF'
        b'J4fItjWMBtuA5dwlLQaQ6ECUVPUlOxfyw/GJCtdQuLlyIPAdyjXJZpDWyCZ8PlcJa7e+91iBPEuexc8xSg3MavdymZADFU8mdxghB0rd0omg6hUdKWyHqQux1FXaRYuJ'
        b'klhGXHV08rIVnILTwC//tUrQwHUwXIfxEVwYp+ViOEevALLLOb3BdXaTE5SGGovTQcUCByVKnWHhHRThHJF+asvIgZ/a3onsntoOpitrKb7sQyYJkxSoP3lWQTzisrkV'
        b'D6G7jFu3o7uPzq9rHo1fB0mS2bjKSDQ22AhX5QPFafGSvPXX+Bz0ydNxHCovD/ZOWYiyWOlAsRf6Q+E0UDjK87Liw6VH/zkxBI1dDEJ1RHmedf4UxIhB2TLiSU2BKT8C'
        b'zeGdqCKVnLG+8I/XkXM+Xb67mz8u/6i8pirP/HZV/HMfrL287+r8zWLx3sZ+aTF9UgziB+IH5YYxwtV+k2L6julzIF0snlccU7ZvRLphY9ScCONB67+pAHFHJfJPjStJ'
        b'EapD0PAvog//4Xd63kVbH1yaS1l/r0kS8wfWv2eKi6ow5FoqvpiQlGMYpU8CuY5sEsgOhGJ0ioUWfEvPPRoK9qqssVQuNlU6LKLVZXeYZC4fRke6LIYhYhikgHZRAWgn'
        b'VFpFr7rS7q5zOVb0jHWUYDv6+LGO1vKUH+tO94B1CXC/XwzZacQn8B6yNRv0KLy1MCk3H0QksimZConA/KfgAypyKhK/3En18KMgExg5QMI2gZFjCPhoqkEnxk/7EdsJ'
        b'AYdJCDgqMxKNQIdVFAGze/WRce2L6F5It/wAD7im9U4cjGaz0rdmgB5gWy2AXG/TTB8hYaCwCGRDxV411YlPzVskFaq1WhQztlRAReW2n1TkSIVf1kSj+Mk/QfD6gjdd'
        b'yVLhriGD0ISizfTJydNHpkqFkTYdmubaQFF98uG00VJhzKwRKHvaT3l4nc9dUygVrk+IR0WZagUsFf6XymlS4WezE9E83V5a5/QfTQySCqOeViOtbg2PdOV5ingZpMj8'
        b'YBSl+wsPy8cQbdNLhQftcSjPlSzAk/zaqeOlwivGBDS7vD9daPz96WOlQntCP5RSPxO6Xj55dfxQqbAkPwge+o8KCvPiCldIhdXJ4WigtoFHKeXaESDisMJfT+yPxs77'
        b'ioPHG6pXL5ZfLxyMJhtSlPBkw4b+TqnwVwOGocyGCECT8oofLJZH/u9lfZBh7B0FwNlgn71SKvzPU0logeZ9AV7nZ1bxUuHREWNRDSqkIx8ZFpQmFabGjkFiQzyd+cg3'
        b'Ji+UCmfkjkbl4j+UMPL8xwVTkX4EE7jIFXw9gerGeH3saDR6UY0bZBbUS0fWpQJCLQkZg8asSmVlBtWUVJ7aEsRUlGoys7fn4otAkKChkLCxaCwIwW5QMdFYvGthKiyC'
        b'YHzpCfRESi4rHBY1PhXwlZzVj0PjcvA1N6X/uAVfElKh88vwhvFoPD4wm5E5cphsN6UC4oEucnQCiEx3yX4m8+BLa0ASvEaJKjkwEU2chZtY5YXJanwN4F2In01DaeOX'
        b'S5U348396bJQ4c3T0XRyUMGKQadcR15yQldGLshAGeSsi3VFn4lbqEoBDLcxE2VGq1jp0/j+cid0BZh4yww0Y/QwVtoLr1/sVFJpdWEWysL3kqWh3EPWRTihM/qQmWhm'
        b'Fd7BQNaDnHPISftyltzPRtnk3jAGxhCQ+wjtCT6myEE5+HofSdQ9QO4PJ7Qv+BA+notyySV8QxIEt0ANW8g1OgcHhxiRcREI8uzGTbyN7CPXAPil+FYeyssgx6QBWFef'
        b'Rq4B9ORUZT7KzwX5lxUfmDqJXKPg36spQAWjyVEG/izSUkauAfiRIwtRYRZ+lj0c/CSM1jUAfz5+tggV1eJTUl+vZpGz1OCXsWoWvHk+S5qeLQ78fIiC6v14dzEqrsJX'
        b'GOr0JvdjQgBu9/ASVNJ/gAT1IbxrbAgd8H1422wQbfdCi6yS/SBJrQsBsLNXlSJQOfAhNsfkXOGqEIB6HD4yB83JyZTguDBhWYhA5a9bcwEbm2ukKT7tJFtD1FQ+f34e'
        b'mrcKsIQ12Yqb8Mu4hXX21nw0v5TIaHhpJGnFLQC4ZXoZKjOQw6zyenLcglsA7pg1T6GnyMF+tn998803zxQDrdS9qIAll5ecEyqtrg9WAzWJMqtgxUaaKhqQ9ce7Jiqd'
        b'P4I7W8e4ardNKhDSIzLPVfcZwD/3+WjV2/hvV3oPeWVf8iuhGsOINw5nrm1qWsLv32Q4MfR9pLi37LfTDq6PeY3r9cIZk7o0+Z4tgXz6n4q194rHNT3jTm8tm5J/Jnjx'
        b'+Z8euJLuSTqcv9J25fth9765OnWV9r0/r83YGDPzJwOd03+7K/WdO//aO+JHOf/AP74wYObJJZY9dw/9+vYfnt22dc2F71ZfP//azN/0f78sNXZVw7Y+0av/de97caXz'
        b'rwRbvon/4Od/Wnzx96k/J5d/fHXl1+N2L7j04ezvnlv2T2HxpIkHh88C8XcgG0yQPe+ACBuTW0Dtb9sMHMi453hyccnTLqr8gUr54mgqL+DWUJ/AQPY+7aIyHLmOb5Mb'
        b'+VNBjgOikZ+YSw2jkeS2AC/tL2Ovx+bVQANbjDn4ZDU1G6gm8P3wlijXEEZg9uBTeIvWiS9kFyTGU+sp2SagXmS7gC8viNYruxQ1FF3JBQECSJgsgLgrTVQWZtIHNWIh'
        b'UcspQOgFCYSP4uiv9iuVSgGSQQwtEcJAMokA0VgL/x19fXXqBZBN3JU9iSScI8YvjfRl3NsnjRzuweJALdPk5DwYGiqK4JZYSRrJh4SKxEqgOGuVeCfoy5sfIolQEygK'
        b'kES4R5ZEHlEUVkuSyJcDQiuCQH0Frq296B4nSyJlfYNr/sgxAdfw7hoRscVfphuamqJgZPAYlW+LyRHr//LzeWcGRYnfxX9cXvbK5e3Hdp5tPNZ4dt/oDaMPHMsetkEf'
        b'84bRXGCusTyruBJTvDfdsGRj2caw1/qrjqY9Zzva/7fb3+mDftgr9D7/cz3HJNl4cqFMsmKZ9RJmCoN8cmoPGNJfwhCny+GudLlBUDU5LFUWB+hOErbQ/QP0DOI1gAtM'
        b'Uu0XgA0KJzzcMzr096MDfXG9Hx3W9oAOjHc3kR3JRp9kmpykH5WfpE/MzcebkiG5lWZMzAWFCZRQvANvDibrasnNh6JGeyH10VGjqiNq+BpojxqqAondbcEXXCHUNIF3'
        b'rKFq/74afJehx4elT6CaqE+pSBr5flIByrJOufupwjkebn1R++zH5QsYHlxpXMJVBr8//bVhd8JOhb1W9VrUKdtzw05G/al8Y5gq4sm960C4CAvDW0P041eAFkPX2+AY'
        b'3NxmwQRK8hLQpQ3kPKNqxj7kXKAiA7Sf3CDnQJNZzMsT2T16xHTQYNojR7CEHEEarg8gh2NAIGpUPhQ1BvpRg764iVY4mKEG+rIH5IA1hxrIORvDjbGLO+otgB1+1FiB'
        b'zwaR5hKy/6EatNDBcvlfWry7wg2GAYXpIFnPe4nKyzZ9SYjEaKNjgftOaFJS7nt4pqxVRCSCpqJJgqty29OTxiKraurfBSfVvbMHH/u4/JPyNyr+VVZTdd7yQfkZc3yl'
        b'YcwH5fNeub19KJAP7o2qXPOz5R+I/I/f1q059rQ6Q+0MLkl9fkJGXMbQokJQgvujWWJE3e+DAH2o8kguJJDt+FzevIH5Bh4pjBy+OotsZGyJ3AkhV4Ejkq3JhfmijbQW'
        b'5ODzCtS3WDGONOIbj6oIh9ZZlrtMottiEs0uCXciJNyJCAbmw+wxoAo7BvkxSOFV0Ee9QTaLWYS3VjzE/kIxxzHEj1G0om0BGPV5D7rwCHgiCZSG7aSFbvThTYX6fJCr'
        b'LuMDhWx3M5ZcVZalkZcqhYBpVgZi0XQJixRsD07pUVWpZEwSmA1cAZgkMExSMOwR1ihKAq57UoVVnTBJKWHS6soxjLn+MG7VmAlRkRLSJJco2d7Xb51VhqJMG7J+6qxR'
        b'OisofbH3GrTlSujaFK3iN0uLU9J/9mbY9V36CNes3Hu5lTc1BypmHVr4TNrpDX1V3z2um/jlvpWDPqkZ+2V5Ze++f1w/M2rPmV/emRv7g9a43X+b+VnUUyPV32ys/ubl'
        b'fkrj/qW2P6unlPYbtHonyFAUl/BxZFkkbZCpEY+Pc6XkHtnMqBQ+ic/i68Yc8vwaedMYH8HrySFmXAweO8BI13ALaS0cDK8hDdnCAxO4XMzeDeHJJbjXjA8+mQxUTpHP'
        b'4ZfJKbxWEssO4btF5D4+QVry8XkEzTZxM/lxPclMqm5vdURdbbWlA+b2lzC3H2Atr+CoqASCEs/zGj7yK4XKofPjsJLiMCAuRUuvqtLtslcFksQuFw3gNt2+dgxtj8+0'
        b'0n0B+Pxhn+7xmb6PN5ALqcbCRBmZJUQego+T68UKEEROkrPdc8tpSBak6F4yqlJ+C47Zacc3lNK5Trg8RMLl9c+8hXbBjP+Qq9APGi7j8ueLh1I3kgmvTHdNHjt0jlQ4'
        b'eam043vZYdbuHDxTKtw2JBiBBKRBM2q1/5woSIW7V/VGdGGXly0fmJor2xuSEgahCSAqRYjVCwZFJUqFy8ZQewMsmsyG4k+qKqTC+Ew124QuGro47129bBepSNKjImi9'
        b'SLdkesRs2QATMmAqagCeGlH/jCNOPUkqHFo8GS2HWo5qFkeu10+XCs/2T0MugHNaSrnjqZHzpMKfDYuhYmTKtLA1Aw0pVqmwMtaA5sHrRYl1w5IrJ0uFaXMiEKDBhB9a'
        b'1hhWTYiSCsXV0wAb0IS1/e1j/lZdKRW+UyhtgddPr8p7v1IuXBChRbCS4n+bZ9EuyayXCi/UD0Bj6dAlL5u8wmmTCqeuGods0Pe/jWsYw8WVSIWOobPQUWgI6e25f0iQ'
        b'gf9IK6I36F573yVZ/VzzpUKFohq9Da9vdyxXva0yy/awjL4IFI+Io4utk9dUxcrmn9HADeHe5bT6PCsnj/yyXqvQFwBSSsOKcVOyo6XCf2hTGbV7RbvE0Tz8CalwhXU4'
        b'29FMWWzlfzpgEbIuDjFyzpGA14v/MKF0R3oxSdHO+ON71t+/GpsflLNoQvCtD6LHWn7Ur+qN9bvvf++1T1Y2/Yk/2OSsDxPfryof/vJfk998JvLIiidawv+4u+9fU1oX'
        b'LnevHb58A14vvF0U6VrrQLP73P7TLPve4JDhE9b98ZvBL71/4cyq+sgn3gzLvlxyZc6Jyzdf+emrZZ66Z2/fmPzk2rf+vvUnaFeq/fLvZn/0z9LvLc941/OrEQuV464f'
        b'q7j/4bOlb/5n/9hP31n04B9DXwxe1DT/7kc/fXVATtqZNxJvXjvxPaOh+jtBL7zxl7cnPv9y+JoTqwxzPvrx2xkftPzk0tjz14Z/b+yPfj80/72ffn+08dPme5m/ePLS'
        b'lIuvfvrWr3969v1N1waMmTvvX5OO/HFGnkms23foTvOtwhcurX97mCLFEtKU+tUPqqduO1r45DOfWS//6Q29IFm6m1RjfBxe5u8R/RiHH4cbGfE14VPkrtEQnw1iFSxT'
        b'0IgVjhXk+SmM+M6lpvsEeHsUhxRurj++QTbF4nP60IdQ2IcnPdDvQBs7pc8V5rrFphq7zUrpLSPScyQiPVEjAJmGvxFMzIjgdGybJ4KJHJG8VhEMxJvngqVfocN/6erP'
        b'ioFaIPOgDwOJB314uJ/Ag5i7wmJ2BND0HlgO5xjhJ+e0iosB5PwnUd2Tc6qv4+vjs4zkai0j6LlkC2nBW5kLyDayKQ9mzKBCU8gVFbkdjS920lSU8n9nFSQW6oyHyngx'
        b'hFnteVCIeFFoCioTLApRISqbUCNXpoRrlXytgmu1fK2Ga418rbEoKJOo4sUgMbhJAyVBHpCty4KZLq31qtNF0WFxOgsqVQGwaOQ/xgeod4zsrOR3XqrSyOxG1awBdqMG'
        b'dqNi7EbNWIxqjbok4Lo73Z3ys866u7JAssYdiiH7Syjm7yPPD0VDycZwyR0lbqNT4QQKjX7qnT9o85VeOCVC8U3hc00lnlczo9KV78SvzXxpR+Xpwen/2px9UXu25Ncj'
        b'Vjkn3TP2PnV3r+s3x0Zt+WvCrCEz7o0ZfIv//e2+thjvF5/kTdr41S8WzB2/7suGI5vw32Zs044UQg9qL2VOSH3+c/yHg6GF+24NeePikCcyW/TBkrPKXpjTrb7Fhl+Y'
        b'wNbbCtyEL7Hlhl8eVtq2Q6rom0g3SJ+SvGDIDsUyfJ3c9+/g0t3bcLKWqYHkObyjhDmy0YrJi3griFj3eLwpG5+V3GCg7IYpJiEpUdIjT/Ap+LlMRiKeaSD7cAveRrYZ'
        b'E/E2vE091oRC+vDEQzbg0+yJXLx7EG4pBDJAWhP0+AUFCse3hgYJLryHNLHqly+pj7azRwz4rAKpNHw/vL2OKRn4+ZWgxrUkk+bkpByyNQgfLmS2s5MCWTcP72XyIT6D'
        b'r1XAM0n63PxEbkIECiEtPLkVR3Z31gY0j0xm2siI2mSqsywzmXj/qnwGBHd5f7gP26ajbjkq+XdluIzeSfJ7EkHQeIVKm5PtyIEGbHWt8Grq7dR/QLR4VU6Xw2JxebXu'
        b'ujZrS09KjcpB/Q8d1Dgm7fHpaUJdUx0JfkoyEpKvAijJxv7dUpJOMLcTATn5jy4MJ12iDWiRpJZwBWc5r8Ykb0jCtcJpsQW4T0gDqJlsM9dWiOapoVCLg2p3KyN87flu'
        b'PVKDVdCgnvMqTXT8HEn+VvxNOagJIMzXyiPV2STVGWTyzUa39YY/Vr3VUr1qkzS33dYa0WWt7aTuNCTZqICgPr683Ul3pD886kgAhQLrsJYJnJOa4uqLV35cLl79oPzt'
        b'ipoqbdVvQWTr/Rn/al2OnmMLjuxYjHez9boIpAP/kr2BL0iozne5jEKtzgBbYptP2zPw22dltA8h2j0l+eAIjmRaS9t6CGwgyT+aIK2iSM7nzbEWfv8W1j3Gd90gMAL6'
        b'ow8BrDZR1zqTyRtsMkme43CtNZmWuM026Q5bYbCMHfZ6iwMQkq1EtjDbluNY1nXqimd2OistNpuPHnRc02cpDkqPwSOsQ3Sz+590nOiujUYJoH8T2UvLsV+el5yG7XgX'
        b'vuPMy9HnJiapULBhwCKgvfjupE5THiL/d27hAlg9VybsEnaF74qAv9Bd4Va+iocr+VfkW1WigYoCAf7CEcCGqTAQBGxdYVGCMKBuQsD6g1p5EAiUYjDLh7C8GvJalg9l'
        b'eQ3kw1g+nOWDIB/B8r1YPhjykSzfm+VDIB/F8tEsr4V8H5bvy/KhAFkwrIoYsV+TpiyM9kSkYkf/Vo7BrAURZoA4kIkg4fDuIPquJVwcDG8LZRGs5+HikFZeTJStM4Ko'
        b'E4eyvvWC54extoaztiIhP4LlY1m+t/T2LvUuTZWwSyGObBXEJCasSCcA6GiFecKrgsR4Uc9qjIIaRrEaElgN0aLABJRkEIgqGQl9EBesC/iRS6WjCe3u6FVehRUkW6+C'
        b'YmJXiFdQqQ6YfLp0wnxrvpiSE0myCqIDKE+sz0E8rCpMJjNqJmdpgMyoGZnRMNKiXqMpCbgGMiMwMqr43ZeA2O3ApD85dVaX1WyzrqRnK2osOrPcKSuwOnNdJT2c0fGV'
        b'tHqzw1yrox1M082wwlsO9mrO9PQCnd2hM+vGJLrc9TYLVMJuVNkdtTp7VaeK6I9Fej+evmzQTc/J0NMq4tMzMgpLC2abCkrzp88ohhvpBUZTRmHmDH1Sl9XMhmZsZpcL'
        b'qlpmtdl0FRZdpb1uKax7i0jPjFAwKu0OoCj19jrRWlfdZS2sB2a3y15rdlkrzTbbiiRdep1UbHXqmEUd6oP+6JbCmInA5jqDIw8Pnfk0Bhe98p2A8Q0vaDyUlXX3ssyx'
        b'pfflDIxRSWFi6uhx43TpeUXZ6box+g61dtknqSVdvL2eHqYx27oYQF+j0B25RbjqGuJHqcfHqaW6fLlvX5/EoaXapOtvUVcnS39n+6y2gBmUgyrwC9SYaUiiJ1SMmUFz'
        b'SbORnaAZgo8r8H18B99hVoyMmG3j7goTqLNNWOggG3JTf3hyfTU+zayZRWQTOUKaqdCeTDYVkebCEqmi0my6U5yfn5PPIbyZHA8iN0PxbsmE4lDXtQrAOHTleScHZCI3'
        b'5azkOAByk+4/JxipB2berGxJWic7g6jATp7V47OoJF1N9uAt5DKr6Ol0oeJNjl6VG+7P7SeZXdKfVEyu4SKof46tz0JRqn0+uUBP0bRVTprpiRqANbk4m2zOU6GZ5KQK'
        b'dJB95Ap5fo7kErOWbMx1LgEuODyPbINOiOSs1ZL2gtL5Q7j78ju9YrdNqps+OmLG6/+4v+3LpszjQxPK+32yblxx/4TN6zPN8fmNB/69dPtnd8yD5pddzHdmTV3WcHJd'
        b'4w+qPvvbnr+Urn/zT3Ups/t+kvP+4XeeqH5/3a9//PGb3xVWz129/cBRT0Xr39+qGtB77BeT9uXvWL598YzxT73kOTS59srOwzM/UMd98+Enm/O+l7hh5Kk9pn9svTE+'
        b'p2HE2S/z3/nrLz9Znzzy62P//jDhz1xZ3l9e+cyZN/0zlYMzJmU8ce419/vG91X4l+uWPdvyWum4Ozfv32y9pZv599988+fdufHeKH0kcxPIXojPhcAY6fPxc7jFnTiK'
        b'bE7mUTT2KDTkfqmkqV10YOpIK/sg4KaxPjeExYNdVOxJw+vwfmNSbr4hB7eSbXSgDfiEgPrj64o6cjeG6VvDHU/RLcFB5IjftfEYfp7pWyVrhvt2Vi8ZqSFBOvwUTZoE'
        b'cltnk4DYMGgy2zXE68j6tp1DnWKha66Lzjg9VVEGMw6vJ5BNhf6dWuOCYOjUVsl9YSa+oga1cR25JTlYPEd2FElWacCJWHJZhUJm8fDaEXyZOSBXDiPncQsFaCDZQWFS'
        b'kv0cuTuhknVJPT6XCqQUmwRygAt14a39yV1Jbb5BrpJb9FWKfxvITVhoSnKX55LGSEauF3FrYgcFNUhwk1ZXP3LORRkquVYZR3XQVj07uWbIIc+S43R4pVWbgK8pQdt9'
        b'Fp+R1PA9WrKX1ZfHATBHuAYD3h5ZyA6NDHJNhTtJ+RTKmxw+YcUHRvRnUC4cV0lBzKc+INQgH1Yt4OOkMY3sms4U+PLxMLMthT5BLyxDmDAlaxZpZF2ginc4fd0Ao8xc'
        b'hMPwGQE6/VLmgKm+jbiw/9rq1lGiBxHZCtxd1oyzfcL8aA1zX9XyGmZMU3BhvJbrw1OzmpaT/KqpA4mqwy9PJXX6+5VKBfqhRHmTfE0USFJzkKQKPEmTacin/XaQudsU'
        b'hUdW9/VqqZI+7WtndSb7K2ZSOd3RG9JOzXh/ZPdqRqeOPLKie5YqulQG6lZ1nBegTsut+NTpB7Gz/QITZWUgXPh4WbzDYhYT7XW2FfokaEMQ7ZWPo+0rTBXWym5BesoH'
        b'0oMRFAAQt3ps/3EaVjJ9rNuWF/pbTuhZJnp8AKiJwEFtrd02bvY3nhQoUP037QfL7S/ifIYPHhacWVJaJWTtDhqx/VD0JGw9Pig1DBRHoX95dAdFtR+K5EcR077toEiQ'
        b'jOoJkkV+SBIfLuJ9O+yUoOgOgFo/ACmzmd4CbQea+nTytOps7GB6tzD831iFJK1T8eB4Jxk2g+ofTp21w4p1Wiy17GA8KD1MLen0Ij0sL+tiJaD7QA9nuB12XZF5Ra2l'
        b'zuXUpUOPOovM8dBt6Dy8uHRc0pikFH3PQjX9UaLOlvvZes5N6fbSIrw+gXE/xTQQGTn8Ar5FjlsPrr6JnPQo/Nxrv/y4/O2KbHO8Jb74g/I3Kj6BHF/xp6jXok4t/FPY'
        b'a8tVOm/ytqF716UOQq9+FjRO8z96heTp0oTPODuyV5CErwiZeCuIJ2xX/QjZS675vdJ8gtOwCZLo1AcfYsKBHV8eFXCifGoZhw/MIrtdtE+jHalGKsHY8R7EL+SS8f4p'
        b'PdnT1NRw5TvAJLtbPYOWBnN9qDlX5gfyMxL3dDzRsbY24xndFKtvx9We7cF41rF+kDGmwWsPcaaiFgbk4R7bmUpgi13xwNMJP0osLsmq4La5rKBTy3Tf7ZSVaBYiwuUw'
        b'1znNAaEeKlZ0qojWkcbsLGnl+fAMVAX/zNUWR/lDVD3609mcKrviDAnaWvELWYO7H5GI3NShbzjZ8bSswAUqb6R1Xk/62z7r+R9wSucEqODdkrKPy3MBjQ3FH5Z/UL7o'
        b'tTNVn4gflSt+pN/yP4YZo2K1+mlLexedaJx4ePQGQOdrIKIuCrnVOEvPM1HTUGeW1AyfivFkJVMysnCjJO7uIrfJnZn0EECAzNtJ3m1ZJrtjPWwX1mlxmXzzw3h4oJMX'
        b'/eV8ouHKfj686vROga8xJo1RZOvZ6Ys9kexHb3pCc2U79G7u3u2rBzAeiSXUSAJLWPtXu+UOG9uzp0dF5STfIS+qHnTvgEYHQnLXocZJv8vOo7qfyczid3lcF7Y9//Kz'
        b'O6zV1jqzC+C0it1x1jrLMpnWj04a3YUFpXuzkSjZZtgQ+PxNoaEkXbFlidvqkEdIhKtKl060VFhdzi5NVXTxAwROe61PRrMCuzXbnHZWgVS1NMhVFoeze0OWu1KCKGN6'
        b'DjBy6xI3rQ9km3jKtHUOH1TQVo7LTNn4w2lIZ8dQTYGbkk1yimwnp4wFdGufxZYoSJyV7XdrnZtXTJrzZmULxXp8Nke3sMLhWGNdGISmV4fX4ufxcTflfGTnGGqCwefJ'
        b'6QAbj7+OYoSvkt2lwOF2c0vIDc3c3vnMXXkq2VtArmnpkZpNDnIG4cOL8U439asBBfcUbnGGuedkUy/8UtJsmEOa8ZYssg2aOTs720Ab2ZKTR4ANbyYn9MvxcyPIqdk8'
        b'IrvxLW0RvogvuymticiIDTQN1ftrLJqbOEeNyP3iomdU+ITZZHUfP4GcdfDKi5+/lvj2PeqvOGPWM9jOZZkjYta+Fj0jmA+J2Px6n8v6OUevGIY8nfHEyi1LF6qbNvxs'
        b'TeX7b6sz6lZ8EBnx6oxrJ8whI7cf3rz47PGn3D8/FX76R1Ma5pRtsO8r+WKV8j+Tvhk3vujIhR9l/upL/unlulspmfogtuU1LhdvJM1rgGz7FPSQOp4cIJdS2BlmdVRE'
        b'yChqMNuEW/A5oJI+0joEX1OQS8tnSZaBSyW4Fe/h2/yx+URyfI50vvkFsjf9GXzQGGCG0EYI0fheBrOP5ONLTolqzyJN7WxD9fKm3CncnExFC7yrwB+v5gA+Sg5LG+lH'
        b'8smLzGpDDuC77aw2eC05x0wsDeQFNzNckP34nmy8wNuz8QbJR/Mq3o091HwxihzyWTAOGMbIDo2P5JBD6WkbrfAdeh3Wxgp6aziVzA60MlOQcqoOVLldLQU+GBjB9xPF'
        b'njiEEPBYG5t4GpJNnA+ktez3y+4dcHoA6XHUfIUJSFy37OGYnz2MZtpcG/3rSYV5TA1Gz6Bwd6/Yn/BDMalLwpdRmtFxt6ALeKhbVK3DUuVVOa3VdRbRGwQk2+1wgJKQ'
        b'VakIgJUaz7U+ilggsbC22FrIEyK7BWmrtDJDUzQrgaEpgaEpGENTMiamWKMsCbiWGVo1MLR9PTI0KbaYJAgy3hCoEHW/ZUX7JnEG37v+UxHd7z6wkZDeYq/AKNIyM1UN'
        b'k3QZ5jqqd5nlexWLgMd1ydzoxhjwm5LCCeNSRrMtMbpdJVJ1F1Sybpv3T0CaLstmrtYtq7HIG27QYdrntid8nequ+Tq7q4tmHBboSJ0zTZfeUcIul7vzCNyxs94XXOCm'
        b'ljhykJwHqilzxyExEn8kzTKdLs0GllksszpuTCTeiXdSNe1aLoolJ8LI/pHT3JOgmiVacsiYlDgqF2iv/21yh9yEGvycNzu3NF6KclEAkjk5OUhLzthtTNA/FZKDtusG'
        b'CTTUwUerw5GbqlpPkn1kdxeSPoj5ibn5JUzKJ2srZEG/pSSIvOywuemJJLytEPTLFvYUM6PnUHaaMIdFdtozNWCbJtuQm5eUkzhKhUiLXrtkJd7OjsHgtUUl7TZ06FjQ'
        b'puPJ1jwQ5KOTDfrEXCVaSU4H4dYiXi8wjp8TgTexZp/SC0gxlQNedi6dBS97glwyJAAoF+bQ1/OpE/4+fhXetoCFXCOtq6Yk5ObLA8ih3nECWa8mBybivdalW77POekR'
        b'no9UaNA790JJilZRVGxq4cZs8LwR8eGPf9G6Fjl6RxzW5X7nk+3TvWN37U8YXO/ZOdv01dpLcVXn/5WV892/pV2dt7D0+7OTj1Xc9Lz/iw+vHujzatgUw29++tXYuBF7'
        b'Fi3fGT/778aSLd8znvkybNSI96arf/WgJvntwR/0v/Fe+nMDn7n50bbV/ZIHbz/8zO4DCTOa3gWezg7IHsG7LEZmpucruPq5o0fjFhf1uQDp5DRukRk6ZeZ4a1o7fo43'
        b'yb5ty/AGthlH0YWsJ2faBIOtZDPjqWMmxMKtTeSl/FEgafFIg1t4vA6f00i7HrvU/WRdjBwLDeTqwjS2r9Ef3+pF8RivxfvlcxHkXBKreQW51SsBH8YXyaZCdvJGZeOH'
        b'kVayn20E4Rds+ALz3S2UQqsYYFaSBXIObwAR7NwiyXNub98B8q7DcOzxbzykmSXHG732/2ijIISyR5l4MI6f1Mbxx6pYqAuNn98Hy39advKH7gnw/wlWruwdyGrlumS+'
        b'r5I4OCUaDuoK7rC0Z/5Bj+dbrJBqYpUk++tknLAaktMd5INfDOtePugK6MfxStP4XuqWL7/h58tDKQMB8srYiZ//BNoS9Qrm28TDH5el7+MYRyuhFgkHtSpQP0fRXmky'
        b'sR0OB91rZjshXoEa/KfRbBebLV61zyRNLUhMz/aGttd7qVAVIG1Vs7d8/WIT2Ov/aGuqOwR00LBM/ei8NcCFhlcoojjVNwo6U98MHsdQ7GuV8C3/K8KCtVxkMC8FDlIE'
        b'c1F9Oj4RyemGSNcsvmXa8GHOvAJJ0OdQsAvfWMkDwbhHNnXie8Hyf+fXHby2RL5MIQplSisqU4mKMjX8aURlWZCoKgsW1WUhu5S7NLsidnFVwq4IUdPKi4UgMYV4IqoE'
        b'5pRN/ZG0llAxRNQy76ywVr4sDPLhLB/B8uGQ78XykSwfsSvM0kuKKASSGHUZCvf0qtKIvcUo6mEFNUbuCoN2I8ToVuZAzp7rVUV9tvrKT/SGOqm3FnUTj4JnqPdWf3FA'
        b'k6YsGmDjxIHiILjuIw4WhzShsr7MGwuVxYjDxOHwv5/8xggxFp7qL44U46B0APOwQmUDxVFiAvwf5FFBTQYxEZ4Z7EFwnSQmw/UQMUUcDfd1rGyMmAplQ8Wx4hNQNkyu'
        b'eZw4HkqHixPEiVA6Qi5NEydBaaycmyxOgdxIOTdVfBJycXJumpgOuXjWwnQxA6717DpTnAHXo9h1ljgTrhM8QXCdLebAtcGjgetc0QjXiWKRbKoRxHyxoCmoLElUMCPM'
        b'LK8qvZa5ib3QTmCi6166IXmKSaFrQRakgQSrHWYqBEoSXOUKv9NSB9eg9n5nDqig1uKyVuqoZ6NZspxWSoIoFFDZEuqU7C22FTp7nSQtdiXN6XmvyrTUbHNbvEEmHxRe'
        b'YUZpccGDyTUuV31acvKyZcuSLJUVSRa3w15vhn/JTpfZ5Uym+arlIEG3XSWKZqttRdLyWpte5RUy8oq8QnZpllfIySz2CrlF872CsXiuVyidOS/rLO9VSg1rfO22s5K1'
        b'20yhdKGBdwZT8ruab+Ya+EZO5BYLzsEN/FHuGHKOcvEi38D3QTQYcTPfAMi8mhOFBm4pcpQ1cNQlEt7ijgo0hLGo6gfPxaAoNB6t5uo0cF9Nr5oRfa8BmRRQq/IYEHuT'
        b'StQwhSTod6auFJKO3nPyPLc5z3V8oTsxn42EpGSYpTpYSQ8mLmnI0ph/Wklh4tgxo8cHopEIuklOFZX5dc56S6W1ymoRDV1qBlYX1SOAA/r85FjLPmVRQllQVRzWCnc3'
        b'ukUavZ1WLlqqzMBa/GhUDsqKtbKG1m6VxgmQUW4HEKxz3z6kc/4g2lrHdrHaehMX64zzckleLuVDyjM+/AZ+HghJKSkFerU3omOzdOfFbKuvMXuD59CezHA47A6v0llv'
        b's7ocSyh3U7rrYZk4HIgZGpgMQRHMsRr1eKSeMd5fUzYVxWi/AlhGlGwD0fFUKloZLiHA43kTSMIEA61bOeJ//b4Evib8rgSJHZGGTd2KeouuHKakEji9LSlT+l9enuSg'
        b'R3ceGayzHBulbsH6l1+8GcAcGrpGxE7N8b7mIuTm6BpexIf4DxEIbEK8GrPTxDxJvRrL8np7HSi53YLybz8olczBwF1bAWoyDIU8Brp6m7mS7t6aXTqbxex06cbok3Sl'
        b'TgtD8wq31eZKtNbBmDlgJMXycoqlZnGRGx6kD7SvpfO+b/ujURyLWeGPOO4/GsUxs/6j7QFX6RW/+7QrolNaT0UzieBYllfWmOuqLToHK6ow0/0Iu7TVC0+ZdfUO+1Ir'
        b'3catWEELO1VGN4LrLcA7MujgQgenm+sWM0u802UHwZGRh7pHIgUyGfCBZGIgldMxdrOlLxEaSpH8FngYY+pm28V+H40Hb3HV2Nv4mEHntAJNlauhr9Gd+UBn3e76KFeU'
        b'RiPKp5XLLLaLjcMejSMVdjsN16urCrTCuNlUiB2moUsiuczigGW6FPijuYK6GHRjj2knYrJDuaijaSWswJ2I6DGPkrkJidk5BhW5S/Vg41xqsSBbs+GysDQ+15CTqEK1'
        b'kRry8mh8302VgZHTEKiTl8kNchufnhWfm0gDK29LKMA3yPHiRHKKR2NnKqvJFnyUnV3AG40rnUn5uWT3MlUkCs8g2/EeIWl0iZsuQbKBXMRHA20Y8QWJo4yJxb5qjUoQ'
        b'VDVxeB++1zeWydVkF96Cdzvj5Xj0uLFBibdx5PKKWex2lqOqBLeSXaWgJO8upSaMQm6NnlwXDVnM+BFMLuDDAI8tNleJBLyXw2ttA1kQTtw4eZ4zW7JuGEH9v4ovKlAv'
        b'ABafxydXMecDbiY544xnkZ3IqcnK1Ry5MBm/PNs690+LlM434IGarZ9Gt06qmz5Lm/mXf/8xPfLM9l8vzH49rHh4/5bsHOWm+O2/anrtrcsnDXEh5RP//pesw6mvl4Vq'
        b'BvW63m/Rg+z1A7c+N0hxvezYq7/Vp4m3n0eNpd/bun6L6d9/zfrj1ifP/E/a8J/2O7Pi6ozzO5ceGDh20J7fLcg5lfTHQSfGeHsnDvxn/XuhIfmp2SXN1w++vu2d/zl8'
        b'Z6Ljm7f3mMpyfnd7yS+4uav6heIvX9Pf/1j3dVbaRfXp2JsDwo3v3frx7SUv/v6Po392KaX588a3BuSdfmbMmSfXfyroe0nbDXfJaZ6FrALN5RJpUSNFIocvVOLbzDgx'
        b'7eklCYlkM9mUnE1aBaSNJLuzBBXZXipthOwjt5bgluTE7FyymUOKZA5fm4/PMxfJXDu5m5Cbn4mv5MGdoRw+RPaNYHfI86vqjDn5o/LVNCScSsFrJuP70unGDeQa3myk'
        b'4OAXxxjhvb4cPm6rd1F366fq8ZYAW06gIWcdvgqwXyTHJS/KA9PJzoQk/SgfAoWTq0J/cmwFPkD2MItRxspaY45hAt7si1FBXjZJYVL2qSJZ/amkGV5UFHD4cpSW1RoR'
        b'zxw7cwxJeFMyXU3wrk6nSC8jNzVJDEB8D5/GF4ywtqJr5NWFW5Ol5TWK3FeS9crBzEE4jTTj00YpThhdEhwKqcbnRWpuOkBOMR8SZRW5aixM5BC/lMMvKNLTyGlp8+bc'
        b'/P7tjmln4RdWkO2ZLnrcmOzBl7OM+cbxZKcxP4lsMhh9YSFG4a1KfCmGXJbm/AzZt5y0FOALsDQ9BhVSZHL4RXKb3HwMR8tvcwIzWiKDpvaUn1mS6A6pbEl6BoVRz1LJ'
        b'hkQ9UKOYlyk9qSnZl8Ikv1S5lPqmsvOaA2WBp8tGCnyntdhZy2/jWcpJrzI54llIvulgP2rs4Vhmj6BBzVSg7N7phsWeYWHPQE7gAmLP8OzLIo/meEP3Sn7WlZSQIbE5'
        b'+VSPJB5SkQa4DuVcfglNFhao5OCUhf7OTEneYOggbXSQLbqWJTqzuNmd5RYz5Y3tWLmPs9opy6e7KyuoUNIZMnNljbSTX2uptTtWsM2gKrdD4s5O9nWZh7P5jjpVe1k2'
        b'wCvSZXZUgwLje7LH7ZQ6/36KhCW+7RSfOEWFIIszUPt/iDTQ9dF4jeTKtG5qKAsSglxVeYIhTjrwcXLxQBY1pWhWVUP8AjlqylPCTZQ95zNAy2lLYlZULmf8UU1O4VYn'
        b'OTQjNBQQnGxFwGxPLWGfrkhaEWfsIFj4tm0kjosvzqbuAHOB67fg3fOSZwW4FwCRWjk4Ig2fJjut436cyzvPQo2fv+XNl0OnV/88LGLqoM3NE+asHJWQfftaxO53t1dZ'
        b'J3Ab/tln4NpG84GNn37/g9asCel/Lzdf6fvZwLQrwpjPFaPfjB+5WXP6l+9ln521vGn0u9N/98Hre/QjTlbaSXx+mfV/bqonlAw48LPgUb+qeiH8nZW9F24YVhd1+OcX'
        b'Fud+lPLuoWGv/7542/CrP/jp15q5/3z66a9T77w+ddWOdy9O1uj/HF2x8J3JR6c8w63aNOG11Xp9mBSlaCuILh7ZLSDqGelIxtkhjOjjO2Qfvm/0DwW5Ru4oUPgcwUZu'
        b'4nWMfjfYowMGEHiHEl8LZB8iaZUCMB3GR+mu0Lp5bSGYpoYwHlSLW/EhYAF++o9PTwhkAXTPQGLCTfj86j6l/o/7AA+8WcVYvqE6NMEfJgSF4ANF+CpPzpl5aavhzmwQ'
        b'nHbhWzRUU1ucpmP4ojQCO80ze/VLkBkv45/A055jzhXkRbx2eTseSjZPkdkouVmAt7uotIp3ASu/w+TVHGBfMB79ATb/kPDkKt7MmZI1+AR+LoFx84n4cv8EtvmiROnP'
        b'qBbxg0vnM5a9dCbeKu/K1OKbgbsyWXi35BG6B2TcgwmGfJBOWcR6st8G8gLeKTjINnKjqwP7j8rr1LL6wLjb5EDuNk7iayp2hkL7Dc8Hf83zmq95IeI/vILyMhqWJIzx'
        b'Osl/IoxbGSYzELnS9l50q9uztB4ClPDSs22OErsgiYe6nCPaGNla5O0+9FRHSDqp7JT4MJWdCv9UZYc/alzrL3IuHq6FRq4PPCDy7XK+EB8P+FjrA0Vs0hhQahmsXq2p'
        b'zm6SlWqnVzBXOCUbTBfqvTfC5N8ul2yVubzvdDoPw8iv7Oszu3R4rpNB0b9PnQdJM/u0RCPvyGrgWH/QYsExjfbLMaqBO0r7gY5xq7m6Pi5B5BpYnj5ZJUhmRrhW0M9T'
        b'MFsJX/Agzs9Ta61OAKOyhnGjWGAG1ILFlGp6ATPJhqC3tbbeZq20ukzSoDut9jo2c96g2SvqJbsVGxTZSOVVMtbt1UhWX7ujG8/jMFO9wwIszWJiz8/i5SPqiIWFVcGA'
        b'UfykWLAy2jdw7d7ocvLZsFEyJVI7KQwFtZQu4qr4PpLVBgYgUqotnnbSIHXVsco/qWHtodSYTNCmw2RaQOFjQlKg/Uy61z0aRjJIfIgoQ1FDoVBTNINRD2i6Az6pTTSk'
        b'gIkdjPK1HOZvmd1qJ7XRa4Wv4RiG/0cBE0TuGL+aDUIDt9g/CNzks7zjCJJtinDNVuWhLsBQmUw2l8lUwcvsHMHsrAz1w0HvPTYYnA8MfvIUx0na1KluWraYTFXdtWzp'
        b'omU/DiQFLp1hvkWxmLfrJBgWcYupOYuV0yvpfM4qHyzdIC2AZFliMi3ifd7yDFmDgYwGAEaf6ASY35ioZUNCG9X63HylBroZgjroZn0ACrS1U9fVADxs6BU+OsBN7XHk'
        b'q2Fend2MfPW3mXOlf86n9jznoJmYlnXXsqWL1eZ3nKdD61v1babhNoLdeW1Tc5nJtKrLtS3da9fPdrLtiC772Zfu/CBGhvlGnqk+dLATzgpty40RVl9AkkP+0g7gwfo3'
        b'i6LJtMbPRpjWGUAD2O0ul0AAplEAjwUMx43uhp6SOlZjY9ekrnNrjzAcMV0PR6KDhvF3XO+62053hcm0sdtus9vddzuMARLSvuOOmz11m9XY0nW3O7cmoAA6Q6O3+OlM'
        b'mAsxmgL5qM4dpzsG3rACuysHOKqFnmmyiG34wAaju1M6JlOtG5BxKy9vfiAmxLUbFfbAIyNDjbSbc7+nUWE17up6VDq31g4ZJgeOiq4zWgzwj9OADuMktrGo5DYk6WZc'
        b'Qkwml8NtEa1LTaY9HWgyD6MT6QfY/9i3h7m/H+b+3cLMJz8caC2wNJvd7mDgHOkC6t5+qNue+/Zg9/GD3acrsJkwwsU+FGo1i19kMp3uAuAAJLR3pBGKQFiLUHum3Aar'
        b'i0JLN8QBrrbrBfxqfrUgwyw0UugF6arKBz+lJ14VjBE0DVI7o7GvokBC61NUKKH1KpfV2G0W6jFca7bWiZbupNNgk0mq02S6xMtEReqxlqfnzoO/WdnL32vfk91LpFQO'
        b'lDhTCJsMP0XoXvJkAeOqTabbXYp/7NajtBfc1l7Nw9qrtztNpntdtsdudd9eFGvPJbXF+WmevEu6t918dNc6KFcm00tdts5uPTLfZ/283ENL1joQYL7TZUvs1iO3VN1j'
        b'S0FsAZuhwlcD2ooIXN30pqMRdWF/bbe+6SpZjBwRLtBcmesIJwqigjKZvgDIaro6qCbIN/PHpPUirxI2GMqCD2mlD4axLWNrXbWu3r5M2nQenSK5Xrjr6+00BtEDPiXJ'
        b'y42GFdPsmzKvZonbXOeyrrQELiavGmqqtrpAJ7Ysr/epf92aI2AkWOMm0+tt5EPD4qWGBY6I/JDEm+iw6JM7+Bc6Fsn1OW12F41xRj+e7Q1rb9OGfFWVpdJlXSpF1QaS'
        b'azM7XSbJWutVmNwOm2MPre0ATaiFW/JU9OOoV+NX+kOYeVTanGWmd6b8OmiwbInaHKPJ8zQ5TRNqOnS8QJNzNLlAk0s0uUITJn3doskdmtylCWPCL9LkZZp8hyaEJq/T'
        b'hG77Od6kyfdo8hZN3qbJT3xjrI/8/+P52MGvxA7J23TbgfpaaASFUsEruIBfoItR0d24NyqpD+7gOOreGKPjuWBVWIhW0AgahUYRppL+awWtUsP+aEmYhv0GQan8ywzA'
        b'mYYkJ9lCWpOXxDK3R00M7x79dCeHR4X83/leB4dHXxzYKgWLSqthwedYVFoagk4OPsci0IpBLK9mweiULBidWg4+p2X5UJYPYsHolCwYnVoOPhfB8r1YPoQFo1OyYHRq'
        b'OfhcFMtHs3woC0anZMHo1Mx9UinGsHw/lqcB5/qz/ACWj4D8QJYfxPI0wNxglh/C8jTAnI7lh7J8bxaATskC0NF8FAtAp2QB6Gg+GvIjWT6O5ftAPp7l9Szfl4WbU7Jw'
        b'czQfA3kDyyeyfD/IJ7F8Msv3h3wKy49m+QGQH8PyqSw/EPJjWf4Jlh8E+XEsP57lJVdL6jhJXS2pyyQq0zFnSVQ2lLlJorJh4jTGW9K94fSEzey246y/u9xxj8l34jPg'
        b'ITkSXofHqLMG8xypNNdRmlhhkf3jXFa2w+Pz72Ch1nyec9TFQ9pKsbTf9JG3mtq7dFAFKuDsbTmlwGbpkJBor3RThcBfc7va7A5fhVaXZFOTXvXt3GSk58/OlGso78at'
        b'r10mp0r2TzHrKpgFEKqTNtwCzwYbpCZ9fZVdN10OCx2QdvWZncxTlALHvEaWQk1mm03nphKWbQXlOe0OHbd7uR23pQofpTbUPu6s4Cjrc0RQ9tcPNfNuzhHjY4EuZvo8'
        b'xq0WRGB3JilVsFTJUhVL1SzVsDSIpcEgfNL/ISynZWkoS8NEAdJwdh3B0l4sjWRpb5ZGsTSapX1Y2pelMSztx9L+LB3A0oEsHcTSwSwdAoxbMOlEDtKhrGRYA390+DGU'
        b'iZ5eAAKvYrWyQXEU1ugxbjvnBNrToOiLVivq+rNSFS11jBDVwOBjGxTUorha4RoJDF/RyMPzk11xoqZBIZl+XfG0vEHZKHBoySfN0LtFYc0ce25BLloPEDDtOKjA8X0q'
        b'IDwhLYBOy6XnBcE4RJaXM3l5k+mB0hTrjHU+iO1YSY2Z+lS1uWVJdle9V1sMnN9aK7s/qqS9RykkqmCyil6lyW1xOWjMGukMhDdcisXuPxHnyKS8iX4K10Gt5Q66iyPF'
        b'USljkkH7A5Ug/UmbzFBjvdsBUq0FmmBSgZoZ411mr8pU66xmTS+mhwyVJov0jx05DPW9xr53Bi9V1tANUhah1+xyO0E0cVioldxso4GX6qrsADEbV2uVtZI5QYM0ItEM'
        b'/21zrautQ94ok81eaba1P/dP4yPX0G1dJ8DH1ixUw/5LcZO9A00dhhxkWViP8rNKuK51eoMBSIfLSV27mVzlVcO80DnxhqX7ZkaaCbXT4qI39CrJ8YAaHbyqxcvo1+ED'
        b'oic0oIfHbmCz+Rsq95UxuS+CuVZ0DNyl6VTSzS8v/Y9gViEt+6wyTSO5lX07jMBjh6EGofMDhLr3I40EfUdyb43p2JTfz3XybOamULe47dCmQYq/4LLLh12pk6EIpNpa'
        b'tQIIcABhfAy3V6bjZPQEbLQP2Acj20fxonv6tXZX2wlbFtX0MY75OrJ7ajfG32774F2dm6VhVB+jVWNPrQ5o39vAwF0dmpVjmv4fxewa7G9X30XMrv+iaTbBJT01PdTf'
        b'9C/SdVIkW6e7Qj68wVzaaXuyZ40cGqpHuJiwJFXE9iWpbFMPr1G5hIXH6SLYVJKupK2symqhDcqCAtQOD7T53fhpv1M3Sh6nUQa4tLrYf19or1FsB3KUFF9r1GPgx/ye'
        b'BiveP1hjO4dH6QY/06fPTU+GZMZjHYF3fNgTHAl+OCa3O4dPI49YKtqfyO8IT0bxjMzkzBnTZz8iPLKN96Oe4Enyw1PMZj+AZcveWD43/Q5uQkm6TBYiRXKKsi0zr3DK'
        b'h9B1dZZqM9W9HwvKj3uCcowfylE+VPe5OgUALHNmXXzJnLlljxGVD1r/pKfWn/C3HseIu92+mEq00lF6EHTr6+30kBSIRG7p8P1joctfemp6gr/p8Nn+My+P3oTcu097'
        b'amJSewpWC2vWXG0JQMP6mhVO6u6mK0rPKYA1bnuM/p3lHH/tqfGp7Ye2rVGbvbp9m7p4Y/GMrMdbiX/rqel0f9OSq1+dmOiyJ8K/Nsati5/x6G1KYTgcf++pzUx/m4O6'
        b'DO+gi89/9AblhfNZTw3O9Dc4VPJnBJGwjp4PkZeKFHajqLS46PEa/bynRnP9jUYyGsckZPmoy2ON5T96aiW/jSZ0pFxUrqYeNvQ6fnphoTGnYObsGfMelW7K2PPPnlov'
        b'8rf+146tt5f2k3RZQCNmWgCeOiYXOv2qd1fR54F4zc3Jmk1jyBt0M+dkGHRFxTn56QWFs9MNOtoH44z5egPz2MmiKFMj19ldbZmF+bCCpOqy0vNz8uZL1yWl0wOzs4vT'
        b'C0rSM2bnFLJnoQVmDlhmdVK31nqbmQa8kkKAPM4Q/qunIZzjH8JhAURdUo0kxDSzxWh2wig+Tqtf9NTqfH+r4zpOnKTBJenS2w6o5RRkFcIUZBbMpJSeotJjQfK/PUGy'
        b'wA9J39mM20tqI0yhSHHH/hiCIqyVr3pqytRG4+XwLOzEo9SQpc0MFKiLPA6D+bKnxivaE702Ykf9vHXUdtUFU/F5lLAtkDlyg84C5vYWw7YHmT9V/UB6LZ2JpVse8Kdo'
        b'hNREn1cyNzklfdPE0qMqSNXHOC5gmh5MKpZ8oakFyy/jSCJXmy2ta5EsSa9x/Jl2czFNOoSTZjYIGsnAUYvYrmpbzOkO+0Qh9AtzcpUWwbfZCHpuDPsgFHXHXDmgo8IZ'
        b'8E73M0WtaaLP82+21GRX00S3JuxC2x5VJ/XW7w3T7RnJGHmOHGF0W/cYotu41W37cdD/r2lfFdQo0aW7m0Y2WJjot9Jkxw9qFugKGOnB7vsdFQCMFOdX9LmcMVOXDxql'
        b'pId0431ns9SZTMs6QNOFkYE9V6Af3tVWFTN+sM0lb1gHw9WTfsxpQxqbD1+8oe3tVirZbKWWOTf7HrFXJZuslJLFSsEMVgpqr2LRR7zadsYqlWyrUjC7U1gHq1RIoFFK'
        b'JVuzNG3GLMmQFNbeWOUYzsno44ilV3GcPIiPFMrN8UtIfkQtQ3QvSyMoQiLHPGbcDHV38TT+y3gc3f1XPWo8D22wRtAo3dT1PC29NCQpfmlovVafS7YkFOQlUQ91+vmC'
        b'UTVKfHmw0GUYR/rjXI4C969Evgmx7ygKosL/HUWlfK1i31SUrtWiWtTAsxoPX8VJ308sC5LCdJQFs+i5PA3XAaUh7IlwMQKutWIvMRKeCBV7M5IR5e3dAdnzrKCjKwIA'
        b'VQSSAIqSlAybmL+GiaO70Ca+mgYoEET/oWkF0wi8Qf5vHsNlrV002+jX7IZ1tGLSFk2BuyZOnztHEse2aX2VaHx1dKRtdHd3reD3m5I/rzewi3Ye7zw8sznQL4V1H5LV'
        b'by7ssrVv8dE6R1pP7Xl87T2OiDKppxqbu63RP+nUI8Ln99FG60fQWid3VzUlFZsD2E13k9E1le/J7QM61NZqezbLaFNrQKsdWarcKqPmj8BSax7OUrc/vI8yW+14AsDv'
        b'WEOjFvo8ppyRLmha9uln3l2LBedYuGbeUeyaXikWC47JLqW0TQZ51VE1dfrjAs45JAaKvbU0eEBFWzyGuA6QxrV/XLRbpOPx0tkBFibGd/KO8QgQig4ieYEyNuWYQq+m'
        b'0oS5ldAZAoZWXw/Ktu/QQEhAE+zRbvyyBLMo7hQCjgpoZP9reoSlC/bMhhne6R6LgmUsanPoaZvTDhhEP/18MGBO+3XVWNcimd8PM4qtF4mWN6BM1OhbN0JBJwHY/xKV'
        b'DSgdfVpLT3JQiWYHv4R6cktfyYSxGkVHt0G6puvCy7k6YmQ4JEf9JCmxK9hddpfZBoSJ7j85p8IFpff22vqpes4rON21XUpKSvbWkYeNC3uqQB/WUUpq875hCNOGK20C'
        b'BZMvMjh5BhxZfiGjhygoE+Gh1YI84MCKVdIHDzUC9TuhfiUscvCsEktIZ8ZMrpFNhqRFizmUSS6o8/Bm4unEovvI/53Pcu1YNEws+xUOKssE6lpCHUvolw3FYMqA6TcM'
        b'xTDKcMVeB8PK6CeOlcCMI8XewICV7IythkbE8kR6+lWpxSgxGspVFjWLfiV9FlktxtBrsZ/YnzmgqMUBLD+Q5YMhP4jlB7N8COSHsLyO5bWQH8ryw1g+FPLDWX4Ey4dB'
        b'PpblR7J8uARRlSDGifEAS4RFXYWsyBLRiE5wW7myCLgfCT3Qi6Pgbi/oDScmiAa4jmTXiWISXPcWJ8oxv2iskbbvQIZBXyNYb3t7ojzRnj6evp6YqmgWYyuoLGqXelcf'
        b'cUwrJ6bRVmBEBBZpi8Ydi6bfTBTHwb1JrJ3x4gRW3kdMZet4sldLsdDnFuHlirxcoV7p5WdO9/I5M7z8jBL4P9vLZ2R7hekzC7xCptHoFWZOL/IKOSVwlV0MSUZ2llco'
        b'KISrojx4pLgQkpIZ9EaZ0bGUEaSZOUX6MC8/faaXzzQ6cilt43Og7uxiL5+X4+ULCr18UZ6XL4b/JTMcBeyBjDJ4oBSAyWm36H0x15n3g/y1AymMl8IfcV3xSBHXJZmh'
        b'i4+2do4Qrihw0+3z8XPwCboWXGRTYRJpzacxTNuiltKYoQlJOeQU9rDTinmGnPxZ2bBMculZT/r11qlkfTi+noFvWk98vVXhpKvrws2jH5d/VB5viY+MN2ebbVW2CoN5'
        b'wSt5b/3kO9e3j967LlVANSWqv6e8rhfYKVVyEO/tHYLPGrKlAAumbB71IncFfAG34DvSCdC1aGAyuUjoZ7qgaRqG4AC/HG/Ah6Ua7hJPVeCXpM34vFr6lLSTXPedW3z4'
        b'djXvI9X+c5PS7wTqtLgyKhCz2n+gWdm2Xe5QUDrV5fdmgXCxJ+L8j/lbvkppFg2D4j8PKf3+sIcvDXQJT6UmYNYpAO0/3alhiBUsfxZdWo1SHKC2T3dqmoMA2YIA2TQM'
        b'2YIYgmnWBJUEXHf3iXTaz85fLxxYwL4/iJ/HLRVGGr6QXMYnkqV4uYmJSTQ6LgswS5GgtGgZbsrGZwREttaHkO34OexhcXbJdnLGZvQFP6RoWJhIo9qy6LqkFYj4thL8'
        b'knFuPNk0VwMorUD4Dr4UEkpOD2Zny38QoUba7J+oka7c8IesGiR9LfAEPpLlDA3lG/rKR8vHzmVPHx6oQREpN2lUXpveOgW56cexg2aSc+1C47Kj1aeC2g6aq9H8EvUK'
        b'ciSMRakhjXaTMSffaCCteg6FFBTW8rCWXk5mCiL9Jrs6IZueRic7U1NScFO5EQ3DN4Risha/1JfcYJ9AXJ5KTiUU0MPIrfml/qPsybPikxLjSXPyqJww/Fw+h+x6DbmG'
        b'X1ZIza7Hl8ghI2nJyUtWkWfxDqTqy4cZrAxZ3ezM9I3UsAQ62okqsqsaqfBdfhzZEuOm1okhKyckSBPRRWv5s+LJRnyOhYAvipfgwhuyBTQYbwjFt/DdCDas44wrnEvJ'
        b'VUWEAXF4HwLm2prrTqedPjGaxvknrXEh8jcs59bDg7PjYQJbDIb8UimEv3SGvy3QJTkhaOG9i2SDm4Vb2bvcKUW7X002JOjJ5rxEFeo9UyCHyLWn3FTAMJLzYW3DxvBE'
        b'+rxAQE9oIzzezOO1oxC+gV8OecI4xE0lzGm1NWTnLLhYiRbMzscXyHo3pc3L8W58C6SEK8uWTiEech1vWkauulQodACP9y3OdVMRh7wcVu2E0jmkEW+nnzaIz02E2QeC'
        b'yZorjm+DSYXwTnI7GE3BZ9iXFvAGsi0ugY4DjEtLMmBzfDwQxObkglL/dw3UgwDD8Fp8NgjmbL17GG3xXAk+HEJukutOGhmndZlDu4TcRHi/E/VNFXCTWOmm4YJLTaSR'
        b'tNCvsPSqSEyCoVWiSLxbwBfxuicZwifXKpBmhMCjaeXaI3kuaXmsxsdL2bc0yTa0CJ8EmeiS1vqD94ycE8Qk9NuYnaXFxuLGaRGHBqsip365I/nr73OT18e9kfvPqnct'
        b'w84Wh8TP2dn6oxfe2To8ZdW2P4x2oAGfnf3en9J/8G9XofBEULZN7F/FmwXTtKL1vT4cuzP+Y2/BkDe3XSju9eq44OtrxBFF/e7ceDN2lVBz6fwXmz75sfk3If8eeHXm'
        b'8X+stKaPe2F33ph3asqHRx6ZOO7nx194p/eN32b+tf7TfvMaN36x590Fn/3D2j93w+AHWRdjlZZ3m2unrVNph+3I+Ox1b5//x953gEV1pm2fOTMMZWgiYlfsDB0b9grS'
        b'QSl2BaSJIm0odkHpTZEi2CsKooII2NDkeVLMpuymJyabspuYbDbV1DXF/y0zw4AzarLffv9//deGCAPnnPe8/X3qfRt91PWnmB9febojN/bZbdcznt36SfWrH1vWdpj5'
        b'DnupoSX9zEtL3xllha+8WZsbM/KH9heMvp3wg8zo5IQ3nkiwqPi2ck28n+P61wcG3Ck4afnSy0/+K+jcxQ1e7zbeGbfjvW3ZLdvXRX3+zYZnFkUUbu27471x793autCp'
        b'YFLFD9u3D/72/DOnD5pG/FY05BnF3rJ9U6Kvj3x644uRCReubTr7ddaiD4cue63oK8W/+iye/sEG74L7kvgGh8P5134ynnu8IkxqrRzF4AXmbINcdlTCSSsNHBE/K8Px'
        b'PD8Lj2MNQ2/W8E0pyF5wBE6IeArbHTir5c3lzj1ZfChAge8iE0t/DhtxbIUrlGZbWpilQzN0YLsKOzIs5IJtmjTMawaDcoAr3lhCwYKwGS5SwKC5Y+AsA4rY6m6tQ1Il'
        b'WaiCA1jpxNkyL8tIJSgDaZkSi1jVzu+gNTsBzX6sZlZwch2UWmVhRyrZ/sgrFavgUn9x7Sq8xKAebMkCr+JYF9ABdZwGQ8ZZLnBvtC8jqdAlqFgDbauhYBzDN8JjE7Eg'
        b'wDVIjmemCeImyYw0GcM3snIHsjKwhGwQpNKyqRI4ZQ+t81ezh/yVaxixFlwXGLEW5iVk0JNgkAKvqrLM0zKx0wpKoMzKxHiwhRm2WGWRFYgd2Wmk8kEyOVzpk8K6RbYc'
        b'u5xcsDzQQ6KcKMiXkY5zJb3aj20rHTIs9YVzFK1ilyBukyyYPoYRgxERq3gkZdUohWbfoCwsA3LGufoHUU7Wdln2RsjliBK1uD+Bk2/sJpt+IBF95uBuOC8yYtwuzuFR'
        b'i1W+aiLTIPX6twuUkd2szAI6pBxa69q2CCh1o9PLCGq8BHmUOHIg1LKRCcWqpeSaevcyEhQhcN5IxBps2ZBBBRhoCfVV05yF0JOYvIMckHJsxIPCcDxFX5SH5RwrqwOr'
        b'Z/WkRMMiqCAnvpcqi1UkAlvNKMQX6S7JZjgsyP3E/li/gyF6QC6WLWXA4y6uwT5QHxjCyGolwiA8KEvDw9PZmHonWFHGU+35YRnjGCYNGjCRSZNb4exoykXiQiSIACmZ'
        b'hSXmgoinTbGOXZbCCbK3l4b4O/sRgWA8XBBMpohroAzyOcJ7O94QNJehSM396uciCo4ORp5wEHNhpzfndbsORRQNPiTYGYrd1Hu5ERT2JT3SaWQ0H/ax5bYBLsxl1ekP'
        b'NWqgFhnZm89LybA3rMigOvNkLPKk66KHnA7FsNutpwrrJIfGAAHKR5nBkUlwjoGbzIkN7PVoJezXPA6NWBSolAuBgjFchCvZjIM3rT8RtXQoeCfBUQ0Lb28OXjIhz7L5'
        b'tVniwacHaEh75URZlvaBfXgzHo/qF7//53llmV2BifGpD4rxM80kJpRKVpRJBlBwVPLTTjJANKeQKIxy1lxiLVqT62aSQTTP9r6J1IYl/pmLZlIiiItynQhW6p+T6/zG'
        b'7Mv9eonk3LDMqtdopk6h0oQ0y6jZLZ3Ok3RPqh0qYqIztNHJclXM2rgNcb1hVowfozMaTdLXStSFpjP6SlYIexE9tLkdPVGi22OdBtSP5x/CTqu/rb+HldU4Ut1Kgwiu'
        b'WrtVz5f9Lhs6i+bc8DB79z2tq9qBEalosjJ47ezV6Cc94PB/X8guaasiUh1iFfkQup5ftRVx1heUlajqrtvv5hpVB9cwx7Wh91Ptjb9/WDiLxqKxWH+Ye5c7L2iwfGZG'
        b'Sny8wbdKtW9lZK/kbhdyuz3ND+iOC6M1YfHVf6ga6cMfNv5ybQUcWZxEYrw6MGIDDUchvR6XTBNcYv9wF5hH6qxtg9Uw1VaDRW3RGI0EihqnDXD8Q9zDZQ8bcHPtK8cZ'
        b'hkju+WKd97KNVosYSDNWtejz3JIg0KSbbZLNNlsFZkmQMOuBsF0SpvPZkCVBYwrvjShnmNV2CqtBvOQPcNpSPONMiR6kQvpfD26jnrEgKnvV2pTMpFhGbxuXzpDM7aMT'
        b'omkEid6ytARR85Piomlklb0Xy6ihA62G3WWBiWpQcnVMUqJ+2F41XnlUVHh6ZlxUFCffjbN3XJ+SnJESQwl5He2TEtekR5PCaeyZBuDXIMFhxgOrnkLzq0MSOJQhj2nb'
        b'pBMq9mjg9qioBdFJKlLDB0EEWSqY0Os/yQPDLg1OfCsfJCoqL3tdtvpn1K01JvEfJEmEiOdNGiSv3klTSrh0eMkH9+gKIrM9NaII3sRW3M3tdZLeDiZZfEIcg037lnmY'
        b'dvT6GrZ5dI8DSBWTFMn6t9trQgvQocrlTqRujtytpE3W5KUqmlfQ65TNEe6aGzxnM73J/YFEq2vpZaYlWhU1pF3z0kpcRNxvI3JgcQhVsIiUXRXA4FyxBTst3I0m/4cY'
        b'dvlOo8fmrPW16dqcKZsKka4POuoKmLTy1EJTHOjo7wxN4dzmRP8QEugXtAVuSgQ4C8WKqdAVnBjh8oKgojJMW7/yf0a52nwW9cIaBzvH6EBmaf486tOo5PjPo0oS/OM+'
        b'iuZzpNbBxC1wuFLKhFt/OIK5vV9ORdtZ2NhbujXCgxzkthVLByrwUJp+KOALWCUwIXhDFFRpJh9ekuoKwnhzgNFjGaLJVFSpp6Kdvqk4gjo/H2M6kkK43CnTIREwTGqo'
        b'wQLbqp2x28mMHWRwxn5q2DDNZixeXxqjf8K24+mHzFinYDpjWwdbzICCEUqRpX9jjfM2OpWJopcvEWRWEqJUtbow+5R8EZ6jz8gGkQsTJNAGTdMTNz57SVBNJFe3DXxy'
        b'fYJvTCCZG+s+PBO3NmFtQlKCf0xwdHC05O7A9QPWDQhb+knbPnejCakNEuFpR9NIcyeNa1XXam8Y4UDb80zn0DtgduZm1rLNdvoHjA+R+JCB0Tmxd5IRsTI4It9aG5bV'
        b'Dbz9P0AQ/zt2A7Knn3q+S6KiAKAT3rz2T7JyX1izNt6crVlbEC3FDyb9TPZ15jmG3bGPpQBPhk65WgGePP6BsewVF8IGTe+G7/CAd4UFiHTv7wao0GmpIwwO0YcPoUXX'
        b'+77/cVnH4PA8eOTKgsMTrwz5h0xF/zz0/YCAaDIyL5CTo+2oUuJ4sl+3PPnAccpc94ZPU6cHdEceD2P49KTljTbYre8ZPj0NvOk/0q8Jj+d4JdM+dvlRIxU1hc3a4ukU'
        b'/SkRZlY+cWnPsXrqHLUQRv30xFbpN+vOkwOLijvbLNcFQQOWOlMTk2yOBNrjMYdZheBqX4/HswrRFQGt2WRRQNEMDnt/dU0cA7DFA0ODXOSCCV4ToXJTmIEBHfPQ1eL6'
        b'oDGAx/QaHFBa3jiDA/rO7xjQ7uhh4QHf5xBN51PuZzX/qznTUTQxCGJhHyb49IhEKDQqHMh8ooMKBxcOiR+i9YsqHtsv+sBcoNE5tg/MBedgdorZwaH+AVi6cB311zFf'
        b'neUo7qujUsVMzMHLinRsXzYI262oh4d5nazhpIhXx0xh7i7VcGhnbidfMqQh0Kz1O03vo9fzhAUbFdBuZKSUswoshzILFXUa1Y+gflYByoQhjNcCyq2mYFumfOUi8vcj'
        b'AlRCLdZxx2khHrVUYIdR/4nUnSjAMVt3flofh2MjVRkS2A8HyW9FAhRA1yZe2nkjbFCoZLg7mly5IEAd7F/PSoO24X1V2eIU3EUN+QKUJOIF5pX6abwx7buNcx2iknLi'
        b'rQRO/tGMN+KoI04GFV6U3EGAWriGF9lLnHHXFNaWC77qtthCIeNUHQf1sayTevnksCUjHS+F+VoucaJeAO6a2wN1pttccCdrk+XGYRNwzwRS38vuMkFCegJzjFcytlQz'
        b'B9ITOi5huAQ7fRlYDXVSL1yCNRP8w4yFCKyTk9HDmsw+tI8OTVw2QXAmI+cheMBuKGedsBXy8QpWSfEodgqCm+C2Ca8k/XT//n2frTJKt5I61C8qyadvjMA8qcP9QwK0'
        b'78EiX8qiTn7zj3DAYlKBMAcl7l7i60elrLIgJl5Ba/9Q2jZ5ssUqNzzNSnHBAqymwR66t9JZRMUytxB1D6nR1NcB93PTCXQWrpnjRZshmWQohcVEdjtqQR6ptIAcdxMj'
        b'zInAw3KsCLdYYDPIZEYoXIMuPIwXvBM2msb3TzPD6/JsEygxDTGHFtyFJ6E2wR27tiiHY9F0V9wvh33zldA2ayLWD4A6vAC7MyMEBmfejrlGRHzPhYLNFoKHiRRaIuDi'
        b'cqyRE4G7EGocIQ+7cDdUhA9O3A5nMGcwdK0bORg6qfUeOuK3YJ7Uw4HUpHw4tnr1DYrGHLZzsKn2rNtgyURRSH3KLmrbktQpQiYVgmAvNlAqmQeJeLuds5SLV03Eex47'
        b'FXAOT8R4DGBl5k/1FfYIQtRfNkStM126UsikWHi0lnm0GfWmgr05+bB49XrYSyb1VTwm8YCdeGr6BDIkVVHQjs24P2IcnlhO6pzTLxx2xkFREJYkkCly2XgtXLfeNBKr'
        b'2Q4A+0Ko24/Xk2hLdbp19XXxN7LpRyN2oFFJ/icLDM+aYqcl7AlXSpgbGdrhBl6kM4HMx2asccMKP2eyY5Cx7m8ic8dCGWcXLloIJQEacuFzi3ryC+snFy5RmieSpuRk'
        b'TqAFVHlDl9bLnYB79Tu6tW5ubE0mNWQ7TumsWKpBSAQRKiTy8fPHYWUmBUOYG7nayReavVzp7GWLwc3fzyWUR5M8EL/gSxTMVLoLLAx1WSwKm8KtNm3YkhkuMHfbQV8e'
        b'VuC3SB1YolZOfQNDWCtdF5lkYcciX/+gYGeX4AhOyEy2Ek0oA92ZZ8M+ActC+8CptVDLZsHLA0WqcNv3E6MCm6Q7yPnKwzRuumQHaLxQJtgijpBBEVSbsUmSnA0dYSHK'
        b'IE6nErFET6CMQCZ9E+SQau/FspX2ZNAvw0nfEXDTF094jJgAF2QCGdFcG6jHwz6Z9rTzL5KVWE92zjYrUxO8aIVtGSK0pmUSeVslDZk8nG12PtgIdWFk3xoq+kvJZtcs'
        b'YHPCSEbSNHKtaYDShWnqwc7LEv0iHHrnNqyyN4GdUGvMYg7Iq85jYRiUh2M5JU0ycpRgHR6F/Wlk96GOvniypCsUWZbkeMdaYTqewrPYBRcYazTZDG9gDanrJRVcd8A2'
        b'Y0HEcxKXsVHKPmw6hG6ibttAyQZsEiRTBKyIx2JOKN1BdG8WJwRnw7n7T7FcxPOmkMepntqxNZH6qOEA7NP4qeGAFIpZ8McKL+hkLl/q701OcHO14WfO8dgYFj9BzsBm'
        b'yjMwTALHHSCXvTKO7DXVfOasxdNOSmiSCebW0n6RWJjJDAhFMcFkziuZ7cAZd272o07LAEZYMBZyjOJXJ7IOs4frKdpNnfJk14lYBwehBq70553Skh7nRBfLBRlzJgrm'
        b'CVJyqOBl1iUWzv0C/JyhMUnDr9AHGnm4T+0MKyx1WT06mLlK5avEfmT7uciGO2uUF5a6+kMpXA6SCrLJEmhMwDz+2GGsDCSLnWxrF+k10uQT0BbErx1diZWU75scH+1B'
        b'asbvtADWXKKfH8QqJ/WiJjOYrmojYQRUGUnJsUq271Ie8dKFbXCZ7ATFIUSYCKb+bTdtL+l0UTDkGuMeuAklfN3Ukml/ivr6lWR3Mp0qTh4Mp3B3WmLfSROMVDuI4DRu'
        b'2BfeYdeS35ljfX36MGWJTdwKt9COvs/vnlF5u2a2vXeJvd/Ak8vPHBWePCpb4vOESWVUvzk5f7J1vTXc99CfTVaefKn/T9KVcV+OHpef0dk2oa1zi0/whEV+e0+uizB5'
        b'o35/5KjnqhKeqrkV6TrjlYPxmx38/7Vsb6Sv13a7PUc/KB1UPC/3/uy7ZePfe+35C8uWlC//KHbGqA9VG2wnNThGDtgNyl8+fGfie8/UbLOzrUl3vPvVEys+T/mmz8/L'
        b'lv6pye+L5Xb715z4MDMlo9+ilQGfHT3+51V/37d3Z+NLO+Z3xXy3a738dPMXttv7rdj9y7CyVQfeTv9hyofbvgwKb3xj/M0PXMe99Pz8ifLsP7fu3d1kUmvqGbjwT+0H'
        b'd8xpWD+hrVp6VvjZZZz3nK648a++5iT2DU9zaQp2MXP/fNi92o/X/DX8HyGTMiI/nJQacfWNQwWWXZL9Uy6Vf2pX8sPNd0M+eiXIsmLDoJd/87/S9/2Rqg/GexyfXtF/'
        b'+pIfkrKfsJr63g8H46+trzmSkry27XnbN5Zcr/ri7ZkDVm2+JE6eXXi39enJt5c99WuTj0979c5Ra1fH7OzzVe3i+8XT7a5t9YmZ8t0/Np6qfbn5qwGjnr216dblT+I+'
        b'amnAuhPrcv4xw31+6UspdvOnpZ2embNkzfsDxh5z3fEX5aG3f3zStKGfrcWrc2Z1Xdz2Cyw7kjR9yIjfYt4ceXBo8swFP73vNsZq4Tc5h9+4+Jr3p5u3TY5Y7zZ8r8P+'
        b'z8NOu9X+5uz1In7ex/q5YU1rs+XThx56u3jIh57x78sW3vC4/HfTGa7fmI21WXXy7VbTKxv2D7n2VVzgn//xdNOKt17wGxNU9OO748+1e95/xuyFIuNTCZWfvRYV6aQM'
        b'fD49aOOIpMLX6xPfajzwadfa4N/E+9nygS67lWN4XMZhskHvVwdmYC2c0gRniFi7AcqXW8+bOFBDuOU/e67vuAwqG24a76PdfhaGusUvYdEt0oARNGQHj2zsGbVjshzz'
        b'eVTFcbxCFoU2QMME2kU4CZ1ZZBnVMZVvFBxyY9vilmSdXXFGILsYRNZsDt0UlZO7t0RsXcSCP7Aqcy6PKJoKlzRBRSKeEjGPk8Nc957qFGDuwflQKBsKkWPzGbMLnIIz'
        b'KidHVyWWEFXPdJnoDC1ksbbF8Kvnce9CJ9cNq+mR4kw2JqgQXcj50cZeOwr3wZ5u9hpZPDQz8prR0MhiTvCqMZ6moSBUZgnpFl/lwvAAGdSQc+DwLCLb091qTVa4kys5'
        b'Xq7yesihWZyQSE4/umuuhhMeTi62cYxBh0UUrVyZ4cFOoNEqFZSbpFngRRUN97My6RXig3uwQAjCdjmRnc7BfhbOocQz/Z26AyGggpyCFXLBxk8KRwfM4TFa+8L7Bmgs'
        b'zyFE52jyIePdBwulUNZvOBvv8dkilLqRYXZh9InGUOkpWIVI1xIx7Qgb7wm4z9QpxJk8nAOnGa8bmVl4Q8ROD7zEioACIlo39xAwyPZ9GYoG4mFO7HaaiHrXyIkxBE9o'
        b'GXkK1Ix2ZO9vcOmOyh4l1Uaa4SkHHmMzCjtoHa9DHovUYWE6cHZIhjMbd9kS/bYJIoPWpOpEnWyam0FFk8lEhSjQxjqxQCePMG2ok+DFRnwsjf+isTekwaf0xd9grjsW'
        b'sdYPhBPZTq5KfzUvEDkxigUrzJGmQBNnFRoRR836QZSF8FxfRkmkSBbxQArUsTk9ZCwN9SXHW0205nST4xE2a8PgIukdJgvs6aMRBchCr+fRdYfxfCyXBchd17qFgfDR'
        b'3JlwOBILuoUBT6G3LLBkeAaX1bCeCuRBLlAxxDVYG+dkhwUyGyc8xUxA9lBJY5Ws4EqfxzQDmcER/0U8Hq4KW9cFBPqR/SdUkubviDcCWPOiIde8B98fuXHXJiiWK83/'
        b'nSAd5ZD/IF7t7//WbcS36oXQyexcH5FvD9i5xlP7rQnjqLFmXEny+yL9J8p/Y/+k5iLNN6JQdxygzo7cS+8UJeJ9mZQC4FHkdJlETlluGBSyJf9HyqWfbMgnGm5kwxgI'
        b'rWnYESnDXM08SH6SK2b3ZaK5OpDJkv4mpQFMZqKJSNF26Vc3Oq9IShHZT/4ll4hfyu0oz465ukSeoai1p/XqCm4N5JFLPKqIZZw5sTAiFrQUt7E7sKE7iavbndHvf21E'
        b'lSY6NZypqWF6gbZSTtrgJ2aCzCe/Oho0Qb417yHMig/rMqWEZbQFP8LbSv2tEoZI/Pu8rVIWKiH78G1RT7DC3PgMyp4YnZTEsFd1eIpJJRNp7aKTekCychiv2FiOUxht'
        b'nxyX/UChPBTGISpq4YYMv+T4qCj7NUkpMeuVrmr4XE34Q6YqLj4zicYgbErJtM+O5pSOsYmUhfFBDmXdSiQmsxvjGbqAOp00TsVzTDl2oj1FgbJPjFU9PmEiBUWYZu/H'
        b'whDI7FQlUoha8h4akhBtH5OpykjZwIvVNs0vNipKSUF0DEZukP7R9Af9mJhsn+XpSqm655FuzKadmbE2OkNb2+7gEL0lqtvGcHNZtBMPwSAFUBTdHl2kydZNSE/JTGXg'
        b'enpLJE3PSIzJTIpO50EmqtS4GC3Wg8regebMO5MuIK9lUCybUsmvcRkxrko2CAaCTGiHZsRpxkU97iwYLbk3M6Z69GNTWK5wKkVc1ldmjwF4BLOkRNDHLGkWzLTQkTRy'
        b'WJ3oQgTcEmo7nwhHuPGcmbWKVNjyQHZETJzAkyPc4HJmED0L8ydgCbMsWgj2JlJqv7ya5o7Vi/HkoGG+fcekbcMLoZAP5+ZD9Yp5fhlwFo9Bi8nMYOeheBCP4UEvuDZ8'
        b'MzRZu8M+T2bzudCPWf7c3SM6Z4ZPMea18YWzsVTZDgqjPMG7aXIN+REQtsNYGLlOhmd9vNmzfx3P7L327vJj0YcXRAqJN8LmiyqaePjtSy1j/tRlscvd1vvD7ed/Pvzi'
        b'V8LAkYq/tBiFJ649nxe7/9bcxqO5d+IUW161f3notmkNEj+H15qnfzp5a58trx795sq0e2d/kZ4esuan7+6EVvb5U3jcL1FFJ1ZtNyt9+tm0c8ve++Rn77rg8kaftcsy'
        b'Fwa6eBytv180avAJswalgkfYF8zF/B5x5laBTJnBwxuYRDHWKIm66c9jFdNp5uK1scx76wn71htyVMHxmXqFFOuBTFReOnO+itpXXRw0FqY+MiLz7JESNaJrOJNDF26D'
        b'Exq9Z8dgrvlkYVU/rprcTF+ojrsXprmxuHsFVDG5Hy8lbGRx99vTBBZ1PxSucLn4oimUqRk1x2EXUwmwE04x8W50bPADuRNGUCEz2TiCBX37JFuTLoJObNKRZLVyLJk1'
        b'zTxevhIuQAm503iS3kByMhWLoVbtiHtkzIgpzf1j65MJL476hJcdwhQmslD4/vvku5SKJlQk6RUdoC2qJ+Gja89z/QGWSpHf0X2+FpFfT9Dz1VXf+ZojvP+Q1EYDNaLR'
        b'pOSYiSTnTA/sBE0CraE4RGmR9LHSZzWRgD/J9ByuYXHJaljVntjtmSp+2Max7Y7szd7z/OaH6eCxGzqh4tYkxqgiY5ISSSmc1lcDRBVPgSVj1rqyO1y96ff57DZDMO86'
        b'par7ZxqLWnTWhi1SGGJVHKtmSnos/QPZ+/XuzWrYeoN1cF0QERjFoOgyU5NSomM1rdd0iN5CKdapFlqOHhvqwF5VZmIGB4/XVkr/ifHIWs2fHx7l/EcfjfjDj/ot/KOP'
        b'zl26/A+/1cvrjz86748+utR7/B9/dEKUvQG56jEenmggcNQvnhPZcCknLtbZ3lE9/R17RJ/2DI9lIXL6xRJDQa8L0qMZonf3HP498a1LqCDLd4WsCa7uPVYLi8vlOLp8'
        b'OZEXZiVG/7GemhceoacK3bTfdI/h9eDLLTH2EbKXTNChpdXKXn05q7ePsVwwX1otEeyjzAfEJAnMs50mcVQpROoeWGouQL3rFmaxzyBHXSvs7INt7u7uRoLoR22jnXA1'
        b'kxYMV3wsnIJdLakhFGolAdgZyf6+cbG3U7C/EZSK5O87JVOwYixz0PhEWDsF+2HpZnp/kWSGe6hSxoRBuILHJ2OtN/Nv4UUjQTpIMtMzjTlOYuDsspVIs3dbMqh3XcQa'
        b'yQjIg5OsyFHQMkM1Pp36AyUpAnROn8YewnI4Co1peFKFHVbkVBOxQeIIzaTeLGahmjx/ASkuDXTBLjfBzX4R86j0w8blNAKBpawXQZsAZUPwpFLkfqTLQbDHCJp7VBIq'
        b'VrKLLnhmCB527lXL6k2sWLixdi7UrdGtC+6fxariGeNJqg+Vwer6w368ouTcOdC+1cQBd/V4XYozd4Q1EBnjQhRc6vm+kdjGn8zHg5CLJTaKLFMy+FJTiRvpWhZjgS2w'
        b'H3YGuCksKL6M1FkyewSWsYf6w4W5MXCduu0UlhJBai6Z7QhnMilK9xpoiA5gWfostpfmOBMBmMaL7N1KROsyzIPrpE8PhpNfqvE6nsS9RLau3gqn4bqNEdasMbIg34JI'
        b'tcpm2PclYqKNFZwhle9M/OGbKFFF8T/PfhcQ8ZfpwU+5W8s/qE/7oXKbfM+eT89MMer0RcmC0mr7/qPm2FoamTyXYVttG/zsCOt+kyYZf2Ab/otfx1s1B77xvPnsxVFL'
        b'wlv33q06uHD+ourkW8HSxtfuOi96wafJa9UXL6wvmPRKa/B7Fz8auWTZ8xbGHU6HGvosXvDD358YnOv30cTExrTKVyb6pp6r/uhmYWPWJzcXfnxm1rWB066N2eI9fve7'
        b'6X5dL768rfDFrCTJzzkvGn/7Y5dr2r3+r8P2v6xI/rZ68TuveR9Z/vrdeT8YR34VuHL+22ZrW3d4fme+uWXH9O+GbJ7y6feVdn89cC35aPn0Bp/tT0TWVkf+Jt3jsOpP'
        b'K/KVttzaW4J7NwZgCV7sznpkBn5szGRmPWyDPVAiButm58IBOLGOm/jb4SgedIqy00nxM3eWGuON7cwrYTnbj4r2lzdwyX74bCYpT4IbcHMkHGR4AUaCDPIkuCsbD/AX'
        b'Xg1cPw5aeqbWtkLDBHY1MRXPaKT2CXBKLbaHYg5XNcrgCDY4UcO/n8tErBUFEywVyWwsggKeq3oC6zaqFNhOJkktdR+XCnhGMYBdW4AdQ6A0dRJehxyyILCQrEM4M4dX'
        b'6gyZZgfoVdiF1+TkKpmBlVi2nicvT19DLy3EAlpksYB74SqWMXOxCVyXqJNWI+zUaas0ZTV1GI+nu4gH4KoqyxJa+pNnoUHAA1gCRVwJqU6JUkEZFCV70/rsIarHXCxl'
        b'de0L9ewxrLE1Io+dFsiUL4RqFvk3ibQuhyx3c4UDUYPhvICHUiPYFbwyzkiVlQY3x9F31ZHuWoO1TKmBy1CygVyauJS8CWoFLNkxkylSThOxrM+03roUU6Swys1AfuZD'
        b'Qp9lKiIPM20jSr+2EUW1C2qiZPoG+SdjZlNu8hSZ5qH5Mmf5k2aixiip/UeeIPfeF+9v7tMzgpm8O1gDvcLSKs11pen04h7KCgs+JG0p0yooxdrsx1Ly6cmHaClPPiSq'
        b'+sE6EX2N6iUs6ytY2b8X6NVtWWSIX/BtReT8iNBQ7+D5ft5hHChUC4Z1W5EanZisSYuk2Zq3zXTyBpl9U5sxqpPcubMnaBbD0MqXqJUw1kbeWYP+XzK8p/tQDZFmnq6h'
        b'68vYWkrngsmvcrml0YA51LAuE/8gXqfM2tpatKQEcjLh/uRNJhLboSaSTIZtcCFgVq+8BIkwyGeOXJY4GJseCN81V/9UOUp6UspRrC+O83VQpkb64p8p3pcp+aKfKe4X'
        b'Rf3if+/+bE0hN2P7ss+2sf20n+1i+5PPA9jngbGDYgfHDjmooGR1hfJ4SezQ2GF5JhTys9q4WhKrqDavNqm2oV+xw8uNYz0KKY6YnOi8o2PHMEwsY0byNi5PiHWIVVIS'
        b'O/pctaJajBfJU33JP+tqm0T+mw0pzabatNosXhbrGOtEyhtPMcpoiYWmhRaFNoW28SYM1YuWbMpiZuUshrZPvDzWLdY9z4RCjMqE5QoW/Trhtg1dHPMZ0QXDhIuPS783'
        b'voe0+eANao423ZvuuRLRdVqiKmWaKiOW/Rzv7j5+/DQqAU/bqIqdRheMq7u7B/lHZOsJSultWXBIaNBtma+fj+9tWUSoz8JGyW3Ry5t8N6WvjAwJDlzWKEunBoPbRkzj'
        b'vG3KEYETyUejeKI3q37Paz3oa2Xp1XSV1dBvtXTdyvyCwzhQ5O8sayrZ0nqWlX6UFRjmtXjuvXlrMzJSp7m5ZWdnu6oSN7pQXSCdJsa6xKgTCl1jUja4xca59aqhK9EY'
        b'3Me7kvcpxe7yG0UGTZYeSbEXSQcFhsyfGxhJVIR7Y2ml58/zYzUkPxdGb6LbXCi1HasySKGu7hPJd7Lj0cIaJelBHL5xP62reZhfsE+gd+S8ueHzfR+zKA+yQ1f3aPI9'
        b'z14Pzk9PUanmMd2lZxmBKQlBqgRWkgctSewuiVTwDC3Lqld/3BtkuFH3+untPKWiRyl0uqWf1VP21PRz9K+9CpnKCpmQ3kyvGX65xz2n39HS28axcfHRmUkZrPvZWP7v'
        b'5Tboyxlh6kgYHkhUZBlBozqwD8/KQhMjPe8KLJekfkgwyyUJNBZkDpKd85T7Jjwkl+S2CeWHzSAT23CKFf3y4ciuPTcUV82zhjMRLpFWzCSfVO76BYAc4emHZCM87J2N'
        b'xvzATtRzaq/XHt10ov6D1ik8+IH8BTNNB/sL6vwFQUNlylHb4s20uQlmj5WbIGVjKftwp7EeC6cfzzlO3BynY+fkXEXcG0W36IfYNcM0hML2qYw5gkkxqmkP3uhi32sZ'
        b'2Tt4eSsffhtdho+8Y6q9g6Mqkbq2sjxdJzs+RpF8Zds7zPd99M3qFUxvdrZ/1HsM7y72Dn7hv+sJj4c88bgbBS2id6UNmZDVZjBuL+Lp4GqWKg0DgqEn6WnKH+s9bVLT'
        b'E1PSEzM2cbBhB0d6RlP+L3pKO+q3KjrSs5veQ09SR2pCdqRHoKPStdv7Otl1vKv7NPUt+ovpdtS6s1vVpXb/eTL7My/aUMM4hIW6aXoAKnj/jFMxjAqD3cOcGNN64gmw'
        b'RaYfbkKNB2CwTt2YEtO0jLcPwkZQCAetr16PK57+R64xskJq1WfWVBYnEBedQSeUSkPlpoPCQT3VBkAJqEWWlJMdna4OK9Bh0GC9Yx8WF0fbmpmkww6nt6j5c8O9fUJC'
        b'l0VSqqKQMO9IylITxmqpdelzzjqDncQ3Id4/jFVKDeqiGTeN9qa2Jev3gHfbl5nPgpfQbf517LWnOBqMIWAjlMrXqYoz3vXaYhx56zS3JCbrR0zg+BxEXtUQ+K6NTrb3'
        b'jgg1YCdPtg/LTszYHJeexAYu4yGV5xuigbVEFoxfRnTSJvag4R3O0fCcVQOL8AHpxhuhM189JFrsEe6yMtCiDB4SoYNG3uPZHrgxBnctVtIDPgTSPWqhSqWZvr3K1T8m'
        b'ahLI7vcy8s01cUkpyQm0pEfY2qmEYvqARGUVzK3GxdZwCKsCsAL3SAV3mhdwQuJgtIRZYwOWL+67QhMEQSMgaK4TD4Gg4pIJtsI+lYU31lmIaoxTuBTJIUhzHPE4VYeh'
        b'DDupdRyKZaT0XAvME7F0BJ7IpKYJKR6HvO443PCFLkOhdLEeYFBdUNAgI39RmAS7LDHPfplSZBV1gxoLjWUYj66mxuHohUxi7K9cym3JQ+AQNSdDB57KpAicWJENp3VA'
        b'X7trQRNivKCd5cSkWliEUthXB5fgCAcHLMEyNyxxpmifHMjUhRr69vWV4HXLBTyPYj+2wwFVlh150UWZGqMUSjCPeTZGb5FTzT+qyyEqyXbJep4JZroijOKWalJ9fF39'
        b'g7CYNNjNFHeGYlHgIl9pKBTTtDkaiL1pjAA3ZQqsw+tWiU13PzBSHSVlFEXNGlPuYQZzrL0T4qs+T967vOV7/46dL9rbzI3tGzrG+kKIOXR+a/Jcv/R52e0DN3717f0M'
        b'2c4DcdEmM8wGxLbcWvL8y553O/7UMrO8+IW9jWeWxX3keyXes+/YF42/VB68Oq80Ntrt4on6I+YXWgcO80j7eofnwumNhdPfeT+z0vOtp9dfSf/pXas9DeGvfDbm5+9a'
        b'S351uXr1r3/zP2RXXfHRhUj3W+6mzrOUFsxe6RKFB7BwgJOrCw+JPim6K7CIhy5fh6pYCrU8zZ8adWlUeDHsNhYsQ6Ueq6XcxNqAe1Y6BffppxuKngWt6qD4I5BDJqRu'
        b'FAnui+RhJJehi8WRpEA75gaEzAl2UceRHBjOjNR2UIT7AlyDoFEbE84Cwl3xEK9cC9Zv0o3OgIO4Xx0nn7SchTVPh1zYT+24O+BYN/4gNeRm4SmO73cCT46gd8DOqb3Q'
        b'DDVIhif7s7KcknCXLuJkGl5moJOrsRwu8kiSPXgD9mos7tP6cpt7Zhq/eD4Rm8iL6MK7JBV2DJMGSRZEQDHrglAstqarfdfsQNIHayQeO6J7gFKY/VuWNy1K3hxD6tRW'
        b'G2p/k/JwVwo5IpOY3JeL9KdIo0cYJ7OlKEoGGVCC1HhwakicBIk+a3JSDxC6oIdqYe3DfqcW9gcA6YwiGSafIbSscvKJw9Hpe6GWC9r1MeTf3lBy1GwV5js39LaMMr3e'
        b'llHSV6WxvpBbHtBK41tvG6u5wdOvSfQkv1tpzpJwQZv8ztVHc7UCacGBvwut4q1+Z4q7Ro08o0+NnBsbq+rJcK05RvVY/LQC2IPaaLz9NCoeTovS4pVE6fHqO6vFGS36'
        b'Fg2gfDDetDdbIycrppp6t5CaQXszQy3CP5ZypBZrtXy+j9KPOJ0Xf1YP6W60yj4+KSWaGg/sGbusmj7TUEhNdHIPqrreXL2GatFDadBHpZsRt5FLxBla9tkNPPjTQDQn'
        b'uScxlopz3V3RTfjH22DvwFjoadOYuDYydIGrq+tIpQFBkwdGsMjkaDqbdDiotSVzkk0uAHdf11ue9pluzkz1FFAHbfVk0NRbhkOo9wJv6rfxjgyOCJrnHepsr9FLOM2o'
        b'wUAvFopsmG42JZWHZj+khI36VD0DvK4PKY7+p9UEaQ8/TFHTIsKpZ7Xe0jQk4vp0OnvSK96hwXMDH9Tf9EcvP6ZOp2H/4l2hpV+mE1Y9b+i6IGpwHGPYjooKTkmmO8VD'
        b'wro3ZnS/nZHz0j6KTqKh1HSD0E7d+PSUDaSrYqMNxF8nZXLTWUJiVlyyZuaTpRlLA3wcYlKSVYmku2hJpOMS2V9JLxusGC9G1+Cg1G2mmox6zbq4mAy+H+hXccJCpkx2'
        b'97Dn9Li8PbQOzmpMUXV7mQWArk2yKeotJz4zna01tto5za1BPY+fTNPsw9R6lYacnkaobyJvSUoiiy86nWtX/Gb9e4tKlRKTyAZBq+WlpqdQjnnai6Rr1YNNFgKf9vo7'
        b'U4e60T6Y6HvRqalJiTEs9JAq3Gw96Ubc618789Uc991UsfTQtncg35XO9vTotncIiQhV0sGgR7i9wzzvYAPr0FEnhWCy0vExEhu0cVxztVt9L8qlh8WH9lA2TfQqm8N5'
        b'UD1UrMNOrk8Ox6NcpVyj1iiZfhSvYPrRHDunKPN5WyZyNTMWqiNxv0C5NDRa5lVsXMAUvxlEIm5Sh0QdN2WgLNmx7KlpftjBkFwEwQuPMiQXvOYbzrRTH6JvXSbaKd7I'
        b'7KGgcu0Udg3IDCR3jVyegaVqcgdK+xGuxiQIcHFc7OvsH2FYQ4VzcI2DvVzw7kN0mhYjHsKEh+YwLXUq3FCHMMERW45AcsQJT2zc8Dvfp2HRKXNa5OALzRylQikXprnb'
        b'YssCKxaBNtRxLlGAJyeqw6mw3jszW6AJj10TAxh6j4t/CFWAeQFGeDYL92K+2ZiB0GjWrXXOwVw8SC4ct4F8OBkOR2MXQfG87TRYC86SrxPkZ8H6jbAHGuatWQ0l89IT'
        b'Fy1atzp9zEqoX7/WmmjbM4fAwRVjWHgYHMAWuKTAjlSixlSZi4KI1yVuWIXNmVR+9p8ERXqrRuuFxQOheA5UrqFBZN0Visdq8ofjWE1/pVFfUVZYaC9A86I+AwZhNQ87'
        b'K5oCdYosU6JX1qrDzrDLMzOOzp1rpOfztNYA5WJfDtiTmpkZjntSLaxwb7i6z3UMBdQ4QAdGg+ihgbYhmuAZEzLQtSy8zRKL7MiULYvJpPlZwxagfjwlDWaQCXkofJRl'
        b'j/HEdii08LGF05lUpIemWVgToEulVA7NC02y8HA6mTSk3ACGMUJmUpWRyh9KbMjkLsGqUDIRSyR4M83Ch2jEbZmUChCuQvOyB4ry1WqmFDgmcHGPIiFfAdW2Y7ChH5yG'
        b'U3b9pALUB/WBU3jFh5G84GU8N0EHDAmrwzRtE/EYVpN3XZpBBmkn5pEuPkjG7TrsXSNgYah5KFwcyKqFZ+fO0zHNBPop/V1cF+shPdFUymIBnum5YkinHcq0gcoszM2k'
        b'fM+DcLeK4UGQxi7yfbyyM4kOzYvvXXaovy1cx9MhHJeqYWUyHO7LaGnUBp9MPMDidVhkiKnXTA0ZTxJU6/LxwA3XjZT2MXGMm1yqaiDK1lC/jqBFXcHvzrF+b+iWrhvT'
        b'f86RukqO21bP8DqcU/LdVNPynbEBPrFS/9bkKSMswn80ydphtNv6lH/+xpzqccMki+68M3PUqW9e+HHC3+uXDfR3Xjf3+3Dbi81ztn91Irl4UphPuVhSUtfPJzvj6CCX'
        b'+6N2rluefvXVoNFpx6ZkvZx99eXXpx4Ye3hH1v6qvU1HKt66d0v51muJPmMmtXpteKXx+Y8bbMo+zA3zbFo+NezCeWerl2cfasq/8fot+Yx5uxPW3jwWl9v+fdXoL1rC'
        b'fszabjdj6oyUr68/McFyGK6IC+8SU7bMmG1649De2qvTsuTvm17y+3rB02sb/xnzwV9/u/DVdOVPw3ImLH5z0KYPy3zibO+2jLuoSr2y23XBEXHbD/dmDTzwz7/gvxSD'
        b'lJ8c+1Jy78abv9p+P+21Zsy8fvXL05vy1t8O8ZTfV6Qpfhn+9fB7Xw7+OOXW9Y6CH1rffCXrgNW02d8eqBtb/+zWt0YvmS5umPuF19fp4/eGy9eseuXtZ0rSsjreWTLs'
        b'2N6msEDf1/f9qNiyIH1g55ahq42/3Haz7w6oOXPvjufBj6M/sfgW319XO/XnCAvX3ySTky/avv6F0o4nZDf5wzkdGAE8sI1ZjbZCK7caVUINHJQG9WLQoAapK3CSpwrV'
        b'wHFoUfXVoDXMlWElj1PcDW14zAjqAnpFXY6EGm4M270NLlIDUHIfnaDLXLzA4IrxAJ7CPDXXCt1xrmBBN9dKDB5jDXAfbQoVlJJBl9OF8rkcduDcHkcxN42bvQZgTg90'
        b'CDyLNSzOcNqywTrYEFlR1CRnjvUsmlAKLRNpBKciRRvD6WDJnsJmdzxOYXL9oHktFMkEeZI4cuEATgGTG+ILxzO1WBVueANLWajkpJRwXXoPm63cwCaHsyxDSoYNqT2p'
        b'QoJjdc1riTJu7BuCeZOxMkC912uy6OEmHuYRoIWwL4RcdYbzyykTncxZAldXzmdDmk5W8VVmmsMCOKNLCLMa6+34wFRi5wpm4YRDeFlt5SRjkcuhJW7OxcKAQD8o5kn0'
        b'mVCgA3LkDpflbnAlkZnx3CTJbOaQIybERQ418wVLL+nM4YvYxXRSuJr3BavNJJz4ZTmUZ/A48Y5VUOoW5KKEOqgmVZgp2q8xVZo8dsaz1X8mLi9fA/a4l4qK+qyDO4RZ'
        b'ZhJzkSW3i+YSmhZvLcqlJhIba3Me7ymlae6UaYMnvNN0dRrfKVcnrltLB4gDyE/6z44lwlPeDVuJiZElzVAT1dZH0ZImzktM7stES5GnrcvFzSP1WN96ZWEHPypzvduM'
        b'ln6jZ2bb43e/bsL5DT1Z53oSzvdQGyeFPtJr48wR7joYtnI+RrMNx/5QAysz/vHIESFero0Ckj42Sn6CUnYv6gHFIjQumei0qkdZ+Jg5Qa3CUAU2WmW/NCjwEXoKDT0f'
        b'9oCe4hzMueSKNlARVIe4kqF6d+PRlS7R4JNBh2l3gikehHMW/aR4lvOnXYIaR37yTydyT1XPk58IiUVqCK1EOKfyhnYd+QFPhjFFJQRKUqhckZEC1a5k83XNIt/8aSbn'
        b'6NVGnlgl5z6no0QsqyXycwXUTqAwksMoyuQJ7OBKV9UwaFd7+AaulArMwedhz/Qt1zkMP05wl49Y9cYKN4Enpxwi0txRCkvpDrvhvECUrsMC3HSLYckz5HRochmLR1h6'
        b'ipvgBruncyTLkBQFqcB+03QK7dZItbTrUM19jK1Qj4VOSscgUsvD5CTYJMFcaJ7ENLiEsIwA6PKnh0ywkSC3E83DsJSjcV2CXXguDMtltEpHBGgXYPcmdauCzOAqhZLz'
        b'Xw+lGiy5RDzFW7x3CLZTrx8UwH612lOBVbxxZe7kJORpKREjNYkwJVjMGuGysa86n2UrnOcpLaugkNXTZ0R/5s+sBjJK5I2O0IIHWI+s9Tblvsd5y7lSt80nk9OPYk3k'
        b'GsqiR4TgCCIJ11CoOpMQCV7yxEus/1P8dgtDJMIA9+xPspekTuZKsMOsUYIXHZS0j0dOnTqA//H74Zqs753znxjjJzxA7qxdkPaCmtzZjixB4aiwVRIrxEryxYHCMS3N'
        b'MxE6/0FVCcqVMzc2PTAxOa5RTfQsSyK/9Gaqpib/VXK1k4LBsEMdtpnRDhHJmcM9lqYaARn3svwKSejkqUTuKIbiqZifNWdBfJpf+vZkyB0qbB1vTeZEVzpr2fokc4EM'
        b't4P74j07rjh68+bGDrcTnAXB2n113/Rho+ZyvFqFL1H4yPDEQ60WZVADMYg7bfhqqiCaajvVLc0t8KJatQzsx4ZwAZ6AGnIpzQJbNhKRyVYyPduEvW64ktkdrN3HZsx7'
        b'xXSpoBTZyCbATcrzmW5ltINPoyHjucS/hwzpIZq9hEXbuSZpDAfYpfUjsAnbyDN4ZoqxIB0rmUmO/tNKCddAy7FuiwpLooOpg1FUSOxxF+T/W0OZR4Yy/Ul6HgD99pRE'
        b'eIBmnA7eOe3gscS4vV5TFFnYYTXVRKS1nzJtK+ug+UlYoCDrdwIUk+VEFDuoIroMXTYZ1PdK9MhcLDfHDmOy4KrIHXDdn5d3wIIMcxHmKcgvi4RFK3Ava685nM9SODg6'
        b'bffF1kAy9f3F5Vg2h9sAWlKWkLHMx91u/thJLhrBLgnWwr7VieGSKzKVN9mWViWujosI2G0bYXuj8/Cv+78syC0YWDBwwDPRT3iOsurz7Jtnzpyo2Dlq5K4Sn6dG1q9r'
        b'eu6puhWua18b/+TJNWUeBXVNQz1cV15ek1im2L7rZk5L1IalPx0Ke32UtPSdzJd+3Jb50jnVn68cmlL85ptdP3h7X73g9o+nFBnxlTX/XFrTYbElZ3qLywk88bd3PrrT'
        b'Uv76wtagYTFnHRc89YTpc1M+HLjUdcq+X94KmBhxb9oPfRUO6dvPllVsDy5xnhWhCvqtaOfxNY5pmaeqzjTvjHgxwnVAW9qkb+5EfOb6fsX6htrX0/u9WZ7wmXHE56ua'
        b'pYkfDTkWvfVV4c6BdZPzBgQ11zYafbESb8+ZtCnZ686H4T6Tmk5ffefogvPlyWfCC6uiPF/e05j92qAs4a34dfsLopKbtigWeLy64oMLeX+zsz0U+uuYFpfXpqWUnrt4'
        b'7m+df15x60ej9so//6VgfPDydU/m35w/feeke7PtfvV3+XTHifIrL7V/gMe7JH+d/MYr7hPi7hxYWPZcWNw7z/vGvPCJ5fU0nH4j5vPXSm5/PW5hzdC3g28/VfLaZxXv'
        b'fbHrE//P5+U1fiB5bma/wNOLf/L8y1+LYvNPGx3oExC3xWy37Ybf/jTow2mtd/Ye3fJ06Nu78o2DPnF9McLdyvRb9zoXI+nnlSPHnR3U/PM/B2cufnXxoCsr+9x5edPB'
        b'7C/v2F3aHT2zoj2k7u32/Us/3HA0RPirVVnN1lrj8uAv1g55Y0TzuNLstdUd/a4ssri2JfQv+JcPm7+ZbvxxmNHiu47Tx3+95PLzh+/MXLgoxeWT9T+KL9n+JsYnfxH+'
        b'xadmPp9v2/BUwxdFWTWvvxwy0TXLZaO8z2ef/joibP6fVzx//5kXn/J48YO3bzSYFqft6gpb/G7JO05BoWml2+qrOgbufWmH5T83Nfd/4oUA78i8723Gv/vhqjVWwW9J'
        b'7o6f/eSwuMGbNkRvn1i3erudytlu89ZznYe+/ujqe1nHx3zX8erMJ7u6zldlN//ti7U1G74+8upLF/c9a/33wp+nvb7g6YNfb34uct/BH9dN+c2p2Gz10xWRCruPsmcH'
        b'bU/we/3Ql7PTf6gI/HjIW2/meu7yDPX8aOrGqp/3b5t6Kr6lKCxr/vnXVrwy+HLM5qo6G8/bzyasdki9k7xvywe3nnD78ZusgRsqT3sdfrUo6+xBG8/rzm+Zr5gxJr8z'
        b'2f/dr/cf3fL235TK65lhfyvYcbfaRPXnatupzyvT8MD4Mdc2+udd2eJfYdHgVff2xZC3Zx3enP5tV9sPk54NSDZ9IfroV3dNWyK3/2j6qn/Xp1uWfhWd5nZ9d6b/lyeV'
        b'mzrz75u/JvvKZ86+xKsHn3i14enaxF1XxPvSV+Nnf3/1J59bs2xDPrlcOanhI2hX7Phg7P2irakJLbMW9M9V7fn8g6qnvuw/6YOfb//TdvL7r25PPNL1lfyA9xdjL2d9'
        b'Pcs78t6HTWmD7jqvw582f1x0/K+fpsyeNmdC4/szvbbI2yqCvz/hveiItG30Gwlbv7VfnZ2Df7vQ+a/BP9vdv5u4tuay/H7x8np/u48+q2s6/LOVzVWv/bGjlOuZQizO'
        b'x2KFLssK7FqvQ7QSPZPrbjlZeJKps6KiO8IEy3Zw5Lp6KMAcqv3hyZU92EBXL1zBVMuh1nAVdkFOADn+tNet3KUJ6QJPhiy1wLNu/XpyVFIV1pOzDKV5mvfiuuyj0FFg'
        b'TeOZbSA1kdSEM27a2epwblpghQdTDueSY6XVyQg6XXXhD0NGchLWi3CJ2kyxSqWbqmSBN6VzQrdlUA7xOLw8XeVK5FqX9GAlPdbbgFK/0qAcLJYKE/GsPMwaqpmu6TjN'
        b'KAD2wz6NkUIeKTrOn86MG+5Ek84NgNLsQEeiyK+SeELDZNbNIZ6wyymKaLDFbkSmptXbLY4hLWrmg9CErVEMJ67QVgsVt2kynmI2AKPF0KXAIhdsxX1wHssCpIIxXhJD'
        b'ogfzKKAr/kT2LRirvqUsANvI4WIBRUQQwJ0KpuB7bcdjDCyHaMcX1Mi0K+ACj505uw2O8oeNB7n4kZebiUvs4RCHEiRia6HKkaKqHMRjqSz9dHewsWANLdKMZXCYdchc'
        b'ODYzwGEmJ/kUjLBLlMYT5Z91fQmcdcC2ACiGSrwYooBGB7lgip0iEbhzHNjYWmIdXFS5QsFoJZYQ1aLcSDDDChFL50E9n4Sl4wdiWV9aRVMltrAOsIDr0r6wk4wIE387'
        b'bKGDJc5CVazG7hI5gk3AwLFkHNuo18BzqtLMwZHaN2wGSDFn0Fre9xexeILCNQA7AucosZQ031JcgU1wmmeHNialqoIllF76KBMQzkCNL+v2xPGu2EYaTLq8fDstntTe'
        b'SOhjJyUyxHHg9Kw+y7AlIHizjy5nqTAYdsqgYcUYjtrZgZ195k5SufrBBXNyC+kOuXQ21Pux3ptBVJrjCv/t2OYSmAbnfMn8VCklwsBwmQ+cm83NaYWjFtK/CVAtUDLV'
        b'KyPhOOsTG8eANLcADei1EVl01dIZ8fHcqoTlYf0tdSAdOZxjNnAj1lwjaFT5OSppqocUqiVQDlVbWShVTNJQ0pelRgIcnyxRCHDdeRbrZEe4vDgg0AUv9bTcwXU8wSqz'
        b'PIQCv1NgxmW4V4Py2LiRZ1t3EpmzgCprFck9zFNY6sP7aM94a4UDHHYgzU8LVIpkeuwX4ZqJO5++B+ZhAW0KFsHVIBeJYOohQt3Q/uy9CVA/R+GqdMSSjRShkuxuiWLi'
        b'1EiO8rqfzMFSLIAqJzIwrn4cWNkKyqVrlmxlRcfiXjil8MCTDq5pwVReOy3BIwPxCGuyKRGJOxWy/kqyIliXGGGdBNtJowtZrVeSjegms6k12mC+2qaGR+AIq1gQ5IxU'
        b'uZKmEtXsGpGnsVgCJ9LGsNfGrYG8gMDBmMsM9XJB4S/iaQUcZUM3lQikTaTzcugApQcGu5Kl7iY16YMcahNq8CZVGMgOANeTBLwswPnhHuzSsCR6gdIzQKkNUYrhhmTw'
        b'spWsNlZkGt7goXXhWRrLan+BPeYLR0aqyOjld0vwxXCSd4Ennif7Sq2OQZhZg+Hiqgw1evgxPKvyI/oHraubRDCbI0IjnIOWjNFU4ie7QwP1UZRh2zIy1ckiItOR1t2W'
        b'bLpks6vCAo7z2TQUdqnIHnQKryvN4LwzKZls4hfJnQOtZY7QBcf4Wj410JOsFSqz86tGiyVY0hcaOEjnlZWzAvDcBK2VdcAa1t/OMriughNwFi9mZGEbGao+ktVQsZA1'
        b'H68mwQHVovWMJ0QChwXcHYpFPE89P2kFtrlhscMyKCYrBQ+T65jnxiftaczBnaTODv5pUdmOomAMVeJUyB/GttVIPEgqXQRXaBhsCLWyFDvTjclKlMZCPpayIhYswUtO'
        b'DolYqNk5KEA5XIF2tjeEw2kXVbCXDT2tyLaq3hcHwFmZBzZ7s7lC5nZenGIFnmObO9M4DpAZbEc2fqatd2E1aTTZG0fDGbp/0R4zw3YyM8yhkXWZZPgsKLWwYGCp4mKJ'
        b'y3w8xtm0r0IV1KrImJtuoApvNvnE3tAXq6RwZBns53btnGWrKcEBFJDNh2OeL7fmV06v3Qyl8ixqseXW2g1whb3SYSs0KzItTOHSQtKnIyRzLadkUK/uBpMg1Sg6V6jb'
        b'wFYyymwmm2MjsHJLKlGq2A7vl8YuW2CjdIySB6kS6aRlHseBJ6LMfi0WPNSYwwl29MNZqFjN0HLdsCTIWekXRHbrRLwawCGYp8yQk+XWMY3vVflE1jmOBwJ0zNTMRo1F'
        b'tgzn2BWvRbGA111k6jPXmwEc9gg8b+KGuav4WeKAuxX8rmo84pJGljZFCL5E6bN3QhF3vRzbtBRvzutJxR0mDYJcSzYbjeDMOFVwfzivVC81bxGa4OpW1t0ZbnhCFaxU'
        b'ToRKuqXXSqAieRKbI0TMuYRNA+AwvazeTyZJTaFtOFui9rhnlFM4kTr0NIEh7EL7ctYzwdgB13kbTPxc0khhtAUdUji5aiqb8kq8RKezDo69JXRooOxNR8xjq20Jnl2l'
        b'IPfYwE4aK98pgTMz4SBbDVuhyUqBJWQiQ2Uwm+smgrgIbzhzCWBPFLaSnd5/JV6VkCcvkaW4GGrYm1fCof60dVgD7Wb+QXSqkKdtIU9KtugjWMimHZnP+XMVSoreESYZ'
        b'RNa2xwDWrlVYhdWqYGx1w5vDiPjATifrdVIoiR/AqjxiyDpsc3Z1HUw9H1KsJyebJVzlZZbEwAnFnAAKWScqJcMWk01kBOuKaqhXBeJZvOlH+suUtYovX9wjm7bCmjUp'
        b'lIi0BxSQCydcSLuIyDhM7AsXNrHJsEy5nRHlBMMBvOziSKc0Wba12AC7+Ua4bxQcUbk5YovreF8l3Xyui75YCTfYVAnFM7ZEwD0w1SWYGyK2SbAmhCwHJk5Wwt50CpXs'
        b'isehsBdWssgp4fFyhpfK1cfXP1NpisVEXhNFqMbyVWzFbcHjXiPgAu1myrRl5UA3Ngu8Ip0KF2R8X2qJt9UEa5NOOEFOnCDJAtyLHEwQWkxxXwCeGegaRPbpTZIZWOrP'
        b'LpjBySkBUJKKFepAbrgu4QXmRIcwA9xavEBNxRzghDqjlH3+MwC58kdc5+AVPOtWns6s+swNtJhavvS7gXYIjiYMnZijHZtJbBhkBwXusGVQg9SNY8ICyE3UiMf0sx25'
        b'aisOojTs90WpnWTQfdFkkMT+W9HKWmJ9Xyaa/SbKKEKypWS0OFoyiHwack/8TbSgmMbm5AmbX0Q5/TxalN93kFj+KpLnrSXDJNa/ic/Lp5sxDGWGiUyRkSXWkgG/ivIh'
        b'5Cd9m0wyhHwf8C/R1Ia8i/5O/moxgNSFQpU43CdlGT3k3eTqEHIvLZdjLJuQMmxJfUxIiZY/yBUm34lPmwdogE04ubw9+T6Wvlky4DeR1vZX8We5rYlk80A9Ph3e8zpc'
        b'so8aOJ1s5mfIUA2RC5z+0oCPKUe4Y2fYy2S4RqQaLKu+Q0KTlYODlTLyjcWeN5r3QjpJXyewzO2w+b7eQd5hDNuEZVpzqJNELT4JrW86za7h/jrb/xUEkuna7qqkM5u6'
        b'5PLITxNRJlcDZf8iM/4f/PSC3FOUWFqZMD8m6ej7tjM1OCV00om/yaT0r8N2CGaZzPlckRxBbfbRZHfrZbMXhRnL5UShbcXrD6Tjm6l/qswejlUijTVRfzbV+WxGPiti'
        b'zdlnC/LZUv13K53PatySg6ZaTBLb2H46mCRSHUwSu3Lj2LFaTJLBsUO0mCQUx0SIHR5r/zswSUaUy2PHaRFJLOKNYkfGjtKLRULRT3SxSOKVDretGFAP49n2iluTmHHP'
        b'7QEgEp2r/wYKyRSezz5eKd6WzQ8J9b4tnTd+Xvo+Osnr6bcDkseHA5nCEzLH/y4MEfVDU34/TojmdSz/04PihKSf5Ek7FNEj/RTDIgr1DgoJ92b4IKN7YXOEeXmFxqX1'
        b'zDp3Tz9NG/w4t3poQTQ0Fbk3wFCpWmSNnnVWmvYog45D+mu68Byazkl/g7bodXrJ0Ds80tvoPf8XQDUe5Mk1ClbD/23Eo2rwPyxKZfh/TjbMIZQaCa2KrLSVRPbkgGYH'
        b'bfBU4sZ0U6mKim5Wk45TwnTf6DtxL8Q7/i0g2iz+U+HuzoFTXpVMTZK1bVqslDDhLUu5SA3khq3B3B5F9MEKA5SglzRRIlS3Mige0C97elRuHtBrmT0mNoeNsbqTDZ5m'
        b'9Ovrh2B0GH5xOx3eFygAB1Ub/tcAOCjE8Aj54wJwxLKaU4QBGvX/P4m+oVklj0Df0KyyR94x5bHRN3ouXEPoG4bW/0PgMPSuZf33/w70i975XTwVITqZZhHQNC0DSUfa'
        b'x/ThrD6AmNFjnNUoGfQM4cgX5BxxNJwf9Ch4Ck1Nfg9ARWL8f7Ep/v/BptCsOD3QDPS/x0GI6LloHxMhQu8C/i8+xB/Ah6D/PZiyYxQcnjmH6gyNuJcmpfQAKLDHg2qM'
        b'AnKxPFDN5dttioObWKjAU3AGqhJf/ROKKsqm+tztOMpJ/ukHa+OXP/HWk689+faTbzz57pOvPPnek1f3HKockd+6a9Thxl3K0itvHc0bk99Y31rskT+iLnfC0NYZQu5V'
        b'i4kdbyuNNCG2x6BDgyIQh200xBbysJbHPudBLu6lUAI9gQSgcVio1APbLZi9tz924eGejthgrKO+WOyAdm56yYU9WwISVmstLDFQxIw6S8fAJRoWbQPlvUjzYFeYJkD0'
        b'3wmU1abROzxKBFqgSaeX65NHfn+u/IDHkoo+e0jOvMFaPFbC/FqlJDj9skQjrelJlp9nrA5levBN2kz5kQbOvQey4+UPD+GNMe61RhSadUITxAqNe0luCiq7xSvUkpsx'
        b'k9xMiORmzCQ3EyatGW83CdP5rMO8tE2f5PbwnHdd5fL/i4T3nnBganFInQW+gRwgNB33vznw/82Bt/9vDvx/c+AfnQPvbFBoSiIngS432u9KiX/IlvG/mRL/H03kluqV'
        b'Cm14IneCA9RoccEmwBUKDXYDjnFoMGqxn6hYxCMowoKMfbE4xEWN6uXrj+WMmWwJRdWiWc4yAYisZgpXE7GSRXkPdRV7AYfhkSRNanZnFGfIuImdDqqVxt0p4VsdM6ln'
        b'YgcUbNHynPcG9Zo8X4PpJdIQpiOmeB2qsTrTiTw4ZCU0d6ecYpGvM8/zwCJK5OrnvNjfz0iIHGcyV5yfSXkdsXNWcoAWqQv3zqXe9ECWQeuMFUE8+CtUYYzlwQszZ5IH'
        b'4keO56Swfs5+EQuXuCxeQjOA/YMCoTHcF875Brm6+AWR591EuKgYD6WhYcIwzB0NBy2TTLyYnc4RG+CCCopTqeWWsXFgLlzKnED7oxQvU9L0HuXTnFZyL02SZUnlMrjm'
        b'J0RBqTHUDMSuTCpLWeFx5zDNveoRCufPqIsyElbEG+M5vAmnYOdcZhT0wGo8rEi3tBBnQYMg7SOZiXUKdiXMKBDbsDNbJY2ikfc3JU4R6kQHSmzPiOfGbp3X6thPSEy7'
        b'uVVU/YVceSFzecTumZbgbp7/xcl/zM6I+cj24K58hfvGOXPnRSyveyXfNf5j2Rczp/glPHVrYKrXmKfW3Pxpy1d+H1aPKlg9yUm+6Eq/bYrBxt6+68KHtgz7zuTFhnLf'
        b'Hzd6l8xY+cSGqRfn3Dnz1w2LFvsOMVm/ftp3b33+8d68Up/B04c3ZIydbNeZEuZ/M+nWyR9dvwoc8i+zO15zUxd4Gn08bK+Tct+787c+/efs5cbvBU5Ykmyz+rfvnd+t'
        b'svu+tPbQmrCbjVfrs567telCQUn7L55/r+s7eXX5c5YX0bjwtv/G/iVKax6gcEQBTZpQIDzmrokGwtOb2fUN2L6wR15o3y0sM3QL1jBveYD9+AAohEJNXigcj+MRHB14'
        b'CffpZGxC0QietLkIzzLFZjIWwjGFQ0hvLjminJTATR5D6UED0LQjPHY4IyiGNijjUT5NuBMKAmzIBNNoPiORh0eaYZepTkaqow+LbJtqy8IjEkKwWgFHYa9unK1OkC2Z'
        b'hPu5hnYDKvE4b0QAS5svhD3kTZZ4TRoI16CWhWn4p82mPMlB0h1wgfMk94OzPL7h0kq7AFK72vH+dP1fIKsR6uAYq6HlNtjHjc2w01Qd/Ag5sJuTX4+CQif/ID4sThJs'
        b'DxT6jpOSph/AEvb0CtK7BRrFEiszmGJZAjWsfWZrx2kyN+FcvC65oCZz88icB/nrFP+DeZOBj1IHU1n2pNSEEfqayOXUjSyxVRMCU4c1/bIULUUTlgm5eXhvFUp/uqPp'
        b'46Q7dmc6GhkOBTA2zKWrJ6vR+7G00S57w9rooxr4H05szFPK7q16ZGKjPjXuD2U1UjfHg1mNo3hWY8RgKH8wqRG7BurLa+yd1EjOnrpMhmJ4BWtxrxOcy1RjGkxwhxZh'
        b'zfyZUoUwEpulmAedq9l5FbYAmxkoAh701QBhVqfxjMBzeIanRMrwZjJPWMRa6GRnhfsOcekYCf0UleSYZSzwnL79o1axlESye7SO4hmJcNWTQZy4Qe0KdToiXpvkZgMN'
        b'7P0BkGuuSoMjcFFCXd8CFOM1KOLyw044YUMTEo2EvmYsHTHKjWd2HYLDmJ/lHaCTj7iFu8nw/AhsC8NyGlQo8GREPDWFN4dsmJtYNqJUwMszeDYiXl7CnvOBWixXcEnn'
        b'ElSx1MGzPKEN22ZBfXd6IBTYaTME4Trc4JChNrttbcUpouAeZfmdewhPjxtqPHLpU5Ii2kXzQreqc+byI/zMtgn2EiEqyvFJ/wn/XopgwuPllV3VGGMyfQUW5nlpqpoE'
        b'xZlss2l+QVjijJVquiXcC20UIoUGAiqhQzqeiDkBsBfbVERaPEk6bT4WWYVj3g7WnG0TLIK/F8h4L4xyXuyznbcxyNFus524lEgSUVvLgsI5wIai7xKWtdkjJ3AbNKik'
        b'IYF4Xk05FkGEFJr6JxWGJNPMPyiGalakuZ3cPVEcQIs0j41IEJQSNkVwz7SBKhrl6wo3WKAv1Af920mXj9GjUhNNj7J6758iskw9IrHesKGpenAI8zhVWg0e2KhIh/3B'
        b'UoFn643EQ6zqyig7bKNpemsXqBP1JpqxPL0dRG4+znP08ARULoKKJD5/KUJtDc3UU+fpwTF/cblqVSaL8tyJOX7QTtMae6bqFWF14l2pg0RVQyrgdy0xMzxA1c/b9ssv'
        b'/1H/8/68r31vWVjPWV1S1Kfyp1qfPdmyb/JHf3DCe8jXL8Wtaf3s7Y0nKhYvmxTQ33bStz7OS6oD+tcqlpxf9pPUueRv00//HFpcW6r6ZOsn0z/JOjIrMvtY6Vr7fc/c'
        b'sFlg+dGbF4tslilPrKtXfGX89amaf4x4JvflJ/6Ut2mh767bK/ublQ279VV+zdsvwuv5DYsC+mYZjZ83+M6ilOPWEbL1rx2/M6B1U7iX6vhrpfc/snjnzP72Wwcmt7y4'
        b'rNL4CZcPal/vMGreEN6+6P3cpzsqy16zee9M4t1si8VDn9/uee634Q2rYm62+n416sYbGUmqeT/dknq9Uf9Wh4O4Y2aSNOndD96fMu/akGd3bPhuo41T5qpM5atVUQ0/'
        b'OTUFzVKVjF9vcWnglRVZaU2JEz5b3wkdI2K23PVy+de1E+HKuC8vfZeSPaWjdOaiL7JumbTdGfz6qaFhL7kN+SsePnM4w2RqjFP6b7JvbSdsebI503xNyLVJSsW1JY33'
        b'gldWxR9advPd2Pj3hzSEFbbP+3JCy68tCfX1xywvJ9SEfjfVy8p+Qf2f0XL5sqYkyXuKlvnnn0ly/3vyF4OS7o+reGnkV8afh8bZ1btdrfvE+/tXrH9ckLu6YWad6ayQ'
        b'7J0X6sp/2fb6V1+2R9u92fXSu4NbMHl7+912D9s3OiwcAlzee3F6fsehj27N2f/c4Cbz8d5r536cNuuVwZNG7jZtG+STdGBSlm2W+WTjO1Mu3B37f4h7D4Corux//L03'
        b'w1CGDiLYQBRl6IINFDtKB0FRUaRIEaUIA4gdkN6UKkUUEKUrgqIUMTk3m8T0bLJxY3o3iem9+r9lBgE1m2S/v/0vG+S+d9/t99xz7jmfc4YNol5Y/uQvgbeXu0/erPVt'
        b'qmdwt9oGi7nrU62cn72u6v3DOpfrTj19PfL85+YmWnz001379G+/1/ht22yLm1ePvP3moy7LZ31vF1vo4Je/K/rpsI8XnarybX105Ilvkoqfizh5qOfbK2dHTP8pnnZU'
        b'/fbvhj5h+XdjhC9++e5DD/TrG5mph7+b8srH66a95jYj9t9NG/Hfjut+OL5uStrOqtzU/SfmP/PM9fl3XvkWP3d95UvD2Jraqim/h7WFR0dv07kTusoi9e477yXY7fs8'
        b'2eRcykexue9lH3qraKEd6lL9QuOOVfHPv9S8Veizbep78a8XyzVf2rdm+bytv/7248uPdx3Xc7iZWWIR3+F45y3Jz8+4nE3bJWt6buuRN342+uLWAoOsX6alTf/5p6y9'
        b'xw0ffaSBvxaeeeTi7e/++eb1r07/ECWJWeQRo5ryTb/lmW8vLTGATqdB8H5v4Zotr8XZnjkc16/1kU78uld9n/td/5k33wk5k+6yqBidOS/6JL7xx8/DNQIM019Vvf1s'
        b'7sYLRpPddv+kZ7rg48+e/12WSNltaNqmRrFvFnoP4MqhNZRKJBLIQdfHuHLBW/4ytAtpKaiavpcuDLS2gxbNe26JFX5PrsYxa/DMDe5K3BtcQ6dHsW8oy5FmmCoEEn0L'
        b'yo8lFtNjYGtiaFEAl1ZAY7rEehxqbZ8B/XgfNIiVeLVlcPEeZG0yXE6RkY9HgpYqMGsyT3zyWBEjYgpYw6dzjohbAtkSLOEM7aVVhYjtUfcCr7GgNaiFUiodpS9BQ2gA'
        b'8zjj4GmoGZgTGtQIVbYUnqbApmGRrF3YJ0EjbBgGUMauUfQZBadBtr3ghzpgmGZYCiWOo+8Pao/Bp61fSOWeVficPE3xaSIuZg1Fp7kyq/a16CJksm8ZNA36jIRN3nuo'
        b'YTeWXCqgWZ6IyghAbQI4DRVvY5qzM9ARg0oMvMbC01ATusIwENlwCnKgSBf1eU3ApwVCJuteBepGfZ5z5HYT8Glwej8VUEX4oLigRKfBZcz8jCLUnDfSXuwQraEIMwW+'
        b'DF1F2cJWc6hnkJ1hdFIdn7vDaIDnFBizjm20g/E6MIL6dqFjDGc2DmSGObsOBoAqXoZOK4yNpqMKhbFRKXMgHofPv0LIWy71tdWUEZDAGR6dxwcq6z1UQq3kHgQlmMin'
        b'ChTKarhAzcGXoM65Xr7jAWyoZQvFsMHplbSSyeKpCgBbOpwaxbD1YRmSuh4MmSL1tPU+CANJhP1GBTKGYpshFsNFKIaTdJRn4R1QrYCrwXFoG4Wswbk5dBEui4JSBWKN'
        b'8KGjoDVdTzYKFbgoinHAfEO7jGEcVGGQoU0qfQjThYoM/FU4ilvbAq202ploeCPmf+/zOQXnFYEj1QV0kiHXVDi5HgWuSeNog8KcoQu/OzbRq5KpBS05BfN32WQipBNw'
        b'axowQHWtqf7GpD8MsqYRJEDNKgbWRDW2GyloTYFYg+FIIXbpdFrpNm+UpYSraRqNAtZC4RpDHfVB9VzomSQdi1hDZegE28f9UL58f6B0ImStOIAO4VzUgE4xxJqY49MZ'
        b'YK0XjtGXqihjAQWsYZ6+HbUywBrksoids1HOctSg4+U9FrGmhqoYwuTUXg0GLsEcf7cSYIJy4ari/uEKaY43lKFCsv4JYg0T4nb6Uhev8w4GWsNyxsVIClqDRhs25ScM'
        b'UI7SIfwBKGCwtWVzGXDzdCw6T7nZw6iacrMuKI/t5140ZKS4p4qG4XuotXNwhZbrYIEpWstS1uZRJM3IQXojgnOdRNflePdf0yG4tftBa0dn0owoCw93txyVTgSsoQxU'
        b'Q0BrGWiQzco5aLTH9JegVMfC1qamUvKwzB6VUsdg0IKFKAJbw2T7En21L8B0xwr5WNQaakTHGUKjnvxJ3kmgeb0CuIYyvekCc4yOYLg1vFXqNBlubTlSIEfOohxop7g1'
        b'BWpNG04KzoGbKTWYLYJsMi4aeLeQC9PLuLHGrphI9YitoWeTIpzs3JAxjLWfiRCMiSKjdaggCF3zInds0A7Z9J7NCilwJ83oAurSwUy5smyyQjWgXIAuY7yP6ecZ+Dgd'
        b'tLeQKnA4WFY1n7uGtlsH6oE4VhyxthwLl9Ney/BqR/WhS45PyWSUjw9K9VG83PQlYijDcnUh6/xlaJBa6kvH4+X24YkiC2eOLhqAPFBM+li43IY5bEHm4VPsKDnxvXlU'
        b'C70UMocy/SktX7wV9cpRydTtXur34eVwmfUMzVuLMg8TxJyIM95M8XKbljAoZffqCCXGDS5K78HcklzZom5C/bNH1QAU4oZqXAWoCkRD1AtbGtSjElXXiTi3sSA3OLOe'
        b'1XV8Y5QcLsUzpgKPFd6HKEuUchC1sJV9Ga4aksXqJVNHhTIPxbFvgtrwDGSK1+H+1NOCZkOJIh/tqyqmloUpwkq89auYx78SAiVVItr24xNQCWpztGBXys3u2gfxaXnv'
        b'4pZe26JiaKYDPh1IzGJ6Y8qh6tX0xhSLaZX0WD5CHeVC2xFcux9eVMesMQnW3Sc6CHWQwfg7dGqKNV6MmIaTSwg8+DVoSDiAyqCCLcnWPTpyyJhFvJIWkAte0lGe05sk'
        b'OoQ3bQcF/KFrMLDJNJ2yef8Z71cPvYztyIBaDykqE2jWcXA5GExmi6nRet0+NYbyHUXODkMbO9DadSRyihLcacAQ2iifsXmO8YHsm2UiJTYYt4l5CwyB7gRrm7CHYvnS'
        b'0hiyFPN7lVJ0OkDRuDFoRB9MecjIJKxdTPdZQdoomm8UymesdGowhCoipBTTDkfxSU7RfHASetjbxpVQJr2HfFPDG0RYH4+u0Y2+DYv6BVIKewuBIQbn09JjrH0W1B3E'
        b'hL0UXcN0aAKcD3M2ZVSZsAiuu+NzLg8TWIrmg6F9dFGkY3awWY5PmAwC6RuH55MzX4wWm2Mpnk/gHBIZnC8SrlMEKhb/z+KjzUeUuojC+UxmU3AytKGzYrn3fUi+k/hw'
        b'Oi52QZ1QQwtetnAt6jkkHQPm60QnmXtGdG0ug/MpoHyoXUzQfMWISQnJsT4Uy6dA8hG3jYL7JC82jkWoLR214ZXbNxbNl6jJVvBVKMfbqgjPm4at3QQwn7EeLX0GHDPa'
        b'nCC3Gwfm0xaY64WuVbNGgXyof+s9LB+PMmn9qTRa92jkFegi7j/5tUt1KT2LQOdQv5edjwRdc6FQPnXIol32R/nTFXdkFK4HBdBMIHuV0CPT/t9j9Ch4iuob/P8IoMd+'
        b'TJQwPV3RwwF6aqMAPX36I+a1eV2cNvtVkOjyfxGQp6qmAMiJKQhO7S7Of5f+/Fuy8D6I3u+CmMHxDOkX2kQbQmF9xrwRL8al2vHa5HvJfwnNe1lz6XhonvHDoHlGE1US'
        b'/y0uL59oSQjW7Q+1JBncz3+AzntIo3BLCIwh+ZYSmici0LwneMW1pczgfwepu4ErfYcgEOO4/yNI3b8l1gKvrTIGPjd3DHxO8cx4JQtolhUJBVL7TRMvt3nOEq6rxIfc'
        b'j7fRVvwrz7oPNRcsrlStVK80iBbI70ptxd+Gin812L+xomhRpKhEiLQaVUORUDuaeVp52nm6NHK2JkHfUbSaSpQkUhKpms2RiOElQrAqTmvQtJSm1XBak6a1aFodp7Vp'
        b'WoemNXBal6b1aFqK0/o0bUDTmjhtSNOTaFoLp41oejJNa+O0MU2b0LQOTk+h6ak0rYvT02h6Ok3r4fQMmjalaX2cNqPpmTRtgNPmND2Lpg3zVKJ5BQZvEv2bRCBXCzai'
        b'5pciqqJTy5PisdHBY6NHx8YyUoZzTI4UqIGl9S3N1St9NqxR6Nfe6RcmmFsSe6exORhcb9RaJyWRxJiQszwLHG3Yv040IgP5a/64wpRqPLmd2coxhoQKuzgKM1BY3+G3'
        b'KVHJNGBEYhqJg5sy3hBwbPAIG7Oo8B07zZKj9iRHyaMSxhQxxlKRmLqOK+FhpkDjlYnjEr6JxALMI9qMBoCVm+2NSo4yk6dGxMdSm6bYhDHoDWpkhV+H4/9SdiZHja88'
        b'PiplZ2IkNWjHbU6MS4uias9UQl3i9hFjrXHRMczcYqndk+VKmcKAN268NRgxmlLYE7KJsFfMg3LEbcwsV8mU2cLN5FHEri0l6o8micyh5WoZgXyEj7EdVFjtJSbHxsQm'
        b'hMcR7IECuIyHgOAqJnRULg+PoaiTKBYFBOdivTeLjNqDyancLJE1nBoAWirerSIrLD5RPt4ObEdifDwxVKZrb4Kxoa9MuCVKj4+7JdkRHp+yYP4O0Riyo6IgPVQtFYB/'
        b'KTBlqnnKWF1SSkJ4TESEaG2FTluULznKHRLv1z8oojptMdVjiw6LA8f8PcZW+Wf+T6DMxm2mh5udPcwSEfeQGSFu9vFWWNHRsCy03Htzh2eJWprirflg81TLKLakHrZv'
        b'/wD9RIfXhYBYdoTjnR+GmxTGrAFZYaOFjF1+DwmWEx4ZGctsRxX1jlt+ZKEmpUYptrA8Fe+tURLyYNTHOAtbFgOH7MDw1JTE+PCU2B10wcZHJceMiXDzEPxIMt6ZexIT'
        b'IskIs339xxFrxp11WopFN97mYLqvnLDMrucN+178wVqWYtqRIrsh6y+SvdKbKediD6mdNepjak5qTXfRJAr6iOd0a+IOpAGLk1iAkEE/FMmwCNsL7Bs4K4FjlE/dkEq+'
        b'PZioBZ247sPaTtxhVMp8Gn9mLHCPqJJWhdkUR63lqIkAdMxAZ6FPIHEaqydzS7Zqxf149+7dM7EqnJom5s1XhMVxTuEcVXiiDNSCf4i/ZlTp5CBwKtpQ6cz7o+tQKRMY'
        b'kL4OjurKUaE2ubw4jnqZ3sHb107dypLnHFGlxBqqVjDfqCPrIF9qtVuKXwg+/KIUyMGFmOE3G2PhNCnjYBouhZagQX7xnLmLijm6bM7sHsrmpEjZYxGUQDsa5KH9sA4u'
        b'gvCAcB0PUQ4uBFUu0laWkuxhhUVodNHaw8uOuOsLQjVq0yAf2qmudxFcSER95B20OZHXaguEBKjbJBMxR6+u20g8EFss9p+KcXJYIHCah4TdkOWdSqZzKpZMcpTva9EA'
        b'ziDhNA8LcVAIZUxb3IhGYEiRBQ2uwjl4TvOIEJ+EhlOJgyH9lXNZsBH3De4k13p3hVYHTnvQG481OqqTNXbTEdq6COUzWXK9LeqnkqQBZKAmKBXB6RlwhRodeOGJLR9r'
        b'18ICtaBuqCGRTLy9vGyFJFdomIauQeEkLKD1ehlCoZdUA/VCkWdAIBcVrbsoHWXQxZO7SYXTdZ9MFoT3B3qmXGowIafQ7nt/BST6Tom950ZLVOCOigOJlaXXRtRDrr7p'
        b'4qX2NH4eKvoWGljiPquiArkJaMDNAtplnNteQ9QQhFrxoNObvFOyGahPZ08yXiKoxA9d5ed4oVyqy7fC32ZJ1ZLT8PzvQ1fEvNXUXWxh5KIeOIP6NJPIV7ukqIufnQyn'
        b'qWkAlkBzN8r3UB9lIpGuJh+mgbrp7PugozAsT0K9mqSqk1iszuBno/JoRRzdRGsYkqN+WuS6YBjmjaCcBVry26GtrAsyNEllM+Es9eRrCq0zlUtiBHpHJ3zbtlTincMS'
        b'TkOBMsQMakQXSZgZH1tPv43u7CP8gWJE8dT2ceh0nBTaXNAVusBnzYBi/HE+ar8Xo4Z+7G8bxD7iUDkXia6qcejYgdhDSxtU5Jl4l2cv842vWCI3mKf7hEXDwZFvGuwL'
        b'KhYnqb3jk56bnVcRVuH//tQXcj363tN0rPiqyLD45T0ljijyfHPzl99pmmY0NTc2t0RYytodvXcFff2Pecfg689D777xm0f15c6iWwVbYnwn/yy2dAjxbjj67vZIueqP'
        b'ZjfbVttFF7o3H51uVRB2SPX1ylUjqxy+dvjaOvrYpyu+PGznWhBiZu/+0dmN3/i7x+5M26Zmlm2+JnG6m8VnB2Svmvtd6a+NeKpM+7C86tOfyt1LU/L6B822eA6ZznZq'
        b'8Pve8GJZuFwWeyTR9HvBuOhja2TcMfxMUXN+T4T3YO7G4tfizJ/2NPfc2VkZVZGW6PnL5gW2zTURQY+nPz64UGJnfGLAceWVr56Lrpp0Z0lMiEPzyRvnntW53Bex8mTf'
        b'yM0jOz/q/gL8hyzttnzwtf9AxDedx59IXT+YvvX5qrmuTut++ufz544gy3qrD+t9Vy1ZfuBmGLyZN/f8jn9lWd0etsmfOi8noOLMe2rTKx4ve+H7Mu3FekW3V+z13qQ+'
        b'a0lR25FKu+euFSxyenvAIqHoyWG1DSe6Ptn63XP+Ic+dtF4sD1Vx1N37D9ck0x9av/cAFy0f/wNm5n2QkvPvDqvoztuyRSb739xaZ/Xjp7lnCmOCPTf/YP2c9LG6zU8Y'
        b'9L0yeeqFhn/633nz98zTkpoTQZ+5vrz98Sv6L9X8jpx27Cu9+3Tg1HeS5tW5TK1urf7q5eMxzkmDDvDepf67725ZO6P1jdWndjwdeCD6lcEP1b+oufvEmcN8dGDhG299'
        b'u7Ax4rDqZ7vOX5xyeW/dD4sCkx/54amg71L+HRbd+ovHNyH7H1nwxDcvb2xr19zRscrkVNqd36FUHp27fmqX950lauvbz3x9NeHJZaJ9q3594y2PF/R8sk1lK+nNWyA6'
        b'x1vbuYb5CHjftPFeqqiDXcGfQZWoAYrgAqEimLagQoGToirogGEBdUHrAaYNPQHn4Zi1BzQ6eaviEvJ5VzinxRQlhRGQrVCVoyZdhbYcXUJX6Zem6PgqKLKnXkDzUlQ4'
        b'SZhg7u9AX4VI4TgJhWTvZws5lgInOSxYuTuk2HJU7XAC11lkH7CAKFe97aDAj2qKId/e3caK4j9VuVB8EnenerNb62b77QqtfxaUjfF4C3WG9OZWPh/OkQszVGI7GR2V'
        b'cJLtwiw4B320E2bu6IyXn62HDbnxlaI8dBouCWgYuueyCzd8DruPDYTMccaJcM1MvN0PGliEmhFXdE46wdS5ClUQc2fcIqb9yVq0mt0YimFY6f4LBo/QGzsLVC1TXBZC'
        b'6ULFfSGcAeZAUtdzNh78bnx0i1E29MXwKFcdzlANBlzbj4rIRbcPuUr0V1VeJk5BJ8VJkDGPTr9m0AGqDONm4EEgurxdZsyF43F0BRXicfbcsN/Hy5Zc/fkqvp+NqlSW'
        b'wLEltBKnJOLpscSDTIaXti+e3oPQ5SVwM9aK4WwK6mXajlMb1Yjz1WPqvonmOAt+r+UmoAHoQmV0sUG7Dz63i+x9bW18lDWhS6txZWbzxOjsXFROh2I/ztQ45uYT9dqQ'
        b'y8+t++hbX9QbD0V+dp4+/ik2Hj48p71TtBhdxYcduSVPB/wXO6pRF15F7NpXa4FIFbNzGUwbeyrSgyoGir3w6su0V+Uk6oIm5KswXc8wyk+QU497IhOL3fzBw8CUnpj9'
        b'u+SmVHoKuE/HiNbT34+WGQWnCEaEae9EK1A18zp5mumk8RCcn08VUJ6oeA20izgVVMejQY0lTLPcbbhKaudlR3wAtgSgDh6fVOehkRlTDEhXKHxxjtVpbplKtZomhvQO'
        b'e5LcUo56pyeO+sJErVDCtLyDqEhDoYuEMmhWeNEsUbicW4GZmV6ifCK+N0Whqaieh1JrpWvDStQIZ0mnjlkTH3r1pIc8tMrRFTZSmXibU4U1L15NtPf+kMu2Yj3koCGF'
        b'Y2gfVIMGiU57UOChQcJ0kdcgd6/cF1Odi6PeS7Pw0JKNlBoEpaRFp+HMGP+l+nBehFf5KQfaMg+UrUcxC/aoBC6tIoo1qBOgIAX/n979Fy3SkY63/XeE1nuGRi0wpFDf'
        b'4d5fxUwoVTeI8ILpR5d5PPa9KxX+cy+RGB2Uk0KXZhBmSsJpR4rcInamEKYgeBqBDO3FA1uZhi5pJd1jzQjS2x6VuvvY4i8C3dS07VEuW0UNvihTbq2BeeTpUC7jOdVD'
        b'wnxUvJ8thNNm0XLrZJk6HBeTla8aJThC/z6mYLkE9btwpz2IfsiPRgVU4SZh8l2DOsR6qNCN6R364fgcKS5cpp5qTYuADsEVqn1of+wJ60mLWAX1UIJXqyqn7StasRW1'
        b'UVWK7aSpcs9gE2JqxKMrvO4CgTlMPIpyg4gTRt4HnSBqG96T0bx8lInOyX2J29GJahtoEjPoeqMskXhq5mTQQo1oUHEKc/vaknZIjoojrBWOQ1VRDZ27Kdoy3ERPNGyH'
        b'ij3wFqVEwt4dlYi4WeicyiKoT6R92Qx1xHmmLZySKWysvHhOd7pofdwhSjHNY6CfemDGK7GRumCGTNRDXy2BArGc0RaRE2Zec/j9qNubTo/FSg9rT1svW11UY+WLaYtO'
        b'jCgcZUB1CrE4XwXXMMtPGqdsGYHNFBCltizZbbsK1KMynxQiRkIxJkhX8dIgy+IAapmwMvwWYtZ0CZyX+KJOSzZvF6E7XGEtJIajkEXNhbbgw4VibQrlWlJMPCfZuCsP'
        b'Fz00KIJuTIOYqRgqmoOqrenxg/n047YSTg0NCVAW4E6pYoQlFpKKfMbpmqAYWom+yWOuTOu/1+r8H2mHHuR6gMRU/Q+6nyNclAavKxBkiYSfxmsSfYtAr9Z/k6joUo0P'
        b'ia1FtCISQY3+pY3zafMz+Dm8Ja8v6JK4XfhnGs2rS7UmEt6IN8Jl6uN/tfGPGs6tIUgEo4lPePKjTbVP5FuJAuViyO+fNPbmaYIXBJkKw5i8Q3QY747HrWj+V3MhYsXd'
        b'K310PD2waClfSsbzjxU0GdzAnIeraB7cqz/lVSHmP3pV6FaanU+oZtSlwjzl9Ti9X7Yxi4qxM7MiF2R2DguclD5g7vew8OedPuz5o+b1KJv381TSDsVdq1ls5Lga/1Rl'
        b'2biydv6WWugOdgn/0Dr7RuucSaHQFP8bbUY/I4D+v1wz6aaMv6UVOnrFHBr78Or7R6ufs9IsNSE2KTXqAbj/v9N73AbNUOV14x81YWC0CVZkBOQpeAjoheXoXeXfbQad'
        b'cZM/mvHh0brtAhOJ56GE6ETqO8EsPCIxNWWcI6O/WT9xSvPQ+q+PX3FjHOv85cro7nP/o8pgtLIp9ypb5bH6b9bl9Ud1/UNZV7IP91f2Z/EfFfrkaAcsNzzAHZLSn8ff'
        b'3TIa1CVBKHEQ8NAmPD1+wqhXAbZp/9YgygiJoLWmJD60zudG6zRReKD4mzVmK0lDRHgc0ZKEJu6JSnhotS+OVruYVEvysqv7uLE6wIkuS/726GuPtmpHXKI86qHNenl8'
        b's0jm/6pZ/0/dYfLcRJWFyDfWedGIICei3UjA45/ucw57MkIt+u1nOE6tkL9y5EsZT1ngqWgIDUPRZFTup7SSZnLQtvSHeLScq7SnIQaD/5GnOsLF7DeccNbHRSWEhj7c'
        b'nyWp4CZhMkiI8f/IZGRwnX/g1fKBVf//OS9i3w2xM83tVOTk8WKnSq9vK8I1o9/2VuXElrzM58l7S/H+kb/IsZFPzubvY21CQyMSE+P+aFjJ17f+wrC2/cGwPrjuceNK'
        b'2k5aQBYZU93ecwiqdDbF1Ld8ntao6lbIV8EjLsIjLtARF9FRFg6LAsf8rRjx6IkjTsRPEvbRadyIm/qyuKJnIRv1j2oLMtCFBH42loC7qe7sc3Uxp7ZNXSCqkp0zwjiq'
        b'JpiJX1+Xayerkw+aFzvzdtAYQzUrd6Jwdu4LMc5uE+JwmKP+J1A+dEMlvWPxivYkqAvqQqPYC//hSxxrBPgH2AYJ3PYVqtAEBVHUFMcTTrh6kcxFUGrv6TM9RXGBpsJZ'
        b'7VCBTmMHFgjytB+0K3UgmmFwmg/DEuUxqrKI3gRFiigY7bvHBMHg4+in6VDvRu5+vFARXmO2M9AwD93T9injSzbMYMhh8T5UiQZ5LIx3+7CYhtlGxL2ArRfqQoO2Vr5E'
        b'oMeSbJR30AYW0LQYrqtQaRF1TbP1EHPqqgKULjJVBnHtgkFm1ysWY5E3j9xHZaLOVHopdA4VoFpyFQpnULkMC5rqzgKen1YYYc2qR8fROQVoSLxQBcp5aFc3Yu/aIt1R'
        b'ka0vllqHoAfLoJIQYZKzjKK516PSAC9U6kF8+3njPnfMpePOfBpYu6qgEsjTuW+RSpWL1PveIh2/RPlRL2j/1fIk1wbq9y1PO1+6AHvF1KeIf5N3mM2FeHuOQVlL4XQU'
        b'A76IVDCZJsAXqEIZVM92CAagnlkKi8JdqaXwOtTEvjtl7kavIOi0wfVldOa07RjU9jpqs1BcTkINqtjNH/RlPll2oTxolROTZCz1oxI1fjr0wnGquYsN1lCEMNdAVQSo'
        b'kANX2TKpdyVgFobUEEEFlFOoxgGUrWgJVKBTSpSNeLohQdlAeRzTTdeio6jQKxSvj/E4G1QXSRXjVNu93ig1kIMiqMUbEm/JY+iCTIVFvx30UvOKs5n47YmpdKFswyvo'
        b'rBLyIp6DzhHMy8ZYtgD79nBjIkOhGnSVgW3s3NjazoMzoaMIHlRtQOJOrUcDDOdeAaUzrXGVdnjj2MlsPX14zjwA5UCOijOHyumoOOHl3+kFw6hnHG4GyhLoazSCGsxZ'
        b'RBVcgURNgPOQPRmOwlmqkF+Hcghgj9ly48E5cb89txT66JKfiepw64nZvzc65rgIb3NCaKCQXs/M2aSyG3JRXiqxZodLqsRPyj1L9izVB1mL+0KmKt59g9DIFLNNkaha'
        b'SXjQCSjSxJQnW4uOIho4kD4WlwA9/pTwmEAWc66QialJ2Rjido+0bUODhLrtgQt0vCVBOOcojUKlS20xjYIiG7aEavGSL2TICbEfVBLoBKZJ9XQxq4UTQsHeHUSNBCWQ'
        b'HsoWZiVeo+WMVDAyYQkDk9AV1M+01D0+mkoKs9t1IQWtoKO0TFc4F4qKIqAMf8YvJkQSjxfbOuc8OGsa1kgM2XvDMbVci6poIzXIbTVebe62NhRu2hYC1cLBaFtK463Q'
        b'oNa48DjMoL4LVROjeitUyBrciHLTrOGinuWEoFBnUgmnlYx6zMYQt7GUbZkToW2o2Vah+F6y0B6KUG+amOMt8eZr41Croz2dzkR0Fp+BKHMXuighoHviqSIbVVLbDje8'
        b'V7NRhWQ76uY4G84GdQbSs+7Jw1IOk4DNh4zDNNfZpTHXBVpTaKzt9BJxWJyTSPEwaSU5FfGZuCos7nlXS/bw2VU0IvLmFwPCbMzNHNjDnalqHOatw4YTwmwk+m73e3eg'
        b'DCb5jwzuQS5E+xB/kN+jGckFYSKbJESOCnKUU1JEe+bTJjDyt9SXxkQlRKXvSV4Wpa5g56kRxO4NmNBNuG5HZczLqo2HLRTiP06M8++AKkSoDyr0vaDcSTdiIWqH9n3Q'
        b'PknFLY1Ej+5Fpesn4fe5DtTNLGTC1RXUROAYqrC186AQF8/1/rZB7uNncESTTSL0CRo8hxpQh2YYKjCkEdfx1FSgXEzGZbZEu6bQNaly01ah0xvF0LVRM/YdfbGK/Fnc'
        b'3XOZl6ICh3ynrjS85jS0+8C1w9fDSnjRhz7b399y1X1l2bKASslZk0zH6uNbZhfuPCc02ZbvXJ4RYfvB1OaDoqdUWzwbrDYuM9v7uY12Ngx9dPLA59ecfjj/3rszZn/+'
        b'e6LWxXoQzy+SZpWkz9fdJn9n50dtGX6lz6w3q02bZJCgNte+7KvbR5MnTX5TM9ts+seeiTYJMudf990K3H7yxE9lXy0plL/QH8w3OCf/3Js/8PGRYDPXO9Wm0GC3ae9Q'
        b'Y19YQ1tVpEnIdcegc23LS4JSfD+IrHr5XV3tlR+V3fw+7EijtMPsWnbJAXP3Tw3cN29Y/9Ol8JfVdzx5zHpezbCuQ2vBguReC9f1nq/lu1T+EiTOj1GT6k37Ur3v8uNl'
        b'XNXkD/zOyf9xct2GSa1bXyh4sezNF+4M7H5JviQ5bf/N/dWfvf7U7/tWH0noe1Xr20zNqE3Phf+q867zZ9bL31nv91PN0S9qTFoOvqj5TvETOdUDoUVf7x9sK0x+88fH'
        b'h9r6VxvsDozLfHnTk0ta0vxtn3L7xGX1Vb/06i/1B/zK8t7X9giZ892sr+3aQwI2WSaWfpmx59iXVu/s+2Rkzk3ZD4VfStyMLHvbj64O3K23xezK+/2vP5rY0+JZYJB0'
        b'Ji/jF5vakpqS8o9mfD7S+fRLls997nJq8RNu374+d13UJ22vJ995bKTk5MUupydVk1dv2lj13MfFT7T98HHpbzM3n7z6osXjpu/e7EvZZfLxx7MuLg0fNDrQkfb4Y0+p'
        b'LVnz1gbb+HyzT/e274rIeO6Nghufmm11+/7HOX3avl807TuvPbPz6sJ3Xzmx7NEjB11fO3vgn+tTh56IjXlvyOGZl39ujXwj/npR1y+fV3bnmQnvLXXuveNi9EvE6rhT'
        b'78V+3zPlWY3WpJcL5B8HXoyKCY9xSKqpnXlT61/Hn9+Z+/mP1uGvX04w31/6RfWuiBNfdOT860jbuV3Ta7QS39NKvzOt54fFH9vfcXopXqXjt89zdl3nJU+cz7j59um7'
        b'KsZGi46F7pI5Uw2LXYgvwd9CGz6+USecwzR62MKPqiJ2JMCAlODT1C0xb435Rz2iPIJWEZycCycV0EtUB+elVjK8NykISXXWVCEI+qGR2SKMQK4p3rCXD3qPIlObtlD1'
        b'jRmMGI+qaNFJ1ExUtK4oh2nXCmAAlSnV6L6QQbToW44wPWkB9I+iL0WodwrT355HDNGGaiLxiajklFB/OmWUVoioGK4VBVdoj5K87WUS1HCQ08LZ5hDFOtV6z4NmdEXu'
        b'pn6/FpchU/MYRAwz0U2L5YqAhs1wgipypc7s3YgjqhoLKT0gbEddMVT5q4eOhkopAkjYgkY28Mtwv7PpG60NG3B9l/WoipYoaHGTzlANrWU4FEvxsVk/AQSNSedF1uFT'
        b'3tChABaLoNmJ4YqPTWJ6/nxUaisnbhm8yRRhKuilwmloCtA4dxpt7sJJUEdB8TbEm0OX4DzHCa6gOqrpMsRiVv09rwV+kEeC6qIKN6bpqocOVDceCg216AK6vBpdUDgO'
        b'CEP9Y4DUcAEzoqcFdJq+XY7ZXjzOxOUAnikxDIQ583ARZS9i3w5A5e4xGO695rFCLGbtRtjbK1AwW44KPTzQFS+BUzVCdUmCFRwzpX06gNnC7nsAWqg/4ikEy1hsNdRx'
        b'EPrlMIhaUbFtElMTa2wSYBAv1cu07GWY8+zBI76HQkRVoI5HfQvRhWm7mCa9SAwn5SyGoj5qMeRneexjaMMSdDlA6uljLcGzMKIFgzxm7uugmO6kg6hhCZEF1O287DQo'
        b'NhXyoQsuixeheuhnSuPrqMJCDt2JDAc3iq81xAwzqliJKhWhisWcHKqcSdzI+0CwtqG0A5ah6NpY0CgUHEYnhZX+2+iWXLd8+1igm545qoKcxbSVDnLLcSGQoXG5wssE'
        b'1KEMNuldqNMBF34paiKCdydiHvgCIBtqSPhJsjkb18zkV6Kew7RdrkuhgcCiqbWJihuPMhZhdmoQnaft2m6iy6COIqiC0xTqaA9NDKtZMwtzx9ugyHfUvUORGZ2Nyfv2'
        b'j0EyhwSbo5qddKOvPIhXwBhsJGZRazhhPVyHK2yXDutAL4NHitQxS0jgkZuhl/ZxOVxYJp8b7ns/OBJlbKTVznJEp6Q0JiFkwTUZPwOdS6XTI7JNuB/HOH8SQTFCNypl'
        b'avaK9S73MIzGUGPgqM9oaTUq0CbGvXjt+RKwb9d8L2Em5oubGE08hft9SYGsFAULFFmpLmE0cQAvtpxxTlACl9tCDTDcNcpzhRZUtN7exhcTcsx78ZwUb2V03hZnoNM6'
        b'DCVYmikSVGwIH4by3cU4x3kBnQlBrQw4XpMEV4kwh5lGizRo4v2xdFVDS48+pGmNmdo+Pxu8mYuotZcUjQiYgrXztMfToQXKpFaolAzYUW0ffv5OK2bUkZccrTAAomM1'
        b'F/VT+x9XPEtmdLVrEJF0GNPbcTZv1N4Ni50yo//XULIJ6tr/3i/jLQ2C3AmlFvOU+36d8OL/+Xr3CGfIYJFiCpQkv7X5OVRNbsNbEeU2hRBq8Pq8LrlOpD8EUqj5u6ZI'
        b'kAjfaOhY8ka8paDPa/PGAlWYK+Iksn81hSlEHS4Q5bs+UapjVtmY1xVIfERjNW2BKNGniaZQ5TluiWDGa9wVk/8Ejd/pfyJSqiaNK2DE4J2CLn6yXzZRBU36H2q3lCqs'
        b'5Mvs7o0HkzLEt9RT0iOjUsJj4+S3VENT0iPC5VFjFO5/I0oCllx+I3rDX0c17L/gv0S4TDmRI/7ELW0Gd/fhDiNTvehhBwWo7W9JO6uhgwo83EJUq2PjM1thVk/csaBW'
        b'4nVHG59XSsc7e9F5Bi68tMrNS2Fn6TcpTqlVmAJnxFiKKcXSLjUaLNC1GtMCP08sb3LUi4/pEjGqxJTvBJZmaW1HY91JeZh3qx6tDK5iwZvUFudoOloZXFbeJI1Wl62S'
        b'astYs3rUbk0MwbqhYr+lu4+dh8/6PWRMaLgP4jWB58Imqc1GZ3WZNF6Dd/4ANQVfuIzadTND8EjVVBLGYjqqReVeqMQWM00baDnzFqx397QxhAraCZfZEg5TtmoKCJmy'
        b'dx8LOeICxSzqCKvZcsyVyDaoU9PZhUppp5w8nMaPzW44f29sgqGFdmqlP+qVTyhoo8LvMekT4Y2ij8zaqwbN3JzYsF1xInkLXsiBvTFRgU8nvLTCsOHE9NcuGsyNf+mc'
        b'7QXhgxDdT8/7/2OKeoGKeaSTRoS5ylxZV/TsNcfjFlZt6up1n/1Y3aSIVxe89ULiCrWv+JMmquoFPsmHnhv46NSSGZMLzNe1GLpG588pbP7w2lu5Rr9n2RaE11mdz25Z'
        b'vXDA/lVVx1tbZ057ssxwxT93+O2fdGum08+lzd9XPdkSXVT37YkNTh+blsN+Fc9/h275tNzE+kkXfvI0/bCZLssGS19IzdYuOXfaYt93/wiqMdEyqXEZ/mTFJ1YSo+dt'
        b'qhenRpTdeWajloVmXimWatCuwbRgJKu32tjcUvvFLn744y+rd01tygmW3xl5umJwqSy96ZV3Pom90FKRd8ta//K8yDZT55DdHraq8bs/+Nf6+jTt4/2rXR6/knqiMuVn'
        b'n19uP3bhVvKUX976rfVW2r8+tGp15TfpBCU4P7vlOXnZgX016/aVVwzPy3+/btsR05q6+pEdWeYrPgz56Ms+tVSHM067Vr2/bFOvR/DLl2peLI+6qH3WWMOgpD9T5ZPh'
        b'wbC3DGsOLW1atall1rfPfJb25PO9qmF2t77Z/FmRQfKPgXkXnKfFBD02pVT0vX6h37fZdfurVt/85YTG9nSR1byQmx88vvryyQuGF7VTXn9rquuFSvfHHX765auoj9Z0'
        b'vuz+em1fh+jjd190nV4Z93Pn17+GijZ9sk30+is+B7ySNDYZbfrglfLqiF1ffHj4Rl+/0ZwXC97oNDTIjUu6O+Xrf/z26YrEMOsntIyP12/UOr01MX/jax0w+Nj8lNVv'
        b'zDh+/YBp2ZsFsRFn5vie9HvL3O3mIWufVNXnpQ5aVzotf3rf+t/xT5e6VJ/4Ur63ZOv593ec3ZHac3XosROvLUl/3HtX8KDFjd0Hh15yGjgT+P47FYHfztg5PKnzlfTJ'
        b't5eedXeJfkXklBaS9aN6U+TrM34pXzrnnaLll3S1A74OkTlQ20hvP1SjMIB7kF0kZgw6lbaR0KnHDHNPbEcN96wxL6NiPWKM2ZpEmYW5JnBmVKhcOBPysUw534ZZqp5E'
        b'tRZy33GGgBv2idZ7oUbK68lnSJRiXwwMGmCxLxC1M/vnSjg7dZypKORpjvFJtw1aaA2LUSeqUDDb67co2W3Mau/VYNxkHiYO172gwVjpJzsaHaN2jmHpUC4PJaUrDB2j'
        b'9lFjQuIyh9zYM0aF9BldQnk+zP0NqhLDpS0KT2eYXB0LkmLBo1TROamBELuRXL9DpUI6hZF4YnuehGp0ZJgD38tjGXBkF60f84mWqFWFmUISM8jofUwEhCqUK1c4Z9uL'
        b'32rsFQSUA51o2JiVOgQ9UKu0k4SczTb8ftSm8IizhXiwlUJdgB2eQ2ETv8QE820U33Z0p3GaXD7KVJutoOOXMh9zdnRmZ6GKlHuGtKgxhFXWEg1H5VaUUIqgGprQcR6y'
        b'tI5QEWI69HBMhoCqxQoxQiFDOEArE5TKlq5mEoiwWelsAxPhLiavXo5cEmM80f6R2D6KnenCC3AhToAIjwyNcIXyyZhJ3qv0jtSDrm4nEgHKnat0b+TtwnjN+q1oSE7i'
        b'CBD7VBG0a8Awj+uthzOsWUXzFxLr7RIinoswo311KxZnly1n81qmB6ekdj7JLEMKrlbPcEqSaBfKcmUCaSbKVSNCoyyAiNl4yNS0hEjUsoyy53r+thO941nASTi7azPd'
        b'f3BtCk4V2T8YPnEYzt9DUEDeEoVfH+/98nESLKrfh4XYQYUFvJkzGmYy7Ao4qhRjL6j4sK4SVyMXlLLqILrgiWXVA1hoJ9sjSQMqmEO2xLkKL4e+k+jliB80o56J8BPC'
        b'imdAA5a4c1EJK717C+pGRV5sE/sFE3VnxiF0kr5cjTp3j9rOZhN3T9TV+h42RcNrpyxAvRPAG2bi7U4mTEQ+A0fd78kLa6Dbi4pnPGccJTaH/gQqJ5ltOEQMf23cZ9Il'
        b'qrZYiMD5R6jjpf2oSZe+ZJwM6WYLjFBOxtRYjDrQVSilEx6ExfGzbJXiKSdOujS8BXtUC8f1dZgLp+pAwtsRRm4dVNpCwVjFi0OwxGAhlthJkAg7NIzqHkxd/Y5A0ah5'
        b'sTnqYBiRZsiADgVfgqW6i4xzVOW0g0XzoNOO+VDrmaNLmSZaL+7L5XtKH5SvApcgdwXtx2wXLATisvxQATSvJ4uLFiUSzfQPptPtEYnaGdRmg4ctQ9rEG8n0/x/KUP9X'
        b'zmnGOp+xUBrLvPznpKl4TRr/ncg6+D8spxjx07DUMoVEgifyDpZ6jKnjGSLp6GOWn8hBRNYy/FVNdUYylolw2lA0BQtWJFY7yYeFgrsClrgELA0RbyBqvDaW08gzieKZ'
        b'hkiCpSvhLnkqEakJaiJtkSY1g5YIRGojZsi4PhXmdl+fF+OnpD0aOO/9hrxUilJITMx++Lf/S8NkhcRkP26I3/gLdi1n/4pVMu0MMRwzfmDs9kmhBMq/I4WJiaEEt08i'
        b'5tLw7TSaO43hfhz/uqWqsNC9pTnWYPaWdKzpqiPJvZx8t5v8WkF+HSL1qI9aDN5SVZjx3dIca113S2u8VRuxoaIWP3R42GxM+t/dSdyzWXoLV7+IzM5hjjq60RYLNvyc'
        b'CIVrGtH/6F+xpkhTREWrVMwAXJgoDBPXjW1+qEEcNXXtw43D1nAcc8/CjcY1Vh01FBP+vqEYOWFsuYmGYut8U/3x3wfh1Gwnh/mOC+ctcIIrmJtqQxkpKclpSalyfAL0'
        b'YH6vF/XjQ+cy6tNR09TQVteSwjHIx4JmOaoK9CcOQoNUOHQeDUilaBDlU1cDqCgWZTpxnJUvN4+b576a2lkk7EMDTsQFKGRzjpxjHOplzgZy9sNFJ4FbBIWcE+cEedap'
        b'ehy10WnY4iTh7KGPm8/Nn3uIFuy9fYYTz0HpHm4BtwCKnWjWxHnQ4aTCbUbd3EJu4TxoYgW0oso0JxGH2j25RdyiHTxVQqMaVIUqnVRxdY3cYm5xGjCdPMqywJ3qo9YA'
        b'1Zwz5wwDqJi2bxvUrsNsNodKLDkXzsUBrjFPBRfQeXc8mlCAjnOruFX70RmaXQsKkuUC8Z5Wwq3mVtvCcdoaN3QMBuUSbi9q5NZwa/ZOSiXu67XsRXKe2zmdc+PcZqEh'
        b'VvAAHtsTchXinq2fW8utXWdB80qtpHIRB1dTuHXcukM72Dg3ObvJMYMk5dw5d9TlyHzxd6FKzJX1kTsQ1MJ5cB5Wc2nJNlC1mqhmUIUq58l54hHuZGNSgooWoT7c6Et7'
        b'OC/OSxsV0DZ7bfZAfRJuORrivDlvH3SOFV8Fpcaoj+eSoY7z4Xyw0KHA0V/CDEUR6lPhoB/qOV/OF50Ioc2M37AX9Ym40OWcH4fP42A6ULug1hn1qXKRCzh/zh+dxuNK'
        b'l8PJSUZSomjCta7n1qOjy+hj1O+/VSomsSMucAFcwFZopY9V0YChVODgYjBe0oFEtcDaeHQbKpJKyBC2chu4DVj2ymPTfAozivlSnmC8rnAbuY14oOppZ6EFNW6XqnDa'
        b'9lwQF4SatRRP5x+WiritUIN33SYoCaRPgz1QsVQVF9vPbcbL7mQam7gCzCVdhCL8V5U7t4XbskBMG6ODTqDrUERCdwVywVwwztfO4mpcgVOErxQ4Kw1uK7cVCzYd9MU2'
        b'KNNEFXgFVKKrnB1mpE7DCTZTPeiyPgnesQoNcvZ4bwy5s2bWoZoVgRwnRpeJDZOLLhuzOutlqILAsE5w1pw15CbRxxsDMQuHR2B4L2fBWUAFNNJJgstblpKVoebFOXAO'
        b'zvtYn06gXGLDhVfBHmKzkYSbTsowh2vzA1WIM+Vsbg43xw1aZDbUeGnN/mRql1BkbY+ObbWxJsG0RJwBahBhSbI0hXm9uDYvjL7Av5wXiiArGWe4gDOgsnQaogJv0bZZ'
        b'ykJC0YgiCyljHvTT6zPDSGjAn5MMIp4z3Iv3LymgA7qp641wvP96lA2JPIAz6eMCinCWZDRMc2DyVY4qWTPs4TKe/mMigTM0wFnikui9YKKhEfveHl1bxN7y+O2UONbG'
        b'QhhGGYoqVKGJNLDoIAyQfjYmKK4xBVSLa8By9ymSaRYrwDiNFXAaLporO5msjxtnrhyGBqimnQzy3oY/J703EzgDOLuGDWMO3olUd5GLd0kdbUIfiU1zTDRL0UlP1MMs'
        b'qIo3y6zZK2hayhmia/NIB1E2roC+77daybqAm+Exy141AldDurBAO5XhF2tRAx0j/N5rub2qPuuCCQzSw05zBxbRiuhEWtvrLGMZRYpuQBYqYxe2p7BE0UZf4We9cCwd'
        b'/xrGAwatpDFdqnTl7EZX0QjrLj5yBnRInqXKERmcxEzjOjHZzVXUiJn3/dakxXRUUBFex+S2ZCbUk+BZo6uwDQ3bK1chGZsA1EFnZ4fYksxN/gIRHEW9yYq3u6Cc1uS8'
        b'lBqzFdEG5QeQNiUrxgYLS73MvPD4NKhTDO/mQyTLUjY8cG4d9cgihRzIH20K9E5WhebRbufgmsgYJ2PCpxxi1Zm4GZfc2fCVOtFFIKBrRK1P3q4iyyAGH7mkw+L9tKHp'
        b'0KUc20ziroV0pCIMqkgVl1E1G7ZBvARP0q7QPGRYh/HyJcVsRteYNVALyosYHVn8c9STbi7FuKRAFp1L1ORHnJoruoSO+cQoctGhMVN4OcGll5lY28dhUofrPJrMhgWv'
        b'+Ay2cOuCiItm+iVkkhYfg6u0025Qz6znumYesLaXOJMcIs5wEX51BErYxi2DTImimSJXTSw1DiuJw047mmMFZK21ZnOOTs0nGfC8UPJwEs8cad9a6NFk9VtDX+S9na95'
        b'gBbgo4WyFVOftQYuKVYrHYcVC6g5njdqmU+bL5hh6rMa6um2qplO18VkyCaOh1kT1Hn8XQQbgIUog2YwiN+u6IA1VNqooizlOo9S9PEAdOOhoy1AmbT5cBHVkiK8YYgW'
        b'ETB9P9t2eArwgU+qUGyVM6sYkS1cHDk6mdtlePEoBwmdYnPUEAnN5OXOtWRtrVZ0UAdly3hmxHoNL60LXjRmozt1tVqqCxcEyNwZ8BHlK48nr5BpUHM7czURJ+bCvNS5'
        b'ME333WHMBs8sQosz5r405P3DNHekHmQPR2arc7pcmKpGWFjc7zre7KFEW5+bzeXHqXJhB5evUQRomikhxn75wRorwjTjXHawhy/raXPT8OkkOIR5ZwUGsYfmyyWcJveC'
        b'i5pZWNxTG1LZwy1GepwZt3mOsCfMZnl8MHs4f4cGZ8hZ+nC6Yd5xnkbsoXoUfsR9uV59RdhS2/0L2cMTxF6fS9dWXREWt3NFnML+kCNGiT0ybS7MpjZsNkcNqwMSJuOT'
        b'sceABFnau9MLC5Ab1tIXu5OIxfXb1rjcuLcjjFju+AjS1rZdErMw729tXbmP6mrJ/24spxX8joUBTe7tfepmYTZyNSfuIyf6v2+WM64mB11KJoQMVWDmMpFLhLO+9OiO'
        b'sZhmrcrBdVsunUtHfXrMtpkeMo07yHZVrLUW1TFrDardaJ1ie9L+R7bi0Tv4uY8iclTWQjImjSu4FWHbKvYH328/OerDjOyGGIUFJYvldC+GkwJmckslNiEyKj2ZGMI/'
        b'KIiTDpbamekkCf2JaUEWNFr7EitiapTo4+2HeU6mPZSg9vvDYZE73AuoTrpySyJtvP3aLVwPtzlQPSzM5TfbQ3hGfH1jv/t0uyDfiCt+e//HPgFPJxis1L1Te/na9z+b'
        b'xHz23axhcNIVFh8Xuz+Scdds0ZrFVYKnf3bDtMXfnjR67P2MS6aPhB/6wCn5Q+niPW876RbeftWsCO2M6egcHPSSpnq/8OXx1TNUfrRszuaiNvi7aaXOd8ib86Fec85C'
        b'85QX3HQO2bw97bn3BLt39Y2STDbtmXRzz/RFPdn1V3OiXn/8qZtRqxcmunZ+b/lKnmmXZ9V35z75d9+bp65qfP7Oc5MbrskvXFq/dqv9s3430hc+MWXvL4bWFeiansX+'
        b'ufP2fSp1ua37kfPkgLyewl8+Nzpg8l6DbHjme1Kvf+xas8Q1MHK5bc8TKkEzk+Y12/lUNX/lt/RJw6nnZhdykU+9ckXl+x0f/BzzyYlzsGzTYGTHNs+XI1+65rDH1fsz'
        b'syc2Br5ndeIH1/bM3X1bjxs57LEDS9P5ix8J3j7fuKtiXX1l21dZYeKfW84GNnzavtwi/KbK1uUozje6/WmbqU1ejY+mJrzdFPeC5fMbClyWmpyeMWn6F6a/rD/9c2Ta'
        b'jx/2+mT9aHPU7VXzPVu/fH0k3e/we0nNb9599NzqvtjD4da2SQ4bz8n6VBOqTRyPLTBIrvho7+X3z6ZpgHqIZM5jHbHhT18aqK3+KntrYHzw69Bx9faNT9cc29QTab7y'
        b'lMbQrNDWXUmz/zVzbyREdzl+7v/z3m2flL/43qFDQU/4/zvk3KV3O15P3brDa6l5aU/lRd/H3lO94qwfvdWw9liYgTM6827MrY3puR+ZFr1eHXlzW57ewIYvm33OPfHZ'
        b'pV0FBz4/9uTSGJtO5+J/nX+l/LG7MfXbYq68+mPKr4d+1ToTb3XtN+nnbv/M/fJZmTZzCiOCUurzungjXrUqnMpBHrVAK3TSK2AJtMdhgpsfxDxFiN15vKprURm9vHXa'
        b'FedFQwx6RaoRV95SVC8SvAVms3MsmhjJNWFmrw9dwaKhSIOfZ2tG38mgl8f8ZwkqhS5PFU4cyePzAuXRChMhA/qIxyAPbz0bDzEnTaOBS5fQtjrFQuuYwDxDS6mJ21WF'
        b'zc0cfOgVWnuRcu1xa8SpPCqAa1OYriFvgSlqgzZrGtBGgD4+KFJxe4xZkRFowLxY17JR+zZi3AYnoZHWughKp1LkCBYdrlgRG3QJZnDQ2QO0wQtQQ7AXDIdRYxpc62Ri'
        b'ZIh5KKokCsZPL6FmKy+l9mrrbqY5qYSBbcSrEiYXOaO358SrkkGibOr/1k7m4deKqn/xZveWhnxHeEJobHx4TBS94B0hpPfPmMsc4XzECn8PD/4RfyXRY14gNKjZi4bI'
        b'XOGDm3nsNsRPJfQS15D6ojBUXBnr8vrktktkiP8yo/7JNaiPcDVeLIipXwnq7Rv/zKFxVDVoivgXN8dfOPLJGoLyqlB0SxQbHzPmzvZPDo9UUB4cpKwhdUXk0T9xK0t+'
        b'njB+uCULZS0bt4fRg2eB5ejRo8IZbRerodwF9/mN1VAegZ7cqN9YCXWwzJBdQrTGqL9Y8Z/yF/vA2zuCPFDj7vcY+vB7ROLcHLdDiBb+Bsx054NgpsJ99av40qM21Fng'
        b'NOOo+1DvvNX2HLVdQcPL4/Fe7V5FIqR6MZyipbtHoDvZ1h4q3KIDEkuUD1dit4rcRXKiKlo4afGnYe7hz0RbooTy22HbHuk5nlnWlD0vp732YsHFozNrMp2mc4kvS17z'
        b'TpAJlFLMQ2fgkhf1bIP6lpDYo0uFyeqYUhBZxgrVL76nL5+HxdDxkZV7ZylhHQ+4Ub4l3bEzasfuUMqz0J3n8Od33hHOknnv328aSnwphxJHDPcsvsaUrNwHfOyYXSCM'
        b'W+xao4tdE/81SUNxRfwnF3sG95n2w5c72TVbsGzRTT2duUOx0tXYRDstgjnyQaWY8YIuKISz0BJERANjKWoIc6aymrN7qJcNCbxTLOYkUxxQtaABR1Xp9dHO6dBujcp9'
        b'BU7Q4x3QCW6JC102AzNE7m8KNGit5kD0dhJFlBw6U+AY1Hh5b4B6X1+CaVPzE+QoeyX9pMRDGjAV86SYdbdZunU9Jyf3Xj+seztQq+fXPUkiEi+H2zqd8tgvBqikjfC6'
        b'BChkw6ljNp0M8AfxYvF+gU6l5qvGj9nf5uTkIqtfSA3cmPrdXhEnUtGYzVssB1pb6Vzx/CqOFqFpqeHGyQnb+upFzMYRPCfmNf2HaD61A5LtdTwNhxpXeUSRr6Tp7nsq'
        b'BJzcYqddcFBOWFyLl26/98Hjm/DXczjjShM5YefTWzIDN2qlae3ZMOMFzBzY8pWPzpVTDOdrG63tuhI8bKzaLYkNh8FF0fvdT9OjgaK6b+5NfUlnWPeGzQ28mVR5wfH8'
        b'FFrvHN2zL5GVw7V/Lav/mD4y1P/1JbyarDjDIaufb9BHL318owiTjhBuRC/kXDBt3VW1Z4te9CHH87tczu3X6LOnbhgUvXjLCX/8Hpf7oju9Mlm8Hh/ARR6o2pxiw/BL'
        b'NSgSPOcciYU3DETyS7jYJQmn3QJ8dr2xQrM6eun3xW897ffSh6+qu1bFrvboe7Jj3ZN2Rf+8pjY/94WrtilNmRmBjhd0P3HTCQttnCtz9tHxj/210TjuK4+3Wv16Zzw7'
        b'a9vUVY46y4SVj72vNhJxpKxDvbw+6dPy+uNxpYXvS36L6Gg3fmbn4bqdAVfnxc1ZInIukFqdvmNU3rb+uzdOcj89972rKIdf/+WNZ3U/O1E+bWvHVmNvm81fFQZteyb6'
        b'kdv6PWdSrRM35lucuHSz9ne/x394LWRhp6mlb97Ah26iiwEW5zfI9n//vovxxbdsprd82JYZMvnG48dPRj4/OSFZK+6Nz3Z/f0O+oLHtp2e+2db7/Mmzv28/KH7qtx0N'
        b'wwk5ol+MgvOt23Xi9v3rka5vXM67mTxW8PL1wMv7JZWfube+VSj3b4hdUPS83/VlGqeeevHbxNtnfy35xzed/5CfmpuSE/2vSdM7rYNjTrsURUzVDjDpXf1GWFDrub53'
        b'f/li5+eOdsUO777xzd3f9UxaF1xOsbljsazpWbs3z7xk0ld/6Lvft78++WtNo3e+v21b/OE3H9S+/fNBrmHLtMNeaXttfX98+rcNLz2aHFi8Pyrgu9XfH735oefiTboz'
        b'fucDKxqP+/4u02Uex/bv9pIRi0MJJ4lBFb6CFd7zV5h9whl01hqzWJhIVHkxeKEaHBcSUe5m9mm8NrEPQQUHfGywRDmPx7Qi34FxZ2dRNuRiyqIBLcQlWQmBmKlBk3DY'
        b'N5Cq/TVnQIE8JS1NSxtKdVCLnQ7q1cSSsxE6JYIGKAujdiQb0QA0W2MeNwtl3ONzUTUoHNZ1QCemW0U+0IUPK8jmVdD5dZugRGG2gwXKYmtPBVMpCdCAfMFwnjrlc9Wh'
        b'CV3GrYM8r3ss5zZn+mGcW5y1J5TwtgreWl0qQAU6b0U/3LWHGLYUyWyJqYUkDI6iCmGWqwllctX0oXMMtAROoxzBCbeRhY4So7y1mAVG+R7evmgQlatwUrgooIapCqP/'
        b'qVMFLw9ojvZRDHSIELXCjdYZCy0eXkpvbpKlakeEyYSAM8DR1RgxRd96y/D8LYGRLYLhNtP/Uhf+dyyOx/Gw9w5BepJW/5WTdK62Co2RQ7lUbd6I11X4LNOl/KdY4cuM'
        b'RKoh3Kom9WqmSc0JSE7iA40YgutSTlcsEINvMTP4pt9ZUh9oLAqNGp+sPcqbqtwS7wlP2XlLHBmeEn5LPSYqJTQlNiUu6q9yq6JkXVKmHvmlM3qUk3oM//JR/vmMhx/l'
        b'9Fp2BM5o0qMcVaOme8e5KmfkIzaEhtk7hDHsHGneKLdIPK1RnTMfLRr1QiD8aS8E2Q/iF8Xc/W5J8BlPb6Quw1EOi3AEIU5uFj1URNM5fbgiQllQODnWap6KWE52iVvt'
        b'1U/Dbod9EuYdfidKGqUR/ba3iJt6XBQQWj3GhYnooYYBt7TIxI1fflZ/ZfntTNYfXRJiNoF0Kh/MrQkT55l8vPEvz3O37sPnmRDLBetms7GjPNsmuDY6zxarVTakrfzf'
        b'TrPovmkW+cZeinHgaTSDffHffBr2xSkyh3HREZHu4Wp0Dk1fFbl/kPQn51D+383h7mSDiXOo+0dzqDt+DsnHm//yHHb8wRxSb9Znt6ET1r6js2i+/t4kotMqYWrJD59F'
        b'YoKUR+aRzxNHi//GPN4n3pE5vD8ghYYvc4ZyzB6aKHO/JIax94IGytKlrO857RnCQXGKDrfnnSPppm+k0YcuMwSuawVl7G2S4wzZZTKnyQtvi0Rq3J5w08JpWpzCXQ4W'
        b'NWoCoZujRhmNKJuj2vAa+kmHpyrXoz2d8NXe+iGrONaaQcxCVAZiEmftbi31EHGSLQJvvCA250tOLE/DGSxuLpv+zJCWME83+7jnO7Vfua4RuaescFYLgCrfQc01V0u9'
        b'e2a/HBYoG/G6HurUVJh7LKvJc8eO8Me9tAPLzho4GkW6nDoRktc85Nh7csGrt12atRdeHpk946PzO0QXbzrvf2PpP1265WFN3zxhPfLarMTFw3ffypox1dhSpkYP5/VJ'
        b'c61tLd0x/R2wFfCxXyfYostoiBmNZ8wwJTdU+ER38x9lnqqhgTI3EYsJV4WJIWahdun6Ef86xZiJQaeZ2+bpYaiZXdStRMdZEG1hH/RDD7tx64YLqBA6KXuDatxRAU98'
        b'lJtDJ2JxfQ+j06hR4axFBY+xKr1xkwLzfD4by3id1u70ykxsorKIh/OokRmso/JU/zEwVXQRTtKrvGFouW/P4t31oHPw3k7WJNR4T2R0KDlaBeVS/tMbOYEYFWqT+yXK'
        b'CTDPpcmGYzY3WdS3xBMQU/c1U0ieRL7ZoWwXLWLrX97irfoP3+KzydC1kmiEjFK7e+BzmQ2wKWaFO9AxMTrnD233UVN1xb/yKRNCoFWKKjUrVaOFSKGEp/dLwj3fQdFq'
        b'kaJIcbbaUT5YHKUSqRIpyeYiVSPVSoRgCU6r07QGTavitJSmNWlaDae1aFqbptVxWoemdWlaA6f1aFqfpqU4bUDThjStidOTaNqIprVwejJNG9O0Nk6b0PQUmtbB6ak0'
        b'PY2mdUmYNtyr6ZEzstWC9aJUorlYLkrvKNfCl/LBevgtuU9Tx2TONNIM59CPnEkPIvNbqj7hCcRK8WfbccF2SMQus3j2ioUjGx+MB7OmhLbfR13VleSPeJ2kDpqo8R0d'
        b'YnJeqo/SWfGforOKsE8/H/2PMZ/GtfhezKeHRVgie4cFeSJ/kVhO4awI/zVrzaJj4x4QLmrcKiMr/v6rxBm+qeRQRX3TUQalBCQQjJ8tjchivxEVrHeHbpRvY8dz63jV'
        b'ReZQTMFhc4NRlXRPUiB+E6TAhG1QI5cZKN8nzEwZc3eHmZomGvJgrn7Oo67tSl86yyBzFg+dm9BZehr4G69SRtOFXNROI+oKB2DIjBladIWjAmtPH3QmjLlbt+Y5g7ki'
        b'VL8RBpm5wPUDqNzL0TMJVeKtiC5w6Aq6vpIqTaXeSSRoNJww5WnMaKhBJ2iVOyPRdS87Tx/qnl+aKKAhuI5qUcEhWmVYiCMNbk9Qw0XePqgOGnhOG50WrdIzo+pzAvQ4'
        b'6wXd7j52th4+81Etz+nMEm1GWbG09C3bUJZCVPOBOjhJyPYV4cAuU+b/KWNtvJeHjxV+vQVdFeg1CmRyKcztVDmUQt/YgOgyLOq2WiWxT9ugg7/n5WHkEDrBQ/2+nUxD'
        b'nCVHw8SP1kxbCY33jc4fZmWeCEUjo16yZkShAaJZaQHmGQgNuRMXb+P8XC1ZMAmVL6P3aaYB1O2O2dvRUd679D05qnPeY4WGAtMInzeTm2mG2LHdE0OdjJk9YnLA5sDS'
        b'5ZyS5++By/HjPFqhnjCeMycerczl9MubqSK6Fx/RSvae4ZPMeAR0HUqgctTHls1KaOFhcBbkU/sEa+jYcM/JFipeqAhoj2oYwhKVWqEe5mQLTqIenlMnXrawOJ5DvUfh'
        b'yekWrB8Y0Bg1oAriBGuJIzNXyZmKiTleKlRgsU9FFwW8FBpFIVAG1bG+n4hEcnxoc63tqofKhwKQg67b3g983l/8xRWV62U6jS2tZ5LOeLyTBTf8b2glVApzToctOji3'
        b'syT9GS426IfP73zySfqdG7svTNnYPXz+UfBY/tnBC9lG1z7/ssWts1FnaEfExUcnf1twU+uVt9/ec2R256rnM300f7x0+6dlux1fMFvySnf/NbvbG1JCv11xyajhp6c3'
        b'3Gq6o3nGdM3ywmVFh98JsUmwHDKY6tj6T5PUzWeQU9AXaXe+NNnsun/PzrlzXm7PvPaufE7Cc/bekZM/+3dGiPHOmLTYTQ0dVU/8O+R6RMO2cyEBzzRoyLuMuhY2Vyd9'
        b'/W5Q6Rc2rf+ou/5uVeT5re0DG1Dix3lXst9IQw1TRdPN+27Eb216JufratmNF7dsTPT28G7vWPKc+Y3mGrdyt9BK50+vW36sahFytiW0cl/Lr4tqPw3aZfddhaPOkLfH'
        b'W5VRc36I+tX+XM7FL7mjv6mKjpz4/ccWGVM2Qq5LuJI/WbSKuDQ5L0GNlG8yRsN413tb2bHX0jgBahcSWMte5lVg6IAeKsLMK9E6oAw8oSRasHAoJpYCtqzR4NyJsVDy'
        b'4NoasRo6Bi0UdhPksH1ChAZ7Q6hVqhF2ozZ2vzQARZBFFEaUtEnmamAu2QkxNzFSVIsZpiL70VDhUrkQHoPqFiylOs2FcN0Pswkc1DKV5jKoZc46RmbDKRLxxGeU4Bmh'
        b'U7v8xS6eiEXFQM2YHS6HIj9HT4ETxWGxuosPSkc5jHVrggY4RqNPePOYSpyGHkxtj2MSd5IVfxrTukIWoATTP8jE9ICFKMlDCgcEI5NwJqIEK0EX4KiSDvKc/iIRNE02'
        b'osXYYpKOO+4H3Y7QxgghznBABFeCoYAyn0lrZ9BWUDqIO79e2AbNqC7EgDZzDxpaSUI9UEIocFILAXqhFjWqwDnGNl9DNfwY3w7nzUnUnlmIxYHetwUzWYoAG4RsLdQT'
        b'czrqohSUs5N93b+MgMv8FORDEjFDTTDBT7Lo9C/aRkPK4LIHoEfpqI/TR2dFKFOuQwvYsY6n2DTqpU+Kl842qEBXEqGPTUCeHpl1P0anw6IlnPZq0drFB1NI3DZ3dMqA'
        b'iXjjCYwagYcSGrMiVVWPU6f9SOKYpYsiUH0g6lDhtGNELihjHR1lIwlBMvnZwTnIVNIggdNfLIJh6zV0kTn+f8y9B1yV99kwfM7hsPcQUVEQlQ0iuMCFE2QLDoaDdVgi'
        b'IEMQF0P23lOQKSDI3qu5ru6mK2ma0TZp0z5Jm6RJkzZt2qRv3ut/34elaBL79Hu/8IviOff9n9ee7tuYjKmutSRqaqnJQKfjRjPZp9unFJ835WKx6cEEEyq+rgh/R6Ck'
        b'xFVv4DOQFIS8cY9lAnENsbkfVhKW5QUpiUQk4ssJ5f4tJ6/DZQUpce0QFj/nf/4lp6DBOau/6TtKwlQNqRD5eMcDaU6R+ko7gcLXtn+K+Fe3rziuuG+sYpTrPz2L6Iml'
        b'f6361GGsnN2aZ1WR//FCINbSDIsdDYy4TgJSUXWpsv7ztTCQFvCWv5QQGR7zjKYCP1tYED/9QlMB9lZQYlL88xcrF18Ktg1+6rQvL05reiI6KNwwMswwMpHvZHrE9sji'
        b'KTxX3fL4i4Jn3MAvF2fW54qCx0tCIxNj45+7dUP8O8+679cXZ9sknY3v1fB8u5PWP1e8dCU2NDIs8hnX+uvFeU24Av5BCYmG/Esh/8kC7i4sQJIiCUl6VrOKtxYXsHVx'
        b'AfxL//Hs8nyC3NPnfntxbvMF4EpchloEZfwA/8EKQiXBBDRPXcH/LK7AgMMq7unn7zoQvnDsC9D61In/uDjx5hXQ/Z82PFBctCw9der3F6fetlx/Zie/oDyvnH7Z7Byz'
        b'ezy6RrgYXSPIFWQKbglTtW4KOLOAkDMFCG4LfZb9/rSazWzoJ83oCs+I7nnOEvIyHICI/+W7aldjDhKTIyRc6+fECNZjewke4yV8hwqu9XJMbOKTVoYnLA0Ll/aEd6Dw'
        b'h/cFXM+A8y87vc93DHBL2CYvUMgTjpUFmQk5iScEcqJWCr+7oIbkX7GDD1Q9pXb9zYVEaAYB30AouSOQTzVY4HaLO10K2QkLlyR6PL3oPZv2I8bcGe/72sw9TVDx9OL3'
        b'SftoJAX1rTi8M0UqE2KVxeJhYNnjETpcQCTMyinDLLTg8H/NB/Q1Q8Polv/hNivD+YDubMpkXryosA8CC8OdgxTWWnM+IKMxmY7Xkui2OevOuAxWLVy3zu5FbUfsEGT8'
        b'VR6i+NvPfe3Kz772BEkiP02a8LFIsXTh8sn//hyXX/gMDxG7fLcUnMRhmN79ta6f9Ax2/ebKmKezUKHZxRAbebhIdROrC+EBvVTPm8pIVxvm39mdILYTwjDcx/rI+NEe'
        b'YYItff/RpszL4c4hbkFuQVG/65JEhEeEu4W4BHkECT/Ru6wXpefj+66NrF3c2DgJ/wOTCn9NH3wilm71uLp4iRRauGm+0VXJqMiriVI1n7gufvDMxy9o5ZQfPscFVT49'
        b'cm6VZTydVnPuOr7iv2DRXfdNKHYYUWz3J8jtURZGmMBLDkSfV1qREwwTEiOjow2vBUVHhn6FQVgoWI37yHmcPsE77lxvpBYKmFPU8Nprws9FkW+dSZRNuERf3N+S8X7g'
        b'T4JN33FxaAlSCfsj/W6pJVPudtzbzC3wYMKgbmmo2UsZn/gpuTn2RK1zqI3Sc9BrqMvfH6WnO2AdKsi3sQwM+L4XGr5Q+p0maPyxt478SzK2NXYbBS+9q+cod8VMgeMD'
        b'x/A+PLJYcqA4QYNADcZknOAelnG0w5ggu5WzHGcyXzgzsHCWY+yBEr48zd1DSZwdFiawkrNBcHZYZ75HpwTabiyhVgQMSO3KJ6QVe/RgQGPRxit0xnHOxmt3nIvToSlH'
        b'zy+0oBBquEAzlCRwrsDbG7HCglD0JPSKBc5actEiI1pnH99Cl4Wru9I3lnICsb4QK6ADhiAHB6Qs7Ss9aQqRCZe4u+Vw6dg3xSVtvjgi9z+L/eaKfYiX6ZQLwy9jek9Z'
        b'0xIXtKZHP38OPMt5uh9tlQWZaa9WI2NZMQzOrRfKDkmGqXfskuK/ZLUxFBZUkjcUFnSDN+R4MfsNOV7+fUNhQRx9Q2FRmpQsbI6ncf95C8pltEmXfr3MzowtWEEkllER'
        b'6gf8t8pTqClriPi0wCKYCcNh9wUHjZIqtEIxq6o86v0Eb9eS/p2Q/bhHUq5Sr1IQKipiPjr5HNUcrRztMNmv74nk3yIhRDlU5a4C80Ryvj8Fqe9PgY0fqlok5GLqlWls'
        b'cahaqDo3tuLid7IkA2uEanKfKnEr0gvVKhKFbuXe0eLe0gldc1eRvlem7wXsiUp5+tEL1S2SC93G1dqQlfZgUc1Ry9HI0czRztELUwldF7qee0+FH5d+FCoVab0bimRC'
        b'jTkPrCznHmTthdRy1NlsOTo5a3J0c9bS+xqh+qEbufdVpe9zb1fKh26i9024Odmb6txbuvSGIufjZG+ocfvbzPZHOxCFGoVu4XaoHqrNiWCmb6hJEYP+CgqXxP9uJ13O'
        b'CjJ/2HDlE4w30N8JhkHEFpYzC+aEDEo0DIpnFp2rSZGEACsGCiN5n3s+lL4KSWSaYmSiYWJ8UExCUAhTlRMe81WeTCTmExsvnWpxlqCERSWLuFaMYZBheOQ1SYx02Nj4'
        b'648NY21tmBwUz7q0OTg86Qxl+ttjG1xkekeOnz5sbXgsNsYk0TApQcLtIC4+NjSJW+7mle5gqaUugs7vieSOlUVZFguysKtfLMoikyvztdI6pP7g3/k/flHckT3mEl7g'
        b'41cWtvZcXuHFk2VKHV3v8utYVXtjMMBdXai14UnO3BUaSysibc9QkhKZkMg+SWYnHCy1E0lWkS2kC5Kq8/yanlDykyPZIumbsCQaLig0lMDlKWuKCaX/DYPi4mIjY2jC'
        b'5eawrxBs2HU+6elW9UhixY9g2okkAlbPrliJ9cpgBVOdF917WI5FblyBU29nN4+Fcq8wjznK2AHFMMV3u+lPhnq+6OrjA9BrTlgo9d5ewxzFW9COfOMpf0sFkgygy9fD'
        b'ylkskDURYi3J+dVcSY0UEgyyLaDuHIFeCv2r34Z3Plb57faBBmy1wk4cwg5bgYy1QH2/aCv0QDGfblOsEMs3BVtItWE+fC9vK9bU/KxIsMdMFsoUsJYvr5KO7dhpgV3h'
        b'ItYAJcHXn5P0jI/w7tffXgyzdNl9QcC5+PdDJpYv+j2xXHm7N+ZyLceKLLHY3ZKrMncqVh7TVDGf8z9f88fGhKuyrG6IO5YIIP8g9Ea6B9rJJrxJ367RDXYvPeAhs0Mj'
        b'663PTH4g90mBTvqxwy8If2tcZurVs9PayOkN0x0d40ENLRlbXrM/rVaubXPN/0drisJ2esb+7cevqZTY/NvI6cAtbXz4F0uXM5IZj+wrnQYBN370yz/1OpzeZeoRuDvS'
        b'10H0vkJ46qefv3SqfWf82RTflpTmOButWWP9/o8UPlY9HbLl9X+5RLe+mD38wdq/K/1P9rUL3Udb5s6+t3fLb06+GT7xc22HJNeYd4/M/br8R7Kn/vzpn8x/0Tn3w08C'
        b'9+WVOvyPd7hb7xdflKiV2M46u+75yScb3t6/9+b91/8t82XQscntBWY6XNFJRQcW7V7sJoRayOciDvxPcqKqDbZbPuZvxFZVyBEr6KrybQF2QqXU638Dexc6Ok1AGydT'
        b'roFsUgMXHKFCIfO9jeBd3tOVDXcTFxyhAYc4Vyi2m8AjTojdlxq7LIzLXgjz0ACDrmf4V4sDrrjiPQM+xMNMTqCoI4IWbBNzjqXIVAcsSAglacGDAYG5HInfIzKncOIi'
        b'n5fa5rjLYjtObcV8JkvIQZfIknWK4LyvZZHJWLBOUep/lfpeMR1LeOH5bsQOkrzdhALxZqGqPAn0uZDPS+wFWAIlFtYkF+cudWewc9LliwSO24ilHkGmBRPmWckJ1kKZ'
        b'BMbEzlBqIk0yHdInnYE2mskfmJy2SBUqcJgbIgCyOMedhysJ5fOsQiC/QE2okYESLQU+baF9L3MewtAhzyUioOYj445TO7jSlWLnbVjAJeyygpBcjhQUb3fFHh263WK+'
        b'cZITDMpDCc5DMV/H/pESq5C0GLohdDSGhgsXOVXncjjMPVb+UQtGDcUXoRRnuGVLsHgHi/CmeRYmlBPoYpUZDTWPJYeeDHb7OlHqq7n1TjMK+k10CnsWSS/HxeOrcbH1'
        b'KkIb9jvpF7achsG73lLXrmTbT+k1vsiUl7nfnuHGlOGfXcXptkFZGtP1DTSSNMG7T08SfeoGvomdXPbZhur9ylJD9ROTLbri7BZ5/ZPMfRkjf07fHOcmTHiW2+jQwhLj'
        b'zVg43XK+u8JSzpkbuXjFRXPjN7GVP5EJ+/+prTyclN4bwse2t3BuTxg8x75oluXM2gdT/iY1a78YN8K3wnWqNRPyVVwHcYYIzgIOE61ZRGOGw/FPa4i7YNqOv8Xasho/'
        b'BhYJIdGXuLzSb2SzPvpcuDH/DKv1cRrrhhYM8MrlsfPMbjnKfnXztMJyi+V0C6tXNWHrbVI7AHUOXxH9zhnTcoTPFf2+ahbDkxZssQdXiUQB63GWEXnITV1O51m8Y56b'
        b'uYsl9JzmQx/ZB55uLPoFHkKesn0wPIp86VM9mQRGkF7d7v9+4KMb1lrvBb4YbKprHuQWFB0WHfxB4B8DY8I+CMwPd5FmRlQrKWh6fWwmw5dGbvFiId3FB7wfZzFP8JdM'
        b'GOHrhN+7jVXK5pvsVoYsLaY9V0Mex0nkr8MoC32p032MmXCcJGfTQhzEs9nFguU9/s7XhcqVJvUnjPrpK+zq7s8FoKPPCMxmmlxK8CkePqHL5xsBKGcw1zuidlI21EzE'
        b'5TZb3Lro6qoJEwxyORN7vIQvgzivEeBqcdSRvcDb18uwJjLwWz8VJeykr7er6F8OP2Ky0sIeHe4S4sHZ2Ncts7GHCQTfsVQM+lXckxb2Z3hEMoTPa2Y/p6KkIU7Ve9pN'
        b'LrO2f8X0R57r7r71dK/I0xdF1JIh9NNphqOAM8EzmiFLVEN2kWrIfO1YbmaE73xC33SSJJKiLWW1y60qT9fUr8RLwnit+IlAmlWU6XhJYlJ8TIKD4eHFJvDSUwg0jA2O'
        b'Iv3+K5Tg1fmlrEcSg0OiLWmsfZnUEnjG65zV2XPLAr+Xor7jBJC2UzEK5uWTGDkjdEjDStfH9OWVSiEW2Xgry2NRCFRGZgwWyyZ40os7y3e+H/hB4HuBPwiOCPsirkfC'
        b'vAa+3/LFgdJB3467ZrKmW777sxdf+/ZrL3jJtF8mRBiuTY/yG6odritodPH1qXUc2lX4gkpjpKDCQjP55XgzOS4+VPfiDU4rgkfQz2lGQFJ2PqeC3MZG1mhtuQYCJYai'
        b'W/t38a2fBmDMS9kVqo48FgQqVtjrzo29A3L3uUIbacwsjJLpctiGFZyKsVkdG12XNAPdy8r+InykBmVclfId2IT5Kzs2dJMOv0SLhZC+Ap+fLt8uL0zBcmikkMNhuMM3'
        b'xfA4PtZOgSvakrr+MaRaNjwvPXRLY+E4u/qSML4qZ+gW8Y8tieD7aYjTz0UJHuk8nRI8Y9FPJwJPxGx8XaFBKgn+a3RV9E98MnomNmwhJ+O/Tw0O83N+TWqwuq+PZNf3'
        b'603FCaxMJMj+6v3A89/62QuEkNUt2ZsLdtSmD8taqwu2vyWuDfY2E3HFVTADGiCby23iY1ZJ5BvhfAnr8Z44FRpl+MZsndi1XprjIIIK6JQmOdzSX3B0re6y3fLc7OuO'
        b'gIV1rgYf0suRisQHRAsi8UHR8llDnwtWm57hKn7GWsx4dHlDPiHomuRSUILH0y3QTJWV8i85TpmSe077c/Bq9ucFOGYG+lBpYfqvBcWHF50JksQgFjMXxMcKXYm9RgyR'
        b'lZJfGPd/CwX4d6QH5sDM1JwbwZLZpq8kJSQy2zSPkgmJkTF8JCFTk1c1LvOq84r4L+ZFoMFXM2wvYh9ba3xQMn9ctOevQDoG3E/aoZV4FrzGBwewFSq+DhPmWfCkI1+V'
        b'eQrm8a6Fi0hgaC50FmDVLRmuMMxlj4LM3/E1ZcQCcZ0w8W0rzrp7Yj8xv2hjocAxMDrdXldwmq+2yNnh+rdir4WnSHABs4TeAqyHRuLZjRrpooRm+toh5A+Son1KosMa'
        b'xx5OhyfvsPtk7Q3BbE5dukK2KsjJCZQfBXm+bZj4zpqwmKAPfqC/R9usJ8O86924Tzqd3lao2VSnkpX9aVFVY5hzokl4Zvzb7xqVn6rO+L686ZEzWiCZ+s7Ar9JObHxY'
        b'lOD1c6/Pvl3WVvuHEw1HTo38uO+V4x//dttc0eAPZg6mTszNdl6rGll/8t7VzWDw/qc/eiMk/v8IJK+ZvfPbUjMFvvHKhNudRdMoKTq5rCPTDPLZtWutoFIvYqUYILoF'
        b'3djESQGJWAGDK+2y17GFkwK28o1PU1IcFyyVJ2BcCPcgz4sbWZc0hgH6Z42F+UKOguI+ETSfC+LUfXO4j9NP2CpxVLSW2SpdcYobZJ06V7530TxLv2WybrB9cZwIEnZL'
        b'EwtDLbYvs7Biqd/qLNhM7uva+t6Ql6bjcpTW+ZtTWo2FOhrGIg2uZYcCF1FgKkzVXYXm0UQrTXycpOAo+mqpgjSNpWeXWffon7HPRa4rdJ9Orp+ydDpWzsLI0WvFxdhz'
        b'PjiAwEXwhjg6KCb89IkQ+WWYzzamtYD5rCU8l1DKrGFKnO+X+ZtFOeo5GjkyOZpS96JWmJaUtMvnKhJpVyDSLs+RdgWOnMvfVvBZ9vuSfPK72+JVSPvh0FAWsh4jSV4Z'
        b'IsT8arwPj3c5hsTGx0sS4mJjQiNjwp+RS0oE1yEoMTHeIXBR/QrkiCZjIbGGgYGn45MkgYGW0mD5a5J4LuaCczI/MVjQU53KhiFBMYyUx8eyOI2FKN3EoHi6D8PgoJjL'
        b'T+cnKzyPj0lmq/odn8plnsWZ2EEwx2hCnCSE26Elf8qr8pmlVImYpCvBkviv7UVdBDR+GUs5D8kRkSERKxget6OYoCuSVVcQyweYL5xDRGx0KAH3Mvb5WPj5laD4y48F'
        b'AixeWoIhn7FhbejJQoWTIxP4FZAMEBEbaugQlhQTQuBBzywI5YGrDrSw+pCg6Gi642BJWKyUGy/mb/NAkMQi4ZkXP2jVcZbD0FNPcjFQz8Hw8XSOpdDmhXmfFuIsHSvY'
        b'NvjJUZYnhXzF+4xSkOji42m4287eagf37ySiNoSEoZKFq1oYi0Cfh5LVI66PScKCkqITExZQZHGsVW/cJMGQ+yeLtnhicSvkGylksq3EkaJBv30N6WyF2KMuJXwrxR4T'
        b'Dy4CVYgZXgm28TCCvUR9Y1lTthno4r6CRhw+p3ztago8ILKMuQJsvAptZkI+ubne7Tqz0m0Rky4OxcKj8PAwb8qohmFZeusULzOZWluZYu5285PuJD71SGD2dBwOJZ71'
        b'8rY6KxJApbniXmeoTjJjnH3X0RUufE5bkTnOPPhS933IRQVoMeSLnM/aqehGCW0EAq9ASwsvkYAbAvoVA5hcseh85xM9Lc2sXGQFB5JwyEIO63Ec67gtOMNQkIUVNmC5'
        b'nECoyQqedFvwdQT95fbnibg6gm7/kBjzdVNeUhYfmRXxRQgNtnjxH04byyiNcTJlYPTcSV0Bf275WA6t2CZi1QlhCuuUoRhauUJc3Es/3aroViI0pHcCVbT8YwVclLED'
        b'lkA5l4/vk3zAmXNlnmSliy2Y7Lm4IfrC2dLFzfqklTnrp2KmchW7DZPs6P29h5WekFwLzUhSgu7Tzov+ZEiHJn2cVIQ2vJt6wkyBT2Ivwuw9Uk/ojR2cLxQabkAVH6Fc'
        b'iK1hLIkdm3CET2OHAX3+vSpfKJWmsUPbZYF4k5C2nb2WC22zJDiYY7Ge1QrLE9nXwATOc29vx4dczVCWDroT7wnElkKYOo3DfI2BGmOoXkon53PJz+J8sAA7udiNNfs2'
        b'WkhzQRWhHnJZMrkJjHK55MbbYWYhldwTK1Zmk7NMcsyFATNlvorNENR58GUQYMpAID4ohIe7aeucN77cAR5ZLOYKK2gGcmUQcvdwCe2RV7A6HKYsluVFcNGq3nv4gfPw'
        b'PtxztXURWC4UQYBMrOcAL8aFdRMudoMHXtIyCLOnuDFvwygOuVrDI5xbVgqhDrKuc5n70CSiYZcVQuCLIPgHHmEJx3wPkft0BQ1LUbIsRBbHnH3h3l4+Db8OhzHXdTEH'
        b'WGH/JRaBCxnq3NdXTdWXbIl8Xj2kn7hAIMy/XXMBWhfMCAIFyyDOiACTyDf6Obc91scKO71JsJYRJ0uE+7DpGt9eeRQasNbHytTuLJae8WIN/qyE0ARZt7mSBkeUxB6T'
        b'fInQ6D94OvBYFGcDZbTXCk8cURMLRCoCnPfHdjMlvmpTPUxAT4IrFKjFJ+GgCg6qE9aNJ9IdRMmcJBxv4Sq/bMBGbEzgHrkSvfBQAo4kMfNIpwzew0FTDmR0wmE0YdlQ'
        b'yYlXFeNV1eQEpoS63TJizICMVD4CqBWqNuOwa0ISjiRcVbkKRerxSTICbX2ZPRIrziSLlZADjQlXk5S4odRxVBEHaU7C1QIYIVCUruDQRTlZLJPheoIYsAamCYcDF15a'
        b'eEZbInPYEUu4qnKbYBqn+GHlzi5f4yZ4JDaOAr4ftx7psDMJUO20NFRiPI7QCo/LOEAzjvI1IApdoCkhdfGhZKLJcgINORE+CoK7HAqm4LSpBMqUcSyRVqOiqErCvupt'
        b'EQx7SetU6OAjWx8raMGis15e7E5lWR2LMksY4oqjyRMfyfRxxzIfoi9VPlDE6pPWC2kJj3BMB8v4Gs8tV2FUFbOfnAXqr3BkgnUAY6cxph4vCwNqAhF2Cs0hU8Dxmm1Y'
        b'pspKoBa6bnd38zzDmIq3VFW3ZBSz8KQb5hP1gAwcSD6jmICt2MFBqoQAqNj1EGsWKiMQOtCdmRziF1S3RlaeNZ51JgLiakV45iEWaEKjDFRHGXHUe9R7vdpBUQQrfXsz'
        b'VieAJ+mhceY6e0Rd7MMjXxgEC/iWHILPDkl/MXU049tPJUAHXdBD+u26AApNrhNA5PLtodrlNOAhcedUogJjqTgayn88CmXHLLggNMzErJSjVrzNoYHgsBkLGB0S3MHx'
        b'yOOykT//yS+FCbeI6aS89+cr3q6sp0Lfh+t+9dfR7/3ztbovDr2j7v19B+VfRvsZtlu6arpt/dF6+a2tmxQljlHbRQcdde28f5K2V1b525p7hSa/TSrJvHv3hM+FMx8l'
        b'JSW/8vJs4SdbrOyEv/pB+8cjFbFDtdHDoe+6eJT8ZOM199uOHRM6f/n1n+z+4L/bpfbN/C+OyTuYyY7/1PSQ8JeDvuLCd4w+imq54Vcw63170tT51CuPut/77T+izO+q'
        b'VQYeOv7pkffm/h6zRS17oKo/1Mrtw9c+UNnbm2Vz8fun1pidKjiu/+pW5++dWXu737ji1kk367mXNHd6NL30t39s3vvOjazmkOFmmQ9vl5t9NuzsNNXR5t1oP/Gpwkd/'
        b'fD15pOwjyUkzZafv+Xl/WuWjbNOUWfbHiJ+vHfeHy+fjtAP7qwKsfp9lscvB5ge1ief2dQ3Vq6YZ/srX+MNfffAz/6A/1492j77/yxjf6cg/626/cKMWfvYTlwyrF6oC'
        b'Xf6y1Xfod3/5JMl3pD7/+PTr+2omf2RR1P/Gg3hHxyMbpv94J+dcw/CZHHmzdb9O+Z64eERFXaXxwcz8RPjH70iu7KvwKHq9IeDF//lD4lXcVZAyOjFrP6C+/w+1rz7K'
        b'BKefht5Gs6mhH78fuG1s7Kcbuty3rUm/9q3Pfhj21p43LY/8ecv/6fh31IPOuv5///XCms6/ebx479d4fmzkrRcl+21NWn86V/fJl6/NHAj49vopC6M1667U7/rVvo49'
        b'E98p+sxSQ/6VufyUnGT7R78xOnv4mqDoo6CNH79ZmtKsnpL4Ssb6zPeK8+3d+pQ0f/PKz2H61RdDNH9zzur3fmcO2PSYT/3yTteUV63dv6+nT6SGGrW98/H3O/76vYR3'
        b'/11y4jtfxs1fOvJKyPWIaz957+CO0TSn7d//8jN5gfO/A0p1zKwTGUFbD7XKrMaNxUqnttZJGbgP1be5chuaYlMmWDhiAS9XbIMC7l0LxVS4Z+C64GP3pGfkBJqYIwOF'
        b'kAezfM2MIa1ryt6Y/3jJELHCSSJ4jHvHmOOIqxuWwsxS6R58EIdpnNd9F2FhB1Qp85Fnj0Wd+eE0HyJ2DydJDmPmJl+8z2Lj4B6O+vOheg/jsWyprOwoMd5ekV0QDc+2'
        b'YKltamGKDU+Gxo2JnbHBh7M1aUPXhoVKcaxMHO21/7bIyBor+b4OHVAE8xYe7lgkd14oEO8UQrfHbW5d8URbF41Q3jDD7FBncICzvpkb4sCiBQurdvAdH6xTuEWH4QQ8'
        b'XKqTS9yxK1C0BcaN+Roa94nj9rpacI2eiUVfs7ou2oqtfEgcztNZFLjy5Vv4ssGYuZ5VDjbCaj6IsN0U+njDn7sv7/vTOcN3iW6CehfXpaBGGNbl4hrTac3cmw3hfJOw'
        b'7bq75EmbaBWeidblDyEdZ2lJzKFxzIMl9hDRSwvijvgOzuAU1BJrLbAkGZFexnx3SxIAttO29ax4t0fLNcx2dVOA4UXfIOcZtAjh77cJ5rCJSWIy2Ct1KWZI7/4wtCpL'
        b'ZeKT2C4Vit1VuFVtNIUaqdzrjLW83Ls5gU+fbN0IvUy8arNcIfYSLrRye1W2jpMKvYeNeJkXG7Zyi90ZEPa4xHsLGoP98C5feqflzt5FkddRhwm8pKwlGnNHUQRlCxLv'
        b'Bmh9UuKFCmzm1ncI27GNDcP7QmkaTJPBDp1YHLPh9n0Ve+iqC0jA82SFE20Nb4vMnWCSa0AfivcTSEDnBJ/4TUz0uYrEvQeEtpAhtMRWWbpZBd4YexJmXBevRIFEAqwX'
        b'Qf4VKOFjrzJgEkpcYxT4jieQt/0k16Z7wwkxYVghzvGxp/nWqlx9612ENgJ5gqJqbBEpiM5x1MPvpJyUX8J9zEjFPrjHA+rIFRy5RgjisayqrUCbxOBiWVfeZ9ZJQ/VY'
        b'HMQH3CPW7phPQjzNjrVi0nkHsYoDMKjEYSiw8MZS9pinJQkDdD0iwdpd4kM4s40L8oEiIZTzM1lbL6/cL60e6oO1fADrAO3qrivmOR+15IiWO6szXSTCFsNdHFjAZII9'
        b'ZxXPI3VBboO8h0j/lB33qolHIqfYLY/5xQqoO4U113iQ6yCgHcNhdY/L16SEUBG7RYRu07HclW7zu05XYWVmyiAnAnvCRTCENUlm6v95AtWSafi/2Kp7udM9KDR0hdP9'
        b'EyZdfTNr+W7WW0WNi5DV4YvesFI3wk1cZWoFoaVQS6S2GD2rIBIJdZlxWho1S7893s3lM7GyWLji5zPxB3IGCtx4fB8X3sytQP+rcIV2xKxR99/lVOSErCq2BrcWNaGa'
        b'SEuoxlnuFbjyO+u5sjlqXASvmpCVzVHjQgVW8asuOxapbV+RN9Av2srjjzKj/aKVPP7YSnv/f1aZXJ6fZ2lgbkZ+ssW5OV+BM/2Wryxt0/KNfAVpgs+sv75zd9mBmMm8'
        b'obDgS11KSgwRC5b+kxMss5CdFwj4DCPeRaAodREIOScBcxGIcjRztHJkcrTDtKUOAnGuXKbglmyqFvP0nhPclOWcAuLbsj7Lfl8q+/A7H9EqDoIzcdKY4ZX+Ac5SHiS1'
        b'9C46hZ9udV94YmUSUqLUaL1sCEup7TokKGZVg2Yw800Yci2PmPHx6Z6I5zHSM7fHqrOaLyzP3JBLNOLsqQvr4K3j/JKYq4OWHsNbpFc3kBsejQ2V2NkbBgfFcxZdfsPx'
        b'krh4SYKEG/ubObu5A5T6Mx6vfrSaI4KGX706h9TMvWDkZ3b1r7IDf1Or7+qdigw8kljWri70wrzrUkv0U8/wdRebKboaY/8GvM/p3Mx0aLLcyOrMLI6Y6+mzwtoaDLOp'
        b'+ECRZNgabOFU3wPiOOYkZy7yMezGKmLbrZzybHWe9YEUKASuv6GyRdaLbyaT/tG8j6q0lcyDHwpMUpOcOEnxGuufWB4FXUyszsUSH2YedXfj2O65J0KBV5oBZM6oEu/v'
        b'xDauZub6Teo4vJOFX7sL3CHrKJ9l/6bgX2f/KTAUC2wCJb6SKh9egX+tzvE09/UPDvvH3RZNCAWBaVETWu/581+faHXkvt1x67LwFyKBhuP5hIDJ9T58bc4dPpp2kVhJ'
        b'V2ArsIXhXVxsNjZjA+TQMdbfWDJ5Yy4rxlnBrLwkPJ6UWtC5Rk2up5xdLF14yRDHsUTVJRCnk1hUjvwWEpKfHrMQh5UrwxY2bzLjuxTAGC2gnAsdCsElSUla/X8AGzgr'
        b'jwHNXr5oBD1jKc3ozyM5kJmdoRmyoOmplmdT4wOL9lNIhznFW1qu3El9S4NPcRtQvuP291QTqcHEMYo/x4HEc6lvCYinOKal1m7706Z4OcZAmAHdTJZv1l1+CevhIXTB'
        b'pICZUq7bYikf7zvJ8vfpm1wlTjZMxVbs57ty98fjgAVkmvIZfb5buE8DcV6N5C4W1RMpiJRAHm/5HVRkWVokITPdVLybRH8v6IfBZM7GmkhTl7vu9XjMUHrBFpp4k1Uu'
        b'luoslXcVYg6dUquHKPLVK0EyCX0EcJsUHQ+UzRe/7Kjx3fBX3z+0Yd+dxh9lKedorNmVqHP6nJGDktjhVJGGS7vOx1XDqjHGWvL/UHi/OP/d361LUZrbtdnfr/7eP//8'
        b'4p7m0Te9d74n9/KF3/idGOl88+auN6799JXvRt8Pmb4U1dFnfeNGSkfR2Kz9WIjx0XeKxn6+TekfZW9NokniUEhNnoPcp7+PNGyptXsnbm74hRkT45yXw7P/XlDzi1s3'
        b'DoftN/hL3nWb3wTs+s1PpzMKBivyJN7rel/zvfrP7W/8K2DD0G8nlCZDP9jxeUn12ylGr+/qG1CMOhh6vu3Didcn5RMiHEP3r0k2so1x3Gbk9Om6f/1+dOKnu3/spb5t'
        b'j8OaDxIulxzU8U6bEp756we94bfDDgX/4ztdr31Pbi7lx6+8H+06q9pRHKP8i8zTpX3/qngrq/L8Xz95M7jNPKX7s+CjtX9T/sV7bqNXHbx6ZjcdcPjil8cbu486XXZ+'
        b'19vllS1v3Dn3npnejqs/qfmTyl/qXg0y0r5q4fLhXf+o22KnD4J+fO5PxuvM42QrX7f+dmfyby+/+Rd7099/bvTvqtfyDV7Us/r0TqLwwKsb3jbZ4CA5632v9UcjFpX/'
        b'TP7D/BeyO/XqqsvWmulyUvQtOchYyviDIVdSk4ehn9czR4NwbFHBvRzG5+1BORZx1S3joDp2IajFG5uWGSuwCYf45L1+nHHDad3FQhWsTEVSEKf5HYBc1cXKFji2m6Bp'
        b'Bnp5pXAKWm2WMvcgjVUaPczpWJh1SllZBtLMV88/uObPB+s0xWEL0YmFHpgxOA7DR3CG19sbdq+VtsG0Mheewha+DyaUYQevoJUR2W23WGp2uZNoysxu7OEOxQEGoYK1'
        b'1uG+xkxvvmUPVIv4l3O3QpoFrYjt7DKWCRQ3iqDUBbu4MB9PK3sTWVbBf7F6f8t5flt5eJflC3M6f3/ESrUfp/EBd+LJ/lDjilkwSJQUutyk1h313TLnsQ2aOC0QZkiL'
        b'auF0NyxxJ9pKHMRCTrABGsShtnDPEKu5i7lGlzwYZs9G4PoPyumLxDCvwWuId6GHLywKIyErVU3sgFzuGTfSJ/MtnlQ0LQ6QqlmykdPg4tbpWEh1zG2kmi2pmVDnxFmr'
        b'IlWdl7WoYCsNNllSMpX3c1dpQxDXsqDoHYE8gSJT9G5d/w9le+3/omL3mHansjxUgVPvehhX+Gbq3R2BtQqnZilJm2IqSBtmWnINiOgTGfpGJOaULDH3HP83a1vEWhax'
        b'2qVKnEq2oARqcCqYCtfQiOVc8UqaEvenLjePFvdn6obHEyOW7Ueql8nxGtHJRS2JKSPLFDGN/+3zNRMvm2z74oycNubB9BASFBPc2Dl/M22M9DGbp+tjzzqJhTCyHWxZ'
        b'tqJVdDEmu3Jyq4eACxWXJe2L7wEg4vQxGaaRhaksal/ir619sfCsw6tF3i5oX0uNABYDabn42//lAHL+nYXyN/x7qxS+tDY8ykfecEt5SkQRF2/OVDR69KSP597dNjuY'
        b'SnQlKJHFjSQkxkfGhD91CXzdnaUomsfLDfLfP1dui4IHJyJeEXuslA9xCrKeEVfrha0neG/zmKLekicb66CTK/gE1aHc13EwDHeXebKJNTBXthDzOP+lHbRtX+ErJ/mR'
        b'axkAU8qRk6+8KpuQRk+9OWdilT+oCjY6xz5qvud4P1zwbb3cbYECpXNmGrbtCesb334N3tTZ0jF1I9XTYzZbs85uZN0py5Y33v9bmM2n8qGf196M2tegt3fzRVG5bPJ3'
        b'f2/63WmHU5+/mPLy2Rf/3uF7/sKGzYFDn/2i+ZbH70Ms5oI/vfD7C1HbX/ZP/s7AF4LYyC3/tvU3k+Xt3HOpMEHShQpTqaSJM6bmHHNwhCnPFfGyk1jLxcw+ggecwdMO'
        b'h5KXhczihNFi4gyWcE9c3SS1kmOm52OG8r3GHJfz3Hgca+AuZ4OXWuDhIU6syIr5j9jIMiqvlsSh2go67/E8dP6OYP1CBg3f/HiB1jPKnrrxMQq0ctaV1HglOVpGjb9Z'
        b'VW4itdz7O1bSW47UetFn15+b1OYZPZ3UPnujrARtamQcs9z8V0pRLqTkdT8Z8BofEhF5TVp9SFpFd0W9o1Vo6VHeMBJ9nbOkRF6Ji5YwW5AkdPNT6a50c4/X3KGPv04T'
        b'FsGqlEvswZVcuRQO3bzH6ykRVUHnzOQEwWsVIrFha+SXXxTJct2J/UbLWda577dee2GkdNC59a6Z7Pe1QiLCovOVgi2DYsIigt1YjnG0UPBgUqGoz9pMzOEgyepQzTSM'
        b'DGbGkBKBnXzXKRiFcT3X5WVBsH0LtBjY8nJoowVmPNE9QUwUokvBGee5DGYlnLdmGYbbiRQUsnaXvOHnpPtV6RuuhPCFF+RJ8R+F6q/sBacRxN/uApglcGi89/nQ2J4h'
        b'8WIB0EUT7mMzrKwIf2oloq4seLn0BId7zNxap7JAZr4p7qUJ/vSMXNivWjUrMyHr4XH6hIeZyIP/X+MrCuctldxg6btc5h6XEsUF2nMWdE5w40gKtzf+YNb9twX1r0ng'
        b'43fTr2rK0goBCiKxspJQ1+DxGngaGhoiBaGOuoJQTYm+X68glPtSzA72S+PbWkLrGC2hoYEC36JPYzM08HnieHfH8jxxkcDURPaaAgwmfUxTymrZk/ZbfiAWG2w0IBvH'
        b'cXrNnt2QFoL9cg6YC2VQrkC63j3MMFCFUlIO70MvVBw7Bq3KUA75wg04B+M4pwp1DjgCxTAUBKPYfVpVhI8gE/sP7Ic5GHCGOSd6qgTzr8M4dEOv9U1oc4NH+2/iLD6Q'
        b'xwHooZ+pXdABbdgZftV2G9btwDRsiYEmUly7cQgbbh6AAugkaWVwrdPV/Z66ULAF047eirLDIpyF8cj9mH3Zab1B0PoTDq6yfrY3rD2hzU/fCipwdD9M4gOSe0pjoAfL'
        b'aJgxZxizv2KOJbaXsFAVO0NxQJv4/H0ox1b6mcbqwKNY72UXBUUh2CcHTTCG2bGkF5dhkw/2wUDyFdaj5RZMY81pKFuHrZcDsBra96zBR84wbQOFtPcyKNY8Bv0+kGni'
        b'SgsYw/q90H8LH56COiF2Qj1RrEpopL9LIqAL66E1eZOMMlTCCDbbWmIbjkXsVdpPZCUnRB/SnK7A3VAatsYdZsxCTsQanMDiSJzDBhes8tODvpTDOEFK8D0cOCAHtafM'
        b'zrCULKiCLCXj0zishy3YSv8ad2dBdr50GFVQY4njew9uO7BVRxuHztIHjTdMAiywDns0tDEHS2H0dAJ9WqamZITz9EYPDkI/LWdAgDV2kn1Ydx4abGFGC5vVgt2hODzx'
        b'IKZ5n6f3azZBwaXdCjgPE/raMBEN8xsgO5xG6I0jJb12hz62hhqd9T+wHSsIFCagMyGIoK4a60+rrDufGrPvBo7oX9gI9R7Qui4A++mIarBLgfYzQiBVj62OWKgAOcdx'
        b'yoZushoe2tNGe2mJ45DpS5dQYnWIICI/BYbWbiC5bo5u877abRmcwTynrYY4l1REUK9A95MO97wPQzHBvQrM4PCam450wQ+OQ9omaMRaK5Wd+IiuaBCaZI5DZ0jQFjMo'
        b'jRBDgeGd7dCxNyk1Qh2rCBpbsYsOtzAu8BzMrvGFekeoh0Foh8wgbDTHGgtjnCDJfVwGBhSxcgOOBcnG4T0YOeOXfAgbbvlEE/9ooIOYNaVdEIhgX4zrPhqiSZ+wN93L'
        b'l8Yu94WaPVALOcGEe+kie3cshwEremaI9dG6FXBLW8P3TvBOp3Bs1Ly+UxP7aKsFBMuZhBYZuwiv8pwM3LZeN8bK2wS6JVCHvTsI0B8SgE5gbhCWR7PuPobHcRry5LHj'
        b'IJbfgOYk18OR2GeCOabEVudv7rG+A9kXFX1gQm8Tq9OGDzT3imNxPhCHRFiaoht0HO/CsBIU3naGWkzXd4JiP0jDrFB1aIYuT58ztiFaxuuw+7CTko6WtY3sBrszLPTA'
        b'DXN96IZrsUcPcomupAVh5266ymnIwCwZLPeAMhw0xEYPzPfFHhgWaxIA5q+FVtoGI01Zl2zZ4UIu9sJIcso6KNpE8/URUHWlEDzkpGoqEEoMh2ElTt601YEKOsa7dD0D'
        b'RLpGFcLVXLB5HWsW6X8WHxLmZeG4wQWYdXeFeXiguBXKE4godEK2vQSHr2CeL8xar2dGwfOeML6BYO4hFnlDuauL5vlkHKX5OgkWmgIgnZBgnraVbosPtU18tq7xhHQ6'
        b'8FE/7Iimo+vyhCEznJCF2uCt0AI5u5NeIYjUxzZ/AsgDUMIAksVQWcBIkj02nhfTqPfxbkwQ3L+qTJhZs8vLEjo1Al2h+yAU4hid1QzWbCBAmoN82tgQ9J+E7ABC2Cwj'
        b'nHU+ePAA1rpAW6iGEmYRwHYQSI3D3S1Qb3iNILhGdBBmrgt2W5/EisuJFnRpw9BJIlM+TBHmlBPKNQQHXIgh8tFqiQ1RdNjTLFY3n0C1B9qgGivPHyey2EXIMm+x9lzi'
        b'hYtw351W2Y6lOGJK6FF2yMg2BQt1FGFyOdASilR7raO1jCZjppXiHRiJ4ahmpdp1qCNy2XnYbXfq5hAY8LhxU1fmohMUrIX0MNrcPA3QSeQpc/dBgt9a+StQBA8uQYUq'
        b'XXK3oSpU7MU6Z7ifSI+ks/IQ0IxNxJceQJq6CDMPEBXpWCMP43txSs+YwGEIpmxxTicZ22LWXBdHRGMaVBHKZmOlOh1WO22xE2dg2Ivus1UT8/02RhC0ZeKgI7TTsc+c'
        b'NyHu9MgvRZ+gt+XKASwNJB5WYwbdyYQQhdZ0Ha2HbYnM5XEun/vnd17ehWWmUdh164haKi0wk8TXEoLn4R2GpqFBMEwUZ1xFBytwCjNVMPcENNmeJpiAluu0gDwsMSWZ'
        b'tgUeQkkqtspv2EqHPI3tJ/y2wxw2Kp0wpw1nE428T4y74RgMO4V702UOQ0aCH11pHbHEZphOxYJrUHtBXoLVB8KcrDmmXuKaSBwnO4loQik9U73faa0vqbYNlyFfdE0P'
        b'Ggm+6QQJvqHJP4pWOY/NMttiXU5gXowqlknOyW+8iH3roYZB13bC59YTmqRvFye9LGJS+OV9jNTGcBLGDPZb4Jjw+KZAuC+Pdd5KQhhk0cfFhDS1UJoIQwIit1vXYNoO'
        b'Ot9a/Rv4SB6moF3iZAr1R+GhNnGD+nX0eLEaNspf0Y9i+QHqhIy1tmY4d8baGRpO3cBKfSh02bSHGME4q1c3hwXyXtAdyNAlSBh3nslC92KwH6cvnCNywQhwL9EBEkFi'
        b'd0ODtqOFtxb2+0FZ4DHIOA5TGnjf6U4Ancv9PTe0odDHzQ+6t+HInY1HA4lu9NB1PLxCh/IQGgKuC7H6hB1Mnra5oXaUWEwD1B4MIdacQXfcqqdJh52N7TIwr4nlZ9Zq'
        b'rCfGl68DpRfcgk4T7s7anXKIJiyu8IUKa8h009mug13R0OtI2JcbBZXGmHFUiGmyXjAVegSqTkTC8EEPmIbcI/ZHj99ej3UE+kQVO2i+HMEVLqlhUA7uEw7k6RKuDNFR'
        b'lWCjLcxC4TpC0cZtMH0Lx64eJJCtJUZXjNXxMLX/KrYeJqqSFnoqBbKdYgkD7t+C6ltrCK5GQ69jd7geXW0ethCpyN+HRec0dyMBfCm2O5FwRCDdYbiHlnGPfmtz3JPi'
        b'pEF88dh6GPYhOByHkes7CednsecoFtLJZRHXa96ziQll8VAYZmjCYBHLdA5xtKCVVpoGTZFQHayZes0dG2mWEcKrGiiPpNV0k0yQKYLiJDr7wnU3aIcNrBMwcc4EX2ix'
        b'xiZs1/NU9SFO8SBKF1skWHWSrrgTp8/DvUBa4qODpOu1Y6493EWG5rNYfYb5ly9GXGM8CNOvrMPhOCIvQ5i19YS/Eg5s2HHi1EYPqE0qEbHumT0MrmkHizKEBU4Ir2Ax'
        b'yRAH9lrAuA0MXFM2sZePJxm29sRZLD9CO4H7h+mKZ2ni4Xg6ozFGgXyNINsOM3cEwT1kTe0G4m4cUNnkCrPYH4zN9MwjIh41dwwgzeIs3feEeC+RwWqYNN99CB9eICmt'
        b'CiclJGEWExPrIf48ikTUMu9YYaUWQW3ukQtw3wWrvR2JsZZKHKHujDkJHe0w7UCzFZM4ch9m1Am370GLBnY7Q/GOFCxXczcIv0KULl2e8KPphtIlGNjmcMxN74AqgVgv'
        b'VKlZbRTTkd1T0rLHEQNjBZkTmLGZTjFtG4F9h+YG4u/FNGbfecy8AJWHgejSQeKCRJpIPsCpS9iITfuuErmqggfETNqhyZvE6QG6J6GX1Vko2BZDjLoBej0x0x9bzztA'
        b'vpulO51cJuQdjdrg6XSKCTH5F25DZ7AZZoRAmvYNQ6whjlUWgGPxBDvVp/BhIOZa2UCNiACt2Q1zDhN4zRNZ7wu/QGpJKZHuvHV6dMojgVixjzmcY/fS6XfZQvZBgpp2'
        b'LNvhpxO2294zGNoDcSL2PNHl+/vUlbbZ7dFZZ2fGHFgqmKd9zMOE+OH8Nmg8Q6OWqxJozV2BfO+zhCNT5+G+MXTqhOJgDE3YQDu9d5EwoSNAsoboTzn0WUO/Mp1nPtaE'
        b'Q54BDF2Iu7j2EPRE00N9UBfG8u5komhVaT4E8CN2UHIAZk2I407i3Ts6OCeIxgYLrPZ14KQIW+VAuLcd+r0xPYYDylkCyhR8KMGu6wok9mRq36ADTDfeSCLuiL6NFlZo'
        b'kCx5zjvVGUrvGGy7kQTZQXpel1S8WcAr+4HMXcyyQZSEXjvAxKabGqrQm0J3O4XNZw8pE68cg3n1QOzAuijitQ9kMS0Jq05LYPZGDH3VEHyBhJlHnPwAJD9Mw2wkQf9w'
        b'sB5mxRtghykBRivhzsPTMVh205CIQyOTdyNoAbkXHa7oKdMbZUQ4quk0Ctz9SNDrueVz61xEipGKB5K82oYdRkS6H5w/mKJGh1sADHNLYSIm7qAWjKknEpqkx5M8Uerr'
        b'Yae4FQeCPTADqn3okTG4K489qhLMPcX6utLHOXFQr06Kyl1oSsGhSwSrA9tVLFyIOtVFapyIun6QtKfWjYSj/URrCjaYiuksq2xI2ixdqwOVMYYGxwlZezfipBORrSLS'
        b'TkaIH0/FsFh+LL+6DTu3kHrbg3dvQb2pFVG/CXmaLBM77Zwkdimbz4cRmqcTOmQmERrUK0H5Diy+bIcNbtsIE4a1NROCifrNYI8/9lwgvGnfTADYuIcElnE7yMGJuBho'
        b'SyQdPJd05bU2OkQtaw4RlR/et4WWXRoBRSQxyGLXGeKVuQSnFQcv4+iZdZglhkrsl9C89wjW6gVbkg/E+SfoetH9DhqZE7Lcg7LQRGg8mAL5WzBP9jwWREHdfnp2CEZI'
        b'6KzBvLPEIwpILGnUcVODZhfjO54En734KNUvmkTFGp+Dx/cwzeyhPXQcjjc/D+MEUiXuMHgjUieMKFCdOoH3iBW2nbrphBUnzAkiHq01wvTtblFnsDhwh5kcn73Ttz/G'
        b'laUlzeGwcLsA813vcFEtEettXJkfnnZwl0tKgmZX7oVbYsh2tRAJsCxR6CggrEy7wGcTYVYAyytIIEX8EPt8FrK55LnLkOnEjPlCwW6oFboIiBmM4yTf+LkKGa8osGQR'
        b'OTS/s4DYS+m5JCcZFuD9AOn0iBsVEVrUO6rQqfffVjIIUITqfd7qQdrElcqsCRha6ZyqmMBujHdPnnCH7KiDumZEaMaxY10qsaYWaDqpcTiAyHcpNAZjCYkrhL/YvJuZ'
        b'XEj5LkuxTjoKPbpMxrsFHZIgzFGGlvggQpoKmD8IaedOYZUHnQN9T6iYdZx+bYcHAiKwOWe0SIBr2E4Xds/WfyvBXfpGUgcGzf1o3BKBJ82ZJSGC2k/st4JumhScyJuQ'
        b'bU2stew0lBqTpjBE8OBP4kuZMR1ZH5Tbk5aUlXjJHeZcCdjbiUsUEFgN6ZPGlElaWa692U3IsSPZbYpoxACxg/swsJlE4S6o2yvZe00GS+Ql6ljrfBm6d+NEvIUBTl7E'
        b'h/4n10C3/M0kiXv8JaKfZdCuyKwGUKu/DtPpYB8SKUon2th53p/GKqTzrPbTiSKUnaQllO6irXYeWK90TgWbQgI5tateBjNt6fLS6FT6kKjovC0UyuCAn7mnLWb5Eklr'
        b'2edDJz1gTJjzwM4CWBpIN5TuI4mohLaUFr82SQx02Qm0jXaYPRZA4mQF5JtDkzz2RmKpM1QdwvtnSKkqJM1lVn4NFgRuDjE7ugF7FaAqEKriCVNmzdSSsDskPh476af8'
        b'liqtOG/3WV/SIfuIFpfZ4dBRp5uaYaEwaqoKY2rY7EyYlbEH+7afJOTuhmxk1p08dVLfRyB9PTReIkIA1Yec/T0C4s/5ryV5KJc4+eTavVgZv92OKMXQNRkiEB3Qa6UL'
        b'80kR+HAP6QKl5tpYv5bRcWJ3OTZ3CE1Hd5G8mMfsUWYeYcROYXw7NCQSTOXAeADkxBATb4eeY4TAfa53oO8S6XxNdKt9Lg6c/WVGhphMc0A46VIdULJn7YbbFiR5jngw'
        b'NQLLwoint9rQH/M4a6gL1ZIEy0Q9krceHsSJi6qYroozQmi6eCcgbm1SJzGwW/hoz+N2GSKijw4aOqpfw15dufXJ2BJKqJEeTGR50CsA8110dA+T1jIPNfF0ktnKOrL+'
        b'l9y8iQyU2q0nwKmG/nXYuUPPdfN+GL5BxCPHV8/TKuSwPHG0iVNnOQPNkKcBTVIPFbvpPGaUaP1DMUSTWlnx1AgcS4IxM+iHgv0WhBid2BhD/yi5thPqiaMRcS9lgNoG'
        b'g+bwyCaWJP0mBxwKDaAzznY/u5bJmUhUuuOckAjHDAFauj5hz6ATMbgmsT4+sCC6O4xt2mehy4iIajE0OMa7kYTdFE5yZ6Yjo62DkH4rmqT7DY4kJrStU2dmLTd8kKp1'
        b'VAl6rlwgMlzIGwESQgj+Sy9vo2URN8OW20QHJvUJDe6RfgsP3C8KojDnSDQRnMaLR8KJLQxjo4RWWJ5IPDiT3iB5HO+FhEJ/tNceHFmrAXNb/AkOanWw47A1OxFz7F4r'
        b'wclIAhkm4feQ4jATj7MXZfdrYN2GHVjuGUcErVAbW7VI+aq4QTQzDeavkqAzcgi6NT1ND9ltJc57H6v8FLDFKZYOvcHUJGmTWaSul5OWJt7XvpPkoArZR0QeBO49BHt5'
        b'0HmbyEBL0llnKAggIpthARM6EsLImbi9hBRjt85dIVYZA8UyOEj/7iUZbzLoGhHbxgM3fbHDz4qoUj0+NIPpIxehz2DbSSIKFeyK6RrmiK7VEXHo06SNzOL8bS83Osf2'
        b'XVB+ZY2TJ80+tYFOZPooTBwmCpxzSdboUCLMhXOyFhRfsIF7PliwqNieo8mLoGanAdNt/byVhTCqhbke0C9nBX0BcrrQjUQBR3YRGPTbn8VZyLeOtCcALeOsJT1GViy/'
        b'hxC8TtMSsoimEYRmwwApBjiX7GllxiI0cebgYejWhzp1/fV0+oUwEkqY2nZovwC617HIqm1QZ49pm4nUDUGvLzafgQZbPyI5OSehMdSPGEL/WSadtGKLX7yJrEzEfqze'
        b'jh0pmGcNQ1tOY2aMDbRHHSGm0E4bfkAia+MJIjYw6Yb5ln7ENhrMCZXvWm0+F4Ede9b4x+OcB0FbNTGOrJ06CtAcFQMDRLmaaIYBD3lCgvk4T1LZywhgCqE9lTZNrGo9'
        b'dm6HqiTMltBjNR5RBFGkt9RYqsZAlpKhA/bZR2Kti+4VmIHuJGywh6nD8VhDx1eCA2c3wfxpwV68q6qA8zK00Gz3NTApywwjbfbQGa7rDNXHN6y3J50rn3aFffuIiM8Q'
        b'UPQTHowTJMxeJdWzV5vOvS44hOFOWIQp0dQi0fnD4VdVYDQAO6M8PSLDLpJcMKRGS6gnfvtQCYdcoSAEas5arAXSLzKwKEolCHtPQ4m2Y+CFG9jk4r5xB5bZ4ODGiPNY'
        b'bCdiYitRoSxSoZtxxi3lJh1AQbAG8a4WnNsk3gbV2t6YHeLrdPGI+wnC8cIDWJWwNxQnjYgiPWLxhaQYyl0i8tCr7KfPkRhGtCvpLGtDdsIgjhqZEe7WYtt1QrliGDAl'
        b'5adAU57YY0+c7xqW6ByKs15X6XqKkKSDUkUY09pnTTSt6br2HXUTwq86Ijhzlph7CZr2XGHm5+1JR0mgCbl5aAVgk147JiNai11Y5qgeD+06clEmRHHv0VYGiR5W7xC6'
        b'nD5J1KGEtNSuEJwIwWFVQq1R2n2L5T41LNX33ygmKK8n/l1IEnxvKp131c7Timfg0W6s9yUAryfSPaXM9HF4qH+GDpy0aijWxSyfE0z00abB+i4ZQIct9h03J3krx2Uj'
        b'nVGBETRbs1jrqv3QsIYOpyGBmM4DCQz66hOo14u8d26AtnX2kBYMedtJ+D1AFNHgjNkGohTlEZipCIOS+DvEtzJhxG83cZVhCSPjBfKJXnbQrbKHDrkE6/Qu0TFNamFr'
        b'+Bp8pGCaenj/1bVwbw/0u90ksOogxteOdetwLNEFu7VI0ikhHjodQdwgVeloPN1iEw1SbrQ3Edr3iXdg36Gt0HVQCRsTsVcj7IIedGpqXIWKNVjoGk4DpUOlpbytO90o'
        b'SRmsYIPY0D3OcY93FD4yogPuJjxqDDTC+RNEvWrg3snDBwSEGfmEmSR/E+0qhzHlMMzZRcyZYLTgKAysVxQSNRi/dJ7oXgddyQSNmqW55hzx8CJoU4C7EZBtj91WxAJy'
        b'b1+D8r3nkdnIWwUwfHHfBqIpU5AdaUKI9kAPWqwI0esIJwZIo24MVFy3C6fXQs3pva5xTsRBu6AL+8T0SgYMG+rYk8rRBp2HoUdWn3CpEea3rVlHomyROZbexFJ2NHnJ'
        b'MCQTZ7yPPi3bD60m53CSWCVWa27dvxWb9kKtxJfgJher44k1zaYEYP/O/WcgMzqRSGOlNYnpnUEpOsHBdOrRETgNRcEwcJWE5zKS3YrotAYdiLJmbbUnlXASc+IdXMMO'
        b'EBnIxfwbVnS4QypCgrweFSYY00XWhSak3IIJT/pnG9S7kXbeDP1xzvjoHMcYR3B6f8BBqDElpkmqr9MBHHEh2a1fOXQHCXG1foQd8/LBJKmlGeG9dUksPiLS9BTDo3QC'
        b'ZYZIszhtQZS4liBzzB5H9EjO9cUKpcij8HArNhzdDmUyxN7uq7InDmhEkq44cyPc2ZlkgUyXM/aGmJ0aS7L1LD44THc/BM2KOLNbPpp4zkMhtvjg1LZbkEZaX5XxCXVl'
        b'H6wO5bxqfczGf+cGVMIUM2W1waQ3bZBQpJPZiUjC7YBOZ12su+5t4r+dtlaFPfsx/Q4W46g+Mcbc89B8hiStUSu5iFhbPRhwViK876UHi2zpVLOjCf5n1fH+BUL9dBwg'
        b'zlK8w0oZSzfI0y47FK3w0c0Ikv6yg1Pg7gHiycVwXwaH9BSx4azeCT0Cl15TWY2NOHHoDJSqOSoQzZzCNCeSZh4yirYLH5G6RzJ+iY2axAtIbTPdmxilhLMa51JNWNAW'
        b'th+84gUlcVhh60MKNRNBh+0jbhJ05JnAgKaDK2Fwy1qYUoIx3+vR5ti1jejWOOl1WRdxKkUJs4/7EFYQ1aKfApo8x24zHXfNJrynoiQTthYL/KMiL1yyw3pXNeFxXXqv'
        b'D8rkoFxzLWFbBYxHqZy02I5jm5jVk/h2Gsysh3HmuXugv5H0vcLgQwdIcG/aSWfRAo82WsVAmdsWwoliUnsSkqBuJ91C9kkc3a9Movs0iQWNx1PXYqvKbVnaQfkJqNdW'
        b'vEnoVk7/KoN5i5jA69C0meh0ptZeTxjVg0aNPQdUkjHDBbP0L8njg9NQHgFN8JDAqNjbj1lK8UESs3TRzU8T4R0gDpGJ7daYe/vSZuLSJACdpWfvedBmMs7hWKo1yWXQ'
        b'QchSQYw6V9kvOMmf0LEZGCchcbR9N+1t/hZUbsJyCUnco1cJXvqS9QisHt7CnDuQR0ScBI8MX5q51TzpTRKT3GHmxCIWODKLVMk5YsBEvaIOGXqrb8VSwoBzW2/Q143r'
        b'wkMU9bB93d6tdLnz+CgceuWdA2mOMZKPOkS7cWwDzOODPVHKtKEsvJ8IzPWb7r8fysVQrUdkfCYZ61yhVYZ+7YQpCfGZrttEFUsImSrpKsqUNmGbC1HRh3TyhVh+E+dh'
        b'er8O5u2GaSts3eqOBdHMxXWSmahCvehssoyJnuSpiLFHsp7gfuS6IaH45A7PWAK3dm1bWlu5jS5WbzEwwwbj4yQrEG4cJViY1YnAURWs37cZO1RJX8w6D5lHcdIRHiqm'
        b'EGmpIEW6ishyGyt1NSUH9/SdoUaZtIMOG3VoObwD6uxITMjSO70Gu7YwMGmXk8PcU0cxTxkzjnqRSjxtTbJTjj0Oqsfh6HYVV1totcOKww6OdDDDUC8mzG8nWp+dGmio'
        b'wfK+JokYTEK6IUF7n5AEszvXdhDAVXhDljIHF5OXiHzPXzYmktCIObF0cp2MFIzakORRERYBbXsJopn1vQLz1+LwblJrysIhVw5aIwyhSwz9Bx1wjCnnmHaKKNiIWzJx'
        b'8zk7ORKr26DQFDMt6XD6daH1FtRoEnjkGjE3suxNud3hp2nkyv1qWE2Cg1wyE4AytXfFkLZH4nwG0Ygy6NTGumNrU1hUhQ+dXj1MXby2DXqsGGy1mclC3WYSrhp8ofsy'
        b'aTx90GZ1icQfYtq7HWJ3wpSLyVVs3Qa1LtBpYXMch2WJo9Sc3Ewa7T0c2kH8rZshSZ2P1jE7krAfWuP8ma1E3Gq8A9Uu3Tq93o+AJxfTdrnRHLVbDhg43hKQcJl7Gbsd'
        b'WSMFZjmKvIFDXLUdkkEyZPlyO4eC+eq01ZAvm2Abz+rE2d5mleLuQZqZDP9dAcmkda6WQgF2WAn3smebU7lvLkmgypWVmyC8bRPasIJiGee4bwx2EC4UYJ5YgHORwqP0'
        b'jjU85KreeB9TZPYxnPPnzGP40EXa5gF6XWHc1VMk2AxdQlv6yuEIt+rb2GmDBW70SiFUCe0FJKfQVfGvZOqpc1Y1FZjijGoGitK2zK4El8VYYCYr8D4q9BQQTZ+EUu4d'
        b'zLy9Bgvc5QTYlsoMa2WbE/nPy7HEhRni9kMeZ4izuWkm5L6543bS1UVWQMypRmghYKpSPZ+PNnzqDG+Ig1ZTzhDnDONmwhNc9yEu1+1YjIgLxiy1iHczcrwkMJPhPv6j'
        b'HZ8gZxhyXaXG+wJfZui7/vyzaWZBlvuubxKweLIT3GhcclzkSFiBTMIgkaqxV6xuVZzz3HBYJys8+cILacINIS/vk3P7aDZZQfFkmo5i+5YHhi06h47/pfz45PT1H6r/'
        b'9nvvfJAiCd5k9KP3Z9/9dew7bh9/9KFBzU9GXpZssHnU99G7b+57cST4yp/+dd93y28jfyLMGPvQosv7kmmLhofZsbMHim69+svxH2Wkd135YudPfuHe1jJTkuBrcypo'
        b'Q1NqS4z5iX9r/tr69NQPT+V2VAb8qfDm2CPRTbn+Izez+41e2vK969pnuuZKJtxTrKpOF3+i+3bXbMlU0t6QA1Z/Pf2el2eHf+WDAQ/Dk8YXP9lQGnzhR1NnPy9yHn70'
        b'gn1V6utt5Ye1nSK+LVvVuNNb+f46q19oNVc2tDpsNVv3YNMxizecX/3IdEd3+Mnxtt8fzFALf2vs/Mt+r3qUXuwP7fB/OzTB2yTE9oX9dkNG+4aa+4+bTDknvd55ZSJ7'
        b'+EPL0uF2P4f2l8MTbH9oX/CLXssf6v7gNzc3Tv386ND3tvzA36Byw1+vZ9oFaFUovvPBcYPpf33xqOvvbW9GuP26xHK2t2n6SMKPtVoCXqgLSf1w/YdndiRn/MDA549/'
        b'e+nbwz8IFGTqS362+ze5F0db/jru/P2fHjrt/0J756s7bzR6BirYl9ubBAe4aZi34Zdtf/1U77sKr2s2q36u98vPr5xM++c+13/Kh05YftoTHXUw71RhmcHLl9WdG5Kz'
        b'b7974mDhVbe/JL6csuXPif9qv9T5xxd/XvdtnY+OrnnTu//tHzd+V+V9ufn67+hPqrw5uKlS8uHH+3X/aPLv0bove6N81+99a2i85p/mlsF516sTm+6/9Zsfnv9zx77T'
        b'+3O2dn+vwvelm/62Qz8+9ZLvd5Wc/D4+Menj+531vxxMd48O+nzz3Y0fBKt/vvdbLY9KNr340LR49yufX0qWK/5nw6Sd8s8DMr/8LDzyzM3pXWtfaf7Wq3s9fvjFu55f'
        b'nJox/atn82cmKX7vzKe+fed3e0RJPa0GX4rWXzhVqZhspsSlfRH3HrxEiEzo0qHGyEix2nUuCv7oNbzLRbhivcHKej8SNa7Jgzthfr3yasluxDoeiLF/G/bxtUdIZNmt'
        b'HK+qqErsvUA9np5IUiG2PC4j0E8VKySd42uEZBH/WnwqGceSr6rKCfQcYTRJhvhFGhRxFVH2YvWdhGsqV5NwXB3yoVBdQVWJZMfmDerXZAVmamLstYLpRAt6UsV649KD'
        b'OpYLj6pfg6KF0d3FckSBchO4bK79ahuVpU/IChQuO+MD0XYilw8SWWDyZn+YSoAihauqjFiP7LCBvFWGw1E5mDMyTjRh+2mHcmOSkweYT2uhcN3j1VuuXn6ybZ3d/9uo'
        b'0v/nf5jpc6T1/y9/8E3HL12Kjg0KvXSJC7r+Gf0hsBCJRMKdwk1fikQsT01LpCAjFirIyInoR0ZNVktLS1Fjk8b/Le5aY6M47vi+7nzm7OP8oHV4mJgjKWf77BjjAOFV'
        b'HExqzncmwSThubnHnr34HuvdPWxoLIMDCcbYkDglKVJCIeFlMLENThyHkHRGaRUlNf1U2pGqRKraKIkUfwgij35o5z9rm6hSPrSqhFb3u92d2dl57c5/7ub3+2e47bkz'
        b'8vMkIb+2YAGN38FVgrTJMliELUoC7Bd20LT4gvvWwTlZ4FdaS7QjAv8QfD8xfcZesGX2WrfoEnPdAl/awXkEfp0V4hGKBS/9lFDcx12SWGyhlJ2BbR93VoJl1f+0TwuY'
        b'A2ej4AcfvWF6WbOofwoFv7PUe/Hd7xR3rTPyVmWwZdZQRfBmMeD9yN3UftzXFjBiV0rUnuymJvFRcF82fG8d6kJHMzjXPeI81BtWf7vggmgU8ByX85d/VfUsD4pr3TUX'
        b'Gz+J3/hHIstetPBBPjbrowqH+ztHjrlCDzsXvz4xdvBt92efFtxa8kxx23u3vmi9efr+2vm3gnOGBq9Lv/+yLXLz+Pjx34wNuVqzdoxnrRqvSnxecrJ91uC56rKPBzye'
        b'WVcu5u4myec8uOxnz676as7Z7bvGFm9a3lf87UR5/fH+G6c+vD4uunxrpYHYxYaJ/XP7c5xrbyx5Y+7WIy990nmiYkL9utpo/tOf9w+tGTjT8dpE9ZYLmefO5n3oG/nD'
        b'X99c8/dCh5hV9EDnwYp4w8vv7+/27h50zlx92/3U/CKXdsizbtnvMsMLl31wz3jLftflP35QldS6Cx+Ljj7cK3zT9r5nwy25/MvR4GrxzZu38w6m3jvdsr3669ve+YxY'
        b'TGfHA+Ctqau+nklOZLSjVzknGhbwefxWkLGm1Qga89f78BBEqvfNyRO4HHxNRKc2bGRDmRd31VgtQcezFQsC8PsObYhcsZDbwbSgIqi7BkRWA+hQKoOzS4KjCF2zhNJG'
        b'0YF5uNuJhsrtHL+Jmqct+B1Gtg6j18wS3LsIRKqO8FxmA+oqE2iLX1lo0byHs9GJKckvKchv3kRnSp3oiiVOdRxfqwJ2no8a2pNxXPiwGGxHY2xUbumIT/PPH5HofOQV'
        b'1M+IJ6Am9qKVbKAW93hr6ZTsqsTl4j4RjS3dxagre+ms85x/Q2mwqpLnYJnAMH5BsC9AL1rM+Us/f9i/uJJezJS+5tls3MwicQUeTltZe36pG4JrAxCKTquQs8siTByu'
        b'W45tf7UT9eNucMJ3lBrMj/J4FA+hd7ahqxZv5jydMD8LNMBAKcdJFXzFNjrNPoA6LfZ8r/+nJT7cA+z5BI8PRtFoIz7JSkYveR0NlIDSXR3cOrBTpTUgcXPaJdQZS0yK'
        b'em3GfX7IGi0/rXV8qINzegWat/O7WU/AL5n4OeNOBDSoczNqBTS4faOlHjayCv/aiYdn4hEDdeG3NHy1hZok2Rw3V0ZDHinj0RqrcZ3oMOMhlUBaXGE17XEnBHy6udUq'
        b'5Ls5y3/oyLYF/txAg7TxQBN7TSk640cDi2jrgvAY6jLQvnpWmz3lQZ/Xzj1Sk/E0egMfsDQA+9EIfsFJ7YSrmgNUv58HubQRjt2oHV8uhzXTgbr6JfiYjbM9zdNaOoYu'
        b'MJJ6aG4DBPpA7bvFh67XWRbY7LREW+DKlBBa/+P4JK3zwyCKWAdKZUfwqfsF1G3iXqtNeoq2lGzwlQZ8ZXwK9XFZs8QZDzWxZ2/mDtTtp03iL6MX08fH68GH7FxepYhf'
        b'XYnPWFpol5iK9y9Ki4H1eYS3VXJOfAwYHGfzmWocehf3BUsEdIBO1ng/h1+ub53ygLTo7r/f/0+jxE/uglFyx2GxBsORy8E48w625TNhNcckMxPIXmBpwF7upINiGlNM'
        b'/vfEsantAYs9xeyFYiLGlaSu0rGM2My0FleIFFcNk0hRNUIxpSlJIhqmTmzhPaZiECmcSsWJqCZNYotRu4p+6aFko0JsalJLm0SMNOlETOlRYo+pcVOhB4mQRsS9qkZs'
        b'ISOiqkRsUtpoFJr8DNVQk4YZSkYUYtfS4bgaIVk1FosxEGqmF2dpumKaamyP3JaIE0ddKtK8XqWZzAxXPqgkQaaKZKtGSjbVhEITSmhEWr9x3XqSrYV0Q5FpEBC8SU4i'
        b'FV2+1PL7IUfVRtUkGaFIRNFMg2SzgslmipqJyUYiPhmoI06jSY2ZsqLrKZ1kp5ORppCaVKKy0hYhmbJsKLSqZJm4kik5FY6ljQjz2EQypw5ocdJJ0Km6Y4lZ9b1IbwZb'
        b'TQNIAKQB2gCAFKiDVxs9CbAdYBuACRACeJJRZQF2AjQCPAWwA0AFSAFsBngCIAoAt9b3AOxlZDmALQBhgBaAOMAuADCT9d0AWwEeZykDn64V9n7JdPGmuYLQkTKnrarv'
        b'tv6oVcVifu+I0X6jRJrKiFuWJ/cnjfPvZ08e36uFIs0gWQacVghTokGvg7H+SIYsh+JxWbY6MOMFgm84Yrf8tOp/gzPtU8bwf/h/Jo6VtBek48pqcCdngFNpCcyF//1B'
        b'2pzPdAr/Dflyiyo='
    ))))
