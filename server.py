from flask import Flask, render_template, request
import spacy
import datetime
app = Flask(__name__)
nlp = spacy.load('en_core_web_sm')
@app.route('/')
def home():
    return render_template('blog.html')

@app.route('/result', methods = ['POST','GET'])
def result():
    if request.method=='POST':
        result = request.form

        example = result['message']

        def detect_past_sentence(sentence):
            sent = sentence
            return (
                    sent.root.tag_ == "VBD" or
                    any(w.dep_ == "aux" and w.tag_ == "VBD" for w in sent.root.children))

        def getweek(week):
            if (week == 'sunday'):
                return 6
            elif (week == 'monday'):
                return 0
            elif (week == 'tuesday'):
                return 1
            elif (week == 'wednesday'):
                return 2
            elif (week == 'thursday'):
                return 3
            elif (week == 'friday'):
                return 4
            elif (week == 'saturday'):
                return 5

        # example = "Hey Snigdha, how are you? It's been a long time. Yeah I am good. How is everything at your place ? Yeah everything's fine. All of our friends are planning something. Will it be possible for you to attend a get-together on 4 October?. Oh yes. I will definetly come. When does it start? The meet starts at 10 AM. Please come along with your family. Yeah sure. See you there. Alright bye"
        # example = "Hello doctor. Hello. Take a seat. Tell me what your problem is. I have been suffering from fever for the past 2 days. Okay, let me check your temperature. It's 103 degrees. You have high fever. Take this medicine at 2 PM today. If the fever does not subdue, take a corona test tomorrow. Meet me at 3 PM this wednesday."
        sen_doc = nlp(example)
        sentences = list(sen_doc.sents)
        # print(sentences)
        present_perfect=['had been','have been','has been']
        rem_list = {}
        for sentence in sentences:
            #print(sentence,sentence.ents)
            pp = False
            for i in present_perfect:
                #print(sentence,str(sentence).find(i),i)
                if str(sentence).find(i)!=-1:
                    pp = True
                    break
            if pp:
                continue
            if detect_past_sentence(sentence) == True :
                continue
            date = False
            time = False
            ent1 = ""
            ent2 = ""
            list1 = []
            list2 = []
            pobj=''
            notpobj = ['AM','PM','am','pm','January','january','February','february','March','march','April','april','May','may','June','june','July','july','August','august','September','september','October','october','November','november','December','december']
            words = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
            rem = {'appointment': 'Your appointment at', 'meet': 'Your meeting at ', 'meeting': 'Your meeting at',
                   'medicine': 'Take medicines at', 'medicines': 'Take medicines at', 'come': 'Your Meeting at','tablet': 'Take medicines at',
                   'party' : 'Attend Party at', }
            for ent in sentence.ents:

                #print(ent.text,ent.label_)
                if ent.label_ == "DATE":
                    date_words = ent.text.split(" ")
                    print(ent.text)
                    if (ent.text.casefold() == 'today'):
                        list1.append(str(datetime.date.today()))
                    elif (ent.text .casefold() == 'tomorrow'):
                        list1.append(str(datetime.date.today() + datetime.timedelta(days=1)))
                    elif ((date_words[0].casefold() == 'this') and date_words[1] in words):
                        n = int(datetime.datetime.today().weekday())
                        w = int(getweek(date_words[1]))
                        list1.append(str(datetime.date.today() + datetime.timedelta(days=w - n)))
                    elif (date_words[0].casefold() == 'next' and date_words[1] in words):
                        num = 6 - int(datetime.datetime.today().weekday())
                        num = num + getweek(date_words[1]) + 1
                        list1.append(str(datetime.date.today() + datetime.timedelta(days=num)))
                    elif (date_words[0] in words):
                        n = int(datetime.datetime.today().weekday())
                        w = int(getweek(date_words[0]))
                        list1.append(str(datetime.date.today() + datetime.timedelta(days=w - n)))
                    else:
                        list1.append(ent.text)
                    #print(ent.text)
                    ent1 = ent.text
                    date = True
                if ent.label_ == "TIME":
                    list1.append(ent.text)
                    ent2 = ent.text
                    time = True
            if date or time:
                for token in sentence:
                    if token.dep_ == "ROOT" or token.dep_ == 'dobj' or token.dep_ == 'pobj' or token.dep_ == 'compound' or token.dep_ == 'nsubjpass':
                        if (token.dep_=='pobj' or token.dep_ == 'compound') and (token.text not in notpobj):
                            pobj=pobj+' '+token.text

                        if token.dep_ != 'pobj':
                            list2.append(token.text)

                        #print(token.text,":",ent1,ent2)
                    #print (token.text, token.tag_, token.head.text, token.dep_)
            if len(list1) > 0 and len(list2) > 0:
                key = ' '.join(list2)
                key1=''
                flag = False
                words_in_key = key.split(" ")
                for word in words_in_key:
                    #print(word)
                    if word.casefold() in rem:
                        flag = True
                        key1 = rem[word.casefold()]+' '+str(pobj)
                        break
                value = ' '.join(list1)
                #print(key1)
                if flag:
                    rem_list[key1] = value
                else:
                    rem_list[key] = value
        return render_template("result.html",result = rem_list)

if __name__ == "__main__":
    app.run()


