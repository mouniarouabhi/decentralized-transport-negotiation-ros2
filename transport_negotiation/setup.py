from setuptools import find_packages, setup

package_name = 'transport_negotiation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/multi_robot.launch.py']),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mounia Rouabhi',
    maintainer_email='mm_rouabhi@esi.dz',
    description='Decentralized multi-robot negotiation and collective transport in ROS2',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'robot_agent = transport_negotiation.robot_agent:main',
	    'task_generator = transport_negotiation.task_generator:main',
        ],
    },
)
