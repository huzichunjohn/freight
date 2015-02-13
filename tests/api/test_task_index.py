from __future__ import absolute_import, unicode_literals

import json

from ds.models import Task, TaskStatus
from ds.testutils import TestCase


class TaskIndexBase(TestCase):
    path = '/api/0/tasks/'

    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        super(TaskIndexBase, self).setUp()


class TaskListTest(TaskIndexBase):
    def setUp(self):
        super(TaskListTest, self).setUp()

    def test_no_filters(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

    def test_status_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
            status=TaskStatus.pending,
        )
        resp = self.client.get(self.path + '?status=pending')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?status=in_progress')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0

    def test_app_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path + '?app=' + self.app.name)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?app=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0

    def test_user_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path + '?user=' + self.user.name)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?user=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0

    def test_env_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path + '?env=' + task.environment)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?env=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0

    def test_ref_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path + '?ref=' + task.ref)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?ref=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0


class TaskCreateTest(TaskIndexBase):
    def test_simple(self):
        resp = self.client.post(self.path, data={
            'env': 'production',
            'app': self.app.name,
            'ref': 'master',
            'user': self.user.name,
        })
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['id']

        task = Task.query.get(data['id'])
        assert task.environment == 'production'
        assert task.app_id == self.app.id
        assert task.ref == 'master'
        assert task.user_id == self.user.id

    def test_locked(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
            status=TaskStatus.pending,
        )

        resp = self.client.post(self.path, data={
            'env': task.environment,
            'app': self.app.name,
            'ref': 'master',
            'user': self.user.name,
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'locked'
