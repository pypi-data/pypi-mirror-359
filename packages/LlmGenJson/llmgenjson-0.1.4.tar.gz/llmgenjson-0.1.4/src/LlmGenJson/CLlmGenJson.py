# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250630-174328
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
Program description
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg
import os
import glob
import json
from openai import OpenAI
from LlmGenJson.funcStrictJson import parse_json_str_from_text


class CLlmGenJson:
    # 调用LLM生成JSON数据
    def __init__(self, sOpenAiUrl, sOpenAiKey, sOpenAiModel, sSystemPromptDir):
        self.sOpenAiUrl = sOpenAiUrl
        self.sOpenAiKey = sOpenAiKey
        self.sOpenAiModel = sOpenAiModel

        # sSystemPromptDir = 系统提示语所在路径，包括 SystemPrompt 子目录
        self.sSystemPromptDir = sSystemPromptDir
        PrintTimeMsg(f'CLlmGenJson.sSystemPromptDir={self.sSystemPromptDir}=')

        self.bDebugPrint = True

    def _loadHigherVersion(self, sPromptTemplateId, sExtFN):
        # 从系统提示语模板目录下加载最大版本的系统提示语或输出JSON格式
        # 提示语模板位于工作目录的 SystemPrompt 子目录下
        # <sPromptTemplateId>_v<NN>.md 格式 或 <sPromptTemplateId>_v<NN>.json 格式
        # 传入的 sPromptTemplateId 用于匹配相同前缀的文件名
        # 传入的 sExtFN 用于匹配文件扩展名
        # 并按文件名从小到大排序，取最大的文件内容
        sPatternFN = f'{sPromptTemplateId}*{sExtFN}'
        lsPatternFN = glob.glob(sPatternFN, root_dir=self.sSystemPromptDir)
        # PrintTimeMsg(f'_loadHigherVersion({sPatternFN}).lsPatternFN={lsPatternFN}')
        sContent = ''
        if lsPatternFN:
            lsSorted = sorted(lsPatternFN, reverse=True)
            sMatchFN = lsSorted[0]
            # PrintTimeMsg(f'_loadHigherVersion.sMatchFN={sMatchFN}')
            sFullFN = os.path.join(self.sSystemPromptDir, sMatchFN)
            with open(sFullFN, 'r', encoding='utf8') as f:
                sContent = f.read()
            PrintTimeMsg(f'_loadHigherVersion({sPromptTemplateId}{sExtFN})={sMatchFN}={len(sContent)}')
        else:
            PrintTimeMsg(f'_loadHigherVersion({sPromptTemplateId}{sExtFN})=NotMatch=Null!')
        return sContent

    def _loadSystemPrompt(self, sPromptTemplateId):
        # 从系统提示语模板目录下加载最大版本的系统提示语
        return self._loadHigherVersion(sPromptTemplateId, '.md')

    def _invoke_llm(self, sPromptSystem, sPromptUser):
        # 调用LLM sPromptSystem=系统提示语，sPromptUser=用户问题
        # 返回结果内容
        oOpenAI = OpenAI(api_key=self.sOpenAiKey, base_url=self.sOpenAiUrl)  # 兼容 OpenAI 客户端
        response = oOpenAI.chat.completions.create(
            model=self.sOpenAiModel,
            temperature=0,
            messages=[
                {"role": "system", "content": sPromptSystem},
                {"role": "user", "content": sPromptUser}
            ]
        )
        return response.choices[0].message.content

    def NaturalLanguageToJson(self, sPromptTemplateId, sPromptUser):
        # 采用 模板 方式调用LLM
        # sPromptTemplateId=模板标识
        # sPromptUser=用户提示语
        # 返回 json 对象
        sPromptSystem = self._loadSystemPrompt(sPromptTemplateId)
        iRetryCnt = 0
        while iRetryCnt < 3:
            sLlmResult = self._invoke_llm(sPromptSystem, sPromptUser)
            if self.bDebugPrint:
                PrintTimeMsg(f'NaturalLanguageToJson({sPromptUser}).sLlmResult={sLlmResult}={iRetryCnt}=')
            sJsonResult = parse_json_str_from_text(sLlmResult)
            if self.bDebugPrint:
                PrintTimeMsg(f'NaturalLanguageToJson({sPromptUser}).sJsonResult={sJsonResult}={iRetryCnt}=')
            try:
                oResult = json.loads(sJsonResult)
                return oResult
            except Exception as e:
                PrintTimeMsg(f'NaturalLanguageToJson({sPromptUser}).sLlmResult={sLlmResult}={iRetryCnt}={repr(e)}')
            iRetryCnt += 1
        return {}

