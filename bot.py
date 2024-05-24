# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, TurnContext,ConversationState,UserState,MessageFactory,CardFactory
from botbuilder.schema import ChannelAccount,SuggestedActions,CardAction,ActionTypes,Activity,ActivityTypes,Attachment
from googleai import ai
from googlefunction import run_conversation
from datamodel import ConState,UserProfile,EnumUser
import time
import os
import json
CARDS = [
    "resources/card.json"
]

class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    def __init__(self,constate:ConversationState,userstate:UserState,expire_after_seconds: int):
        self.constate=constate
        self.userstate=userstate

        self.conprop=self.constate.create_property('constate')
        self.userprop=self.userstate.create_property('userstate')

        self.expire_after_seconds = expire_after_seconds
        self.last_accessed_time_property = constate.create_property("LastAccessedTime")
        
        # self.state_prop=self.constate.create_property('dialog_set')
        # self.dialog_set=DialogSet(self.state_prop)
        # self.dialog_set.add(TextPrompt('text_prompt'))
        # self.dialog_set.add(WaterfallDialog('main_dialog',[self.Getusername,self.Getphone,self.Getid]))





    async def on_turn(self, turn_context: TurnContext):  
        now_seconds = int(time.time())
        last_access = int(await self.last_accessed_time_property.get(turn_context, now_seconds))
        if now_seconds != last_access and (now_seconds - last_access >= self.expire_after_seconds):
        # Notify the user that the conversation is being restarted.
                  await turn_context.send_activity(
            """Welcome back!  Let's start ."""
        )
        # Clear state.
                  await self.userstate.clear_state(turn_context)
                  await self.userstate.save_changes(turn_context, True)
                  await self.constate.clear_state(turn_context)
                  await self.constate.save_changes(turn_context, True)


        await super().on_turn(turn_context)
    # Set LastAccessedTime to the current time.
        await self.last_accessed_time_property.set(turn_context, now_seconds)

    # Save any state changes that might have occurred during the turn.
        await self.constate.save_changes(turn_context)
        await self.userstate.save_changes(turn_context)
 

    
    async def on_message_activity(self, turn_context: TurnContext):
        conmode=await self.conprop.get(turn_context,ConState)
        usermode=await self.userprop.get(turn_context,UserProfile)
        print(usermode.name)

        if(turn_context.activity.text=="Restro info"):
            message = Activity(
            text="Here is an Adaptive Card:",
            type=ActivityTypes.message,
            attachments=[self._create_adaptive_card_attachment()],
        )
            await turn_context.send_activity(message)
            # await self._send_suggested_actions(turn_context) 



        else:
         response=run_conversation(turn_context.activity.text,usermode.name)
         
         if(response=="Agent stopped due to iteration limit or time limit."):
            a="I didn't understand what you mean,pls try again"
            await turn_context.send_activity(f"{a}")
            if(conmode.profile == EnumUser.NAME):
              usermode.name +=" "
              usermode.name +="user:"+turn_context.activity.text
              usermode.name +=" "
              usermode.name += "you:previous conversation table is no use in this question so i need to check differnt table to find currect response"+" "+response
              
            #   await self._send_suggested_actions(turn_context)

         else:
             await turn_context.send_activity(f"{response}")    
             if(conmode.profile == EnumUser.NAME):
              usermode.name +=" "
              usermode.name +="user:"+turn_context.activity.text
              usermode.name +=" "
              usermode.name += "you:"+response
             
            #   await self._send_suggested_actions(turn_context)

        

       
    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")
                
        # await self._send_suggested_actions(turn_context)


    
    
    # async def _send_suggested_actions(self, turn_context: TurnContext):
    #  """
    # Creates and sends an activity with suggested actions to the user. When the user
    # clicks one of the buttons the text value from the "CardAction" will be displayed
    # in the channel just as if the user entered the text. There are multiple
    # "ActionTypes" that may be used for different situations.
    # """

    # #  reply = MessageFactory.text("What is your favorite color?")
    #  reply =Activity(type=ActivityTypes.message)

    #  reply.suggested_actions = SuggestedActions(
    #     actions=[
    #         CardAction(
    #             title="restro info",
    #             type=ActionTypes.im_back,
    #             value="Restro info",
    #             image="",
    #             image_alt_text="",
    #         ),
    #         CardAction(
    #             title="contact info",
    #             type=ActionTypes.im_back,
    #             value="contact info",
    #             image="",
    #             image_alt_text="",
    #         ),
    #         CardAction(
    #             title="Fill the form",
    #             type=ActionTypes.im_back,
    #             value="Fill the form",
    #             image="https://via.placeholder.com/20/0000FF?text=B",
    #             image_alt_text="",
    #         ),
    #     ]
    # )

    #  return await turn_context.send_activity(reply)
    


    def _create_adaptive_card_attachment(self) -> Attachment:
        card_path = os.path.join(os.getcwd(), CARDS[0])
        with open(card_path, "rb") as in_file:
            card_data = json.load(in_file)

        return CardFactory.adaptive_card(card_data)