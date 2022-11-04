from setuptools import setup, find_packages

setup(
    name="checker",
    version='1.0.0',
    description='Checker of available slots for services in Russian consulates',
    author='Igor Lashkov',
    author_email='rwrotson@yandex.ru',
    install_requires=[
        'selenium==4.5.0',
        'webdriver-manager==3.8.2',
        '2captcha-python==1.1.2',
        'jsonschema==4.16.0'
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "consulate-checker = checker.main:main",
        ]
    },
)