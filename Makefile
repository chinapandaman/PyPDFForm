build-all:
	bash ./scripts/build.sh

test-all:
	bash ./scripts/test.sh

coverage-all:
	bash ./scripts/coverage.sh

linting:
	bash ./scripts/linting.sh

format-code:
	bash ./scripts/format.sh

generate-new-pdf-samples:
	bash ./scripts/new_pdf_samples.sh

compare-pdf-diffs:
	bash ./scripts/pdf_diffs.sh

compare-widget-diffs:
	bash ./scripts/diff_widget.sh $(F1) $(F2) $(KEY) $(LV)

serve-docs:
	bash ./scripts/serve_docs.sh

serve-files:
	bash ./scripts/http_server.sh

fix-permission:
	rm -rf ./pdf_samples ./PyPDFForm ./tests ./scripts
	git checkout -- ./pdf_samples ./PyPDFForm ./tests ./scripts

clean-temp:
	rm ./temp/*.pdf
