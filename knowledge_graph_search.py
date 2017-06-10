import json
import logging
import urllib

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }
    
def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None
        
def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }        

def debkg(intent_request):
    """
    Performs dialog management and fulfillment for knowledge graph search.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    logger.debug('debkg intent_request={}'.format(intent_request))
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    # -- who
    author = try_ex(lambda: intent_request['currentIntent']['slots']['Author'])
    artist = try_ex(lambda: intent_request['currentIntent']['slots']['Artist'])
    athelete = try_ex(lambda: intent_request['currentIntent']['slots']['Athelete'])
    person = try_ex(lambda: intent_request['currentIntent']['slots']['person'])
    actor = try_ex(lambda: intent_request['currentIntent']['slots']['Actor'])
    
    # -- where
    city = try_ex(lambda: intent_request['currentIntent']['slots']['City'])
    region = try_ex(lambda: intent_request['currentIntent']['slots']['Region'])
    dessert = try_ex(lambda: intent_request['currentIntent']['slots']['Dessert'])
    country = try_ex(lambda: intent_request['currentIntent']['slots']['Country'])
    europecity = try_ex(lambda: intent_request['currentIntent']['slots']['EuropeCity'])
    
    # -- tell me about
    language = try_ex(lambda: intent_request['currentIntent']['slots']['Language'])
    
    # -- What 
    festival = try_ex(lambda: intent_request['currentIntent']['slots']['Festival'])
    
    query = ""
    word = ""
    if author:
        word = "who"
        query = author

    if artist:
        word = "who"
        query = artist
    
    if athelete:
        word = "who"
        query = athelete
        
    if person:
        word = "who"
        query = person    

    if actor:
        word = "who"
        query = actor 
        
    if city:
        word = "where"
        query = city
        
    if region is not None:
        word = "where"
        query = region    
   
    if dessert:
        word = "where"
        query = dessert    
        
    if country:
        word = "where"
        query = country    
        
    if festival:
        word = "what"
        query = festival


    
    # Booking the hotel.  In a real application, this would likely involve a call to a backend service.
    logger.debug('debkg query={}'.format(query))

    if query:
        service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        params = {
          'query': query,
          'limit': 10,
          'indent': False,
          'key': '<google knowledge graph api key>',
        }
    
        url = service_url + '?' + urllib.urlencode(params)
        response = json.loads(urllib.urlopen(url).read())
        found = False
        result = ""
        for element in response['itemListElement']:
          found = True
          if 'detailedDescription' in element['result'] and 'articleBody' in element['result']['detailedDescription']:
              result += element['result']['detailedDescription']['articleBody'] + ' '
        if not found:
            result =  query + ' not found'
    else:
        logger.debug('debkg not able to retrieve query')

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': result
        }
    )

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name =='kg' or intent_name =='debkg':
        return debkg(intent_request)
   
    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
