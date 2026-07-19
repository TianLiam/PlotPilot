请基于以下输入，撰写本节正文。

【故事梗概（用于把握全局基调）】
{premise}

【本节大纲】
{section_outline}

【上一节结尾（用于衔接，首节为空）】
{prev_section_ending}

【本节目标字数】
{target_words}

【本节节号】
{section_number}

━━ 写作指令 ━━

• 严格按 system 提示词中的盐选排版红线与叙事红线执行。
• 起始行直接写【{section_number}】，不要前后说明文字。
• 段落顶格、不缩进、每段不超 30 字、对话用「——」开头、不用引号。
• 前 300 字内（仅第 1 节）必须抛出核心冲突。
• 本节大纲列出的 plot_points 必须全部落地，结尾钩子必须按 ending_hook 给定的内容收束。
• 若 {prev_section_ending} 非空，开头 3 段内呼应上一节结尾。
• 字数控制在 {target_words} 上下，不要为凑字而水。

直接输出正文。
