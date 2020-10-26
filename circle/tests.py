from rest_framework.test import APITestCase
from .models import Circle, CircleInvitation, User, CircleMembership, CircleRole
from datetime import date

# Create your tests here.

class UpdateCircleTest(APITestCase):
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
        self.client.login(username=self.owner.email, password='badpassword')

        response = self.client.patch(f"/circles/{self.circle.pk}/", {
            "name": "New name"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('name'), 'New name')

    def test_member_cannot_update_circle(self):
        self.client.login(username=self.member.email, password='badpassword')

        response = self.client.patch(f"/circles/{self.circle.pk}/", {
            "name": "New name"
        })

        self.assertEqual(response.status_code, 403)

class ViewInvitationsTest(APITestCase):
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
        self.admin = User.objects.create_user(
            email='admin@example.org',
            name="Admin",
            date_of_birth=date.today(),
            password="badpassword"
        )
        CircleMembership.objects.create(
            circle=self.circle,
            user=self.admin,
            role=CircleRole.ADMIN
        )
        self.invitee = User.objects.create_user(
            email='invitee@example.org',
            name="Invitee",
            date_of_birth=date.today(),
            password="badpassword"
        )
        CircleInvitation.objects.create(
            invitee=self.invitee,
            circle=self.circle,
            role=CircleRole.MEMBER
        )

    def test_owner_can_view_invitations(self):
        self.client.login(email=self.admin.email, password="badpassword")

        response = self.client.get(f'/invitations/?circle={self.circle.pk}')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['invitee'], self.invitee.email)

    def test_owner_can_view_invitations(self):
        self.client.login(email=self.owner.email, password="badpassword")

        response = self.client.get(f'/invitations/?circle={self.circle.pk}')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['invitee'], self.invitee.email)

    def test_invitee_can_view_invitations(self):
        self.client.login(email=self.invitee.email, password="badpassword")

        response = self.client.get(f'/invitations/')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['invitee'], self.invitee.email)
