# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250529-100152
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
from weberFuncs import JoinGetFileNameFmSrcFile
import os
from LlmGenJson.CLlmGenJson import CLlmGenJson
from LlmGenJson.funcHigherVer import loadHigherVersion
from dotenv import load_dotenv


def mainClassOne():

    sSystemPromptDir = JoinGetFileNameFmSrcFile(__file__, ['SystemPrompt'], 1)
    PrintTimeMsg(f'mainClassOne.sSystemPromptDir={sSystemPromptDir}=')

    sFullEnvFN = JoinGetFileNameFmSrcFile(__file__, ['.env'], 1)
    PrintTimeMsg(f'mainClassOne.sFullEnvFN={sFullEnvFN}=')
    bLoad = load_dotenv(dotenv_path=sFullEnvFN, verbose=True)  # load environment variables from .env
    PrintTimeMsg(f"mainClassOne.load_dotenv({sFullEnvFN})={bLoad}")
    sOpenAiUrl = os.getenv("OPENAI_BASE_URL")
    sOpenAiKey = os.getenv("OPENAI_API_KEY")
    sOpenAiModel = os.getenv("OPENAI_MODEL")
    PrintTimeMsg(f'mainClassOne.sOpenAiUrl={sOpenAiUrl}, sOpenAiModel={sOpenAiModel}')

    oLGJ = CLlmGenJson(sOpenAiUrl, sOpenAiKey, sOpenAiModel)

    def _NaturalLanguageToJson(sPromptTemplateId, sPromptUser):
        sPromptSystem = loadHigherVersion(sSystemPromptDir, sPromptTemplateId, '.md')
        oLGJ.gen_json_via_llm(sPromptSystem, sPromptUser, True)
    # _NaturalLanguageToJson('解析定时任务时间参数-v00', '凌晨6点30分打卡')  # v00 的确不行
    # _NaturalLanguageToJson('解析定时任务时间参数', '每天凌晨6点30分打卡')
    # _NaturalLanguageToJson('解析定时任务时间参数', '凌晨6点30分打卡')

    # _NaturalLanguageToJson('识别定时任务时间参数', '每天凌晨6点30分打卡')
    # _NaturalLanguageToJson('识别定时任务时间参数', '每周一三五下午4点汇总AI新闻')
    # _NaturalLanguageToJson('识别定时任务时间参数', '每月第一天早上9点半汇总上月营收')
    # _NaturalLanguageToJson('识别定时任务时间参数', '每年9月1日10点是开学升旗的时刻')
    # _NaturalLanguageToJson('识别定时任务时间参数', '9月1日是小明的生日')
    _NaturalLanguageToJson('识别定时任务时间参数', '每周五下午5点提交周报')


if __name__ == '__main__':
    mainClassOne()
