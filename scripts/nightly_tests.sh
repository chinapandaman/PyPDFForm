docker exec -i $(docker run -i -d --rm 
    -v ./tests:/pypdfform/tests 
    -v ./pdf_samples:/pypdfform/pdf_samples 
    -v ./font_samples:/pypdfform/font_samples 
    -v ./image_samples:/pypdfform/image_samples 
    -v ./js_samples:/pypdfform/js_samples 
    pypdfform-dev) 
    bash -c "pip install PyPDFForm; coverage run -m pytest"
