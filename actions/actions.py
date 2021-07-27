from typing import Any, Text, Dict, List
from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet,FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from .api_handler import  VIN_VALIDATOR,LICENSE_PLATE_VALIDATOR,VERIFY_STATE,TEXT_ANALYZER
from .price_api import FETCH_PRICE
from .data import *
import re 


#
class ActionApproveOffer(Action):
    def name(self) -> Text:
        return "action_approve_offer"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        buttons = [
                {"payload": "/approve_offer", "title": "Yes"},
                {"payload": "/deny_proposal", "title": "No"},
            ] 
        message=tracker.latest_message['text']

        if tracker.get_slot("stop_bot") is True:
            print("stop value  ",tracker.get_slot("stop_bot"),)
        
        
            return []

        # OFFER APPROVED
        if message=='/approve_offer' or tracker.get_slot("open_approve_offers_portal")is True:
            print('ACTION --> APPROVE ', message)


            # 2nd Offer
            if tracker.get_slot('interested_in_selling_car') is True and tracker.get_slot('interested_in_tentative_price') is None:
                print("-->> 2nd Offer")
                buttons = [
                    {"payload": "/approve_offer", "title": "Yes, I am interested"},
                    {"payload": "/deny_proposal", "title": "No, I am not interested"},
                ] 
                dispatcher.utter_message(text="I can give you a tentative price for your car right here if you are interested?", buttons=buttons)
                return [SlotSet('interested_in_tentative_price',True),SlotSet('open_approve_offers_portal',False)] 
            
        


            # 3rd Offer
            elif tracker.get_slot('interested_in_tentative_price') is True and tracker.get_slot('license_plate_or_vin') is  None:
                print("-->> 3rd Offer")
                buttons = [
                    {"payload": "/i_can_provide_vin", "title": "VIN"},
                    {"payload": "/i_have_plate", "title": "License plate"},
                    {"payload": "/deny_proposal", "title": "I don't have any"},
                ]  
                dispatcher.utter_message(text="Do you have your VIN or license plate?", buttons=buttons)
                return [SlotSet('license_plate_or_vin',True),SlotSet('open_approve_offers_portal',False)] 



            # 5th Offer
            elif tracker.get_slot('vin_value') is not None and tracker.get_slot('vehicle_owning_status') is  True  and tracker.get_slot('have_miles') is  None :
                print("-->> 5th Offer")
                buttons = [
                    {"payload": "/approve_offer", "title": "Yes, I can give miles"},
                    {"payload": "/deny_proposal", "title": "No, I don't have miles"},
                ]                  
                dispatcher.utter_message(text="Do you have miles for your vehicle?", buttons=buttons)
                return [SlotSet('have_miles',True),SlotSet('open_approve_offers_portal',False),SlotSet("vin_fetched_locker",False)] 


            # 6th Offer
            elif tracker.get_slot('have_miles') is not None and tracker.get_slot('miles_value') is  None :
                print("-->> 6th Offer")               
                dispatcher.utter_message(text="Please enter the miles on the vehicle")
                return [SlotSet('open_approve_offers_portal',False),SlotSet('miles_locker',True),] 






            # 7th offer
            elif tracker.get_slot('miles_value')is not None  and tracker.get_slot('would_like_to_talk_in_detail') is not True :
                print("-->> 7th offer")
                buttons = [
                    {"payload": "/approve_offer", "title": "Yes"},
                    {"payload": "/deny_proposal", "title": "No"},
                ]    
                dispatcher.utter_message(text="Can you please provide your phone number?",buttons=buttons)
                return [SlotSet('would_like_to_talk_in_detail',True),SlotSet('open_approve_offers_portal',False), SlotSet("price_range_fetched_locker",False)] 

            # 8th offer
            elif tracker.get_slot('would_like_to_talk_in_detail')is True  and tracker.get_slot('phone_number_value') is None :
                print("-->> 8th offer")
                dispatcher.utter_message(text="Please enter your phone number")
                return [SlotSet('open_approve_offers_portal',False),SlotSet('phone_number_locker',True)] 


      
 
        else:
            return [FollowupAction("action_handle_text_data")]
























 
class ActionHandleTextData(Action):
    def name(self) -> Text:
        return "action_handle_text_data"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        if tracker.get_slot("stop_bot") is True:return []
        
        
        message=tracker.latest_message['text']
        message = str(message).strip()
        print(f'ACTION --> TEXT DATA  [{message}]') 
        phone_numbers = re.findall(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]', message)
        buttons = [
                {"payload": "/approve_offer", "title": "Yes"},
                {"payload": "/deny_proposal", "title": "No"},
            ] 

        if tracker.get_slot('license_plate_or_vin')=='vin' and tracker.get_slot('vin_value') is None:
            print("** VIN traced")
            message = [x for x in message.split() if len(x)==17]
            if len(message)>0:
                message=message[0]
                print("-->> 17 Digit VIN traced")
                print("-->> VIN = ", message)
                res = VIN_VALIDATOR(message)

                if res is not None:
                    buttons = [{"payload": "/approve_offer", "title": str(x) }   for x in res[2:]]
                    buttons.append({"payload": "/deny_proposal", "title": "I don't see my trim"})
                    print("display data")

                    # 4th OFFER
                    print("-->> 4th offer")
                    dispatcher.utter_message(text=f"Please confirm your trim for {res[1]}", buttons=buttons)
                    return [SlotSet("fetched_cars",f'{res[2:]}'.lower()),SlotSet('vin_value',message),SlotSet('vehicle_owning_status',True)]
              
                else:                    
                    print("** VIN API validation failed ") 
                    dispatcher.utter_template('utter_send_link_invalid_vin',tracker)
                    return [] 
            else:
                print("-->> In-valid VIN traced ") 
                dispatcher.utter_template('utter_send_link_invalid_vin',tracker)
                return [] 


        elif tracker.get_slot("vin_fetched_locker") is True:
            print("-->> VIN RECALLED ")
            res = VIN_VALIDATOR(tracker.get_slot("vin_value"))

            if res is not None:
                buttons = [{"payload": "/approve_offer", "title": str(x) }   for x in res[2:]]
                buttons.append({"payload": "/deny_proposal", "title": "I don't see my trim"})
                print("display data")

                # 4th OFFER
                print("-->> 4th offer")
                dispatcher.utter_message(text=f"Please confirm your trim for {res[1]}", buttons=buttons)
                return [
                    SlotSet("fetched_cars",f'{res[2:]}'.lower()), 
                    SlotSet('vehicle_owning_status',True),
                    SlotSet('vin_fetched_locker',None)
                ]
              





        elif tracker.get_slot('license_plate_or_vin')=='license_plate' and tracker.get_slot('license_plate_value') is None:
            print("license_plate traced")
            dispatcher.utter_message(text="Please enter the state name for your vehicle?")
            return [SlotSet('license_plate_value',message)]
            


        elif tracker.get_slot('license_plate_or_vin')=='license_plate' and tracker.get_slot('license_plate_value') is not None and tracker.get_slot("state_value") is None:
            # state api called
            print("** STATE traced")
            incoming_state = message
            state_code = [VERIFY_STATE(x) for x in message.split()]
            state_code = [x for x in state_code if x]
             

            if len(state_code)>0:
                state_code = state_code[0]
                print("-->> Valid STATE traced ")
                print("-->> Valid STATE = ", state_code)
                # plate validation api called
                print("-->> Validating License Plate")
                res = LICENSE_PLATE_VALIDATOR(tracker.get_slot('license_plate_value'),state_code)
                if res is not None:
                    buttons = [{"payload": "/approve_offer", "title": str(x) }   for x in res[2:]]
                    buttons.append({"payload": "/deny_proposal", "title": "I don't see my trim"})
                    print("display data")
                    

                    # 4th OFFER
                    print("-->> 4th offer")
                    dispatcher.utter_message(text=f"Please confirm your trim for {res[1]}", buttons=buttons)
                    
                    return [SlotSet("fetched_cars",f'{res[2:]}'.lower()),SlotSet('state_value',message),SlotSet('vin_value',res[0]),SlotSet('vehicle_owning_status',True)]


                else:
                    print('** IN-VALID License Plate Number')
                    dispatcher.utter_template('utter_send_link_invalid_license_plate',tracker)
                    return [SlotSet('state_value',None),SlotSet('license_plate_value',None)]
            else:
                print("-->> In-valid STATE traced ") 
                dispatcher.utter_template('utter_send_link_invalid_state',tracker)
                return []
                

        # Accepting Miles Text data
        elif tracker.get_slot('have_miles') is not None and tracker.get_slot("miles_locker") is True and tracker.get_slot('miles_value') is  None :
            print("** Miles - traced")
            miles = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", message)

            if len(miles)>0:
                miles = miles[0]



                print("--> Valid Miles traced.")
                print("--> Miles = ",miles)
                print("--> VIN = ",tracker.get_slot("vin_value"))
                price = FETCH_PRICE(tracker.get_slot("vin_value"))
                if price is not None: 
                    buttons = [
                        {"payload": "/approve_offer", "title": "Yes"},
                        {"payload": "/deny_proposal", "title": "No"},
                    ] 
                    dispatcher.utter_message(text=f"Here is the price range {price}, would you like to talk to our representative in detail about this price?",buttons=buttons)
                    return [SlotSet('miles_value',miles)] 
                else: 
                    print("** Miles API returned NONE ")
                    dispatcher.utter_template('utter_send_link_invalid_miles',tracker)
                    return [] 
            else:
                print("** In-valid - Miles traced.")
                dispatcher.utter_template('utter_send_link_invalid_miles',tracker)
                return []




        elif tracker.get_slot("price_range_fetched_locker") is True:
            print("-->> PRICE API RECALLED")
            price = FETCH_PRICE(tracker.get_slot("vin_value"))
            if price is not None: 
                buttons = [
                    {"payload": "/approve_offer", "title": "Yes"},
                    {"payload": "/deny_proposal", "title": "No"},
                ] 
                dispatcher.utter_message(text=f"Here is the price range {price}, would you like to talk to our representative in detail about this price?",buttons=buttons)
                return [SlotSet('price_range_fetched_locker',None)] 
            else: 
                print("** Miles API returned NONE ")
                dispatcher.utter_template('utter_send_link_invalid_miles',tracker)
                return [] 







        # Accepting Phone Number Text data
        elif tracker.get_slot('would_like_to_talk_in_detail')is True  and tracker.get_slot("phone_number_locker") is True and tracker.get_slot('phone_number_value') is None :
            print("** Phone Number - traced.")
            phone_numbers = re.findall(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]', message)
            if len(phone_numbers)>0:
                print("-->> VALID  Phone Number - traced.")
                dispatcher.utter_message(text="Thanks. Our representative will contact you soon.")
                return [SlotSet("phone_number_value",phone_numbers[0]),SlotSet("stop_bot",True)]
            else:
                print("** In-valid - Phone Number traced.")
                dispatcher.utter_template('utter_send_link_invalid_phone_number',tracker)
                return []


        else:
            print("** Redirecting - AskPreviousQuestion")
            return [FollowupAction("action_ask_previous_question")]
































class AskPreviousQuestion(Action):
    def name(self) -> Text:
        return "action_ask_previous_question"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        if tracker.get_slot("stop_bot") is True:return []
        
        
        message=str(tracker.latest_message['text']).strip().lower()

        cars=tracker.get_slot("fetched_cars")
        if cars is not None:
            cars = list(tracker.get_slot("fetched_cars").strip('][').split(','))
            cars = [x.replace("'",'') for x in cars]
        else:
            cars =[]

        if TEXT_ANALYZER(target_text=message, data_set=accept_keywords+list(cars)):
            print("==>> DATA_SET accept_keywords [PASSED]")
            print("==>> ** Redirecting to approve_offer")
            # 2nd Offer 
            return [FollowupAction("action_approve_offer"),SlotSet("open_approve_offers_portal",True)]


        elif TEXT_ANALYZER(target_text=message, data_set=deny_keywords):
            print("==>> DATA_SET deny_keywords [PASSED]")
            print("==>> ** Redirecting to action_deny_proposal") 
            return [FollowupAction("action_deny_proposal")]
        
        
        elif TEXT_ANALYZER(target_text=message, data_set=vin_keywords):
            print("==>> DATA_SET vin_keywords [PASSED]")
            print("==>> ** Redirecting to action_i_can_provide_vin")
            return [FollowupAction('action_i_can_provide_vin')]
        
        
        elif TEXT_ANALYZER(target_text=message, data_set=license_plate_keywords):
            print("==>> DATA_SET license_plate_keywords [PASSED]")
            print("==>> ** Redirecting to action_i_have_plate")
            return  [FollowupAction('action_i_have_plate')]

        else:
            print("**** IN-VALID TEXT DATA",[message])
            print("**** Moving to LEVEL 2",[message])
            return [FollowupAction("action_ask_previous_question_level_2")]
            
        

       
 



class AskPreviousQuestionLevel2(Action):
    def name(self) -> Text:
        return "action_ask_previous_question_level_2"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        if tracker.get_slot("stop_bot") is True:return []
        
        
        message=str(tracker.latest_message['text']).strip().lower()



        if tracker.get_slot('interested_in_selling_car') is True and tracker.get_slot('interested_in_tentative_price') is None:
            print("-->> 1st Offer LEVEL 2")
            buttons = [
                    {"payload": "/approve_offer", "title": "Yes, I am ready to talk with with a Bot." },
                    {"payload": "/deny_proposal", "title": "No, I can't talk with a Bot."},
                ]
            dispatcher.utter_message(text="Thanks for your interest in Buy Your Car, this is an interactive web chat for you to find out the price of your vehicle without any human intervention and pressure, should we start now?", buttons=buttons)
            return [SlotSet('interested_in_selling_car',True)]
        else:
            

            RETURNED_DATA=[FollowupAction("action_approve_offer"),SlotSet("open_approve_offers_portal",True)]


            if tracker.get_slot('interested_in_tentative_price') is True and tracker.get_slot('license_plate_or_vin') is None:
                print("** Redirecting ---  From LEVEL 2 -->> action_approve_offer")
                RETURNED_DATA.append(SlotSet("interested_in_tentative_price",None))
                return RETURNED_DATA

       
            elif tracker.get_slot('license_plate_or_vin') is True and (tracker.get_slot('vin_value') is None or tracker.get_slot('license_plate_value') is None):
                print("** Redirecting ---  From LEVEL 2 -->> action_approve_offer")
                RETURNED_DATA.append(SlotSet("license_plate_or_vin",None))
                return RETURNED_DATA
       
            elif tracker.get_slot('vin_value') is not None and tracker.get_slot("vin_fetched_locker") is None:
                print("** Redirecting ---  From LEVEL 2 -->> action_handle_text_data")
                print(tracker.get_slot('vin_value') )
                RETURNED_DATA=[FollowupAction("action_handle_text_data")]
                RETURNED_DATA.append(SlotSet("vin_fetched_locker",True))
                return RETURNED_DATA

            elif tracker.get_slot('have_miles') is True and tracker.get_slot('miles_value') is None :
                print("** Redirecting ---  From LEVEL 2 -->> action_approve_offer")
                RETURNED_DATA.append(SlotSet("have_miles",None))
                return RETURNED_DATA
 



            elif tracker.get_slot('miles_value')is not None  and tracker.get_slot('price_range_fetched_locker') is None :
                print("** Redirecting ---  From LEVEL 2 -->> action_handle_text_data")
                print(tracker.get_slot('vin_value') )
                RETURNED_DATA=[FollowupAction("action_handle_text_data")]
                RETURNED_DATA.append(SlotSet("price_range_fetched_locker",True))
                return RETURNED_DATA




            elif tracker.get_slot('would_like_to_talk_in_detail')is True  and tracker.get_slot('phone_number_value') is None :
                print("** Redirecting ---  From LEVEL 2 -->> action_approve_offer")
                RETURNED_DATA.append(SlotSet("would_like_to_talk_in_detail",None))
                return RETURNED_DATA



















 
class ActionICanProvideVIN(Action):
    def name(self) -> Text:
        return "action_i_can_provide_vin"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        if tracker.get_slot("stop_bot") is True:return []
        
        message=tracker.latest_message['text']
        print(f'ACTION --> ** [{message}]')  
        dispatcher.utter_message(text="Please enter your 17 digit VIN?")
        return [SlotSet('license_plate_or_vin','vin')] 

       
 



class ActionIHavePlate(Action):
    def name(self) -> Text:
        return "action_i_have_plate"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        if tracker.get_slot("stop_bot") is True:return []

        message=tracker.latest_message['text']
        print(f'ACTION --> ** [{message}]')
        dispatcher.utter_message(text="Please enter your License plate?")
        return [SlotSet('license_plate_or_vin','license_plate')] 




class ActionStartConversation(Action):
    def name(self) -> Text:
        return "action_start_conversation"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        if tracker.get_slot("stop_bot") is True:return []

        message=tracker.latest_message['text']
        print('ACTION -->', message)
        print("-->> 1st Offer")
        buttons = [
                {"payload": "/approve_offer", "title": "Yes, I am ready to talk with with a Bot." },
                {"payload": "/deny_proposal", "title": "No, I can't talk with a Bot."},
            ]
        dispatcher.utter_message(text="Thanks for your interest in Buy Your Car, this is an interactive web chat for you to find out the price of your vehicle without any human intervention and pressure, should we start now?", buttons=buttons)
        return [SlotSet('interested_in_selling_car',True)]

 
class ActionDenyOffer(Action):
    def name(self) -> Text:
        return "action_deny_proposal"
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        if tracker.get_slot("stop_bot") is True:return []


        message=tracker.latest_message['text']

        if message=='/i_can_provide_vin':
            return [FollowupAction('action_i_can_provide_vin')]
        elif  message =='/i_have_plate':
            return [FollowupAction('action_i_have_plate')]
        else:
            print('ACTION --> DENY ', message) 
            dispatcher.utter_template('utter_send_link',tracker)
            return [SlotSet("stop_bot",True)]








 