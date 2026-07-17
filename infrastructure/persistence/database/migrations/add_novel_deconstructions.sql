CREATE TABLE IF NOT EXISTS novel_deconstructions (
    deconstruction_id TEXT PRIMARY KEY,
    novel_id TEXT NOT NULL,
    novel_name TEXT NOT NULL,
    author TEXT DEFAULT '',
    platform TEXT NOT NULL,
    category TEXT DEFAULT '',
    analyzed_chapters INTEGER DEFAULT 0,
    total_word_count INTEGER DEFAULT 0,
    chapter_beats_json TEXT DEFAULT '[]',
    characters_json TEXT DEFAULT '[]',
    plot_structure_json TEXT DEFAULT '[]',
    golden_fingers_json TEXT DEFAULT '[]',
    cool_points_json TEXT DEFAULT '[]',
    conflicts_json TEXT DEFAULT '[]',
    dna_json TEXT DEFAULT '{}',
    ai_summary TEXT DEFAULT '',
    ai_strengths TEXT DEFAULT '',
    ai_weaknesses TEXT DEFAULT '',
    ai_replicable_elements TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_deconstructions_platform ON novel_deconstructions(platform);
CREATE INDEX IF NOT EXISTS idx_deconstructions_category ON novel_deconstructions(category);
CREATE INDEX IF NOT EXISTS idx_deconstructions_created ON novel_deconstructions(created_at DESC);
