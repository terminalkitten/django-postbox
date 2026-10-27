.PHONY: rs migrate shell mail htmx screenshots lint test docs docs-serve clean

rs:
	uv run python manage.py runserver

migrate:
	mkdir -p db
	uv run python manage.py migrate

shell:
	uv run python manage.py shell

mail:
	uv run python manage.py send_test_mails --bulk 30

htmx:
	uv run python scripts/update_htmx.py

screenshots:
	uv run python scripts/screenshots.py

lint:
	uv run ruff check --fix .
	uv run ruff format .
	uv run ty check
	uv run pytest

test:
	uv run pytest

docs:
	uv run dokk check
	uv run dokk build

docs-serve:
	uv run dokk serve

clean:
	rm -f db/*.db
	$(MAKE) migrate
