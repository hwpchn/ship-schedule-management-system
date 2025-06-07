// 港口数据配置文件
// 包含全球主要港口信息，支持按国家/地区搜索

export const portData = [
  // 越南
  { code: 'VNHPH', name: 'HAIPHONG(海防,越南)', country: '越南', city: '海防' },
  { code: 'VNDAD', name: 'DANANG(岘港,越南)', country: '越南', city: '岘港' },
  { code: 'VNHAN', name: 'HANOI(河内,越南)', country: '越南', city: '河内' },
  {
    code: 'VNPHG',
    name: 'HOCHIMINH--PHUOC LONG(胡志明芙蓉港,越南)',
    country: '越南',
    city: '胡志明',
  },
  { code: 'VNSGN', name: 'HOCHIMINH(胡志明,越南)', country: '越南', city: '胡志明' },

  // 泰国
  { code: 'THLCH', name: 'LAEM CHABANG(林查班,泰国)', country: '泰国', city: '林查班' },
  { code: 'THSGZ', name: 'SONGKHLA(宋卡,泰国)', country: '泰国', city: '宋卡' },
  { code: 'THLKR', name: 'LAT KRABANG(莱卡邦,泰国)', country: '泰国', city: '莱卡邦' },
  { code: 'THBKK', name: 'BANGKOK(曼谷,泰国)', country: '泰国', city: '曼谷' },

  // 新加坡
  { code: 'SGSIN', name: 'SINGAPORE(新加坡,新加坡)', country: '新加坡', city: '新加坡' },

  // 马来西亚
  { code: 'MYWSP', name: 'PORT KELANG W(巴生西,马来西亚)', country: '马来西亚', city: '巴生' },
  { code: 'MYLPK', name: 'PORT KELANG N(巴生北,马来西亚)', country: '马来西亚', city: '巴生' },
  { code: 'MYPGU', name: 'PASIR GUDANG(巴西古单,马来西亚)', country: '马来西亚', city: '巴西古单' },
  { code: 'MYPEN', name: 'PENANG(槟城,马来西亚)', country: '马来西亚', city: '槟城' },
  { code: 'MYKCH', name: 'KUCHING(古晋,马来西亚)', country: '马来西亚', city: '古晋' },
  {
    code: 'MYBKI',
    name: 'KOTA KINABALU(哥打基纳巴卢,马来西亚)',
    country: '马来西亚',
    city: '哥打基纳巴卢',
  },
  { code: 'MYBTU', name: 'BINTULU(民都鲁,马来西亚)', country: '马来西亚', city: '民都鲁' },
  { code: 'MYMYY', name: 'MIRI(米里,马来西亚)', country: '马来西亚', city: '米里' },
  {
    code: 'MYTPP',
    name: 'TANJUNG PELEPAS(丹戎帕拉帕斯,马来西亚)',
    country: '马来西亚',
    city: '丹戎帕拉帕斯',
  },

  // 印度尼西亚
  { code: 'IDJKT', name: 'JAKARTA(雅加达,印度尼西亚)', country: '印度尼西亚', city: '雅加达' },
  { code: 'IDBTM', name: 'BATAM(巴淡,印度尼西亚)', country: '印度尼西亚', city: '巴淡' },
  { code: 'IDSRG', name: 'SEMARANG(三宝垄,印度尼西亚)', country: '印度尼西亚', city: '三宝垄' },
  { code: 'IDSUB', name: 'SURABAYA(泗水,印度尼西亚)', country: '印度尼西亚', city: '泗水' },
  { code: 'IDBLW', name: 'BELAWAN(乌拉湾,印度尼西亚)', country: '印度尼西亚', city: '乌拉湾' },

  // 菲律宾
  { code: 'PHMNS', name: 'MANILA S(马尼拉南,菲律宾)', country: '菲律宾', city: '马尼拉' },
  { code: 'PHMNN', name: 'MANILA N(马尼拉北,菲律宾)', country: '菲律宾', city: '马尼拉' },
  { code: 'PHDVO', name: 'DAVAO(达沃,菲律宾)', country: '菲律宾', city: '达沃' },
  { code: 'PHCEB', name: 'CEBU(宿务,菲律宾)', country: '菲律宾', city: '宿务' },
  { code: 'PHSFS', name: 'SUBIC BAY(苏比克湾,菲律宾)', country: '菲律宾', city: '苏比克湾' },
  { code: 'PHCGY', name: 'CAGAYAN(卡加延,菲律宾)', country: '菲律宾', city: '卡加延' },

  // 日本
  { code: 'JPTYO', name: 'TOKYO(东京,日本)', country: '日本', city: '东京' },
  { code: 'JPYOK', name: 'YOKOHAMA(横滨,日本)', country: '日本', city: '横滨' },
  { code: 'JPNGO', name: 'NAGOYA(名古屋,日本)', country: '日本', city: '名古屋' },
  { code: 'JPUKB', name: 'KOBE(神户,日本)', country: '日本', city: '神户' },
  { code: 'JPOSA', name: 'OSAKA(大阪,日本)', country: '日本', city: '大阪' },
  { code: 'JPMOJ', name: 'MOJI(门司,日本)', country: '日本', city: '门司' },

  // 韩国
  { code: 'KRINC', name: 'INCHON(仁川,韩国)', country: '韩国', city: '仁川' },
  { code: 'KRPUS', name: 'BUSAN(釜山,韩国)', country: '韩国', city: '釜山' },

  // 中国台湾
  { code: 'TWTXG', name: 'TAICHUNG,TAIWAN(台中,中国台湾)', country: '中国台湾', city: '台中' },
  { code: 'TWTPE', name: 'TAIPEI,TAIWAN(台北,中国台湾)', country: '中国台湾', city: '台北' },
  { code: 'TWKEL', name: 'KEELUNG,TAIWAN(基隆,中国台湾)', country: '中国台湾', city: '基隆' },
  { code: 'TWKHH', name: 'KAOHSIUNG,TAIWAN(高雄,中国台湾)', country: '中国台湾', city: '高雄' },

  // 印度
  { code: 'INMUN', name: 'MUNDRA(蒙德拉,印度)', country: '印度', city: '蒙德拉' },
  { code: 'INMAA', name: 'CHENNAI(清奈,印度)', country: '印度', city: '清奈' },
  { code: 'INCOK', name: 'COCHIN(科钦,印度)', country: '印度', city: '科钦' },
  { code: 'INCCU', name: 'CALCUTTA(加尔各答,印度)', country: '印度', city: '加尔各答' },
  { code: 'INPAV', name: 'PIPAVAV(皮帕瓦,印度)', country: '印度', city: '皮帕瓦' },
  { code: 'INBOM', name: 'MUMBAI(孟买,印度)', country: '印度', city: '孟买' },
  { code: 'INICD', name: 'NEW DELHI(新德里,印度)', country: '印度', city: '新德里' },
  { code: 'INBLR', name: 'BANGALORE(班加罗尔,印度)', country: '印度', city: '班加罗尔' },
  {
    code: 'INVTZ',
    name: 'VISAKHAPATNAM(维沙卡帕特南,印度)',
    country: '印度',
    city: '维沙卡帕特南',
  },
  { code: 'INNSA', name: 'NHAVA SHEVA(那瓦西瓦,印度)', country: '印度', city: '那瓦西瓦' },

  // 斯里兰卡
  { code: 'LKCMB', name: 'COLOMBO(科伦坡,斯里兰卡)', country: '斯里兰卡', city: '科伦坡' },

  // 巴基斯坦
  { code: 'PKKHI', name: 'KARACHI(卡拉奇,巴基斯坦)', country: '巴基斯坦', city: '卡拉奇' },

  // 孟加拉
  { code: 'BDCGP', name: 'CHATTOGRAM(吉大港,孟加拉)', country: '孟加拉', city: '吉大港' },
  { code: 'BDDAC', name: 'DHAKA(达卡,孟加拉)', country: '孟加拉', city: '达卡' },

  // 缅甸
  { code: 'MMRGN', name: 'YANGON(仰光,缅甸)', country: '缅甸', city: '仰光' },

  // 柬埔寨
  { code: 'KHKOS', name: 'SIHANOUKVILLE(西哈努克,柬埔寨)', country: '柬埔寨', city: '西哈努克' },
  { code: 'KHPNH', name: 'PHNOM PENH(金边,柬埔寨)', country: '柬埔寨', city: '金边' },

  // 阿联酋
  { code: 'AEJEA', name: 'JEBEL ALI,DUBAI(杰贝阿里,迪拜,阿联酋)', country: '阿联酋', city: '迪拜' },
  { code: 'AESHJ', name: 'SHARJAH(沙迦,阿联酋)', country: '阿联酋', city: '沙迦' },
  { code: 'AEAUH', name: 'ABU DHABI(阿布扎比,阿联酋)', country: '阿联酋', city: '阿布扎比' },
  { code: 'AEAJM', name: 'AJMAN(阿治曼,阿联酋)', country: '阿联酋', city: '阿治曼' },

  // 沙特阿拉伯
  { code: 'SADMM', name: 'DAMMAM(达曼,沙特阿拉伯)', country: '沙特阿拉伯', city: '达曼' },
  { code: 'SARYP', name: 'RIYADH(利雅得,沙特阿拉伯)', country: '沙特阿拉伯', city: '利雅得' },
  { code: 'SAJED', name: 'JEDDAH(吉达,沙特阿拉伯)', country: '沙特阿拉伯', city: '吉达' },

  // 阿曼
  { code: 'OMSOH', name: 'SOHAR(苏哈,阿曼)', country: '阿曼', city: '苏哈' },

  // 卡塔尔
  { code: 'QAHMD', name: 'HAMAD PORT,DOHA(哈马德港,卡塔尔)', country: '卡塔尔', city: '多哈' },

  // 巴林
  { code: 'BHBAH', name: 'BAHRAIN(巴林,巴林)', country: '巴林', city: '巴林' },

  // 科威特
  {
    code: 'KWSWK',
    name: 'KUWAIT–SHUWAIKH(科威特舒瓦克,科威特)',
    country: '科威特',
    city: '科威特',
  },
  { code: 'KWSAA', name: 'KUWAIT–SHUAIBA(科威特舒艾拜,科威特)', country: '科威特', city: '科威特' },

  // 伊拉克
  { code: 'IQUQR', name: 'UMM QASAR(乌姆盖斯尔,伊拉克)', country: '伊拉克', city: '乌姆盖斯尔' },

  // 约旦
  { code: 'JOAQJ', name: 'AQABAH(亚喀巴,约旦)', country: '约旦', city: '亚喀巴' },

  // 吉布提
  { code: 'DJJIB', name: 'DJIBOUTI(吉布提,吉布提)', country: '吉布提', city: '吉布提' },

  // 埃及
  { code: 'EGSOK', name: 'SOKHNA(苏科纳,埃及)', country: '埃及', city: '苏科纳' },
]

// 中国港口数据（包含城市和具体港口映射）
export const chineseCityPorts = [
  {
    code: 'SHENZHEN',
    name: 'SHENZHEN(深圳)',
    country: '中国',
    terminals: [
      { code: 'CNSHK', name: '蛇口' },
      { code: 'CNDCB', name: '大铲湾' },
      { code: 'CNYTN', name: '盐田' },
    ],
  },
  {
    code: 'NANSHA',
    name: 'NANSHA(广州南沙)',
    country: '中国',
    terminals: [{ code: 'CNNAN', name: '广州南沙' }],
  },
]

// 获取所有港口（包含中国港口的具体码头）
export const getAllPorts = () => {
  const allPorts = [...portData]

  // 添加中国港口的具体码头
  chineseCityPorts.forEach(city => {
    city.terminals.forEach(terminal => {
      allPorts.push({
        code: terminal.code,
        name: `${terminal.name}(${city.name})`,
        country: city.country,
        city: terminal.name,
        parentCity: city.code,
      })
    })
  })

  return allPorts
}

// 搜索港口
export const searchPorts = searchTerm => {
  if (!searchTerm) return getAllPorts()

  const term = searchTerm.toLowerCase()
  const allPorts = getAllPorts()

  return allPorts.filter(port => {
    return (
      port.name.toLowerCase().includes(term) ||
      port.code.toLowerCase().includes(term) ||
      port.country.toLowerCase().includes(term) ||
      port.city.toLowerCase().includes(term)
    )
  })
}

// 按国家分组港口
export const getPortsByCountry = () => {
  const allPorts = getAllPorts()
  const grouped = {}

  allPorts.forEach(port => {
    if (!grouped[port.country]) {
      grouped[port.country] = []
    }
    grouped[port.country].push(port)
  })

  return grouped
}
