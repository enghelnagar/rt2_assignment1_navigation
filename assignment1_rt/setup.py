from setuptools import find_packages, setup

package_name = 'assignment1_rt'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='eng.h.elnagar@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
             'spawn = rt1_assignment1.turtle_spawn: main',
             'controller = rt1_assignment1.robot_controller: main',
             'monitor = rt1_assignment1.distance_monitor: main',
        ],
    },
)
