请基于以下短篇全文，生成知乎盐选投稿所需的元信息。

【短篇全文】
{full_content}

【题材】
{genre}

━━ 任务要求 ━━

• 严格按 system 提示词中的字段细则与自查清单执行。
• 输出严格 JSON，包含 hook_quote、short_intro、synopsis、tags、title_suggestion、opening_optimization 六个字段。
• 不要包代码块、不要加注释、不要写前后说明文字。
• hook_quote 15-25 字，必须能独立传播。
• short_intro 100-150 字，禁止剧透反转。
• synopsis 300-500 字，必须突出信息差和反转点。
• tags 3-5 个，第一个必须是 {genre} 主赛道。
• title_suggestion 必须符合《主标题｜赛道·情绪标签》格式。
• opening_optimization 必须具体到改哪句、为什么改、改成什么。

直接输出 JSON。
