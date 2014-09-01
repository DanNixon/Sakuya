from setuptools import setup

setup(
    name='sakuya-client',
    version='0.6.0',
    entry_points = {
        'console_scripts': ['sakuya=sakuyaclient:run'],
    },
    description='PC side data aggregation client for the Sakuya development assistant',
    classifiers=[
	'License :: OSI Approved :: Apache Software License',
	'Natural Language :: English',
	'Programming Language :: Python :: 2.7',
    ],
    url='http://github.com/DanNixon/Sakuya',
    author='Dan Nixon',
    author_email='dan@dan-nixon.com',
    license='Apache',
    packages=['sakuyaclient'],
    install_requires=[
        'pyserial',
        'jenkinsapi',
    ],
    include_package_data=True,
    zip_safe=False)
