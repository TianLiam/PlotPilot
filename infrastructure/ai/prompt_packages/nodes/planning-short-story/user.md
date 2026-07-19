请基于以下输入，生成知乎盐选短篇大纲。

【故事梗概】
{premise}

【题材标签】
{genre_tags}

【目标总字数】
{target_words}

【目标节数】
{target_sections}

━━ 规划要求 ━━

• 直接产出单篇大纲，不要宏观/卷/幕级规划。
• 严格按 system 提示词中的盐选结构红线执行：第一人称、前 300 字抛冲突、≥12 个剧情点、开篇钩子→冲突升级→反转→结局、每节结尾留钩子、结局给情绪价值。
• 节数必须等于 {target_sections}，每节目标字数 1500-2500，总和应接近 {target_words}。
• 反转点前文必须埋伏笔，并在 foreshadowing 字段中明确 planted_at / paid_off_at。
• 触及禁忌的，在 taboo_check 字段中说明并给替代方案。
• 输出严格 JSON，不要包代码块、不要加注释、不要写前后说明文字。
