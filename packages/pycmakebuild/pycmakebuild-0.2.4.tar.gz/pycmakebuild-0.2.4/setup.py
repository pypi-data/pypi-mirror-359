from setuptools import setup, find_packages

setup(
    name="pycmakebuild",
    version="0.1.0",
    description="Python CMake 批量构建工具，支持 build.json 配置和命令行批量编译",
    author="Patchlion",
    author_email="your@email.com",
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv",
        "cmake"
    ],
    entry_points={
        'console_scripts': [
            'pycmakebuild = pycmakebuild.__main__:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    long_description=open("README.md", encoding="utf-8").read() if __import__('os').path.exists('README.md') else '',
    long_description_content_type="text/markdown",
)
