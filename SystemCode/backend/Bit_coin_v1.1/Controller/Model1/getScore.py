from Controller.Model1 import model as model1, score
import Controller.SpiderByData.getDataFromDB as getDataFromDB


def get_score_from_DB(data):
    comments = getDataFromDB.selectComment(data)
    this_score = score(model1, comments)
    number = comments.size
    print(this_score)
    return this_score, number

# get_score_from_DB('2020-09-09')