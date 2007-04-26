# Author: Kun Xi <kunxi@kunxi.org>
# License: Python Software Foundation License

"""
A Python wrapper to access Amazon Web Service(AWS) E-Commerce Serive APIs,
based upon pyamazon (http://www.josephson.org/projects/pyamazon/), enhanced
to meet the latest AWS specification(http://www.amazon.com/webservices).

This module defines the following classes:

- `Bag`, a generic container for the python objects
- `listIterator`, a derived class of list
- `pagedIterator`, a page-based iterator using lazy evaluation

Exception classes:

- `AWSException`
- `NoLicenseKey`
- `BadLocale`
- `BadOption`
- `ExactParameterRequirement`
- `ExceededMaximumParameterValues`
- `InsufficientParameterValues`
- `InternalError`
- `InvalidEnumeratedParameter`
- `InvalidISO8601Time`
- `InvalidOperationForMarketplace`
- `InvalidOperationParameter`
- `InvalidParameterCombination`
- `InvalidParameterValue`
- `InvalidResponseGroup`
- `InvalidServiceParameter`
- `InvalidSubscriptionId`
- `InvalidXSLTAddress`
- `MaximumParameterRequirement`
- `MinimumParameterRequirement`
- `MissingOperationParameter`
- `MissingParameterCombination`
- `MissingParameters`
- `MissingParameterValueCombination`
- `MissingServiceParameter`
- `ParameterOutOfRange`
- `ParameterRepeatedInRequest`
- `RestrictedParameterValueCombination`
- `XSLTTransformationError`

Functions:

- `setLocale`
- `getLocale`
- `setLicenseKey`
- `getLicenseKey`
- `getVersion`
- `setOptions` 
- `getOptions`
- `buildRequest`
- `buildException`
- `query`
- `rawObject`
- `rawIterator`
- `unmarshal`
- `ItemLookup`
- `XMLItemLookup`
- `ItemSearch`
- `XMLItemSearch`
- `SimilarityLookup`
- `XMLSimilarityLookup`
- `ListLookup`
- `XMLListLookup`
- `ListSearch`
- `XMLListSearch`
- `CartCreate`
- `XMLCartCreate`
- `CartAdd`
- `XMLCartAdd`
- `CartGet`
- `XMLCartGet`
- `CartModify`
- `XMLCartModify`
- `CartClear`
- `XMLCartClear`
- `SellerLookup`
- `XMLSellerLookup`
- `SellerListingLookup`
- `XMLSellerListingLookup`
- `SellerListingSearch`
- `XMLSellerListingSearch`
- `CustomerContentSearch`
- `XMLCustomerContentSearch`
- `CustomerContentLookup`
- `XMLCustomerContentLookup`
- `BrowseNodeLookup`
- `XMLBrowseNodeLookup`
- `Help`
- `XMLHelp`
- `TransactionLookup`
- `XMLTransactionLookup`

Accroding to the ECS specification, there are two implementation foo and XMLfoo, for example, `ItemLookup` and `XMLItemLookup`. foo returns a Python object, XMLfoo returns the raw XML file.

How To Use This Module
======================
(See the individual classes, methods, and attributes for details.)

1. Apply for a Amazon Web Service API key from Amazon Web Service:
   https://aws-portal.amazon.com/gp/aws/developer/registration/index.html

2. Import it: ``import pyaws.ecs``

3. Setup the license key: ``ecs.setLicenseKey('YOUR-KEY-FROM-AWS')``
   or you could use the environment variable AMAZON_LICENSE_KEY

   Optional: 
   a) setup other options, like AssociateTag, MerchantID, Validate
   b) export the http_proxy environment variable if you want to use proxy
   c) setup the locale if your locale is not ``us``

4. Send query to the AWS, and manupilate the returned python object.
"""

__author__ = "Kun Xi < kunxi@kunxi.org >"
__version__ = "0.2.0"
__license__ = "Python Software Foundation"
__docformat__ = 'restructuredtext'


import os, urllib, string
from xml.dom import minidom


# Package-wide variables:
LICENSE_KEY = None;
LOCALE = "us"
VERSION = "2007-04-04"
OPTIONS = {}


__supportedLocales = {
		None : "ecs.amazonaws.com",  
		"us" : "ecs.amazonaws.com",  
		"uk" : "ecs.amazonaws.co.uk", 
		"de" : "ecs.amazonaws.co.de", 
		"jp" : "ecs.amazonaws.co.jp", 
		"fr" : "ecs.amazonaws.co.fr", 
		"ca" : "ecs.amazonaws.co.ca", 
	}

__licenseKeys = (
	(lambda key: key),
	(lambda key: LICENSE_KEY), 
	(lambda key: os.environ.get('AWS_LICENSE_KEY', None))
   )



def __buildPlugins():
	"""
	Build plugins used in unmarshal
	Return the dict like:
	Operation => { 'isByPassed'=>(...), 'isPivoted'=>(...), 
		'isCollective'=>(...), 'isCollected'=>(...) }  
	"""

	"""
	ResponseGroup and corresponding plugins:
	ResponseGroup=>(isBypassed, isPivoted, isCollective, isCollected)
	"""
	rgps = {
		'Accessories': ((), (), (), ()), 
		'AlternateVersions': ((), (), (), ()), 
		'BrowseNodeInfo': ((), (), ('Children', 'Ancestors'), ('BrowseNode',)),
		'BrowseNodes': ((), (), (), ()),
		'Cart': ((), (), (), ()),
		'CartNewReleases': ((), (), (), ()),
		'CartTopSellers': ((), (), (), ()),
		'CartSimilarities': ((), (), (), ()),
		'Collections': ((), (), (), ()),
		'CustomerFull': ((), (), (), ()),
		'CustomerInfo': ((), (), ('Customers',), ('Customer',)),
		'CustomerLists': ((), (), (), ()),
		'CustomerReviews': ((), (), (), ()),
		'EditorialReview': ((), (), (), ()),
		'Help': ((), (), ('RequiredParameters', 'AvailableParameters',
			'DefaultResponseGroups', 'AvailableResponseGroups'),
			 ('Parameter', 'ResponseGroup')),
		'Images': ((), (), (), ()),
		'ItemAttributes': ((), (), (), ()),
		'ItemIds': ((), (), (), ()),
		'Large': ((), (), (), ()),
		'ListFull': ((), (), (), ()),
		'ListInfo': ((), (), (), ()),
		'ListItems': ((), (), (), ()),
		'ListManiaLists': ((), (), (), ()),
		'ListMinimum': ((), (), (), ()),
		'Medium': ((), (), (), ()),
		'MerchantItemAttributes': ((), (), (), ()),
		'NewReleases': ((), (), ('NewReleases',), ('NewRelease',)),
		'OfferFull': ((), (), (), ()),
		'OfferListings': ((), (), (), ()),
		'Offers': ((), (), (), ()),
		'OfferSummary': ((), (), (), ()),
		'Request': (('Request',), (), (), ()),
		'Reviews': ((), (), (), ()),
		'SalesRank': ((), (), (), ()),
		'SearchBins': ((), (), (), ()),
		'Seller': ((), (), (), ()),
		'SellerListing': ((), (), (), ()),
		'Similarities': ((), (), (), ()),
		'Small': ((), (), (), ()),
		'Subjects': ((), (), (), ()),
		'TopSellers': ((), (), ('TopSellers',), ('TopSeller',)),
		'Tracks': ((), (), (), ()),
		'TransactionDetails': ((), (), ('Transactions', 'TransactionItems', 'Shipments'),
			('Transaction', 'TransactionItem', 'Shipment')),
		'VariationMinimum': ((), (), (), ()),
		'Variations': ((), (), (), ()),
		'VariationImages': ((), (), (), ()),
		'VariationSummary':((), (), (), ()) 
	}
	
	"""
	Operation=>ResponseGroups 
	"""
	orgs = {
		'BrowseNodeLookup': ('Request', 'BrowseNodeInfo', 'NewReleases', 'TopSellers'),
		'CartAdd': ('Cart', 'Request', 'CartSimilarities', 'CartTopSellers', 'NewReleases'),
		'CartClear': ('Cart', 'Request'),
		'CartCreate': ('Cart', 'Request', 'CartSimilarities', 'CartTopSellers', 'CartNewReleases'),
		'CartGet': ('Cart', 'Request', 'CartSimilarities', 'CartTopSellers', 'CartNewReleases'),
		'CartModify': ('Cart', 'Request', 'CartSimilarities', 'CartTopSellers', 'CartNewReleases'),
		'CustomerContentLookup': ('Request', 'CustomerInfo', 'CustomerReviews', 'CustomerLists', 'CustomerFull'),
		'CustomerContentSearch': ('Request', 'CustomerInfo'),
		'Help': ('Request', 'Help'),
		'ItemLookup': ('Request', 'Small', 'Accessories', 'BrowseNodes', 'EditorialReview', 'Images', 'ItemAttributes', 'ItemIds', 'Large', 'ListManiaLists', 'Medium', 'MerchantItemAttributes', 'OfferFull', 'Offers', 'OfferSummary', 'Reviews', 'SalesRank', 'Similarities', 'Subjects', 'Tracks', 'VariationImages', 'VariationMinimum', 'Variations', 'VariationSummary'),
		'ItemSearch': ('Request', 'Small', 'Accessories', 'BrowseNodes', 'EditorialReview', 'ItemAttributes', 'ItemIds', 'Large', 'ListManiaLists', 'Medium', 'MerchantItemAttributes', 'OfferFull', 'Offers', 'OfferSummary', 'Reviews', 'SalesRank', 'SearchBins', 'Similarities', 'Subjects', 'Tracks', 'VariationMinimum', 'Variations', 'VariationSummary'),
		'ListLookup': ('Request', 'ListInfo', 'Accessories', 'BrowseNodes', 'EditorialReview', 'Images', 'ItemAttributes', 'ItemIds', 'Large', 'ListFull', 'ListItems', 'ListManiaLists', 'Medium', 'Offers', 'OfferSummary', 'Reviews', 'SalesRank', 'Similarities', 'Subjects', 'Tracks', 'VariationMinimum', 'Variations', 'VariationSummary'),
		'ListSearch': ('Request', 'ListInfo', 'ListMinimum'),
		'SellerListingLookup': ('Request', 'SellerListing'),
		'SellerListingSearch': ('Request', 'SellerListing'),
		'SellerLookup': ('Request', 'Seller'),
		'SimilarityLookup': ('Request', 'Small', 'Accessories', 'BrowseNodes', 'EditorialReview', 'Images', 'ItemAttributes', 'ItemIds', 'Large', 'ListManiaLists', 'Medium', 'Offers', 'OfferSummary', 'Reviews', 'SalesRank', 'Similarities', 'Tracks', 'VariationMinimum', 'Variations', 'VariationSummary'),
		'TransactionLookup':('Request', 'TransactionDetails') 
	}

	def mergePlugins(responseGroups, index):
		#return reduce(lambda x, y: x.update(set(rgps[y][index])), responseGroups, set()) 
		# this magic reduce does not work, using the primary implementation first.
		s = set()
		for x in responseGroups:
			s.update(set(rgps[x][index]))
		return s
			
	def unionPlugins(responseGroups):
		return dict( [ (key, mergePlugins(responseGroups, index)) for index, key in enumerate(['isBypassed', 'isPivoted', 'isCollective', 'isCollected']) ])

	return dict( [ (k, unionPlugins(v)) for k, v in orgs.items() ] )
	

__plugins = __buildPlugins()

# Wrapper class for ECS
class Bag : 
	"""A generic container for the python objects"""
	def __repr__(self):
		return '<Bag instance: ' + self.__dict__.__repr__() + '>'


def rawObject(XMLSearch, arguments, kwItem, plugins=None):
	"""Return simple object from `unmarshal`"""
	dom = XMLSearch(** arguments)
	return unmarshal(dom.getElementsByTagName(kwItem).item(0), plugins) 


def rawIterator(XMLSearch, arguments, kwItems, plugins=None):
	"""Return list of objects from `unmarshal`"""
	dom = XMLSearch(** arguments)
	return unmarshal(dom.getElementsByTagName(kwItems).item(0), plugins, listIterator())


class listIterator(list):
	"""List with extended attributes"""
	pass

	
class pagedIterator:
	"""
	A page-based iterator using lazy evaluation.
	In some service, such as ItemSearch, AWS returns the result based on
	pages, the pagedIterator keeps track of the current page, and send
	the request only if necessary.

	Bugs: 

	- list slicing is still missing.
	"""

	def __init__(self, XMLSearch, arguments, kwPage, kwItems, plugins=None, pageSize=10):
		"""
		Initialize a `pagedIterator` object.
		Parameters:

		- `XMLSearch`: a function, the query to get the DOM
		- `arguments`: a dictionary, `XMLSearch`'s arguments
		- `kwPage`: a string, tag name of page
		- `kwItems`: a string, tag name of items
		- `plugins`: a dictionary, collection of plugged objects
		- `pageSize`: an integer, the amount of items in the page
	
		"""
		self.__search = XMLSearch 
		self.__arguments = arguments 
		self.__keywords ={'Page':kwPage, 'Items':kwItems} 
		self.__plugins = plugins
		self.__page = arguments[kwPage] or 1
		"""Current page"""
		self.__index = 0
		"""Current index"""
		self.__pageSize = pageSize

		dom = self.__search(** self.__arguments)
		self.__items = unmarshal(dom.getElementsByTagName(kwItems).item(0), plugins, listIterator())
		"""Cached items"""
		try:
			self.__len = int(dom.getElementsByTagName("TotalResults").item(0).firstChild.data)
		except AttributeError, e:
			self.__len = len(self.__items)

	def __len__(self):
		return self.__len

	def __iter__(self):
		return self

	def next(self):
		if self.__index < self.__len:
			self.__index = self.__index + 1
			return self.__getitem__(self.__index-1)
		else:
			raise StopIteration

	def __getitem__(self, key):
		num = int(key)
		if num >= self.__len:
			raise IndexError

		page = num / self.__pageSize + 1
		index = num % self.__pageSize
		if page != self.__page:
			self.__arguments[self.__keywords['Page']] = page
			dom = self.__search(** self.__arguments)
			self.__items = unmarshal(dom.getElementsByTagName(self.__keywords['Items']).item(0), self.__plugins, listIterator())
			self.__page = page

		return self.__items[index]


# Exception classes
class AWSException(Exception) : pass
class NoLicenseKey(AWSException) : pass
class BadLocale(AWSException) : pass
class BadOption(AWSException): pass
# Runtime exception
class ExactParameterRequirement(AWSException): pass
class ExceededMaximumParameterValues(AWSException): pass
class InsufficientParameterValues(AWSException): pass
class InternalError(AWSException): pass
class InvalidEnumeratedParameter(AWSException): pass
class InvalidISO8601Time(AWSException): pass
class InvalidOperationForMarketplace(AWSException): pass
class InvalidOperationParameter(AWSException): pass
class InvalidParameterCombination(AWSException): pass
class InvalidParameterValue(AWSException): pass
class InvalidResponseGroup(AWSException): pass
class InvalidServiceParameter(AWSException): pass
class InvalidSubscriptionId(AWSException): pass
class InvalidXSLTAddress(AWSException): pass
class MaximumParameterRequirement(AWSException): pass
class MinimumParameterRequirement(AWSException): pass
class MissingOperationParameter(AWSException): pass
class MissingParameterCombination(AWSException): pass
class MissingParameters(AWSException): pass
class MissingParameterValueCombination(AWSException): pass
class MissingServiceParameter(AWSException): pass
class ParameterOutOfRange(AWSException): pass
class ParameterRepeatedInRequest(AWSException): pass
class RestrictedParameterValueCombination(AWSException): pass
class XSLTTransformationError(AWSException): pass


# Utilities functions
def setLocale(locale):
	"""Set the locale
	if unsupported locale is set, BadLocale is raised."""
	global LOCALE
	if not __supportedLocales.has_key(locale):
		raise BadLocale, ("Unsupported locale. Locale must be one of: %s" %
			', '.join([x for x in __supportedLocales.keys() if x]))
	LOCALE = locale


def getLocale():
	"""Get the locale"""
	return LOCALE


def setLicenseKey(license_key=None):
	"""Set AWS license key.
	If license_key is not specified, the license key is set using the
	environment variable: AMAZON_LICENSE_KEY; if no license key is 
	set, NoLicenseKey exception is raised."""
	
	global LICENSE_KEY
	for get in __licenseKeys:
		rc = get(license_key)
		if rc: 
			LICENSE_KEY = rc;
			return;
	raise NoLicenseKey, ("Please get the license key from  http://www.amazon.com/webservices")


def getLicenseKey():
	"""Get license key.
	If no license key is specified,  NoLicenseKey is raised."""

	if not LICENSE_KEY:
		setLicenseKey()
	return LICENSE_KEY


def getVersion():
	"""Get the version of ECS specification"""
	return VERSION
	

def setOptions(options):
	"""
	Set the general optional parameter, available options are:
	- AssociateTag
	- MerchantID
	- Version
	- Validate
	"""
	
	if set(options.keys()).issubset( set(['AssociateTag', 'MerchantID', 'Validate']) ):
		global OPTIONS
		OPTIONS.update(options)
	else:
		raise BadOption, ('Unsupported option')

		
def getOptions():
	"""Get options"""
	return OPTIONS 


def buildRequest(argv):
	"""Build the REST request URL from argv."""

	url = "http://" + __supportedLocales[getLocale()] + "/onca/xml?Service=AWSECommerceService&" + 'Version=%s&' % VERSION
	if not argv['AWSAccessKeyId']:
		argv['AWSAccessKeyId'] = getLicenseKey()
	argv.update(getOptions())
	return url + '&'.join(['%s=%s' % (k,urllib.quote(str(v))) for (k,v) in argv.items() if v]) 


def buildException(els):
	"""Build the exception from the returned DOM node
	Note: only the first exception is raised."""

	error = els[0]
	class_name = error.childNodes[0].firstChild.data[4:]
	msg = error.childNodes[1].firstChild.data 

	e = globals()[ class_name ](msg)
	return e


def query(url):
	"""Send the query url and return the DOM
	Exception is raised if there are errors"""
	u = urllib.FancyURLopener()
	usock = u.open(url)
	dom = minidom.parse(usock)
	usock.close()

	errors = dom.getElementsByTagName('Error')
	if errors:
		e = buildException(errors)
		raise e
	return dom


def unmarshal(element, plugins=None, rc=None):
	"""Return the `Bag` / `listIterator` object with attributes 
	populated using DOM element.
	
	Parameters:

	- `element`: DOM object, the DOM element interested in
	- `plugins`: a dictionary, collection of plugged objects to fine-tune
	  the object attributes
	- `rc`: Bag object, parent object

	This core function is inspired by Mark Pilgrim (f8dy@diveintomark.org)
	with some enhancement. Each node.tagName is evalued by plugins' callback
	functions:
		
	- if tagname in plugins['isBypassed']
	    this elment is ignored
	- if tagname in plugins['isPivoted'] 
	    this children of this elment is moved to grandparents
	    this object is ignored.
	- if tagname in plugins['isCollective'] 
	    this elment is mapped to []
	- if tagname in plugins['isCollected'] 
	    this children of elment is appended to grandparent
	    this object is ignored.
	"""

	if(rc == None):
		rc = Bag()

	childElements = [e for e in element.childNodes if isinstance(e, minidom.Element)]

	if childElements:
		for child in childElements:
			key = child.tagName
			if hasattr(rc, key):
				if type(getattr(rc, key)) <> type([]):
					setattr(rc, key, [getattr(rc, key)])
				setattr(rc, key, getattr(rc, key) + [unmarshal(child, plugins)])
			elif isinstance(child, minidom.Element):
				if child.tagName in plugins['isPivoted']:
					unmarshal(child, plugins, rc)
				elif child.tagName in plugins['isBypassed']:
					continue
				elif child.tagName in plugins['isCollective']:
					setattr(rc, key, unmarshal(child, plugins, listIterator([])))
				elif child.tagName in plugins['isCollected']:
					rc.append(unmarshal(child, plugins))
				else:
					setattr(rc, key, unmarshal(child, plugins))
	else:
		rc = "".join([e.data for e in element.childNodes if isinstance(e, minidom.Text)])
	return rc


	
# User interfaces

def ItemLookup(ItemId, IdType=None, SearchIndex=None, MerchantId=None, Condition=None, DeliveryMethod=None, ISPUPostalCode=None, OfferPage=None, ReviewPage=None, ReviewSort=None, VariationPage=None, ResponseGroup=None, AWSAccessKeyId=None): 
	'''ItemLookup in ECS'''
	argv = vars()
	plugins = {
		'isBypassed': ('Request',), 
		'isPivoted': ('ItemAttributes',),
		'isCollective': ('Items',), 
		'isCollected': ('Item',)
	}
	return pagedIterator(XMLItemLookup, argv, 'OfferPage', 'Items', plugins)

	
def XMLItemLookup(ItemId, IdType=None, SearchIndex=None, MerchantId=None, Condition=None, DeliveryMethod=None, ISPUPostalCode=None, OfferPage=None, ReviewPage=None, ReviewSort=None, VariationPage=None, ResponseGroup=None, AWSAccessKeyId=None): 
	'''DOM representation of ItemLookup in ECS'''

	Operation = "ItemLookup"
	return query(buildRequest(vars()))


def ItemSearch(Keywords, SearchIndex="Blended", Availability=None, Title=None, Power=None, BrowseNode=None, Artist=None, Author=None, Actor=None, Director=None, AudienceRating=None, Manufacturer=None, MusicLabel=None, Composer=None, Publisher=None, Brand=None, Conductor=None, Orchestra=None, TextStream=None, ItemPage=None, Sort=None, City=None, Cuisine=None, Neighborhood=None, MinimumPrice=None, MaximumPrice=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None):  
	'''ItemSearch in ECS'''

	argv = vars()
	plugins = {
		'isBypassed': (), 
		'isPivoted': ('ItemAttributes',),
		'isCollective': ('Items',), 
		'isCollected': ('Item',)
	}
	return pagedIterator(XMLItemSearch, argv, "ItemPage", 'Items', plugins)


def XMLItemSearch(Keywords, SearchIndex="Blended", Availability=None, Title=None, Power=None, BrowseNode=None, Artist=None, Author=None, Actor=None, Director=None, AudienceRating=None, Manufacturer=None, MusicLabel=None, Composer=None, Publisher=None, Brand=None, Conductor=None, Orchestra=None, TextStream=None, ItemPage=None, Sort=None, City=None, Cuisine=None, Neighborhood=None, MinimumPrice=None, MaximumPrice=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None):  
	'''DOM representation of ItemSearch in ECS'''

	Operation = "ItemSearch"
	return query(buildRequest(vars()))


def SimilarityLookup(ItemId, SimilarityType=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None):  
	'''SimilarityLookup in ECS'''

	argv = vars()
	plugins = {
		'isBypassed': (), 
		'isPivoted': ('ItemAttributes',),
		'isCollective': ('Items',),
		'isCollected': ('Item',)
	}
	return rawIterator(XMLSimilarityLookup, argv, 'Items', plugins)


def XMLSimilarityLookup(ItemId, SimilarityType=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None):  
	'''DOM representation of SimilarityLookup in ECS'''

	Operation = "SimilarityLookup"
	return query(buildRequest(vars()))


# List Operations

def ListLookup(ListType, ListId, ProductPage=None, ProductGroup=None, Sort=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None):  
	'''ListLookup in ECS'''

	argv = vars()
	plugins = {
		'isBypassed': (), 
		'isPivoted': ('ItemAttributes',),
		'isCollective': ('Lists',), 
		'isCollected': ('List',)
	}
	return pagedIterator(XMLListLookup, argv, 'ProductPage', 'Lists', plugins)


def XMLListLookup(ListType, ListId, ProductPage=None, ProductGroup=None, Sort=None, MerchantId=None, Condition=None, DeliveryMethod=None, ResponseGroup=None, AWSAccessKeyId=None):  
	'''DOM representation of ListLookup in ECS'''

	Operation = "ListLookup"
	return query(buildRequest(vars()))


def ListSearch(ListType, Name=None, FirstName=None, LastName=None, Email=None, City=None, State=None, ListPage=None, ResponseGroup=None, AWSAccessKeyId=None):
	'''ListSearch in ECS'''

	argv = vars()
	plugins = {
		'isBypassed': (), 
		'isPivoted': ('ItemAttributes',),
		'isCollective': ('Lists',), 
		'isCollected': ('List',)
	}
	return pagedIterator(XMLListSearch, argv, 'ListPage', 'Lists', plugins)


def XMLListSearch(ListType, Name=None, FirstName=None, LastName=None, Email=None, City=None, State=None, ListPage=None, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of ListSearch in ECS'''

	Operation = "ListSearch"
	return query(buildRequest(vars()))


#Remote Shopping Cart Operations
def CartCreate(Items, Quantities, ResponseGroup=None, AWSAccessKeyId=None):
	'''CartCreate in ECS'''

	return __cartOperation(XMLCartCreate, vars())


def XMLCartCreate(Items, Quantities, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of CartCreate in ECS'''

	Operation = "CartCreate"
	argv = vars()
	for x in ('Items', 'Quantities'):
		del argv[x]

	__fromListToItems(argv, Items, 'ASIN', Quantities)
	return query(buildRequest(argv))


def CartAdd(Cart, Items, Quantities, ResponseGroup=None, AWSAccessKeyId=None):
	'''CartAdd in ECS'''

	return __cartOperation(XMLCartAdd, vars())


def XMLCartAdd(Cart, Items, Quantities, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of CartAdd in ECS'''

	Operation = "CartAdd"
	CartId = Cart.CartId
	HMAC = Cart.HMAC
	argv = vars()
	for x in ('Items', 'Cart', 'Quantities'):
		del argv[x]

	__fromListToItems(argv, Items, 'ASIN', Quantities)
	return query(buildRequest(argv))


def CartGet(Cart, ResponseGroup=None, AWSAccessKeyId=None):
	'''CartGet in ECS'''
	return __cartOperation(XMLCartGet, vars())


def XMLCartGet(Cart, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of CartGet in ECS'''

	Operation = "CartGet"
	CartId = Cart.CartId
	HMAC = Cart.HMAC
	argv = vars()
	del argv['Cart']
	return query(buildRequest(argv))


def CartModify(Cart, Items, Actions, ResponseGroup=None, AWSAccessKeyId=None):
	'''CartModify in ECS'''

	return __cartOperation(XMLCartModify, vars())


def XMLCartModify(Cart, Items, Actions, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of CartModify in ECS'''
	Operation = "CartModify"
	CartId = Cart.CartId
	HMAC = Cart.HMAC
	argv = vars()
	for x in ('Cart', 'Items', 'Actions'):
		del argv[x]

	__fromListToItems(argv, Items, 'CartItemId', Actions)
	return query(buildRequest(argv))

	
def CartClear(Cart, ResponseGroup=None, AWSAccessKeyId=None):
	'''CartClear in ECS'''
	return __cartOperation(XMLCartClear, vars())


def XMLCartClear(Cart, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of CartClear in ECS'''

	Operation = "CartClear"
	CartId = Cart.CartId
	HMAC = Cart.HMAC
	argv = vars()
	del argv['Cart']

	return query(buildRequest(argv))


def __fromListToItems(argv, items, id, actions):
	'''Convert list to AWS REST arguments'''

	for i in range(len(items)):
		argv["Item.%d.%s" % (i+1, id)] = getattr(items[i], id);
		action = actions[i]
		if isinstance(action, int):
			argv["Item.%d.Quantity" % (i+1)] = action
		else:
			argv["Item.%d.Action" % (i+1)] = action


def __cartOperation(XMLSearch, arguments):
	'''Generic cart operation'''

	plugins = {
		'isBypassed': ('Request',),
		'isPivoted': (), 
		'isCollective': ('CartItems', 'SavedForLaterItems'),
		'isCollected': ('CartItem', 'SavedForLaterItem') 
	}
	return rawObject(XMLSearch, arguments, 'Cart', plugins)


# Seller Operation
def SellerLookup(Sellers, FeedbackPage=None, ResponseGroup=None, AWSAccessKeyId=None):
	'''SellerLookup in AWS'''

	argv = vars()
	plugins = {
		'isBypassed': ('Request',),
		'isPivoted': (), 
		'isCollective': ('Sellers',),
		'isCollected': ('Seller',)
	}
	return rawIterator(XMLSellerLookup, argv, 'Sellers', plugins)


def XMLSellerLookup(Sellers, FeedbackPage=None, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of SellerLookup in AWS'''

	Operation = "SellerLookup"
	SellerId = ",".join(Sellers)
	argv = vars()
	del argv['Sellers']
	return query(buildRequest(argv))


def SellerListingLookup(SellerId, Id, IdType="Listing", ResponseGroup=None, AWSAccessKeyId=None):
	'''SellerListingLookup in AWS

	Notice: although the repsonse includes TotalPage, TotalResults, 
	there is no ListingPage in the request, so we have to use rawIterator
	instead of pagedIterator. Hope Amazaon would fix this inconsistance'''
	
	argv = vars()
	plugins = {
		'isBypassed': ('Request',),
		'isPivoted': (), 
		'isCollective': ('SellerListings',), 
		'isCollected': ('SellerListing',)
	}
	return rawIterator(XMLSellerListingLookup, argv, "SellerListings", plugins)


def XMLSellerListingLookup(SellerId, Id, IdType="Listing", ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of SellerListingLookup in AWS'''

	Operation = "SellerListingLookup"
	return query(buildRequest(vars()))


def SellerListingSearch(SellerId, Title=None, Sort=None, ListingPage=None, OfferStatus=None, ResponseGroup=None, AWSAccessKeyId=None):
	'''SellerListingSearch in AWS'''

	argv = vars()
	plugins = {
		'isBypassed': ('Request',),
		'isPivoted': (), 
		'isCollective': ('SellerListings',), 
		'isCollected': ('SellerListing',)
	}
	return pagedIterator(XMLSellerListingSearch, argv, "ListingPage", "SellerListings", plugins)


def XMLSellerListingSearch(SellerId, Title=None, Sort=None, ListingPage=None, OfferStatus=None, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of SellerListingSearch in AWS'''

	Operation = "SellerListingSearch"
	return query(buildRequest(vars()))


def CustomerContentSearch(Name=None, Email=None, CustomerPage=1, ResponseGroup=None, AWSAccessKeyId=None):
	'''CustomerContentSearch in AWS'''

	return rawIterator(XMLCustomerContentSearch, vars(), 'Customers', __plugins['CustomerContentSearch'])


def XMLCustomerContentSearch(Name=None, Email=None, CustomerPage=1, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of CustomerContentSearch in AWS'''

	Operation = "CustomerContentSearch"
	argv = vars()
	for x in ('Name', 'Email'):
		if not argv[x]:
			del argv[x]
	return query(buildRequest(argv))


def CustomerContentLookup(CustomerId, ReviewPage=1, ResponseGroup=None, AWSAccessKeyId=None):
	'''CustomerContentLookup in AWS'''

	argv = vars()
	plugins = {
		'isBypassed': ('Request',),
		'isPivoted': (), 
		'isCollective': ('Customers',),
		'isCollected': ('Customer',)
	}
	return rawIterator(XMLCustomerContentLookup, argv, 'Customers', plugins)


def XMLCustomerContentLookup(CustomerId, ReviewPage=1, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of CustomerContentLookup in AWS'''

	Operation = "CustomerContentLookup"
	return query(buildRequest(vars()))


# BrowseNode
def BrowseNodeLookup(BrowseNodeId, ResponseGroup=None, AWSAccessKeyId=None):
	"""
	BrowseNodeLookup in AWS 
	"""
	return rawIterator(XMLBrowseNodeLookup, vars(), 'BrowseNodes', __plugins['BrowseNodeLookup'])


def XMLBrowseNodeLookup(BrowseNodeId, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of BrowseNodeLookup in AWS'''
	
	Operation = "BrowseNodeLookup"
	return query(buildRequest(vars()))


# Help
def Help(HelpType, About, ResponseGroup=None, AWSAccessKeyId=None):
	'''Help in AWS'''
	return rawObject(XMLHelp, vars(), 'Information', __plugins['Help'])


def XMLHelp(HelpType, About, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of Help in AWS'''

	Operation = "Help"
	return query(buildRequest(vars()))


# Transaction
def TransactionLookup(TransactionId, ResponseGroup=None, AWSAccessKeyId=None):
	'''TransactionLookup in AWS'''
	return rawIterator(XMLTransactionLookup, vars(), 'Transactions', __plugins['TransactionLookup'])
	

def XMLTransactionLookup(TransactionId, ResponseGroup=None, AWSAccessKeyId=None):
	'''DOM representation of TransactionLookup in AWS'''

	Operation = "TransactionLookup"
	return query(buildRequest(vars()))



if __name__ == "__main__" :
	import pdb
	setLicenseKey("1MGVS72Y8JF7EC7JDZG2")
	obj = BrowseNodeLookup("1065852", ResponseGroup='NewReleases,BrowseNodeInfo,TopSellers')
	print obj
	
	s = XMLCustomerContentSearch('Sam', None, 20, ResponseGroup='CustomerInfo')
	print s.toprettyxml()
