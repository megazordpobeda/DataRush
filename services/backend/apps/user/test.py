import json
from django.test import TestCase

from apps.user.models import User


class SignUpAPITestCase(TestCase):
    def test_successful_sign_up(self):
        payload = {
            "email": "user@example.com",
            "password": "securepassword123",
            "username": "123",
        }
        response = self.client.post(
            "/api/v1/sign-up",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.json())
        self.assertEqual(User.objects.count(), 1)

    def test_missing_required_fields(self):
        payload = {"password": "testpass123", "username": "sffsdf"}
        response = self.client.post(
            "/api/v1/sign-up",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_email_format(self):
        payload = {
            "email": "ervtb uktr bym",
            "password": "securepassword123",
            "username": "123",
        }
        response = self.client.post(
            "/api/v1/sign-up",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_existing_user_conflict(self):
        User.objects.create(
            email="existing@example.com", password="existingpass123", username="testing"
        )
        payload = {
            "email": "existing@example.com",
            "password": "sfsad",
            "username": "testing",
        }
        response = self.client.post(
            "/api/v1/sign-up",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("detail", response.json())
