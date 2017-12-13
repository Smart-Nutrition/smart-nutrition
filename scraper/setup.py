from setuptools import setup

setup(
    name='smartNutritionScraper',
    version='0.1.0',
    packages=['smartNutritionScraper'],
    include_package_data=True,
    install_requires=[
        'sh',
        'scrapy',
        'requests',
	'beautifulsoup4',
	'selenium'
    ],
    entry_points={
        'console_scripts': [
            'smartNutritionScraper = smartNutritionScraper.__main__:main'
        ]
    },
)
