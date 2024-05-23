.PHONY: clean install test docker_image

clean:
	find . -name '*.py[co]' -delete
	rm -rf build
	rm -rf *.egg-info
	rm -rf venv
	rm -rf .pytest_cache



install: clean
	virtualenv -p python3 --prompt '|> cloudflare_ddns <| ' venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install pytest
	venv/bin/pip install .
	@echo
	@echo "VirtualENV Setup Complete. Now run: source venv/bin/activate"
	@echo


test:
	pytest -rA tests/




docker_image:
	docker build -t cloudflare_ddns:latest .


