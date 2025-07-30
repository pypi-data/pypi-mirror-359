from setuptools import setup, find_packages

setup(
    name='fu_downloader',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'fu-download=fu_downloader.cli:download_images',
        ],
    },
    author='Kappy',
    description='CLI tool để tải ảnh từ thread FuOverflow',
    python_requires='>=3.7',
)
