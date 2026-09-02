#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

class RobotAgent(Node):
	def __init__(self):
		super().__init__('robot_agent')
		self.get_logger().info('robot_agent node started')

def main(args=None):
	rclpy.init(args=args)
	node=RobotAgent()
	rclpy.spin(node)
	node.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
