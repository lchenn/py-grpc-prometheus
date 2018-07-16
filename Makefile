.PHONY: initialize-development

# Initialize the project development environment.
initialize-development:
	@pip install --upgrade -r requirements.txt
	@pip install --upgrade pylint future pre-commit
	@pre-commit install

# Run pre-commit for all
pre-commit:
	@pre-commit run --all-files
