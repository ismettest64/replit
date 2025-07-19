from setuptools import setup, find_packages

setup(
    name="zeppelin-betting-game",
    version="1.0.0",
    description="Kick streaming platformu ile entegre çalışan gerçek zamanlı bahis oyunu",
    author="Zeppelin Game Team",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0.0",
        "flask-socketio>=5.3.6",
        "flask-sqlalchemy>=3.1.1",
        "gunicorn>=21.2.0",
        "psycopg2-binary>=2.9.9",
        "requests>=2.31.0",
        "sqlalchemy>=2.0.23",
        "trafilatura>=1.6.4",
        "email-validator>=2.1.0",
        "python-socketio>=5.10.0",
        "eventlet>=0.33.3"
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Topic :: Games/Entertainment",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)