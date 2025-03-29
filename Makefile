build-all:
	bash ./scripts/build.sh

test-all:
	bash ./scripts/test.sh

coverage-all:
	bash ./scripts/coverage.sh

linting:
	bash ./scripts/linting.sh

generate-new-pdf-samples:
	bash ./scripts/new_pdf_samples.sh

compare-pdf-diffs:
	bash ./scripts/pdf_diffs.sh

deploy:
	bash ./scripts/create_release.sh

bump-patch:
	bash ./scripts/bump_version.sh patch

bump-minor:
	bash ./scripts/bump_version.sh minor

bump-major:
	bash ./scripts/bump_version.sh major

serve-docs:
	bash ./scripts/serve_docs.sh

serve-files:
	bash ./scripts/http_server.sh

clean-temp:
	rm ./temp/*.pdf
