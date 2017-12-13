from setuptools import setup

setup(
    name='smartNutrition',
    version='0.1.0',
    packages=['smartNutrition'],
    include_package_data=True,
    install_requires=[
        'flask',
        'arrow',
        'sh',
        'requests',
	'pint',
        'pymongo',
    ],
)
