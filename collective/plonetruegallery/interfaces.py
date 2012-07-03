from zope.interface import Interface, Attribute
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery import PTGMessageFactory as _


class IGalleryAdapter(Interface):
    sizes = Attribute("image size mappings for the gallery type")
    schema = Attribute("Schema of gallery specific")
    name = Attribute("Name of the gallery")
    description = Attribute("Description of gallery type")
    cook_delay = Attribute("Time between updates of gallery images.  "
        "This update of images can be forced by appending refresh on "
        "a gallery.")
    cooked_images = Attribute("The images after they've been cooked up.")

    def cook():
        """
        this will make it so the gallery's images are not aggregated every
        single time the gallery is displayed.
        """

    def time_to_cook():
        """
        called to see if it is time to the cook the gallery.
        """

    def get_random_image():
        """
        returns a random image with data.
        returns an empty dict if the gallery is empty.
        """

    def log_error():
        """
        provides an easy way to log errors in gallery adapters.
        we don't want an adapter to prevent a page from loading...
        Who knows what kind of odd behavior some adapters may run into
        when working with picasa or flickr apis...
        """

    def retrieve_images():
        """
        This method retrieves all the images to be cooked
        """
    def number_of_images():
        """"""

    def get_all_images():
        """
        returns all the cooked images for the gallery
        """


class IBasicAdapter(IGalleryAdapter):
    """
    Use plone to manage images for the gallery.
    """

    size_map = Attribute("allows us to map specific sizes to plone urls")


class IFlickrAdapter(IGalleryAdapter):
    """
    """

    flickr = Attribute("returns a flickrapi object for the api key")

    def get_flickr_user_id(username):
        """
        Returns the actual user id of someone given a username.
        if a username is not given, it will use the one in its
        settings
        """

    def get_flickr_photoset_id(theset=None, userid=None):
        """
        Returns the photoset id given a set name and user id.
        Uses the set and get_flickr_user_id() if they are
        not specified.
        """

    def get_mini_photo_url(photo):
        """
        takes a photo and creates the thumbnail photo url
        """

    def get_photo_link(photo):
        """
        creates the photo link url
        """

    def get_large_photo_url(photo):
        """
        create the large photo url
        """


class IPicasaAdapter(IGalleryAdapter):
    """
    """

    gd_client = Attribute("property for gd_client instance")

    def get_album_name(name, user):
        """
        Returns the selected album name and user.
        Uses name and user in settings if not specified.
        """

    def feed():
        """
        Returns the picasa feed for the given album.
        """


class IDisplayType(Interface):
    name = Attribute("name of display type")
    description = Attribute("description of type")
    schema = Attribute("Options for this display type")
    userWarning = Attribute("A warning to be displayed to to "
                            "the user if they use this type.")
    width = Attribute("The width of the gallery")
    height = Attribute("The height of the gallery")
    start_image_index = Attribute("What image the gallery should "
                                  "start playing at.")

    def content():
        """
        the content of the display yet
        """

    def javascript():
        """
        content to be included in javascript area of template
        """

    def css():
        """
        content to be included in css area of template
        """


class IBatchingDisplayType(Interface):

    def uses_start_image(self):
        """
        disable start image if a batch start is specified.
        """

    b_start = Attribute("")
    start_image_index = Attribute("")

    def get_page(self):
        """"""

    start_automatically = Attribute("")
    batch = Attribute("")


class IGallery(Interface):
    """
    marker interface for content types that implement
    the gallery
    """


class IGallerySettings(Interface):
    gallery_type = schema.Choice(
        title=_(u"label_gallery_type", default=u"Type"),
        description=_(u"description_gallery_type",
            default=u"Select the type of gallery you want this to be.  "
                    u"If you select something other than default, you "
                    u"must fill out the information in the corresponding "
                    u"tab for that gallery type."),
        vocabulary="collective.plonetruegallery.GalleryTypeVocabulary",
        default="basic")
    display_type = schema.Choice(
        title=_(u"label_gallery_display_type",
                default=u"Gallery Display Type"),
        description=_(
            u"label_gallery_display_type_description",
            default=u"Choose the method in which the "
                    u"gallery should be displayed"
        ),
        default="galleria",
        vocabulary="collective.plonetruegallery.DisplayTypes")
    # the specific options for the gallery types will be added
    # dynamcially in the form
    size = schema.Choice(
        title=_(u"label_gallery_size", default=u"Size"),
        description=_(u"description_gallery_size",
            default=u"The actual sizes used can vary depending on the "
                    u"gallery type that is used since different services "
                    u"have different size constraints."),
        default='medium',
        vocabulary=SimpleVocabulary([
            SimpleTerm('small', 'small', _(u"label_size_small",
                                            default=u'Small')),
            SimpleTerm('medium', 'medium', _(u"label_size_medium",
                                            default=u'Medium')),
            SimpleTerm('large', 'large', _(u"label_size_large",
                                            default=u'Large'))
        ]))
    thumb_size = schema.Choice(
        title=_(u"label_thumb_size", default=u"Thumbnail image size"),
        description=_(u"description_thumb_size",
            default=u"The size of thumbnail images. "
                    u"Will only work with plone image gallery type."
        ),
        default='thumb',
        vocabulary=SimpleVocabulary([
            SimpleTerm('tile', 'tile', _(u"label_tile", default=u"tile")),
            SimpleTerm('thumb', 'thumb', _(u"label_thumb", default=u"thumb")),
            SimpleTerm('mini', 'mini', _(u"label_mini", default=u"mini")),
            SimpleTerm('preview', 'preview', _(u"label_preview",
                                                default=u"preview")),
        ]))
    # the options for the display type will also be added dynamically
    timed = schema.Bool(
        title=_(u"label_timed", default=u"Timed?"),
        description=_(u"description_timed",
            default=u"Should this gallery automatically "
                    u"change images for the user?"
        ),
        default=True)
    delay = schema.Int(
        title=_(u"label_delay", default=u"Delay"),
        description=_(u"description_delay",
            default=u"If slide show is timed, the delay sets "
                    u"how long before the next image is shown in miliseconds."
        ),
        default=5000,
        required=True)
    duration = schema.Int(
        title=_(u"label_image_change_duration", default=u"Change Duration"),
        description=_(u"description_fade_in_duration",
            default=u"The amount of time the change effect should "
                    u"take in miliseconds."
        ),
        default=500,
        required=True)
    show_subgalleries = schema.Bool(
        title=_(u"label_show_subgalleries", default=u"Show Sub-Galleries?"),
        description=_(u"description_show_subgalleries",
            default=u"If you select this option, previews for all "
                    u"nested galleries will show up below this gallery."
        ),
        default=True)
    batch_size = schema.Int(
        title=_(u"label_batch_size", default=u"Batch Size"),
        description=_(u"description_batch_size",
            default=u"The amount of images shown in one page. "
                    u"This is not used for all display types."
        ),
        default=50,
        required=True)


class IBaseSettings(Interface):
    pass


class IS3sliderDisplaySettings(IBaseSettings):
    s3_width = schema.TextLine(
        title=_(u"label_s3_width",
            default=u"Width of the gallery"),
        default=u"600px")
    s3_height = schema.TextLine(
        title=_(u"label_s3_height",
            default=u"Height of the gallery"),
        default=u"350px")
    s3_textwidth = schema.TextLine(
        title=_(u"label_s3_textwidth",
            default=u"Width of the (black) text box"),
        default=u"150px")
    s3slider_style = schema.Choice(
        title=_(u"label_s3slider_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_s3slider_style_default",
                    default=u"Default")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_s3slider_style_custom",
                    default=u"Custom css file")
            )
        ]))
    s3slider_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class IThumbnailzoomDisplaySettings(IBaseSettings):
    thumbnailzoom_columns = schema.Int(
        title=_(u"label_thumbnailzoom_columns",
            default=u"Number of thumbs before a forced new row (use a high "
                    u"number if you dont want this)"),
        default=3,
        min=1)
    thumbnailzoom_increase = schema.Int(
        title=_(u"label_thumbnailzoom_increase",
            default=u"Pixels to zoom when mouse over"),
        default=50)
    thumbnailzoom_effectduration = schema.Int(
        title=_(u"label_thumbnaizoom_effectduration",
            default=u"How long time the effect takes"),
        default=100,
        min=16)
    thumbnailzoom_use_icons = schema.Bool(
        title=_(u"label_thumbnailzoom_use_images",
            default=u"Use Image size instead of Thumbnail size"),
        default=False)
    thumbnailzoom_style = schema.Choice(
        title=_(u"label_thumbnailzoom_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_thumbnailzoom_style_default",
                    default=u"Default")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_thumbnailzoom_style_custom",
                    default=u"Custom css file")
            )
        ]))
    thumbnailzoom_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class ISupersizedDisplaySettings(IBaseSettings):
    supersized_slideshow = schema.Bool(
        title=_(u"label_slideshow",
            default=u"Slideshow on"),
        default=True)
    supersized_stop_loop = schema.Bool(
        title=_(u"label_stop_loop",
            default=u"Pauses slideshow on last slide"),
        default=False)
    supersized_transition = schema.Choice(
        title=_(u"label_supersized_transition",
            default=u"Transition"),
        default=1,
        vocabulary=SimpleVocabulary([
            SimpleTerm(0, 0,
                _(u"label_supersized_transition0", default=u"None")),
            SimpleTerm(1, 1,
                _(u"label_supersized_transition1", default=u"Fade")),
            SimpleTerm(2, 2,
                _(u"label_supersized_transition2", default=u"Slide Top")),
            SimpleTerm(3, 3,
                _(u"label_supersized_transition3", default=u"Slide Right")),
            SimpleTerm(4, 4,
                _(u"label_supersized_transition4", default=u"Slide Bottom")),
            SimpleTerm(5, 5,
                _(u"label_supersized_transition5", default=u"Slide Left")),
            SimpleTerm(6, 6,
                _(u"label_supersized_transition6", default=u"Carousel Right")),
            SimpleTerm(7, 7,
                _(u"label_supersized_transition7", default=u"Carousel Left")
            )
        ]))
    supersized_performance = schema.Choice(
        title=_(u"label_performance",
            default=u"Performance"),
        default=1,
        vocabulary=SimpleVocabulary([
            SimpleTerm(0, 0,
                _(u"label_supersized_performance0", default=u"Normal")),
            SimpleTerm(1, 1,
                _(u"label_supersized_performance1",
                    default=u"Hybrid between speed and quality")),
            SimpleTerm(2, 2,
                _(u"label_supersized_performance2",
                    default=u"Optimizes image quality")),
            SimpleTerm(3, 3,
                _(u"label_supersized_performance3",
                    default=u"Optimizes transition speed. Only works for "
                            u"Firefox, IE, not Webkit")
            )
        ]))
    supersized_min_width = schema.Int(
        title=_(u"label_min_width",
            default=u"Min width allowed, in pixels"),
        default=0)
    supersized_min_height = schema.Int(
        title=_(u"label_min_height",
            default=u"Min height allowed, in pixels"),
        default=0)
    supersized_horizontal_center = schema.Bool(
        title=_(u"label_horizontal_center",
            default=u"Horizontally center background"),
        default=True)
    supersized_vertical_center = schema.Bool(
        title=_(u"label_vertical_center",
            default=u"Vertically center background"),
        default=True)
    supersized_fit_always = schema.Bool(
        title=_(u"label_fit_always",
            default=u"Image will never exceed browser width or height. "
                    u"Ignores min. dimensions"),
        default=False)
    supersized_fit_portrait = schema.Bool(
        title=_(u"label_fit_portrait",
            default=u"Portrait images will not exceed browser height"),
        default=True)
    supersized_fit_landscape = schema.Bool(
        title=_(u"label_fit_landscape",
            default=u"Landscape images will not exceed browser width"),
        default=False)
    supersized_thumbnail_navigation = schema.Bool(
        title=_(u"label_thumbnail_navigation",
            default=u"Show next and previous thumb "),
        default=False)
    supersized_thumb_links = schema.Bool(
        title=_(u"label_thumb_links",
            default=u"Individual thumb links for each "
                    u"slide in the 'bottom tray'"),
        default=True)
    supersized_slide_links = schema.Choice(
        title=_(u"label_slide_link",
            default=u"Show slide names in the center of bottom tray (you will "
                    u"need to style 'Name' with css)"),
        default="blank",
        vocabulary=SimpleVocabulary([
            SimpleTerm('name', 'name',
                _(u"label_slide_links_name",
                    default=u"Name")),
            SimpleTerm('blank', 'blank',
                _(u"label_slide_links_blank",
                    default=u"Blank")
            )
        ]))
    supersized_progress_bar = schema.Bool(
        title=_(u"label_progress_bar",
            default=u"Show progress bar"),
        default=False)
    supersized_show_controls = schema.Bool(
        title=_(u"label_show_controls",
            default=u"Hide ALL Controls"),
        default=False)
    supersized_css = schema.Text(
        title=_(u"label_supersized_css",
            default=u"CSS to customize the layout"),
        required=False,
        default=u'#portal-footer {display: none; } body {background: #111; }')


class IPresentationDisplaySettings(IBaseSettings):
    presentation_effect = schema.Choice(
        title=_(u"label_presentation_effect",
            default=u"Mouseover or click"),
        default="click",
        vocabulary=SimpleVocabulary([
            SimpleTerm("click", "click",
                _(u"label_presentation_click", default=u"Click on image")),
            SimpleTerm("mouseenter", "mouseenter",
                _(u"label_presentation_mouseover", default=u"Mouse enter")
            )
        ]))
    presentation_width = schema.Int(
        title=_(u"label_presentation_width",
            default=u"Width of the gallery in pixels"),
        default=600,
        min=200)
    presentation_height = schema.Int(
        title=_(u"label_presentation_height",
            default=u"Height of the gallery in pixels"),
        default=350,
        min=60)
    minimum_width = schema.Int(
        title=_(u"label_presentation_minimum_width",
            default=u"Minimum width of images"),
        default=15)
    presentation_xposition = schema.Choice(
        title=_(u"label_presentation_xposition",
            default=u"Horizontal image position"),
        default="center",
        vocabulary=SimpleVocabulary([
            SimpleTerm("top", "top",
                _(u"label_presentation_xpositiontop", default=u"Top")),
            SimpleTerm("center", "center",
                _(u"label_presentation_xpositioncenter", default=u"Center")),
            SimpleTerm("bottom", "bottom",
                _(u"label_presentation_xpositionbottom", default=u"Bottom")
            )
        ]))
    presentation_yposition = schema.Choice(
        title=_(u"label_presentation_yposition",
            default=u"Vertical image position"),
        default="center",
        vocabulary=SimpleVocabulary([
            SimpleTerm("left", "left",
                _(u"label_presentation_ypositionleft", default=u"Left")),
            SimpleTerm("center", "center",
                _(u"label_presentation_ypositioncenter", default=u"Center")),
            SimpleTerm("right", "right",
                _(u"label_presentation_ypositionright", default=u"Right")
            )
        ]))


class IBasicGallerySettings(IBaseSettings):
    pass


class IFlickrGallerySettings(IBaseSettings):
    flickr_username = schema.TextLine(
        title=_(u"label_flickr_username", default=u"flickr username"),
        description=_(u"description_flickr_username",
            default=u"The username/id of your flickr account. "
                    u"(*flickr* gallery type)"
        ),
        required=False)
    flickr_set = schema.TextLine(
        title=_(u"label_flickr_set", default="Flickr Set"),
        description=_(u"description_flickr_set",
            default=u"Name/id of your flickr set."
                    u"(*flickr* gallery type)"
        ),
        required=False)


class IPicasaGallerySettings(IBaseSettings):
    picasa_username = schema.TextLine(
        title=_(u"label_picasa_username", default=u"GMail address"),
        description=_(u"description_picasa_username",
            default=u"GMail address of who this album belongs to. "
                    u"(*Picasa* gallery type)"
        ),
        required=False)
    picasa_album = schema.TextLine(
        title=_(u"label_picasa_album", default=u"Picasa Album"),
        description=_(u"description_picasa_album",
            default=u"Name of your picasa web album. "
                    u"This will be the qualified name you'll see in "
                    u"the address bar or the full length name of the "
                    u"album. (*Picasa* gallery type)"
        ),
        required=False)


class IImageInformationRetriever(Interface):
    """
    This interface is interesting for everybody who wants to filter
    the items to be shown in a gallery view
    """
    def getImageInformation(self, size):
        """
        Return a list of Information relevant for gallery display for each
        image.
        Size should be a hint of the image size to use, in string format.
        The standard implementations support the following sizes, which
        map to the given size of the archetypes Image size:

            small -> mini
            medium -> preview
            large -> large

        This information returned consists of:
        image_url
            The URL to the image itself
        thumb_url
            The URL to a thumbnail version of the image
        link
            The Link to which an image must point to
        title
            The image title
        description
            The image description
        """
