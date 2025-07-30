from setuptools import setup

setup(
    name='furs_fiscalization',
    packages=['furs_fiscalization'],
    version='1.0.4',
    license='MIT',
    description='Python library for simplified communication with FURS (Financna uprava Republike Slovenije).',
    author='Hermes d.o.o.',
    author_email='info@hermes-solutions.si ',
    url='https://github.com/HermesGH/furs-fiscalization',
    download_url='https://github.com/HermesGH/furs-fiscalization/archive/v1.0.4.zip',
    keywords=['FURS', 'fiscal', 'fiscal register', 'davcne blagajne'],
    classifiers=[],
    package_data={'furs_fiscalization': ['certs/*.pem']},
    install_requires=[
        'requests>=2.20.0',        
        'PyJWT==2.8.0',
        'pyOpenSSL>=17.5.0',
        'Pillow',
        'qrcode',
    ]
)
