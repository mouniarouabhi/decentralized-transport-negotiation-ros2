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
		self.known_task = {}

		self.task_sub = self.create_subscription(String, '/task_announcements', self.on_task_announcement, 10)
		self.bid_sub = self.create_subscription(String, '/bids', self.on_bid, 10)
		self.bid_pub = self.create_publisher(String, '/bids', 10)
		self.task_announce_pub = self.create_publisher(String, 'task_announcements', 10)

		self.get_logger().info('robot_agent node started')


	def on_task_announcement(self, msg):
		task = json.loads(msg.data)
		self.known_task[task['task_id']] = task

		if self.busy:
			self.get_logger().info('Busy, skipping bid')
			return
		
		self.get_logger().info(f'Received task announcement : {msg.data}') 

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
	
		existing_robot_ids = [b['robot_id'] for b in self.pending_tasks[task_id]['bids']]
		if bid['robot_id'] not in existing_robot_ids:
			self.pending_tasks[task_id]['bids'].append(bid)

	def resolve_winner(self, task_id):
		entry = self.pending_tasks.get(task_id)
		if entry is None:
			return

		entry['timer'].cancel()

		bids = entry['bids']
		task = self.known_task.get(task_id, {})
		required = task.get('required_robots', 1)

		sorted_bids = sorted(bids, key=lambda b: (b['bid'], b['robot_id']))

		if len(sorted_bids) < required:
			self.get_logger().info(f'Not enough bidders for {task_id} ({len(sorted_bids)}/{required}) - re-announcing')
			msg = String()
			msg.data = json.dumps(task)
			self.task_announce_pub.publish(msg)
			del self.pending_tasks[task_id]
			return

		crew = sorted_bids[:required]
		crew_ids=[c['robot_id'] for c in crew]
		if self.robot_id in crew_ids:
			self.get_logger().info(f'*** I am part of the crew for {task_id} ***')
			self.busy = True
			self.finish_timer = self.create_timer(5.0, self.finish_task)
		else:
			self.get_logger().info(f'Task {task_id} crew: {crew_ids}')
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