import setuptools
with open(r'/Users/aleksejzuravlev/PycharmProjects/vk-a/README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='vka',
	version='0.1',
	author='Major4ik',
	author_email='2772771882@mail.ru',
	description='module for the vk api wrapper',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/MrCreEper002/vka',
	packages=['vka'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)