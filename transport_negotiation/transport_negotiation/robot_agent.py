#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import math

class RobotAgent(Node):
	def __init__(self):
		super().__init__('robot_agent')
		self.declare_parameter('robot_id', 'robot_0')
		self.robot_id = self.get_parameter('robot_id').value
		self.position = (0.0, 0.0)
		self.busy = False
		self.pending_tasks = {}
		self.get_logger().info('robot_agent node started')
		self.task_sub = self.create_subscription(String, '/task_announcements', self.on_task_announcement, 10)
		self.bid_sub = self.create_subscription(String, '/bids', self.on_bid, 10)
		self.bid_pub = self.create_publisher(String, '/bids', 10)

	def on_task_announcement(self, msg):
		if self.busy:
			self.get_logger().info('Busy, skipping bid')
			return
		
		self.get_logger().info(f'Received task announcement : {msg.data}') 

		task = json.loads(msg.data)
		pickup = tuple(task['pickup'])
		drop = tuple(task['drop'][:2])

		total_dist = math.dist(self.position, pickup) + math.dist(pickup, drop)

		bid = {
			'task_id' : task['task_id'],
			'robot_id' : self.robot_id,
			'bid' : total_dist
		}
		bid_msg = String()
		bid_msg.data = json.dumps(bid)
		self.bid_pub.publish(bid_msg)
		self.get_logger().info(f'Bid on {task["task_id"]} : distance={total_dist:.2f}')

	def on_bid(self, msg: String):
		bid = json.loads(msg.data)
		task_id = bid['task_id']

		if task_id not in self.pending_tasks:
			timer = self.create_timer(2.0, lambda tid=task_id: self.resolve_winner(tid))
			self.pending_tasks[task_id] = {'bids': [], 'timer': timer}
	
		self.pending_tasks[task_id]['bids'].append(bid)

	def resolve_winner(self, task_id):
		entry = self.pending_tasks.get(task_id)
		if entry is None:
			return

		entry['timer'].cancel()

		bids = entry['bids']
		winner = sorted(bids, key=lambda b: (b['bid'], b['robot_id']))[0]

		if winner['robot_id'] == self.robot_id:
			self.get_logger().info(f'*** I WON task {task_id} - starting delivery ***')
			self.busy = True
			self.finish_timer = self.create_timer(5.0, self.finish_task)
		else:
			self.get_logger().info(f'Task {task_id} won by {winner["robot_id"]} (bid={winner["bid"]:.2f})')

		del self.pending_tasks[task_id]

	def finish_task(self):
		self.finish_timer.cancel()
		self.busy = False
		self.get_logger().info('Task complete, available again')


def main(args=None):
	rclpy.init(args=args)
	node=RobotAgent()
	rclpy.spin(node)
	node.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
