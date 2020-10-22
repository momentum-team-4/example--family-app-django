from django.test import TestCase
from rest_framework.test import APIClient
from .models import Circle, User, CircleMembership, CircleRole
from datetime import date

# Create your tests here.

class UpdateCircleTest(TestCase):
    def setUp(self):
        self.circle = Circle.objects.create(name="Test Circle")
        self.owner = User.objects.create_user(
            email='owner@example.org',
            name="Owner",
            date_of_birth=date.today(),
            password="badpassword"
        )
        CircleMembership.objects.create(
            circle=self.circle,
            user=self.owner,
            role=CircleRole.OWNER
        )
        self.member = User.objects.create_user(
            email='member@example.org',
            name="Member",
            date_of_birth=date.today(),
            password="badpassword"
        )
        CircleMembership.objects.create(
            circle=self.circle,
            user=self.member,
            role=CircleRole.MEMBER
        )

    def test_owner_can_update_circle(self):
        client = APIClient()
        client.login(username=self.owner.email, password='badpassword')

        response = client.patch(f"/circles/{self.circle.pk}/", {
            "name": "New name"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('name'), 'New name')

    def test_member_cannot_update_circle(self):
        client = APIClient()
        client.login(username=self.member.email, password='badpassword')

        response = client.patch(f"/circles/{self.circle.pk}/", {
            "name": "New name"
        })

        self.assertEqual(response.status_code, 403)
