import math as ma
import sys


class SparseTable:
	def __init__(self, nums: list[int] = None):
		if not nums:
			raise ValueError("Input list 'nums' cannot be empty for SparseTable.")
		self.st = self.build(nums)

	def build(self, nums: list[int] = None) -> list[list[int]]:
		n: int = len(nums)
		k: int = ma.ceil(ma.log2(n)) + 1
		self.n = n
		self.k = k
		st: list[list[int]] = [[0] * k for _ in range(n)]
		for i in range(n):
			st[i][0] = nums[i]
		for j in range(1, k + 1):
			i: int = 0
			while i + (1 << j) - 1 < n:
				st[i][j] = min(st[i][j - 1], st[i + (1 << (j - 1))][j - 1])
				i += 1
		return st

	def range_query(self, left: int, right: int) -> int:
		if not (0 <= left <= right < self.n):
			raise IndexError(
				f"Query range [{left}, {right}] is out of bounds "
				f"for array of size {self.n} or invalid (left > right)."
			)

		min_: int = sys.maxsize
		for j in range(self.k, -1, -1):
			if (1 << j) <= right - left + 1:
				min_ = min(self.st[left][j], min_)
				left += 1 << j
		return min_


if __name__ == "__main__":
	nums: list[int] = [1, 2, 3, 4, 5]
	st = SparseTable(nums)
	print(st.range_query(1, 2))
	print(st.range_query(3, 4))
