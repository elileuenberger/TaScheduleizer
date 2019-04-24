from django.test import TestCase
from Main.models import Account
from django.test import Client


class TestAccount(TestCase):
    def setUp(self):

        self.account1 = Account.objects.create(userName="cwhitley", firstName="Chip", lastName="Whitley",
                                               email="cwhitley@uwm.edu", title=1, address="123 Fake Street",
                                               city="Springfield", state="IL", zipCode="90210", officeNumber=102,
                                               officePhone="555-1235", officeDays='W', officeHoursStart=1300,
                                               officeHoursEnd=1400, homePhone="555-5555")

    def test_displayPublic_TA(self):
        self.assertMultiLineEqual(self.account1.displayPublic(), "Chip Whitley\n"
                                                                 "Teaching Assistant\n"
                                                                 "Email: cwhitley@uwm.edu\n"
                                                                 "Office: 102\n"
                                                                 "Office Phone: 555-1235\n"
                                                                 "Office Hours: W 1300 1400")

    def test_displayPublic_Instructor(self):
        self.account1.title = 2

        self.assertMultiLineEqual(self.account1.displayPublic(), "Chip Whitley\n"
                                                                 "Instructor\n"
                                                                 "Email: cwhitley@uwm.edu\n"
                                                                 "Office: 102\n"
                                                                 "Office Phone: 555-1235\n"
                                                                 "Office Hours: W 1300 1400")
