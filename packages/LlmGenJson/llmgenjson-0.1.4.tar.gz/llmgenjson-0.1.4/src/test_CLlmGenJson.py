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

    o = CLlmGenJson(sOpenAiUrl, sOpenAiKey, sOpenAiModel, sSystemPromptDir)
    # o._loadSystemPrompt('')
    # o._loadSystemPrompt('Translate_prompt')
    # o._loadSystemPrompt('Translate_stem')
    # o.test_strict_json_llm()
    # return
    # o.NaturalLanguageToJson('解析定时任务时间参数-v00', '凌晨6点30分打卡')  # v00 的确不行
    # o.NaturalLanguageToJson('解析定时任务时间参数', '每天凌晨6点30分打卡')
    # o.NaturalLanguageToJson('解析定时任务时间参数', '凌晨6点30分打卡')

    # o.NaturalLanguageToJson('识别定时任务时间参数', '每天凌晨6点30分打卡')
    # o.NaturalLanguageToJson('识别定时任务时间参数', '每周一三五下午4点汇总AI新闻')
    # o.NaturalLanguageToJson('识别定时任务时间参数', '每月第一天早上9点半汇总上月营收')
    # o.NaturalLanguageToJson('识别定时任务时间参数', '每年9月1日10点是开学升旗的时刻')
    # o.NaturalLanguageToJson('识别定时任务时间参数', '9月1日是小明的生日')
    o.NaturalLanguageToJson('识别定时任务时间参数', '每周五下午5点提交周报')



if __name__ == '__main__':
    mainClassOne()
