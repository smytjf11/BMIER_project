from pptx import Presentation

# Create a new presentation
presentation = Presentation()

# Add a slide to the presentation
slide = presentation.slides.add_slide(presentation.slide_layouts[0])

# Add a title to the slide
title = slide.shapes.title
title.text = "My Presentation"

# Add some body text to the slide
body = slide.shapes.placeholders[1]
tf = body.text_frame
tf.text = "This is the body of my presentation."

# Save the presentation to a file
presentation.save("presentation.pptx")
