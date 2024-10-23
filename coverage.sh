
coverage run -m pytest
coverage report -m --fail-under=90
coverage html
