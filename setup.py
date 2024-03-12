import setuptools
with open(r'README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='vka',
	version='1.2.19',
	author='Major4ik',
	author_email='2772771882@mail.ru',
	description='module for the vk api wrapper',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/MrCreEper002/vka',
	include_package_data=True,
	packages=['vka', 'vka/base', 'vka/base/buiders', 'vka/chatbot', 'vka/chatbot/wrappers'],
	install_requires=[
		'loguru==0.6.0',
		'bs4==0.0.1',
	],
	classifiers=[
		'Programming Language :: Python :: 3.10',
		'Programming Language :: Python :: 3.11',
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.10',
)