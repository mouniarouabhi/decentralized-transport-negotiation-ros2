# Decentralized Transport Negotiation (ROS2)

Decentralized multi-robot task negotiation and collective transport in ROS2 —
contract-net-style bidding, coalition formation for heavy loads, and
fault-tolerant task re-negotiation. No central coordinator: every robot
independently computes the same outcome from the same broadcast data.

## Overview

A fleet of simulated robot agents negotiate over incoming transport tasks with
no coordinator node. Each robot bids on tasks based on estimated travel cost;
the fleet deterministically agrees on a winner (or a multi-robot crew, for
heavier loads) purely from locally observed bids. Robots track their own
availability, and the fleet detects and recovers from a robot going silent
mid-task — without any central authority declaring the failure.

## Architecture

- **`task_generator`** — periodically announces new transport tasks (`pickup`,
  `drop`, `required_robots`) on `/task_announcements`.
- **`robot_agent`** (one instance per robot) —
  - Bids on announced tasks it's eligible for (idle, i.e. not already
    committed to another task), using total path distance
    (`position → pickup → drop`) as its cost estimate.
  - Publishes bids on `/bids`; subscribes to the same topic to hear everyone
    else's bids.
  - After a short collection window, every robot independently sorts all
    observed bids for a task (lowest cost first, alphabetical `robot_id` as
    tiebreak) and selects the top *N* bidders as the crew, where *N* is the
    task's `required_robots`. Because the rule and the data are identical for
    every robot, they all arrive at the same crew with no message exchange
    beyond the bids themselves.
  - If fewer robots bid than required, the task is re-announced rather than
    partially staffed.
  - Crew members broadcast lifecycle status (`started` / `done`) on
    `/task_status`. Every robot (not just crew members) watches this and
    expects a `done` from **every** crew member within a deadline
    (expected duration + grace period). If any crew member goes silent
    (e.g. process killed), the task is flagged as stalled and re-announced —
    the fleet renegotiates it among the survivors automatically.

## Build & Run

```bash
cd ~/ros2_ws
colcon build --packages-select transport_negotiation
source install/setup.bash
ros2 launch transport_negotiation multi_robot.launch.py
```

This starts 3 robot agents and the task generator together. Kill one robot's
process mid-task (e.g. via `ros2 node list` + inspecting logs, or by running
nodes in separate terminals with `ros2 run` and using Ctrl+C) to see the
fault-recovery path in action.

## Design decisions & known limitations

- **Single-round coalition selection, not iterative recruitment.** Crews for
  multi-robot tasks are formed by taking the top-*N* bidders from one auction
  round, rather than a leader running a separate recruitment negotiation
  after winning solo. This is simpler and sufficient for a homogeneous fleet
  with no specialized roles, at the cost of not modeling leader-initiated
  coalition formation as described in some collective-transport literature
  (e.g. Legarda Herranz et al., 2022).
- **Fixed robot positions.** Robots don't currently move or update position
  from odometry; bids are computed from a static coordinate. Real navigation
  (e.g. via Nav2) and dynamic position tracking are natural next steps.
- **Bid deduplication is necessary and non-obvious.** Because every robot
  independently re-announces on insufficient bidders, a single robot's bid
  can otherwise be double-counted across near-simultaneous re-announcements
  of the same task. Bids are deduplicated per `(task_id, robot_id)`.
- **Crew-aware completion tracking.** An early version considered a task
  "done" as soon as any one crew member reported completion — which meant
  one surviving robot's normal completion could mask another crew member's
  silent failure. Completion is now tracked per crew member, and a task is
  only cleared once every assigned robot has reported done.
- **Task execution is currently simulated** via a fixed-duration timer rather
  than actual movement — this isolates the negotiation/fault-tolerance logic
  for testing without depending on a working navigation stack.

## Related Work

- Choi, Brunet, How (2009) — Consensus-Based Bundle Algorithm for
  decentralized, auction-based task allocation among multiple agents.
- Legarda Herranz, Hauert, Jones (2022) — Decentralised negotiation
  approaches for collective transport tasks among robot teams.

## License

MIT — see [LICENSE](./LICENSE).