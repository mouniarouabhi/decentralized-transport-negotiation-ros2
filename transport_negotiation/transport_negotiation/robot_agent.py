#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class RobotAgent(Node):
	def __init__(self):
		super().__init__('robot_agent')
		self.get_logger().info('robot_agent node started')
		self.task_sub = self.create_subscription(String, '/task_announcements', self.on_task_announcement, 10)
		self.bid_pub = self.create_publisher(String, '/bids', 10)

	def on_task_announcement(self, msg):
		self.get_logger().info(f'Received task announcement : {msg.data}')

def main(args=None):
	rclpy.init(args=args)
	node=RobotAgent()
	rclpy.spin(node)
	node.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
