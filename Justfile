package := 'wagtail_oauth2'
default_test_suite := 'src/tests'

install:
    uv sync --group doc --frozen

update:
    uv sync --group dev

upgrade:
    uv sync --group dev --upgrade

doc:
    uv sync --group dev --group doc
    cd docs && uv run make html
    xdg-open docs/build/html/index.html

cleandoc:
    cd docs && uv run make clean

lint:
    uv run ruff check .

test: lint unittest

unittest test_suite=default_test_suite:
    uv run pytest -sxv {{test_suite}}

lf:
    uv run pytest -sxvvv --lf

cov test_suite=default_test_suite:
    rm -f .coverage
    rm -rf htmlcov
    uv run pytest --cov-report=html --cov={{package}} {{test_suite}}
    xdg-open htmlcov/index.html

fmt:
    uv run ruff check --fix .
    uv run ruff format src

release major_minor_patch: test && changelog
    uvx --with=pdm,pdm-bump --python-preference system pdm bump {{major_minor_patch}}
    uv sync --group dev --frozen

changelog:
    uv run python scripts/write_changelog.py
    cat CHANGELOG.rst >> CHANGELOG.rst.new
    rm CHANGELOG.rst
    mv CHANGELOG.rst.new CHANGELOG.rst
    $EDITOR CHANGELOG.rst

publish:
    git commit -am "Release $(uv run scripts/get_version.py)"
    git tag "v$(uv run scripts/get_version.py)"
    git push
    git push origin "v$(uv run scripts/get_version.py)"
