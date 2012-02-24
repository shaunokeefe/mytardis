from flexmock import flexmock
from django.test import TestCase

from tardis.tardis_portal.models import Experiment

from tardis.apps.sync.consumer_fsm import Complete, InProgress, FailPermanent, \
        CheckingIntegrity, Requested, Ingested
from tardis.apps.sync.tasks import clock_tick
from tardis.apps.sync.models import SyncedExperiment
from ..transfer_service import TransferClient, TransferService
from ..integrity import IntegrityCheck

from django.contrib.auth.models import User


class consumerFSMTestCase(TestCase):

    def load_test_stub(self):
        pass

    def setUp(self):
        pass

    def finishes_on_hard_fail(func):
        pass

    def finishes_on_complete(func):
        pass

    @finishes_on_complete
    def testRegularProgression(self):
        pass

    @finishes_on_hard_fail
    def testTranferFailure(self):
        pass

    @finishes_on_hard_fail
    def testHardFail(self):
        pass


