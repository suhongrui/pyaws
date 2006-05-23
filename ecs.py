"""Python wrapper for AWS E-Commerce Serive APIs.

Based upon pyamazon ( http://www.josephson.org/projects/pyamazon/ ) with 
efforts to meet the latest AWS specification.

The Amazon's web APIs specication is described here:
  http://www.amazon.com/webservices

You need a Amazon-provided license key to use these services.
Follow the link above to get one.  These functions will look in
several places (in this order) for the license key:
- the "license_key" argument of each function
- the module-level LICENSE_KEY variable (call setLicense once to set it)
- an environment variable called AMAZON_LICENSE_KEY


TODO: 
  - Add more decriptions about this module. 
"""

import os, urllib, string, inspect
from xml.dom import minidom
import pdb

__author__ = "Kun Xi < kunxi@kunxi.org >"
__version__ = "0.0.1"
__license__ = "GPL"


# Package-wide variables:
LICENSE_KEY = None;
HTTP_PROXY = None
LOCALE = "us"
VERSION = "2005-10-05"

_supportedLocales = {
        "us" : (None, "webservices.amazon.com"),   
        "uk" : ("uk", "webservices.amazon.co.uk"),
        "de" : ("de", "webservices.amazon.de"),
        "jp" : ("jp", "webservices.amazon.co.jp"),
        "fr" : ("fr", "webservices.amazon.fr"),
        "ca" : ("ca", "webservices.amazon.ca" )
    }

_licenseKeys = (
    (lambda key: key ),
    (lambda key: LICENSE_KEY ), 
    (lambda key: os.environ.get('AWS_LICENSE_KEY', None))
    )

# Exception class
class AWSException( Exception ) : pass
class NoLicenseKey( AWSException ) : pass
class BadLocale( AWSException ) : pass
# Runtime exception
class ExactParameterRequirement( AWSException ): pass
class ExceededMaximumParameterValues( AWSException ): pass
class InsufficientParameterValues( AWSException ): pass
class InternalError( AWSException ): pass
class InvalidEnumeratedParameter( AWSException ): pass
class InvalidISO8601Time( AWSException ): pass
class InvalidOperationForMarketplace( AWSException ): pass
class InvalidOperationParameter( AWSException ): pass
class InvalidParameterCombination( AWSException ): pass
class InvalidParameterValue( AWSException ): pass
class InvalidResponseGroup( AWSException ): pass
class InvalidServiceParameter( AWSException ): pass
class InvalidSubscriptionId( AWSException ): pass
class InvalidXSLTAddress( AWSException ): pass
class MaximumParameterRequirement( AWSException ): pass
class MinimumParameterRequirement( AWSException ): pass
class MissingOperationParameter( AWSException ): pass
class MissingParameterCombination( AWSException ): pass
class MissingParameters( AWSException ): pass
class MissingParameterValueCombination( AWSException ): pass
class MissingServiceParameter( AWSException ): pass
class ParameterOutOfRange( AWSException ): pass
class ParameterRepeatedInRequest( AWSException ): pass
class RestrictedParameterValueCombination( AWSException ): pass
class XSLTTransformationError( AWSException ): pass

#TODO: ECommerceService.foo 


class Bag : pass


# Utilities functions

def _checkLocaleSupported(locale):
    if not _supportedLocales.has_key(locale):
        raise BadLocale, ("Unsupported locale. Locale must be one of: %s" %
            string.join(_supportedLocales, ", "))


def setLocale(locale):
    """set locale"""
    global LOCALE
    _checkLocaleSupported(locale)
    LOCALE = locale


def getLocale():
    """get locale"""
    return LOCALE


def setLicenseKey(license_key=None):
    """set license key

    license key can come from any number of locations;
    see module docs for search order"""

    global LICENSE_KEY
    for get in _licenseKeys:
        rc = get(license_key)
        if rc: 
            LICENSE_KEY = rc;
            return;
    raise NoLicenseKey, ("Please get the license key from  http://www.amazon.com/webservices" )


def getLicenseKey():
    """get license key"""
    if not LICENSE_KEY:
        raise NoLicenseKey, ("Please get the license key from  http://www.amazon.com/webservices" )
        
    return LICENSE_KEY
    

def getVersion():
    """get version"""
    return VERSION


def setVersion(version):
    global VERSION
    VERSION = version
    

def buildRequest( argv ):
    url = "http://" + _supportedLocales[LOCALE][1] + "/onca/xml?Service=AWSECommerceService"
    for k,v in argv.items():
        if v:
            url += '&%s=%s' % (k,v)

    print "url=", url
    return url;


def buildException( els ):
    # We just care the first error.
    error = els[0]
    class_name = error.childNodes[0].firstChild.data[4:]
    msg = error.childNodes[1].firstChild.data 

    e = globals()[ class_name ](msg)
    return e


# core functions
def query( url ):
    u = urllib.FancyURLopener( HTTP_PROXY )
    usock = u.open(url)
    dom = minidom.parse(usock)
    usock.close()

    errors = dom.getElementsByTagName('Error')
    if errors:
        e = buildException( errors )
        raise e
    
    return dom

class pagedIterator:
    def __init__(self, XMLSearch, arguments, Keyword):
        self.search = XMLSearch 
        self.arguments = arguments 
        self.keyword = Keyword
        self.page = arguments[Keyword] or 1
        self.index = 0
        dom = self.search( ** self.arguments )
        ( self.items, self.len ) = createObjects(dom)

    def __len__(self):
        return self.len

    def __iter__(self):
        return self

    def next(self):
        if self.index < self.len:
            self.index = self.index + 1
            return self.__getitem__(self.index-1)
        else:
            raise StopIteration

    def __getitem__(self, key):
        try:
            num = int(key)
        except TypeError, e:
            raise e

        if num >= self.len:
            raise IndexError

        page = num / 10 + 1
        index = num % 10
        if page != self.page:
            self.arguments[self.keyword] = page
            ( self.items, unused ) = createObjects( self.search ( **self.arguments ))
	    self.page = page

        return self.items[index]


def createObjects( dom ):
    items = unmarshal( dom.getElementsByTagName('Items' ).item(0)).Item
    if type(items) <> type([]):
        items = [items]
    try:
    	total = dom.getElementsByTagName("TotalResults").item(0).firstChild.data

    except AttributeError, e:
        total = len(items)
	
    return (items, total)

def unmarshal(element, rc=None):
    # this core function is implemented by Mark Pilgrim (f8dy@diveintomark.org)
    if(rc == None):
        rc = Bag()
    childElements = [e for e in element.childNodes if isinstance(e, minidom.Element)]

    if childElements:
        for child in childElements:
            key = child.tagName
            if hasattr(rc, key):
                if type(getattr(rc, key)) <> type([]):
                    setattr(rc, key, [getattr(rc, key)])
                setattr(rc, key, getattr(rc, key) + [unmarshal(child)])
            elif isinstance(child, minidom.Element) and (child.tagName == 'ItemAttributes') :
                unmarshal(child, rc)
            else:
                setattr(rc, key, unmarshal(child))
    else:
        rc = "".join([e.data for e in element.childNodes if isinstance(e, minidom.Text)])
    return rc

    
# User interfaces

# ItemOperation
def ItemLookup( ItemId, IdType=None, SearchIndex=None, MerchantId=None, Condition=None, DeliveryMethod=None, ISPUPostalCode=None, OfferPage=None, ReviewPage=None, VariationPage=None, ResponseGroup=None, AWSAccessKeyId=None ): 
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return pagedIterator( XMLItemLookup, argv, "OfferPage" )
    
def XMLItemLookup( ItemId, IdType=None, SearchIndex=None, MerchantId=None, Condition=None, DeliveryMethod=None, ISPUPostalCode=None, OfferPage=None, ReviewPage=None, VariationPage=None, ResponseGroup=None, AWSAccessKeyId=None ): 
    Operation = "ItemLookup"
    AWSAccessKeyId = AWSAccessKeyId or LICENSE_KEY
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return query( buildRequest(argv) )

def ItemSearch( Keywords, SearchIndex="Blended", Availability=None, Title=None, Power=None, BrowseNode=None, Artist=None, Author=None, Actor=None, Director=None, AudienceRating=None, Manufacturer=None, MusicLabel=None, Composer=None, Publisher=None, Brand=None, Conductor=None, Orchestra=None, TextStream=None, ItemPage=None, Sort=None, City=None, Cuisine=None, Neighborhood=None, MinimumPrice=None, MaximumPrice=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None ):  
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return pagedIterator( XMLItemSearch, argv, "ItemPage" )

def XMLItemSearch( Keywords, SearchIndex="Blended", Availability=None, Title=None, Power=None, BrowseNode=None, Artist=None, Author=None, Actor=None, Director=None, AudienceRating=None, Manufacturer=None, MusicLabel=None, Composer=None, Publisher=None, Brand=None, Conductor=None, Orchestra=None, TextStream=None, ItemPage=None, Sort=None, City=None, Cuisine=None, Neighborhood=None, MinimumPrice=None, MaximumPrice=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None ):  
    Operation = "ItemSearch"
    AWSAccessKeyId = AWSAccessKeyId or LICENSE_KEY
    Keywords = urllib.quote(Keywords)
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return query( buildRequest(argv) )

def SimilarityLookup( ItemId, SimilarityType=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None ):  
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return pagedIterator( XMLSimilarityLookup, argv, "OfferPage" )

def XMLSimilarityLookup( ItemId, SimilarityType=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None ):  
    Operation = "SimilarityLookup"
    AWSAccessKeyId = AWSAccessKeyId or LICENSE_KEY
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return query( buildRequest(argv) )

# ListOperation
def ListLookup( ListType, ListId, ProductPage=None, ProductGroup=None, Sort=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None ):  
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return pagedIterator( XMLListLookup, argv, "OfferPage" )

def XMLListLookup( ListType, ListId, ProductPage=None, ProductGroup=None, Sort=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None ):  
    Operation = "ListLookup"
    AWSAccessKeyId = AWSAccessKeyId or LICENSE_KEY
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return query( buildRequest(argv) )

def ListSearch( ListType, Name=None, FirstName=None, LastName=None, Email=None, City=None, State=None, ListPage=None, ResponseGroup=None, AWSAccessKeyId=None ):
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return pagedIterator( XMLListSearch, argv, "OfferPage" )

def XMLListSearch( ListType, Name=None, FirstName=None, LastName=None, Email=None, City=None, State=None, ListPage=None, ResponseGroup=None, AWSAccessKeyId=None ):
    Operation = "ListSearch"
    AWSAccessKeyId = AWSAccessKeyId or LICENSE_KEY
    argv = inspect.getargvalues( inspect.currentframe() )[-1]
    return query( buildRequest(argv) )

#Remote Shopping Cart Operations



if __name__ == "__main__" :
    setLicenseKey("1MGVS72Y8JF7EC7JDZG2")

#    books = ItemSearch("python", SearchIndex="Books")
#    for book in books:
#    	print book.Title

    books = ItemLookup( "0596009259" )
    for book in books:
        for att in dir(book):
            print '%s = %s' %( att, getattr(book, att) )
            
        
