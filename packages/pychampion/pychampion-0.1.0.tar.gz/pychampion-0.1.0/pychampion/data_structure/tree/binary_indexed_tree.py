class BinaryIndexedTree:
	def __init__(self, nums: list[int]) -> None:
		self.n = len(nums) + 1
		self.tree = [0] * self.n
		self.build(nums)

	def build(self, nums: list[int]) -> None:
		for i in range(len(nums)):
			self.update(i, nums[i])

	def update(self, idx: int, val: int) -> None:
		idx += 1
		while idx < self.n:
			self.tree[idx] += val
			idx += idx & -idx

	def query(self, idx: int) -> int:
		idx += 1
		sum_: int = 0
		while idx > 0:
			sum_ += self.tree[idx]
			idx -= idx & -idx
		return sum_

	def range_query(self, l: int, r: int) -> int:  # noqa: E741
		return self.query(r) - self.query(l - 1)

	def read_single(self, idx: int) -> int:
		sum_: int = self.tree[idx]
		if idx > 0:
			z = idx - (idx & -idx)
			idx -= 1
			while idx != z:
				sum_ -= self.tree[idx]
				idx -= idx & -idx
		return sum_


if __name__ == "__main__":
	arr: list[int] = [2, 1, 1, 3, 2, 3, 4, 5, 6, 7, 5, 5]
	bit = BinaryIndexedTree(arr)
	print(bit.query(2))
	print(bit.range_query(2, 5))
	print(bit.read_single(12))
	print(bit.read_single(3))
