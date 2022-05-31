import time
from pathlib import Path

import pytest
from django.conf import settings
from django.test import TestCase

from .models import JobStatus
from .services import TrainService


# Create your tests here.
class TestTrainIntegration(TestCase):
    def setUp(self):
        self.data_dir = Path(settings.DATA_DIR)
        self.tub_paths = [
            f"{str(self.data_dir)}/tub_2_21-12-07"]
        self.job_uuids = ["02902f0d-d454-4392-9a96-f587a27aed46", "a241a201-bdca-4a97-8a3f-67c5c3ea3966"]

    # @pytest.mark.slow
    # def test_submit_job(self):
    #     client = Client()
    #     data = dict()
    #     data["tub_paths"] = [str(self.data_dir / "tub_18_19-04-06")]

    #     response = client.post(
    #         reverse('train:submit_job'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )

    #     assert response.status_code == status.HTTP_200_OK

        # mock_method.assert_called_with(data["tub_paths"])

    @pytest.mark.slow
    def test_submit_job(self):
        TrainService.submit_job(self.tub_paths)

    @pytest.mark.slow
    def test_refresh_jobs(self):
        TrainService.get_latest_job_status_from_hq(self.job_uuids)

    @pytest.mark.slow
    def test_upload_job_to_s3(self):
        job = TrainService.create_job(self.tub_paths)
        TrainService.upload_job_to_s3(job.uuid, self.tub_paths)

    @pytest.mark.slow
    def test_launch_ec2_instance_integration(self):
        job = TrainService.create_job(self.tub_paths)
        TrainService.upload_job_to_s3(job.uuid, self.tub_paths)

        instance_type = settings.INSTANCE_TYPE
        spot_request_id = TrainService.launch_ec2_instance(job.uuid, instance_type, 2, 10) is not None

        assert job.status == JobStatus.SCHEDULED
        time.sleep(10)
        job = TrainService.refresh_job_status(job.uuid)

        assert job.status == JobStatus.TRAINING
        assert job.ec2_instance_id is not None

        time.sleep(60*5)
        assert TrainService.is_training_completed(job) is True

        # test model file publicly accessible


        # assert ec2 instance shutdown


    @pytest.mark.slow
    def test_get_latest_job_status_from_hq(self):
        job_uuids = ["19460b57-27fa-4e7d-8a79-9434af0f9629"]

        result = TrainService.get_latest_job_status_from_hq(job_uuids)
        assert len(result) == 1
        assert 'status' in result[0]
