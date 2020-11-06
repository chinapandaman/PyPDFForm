# API Reference

This part of the documentation covers all the interfaces 
of PyPDFForm.

## PyPDFForm Object

### *class* PyPDFForm.**PyPDFForm**(*template=b"", simple_mode=True*)

The PyPDFForm object implements a PDF form and acts as 
the central object. It can be constructed with or without a 
template stream. In the case of latter it acts as an empty PDF 
object and can be used to concatenate with other PDFs. Turning simple 
mode on and off yields different interactions with the fill method.

#### Parameters:

* **template** - a byte stream of the unfilled PDF form template. Usually generated 
by python IO's `.read()` method.

* **simple_mode** - a simple mode PyPDFForm object only allows filling data without specifying 
details like font size. However turning simple mode on also allows leaving PDF editable 
after filling.

### **fill**(*data, font_size=12, text_x_offset=0, text_y_offset=0, text_wrap_length=100, editable=False*)

The fill method takes a python dictionary object `data` and fill the PDF form 
template with it. The key of the object should match the annotation names of the PDF form. 
The value of the object will be printed on the corresponding annotation field if it's a `string`. 
If the value is a `boolean` the corresponding checkboxes will be checked on the PDF form.

#### Parameters:

* **data** - a python dictionary which holds the data that will be filled on the PDF form. A `string` will 
be printed and a `boolean` will check the corresponding checkboxes.

* **font_size** - only available if `simple_mode` is `False`, sets the global font size for texts 
printed on the PDF form.

* **text_x_offset** - only available if `simple_mode` is `False`, setting this value will offset all texts 
printed on the PDF form by specified value horizontally.

* **text_y_offset** - only available if `simple_mode` is `False`, setting this value will offset all texts 
printed on the PDF form by specified value vertically.

* **text_wrap_length** - only available if `simple_mode` is `False`, sets the maximum number of characters before 
wrapping to a new line for texts printed on the PDF form.

* **editable** - only available if `simple_mode` is `True`, enabling this will allow the filled PDF to be still 
editable.

### **simple_mode** = *True*

A boolean value which indicates whether the PDF form can be filled with more detailed specifications 
like font size.

### **stream** = *b""*

A byte object which holds the stream with the current state of the PDF form. This can be used by 
python IO to `.write` to another destination.
