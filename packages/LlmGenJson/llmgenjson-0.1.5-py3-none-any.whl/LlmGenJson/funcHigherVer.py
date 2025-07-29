# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250630-174119
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


def loadHigherVersion(sSystemPromptDir, sPromptTemplateId, sExtFN):
    # 从系统提示语模板目录下加载最大版本的系统提示语或输出JSON格式
    # sSystemPromptDir = 系统提示语所在路径，包括 SystemPrompt 子目录
    # <sPromptTemplateId>_v<NN>.md 格式 或 <sPromptTemplateId>_v<NN>.json 格式
    # 传入的 sPromptTemplateId 用于匹配相同前缀的文件名
    # 传入的 sExtFN 用于匹配文件扩展名
    # 并按文件名从小到大排序，取最大的文件内容
    PrintTimeMsg(f'_loadHigherVersion={sSystemPromptDir}=')
    sPatternFN = f'{sPromptTemplateId}*{sExtFN}'
    lsPatternFN = glob.glob(sPatternFN, root_dir=sSystemPromptDir)
    # PrintTimeMsg(f'_loadHigherVersion({sPatternFN}).lsPatternFN={lsPatternFN}')
    sContent = ''
    if lsPatternFN:
        lsSorted = sorted(lsPatternFN, reverse=True)
        sMatchFN = lsSorted[0]
        # PrintTimeMsg(f'_loadHigherVersion.sMatchFN={sMatchFN}')
        sFullFN = os.path.join(sSystemPromptDir, sMatchFN)
        with open(sFullFN, 'r', encoding='utf8') as f:
            sContent = f.read()
        PrintTimeMsg(f'_loadHigherVersion({sPromptTemplateId}{sExtFN})={sMatchFN}={len(sContent)}')
    else:
        PrintTimeMsg(f'_loadHigherVersion({sPromptTemplateId}{sExtFN})=NotMatch=Null!')
    return sContent


def mainClassOne():
    from weberFuncs import JoinGetFileNameFmSrcFile
    sSystemPromptDir = JoinGetFileNameFmSrcFile(__file__, ['SystemPrompt'], 2)
    PrintTimeMsg(f'mainClassOne.sSystemPromptDir={sSystemPromptDir}=')

    loadHigherVersion(sSystemPromptDir, 'Translate_prompt', '.md')


if __name__ == '__main__':
    mainClassOne()

