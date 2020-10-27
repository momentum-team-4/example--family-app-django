from circle.models import Circle, CircleMembership, CircleRole
from .factories import CircleFactory, UserFactory
from rest_framework.test import APITestCase

# Create your tests here.


class UpdateCircleTest(APITestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.circle = CircleFactory(owners=[self.owner], members=[self.member])

    def test_owner_can_update_circle(self):
        self.client.login(username=self.owner.email, password="testpassword")

        response = self.client.patch(
            f"/circles/{self.circle.pk}/", {"name": "New name"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("name"), "New name")

    def test_member_cannot_update_circle(self):
        self.client.login(username=self.member.email, password="testpassword")

        response = self.client.patch(
            f"/circles/{self.circle.pk}/", {"name": "New name"}
        )

        self.assertEqual(response.status_code, 403)
