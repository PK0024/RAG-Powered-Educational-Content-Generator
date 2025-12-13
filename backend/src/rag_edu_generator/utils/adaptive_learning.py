"""Adaptive learning algorithms for competitive quiz: Q-Learning and Thompson Sampling."""

import logging
import random
import numpy as np
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class DifficultyLevel(str, Enum):
    """Difficulty levels for questions."""

    LOW = "low"
    MEDIUM = "medium"
    HARD = "hard"


class QLearningAgent:
    """
    Q-Learning agent for adaptive difficulty selection.
    
    Learns optimal difficulty selection based on user performance.
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        exploration_rate: float = 0.2,
    ):
        """
        Initialize Q-Learning agent.

        Args:
            learning_rate: Learning rate (alpha) for Q-value updates
            discount_factor: Discount factor (gamma) for future rewards
            exploration_rate: Epsilon for epsilon-greedy exploration
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

        # Q-table: state -> action -> Q-value
        # State: (current_difficulty, performance_trend)
        # Action: next_difficulty (low, medium, hard)
        # Performance trend: "improving", "stable", "declining"
        self.q_table: Dict[Tuple[str, str], Dict[str, float]] = {}

        # Initialize Q-values for all state-action pairs
        self._initialize_q_table()

    def _initialize_q_table(self) -> None:
        """Initialize Q-table with zero values for all state-action pairs."""
        difficulties = [DifficultyLevel.LOW, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
        performance_trends = ["improving", "stable", "declining"]

        for difficulty in difficulties:
            for trend in performance_trends:
                state = (difficulty.value, trend)
                self.q_table[state] = {
                    DifficultyLevel.LOW.value: 0.0,
                    DifficultyLevel.MEDIUM.value: 0.0,
                    DifficultyLevel.HARD.value: 0.0,
                }

    def get_state(self, current_difficulty: str, performance_trend: str) -> Tuple[str, str]:
        """
        Get current state.

        Args:
            current_difficulty: Current difficulty level
            performance_trend: Performance trend ("improving", "stable", "declining")

        Returns:
            State tuple
        """
        return (current_difficulty, performance_trend)

    def choose_action(
        self, state: Tuple[str, str], available_actions: Optional[List[str]] = None
    ) -> str:
        """
        Choose action using epsilon-greedy policy.

        Args:
            state: Current state
            available_actions: Optional list of available actions

        Returns:
            Selected action (difficulty level)
        """
        if state not in self.q_table:
            self.q_table[state] = {
                DifficultyLevel.LOW.value: 0.0,
                DifficultyLevel.MEDIUM.value: 0.0,
                DifficultyLevel.HARD.value: 0.0,
            }

        if available_actions is None:
            available_actions = [
                DifficultyLevel.LOW.value,
                DifficultyLevel.MEDIUM.value,
                DifficultyLevel.HARD.value,
            ]

        # Epsilon-greedy: explore with probability epsilon
        if random.random() < self.exploration_rate:
            return random.choice(available_actions)

        # Exploit: choose action with highest Q-value
        q_values = self.q_table[state]
        best_action = max(available_actions, key=lambda a: q_values.get(a, 0.0))
        return best_action

    def update_q_value(
        self,
        state: Tuple[str, str],
        action: str,
        reward: float,
        next_state: Optional[Tuple[str, str]] = None,
    ) -> None:
        """
        Update Q-value using Q-learning update rule.

        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state (optional, for future rewards)
        """
        if state not in self.q_table:
            self.q_table[state] = {
                DifficultyLevel.LOW.value: 0.0,
                DifficultyLevel.MEDIUM.value: 0.0,
                DifficultyLevel.HARD.value: 0.0,
            }

        current_q = self.q_table[state].get(action, 0.0)

        # Calculate max Q-value for next state
        if next_state and next_state in self.q_table:
            max_next_q = max(self.q_table[next_state].values())
        else:
            max_next_q = 0.0

        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )

        self.q_table[state][action] = new_q

        logger.debug(
            f"Updated Q-value: state={state}, action={action}, "
            f"reward={reward}, Q: {current_q:.3f} -> {new_q:.3f}"
        )

    def get_q_table(self) -> Dict:
        """Get current Q-table for inspection."""
        return self.q_table.copy()


class ThompsonSamplingAgent:
    """
    Thompson Sampling agent for exploration-exploitation balance.
    
    Uses Bayesian approach to balance exploration and exploitation.
    """

    def __init__(self):
        """Initialize Thompson Sampling agent."""
        # Beta distribution parameters for each difficulty level
        # (alpha, beta) for Beta distribution
        # alpha = successes + 1, beta = failures + 1
        self.difficulty_params: Dict[str, Tuple[float, float]] = {
            DifficultyLevel.LOW.value: (1.0, 1.0),  # Uniform prior
            DifficultyLevel.MEDIUM.value: (1.0, 1.0),
            DifficultyLevel.HARD.value: (1.0, 1.0),
        }

    def choose_action(self, available_actions: Optional[List[str]] = None) -> str:
        """
        Choose action using Thompson Sampling.

        Samples from Beta distribution for each action and selects the one
        with highest sample value.

        Args:
            available_actions: Optional list of available actions

        Returns:
            Selected action (difficulty level)
        """
        if available_actions is None:
            available_actions = [
                DifficultyLevel.LOW.value,
                DifficultyLevel.MEDIUM.value,
                DifficultyLevel.HARD.value,
            ]

        # Sample from Beta distribution for each action
        samples = {}
        for action in available_actions:
            alpha, beta = self.difficulty_params.get(action, (1.0, 1.0))
            # Sample from Beta distribution
            sample = np.random.beta(alpha, beta)
            samples[action] = sample

        # Choose action with highest sample
        best_action = max(samples, key=samples.get)
        return best_action

    def update(self, action: str, reward: float) -> None:
        """
        Update Beta distribution parameters based on reward.

        Args:
            action: Action taken
            reward: Reward received (positive for success, negative for failure)
        """
        if action not in self.difficulty_params:
            self.difficulty_params[action] = (1.0, 1.0)

        alpha, beta = self.difficulty_params[action]

        # Update based on reward
        # Positive reward (correct answer) -> increase alpha
        # Negative reward (wrong answer) -> increase beta
        if reward > 0:
            alpha += 1.0
        else:
            beta += 1.0

        self.difficulty_params[action] = (alpha, beta)

        logger.debug(
            f"Updated Thompson Sampling: action={action}, "
            f"reward={reward}, params: alpha={alpha:.2f}, beta={beta:.2f}"
        )

    def get_params(self) -> Dict[str, Tuple[float, float]]:
        """Get current Beta distribution parameters."""
        return self.difficulty_params.copy()


class AdaptiveQuizManager:
    """
    Manages adaptive quiz using Q-Learning and Thompson Sampling.
    """

    def __init__(self):
        """Initialize adaptive quiz manager."""
        self.q_learning_agent = QLearningAgent()
        self.thompson_sampling_agent = ThompsonSamplingAgent()

    def calculate_performance_trend(
        self, recent_answers: List[bool], window_size: int = 3
    ) -> str:
        """
        Calculate performance trend from recent answers.

        Args:
            recent_answers: List of boolean values (True = correct, False = wrong)
            window_size: Number of recent answers to consider

        Returns:
            Performance trend: "improving", "stable", or "declining"
        """
        if len(recent_answers) < 2:
            return "stable"

        # Consider last window_size answers
        recent = recent_answers[-window_size:]
        if len(recent) < 2:
            return "stable"

        # Calculate trend
        first_half = recent[: len(recent) // 2]
        second_half = recent[len(recent) // 2 :]

        first_score = sum(first_half) / len(first_half) if first_half else 0.5
        second_score = sum(second_half) / len(second_half) if second_half else 0.5

        if second_score > first_score + 0.1:
            return "improving"
        elif second_score < first_score - 0.1:
            return "declining"
        else:
            return "stable"

    def calculate_reward(
        self, is_correct: bool, difficulty: str, expected_difficulty: Optional[str] = None
    ) -> float:
        """
        Calculate reward based on answer correctness and difficulty.

        Args:
            is_correct: Whether answer is correct
            difficulty: Difficulty level of the question
            expected_difficulty: Expected difficulty based on user level (optional)

        Returns:
            Reward value (positive for correct, negative for wrong)
        """
        # Reward system with variations based on difficulty and correctness
        if is_correct:
            # Positive rewards for correct answers
            if difficulty == DifficultyLevel.LOW.value:
                reward = 0.5  # Small reward for easy questions
            elif difficulty == DifficultyLevel.MEDIUM.value:
                reward = 1.0  # Standard reward for medium
            else:  # HARD
                reward = 1.5  # Higher reward for hard questions
        else:
            # Negative rewards for wrong answers
            if difficulty == DifficultyLevel.LOW.value:
                reward = -0.55  # Higher penalty for getting easy wrong
            elif difficulty == DifficultyLevel.MEDIUM.value:
                reward = -0.50  # Standard penalty for medium
            else:  # HARD
                reward = -0.75  # Lower penalty for hard (expected to be difficult)

        return reward

    def select_next_difficulty(
        self,
        current_difficulty: str,
        performance_trend: str,
        last_answer_correct: bool,
        use_thompson_sampling: bool = True,
    ) -> str:
        """
        Select next difficulty level using adaptive algorithms.
        
        Core logic: Increase difficulty on correct answer, decrease on wrong answer.

        Args:
            current_difficulty: Current difficulty level
            performance_trend: Performance trend ("improving", "stable", "declining")
            last_answer_correct: Whether the last answer was correct
            use_thompson_sampling: Whether to use Thompson Sampling (True) or Q-Learning (False)

        Returns:
            Next difficulty level
        """
        # Core logic: Increase difficulty on correct, decrease on wrong
        difficulty_levels = [
            DifficultyLevel.LOW.value,
            DifficultyLevel.MEDIUM.value,
            DifficultyLevel.HARD.value,
        ]
        
        current_index = difficulty_levels.index(current_difficulty)
        
        if last_answer_correct:
            # Correct answer: Move to higher difficulty (or stay at hard)
            if current_index < len(difficulty_levels) - 1:
                # Can increase difficulty
                next_difficulty = difficulty_levels[min(current_index + 1, len(difficulty_levels) - 1)]
                logger.info(f"Correct answer: Increasing difficulty from {current_difficulty} to {next_difficulty}")
            else:
                # Already at hard, stay at hard
                next_difficulty = DifficultyLevel.HARD.value
                logger.info(f"Correct answer at hard level: Staying at {next_difficulty}")
        else:
            # Wrong answer: Move to lower difficulty (or stay at low)
            if current_index > 0:
                # Can decrease difficulty
                next_difficulty = difficulty_levels[max(current_index - 1, 0)]
                logger.info(f"Wrong answer: Decreasing difficulty from {current_difficulty} to {next_difficulty}")
            else:
                # Already at low, stay at low
                next_difficulty = DifficultyLevel.LOW.value
                logger.info(f"Wrong answer at low level: Staying at {next_difficulty}")

        # Update learning algorithms with the selected difficulty
        if use_thompson_sampling:
            # Update Thompson Sampling parameters
            self.thompson_sampling_agent.update(
                next_difficulty, 
                1.0 if last_answer_correct else -0.5
            )
        else:
            # Update Q-Learning
            state = self.q_learning_agent.get_state(current_difficulty, performance_trend)
            next_state = self.q_learning_agent.get_state(next_difficulty, performance_trend)
            reward = 1.0 if last_answer_correct else -0.5
            self.q_learning_agent.update_q_value(state, next_difficulty, reward, next_state)

        logger.info(
            f"Selected next difficulty: {next_difficulty} "
            f"(current: {current_difficulty}, last_correct: {last_answer_correct}, "
            f"trend: {performance_trend}, method: {'Thompson Sampling' if use_thompson_sampling else 'Q-Learning'})"
        )

        return next_difficulty

    def update_learning(
        self,
        current_difficulty: str,
        next_difficulty: str,
        performance_trend: str,
        reward: float,
        use_thompson_sampling: bool = True,
    ) -> None:
        """
        Update learning algorithms based on user performance.

        Args:
            current_difficulty: Current difficulty level
            next_difficulty: Next difficulty level that was selected
            performance_trend: Performance trend
            reward: Reward received
            use_thompson_sampling: Whether to use Thompson Sampling
        """
        if use_thompson_sampling:
            # Update Thompson Sampling
            self.thompson_sampling_agent.update(next_difficulty, reward)
        else:
            # Update Q-Learning
            current_state = self.q_learning_agent.get_state(
                current_difficulty, performance_trend
            )
            next_state = self.q_learning_agent.get_state(next_difficulty, performance_trend)
            self.q_learning_agent.update_q_value(
                current_state, next_difficulty, reward, next_state
            )

        logger.debug(
            f"Updated learning: difficulty={current_difficulty}->{next_difficulty}, "
            f"reward={reward:.2f}, trend={performance_trend}"
        )

    def get_learning_stats(self) -> Dict:
        """Get learning statistics for analysis."""
        return {
            "q_learning": {
                "q_table": self.q_learning_agent.get_q_table(),
                "exploration_rate": self.q_learning_agent.exploration_rate,
            },
            "thompson_sampling": {
                "beta_params": self.thompson_sampling_agent.get_params(),
            },
        }

