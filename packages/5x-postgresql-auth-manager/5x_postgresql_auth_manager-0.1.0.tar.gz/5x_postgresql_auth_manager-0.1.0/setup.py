from setuptools import setup, find_packages

setup(
    name='5x-postgresql-auth-manager',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'psycopg2-binary>=2.9.0',
    ],
    author='Your Name',  # Replace with your name
    author_email='your.email@example.com',  # Replace with your email
    description='A package to manage PostgreSQL connections using environment variables.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-org/5x-postgresql-auth-manager',  # Replace with your project URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)