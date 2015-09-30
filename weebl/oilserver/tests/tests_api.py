#! /usr/bin/env python3
import utils
from freezegun import freeze_time
from common_test_methods import ResourceTests
from oilserver import models


class TimeStampedBaseModelTest(ResourceTests):

    def test_save_generates_timestamps(self):
        with freeze_time("Jan 1 2000 00:00:00"):
            timestamp1 = utils.time_now()
            # Environment uses TimeStampedBaseModel and is easy to
            # make.
            environment = models.Environment(name="environment")
            environment.save()
        self.assertEqual(environment.created_at, timestamp1)
        self.assertEqual(environment.updated_at, timestamp1)
        with freeze_time("Jan 2 2000 00:00:00"):
            timestamp2 = utils.time_now()
            environment.save()
        self.assertEqual(environment.created_at, timestamp1)
        self.assertEqual(environment.updated_at, timestamp2)


class EnvironmentResourceTest(ResourceTests):
    def test_get_specific_environment_by_name(self):
        """GET a specific environment instance by its name."""
        name = "mock_production"
        r_dict0 = self.make_environment(name)
        response = self.api_client.get('/api/{}/environment/by_name/{}/'
                                       .format(self.version, name),
                                       format='json')
        r_dict1 = self.deserialize(response)

        self.assertEqual(r_dict0, r_dict1)
        self.assertEqual(response.status_code, 200,
                         msg="Incorrect status code")
