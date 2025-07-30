==================================
Account Batch Line Update Scenario
==================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> from trytond.modules.account_batch.tests.tools import \
    ...     create_tax, create_tax_code, create_tax_code_line
    >>> today = datetime.date.today()
    >>> tomorrow = today + datetime.timedelta(days=1)

Install account_batch::

    >>> config = activate_modules('account_batch')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> fiscalyear.save()
    >>> period_ids = [p.id for p in fiscalyear.periods]
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> receivable = accounts['receivable']
    >>> payable = accounts['payable']
    >>> cash = accounts['cash']
    >>> tax = accounts['tax']

Create tax groups::

    >>> TaxCode = Model.get('account.tax.code')
    >>> TaxGroup = Model.get('account.tax.group')

    >>> group_ust = TaxGroup()
    >>> group_ust.name = 'Ust.'
    >>> group_ust.code = 'ust'
    >>> group_ust.kind = 'sale'
    >>> group_ust.save()

    >>> group_vst = TaxGroup()
    >>> group_vst.name = 'Vst.'
    >>> group_vst.code = 'vst'
    >>> group_vst.kind = 'purchase'
    >>> group_vst.save()

Create taxes and tax codes: VAT Sale::

    >>> tax_out = create_tax('USt. 19%', Decimal('0.19'))
    >>> tax_out.group = group_ust
    >>> tax_out.save()

    >>> base19out = create_tax_code('Base Out', tax_out)
    >>> base19out.save()
    >>> base19out_line1 = create_tax_code_line(base19out, tax_out,
    ...     operator='+', type='invoice', amount='base')
    >>> base19out_line1.save()
    >>> base19out_line2 = create_tax_code_line(base19out, tax_out,
    ...     operator='-', type='credit', amount='base')
    >>> base19out_line2.save()
 
    >>> tax19out = create_tax_code('Tax Out', tax_out)
    >>> tax19out.save()
    >>> tax19out_line1 = create_tax_code_line(tax19out, tax_out,
    ...     operator='+', type='invoice', amount='tax')
    >>> tax19out_line1.save()
    >>> tax19out_line2 = create_tax_code_line(tax19out, tax_out,
    ...     operator='-', type='credit', amount='tax')
    >>> tax19out_line2.save()

Create taxes and tax codes: VAT Purchase::

    >>> tax_in = create_tax('VSt. 19%', Decimal('0.19'))
    >>> tax_in.group = group_vst
    >>> tax_in.save()

    >>> base19in = create_tax_code('Base In', tax_in)
    >>> base19in.save()
    >>> base19in_line1 = create_tax_code_line(base19in, tax_in,
    ...     operator='+', type='invoice', amount='base')
    >>> base19in_line1.save()
    >>> base19in_line2 = create_tax_code_line(base19in, tax_in,
    ...     operator='-', type='credit', amount='base')
    >>> base19in_line2.save()
 
    >>> tax19in = create_tax_code('Tax In', tax_in)
    >>> tax19in.save()
    >>> tax19in_line1 = create_tax_code_line(tax19in, tax_in,
    ...     operator='+', type='invoice', amount='tax')
    >>> tax19in_line1.save()
    >>> tax19in_line2 = create_tax_code_line(tax19in, tax_in,
    ...     operator='-', type='credit', amount='tax')
    >>> tax19in_line2.save()

Create taxes and tax codes: Nested VAT Intracommunity Purchase (Reverse Charge)::

    >>> tax_in_intra = create_tax('Steuerpflichtiger innergemeinschaftlicher Erwerb 19%', None, type='none')
    >>> tax_in_intra.group = group_vst
    >>> tax_in_intra.reverse_charge = True
    >>> tax_in_intra.save()

    >>> tax_in_intra_sub = create_tax('Innergem. Erwerb 19%USt/19%VSt', None, type='none')
    >>> tax_in_intra_sub.parent = tax_in_intra
    >>> tax_in_intra_sub.reverse_charge = True
    >>> tax_in_intra_sub.save()

    >>> tax_in_intra_sub_vst = create_tax('19% Vorsteuer aus innergem. Erwerb', Decimal('0.19'))
    >>> tax_in_intra_sub_vst.parent = tax_in_intra_sub
    >>> tax_in_intra_sub_vst.reverse_charge = True
    >>> tax_in_intra_sub_vst.save()

    >>> tax_in_intra_sub_ust = create_tax('19% Umsatzsteuer aus innergem. Erwerb', Decimal('-0.19'))
    >>> tax_in_intra_sub_ust.parent = tax_in_intra_sub
    >>> tax_in_intra_sub_ust.reverse_charge = True
    >>> tax_in_intra_sub_ust.save()

    >>> code_base19in_vst = create_tax_code(
    ...     'Vorsteuerbeträge aus dem innergemeinschaftlichen Erwerb von Gegenständen Netto (89)',
    ...     tax_in_intra_sub_vst)
    >>> code_base19in_vst.save()
    >>> code_base19in_vst_line1 = create_tax_code_line(code_base19in_vst, tax_in_intra_sub_vst,
    ...     operator='+', type='invoice', amount='base')
    >>> code_base19in_vst_line1.save()
    >>> code_base19in_vst_line2 = create_tax_code_line(code_base19in_vst, tax_in_intra_sub_vst,
    ...     operator='-', type='credit', amount='base')
    >>> code_base19in_vst_line2.save()

    >>> code_tax19in_vst = create_tax_code(
    ...     'Vorsteuerbeträge aus dem innergemeinschaftlichen Erwerb von Gegenständen Steuer (61)',
    ...     tax_in_intra_sub_vst)
    >>> code_tax19in_vst.save()
    >>> code_tax19in_vst_line1 = create_tax_code_line(code_tax19in_vst, tax_in_intra_sub_vst,
    ...     operator='+', type='invoice', amount='tax')
    >>> code_tax19in_vst_line1.save()
    >>> code_tax19in_vst_line2 = create_tax_code_line(code_tax19in_vst, tax_in_intra_sub_vst,
    ...     operator='-', type='credit', amount='tax')
    >>> code_tax19in_vst_line2.save()
 
    >>> code_tax19in_ust = create_tax_code(
    ...     'Steuerpflichtige innergemeinschaftliche Erwerbe Steuer (891)',
    ...     tax_in_intra_sub_ust)
    >>> code_tax19in_ust.save()
    >>> code_tax19in_ust_line1 = create_tax_code_line(code_tax19in_ust, tax_in_intra_sub_ust,
    ...     operator='+', type='invoice', amount='tax')
    >>> code_tax19in_ust_line1.save()
    >>> code_tax19in_ust_line2 = create_tax_code_line(code_tax19in_ust, tax_in_intra_sub_ust,
    ...     operator='-', type='credit', amount='tax')
    >>> code_tax19in_ust_line2.save()

Create taxes and tax codes: Nested VAT Sale (Reverse Charge)::

    >>> # While this tax is not really applicable in EU, it should also work just in case.

    >>> tax_out_intra = create_tax('Steuerpflichtige Lieferung Reverse Charge 19%', None, type='none')
    >>> tax_out_intra.group = group_ust
    >>> tax_out_intra.reverse_charge = True
    >>> tax_out_intra.save()

    >>> tax_out_intra_sub = create_tax('Lieferung Reverse Charge 19%VSt/19%USt', None, type='none')
    >>> tax_out_intra_sub.parent = tax_out_intra
    >>> tax_out_intra_sub.reverse_charge = True
    >>> tax_out_intra_sub.save()

    >>> tax_out_intra_sub_vst = create_tax('19% Vorsteuer aus innergem. Lieferung', Decimal('-0.19'))
    >>> tax_out_intra_sub_vst.parent = tax_out_intra_sub
    >>> tax_out_intra_sub_vst.reverse_charge = True
    >>> tax_out_intra_sub_vst.save()

    >>> tax_out_intra_sub_ust = create_tax('19% Umsatzsteuer aus innergem. Lieferung', Decimal('0.19'))
    >>> tax_out_intra_sub_ust.parent = tax_out_intra_sub
    >>> tax_out_intra_sub_ust.reverse_charge = True
    >>> tax_out_intra_sub_ust.save()

    >>> code_base19out_vst = create_tax_code(
    ...     'Vorsteuerbeträge aus der innergemeinschaftlichen Lieferung von Gegenständen Netto (89x)',
    ...     tax_out_intra_sub_vst)
    >>> code_base19out_vst.save()
    >>> code_base19out_vst_line1 = create_tax_code_line(code_base19out_vst, tax_out_intra_sub_vst,
    ...     operator='+', type='invoice', amount='base')
    >>> code_base19out_vst_line1.save()
    >>> code_base19out_vst_line2 = create_tax_code_line(code_base19out_vst, tax_out_intra_sub_vst,
    ...     operator='-', type='credit', amount='base')
    >>> code_base19out_vst_line2.save()

    >>> code_tax19out_vst = create_tax_code(
    ...     'Vorsteuerbeträge aus dem innergemeinschaftlichen Lieferung von Gegenständen Steuer (61x)',
    ...     tax_out_intra_sub_vst)
    >>> code_tax19out_vst.save()
    >>> code_tax19out_vst_line1 = create_tax_code_line(code_tax19out_vst, tax_out_intra_sub_vst,
    ...     operator='+', type='invoice', amount='tax')
    >>> code_tax19out_vst_line1.save()
    >>> code_tax19out_vst_line2 = create_tax_code_line(code_tax19out_vst, tax_out_intra_sub_vst,
    ...     operator='-', type='credit', amount='tax')
    >>> code_tax19out_vst_line2.save()
 
    >>> code_tax19out_ust = create_tax_code(
    ...     'Steuerpflichtige innergemeinschaftliche Lieferungen Steuer (891x)',
    ...     tax_out_intra_sub_ust)
    >>> code_tax19out_ust.save()
    >>> code_tax19out_ust_line1 = create_tax_code_line(code_tax19out_ust, tax_out_intra_sub_ust,
    ...     operator='+', type='invoice', amount='tax')
    >>> code_tax19out_ust_line1.save()
    >>> code_tax19out_ust_line2 = create_tax_code_line(code_tax19out_ust, tax_out_intra_sub_ust,
    ...     operator='-', type='credit', amount='tax')
    >>> code_tax19out_ust_line2.save()

Create sequence and account journal::

    >>> Sequence = Model.get('ir.sequence')
    >>> SequenceType = Model.get('ir.sequence.type')
    >>> AccountJournal = Model.get('account.journal')

    >>> sequence_type, = SequenceType.find([('name', '=', "Account Journal")])
    >>> sequence = Sequence(name='Bank',
    ...     sequence_type=sequence_type,
    ...     company=company,
    ... )
    >>> sequence.save()
    >>> account_journal = AccountJournal(name='Bank',
    ...     type='bank',
    ...     sequence=sequence,
    ... )
    >>> account_journal.save()     

Create parties::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create a batch user::

    >>> User = Model.get('res.user')
    >>> Group = Model.get('res.group')
    >>> Party = Model.get('party.party')
    >>> Employee = Model.get('company.employee')
    >>> batch_user = User()
    >>> batch_user.name = 'Batch User'
    >>> batch_user.login = 'batch'
    >>> batch_group, = Group.find([('name', '=', 'Batch')])
    >>> batch_user.groups.append(batch_group)
    >>> account_group, = Group.find([('name', '=', 'Account')])
    >>> batch_user.groups.append(account_group)
    >>> employee_party = Party(name="Batch Employee")
    >>> employee_party.save()
    >>> employee = Employee(party=employee_party)
    >>> employee.save()
    >>> batch_user.employees.append(employee)
    >>> batch_user.employee = employee
    >>> batch_user.save()

.. comment:: We either work as batch_admin or batch_user to check
   correct permission settings
   

Create a batch admin::

    >>> batch_admin = User()
    >>> batch_admin.name = 'Batch Admin'
    >>> batch_admin.login = 'batch_admin'
    >>> account_admin_group, = Group.find([('name', '=', 'Account Administration')])
    >>> batch_admin.groups.append(account_admin_group)
    >>> batch_admin.save()

Create a batch journal (without optional account)::

    >>> config.user = batch_admin.id
    >>> config._context = User.get_preferences(True, config.context)
    >>> BatchJournal = Model.get('account.batch.journal')

    >>> batch_journal = BatchJournal(name='Batch Bank',
    ...     account_journal=account_journal,
    ...     currency=company.currency,
    ...     company=company,
    ... )
    >>> batch_journal.save()

Create a batch and check for missing account on journal::

    >>> config.user = batch_user.id
    >>> config._context = User.get_preferences(True, config.context)
    >>> Batch = Model.get('account.batch')
    >>> batch = Batch(name='Testbatch',
    ...     journal=batch_journal,
    ... )  # doctest: +IGNORE_EXCEPTION_DETAIL 
    Traceback (most recent call last):
        ...
    UserError: ...

Create a batch after configuring the journal with an account::

    >>> config.user = batch_admin.id
    >>> config._context = User.get_preferences(True, config.context)
    >>> batch_journal.account = cash
    >>> batch_journal.save()
    >>> batch = Batch(name='Testbatch',
    ...     journal=batch_journal,
    ... )
    >>> batch.save()

Create a revenue batch line without tax::

    >>> config.user = batch_user.id
    >>> config._context = User.get_preferences(True, config.context)
    >>> BatchLine = Model.get('account.batch.line')
    >>> batch_line1 = BatchLine(journal=batch_journal,
    ...     batch=batch,
    ...     date=today,
    ...     amount=Decimal(100),
    ...     account=cash,
    ...     contra_account=revenue,
    ... )
    >>> batch_line1.save()
    >>> batch_line1.side_account
    'debit'
    >>> batch_line1.side_contra_account
    'credit'
    >>> len(batch.lines)
    1
    >>> len(batch.move_lines)
    2
    
    >>> move_line1 = batch.move_lines[0]
    >>> move_line1.date == today
    True
    >>> move_line1.debit
    Decimal('100.00')
    >>> move_line1.credit
    Decimal('0')
    >>> move_line1.account == cash
    True
    >>> move_line1.description_used == cash.name
    True

    >>> move_line2 = batch.move_lines[1]
    >>> move_line2.date == today
    True
    >>> move_line2.debit
    Decimal('0')
    >>> move_line2.credit
    Decimal('100.00')
    >>> move_line2.account == revenue
    True
    >>> move_line2.description_used == revenue.name
    True


Change some data on the batch_line::

    >>> original_move_id = batch_line1.move.id
    >>> batch_line1.date = tomorrow
    >>> # new date may clear contra_account
    >>> batch_line1.contra_account = revenue
    >>> batch_line1.posting_text = 'new description'
    >>> batch_line1.reference = 'new reference'
    >>> batch_line1.amount = Decimal('110')
    >>> batch_line1.save()

Check for correctly updated data using the same move::

    >>> batch.reload()
    >>> batch_line1.move.id == original_move_id
    True
    >>> batch_line1.move.date == tomorrow
    True
    >>> batch_line1.move.reference
    'new reference'
    >>> batch_line1.move.description_used
    'new description'

Check for correct values on re-created move lines::

    >>> move_line1 = batch.move_lines[0]
    >>> move_line1.date == tomorrow
    True
    >>> move_line1.debit
    Decimal('110.00')
    >>> move_line1.credit
    Decimal('0')
    >>> move_line1.account == cash
    True
    >>> move_line1.description_used
    'new description'
    >>> move_line1.reference
    'new reference'

    >>> move_line2 = batch.move_lines[1]
    >>> move_line2.date == tomorrow
    True
    >>> move_line2.debit
    Decimal('0')
    >>> move_line2.credit
    Decimal('110.00')
    >>> move_line2.account == revenue
    True
    >>> move_line2.description_used
    'new description'
    >>> move_line2.reference
    'new reference'


