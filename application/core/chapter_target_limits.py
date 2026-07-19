"""每章目标字数：API、持久化、体量推导与全托管链路共用夹逼，避免各层上限不一致。"""

CHAPTER_TARGET_WORDS_MIN = 500
CHAPTER_TARGET_WORDS_MAX = 20_000

# 短篇（知乎盐选/番茄短故事）每节字数范围：800-3000，符合盐选规范
SHORT_STORY_CHAPTER_TARGET_WORDS_MIN = 800
SHORT_STORY_CHAPTER_TARGET_WORDS_MAX = 3000


def clamp_chapter_target_words(w: int) -> int:
    return max(CHAPTER_TARGET_WORDS_MIN, min(CHAPTER_TARGET_WORDS_MAX, int(w)))


def clamp_short_story_chapter_target_words(w: int) -> int:
    """短篇专用：每节字数夹逼到 800-3000 范围内（盐选规范）。"""
    return max(
        SHORT_STORY_CHAPTER_TARGET_WORDS_MIN,
        min(SHORT_STORY_CHAPTER_TARGET_WORDS_MAX, int(w)),
    )
