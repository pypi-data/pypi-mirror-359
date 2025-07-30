from setuptools import setup, find_packages

setup(
    name='simpledb-wrapper',
    version='0.1.0',
    author='Your Name', # 여기에 당신의 이름을 넣어주세요
    author_email='your.email@example.com', # 여기에 당신의 이메일을 넣어주세요
    description='A simple SQLite wrapper class based on Python sqlite3',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/SimpleDB', # 여기에 당신의 GitHub 저장소 URL을 넣어주세요
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
