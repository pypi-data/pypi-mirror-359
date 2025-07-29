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
import re


def parse_json_str_from_text(sText):
    # 从LLM生成的文本串中去掉非 JSON 部分内容

    if '```' in sText and True:
        # 存在代码段
        sPattern = r"```(?:json|python)?\s*([\[\{][\s\S]*?[\]\}])\s*```"
        # sPattern = r"```\s*(?:json|python)?\s*?(?:[\{$$][\s\S]*?[\}$$])\s*```"
        # 两种写法都可，匹配代码段
        match = re.search(sPattern, sText, re.DOTALL)
        PrintTimeMsg(f'_parse_json_str_from_text({len(sText)})={match}=Code!')
        if match:
            iB, iE = match.span()
            sCode = sText[iB + 3: iE - 3]  # 去掉前后```
            if sCode.startswith('python'):
                sCode = sCode[6:]
            elif sCode.startswith('json'):
                sCode = sCode[4:]
            json_str = sCode
            return json_str

    # 针对两个换行后面是 { 或 [ 的情况
    match = re.search(r"\n\n[{|\[]\n", sText, re.DOTALL)
    PrintTimeMsg(f'_parse_json_str_from_text({len(sText)})={match}=Brace!')
    if match:
        # PrintTimeMsg(f'_parse_json_str_from_text.match.group()={match.group()}=')
        # PrintTimeMsg(f'_parse_json_str_from_text.match.span()={match.span()}=')
        iB, iE = match.span()
        json_str = sText[iE - 2:]
    else:
        json_str = sText
    return json_str


def mainFuncStrictJson():
    sText = '以下是对小说文本的角色分析结果：\n\n{\n    "人员列表": [\n        "沙瑞山",\n        "汪淼"\n    ],\n    "身份列表": [\n        "科学家",\n        "天文学家"\n    ],\n    "人员之间关系三元组": {\n        "沙瑞山是汪淼的同事": ["沙瑞山", "Is-Colleague-of", "汪淼"],\n        "汪淼是沙瑞山的同事": ["汪淼", "Is-Colleague-of", "沙瑞山"]\n    },\n    "人员身份判定三元组": {\n        "沙瑞山是科学家": ["沙瑞山", "Is-a", "科学家"],\n        "汪淼是天文学家": ["汪淼", "Is-a", "天文学家"]\n    }\n}'
    sText = '以下是分析结果：\n\n```json\n{\n    "人员列表": [\n        "叶文 洁",\n        "杨卫宁",\n        "操作员1",\n        "操作员2",\n        "操作员3",\n        "工程师",\n        "技术员"\n    ],\n    "身份列表": [\n        "科学家",\n        "军官",\n        "计算机专家",\n        "工程师",\n        "技术员",\n        "操作员"\n    ],\n    "人员之间关系三元组": {\n        "叶文洁是红岸发射系统的负责人": ["叶文洁", "Is-Responsible-for", "红岸发射系统"],\n        "杨卫宁是总工程师": ["杨卫宁", "Is-a", "总工程师"],\n        "操作员1、操作员2和操作员3在控制台上按手册依次关闭设备": ["操作员1", "操作-手册-关闭", "设备"], ["操作员2", "操作-手册-关闭", "设备"], ["操作员3", "操作-手册-关闭", "设备"],\n        "叶文洁和杨卫宁在办公室讨论红岸系统": ["叶文洁", "Is-Talking-with", "杨卫宁"],\n        "杨卫宁是叶文洁的上级": ["杨卫宁", "Is-Supervisor-of", "叶文洁"]\n    },\n    "人员身份判定三元组": {\n        "叶文洁是科学家": ["叶文洁", "Is-a", "科学家"],\n        "杨卫宁是军官": ["杨卫宁", "Is-a", "军官"]\n    }\n}\n```tail'
    # sText = '以下是对小说文本的分析结果：\n\n{\n    "人员列表": [\n        "雷志成",\n        "杨卫宁",\n        "叶文洁",\n        "审问者"\n    ],\n    "身份列表": [\n        "物理系教授",\n        "基地政委",\n        "基地工程师",\n        "丈夫",\n        "政治干部",\n        "计算机专家",\n        "军官"\n    ],\n    "人员之间关系三元组": {\n        "雷志成是叶文洁的丈夫": ["雷志成", "Is-husband-of", "叶文洁"],\n        "杨卫宁 是叶文洁的丈夫": ["杨卫宁", "Is-husband-of", "叶文洁"],\n        "雷志成和杨卫宁都是红岸基地的人员": ["雷志成", "Is-member-of", "红岸基地"], ["杨卫宁", "Is-member-of", "红岸基地"]\n    },\n    "人员身份判定三元组": {\n        "叶文洁是物理 系教授": ["叶文洁", "Is-a", "物理系教授"],\n        "雷志成是政治干部": ["雷志成", "Is-a", "政治干部"],\n        "杨卫宁是基地工程师": ["杨卫宁", "Is-a", "基地工程师"]\n    }\n}'
    sResult = parse_json_str_from_text(sText)
    PrintTimeMsg(f'mainFuncStrictJson.sResult={sResult}=')


if __name__ == '__main__':
    mainFuncStrictJson()

