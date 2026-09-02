from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIRequestFactory
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status
from academics.tests.base import BaseAPITestSetup
from academics.models import Department
from django.contrib.auth.models import AnonymousUser

@override_settings(DEBUG=True)
class QueryCountTest(BaseAPITestSetup):
    def test_list_departments_query_count(self):
        Department.objects.create(name="Math", code="MATH")
        Department.objects.create(name="Physics", code="PHY")
        self.client.force_authenticate(user=self.student)
        with self.assertNumQueries(2):
            response = self.client.get('/api/v1/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ThrottleUnitTest(BaseAPITestSetup):
    def setUp(self):
        super().setUp()
        cache.clear()  # clear throttle cache

    def test_user_rate_throttle(self):
        factory = APIRequestFactory()
        request = factory.get('/api/v1/departments/')
        request.user = self.student
        throttle = UserRateThrottle()
        throttle.rate = '3/min'
        throttle.num_requests, throttle.duration = throttle.parse_rate('3/min')

        self.assertTrue(throttle.allow_request(request, None))
        self.assertTrue(throttle.allow_request(request, None))
        self.assertTrue(throttle.allow_request(request, None))
        self.assertFalse(throttle.allow_request(request, None))

    def test_anon_rate_throttle(self):
        factory = APIRequestFactory()
        request = factory.get('/api/v1/departments/')
        request.user = AnonymousUser()
        throttle = AnonRateThrottle()
        throttle.rate = '2/min'
        throttle.num_requests, throttle.duration = throttle.parse_rate('2/min')

        self.assertTrue(throttle.allow_request(request, None))
        self.assertTrue(throttle.allow_request(request, None))
        self.assertFalse(throttle.allow_request(request, None))