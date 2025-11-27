
🛠️ 安装指南
下面提供了快速安装和数据集准备的步骤。

💻 环境搭建
我们强烈建议使用 conda 来管理您的 Python 环境。

创建虚拟环境
conda create --name opencompass python=3.10 -y
conda activate opencompass
通过pip安装OpenCompass
# 支持绝大多数数据集及模型
pip install -U opencompass

# 完整安装（支持更多数据集）
# pip install "opencompass[full]"

# 模型推理后端，由于这些推理后端通常存在依赖冲突，建议使用不同的虚拟环境来管理它们。
# pip install "opencompass[lmdeploy]"
# pip install "opencompass[vllm]"

# API 测试（例如 OpenAI、Qwen）
# pip install "opencompass[api]"
基于源码安装OpenCompass
如果希望使用 OpenCompass 的最新功能，也可以从源代码构建它：

git clone https://github.com/open-compass/opencompass opencompass
cd opencompass
pip install -e .
# pip install -e ".[full]"
# pip install -e ".[vllm]"
📂 数据准备
提前离线下载
OpenCompass支持使用本地数据集进行评测，数据集的下载和解压可以通过以下命令完成：

# 下载数据集到 data/ 处
wget https://github.com/open-compass/opencompass/releases/download/0.2.2.rc1/OpenCompassData-core-20240207.zip
unzip OpenCompassData-core-20240207.zip
从 OpenCompass 自动下载
我们已经支持从OpenCompass存储服务器自动下载数据集。您可以通过额外的 --dry-run 参数来运行评估以下载这些数据集。 目前支持的数据集列表在这里。更多数据集将会很快上传。

(可选) 使用 ModelScope 自动下载
另外，您还可以使用ModelScope来加载数据集： 环境准备：

pip install modelscope
export DATASET_SOURCE=ModelScope
配置好环境后，无需下载全部数据，直接提交评测任务即可。目前支持的数据集有：

humaneval, triviaqa, commonsenseqa, tydiqa, strategyqa, cmmlu, lambada, piqa, ceval, math, LCSTS, Xsum, winogrande, openbookqa, AGIEval, gsm8k, nq, race, siqa, mbpp, mmlu, hellaswag, ARC, BBH, xstory_cloze, summedits, GAOKAO-BENCH, OCNLI, cmnli
有部分第三方功能,如 Humaneval 以及 Llama,可能需要额外步骤才能正常运行，详细步骤请参考安装指南。

🔝返回顶部

# 命令行界面 (CLI)
opencompass --models hf_internlm2_5_1_8b_chat --datasets demo_gsm8k_chat_gen

# Python 脚本
opencompass examples/eval_chat_demo.py
你可以在examples 文件夹下找到更多的脚本示例。

export OPENAI_API_KEY="YOUR_OPEN_API_KEY"
# 命令行界面 (CLI)
opencompass --models gpt_4o_2024_05_13 --datasets demo_gsm8k_chat_gen

# Python 脚本
opencompass  examples/eval_api_demo.py


# 现已支持 o1_mini_2024_09_12/o1_preview_2024_09_12  模型, 默认情况下 max_completion_tokens=8192.
推理后端
另外，如果您想使用除 HuggingFace 之外的推理后端来进行加速评估，比如 LMDeploy 或 vLLM，可以通过以下命令进行。请确保您已经为所选的后端安装了必要的软件包，并且您的模型支持该后端的加速推理。更多信息，请参阅关于推理加速后端的文档 这里。以下是使用 LMDeploy 的示例：

opencompass --models hf_internlm2_5_1_8b_chat --datasets demo_gsm8k_chat_gen -a lmdeploy
支持的模型与数据集
OpenCompass 预定义了许多模型和数据集的配置，你可以通过 工具 列出所有可用的模型和数据集配置。

# 列出所有配置
python tools/list_configs.py
# 列出所有跟 llama 及 mmlu 相关的配置
python tools/list_configs.py llama mmlu
支持的模型
如果模型不在列表中，但支持 Huggingface AutoModel 类或支持针对 OpenAI 接口的推理引擎封装（详见官方文档），您仍然可以使用 OpenCompass 对其进行评估。欢迎您贡献维护 OpenCompass 支持的模型和数据集列表。

opencompass --datasets demo_gsm8k_chat_gen --hf-type chat --hf-path internlm/internlm2_5-1_8b-chat
支持的数据集
目前，OpenCompass针对数据集给出了标准的推荐配置。通常，_gen.py或_llm_judge_gen.py为结尾的配置文件将指向我们为该数据集提供的推荐配置。您可以参阅官方文档 的数据集统计章节来获取详细信息。

# 基于规则的推荐配置
opencompass --datasets aime2024_gen --models hf_internlm2_5_1_8b_chat

# 基于LLM Judge的推荐配置
opencompass --datasets aime2024_llmjudge_gen --models hf_internlm2_5_1_8b_chat
此外，如果你想在多块 GPU 上使用模型进行推理，您可以使用 --max-num-worker 参数。

CUDA_VISIBLE_DEVICES=0,1 opencompass --datasets demo_gsm8k_chat_gen --hf-type chat --hf-path internlm/internlm2_5-1_8b-chat --max-num-worker 2
[!TIP]

--hf-num-gpus 用于 模型并行(huggingface 格式)，--max-num-worker 用于数据并行。

[!TIP]

configuration with _ppl is designed for base model typically. 配置带 _ppl 的配置设计给基础模型使用。 配置带 _gen 的配置可以同时用于基础模型和对话模型。

通过命令行或配置文件，OpenCompass 还支持评测 API 或自定义模型，以及更多样化的评测策略。请阅读快速开始了解如何运行一个评测任务。

更多教程请查看我们的文档。

🔝返回顶部

✨ 介绍

面向大模型评测的一站式平台。其主要特点如下：

开源可复现：提供公平、公开、可复现的大模型评测方案

全面的能力维度：五大维度设计，提供 70+ 个数据集约 40 万题的的模型评测方案，全面评估模型能力

丰富的模型支持：已支持 20+ HuggingFace 及 API 模型

分布式高效评测：一行命令实现任务分割和分布式评测，数小时即可完成千亿模型全量评测

多样化评测范式：支持零样本、小样本及思维链评测，结合标准型或对话型提示词模板，轻松激发各种模型最大性能

灵活化拓展：想增加新模型或数据集？想要自定义更高级的任务分割策略，甚至接入新的集群管理系统？OpenCompass 的一切均可轻松扩展！



🔝返回顶部

📖 模型支持
开源模型	API 模型
Alpaca
Baichuan
BlueLM
ChatGLM2
ChatGLM3
Gemma
InternLM
LLaMA
LLaMA3
Qwen
TigerBot
Vicuna
WizardLM
Yi
……
OpenAI
Gemini
Claude
ZhipuAI(ChatGLM)
Baichuan
ByteDance(YunQue)
Huawei(PanGu)
360
Baidu(ERNIEBot)
MiniMax(ABAB-Chat)
SenseTime(nova)
Xunfei(Spark)
……
🔝返回顶部

🔜 路线图
主观评测
发布主观评测榜单
发布主观评测数据集
长文本
支持广泛的长文本评测集
发布长文本评测榜单
代码能力
发布代码能力评测榜单
提供非Python语言的评测服务
智能体
支持丰富的智能体方案
提供智能体评测榜单
鲁棒性
支持各类攻击方法


🤝 致谢
该项目部分的代码引用并修改自 OpenICL、OpenCompass。

该项目部分的数据集和提示词实现修改自 chain-of-thought-hub, instruct-eval
