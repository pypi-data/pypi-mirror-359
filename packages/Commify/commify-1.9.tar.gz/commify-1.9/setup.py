import codecs
import os
from setuptools import setup, find_packages
from commify.version import __version__

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as fh:
    long_description = '\n' + fh.read()

long_description = long_description.replace("[!NOTE]", "")
long_description = long_description.replace("[!Caution]", "")
long_description = long_description.replace("[!Warning]", "")

setup(
    name='Commify',
    version=__version__,
    description='Commify: You Should Commit Yourself.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Matuco19',
    license="MATCO-Open-Source",
    url="https://matuco19.com/Commify",
    project_urls={
        'Source Code': 'https://github.com/Matuco19/Commify',  
        'Bug Tracker': 'https://github.com/Matuco19/Commify/issues', 
    },
    packages=find_packages(),
    install_requires=[
        'ollama',
        'GitPython',
        'g4f',
        'rich',
        'requests',
        'openai',
        'groq',
        'google-generativeai'
    ],
    entry_points={
        'console_scripts': [
            'commify=commify.main:main', 
        ],
    },
    keywords=[
        'commify',
        'python',
        'ai',
        'commit',
        'commits',
        'git',
        'github',
        'gpt',
        'language-model',
        'automation',
        'commits',
        'gpt-4',
        'gpt4',
        'gpt-4o',
        'gpt4o',
        'gpt4-o',
        'gpt-4omni',
        'o1',
        'o3-mini',
        'o3',
        'o4-mini',
        'o4',
        'deepseek-r1',
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-2.0-flash',
        'groq',
        'cli',
        'cli-app',
        'ollama',
        'ollama-api',
        'llama3',
        'llama3.1',
        'llama3.2',
        'llama3.3',
        'matuco19',
        'openai',
        'python3',
        'gitpython',
        'pollinations.ai',
        'pollinations',
        'google-generativeai',
        'gemini',
        'gemini-api',
        'google-ai'
    ],
)
