from setuptools import setup,find_packages
setup(
    name='SKP_DEBUG',
    version='0.4.0', 
   install_requires=[
        "requests",
    ],
    description='テスト',
    author='noname',
    author_email='hogehoge@hoge.hoge',
    url='https://github.com/xfiletouhou/SKP_DEBUG',
    packages=find_packages(),
)