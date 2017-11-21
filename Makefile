tests = tests.py
module = logger_helper
documentation_dir = docs

docker_image = logger-helper-build-environment

# Define the base command to run another command inside our build environment
define docker_run
	docker run \
	--rm \
	--volume "$(PWD)":"$(PWD)" \
	--name "$(docker_image)-$(shell hexdump -n 5 -e '"%02x"' /dev/urandom)" \
	--workdir "$(PWD)" \
	$(2) \
	$(docker_image) \
	$(1)
endef

.PHONY: all
all: test lint docs

.PHONY: build-environment
build-environment:
	@echo "Building environment"
	@docker build --tag $(docker_image) .

.PHONY: run-build-environment
run-build-environment: build-environment
	@echo "Running build environment"
	@$(call docker_run, /bin/sh, -it)

.PHONY: docs
docs: build-environment
	@echo "Building documentation"
	@$(call docker_run, $(MAKE) -C $(documentation_dir) html)

.PHONY: serve-docs
serve-docs: docs
	@echo "Serving documentation on localhost:8080..."
	@cd docs/_build/html && python3 -m http.server 8080

.PHONY: test
test: build-environment
	@echo "Running tests"
	@$(call docker_run, coverage run -m unittest $(tests))

.PHONY: lint
lint: lint-module lint-tests

.PHONY: lint-module
lint-module: build-environment
	@echo "Linting the module code"
	@$(call docker_run, pylint --reports no $(module))
	@$(call docker_run, flake8 $(module))

.PHONY: lint-tests
lint-tests: build-environment
	@echo "Linting the test code"
	@$(call docker_run, \
			pylint \
				--reports no \
				--disable protected-access \
				--disable missing-docstring \
				$(tests))
	@$(call docker_run, flake8 \
			--ignore $(strip D100,D101,D102,D103,D107) \
			$(tests))
