from zope.component import getUtilitiesFor, queryUtility
from zope.component.hooks import getSite
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from collective.plonetruegallery.interfaces import IGallerySettings, IDisplayType
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.vocabularies.catalog import SearchableTextSource
from plone.app.vocabularies.catalog import parse_query
from plone.namedfile.interfaces import IAvailableSizes
from collective.plonetruegallery.interfaces import IGallery
from Products.CMFCore.utils import getToolByName
from collective.plonetruegallery import PTGMessageFactory as _


#from collective.plonetruegallery.utils import getGalleryAdapter
    

class PTGVocabulary(SimpleVocabulary):
    """
    Don't error out if you can't find it right away
    and default to the default value...
    This prevents any issues if a gallery or display
    type is removed and the user had it selected.
    """

    def __init__(self, terms, *interfaces, **config):
        try:
            super(PTGVocabulary, self).__init__(terms, *interfaces)
        except:
            raise
        if 'default' in config:
            self.default = config['default']
        else:
            self.default = None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return self.by_value[value]
        except KeyError:
            return self.by_value[self.default]
        except:
            raise LookupError(value)


def DisplayTypeVocabulary(context):
    terms = []
    utils = list(getUtilitiesFor(IDisplayType))
    for name, utility in sorted(utils, key=lambda x: x[1].name):
        if utility.name:
            name = utility.name or name
            terms.append(SimpleTerm(name, name, utility.description))

    return PTGVocabulary(terms,
                default=IGallerySettings['display_type'].default)


def GalleryTypeVocabulary(context):
    from collective.plonetruegallery.meta.zcml import GalleryTypes
    items = []
    for t in GalleryTypes:
        items.append(SimpleTerm(t.name, t.name, t.description))

    return PTGVocabulary(items,
                default=IGallerySettings['gallery_type'].default)

def format_size(size):
    return size.split(' ')[0]

def SizeVocabulary(context):
        size_terms = { 'small' : SimpleTerm('small', 'small', _(u"label_size_small", default=u'Small')),
                        'medium' : SimpleTerm('medium', 'medium', _(u"label_size_medium",default=u'Medium')),
                        'large': SimpleTerm('large', 'large', _(u"label_size_large",default=u'Large'))
                        }
        site = getSite()
        portal_properties = getToolByName(site, 'portal_properties', None)
        # here we add the custom image sizes, we skip the small ones and
        # preview, large since they are already added.
        #if we add them back, be sure to do it in basic.py, too
        # we also need to test if gallery_type == 'basic':
        # dont think this is right, it might be the overall seting
        if IGallerySettings['gallery_type'].default  == 'basic':
            if 'imaging_properties' in portal_properties.objectIds():
                sizes = portal_properties.imaging_properties.getProperty('allowed_sizes')
                for pair in sizes:
                    term = SimpleTerm(value=format_size(pair), token=format_size(pair), title=pair)
                    size_terms[format_size(pair)] = term
            sizes = queryUtility(IAvailableSizes)()
            for size in sizes:
                if size not in size_terms:
                    size_terms[size] = SimpleTerm(value=size, token=size, title=size)


        return SimpleVocabulary(size_terms.values())
        
        
def ThumbVocabulary(context):
        return SizeVocabulary(context)
    

class GallerySearchableTextSource(SearchableTextSource):

    def search(self, query_string):
        results = super(GallerySearchableTextSource, self).search(query_string)
        utils = getToolByName(self.context, 'plone_utils')
        query = self.base_query.copy()
        if query_string == '':
            if self.default_query is not None:
                query.update(parse_query(self.default_query, self.portal_path))
        else:
            query.update(parse_query(query_string, self.portal_path))
        try:
            results = self.catalog(**query)
        except:
            results = []

        utils = getToolByName(self.context, 'plone_utils')
        for result in results:
            try:
                if utils.browserDefault(result.getObject())[1][0] ==\
                                                        "galleryview":
                    yield result.getPath()[len(self.portal_path):]
            except:
                pass


class GallerySearchabelTextSourceBinder(SearchableTextSourceBinder):

    def __init__(self):
        self.query = {'object_provides': IGallery.__identifier__}
        self.default_query = 'path:'

    def __call__(self, context):
        return GallerySearchableTextSource(
            context,
            base_query=self.query.copy(),
            default_query=self.default_query
        )
