from setuptools import setup, find_packages

setup(
	py_modules=["openstuder"],
	install_requires=[
		'websocket-client==1.3.1',
		'cbor2==5.4.2.post1',
		'bleak==0.14.2'
	]
)
