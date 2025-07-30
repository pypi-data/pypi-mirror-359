from setuptools import setup, find_packages

setup(
    name="robot_library",               # pip install 后的包名
    version="0.1.0",
    packages=find_packages(),           # 自动找到 robot_library
    author="Liu Yu",
    description="TL Robot robotics helper library",
    python_requires=">=3.10",
)
