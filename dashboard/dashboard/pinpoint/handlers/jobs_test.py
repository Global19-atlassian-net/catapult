# Copyright 2017 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import json
import mock

from dashboard.pinpoint.handlers import jobs
from dashboard.pinpoint.models import job as job_module
from dashboard.pinpoint.models import results2 as results2_module
from dashboard.pinpoint import test
from dashboard.common import utils

_SERVICE_ACCOUNT_EMAIL = 'some-service-account@example.com'


class JobsTest(test.TestCase):

  @mock.patch.object(utils,
                     'ServiceAccountEmail', lambda: _SERVICE_ACCOUNT_EMAIL)
  @mock.patch.object(results2_module, 'GetCachedResults2', return_value="")
  def testGet_NoUser(self, _):
    job = job_module.Job.New((), ())

    data = json.loads(self.testapp.get('/api/jobs?o=STATE').body)

    self.assertEqual(1, data['count'])
    self.assertEqual(1, len(data['jobs']))
    self.assertEqual(job.AsDict([job_module.OPTION_STATE]), data['jobs'][0])

  @mock.patch.object(utils,
                     'ServiceAccountEmail', lambda: _SERVICE_ACCOUNT_EMAIL)
  @mock.patch.object(results2_module, 'GetCachedResults2', return_value="")
  def testGet_WithUserFilter(self, _):
    job_module.Job.New((), ())
    job_module.Job.New((), (), user='lovely.user@example.com')
    job = job_module.Job.New((), (), user='lovely.user@example.com')

    data = json.loads(
        self.testapp.get(
            '/api/jobs?o=STATE&filter=user=lovely.user@example.com').body)

    # We now always explicitly get all the jobs, unless we explicitly filter
    # for a user's own jobs.
    self.assertEqual(2, data['count'])
    self.assertEqual(2, len(data['jobs']))

    sorted_data = sorted(data['jobs'], key=lambda d: d['job_id'])
    self.assertEqual(job.AsDict([job_module.OPTION_STATE]), sorted_data[-1])

  @mock.patch.object(utils,
                     'ServiceAccountEmail', lambda: _SERVICE_ACCOUNT_EMAIL)
  @mock.patch.object(jobs.utils, 'GetEmail',
                     mock.MagicMock(return_value=_SERVICE_ACCOUNT_EMAIL))
  @mock.patch.object(results2_module, 'GetCachedResults2', return_value="")
  def testGet_WithServiceAccountUser(self, _):
    job_module.Job.New((), ())
    job_module.Job.New((), (), user=_SERVICE_ACCOUNT_EMAIL)
    job = job_module.Job.New((), (), user=_SERVICE_ACCOUNT_EMAIL)

    data = json.loads(
        self.testapp.get('/api/jobs?o=STATE&filter=user=%s' %
                         (_SERVICE_ACCOUNT_EMAIL,)).body)

    self.assertEqual(2, data['count'])
    self.assertEqual(2, len(data['jobs']))
    self.assertEqual(data['jobs'][0]['user'], 'chromeperf (automation)')
    self.assertEqual(data['jobs'][1]['user'], 'chromeperf (automation)')

    sorted_data = sorted(data['jobs'], key=lambda d: d['job_id'])
    expected_job_dict = job.AsDict([job_module.OPTION_STATE])
    expected_job_dict['user'] = 'chromeperf (automation)'
    self.assertEqual(expected_job_dict, sorted_data[-1])
