import os
import gym
import logging
import unittest
import numpy as np

import envs

from algorithms import a2c
from algorithms.a2c.multi_env import MultiEnv

from utils.common_utils import get_test_logger


logger = get_test_logger()


class MultiEnvTest(unittest.TestCase):
    def test_multi_env(self):
        def make_env_func():
            return gym.make('MicroTbs-CollectWithTerrain-v1')

        num_envs = 16
        multi_env = MultiEnv(num_envs=num_envs, make_env_func=make_env_func)
        obs = multi_env.initial_observations()

        self.assertEqual(len(obs), num_envs)

        num_different = 0
        for i in range(1, len(obs)):
            if not np.array_equal(obs[i - 1], obs[i]):
                num_different += 1

        # By pure chance some of the environments might be identical even with different seeds, but definitely not
        # all of them!
        self.assertGreater(num_different, len(obs) // 2)

        for i in range(20):
            logger.info('Step %d...', i)
            obs, rewards, dones = multi_env.step([0] * num_envs)
            self.assertEqual(len(obs), num_envs)
            self.assertEqual(len(rewards), num_envs)
            self.assertEqual(len(dones), num_envs)

        multi_env.close()


class A2CTest(unittest.TestCase):
    @staticmethod
    def test_discounted_reward():
        gamma = 0.9
        value = 100.0
        rewards = [1, 2, 3, 4, 5]
        dones = [
            [True, False, False, True, False],
            [True, True, True, True, True],
            [False, False, False, False, True],
        ]
        expected = [
            [1, 7.94, 6.6, 4, 95],
            rewards,
            [11.4265, 11.585, 10.65, 8.5, 5],
        ]

        for done_mask, expected_result in zip(dones, expected):
            calculated = list(a2c.AgentA2C._calc_discounted_rewards(gamma, rewards, done_mask, value))
            np.testing.assert_array_almost_equal(calculated, expected_result)