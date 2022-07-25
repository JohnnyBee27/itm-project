import requests
import datetime 
import json
from scheduler import book_timeslot
import re 
#create a python file called api_key 
#that contains a dictionary api={"api_key":"your_api_key"}
import api_key
api_key=api_key.api['api_key']
import api
import picker

def check_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if(re.search(regex,email)):  
        print("Valid Email") 
        return True
    else:  
        print("Invalid Email")  
        return False
'''   
def check_user():
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if(re.search(regex,email)):  
        print("Valid Email") 
        return True
    else:  
        print("Invalid Email")  
        return False
'''

def getLastMessage(update_id):
    no_response = None, None, None, None, None
    result = api.tgGetMessages(update_id)
    size= len(result)
    if (size == 0):
        return no_response
    last_index = size-1
    last_item = result[last_index]

    update_id = last_item['update_id']
    if 'message' not in last_item:
        return no_response
    message = last_item['message']
    message_id = message['message_id']
    chat = message['chat']
    chat_id = chat['id']
    chat_type = chat['type']
    if chat_type != 'group': 
        # print('update not of type group')
        return no_response
    if 'text' not in message:
        return no_response
    last_msg = message['text']
    sender = message['from']
    if sender['is_bot']:
        return no_response
    user_id = sender['id']

    return last_msg,chat_id,update_id, user_id, message_id
    
    # if size < 100:
    #     return last_msg,chat_id,update_id, user_id, message_id
    # else:
    #     print('offseting updates limit...')
    #     url = "https://api.telegram.org/bot{}/getUpdates?offset={}".format(api_key,update_id)
    #     response = requests.get(url)
    #     data=response.json()
    #     last_msg=data['result'][len(data['result'])-1]['message']['text']
    #     chat_id=data['result'][len(data['result'])-1]['message']['chat']['id']
    #     update_id=data['result'][len(data['result'])-1]['update_id']
    #     return last_msg,chat_id,update_id


def sendInlineMessageForService(chat_id, reply_to_message_id):
    text='Hi! I am Arc Bot, your corporate scheduling buddy! \n\nYou can control me using these commands\n\n/start-to start chatting with the bot\n/cancel-to stop chatting with the bot.\n\nFor more information please contact jana.ang@obf.ateneo.edu.'
    keyboard={
        'keyboard':
            [
                [{'text':'Progress Report'},{'text':'Post-Project Evaluation'}],
                [{'text':'Planning Seminar'},{'text':'Onboarding'}]
            ],
        'one_time_keyboard': True,
        'selective': True,
    }
    reply_markup=json.JSONEncoder().encode(keyboard)
    response = api.tgSendMessage({ 
        'chat_id': chat_id, 
        'text': text, 
        'reply_markup' : reply_markup, 
        'reply_to_message_id': reply_to_message_id
    })
    return response

time_range = range(8,18)
def generateTimeKeyboard():
    items = []
    for hour in time_range:
        items.append([{'text': '{0:02}:00'.format(hour)}, {'text': '{0:02}:30'.format(hour)}])
        
    return items

def generateTimeList():
    items = []
    for hour in time_range:
        items.append('{0:02}:00'.format(hour))
        items.append('{0:02}:30'.format(hour))
        
    return items

def sendInlineMessageForBookingTime(chat_id):
    text_message='Please choose a time slot...'
    keyboard = generateTimeKeyboard()
    key=json.JSONEncoder().encode({'keyboard': keyboard, 'one_time_keyboard': True})
    response = api.tgSendMessage({ 
        'chat_id': chat_id, 
        'text': text_message, 
        'reply_markup' : key,
    })
    return response

def sendInlineMessageForBookRepeat(chat_id):
    text_message='Already chosen, please choose another time slot...'
    keyboard = generateTimeKeyboard()
    key=json.JSONEncoder().encode({'keyboard': keyboard, 'one_time_keyboard': True})
    response = api.tgSendMessage({ 
        'chat_id': chat_id, 
        'text': text_message, 
        'reply_markup' : key,
    })
    return response

def sendInlineMessageForBookLoop(chat_id):
    text_message='Would you like to add another availability'
    keyboard={'keyboard':[
                [{'text':'yes'}],[{'text':'no'}], #IDK how to do this 
            ]}
    key=json.JSONEncoder().encode(keyboard)
    url='https://api.telegram.org/bot'+str(api_key)+'/sendmessage?chat_id='+str(chat_id)+'&text='+str(text_message)+'&reply_markup='+key
    response = requests.get(url)
    return response

def sendInlineMessageForConfirmation(chat_id):
    text_message='Would you like to continue with these details'
    keyboard={'keyboard':[
                [{'text':'confirm'}],[{'text':'restart'}],
            ]}
    key=json.JSONEncoder().encode(keyboard)
    url='https://api.telegram.org/bot'+str(api_key)+'/sendmessage?chat_id='+str(chat_id)+'&text='+str(text_message)+'&reply_markup='+key
    response = requests.get(url)
    return response

def timeSelector(chat_id, best_time_list):
    text_message='Would you like to continue with these details'
    keyboard = dict()
    keyboard['keyboard'] = []

    for i in range(len(best_time_list)):
        l2 = [{'text': best_time_list[i]}]
        keyboard['keyboard'].append(l2)
        
    key=json.JSONEncoder().encode(keyboard)
    url='https://api.telegram.org/bot'+str(api_key)+'/sendmessage?chat_id='+str(chat_id)+'&text='+str(text_message)+'&reply_markup='+key
    response = requests.get(url)
    return response


def confirmMessage(email,time_slots):
    prompt = "Here are your details:\nEmail:{}\n\navailabilities:{}"
    availabilities = '/n'.join(str(i) for i in time_slots)
    
    message = prompt.format(email,availabilities)
    return message

meeting_types = ['Progress Report','Post-Project Evaluation','Planning Seminar','Onboarding']

def book_session(session):
    description = session['description']
    booking_time = session['booking_time']
    emails = session['emails']
    response = book_timeslot(description,booking_time,emails)
    return response;

def emailHandler(emails):
    l2 = list()

    for i in range(len(emails)):
        l2.append({'email': emails[i]})
        
    print(l2)

    return l2

    

def run():
    prev_last_msg = None
    prev_update_id = None
    sessions = {}
    email_current = None
    while True:
        current_last_msg,chat_id,current_update_id,user_id, message_id =getLastMessage(prev_update_id)
        print({ current_last_msg })
        print(sessions)
        print(user_id)
        if current_update_id==prev_update_id:
            continue
         
        prev_last_msg = current_last_msg
        prev_update_id = current_update_id
        
        if chat_id in sessions:
            session = sessions[chat_id]
            step = session['step']
            user = session['user']
            inp_cnt = session['input_count']
            print(session)
            
            if(session['input_count'] != session['members_count']):
                if (user != user_id):
                    if(step == 6 and
                       current_last_msg != "confirm"):
                        if (user == user_id):
                            api.tgSendSimpleMessage(chat_id,"You are already done")
                            api.tgSendSimpleMessage(chat_id,"Next user, please reply email {}:".format(inp_cnt + 1))
                        else:
                            sessions[chat_id]['user'] = user_id
                            sessions[chat_id]['step'] = 1
                            step = 1
                    if(step == 1):
                        api.tgSendSimpleMessage(chat_id,"Please reply email address {}:".format(inp_cnt + 1))

                elif (user == user_id):
                    if (step == 0 and
                        inp_cnt == 0 and
                        current_last_msg in meeting_types):
                        sessions[chat_id]['step'] = 1
                        sessions[chat_id]['description'] = current_last_msg

                        api.tgSendSimpleMessage(chat_id,"Please reply email address{}:".format(inp_cnt + 1))



                    if (step == 1):
                        if check_email(current_last_msg):
                            if current_last_msg in sessions[chat_id]['emails']:
                                api.tgSendSimpleReply(chat_id, "That email address is already in the guest list", message_id)
                                api.tgSendSimpleReply(chat_id,"Please enter a valid email.\nEnter /cancel to cancel this schedule\nThanks!", message_id)
                                api.tgSendSimpleMessage(chat_id,"Please reply email address {}:".format(inp_cnt + 1))
                                continue

                            email_current = current_last_msg
                            sessions[chat_id]['emails'].append(email_current)
                            sessions[chat_id]['step'] = 2

                            sendInlineMessageForBookingTime(chat_id)

                        else:
                            api.tgSendSimpleReply(chat_id,"Please enter a valid email.\nEnter /cancel to cancel this schedule\nThanks!", message_id)
                            api.tgSendSimpleMessage(chat_id,"Please reply email address {}:".format(inp_cnt + 1))

                    if (step == 2 and 
                        (current_last_msg in generateTimeList() or 
                         current_last_msg == 'yes')):
                            if current_last_msg in sessions[chat_id]['booking_time']:
                                sendInlineMessageForBookRepeat(chat_id)

                            else:
                                sessions[chat_id]['step'] = 3
                                sessions[chat_id]['booking_time'].append(current_last_msg)
                                sendInlineMessageForBookLoop(chat_id)


                    if (step == 3 and current_last_msg == 'yes'): #Repeat or not 
                        sessions[chat_id]['step'] = 2

                        sendInlineMessageForBookingTime(chat_id)

                    if (step == 3 and current_last_msg == 'no'):
                        sessions[chat_id]['step'] = 4
                        step = 4 #hardcoded because for some reason step won't become 4

                    if (step == 4):
                        sendInlineMessageForConfirmation(chat_id)
                        sessions[chat_id]['step'] = 5
                        step = 5

                    if (step == 5 and current_last_msg == 'restart'): 
                        api.tgSendSimpleMessage(chat_id,"Resarting session")
                        sessions[chat_id]['booking_time'] = []
                        sessions[chat_id]['emails'].remove(email_current)
                        sessions[chat_id]['step'] = 0
                        step = 0
                        sendInlineMessageForService(chat_id, message_id)


                    if (step == 5 and current_last_msg == 'confirm'):
                        sessions[chat_id]['step'] = 6
                        step = 6
                        api.tgSendSimpleMessage(chat_id,"Proceeding to add your availabilities")
                        #----------code to send availabilities to picker--------------------------
                        picker.updateLists(sessions[chat_id]['booking_time'])
                        #----------------------------------------
                        api.tgSendSimpleMessage(chat_id,"Thank you! Your availabilites have been added")
                        sessions[chat_id]['booking_time'] = []
                        sessions[chat_id]['input_count'] = sessions[chat_id]['input_count'] + 1
                        sessions[chat_id]['users_done'].append(user)
                        #sessions[chat_id]['user'].append(user)
                        if (sessions[chat_id]['input_count'] != sessions[chat_id]['members_count']):
                            api.tgSendSimpleMessage(chat_id,"Next user, please reply the word 'next'.".format(inp_cnt + 2))
                            
                        if (sessions[chat_id]['input_count'] == sessions[chat_id]['members_count']):
                            api.tgSendSimpleMessage(chat_id,"All users have placed their availabilites")
                            api.tgSendSimpleMessage(chat_id,"Proceeding to booking...")
                            sessions[chat_id]['step'] = 7
                            step = 7

                    if (step == 6 and
                        current_last_msg != "confirm"):
                        api.tgSendSimpleMessage(chat_id,"You are already done")
                        api.tgSendSimpleMessage(chat_id,'Next user, please reply "next".'.format(inp_cnt + 1))

                    if current_last_msg == '/cancel':
                        sessions.pop(chat_id)
                        continue        

                else:
                    api.tgSendSimpleReply(chat_id,"Please wait for your turn to add your availability, Thank you!! :>", message_id)
                    
            #------------Get Best Time, then select from the choices-------------------------------
            
            elif (sessions[chat_id]['input_count'] == sessions[chat_id]['members_count']):
                if (user_id == sessions[chat_id]['users_done'][0]):
                    best_times = picker.bestTime()
                    best_times_list = best_times.split(', ')

                    if(step == 7):
                        api.tgSendSimpleMessage(chat_id,"Here are the best times for your meeting")
                        api.tgSendSimpleMessage(chat_id,"Time/s: {}".format(best_times))
                        if(len(best_times_list)) != 0:
                            api.tgSendSimpleMessage(chat_id,"Please Select your preferred time".format(best_times))
                            timeSelector(chat_id, best_times_list)
                            sessions[chat_id]['step'] = 8
                            step = 8

                    if(step == 8 and
                      current_last_msg in best_times_list):
                        response = book_timeslot(sessions[chat_id]['description'],current_last_msg,emailHandler(sessions[chat_id]['emails']))
                        if response:
                            api.tgSendSimpleMessage(chat_id,"Meeting successfully Booked! Thank you!!! : >")
                            sessions.pop(chat_id)
                        else:
                            api.tgSendSimpleMessage(chat_id,"Sorry, but meeting scheduler was unsuccessful/nTry another date, or try again tomorrow")
                            sessions.pop(chat_id)
                        
                    
                else:
                    api.tgSendSimpleMessage(chat_id,"User did not start this meeting scheduler")
                
                    
                    
                       


          
        elif current_last_msg=='/start':
            member_count = api.tgGetChatMembersCount(chat_id) - 1
            picker.listReset()
            sessions[chat_id] = {
                'step': 0,
                'user': user_id,
                'members_count': member_count,
                'input_count': 0,
                'description': None,
                'booking_time': list(),
                'users_done': [],
                'emails': []
            }
            
            print(sessions[chat_id])
            sendInlineMessageForService(chat_id, message_id)

            
            
if __name__ == "__main__":
    run()