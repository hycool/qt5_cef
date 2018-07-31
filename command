
python setup.py sdist bdist_wheel

twine register dist/qt5_cef-0.0.4.tar.gz -r testpypi
twine upload dist/* -r testpypi

twine register dist/qt5_cef-0.0.4.tar.gz -r pypi
twine upload dist/* -r pypi