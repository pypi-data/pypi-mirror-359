import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='Flask-Modals2',
    version='0.5.2',
    author='Leandro Dariva Pinto',
    author_email='leandro.dariva@gmail.com',
    description='Use forms in Bootstrap modals with Flask.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ldariva/flask-modals2',
    packages=['flask_modals2'],
    package_data={'flask_modals2': ['templates/modals/*.html',
                                    'static/js/main.js',
                                    'static/css/progressBarStyle.css']},
    include_package_data=True,
    install_requires=['Flask'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
