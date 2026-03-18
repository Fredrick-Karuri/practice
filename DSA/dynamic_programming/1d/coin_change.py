
class Solution:
    """
    THE PROBLEM: Find minimum coins needed to make amount  - problem 322

    PATTERN: Dynamic Programming (Bottom Up)

    INSIGHT: For each amount, try all coins and take minimum.
    dp[i] = minimum coins to make amount i

    THE PLAN: 
    1.Create dp array of size amount+1, initialize with infinity
    2.Base Case: dp[0] = 0 (o coins of amount 0) 
    3.For each amount from 1 to target:
        - Try each coin
        - If coin is <= amount: dp[amount] = min(dp[amount],dp[amount-coin]+1)
    4.Return dp[amount] or -1 if impossible

    Example: coins=[1,2,5], amount=11
    - dp[11] = dp[11-5] + 1 = dp[6] + 1 = 3 + 1 = 4
    - But also dp[11] = dp[11-1] + 1 = dp[10] + 1 = 3 + 1 = 4
    - Minimum: 3 coins (5+5+1)

    TIME: O(amount*coin)
    SPACE: O(amount)
    """
    def coinChange(self, coins: list[int], amount: int) -> int:
        # dp[i] min coins to make amount i
        dp = [float('inf')] * (amount + 1)
        dp[0] = 0

        self._calculate_min_coins(coins, amount, dp)
        min_coins_required = dp[amount] if dp[amount] != float('inf') else -1
        return min_coins_required

    def _calculate_min_coins(self, coins, amount, dp):
        for amt in range (1, amount + 1):
            for coin in coins:
                if coin <= amt:
                    dp[amt] = min(dp[amt],dp[amt-coin]+1)
        