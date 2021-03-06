from django.shortcuts import render
from urllib.request import urlopen, Request
import json
from random import randint
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

def getReq(_request):
    return render(_request, 'quiz_generator/home.html')

def getQuiz(_request):
    categories = _request.POST.getlist('check[]')
    number_of_questions = int(_request.POST.get('spinner'))

    if len(categories) == 0 or number_of_questions == 0:
        return render(_request, 'quiz_generator/home.html')

    categories_list = []
    for c in categories:
        response = urlopen(Request("http://jservice.io/api/category" + '?id=' + str(c)))
        resp_parsed = json.loads(response.read().decode())
        categories_list.append(resp_parsed['clues'])
    counter = 0
    questions = []
    both = []
    for i in range(number_of_questions):
        rand = randint(0, len(categories_list[counter]) - 1)
        question = categories_list[counter][rand]['question']
        answer   = categories_list[counter][rand]['answer']
        if question == '' or answer == '' or isQuestionInList(question, questions):
            while isQuestionInList(question, questions) or question == '' or answer == '':
                rand = randint(0, len(categories_list[counter]) - 1)
                question = categories_list[counter][rand]['question']
                answer = categories_list[counter][rand]['answer']
        questions.append((i+1, question, categories_list[counter][rand]['category_id']))
        (q, a) = check(question, answer)
        both.append((i+1, q, a))
        counter = (counter + 1, 0)[counter == len(categories_list) - 1]

    return render(_request, 'quiz_generator/questions.html', {'both': both})

def postAnswers(_request):
    questions = _request.POST.getlist('question[]')
    answers = _request.POST.getlist('answer[]')
    right_answers = _request.POST.getlist('right_answer[]')
    cleaned_input = []
    cleaned_answers = []
    count_total = len(questions)
    total_correct = 0
    for i in range(count_total):
        j = answers[i].replace(' ', '').replace('\'',"")
        cleaned_input.append(j.lower())
        j = right_answers[i].replace(' ', '').replace('\'', '')
        cleaned_answers.append(j.lower())
    tup_list = []
    for i in range(count_total):
        tup_list.append((i+1, questions[i], answers[i], right_answers[i], cleaned_answers[i] == cleaned_input[i]))
        if cleaned_input[i] == cleaned_answers[i]:
            total_correct += 1
    return render(_request, 'quiz_generator/answers.html', {'all':tup_list, 'total_correct':[(total_correct, count_total)]})

def getPDF(_request):
    questions = _request.POST.getlist('pdf_questions[]')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="quiz.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    l = []
    l.append(Spacer(1, 20))
    l.append(Paragraph("Quiz generated by the Quiz Generator", styles['title']))
    l.append(Spacer(1, 20))
    for c, q in enumerate(questions):
        l.append(Paragraph(str(c + 1) + '. ' + q + '?', styles['Normal']))
        l.append(Spacer(1, 12))
        l.append(Paragraph('Answer: ______________________________________________________________________', styles['Normal']))
        l.append(Spacer(1, 25))
    doc.build(l)
    return response


def isQuestionInList(question, list):
    for tuple in list:
        if question == tuple[1]:
            return True
    return False
g
def check(q, a):
    q = q.replace('\\', '').replace('<i>', '').replace('</i>', '')
    a = a.replace('\\', '').replace('<i>', '').replace('</i>', '')
    return (q, a)


