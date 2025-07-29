import time
import os
import tempfile
import pytest
import random
import uuid

from retry import retry
from hyperpod_elastic_agent.logagent.log_agent import LogAgent, LogState, LogEvaluator

RETRY_DELAY = 1
RETRY_TIMEOUT = 60


class TestLogEvaluator(object):

    def test_without_threshold(self):
        # Match case 1
        rule = {
            'name': 'testRule',
            'logPattern': '.*',
        }
        input_cases = [
            "this is any log", "another random log that should be match"
        ]
        evaluator = LogEvaluator(rule, time.time())
        for log in input_cases:
            log_state = evaluator.evaluate(log)
            assert log_state == LogState.HEALTHY

        # Match case 2
        rule = {
            'name': 'testRule',
            'logPattern': '.+ (.+) TFLOPs.*',
        }
        input_cases = [
            "current throughput 12.5 TFLOPs",
            "training speed: 22.1 TFLOPs, 1.8 seconds per iteration"
        ]
        evaluator = LogEvaluator(rule, time.time())
        for log in input_cases:
            log_state = evaluator.evaluate(log)
            assert log_state == LogState.HEALTHY

        # Not match case 1
        rule = {
            'name': 'testRule',
            'logPattern': '.+ (.+) TFLOPs.*',
            'expectedStartCutOffInSeconds': 1,
        }
        input_cases = [
            "doing rendezvous...", "training speed: 1.8 seconds per iteration"
        ]

        evaluator = LogEvaluator(rule, time.time())
        time.sleep(rule["expectedStartCutOffInSeconds"] + 1)
        for log in input_cases:
            log_state = evaluator.evaluate(log)
            assert log_state == LogState.HANGING

        # Not match case 2
        rule = {
            'name': 'testRule',
            'logPattern': '.+ (.+) TFLOPs.*',
            'expectedRecurringFrequencyInSeconds': 1,
        }
        input_cases = ["doing rendezvous...", "current throughput 12.5 TFLOPs"]

        evaluator = LogEvaluator(rule, time.time())
        log_state = evaluator.evaluate(input_cases[0])
        assert log_state == LogState.WAITING
        log_state = evaluator.evaluate(input_cases[1])
        assert log_state == LogState.HEALTHY

        time.sleep(rule["expectedRecurringFrequencyInSeconds"] + 1)

        assert evaluator.evaluate(input_cases[0]) == LogState.HANGING
        assert evaluator.evaluate(input_cases[1]) == LogState.HEALTHY

    def test_with_threshold(self):
        # Match case 1
        threshold = 10
        rule = {
            "name": "TFLOPs",
            'logPattern': '.+ (.+) TFLOPs.*',
            'metricThreshold': threshold,
            "operator": "lt"
        }
        evaluator = LogEvaluator(rule, time.time())
        for _ in range(100):
            random_tflops = random.gauss(rule["metricThreshold"], 2)
            random_tflops = round(random_tflops, 2)
            log = f"training speed: {random_tflops:.2f} TFLOPs"

            is_slow = random_tflops < rule["metricThreshold"]
            log_state = evaluator.evaluate(log)
            assert log_state == LogState.SLOW if is_slow else log_state == LogState.HEALTHY, f"{random_tflops=}, {threshold=}, {is_slow=}, {log_state=}"


class TestLogAgent(object):

    @pytest.fixture
    def hanging_threshold(self):
        return 5

    @pytest.fixture
    def tflops_threshold(self):
        return 100

    @pytest.fixture
    def iterations_threshold(self):
        return 5

    @pytest.fixture
    def log_agent_config(self, hanging_threshold, tflops_threshold,
                         iterations_threshold):
        return [{
            "name": "TFLOPs",
            "logPattern": ".* (.+) TFLOPs.*",
            "expectedStartCutOffInSeconds": hanging_threshold,
            "expectedRecurringFrequencyInSeconds": hanging_threshold,
            "metricThreshold": tflops_threshold,
            "operator": "lt"
        }, {
            "name": "iterations/s",
            "logPattern": ".* (.+) iterations/s.*",
            "metricThreshold": iterations_threshold,
            "operator": "lt"
        }]

    @pytest.fixture
    def local_world_size(self):
        return 8

    def test_log_agent_no_config(self, local_world_size):
        log_agent = LogAgent(local_world_size)
        assert not log_agent.is_running()

        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

    def test_log_agent_log_file_does_not_exist(self, local_world_size,
                                               log_agent_config,
                                               hanging_threshold):

        log_path = str(uuid.uuid4())
        log_agent = LogAgent(local_world_size)

        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

        log_agent.start(log_path,
                        log_monitoring_configuration=log_agent_config)
        validate_agent_running(log_agent)

        validate_agent_log_state(log_agent,
                                 [LogState.HANGING] * local_world_size)

        log_agent.stop()
        assert not log_agent.is_running()

        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

    def test_log_agent_slow_job(self, local_world_size, log_agent_config):

        attempt_dir = tempfile.TemporaryDirectory()

        fds = []
        for rank in range(local_world_size):
            rank_dir = os.path.join(attempt_dir.name, str(rank))
            os.makedirs(rank_dir)
            fds.append(open(os.path.join(rank_dir, f"stdout.log"), 'w'))

        log_agent = LogAgent(local_world_size=local_world_size)
        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

        log_agent.start(attempt_dir.name,
                        log_monitoring_configuration=log_agent_config)
        validate_agent_running(log_agent)

        for rank in range(local_world_size):
            fds[rank].write("Start training process...\n")
            fds[rank].write("training speed: 50 TFLOPs...\n")
            fds[rank].flush()

        validate_agent_log_state(log_agent, [LogState.SLOW] * local_world_size)

        log_agent.stop()
        assert not log_agent.is_running()

        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

        for fd in fds:
            fd.close()
        attempt_dir.cleanup()

    def test_log_agent_hanging_job(self, local_world_size, log_agent_config,
                                   hanging_threshold):
        attempt_dir = tempfile.TemporaryDirectory()

        fds = []
        for rank in range(local_world_size):
            rank_dir = os.path.join(attempt_dir.name, str(rank))
            os.makedirs(rank_dir)
            fds.append(open(os.path.join(rank_dir, f"stdout.log"), 'w'))

        log_agent = LogAgent(local_world_size)

        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

        log_agent.start(attempt_dir.name,
                        log_monitoring_configuration=log_agent_config)
        validate_agent_running(log_agent)

        for rank in range(local_world_size):
            fds[rank].write("Start training process...\n")
            fds[rank].write("training speed: 50 TFLOPs...\n")
            fds[rank].flush()

        validate_agent_log_state(log_agent,
                                 [LogState.HANGING] * local_world_size)

        log_agent.stop()
        assert not log_agent.is_running()

        validate_agent_log_state(log_agent,
                                 [LogState.WAITING] * local_world_size)

        for fd in fds:
            fd.close()
        attempt_dir.cleanup()

    def test_log_agent_healthy_job(self, local_world_size, log_agent_config,
                                   tflops_threshold):
        attempt_dir = tempfile.TemporaryDirectory()

        fds = []
        for rank in range(local_world_size):
            rank_dir = os.path.join(attempt_dir.name, str(rank))
            os.makedirs(rank_dir)
            fds.append(open(os.path.join(rank_dir, f"stdout.log"), 'w'))

        log_agent = LogAgent(local_world_size)
        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

        log_agent.start(attempt_dir.name,
                        log_monitoring_configuration=log_agent_config)
        validate_agent_running(log_agent)

        for rank in range(local_world_size):
            fds[rank].write("Start training process...\n")
            fds[rank].write(
                f"training speed: {tflops_threshold + 1} TFLOPs...\n")
            fds[rank].flush()

        validate_agent_log_state(log_agent,
                                 [LogState.HEALTHY] * local_world_size)

        log_agent.stop()
        assert not log_agent.is_running()

        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

        for fd in fds:
            fd.close()
        attempt_dir.cleanup()

    def test_log_agent_change_attempt_directory(self, local_world_size):
        log_monitoring_configuration = [
            {
                "name": "pretrain",
                "logPattern": ".*Start data loading.*",
                "stopPattern": ".*Start training.*",
                "expectedStartCutOffInSeconds": 60,
            },
            {
                "name": "train",
                "logPattern": ".* (.+) TFLOPs.*",
                "stopPattern": ".*Training complete.*",
                "expectedStartCutOffInSeconds": 120,
                "expectedRecurringFrequencyInSeconds": 30,
                "metricThreshold": 100,
                "operator": "lt",
                "metricEvaluationDataPoints": 1
            },
            {
                "name": "posttrain",
                "logPattern": ".*Saving data*",
                "expectedStartCutOffInSeconds": 180
            },
        ]

        log_agent = LogAgent(local_world_size)
        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

        # Pretrain script logs monitoring
        pretrain_attempt_dir = tempfile.TemporaryDirectory(prefix="pretrain")
        fds = []
        for rank in range(local_world_size):
            rank_dir = os.path.join(pretrain_attempt_dir.name, str(rank))
            os.makedirs(rank_dir)
            fds.append(open(os.path.join(rank_dir, f"stdout.log"), 'w'))

        log_agent.start(pretrain_attempt_dir.name, {0},
                        log_monitoring_configuration)
        validate_agent_running(log_agent)

        fds[0].write("Start data loading...\n")
        fds[0].flush()

        validate_agent_log_state(log_agent, [LogState.HEALTHY] +
                                 [LogState.WAITING] * (local_world_size - 1))

        for fd in fds:
            fd.close()

        # Training script logs monitoring
        train_attempt_dir = tempfile.TemporaryDirectory(prefix="train")
        fds = []
        for rank in range(local_world_size):
            rank_dir = os.path.join(train_attempt_dir.name, str(rank))
            os.makedirs(rank_dir)
            fds.append(open(os.path.join(rank_dir, f"stdout.log"), 'w'))

        log_agent.start(train_attempt_dir.name, {0},
                        log_monitoring_configuration)
        validate_agent_running(log_agent)
        validate_agent_log_state(log_agent, [LogState.HEALTHY] +
                                 [LogState.WAITING] * (local_world_size - 1))

        fds[0].write("Start training...\n")
        fds[0].write("training speed: 120 TFLOPs...\n")
        fds[0].flush()

        validate_agent_log_state(log_agent, [LogState.HEALTHY] +
                                 [LogState.WAITING] * (local_world_size - 1))

        fds[0].write("training speed: 80 TFLOPs...\n")
        fds[0].flush()

        validate_agent_log_state(log_agent, [LogState.SLOW] +
                                 [LogState.WAITING] * (local_world_size - 1))

        fds[0].write("Training complete\n")
        fds[0].flush()

        validate_agent_log_state(log_agent, [LogState.HEALTHY] +
                                 [LogState.WAITING] * (local_world_size - 1))

        for fd in fds:
            fd.close()

        # Posttrain script logs monitoring
        posttrain_attempt_dir = tempfile.TemporaryDirectory(prefix="posttrain")
        fds = []
        for rank in range(local_world_size):
            rank_dir = os.path.join(posttrain_attempt_dir.name, str(rank))
            os.makedirs(rank_dir)
            fds.append(open(os.path.join(rank_dir, f"stdout.log"), 'w'))

        log_agent.start(posttrain_attempt_dir.name, {0},
                        log_monitoring_configuration)
        validate_agent_log_state(log_agent, [LogState.HEALTHY] +
                                 [LogState.WAITING] * (local_world_size - 1))

        fds[0].write("Saving data\n")
        fds[0].flush()

        validate_agent_log_state(log_agent, [LogState.HEALTHY] +
                                 [LogState.WAITING] * (local_world_size - 1))

        log_agent.stop(clear_log_monitoring_configuration=True)
        assert not log_agent.is_running()

        for i in range(local_world_size):
            assert log_agent.log_state[i] == LogState.WAITING

        # Cleanup
        pretrain_attempt_dir.cleanup()
        train_attempt_dir.cleanup()
        posttrain_attempt_dir.cleanup()


@retry(AssertionError, delay=RETRY_DELAY, max_delay=RETRY_TIMEOUT)
def validate_agent_running(log_agent):
    assert log_agent.is_running()


@retry(AssertionError, delay=RETRY_DELAY, max_delay=RETRY_TIMEOUT)
def validate_agent_log_state(log_agent, expected_log_state):
    assert log_agent.log_state == expected_log_state
