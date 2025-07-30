from setuptools import setup, find_packages

setup(
    # 指定项目名称，我们在后期打包时，这就是打包的包名称，当然打包时的名称可能还会包含下面的版本号哟~
    name='aiwenSDK',
    # 指定版本号
    version='1.0.6',
    # 这是对当前项目的一个描述
    description='对埃文商业API的网络请求的封装，方便调用',
    # 作者是谁，指的是此项目开发的人，这里就写你自己的名字即可
    author='aiwen',
    # 作者的邮箱
    author_email='sales@ipplus360.com',
    # 写上项目的地址，比如你开源的地址开源写博客地址，也开源写GitHub地址，自定义的官网地址等等。
    url='https://www.ipplus360.com',
    # 使用 find_packages 自动发现 src 目录下的所有包
    packages=find_packages(where='src'),
    # 指定包的根目录
    package_dir={'': 'src'},
    # Python 版本要求
    python_requires='>=3.6',
    # 长描述，通常从 README 文件读取
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)