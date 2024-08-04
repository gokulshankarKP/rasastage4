from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
import openai
from gtts import gTTS
import pandas as pd
import requests
import os
from  dotenv import load_dotenv, find_dotenv
find_dotenv()
load_dotenv()
import boto3
import numpy as np
import json
import ast
from tqdm import tqdm
import time
import string
import chardet
import base64

#############################################################################################################################################################################################################
#############################################################################################################################################################################################################
#############################################################################################################################################################################################################
#############################################################################################################################################################################################################

class ActionCheckAge(Action):
    def name(self) -> Text:
        return "action_check_age"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global age
        recipe = pd.read_csv(r"recipe.csv", encoding = 'latin-1')
        recipe['age'] = recipe['age'].astype(str)
        age_list = recipe['age'].to_list()
        age = str(tracker.get_slot("age"))
        age_is_valid = age in age_list
        return [SlotSet("age_is_valid", age_is_valid)]
    

class ActionCheckGoodbyeCertaindays(Action):

    def name(self) -> str:
        return "action_check_goodbye_certaindays"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input = tracker.get_slot("any_question_certaindays")
        if 'bye' in user_input:
            return [SlotSet("user_said_goodbye_certaindays", True)]
        return [SlotSet("user_said_goodbye_certaindays", False)]
    



class ActionGetRecipe(Action):
    def name(self) -> Text:
        return "action_get_recipe"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        food_category = str(tracker.get_slot("food_category"))
        lactose_intolerant = tracker.get_slot("lactose_intolerant")
        age=tracker.get_slot("age")
        file_path = r"C:\Users\gokul\Downloads\rasa_dev\recipesss.csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        recipe = pd.read_csv(file_path, encoding=encoding)
        print("recipe1")

        
       

        if(lactose_intolerant==True):
            lactose_intolerant=1
        else:
            lactose_intolerant=0

        file_path = r"C:\Users\gokul\Downloads\rasa_dev\Nestle_Infant_Milk_Products_and_cereals.csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        nestle_products = pd.read_csv(file_path, encoding=encoding)
        nestle_products_text=nestle_products.to_string()


        recipe.to_csv(r"C:\Users\gokul\Downloads\rasa_dev\details_of_recipe.csv",index=False)

        all_text = recipe.to_string()
        print(recipe.shape)
        print(len(all_text))
        prompt = f"""
        the data of the recipe with details 
        
        {all_text} and my child age is {age} and lactose {lactose_intolerant} and food session is {food_category}
        
        please select the good recipe from this data and give details of recipe name , description , incredients , steps , nutrients present with nestle product {nestle_products_text}.
        """
       
        if True:
        
        

            response = openai.ChatCompletion.create(
                # model="gpt-3.5-turbo",
                model="gpt-4o-mini",
                temperature=0.0,
                top_p=0.0001,
                messages=[
                    {"role": "system", "content": "You behave like a chatbot and give recipe details to user."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the CSV formatted response
            csv_data = response['choices'][0]['message']['content']

     
        
        print(csv_data)
        recommended_recipe=csv_data
        rephrased_recipe=recommended_recipe

        input_value = "can you suggest food?"
        response_value = recommended_recipe

        # Read the existing CSV file into a DataFrame
        file_path = r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        prev_res = pd.read_csv(file_path, encoding=encoding)
        # Create a new DataFrame for the new row
        new_data = {'input': input_value, 'response': response_value}
        new_row = pd.DataFrame([new_data])
        prev_res = pd.concat([prev_res, new_row], ignore_index=True)
 
      
        # Save the updated DataFrame back to the CSV file
        prev_res.to_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv", index=False)
        return [SlotSet("recommended_recipe", recommended_recipe), SlotSet("rephrased_recipe", rephrased_recipe)]





    

class ActionHandleFallbackQuestion(Action):
    def name(self) -> Text:
        return "action_handle_fallback_question"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input =tracker.get_slot("any_question")
        print(user_input)
        file_path=r"C:\Users\gokul\Downloads\rasa_dev\details_of_recipe.csv"
        recipe = pd.read_csv(file_path, encoding='latin1')
        print("handle recipe2")

        prev_response=pd.read_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv", encoding='latin1')

        
        prev_data=prev_response.to_string()
        all_text = recipe.to_string()


        prompt = f"""
        the data of the recipe with details 
        
        {all_text}   and previous context of chat gives this recipe {prev_data} and my wquestion is {user_input}
        
        please answer above question using the data , with good description 
        """
       
        if True:
            response = openai.ChatCompletion.create(
                # model="gpt-3.5-turbo",
                model="gpt-4o-mini",
                temperature=0.0,
                top_p=0.0001,
                messages=[
                    {"role": "system", "content": "You behave like a chatbot and give recipe details to user."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the CSV formatted response
            csv_data = response['choices'][0]['message']['content']

        

     
        another_recipe=csv_data
        prev_response=pd.read_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv")
        new_data = {'input': user_input, 'response': csv_data}
        new_row = pd.DataFrame([new_data])
        prev_response = pd.concat([prev_response, new_row], ignore_index=True)
 

        prev_response.to_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv",index=False)
        return [SlotSet("another_recipe", another_recipe)]

       



    



    
    

class ActionCheckGoodbye(Action):

    def name(self) -> str:
        return "action_check_goodbye"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input = tracker.get_slot("any_question")
        if 'bye' in user_input:
            return [SlotSet("user_said_goodbye", True)]
        return [SlotSet("user_said_goodbye", False)]
    


# class ActionAudioConvert(Action):

#     def name(self) -> str:
#         return "action_audio_convert"

#     async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         certaindays_output = tracker.get_slot("certaindays_output")
#         if certaindays_output:
#              # Directory where the audio file will be saved
#             print("audioconvertedstarted")
#             audio_file_path = r"C:\Users\gokul\Downloads\rasa_dev\static\audio\output.mp3"
#             os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)

#             # Generate the audio file
#             tts = gTTS(text=certaindays_output, lang='en')
#             tts.save(audio_file_path)
#             print("audioconvertioncompleted")

#             # URL to the audio file, served by Rasa
#             audio_url = "/static/audio/output.mp3"
            
#             return [SlotSet("audiofile", audio_url)]
#         return []

        

# class ActionProvideAudioLink(Action):

#     def name(self) -> str:
#         return "action_provide_audio_link"

#     async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         path = tracker.get_slot("audiofile")
#         print(path)
#         path="C:\\Users\\gokul\\Downloads\\rasa_dev\\static\\audio\\output.mp3"
#         audio_file_path = path

#         with open(audio_file_path, "rb") as audio_file:
#             encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

#         # Construct the URL for the audio file
#         # base_url = "http://localhost:5005"
#         # audio_url = f"{base_url}/{audio_file_path}"
#         # print(audio_url)

#         custom_payload = {
#             "audio": encoded_audio,
#             "format": "mp3"
#         }

#         dispatcher.utter_message(text="Here is the audio file for your recipe suggestion:", custom=custom_payload)


#         return []



class ActionCertaindaysPlan(Action):
    def name(self) -> Text:
        return "action_certaindays_plan"


    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        age=tracker.get_slot("age_certaindays")
        height=tracker.get_slot("height_certaindays")
        weight=tracker.get_slot("weight_certaindays")
        certaindays_output=tracker.get_slot("no_of_days")
        lactose_intolerant=tracker.get_slot("lactose_intolerant_certaindays")
        print("certain_days started")

        
        file_path = r"C:\Users\gokul\Downloads\rasa_dev\recipesss.csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        recipe = pd.read_csv(file_path, encoding=encoding)
        recipe_text = recipe.to_string()


        file_path = r"C:\Users\gokul\Downloads\rasa_dev\nutrient_requirements (1).csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        deit_details = pd.read_csv(file_path, encoding=encoding)
        deit_details_text=deit_details.to_string()


        file_path = r"C:\Users\gokul\Downloads\rasa_dev\Nestle_Infant_Milk_Products_and_cereals.csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        nestle_products = pd.read_csv(file_path, encoding=encoding)
        nestle_products_text=nestle_products.to_string()
       

        if(lactose_intolerant==True):
            lactose_intolerant=1
        else:
            lactose_intolerant=0


        #recipe.to_csv(r"C:\Users\gokul\Downloads\rasa_dev\details_of_recipe.csv",index=False)

        
        print(recipe.shape)
        print(len(recipe_text))

        prompt = f"""
        please good recipe for {certaindays_output} days , i need output  like day1 with day1(header) breakfast(header)(recipe name ,descrption,) lunch(header)(recipe name , dexfcrption , incredient) ,snacks (rescipe name, description ), dinner(name , description , incredient) and followed by day2..
        data is {recipe_text} and my child age is {age} and height {height} and weight is {weight} and lactose suggestion {lactose_intolerant} and 
         each day with breakfast , lunch , dinner and snacks without repetitive recipe from this data and give details  with nestle products {nestle_products_text} with each recipe:
        """
       
        if True:
            response = openai.ChatCompletion.create(
                # model="gpt-3.5-turbo",
                model="gpt-4o-mini",
                temperature=0.0,
                top_p=0.0001,
                messages=[
                    {"role": "system", "content": "You behave like a chatbot and give recipe details to user."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the CSV formatted response
            csv_data = response['choices'][0]['message']['content']

        certaindays_output=csv_data


        input_value = "can you suggest food for {certaindays_output} days and age {age} and height {height} and lactose intolerace {lactose_intolerant}?"
        response_value = certaindays_output


        # Read the existing CSV file into a DataFrame
        file_path = r"C:\Users\gokul\Downloads\rasa_dev\prev_response_certaindays.csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        prev_res = pd.read_csv(file_path, encoding=encoding)

        # Create a new DataFrame for the new row
        new_data = {'input': input_value, 'response': response_value}
        new_row = pd.DataFrame([new_data])
        prev_res = pd.concat([prev_res, new_row], ignore_index=True)
 
      
        # Save the updated DataFrame back to the CSV file
        prev_res.to_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response_certaindays.csv", index=False)
        return [SlotSet("certaindays_output", certaindays_output)]





    

class ActionCertaindaysFallbackQuestion(Action):
    def name(self) -> Text:
        return "action_certaindays_fallback_question"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input =tracker.get_slot("any_question_certaindays")
        age=tracker.get_slot("age_certaindays")
        height=tracker.get_slot("height_certaindays")
        weight=tracker.get_slot("weight_certaindays")
        lactose_intolerant=tracker.get_slot("lactose_intolerant_certaindays")
        certain_days_question=tracker.get_slot("no_of_days")




        print(user_input)
        file_path=r"C:\Users\gokul\Downloads\rasa_dev\details_of_recipe.csv"
        recipe = pd.read_csv(file_path, encoding='latin1')
        prev_response=pd.read_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response_certaindays.csv", encoding='latin1')
        prev_data=prev_response.to_string()
        all_text = recipe.to_string()



        file_path = r"C:\Users\gokul\Downloads\rasa_dev\nutrient_requirements (1).csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        deit_details = pd.read_csv(file_path, encoding=encoding)
        deit_details_text=deit_details.to_string()


        file_path = r"C:\Users\gokul\Downloads\rasa_dev\Nestle_Infant_Milk_Products_and_cereals.csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        nestle_products = pd.read_csv(file_path, encoding=encoding)
        nestle_products_text=nestle_products.to_string()
       





        prompt = f"""
        you are chatbot, my question is {user_input}, my previous conversation is {prev_data} , the data of the recipe with details
        {all_text} and my child age is {age} and height {height} and weight is {weight} and lactose suggestion {lactose_intolerant} and 
        {certain_days_question} days ,give details of recipe name , description , incredients ,nutrients present in recipe for each day(breakfast ,lunch , snacks , dinner) with nestle products {nestle_products_text}.
        """
       
        if True:
            response = openai.ChatCompletion.create(
                # model="gpt-3.5-turbo",
                model="gpt-4o-mini",
                temperature=0.0,
                top_p=0.0001,
                messages=[
                    {"role": "system", "content": "You behave like a chatbot and give recipe details to user."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the CSV formatted response
            csv_data = response['choices'][0]['message']['content']

        

     
        certaindays_another_recipe=csv_data
        prev_response=pd.read_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response_certaindays.csv")
        new_data = {'input': user_input, 'response': csv_data}
        new_row = pd.DataFrame([new_data])
        prev_response = pd.concat([prev_response, new_row], ignore_index=True)
        prev_response.to_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv",index=False)
        
        return [SlotSet("certaindays_another_recipe", certaindays_another_recipe)]



