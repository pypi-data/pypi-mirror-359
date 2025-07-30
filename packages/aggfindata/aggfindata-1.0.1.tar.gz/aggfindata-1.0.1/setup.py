from setuptools import setup, find_packages

setup(
    name="aggfindata",
    version="1.0.1",
    description="A Flask application for aggregating stock data and financial news",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(include=["AggFin", "AggFin.*"]),
    include_package_data=True,
    install_requires=[
        "Flask==3.0.3",
        "Flask-Login==0.6.2",
        "Flask-Bcrypt==1.0.1",
        "Flask-WTF==1.1.1",
        "Flask-Mail==0.9.1",
        "Flask-Migrate==4.1.0",
        "Flask-SQLAlchemy==3.0.3",
        "email-validator==2.0.0.post2",
        "yfinance",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
