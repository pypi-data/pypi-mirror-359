"""
Type stubs for RustyTags - High-performance HTML generation library
"""

from typing import Any, Union

# Type aliases for better type hints
AttributeValue = Union[str, int, float, bool]
Child = Union[str, int, float, bool, "HtmlString", Any]

class HtmlString:
    """Core HTML content container with optimized memory layout"""
    content: str
    
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def render(self) -> str: ...
    def _repr_html_(self) -> str: ...



# HTML Tag Functions
def A(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a hyperlink"""
    ...

def Aside(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines aside content"""
    ...

def B(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines bold text"""
    ...

def Body(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the document body"""
    ...

def Br(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a line break"""
    ...

def Button(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a clickable button"""
    ...

def Code(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines computer code"""
    ...

def Div(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a division or section"""
    ...

def Em(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines emphasized text"""
    ...

def Form(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an HTML form"""
    ...

def H1(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 1 heading"""
    ...

def H2(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 2 heading"""
    ...

def H3(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 3 heading"""
    ...

def H4(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 4 heading"""
    ...

def H5(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 5 heading"""
    ...

def H6(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 6 heading"""
    ...

def Head(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the document head"""
    ...

def Header(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a page header"""
    ...

def Html(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the HTML document with DOCTYPE"""
    ...

def I(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines italic text"""
    ...

def Img(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an image"""
    ...

def Input(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an input field"""
    ...

def Label(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a label for a form element"""
    ...

def Li(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a list item"""
    ...

def Link(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a document link"""
    ...

def Main(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the main content"""
    ...

def Nav(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines navigation links"""
    ...

def P(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a paragraph"""
    ...

def Script(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a client-side script"""
    ...

def Section(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a section"""
    ...

def Span(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an inline section"""
    ...

def Strong(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines strong/important text"""
    ...

def Table(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table"""
    ...

def Td(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table cell"""
    ...

def Th(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table header cell"""
    ...

def Title(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the document title"""
    ...

def Tr(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table row"""
    ...

def Ul(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an unordered list"""
    ...

def Ol(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an ordered list"""
    ...

def CustomTag(tag_name: str, *children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Creates a custom HTML tag with any tag name"""
    ...

# SVG Tag Functions
def Svg(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an SVG graphics container"""
    ...

def Circle(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a circle in SVG"""
    ...

def Rect(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a rectangle in SVG"""
    ...

def Line(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a line in SVG"""
    ...

def Path(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a path in SVG"""
    ...

def Polygon(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a polygon in SVG"""
    ...

def Polyline(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a polyline in SVG"""
    ...

def Ellipse(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an ellipse in SVG"""
    ...

def Text(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines text in SVG"""
    ...

def G(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a group in SVG"""
    ...

def Defs(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines reusable SVG elements"""
    ...

def Use(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a reusable SVG element instance"""
    ...

def Symbol(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a reusable SVG symbol"""
    ...

def Marker(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a marker for SVG shapes"""
    ...

def LinearGradient(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a linear gradient in SVG"""
    ...

def RadialGradient(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a radial gradient in SVG"""
    ...

def Stop(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a gradient stop in SVG"""
    ...

def Pattern(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a pattern in SVG"""
    ...

def ClipPath(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a clipping path in SVG"""
    ...

def Mask(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a mask in SVG"""
    ...

def Image(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an image in SVG"""
    ...

def ForeignObject(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines foreign content in SVG"""
    ...

# Phase 1: Critical High Priority HTML Tags
def Meta(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines metadata about an HTML document"""
    ...

def Hr(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a thematic break/horizontal rule"""
    ...

def Iframe(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an inline frame"""
    ...

def Textarea(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a multiline text input control"""
    ...

def Select(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a dropdown list"""
    ...

def Figure(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines self-contained content"""
    ...

def Figcaption(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a caption for a figure element"""
    ...

def Article(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines independent, self-contained content"""
    ...

def Footer(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a footer for a document or section"""
    ...

def Details(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines additional details that can be viewed or hidden"""
    ...

def Summary(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a visible heading for a details element"""
    ...

def Address(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines contact information for the author"""
    ...

# Phase 2: Table Enhancement Tags
def Tbody(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table body"""
    ...

def Thead(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table header"""
    ...

def Tfoot(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table footer"""
    ...

def Caption(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table caption"""
    ...

def Col(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table column"""
    ...

def Colgroup(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a group of table columns"""
    ...

# All remaining HTML tags - comprehensive implementation
def Abbr(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an abbreviation"""
    ...

def Area(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an area in an image map"""
    ...

def Audio(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines audio content"""
    ...

def Base(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the base URL for all relative URLs"""
    ...

def Bdi(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines bidirectional text isolation"""
    ...

def Bdo(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines bidirectional text override"""
    ...

def Blockquote(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a block quotation"""
    ...

def Canvas(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a graphics canvas"""
    ...

def Cite(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a citation"""
    ...

def Data(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines machine-readable data"""
    ...

def Datalist(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a list of input options"""
    ...

def Dd(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a description in a description list"""
    ...

def Del(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines deleted text"""
    ...

def Dfn(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a definition term"""
    ...

def Dialog(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a dialog box"""
    ...

def Dl(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a description list"""
    ...

def Dt(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a term in a description list"""
    ...

def Embed(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines external content"""
    ...

def Fieldset(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a fieldset for form controls"""
    ...

def Hgroup(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a heading group"""
    ...

def Ins(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines inserted text"""
    ...

def Kbd(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines keyboard input"""
    ...

def Legend(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a caption for a fieldset"""
    ...

def Map(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an image map"""
    ...

def Mark(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines highlighted text"""
    ...

def Menu(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a menu list"""
    ...

def Meter(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a scalar measurement"""
    ...

def Noscript(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines content for users without script support"""
    ...

def Object(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an embedded object"""
    ...

def Optgroup(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a group of options in a select list"""
    ...

def OptionEl(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an option in a select list"""
    ...

def Picture(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a picture container"""
    ...

def Pre(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines preformatted text"""
    ...

def Progress(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines progress of a task"""
    ...

def Q(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a short quotation"""
    ...

def Rp(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines ruby parentheses"""
    ...

def Rt(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines ruby text"""
    ...

def Ruby(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines ruby annotation"""
    ...

def S(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines strikethrough text"""
    ...

def Samp(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines sample computer output"""
    ...

def Small(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines small text"""
    ...

def Source(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines media resources"""
    ...

def Style(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines style information"""
    ...

def Sub(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines subscript text"""
    ...

def Sup(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines superscript text"""
    ...

def Template(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a template container"""
    ...

def Time(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines date/time information"""
    ...

def Track(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines media track"""
    ...

def U(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines underlined text"""
    ...

def Var(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a variable"""
    ...

def Video(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines video content"""
    ...

def Wbr(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a word break opportunity"""
    ...

__version__: str
__author__: str 
__description__: str