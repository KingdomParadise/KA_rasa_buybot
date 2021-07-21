from os import link
from typing import Any, Text, Dict, List
from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from .api_handler import  VIN_VALIDATOR,LICENSE_PLATE_VALIDATOR
from .price_api import FETCH_PRICE
import re


#
class ActionMain(Action):
    def name(self) -> Text:
        return "action_main"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        buttons = [
                {"payload": "/accept_offer", "title": "Yes"},
                {"payload": "/deny_offer", "title": "No"},
            ] 
        

        message=tracker.latest_message['text']
        phone_numbers = re.findall(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]', message) 
        print(message)
        if message.lower()=='/accept_offer':
            if tracker.get_slot('interested_in_selling_car') is True and tracker.get_slot('interested_in_tentative_price') is not True:
                dispatcher.utter_message(text="Ok Great, I can give you a tentative price for your car write here if you are interested ?", buttons=buttons)
                return [SlotSet('interested_in_tentative_price',True)] 


            elif tracker.get_slot('interested_in_tentative_price') is True and tracker.get_slot('have_license_plate') is  not True:
                dispatcher.utter_message(text="Great, do you have your vin or license plate ?", buttons=buttons)
                return [SlotSet('have_license_plate',True)] 


            elif tracker.get_slot('have_license_plate') is True and tracker.get_slot('vehicle_owning_status') is not True:
                dispatcher.utter_message(text="Please provide your 17 digit VIN / License Plate Number")
                return [] 

            elif tracker.get_slot('vehicle_owning_status') is True and tracker.get_slot('have_miles') is not True:
                buttons = [
                    {"payload": "/accept_offer", "title": "Yes, i can give miles."},
                    {"payload": "/deny_offer", "title": "No, i don't have miles."},
                ] 
                dispatcher.utter_message(text="Ok Great, Can you please provide miles on the vehicle ?", buttons=buttons)
                return [SlotSet('have_miles',True)] 
           
            elif tracker.get_slot('have_miles') is True and tracker.get_slot('miles_value') is None:
                dispatcher.utter_message(text="Please enter the miles.")
                return [] 

            elif tracker.get_slot('miles_value')is not None  and tracker.get_slot('would_like_to_talk_in_detail') is not True :
                dispatcher.utter_message(text="Can you please provide your phone number?.",buttons=buttons)
                return [SlotSet('would_like_to_talk_in_detail',True)] 

            elif tracker.get_slot('would_like_to_talk_in_detail')is True  and tracker.get_slot('phone_number_value') is None :
                dispatcher.utter_message(text="Please Enter your phone number.")
                return [SlotSet('would_like_to_talk_in_detail',True)] 

                
             
        elif len(message)==17 and ' ' not in message and tracker.get_slot('vehicle_owning_status') is not  True:
            print('--> Received VIN VALUE')
            response = VIN_VALIDATOR(message)
            if response is not  None: 
                dispatcher.utter_message(text=response)
                dispatcher.utter_message(text="Is this your vehicle?", buttons=buttons)
                return [SlotSet('vin_value',message),SlotSet('vehicle_owning_status',True)] 
            else:
                dispatcher.utter_message(text="Wrong VIN value")
                dispatcher.utter_template('utter_send_link',tracker)
                return []


        elif message.replace(' ','').replace(',','').isnumeric() is True   and tracker.get_slot('miles_value') is None and tracker.get_slot('vin_value') is not None:
            price = FETCH_PRICE(tracker.get_slot('vin_value'))
            if price is not None:
                dispatcher.utter_message(text=price)
                dispatcher.utter_message(text="Here is the price range, would you like to talk to our rep in detail about this price",buttons=buttons)
                return [SlotSet('miles_value',message)] 
            else:
                dispatcher.utter_message("Sorry, unable to tell you the price.")
                dispatcher.utter_template('utter_send_link',tracker)
                return []
 
        elif message.replace(' ','').isalnum() and tracker.get_slot('vehicle_owning_status') is not  True:
            print('--> Received Lisense Plate Number')
            response = LICENSE_PLATE_VALIDATOR(message)
            if response is not None:
                dispatcher.utter_message(text=response)
                dispatcher.utter_message(text=f"Is this your vehicle?", buttons=buttons)
                return [SlotSet('vin_value',message),SlotSet('vehicle_owning_status',True)] 
            else:
                dispatcher.utter_message(text="Wrong Lisense Plate Number")
                dispatcher.utter_template('utter_send_link',tracker)
                return []

        elif phone_numbers!=[]:
            print('--> Received PHONE NUMBER')
            dispatcher.utter_message(text="Thanks for providing details")
            return [SlotSet('phone_number_value',phone_numbers[0])] 


                

        elif message.lower()=='/deny_offer':
            dispatcher.utter_template('utter_send_link',tracker)
            return []
        return []




















class ActionStartConversation(Action):
    def name(self) -> Text:
        return "action_start_conversation"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        buttons = [
                {"payload": "/accept_offer", "title": "Yes, I am ready to talk with with a Bot." },
                {"payload": "/deny_offer", "title": "No, i can't talk with a Bot."},
            ]
        dispatcher.utter_message(text="Thanks for your interest in Buy Your Car, this is an interactive web chat for you to find out the price of your vehicle without any human intervention and pressure, should we start now ?", buttons=buttons)
        return [SlotSet('interested_in_selling_car',True)]




 
class ActionDenyOffer(Action):
    def name(self) -> Text:
        return "action_deny_offer"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        message=tracker.latest_message['text']
        phone_numbers = re.findall(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]', message)
        buttons = [
                {"payload": "/accept_offer", "title": "Yes"},
                {"payload": "/deny_offer", "title": "No"},
            ] 
        if len(message)==17 and ' ' not in message and tracker.get_slot('vehicle_owning_status') is not  True:
            print('--> Received VIN VALUE')
            response = VIN_VALIDATOR(message)
            if response is not  None: 
                dispatcher.utter_message(text=response)
                dispatcher.utter_message(text="Is this your vehicle?", buttons=buttons)
                return [SlotSet('vin_value',message),SlotSet('vehicle_owning_status',True)] 
            else:
                dispatcher.utter_message(text="Wrong VIN value")
                dispatcher.utter_template('utter_send_link',tracker)
                return []

        elif message.replace(' ','').isalnum() and tracker.get_slot('vehicle_owning_status') is not  True:
            print('--> Received Lisense Plate Number')
            response = LICENSE_PLATE_VALIDATOR(message)
            if response is not None:
                dispatcher.utter_message(text=response)
                dispatcher.utter_message(text=f"Is this your vehicle?", buttons=buttons)
                return [SlotSet('vin_value',message),SlotSet('vehicle_owning_status',True)] 
            else:
                dispatcher.utter_message(text="Wrong Lisense Plate Number")
                dispatcher.utter_template('utter_send_link',tracker)
                return []

                

            

        elif message.replace(' ','').replace(',','').isnumeric() is True and tracker.get_slot('miles_value') is None and tracker.get_slot('vin_value') is not None:
            print('--> Received miles value')
            price = FETCH_PRICE(tracker.get_slot('vin_value'))
            dispatcher.utter_message(text=price)
            dispatcher.utter_message(text="Here is the price range, would you like to talk to our rep in detail about this price",buttons=buttons)
            return [SlotSet('miles_value',message)] 
 
        elif phone_numbers!=[]:
            print('--> Received PHONE NUMBER')
            dispatcher.utter_message(text="Thanks for providing details")
            return [SlotSet('phone_number_value',phone_numbers[0])] 

        

        elif message.lower()=='/deny_offer':
            dispatcher.utter_template('utter_send_link',tracker)
            return []
        else:
            print('** NO PATH FOUND')
            dispatcher.utter_template('utter_send_link',tracker)
            return []
        return []


 











# message = tracker.latest_message['text']
# sender_id = (tracker.current_state()['sender_id'])

# dispatcher.utter_message(buttons = [
#                 {"payload": "/affirm", "title": "Yes"},
#                 {"payload": "/deny", "title": "No"},
#             ])

# - text: "Please click this link [Google Website](https://www.google.com/)."