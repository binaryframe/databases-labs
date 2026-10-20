from setuptools import find_packages, setup

setup(
    name="booking-system-lab4",
    version="1.0.0",
    description="Flask + MySQL REST API for the booking_system academic project",
    packages=find_packages(where="app"),
    package_dir={"": "app"},
    install_requires=[
        "Flask>=3.0,<4.0",
        "mysql-connector-python>=8.3,<10.0",
        "PyYAML>=6.0,<7.0",
    ],
    python_requires=">=3.10",
)
