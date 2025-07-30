# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase


class AccountBatchTestCase(ModuleTestCase):
    "Test Account Batch module"
    module = 'account_batch'


del ModuleTestCase
