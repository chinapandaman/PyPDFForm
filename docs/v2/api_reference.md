# API Reference

This part of the documentation covers all the interfaces 
of PyPDFForm.

## PyPDFForm Object

### *class* PyPDFForm.**PyPDFForm**(*template=b"", simple_mode=True, global_font="Helvetica", global_font_size=12, global_font_color=(0, 0, 0), global_text_x_offset=0, global_text_y_offset=0, global_text_wrap_length=100*)

The PyPDFForm object implements a PDF form and acts as 
the central object. It can be constructed with or without a 
template stream. In the case of latter it acts as an empty PDF 
object and can be used to concatenate with other PDFs. Turning simple 
mode on and off yields different interactions with the fill method.

#### Parameters:

* **template** - a file path, file object, or `bytes` stream of the unfilled PDF form template.

* **simple_mode** - a simple mode PyPDFForm object only allows filling data without specifying 
details like font size. Turning simple mode on also allows leaving PDF editable 
after filling. NOTE: `simple_mode` is not available when `sejda` is set to `True`.
  
* **global_font** - a string which sets the global font for text filled on the PDF form. The 
font set by this parameter has to be registered first. This will only take effect if `simple_mode` is `False`. 
  
* **global_font_size** - an integer/float value which sets the global font size for texts 
filled on the PDF form. This will only take effect if `simple_mode` is `False`.
  
* **global_font_color** - an RGB integer/float tuple which sets the global font color for texts 
filled on the PDF form. This will only take effect if `simple_mode` is `False`.
  
* **global_text_x_offset** - an integer/float value which sets the global horizontal offset for texts 
filled on the PDF form. This will only take effect if `simple_mode` is `False`.
  
* **global_text_y_offset** - an integer/float value which sets the global vertical offset for texts 
filled on the PDF form. This will only take effect if `simple_mode` is `False`.
  
* **global_text_wrap_length** - an integer value which sets the global maximum number of characters before 
wrapping to a new line for texts 
filled on the PDF form. This will only take effect if `simple_mode` is `False`.
  
* **sejda** - This boolean parameter should be set to `True` if the PDF form template is prepared using Sejda. 
NOTE: enabling this will disable `simple_mode` even if it's set to `True`.

### *PyPDFForm()* **+** *PyPDFForm()*

PyPDFForm supports merging of multiple PDFs by overloading the addition operator. 
This operation can also be done by assignment operator `+=`.

### **draw_image**(*image, page_number, x, y, width, height, rotation=0*)

The draw image method takes an image and draws it 
on the specified page, coordinates with specified resolutions and rotation angle.

#### Parameters:

* **image** - a file path, file object, or `bytes` stream of the image.

* **page_number** - integer, page number of which the image will be drawn on.

* **x** - integer/float, horizontal coordinate of which the image will be drawn at.

* **y** - integer/float, vertical coordinate of which the image will be drawn at.

* **width** - integer/float, horizontal resolution of the image after drawn.

* **height** - integer/float, vertical resolution of the image after drawn.

* **rotation** - integer/float, degrees the image will be rotated after drawn.

### **draw_text**(*text, page_number, x, y, font="Helvetica", font_size=12, font_color=(0, 0, 0), text_x_offset=0, text_y_offset=0, text_wrap_length=100*)

The draw text method takes a text string and draws it on the specified page 
at the specified coordinates.

#### Parameters:

* **text** - string, a text string.

* **page_number** - integer, page number of which the text will be drawn on.

* **x** - integer/float, horizontal coordinate of which the text will be drawn at.

* **y** - integer/float, vertical coordinate of which the text will be drawn at.

* **font** - string, sets the font for text drawn. Font set by this parameter has to be 
registered first.

* **font_size** - integer/float, font size of the text drawn.

* **font_color** - RGB integer/float tuple, font color of the text drawn.

* **text_x_offset** - integer/float, horizontal offset of the text drawn.

* **text_y_offset** - integer/float, vertical offset of the text drawn.

* **text_wrap_length** - integer/float, maximum number of characters before wrapping to a new line for the text drawn.

### **elements**

A Python dictionary only available when `simple_mode` is `False`. 
This attribute is the primary way of customizing details like font size and text wrap length for an individual element. 
Its keys consist 
all elements' annotated names while the values hold their corresponding `Element()` objects. 
Please read more about `Element()` [here](https://github.com/chinapandaman/PyPDFForm/blob/master/docs/v2/api_reference.md#element-object).

### **fill**(*data, editable=False*)

The fill method takes a Python dictionary object `data` and fill the PDF form 
template with it. Keys of the objects should match the annotated names of elements on the PDF form. 
Based on types of values as well as different types of elements different 
actions will be performed on the PDF form.

#### Parameters:

* **data** - a Python dictionary which holds the data that will be filled on the PDF form. 
Its keys have to be `string` and need to match the annotated names of elements. 
Its values currently support the following:
    1) A `string`, which will be printed on the corresponding `text` element.
    2) A `boolean`, which will check the corresponding `checkbox` element.
    3) An `integer`, which will select the corresponding option of a group of radio buttons with the same name.
       NOTE: Only groups of radio buttons with the same name are supported. If there is only one 
       radio button with a name, please consider using `checkbox` instead.

* **editable** - only available if `simple_mode` is `True` and `sejda` is `False`, enabling this will allow the filled PDF to be still 
editable.
  
### **read**()

Returns the `stream`. This method allows the implementation of PyPDFForm to behave like a file object.

### **register_font**(*font_name, ttf_file*)

This class method takes a TTF font file stream and register it with the `font_name` specified. 
Registered fonts can then be used by any instance of object.

#### Parameters:

* **font_name** - a string of which the font will be registered as. Registered fonts can be referenced and 
used via this name.

* **ttf_file** - a file path, file object, or `bytes` stream of the ttf font file.

### **simple_mode** = *True*

A boolean value which indicates whether the PDF form can be filled with more detailed specifications 
like font size.

### **stream** = *b""*

A `bytes` object which holds the stream with the current state of the PDF form. This can be used by 
Python IO to `.write` to another destination.

## Element Object

### *class* PyPDFForm.middleware.element.**Element**(*element_name, element_type, element_value*)

The Element object implements a single PDF form element. It is constructed for each element 
of a **non-simple-mode** `PyPDFForm` object constructed with a template stream and makes up the `elements` attribute. 
When accessed through the `elements` attribute it can be used to customize an individual element's detail for filling method 
such as font size and text wrap length.

#### Parameters:

* **element_name** - a string which represents the annotated name of the element.

* **element_type** - an enum which represents the type of the element, currently supporting 
`text`, `checkbox`, and `radio`.

* **element_value** - this is the value that's used to fill this element. 
It currently supports the following based on the type of the element:
  1) A `string`, if the element is a `text`.
  2) A `boolean`, if the element is a `checkbox`.
  3) An `integer`, if the element is a `radio`.

### **name**

A string which represents the annotated name of the element. Readonly.

### **type**

An enum value which represents the type of the element, currently supporting 
`text`, `checkbox`, and `radio`. Readonly.

### **value**

This attribute holds the value that's used to fill this element. 
It currently supports the following based on the type of the element:

1) A `string`, if the element is a `text`.
2) A `boolean`, if the element is a `checkbox`.
3) An `integer`, if the element is a `radio`.

### **font** = *None*

Only available if the `element_type` is `text`. Setting this string attribute will 
change the font used for the text filled on this element.

### **font_size** = *None*

Only available if the `element_type` is `text`. Setting this numerical attribute will 
change the font size used for the text filled on this element.

### **font_color** = *None*

Only available if the `element_type` is `text`. Setting this tuple of RGB values will 
change the font color used for the text filled on this element.

### **text_x_offset** = *None*

Only available if the `element_type` is `text`. Setting this numerical attribute will 
change the horizontal offset used for the text filled on this element.

### **text_y_offset** = *None*

Only available if the `element_type` is `text`. Setting this numerical attribute will 
change the vertical offset used for the text filled on this element.

### **text_wrap_length** = *None*

Only available if the `element_type` is `text`. Setting this integer attribute will 
change the maximum text wrap length used for the text filled on this element.

### **validate_constants**()

The validate method validates all readonly attributes for the Element object and raises 
appropriate exceptions based on the validation.

### **validate_text_attributes**()

The validate method validates all `text` attributes for the Element object and raises 
appropriate exceptions based on the validation.

### **validate_value**()

The validate method validates the `value` of the Element object and raises 
appropriate exceptions based on the validation.
