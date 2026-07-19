/** 知乎盐选短篇题材模板 */

export interface YanxuanTemplate {
  id: string
  name: string
  description: string
  tags: string[]
  coreAppeal: string
  classicTropes: string[]
  characterArchetypes: string[]
  pacingNotes: string
  recommendedWords: number
  recommendedSections: number
  twistDesign: string
  taboo: string
  /** 用于创建作品时填入 premise 的模板文本 */
  premiseTemplate: string
}

export const YANXUAN_TEMPLATES: YanxuanTemplate[] = [
  {
    id: 'female_suspense',
    name: '女性悬疑',
    description: '以女性视角展开的悬疑故事，强调反转和信息差',
    tags: ['悬疑', '反转', '女性视角'],
    coreAppeal: '揭开隐藏的真相，每一次反转都颠覆读者认知',
    classicTropes: [
      '看似完美的丈夫/男友隐藏着可怕秘密',
      '闺蜜/姐妹间的背叛与真相',
      '记忆错位——主角发现记忆被篡改',
      '双线叙事——过去与现在的交织',
    ],
    characterArchetypes: [
      '女主角：表面平凡但内心坚韧，有洞察力',
      '反派：表面可信但隐藏真实身份',
      '关键证人：提供翻转性信息',
    ],
    pacingNotes: '开篇即悬念，每2000字一个小反转，结尾大反转',
    recommendedWords: 15000,
    recommendedSections: 8,
    twistDesign: '三层反转：表层真相→中层误导→底层真相',
    taboo: '不写真实案件，不具象暴力',
    premiseTemplate:
      '我发现丈夫的手机里有一个加密相册。破解后看到的不是出轨证据，而是一系列我家周边的监控截图——拍的全是我本人。最新一张是今天下午的，拍摄角度来自我们家衣柜的方向。我开始暗中调查，发现他书桌抽屉里有一本日记，已经记录我三年行踪。我以为嫁的是完美丈夫，其实他一直在监视我。但真正让我脊背发凉的，是日记最后一页——上面写着：她终于发现了，游戏才刚刚开始。',
  },
  {
    id: 'realistic_emotion',
    name: '现实情感',
    description: '聚焦现实生活中的情感冲突，代入感强',
    tags: ['情感', '现实', '代入感'],
    coreAppeal: '读者在故事中看到自己的生活，获得情感宣泄',
    classicTropes: [
      '婚姻危机——从发现端倪到决断',
      '职场情感——上下级/同事间的暧昧与博弈',
      '原生家庭——与父母的和解或决裂',
      '中年困境——事业家庭的双重压力',
    ],
    characterArchetypes: [
      '主角：30岁左右都市女性，有工作有家庭',
      '对手：造成情感冲突的核心人物',
      '支持者：朋友/同事，提供情感支撑',
    ],
    pacingNotes: '开篇300字内点明冲突，中段层层升级，结尾给出态度',
    recommendedWords: 12000,
    recommendedSections: 6,
    twistDesign: '情感反转：从忍让到觉醒，从误解到理解',
    taboo: '不写狗血，不写三观不正',
    premiseTemplate:
      '结婚第七年，我以为婚姻还算体面。直到那天我提前下班回家，看到丈夫在厨房给陌生女人煲汤——他七年没为我下过厨。我没闹没问，默默把门关上。接下来的一个月，我搜集证据、清算财产、咨询律师，照常上班、接孩子、维持体面。当我把离婚协议书摆在他面前，他第一次慌了：你不是说不在乎吗？我笑了：你以为什么都没变，其实我什么都看在眼里，只是终于攒够了失望。孩子归我，房子归我，你净身出户。',
  },
  {
    id: 'brain_hole',
    name: '脑洞反转',
    description: '高概念设定，强反转，适合脑洞类短篇',
    tags: ['脑洞', '反转', '奇幻'],
    coreAppeal: '一个惊艳的设定贯穿全文，结尾给出颠覆性反转',
    classicTropes: [
      '时间循环——主角被困在某一天',
      '身份互换——两个灵魂的错位',
      '规则怪谈——遵守规则才能存活',
      '平行世界——另一个自己的选择',
    ],
    characterArchetypes: [
      '主角：普通人，被卷入异常事件',
      '引导者：解释规则的关键角色',
      '反转角色：看似敌对实则帮助',
    ],
    pacingNotes: '开篇即抛出设定，每个节点揭示新规则，结尾颠覆全局',
    recommendedWords: 18000,
    recommendedSections: 10,
    twistDesign: '终极反转：主角发现自己才是...',
    taboo: '不写封建迷信，设定要有内在逻辑',
    premiseTemplate:
      '我从噩梦中惊醒，发现手机日期停在三月十五日。出门、上班、被领导骂、和女友分手——一切都和昨天一模一样。我开始记录规则：每重复一次，会有一个人忘记我的存在。第一次是同事，第二次是邻居，第三次是我的猫。到第三十次，整个城市都不再认识我。我冲进警局想自首，警察问我找谁。我说我叫什么名字。警察摇头：先生，你叫什么名字——那一刻我才意识到，我自己也快忘了。',
  },
  {
    id: 'wife_chasing',
    name: '追妻火葬场',
    description: '经典爽文套路，男主作死后悔追妻',
    tags: ['爽文', '虐恋', 'HE'],
    coreAppeal: '看渣男后悔，看女主逆袭，爽感十足',
    classicTropes: [
      '误会抛弃——男主因误会伤害女主',
      '身份反转——女主其实是隐藏大佬',
      '追妻火葬——男主百般讨好求复合',
      '新欢出现——女主已有更好的人',
    ],
    characterArchetypes: [
      '女主：前期隐忍，后期果断强大',
      '男主：前期傲慢，后期卑微',
      '新欢：比男主更懂女主的优质角色',
    ],
    pacingNotes: '前1/3虐，中1/3反转，后1/3爽',
    recommendedWords: 15000,
    recommendedSections: 8,
    twistDesign: '身份反转+情感反转：女主从未真正爱过',
    taboo: '不写三观不正的复合结局',
    premiseTemplate:
      '三年婚姻，我把丈夫当全世界。直到他初恋回国，他当众说我是替代品，签字离婚那天我淋了一夜的雨。我没说一句挽留。三年后，我以集团新任CEO的身份回国，他站在接机人群里，眼神发直。他开始追我：每天送花、堵我办公室、跪在我家门口。我看着他卑微的样子，心里毫无波澜。他的初恋早已离开，他这才明白失去的是什么。当他红着眼问还能不能重来，我笑：可以的——只要你能回到三年前那场雨里，把伞递给我。',
  },
  {
    id: 'rebirth_revenge',
    name: '重生复仇',
    description: '重生类复仇爽文，前世被害重生后复仇',
    tags: ['重生', '复仇', '爽文'],
    coreAppeal: '带着记忆重来，步步为营，让仇人付出代价',
    classicTropes: [
      '前世被害——重生回到关键节点',
      '改写命运——避开前世的坑',
      '布局复仇——一步步揭露仇人真面目',
      '终局清算——仇人失去一切',
    ],
    characterArchetypes: [
      '主角：重生者，冷静智慧',
      '仇人：前世加害者，表面可信',
      '盟友：前世错过的人，今生成为助力',
    ],
    pacingNotes: '开篇即重生，每节一个复仇节点，结尾大清算',
    recommendedWords: 20000,
    recommendedSections: 10,
    twistDesign: '终极反转：仇人也有自己的苦衷？不，坚定复仇',
    taboo: '不写血腥复仇，靠智慧和信息差取胜',
    premiseTemplate:
      '前世我是江家最不起眼的二小姐，被继姐陷害、被未婚夫抛弃、被父亲卖掉抵债，最后死在精神病院的地下室。临死前我听见继姐在耳边笑：姐，你太善良了。再睁眼，我回到了十八岁生日那天——继姐第一次给我下药的那天。这一次，我把药换成了安眠药，看着她当众睡着。我开始布局：拉拢前世错过的商界大佬，揭露继姐的假学历，让父亲的生意在关键节点崩盘。前世加诸于我的一切，今生我会十倍奉还。他们以为我好欺负，殊不知，那个善良的江家二小姐，已经死在了上辈子的地下室里。',
  },
]
