# coding=GBK
import json
import numpy as np
#概念信息统计json
class CJsonConcept:

    def __init__(self):
        self.listConcept = list()

    def AddConcept(self,concept,count):
        dic = dict()
        dic['concept'] = concept
        dic['count'] = count
        self.listConcept.append(dic)

    def ToJson(self):
        concept = {}
        concept['type'] = 'concept_push'
        concept['concept'] = ['']*len(self.listConcept)

        for i in range(len(self.listConcept)):
            concept['concept'][i] = self.listConcept[i]

        #print(stock)

        strJson = json.dumps(concept, ensure_ascii=False)
        print(strJson)
        return strJson
