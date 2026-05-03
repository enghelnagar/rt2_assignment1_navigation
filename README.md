# Research Track 2 - Assignment 1: ROS 2 Navigation Framework using Actions and Components

## Author Information
* **Name:** Hussein Mohamed Elnaggar
* **Program:** M.Sc. in Robotics Engineering (1st Year)
* **Institution:** University of Genoa (UniGe), Italy
* **Course:** Research Track 2 / Assignment No. 1 
* **Student ID:** 8786438

---

## 1. Abstract & Project Overview
This repository contains the complete implementation of the first assignment for the Research Track 2 course. The primary objective is to develop a robust ROS 2 navigation framework that allows a mobile robot to navigate toward a specific target pose $(x, y, \theta)$ within a simulated Gazebo environment. 

The project strictly adheres to modern ROS 2 software architecture paradigms, utilizing **ROS 2 Actions** for asynchronous goal execution and continuous feedback, alongside **ROS 2 Components** for optimized zero-copy intra-process communication.

Furthermore, a full **Python equivalent** of the system has been developed as a **Bonus Implementation**, demonstrating multi-language proficiency and highlighting the architectural distinctions between C++ memory-sharing components and Python's multi-threaded execution models.

---

## 2. System Architecture & Package Structure

The workspace is modularly designed and comprises the following packages:

*   **`nav_action_interfaces`**: Contains the custom Action definition (`NavigateRobot.action`) representing the communication protocol.
*   **`nav_action_server` (C++ Core)**: The core navigation component that executes the kinematic control loop.
*   **`nav_action_client` (C++ Core)**: The interactive UI component that dispatches goals and handles cancellation requests.
*   **`nav_action_py` (Python Bonus)**: The complete Python implementation of both the server and the interactive client, consolidated within a single package.
*   **`bme_gazebo_sensors`**: The provided simulation environment containing the differential drive robot and Gazebo worlds.

### 2.1. Custom Action Interface Protocol
The communication protocol between the client and the server is strictly defined by the `NavigateRobot.action` file. The data structure is organized as follows:

| Request (Goal) | Response (Result) | Feedback |
| :--- | :--- | :--- |
| `float64 x` | `bool success` | `float64 distance_remaining` |
| `float64 y` | | |
| `float64 theta` | | |

---

## 3. Methodological Implementation

### 3.1. C++ Implementation (Core Requirement)
The C++ implementation leverages the `rclcpp_components` package to maximize performance. Both the `NavigationServer` and `NavigationClient` are engineered as subclasses of `rclcpp::Node` and registered as dynamically loadable components. 

This architectural choice allows both nodes to be loaded into a single `component_container`, enabling zero-copy communication. A custom launch file (`navigation.launch.py`) is provided to initialize the container. The client is explicitly loaded via terminal commands to preserve the standard input stream (`std::cin`) for the interactive user menu.

### 3.2. Python Implementation (Bonus Requirement)
The Python package replicates the entire system functionality with necessary architectural adaptations:
*   **Concurrency Handling:** Due to Python's Global Interpreter Lock (GIL), true shared-memory components are not natively supported. Consequently, standard nodes are utilized.
*   **Asynchronous UI:** To prevent the `input()` function from blocking the ROS 2 executor, the Python Action Client implements a dedicated **daemon thread** for the user interface. Simultaneously, a `MultiThreadedExecutor` is utilized in the Server to handle concurrent goal requests and control loops.
*   **Integrated Launch File:** A consolidated `navigation_py.launch.py` is provided. It employs the `xterm` utility to launch the server in the background while automatically spawning a new interactive terminal window exclusively for the client's user interface.

---

## 4. Kinematic Control Strategy
The navigation server relies on real-time Odometry data (`/odom`) to compute the required velocity commands (`/cmd_vel`). The control loop operates sequentially based on proportional control logic:

1.  **Positional Error Calculation:** The Euclidean distance to the target coordinates is continuously computed:
    $$dist = \sqrt{(x_{target} - x_{current})^2 + (y_{target} - y_{current})^2}$$
2.  **Orientation Extraction:** The robot's current orientation is provided as a Quaternion $(q_x, q_y, q_z, q_w)$. It is mathematically transformed into Euler angles to extract the Yaw angle $(\psi)$:
    $$\psi = \text{atan2}(2(q_w q_z + q_x q_y), 1 - 2(q_y^2 + q_z^2))$$
3.  **Proportional Navigation:** 
    *   While $dist > 0.2$ meters, the robot adjusts its angular velocity to face the target and moves linearly forward.
    *   Upon reaching the proximity threshold, linear velocity halts, and the robot pivots to align with the final desired heading $(\theta)$.

---

## 5. Build and Execution Instructions

### 5.1. Building the Workspace
Navigate to the root of your ROS 2 workspace and compile all packages:
```bash
cd ~/workspace
colcon build
source install/setup.bash
```

### 5.2. Running the Simulation Environment
Open a new terminal, source the workspace, and launch Gazebo:
```bash
source install/setup.bash
ros2 launch bme_gazebo_sensors spawn_robot_ex.launch.py
```

### 5.3. Executing the C++ Components (Core)
To launch the entire C++ navigation framework seamlessly, a unified launch file is provided. It automatically initializes the Component Container, loads the Server in the background, and spawns a dedicated `xterm` window for the Client's interactive UI:

Open a new terminal and execute:
```bash
source install/setup.bash
ros2 launch nav_action_server navigation.launch.py
```

### 5.4. Executing the Python Nodes (Bonus)
To evaluate the Python implementation with the integrated interactive launch file:
```bash
source install/setup.bash
ros2 launch nav_action_py navigation_py.launch.py
```
(Note: Ensure xterm is installed on the system to spawn the interactive client terminal).
