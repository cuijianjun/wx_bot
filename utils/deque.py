from collections import deque


class FixedSizeQueue:
    def __init__(self, max_size):
        self.max_size = max_size
        self.queue = deque()

    def add(self, item):
        self.queue.append(item)
        if len(self.queue) > self.max_size:
            self.queue.popleft()

    def get_queue(self):
        return list(self.queue)

# 使用示例
if __name__ == '__main__':
    max_queue_size = 2
    queue = FixedSizeQueue(max_queue_size)

    # 添加元素
    queue.add(1)
    queue.add(2)
    queue.add(3)
    print(queue.get_queue())  # 输出: [1, 2, 3]

    # 添加更多元素，超过队列长度
    queue.add(4)
    queue.add(5)
    queue.add(6)
    print(queue.get_queue())  # 输出: [2, 3, 4, 5, 6]
