#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import uuid
import random

class TaskGenerator(Node):
	def __init__(self):
		super().__init__('task_generator')
		self.get_logger().info('task_generator has started')
		self.task_pub = self.create_publisher(String, '/task_announcements', 10)
		self.timer = self.create_timer(15.0, self.publish_tasks)

	def publish_tasks(self):
		required = random.choices([1,2], weights=[0.7, 0.3])[0]
		task = {
			'task_id' : str(uuid.uuid4())[:8],
			'pickup' : [0.0, 0.0],
			'drop' : [1.1, 1.1],
			'required_robots' : required,
        }
		msg = String()
		msg.data = json.dumps(task)
		self.task_pub.publish(msg)
		self.get_logger().info(f'Announced task {task["task_id"]}: {msg.data}')
		

def main(args=None):
	rclpy.init(args=args)
	node=TaskGenerator()
	rclpy.spin(node)
	node.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
