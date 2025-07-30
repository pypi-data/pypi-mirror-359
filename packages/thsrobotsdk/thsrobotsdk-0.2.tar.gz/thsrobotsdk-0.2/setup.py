from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='thsrobotsdk',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='linagzxx',
    author_email='admin@linagzxx.com',
    description='Thsroot SDK for Python',
    long_description=long_description,
    url='https://github.com/your-repo-url',  # 替换为实际仓库地址
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='thsrobot sdk',
)
