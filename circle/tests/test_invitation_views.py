from circle.models import CircleInvitation, CircleRole
from rest_framework.test import APITestCase

from .factories import CircleFactory, CircleInvitationFactory, UserFactory
from .util import url


class ViewInvitationsTest(APITestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.admin = UserFactory()
        self.circle = CircleFactory(owners=[self.owner], admins=[self.admin])
        invitation = CircleInvitationFactory(circle=self.circle)
        self.invitee = invitation.invitee

    def test_admin_can_view_invitations(self):
        self.client.login(email=self.admin.email, password="testpassword")

        response = self.client.get(f"/invitations/?circle={self.circle.pk}")
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["invitee"], self.invitee.email)
        self.assertEqual(data[0]["circle"], url("circle-detail", pk=self.circle.pk))

    def test_owner_can_view_invitations(self):
        self.client.login(email=self.owner.email, password="testpassword")

        response = self.client.get(f"/invitations/?circle={self.circle.pk}")
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["invitee"], self.invitee.email)
        self.assertEqual(data[0]["circle"], url("circle-detail", pk=self.circle.pk))

    def test_invitee_can_view_invitations(self):
        self.client.login(email=self.invitee.email, password="testpassword")

        response = self.client.get("/invitations/")
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["invitee"], self.invitee.email)
        self.assertEqual(data[0]["circle"], url("circle-detail", pk=self.circle.pk))


class CreateInvitationsTest(APITestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.admin = UserFactory()
        self.member = UserFactory()
        self.circle = CircleFactory(
            owners=[self.owner], admins=[self.admin], members=[self.member]
        )

    def user_can_invite_people(self, user):
        self.client.login(email=user.email, password="testpassword")
        invitee = UserFactory()

        response = self.client.post(
            "/invitations/",
            {
                "circle": url("circle-detail", pk=self.circle.pk),
                "invitee": invitee.email,
                "role": CircleRole.MEMBER,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["invitee"], invitee.email)
        self.assertEqual(
            response.data["circle"], url("circle-detail", pk=self.circle.pk)
        )

    def test_owner_can_invite_people(self):
        self.user_can_invite_people(self.owner)

    def test_admin_can_invite_people(self):
        self.user_can_invite_people(self.admin)

    def test_member_cannot_invite_people(self):
        self.client.login(email=self.member.email, password="testpassword")
        invitee = UserFactory()

        response = self.client.post(
            "/invitations/",
            {
                "circle": url("circle-detail", pk=self.circle.pk),
                "invitee": invitee.email,
                "role": CircleRole.MEMBER,
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_other_user_cannot_invite_people(self):
        user = UserFactory()
        self.client.login(email=user.email, password="testpassword")
        invitee = UserFactory()

        response = self.client.post(
            "/invitations/",
            {
                "circle": url("circle-detail", pk=self.circle.pk),
                "invitee": invitee.email,
                "role": CircleRole.MEMBER,
            },
        )

        self.assertEqual(response.status_code, 403)


class AcceptInvitationTest(APITestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.circle = CircleFactory(owners=[self.owner])
        self.invitation = CircleInvitationFactory(circle=self.circle)
        self.invitee = self.invitation.invitee

    def test_invitee_can_accept_invitation(self):
        self.client.login(email=self.invitee.email, password="testpassword")
        response = self.client.patch(
            f"/invitations/{self.invitation.pk}/", {"accepted": True}
        )

        self.assertEqual(response.status_code, 204)
        self.assertTrue(
            CircleInvitation.objects.filter(invitee=self.invitee, circle=self.circle)
            .get()
            .accepted
        )
        self.assertEqual(self.circle.memberships.filter(user=self.invitee).count(), 1)

    def test_other_user_cannot_accept_invitation(self):
        user = UserFactory()
        self.client.login(email=user.email, password="testpassword")
        response = self.client.patch(
            f"/invitations/{self.invitation.pk}/", {"accepted": True}
        )

        self.assertEqual(response.status_code, 403)


class DeleteInvitationTest(APITestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.admin = UserFactory()
        self.circle = CircleFactory(owners=[self.owner], admins=[self.admin])
        self.invitation = CircleInvitationFactory(circle=self.circle)
        self.invitee = self.invitation.invitee

    def can_delete_invitation(self, user):
        self.client.login(email=user.email, password="testpassword")
        response = self.client.delete(f"/invitations/{self.invitation.pk}/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            CircleInvitation.objects.filter(
                invitee=self.invitee, circle=self.circle
            ).count(),
            0,
        )

    def test_invitee_can_delete_invitation(self):
        self.can_delete_invitation(self.invitee)

    def test_admin_can_delete_invitation(self):
        self.can_delete_invitation(self.admin)

    def test_owner_can_delete_invitation(self):
        self.can_delete_invitation(self.owner)

    def test_other_user_cannot_delete_invitation(self):
        user = UserFactory()
        self.client.login(email=user.email, password="testpassword")
        response = self.client.delete(f"/invitations/{self.invitation.pk}/")
        self.assertEqual(response.status_code, 403)
