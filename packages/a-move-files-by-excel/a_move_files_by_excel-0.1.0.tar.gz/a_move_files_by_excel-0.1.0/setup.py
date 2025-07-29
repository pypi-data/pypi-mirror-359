
from setuptools import setup, find_packages
setup(
    name='a_move_files_by_excel',
    version='0.1.0',
    description='极简批量移动文件脚本，支持Excel批量移动并保留原始路径结构，适合所有用户。',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='nighm',
    author_email='nighm@sina.com',
    url='',
    packages=find_packages(),
    install_requires=['pandas>=1.5.0', 'openpyxl>=3.0.10', 'lxml==4.9.3', 'html5lib==1.1', 'beautifulsoup4>=4.11.0', 'PyYAML>=6.0'],
    include_package_data=True,
    license='MIT',
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={'console_scripts': ['a_move_files_by_excel = a_move_files_by_excel.move_files_by_excel:main']},
)
